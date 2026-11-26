#!/usr/bin/env python3
"""Run the BAB signal through the proven MEXC public-data paper engine."""
from __future__ import annotations

import importlib.util
import json
import math
import os
import sys
import time
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ENGINE_ROOT = ROOT.parent / "engine"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ENGINE_ROOT / "src"))

from high_vs_low.github_state import GitHubStateError, GitHubStatePublisher
from high_vs_low.indicators import wilder_atr
from high_vs_low.mexc_api import _normalize_ticker_row, _payload_rows
from high_vs_low.mexc_paper import Candidate, MEXCRankings
from strategies.betting_against_beta.beta import calculate_beta

BETA_WINDOW = 90
MIN_BETA_OBSERVATIONS = 60
ACCOUNT_ID = "mexc-usdt-forward-bab-100usdt-v1"
STRATEGY_ID = "crypto-bab-low-beta-long-high-beta-short-v1"


def fetch_bab_tickers_with_rest_fallback(
    client: Any,
    websocket_tickers: Any,
) -> list[dict[str, Any]]:
    """Prefer the established all-market WS feed, then use MEXC bulk REST.

    MEXC's public GET /api/v1/contract/ticker endpoint returns all contracts
    when no symbol parameter is supplied. This avoids per-symbol REST calls
    when GitHub-hosted runners cannot complete the public WebSocket handshake.
    """
    try:
        rows = websocket_tickers()
        if rows:
            return rows
        raise RuntimeError("MEXC all-market WebSocket returned an empty ticker set")
    except Exception as websocket_error:
        try:
            payload = client._request("/api/v1/contract/ticker")
            raw_rows = _payload_rows(payload)
            normalized = [_normalize_ticker_row(row) for row in raw_rows]
            if not normalized:
                raise RuntimeError("MEXC bulk REST ticker endpoint returned no usable rows")
            print(
                "[bab-tickers] all-market WebSocket unavailable; "
                f"bulk REST fallback returned {len(normalized)} contract tickers "
                f"({type(websocket_error).__name__})",
                flush=True,
            )
            return normalized
        except Exception as rest_error:
            raise RuntimeError(
                "MEXC ticker acquisition failed via both all-market WebSocket "
                f"and bulk REST; websocket={type(websocket_error).__name__}: "
                f"{str(websocket_error)[:140]}; "
                f"rest={type(rest_error).__name__}: {str(rest_error)[:140]}"
            ) from rest_error


def _close_map(rows: list[dict[str, Any]], cutoff_ms: int) -> dict[int, float]:
    values: dict[int, float] = {}
    for row in rows:
        stamp = int(row.get("timestamp_ms", 0))
        try:
            close = float(row.get("close"))
        except (TypeError, ValueError):
            continue
        if 0 < stamp <= cutoff_ms and math.isfinite(close) and close > 0:
            values[stamp] = close
    return values


def _daily_returns(rows: list[dict[str, Any]], cutoff_ms: int) -> dict[int, float]:
    closes = _close_map(rows, cutoff_ms)
    stamps = sorted(closes)
    return {
        current: closes[current] / closes[previous] - 1.0
        for previous, current in zip(stamps, stamps[1:])
    }


def _has_positive_long_stop(
    rows: list[dict[str, Any]],
    entry_price: float,
    *,
    stop_atr_multiple: Decimal = Decimal("3"),
) -> bool:
    """Keep only long candidates whose inherited 3x-ATR stop is above zero."""
    ordered = sorted(
        (
            row for row in rows
            if int(row.get("timestamp_ms", 0)) > 0
        ),
        key=lambda row: int(row["timestamp_ms"]),
    )
    if len(ordered) < 14:
        return False
    try:
        atr_values = wilder_atr(
            [float(row["high"]) for row in ordered],
            [float(row["low"]) for row in ordered],
            [float(row["close"]) for row in ordered],
            period=14,
        )
        atr = atr_values[-1]
        if atr is None or not math.isfinite(float(atr)) or float(atr) <= 0:
            return False
        return (
            Decimal(str(entry_price))
            - Decimal(str(atr)) * stop_atr_multiple
        ) > 0
    except (KeyError, TypeError, ValueError, ArithmeticError):
        return False


def rank_bab_mexc_universe(
    instruments: list[dict[str, Any]],
    histories: dict[int, list[dict[str, Any]]],
    tickers: dict[int, dict[str, Any]],
    nav: Decimal,
    *,
    as_of_timestamp_ms: int,
    **_: Any,
) -> MEXCRankings:
    """Rank eligible USDT perps by 90d OLS beta to BTC: low beta long, high beta short."""
    del nav
    normalized = {int(row["instrument_id"]): row for row in instruments}
    benchmark_id = None
    for iid, row in normalized.items():
        symbol = str(row.get("symbol", "")).upper()
        base = str(row.get("base_asset") or symbol.split("_", 1)[0]).upper()
        if base == "BTC" and bool(row.get("usdt_account_eligible")):
            benchmark_id = iid
            break
    if benchmark_id is None:
        raise RuntimeError("BAB ranking blocked: no eligible BTC-USDT benchmark contract")

    benchmark_rows = histories.get(benchmark_id, [])
    benchmark_returns = _daily_returns(benchmark_rows, as_of_timestamp_ms)
    benchmark_closes = _close_map(benchmark_rows, as_of_timestamp_ms)
    if not benchmark_closes or max(benchmark_closes) != as_of_timestamp_ms:
        raise RuntimeError("BAB ranking blocked: BTC benchmark lacks the latest completed daily candle")

    ranked: list[tuple[float, str, dict[str, Any], float]] = []
    excluded: list[str] = []
    for iid, instrument in normalized.items():
        symbol = str(instrument.get("symbol", iid))
        if iid == benchmark_id or not bool(instrument.get("usdt_account_eligible")):
            continue
        if tickers.get(iid) is None:
            excluded.append(f"{symbol}:MISSING_TICKER")
            continue
        asset_rows = histories.get(iid, [])
        asset_closes = _close_map(asset_rows, as_of_timestamp_ms)
        if not asset_closes or max(asset_closes) != as_of_timestamp_ms:
            excluded.append(f"{symbol}:MISSING_DECISION_CANDLE")
            continue
        asset_returns = _daily_returns(asset_rows, as_of_timestamp_ms)
        common = sorted(set(asset_returns) & set(benchmark_returns))[-BETA_WINDOW:]
        if len(common) < MIN_BETA_OBSERVATIONS:
            excluded.append(f"{symbol}:INSUFFICIENT_ALIGNED_BETA_HISTORY:{len(common)}")
            continue
        beta = calculate_beta(
            [asset_returns[stamp] for stamp in common],
            [benchmark_returns[stamp] for stamp in common],
            min_obs=MIN_BETA_OBSERVATIONS,
        )
        if beta is None or not math.isfinite(float(beta)):
            excluded.append(f"{symbol}:UNDEFINED_BETA")
            continue
        ranked.append((float(beta), f"mexc:{iid}", instrument, asset_closes[as_of_timestamp_ms]))

    ranked.sort(key=lambda item: (item[0], item[1]))
    if len(ranked) < 2:
        raise RuntimeError(
            "BAB ranking blocked: fewer than two eligible contracts have "
            f"{MIN_BETA_OBSERVATIONS}+ aligned observations; eligible={len(ranked)}"
        )

    low_beta_first: list[Candidate] = []
    executable_longs: list[Candidate] = []
    high_beta_first: list[Candidate] = []
    instruments_by_key: dict[str, dict[str, Any]] = {}
    for beta, key, instrument, close in ranked:
        instruments_by_key[key] = dict(instrument)
        long_candidate = Candidate(
            symbol=key, distance_pct=beta, extreme_price=None,
            direction="long", close_price=close,
            decision_timestamp_ms=as_of_timestamp_ms,
        )
        low_beta_first.append(long_candidate)
        if _has_positive_long_stop(
            histories.get(int(instrument["instrument_id"]), []),
            close,
        ):
            executable_longs.append(long_candidate)
        else:
            excluded.append(f"{instrument.get('symbol', key)}:NONPOSITIVE_OR_UNAVAILABLE_3X_ATR_LONG_STOP")
        high_beta_first.append(Candidate(
            symbol=key, distance_pct=beta, extreme_price=None,
            direction="short", close_price=close,
            decision_timestamp_ms=as_of_timestamp_ms,
        ))

    if not executable_longs:
        raise RuntimeError(
            "BAB ranking blocked: no low-beta long candidate has a valid positive 3x-ATR stop"
        )

    # The engine tests the top ten ranked candidates for executable pair fills.
    # It therefore keeps the best-ranked candidate first and falls back only
    # when public depth/lot-size/shortfall gates make that pair unavailable.
    high_beta_first.reverse()
    if low_beta_first[0].symbol == high_beta_first[0].symbol:
        raise RuntimeError("BAB ranking blocked: long and short candidates are not distinct")

    return MEXCRankings(
        research_longs=low_beta_first,
        research_shorts=high_beta_first,
        executable_longs=executable_longs,
        executable_shorts=high_beta_first,
        instruments_by_key=instruments_by_key,
        excluded=excluded,
    )


DAY_MS = 86_400_000
MINIMUM_REQUEST_INTERVAL_SECONDS = 0.12


def filter_bab_positive_stop_longs(
    rankings: MEXCRankings,
    history: dict[int, list[dict[str, Any]]],
    tickers: dict[int, dict[str, Any]],
) -> MEXCRankings:
    """Revalidate 3x-ATR long stops, including rankings frozen by earlier runs."""
    executable_longs: list[Candidate] = []
    rejected: list[str] = []
    for candidate in rankings.executable_longs:
        instrument = rankings.instruments_by_key.get(candidate.symbol)
        if instrument is None:
            rejected.append(f"{candidate.symbol}:MISSING_INSTRUMENT_FOR_LONG_STOP_CHECK")
            continue
        instrument_id = int(instrument["instrument_id"])
        ticker = tickers.get(instrument_id, {})
        reference_price = None
        for value in (
            ticker.get("ask_price"),
            ticker.get("mark_price"),
            ticker.get("mid_price"),
            candidate.close_price,
        ):
            try:
                parsed = Decimal(str(value))
            except Exception:
                continue
            if parsed.is_finite() and parsed > 0:
                reference_price = float(parsed)
                break
        if reference_price is None or not _has_positive_long_stop(
            history.get(instrument_id, []),
            reference_price,
        ):
            rejected.append(
                f"{instrument.get('symbol', candidate.symbol)}:"
                "NONPOSITIVE_OR_UNAVAILABLE_3X_ATR_LONG_STOP"
            )
            continue
        executable_longs.append(candidate)

    return MEXCRankings(
        research_longs=rankings.research_longs,
        research_shorts=rankings.research_shorts,
        executable_longs=executable_longs,
        executable_shorts=rankings.executable_shorts,
        instruments_by_key=rankings.instruments_by_key,
        excluded=list(rankings.excluded) + rejected,
    )


def refresh_bab_rolling_history(
    client: Any,
    store: Any,
    instruments: list[dict[str, Any]],
    server_ms: int,
    latest_completed_bar_ms: int,
    batch_size: int,
) -> tuple[int, int, list[dict[str, Any]]]:
    """Refresh only the rolling BAB beta window for the complete USDT universe.

    Unlike the ATH/ATL engine, BAB does not need a contract's lifetime history.
    A 90-day window is sufficient for its 90-return beta estimate, with a
    60-aligned-return minimum. Newer/illiquid contracts are recorded as
    insufficient-history exclusions; an API error remains a fail-closed gate.
    """
    del batch_size  # BAB refreshes the full eligible cross-section in one pass.
    if latest_completed_bar_ms <= 0:
        raise ValueError("latest_completed_bar_ms must be positive")

    window_start_ms = latest_completed_bar_ms - BETA_WINDOW * DAY_MS
    end_ms = min(int(server_ms), int(latest_completed_bar_ms) + DAY_MS)
    if end_ms <= latest_completed_bar_ms:
        raise RuntimeError("MEXC server clock has not reached the completed-bar boundary")

    history_by_id = store.load_all_candles(start_timestamp_ms=window_start_ms)
    candle_updates: list[dict[str, Any]] = []
    api_failures: list[dict[str, Any]] = []
    checked_count = 0
    available_count = 0
    insufficient_count = 0

    print(
        f"[bab-history] refreshing rolling {BETA_WINDOW}-day window for "
        f"{len(instruments)} eligible USDT contracts in one daily pass",
        flush=True,
    )

    for instrument in instruments:
        if not bool(instrument.get("usdt_account_eligible")):
            continue

        instrument_id = int(instrument["instrument_id"])
        symbol = str(instrument["symbol"])
        record = store.manifest["instruments"].get(str(instrument_id))
        if record is None:
            raise RuntimeError(f"BAB market-data manifest is missing {symbol} ({instrument_id})")

        listing_time = instrument.get("opening_time_ms") or instrument.get("create_time_ms")
        listing_day_ms = (
            (int(listing_time) // DAY_MS) * DAY_MS
            if listing_time is not None else window_start_ms
        )
        expected_start_ms = max(window_start_ms, listing_day_ms)
        expected_stamps = list(range(
            expected_start_ms, latest_completed_bar_ms + 1, DAY_MS
        ))

        existing_rows = history_by_id.get(instrument_id, [])
        by_timestamp = {
            int(row["timestamp_ms"]): dict(row)
            for row in existing_rows
            if expected_start_ms <= int(row["timestamp_ms"]) <= latest_completed_bar_ms
        }
        missing_stamps = [stamp for stamp in expected_stamps if stamp not in by_timestamp]

        if missing_stamps:
            try:
                fetched = client.candles(
                    symbol,
                    start_timestamp_ms=missing_stamps[0],
                    end_timestamp_ms=end_ms,
                    interval="Day1",
                )
                for candle in fetched:
                    stamp = int(candle["timestamp_ms"])
                    if expected_start_ms <= stamp <= latest_completed_bar_ms:
                        normalized = {
                            **candle,
                            "instrument_id": instrument_id,
                            "symbol": symbol,
                        }
                        by_timestamp[stamp] = normalized
                        candle_updates.append(normalized)
                record["last_bootstrap_error"] = None
            except Exception as exc:
                api_failures.append({
                    "instrument_id": instrument_id,
                    "symbol": symbol,
                    "error": f"{type(exc).__name__}: {str(exc)[:240]}",
                })
                record["last_bootstrap_error"] = (
                    f"{type(exc).__name__}: {str(exc)[:240]}"
                )
                continue

        # Require at least 61 consecutive completed closes ending at the
        # decision candle, which gives at least 60 genuine daily returns.
        consecutive_closes = 0
        stamp = latest_completed_bar_ms
        while stamp in by_timestamp:
            consecutive_closes += 1
            stamp -= DAY_MS

        expected_present = sum(stamp in by_timestamp for stamp in expected_stamps)
        gap_count = max(0, len(expected_stamps) - expected_present)
        if consecutive_closes >= MIN_BETA_OBSERVATIONS + 1:
            history_status = "AVAILABLE"
            available_count += 1
        else:
            history_status = (
                "NO_TRADES_IN_WINDOW" if not by_timestamp else "INSUFFICIENT_HISTORY"
            )
            insufficient_count += 1

        store.mark_bootstrap_complete(
            instrument_id,
            completed_at_ms=server_ms,
            history_status=history_status,
        )
        record["last_checked_daily_bar_ms"] = latest_completed_bar_ms
        record["history_first_candle_timestamp_ms"] = (
            min(by_timestamp) if by_timestamp else None
        )
        record["history_last_candle_timestamp_ms"] = (
            max(by_timestamp) if by_timestamp else None
        )
        record["history_observed_daily_gap_count"] = gap_count
        record["bootstrap_attempts"] = int(record.get("bootstrap_attempts", 0)) + 1
        checked_count += 1

    if candle_updates:
        store.append_candles(candle_updates)
    store.save_manifest(server_ms)

    remaining = sum(
        not bool(store.manifest["instruments"][str(int(row["instrument_id"]))].get("bootstrap_complete"))
        or int(
            store.manifest["instruments"][str(int(row["instrument_id"]))].get(
                "last_checked_daily_bar_ms"
            ) or 0
        ) < latest_completed_bar_ms
        for row in instruments
        if bool(row.get("usdt_account_eligible"))
    )
    print(
        f"[bab-history] checked={checked_count}; available={available_count}; "
        f"insufficient-history={insufficient_count}; api-failures={len(api_failures)}; "
        f"decision-bar-pending={remaining}",
        flush=True,
    )
    return checked_count, remaining, api_failures


def main() -> int:
    if not (ENGINE_ROOT / "scripts" / "high_low_paper_cycle.py").is_file():
        raise RuntimeError("MEXC paper engine checkout is missing at ../engine")
    spec = importlib.util.spec_from_file_location(
        "bab_mexc_engine_cycle",
        ENGINE_ROOT / "scripts" / "high_low_paper_cycle.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the MEXC paper-cycle engine")
    engine = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = engine
    spec.loader.exec_module(engine)

    # GitHub's Git Data endpoints can briefly return a stale ref/tree immediately
    # after a successful ref update. Retry only that eventual-consistency symptom;
    # all integrity, fork and content checks remain hard failures.
    original_verify = GitHubStatePublisher._verify_remote_batch

    def verify_remote_batch_with_retry(self, *args, **kwargs):
        last_error = None
        for attempt in range(5):
            try:
                return original_verify(self, *args, **kwargs)
            except GitHubStateError as exc:
                if (
                    "Required event batch is missing from remote chain" not in str(exc)
                    and "Published event batch is not in the verified remote chain" not in str(exc)
                ):
                    raise
                last_error = exc
                time.sleep(min(2 ** attempt, 8))
        raise last_error

    GitHubStatePublisher._verify_remote_batch = verify_remote_batch_with_retry

    engine.ACCOUNT_ID = ACCOUNT_ID
    engine.STRATEGY_ID = STRATEGY_ID
    engine.INITIAL_CAPITAL = Decimal("100")
    engine.rank_mexc_universe = rank_bab_mexc_universe
    engine._bootstrap_or_increment = refresh_bab_rolling_history

    # The established MEXC engine discovers the market once and obtains all
    # tickers through one WebSocket subscription. BAB narrows its signal and
    # history refresh to the actual USDT-settled account universe.
    base_client = engine.MEXCPublicClient

    class BABMEXCPublicClient(base_client):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault(
                "minimum_interval_seconds", MINIMUM_REQUEST_INTERVAL_SECONDS
            )
            super().__init__(*args, **kwargs)

        def instruments(self, *, usdt_only: bool = True):
            return super().instruments(usdt_only=True)

        def tickers(self):
            return fetch_bab_tickers_with_rest_fallback(self, super().tickers)

    engine.MEXCPublicClient = BABMEXCPublicClient

    original_report_rows = engine._ranking_report_rows

    def bab_ranking_report_rows(candidates, instruments_by_key):
        rows = original_report_rows(candidates, instruments_by_key)
        for row in rows:
            row["beta_vs_btc_90d"] = row.get("distance_pct")
            row["distance_metric"] = "rolling_90d_ols_beta_vs_btc"
            row["extreme_price"] = None
            row["extreme_timestamp_ms"] = None
            row.pop("all_time_history_verified", None)
            row.pop("history_observed_daily_gap_count", None)
        return rows

    engine._ranking_report_rows = bab_ranking_report_rows

    # A pending BAB signal may have been frozen by an earlier run before the
    # ATR-stop filter existed. Revalidate it at the shared pair-selection
    # boundary, including during retry cycles, without resetting the ledger.
    original_try_pair = engine._try_pair

    def bab_try_pair(client, rankings, history, tickers, state, now_ms, *, max_pairs=100):
        safe_rankings = filter_bab_positive_stop_longs(
            rankings, history, tickers
        )
        return original_try_pair(
            client, safe_rankings, history, tickers, state, now_ms,
            max_pairs=max_pairs,
        )

    engine._try_pair = bab_try_pair

    # A blocked portfolio decision is a failed paper cycle. Do not convert
    # missing history, API errors, or incomplete ranking coverage into green CI.
    return int(engine._run())


if __name__ == "__main__":
    raise SystemExit(main())
