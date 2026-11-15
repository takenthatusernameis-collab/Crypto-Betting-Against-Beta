"""P16-2 (D3) regression: BABDataError must propagate from beta.calculate_beta.

Contract:
  - BABDataError subclasses ValueError (data_loader.py:21), so the broad
    ``except (TypeError, ValueError, AttributeError): return np.nan`` handler at
    beta.py:148-149 would swallow a genuine data error and turn it into a silent
    NaN / "no signal". BABDataError must be re-raised first.
  - A reachable __array__-raising object passed as either asset_returns or
    benchmark_returns must propagate BABDataError rather than return NaN.
"""

import numpy as np
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.data_loader import BABDataError


class _BABDataErrorArray:
    """Object whose __array__ raises BABDataError, reaching the guarded
    np.asarray(..., dtype=float) conversion inside calculate_beta."""

    def __array__(self, dtype=None):
        raise BABDataError("injected data error via __array__")


def _valid_benchmark():
    return np.array([0.01, -0.02, 0.03, -0.01, 0.02])


def test_calculate_beta_asset_arg_babdataerror_propagates():
    with pytest.raises(BABDataError, match="injected data error via __array__"):
        beta.calculate_beta(_BABDataErrorArray(), _valid_benchmark())


def test_calculate_beta_benchmark_arg_babdataerror_propagates():
    with pytest.raises(BABDataError, match="injected data error via __array__"):
        beta.calculate_beta(np.array([0.01, -0.02, 0.03]), _BABDataErrorArray())


def test_calculate_beta_none_still_raises_babdataerror():
    # The pre-try None guard must keep raising BABDataError (regression guard).
    with pytest.raises(BABDataError, match="must not be None"):
        beta.calculate_beta(None, _valid_benchmark())
    with pytest.raises(BABDataError, match="must not be None"):
        beta.calculate_beta(_valid_benchmark(), None)


def test_calculate_beta_plain_value_error_still_nan():
    # Non-BABDataError ValueError (and TypeError/AttributeError) still coerce
    # to NaN: only BABDataError is promoted to a propagated error.
    class _PlainValue:
        def __array__(self, dtype=None):
            raise ValueError("plain value error, not a data error")

    assert np.isnan(beta.calculate_beta(_PlainValue(), _valid_benchmark()))
    assert np.isnan(beta.calculate_beta(_valid_benchmark(), _PlainValue()))
