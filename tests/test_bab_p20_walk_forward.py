"""Acceptance tests for P20 WP3: the deterministic walk-forward (out-of-sample) harness.

These tests are the claim that ``research_state/bab_p20/walk_forward.json`` and
``walk_forward.md`` are reproducible out-of-sample evidence rather than an
in-sample grid winner quoted as a result. Selection happens on train rows only;
the test slice is never read during selection.
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

import pandas as pd
import pytest

from scripts import bab_walk_forward as wf_mod
from strategies.betting_against_beta.data_loader import load_prices

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = REPO_ROOT / "tests/fixtures/real_market_prices.csv"
JSON_PATH = REPO_ROOT / "research_state/bab_p20/walk_forward.json"
MD_PATH = REPO_ROOT / "research_state/bab_p20/walk_forward.md"
SCRIPT_PATH = REPO_ROOT / "scripts/bab_walk_forward.py"
NUMERIC_TOKEN = re.compile(r"-?\d+\.\d+")
FORBIDDEN_RANK_TOKENS = ("rank", "rank_min_leg_beta", "rank_max_gross")


@pytest.fixture(scope="module")
def artifact() -> dict:
    return wf_mod.build_walk_forward()


def _load_returns() -> pd.DataFrame:
    path = FIXTURE
    prices = pd.read_csv(path)
    return load_prices(path, benchmark="BTC")


def _serialize(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _numeric_values(node) -> list:
    values = []
    if isinstance(node, dict):
        for value in node.values():
            values.extend(_numeric_values(value))
    elif isinstance(node, list):
        for value in node:
            values.extend(_numeric_values(value))
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        values.append(round(float(node), wf_mod.DECIMALS))
    return values


def test_walk_forward_completes_under_twenty_seconds(artifact: dict) -> None:
    started = time.perf_counter()
    wf_mod.build_walk_forward()
    elapsed = time.perf_counter() - started
    assert len(artifact["aggregate"]["folds"]) == 5
    assert all(fold["n_test"] == 40 for fold in artifact["aggregate"]["folds"])
    assert elapsed < 20.0, f"walk-forward took {elapsed:.2f}s"


def test_build_walk_forward_is_byte_identical_across_calls() -> None:
    first = _serialize(wf_mod.build_walk_forward())
    second = _serialize(wf_mod.build_walk_forward())
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


def test_fold_separation_and_geometry(artifact: dict) -> None:
    folds = artifact["aggregate"]["folds"]
    assert len(folds) == 5
    expected_train_end = wf_mod.TRAIN_ROWS
    for fold in folds:
        assert fold["train_start"] == 0
        assert fold["train_end"] == expected_train_end
        assert fold["test_start"] == expected_train_end
        assert fold["test_end"] == expected_train_end + wf_mod.TEST_ROWS
        assert fold["n_train"] == expected_train_end
        assert fold["n_test"] == wf_mod.TEST_ROWS
        # Strict separation: max(train_index) < min(test_index).
        assert fold["train_end"] - 1 < fold["test_start"]
        wf_mod.assert_train_before_test(
            range(fold["train_start"], fold["train_end"]),
            range(fold["test_start"], fold["test_end"]),
        )
        expected_train_end += wf_mod.TEST_ROWS
    assert folds[-1]["test_end"] - 1 == wf_mod.LAST_TEST_INDEX  # 379


def test_lookahead_guard_rejects_misordered_index() -> None:
    wf_mod.assert_train_before_test(range(0, 180), range(180, 220))  # valid split
    with pytest.raises(ValueError):
        wf_mod.assert_train_before_test(range(0, 180), range(179, 219))  # overlap
    with pytest.raises(ValueError):  # deliberately misordered: test before train
        wf_mod.assert_train_before_test([50, 100, 150], [1, 2, 3])


def test_selection_independence_from_test_slice() -> None:
    """Corrupting a fold's test-slice returns must not change what train selects."""
    returns = _load_returns()
    for k in range(wf_mod.N_FOLDS):
        _, train_end, test_start, test_end = wf_mod._fold_bounds(k)
        base = wf_mod.select_on_train(returns, train_end)
        corrupted = returns.copy()
        corrupted.iloc[test_start:test_end] = 0.001
        variant = wf_mod.select_on_train(corrupted, train_end)
        assert base == variant, f"fold {k} selection changed after corrupting its test slice"


def test_end_to_end_test_slice_does_not_change_fold_zero_selection(tmp_path: Path) -> None:
    """End-to-end: returns inside fold 0's test window are replaced with a
    constant; fold 0's train window is upstream of it, so its selection must be
    byte-identical. Other folds are allowed to differ (their train windows
    overlap the corrupted rows) and are not asserted.
    """
    base = wf_mod.build_walk_forward()
    prices = pd.read_csv(FIXTURE)
    corrupted = prices.copy()
    anchor_row = wf_mod.TRAIN_ROWS - 1  # last train row of fold 0 (returns row 179 uses price 180)
    for column in corrupted.columns:
        if column == "date":
            continue
        anchor_value = pd.to_numeric(corrupted.at[anchor_row, column], errors="coerce")
        if pd.isna(anchor_value):
            continue
        # Corrupt price rows [181, 220] so returns [180, 221) (fold 0's test
        # window) change while train returns [0, 180) (prices [0, 180]) stay
        # byte-identical: load_prices drops the first pct_change row, so
        # return i = price[i+1] / price[i] - 1.
        for offset in range(2, wf_mod.TEST_ROWS + 2):
            corrupted.at[anchor_row + offset, column] = float(anchor_value) * (1.0 + 0.001 * offset)
    path = tmp_path / "corrupted_prices.csv"
    corrupted.to_csv(path, index=False)
    variant = wf_mod.build_walk_forward(str(path))
    base_fold = base["aggregate"]["folds"][0]
    variant_fold = variant["aggregate"]["folds"][0]
    assert base_fold["selected_beta_window"] == variant_fold["selected_beta_window"]
    assert base_fold["selected_long_quantile"] == variant_fold["selected_long_quantile"]
    assert base_fold["selected_short_quantile"] == variant_fold["selected_short_quantile"]
    assert base_fold["train_sharpe"] == variant_fold["train_sharpe"]


def test_honesty_and_schema(artifact: dict) -> None:
    assert artifact["schema"] == "bab_p20.walk_forward/1"
    assert set(artifact) == {"schema", "provenance", "aggregate", "folds"}
    assert set(artifact["aggregate"]) == {
        "mean_oos_sharpe",
        "median_oos_sharpe",
        "fraction_positive_oos_sharpe",
        "total_oos_rows",
        "folds",
        "candidates_evaluated",
    }
    assert artifact["aggregate"]["candidates_evaluated"] == 40
    assert artifact["aggregate"]["total_oos_rows"] == 200

    provenance = artifact["provenance"]
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
    assert "not real market data" in provenance["synthetic_fixture"]
    assert isinstance(provenance["selection_rule"], str) and provenance["selection_rule"]
    assert isinstance(provenance["no_lookahead"], str) and provenance["no_lookahead"]

    # No rank anywhere; equal-weight only; no beta_window=180 selected.
    payload_text = json.dumps(artifact, sort_keys=True).lower()
    markdown_text = MD_PATH.read_text(encoding="utf-8").lower()
    for token in FORBIDDEN_RANK_TOKENS:
        assert token not in payload_text, f"rank token {token} leaked into JSON"
        assert token not in markdown_text, f"rank token {token} leaked into markdown"
    assert wf_mod.WEIGHTING == "equal"
    for fold in artifact["aggregate"]["folds"]:
        assert fold["selected_beta_window"] in (30, 60, 90, 120)
        assert fold["selected_long_quantile"] in (0.2, 0.3)
        assert fold["selected_short_quantile"] in (0.2, 0.3)
        assert set(fold) == set(wf_mod.FOLD_FIELDS)

    # Every numeric field finite; any None carries a documented reason.
    null_reasons = set(provenance["null_field_reasons"])
    for fold in artifact["aggregate"]["folds"]:
        for field in wf_mod.FOLD_FIELDS:
            value = fold[field]
            if value is None:
                assert field in null_reasons, f"{field} is null without a documented reason"
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                assert math.isfinite(float(value)), f"{field} is non-finite: {value!r}"
    for field in ("mean_oos_sharpe", "median_oos_sharpe", "fraction_positive_oos_sharpe"):
        value = artifact["aggregate"][field]
        if value is None:
            assert field in null_reasons
        else:
            assert math.isfinite(float(value))


def test_markdown_is_rendered_from_json(artifact: dict) -> None:
    assert MD_PATH.read_text(encoding="utf-8") == wf_mod.render_markdown(artifact)


def test_markdown_numeric_tokens_all_trace_to_json(artifact: dict) -> None:
    allowed = set(_numeric_values(artifact))
    tokens = NUMERIC_TOKEN.findall(MD_PATH.read_text(encoding="utf-8"))
    assert tokens, "markdown table contains no numeric cells"
    for token in tokens:
        assert round(float(token), wf_mod.DECIMALS) in allowed, f"hand-typed value {token}"
