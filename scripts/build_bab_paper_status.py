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
    .replace(
        "The next daily decision requires a newer completed UTC candle and a passing data-coverage gate.",
        "The latest completed UTC daily candle is waiting for full-universe history coverage; no portfolio decision has been consumed."
    )
)

coverage_path = market_data / "data" / "reports" / "mexc" / "latest_cycle.json"
if coverage_path.is_file():
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    coverage_state = "READY" if coverage.get("history_coverage_pass") else "BOOTSTRAPPING"
    coverage_note = "\n".join([
        "",
        "## MEXC market-data coverage",
        "",
        f"- Coverage state: **{coverage_state}**",
        f"- Active cross-margin contracts: {coverage.get('active_cross_margin_perpetual_count', '—')}",
        f"- USDT-settled eligible contracts: {coverage.get('active_cross_usdt_perpetual_count', '—')}",
        f"- New histories completed this run: {coverage.get('bootstrap_completed_this_run', 0)}",
        f"- Histories remaining: {coverage.get('bootstrap_remaining', '—')}",
        f"- API failures: {coverage.get('api_failure_count', '—')}",
        f"- Latest completed daily bar (UTC ms): {coverage.get('latest_completed_daily_bar_ms', '—')}",
        f"- Portfolio decision status: `{coverage.get('paper_decision_status', 'UNKNOWN')}`",
        "",
        "Portfolio changes remain blocked until the full active cross-section has the required current daily history.",
        "",
    ])
    if coverage_state == "BOOTSTRAPPING":
        markdown = markdown.replace(
            "**🟢 ACTIVE · PAPER ONLY · NO LIVE ORDERS**",
            "**BOOTSTRAPPING · PAPER ONLY · NO LIVE ORDERS**",
        )
    long_preview = coverage.get("research_long_top", [])[:3]
    short_preview = coverage.get("research_short_top", [])[:3]
    preview_lines = [
        "",
        "### Provisional BAB ranking preview",
        "",
        "Not execution-approved until full-universe coverage passes.",
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
    coverage_note += "\n".join(preview_lines) + "\n"
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
