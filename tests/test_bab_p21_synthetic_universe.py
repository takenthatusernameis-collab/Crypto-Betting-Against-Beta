"""Acceptance tests for P21 WP0: deterministic wide universe with ground truth.

These tests are the claim that ``scripts/bab_synthetic_universe.py`` produces a
deterministic, sha-pinned ``>= 41`` asset / ``>= 600`` row universe in two
variants whose only difference is the alpha vector, and that a beta-neutral
BAB book built from the shipped ``BABStrategy`` weights recovers the planted
alpha and nothing on the null variant. They never touch the network and never
edit product code.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import spearmanr

from scripts import bab_synthetic_universe as u
from strategies.betting_against_beta import BABStrategy

REPO_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = REPO_ROOT / "research_state/bab_p21/universe.json"
MD_PATH = REPO_ROOT / "research_state/bab_p21/universe.md"

DEGENERATE_TOL = 1e-12
BETA_NEUTRAL_TOL = 0.02
RECOVERY_FLOOR = 1e-5
NULL_RECOVERY_TOL = 1e-15
RESIDUAL_TOL = 2e-6
NUMERIC_TOKEN = re.compile(r"-?\d+(?:\.\d+)?")

_RUN_CACHE: dict[str, object] = {}


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def _book(variant: str, payload: dict):
    """Run the shipped strategy once per variant and return the full book."""
    if variant not in _RUN_CACHE:
        frame = u.build_returns_frame(variant, payload)
        result = BABStrategy(
            benchmark=payload["provenance"]["benchmark"],
            beta_window=90,
            min_observations=60,
            long_quantile=0.3,
            short_quantile=0.3,
            beta_neutral=True,
            transaction_costs=0.0,
            universe=list(payload["assets"]),
        ).run(returns_df=frame)
        columns = [payload["provenance"]["benchmark"], *payload["assets"]]
        weights = result.weights.reindex(columns=columns).fillna(0.0).to_numpy(dtype=float)
        betas = np.concatenate([[1.0], [payload["betas"][a] for a in payload["assets"]]])
        alphas = np.concatenate(
            [[0.0], [payload["alphas"][variant][a] for a in payload["assets"]]]
        )
        gross = np.abs(weights).sum(axis=1)
        active = gross > DEGENERATE_TOL
        _RUN_CACHE[variant] = {
            "weights": weights[active],
            "betas": betas,
            "alphas": alphas,
            "gross": gross[active],
        }
    return _RUN_CACHE[variant]


def test_schema_and_provenance(payload: dict) -> None:
    prov = payload["provenance"]
    assert payload["schema"] == u.SCHEMA == "bab_p21.universe/1"
    assert prov["synthetic"] is True
    assert "not real market data" in prov["note"]
    assert prov["variants"] == ["planted", "null"]
    assert prov["benchmark"] == u.BENCHMARK
    assert prov["seed"] == u.SEED
    assert "sha256" in prov["panel_sha_rule"]


def test_determinism_two_builds() -> None:
    first = json.dumps(u.build_universe(), indent=2, sort_keys=True)
    second = json.dumps(u.build_universe(), indent=2, sort_keys=True)
    assert first == second


def test_committed_json_matches_fresh_build() -> None:
    fresh = json.dumps(u.build_universe(), indent=2, sort_keys=True) + "\n"
    assert JSON_PATH.read_text(encoding="utf-8") == fresh


def test_scale_minimums(payload: dict) -> None:
    prov = payload["provenance"]
    assert prov["assets"] >= 41
    assert prov["return_rows"] >= 600
    assert len(payload["assets"]) == prov["assets"]
    assert set(prov["variants"]) == {"planted", "null"}
    assert prov["benchmark"] in u.build_returns_frame("planted", payload).columns


def test_planted_alpha_strictly_decreasing_in_beta(payload: dict) -> None:
    betas = np.array([payload["betas"][a] for a in payload["assets"]], dtype=float)
    alphas = np.array(
        [payload["alphas"]["planted"][a] for a in payload["assets"]], dtype=float
    )
    order = np.argsort(betas, kind="stable")
    assert np.all(np.diff(alphas[order]) < 0.0)
    assert np.all(np.diff(betas[order]) > 0.0)
    assert float(spearmanr(betas, alphas).statistic) == -1.0


def test_null_alphas_equal(payload: dict) -> None:
    alphas = np.array(
        [payload["alphas"]["null"][a] for a in payload["assets"]], dtype=float
    )
    assert np.all(alphas == alphas[0])


def test_variants_differ_only_in_alpha(payload: dict) -> None:
    planted = np.asarray(payload["panels"]["planted"]["returns"], dtype=float)
    null = np.asarray(payload["panels"]["null"]["returns"], dtype=float)
    betas = np.array([payload["betas"][a] for a in payload["assets"]], dtype=float)
    alphas = np.array(
        [payload["alphas"]["planted"][a] for a in payload["assets"]], dtype=float
    )
    benchmark = np.asarray(payload["benchmark"], dtype=float)[:, np.newaxis]
    planted_residual = planted - alphas[np.newaxis, :] - betas[np.newaxis, :] * benchmark
    null_residual = null - betas[np.newaxis, :] * benchmark
    assert np.allclose(planted_residual, null_residual, atol=RESIDUAL_TOL, rtol=0.0)
    delta = planted - null
    assert np.allclose(delta, np.broadcast_to(alphas, delta.shape), atol=RESIDUAL_TOL, rtol=0.0)


def test_panels_finite_and_shaped_no_nans(payload: dict) -> None:
    prov = payload["provenance"]
    expected = (prov["return_rows"], prov["assets"])
    for variant in ("planted", "null"):
        panel = np.asarray(payload["panels"][variant]["returns"], dtype=float)
        assert panel.shape == expected
        assert np.isfinite(panel).all()
        assert payload["panels"][variant]["shape"] == list(panel.shape)


def test_benchmark_aligned(payload: dict) -> None:
    prov = payload["provenance"]
    benchmark = np.asarray(payload["benchmark"], dtype=float)
    assert benchmark.shape == (prov["return_rows"],)
    assert np.isfinite(benchmark).all()
    frame = u.build_returns_frame("planted", payload)
    assert len(frame) == prov["return_rows"]
    assert frame.columns[0] == prov["benchmark"]
    assert np.allclose(frame[prov["benchmark"]].to_numpy(), benchmark)


def test_panel_sha_reproducible(payload: dict) -> None:
    for variant in ("planted", "null"):
        panel = payload["panels"][variant]["returns"]
        assert payload["panels"][variant]["sha256"] == u._panel_sha(panel)


def test_markdown_numbers_derived_from_json(payload: dict) -> None:
    json_text = json.dumps(payload, indent=2, sort_keys=True)
    markdown = MD_PATH.read_text(encoding="utf-8")
    assert markdown == u.render_markdown(payload)
    tokens = NUMERIC_TOKEN.findall(markdown)
    assert tokens
    missing = [token for token in tokens if token not in json_text]
    assert not missing, f"markdown numbers absent from JSON: {missing}"


def test_book_is_dollar_and_beta_neutral(payload: dict) -> None:
    for variant in ("planted", "null"):
        book = _book(variant, payload)
        assert book["weights"].shape[0] > 0
        assert np.abs(book["weights"].sum(axis=1)).max() < DEGENERATE_TOL
        assert np.abs(book["weights"] @ book["betas"]).max() < BETA_NEUTRAL_TOL


def test_planted_recovery_positive_and_null_zero(payload: dict) -> None:
    planted = _book("planted", payload)
    null = _book("null", payload)
    planted_mean = planted["weights"].mean(axis=0)
    null_mean = null["weights"].mean(axis=0)
    planted_alpha = float(planted_mean @ planted["alphas"])
    null_alpha = float(null_mean @ null["alphas"])
    assert planted_alpha > RECOVERY_FLOOR
    assert abs(null_alpha) < NULL_RECOVERY_TOL
    assert planted_alpha > 10.0 * max(abs(null_alpha), NULL_RECOVERY_TOL)


def test_build_is_fast_and_offline() -> None:
    started = time.perf_counter()
    u.build_universe()
    u.build_universe()
    assert time.perf_counter() - started < 5.0
    assert not hasattr(u, "requests")
    assert not hasattr(u, "urllib")
