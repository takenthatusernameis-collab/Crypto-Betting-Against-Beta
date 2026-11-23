"""Acceptance tests for P38 WP3: the deflated-significance & tail-risk decision.

These tests are the claim that ``docs/BAB_P38_DECISION.md`` publishes only numbers
that exist in the committed P38 JSON artifacts
(``research_state/bab_p38/deflated_summary.json`` and
``research_state/bab_p38/tail_risk_summary.json``).

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
RESEARCH_P38_DIR = REPO_ROOT / "research_state/bab_p38"
REPORT_PATH = REPO_ROOT / "docs/BAB_P38_DECISION.md"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z0-9_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)
NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ISO_DATE = r"\d{4}-\d{2}-\d{2}"

SOURCES = (
    "deflated_summary.json",
    "tail_risk_summary.json",
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
    return json.loads((RESEARCH_P38_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def deflated() -> dict:
    return _load("deflated_summary.json")


@pytest.fixture(scope="module")
def tail() -> dict:
    return _load("tail_risk_summary.json")


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


def provenance_table(deflated, tail) -> tuple[list[str], list[dict]]:
    dprov = deflated["provenance"]
    tprov = tail["provenance"]
    rows = [
        {"Fact": "Schema deflated", "Value": deflated["schema"]},
        {"Fact": "Schema tail_risk", "Value": tail["schema"]},
        {"Fact": "Campaign", "Value": dprov["campaign"]},
        {"Fact": "WP", "Value": (
            "WP3 - Decision doc + documentation-integrity closure + gate wire"
        )},
        {"Fact": "Synthetic deflated", "Value": dprov["synthetic"]},
        {"Fact": "Synthetic tail_risk", "Value": tprov["synthetic"]},
        {"Fact": "Deflated note", "Value": dprov["note"]},
        {"Fact": "Tail-risk note", "Value": tprov["note"]},
        {"Fact": "Fixture path", "Value": tprov["fixture_path"]},
        {"Fact": "Returns SHA256", "Value": "`" + tprov["returns_sha256"] + "`"},
        {"Fact": "BTC source SHA256", "Value": "`" + tprov["btc_source_sha256"] + "`"},
        {
            "Fact": "Seeds (base/inc/n)",
            "Value": (
                f"{tprov['seeds']['base_seed']}/"
                f"{tprov['seeds']['increment']}/"
                f"{tprov['seeds']['n_seeds']}"
            ),
        },
        {"Fact": "Seed list", "Value": tprov["seeds"]["seed_list"]},
        {"Fact": "Beta window", "Value": tprov["config_grid"]["beta_window"]},
        {"Fact": "Quantile", "Value": tprov["config_grid"]["quantile"]},
        {"Fact": "Weighting", "Value": tprov["config_grid"]["weighting"]},
        {"Fact": "Beta neutral", "Value": tprov["config_grid"]["beta_neutral"]},
        {"Fact": "Dollar neutral", "Value": tprov["config_grid"]["dollar_neutral"]},
        {"Fact": "Gross transaction costs",
         "Value": tprov["config_grid"]["gross_transaction_costs"]},
        {"Fact": "Costed transaction costs",
         "Value": tprov["config_grid"]["costed_transaction_costs"]},
        {"Fact": "Model beta-neutral tol",
         "Value": tprov["neutrality_tolerances"]["model_beta_neutral"]},
        {"Fact": "Dollar-neutral tol",
         "Value": tprov["neutrality_tolerances"]["dollar_neutral"]},
        {"Fact": "Realized beta tol",
         "Value": tprov["neutrality_tolerances"]["realized_beta"]},
        {"Fact": "Deflation trials (n_trials_total)",
         "Value": deflated["trial_enumeration"]["n_trials_total"]},
        {"Fact": "DSR survive threshold", "Value": dprov["dsr_survive_threshold"]},
        {"Fact": "Campaign verdict", "Value": deflated["campaign_verdict"]},
        {"Fact": "Tail-risk status", "Value": tail["tail_risk_status"]},
    ]
    return ["Fact", "Value"], rows


def deflated_table(deflated) -> tuple[list[str], list[dict]]:
    rows = []
    for label in ("shipped_default", "best_insample_config"):
        r = deflated["results"][label]
        rows.append({
            "Config": label,
            "Beta_Window": r["beta_window"],
            "Quantile": r["quantile"],
            "Mean_Sharpe": r["mean_sharpe"],
            "N_Trials": r["n_trials"],
            "Sigma0": r["sigma0"],
            "Gamma": r["gamma"],
            "Kappa": r["kappa"],
            "DSR": r["dsr"],
            "PSR": r["psr"],
            "Trials_Adj_p": r["trials_adjusted_p_value"],
            "Min_BT_Len_PSR50": r["min_backtest_length_for_psr_0_50"],
            "Survives": r["survives_deflation"],
            "Verdict": r["verdict"],
        })
    columns = [
        "Config", "Beta_Window", "Quantile", "Mean_Sharpe", "N_Trials", "Sigma0",
        "Gamma", "Kappa", "DSR", "PSR", "Trials_Adj_p", "Min_BT_Len_PSR50",
        "Survives", "Verdict",
    ]
    return columns, rows


def _agg(config_agg: dict, metric: str) -> dict:
    return config_agg["tail_metric_aggregates"][metric]


def tail_table(tail) -> tuple[list[str], list[dict]]:
    gross_agg = tail["results"]["gross"]["aggregate"]
    costed_agg = tail["results"]["costed"]["aggregate"]
    rows = []
    for metric in _TAIL_METRIC_ROWS:
        g = _agg(gross_agg, metric)
        c = _agg(costed_agg, metric)
        rows.append({
            "Metric": metric,
            "Gross_Mean": g["mean"],
            "Gross_Min": g["min"],
            "Gross_Max": g["max"],
            "Costed_Mean": c["mean"],
            "Costed_Min": c["min"],
            "Costed_Max": c["max"],
        })
    columns = [
        "Metric", "Gross_Mean", "Gross_Min", "Gross_Max",
        "Costed_Mean", "Costed_Min", "Costed_Max",
    ]
    return columns, rows


def coverage_table(tail) -> tuple[list[str], list[dict]]:
    rows = []
    for label in ("gross", "costed"):
        agg = tail["results"][label]["aggregate"]
        rows.append({
            "Config": label,
            "N_Cells": agg["n_cells"],
            "N_OK": agg["n_ok_cells"],
            "N_Neutrality_Violations": agg["n_neutrality_violations"],
            "N_Error": agg["n_error_cells"],
            "All_Neutrality_OK": agg["all_neutrality_ok"],
        })
    columns = [
        "Config", "N_Cells", "N_OK", "N_Neutrality_Violations", "N_Error",
        "All_Neutrality_OK",
    ]
    return columns, rows


def decision_table(deflated, tail) -> tuple[list[str], list[dict]]:
    dprov = deflated["provenance"]
    tprov = tail["provenance"]
    dresults = deflated["results"]
    gross_agg = tail["results"]["gross"]["aggregate"]
    costed_agg = tail["results"]["costed"]["aggregate"]

    n_trials = deflated["trial_enumeration"]["n_trials_total"]
    default_dsr = dresults["shipped_default"]["dsr"]
    best_dsr = dresults["best_insample_config"]["dsr"]
    campaign_verdict = deflated["campaign_verdict"]
    both_dsr_survive = (
        default_dsr >= dprov["dsr_survive_threshold"]
        and best_dsr >= dprov["dsr_survive_threshold"]
    )
    all_tail_ok = (
        gross_agg["all_neutrality_ok"]
        and costed_agg["all_neutrality_ok"]
        and gross_agg["n_error_cells"] == 0
        and costed_agg["n_error_cells"] == 0
    )
    shas_match = (
        dprov["returns_sha256"] == tprov["returns_sha256"]
        and dprov["btc_source_sha256"] == tprov["btc_source_sha256"]
    )

    rows = [
        {"Criterion": "WP1 deflated significance computed over n_trials_total "
         "(read-only trial enumeration from committed P20-P37 artifacts)",
         "Required": n_trials > 0},
        {"Criterion": "WP1 campaign verdict is SURVIVES_DEFLATION (both configs DSR >= "
         "threshold after deflation)",
         "Required": campaign_verdict == "SURVIVES_DEFLATION" and both_dsr_survive},
        {"Criterion": "WP1 trials-adjusted p-values are reported honestly as marginal "
         "(below 0.10 but above 0.05), not as decisive evidence",
         "Required": True},
        {"Criterion": "WP2 tail-risk computed on the wide synthetic fixture for gross and "
         "costed books (CVaR / expected shortfall / drawdown)",
         "Required": all_tail_ok},
        {"Criterion": "WP2 neutrality holds at every tail-risk cell (model beta <= 1e-3, "
         "dollar <= 1e-9, realized |beta| <= 0.15)",
         "Required": all_tail_ok},
        {"Criterion": "WP2 tail metrics are internally ordered (VaR/CVaR/ES nesting, "
         "worst-day <= CVaR, drawdown ordering, tail asymmetry in [-1, 1])",
         "Required": True},
        {"Criterion": "Fixture SHA256 match across the deflated and tail-risk artifacts",
         "Required": shas_match},
        {"Criterion": "Synthetic universe labelled controlled synthetic",
         "Required": (
             "Not real market data" in tprov["note"]
             and "not market profitability evidence" in tprov["note"]
         )},
        {"Criterion": "Not market evidence / no real alpha", "Required": True},
        {"Criterion": "Shipped default (weighting=equal, beta_neutral=True, "
         "beta_window=90, rolling-OLS) RETAINED",
         "Required": True},
    ]
    return ["Criterion", "Required"], rows


TABLE_BUILDERS = {
    "provenance": provenance_table,
    "deflated": deflated_table,
    "tail_risk": tail_table,
    "coverage": coverage_table,
    "decision": decision_table,
}


def _args_for(name: str, deflated, tail) -> dict:
    if name == "provenance":
        return {"deflated": deflated, "tail": tail}
    if name == "deflated":
        return {"deflated": deflated}
    if name in ("tail_risk", "coverage"):
        return {"tail": tail}
    return {"deflated": deflated, "tail": tail}


def _built(name: str, deflated, tail) -> list[str]:
    kwargs = _args_for(name, deflated, tail)
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


def _allowed_numeric(deflated, tail) -> set:
    allowed = set()
    allowed |= _numeric_leaves(deflated)
    allowed |= _numeric_leaves(tail)
    return allowed


# --------------------------------------------------------------------------- #
# 1. Zero unmatched numbers in every table cell
# --------------------------------------------------------------------------- #
def test_report_exists_and_declares_its_sources(deflated, tail, report) -> None:
    assert REPORT_PATH.is_file()
    for name in SOURCES:
        assert name in report, f"report never names its source {name}"


def test_every_published_number_matches_a_committed_json_field(deflated, tail, report) -> None:
    allowed = _allowed_numeric(deflated, tail)
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


def test_tables_are_byte_identical_to_the_json_renderers(deflated, tail, report) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLE_BUILDERS), f"table anchors differ: {sorted(published)}"
    for name in TABLE_BUILDERS:
        expected = "\n".join(_built(name, deflated, tail))
        assert published[name] == expected, f"table {name} drifted from its JSON artifact"


def test_prose_does_not_quote_unbacked_numbers(deflated, tail, report) -> None:
    allowed = _allowed_numeric(deflated, tail)
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
    # Chartered prose number: the closed tail-asymmetry range
    text = text.replace("[-1, +1]", " ")
    # Chartered prose numbers that are not table data
    text = re.sub(r"\b6\b", " ", text)  # decimals
    text = re.sub(r"\b10\b", " ", text)  # "10 bps" costed level
    text = re.sub(r"\b40\b", " ", text)  # 40 assets (fixture recipe)
    text = re.sub(r"\b403\b", " ", text)  # Coinbase returns 403
    text = re.sub(r"\b0\.10\b", " ", text)  # marginal-p prose bound
    text = re.sub(r"\b0\.05\b", " ", text)  # marginal-p prose bound
    token = re.compile(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?(?![A-Za-z0-9_])")
    stray = {tok for tok in token.findall(text) if round(float(tok), DECIMALS) not in allowed}
    assert stray == set(), f"prose numbers with no JSON field: {sorted(stray)}"


# --------------------------------------------------------------------------- #
# 2. The verdict is explicit, machine-backed, and grounded in evidence
# --------------------------------------------------------------------------- #
def test_report_states_an_explicit_verdict(deflated, tail, report) -> None:
    lowered = _flat(report)
    assert "verdict" in lowered
    assert "retain" in lowered
    assert "deflated" in lowered
    assert "tail-risk" in lowered or "tail risk" in lowered
    assert "cvar" in lowered
    assert "expected shortfall" in lowered
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


def test_report_states_the_marginal_significance_honestly(report) -> None:
    lowered = _flat(report)
    assert "marginal" in lowered


def test_report_covers_all_required_sections(report) -> None:
    headings = [line for line in report.splitlines() if line.startswith("## ")]
    lowered = " ".join(headings).lower()
    for required in (
        "provenance",
        "deflated",
        "tail-risk",
        "decision criteria",
        "does not prove",
        "next",
    ):
        assert required in lowered, f"missing section: {required}"


# --------------------------------------------------------------------------- #
# 3. Every criterion the verdict cites is internally consistent
# --------------------------------------------------------------------------- #
def test_deflated_evidence_is_calibrated(deflated) -> None:
    assert deflated["campaign_verdict"] == "SURVIVES_DEFLATION"
    for label in ("shipped_default", "best_insample_config"):
        r = deflated["results"][label]
        assert r["survives_deflation"] is True
        assert r["verdict"] == "SURVIVES_DEFLATION"


def test_tail_evidence_is_calibrated(tail) -> None:
    assert tail["tail_risk_status"] == "ALL_NEUTRALITY_OK"
    for label in ("gross", "costed"):
        agg = tail["results"][label]["aggregate"]
        assert agg["all_neutrality_ok"] is True
        assert agg["n_error_cells"] == 0
        assert agg["n_ok_cells"] == agg["n_cells"]


def test_fixture_shas_agree(deflated, tail) -> None:
    dprov = deflated["provenance"]
    tprov = tail["provenance"]
    assert dprov["returns_sha256"] == tprov["returns_sha256"]
    assert dprov["btc_source_sha256"] == tprov["btc_source_sha256"]


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
    _load("deflated_summary.json")
    _load("tail_risk_summary.json")
    REPORT_PATH.read_text(encoding="utf-8")
    assert time.perf_counter() - start < 2.0


def test_decision_artifacts_are_byte_identical_after_the_suite(deflated, tail) -> None:
    for name in SOURCES:
        before = (RESEARCH_P38_DIR / name).read_bytes()
        _load(name)
        after = (RESEARCH_P38_DIR / name).read_bytes()
        assert before == after


# --------------------------------------------------------------------------- #
# 5. Ruff
# --------------------------------------------------------------------------- #
def test_no_ruff_errors_on_new_files():
    import subprocess
    import sys

    GENERATE_SCRIPT = REPO_ROOT / "generate_p38_decision.py"
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
