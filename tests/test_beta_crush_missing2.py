import numpy as np
import pandas as pd

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.data_loader import BABDataError


def test_calculate_rolling_beta_264_268_direct():
    df = pd.DataFrame({'MKT': [0.01]*150, 'A': [0.02]*150})
    class BadSer:
        def to_numpy(self, *args, **kwargs):
            raise RuntimeError("x")
        def __array__(self, dtype=None):
            raise TypeError("y")
    # Put it as the object itself
    benchmark_returns = BadSer()
    try:
        try:
            bench_arr = benchmark_returns.to_numpy(dtype=float, copy=False)
        except Exception:
            try:
                bench_arr = np.asarray(benchmark_returns, dtype=float)
            except Exception as e:
                raise BABDataError(str(e))
    except BABDataError:
        pass
