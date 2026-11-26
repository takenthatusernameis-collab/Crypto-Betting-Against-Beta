#!/usr/bin/env python3
"""Publish BAB paper status and the inverse-volatility shadow equity path."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_ROOT = ROOT.parent / "engine"
sys.path.insert(0, str(ENGINE_ROOT / "src"))

from high_vs_low.market_data_store import MarketDataStore
import high_vs_low.paper_status as status

status.ACCOUNT_ID = "mexc-usdt-forward-bab-100usdt-v1"
status.STRATEGY_ID = "crypto-bab-low-beta-long-high-beta-short-v1"
status.INITIAL_CAPITAL = __import__("decimal").Decimal("100")

market_data = Path(os.environ.get("MARKET_DATA_DIR", "../market-data"))
state_dir = Path(os.environ.get("PAPER_STATE_DIR", "../state"))
store = MarketDataStore(market_data, provider="mexc")
metadata = {
    "repository": os.environ.get("GITHUB_REPOSITORY", ""),
    "server_url": os.environ.get("GITHUB_SERVER_URL", "https://github.com"),
    "run_id": os.environ.get("GITHUB_RUN_ID", ""),
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
    store.load_all_candles(),
    metadata,
    generated_at_ms=int(time.time() * 1000),
    equal_svg_path=ROOT / "equal_exposure_equity_curve.svg",
    alternative_svg_path=ROOT / "alternative_path_equity_curve.svg",
)
markdown = (
    markdown.replace("High-Low", "BAB")
    .replace("high-low-paper-cycle.yml", "bab-paper-cycle.yml")
    .replace("ATH/ATL", "BAB low-beta/high-beta")
)
(ROOT / "PAPER_STATUS.md").write_text(markdown, encoding="utf-8")
print("Published BAB paper status and both equity curves.")
