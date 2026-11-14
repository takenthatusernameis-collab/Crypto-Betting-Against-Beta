"""Pluggable data sources for BAB strategy."""

from __future__ import annotations

import contextlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from .data_loader import load_returns


class DataSource(ABC):
    """Abstract base class for data sources."""

    @abstractmethod
    def load(self, **kwargs) -> pd.DataFrame:
        """Load returns data as a DataFrame."""
        raise NotImplementedError


class CSVDataSource(DataSource):
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self, benchmark: str | None = None, min_rows: int = 1, **kwargs) -> pd.DataFrame:
        return load_returns(self.path, benchmark=benchmark, min_rows=min_rows, **kwargs)


class ParquetDataSource(DataSource):
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self, benchmark: str | None = None, min_rows: int = 1, **kwargs) -> pd.DataFrame:
        return load_returns(self.path, benchmark=benchmark, min_rows=min_rows, **kwargs)


class HDF5DataSource(DataSource):
    def __init__(self, path: str | Path, key: str | None = None):
        self.path = Path(path)
        self.key = key

    def load(self, benchmark: str | None = None, min_rows: int = 1, **kwargs) -> pd.DataFrame:
        kwargs = dict(kwargs)
        if self.key is not None and "key" not in kwargs:
            kwargs["key"] = self.key
        return load_returns(self.path, benchmark=benchmark, min_rows=min_rows, **kwargs)


class PickleDataSource(DataSource):
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self, benchmark: str | None = None, min_rows: int = 1, **kwargs) -> pd.DataFrame:
        return load_returns(self.path, benchmark=benchmark, min_rows=min_rows, **kwargs)


class DataFrameDataSource(DataSource):
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def load(self, benchmark: str | None = None, min_rows: int = 1, **kwargs) -> pd.DataFrame:
        return load_returns(self.df, benchmark=benchmark, min_rows=min_rows, **kwargs)


class DataCache:
    """Simple in-memory cache for loaded data with basic size limits."""

    def __init__(self, max_entries: int = 32):
        self.max_entries = int(max_entries)
        self._cache: dict[str, pd.DataFrame] = {}
        self._order: list[str] = []

    def get(self, key: str) -> pd.DataFrame | None:
        if key in self._cache:
            # move to end (LRU-ish)
            with contextlib.suppress(ValueError):
                self._order.remove(key)
            self._order.append(key)
            # return a copy to avoid external mutation
            cached = self._cache[key]
            if isinstance(cached, pd.DataFrame):
                return cached.copy()
            return cached
        return None

    def set(self, key: str, df: pd.DataFrame) -> None:
        if key in self._cache:
            with contextlib.suppress(ValueError):
                self._order.remove(key)
        self._cache[key] = df.copy() if isinstance(df, pd.DataFrame) else df
        self._order.append(key)
        while len(self._order) > self.max_entries:
            oldest = self._order.pop(0)
            self._cache.pop(oldest, None)


# ---------------------------------------------------------------------------
# P9: Real-time data feed & freshness SLA
# ---------------------------------------------------------------------------


class BABDataError(Exception):
    """Exception for BAB data errors (freshness, schema, connectivity)."""
    pass


@dataclass(frozen=True)
class FeedHealth:
    """Health check status for a real-time feed.

    Strict-JSON-safe: every field is a primitive or a dict of primitives.
    """

    connected: bool
    last_tick: str | None = None
    staleness_seconds: float | None = None
    gap_seconds: float | None = None
    symbols: list[str] = field(default_factory=list)
    error: str | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "connected": self.connected,
            "last_tick": self.last_tick,
            "staleness_seconds": self.staleness_seconds,
            "gap_seconds": self.gap_seconds,
            "symbols": list(self.symbols),
            "error": self.error,
            "metadata": self.metadata,
        }


class RealtimeFeed(ABC):
    """Abstract base class for real-time data feeds.

    Enforces tick/bar freshness SLA (max_staleness_seconds, max_gap_seconds).
    Normalizes output to load_prices/load_returns schema.
    """

    def __init__(
        self,
        symbols: list[str],
        max_staleness_seconds: float = 30.0,
        max_gap_seconds: float = 60.0,
    ) -> None:
        self.symbols = [s.upper() for s in symbols]
        self.max_staleness_seconds = float(max_staleness_seconds)
        self.max_gap_seconds = float(max_gap_seconds)
        self._connected = False
        self._last_tick_time: dict[str, float] = {}
        self._last_tick_data: dict[str, dict] = {}
        self._error: str | None = None

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the feed."""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the feed."""
        ...

    @abstractmethod
    def fetch_latest(self) -> dict[str, dict]:
        """Fetch latest tick/bar data for all symbols.

        Returns dict: {symbol: {"price": float, "timestamp": float, "volume": float, ...}}
        """
        ...

    def is_connected(self) -> bool:
        """Check if feed is connected."""
        return self._connected

    def validate_freshness(self, data: dict[str, dict]) -> bool:
        """Validate data freshness against SLA.

        Raises BABDataError on violation (no silent fallback).
        """
        import time
        now = time.time()

        for symbol in self.symbols:
            if symbol not in data:
                raise BABDataError(f"Missing data for required symbol: {symbol}")

            tick = data[symbol]
            tick_time = tick.get("timestamp")
            if tick_time is None:
                raise BABDataError(f"Missing timestamp for {symbol}")

            staleness = now - tick_time
            if staleness > self.max_staleness_seconds:
                raise BABDataError(
                    f"Staleness SLA violation for {symbol}: {staleness:.1f}s > "
                    f"{self.max_staleness_seconds:.1f}s"
                )

            last_time = self._last_tick_time.get(symbol)
            if last_time is not None:
                gap = tick_time - last_time
                if gap > self.max_gap_seconds:
                    raise BABDataError(
                        f"Gap SLA violation for {symbol}: {gap:.1f}s > "
                        f"{self.max_gap_seconds:.1f}s"
                    )

            self._last_tick_time[symbol] = tick_time
            self._last_tick_data[symbol] = tick

        return True

    def health_check(self) -> FeedHealth:
        """Return health status for the feed."""
        import time
        now = time.time()
        last_tick = None
        staleness = None
        gap = None

        if self._last_tick_time:
            latest_time = max(self._last_tick_time.values())
            last_tick = pd.Timestamp(latest_time, unit="s", tz="UTC").isoformat()
            staleness = now - latest_time

            times = sorted(self._last_tick_time.values())
            if len(times) > 1:
                gaps = [times[i] - times[i - 1] for i in range(1, len(times))]
                gap = max(gaps) if gaps else None

        return FeedHealth(
            connected=self._connected,
            last_tick=last_tick,
            staleness_seconds=staleness,
            gap_seconds=gap,
            symbols=self.symbols,
            error=self._error,
        )

    def to_returns_df(self, data: dict[str, dict]) -> pd.DataFrame:
        """Convert tick data to returns DataFrame compatible with load_returns."""
        rows = []
        for symbol, tick in data.items():
            if "price" in tick and "timestamp" in tick:
                rows.append(
                    {
                        "date": pd.Timestamp(tick["timestamp"], unit="s", tz="UTC"),
                        symbol: tick["price"],
                    }
                )
        if not rows:
            return pd.DataFrame()

        # Build price DataFrame then convert to returns
        price_df = pd.DataFrame(rows)
        price_df = price_df.set_index("date").sort_index()
        returns_df = price_df.pct_change().dropna()
        return returns_df


class CCXTFeed(RealtimeFeed):
    """CCXT-based real-time feed for spot/futures markets.

    Dry-run by default: returns simulated ticks without network calls.
    """

    def __init__(
        self,
        symbols: list[str],
        exchange: str = "binance",
        max_staleness_seconds: float = 30.0,
        max_gap_seconds: float = 60.0,
        dry_run: bool = True,
        api_key: str | None = None,
        api_secret: str | None = None,
        testnet: bool = False,
        rate_limit: bool = True,
    ) -> None:
        super().__init__(symbols, max_staleness_seconds, max_gap_seconds)
        self.exchange_name = exchange.lower()
        self.dry_run = dry_run
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.rate_limit = rate_limit
        self._exchange = None
        self._markets_loaded = False

    def _get_ccxt(self):
        """Lazy import of CCXT."""
        try:
            import ccxt
            return ccxt
        except ImportError:
            raise RuntimeError(
                "ccxt is required for CCXTFeed. "
                "Install with: pip install 'crypto-betting-against-beta[live]'"
            )

    def connect(self) -> None:
        """Establish connection to the exchange."""
        if self._connected:
            return

        ccxt = self._get_ccxt()
        exchange_class = getattr(ccxt, self.exchange_name, None)
        if exchange_class is None:
            raise ValueError(f"Exchange '{self.exchange_name}' not supported by CCXT")

        config = {"enableRateLimit": self.rate_limit}
        if self.api_key:
            config["apiKey"] = self.api_key
        if self.api_secret:
            config["secret"] = self.api_secret
        if self.testnet:
            config["options"] = {"defaultType": "future"}

        self._exchange = exchange_class(config)

        if not self.dry_run:
            self._exchange.load_markets()
            self._markets_loaded = True

        self._connected = True
        self._error = None

    def disconnect(self) -> None:
        """Close connection to the exchange."""
        if self._exchange and hasattr(self._exchange, "close"):
            with contextlib.suppress(Exception):
                self._exchange.close()
        self._exchange = None
        self._connected = False
        self._markets_loaded = False

    def fetch_latest(self) -> dict[str, dict]:
        """Fetch latest ticker data for all symbols."""
        if not self.is_connected():
            raise RuntimeError("Feed not connected. Call connect() first.")

        result = {}
        for symbol in self.symbols:
            ccxt_symbol = self._to_ccxt_symbol(symbol)
            if self.dry_run:
                # Simulated tick
                import random
                import time
                base_price = 100.0 + hash(symbol) % 10000 / 100
                price = base_price * (1 + random.uniform(-0.01, 0.01))
                result[symbol] = {
                    "price": price,
                    "timestamp": time.time(),
                    "volume": random.uniform(1000, 100000),
                    "bid": price * 0.999,
                    "ask": price * 1.001,
                }
            else:
                try:
                    ticker = self._exchange.fetch_ticker(ccxt_symbol)
                    result[symbol] = {
                        "price": ticker.get("last") or ticker.get("close"),
                        "timestamp": ticker.get("timestamp", time.time() * 1000) / 1000,
                        "volume": ticker.get("baseVolume"),
                        "bid": ticker.get("bid"),
                        "ask": ticker.get("ask"),
                    }
                except Exception as exc:
                    self._error = str(exc)
                    raise BABDataError(f"Failed to fetch ticker for {symbol}: {exc}") from exc

        self.validate_freshness(result)
        return result

    def _to_ccxt_symbol(self, symbol: str) -> str:
        """Convert asset symbol to CCXT format (e.g., BTC -> BTC/USDT)."""
        return f"{symbol.upper()}/USDT"


class WebSocketFeed(RealtimeFeed):
    """WebSocket-based real-time feed (abstract, exchange-specific implementations).

    Subclasses must implement _connect_ws, _disconnect_ws, and _on_message.
    """

    def __init__(
        self,
        symbols: list[str],
        url: str,
        max_staleness_seconds: float = 30.0,
        max_gap_seconds: float = 60.0,
    ) -> None:
        super().__init__(symbols, max_staleness_seconds, max_gap_seconds)
        self.url = url
        self._ws = None
        self._running = False

    @abstractmethod
    def _connect_ws(self) -> None:
        """Establish WebSocket connection."""
        ...

    @abstractmethod
    def _disconnect_ws(self) -> None:
        """Close WebSocket connection."""
        ...

    @abstractmethod
    def _on_message(self, message: dict) -> None:
        """Handle incoming WebSocket message."""
        ...

    def connect(self) -> None:
        """Establish WebSocket connection."""
        if self._connected:
            return
        self._connect_ws()
        self._running = True
        self._connected = True
        self._error = None

    def disconnect(self) -> None:
        """Close WebSocket connection."""
        self._running = False
        self._disconnect_ws()
        self._ws = None
        self._connected = False

    def fetch_latest(self) -> dict[str, dict]:
        """Return latest cached tick data."""
        if not self.is_connected():
            raise RuntimeError("Feed not connected. Call connect() first.")

        if not self._last_tick_data:
            raise BABDataError("No tick data received yet")

        # Return cached data (WebSocket pushes updates asynchronously)
        result = dict(self._last_tick_data)
        self.validate_freshness(result)
        return result


def validate_freshness(
    returns_df: pd.DataFrame,
    max_staleness_days: float = 2.0,
    max_gap_days: float = 7.0,
) -> None:
    """Validate freshness of loaded returns data.

    Raises BABDataError if data is stale or has gaps beyond thresholds.
    """
    if returns_df is None or returns_df.empty:
        raise BABDataError("Empty returns data")

    idx = returns_df.index
    if not isinstance(idx, pd.DatetimeIndex):
        try:
            idx = pd.to_datetime(idx)
        except Exception:
            raise BABDataError("Index cannot be parsed as datetime")

    now = pd.Timestamp.now(tz="UTC")
    idx = idx.tz_localize("UTC") if idx.tz is None else idx.tz_convert("UTC")

    # Check staleness (time since last observation)
    last_date = idx[-1]
    staleness = (now - last_date).total_seconds() / 86400  # days
    if staleness > max_staleness_days:
        raise BABDataError(
            f"Data staleness {staleness:.1f} days exceeds max {max_staleness_days:.1f} days"
        )

    # Check gaps
    diffs = idx.to_series().diff().dropna()
    max_gap = diffs.max().total_seconds() / 86400  # days
    if max_gap > max_gap_days:
        raise BABDataError(
            f"Data gap {max_gap:.1f} days exceeds max {max_gap_days:.1f} days"
        )
