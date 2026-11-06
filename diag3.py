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

# 1926-1929: _drop_metadata_columns - non-positive all-integer sequential col
df = pd.DataFrame({'date': pd.to_datetime(['2024-01-01','2024-01-02','2024-01-03']), 'rowid':[0,1,2], 'BTC':[100.0,101.0,102.0]})
run("1926-1929 rowid", lambda: dl._drop_metadata_columns(df))

# 1926-1929: minv<=0 allclose round
df2 = pd.DataFrame({'date': pd.to_datetime(['2024-01-01','2024-01-02','2024-01-03']), 'junk':[0,1,2], 'BTC':[100.0,101.0,102.0]})
run("1926-1929 junk", lambda: dl._drop_metadata_columns(df2))

# 2160-2163: normalize_schema MultiIndex
mi = pd.MultiIndex.from_tuples([('A','x'),('A','y'),('B','z')])
df3 = pd.DataFrame([[0.01,0.02,0.03]], columns=mi)
df3.index = pd.to_datetime(['2024-01-01'])
run("2160-2163 multiindex", lambda: dl.normalize_schema(df3, benchmark=None))

# 2167-2168: normalize_schema first-row headers
df4 = pd.DataFrame({'Unnamed: 0': ['BTC','ETH'], 'Unnamed: 1': [100.0, 10.0], 'Unnamed: 2': [101.0, 11.0]})
run("2167-2168 first-row headers", lambda: dl.normalize_schema(df4, benchmark=None))

# 2187-2189: normalize_schema junk drop except
df5 = pd.DataFrame({'date': pd.to_datetime(['2024-01-01','2024-01-02']), 'junkcol': ['abc','def'], 'BTC':[0.01,0.02]})
run("2187-2189 junk drop", lambda: dl.normalize_schema(df5, benchmark=None))

# 2192-2193: normalize_schema cols_to_drop except
class WeirdCols(pd.DataFrame):
    @property
    def _constructor(self): return WeirdCols
    @property
    def columns(self):
        raise RuntimeError("cols boom")
df6 = WeirdCols({'date': pd.to_datetime(['2024-01-01','2024-01-02']), 'BTC':[0.01,0.02]})
run("2192-2193 weird cols", lambda: dl.normalize_schema(df6, benchmark=None))

# 1097-1098: _drop_all_nan_columns except
df7 = pd.DataFrame({'BTC':[np.nan, np.nan], 'ETH':[0.01, 0.02]})
class BadDrop(pd.DataFrame):
    @property
    def _constructor(self): return BadDrop
    def __getitem__(self, k):
        raise RuntimeError("getitem boom")
df8 = BadDrop({'BTC':[np.nan, np.nan], 'ETH':[0.01, 0.02]})
run("1097-1098 bad getitem", lambda: dl._drop_all_nan_columns(df8))

# 1626-1627: parquet OSError
run("1626-1627 parquet missing", lambda: dl.load_returns_from_parquet('/nonexistent/file.parquet'))

# 1663-1664: hdf5 OSError
run("1663-1664 hdf5 missing", lambda: dl.load_returns_from_hdf5('/nonexistent/file.h5'))