#!/usr/bin/env python3
"""P38 WP2 — Tail-risk & drawdown characterization (CVaR / expected shortfall).

Deterministic, offline runner that characterizes the LEFT TAIL of the shipped
equal-weight, beta-neutral, dollar-neutral Betting-Against-Beta book on the
P35/P37 wide synthetic fixture (40 assets, 8 seeds). P20-P37 never measured tail
risk anywhere; this closes that gap.

For every seed cell it reports, on the strategy return series:
  * CVaR@95  (mean of the worst 5% of returns) and the 5% VaR,
  * CVaR@99  (mean of the worst 1% of returns) and the 1% VaR,
  * expected shortfall @97.5% (mean of the worst 2.5% of returns),
  * worst-day / best-day return,
  * return skew and excess kurtosis,
  * tail asymmetry (left vs right 5% tails, normalized to [-1, +1]),
  * drawdown-at-confidence (conditional drawdown at risk @95, CDaR95) and
    max drawdown,
and asserts the neutrality invariants at every cell:
  * model beta-neutral:   max_t |sum_i w_{t,i} * beta_{t,i}| <= 1e-3
  * dollar-neutral:       max_t |sum_i w_{t,i}|               <= 1e-9
  * realized |beta|:      |OLS beta vs benchmark|             <= 0.15

Each cell is computed twice: gross (transaction_costs=0.0, the structural tail
signature) and costed (transaction_costs=0.001, the decision-relevant tail).

Publishes research_state/bab_p38/tail_risk_summary.json (+ .md sidecar).
Emits --check-tail-risk-summary for byte-diff verification.
All data is deterministic synthetic; not real market data.
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

from strategies.betting_against_beta.backtest import run_backtest  # noqa: E402
from strategies.betting_against_beta.beta_estimators import (  # noqa: E402
    estimate_rolling_ols_beta,
)
from strategies.betting_against_beta.metrics import (  # noqa: E402
    max_drawdown,
    sharpe_ratio,
    strategy_beta,
)
from strategies.betting_against_beta.portfolio import (  # noqa: E402
    construct_portfolio,
    enforce_beta_neutrality,
)
from strategies.betting_against_beta.signals import generate_bab_signals  # noqa: E402

# --- Constants matching the P35/P36/P37/P38-wide universe recipe ---
SEED_BASE = 20261120
SEED_INCREMENT = 1009
N_SEEDS = 8
IDIO_VOL = 0.003
BETA_MIN = 0.35
BETA_MAX = 1.90
N_ASSETS = 40
FIXTURE_PATH = _REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"

BETA_WINDOW = 90
QUANTILE = 0.3

# Gross (structural) and costed (decision-relevant) transaction-cost levels.
GROSS_TC = 0.0
COSTED_TC = 0.001

ASSET_COLUMNS = [f"A{i:03d}" for i in range(1, N_ASSETS + 1)]

# Neutrality tolerances (per HANDOFF.md P34/P36/P37)
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

# Tail levels.
CVAR_LEVELS = (95.0, 99.0)
ES_LEVEL = 975.0  # expected shortfall @97.5% (Basel FRTB-style level)

SCHEMA_VERSION = "bab_p38.tail_risk/1"
SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p38" / "tail_risk_summary.json"
MARKDOWN_PATH = _REPO_ROOT / "research_state" / "bab_p38" / "tail_risk_summary.md"


# --- Universe / reference (P35 wide-universe recipe) ---


def _load_btc_prices() -> pd.Series:
    df = pd.read_csv(FIXTURE_PATH, index_col="date", parse_dates=True)
    df.index = pd.DatetimeIndex(df.index)
    if "BTC" not in df.columns:
        raise ValueError(f"wide universe fixture missing BTC column: {list(df.columns)}")
    return df["BTC"].astype(float)


def _build_wide_universe_for_seed(seed: int) -> pd.DataFrame:
    """Build synthetic wide universe: asset returns = beta * BTC_return + seeded idio.

    BTC prices are loaded read-only from tests/fixtures/wide_bab_universe.csv.
    Not real market data; not market profitability evidence.
    """
    btc_prices = _load_btc_prices()
    btc_returns = btc_prices.pct_change().iloc[1:]
    btc_return_dates = btc_returns.index

    rng = np.random.default_rng(seed)
    betas = np.linspace(BETA_MIN, BETA_MAX, N_ASSETS)

    n_returns = len(btc_return_dates)
    idio = rng.normal(loc=0.0, scale=IDIO_VOL, size=(N_ASSETS, n_returns))

    asset_returns = np.vstack([
        beta * btc_returns.to_numpy(dtype=float) + idio[i]
        for i, beta in enumerate(betas)
    ])

    returns_df = pd.DataFrame(
        asset_returns.T,
        index=btc_return_dates,
        columns=ASSET_COLUMNS,
    )
    returns_df["BTC"] = btc_returns

    return returns_df


# --- Strategy pipeline (shipped default; mirrors bab_p38_deflated_significance) ---


def _base_weights(
    returns_df: pd.DataFrame, beta_estimates: pd.DataFrame, quantile: float
) -> pd.DataFrame:
    """Equal-weight, beta-neutral, dollar-neutral base portfolio (shipped default)."""
    signals = generate_bab_signals(
        beta_estimates,
        long_quantile=quantile,
        short_quantile=quantile,
    )
    weights = construct_portfolio(
        signals,
        betas=beta_estimates,
        weighting="equal",
        dollar_neutral=True,
    )
    weights = enforce_beta_neutrality(
        weights,
        beta_estimates,
        target_beta=0.0,
        tolerance=1e-4,
        max_drift=1e-4,
        correction=True,
    )
    return weights


def _compute_strat_returns(
    weights: pd.DataFrame, returns_df: pd.DataFrame, transaction_costs: float
) -> pd.Series:
    backtest = run_backtest(returns_df, weights, transaction_costs=transaction_costs)
    if "returns" in backtest.columns:
        return backtest["returns"]
    if "cumulative" in backtest.columns:
        cum = backtest["cumulative"]
        return cum.pct_change().iloc[1:]
    return pd.Series(dtype=float)


# --- Neutrality invariants (mirrors bab_p34_multiseed_robustness) ---


def _model_beta_series(weights: pd.DataFrame, betas: pd.DataFrame) -> pd.Series:
    """Per-period gross-exposure-weighted model portfolio beta: sum_i w_i*beta_i / sum|w|."""
    common_idx = weights.index.intersection(betas.index)
    common_cols = weights.columns.intersection(betas.columns)
    if len(common_idx) == 0 or len(common_cols) == 0:
        return pd.Series(index=weights.index, dtype=float)

    w = weights.loc[common_idx, common_cols].astype(float).replace(
        [np.inf, -np.inf], np.nan
    ).fillna(0.0)
    b = betas.loc[common_idx, common_cols].astype(float).replace([np.inf, -np.inf], np.nan)

    wv = w.to_numpy(dtype=float)
    bv = b.to_numpy(dtype=float)
    finite = np.isfinite(bv)
    wv = np.where(finite, wv, 0.0)
    bv = np.where(finite, bv, 0.0)

    gross = np.abs(wv).sum(axis=1)
    pb = np.full(len(common_idx), np.nan)
    mask = gross > 1e-18
    if mask.any():
        pb[mask] = (wv[mask] * bv[mask]).sum(axis=1) / gross[mask]

    return pd.Series(pb, index=common_idx).reindex(weights.index)


# --- Tail-risk statistics ---


def _drawdown_series(returns: np.ndarray) -> np.ndarray:
    """Per-period drawdown (non-positive) from a returns array."""
    cum = np.cumprod(1.0 + returns)
    running_max = np.maximum.accumulate(cum)
    with np.errstate(divide="ignore", invalid="ignore"):
        dd = (cum - running_max) / running_max
    return np.where(np.isfinite(dd), dd, 0.0)


def _tail_below(returns: np.ndarray, pct: float) -> tuple[float, float, int]:
    """Return (value_at_risk, conditional_tail_mean, n_tail_obs) for a lower tail pct.

    ``value_at_risk`` is the ``pct``-th percentile of returns (a loss threshold,
    typically negative). ``conditional_tail_mean`` is the mean of returns at or
    below that threshold (CVaR / expected shortfall). ``n_tail_obs`` is the count
    of observations in the tail.
    """
    var = float(np.percentile(returns, 100.0 - pct))
    tail = returns[returns <= var]
    if tail.size == 0:
        return var, var, 0
    return var, float(tail.mean()), int(tail.size)


def _tail_metrics(returns: np.ndarray) -> dict:
    """Compute the full tail-risk / drawdown metric set for one return series."""
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    n = int(r.size)

    var_95, cvar_95, n95 = _tail_below(r, 95.0)
    var_99, cvar_99, n99 = _tail_below(r, 99.0)
    _var_975, es_975, _nes = _tail_below(r, 97.5)

    worst_day = float(r.min())
    best_day = float(r.max())

    # Standardized moments (population convention, mirroring WP1's _sample_moments).
    mean = float(r.mean())
    std = float(r.std(ddof=0))
    if std == 0.0 or not np.isfinite(std):
        skew = 0.0
        excess_kurtosis = 0.0
    else:
        centred = r - mean
        skew = float(np.mean(centred ** 3) / std ** 3)
        raw_kurt = float(np.mean(centred ** 4) / std ** 4)
        excess_kurtosis = raw_kurt - 3.0

    # Tail asymmetry: normalized (left-tail severity - right-tail magnitude).
    left_tail_mean = cvar_95  # mean of the worst 5%
    right_tail = r[r >= float(np.percentile(r, 95.0))]
    right_tail_mean = float(right_tail.mean()) if right_tail.size else best_day
    denom = abs(left_tail_mean) + abs(right_tail_mean)
    tail_asymmetry = (
        float((abs(left_tail_mean) - abs(right_tail_mean)) / denom) if denom > 0 else None
    )

    dd = _drawdown_series(r)
    var_dd, c_dar_95, _ndd = _tail_below(dd, 95.0)
    max_dd = float(dd.min())
    # Guard: metrics.max_drawdown is the canonical reported max drawdown; keep the
    # drawdown-series value as the CDaR basis and report both so they reconcile.
    canonical_max_dd = float(max_drawdown(r)) if n >= 1 else max_dd

    return {
        "n_observations": n,
        "mean_return": mean,
        "std_return": std,
        "var_95": var_95,
        "cvar_95": cvar_95,
        "n_tail_obs_95": n95,
        "var_99": var_99,
        "cvar_99": cvar_99,
        "n_tail_obs_99": n99,
        "expected_shortfall_975": es_975,
        "worst_day_return": worst_day,
        "best_day_return": best_day,
        "skew": skew,
        "excess_kurtosis": excess_kurtosis,
        "left_tail_mean": left_tail_mean,
        "right_tail_mean": right_tail_mean,
        "tail_asymmetry": tail_asymmetry,
        "drawdown_var_95": var_dd,
        "conditional_drawdown_95": c_dar_95,
        "max_drawdown": max_dd,
        "max_drawdown_canonical": canonical_max_dd,
        "sharpe": float(sharpe_ratio(r)) if r.size >= 2 else None,
    }


# --- Per-seed cell runner ---


def _run_seed_cell(
    returns_df: pd.DataFrame, seed: int, seed_idx: int, transaction_costs: float
) -> dict:
    """Run one (seed, transaction-cost) cell and return its tail + neutrality block."""
    betas = estimate_rolling_ols_beta(
        returns_df, "BTC", window=BETA_WINDOW, min_obs=min(60, BETA_WINDOW)
    )

    valid_betas = betas.dropna(how="all", subset=ASSET_COLUMNS)
    if len(valid_betas) == 0:
        return {
            "cell_key": f"seed_{seed_idx}",
            "seed_index": seed_idx,
            "seed": seed,
            "transaction_costs": float(transaction_costs),
            "status": "error",
            "error": "no valid beta estimates",
        }

    valid_returns = returns_df.loc[valid_betas.index]
    valid_betas_aligned = valid_betas[[*ASSET_COLUMNS, "BTC"]]

    weights = _base_weights(valid_returns, valid_betas_aligned, QUANTILE)
    strat_returns = _compute_strat_returns(weights, valid_returns, transaction_costs)
    bench_returns = valid_returns["BTC"]

    tail = _tail_metrics(strat_returns.to_numpy(dtype=float))

    model_beta_series = _model_beta_series(weights, valid_betas_aligned)
    max_model_beta = (
        float(model_beta_series.abs().max()) if len(model_beta_series) > 0 else None
    )
    dollar_series = weights.sum(axis=1)
    max_dollar = float(dollar_series.abs().max()) if len(dollar_series) > 0 else None
    realized_beta = strategy_beta(strat_returns, bench_returns)

    model_beta_ok = (
        max_model_beta is not None and max_model_beta <= MODEL_BETA_NEUTRAL_TOL
    )
    dollar_ok = max_dollar is not None and max_dollar <= DOLLAR_NEUTRAL_TOL
    realized_ok = (
        realized_beta is not None
        and np.isfinite(realized_beta)
        and abs(realized_beta) <= REALIZED_BETA_TOL
    )

    status = (
        "ok"
        if (model_beta_ok and dollar_ok and realized_ok)
        else "neutrality_violation"
    )
    return {
        "cell_key": f"seed_{seed_idx}",
        "seed_index": seed_idx,
        "seed": seed,
        "transaction_costs": float(transaction_costs),
        "n_periods": int(tail["n_observations"]),
        "n_valid_beta_rows": len(valid_betas),
        "tail": tail,
        "neutrality": {
            "max_model_beta": max_model_beta,
            "max_dollar_neutral": max_dollar,
            "realized_beta": round(float(realized_beta), 12)
            if realized_beta is not None and np.isfinite(realized_beta)
            else None,
            "model_beta_neutral": {
                "passed": bool(model_beta_ok),
                "tolerance": MODEL_BETA_NEUTRAL_TOL,
            },
            "dollar_neutral": {
                "passed": bool(dollar_ok),
                "tolerance": DOLLAR_NEUTRAL_TOL,
            },
            "realized_beta_check": {
                "passed": bool(realized_ok),
                "tolerance": REALIZED_BETA_TOL,
            },
        },
        "status": status,
    }


def _run_config(transaction_costs: float) -> dict:
    cells = []
    for seed_idx in range(N_SEEDS):
        seed = SEED_BASE + SEED_INCREMENT * seed_idx
        returns_df = _build_wide_universe_for_seed(seed)
        try:
            cells.append(_run_seed_cell(returns_df, seed, seed_idx, transaction_costs))
        except Exception as exc:  # pragma: no cover - defensive
            cells.append({
                "cell_key": f"seed_{seed_idx}",
                "seed_index": seed_idx,
                "seed": seed,
                "transaction_costs": float(transaction_costs),
                "status": "error",
                "error": str(exc),
            })
    return {"transaction_costs": float(transaction_costs), "cells": cells}


# --- Aggregation ---


def _agg(values: list[float]) -> dict:
    """Mean / min / max of a list of finite floats (skips None / non-finite)."""
    clean = [float(v) for v in values if v is not None and np.isfinite(v)]
    if not clean:
        return {"mean": None, "min": None, "max": None, "n": 0}
    return {
        "mean": float(np.mean(clean)),
        "min": float(np.min(clean)),
        "max": float(np.max(clean)),
        "n": len(clean),
    }


_TAIL_KEYS = (
    "cvar_95",
    "cvar_99",
    "expected_shortfall_975",
    "worst_day_return",
    "skew",
    "excess_kurtosis",
    "tail_asymmetry",
    "conditional_drawdown_95",
    "max_drawdown",
)


def _aggregate(cells: list[dict]) -> dict:
    ok = [c for c in cells if c.get("status") == "ok" and "tail" in c]
    agg: dict = {
        "n_cells": len(cells),
        "n_ok_cells": len(ok),
        "n_error_cells": sum(1 for c in cells if c.get("status") == "error"),
        "n_neutrality_violations": sum(
            1 for c in cells if c.get("status") == "neutrality_violation"
        ),
        "all_neutrality_ok": all(
            c.get("status") == "ok" for c in cells
        ),
        "tail_metric_aggregates": {
            key: _agg([c["tail"].get(key) for c in ok]) for key in _TAIL_KEYS
        },
    }
    return agg


# --- Summary artifact ---


def _build_summary_artifact(gross: dict, costed: dict) -> dict:
    base_returns = _build_wide_universe_for_seed(SEED_BASE)
    returns_sha256 = hashlib.sha256(
        base_returns.to_csv(date_format="%Y-%m-%d").encode("utf-8")
    ).hexdigest()

    btc_prices = _load_btc_prices()
    btc_sha256 = hashlib.sha256(btc_prices.to_numpy(dtype=float).tobytes()).hexdigest()

    gross_agg = _aggregate(gross["cells"])
    costed_agg = _aggregate(costed["cells"])

    summary = {
        "schema": SCHEMA_VERSION,
        "provenance": {
            "generator": "scripts/bab_p38_tail_risk.py",
            "campaign": "P38 Deflated Significance & Tail-Risk Closure",
            "wp": "WP2 - Tail-risk & drawdown characterization (CVaR / expected shortfall)",
            "synthetic": True,
            "note": (
                "Deterministic synthetic wide universe (P35 wide-universe recipe). "
                "BTC prices from tests/fixtures/wide_bab_universe.csv. "
                "Asset returns = beta * BTC_return + idio, idio ~ N(0, 0.003), "
                "betas linspace(0.35, 1.9, 40). Not real market data; not market "
                "profitability evidence. Tail-risk metrics are gross (transaction_costs=0.0) "
                "and costed (0.001); they characterize the structural short-high-beta / "
                "short-vol crash signature, not market alpha."
            ),
            "fixture_path": str(FIXTURE_PATH),
            "returns_sha256": returns_sha256,
            "btc_source_sha256": btc_sha256,
            "seeds": {
                "base_seed": SEED_BASE,
                "increment": SEED_INCREMENT,
                "n_seeds": N_SEEDS,
                "seed_list": [SEED_BASE + SEED_INCREMENT * i for i in range(N_SEEDS)],
            },
            "config_grid": {
                "beta_window": BETA_WINDOW,
                "quantile": QUANTILE,
                "gross_transaction_costs": GROSS_TC,
                "costed_transaction_costs": COSTED_TC,
                "weighting": "equal",
                "beta_neutral": True,
                "dollar_neutral": True,
            },
            "neutrality_tolerances": {
                "model_beta_neutral": MODEL_BETA_NEUTRAL_TOL,
                "dollar_neutral": DOLLAR_NEUTRAL_TOL,
                "realized_beta": REALIZED_BETA_TOL,
            },
            "tail_risk_definitions": {
                "cvar_95": "mean of the worst 5% of returns (expected shortfall @95%)",
                "cvar_99": "mean of the worst 1% of returns (expected shortfall @99%)",
                "var_95": "5th percentile of returns (value at risk @95%)",
                "var_99": "1st percentile of returns (value at risk @99%)",
                "expected_shortfall_975": (
                    "mean of the worst 2.5% of returns (expected shortfall @97.5%)"
                ),
                "worst_day_return": "minimum single-period return",
                "best_day_return": "maximum single-period return",
                "skew": "population skewness of returns",
                "excess_kurtosis": "population excess kurtosis (raw kurtosis - 3)",
                "tail_asymmetry": (
                    "(|left 5% tail mean| - |right 5% tail mean|) / "
                    "(|left 5% tail mean| + |right 5% tail mean|); in [-1, +1], "
                    "positive = heavier left tail"
                ),
                "conditional_drawdown_95": (
                    "mean of the worst 5% of the per-period drawdown series "
                    "(conditional drawdown at risk @95%)"
                ),
                "max_drawdown": "minimum of the per-period drawdown series",
                "sharpe": "annualized Sharpe ratio of the strategy return series",
            },
        },
        "results": {
            "gross": {
                "transaction_costs": GROSS_TC,
                "cells": gross["cells"],
                "aggregate": gross_agg,
            },
            "costed": {
                "transaction_costs": COSTED_TC,
                "cells": costed["cells"],
                "aggregate": costed_agg,
            },
        },
    }
    summary["tail_risk_status"] = (
        "ALL_NEUTRALITY_OK"
        if (gross_agg["all_neutrality_ok"] and costed_agg["all_neutrality_ok"])
        else "NEUTRALITY_VIOLATION"
    )
    return summary


def _round_floats(obj, sig: int = 12):
    """Recursively round floats to ``sig`` significant digits (byte-reproducibility).

    Cross-version BLAS / numpy differences perturb trailing ULPs; the neutrality
    tolerances and tail magnitudes are many orders above 1e-12, so this cannot
    change any decision -- it only makes the committed artifact reproducible.
    Signed zero is normalized to ``0.0`` so ``json.dumps`` bytes are stable.
    """
    if isinstance(obj, float):
        if obj == 0.0 or not np.isfinite(obj):
            return 0.0 if obj == 0.0 else obj
        return float(f"{obj:.{sig}g}")
    if isinstance(obj, dict):
        return {k: _round_floats(v, sig) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_floats(v, sig) for v in obj]
    return obj


def build_summary() -> dict:
    """Build the deterministic, rounded summary artifact (read-only; no disk writes)."""
    gross = _run_config(GROSS_TC)
    costed = _run_config(COSTED_TC)
    return _round_floats(_build_summary_artifact(gross, costed))


def write_artifacts(payload: dict) -> tuple[Path, Path]:
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MARKDOWN_PATH.write_text(render_markdown(payload), encoding="utf-8")
    return SUMMARY_PATH, MARKDOWN_PATH


def check_summary(path: Path = SUMMARY_PATH) -> bool:
    if not path.exists():
        print(f"Summary artifact not found: {path}")
        return False

    fresh = build_summary()
    expected_bytes = path.read_bytes()
    actual_bytes = json.dumps(fresh, indent=2, sort_keys=True).encode("utf-8") + b"\n"

    if expected_bytes == actual_bytes:
        print("Summary artifact check: PASS (byte-identical)")
        return True

    print("Summary artifact check: FAIL (byte mismatch)")
    for i, (e, a) in enumerate(zip(expected_bytes, actual_bytes)):
        if e != a:
            print(f"  First difference at byte {i}: expected {e!r}, got {a!r}")
            break
    if len(expected_bytes) != len(actual_bytes):
        print(f"  Length mismatch: expected {len(expected_bytes)}, got {len(actual_bytes)}")
    return False


# --- Markdown sidecar ---


def _fmt(v, decimals: int = 6) -> str:
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "True" if v else "False"
    return f"{float(v):.{decimals}f}"


def render_markdown(payload: dict) -> str:
    prov = payload["provenance"]
    results = payload["results"]
    lines = [
        "# BAB P38 WP2 - Tail-Risk & Drawdown Characterization (CVaR / Expected Shortfall)",
        "",
        f"Schema `{payload['schema']}`. Controlled synthetic stimulus: not real market "
        "data and not market profitability evidence.",
        "",
        f"**Tail-risk status:** **{payload['tail_risk_status']}**",
        "",
        "## Setup",
        "",
        f"- Seeds: {prov['seeds']['n_seeds']} (base={prov['seeds']['base_seed']}, "
        f"increment={prov['seeds']['increment']})",
        f"- beta_window: {prov['config_grid']['beta_window']}d, quantile: "
        f"{_fmt(prov['config_grid']['quantile'])}",
        f"- Gross transaction_costs: {_fmt(prov['config_grid']['gross_transaction_costs'])}, "
        f"costed transaction_costs: {_fmt(prov['config_grid']['costed_transaction_costs'])}",
        f"- weighting: {prov['config_grid']['weighting']}, beta_neutral: "
        f"{prov['config_grid']['beta_neutral']}, dollar_neutral: "
        f"{prov['config_grid']['dollar_neutral']}",
        "",
        "## Definitions",
        "",
    ]
    for key, definition in prov["tail_risk_definitions"].items():
        lines.append(f"- `{key}`: {definition}")
    lines.append("")

    for label, title in (("gross", "Gross (structural)"), ("costed", "Costed (10 bps)")):
        block = results[label]
        agg = block["aggregate"]
        lines += [
            f"## {title}",
            "",
            f"transaction_costs = {_fmt(block['transaction_costs'])}; "
            f"cells: {agg['n_cells']} total, {agg['n_ok_cells']} OK, "
            f"{agg['n_neutrality_violations']} neutrality violations, "
            f"{agg['n_error_cells']} errors.",
            "",
            "| Tail metric | mean | min (worst) | max |",
            "|---|---|---|---|",
        ]
        for key in _TAIL_KEYS:
            a = agg["tail_metric_aggregates"][key]
            lines.append(
                f"| {key} | {_fmt(a['mean'])} | {_fmt(a['min'])} | {_fmt(a['max'])} |"
            )
        lines.append("")

    lines += [
        "---",
        "",
        "## Interpretation",
        "",
        "- CVaR@95 / CVaR@99 / expected shortfall are (negative) average losses in the "
        "worst 5% / 1% / 2.5% of periods. More negative = fatter left tail.",
        "- tail_asymmetry in [-1, +1]: positive means the left tail dominates the right "
        "(the short-high-beta / short-vol crash signature); near zero means symmetric.",
        "- excess_kurtosis > 0 means fat tails relative to a Gaussian; skew < 0 means a "
        "long left tail.",
        "- conditional_drawdown_95 is the average of the worst 5% of per-period drawdowns; "
        "max_drawdown is the single worst peak-to-trough.",
        "- Every seed cell asserts model beta <= 1e-3, dollar <= 1e-9, realized |beta| "
        "<= 0.15; tail_risk_status is ALL_NEUTRALITY_OK only if all cells pass.",
        "",
        "Synthetic-provenance caveat: results are on the committed synthetic wide universe "
        "(BTC prices + seeded idiosyncratic noise), not real market data. Never market alpha.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="P38 WP2 tail-risk & drawdown characterization"
    )
    parser.add_argument(
        "--check-tail-risk-summary",
        action="store_true",
        help="Verify existing summary artifact is byte-identical to fresh recomputation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=SUMMARY_PATH,
        help=f"Output path for summary artifact (default: {SUMMARY_PATH})",
    )
    args = parser.parse_args()

    if args.check_tail_risk_summary:
        ok = check_summary(args.output)
        return 0 if ok else 1

    print("Running P38 WP2 tail-risk & drawdown characterization...")
    print(f"  Seeds: {N_SEEDS} (base={SEED_BASE}, inc={SEED_INCREMENT})")
    print(f"  beta_window={BETA_WINDOW}, quantile={QUANTILE}")
    print(f"  transaction_costs: gross={GROSS_TC}, costed={COSTED_TC}")

    started = time.perf_counter()
    payload = build_summary()
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MARKDOWN_PATH.write_text(render_markdown(payload), encoding="utf-8")
    elapsed = time.perf_counter() - started

    gross_agg = payload["results"]["gross"]["aggregate"]
    costed_agg = payload["results"]["costed"]["aggregate"]
    print(f"Done in {elapsed:.2f}s")
    print(f"  Gross:  ok={gross_agg['n_ok_cells']}/{gross_agg['n_cells']} "
          f"neutrality_violations={gross_agg['n_neutrality_violations']} "
          f"errors={gross_agg['n_error_cells']}")
    print(f"  Costed: ok={costed_agg['n_ok_cells']}/{costed_agg['n_cells']} "
          f"neutrality_violations={costed_agg['n_neutrality_violations']} "
          f"errors={costed_agg['n_error_cells']}")
    cvar95 = gross_agg["tail_metric_aggregates"]["cvar_95"]["mean"]
    print(f"  Gross mean CVaR@95: {cvar95}")
    print(f"  Tail-risk status: {payload['tail_risk_status']}")
    print(f"  Summary written to: {SUMMARY_PATH}")
    print(f"  Markdown written to: {MARKDOWN_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
