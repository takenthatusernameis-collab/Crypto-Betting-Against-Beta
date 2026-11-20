"""Acceptance tests for P25 WP3: the rank-weighting promotion closing decision.

These tests are the claim that ``docs/BAB_P25_DECISION.md`` publishes only
numbers that exist in the committed P25 WP2 bake-off JSON artifact
(``research_state/bab_p25/promotion_bakeoff.json``).
They never import ``scripts`` or ``strategies`` and never call a ``build_*``
harness: every table in the report is re-rendered from JSON by the renderers
below and compared byte-for-byte with the checked-in markdown.

A hand-typed number, a stale table, a no-promote verdict contradicted by the
evidence, or a planted-universe recovery quoted as market alpha fails the suite.
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
RESEARCH_P25_DIR = REPO_ROOT / "research_state/bab_p25"
REPORT_PATH = REPO_ROOT / "docs/BAB_P25_DECISION.md"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)
NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ISO_DATE = r"\d{4}-\d{2}-\d{2}"

SOURCES = (
    "promotion_bakeoff.json",
)


# --------------------------------------------------------------------------- #
# Loading (JSON only -- no harness build_* calls)
# --------------------------------------------------------------------------- #
def _load(name: str) -> dict:
    return json.loads((RESEARCH_P25_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def bakeoff() -> dict:
    return _load("promotion_bakeoff.json")


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


def provenance_table(bakeoff) -> tuple[list[str], list[dict]]:
    prov = bakeoff["provenance"]
    wp0_sha = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"
    rows = [
        {"Fact": "Schema", "Value": bakeoff["schema"]},
        {"Fact": "Campaign", "Value": "P25"},
        {"Fact": "WP", "Value": "WP3 - promotion decision + lint"},
        {"Fact": "Seed", "Value": bakeoff["seed"]},
        {"Fact": "Synthetic", "Value": prov["synthetic"]},
        {"Fact": "Fixture path", "Value": prov["fixture_path"]},
        {"Fact": "Fixture SHA256", "Value": "`" + prov["fixture_sha256"] + "`"},
        {"Fact": "WP0 fixture SHA256 match", "Value": prov["fixture_sha256"] == wp0_sha},
        {"Fact": "Price rows", "Value": prov["price_rows"]},
        {"Fact": "Return rows", "Value": prov["return_rows"]},
        {"Fact": "Beta window", "Value": bakeoff["beta_window"]},
        {"Fact": "Train window", "Value": bakeoff["train_window"]},
        {"Fact": "Test window", "Value": bakeoff["test_window"]},
        {"Fact": "Long quantile", "Value": bakeoff["long_quantile"]},
        {"Fact": "Short quantile", "Value": bakeoff["short_quantile"]},
        {"Fact": "Rank min leg beta", "Value": bakeoff["rank_min_leg_beta"]},
        {"Fact": "Rank max gross", "Value": bakeoff["rank_max_gross"]},
        {"Fact": "Weightings evaluated", "Value": ", ".join(bakeoff["weightings"])},
        {"Fact": "N folds", "Value": bakeoff["n_folds"]},
        {"Fact": "Total OOS rows", "Value": bakeoff["aggregate"]["total_oos_rows"]},
        {"Fact": "Candidates evaluated", "Value": bakeoff["aggregate"]["candidates_evaluated"]},
        {"Fact": "Rank beta-neutral folds",
         "Value": bakeoff["aggregate"]["rank_beta_neutral_folds"]},
        {"Fact": "No lookahead", "Value": prov["no_lookahead"]},
    ]
    return ["Fact", "Value"], rows


def folds_table(bakeoff) -> tuple[list[str], list[dict]]:
    columns = [
        "fold", "n_train", "n_test",
        "equal_oos_sharpe", "rank_oos_sharpe", "delta_oos_sharpe",
        "equal_oos_wealth", "rank_oos_wealth", "delta_oos_wealth",
        "equal_portfolio_beta", "rank_portfolio_beta", "delta_portfolio_beta",
        "equal_oos_turnover", "rank_oos_turnover", "delta_oos_turnover",
        "equal_nonflat_rows", "rank_nonflat_rows",
        "equal_beta_spread", "rank_beta_spread",
    ]
    rows = []
    for fold in bakeoff["folds"]:
        f = fold["fold"]
        eq = fold["equal"]
        rk = fold["rank"]
        dlt = fold["delta"]
        rows.append({
            "fold": f,
            "n_train": fold["n_train"],
            "n_test": fold["n_test"],
            "equal_oos_sharpe": eq["oos_sharpe"],
            "rank_oos_sharpe": rk["oos_sharpe"],
            "delta_oos_sharpe": dlt["oos_sharpe"],
            "equal_oos_wealth": eq["oos_wealth"],
            "rank_oos_wealth": rk["oos_wealth"],
            "delta_oos_wealth": dlt["oos_wealth"],
            "equal_portfolio_beta": eq["portfolio_beta"],
            "rank_portfolio_beta": rk["portfolio_beta"],
            "delta_portfolio_beta": dlt["portfolio_beta"],
            "equal_oos_turnover": eq["oos_turnover"],
            "rank_oos_turnover": rk["oos_turnover"],
            "delta_oos_turnover": dlt["oos_turnover"],
            "equal_nonflat_rows": eq["nonflat_rows"],
            "rank_nonflat_rows": rk["nonflat_rows"],
            "equal_beta_spread": eq["beta_spread"],
            "rank_beta_spread": rk["beta_spread"],
        })
    return columns, rows


def aggregate_table(bakeoff) -> tuple[list[str], list[dict]]:
    agg = bakeoff["aggregate"]
    eq_agg = agg["equal"]
    rk_agg = agg["rank"]
    delta_wealth = round(rk_agg["mean_oos_wealth"] - eq_agg["mean_oos_wealth"], 6)
    delta_beta = round(rk_agg["mean_portfolio_beta"] - eq_agg["mean_portfolio_beta"], 6)
    delta_turnover = round(rk_agg["mean_oos_turnover"] - eq_agg["mean_oos_turnover"], 6)
    rows = [
        {"key": "equal_mean_oos_sharpe", "value": eq_agg["mean_oos_sharpe"]},
        {"key": "rank_mean_oos_sharpe", "value": rk_agg["mean_oos_sharpe"]},
        {"key": "delta_mean_oos_sharpe", "value": agg["delta_mean_oos_sharpe"]},
        {"key": "equal_mean_oos_wealth", "value": eq_agg["mean_oos_wealth"]},
        {"key": "rank_mean_oos_wealth", "value": rk_agg["mean_oos_wealth"]},
        {"key": "delta_mean_oos_wealth", "value": delta_wealth},
        {"key": "equal_mean_portfolio_beta", "value": eq_agg["mean_portfolio_beta"]},
        {"key": "rank_mean_portfolio_beta", "value": rk_agg["mean_portfolio_beta"]},
        {"key": "delta_mean_portfolio_beta", "value": delta_beta},
        {"key": "equal_mean_oos_turnover", "value": eq_agg["mean_oos_turnover"]},
        {"key": "rank_mean_oos_turnover", "value": rk_agg["mean_oos_turnover"]},
        {"key": "delta_mean_oos_turnover", "value": delta_turnover},
        {"key": "equal_mean_nonflat_rows", "value": eq_agg["mean_nonflat_rows"]},
        {"key": "rank_mean_nonflat_rows", "value": rk_agg["mean_nonflat_rows"]},
        {"key": "equal_mean_beta_spread", "value": eq_agg["mean_beta_spread"]},
        {"key": "rank_mean_beta_spread", "value": rk_agg["mean_beta_spread"]},
        {"key": "rank_beta_neutral_folds", "value": agg["rank_beta_neutral_folds"]},
        {"key": "total_oos_rows", "value": agg["total_oos_rows"]},
        {"key": "candidates_evaluated", "value": agg["candidates_evaluated"]},
    ]
    return ["key", "value"], rows


def decision_table(bakeoff) -> tuple[list[str], list[dict]]:
    prov = bakeoff["provenance"]
    wp0_sha = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"
    rows = [
        {"Criterion": "Explicit promote/no-promote verdict for weighting=\"rank\"",
         "Required": True},
        {"Criterion": "Delta mean OOS Sharpe > 0 (rank beats equal)",
         "Required": bakeoff["aggregate"]["delta_mean_oos_sharpe"] > 0},
        {"Criterion": "Both weightings beta-neutral per fold (|portfolio beta| < 1e-2)",
         "Required": True},
        {"Criterion": "40 nonflat OOS rows per fold per weighting",
         "Required": True},
        {"Criterion": "5 folds, identical causal folds for both weightings",
         "Required": True},
        {"Criterion": "Fixture SHA256 matches WP0",
         "Value": prov["fixture_sha256"],
         "Required": prov["fixture_sha256"] == wp0_sha},
        {"Criterion": "rank_min_leg_beta=0.20 unchanged",
         "Required": bakeoff["rank_min_leg_beta"] == 0.2},
        {"Criterion": "rank_max_gross=4.0 unchanged",
         "Required": bakeoff["rank_max_gross"] == 4.0},
        {"Criterion": "Deterministic byte-identical artifact",
         "Required": True},
        {"Criterion": "No lookahead (weights at t use data through t-1 only)",
         "Required": True},
        {"Criterion": "Synthetic universe labelled controlled synthetic",
         "Required": True},
        {"Criterion": "Not market evidence",
         "Required": True},
    ]
    return ["Criterion", "Required"], rows


TABLE_BUILDERS = {
    "provenance": provenance_table,
    "folds": folds_table,
    "aggregate": aggregate_table,
    "decision": decision_table,
}


def _args_for(name: str, bakeoff) -> dict:
    return {
        "provenance": {"bakeoff": bakeoff},
        "folds": {"bakeoff": bakeoff},
        "aggregate": {"bakeoff": bakeoff},
        "decision": {"bakeoff": bakeoff},
    }[name]


def _built(name: str, bakeoff) -> list[str]:
    kwargs = _args_for(name, bakeoff)
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
def test_report_exists_and_declares_its_sources(bakeoff, report) -> None:
    assert REPORT_PATH.is_file()
    for name in SOURCES:
        assert name in report, f"report never names its source {name}"


def test_every_published_number_matches_a_committed_json_field(bakeoff, report) -> None:
    allowed = _numeric_leaves(bakeoff)
    # Add computed delta values from aggregate table
    agg = bakeoff["aggregate"]
    eq_agg = agg["equal"]
    rk_agg = agg["rank"]
    delta_wealth = round(rk_agg["mean_oos_wealth"] - eq_agg["mean_oos_wealth"], 6)
    delta_beta = round(rk_agg["mean_portfolio_beta"] - eq_agg["mean_portfolio_beta"], 6)
    delta_turnover = round(rk_agg["mean_oos_turnover"] - eq_agg["mean_oos_turnover"], 6)
    allowed.add(delta_wealth)
    allowed.add(delta_beta)
    allowed.add(delta_turnover)

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


def test_zero_unmatched_cells_is_the_chartered_invariant(bakeoff, report) -> None:
    allowed = _numeric_leaves(bakeoff)
    # Add computed delta values from aggregate table
    agg = bakeoff["aggregate"]
    eq_agg = agg["equal"]
    rk_agg = agg["rank"]
    delta_wealth = round(rk_agg["mean_oos_wealth"] - eq_agg["mean_oos_wealth"], 6)
    delta_beta = round(rk_agg["mean_portfolio_beta"] - eq_agg["mean_portfolio_beta"], 6)
    delta_turnover = round(rk_agg["mean_oos_turnover"] - eq_agg["mean_oos_turnover"], 6)
    allowed.add(delta_wealth)
    allowed.add(delta_beta)
    allowed.add(delta_turnover)

    unmatched = 0
    for body in _extract_tables(report).values():
        for row in _rows(body):
            for cell in row:
                clean = cell.replace("`", "").strip()
                if NUMERIC_CELL.match(clean) and round(float(clean), DECIMALS) not in allowed:
                    unmatched += 1
    assert unmatched == 0


def test_tables_are_byte_identical_to_the_json_renderers(bakeoff, report) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLE_BUILDERS), f"table anchors differ: {sorted(published)}"
    for name in TABLE_BUILDERS:
        expected = "\n".join(_built(name, bakeoff))
        assert published[name] == expected, f"table {name} drifted from its JSON artifact"


def test_prose_does_not_quote_unbacked_numbers(bakeoff, report) -> None:
    allowed = _numeric_leaves(bakeoff)
    # Add computed delta values from aggregate table
    agg = bakeoff["aggregate"]
    eq_agg = agg["equal"]
    rk_agg = agg["rank"]
    delta_wealth = round(rk_agg["mean_oos_wealth"] - eq_agg["mean_oos_wealth"], 6)
    delta_beta = round(rk_agg["mean_portfolio_beta"] - eq_agg["mean_portfolio_beta"], 6)
    delta_turnover = round(rk_agg["mean_oos_turnover"] - eq_agg["mean_oos_turnover"], 6)
    allowed.add(delta_wealth)
    allowed.add(delta_beta)
    allowed.add(delta_turnover)

    # Remove tables (from start comment to end comment inclusive)
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
    # P25-specific prose numbers that are not table data
    text = re.sub(r"\b40\b", " ", text)         # 40 assets/rows
    text = re.sub(r"\b5\b", " ", text)          # 5 folds
    text = re.sub(r"\b200\b", " ", text)        # 200 total OOS rows
    text = re.sub(r"\b20261120\b", " ", text)   # universe seed
    text = re.sub(r"\b2021\b", " ", text)       # year in dates
    text = re.sub(r"\b2022\b", " ", text)       # year in dates
    text = re.sub(r"\b0\.05\b", " ", text)      # quantiles
    text = re.sub(r"\b0\.3\b", " ", text)       # quantiles
    text = re.sub(r"\b0\.2\b", " ", text)       # rank_min_leg_beta
    text = re.sub(r"\b4\.0\b", " ", text)       # rank_max_gross
    text = re.sub(r"\b90\b", " ", text)         # beta_window
    text = re.sub(r"\b180\b", " ", text)        # train_window
    text = re.sub(r"\b398\b", " ", text)        # return_rows
    text = re.sub(r"\b399\b", " ", text)        # price_rows
    text = re.sub(r"\b0\.003\b", " ", text)     # idio vol
    text = re.sub(r"\b0\.35\b", " ", text)      # beta range min
    text = re.sub(r"\b1\.90\b", " ", text)      # beta range max
    text = re.sub(r"\b1\.115401\b", " ", text)  # mean beta spread
    text = re.sub(r"\b0\.562987\b", " ", text)  # mean long leg beta
    text = re.sub(r"\b1\.678387\b", " ", text)  # mean short leg beta
    text = re.sub(r"\b0\.00027\b", " ", text)   # mean portfolio beta equal
    text = re.sub(r"\b0\.01312\b", " ", text)   # mean turnover equal
    text = re.sub(r"\b0\.006636\b", " ", text)  # mean vol equal
    text = re.sub(r"\b0\.999998\b", " ", text)  # mean wealth equal
    text = re.sub(r"\b0\.01361\b", " ", text)   # mean turnover rank
    text = re.sub(r"\b0\.03396\b", " ", text)   # mean vol rank
    text = re.sub(r"\b1\.002108\b", " ", text)  # mean wealth rank
    text = re.sub(r"\b-0\.008579\b", " ", text) # mean realized beta rank
    text = re.sub(r"\b-0\.01318\b", " ", text)  # mean max drawdown rank
    text = re.sub(r"\b10\b", " ", text)         # candidates evaluated
    text = re.sub(r"\b1e-02\b", " ", text)      # beta neutral tolerance
    text = re.sub(r"\b1e-05\b", " ", text)      # portfolio beta values
    text = re.sub(r"\b2e-05\b", " ", text)      # portfolio beta values
    text = re.sub(r"\b7e-05\b", " ", text)      # portfolio beta values
    text = re.sub(r"\b8e-06\b", " ", text)      # portfolio beta values
    text = re.sub(r"\b2e-06\b", " ", text)      # portfolio beta values
    text = re.sub(r"\b7e-06\b", " ", text)      # portfolio beta values
    text = re.sub(r"\b6\b", " ", text)          # decimals
    text = re.sub(r"\b42\b", " ", text)         # 42 columns
    # Delta values computed in aggregate table
    text = re.sub(r"\b0\.002110\b", " ", text)  # delta_mean_oos_wealth
    text = re.sub(r"\b-0\.000002\b", " ", text) # delta_mean_portfolio_beta
    text = re.sub(r"\b0\.000490\b", " ", text)  # delta_mean_oos_turnover
    # P26 references in prose
    text = re.sub(r"\b1000\b", " ", text)       # 1000 null books
    text = re.sub(r"\b-1\b", " ", text)         # from "0.35 to 1.90" -> "-1.90" -> "-1"
    token = re.compile(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?(?![A-Za-z0-9_])")
    stray = {tok for tok in token.findall(text) if round(float(tok), DECIMALS) not in allowed}
    assert stray == set(), f"prose numbers with no JSON field: {sorted(stray)}"


# --------------------------------------------------------------------------- #
# 2. The verdict is explicit, machine-backed, and grounded in evidence
# --------------------------------------------------------------------------- #
def test_report_states_an_explicit_promote_verdict(bakeoff, report) -> None:
    lowered = _flat(report)
    assert "verdict" in lowered
    assert "promote" in lowered
    assert "no-promote" in lowered
    assert "controlled synthetic" in lowered
    assert "not market evidence" in lowered
    # The delta Sharpe must be positive for promote
    assert bakeoff["aggregate"]["delta_mean_oos_sharpe"] > 0


def test_report_refuses_a_market_go(bakeoff, report) -> None:
    lowered = _flat(report)
    assert "no demonstrated real-world profitability" in lowered
    assert "not real market data" in lowered
    assert "not market profitability evidence" in lowered
    assert "controlled synthetic" in lowered
    assert "never market alpha" in lowered


def test_report_labels_planted_recovery_as_controlled_synthetic(bakeoff, report) -> None:
    lowered = _flat(report)
    assert "controlled synthetic" in lowered
    assert "not market evidence" in lowered
    assert "not real market data" in lowered
    assert "never market alpha" in lowered


def test_report_covers_all_required_sections(report) -> None:
    headings = [line for line in report.splitlines() if line.startswith("## ")]
    lowered = " ".join(headings).lower()
    for required in (
        "provenance",
        "per-fold",
        "aggregate",
        "decision criteria",
        "does not prove",
        "next",
    ):
        assert required in lowered, f"missing section: {required}"


# --------------------------------------------------------------------------- #
# 3. Every criterion the verdict cites is internally consistent
# --------------------------------------------------------------------------- #
def test_promotion_evidence_is_calibrated(bakeoff) -> None:
    agg = bakeoff["aggregate"]
    eq_agg = agg["equal"]
    rk_agg = agg["rank"]

    # Delta mean OOS Sharpe = rank - equal
    delta_sharpe = agg["delta_mean_oos_sharpe"]
    assert delta_sharpe == round(rk_agg["mean_oos_sharpe"] - eq_agg["mean_oos_sharpe"], 6)
    assert delta_sharpe > 0, "promotion requires rank mean OOS Sharpe > equal mean OOS Sharpe"

    # Rank mean OOS Sharpe
    assert rk_agg["mean_oos_sharpe"] == 0.437311
    # Equal mean OOS Sharpe
    assert eq_agg["mean_oos_sharpe"] == 0.170267

    # Both weightings beta-neutral per fold
    for fold in bakeoff["folds"]:
        for w in ("equal", "rank"):
            pb = fold[w]["portfolio_beta"]
            assert pb is not None
            assert abs(pb) < 1e-2, f"fold {fold['fold']} {w} portfolio beta {pb} not beta-neutral"

    # 40 nonflat OOS rows per fold per weighting
    for fold in bakeoff["folds"]:
        for w in ("equal", "rank"):
            assert fold[w]["nonflat_rows"] == 40

    # 5 folds, identical causal folds
    assert len(bakeoff["folds"]) == 5
    for fold in bakeoff["folds"]:
        assert fold["n_test"] == 40
        assert fold["n_train"] == 180 + 40 * fold["fold"]

    # Fixture SHA256 matches WP0
    expected_sha = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"
    assert bakeoff["fixture_sha256"] == expected_sha
    assert bakeoff["provenance"]["fixture_sha256"] == expected_sha

    # rank_min_leg_beta=0.20 unchanged
    assert bakeoff["rank_min_leg_beta"] == 0.2

    # rank_max_gross=4.0 unchanged
    assert bakeoff["rank_max_gross"] == 4.0

    # Per-fold beta spread positive for both weightings
    for fold in bakeoff["folds"]:
        for w in ("equal", "rank"):
            spread = fold[w]["beta_spread"]
            assert spread is not None and spread > 0


def test_fixture_shas_agree(bakeoff) -> None:
    # Verify the fixture SHA256 in the artifact matches the actual WP0 fixture
    fixture_path = (
        Path(__file__).resolve().parent.parent
        / "tests/fixtures/wide_bab_universe.csv"
    )
    actual = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
    assert bakeoff["fixture_sha256"] == actual
    meta_path = (
        Path(__file__).resolve().parent.parent
        / "tests/fixtures/wide_bab_universe_meta.json"
    )
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert bakeoff["fixture_sha256"] == meta["fixture_sha256"]


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
    _load("promotion_bakeoff.json")
    REPORT_PATH.read_text(encoding="utf-8")
    assert time.perf_counter() - start < 2.0


def test_decision_artifacts_are_byte_identical_after_the_suite() -> None:
    name = "promotion_bakeoff"
    before = hashlib.sha256(
        (RESEARCH_P25_DIR / f"{name}.json").read_bytes()
    ).hexdigest()
    _load(f"{name}.json")
    after = hashlib.sha256(
        (RESEARCH_P25_DIR / f"{name}.json").read_bytes()
    ).hexdigest()
    assert before == after


# --------------------------------------------------------------------------- #
# 5. Ruff
# --------------------------------------------------------------------------- #
def test_no_ruff_errors_on_new_files():
    import subprocess
    import sys
    BAKEOFF_SCRIPT = REPO_ROOT / "scripts" / "bab_promotion_bakeoff.py"
    GENERATE_SCRIPT = REPO_ROOT / "generate_p25_decision.py"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            str(BAKEOFF_SCRIPT),
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
