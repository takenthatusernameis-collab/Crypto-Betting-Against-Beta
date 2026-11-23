#!/usr/bin/env python3
"""P26 WP1 — Regime-conditional rank stress for rank-weighted BAB.

Splits the P25 WP0 wide synthetic universe into calm vs stress regimes by
60-day rolling BTC return volatility (median split), then runs the P25 WP2
rank walk-forward (train 180 / test 40, rank_min_leg_beta=0.20,
rank_max_gross=4.0) on the folds whose test window falls primarily in each
regime, computing mean OOS Sharpe for rank and equal weightings per regime.

Falsification gate (the reason P26 exists):
  (a) rank mean OOS Sharpe > 0 in the calm regime, AND
  (b) rank mean OOS Sharpe < equal mean OOS Sharpe in the stress regime.
If the rank premium does not survive regime stress, the P25 PROMOTE verdict
is qualified by regime — no real-market claim until rank survives regime stress.

Writes two artifacts:
  research_state/bab_p26/regime_stress.json  -- machine-readable
  research_state/bab_p26/regime_stress.md    -- human-readable

Single entry point: ``run_regime_stress()`` returns the results dict and
writes the JSON + markdown artifacts. ``build_regime_stress()`` does no writes.

Usage:
  python3 scripts/bab_p26_regime_stress.py
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta import BABStrategy, metrics  # noqa: E402
from strategies.betting_against_beta.beta import calculate_rolling_beta  # noqa: E402
from strategies.betting_against_beta.data_loader import load_prices  # noqa: E402

SCHEMA = "bab_p26.regime_stress/1"
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
VOL_WINDOW = 60
DECIMALS = 6
FLAT = 1e-9

WEIGHTINGS = ("equal", "rank")
REGIMES = ("calm", "stress")


def _clean(value) -> float | None:
    """Round a float to artifact precision, mapping non-finite to None."""
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    # + 0.0 normalizes -0.0 to 0.0 so the artifact is byte-stable across libraries.
    return round(number, DECIMALS) + 0.0


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def _load_and_prepare_fixture():
    """Load the P25 WP0 fixture and compute rolling betas once."""
    returns = load_prices(FIXTURE_CSV, benchmark=BENCHMARK, min_rows=2, quality=False)
    betas = calculate_rolling_beta(
        returns,
        BENCHMARK,
        window=BETA_WINDOW,
        min_obs=MIN_OBSERVATIONS,
    )
    return returns, betas


def _get_fold_indices():
    """Return list of (train_end, test_start, test_end) for each fold."""
    folds = []
    for k in range(N_FOLDS):
        train_end = TRAIN_WINDOW + TEST_WINDOW * k
        test_start = train_end
        test_end = test_start + TEST_WINDOW
        folds.append((train_end, test_start, test_end))
    return folds


def _btc_volatility(returns: pd.DataFrame) -> pd.Series:
    """Per-day BTC return volatility over a 60-day rolling window (causal)."""
    bench = returns[BENCHMARK].astype("float64")
    vol = bench.rolling(window=VOL_WINDOW, min_periods=VOL_WINDOW).std()
    return vol


def _regime_labels(vol: pd.Series) -> pd.Series:
    """Split the sample at the median volatility into calm / stress regimes.

    Low volatility -> calm, high volatility -> stress. Ties at the median go to
    calm. The median is computed over the full sample; each day's volatility is
    causal (rolling window looks backward only), so no future data is used to
    compute a day's vol. Regime assignment per fold uses only the test-window
    days' pre-computed labels.
    """
    median_vol = float(vol.median())
    labels = pd.Series("calm", index=vol.index, dtype=object)
    labels[vol > median_vol] = "stress"
    return labels


def _fold_regime(regime_labels: pd.Series, test_start: int, test_end: int) -> str | None:
    """Return the regime a fold's test window falls primarily in.

    A fold is assigned to the regime that covers the majority of its test
    days. Returns None if the test window is evenly split (no primary regime).
    """
    test_days = regime_labels.iloc[test_start:test_end]
    if len(test_days) == 0:
        return None
    counts = test_days.value_counts()
    if len(counts) == 1:
        return str(counts.index[0])
    if len(counts) == 2:
        majority = counts.idxmax()
        minority = counts.idxmin()
        if counts[majority] > counts[minority]:
            return str(majority)
        return None  # tie: no primary regime
    return str(counts.idxmax())


def _score_fold(returns: pd.DataFrame, weighting: str, test_start: int, test_end: int) -> dict:
    """Run one weighting on causal history [0, test_end) and score [test_start, test_end).

    Mirrors P25 WP2's _score_fold exactly: BABStrategy runs the full pipeline
    (rolling beta -> signals -> portfolio -> backtest with one-day lag) on
    returns[:test_end], then the OOS test slice is scored.
    """
    result = BABStrategy(**_strategy_config(weighting)).run(returns_df=returns.iloc[:test_end])
    weights = result.weights
    betas = result.betas
    backtest = result.backtest
    oos_returns = backtest["returns"].iloc[test_start:test_end]
    oos_weights = weights.iloc[test_start:test_end]
    oos_betas = betas.iloc[test_start:test_end]
    bench = returns[BENCHMARK].iloc[test_start:test_end]
    cumulative = (1.0 + oos_returns.astype("float64")).cumprod()
    wealth = float(cumulative.iloc[-1]) if len(cumulative) else 1.0
    return {
        "oos_sharpe": _clean(metrics.sharpe_ratio(oos_returns)),
        "oos_vol": _clean(metrics.annualized_volatility(oos_returns)),
        "oos_max_drawdown": _clean(metrics.max_drawdown(cumulative)),
        "oos_turnover": _clean(metrics.turnover(oos_weights)),
        "oos_realized_beta": _clean(metrics.strategy_beta(oos_returns, bench)),
        "oos_wealth": _clean(wealth),
        "portfolio_beta": _clean(metrics.portfolio_beta(oos_weights, oos_betas)),
        "nonflat_rows": int((oos_weights.abs().sum(axis=1) > FLAT).sum()),
    }


def _regime_result(
    returns: pd.DataFrame,
    regime_name: str,
    fold_indices: list,
    regime_labels: pd.Series,
) -> dict:
    """Run rank + equal on the folds assigned to a regime; return per-regime result."""
    assigned = []
    for fold_idx, (train_end, test_start, test_end) in enumerate(fold_indices):
        fold_regime = _fold_regime(regime_labels, test_start, test_end)
        if fold_regime == regime_name:
            assigned.append((fold_idx, train_end, test_start, test_end))

    per_fold = {"equal": [], "rank": []}
    for fold_idx, train_end, test_start, test_end in assigned:
        for weighting in WEIGHTINGS:
            scores = _score_fold(returns, weighting, test_start, test_end)
            scores["fold"] = fold_idx
            scores["test_start"] = test_start
            scores["test_end"] = test_end
            scores["train_end"] = train_end
            scores["regime"] = regime_name
            per_fold[weighting].append(scores)

    def mean_sharpe(weighting):
        sharpes = [f["oos_sharpe"] for f in per_fold[weighting] if f["oos_sharpe"] is not None]
        return _clean(sum(sharpes) / len(sharpes)) if sharpes else None

    rank_sharpes = [f["oos_sharpe"] for f in per_fold["rank"] if f["oos_sharpe"] is not None]
    equal_sharpes = [f["oos_sharpe"] for f in per_fold["equal"] if f["oos_sharpe"] is not None]
    mean_rank = _clean(sum(rank_sharpes) / len(rank_sharpes)) if rank_sharpes else None
    mean_equal = _clean(sum(equal_sharpes) / len(equal_sharpes)) if equal_sharpes else None

    return {
        "regime": regime_name,
        "n_folds_assigned": len(assigned),
        "folds_assigned": [f[0] for f in assigned],
        "equal": {
            "per_fold": per_fold["equal"],
            "mean_oos_sharpe": mean_equal,
        },
        "rank": {
            "per_fold": per_fold["rank"],
            "mean_oos_sharpe": mean_rank,
        },
        "delta_mean_oos_sharpe": (
            _clean(mean_rank - mean_equal)
            if mean_rank is not None and mean_equal is not None
            else None
        ),
    }


def _assertions(calm: dict, stress: dict) -> dict:
    """Evaluate the falsification gate assertions."""
    calm_rank = calm["rank"]["mean_oos_sharpe"]
    stress_rank = stress["rank"]["mean_oos_sharpe"]
    stress_equal = stress["equal"]["mean_oos_sharpe"]

    a_calm = (
        calm_rank is not None and calm_rank > 0
    )  # rank mean OOS Sharpe > 0 in calm
    b_stress = (
        stress_rank is not None
        and stress_equal is not None
        and stress_rank < stress_equal
    )  # rank < equal in stress

    return {
        "assertion_a_calm_rank_positive": bool(a_calm),
        "assertion_b_stress_rank_below_equal": bool(b_stress),
        "falsification_gate_passed": bool(a_calm and b_stress),
        "calm_rank_mean_oos_sharpe": calm_rank,
        "stress_rank_mean_oos_sharpe": stress_rank,
        "stress_equal_mean_oos_sharpe": stress_equal,
    }


def _provenance(returns: pd.DataFrame, fixture_sha: str, n_rows: int, vol: pd.Series) -> dict:
    median_vol = float(vol.median())
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
            "BTC volatility used for the regime split is a causal 60-day rolling "
            "standard deviation (looks backward only). Regime labels are computed once "
            "over the full sample; fold assignment uses only each fold's test-window days."
        ),
        "weightings": list(WEIGHTINGS),
        "regimes": list(REGIMES),
        "regime_split_rule": (
            "Per-day BTC return volatility over a 60-day rolling window; sample split at "
            "the median volatility into calm (low-vol) and stress (high-vol) regimes. "
            f"Median volatility: {median_vol:.6f}. A fold is assigned to the regime that "
            "covers the majority of its test-window days; ties are unassigned."
        ),
        "rank_rule": (
            "Frazzini-Pedersen rank weighting: long the lowest-beta quantile, short the "
            "highest-beta quantile, beta-neutral by construction, rank_min_leg_beta="
            f"{RANK_MIN_LEG_BETA}, rank_max_gross={RANK_MAX_GROSS}. Equal weighting is the "
            "dollar-neutral default with beta-neutral enforcement."
        ),
        "falsification_gate": (
            "Assertion A: rank mean OOS Sharpe > 0 in the calm regime. "
            "Assertion B: rank mean OOS Sharpe < equal mean OOS Sharpe in the stress regime. "
            "Both must hold for the gate to pass."
        ),
    }


def build_regime_stress(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the full regime-conditional rank stress and return the artifact dict. No file writes."""
    path = Path(fixture_path)
    if not path.is_absolute():
        path = _REPO_ROOT / path
    if not path.is_file():
        raise FileNotFoundError(f"fixture not found: {path}")

    returns, _betas = _load_and_prepare_fixture()
    n_rows = len(returns)
    needed = TRAIN_WINDOW + TEST_WINDOW * N_FOLDS
    if n_rows < needed:
        raise ValueError(
            f"fixture has {n_rows} return rows but regime stress needs {needed}"
        )

    fixture_sha = _sha256(path)

    # Regime split: causal 60-day rolling BTC volatility, median split.
    vol = _btc_volatility(returns)
    regime_labels = _regime_labels(vol)

    fold_indices = _get_fold_indices()

    regimes = {}
    for regime_name in REGIMES:
        regimes[regime_name] = _regime_result(
            returns, regime_name, fold_indices, regime_labels
        )

    assertions = _assertions(regimes["calm"], regimes["stress"])

    return {
        "schema": SCHEMA,
        "seed": SEED,
        "n_folds": N_FOLDS,
        "train_window": TRAIN_WINDOW,
        "test_window": TEST_WINDOW,
        "beta_window": BETA_WINDOW,
        "min_observations": MIN_OBSERVATIONS,
        "vol_window": VOL_WINDOW,
        "long_quantile": LONG_QUANTILE,
        "short_quantile": SHORT_QUANTILE,
        "rank_min_leg_beta": RANK_MIN_LEG_BETA,
        "rank_max_gross": RANK_MAX_GROSS,
        "transaction_costs": TRANSACTION_COSTS,
        "weightings": list(WEIGHTINGS),
        "fixture_sha256": fixture_sha,
        "synthetic": True,
        "provenance": _provenance(returns, fixture_sha, n_rows, vol),
        "regimes": regimes,
        "assertions": assertions,
    }


def run_regime_stress(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the regime stress, write JSON + markdown artifacts, return the dict."""
    payload = build_regime_stress(fixture_path)
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
    """Render the regime stress results as markdown."""
    lines = [
        "# P26 WP1 Regime-Conditional Rank Stress",
        "",
        f"**Falsification gate passed:** {payload['assertions']['falsification_gate_passed']}",
        "",
        f"**Seed:** {payload['seed']} | **Folds:** {payload['n_folds']} | "
        f"Train: {payload['train_window']} | Test: {payload['test_window']} | "
        f"Beta Window: {payload['beta_window']} | Min Obs: {payload['min_observations']} | "
        f"Vol Window: {payload['vol_window']} | Quantiles: {payload['long_quantile']}/"
        f"{payload['short_quantile']} | Rank Min Leg Beta: {payload['rank_min_leg_beta']} | "
        f"Rank Max Gross: {payload['rank_max_gross']} | Costs: {payload['transaction_costs']}",
        "",
        f"**Fixture SHA256:** {payload['fixture_sha256']}",
        "",
        "## Regime Split",
        "",
        "| Regime | Folds Assigned | Fold Indices |",
        "|---|---|---|",
    ]
    for regime_name in REGIMES:
        reg = payload["regimes"][regime_name]
        lines.append(
            f"| {regime_name} | {reg['n_folds_assigned']} | {reg['folds_assigned']} |"
        )
    lines.append("")
    lines.append("## Per-Regime Mean OOS Sharpe")
    lines.append("")
    lines.append("| Regime | Weighting | Mean OOS Sharpe | N Folds |")
    lines.append("|---|---|---|---|")
    for regime_name in REGIMES:
        reg = payload["regimes"][regime_name]
        lines.extend(
            f"| {regime_name} | {weighting} | "
            f"{_format(reg[weighting]['mean_oos_sharpe'])} | "
            f"{len(reg[weighting]['per_fold'])} |"
            for weighting in WEIGHTINGS
        )
    lines.append("")
    lines.append("## Falsification Gate Assertions")
    lines.append("")
    lines.append("| Assertion | Passed | Value |")
    lines.append("|---|---|---|")
    a = payload["assertions"]
    lines.append(
        f"| A: rank mean OOS Sharpe > 0 in calm | "
        f"{a['assertion_a_calm_rank_positive']} | {_format(a['calm_rank_mean_oos_sharpe'])} |"
    )
    lines.append(
        f"| B: rank mean OOS Sharpe < equal in stress | "
        f"{a['assertion_b_stress_rank_below_equal']} | "
        f"rank={_format(a['stress_rank_mean_oos_sharpe'])} < "
        f"equal={_format(a['stress_equal_mean_oos_sharpe'])} |"
    )
    lines.append(
        f"| Falsification gate passed | {a['falsification_gate_passed']} | - |"
    )
    lines.append("")
    lines.append("## Per-Fold Detail")
    lines.append("")
    lines.append(
        "| Regime | Fold | Weighting | Test Start | Test End | "
        "OOS Sharpe | Portfolio Beta | Nonflat Rows |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")
    for regime_name in REGIMES:
        reg = payload["regimes"][regime_name]
        lines.extend(
            f"| {regime_name} | {f['fold']} | {weighting} | "
            f"{f['test_start']} | {f['test_end']} | "
            f"{_format(f['oos_sharpe'])} | {_format(f['portfolio_beta'])} | "
            f"{f['nonflat_rows']} |"
            for weighting in WEIGHTINGS
            for f in reg[weighting]["per_fold"]
        )
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str | Path = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "regime_stress.json"
    markdown_path = directory / "regime_stress.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    payload = run_regime_stress()
    a = payload["assertions"]
    print(
        f"wrote {OUTPUT_DIR / 'regime_stress.json'} "
        f"({payload['n_folds']} folds x {len(WEIGHTINGS)} weightings x {len(REGIMES)} regimes)"
    )
    print(f"wrote {OUTPUT_DIR / 'regime_stress.md'}")
    print(f"Assertion A (calm rank > 0): {a['assertion_a_calm_rank_positive']}")
    print(f"Assertion B (stress rank < equal): {a['assertion_b_stress_rank_below_equal']}")
    print(f"Falsification gate passed: {a['falsification_gate_passed']}")


if __name__ == "__main__":
    main()
