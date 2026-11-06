import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import numpy as np
import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

# Batch 72: stretch probes for remaining reachable missing lines

# 84: _coerce_series_to_datetime_index elementwise tz_convert branch.
# pdv is a tz-aware STRING (no tzinfo attr) -> pd.Timestamp(pdv) is tz-aware -> line 83->84.
def test_84_coerce_series_index_tz_string_elements():
    df = pd.DataFrame({'BTC': [0.01, 0.02]}, index=pd.RangeIndex(2))
    ok = dl._coerce_series_to_datetime_index(
        df, 'BTC',
        pd.Series(['2024-01-01T00:00:00+05:00', '2024-01-02T00:00:00+05:00']),
    )
    assert ok is True
