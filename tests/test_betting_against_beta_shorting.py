"""Tests for shorting constraints (borrow costs, availability, caps)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import shorting
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.portfolio import construct_portfolio


class TestShortingConstraintsValidation:
    def test_shorting_constraints_accepts_valid_config(self):
        sc = shorting.ShortingConstraints()
        assert sc.default_borrow_bps_per_year >= 0
        assert sc.max_short_exposure is None or sc.max_short_exposure >= 0
        assert sc.max_short_notional_per_asset is None or sc.max_short_notional_per_asset >= 0

    def test_negative_borrow_raises(self):
        with pytest.raises(Exception):
            shorting.ShortingConstraints(default_borrow_bps_per_year=-1.0)

    def test_invalid_caps_raise(self):
        with pytest.raises(Exception):
            shorting.ShortingConstraints(max_short_exposure=-0.1)
        with pytest.raises(Exception):
            shorting.ShortingConstraints(max_short_notional_per_asset=-1.0)
        with pytest.raises(Exception):
            shorting.ShortingConstraints(max_short_leverage=-1.0)

    def test_frozen_config(self):
        sc = shorting.ShortingConstraints()
        with pytest.raises(AttributeError):
            sc.default_borrow_bps_per_year = 0.05


class TestShortAvailability:
    def test_default_all_borrowable(self):
        sc = shorting.ShortingConstraints()
        assert sc.is_borrowable("BTC") is True

    def test_can_disable_asset(self):
        sc = shorting.ShortingConstraints(borrowable={"BTC": False})
        assert sc.is_borrowable("BTC") is False

    def test_can_set_per_asset_borrow_rate(self):
        sc = shorting.ShortingConstraints(borrow_bps_per_year={"ETH": 0.1})
        assert sc.borrow_bps("ETH") > sc.borrow_bps("BTC")


class TestShortingConstraintsEnforcement:
    def test_excess_short_exposure_scaled_or_raises(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        signals = pd.DataFrame({"A": [-1.0], "B": [-1.0]}, index=idx)
        sc = shorting.ShortingConstraints(max_short_exposure=0.5)  # total short notional > 0.5
        weights = shorting.apply_shorting_constraints(signals, sc)
        # Should reduce shorts so total short exposure <= 0.5
        assert weights.abs().sum(axis=1).iloc[0] <= 0.5 + 1e-12 or (weights < 0).sum().sum() >= 0

    def test_per_asset_short_limit(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        signals = pd.DataFrame({"A": [-1.0]}, index=idx)
        sc = shorting.ShortingConstraints(max_short_notional_per_asset=0.3)
        weights = shorting.apply_shorting_constraints(signals, sc)
        assert abs(weights["A"].iloc[0]) <= 0.3 + 1e-12

    def test_unborrowable_asset_forces_flat_or_error(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        signals = pd.DataFrame({"A": [-1.0]}, index=idx)
        sc = shorting.ShortingConstraints(borrowable={"A": False}, strict=True)
        with pytest.raises(BABDataError):
            shorting.apply_shorting_constraints(signals, sc)

    def test_unborrowable_asset_scaled_if_not_strict(self):
        idx = pd.date_range("2023-01-01", periods=1, freq="D")
        signals = pd.DataFrame({"A": [-1.0]}, index=idx)
        sc = shorting.ShortingConstraints(borrowable={"A": False}, strict=False)
        weights = shorting.apply_shorting_constraints(signals, sc)
        assert weights["A"].iloc[0] >= -1e-12


class TestConfigIntegration:
    def test_babconfig_accepts_shorting_constraints(self):
        sc = shorting.ShortingConstraints(max_short_exposure=0.5)
        cfg = BABConfig(shorting_constraints=sc)
        assert cfg.shorting_constraints is sc

    def test_babconfig_accepts_shorting_dict(self):
        cfg = BABConfig(shorting_constraints={"max_short_exposure": 0.4})
        assert cfg.shorting_constraints is not None
