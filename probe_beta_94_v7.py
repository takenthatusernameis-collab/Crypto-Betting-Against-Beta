"""Probe 429-433: fast path raises + fallback column unconvertible."""
import numpy as np
import pandas as pd
from strategies.betting_against_beta import beta

idx = pd.date_range("2023-01-01", periods=60, freq="D")
rng = np.random.default_rng(5)
mkt = rng.normal(0, 0.01, 60)
# BTC numeric, ETH strings -> ETH goes to bad_cols
df = pd.DataFrame({"BTC": mkt, "ETH": ["a", "b"] * 30}, index=idx)

# Monkeypatch rolling to make fast path raise
orig_rolling = pd.DataFrame.rolling
def raising_rolling(self, *a, **k):
    raise ValueError("bad rolling")
pd.DataFrame.rolling = raising_rolling
try:
    out = beta.estimate_betas(df, benchmark="BTC", window=10, min_obs=5)
    print(f"  result: shape={out.shape}")
except Exception as e:
    print(f"  raised: {type(e).__name__}: {e}")
finally:
    pd.DataFrame.rolling = orig_rolling