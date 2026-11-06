import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import numpy as np
import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

def show(label, fn):
    try:
        r = fn()
        print(label, "-> OK", type(r).__name__ if r is not None else None)
    except Exception as e:
        print(label, "-> RAISED", type(e).__name__, str(e)[:80])

# 894: datetime64 column that is not a candidate name, with DatetimeIndex already
idx = pd.date_range('2024-01-01', periods=3)
df = pd.DataFrame({'BTC':[0.01,0.02,0.03], 'ETH':[0.04,0.05,0.06], 'other_date': pd.to_datetime(['2024-01-01','2024-01-02','2024-01-03'])}, index=idx)
show("894 datetime64 col", lambda: dl.validate_returns_dataframe(df, benchmark='BTC', quality=False))

# 901-903: last-resort object column with tz-aware strings
df2 = pd.DataFrame({'mystery': ['2024-01-01T00:00:00Z','2024-01-02T00:00:00Z','2024-01-03T00:00:00Z'], 'BTC':[0.01,0.02,0.03], 'ETH':[0.04,0.05,0.06]}, index=idx)
show("901 tz-aware mystery", lambda: dl.validate_returns_dataframe(df2, benchmark='BTC', quality=False))

# Check what pd.to_datetime returns for tz strings
s = pd.Series(['2024-01-01T00:00:00Z','2024-01-02T00:00:00Z'])
p = pd.to_datetime(s, errors="raise")
print("to_datetime tz strings -> tz:", getattr(p,'tz',None), "dtype:", p.dtype)

# 859: unnamed column where values have no tzinfo but Timestamp(value) is tz-aware
# Need _coerce_to_datetime_scalar to return such a value. What if the unnamed col is int epoch ms?
df3 = pd.DataFrame({'Unnamed: 0': [1704067200000, 1704153600000, 1704240000000], 'BTC':[0.01,0.02,0.03], 'ETH':[0.04,0.05,0.06]}, index=idx)
show("859 unnamed epoch", lambda: dl.validate_returns_dataframe(df3, benchmark='BTC', quality=False))

# 1530-1536: benchmark case-insensitive rename
df4 = pd.DataFrame({'date': idx, 'btc':[0.01]*3, 'ETH':[0.02]*3})
show("1530 case-insensitive", lambda: dl.validate_returns_dataframe(df4, benchmark='BTC', quality=False))