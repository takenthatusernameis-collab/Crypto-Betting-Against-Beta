"""Tests for RealtimeFeed, CCXTFeed, and SLA enforcement (P9)."""

from __future__ import annotations

import time

import pandas as pd
import pytest

from strategies.betting_against_beta.data_sources import (
    BABDataError,
    CCXTFeed,
    FeedHealth,
    RealtimeFeed,
    validate_freshness,
)


class TestFeedHealth:
    """Tests for FeedHealth dataclass."""

    def test_feed_health_creation(self):
        health = FeedHealth(
            connected=True,
            last_tick="2024-01-01T00:00:00Z",
            staleness_seconds=5.0,
            gap_seconds=1.0,
            symbols=["BTC", "ETH"],
        )
        assert health.connected is True
        assert health.last_tick == "2024-01-01T00:00:00Z"
        assert health.staleness_seconds == 5.0

    def test_feed_health_to_dict(self):
        health = FeedHealth(
            connected=False,
            error="Connection failed",
            symbols=["BTC"],
        )
        d = health.to_dict()
        assert d["connected"] is False
        assert d["error"] == "Connection failed"
        assert d["symbols"] == ["BTC"]


class TestRealtimeFeedBase:
    """Tests for RealtimeFeed abstract base class behavior."""

    def test_feed_creation(self):
        feed = RealtimeFeed(
            symbols=["BTC", "ETH"],
            max_staleness_seconds=30.0,
            max_gap_seconds=60.0,
        )
        assert feed.symbols == ["BTC", "ETH"]
        assert feed.max_staleness_seconds == 30.0
        assert feed.max_gap_seconds == 60.0
        assert feed.is_connected() is False

    def test_symbol_normalization(self):
        feed = RealtimeFeed(symbols=["btc", "eth", "Sol"])
        assert feed.symbols == ["BTC", "ETH", "SOL"]

    def test_validate_freshness_success(self):
        feed = RealtimeFeed(symbols=["BTC", "ETH"], max_staleness_seconds=60.0)
        import time
        now = time.time()
        data = {
            "BTC": {"price": 50000.0, "timestamp": now, "volume": 100.0},
            "ETH": {"price": 3000.0, "timestamp": now, "volume": 500.0},
        }
        assert feed.validate_freshness(data) is True

    def test_validate_freshness_missing_symbol(self):
        feed = RealtimeFeed(symbols=["BTC", "ETH"], max_staleness_seconds=60.0)
        import time
        now = time.time()
        data = {
            "BTC": {"price": 50000.0, "timestamp": now, "volume": 100.0},
            # ETH missing
        }
        with pytest.raises(BABDataError, match="Missing data for required symbol: ETH"):
            feed.validate_freshness(data)

    def test_validate_freshness_staleness_violation(self):
        feed = RealtimeFeed(symbols=["BTC"], max_staleness_seconds=10.0)
        import time
        old_time = time.time() - 20.0  # 20 seconds ago
        data = {
            "BTC": {"price": 50000.0, "timestamp": old_time, "volume": 100.0},
        }
        with pytest.raises(BABDataError, match="Staleness SLA violation"):
            feed.validate_freshness(data)

    def test_validate_freshness_gap_violation(self):
        feed = RealtimeFeed(symbols=["BTC"], max_gap_seconds=10.0)
        import time
        now = time.time()
        # First call to set last tick time
        data1 = {"BTC": {"price": 50000.0, "timestamp": now - 20.0, "volume": 100.0}}
        feed.validate_freshness(data1)
        # Second call with large gap
        data2 = {"BTC": {"price": 50100.0, "timestamp": now, "volume": 100.0}}
        with pytest.raises(BABDataError, match="Gap SLA violation"):
            feed.validate_freshness(data2)

    def test_validate_freshness_missing_timestamp(self):
        feed = RealtimeFeed(symbols=["BTC"])
        data = {"BTC": {"price": 50000.0, "volume": 100.0}}  # No timestamp
        with pytest.raises(BABDataError, match="Missing timestamp"):
            feed.validate_freshness(data)

    def test_health_check_disconnected(self):
        feed = RealtimeFeed(symbols=["BTC", "ETH"])
        health = feed.health_check()
        assert health.connected is False
        assert health.last_tick is None
        assert health.symbols == ["BTC", "ETH"]

    def test_to_returns_df(self):
        feed = RealtimeFeed(symbols=["BTC", "ETH"])
        import time
        now = time.time()
        data = {
            "BTC": {"price": 50000.0, "timestamp": now, "volume": 100.0},
            "ETH": {"price": 3000.0, "timestamp": now, "volume": 500.0},
        }
        returns_df = feed.to_returns_df(data)
        # With single tick, pct_change will be NaN, so dropna returns empty
        assert isinstance(returns_df, pd.DataFrame)


class TestCCXTFeed:
    """Tests for CCXTFeed (dry-run mode)."""

    def test_ccxt_feed_creation(self):
        feed = CCXTFeed(
            symbols=["BTC", "ETH"],
            exchange="binance",
            max_staleness_seconds=30.0,
            dry_run=True,
        )
        assert feed.exchange_name == "binance"
        assert feed.dry_run is True
        assert feed.is_connected() is False

    def test_ccxt_feed_connect_disconnect(self):
        feed = CCXTFeed(symbols=["BTC"], exchange="binance", dry_run=True)
        feed.connect()
        assert feed.is_connected() is True
        feed.disconnect()
        assert feed.is_connected() is False

    def test_ccxt_feed_fetch_latest_dry_run(self):
        feed = CCXTFeed(
            symbols=["BTC", "ETH"],
            exchange="binance",
            max_staleness_seconds=60.0,
            dry_run=True,
        )
        feed.connect()
        data = feed.fetch_latest()
        assert "BTC" in data
        assert "ETH" in data
        assert "price" in data["BTC"]
        assert "timestamp" in data["BTC"]
        assert "volume" in data["BTC"]
        assert data["BTC"]["price"] > 0

    def test_ccxt_feed_invalid_exchange(self):
        feed = CCXTFeed(symbols=["BTC"], exchange="invalid_exchange_xyz", dry_run=True)
        with pytest.raises(ValueError, match="not supported by CCXT"):
            feed.connect()

    def test_ccxt_feed_health_check(self):
        feed = CCXTFeed(symbols=["BTC"], exchange="binance", dry_run=True)
        health = feed.health_check()
        assert health.connected is False
        feed.connect()
        health = feed.health_check()
        assert health.connected is True

    def test_ccxt_feed_to_returns_df(self):
        feed = CCXTFeed(symbols=["BTC", "ETH"], exchange="binance", dry_run=True)
        feed.connect()
        data = feed.fetch_latest()
        returns_df = feed.to_returns_df(data)
        assert isinstance(returns_df, pd.DataFrame)


class TestValidateFreshness:
    """Tests for standalone validate_freshness function."""

    def test_validate_freshness_success(self):
        returns_df = pd.DataFrame(
            {"BTC": [0.01, -0.005, 0.002], "ETH": [0.02, 0.001, -0.01]},
            index=pd.date_range("2024-01-01", periods=3, freq="D", tz="UTC"),
        )
        # Should not raise
        validate_freshness(returns_df, max_staleness_days=5.0, max_gap_days=2.0)

    def test_validate_freshness_staleness_violation(self):
        # Data from 10 days ago
        old_date = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=10)
        returns_df = pd.DataFrame(
            {"BTC": [0.01, -0.005]},
            index=pd.DatetimeIndex([old_date, old_date + pd.Timedelta(days=1)], tz="UTC"),
        )
        with pytest.raises(BABDataError, match="staleness.*exceeds max"):
            validate_freshness(returns_df, max_staleness_days=5.0, max_gap_days=2.0)

    def test_validate_freshness_gap_violation(self):
        # Gap of 10 days between observations
        dates = pd.DatetimeIndex(
            ["2024-01-01", "2024-01-11"], tz="UTC"
        )
        returns_df = pd.DataFrame(
            {"BTC": [0.01, -0.005]},
            index=dates,
        )
        with pytest.raises(BABDataError, match="gap.*exceeds max"):
            validate_freshness(returns_df, max_staleness_days=30.0, max_gap_days=5.0)

    def test_validate_freshness_empty_dataframe(self):
        returns_df = pd.DataFrame()
        with pytest.raises(BABDataError, match="Empty returns data"):
            validate_freshness(returns_df)

    def test_validate_freshness_no_datetime_index(self):
        returns_df = pd.DataFrame(
            {"BTC": [0.01, -0.005]},
            index=[0, 1],  # Not datetime
        )
        with pytest.raises(BABDataError, match="cannot be parsed as datetime"):
            validate_freshness(returns_df)

    def test_validate_freshness_naive_datetime_index(self):
        # Naive datetime index should be treated as UTC
        returns_df = pd.DataFrame(
            {"BTC": [0.01, -0.005]},
            index=pd.DatetimeIndex(["2024-01-01", "2024-01-02"]),
        )
        # Should not raise (treated as UTC)
        validate_freshness(returns_df, max_staleness_days=1000.0, max_gap_days=10.0)


class TestCCXTFeedReconnect:
    """Tests for CCXTFeed reconnect/backfill behavior (simulated)."""

    def test_multiple_fetch_latest(self):
        feed = CCXTFeed(symbols=["BTC"], exchange="binance", dry_run=True)
        feed.connect()
        data1 = feed.fetch_latest()
        time.sleep(0.01)  # Small delay to ensure different timestamps
        data2 = feed.fetch_latest()
        # Both should succeed
        assert "BTC" in data1
        assert "BTC" in data2
        # Timestamps should be different (or at least valid)
        assert data1["BTC"]["timestamp"] > 0
        assert data2["BTC"]["timestamp"] > 0


class TestSLAEnforcement:
    """Tests for SLA enforcement edge cases."""

    def test_staleness_exactly_at_limit(self):
        feed = RealtimeFeed(symbols=["BTC"], max_staleness_seconds=10.0)
        import time
        # Exactly at limit (10 seconds ago) - should pass
        limit_time = time.time() - 10.0
        data = {"BTC": {"price": 50000.0, "timestamp": limit_time, "volume": 100.0}}
        assert feed.validate_freshness(data) is True

    def test_staleness_just_over_limit(self):
        feed = RealtimeFeed(symbols=["BTC"], max_staleness_seconds=10.0)
        import time
        # Just over limit (10.1 seconds ago) - should fail
        over_time = time.time() - 10.1
        data = {"BTC": {"price": 50000.0, "timestamp": over_time, "volume": 100.0}}
        with pytest.raises(BABDataError):
            feed.validate_freshness(data)

    def test_gap_exactly_at_limit(self):
        feed = RealtimeFeed(symbols=["BTC"], max_gap_seconds=10.0)
        import time
        now = time.time()
        # First tick at now - 10
        data1 = {"BTC": {"price": 50000.0, "timestamp": now - 10.0, "volume": 100.0}}
        feed.validate_freshness(data1)
        # Second tick at now - exactly 10 second gap
        data2 = {"BTC": {"price": 50100.0, "timestamp": now, "volume": 100.0}}
        assert feed.validate_freshness(data2) is True

    def test_gap_just_over_limit(self):
        feed = RealtimeFeed(symbols=["BTC"], max_gap_seconds=10.0)
        import time
        now = time.time()
        data1 = {"BTC": {"price": 50000.0, "timestamp": now - 10.1, "volume": 100.0}}
        feed.validate_freshness(data1)
        data2 = {"BTC": {"price": 50100.0, "timestamp": now, "volume": 100.0}}
        with pytest.raises(BABDataError, match="Gap SLA violation"):
            feed.validate_freshness(data2)

    def test_multiple_symbols_independent_sla(self):
        feed = RealtimeFeed(symbols=["BTC", "ETH"], max_staleness_seconds=10.0)
        import time
        now = time.time()
        # BTC fresh, ETH stale
        data = {
            "BTC": {"price": 50000.0, "timestamp": now, "volume": 100.0},
            "ETH": {"price": 3000.0, "timestamp": now - 20.0, "volume": 500.0},
        }
        with pytest.raises(BABDataError, match="ETH"):
            feed.validate_freshness(data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
