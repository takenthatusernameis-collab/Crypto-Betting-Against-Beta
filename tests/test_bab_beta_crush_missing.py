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


class FakeCol:
    def to_numpy(self, *args, **kwargs):
        return None


class FakeAligned:
    def __len__(self):
        return 5

    def dropna(self):
        return self

    @property
    def iloc(self):
        class FakeIloc:
            def __getitem__(self, idx):
                return FakeCol()

        return FakeIloc()


def test_crush_66_67():
    # rolling_beta fallthrough: both _calc_rolling_beta_series paths fail and
    # the final fallthrough array allocation raises -> line 66-67.
    class Huge:
        def __len__(self):
            return 2 ** 40

    res = beta.rolling_beta(Huge(), Huge())
    assert isinstance(res, np.ndarray)
    assert res.shape == (1,)
    assert np.isnan(res[0])


def test_crush_114(monkeypatch):
    # calculate_beta: y is None -> line 114.
    # Two *real* series of different length so np.asarray succeeds, then the
    # Series-alignment path runs with a concat whose cell to_numpy() returns None.
    orig_concat = pd.concat
    pd.concat = lambda *a, **kw: FakeAligned()
    try:
        res = beta.calculate_beta(pd.Series([1.0, 2.0, 3.0, 4.0, 5.0]),
                                  pd.Series([1.0, 2.0, 3.0]))
        assert np.isnan(res)
    finally:
        pd.concat = orig_concat


def test_crush_124():
    # calculate_beta: mask empties out -> nan.
    s1 = pd.Series([np.nan, np.inf])
    s2 = pd.Series([np.nan, np.nan])
    assert np.isnan(beta.calculate_beta(s1, s2))


def test_crush_144_145():
    # calculate_beta: None input raises BABDataError.
    try:
        beta.calculate_beta(None, [1, 2, 3])
        assert False
    except BABDataError:
        pass


def test_crush_166():
    # calculate_beta_fast: everything non-finite -> nan.
    assert np.isnan(beta.calculate_beta_fast([np.nan], [np.inf]))


def test_crush_182_183():
    # calculate_beta_fast: 2D input makes the inner lstsq except path return 0.0.
    a = np.array([[1.0, 2.0], [3.0, 4.0]])
    b = np.array([[1.0, 2.0], [3.0, 4.0]])
    assert beta.calculate_beta_fast(a, b) == 0.0


def test_crush_184_185():
    # calculate_beta_fast: non-comparable min_obs triggers the outer except -> 0.0.
    assert beta.calculate_beta_fast([1.0, 2.0], [1.0, 2.0], min_obs="x") == 0.0


class BadToNumpy:
    def __init__(self, data):
        self._data = data

    def to_numpy(self, *args, **kwargs):
        raise TypeError("x")

    def __len__(self):
        return len(self._data)


def test_crush_355_359():
    # calculate_rolling_beta: an asset column that cannot be coerced raises
    # BABDataError from the bad-column conversion path.
    df = pd.DataFrame({"BTC": [0.01, 0.02, -0.01, 0.0] * 30})
    df["BAD"] = BadToNumpy([0.01] * 120)
    try:
        beta.calculate_rolling_beta(df, "BTC", window=90, min_obs=60)
        assert False
    except BABDataError:
        pass
