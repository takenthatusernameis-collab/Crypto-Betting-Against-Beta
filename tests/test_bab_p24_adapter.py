"""Acceptance tests for P24 WP3: the licensed-data adapter dry run.

These tests are the claim that ``scripts/bab_licensed_adapter.py`` reads the
maintainer-supplied offline schema fixture ``tests/fixtures/licensed_price_schema.csv``
(never the network), validates it against the committed P21 universe contract
and the committed P23/P24 charters, and publishes
``research_state/bab_p24/adapter_dryrun.{json,md}`` without regenerating or
editing any committed P21/P22/P23/P24 artifact.

They prove the mechanical contract the charter declares:

* the fixture is a well-formed 5-row x 43-column licensed schema
  (``date``, ``BTC``, ``A001``..``A041``) with no missing cells;
* the column contract is *derived* from committed P21 JSON
  (``assets``/``benchmark``), never hand-typed;
* the artifact's numeric block resolves to committed P21/P23/P24 JSON leaves;
* the dry run never touches the network and never rewrites its inputs;
* a malformed fixture is rejected (``valid=False`` with machine-readable
  errors) -- a validator that silently accepts missing cells is a failed gate;
* committed JSON equals a fresh build, markdown equals the renderer output, and
  a second build is byte-identical;
* verdict strings: synthetic, not market evidence, no-go for market.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from scripts import bab_licensed_adapter as adapter

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "bab_licensed_adapter.py"
TEST_PATH = Path(__file__).resolve()
JSON_PATH = REPO_ROOT / "research_state/bab_p24/adapter_dryrun.json"
MD_PATH = REPO_ROOT / "research_state/bab_p24/adapter_dryrun.md"
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "licensed_price_schema.csv"
P21_UNIVERSE_PATH = REPO_ROOT / "research_state/bab_p21" / "universe.json"
P23_CHARTER_PATH = REPO_ROOT / "research_state/bab_p23" / "charter.json"
P24_CHARTER_PATH = REPO_ROOT / "research_state/bab_p24" / "charter.json"

FORBIDDEN_BUILDERS = (
    "build_universe",
    "build_rank_eval",
    "build_null_battery",
    "build_impact_surface",
    "build_capacity",
    "build_significance",
    "build_synthetic_universe",
    "build_breadth_ladder",
    "build_beta_drift",
    "build_short_haircut",
    "build_regime_split",
    "build_hysteresis_ladder",
)

NETWORK_MODULES = ("urllib", "requests", "httpx", "socket", "aiohttp", "ccxt")

ARTIFACT_KEYS = {"columns", "errors", "provenance", "row_count", "schema", "valid"}
VALIDATION_KEYS = {
    "column_names_match",
    "columns_actual",
    "columns_expected",
    "date_start",
    "date_start_matches_universe",
    "dates_strictly_increasing",
    "errors",
    "min_rows_met",
    "nan_columns",
    "non_numeric_columns",
    "non_positive_columns",
    "rows",
    "valid",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _frame(**overrides) -> pd.DataFrame:
    return pd.read_csv(FIXTURE_PATH).assign(**overrides)


@pytest.fixture(scope="module")
def payload() -> dict:
    return _load(JSON_PATH)


@pytest.fixture(scope="module")
def universe() -> dict:
    return _load(P21_UNIVERSE_PATH)


@pytest.fixture(scope="module")
def p24_charter() -> dict:
    return _load(P24_CHARTER_PATH)


@pytest.fixture(scope="module")
def p23_charter() -> dict:
    return _load(P23_CHARTER_PATH)


# --------------------------------------------------------------------------- #
# Deliverables and static contract
# --------------------------------------------------------------------------- #
def test_deliverables_exist() -> None:
    for path in (SCRIPT_PATH, JSON_PATH, MD_PATH, FIXTURE_PATH):
        assert path.is_file(), f"missing deliverable {path}"


def test_artifact_top_level_keys(payload: dict) -> None:
    assert set(payload) == ARTIFACT_KEYS
    assert payload["schema"] == "bab_p24.adapter_dryrun/1"
    assert set(payload["provenance"]["validation"]) == VALIDATION_KEYS


def test_script_ast_never_imports_network() -> None:
    tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in NETWORK_MODULES
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".")[0] not in NETWORK_MODULES


def test_test_ast_never_calls_p21_p24_builders() -> None:
    tree = ast.parse(TEST_PATH.read_text(encoding="utf-8"))
    imported: set[str] = set()
    called: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[-1] for alias in node.names)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            called.add(node.func.id)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            called.add(node.func.attr)
    assert called.isdisjoint(FORBIDDEN_BUILDERS)
    assert imported.isdisjoint(FORBIDDEN_BUILDERS)


def test_script_does_not_silently_swallow_missing_cells() -> None:
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "if frame.isna().any().any():\n        pass" not in source
    assert "nan_columns" in source


# --------------------------------------------------------------------------- #
# Fixture is a well-formed licensed schema
# --------------------------------------------------------------------------- #
def test_fixture_columns_match_committed_p21_contract(universe: dict) -> None:
    frame = pd.read_csv(FIXTURE_PATH)
    provenance = universe["provenance"]
    expected = ["date", provenance["benchmark"], *universe["assets"]]
    assert list(frame.columns) == expected
    assert len(frame.columns) == provenance["assets"] + 2


def test_fixture_has_no_missing_or_non_numeric_cells() -> None:
    frame = pd.read_csv(FIXTURE_PATH)
    assert not frame.isna().any().any()
    assert frame.shape == (5, 43)
    for column in frame.columns:
        if column == "date":
            continue
        assert (pd.to_numeric(frame[column]) > 0).all()


def test_fixture_dates_start_at_committed_universe_start(universe: dict) -> None:
    dates = pd.to_datetime(pd.read_csv(FIXTURE_PATH)["date"]).dt.strftime("%Y-%m-%d")
    assert list(dates) == sorted(dates)
    assert len(set(dates)) == len(dates)
    assert dates.iloc[0] == universe["provenance"]["date_start"]


# --------------------------------------------------------------------------- #
# Artifact provenance resolves to committed JSON
# --------------------------------------------------------------------------- #
def test_artifact_is_valid_and_error_free(payload: dict) -> None:
    assert payload["valid"] is True
    assert payload["errors"] == []
    assert payload["provenance"]["validation"]["valid"] is True
    assert payload["provenance"]["validation"]["errors"] == []
    assert payload["row_count"] == pd.read_csv(FIXTURE_PATH).shape[0]


def test_artifact_columns_match_committed_p21_universe(
    payload: dict, universe: dict
) -> None:
    expected = ["date", universe["provenance"]["benchmark"], *universe["assets"]]
    assert payload["columns"] == expected
    assert payload["provenance"]["validation"]["column_names_match"] is True


def test_artifact_numeric_contract_matches_p21_provenance(
    payload: dict, universe: dict
) -> None:
    contract = payload["provenance"]["numeric_contract"]
    provenance = universe["provenance"]
    assert contract["assets"] == provenance["assets"]
    assert contract["benchmark"] == provenance["benchmark"]
    assert contract["decimals"] == provenance["decimals"]
    assert contract["date_start"] == provenance["date_start"]
    assert contract["universe_seed"] == provenance["seed"]
    assert contract["expected_columns"] == provenance["assets"] + 2


def test_artifact_charter_chain_matches_committed_files(
    payload: dict, p24_charter: dict, p23_charter: dict, universe: dict
) -> None:
    provenance = payload["provenance"]
    assert provenance["p24_charter_path"] == "research_state/bab_p24/charter.json"
    assert provenance["p24_charter_schema"] == p24_charter["schema"]
    assert provenance["p23_charter_path"] == "research_state/bab_p23/charter.json"
    assert provenance["p23_charter_schema"] == p23_charter["schema"]
    assert provenance["p21_universe_path"] == "research_state/bab_p21/universe.json"
    assert provenance["p21_universe_schema"] == universe["schema"]
    assert (
        provenance["licensed_price_csv_schema"]
        == p24_charter["charter"]["licensed_price_csv_schema"]
    )
    assert provenance["fixture_path"] == provenance["licensed_price_csv_schema"]
    assert provenance["fixture_matches_charter_schema"] is True


def test_artifact_offline_and_holdout_flags(
    payload: dict, p24_charter: dict
) -> None:
    provenance = payload["provenance"]
    charter = p24_charter["charter"]
    assert provenance["network_used"] is False
    assert provenance["dry_run"] is True
    assert provenance["synthetic"] is True
    assert provenance["licensed_data_required"] is charter["licensed_data_required"]
    assert provenance["holdout_before_tuning"] is charter["holdout_before_tuning"]
    assert provenance["not_market_evidence"] is charter["not_market_evidence"]
    assert provenance["fixture_sha256"] == _sha(FIXTURE_PATH)


def test_no_go_verdict_restated_from_committed_charters(
    payload: dict, p24_charter: dict, p23_charter: dict
) -> None:
    provenance = payload["provenance"]
    assert provenance["no_go_for_market"] is True
    assert provenance["no_go_for_market"] is p24_charter["provenance"]["no_go_for_market"]
    assert (
        provenance["p23_no_go_for_market"]
        is p23_charter["provenance"]["p22_verdict"]["no_go_for_market"]
    )


def test_verdict_strings_are_exact(payload: dict) -> None:
    verdict = payload["provenance"]["verdict"]
    assert verdict == {
        "signal": "signal",
        "noise": "noise",
        "no_go_for_market": "no-go for market",
        "controlled_synthetic": "controlled synthetic",
        "not_market_evidence": "not market evidence",
    }


# --------------------------------------------------------------------------- #
# Determinism: committed artifacts equal a fresh build
# --------------------------------------------------------------------------- #
def test_committed_json_equals_fresh_build(payload: dict) -> None:
    assert adapter.build_adapter_dryrun() == payload


def test_committed_markdown_equals_renderer(payload: dict) -> None:
    assert MD_PATH.read_text(encoding="utf-8") == adapter.render_markdown(payload)


def test_second_build_is_byte_identical(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    adapter.write_artifacts(
        adapter.build_adapter_dryrun(), first / "a.json", first / "a.md"
    )
    adapter.write_artifacts(
        adapter.build_adapter_dryrun(), second / "a.json", second / "a.md"
    )
    for name in ("a.json", "a.md"):
        assert _sha(first / name) == _sha(second / name)


def test_main_never_edits_inputs_or_artifacts() -> None:
    watched = (
        FIXTURE_PATH,
        P21_UNIVERSE_PATH,
        P23_CHARTER_PATH,
        P24_CHARTER_PATH,
        JSON_PATH,
        MD_PATH,
    )
    before = {path: _sha(path) for path in watched}
    adapter.main()
    after = {path: _sha(path) for path in watched}
    assert before == after


# --------------------------------------------------------------------------- #
# A malformed fixture must be rejected, never silently accepted
# --------------------------------------------------------------------------- #
def test_missing_cells_are_rejected(universe: dict) -> None:
    frame = _frame()
    frame.loc[1, "A041"] = None
    result = adapter.validate_fixture(frame, universe)
    assert result["valid"] is False
    assert "A041" in result["nan_columns"]
    assert any("missing cells" in error for error in result["errors"])


def test_missing_column_is_rejected(universe: dict) -> None:
    frame = pd.read_csv(FIXTURE_PATH).drop(columns=["A017"])
    result = adapter.validate_fixture(frame, universe)
    assert result["valid"] is False
    assert result["column_names_match"] is False
    assert any("column mismatch" in error for error in result["errors"])


def test_non_numeric_price_is_rejected(universe: dict) -> None:
    frame = _frame()
    frame["A005"] = frame["A005"].astype(object)
    frame.loc[0, "A005"] = "n/a"
    result = adapter.validate_fixture(frame, universe)
    assert result["valid"] is False
    assert "A005" in result["non_numeric_columns"]


def test_out_of_order_dates_are_rejected(universe: dict) -> None:
    frame = _frame()
    frame.loc[0, "date"] = "2024-01-09"
    result = adapter.validate_fixture(frame, universe)
    assert result["valid"] is False
    assert result["dates_strictly_increasing"] is False


def test_non_positive_price_is_rejected(universe: dict) -> None:
    frame = _frame()
    frame.loc[2, "A031"] = 0.0
    result = adapter.validate_fixture(frame, universe)
    assert result["valid"] is False
    assert "A031" in result["non_positive_columns"]


def test_too_few_rows_is_rejected(universe: dict) -> None:
    frame = pd.read_csv(FIXTURE_PATH).head(1)
    result = adapter.validate_fixture(frame, universe)
    assert result["valid"] is False
    assert result["min_rows_met"] is False


def test_malformed_fixture_yields_invalid_artifact(tmp_path: Path, universe: dict) -> None:
    frame = pd.read_csv(FIXTURE_PATH).head(1)
    path = tmp_path / "broken.csv"
    frame.to_csv(path, index=False)
    broken = adapter.build_adapter_dryrun(fixture_path=str(path))
    assert broken["valid"] is False
    assert broken["errors"]
    assert broken["provenance"]["network_used"] is False
    assert broken["provenance"]["dry_run"] is True


# --------------------------------------------------------------------------- #
# Markdown states the verdict it must state
# --------------------------------------------------------------------------- #
def test_markdown_states_no_go_and_offline() -> None:
    text = MD_PATH.read_text(encoding="utf-8")
    assert "no-go for market" in text
    assert "not market evidence" in text
    assert "network_used=false" in text
    assert "tests/fixtures/licensed_price_schema.csv" in text
    assert "adapter_dryrun/1" in text
