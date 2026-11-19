"""Acceptance tests for P22 WP4: the decision-grade GO/NO-GO report.

These tests are the claim that ``docs/BAB_P22_DECISION.md`` publishes only
numbers that exist in the committed P22 JSON artifacts
(``research_state/bab_p22/{charter,null_battery,impact_surface,capacity}.json``).
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
RESEARCH_DIR = REPO_ROOT / "research_state/bab_p22"
REPORT_PATH = REPO_ROOT / "docs/BAB_P22_DECISION.md"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)
NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ISO_DATE = r"\d{4}-\d{2}-\d{2}"

SOURCES = ("charter.json", "null_battery.json", "impact_surface.json", "capacity.json")


# --------------------------------------------------------------------------- #
# Loading (JSON only -- no harness build_* calls)
# --------------------------------------------------------------------------- #
def _load(name: str) -> dict:
    return json.loads((RESEARCH_DIR / f"{name}.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def charter() -> dict:
    return _load("charter")


@pytest.fixture(scope="module")
def null_battery() -> dict:
    return _load("null_battery")


@pytest.fixture(scope="module")
def impact_surface() -> dict:
    return _load("impact_surface")


@pytest.fixture(scope="module")
def capacity() -> dict:
    return _load("capacity")


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


def _book(books: list[dict], variant: str, weighting: str) -> dict:
    for book in books:
        if book["variant"] == variant and book["weighting"] == weighting:
            return book
    raise AssertionError(f"no book for variant={variant!r} weighting={weighting!r}")


def provenance_table(
    charter, null_battery, impact_surface, capacity
) -> tuple[list[str], list[dict]]:
    prov = charter["provenance"]
    charter_body = charter["charter"]
    impact_prov = impact_surface["provenance"]
    refer = null_battery["provenance"]
    rows = [
        {"Fact": "Charter schema", "Value": charter["schema"]},
        {"Fact": "Capacity schema", "Value": capacity["schema"]},
        {"Fact": "Campaign", "Value": charter_body["campaign"]},
        {"Fact": "Charter question", "Value": charter_body["question"]},
        {"Fact": "Certified by prior campaign", "Value": charter_body["answered_by_p21"]},
        {"Fact": "Universe seed", "Value": impact_prov["universe_seed"]},
        {"Fact": "Reference universe seed", "Value": refer["reference_universe_seed"]},
        {"Fact": "Synthetic", "Value": impact_prov["synthetic"]},
        {"Fact": "Licensed data required", "Value": charter_body["licensed_data_required"]},
        {"Fact": "Not market evidence", "Value": charter_body["not_market_evidence"]},
        {"Fact": "Artifact gated", "Value": charter_body["artifact_gated"]},
        {"Fact": "Nominal slack", "Value": prov["nominal_slack"]},
        {
            "Fact": "Planted panel sha256",
            "Value": "`" + impact_prov["panel_sha256"]["planted"] + "`",
        },
        {
            "Fact": "Null panel sha256",
            "Value": "`" + impact_prov["panel_sha256"]["null"] + "`",
        },
        {
            "Fact": "Reference panel shas matched",
            "Value": refer["reference_panel_sha256_matched"],
        },
    ]
    return ["Fact", "Value"], rows


def null_battery_table(null_battery) -> tuple[list[str], list[dict]]:
    summary = null_battery["provenance"]["summary"]
    planted_min = summary["planted_recovery_min"]
    positive_fraction = summary["planted_recovery_positive_fraction"]
    rows = [
        {"Statistic": "Chartered seeds", "Value": summary["n_seeds"]},
        {"Statistic": "Null books", "Value": summary["n_null_books"]},
        {"Statistic": "Planted books", "Value": summary["n_planted_books"]},
        {"Statistic": "Null recovery max abs", "Value": summary["null_recovery_max_abs"]},
        {
            "Statistic": "Null books with zero recovery",
            "Value": summary["null_recovery_zero_books"],
        },
        {
            "Statistic": "Null recovery exactly zero every seed",
            "Value": summary["null_recovery_exactly_zero_every_seed"],
        },
        {"Statistic": "False positives", "Value": summary["fpr_count"]},
        {"Statistic": "False-positive denominator", "Value": summary["fpr_denominator"]},
        {"Statistic": "False-positive rate", "Value": summary["fpr_rate"]},
        {"Statistic": "False-positive expected count", "Value": summary["fpr_expected_count"]},
        {
            "Statistic": "False-positive max declared",
            "Value": summary["fpr_max_count_declared"],
        },
        {
            "Statistic": "False-positive within bound",
            "Value": summary["fpr_within_declared_bound"],
        },
        {"Statistic": "Planted recovery min equal", "Value": planted_min["equal"]},
        {"Statistic": "Planted recovery min rank", "Value": planted_min["rank"]},
        {
            "Statistic": "Planted recovery positive fraction equal",
            "Value": positive_fraction["equal"],
        },
        {
            "Statistic": "Planted recovery positive fraction rank",
            "Value": positive_fraction["rank"],
        },
        {"Statistic": "Null Sharpe max", "Value": summary["null_sharpe_max"]},
        {"Statistic": "Planted Sharpe min", "Value": summary["planted_sharpe_min"]},
        {
            "Statistic": "Planted recovery exceeds null max",
            "Value": summary["planted_recovery_exceeds_null_max"],
        },
    ]
    return ["Statistic", "Value"], rows


def seed_table(null_battery) -> tuple[list[str], list[dict]]:
    columns = [
        "seed",
        "planted_recovery_equal",
        "planted_recovery_rank",
        "null_sharpe_equal",
        "null_sharpe_rank",
        "null_p_equal",
        "null_p_rank",
    ]
    rows = []
    for payload in null_battery["seeds"]:
        books = payload["books"]
        rows.append(
            {
                "seed": payload["seed"],
                "planted_recovery_equal": _book(books, "planted", "equal")["recovery_mean"],
                "planted_recovery_rank": _book(books, "planted", "rank")["recovery_mean"],
                "null_sharpe_equal": _book(books, "null", "equal")["oos_sharpe"],
                "null_sharpe_rank": _book(books, "null", "rank")["oos_sharpe"],
                "null_p_equal": _book(books, "null", "equal")["p_value"],
                "null_p_rank": _book(books, "null", "rank")["p_value"],
            }
        )
    return columns, rows


def impact_table(impact_surface) -> tuple[list[str], list[dict]]:
    columns = [
        "variant",
        "weighting",
        "level",
        "costed_sharpe",
        "cost_drag_mean",
        "total_cost",
        "final_cumulative",
    ]
    rows = []
    for book in impact_surface["books"]:
        for row in book["surfaces"]["market_impact"]:
            rows.append(
                {
                    "variant": book["variant"],
                    "weighting": book["weighting"],
                    "level": row["level"],
                    "costed_sharpe": row["costed_sharpe"],
                    "cost_drag_mean": row["cost_drag_mean"],
                    "total_cost": row["total_cost"],
                    "final_cumulative": row["final_cumulative"],
                }
            )
    return columns, rows


def capacity_table(capacity) -> tuple[list[str], list[dict]]:
    columns = [
        "variant",
        "weighting",
        "active_rows",
        "gross_sharpe",
        "break_even_coefficient",
        "break_even_sharpe",
        "censored",
        "censor_reason",
        "bracket_halving_verified",
    ]
    rows = []
    for book in capacity["books"]:
        rows.append({column: book[column] for column in columns})
    return columns, rows


def decision_table(charter) -> tuple[list[str], list[dict]]:
    thresholds = charter["provenance"]["acceptance_thresholds"]
    wp4 = thresholds["wp4"]
    rows = [
        {
            "Criterion": "Explicit signal-or-noise verdict",
            "Required": wp4["explicit_signal_noise_verdict"],
        },
        {"Criterion": "NO-GO for market", "Required": wp4["no_go_for_market"]},
        {"Criterion": "No harness re-run", "Required": wp4["no_harness_re_run"]},
        {
            "Criterion": "Planted recovery labelled controlled synthetic",
            "Required": wp4["planted_recovery_labelled_controlled_synthetic"],
        },
        {"Criterion": "Numbers matched minimum", "Required": wp4["numbers_matched_min"]},
        {"Criterion": "Unmatched cells maximum", "Required": wp4["zero_unmatched_cells"]},
        {"Criterion": "Nominal slack", "Required": thresholds["nominal_slack"]},
    ]
    return ["Criterion", "Required"], rows


TABLE_BUILDERS = {
    "provenance": provenance_table,
    "null_battery": null_battery_table,
    "null_seeds": seed_table,
    "impact": impact_table,
    "capacity": capacity_table,
    "decision": decision_table,
}


def _args_for(name: str, charter, null_battery, impact_surface, capacity) -> dict:
    return {
        "provenance": {
            "charter": charter,
            "null_battery": null_battery,
            "impact_surface": impact_surface,
            "capacity": capacity,
        },
        "null_battery": {"null_battery": null_battery},
        "null_seeds": {"null_battery": null_battery},
        "impact": {"impact_surface": impact_surface},
        "capacity": {"capacity": capacity},
        "decision": {"charter": charter},
    }[name]


def _built(name: str, charter, null_battery, impact_surface, capacity) -> list[str]:
    kwargs = _args_for(name, charter, null_battery, impact_surface, capacity)
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
    charter, null_battery, impact_surface, capacity, report
) -> None:
    allowed = set()
    for payload in (charter, null_battery, impact_surface, capacity):
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
    charter, null_battery, impact_surface, capacity, report
) -> None:
    allowed = set()
    for payload in (charter, null_battery, impact_surface, capacity):
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
    charter, null_battery, impact_surface, capacity, report
) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLE_BUILDERS), f"table anchors differ: {sorted(published)}"
    for name in TABLE_BUILDERS:
        expected = "\n".join(_built(name, charter, null_battery, impact_surface, capacity))
        assert published[name] == expected, f"table {name} drifted from its JSON artifact"


def test_prose_does_not_quote_unbacked_numbers(
    charter, null_battery, impact_surface, capacity, report
) -> None:
    allowed = set()
    for payload in (charter, null_battery, impact_surface, capacity):
        allowed |= _numeric_leaves(payload)
    text = re.sub(r"<!--.*?-->", " ", report, flags=re.DOTALL)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(ISO_DATE, " ", text)
    text = re.sub(r"\b[0-9a-f]{40,}\b", " ", text)
    text = re.sub(r"§\s*\d+(?:\.\d+)*", " ", text)
    text = re.sub(r"\b(?:P|WP)\d+\b", " ", text)
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
    assert "not a demonstrated profitable strategy" in lowered
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
        "null battery",
        "impact",
        "capacity",
        "decision",
        "does not prove",
        "next",
    ):
        assert required in lowered, f"missing section: {required}"


# --------------------------------------------------------------------------- #
# 3. Every criterion the verdict cites is internally consistent
# --------------------------------------------------------------------------- #
def test_null_battery_evidence_is_calibrated(null_battery) -> None:
    prov = null_battery["provenance"]
    summary = prov["summary"]
    assert summary["null_recovery_max_abs"] == 0.0
    assert summary["null_recovery_exactly_zero_every_seed"] is True
    assert summary["null_recovery_zero_books"] == summary["n_null_books"]
    assert summary["fpr_count"] == summary["fpr_rate"] * summary["fpr_denominator"]
    assert summary["fpr_count"] <= summary["fpr_max_count_declared"]
    assert summary["fpr_within_declared_bound"] is True
    assert summary["planted_recovery_exceeds_null_max"] is True
    assert summary["planted_recovery_positive_fraction"]["equal"] == 1.0
    assert summary["planted_recovery_positive_fraction"]["rank"] == 1.0
    significant_nulls = 0
    for payload in null_battery["seeds"]:
        for book in payload["books"]:
            if book["variant"] == "null":
                significant_nulls += int(book["significant"])
    assert significant_nulls == summary["fpr_count"]
    for payload in null_battery["seeds"]:
        for book in payload["books"]:
            if book["variant"] == "null":
                assert book["recovery_mean"] == 0.0
                assert 0.0 <= book["p_value"] <= 1.0
                assert book["significant"] is (book["p_value"] < prov["nominal_slack"])
            else:
                assert book["recovery_mean"] > 0.0


def test_impact_surface_is_monotone_and_zero_level_is_gross(impact_surface) -> None:
    grid = impact_surface["provenance"]["impact_coefficient_grid"]
    for book in impact_surface["books"]:
        surface = book["surfaces"]["market_impact"]
        assert [row["level"] for row in surface] == grid
        assert surface[0]["costed_sharpe"] == book["gross_sharpe"]
        assert surface[0]["total_cost"] == 0.0
        assert book["monotonicity"]["market_impact"] is True
        assert book["period_wise_non_increasing"]["market_impact"] is True
        sharpes = [row["costed_sharpe"] for row in surface]
        assert all(
            current <= previous + 1e-9
            for previous, current in zip(sharpes, sharpes[1:])
        ), f"{book['variant']}/{book['weighting']} impact curve rose"


def test_capacity_break_even_is_bracketed_or_documented(capacity) -> None:
    for book in capacity["books"]:
        if book["censored"]:
            assert book["break_even_coefficient"] is None
            assert book["break_even_sharpe"] is None
            assert isinstance(book["censor_reason"], str) and book["censor_reason"]
            signs = [row["sign"] for row in book["sign_test"]]
            assert signs[0] == 1 and -1 not in signs
        else:
            assert book["censor_reason"] is None
            assert book["break_even_coefficient"] > 0.0
            assert abs(book["break_even_sharpe"]) <= 0.001
            assert book["bracket_halving_verified"] is True
            signs = [row["sign"] for row in book["sign_test"]]
            assert signs[0] == 1 and -1 in signs
            first_negative = signs.index(-1)
            lo_level = book["sign_test"][first_negative - 1]["coefficient"]
            hi_level = book["sign_test"][first_negative]["coefficient"]
            assert lo_level <= book["break_even_coefficient"] <= hi_level


def test_panel_shas_agree_across_artifacts(charter, null_battery, impact_surface, capacity) -> None:
    expected = impact_surface["provenance"]["panel_sha256"]
    assert capacity["provenance"]["panel_sha256"] == expected
    assert null_battery["provenance"]["reference_panel_sha256"] == expected
    assert null_battery["provenance"]["committed_p21_panel_sha256"] == expected
    assert len(set(expected.values())) == 2, "planted and null panels must be distinct"
    verdict = charter["provenance"]["p21_verdict"]
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
    for name in ("charter", "null_battery", "impact_surface", "capacity"):
        _load(name)
    REPORT_PATH.read_text(encoding="utf-8")
    assert time.perf_counter() - start < 2.0


def test_decision_artifacts_are_byte_identical_after_the_suite() -> None:
    names = ("charter", "null_battery", "impact_surface", "capacity")
    before = {
        name: hashlib.sha256((RESEARCH_DIR / f"{name}.json").read_bytes()).hexdigest()
        for name in names
    }
    for name in names:
        _load(name)
    after = {
        name: hashlib.sha256((RESEARCH_DIR / f"{name}.json").read_bytes()).hexdigest()
        for name in names
    }
    assert before == after
