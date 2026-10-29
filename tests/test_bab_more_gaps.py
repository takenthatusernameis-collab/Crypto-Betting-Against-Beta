import numpy as np
import pandas as pd

from strategies.betting_against_beta import regime, quality, errors
from strategies.betting_against_beta.errors import BABDataError


def test_regime_default_and_vol():
    idx = pd.date_range("2023-01-01", periods=10)
    mkt = pd.Series(0.01 * np.random.RandomState(0).randn(10), index=idx)
    r = regime.classify_volatility_regimes(mkt.to_frame("BTC"))
    assert r is not None
    r2 = regime.classify_volatility_regimes_percentile(mkt.to_frame("BTC"))
    assert r2 is not None


def test_quality_functions():
    idx = pd.date_range("2023-01-01", periods=5)
    df = pd.DataFrame({"BTC": [0.01, 0.02, -0.01, 0.01, 0.02]}, index=idx)
    q = quality.data_quality_report(df)
    assert isinstance(q, dict)
    assert quality.check_data_quality(df) in (True, False)


def test_errors_alias():
    assert BABDataError is errors.BABDataError
