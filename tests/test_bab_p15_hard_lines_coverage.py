"""P15: hard-line coverage triage (metrics / turnover-NaN, data_sources / tz path).

Confirmed coverable targets. Dead/unreachable residue (replay resize,
signals object-dtype, data_sources to_datetime/tz fallback, reconciliation
empty-columns early-return) is deliberately not forced here; P15 triage
classifies each of the 99 remaining misses as coverable vs dead and the
TOTAL floor governs.

Fakes/monkeypatches only — no network, no credentials, no live execution.
"""

from __future__ import annotations

import pandas as pd
import pytest

from strategies.betting_against_beta.data_sources import validate_freshness
from strategies.betting_against_beta.metrics import turnover


def test_metrics_turnover_all_nan_changes_returns_zero():
    # single row -> diff all NaN -> dropna empty -> mean NaN -> return 0.0
    assert turnover(pd.DataFrame({"A": [0.1]})) == 0.0


def test_data_sources_tz_aware_reference_converts():
    idx = pd.date_range("2026-11-15", periods=3, freq="D", tz="UTC")
    df = pd.DataFrame({"A": [1.0, 1.0, 1.0]}, index=idx)
    ref = pd.Timestamp("2026-11-20", tz="UTC")
    assert validate_freshness(df, reference_date=ref, max_staleness_days=100000.0) is True


def test_data_sources_stale_raises():
    idx = pd.date_range("2020-01-01", periods=3, freq="D")
    df = pd.DataFrame({"A": [1.0, 1.0, 1.0]}, index=idx)
    with pytest.raises(Exception):
        validate_freshness(df, max_staleness_days=0.0)
