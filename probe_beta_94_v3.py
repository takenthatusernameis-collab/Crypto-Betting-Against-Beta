"""Batch94 probe v3: targeted beta.py paths."""
import numpy as np
import pandas as pd
from strategies.betting_against_beta import beta

# 194-195: min_obs weird types
print("=== 194-195 min_obs weird types ===")
for desc, mo in [("str", "5"), ("list", [5]), ("dict", {1: 2})]:
    r = beta.calculate_beta_fast([1.0, 2.0, 3.0, 4.0], [2.0, 4.0, 6.0, 8.0], min_obs=mo)
    print(f"  {desc}: -> {r}")

# 215-216: lstsq TypeError/ValueError/AttributeError
print("=== 215-216 lstsq non-LinAlgError ===")
# Need a_m/b_m that pass std check but break lstsq
# object dtype after mask? No - mask filters.
# Try a_m with non-finite but std ok? std of inf is inf -> fails 201.
# Try a_m that is a non-array? After mask, a_m is ndarray.
# What if a_m is a pandas Series? Only if input is Series.
# Actually calculate_beta_fast converts to ndarray. So a_m is always ndarray.
# lstsq on ndarray only raises LinAlgError or UFuncTypeError (TypeError subclass)
# UFuncTypeError happens for object dtype - but asarray(dtype=float) already failed.
# So 215-216 may be dead. Let me test directly:
for desc, X, y in [
    ("obj_X", np.array([[1.0, 2.0]], dtype=object), np.array([1.0])),
    ("str_X", np.array([["1.0", "2.0"]]), np.array([1.0])),
]:
    try:
        c, *_ = np.linalg.lstsq(X, y, rcond=None)
        print(f"  {desc}: ok -> {c}")
    except np.linalg.LinAlgError:
        print(f"  {desc}: LinAlgError")
    except (TypeError, ValueError, AttributeError) as e:
        print(f"  {desc}: {type(e).__name__}")
    except Exception as e:
        print(f"  {desc}: {type(e).__name__}")

# 217-218: outer except of calculate_beta_fast
print("=== 217-218 outer except ===")
# What could raise uncaught after asarray succeeds?
# Test with a weird object that asarray accepts but breaks later
class WeirdArray:
    def __init__(self, data): self.data = np.asarray(data, dtype=float)
    def __array__(self, dtype=None): return self.data
    def __len__(self): return len(self.data)
    def __getitem__(self, i): return self.data[i]
    @property
    def ndim(self): return 1
    def __iter__(self): return iter(self.data)
for desc, a, b in [
    ("weird", WeirdArray([1.0, 2.0, 3.0]), WeirdArray([2.0, 4.0, 6.0])),
]:
    try:
        r = beta.calculate_beta_fast(a, b)
        print(f"  {desc}: -> {r}")
    except Exception as e:
        print(f"  {desc}: {type(e).__name__}: {e}")

# 101-102: calculate_beta alignment except
print("=== 101-102 alignment except ===")
# Need Series alignment to raise
class BadSeries(pd.Series):
    @property
    def _constructor(self): return BadSeries
    def dropna(self): raise RuntimeError("bad")
    def concat(self, *a, **k): raise RuntimeError("bad")
try:
    a = BadSeries([1.0, 2.0, 3.0, 4.0], index=[10, 20, 30, 40])
    b = pd.Series([2.0, 4.0, 6.0], index=[10, 20, 30])
    r = beta.calculate_beta(a, b)
    print(f"  badseries: -> {r}")
except Exception as e:
    print(f"  badseries: {type(e).__name__}: {e}")

# 149-150: BABDataError in calculate_beta
print("=== 149-150 BABDataError ===")
# What raises BABDataError inside calculate_beta? Only if x_std check or lstsq raises BABDataError - none.
# So 149-150 is dead unless a custom exception subclass. Skip.

# 124/188: empty after mask
print("=== 124/188 empty after mask ===")
a = np.array([np.nan, np.nan])
b = np.array([np.nan, np.nan])
mask = np.isfinite(a) & np.isfinite(b)
print(f"  all-nan: any(mask)={np.any(mask)}, len(a[mask])={len(a[mask])}")

# 356-359: _finalize_betas 1D branch
print("=== 356-359 _finalize_betas ndim ===")
# Called with beta (n,1) 2D in fast path, or 1D in bad_cols path
# bad_cols path calls _calc_rolling_beta_series which returns 1D, then _finalize_betas(beta_arr) with 1D
# So 356-359 IS reachable via bad_cols! Let me verify.
idx = pd.date_range("2023-01-01", periods=60, freq="D")
rng = np.random.default_rng(5)
mkt = rng.normal(0, 0.01, 60)
# asset with NaN values -> bad_cols
df = pd.DataFrame({"BTC": mkt, "ETH": np.concatenate([mkt[:30], [np.nan]*30])}, index=idx)
out = beta.estimate_betas(df, benchmark="BTC", window=10, min_obs=5)
print(f"  bad_cols path: shape={out.shape}, ETH has NaN: {out['ETH'].isna().any()}")