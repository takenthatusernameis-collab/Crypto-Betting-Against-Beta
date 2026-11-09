"""Campaign11 slice (j): CLI-level universe edge contract (evidence-first, non-duplicative).

Distinct from `test_bab_cli_universe_subset_campaign11.py` (which locks the
*subset-affects-backtest* regression) and `test_betting_against_beta.py::TestResolvedUniverse`
(which locks `resolved_universe` unit semantics). This module locks the *CLI end-to-end*
contract for three universe edge shapes proven safe by probe (2026-11-09, HEAD `d5fd66f`):

  (a) benchmark-only universe  -> single-asset tradable universe, flat cumulative (1.0)
  (b) duplicate tokens         -> de-duplicated effective universe, finite output
  (c) partial overlap          -> absent tokens silently dropped, overlap kept, finite

No production edits; no assertions weakened. Evidence: probe at /tmp/probe_universe_edges.py
showed rc=0, strict-finite JSON, and contract-respecting universe lists for all three.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
REAL = "tests/fixtures/real_market_prices.csv"


def _run_cli(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli", *argv],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
    )


def _assert_strict_finite(payload: dict) -> None:
    raw = json.dumps(payload, allow_nan=False)
    for tok in ("NaN", "Infinity", "-Infinity"):
        assert tok not in raw
    fc = payload["final_cumulative"]
    assert isinstance(fc, (int, float)) and not isinstance(fc, bool)
    assert math.isfinite(float(fc))
    assert isinstance(payload["periods"], int) and not isinstance(payload, bool)
    assert payload["periods"] > 0
    assert isinstance(payload["benchmark"], str)
    assert isinstance(payload["universe"], list)


class TestCliUniverseBenchmarkOnlyEdge:
    def test_benchmark_only_universe_flat_cumulative(self, tmp_path: Path):
        # (a) universe == [benchmark] => only the benchmark is tradable; no
        # long/short spread is possible, so cumulative stays flat at 1.0.
        out = tmp_path / "bench_only.json"
        res = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--universe", "BTC", "--output", str(out),
        ])
        assert res.returncode == 0, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        assert "Traceback" not in (res.stdout + res.stderr)
        d = json.loads(out.read_text())
        _assert_strict_finite(d)
        assert d["universe"] == ["BTC"]
        assert d["final_cumulative"] == pytest.approx(1.0)


class TestCliUniverseDuplicateTokensEdge:
    def test_duplicate_tokens_deduplicated(self, tmp_path: Path):
        # (b) duplicate tokens must not create phantom columns or duplicate
        # effective universe entries; output stays strict-finite.
        out = tmp_path / "dup.json"
        res = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--universe", "ETH", "ETH", "SOL", "--output", str(out),
        ])
        assert res.returncode == 0, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        assert "Traceback" not in (res.stdout + res.stderr)
        d = json.loads(out.read_text())
        _assert_strict_finite(d)
        # Effective universe is de-duplicated (order preserved, dup removed)
        assert d["universe"] == ["ETH", "SOL"]
        # And the backtest result matches the explicit de-duplicated subset
        # (duplicates must not change portfolio construction).
        out2 = tmp_path / "dup2.json"
        res2 = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--universe", "ETH", "SOL", "--output", str(out2),
        ])
        assert res2.returncode == 0, f"rc={res2.returncode}\n{res2.stderr}\n{res2.stdout}"
        d2 = json.loads(out2.read_text())
        assert d["final_cumulative"] == pytest.approx(d2["final_cumulative"])


class TestCliUniversePartialOverlapEdge:
    def test_partial_overlap_drops_absent_tokens(self, tmp_path: Path):
        # (c) tokens absent from the data are silently dropped; the overlap is
        # kept and the backtest is strict-finite.
        out = tmp_path / "partial.json"
        res = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--universe", "ETH", "SOL", "NOPE", "--output", str(out),
        ])
        assert res.returncode == 0, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        assert "Traceback" not in (res.stdout + res.stderr)
        d = json.loads(out.read_text())
        _assert_strict_finite(d)
        assert d["universe"] == ["ETH", "SOL"]

    def test_partial_overlap_matches_explicit_subset(self, tmp_path: Path):
        # Contract: dropping an absent token must not change the result vs the
        # same explicit subset without the absent token.
        out_a = tmp_path / "a.json"
        out_b = tmp_path / "b.json"
        for out, uni in ((out_a, ["ETH", "SOL", "NOPE"]), (out_b, ["ETH", "SOL"])):
            res = _run_cli([
                "--data", REAL, "--from-prices", "--benchmark", "BTC",
                "--universe", *uni, "--output", str(out),
            ])
            assert res.returncode == 0, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        da = json.loads(out_a.read_text())
        db = json.loads(out_b.read_text())
        assert da["universe"] == db["universe"]
        assert da["final_cumulative"] == pytest.approx(db["final_cumulative"])