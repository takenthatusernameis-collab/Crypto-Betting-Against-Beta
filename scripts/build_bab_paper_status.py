#!/usr/bin/env python3
"""Build BAB paper status, primary journal and inverse-volatility shadow curve."""
from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_ROOT = ROOT.parent / "engine"
sys.path.insert(0, str(ENGINE_ROOT / "src"))

from high_vs_low.market_data_store import MarketDataStore
import high_vs_low.paper_status as status

status.ACCOUNT_ID = "mexc-usdt-forward-bab-100usdt-v1"
status.STRATEGY_ID = "crypto-bab-low-beta-long-high-beta-short-v1"
status.INITIAL_CAPITAL = Decimal("100")

market_data = Path(os.environ.get("MARKET_DATA_DIR", "../market-data"))
state_dir = Path(os.environ.get("PAPER_STATE_DIR", "../state"))
generated_at_ms = int(datetime.now(UTC).timestamp() * 1000)
store = MarketDataStore(market_data, provider="mexc")
history = store.load_all_candles(
    start_timestamp_ms=max(0, generated_at_ms - 45 * 86_400_000)
)
metadata = {
    "repository": os.environ.get("GITHUB_REPOSITORY", ""),
    "server_url": os.environ.get("GITHUB_SERVER_URL", "https://github.com"),
    "run_id": os.environ.get("GITHUB_RUN_ID", ""),
    "run_number": os.environ.get("GITHUB_RUN_NUMBER", ""),
    "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
    "run_url": (
        f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/"
        f"{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/"
        f"{os.environ.get('GITHUB_RUN_ID', '')}"
    ),
    "outcome": os.environ.get("PAPER_WORKFLOW_OUTCOME", "unknown"),
    "event_name": os.environ.get("GITHUB_EVENT_NAME", "scheduled"),
}
markdown = status.render_paper_status(
    state_dir,
    history,
    metadata,
    generated_at_ms=generated_at_ms,
    equal_svg_path=ROOT / "equal_exposure_equity_curve.svg",
    alternative_svg_path=ROOT / "alternative_path_equity_curve.svg",
)
markdown = (
    markdown.replace("HIGH-LOW", "BAB")
    .replace("High-Low", "BAB")
    .replace("high-low-paper-cycle.yml", "bab-paper-cycle.yml")
    .replace("ATH/ATL", "BAB low-beta/high-beta")
)


coverage_path = market_data / "data" / "reports" / "mexc" / "latest_cycle.json"
if coverage_path.is_file():
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    latest_bar_ms = int(coverage.get("latest_completed_daily_bar_ms") or 0)
    last_verified_bar_ms = int(store.manifest.get("last_research_daily_bar_ms") or 0)
    explicit_coverage = coverage.get("history_coverage_pass")
    if explicit_coverage is True:
        coverage_state = "READY"
    elif explicit_coverage is False:
        coverage_state = "BOOTSTRAPPING"
    elif latest_bar_ms > 0 and last_verified_bar_ms >= latest_bar_ms:
        coverage_state = "VERIFIED — SNAPSHOT ONLY"
    else:
        coverage_state = "NOT VERIFIED"

    manifest_rows = store.manifest.get("instruments", {})
    active_rows = [
        row for row in manifest_rows.values()
        if row.get("status") == "active"
    ]
    eligible_rows = [
        row for row in active_rows if bool(row.get("usdt_account_eligible"))
    ]
    available_histories = sum(
        row.get("history_status") == "AVAILABLE" for row in eligible_rows
    )
    insufficient_histories = sum(
        row.get("history_status") in {"INSUFFICIENT_HISTORY", "NO_TRADES_IN_WINDOW"}
        for row in eligible_rows
    )
    coverage_note = "\n".join([
        "",
        "## MEXC market-data coverage",
        "",
        f"- Coverage state: **{coverage_state}**",
        f"- Active USDT-settled trading contracts: {len(eligible_rows)}",
        f"- Contracts with at least 60 aligned daily beta returns: {available_histories}",
        f"- Contracts excluded for insufficient rolling history: {insufficient_histories}",
        f"- Latest completed daily bar (UTC ms): {coverage.get('latest_completed_daily_bar_ms', '—')}",
        f"- Portfolio decision status: `{coverage.get('paper_decision_status', 'UNKNOWN')}`",
        "",
        (
            "The complete eligible USDT universe is evaluated through the rolling-history gate "
            "at each daily decision. Snapshot-only runs reuse the last verified daily gate and "
            "do not recompute the ranking."
            if coverage_state == "VERIFIED — SNAPSHOT ONLY"
            else "The full eligible USDT cross-section must pass the rolling-history, ticker and latest-bar gates before a daily portfolio decision."
        ),
        "",
    ])
    if coverage_state == "BOOTSTRAPPING":
        markdown = markdown.replace(
            "**🟢 ACTIVE · PAPER ONLY · NO LIVE ORDERS**",
            "**BOOTSTRAPPING · PAPER ONLY · NO LIVE ORDERS**",
        )

    mode = str(coverage.get("mode", ""))
    if mode == "PORTFOLIO_SNAPSHOT_ONLY":
        progress_text = (
            "The latest daily decision has already been processed. Intervening five-minute "
            "runs only mark the existing paper positions and update equity, funding and risk; "
            "the next ranking occurs after a new completed UTC daily candle."
        )
    elif coverage_state == "READY":
        progress_text = (
            "The complete eligible USDT cross-section passed the rolling-history and "
            "execution-data gates for the latest daily decision. The next ranking occurs "
            "after a new completed UTC daily candle."
        )
    else:
        progress_text = (
            "The next daily portfolio decision remains blocked until the complete eligible "
            "USDT cross-section passes the rolling-history and current-market-data gates."
        )
    markdown = markdown.replace(
        "The next daily decision requires a newer completed UTC candle and a passing data-coverage gate.",
        progress_text,
    ).replace(
        "The latest completed UTC daily candle is waiting for full-universe history coverage; no portfolio decision has been consumed.",
        progress_text,
    )
    coverage_note += "The portfolio remains a paper simulation; all fills are simulated and no exchange orders are submitted.\n"

    if mode != "PORTFOLIO_SNAPSHOT_ONLY":
        long_preview = coverage.get("research_long_top", [])[:3]
        short_preview = coverage.get("research_short_top", [])[:3]
        preview_lines = [
            "",
            "### BAB daily ranking preview",
            "",
            "Research ranks include assets excluded from executable sizing; execution eligibility is shown separately in exclusions.",
            "",
            "**Lowest-beta long candidates**",
        ]
        preview_lines.extend(
            f"- {row.get('symbol', '—')}: β(BTC)={row.get('beta_vs_btc_90d', row.get('distance_pct', '—'))}"
            for row in long_preview
        )
        preview_lines.extend(["", "**Highest-beta short candidates**"])
        preview_lines.extend(
            f"- {row.get('symbol', '—')}: β(BTC)={row.get('beta_vs_btc_90d', row.get('distance_pct', '—'))}"
            for row in short_preview
        )
        coverage_note += "\\n".join(preview_lines) + "\n"
    markdown = markdown.replace("## Current performance", coverage_note + "## Current performance")

(ROOT / "PAPER_STATUS.md").write_text(markdown, encoding="utf-8")
journal = status.render_primary_trade_journal(
    state_dir,
    generated_at_ms=generated_at_ms,
    workflow_metadata=metadata,
)
journal = (
    journal.replace("HIGH-LOW", "BAB")
    .replace("High-Low", "BAB")
    .replace("ATH/ATL", "BAB")
)
(ROOT / "PAPER_TRADE_JOURNAL.md").write_text(journal, encoding="utf-8")
print("Published BAB status, primary trade journal and both equity curves.")
