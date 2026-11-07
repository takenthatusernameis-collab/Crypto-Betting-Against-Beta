"""Trace which call hits 92-93."""
import coverage

cov = coverage.Coverage(source=['strategies.betting_against_beta'])
cov.start()

import numpy as np
import pandas as pd
import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import _coerce_series_to_datetime_index

# Series subclass whose __iter__ raises
class BadIter(pd.Series):
    def __iter__(self):
        raise RuntimeError("boom-iter")

df = pd.DataFrame({"date": [1, 2], "BTC": [1.0, 2.0]})
coerced = BadIter([pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")])
print("BadIter type at call:", type(coerced))
ok = _coerce_series_to_datetime_index(df, "date", coerced)
print("BadIter result:", ok)

# DataFrame subclass whose copy() raises
class BadCopy(pd.DataFrame):
    def copy(self, *a, **k):
        raise RuntimeError("boom-copy")

df2 = BadCopy({"date": [1, 2], "BTC": [1.0, 2.0]})
print("BadCopy type at call:", type(df2))
coerced2 = pd.Series([pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")])
ok2 = _coerce_series_to_datetime_index(df2, "date", coerced2)
print("BadCopy result:", ok2)

cov.stop()
cov.save()
data = cov.get_data()
for f in data.measured_files():
    if f.endswith('data_loader.py'):
        executed = sorted(l for l in range(64, 100) if l in data.lines(f))
        print('Executed 64-99:', executed)