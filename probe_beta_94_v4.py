"""Probe remaining beta.py clusters."""
import numpy as np
import pandas as pd
from strategies.betting_against_beta import beta

# 356-359: is _finalize_betas ever called with 1D?
import inspect
src = inspect.getsource(beta.calculate_rolling_beta)
calls = [l.strip() for l in src.splitlines() if "_finalize_betas(" in l]
print("_finalize_betas calls:", calls)

# 429-433: except path with unconvertible column
print("=== 429-433 except path ===")
idx = pd.date_range("2023-01-01", periods=60, freq="D")
rng = np.random.default_rng(5)
mkt = rng.normal(0, 0.01, 60)
# Column that can't convert to float
df = pd.DataFrame({"BTC": mkt, "ETH": ["a", "b"] * 30}, index=idx)
try:
    out = beta.estimate_betas(df, benchmark="BTC", window=10, min_obs=5)
    print(f"  unconvertible col: shape={out.shape}")
except Exception as e:
    print(f"  unconvertible col: {type(e).__name__}: {e}")

# What if the fast path raises TypeError? Need a column that breaks rolling.
# Try a column with mixed types that to_numpy(dtype=float) succeeds but rolling fails
df2 = pd.DataFrame({"BTC": mkt, "ETH": [1, 2, 3]}, index=idx[:3])
try:
    out = beta.estimate_betas(df2, benchmark="BTC", window=10, min_obs=5)
    print(f"  short df: shape={out.shape}")
except Exception as e:
    print(f"  short df: {type(e).__name__}: {e}")

# 101-102: alignment except in calculate_beta
print("=== 101-102 ===")
# Need Series alignment to raise. concat/dropna on a subclass.
class BadSeries(pd.Series):
    @property
    def _constructor(self):
        return BadSeries
    def dropna(self):
        raise RuntimeError("bad")
a = BadSeries([1.0, 2.0, 3.0, 4.0], index=[10, 20, 30, 40])
b = pd.Series([2.0, 4.0, 6.0], index=[10, 20, 30])
try:
    r = beta.calculate_beta(a, b)
    print(f"  badseries: -> {r}")
except Exception as e:
    print(f"  badseries: {type(e).__name__}: {e}")

# 130-131: min_obs int() raises
print("=== 130-131 ===")
r = beta.calculate_beta(pd.Series([1.0, 2.0, 3.0]), pd.Series([2.0, 4.0, 6.0]), min_obs="5")
print(f"  min_obs str: -> {r}")

# 124: len(aligned) == 0 -> return nan
print("=== 124 ===")
a = pd.Series([1.0, 2.0], index=[10, 20])
b = pd.Series([3.0, 4.0], index=[30, 40])  # no overlap
try:
    r = beta.calculate_beta(a, b)
    print(f"  no overlap: -> {r}")
except Exception as e:
    print(f"  no overlap: {type(e).__name__}: {e}")

# 188: len(a_m) == 0 after mask
print("=== 188 ===")
r = beta.calculate_beta_fast(np.array([np.nan, np.nan]), np.array([np.nan, np.nan]))
print(f"  all nan: -> {r}")

# 162: a is None after asarray
print("=== 162 ===")
arr = np.asarray(None, dtype=float)
print(f"  asarray(None): {arr!r}, is None: {arr is None}")

# 169-170: np.array(a).ravel() raises
print("=== 169-170 ===")
# After asarray(dtype=float) succeeds, a is ndarray. np.array(ndarray).ravel() ok.
# What if a is a non-array that asarray accepts? E.g. a list -> asarray -> ndarray.
# ravel always ok on ndarray. Dead.
print("  dead: asarray output is always ndarray, ravel ok")

# 215-218: lstsq + outer except
print("=== 215-218 ===")
# lstsq on float ndarray only raises LinAlgError. UFuncTypeError needs object dtype
# which asarray(dtype=float) rejects. So 215-216 dead.
# 217-218: what raises uncaught? After asarray, ndim check, ravel try/except,
# len, mask, std, lstsq try/except. All guarded. Dead.
print("  dead: all ops guarded")