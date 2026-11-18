"""P19-7: data_sources.py broad-except hardening (sites @380,482).

Class B (surfacing): ticker fetch failures and unparseable datetime indexes must
raise BABDataError (chained) with stable messages; no silent fallback.
"""

from __future__ import annotations

import pandas as pd
import pytest

from strategies.betting_against_beta.data_sources import BABDataError, CCXTFeed, validate_freshness


def test_data_sources_site380_class_b_ticker_fetch_failure_surfaces():
    """Site 380: fetch_ticker exception -> BABDataError chained, error recorded."""
    feed = CCXTFeed(symbols=["BTC"], exchange="binance", dry_run=False)
    feed._connected = True

    class BoomExchange:
        def fetch_ticker(self, symbol):
            raise RuntimeError("ticker boom")

    feed._exchange = BoomExchange()
    with pytest.raises(BABDataError, match="Failed to fetch ticker for BTC") as excinfo:
        feed.fetch_latest()
    assert feed._error == "ticker boom"
    assert isinstance(excinfo.value.__cause__, RuntimeError)


def test_data_sources_site482_class_b_unparseable_index_surfaces():
    """Site 482: non-numeric, non-datetime index that cannot be parsed -> BABDataError."""
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["not-a-date", "still-bad"])
    with pytest.raises(BABDataError, match="Index cannot be parsed as datetime") as excinfo:
        validate_freshness(df)
    # Cause chaining added by P19-7 Class B hardening.
    assert excinfo.value.__cause__ is not None


def test_data_sources_validate_freshness_happy_path_unchanged():
    idx = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"], utc=True)
    df = pd.DataFrame({"BTC": [0.01, -0.02, 0.03]}, index=idx)
    assert validate_freshness(df, reference_date="2024-01-04") is True
