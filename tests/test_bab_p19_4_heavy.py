"""P19-4 heavy-work: prove the reachable per-column quality branches.

These lines live in ``data_loader._run_data_quality_campaign``'s per-column
fallback. The public ``validate_returns_dataframe`` path always coerces the
frame to numeric before the campaign, so the vectorized fast path handles it;
the per-column branch is only exercised when the campaign receives a frame
that still contains a non-numeric column (defensive / direct-call path). We
drive that branch with realistic contaminated frames and assert the
safety-relevant outcome (a ``BABDataError`` naming the offending column).
"""

from __future__ import annotations

import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import _run_data_quality_campaign
from strategies.betting_against_beta.errors import BABDataError


def _dates(periods: int) -> pd.DatetimeIndex:
    return pd.date_range("2024-01-01", periods=periods, freq="D")


def test_quality_per_column_insufficient_finite_fraction():
    """A non-numeric junk column coerces to all-NaN; min_finite_fraction rejects it."""
    df = pd.DataFrame(
        {"BTC": [0.01, 0.02, 0.03, 0.04], "JUNK": ["n/a", "n/a", "n/a", "n/a"]},
        index=_dates(4),
    )
    with pytest.raises(BABDataError, match="insufficient finite data"):
        _run_data_quality_campaign(df, min_finite_fraction=0.5)


def test_quality_per_column_stale_frozen_run():
    """A frozen run of equal finite values is rejected in the per-column branch."""
    df = pd.DataFrame(
        {"BTC": [0.10, 0.10, 0.10, 0.20], "JUNK": ["a", "b", "c", "d"]},
        index=_dates(4),
    )
    with pytest.raises(BABDataError, match="Stale/frozen data detected"):
        _run_data_quality_campaign(df, stale_run_threshold=3, min_finite_fraction=0.0)


def test_quality_per_column_clean_contamination_passes():
    """A non-numeric junk column with finite data and no frozen run passes cleanly."""
    df = pd.DataFrame(
        {"BTC": [0.01, 0.02, 0.03, 0.04], "JUNK": ["a", "b", "c", "d"]},
        index=_dates(4),
    )
    out = _run_data_quality_campaign(df, min_finite_fraction=0.0, stale_run_threshold=0)
    assert list(out.columns) == ["BTC", "JUNK"]
    assert len(out) == 4
