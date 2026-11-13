"""Production-relevant coverage for backtest.py residual branches.

Targets miss clusters documented in HANDOFF (09:19Z evidence):
  - 15,17: tc/slippage_cost alias handling when primary args are 0
  - 103-108: cost_model application path (TransactionCostModel + compute)
  - 116-117,122-125: finiteness hardening exception/repair branches
  - 130,133-149: cumulative fallback/sanitization paths

Uses real DataFrames and minimal, scoped monkeypatching only to force
defensive branches that cannot be reached with valid public inputs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import backtest as backtest_mod
from strategies.betting_against_beta.costs import TransactionCostModel, compute_transaction_costs


def _returns_weights(periods: int = 20, seed: int = 0):
    idx = pd.date_range("2024-01-01", periods=periods, freq="D")
    rng = np.random.default_rng(seed)
    returns = pd.DataFrame(
        {
            "BTC": rng.normal(0.0004, 0.02, periods),
            "ETH": rng.normal(0.0006, 0.03, periods),
        },
        index=idx,
    )
    weights = pd.DataFrame(
        {
            "BTC": [0.5, -0.5] * (periods // 2) + ([0.5] if periods % 2 else []),
            "ETH": [-0.5, 0.5] * (periods // 2) + ([-0.5] if periods % 2 else []),
        },
        index=idx,
    )
    return returns, weights


def test_tc_and_slippage_cost_aliases_apply_when_primary_zero():
    returns, weights = _returns_weights(periods=12, seed=1)
    base = backtest_mod.run_backtest(returns, weights)
    aliased = backtest_mod.run_backtest(
        returns, weights, transaction_costs=0.0, slippage=0.0, tc=0.001, slippage_cost=0.0005
    )
    assert list(aliased.columns) == ["returns", "gross_return", "cost_drag", "slippage_drag", "cumulative"]
    assert np.all(np.isfinite(aliased["cumulative"].to_numpy(dtype=float)))
    assert np.all(aliased["cost_drag"].to_numpy(dtype=float) >= 0)
    assert np.all(aliased["slippage_drag"].to_numpy(dtype=float) >= 0)
    assert aliased["cost_drag"].sum() > 0
    assert aliased["slippage_drag"].sum() > 0
    # Aliases should reduce net returns relative to gross in periods with turnover.
    assert aliased["returns"].iloc[1:].sum() <= base["returns"].iloc[1:].sum() + 1e-12


def test_primary_cost_args_take_precedence_over_zero_alias_semantics():
    returns, weights = _returns_weights(periods=10, seed=2)
    # tc/slippage_cost only used when corresponding primary arg == 0.0.
    res = backtest_mod.run_backtest(
        returns, weights, transaction_costs=0.002, slippage=0.001, tc=0.5, slippage_cost=0.5
    )
    # Production computes weight change as weights - shifted(fillna(0)), which counts
    # the initial position establishment (0 -> initial weights) as period-0 turnover.
    w_shifted_filled = weights.shift(1).fillna(0.0)
    expected_cost = (weights.to_numpy(dtype=float) - w_shifted_filled.to_numpy(dtype=float))
    expected_cost = np.abs(expected_cost).sum(axis=1) * 0.002
    expected_slip = np.abs(weights.to_numpy(dtype=float) - w_shifted_filled.to_numpy(dtype=float)).sum(axis=1) * 0.001
    assert np.allclose(res["cost_drag"].to_numpy(dtype=float), expected_cost, atol=1e-12)
    assert np.allclose(res["slippage_drag"].to_numpy(dtype=float), expected_slip, atol=1e-12)
    # Primary args must win: 0.5 alias values are ignored.
    assert res["cost_drag"].to_numpy(dtype=float)[0] == pytest.approx(0.002)


def test_cost_model_path_applies_modeled_costs_and_preserves_shape():
    returns, weights = _returns_weights(periods=15, seed=3)
    prices = pd.DataFrame(
        {
            "BTC": np.linspace(30000, 33000, 15),
            "ETH": np.linspace(2000, 2200, 15),
        },
        index=returns.index,
    )
    adv = {"BTC": 5_000_000_000.0, "ETH": 2_000_000_000.0}
    model = TransactionCostModel(linear_fee=0.001, bid_ask_bps=0.0005, impact_coefficient=0.0002)
    res = backtest_mod.run_backtest(
        returns, weights, cost_model=model, prices_df=prices, adv_usd=adv
    )
    assert isinstance(res, pd.DataFrame)
    assert len(res) == len(returns)
    assert np.all(np.isfinite(res[["returns", "gross_return", "cumulative"]].to_numpy(dtype=float)))
    # Modeled costs should not create impossible gains above gross in nontrivial turnover periods.
    assert (res["returns"].iloc[1:] <= res["gross_return"].iloc[1:] + 1e-12).all()


def test_cost_model_rejects_non_transaction_cost_model():
    returns, weights = _returns_weights(periods=8, seed=4)
    with pytest.raises(TypeError, match="TransactionCostModel"):
        backtest_mod.run_backtest(returns, weights, cost_model=object())


def test_finiteness_hardening_repairs_nonfinite_log_and_cumulative_paths(monkeypatch):
    returns, weights = _returns_weights(periods=12, seed=5)
    real_log1p = np.log1p
    real_exp = np.exp
    state = {"log": 0, "exp": 0}

    def log1p_with_nonfinite(x):
        state["log"] += 1
        out = np.asarray(real_log1p(x), dtype=float)
        if state["log"] == 1:
            out = out.copy()
            out[2] = np.nan
            out[4] = np.inf
        return out

    def exp_with_nonfinite(x):
        state["exp"] += 1
        out = np.asarray(real_exp(x), dtype=float)
        if state["exp"] == 1:
            out = out.copy()
            out[3] = -np.inf
            out[5] = np.nan
        return out

    monkeypatch.setattr(backtest_mod.np, "log1p", log1p_with_nonfinite)
    monkeypatch.setattr(backtest_mod.np, "exp", exp_with_nonfinite)
    res = backtest_mod.run_backtest(returns, weights)
    assert state["log"] >= 1 and state["exp"] >= 1
    assert np.all(np.isfinite(res["cumulative"].to_numpy(dtype=float)))
    assert np.all(np.isfinite(res["returns"].to_numpy(dtype=float)))
    assert list(res.columns) == ["returns", "gross_return", "cost_drag", "slippage_drag", "cumulative"]


def test_cumulative_fallback_sanitizes_nonfinite_cumprod(monkeypatch):
    returns, weights = _returns_weights(periods=10, seed=6)

    def raising_log1p(_x):
        raise RuntimeError("force cumulative fallback")

    class BadCumprodSeries(pd.Series):
        @property
        def _constructor(self):
            return BadCumprodSeries

        def cumprod(self, axis=None, skipna=True, *args, **kwargs):
            base = super().cumprod(axis=axis, skipna=skipna, *args, **kwargs)
            arr = np.asarray(base.to_numpy(dtype=float), dtype=float).copy()
            if arr.size > 2:
                arr[1] = np.inf
                arr[2] = np.nan
            return BadCumprodSeries(arr, index=self.index)

    real_series = backtest_mod.pd.Series

    def series_factory(data=None, index=None, *args, **kwargs):
        obj = real_series(data=data, index=index, *args, **kwargs)
        # Only wrap the specific portfolio_returns_filled path (length matches index, float-ish data).
        if index is not None and len(obj) == len(returns.index) and not isinstance(data, BadCumprodSeries):
            try:
                vals = np.asarray(obj.to_numpy(dtype=float), dtype=float)
                if vals.ndim == 1 and np.all(np.isfinite(vals) | True):
                    return BadCumprodSeries(vals, index=index)
            except Exception:
                pass
        return obj

    monkeypatch.setattr(backtest_mod.np, "log1p", raising_log1p)
    monkeypatch.setattr(backtest_mod.pd, "Series", series_factory)
    res = backtest_mod.run_backtest(returns, weights)
    cum = res["cumulative"].to_numpy(dtype=float)
    assert np.all(np.isfinite(cum))
    assert cum[0] > 0


def test_final_sanitization_defensive_replace_fallback_wired(monkeypatch):
    returns, weights = _returns_weights(periods=8, seed=7)
    real_replace = pd.DataFrame.replace
    real_to_numpy = pd.DataFrame.to_numpy
    triggered = {"n": 0}

    def raising_replace(self, *args, **kwargs):
        # Only the final results frame (5-column portfolio result) should trip the
        # defensive except branch; all other replace calls pass through untouched.
        if set(["returns", "gross_return", "cost_drag", "slippage_drag", "cumulative"]).issubset(
            getattr(self, "columns", [])
        ):
            triggered["n"] += 1
            raise RuntimeError("force final-sanitization except branch")
        return real_replace(self, *args, **kwargs)

    def raising_to_numpy(self, *args, **kwargs):
        # Force the primary numpy repair path to fail so the defensive
        # ``results.replace(...)`` fallback is reached.
        if len(getattr(self, "columns", [])) == 5:
            raise RuntimeError("force primary path except")
        return real_to_numpy(self, *args, **kwargs)

    monkeypatch.setattr(pd.DataFrame, "replace", raising_replace)
    monkeypatch.setattr(pd.DataFrame, "to_numpy", raising_to_numpy)
    res = backtest_mod.run_backtest(returns, weights)
    # The defensive replace fallback must have been exercised.
    assert triggered["n"] >= 1
    assert isinstance(res, pd.DataFrame)
    assert list(res.columns) == ["returns", "gross_return", "cost_drag", "slippage_drag", "cumulative"]
    assert len(res) == len(returns.index)


def test_hardening_exception_branches_are_defensive(monkeypatch):
    returns, weights = _returns_weights(periods=6, seed=8)

    class ExplodingSeries(pd.Series):
        @property
        def _constructor(self):
            return ExplodingSeries

        def replace(self, *args, **kwargs):
            raise RuntimeError("boom")

        def to_numpy(self, *args, **kwargs):
            raise RuntimeError("boom")

    real_series = backtest_mod.pd.Series
    injected = {"n": 0}

    def series_factory(data=None, index=None, *args, **kwargs):
        obj = real_series(data=data, index=index, *args, **kwargs)
        if injected["n"] < 1 and index is not None and len(obj) == len(returns.index):
            try:
                np.asarray(obj.to_numpy(dtype=float), dtype=float)
                injected["n"] += 1
                return ExplodingSeries(obj)
            except Exception:
                pass
        return obj

    monkeypatch.setattr(backtest_mod.pd, "Series", series_factory)
    res = backtest_mod.run_backtest(returns, weights)
    assert isinstance(res, pd.DataFrame)
    assert len(res) == len(returns.index)


def test_finiteness_hardening_where_branch_repairs_nonfinite_arr(monkeypatch):
    """Covers lines 122-123: the np.where(...) repair when arr_pr still has non-finite.

    Force the line-114 replace to raise (so the line-116 except pass leaves
    non-finite values in portfolio_returns) and inject inf into the returns so
    arr_pr at line 119 is non-finite, exercising the np.where repair.
    """
    returns, weights = _returns_weights(periods=8, seed=9)
    # Inject a non-finite value into the returns so portfolio_returns carries it.
    returns = returns.copy()
    returns.iloc[3, 0] = np.inf
    returns.iloc[5, 1] = -np.inf

    real_replace = pd.Series.replace
    triggered = {"n": 0}

    def raising_replace(self, *args, **kwargs):
        # Only trip the defensive except on the portfolio_returns series (which
        # carries non-finite values); let all other replace calls through.
        try:
            arr = self.to_numpy(dtype=float)
            if not np.all(np.isfinite(arr)):
                triggered["n"] += 1
                raise RuntimeError("force line-116 except pass")
        except RuntimeError:
            raise
        except Exception:
            pass
        return real_replace(self, *args, **kwargs)

    monkeypatch.setattr(pd.Series, "replace", raising_replace)
    res = backtest_mod.run_backtest(returns, weights)
    assert triggered["n"] >= 1
    assert np.all(np.isfinite(res["returns"].to_numpy(dtype=float)))
    assert np.all(np.isfinite(res["cumulative"].to_numpy(dtype=float)))


def test_cumulative_fallback_forward_fills_bad_cumprod_entries(monkeypatch):
    """Covers line 144: the i>0 forward-fill branch in the cumprod fallback.

    Force the log1p path to raise and make cumprod produce non-finite entries at
    index 0 and 1 so the loop's i>0 branch (forward-fill from previous) executes.
    """
    returns, weights = _returns_weights(periods=8, seed=10)

    def raising_log1p(_x):
        raise RuntimeError("force cumulative fallback")

    real_cumprod = pd.Series.cumprod

    def bad_cumprod(self, axis=None, skipna=True, *args, **kwargs):
        base = real_cumprod(self, axis=axis, skipna=skipna, *args, **kwargs)
        arr = np.asarray(base.to_numpy(dtype=float), dtype=float).copy()
        if arr.size > 2:
            arr[0] = np.inf
            arr[1] = np.nan
        return pd.Series(arr, index=self.index)

    monkeypatch.setattr(backtest_mod.np, "log1p", raising_log1p)
    monkeypatch.setattr(pd.Series, "cumprod", bad_cumprod)
    res = backtest_mod.run_backtest(returns, weights)
    cum = res["cumulative"].to_numpy(dtype=float)
    assert np.all(np.isfinite(cum))
    assert cum[0] == 1.0  # i==0 -> 1.0
    assert cum[1] == 1.0  # i>0 -> forward-fill from cum[0] == 1.0


def test_cumulative_fallback_ones_branch_when_inner_fallback_raises(monkeypatch):
    """Covers lines 148-149: final except when the cumprod fallback itself raises."""
    returns, weights = _returns_weights(periods=8, seed=11)

    def raising_log1p(_x):
        raise RuntimeError("force cumulative fallback")

    def raising_cumprod(self, axis=None, skipna=True, *args, **kwargs):
        raise RuntimeError("cumprod failure")

    monkeypatch.setattr(backtest_mod.np, "log1p", raising_log1p)
    monkeypatch.setattr(pd.Series, "cumprod", raising_cumprod)
    res = backtest_mod.run_backtest(returns, weights)
    cum = res["cumulative"].to_numpy(dtype=float)
    assert np.all(cum == 1.0)
    assert np.all(np.isfinite(cum))
    assert list(res.columns) == ["returns", "gross_return", "cost_drag", "slippage_drag", "cumulative"]
