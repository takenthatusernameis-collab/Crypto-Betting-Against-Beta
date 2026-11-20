#!/usr/bin/env python3
"""P24 WP3 — licensed-data adapter dry run.

Reads the committed offline licensed price schema fixture
``tests/fixtures/licensed_price_schema.csv`` (never network), validates its
columns, shape and numeric contract against the committed P21 universe and the
P24/P23 charters, and publishes a dry-run adapter artifact
``research_state/bab_p24/adapter_dryrun.{json,md}``.

The fixture is a schema-shaped stand-in, not a price history: the universe
columns (``A001``..``A041``) and the benchmark column (``BTC``) are taken from
committed P21 JSON, so the adapter proves the licensed schema is consumable
before any licensed series exists. Controlled synthetic stimulus with known
ground truth: not real market data and not market profitability evidence.
"""

from __future__ import annotations

import hashlib
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
P21_UNIVERSE_PATH = "research_state/bab_p21/universe.json"
P23_CHARTER_PATH = "research_state/bab_p23/charter.json"
P24_CHARTER_PATH = "research_state/bab_p24/charter.json"
OUTPUT_DIR = "research_state/bab_p24"
DECIMALS = 6
MIN_ROWS = 2
DATE_COLUMN = "date"


def _clean(value):
    return round(float(value), DECIMALS) if isinstance(value, (int, float)) else value


def load_json(relative_path: str) -> dict:
    return json.loads((_REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def file_sha256(relative_path: str) -> str:
    return hashlib.sha256((_REPO_ROOT / relative_path).read_bytes()).hexdigest()


def expected_columns(universe: dict) -> list[str]:
    provenance = universe["provenance"]
    assets = list(universe["assets"])
    if len(assets) != provenance["assets"]:
        raise ValueError(
            f"committed P21 universe declares {provenance['assets']} assets "
            f"but lists {len(assets)}"
        )
    return [DATE_COLUMN, provenance["benchmark"], *assets]


def _numeric_columns(frame: pd.DataFrame) -> list[str]:
    bad = []
    for column in frame.columns:
        if column == DATE_COLUMN:
            continue
        coerced = pd.to_numeric(frame[column], errors="coerce")
        if coerced.isna().any():
            bad.append(column)
    return bad


def validate_fixture(frame: pd.DataFrame, universe: dict) -> dict:
    expected = expected_columns(universe)
    actual = list(frame.columns)
    parsed_dates = pd.to_datetime(frame[DATE_COLUMN], errors="coerce")
    dates = [value.strftime("%Y-%m-%d") for value in parsed_dates.dropna()]
    errors: list[str] = []

    if actual != expected:
        errors.append(f"column mismatch: expected {expected}, got {actual}")
    if len(frame) < MIN_ROWS:
        errors.append(f"row count {len(frame)} < {MIN_ROWS}")

    nan_columns = [column for column in frame.columns if frame[column].isna().any()]
    if nan_columns:
        errors.append(f"missing cells in columns: {nan_columns}")

    non_numeric_columns = _numeric_columns(frame)
    if non_numeric_columns:
        errors.append(f"non-numeric columns: {non_numeric_columns}")

    if len(dates) != len(frame):
        errors.append(f"unparseable dates in column {DATE_COLUMN!r}")
    elif len(set(dates)) != len(dates):
        errors.append(f"duplicate dates in column {DATE_COLUMN!r}")
    elif dates != sorted(dates):
        errors.append(f"dates in column {DATE_COLUMN!r} are not increasing")

    non_positive = [
        column
        for column in frame.columns
        if column != DATE_COLUMN
        and (pd.to_numeric(frame[column], errors="coerce") <= 0).any()
    ]
    if non_positive:
        errors.append(f"non-positive prices in columns: {non_positive}")

    provenance = universe["provenance"]
    date_start_matches = bool(dates) and dates[0] == provenance["date_start"]
    if not date_start_matches:
        errors.append(
            f"fixture starts at {dates[0] if dates else None!r}, "
            f"committed P21 universe starts at {provenance['date_start']!r}"
        )

    return {
        "columns_expected": len(expected),
        "columns_actual": len(actual),
        "rows": len(frame),
        "column_names_match": actual == expected,
        "min_rows_met": len(frame) >= MIN_ROWS,
        "nan_columns": nan_columns,
        "non_numeric_columns": non_numeric_columns,
        "date_start": dates[0] if dates else None,
        "date_start_matches_universe": date_start_matches,
        "dates_strictly_increasing": len(dates) == len(frame) and dates == sorted(dates),
        "non_positive_columns": non_positive,
        "valid": len(errors) == 0,
        "errors": errors,
    }


def build_adapter_dryrun(
    fixture_path: str | Path | None = None,
    p24_charter: dict | None = None,
    p21_universe: dict | None = None,
) -> dict:
    fixture_rel = fixture_path if fixture_path is not None else FIXTURE_PATH
    p24_charter = load_json(P24_CHARTER_PATH) if p24_charter is None else p24_charter
    p21_universe = load_json(P21_UNIVERSE_PATH) if p21_universe is None else p21_universe
    p23_charter = load_json(P23_CHARTER_PATH)

    charter = p24_charter["charter"]
    licensed_schema = charter["licensed_price_csv_schema"]
    universe_provenance = p21_universe["provenance"]
    validation = validate_fixture(
        pd.read_csv(_REPO_ROOT / fixture_rel), p21_universe
    )

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
            "fixture_sha256": file_sha256(str(fixture_rel)),
            "licensed_price_csv_schema": licensed_schema,
            "fixture_matches_charter_schema": str(fixture_rel) == licensed_schema,
            "p24_charter_path": P24_CHARTER_PATH,
            "p24_charter_schema": p24_charter["schema"],
            "p21_universe_path": P21_UNIVERSE_PATH,
            "p21_universe_schema": p21_universe["schema"],
            "p23_charter_path": P23_CHARTER_PATH,
            "p23_charter_schema": p23_charter["schema"],
            "licensed_data_required": charter["licensed_data_required"],
            "holdout_before_tuning": charter["holdout_before_tuning"],
            "not_market_evidence": charter["not_market_evidence"],
            "no_go_for_market": p24_charter["provenance"]["no_go_for_market"],
            "p23_no_go_for_market": p23_charter["provenance"]["p22_verdict"][
                "no_go_for_market"
            ],
            "network_used": False,
            "dry_run": True,
            "numeric_contract": {
                "assets": universe_provenance["assets"],
                "benchmark": universe_provenance["benchmark"],
                "decimals": universe_provenance["decimals"],
                "date_start": universe_provenance["date_start"],
                "universe_seed": universe_provenance["seed"],
                "expected_columns": len(expected_columns(p21_universe)),
            },
            "validation": validation,
            "verdict": {
                "signal": "signal",
                "noise": "noise",
                "no_go_for_market": "no-go for market",
                "controlled_synthetic": "controlled synthetic",
                "not_market_evidence": "not market evidence",
            },
        },
        "columns": list(expected_columns(p21_universe)),
        "row_count": validation["rows"],
        "valid": validation["valid"],
        "errors": validation["errors"],
    }


def render_markdown(payload: dict) -> str:
    prov = payload["provenance"]
    validation = prov["validation"]
    contract = prov["numeric_contract"]
    lines = [
        "# BAB P24 WP3 — licensed-data adapter dry run",
        "",
        f"Schema `{payload['schema']}`. {prov['note']}",
        "",
        f"Fixture: `{prov['fixture_path']}` (offline only, network_used=false).",
        f"Fixture sha256: `{prov['fixture_sha256']}`.",
        f"Licensed schema declared by charter: `{prov['licensed_price_csv_schema']}`.",
        f"Universe contract: {contract['assets']} assets + `{contract['benchmark']}` "
        f"benchmark + `date` = {contract['expected_columns']} columns, "
        f"decimals {contract['decimals']}, start {contract['date_start']}.",
        f"Validated: {validation['rows']} rows, {validation['columns_actual']} columns, "
        f"valid={payload['valid']}.",
        f"Verdict: controlled synthetic, not market evidence, no-go for market "
        f"(no_go_for_market={prov['no_go_for_market']}).",
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
    print(
        f"valid={payload['valid']} rows={payload['row_count']} "
        f"cols={len(payload['columns'])}"
    )
    for error in payload["errors"]:
        print(f"error: {error}")
    print(f"wrote {jp}")
    print(f"wrote {mp}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
