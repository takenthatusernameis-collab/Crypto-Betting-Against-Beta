"""Targeted coverage campaign for strategy.py uncovered paths.

Covers:
  - _normalize_position_sizer dict shorthands (lines 40, 44-64)
  - empty universe ValueError (line 223)
  - freeze fallback AttributeError/TypeError path (lines 230-235)
  - shorting_constraints exception re-wrap (lines 280-281)
  - position_sizer exception re-wrap (lines 296-297)
  - regime_filter exception re-wrap (line 320)
"""

from __future__ import annotations

from unittest import mock

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import shorting
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.sizing import (
    EqualWeightSizer,
    KellySizer,
    RiskParitySizer,
    VolatilityTargetSizer,
)
from strategies.betting_against_beta.strategy import (
    BABStrategy,
    _normalize_position_sizer,
)


def _returns(n=80, seed=31):
    idx = pd.date_range("2023-01-01", periods=n, freq="D")
    rng = np.random.default_rng(seed)
    mkt = rng.normal(0, 0.01, n)
    return pd.DataFrame(
        {
            "BTC": mkt,
            "ETH": 0.6 * mkt + rng.normal(0, 0.005, n),
            "SOL": 1.2 * mkt + rng.normal(0, 0.007, n),
        },
        index=idx,
    )


class TestNormalizePositionSizer:
    def test_passthrough_non_dict(self):
        sizer = EqualWeightSizer()
        assert _normalize_position_sizer(sizer) is sizer

    def test_dict_equal(self):
        s = _normalize_position_sizer({"type": "equal", "max_leverage": 2.0})
        assert isinstance(s, EqualWeightSizer)

    def test_dict_kelly(self):
        s = _normalize_position_sizer({"type": "kelly", "lookback": 30, "fraction": 0.5})
        assert isinstance(s, KellySizer)
        assert s.lookback == 30
        assert s.fraction == 0.5

    def test_dict_kelly_fraction_alias(self):
        s = _normalize_position_sizer({"type": "kelly_fraction"})
        assert isinstance(s, KellySizer)

    def test_dict_vol_target_aliases(self):
        for alias in ("vol_target", "volatility_target", "voltarget"):
            s = _normalize_position_sizer({"type": alias, "target_vol": 0.2})
            assert isinstance(s, VolatilityTargetSizer), alias

    def test_dict_risk_parity_aliases(self):
        for alias in ("risk_parity", "riskparity", "rp"):
            s = _normalize_position_sizer({"type": alias})
            assert isinstance(s, RiskParitySizer), alias

    def test_dict_unknown_type_raises(self):
        with pytest.raises(BABDataError):
            _normalize_position_sizer({"type": "bogus"})


class TestEmptyUniverse:
    def test_empty_universe_value_error(self):
        # Only the benchmark column exists -> no tradable assets remain.
        idx = pd.date_range("2023-01-01", periods=40, freq="D")
        df = pd.DataFrame({"BTC": np.random.default_rng(1).normal(0, 0.01, 40)}, index=idx)
        cfg = BABConfig(universe=["ETH"], benchmark="BTC", beta_window=10, min_observations=5)
        with pytest.raises(ValueError):
            BABStrategy(cfg).run(returns_df=df)

    def test_universe_override_empty_falls_back_to_all(self):
        # universe_override=[] -> resolved_universe returns all available columns
        df = _returns(40)
        cfg = BABConfig(universe_override=[], benchmark="BTC", beta_window=10, min_observations=5)
        res = BABStrategy(cfg).run(returns_df=df)
        assert np.isfinite(res.weights.values).all()


class TestFreezeFallback:
    def test_freeze_fallback_path(self):
        # The fallback assignment path (strategy.py:235) is hit when
        # object.__setattr__ raises AttributeError but normal assignment
        # succeeds.  Use a mock config that allows normal assignment.
        df = _returns(40)
        cfg = mock.MagicMock(spec=BABConfig)
        cfg.benchmark = "BTC"
        cfg.beta_window = 10
        cfg.min_observations = 5
        cfg.min_rows = 1
        cfg.universe = ["BTC", "ETH", "SOL"]
        cfg.data_source = None
        cfg.synthetic_seed = 42
        cfg.synthetic_n_days = 252
        cfg.rebalance_freq = "daily"
        cfg.long_quantile = 0.3
        cfg.short_quantile = 0.3
        cfg.dollar_neutral = True
        cfg.transaction_costs = 0.0
        cfg.slippage = 0.0
        cfg.cost_model = (
            None  # freeze-fallback test targets object.__setattr__, not cost-model validation
        )
        cfg.max_turnover = None
        cfg.max_position_size = None
        cfg.gross_exposure_limit = None
        cfg.net_exposure_limit = None
        cfg.max_single_weight = None
        cfg.shorting_constraints = None
        cfg.position_sizer = None
        cfg.regime_filter = False
        cfg.beta_neutral = False
        cfg.beta_neutral_enforcement = False
        cfg.resolved_universe.return_value = ["BTC", "ETH", "SOL"]

        real_object = object

        class _RaisingObject:
            def __setattr__(self, name, value):
                raise AttributeError("simulated slots")

            def __getattr__(self, name):
                return getattr(real_object, name)

        with mock.patch("strategies.betting_against_beta.strategy.object", _RaisingObject()):
            res = BABStrategy(cfg).run(returns_df=df)
        assert np.isfinite(res.weights.values).all()


class TestExceptionRewrap:
    def test_shorting_constraints_typeerror_rewrap(self):
        df = _returns(40)
        cfg = BABConfig(
            shorting_constraints={"max_short_leverage": 1.0}, beta_window=10, min_observations=5
        )
        strat = BABStrategy(cfg)
        with mock.patch(
            "strategies.betting_against_beta.strategy.shorting.apply_shorting_constraints",
            side_effect=TypeError("boom"),
        ), pytest.raises(BABDataError, match="shorting_constraints failed"):
            strat.run(returns_df=df)

    def test_position_sizer_typeerror_rewrap(self):
        df = _returns(40)
        cfg = BABConfig(position_sizer={"type": "equal"}, beta_window=10, min_observations=5)
        strat = BABStrategy(cfg)
        with mock.patch(
            "strategies.betting_against_beta.strategy.sizing.apply_position_sizing",
            side_effect=TypeError("boom"),
        ), pytest.raises(BABDataError, match="position_sizer failed"):
            strat.run(returns_df=df)

    def test_regime_filter_typeerror_rewrap(self):
        df = _returns(40)
        cfg = BABConfig(regime_filter=True, beta_window=10, min_observations=5)
        strat = BABStrategy(cfg)
        with mock.patch(
            "strategies.betting_against_beta.regime.regime_scale_scalar",
            side_effect=TypeError("boom"),
        ), pytest.raises(BABDataError, match="regime_filter failed"):
            strat.run(returns_df=df)
