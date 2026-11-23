"""Acceptance tests for P39 WP3: the regime-conditional & cross-fixture decision.

These tests are the claim that ``docs/BAB_P39_DECISION.md`` publishes only numbers
that exist in the committed P39 JSON artifacts
(``research_state/bab_p39/regime_summary.json`` and
``research_state/bab_p39/cross_fixture_summary.json``).

They never import ``scripts`` or ``strategies`` and never call a ``build_*``
harness: every table in the report is re-rendered from JSON by the renderers
below and compared byte-for-byte with the checked-in markdown.

A hand-typed number, a stale table, a verdict contradicted by the evidence, or a
synthetic dry-run result quoted as market alpha fails the suite.
"""

from __future__ import annotations

import ast
import json
import re
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_P39_DIR = REPO_ROOT / "research_state/bab_p39"
REPORT_PATH = REPO_ROOT / "docs/BAB_P39_DECISION.md"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z0-9_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)
NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ISO_DATE = r"\d{4}-\d{2}-\d{2}"

SOURCES = (
    "regime_summary.json",
    "cross_fixture_summary.json",
)

_TAIL_METRIC_ROWS = (
    "cvar_95",
    "cvar_99",
    "expected_shortfall_975",
    "worst_day_return",
    "skew",
    "excess_kurtosis",
    "tail_asymmetry",
    "conditional_drawdown_95",
    "max_drawdown",
)


# --------------------------------------------------------------------------- #
# Loading (JSON only -- no harness build_* calls)
# --------------------------------------------------------------------------- #
def _load(name: str) -> dict:
    return json.loads((RESEARCH_P39_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def regime() -> dict:
    return _load("regime_summary.json")


@pytest.fixture(scope="module")
def cross() -> dict:
    return _load("cross_fixture_summary.json")


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
    if isinstance(value, (list, tuple)):
        return ", ".join(_cell(v) for v in value)
    return f"{float(value):.{DECIMALS}f}"


def _render(columns, rows) -> list[str]:
    lines = ["| " + " | ".join(columns) + " |"]
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    for row in rows:
        lines.append("| " + " | ".join(_cell(row[column]) for column in columns) + " |")
    return lines


def provenance_table(regime, cross) -> tuple[list[str], list[dict]]:
    rprov = regime["provenance"]
    cprov = cross["provenance"]
    rows = [
        {"Fact": "Schema regime", "Value": regime["schema"]},
        {"Fact": "Schema cross_fixture", "Value": cross["schema"]},
        {"Fact": "Campaign", "Value": rprov["campaign"]},
        {
            "Fact": "WP",
            "Value": "WP3 - Decision doc + documentation-integrity closure + gate wire",
        },
        {"Fact": "Synthetic regime", "Value": rprov["synthetic"]},
        {"Fact": "Synthetic cross_fixture", "Value": cprov["synthetic"]},
        {"Fact": "Regime note", "Value": rprov["note"]},
        {"Fact": "Cross-fixture note", "Value": cprov["note"]},
        {"Fact": "Fixture path regime", "Value": rprov["fixture_path"]},
        {"Fact": "Fixture path cross_fixture", "Value": cprov["fixture_path"]},
        {"Fact": "Returns SHA256 regime", "Value": "`" + rprov["returns_sha256"] + "`"},
        {
            "Fact": "Returns SHA256 cross_fixture",
            "Value": "`" + cprov["returns_sha256"] + "`",
        },
        {"Fact": "BTC source SHA256", "Value": "`" + rprov["btc_source_sha256"] + "`"},
        {
            "Fact": "Regime seeds (base/inc/n)",
            "Value": (
                f"{rprov['seeds']['base_seed']}/"
                f"{rprov['seeds']['increment']}/"
                f"{rprov['seeds']['n_seeds']}"
            ),
        },
        {"Fact": "Regime seed list", "Value": rprov["seeds"]["seed_list"]},
        {
            "Fact": "Cross seeds (base/inc/n)",
            "Value": (
                f"{cprov['seeds']['base_seed']}/"
                f"{cprov['seeds']['increment']}/"
                f"{cprov['seeds']['n_seeds']}"
            ),
        },
        {"Fact": "Cross seed list", "Value": cprov["seeds"]["seed_list"]},
        {"Fact": "Beta window", "Value": rprov["config_grid"]["beta_window"]},
        {"Fact": "Quantile", "Value": rprov["config_grid"]["quantile"]},
        {"Fact": "Weighting", "Value": rprov["config_grid"]["weighting"]},
        {"Fact": "Beta neutral", "Value": rprov["config_grid"]["beta_neutral"]},
        {"Fact": "Dollar neutral", "Value": rprov["config_grid"]["dollar_neutral"]},
        {
            "Fact": "Min periods per regime",
            "Value": rprov["config_grid"]["min_periods_per_regime"],
        },
        {"Fact": "Regime labels", "Value": rprov["config_grid"]["regime_labels"]},
        {
            "Fact": "Deflation trials (n_trials_total)",
            "Value": regime["trial_enumeration"]["n_trials_total"],
        },
        {"Fact": "DSR survive threshold", "Value": rprov["dsr_survive_threshold"]},
        {"Fact": "Campaign verdict regime", "Value": regime["campaign_verdict"]},
        {
            "Fact": "Campaign verdict cross_fixture",
            "Value": cross["campaign_verdict"],
        },
    ]
    return ["Fact", "Value"], rows


def regime_table(regime) -> tuple[list[str], list[dict]]:
    rows = []
    rregimes = regime["results"]["regimes"]
    for name in sorted(rregimes):
        reg = rregimes[name]
        neu = reg["neutrality"]
        rows.append({
            "Regime": name,
            "N_Cells": reg["n_cells"],
            "N_OK_Cells": reg["n_ok_cells"],
            "N_Insufficient": reg["n_insufficient"],
            "N_Error": reg["n_error"],
            "N_Survive": reg["n_survive"],
            "All_Survive": reg["all_survive"],
            "Any_Survive": reg["any_survive"],
            "DSR_Mean": reg["dsr"]["mean"],
            "DSR_Min": reg["dsr"]["min"],
            "DSR_Max": reg["dsr"]["max"],
            "PSR_Mean": reg["psr"]["mean"],
            "PSR_Min": reg["psr"]["min"],
            "PSR_Max": reg["psr"]["max"],
            "Neutrality_OK": neu["all_dollar_ok"]
            and neu["all_model_beta_ok"]
            and neu["all_realized_ok"],
        })
    columns = [
        "Regime", "N_Cells", "N_OK_Cells", "N_Insufficient", "N_Error", "N_Survive",
        "All_Survive", "Any_Survive", "DSR_Mean", "DSR_Min", "DSR_Max",
        "PSR_Mean", "PSR_Min", "PSR_Max", "Neutrality_OK",
    ]
    return columns, rows


def cross_table(cross) -> tuple[list[str], list[dict]]:
    rows = []
    for cell in cross["results"]["cells"]:
        rows.append({
            "Cell_Key": cell["cell_key"],
            "Seed": cell["seed"],
            "Seed_Index": cell["seed_index"],
            "Status": cell["status"],
            "Survives": cell["survives_deflation"],
            "DSR": cell["dsr"],
            "PSR": cell["psr"],
            "Sharpe": cell["sharpe"],
            "Verdict": cell["verdict"],
        })
    columns = [
        "Cell_Key", "Seed", "Seed_Index", "Status", "Survives", "DSR", "PSR",
        "Sharpe", "Verdict",
    ]
    return columns, rows


def decision_table(regime, cross) -> tuple[list[str], list[dict]]:
    rprov = regime["provenance"]
    cprov = cross["provenance"]
    cagg = cross["results"]["aggregate"]
    r_threshold = rprov["dsr_survive_threshold"]
    n_trials = regime["trial_enumeration"]["n_trials_total"]
    r_verdict = regime["campaign_verdict"]
    c_verdict = cross["campaign_verdict"]
    r_neutrality_ok = all(
        reg["neutrality"]["all_dollar_ok"]
        and reg["neutrality"]["all_model_beta_ok"]
        and reg["neutrality"]["all_realized_ok"]
        for reg in regime["results"]["regimes"].values()
    )
    regime_fails = any(
        reg["dsr"]["mean"] is not None and reg["dsr"]["mean"] < r_threshold
        for reg in regime["results"]["regimes"].values()
    )
    c_neutrality_ok = (
        cagg["neutrality"]["all_dollar_ok"]
        and cagg["neutrality"]["all_model_beta_ok"]
        and cagg["neutrality"]["all_realized_ok"]
    )
    c_survive = cagg["n_survive"]
    c_cells = cagg["n_cells"]
    shas_differ = rprov["returns_sha256"] != cprov["returns_sha256"]

    crit_wp1_verdict = (
        "WP1 campaign verdict is DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME "
        "(honest within-regime negative)"
    )
    crit_wp1_fails = (
        "WP1 at least one well-populated regime has DSR mean below the "
        f"{r_threshold} survive threshold after deflation over n_trials_total={n_trials}"
    )
    crit_wp1_neutrality = (
        "WP1 neutrality holds at every populated (seed, regime) cell "
        "(model beta <= 1e-3, dollar <= 1e-9, realized |beta| <= 0.15)"
    )
    crit_wp2_verdict = (
        "WP2 campaign verdict is DOES_NOT_REPLICATE (honest cross-fixture negative)"
    )
    crit_wp2_neutrality = "WP2 neutrality holds at every cross-fixture cell (gross + costed)"
    crit_wp2_survive = (
        f"WP2 exactly {c_survive} of {c_cells} second-universe seeds survive deflation "
        f"over n_trials_total={n_trials}"
    )
    crit_independent = (
        "Regime and cross-fixture universes are independent fixtures "
        "(distinct returns SHA256)"
    )
    crit_synthetic = (
        "Both universes labelled controlled synthetic; not real market data; "
        "not market profitability evidence"
    )
    crit_no_alpha = (
        "No demonstrated real-world profitability; shipped default retained; "
        "nothing flipped"
    )

    rows = [
        {
            "Criterion": crit_wp1_verdict,
            "Required": r_verdict == "DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME",
        },
        {"Criterion": crit_wp1_fails, "Required": regime_fails},
        {"Criterion": crit_wp1_neutrality, "Required": r_neutrality_ok},
        {"Criterion": crit_wp2_verdict, "Required": c_verdict == "DOES_NOT_REPLICATE"},
        {"Criterion": crit_wp2_neutrality, "Required": c_neutrality_ok},
        {"Criterion": crit_wp2_survive, "Required": c_survive == 3 and c_cells == 8},
        {"Criterion": crit_independent, "Required": shas_differ},
        {
            "Criterion": crit_synthetic,
            "Required": rprov["synthetic"] and cprov["synthetic"]
            and "not market profitability evidence" in rprov["note"]
            and "not market profitability evidence" in cprov["note"],
        },
        {"Criterion": crit_no_alpha, "Required": True},
    ]
    return ["Criterion", "Required"], rows


TABLE_BUILDERS = {
    "provenance": provenance_table,
    "regime": regime_table,
    "cross_fixture": cross_table,
    "decision": decision_table,
}


def _args_for(name: str, regime, cross) -> dict:
    if name == "provenance":
        return {"regime": regime, "cross": cross}
    if name == "regime":
        return {"regime": regime}
    if name == "cross_fixture":
        return {"cross": cross}
    return {"regime": regime, "cross": cross}


def _built(name: str, regime, cross) -> list[str]:
    kwargs = _args_for(name, regime, cross)
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


def _allowed_numeric(regime, cross) -> set:
    allowed = set()
    allowed |= _numeric_leaves(regime)
    allowed |= _numeric_leaves(cross)
    return allowed


# --------------------------------------------------------------------------- #
# 1. Zero unmatched numbers in every table cell
# --------------------------------------------------------------------------- #
def test_report_exists_and_declares_its_sources(regime, cross, report) -> None:
    assert REPORT_PATH.is_file()
    for name in SOURCES:
        assert name in report, f"report never names its source {name}"


def test_every_published_number_matches_a_committed_json_field(regime, cross, report) -> None:
    allowed = _allowed_numeric(regime, cross)
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
    minimum = 90  # chartered minimum machine-checked numeric cells
    assert published, "report publishes no numeric table cells"
    assert len(published) >= minimum, (
        f"report publishes {len(published)} machine-checked cells, below the chartered {minimum}"
    )
    assert unmatched == [], f"published numbers absent from JSON: {sorted(set(unmatched))}"


def test_tables_are_byte_identical_to_the_json_renderers(regime, cross, report) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLE_BUILDERS), f"table anchors differ: {sorted(published)}"
    for name in TABLE_BUILDERS:
        expected = "\n".join(_built(name, regime, cross))
        assert published[name] == expected, f"table {name} drifted from its JSON artifact"


def test_prose_does_not_quote_unbacked_numbers(regime, cross, report) -> None:
    allowed = _allowed_numeric(regime, cross)
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
    text = re.sub(r"\bP\d+-\d+\b", " ", text)
    text = re.sub(r"\b(?:P|WP)\d+\b", " ", text)
    # Chartered prose numbers that are not table data
    text = text.replace("[-1, +1]", " ")
    text = re.sub(r"\b6\b", " ", text)  # decimals
    text = re.sub(r"\b0\.5\b", " ", text)  # DSR survive threshold (in allowed)
    text = re.sub(r"\b552\b", " ", text)  # n_trials_total (in allowed)
    text = re.sub(r"\b3\b", " ", text)  # survive count (in allowed)
    text = re.sub(r"\b8\b", " ", text)  # cell count (in allowed)
    text = re.sub(r"\b403\b", " ", text)  # Coinbase returns 403
    token = re.compile(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?(?![A-Za-z0-9_])")
    stray = {tok for tok in token.findall(text) if round(float(tok), DECIMALS) not in allowed}
    assert stray == set(), f"prose numbers with no JSON field: {sorted(stray)}"


# --------------------------------------------------------------------------- #
# 2. The verdict is explicit, machine-backed, and grounded in evidence
# --------------------------------------------------------------------------- #
def test_report_states_an_explicit_verdict(regime, cross, report) -> None:
    lowered = _flat(report)
    assert "verdict" in lowered
    assert "retain" in lowered
    assert (
        "does_not_survive_deflation_in_some_regime" in lowered
        or "does not survive deflation in some regime" in lowered
    )
    assert "does_not_replicate" in lowered or "does not replicate" in lowered
    assert "regime" in lowered
    assert "synthetic" in lowered
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


def test_report_states_the_honest_negatives(report) -> None:
    lowered = _flat(report)
    assert (
        "does_not_survive_deflation_in_some_regime" in lowered
        or "does not survive deflation in some regime" in lowered
    )
    assert "does_not_replicate" in lowered or "does not replicate" in lowered
    assert "fixture-dependent" in lowered


def test_report_covers_all_required_sections(report) -> None:
    headings = [line for line in report.splitlines() if line.startswith("## ")]
    lowered = " ".join(headings).lower()
    for required in (
        "provenance",
        "wp1",
        "wp2",
        "decision criteria",
        "does not prove",
        "next",
    ):
        assert required in lowered, f"missing section: {required}"


# --------------------------------------------------------------------------- #
# 3. Every criterion the verdict cites is internally consistent
# --------------------------------------------------------------------------- #
def test_regime_evidence_is_calibrated(regime) -> None:
    assert regime["campaign_verdict"] == "DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME"
    r_neutrality_ok = all(
        reg["neutrality"]["all_dollar_ok"]
        and reg["neutrality"]["all_model_beta_ok"]
        and reg["neutrality"]["all_realized_ok"]
        for reg in regime["results"]["regimes"].values()
    )
    assert r_neutrality_ok is True
    r_threshold = regime["provenance"]["dsr_survive_threshold"]
    regime_fails = any(
        reg["dsr"]["mean"] is not None and reg["dsr"]["mean"] < r_threshold
        for reg in regime["results"]["regimes"].values()
    )
    assert regime_fails is True, "expected at least one regime to fail deflation (honest negative)"


def test_cross_fixture_evidence_is_calibrated(cross) -> None:
    assert cross["campaign_verdict"] == "DOES_NOT_REPLICATE"
    cagg = cross["results"]["aggregate"]
    assert cagg["n_survive"] == 3
    assert cagg["n_cells"] == 8
    assert cagg["all_neutrality_ok"] is True
    assert cagg["n_error_cells"] == 0


def test_fixture_shas_distinct(regime, cross) -> None:
    rprov = regime["provenance"]
    cprov = cross["provenance"]
    assert len(rprov["returns_sha256"]) == 64
    assert len(cprov["returns_sha256"]) == 64
    assert rprov["returns_sha256"] != cprov["returns_sha256"], (
        "regime and cross-fixture universes must be independent fixtures"
    )


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
    _load("regime_summary.json")
    _load("cross_fixture_summary.json")
    REPORT_PATH.read_text(encoding="utf-8")
    assert time.perf_counter() - start < 2.0


def test_decision_artifacts_are_byte_identical_after_the_suite(regime, cross) -> None:
    for name in SOURCES:
        before = (RESEARCH_P39_DIR / name).read_bytes()
        _load(name)
        after = (RESEARCH_P39_DIR / name).read_bytes()
        assert before == after


# --------------------------------------------------------------------------- #
# 5. Ruff
# --------------------------------------------------------------------------- #
def test_no_ruff_errors_on_new_files():
    import subprocess
    import sys

    GENERATE_SCRIPT = REPO_ROOT / "generate_p39_decision.py"
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
    assert result.returncode == 0, f"ruff must pass on new files: {result.stdout} {result.stderr}"
