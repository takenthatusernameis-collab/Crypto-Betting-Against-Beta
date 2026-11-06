import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import numpy as np
import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

def run(label, df, bench='BTC', quality=False, min_rows=1):
    try:
        r = dl.validate_returns_dataframe(df, benchmark=bench, quality=quality, min_rows=min_rows)
        print(label, "-> OK cols=", list(r.columns), "idx=", type(r.index).__name__)
    except Exception as e:
        print(label, "-> RAISED", type(e).__name__, str(e)[:70])

# 894 + 895-914: RangeIndex, object col 'mystery' parses as datetime, no candidate name
idx = pd.RangeIndex(5)
df = pd.DataFrame({'BTC':[0.01,0.02,0.03,0.04,0.05], 'ETH':[0.04,0.05,0.06,0.07,0.08], 'mystery': ['2024-01-01','2024-01-02','2024-01-03','2024-01-04','2024-01-05']}, index=idx)
run("894+895-907 mystery object", df)

# 901-903: mystery with tz-aware strings
df2 = pd.DataFrame({'BTC':[0.01,0.02,0.03,0.04,0.05], 'ETH':[0.04,0.05,0.06,0.07,0.08], 'mystery': ['2024-01-01T00:00:00Z','2024-01-02T00:00:00Z','2024-01-03T00:00:00Z','2024-01-04T00:00:00Z','2024-01-05T00:00:00Z']}, index=idx)
run("901-903 mystery tz-aware", df2)

# 894 only: datetime64 column
df3 = pd.DataFrame({'BTC':[0.01,0.02,0.03,0.04,0.05], 'ETH':[0.04,0.05,0.06,0.07,0.08], 'other_date': pd.to_datetime(['2024-01-01','2024-01-02','2024-01-03','2024-01-04','2024-01-05'])}, index=idx)
run("894 datetime64 col", df3)

# 867-868: single-row unnamed column -> apply returns scalar
df4 = pd.DataFrame({'Unnamed: 0': ['2024-01-01'], 'BTC':[0.01], 'ETH':[0.04]}, index=pd.RangeIndex(1))
run("867-868 single-row unnamed", df4, min_rows=1)

# 859: unnamed col with value that has no tzinfo but Timestamp(value) is tz-aware
# Try a value that is a pd.Timestamp with tz but .tzinfo raises? Hard. Try numpy datetime64 with timezone via astype?
# Try: value = pd.Timestamp('2024-01-01', tz='UTC') but stored in object series -> has tzinfo -> 854 branch
# Try value = np.datetime64 with 'Z'? numpy datetime64 has no tz
df5 = pd.DataFrame({'Unnamed: 0': [np.datetime64('2024-01-01T00:00:00Z')], 'BTC':[0.01], 'ETH':[0.04]}, index=pd.RangeIndex(1))
run("859 numpy dt64 unnamed", df5, min_rows=1)

# 1530-1536: benchmark case-insensitive rename
df6 = pd.DataFrame({'date': pd.to_datetime(['2024-01-01','2024-01-02','2024-01-03','2024-01-04','2024-01-05']), 'btc':[0.01]*5, 'ETH':[0.02]*5})
run("1530 case-insensitive bench", df6)

# 1533-1536 second bench_map: benchmark not in columns after first rename failed, case-insensitive still present
# Need bench_found != benchmark, benchmark not in columns, first rename raises -> 1530-1531, then 1532 benchmark not in columns -> 1533-1536
class FlakyRename(pd.DataFrame):
    _n = 0
    @property
    def _constructor(self): return FlakyRename
    def rename(self, *a, **k):
        FlakyRename._n += 1
        if FlakyRename._n == 1:
            raise RuntimeError('boom')
        return super().rename(*a, **k)
df7 = FlakyRename({'date': pd.to_datetime(['2024-01-01','2024-01-02','2024-01-03','2024-01-04','2024-01-05']), 'btc':[0.01]*5, 'ETH':[0.02]*5})
FlakyRename._n = 0
run("1533-1536 flaky rename", df7)