"""Backtest/metrics/report contract smoke (campaign11 slice f, evidence-first).

Contracts asserted only where present in current API:
- BABResult.backtest DataFrame columns: returns,gross_return,cost_drag,slippage_drag,cumulative
  (verified against run_backtest + strategy + fixture runs)
- monotonic index, finite scalar values, len parity with CLI periods on fixtures
- BABStrategy.report()/tear_sheet() exist and return finite/serializable outputs for a
  deterministic synthetic run (cheap). No production changes.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.cli import main
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.data_loader import load_prices, load_returns

BACKTEST_COLUMNS = [
    "returns",
    "gross_return",
    "cost_drag",
    "slippage_drag",
    "cumulative",
]
PRICE_FIXTURES = [
    "tests/fixtures/real_market_prices.csv",
    "tests/fixtures/real_market_prices_expanded.csv",
]
RETURNS_FIXTURE = "tests/fixtures/returns.json"


def _cli_run(argv):
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "o.json"
        rc = main([*argv, "--output", str(out)])
        payload = json.loads(out.read_text()) if out.exists() else None
        return rc, payload


def _assert_backtest_contract(bt: pd.DataFrame) -> None:
    assert isinstance(bt, pd.DataFrame)
    assert list(bt.columns) == BACKTEST_COLUMNS
    assert bt.index.is_monotonic_increasing
    assert len(bt) > 0
    for col in BACKTEST_COLUMNS:
        s = bt[col]
        assert s.notna().all(), f"{col} has NA"
        arr = s.to_numpy(dtype=float)
        assert np.isfinite(arr).all(), f"{col} not finite"
    # cumulative is a positive finite series in normal runs (log1p/exp path has guards);
    # assert positivity only as a soft contract consistent with observed fixture behavior.
    cum = bt["cumulative"].to_numpy(dtype=float)
    assert (cum > 0).all()
    # drag columns are non-negative for standard cost/slippage configs (>=0 scalars)
    assert (bt["cost_drag"].to_numpy(dtype=float) >= 0).all()
    assert (bt["slippage_drag"].to_numpy(dtype=float) >= 0).all()


class TestBacktestContractFixtures:
    @pytest.mark.parametrize("fixture", PRICE_FIXTURES)
    def test_price_fixture_backtest_contract_and_cli_periods(self, fixture):
        df = load_prices(fixture, benchmark="BTC", min_rows=BABConfig().min_rows)
        result = BABStrategy(benchmark="BTC", beta_window=90).run(returns_df=df)
        _assert_backtest_contract(result.backtest)
        rc, payload = _cli_run(
            ["--data", fixture, "--from-prices", "--benchmark", "BTC", "--beta-window", "90"]
        )
        assert rc == 0
        assert payload["periods"] == len(result.backtest)
        tail = float(result.backtest["cumulative"].iloc[-1])
        assert math.isfinite(tail)
        assert payload["final_cumulative"] == pytest.approx(tail, rel=0, abs=1e-12)

    def test_returns_fixture_backtest_contract_and_cli_periods(self):
        df = load_returns(RETURNS_FIXTURE, benchmark="BTC", min_rows=BABConfig().min_rows)
        result = BABStrategy(benchmark="BTC").run(returns_df=df)
        _assert_backtest_contract(result.backtest)
        rc, payload = _cli_run(["--data", RETURNS_FIXTURE, "--benchmark", "BTC"])
        assert rc == 0
        assert payload["periods"] == len(result.backtest)
        tail = float(result.backtest["cumulative"].iloc[-1])
        assert payload["final_cumulative"] == pytest.approx(tail, rel=0, abs=1e-12)


class TestBacktestContractSynthetic:
    @pytest.mark.parametrize(
        "cfg_kwargs",
        [
            dict(universe=None, benchmark="BTC", beta_window=30),
            dict(universe=None, benchmark="BTC", beta_window=30, transaction_costs=0.001),
            dict(universe=None, benchmark="BTC", beta_window=30, slippage=0.0005),
        ],
    )
    def test_synthetic_backtest_contract(self, cfg_kwargs):
        result = BABStrategy(BABConfig(**cfg_kwargs)).run()
        _assert_backtest_contract(result.backtest)
        # net returns should be finite and consistent with gross/cost/slippage presence
        net = result.backtest["returns"].to_numpy(dtype=float)
        gross = result.backtest["gross_return"].to_numpy(dtype=float)
        assert np.isfinite(net).all() and np.isfinite(gross).all()

    def test_synthetic_cli_periods_and_tail_match_config_parity(self):
        cfg = BABConfig(
            universe=None,
            benchmark="BTC",
            beta_window=30,
            long_quantile=0.3,
            short_quantile=0.3,
            rebalance_freq="daily",
            transaction_costs=0.0,
            slippage=0.0,
        )
        result = BABStrategy(cfg).run()
        rc, payload = _cli_run(
            [
                "--synthetic",
                "--beta-window",
                "30",
                "--benchmark",
                "BTC",
                "--long-quantile",
                "0.3",
                "--short-quantile",
                "0.3",
                "--rebalance-freq",
                "daily",
                "--transaction-costs",
                "0.0",
                "--slippage",
                "0.0",
            ]
        )
        assert rc == 0
        assert payload["periods"] == len(result.backtest)
        assert payload["final_cumulative"] == pytest.approx(
            float(result.backtest["cumulative"].iloc[-1]), rel=0, abs=1e-12
        )


class TestStrategyReportTearSheetSmoke:
    """report()/tear_sheet() are present on BABStrategy (evidence); smoke finite/serializable."""

    @pytest.mark.parametrize("beta_window", [30, 90])
    def test_report_and_tear_sheet_finite(self, beta_window):
        s = BABStrategy(benchmark="BTC", beta_window=beta_window)
        r = s.run()
        report = s.report(r)
        ts = s.tear_sheet(r)
        assert isinstance(report, dict)
        assert isinstance(ts, str) and len(ts) > 0
        # report must be JSON-serializable with default=str (API may include DataFrames/objects)
        raw = json.dumps(report, default=str, allow_nan=False)
        assert "NaN" not in raw and "Infinity" not in raw

        def walk(x):
            if isinstance(x, dict):
                for v in x.values():
                    walk(v)
            elif isinstance(x, (list, tuple)):
                for v in x:
                    walk(v)
            elif isinstance(x, np.ndarray):
                arr = x.astype(float, copy=False) if np.issubdtype(x.dtype, np.number) else None
                if arr is not None:
                    assert np.isfinite(arr).all()
            elif isinstance(x, pd.Series):
                if np.issubdtype(x.dtype, np.number):
                    assert np.isfinite(x.to_numpy(dtype=float)).all()
            elif isinstance(x, (int, float)) and not isinstance(x, bool):
                assert math.isfinite(float(x))

        walk(report)
