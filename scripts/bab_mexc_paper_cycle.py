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
from high_vs_low.mexc_paper import Candidate, MEXCRankings
from strategies.betting_against_beta.beta import calculate_beta

BETA_WINDOW = 90
MIN_BETA_OBSERVATIONS = 60
ACCOUNT_ID = "mexc-usdt-forward-bab-100usdt-v1"
STRATEGY_ID = "crypto-bab-low-beta-long-high-beta-short-v1"


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
    high_beta_first: list[Candidate] = []
    instruments_by_key: dict[str, dict[str, Any]] = {}
    for beta, key, instrument, close in ranked:
        instruments_by_key[key] = dict(instrument)
        low_beta_first.append(Candidate(
            symbol=key, distance_pct=beta, extreme_price=None,
            direction="long", close_price=close,
            decision_timestamp_ms=as_of_timestamp_ms,
        ))
        high_beta_first.append(Candidate(
            symbol=key, distance_pct=beta, extreme_price=None,
            direction="short", close_price=close,
            decision_timestamp_ms=as_of_timestamp_ms,
        ))

    # The engine tests the top ten ranked candidates for executable pair fills.
    # It therefore keeps the best-ranked candidate first and falls back only
    # when public depth/lot-size/shortfall gates make that pair unavailable.
    high_beta_first.reverse()
    if low_beta_first[0].symbol == high_beta_first[0].symbol:
        raise RuntimeError("BAB ranking blocked: long and short candidates are not distinct")

    return MEXCRankings(
        research_longs=low_beta_first,
        research_shorts=high_beta_first,
        executable_longs=low_beta_first,
        executable_shorts=high_beta_first,
        instruments_by_key=instruments_by_key,
        excluded=excluded,
    )


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
    result = int(engine._run())

    # A clean bounded history-bootstrap batch is normal progress. Keep it green
    # while the full universe is being collected; API errors and stale/missing
    # current bars still fail the run and remain visible in latest_cycle.json.
    report_path = (
        Path(os.environ.get("MARKET_DATA_DIR", "../market-data"))
        / "data" / "reports" / "mexc" / "latest_cycle.json"
    )
    if result != 0 and report_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        expected_bootstrap = (
            report.get("paper_decision_status") == "BLOCKED_INCOMPLETE_MARKET_DATA"
            and int(report.get("bootstrap_remaining", 0)) > 0
            and int(report.get("api_failure_count", 0)) == 0
            and int(report.get("missing_ticker_count", 0)) == 0
            and int(report.get("missing_latest_bar_count", 0)) == 0
        )
        if expected_bootstrap:
            print(
                "[bab-bootstrap] Full-universe history is still being collected; "
                "portfolio changes remain blocked. This is normal resumable progress."
            )
            return 0
    return result


if __name__ == "__main__":
    raise SystemExit(main())
