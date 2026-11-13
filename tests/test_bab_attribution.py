"""Attribution tests for `strategies/betting_against_beta/attribution.py`."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.attribution import (
    ATTRIBUTION_COLUMNS,
    attribution_totals,
    trade_attribution,
)
from strategies.betting_against_beta import attribution as attribution_mod


def _old_finite_series(values, index):
    """Reference: the pre-change per-series pandas sanitization."""
    return (
        pd.Series(values, index=index)
        .astype("float64")
        .replace([float("inf"), float("-inf")], float("nan"))
        .fillna(0.0)
    )


def _old_trade_attribution(backtest):
    """Reference: the pre-change trade_attribution implementation."""
    if backtest is None or not isinstance(backtest, pd.DataFrame) or backtest.empty:
        return pd.DataFrame(columns=ATTRIBUTION_COLUMNS)
    idx = backtest.index
    zero = pd.Series(0.0, index=idx)
    gross = backtest.get("gross_return", zero)
    cost = backtest.get("cost_drag", zero)
    slip = backtest.get("slippage_drag", zero)
    frame = pd.DataFrame(index=idx)
    frame["gross_return"] = _old_finite_series(gross, idx)
    frame["cost_drag"] = _old_finite_series(cost, idx)
    frame["slippage_drag"] = _old_finite_series(slip, idx)
    if "returns" in backtest.columns:
        frame["net_return"] = _old_finite_series(backtest["returns"], idx)
    else:
        frame["net_return"] = (
            frame["gross_return"] - frame["cost_drag"] - frame["slippage_drag"]
        )
    frame["net_return"] = _old_finite_series(frame["net_return"], idx)
    return frame[ATTRIBUTION_COLUMNS]


def _old_finite_sum(values):
    return float(
        pd.Series(values)
        .replace([float("inf"), float("-inf")], float("nan"))
        .fillna(0.0)
        .sum()
    )


def _old_attribution_totals(attribution_df):
    """Reference: the pre-change attribution_totals implementation."""
    if (
        attribution_df is None
        or not isinstance(attribution_df, pd.DataFrame)
        or attribution_df.empty
    ):
        return {
            "gross_return": 0.0,
            "cost_drag": 0.0,
            "slippage_drag": 0.0,
            "net_return": 0.0,
            "cost_share": 0.0,
            "slippage_share": 0.0,
        }
    df = attribution_df
    gross = _old_finite_sum(df["gross_return"]) if "gross_return" in df.columns else 0.0
    cost = _old_finite_sum(df["cost_drag"]) if "cost_drag" in df.columns else 0.0
    slip = _old_finite_sum(df["slippage_drag"]) if "slippage_drag" in df.columns else 0.0
    if "net_return" in df.columns:
        net = _old_finite_sum(df["net_return"])
    else:
        net = gross - cost - slip
    denom = abs(gross)
    if denom == 0 or not (denom == denom):
        cost_share = 0.0
        slip_share = 0.0
    else:
        cost_share = float(cost / denom)
        slip_share = float(slip / denom)
    return {
        "gross_return": float(gross),
        "cost_drag": float(cost),
        "slippage_drag": float(slip),
        "net_return": float(net),
        "cost_share": float(cost_share),
        "slippage_share": float(slip_share),
    }


def _frame(n=10):
    idx = pd.date_range("2023-01-01", periods=n)
    return pd.DataFrame(
        {
            "gross_return": [0.001 * i for i in range(n)],
            "cost_drag": [0.0001 * i for i in range(n)],
            "slippage_drag": [0.00005 * i for i in range(n)],
        },
        index=idx,
    )


def test_trade_attribution_basic():
    df = _frame()
    out = trade_attribution(df)
    assert list(out.columns) == ATTRIBUTION_COLUMNS
    assert len(out) == n if (n := len(df)) else True
    expected_net = (
        df["gross_return"] - df["cost_drag"] - df["slippage_drag"]
    )
    pd.testing.assert_series_equal(out["net_return"], expected_net, check_names=False)


def test_trade_attribution_uses_returns_column():
    df = _frame()
    df["returns"] = [0.005] * len(df)
    out = trade_attribution(df)
    assert (out["net_return"] == 0.005).all()


def test_trade_attribution_missing_cost_columns_treated_as_zero():
    idx = pd.date_range("2023-01-01", periods=5)
    df = pd.DataFrame({"gross_return": [0.01] * 5}, index=idx)
    out = trade_attribution(df)
    assert (out["cost_drag"] == 0.0).all()
    assert (out["slippage_drag"] == 0.0).all()
    assert (out["net_return"] == 0.01).all()


def test_trade_attribution_none_and_empty():
    assert trade_attribution(None).empty
    assert trade_attribution(pd.DataFrame()).empty
    out = trade_attribution(None)
    assert list(out.columns) == ATTRIBUTION_COLUMNS


def test_trade_attribution_non_dataframe():
    out = trade_attribution([1, 2, 3])
    assert out.empty


def test_trade_attribution_nan_filled():
    idx = pd.date_range("2023-01-01", periods=4)
    df = pd.DataFrame(
        {
            "gross_return": [0.01, np.nan, 0.03, 0.04],
            "cost_drag": [0.0, np.nan, 0.0, 0.0],
        },
        index=idx,
    )
    out = trade_attribution(df)
    assert out["net_return"].notna().all()
    assert (out.columns == ATTRIBUTION_COLUMNS).all()


def test_attribution_totals_basic():
    df = _frame()
    att = trade_attribution(df)
    totals = attribution_totals(att)
    assert set(totals) == {
        "gross_return",
        "cost_drag",
        "slippage_drag",
        "net_return",
        "cost_share",
        "slippage_share",
    }
    assert totals["gross_return"] == float(df["gross_return"].sum())
    assert totals["net_return"] == float(att["net_return"].sum())


def test_attribution_totals_zero_gross_guard():
    idx = pd.date_range("2023-01-01", periods=3)
    att = pd.DataFrame(
        {
            "gross_return": [0.0, 0.0, 0.0],
            "cost_drag": [0.1, 0.2, 0.3],
            "slippage_drag": [0.0, 0.0, 0.0],
            "net_return": [-0.1, -0.2, -0.3],
        },
        index=idx,
    )
    totals = attribution_totals(att)
    assert totals["cost_share"] == 0.0
    assert totals["slippage_share"] == 0.0


def test_attribution_totals_missing_columns():
    idx = pd.date_range("2023-01-01", periods=3)
    att = pd.DataFrame({"gross_return": [0.1, 0.2, 0.3]}, index=idx)
    totals = attribution_totals(att)
    assert totals["cost_drag"] == 0.0
    assert totals["slippage_drag"] == 0.0
    assert totals["net_return"] == pytest.approx(0.6)


def test_attribution_totals_none_and_empty():
    assert attribution_totals(None)["gross_return"] == 0.0
    assert attribution_totals(pd.DataFrame())["gross_return"] == 0.0
    assert attribution_totals(None)["net_return"] == 0.0


class TestAttributionSanitizationParity:
    """The single-pass numpy finite repair must be provably identical to the
    old per-series ``replace([inf,-inf],nan).fillna(0.0)`` sanitization
    (index/columns/dtypes/values exact at 1e-12) while dropping the pandas
    ``replace_list``/``fillna`` block-manager churn."""

    def test_trade_attribution_matches_old_on_nonfinite_frame(self):
        idx = pd.date_range("2024-01-01", periods=8, freq="D")
        raw = pd.DataFrame(
            {
                "gross_return": [np.inf, 0.1, -np.inf, np.nan, 0.2, np.inf, 0.0, -np.nan],
                "cost_drag": [0.0, np.inf, 0.0, np.nan, -np.inf, 0.3, 0.0, 0.0],
                "slippage_drag": [np.nan, 0.0, 0.0, np.inf, 0.0, -np.inf, np.nan, 0.0],
                "returns": [0.05, np.inf, -np.inf, np.nan, 0.1, 0.0, np.inf, 0.02],
            },
            index=idx,
        )
        expected = _old_trade_attribution(raw)
        got = attribution_mod.trade_attribution(raw)
        pd.testing.assert_frame_equal(
            got, expected, check_exact=False, rtol=1e-12, atol=1e-12
        )
        assert got.index.equals(expected.index)
        assert list(got.columns) == list(expected.columns)
        assert all(got[c].dtype == expected[c].dtype for c in got.columns)
        assert np.all(np.isfinite(got.to_numpy(dtype=float)))

    def test_trade_attribution_all_finite_is_identity(self):
        idx = pd.date_range("2024-01-01", periods=5, freq="D")
        raw = pd.DataFrame(
            {
                "gross_return": [0.01, 0.02, 0.03, 0.04, 0.05],
                "cost_drag": [0.001, 0.0, 0.002, 0.0, 0.0],
                "slippage_drag": [0.0, 0.0005, 0.0, 0.0, 0.0],
                "returns": [0.009, 0.019, 0.028, 0.04, 0.05],
            },
            index=idx,
        )
        expected = _old_trade_attribution(raw)
        got = attribution_mod.trade_attribution(raw)
        pd.testing.assert_frame_equal(
            got, expected, check_exact=False, rtol=1e-12, atol=1e-12
        )

    def test_trade_attribution_missing_cost_slip_returns_columns(self):
        idx = pd.date_range("2024-02-01", periods=6, freq="D")
        raw = pd.DataFrame({"gross_return": [0.01, np.inf, 0.02, np.nan, 0.03, 0.04]}, index=idx)
        expected = _old_trade_attribution(raw)
        got = attribution_mod.trade_attribution(raw)
        pd.testing.assert_frame_equal(
            got, expected, check_exact=False, rtol=1e-12, atol=1e-12
        )
        # net_return falls back to gross - cost - slip, all finite.
        assert np.all(np.isfinite(got["net_return"].to_numpy()))

    def test_trade_attribution_misaligned_short_series(self):
        idx = pd.date_range("2024-03-01", periods=6, freq="D")
        raw = pd.DataFrame(
            {
                "gross_return": [0.01, 0.02, 0.03, 0.04, 0.05, 0.06],
                "cost_drag": pd.Series([0.001, np.inf], index=idx[:2]),
                "slippage_drag": pd.Series([0.0005], index=idx[:1]),
            },
            index=idx,
        )
        expected = _old_trade_attribution(raw)
        got = attribution_mod.trade_attribution(raw)
        pd.testing.assert_frame_equal(
            got, expected, check_exact=False, rtol=1e-12, atol=1e-12
        )
        assert len(got) == 6

    def test_attribution_totals_matches_old_on_nonfinite(self):
        idx = pd.date_range("2024-04-01", periods=6, freq="D")
        att = pd.DataFrame(
            {
                "gross_return": [0.1, np.inf, 0.2, np.nan, 0.3, 0.4],
                "cost_drag": [0.01, 0.0, np.inf, 0.02, 0.0, 0.0],
                "slippage_drag": [0.001, 0.0, 0.0, np.inf, 0.002, 0.0],
                "net_return": [0.089, np.inf, 0.178, np.nan, 0.298, 0.4],
            },
            index=idx,
        )
        expected = _old_attribution_totals(att)
        got = attribution_mod.attribution_totals(att)
        assert set(got) == set(expected)
        for k in expected:
            assert got[k] == pytest.approx(expected[k], rel=1e-12, abs=1e-12)

    def test_attribution_totals_missing_columns_matches_old(self):
        att = pd.DataFrame({"gross_return": [0.1, np.inf, 0.2, np.nan]}, index=pd.date_range("2024-05-01", periods=4))
        expected = _old_attribution_totals(att)
        got = attribution_mod.attribution_totals(att)
        for k in expected:
            assert got[k] == pytest.approx(expected[k], rel=1e-12, abs=1e-12)
        # net falls back to gross - cost - slip (cost/slip default 0).
        assert got["net_return"] == pytest.approx(got["gross_return"])

    def test_attribution_identities_hold_at_1e12(self):
        idx = pd.date_range("2024-06-01", periods=10, freq="D")
        raw = pd.DataFrame(
            {
                "gross_return": np.linspace(-0.02, 0.02, 10),
                "cost_drag": np.linspace(0.0, 0.002, 10),
                "slippage_drag": np.linspace(0.0, 0.001, 10),
            },
            index=idx,
        )
        out = attribution_mod.trade_attribution(raw)
        pd.testing.assert_series_equal(
            out["net_return"],
            out["gross_return"] - out["cost_drag"] - out["slippage_drag"],
            check_names=False,
            check_exact=False,
            rtol=1e-12,
            atol=1e-12,
        )

    def test_attribution_defensive_fallback_wired(self, monkeypatch):
        # Force the primary numpy fast path to raise; the defensive ``except``
        # must still yield a finite, correctly-shaped frame.
        import numpy as _np

        real_isfinite = _np.isfinite

        def _boom(a, *args, **kwargs):
            raise RuntimeError("forced failure for parity test")

        monkeypatch.setattr(attribution_mod.np, "isfinite", _boom)
        idx = pd.date_range("2024-07-01", periods=4, freq="D")
        raw = pd.DataFrame(
            {
                "gross_return": [0.01, np.inf, np.nan, 0.02],
                "cost_drag": [0.001, 0.0, np.nan, 0.0],
                "slippage_drag": [0.0, 0.0, np.inf, 0.0],
            },
            index=idx,
        )
        out = attribution_mod.trade_attribution(raw)
        assert list(out.columns) == ATTRIBUTION_COLUMNS
        assert len(out) == 4
        # Every column must be finite despite the forced primary-path failure.
        assert np.all(real_isfinite(out.to_numpy(dtype=float)))
        totals = attribution_mod.attribution_totals(out)
        assert all(np.isfinite(float(v)) for v in totals.values())
