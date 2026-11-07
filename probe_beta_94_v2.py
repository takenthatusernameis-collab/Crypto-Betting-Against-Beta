"""Batch94 probe v2: find reachable paths in beta.py."""
import numpy as np
import pandas as pd
from strategies.betting_against_beta import beta

# Test calculate_beta_fast with inputs that pass asarray but break later
print("=== calculate_beta_fast edge battery ===")
tests = [
    ("0d_scalar", 5.0, 2.0),
    ("list_int", [1, 2, 3], [4, 5, 6]),
    ("mixed_str", ["1.0", "2.0"], ["3.0", "4.0"]),
    ("pandas_series", pd.Series([1.0, 2.0, 3.0]), pd.Series([4.0, 5.0, 6.0])),
    ("ndarray_obj", np.array([1.0, 2.0], dtype=object), np.array([3.0, 4.0], dtype=object)),
    ("2d_array", np.array([[1.0, 2.0]]), np.array([[3.0, 4.0]])),
    ("string_array", np.array(["a", "b"]), np.array(["c", "d"])),
    ("none", None, [1.0, 2.0]),
    ("min_obs_str", [1.0, 2.0, 3.0], [4.0, 5.0, 6.0]),
]
for desc, a, b in tests:
    try:
        r = beta.calculate_beta_fast(a, b, min_obs=2)
        print(f"  {desc}: -> {r}")
    except Exception as e:
        print(f"  {desc}: {type(e).__name__}: {e}")

# Test with min_obs as weird type to hit 194-195
print("=== min_obs weird types (194-195) ===")
for desc, mo in [("str", "5"), ("list", [5]), ("none", None), ("float", 5.0)]:
    try:
        r = beta.calculate_beta_fast([1.0, 2.0, 3.0, 4.0], [2.0, 4.0, 6.0, 8.0], min_obs=mo)
        print(f"  {desc} min_obs={mo!r}: -> {r}")
    except Exception as e:
        print(f"  {desc} min_obs={mo!r}: {type(e).__name__}: {e}")

# Test calculate_beta with pandas Series of different lengths (84-102 path)
print("=== calculate_beta alignment (84-102) ===")
a_s = pd.Series([1.0, 2.0, 3.0, 4.0], index=[10, 20, 30, 40])
b_s = pd.Series([2.0, 4.0, 6.0], index=[10, 20, 30])
try:
    r = beta.calculate_beta(a_s, b_s)
    print(f"  aligned series: -> {r}")
except Exception as e:
    print(f"  aligned series: {type(e).__name__}: {e}")

# Test calculate_beta with object-dtype Series
print("=== calculate_beta object series ===")
a_obj = pd.Series([1.0, 2.0, 3.0], dtype=object)
b_obj = pd.Series([2.0, 4.0, 6.0], dtype=object)
try:
    r = beta.calculate_beta(a_obj, b_obj)
    print(f"  object series: -> {r}")
except Exception as e:
    print(f"  object series: {type(e).__name__}: {e}")

# Test rolling_beta with non-array inputs (37-67 path)
print("=== rolling_beta generic (37-67) ===")
for desc, a, b in [
    ("lists", [1.0, 2.0, 3.0, 4.0, 5.0], [2.0, 4.0, 6.0, 8.0, 10.0]),
    ("ndarray_obj", np.array([1.0, 2.0], dtype=object), np.array([2.0, 4.0], dtype=object)),
    ("mixed_len", [1.0, 2.0, 3.0], [4.0, 5.0]),
    ("none", None, [1.0, 2.0]),
    ("scalar", 5.0, 2.0),
]:
    try:
        r = beta.rolling_beta(a, b, window=2, min_obs=1)
        print(f"  {desc}: -> {r}")
    except Exception as e:
        print(f"  {desc}: {type(e).__name__}: {e}")