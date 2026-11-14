"""Regression tests for Campaign 17: BAB strategy core pipeline fidelity on real & defective data.

Evidence: /home/runner/work/_temp/kilo-tmp/c17_bab_strategy_core_fidelity_probe_evidence.log
Conclusion: no proven gaps. These tests lock in the verified C17 probe behavior
(subprocess + in-process: console/module CLI --output JSON schema & finiteness,
periods==398 on real fixtures, benchmark passthrough, lookback/quantile variants,
determinism, defective-fixture clean error paths rc=1 with actionable messages and
no output JSON, in-process console<->BABStrategy.run parity, dollar-neutral weights
with shorting coverage) so future sessions cannot regress core pipeline fidelity
without a failing test.

Console script equivalent: `python -m scripts.load_real_bab_example` (the
`bab-example` console-script main(); the installed entry point is not on PATH
in this environment).
"""

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
REAL = str(REPO / "tests" / "fixtures" / "real_market_prices.csv")
EXP = str(REPO / "tests" / "fixtures" / "real_market_prices_expanded.csv")
DEFECTS = str(REPO / "tests" / "fixtures" / "real_data_defects.csv")
BENCH_NAN = str(REPO / "tests" / "fixtures" / "benchmark_nan_window.csv")
ALL_NAN = str(REPO / "tests" / "fixtures" / "all_nan_column.csv")
JUNK = str(REPO / "tests" / "fixtures" / "junk_columns.csv")
DEGEN = str(REPO / "tests" / "fixtures" / "degenerate_metrics.csv")
TMP_DIR = str(REPO / ".pytest_cache" / "c17")

EXPECTED_KEYS = {"final_cumulative", "periods", "benchmark", "universe"}


def _run_bab_example(argv):
    env = {**__import__("os").environ, "PYTHONPATH": str(REPO)}
    return subprocess.run(
        [sys.executable, "-m", "scripts.load_real_bab_example", *argv],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(REPO),
        env=env,
    )


def _run_cli(argv):
    env = {**__import__("os").environ, "PYTHONPATH": str(REPO)}
    return subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli", *argv],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(REPO),
        env=env,
    )


def _assert_no_traceback(r):
    blob = (r.stdout or "") + (r.stderr or "")
    assert "Traceback" not in blob, blob


def _assert_finite_json(path):
    payload = json.loads(path.read_text())
    assert set(payload.keys()) >= EXPECTED_KEYS, payload.keys()
    for k, v in payload.items():
        if isinstance(v, float):
            assert math.isfinite(v), f"non-finite JSON value {k}={v}"
    return payload


class TestConsoleScriptReportingSchema:
    """C17 probes 1-6: bab-example --output writes valid finite JSON summary."""

    @pytest.mark.parametrize(
        "argv,expect_benchmark,expect_periods",
        [
            ([REAL, "--from-prices", "--benchmark", "BTC"], "BTC", 398),
            ([EXP, "--from-prices", "--benchmark", "BTC"], "BTC", 398),
            ([REAL, "--from-prices", "--benchmark", "ETH"], "ETH", 398),
            ([REAL, "--from-prices", "--benchmark", "BTC", "--lookback", "60"], "BTC", 398),
            ([REAL, "--from-prices", "--benchmark", "BTC", "--quantile", "0.2"], "BTC", 398),
        ],
    )
    def test_output_json_valid_finite_keys(self, tmp_path, argv, expect_benchmark, expect_periods):
        out = tmp_path / "out.json"
        r = _run_bab_example([*argv, "--output", str(out)])
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        assert r.stderr == "", r.stderr
        assert "cumulative_return=" in r.stdout
        assert "periods=" in r.stdout
        _assert_no_traceback(r)
        assert out.exists()
        payload = _assert_finite_json(out)
        assert payload["benchmark"] == expect_benchmark
        assert isinstance(payload["periods"], int) and payload["periods"] == expect_periods
        assert isinstance(payload["final_cumulative"], (int, float))


class TestModuleCliSyntheticReporting:
    """C17 probe module CLI --synthetic --output."""

    def test_synthetic_output_json(self, tmp_path):
        out = tmp_path / "out.json"
        r = _run_cli(["--synthetic", "--output", str(out)])
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        assert r.stderr == "", r.stderr
        assert out.exists()
        payload = _assert_finite_json(out)
        assert isinstance(payload["periods"], int) and payload["periods"] > 0


class TestConsoleScriptDeterminism:
    """C17 probe: repeated runs produce identical stdout and JSON."""

    def test_deterministic_repeat(self, tmp_path):
        outs, cumulatives, periods = [], [], []
        for _ in range(2):
            out = tmp_path / f"out{len(outs)}.json"
            r = _run_bab_example(
                [REAL, "--from-prices", "--benchmark", "BTC", "--output", str(out)]
            )
            assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
            assert r.stderr == "", r.stderr
            outs.append(r.stdout)
            payload = _assert_finite_json(out)
            cumulatives.append(payload["final_cumulative"])
            periods.append(payload["periods"])
        assert outs[0] == outs[1], "stdout not deterministic across repeats"
        assert cumulatives[0] == cumulatives[1], "final_cumulative not deterministic"
        assert periods[0] == periods[1] == 398, "periods not deterministic"


class TestConsoleScriptDefectiveFixtures:
    """C17 probes 8-10: defective fixtures -> clean rc (0 or 1), no Traceback,
    no non-finite/corrupt JSON when --output written."""

    @pytest.mark.parametrize("fixture", [DEGEN, BENCH_NAN, DEFECTS])
    def test_defective_fixture_clean_error(self, tmp_path, fixture):
        out = tmp_path / "out.json"
        r = _run_bab_example([fixture, "--from-prices", "--benchmark", "BTC", "--output", str(out)])
        assert r.returncode in (0, 1), (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)
        assert r.stdout or r.stderr, "expected actionable error or run message"
        if out.exists():
            payload = _assert_finite_json(out)


class TestConsoleScriptNaNDefectPaths:
    """C17 probe 13: junk_columns / all_nan_column -> rc=1, actionable, no output JSON."""

    @pytest.mark.parametrize("fixture", [ALL_NAN, JUNK])
    def test_nan_defect_no_output_json(self, tmp_path, fixture):
        out = tmp_path / "out.json"
        if out.exists():
            out.unlink()
        r = _run_bab_example([fixture, "--from-prices", "--benchmark", "BTC", "--output", str(out)])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)
        assert not out.exists(), f"output JSON must not be created for {fixture}"
        assert r.stdout or r.stderr, "expected actionable error message"


class TestConsoleScriptInProcessParity:
    """C17 probe 11: console --output JSON matches BABStrategy.run in-process."""

    @pytest.mark.parametrize(
        "argv,expect_cum,expect_periods",
        [
            ([REAL, "--from-prices", "--benchmark", "BTC"], 0.45632700835934265, 398),
            ([EXP, "--from-prices", "--benchmark", "BTC"], 0.5311665101149625, 398),
            ([REAL, "--from-prices", "--benchmark", "ETH"], 2.1986969529723432, 398),
        ],
    )
    def test_console_vs_in_process_parity(self, tmp_path, argv, expect_cum, expect_periods):
        out = tmp_path / "out.json"
        r = _run_bab_example([*argv, "--output", str(out)])
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        console = _assert_finite_json(out)
        assert console["periods"] == expect_periods
        assert math.isclose(console["final_cumulative"], expect_cum, rel_tol=1e-6, abs_tol=1e-9)

        from strategies.betting_against_beta import BABStrategy
        from strategies.betting_against_beta.data_loader import load_prices

        data_path = argv[0]
        benchmark = argv[argv.index("--benchmark") + 1]
        lookback = int(argv[argv.index("--lookback") + 1]) if "--lookback" in argv else 252
        rets = load_prices(data_path, benchmark=benchmark, min_rows=30)
        strat = BABStrategy(
            benchmark=benchmark,
            beta_window=lookback,
            long_quantile=0.3,
            short_quantile=0.3,
            transaction_costs=0.001,
        )
        res = strat.run(returns_df=rets)
        bt = getattr(res, "backtest", None)
        ip_periods = len(bt) if bt is not None and hasattr(bt, "__len__") else 0
        ip_cum = None
        if bt is not None and hasattr(bt, "columns") and "cumulative" in bt.columns:
            try:
                ip_cum = float(bt["cumulative"].iloc[-1])
            except Exception:
                ip_cum = None
        assert console["periods"] == ip_periods, (console, ip_periods)
        assert ip_cum is not None
        assert math.isclose(console["final_cumulative"], ip_cum, rel_tol=1e-6, abs_tol=1e-9), (
            console["final_cumulative"],
            ip_cum,
        )


class TestInProcessWeightsNeutralityShorting:
    """C17 probe 12: portfolio weights dollar-neutral (sum ~ 0) with shorting coverage."""

    def test_weights_dollar_neutral_and_shorting(self):
        import numpy as np

        from strategies.betting_against_beta import BABStrategy
        from strategies.betting_against_beta.data_loader import load_prices

        rets = load_prices(REAL, benchmark="BTC", min_rows=30)
        strat = BABStrategy(
            benchmark="BTC",
            beta_window=252,
            long_quantile=0.3,
            short_quantile=0.3,
            transaction_costs=0.001,
        )
        res = strat.run(returns_df=rets)
        weights = getattr(res, "weights", None)
        assert weights is not None and hasattr(weights, "shape")
        wa = weights.to_numpy(dtype=float)
        row_sums = wa.sum(axis=1)
        finite_sums = row_sums[np.isfinite(row_sums)]
        assert len(finite_sums) > 0
        assert np.allclose(finite_sums, 0.0, atol=1e-6), (
            f"weights not dollar-neutral: row sums {finite_sums[:5]}"
        )
        assert (wa < 0).any(), "expected negative (short) weights present"
        assert wa.shape[1] == 8, f"expected 8 assets, got {wa.shape[1]}"
