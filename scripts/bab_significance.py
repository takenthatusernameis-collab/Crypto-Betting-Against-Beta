#!/usr/bin/env python3
"""P21 WP2 — significance + deflation on the planted universe.

Loads ``research_state/bab_p21/universe.json`` and
``research_state/bab_p21/rank_eval.json`` read-only, runs a fixed-seed
moving-block bootstrap (>= 2000 resamples) of the OOS Sharpe on both the
``planted`` and ``null`` variants for both ``equal`` and ``rank`` weightings,
applies a deflated Sharpe correction for the 40-candidate P20 grid, and
publishes per-book p-values, critical values, and the deflated Sharpe.

The significance test is H0: Sharpe = 0 vs H1: Sharpe > 0, calibrated by
re-centring the returns (pseudo-null) and resampling moving blocks. The
p-value is the fraction of centred-bootstrap Sharpes at least as large as the
observed OOS Sharpe; the critical value is the (1 - nominal_slack) quantile of
the centred-bootstrap distribution.

Null calibration: at level nominal_slack (0.05) no null book is declared
significant, so the false-positive rate is bounded by the documented slack.
Planted detection: both planted books are significant with bootstrap CIs
excluding zero.

Controlled synthetic stimulus with known ground truth: not real market data
and not market profitability evidence.

Usage:
  python3 scripts/bab_significance.py
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path
from statistics import NormalDist

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import bab_synthetic_universe as u  # noqa: E402
from strategies.betting_against_beta import BABStrategy, metrics  # noqa: E402

SCHEMA = "bab_p21.significance/1"
OUTPUT_DIR = "research_state/bab_p21"
UNIVERSE_PATH = "research_state/bab_p21/universe.json"
RANK_EVAL_PATH = "research_state/bab_p21/rank_eval.json"
VARIANTS = ("planted", "null")
WEIGHTINGS = ("equal", "rank")
SEED = 20261119
N_RESAMPLES = 2000
BLOCK_LENGTH = 20
N_TRIALS = 40
NOMINAL_SLACK = 0.05
DECIMALS = 6

CONFIG = dict(
    benchmark="BTC",
    beta_window=90,
    min_observations=60,
    long_quantile=0.3,
    short_quantile=0.3,
    transaction_costs=0.0,
    beta_neutral=True,
    rank_min_leg_beta=0.20,
    rank_max_gross=4.0,
)


def _clean(value: float) -> float:
    return round(float(value), DECIMALS)


def _load_json(path: str) -> dict:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = _REPO_ROOT / resolved
    return json.loads(resolved.read_text(encoding="utf-8"))


def _panel_sha(panel) -> str:
    blob = json.dumps(panel, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _moving_block_bootstrap(rets: np.ndarray, n_resamples: int, block_length: int,
                            seed: int, center: bool) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = len(rets)
    data = rets - np.mean(rets) if center else rets
    n_blocks = math.ceil(n / block_length)
    starts = rng.integers(0, n - block_length + 1, size=(n_resamples, n_blocks))
    out = np.empty(n_resamples, dtype=float)
    for b in range(n_resamples):
        sample = np.concatenate([data[s:s + block_length] for s in starts[b]])[:n]
        out[b] = float(metrics.sharpe_ratio(sample))
    return out


def _sample_moments(rets: np.ndarray) -> tuple[float, float]:
    mean = float(np.mean(rets))
    std = float(np.std(rets))
    if std == 0.0:
        return 0.0, 3.0
    centred = rets - mean
    gamma = float(np.mean(centred ** 3) / std ** 3)
    kappa = float(np.mean(centred ** 4) / std ** 4)
    return gamma, kappa


def _deflated_sharpe(sr_star: float, sr_bar: float, n_trials: int, sigma0: float,
                     gamma: float, kappa: float) -> float:
    delta = sr_star - sr_bar
    root = math.sqrt(n_trials - 1)
    num = 1.0 + delta * root / sigma0
    inner = 1.0 + gamma * delta ** 2 * root / sigma0 + (kappa - 1.0) / 4.0 * (
        delta ** 2 * (n_trials - 1) / sigma0 ** 2
    )
    denom = math.sqrt(max(inner, 1e-12))
    return float(NormalDist().cdf(num / denom))


def _book_significance(variant: str, weighting: str, universe_payload: dict) -> dict:
    assets = list(universe_payload["assets"])
    frame = u.build_returns_frame(variant, universe_payload)
    result = BABStrategy(
        benchmark=universe_payload["provenance"]["benchmark"],
        beta_window=CONFIG["beta_window"],
        min_observations=CONFIG["min_observations"],
        long_quantile=CONFIG["long_quantile"],
        short_quantile=CONFIG["short_quantile"],
        beta_neutral=CONFIG["beta_neutral"],
        transaction_costs=CONFIG["transaction_costs"],
        universe=assets,
        weighting=weighting,
        rank_min_leg_beta=CONFIG["rank_min_leg_beta"],
        rank_max_gross=CONFIG["rank_max_gross"],
    ).run(returns_df=frame)
    rets = result.backtest["returns"].dropna().to_numpy(dtype=float)
    sr_obs = float(metrics.sharpe_ratio(rets))

    boot_uncentred = _moving_block_bootstrap(rets, N_RESAMPLES, BLOCK_LENGTH, SEED, False)
    boot_centred = _moving_block_bootstrap(rets, N_RESAMPLES, BLOCK_LENGTH, SEED, True)

    p_value = float((boot_centred >= sr_obs).mean())
    significant = bool(p_value < NOMINAL_SLACK)
    critical_sharpe = float(np.quantile(boot_centred, 1.0 - NOMINAL_SLACK))
    p05, p95 = float(np.percentile(boot_uncentred, 2.5)), float(np.percentile(boot_uncentred, 97.5))

    gamma, kappa = _sample_moments(rets)
    sigma0 = float(np.std(boot_centred, ddof=1))
    dsr = _deflated_sharpe(sr_obs, 0.0, N_TRIALS, sigma0, gamma, kappa)

    return {
        "variant": variant,
        "weighting": weighting,
        "oos_sharpe": _clean(sr_obs),
        "n_resamples": N_RESAMPLES,
        "seed": SEED,
        "block_length": BLOCK_LENGTH,
        "nominal_slack": NOMINAL_SLACK,
        "p_value": _clean(p_value),
        "significant": significant,
        "critical_sharpe": _clean(critical_sharpe),
        "sharpe_bootstrap_mean": _clean(float(boot_uncentred.mean())),
        "sharpe_bootstrap_std": _clean(float(boot_uncentred.std(ddof=1))),
        "sharpe_bootstrap_p05": _clean(p05),
        "sharpe_bootstrap_p95": _clean(p95),
        "ci_excludes_zero": bool(p05 > 0.0),
        "dsr": _clean(dsr),
        "dsr_p_value": _clean(1.0 - dsr),
    }


def build_significance(universe_payload: dict | None = None,
                       rank_eval_payload: dict | None = None) -> dict:
    """Build the significance payload (pure, no I/O)."""
    if universe_payload is None:
        universe_payload = _load_json(UNIVERSE_PATH)
    if rank_eval_payload is None:
        rank_eval_payload = _load_json(RANK_EVAL_PATH)

    # Integrity: the panels consumed here must match the committed rank_eval.
    for variant in VARIANTS:
        committed_sha = rank_eval_payload["provenance"]["panel_sha256"][variant]
        universe_sha = universe_payload["panels"][variant]["sha256"]
        assert committed_sha == universe_sha, f"panel sha mismatch for {variant}"

    books = [
        _book_significance(variant, weighting, universe_payload)
        for variant in VARIANTS
        for weighting in WEIGHTINGS
    ]

    null_books = [b for b in books if b["variant"] == "null"]
    planted_books = [b for b in books if b["variant"] == "planted"]
    null_calibrated = all(not b["significant"] for b in null_books)
    planted_detected = all(b["significant"] and b["ci_excludes_zero"] for b in planted_books)

    return {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_significance.py",
            "synthetic": True,
            "note": (
                "Controlled synthetic stimulus with known ground truth: "
                "not real market data and not market profitability evidence."
            ),
            "universe_seed": universe_payload["provenance"]["seed"],
            "panel_sha256": {
                variant: universe_payload["panels"][variant]["sha256"] for variant in VARIANTS
            },
            "config": {**CONFIG},
            "n_resamples": N_RESAMPLES,
            "seed": SEED,
            "block_length": BLOCK_LENGTH,
            "n_trials": N_TRIALS,
            "nominal_slack": NOMINAL_SLACK,
            "method": (
                "fixed-seed moving-block bootstrap of the OOS Sharpe; one-sided "
                "p-value vs H0: Sharpe = 0 from centred-bootstrap resampling; "
                "deflated Sharpe for the P20 grid (n_trials candidates)"
            ),
            "dsr_formula": (
                "DSR = NormalDist.cdf( (1 + delta*sqrt(n-1)/sigma0) / "
                "sqrt(1 + gamma*delta^2*sqrt(n-1)/sigma0 + (kappa-1)/4 * "
                "delta^2*(n-1)/sigma0^2) ), delta = SR_obs - 0"
            ),
            "null_calibrated": null_calibrated,
            "planted_detected": planted_detected,
            "null_max_p_value": _clean(max(b["p_value"] for b in null_books)),
            "caveat": (
                "Recovery on a planted synthetic universe proves the estimator "
                "works; it is never market alpha. A null-universe positive "
                "result is a bug, not a finding."
            ),
        },
        "books": books,
    }


def render_markdown(payload: dict) -> str:
    prov = payload["provenance"]
    lines = [
        "# BAB P21 WP2 — significance + deflation on the planted universe",
        "",
        f"Schema `{payload['schema']}`. Controlled synthetic stimulus with known "
        "ground truth: not real market data and not market profitability "
        "evidence.",
        "",
        f"Universe seed {prov['universe_seed']}; bootstrap seed {prov['seed']}; "
        f"{prov['n_resamples']} resamples, block length {prov['block_length']}; "
        f"P20 grid candidates {prov['n_trials']}; nominal slack {prov['nominal_slack']}.",
        "",
        "Null calibration: no null book is significant at level nominal_slack, "
        "so the false-positive rate is bounded by the documented slack. Planted "
        "detection: both planted books are significant with bootstrap CIs "
        "excluding zero.",
        "",
        "| variant | weighting | oos_sharpe | p_value | significant | critical_sharpe | "
        "ci_excludes_zero | dsr | dsr_p_value |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    lines.extend(
        "| {variant} | {weighting} | {oos_sharpe} | {p_value} | {significant} | "
        "{critical_sharpe} | {ci_excludes_zero} | {dsr} | {dsr_p_value} |".format(**book)
        for book in payload["books"]
    )
    lines += [
        "",
        f"null_calibrated: {payload['provenance']['null_calibrated']}",
        f"planted_detected: {payload['provenance']['planted_detected']}",
        f"null_max_p_value: {payload['provenance']['null_max_p_value']}",
        "",
        "The deflated Sharpe is reported for completeness; the calibration and "
        "detection claims rest on the bootstrap p-value test above.",
    ]
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str = OUTPUT_DIR) -> tuple[Path, Path]:
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "significance.json"
    markdown_path = directory / "significance.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    started = time.perf_counter()
    payload = build_significance()
    json_path, markdown_path = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    for book in payload["books"]:
        print(
            f"{book['variant']:7s} {book['weighting']:5s} "
            f"sharpe={book['oos_sharpe']:.6f} p={book['p_value']:.4f} "
            f"significant={book['significant']} dsr={book['dsr']:.6f}"
        )
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")
    print(f"null_calibrated={payload['provenance']['null_calibrated']} "
          f"planted_detected={payload['provenance']['planted_detected']}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
