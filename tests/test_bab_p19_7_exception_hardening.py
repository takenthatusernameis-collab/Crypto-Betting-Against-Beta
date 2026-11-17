"""P19-7 Milestone 1: data_sources.py exception-handling hardening (sites 10-12).

Class A (10, 11): surfacing contracts — BABDataError raised with chained cause.
Class B (12): the silent ``except Exception: idx_utc = idx`` fallback was
unreachable for any valid DatetimeIndex (UTC convert/localize cannot raise);
the except is removed so any unexpected tz failure now propagates. Regression
tests pin identical happy-path behavior and prove surfacing via monkeypatch.
"""

from __future__ import annotations

from zoneinfo import ZoneInfoNotFoundError

import pandas as pd
import pytest

from strategies.betting_against_beta.data_sources import BABDataError, validate_freshness


def _fresh_df(index):
    return pd.DataFrame({"BTC": [0.01, -0.005, 0.002]}, index=index)


# ---------------------------------------------------------------------------
# Site 10 — data_sources.py:376  (ticker fetch failure surfaces, Class A)
# ---------------------------------------------------------------------------


def test_ticker_fetch_failure_surfaces_babdataerror(monkeypatch):
    # The fetch_ticker try/except re-raises as BABDataError chained from the
    # original exception; the original message is preserved in the surfaced
    # error. Prove the chain + message via the public CCXTFeed.fetch_latest
    # path with a stubbed exchange.
    from strategies.betting_against_beta.data_sources import CCXTFeed

    class StubExchange:
        def fetch_ticker(self, symbol):
            raise RuntimeError("exchange down")

    class StubFeed(CCXTFeed):
        def __init__(self):
            self._exchange = StubExchange()
            self._error = None
            self.symbols = ["BTC"]
            self.dry_run = False
            self.max_staleness_seconds = 30.0
            self.max_gap_seconds = 60.0
            self._connected = True
            self._markets_loaded = True
            self._last_tick_data = {}
            self._last_tick_time = {}

        def _to_ccxt_symbol(self, symbol):
            return f"{symbol}/USDT"

    feed = StubFeed()
    with pytest.raises(BABDataError) as exc_info:
        feed.fetch_latest()
    assert "exchange down" in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, RuntimeError)
    assert feed._error == "exchange down"


# ---------------------------------------------------------------------------
# Site 11 — data_sources.py:478  (unparseable index surfaces, Class A)
# ---------------------------------------------------------------------------


def test_unparseable_object_index_surfaces_babdataerror():
    # An object index whose values cannot be coerced to datetime raises
    # BABDataError (surfacing), not a swallowed pandas error.
    df = _fresh_df(pd.Index(["abc", "def", "ghi"]))
    with pytest.raises(BABDataError, match="Index cannot be parsed as datetime"):
        validate_freshness(
            df,
            max_staleness_days=5.0,
            max_gap_days=2.0,
            reference_date=df.index[-1],
        )


# ---------------------------------------------------------------------------
# Site 12 — data_sources.py:506  (silent tz fallback removed, Class B)
# ---------------------------------------------------------------------------


def test_tz_aware_index_happy_path_unchanged():
    # tz_convert("UTC") path — identical happy-path behavior preserved.
    idx = pd.DatetimeIndex(
        ["2024-01-01", "2024-01-02", "2024-01-03"], tz="US/Eastern"
    )
    df = _fresh_df(idx)
    assert (
        validate_freshness(
            df,
            max_staleness_days=5.0,
            max_gap_days=2.0,
            reference_date=idx[-1],
        )
        is True
    )


def test_naive_index_happy_path_unchanged():
    # tz_localize("UTC") path — identical happy-path behavior preserved.
    idx = pd.DatetimeIndex(["2024-01-01", "2024-01-02", "2024-01-03"])
    df = _fresh_df(idx)
    assert (
        validate_freshness(
            df,
            max_staleness_days=5.0,
            max_gap_days=2.0,
            reference_date=idx[-1],
        )
        is True
    )


def test_tz_failure_surfaces_instead_of_silent_fallback(monkeypatch):
    # Class B surfacing proof: monkeypatch tz_convert to raise and assert the
    # underlying exception propagates (the old silent ``idx_utc = idx`` fallback
    # is gone). The index is otherwise a valid DatetimeIndex.
    idx = pd.DatetimeIndex(
        ["2024-01-01", "2024-01-02", "2024-01-03"], tz="US/Eastern"
    )
    df = _fresh_df(idx)

    def boom(self, tz):
        raise ZoneInfoNotFoundError("monkeypatched tz failure")

    monkeypatch.setattr(pd.DatetimeIndex, "tz_convert", boom)
    with pytest.raises(ZoneInfoNotFoundError, match="monkeypatched tz failure"):
        validate_freshness(
            df,
            max_staleness_days=5.0,
            max_gap_days=2.0,
            reference_date=idx[-1],
        )
