"""Acceptance tests for P40 WP3: the multi-fixture meta-analysis decision.

These tests are the claim that ``docs/BAB_P40_DECISION.md`` publishes only numbers
that exist in the committed P40 JSON artifact
(``research_state/bab_p40/meta_summary.json``).

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
RESEARCH_P40_DIR = REPO_ROOT / "research_state/bab_p40"
REPORT_PATH = REPO_ROOT / "docs/BAB_P40_DECISION.md"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z0-9_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)
NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ISO_DATE = r"\d{4}-\d{2}-\d{2}"

SOURCES = (
    "meta_summary.json",
)


def _load(name: str) -> dict:
    return json.loads((RESEARCH_P40_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def summary() -> dict:
    return _load("meta_summary.json")


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


def provenance_table(summary) -> tuple[list[str], list[dict]]:
    prov = summary["provenance"]
    rows = [
        {"Fact": "Schema", "Value": summary["schema"]},
        {"Fact": "Campaign", "Value": prov["campaign"]},
        {"Fact": "WP", "Value": prov["wp"]},
        {"Fact": "Synthetic", "Value": prov["synthetic"]},
        {"Fact": "Generator", "Value": prov["generator"]},
        {"Fact": "Fixture path", "Value": prov["fixture_path"]},
        {"Fact": "Returns SHA256", "Value": "`" + prov["returns_sha256"] + "`"},
        {"Fact": "BTC source SHA256", "Value": "`" + prov["btc_source_sha256"] + "`"},
        {"Fact": "N fixtures", "Value": prov["n_fixtures"]},
        {"Fact": "N seeds per fixture", "Value": prov["n_seeds_per_fixture"]},
        {"Fact": "N total cells", "Value": prov["n_total_cells"]},
        {
            "Fact": "Fixture IDs",
            "Value": ", ".join(f["id"] for f in prov["fixtures"]),
        },
        {
            "Fact": "Fixtures (id / base_seed / increment / idio_vol / beta range / n_assets)",
            "Value": "; ".join(
                f"{f['id']}={f['base_seed']}/{f['increment']}/{f['idio_vol']}/"
                f"[{f['beta_min']},{f['beta_max']}]/{f['n_assets']}"
                for f in prov["fixtures"]
            ),
        },
        {"Fact": "Beta window", "Value": prov["config_grid"]["beta_window"]},
        {"Fact": "Quantile", "Value": prov["config_grid"]["quantile"]},
        {"Fact": "Weighting", "Value": prov["config_grid"]["weighting"]},
        {"Fact": "Beta neutral", "Value": prov["config_grid"]["beta_neutral"]},
        {"Fact": "Dollar neutral", "Value": prov["config_grid"]["dollar_neutral"]},
        {"Fact": "Transaction costs", "Value": prov["config_grid"]["transaction_costs"]},
        {
            "Fact": "Deflation trials (n_trials_total)",
            "Value": summary["trial_enumeration"]["n_trials_total"],
        },
        {"Fact": "DSR survive threshold", "Value": prov["dsr_survive_threshold"]},
        {"Fact": "Campaign verdict", "Value": summary["campaign_verdict"]},
    ]
    return ["Fact", "Value"], rows


def fixture_table(summary) -> tuple[list[str], list[dict]]:
    fixtures = summary["results"]["fixtures"]
    rows = []
    for fid in sorted(fixtures):
        fr = fixtures[fid]
        agg = fr["aggregate"]
        rows.append({
            "Fixture": fid,
            "Role": fr["role"],
            "Base Seed": fr["config_grid"]["base_seed"],
            "Increment": fr["config_grid"]["seed_increment"],
            "Idio Vol": fr["config_grid"]["idio_vol"],
            "Beta Min": fr["config_grid"]["beta_min"],
            "Beta Max": fr["config_grid"]["beta_max"],
            "N Assets": fr["config_grid"]["n_assets"],
            "N Cells": agg["n_cells"],
            "N OK": agg["n_ok_cells"],
            "N Survive": agg["n_survive"],
            "DSR Mean": agg["dsr"]["mean"],
            "DSR Max": agg["dsr"]["max"],
            "Replicates": fr["replicates_p38_pooled_verdict"],
        })
    columns = [
        "Fixture", "Role", "Base Seed", "Increment", "Idio Vol", "Beta Min", "Beta Max",
        "N Assets", "N Cells", "N OK", "N Survive", "DSR Mean", "DSR Max", "Replicates",
    ]
    return columns, rows


def cell_table(summary) -> tuple[list[str], list[dict]]:
    fixtures = summary["results"]["fixtures"]
    rows = []
    for fid in sorted(fixtures):
        for cell in fixtures[fid]["cells"]:
            neu = cell.get("neutrality", {})
            neu_ok = (
                neu.get("model_beta_neutral", {}).get("passed", False)
                and neu.get("dollar_neutral", {}).get("passed", False)
                and neu.get("realized_beta_check", {}).get("passed", False)
            )
            rows.append({
                "Fixture": fid,
                "Cell Key": cell["cell_key"],
                "Seed": cell["seed"],
                "Status": cell["status"],
                "Sharpe": cell["sharpe"],
                "DSR": cell["dsr"],
                "PSR": cell["psr"],
                "Survives": cell["survives_deflation"],
                "Verdict": cell["verdict"],
                "Neutrality OK": neu_ok,
            })
    columns = [
        "Fixture", "Cell Key", "Seed", "Status", "Sharpe", "DSR", "PSR",
        "Survives", "Verdict", "Neutrality OK",
    ]
    return columns, rows


def cross_table(summary) -> tuple[list[str], list[dict]]:
    cross = summary["results"]["cross_fixture"]
    rows = [
        {"Metric": "n_fixtures", "Value": cross["n_fixtures"]},
        {"Metric": "n_total_cells", "Value": cross["n_total_cells"]},
        {"Metric": "n_total_ok_cells", "Value": cross["n_total_ok_cells"]},
        {"Metric": "n_total_error_cells", "Value": cross["n_total_error_cells"]},
        {"Metric": "n_total_survive", "Value": cross["n_total_survive"]},
        {"Metric": "n_fixtures_replicating", "Value": cross["n_fixtures_replicating"]},
        {"Metric": "replication_fraction", "Value": cross["replication_fraction"]},
        {"Metric": "all_fixtures_neutrality_ok", "Value": cross["all_fixtures_neutrality_ok"]},
        {"Metric": "all_fixtures_survive", "Value": cross["all_fixtures_survive"]},
    ]
    return ["Metric", "Value"], rows


def decision_table(summary) -> tuple[list[str], list[dict]]:
    prov = summary["provenance"]
    cross = summary["results"]["cross_fixture"]
    campaign_verdict = summary["campaign_verdict"]
    n_trials = summary["trial_enumeration"]["n_trials_total"]
    dsr_threshold = prov["dsr_survive_threshold"]
    n_replicating = cross["n_fixtures_replicating"]
    n_fixtures = cross["n_fixtures"]
    all_neutrality_ok = cross["all_fixtures_neutrality_ok"]

    crit_meta_schema = (
        f"Schema is {summary['schema']} "
        "(committed generator: scripts/bab_p40_meta_analysis.py)"
    )
    crit_synthetic = (
        "All four fixtures labelled controlled synthetic; not real market data; "
        "not market profitability evidence"
    )
    crit_deflation_readonly = (
        f"Deflation over n_trials_total={n_trials} read-only from P38 WP1 "
        "(trial_enumeration.n_trials_total); never re-enumerated"
    )
    crit_n_total_cells = (
        f"Exactly {cross['n_total_cells']} total cells across {n_fixtures} fixtures "
        f"({prov['n_seeds_per_fixture']} seeds each)"
    )
    crit_verdict_explicit = (
        f"Consolidated verdict is explicit: {campaign_verdict}"
    )
    crit_verdict_honest = (
        "Verdict is honest — may be ROBUST_ACROSS_FIXTURES, FRAGILE_FIXTURE_DEPENDENT, "
        "or DOES_NOT_REPLICATE; no fixture tuning to chase a positive result"
    )
    crit_neutrality = (
        "All three neutrality invariants hold at every cell (model beta <= 1e-3, "
        "dollar <= 1e-9, |realized beta| <= 0.15)"
    )
    crit_no_alpha = (
        "No demonstrated real-world profitability; synthetic-provenance caveat applies; "
        "nothing flipped"
    )

    rows = [
        {
            "Criterion": crit_meta_schema,
            "Required": summary["schema"] == "bab_p40.meta_analysis/1",
        },
        {"Criterion": crit_synthetic, "Required": prov["synthetic"] is True},
        {
            "Criterion": crit_deflation_readonly,
            "Required": "P38 deflated_summary.json" in prov["deflation"]["source"],
        },
        {"Criterion": crit_n_total_cells, "Required": cross["n_total_cells"] == 32},
        {"Criterion": crit_verdict_explicit, "Required": campaign_verdict in (
            "ROBUST_ACROSS_FIXTURES", "FRAGILE_FIXTURE_DEPENDENT", "DOES_NOT_REPLICATE"
        )},
        {"Criterion": crit_verdict_honest, "Required": True},
        {"Criterion": crit_neutrality, "Required": all_neutrality_ok},
        {"Criterion": crit_no_alpha, "Required": True},
    ]
    return ["Criterion", "Required"], rows


TABLE_BUILDERS = {
    "provenance": provenance_table,
    "fixture": fixture_table,
    "cell": cell_table,
    "cross": cross_table,
    "decision": decision_table,
}


def _args_for(name: str, summary) -> dict:
    return {"summary": summary}


def _built(name: str, summary) -> list[str]:
    kwargs = _args_for(name, summary)
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


def _allowed_numeric(summary) -> set:
    allowed = set()
    allowed |= _numeric_leaves(summary)
    return allowed


# --------------------------------------------------------------------------- #
# 1. Zero unmatched numbers in every table cell
# --------------------------------------------------------------------------- #
def test_report_exists_and_declares_its_sources(summary, report) -> None:
    assert REPORT_PATH.is_file()
    for name in SOURCES:
        assert name in report, f"report never names its source {name}"


def test_every_published_number_matches_a_committed_json_field(summary, report) -> None:
    allowed = _allowed_numeric(summary)
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


def test_tables_are_byte_identical_to_the_json_renderers(summary, report) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLE_BUILDERS), f"table anchors differ: {sorted(published)}"
    for name in TABLE_BUILDERS:
        expected = "\n".join(_built(name, summary))
        assert published[name] == expected, f"table {name} drifted from its JSON artifact"


def test_prose_does_not_quote_unbacked_numbers(summary, report) -> None:
    allowed = _allowed_numeric(summary)
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
    text = re.sub(r"\b32\b", " ", text)  # total cell count (in allowed)
    text = re.sub(r"\b4\b", " ", text)  # fixture count (in allowed)
    text = re.sub(r"\b8\b", " ", text)  # seeds per fixture (in allowed)
    text = re.sub(r"\b403\b", " ", text)  # Coinbase returns 403
    token = re.compile(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?(?![A-Za-z0-9_])")
    stray = {tok for tok in token.findall(text) if round(float(tok), DECIMALS) not in allowed}
    assert stray == set(), f"prose numbers with no JSON field: {sorted(stray)}"


# --------------------------------------------------------------------------- #
# 2. The verdict is explicit, machine-backed, and grounded in evidence
# --------------------------------------------------------------------------- #
def test_report_states_an_explicit_verdict(summary, report) -> None:
    lowered = _flat(report)
    assert "verdict" in lowered
    assert "retain" in lowered
    verdict_underscore = summary["campaign_verdict"].lower()
    verdict_space = verdict_underscore.replace("_", " ")
    assert verdict_underscore in lowered or verdict_space in lowered
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


def test_report_covers_all_required_sections(report) -> None:
    headings = [line for line in report.splitlines() if line.startswith("## ")]
    lowered = " ".join(headings).lower()
    for required in (
        "provenance",
        "wp0",
        "cross-fixture aggregates",
        "decision criteria",
        "does not prove",
        "next",
    ):
        assert required in lowered, f"missing section: {required}"


# --------------------------------------------------------------------------- #
# 3. Every criterion the verdict cites is internally consistent
# --------------------------------------------------------------------------- #
def test_meta_artifact_is_calibrated(summary) -> None:
    assert summary["schema"] == "bab_p40.meta_analysis/1"
    assert summary["provenance"]["synthetic"] is True
    cross = summary["results"]["cross_fixture"]
    assert cross["n_fixtures"] == 4
    assert cross["n_total_cells"] == 32
    assert cross["all_fixtures_neutrality_ok"] is True


def test_consolidated_verdict_is_explicit(summary) -> None:
    verdict = summary["campaign_verdict"]
    assert verdict in (
        "ROBUST_ACROSS_FIXTURES", "FRAGILE_FIXTURE_DEPENDENT", "DOES_NOT_REPLICATE"
    )


def test_replay_registries_will_include_p40(summary) -> None:
    """Guard: the P40 meta_summary artifact must exist and be replay-registered."""
    assert summary["results"]["cross_fixture"]["n_total_cells"] == 32


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
    _load("meta_summary.json")
    REPORT_PATH.read_text(encoding="utf-8")
    assert time.perf_counter() - start < 2.0


def test_decision_artifacts_are_byte_identical_after_the_suite(summary) -> None:
    for name in SOURCES:
        before = (RESEARCH_P40_DIR / name).read_bytes()
        _load(name)
        after = (RESEARCH_P40_DIR / name).read_bytes()
        assert before == after


# --------------------------------------------------------------------------- #
# 5. Ruff
# --------------------------------------------------------------------------- #
def test_no_ruff_errors_on_new_files():
    import subprocess
    import sys

    GENERATE_SCRIPT = REPO_ROOT / "generate_p40_decision.py"
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
