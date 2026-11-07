"""Debug which mechanisms hit beta.py lines."""
import numpy as np
import pandas as pd
from strategies.betting_against_beta import beta

# 130-131: min_obs non-convertible
print("=== 130-131 ===")
for mo in ["abc", [1, 2], {"a": 1}]:
    try:
        r = beta.calculate_beta(pd.Series([1.0, 2.0, 3.0]), pd.Series([2.0, 4.0, 6.0]), min_obs=mo)
        print(f"  min_obs={mo!r}: -> {r}")
    except Exception as e:
        print(f"  min_obs={mo!r}: {type(e).__name__}: {e}")

# 101-102: monkeypatch pd.concat
print("=== 101-102 ===")
orig = pd.concat
pd.concat = lambda *a, **k: (_ for _ in ()).throw(ValueError("bad"))
try:
    r = beta.calculate_beta(pd.Series([1.0, 2.0, 3.0, 4.0], index=[10,20,30,40]), pd.Series([2.0, 4.0, 6.0], index=[10,20,30]))
    print(f"  concat raises: -> {r}")
except Exception as e:
    print(f"  concat raises: {type(e).__name__}: {e}")
finally:
    pd.concat = orig

# 429-433: rolling monkeypatch
print("=== 429-433 ===")
idx = pd.date_range("2023-01-01", periods=60, freq="D")
rng = np.random.default_rng(5)
mkt = rng.normal(0, 0.01, 60)
df = pd.DataFrame({"BTC": mkt, "ETH": ["a", "b"] * 30}, index=idx)
orig_rolling = pd.DataFrame.rolling
print(f"  rolling type: {type(pd.DataFrame.rolling)}")
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