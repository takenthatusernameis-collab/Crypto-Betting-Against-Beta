"""Campaign11p: probe-backed CLI regressions (2026-11-10).

Locks exercised, non-duplicative invariants from follow-up probe matrix:
- Returns-path + --transaction-costs/--slippage parity on real fixture
  (CLI == in-process BABStrategy, strict finite JSON).
- --dry-run invalid-data cleanliness on both fixtures (missing/dir/unsupported/
  bad-benchmark) -> rc=1, no Traceback, actionable INVALID message.
- --dry-run rejects whitespace-only --universe tokens cleanly (rc=1).
- --synthetic parity across alternate benchmarks and universe subsets on CLI
  vs in-process (strict finite, exact cumulative/periods/universe).
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import load_prices, load_returns

REPO = Path(__file__).resolve().parents[1]
REAL_PRICES = str(REPO / "tests" / "fixtures" / "real_market_prices.csv")
EXP_PRICES = str(REPO / "tests" / "fixtures" / "real_market_prices_expanded.csv")


def _run(argv):
    return subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli", *argv],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=180,
    )


def _assert_finite_json(path: Path):
    raw = path.read_text()
    payload = json.loads(raw)
    json.dumps(payload, allow_nan=False)
    for tok in ("NaN", "Infinity", "-Infinity"):
        assert tok not in raw
    fc = payload["final_cumulative"]
    assert isinstance(fc, (int, float)) and not isinstance(fc, bool)
    assert math.isfinite(float(fc))
    assert isinstance(payload["periods"], int) and payload["periods"] > 0
    return payload


class TestRealReturnsPathCostSlippageParity:
    @pytest.mark.parametrize("tc,sl", [(0.001, 0.0005), (0.01, 0.0), (0.0, 0.01), (0.005, 0.005)])
    def test_real_fixture_returns_path_matches_inprocess(self, tmp_path, tc, sl):
        returns_df = load_prices(REAL_PRICES, benchmark="BTC")
        ret_path = tmp_path / "returns.csv"
        returns_df.to_csv(ret_path)
        out = tmp_path / "o.json"
        r = _run(
            [
                "--data",
                str(ret_path),
                "--benchmark",
                "BTC",
                "--transaction-costs",
                str(tc),
                "--slippage",
                str(sl),
                "--output",
                str(out),
            ]
        )
        assert r.returncode == 0, (r.returncode, r.stdout + r.stderr)
        payload = _assert_finite_json(out)
        rdf = load_returns(str(ret_path), benchmark="BTC")
        res = BABStrategy(benchmark="BTC", transaction_costs=tc, slippage=sl).run(returns_df=rdf)
        assert math.isclose(
            float(payload["final_cumulative"]),
            float(res.backtest["cumulative"].iloc[-1]),
            abs_tol=1e-12,
        )
        assert payload["periods"] == len(res.backtest)
        assert payload["benchmark"] == "BTC"
        assert payload["universe"] == list(res.config.universe)


class TestDryRunInvalidDataCleanliness:
    @pytest.mark.parametrize("fixture", [REAL_PRICES, EXP_PRICES])
    def test_missing_file(self, fixture):
        r = _run(
            ["--dry-run", "--data", "/tmp/no_such_bab_file_campaign11p.csv", "--benchmark", "BTC"]
        )
        combined = r.stdout + r.stderr
        assert r.returncode == 1, (r.returncode, combined)
        assert "Traceback" not in combined
        assert "INVALID" in combined

    @pytest.mark.parametrize("fixture", [REAL_PRICES, EXP_PRICES])
    def test_directory_path(self, fixture):
        r = _run(["--dry-run", "--data", "tests/fixtures", "--benchmark", "BTC"])
        combined = r.stdout + r.stderr
        assert r.returncode == 1, (r.returncode, combined)
        assert "Traceback" not in combined
        assert "INVALID" in combined

    @pytest.mark.parametrize("fixture", [REAL_PRICES, EXP_PRICES])
    def test_unsupported_extension(self, fixture):
        r = _run(["--dry-run", "--data", "README.md", "--benchmark", "BTC"])
        combined = r.stdout + r.stderr
        assert r.returncode == 1, (r.returncode, combined)
        assert "Traceback" not in combined
        assert "INVALID" in combined

    @pytest.mark.parametrize("fixture", [REAL_PRICES, EXP_PRICES])
    def test_bad_benchmark(self, fixture):
        r = _run(["--dry-run", "--data", fixture, "--from-prices", "--benchmark", "NOTHERE"])
        combined = r.stdout + r.stderr
        assert r.returncode == 1, (r.returncode, combined)
        assert "Traceback" not in combined
        assert "INVALID" in combined

    @pytest.mark.parametrize("token", ["", "   "])
    def test_whitespace_only_universe_rejected(self, token):
        r = _run(
            [
                "--dry-run",
                "--data",
                EXP_PRICES,
                "--from-prices",
                "--benchmark",
                "BTC",
                "--universe",
                token,
            ]
        )
        combined = r.stdout + r.stderr
        assert r.returncode == 1, (r.returncode, combined)
        assert "Traceback" not in combined
        assert "non-empty asset token" in combined


class TestSyntheticParityAlternateConfigs:
    @pytest.mark.parametrize(
        "benchmark,universe",
        [
            ("BTC", None),
            ("SOL", None),
            ("BTC", ["BTC", "ETH", "SOL"]),
            ("ETH", ["BTC", "ETH", "SOL", "ADA"]),
        ],
    )
    def test_synthetic_cli_matches_inprocess(self, tmp_path, benchmark, universe):
        out = tmp_path / "s.json"
        cmd = ["--synthetic", "--benchmark", benchmark, "--output", str(out)]
        if universe:
            cmd += ["--universe", *universe]
        r = _run(cmd)
        assert r.returncode == 0, (r.returncode, r.stdout + r.stderr)
        payload = _assert_finite_json(out)
        res = BABStrategy(benchmark=benchmark, universe=universe).run()
        assert math.isclose(
            float(payload["final_cumulative"]),
            float(res.backtest["cumulative"].iloc[-1]),
            abs_tol=1e-12,
        )
        assert payload["periods"] == len(res.backtest)
        assert payload["benchmark"] == benchmark
        assert payload["universe"] == list(res.config.universe)
