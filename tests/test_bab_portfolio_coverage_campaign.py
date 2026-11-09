"""Coverage campaign for strategies/betting_against_beta/portfolio.py.

Real-behavior tests (no vacuous mocks) targeting the uncovered portfolio
construction paths: signal string cleaning, None/empty input, kwargs limit
aliases, dollar-neutrality per-row adjustment, position/turnover/net exposure
validation, risk-check bad-type defaults, and enforce_beta_neutrality guards.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.portfolio import (
    _clean_signal_value,
    construct_portfolio,
    enforce_beta_neutrality,
)


class TestCleanSignalValueStringBranch:
    def test_string_one_returns_long(self):
        assert _clean_signal_value("1") == 1

    def test_string_minus_one_returns_short(self):
        assert _clean_signal_value("-1") == -1

    def test_string_non_numeric_returns_zero(self):
        assert _clean_signal_value("abc") == 0
        assert _clean_signal_value("xyz") == 0

    def test_string_float_one_returns_long(self):
        assert _clean_signal_value("1.0") == 1
        assert _clean_signal_value("1.5") == 1  # int(1.5) == 1

    def test_string_other_number_returns_zero(self):
        # Parses to a number but not +/- 1 -> falls through to return 0.
        assert _clean_signal_value("2") == 0
        assert _clean_signal_value("-2.5") == 0
        assert _clean_signal_value("0") == 0


class TestConstructPortfolioEarlyReturns:
    def test_none_input_returns_empty_frame(self):
        out = construct_portfolio(None)
        assert isinstance(out, pd.DataFrame)
        assert out.empty

    def test_non_dataframe_input_returns_empty_frame(self):
        out = construct_portfolio([1, -1, 0])
        assert isinstance(out, pd.DataFrame)
        assert out.empty

    def test_empty_dataframe_returns_empty_frame(self):
        out = construct_portfolio(pd.DataFrame())
        assert isinstance(out, pd.DataFrame)
        assert out.empty


class TestKwargsLimitAliasResolution:
    def test_max_turnover_kwargs_alias_resolved(self):
        sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1]}, index=[0, 1])
        # max_total_turnover alias should bind max_turnover without error.
        out = construct_portfolio(sig, dollar_neutral=True, max_total_turnover=0.5)
        assert isinstance(out, pd.DataFrame)
        assert np.isfinite(out.to_numpy()).all()

    def test_max_position_size_kwargs_alias_resolved(self):
        sig = pd.DataFrame({"A": [1], "B": [-1]}, index=[0])
        out = construct_portfolio(sig, dollar_neutral=True, max_pos_size=1.0)
        assert isinstance(out, pd.DataFrame)
        assert np.isfinite(out.to_numpy()).all()


class TestDollarNeutralityAdjustmentLoop:
    def test_dollar_neutral_normalizes_long_and_short_sides(self):
        # One long and one short on the same row -> both sides exist -> the
        # per-row dollar-neutrality adjustment loop (152-157) runs.
        sig = pd.DataFrame({"A": [1], "B": [-1]}, index=[0])
        out = construct_portfolio(sig, dollar_neutral=True)
        assert abs(out.loc[0, "A"] - 1.0) < 1e-12
        assert abs(out.loc[0, "B"] - (-1.0)) < 1e-12
        assert abs(out.sum(axis=1).iloc[0]) < 1e-12

    def test_dollar_neutral_multi_asset_row(self):
        sig = pd.DataFrame(
            {"A": [1], "B": [1], "C": [-1], "D": [-1]}, index=[0]
        )
        out = construct_portfolio(sig, dollar_neutral=True)
        longs = out.loc[0, ["A", "B"]]
        shorts = out.loc[0, ["C", "D"]]
        assert (longs > 0).all()
        assert (shorts < 0).all()
        assert abs(out.sum(axis=1).iloc[0]) < 1e-12


class TestPositionTurnoverRiskValidation:
    def test_max_position_size_non_positive_raises(self):
        sig = pd.DataFrame({"A": [1]}, index=[0])
        with pytest.raises(BABDataError):
            construct_portfolio(sig, dollar_neutral=True, max_position_size=0)

    def test_max_position_size_exceeded_raises(self):
        # Single long asset gets weight 1.0, exceeding max_single_weight=0.5.
        sig = pd.DataFrame({"A": [1]}, index=[0])
        with pytest.raises(BABDataError):
            construct_portfolio(
                sig, dollar_neutral=True, max_single_weight=0.5, enforce_risk_checks=True
            )

    def test_max_turnover_non_positive_raises(self):
        sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1]}, index=[0, 1])
        prev = pd.DataFrame({"A": [1.0, -1.0], "B": [-1.0, 1.0]}, index=[0, 1])
        with pytest.raises(BABDataError):
            construct_portfolio(
                sig,
                dollar_neutral=True,
                max_turnover=0,
                weights_df_prev=prev,
            )

    def test_turnover_limit_check_raises(self):
        sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1]}, index=[0, 1])
        prev = pd.DataFrame({"A": [-1.0, 1.0], "B": [1.0, -1.0]}, index=[0, 1])
        # Turnover = 1.0 per row > max_turnover 0.5 -> raise.
        with pytest.raises(BABDataError):
            construct_portfolio(
                sig,
                dollar_neutral=True,
                max_turnover=0.5,
                weights_df_prev=prev,
            )

    def test_turnover_babdataerror_reraised(self):
        sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1]}, index=[0, 1])
        prev = pd.DataFrame({"A": [-1.0, 1.0], "B": [1.0, -1.0]}, index=[0, 1])
        with pytest.raises(BABDataError):
            construct_portfolio(
                sig,
                dollar_neutral=True,
                max_turnover=0.5,
                weights_df_prev=prev,
            )

    def test_turnover_inner_except_on_non_numeric_prev(self):
        # weights_df_prev with string columns makes cur - prev raise TypeError
        # inside the turnover try; the inner except swallows it (200-201).
        sig = pd.DataFrame({"a": [1, -1], "b": [-1, 1]}, index=[0, 1])
        prev = pd.DataFrame({"a": ["x", "y"], "b": ["p", "q"]}, index=[0, 1])
        w = construct_portfolio(
            sig, dollar_neutral=True, max_turnover=0.5, weights_df_prev=prev
        )
        assert isinstance(w, pd.DataFrame)
        assert np.isfinite(w.to_numpy()).all()
        assert w.loc[0, "a"] == 1.0
        assert w.loc[1, "a"] == -1.0

    def test_risk_checks_bad_types_use_defaults(self):
        sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1]}, index=[0, 1])
        # gross_exposure_limit unparseable -> falls back to default 2.0 (207-208).
        out = construct_portfolio(
            sig,
            dollar_neutral=True,
            enforce_risk_checks=True,
            gross_exposure_limit="not-a-number",
        )
        assert isinstance(out, pd.DataFrame)
        assert np.isfinite(out.to_numpy()).all()

    def test_gross_exposure_limit_raises(self):
        sig = pd.DataFrame({"A": [1], "B": [-1]}, index=[0])
        with pytest.raises(BABDataError):
            construct_portfolio(
                sig,
                dollar_neutral=True,
                enforce_risk_checks=True,
                gross_exposure_limit=0.5,
            )

    def test_net_exposure_limit_raises(self):
        # dollar_neutral=False with only longs -> net exposure exceeds limit.
        sig = pd.DataFrame({"A": [1], "B": [1]}, index=[0])
        with pytest.raises(BABDataError):
            construct_portfolio(
                sig,
                dollar_neutral=False,
                enforce_risk_checks=True,
                net_exposure_limit=0.5,
            )


class TestEnforceBetaNeutralityGuards:
    def test_none_weights_returns_none(self):
        b = pd.DataFrame({"A": [0.5]}, index=[0])
        assert enforce_beta_neutrality(None, b) is None

    def test_none_betas_returns_weights(self):
        w = pd.DataFrame({"A": [1.0]}, index=[0])
        out = enforce_beta_neutrality(w, None)
        assert out is w or out.equals(w)

    def test_empty_weights_returns_input(self):
        w = pd.DataFrame({"A": []})
        b = pd.DataFrame({"A": [0.5]}, index=[])
        out = enforce_beta_neutrality(w, b)
        assert out is w or out.equals(w)

    def test_tolerance_skip_no_correction(self):
        # Dollar-neutral with equal betas -> port_beta == target == 0.0,
        # within tolerance -> skip at 314.
        w = pd.DataFrame({"A": [0.5], "B": [-0.5]}, index=[0])
        b = pd.DataFrame({"A": [1.0], "B": [1.0]}, index=[0])
        out = enforce_beta_neutrality(w, b, target_beta=0.0, tolerance=1e-4)
        assert out is w or out.equals(w)
