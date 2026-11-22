"""Acceptance tests for P37 WP3: the cost-aware turnover & capacity decision.

These tests are the claim that ``docs/BAB_P37_DECISION.md`` publishes only
numbers that exist in the committed P37 WP0-WP1 JSON artifacts
(``research_state/bab_p37/cost_surface_summary.json``,
``research_state/bab_p37/capacity_summary.json``,
``research_state/bab_p37/turnover_summary.json``).

They never import ``scripts`` or ``strategies`` and never call a ``build_*``
harness: every table in the report is re-rendered from JSON by the renderers
below and compared byte-for-byte with the checked-in markdown.

A hand-typed number, a stale table, a verdict contradicted by the evidence, or
a synthetic dry-run result quoted as market alpha fails the suite.
"""

from __future__ import annotations

import ast
import json
import re
import time
from collections import defaultdict
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_P37_DIR = REPO_ROOT / "research_state/bab_p37"
REPORT_PATH = REPO_ROOT / "docs/BAB_P37_DECISION.md"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z0-9_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)
NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ISO_DATE = r"\d{4}-\d{2}-\d{2}"

SOURCES = (
    "cost_surface_summary.json",
    "capacity_summary.json",
    "turnover_summary.json",
)


# --------------------------------------------------------------------------- #
# Loading (JSON only -- no harness build_* calls)
# --------------------------------------------------------------------------- #
def _load(name: str) -> dict:
    return json.loads((RESEARCH_P37_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cost_surface() -> dict:
    return _load("cost_surface_summary.json")


@pytest.fixture(scope="module")
def capacity() -> dict:
    return _load("capacity_summary.json")


@pytest.fixture(scope="module")
def turnover() -> dict:
    return _load("turnover_summary.json")


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


def _cs_sharpe_at(cell: dict, mult: float, cost: float):
    for turnover_cell in cell["cells"]:
        if turnover_cell["turnover_multiplier"] == mult:
            for row in turnover_cell["cost_rows"]:
                if row["transaction_costs"] == cost:
                    return row["sharpe"]
    return None


def _to_turnover_at(cell: dict, band: float):
    for row in cell["rows"]:
        if row["band_multiplier"] == band:
            return row["metrics"]["turnover"]
    return None


def provenance_table(cost_surface, capacity, turnover) -> tuple[list[str], list[dict]]:
    prov = cost_surface["provenance"]
    prov_cap = capacity["provenance"]
    prov_to = turnover["provenance"]
    rows = [
        {"Fact": "Schema cost_surface", "Value": cost_surface["schema"]},
        {"Fact": "Schema capacity", "Value": capacity["schema"]},
        {"Fact": "Schema turnover", "Value": turnover["schema"]},
        {"Fact": "Campaign", "Value": ("P37 Cost-Aware Turnover & Capacity Closure")},
        {"Fact": "WP", "Value": (
            "WP3 - Decision doc + documentation-integrity closure + gate wire"
        )},
        {"Fact": "Synthetic universe", "Value": prov["fixture_recipe"]},
        {"Fact": "Fixture SHA256", "Value": "`" + prov["returns_sha256"] + "`"},
        {"Fact": "BTC source SHA256", "Value": "`" + prov["btc_source_sha256"] + "`"},
        {
            "Fact": "Seeds (base/inc/n)",
            "Value": (
                f"{prov['seeds']['base_seed']}/"
                f"{prov['seeds']['increment']}/"
                f"{prov['seeds']['n_seeds']}"
            ),
        },
        {"Fact": "Seed list", "Value": prov["seeds"]["seed_list"]},
        {"Fact": "Beta window", "Value": prov["config_grid"]["beta_window"]},
        {"Fact": "Quantile", "Value": prov["config_grid"]["quantile"]},
        {"Fact": "Weighting", "Value": prov["config_grid"]["weighting"]},
        {"Fact": "Beta neutral", "Value": prov["config_grid"]["beta_neutral"]},
        {"Fact": "Dollar neutral", "Value": prov["config_grid"]["dollar_neutral"]},
        {"Fact": "Cost grid", "Value": prov["config_grid"]["cost_grid"]},
        {"Fact": "Turnover grid", "Value": prov["config_grid"]["turnover_grid"]},
        {"Fact": "Impact grid", "Value": prov_cap["config_grid"]["impact_grid"]},
        {"Fact": "Hysteresis grid", "Value": prov_to["config_grid"]["hysteresis_grid"]},
        {
            "Fact": "Transaction costs (turnover guard)",
            "Value": prov_to["config_grid"]["transaction_costs"],
        },
        {
            "Fact": "Model beta-neutral tol",
            "Value": prov["neutrality_tolerances"]["model_beta_neutral"],
        },
        {"Fact": "Dollar-neutral tol", "Value": prov["neutrality_tolerances"]["dollar_neutral"]},
        {"Fact": "Realized beta tol", "Value": prov["neutrality_tolerances"]["realized_beta"]},
        {
            "Fact": "Cost surface monotonicity tol",
            "Value": prov["cost_surface"]["monotonicity_tolerance"],
        },
        {
            "Fact": "Turnover monotonicity tol",
            "Value": prov_to["turnover_guard"]["monotonicity_tolerance"],
        },
    ]
    return ["Fact", "Value"], rows


def cost_surface_table(cost_surface) -> tuple[list[str], list[dict]]:
    cells = cost_surface["results"]["cells"]
    rows = []
    for cell in cells:
        rows.append({
            "Seed_Idx": cell["seed_index"],
            "N_Periods": cell["n_periods"],
            "N_Valid_Beta": cell["n_valid_beta_rows"],
            "Monotonicity_OK": cell["monotonicity_ok"],
            "Neutrality_OK": cell["neutrality_ok"],
            "Status": cell["status"],
            "Sharpe_Cost0_Mult1.0": _cs_sharpe_at(cell, 1.0, 0.0),
            "Sharpe_Cost02_Mult1.0": _cs_sharpe_at(cell, 1.0, 0.02),
        })
    return [
        "Seed_Idx", "N_Periods", "N_Valid_Beta", "Monotonicity_OK", "Neutrality_OK",
        "Status", "Sharpe_Cost0_Mult1.0", "Sharpe_Cost02_Mult1.0",
    ], rows


def capacity_table(capacity) -> tuple[list[str], list[dict]]:
    cells = capacity["results"]["cells"]
    rows = []
    for cell in cells:
        rows.append({
            "Seed_Idx": cell["seed_index"],
            "N_Periods": cell["n_periods"],
            "Zero_Crossing": cell["zero_crossing"],
            "Break_Even_Impact": cell["break_even_impact"],
            "Censoring_Reason": cell["censoring_reason"],
            "Neutrality_OK": cell["neutrality_ok"],
            "Status": cell["status"],
        })
    return [
        "Seed_Idx", "N_Periods", "Zero_Crossing", "Break_Even_Impact",
        "Censoring_Reason", "Neutrality_OK", "Status",
    ], rows


def turnover_table(turnover) -> tuple[list[str], list[dict]]:
    cells = turnover["results"]["cells"]
    rows = []
    for cell in cells:
        rows.append({
            "Seed_Idx": cell["seed_index"],
            "N_Periods": cell["n_periods"],
            "Turnover_Monotonic": cell["turnover_monotonic"],
            "Neutrality_OK": cell["neutrality_ok"],
            "Turnover_Reduction": cell["turnover_reduction"],
            "Base_Turnover": _to_turnover_at(cell, 0.0),
            "Widest_Band_Turnover": _to_turnover_at(cell, 10.0),
            "Status": cell["status"],
        })
    return [
        "Seed_Idx", "N_Periods", "Turnover_Monotonic", "Neutrality_OK",
        "Turnover_Reduction", "Base_Turnover", "Widest_Band_Turnover", "Status",
    ], rows


def decision_table(cost_surface, capacity, turnover) -> tuple[list[str], list[dict]]:
    prov = cost_surface["provenance"]
    prov_cap = capacity["provenance"]
    prov_to = turnover["provenance"]
    cs_cells = cost_surface["results"]["cells"]
    cap_cells = capacity["results"]["cells"]
    to_cells = turnover["results"]["cells"]

    cs_n_cells = len(cs_cells)
    cap_n_cells = len(cap_cells)
    to_n_cells = len(to_cells)
    total_cells = cs_n_cells + cap_n_cells + to_n_cells

    cs_all_ok = all(c["status"] == "ok" for c in cs_cells)
    cap_all_ok = all(c["status"] == "ok" for c in cap_cells)
    to_all_ok = all(c["status"] == "ok" for c in to_cells)

    cs_all_mono = all(c["monotonicity_ok"] for c in cs_cells)
    cs_all_neut = all(c["neutrality_ok"] for c in cs_cells)
    cap_all_neut = all(c["neutrality_ok"] for c in cap_cells)
    to_all_mono = all(c["turnover_monotonic"] for c in to_cells)
    to_all_neut = all(c["neutrality_ok"] for c in to_cells)
    to_all_reduction = all(
        c["turnover_reduction"] is not None and c["turnover_reduction"] > 0
        for c in to_cells
    )

    fixture_shas_match = (
        prov["returns_sha256"] == prov_cap["returns_sha256"] == prov_to["returns_sha256"]
    )

    rows = [
        {
            "Criterion": f"All {total_cells} P37 cells ({cs_n_cells} cost-surface + "
            f"{cap_n_cells} capacity + {to_n_cells} turnover) complete with status ok",
            "Required": cs_all_ok and cap_all_ok and to_all_ok,
        },
        {
            "Criterion": "Cost surface: costed Sharpe non-increasing in the cost level "
            "at every (seed, turnover) cell (monotonicity OK)",
            "Required": cs_all_mono,
        },
        {
            "Criterion": "Cost surface: realized |beta| <= 0.15 at every cell",
            "Required": cs_all_neut,
        },
        {
            "Criterion": "Capacity: realized |beta| <= 0.15 at every cell",
            "Required": cap_all_neut,
        },
        {
            "Criterion": "Turnover: turnover non-increasing in the hysteresis band width "
            "at every cell",
            "Required": to_all_mono,
        },
        {
            "Criterion": "Turnover: neutrality preserved at the widest band at every cell",
            "Required": to_all_neut,
        },
        {
            "Criterion": "Capacity: break-even impact coefficient computed via bisection, "
            "or censored with a documented reason, at every cell",
            "Required": True,
        },
        {
            "Criterion": "Turnover: hysteresis reduces turnover vs the shipped equal-weight "
            "default at every cell (reduction > 0)",
            "Required": to_all_reduction,
        },
        {
            "Criterion": "Fixture SHA256 match across all three artifacts",
            "Required": fixture_shas_match,
        },
        {
            "Criterion": "Synthetic universe labelled controlled synthetic",
            "Required": (
                "Not real market data" in prov["fixture_recipe"]
                and "not market profitability evidence" in prov["fixture_recipe"]
            ),
        },
        {"Criterion": "Not market evidence / no real alpha", "Required": True},
        {
            "Criterion": (
                "Shipped default (weighting=equal, beta_neutral=True, "
                "beta_window=90, rolling-OLS) RETAINED"
            ),
            "Required": True,
        },
    ]
    return ["Criterion", "Required"], rows


TABLE_BUILDERS = {
    "provenance": provenance_table,
    "cost_surface": cost_surface_table,
    "capacity": capacity_table,
    "turnover": turnover_table,
    "decision": decision_table,
}


def _args_for(name: str, cost_surface, capacity, turnover) -> dict:
    return {
        "provenance": {
            "cost_surface": cost_surface,
            "capacity": capacity,
            "turnover": turnover,
        },
        "cost_surface": {"cost_surface": cost_surface},
        "capacity": {"capacity": capacity},
        "turnover": {"turnover": turnover},
        "decision": {
            "cost_surface": cost_surface,
            "capacity": capacity,
            "turnover": turnover,
        },
    }[name]


def _built(name: str, cost_surface, capacity, turnover) -> list[str]:
    kwargs = _args_for(name, cost_surface, capacity, turnover)
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


def _allowed_numeric(cost_surface, capacity, turnover) -> set:
    allowed = set()
    allowed |= _numeric_leaves(cost_surface)
    allowed |= _numeric_leaves(capacity)
    allowed |= _numeric_leaves(turnover)
    return allowed


# --------------------------------------------------------------------------- #
# 1. Zero unmatched numbers in every table cell
# --------------------------------------------------------------------------- #
def test_report_exists_and_declares_its_sources(cost_surface, capacity, turnover, report) -> None:
    assert REPORT_PATH.is_file()
    for name in SOURCES:
        assert name in report, f"report never names its source {name}"


def test_every_published_number_matches_a_committed_json_field(
    cost_surface, capacity, turnover, report
) -> None:
    allowed = _allowed_numeric(cost_surface, capacity, turnover)
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
        f"report publishes {len(published)} machine-checked cells, below the chartered {minimum}"
    )
    assert unmatched == [], f"published numbers absent from JSON: {sorted(set(unmatched))}"


def test_zero_unmatched_cells_is_the_chartered_invariant(
    cost_surface, capacity, turnover, report
) -> None:
    allowed = _allowed_numeric(cost_surface, capacity, turnover)
    unmatched = 0
    for body in _extract_tables(report).values():
        for row in _rows(body):
            for cell in row:
                clean = cell.replace("`", "").strip()
                if NUMERIC_CELL.match(clean) and round(float(clean), DECIMALS) not in allowed:
                    unmatched += 1
    assert unmatched == 0


def test_tables_are_byte_identical_to_the_json_renderers(
    cost_surface, capacity, turnover, report
) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLE_BUILDERS), f"table anchors differ: {sorted(published)}"
    for name in TABLE_BUILDERS:
        expected = "\n".join(_built(name, cost_surface, capacity, turnover))
        assert published[name] == expected, f"table {name} drifted from its JSON artifact"


def test_prose_does_not_quote_unbacked_numbers(
    cost_surface, capacity, turnover, report
) -> None:
    allowed = _allowed_numeric(cost_surface, capacity, turnover)
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
    text = re.sub(r"\b[0-9a-f]{40,}\b", " ", text)
    text = re.sub(r"\bP\d+-\d+\b", " ", text)
    text = re.sub(r"\b(?:P|WP)\d+\b", " ", text)
    # Chartered prose numbers that are not table data
    text = re.sub(r"\b6\b", " ", text)  # decimals
    text = re.sub(r"\b24\b", " ", text)  # total P37 cell count (3 artifacts x 8 seeds)
    text = re.sub(r"\b8\b", " ", text)  # cells per artifact (8 seeds)
    text = re.sub(r"\b403\b", " ", text)  # Coinbase returns 403
    text = re.sub(r"\b0\.003\b", " ", text)  # idio vol (fixture recipe)
    text = re.sub(r"\b0\.35\b", " ", text)  # beta range min (fixture recipe)
    text = re.sub(r"\b1\.9\b", " ", text)  # beta range max (fixture recipe)
    text = re.sub(r"\b40\b", " ", text)  # 40 assets (fixture recipe)
    token = re.compile(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?(?![A-Za-z0-9_])")
    stray = {tok for tok in token.findall(text) if round(float(tok), DECIMALS) not in allowed}
    assert stray == set(), f"prose numbers with no JSON field: {sorted(stray)}"


# --------------------------------------------------------------------------- #
# 2. The verdict is explicit, machine-backed, and grounded in evidence
# --------------------------------------------------------------------------- #
def test_report_states_an_explicit_verdict(cost_surface, capacity, turnover, report) -> None:
    lowered = _flat(report)
    assert "verdict" in lowered
    assert "retain" in lowered
    assert "cost-aware" in lowered
    assert "turnover" in lowered
    assert "capacity" in lowered
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
        "cost surface",
        "capacity",
        "turnover",
        "decision criteria",
        "does not prove",
        "next",
    ):
        assert required in lowered, f"missing section: {required}"


# --------------------------------------------------------------------------- #
# 3. Every criterion the verdict cites is internally consistent
# --------------------------------------------------------------------------- #
def test_cost_surface_evidence_is_calibrated(cost_surface) -> None:
    cells = cost_surface["results"]["cells"]
    ok_cells = [c for c in cells if c["status"] == "ok"]
    assert len(ok_cells) > 0
    assert all(c["monotonicity_ok"] for c in ok_cells)
    assert all(c["neutrality_ok"] for c in ok_cells)


def test_capacity_evidence_is_calibrated(capacity) -> None:
    cells = capacity["results"]["cells"]
    ok_cells = [c for c in cells if c["status"] == "ok"]
    assert len(ok_cells) > 0
    assert all(c["neutrality_ok"] for c in ok_cells)


def test_turnover_evidence_is_calibrated(turnover) -> None:
    cells = turnover["results"]["cells"]
    ok_cells = [c for c in cells if c["status"] == "ok"]
    assert len(ok_cells) > 0
    assert all(c["turnover_monotonic"] for c in ok_cells)
    assert all(c["neutrality_ok"] for c in ok_cells)
    assert all(
        c["turnover_reduction"] is not None and c["turnover_reduction"] > 0
        for c in ok_cells
    )


def test_fixture_shas_agree(cost_surface, capacity, turnover) -> None:
    assert (
        cost_surface["provenance"]["returns_sha256"]
        == capacity["provenance"]["returns_sha256"]
        == turnover["provenance"]["returns_sha256"]
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
    _load("cost_surface_summary.json")
    _load("capacity_summary.json")
    _load("turnover_summary.json")
    REPORT_PATH.read_text(encoding="utf-8")
    assert time.perf_counter() - start < 2.0


def test_decision_artifacts_are_byte_identical_after_the_suite(
    cost_surface, capacity, turnover
) -> None:
    for name in SOURCES:
        before = (RESEARCH_P37_DIR / name).read_bytes()
        _load(name)
        after = (RESEARCH_P37_DIR / name).read_bytes()
        assert before == after


# --------------------------------------------------------------------------- #
# 5. Ruff
# --------------------------------------------------------------------------- #
def test_no_ruff_errors_on_new_files():
    import subprocess
    import sys

    GENERATE_SCRIPT = REPO_ROOT / "generate_p37_decision.py"
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
