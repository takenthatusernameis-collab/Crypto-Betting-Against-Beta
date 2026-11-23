#!/usr/bin/env python3
"""P26 WP2 — deterministic capacity & turnover sweep of the rank-weighted BAB book.

Sweeps gross exposure caps [1.0, 2.0, 3.0, 4.0] x rebalance frequencies
[daily, weekly, monthly] on the P25 WP0 wide synthetic universe fixture
(read-only), running the P25 WP2 walk-forward (train 180 / test 40,
rank_min_leg_beta=0.20, rank_max_gross=<cell cap>) for both rank and equal
weightings on identical causal folds.

For each (gross_cap, rebalance_freq) cell measures OOS Sharpe, turnover, wealth
and a capacity break-even estimate (the AUM at which estimated square-root
market-impact costs exceed the cell's net mean OOS daily return) for rank vs
equal, and records a summary verdict: rank survives capacity / rank does not
survive capacity.

Writes two artifacts:

  research_state/bab_p26/rank_capacity.json  -- machine-readable cells + aggregate + verdict
  research_state/bab_p26/rank_capacity.md    -- table rendered from that JSON in memory

Single entry point: ``run_capacity_sweep()`` returns the results dict and writes
the JSON + markdown artifacts. ``build_capacity_sweep()`` does no writes.

Usage:
  python3 scripts/bab_rank_capacity.py
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
from strategies.betting_against_beta.data_loader import load_prices  # noqa: E402

SCHEMA = "bab_p26.rank_capacity/1"
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
RANK_MAX_GROSS_DEFAULT = 4.0
TRANSACTION_COSTS = 0.001
GROSS_CAPS = (1.0, 2.0, 3.0, 4.0)
REBALANCE_FREQS = ("daily", "weekly", "monthly")
DECIMALS = 6
FLAT = 1e-9

# Capacity break-even model (documented estimate, not market evidence):
#   net_daily_return = mean(OOS daily returns)   [already net of flat txn costs]
#   daily_turnover   = mean(OOS turnover)
#   impact_cost(AUM) = IMPACT_GAMMA * daily_turnover * sqrt(AUM / REF_AUM)
#   break-even AUM solves impact_cost(AUM) = net_daily_return
# If net_daily_return <= 0 or turnover <= 0 the book never covers even flat
# costs and break-even is None.
CAPACITY_REF_AUM = 1_000_000.0
CAPACITY_IMPACT_GAMMA = 1e-4

WEIGHTINGS = ("equal", "rank")

CELL_FIELDS = (
    "cell",
    "gross_cap",
    "rebalance_freq",
    "weighting",
    "mean_oos_sharpe",
    "mean_oos_turnover",
    "mean_oos_wealth",
    "mean_portfolio_beta",
    "mean_nonflat_rows",
    "capacity_break_even_aum",
)
AGGREGATE_FIELDS = (
    "gross_caps",
    "rebalance_freqs",
    "rank_min_leg_beta",
    "rank_max_gross_default",
    "cells_evaluated",
    "candidates_evaluated",
    "rank_survives_capacity",
    "verdict",
    "default_cell_gross_cap",
    "default_cell_rebalance_freq",
    "rank_beats_equal_default_cell",
)


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


def _strategy_config(weighting: str, rank_max_gross: float, rebalance_freq: str) -> dict:
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
        rank_max_gross=rank_max_gross,
        rebalance_freq=rebalance_freq,
    )


def _score_fold(returns: pd.DataFrame, weighting: str, rank_max_gross: float,
                rebalance_freq: str, test_start: int, test_end: int) -> dict:
    """Run one weighting on causal history [0, test_end) and score [test_start, test_end).

    Mirrors P25 WP2's _score_fold exactly: BABStrategy runs the full pipeline
    (rolling beta -> signals -> portfolio -> backtest with one-day lag) on
    returns[:test_end], then the OOS test slice is scored.
    """
    result = BABStrategy(**_strategy_config(weighting, rank_max_gross, rebalance_freq)).run(
        returns_df=returns.iloc[:test_end]
    )
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
        "mean_oos_return": _clean(float(oos_returns.mean()) if len(oos_returns) else None),
    }


def _capacity_break_even_aum(
    net_daily_return: float | None, turnover: float | None
) -> float | None:
    """AUM at which square-root impact costs exceed the net daily return.

    Returns None when the book never covers even flat costs (net return <= 0)
    or turnover is zero / non-finite.
    """
    if net_daily_return is None or turnover is None:
        return None
    if not (math.isfinite(net_daily_return) and math.isfinite(turnover)):
        return None
    if net_daily_return <= 0.0 or turnover <= 0.0:
        return None
    ratio = net_daily_return / (CAPACITY_IMPACT_GAMMA * turnover)
    return _clean(CAPACITY_REF_AUM * ratio * ratio)


def _fold_indices():
    folds = []
    for k in range(N_FOLDS):
        train_end = TRAIN_WINDOW + TEST_WINDOW * k
        test_start = train_end
        test_end = test_start + TEST_WINDOW
        folds.append((train_end, test_start, test_end))
    return folds


def _build_cell(returns: pd.DataFrame, gross_cap: float, rebalance_freq: str) -> dict:
    """Evaluate one (gross_cap, rebalance_freq) cell across both weightings."""
    cell = {
        "gross_cap": gross_cap,
        "rebalance_freq": rebalance_freq,
        "rank_max_gross": gross_cap,
        "weightings": list(WEIGHTINGS),
        "results": {},
        "delta": {},
        "capacity_break_even": {},
    }
    for weighting in WEIGHTINGS:
        per_fold = []
        for fold_idx, (train_end, test_start, test_end) in enumerate(_fold_indices()):
            scores = _score_fold(
                returns, weighting, gross_cap, rebalance_freq, test_start, test_end
            )
            scores["fold"] = fold_idx
            scores["test_start"] = test_start
            scores["test_end"] = test_end
            per_fold.append(scores)

        def _mean(field):
            vals = [f[field] for f in per_fold if f.get(field) is not None]
            return _clean(sum(vals) / len(vals)) if vals else None

        sharpe = _mean("oos_sharpe")
        turnover = _mean("oos_turnover")
        wealth = _mean("oos_wealth")
        pb = _mean("portfolio_beta")
        nfr = _mean("nonflat_rows")
        net_return = _mean("mean_oos_return")
        cell["results"][weighting] = {
            "per_fold": per_fold,
            "mean_oos_sharpe": sharpe,
            "mean_oos_turnover": turnover,
            "mean_oos_wealth": wealth,
            "mean_portfolio_beta": pb,
            "mean_nonflat_rows": nfr,
            "mean_oos_return": net_return,
        }
        cell["capacity_break_even"][weighting] = _capacity_break_even_aum(net_return, turnover)

    rank = cell["results"]["rank"]
    equal = cell["results"]["equal"]
    cell["delta"] = {
        "delta_oos_sharpe": _clean(rank["mean_oos_sharpe"] - equal["mean_oos_sharpe"])
        if rank["mean_oos_sharpe"] is not None and equal["mean_oos_sharpe"] is not None
        else None,
        "delta_oos_turnover": _clean(rank["mean_oos_turnover"] - equal["mean_oos_turnover"])
        if rank["mean_oos_turnover"] is not None and equal["mean_oos_turnover"] is not None
        else None,
        "delta_oos_wealth": _clean(rank["mean_oos_wealth"] - equal["mean_oos_wealth"])
        if rank["mean_oos_wealth"] is not None and equal["mean_oos_wealth"] is not None
        else None,
    }
    return cell


def _verdict_rule() -> str:
    return (
        "rank survives capacity iff rank mean OOS Sharpe > equal mean OOS Sharpe at "
        f"the default cell (gross_cap={RANK_MAX_GROSS_DEFAULT}, rebalance_freq=daily); "
        "otherwise rank does not survive capacity. Data-driven, not a forced outcome."
    )


def build_capacity_sweep(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the full capacity & turnover sweep and return the artifact dict. No file writes."""
    path = Path(fixture_path)
    if not path.is_absolute():
        path = _REPO_ROOT / path
    if not path.is_file():
        raise FileNotFoundError(f"fixture not found: {path}")
    returns = load_prices(path, benchmark=BENCHMARK, min_rows=2, quality=False)
    n_rows = len(returns)
    needed = TRAIN_WINDOW + TEST_WINDOW * N_FOLDS
    if n_rows < needed:
        raise ValueError(f"fixture has {n_rows} return rows but capacity sweep needs {needed}")
    fixture_sha = _sha256(path)

    cells = []
    cell_index = 0
    for gross_cap in GROSS_CAPS:
        for rebalance_freq in REBALANCE_FREQS:
            cell = _build_cell(returns, gross_cap, rebalance_freq)
            cell["cell"] = cell_index
            cells.append(cell)
            cell_index += 1

    default_cell = next(
        c for c in cells
        if c["gross_cap"] == RANK_MAX_GROSS_DEFAULT and c["rebalance_freq"] == "daily"
    )
    d_rank = default_cell["results"]["rank"]
    d_equal = default_cell["results"]["equal"]
    rank_beats_equal_default = (
        d_rank["mean_oos_sharpe"] is not None
        and d_equal["mean_oos_sharpe"] is not None
        and d_rank["mean_oos_sharpe"] > d_equal["mean_oos_sharpe"]
    )
    rank_survives = bool(rank_beats_equal_default)

    aggregate = {
        "gross_caps": list(GROSS_CAPS),
        "rebalance_freqs": list(REBALANCE_FREQS),
        "rank_min_leg_beta": RANK_MIN_LEG_BETA,
        "rank_max_gross_default": RANK_MAX_GROSS_DEFAULT,
        "cells_evaluated": len(cells),
        "candidates_evaluated": len(cells) * len(WEIGHTINGS) * N_FOLDS,
        "rank_survives_capacity": rank_survives,
        "verdict": (
            "rank survives capacity"
            if rank_survives
            else "rank does not survive capacity"
        ),
        "default_cell_gross_cap": default_cell["gross_cap"],
        "default_cell_rebalance_freq": default_cell["rebalance_freq"],
        "rank_beats_equal_default_cell": rank_beats_equal_default,
        "cells": cells,
    }

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
        "rank_max_gross": RANK_MAX_GROSS_DEFAULT,
        "transaction_costs": TRANSACTION_COSTS,
        "weightings": list(WEIGHTINGS),
        "gross_caps": list(GROSS_CAPS),
        "rebalance_freqs": list(REBALANCE_FREQS),
        "fixture_sha256": fixture_sha,
        "synthetic": True,
        "provenance": _provenance(returns, fixture_sha, n_rows),
        "aggregate": aggregate,
        "cells": cells,
    }


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
            "Each cell runs both weightings over causal history [0, test_end); weights at "
            "row t use the one-day backtest lag and rolling betas computed from returns "
            "through t-1, so the OOS return at row t is never used to weight itself. The "
            "test slice [test_start, test_end) is scored but never read during weight "
            "construction for that row. Equal and rank are run on identical folds."
        ),
        "weightings": list(WEIGHTINGS),
        "rank_rule": (
            "Frazzini-Pedersen rank weighting: long the lowest-beta quantile, short the "
            "highest-beta quantile, beta-neutral by construction, rank_min_leg_beta="
            f"{RANK_MIN_LEG_BETA}, rank_max_gross=<cell cap>. Equal weighting is the "
            "dollar-neutral default (rank_max_gross has no effect on it)."
        ),
        "gross_cap_sweep": (
            f"Gross exposure caps {list(GROSS_CAPS)} applied as rank_max_gross; rank rows "
            "flatten when gross exceeds the cap, never rescaled."
        ),
        "rebalance_sweep": (
            f"Rebalance frequencies {list(REBALANCE_FREQS)}; weights held constant between "
            "rebalance dates (one-day lag preserved)."
        ),
        "capacity_break_even_model": (
            f"Square-root impact estimate: impact_cost(AUM) = {CAPACITY_IMPACT_GAMMA} * "
            "turnover * sqrt(AUM / {CAPACITY_REF_AUM:g}); break-even AUM solves "
            "impact_cost(AUM) = net mean OOS daily return (already net of flat "
            f"transaction costs {TRANSACTION_COSTS}); None when net return <= 0 or "
            "turnover == 0. Not market evidence."
        ).replace("{CAPACITY_REF_AUM:g}", f"{CAPACITY_REF_AUM:g}"),
        "verdict_rule": _verdict_rule(),
        "null_field_reasons": {
            "oos_sharpe": "null when the OOS slice has fewer than two finite returns",
            "oos_turnover": "null when the OOS weight frame is empty",
            "oos_wealth": "null when the OOS path is empty",
            "portfolio_beta": "null when no OOS row has nonzero gross exposure",
            "capacity_break_even_aum": "null when net mean OOS daily return <= 0 or turnover == 0",
        },
    }


def run_capacity_sweep(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the sweep, write JSON + markdown artifacts, return the dict."""
    payload = build_capacity_sweep(fixture_path)
    write_artifacts(payload)
    return payload


def _format(value) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return ", ".join(_format(v) for v in value)
    if isinstance(value, (int, float, np.integer, np.floating)):
        return f"{float(value):.{DECIMALS}f}"
    return str(value)


def render_markdown(payload: dict) -> str:
    """Render the capacity sweep cells and aggregate from the JSON object."""
    lines = [
        "# P26 WP2 Capacity & Turnover of Rank Book",
        "",
        f"**Verdict:** {payload['aggregate']['verdict']}",
        "",
        f"**Seed:** {payload['seed']} | **Folds:** {payload['n_folds']} | "
        f"Train: {payload['train_window']} | Test: {payload['test_window']} | "
        f"Beta Window: {payload['beta_window']} | Min Obs: {payload['min_observations']} | "
        f"Quantiles: {payload['long_quantile']}/{payload['short_quantile']} | "
        f"Rank Min Leg Beta: {payload['rank_min_leg_beta']} | "
        f"Rank Max Gross (default): {payload['rank_max_gross']} | "
        f"Costs: {payload['transaction_costs']} | "
        f"Gross Caps: {list(payload['aggregate']['gross_caps'])} | "
        f"Rebalance Freqs: {list(payload['aggregate']['rebalance_freqs'])}",
        "",
        f"**Fixture SHA256:** {payload['fixture_sha256']}",
        "",
        "## Aggregate",
        "",
        "| key | value |",
        "|---|---|",
    ]
    agg = payload["aggregate"]
    for field in AGGREGATE_FIELDS:
        if field in ("cells",):
            continue
        value = agg.get(field)
        lines.append("| " + field + " | " + _format(value) + " |")
    lines.append("")
    lines.append("| cells_evaluated | " + str(len(payload["cells"])) + " |")
    lines.append("| last_cell_index | " + str(payload["cells"][-1]["cell"]) + " |")
    lines.append("")
    lines.append("## Per-Cell Results (rank vs equal)")
    lines.append("")
    lines.append(
        "| Cell | Gross Cap | Rebalance | Weighting | Mean OOS Sharpe | "
        "Mean OOS Turnover | Mean OOS Wealth | Mean Portfolio Beta | Break-Even AUM |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for cell in payload["cells"]:
        for weighting in WEIGHTINGS:
            r = cell["results"][weighting]
            lines.append(
                "| {cell} | {gross} | {freq} | {w} | {sharpe} | {turnover} | "
                "{wealth} | {pb} | {be} |".format(
                    cell=cell["cell"],
                    gross=_format(cell["gross_cap"]),
                    freq=cell["rebalance_freq"],
                    w=weighting,
                    sharpe=_format(r["mean_oos_sharpe"]),
                    turnover=_format(r["mean_oos_turnover"]),
                    wealth=_format(r["mean_oos_wealth"]),
                    pb=_format(r["mean_portfolio_beta"]),
                    be=_format(cell["capacity_break_even"][weighting]),
                )
            )
        d = cell["delta"]
        lines.append(
            "| {cell} | {gross} | {freq} | DELTA | {dsharpe} | {dturnover} | "
            "{dwealth} | - | - |".format(
                cell=cell["cell"],
                gross=_format(cell["gross_cap"]),
                freq=cell["rebalance_freq"],
                dsharpe=_format(d["delta_oos_sharpe"]),
                dturnover=_format(d["delta_oos_turnover"]),
                dwealth=_format(d["delta_oos_wealth"]),
            )
        )
    lines.append("")
    lines.append("## Capacity Break-Even Model")
    lines.append("")
    lines.append("Square-root impact estimate (not market evidence):")
    lines.append("- impact_cost(AUM) = 1e-4 * turnover * sqrt(AUM / 1,000,000)")
    lines.append("- break-even AUM solves impact_cost(AUM) = net mean OOS daily return")
    lines.append("- None when net mean OOS daily return <= 0 or turnover == 0")
    lines.append("")
    lines.append("## Verdict Rule")
    lines.append("")
    lines.append(payload["provenance"]["verdict_rule"])
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str | Path = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "rank_capacity.json"
    markdown_path = directory / "rank_capacity.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    payload = run_capacity_sweep()
    print(
        "wrote "
        f"{OUTPUT_DIR / 'rank_capacity.json'} "
        f"({payload['aggregate']['cells_evaluated']} cells x "
        f"{len(WEIGHTINGS)} weightings x {payload['n_folds']} folds)"
    )
    print(f"wrote {OUTPUT_DIR / 'rank_capacity.md'}")
    print(f"Verdict: {payload['aggregate']['verdict']}")
    print(f"Rank survives capacity: {payload['aggregate']['rank_survives_capacity']}")


if __name__ == "__main__":
    main()
