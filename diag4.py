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

# 791-792: name-match elementwise apply raising. Need parsed (Series of tz-aware Timestamps)
# where parsed.apply raises. Real pandas apply over tz-aware Timestamps works.
# Try: parsed is a Series subclass whose apply raises.
class BoomApply(pd.Series):
    @property
    def _constructor(self): return BoomApply
    def apply(self, *a, **k): raise RuntimeError("apply boom")
# Need _coerce_to_datetime_scalar to return tz-aware Timestamps for 'date' col.
# Use tz-aware ISO strings -> coercer returns tz-aware Timestamp.
df = pd.DataFrame({'date': ['2024-01-01T00:00:00Z','2024-01-02T00:00:00Z'], 'BTC':[0.01,0.02], 'ETH':[0.03,0.04]})
# Replace df['date'] with BoomApply so apply raises at 783
df['date'] = BoomApply(df['date'].values)
run("791-792 boom apply", lambda: dl.validate_returns_dataframe(df, benchmark='BTC', quality=False))

# 859: unnamed col value with no tzinfo but Timestamp(value) is tz-aware
# Try value = pd.Timestamp('2024-01-01', tz='UTC') stored in object series
df2 = pd.DataFrame({'Unnamed: 0': [pd.Timestamp('2024-01-01', tz='UTC'), pd.Timestamp('2024-01-02', tz='UTC')], 'BTC':[0.01,0.02], 'ETH':[0.03,0.04]})
run("859 unnamed tz timestamp", lambda: dl.validate_returns_dataframe(df2, benchmark='BTC', quality=False))

# 867-868: unnamed single-row where apply returns scalar
df3 = pd.DataFrame({'Unnamed: 0': ['2024-01-01'], 'BTC':[0.01], 'ETH':[0.04]}, index=pd.RangeIndex(1))
run("867-868 single-row unnamed", lambda: dl.validate_returns_dataframe(df3, benchmark='BTC', quality=False, min_rows=1))

# 901-903: last-resort object col with tz-aware strings
df4 = pd.DataFrame({'BTC':[0.01,0.02,0.03], 'ETH':[0.04,0.05,0.06], 'mystery': ['2024-01-01T00:00:00Z','2024-01-02T00:00:00Z','2024-01-03T00:00:00Z']}, index=pd.RangeIndex(3))
run("901-903 mystery tz", lambda: dl.validate_returns_dataframe(df4, benchmark='BTC', quality=False))

# 908-914: last-resort where set_index result is not DatetimeIndex
class WeirdSet(pd.DataFrame):
    @property
    def _constructor(self): return WeirdSet
    def set_index(self, keys, *a, **k):
        res = super().set_index(keys, *a, **k)
        res.index = pd.Index(['a','b','c'])
        return res
df5 = WeirdSet({'BTC':[0.01,0.02,0.03], 'ETH':[0.04,0.05,0.06], 'mystery': ['2024-01-01','2024-01-02','2024-01-03']}, index=pd.RangeIndex(3))
run("908-914 weird set_index", lambda: dl.validate_returns_dataframe(df5, benchmark='BTC', quality=False))

# 1530-1531: first rename raises
class FlakyRename(pd.DataFrame):
    _n = 0
    @property
    def _constructor(self): return FlakyRename
    def rename(self, *a, **k):
        FlakyRename._n += 1
        if FlakyRename._n == 1:
            raise RuntimeError('boom')
        return super().rename(*a, **k)
df6 = FlakyRename({'date': pd.to_datetime(['2024-01-01','2024-01-02','2024-01-03','2024-01-04','2024-01-05']), 'btc':[0.01]*5, 'ETH':[0.02]*5})
FlakyRename._n = 0
run("1530-1531 flaky rename", lambda: dl.validate_returns_dataframe(df6, benchmark='BTC', quality=False))

# 1591-1592: csv defensive empty
import tempfile
p = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
p.write(b'date,BTC,ETH\n2024-01-01,0.01,0.02\n2024-01-02,0.01,0.02\n')
p.close()
class StateEmpty(pd.DataFrame):
    _c = 0
    @property
    def _constructor(self): return StateEmpty
    @property
    def empty(self):
        StateEmpty._c += 1
        if StateEmpty._c >= 3:
            return True
        return super().empty
orig = pd.read_csv
def fake(*a, **k):
    return StateEmpty(orig(*a, **k))
pd.read_csv = fake
StateEmpty._c = 0
try:
    run("1591-1592 csv empty", lambda: dl.load_returns_from_csv(p.name, benchmark='BTC', quality=False))
finally:
    pd.read_csv = orig