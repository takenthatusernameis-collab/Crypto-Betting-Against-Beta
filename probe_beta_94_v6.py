"""Probe 101-102 and 429-433 via monkeypatching."""
import numpy as np
import pandas as pd
from strategies.betting_against_beta import beta

# 101-102: monkeypatch pd.concat to raise
print("=== 101-102 via pd.concat monkeypatch ===")
orig_concat = pd.concat
def raising_concat(*a, **k):
    raise ValueError("bad concat")
pd.concat = raising_concat
try:
    a = pd.Series([1.0, 2.0, 3.0, 4.0], index=[10, 20, 30, 40])
    b = pd.Series([2.0, 4.0, 6.0], index=[10, 20, 30])
    r = beta.calculate_beta(a, b)
    print(f"  concat raises: -> {r}")
except Exception as e:
    print(f"  concat raises: {type(e).__name__}: {e}")
finally:
    pd.concat = orig_concat

# 429-433: fast path raises, fallback succeeds
print("=== 429-433 via DataFrame.rolling monkeypatch ===")
idx = pd.date_range("2023-01-01", periods=60, freq="D")
rng = np.random.default_rng(5)
mkt = rng.normal(0, 0.01, 60)
df = pd.DataFrame({"BTC": mkt, "ETH": mkt.copy()})

orig_rolling = pd.DataFrame.rolling
def raising_rolling(self, *a, **k):
    raise ValueError("bad rolling")
pd.DataFrame.rolling = raising_rolling
try:
    out = beta.estimate_betas(df, benchmark="BTC", window=10, min_obs=5)
    print(f"  rolling raises: shape={out.shape}, has NaN: {out.isna().any().any()}")
except Exception as e:
    print(f"  rolling raises: {type(e).__name__}: {e}")
finally:
    pd.DataFrame.rolling = orig_rolling

# 429-433 variant: fast path raises, fallback also fails -> BABDataError
print("=== 429-433 fallback fails -> BABDataError ===")
# Need returns_df[asset].to_numpy(dtype=float) to fail in fallback too
# Monkeypatch Series.to_numpy to always raise
orig_to_numpy = pd.Series.to_numpy
def raising_to_numpy(self, *a, **k):
    raise TypeError("bad to_numpy")
pd.Series.to_numpy = raising_to_numpy
try:
    out = beta.estimate_betas(df, benchmark="BTC", window=10, min_obs=5)
    print(f"  to_numpy raises: shape={out.shape}")
except Exception as e:
    print(f"  to_numpy raises: {type(e).__name__}: {e}")
finally:
    pd.Series.to_numpy = orig_to_numpy