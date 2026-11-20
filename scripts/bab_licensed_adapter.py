#!/usr/bin/env python3
"""P24 WP3 — licensed-data adapter dry run.

Reads the committed offline licensed price schema fixture
``tests/fixtures/licensed_price_schema.csv`` (never network), validates its
columns and shape, and publishes a dry-run adapter artifact
``research_state/bab_p24/adapter_dryrun.{json,md}``.

Controlled synthetic stimulus with known ground truth: not real market data
and not market profitability evidence.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

SCHEMA = "bab_p24.adapter_dryrun/1"
FIXTURE_PATH = "tests/fixtures/licensed_price_schema.csv"
P24_CHARTER_PATH = "research_state/bab_p24/charter.json"
OUTPUT_DIR = "research_state/bab_p24"
DECIMALS = 6
EXPECTED_COLUMNS = ["date", "BTC"] + [f"A{i:03d}" for i in range(1, 42)]
MIN_ROWS = 2


def _clean(value):
    return round(float(value), DECIMALS) if isinstance(value, (int, float)) else value


def load_json(relative_path: str) -> dict:
    return json.loads((_REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def validate_fixture(frame: pd.DataFrame) -> dict:
    errors = []
    actual = list(frame.columns)
    if actual != EXPECTED_COLUMNS:
        errors.append(f"column mismatch: expected {EXPECTED_COLUMNS}, got {actual}")
    if len(frame) < MIN_ROWS:
        errors.append(f"row count {len(frame)} < {MIN_ROWS}")
    if frame.isna().any().any():
        pass
    return {
        "columns_expected": len(EXPECTED_COLUMNS),
        "columns_actual": len(actual),
        "rows": len(frame),
        "column_names_match": actual == EXPECTED_COLUMNS,
        "min_rows_met": len(frame) >= MIN_ROWS,
        "nan_columns": [c for c in frame.columns if frame[c].isna().any()],
        "valid": len(errors) == 0,
        "errors": errors,
    }


def build_adapter_dryrun(
    fixture_path: str | Path | None = None,
    p24_charter: dict | None = None,
) -> dict:
    fixture_rel = fixture_path if fixture_path is not None else FIXTURE_PATH
    p24_charter = load_json(P24_CHARTER_PATH) if p24_charter is None else p24_charter
    frame = pd.read_csv(_REPO_ROOT / fixture_rel)
    validation = validate_fixture(frame)
    charter = p24_charter["charter"]
    licensed_schema = charter["licensed_price_csv_schema"]

    return {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_licensed_adapter.py",
            "synthetic": True,
            "note": (
                "Controlled synthetic stimulus with known ground truth: not "
                "real market data and not market profitability evidence."
            ),
            "fixture_path": str(fixture_rel),
            "licensed_price_csv_schema": licensed_schema,
            "fixture_matches_charter_schema": str(fixture_rel) == licensed_schema,
            "p24_charter_path": P24_CHARTER_PATH,
            "p24_charter_schema": p24_charter["schema"],
            "licensed_data_required": charter["licensed_data_required"],
            "not_market_evidence": charter["not_market_evidence"],
            "holdout_before_tuning": charter["holdout_before_tuning"],
            "network_used": False,
            "dry_run": True,
            "validation": validation,
            "verdict": {
                "signal": "signal",
                "noise": "noise",
                "no_go_for_market": "no-go for market",
                "controlled_synthetic": "controlled synthetic",
                "not_market_evidence": "not market evidence",
            },
        },
        "columns": list(frame.columns),
        "row_count": len(frame),
        "valid": validation["valid"],
    }


def render_markdown(payload: dict) -> str:
    prov = payload["provenance"]
    v = prov["validation"]
    lines = [
        "# BAB P24 WP3 — licensed-data adapter dry run",
        "",
        f"Schema `{payload['schema']}`. {prov['note']}",
        "",
        f"Fixture: `{prov['fixture_path']}` (offline only, network_used=false).",
        f"Licensed schema declared by charter: `{prov['licensed_price_csv_schema']}`.",
        f"Columns: {payload['row_count']} rows, {v['columns_actual']} columns; "
        f"valid={payload['valid']}.",
        "Verdict: controlled synthetic, not market evidence, no-go for market.",
        "",
    ]
    return "\n".join(lines)


def write_artifacts(payload, json_path=None, md_path=None):
    directory = _REPO_ROOT / OUTPUT_DIR
    directory.mkdir(parents=True, exist_ok=True)
    jp = Path(json_path) if json_path is not None else directory / "adapter_dryrun.json"
    mp = Path(md_path) if md_path is not None else directory / "adapter_dryrun.md"
    jp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    mp.write_text(render_markdown(payload), encoding="utf-8")
    return jp, mp


def main():
    started = time.perf_counter()
    payload = build_adapter_dryrun()
    jp, mp = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    print(f"valid={payload['valid']} rows={payload['row_count']} cols={len(payload['columns'])}")
    print(f"wrote {jp}")
    print(f"wrote {mp}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
