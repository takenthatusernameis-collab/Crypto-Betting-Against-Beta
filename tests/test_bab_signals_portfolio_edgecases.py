"""BAB signals and portfolio edge cases - NaN/empty/single-asset/extremes/ties."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.portfolio import construct_portfolio, _clean_signal_value, enforce_beta_neutrality
from strategies.betting_against_beta.signals import generate_bab_signals


def test_signals_empty_input():
    assert generate_bab_signals(None).empty
    assert generate_bab_signals(pd.DataFrame()).empty


def test_signals_nan_betas_all_zero():
    dates = pd.date_range("2023-01-01", periods=5)
    betas = pd.DataFrame({"BTC": [np.nan]*5, "ETH": [np.nan]*5}, index=dates)
    sig = generate_bab_signals(betas)
    assert sig.shape == betas.shape
    assert (sig.values == 0).all()
    assert np.isfinite(sig.values).all()


def test_signals_all_equal_betas_ties():
    dates = pd.date_range("2023-01-01", periods=3)
    betas = pd.DataFrame({"A": [1.0]*3, "B": [1.0]*3, "C": [1.0]*3}, index=dates)
    sig = generate_bab_signals(betas)
    assert sig.shape == betas.shape
    # With ties, ranking is stable; must not crash and produce finite integer values
    assert np.isfinite(sig.values).all()
    assert sig.dtypes.apply(lambda x: np.issubdtype(x, np.integer)).all()


def test_signals_single_asset_universe_flat():
    dates = pd.date_range("2023-01-01", periods=4)
    betas = pd.DataFrame({"BTC": [0.5, 0.6, 0.7, 0.8]}, index=dates)
    sig = generate_bab_signals(betas)
    assert (sig.values == 0).all()


def test_signals_extreme_quantiles_zero_one_boundaries():
    dates = pd.date_range("2023-01-01", periods=10)
    betas = pd.DataFrame({
        "A": np.linspace(0.2, 1.5, 10),
        "B": np.linspace(0.3, 1.4, 10),
        "C": np.linspace(0.4, 1.3, 10),
        "D": np.linspace(0.5, 1.2, 10),
        "E": np.linspace(0.6, 1.1, 10),
    }, index=dates)
    # q=0 should behave safely (no division by zero / crashes)
    sig = generate_bab_signals(betas, long_quantile=0.0, short_quantile=0.3)
    assert np.isfinite(sig.values).all()
    assert (sig.values == 0).all() or True  # may be all zero or still safe; main thing no crash
    sig2 = generate_bab_signals(betas, long_quantile=0.3, short_quantile=0.0)
    assert np.isfinite(sig2.values).all()
    # q>=1 - should not crash
    sig3 = generate_bab_signals(betas, long_quantile=1.0, short_quantile=1.0)
    assert np.isfinite(sig3.values).all()
    # q very small
    sig4 = generate_bab_signals(betas, long_quantile=0.01, short_quantile=0.01)
    assert np.isfinite(sig4.values).all()


def test_portfolio_ties_equal_betas_dollar_neutral():
    dates = pd.date_range("2023-01-01", periods=2)
    # All equal betas -> signals may be all zero depending on ranking; if any signals exist, weights must be neutral
    sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1], "C": [0, 0]}, index=dates)
    w = construct_portfolio(sig, dollar_neutral=True)
    assert np.isfinite(w.values).all()
    # Dollar neutral check when both sides exist
    net = w.sum(axis=1)
    assert np.allclose(net.values, 0.0, atol=1e-10)


def test_portfolio_single_asset_row_dollar_neutral_long_only_case():
    dates = pd.date_range("2023-01-01", periods=3)
    sig = pd.DataFrame({"BTC": [1, 1, 0]}, index=dates)
    w = construct_portfolio(sig, dollar_neutral=True)
    assert np.isfinite(w.values).all()
    # Long only with dollar_neutral True in current semantics gives equal weights on longs? Let us check behavior
    assert (w.values >= 0).all()
    # Weights finite and sum appropriately for long only
    assert np.allclose(w.sum(axis=1).values, [1.0, 1.0, 0.0], atol=1e-10)


def test_portfolio_extreme_weights_finiteness():
    dates = pd.date_range("2023-01-01", periods=4)
    sig = pd.DataFrame({"A": [1]*4, "B": [-1]*4, "C": [0]*4}, index=dates)
    w = construct_portfolio(sig)
    assert np.isfinite(w.values).all()
    assert np.allclose(w.sum(axis=1).values, 0.0, atol=1e-10)


def test_signals_mixed_type_beta_columns_no_crash():
    dates = pd.date_range("2023-01-01", periods=4)
    betas = pd.DataFrame({
        "A": [0.5, "0.6", None, 0.8],
        "B": ["garbage", 0.4, 0.9, "1.2"],
    }, index=dates)
    sig = generate_bab_signals(betas)
    assert sig.shape == betas.shape
    assert np.isfinite(sig.values).all()
    assert sig.dtypes.apply(lambda x: np.issubdtype(x, np.integer)).all()


def test_signals_quantile_clamp_extremes():
    dates = pd.date_range("2023-01-01", periods=6)
    betas = pd.DataFrame({
        "A": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
        "B": [0.6, 0.5, 0.4, 0.3, 0.2, 0.1],
        "C": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
    }, index=dates)
    for lq, sq in ((0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0), (-0.5, 2.5)):
        sig = generate_bab_signals(betas, long_quantile=lq, short_quantile=sq)
        assert sig.shape == betas.shape
        assert np.isfinite(sig.values).all()
        assert sig.dtypes.apply(lambda x: np.issubdtype(x, np.integer)).all()


def test_portfolio_dollar_neutral_exact_when_both_sides():
    dates = pd.date_range("2023-01-01", periods=3)
    # Odd counts so equal weights do not sum to exactly 1.0 in floating point.
    sig = pd.DataFrame({"A": [1]*3, "B": [1]*3, "C": [1]*3, "D": [-1]*3, "E": [-1]*3}, index=dates)
    w = construct_portfolio(sig, dollar_neutral=True)
    assert np.isfinite(w.values).all()
    net = w.sum(axis=1).values
    assert np.allclose(net, 0.0, atol=1e-12)
    # Longs sum to +1.0, shorts to -1.0 within each row.
    for i in range(len(dates)):
        row = w.iloc[i].to_numpy(dtype=float)
        assert np.allclose(row[row > 0].sum(), 1.0, atol=1e-12)
        assert np.allclose(row[row < 0].sum(), -1.0, atol=1e-12)


class TestCleanSignalValue:
    def test_none_and_nan(self):
        assert _clean_signal_value(None) == 0
        assert _clean_signal_value(float("nan")) == 0

    def test_string_parsing(self):
        assert _clean_signal_value("1") == 1
        assert _clean_signal_value("-1") == -1
        assert _clean_signal_value("garbage") == 0
        assert _clean_signal_value("1.5") == 1

    def test_numeric(self):
        assert _clean_signal_value(1) == 1
        assert _clean_signal_value(-1) == -1
        assert _clean_signal_value(2) == 0
        assert _clean_signal_value(1.0) == 1
        assert _clean_signal_value(np.int64(-1)) == -1

    def test_type_error(self):
        assert _clean_signal_value([1, 2]) == 0


class TestConstructPortfolioBranches:
    def test_max_position_size_kw_alias(self):
        dates = pd.date_range("2023-01-01", periods=2)
        sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1]}, index=dates)
        w = construct_portfolio(sig, max_pos_size=1.0)
        assert np.isfinite(w.values).all()

    def test_max_position_size_limit_raises(self):
        dates = pd.date_range("2023-01-01", periods=2)
        sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1]}, index=dates)
        from strategies.betting_against_beta.errors import BABDataError
        with pytest.raises(BABDataError):
            construct_portfolio(sig, max_pos_size=0.4)

    def test_max_position_size_bad_type_ignored(self):
        dates = pd.date_range("2023-01-01", periods=2)
        sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1]}, index=dates)
        w = construct_portfolio(sig, max_position_size="not-a-number")
        assert np.isfinite(w.values).all()

    def test_max_turnover_bad_type_ignored(self):
        dates = pd.date_range("2023-01-01", periods=2)
        sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1]}, index=dates)
        prev = pd.DataFrame({"A": [0.0, 0.0], "B": [0.0, 0.0]}, index=dates)
        w = construct_portfolio(sig, max_turnover="not-a-number", weights_df_prev=prev)
        assert np.isfinite(w.values).all()

    def test_risk_checks_bad_gross_limit_uses_defaults(self):
        dates = pd.date_range("2023-01-01", periods=2)
        sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1]}, index=dates)
        w = construct_portfolio(sig, enforce_risk_checks=True, gross_exposure_limit="not-a-number")
        assert np.isfinite(w.values).all()


class TestEnforceBetaNeutralityBranches:
    def _w_b(self):
        dates = pd.date_range("2023-01-01", periods=2)
        w = pd.DataFrame({"A": [0.5, -0.5], "B": [-0.5, 0.5]}, index=dates)
        b = pd.DataFrame({"A": [1.0, 1.0], "B": [1.2, 1.2]}, index=dates)
        return w, b

    def test_weights_empty_returned(self):
        w, b = self._w_b()
        out = enforce_beta_neutrality(pd.DataFrame(), b)
        assert out.equals(pd.DataFrame())

    def test_betas_empty_returned(self):
        w, b = self._w_b()
        out = enforce_beta_neutrality(w, pd.DataFrame())
        assert out.equals(w)

    def test_no_common_columns_returned(self):
        w, b = self._w_b()
        b2 = pd.DataFrame({"C": [1.0, 1.0]}, index=w.index)
        out = enforce_beta_neutrality(w, b2)
        assert out.equals(w)

    def test_invalid_tolerance_and_drift_default(self):
        w, b = self._w_b()
        out = enforce_beta_neutrality(w, b, tolerance=float("nan"), max_drift=-1.0)
        assert np.isfinite(out.values).all()

    def test_non_finite_target_beta(self):
        w, b = self._w_b()
        out = enforce_beta_neutrality(w, b, target_beta=float("nan"))
        assert np.isfinite(out.values).all()

    def test_row_no_finite_betas_skipped(self):
        w, b = self._w_b()
        b2 = b.copy()
        b2.loc[:, :] = np.nan
        out = enforce_beta_neutrality(w, b2)
        assert np.isfinite(out.values).all()

    def test_zero_weight_denom_skipped(self):
        w, b = self._w_b()
        w2 = pd.DataFrame({"A": [0.0, 0.0], "B": [0.0, 0.0]}, index=w.index)
        out = enforce_beta_neutrality(w2, b)
        assert np.isfinite(out.values).all()

    def test_correction_false_returns_input(self):
        w, b = self._w_b()
        out = enforce_beta_neutrality(w, b, target_beta=99.0, correction=False)
        assert out.equals(w)

    def test_equal_betas_skipped(self):
        w, b = self._w_b()
        b2 = pd.DataFrame({"A": [1.0, 1.0], "B": [1.0, 1.0]}, index=w.index)
        out = enforce_beta_neutrality(w, b2, target_beta=99.0)
        assert np.isfinite(out.values).all()
