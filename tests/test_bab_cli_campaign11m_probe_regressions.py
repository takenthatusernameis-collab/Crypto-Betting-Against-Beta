"""Campaign11m: probe-backed CLI/strategy regression locks (evidence 2026-11-10T03:39Z @ 18339ed).

Covers exercised gaps/invariants probed during campaign11b Step 0+probe matrix:
- CLI --output summary parity vs in-process BABStrategy for additional real-data
  flag combinations (beta-window override, rebalance freq, quantile overrides,
  combined cost/slippage/rebalance/window) and returns-data path combos.
- --dry-run validates --output target but never writes it (including rejection of
  directory output target) while reporting valid resolved config/data.
- Non-finite propagation boundaries: NaN injections in asset/benchmark columns
  handled defensively with finite JSON-safe outputs where admissible; Inf/-Inf in
  asset or benchmark columns rejected cleanly (rc=1, no Traceback).
- Error-path cleanliness for exercised malformed/extreme inputs (no Traceback,
  actionable rc=1).

All assertions are non-duplicative with campaign11/l/k/j coverage and tied to
probed, exercised behavior.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.cli import main
from strategies.betting_against_beta.data_loader import load_prices, load_returns
from strategies.betting_against_beta.strategy import BABStrategy

REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_PRICES = str(REPO_ROOT / "tests" / "fixtures" / "real_market_prices.csv")


def _run_cli(argv, out_path: Path):
    rc = main([*argv, "--output", str(out_path)])
    raw = out_path.read_text() if out_path.exists() else ""
    payload = json.loads(raw) if out_path.exists() else None
    return rc, payload, raw


def _assert_strict_finite_payload(payload: dict, raw: str):
    assert payload is not None
    json.dumps(payload, allow_nan=False)
    for tok in ("NaN", "Infinity", "-Infinity"):
        assert tok not in raw
    fc = payload["final_cumulative"]
    assert isinstance(fc, (int, float)) and not isinstance(fc, bool)
    assert math.isfinite(float(fc))
    assert isinstance(payload["periods"], int) and not isinstance(payload["periods"], bool)
    assert payload["periods"] > 0


class TestCliParityAdditionalCombosRealFixture:
    @pytest.mark.parametrize(
        "argv,cfgkw",
        [
            (
                ["--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC", "--beta-window", "30"],
                {"benchmark": "BTC", "beta_window": 30},
            ),
            (
                ["--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC", "--rebalance-freq", "weekly"],
                {"benchmark": "BTC", "rebalance_freq": "weekly"},
            ),
            (
                ["--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC", "--rebalance-freq", "monthly"],
                {"benchmark": "BTC", "rebalance_freq": "monthly"},
            ),
            (
                ["--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC", "--long-quantile", "0.2", "--short-quantile", "0.2"],
                {"benchmark": "BTC", "long_quantile": 0.2, "short_quantile": 0.2},
            ),
            (
                [
                    "--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC",
                    "--beta-window", "45", "--transaction-costs", "0.002",
                    "--slippage", "0.001", "--rebalance-freq", "weekly",
                ],
                {"benchmark": "BTC", "beta_window": 45, "transaction_costs": 0.002, "slippage": 0.001, "rebalance_freq": "weekly"},
            ),
        ],
    )
    def test_from_prices_output_matches_inprocess(self, tmp_path, argv, cfgkw):
        out = tmp_path / "out.json"
        rc, payload, raw = _run_cli(argv, out)
        assert rc == 0, (rc, raw)
        _assert_strict_finite_payload(payload, raw)
        returns_df = load_prices(REAL_PRICES, benchmark=cfgkw.get("benchmark", "BTC"))
        res = BABStrategy(**cfgkw).run(returns_df=returns_df)
        assert payload["final_cumulative"] == float(res.backtest["cumulative"].iloc[-1])
        assert payload["periods"] == len(res.backtest)
        assert payload["benchmark"] == res.config.benchmark
        assert payload["universe"] == list(res.config.universe)

    @pytest.mark.parametrize(
        "extra_argv,extra_cfg",
        [
            ([], {}),
            (["--rebalance-freq", "weekly", "--transaction-costs", "0.001"], {"rebalance_freq": "weekly", "transaction_costs": 0.001}),
        ],
    )
    def test_returns_path_output_matches_inprocess(self, tmp_path, extra_argv, extra_cfg):
        # Materialize deterministic returns CSV from real prices fixture.
        returns_df = load_prices(REAL_PRICES, benchmark="BTC")
        ret_path = tmp_path / "returns.csv"
        returns_df.to_csv(ret_path)
        cfgkw = {"benchmark": "BTC", **extra_cfg}
        out = tmp_path / "out.json"
        rc, payload, raw = _run_cli(["--data", str(ret_path), "--benchmark", "BTC", *extra_argv], out)
        assert rc == 0, (rc, raw)
        _assert_strict_finite_payload(payload, raw)
        rdf = load_returns(str(ret_path), benchmark="BTC")
        res = BABStrategy(**cfgkw).run(returns_df=rdf)
        assert payload["final_cumulative"] == float(res.backtest["cumulative"].iloc[-1])
        assert payload["periods"] == len(res.backtest)
        assert payload["benchmark"] == res.config.benchmark
        assert payload["universe"] == list(res.config.universe)


class TestDryRunOutputValidationNoWrite:
    def test_dry_run_validates_output_but_does_not_write(self, tmp_path):
        out = tmp_path / "would_write.json"
        rc = main(["--dry-run", "--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC", "--output", str(out)])
        assert rc == 0
        assert not out.exists(), "dry-run must validate but never write --output"

    def test_dry_run_rejects_directory_output_target(self, tmp_path, capsys):
        # Directory target must be rejected cleanly during dry-run validation.
        rc = main(["--dry-run", "--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC", "--output", str(tmp_path)])
        assert rc == 1
        captured = capsys.readouterr()
        combined = captured.out + captured.err
        assert "Traceback" not in combined
        assert "directory" in combined.lower() or "output" in combined.lower()


def _write_mutated_prices(tmp_path: Path, mutate_fn, name: str = "mut.csv") -> str:
    base = pd.read_csv(REAL_PRICES)
    mutate_fn(base)
    p = tmp_path / name
    base.to_csv(p, index=False)
    return str(p)


class TestNonFinitePropagationBoundaries:
    @pytest.mark.parametrize(
        "label,mutate",
        [
            ("single_nan_eth", lambda df: df.__setitem__("ETH", df["ETH"].where(df.index != 5))),
            ("sparse_nans_sol", lambda df: df.__setitem__("SOL", df["SOL"].mask(df.index.isin([2, 10, 50])))),
            ("nan_benchmark_btc", lambda df: df.__setitem__("BTC", df["BTC"].where(df.index != 3))),
        ],
    )
    def test_admissible_nans_yield_finite_json(self, tmp_path, label, mutate):
        path = _write_mutated_prices(tmp_path, mutate, f"{label}.csv")
        out = tmp_path / "out.json"
        rc, payload, raw = _run_cli(["--data", path, "--from-prices", "--benchmark", "BTC"], out)
        assert rc == 0, (label, rc, raw)
        _assert_strict_finite_payload(payload, raw)

    @pytest.mark.parametrize(
        "label,mutate",
        [
            ("inf_asset_bnb", lambda df: df.loc.__setitem__((7, "BNB"), np.inf)),
            ("neginf_asset_bnb", lambda df: df.loc.__setitem__((7, "BNB"), -np.inf)),
            ("inf_benchmark_btc", lambda df: df.loc.__setitem__((3, "BTC"), np.inf)),
        ],
    )
    def test_infinite_values_rejected_cleanly(self, tmp_path, capsys, label, mutate):
        path = _write_mutated_prices(tmp_path, mutate, f"{label}.csv")
        out = tmp_path / "out.json"
        rc, payload, raw = _run_cli(["--data", path, "--from-prices", "--benchmark", "BTC"], out)
        captured = capsys.readouterr()
        combined = (captured.out + captured.err + raw)
        assert rc == 1, (label, rc, combined)
        assert payload is None
        assert "Traceback" not in combined
        assert "infinite" in combined.lower() or "error" in combined.lower()

    def test_all_but_one_nan_column_rejected_cleanly(self, tmp_path, capsys):
        def mutate(df):
            vals = df["ADA"].astype(float).to_numpy().copy()
            vals[1:] = np.nan
            df["ADA"] = vals
        path = _write_mutated_prices(tmp_path, mutate, "all_but_one_nan_ada.csv")
        out = tmp_path / "out.json"
        rc, payload, raw = _run_cli(["--data", path, "--from-prices", "--benchmark", "BTC"], out)
        captured = capsys.readouterr()
        combined = (captured.out + captured.err + raw)
        assert rc == 1
        assert payload is None
        assert "Traceback" not in combined
        assert "ADA" in combined or "insufficient" in combined.lower() or "finite" in combined.lower()


class TestErrorPathCleanlinessExercised:
    @pytest.mark.parametrize(
        "argv,needle",
        [
            (["--data", "/no/such/file_prices.csv", "--from-prices", "--benchmark", "BTC"], "not found"),
            (["--data", "tests/fixtures", "--from-prices", "--benchmark", "BTC"], "directory"),
            (["--universe", "   ", "  ", "--synthetic"], "universe"),
            (["--data", REAL_PRICES, "--from-prices", "--benchmark", "NOTCOIN"], "NOTCOIN"),
            (["--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC", "--universe", "NOPE"], "overlap"),
            (["--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC", "--long-quantile", "0"], "long_quantile"),
            (["--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC", "--long-quantile", "-0.1"], "long_quantile"),
            (["--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC", "--transaction-costs", "-1"], "transaction_costs"),
            (["--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC", "--slippage", "-0.1"], "slippage"),
        ],
    )
    def test_clean_error_no_traceback(self, argv, needle, capsys):
        rc = main(argv)
        captured = capsys.readouterr()
        combined = captured.out + captured.err
        assert rc == 1, (rc, combined)
        assert "Traceback" not in combined
        assert needle.lower() in combined.lower()

    def test_unsupported_extension_rejected_cleanly(self, tmp_path, capsys):
        p = tmp_path / "data.xlsxlike"
        p.write_text("a,b\n1,2\n")
        rc = main(["--data", str(p), "--from-prices", "--benchmark", "BTC"])
        captured = capsys.readouterr()
        combined = captured.out + captured.err
        assert rc == 1
        assert "Traceback" not in combined
        assert "unsupported" in combined.lower() or "extension" in combined.lower()

    @pytest.mark.parametrize("extra", [["--beta-window", "9999"], ["--beta-window", "1"]])
    def test_extreme_beta_windows_exercised_no_traceback(self, tmp_path, extra, capsys):
        # Extreme-but-accepted windows must run through exercised path without Traceback
        # and produce finite strict JSON when a backtest completes.
        out = tmp_path / "out.json"
        rc = main(["--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC", *extra, "--output", str(out)])
        captured = capsys.readouterr()
        combined = captured.out + captured.err
        assert "Traceback" not in combined
        if rc == 0 and out.exists():
            raw = out.read_text()
            payload = json.loads(raw)
            _assert_strict_finite_payload(payload, raw)
        else:
            # If rejected, must be a clean error.
            assert rc == 1
