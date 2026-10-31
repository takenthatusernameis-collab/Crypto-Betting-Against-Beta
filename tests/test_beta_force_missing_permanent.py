import numpy as np
import pandas as pd

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.data_loader import BABDataError


def test_rolling_beta_fallthrough_all_fail_paths():
    class Bad:
        def __len__(self):
            raise RuntimeError()

    class Worse:
        pass

    old = np.asarray
    try:
        def fake_asarray(x, *args, **kwargs):
            if isinstance(x, (Bad, Worse)):
                raise RuntimeError("x")
            return old(x, *args, **kwargs)
        np.asarray = fake_asarray
        res = beta.rolling_beta(Bad(), Worse(), window=5)
        assert isinstance(res, np.ndarray)
    finally:
        np.asarray = old


def test_calculate_beta_y_none():
    res = beta.calculate_beta([], [])
    assert np.isnan(res)


def test_calculate_beta_empty_after_mask():
    res = beta.calculate_beta([np.nan, np.inf], [np.inf, np.nan])
    assert np.isnan(res)


def test_calculate_beta_nonfinite_beta_result():
    res = beta.calculate_beta([np.inf, np.inf, np.inf], [1.0, 2.0, 3.0])
    assert np.isnan(res)


def test_calculate_beta_linalg_error():
    class BadArr:
        def __array__(self, dtype=None):
            raise np.linalg.LinAlgError("bad")
    res = beta.calculate_beta(BadArr(), [1.0, 2.0, 3.0])
    assert np.isnan(res)


def test_calculate_beta_babdataerror_reraise():
    try:
        beta.calculate_beta(None, np.array([1.0, 2.0]))
        assert False
    except BABDataError:
        pass


def test_calculate_beta_fast_empty_mask():
    res = beta.calculate_beta_fast([np.nan], [np.nan])
    assert np.isnan(res)


def test_calculate_beta_fast_nonfinite_beta():
    res = beta.calculate_beta_fast([1.0, 2.0, 3.0], [0.0, 0.0, 0.0])
    assert res == 0.0


def test_calculate_beta_fast_exceptions():
    class Bad1:
        def __array__(self, dtype=None):
            raise np.linalg.LinAlgError()
    assert beta.calculate_beta_fast(Bad1(), [1, 2, 3]) == 0.0
    class Bad2:
        def __array__(self, dtype=None):
            raise TypeError()
    assert beta.calculate_beta_fast(Bad2(), [1, 2, 3]) == 0.0
    class Bad3:
        def __array__(self, dtype=None):
            raise ValueError()
    assert beta.calculate_beta_fast(Bad3(), [1, 2, 3]) == 0.0
    class Bad4:
        def __array__(self, dtype=None):
            raise AttributeError()
    assert beta.calculate_beta_fast(Bad4(), [1, 2, 3]) == 0.0


def test_calculate_rolling_beta_bench_both_fail():
    class BadBench:
        def __init__(self, vals):
            self.vals = np.array(vals)
        def to_numpy(self, *args, **kwargs):
            raise TypeError("t1")
        def __array__(self, dtype=None):
            raise ValueError("t2")
        def __len__(self):
            return len(self.vals)

    class WeirdDF(pd.DataFrame):
        def __getitem__(self, key):
            if key == 'MKT':
                return BadBench(np.random.randn(len(self)))
            return super().__getitem__(key)

    df = WeirdDF({'A': np.random.randn(100)})
    try:
        beta.calculate_rolling_beta(df, 'MKT', window=50, min_obs=50)
        assert False
    except BABDataError:
        pass


def test_calculate_rolling_beta_outer_bad_asset_both_fail():
    class BadAsset:
        def to_numpy(self, *args, **kwargs):
            raise TypeError()
        def __array__(self, dtype=None):
            raise ValueError()
        def __len__(self):
            return 150

    df = pd.DataFrame({'MKT': np.random.randn(150), 'BAD': BadAsset()})
    try:
        beta.calculate_rolling_beta(df, 'MKT', window=60, min_obs=60)
        assert False
    except BABDataError:
        pass
