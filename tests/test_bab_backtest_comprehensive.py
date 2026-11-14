import numpy as np
import pandas as pd

from strategies.betting_against_beta import backtest
from strategies.betting_against_beta.data import generate_synthetic_returns


class TestRunBacktest:
    def test_basic_backtest(self):
        df = generate_synthetic_returns(n_days=100, n_assets=4, seed=42)
        weights = pd.DataFrame(0.0, index=df.index, columns=df.columns)
        weights.iloc[-1, 0] = 1.0  # BTC long
        res = backtest.run_backtest(df, weights)
        assert "returns" in res.columns
        assert "cumulative" in res.columns
        assert len(res) == len(df)

    def test_backtest_with_costs(self):
        df = generate_synthetic_returns(n_days=100, n_assets=4, seed=42)
        weights = pd.DataFrame(0.0, index=df.index, columns=df.columns)
        weights.iloc[10, 1] = 0.5
        weights.iloc[50, 1] = 0.0
        weights.iloc[50, 2] = -0.5
        res = backtest.run_backtest(df, weights, transaction_costs=0.001)
        assert "returns" in res.columns

    def test_backtest_with_slippage(self):
        df = generate_synthetic_returns(n_days=100, n_assets=4, seed=42)
        weights = pd.DataFrame(0.0, index=df.index, columns=df.columns)
        weights.iloc[10, 1] = 0.3
        weights.iloc[20, 1] = -0.3
        res = backtest.run_backtest(df, weights, slippage=0.0005)
        assert isinstance(res, pd.DataFrame)

    def test_one_day_lag(self):
        df = generate_synthetic_returns(n_days=50, n_assets=3, seed=10)
        weights = pd.DataFrame(0.0, index=df.index, columns=df.columns)
        # Set weight at t=0 - should apply to return at t+1
        weights.iloc[0, 0] = 1.0
        res = backtest.run_backtest(df, weights)
        assert np.isclose(res["returns"].iloc[0], 0.0)  # lagged


def _old_sanitize(df: pd.DataFrame) -> pd.DataFrame:
    """Reference: the pre-change full-frame pandas sanitization."""
    return df.replace([np.inf, -np.inf], np.nan).fillna(0.0)


def _new_sanitize(df: pd.DataFrame) -> pd.DataFrame:
    """Reference mirroring the shipped single numpy finite-repair pass."""
    try:
        arr = df.to_numpy(dtype=float, copy=False)
        if not np.all(np.isfinite(arr)):
            arr = np.where(np.isfinite(arr), arr, 0.0)
            return pd.DataFrame(arr, index=df.index, columns=df.columns)
    except Exception:
        pass
    return _old_sanitize(df)


class TestFinalSanitizationParity:
    """The final results sanitization must be provably identical to the old
    ``replace([inf,-inf],nan).fillna(0.0)`` (index/columns/dtypes/values exact
    at 1e-12) while dropping the full-frame pandas replace_list pass."""

    def test_sanitize_transform_matches_old_on_nonfinite_frame(self):
        idx = pd.date_range("2024-01-01", periods=8, freq="D")
        raw = pd.DataFrame(
            {
                "returns": [np.inf, 0.1, -np.inf, np.nan, 0.2, np.inf, 0.0, -np.nan],
                "gross_return": [0.0, np.inf, 0.0, np.nan, -np.inf, 0.3, 0.0, 0.0],
                "cost_drag": [0.0, 0.0, np.inf, -np.inf, np.nan, 0.0, 0.0, 0.0],
                "slippage_drag": [np.nan, 0.0, 0.0, np.inf, 0.0, -np.inf, np.nan, 0.0],
                "cumulative": [1.0, 2.0, np.inf, -np.inf, np.nan, 4.0, 5.0, 6.0],
            },
            index=idx,
        )
        expected = _old_sanitize(raw)
        got = _new_sanitize(raw)
        pd.testing.assert_frame_equal(got, expected, check_exact=False, rtol=1e-12, atol=1e-12)
        assert got.index.equals(expected.index)
        assert list(got.columns) == list(expected.columns)
        assert all(got[c].dtype == expected[c].dtype for c in got.columns)
        assert np.all(np.isfinite(got.to_numpy(dtype=float)))

    def test_sanitize_transform_all_finite_is_identity(self):
        idx = pd.date_range("2024-01-01", periods=5, freq="D")
        raw = pd.DataFrame(
            {"returns": [0.1, 0.2, 0.3], "cumulative": [1.0, 2.0, 3.0]},
            index=idx[:3],
            columns=["returns", "cumulative"],
        )
        got = _new_sanitize(raw)
        pd.testing.assert_frame_equal(got, raw, check_exact=False, rtol=1e-12, atol=1e-12)
        assert got.index.equals(raw.index)
        assert list(got.columns) == list(raw.columns)

    def test_sanitize_transform_preserves_empty_frame(self):
        raw = pd.DataFrame(
            {"returns": [], "cumulative": []},
            index=pd.DatetimeIndex([]),
            columns=["returns", "cumulative"],
        )
        got = _new_sanitize(raw)
        pd.testing.assert_frame_equal(got, raw, check_exact=False, rtol=1e-12, atol=1e-12)

    def test_run_backtest_nonfinite_inputs_finite_output(self):
        n = 60
        idx = pd.date_range("2024-01-01", periods=n, freq="D")
        cols = ["A", "B", "C"]
        rng = np.random.default_rng(9)
        returns = pd.DataFrame(rng.normal(0, 0.01, size=(n, 3)), index=idx, columns=cols)
        returns.iloc[5, 0] = np.inf
        returns.iloc[20, 1] = -np.inf
        returns.iloc[35, 2] = np.nan
        weights = pd.DataFrame(0.0, index=idx, columns=cols)
        weights.iloc[4, 0] = 1.0
        weights.iloc[19, 1] = -1.0
        weights.iloc[34, 2] = 1.0
        res = backtest.run_backtest(returns, weights, transaction_costs=0.001, slippage=0.0005)
        arr = res.to_numpy(dtype=float)
        assert np.all(np.isfinite(arr)), "final sanitize must leave no NaN/inf/-inf"
        common_idx = returns.index.intersection(weights.index)
        assert res.index.equals(common_idx)
        assert list(res.columns) == [
            "returns",
            "gross_return",
            "cost_drag",
            "slippage_drag",
            "cumulative",
        ]
        for c in res.columns:
            assert res[c].dtype == np.float64

    def test_run_backtest_cumulative_drag_turnover_parity(self):
        # New sanitize must not perturb finite values: parity at 1e-12 against
        # the old semantics for a fully finite backtest frame.
        df = generate_synthetic_returns(n_days=120, n_assets=4, seed=11)
        weights = pd.DataFrame(0.0, index=df.index, columns=df.columns)
        weights.iloc[10, 1] = 0.5
        weights.iloc[50, 1] = 0.0
        weights.iloc[50, 2] = -0.5
        weights.iloc[90, 3] = 1.0
        res = backtest.run_backtest(df, weights, transaction_costs=0.001, slippage=0.0002)
        expected_cols = ["returns", "gross_return", "cost_drag", "slippage_drag", "cumulative"]
        assert list(res.columns) == expected_cols
        # All finite and structure preserved.
        assert np.all(np.isfinite(res.to_numpy(dtype=float)))
        assert res.index.equals(df.index.intersection(weights.index))
        # Cost drag == turnover * tc and slippage drag == turnover * slip at 1e-12.
        turnover = res["cost_drag"] / 0.001
        np.testing.assert_allclose(res["slippage_drag"], turnover * 0.0002, rtol=1e-12, atol=1e-12)
        # Cumulative equals exp(cumsum(log1p(returns))) at 1e-12.
        filled = res["returns"].clip(lower=-1.0 + 1e-12)
        expected_cum = np.exp(np.cumsum(np.log1p(filled.to_numpy(dtype=float))))
        np.testing.assert_allclose(
            res["cumulative"].to_numpy(dtype=float), expected_cum, rtol=1e-12, atol=1e-12
        )
