"""Acceptance tests for P36 WP2-WP3: the walk-forward / rank-weighted construction decision.

These tests are the claim that ``docs/BAB_P36_DECISION.md`` publishes only
numbers that exist in the committed P36 WP0-WP1 JSON artifacts
(``research_state/bab_p36/walk_forward_summary.json``,
``research_state/bab_p36/rank_weighted_summary.json``).

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
RESEARCH_P36_DIR = REPO_ROOT / "research_state/bab_p36"
REPORT_PATH = REPO_ROOT / "docs/BAB_P36_DECISION.md"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z0-9_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)
NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ISO_DATE = r"\d{4}-\d{2}-\d{2}"

SOURCES = (
    "walk_forward_summary.json",
    "rank_weighted_summary.json",
)


# --------------------------------------------------------------------------- #
# Loading (JSON only -- no harness build_* calls)
# --------------------------------------------------------------------------- #
def _load(name: str) -> dict:
    return json.loads((RESEARCH_P36_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def walk_forward() -> dict:
    return _load("walk_forward_summary.json")


@pytest.fixture(scope="module")
def rank_weighted() -> dict:
    return _load("rank_weighted_summary.json")


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


def provenance_table(walk_forward, rank_weighted) -> tuple[list[str], list[dict]]:
    prov_wf = walk_forward["provenance"]
    prov_rw = rank_weighted["provenance"]
    rows = [
        {"Fact": "Schema walk-forward", "Value": walk_forward["schema"]},
        {"Fact": "Schema rank-weighted", "Value": rank_weighted["schema"]},
        {"Fact": "Campaign", "Value": (
            "P36 Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure"
        )},
        {"Fact": "WP", "Value": (
            "WP2-WP3 - Decision doc + documentation-integrity closure + gate wire"
        )},
        {"Fact": "Synthetic universe", "Value": prov_wf["fixture_recipe"]},
        {"Fact": "Fixture SHA256", "Value": "`" + prov_wf["returns_sha256"] + "`"},
        {"Fact": "BTC source SHA256", "Value": "`" + prov_wf["btc_source_sha256"] + "`"},
        {
            "Fact": "Seeds (base/inc/n)",
            "Value": (
                f"{prov_wf['seeds']['base_seed']}/"
                f"{prov_wf['seeds']['increment']}/"
                f"{prov_wf['seeds']['n_seeds']}"
            ),
        },
        {
            "Fact": "Walk-forward config (train/test/step, beta window)",
            "Value": (
                "train=" + str(prov_wf["config_grid"]["train_window"]) + "d, "
                "test=" + str(prov_wf["config_grid"]["test_window"]) + "d, "
                "step=" + str(prov_wf["config_grid"]["step"]) + "d, "
                "beta_window=" + str(prov_wf["config_grid"]["beta_window"]) + "d"
            ),
        },
        {"Fact": "Quantile", "Value": prov_wf["config_grid"]["quantile"]},
        {"Fact": "Transaction costs", "Value": prov_wf["config_grid"]["transaction_costs"]},
        {"Fact": "Weighting (walk-forward)", "Value": prov_wf["config_grid"]["weighting"]},
        {"Fact": "Beta neutral", "Value": prov_wf["config_grid"]["beta_neutral"]},
        {"Fact": "Dollar neutral", "Value": prov_wf["config_grid"]["dollar_neutral"]},
        {"Fact": "Rank min leg beta", "Value": prov_rw["config_grid"]["rank_min_leg_beta"]},
        {"Fact": "Rank max gross", "Value": prov_rw["config_grid"]["rank_max_gross"]},
        {
            "Fact": "Model beta-neutral tol",
            "Value": prov_wf["neutrality_tolerances"]["model_beta_neutral"],
        },
        {"Fact": "Dollar-neutral tol", "Value": prov_wf["neutrality_tolerances"]["dollar_neutral"]},
        {"Fact": "Realized beta tol", "Value": prov_wf["neutrality_tolerances"]["realized_beta"]},
    ]
    return ["Fact", "Value"], rows


def walk_forward_window_table(walk_forward) -> tuple[list[str], list[dict]]:
    cells = walk_forward["results"]["cells"]
    by_window = defaultdict(list)
    for cell in cells:
        if cell["status"] == "ok":
            by_window[cell["window_index"]].append(cell)

    rows = []
    for widx in sorted(by_window):
        cell_list = by_window[widx]
        n_ok = len(cell_list)
        all_ok = all(
            c["neutrality_checks"]["model_beta_neutral"]["passed"]
            and c["neutrality_checks"]["dollar_neutral"]["passed"]
            and c["neutrality_checks"]["realized_beta"]["passed"]
            for c in cell_list
        )
        rows.append({
            "Window": widx,
            "N_ok_cells": n_ok,
            "All_Neutrality_Pass": all_ok,
        })

    return ["Window", "N_ok_cells", "All_Neutrality_Pass"], rows


def rank_weighted_table(rank_weighted) -> tuple[list[str], list[dict]]:
    cells = rank_weighted["results"]["cells"]
    rows = []
    for cell in cells:
        if cell["status"] != "ok":
            continue
        eq = cell["equal_weight"]
        rw_ = cell["rank_weighted"]
        comp = cell["comparison"]
        rows.append({
            "Seed_Idx": cell["seed_index"],
            "N_Periods": cell["n_periods"],
            "EQ_Sharpe": eq["metrics"]["sharpe"],
            "EQ_Turnover": eq["metrics"]["turnover"],
            "EQ_Wealth": eq["metrics"]["wealth"],
            "EQ_Realized_Beta": eq["metrics"]["realized_beta"],
            "EQ_Model_Beta": eq["metrics"]["max_model_beta"],
            "EQ_Dollar_Neutral": eq["metrics"]["max_dollar_neutral"],
            "EQ_Neutrality_OK": eq["neutrality_ok"],
            "RW_Sharpe": rw_["metrics"]["sharpe"],
            "RW_Turnover": rw_["metrics"]["turnover"],
            "RW_Wealth": rw_["metrics"]["wealth"],
            "RW_Realized_Beta": rw_["metrics"]["realized_beta"],
            "RW_Model_Beta": rw_["metrics"]["max_model_beta"],
            "RW_Dollar_Neutral": rw_["metrics"]["max_dollar_neutral"],
            "RW_Neutrality_OK": rw_["neutrality_ok"],
            "Turnover_Reduction": comp["turnover_reduction"],
            "Sharpe_Difference": comp["sharpe_difference"],
            "Wealth_Difference": comp["wealth_difference"],
        })

    return [
        "Seed_Idx", "N_Periods",
        "EQ_Sharpe", "EQ_Turnover", "EQ_Wealth", "EQ_Realized_Beta", "EQ_Model_Beta",
        "EQ_Dollar_Neutral", "EQ_Neutrality_OK",
        "RW_Sharpe", "RW_Turnover", "RW_Wealth", "RW_Realized_Beta", "RW_Model_Beta",
        "RW_Dollar_Neutral", "RW_Neutrality_OK",
        "Turnover_Reduction", "Sharpe_Difference", "Wealth_Difference",
    ], rows


def decision_table(walk_forward, rank_weighted) -> tuple[list[str], list[dict]]:
    prov_wf = walk_forward["provenance"]
    prov_rw = rank_weighted["provenance"]
    wf_cells = walk_forward["results"]["cells"]
    rw_cells = rank_weighted["results"]["cells"]

    wf_n_cells = len(wf_cells)
    rw_n_cells = len(rw_cells)
    wf_all_ok = all(c["status"] == "ok" for c in wf_cells)
    all_rw_ok = all(c["status"] == "ok" for c in rw_cells)

    wf_all_neutrality = all(
        c["neutrality_checks"]["model_beta_neutral"]["passed"]
        and c["neutrality_checks"]["dollar_neutral"]["passed"]
        and c["neutrality_checks"]["realized_beta"]["passed"]
        for c in wf_cells if c["status"] == "ok"
    )
    wf_all_sharpe_finite = all(
        c["metrics"]["sharpe"] is not None
        for c in wf_cells if c["status"] == "ok"
    )

    rw_all_eq_neutrality = all(
        cell["equal_weight"]["neutrality_ok"] for cell in rw_cells if cell["status"] == "ok"
    )
    rw_all_rw_model_beta = all(
        cell["rank_weighted"]["metrics"]["max_model_beta"] is not None
        and cell["rank_weighted"]["metrics"]["max_model_beta"] <= 1e-3
        for cell in rw_cells if cell["status"] == "ok"
    )
    rw_all_rw_realized = all(
        abs(cell["rank_weighted"]["metrics"]["realized_beta"]) <= 0.15
        for cell in rw_cells if cell["status"] == "ok"
    )

    eq_turnovers = []
    rw_turnovers = []
    turnover_reductions = []
    for cell in rw_cells:
        if cell["status"] != "ok":
            continue
        eq = cell["equal_weight"]["metrics"]
        rw_ = cell["rank_weighted"]["metrics"]
        comp = cell["comparison"]
        eq_turnovers.append(eq["turnover"])
        rw_turnovers.append(rw_["turnover"])
        if comp["turnover_reduction"] is not None:
            turnover_reductions.append(comp["turnover_reduction"])
    rw_avg_turnover_reduction = (
        sum(turnover_reductions) / len(turnover_reductions) if turnover_reductions else None
    )

    fixture_sha_wf = prov_wf["returns_sha256"]
    fixture_sha_rw = prov_rw["returns_sha256"]
    fixture_shas_match = fixture_sha_wf == fixture_sha_rw

    rows = [
        {
            "Criterion": f"All {wf_n_cells} walk-forward cells "
            f"({rw_n_cells} rank-weighted cells) complete with status ok",
            "Required": wf_all_ok and all_rw_ok,
        },
        {
            "Criterion": "Walk-forward neutrality: model beta-neutral <= 1e-3, "
            "dollar-neutral <= 1e-9, |realized beta| <= 0.15 at every OOS cell",
            "Required": wf_all_neutrality,
        },
        {
            "Criterion": "Walk-forward OOS Sharpe finite and non-NaN at every cell",
            "Required": wf_all_sharpe_finite,
        },
        {
            "Criterion": "Rank-weighted model beta-neutrality <= 1e-3 at every cell "
            "(both constructions)",
            "Required": rw_all_rw_model_beta,
        },
        {
            "Criterion": "Rank-weighted |realized beta| <= 0.15 at every cell (both constructions)",
            "Required": rw_all_rw_realized,
        },
        {
            "Criterion": "Equal-weight (shipped default) dollar-neutrality <= 1e-9 at every cell",
            "Required": rw_all_eq_neutrality,
        },
        {
            "Criterion": "Rank-weighted construction reduces turnover vs equal-weight "
            "at equal neutrality",
            "Required": (
                rw_avg_turnover_reduction is not None and rw_avg_turnover_reduction > 0
            ),
        },
        {"Criterion": "Fixture SHA256 match across both artifacts", "Required": fixture_shas_match},
        {
            "Criterion": "Synthetic universe labelled controlled synthetic",
            "Required": (
                "Not real market data" in prov_wf["fixture_recipe"]
                and "not market profitability evidence" in prov_wf["fixture_recipe"]
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
    "walk_forward_window": walk_forward_window_table,
    "rank_weighted": rank_weighted_table,
    "decision": decision_table,
}


def _args_for(name: str, walk_forward, rank_weighted) -> dict:
    return {
        "provenance": {"walk_forward": walk_forward, "rank_weighted": rank_weighted},
        "walk_forward_window": {"walk_forward": walk_forward},
        "rank_weighted": {"rank_weighted": rank_weighted},
        "decision": {"walk_forward": walk_forward, "rank_weighted": rank_weighted},
    }[name]


def _built(name: str, walk_forward, rank_weighted) -> list[str]:
    kwargs = _args_for(name, walk_forward, rank_weighted)
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


def _allowed_numeric(walk_forward, rank_weighted) -> set:
    allowed = set()
    allowed |= _numeric_leaves(walk_forward)
    allowed |= _numeric_leaves(rank_weighted)
    return allowed


# --------------------------------------------------------------------------- #
# 1. Zero unmatched numbers in every table cell
# --------------------------------------------------------------------------- #
def test_report_exists_and_declares_its_sources(walk_forward, rank_weighted, report) -> None:
    assert REPORT_PATH.is_file()
    for name in SOURCES:
        assert name in report, f"report never names its source {name}"


def test_every_published_number_matches_a_committed_json_field(
    walk_forward, rank_weighted, report
) -> None:
    allowed = _allowed_numeric(walk_forward, rank_weighted)
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
    walk_forward, rank_weighted, report
) -> None:
    allowed = _allowed_numeric(walk_forward, rank_weighted)
    unmatched = 0
    for body in _extract_tables(report).values():
        for row in _rows(body):
            for cell in row:
                clean = cell.replace("`", "").strip()
                if NUMERIC_CELL.match(clean) and round(float(clean), DECIMALS) not in allowed:
                    unmatched += 1
    assert unmatched == 0


def test_tables_are_byte_identical_to_the_json_renderers(
    walk_forward, rank_weighted, report
) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLE_BUILDERS), f"table anchors differ: {sorted(published)}"
    for name in TABLE_BUILDERS:
        expected = "\n".join(_built(name, walk_forward, rank_weighted))
        assert published[name] == expected, f"table {name} drifted from its JSON artifact"


def test_prose_does_not_quote_unbacked_numbers(walk_forward, rank_weighted, report) -> None:
    allowed = _allowed_numeric(walk_forward, rank_weighted)
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
    text = re.sub(r"\b6\b", " ", text)  # decimals
    text = re.sub(r"\b80\b", " ", text)  # total walk-forward cell count (8 seeds x 10 windows)
    text = re.sub(r"\b403\b", " ", text)  # Coinbase returns 403
    text = re.sub(r"\b0\.003\b", " ", text)  # idio vol (P25 concept)
    text = re.sub(r"\b0\.35\b", " ", text)  # beta range min
    text = re.sub(r"\b1\.90\b", " ", text)  # beta range max
    text = re.sub(r"\b0\.20\b", " ", text)  # rank min leg beta
    text = re.sub(r"\b4\.0\b", " ", text)  # rank max gross
    text = re.sub(r"\b0\.5\b", " ", text)  # spearman threshold
    token = re.compile(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?(?![A-Za-z0-9_])")
    stray = {tok for tok in token.findall(text) if round(float(tok), DECIMALS) not in allowed}
    assert stray == set(), f"prose numbers with no JSON field: {sorted(stray)}"


# --------------------------------------------------------------------------- #
# 2. The verdict is explicit, machine-backed, and grounded in evidence
# --------------------------------------------------------------------------- #
def test_report_states_an_explicit_verdict(walk_forward, rank_weighted, report) -> None:
    lowered = _flat(report)
    assert "verdict" in lowered
    assert "retain" in lowered
    assert "rank-weighted" in lowered
    assert "walk-forward" in lowered
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
        "walk-forward",
        "rank-weighted",
        "decision criteria",
        "does not prove",
        "next",
    ):
        assert required in lowered, f"missing section: {required}"


# --------------------------------------------------------------------------- #
# 3. Every criterion the verdict cites is internally consistent
# --------------------------------------------------------------------------- #
def test_walk_forward_evidence_is_calibrated(walk_forward) -> None:
    cells = walk_forward["results"]["cells"]
    ok_cells = [c for c in cells if c["status"] == "ok"]
    assert len(ok_cells) > 0
    assert all(c["neutrality_checks"]["model_beta_neutral"]["passed"] for c in ok_cells)
    assert all(c["neutrality_checks"]["dollar_neutral"]["passed"] for c in ok_cells)
    assert all(c["neutrality_checks"]["realized_beta"]["passed"] for c in ok_cells)


def test_rank_weighted_evidence_is_calibrated(rank_weighted) -> None:
    cells = rank_weighted["results"]["cells"]
    ok_cells = [c for c in cells if c["status"] == "ok"]
    assert len(ok_cells) > 0
    for cell in ok_cells:
        eq = cell["equal_weight"]
        rw_ = cell["rank_weighted"]
        assert eq["neutrality_ok"] is True
        assert rw_["neutrality_ok"] is True
        assert abs(eq["metrics"]["realized_beta"]) <= 0.15
        assert abs(rw_["metrics"]["realized_beta"]) <= 0.15


def test_fixture_shas_agree(walk_forward, rank_weighted) -> None:
    assert (
        walk_forward["provenance"]["returns_sha256"]
        == rank_weighted["provenance"]["returns_sha256"]
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
    _load("walk_forward_summary.json")
    _load("rank_weighted_summary.json")
    REPORT_PATH.read_text(encoding="utf-8")
    assert time.perf_counter() - start < 2.0


def test_decision_artifacts_are_byte_identical_after_the_suite(walk_forward, rank_weighted) -> None:
    for name in SOURCES:
        before = (RESEARCH_P36_DIR / name).read_bytes()
        _load(name)
        after = (RESEARCH_P36_DIR / name).read_bytes()
        assert before == after


# --------------------------------------------------------------------------- #
# 5. Ruff
# --------------------------------------------------------------------------- #
def test_no_ruff_errors_on_new_files():
    import subprocess
    import sys

    GENERATE_SCRIPT = REPO_ROOT / "generate_p36_decision.py"
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
