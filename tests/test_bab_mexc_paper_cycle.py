from __future__ import annotations

from decimal import Decimal

from high_vs_low.mexc_paper import Candidate, MEXCRankings
from scripts.bab_mexc_paper_cycle import (
    rank_bab_mexc_universe,
    refresh_bab_rolling_history,
    filter_bab_positive_stop_longs,
)

DAY = 86_400_000


def _history(asset_returns: list[float], start: int) -> list[dict]:
    price = 100.0
    rows = [{
        "timestamp_ms": start,
        "open": str(price),
        "high": str(price * 1.01),
        "low": str(price * 0.99),
        "close": str(price),
    }]
    for i, value in enumerate(asset_returns, start=1):
        price *= 1.0 + value
        rows.append({
            "timestamp_ms": start + i * DAY,
            "open": str(price),
            "high": str(price * 1.01),
            "low": str(price * 0.99),
            "close": str(price),
        })
    return rows


def test_bab_selects_lowest_beta_long_and_highest_beta_short() -> None:
    start = 1_700_000_000_000
    benchmark_returns = [0.012 * ((i % 7) - 3) for i in range(100)]
    low_returns = [0.25 * value for value in benchmark_returns]
    high_returns = [1.8 * value for value in benchmark_returns]
    medium_returns = [0.9 * value for value in benchmark_returns]
    histories = {
        1: _history(benchmark_returns, start),
        2: _history(low_returns, start),
        3: _history(medium_returns, start),
        4: _history(high_returns, start),
    }
    instruments = [
        {"instrument_id": 1, "symbol": "BTC_USDT", "usdt_account_eligible": True},
        {"instrument_id": 2, "symbol": "LOW_USDT", "usdt_account_eligible": True},
        {"instrument_id": 3, "symbol": "MID_USDT", "usdt_account_eligible": True},
        {"instrument_id": 4, "symbol": "HIGH_USDT", "usdt_account_eligible": True},
    ]
    as_of = start + 100 * DAY
    tickers = {iid: {"last_price": "100"} for iid in histories}

    result = rank_bab_mexc_universe(
        instruments, histories, tickers, Decimal("100"),
        as_of_timestamp_ms=as_of,
    )

    assert result.executable_longs[0].symbol == "mexc:2"
    assert result.executable_shorts[0].symbol == "mexc:4"
    assert result.executable_longs[0].direction == "long"
    assert result.executable_shorts[0].direction == "short"
    assert result.executable_longs[0].symbol != result.executable_shorts[0].symbol


def test_bab_requires_at_least_two_eligible_non_benchmark_contracts() -> None:
    start = 1_700_000_000_000
    returns = [0.01 * ((i % 5) - 2) for i in range(100)]
    histories = {
        1: _history(returns, start),
        2: _history([0.5 * value for value in returns], start),
    }
    instruments = [
        {"instrument_id": 1, "symbol": "BTC_USDT", "usdt_account_eligible": True},
        {"instrument_id": 2, "symbol": "ONLY_USDT", "usdt_account_eligible": True},
    ]
    tickers = {1: {"last_price": "100"}, 2: {"last_price": "100"}}
    try:
        rank_bab_mexc_universe(
            instruments, histories, tickers, Decimal("100"),
            as_of_timestamp_ms=start + 100 * DAY,
        )
    except RuntimeError as exc:
        assert "fewer than two" in str(exc)
    else:
        raise AssertionError("A one-contract universe must not create a self-hedged pair")



class _FakeStore:
    def __init__(self, instruments, history=None):
        self.manifest = {
            "instruments": {
                str(row["instrument_id"]): {
                    "bootstrap_complete": False,
                    "bootstrap_attempts": 0,
                    "last_checked_daily_bar_ms": None,
                }
                for row in instruments
            }
        }
        self.rows = {
            int(iid): {int(row["timestamp_ms"]): dict(row) for row in rows}
            for iid, rows in (history or {}).items()
        }

    def load_all_candles(self, *, start_timestamp_ms=None):
        output = {}
        for iid, items in self.rows.items():
            selected = [
                dict(row) for stamp, row in sorted(items.items())
                if start_timestamp_ms is None or stamp >= start_timestamp_ms
            ]
            if selected:
                output[iid] = selected
        return output

    def append_candles(self, rows):
        for row in rows:
            iid = int(row["instrument_id"])
            self.rows.setdefault(iid, {})[int(row["timestamp_ms"])] = dict(row)

    def mark_bootstrap_complete(self, instrument_id, *, completed_at_ms, history_status):
        record = self.manifest["instruments"][str(int(instrument_id))]
        record["bootstrap_complete"] = True
        record["bootstrap_completed_at_ms"] = int(completed_at_ms)
        record["history_status"] = history_status

    def save_manifest(self, now_ms):
        self.manifest["updated_at_ms"] = int(now_ms)


class _FakeCandleClient:
    def __init__(self, *, failures=None):
        self.failures = set(failures or [])
        self.calls = []

    def candles(self, symbol, *, start_timestamp_ms, end_timestamp_ms, interval):
        self.calls.append((symbol, start_timestamp_ms, end_timestamp_ms, interval))
        if symbol in self.failures:
            raise RuntimeError("simulated public candle endpoint failure")
        return [
            {
                "timestamp_ms": stamp,
                "open": "100",
                "high": "101",
                "low": "99",
                "close": str(100 + (stamp // DAY) / 1000),
                "volume_contracts": "10",
                "turnover_quote": "1000",
            }
            for stamp in range(start_timestamp_ms, end_timestamp_ms, DAY)
        ]


def test_bab_refreshes_full_usdt_universe_in_one_daily_pass() -> None:
    latest = 100 * DAY
    instruments = [
        {"instrument_id": 1, "symbol": "BTC_USDT", "usdt_account_eligible": True},
        {"instrument_id": 2, "symbol": "LOW_USDT", "usdt_account_eligible": True},
        {
            "instrument_id": 3,
            "symbol": "NEW_USDT",
            "usdt_account_eligible": True,
            "opening_time_ms": 80 * DAY,
        },
    ]
    store = _FakeStore(instruments)
    client = _FakeCandleClient()

    checked, remaining, failures = refresh_bab_rolling_history(
        client, store, instruments, 102 * DAY, latest, batch_size=150
    )

    assert checked == 3
    assert remaining == 0
    assert failures == []
    assert [call[0] for call in client.calls] == [
        "BTC_USDT", "LOW_USDT", "NEW_USDT"
    ]
    assert store.manifest["instruments"]["1"]["history_status"] == "AVAILABLE"
    assert store.manifest["instruments"]["2"]["history_status"] == "AVAILABLE"
    assert store.manifest["instruments"]["3"]["history_status"] == "INSUFFICIENT_HISTORY"
    assert store.manifest["instruments"]["3"]["last_checked_daily_bar_ms"] == latest


def test_bab_refresh_skips_history_already_complete_through_decision_bar() -> None:
    latest = 100 * DAY
    instruments = [
        {"instrument_id": 1, "symbol": "BTC_USDT", "usdt_account_eligible": True},
        {"instrument_id": 2, "symbol": "ALT_USDT", "usdt_account_eligible": True},
    ]
    history = {
        iid: [
            {
                "timestamp_ms": stamp,
                "open": "100",
                "high": "101",
                "low": "99",
                "close": "100",
            }
            for stamp in range(latest - 90 * DAY, latest + 1, DAY)
        ]
        for iid in (1, 2)
    }
    store = _FakeStore(instruments, history)
    client = _FakeCandleClient()

    checked, remaining, failures = refresh_bab_rolling_history(
        client, store, instruments, 102 * DAY, latest, batch_size=0
    )

    assert checked == 2
    assert remaining == 0
    assert failures == []
    assert client.calls == []


def test_bab_candle_api_failure_keeps_the_daily_decision_blocked() -> None:
    latest = 100 * DAY
    instruments = [
        {"instrument_id": 1, "symbol": "BTC_USDT", "usdt_account_eligible": True},
        {"instrument_id": 2, "symbol": "BROKEN_USDT", "usdt_account_eligible": True},
    ]
    store = _FakeStore(instruments)
    client = _FakeCandleClient(failures={"BROKEN_USDT"})

    checked, remaining, failures = refresh_bab_rolling_history(
        client, store, instruments, 102 * DAY, latest, batch_size=0
    )

    assert checked == 1
    assert remaining == 1
    assert len(failures) == 1
    assert failures[0]["symbol"] == "BROKEN_USDT"
    assert not store.manifest["instruments"]["2"]["bootstrap_complete"]



def test_bab_keeps_research_rank_but_skips_nonpositive_atr_long_stop() -> None:
    start = 1_700_000_000_000
    benchmark_returns = [0.012 * ((i % 7) - 3) for i in range(100)]
    low_returns = [0.25 * value for value in benchmark_returns]
    medium_returns = [0.9 * value for value in benchmark_returns]
    high_returns = [1.8 * value for value in benchmark_returns]
    histories = {
        1: _history(benchmark_returns, start),
        2: _history(low_returns, start),
        3: _history(medium_returns, start),
        4: _history(high_returns, start),
    }
    # Preserve the low-beta signal while making its 3x-ATR long stop
    # mathematically non-positive, as occurred with the first candidate in run #9.
    for row in histories[2]:
        close = float(row["close"])
        row["high"] = str(close * 2.0)
        row["low"] = str(close * 0.1)

    instruments = [
        {"instrument_id": 1, "symbol": "BTC_USDT", "usdt_account_eligible": True},
        {"instrument_id": 2, "symbol": "LOW_USDT", "usdt_account_eligible": True},
        {"instrument_id": 3, "symbol": "MID_USDT", "usdt_account_eligible": True},
        {"instrument_id": 4, "symbol": "HIGH_USDT", "usdt_account_eligible": True},
    ]
    tickers = {iid: {"last_price": "100"} for iid in histories}

    result = rank_bab_mexc_universe(
        instruments,
        histories,
        tickers,
        Decimal("100"),
        as_of_timestamp_ms=start + 100 * DAY,
    )

    assert result.research_longs[0].symbol == "mexc:2"
    assert result.executable_longs[0].symbol == "mexc:3"
    assert any("NONPOSITIVE_OR_UNAVAILABLE_3X_ATR_LONG_STOP" in item for item in result.excluded)



def test_bab_retry_filter_removes_stale_invalid_long_from_frozen_ranking() -> None:
    start = 1_700_000_000_000
    returns = [0.01 * ((i % 7) - 3) for i in range(100)]
    unsafe_history = _history(returns, start)
    safe_history = _history(returns, start)
    for row in unsafe_history:
        close = float(row["close"])
        row["high"] = str(close * 2.0)
        row["low"] = str(close * 0.1)

    unsafe = Candidate(
        symbol="mexc:2", distance_pct=-1.0, extreme_price=None,
        direction="long", close_price=None,
    )
    safe = Candidate(
        symbol="mexc:3", distance_pct=-0.5, extreme_price=None,
        direction="long", close_price=None,
    )
    rankings = MEXCRankings(
        research_longs=[unsafe, safe],
        research_shorts=[],
        executable_longs=[unsafe, safe],
        executable_shorts=[],
        instruments_by_key={
            "mexc:2": {"instrument_id": 2, "symbol": "UNSAFE_USDT"},
            "mexc:3": {"instrument_id": 3, "symbol": "SAFE_USDT"},
        },
        excluded=[],
    )
    filtered = filter_bab_positive_stop_longs(
        rankings,
        {2: unsafe_history, 3: safe_history},
        {
            2: {"ask_price": "100"},
            3: {"ask_price": "100"},
        },
    )

    assert [candidate.symbol for candidate in filtered.research_longs] == [
        "mexc:2", "mexc:3"
    ]
    assert [candidate.symbol for candidate in filtered.executable_longs] == [
        "mexc:3"
    ]
    assert any(
        "UNSAFE_USDT:NONPOSITIVE_OR_UNAVAILABLE_3X_ATR_LONG_STOP" in item
        for item in filtered.excluded
    )
