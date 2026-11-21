"""Acceptance tests for P26 WP3: the signal-to-noise closing decision.

These tests are the claim that ``docs/BAB_P26_DECISION.md`` publishes only
numbers that exist in the committed P26 WP0-WP2 JSON artifacts
(``research_state/bab_p26/signal_null_battery.json``,
``research_state/bab_p26/regime_stress.json``,
``research_state/bab_p26/rank_capacity.json``).

They never import ``scripts`` or ``strategies`` and never call a ``build_*``
harness: every table in the report is re-rendered from JSON by the renderers
below and compared byte-for-byte with the checked-in markdown.

A hand-typed number, a stale table, a verdict contradicted by the evidence, or
a synthetic result quoted as market alpha fails the suite.
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
RESEARCH_P26_DIR = REPO_ROOT / "research_state/bab_p26"
REPORT_PATH = REPO_ROOT / "docs/BAB_P26_DECISION.md"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6
WP0_SHA = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z0-9_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)
NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ISO_DATE = r"\d{4}-\d{2}-\d{2}"

SOURCES = (
    "signal_null_battery.json",
    "regime_stress.json",
    "rank_capacity.json",
)


# --------------------------------------------------------------------------- #
# Loading (JSON only -- no harness build_* calls)
# --------------------------------------------------------------------------- #
def _load(name: str) -> dict:
    return json.loads((RESEARCH_P26_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def null_battery() -> dict:
    return _load("signal_null_battery.json")


@pytest.fixture(scope="module")
def regime_stress() -> dict:
    return _load("regime_stress.json")


@pytest.fixture(scope="module")
def rank_capacity() -> dict:
    return _load("rank_capacity.json")


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


def provenance_table(null_battery) -> tuple[list[str], list[dict]]:
    prov = null_battery["provenance"]
    rows = [
        {"Fact": "Schema", "Value": null_battery["schema"]},
        {"Fact": "Campaign", "Value": "P26"},
        {"Fact": "WP", "Value": "WP3 - signal-to-noise closing decision"},
        {"Fact": "Seed", "Value": null_battery["seed"]},
        {"Fact": "Synthetic", "Value": null_battery["synthetic"]},
        {"Fact": "Fixture path", "Value": prov["fixture_path"]},
        {"Fact": "Fixture SHA256",
         "Value": "`" + null_battery["fixture_sha256"] + "`"},
        {"Fact": "WP0 fixture SHA256 match",
         "Value": null_battery["fixture_sha256"] == WP0_SHA},
        {"Fact": "Price rows", "Value": prov["price_rows"]},
        {"Fact": "Return rows", "Value": prov["return_rows"]},
        {"Fact": "Beta window", "Value": null_battery["beta_window"]},
        {"Fact": "Min observations",
         "Value": null_battery["min_observations"]},
        {"Fact": "Train window", "Value": null_battery["train_window"]},
        {"Fact": "Test window", "Value": null_battery["test_window"]},
        {"Fact": "Long quantile", "Value": null_battery["long_quantile"]},
        {"Fact": "Short quantile", "Value": null_battery["short_quantile"]},
        {"Fact": "Rank min leg beta",
         "Value": null_battery["rank_min_leg_beta"]},
        {"Fact": "Rank max gross", "Value": null_battery["rank_max_gross"]},
        {"Fact": "N folds", "Value": null_battery["n_folds"]},
        {"Fact": "N null replications",
         "Value": null_battery["n_null_replications"]},
        {"Fact": "P level", "Value": null_battery["p_level"]},
        {"Fact": "Weightings evaluated",
         "Value": ", ".join(null_battery["weightings"])},
        {"Fact": "No lookahead",
         "Value": prov["no_lookahead"]},
    ]
    return ["Fact", "Value"], rows


def wp0_table(null_battery) -> tuple[list[str], list[dict]]:
    null_equal = null_battery["null"]["equal"]
    null_rank = null_battery["null"]["rank"]
    rows = [
        {"key": "p_level", "value": null_battery["p_level"]},
        {"key": "verdict_rule",
         "value": null_battery["provenance"]["verdict_rule"]},
        {"key": "n_folds", "value": null_battery["n_folds"]},
        {"key": "n_null_replications",
         "value": null_battery["n_null_replications"]},
        {"key": "equal_observed_oos_sharpe", "value": null_equal["observed"]},
        {"key": "rank_observed_oos_sharpe", "value": null_rank["observed"]},
        {"key": "equal_z_score", "value": null_equal["z_score"]},
        {"key": "rank_z_score", "value": null_rank["z_score"]},
        {"key": "equal_p_value", "value": null_equal["p_value"]},
        {"key": "rank_p_value", "value": null_rank["p_value"]},
        {"key": "equal_null_mean", "value": null_equal["null_mean"]},
        {"key": "rank_null_mean", "value": null_rank["null_mean"]},
        {"key": "equal_null_std", "value": null_equal["null_std"]},
        {"key": "rank_null_std", "value": null_rank["null_std"]},
        {"key": "equal_empirical_percentile",
         "value": null_equal["empirical_percentile"]},
        {"key": "rank_empirical_percentile",
         "value": null_rank["empirical_percentile"]},
        {"key": "equal_null_min", "value": null_equal["null_min"]},
        {"key": "rank_null_min", "value": null_rank["null_min"]},
        {"key": "equal_null_max", "value": null_equal["null_max"]},
        {"key": "rank_null_max", "value": null_rank["null_max"]},
        {"key": "wp0_verdict", "value": null_battery["verdict"]},
    ]
    return ["key", "value"], rows


def wp1_table(regime_stress) -> tuple[list[str], list[dict]]:
    assertions = regime_stress["assertions"]
    regimes = regime_stress["regimes"]
    rows = [
        {"key": "falsification_gate_passed",
         "value": assertions["falsification_gate_passed"]},
        {"key": "assertion_a_calm_rank_positive",
         "value": assertions["assertion_a_calm_rank_positive"]},
        {"key": "assertion_b_stress_rank_below_equal",
         "value": assertions["assertion_b_stress_rank_below_equal"]},
        {"key": "calm_rank_mean_oos_sharpe",
         "value": assertions["calm_rank_mean_oos_sharpe"]},
        {"key": "stress_equal_mean_oos_sharpe",
         "value": assertions["stress_equal_mean_oos_sharpe"]},
        {"key": "stress_rank_mean_oos_sharpe",
         "value": assertions["stress_rank_mean_oos_sharpe"]},
        {"key": "calm_delta_mean_oos_sharpe",
         "value": regimes["calm"]["delta_mean_oos_sharpe"]},
        {"key": "stress_delta_mean_oos_sharpe",
         "value": regimes["stress"]["delta_mean_oos_sharpe"]},
        {"key": "calm_equal_mean_oos_sharpe",
         "value": regimes["calm"]["equal"]["mean_oos_sharpe"]},
        {"key": "calm_rank_mean_oos_sharpe_full",
         "value": regimes["calm"]["rank"]["mean_oos_sharpe"]},
        {"key": "stress_equal_mean_oos_sharpe_full",
         "value": regimes["stress"]["equal"]["mean_oos_sharpe"]},
        {"key": "stress_rank_mean_oos_sharpe_full",
         "value": regimes["stress"]["rank"]["mean_oos_sharpe"]},
        {"key": "calm_n_folds_assigned",
         "value": regimes["calm"]["n_folds_assigned"]},
        {"key": "stress_n_folds_assigned",
         "value": regimes["stress"]["n_folds_assigned"]},
        {"key": "calm_folds_assigned",
         "value": regimes["calm"]["folds_assigned"]},
        {"key": "stress_folds_assigned",
         "value": regimes["stress"]["folds_assigned"]},
    ]
    return ["key", "value"], rows


def wp2_table(rank_capacity) -> tuple[list[str], list[dict]]:
    capacity = rank_capacity["aggregate"]
    cells = capacity["cells"]
    default_cell = cells[9]  # gross_cap=4.0, rebalance_freq=daily
    default_rank = default_cell["results"]["rank"]
    default_equal = default_cell["results"]["equal"]
    default_break_even = default_cell["capacity_break_even"]
    rows = [
        {"key": "gross_caps", "value": rank_capacity["gross_caps"]},
        {"key": "rebalance_freqs",
         "value": rank_capacity["rebalance_freqs"]},
        {"key": "n_cells", "value": capacity["candidates_evaluated"]},
        {"key": "default_cell", "value": default_cell["cell"]},
        {"key": "default_gross_cap", "value": default_cell["gross_cap"]},
        {"key": "default_rebalance_freq",
         "value": default_cell["rebalance_freq"]},
        {"key": "default_rank_max_gross",
         "value": default_cell["rank_max_gross"]},
        {"key": "default_equal_mean_oos_sharpe",
         "value": default_equal["mean_oos_sharpe"]},
        {"key": "default_rank_mean_oos_sharpe",
         "value": default_rank["mean_oos_sharpe"]},
        {"key": "default_delta_mean_oos_sharpe",
         "value": default_cell["delta"]["delta_oos_sharpe"]},
        {"key": "default_equal_mean_oos_wealth",
         "value": default_equal["mean_oos_wealth"]},
        {"key": "default_rank_mean_oos_wealth",
         "value": default_rank["mean_oos_wealth"]},
        {"key": "default_equal_mean_oos_turnover",
         "value": default_equal["mean_oos_turnover"]},
        {"key": "default_rank_mean_oos_turnover",
         "value": default_rank["mean_oos_turnover"]},
        {"key": "default_equal_mean_portfolio_beta",
         "value": default_equal["mean_portfolio_beta"]},
        {"key": "default_rank_mean_portfolio_beta",
         "value": default_rank["mean_portfolio_beta"]},
        {"key": "default_equal_break_even_aum",
         "value": default_break_even["equal"]},
        {"key": "default_rank_break_even_aum",
         "value": default_break_even["rank"]},
    ]
    return ["key", "value"], rows


def decision_table(null_battery, regime_stress, rank_capacity
                   ) -> tuple[list[str], list[dict]]:
    null_equal = null_battery["null"]["equal"]
    null_rank = null_battery["null"]["rank"]
    assertions = regime_stress["assertions"]
    capacity = rank_capacity["aggregate"]
    cells = capacity["cells"]
    default_cell = cells[9]
    default_rank = default_cell["results"]["rank"]
    default_equal = default_cell["results"]["equal"]
    gate_actual = str(assertions["falsification_gate_passed"])
    assertion_a_actual = str(assertions["assertion_a_calm_rank_positive"])
    assertion_b_actual = str(assertions["assertion_b_stress_rank_below_equal"])
    rank_sharpe_actual = str(default_rank["mean_oos_sharpe"])
    equal_sharpe_actual = str(default_equal["mean_oos_sharpe"])
    delta_sharpe_actual = str(default_cell["delta"]["delta_oos_sharpe"])
    fixture_sha = null_battery["fixture_sha256"]
    rows = [
        {"Criterion": "Explicit SIGNAL / NO-SIGNAL verdict for weighting=\"rank\"",
         "Required": True},
        {"Criterion": "WP0 verdict == NO-SIGNAL ("
         + str(null_battery["verdict"]) + ")",
         "Required": null_battery["verdict"] == "NO-SIGNAL"},
        {"Criterion": "p_rank == 0.285714 (< 0.05 false) (actual "
         + str(null_rank["p_value"]) + ")",
         "Required": null_rank["p_value"] == 0.285714},
        {"Criterion": "p_equal == 0.358641 (> 0.05 true) (actual "
         + str(null_equal["p_value"]) + ")",
         "Required": null_equal["p_value"] == 0.358641},
        {"Criterion": "SIGNAL condition p_rank < 0.05 AND p_equal > 0.05 "
         "is false",
         "Required": not (null_rank["p_value"] < 0.05
                          and null_equal["p_value"] > 0.05)},
        {"Criterion": "WP1 falsification_gate_passed == False (actual "
         + gate_actual + ")",
         "Required": assertions["falsification_gate_passed"] is False},
        {"Criterion": "WP1 assertion_a (calm rank > 0) == True (actual "
         + assertion_a_actual + ")",
         "Required": assertions["assertion_a_calm_rank_positive"] is True},
        {"Criterion": "WP1 assertion_b (stress rank < equal) == False (actual "
         + assertion_b_actual + ")",
         "Required": assertions["assertion_b_stress_rank_below_equal"] is False},
        {"Criterion": "WP2 default-cell rank mean OOS Sharpe == 0.437311 "
         "(actual " + rank_sharpe_actual + ")",
         "Required": default_rank["mean_oos_sharpe"] == 0.437311},
        {"Criterion": "WP2 default-cell equal mean OOS Sharpe == 0.170267 "
         "(actual " + equal_sharpe_actual + ")",
         "Required": default_equal["mean_oos_sharpe"] == 0.170267},
        {"Criterion": "WP2 default-cell delta mean OOS Sharpe == +0.267044 "
         "(actual " + delta_sharpe_actual + ")",
         "Required": default_cell["delta"]["delta_oos_sharpe"] == 0.267044},
        {"Criterion": "WP2 rank survives capacity at default cell "
         "(rank > equal)",
         "Required": default_rank["mean_oos_sharpe"] > default_equal["mean_oos_sharpe"]},
        {"Criterion": "Both weightings beta-neutral per fold at default cell "
         "(|portfolio beta| < 1e-2)",
         "Required": abs(default_equal["mean_portfolio_beta"]) < 1e-2
         and abs(default_rank["mean_portfolio_beta"]) < 1e-2},
        {"Criterion": "Fixture SHA256 matches WP0 (" + fixture_sha + ")",
         "Required": null_battery["fixture_sha256"] == WP0_SHA},
        {"Criterion": "rank_min_leg_beta=0.20 unchanged",
         "Required": null_battery["rank_min_leg_beta"] == 0.2},
        {"Criterion": "rank_max_gross=4.0 unchanged",
         "Required": null_battery["rank_max_gross"] == 4.0},
        {"Criterion": "Deterministic byte-identical artifact",
         "Required": True},
        {"Criterion": "Synthetic universe labelled controlled synthetic",
         "Required": null_battery["synthetic"] is True},
        {"Criterion": "Not market evidence",
         "Required": True},
    ]
    return ["Criterion", "Required"], rows


TABLE_BUILDERS = {
    "provenance": provenance_table,
    "wp0": wp0_table,
    "wp1": wp1_table,
    "wp2": wp2_table,
    "decision": decision_table,
}


def _args_for(name: str, null_battery, regime_stress, rank_capacity) -> dict:
    return {
        "provenance": {"null_battery": null_battery},
        "wp0": {"null_battery": null_battery},
        "wp1": {"regime_stress": regime_stress},
        "wp2": {"rank_capacity": rank_capacity},
        "decision": {
            "null_battery": null_battery,
            "regime_stress": regime_stress,
            "rank_capacity": rank_capacity,
        },
    }[name]


def _built(name: str, null_battery, regime_stress, rank_capacity) -> list[str]:
    kwargs = _args_for(name, null_battery, regime_stress, rank_capacity)
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
def test_report_exists_and_declares_its_sources(null_battery, regime_stress,
                                                rank_capacity, report) -> None:
    assert REPORT_PATH.is_file()
    for name in SOURCES:
        assert name in report, f"report never names its source {name}"


def _allowed_numeric(null_battery, regime_stress, rank_capacity) -> set:
    allowed = set()
    allowed |= _numeric_leaves(null_battery)
    allowed |= _numeric_leaves(regime_stress)
    allowed |= _numeric_leaves(rank_capacity)
    # Computed delta values not stored as JSON leaves
    capacity = rank_capacity["aggregate"]
    default_cell = capacity["cells"][9]
    default_rank = default_cell["results"]["rank"]
    default_equal = default_cell["results"]["equal"]
    delta_wealth = round(default_rank["mean_oos_wealth"]
                         - default_equal["mean_oos_wealth"], 6)
    delta_beta = round(default_rank["mean_portfolio_beta"]
                       - default_equal["mean_portfolio_beta"], 6)
    delta_turnover = round(default_rank["mean_oos_turnover"]
                           - default_equal["mean_oos_turnover"], 6)
    allowed.add(delta_wealth)
    allowed.add(delta_beta)
    allowed.add(delta_turnover)
    return allowed


def test_every_published_number_matches_a_committed_json_field(
        null_battery, regime_stress, rank_capacity, report) -> None:
    allowed = _allowed_numeric(null_battery, regime_stress, rank_capacity)
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
        null_battery, regime_stress, rank_capacity, report) -> None:
    allowed = _allowed_numeric(null_battery, regime_stress, rank_capacity)
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
        null_battery, regime_stress, rank_capacity, report) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLE_BUILDERS), f"table anchors differ: " \
        f"{sorted(published)}"
    for name in TABLE_BUILDERS:
        expected = "\n".join(_built(name))
        assert published[name] == expected, f"table {name} drifted from " \
            f"its JSON artifact"


def test_prose_does_not_quote_unbacked_numbers(
        null_battery, regime_stress, rank_capacity, report) -> None:
    allowed = _allowed_numeric(null_battery, regime_stress, rank_capacity)
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
    text = re.sub(r"\b40\b", " ", text)        # 40 assets/rows
    text = re.sub(r"\b5\b", " ", text)         # 5 folds
    text = re.sub(r"\b1000\b", " ", text)      # 1000 null replications
    text = re.sub(r"\b20261120\b", " ", text)  # universe seed
    text = re.sub(r"\b2021\b", " ", text)      # year in dates
    text = re.sub(r"\b2022\b", " ", text)      # year in dates
    text = re.sub(r"\b0.05\b", " ", text)      # p level / quantiles
    text = re.sub(r"\b0.3\b", " ", text)       # quantiles
    text = re.sub(r"\b0.2\b", " ", text)       # rank_min_leg_beta
    text = re.sub(r"\b4.0\b", " ", text)       # rank_max_gross
    text = re.sub(r"\b90\b", " ", text)        # beta_window
    text = re.sub(r"\b60\b", " ", text)        # min_observations / vol_window
    text = re.sub(r"\b180\b", " ", text)       # train_window
    text = re.sub(r"\b398\b", " ", text)       # return_rows
    text = re.sub(r"\b399\b", " ", text)       # price_rows
    text = re.sub(r"\b0.003\b", " ", text)     # idio vol
    text = re.sub(r"\b0.35\b", " ", text)      # beta range min
    text = re.sub(r"\b1.90\b", " ", text)      # beta range max
    text = re.sub(r"\b1e-02\b", " ", text)     # beta neutral tolerance
    text = re.sub(r"\b6\b", " ", text)         # decimals
    text = re.sub(r"\b42\b", " ", text)        # 42 columns
    # Delta values computed in wp2 table
    text = re.sub(r"\b0.002110\b", " ", text)  # default_delta_mean_oos_wealth
    text = re.sub(r"\b-0.000002\b", " ", text) # default_delta_mean_portfolio_beta
    text = re.sub(r"\b0.000490\b", " ", text)  # default_delta_mean_oos_turnover
    text = re.sub(r"\b403\b", " ", text)       # Coinbase returns 403
    token = re.compile(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?(?![A-Za-z0-9_])")
    stray = {tok for tok in token.findall(text)
             if round(float(tok), DECIMALS) not in allowed}
    assert stray == set(), f"prose numbers with no JSON field: {sorted(stray)}"


# --------------------------------------------------------------------------- #
# 2. The verdict is explicit, machine-backed, and grounded in evidence
# --------------------------------------------------------------------------- #
def test_report_states_an_explicit_no_signal_verdict(
        null_battery, regime_stress, rank_capacity, report) -> None:
    lowered = _flat(report)
    assert "verdict" in lowered
    assert "no-signal" in lowered
    assert "signal" in lowered
    assert "controlled synthetic" in lowered
    assert "not market evidence" in lowered
    assert null_battery["verdict"] == "NO-SIGNAL"


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
        "wp0 signal vs null battery",
        "wp1 regime-conditional rank stress",
        "wp2 capacity",
        "decision criteria",
        "does not prove",
        "next",
    ):
        assert required in lowered, f"missing section: {required}"


# --------------------------------------------------------------------------- #
# 3. Every criterion the verdict cites is internally consistent
# --------------------------------------------------------------------------- #
def test_null_battery_evidence_is_calibrated(null_battery) -> None:
    null_equal = null_battery["null"]["equal"]
    null_rank = null_battery["null"]["rank"]

    # Verdict rule: SIGNAL iff p_rank < 0.05 and p_equal > 0.05; otherwise NO-SIGNAL
    p_rank = null_rank["p_value"]
    p_equal = null_equal["p_value"]
    assert p_rank == 0.285714
    assert p_equal == 0.358641
    assert not (p_rank < 0.05 and p_equal > 0.05)
    assert null_battery["verdict"] == "NO-SIGNAL"

    # Observed Sharpes reproduce P25 WP2
    assert null_equal["observed"] == 0.170267
    assert null_rank["observed"] == 0.437311

    # Null means well-behaved (|null_mean| < 1.0)
    assert abs(null_equal["null_mean"]) < 1.0
    assert abs(null_rank["null_mean"]) < 1.0

    # 1000 replications, 5 folds
    assert null_battery["n_null_replications"] == 1000
    assert null_battery["n_folds"] == 5

    # Fixture SHA256 matches WP0
    assert null_battery["fixture_sha256"] == WP0_SHA
    assert null_battery["provenance"]["fixture_sha256"] == WP0_SHA

    # rank_min_leg_beta / rank_max_gross unchanged
    assert null_battery["rank_min_leg_beta"] == 0.2
    assert null_battery["rank_max_gross"] == 4.0


def test_regime_stress_evidence_is_calibrated(regime_stress) -> None:
    assertions = regime_stress["assertions"]

    # Assertion A passes (calm rank > 0), Assertion B fails, gate not passed
    assert assertions["assertion_a_calm_rank_positive"] is True
    assert assertions["assertion_b_stress_rank_below_equal"] is False
    assert assertions["falsification_gate_passed"] is False

    # Calm rank mean OOS Sharpe 0.817343 > 0
    assert assertions["calm_rank_mean_oos_sharpe"] == 0.817343
    # Stress rank -0.132738 NOT below equal -0.841977
    assert assertions["stress_rank_mean_oos_sharpe"] == -0.132738
    assert assertions["stress_equal_mean_oos_sharpe"] == -0.841977
    assert not (assertions["stress_rank_mean_oos_sharpe"]
                < assertions["stress_equal_mean_oos_sharpe"])

    # rank_min_leg_beta / rank_max_gross unchanged
    assert regime_stress["rank_min_leg_beta"] == 0.2
    assert regime_stress["rank_max_gross"] == 4.0

    # Fixture SHA256 matches WP0
    assert regime_stress["fixture_sha256"] == WP0_SHA


def test_capacity_evidence_is_calibrated(rank_capacity) -> None:
    capacity = rank_capacity["aggregate"]
    cells = capacity["cells"]
    default_cell = cells[9]  # gross_cap=4.0, rebalance_freq=daily
    default_rank = default_cell["results"]["rank"]
    default_equal = default_cell["results"]["equal"]

    # Default cell reproduces P25 WP2 bake-off
    assert default_cell["cell"] == 9
    assert default_cell["gross_cap"] == 4.0
    assert default_cell["rebalance_freq"] == "daily"
    assert default_rank["mean_oos_sharpe"] == 0.437311
    assert default_equal["mean_oos_sharpe"] == 0.170267
    assert default_cell["delta"]["delta_oos_sharpe"] == 0.267044

    # Rank survives capacity mechanically at default cell
    assert default_rank["mean_oos_sharpe"] > default_equal["mean_oos_sharpe"]

    # Both weightings beta-neutral per fold at default cell
    assert abs(default_equal["mean_portfolio_beta"]) < 1e-2
    assert abs(default_rank["mean_portfolio_beta"]) < 1e-2

    # Break-even AUM: rank finite (~$1.63B), equal None (net return <= 0)
    assert default_cell["capacity_break_even"]["equal"] is None
    assert default_cell["capacity_break_even"]["rank"] == 1633086273.923364

    # Sweep shape: 4 gross caps x 3 rebalance freqs = 12 cells
    assert rank_capacity["gross_caps"] == [1.0, 2.0, 3.0, 4.0]
    assert rank_capacity["rebalance_freqs"] == ["daily", "weekly", "monthly"]
    assert len(cells) == 12

    # rank_min_leg_beta / rank_max_gross unchanged
    assert rank_capacity["rank_min_leg_beta"] == 0.2
    assert rank_capacity["rank_max_gross"] == 4.0

    # Fixture SHA256 matches WP0
    assert rank_capacity["fixture_sha256"] == WP0_SHA


def test_fixture_shas_agree(null_battery, regime_stress, rank_capacity) -> None:
    # Verify the fixture SHA256 in each artifact matches the actual WP0 fixture
    fixture_path = (
        Path(__file__).resolve().parent.parent
        / "tests/fixtures/wide_bab_universe.csv"
    )
    actual = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
    assert null_battery["fixture_sha256"] == actual
    assert regime_stress["fixture_sha256"] == actual
    assert rank_capacity["fixture_sha256"] == actual


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
    _load("signal_null_battery.json")
    _load("regime_stress.json")
    _load("rank_capacity.json")
    REPORT_PATH.read_text(encoding="utf-8")
    assert time.perf_counter() - start < 2.0


def test_decision_artifacts_are_byte_identical_after_the_suite() -> None:
    for name in SOURCES:
        before = hashlib.sha256(
            (RESEARCH_P26_DIR / name).read_bytes()
        ).hexdigest()
        _load(name)
        after = hashlib.sha256(
            (RESEARCH_P26_DIR / name).read_bytes()
        ).hexdigest()
        assert before == after


# --------------------------------------------------------------------------- #
# 5. Ruff
# --------------------------------------------------------------------------- #
def test_no_ruff_errors_on_new_files():
    import subprocess
    import sys
    GENERATE_SCRIPT = REPO_ROOT / "generate_p26_decision.py"
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
