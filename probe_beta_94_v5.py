"""Probe 101-102, 429-433 precisely."""
import numpy as np
import pandas as pd
from strategies.betting_against_beta import beta

# 101-102: concat/dropna raises TypeError/ValueError/AttributeError
print("=== 101-102 ===")
class VSeries(pd.Series):
    @property
    def _constructor(self):
        return VSeries
    def dropna(self):
        raise ValueError("bad dropna")
a = VSeries([1.0, 2.0, 3.0, 4.0], index=[10, 20, 30, 40])
b = pd.Series([2.0, 4.0, 6.0], index=[10, 20, 30])
try:
    r = beta.calculate_beta(a, b)
    print(f"  VSeries dropna ValueError: -> {r}")
except Exception as e:
    print(f"  VSeries: {type(e).__name__}: {e}")

# 429-433: fast path raises TypeError/ValueError/AttributeError, then fallback fails
print("=== 429-433 ===")
# Need fast path (369-418) to raise TypeError/ValueError/AttributeError.
# What raises? y_df.mul, rolling, arithmetic, _finalize_betas.
# Try a DataFrame where rolling raises.
idx = pd.date_range("2023-01-01", periods=60, freq="D")
rng = np.random.default_rng(5)
mkt = rng.normal(0, 0.01, 60)
# A column that to_numpy(dtype=float) succeeds but breaks rolling
class BreakRolling:
    """Object that to_numpy accepts but rolling breaks."""
    def __init__(self, data): self.data = np.asarray(data, dtype=float)
    def __array__(self, dtype=None): return self.data
    def to_numpy(self, dtype=None, copy=False):
        if dtype is float: return self.data
        return np.asarray(self.data)
    def __len__(self): return len(self.data)
    def __iter__(self): return iter(self.data)
    @property
    def dtype(self): return np.dtype(float)

# Actually let me try a simpler approach: a DataFrame with a column that's a
# non-numeric type that to_numpy(dtype=float) accepts via __array__
df = pd.DataFrame({"BTC": mkt})
df["ETH"] = [BreakRolling([1.0, 2.0])]  # won't work due to length
print("  skip complex")

# Try: what if returns_df[asset] returns something whose .mul raises?
# E.g. a DataFrame subclass
class BadDF(pd.DataFrame):
    @property
    def _constructor(self):
        return BadDF
    def __getitem__(self, key):
        col = super().__getitem__(key)
        if key != "BTC" and hasattr(col, "mul"):
            orig_mul = col.mul
            def raising_mul(*a, **k):
                raise ValueError("bad mul")
            col.mul = raising_mul
        return col
bdf = BadDF({"BTC": mkt, "ETH": mkt.copy()})
try:
    out = beta.estimate_betas(bdf, benchmark="BTC", window=10, min_obs=5)
    print(f"  BadDF: shape={out.shape}")
except Exception as e:
    print(f"  BadDF: {type(e).__name__}: {e}")