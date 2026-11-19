"""Acceptance tests for P21 WP4: the honest signal-or-noise verdict report.

These tests are the claim that ``docs/BAB_SIGNAL_OR_NOISE.md`` publishes only
numbers that exist in the committed P21 JSON artifacts
(``research_state/bab_p21/{universe,significance,rank_eval,cost_surface}.json``).
They never import ``scripts`` or ``strategies`` and never call a ``build_*``
harness: every table in the report is re-rendered from JSON by the renderers
below and compared byte-for-byte with the checked-in markdown.

A hand-typed number, a stale table, a market-profitability claim, a planted
recovery quoted as market alpha, or a null result published as a finding fails
the suite.
"""

from __future__ import annotations

import ast
import json
import re
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_DIR = REPO_ROOT / "research_state/bab_p21"
REPORT_PATH = REPO_ROOT / "docs/BAB_SIGNAL_OR_NOISE.md"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)
NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ISO_DATE = r"\d{4}-\d{2}-\d{2}"

SOURCES = ("universe.json", "significance.json", "rank_eval.json", "cost_surface.json")
COMPONENTS = ("linear_transaction_cost", "borrow_funding", "notional_slippage")


# --------------------------------------------------------------------------- #
# Loading (JSON only -- no harness build_* calls)
# --------------------------------------------------------------------------- #
def _load(name: str) -> dict:
    return json.loads((RESEARCH_DIR / f"{name}.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def universe() -> dict:
    return _load("universe")


@pytest.fixture(scope="module")
def significance() -> dict:
    return _load("significance")


@pytest.fixture(scope="module")
def rank_eval() -> dict:
    return _load("rank_eval")


@pytest.fixture(scope="module")
def cost_surface() -> dict:
    return _load("cost_surface")


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


def provenance_table(universe, significance) -> tuple[list[str], list[dict]]:
    prov = universe["provenance"]
    sig_prov = significance["provenance"]
    rows = [
        {"Fact": "Universe schema", "Value": universe["schema"]},
        {"Fact": "Universe seed", "Value": prov["seed"]},
        {"Fact": "Significance seed", "Value": sig_prov["seed"]},
        {"Fact": "Assets", "Value": prov["assets"]},
        {"Fact": "Return rows", "Value": prov["return_rows"]},
        {"Fact": "Trading days", "Value": prov["trading_days"]},
        {"Fact": "Benchmark", "Value": prov["benchmark"]},
        {"Fact": "Alpha exponent", "Value": prov["alpha_exponent"]},
        {
            "Fact": "Planted alpha spread (annual)",
            "Value": prov["planted_alpha_spread_annual"],
        },
        {"Fact": "Idiosyncratic vol min", "Value": prov["idio_vol_min"]},
        {"Fact": "Idiosyncratic vol max", "Value": prov["idio_vol_max"]},
        {"Fact": "Beta min", "Value": prov["beta_min"]},
        {"Fact": "Beta max", "Value": prov["beta_max"]},
        {
            "Fact": "Planted panel sha256",
            "Value": "`" + universe["panels"]["planted"]["sha256"] + "`",
        },
        {
            "Fact": "Null panel sha256",
            "Value": "`" + universe["panels"]["null"]["sha256"] + "`",
        },
        {"Fact": "Bootstrap resamples", "Value": sig_prov["n_resamples"]},
        {"Fact": "Bootstrap block length", "Value": sig_prov["block_length"]},
        {"Fact": "Nominal slack", "Value": sig_prov["nominal_slack"]},
        {"Fact": "Deflation trials", "Value": sig_prov["n_trials"]},
        {"Fact": "Synthetic", "Value": prov["synthetic"]},
    ]
    return ["Fact", "Value"], rows


def recovery_table(rank_eval) -> tuple[list[str], list[dict]]:
    columns = [
        "variant",
        "weighting",
        "active_rows",
        "total_rows",
        "gross_mean_active",
        "recovery_mean",
        "recovery_frac_positive",
        "min_leg_beta",
        "gross_max",
        "beta_exposure_max",
        "dollar_imbalance_max",
    ]
    rows = [{column: book[column] for column in columns} for book in rank_eval["books"]]
    return columns, rows


def significance_table(significance) -> tuple[list[str], list[dict]]:
    columns = [
        "variant",
        "weighting",
        "oos_sharpe",
        "sharpe_bootstrap_mean",
        "sharpe_bootstrap_p05",
        "sharpe_bootstrap_p95",
        "p_value",
        "ci_excludes_zero",
        "significant",
        "n_resamples",
        "dsr",
        "critical_sharpe",
        "dsr_p_value",
    ]
    rows = [{column: book[column] for column in columns} for book in significance["books"]]
    return columns, rows


def cost_table(cost_surface) -> tuple[list[str], list[dict]]:
    columns = [
        "variant",
        "weighting",
        "active_rows",
        "gross_sharpe",
        "gross_turnover_mean",
        "costed_sharpe_linear_tc_max",
        "costed_sharpe_borrow_max",
        "costed_sharpe_slippage_max",
        "monotone_linear_tc",
        "monotone_borrow",
        "monotone_slippage",
    ]
    rows = []
    for book in cost_surface["books"]:
        rows.append(
            {
                "variant": book["variant"],
                "weighting": book["weighting"],
                "active_rows": book["active_rows"],
                "gross_sharpe": book["gross_sharpe"],
                "gross_turnover_mean": book["gross_turnover_mean"],
                "costed_sharpe_linear_tc_max": book["surfaces"]["linear_transaction_cost"][
                    -1
                ]["costed_sharpe"],
                "costed_sharpe_borrow_max": book["surfaces"]["borrow_funding"][-1][
                    "costed_sharpe"
                ],
                "costed_sharpe_slippage_max": book["surfaces"]["notional_slippage"][-1][
                    "costed_sharpe"
                ],
                "monotone_linear_tc": book["monotonicity"]["linear_transaction_cost"],
                "monotone_borrow": book["monotonicity"]["borrow_funding"],
                "monotone_slippage": book["monotonicity"]["notional_slippage"],
            }
        )
    return columns, rows


def verdict_basis_table(significance, rank_eval) -> tuple[list[str], list[dict]]:
    sig_prov = significance["provenance"]
    rows = [
        {"Fact": "Null calibrated", "Value": sig_prov["null_calibrated"]},
        {"Fact": "Planted detected", "Value": sig_prov["planted_detected"]},
        {"Fact": "Null max one-sided p-value", "Value": sig_prov["null_max_p_value"]},
        {"Fact": "Nominal slack", "Value": sig_prov["nominal_slack"]},
        {
            "Fact": "Null equal p-value",
            "Value": _book(significance["books"], "null", "equal")["p_value"],
        },
        {
            "Fact": "Null rank p-value",
            "Value": _book(significance["books"], "null", "rank")["p_value"],
        },
        {
            "Fact": "Planted equal p-value",
            "Value": _book(significance["books"], "planted", "equal")["p_value"],
        },
        {
            "Fact": "Planted rank p-value",
            "Value": _book(significance["books"], "planted", "rank")["p_value"],
        },
        {
            "Fact": "Planted recovery equal",
            "Value": _book(rank_eval["books"], "planted", "equal")["recovery_mean"],
        },
        {
            "Fact": "Planted recovery rank",
            "Value": _book(rank_eval["books"], "planted", "rank")["recovery_mean"],
        },
        {
            "Fact": "Null recovery equal",
            "Value": _book(rank_eval["books"], "null", "equal")["recovery_mean"],
        },
        {
            "Fact": "Null recovery rank",
            "Value": _book(rank_eval["books"], "null", "rank")["recovery_mean"],
        },
    ]
    return ["Fact", "Value"], rows


TABLE_BUILDERS = {
    "provenance": provenance_table,
    "recovery": recovery_table,
    "significance": significance_table,
    "cost": cost_table,
    "verdict_basis": verdict_basis_table,
}


def _built(name: str, universe, significance, rank_eval, cost_surface) -> list[str]:
    columns, rows = TABLE_BUILDERS[name](
        **{
            "provenance": {"universe": universe, "significance": significance},
            "recovery": {"rank_eval": rank_eval},
            "significance": {"significance": significance},
            "cost": {"cost_surface": cost_surface},
            "verdict_basis": {"significance": significance, "rank_eval": rank_eval},
        }[name]
    )
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
    universe, significance, rank_eval, cost_surface, report
) -> None:
    allowed = set()
    for payload in (universe, significance, rank_eval, cost_surface):
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
    assert published, "report publishes no numeric table cells"
    assert unmatched == [], f"published numbers absent from JSON: {sorted(set(unmatched))}"
    assert len(published) >= 100, "report publishes too few machine-checked numbers"


def test_tables_are_byte_identical_to_the_json_renderers(
    universe, significance, rank_eval, cost_surface, report
) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLE_BUILDERS), (
        f"table anchors differ: {sorted(published)}"
    )
    for name in TABLE_BUILDERS:
        expected = "\n".join(
            _built(name, universe, significance, rank_eval, cost_surface)
        )
        assert published[name] == expected, f"table {name} drifted from its JSON artifact"


def test_prose_does_not_quote_unbacked_numbers(
    universe, significance, rank_eval, cost_surface, report
) -> None:
    allowed = set()
    for payload in (universe, significance, rank_eval, cost_surface):
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
# 2. The verdict is explicit and machine-backed
# --------------------------------------------------------------------------- #
def test_report_states_an_explicit_signal_verdict(significance, report) -> None:
    lowered = _flat(report)
    assert "verdict" in lowered
    assert "signal" in lowered
    assert "noise" in lowered
    prov = significance["provenance"]
    assert prov["null_calibrated"] is True
    assert prov["planted_detected"] is True
    assert "null calibrated" in lowered
    assert "planted detected" in lowered
    null_books = [b for b in significance["books"] if b["variant"] == "null"]
    planted_books = [b for b in significance["books"] if b["variant"] == "planted"]
    assert null_books and planted_books
    for book in null_books:
        assert book["significant"] is False
        assert book["p_value"] >= prov["nominal_slack"]
    for book in planted_books:
        assert book["significant"] is True
        assert book["p_value"] < prov["nominal_slack"]


def test_report_labels_planted_recovery_as_controlled_synthetic(report) -> None:
    lowered = _flat(report)
    assert "controlled synthetic" in lowered
    assert "not market evidence" in lowered
    assert "not real market data" in lowered
    assert "never market alpha" in lowered


def test_report_refuses_a_market_go(report) -> None:
    lowered = _flat(report)
    assert "no-go" in lowered or "no go" in lowered
    assert "not a go" in lowered or "no-go for market" in lowered
    assert "not a demonstrated profitable strategy" in lowered
    assert "no demonstrated real-world profitability" in lowered


def test_report_states_null_results_are_not_findings(significance, report) -> None:
    lowered = _flat(report)
    assert "not significant" in lowered
    assert "bug" in lowered
    for book in significance["books"]:
        if book["variant"] == "null":
            assert book["ci_excludes_zero"] is False


# --------------------------------------------------------------------------- #
# 3. Recovery and cost facts are internally consistent
# --------------------------------------------------------------------------- #
def test_planted_recovery_positive_and_null_exactly_zero(rank_eval) -> None:
    for book in rank_eval["books"]:
        if book["variant"] == "planted":
            assert book["recovery_mean"] > 0.0
            assert book["active_rows"] > 0
        else:
            assert book["recovery_mean"] == 0.0
            assert book["recovery_frac_positive"] == 0.0


def test_cost_surface_books_are_monotone_and_uncensored(cost_surface) -> None:
    for book in cost_surface["books"]:
        assert book["censored"] is False
        assert book["censor_reason"] is None
        for component in COMPONENTS:
            assert book["monotonicity"][component] is True
            sharpes = [row["costed_sharpe"] for row in book["surfaces"][component]]
            assert all(value is not None for value in sharpes)
            assert all(
                current <= previous + 1e-12
                for previous, current in zip(sharpes, sharpes[1:])
            ), f"{book['variant']}/{book['weighting']}/{component} costed Sharpe rose"


def test_panel_shas_agree_across_artifacts(
    universe, significance, rank_eval, cost_surface
) -> None:
    for variant in ("planted", "null"):
        expected = universe["panels"][variant]["sha256"]
        assert significance["provenance"]["panel_sha256"][variant] == expected
        assert rank_eval["provenance"]["panel_sha256"][variant] == expected
        assert cost_surface["provenance"]["panel_sha256"][variant] == expected
        assert expected in universe["panels"][variant]["sha256"]


# --------------------------------------------------------------------------- #
# 4. The test itself never re-runs a harness
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
    for name in ("universe", "significance", "rank_eval", "cost_surface"):
        _load(name)
    REPORT_PATH.read_text(encoding="utf-8")
    assert time.perf_counter() - start < 2.0


def test_report_covers_all_required_sections(report) -> None:
    headings = [line for line in report.splitlines() if line.startswith("## ")]
    lowered = " ".join(headings).lower()
    for required in (
        "provenance",
        "recovery",
        "significance",
        "cost",
        "verdict",
        "does not prove",
    ):
        assert required in lowered, f"missing section: {required}"
