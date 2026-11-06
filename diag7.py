import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import strategies.betting_against_beta.data_loader as dl

# Trace which lines execute in _promote_datetime_column for the last-resort case
import linecache

df = pd.DataFrame({'BTC':[0.01,0.02], 'ETH':[0.03,0.04], 'mystery': ['2024-01-01','2024-01-02']})
print("columns:", list(df.columns))
print("dtypes:", df.dtypes.to_dict())
for c in df.columns:
    print(c, "is_string:", pd.api.types.is_string_dtype(df[c]), "is_object:", pd.api.types.is_object_dtype(df[c]), "is_numeric:", pd.api.types.is_numeric_dtype(df[c]))
out = dl._promote_datetime_column(df)
print("RESULT cols", list(out.columns), "idx", type(out.index).__name__)