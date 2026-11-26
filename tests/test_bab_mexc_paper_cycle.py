from __future__ import annotations

from decimal import Decimal

from scripts.bab_mexc_paper_cycle import rank_bab_mexc_universe

DAY = 86_400_000


def _history(asset_returns: list[float], start: int) -> list[dict]:
    price = 100.0
    rows = [{"timestamp_ms": start, "close": str(price)}]
    for i, value in enumerate(asset_returns, start=1):
        price *= 1.0 + value
        rows.append({"timestamp_ms": start + i * DAY, "close": str(price)})
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
