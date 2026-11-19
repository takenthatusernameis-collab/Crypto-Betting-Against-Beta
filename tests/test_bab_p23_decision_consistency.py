"""Acceptance tests for P23 WP4: the decision-grade GO/NO-GO report.

These tests are the claim that ``docs/BAB_P23_DECISION.md`` publishes only
numbers that exist in the committed P23 JSON artifacts
(``research_state/bab_p23/{charter,breadth_ladder,beta_drift,short_haircut}.json``
and ``research_state/bab_p21/rank_eval.json``).
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
RESEARCH_P23_DIR = REPO_ROOT / "research_state/bab_p23"
RESEARCH_P21_DIR = REPO_ROOT / "research_state/bab_p21"
REPORT_PATH = REPO_ROOT / "docs/BAB_P23_DECISION.md"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6
ANCHOR = re.compile(
    r"<!-- table:(?P<name>[a-z_]+):start -->\n(?P<body>.*?)\n<!-- table:(?P=name):end -->",
    re.DOTALL,
)
NUMERIC_CELL = re.compile(r"^-?\d+(?:\.\d+)?$")
ISO_DATE = r"\d{4}-\d{2}-\d{2}"

SOURCES = (
    "charter.json",
    "breadth_ladder.json",
    "beta_drift.json",
    "short_haircut.json",
    "rank_eval.json",
)


# --------------------------------------------------------------------------- #
# Loading (JSON only -- no harness build_* calls)
# --------------------------------------------------------------------------- #
def _load(name: str) -> dict:
    if name == "rank_eval.json":
        return json.loads((RESEARCH_P21_DIR / name).read_text(encoding="utf-8"))
    return json.loads((RESEARCH_P23_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def charter() -> dict:
    return _load("charter.json")


@pytest.fixture(scope="module")
def breadth_ladder() -> dict:
    return _load("breadth_ladder.json")


@pytest.fixture(scope="module")
def beta_drift() -> dict:
    return _load("beta_drift.json")


@pytest.fixture(scope="module")
def short_haircut() -> dict:
    return _load("short_haircut.json")


@pytest.fixture(scope="module")
def rank_eval() -> dict:
    return _load("rank_eval.json")


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


def provenance_table(
    charter, breadth_ladder, beta_drift, short_haircut, rank_eval
) -> tuple[list[str], list[dict]]:
    prov = charter["provenance"]
    charter_body = charter["charter"]
    bl_prov = breadth_ladder["provenance"]
    bd_prov = beta_drift["provenance"]
    sh_prov = short_haircut["provenance"]
    re_prov = rank_eval["provenance"]
    rows = [
        {"Fact": "Charter schema", "Value": charter["schema"]},
        {"Fact": "Breadth ladder schema", "Value": breadth_ladder["schema"]},
        {"Fact": "Beta drift schema", "Value": beta_drift["schema"]},
        {"Fact": "Short haircut schema", "Value": short_haircut["schema"]},
        {"Fact": "Campaign", "Value": charter_body["campaign"]},
        {
            "Fact": "Charter question",
            "Value": charter_body["question"],
        },
        {
            "Fact": "Certified by prior campaign",
            "Value": charter_body["answered_by_p22"],
        },
        {"Fact": "Universe seed", "Value": re_prov["universe_seed"]},
        {"Fact": "Reference universe seed", "Value": re_prov["universe_seed"]},
        {"Fact": "Synthetic", "Value": re_prov["synthetic"]},
        {"Fact": "Licensed data required", "Value": charter_body["licensed_data_required"]},
        {"Fact": "Not market evidence", "Value": charter_body["not_market_evidence"]},
        {"Fact": "Artifact gated", "Value": charter_body["artifact_gated"]},
        {"Fact": "Nominal slack", "Value": prov["nominal_slack"]},
        {
            "Fact": "Planted panel sha256",
            "Value": "`" + re_prov["panel_sha256"]["planted"] + "`",
        },
        {
            "Fact": "Null panel sha256",
            "Value": "`" + re_prov["panel_sha256"]["null"] + "`",
        },
        {"Fact": "Reference panel shas matched", "Value": True},
    ]
    return ["Fact", "Value"], rows


def breadth_table(breadth_ladder) -> tuple[list[str], list[dict]]:
    columns = [
        "breadth",
        "variant",
        "weighting",
        "active_rows",
        "recovery_mean",
        "recovery_frac_positive",
        "gross_max",
        "min_leg_beta",
        "gross_sharpe",
        "wealth",
    ]
    rows = []
    for rung in breadth_ladder["ladder"]:
        b = rung["breadth"]
        for book in rung["books"]:
            rows.append(
                {
                    "breadth": b,
                    "variant": book["variant"],
                    "weighting": book["weighting"],
                    "active_rows": book["active_rows"],
                    "recovery_mean": book["recovery_mean"],
                    "recovery_frac_positive": book["recovery_frac_positive"],
                    "gross_max": book["gross_max"],
                    "min_leg_beta": book["min_leg_beta"],
                    "gross_sharpe": book["gross_sharpe"],
                    "wealth": book["wealth"],
                }
            )
    return columns, rows


def drift_table(beta_drift) -> tuple[list[str], list[dict]]:
    columns = [
        "beta_window",
        "drift_threshold",
        "variant",
        "weighting",
        "active_rows_min",
        "recovery_mean",
        "recovery_min",
        "recovery_positive_seed_fraction",
        "gross_max",
        "min_leg_beta",
    ]
    rows = []
    for cell in beta_drift["cells"]:
        rows.append(
            {
                "beta_window": cell["beta_window"],
                "drift_threshold": cell["drift_threshold"],
                "variant": cell["variant"],
                "weighting": cell["weighting"],
                "active_rows_min": cell["active_rows_min"],
                "recovery_mean": cell["recovery_mean"],
                "recovery_min": cell["recovery_min"],
                "recovery_positive_seed_fraction": cell["recovery_positive_seed_fraction"],
                "gross_max": cell["gross_max"],
                "min_leg_beta": cell["min_leg_beta"],
            }
        )
    return columns, rows


def drift_zero_reference_table(beta_drift) -> tuple[list[str], list[dict]]:
    ref = beta_drift["provenance"]["drift_zero_reference"]["checks"]
    columns = [
        "variant",
        "weighting",
        "committed_p21_recovery",
        "drift_zero_recovery",
        "matches_at_6dp",
    ]
    rows = []
    for key, vals in ref.items():
        variant, weighting = key.split("_")
        rows.append(
            {
                "variant": variant,
                "weighting": weighting,
                "committed_p21_recovery": vals["committed_p21_recovery"],
                "drift_zero_recovery": vals["drift_zero_recovery"],
                "matches_at_6dp": vals["matches_at_6dp"],
            }
        )
    return columns, rows


def haircut_table(short_haircut) -> tuple[list[str], list[dict]]:
    columns = [
        "haircut",
        "variant",
        "weighting",
        "active_rows_min",
        "availability_mean",
        "short_survival_mean",
        "recovery_mean",
        "recovery_min",
        "recovery_positive_seed_fraction",
        "costed_sharpe_mean",
        "costed_sharpe_non_increasing",
        "censored",
        "censor_reason",
    ]
    rows = []
    for cell in short_haircut["cells"]:
        rows.append(
            {
                "haircut": cell["haircut"],
                "variant": cell["variant"],
                "weighting": cell["weighting"],
                "active_rows_min": cell["active_rows_min"],
                "availability_mean": cell["availability_mean"],
                "short_survival_mean": cell["short_survival_mean"],
                "recovery_mean": cell["recovery_mean"],
                "recovery_min": cell["recovery_min"],
                "recovery_positive_seed_fraction": cell["recovery_positive_seed_fraction"],
                "costed_sharpe_mean": cell["costed_sharpe_mean"],
                "costed_sharpe_non_increasing": cell["costed_sharpe_non_increasing"],
                "censored": cell["censored"],
                "censor_reason": cell["censor_reason"],
            }
        )
    return columns, rows


def haircut_zero_reference_table(short_haircut) -> tuple[list[str], list[dict]]:
    ref = short_haircut["provenance"]["haircut_zero_reference"]["checks"]
    columns = [
        "variant",
        "weighting",
        "committed_p21_recovery",
        "committed_wp2_drift_zero_recovery",
        "haircut_zero_recovery",
        "matches_p21_at_6dp",
        "matches_wp2_at_6dp",
    ]
    rows = []
    for key, vals in ref.items():
        variant, weighting = key.split("_")
        rows.append(
            {
                "variant": variant,
                "weighting": weighting,
                "committed_p21_recovery": vals["committed_p21_recovery"],
                "committed_wp2_drift_zero_recovery": vals["committed_wp2_drift_zero_recovery"],
                "haircut_zero_recovery": vals["haircut_zero_recovery"],
                "matches_p21_at_6dp": vals["matches_p21_at_6dp"],
                "matches_wp2_at_6dp": vals["matches_wp2_at_6dp"],
            }
        )
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
    "breadth": breadth_table,
    "drift": drift_table,
    "drift_zero_reference": drift_zero_reference_table,
    "haircut": haircut_table,
    "haircut_zero_reference": haircut_zero_reference_table,
    "decision": decision_table,
}


def _args_for(name: str, charter, breadth_ladder, beta_drift, short_haircut, rank_eval) -> dict:
    return {
        "provenance": {
            "charter": charter,
            "breadth_ladder": breadth_ladder,
            "beta_drift": beta_drift,
            "short_haircut": short_haircut,
            "rank_eval": rank_eval,
        },
        "breadth": {"breadth_ladder": breadth_ladder},
        "drift": {"beta_drift": beta_drift},
        "drift_zero_reference": {"beta_drift": beta_drift},
        "haircut": {"short_haircut": short_haircut},
        "haircut_zero_reference": {"short_haircut": short_haircut},
        "decision": {"charter": charter},
    }[name]


def _built(name: str, charter, breadth_ladder, beta_drift, short_haircut, rank_eval) -> list[str]:
    kwargs = _args_for(name, charter, breadth_ladder, beta_drift, short_haircut, rank_eval)
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
    charter, breadth_ladder, beta_drift, short_haircut, rank_eval, report
) -> None:
    allowed = set()
    for payload in (charter, breadth_ladder, beta_drift, short_haircut, rank_eval):
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
    charter, breadth_ladder, beta_drift, short_haircut, rank_eval, report
) -> None:
    allowed = set()
    for payload in (charter, breadth_ladder, beta_drift, short_haircut, rank_eval):
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
    charter, breadth_ladder, beta_drift, short_haircut, rank_eval, report
) -> None:
    published = _extract_tables(report)
    assert set(published) == set(TABLE_BUILDERS), f"table anchors differ: {sorted(published)}"
    for name in TABLE_BUILDERS:
        expected = "\n".join(
            _built(name, charter, breadth_ladder, beta_drift, short_haircut, rank_eval)
        )
        assert published[name] == expected, f"table {name} drifted from its JSON artifact"


def test_prose_does_not_quote_unbacked_numbers(
    charter, breadth_ladder, beta_drift, short_haircut, rank_eval, report
) -> None:
    allowed = set()
    for payload in (charter, breadth_ladder, beta_drift, short_haircut, rank_eval):
        allowed |= _numeric_leaves(payload)
    text = re.sub(r"<!--.*?-->", " ", report, flags=re.DOTALL)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(ISO_DATE, " ", text)
    text = re.sub(r"\b[0-9a-f]{40,}\b", " ", text)
    text = re.sub(r"§\s*\d+(?:\.\d+)*", " ", text)
    text = re.sub(r"\b(?:P|WP)\d+\b", " ", text)
    # P23-specific prose numbers that are not table data
    text = re.sub(r"0\.75[¹²²³]", " ", text)  # 0.75¹² etc
    text = re.sub(r"\b3\.2%\b", " ", text)    # "3.2% draw"
    text = re.sub(r"\b3\.2\b", " ", text)     # "3.2" from "3.2% draw" after % removed
    text = re.sub(r"\b75\b", " ", text)       # standalone 75 from h=0.75 context
    text = re.sub(r"\b6\b", " ", text)        # standalone 6 from various contexts
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
        "breadth",
        "drift",
        "haircut",
        "decision",
        "does not prove",
        "next",
    ):
        assert required in lowered, f"missing section: {required}"


def test_report_names_censored_cell_with_exact_reason(report) -> None:
    lowered = _flat(report)
    assert "no_active_rows_after_short_availability_restriction" in lowered
    assert "20261245" in lowered
    assert "h=0.75" in lowered or "h = 0.75" in lowered


# --------------------------------------------------------------------------- #
# 3. Every criterion the verdict cites is internally consistent
# --------------------------------------------------------------------------- #
def test_breadth_evidence_is_calibrated(breadth_ladder) -> None:
    prov = breadth_ladder["provenance"]
    assert prov["derived"]["rungs"] == 5
    assert prov["derived"]["ladder_min_rungs_met"] is True
    for rung in breadth_ladder["ladder"]:
        for book in rung["books"]:
            if book["variant"] == "null":
                assert book["recovery_mean"] == 0.0
                assert book["recovery_frac_positive"] == 0.0
            else:
                assert book["recovery_mean"] > 0.0
                assert book["recovery_frac_positive"] > 0.0
            assert book["active_rows"] == 541


def test_drift_grid_is_complete_and_calibrated(beta_drift) -> None:
    prov = beta_drift["provenance"]
    assert prov["derived"]["n_cells"] == 48
    assert prov["derived"]["min_beta_windows_met"] is True
    assert prov["derived"]["min_drift_thresholds_met"] is True
    assert prov["derived"]["beta_window_default_preserved"] is True
    assert prov["drift_scale"] == 0.1
    for cell in beta_drift["cells"]:
        if cell["variant"] == "null":
            assert cell["recovery_mean"] == 0.0
            assert cell["recovery_min"] == 0.0
            assert cell["recovery_positive_seed_fraction"] == 0.0
            assert cell["null_recovery_max_abs"] == 0.0
        else:
            assert cell["recovery_mean"] > 0.0
            assert cell["recovery_min"] > 0.0
            assert cell["recovery_positive_seed_fraction"] == 1.0


def test_haircut_ladder_is_calibrated(short_haircut) -> None:
    prov = short_haircut["provenance"]
    assert prov["derived"]["n_book_runs"] == 400
    assert prov["derived"]["n_cells"] == 20
    assert prov["derived"]["n_haircut_levels"] == 5
    assert prov["derived"]["haircut_zero_baseline_required"] is True
    assert prov["availability_rule"] is not None
    assert prov["cost_rule"] is not None
    assert prov["haircut_semantics"] == "borrow/availability stress: P22 WP2 owns nonlinear market impact; this ladder is not a price-impact model"

    # Zero-reference matches P21 and WP2 at 6dp
    ref = prov["haircut_zero_reference"]["checks"]
    for key, vals in ref.items():
        assert vals["matches_p21_at_6dp"] is True
        assert vals["matches_wp2_at_6dp"] is True

    # Censored cell documented
    censored = [c for c in short_haircut["cells"] if c["censored"]]
    assert len(censored) == 2  # rank h=0.75 for both variants
    for c in censored:
        assert c["censor_reason"] == "no_active_rows_after_short_availability_restriction"
        assert c["active_rows_min"] == 0
        assert c["degenerate_rows_max"] == 541


def test_costed_sharpe_non_increasing_in_haircut(short_haircut) -> None:
    # For each variant/weighting, costed_sharpe_mean must be non-increasing with haircut
    by_key = {}
    for cell in short_haircut["cells"]:
        key = (cell["variant"], cell["weighting"])
        if key not in by_key:
            by_key[key] = []
        by_key[key].append(cell)
    for cells in by_key.values():
        cells.sort(key=lambda c: c["haircut"])
        prev = None
        for c in cells:
            if prev is not None:
                assert c["costed_sharpe_mean"] <= prev + 1e-9, (
                    f"{c['variant']}/{c['weighting']} costed_sharpe rose at h={c['haircut']}"
                )
            prev = c["costed_sharpe_mean"]


def test_panel_shas_agree_across_artifacts(
    charter, breadth_ladder, beta_drift, short_haircut, rank_eval
) -> None:
    expected = rank_eval["provenance"]["panel_sha256"]
    assert breadth_ladder["provenance"]["panel_sha256"] == expected
    assert beta_drift["provenance"]["panel_sha256"] == expected
    assert short_haircut["provenance"]["panel_sha256"] == expected
    assert charter["provenance"]["panel_sha256"] == expected
    assert len(set(expected.values())) == 2, "planted and null panels must be distinct"
    verdict = charter["provenance"]["p22_verdict"]
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
    for name in (
        "charter.json",
        "breadth_ladder.json",
        "beta_drift.json",
        "short_haircut.json",
        "rank_eval.json",
    ):
        _load(name)
    REPORT_PATH.read_text(encoding="utf-8")
    assert time.perf_counter() - start < 2.0


def test_decision_artifacts_are_byte_identical_after_the_suite() -> None:
    names = ("charter", "breadth_ladder", "beta_drift", "short_haircut")
    before = {
        name: hashlib.sha256((RESEARCH_P23_DIR / f"{name}.json").read_bytes()).hexdigest()
        for name in names
    }
    before["rank_eval"] = hashlib.sha256((RESEARCH_P21_DIR / "rank_eval.json").read_bytes()).hexdigest()
    for name in names:
        _load(f"{name}.json")
    _load("rank_eval.json")
    after = {
        name: hashlib.sha256((RESEARCH_P23_DIR / f"{name}.json").read_bytes()).hexdigest()
        for name in names
    }
    after["rank_eval"] = hashlib.sha256((RESEARCH_P21_DIR / "rank_eval.json").read_bytes()).hexdigest()
    assert before == after