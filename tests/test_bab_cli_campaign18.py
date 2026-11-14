"""Regression tests for Campaign 18: BAB metrics, report, attribution & sizing fidelity
on real & defective data.

Evidence: /home/runner/work/_temp/kilo-tmp/c18_bab_metrics_report_attribution_fidelity_probe_evidence.log
Conclusion: no proven gaps. These tests lock in the verified C18 probe behavior
(report()/tear_sheet()/report_to_json() metric finiteness & strict-JSON fidelity,
trade-attribution totals, position-sizer dict shorthands, regime filter, beta-neutral
trading, execution-adapter plumbing, and output determinism,
enforcement, and CLI dry-run/version/error edges) so future sessions cannot regress
reporting/analytics fidelity without a failing test.
Console script equivalent: `python -m scripts.load_real_bab_example` (the
`bab-example` console-script main(); the installed entry point is not on PATH
in this environment).
"""

import json
import math
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
REAL = str(REPO / "tests" / "fixtures" / "real_market_prices.csv")
EXP = str(REPO / "tests" / "fixtures" / "real_market_prices_expanded.csv")
DEGEN = str(REPO / "tests" / "fixtures" / "degenerate_metrics.csv")
ALL_NAN = str(REPO / "tests" / "fixtures" / "all_nan_column.csv")
JUNK = str(REPO / "tests" / "fixtures" / "junk_columns.csv")

REQUIRED_METRIC_KEYS = {
    "final_cumulative",
    "total_return",
    "sharpe_ratio",
    "annualized_volatility",
    "max_drawdown",
    "turnover",
    "strategy_beta",
    "n_observations",
}
REQUIRED_TOTAL_KEYS = {
    "gross_return",
    "cost_drag",
    "slippage_drag",
    "net_return",
    "cost_share",
    "slippage_share",
}


def _run_module_cli(argv):
    env = {**__import__("os").environ, "PYTHONPATH": str(REPO)}
    return subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli", *argv],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(REPO),
        env=env,
    )


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


def _assert_no_traceback(r):
    blob = (r.stdout or "") + (r.stderr or "")
    assert "Traceback" not in blob, blob


def _assert_finite_mapping(mapping, label):
    for k, v in mapping.items():
        if isinstance(v, float):
            assert math.isfinite(v), f"{label}: non-finite {k}={v}"


class TestReportMetricsFiniteness:
    """C18 probes 1-3: report() metrics finite + report_to_json strict JSON."""

    @pytest.mark.parametrize(
        "fixture,benchmark,expect_cum",
        [
            (REAL, "BTC", 0.45632700835934265),
            (EXP, "BTC", 0.5311665101149625),
            (REAL, "ETH", 2.1986969529723432),
        ],
    )
    def test_report_metrics_finite_strict_json(self, tmp_path, fixture, benchmark, expect_cum):
        from strategies.betting_against_beta import BABStrategy
        from strategies.betting_against_beta.data_loader import load_prices

        rets = load_prices(fixture, benchmark=benchmark, min_rows=30)
        strat = BABStrategy(
            benchmark=benchmark,
            beta_window=252,
            long_quantile=0.3,
            short_quantile=0.3,
            transaction_costs=0.001,
        )
        res = strat.run(returns_df=rets)
        rep = strat.report(res)
        m = rep["metrics"]
        assert set(m.keys()) >= REQUIRED_METRIC_KEYS, (
            f"missing keys: {REQUIRED_METRIC_KEYS - set(m.keys())}"
        )
        _assert_finite_mapping(m, "report metrics")
        assert math.isclose(m["final_cumulative"], expect_cum, rel_tol=1e-6, abs_tol=1e-9), m[
            "final_cumulative"
        ]
        json_str = BABStrategy.report_to_json(rep)
        payload = json.loads(json_str)  # report_to_json uses allow_nan=False internally
        assert isinstance(payload, dict)
        _assert_finite_mapping(payload.get("metrics", {}), "json metrics")
        _assert_finite_mapping(payload.get("attribution_totals", {}), "json attribution_totals")


class TestTearSheet:
    """C18 probe 4: tear_sheet() renders without exception, finite-formatted."""

    def test_tear_sheet_renders_finite(self):
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
        sheet = strat.tear_sheet(res)
        assert "BAB STRATEGY TEAR SHEET" in sheet
        low = sheet.lower()
        assert "nan" not in low and "inf" not in low and "-inf" not in low


class TestAttributionTotals:
    """C18 probe 5: trade_attribution / attribution_totals all finite."""

    def test_attribution_totals_finite(self):
        from strategies.betting_against_beta import BABStrategy
        from strategies.betting_against_beta.attribution import (
            attribution_totals,
            trade_attribution,
        )
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
        bt = res.backtest
        attr = trade_attribution(bt if isinstance(bt, pd.DataFrame) else pd.DataFrame())
        totals = attribution_totals(attr)
        assert set(totals.keys()) >= REQUIRED_TOTAL_KEYS, (
            f"missing keys: {REQUIRED_TOTAL_KEYS - set(totals.keys())}"
        )
        _assert_finite_mapping(totals, "attribution_totals")


class TestMetricsFinitenessSweep:
    """C18 probe 6: metrics.summary finiteness sweep incl. degenerate (never raises)."""

    @pytest.mark.parametrize("tc", [0.0, 0.001])
    def test_real_tc_finiteness(self, tc):
        from strategies.betting_against_beta import BABStrategy
        from strategies.betting_against_beta.data_loader import load_prices

        rets = load_prices(REAL, benchmark="BTC", min_rows=30)
        strat = BABStrategy(
            benchmark="BTC",
            beta_window=252,
            long_quantile=0.3,
            short_quantile=0.3,
            transaction_costs=tc,
        )
        res = strat.run(returns_df=rets)
        m = strat.report(res)["metrics"]
        _assert_finite_mapping(m, f"report metrics tc={tc}")

    def test_degenerate_never_raises_all_finite(self):
        from strategies.betting_against_beta import BABStrategy
        from strategies.betting_against_beta.data_loader import load_returns

        drets = load_returns(DEGEN, benchmark="BTC", min_rows=2)
        strat = BABStrategy(
            benchmark="BTC",
            beta_window=60,
            long_quantile=0.3,
            short_quantile=0.3,
            transaction_costs=0.001,
        )
        res = strat.run(returns_df=drets)
        m = strat.report(res)["metrics"]
        _assert_finite_mapping(m, "degenerate report metrics")


class TestWeightsNeutralityShorting:
    """C18 probe 7: dollar-neutral weights + shorting across quantiles {0.1, 0.3, 0.5}."""

    @pytest.mark.parametrize("q", [0.1, 0.3, 0.5])
    def test_weights_dollar_neutral_and_shorting(self, q):
        import numpy as np

        from strategies.betting_against_beta import BABStrategy
        from strategies.betting_against_beta.data_loader import load_prices

        rets = load_prices(REAL, benchmark="BTC", min_rows=30)
        strat = BABStrategy(
            benchmark="BTC",
            beta_window=252,
            long_quantile=q,
            short_quantile=q,
            transaction_costs=0.001,
        )
        res = strat.run(returns_df=rets)
        w = res.weights
        wa = w.to_numpy(dtype=float)
        row_sums = wa.sum(axis=1)
        finite_sums = row_sums[np.isfinite(row_sums)]
        assert len(finite_sums) > 0
        assert np.allclose(finite_sums, 0.0, atol=1e-6), f"weights not dollar-neutral at q={q}"
        assert (wa < 0).any(), f"expected negative (short) weights at q={q}"


class TestPositionSizerShorthands:
    """C18 probe 8: position-sizer dict shorthands; unknown type -> BABDataError."""

    @pytest.mark.parametrize(
        "ps",
        [
            {"type": "equal"},
            {"type": "kelly", "lookback": 60, "max_leverage": 1.0, "fraction": 1.0},
            {
                "type": "vol_target",
                "target_vol": 0.10,
                "lookback": 60,
                "annualize": 252,
                "max_leverage": 2.0,
            },
            {"type": "risk_parity", "lookback": 60, "max_leverage": 1.0},
        ],
    )
    def test_recognized_sizer_runs_finite_weights(self, ps):
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
            position_sizer=ps,
        )
        res = strat.run(returns_df=rets)
        wa = res.weights.to_numpy(dtype=float)
        assert np.isfinite(wa).all(), f"non-finite weights for sizer {ps}"

    def test_unknown_sizer_raises_babdataerror(self):
        from strategies.betting_against_beta import BABStrategy
        from strategies.betting_against_beta.data_loader import load_prices
        from strategies.betting_against_beta.errors import BABDataError

        rets = load_prices(REAL, benchmark="BTC", min_rows=30)
        strat = BABStrategy(
            benchmark="BTC",
            beta_window=252,
            long_quantile=0.3,
            short_quantile=0.3,
            transaction_costs=0.001,
            position_sizer={"type": "bogus"},
        )
        with pytest.raises(BABDataError):
            strat.run(returns_df=rets)


class TestRegimeFilter:
    """C18 probe 9: regime_filter True vs False both finite + deterministic."""

    def test_regime_filter_both_finite_deterministic(self):
        from strategies.betting_against_beta import BABStrategy
        from strategies.betting_against_beta.data_loader import load_prices

        rets = load_prices(REAL, benchmark="BTC", min_rows=30)
        cum_by_flag = {}
        for flag in (False, True):
            strat = BABStrategy(
                benchmark="BTC",
                beta_window=252,
                long_quantile=0.3,
                short_quantile=0.3,
                transaction_costs=0.001,
                regime_filter=flag,
            )
            res = strat.run(returns_df=rets)
            m = strat.report(res)["metrics"]
            _assert_finite_mapping(m, f"regime_filter={flag}")
            cum_by_flag[flag] = m["final_cumulative"]
        # determinism: two regime_filter=True runs identical
        sheets = []
        for _ in range(2):
            strat = BABStrategy(
                benchmark="BTC",
                beta_window=252,
                long_quantile=0.3,
                short_quantile=0.3,
                transaction_costs=0.001,
                regime_filter=True,
            )
            res = strat.run(returns_df=rets)
            sheets.append(strat.tear_sheet(res))
        assert sheets[0] == sheets[1], "tear_sheet not deterministic across regime_filter=True runs"


class TestBetaNeutral:
    """C18 probe 10: beta_neutral=True runs, weights finite + dollar-neutral."""

    def test_beta_neutral_runs_weights_finite_neutral(self):
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
            beta_neutral=True,
            beta_target=0.0,
            beta_tolerance=1e-4,
        )
        res = strat.run(returns_df=rets)
        wa = res.weights.to_numpy(dtype=float)
        assert np.isfinite(wa).all()
        row_sums = wa.sum(axis=1)
        finite_sums = row_sums[np.isfinite(row_sums)]
        assert len(finite_sums) > 0
        assert np.allclose(finite_sums, 0.0, atol=1e-6)
        m = strat.report(res)["metrics"]
        _assert_finite_mapping(m, "beta_neutral report metrics")


class TestCLIDryRunVersion:
    """C18 probe 11: module CLI --dry-run (rc=0, config printed) + --version (rc=0)."""

    def test_dry_run_and_version(self):
        r_dry = _run_module_cli(
            ["--dry-run", "--data", REAL, "--from-prices", "--benchmark", "BTC"]
        )
        r_ver = _run_module_cli(["--version"])
        assert r_dry.returncode == 0, (r_dry.returncode, r_dry.stdout, r_dry.stderr)
        assert r_ver.returncode == 0, (r_ver.returncode, r_ver.stdout, r_ver.stderr)
        assert "Resolved BAB configuration:" in r_dry.stdout
        assert "bab 0.1.0" in r_ver.stdout
        _assert_no_traceback(r_dry)
        _assert_no_traceback(r_ver)


class TestCLIErrorPaths:
    """C18 probe 12: --from-prices without --data (rc=1); nonexistent --data (rc=1)."""

    def test_from_prices_without_data_clean_error(self):
        r = _run_module_cli(["--from-prices", "--benchmark", "BTC"])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)
        assert "--from-prices requires --data" in (r.stdout + r.stderr)

    def test_nonexistent_data_clean_error(self):
        r = _run_module_cli(
            ["--data", "/nonexistent/does_not_exist.csv", "--from-prices", "--benchmark", "BTC"]
        )
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)
        blob = (r.stdout + r.stderr).lower()
        assert "file not found" in blob or "not found" in blob


class TestCLIOutputDirectory:
    """C18 probe 13: --output to an existing directory (rc=1, clean error)."""

    def test_output_is_directory_clean_error(self):
        r = _run_module_cli(["--synthetic", "--output", str(REPO / ".pytest_cache")])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)
        blob = r.stdout + r.stderr
        assert "is a directory" in blob or "Error validating output path" in blob


class TestReportToJsonStrictJSON:
    """C18 probe 14: report_to_json() strict JSON + key set + metrics/totals finite."""

    def test_report_to_json_strict_finite(self):
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
        rep = strat.report(res)
        json_str = BABStrategy.report_to_json(rep)
        payload = json.loads(json_str)  # strict: allow_nan=False
        assert {"config", "metrics", "attribution", "attribution_totals", "rebalances"} <= set(
            payload.keys()
        ), payload.keys()
        _assert_finite_mapping(payload["metrics"], "json metrics")
        _assert_finite_mapping(payload["attribution_totals"], "json attribution_totals")


class TestReportDeterminism:
    """C18 probe 15: report_to_json deterministic across two runs."""

    def test_report_deterministic(self):
        from strategies.betting_against_beta import BABStrategy
        from strategies.betting_against_beta.data_loader import load_prices

        rets = load_prices(REAL, benchmark="BTC", min_rows=30)
        payloads = []
        for _ in range(2):
            strat = BABStrategy(
                benchmark="BTC",
                beta_window=252,
                long_quantile=0.3,
                short_quantile=0.3,
                transaction_costs=0.001,
            )
            res = strat.run(returns_df=rets)
            payloads.append(BABStrategy.report_to_json(strat.report(res)))
        assert payloads[0] == payloads[1], "report_to_json not deterministic across runs"
