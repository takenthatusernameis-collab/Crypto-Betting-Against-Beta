"""Coverage campaign 3 for strategies/betting_against_beta/portfolio.py.

Targets residual uncovered paths: _clean_signal_value fallbacks, kwargs
alias routing, non-numeric dtype/coercion defensive branches, dollar-
neutral renormalization (152-157), outer exception fallback (159-160),
max_position_size/max_turnover validation, and risk-check raise paths.
Production-realistic controlled inputs; scoped monkeypatches only for
defensive branches unreachable via public API.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.portfolio import (
    _clean_signal_value,
    check_portfolio_risk,
    construct_portfolio,
    enforce_beta_neutrality,
)


class TestCleanSignalValueResiduals:
    def test_none_returns_zero(self):
        assert _clean_signal_value(None) == 0

    def test_nan_float_returns_zero(self):
        assert _clean_signal_value(float("nan")) == 0

    def test_string_numeric_one(self):
        assert _clean_signal_value("1") == 1
        assert _clean_signal_value("1.0") == 1

    def test_string_numeric_minus_one(self):
        assert _clean_signal_value("-1") == -1
        assert _clean_signal_value("-1.0") == -1

    def test_string_other_number_returns_zero(self):
        assert _clean_signal_value("2") == 0
        assert _clean_signal_value("0.5") == 0

    def test_string_garbage_returns_zero(self):
        assert _clean_signal_value("abc") == 0
        assert _clean_signal_value("") == 0

    def test_valid_int_float_np(self):
        assert _clean_signal_value(1) == 1
        assert _clean_signal_value(-1) == -1
        assert _clean_signal_value(1.0) == 1
        assert _clean_signal_value(-1.0) == -1
        assert _clean_signal_value(np.int64(1)) == 1
        assert _clean_signal_value(np.float64(-1.0)) == -1

    def test_non_unit_values_return_zero(self):
        assert _clean_signal_value(0) == 0
        assert _clean_signal_value(2) == 0
        assert _clean_signal_value(0.5) == 0

    def test_nonfinite_numeric_returns_zero(self):
        assert _clean_signal_value(np.inf) == 0
        assert _clean_signal_value(-np.inf) == 0

    def test_unhashable_weird_type_returns_zero(self):
        # Trigger outer except (TypeError/ValueError) via pathological __float__?
        class Bad:
            def __float__(self):
                raise TypeError("no")

        # Not a str/int/float/numpy numeric instance check path -> returns 0
        assert _clean_signal_value(Bad()) == 0


class TestConstructPortfolioBasicContracts:
    def test_none_and_empty(self):
        assert construct_portfolio(None).empty
        assert construct_portfolio(pd.DataFrame()).empty

    def test_dollar_neutral_balances(self):
        sig = pd.DataFrame({"A": [1, 1], "B": [-1, -1], "C": [1, 0]})
        w = construct_portfolio(sig, dollar_neutral=True)
        assert w.shape == sig.shape
        net = w.sum(axis=1)
        assert np.allclose(net.to_numpy(), 0.0, atol=1e-12)
        assert np.isfinite(w.to_numpy()).all()

    def test_check_portfolio_risk_alias(self):
        sig = pd.DataFrame({"A": [1], "B": [-1]})
        assert check_portfolio_risk is construct_portfolio
        w = check_portfolio_risk(sig)
        assert np.isfinite(w.to_numpy()).all()


class TestKwargsAliasRouting:
    def test_max_total_turnover_alias(self):
        sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1]})
        prev = pd.DataFrame({"A": [0.5, 0.5], "B": [-0.5, -0.5]}, index=sig.index)
        # very tight turnover limit via alias -> raises
        with pytest.raises(BABDataError, match="Turnover exceeds"):
            construct_portfolio(sig, weights_df_prev=prev, max_total_turnover=0.0001)

    def test_max_pos_size_alias(self):
        sig = pd.DataFrame({"A": [1], "B": [-1]})
        # position size alias routes to max_position_size enforcement
        with pytest.raises(BABDataError, match="max_position_size"):
            construct_portfolio(sig, max_pos_size=0.1)

    def test_position_limit_alias(self):
        sig = pd.DataFrame({"A": [1], "B": [-1]})
        with pytest.raises(BABDataError, match="max_position_size"):
            construct_portfolio(sig, position_limit=0.1)


class TestRiskAndConstraintValidation:
    def test_max_position_size_must_be_positive(self):
        sig = pd.DataFrame({"A": [1], "B": [-1]})
        with pytest.raises(BABDataError, match="max_position_size must be positive"):
            construct_portfolio(sig, max_position_size=0)
        with pytest.raises(BABDataError, match="max_position_size must be positive"):
            construct_portfolio(sig, max_position_size=-1)

    def test_max_turnover_must_be_positive(self):
        sig = pd.DataFrame({"A": [1], "B": [-1]})
        prev = pd.DataFrame({"A": [0.0], "B": [0.0]})
        with pytest.raises(BABDataError, match="max_turnover must be positive"):
            construct_portfolio(sig, weights_df_prev=prev, max_turnover=0)

    def test_turnover_within_limit_ok(self):
        sig = pd.DataFrame({"A": [1, 1], "B": [-1, -1]})
        prev = pd.DataFrame({"A": [0.5, 0.5], "B": [-0.5, -0.5]})
        w = construct_portfolio(sig, weights_df_prev=prev, max_turnover=10.0)
        assert np.isfinite(w.to_numpy()).all()

    def test_enforce_risk_checks_net_exposure(self):
        sig = pd.DataFrame({"A": [1, 1], "B": [1, 1], "C": [0, 0]})
        # long-only with dollar_neutral False -> net > 0
        with pytest.raises(BABDataError, match="Net exposure"):
            construct_portfolio(
                sig, dollar_neutral=False, enforce_risk_checks=True, net_exposure_limit=0.0
            )

    def test_single_asset_weight_exceeds_limit(self):
        sig = pd.DataFrame({"A": [1], "B": [0]})
        # A gets weight 1.0 as only long; short side absent with dollar_neutral False
        with pytest.raises(BABDataError, match="Single asset weight"):
            construct_portfolio(sig, dollar_neutral=False, max_single_weight=0.5)

    def test_gross_exposure_exceeds_limit(self):
        sig = pd.DataFrame({"A": [1], "B": [-1]})
        with pytest.raises(BABDataError, match="Gross exposure"):
            construct_portfolio(sig, gross_exposure_limit=0.5)


class TestNonNumericAndDefensiveBranches:
    def test_object_dtype_signals_coerced(self):
        sig = pd.DataFrame({"A": [1, "1", 1], "B": [-1, "-1", -1]}, dtype=object)
        w = construct_portfolio(sig)
        assert w.shape == sig.shape
        assert np.isfinite(w.to_numpy()).all()

    def test_mixed_garbage_signals_become_zero(self):
        sig = pd.DataFrame({"A": ["x", None, np.nan], "B": [1, -1, 1]})
        w = construct_portfolio(sig)
        assert np.isfinite(w.to_numpy()).all()

    def test_outer_exception_surfaces_error(self, monkeypatch):
        sig = pd.DataFrame({"A": [1, 1], "B": [-1, -1]})
        # Break np.where to force outer exception path (179).  The outer
        # handler now re-raises as BABPortfolioError rather than silently
        # returning a zero frame (which would report "no positions").
        import pytest

        from strategies.betting_against_beta.portfolio import BABPortfolioError

        real_where = np.where

        def boom(*a, **k):
            raise RuntimeError("boom")

        monkeypatch.setattr(np, "where", boom)
        with pytest.raises(BABPortfolioError):
            construct_portfolio(sig)


class TestDollarNeutralRenormalization:
    def test_both_sides_renormalized(self):
        # Multiple longs/shorts with uneven counts exercise renorm loops
        sig = pd.DataFrame({"A": [1], "B": [1], "C": [1], "D": [-1], "E": [-1]})
        w = construct_portfolio(sig, dollar_neutral=True)
        long_sum = w[w > 0].sum(axis=1).iloc[0]
        short_sum = w[w < 0].sum(axis=1).iloc[0]
        assert abs(long_sum - 1.0) < 1e-12
        assert abs(short_sum + 1.0) < 1e-12
        assert abs(w.sum(axis=1).iloc[0]) < 1e-12

    def test_net_correction_path(self):
        # Normal case should still be net-neutral; exercises 151-157 code path
        sig = pd.DataFrame({"A": [1, 1, -1], "B": [-1, 1, -1], "C": [1, -1, 1], "D": [-1, -1, 1]})
        w = construct_portfolio(sig, dollar_neutral=True)
        assert np.allclose(w.sum(axis=1).to_numpy(), 0.0, atol=1e-10)


class TestEnforceBetaNeutralityResiduals:
    def test_none_and_empty_inputs(self):
        assert enforce_beta_neutrality(None, None) is None
        w = pd.DataFrame({"A": [0.5], "B": [-0.5]})
        assert enforce_beta_neutrality(w, None).equals(w)
        assert enforce_beta_neutrality(w, pd.DataFrame()).equals(w)
        assert enforce_beta_neutrality(pd.DataFrame(), pd.DataFrame({"A": [1.0]})).empty

    def test_no_common_columns_or_index(self):
        w = pd.DataFrame({"A": [0.5], "B": [-0.5]}, index=[0])
        b = pd.DataFrame({"X": [1.0]}, index=[0])
        assert enforce_beta_neutrality(w, b).equals(w)
        b2 = pd.DataFrame({"A": [1.0]}, index=[99])
        assert enforce_beta_neutrality(w, b2).equals(w)

    def test_no_finite_beta_returns_unchanged(self):
        w = pd.DataFrame({"A": [0.5, 0.5], "B": [-0.5, -0.5]})
        b = pd.DataFrame({"A": [np.nan, np.nan], "B": [np.inf, -np.inf]})
        out = enforce_beta_neutrality(w, b)
        pd.testing.assert_frame_equal(out, w)

    def test_correction_false_no_adjustment(self):
        w = pd.DataFrame({"A": [0.6], "B": [-0.4]})
        b = pd.DataFrame({"A": [2.0], "B": [0.1]})
        out = enforce_beta_neutrality(w, b, correction=False)
        pd.testing.assert_frame_equal(out, w)

    def test_already_neutral_no_change(self):
        # symmetric weights with equal betas -> beta near target
        w = pd.DataFrame({"A": [0.5], "B": [-0.5]})
        b = pd.DataFrame({"A": [1.0], "B": [1.0]})
        out = enforce_beta_neutrality(w, b, target_beta=0.0, tolerance=1.0)
        pd.testing.assert_frame_equal(out, w)

    def test_correction_reduces_beta_drift(self):
        w = pd.DataFrame({"A": [0.7], "B": [-0.3]})
        b = pd.DataFrame({"A": [1.5], "B": [0.5]})
        out = enforce_beta_neutrality(w, b, target_beta=0.0, tolerance=1e-9)
        assert np.isfinite(out.to_numpy()).all()
        # output shape preserved
        assert out.shape == w.shape

    def test_degenerate_centered_variance_skips(self):
        # identical betas -> s2_centered ~ 0 -> continue (330-331)
        w = pd.DataFrame({"A": [0.7], "B": [-0.3]})
        b = pd.DataFrame({"A": [1.0], "B": [1.0]})
        out = enforce_beta_neutrality(w, b, target_beta=0.5, tolerance=1e-9)
        assert np.isfinite(out.to_numpy()).all()

    def test_invalid_tolerance_target_handled(self):
        w = pd.DataFrame({"A": [0.5], "B": [-0.5]})
        b = pd.DataFrame({"A": [1.2], "B": [0.8]})
        out = enforce_beta_neutrality(w, b, tolerance=-1, max_drift=np.nan, target_beta=np.inf)
        assert np.isfinite(out.to_numpy()).all()
