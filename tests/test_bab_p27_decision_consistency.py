"""Acceptance tests for P27 WP3: the production-readiness decision.

These tests are the claim that ``docs/BAB_P27_DECISION.md`` publishes only
numbers that exist in the committed P27 WP0-WP2 JSON artifacts
(``research_state/bab_p27/execution_hardening.json``,
``research_state/bab_p27/risk_controls.json``,
``research_state/bab_p27/reconciliation_e2e.json``).

They never import ``scripts`` or ``strategies`` and never call a ``build_*``
harness: every table in the report is re-rendered from JSON by the renderers
below and compared byte-for-byte with the checked-in markdown.

A hand-typed number, a stale table, a verdict contradicted by the evidence, or
a synthetic dry-run result quoted as market alpha fails the suite.
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
RESEARCH_P27_DIR = REPO_ROOT / "research_state/bab_p27"
REPORT_PATH = REPO_ROOT / "docs/BAB_P27_DECISION.md"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z0-9_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)
NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ISO_DATE = r"\d{4}-\d{2}-\d{2}"

WP0_SHA = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"

SOURCES = (
    "execution_hardening.json",
    "risk_controls.json",
    "reconciliation_e2e.json",
)


# --------------------------------------------------------------------------- #
# Loading (JSON only -- no harness build_* calls)
# --------------------------------------------------------------------------- #
def _load(name: str) -> dict:
    return json.loads((RESEARCH_P27_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def execution() -> dict:
    return _load("execution_hardening.json")


@pytest.fixture(scope="module")
def risk() -> dict:
    return _load("risk_controls.json")


@pytest.fixture(scope="module")
def reconciliation() -> dict:
    return _load("reconciliation_e2e.json")


@pytest.fixture(scope="module")
def report() -> str:
    return REPORT_PATH.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Table construction, derived from the committed JSON only
# --------------------------------------------------------------------------- #
def _cell(value) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, (list, tuple)):
        return ", ".join(_cell(v) for v in value)
    if isinstance(value, str):
        return value
    return f"{float(value):.{DECIMALS}f}"


def _render(columns, rows) -> list[str]:
    lines = ["| " + " | ".join(columns) + " |"]
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    for row in rows:
        lines.append("| " + " | ".join(_cell(row[column]) for column in columns) + " |")
    return lines


def provenance_table(execution, risk, reconciliation) -> tuple[list[str], list[dict]]:
    rows = [
        {"Fact": "Schema WP0", "Value": execution["schema"]},
        {"Fact": "Schema WP1", "Value": risk["schema"]},
        {"Fact": "Schema WP2", "Value": reconciliation["schema"]},
        {"Fact": "Campaign", "Value": "P27"},
        {"Fact": "WP", "Value": "WP3 - production readiness decision"},
        {"Fact": "Seed", "Value": execution["seed"]},
        {"Fact": "Synthetic", "Value": execution["synthetic"]},
        {"Fact": "Fixture path",
         "Value": execution["provenance"].get("fixture_path",
                                              "tests/fixtures/wide_bab_universe.csv")},
        {"Fact": "Fixture SHA256",
         "Value": "`" + execution["fixture_sha256"] + "`"},
        {"Fact": "WP0 fixture SHA256 match",
         "Value": execution["fixture_sha256"] == WP0_SHA},
        {"Fact": "WP1 fixture SHA256 match",
         "Value": risk["fixture_sha256"] == WP0_SHA},
        {"Fact": "WP2 fixture SHA256 match",
         "Value": reconciliation["fixture_sha256"] == WP0_SHA},
        {"Fact": "Price rows", "Value": execution["price_rows"]},
        {"Fact": "Return rows", "Value": execution["return_rows"]},
        {"Fact": "Beta window", "Value": execution["beta_window"]},
        {"Fact": "Min observations", "Value": execution["min_observations"]},
        {"Fact": "Long quantile", "Value": execution["long_quantile"]},
        {"Fact": "Short quantile", "Value": execution["short_quantile"]},
        {"Fact": "Rank min leg beta", "Value": execution["rank_min_leg_beta"]},
        {"Fact": "Rank max gross", "Value": execution["rank_max_gross"]},
        {"Fact": "No network", "Value": execution["no_network"]},
        {"Fact": "No lookahead", "Value": execution["provenance"]["no_lookahead"]},
    ]
    return ["Fact", "Value"], rows


def wp0_table(execution) -> tuple[list[str], list[dict]]:
    paper = execution["paper"]
    lifecycle = paper["lifecycle"]
    rows = [
        {"key": "adapter_present", "value": paper["adapter_present"]},
        {"key": "adapter_fills_match_engine",
         "value": paper["adapter_fills_match_engine"]},
        {"key": "adapter_n_intents", "value": paper["adapter_n_intents"]},
        {"key": "adapter_n_fills", "value": paper["adapter_n_fills"]},
        {"key": "n_orders", "value": paper["n_orders"]},
        {"key": "n_fills", "value": paper["n_fills"]},
        {"key": "n_diagnostics", "value": paper["n_diagnostics"]},
        {"key": "backtest_pnl", "value": paper["backtest_pnl"]},
        {"key": "lifecycle_valid", "value": lifecycle["lifecycle_valid"]},
        {"key": "fills_match_orders", "value": lifecycle["fills_match_orders"]},
        {"key": "n_fills_equals_n_orders",
         "value": lifecycle["n_fills_equals_n_orders"]},
        {"key": "no_orphan_fills", "value": lifecycle["no_orphan_fills"]},
        {"key": "no_double_submit", "value": lifecycle["no_double_submit"]},
        {"key": "no_fill_without_order",
         "value": lifecycle["no_fill_without_order"]},
        {"key": "weights_sum_zero", "value": lifecycle["weights_sum_zero"]},
        {"key": "beta_neutral", "value": lifecycle["beta_neutral"]},
        {"key": "determinism_byte_identical",
         "value": execution["determinism"]["byte_identical"]},
        {"key": "no_network", "value": execution["no_network"]},
    ]
    return ["key", "value"], rows


def wp0_diagnostics_table(execution) -> tuple[list[str], list[dict]]:
    columns = ["n_long", "n_short", "turnover", "beta_mean", "beta_median",
               "beta_std", "beta_min", "beta_max", "beta_neutrality_error",
               "hhi", "long_beta_boundary", "short_beta_boundary"]
    diagnostics = execution["paper"]["diagnostics"]
    rows = [{col: d[col] for col in columns} for d in diagnostics]
    return columns, rows


def wp1_table(risk) -> tuple[list[str], list[dict]]:
    kill_switch = risk["kill_switch"]
    position_weight = risk["position_weight"]
    staleness = risk["staleness"]
    gross_exposure = risk["gross_exposure"]
    kill_switch_none = risk["kill_switch_none"]
    kill_switch_rm = risk["kill_switch_risk_manager"]
    limits = risk["limits"]
    rows = [
        {"key": "risk_gates_all_trip", "value": risk["risk_gates_all_trip"]},
        {"key": "kill_switch_triggered", "value": kill_switch["triggered"]},
        {"key": "kill_switch_positions_flattened",
         "value": kill_switch["positions_flattened"]},
        {"key": "kill_switch_flattened_from_breach_date_onward",
         "value": kill_switch["flattened_from_breach_date_onward"]},
        {"key": "kill_switch_limit", "value": kill_switch["limit"]},
        {"key": "kill_switch_observed_drawdown",
         "value": kill_switch["observed_drawdown"]},
        {"key": "kill_switch_breach_date", "value": kill_switch["breach_date"]},
        {"key": "order_rejected", "value": position_weight["order_rejected"]},
        {"key": "staleness_trips", "value": staleness["trips"]},
        {"key": "staleness_limit_breach_events",
         "value": staleness["limit_breach_events"]},
        {"key": "gross_exposure_limit_breach",
         "value": gross_exposure["limit_breach"]},
        {"key": "gross_exposure_rejected", "value": gross_exposure["rejected"]},
        {"key": "kill_switch_none_byte_identical_default",
         "value": kill_switch_none["byte_identical_default_path"]},
        {"key": "kill_switch_none_weights_unchanged",
         "value": kill_switch_none["weights_unchanged"]},
        {"key": "risk_manager_event_types",
         "value": kill_switch_rm["event_types"]},
        {"key": "risk_manager_kill_switch_triggered",
         "value": kill_switch_rm["kill_switch_triggered"]},
        {"key": "risk_manager_position_flattened",
         "value": kill_switch_rm["position_flattened"]},
        {"key": "max_drawdown", "value": limits["max_drawdown"]},
        {"key": "max_gross_exposure", "value": limits["max_gross_exposure"]},
        {"key": "max_position_age_days", "value": limits["max_position_age_days"]},
        {"key": "max_position_weight", "value": limits["max_position_weight"]},
        {"key": "rank_min_leg_beta", "value": limits["rank_min_leg_beta"]},
        {"key": "rank_max_gross", "value": limits["rank_max_gross"]},
        {"key": "rank_min_leg_beta_unchanged",
         "value": risk["rank_min_leg_beta_unchanged"]},
        {"key": "rank_max_gross_unchanged",
         "value": risk["rank_max_gross_unchanged"]},
    ]
    return ["key", "value"], rows


def wp2_table(reconciliation) -> tuple[list[str], list[dict]]:
    paper_run = reconciliation["paper_run"]
    costs = paper_run["costs_aggregate"]
    fills = paper_run["fills_aggregate"]
    gates = {k: v for k, v in paper_run.items() if k.startswith("gate_")}
    stress = reconciliation["stress_scenarios"]
    rows = [
        {"key": "all_gates_trip", "value": reconciliation["all_gates_trip"]},
        {"key": "reconciliation_enforced",
         "value": paper_run["reconciliation_enforced"]},
        {"key": "n_periods_costs", "value": costs["n_periods"]},
        {"key": "n_periods_fills", "value": fills["n_periods"]},
        {"key": "costs_delta_max_abs", "value": costs["delta_max_abs"]},
        {"key": "costs_delta_mean", "value": costs["delta_mean"]},
        {"key": "costs_delta_total", "value": costs["delta_total"]},
        {"key": "costs_n_mismatches", "value": costs["n_mismatches"]},
        {"key": "costs_executed_total", "value": costs["executed_total"]},
        {"key": "costs_modeled_total", "value": costs["modeled_total"]},
        {"key": "fills_n_mismatches", "value": fills["n_mismatches"]},
        {"key": "fills_max_delta_abs", "value": fills["max_delta_abs"]},
        {"key": "fills_model_final_equity", "value": fills["model_final_equity"]},
        {"key": "fills_realized_final_equity",
         "value": fills["realized_final_equity"]},
        {"key": "gate_drift_exact_ok", "value": gates["gate_drift_exact_ok"]},
        {"key": "gate_drift_zero_ok", "value": gates["gate_drift_zero_ok"]},
        {"key": "gate_emit_only_ok", "value": gates["gate_emit_only_ok"]},
        {"key": "gate_max_mismatch_zero_ok",
         "value": gates["gate_max_mismatch_zero_ok"]},
        {"key": "stress_a_drift_above_tolerance_ok",
         "value": stress["a_drift_above_tolerance"]["ok"]},
        {"key": "stress_b_tolerance_exact_equal_ok",
         "value": stress["b_tolerance_exact_equal"]["ok"]},
        {"key": "stress_c_mismatch_above_limit_ok",
         "value": stress["c_mismatch_above_limit"]["ok"]},
        {"key": "stress_d_emit_only_ok",
         "value": stress["d_emit_only"]["ok"]},
        {"key": "stress_e_clean_path_ok",
         "value": stress["e_clean_path"]["ok"]},
        {"key": "observed_drift_max_abs",
         "value": stress["observed_drift_max_abs"]},
        {"key": "observed_n_mismatches",
         "value": stress["observed_n_mismatches"]},
        {"key": "rank_min_leg_beta", "value": reconciliation["rank_min_leg_beta"]},
        {"key": "rank_max_gross", "value": reconciliation["rank_max_gross"]},
        {"key": "rank_min_leg_beta_unchanged",
         "value": reconciliation["rank_min_leg_beta_unchanged"]},
        {"key": "rank_max_gross_unchanged",
         "value": reconciliation["rank_max_gross_unchanged"]},
    ]
    return ["key", "value"], rows


def live_table(execution) -> tuple[list[str], list[dict]]:
    health = execution["live_health_check"]
    detail = health["health"]
    rows = [
        {"key": "mode", "value": detail["mode"]},
        {"key": "exchange", "value": detail["exchange"]},
        {"key": "dry_run", "value": detail["dry_run"]},
        {"key": "dry_run_true", "value": health["dry_run_true"]},
        {"key": "never_implicit_live", "value": health["never_implicit_live"]},
        {"key": "strict_json", "value": health["strict_json"]},
        {"key": "has_required_keys", "value": health["has_required_keys"]},
        {"key": "mode_live", "value": health["mode_live"]},
        {"key": "connected", "value": detail["connected"]},
        {"key": "testnet", "value": detail["testnet"]},
        {"key": "n_submitted", "value": detail["n_submitted"]},
        {"key": "n_fills", "value": detail["n_fills"]},
        {"key": "no_network", "value": execution["no_network"]},
    ]
    return ["key", "value"], rows


def decision_table(execution, risk, reconciliation
                   ) -> tuple[list[str], list[dict]]:
    lifecycle = execution["paper"]["lifecycle"]
    kill_switch = risk["kill_switch"]
    position_weight = risk["position_weight"]
    staleness = risk["staleness"]
    gross_exposure = risk["gross_exposure"]
    paper_run = reconciliation["paper_run"]
    costs = paper_run["costs_aggregate"]
    fills = paper_run["fills_aggregate"]
    gates = {k: v for k, v in paper_run.items() if k.startswith("gate_")}
    stress = reconciliation["stress_scenarios"]
    health = execution["live_health_check"]
    detail = health["health"]
    fixture_sha = execution["fixture_sha256"]
    dry_run_true_actual = str(health["dry_run_true"])
    rows = [
        {"Criterion": "Explicit production-READY / NOT-READY verdict "
                      "for the BAB beta bet",
         "Required": True},
        {"Criterion": "WP0 paper lifecycle valid (lifecycle_valid=true)",
         "Required": lifecycle["lifecycle_valid"] is True},
        {"Criterion": "WP0 lifecycle invariants hold (lifecycle valid)",
         "Required": (lifecycle["no_orphan_fills"]
                      and lifecycle["no_double_submit"]
                      and lifecycle["no_fill_without_order"]
                      and lifecycle["weights_sum_zero"]
                      and lifecycle["beta_neutral"]) is True},
        {"Criterion": "WP1 risk_gates_all_trip == True",
         "Required": risk["risk_gates_all_trip"] is True},
        {"Criterion": "WP1 kill switch triggered + positions flattened",
         "Required": kill_switch["triggered"] is True
         and kill_switch["positions_flattened"] is True},
        {"Criterion": "WP1 order_rejected on per-leg weight violation",
         "Required": position_weight["order_rejected"] is True},
        {"Criterion": "WP1 staleness limit breach trips",
         "Required": staleness["trips"] is True},
        {"Criterion": "WP2 all_gates_trip == True",
         "Required": reconciliation["all_gates_trip"] is True},
        {"Criterion": "WP2 reconciliation_enforced == True",
         "Required": paper_run["reconciliation_enforced"] is True},
        {"Criterion": "WP2 fail-closed: drift-zero breached",
         "Required": gates["gate_drift_zero_ok"] is False},
        {"Criterion": "WP2 fail-closed: max-mismatch-zero breached",
         "Required": gates["gate_max_mismatch_zero_ok"] is False},
        {"Criterion": "WP2 emit-only passes (gate_emit_only_ok=True)",
         "Required": gates["gate_emit_only_ok"] is True},
        {"Criterion": "Live health check dry_run=true (actual "
         + dry_run_true_actual + ")",
         "Required": health["dry_run_true"] is True},
        {"Criterion": "Live health check no implicit live execution",
         "Required": health["never_implicit_live"] is True},
        {"Criterion": "Live health check strict JSON with required keys",
         "Required": health["strict_json"] is True
         and health["has_required_keys"] is True},
        {"Criterion": "Fixture SHA256 matches WP0 (" + fixture_sha + ")",
         "Required": (execution["fixture_sha256"] == WP0_SHA
                      and risk["fixture_sha256"] == WP0_SHA
                      and reconciliation["fixture_sha256"] == WP0_SHA)},
        {"Criterion": "rank_min_leg_beta=0.20 unchanged (never weakened)",
         "Required": execution["rank_min_leg_beta"] == 0.2
         and risk["rank_min_leg_beta"] == 0.2
         and reconciliation["rank_min_leg_beta"] == 0.2},
        {"Criterion": "rank_max_gross=4.0 unchanged (never weakened)",
         "Required": execution["rank_max_gross"] == 4.0
         and risk["rank_max_gross"] == 4.0
         and reconciliation["rank_max_gross"] == 4.0},
        {"Criterion": "Deterministic byte-identical artifacts (all three WPs)",
         "Required": (execution["determinism"]["byte_identical"]
                      and risk["determinism"]["byte_identical"]
                      and reconciliation["determinism"]["byte_identical"]) is True},
        {"Criterion": "Synthetic universe labelled controlled synthetic",
         "Required": (execution["synthetic"]
                      and risk["synthetic"]
                      and reconciliation["synthetic"]) is True},
        {"Criterion": "Not market evidence / no real alpha (P26 NO-SIGNAL)",
         "Required": True},
        {"Criterion": "No implicit live execution (n_submitted=0, n_fills=0, "
                      "connected=false)",
         "Required": (detail["n_submitted"] == 0
                      and detail["n_fills"] == 0
                      and detail["connected"] is False)},
    ]
    return ["Criterion", "Required"], rows


TABLE_BUILDERS = {
    "provenance": provenance_table,
    "wp0": wp0_table,
    "wp0_diagnostics": wp0_diagnostics_table,
    "wp1": wp1_table,
    "wp2": wp2_table,
    "live": live_table,
    "decision": decision_table,
}


def _args_for(name: str, execution, risk, reconciliation) -> dict:
    return {
        "provenance": {
            "execution": execution, "risk": risk,
            "reconciliation": reconciliation},
        "wp0": {"execution": execution},
        "wp0_diagnostics": {"execution": execution},
        "wp1": {"risk": risk},
        "wp2": {"reconciliation": reconciliation},
        "live": {"execution": execution},
        "decision": {
            "execution": execution, "risk": risk,
            "reconciliation": reconciliation},
    }[name]


def _built(name: str, execution, risk, reconciliation) -> list[str]:
    kwargs = _args_for(name, execution, risk, reconciliation)
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


def _allowed_numeric(execution, risk, reconciliation) -> set:
    allowed = set()
    allowed |= _numeric_leaves(execution)
    allowed |= _numeric_leaves(risk)
    allowed |= _numeric_leaves(reconciliation)
    return allowed


# --------------------------------------------------------------------------- #
# 1. Zero unmatched numbers in every table cell
# --------------------------------------------------------------------------- #
def test_report_exists_and_declares_its_sources(execution, risk,
                                                reconciliation, report) -> None:
    assert REPORT_PATH.is_file()
    for name in SOURCES:
        assert name in report, f"report never names its source {name}"


def test_every_published_number_matches_a_committed_json_field(
        execution, risk, reconciliation, report) -> None:
    allowed = _allowed_numeric(execution, risk, reconciliation)
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
    minimum = 100  # chartered minimum
    assert published, "report publishes no numeric table cells"
    assert len(published) >= minimum, (
        f"report publishes {len(published)} machine-checked cells, below the "
        f"chartered {minimum}"
    )
    assert unmatched == [], f"published numbers absent from JSON: " \
        f"{sorted(set(unmatched))}"


def test_zero_unmatched_cells_is_the_chartered_invariant(
        execution, risk, reconciliation, report) -> None:
    allowed = _allowed_numeric(execution, risk, reconciliation)
    unmatched = 0
    for body in _extract_tables(report).values():
        for row in _rows(body):
            for cell in row:
                clean = cell.replace("`", "").strip()
                if (NUMERIC_CELL.match(clean)
                        and round(float(clean), DECIMALS) not in allowed):
                    unmatched += 1
    assert unmatched == 0


def test_tables_are_byte_identical_to_the_json_renderers(
        execution, risk, reconciliation, report) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLE_BUILDERS), f"table anchors differ: " \
        f"{sorted(published)}"
    for name in TABLE_BUILDERS:
        expected = "\n".join(
            _built(name, execution, risk, reconciliation))
        assert published[name] == expected, f"table {name} drifted from " \
            f"its JSON artifact"


def test_prose_does_not_quote_unbacked_numbers(
        execution, risk, reconciliation, report) -> None:
    allowed = _allowed_numeric(execution, risk, reconciliation)
    text = re.sub(
        r"<!-- table:[a-z_]+:start -->.*?<!-- table:[a-z_]+:end -->",
        " ",
        report,
        flags=re.DOTALL,
    )
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(ISO_DATE, " ", text)
    text = re.sub(r"\b[0-9a-f]{40,}\b", " ", text)
    text = re.sub(r"§\s*\d+(?:\.\d+)*", " ", text)
    text = re.sub(r"\bP\d+-\d+\b", " ", text)
    text = re.sub(r"\b(?:P|WP)\d+\b", " ", text)
    # Chartered prose numbers that are not table data
    text = re.sub(r"\b6\b", " ", text)        # decimals
    text = re.sub(r"\b403\b", " ", text)      # Coinbase returns 403
    text = re.sub(r"\b2021\b", " ", text)     # year in dates
    text = re.sub(r"\b2022\b", " ", text)     # year in dates
    text = re.sub(r"\b0\.003\b", " ", text)   # idio vol (P25 concept)
    text = re.sub(r"\b0\.35\b", " ", text)    # beta range min
    text = re.sub(r"\b1\.90\b", " ", text)    # beta range max
    token = re.compile(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?(?![A-Za-z0-9_])")
    stray = {tok for tok in token.findall(text)
             if round(float(tok), DECIMALS) not in allowed}
    assert stray == set(), f"prose numbers with no JSON field: {sorted(stray)}"


# --------------------------------------------------------------------------- #
# 2. The verdict is explicit, machine-backed, and grounded in evidence
# --------------------------------------------------------------------------- #
def test_report_states_an_explicit_verdict(execution, risk, reconciliation,
                                           report) -> None:
    lowered = _flat(report)
    assert "verdict" in lowered
    assert "not-ready" in lowered
    assert "ready" in lowered
    assert "dry_run=true" in lowered
    assert "no implicit live" in lowered
    assert "controlled synthetic" in lowered
    assert "not market evidence" in lowered
    assert "no real alpha" in lowered
    assert "no demonstrated real-world profitability" in lowered


def test_report_refuses_a_market_go(report) -> None:
    lowered = _flat(report)
    assert "no demonstrated real-world profitability" in lowered
    assert "not real market data" in lowered
    assert "not market profitability evidence" in lowered
    assert "controlled synthetic" in lowered
    assert "never market alpha" in lowered


def test_report_covers_all_required_sections(report) -> None:
    headings = [line for line in report.splitlines() if line.startswith("## ")]
    lowered = " ".join(headings).lower()
    for required in (
        "provenance",
        "execution adapter hardening",
        "risk controls",
        "reconciliation enforcement",
        "live health check",
        "decision criteria",
        "does not prove",
        "next",
    ):
        assert required in lowered, f"missing section: {required}"


# --------------------------------------------------------------------------- #
# 3. Every criterion the verdict cites is internally consistent
# --------------------------------------------------------------------------- #
def test_execution_evidence_is_calibrated(execution) -> None:
    lifecycle = execution["paper"]["lifecycle"]
    paper = execution["paper"]

    # Paper lifecycle valid end-to-end
    assert lifecycle["lifecycle_valid"] is True
    assert lifecycle["fills_match_orders"] is True
    assert lifecycle["no_orphan_fills"] is True
    assert lifecycle["no_double_submit"] is True
    assert lifecycle["no_fill_without_order"] is True
    assert lifecycle["weights_sum_zero"] is True
    assert lifecycle["beta_neutral"] is True
    assert paper["adapter_present"] is True
    assert paper["adapter_fills_match_engine"] is True
    assert paper["n_orders"] == paper["n_fills"] == 13858

    # Determinism, no network, fixture SHA
    assert execution["determinism"]["byte_identical"] is True
    assert execution["no_network"] is True
    assert execution["fixture_sha256"] == WP0_SHA

    # rank_min_leg_beta / rank_max_gross unchanged
    assert execution["rank_min_leg_beta"] == 0.2
    assert execution["rank_max_gross"] == 4.0
    assert execution["rank_min_leg_beta_unchanged"] is True
    assert execution["rank_max_gross_unchanged"] is True


def test_risk_controls_evidence_is_calibrated(risk) -> None:
    kill_switch = risk["kill_switch"]
    position_weight = risk["position_weight"]
    staleness = risk["staleness"]
    gross_exposure = risk["gross_exposure"]
    limits = risk["limits"]

    # All risk gates trip
    assert risk["risk_gates_all_trip"] is True

    # Kill switch on max drawdown: triggered + flattened
    assert kill_switch["triggered"] is True
    assert kill_switch["positions_flattened"] is True
    assert kill_switch["flattened_from_breach_date_onward"] is True
    assert kill_switch["limit"] == 0.1
    assert kill_switch["observed_drawdown"] == -0.15

    # Per-leg weight cap rejects oversized legs
    assert position_weight["order_rejected"] is True

    # Staleness position-age breach trips
    assert staleness["trips"] is True
    assert staleness["limit_breach_events"] == 1

    # Gross/net exposure batch rejection
    assert gross_exposure["limit_breach"] is True
    assert gross_exposure["rejected"] is True

    # No-limit default path is byte-identical, weights unchanged
    assert risk["kill_switch_none"]["byte_identical_default_path"] is True
    assert risk["kill_switch_none"]["weights_unchanged"] is True

    # rank_min_leg_beta / rank_max_gross unchanged
    assert risk["rank_min_leg_beta"] == 0.2
    assert risk["rank_max_gross"] == 4.0
    assert risk["rank_min_leg_beta_unchanged"] is True
    assert risk["rank_max_gross_unchanged"] is True

    # Fixture SHA256 matches WP0
    assert risk["fixture_sha256"] == WP0_SHA


def test_reconciliation_evidence_is_calibrated(reconciliation) -> None:
    paper_run = reconciliation["paper_run"]
    costs = paper_run["costs_aggregate"]
    fills = paper_run["fills_aggregate"]
    gates = {k: v for k, v in paper_run.items() if k.startswith("gate_")}
    stress = reconciliation["stress_scenarios"]

    # All gates trip, reconciliation enforced
    assert reconciliation["all_gates_trip"] is True
    assert paper_run["reconciliation_enforced"] is True

    # Fail-closed gates
    assert gates["gate_drift_zero_ok"] is False
    assert gates["gate_max_mismatch_zero_ok"] is False
    assert gates["gate_emit_only_ok"] is True

    # Stress scenarios: drift above tolerance fails, tolerance exact passes,
    # mismatch above limit fails, emit-only passes, clean path passes
    assert stress["a_drift_above_tolerance"]["ok"] is False
    assert stress["b_tolerance_exact_equal"]["ok"] is True
    assert stress["c_mismatch_above_limit"]["ok"] is False
    assert stress["d_emit_only"]["ok"] is True
    assert stress["e_clean_path"]["ok"] is True

    # Cost drift and mismatch counts
    assert costs["delta_max_abs"] == 0.000762
    assert costs["n_mismatches"] == 338
    assert fills["n_mismatches"] == 0

    # rank_min_leg_beta / rank_max_gross unchanged
    assert reconciliation["rank_min_leg_beta"] == 0.2
    assert reconciliation["rank_max_gross"] == 4.0
    assert reconciliation["rank_min_leg_beta_unchanged"] is True
    assert reconciliation["rank_max_gross_unchanged"] is True

    # Fixture SHA256 matches WP0
    assert reconciliation["fixture_sha256"] == WP0_SHA


def test_live_health_check_evidence_is_calibrated(execution) -> None:
    health = execution["live_health_check"]
    detail = health["health"]

    assert health["dry_run_true"] is True
    assert health["never_implicit_live"] is True
    assert health["strict_json"] is True
    assert health["has_required_keys"] is True
    assert health["mode_live"] is True
    assert detail["mode"] == "live"
    assert detail["exchange"] == "binance"
    assert detail["dry_run"] is True
    assert detail["connected"] is False
    assert detail["testnet"] is False
    assert detail["n_submitted"] == 0
    assert detail["n_fills"] == 0


def test_fixture_shas_agree(execution, risk, reconciliation) -> None:
    # Verify the fixture SHA256 in each artifact matches the actual WP0 fixture
    fixture_path = (
        Path(__file__).resolve().parent.parent
        / "tests/fixtures/wide_bab_universe.csv"
    )
    actual = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
    assert execution["fixture_sha256"] == actual
    assert risk["fixture_sha256"] == actual
    assert reconciliation["fixture_sha256"] == actual


# --------------------------------------------------------------------------- #
# 4. The test itself never re-runs a harness and never edits an artifact
# --------------------------------------------------------------------------- #
def test_report_consistency_never_executes_a_research_harness() -> None:
    tree = ast.parse(TEST_PATH.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                assert not func.attr.startswith("build_"), f"harness call: " \
                    f"{func.attr}"
            elif isinstance(func, ast.Name):
                assert not func.id.startswith("build_"), f"harness call: " \
                    f"{func.id}"
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert not module.startswith(("scripts", "strategies")), module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith(("scripts", "strategies")), \
                    alias.name
    start = time.perf_counter()
    _load("execution_hardening.json")
    _load("risk_controls.json")
    _load("reconciliation_e2e.json")
    REPORT_PATH.read_text(encoding="utf-8")
    assert time.perf_counter() - start < 2.0


def test_decision_artifacts_are_byte_identical_after_the_suite(
        execution, risk, reconciliation) -> None:
    for name in SOURCES:
        before = hashlib.sha256(
            (RESEARCH_P27_DIR / name).read_bytes()
        ).hexdigest()
        _load(name)
        after = hashlib.sha256(
            (RESEARCH_P27_DIR / name).read_bytes()
        ).hexdigest()
        assert before == after


# --------------------------------------------------------------------------- #
# 5. Ruff
# --------------------------------------------------------------------------- #
def test_no_ruff_errors_on_new_files():
    import subprocess
    import sys
    GENERATE_SCRIPT = REPO_ROOT / "generate_p27_decision.py"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            str(GENERATE_SCRIPT),
            str(__file__),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"ruff must pass on new files: {result.stdout} {result.stderr}"
    )
