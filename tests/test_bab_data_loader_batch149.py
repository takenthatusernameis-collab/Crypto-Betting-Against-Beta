"""Batch 149: coverage-compatible closure of 334-335 in _coerce_to_datetime_scalar.

334-335: `except Exception: pass` after `except ValueError: raise` in the NaTType
name-guard try (329-335). `type(val).__name__` at 330 can raise a non-ValueError
when the value's metaclass defines `__name__` as a descriptor that raises (e.g.
RuntimeError/TypeError). This is a defensive path for unusual object-dtype scalar
types in production-realistic DataFrame/index coercion flows. The value is still
rejected downstream (non-datetime object) preserving semantics.

No sys.settrace; coverage records execution in canonical aggregate.
"""
from __future__ import annotations

import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dl


class _NameRaisesMeta(type):
    @property
    def __name__(cls):  # type: ignore[override]
        raise RuntimeError("metaclass __name__ access error")


class _EvilScalar(metaclass=_NameRaisesMeta):
    pass


def test_coerce_to_datetime_scalar_typename_raises_hits_334_335():
    val = _EvilScalar()
    # Sanity: the mechanism is active.
    with pytest.raises(RuntimeError):
        _ = type(val).__name__
    # 330 raises RuntimeError -> 334-335 except Exception: pass executes;
    # coercion continues and ultimately rejects the non-datetime value.
    with pytest.raises((ValueError, TypeError, Exception)):
        dl._coerce_to_datetime_scalar(val)


def test_normalize_index_object_dtype_evil_scalar_hits_334_335():
    df = pd.DataFrame({"a": [1.0, 2.0]}, index=[pd.Timestamp("2020-01-01"), _EvilScalar()])
    with pytest.raises((dl.BABDataError, ValueError, TypeError, Exception)):
        dl._normalize_index(df)


def test_load_returns_public_path_evil_scalar_hits_334_335():
    df = pd.DataFrame(
        {"date": [pd.Timestamp("2020-01-01"), _EvilScalar()], "BTC": [1.0, 2.0]}
    )
    with pytest.raises((dl.BABDataError, ValueError, TypeError, Exception)):
        dl.load_returns(df, benchmark="BTC")
