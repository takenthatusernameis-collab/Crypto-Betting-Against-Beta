"""P11 coverage campaign for `data_sources.py` real reachable branches.

Targets the statements still missed after the existing data_sources /
realtime_feed suites: base RealtimeFeed connect/disconnect/fetch_latest,
health_check with populated ticks, to_returns_df empty input, CCXTFeed
_get_ccxt ImportError, non-dry-run connect/fetch paths, WebSocketFeed
abstract/concrete edges, and validate_freshness bad reference_date.

All doubles are fakes/mocks only: no real network, no credentials, no live
execution enabled. Public API stays explicit opt-in; deterministic-offline
default unchanged.
"""

from __future__ import annotations

import time
import types

import pandas as pd
import pytest

from strategies.betting_against_beta.data_sources import (
    BABDataError,
    CCXTFeed,
    RealtimeFeed,
    WebSocketFeed,
    validate_freshness,
)


class _ConcreteWebSocket(WebSocketFeed):
    """Minimal concrete WebSocketFeed for edge-branch coverage."""

    def _connect_ws(self) -> None:
        self._ws = object()

    def _disconnect_ws(self) -> None:
        self._ws = None

    def _on_message(self, message: dict) -> None:
        return None


def test_realtime_feed_base_connect_disconnect():
    # data_sources.py:162-169 base connect/disconnect bodies.
    feed = RealtimeFeed(symbols=["BTC"])
    assert feed.is_connected() is False
    feed.connect()
    assert feed.is_connected() is True
    assert feed._error is None
    feed.disconnect()
    assert feed.is_connected() is False


def test_realtime_feed_base_fetch_latest_cached():
    # data_sources.py:171-173 base fetch_latest returns cached (empty).
    feed = RealtimeFeed(symbols=["BTC"])
    feed.connect()
    assert feed.fetch_latest() == {}
    feed.disconnect()


def test_realtime_feed_health_check_with_ticks():
    # data_sources.py:229-237 health_check _last_tick_time populated branch.
    feed = RealtimeFeed(symbols=["BTC"], max_staleness_seconds=60.0)
    now = time.time()
    data = {"BTC": {"price": 50000.0, "timestamp": now, "volume": 100.0}}
    feed.validate_freshness(data, now=now)
    health = feed.health_check()
    assert health.connected is False
    assert health.last_tick is not None
    assert health.staleness_seconds is not None
    assert health.symbols == ["BTC"]


def test_to_returns_df_empty_input():
    # data_sources.py:259-260 to_returns_df early return on no rows.
    feed = RealtimeFeed(symbols=["BTC"])
    assert feed.to_returns_df({}).empty


def test_ccxt_get_ccxt_import_error(monkeypatch):
    # data_sources.py:302-306 _get_ccxt ImportError path.
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "ccxt":
            raise ImportError("no ccxt")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    feed = CCXTFeed(symbols=["BTC"], dry_run=True)
    with pytest.raises(RuntimeError, match="ccxt is required"):
        feed.connect()


def test_ccxt_connect_non_dry_run_loads_markets(monkeypatch):
    # data_sources.py:328-330 non-dry-run connect load_markets branch.
    fake_ccxt = types.ModuleType("ccxt")

    class FakeExchange:
        def __init__(self, config):
            self.config = config

        def load_markets(self):
            self.markets_loaded = True

    fake_ccxt.binance = FakeExchange
    monkeypatch.setitem(__import__("sys").modules, "ccxt", fake_ccxt)
    feed = CCXTFeed(symbols=["BTC"], exchange="binance", dry_run=False)
    feed.connect()
    assert feed._markets_loaded is True
    assert feed.is_connected() is True
    feed.disconnect()


def test_ccxt_fetch_latest_not_connected():
    # data_sources.py:346-347 fetch_latest guard.
    feed = CCXTFeed(symbols=["BTC"], dry_run=True)
    with pytest.raises(RuntimeError, match="not connected"):
        feed.fetch_latest()


def test_ccxt_fetch_latest_non_dry_run(monkeypatch):
    # data_sources.py:366-377 non-dry-run ticker fetch + error wiring.
    fake_ccxt = types.ModuleType("ccxt")

    class FakeExchange:
        def __init__(self, config):
            self.config = config

        def load_markets(self):
            pass

        def fetch_ticker(self, symbol):
            now_ms = time.time() * 1000
            return {
                "last": 50000.0,
                "timestamp": now_ms,
                "baseVolume": 100.0,
                "bid": 49995.0,
                "ask": 50005.0,
            }

    fake_ccxt.binance = FakeExchange
    monkeypatch.setitem(__import__("sys").modules, "ccxt", fake_ccxt)
    feed = CCXTFeed(
        symbols=["BTC"],
        exchange="binance",
        dry_run=False,
        max_staleness_seconds=60.0,
    )
    feed.connect()
    data = feed.fetch_latest()
    assert "BTC" in data
    assert data["BTC"]["price"] == 50000.0
    feed.disconnect()


def test_ccxt_to_ccxt_symbol():
    # data_sources.py:382-384 _to_ccxt_symbol.
    feed = CCXTFeed(symbols=["btc"], dry_run=True)
    assert feed._to_ccxt_symbol("btc") == "BTC/USDT"


def test_websocket_feed_connect_disconnect():
    # data_sources.py:420-434 WebSocketFeed connect/disconnect bodies.
    feed = _ConcreteWebSocket(symbols=["BTC"], url="wss://example")
    feed.connect()
    assert feed.is_connected() is True
    assert feed._running is True
    feed.disconnect()
    assert feed.is_connected() is False
    assert feed._running is False


def test_websocket_feed_fetch_latest_not_connected():
    # data_sources.py:438-439 fetch_latest not connected.
    feed = _ConcreteWebSocket(symbols=["BTC"], url="wss://example")
    with pytest.raises(RuntimeError, match="not connected"):
        feed.fetch_latest()


def test_websocket_feed_fetch_latest_no_ticks():
    # data_sources.py:441-442 no tick data received yet.
    feed = _ConcreteWebSocket(symbols=["BTC"], url="wss://example")
    feed.connect()
    with pytest.raises(BABDataError, match="No tick data received yet"):
        feed.fetch_latest()
    feed.disconnect()


def test_websocket_feed_fetch_latest_with_ticks():
    # data_sources.py:444-447 cached path + validate_freshness.
    feed = _ConcreteWebSocket(symbols=["BTC"], url="wss://example")
    feed.connect()
    now = time.time()
    feed._last_tick_data = {
        "BTC": {"price": 50000.0, "timestamp": now, "volume": 100.0}
    }
    data = feed.fetch_latest()
    assert "BTC" in data
    feed.disconnect()


def test_validate_freshness_bad_reference_date():
    # data_sources.py:488-490 unparseable reference_date.
    returns_df = pd.DataFrame(
        {"BTC": [0.01]},
        index=pd.DatetimeIndex(["2024-01-01"], tz="UTC"),
    )
    with pytest.raises(BABDataError, match="cannot be parsed as datetime"):
        validate_freshness(returns_df, reference_date="not-a-date")


def test_validate_freshness_reference_date_naive_localized():
    # data_sources.py:496-497 naive reference tz_localize UTC branch.
    returns_df = pd.DataFrame(
        {"BTC": [0.01, -0.005]},
        index=pd.DatetimeIndex(["2024-01-01", "2024-01-02"]),
    )
    validate_freshness(
        returns_df,
        max_staleness_days=1000.0,
        max_gap_days=10.0,
        reference_date=pd.Timestamp("2024-01-02"),
    )
