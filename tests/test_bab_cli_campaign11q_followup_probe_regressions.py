"""Campaign11q: follow-up probe-backed CLI regressions (2026-11-10T05:18Z @ 7e281b1).

Locks exercised, non-duplicative invariants from HANDOFF §NEXT FOCUS probes:
- Real-fixture from-prices CLI parity (via --output JSON) vs in-process
  load_prices+BABStrategy across tc/slippage/rebalance combos: strict finite,
  exact final_cumulative/periods/benchmark/universe match.
- Malformed/edge data --dry-run on both fixtures and temp inputs: clean rc=1 or
  documented loader-contract rc=0 finite-valid behavior; no Traceback in all cases.
- --output edge cases: deep nested parent creation writes finite JSON; output to
  directory fails cleanly (rc=1, no Traceback); --dry-run never writes output even
  with invalid data or with valid deep-nested target.
- Dry-run semantic audit (characterization, evidence-first): dry-run validates
  data/loadability and output target but does not enforce all run-time strategy
  semantics (e.g. quantile overlap acceptance, universe/data overlap). Locks
  observed rc/message parity or gap without altering contract.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pytest

REAL = "tests/fixtures/real_market_prices.csv"
EXP = "tests/fixtures/real_market_prices_expanded.csv"


def _run(args, cwd=None):
    env = {**os.environ, "PYTHONPATH": os.getcwd()}
    return subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli"] + args,
        capture_output=True,
        text=True,
        cwd=cwd or os.getcwd(),
        env=env,
    )


def _assert_no_traceback(r):
    blob = (r.stdout or "") + (r.stderr or "")
    assert "Traceback" not in blob, blob


class TestFromPricesParity:
    @pytest.mark.parametrize("fixture", [REAL, EXP])
    @pytest.mark.parametrize(
        "tc,sl,rf",
        [
            (0.001, 0.0005, "daily"),
            (0.01, 0.0, "daily"),
            (0.0, 0.01, "weekly"),
            (0.005, 0.005, "daily"),
        ],
    )
    def test_from_prices_output_json_matches_inprocess(self, tmp_path, fixture, tc, sl, rf):
        out = tmp_path / "out.json"
        r = _run([
            "--data", fixture, "--from-prices", "--benchmark", "BTC",
            "--transaction-costs", str(tc), "--slippage", str(sl),
            "--rebalance-freq", rf, "--output", str(out),
        ])
        _assert_no_traceback(r)
        assert r.returncode == 0, r.stdout + r.stderr
        assert out.exists()
        payload = json.loads(out.read_text())
        assert set(payload) == {"final_cumulative", "periods", "benchmark", "universe"}
        assert math.isfinite(payload["final_cumulative"])

        from strategies.betting_against_beta.data_loader import load_prices
        from strategies.betting_against_beta.strategy import BABStrategy

        df = load_prices(fixture, benchmark="BTC")
        res = BABStrategy(
            benchmark="BTC", transaction_costs=tc, slippage=sl, rebalance_freq=rf
        ).run(returns_df=df)
        exp_final = float(res.backtest["cumulative"].iloc[-1])
        assert payload["final_cumulative"] == exp_final
        assert payload["periods"] == int(len(res.backtest))
        assert payload["benchmark"] == "BTC"
        # CLI reports resolved/config universe; result.config holds resolved
        # universe used by the run (may be a subset of loaded columns depending
        # on fixture/config resolution path). Lock CLI parity to in-process run.
        expected_universe = list(getattr(res.config, "universe", None) or [])
        assert payload["universe"] == expected_universe, (
            f"cli={payload['universe']} expected={expected_universe} df_cols={list(df.columns)}"
        )


class TestMalformedDryRunNoTraceback:
    @pytest.mark.parametrize("mode", [[], ["--from-prices"]])
    @pytest.mark.parametrize(
        "name,builder,expect_rc",
        [
            ("empty_csv", lambda: "", 1),
            ("header_only", lambda: "date,BTC,ETH\n", 1),
            ("single_col", lambda: "date\n2024-01-01\n2024-01-02\n", 1),
            ("nat_heavy", lambda: "date,BTC,ETH\nnotadate,1,2\nalsobad,3,4\n2024-01-03,5,6\n", 1),
        ],
    )
    def test_invalid_temp_inputs_clean(self, tmp_path, mode, name, builder, expect_rc):
        p = tmp_path / f"{name}.csv"
        p.write_text(builder())
        r = _run(["--dry-run", "--data", str(p), "--benchmark", "BTC"] + mode)
        _assert_no_traceback(r)
        assert r.returncode == expect_rc, f"{name} {mode}: {r.stdout}\n{r.stderr}"
        blob = r.stdout + r.stderr
        assert "INVALID" in blob or r.returncode == 0

    @pytest.mark.parametrize("mode", [[], ["--from-prices"]])
    def test_duplicate_index_loader_contract_clean(self, tmp_path, mode):
        base = pd.read_csv(REAL).head(5)
        base = pd.concat([base, base.iloc[[0]]], ignore_index=True)
        p = tmp_path / "dup_index.csv"
        base.to_csv(p, index=False)
        r = _run(["--dry-run", "--data", str(p), "--benchmark", "BTC"] + mode)
        _assert_no_traceback(r)
        assert r.returncode in (0, 1)
        if r.returncode == 1:
            assert "INVALID" in (r.stdout + r.stderr)

    @pytest.mark.parametrize("mode", [[], ["--from-prices"]])
    def test_duplicate_columns_loader_contract_clean(self, tmp_path, mode):
        p = tmp_path / "dup_cols.csv"
        p.write_text("date,BTC,BTC\n2024-01-01,1,2\n2024-01-02,3,4\n")
        r = _run(["--dry-run", "--data", str(p), "--benchmark", "BTC"] + mode)
        _assert_no_traceback(r)
        assert r.returncode in (0, 1)

    @pytest.mark.parametrize("mode", [[], ["--from-prices"]])
    def test_mixed_inf_nan_loader_contract_clean(self, tmp_path, mode):
        base = pd.read_csv(REAL).head(5).copy()
        base.loc[0, "BTC"] = float("nan")
        base.loc[1, "ETH"] = float("inf")
        p = tmp_path / "mixed.csv"
        base.to_csv(p, index=False)
        r = _run(["--dry-run", "--data", str(p), "--benchmark", "BTC"] + mode)
        _assert_no_traceback(r)
        assert r.returncode in (0, 1)
        if r.returncode == 1:
            assert "INVALID" in (r.stdout + r.stderr)

    @pytest.mark.parametrize("fixture", [REAL, EXP])
    @pytest.mark.parametrize("mode", [[], ["--from-prices"]])
    def test_real_fixtures_dry_run_valid(self, fixture, mode):
        r = _run(["--dry-run", "--data", fixture, "--benchmark", "BTC"] + mode)
        _assert_no_traceback(r)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "(valid" in r.stdout


class TestOutputEdgeCases:
    def test_output_to_directory_fails_cleanly(self):
        r = _run(["--data", REAL, "--from-prices", "--benchmark", "BTC", "--output", "tests/fixtures"])
        _assert_no_traceback(r)
        assert r.returncode == 1
        assert "directory" in (r.stdout + r.stderr).lower()

    def test_deep_nested_output_created_with_finite_json(self, tmp_path):
        out = tmp_path / "a" / "b" / "c" / "out.json"
        r = _run(["--data", REAL, "--from-prices", "--benchmark", "BTC", "--output", str(out)])
        _assert_no_traceback(r)
        assert r.returncode == 0, r.stdout + r.stderr
        assert out.exists()
        j = json.loads(out.read_text())
        assert math.isfinite(j["final_cumulative"])
        assert j["periods"] > 0

    def test_dry_run_invalid_data_never_writes_output(self, tmp_path):
        out = tmp_path / "should_not_write.json"
        r = _run([
            "--dry-run", "--data", "/tmp/no_such_bab_file_campaign11q.csv",
            "--benchmark", "BTC", "--output", str(out),
        ])
        _assert_no_traceback(r)
        assert r.returncode == 1
        assert not out.exists(), "dry-run with invalid data must never write output"
        assert "INVALID" in r.stdout

    def test_dry_run_valid_deep_output_never_writes(self, tmp_path):
        out = tmp_path / "x" / "y" / "z" / "out.json"
        r = _run([
            "--dry-run", "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--output", str(out),
        ])
        _assert_no_traceback(r)
        assert r.returncode == 0, r.stdout + r.stderr
        assert not out.exists(), "dry-run must validate but never write output"


class TestDryRunSemanticAuditCharacterization:
    """Evidence-first characterization: dry-run validates loadability/output target
    but does not currently enforce all run-time strategy/config semantics."""

    def test_quantile_sum_ge_one_dry_run_valid_but_run_still_succeeds_contract(self):
        # Probed 2026-11-10: dry-run rc=0 (reports config) and real run rc=0 finite
        # for 0.6/0.6 on this fixture; lock exercised behavior (no over-strict reject).
        r = _run(["--dry-run", "--data", REAL, "--from-prices", "--benchmark", "BTC",
                  "--long-quantile", "0.6", "--short-quantile", "0.6"])
        _assert_no_traceback(r)
        assert r.returncode == 0
        assert "(valid" in r.stdout
        r2 = _run(["--data", REAL, "--from-prices", "--benchmark", "BTC",
                   "--long-quantile", "0.6", "--short-quantile", "0.6"])
        _assert_no_traceback(r2)
        assert r2.returncode == 0
        assert "Final cumulative return" in r2.stdout

    def test_universe_no_overlap_dry_run_loads_but_run_rejects(self):
        # Probed: dry-run validates data loading (rc=0, valid) but real run fails
        # with clean overlap error rc=1. Characterizes current semantic gap.
        r = _run(["--dry-run", "--data", REAL, "--from-prices", "--benchmark", "BTC",
                  "--universe", "ZZZ,YYY"])
        _assert_no_traceback(r)
        assert r.returncode == 0
        assert "(valid" in r.stdout
        r2 = _run(["--data", REAL, "--from-prices", "--benchmark", "BTC",
                   "--universe", "ZZZ,YYY"])
        _assert_no_traceback(r2)
        assert r2.returncode == 1
        assert "overlap" in (r2.stdout + r2.stderr).lower()

    def test_universe_all_empty_tokens_dry_run_loads_but_run_rejects(self):
        r = _run(["--dry-run", "--data", REAL, "--from-prices", "--benchmark", "BTC",
                  "--universe", ",,,"])
        _assert_no_traceback(r)
        assert r.returncode == 0
        r2 = _run(["--data", REAL, "--from-prices", "--benchmark", "BTC",
                   "--universe", ",,,"])
        _assert_no_traceback(r2)
        assert r2.returncode == 1
