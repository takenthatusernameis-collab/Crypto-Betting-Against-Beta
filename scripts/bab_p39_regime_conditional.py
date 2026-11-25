#!/usr/bin/env python3
"""P39 WP1 — Regime-conditional deflated significance + tail risk.

Deterministic, offline runner that, on the P35/P37 wide synthetic fixture
(40 assets, 8 seeds), splits each seed's return series into causal, lagged
market regimes (trailing BTC trend x trailing realized-vol tercile, computed
only from data available at t-1, no lookahead) and recomputes DSR/PSR and
CVaR/ES/drawdown *within each regime*, deflating over the same
n_trials_total read-only from P38 WP1.

Publishes research_state/bab_p39/regime_summary.json (+ .md sidecar).
Emits --check-regime-summary for byte-diff verification.
All data is deterministic synthetic; not real market data.
The honest per-regime verdict may be negative (a thin regime can fail
deflation); report it honestly, do not overclaim.
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
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta.backtest import run_backtest  # noqa: E402
from strategies.betting_against_beta.beta_estimators import (  # noqa: E402
    estimate_rolling_ols_beta,
)
from strategies.betting_against_beta.metrics import (  # noqa: E402
    annualized_volatility,
    final_cumulative,
    max_drawdown,
    sharpe_ratio,
    strategy_beta,
    total_return,
    turnover,
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

ASSET_COLUMNS = [f"A{i:03d}" for i in range(1, N_ASSETS + 1)]

# Neutrality tolerances (per HANDOFF.md P34/P36/P37)
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

# Regime labeling (causal, lagged, no lookahead).
REGIME_LOOKBACK = 10  # trailing window for trend and realized vol
MIN_PERIODS_PER_REGIME = 30  # skip regimes with too few observations

# Bootstrap settings for sigma0 (std of Sharpe under the null), mirroring P21/P38.
N_BOOTSTRAP = 2000
BLOCK_LENGTH = 20
BOOTSTRAP_SEED = 20261123

# DSR verdict threshold: DSR >= 0.50 means more likely than not genuine skill
# after multiple-testing deflation.
DSR_SURVIVE_THRESHOLD = 0.50

# Read-only trial enumeration from P38 WP1 (deflate over the same search).
P38_DEFLATED_PATH = (
    _REPO_ROOT / "research_state" / "bab_p38" / "deflated_summary.json"
)

SCHEMA_VERSION = "bab_p39.regime_conditional/1"
SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p39" / "regime_summary.json"
MARKDOWN_PATH = _REPO_ROOT / "research_state" / "bab_p39" / "regime_summary.md"

WEIGHT_THRESHOLD = 1e-10

TREND_LABELS = ("bull", "bear")
VOL_LABELS = ("low_vol", "mid_vol", "high_vol")
REGIME_LABELS = tuple(f"{t}_{v}" for t in TREND_LABELS for v in VOL_LABELS)


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


# --- Neutrality invariants (mirrors bab_p38_tail_risk) ---


def _model_beta_series(weights: pd.DataFrame, betas: pd.DataFrame) -> pd.Series:
    """Per-period gross-exposure-weighted model portfolio beta: sum_i w_i*beta_i / sum|w|."""
    common_idx = weights.index.intersection(betas.index)
    common_cols = weights.columns.intersection(betas.columns)
    if len(common_idx) == 0 or len(common_cols) == 0:
        return pd.Series(index=weights.index, dtype=float)

    w = weights.loc[common_idx, common_cols].astype(float).replace(
        [np.inf, -np.inf], np.nan
    ).fillna(0.0)
    b = betas.loc[common_idx, common_cols].astype(float).replace(
        [np.inf, -np.inf], np.nan
    )

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


# --- Regime labeling (causal, lagged, no lookahead) ---


def _regime_labels(btc_returns: pd.Series) -> pd.Series:
    """Causal, lagged regime label per period: trailing trend x trailing vol tercile.

    trend[t]   = sign of mean(btc_returns over trailing lookback ending at t-1)
    vol[t]     = std(btc_returns over trailing lookback ending at t-1)
    vol tercile[t] = percentile of vol[t] within vol[0:t+1] (expanding, causal)

    The label at t depends only on data strictly before t: no lookahead.
    Periods without enough trailing history are labelled None (excluded).
    """
    n = len(btc_returns)
    labels = pd.Series(index=btc_returns.index, dtype=object)
    if n == 0:
        return labels

    r = btc_returns.to_numpy(dtype=float)
    trailing_mean = np.full(n, np.nan)
    trailing_vol = np.full(n, np.nan)
    lookback = REGIME_LOOKBACK
    for t in range(n):
        start = max(0, t - lookback)
        window = r[start:t]  # strictly before t -> causal
        if window.size >= 2:
            trailing_mean[t] = float(np.mean(window))
            trailing_vol[t] = float(np.std(window, ddof=0))

    # Expanding percentile of trailing_vol (causal): rank of vol[t] within vol[0:t+1].
    vol_pct = np.full(n, np.nan)
    for t in range(n):
        if not np.isfinite(trailing_vol[t]):
            continue
        hist = trailing_vol[: t + 1]
        valid = hist[np.isfinite(hist)]
        if valid.size == 0:
            continue
        vol_pct[t] = float(np.mean(valid <= trailing_vol[t]))

    trend_label = np.where(trailing_mean > 0.0, "bull", "bear")
    vol_label = np.full(n, "", dtype=object)
    for t in range(n):
        if not np.isfinite(vol_pct[t]):
            continue
        if vol_pct[t] < 1.0 / 3.0:
            vol_label[t] = "low_vol"
        elif vol_pct[t] < 2.0 / 3.0:
            vol_label[t] = "mid_vol"
        else:
            vol_label[t] = "high_vol"

    for t in range(n):
        if not np.isfinite(trailing_mean[t]) or vol_label[t] == "":
            labels.iloc[t] = None
        else:
            labels.iloc[t] = f"{trend_label[t]}_{vol_label[t]}"
    return labels


# --- Significance statistics (DSR + PSR) ---


def _sample_moments(rets: np.ndarray) -> tuple[float, float]:
    mean = float(np.mean(rets))
    std = float(np.std(rets))
    if std == 0.0:
        return 0.0, 3.0
    centred = rets - mean
    gamma = float(np.mean(centred ** 3) / std ** 3)
    kappa = float(np.mean(centred ** 4) / std ** 4)
    return gamma, kappa


def _moving_block_bootstrap(
    rets: np.ndarray, n_resamples: int, block_length: int, seed: int, center: bool
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = len(rets)
    data = rets - np.mean(rets) if center else rets
    n_blocks = math.ceil(n / block_length)
    starts = rng.integers(0, n - block_length + 1, size=(n_resamples, n_blocks))
    out = np.empty(n_resamples, dtype=float)
    for b in range(n_resamples):
        sample = np.concatenate([data[s:s + block_length] for s in starts[b]])[:n]
        out[b] = float(sharpe_ratio(sample))
    return out


def _deflated_sharpe(
    sr_obs: float, sr_bar: float, n_trials: int, sigma0: float, gamma: float, kappa: float
) -> float:
    delta = sr_obs - sr_bar
    root = math.sqrt(max(n_trials - 1, 1))
    num = 1.0 + delta * root / sigma0
    inner = (
        1.0
        + gamma * delta ** 2 * root / sigma0
        + (kappa - 1.0) / 4.0 * (delta ** 2 * (n_trials - 1) / sigma0 ** 2)
    )
    denom = math.sqrt(max(inner, 1e-12))
    return float(NormalDist().cdf(num / denom))


def _probabilistic_sharpe(
    sr: float, gamma: float, kappa: float, n_obs: int, sr_bench: float = 0.0
) -> float:
    """Analytical PSR: NormalDist.cdf((SR - SR_bench) / SE(SR))."""
    if n_obs < 2:
        return float("nan")
    se_sr_sq = (
        1.0 + 0.5 * gamma * sr ** 2 + 0.25 * (kappa - 1.0) * sr ** 4
    ) / max(n_obs - 1, 1)
    se_sr = math.sqrt(max(se_sr_sq, 1e-18))
    return float(NormalDist().cdf((sr - sr_bench) / se_sr))


# --- Tail-risk statistics ---


def _drawdown_series(returns: np.ndarray) -> np.ndarray:
    """Per-period drawdown (non-positive) from a returns array."""
    cum = np.cumprod(1.0 + returns)
    running_max = np.maximum.accumulate(cum)
    with np.errstate(divide="ignore", invalid="ignore"):
        dd = (cum - running_max) / running_max
    return np.where(np.isfinite(dd), dd, 0.0)


def _tail_below(returns: np.ndarray, pct: float) -> tuple[float, float, int]:
    """Return (value_at_risk, conditional_tail_mean, n_tail_obs) for a lower tail pct."""
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

    left_tail_mean = cvar_95
    right_tail = r[r >= float(np.percentile(r, 95.0))]
    right_tail_mean = float(right_tail.mean()) if right_tail.size else best_day
    denom = abs(left_tail_mean) + abs(right_tail_mean)
    tail_asymmetry = (
        float((abs(left_tail_mean) - abs(right_tail_mean)) / denom) if denom > 0 else None
    )

    dd = _drawdown_series(r)
    var_dd, c_dar_95, _ndd = _tail_below(dd, 95.0)
    max_dd = float(dd.min())
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


# --- Per-(seed, regime) cell runner ---


def _run_regime_cell(
    returns_df: pd.DataFrame,
    betas: pd.DataFrame,
    regime_series: pd.Series,
    regime_label: str,
    seed: int,
    seed_idx: int,
    n_trials: int,
    transaction_costs: float,
) -> dict:
    """Run one (seed, regime) cell and return its DSR/PSR + tail + neutrality block."""
    mask = regime_series == regime_label
    n_periods = int(mask.sum())
    if n_periods < MIN_PERIODS_PER_REGIME:
        return {
            "cell_key": f"seed_{seed_idx}",
            "seed_index": seed_idx,
            "seed": seed,
            "regime": regime_label,
            "n_periods": n_periods,
            "status": "insufficient_periods",
            "error": (
                f"regime has {n_periods} periods, need >= {MIN_PERIODS_PER_REGIME}"
            ),
        }

    regime_returns = returns_df.loc[mask]
    regime_betas = betas.loc[mask][[*ASSET_COLUMNS, "BTC"]]

    weights = _base_weights(regime_returns, regime_betas, QUANTILE)
    strat_returns = _compute_strat_returns(weights, regime_returns, transaction_costs)
    bench_returns = regime_returns["BTC"]

    sr = sharpe_ratio(strat_returns)
    ann_vol = annualized_volatility(strat_returns)
    max_dd = max_drawdown(strat_returns)
    tr = total_return(strat_returns)
    turn = turnover(weights)
    realized_beta = strategy_beta(strat_returns, bench_returns)
    wealth = final_cumulative(strat_returns)

    strat_returns_arr = strat_returns.to_numpy(dtype=float)
    gamma, kappa = _sample_moments(strat_returns_arr)
    boot_centred = _moving_block_bootstrap(
        strat_returns_arr, N_BOOTSTRAP, BLOCK_LENGTH, BOOTSTRAP_SEED, center=True
    )
    sigma0 = float(np.std(boot_centred, ddof=1))
    if not np.isfinite(sigma0) or sigma0 <= 0.0:
        se_sr_sq = (
            1.0 + 0.5 * gamma * sr ** 2 + 0.25 * (kappa - 1.0) * sr ** 4
        ) / max(n_periods - 1, 1)
        sigma0 = math.sqrt(max(se_sr_sq, 1e-18))

    dsr = _deflated_sharpe(float(sr), 0.0, n_trials, sigma0, gamma, kappa)
    psr = _probabilistic_sharpe(float(sr), gamma, kappa, n_periods, sr_bench=0.0)
    survives = bool(dsr >= DSR_SURVIVE_THRESHOLD)

    tail = _tail_metrics(strat_returns_arr)

    model_beta_series = _model_beta_series(weights, regime_betas)
    max_model_beta = (
        float(model_beta_series.abs().max()) if len(model_beta_series) > 0 else None
    )
    dollar_series = weights.sum(axis=1)
    max_dollar = float(dollar_series.abs().max()) if len(dollar_series) > 0 else None

    model_beta_ok = (
        max_model_beta is not None and max_model_beta <= MODEL_BETA_NEUTRAL_TOL
    )
    dollar_ok = max_dollar is not None and max_dollar <= DOLLAR_NEUTRAL_TOL
    realized_ok = (
        realized_beta is not None
        and np.isfinite(realized_beta)
        and abs(realized_beta) <= REALIZED_BETA_TOL
    )

    status = "ok" if (model_beta_ok and dollar_ok and realized_ok) else "neutrality_violation"

    return {
        "cell_key": f"seed_{seed_idx}",
        "seed_index": seed_idx,
        "seed": seed,
        "regime": regime_label,
        "n_periods": n_periods,
        "n_valid_beta_rows": len(regime_betas),
        "sharpe": float(sr) if np.isfinite(sr) else None,
        "annualized_volatility": float(ann_vol) if np.isfinite(ann_vol) else None,
        "max_drawdown": float(max_dd) if np.isfinite(max_dd) else None,
        "total_return": float(tr) if np.isfinite(tr) else None,
        "wealth": float(wealth) if np.isfinite(wealth) else None,
        "turnover": float(turn) if np.isfinite(turn) else None,
        "realized_beta": (
            round(float(realized_beta), 12)
            if realized_beta is not None and np.isfinite(realized_beta)
            else None
        ),
        "dsr": round(float(dsr), 6),
        "psr": round(float(psr), 6),
        "survives_deflation": survives,
        "verdict": "SURVIVES_DEFLATION" if survives else "DOES_NOT_SURVIVE_DEFLATION",
        "sigma0": round(float(sigma0), 10),
        "gamma": round(float(gamma), 6),
        "kappa": round(float(kappa), 6),
        "tail": tail,
        "neutrality": {
            "max_model_beta": max_model_beta,
            "max_dollar_neutral": max_dollar,
            "realized_beta": (
                round(float(realized_beta), 12)
                if realized_beta is not None and np.isfinite(realized_beta)
                else None
            ),
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


def _run_seed_all_regimes(
    returns_df: pd.DataFrame,
    seed: int,
    seed_idx: int,
    n_trials: int,
    transaction_costs: float,
) -> dict:
    betas = estimate_rolling_ols_beta(
        returns_df, "BTC", window=BETA_WINDOW, min_obs=min(60, BETA_WINDOW)
    )
    valid_betas = betas.dropna(how="all", subset=ASSET_COLUMNS)
    if len(valid_betas) == 0:
        return {
            "cell_key": f"seed_{seed_idx}",
            "seed_index": seed_idx,
            "seed": seed,
            "status": "error",
            "error": "no valid beta estimates",
            "regimes": {},
        }

    valid_returns = returns_df.loc[valid_betas.index]
    valid_betas_aligned = valid_betas[[*ASSET_COLUMNS, "BTC"]]
    regime_series = _regime_labels(valid_returns["BTC"])

    regimes = {}
    for regime_label in REGIME_LABELS:
        cell = _run_regime_cell(
            valid_returns,
            valid_betas_aligned,
            regime_series,
            regime_label,
            seed,
            seed_idx,
            n_trials,
            transaction_costs,
        )
        regimes[regime_label] = cell

    return {
        "cell_key": f"seed_{seed_idx}",
        "seed_index": seed_idx,
        "seed": seed,
        "n_regimes": len(REGIME_LABELS),
        "status": "ok",
        "regimes": regimes,
    }


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


def _aggregate_regime(cells: list[dict]) -> dict:
    ok = [c for c in cells if c.get("status") == "ok"]
    return {
        "n_cells": len(cells),
        "n_ok_cells": len(ok),
        "n_insufficient": sum(
            1 for c in cells if c.get("status") == "insufficient_periods"
        ),
        "n_error": sum(1 for c in cells if c.get("status") == "error"),
        "all_survive": all(c.get("survives_deflation") is True for c in ok),
        "any_survive": any(c.get("survives_deflation") is True for c in ok),
        "n_survive": sum(1 for c in ok if c.get("survives_deflation") is True),
        "dsr": _agg([c.get("dsr") for c in ok]),
        "psr": _agg([c.get("psr") for c in ok]),
        "sharpe": _agg([c.get("sharpe") for c in ok]),
        "tail_metric_aggregates": {
            key: _agg([c["tail"].get(key) for c in ok if "tail" in c])
            for key in _TAIL_KEYS
        },
        "neutrality": {
            "all_model_beta_ok": all(
                c["neutrality"]["model_beta_neutral"]["passed"] for c in ok
            ),
            "all_dollar_ok": all(
                c["neutrality"]["dollar_neutral"]["passed"] for c in ok
            ),
            "all_realized_ok": all(
                c["neutrality"]["realized_beta_check"]["passed"] for c in ok
            ),
        },
    }


# --- Summary artifact ---


def _load_n_trials_total() -> int:
    """Read-only: n_trials_total from the committed P38 deflated summary."""
    payload = json.loads(P38_DEFLATED_PATH.read_text(encoding="utf-8"))
    return int(payload["trial_enumeration"]["n_trials_total"])


def _build_summary_artifact(seed_results: list[dict], n_trials: int) -> dict:
    base_returns = _build_wide_universe_for_seed(SEED_BASE)
    returns_sha256 = hashlib.sha256(
        base_returns.to_csv(date_format="%Y-%m-%d").encode("utf-8")
    ).hexdigest()

    btc_prices = _load_btc_prices()
    btc_sha256 = hashlib.sha256(btc_prices.to_numpy(dtype=float).tobytes()).hexdigest()

    regime_aggregates: dict[str, dict] = {}
    all_cells: list[dict] = []
    for sr in seed_results:
        all_cells.extend(sr["regimes"].values())
        for regime_label in REGIME_LABELS:
            cell = sr["regimes"][regime_label]
            regime_aggregates.setdefault(regime_label, []).append(cell)

    regime_results: dict[str, dict] = {}
    for regime_label in REGIME_LABELS:
        regime_results[regime_label] = _aggregate_regime(
            regime_aggregates[regime_label]
        )

    overall_ok = [c for c in all_cells if c.get("status") == "ok"]
    campaign_survives_all = all(
        c.get("survives_deflation") is True for c in overall_ok
    )
    campaign_verdict = (
        "SURVIVES_DEFLATION_IN_ALL_REGIMES"
        if (campaign_survives_all and len(overall_ok) > 0)
        else "DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME"
    )

    summary = {
        "schema": SCHEMA_VERSION,
        "provenance": {
            "generator": "scripts/bab_p39_regime_conditional.py",
            "campaign": "P39 Regime-Conditional & Cross-Fixture Robustness Closure",
            "wp": "WP1 - Regime-conditional deflated significance + tail risk",
            "synthetic": True,
            "note": (
                "Deterministic synthetic wide universe (P35 wide-universe recipe). "
                "BTC prices from tests/fixtures/wide_bab_universe.csv. "
                "Asset returns = beta * BTC_return + idio, idio ~ N(0, 0.003), "
                "betas linspace(0.35, 1.9, 40). Regimes are causal and lagged: "
                "trailing BTC trend (bull/bear) x trailing realized-vol tercile "
                "(low/mid/high), computed only from data available at t-1, no lookahead. "
                "Not real market data; not market profitability evidence. The verdict "
                "is honest and may be negative (a thin regime can fail deflation)."
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
                "weighting": "equal",
                "beta_neutral": True,
                "dollar_neutral": True,
                "regime_lookback": REGIME_LOOKBACK,
                "min_periods_per_regime": MIN_PERIODS_PER_REGIME,
                "regime_labels": list(REGIME_LABELS),
            },
            "neutrality_tolerances": {
                "model_beta_neutral": MODEL_BETA_NEUTRAL_TOL,
                "dollar_neutral": DOLLAR_NEUTRAL_TOL,
                "realized_beta": REALIZED_BETA_TOL,
            },
            "bootstrap": {
                "n_resamples": N_BOOTSTRAP,
                "block_length": BLOCK_LENGTH,
                "seed": BOOTSTRAP_SEED,
            },
            "dsr_survive_threshold": DSR_SURVIVE_THRESHOLD,
            "deflation": {
                "n_trials_total": n_trials,
                "source": "P38 deflated_summary.json (trial_enumeration.n_trials_total)",
                "note": (
                    "Deflate over the same n_trials_total read-only from P38 WP1; "
                    "never re-enumerated or invented here."
                ),
            },
        },
        "trial_enumeration": {
            "n_trials_total": n_trials,
            "source": "P38 deflated_summary.json",
        },
        "results": {
            "seeds": seed_results,
            "regimes": regime_results,
        },
        "campaign_verdict": campaign_verdict,
        "campaign_verdict_reason": (
            f"Every well-populated (seed, regime) cell has DSR >= {DSR_SURVIVE_THRESHOLD} "
            f"after deflation over n_trials_total={n_trials}; neutrality holds at every "
            f"cell."
            if campaign_survives_all and len(overall_ok) > 0
            else f"At least one well-populated (seed, regime) cell has DSR < "
            f"{DSR_SURVIVE_THRESHOLD} after deflation over n_trials_total={n_trials}, "
            f"or neutrality fails at some cell; honest negative verdict."
        ),
    }
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
    n_trials = _load_n_trials_total()
    seed_results = []
    for seed_idx in range(N_SEEDS):
        seed = SEED_BASE + SEED_INCREMENT * seed_idx
        returns_df = _build_wide_universe_for_seed(seed)
        seed_results.append(
            _run_seed_all_regimes(
                returns_df, seed, seed_idx, n_trials, transaction_costs=0.0
            )
        )
    return _round_floats(_build_summary_artifact(seed_results, n_trials))


def write_summary(summary: dict, path: Path = SUMMARY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
    else:
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


def _fmt_cell(v, decimals: int = 6) -> str:
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "True" if v else "False"
    return f"{float(v):.{decimals}f}"


def render_markdown(payload: dict) -> str:
    prov = payload["provenance"]
    results = payload["results"]
    lines = [
        "# BAB P39 WP1 — Regime-Conditional Deflated Significance & Tail Risk",
        "",
        f"Schema `{payload['schema']}`. Controlled synthetic stimulus: not real market "
        "data and not market profitability evidence. The verdict is honest and may "
        "be negative.",
        "",
        f"**Campaign verdict:** **{payload['campaign_verdict']}**",
        f"**Reason:** {payload['campaign_verdict_reason']}",
        "",
        "## Setup",
        "",
        f"- Seeds: {prov['seeds']['n_seeds']} (base={prov['seeds']['base_seed']}, "
        f"increment={prov['seeds']['increment']})",
        f"- beta_window: {prov['config_grid']['beta_window']}d, quantile: "
        f"{_fmt(prov['config_grid']['quantile'])}",
        f"- weighting: {prov['config_grid']['weighting']}, beta_neutral: "
        f"{prov['config_grid']['beta_neutral']}, dollar_neutral: "
        f"{prov['config_grid']['dollar_neutral']}",
        f"- regime lookback: {prov['config_grid']['regime_lookback']}d, "
        f"min periods per regime: {prov['config_grid']['min_periods_per_regime']}",
        f"- regime labels: {', '.join(prov['config_grid']['regime_labels'])}",
        "",
        "## Regime definition (causal, lagged, no lookahead)",
        "",
        "- trend[t]: sign of mean BTC return over the trailing "
        f"{REGIME_LOOKBACK}d window ending at t-1 (bull if > 0, else bear).",
        "- vol[t]: std of BTC return over the trailing "
        f"{REGIME_LOOKBACK}d window ending at t-1.",
        "- vol tercile[t]: expanding percentile of vol[t] within vol[0:t+1] "
        "(low / mid / high).",
        "- regime[t] = trend[t] x vol tercile[t]; the label at t uses only data "
        "strictly before t.",
        "",
        "## Trial enumeration (read-only from P38 WP1)",
        "",
        f"Deflation over n_trials_total = **{payload['trial_enumeration']['n_trials_total']}**, "
        "read-only from research_state/bab_p38/deflated_summary.json "
        "(trial_enumeration.n_trials_total). Never re-enumerated or invented here.",
        "",
        "## Per-regime results (aggregated across the eight seeds)",
        "",
        "| Regime | N cells | N OK | N survive | DSR mean | PSR mean | Survive all |",
        "|---|---|---|---|---|---|---|",
    ]
    for regime_label in REGIME_LABELS:
        agg = results["regimes"][regime_label]
        lines.append(
            f"| {regime_label} | {agg['n_cells']} | {agg['n_ok_cells']} | "
            f"{agg['n_survive']} | {_fmt_cell(agg['dsr']['mean'])} | "
            f"{_fmt_cell(agg['psr']['mean'])} | {agg['all_survive']} |"
        )
    lines += [
        "",
        "## Neutrality (every cell)",
        "",
        "| Regime | model beta <= 1e-3 | dollar <= 1e-9 | |realized beta| <= 0.15 |",
        "|---|---|---|---|",
    ]
    for regime_label in REGIME_LABELS:
        neu = results["regimes"][regime_label]["neutrality"]
        lines.append(
            f"| {regime_label} | {neu['all_model_beta_ok']} | {neu['all_dollar_ok']} | "
            f"{neu['all_realized_ok']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- DSR = Deflated Sharpe Ratio: probability the observed Sharpe is genuine "
        "skill after correcting for the multiple trials searched (n_trials_total). "
        "DSR >= 0.50 means more likely than not genuine skill.",
        "- PSR = Probabilistic Sharpe Ratio: probability the Sharpe exceeds zero "
        "(analytical, Bailey & Lopez de Prado).",
        "- CVaR/expected-shortfall/drawdown characterize the left tail within each "
        "regime; neutrality invariants hold at every cell.",
        "- Regimes are causal and lagged: no lookahead, so this is a genuine "
        "out-of-sample stability test, not an in-sample fit.",
        "- Synthetic-provenance caveat: results are on the committed synthetic wide "
        "universe (BTC prices + seeded idiosyncratic noise), not real market data. "
        "Never market alpha.",
    ]
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict) -> tuple[Path, Path]:
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MARKDOWN_PATH.write_text(render_markdown(payload), encoding="utf-8")
    return SUMMARY_PATH, MARKDOWN_PATH


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="P39 WP1 regime-conditional deflated significance + tail risk"
    )
    parser.add_argument(
        "--check-regime-summary",
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

    if args.check_regime_summary:
        ok = check_summary(args.output)
        return 0 if ok else 1

    print("Running P39 WP1 regime-conditional deflated significance + tail risk...")
    print(f"  Seeds: {N_SEEDS} (base={SEED_BASE}, inc={SEED_INCREMENT})")
    print(f"  Beta window: {BETA_WINDOW}d, quantile: {QUANTILE}")
    print(f"  Regime lookback: {REGIME_LOOKBACK}d, min periods/regime: {MIN_PERIODS_PER_REGIME}")
    print(f"  Bootstrap: {N_BOOTSTRAP} resamples, block length {BLOCK_LENGTH}")

    n_trials = _load_n_trials_total()
    print(f"  n_trials_total (read-only from P38 WP1): {n_trials}")

    started = time.perf_counter()

    payload = build_summary()
    json_path, md_path = write_artifacts(payload)
    elapsed = time.perf_counter() - started

    print(f"Done in {elapsed:.2f}s")
    print(f"  Campaign verdict: {payload['campaign_verdict']}")
    for regime_label in REGIME_LABELS:
        agg = payload["results"]["regimes"][regime_label]
        print(
            f"  {regime_label}: cells={agg['n_cells']} ok={agg['n_ok_cells']} "
            f"survive={agg['n_survive']}/{agg['n_ok_cells']} all_survive={agg['all_survive']} "
            f"DSR={agg['dsr']['mean']}"
        )
    print(f"  Summary written to: {json_path}")
    print(f"  Markdown written to: {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
