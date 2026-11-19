#!/usr/bin/env python3
"""P23 WP0 — machine-readable charter for Campaign P23.

Loads the committed P22 artifacts
``research_state/bab_p22/{charter,null_battery,impact_surface,capacity}.json``
read-only and publishes a machine-readable charter that:

1. **Restates the closed P22 verdict from committed P22 JSON only** (no
   hand-typed numbers): NO-GO for market deployment, signal on the planted
   controlled-synthetic universe, noise on the null universe, monotone
   nonlinear impact, and the capacity break-evens with documented censoring.
2. **Pins the P23 breadth-and-instability constants** consumed by WP1-WP3: the
   breadth ladder, the beta-window/drift grid, the short-availability haircut
   ladder, and >= 20 independent seeds per work package.
3. **Pins the exact acceptance thresholds** consumed by P23 WP1-WP4 so every
   later row has machine-checkable acceptance criteria.

Every number in the JSON and the markdown is either a committed P22 JSON field
or a charter-declared constant. Committed JSON equals a fresh build
(``build_charter()`` == ``charter.json``) and the markdown is derived from JSON
only. No P22 harness is imported or re-run, and no P22 artifact is written.

Controlled synthetic stimulus with known ground truth: not real market data and
not market profitability evidence.

Usage:
  python3 scripts/bab_p23_charter.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

SCHEMA = "bab_p23.charter/1"
OUTPUT_DIR = "research_state/bab_p23"
KICKOFF_PATH = "docs/BAB_P23_KICKOFF.md"
P22_CHARTER_PATH = "research_state/bab_p22/charter.json"
P22_NULL_BATTERY_PATH = "research_state/bab_p22/null_battery.json"
P22_IMPACT_SURFACE_PATH = "research_state/bab_p22/impact_surface.json"
P22_CAPACITY_PATH = "research_state/bab_p22/capacity.json"
VARIANTS = ("planted", "null")
WEIGHTINGS = ("equal", "rank")
DECIMALS = 6

# --- Charter-declared P23 constants (not derived from P22 JSON) -------------
# Every later P23 work package consumes these lists; none may be re-declared.

P23_BREADTH_LADDER = [9, 17, 25, 33, 41]
P23_BETA_WINDOW_GRID = [60, 90, 120, 180]
P23_DRIFT_THRESHOLD_GRID = [1e-4, 5e-4, 1e-3]
P23_BORROW_HAIRCUT_LADDER = [0.0, 0.10, 0.25, 0.50, 0.75]

P23_WP1_SEEDS = [
    20261201, 20261202, 20261203, 20261204, 20261205,
    20261206, 20261207, 20261208, 20261209, 20261210,
    20261211, 20261212, 20261213, 20261214, 20261215,
    20261216, 20261217, 20261218, 20261219, 20261220,
]
P23_WP2_SEEDS = [
    20261221, 20261222, 20261223, 20261224, 20261225,
    20261226, 20261227, 20261228, 20261229, 20261230,
    20261231, 20261232, 20261233, 20261234, 20261235,
    20261236, 20261237, 20261238, 20261239, 20261240,
]
P23_WP3_SEEDS = [
    20261241, 20261242, 20261243, 20261244, 20261245,
    20261246, 20261247, 20261248, 20261249, 20261250,
    20261251, 20261252, 20261253, 20261254, 20261255,
    20261256, 20261257, 20261258, 20261259, 20261260,
]

NOMINAL_SLACK = 0.05
P23_MIN_RUNGS = 3
P23_MIN_SEEDS = 20
P23_NUMBERS_MATCHED_MIN = 100


def _md_value(value) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def _md_row(columns: list, values: dict) -> str:
    return "| " + " | ".join(_md_value(values[col]) for col in columns) + " |"


def _md_table(name: str, columns: list, rows: list) -> list:
    lines = [
        f"<!-- table:{name}:start -->",
        "| " + " | ".join(columns) + " |",
        "|" + "|".join("---" for _ in columns) + "|",
    ]
    lines.extend(_md_row(columns, row) for row in rows)
    lines.append(f"<!-- table:{name}:end -->")
    return lines


def _load_json(path: str) -> dict:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = _REPO_ROOT / resolved
    return json.loads(resolved.read_text(encoding="utf-8"))


def _book(books: list, variant: str, weighting: str) -> dict:
    for book in books:
        if book["variant"] == variant and book["weighting"] == weighting:
            return book
    raise AssertionError(f"no book for variant={variant!r} weighting={weighting!r}")


def build_charter(
    p22_charter: dict | None = None,
    null_battery: dict | None = None,
    impact_surface: dict | None = None,
    capacity: dict | None = None,
) -> dict:
    """Build the P23 charter payload (pure, no I/O, no harness re-run)."""
    if p22_charter is None:
        p22_charter = _load_json(P22_CHARTER_PATH)
    if null_battery is None:
        null_battery = _load_json(P22_NULL_BATTERY_PATH)
    if impact_surface is None:
        impact_surface = _load_json(P22_IMPACT_SURFACE_PATH)
    if capacity is None:
        capacity = _load_json(P22_CAPACITY_PATH)

    # Integrity: all four P22 artifacts must agree on the pinned panels.
    charter_shas = p22_charter["provenance"]["panel_sha256"]
    for variant in VARIANTS:
        assert null_battery["provenance"]["committed_p21_panel_sha256"][variant] == (
            charter_shas[variant]
        ), f"null battery panel sha mismatch {variant}"
        assert impact_surface["provenance"]["panel_sha256"][variant] == (
            charter_shas[variant]
        ), f"impact surface panel sha mismatch {variant}"
        assert capacity["provenance"]["panel_sha256"][variant] == (
            charter_shas[variant]
        ), f"capacity panel sha mismatch {variant}"
    seeds = (
        p22_charter["provenance"]["universe_seed"],
        null_battery["provenance"]["reference_universe_seed"],
        impact_surface["provenance"]["universe_seed"],
        capacity["provenance"]["universe_seed"],
    )
    assert len(set(seeds)) == 1, "P22 universe seed mismatch across artifacts"
    assert null_battery["provenance"]["reference_panel_sha256_matched"] is True

    nb_summary = null_battery["provenance"]["summary"]
    config = impact_surface["provenance"]["config"]
    p21_verdict = p22_charter["provenance"]["p21_verdict"]

    # P22 verdict restated from committed P22 JSON only (no hand-typed numbers).
    signal_on_planted = (
        nb_summary["planted_recovery_positive_fraction"]["equal"] == 1.0
        and nb_summary["planted_recovery_positive_fraction"]["rank"] == 1.0
        and nb_summary["planted_recovery_exceeds_null_max"] is True
    )
    noise_on_null = (
        nb_summary["null_recovery_max_abs"] == 0.0
        and nb_summary["null_recovery_exactly_zero_every_seed"] is True
    )
    no_go_for_market = "NO-GO for market deployment" in p21_verdict["verdict"]
    assert signal_on_planted, "P22 planted-signal evidence drifted"
    assert noise_on_null, "P22 null-calibration evidence drifted"
    assert no_go_for_market, "P22 NO-GO verdict drifted"

    impact_books = {
        f"{variant}_{w}": {
            "variant": variant,
            "weighting": w,
            "monotone": _book(impact_surface["books"], variant, w)["monotonicity"][
                "market_impact"
            ],
            "period_wise_non_increasing": _book(
                impact_surface["books"], variant, w
            )["period_wise_non_increasing"]["market_impact"],
            "gross_sharpe": _book(impact_surface["books"], variant, w)["gross_sharpe"],
        }
        for variant in VARIANTS
        for w in WEIGHTINGS
    }
    assert all(book["monotone"] for book in impact_books.values()), "impact drifted"
    assert all(
        book["period_wise_non_increasing"] for book in impact_books.values()
    ), "impact period monotonicity drifted"

    capacity_books = {}
    for variant in VARIANTS:
        for w in WEIGHTINGS:
            book = _book(capacity["books"], variant, w)
            if book["censored"]:
                assert book["censor_reason"], "censored book without a documented reason"
                assert book["break_even_coefficient"] is None
            else:
                assert book["bracket_halving_verified"] is True
                assert book["break_even_coefficient"] is not None
            capacity_books[f"{variant}_{w}"] = {
                "variant": variant,
                "weighting": w,
                "gross_sharpe": book["gross_sharpe"],
                "break_even_coefficient": book["break_even_coefficient"],
                "censored": book["censored"],
                "censor_reason": book["censor_reason"],
                "bracket_halving_verified": book["bracket_halving_verified"],
            }

    p22_verdict = {
        "verdict": (
            "NO-GO for market deployment"
            if no_go_for_market
            else "UNRESOLVED — P22 evidence no longer supports NO-GO"
        ),
        "no_go_for_market": no_go_for_market,
        "signal_on_planted": signal_on_planted,
        "noise_on_null": noise_on_null,
        "p22_charter_verdict": p21_verdict["verdict"],
        "nominal_slack": p22_charter["provenance"]["nominal_slack"],
        "null_battery": {
            "n_seeds": nb_summary["n_seeds"],
            "n_null_books": nb_summary["n_null_books"],
            "n_planted_books": nb_summary["n_planted_books"],
            "null_recovery_max_abs": nb_summary["null_recovery_max_abs"],
            "null_recovery_zero_books": nb_summary["null_recovery_zero_books"],
            "null_recovery_exactly_zero_every_seed": nb_summary[
                "null_recovery_exactly_zero_every_seed"
            ],
            "fpr_count": nb_summary["fpr_count"],
            "fpr_denominator": nb_summary["fpr_denominator"],
            "fpr_rate": nb_summary["fpr_rate"],
            "fpr_max_count_declared": nb_summary["fpr_max_count_declared"],
            "fpr_within_declared_bound": nb_summary["fpr_within_declared_bound"],
            "planted_recovery_min": nb_summary["planted_recovery_min"],
            "planted_recovery_positive_fraction": nb_summary[
                "planted_recovery_positive_fraction"
            ],
            "planted_recovery_exceeds_null_max": nb_summary[
                "planted_recovery_exceeds_null_max"
            ],
            "null_sharpe_max": nb_summary["null_sharpe_max"],
            "planted_sharpe_min": nb_summary["planted_sharpe_min"],
        },
        "impact": impact_books,
        "capacity": capacity_books,
    }

    # Shipped strategy defaults, read from the committed P22 impact config.
    strategy_config = {
        "benchmark": config["benchmark"],
        "beta_neutral": config["beta_neutral"],
        "beta_window": config["beta_window"],
        "min_observations": config["min_observations"],
        "long_quantile": config["long_quantile"],
        "short_quantile": config["short_quantile"],
        "rank_min_leg_beta": config["rank_min_leg_beta"],
        "rank_max_gross": config["rank_max_gross"],
    }

    wp_seeds = {
        "wp1": list(P23_WP1_SEEDS),
        "wp2": list(P23_WP2_SEEDS),
        "wp3": list(P23_WP3_SEEDS),
    }
    wp_seed_counts = {name: len(seeds) for name, seeds in wp_seeds.items()}

    # Acceptance thresholds consumed by P23 WP1-WP4 (charter-declared; the
    # strategy defaults are the committed P22 config values, never widened).
    acceptance_thresholds = {
        "nominal_slack": NOMINAL_SLACK,
        "wp1": {
            "ladder_min_rungs": P23_MIN_RUNGS,
            "min_active_rows": 1,
            "recovery_planted_strictly_positive": True,
            "recovery_null_exactly_zero": 0.0,
            "rank_min_leg_beta": config["rank_min_leg_beta"],
            "rank_max_gross": config["rank_max_gross"],
            "rank_guards_never_relaxed": True,
        },
        "wp2": {
            "min_beta_windows": P23_MIN_RUNGS,
            "min_drift_thresholds": P23_MIN_RUNGS,
            "beta_window_default_preserved": config["beta_window"],
            "every_cell_reported": True,
            "recovery_planted_strictly_positive": True,
            "recovery_null_exactly_zero": 0.0,
        },
        "wp3": {
            "min_haircut_levels": P23_MIN_RUNGS,
            "haircut_zero_baseline_required": True,
            "costed_sharpe_non_increasing_in_haircut": True,
            "recovery_null_exactly_zero": 0.0,
            "censored_reports_document_reason_never_zero_tolerance": True,
        },
        "wp4": {
            "numbers_matched_min": P23_NUMBERS_MATCHED_MIN,
            "zero_unmatched_cells": 0,
            "no_harness_re_run": True,
            "no_go_for_market": True,
            "planted_recovery_labelled_controlled_synthetic": True,
            "explicit_signal_noise_verdict": True,
        },
    }

    return {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_p23_charter.py",
            "synthetic": True,
            "note": (
                "Controlled synthetic stimulus with known ground truth: "
                "not real market data and not market profitability evidence."
            ),
            "p22_source_schema": p22_charter["schema"],
            "universe_seed": p22_charter["provenance"]["universe_seed"],
            "panel_sha256": {variant: charter_shas[variant] for variant in VARIANTS},
            "p22_verdict": p22_verdict,
            "strategy_config": strategy_config,
            "nominal_slack": NOMINAL_SLACK,
            "acceptance_thresholds": acceptance_thresholds,
            "method": (
                "reads the committed P22 JSON artifacts (charter, null_battery, "
                "impact_surface, capacity) read-only; restates the P22 NO-GO "
                "verdict from committed fields; declares the P23 breadth ladder, "
                "beta-window/drift grid, borrow-haircut ladder, per-WP seed "
                "lists and WP1-WP4 acceptance thresholds as charter constants; "
                "never imports or re-runs any P21/P22 build_* harness."
            ),
            "caveat": (
                "P23 stress results on a controlled synthetic universe prove "
                "instability handling of the estimator; they are never market "
                "alpha. A null-universe positive result is a bug, not a finding. "
                "NO-GO for market deployment remains in force until a maintainer "
                "supplies a licensed price series."
            ),
        },
        "charter": {
            "campaign": "P23",
            "title": "Breadth and instability stress",
            "question": (
                "Does the BAB estimator survive breadth concentration, "
                "beta-estimation drift and crypto short-availability scarcity?"
            ),
            "answered_by_p22": (
                "Does the BAB estimator survive repeated null universes, "
                "nonlinear market impact and capacity constraints? Yes on "
                "controlled synthetic evidence, and the market verdict stays "
                "NO-GO."
            ),
            "not_market_evidence": True,
            "licensed_data_required": True,
            "breadth_ladder": list(P23_BREADTH_LADDER),
            "beta_window_grid": list(P23_BETA_WINDOW_GRID),
            "drift_threshold_grid": list(P23_DRIFT_THRESHOLD_GRID),
            "borrow_haircut_ladder": list(P23_BORROW_HAIRCUT_LADDER),
            "wp_seeds": wp_seeds,
            "wp_seed_counts": wp_seed_counts,
            "wps_in_order": [
                "P23 WP0 — charter",
                "P23 WP1 — breadth ladder",
                "P23 WP2 — beta-window/drift grid",
                "P23 WP3 — short-availability haircut ladder",
                "P23 WP4 — decision report (must keep NO-GO in force)",
            ],
            "binding_row": "P23 WP0",
            "artifact_gated": True,
        },
    }


def render_markdown(payload: dict) -> str:
    """Render the charter from the payload; no external numbers."""
    prov = payload["provenance"]
    verdict = prov["p22_verdict"]
    thresholds = prov["acceptance_thresholds"]
    charter = payload["charter"]
    nb = verdict["null_battery"]
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
        "## P22 verdict (restated from committed P22 JSON only)",
    ]
    lines.extend(
        _md_table(
            "p22_verdict",
            ["Fact", "Value"],
            [
                {"Fact": "Verdict", "Value": verdict["verdict"]},
                {"Fact": "NO-GO for market", "Value": verdict["no_go_for_market"]},
                {"Fact": "Signal on planted", "Value": verdict["signal_on_planted"]},
                {"Fact": "Noise on null", "Value": verdict["noise_on_null"]},
                {"Fact": "Nominal slack", "Value": verdict["nominal_slack"]},
            ],
        )
    )
    lines += ["", "### P22 null battery (committed JSON fields)"]
    lines.extend(
        _md_table(
            "p22_null_battery",
            ["Statistic", "Value"],
            [
                {"Statistic": "Chartered seeds", "Value": nb["n_seeds"]},
                {"Statistic": "Null books", "Value": nb["n_null_books"]},
                {"Statistic": "Planted books", "Value": nb["n_planted_books"]},
                {
                    "Statistic": "Null recovery max abs",
                    "Value": nb["null_recovery_max_abs"],
                },
                {
                    "Statistic": "Null books with zero recovery",
                    "Value": nb["null_recovery_zero_books"],
                },
                {
                    "Statistic": "False positives",
                    "Value": nb["fpr_count"],
                },
                {
                    "Statistic": "False-positive denominator",
                    "Value": nb["fpr_denominator"],
                },
                {"Statistic": "False-positive rate", "Value": nb["fpr_rate"]},
                {
                    "Statistic": "False-positive max declared",
                    "Value": nb["fpr_max_count_declared"],
                },
                {
                    "Statistic": "False-positive within bound",
                    "Value": nb["fpr_within_declared_bound"],
                },
                {
                    "Statistic": "Planted recovery min equal",
                    "Value": nb["planted_recovery_min"]["equal"],
                },
                {
                    "Statistic": "Planted recovery min rank",
                    "Value": nb["planted_recovery_min"]["rank"],
                },
                {
                    "Statistic": "Null Sharpe max",
                    "Value": nb["null_sharpe_max"],
                },
                {
                    "Statistic": "Planted Sharpe min",
                    "Value": nb["planted_sharpe_min"],
                },
            ],
        )
    )
    lines += ["", "### P22 nonlinear impact monotonicity (committed JSON fields)"]
    lines.extend(
        _md_table(
            "p22_impact",
            ["variant", "weighting", "monotone", "period_wise_non_increasing", "gross_sharpe"],
            [verdict["impact"][key] for key in sorted(verdict["impact"].keys())],
        )
    )
    lines += ["", "### P22 capacity break-even (committed JSON fields)"]
    lines.extend(
        _md_table(
            "p22_capacity",
            [
                "variant",
                "weighting",
                "gross_sharpe",
                "break_even_coefficient",
                "censored",
                "bracket_halving_verified",
            ],
            [verdict["capacity"][key] for key in sorted(verdict["capacity"].keys())],
        )
    )
    lines += [
        "",
        "## P23 charter constants (declared here, not derived from P22 JSON)",
    ]
    lines.extend(
        _md_table(
            "p23_grids",
            ["Grid", "Values"],
            [
                {
                    "Grid": "Breadth ladder (WP1)",
                    "Values": ", ".join(str(v) for v in charter["breadth_ladder"]),
                },
                {
                    "Grid": "Beta-window grid (WP2)",
                    "Values": ", ".join(str(v) for v in charter["beta_window_grid"]),
                },
                {
                    "Grid": "Drift-threshold grid (WP2)",
                    "Values": ", ".join(str(v) for v in charter["drift_threshold_grid"]),
                },
                {
                    "Grid": "Borrow-haircut ladder (WP3)",
                    "Values": ", ".join(
                        str(v) for v in charter["borrow_haircut_ladder"]
                    ),
                },
                {
                    "Grid": "Nominal slack",
                    "Values": str(prov["nominal_slack"]),
                },
            ],
        )
    )
    lines += ["", "### P23 per-work-package seeds (declared here)"]
    lines.extend(
        _md_table(
            "p23_seeds",
            ["WP", "n", "seeds"],
            [
                {
                    "WP": name.upper(),
                    "n": charter["wp_seed_counts"][name],
                    "seeds": ", ".join(str(s) for s in charter["wp_seeds"][name]),
                }
                for name in sorted(charter["wp_seeds"].keys())
            ],
        )
    )
    lines += ["", "### Shipped strategy defaults (committed P22 config, never relaxed)"]
    lines.extend(
        _md_table(
            "p23_strategy",
            ["Parameter", "Value"],
            [
                {"Parameter": key, "Value": prov["strategy_config"][key]}
                for key in sorted(prov["strategy_config"].keys())
            ],
        )
    )
    lines += ["", "### Acceptance thresholds consumed by P23 WP1-WP4"]
    threshold_rows = []
    for wp_name, wp in thresholds.items():
        if wp_name == "nominal_slack":
            continue
        for label, value in wp.items():
            threshold_rows.append(
                {"WP": wp_name.upper(), "Threshold": label, "Value": value}
            )
    lines.extend(_md_table("p23_thresholds", ["WP", "Threshold", "Value"], threshold_rows))
    lines += [
        "",
        "## Provenance",
        f"- Universe seed: {prov['universe_seed']}",
        f"- P22 source schema: {prov['p22_source_schema']}",
        f"- Planted panel sha256: `{prov['panel_sha256']['planted']}`",
        f"- Null panel sha256: `{prov['panel_sha256']['null']}`",
        f"- Generator: {prov['generator']}",
        "",
        "## WPs in order",
    ]
    lines.extend(f"- {wp}" for wp in charter["wps_in_order"])
    lines += [
        "",
        prov["method"],
        "",
        prov["caveat"],
    ]
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str = OUTPUT_DIR) -> tuple:
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
        f"P23 WP0 charter: no_go={prov['p22_verdict']['no_go_for_market']} "
        f"breadth_rungs={len(payload['charter']['breadth_ladder'])} "
        f"wp1_seeds={payload['charter']['wp_seed_counts']['wp1']}"
    )
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")
    print(f"wrote {kickoff_path}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
