"""Acceptance tests for P20 WP4: honest reporting + provenance.

These tests are the claim that ``docs/BAB_RESEARCH_REPORT.md`` publishes only
numbers that exist in the committed P20 JSON artifacts
(``research_state/bab_p20/{sweep,walk_forward,breakeven}.json``). They never
import or call a research harness: the report is regenerated from JSON by the
renderers below and compared byte-for-byte with the markdown that is checked
in. A hand-typed number, a stale table, a rank performance claim, or a "zero
break-even" for a null row fails the suite.
"""

from __future__ import annotations

import ast
import json
import re
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_DIR = REPO_ROOT / "research_state/bab_p20"
REPORT_PATH = REPO_ROOT / "docs/BAB_RESEARCH_REPORT.md"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)
NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ISO_DATE = r"\d{4}-\d{2}-\d{2}"

FORBIDDEN_RANK_TOKENS = ("rank_min_leg_beta", "rank_max_gross", "weighting=rank")


# --------------------------------------------------------------------------- #
# Loading (JSON only -- no harness build_* calls)
# --------------------------------------------------------------------------- #
def _load(name: str) -> dict:
    return json.loads((RESEARCH_DIR / f"{name}.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def sweep() -> dict:
    return _load("sweep")


@pytest.fixture(scope="module")
def walk_forward() -> dict:
    return _load("walk_forward")


@pytest.fixture(scope="module")
def breakeven() -> dict:
    return _load("breakeven")


@pytest.fixture(scope="module")
def report() -> str:
    return REPORT_PATH.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Table construction, derived from the committed JSON
# --------------------------------------------------------------------------- #
def _f(value: float) -> str:
    return f"{float(value):.{DECIMALS}f}"


def _cell(value, integer: bool) -> str:
    if value is None:
        return "None"
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "True" if value else "False"
    if integer:
        return str(int(value))
    if isinstance(value, int):
        return str(value)
    return _f(value)


def _render(columns, rows, int_cols=()) -> list[str]:
    lines = ["| " + " | ".join(columns) + " |"]
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    for row in rows:
        cells = [_cell(row[column], column in int_cols) for column in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def provenance_rows(payload: dict) -> tuple[list[str], list[dict], tuple]:
    provenance = payload["provenance"]
    rows = [
        {"Fact": "Fixture path", "Value": f"`{provenance['fixture_path']}`"},
        {"Fact": "Fixture sha256", "Value": f"`{provenance['fixture_sha256']}`"},
        {"Fact": "Price rows", "Value": provenance["price_rows"]},
        {"Fact": "Return rows", "Value": provenance["return_rows"]},
        {"Fact": "First date", "Value": provenance["date_first"]},
        {"Fact": "Last date", "Value": provenance["date_last"]},
        {"Fact": "Seed", "Value": provenance["seed"]},
        {"Fact": "Known gap", "Value": provenance["known_gap"]},
        {"Fact": "All-NaN columns", "Value": ", ".join(provenance["nan_columns"])},
        {"Fact": "Synthetic", "Value": provenance["synthetic"]},
    ]
    return ["Fact", "Value"], rows, ("Fact",)


def in_sample_selection(payload: dict) -> list[dict]:
    return sorted(
        (
            row
            for row in payload["rows"]
            if row["weighting"] == "equal"
            and row["beta_neutral"] is True
            and row["transaction_costs"] == 0.001
            and row["long_quantile"] == row["short_quantile"]
        ),
        key=lambda row: (row["beta_window"], row["long_quantile"]),
    )


IN_SAMPLE_COLUMNS = (
    "beta_window",
    "long_quantile",
    "short_quantile",
    "transaction_costs",
    "sharpe",
    "wealth",
    "realized_beta",
    "model_beta",
    "turnover",
    "gross",
)
IN_SAMPLE_INTS = ("beta_window",)


def in_sample_table(payload: dict) -> tuple[list[str], list[dict], tuple]:
    return list(IN_SAMPLE_COLUMNS), in_sample_selection(payload), ("beta_window", "long_quantile")


def contrast_table(payload: dict) -> tuple[list[str], list[dict], tuple]:
    rows = sorted(
        (
            row
            for row in payload["rows"]
            if row["weighting"] == "equal"
            and row["beta_window"] == 90
            and row["long_quantile"] == 0.3
            and row["transaction_costs"] == 0.001
        ),
        key=lambda row: row["beta_neutral"],
    )
    columns = ("beta_neutral", "model_beta", "realized_beta", "sharpe", "wealth", "gross")
    return list(columns), rows, ("beta_neutral",)


FOLD_COLUMNS = (
    "fold",
    "n_train",
    "n_test",
    "selected_beta_window",
    "selected_long_quantile",
    "selected_short_quantile",
    "train_sharpe",
    "oos_sharpe",
    "oos_wealth",
    "oos_realized_beta",
    "oos_turnover",
    "oos_max_drawdown",
    "oos_vol",
)
FOLD_INTS = ("fold", "n_train", "n_test", "selected_beta_window")


def folds_table(payload: dict) -> tuple[list[str], list[dict], tuple]:
    return list(FOLD_COLUMNS), list(payload["folds"]), ("fold",)


AGGREGATE_COLUMNS = ("candidates_evaluated", "total_oos_rows", "mean_oos_sharpe",
                     "median_oos_sharpe", "fraction_positive_oos_sharpe")


def aggregate_table(payload: dict) -> tuple[list[str], list[dict], tuple]:
    aggregate = payload["aggregate"]
    rows = [{"Metric": column, "Value": aggregate[column]} for column in AGGREGATE_COLUMNS]
    return ["Metric", "Value"], rows, ("Metric",)


BREAKEVEN_COLUMNS = (
    "beta_window",
    "long_quantile",
    "uncosted_sharpe",
    "break_even_tc",
    "sharpe_at_break_even",
    "turnover_at_break_even",
    "gross_at_break_even",
)


def breakeven_table(payload: dict) -> tuple[list[str], list[dict], tuple]:
    rows = sorted(payload["rows"], key=lambda row: (row["beta_window"], row["long_quantile"]))
    return list(BREAKEVEN_COLUMNS), rows, ("beta_window", "long_quantile")


def null_rows_table(payload: dict) -> tuple[list[str], list[dict], tuple]:
    reasons = payload["provenance"]["null_field_reasons"]
    rows = []
    for row in payload["rows"]:
        if row["break_even_tc"] is not None:
            continue
        key = f"{row['beta_window']}|{row['long_quantile']}"
        detail = reasons[key]
        rows.append(
            {
                "Configuration": f"w{row['beta_window']} q{row['long_quantile']:g}",
                "Empty fields": ", ".join(detail["fields"]),
                "Documented reason": detail["reason"],
            }
        )
    return ["Configuration", "Empty fields", "Documented reason"], rows, ("Configuration",)


TABLES = {
    "provenance": provenance_rows,
    "in_sample": in_sample_table,
    "contrast": contrast_table,
    "folds": folds_table,
    "aggregate": aggregate_table,
    "breakeven": breakeven_table,
    "null_rows": null_rows_table,
}


def _built(name: str, payload: dict) -> tuple[list[str], list[dict], tuple]:
    columns, rows, ids = TABLES[name](payload)
    int_cols = {
        "in_sample": IN_SAMPLE_INTS,
        "folds": FOLD_INTS,
        "aggregate": ("candidates_evaluated", "total_oos_rows"),
        "breakeven": ("beta_window",),
    }.get(name, ())
    return columns, rows, ids, int_cols


def _payload_for(name: str, sweep, walk_forward, breakeven) -> dict:
    return {
        "provenance": sweep,
        "in_sample": sweep,
        "contrast": sweep,
        "folds": walk_forward,
        "aggregate": walk_forward,
        "breakeven": breakeven,
        "null_rows": breakeven,
    }[name]


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


def _all_cells(markdown: str) -> list[str]:
    cells = []
    for body in _extract_tables(markdown).values():
        for row in _rows(body):
            cells.extend(row)
    return cells


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


# --------------------------------------------------------------------------- #
# 1 + 2. Zero unmatched numbers, and no hand-typed drift
# --------------------------------------------------------------------------- #
def test_report_exists_and_declares_its_sources() -> None:
    assert REPORT_PATH.is_file()
    text = REPORT_PATH.read_text(encoding="utf-8")
    for name in ("sweep.json", "walk_forward.json", "breakeven.json"):
        assert name in text


def test_every_published_number_matches_a_committed_json_field(
    sweep, walk_forward, breakeven, report
) -> None:
    allowed = (
        _numeric_leaves(sweep) | _numeric_leaves(walk_forward) | _numeric_leaves(breakeven)
    )
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
    assert len(published) >= 150, "report publishes too few checked numbers"


def test_tables_are_byte_identical_to_the_json_renderers(
    sweep, walk_forward, breakeven, report
) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLES), f"table anchors differ: {sorted(published)}"
    for name in TABLES:
        payload = _payload_for(name, sweep, walk_forward, breakeven)
        columns, rows, _ids, int_cols = _built(name, payload)
        expected = "\n".join(_render(columns, rows, int_cols))
        assert published[name] == expected, f"table {name} drifted from its JSON artifact"


def test_triples_are_set_equal_to_the_json_artifacts(
    sweep, walk_forward, breakeven, report
) -> None:
    published = _extract_tables(report)

    def triples(lines: list[str], id_columns: tuple) -> set:
        header = [cell.strip() for cell in lines[0].strip().strip("|").split("|")]
        result = set()
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            mapping = dict(zip(header, cells))
            identity = tuple(mapping[column] for column in id_columns)
            for column, value in mapping.items():
                result.add((identity, column, value))
        return result

    for name in TABLES:
        payload = _payload_for(name, sweep, walk_forward, breakeven)
        columns, rows, ids, int_cols = _built(name, payload)
        expected = triples(_render(columns, rows, int_cols), ids)
        actual = triples(published[name].splitlines(), ids)
        assert actual == expected, f"triple drift in table {name}"


def test_prose_does_not_quote_unbacked_numbers(sweep, walk_forward, breakeven, report) -> None:
    allowed = (
        _numeric_leaves(sweep) | _numeric_leaves(walk_forward) | _numeric_leaves(breakeven)
    )
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
# 3. Provenance facts are present and true
# --------------------------------------------------------------------------- #
def _flat(text: str) -> str:
    return " ".join(text.lower().split())


def test_provenance_section_states_the_fixture_is_synthetic(report, sweep) -> None:
    provenance = sweep["provenance"]
    lowered = _flat(report)
    assert "deterministic synthetic random walk" in lowered
    assert "not real market data" in lowered
    assert provenance["synthetic"] is True
    assert re.search(r"\b[0-9a-f]{64}\b", report)
    assert provenance["fixture_sha256"] in report
    assert provenance["date_first"] in report
    assert provenance["date_last"] in report
    assert str(provenance["seed"]) in report
    assert provenance["known_gap"] in report
    assert "DEL" in report
    assert str(provenance["price_rows"]) in report
    assert str(provenance["return_rows"]) in report


# --------------------------------------------------------------------------- #
# 4. Rank discipline
# --------------------------------------------------------------------------- #
def test_rank_mode_is_declared_not_evaluable_without_rank_numbers(report) -> None:
    lowered = _flat(report)
    assert "not empirically evaluable" in lowered
    for token in FORBIDDEN_RANK_TOKENS:
        assert token not in report
    assert not re.search(r"^\|\s*rank\s*\|", report, flags=re.MULTILINE)


# --------------------------------------------------------------------------- #
# 5. Null honesty
# --------------------------------------------------------------------------- #
def test_every_null_break_even_publishes_its_documented_reason(breakeven, report) -> None:
    reasons = breakeven["provenance"]["null_field_reasons"]
    nulls = [row for row in breakeven["rows"] if row["break_even_tc"] is None]
    assert len(nulls) == len(reasons) > 0
    for row in nulls:
        key = f"{row['beta_window']}|{row['long_quantile']}"
        assert reasons[key]["reason"] in report
    assert "zero break-even" not in _flat(report)
    table = _extract_tables(report)["breakeven"]
    header = [cell.strip() for cell in table.splitlines()[0].strip().strip("|").split("|")]
    rows = _rows(table)
    column = header.index("break_even_tc")
    for null in nulls:
        matches = [
            row
            for row in rows
            if row[0] == str(null["beta_window"])
            and round(float(row[1]), DECIMALS) == round(float(null["long_quantile"]), DECIMALS)
        ]
        assert len(matches) == 1
        assert matches[0][column] == "None"
        assert "0.000000" not in matches[0]


def test_null_break_even_companion_fields_stay_null(breakeven) -> None:
    for row in breakeven["rows"]:
        if row["break_even_tc"] is None:
            assert row["sharpe_at_break_even"] is None
            assert row["turnover_at_break_even"] is None
            assert row["gross_at_break_even"] is None


# --------------------------------------------------------------------------- #
# 6. The test itself never re-runs a harness
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
    for name in ("sweep", "walk_forward", "breakeven"):
        _load(name)
    REPORT_PATH.read_text(encoding="utf-8")
    assert time.perf_counter() - start < 2.0


# --------------------------------------------------------------------------- #
# Supporting guarantees: the report is a complete P20 report
# --------------------------------------------------------------------------- #
def test_report_covers_all_required_sections(report) -> None:
    headings = [line for line in report.splitlines() if line.startswith("## ")]
    lowered = " ".join(headings).lower()
    for required in ("provenance", "in-sample", "walk-forward", "break-even",
                     "conclusion", "does not prove"):
        assert required in lowered, f"missing section: {required}"


def test_report_never_claims_real_profitability(report, walk_forward) -> None:
    lowered = _flat(report)
    assert "no demonstrated real-world profitability" in lowered
    aggregate = walk_forward["aggregate"]
    if aggregate["fraction_positive_oos_sharpe"] <= 0.6:
        assert "not a demonstrated profitable strategy" in lowered
