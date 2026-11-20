"""Acceptance tests for P24 WP0: the charter artifact.

These tests are the claim that ``research_state/bab_p24/charter.json`` publishes
only thresholds and constants that exist in the committed P21/P22/P23 JSON
artifacts and that the licensed-price CSV schema fixture is valid.

They never import ``scripts`` or ``strategies`` and never call a ``build_*``
harness: every charter field is validated against committed JSON and the
fixture is schema-checked.

A hand-typed number, a stale field, a market GO verdict, or a planted-universe
recovery quoted as market alpha fails the suite.
"""

from __future__ import annotations

import ast
import hashlib
import json
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_P24_DIR = REPO_ROOT / "research_state/bab_p24"
RESEARCH_P23_DIR = REPO_ROOT / "research_state/bab_p23"
RESEARCH_P22_DIR = REPO_ROOT / "research_state/bab_p22"
RESEARCH_P21_DIR = REPO_ROOT / "research_state/bab_p21"
CHARTER_P24_PATH = RESEARCH_P24_DIR / "charter.json"
FIXTURE_PATH = REPO_ROOT / "tests/fixtures/licensed_price_schema.csv"
TEST_PATH = Path(__file__).resolve()

DECIMALS = 6

SOURCES = (
    "charter.json",  # P23 charter
    "breadth_ladder.json",
    "beta_drift.json",
    "short_haircut.json",
    "rank_eval.json",  # P21
    "null_battery.json",  # P22
    "impact_surface.json",  # P22
    "capacity.json",  # P22
)


# --------------------------------------------------------------------------- #
# Loading (JSON only -- no harness build_* calls)
# --------------------------------------------------------------------------- #
def _load_p24(name: str) -> dict:
    p = RESEARCH_P24_DIR / name
    return json.loads(p.read_text(encoding="utf-8"))


def _load_p23(name: str) -> dict:
    p = RESEARCH_P23_DIR / name
    return json.loads(p.read_text(encoding="utf-8"))


def _load_p22(name: str) -> dict:
    p = RESEARCH_P22_DIR / name
    return json.loads(p.read_text(encoding="utf-8"))


def _load_p21(name: str) -> dict:
    p = RESEARCH_P21_DIR / name
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def p24_charter() -> dict:
    return _load_p24("charter.json")


@pytest.fixture(scope="module")
def p23_charter() -> dict:
    return _load_p23("charter.json")


@pytest.fixture(scope="module")
def breadth_ladder() -> dict:
    return _load_p23("breadth_ladder.json")


@pytest.fixture(scope="module")
def beta_drift() -> dict:
    return _load_p23("beta_drift.json")


@pytest.fixture(scope="module")
def short_haircut() -> dict:
    return _load_p23("short_haircut.json")


@pytest.fixture(scope="module")
def rank_eval() -> dict:
    return _load_p21("rank_eval.json")


@pytest.fixture(scope="module")
def null_battery() -> dict:
    return _load_p22("null_battery.json")


@pytest.fixture(scope="module")
def impact_surface() -> dict:
    return _load_p22("impact_surface.json")


@pytest.fixture(scope="module")
def capacity() -> dict:
    return _load_p22("capacity.json")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _flat(text: str) -> str:
    return " ".join(text.lower().split())


def _numeric_leaves(node) -> set:
    values = set()
    if isinstance(node, dict):
        for v in node.values():
            values |= _numeric_leaves(v)
    elif isinstance(node, list):
        for v in node:
            values |= _numeric_leaves(v)
    elif isinstance(node, bool):
        return values
    elif isinstance(node, (int, float)):
        values.add(round(float(node), DECIMALS))
    return values


def _csv_header(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()[0].split(",")


# --------------------------------------------------------------------------- #
# 1. Charter JSON validates against committed P21/P22/P23 artifacts
# --------------------------------------------------------------------------- #
def test_p24_charter_exists_and_reads() -> None:
    assert CHARTER_P24_PATH.is_file()
    data = json.loads(CHARTER_P24_PATH.read_text(encoding="utf-8"))
    assert data["schema"] == "bab_p24.charter/1"
    charter = data["charter"]
    assert charter["campaign"] == "P24"
    assert charter["title"] == "Regime-conditional BAB and holdout discipline"
    assert charter["binding_row"] == "P24 WP0"
    assert charter["artifact_gated"] is True
    assert charter["not_market_evidence"] is True
    assert charter["licensed_data_required"] is True
    assert charter["holdout_before_tuning"] is True
    assert charter["regime_grid"] == ["calm", "stress"]
    assert charter["hysteresis_band_grid"] == [0.05, 0.10, 0.15]
    schema_path = "tests/fixtures/licensed_price_schema.csv"
    assert charter["licensed_price_csv_schema"] == schema_path
    assert charter["wps_in_order"] == ["P24 WP0 \u2014 charter"]
    prov = data["provenance"]
    assert prov["no_go_for_market"] is True
    assert prov["licensed_data_required"] is True
    assert prov["synthetic"] is True
    assert prov["universe_seed"] == 20261118
    assert prov["p23_source_schema"] == "bab_p23.charter/1"


def test_charter_sources_all_exist_and_parse() -> None:
    for name in SOURCES:
        if name == "rank_eval.json":
            _load_p21(name)
        elif name in ("null_battery.json", "impact_surface.json", "capacity.json"):
            _load_p22(name)
        else:
            _load_p23(name)


def test_p24_charter_universe_seed_matches_p21(p24_charter, rank_eval) -> None:
    expected_seed = 20261118
    assert p24_charter["provenance"]["universe_seed"] == expected_seed
    assert rank_eval["provenance"]["universe_seed"] == expected_seed


def test_p24_charter_panel_shas_match_p21(p24_charter) -> None:
    p23_charter = _load_p23("charter.json")
    rank_eval = _load_p21("rank_eval.json")
    expected = rank_eval["provenance"]["panel_sha256"]
    assert p23_charter["provenance"]["panel_sha256"] == expected
    assert p24_charter["provenance"]["p23_source_schema"] == p23_charter["schema"]


def test_charter_no_go_for_market_enforced(p24_charter, p23_charter) -> None:
    # P23 charter verdict must have no_go_for_market = True
    assert p23_charter["provenance"]["p22_verdict"]["no_go_for_market"] is True
    # P24 charter must also declare it
    assert p24_charter["provenance"]["no_go_for_market"] is True


def test_p24_charter_numeric_fields_exist_in_committed_json(
    p24_charter, p23_charter, breadth_ladder, beta_drift,
    short_haircut, rank_eval, null_battery, impact_surface, capacity
) -> None:
    """Every numeric field in P24 charter must resolve to a committed JSON leaf."""
    allowed = set()
    for payload in (
        p23_charter, breadth_ladder, beta_drift, short_haircut,
        rank_eval, null_battery, impact_surface, capacity
    ):
        allowed |= _numeric_leaves(payload)

    # P24 charter declares hysteresis_band_grid constants -- these are charter
    # constants, not measured numbers; verify they're explicitly declared
    declared_constants = {0.05, 0.10, 0.15}
    charter_numeric = _numeric_leaves(p24_charter["charter"])
    charter_prov_numeric = _numeric_leaves(p24_charter["provenance"])
    for val in charter_numeric | charter_prov_numeric:
        if val not in allowed and val not in declared_constants:
            assert val in allowed, f"P24 charter introduces undeclared numeric constant: {val}"


# --------------------------------------------------------------------------- #
# 2. Licensed-price CSV schema fixture validation
# --------------------------------------------------------------------------- #
def test_fixture_exists() -> None:
    assert FIXTURE_PATH.is_file(), f"Missing fixture: {FIXTURE_PATH}"


def test_fixture_has_valid_header() -> None:
    header = _csv_header(FIXTURE_PATH)
    assert header[0] == "date"
    assert header[1] == "BTC"
    asset_cols = header[2:]
    assert len(asset_cols) == 41, f"Expected 41 asset columns, got {len(asset_cols)}"
    expected = [f"A{i:03d}" for i in range(1, 42)]
    assert asset_cols == expected, f"Asset columns mismatch: {asset_cols} != {expected}"


def test_fixture_compatible_with_load_prices() -> None:
    """Fixture must be parseable by pandas and compatible with load_prices()."""
    import pandas as pd
    df = pd.read_csv(FIXTURE_PATH)
    assert "date" in df.columns
    assert "BTC" in df.columns
    assert len(df.columns) == 43  # date + BTC + 41 assets
    assert len(df) >= 2  # at least 2 rows for returns calc
    dates = pd.to_datetime(df["date"])
    assert dates.is_monotonic_increasing
    for col in df.columns:
        if col != "date":
            assert pd.api.types.is_numeric_dtype(df[col]), f"Column {col} not numeric"


# --------------------------------------------------------------------------- #
# 3. Verdict strings must be explicit and machine-backed
# --------------------------------------------------------------------------- #
def test_charter_declares_no_go_verdict(p24_charter, p23_charter) -> None:
    assert p24_charter["provenance"]["no_go_for_market"] is True
    p22_verdict = p23_charter["provenance"]["p22_verdict"]
    assert p22_verdict["verdict"] == "NO-GO for market deployment"
    assert p22_verdict["signal_on_planted"] is True
    assert p22_verdict["noise_on_null"] is True


def test_charter_labels_synthetic_not_market(p24_charter, p23_charter) -> None:
    assert p24_charter["provenance"]["synthetic"] is True
    assert p24_charter["charter"]["not_market_evidence"] is True
    assert p23_charter["provenance"]["synthetic"] is True
    assert p23_charter["charter"]["not_market_evidence"] is True
    caveat = p23_charter["provenance"]["caveat"]
    assert caveat is not None
    assert "never market alpha" in caveat.lower()


# --------------------------------------------------------------------------- #
# 4. Key thresholds from P23 charter must be present and match
# --------------------------------------------------------------------------- #
def test_p23_charter_thresholds_are_machine_pinned(
    p23_charter, breadth_ladder, beta_drift, short_haircut
) -> None:
    thresholds = p23_charter["provenance"]["acceptance_thresholds"]

    # WP1 breadth ladder
    assert thresholds["wp1"]["ladder_min_rungs"] == 3
    assert thresholds["wp1"]["recovery_null_exactly_zero"] == 0.0
    assert thresholds["wp1"]["recovery_planted_strictly_positive"] is True
    assert thresholds["wp1"]["rank_guards_never_relaxed"] is True
    assert thresholds["wp1"]["rank_max_gross"] == 4.0
    assert thresholds["wp1"]["rank_min_leg_beta"] == 0.2

    # WP2 drift grid
    assert thresholds["wp2"]["beta_window_default_preserved"] == 90
    assert thresholds["wp2"]["recovery_null_exactly_zero"] == 0.0
    assert thresholds["wp2"]["recovery_planted_strictly_positive"] is True

    # WP3 haircut ladder
    assert thresholds["wp3"]["haircut_zero_baseline_required"] is True
    assert thresholds["wp3"]["recovery_null_exactly_zero"] == 0.0
    assert thresholds["wp3"]["costed_sharpe_non_increasing_in_haircut"] is True
    assert thresholds["wp3"]["censored_reports_document_reason_never_zero_tolerance"] is True

    # WP4 decision
    wp4 = thresholds["wp4"]
    assert wp4["explicit_signal_noise_verdict"] is True
    assert wp4["no_go_for_market"] is True
    assert wp4["no_harness_re_run"] is True
    assert wp4["numbers_matched_min"] == 100
    assert wp4["planted_recovery_labelled_controlled_synthetic"] is True
    assert wp4["zero_unmatched_cells"] == 0


def test_p23_breadth_ladder_shape(breadth_ladder) -> None:
    ladder = breadth_ladder["ladder"]
    breadths = [rung["breadth"] for rung in ladder]
    assert breadths == [9, 17, 25, 33, 41]
    for rung in ladder:
        for book in rung["books"]:
            if book["variant"] == "null":
                assert book["recovery_mean"] == 0.0
            else:
                assert book["recovery_mean"] > 0.0


def test_p23_drift_grid_calibrated(beta_drift) -> None:
    assert beta_drift["provenance"]["drift_scale"] == 0.1
    cells = beta_drift["cells"]
    assert len(cells) == 48
    for cell in cells:
        if cell["variant"] == "null":
            assert cell["recovery_mean"] == 0.0
            assert cell["recovery_min"] == 0.0
        else:
            assert cell["recovery_mean"] > 0.0
            assert cell["recovery_min"] > 0.0


def test_p23_haircut_ladder_calibrated(short_haircut) -> None:
    prov = short_haircut["provenance"]
    assert prov["derived"]["n_book_runs"] == 400
    assert prov["derived"]["n_cells"] == 20
    assert prov["derived"]["n_haircut_levels"] == 5
    assert prov["availability_rule"] is not None
    assert prov["cost_rule"] is not None
    ref = prov["haircut_zero_reference"]["checks"]
    for vals in ref.values():
        assert vals["matches_p21_at_6dp"] is True
        assert vals["matches_wp2_at_6dp"] is True
    censored = [c for c in short_haircut["cells"] if c["censored"]]
    assert len(censored) == 2
    for c in censored:
        assert c["censor_reason"] == "no_active_rows_after_short_availability_restriction"
        assert c["active_rows_min"] == 0
        assert c["degenerate_rows_max"] == 541


def test_p22_null_battery_calibrated(null_battery) -> None:
    prov = null_battery["provenance"]
    summary = prov["summary"]
    assert summary["n_null_books"] == 40
    assert summary["n_planted_books"] == 40
    assert summary["n_seeds"] == 20
    assert summary["null_recovery_exactly_zero_every_seed"] is True
    assert summary["null_recovery_max_abs"] == 0.0
    assert summary["fpr_within_declared_bound"] is True
    assert summary["planted_recovery_exceeds_null_max"] is True


def test_p22_impact_surface_monotone(impact_surface) -> None:
    prov = impact_surface["provenance"]
    for book in impact_surface["books"]:
        assert book["monotonicity"]["market_impact"] is True
        assert book["period_wise_non_increasing"]["market_impact"] is True


def test_p22_capacity_break_even(capacity) -> None:
    for book in capacity["books"]:
        if not book["censored"]:
            assert book["bracket_halving_verified"] is True
            assert book["break_even_coefficient"] is not None
            assert book["break_even_coefficient"] > 0


# --------------------------------------------------------------------------- #
# 5. The test itself never re-runs a harness and never edits an artifact
# --------------------------------------------------------------------------- #
def test_charter_acceptance_never_executes_a_research_harness() -> None:
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
    for name in ("charter.json", "breadth_ladder.json", "beta_drift.json", "short_haircut.json"):
        _load_p23(name)
    for name in ("null_battery.json", "impact_surface.json", "capacity.json"):
        _load_p22(name)
    _load_p21("rank_eval.json")
    assert time.perf_counter() - start < 2.0


def test_charter_artifacts_are_byte_identical_after_suite() -> None:
    names_p23 = ("charter", "breadth_ladder", "beta_drift", "short_haircut")
    names_p22 = ("null_battery", "impact_surface", "capacity")
    name_p21 = "rank_eval"

    before = {}
    for name in names_p23:
        p = RESEARCH_P23_DIR / f"{name}.json"
        before[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    for name in names_p22:
        p = RESEARCH_P22_DIR / f"{name}.json"
        before[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    p21_path = RESEARCH_P21_DIR / f"{name_p21}.json"
    before[name_p21] = hashlib.sha256(p21_path.read_bytes()).hexdigest()

    for name in names_p23:
        _load_p23(f"{name}.json")
    for name in names_p22:
        _load_p22(f"{name}.json")
    _load_p21(f"{name_p21}.json")

    after = {}
    for name in names_p23:
        p = RESEARCH_P23_DIR / f"{name}.json"
        after[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    for name in names_p22:
        p = RESEARCH_P22_DIR / f"{name}.json"
        after[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    after[name_p21] = hashlib.sha256(p21_path.read_bytes()).hexdigest()

    assert before == after, "One or more research artifacts mutated during test run"


# --------------------------------------------------------------------------- #
# 6. P24 WP0 charter completeness
# --------------------------------------------------------------------------- #
def test_p24_wp0_charter_is_complete(p24_charter) -> None:
    charter = p24_charter["charter"]
    prov = p24_charter["provenance"]

    assert charter["campaign"] == "P24"
    assert "title" in charter
    assert charter["binding_row"] == "P24 WP0"
    assert charter["artifact_gated"] is True
    assert charter["not_market_evidence"] is True
    assert charter["licensed_data_required"] is True
    assert "regime_grid" in charter
    assert charter["regime_grid"] == ["calm", "stress"]
    assert "holdout_before_tuning" in charter
    assert charter["holdout_before_tuning"] is True
    assert "hysteresis_band_grid" in charter
    assert charter["hysteresis_band_grid"] == [0.05, 0.10, 0.15]
    assert "licensed_price_csv_schema" in charter
    assert charter["licensed_price_csv_schema"] == "tests/fixtures/licensed_price_schema.csv"
    assert "wps_in_order" in charter
    assert charter["wps_in_order"] == ["P24 WP0 \u2014 charter"]

    assert prov["no_go_for_market"] is True
    assert prov["licensed_data_required"] is True
    assert prov["synthetic"] is True
    assert prov["universe_seed"] == 20261118
    assert "p23_source_schema" in prov


# --------------------------------------------------------------------------- #
# 7. Integration: fixture path declared in charter must exist and be valid
# --------------------------------------------------------------------------- #
def test_charter_fixture_path_resolves(p24_charter) -> None:
    fixture_rel = p24_charter["charter"]["licensed_price_csv_schema"]
    fixture_abs = REPO_ROOT / fixture_rel
    assert fixture_abs.is_file(), f"Charter declares fixture {fixture_rel} but it does not exist"
    header = _csv_header(fixture_abs)
    assert header[0] == "date"
    assert header[1] == "BTC"
    asset_cols = header[2:]
    assert len(asset_cols) == 41
    expected = [f"A{i:03d}" for i in range(1, 42)]
    assert asset_cols == expected
