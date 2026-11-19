#!/usr/bin/env python3
"""P22 WP1 — null battery over the chartered >= 20 independent seeds.

Consumes ``research_state/bab_p22/charter.json`` read-only for the pinned seed
list, nominal slack and acceptance thresholds, then for every chartered seed:

1. generates the same planted/null synthetic universe pair used by P21 WP0,
   parameterised by that seed (identical draws shared by both variants, only
   the alpha vector differs);
2. runs the shipped ``BABStrategy`` for ``equal`` and ``rank`` weighting on
   both panels with the identical P21 config;
3. publishes per-seed recovery, activity, gross Sharpe, and — for the null
   books — a fixed-seed moving-block bootstrap p-value.

Battery-level claims published from the per-seed records:

* **null recovery is exactly zero** for every null book (a non-zero null is a
  bug, not a finding);
* **empirical false-positive rate** = significant null books / null books,
  published even when it exceeds the nominal slack;
* **planted recovery is strictly positive** on the documented fraction.

At the reference P21 universe seed the locally generated panels must reproduce
the committed P21 panel sha256 values exactly; that is how this harness proves
it runs the same synthetic generator without re-running (or editing) any P21
harness.

Controlled synthetic stimulus with known ground truth: not real market data
and not market profitability evidence.

Usage:
  python3 scripts/bab_null_battery.py
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import bab_synthetic_universe as u  # noqa: E402
from strategies.betting_against_beta import BABStrategy, metrics  # noqa: E402

SCHEMA = "bab_p22.null_battery/1"
OUTPUT_DIR = "research_state/bab_p22"
CHARTER_PATH = "research_state/bab_p22/charter.json"
P21_UNIVERSE_PATH = "research_state/bab_p21/universe.json"
REFERENCE_UNIVERSE_SEED = 20261118
VARIANTS = ("planted", "null")
WEIGHTINGS = ("equal", "rank")
DECIMALS = 6
DEGENERATE_TOL = 1e-12
RECOVERY_POSITIVE_FLOOR = 0.0

# Bootstrap settings must satisfy the chartered WP2 minimum (>= 2000).
N_RESAMPLES = 2000
BLOCK_LENGTH = 20
BOOTSTRAP_SEED_OFFSET = 1

# Pre-declared calibration bound: expected significant null books is
# n_books * nominal_slack; allow 2x that before the battery reports a
# calibration failure. Declared here, never tuned after measurement.
FPR_EXPECTED_MULTIPLIER = 2.0

CONFIG = dict(
    benchmark=u.BENCHMARK,
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


def build_seeded_universe(seed: int) -> dict:
    """Rebuild the P21 WP0 planted/null universe for one seed (pure).

    Mirrors ``scripts/bab_synthetic_universe.build_universe`` exactly except
    that the RNG is seeded by ``seed``. The companion test proves the
    reference seed reproduces the committed P21 panel sha256 values.
    """
    n = u.ASSETS
    names = [f"A{i:03d}" for i in range(1, n + 1)]
    rng = np.random.default_rng(int(seed))

    benchmark = rng.normal(u.BENCH_DRIFT, u.BENCH_VOL, u.ROWS)
    betas = np.round(np.linspace(u.BETA_MIN, u.BETA_MAX, n), DECIMALS)
    idio_vol = np.round(np.linspace(u.IDIO_VOL_MIN, u.IDIO_VOL_MAX, n), DECIMALS)
    residuals = rng.normal(0.0, 1.0, (u.ROWS, n)) * idio_vol[np.newaxis, :]

    grid = np.arange(n, dtype=float) / (n - 1)
    alpha_daily = np.round(
        (u.PLANTED_ALPHA_SPREAD_ANNUAL / u.TRADING_DAYS)
        * (0.5 - grid**u.ALPHA_EXPONENT),
        DECIMALS,
    )
    null_alpha = np.zeros(n)

    panels: dict = {}
    for variant, alpha in (("planted", alpha_daily), ("null", null_alpha)):
        raw = (
            alpha[np.newaxis, :]
            + betas[np.newaxis, :] * benchmark[:, np.newaxis]
            + residuals
        )
        rounded = [[round(float(v), DECIMALS) for v in row] for row in raw.tolist()]
        panels[variant] = {
            "returns": rounded,
            "sha256": _panel_sha(rounded),
            "shape": [u.ROWS, n],
        }

    return {
        "seed": int(seed),
        "assets": names,
        "betas": {name: round(float(b), DECIMALS) for name, b in zip(names, betas)},
        "alphas": {
            "planted": {
                name: round(float(a), DECIMALS) for name, a in zip(names, alpha_daily)
            },
            "null": dict.fromkeys(names, 0.0),
        },
        "benchmark": [round(float(v), DECIMALS) for v in benchmark.tolist()],
        "panels": panels,
    }


def _returns_frame(payload: dict, variant: str) -> pd.DataFrame:
    panel = np.asarray(payload["panels"][variant]["returns"], dtype=float)
    benchmark = np.asarray(payload["benchmark"], dtype=float)
    data = np.column_stack([benchmark, panel])
    index = pd.date_range(
        start=u.DATE_START, periods=u.ROWS, freq=u.DATE_FREQ
    )
    columns = [u.BENCHMARK, *payload["assets"]]
    return pd.DataFrame(data, index=index, columns=columns)


def _moving_block_pvalue(rets: np.ndarray, seed: int) -> tuple[float, float]:
    """One-sided p-value vs H0: Sharpe = 0 from a centred block bootstrap."""
    rng = np.random.default_rng(int(seed) + BOOTSTRAP_SEED_OFFSET)
    centred = rets - np.mean(rets)
    n = len(centred)
    n_blocks = math.ceil(n / BLOCK_LENGTH)
    starts = rng.integers(0, n - BLOCK_LENGTH + 1, size=(N_RESAMPLES, n_blocks))
    boot = np.empty(N_RESAMPLES, dtype=float)
    for b in range(N_RESAMPLES):
        sample = np.concatenate(
            [centred[s:s + BLOCK_LENGTH] for s in starts[b]]
        )[:n]
        boot[b] = float(metrics.sharpe_ratio(sample))
    observed = float(metrics.sharpe_ratio(rets))
    p_value = float((boot >= observed).mean())
    return observed, p_value


def _book(
    payload: dict, variant: str, weighting: str, nominal_slack: float
) -> dict:
    assets = list(payload["assets"])
    frame = _returns_frame(payload, variant)
    result = BABStrategy(
        benchmark=CONFIG["benchmark"],
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

    columns = [u.BENCHMARK, *assets]
    weights = (
        result.weights.reindex(columns=columns).fillna(0.0).to_numpy(dtype=float)
    )
    w_assets = weights[:, 1:]
    gross = np.abs(weights).sum(axis=1)
    active = gross > DEGENERATE_TOL
    active_rows = int(active.sum())
    alpha = np.array([float(payload["alphas"][variant][a]) for a in assets])

    if active_rows == 0:
        return {
            "variant": variant,
            "weighting": weighting,
            "active_rows": 0,
            "total_rows": len(weights),
            "gross_mean_active": 0.0,
            "gross_max": 0.0,
            "recovery_mean": 0.0,
            "recovery_frac_positive": 0.0,
            "oos_sharpe": 0.0,
            "p_value": None,
            "significant": False,
        }

    w_active = w_assets[active]
    recovery_mean = float(w_active.mean(axis=0) @ alpha)
    row_recovery = w_active @ alpha
    rets = result.backtest["returns"].dropna().to_numpy(dtype=float)

    record = {
        "variant": variant,
        "weighting": weighting,
        "active_rows": active_rows,
        "total_rows": len(weights),
        "gross_mean_active": _clean(gross[active].mean()),
        "gross_max": _clean(gross[active].max()),
        "recovery_mean": _clean(recovery_mean),
        "recovery_frac_positive": _clean(float((row_recovery > 0.0).mean())),
        "oos_sharpe": _clean(float(metrics.sharpe_ratio(rets))),
    }
    if variant == "null":
        _, p_value = _moving_block_pvalue(rets, payload["seed"])
        record["p_value"] = _clean(p_value)
        record["significant"] = bool(p_value < nominal_slack)
    else:
        record["p_value"] = None
        record["significant"] = False
    return record


def build_null_battery(
    charter_payload: dict | None = None,
    p21_universe_payload: dict | None = None,
    seeds: list | None = None,
) -> dict:
    """Build the null-battery payload (pure, no I/O beyond committed JSON)."""
    if charter_payload is None:
        charter_payload = _load_json(CHARTER_PATH)
    if p21_universe_payload is None:
        p21_universe_payload = _load_json(P21_UNIVERSE_PATH)

    charter_prov = charter_payload["provenance"]
    charter_seeds = [int(s) for s in charter_prov["p22_null_battery_seeds"]]
    assert len(charter_seeds) >= 20, "charter must pin >= 20 null-battery seeds"
    assert len(set(charter_seeds)) == len(charter_seeds), "duplicate charter seeds"
    nominal_slack = float(charter_prov["nominal_slack"])
    assert nominal_slack == 0.05
    assert charter_prov["acceptance_thresholds"]["wp2"]["n_resamples_min"] <= (
        N_RESAMPLES
    )

    if seeds is None:
        seeds = charter_seeds
    seeds = [int(s) for s in seeds]

    # Fidelity: the reference seed must reproduce the committed P21 panels.
    reference = build_seeded_universe(REFERENCE_UNIVERSE_SEED)
    reference_sha = {
        variant: reference["panels"][variant]["sha256"] for variant in VARIANTS
    }
    committed_sha = {
        variant: p21_universe_payload["panels"][variant]["sha256"]
        for variant in VARIANTS
    }
    reference_matched = reference_sha == committed_sha

    seed_records = []
    for seed in seeds:
        universe = build_seeded_universe(seed)
        books = [
            _book(universe, variant, weighting, nominal_slack)
            for variant in VARIANTS
            for weighting in WEIGHTINGS
        ]
        seed_records.append(
            {
                "seed": seed,
                "panel_sha256": {
                    variant: universe["panels"][variant]["sha256"]
                    for variant in VARIANTS
                },
                "books": books,
            }
        )

    null_books = [b for rec in seed_records for b in rec["books"] if b["variant"] == "null"]
    planted_books = [
        b for rec in seed_records for b in rec["books"] if b["variant"] == "planted"
    ]

    fpr_count = sum(1 for b in null_books if b["significant"])
    fpr_denominator = len(null_books)
    expected = fpr_denominator * nominal_slack
    fpr_max_count = math.ceil(FPR_EXPECTED_MULTIPLIER * expected)

    planted_positive = {
        weighting: [
            b["recovery_mean"] > RECOVERY_POSITIVE_FLOOR
            for b in planted_books
            if b["weighting"] == weighting
        ]
        for weighting in WEIGHTINGS
    }
    planted_positive_fraction = {
        weighting: _clean(
            sum(planted_positive[weighting]) / len(planted_positive[weighting])
        )
        for weighting in WEIGHTINGS
    }
    planted_recovery_min = {
        weighting: _clean(
            min(
                b["recovery_mean"]
                for b in planted_books
                if b["weighting"] == weighting
            )
        )
        for weighting in WEIGHTINGS
    }
    null_recovery_values = [b["recovery_mean"] for b in null_books]

    summary = {
        "n_seeds": len(seed_records),
        "n_null_books": len(null_books),
        "n_planted_books": len(planted_books),
        "null_recovery_max_abs": _clean(max(abs(v) for v in null_recovery_values)),
        "null_recovery_zero_books": int(
            sum(1 for v in null_recovery_values if v == 0.0)
        ),
        "null_recovery_exactly_zero_every_seed": bool(
            all(v == 0.0 for v in null_recovery_values)
        ),
        "fpr_count": int(fpr_count),
        "fpr_denominator": fpr_denominator,
        "fpr_rate": _clean(fpr_count / fpr_denominator),
        "fpr_expected_count": _clean(expected),
        "fpr_max_count_declared": fpr_max_count,
        "fpr_within_declared_bound": bool(fpr_count <= fpr_max_count),
        "planted_recovery_positive_fraction": planted_positive_fraction,
        "planted_recovery_min": planted_recovery_min,
        "planted_recovery_exceeds_null_max": bool(
            planted_recovery_min["equal"] > max(null_recovery_values)
            and planted_recovery_min["rank"] > max(null_recovery_values)
        ),
        "null_sharpe_max": _clean(max(b["oos_sharpe"] for b in null_books)),
        "planted_sharpe_min": _clean(min(b["oos_sharpe"] for b in planted_books)),
    }

    return {
        "schema": SCHEMA,
        "provenance": {
            "generator": "scripts/bab_null_battery.py",
            "synthetic": True,
            "note": (
                "Controlled synthetic stimulus with known ground truth: "
                "not real market data and not market profitability evidence."
            ),
            "source_charter": CHARTER_PATH,
            "source_charter_schema": charter_payload["schema"],
            "reference_universe_seed": REFERENCE_UNIVERSE_SEED,
            "reference_panel_sha256_matched": bool(reference_matched),
            "reference_panel_sha256": reference_sha,
            "committed_p21_panel_sha256": committed_sha,
            "seeds": list(seeds),
            "n_seeds": len(seed_records),
            "nominal_slack": nominal_slack,
            "config": {**CONFIG, "universe_assets": u.ASSETS, "return_rows": u.ROWS},
            "bootstrap": {
                "n_resamples": N_RESAMPLES,
                "block_length": BLOCK_LENGTH,
                "seed_rule": (
                    f"default_rng(universe_seed + {BOOTSTRAP_SEED_OFFSET})"
                ),
                "statistic": (
                    "one-sided p-value of the observed OOS Sharpe against a "
                    "centred moving-block bootstrap of the same return series"
                ),
                "applied_to": "null books only (empirical false-positive rate)",
            },
            "declared_calibration": {
                "fpr_expected_multiplier": FPR_EXPECTED_MULTIPLIER,
                "fpr_max_count": int(fpr_max_count),
            },
            "summary": summary,
            "method": (
                "rebuilds the P21 planted/null universe per chartered seed, runs "
                "the shipped BABStrategy for equal and rank weighting, reports "
                "null recovery (must be exactly zero) and a bootstrap "
                "false-positive rate, and proves the reference seed reproduces "
                "the committed P21 panel sha256 values; never imports or calls a "
                "P21 build_* harness."
            ),
            "caveat": (
                "A null-universe positive result is a bug, not a finding. "
                "Planted recovery on this controlled synthetic universe proves "
                "the estimator works; it is never market alpha. NO-GO for "
                "market deployment until a maintainer supplies a licensed "
                "price series."
            ),
        },
        "seeds": seed_records,
    }


def _md(value) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def render_markdown(payload: dict) -> str:
    """Render the battery summary from the payload; no external numbers."""
    prov = payload["provenance"]
    summary = prov["summary"]
    lines = [
        "# BAB P22 WP1 — null battery over the chartered seeds",
        "",
        f"Schema `{payload['schema']}`. {prov['note']}",
        "",
        (
            f"{prov['n_seeds']} chartered seeds; reference seed "
            f"{prov['reference_universe_seed']} reproduces the committed P21 "
            f"panels: {_md(prov['reference_panel_sha256_matched'])}; bootstrap "
            f"{prov['bootstrap']['n_resamples']} resamples, block length "
            f"{prov['bootstrap']['block_length']}."
        ),
        "",
        "## Battery summary (from per-seed records only)",
        "",
        f"- Null books: {summary['n_null_books']}; planted books: "
        f"{summary['n_planted_books']}",
        f"- Null recovery max abs: {_md(summary['null_recovery_max_abs'])}",
        f"- Null recovery exactly zero every seed: "
        f"{_md(summary['null_recovery_exactly_zero_every_seed'])} "
        f"({summary['null_recovery_zero_books']}/{summary['n_null_books']} books)",
        f"- False-positive count: {summary['fpr_count']}/"
        f"{summary['fpr_denominator']} (rate {_md(summary['fpr_rate'])}, "
        f"expected {_md(summary['fpr_expected_count'])}, declared bound "
        f"{summary['fpr_max_count_declared']}, within bound "
        f"{_md(summary['fpr_within_declared_bound'])})",
        f"- Planted recovery positive fraction (equal): "
        f"{_md(summary['planted_recovery_positive_fraction']['equal'])}, "
        f"(rank): {_md(summary['planted_recovery_positive_fraction']['rank'])}",
        f"- Planted recovery min (equal): "
        f"{_md(summary['planted_recovery_min']['equal'])}, (rank): "
        f"{_md(summary['planted_recovery_min']['rank'])}",
        f"- Planted recovery exceeds null max: "
        f"{_md(summary['planted_recovery_exceeds_null_max'])}",
        "",
        "## Per-seed books",
        "",
        "| seed | variant | weighting | active_rows | gross_mean_active | "
        "recovery_mean | oos_sharpe | p_value | significant |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    columns = [
        "variant",
        "weighting",
        "active_rows",
        "gross_mean_active",
        "recovery_mean",
        "oos_sharpe",
        "p_value",
        "significant",
    ]
    for record in payload["seeds"]:
        for book in record["books"]:
            cells = [str(record["seed"])]
            cells.extend(_md(book[col]) for col in columns)
            lines.append("| " + " | ".join(cells) + " |")
    lines += [
        "",
        f"Method: {prov['method']}",
        "",
        f"Caveat: {prov['caveat']}",
    ]
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str = OUTPUT_DIR) -> tuple[Path, Path]:
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "null_battery.json"
    markdown_path = directory / "null_battery.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    started = time.perf_counter()
    payload = build_null_battery()
    json_path, markdown_path = write_artifacts(payload)
    elapsed = time.perf_counter() - started
    summary = payload["provenance"]["summary"]
    print(
        f"P22 WP1 null battery: seeds={summary['n_seeds']} "
        f"fpr={summary['fpr_count']}/{summary['fpr_denominator']} "
        f"null_zero={_md(summary['null_recovery_exactly_zero_every_seed'])} "
        f"planted_positive={summary['planted_recovery_positive_fraction']}"
    )
    print(f"reference_panel_sha256_matched="
          f"{payload['provenance']['reference_panel_sha256_matched']}")
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")
    print(f"build+runtime {elapsed:.3f}s")


if __name__ == "__main__":
    main()
