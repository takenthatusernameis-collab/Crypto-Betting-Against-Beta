"""Batch94 probe: empirically test borderline beta.py paths."""
import numpy as np
import pandas as pd
from strategies.betting_against_beta import beta

# 215-216: can np.linalg.lstsq raise TypeError/ValueError/AttributeError?
print("=== lstsq edge cases (215-216) ===")
for desc, X, y in [
    ("nan_in_X", np.array([[1.0, np.nan]]), np.array([1.0])),
    ("inf_in_X", np.array([[1.0, np.inf]]), np.array([1.0])),
    ("empty_y", np.array([[1.0, 2.0]]), np.array([])),
    ("object_dtype", np.array([[1, 2]], dtype=object), np.array([1.0])),
    ("length1", np.array([[1.0, 2.0]]), np.array([1.0])),
]:
    try:
        c, *_ = np.linalg.lstsq(X, y, rcond=None)
        print(f"  {desc}: ok -> {c}")
    except np.linalg.LinAlgError as e:
        print(f"  {desc}: LinAlgError")
    except (TypeError, ValueError, AttributeError) as e:
        print(f"  {desc}: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"  {desc}: {type(e).__name__}: {e}")

# 169-170: can np.array(a).ravel() raise for an ndarray a?
print("=== ravel edge cases (169-170) ===")
for desc, a in [
    ("0d_array", np.asarray(5.0)),
    ("object_array", np.array([object(), object()])),
    ("scalar_in_list", [5.0]),
]:
    try:
        arr = np.asarray(a, dtype=float)
        r = np.array(arr).ravel()
        print(f"  {desc}: ok -> {r}")
    except Exception as e:
        print(f"  {desc}: {type(e).__name__}: {e}")

# 162: after asarray, is a ever None?
print("=== 162 a is None after asarray ===")
for desc, a in [("None", None), ("nan_scalar", np.nan)]:
    arr = np.asarray(a, dtype=float)
    print(f"  {desc}: arr={arr!r}, arr is None: {arr is None}, len={len(arr) if hasattr(arr,'__len__') else 'n/a'}")

# 124/188: empty after mask filter?
print("=== 124/188 empty-after-mask ===")
a = np.array([np.nan, np.nan])
b = np.array([np.nan, np.nan])
mask = np.isfinite(a) & np.isfinite(b)
print(f"  all-nan: any(mask)={np.any(mask)}, len(a[mask])={len(a[mask])}")

# 149-150: can anything inside calculate_beta raise BABDataError?
print("=== 149-150 BABDataError source in calculate_beta ===")
# Try passing a DataFrame column that is a BABDataError-raising subclass? skip - no source.

# 356-359: _finalize_betas 1D branch -- is it ever called with 1D?
print("=== 356-359 _finalize_betas ndim ===")
import inspect
src = inspect.getsource(beta.calculate_rolling_beta)
print("  _finalize_betas called with:", [l.strip() for l in src.splitlines() if "_finalize_betas(" in l])

# 217-218: outer except of calculate_beta_fast
print("=== 217-218 outer except ===")
# What could raise uncaught? Test a weird input.
for desc, a, b in [
    ("dict", {0: 1.0}, [1.0, 2.0]),
    ("none_a", None, [1.0, 2.0]),
]:
    try:
        r = beta.calculate_beta_fast(a, b)
        print(f"  {desc}: -> {r}")
    except Exception as e:
        print(f"  {desc}: {type(e).__name__}: {e}")