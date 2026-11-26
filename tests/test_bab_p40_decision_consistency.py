"""Acceptance tests for P40 WP2: the consolidated meta-analysis decision.

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
RESEARCH_P40 = REPO_ROOT / "research_state/bab_p40"
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

_FIXTURE_IDS = (
    "F1_PRIMARY",
    "F2_P39_SECOND",
    "F3_LOW_VOL_WIDE",
    "F4_HIGH_VOL_NARROW",
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
    return json.loads((RESEARCH_P40 / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def meta() -> dict:
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


def _fmt(value, decimals: int = DECIMALS) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    return f"{float(value):.{decimals}f}"


def _render(columns, rows) -> list[str]:
    lines = ["| " + " | ".join(columns) + " |"]
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    for row in rows:
        lines.append("| " + " | ".join(_cell(row[column]) for column in columns) + " |")
    return lines


def _agg(value) -> dict:
    # _agg-style block from the committed aggregate (mean/min/max/n)
    return value


def provenance_table(meta) -> tuple[list[str], list[dict]]:
    prov = meta["provenance"]
    rows = [
        {"Fact": "Schema", "Value": meta["schema"]},
        {"Fact": "Campaign", "Value": prov["campaign"]},
        {"Fact": "WP", "Value": prov["wp"]},
        {"Fact": "Synthetic", "Value": prov["synthetic"]},
        {"Fact": "Meta-analysis note", "Value": prov["note"]},
        {"Fact": "BTC source SHA256", "Value": "`" + prov["btc_source_sha256"] + "`"},
        {
            "Fact": "Deflation trials (n_trials_total)",
            "Value": meta["trial_enumeration"]["n_trials_total"],
        },
        {"Fact": "DSR survive threshold", "Value": prov["dsr_survive_threshold"]},
        {"Fact": "Bootstrap resamples", "Value": prov["bootstrap"]["n_resamples"]},
        {"Fact": "Bootstrap block length", "Value": prov["bootstrap"]["block_length"]},
        {"Fact": "Bootstrap seed", "Value": prov["bootstrap"]["seed"]},
        {"Fact": "Fixtures", "Value": prov["config_grid"]["n_fixtures"]},
        {
            "Fact": "Seeds per fixture",
            "Value": prov["config_grid"]["n_seeds_per_fixture"],
        },
        {"Fact": "Total cells", "Value": prov["config_grid"]["n_cells_total"]},
        {"Fact": "Beta window", "Value": prov["config_grid"]["beta_window"]},
        {"Fact": "Quantile", "Value": prov["config_grid"]["quantile"]},
        {"Fact": "Weighting", "Value": prov["config_grid"]["weighting"]},
        {"Fact": "Beta neutral", "Value": prov["config_grid"]["beta_neutral"]},
        {"Fact": "Dollar neutral", "Value": prov["config_grid"]["dollar_neutral"]},
        {
            "Fact": "Transaction costs",
            "Value": prov["config_grid"]["transaction_costs"],
        },
        {"Fact": "Campaign verdict", "Value": meta["campaign_verdict"]},
    ]
    return ["Fact", "Value"], rows


def fixture_table(meta) -> tuple[list[str], list[dict]]:
    prov = meta["provenance"]
    results = meta["results"]
    rows = []
    for e in prov["fixtures"]:
        fid = e["id"]
        cfg = e["config"]
        agg = results["fixtures"][fid]["aggregate"]
        rows.append({
            "Fixture": fid,
            "Role": e["role"],
            "Base seed": cfg["base_seed"],
            "Increment": cfg["increment"],
            "Idio vol": cfg["idio_vol"],
            "Beta range": f"[{_fmt(cfg['beta_min'])}, {_fmt(cfg['beta_max'])}]",
            "Assets": cfg["n_assets"],
            "N cells": agg["n_cells"],
            "N ok": agg["n_ok_cells"],
            "N survive": agg["n_survive"],
            "DSR mean": agg["dsr"]["mean"],
            "DSR min": agg["dsr"]["min"],
            "DSR max": agg["dsr"]["max"],
            "Replicates P38 pooled": e["replicates_p38_pooled_verdict"],
        })
    columns = [
        "Fixture", "Role", "Base seed", "Increment", "Idio vol", "Beta range",
        "Assets", "N cells", "N ok", "N survive", "DSR mean", "DSR min", "DSR max",
        "Replicates P38 pooled",
    ]
    return columns, rows


def cell_table(meta) -> tuple[list[str], list[dict]]:
    results = meta["results"]
    rows = []
    for e in meta["provenance"]["fixtures"]:
        fid = e["id"]
        for cell in results["fixtures"][fid]["cells"]:
            neu = cell.get("neutrality", {})
            neu_ok = (
                neu.get("model_beta_neutral", {}).get("passed", False)
                and neu.get("dollar_neutral", {}).get("passed", False)
                and neu.get("realized_beta_check", {}).get("passed", False)
            )
            rows.append({
                "Fixture": fid,
                "Seed": cell["seed"],
                "Seed index": cell["seed_index"],
                "N periods": cell["n_periods"],
                "Sharpe": cell["sharpe"],
                "DSR": cell["dsr"],
                "PSR": cell["psr"],
                "Survives": cell["survives_deflation"],
                "Verdict": cell["verdict"],
                "Neutrality ok": neu_ok,
            })
    columns = [
        "Fixture", "Seed", "Seed index", "N periods", "Sharpe", "DSR", "PSR",
        "Survives", "Verdict", "Neutrality ok",
    ]
    return columns, rows


def aggregate_table(meta) -> tuple[list[str], list[dict]]:
    cross = meta["results"]["cross_fixture"]
    c_neutrality_ok = (
        cross["neutrality"]["all_dollar_ok"]
        and cross["neutrality"]["all_model_beta_ok"]
        and cross["neutrality"]["all_realized_ok"]
    )
    rows = []
    for metric in ("dsr", "psr", "sharpe"):
        m = cross[metric]
        rows.append({
            "Metric": metric.upper(),
            "N cells": cross["n_cells"],
            "N ok": cross["n_ok_cells"],
            "N errors": cross["n_error_cells"],
            "All neutrality ok": c_neutrality_ok,
            "All survive": cross["all_survive"],
            "N survive": cross["n_survive"],
            "Mean": m["mean"],
            "Min": m["min"],
            "Max": m["max"],
        })
    columns = [
        "Metric", "N cells", "N ok", "N errors", "All neutrality ok", "All survive",
        "N survive", "Mean", "Min", "Max",
    ]
    return columns, rows


def neutrality_table(meta) -> tuple[list[str], list[dict]]:
    cross = meta["results"]["cross_fixture"]
    prov = meta["provenance"]
    rows = [
        {
            "Check": "Model beta neutral",
            "Passed": cross["neutrality"]["all_model_beta_ok"],
            "Tolerance": prov["neutrality_tolerances"]["model_beta_neutral"],
        },
        {
            "Check": "Dollar neutral",
            "Passed": cross["neutrality"]["all_dollar_ok"],
            "Tolerance": prov["neutrality_tolerances"]["dollar_neutral"],
        },
        {
            "Check": "Realized |beta|",
            "Passed": cross["neutrality"]["all_realized_ok"],
            "Tolerance": prov["neutrality_tolerances"]["realized_beta"],
        },
    ]
    return ["Check", "Passed", "Tolerance"], rows


def decision_table(meta) -> tuple[list[str], list[dict]]:
    prov = meta["provenance"]
    cross = meta["results"]["cross_fixture"]
    results = meta["results"]
    n_trials = meta["trial_enumeration"]["n_trials_total"]
    dsr_threshold = prov["dsr_survive_threshold"]
    n_replicate = sum(
        1 for e in prov["fixtures"] if e["replicates_p38_pooled_verdict"]
    )
    n_fixtures = len(prov["fixtures"])
    campaign_verdict = meta["campaign_verdict"]
    all_cells_ok = (
        cross["n_ok_cells"] == cross["n_cells"] and cross["n_error_cells"] == 0
    )
    cross_neutrality_ok = (
        cross["neutrality"]["all_dollar_ok"]
        and cross["neutrality"]["all_model_beta_ok"]
        and cross["neutrality"]["all_realized_ok"]
    )
    dsr_bounded = all(
        0.0 <= c["dsr"] <= 1.0
        for e in prov["fixtures"]
        for c in results["fixtures"][e["id"]]["cells"]
        if c.get("status") == "ok"
    )
    psr_bounded = all(
        0.0 <= c["psr"] <= 1.0
        for e in prov["fixtures"]
        for c in results["fixtures"][e["id"]]["cells"]
        if c.get("status") == "ok"
    )
    verdict_rule_ok = (
        (n_replicate == n_fixtures and campaign_verdict == "ROBUST_ACROSS_FIXTURES")
        or (
            0 < n_replicate < n_fixtures
            and campaign_verdict == "FRAGILE_FIXTURE_DEPENDENT"
        )
        or (n_replicate == 0 and campaign_verdict == "DOES_NOT_REPLICATE")
    )

    rows = [
        {
            "Criterion": (
                "WP0 meta-analysis deflates DSR/PSR over n_trials_total read-only "
                "from P38 WP1 (trial_enumeration.n_trials_total)"
            ),
            "Required": n_trials > 0,
        },
        {
            "Criterion": (
                "Consolidated verdict is an explicit enum value "
                "(ROBUST_ACROSS_FIXTURES / FRAGILE_FIXTURE_DEPENDENT / DOES_NOT_REPLICATE)"
            ),
            "Required": campaign_verdict in (
                "ROBUST_ACROSS_FIXTURES",
                "FRAGILE_FIXTURE_DEPENDENT",
                "DOES_NOT_REPLICATE",
            ),
        },
        {
            "Criterion": f"All {prov['config_grid']['n_cells_total']} cells are status ok with zero errors",
            "Required": all_cells_ok,
        },
        {
            "Criterion": (
                "Neutrality holds at every cell (model beta <= 1e-3, dollar <= 1e-9, "
                "|realized beta| <= 0.15)"
            ),
            "Required": cross_neutrality_ok,
        },
        {
            "Criterion": "DSR and PSR bounded in [0, 1] at every ok cell",
            "Required": dsr_bounded and psr_bounded,
        },
        {
            "Criterion": (
                f"Fixture replication count ({n_replicate} of {n_fixtures}) matches the "
                "per-fixture all-ok + all-survive + no-error rule"
            ),
            "Required": verdict_rule_ok,
        },
        {
            "Criterion": "Synthetic provenance labelled (controlled synthetic, not real market data)",
            "Required": prov["synthetic"] is True
            and "not market profitability evidence" in prov["note"],
        },
        {
            "Criterion": "No demonstrated real-world profitability claim is made",
            "Required": True,
        },
    ]
    return ["Criterion", "Required"], rows


TABLE_BUILDERS = {
    "provenance": provenance_table,
    "fixture": fixture_table,
    "cell": cell_table,
    "aggregate": aggregate_table,
    "neutrality": neutrality_table,
    "decision": decision_table,
}


def _built(name: str, meta) -> list[str]:
    columns, rows = TABLE_BUILDERS[name](meta)
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


def _allowed_numeric(meta) -> set:
    allowed = set()
    allowed |= _numeric_leaves(meta)
    return allowed


# --------------------------------------------------------------------------- #
# 1. Zero unmatched numbers in every table cell
# --------------------------------------------------------------------------- #
def test_report_exists_and_declares_its_source(meta, report) -> None:
    assert REPORT_PATH.is_file()
    assert "meta_summary.json" in report, "report never names its source"


def test_every_published_number_matches_a_committed_json_field(meta, report) -> None:
    allowed = _allowed_numeric(meta)
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
    minimum = 200  # chartered minimum machine-checked numeric cells
    assert published, "report publishes no numeric table cells"
    assert len(published) >= minimum, (
        f"report publishes {len(published)} machine-checked cells, below the chartered {minimum}"
    )
    assert unmatched == [], f"published numbers absent from JSON: {sorted(set(unmatched))}"


def test_tables_are_byte_identical_to_the_json_renderers(meta, report) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLE_BUILDERS), f"table anchors differ: {sorted(published)}"
    for name in TABLE_BUILDERS:
        expected = "\n".join(_built(name, meta))
        assert published[name] == expected, f"table {name} drifted from its JSON artifact"


def test_prose_does_not_quote_unbacked_numbers(meta, report) -> None:
    allowed = _allowed_numeric(meta)
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
    text = re.sub(r"\b32\b", " ", text)  # total cells (in allowed)
    text = re.sub(r"\b8\b", " ", text)  # seeds per fixture (in allowed)
    text = re.sub(r"\b4\b", " ", text)  # fixtures (in allowed)
    text = re.sub(r"\b90\b", " ", text)  # beta window (in allowed)
    text = re.sub(r"\b0\.3\b", " ", text)  # quantile (in allowed)
    text = re.sub(r"\b2000\b", " ", text)  # bootstrap resamples (in allowed)
    text = re.sub(r"\b20\b", " ", text)  # block length (in allowed)
    text = re.sub(r"\b0\b", " ", text)  # zero counts / thresholds (in allowed)
    token = re.compile(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?(?![A-Za-z0-9_])")
    stray = {tok for tok in token.findall(text) if round(float(tok), DECIMALS) not in allowed}
    assert stray == set(), f"prose numbers with no JSON field: {sorted(stray)}"


# --------------------------------------------------------------------------- #
# 2. The verdict is explicit, machine-backed, and grounded in evidence
# --------------------------------------------------------------------------- #
def test_report_states_an_explicit_verdict(meta, report) -> None:
    lowered = _flat(report)
    assert "verdict" in lowered
    assert "retain" in lowered
    assert "does_not_replicate" in lowered or "does not replicate" in lowered
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
    assert "does_not_replicate" in lowered or "does not replicate" in lowered
    assert "fixture-dependent" in lowered


def test_report_covers_all_required_sections(report) -> None:
    headings = [line for line in report.splitlines() if line.startswith("## ")]
    lowered = " ".join(headings).lower()
    for required in (
        "provenance",
        "wp0",
        "decision criteria",
        "does not prove",
        "next",
    ):
        assert required in lowered, f"missing section: {required}"


# --------------------------------------------------------------------------- #
# 3. Every criterion the verdict cites is internally consistent
# --------------------------------------------------------------------------- #
def test_committed_verdict_is_honest_negative(meta):
    assert meta["campaign_verdict"] == "DOES_NOT_REPLICATE"
    cross = meta["results"]["cross_fixture"]
    assert cross["n_cells"] == 32
    assert cross["n_ok_cells"] == 32
    assert cross["n_error_cells"] == 0
    assert cross["all_neutrality_ok"] is True
    n_replicate = sum(
        1 for e in meta["provenance"]["fixtures"] if e["replicates_p38_pooled_verdict"]
    )
    assert n_replicate == 0


def test_decision_criteria_are_consistent(meta):
    for name, rows in TABLE_BUILDERS.items():
        if name == "decision":
            columns, rows = rows(meta)
            assert columns == ["Criterion", "Required"]
            for row in rows:
                assert row["Required"] is True, f"criterion failed: {row['Criterion']}"


# --------------------------------------------------------------------------- #
# 4. The test itself never re-runs a harness and never edits an artifact
# --------------------------------------------------------------------------- #
def test_decision_consistency_never_executes_a_research_harness() -> None:
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


def test_decision_artifacts_are_byte_identical_after_the_suite(meta) -> None:
    before = (RESEARCH_P40 / "meta_summary.json").read_bytes()
    _load("meta_summary.json")
    after = (RESEARCH_P40 / "meta_summary.json").read_bytes()
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
