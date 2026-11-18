#!/usr/bin/env python3
"""Deterministic P21 WP0 wide synthetic universe with a planted BAB effect.

Two return panels are generated from one fixed seed and one shared set of
draws:

  planted -- each asset has an alpha that is *strictly decreasing* in its beta,
             so a beta-neutral BAB long/short book has positive expected alpha.
  null    -- identical betas and identical idiosyncratic draws, all alphas
             equal to zero, so the same book has zero expected alpha.

The only difference between the two variants is the alpha vector. Everything
else (benchmark draws, idiosyncratic draws, betas, idiosyncratic vols) is
shared row-for-row, which the acceptance test proves mechanically.

Why the alpha curve is convex rather than linear
------------------------------------------------
If ``alpha_i = a + b * beta_i`` exactly, then for any dollar-neutral book
(``sum w_i = 0``) that is also beta-neutral (``sum w_i beta_i = 0``) we get
``sum w_i alpha_i = 0`` exactly. A linear planted alpha would therefore be
mathematically invisible to the very estimator under test. The planted variant
uses ``alpha_i = A * (0.5 - u_i**2)`` with ``u_i`` the normalized beta rank:
still strictly decreasing (Spearman exactly -1), but with a non-affine
component that survives beta neutralization.

``research_state/bab_p21/universe.json`` stores both return panels (6 dp), the
per-asset beta/alpha/vol vectors, the benchmark series, and a sha256 of each
serialized panel. ``universe.md`` is rendered from that same dict and contains
no number that is not in the JSON.

This is a controlled synthetic stimulus, never real market data.

Usage:
  python3 scripts/bab_synthetic_universe.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

SCHEMA = "bab_p21.universe/1"
OUTPUT_DIR = "research_state/bab_p21"
ASSETS = 41
ROWS = 600
SEED = 20261118
BENCHMARK = "BTC"
DATE_START = "2024-01-02"
DATE_FREQ = "B"
BENCH_DRIFT = 0.0002
BENCH_VOL = 0.02
BETA_MIN = 0.30
BETA_MAX = 2.70
IDIO_VOL_MIN = 0.0030
IDIO_VOL_MAX = 0.0050
PLANTED_ALPHA_SPREAD_ANNUAL = 4.0
ALPHA_EXPONENT = 2.0
TRADING_DAYS = 252
DECIMALS = 6
VARIANTS = ("planted", "null")


def _clean(value: float) -> float:
    """Round to the artifact precision."""
    return round(float(value), DECIMALS)


def _asset_names(n: int) -> list[str]:
    return [f"A{i:03d}" for i in range(1, n + 1)]


def _panel_sha(panel: list[list[float]]) -> str:
    """sha256 of a canonical serialization of one rounded return panel.

    Consumers can recompute this from ``payload['panels'][variant]['returns']``
    with ``json.dumps(panel, separators=(',', ':'), sort_keys=True)``.
    """
    blob = json.dumps(panel, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def build_universe() -> dict:
    """Build the deterministic universe payload (pure, no I/O)."""
    n = ASSETS
    names = _asset_names(n)
    rng = np.random.default_rng(SEED)

    benchmark = rng.normal(BENCH_DRIFT, BENCH_VOL, ROWS)
    betas = np.round(np.linspace(BETA_MIN, BETA_MAX, n), DECIMALS)
    idio_vol = np.round(np.linspace(IDIO_VOL_MIN, IDIO_VOL_MAX, n), DECIMALS)
    # One shared residual draw reused by both variants.
    residuals = rng.normal(0.0, 1.0, (ROWS, n)) * idio_vol[np.newaxis, :]

    u = np.arange(n, dtype=float) / (n - 1)
    alpha_daily = (PLANTED_ALPHA_SPREAD_ANNUAL / TRADING_DAYS) * (0.5 - u**ALPHA_EXPONENT)
    alpha_daily = np.round(alpha_daily, DECIMALS)
    null_alpha = np.zeros(n)

    panels: dict = {}
    for variant, alpha in (("planted", alpha_daily), ("null", null_alpha)):
        raw = alpha[np.newaxis, :] + betas[np.newaxis, :] * benchmark[:, np.newaxis] + residuals
        rounded = [[_clean(v) for v in row] for row in raw.tolist()]
        panels[variant] = {
            "returns": rounded,
            "sha256": _panel_sha(rounded),
            "shape": [ROWS, n],
        }

    payload = {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_synthetic_universe.py",
            "synthetic": True,
            "note": (
                "Controlled synthetic stimulus with known ground truth: "
                "not real market data and not market profitability evidence."
            ),
            "assets": n,
            "return_rows": ROWS,
            "seed": SEED,
            "benchmark": BENCHMARK,
            "date_start": DATE_START,
            "date_freq": DATE_FREQ,
            "trading_days": TRADING_DAYS,
            "benchmark_drift": BENCH_DRIFT,
            "benchmark_vol": BENCH_VOL,
            "beta_min": _clean(betas.min()),
            "beta_max": _clean(betas.max()),
            "idio_vol_min": _clean(idio_vol.min()),
            "idio_vol_max": _clean(idio_vol.max()),
            "planted_alpha_spread_annual": PLANTED_ALPHA_SPREAD_ANNUAL,
            "alpha_exponent": ALPHA_EXPONENT,
            "decimals": DECIMALS,
            "variants": list(VARIANTS),
            "alpha_rule": (
                "planted: alpha_i = (spread / trading_days) * (0.5 - u_i**exponent), "
                "u_i = rank_i / (assets - 1); null: alpha_i = 0 for every asset"
            ),
            "return_rule": "r_i,t = alpha_i + beta_i * r_m,t + eps_i,t (shared draws)",
            "panel_sha_rule": (
                "sha256(json.dumps(panel, separators=(',', ':'), sort_keys=True))"
            ),
        },
        "assets": names,
        "betas": {name: _clean(b) for name, b in zip(names, betas)},
        "alphas": {
            "planted": {name: _clean(a) for name, a in zip(names, alpha_daily)},
            "null": {name: _clean(a) for name, a in zip(names, null_alpha)},
        },
        "idiosyncratic_vol": {
            name: _clean(v) for name, v in zip(names, idio_vol)
        },
        "benchmark": [_clean(v) for v in benchmark.tolist()],
        "panels": panels,
    }
    return payload


def build_returns_frame(variant: str, payload: dict | None = None) -> pd.DataFrame:
    """Return the committed panel for ``variant`` as a returns DataFrame.

    Columns are the benchmark first, then every asset in universe order. This
    is the exact frame downstream P21 work packages pass to
    ``BABStrategy.run(returns_df=...)``; it re-reads the committed panel so no
    consumer can silently regenerate a different universe.
    """
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}, got {variant!r}")
    payload = build_universe() if payload is None else payload
    panel = np.asarray(payload["panels"][variant]["returns"], dtype=float)
    benchmark = np.asarray(payload["benchmark"], dtype=float)
    data = np.column_stack([benchmark, panel])
    index = pd.date_range(
        start=payload["provenance"]["date_start"],
        periods=payload["provenance"]["return_rows"],
        freq=payload["provenance"]["date_freq"],
    )
    columns = [payload["provenance"]["benchmark"], *payload["assets"]]
    return pd.DataFrame(data, index=index, columns=columns)


def render_markdown(payload: dict) -> str:
    """Render the universe summary from the payload; no external numbers."""
    prov = payload["provenance"]
    lines = [
        "# BAB P21 WP0 — wide synthetic universe with planted ground truth",
        "",
        (
            f"Schema `{payload['schema']}`. {prov['assets']} tradable assets plus "
            f"benchmark `{prov['benchmark']}`, {prov['return_rows']} return rows, "
            f"seed {prov['seed']}."
        ),
        (
            "**Controlled synthetic stimulus with known ground truth: not real "
            "market data and not market profitability evidence.**"
        ),
        "",
        (
            f"Betas in [{prov['beta_min']}, {prov['beta_max']}]; idiosyncratic vol "
            f"in [{prov['idio_vol_min']}, {prov['idio_vol_max']}]; planted annual "
            f"alpha spread {prov['planted_alpha_spread_annual']} with exponent "
            f"{prov['alpha_exponent']}."
        ),
        (
            "The two variants share betas, idiosyncratic vols, benchmark draws and "
            "residual draws; only the alpha vector differs."
        ),
        "",
        "| variant | alpha_min | alpha_max | panel_sha256 |",
        "|---|---|---|---|",
    ]
    for variant in prov["variants"]:
        alphas = list(payload["alphas"][variant].values())
        lines.append(
            f"| {variant} | {min(alphas)} | {max(alphas)} | "
            f"{payload['panels'][variant]['sha256']} |"
        )
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "universe.json"
    markdown_path = directory / "universe.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    started = time.perf_counter()
    payload = build_universe()
    json_path, markdown_path = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    print(f"wrote {json_path} ({payload['provenance']['assets']} assets, "
          f"{payload['provenance']['return_rows']} rows)")
    print(f"wrote {markdown_path}")
    print(f"panel sha256 planted={payload['panels']['planted']['sha256']}")
    print(f"panel sha256 null={payload['panels']['null']['sha256']}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
