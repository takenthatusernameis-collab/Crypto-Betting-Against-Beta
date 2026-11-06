import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import coverage
cov = coverage.Coverage(source=['strategies/betting_against_beta/data_loader.py'])
cov.start()
import strategies.betting_against_beta.data_loader as dl
# object dtype column
df = pd.DataFrame({'BTC':[0.01,0.02], 'ETH':[0.03,0.04], 'mystery': pd.Series(['2024-01-01','2024-01-02'], dtype=object)})
print("mystery dtype:", df['mystery'].dtype, "is_string:", pd.api.types.is_string_dtype(df['mystery']), "is_object:", pd.api.types.is_object_dtype(df['mystery']))
out = dl._promote_datetime_column(df)
print("RESULT cols", list(out.columns), "idx", type(out.index).__name__)
cov.stop()
cov.save()
cov.report(show_missing=True)