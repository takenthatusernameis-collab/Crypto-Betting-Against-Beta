"""Final probe 2: hit the two remaining quality.py branches (132, 259)."""
from __future__ import annotations

import pandas as pd

from strategies.betting_against_beta import quality


def test_detect_gaps_all_nat_index_hits_isna_branch():
    # Line 132: median_gap is NaT -> pd.isna(median_gap) is True -> early return.
    # An all-NaT DatetimeIndex yields a NaT median from the diff() series.
    idx = pd.DatetimeIndex([pd.NaT, pd.NaT, pd.NaT])
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=idx)
    res = quality.detect_gaps(df)
    assert res == {"gaps": [], "count": 0}


def test_detect_duplicate_timestamps_index_without_has_duplicates_attr():
    # Line 259: final return path when df.index lacks has_duplicates.
    # Patch pd.Index.has_duplicates to raise AttributeError so hasattr() returns
    # False, exercising the outer fallback return. Restored afterwards.
    saved = pd.Index.has_duplicates
    class _MissingAttr:
        def __get__(self, obj, objtype=None):
            raise AttributeError("has_duplicates removed for test")
    pd.Index.has_duplicates = _MissingAttr()  # type: ignore[assignment]
    try:
        df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]})
        df.index = pd.Index([0, 1, 2])
        res = quality.detect_duplicate_timestamps(df)
        assert res == {"has_duplicates": False, "count": 0}
    finally:
        pd.Index.has_duplicates = saved  # type: ignore[assignment]