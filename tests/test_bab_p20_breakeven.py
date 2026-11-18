"""Acceptance tests for P20 WP5: cost/turnover break-even harness.

These tests are the claim that ``research_state/bab_p20/breakeven.json`` and
``breakeven.md`` are reproducible evidence rather than hand-typed numbers.

The original WP5 specification asked for a cross-row monotonicity claim
("break-even tc is non-increasing as uncosted Sharpe increases"). That claim is
mathematically false once turnover varies across configurations: cost drag is
``tc * turnover``, so a slightly higher Sharpe with materially higher turnover
breaks even at a *lower* cost. The measured fixture counterexample is
``(beta_window=60, q=0.2)`` with Sharpe 0.834694 and break-even 0.004609 versus
``(beta_window=90, q=0.2)`` with Sharpe 0.810267 and break-even 0.005078.

The provable, load-bearing monotone law is therefore tested instead, per row:
for a fixed configuration the costed Sharpe is non-increasing in ``tc``, so the
zero crossing is unique and the fixed 6-iteration bisection brackets it.
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

from scripts import bab_breakeven as be
from strategies.betting_against_beta import BABStrategy, metrics
from strategies.betting_against_beta.data_loader import load_prices

REPO_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = REPO_ROOT / "research_state/bab_p20/breakeven.json"
MD_PATH = REPO_ROOT / "research_state/bab_p20/breakeven.md"
SCRIPT_PATH = REPO_ROOT / "scripts/bab_breakeven.py"
FIXTURE = REPO_ROOT / "tests/fixtures/real_market_prices.csv"
NUMERIC_TOKEN = re.compile(r"-?\d+\.\d+")
FORBIDDEN_RANK_TOKENS = ("rank_min_leg_beta", "rank_max_gross", "rank")
TC_LADDER = (0.0, 0.001, 0.0025, 0.005, 0.01)


@pytest.fixture(scope="module")
def payload() -> dict:
    return be.build_breakeven()


@pytest.fixture(scope="module")
def returns():
    return load_prices(FIXTURE, benchmark="BTC")


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
        values.append(round(float(node), be.DECIMALS))
    return values


def _sharpe(returns, beta_window: int, quantile: float, transaction_costs: float) -> float:
    result = BABStrategy(
        benchmark="BTC",
        beta_window=beta_window,
        min_observations=60,
        long_quantile=quantile,
        short_quantile=quantile,
        transaction_costs=transaction_costs,
        beta_neutral=True,
    ).run(returns_df=returns)
    return float(metrics.sharpe_ratio(result.backtest["returns"]))


def _key(row: dict) -> str:
    return f"{row['beta_window']}|{row['long_quantile']}"


def test_rows_cover_the_equal_weight_beta_neutral_grid(payload: dict) -> None:
    rows = payload["rows"]
    assert len(rows) == 5 * 2 == 10
    assert {tuple(sorted(row)) for row in rows} == {tuple(sorted(be.ROW_FIELDS))}
    combos = {
        (row["beta_window"], row["long_quantile"], row["short_quantile"]) for row in rows
    }
    assert len(combos) == 10
    assert all(row["long_quantile"] == row["short_quantile"] for row in rows)
    assert payload["provenance"]["weighting"] == "equal"
    assert payload["provenance"]["beta_neutral"] is True


def test_per_row_sharpe_is_monotone_non_increasing_in_tc(payload: dict, returns) -> None:
    for row in payload["rows"]:
        curve = [
            _sharpe(returns, row["beta_window"], row["long_quantile"], tc) for tc in TC_LADDER
        ]
        assert curve[0] == pytest.approx(row["uncosted_sharpe"], abs=1e-6)
        for before, after in zip(curve, curve[1:]):
            assert after <= before + 1e-12, f"Sharpe rose with cost: {curve}"


def test_defined_rows_bracket_the_zero_crossing(payload: dict, returns) -> None:
    defined = [row for row in payload["rows"] if row["break_even_tc"] is not None]
    assert len(defined) == 6
    for row in defined:
        tc = row["break_even_tc"]
        below = max(tc - 0.001, be.TC_LO)
        above = min(tc + 0.001, be.TC_HI)
        below_sharpe = _sharpe(returns, row["beta_window"], row["long_quantile"], below)
        above_sharpe = _sharpe(returns, row["beta_window"], row["long_quantile"], above)
        at_sharpe = _sharpe(returns, row["beta_window"], row["long_quantile"], tc)
        assert below_sharpe > 0.0, f"{_key(row)} does not bracket: {below_sharpe}"
        assert above_sharpe < 0.0, f"{_key(row)} does not bracket: {above_sharpe}"
        assert at_sharpe == pytest.approx(row["sharpe_at_break_even"], abs=1e-3)
        assert abs(at_sharpe) < 0.05, f"{_key(row)} root is not near zero: {at_sharpe}"


def test_zero_cost_identity_matches_sweep_and_direct_run(payload: dict, returns) -> None:
    sweep = json.loads(
        (REPO_ROOT / "research_state/bab_p20/sweep.json").read_text(encoding="utf-8")
    )
    sweep_uncosted = {
        (row["beta_window"], row["long_quantile"]): row["sharpe"]
        for row in sweep["rows"]
        if row["weighting"] == "equal"
        and row["beta_neutral"] is True
        and row["transaction_costs"] == 0.0
        and row["long_quantile"] == row["short_quantile"]
    }
    for row in payload["rows"]:
        config = (row["beta_window"], row["long_quantile"])
        raw = be._run_config(returns, config[0], config[1], 0.0)["sharpe"]
        assert raw == pytest.approx(
            _sharpe(returns, config[0], config[1], 0.0), abs=1e-12
        )
        assert raw == pytest.approx(sweep_uncosted[config], abs=1e-6)
        assert row["uncosted_sharpe"] == pytest.approx(raw, abs=1e-6)


def test_bisection_runs_exactly_six_evaluations() -> None:
    positive_calls = []

    def always_positive(tc: float) -> float:
        positive_calls.append(tc)
        return 1.0

    result = be.bisect_break_even(always_positive)
    assert len(positive_calls) == 6
    assert len(result["trace"]) == 6
    assert result["iterations"] == 6
    assert result["hi"] == pytest.approx(be.TC_HI)
    assert result["lo"] == pytest.approx(be.TC_HI * (1.0 - 2.0 ** -6))
    assert result["tc"] == pytest.approx((result["lo"] + result["hi"]) / 2.0)

    negative_calls = []

    def always_negative(tc: float) -> float:
        negative_calls.append(tc)
        return -1.0

    result = be.bisect_break_even(always_negative)
    assert len(negative_calls) == 6
    assert result["lo"] == pytest.approx(be.TC_LO)
    assert result["tc"] == pytest.approx(be.TC_HI / 2.0 ** 7)


def test_bisection_trace_halves_the_bracket_every_iteration() -> None:
    result = be.bisect_break_even(lambda tc: 0.5 - 60.0 * tc)
    width = be.TC_HI - be.TC_LO
    for step in result["trace"]:
        assert step["mid"] == pytest.approx((step["lo"] + step["hi"]) / 2.0)
        assert step["hi"] - step["lo"] == pytest.approx(width)
        width /= 2.0
    assert result["tc"] == pytest.approx((result["lo"] + result["hi"]) / 2.0)


def test_bisection_converges_within_the_documented_resolution() -> None:
    root = 0.5 / 60.0
    result = be.bisect_break_even(lambda tc: 0.5 - 60.0 * tc)
    resolution = (be.TC_HI - be.TC_LO) / 2.0 ** be.BISECTION_ITERATIONS
    assert abs(result["tc"] - root) <= resolution
    with pytest.raises(ValueError):
        be.bisect_break_even(lambda tc: 1.0, iterations=0)
    with pytest.raises(ValueError):
        be.bisect_break_even(lambda tc: 1.0, lo=0.01, hi=0.01)


def test_build_breakeven_is_byte_identical_across_calls() -> None:
    first = _serialize(be.build_breakeven())
    second = _serialize(be.build_breakeven())
    assert first == second
    assert hashlib.sha256(first).hexdigest() == hashlib.sha256(second).hexdigest()


def test_script_reruns_produce_identical_file_hashes() -> None:
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


def test_null_fields_are_documented_and_complete(payload: dict) -> None:
    provenance = payload["provenance"]
    reasons = provenance["null_field_reasons"]
    assert hasattr(be, "REASON_NON_POSITIVE")
    for row in payload["rows"]:
        companions = [row[field] for field in be.COMPANION_FIELDS]
        if row["break_even_tc"] is None:
            assert all(value is None for value in companions)
            entry = reasons[_key(row)]
            assert entry["fields"] == list(be.COMPANION_FIELDS)
            assert entry["reason"]
            expected = (
                be.REASON_NON_POSITIVE
                if row["uncosted_sharpe"] <= 0.0
                else be.REASON_NO_CROSSING
            )
            assert entry["reason"] == expected
        else:
            assert _key(row) not in reasons
            for value in companions:
                assert isinstance(value, (int, float))
                assert math.isfinite(float(value))


def test_provenance_is_present_and_true(payload: dict) -> None:
    provenance = payload["provenance"]
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
    assert "bisection" in provenance["method"]
    assert provenance["bisection"]["iterations"] == 6
    assert provenance["bisection"]["lo"] == 0.0
    assert provenance["bisection"]["hi"] == 0.01
    for definition in provenance["metric_definitions"].values():
        assert definition


def test_markdown_is_rendered_from_json(payload: dict) -> None:
    assert MD_PATH.read_text(encoding="utf-8") == be.render_markdown(payload)


def test_markdown_numeric_tokens_all_trace_to_json(payload: dict) -> None:
    allowed = set(_numeric_values(payload))
    tokens = NUMERIC_TOKEN.findall(MD_PATH.read_text(encoding="utf-8"))
    assert tokens, "markdown table contains no numeric cells"
    for token in tokens:
        assert round(float(token), be.DECIMALS) in allowed, f"hand-typed value {token}"


def test_no_rank_leakage_and_no_real_data_claim(payload: dict) -> None:
    payload_text = json.dumps(payload, sort_keys=True).lower()
    markdown = MD_PATH.read_text(encoding="utf-8").lower()
    for token in FORBIDDEN_RANK_TOKENS:
        assert token not in payload_text
        assert token not in markdown
    assert "not real market data" in markdown


def test_artifact_contract_and_idempotent_write(payload: dict) -> None:
    artifact = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert set(artifact) == {"schema", "provenance", "rows"}
    assert artifact["schema"] == "bab_p20.breakeven/1"

    before = hashlib.sha256(JSON_PATH.read_bytes()).hexdigest()
    be.write_artifacts(payload)
    after = hashlib.sha256(JSON_PATH.read_bytes()).hexdigest()
    assert before == after

    assert json.loads(_serialize(payload).decode("utf-8")) == artifact


def test_runtime_under_thirty_seconds() -> None:
    started = time.perf_counter()
    payload = be.build_breakeven()
    elapsed = time.perf_counter() - started
    assert len(payload["rows"]) == 10
    assert elapsed < 30.0, f"break-even harness took {elapsed:.2f}s"
