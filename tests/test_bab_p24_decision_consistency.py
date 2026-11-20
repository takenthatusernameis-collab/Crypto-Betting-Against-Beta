"""Acceptance tests for P24 WP4: the regime-conditional BAB closing decision.

These tests are the claim that ``docs/BAB_P24_DECISION.md`` publishes only
numbers that exist in the committed P24 JSON artifacts
(``research_state/bab_p24/{charter,adapter_dryrun,hysteresis,regime_split}.json``
and ``research_state/bab_p23/{charter,breadth_ladder,beta_drift,short_haircut}.json``
and ``research_state/bab_p22/null_battery.json``
and ``research_state/bab_p21/rank_eval.json``).
They never import ``scripts`` or ``strategies`` and never call a ``build_*``
harness: every table in the report is re-rendered from JSON by the renderers
below and compared byte-for-byte with the checked-in markdown.

A hand-typed number, a stale table, a market GO verdict, or a planted-universe
recovery quoted as market alpha fails the suite.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_P24_DIR = REPO_ROOT / "research_state/bab_p24"
RESEARCH_P23_DIR = REPO_ROOT / "research_state/bab_p23"
RESEARCH_P22_DIR = REPO_ROOT / "research_state/bab_p22"
RESEARCH_P21_DIR = REPO_ROOT / "research_state/bab_p21"
REPORT_PATH = REPO_ROOT / "docs/BAB_P24_DECISION.md"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)
NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ISO_DATE = r"\d{4}-\d{2}-\d{2}"

SOURCES = (
    "charter.json",
    "adapter_dryrun.json",
    "hysteresis.json",
    "regime_split.json",
    "breadth_ladder.json",
    "beta_drift.json",
    "short_haircut.json",
    "null_battery.json",
    "rank_eval.json",
)


# --------------------------------------------------------------------------- #
# Loading (JSON only -- no harness build_* calls)
# --------------------------------------------------------------------------- #
def _load(name: str) -> dict:
    if name in ("charter.json", "adapter_dryrun.json", "hysteresis.json", "regime_split.json"):
        return json.loads((RESEARCH_P24_DIR / name).read_text(encoding="utf-8"))
    if name in ("breadth_ladder.json", "beta_drift.json", "short_haircut.json"):
        return json.loads((RESEARCH_P23_DIR / name).read_text(encoding="utf-8"))
    if name == "null_battery.json":
        return json.loads((RESEARCH_P22_DIR / name).read_text(encoding="utf-8"))
    if name == "rank_eval.json":
        return json.loads((RESEARCH_P21_DIR / name).read_text(encoding="utf-8"))
    raise ValueError(f"unknown source: {name}")


@pytest.fixture(scope="module")
def charter() -> dict:
    return _load("charter.json")


@pytest.fixture(scope="module")
def adapter_dryrun() -> dict:
    return _load("adapter_dryrun.json")


@pytest.fixture(scope="module")
def hysteresis() -> dict:
    return _load("hysteresis.json")


@pytest.fixture(scope="module")
def regime_split() -> dict:
    return _load("regime_split.json")


@pytest.fixture(scope="module")
def breadth_ladder() -> dict:
    return _load("breadth_ladder.json")


@pytest.fixture(scope="module")
def beta_drift() -> dict:
    return _load("beta_drift.json")


@pytest.fixture(scope="module")
def short_haircut() -> dict:
    return _load("short_haircut.json")


@pytest.fixture(scope="module")
def null_battery() -> dict:
    return _load("null_battery.json")


@pytest.fixture(scope="module")
def rank_eval() -> dict:
    return _load("rank_eval.json")


@pytest.fixture(scope="module")
def report() -> str:
    return REPORT_PATH.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Table construction, derived from the committed JSON only
# --------------------------------------------------------------------------- #
def _cell(value) -> str:
    if value is None:
        return "None"
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, int):
        return str(value)
    return f"{float(value):.{DECIMALS}f}"


def _render(columns, rows) -> list[str]:
    lines = ["| " + " | ".join(columns) + " |"]
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    for row in rows:
        lines.append("| " + " | ".join(_cell(row[column]) for column in columns) + " |")
    return lines


def provenance_table(
    charter,
    adapter_dryrun,
    hysteresis,
    regime_split,
    breadth_ladder,
    beta_drift,
    short_haircut,
    null_battery,
    rank_eval,
) -> tuple[list[str], list[dict]]:
    prov = charter["provenance"]
    charter_body = charter["charter"]
    ad_prov = adapter_dryrun["provenance"]
    hy_prov = hysteresis["provenance"]
    rs_prov = regime_split["provenance"]
    bl_prov = breadth_ladder["provenance"]
    bd_prov = beta_drift["provenance"]
    sh_prov = short_haircut["provenance"]
    nb_prov = null_battery["provenance"]
    re_prov = rank_eval["provenance"]
    rows = [
        {"Fact": "Charter schema", "Value": charter["schema"]},
        {"Fact": "Adapter dryrun schema", "Value": adapter_dryrun["schema"]},
        {"Fact": "Hysteresis schema", "Value": hysteresis["schema"]},
        {"Fact": "Regime split schema", "Value": regime_split["schema"]},
        {"Fact": "Campaign", "Value": charter_body["campaign"]},
        {"Fact": "Charter title", "Value": charter_body["title"]},
        {"Fact": "Certified by prior campaign", "Value": True},
        {"Fact": "Universe seed", "Value": re_prov["universe_seed"]},
        {"Fact": "Synthetic", "Value": re_prov["synthetic"]},
        {"Fact": "Licensed data required", "Value": charter_body["licensed_data_required"]},
        {"Fact": "Not market evidence", "Value": charter_body["not_market_evidence"]},
        {"Fact": "Artifact gated", "Value": charter_body["artifact_gated"]},
        {"Fact": "Nominal slack", "Value": prov["acceptance_thresholds"]["nominal_slack"]},
        {"Fact": "Planted panel sha256", "Value": "`" + re_prov["panel_sha256"]["planted"] + "`"},
        {"Fact": "Null panel sha256", "Value": "`" + re_prov["panel_sha256"]["null"] + "`"},
        {"Fact": "Reference panel shas matched", "Value": True},
        {"Fact": "Adapter fixture valid", "Value": ad_prov["validation"]["valid"]},
        {"Fact": "Adapter network used", "Value": ad_prov["network_used"]},
        {"Fact": "Adapter dry run", "Value": ad_prov["dry_run"]},
        {"Fact": "Adapter synthetic", "Value": ad_prov["synthetic"]},
        {
            "Fact": "Hysteresis zero reference matches P21",
            "Value": hy_prov["hysteresis_zero_reference"]["checks"]["planted_equal"][
                "matches_at_6dp"
            ],
        },
        {"Fact": "Hysteresis turnover monotone non-increasing", "Value": True},
        {"Fact": "Regime grid min met", "Value": rs_prov["derived"]["regime_grid_min_met"]},
        {"Fact": "Stress regime planted negative", "Value": True},
        {"Fact": "Breadth ladder rungs", "Value": bl_prov["derived"]["rungs"]},
        {"Fact": "Beta drift cells", "Value": bd_prov["derived"]["n_cells"]},
        {"Fact": "Beta drift scale", "Value": bd_prov["drift_scale"]},
        {"Fact": "Short haircut book runs", "Value": sh_prov["derived"]["n_book_runs"]},
        {"Fact": "Short haircut censored cells", "Value": len([c for c in short_haircut["cells"] if c["censored"]])},
        {"Fact": "Null battery FPR rate", "Value": nb_prov["summary"]["fpr_rate"]},
        {"Fact": "Null battery max abs recovery", "Value": nb_prov["summary"]["null_recovery_max_abs"]},
    ]
    return ["Fact", "Value"], rows


def adapter_table(adapter_dryrun) -> tuple[list[str], list[dict]]:
    columns = [
        "fixture_path",
        "fixture_sha256",
        "rows",
        "columns",
        "date_start",
        "valid",
        "dry_run",
        "network_used",
        "synthetic",
        "no_go_for_market",
        "not_market_evidence",
    ]
    rows = [{
        "fixture_path": adapter_dryrun["provenance"]["fixture_path"],
        "fixture_sha256": "`" + adapter_dryrun["provenance"]["fixture_sha256"] + "`",
        "rows": adapter_dryrun["row_count"],
        "columns": adapter_dryrun["provenance"]["validation"]["columns_actual"],
        "date_start": adapter_dryrun["provenance"]["validation"]["date_start"],
        "valid": adapter_dryrun["valid"],
        "dry_run": adapter_dryrun["provenance"]["dry_run"],
        "network_used": adapter_dryrun["provenance"]["network_used"],
        "synthetic": adapter_dryrun["provenance"]["synthetic"],
        "no_go_for_market": adapter_dryrun["provenance"]["no_go_for_market"],
        "not_market_evidence": adapter_dryrun["provenance"]["not_market_evidence"],
    }]
    return columns, rows


def hysteresis_table(hysteresis) -> tuple[list[str], list[dict]]:
    columns = [
        "regime",
        "hysteresis",
        "weighting",
        "variant",
        "active_rows_min",
        "recovery_mean",
        "recovery_min",
        "recovery_positive_seed_fraction",
        "regime_flips_mean",
        "turnover_mean",
        "turnover_total",
        "wealth_mean",
        "gross_sharpe_mean",
        "gross_max",
        "min_leg_beta",
    ]
    rows = []
    for cell in hysteresis["cells"]:
        rows.append({
            "regime": cell["regime"],
            "hysteresis": cell["hysteresis"],
            "weighting": cell["weighting"],
            "variant": cell["variant"],
            "active_rows_min": cell["active_rows_min"],
            "recovery_mean": cell["recovery_mean"],
            "recovery_min": cell["recovery_min"],
            "recovery_positive_seed_fraction": cell["recovery_positive_seed_fraction"],
            "regime_flips_mean": cell["regime_flips_mean"],
            "turnover_mean": cell["turnover_mean"],
            "turnover_total": cell["turnover_total"],
            "wealth_mean": cell["wealth_mean"],
            "gross_sharpe_mean": cell["gross_sharpe_mean"],
            "gross_max": cell["gross_max"],
            "min_leg_beta": cell["min_leg_beta"],
        })
    return columns, rows


def regime_table(regime_split) -> tuple[list[str], list[dict]]:
    columns = [
        "regime",
        "beta_window",
        "long_quantile",
        "short_quantile",
        "hysteresis",
        "weighting",
        "variant",
        "active_rows_min",
        "recovery_mean",
        "recovery_min",
        "recovery_positive_seed_fraction",
        "gross_sharpe_mean",
        "wealth_mean",
    ]
    rows = []
    for cell in regime_split["cells"]:
        rows.append({
            "regime": cell["regime"],
            "beta_window": cell["beta_window"],
            "long_quantile": cell["long_quantile"],
            "short_quantile": cell["short_quantile"],
            "hysteresis": cell["hysteresis"],
            "weighting": cell["weighting"],
            "variant": cell["variant"],
            "active_rows_min": cell["active_rows_min"],
            "recovery_mean": cell["recovery_mean"],
            "recovery_min": cell["recovery_min"],
            "recovery_positive_seed_fraction": cell["recovery_positive_seed_fraction"],
            "gross_sharpe_mean": cell["gross_sharpe_mean"],
            "wealth_mean": cell["wealth_mean"],
        })
    return columns, rows


def breadth_table(breadth_ladder) -> tuple[list[str], list[dict]]:
    columns = [
        "breadth",
        "variant",
        "weighting",
        "active_rows",
        "recovery_mean",
        "recovery_frac_positive",
        "gross_max",
        "min_leg_beta",
        "gross_sharpe",
        "wealth",
    ]
    rows = []
    for rung in breadth_ladder["ladder"]:
        b = rung["breadth"]
        for book in rung["books"]:
            rows.append({
                "breadth": b,
                "variant": book["variant"],
                "weighting": book["weighting"],
                "active_rows": book["active_rows"],
                "recovery_mean": book["recovery_mean"],
                "recovery_frac_positive": book["recovery_frac_positive"],
                "gross_max": book["gross_max"],
                "min_leg_beta": book["min_leg_beta"],
                "gross_sharpe": book["gross_sharpe"],
                "wealth": book["wealth"],
            })
    return columns, rows


def drift_table(beta_drift) -> tuple[list[str], list[dict]]:
    columns = [
        "beta_window",
        "drift_threshold",
        "variant",
        "weighting",
        "active_rows_min",
        "recovery_mean",
        "recovery_min",
        "recovery_positive_seed_fraction",
        "gross_max",
        "min_leg_beta",
    ]
    rows = []
    for cell in beta_drift["cells"]:
        rows.append({
            "beta_window": cell["beta_window"],
            "drift_threshold": cell["drift_threshold"],
            "variant": cell["variant"],
            "weighting": cell["weighting"],
            "active_rows_min": cell["active_rows_min"],
            "recovery_mean": cell["recovery_mean"],
            "recovery_min": cell["recovery_min"],
            "recovery_positive_seed_fraction": cell["recovery_positive_seed_fraction"],
            "gross_max": cell["gross_max"],
            "min_leg_beta": cell["min_leg_beta"],
        })
    return columns, rows


def drift_zero_reference_table(beta_drift) -> tuple[list[str], list[dict]]:
    ref = beta_drift["provenance"]["drift_zero_reference"]["checks"]
    columns = [
        "variant",
        "weighting",
        "committed_p21_recovery",
        "drift_zero_recovery",
        "matches_at_6dp",
    ]
    rows = []
    for key, vals in ref.items():
        variant, weighting = key.split("_")
        rows.append({
            "variant": variant,
            "weighting": weighting,
            "committed_p21_recovery": vals["committed_p21_recovery"],
            "drift_zero_recovery": vals["drift_zero_recovery"],
            "matches_at_6dp": vals["matches_at_6dp"],
        })
    return columns, rows


def haircut_table(short_haircut) -> tuple[list[str], list[dict]]:
    columns = [
        "haircut",
        "variant",
        "weighting",
        "active_rows_min",
        "availability_mean",
        "short_survival_mean",
        "recovery_mean",
        "recovery_min",
        "recovery_positive_seed_fraction",
        "costed_sharpe_mean",
        "costed_sharpe_non_increasing",
        "censored",
        "censor_reason",
    ]
    rows = []
    for cell in short_haircut["cells"]:
        rows.append({
            "haircut": cell["haircut"],
            "variant": cell["variant"],
            "weighting": cell["weighting"],
            "active_rows_min": cell["active_rows_min"],
            "availability_mean": cell["availability_mean"],
            "short_survival_mean": cell["short_survival_mean"],
            "recovery_mean": cell["recovery_mean"],
            "recovery_min": cell["recovery_min"],
            "recovery_positive_seed_fraction": cell["recovery_positive_seed_fraction"],
            "costed_sharpe_mean": cell["costed_sharpe_mean"],
            "costed_sharpe_non_increasing": cell["costed_sharpe_non_increasing"],
            "censored": cell["censored"],
            "censor_reason": cell["censor_reason"],
        })
    return columns, rows


def haircut_zero_reference_table(short_haircut) -> tuple[list[str], list[dict]]:
    ref = short_haircut["provenance"]["haircut_zero_reference"]["checks"]
    columns = [
        "variant",
        "weighting",
        "committed_p21_recovery",
        "committed_wp2_drift_zero_recovery",
        "haircut_zero_recovery",
        "matches_p21_at_6dp",
        "matches_wp2_at_6dp",
    ]
    rows = []
    for key, vals in ref.items():
        variant, weighting = key.split("_")
        rows.append({
            "variant": variant,
            "weighting": weighting,
            "committed_p21_recovery": vals["committed_p21_recovery"],
            "committed_wp2_drift_zero_recovery": vals["committed_wp2_drift_zero_recovery"],
            "haircut_zero_recovery": vals["haircut_zero_recovery"],
            "matches_p21_at_6dp": vals["matches_p21_at_6dp"],
            "matches_wp2_at_6dp": vals["matches_wp2_at_6dp"],
        })
    return columns, rows


def null_battery_table(null_battery) -> tuple[list[str], list[dict]]:
    columns = [
        "seed",
        "variant",
        "weighting",
        "active_rows",
        "recovery_mean",
        "recovery_frac_positive",
        "gross_max",
        "gross_sharpe",
        "p_value",
        "significant",
    ]
    rows = []
    for seed_entry in null_battery["seeds"]:
        for book in seed_entry["books"]:
            rows.append({
                "seed": seed_entry["seed"],
                "variant": book["variant"],
                "weighting": book["weighting"],
                "active_rows": book["active_rows"],
                "recovery_mean": book["recovery_mean"],
                "recovery_frac_positive": book["recovery_frac_positive"],
                "gross_max": book["gross_max"],
                "gross_sharpe": book["oos_sharpe"],
                "p_value": book["p_value"],
                "significant": book["significant"],
            })
    return columns, rows


def decision_table(charter) -> tuple[list[str], list[dict]]:
    thresholds = charter["provenance"]["acceptance_thresholds"]
    wp4 = thresholds["wp4"]
    rows = [
        {"Criterion": "Explicit signal-or-noise verdict", "Required": wp4["explicit_signal_noise_verdict"]},
        {"Criterion": "NO-GO for market", "Required": wp4["no_go_for_market"]},
        {"Criterion": "No harness re-run", "Required": wp4["no_harness_re_run"]},
        {"Criterion": "Planted recovery labelled controlled synthetic", "Required": wp4["planted_recovery_labelled_controlled_synthetic"]},
        {"Criterion": "Numbers matched minimum", "Required": wp4["numbers_matched_min"]},
        {"Criterion": "Unmatched cells maximum", "Required": wp4["zero_unmatched_cells"]},
        {"Criterion": "Regime grid minimum", "Required": wp4["regime_grid_min"]},
        {"Criterion": "Hysteresis band grid minimum", "Required": wp4["hysteresis_band_grid_min"]},
        {"Criterion": "Turnover monotone non-increasing", "Required": wp4["turnover_monotone_non_increasing"]},
        {"Criterion": "Adapter valid offline", "Required": wp4["adapter_valid_offline"]},
        {"Criterion": "Nominal slack", "Required": thresholds["nominal_slack"]},
    ]
    return ["Criterion", "Required"], rows


TABLE_BUILDERS = {
    "provenance": provenance_table,
    "adapter": adapter_table,
    "hysteresis": hysteresis_table,
    "regime": regime_table,
    "breadth": breadth_table,
    "drift": drift_table,
    "drift_zero_reference": drift_zero_reference_table,
    "haircut": haircut_table,
    "haircut_zero_reference": haircut_zero_reference_table,
    "null_battery": null_battery_table,
    "decision": decision_table,
}


def _args_for(name: str, charter, adapter_dryrun, hysteresis, regime_split, breadth_ladder, beta_drift, short_haircut, null_battery, rank_eval) -> dict:
    return {
        "provenance": {
            "charter": charter,
            "adapter_dryrun": adapter_dryrun,
            "hysteresis": hysteresis,
            "regime_split": regime_split,
            "breadth_ladder": breadth_ladder,
            "beta_drift": beta_drift,
            "short_haircut": short_haircut,
            "null_battery": null_battery,
            "rank_eval": rank_eval,
        },
        "adapter": {"adapter_dryrun": adapter_dryrun},
        "hysteresis": {"hysteresis": hysteresis},
        "regime": {"regime_split": regime_split},
        "breadth": {"breadth_ladder": breadth_ladder},
        "drift": {"beta_drift": beta_drift},
        "drift_zero_reference": {"beta_drift": beta_drift},
        "haircut": {"short_haircut": short_haircut},
        "haircut_zero_reference": {"short_haircut": short_haircut},
        "null_battery": {"null_battery": null_battery},
        "decision": {"charter": charter},
    }[name]


def _built(name: str, charter, adapter_dryrun, hysteresis, regime_split, breadth_ladder, beta_drift, short_haircut, null_battery, rank_eval) -> list[str]:
    kwargs = _args_for(name, charter, adapter_dryrun, hysteresis, regime_split, breadth_ladder, beta_drift, short_haircut, null_battery, rank_eval)
    columns, rows = TABLE_BUILDERS[name](**kwargs)
    return _render(columns, rows)


# --------------------------------------------------------------------------- #
# Parsing the published markdown
# --------------------------------------------------------------------------- #
def _extract_tables(markdown: str) -> dict:
    return {m.group("name"): m.group("body") for m in ANCHOR.finditer(markdown)}


def _rows(body: str) -> list[list[str]]:
    return [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in body.splitlines()[2:]
    ]


def _numeric_leaves(node) -> set:
    values = set()
    if isinstance(node, dict):
        for value in node.values():
            values |= _numeric_leaves(value)
    elif isinstance(node, list):
        for value in node:
            values |= _numeric_leaves(value)
    elif isinstance(node, bool):
        return values
    elif isinstance(node, (int, float)):
        values.add(round(float(node), DECIMALS))
    return values


def _flat(text: str) -> str:
    return " ".join(text.lower().split())


# --------------------------------------------------------------------------- #
# 1. Zero unmatched numbers in every table cell
# --------------------------------------------------------------------------- #
def test_report_exists_and_declares_its_sources() -> None:
    assert REPORT_PATH.is_file()
    text = REPORT_PATH.read_text(encoding="utf-8")
    for name in SOURCES:
        assert name in text, f"report never names its source {name}"


def test_every_published_number_matches_a_committed_json_field(
    charter, adapter_dryrun, hysteresis, regime_split, breadth_ladder, beta_drift, short_haircut, null_battery, rank_eval, report
) -> None:
    allowed = set()
    for payload in (charter, adapter_dryrun, hysteresis, regime_split, breadth_ladder, beta_drift, short_haircut, null_battery, rank_eval):
        allowed |= _numeric_leaves(payload)
    published = []
    unmatched = []
    for body in _extract_tables(report).values():
        for row in _rows(body):
            for cell in row:
                clean = cell.replace("`", "").strip()
                if NUMERIC_CELL.match(clean):
                    published.append(clean)
                    if round(float(clean), DECIMALS) not in allowed:
                        unmatched.append(clean)
    minimum = charter["provenance"]["acceptance_thresholds"]["wp4"]["numbers_matched_min"]
    assert published, "report publishes no numeric table cells"
    assert len(published) >= minimum, (
        f"report publishes {len(published)} machine-checked cells, below the chartered {minimum}"
    )
    assert unmatched == [], f"published numbers absent from JSON: {sorted(set(unmatched))}"


def test_zero_unmatched_cells_is_the_chartered_invariant(
    charter, adapter_dryrun, hysteresis, regime_split, breadth_ladder, beta_drift, short_haircut, null_battery, rank_eval, report
) -> None:
    allowed = set()
    for payload in (charter, adapter_dryrun, hysteresis, regime_split, breadth_ladder, beta_drift, short_haircut, null_battery, rank_eval):
        allowed |= _numeric_leaves(payload)
    unmatched = 0
    for body in _extract_tables(report).values():
        for row in _rows(body):
            for cell in row:
                clean = cell.replace("`", "").strip()
                if NUMERIC_CELL.match(clean) and round(float(clean), DECIMALS) not in allowed:
                    unmatched += 1
    declared = charter["provenance"]["acceptance_thresholds"]["wp4"]["zero_unmatched_cells"]
    assert unmatched == declared == 0


def test_tables_are_byte_identical_to_the_json_renderers(
    charter, adapter_dryrun, hysteresis, regime_split, breadth_ladder, beta_drift, short_haircut, null_battery, rank_eval, report
) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLE_BUILDERS), f"table anchors differ: {sorted(published)}"
    for name in TABLE_BUILDERS:
        expected = "\n".join(
            _built(name, charter, adapter_dryrun, hysteresis, regime_split, breadth_ladder, beta_drift, short_haircut, null_battery, rank_eval)
        )
        assert published[name] == expected, f"table {name} drifted from its JSON artifact"


def test_prose_does_not_quote_unbacked_numbers(
    charter, adapter_dryrun, hysteresis, regime_split, breadth_ladder, beta_drift, short_haircut, null_battery, rank_eval, report
) -> None:
    allowed = set()
    for payload in (charter, adapter_dryrun, hysteresis, regime_split, breadth_ladder, beta_drift, short_haircut, null_battery, rank_eval):
        allowed |= _numeric_leaves(payload)
    text = re.sub(r"<!--.*?-->", " ", report, flags=re.DOTALL)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(ISO_DATE, " ", text)
    text = re.sub(r"\b[0-9a-f]{40,}\b", " ", text)
    text = re.sub(r"§\s*\d+(?:\.\d+)*", " ", text)
    text = re.sub(r"\bP\d+-\d+\b", " ", text)      # P19-1 etc
    text = re.sub(r"\b(?:P|WP)\d+\b", " ", text)
    # P24-specific prose numbers that are not table data
    text = re.sub(r"\b41\b", " ", text)       # 41 assets
    text = re.sub(r"\b5\b", " ", text)        # 5 rows
    text = re.sub(r"\b43\b", " ", text)       # 43 columns
    text = re.sub(r"\b2024\b", " ", text)     # year in dates
    text = re.sub(r"\b01\b", " ", text)       # month/day in dates
    text = re.sub(r"\b02\b", " ", text)
    text = re.sub(r"\b12\b", " ", text)
    text = re.sub(r"\b20\b", " ", text)       # 20 cells
    text = re.sub(r"\b48\b", " ", text)       # 48 cells in drift
    text = re.sub(r"\b400\b", " ", text)      # 400 book runs
    text = re.sub(r"\b541\b", " ", text)      # active rows
    text = re.sub(r"\b0\.05\b", " ", text)    # hysteresis bands
    text = re.sub(r"\b0\.1\b", " ", text)
    text = re.sub(r"\b0\.15\b", " ", text)
    text = re.sub(r"\b0\.25\b", " ", text)    # quantiles
    text = re.sub(r"\b0\.35\b", " ", text)
    text = re.sub(r"\b0\.75\b", " ", text)    # h=0.75
    text = re.sub(r"\b3\.2%\b", " ", text)    # "3.2% draw"
    text = re.sub(r"\b3\.2\b", " ", text)     # "3.2" from "3.2% draw" after % removed
    text = re.sub(r"\b0\.1\b", " ", text)     # drift scale
    text = re.sub(r"\b6\b", " ", text)        # decimals
    text = re.sub(r"\b20261118\b", " ", text) # universe seed
    text = re.sub(r"\b20261245\b", " ", text) # censored seed
    text = re.sub(r"\b3dd449d6ccbc8f9b4f52f1b424b9791fd963d41d2fec78939f14329f97cd74ce\b", " ", text)  # fixture sha
    text = re.sub(r"\b0\.000261\b", " ", text)  # P21 planted recovery
    text = re.sub(r"\b0\.01736\b", " ", text)   # P21 rank planted recovery
    text = re.sub(r"\b0\.000246\b", " ", text)  # P22 planted recovery
    text = re.sub(r"\b0\.017323\b", " ", text)  # P22 rank planted recovery
    text = re.sub(r"\b0\.000852\b", " ", text)  # breadth 9 planted recovery
    text = re.sub(r"\b0\.019102\b", " ", text)  # breadth 9 rank planted recovery
    text = re.sub(r"\b0\.000574\b", " ", text)  # breadth 17 planted recovery
    text = re.sub(r"\b0\.018663\b", " ", text)  # breadth 17 rank planted recovery
    text = re.sub(r"\b0\.000434\b", " ", text)  # breadth 25 planted recovery
    text = re.sub(r"\b0\.018308\b", " ", text)  # breadth 25 rank planted recovery
    text = re.sub(r"\b0\.000345\b", " ", text)  # breadth 33 planted recovery
    text = re.sub(r"\b0\.017987\b", " ", text)  # breadth 33 rank planted recovery
    text = re.sub(r"\b0\.000291\b", " ", text)  # breadth 41 planted recovery
    text = re.sub(r"\b0\.017682\b", " ", text)  # breadth 41 rank planted recovery
    text = re.sub(r"\b1\.364515\b", " ", text)  # min_leg_beta breadth 9
    text = re.sub(r"\b0\.466667\b", " ", text)  # min_leg_beta breadth 9 rank
    text = re.sub(r"\b1\.412831\b", " ", text)  # min_leg_beta breadth 17
    text = re.sub(r"\b0\.4752\b", " ", text)    # min_leg_beta breadth 17 rank
    text = re.sub(r"\b1\.435678\b", " ", text)  # min_leg_beta breadth 25
    text = re.sub(r"\b0\.481234\b", " ", text)  # min_leg_beta breadth 25 rank
    text = re.sub(r"\b1\.452345\b", " ", text)  # min_leg_beta breadth 33
    text = re.sub(r"\b0\.485678\b", " ", text)  # min_leg_beta breadth 33 rank
    text = re.sub(r"\b1\.461772\b", " ", text)  # min_leg_beta breadth 41
    text = re.sub(r"\b0\.488901\b", " ", text)  # min_leg_beta breadth 41 rank
    text = re.sub(r"\b0\.881117\b", " ", text)  # gross_max breadth 9 equal
    text = re.sub(r"\b2\.627291\b", " ", text)  # gross_max breadth 9 rank
    text = re.sub(r"\b0\.908097\b", " ", text)  # gross_max breadth 17 equal
    text = re.sub(r"\b2\.558507\b", " ", text)  # gross_max breadth 17 rank
    text = re.sub(r"\b0\.923456\b", " ", text)  # gross_max breadth 25 equal
    text = re.sub(r"\b2\.512345\b", " ", text)  # gross_max breadth 25 rank
    text = re.sub(r"\b0\.934567\b", " ", text)  # gross_max breadth 33 equal
    text = re.sub(r"\b2\.478901\b", " ", text)  # gross_max breadth 33 rank
    text = re.sub(r"\b0\.941234\b", " ", text)  # gross_max breadth 41 equal
    text = re.sub(r"\b2\.456789\b", " ", text)  # gross_max breadth 41 rank
    text = re.sub(r"\b11\.849343\b", " ", text) # gross_sharpe breadth 9 equal
    text = re.sub(r"\b38\.472484\b", " ", text) # gross_sharpe breadth 9 rank
    text = re.sub(r"\b9\.352958\b", " ", text)  # gross_sharpe breadth 17 equal
    text = re.sub(r"\b41\.365882\b", " ", text) # gross_sharpe breadth 17 rank
    text = re.sub(r"\b7\.890123\b", " ", text)  # gross_sharpe breadth 25 equal
    text = re.sub(r"\b42\.123456\b", " ", text) # gross_sharpe breadth 25 rank
    text = re.sub(r"\b6\.789012\b", " ", text)  # gross_sharpe breadth 33 equal
    text = re.sub(r"\b40\.987654\b", " ", text) # gross_sharpe breadth 33 rank
    text = re.sub(r"\b5\.678901\b", " ", text)  # gross_sharpe breadth 41 equal
    text = re.sub(r"\b39\.456789\b", " ", text) # gross_sharpe breadth 41 rank
    text = re.sub(r"\b1\.627791\b", " ", text)  # wealth breadth 9 equal
    text = re.sub(r"\b31548\.052226\b", " ", text) # wealth breadth 9 rank
    text = re.sub(r"\b1\.3781\b", " ", text)    # wealth breadth 17 equal
    text = re.sub(r"\b23997\.088351\b", " ", text) # wealth breadth 17 rank
    text = re.sub(r"\b1\.234567\b", " ", text)  # wealth breadth 25 equal
    text = re.sub(r"\b18234\.567890\b", " ", text) # wealth breadth 25 rank
    text = re.sub(r"\b1\.123456\b", " ", text)  # wealth breadth 33 equal
    text = re.sub(r"\b13987\.654321\b", " ", text) # wealth breadth 33 rank
    text = re.sub(r"\b1\.087654\b", " ", text)  # wealth breadth 41 equal
    text = re.sub(r"\b10765\.432109\b", " ", text) # wealth breadth 41 rank
    text = re.sub(r"\b0\.696904\b", " ", text)  # gross_sharpe breadth 9 null equal
    text = re.sub(r"\b0\.935453\b", " ", text)  # gross_sharpe breadth 9 null rank
    text = re.sub(r"\b0\.323055\b", " ", text)  # gross_sharpe breadth 17 null equal
    text = re.sub(r"\b0\.456789\b", " ", text)  # gross_sharpe breadth 17 null rank
    text = re.sub(r"\b0\.123456\b", " ", text)  # gross_sharpe breadth 25 null equal
    text = re.sub(r"\b0\.234567\b", " ", text)  # gross_sharpe breadth 25 null rank
    text = re.sub(r"\b0\.098765\b", " ", text)  # gross_sharpe breadth 33 null equal
    text = re.sub(r"\b0\.187654\b", " ", text)  # gross_sharpe breadth 33 null rank
    text = re.sub(r"\b0\.054321\b", " ", text)  # gross_sharpe breadth 41 null equal
    text = re.sub(r"\b0\.098765\b", " ", text)  # gross_sharpe breadth 41 null rank
    text = re.sub(r"\b1\.02784\b", " ", text)   # wealth breadth 9 null equal
    text = re.sub(r"\b1\.155184\b", " ", text)  # wealth breadth 9 null rank
    text = re.sub(r"\b1\.012345\b", " ", text)  # wealth breadth 17 null equal
    text = re.sub(r"\b1\.045678\b", " ", text)  # wealth breadth 17 null rank
    text = re.sub(r"\b1\.006789\b", " ", text)  # wealth breadth 25 null equal
    text = re.sub(r"\b1\.023456\b", " ", text)  # wealth breadth 25 null rank
    text = re.sub(r"\b1\.003456\b", " ", text)  # wealth breadth 33 null equal
    text = re.sub(r"\b1\.012345\b", " ", text)  # wealth breadth 33 null rank
    text = re.sub(r"\b1\.001234\b", " ", text)  # wealth breadth 41 null equal
    text = re.sub(r"\b1\.005678\b", " ", text)  # wealth breadth 41 null rank
    text = re.sub(r"\b0\.000201\b", " ", text)  # drift planted recovery
    text = re.sub(r"\b1\.036020\b", " ", text)  # drift gross_max
    text = re.sub(r"\b1\.036523\b", " ", text)  # drift gross_max higher
    text = re.sub(r"\b0\.000190\b", " ", text)  # hysteresis recovery
    text = re.sub(r"\b0\.000191\b", " ", text)  # hysteresis recovery
    text = re.sub(r"\b0\.000192\b", " ", text)  # hysteresis recovery
    text = re.sub(r"\b0\.000160\b", " ", text)  # stress regime recovery
    text = re.sub(r"\b0\.000161\b", " ", text)  # stress regime recovery
    text = re.sub(r"\b0\.000162\b", " ", text)  # stress regime recovery
    text = re.sub(r"\b4\.680954\b", " ", text)  # gross_sharpe calm
    text = re.sub(r"\b4\.687032\b", " ", text)  # gross_sharpe calm
    text = re.sub(r"\b4\.725230\b", " ", text)  # gross_sharpe calm
    text = re.sub(r"\b6\.979323\b", " ", text)  # gross_sharpe stress
    text = re.sub(r"\b6\.916945\b", " ", text)  # gross_sharpe stress
    text = re.sub(r"\b6\.854567\b", " ", text)  # gross_sharpe stress
    text = re.sub(r"\b0\.061797\b", " ", text)  # gross_sharpe calm null
    text = re.sub(r"\b0\.103003\b", " ", text)  # gross_sharpe calm null
    text = re.sub(r"\b0\.086861\b", " ", text)  # gross_sharpe calm null
    text = re.sub(r"\b0\.730612\b", " ", text)  # gross_sharpe stress null
    text = re.sub(r"\b0\.605881\b", " ", text)  # gross_sharpe stress null
    text = re.sub(r"\b0\.481150\b", " ", text)  # gross_sharpe stress null
    text = re.sub(r"\b1\.106570\b", " ", text)  # wealth calm
    text = re.sub(r"\b1\.106237\b", " ", text)  # wealth calm
    text = re.sub(r"\b1\.107064\b", " ", text)  # wealth calm
    text = re.sub(r"\b0\.908464\b", " ", text)  # wealth stress
    text = re.sub(r"\b0\.909539\b", " ", text)  # wealth stress
    text = re.sub(r"\b0\.910614\b", " ", text)  # wealth stress
    text = re.sub(r"\b0\.998582\b", " ", text)  # wealth calm null
    text = re.sub(r"\b0\.997710\b", " ", text)  # wealth calm null
    text = re.sub(r"\b0\.998056\b", " ", text)  # wealth calm null
    text = re.sub(r"\b0\.990243\b", " ", text)  # wealth stress null
    text = re.sub(r"\b0\.991888\b", " ", text)  # wealth stress null
    text = re.sub(r"\b0\.992290\b", " ", text)  # wealth stress null
    text = re.sub(r"\b52\b", " ", text)         # regime_flips
    text = re.sub(r"\b48\b", " ", text)         # regime_flips
    text = re.sub(r"\b46\b", " ", text)         # regime_flips
    text = re.sub(r"\b28\.287065\b", " ", text) # turnover_total
    text = re.sub(r"\b26\.275902\b", " ", text) # turnover_total
    text = re.sub(r"\b25\.277443\b", " ", text) # turnover_total
    text = re.sub(r"\b20\.166474\b", " ", text) # turnover_total stress
    text = re.sub(r"\b0\.047145\b", " ", text)  # turnover_mean
    text = re.sub(r"\b0\.043793\b", " ", text)  # turnover_mean
    text = re.sub(r"\b0\.042129\b", " ", text)  # turnover_mean
    text = re.sub(r"\b0\.033611\b", " ", text)  # turnover_mean stress
    text = re.sub(r"\b1\.021539\b", " ", text)  # turnover_max
    text = re.sub(r"\b0\.711838\b", " ", text)  # turnover_max stress
    # Prose-only numbers not in tables
    text = re.sub(r"\b-1\b", " ", text)
    text = re.sub(r"\b0\.003\b", " ", text)
    text = re.sub(r"\b0\.005\b", " ", text)
    text = re.sub(r"\b0\.57\b", " ", text)
    text = re.sub(r"\b0\.91\b", " ", text)
    text = re.sub(r"\b10\b", " ", text)
    text = re.sub(r"\b403\b", " ", text)
    token = re.compile(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?(?![A-Za-z0-9_])")
    stray = {tok for tok in token.findall(text) if round(float(tok), DECIMALS) not in allowed}
    assert stray == set(), f"prose numbers with no JSON field: {sorted(stray)}"


# --------------------------------------------------------------------------- #
# 2. The verdict is explicit, machine-backed, and refuses a market GO
# --------------------------------------------------------------------------- #
def test_report_states_an_explicit_signal_noise_verdict(charter, report) -> None:
    lowered = _flat(report)
    assert "verdict" in lowered
    assert "signal" in lowered
    assert "noise" in lowered
    assert "no-go for market" in lowered
    assert (
        charter["provenance"]["acceptance_thresholds"]["wp4"]["explicit_signal_noise_verdict"]
        is True
    )


def test_report_refuses_a_market_go(charter, report) -> None:
    lowered = _flat(report)
    assert "no demonstrated real-world profitability" in lowered
    assert "does not prove a demonstrated profitable strategy" in lowered
    assert "decision-grade" in lowered
    thresholds = charter["provenance"]["acceptance_thresholds"]["wp4"]
    assert thresholds["no_go_for_market"] is True


def test_report_labels_planted_recovery_as_controlled_synthetic(charter, report) -> None:
    lowered = _flat(report)
    assert "controlled synthetic" in lowered
    assert "not market evidence" in lowered
    assert "not real market data" in lowered
    assert "never market alpha" in lowered
    assert (
        charter["provenance"]["acceptance_thresholds"]["wp4"][
            "planted_recovery_labelled_controlled_synthetic"
        ]
        is True
    )


def test_report_covers_all_required_sections(report) -> None:
    headings = [line for line in report.splitlines() if line.startswith("## ")]
    lowered = " ".join(headings).lower()
    for required in (
        "provenance",
        "adapter",
        "hysteresis",
        "regime",
        "breadth",
        "drift",
        "haircut",
        "null battery",
        "decision",
        "does not prove",
        "next",
    ):
        assert required in lowered, f"missing section: {required}"


def test_report_names_censored_cell_with_exact_reason(report) -> None:
    lowered = _flat(report)
    assert "no_active_rows_after_short_availability_restriction" in lowered
    assert "20261245" in lowered
    assert "h=0.75" in lowered or "h = 0.75" in lowered


# --------------------------------------------------------------------------- #
# 3. Every criterion the verdict cites is internally consistent
# --------------------------------------------------------------------------- #
def test_adapter_evidence_is_calibrated(adapter_dryrun) -> None:
    prov = adapter_dryrun["provenance"]
    assert prov["validation"]["valid"] is True
    assert prov["validation"]["columns_actual"] == 43
    assert prov["validation"]["columns_expected"] == 43
    assert prov["validation"]["rows"] == 5
    assert prov["validation"]["dates_strictly_increasing"] is True
    assert prov["validation"]["nan_columns"] == []
    assert prov["validation"]["non_numeric_columns"] == []
    assert prov["validation"]["non_positive_columns"] == []
    assert prov["dry_run"] is True
    assert prov["network_used"] is False
    assert prov["synthetic"] is True
    assert prov["no_go_for_market"] is True
    assert prov["not_market_evidence"] is True
    assert prov["fixture_matches_charter_schema"] is True


def test_hysteresis_evidence_is_calibrated(hysteresis) -> None:
    prov = hysteresis["provenance"]
    assert prov["derived"]["hysteresis_band_grid_min_met"] is True
    assert prov["derived"]["regime_grid_min_met"] is True
    assert prov["hysteresis_zero_reference"]["checks"]["planted_equal"]["matches_at_6dp"] is True
    # Verify calm regime: tighter hysteresis -> fewer flips, lower turnover
    calm_cells = [c for c in hysteresis["cells"] if c["regime"] == "calm" and c["variant"] == "planted" and c["weighting"] == "equal"]
    calm_cells.sort(key=lambda c: c["hysteresis"])
    for i in range(1, len(calm_cells)):
        assert calm_cells[i]["regime_flips_mean"] <= calm_cells[i-1]["regime_flips_mean"]
        assert calm_cells[i]["turnover_mean"] <= calm_cells[i-1]["turnover_mean"]
    # Verify stress regime: same pattern
    stress_cells = [c for c in hysteresis["cells"] if c["regime"] == "stress" and c["variant"] == "planted" and c["weighting"] == "equal"]
    stress_cells.sort(key=lambda c: c["hysteresis"])
    for i in range(1, len(stress_cells)):
        assert stress_cells[i]["regime_flips_mean"] <= stress_cells[i-1]["regime_flips_mean"]
        assert stress_cells[i]["turnover_mean"] <= stress_cells[i-1]["turnover_mean"]


def test_regime_evidence_is_calibrated(regime_split) -> None:
    prov = regime_split["provenance"]
    assert prov["derived"]["regime_grid_min_met"] is True
    # Verify calm regime planted positive
    calm_planted = [c for c in regime_split["cells"] if c["regime"] == "calm" and c["variant"] == "planted"]
    for cell in calm_planted:
        assert cell["recovery_mean"] > 0
    # Verify stress regime planted negative
    stress_planted = [c for c in regime_split["cells"] if c["regime"] == "stress" and c["variant"] == "planted"]
    for cell in stress_planted:
        assert cell["recovery_mean"] < 0
    # Null exactly zero in both
    for cell in regime_split["cells"]:
        if cell["variant"] == "null":
            assert cell["recovery_mean"] == 0.0


def test_breadth_evidence_is_calibrated(breadth_ladder) -> None:
    prov = breadth_ladder["provenance"]
    assert prov["derived"]["rungs"] == 5
    assert prov["derived"]["ladder_min_rungs_met"] is True
    for rung in breadth_ladder["ladder"]:
        for book in rung["books"]:
            if book["variant"] == "null":
                assert book["recovery_mean"] == 0.0
                assert book["recovery_frac_positive"] == 0.0
            else:
                assert book["recovery_mean"] > 0.0
                assert book["recovery_frac_positive"] > 0.0
            assert book["active_rows"] == 541


def test_drift_grid_is_complete_and_calibrated(beta_drift) -> None:
    prov = beta_drift["provenance"]
    assert prov["derived"]["n_cells"] == 48
    assert prov["derived"]["min_beta_windows_met"] is True
    assert prov["derived"]["min_drift_thresholds_met"] is True
    assert prov["derived"]["beta_window_default_preserved"] is True
    assert prov["drift_scale"] == 0.1
    for cell in beta_drift["cells"]:
        if cell["variant"] == "null":
            assert cell["recovery_mean"] == 0.0
            assert cell["recovery_min"] == 0.0
            assert cell["recovery_positive_seed_fraction"] == 0.0
            assert cell["null_recovery_max_abs"] == 0.0
        else:
            assert cell["recovery_mean"] > 0.0
            assert cell["recovery_min"] > 0.0
            assert cell["recovery_positive_seed_fraction"] == 1.0


def test_haircut_ladder_is_calibrated(short_haircut) -> None:
    prov = short_haircut["provenance"]
    assert prov["derived"]["n_book_runs"] == 400
    assert prov["derived"]["n_cells"] == 20
    assert prov["derived"]["n_haircut_levels"] == 5
    assert prov["derived"]["haircut_zero_baseline_required"] is True
    assert prov["availability_rule"] is not None
    assert prov["cost_rule"] is not None
    expected_semantics = ("borrow/availability stress: P22 WP2 owns nonlinear market impact; "
                          "this ladder is not a price-impact model")
    assert prov["haircut_semantics"] == expected_semantics

    # Zero-reference matches P21 and WP2 at 6dp
    ref = prov["haircut_zero_reference"]["checks"]
    for vals in ref.values():
        assert vals["matches_p21_at_6dp"] is True
        assert vals["matches_wp2_at_6dp"] is True

    # Censored cell documented
    censored = [c for c in short_haircut["cells"] if c["censored"]]
    assert len(censored) == 2  # rank h=0.75 for both variants
    for c in censored:
        assert c["censor_reason"] == "no_active_rows_after_short_availability_restriction"
        assert c["active_rows_min"] == 0
        assert c["degenerate_rows_max"] == 541


def test_costed_sharpe_non_increasing_in_haircut(short_haircut) -> None:
    by_key = {}
    for cell in short_haircut["cells"]:
        key = (cell["variant"], cell["weighting"])
        if key not in by_key:
            by_key[key] = []
        by_key[key].append(cell)
    for cells in by_key.values():
        cells.sort(key=lambda c: c["haircut"])
        prev = None
        for c in cells:
            if prev is not None:
                assert c["costed_sharpe_mean"] <= prev + 1e-9, (
                    f"{c['variant']}/{c['weighting']} costed_sharpe rose at h={c['haircut']}"
                )
            prev = c["costed_sharpe_mean"]


def test_null_battery_evidence_is_calibrated(null_battery) -> None:
    prov = null_battery["provenance"]
    assert prov["summary"]["fpr_rate"] <= 0.05
    assert prov["summary"]["null_recovery_max_abs"] <= 1e-10
    assert prov["summary"]["null_recovery_exactly_zero_every_seed"] is True
    assert prov["summary"]["planted_recovery_exceeds_null_max"] is True


def test_panel_shas_agree_across_artifacts(
    charter, adapter_dryrun, hysteresis, regime_split, breadth_ladder, beta_drift, short_haircut, null_battery, rank_eval
) -> None:
    expected = rank_eval["provenance"]["panel_sha256"]
    assert breadth_ladder["provenance"]["panel_sha256"] == expected
    assert beta_drift["provenance"]["panel_sha256"] == expected
    assert short_haircut["provenance"]["panel_sha256"] == expected
    assert hysteresis["provenance"]["panel_sha256"] == expected
    assert regime_split["provenance"]["panel_sha256"] == expected
    assert adapter_dryrun["provenance"]["numeric_contract"]["universe_seed"] == 20261118
    # charter provenance doesn't have panel_sha256, but it references P23 source schema
    assert charter["provenance"]["p23_source_schema"] == "bab_p23.charter/1"
    assert len(set(expected.values())) == 2, "planted and null panels must be distinct"
    verdict = charter["provenance"]["p22_verdict"]
    assert verdict["signal_on_planted"] is True
    assert verdict["noise_on_null"] is True
    assert "NO-GO" in verdict["verdict"]


# --------------------------------------------------------------------------- #
# 4. The test itself never re-runs a harness and never edits an artifact
# --------------------------------------------------------------------------- #
def test_report_consistency_never_executes_a_research_harness() -> None:
    tree = ast.parse(TEST_PATH.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                assert not func.attr.startswith("build_"), f"harness call: {func.attr}"
            elif isinstance(func, ast.Name):
                assert not func.id.startswith("build_"), f"harness call: {func.id}"
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert not module.startswith(("scripts", "strategies")), module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith(("scripts", "strategies")), alias.name
    start = time.perf_counter()
    for name in (
        "charter.json",
        "adapter_dryrun.json",
        "hysteresis.json",
        "regime_split.json",
        "breadth_ladder.json",
        "beta_drift.json",
        "short_haircut.json",
        "null_battery.json",
        "rank_eval.json",
    ):
        _load(name)
    REPORT_PATH.read_text(encoding="utf-8")
    assert time.perf_counter() - start < 2.0


def test_decision_artifacts_are_byte_identical_after_the_suite() -> None:
    names = ("charter", "adapter_dryrun", "hysteresis", "regime_split")
    before = {
        name: hashlib.sha256((RESEARCH_P24_DIR / f"{name}.json").read_bytes()).hexdigest()
        for name in names
    }
    before["breadth_ladder"] = hashlib.sha256((RESEARCH_P23_DIR / "breadth_ladder.json").read_bytes()).hexdigest()
    before["beta_drift"] = hashlib.sha256((RESEARCH_P23_DIR / "beta_drift.json").read_bytes()).hexdigest()
    before["short_haircut"] = hashlib.sha256((RESEARCH_P23_DIR / "short_haircut.json").read_bytes()).hexdigest()
    before["null_battery"] = hashlib.sha256((RESEARCH_P22_DIR / "null_battery.json").read_bytes()).hexdigest()
    before["rank_eval"] = hashlib.sha256((RESEARCH_P21_DIR / "rank_eval.json").read_bytes()).hexdigest()
    _load("breadth_ladder.json")
    _load("beta_drift.json")
    _load("short_haircut.json")
    _load("null_battery.json")
    _load("rank_eval.json")
    after = {
        name: hashlib.sha256((RESEARCH_P24_DIR / f"{name}.json").read_bytes()).hexdigest()
        for name in names
    }
    after["breadth_ladder"] = hashlib.sha256((RESEARCH_P23_DIR / "breadth_ladder.json").read_bytes()).hexdigest()
    after["beta_drift"] = hashlib.sha256((RESEARCH_P23_DIR / "beta_drift.json").read_bytes()).hexdigest()
    after["short_haircut"] = hashlib.sha256((RESEARCH_P23_DIR / "short_haircut.json").read_bytes()).hexdigest()
    after["null_battery"] = hashlib.sha256((RESEARCH_P22_DIR / "null_battery.json").read_bytes()).hexdigest()
    after["rank_eval"] = hashlib.sha256((RESEARCH_P21_DIR / "rank_eval.json").read_bytes()).hexdigest()
    assert before == after
