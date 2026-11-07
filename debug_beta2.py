"""Debug why batch94 tests don't hit target lines."""
import numpy as np
import pandas as pd
from strategies.betting_against_beta import beta

# Test 130-131: int("abc") should raise
print("int('abc'):", end=" ")
try:
    int("abc")
    print("no raise!")
except (TypeError, ValueError) as e:
    print(f"{type(e).__name__}")

# Check the actual code path
print("\n=== calculate_beta with min_obs='abc' ===")
a = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
b = pd.Series([2.0, 4.0, 6.0, 8.0, 10.0])
r = beta.calculate_beta(a, b, min_obs="abc")
print(f"result: {r}")

# 194-195
print("\n=== calculate_beta_fast with min_obs='abc' ===")
r = beta.calculate_beta_fast([1.0, 2.0, 3.0, 4.0], [2.0, 4.0, 6.0, 8.0], min_obs="abc")
print(f"result: {r}")

# 101-102
print("\n=== calculate_beta with pd.concat raising ===")
orig = pd.concat
pd.concat = lambda *a, **k: (_ for _ in ()).throw(ValueError("bad"))
try:
    r = beta.calculate_beta(pd.Series([1.0, 2.0, 3.0, 4.0], index=[10,20,30,40]), pd.Series([2.0, 4.0, 6.0], index=[10,20,30]))
    print(f"result: {r}")
except Exception as e:
    print(f"raised: {type(e).__name__}: {e}")
finally:
    pd.concat = orig

# 429-433
print("\n=== estimate_betas with rolling raising + string column ===")
idx = pd.date_range("2023-01-01", periods=60, freq="D")
rng = np.random.default_rng(5)
mkt = rng.normal(0, 0.01, 60)
df = pd.DataFrame({"BTC": mkt, "ETH": ["a", "b"] * 30}, index=idx)
orig_rolling = pd.DataFrame.rolling
pd.DataFrame.rolling = lambda self, *a, **k: (_ for _ in ()).throw(ValueError("bad"))
try:
    out = beta.estimate_betas(df, benchmark="BTC", window=10, min_obs=5)
    print(f"result: shape={out.shape}")
except Exception as e:
    print(f"raised: {type(e).__name__}: {e}")
finally:
    pd.DataFrame.rolling = orig_rolling