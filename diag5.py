import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import numpy as np
import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

def run(label, fn):
    try:
        r = fn()
        print(label, "-> OK", type(r).__name__ if r is not None else None)
    except Exception as e:
        print(label, "-> RAISED", type(e).__name__, str(e)[:70])

# Direct calls to _promote_datetime_column (bypasses _normalize_columns which drops unnamed)

# 843-873 unnamed branch
df = pd.DataFrame({'Unnamed: 0': ['2024-01-01','2024-01-02'], 'BTC':[0.01,0.02], 'ETH':[0.03,0.04]})
run("843 unnamed", lambda: dl._promote_datetime_column(df))

# 859: unnamed value with no tzinfo but Timestamp(value) tz-aware
df2 = pd.DataFrame({'Unnamed: 0': [pd.Timestamp('2024-01-01', tz='UTC'), pd.Timestamp('2024-01-02', tz='UTC')], 'BTC':[0.01,0.02], 'ETH':[0.03,0.04]})
run("859 unnamed tz ts", lambda: dl._promote_datetime_column(df2))

# 867-868: single-row unnamed
df3 = pd.DataFrame({'Unnamed: 0': ['2024-01-01'], 'BTC':[0.01], 'ETH':[0.04]})
run("867 single-row unnamed", lambda: dl._promote_datetime_column(df3))

# 885-914 last resort
df4 = pd.DataFrame({'BTC':[0.01,0.02], 'ETH':[0.03,0.04], 'mystery': ['2024-01-01','2024-01-02']})
run("885 last resort", lambda: dl._promote_datetime_column(df4))

# 901-903 last resort tz
df5 = pd.DataFrame({'BTC':[0.01,0.02], 'ETH':[0.03,0.04], 'mystery': ['2024-01-01T00:00:00Z','2024-01-02T00:00:00Z']})
run("901 last resort tz", lambda: dl._promote_datetime_column(df5))

# 908-914 last resort weird set_index
class WeirdSet(pd.DataFrame):
    @property
    def _constructor(self): return WeirdSet
    def set_index(self, keys, *a, **k):
        res = super().set_index(keys, *a, **k)
        res.index = pd.Index(['a','b'])
        return res
df6 = WeirdSet({'BTC':[0.01,0.02], 'ETH':[0.03,0.04], 'mystery': ['2024-01-01','2024-01-02']})
run("908 last resort weird set", lambda: dl._promote_datetime_column(df6))

# 791-792: name-match where getattr(parsed,'tz') raises
class WeirdSeries(pd.Series):
    @property
    def _constructor(self): return WeirdSeries
    @property
    def tz(self):
        raise RuntimeError("tz boom")
df7 = pd.DataFrame({'date': ['2024-01-01','2024-01-02'], 'BTC':[0.01,0.02], 'ETH':[0.03,0.04]})
df7['date'] = WeirdSeries(df7['date'].values)
run("791 weird tz", lambda: dl._promote_datetime_column(df7))