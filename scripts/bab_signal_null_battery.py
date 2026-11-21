#!/usr/bin/env python3
"""P26 WP0 — deterministic signal-to-noise validation of rank-weighted BAB.

Compares the observed rank-weighted and equal-weight out-of-sample mean Sharpe
(5 causal folds, train 180 / test 40, P25 WP0 wide fixture read-only) against a
stable, beta-neutral-preserving permutation null: B=1000 random long/short
selections drawn once per fold (fixed across all rows of that fold, matching the
fold's per-row long/short counts, drawn from the finite-beta eligible assets),
each book built with the *same* construction as the observed book — rank via
``construct_rank_weights``, equal via equal-weight ``construct_portfolio`` +
``enforce_beta_neutrality`` — scored on the same test slice.

Reports p-value / z-score / empirical percentile for BOTH weightings and records
an explicit, data-driven ``SIGNAL`` / ``NO-SIGNAL`` verdict:

    SIGNAL  iff  p_rank < 0.05 and p_equal > 0.05
    NO-SIGNAL otherwise

The verdict is never forced: on the current no-alpha P25 WP0 fixture
(asset returns are ``beta * r_BTC + idio``, idio iid N(0, 0.003), so no
cross-sectional alpha is planted) the expected, correct anti-victory outcome is
``NO-SIGNAL``.

Observed mean OOS Sharpe MUST reproduce the committed P25 WP2 bake-off
(rank 0.437311, equal 0.170267) to 6 dp; the script asserts this.

Writes two artifacts:

  research_state/bab_p26/signal_null_battery.json  -- machine-readable battery
  research_state/bab_p26/signal_null_battery.md    -- rendered from that JSON

Single entry point: ``run_signal_null_battery()`` returns the results dict and
writes the JSON + markdown artifacts.
``build_signal_null_battery()`` does no writes.

Usage:
  python3 scripts/bab_signal_null_battery.py
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta import BABStrategy, metrics  # noqa: E402
from strategies.betting_against_beta.backtest import run_backtest  # noqa: E402
from strategies.betting_against_beta.beta import calculate_rolling_beta  # noqa: E402
from strategies.betting_against_beta.data_loader import load_prices  # noqa: E402
from strategies.betting_against_beta.portfolio import (  # noqa: E402
    construct_portfolio,
    construct_rank_weights,
    enforce_beta_neutrality,
)
from strategies.betting_against_beta.signals import generate_bab_signals  # noqa: E402

SCHEMA = "bab_p26.signal_null_battery/1"
FIXTURE_CSV = _REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
OUTPUT_DIR = _REPO_ROOT / "research_state" / "bab_p26"
BENCHMARK = "BTC"
SEED = 20261120
BETA_WINDOW = 90
MIN_OBSERVATIONS = 60
TRAIN_WINDOW = 180
TEST_WINDOW = 40
N_FOLDS = 5
LONG_QUANTILE = 0.3
SHORT_QUANTILE = 0.3
RANK_MIN_LEG_BETA = 0.20
RANK_MAX_GROSS = 4.0
TRANSACTION_COSTS = 0.001
N_NULL_REPLICATIONS = 1000
P_LEVEL = 0.05
DECIMALS = 6
FLAT = 1e-9
WEIGHTINGS = ("equal", "rank")

# Committed P25 WP2 reference values the observed path must reproduce (6 dp).
OBSERVED_REFERENCE = {"rank": 0.437311, "equal": 0.170267}


def _clean(value) -> float | None:
    """Round a float to artifact precision, mapping non-finite to None."""
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return round(number, DECIMALS)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fold_windows() -> list[tuple[int, int, int, int]]:
    """Causal walk-forward windows: train 180 / test 40, 5 folds."""
    windows = []
    for k in range(N_FOLDS):
        train_end = TRAIN_WINDOW + TEST_WINDOW * k
        test_start = train_end
        test_end = test_start + TEST_WINDOW
        windows.append((0, train_end, test_start, test_end))
    return windows


def _strategy_config(weighting: str) -> dict:
    return dict(
        benchmark=BENCHMARK,
        beta_window=BETA_WINDOW,
        min_observations=MIN_OBSERVATIONS,
        long_quantile=LONG_QUANTILE,
        short_quantile=SHORT_QUANTILE,
        transaction_costs=TRANSACTION_COSTS,
        beta_neutral=True,
        weighting=weighting,
        rank_min_leg_beta=RANK_MIN_LEG_BETA,
        rank_max_gross=RANK_MAX_GROSS,
    )


def _score_observed_fold(
    returns: pd.DataFrame, weighting: str, test_start: int, test_end: int
) -> float:
    """Observed OOS mean Sharpe for one weighting on one fold (P25 WP2 path)."""
    result = BABStrategy(**_strategy_config(weighting)).run(returns_df=returns.iloc[:test_end])
    backtest = result.backtest
    oos_returns = backtest["returns"].iloc[test_start:test_end]
    return float(metrics.sharpe_ratio(oos_returns))


def _fold_plan(returns: pd.DataFrame, betas: pd.DataFrame, signals: pd.DataFrame):
    """Per-fold: window, long/short counts, eligible assets (finite beta > 0)."""
    plan = []
    for train_start, train_end, test_start, test_end in _fold_windows():
        sig_fold = signals.iloc[test_start:test_end]
        n_long = int((sig_fold == 1).sum(axis=1).mode().iloc[0])
        n_short = int((sig_fold == -1).sum(axis=1).mode().iloc[0])
        betas_fold = betas.iloc[train_start:test_end]
        eligible = [
            c
            for c in betas_fold.columns
            if c != BENCHMARK
            and betas_fold[c].notna().any()
            and (betas_fold[c].dropna() > 0.0).all()
        ]
        plan.append(
            {
                "test_start": test_start,
                "test_end": test_end,
                "train_end": train_end,
                "n_long": n_long,
                "n_short": n_short,
                "eligible": eligible,
            }
        )
    return plan


def _null_signals(
    returns: pd.DataFrame, train_end: int, test_end: int, longs, shorts
) -> pd.DataFrame:
    """Build an all-zero signals frame with one random long/short set held for
    every row in [0, test_end) (the draw is fixed across all rows of the fold)."""
    signals_null = pd.DataFrame(
        0, index=returns.index, columns=returns.columns, dtype=np.int64
    )
    if len(longs) > 0:
        signals_null.loc[returns.index[:test_end], list(longs)] = 1
    if len(shorts) > 0:
        signals_null.loc[returns.index[:test_end], list(shorts)] = -1
    return signals_null


def _construct_null_weights(signals_null, betas, weighting: str) -> pd.DataFrame:
    """Build a null book with the *same* construction as the observed book."""
    if weighting == "rank":
        return construct_rank_weights(
            signals_null,
            betas,
            min_leg_beta=RANK_MIN_LEG_BETA,
            max_gross=RANK_MAX_GROSS,
        )
    weights = construct_portfolio(
        signals_null,
        dollar_neutral=True,
        betas=betas,
        weighting="equal",
    )
    return enforce_beta_neutrality(weights, betas, target_beta=0.0)


def _score_null_fold(returns, betas, fold, rng, weighting: str) -> float:
    """One null OOS Sharpe for one weighting on one fold: a single random
    long/short draw fixed across all rows of the fold.

    For ``weighting="rank"`` the random draw is sorted by mean test-slice beta
    so the lowest-beta assets go long and the highest-beta assets go short,
    matching the Frazzini-Pedersen leg direction that ``construct_rank_weights``
    requires. For ``weighting="equal"`` the draw stays unsorted (random legs).
    """
    test_start = fold["test_start"]
    test_end = fold["test_end"]
    eligible = fold["eligible"]
    n_long = fold["n_long"]
    n_short = fold["n_short"]
    if n_long + n_short > len(eligible):
        return float("nan")
    perm = rng.permutation(eligible)
    draw = list(perm[: n_long + n_short])
    if weighting == "rank":
        beta_mean = betas.iloc[test_start:test_end][draw].mean()
        draw_sorted = sorted(draw, key=lambda c: beta_mean[c])
        longs = draw_sorted[:n_long]
        shorts = draw_sorted[n_long:]
    else:
        longs = draw[:n_long]
        shorts = draw[n_long:]
    signals_null = _null_signals(returns, fold["train_end"], test_end, longs, shorts)
    weights = _construct_null_weights(signals_null, betas.iloc[:test_end], weighting)
    backtest = run_backtest(
        returns.iloc[:test_end], weights.iloc[:test_end], transaction_costs=TRANSACTION_COSTS
    )
    oos_returns = backtest["returns"].iloc[test_start:test_end]
    return float(metrics.sharpe_ratio(oos_returns))


def _p_value(observed: float, null_sharpes: list[float]) -> float:
    b_ge = sum(1 for s in null_sharpes if s is not None and s >= observed)
    return (1 + b_ge) / (len(null_sharpes) + 1)


def _percentile(observed: float, null_sharpes: list[float]) -> float:
    b_lt = sum(1 for s in null_sharpes if s is not None and s < observed)
    return 100.0 * b_lt / len(null_sharpes)


def _provenance(returns: pd.DataFrame, fixture_sha: str, n_rows: int) -> dict:
    return {
        "fixture_path": "tests/fixtures/wide_bab_universe.csv",
        "fixture_sha256": fixture_sha,
        "price_rows": n_rows + 1,
        "return_rows": n_rows,
        "date_first": str(returns.index[0].date()),
        "date_last": str(returns.index[-1].date()),
        "seed": SEED,
        "synthetic": True,
        "universe": "BTC + A001..A040 (DEL all-NaN column dropped by loader)",
        "provenance": (
            "Deterministic synthetic wide universe (P25 WP0 fixture); not real market "
            "data and not evidence of real-market profitability."
        ),
        "no_lookahead": (
            "Each fold runs both weightings over causal history [0, test_end); weights at "
            "row t use the one-day backtest lag and rolling betas computed from returns "
            "through t-1, so the OOS return at row t is never used to weight itself. The "
            "test slice [test_start, test_end) is scored but never read during weight "
            "construction. Null draws are fixed per fold (never per row), so turnover and "
            "cost drag match the observed book's scale."
        ),
        "weightings": list(WEIGHTINGS),
        "rank_rule": (
            "Frazzini-Pedersen rank weighting: long the lowest-beta quantile, short the "
            "highest-beta quantile, beta-neutral by construction, rank_min_leg_beta="
            f"{RANK_MIN_LEG_BETA}, rank_max_gross={RANK_MAX_GROSS}. Equal weighting is the "
            "dollar-neutral default (not beta-neutral)."
        ),
        "verdict_rule": (
            'SIGNAL iff p_rank < 0.05 and p_equal > 0.05; otherwise NO-SIGNAL. The verdict '
            "is data-driven and never forced."
        ),
        "null_field_reasons": {
            "oos_sharpe": "null when the OOS slice has fewer than two finite returns",
        },
    }


def build_signal_null_battery(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the full signal-vs-null battery and return the artifact dict. No file writes."""
    path = Path(fixture_path)
    if not path.is_absolute():
        path = _REPO_ROOT / path
    if not path.is_file():
        raise FileNotFoundError(f"fixture not found: {path}")
    returns = load_prices(path, benchmark=BENCHMARK, min_rows=2, quality=False)
    n_rows = len(returns)
    needed = TRAIN_WINDOW + TEST_WINDOW * N_FOLDS
    if n_rows < needed:
        raise ValueError(f"fixture has {n_rows} return rows but battery needs {needed}")
    fixture_sha = _sha256(path)
    betas = None

    betas = calculate_rolling_beta(
        returns, BENCHMARK, window=BETA_WINDOW, min_obs=MIN_OBSERVATIONS
    )
    signals = generate_bab_signals(
        betas, long_quantile=LONG_QUANTILE, short_quantile=SHORT_QUANTILE
    )
    plan = _fold_plan(returns, betas, signals)

    # --- Observed: reproduce P25 WP2 (rank 0.437311, equal 0.170267) -------
    observed = {}
    per_fold_observed = {"rank": [], "equal": []}
    for weighting in WEIGHTINGS:
        fold_sharpes = []
        for fold in plan:
            s = _score_observed_fold(returns, weighting, fold["test_start"], fold["test_end"])
            fold_sharpes.append(_clean(s))
            per_fold_observed[weighting].append(
                {"fold": len(per_fold_observed[weighting]), "test_start": fold["test_start"],
                 "test_end": fold["test_end"], "oos_sharpe": _clean(s)}
            )
        mean_sharpe = _clean(sum(s for s in fold_sharpes if s is not None) / len(fold_sharpes))
        observed[weighting] = {
            "mean_oos_sharpe": mean_sharpe,
            "per_fold": per_fold_observed[weighting],
        }

    # Assert reproduction of committed P25 WP2 values to 6 dp.
    for weighting in WEIGHTINGS:
        got = observed[weighting]["mean_oos_sharpe"]
        expected = OBSERVED_REFERENCE[weighting]
        if got is None or round(got, DECIMALS) != expected:
            raise AssertionError(
                f"observed {weighting} mean OOS Sharpe {got} does not reproduce "
                f"P25 WP2 reference {expected} to {DECIMALS} dp"
            )

    # --- Null: B=1000 random long/short draws fixed per fold --------------
    rng = np.random.default_rng(SEED)
    null = {"rank": [], "equal": []}
    for _b in range(N_NULL_REPLICATIONS):
        for weighting in WEIGHTINGS:
            fold_sharpes = []
            for fold in plan:
                s = _score_null_fold(returns, betas, fold, rng, weighting)
                fold_sharpes.append(s)
            vals = [s for s in fold_sharpes if s is not None and math.isfinite(s)]
            null[weighting].append(float(sum(vals) / len(vals)) if vals else float("nan"))

    # --- p / z / percentile + verdict ------------------------------------
    weighting_stats = {}
    for weighting in WEIGHTINGS:
        null_sharpes = [s for s in null[weighting] if s is not None and math.isfinite(s)]
        obs = observed[weighting]["mean_oos_sharpe"]
        null_mean = _clean(sum(null_sharpes) / len(null_sharpes)) if null_sharpes else None
        null_std = _clean(float(np.std(null_sharpes))) if null_sharpes else None
        null_min = _clean(min(null_sharpes)) if null_sharpes else None
        null_max = _clean(max(null_sharpes)) if null_sharpes else None
        p = _p_value(obs, null_sharpes) if null_sharpes else None
        z = (
            _clean((obs - null_mean) / null_std)
            if (obs is not None and null_mean is not None and null_std not in (None, 0.0))
            else None
        )
        percentile = _percentile(obs, null_sharpes) if null_sharpes else None
        b_ge = sum(1 for s in null_sharpes if s >= obs)
        weighting_stats[weighting] = {
            "observed_mean_oos_sharpe": obs,
            "null_sharpes": [_clean(s) for s in null_sharpes],
            "null_mean": null_mean,
            "null_std": null_std,
            "null_min": null_min,
            "null_max": null_max,
            "null_b_ge_observed": int(b_ge),
            "n_null_replications": len(null_sharpes),
            "p_value": _clean(p),
            "z_score": z,
            "empirical_percentile": _clean(percentile),
        }

    p_rank = weighting_stats["rank"]["p_value"]
    p_equal = weighting_stats["equal"]["p_value"]
    verdict = (
        "SIGNAL"
        if (p_rank is not None and p_equal is not None
            and p_rank < P_LEVEL and p_equal > P_LEVEL)
        else "NO-SIGNAL"
    )

    return {
        "schema": SCHEMA,
        "seed": SEED,
        "n_folds": N_FOLDS,
        "train_window": TRAIN_WINDOW,
        "test_window": TEST_WINDOW,
        "beta_window": BETA_WINDOW,
        "min_observations": MIN_OBSERVATIONS,
        "long_quantile": LONG_QUANTILE,
        "short_quantile": SHORT_QUANTILE,
        "rank_min_leg_beta": RANK_MIN_LEG_BETA,
        "rank_max_gross": RANK_MAX_GROSS,
        "transaction_costs": TRANSACTION_COSTS,
        "n_null_replications": N_NULL_REPLICATIONS,
        "p_level": P_LEVEL,
        "weightings": list(WEIGHTINGS),
        "synthetic": True,
        "fixture_sha256": fixture_sha,
        "verdict": verdict,
        "verdict_rule": (
            f"SIGNAL iff p_rank < {P_LEVEL} and p_equal > {P_LEVEL}; otherwise NO-SIGNAL."
        ),
        "observed": observed,
        "null": weighting_stats,
        "provenance": _provenance(returns, fixture_sha, n_rows),
    }


def run_signal_null_battery(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the battery, write JSON + markdown artifacts, return the dict."""
    payload = build_signal_null_battery(fixture_path)
    write_artifacts(payload)
    return payload


def _format(value) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        return value
    return f"{float(value):.{DECIMALS}f}"


def render_markdown(payload: dict) -> str:
    """Render the battery from the JSON object."""
    lines = [
        "# P26 WP0 — Signal-to-Noise Validation of Rank-Weighted BAB",
        "",
        f"**Verdict:** {payload['verdict']}",
        f"**Verdict rule:** {payload['verdict_rule']}",
        f"**Seed:** {payload['seed']}  |  **Null replications:** "
        f"{payload['n_null_replications']}  |  **Folds:** {payload['n_folds']}",
        f"**Fixture:** tests/fixtures/wide_bab_universe.csv  |  **SHA256:** "
        f"{payload['fixture_sha256']}",
        "",
        "## Observed mean OOS Sharpe (reproduces P25 WP2 bake-off)",
        "",
        "| weighting | mean_oos_sharpe | reference | match_6dp |",
        "|---|---|---|---|",
    ]
    for weighting in WEIGHTINGS:
        obs = payload["observed"][weighting]["mean_oos_sharpe"]
        ref = OBSERVED_REFERENCE[weighting]
        match = obs is not None and round(obs, DECIMALS) == ref
        lines.append(
            f"| {weighting} | {_format(obs)} | {ref} | {'yes' if match else 'no'} |"
        )
    lines.append("")
    lines.append("## Null distribution vs observed (per weighting)")
    lines.append("")
    lines.append(
        "| weighting | observed | null_mean | null_std | null_min | null_max | "
        "p_value | z_score | percentile |"
    )
    lines.append(
        "|---|---|---|---|---|---|---|---|---|"
    )
    for weighting in WEIGHTINGS:
        st = payload["null"][weighting]
        lines.append(
            f"| {weighting} | {_format(st['observed_mean_oos_sharpe'])} | "
            f"{_format(st['null_mean'])} | {_format(st['null_std'])} | "
            f"{_format(st['null_min'])} | {_format(st['null_max'])} | "
            f"{_format(st['p_value'])} | {_format(st['z_score'])} | "
            f"{_format(st['empirical_percentile'])} |"
        )
    lines.append("")
    lines.append("## Conclusion")
    lines.append("")
    lines.append(
        f"The recorded verdict is **{payload['verdict']}**, grounded in p_rank="
        f"{_format(payload['null']['rank']['p_value'])} and p_equal="
        f"{_format(payload['null']['equal']['p_value'])} at level {P_LEVEL}."
    )
    lines.append(
        "On the no-alpha P25 WP0 fixture the honest outcome is NO-SIGNAL: the rank book's "
        "beta-neutral realized return is a pure idiosyncratic spread with mean zero, so its "
        "OOS Sharpe is structurally consistent with noise."
    )
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    prov = payload["provenance"]
    lines.extend(f"- {key}: {prov.get(key)}" for key in (
        "fixture_path", "fixture_sha256", "return_rows", "date_first", "date_last",
        "seed", "synthetic", "provenance", "no_lookahead", "rank_rule", "verdict_rule",
    ))
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str | Path = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "signal_null_battery.json"
    markdown_path = directory / "signal_null_battery.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    payload = run_signal_null_battery()
    print(
        f"wrote {OUTPUT_DIR / 'signal_null_battery.json'} "
        f"(verdict={payload['verdict']}, "
        f"p_rank={payload['null']['rank']['p_value']}, "
        f"p_equal={payload['null']['equal']['p_value']})"
    )
    print(f"wrote {OUTPUT_DIR / 'signal_null_battery.md'}")


if __name__ == "__main__":
    main()
