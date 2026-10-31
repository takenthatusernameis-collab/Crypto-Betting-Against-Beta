import numpy as np
import pandas as pd

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.data_loader import BABDataError


class Dummy:
    def __init__(self, vals):
        self.vals = list(vals)
    def __len__(self):
        return len(self.vals)
    def __iter__(self):
        return iter(self.vals)


def test_crush_114(monkeypatch):
    orig_concat = pd.concat
    class FakeCol:
        def to_numpy(self, *args, **kwargs):
            return None
    class FakeAligned:
        def __len__(self):
            return 4
        def dropna(self):
            return self
        @property
        def iloc(self):
            class FakeIloc:
                def __getitem__(self, idx):
                    return FakeCol()
            return FakeIloc()
    monkeypatch.setattr(pd, "concat", lambda *a, **kw: FakeAligned())
    try:
        s1 = pd.Series([1, 2, 3, 4, 5])
        res = beta.calculate_beta(s1, Dummy([1, 2, 3]))
        assert np.isnan(res)
    finally:
        monkeypatch.setattr(pd, "concat", orig_concat)


def test_crush_124():
    s1 = pd.Series([np.nan, np.inf])
    s2 = pd.Series([np.nan, np.nan])
    res = beta.calculate_beta(s1, s2)
    assert np.isnan(res)


def test_crush_144_145():
    try:
        beta.calculate_beta(None, [1, 2, 3])
        assert False
    except BABDataError:
        pass


def test_crush_166():
    assert np.isnan(beta.calculate_beta_fast([np.nan], [np.inf]))


def test_crush_182_185():
    class Bad:
        def __array__(self, *args, **kwargs):
            raise AttributeError("x")
        def __len__(self):
            return 3
    assert beta.calculate_beta_fast(Bad(), [1, 2, 3]) == 0.0
    class Bad2:
        def __array__(self, *args, **kwargs):
            raise ValueError("x")
        def __len__(self):
            return 2
    assert beta.calculate_beta_fast([1, 2], Bad2()) == 0.0


class BadToNumpy:
    def __init__(self, data):
        self._data = data
    def to_numpy(self, *args, **kwargs):
        raise TypeError("x")
    def __len__(self):
        return len(self._data)


def test_crush_355_359():
    df = pd.DataFrame({"BTC": [0.01, 0.02, -0.01, 0.0] * 30})
    df["BAD"] = BadToNumpy([0.01] * 120)
    try:
        beta.calculate_rolling_beta(df, "BTC", window=90, min_obs=60)
        assert False
    except BABDataError:
        pass
