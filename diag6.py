import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import coverage
cov = coverage.Coverage(source=['/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta/strategies/betting_against_beta/data_loader.py'])
cov.start()
import pandas as pd
import strategies.betting_against_beta.data_loader as dl
df = pd.DataFrame({'BTC':[0.01,0.02], 'ETH':[0.03,0.04], 'mystery': ['2024-01-01','2024-01-02']})
out = dl._promote_datetime_column(df)
print("RESULT cols", list(out.columns), "idx", type(out.index).__name__)
cov.stop()
cov.save()
cov.report(show_missing=True)