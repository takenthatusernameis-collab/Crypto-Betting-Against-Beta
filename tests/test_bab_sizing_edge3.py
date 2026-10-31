import numpy as np
import pandas as pd
from strategies.betting_against_beta import sizing


def test_kelly_nonnan_sig():
    idx = pd.date_range("2020-01-01", periods=80)
    sig = pd.DataFrame({"A": np.ones(80), "B": -np.ones(80)}, index=idx)
    rets = pd.DataFrame({"A": np.full(80, np.nan), "B": np.full(80, np.nan)}, index=idx)
    out = sizing.apply_position_sizing(sig, returns=rets, sizer=sizing.KellySizer(lookback=60))
    assert isinstance(out, pd.DataFrame)
