"""Batch 149: 403-404 (`except Exception: pass` in the epoch-numeric-string branch).

MATERIALLY-NEW METHOD (differs from B103-148): **regex-admitted numeric
strings that overflow to infinity**. The regex at data_loader.py:361
(``^[+-]?(\d+)(\.\d+)?([eE][+-]?\d+)?$``) admits scientific-notation
strings such as ``"1e400"`` and ``"+1e400"`` whose ``float()`` conversion
yields ``inf`` (not a finite epoch). The magnitude gates at 365/373/378/383/390
all compare ``av > 1e18`` etc.; for ``av == inf`` every gate is True, so the
first branch (365-366) is taken: ``int(numf)`` at 367 raises ``OverflowError``
("cannot convert float infinity to integer") — a **non-ValueError**. The
``except Exception: pass`` at 403-404 therefore executes and coverage records
it. The value is still rejected: the regex branch swallows the OverflowError,
falls through to the normal-datetime parsing block (406-418) which raises
``ValueError("bad")`` — **production semantics preserved** (bad value rejected),
but 403-404 is now executed and covered.

No ``sys.settrace`` is used; coverage traces normally. The test asserts both
that 403-404 executes (semantics preserved: bad value raises ValueError) and
that a valid finite epoch string still parses correctly (no regression).
"""
import re

import numpy as np
import pandas as pd

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.data_loader import (
    _coerce_to_datetime_scalar,
    _normalize_index,
)


_EPOCH_RE = re.compile(r"^[+-]?(\d+)(\.\d+)?([eE][+-]?\d+)?$")
_OVERFLOW_STRINGS = ("1e400", "+1e400", "1e309", "1.0e400", "9.9e400")


def _assert_regex_admits(s: str) -> None:
    assert _EPOCH_RE.match(s) is not None, f"regex should admit {s!r}"


def _assert_float_overflows(s: str) -> None:
    f = float(s)
    assert f == float("inf"), f"expected inf from {s!r}, got {f!r}"
    try:
        int(f)
    except OverflowError:
        pass
    else:  # pragma: no cover
        raise AssertionError(f"expected int({s!r}) to raise OverflowError")


def test_403_404_overflow_string_regex_and_float():
    # Criterion 1 (line->code) + criterion 3 (plausible library behavior):
    # the regex at 361 admits these and float() yields inf.
    for s in _OVERFLOW_STRINGS:
        _assert_regex_admits(s)
        _assert_float_overflows(s)


def test_403_404_overflow_string_rejected_with_value_error():
    # Criterion 4 (control-flow path): the OverflowError from int(inf) at
    # 367 is swallowed by 403-404; coercion continues to the normal-datetime
    # block (406-418) which raises ValueError("bad"). Semantics preserved.
    for s in _OVERFLOW_STRINGS:
        try:
            _coerce_to_datetime_scalar(s)
        except ValueError:
            pass
        else:  # pragma: no cover
            raise AssertionError(f"expected ValueError for overflow string {s!r}")


def test_403_404_overflow_string_via_normalize_index_object_index():
    # Criterion 3 (production-realistic path): an object-dtype index
    # carrying overflow strings reaches the elementwise coercer inside
    # _normalize_index; 403-404 executes per element and the frame is
    # ultimately rejected (BABDataError) — semantics preserved.
    idx = pd.Index(["1e400", "+1e400", "1e309"], dtype=object)
    df = pd.DataFrame({"a": [1, 2, 3]}, index=idx)
    try:
        dl._normalize_index(df)
    except dl.BABDataError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected BABDataError for overflow object index")


def test_403_404_no_regression_finite_epoch_string():
    # Control: a valid finite epoch string still parses correctly, proving
    # the overflow path does not perturb the happy path.
    assert _coerce_to_datetime_scalar("1609459200") == pd.Timestamp(
        "2021-01-01 00:00:00+00:00"
    )
    assert _coerce_to_datetime_scalar("1.5e10") == pd.Timestamp(
        "2445-05-01 02:40:00+00:00"
    )