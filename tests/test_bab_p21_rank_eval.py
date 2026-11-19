"""Acceptance tests for P21 WP1: rank vs equal evaluation on the planted universe.

These tests are the claim that ``scripts/bab_rank_eval.py`` produces a
deterministic, sha-pinned four-book evaluation (planted/null x equal/rank)
on the committed WP0 universe, that rank mode is empirically active on the
planted universe (541 active rows, guards respected), that recovery exists
on planted and vanishes exactly on null for both books, and that the
committed artifacts match a fresh build byte-for-byte.

They never touch the network, never edit product code, and never regenerate
the WP0 universe artifact.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pytest

from scripts import bab_rank_eval
from strategies.betting_against_beta.config import BABConfig

REPO_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = REPO_ROOT / "research_state/bab_p21/rank_eval.json"
MD_PATH = REPO_ROOT / "research_state/bab_p21/rank_eval.md"
UNIVERSE_PATH = REPO_ROOT / "research_state/bab_p21/universe.json"

DEGENERATE_TOL = 1e-12
BETA_NEUTRAL_TOL = 0.05
RECOVERY_FLOOR = 1e-5
NULL_RECOVERY_TOL = 1e-15
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
    raise AssertionError(f"no book for variant={variant!r} weighting={weighting!r}")


def test_schema_and_provenance(payload: dict) -> None:
    assert payload["schema"] == bab_rank_eval.SCHEMA == "bab_p21.rank_eval/1"
    prov = payload["provenance"]
    assert prov["synthetic"] is True
    assert "not real market data" in prov["note"]
    assert prov["universe_seed"] == 20261118
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
    assert len(cfg["universe"]) == 41


def test_determinism_two_builds() -> None:
    first = json.dumps(bab_rank_eval.build_rank_eval(), indent=2, sort_keys=True)
    second = json.dumps(bab_rank_eval.build_rank_eval(), indent=2, sort_keys=True)
    assert first == second


def test_committed_json_matches_fresh_build() -> None:
    fresh = json.dumps(bab_rank_eval.build_rank_eval(), indent=2, sort_keys=True) + "\n"
    assert JSON_PATH.read_text(encoding="utf-8") == fresh


def test_rank_guard_defaults_pinned() -> None:
    assert BABConfig().rank_min_leg_beta == 0.20
    assert BABConfig().rank_max_gross == 4.0


def test_activity_both_books_active_on_planted(payload: dict) -> None:
    for weighting in _WEIGHTINGS:
        book = _book(payload, "planted", weighting)
        assert book["active_rows"] > 0, f"{weighting} book inactive on planted"


def test_guard_compliance_rank_books(payload: dict) -> None:
    for weighting in _WEIGHTINGS:
        book = _book(payload, "planted", weighting)
        if weighting != "rank":
            continue
        assert book["min_leg_beta"] >= 0.20, (
            f"rank min_leg_beta {book['min_leg_beta']} below 0.20 floor"
        )
        assert book["gross_max"] <= 4.0, (
            f"rank gross_max {book['gross_max']} above 4.0 cap"
        )


def test_book_neutrality(payload: dict) -> None:
    for variant in _VARIANTS:
        for weighting in _WEIGHTINGS:
            book = _book(payload, variant, weighting)
            if book["active_rows"] == 0:
                continue
            # Beta neutrality holds for both weightings (rank is beta-neutral
            # by construction; equal is enforced by enforce_beta_neutrality).
            assert book["beta_exposure_max"] < BETA_NEUTRAL_TOL, (
                f"{variant}/{weighting} beta exposure "
                f"{book['beta_exposure_max']} not < {BETA_NEUTRAL_TOL}"
            )
            # Dollar neutrality holds only for the equal weighting. Rank mode
            # is "beta-neutral but not dollar-neutral" (README §5): long leg
            # sums to 1/beta_L and short leg to -1/beta_H, which differ unless
            # beta_L == beta_H. Do not assert dollar neutrality for rank.
            if weighting == "equal":
                assert book["dollar_imbalance_max"] < DEGENERATE_TOL, (
                    f"{variant}/equal dollar imbalance "
                    f"{book['dollar_imbalance_max']} not < 1e-12"
                )


def test_recovery_planted_positive_null_zero(payload: dict) -> None:
    for weighting in _WEIGHTINGS:
        planted = _book(payload, "planted", weighting)
        null = _book(payload, "null", weighting)
        assert planted["recovery_mean"] > RECOVERY_FLOOR, (
            f"{weighting} planted recovery {planted['recovery_mean']} not > 1e-5"
        )
        assert abs(null["recovery_mean"]) < NULL_RECOVERY_TOL, (
            f"{weighting} null recovery {null['recovery_mean']} not ~0"
        )
        assert planted["recovery_mean"] > 10.0 * max(
            abs(null["recovery_mean"]), NULL_RECOVERY_TOL
        )


def test_universe_json_unchanged() -> None:
    from scripts import bab_synthetic_universe as u

    committed = UNIVERSE_PATH.read_text(encoding="utf-8")
    fresh = json.dumps(u.build_universe(), indent=2, sort_keys=True) + "\n"
    assert committed == fresh, "universe.json drifted from its generator"


def test_panel_sha256_matches_universe(payload: dict) -> None:
    universe = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    for variant in _VARIANTS:
        expected = universe["panels"][variant]["sha256"]
        for weighting in _WEIGHTINGS:
            book = _book(payload, variant, weighting)
            assert book["panel_sha256"] == expected, (
                f"{variant}/{weighting} panel sha mismatch"
            )


def test_markdown_numbers_derived_from_json(payload: dict) -> None:
    json_text = json.dumps(payload, indent=2, sort_keys=True)
    markdown = MD_PATH.read_text(encoding="utf-8")
    assert markdown == bab_rank_eval.render_markdown(payload)
    tokens = NUMERIC_TOKEN.findall(markdown)
    assert tokens
    missing = [token for token in tokens if token not in json_text]
    assert not missing, f"markdown numbers absent from JSON: {missing}"


def test_books_schema_keys(payload: dict) -> None:
    expected_keys = {
        "variant", "weighting", "active_rows", "total_rows",
        "gross_mean_active", "gross_max", "long_leg_beta_mean",
        "short_leg_beta_mean", "min_leg_beta", "dollar_imbalance_max",
        "beta_exposure_max", "recovery_mean", "recovery_frac_positive",
        "panel_sha256",
    }
    for book in payload["books"]:
        assert set(book.keys()) == expected_keys, (
            f"book keys {set(book.keys())} != {expected_keys}"
        )
