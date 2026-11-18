"""Acceptance tests for P20 WP0: the deterministic research sweep harness.

These tests are the claim that ``research_state/bab_p20/sweep.json`` and
``sweep.md`` are reproducible evidence rather than hand-typed numbers.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

from scripts import bab_research_sweep as sweep_mod

REPO_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = REPO_ROOT / "research_state/bab_p20/sweep.json"
MD_PATH = REPO_ROOT / "research_state/bab_p20/sweep.md"
SCRIPT_PATH = REPO_ROOT / "scripts/bab_research_sweep.py"
NUMERIC_TOKEN = re.compile(r"-?\d+\.\d+")
FORBIDDEN_RANK_TOKENS = ("rank_min_leg_beta", "rank_max_gross", "rank")


@pytest.fixture(scope="module")
def sweep() -> dict:
    return sweep_mod.build_sweep()


def _serialize(sweep: dict) -> bytes:
    return (json.dumps(sweep, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _numeric_values(node) -> list:
    values = []
    if isinstance(node, dict):
        for value in node.values():
            values.extend(_numeric_values(value))
    elif isinstance(node, list):
        for value in node:
            values.extend(_numeric_values(value))
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        values.append(round(float(node), sweep_mod.DECIMALS))
    return values


def test_sweep_completes_under_ten_seconds() -> None:
    started = time.perf_counter()
    result = sweep_mod.build_sweep()
    elapsed = time.perf_counter() - started
    assert len(result["rows"]) == 80
    assert elapsed < 10.0, f"sweep took {elapsed:.2f}s"


def test_build_sweep_is_byte_identical_across_calls() -> None:
    first = _serialize(sweep_mod.build_sweep())
    second = _serialize(sweep_mod.build_sweep())
    assert first == second
    assert hashlib.sha256(first).hexdigest() == hashlib.sha256(second).hexdigest()


def test_script_reruns_produce_identical_file_hashes(tmp_path: Path) -> None:
    hashes = []
    for _ in range(2):
        subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        hashes.append(
            (
                hashlib.sha256(JSON_PATH.read_bytes()).hexdigest(),
                hashlib.sha256(MD_PATH.read_bytes()).hexdigest(),
            )
        )
    assert hashes[0] == hashes[1]


def test_every_row_is_complete_and_finite(sweep: dict) -> None:
    rows = sweep["rows"]
    assert len(rows) == 5 * 2 * 4 * 2 == 80
    assert {tuple(sorted(row)) for row in rows} == {tuple(sorted(sweep_mod.ROW_FIELDS))}

    combinations = {
        (
            row["beta_window"],
            row["long_quantile"],
            row["short_quantile"],
            row["transaction_costs"],
            row["beta_neutral"],
        )
        for row in rows
    }
    assert len(combinations) == 80

    null_reason_keys = set(sweep["provenance"]["null_field_reasons"])
    for row in rows:
        assert row["weighting"] == "equal"
        for field in sweep_mod.ROW_FIELDS:
            value = row[field]
            if isinstance(value, (bool, str)):
                continue
            if value is None:
                assert field in null_reason_keys, f"{field} is null without a documented reason"
                continue
            assert isinstance(value, (int, float))
            assert math.isfinite(float(value))


def test_provenance_is_present_and_true(sweep: dict) -> None:
    provenance = sweep["provenance"]
    assert provenance["fixture_path"] == "tests/fixtures/real_market_prices.csv"
    assert re.fullmatch(r"[0-9a-f]{64}", provenance["fixture_sha256"])
    assert provenance["price_rows"] == 399
    assert provenance["return_rows"] == 398
    assert provenance["date_first"] == "2021-01-04"
    assert provenance["date_last"] == "2022-07-15"
    assert provenance["synthetic"] is True
    assert provenance["seed"] == 20261028
    assert provenance["known_gap"] == "2021-09-17"
    assert provenance["nan_columns"] == ["DEL"]
    assert provenance["in_sample_windows"] == [180]
    assert "not real market data" in provenance["synthetic_fixture"]
    assert sweep["grid"]["configurations"] == 80
    assert sweep["grid"]["weighting"] == ["equal"]


def test_markdown_is_rendered_from_json(sweep: dict) -> None:
    assert MD_PATH.read_text(encoding="utf-8") == sweep_mod.render_markdown(sweep)


def test_markdown_numeric_tokens_all_trace_to_json(sweep: dict) -> None:
    allowed = set(_numeric_values(sweep))
    tokens = NUMERIC_TOKEN.findall(MD_PATH.read_text(encoding="utf-8"))
    assert tokens, "markdown table contains no numeric cells"
    for token in tokens:
        assert round(float(token), sweep_mod.DECIMALS) in allowed, f"hand-typed value {token}"


def test_no_rank_leakage(sweep: dict) -> None:
    payload = json.dumps(sweep, sort_keys=True).lower()
    markdown = MD_PATH.read_text(encoding="utf-8").lower()
    for token in FORBIDDEN_RANK_TOKENS:
        assert token not in payload
        assert token not in markdown
    assert all(row["weighting"] == "equal" for row in sweep["rows"])


def test_artifact_contract_and_idempotent_write(sweep: dict) -> None:
    artifact = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert set(artifact) == {"schema", "provenance", "grid", "rows"}
    assert artifact["schema"] == "bab_p20.sweep/1"

    before = hashlib.sha256(JSON_PATH.read_bytes()).hexdigest()
    sweep_mod.write_artifacts(sweep)
    after = hashlib.sha256(JSON_PATH.read_bytes()).hexdigest()
    assert before == after

    assert json.loads(_serialize(sweep).decode("utf-8")) == artifact


def test_default_config_row_matches_certified_baseline(sweep: dict) -> None:
    matches = [
        row
        for row in sweep["rows"]
        if row["beta_window"] == 90
        and row["long_quantile"] == 0.3
        and row["transaction_costs"] == 0.001
        and row["beta_neutral"] is True
    ]
    assert len(matches) == 1
    row = matches[0]
    assert row["wealth"] == pytest.approx(0.705655, abs=1e-6)
    assert row["sharpe"] == pytest.approx(-0.725483, abs=1e-6)
    assert row["realized_beta"] == pytest.approx(0.058754, abs=1e-6)
