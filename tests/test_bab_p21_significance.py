"""Acceptance tests for P21 WP2: significance + deflation on the planted universe.

These tests are the claim that ``scripts/bab_significance.py`` produces a
deterministic, sha-pinned significance evaluation (planted/null x equal/rank)
on the committed WP0 universe, that the moving-block bootstrap (>= 2000
resamples, fixed seed) calibrates the null (no null book significant at the
documented nominal slack), that the planted effect is detected (significant,
bootstrap CI excluding zero), and that a deflated Sharpe correction is applied
for the 40-candidate P20 grid (hand-computed DSR unit case pinned).

They never touch the network, never edit product code, and never regenerate
the WP0 universe or WP1 rank_eval artifacts.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from scripts import bab_significance

REPO_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = REPO_ROOT / "research_state/bab_p21/significance.json"
MD_PATH = REPO_ROOT / "research_state/bab_p21/significance.md"
UNIVERSE_PATH = REPO_ROOT / "research_state/bab_p21/universe.json"

NOMINAL_SLACK = 0.05
NUMERIC_TOKEN = re.compile(r"-?\d+(?:\.\d+)?")

_VARIANTS = ("planted", "null")
_WEIGHTINGS = ("equal", "rank")


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def _book(payload: dict, variant: str, weighting: str) -> dict:
    for b in payload["books"]:
        if b["variant"] == variant and b["weighting"] == weighting:
            return b
    raise AssertionError(
        f"no book for variant={variant!r} weighting={weighting!r}"
    )


def test_schema_and_provenance(payload: dict) -> None:
    assert payload["schema"] == bab_significance.SCHEMA == "bab_p21.significance/1"
    prov = payload["provenance"]
    assert prov["synthetic"] is True
    assert "not real market data" in prov["note"]
    assert prov["universe_seed"] == 20261118
    assert prov["seed"] == 20261119
    assert prov["n_resamples"] >= 2000
    assert prov["block_length"] == 20
    assert prov["n_trials"] == 40
    assert prov["nominal_slack"] == NOMINAL_SLACK
    assert set(prov["panel_sha256"].keys()) == {"planted", "null"}
    cfg = prov["config"]
    assert cfg["benchmark"] == "BTC"
    assert cfg["beta_window"] == 90
    assert cfg["min_observations"] == 60
    assert cfg["long_quantile"] == 0.3
    assert cfg["short_quantile"] == 0.3
    assert cfg["transaction_costs"] == 0.0
    assert cfg["beta_neutral"] is True
    assert cfg["rank_min_leg_beta"] == 0.20
    assert cfg["rank_max_gross"] == 4.0
    assert prov["null_calibrated"] is True
    assert prov["planted_detected"] is True


def test_determinism_two_builds() -> None:
    first = json.dumps(bab_significance.build_significance(), indent=2, sort_keys=True)
    second = json.dumps(bab_significance.build_significance(), indent=2, sort_keys=True)
    assert first == second


def test_committed_json_matches_fresh_build() -> None:
    fresh = (
        json.dumps(bab_significance.build_significance(), indent=2, sort_keys=True) + "\n"
    )
    assert JSON_PATH.read_text(encoding="utf-8") == fresh


def test_universe_json_unchanged() -> None:
    from scripts import bab_synthetic_universe as u

    committed = UNIVERSE_PATH.read_text(encoding="utf-8")
    fresh = json.dumps(u.build_universe(), indent=2, sort_keys=True) + "\n"
    assert committed == fresh, "universe.json drifted from its generator"


def test_panel_sha256_matches_universe(payload: dict) -> None:
    universe = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    prov = payload["provenance"]
    for variant in _VARIANTS:
        assert prov["panel_sha256"][variant] == universe["panels"][variant]["sha256"]


def test_null_calibrated(payload: dict) -> None:
    for weighting in _WEIGHTINGS:
        book = _book(payload, "null", weighting)
        assert book["significant"] is False, f"null/{weighting} falsely significant"
        assert book["p_value"] >= NOMINAL_SLACK, (
            f"null/{weighting} p_value {book['p_value']} below nominal slack"
        )
        assert book["oos_sharpe"] <= book["critical_sharpe"], (
            f"null/{weighting} sharpe {book['oos_sharpe']} above critical "
            f"{book['critical_sharpe']}"
        )
        assert book["ci_excludes_zero"] is False


def test_planted_detected(payload: dict) -> None:
    for weighting in _WEIGHTINGS:
        book = _book(payload, "planted", weighting)
        assert book["significant"] is True, f"planted/{weighting} not detected"
        assert book["p_value"] < NOMINAL_SLACK, (
            f"planted/{weighting} p_value {book['p_value']} not below nominal slack"
        )
        assert book["oos_sharpe"] > book["critical_sharpe"], (
            f"planted/{weighting} sharpe {book['oos_sharpe']} below critical "
            f"{book['critical_sharpe']}"
        )
        assert book["ci_excludes_zero"] is True
        assert book["sharpe_bootstrap_p05"] > 0.0


def test_null_max_p_value(payload: dict) -> None:
    prov = payload["provenance"]
    null_p = [_book(payload, "null", w)["p_value"] for w in _WEIGHTINGS]
    assert prov["null_max_p_value"] == max(null_p)
    assert prov["null_max_p_value"] >= NOMINAL_SLACK


def test_n_resamples_minimum(payload: dict) -> None:
    for book in payload["books"]:
        assert book["n_resamples"] >= 2000


def test_dsr_hand_computed_unit_case() -> None:
    # delta=1.0, n=2, sigma0=1.0, gamma=0, kappa=3 (normal) -> z = 1.632993,
    # DSR = Phi(1.632993) = 0.9487647825701253 -> 0.948765 at 6 dp.
    value = bab_significance._deflated_sharpe(1.0, 0.0, 2, 1.0, 0.0, 3.0)
    assert round(value, 6) == 0.948765


def test_markdown_numbers_derived_from_json(payload: dict) -> None:
    json_text = json.dumps(payload, indent=2, sort_keys=True)
    markdown = MD_PATH.read_text(encoding="utf-8")
    assert markdown == bab_significance.render_markdown(payload)
    tokens = NUMERIC_TOKEN.findall(markdown)
    assert tokens
    missing = [token for token in tokens if token not in json_text]
    assert not missing, f"markdown numbers absent from JSON: {missing}"


def test_books_schema_keys(payload: dict) -> None:
    expected_keys = {
        "variant", "weighting", "oos_sharpe", "n_resamples", "seed",
        "block_length", "nominal_slack", "p_value", "significant",
        "critical_sharpe", "sharpe_bootstrap_mean", "sharpe_bootstrap_std",
        "sharpe_bootstrap_p05", "sharpe_bootstrap_p95", "ci_excludes_zero",
        "dsr", "dsr_p_value",
    }
    for book in payload["books"]:
        assert set(book.keys()) == expected_keys, (
            f"book keys {set(book.keys())} != {expected_keys}"
        )
