#!/usr/bin/env python3
"""P24 WP0 charter."""
from __future__ import annotations

import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "bab_p24.charter/1"
OUTPUT_DIR = "research_state/bab_p24"
KICKOFF_PATH = "docs/BAB_P24_KICKOFF.md"

def _load_json(path):
    p = Path(path)
    if not p.is_absolute():
        p = _REPO_ROOT / p
    return json.loads(p.read_text(encoding="utf-8"))

def build_charter():
    p23 = _load_json("research_state/bab_p23/charter.json")
    payload = {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_p24_charter.py",
            "synthetic": True,
            "note": "Controlled synthetic stimulus: not real market data.",
            "p23_source_schema": p23["schema"],
            "universe_seed": p23["provenance"]["universe_seed"],
            "no_go_for_market": True,
            "licensed_data_required": True,
        },
        "charter": {
            "campaign": "P24",
            "title": "Regime-conditional BAB and holdout discipline",
            "binding_row": "P24 WP0",
            "artifact_gated": True,
            "not_market_evidence": True,
            "licensed_data_required": True,
            "regime_grid": ["calm", "stress"],
            "holdout_before_tuning": True,
            "hysteresis_band_grid": [0.05, 0.10, 0.15],
            "licensed_price_csv_schema": "tests/fixtures/licensed_price_schema.csv",
            "wps_in_order": ["P24 WP0 — charter"],
        },
        "provenance": {
            "generator": "scripts/bab_p24_charter.py",
            "synthetic": True,
            "note": "Controlled synthetic stimulus: not real market data.",
            "p23_source_schema": p23["schema"],
            "universe_seed": p23["provenance"]["universe_seed"],
            "no_go_for_market": True,
            "licensed_data_required": True,
            "acceptance_thresholds": {
                "nominal_slack": 0.05,
                "wp4": {
                    "explicit_signal_noise_verdict": True,
                    "no_go_for_market": True,
                    "no_harness_re_run": True,
                    "planted_recovery_labelled_controlled_synthetic": True,
                    "numbers_matched_min": 100,
                    "zero_unmatched_cells": 0,
                    "regime_grid_min": 2,
                    "hysteresis_band_grid_min": 3,
                    "turnover_monotone_non_increasing": True,
                    "adapter_valid_offline": True,
                },
            },
        },
    }
    return payload

def render_markdown(payload):
    return "# BAB P24 WP0\n\n" + json.dumps(payload, indent=2) + "\n"

def write_artifacts(payload, output_dir=OUTPUT_DIR):
    d = Path(output_dir)
    if not d.is_absolute():
        d = _REPO_ROOT / d
    d.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    (d/"charter.json").write_text(text, encoding="utf-8")
    md = render_markdown(payload)
    (d/"charter.md").write_text(md, encoding="utf-8")
    (_REPO_ROOT/KICKOFF_PATH).write_text(md, encoding="utf-8")
    return d/"charter.json", d/"charter.md", _REPO_ROOT/KICKOFF_PATH

def main():
    payload = build_charter()
    write_artifacts(payload)
    print("P24 WP0 charter written")

if __name__ == "__main__":
    main()
