"""Coverage campaign 2 for beta.py residual branches.

Targets the reachable miss evidence from HANDOFF.md:
  - line 143: calculate_beta() non-finite OLS slope -> np.nan
  - line 210: calculate_beta_fast() non-finite / non-scalar beta -> np.nan

Structurally unreachable under the current implementation (no semantic
change solely for coverage, per HANDOFF rules): 101-102, 124, 145-146,
149-150, 162, 169-170, 188, 212-218, 356-359 (_finalize_betas 1-D branch
is never reached: calculate_rolling_beta always passes a 2-D beta array),
429-433. These remain documented misses rather than chased with contrived
monkeypatches.
"""

from __future__ import annotations

import numpy as np
import pytest

from strategies.betting_against_beta.beta import BABDataError, calculate_beta, calculate_beta_fast


def test_calculate_beta_nonfinite_slope_returns_nan():
    # Finite benchmark std (passes the zero-variance guard) with extreme
    # asset returns whose OLS slope (-2e308) overflows to -inf; calculate_beta
    # maps the non-finite slope to NaN (line 143).
    beta = calculate_beta([1e308, -1e308], [1.0, 2.0], min_obs=1)
    assert np.isnan(beta)


def test_calculate_beta_none_inputs_raise_bab_data_error():
    """BABDataError propagates (line 149-150 re-raise path is documentation only)."""
    with pytest.raises(BABDataError):
        calculate_beta(None, [1.0, 2.0, 3.0])


def test_calculate_beta_fast_nonfinite_slope_returns_nan():
    """Non-finite beta from calculate_beta_fast -> np.nan (line 210)."""
    beta = calculate_beta_fast([1e308, -1e308], [1.0, 2.0], min_obs=1)
    assert np.isnan(beta)


def test_calculate_beta_fast_constant_benchmark_returns_nan():
    """Zero-variance benchmark guard returns NaN, never a synthetic 0.0."""
    beta = calculate_beta_fast([1.0, 2.0, 3.0], [1.0, 1.0, 1.0])
    assert np.isnan(beta)
