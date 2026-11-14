"""Batch 148: 351-352 (`except Exception: pass` after `np.isnan`/`np.isinf`).

Coverage-compatible retry of the Batch 147 runtime lead. A ``float`` subclass
instance whose ``np.isnan``/``np.isinf`` raise a *non-ValueError* (here
``TypeError`` via ``__float__``/``__array__``) satisfies ``isinstance(val,
float)`` at data_loader.py:345, so control enters the 346-352 block. At 347
``np.isnan(val)`` raises ``TypeError``; 349-350 (`except ValueError: raise`)
does not match, so 351-352 (`except Exception: pass`) executes and the
coercion continues to the epoch-float branch (443+) which ultimately raises
``ValueError("bad")`` — semantics preserved (the bad value is still rejected),
but 351-352 is now *executed* and coverage records it.

No ``sys.settrace`` is used in the test body; coverage traces normally.
"""

import numpy as np
import pandas as pd

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.data_loader import (
    _coerce_to_datetime_scalar,
    _normalize_index,
)


class _NonValueErrorFloat(float):
    """float subclass where np.isnan/np.isinf raise TypeError (not ValueError)."""

    def __float__(self):
        raise TypeError("bad float")

    def __array__(self, *args, **kwargs):
        raise TypeError("bad array")


def test_351_352_non_value_error_float_in_coercer():
    # isinstance(val, float) is True, so the 346-352 block is entered.
    v = _NonValueErrorFloat(1.5)
    assert isinstance(v, float)
    # np.isnan raises TypeError (non-ValueError) on this subclass.
    try:
        np.isnan(v)
    except TypeError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected np.isnan to raise TypeError")

    # 351-352 executes: the TypeError is swallowed and coercion continues to
    # the epoch-float branch, which raises ValueError("bad"). The value is
    # still rejected (semantics preserved) but 351-352 is covered.
    try:
        _coerce_to_datetime_scalar(v)
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError from epoch-float branch")


def test_351_352_via_normalize_index_object_index():
    # Object-dtype index carrying the bad float reaches the elementwise
    # coercer inside _normalize_index; 351-352 executes per element and the
    # frame is rejected as unparseable (BABDataError) — semantics preserved.
    idx = pd.Index([_NonValueErrorFloat(1.5)], dtype=object)
    df = pd.DataFrame({"BTC": [0.1]}, index=idx)
    try:
        _normalize_index(df.copy())
    except Exception as exc:
        # Rejection path: the bad float cannot become a datetime.
        assert "datetime" in str(exc).lower()
    else:  # pragma: no cover
        raise AssertionError("expected _normalize_index to reject bad float index")


def test_351_352_via_load_returns_object_index():
    # Public API path: load_returns -> validate_returns_dataframe ->
    # _normalize_index elementwise coercer. 351-352 executes; the frame is
    # rejected (no valid datetime index), preserving production semantics.
    df = pd.DataFrame(
        {"BTC": [0.1, 0.2]},
        index=pd.Index([_NonValueErrorFloat(1.5), _NonValueErrorFloat(1.5)], dtype=object),
    )
    try:
        dl.load_returns(df, benchmark="BTC")
    except Exception as exc:
        assert "datetime" in str(exc).lower()
    else:  # pragma: no cover
        raise AssertionError("expected load_returns to reject bad float index")
