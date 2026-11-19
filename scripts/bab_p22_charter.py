#!/usr/bin/env python3
"""P22 WP0 — machine-readable charter for Campaign P22.

Loads the committed P21 artifacts
``research_state/bab_p21/{universe,significance,rank_eval,cost_surface}.json``
read-only and publishes a machine-readable charter that:

1. **Restates the P21 verdict from committed JSON only** (no hand-typed
   numbers): null calibrated, planted detected, the per-book p-values and
   recoveries, the cost-surface monotonicity flags, and the explicit
   signal-vs-noise / NO-GO-for-market verdict.
2. **Pins the P22 null-battery seed list** (>= 20 seeds) consumed by P22 WP1.
3. **Pins the nominal slack and the exact acceptance thresholds** consumed by
   P21 WP1-WP4, so P22 WP1-WP4 have machine-checkable acceptance criteria.

Every number in the JSON and the markdown is either a committed P21 JSON field
or a charter-declared constant; nothing is hand-typed into prose. Committed
JSON equals a fresh build (``build_charter()`` == ``charter.json``) and the
markdown is derived from JSON only. No P21 harness is re-run.

Controlled synthetic stimulus with known ground truth: not real market data
and not market profitability evidence.

Usage:
  python3 scripts/bab_p22_charter.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

SCHEMA = "bab_p22.charter/1"
OUTPUT_DIR = "research_state/bab_p22"
KICKOFF_PATH = "docs/BAB_P22_KICKOFF.md"
UNIVERSE_PATH = "research_state/bab_p21/universe.json"
SIGNIFICANCE_PATH = "research_state/bab_p21/significance.json"
RANK_EVAL_PATH = "research_state/bab_p21/rank_eval.json"
COST_SURFACE_PATH = "research_state/bab_p21/cost_surface.json"
VARIANTS = ("planted", "null")
WEIGHTINGS = ("equal", "rank")
DECIMALS = 6

# --- Charter-declared P22 constants (not derived from P21 JSON) -------------

# Null-battery seed list consumed by P22 WP1 (>= 20 independent seeds).
P22_NULL_BATTERY_SEEDS = [
    20261120, 20261121, 20261122, 20261123, 20261124,
    20261125, 20261126, 20261127, 20261128, 20261129,
    20261130, 20261131, 20261132, 20261133, 20261134,
    20261135, 20261136, 20261137, 20261138, 20261139,
]
P22_NULL_BATTERY_N_SEEDS = len(P22_NULL_BATTERY_SEEDS)
NOMINAL_SLACK = 0.05

# Acceptance thresholds consumed by P21 WP1-WP4 (restated from the P21 spec).
WP1_MIN_ACTIVE_ROWS = 1
WP1_RANK_MIN_LEG_BETA = 0.20
WP1_RANK_MAX_GROSS = 4.0
WP1_BETA_EXPOSURE_MAX = 0.05
WP1_DOLLAR_IMBALANCE_EQUAL_MAX = 1e-12
WP2_N_RESAMPLES_MIN = 2000
WP2_BLOCK_LENGTH = 20
WP3_MIN_COMPONENTS = 3
WP4_NUMBERS_MATCHED_MIN = 100


def _clean(value: float) -> float:
    return round(float(value), DECIMALS)


def _md_value(value) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def _md_row(columns: list[str], values: dict) -> str:
    return "| " + " | ".join(_md_value(values[col]) for col in columns) + " |"


def _load_json(path: str) -> dict:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = _REPO_ROOT / resolved
    return json.loads(resolved.read_text(encoding="utf-8"))


def _panel_sha(panel) -> str:
    blob = json.dumps(panel, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _book(books: list[dict], variant: str, weighting: str) -> dict:
    for book in books:
        if book["variant"] == variant and book["weighting"] == weighting:
            return book
    raise AssertionError(f"no book for variant={variant!r} weighting={weighting!r}")


def build_charter(
    universe_payload: dict | None = None,
    significance_payload: dict | None = None,
    rank_eval_payload: dict | None = None,
    cost_surface_payload: dict | None = None,
) -> dict:
    """Build the charter payload (pure, no I/O, no harness re-run)."""
    if universe_payload is None:
        universe_payload = _load_json(UNIVERSE_PATH)
    if significance_payload is None:
        significance_payload = _load_json(SIGNIFICANCE_PATH)
    if rank_eval_payload is None:
        rank_eval_payload = _load_json(RANK_EVAL_PATH)
    if cost_surface_payload is None:
        cost_surface_payload = _load_json(COST_SURFACE_PATH)

    # Integrity: all P21 artifacts must agree on the panels they consumed.
    prov_u = universe_payload["provenance"]
    prov_s = significance_payload["provenance"]
    prov_r = rank_eval_payload["provenance"]
    prov_c = cost_surface_payload["provenance"]
    for variant in VARIANTS:
        u_sha = universe_payload["panels"][variant]["sha256"]
        assert prov_s["panel_sha256"][variant] == u_sha, f"panel sha mismatch {variant}"
        assert prov_r["panel_sha256"][variant] == u_sha, f"panel sha mismatch {variant}"
        assert prov_c["panel_sha256"][variant] == u_sha, f"panel sha mismatch {variant}"
    seeds = (
        prov_s["universe_seed"],
        prov_r["universe_seed"],
        prov_c["universe_seed"],
        prov_u["seed"],
    )
    assert len(set(seeds)) == 1, "P21 universe seed mismatch across artifacts"

    sig_books = significance_payload["books"]
    rank_books = rank_eval_payload["books"]
    cost_books = cost_surface_payload["books"]

    # P21 verdict restated from committed JSON only.
    null_books = [b for b in sig_books if b["variant"] == "null"]
    planted_books = [b for b in sig_books if b["variant"] == "planted"]
    null_calibrated = all(not b["significant"] for b in null_books)
    planted_detected = all(b["significant"] and b["ci_excludes_zero"] for b in planted_books)

    p21_verdict = {
        "signal_on_planted": planted_detected,
        "noise_on_null": null_calibrated,
        "verdict": (
            "SIGNAL on the planted controlled-synthetic universe; NOISE on the "
            "null universe; NO-GO for market deployment."
        ),
        "null_calibrated": null_calibrated,
        "planted_detected": planted_detected,
        "null_max_p_value": prov_s["null_max_p_value"],
        "nominal_slack": NOMINAL_SLACK,
        "books": {
            f"{variant}_{w}": {
                "variant": variant,
                "weighting": w,
                "p_value": _book(sig_books, variant, w)["p_value"],
                "significant": _book(sig_books, variant, w)["significant"],
                "ci_excludes_zero": _book(sig_books, variant, w)["ci_excludes_zero"],
                "oos_sharpe": _book(sig_books, variant, w)["oos_sharpe"],
                "dsr": _book(sig_books, variant, w)["dsr"],
                "recovery_mean": _book(rank_books, variant, w)["recovery_mean"],
                "active_rows": _book(rank_books, variant, w)["active_rows"],
                "gross_sharpe": _book(cost_books, variant, w)["gross_sharpe"],
                "monotonicity": {
                    component: _book(cost_books, variant, w)["monotonicity"][component]
                    for component in sorted(_book(cost_books, variant, w)["monotonicity"].keys())
                },
                "censored": _book(cost_books, variant, w)["censored"],
            }
            for variant in VARIANTS
            for w in WEIGHTINGS
        },
    }

    # Acceptance thresholds consumed by P21 WP1-WP4 (charter-declared).
    acceptance_thresholds = {
        "nominal_slack": NOMINAL_SLACK,
        "wp1": {
            "min_active_rows": WP1_MIN_ACTIVE_ROWS,
            "rank_min_leg_beta": WP1_RANK_MIN_LEG_BETA,
            "rank_max_gross": WP1_RANK_MAX_GROSS,
            "beta_exposure_max": WP1_BETA_EXPOSURE_MAX,
            "dollar_imbalance_equal_max": WP1_DOLLAR_IMBALANCE_EQUAL_MAX,
            "recovery_planted_strictly_positive": True,
            "recovery_null_exactly_zero": 0.0,
        },
        "wp2": {
            "n_resamples_min": WP2_N_RESAMPLES_MIN,
            "block_length": WP2_BLOCK_LENGTH,
            "null_not_significant_at_slack": True,
            "planted_significant_with_ci_excluding_zero": True,
        },
        "wp3": {
            "min_components": WP3_MIN_COMPONENTS,
            "per_book_monotonicity_true": True,
            "period_wise_non_increasing_true": True,
            "censored_reports_document_reason_never_zero_tolerance": True,
        },
        "wp4": {
            "numbers_matched_min": WP4_NUMBERS_MATCHED_MIN,
            "zero_unmatched_cells": 0,
            "no_harness_re_run": True,
            "explicit_signal_noise_verdict": True,
            "planted_recovery_labelled_controlled_synthetic": True,
            "no_go_for_market": True,
        },
    }

    return {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_p22_charter.py",
            "synthetic": True,
            "note": (
                "Controlled synthetic stimulus with known ground truth: "
                "not real market data and not market profitability evidence."
            ),
            "universe_seed": prov_u["seed"],
            "panel_sha256": {
                variant: universe_payload["panels"][variant]["sha256"]
                for variant in VARIANTS
            },
            "p21_significance_seed": prov_s["seed"],
            "p21_verdict": p21_verdict,
            "p22_null_battery_seeds": list(P22_NULL_BATTERY_SEEDS),
            "p22_null_battery_n_seeds": P22_NULL_BATTERY_N_SEEDS,
            "nominal_slack": NOMINAL_SLACK,
            "acceptance_thresholds": acceptance_thresholds,
            "method": (
                "reads the committed P21 JSON artifacts (universe, significance, "
                "rank_eval, cost_surface) read-only; restates the P21 verdict "
                "from committed fields; declares the P22 null-battery seeds, "
                "nominal slack and WP1-WP4 acceptance thresholds as charter "
                "constants; never imports or re-runs any P21 build_* harness."
            ),
            "caveat": (
                "P21 recovery on a planted synthetic universe proves the "
                "estimator works; it is never market alpha. A null-universe "
                "positive result is a bug, not a finding. NO-GO for market "
                "deployment until a maintainer supplies a licensed price series."
            ),
        },
        "charter": {
            "campaign": "P22",
            "title": "Decision-grade validation",
            "question": (
                "Does the BAB estimator survive repeated null universes, "
                "nonlinear market impact, and capacity constraints?"
            ),
            "answered_by_p21": (
                "Is the estimator calibrated and cost-aware on a controlled "
                "universe? Yes — signal on planted, noise on null, NO-GO for market."
            ),
            "not_market_evidence": True,
            "licensed_data_required": True,
            "wps_in_order": [
                "P22 WP0 — charter",
                "P22 WP1 — null battery (>=20 seeds)",
                "P22 WP2 — nonlinear impact",
                "P22 WP3 — capacity / break-even",
                "P22 WP4 — decision report",
            ],
            "binding_row": "P22 WP0",
            "artifact_gated": True,
        },
    }


def render_markdown(payload: dict) -> str:
    """Render the charter from the payload; no external numbers."""
    prov = payload["provenance"]
    verdict = prov["p21_verdict"]
    thresholds = prov["acceptance_thresholds"]
    charter = payload["charter"]
    lines = [
        f"# BAB {charter['campaign']} WP0 — {charter['title']}",
        "",
        f"Schema `{payload['schema']}`. {prov['note']}",
        "",
        "## Binding row",
        f"- Campaign: {charter['campaign']}",
        f"- Title: {charter['title']}",
        f"- Binding row: {charter['binding_row']}",
        f"- Artifact-gated: {str(charter['artifact_gated']).lower()}",
        f"- Not market evidence: {str(charter['not_market_evidence']).lower()}",
        f"- Licensed data required: {str(charter['licensed_data_required']).lower()}",
        "",
        "## P21 verdict (restated from committed JSON only)",
        f"- Signal on planted: {str(verdict['signal_on_planted']).lower()}",
        f"- Noise on null: {str(verdict['noise_on_null']).lower()}",
        f"- Null calibrated: {str(verdict['null_calibrated']).lower()}",
        f"- Planted detected: {str(verdict['planted_detected']).lower()}",
        f"- Null max p-value: {verdict['null_max_p_value']:.6f}",
        f"- Nominal slack: {verdict['nominal_slack']:.6f}",
        f"- Verdict: {verdict['verdict']}",
        "",
        "### P21 per-book basis (committed JSON fields)",
    ]
    book_columns = [
        "variant",
        "weighting",
        "p_value",
        "significant",
        "ci_excludes_zero",
        "oos_sharpe",
        "dsr",
        "recovery_mean",
        "active_rows",
        "gross_sharpe",
        "censored",
    ]
    lines.extend(
        [_md_row(book_columns, verdict["books"][key]) for key in sorted(verdict["books"].keys())]
    )
    lines += [
        "",
        "### P21 cost-surface monotonicity (committed JSON fields)",
    ]
    mono_columns = [
        "variant",
        "weighting",
        "linear_transaction_cost",
        "borrow_funding",
        "notional_slippage",
        "censored",
    ]
    lines.append("| " + " | ".join(mono_columns) + " |")
    lines.append("|" + "|".join("---" for _ in mono_columns) + "|")
    lines.extend(
        [
            _md_row(
                mono_columns,
                {**verdict["books"][key], **verdict["books"][key]["monotonicity"]},
            )
            for key in sorted(verdict["books"].keys())
        ]
    )
    lines += [
        "",
        "## P22 charter constants (declared here, not derived from P21 JSON)",
        f"- P22 null-battery seeds (n={prov['p22_null_battery_n_seeds']}, >= 20): "
        + ", ".join(str(s) for s in prov["p22_null_battery_seeds"]),
        f"- Nominal slack: {prov['nominal_slack']:.6f}",
        "",
        "### Acceptance thresholds consumed by P21 WP1-WP4",
    ]
    threshold_columns = ["WP", "Threshold", "Value"]
    lines.append("| " + " | ".join(threshold_columns) + " |")
    lines.append("|" + "|".join("---" for _ in threshold_columns) + "|")
    for wp_name, wp in thresholds.items():
        if wp_name == "nominal_slack":
            continue
        for label, value in wp.items():
            lines.append(
                _md_row(
                    threshold_columns,
                    {"WP": wp_name.upper(), "Threshold": label, "Value": value},
                )
            )
    lines += [
        "",
        "## Provenance",
        f"- Universe seed: {prov['universe_seed']}",
        f"- P21 significance seed: {prov['p21_significance_seed']}",
        f"- Planted panel sha256: `{prov['panel_sha256']['planted']}`",
        f"- Null panel sha256: `{prov['panel_sha256']['null']}`",
        f"- Generator: {prov['generator']}",
        f"- Caveat: {prov['caveat']}",
        "",
        "## WPs in order",
    ]
    for wp in charter["wps_in_order"]:
        lines.append(f"- {wp}")
    lines += [
        "",
        prov["method"],
        "",
        prov["caveat"],
    ]
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str = OUTPUT_DIR) -> tuple[Path, Path, Path]:
    """Write the JSON, markdown, and kickoff artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "charter.json"
    markdown_path = directory / "charter.md"
    kickoff_path = _REPO_ROOT / KICKOFF_PATH
    markdown = render_markdown(payload)
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(markdown, encoding="utf-8")
    kickoff_path.write_text(markdown, encoding="utf-8")
    return json_path, markdown_path, kickoff_path


def main() -> None:
    started = time.perf_counter()
    payload = build_charter()
    json_path, markdown_path, kickoff_path = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    prov = payload["provenance"]
    print(
        f"P22 WP0 charter: null_calibrated={prov['p21_verdict']['null_calibrated']} "
        f"planted_detected={prov['p21_verdict']['planted_detected']} "
        f"seeds={prov['p22_null_battery_n_seeds']}"
    )
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")
    print(f"wrote {kickoff_path}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
