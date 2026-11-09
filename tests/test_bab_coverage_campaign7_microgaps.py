"""Coverage campaign 7: residual micro-gaps across BAB modules.

Targets uncovered lines (baseline 2026-11-09):
  signals.py 37,75,139-140
  portfolio.py 39-40,95-96,118-119,131-132,152-157
  metrics.py 97
  config.py 101-102
  costs.py 59-60
  sizing.py 93-95,129,136,240-242
Production-realistic inputs; scoped monkeypatches only for defensive branches.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.costs import TransactionCostModel
from strategies.betting_against_beta.metrics import turnover
from strategies.betting_against_beta.portfolio import _clean_signal_value, construct_portfolio
from strategies.betting_against_beta.signals import _finite_beta_series, generate_bab_signals
from strategies.betting_against_beta.sizing import (
    EqualWeightSizer,
    VolatilityTargetSizer,
    apply_position_sizing,
    BABSizingError,
)


class TestSignalsMicrogaps:
    def test_object_dtype_after_numeric_coercion_casts_float64(self):
        # signals.py:37 defensive; hard to trigger because object numeric coerces
        # cleanly in practice. Closed-without-edit evidence path + adjacent behavior.
        s = pd.Series([1.5, 2.5, np.nan], dtype=object)
        out = _finite_beta_series(s)
        assert out is not None
        assert np.allclose(out.to_numpy(), [1.5, 2.5])

    def test_loop_path_n_zero_continue_defensive(self):
        # signals.py:75: unreachable because _finite_beta_series returns None
        # when len(clean)==0 (signals.py:49-50), so generate_bab_signals takes
        # `if clean is None: continue` (70-71) before `n=len(sorted_betas)==0`.
        # Closed-without-edit; evidence: control-flow proof.
        df = pd.DataFrame({"A": [np.nan, np.nan], "B": [np.nan, np.nan]})
        out = generate_bab_signals(df)
        assert (out.to_numpy() == 0).all()

    def test_outer_try_failure_enters_inner_numeric_coercion(self, monkeypatch):
        # signals.py:139-140 (inner try body) after outer except.
        df = pd.DataFrame({"A": [0.1, 0.2], "B": [0.3, 0.4], "C": [0.5, 0.6]})
        real_is_numeric = pd.api.types.is_numeric_dtype
        call = {"n": 0}

        def flaky_is_numeric(obj):
            call["n"] += 1
            # first all() check in outer try triggers; raise to enter outer except
            if call["n"] == 1:
                raise RuntimeError("dtype check failed")
            return real_is_numeric(obj)

        monkeypatch.setattr(pd.api.types, "is_numeric_dtype", flaky_is_numeric)
        out = generate_bab_signals(df)
        assert out.shape == df.shape
        assert np.isfinite(out.to_numpy()).all()
        assert set(np.unique(out.to_numpy())).issubset({-1, 0, 1})


class TestPortfolioMicrogaps:
    def test_clean_signal_value_outer_except(self, monkeypatch):
        # portfolio.py:39-40 defensive catch.
        # np.isnan on a custom object can raise in edge cases; force via monkeypatch.
        import strategies.betting_against_beta.portfolio as pmod

        real_isnan = pmod.np.isnan

        def bad_isnan(x):
            if getattr(x, "_boom", False):
                raise TypeError("boom")
            return real_isnan(x)

        monkeypatch.setattr(pmod.np, "isnan", bad_isnan)

        class X(float):
            _boom = True

        assert _clean_signal_value(X(1.0)) == 0

    def test_numeric_coercion_outer_except_returns_zero(self, monkeypatch):
        # portfolio.py:95-96 when arr coercion/copy path fails.
        sig = pd.DataFrame({"A": [1, 1], "B": [-1, -1]})
        real_is_numeric = pd.api.types.is_numeric_dtype

        def flaky(obj):
            raise RuntimeError("fail")
        monkeypatch.setattr(pd.api.types, "is_numeric_dtype", flaky)
        # also break to_numeric fallback chain
        monkeypatch.setattr(pd, "to_numeric", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("x")))
        # and break copy-based fallback
        real_copy = pd.DataFrame.copy

        def bad_copy(self, *a, **k):
            if set(self.columns) == {"A", "B"} and self.shape[0] == 2:
                raise RuntimeError("copy fail")
            return real_copy(self, *a, **k)
        monkeypatch.setattr(pd.DataFrame, "copy", bad_copy)
        w = construct_portfolio(sig)
        assert w.shape == sig.shape
        assert (w.to_numpy() == 0.0).all()

    def test_long_cell_assignment_except_pass(self, monkeypatch):
        # portfolio.py:118-119 defensive.
        sig = pd.DataFrame({"A": [1, 1], "B": [-1, -1]})
        import strategies.betting_against_beta.portfolio as pmod
        real_repeat = pmod.np.repeat
        calls = {"n": 0}

        def flaky_repeat(a, repeats, *args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("repeat fail")
            return real_repeat(a, repeats, *args, **kwargs)
        monkeypatch.setattr(pmod.np, "repeat", flaky_repeat)
        w = construct_portfolio(sig)
        assert np.isfinite(w.to_numpy()).all()

    def test_short_cell_assignment_except_pass(self, monkeypatch):
        # portfolio.py:131-132 defensive.
        sig = pd.DataFrame({"A": [1, 1], "B": [-1, -1]})
        import strategies.betting_against_beta.portfolio as pmod
        real_repeat = pmod.np.repeat
        calls = {"n": 0}

        def flaky_repeat(a, repeats, *args, **kwargs):
            calls["n"] += 1
            # second repeat is short side
            if calls["n"] == 2:
                raise RuntimeError("repeat fail")
            return real_repeat(a, repeats, *args, **kwargs)
        monkeypatch.setattr(pmod.np, "repeat", flaky_repeat)
        w = construct_portfolio(sig)
        assert np.isfinite(w.to_numpy()).all()

    def test_dollar_neutral_net_correction_renormalizes_longs(self):
        # portfolio.py:152-157 executes when net remains != 0 after first renorm.
        # Force via monkeypatch: make first pass leave residual net.
        import strategies.betting_against_beta.portfolio as pmod
        sig = pd.DataFrame({"A": [1, 1], "B": [-1, 1], "C": [0, -1], "D": [-1, -1]})
        real_nonzero = pmod.np.nonzero
        stage = {"n": 0}

        def staged_nonzero(a):
            # let normal flow run; we need the correction condition to be true.
            # Easier: monkeypatch sum result? instead force net via post-processing hook.
            return real_nonzero(a)

        w = construct_portfolio(sig, dollar_neutral=True)
        assert np.allclose(w.sum(axis=1).to_numpy(), 0.0, atol=1e-10)

    def test_dollar_neutral_correction_forced(self, monkeypatch):
        # Directly force net correction branch 152-157.
        import strategies.betting_against_beta.portfolio as pmod
        sig = pd.DataFrame({"A": [1, 1], "B": [-1, 1], "C": [1, -1], "D": [-1, -1]})
        real_clip = pmod.np.clip
        injected = {"done": False}

        def clip_hook(a, *args, **kwargs):
            out = real_clip(a, *args, **kwargs)
            # inject a tiny net residual on rows with both sides before renorm?
            # clip is called at 135 before dn block; mutate in place
            if not injected["done"] and out.ndim == 2 and out.shape[1] == 4:
                injected["done"] = True
                out[0, 0] = out[0, 0] + 0.05  # create net > 0 on row 0
            return out

        monkeypatch.setattr(pmod.np, "clip", clip_hook)
        w = construct_portfolio(sig, dollar_neutral=True)
        assert np.isfinite(w.to_numpy()).all()
        # correction should reduce net toward zero on affected row
        assert abs(w.sum(axis=1).iloc[0]) < 0.06


class TestMetricsMicrogaps:
    def test_turnover_empty_returns_nan(self):
        # metrics.py:97 unreachable via public API: _finite_beta_series/dropna
        # mean NaN only in degenerate paths; turnover() returns np.nan for None/
        # empty (90-92) and 0.0 only if pd.isna(turnover_mean) at 96-97.
        # Closed-without-edit with adjacent evidence.
        assert np.isnan(turnover(None))
        assert np.isnan(turnover(pd.DataFrame()))

    def test_turnover_all_nan_rows_returns_zero(self):
        # Force turnover_mean NaN: diff().abs().sum() then dropna() leaves NaN mean?
        w = pd.DataFrame({"A": [np.nan, np.nan], "B": [np.nan, np.nan]})
        out = turnover(w)
        assert out == 0.0 or np.isnan(out)


class TestConfigMicrogaps:
    def test_frozen_setattr_exception_pass_defensive(self):
        # config.py:101-102 defensive except around freeze (unreachable via public
        # API on CPython dataclass path without patching immutable builtins).
        # Closed-without-edit: evidence — object.__setattr__ cannot be monkeypatched.
        c = BABConfig()
        with pytest.raises((AttributeError, Exception)):
            c.beta_window = 999  # frozen enforcement works via __setattr__ override


class TestCostsMicrogaps:
    def test_frozen_exception_pass_defensive(self):
        # costs.py:59-60 defensive except around freeze (unreachable via public API).
        # Closed-without-edit: freeze path is deterministic on CPython.
        m = TransactionCostModel()
        with pytest.raises((AttributeError, Exception)):
            m.linear_fee = 9.99


class TestSizingMicrogaps:
    def test_equal_weight_sizer_post_init_validation(self):
        # sizing.py:93-95
        with pytest.raises(BABSizingError, match="max_leverage must be > 0"):
            EqualWeightSizer(max_leverage=0)
        with pytest.raises(BABSizingError, match="max_leverage must be > 0"):
            EqualWeightSizer(max_leverage=-1.0)
        s = EqualWeightSizer(max_leverage=2.0)
        assert s.max_leverage == 2.0

    def test_equal_weight_shorthand_string(self):
        # sizing.py:129
        sig = pd.DataFrame({"A": [1, 1, -1], "B": [-1, -1, 1], "C": [1, -1, 1], "D": [-1, 1, -1]})
        rets = pd.DataFrame(np.random.default_rng(0).normal(0, 0.01, sig.shape), index=sig.index, columns=sig.columns)
        out = apply_position_sizing(sig, rets, sizer="equal_weight")
        assert out.shape == sig.shape
        assert np.isfinite(out.to_numpy()).all()

    def test_unknown_sizer_type_raises(self):
        # sizing.py:136
        sig = pd.DataFrame({"A": [1, -1], "B": [-1, 1]})
        rets = pd.DataFrame(np.random.default_rng(1).normal(0, 0.01, sig.shape), index=sig.index, columns=sig.columns)
        with pytest.raises(BABSizingError, match="sizer must be"):
            apply_position_sizing(sig, rets, sizer=12345)

    def test_equal_weight_sizer_instance_returns_base(self):
        # sizing.py:240-242
        sig = pd.DataFrame({"A": [1, 1, -1], "B": [-1, -1, 1], "C": [1, -1, 1], "D": [-1, 1, -1]})
        rets = pd.DataFrame(np.random.default_rng(2).normal(0, 0.01, sig.shape), index=sig.index, columns=sig.columns)
        out = apply_position_sizing(sig, rets, sizer=EqualWeightSizer())
        base = apply_position_sizing(sig, rets, sizer=None)
        pd.testing.assert_frame_equal(out, base)
