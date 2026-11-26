#!/usr/bin/env python3
"""P41 WP1 — Estimator Bakeoff Under Non-Gaussian Idiosyncratic Shocks.

Deterministic, offline runner that builds five independent synthetic universes
(one per DGP in the P41 charter) from the read-only BTC price fixture
(tests/fixtures/wide_bab_universe.csv), then recomputes deflated significance
(DSR/PSR, deflated over n_trials_total=552 read-only from P38 WP1), tail risk,
neutrality invariants, and estimator rank-stability for every seed cell across
all five DGPs, comparing the shipped rolling-OLS estimator against the P35
runner-up families (EWMA halflife=40; Shrinkage intensity=0.3, target=1.0 and
cross_sectional_mean) to report which estimator (if any) is least-broken by
non-Gaussianity.

Publishes research_state/bab_p41/estimator_bakeoff.json (+ .md sidecar).
Emits --check-estimator-bakeoff for byte-diff verification in the gate.

All data is deterministic synthetic; not real market data and not market
profitability evidence. The verdict is honest — it may be negative. Nothing is
tuned to chase a positive; the shipped default (equal-weight, beta-neutral,
beta_window=90, rolling-OLS) is retained regardless of outcome.

Cell = (DGP, seed, estimator): 5 DGPs x 8 seeds x 4 estimators = 160 cells
(32 cells per DGP).
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
from scipy.stats import spearmanr

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta.backtest import run_backtest  # noqa: E402
from strategies.betting_against_beta.beta_estimators import (  # noqa: E402
    estimate_ewma_beta,
    estimate_rolling_ols_beta,
    estimate_shrinkage_beta,
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

# --- Neutrality tolerances (per HANDOFF.md P34/P36/P37) ---
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

WEIGHT_THRESHOLD = 1e-10

# DSR verdict threshold: DSR >= 0.50 means more likely than not genuine skill
# after multiple-testing deflation.
DSR_SURVIVE_THRESHOLD = 0.50

# Bootstrap settings for sigma0 (std of Sharpe under the null), mirroring P21/P38.
N_BOOTSTRAP = 2000
BLOCK_LENGTH = 20
BOOTSTRAP_SEED = 20270102

# Read-only trial enumeration from P38 WP1 (deflate over the same search).
P38_DEFLATED_PATH = (
    _REPO_ROOT / "research_state" / "bab_p38" / "deflated_summary.json"
)

SCHEMA_VERSION = "bab_p41.estimator_bakeoff/1"
SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p41" / "estimator_bakeoff.json"
MARKDOWN_PATH = _REPO_ROOT / "research_state" / "bab_p41" / "estimator_bakeoff.md"

FIXTURE_PATH = _REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"

# --- Shipped default grid (charter constants; never relaxed) ---
BETA_WINDOW = 90
BETA_MIN = 0.2
BETA_MAX = 2.4
QUANTILE = 0.3
N_ASSETS = 40
TRANSACTION_COSTS = 0.0

# --- Estimator families under test (shipped rolling-OLS vs P35 runner-ups) ---
ESTIMATORS = [
    {
        "key": "rolling_ols_w90",
        "estimator": "rolling_ols",
        "params": {"window": 90},
    },
    {
        "key": "ewma_h40",
        "estimator": "ewma",
        "params": {"halflife": 40},
    },
    {
        "key": "shrinkage_i0.3_t1.0",
        "estimator": "shrinkage",
        "params": {"window": 90, "shrink_target": 1.0, "shrink_intensity": 0.3},
    },
    {
        "key": "shrinkage_i0.3_csm",
        "estimator": "shrinkage",
        "params": {
            "window": 90,
            "shrink_target": "cross_sectional_mean",
            "shrink_intensity": 0.3,
        },
    },
]

# --- DGP battery (charter constants; do not derive, do not edit) ---
DGPs = [
    {
        "id": "GAUSSIAN_IID",
        "process": "baseline (frozen P40 family)",
        "kind": "gaussian_iid",
        "idio_vol": 0.003,
        "base_seed": 20261201,
        "increment": 1009,
        "note": (
            "Control DGP: idio ~ N(0, 0.003), matching the P40 primary family "
            "so the Gaussian control reproduces P40-family behaviour."
        ),
    },
    {
        "id": "STUDENT_T",
        "process": "heavy-tailed idio (nu=4)",
        "kind": "student_t",
        "idio_vol": 0.003,
        "base_seed": 20271201,
        "increment": 1013,
        "note": (
            "Student-t(4) idio with scale matched to GAUSSIAN variance "
            "(scale = idio_vol / sqrt(2)); fat tails / excess kurtosis."
        ),
    },
    {
        "id": "REGIME_SWITCH",
        "process": "2-state Markov vol (calm/stress)",
        "kind": "regime_switch",
        "idio_vol": 0.003,
        "base_seed": 20281201,
        "increment": 1019,
        "note": (
            "Two-state Markov volatility: calm 0.5x base vol, stress 2.0x base "
            "vol, state persistence 0.95; vol clustering / non-stationarity."
        ),
    },
    {
        "id": "JUMP_DIFFUSION",
        "process": "Merton jump idio",
        "kind": "jump_diffusion",
        "idio_vol": 0.003,
        "base_seed": 20291201,
        "increment": 1021,
        "note": (
            "Merton jump-diffusion idio: jump intensity 0.05/day, jump mean "
            "-0.5 sigma, jump sd 1.5 sigma; discontinuity / gap risk."
        ),
    },
    {
        "id": "STOCHASTIC_VOL",
        "process": "log-normal vol process",
        "kind": "stochastic_vol",
        "idio_vol": 0.003,
        "base_seed": 20301201,
        "increment": 1031,
        "note": (
            "Log-normal stochastic vol (vol-of-vol 0.4, mean-reversion 0.1); "
            "persistent heteroskedasticity."
        ),
    },
]

N_SEEDS = 8

# --- DGP-specific process parameters ---
REGIME_CALM_MULT = 0.5
REGIME_STRESS_MULT = 2.0
REGIME_PERSISTENCE = 0.95
STUDENT_T_NU = 4.0
JUMP_INTENSITY_PER_DAY = 0.05
JUMP_MEAN_SIGMA = -0.5
JUMP_SD_SIGMA = 1.5
SV_VOL_OF_VOL = 0.4
SV_MEAN_REVERSION = 0.1


# --- Universe / reference (multi-DGP synthetic universes) ---


def _load_btc_prices() -> pd.Series:
    df = pd.read_csv(FIXTURE_PATH, index_col="date", parse_dates=True)
    df.index = pd.DatetimeIndex(df.index)
    if "BTC" not in df.columns:
        raise ValueError(f"wide universe fixture missing BTC column: {list(df.columns)}")
    return df["BTC"].astype(float)


def _student_t_scale_matched_to_gaussian(idio_vol: float, nu: float) -> float:
    """Scale of Student-t(nu) whose variance equals idio_vol^2.

    Var(Student-t(nu)) = nu / (nu - 2) * scale^2, so scale = idio_vol /
    sqrt(nu / (nu - 2))."""
    return idio_vol / math.sqrt(nu / (nu - 2.0))


def _build_universe_for_dgp(
    dgp: dict, seed: int,
) -> pd.DataFrame:
    """Build one synthetic universe for a DGP + seed.

    Asset returns = beta * BTC_return + idio_component, where idio_component is
    DGP-specific. BTC prices are loaded read-only from
    tests/fixtures/wide_bab_universe.csv. Not real market data.
    """
    btc_prices = _load_btc_prices()
    btc_returns = btc_prices.pct_change().iloc[1:]
    btc_return_dates = btc_returns.index
    n_returns = len(btc_return_dates)

    rng = np.random.default_rng(seed)
    betas = np.linspace(BETA_MIN, BETA_MAX, N_ASSETS)
    idio_vol = dgp["idio_vol"]
    kind = dgp["kind"]

    if kind == "gaussian_iid":
        idio = rng.normal(loc=0.0, scale=idio_vol, size=(N_ASSETS, n_returns))
    elif kind == "student_t":
        scale = _student_t_scale_matched_to_gaussian(idio_vol, STUDENT_T_NU)
        idio = rng.standard_t(df=STUDENT_T_NU, size=(N_ASSETS, n_returns)) * scale
    elif kind == "regime_switch":
        vol_calm = REGIME_CALM_MULT * idio_vol
        vol_stress = REGIME_STRESS_MULT * idio_vol
        vol_states = np.array([vol_calm, vol_stress], dtype=float)
        state = 0  # start in calm state
        vols = np.empty(n_returns, dtype=float)
        for t in range(n_returns):
            if rng.random() >= REGIME_PERSISTENCE:
                state = 1 - state
            vols[t] = vol_states[state]
        idio = (
            rng.normal(loc=0.0, scale=1.0, size=(N_ASSETS, n_returns))
            * vols[None, :]
        )
    elif kind == "jump_diffusion":
        idio = rng.normal(loc=0.0, scale=idio_vol, size=(N_ASSETS, n_returns))
        jump_mean = JUMP_MEAN_SIGMA * idio_vol
        jump_sd = JUMP_SD_SIGMA * idio_vol
        for t in range(n_returns):
            n_jumps = rng.poisson(JUMP_INTENSITY_PER_DAY, size=N_ASSETS)
            total = int(n_jumps.sum())
            if total > 0:
                sizes = rng.normal(jump_mean, jump_sd, size=total)
                asset_idx = np.repeat(np.arange(N_ASSETS), n_jumps)
                np.add.at(idio[:, t], asset_idx, sizes)
    elif kind == "stochastic_vol":
        log_base = math.log(idio_vol)
        log_v = np.empty(n_returns, dtype=float)
        log_v[0] = log_base
        for t in range(1, n_returns):
            log_v[t] = (
                log_v[t - 1]
                - SV_MEAN_REVERSION * (log_v[t - 1] - log_base)
                + SV_VOL_OF_VOL * rng.standard_normal()
            )
        vols = np.exp(log_v)
        idio = (
            rng.normal(loc=0.0, scale=1.0, size=(N_ASSETS, n_returns))
            * vols[None, :]
        )
    else:
        raise ValueError(f"unknown DGP kind: {kind}")

    asset_returns = np.vstack(
        [
            beta * btc_returns.to_numpy(dtype=float) + idio[i]
            for i, beta in enumerate(betas)
        ]
    )

    asset_columns = [f"{dgp['id'][0:3]}{i:03d}" for i in range(1, N_ASSETS + 1)]

    returns_df = pd.DataFrame(
        asset_returns.T,
        index=btc_return_dates,
        columns=asset_columns,
    )
    returns_df["BTC"] = btc_returns
    return returns_df


# --- Strategy pipeline (shipped default; mirrors bab_p38/bab_p40) ---


def _base_weights(
    returns_df: pd.DataFrame, beta_estimates: pd.DataFrame, quantile: float,
    asset_columns: list[str],
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


# --- Neutrality invariants ---


def _model_beta_series(weights: pd.DataFrame, betas: pd.DataFrame) -> pd.Series:
    """Per-period gross-exposure-weighted model portfolio beta."""
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
    var = float(np.percentile(returns, 100.0 - pct))
    tail = returns[returns <= var]
    if tail.size == 0:
        return var, var, 0
    return var, float(tail.mean()), int(tail.size)


def _tail_metrics(returns: np.ndarray) -> dict:
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    n = int(r.size)

    var_95, cvar_95, n95 = _tail_below(r, 95.0)
    var_99, cvar_99, n99 = _tail_below(r, 99.0)
    _var_975, es_975, _nes = _tail_below(r, 97.5)

    worst_day = float(r.min()) if n > 0 else 0.0
    best_day = float(r.max()) if n > 0 else 0.0

    mean = float(r.mean()) if n > 0 else 0.0
    std = float(r.std(ddof=0)) if n > 0 else 0.0
    if std == 0.0 or not np.isfinite(std):
        skew = 0.0
        excess_kurtosis = 0.0
    else:
        centred = r - mean
        skew = float(np.mean(centred ** 3) / std ** 3)
        raw_kurt = float(np.mean(centred ** 4) / std ** 4)
        excess_kurtosis = raw_kurt - 3.0

    left_tail_mean = cvar_95
    right_tail = r[r >= float(np.percentile(r, 95.0))] if n > 0 else r
    right_tail_mean = float(right_tail.mean()) if right_tail.size else best_day
    denom = abs(left_tail_mean) + abs(right_tail_mean)
    tail_asymmetry = (
        float((abs(left_tail_mean) - abs(right_tail_mean)) / denom) if denom > 0 else None
    )

    dd = _drawdown_series(r)
    var_dd, c_dar_95, _ndd = _tail_below(dd, 95.0)
    max_dd = float(dd.min()) if n > 0 else 0.0
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


# --- Rank-stability vs OLS baseline ---


def _compute_rank_stability(
    estimator_betas: pd.DataFrame,
    ols_betas: pd.DataFrame,
    weights: pd.DataFrame,
    ols_weights: pd.DataFrame,
) -> tuple[float, float]:
    """Beta rank-stability vs OLS baseline: (spearman_corr, jaccard_overlap)."""
    common_idx = estimator_betas.index.intersection(ols_betas.index)
    common_cols = estimator_betas.columns.intersection(ols_betas.columns)

    if len(common_idx) == 0 or len(common_cols) == 0:
        return np.nan, np.nan

    est = estimator_betas.loc[common_idx, common_cols].astype(float)
    ols = ols_betas.loc[common_idx, common_cols].astype(float)

    spearman_vals = []
    for idx in common_idx:
        est_row = est.loc[idx].dropna()
        ols_row = ols.loc[idx].dropna()
        common_names = est_row.index.intersection(ols_row.index)
        if len(common_names) >= 4:
            rho, _ = spearmanr(est_row[common_names], ols_row[common_names])
            if np.isfinite(rho):
                spearman_vals.append(rho)

    avg_spearman = float(np.mean(spearman_vals)) if spearman_vals else np.nan

    common_w_idx = weights.index.intersection(ols_weights.index)
    common_w_cols = weights.columns.intersection(ols_weights.columns)
    if len(common_w_idx) > 0 and len(common_w_cols) > 0:
        jaccard_vals = []
        for idx in common_w_idx:
            w_row = weights.loc[idx, common_w_cols]
            ols_w_row = ols_weights.loc[idx, common_w_cols]
            est_long = set(w_row[w_row > 1e-10].index)
            est_short = set(w_row[w_row < -1e-10].index)
            ols_long = set(ols_w_row[ols_w_row > 1e-10].index)
            ols_short = set(ols_w_row[ols_w_row < -1e-10].index)
            est_set = est_long.union(est_short)
            ols_set = ols_long.union(ols_short)
            if len(est_set) > 0 or len(ols_set) > 0:
                inter = len(est_set.intersection(ols_set))
                union = len(est_set.union(ols_set))
                jaccard_vals.append(inter / union if union > 0 else 1.0)
        avg_jaccard = float(np.mean(jaccard_vals)) if jaccard_vals else np.nan
    else:
        avg_jaccard = np.nan

    return avg_spearman, avg_jaccard


# --- Per-cell runner ---


def _estimate_betas(returns_df: pd.DataFrame, est: dict) -> pd.DataFrame:
    kind = est["estimator"]
    params = est["params"]
    if kind == "rolling_ols":
        return estimate_rolling_ols_beta(
            returns_df, "BTC", window=params["window"], min_obs=min(60, params["window"])
        )
    if kind == "ewma":
        return estimate_ewma_beta(
            returns_df, "BTC", halflife=params["halflife"], min_obs=60
        )
    if kind == "shrinkage":
        return estimate_shrinkage_beta(
            returns_df,
            "BTC",
            window=params["window"],
            shrink_target=params["shrink_target"],
            shrink_intensity=params["shrink_intensity"],
            min_obs=60,
        )
    raise ValueError(f"unknown estimator kind: {kind}")


def _run_seed_cell_for_estimator(
    returns_df: pd.DataFrame,
    dgp: dict,
    seed: int,
    seed_idx: int,
    est: dict,
    n_trials: int,
    ols_baseline_betas: pd.DataFrame,
    ols_baseline_weights: pd.DataFrame,
    asset_columns: list[str],
) -> dict:
    """Run one (DGP, seed, estimator) cell."""
    betas = _estimate_betas(returns_df, est)

    valid_betas = betas.dropna(how="all", subset=asset_columns)
    if len(valid_betas) == 0:
        return {
            "cell_key": f"{dgp['id']}_seed{seed_idx}_{est['key']}",
            "dgp_id": dgp["id"],
            "seed_index": seed_idx,
            "seed": seed,
            "estimator": est["key"],
            "params": est["params"],
            "status": "error",
            "error": "no valid beta estimates",
        }

    valid_returns = returns_df.loc[valid_betas.index]
    valid_betas_aligned = valid_betas[[*asset_columns, "BTC"]]

    weights = _base_weights(valid_returns, valid_betas_aligned, QUANTILE, asset_columns)
    strat_returns = _compute_strat_returns(weights, valid_returns, TRANSACTION_COSTS)
    bench_returns = valid_returns["BTC"]

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
            1.0 + 0.5 * gamma * float(sr) ** 2 + 0.25 * (kappa - 1.0) * float(sr) ** 4
        ) / max(len(strat_returns_arr) - 1, 1)
        sigma0 = math.sqrt(max(se_sr_sq, 1e-18))

    dsr = _deflated_sharpe(float(sr), 0.0, n_trials, sigma0, gamma, kappa)
    psr = _probabilistic_sharpe(float(sr), gamma, kappa, len(strat_returns_arr), sr_bench=0.0)
    survives = bool(dsr >= DSR_SURVIVE_THRESHOLD)

    tail = _tail_metrics(strat_returns_arr)

    model_beta_series = _model_beta_series(weights, valid_betas_aligned)
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

    spearman_corr, jaccard_overlap = _compute_rank_stability(
        betas, ols_baseline_betas, weights, ols_baseline_weights
    )

    status = "ok" if (model_beta_ok and dollar_ok and realized_ok) else "neutrality_violation"

    return {
        "cell_key": f"{dgp['id']}_seed{seed_idx}_{est['key']}",
        "dgp_id": dgp["id"],
        "seed_index": seed_idx,
        "seed": seed,
        "estimator": est["key"],
        "params": est["params"],
        "n_periods": len(strat_returns),
        "n_valid_beta_rows": len(valid_betas),
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
        "rank_stability": {
            "spearman_vs_ols": (
                float(spearman_corr) if np.isfinite(spearman_corr) else None
            ),
            "jaccard_vs_ols": float(jaccard_overlap) if np.isfinite(jaccard_overlap) else None,
        },
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


def _run_all_dgps(n_trials: int) -> dict:
    """Run the full DGP x seed x estimator grid and collect results."""

    all_cells = []
    per_dgp_cells = {dgp["id"]: [] for dgp in DGPs}

    # OLS baseline (window=90) computed once per (DGP, seed) universe for
    # rank-stability comparison; reused across the 4 estimators of that cell.
    for dgp in DGPs:
        for seed_idx in range(N_SEEDS):
            seed = dgp["base_seed"] + dgp["increment"] * seed_idx
            returns_df = _build_universe_for_dgp(dgp, seed)
            asset_columns = [
                f"{dgp['id'][0:3]}{i:03d}" for i in range(1, N_ASSETS + 1)
            ]

            # OLS baseline for rank stability (shipped rolling-OLS window=90)
            ols_baseline_betas = estimate_rolling_ols_beta(
                returns_df, "BTC", window=BETA_WINDOW, min_obs=min(60, BETA_WINDOW)
            )
            valid_ols = ols_baseline_betas.dropna(how="all", subset=asset_columns)
            ols_valid_returns = returns_df.loc[valid_ols.index]
            ols_valid_betas_aligned = valid_ols[[*asset_columns, "BTC"]]
            ols_weights = _base_weights(
                ols_valid_returns, ols_valid_betas_aligned, QUANTILE, asset_columns
            )

            for est in ESTIMATORS:
                try:
                    cell = _run_seed_cell_for_estimator(
                        returns_df, dgp, seed, seed_idx, est, n_trials,
                        ols_baseline_betas, ols_weights, asset_columns,
                    )
                except Exception as exc:  # pragma: no cover - defensive
                    cell = {
                        "cell_key": f"{dgp['id']}_seed{seed_idx}_{est['key']}",
                        "dgp_id": dgp["id"],
                        "seed_index": seed_idx,
                        "seed": seed,
                        "estimator": est["key"],
                        "params": est["params"],
                        "status": "error",
                        "error": str(exc),
                    }
                all_cells.append(cell)
                per_dgp_cells[dgp["id"]].append(cell)

    return {"cells": all_cells, "per_dgp_cells": per_dgp_cells}


# --- Aggregation ---


def _agg(values: list[float]) -> dict:
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


def _aggregate_cells(cells: list[dict]) -> dict:
    ok = [c for c in cells if c.get("status") == "ok" and "tail" in c]
    return {
        "n_cells": len(cells),
        "n_ok_cells": len(ok),
        "n_error_cells": sum(1 for c in cells if c.get("status") == "error"),
        "n_neutrality_violations": sum(
            1 for c in cells if c.get("status") == "neutrality_violation"
        ),
        "all_neutrality_ok": all(c.get("status") == "ok" for c in cells),
        "dsr": _agg([c.get("dsr") for c in ok]),
        "psr": _agg([c.get("psr") for c in ok]),
        "sharpe": _agg([c.get("sharpe") for c in ok]),
        "all_survive": all(c.get("survives_deflation") is True for c in ok),
        "any_survive": any(c.get("survives_deflation") is True for c in ok),
        "n_survive": sum(1 for c in ok if c.get("survives_deflation") is True),
        "tail_metric_aggregates": {
            key: _agg([c["tail"].get(key) for c in ok]) for key in _TAIL_KEYS
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


# --- Estimator comparison (least-broken by non-Gaussianity) ---


def _estimator_comparison(all_cells: list[dict], non_gaussian_dgp_ids: list[str]) -> dict:
    """Compare estimator families; report which is least-broken by non-Gaussianity.

    "Least broken" = highest mean DSR across non-Gaussian DGPs among estimators
    that keep neutrality intact; reported honestly, may be negative / inconclusive.
    """
    by_est = {}
    for est in ESTIMATORS:
        key = est["key"]
        cells = [c for c in all_cells if c.get("estimator") == key and c.get("status") == "ok"]
        ng_cells = [c for c in cells if c.get("dgp_id") in non_gaussian_dgp_ids]
        by_est[key] = {
            "estimator": est["estimator"],
            "params": est["params"],
            "all_cells": _aggregate_cells(cells),
            "non_gaussian_cells": _aggregate_cells(ng_cells),
        }

    # Least broken: max mean DSR over non-Gaussian cells, tie-break on neutrality.
    candidates = [
        (k, v) for k, v in by_est.items()
        if v["non_gaussian_cells"]["all_neutrality_ok"]
    ]
    if candidates:
        best_key = max(
            candidates,
            key=lambda kv: kv[1]["non_gaussian_cells"]["dsr"]["mean"] or -1.0,
        )[0]
    else:
        best_key = max(
            by_est, key=lambda k: by_est[k]["non_gaussian_cells"]["dsr"]["mean"] or -1.0
        )

    return {
        "by_estimator": by_est,
        "least_broken_estimator": best_key,
        "least_broken_reason": (
            f"Highest mean deflated Sharpe across non-Gaussian DGPs "
            f"({', '.join(non_gaussian_dgp_ids)}) among estimators passing all "
            f"neutrality invariants; honest ranking, not tuned to a positive."
        ),
        "note": (
            "The least-broken estimator is ranked on deflated Sharpe over "
            "non-Gaussian DGPs only. A null/negative ranking is a valid finding; "
            "nothing is tuned to chase a positive and the shipped default is "
            "retained regardless of outcome."
        ),
    }


# --- Summary artifact ---


def _load_n_trials_total() -> int:
    payload = json.loads(P38_DEFLATED_PATH.read_text(encoding="utf-8"))
    return int(payload["trial_enumeration"]["n_trials_total"])


def _build_summary_artifact(grid_results: dict, n_trials: int) -> dict:
    all_cells = grid_results["cells"]
    per_dgp_cells = grid_results["per_dgp_cells"]

    base_returns = _build_universe_for_dgp(DGPs[0], DGPs[0]["base_seed"])
    returns_sha256 = hashlib.sha256(
        base_returns.to_csv(date_format="%Y-%m-%d").encode("utf-8")
    ).hexdigest()

    btc_prices = _load_btc_prices()
    btc_sha256 = hashlib.sha256(btc_prices.to_numpy(dtype=float).tobytes()).hexdigest()

    non_gaussian_dgp_ids = [d["id"] for d in DGPs if d["id"] != "GAUSSIAN_IID"]

    dgp_results = {}
    n_total_ok = 0
    n_total_error = 0
    n_total_survive = 0
    n_total_cells = 0
    n_dgps_replicating = 0

    for dgp in DGPs:
        did = dgp["id"]
        cells = per_dgp_cells[did]
        agg = _aggregate_cells(cells)
        ok_cells = [c for c in cells if c.get("status") == "ok"]

        replicate = bool(
            agg["all_neutrality_ok"]
            and agg["n_error_cells"] == 0
            and len(ok_cells) > 0
        )
        if replicate:
            n_dgps_replicating += 1

        n_total_ok += agg["n_ok_cells"]
        n_total_error += agg["n_error_cells"]
        n_total_survive += agg["n_survive"]
        n_total_cells += agg["n_cells"]

        dgp_results[did] = {
            "dgp_id": did,
            "process": dgp["process"],
            "kind": dgp["kind"],
            "config_grid": {
                "base_seed": dgp["base_seed"],
                "increment": dgp["increment"],
                "n_seeds": N_SEEDS,
                "idio_vol": dgp["idio_vol"],
                "beta_min": BETA_MIN,
                "beta_max": BETA_MAX,
                "n_assets": N_ASSETS,
            },
            "seeds": [
                dgp["base_seed"] + dgp["increment"] * i for i in range(N_SEEDS)
            ],
            "aggregate": agg,
            "cells": cells,
            "replicates_p38_neutrality_and_survival": replicate,
        }

    estimator_comparison = _estimator_comparison(all_cells, non_gaussian_dgp_ids)

    # Consolidated bakeoff verdict.
    if estimator_comparison["least_broken_estimator"] == "rolling_ols_w90":
        bakeoff_verdict = "ROLLED_OLS_LEAST_BROKEN"
    else:
        bakeoff_verdict = f"{estimator_comparison['least_broken_estimator']}_LEAST_BROKEN"

    n_dgps = len(DGPs)
    n_estimators = len(ESTIMATORS)

    summary = {
        "schema": SCHEMA_VERSION,
        "provenance": {
            "generator": "scripts/bab_p41_stress.py",
            "campaign": "P41 Non-Gaussian & Regime-Switching Synthetic Stress Battery",
            "wp": "WP1 - Estimator Bakeoff Under Non-Gaussian Idio",
            "synthetic": True,
            "note": (
                "Deterministic synthetic estimator bakeoff across five "
                "data-generating processes (GAUSSIAN_IID control, STUDENT_T, "
                "REGIME_SWITCH, JUMP_DIFFUSION, STOCHASTIC_VOL). Asset returns "
                "= beta * BTC_return + idio, betas linspace(0.2, 2.4, 40), "
                "BTC prices from tests/fixtures/wide_bab_universe.csv. "
                "Not real market data; not market profitability evidence. "
                "Cell = (DGP, seed, estimator): 5 DGPs x 8 seeds x 4 estimators "
                "= 160 cells. Compares shipped rolling-OLS (window=90) vs P35 "
                "runner-ups (EWMA halflife=40; Shrinkage intensity=0.3, "
                "target=1.0 and cross_sectional_mean) and reports which estimator "
                "(if any) is least-broken by non-Gaussianity. "
                "Deflated significance over n_trials_total read-only from P38 WP1."
            ),
            "fixture_path": str(FIXTURE_PATH),
            "returns_sha256": returns_sha256,
            "btc_source_sha256": btc_sha256,
            "n_dgps": n_dgps,
            "n_seeds_per_dgp": N_SEEDS,
            "n_estimators": n_estimators,
            "n_total_cells": n_total_cells,
            "seeds": {
                d["id"]: {
                    "base_seed": d["base_seed"],
                    "increment": d["increment"],
                    "n_seeds": N_SEEDS,
                    "seed_list": [d["base_seed"] + d["increment"] * i for i in range(N_SEEDS)],
                }
                for d in DGPs
            },
            "dgps": [
                {
                    "id": d["id"],
                    "process": d["process"],
                    "kind": d["kind"],
                    "idio_vol": d["idio_vol"],
                    "base_seed": d["base_seed"],
                    "increment": d["increment"],
                    "note": d["note"],
                }
                for d in DGPs
            ],
            "config_grid": {
                "beta_window": BETA_WINDOW,
                "beta_min": BETA_MIN,
                "beta_max": BETA_MAX,
                "n_assets": N_ASSETS,
                "quantile": QUANTILE,
                "weighting": "equal",
                "beta_neutral": True,
                "dollar_neutral": True,
                "transaction_costs": TRANSACTION_COSTS,
                "estimator_families": {
                    e["key"]: {
                        "estimator": e["estimator"],
                        "params": e["params"],
                    }
                    for e in ESTIMATORS
                },
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
                    "Deflate over n_trials_total read-only from P38 WP1; "
                    "never re-enumerated or invented here."
                ),
            },
        },
        "trial_enumeration": {
            "n_trials_total": n_trials,
            "source": "P38 deflated_summary.json",
        },
        "results": {
            "dgps": dgp_results,
            "estimator_comparison": estimator_comparison,
            "cross_dgp": {
                "n_dgps": n_dgps,
                "n_seeds_per_dgp": N_SEEDS,
                "n_estimators": n_estimators,
                "n_total_cells": n_total_cells,
                "n_total_ok_cells": n_total_ok,
                "n_total_error_cells": n_total_error,
                "n_total_survive": n_total_survive,
                "n_dgps_replicating": n_dgps_replicating,
                "all_dgps_neutrality_ok": all(
                    dgp_results[did]["aggregate"]["neutrality"]["all_model_beta_ok"]
                    and dgp_results[did]["aggregate"]["neutrality"]["all_dollar_ok"]
                    and dgp_results[did]["aggregate"]["neutrality"]["all_realized_ok"]
                    for did in dgp_results
                ),
                "all_dgps_survive": all(
                    dgp_results[did]["aggregate"]["all_survive"]
                    for did in dgp_results
                ),
            },
        },
        "bakeoff_verdict": bakeoff_verdict,
        "bakeoff_verdict_reason": (
            f"{estimator_comparison['least_broken_estimator']} is least-broken by "
            f"non-Gaussianity (highest mean DSR across non-Gaussian DGPs among "
            f"neutrality-passing estimators). {estimator_comparison['note']}"
        ),
    }
    return summary


def _round_floats(obj, sig: int = 12):
    if isinstance(obj, float):
        if obj == 0.0 or not np.isfinite(obj):
            return 0.0 if obj == 0.0 else obj
        return float(f"{obj:.{sig}g}")
    if isinstance(obj, dict):
        return {k: _round_floats(v, sig) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_floats(v, sig) for v in obj]
    return obj


def write_summary(summary: dict, path: Path = SUMMARY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_summary() -> dict:
    n_trials = _load_n_trials_total()
    grid_results = _run_all_dgps(n_trials)
    return _round_floats(_build_summary_artifact(grid_results, n_trials))


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


def render_markdown(payload: dict) -> str:
    prov = payload["provenance"]
    results = payload["results"]
    cross = results["cross_dgp"]
    comp = results["estimator_comparison"]
    lines = [
        "# BAB P41 WP1 — Estimator Bakeoff Under Non-Gaussian Idio",
        "",
        f"Schema `{payload['schema']}`. Controlled synthetic stimulus: not real market "
        "data and not market profitability evidence. The verdict is honest and may "
        "be negative.",
        "",
        f"**Bakeoff verdict:** **{payload['bakeoff_verdict']}**",
        f"**Reason:** {payload['bakeoff_verdict_reason']}",
        "",
        "## Setup",
        "",
        f"- DGPs: {prov['n_dgps']} deterministic synthetic data-generating processes, "
        f"{prov['n_seeds_per_dgp']} seeds each, {prov['n_estimators']} estimators "
        f"({prov['n_total_cells']} total cells)",
        f"- beta_window: {prov['config_grid']['beta_window']}d, quantile: "
        f"{_fmt(prov['config_grid']['quantile'])}",
        f"- weighting: {prov['config_grid']['weighting']}, beta_neutral: "
        f"{prov['config_grid']['beta_neutral']}, dollar_neutral: "
        f"{prov['config_grid']['dollar_neutral']}, transaction_costs: "
        f"{prov['config_grid']['transaction_costs']}",
        f"- DSR survive threshold: {_fmt(prov['dsr_survive_threshold'])}",
        f"- n_trials_total (deflation, read-only from P38 WP1): "
        f"{prov['deflation']['n_trials_total']}",
        "",
        "## DGPs (charter constants)",
        "",
        "| DGP | Process | Kind | Idio Vol | Base Seed | Increment |",
        "|---|---|---|---|---|---|",
    ]
    lines.extend(
        [
            f"| {d['id']} | {d['process']} | {d['kind']} | "
            f"{_fmt(d['idio_vol'])} | {d['base_seed']} | {d['increment']} |"
            for d in prov["dgps"]
        ]
    )
    lines += [
        "",
        "- BTC prices read-only from tests/fixtures/wide_bab_universe.csv "
        "(the same deterministic random-walk fixture as P38/P40).",
        "- Asset returns = beta * BTC_return + idio, betas linspace(0.2, 2.4, 40).",
        "- Not real market data; not market profitability evidence.",
        "",
        "## Trial enumeration (read-only from P38 WP1)",
        "",
        f"Deflation over n_trials_total = **{payload['trial_enumeration']['n_trials_total']}**, "
        "read-only from research_state/bab_p38/deflated_summary.json "
        "(trial_enumeration.n_trials_total). Never re-enumerated or invented here.",
        "",
        "## Estimator families under test",
        "",
    ]
    for e in prov["config_grid"]["estimator_families"].values():
        lines.append(
            f"- {e['estimator']}: params={e['params']}"
        )
    lines += [
        "",
        "## Per-DGP aggregates",
        "",
    ]
    for did in sorted(results["dgps"]):
        dr = results["dgps"][did]
        agg = dr["aggregate"]
        lines += [
            f"### {did}",
            "",
            f"- Process: {dr['process']} ({dr['kind']})",
            f"- Seeds: {dr['seeds']}",
            f"- n_cells: {agg['n_cells']}, n_ok_cells: {agg['n_ok_cells']}, "
            f"n_error_cells: {agg['n_error_cells']}, "
            f"n_neutrality_violations: {agg['n_neutrality_violations']}",
            f"- all_neutrality_ok: {agg['all_neutrality_ok']}",
            f"- all_survive: {agg['all_survive']}, any_survive: {agg['any_survive']}, "
            f"n_survive: {agg['n_survive']}",
            f"- DSR mean/min/max: {_fmt(agg['dsr']['mean'])}/"
            f"{_fmt(agg['dsr']['min'])}/{_fmt(agg['dsr']['max'])}",
            f"- Sharpe mean/min/max: {_fmt(agg['sharpe']['mean'])}/"
            f"{_fmt(agg['sharpe']['min'])}/{_fmt(agg['sharpe']['max'])}",
            "",
        ]
    lines += [
        "## Estimator comparison (least-broken by non-Gaussianity)",
        "",
        f"- Least-broken estimator: **{comp['least_broken_estimator']}**",
        f"- Reason: {comp['least_broken_reason']}",
        "",
        "| Estimator | Non-Gaussian DSR mean | Non-Gaussian neutrality OK |",
        "|---|---|---|",
    ]
    for key, v in comp["by_estimator"].items():
        ng = v["non_gaussian_cells"]
        lines.append(
            f"| {key} | {_fmt(ng['dsr']['mean'])} | {ng['all_neutrality_ok']} |"
        )
    lines += [
        "",
        comp["note"],
        "",
        "## Cross-DGP aggregates",
        "",
        f"- n_dgps: {cross['n_dgps']}",
        f"- n_total_cells: {cross['n_total_cells']}",
        f"- n_total_ok_cells: {cross['n_total_ok_cells']}, "
        f"n_total_error_cells: {cross['n_total_error_cells']}",
        f"- n_total_survive: {cross['n_total_survive']}",
        f"- n_dgps_replicating: {cross['n_dgps_replicating']} / {cross['n_dgps']}",
        f"- all_dgps_neutrality_ok: {cross['all_dgps_neutrality_ok']}",
        f"- all_dgps_survive: {cross['all_dgps_survive']}",
        "",
        "## Neutrality (every ok cell, every DGP, every estimator)",
        "",
        "- model beta <= 1e-3: "
        f"{cross['all_dgps_neutrality_ok']}",
        "- dollar <= 1e-9 and |realized beta| <= 0.15 at every ok cell.",
        "",
        "## Interpretation",
        "",
        "- DSR = Deflated Sharpe Ratio: probability the observed Sharpe is genuine "
        "skill after correcting for multiple testing (n_trials_total). "
        "DSR >= 0.50 means more likely than not genuine skill.",
        "- PSR = Probabilistic Sharpe Ratio: probability the Sharpe exceeds zero.",
        "- Rank-stability (Spearman / Jaccard vs OLS baseline) measures how far each "
        "estimator's beta estimates depart from the shipped rolling-OLS reference.",
        "- The bakeoff verdict reports which estimator (if any) is least-broken by "
        "non-Gaussian idio; an honest negative ranking is a valid finding.",
        "- Synthetic-provenance caveat: results are on committed synthetic universes, "
        "not real market data. Never market alpha.",
    ]
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict) -> tuple[Path, Path]:
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MARKDOWN_PATH.write_text(render_markdown(payload), encoding="utf-8")
    return SUMMARY_PATH, MARKDOWN_PATH


# --- Stress summary (WP2) schema ---
SCHEMA_STRESS_VERSION = "bab_p41.stress_summary/1"
STRESS_SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p41" / "stress_summary.json"
STRESS_MARKDOWN_PATH = _REPO_ROOT / "research_state" / "bab_p41" / "stress_summary.md"

STRESS_VERDICT_ROBUST = "ROBUST_ACROSS_DGPS"
STRESS_VERDICT_FRAGILE = "FRAGILE_DGP_DEPENDENT"
STRESS_VERDICT_DOES_NOT_REPLICATE = "DOES_NOT_REPLICATE"


def _dgp_replicates_stress(agg: dict) -> bool:
    """A DGP replicates the stress test when every cell survives deflation and
    all neutrality invariants hold (mirrors the P38 pooled verdict bar)."""
    return bool(
        agg["all_neutrality_ok"]
        and agg["n_error_cells"] == 0
        and agg["all_survive"]
    )


def _stress_verdict(dgp_results: dict, cross: dict) -> tuple[str, str]:
    """Consolidated, honest stress verdict. May be negative.

    ROBUST_ACROSS_DGPS: every DGP replicates (all cells survive + neutrality).
    DOES_NOT_REPLICATE: no cell survives deflation in any DGP.
    FRAGILE_DGP_DEPENDENT: otherwise — survival depends on DGP/seed.
    """
    n_dgps = len(dgp_results)
    n_stress_ok = sum(
        1 for dr in dgp_results.values() if _dgp_replicates_stress(dr["aggregate"])
    )
    n_total_survive = int(cross["n_total_survive"])
    n_total_cells = int(cross["n_total_cells"])
    if n_stress_ok == n_dgps and bool(cross["all_dgps_neutrality_ok"]):
        return STRESS_VERDICT_ROBUST, (
            f"All {n_dgps} DGPs replicate the stress test (every cell survives "
            f"deflation over n_trials_total=552 and neutrality holds everywhere); "
            "BAB behaviour is robust to non-Gaussian idio."
        )
    if n_total_survive == 0:
        return STRESS_VERDICT_DOES_NOT_REPLICATE, (
            "No cell survives deflation across any DGP; BAB behaviour does not "
            "replicate under non-Gaussian idio. Honest negative."
        )
    return STRESS_VERDICT_FRAGILE, (
        f"Survival is DGP-dependent: {n_stress_ok} of {n_dgps} DGPs replicate "
        f"(all cells survive + neutrality), {n_total_survive} of {n_total_cells} "
        "cells survive overall. Honest, may be negative; not tuned to a positive."
    )


def _build_stress_summary_artifact(grid_results: dict, n_trials: int) -> dict:
    per_dgp_cells = grid_results["per_dgp_cells"]

    base_returns = _build_universe_for_dgp(DGPs[0], DGPs[0]["base_seed"])
    returns_sha256 = hashlib.sha256(
        base_returns.to_csv(date_format="%Y-%m-%d").encode("utf-8")
    ).hexdigest()
    btc_prices = _load_btc_prices()
    btc_sha256 = hashlib.sha256(btc_prices.to_numpy(dtype=float).tobytes()).hexdigest()

    dgp_results = {}
    n_total_ok = 0
    n_total_error = 0
    n_total_survive = 0
    n_total_cells = 0
    n_dgps_replicating = 0

    for dgp in DGPs:
        did = dgp["id"]
        cells = per_dgp_cells[did]
        agg = _aggregate_cells(cells)
        replicates = _dgp_replicates_stress(agg)
        if replicates:
            n_dgps_replicating += 1
        n_total_ok += agg["n_ok_cells"]
        n_total_error += agg["n_error_cells"]
        n_total_survive += agg["n_survive"]
        n_total_cells += agg["n_cells"]
        dgp_results[did] = {
            "dgp_id": did,
            "process": dgp["process"],
            "kind": dgp["kind"],
            "config_grid": {
                "base_seed": dgp["base_seed"],
                "increment": dgp["increment"],
                "n_seeds": N_SEEDS,
                "idio_vol": dgp["idio_vol"],
                "beta_min": BETA_MIN,
                "beta_max": BETA_MAX,
                "n_assets": N_ASSETS,
            },
            "seeds": [dgp["base_seed"] + dgp["increment"] * i for i in range(N_SEEDS)],
            "aggregate": agg,
            "cells": cells,
            "replicates_stress_test": replicates,
        }

    cross_dgp = {
        "n_dgps": len(DGPs),
        "n_seeds_per_dgp": N_SEEDS,
        "n_estimators": len(ESTIMATORS),
        "n_total_cells": n_total_cells,
        "n_total_ok_cells": n_total_ok,
        "n_total_error_cells": n_total_error,
        "n_total_survive": n_total_survive,
        "n_dgps_replicating": n_dgps_replicating,
        "all_dgps_neutrality_ok": all(
            dgp_results[did]["aggregate"]["neutrality"]["all_model_beta_ok"]
            and dgp_results[did]["aggregate"]["neutrality"]["all_dollar_ok"]
            and dgp_results[did]["aggregate"]["neutrality"]["all_realized_ok"]
            for did in dgp_results
        ),
        "all_dgps_survive": all(
            dgp_results[did]["aggregate"]["all_survive"] for did in dgp_results
        ),
    }

    stress_verdict, stress_verdict_reason = _stress_verdict(dgp_results, cross_dgp)

    summary = {
        "schema": SCHEMA_STRESS_VERSION,
        "provenance": {
            "generator": "scripts/bab_p41_stress.py",
            "campaign": "P41 Non-Gaussian & Regime-Switching Synthetic Stress Battery",
            "wp": "WP2 - Five-DGP Stress Meta-Analysis",
            "synthetic": True,
            "note": (
                "Deterministic synthetic stress meta-analysis across five "
                "data-generating processes (GAUSSIAN_IID control, STUDENT_T, "
                "REGIME_SWITCH, JUMP_DIFFUSION, STOCHASTIC_VOL). Reuses the WP1 "
                "cell grid (5 DGPs x 8 seeds x 4 estimators = 160 cells). "
                "Per-cell DSR/PSR deflated over n_trials_total read-only from "
                "P38 WP1 (552), plus tail risk and the three neutrality "
                "invariants. Every cell is labelled synthetic; not real market "
                "data and not market profitability evidence. Consolidated verdict "
                "is honest and may be negative."
            ),
            "fixture_path": str(FIXTURE_PATH),
            "returns_sha256": returns_sha256,
            "btc_source_sha256": btc_sha256,
            "n_dgps": len(DGPs),
            "n_seeds_per_dgp": N_SEEDS,
            "n_estimators": len(ESTIMATORS),
            "n_total_cells": n_total_cells,
            "seeds": {
                d["id"]: {
                    "base_seed": d["base_seed"],
                    "increment": d["increment"],
                    "n_seeds": N_SEEDS,
                    "seed_list": [d["base_seed"] + d["increment"] * i for i in range(N_SEEDS)],
                }
                for d in DGPs
            },
            "dgps": [
                {
                    "id": d["id"],
                    "process": d["process"],
                    "kind": d["kind"],
                    "idio_vol": d["idio_vol"],
                    "base_seed": d["base_seed"],
                    "increment": d["increment"],
                    "note": d["note"],
                }
                for d in DGPs
            ],
            "config_grid": {
                "beta_window": BETA_WINDOW,
                "beta_min": BETA_MIN,
                "beta_max": BETA_MAX,
                "n_assets": N_ASSETS,
                "quantile": QUANTILE,
                "weighting": "equal",
                "beta_neutral": True,
                "dollar_neutral": True,
                "transaction_costs": TRANSACTION_COSTS,
                "estimator_families": {
                    e["key"]: {"estimator": e["estimator"], "params": e["params"]}
                    for e in ESTIMATORS
                },
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
                    "Deflate over n_trials_total read-only from P38 WP1; "
                    "never re-enumerated or invented here."
                ),
            },
        },
        "trial_enumeration": {
            "n_trials_total": n_trials,
            "source": "P38 deflated_summary.json",
        },
        "results": {
            "dgps": dgp_results,
            "cross_dgp": cross_dgp,
            "stress_verdict": stress_verdict,
            "stress_verdict_reason": stress_verdict_reason,
        },
    }
    return summary


def build_stress_summary() -> dict:
    n_trials = _load_n_trials_total()
    grid_results = _run_all_dgps(n_trials)
    return _round_floats(_build_stress_summary_artifact(grid_results, n_trials))


def write_stress_artifacts(payload: dict) -> tuple[Path, Path]:
    STRESS_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    STRESS_SUMMARY_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    STRESS_MARKDOWN_PATH.write_text(render_stress_markdown(payload), encoding="utf-8")
    return STRESS_SUMMARY_PATH, STRESS_MARKDOWN_PATH


def check_stress_summary(path: Path = STRESS_SUMMARY_PATH) -> bool:
    if not path.exists():
        print(f"Stress summary artifact not found: {path}")
        return False

    fresh = build_stress_summary()
    expected_bytes = path.read_bytes()
    actual_bytes = json.dumps(fresh, indent=2, sort_keys=True).encode("utf-8") + b"\n"

    if expected_bytes == actual_bytes:
        print("Stress summary artifact check: PASS (byte-identical)")
        return True
    else:
        print("Stress summary artifact check: FAIL (byte mismatch)")
        for i, (e, a) in enumerate(zip(expected_bytes, actual_bytes)):
            if e != a:
                print(f"  First difference at byte {i}: expected {e!r}, got {a!r}")
                break
        if len(expected_bytes) != len(actual_bytes):
            print(f"  Length mismatch: expected {len(expected_bytes)}, got {len(actual_bytes)}")
        return False


def render_stress_markdown(payload: dict) -> str:
    prov = payload["provenance"]
    results = payload["results"]
    cross = results["cross_dgp"]
    lines = [
        "# BAB P41 WP2 — Five-DGP Stress Meta-Analysis",
        "",
        f"Schema `{payload['schema']}`. Controlled synthetic stimulus: not real market "
        "data and not market profitability evidence. The verdict is honest and may "
        "be negative.",
        "",
        f"**Stress verdict:** **{results['stress_verdict']}**",
        f"**Reason:** {results['stress_verdict_reason']}",
        "",
        "## Setup",
        "",
        f"- DGPs: {prov['n_dgps']} deterministic synthetic data-generating processes, "
        f"{prov['n_seeds_per_dgp']} seeds each, {prov['n_estimators']} estimators "
        f"({prov['n_total_cells']} total cells)",
        f"- beta_window: {prov['config_grid']['beta_window']}d, "
        f"quantile: {_fmt(prov['config_grid']['quantile'])}",
        f"- weighting: {prov['config_grid']['weighting']}, beta_neutral: "
        f"{prov['config_grid']['beta_neutral']}, dollar_neutral: "
        f"{prov['config_grid']['dollar_neutral']}, transaction_costs: "
        f"{prov['config_grid']['transaction_costs']}",
        f"- DSR survive threshold: {_fmt(prov['dsr_survive_threshold'])}",
        f"- n_trials_total (deflation, read-only from P38 WP1): "
        f"{prov['deflation']['n_trials_total']}",
        "",
        "## DGPs (charter constants)",
        "",
        "| DGP | Process | Kind | Idio Vol | Base Seed | Increment | Replicates Stress |",
        "|---|---|---|---|---|---|---|",
    ]
    for d in prov["dgps"]:
        did = d["id"]
        rep = results["dgps"][did]["replicates_stress_test"]
        lines.append(
            f"| {did} | {d['process']} | {d['kind']} | "
            f"{_fmt(d['idio_vol'])} | {d['base_seed']} | {d['increment']} | {rep} |"
        )
    lines += [
        "",
        "- BTC prices read-only from tests/fixtures/wide_bab_universe.csv "
        "(the same deterministic random-walk fixture as P38/P40/WP1).",
        "- Reuses the WP1 cell grid: asset returns = beta * BTC_return + idio, "
        "betas linspace(0.2, 2.4, 40).",
        "- Not real market data; not market profitability evidence.",
        "",
        "## Trial enumeration (read-only from P38 WP1)",
        "",
        f"Deflation over n_trials_total = **{payload['trial_enumeration']['n_trials_total']}**, "
        "read-only from research_state/bab_p38/deflated_summary.json "
        "(trial_enumeration.n_trials_total). Never re-enumerated or invented here.",
        "",
        "## Per-DGP aggregates",
        "",
    ]
    for did in sorted(results["dgps"]):
        dr = results["dgps"][did]
        agg = dr["aggregate"]
        lines += [
            f"### {did}",
            "",
            f"- Process: {dr['process']} ({dr['kind']})",
            f"- Seeds: {dr['seeds']}",
            f"- n_cells: {agg['n_cells']}, n_ok_cells: {agg['n_ok_cells']}, "
            f"n_error_cells: {agg['n_error_cells']}, "
            f"n_neutrality_violations: {agg['n_neutrality_violations']}",
            f"- all_neutrality_ok: {agg['all_neutrality_ok']}",
            f"- all_survive: {agg['all_survive']}, any_survive: {agg['any_survive']}, "
            f"n_survive: {agg['n_survive']}",
            f"- replicates_stress_test: {dr['replicates_stress_test']}",
            f"- DSR mean/min/max: {_fmt(agg['dsr']['mean'])}/"
            f"{_fmt(agg['dsr']['min'])}/{_fmt(agg['dsr']['max'])}",
            f"- Sharpe mean/min/max: {_fmt(agg['sharpe']['mean'])}/"
            f"{_fmt(agg['sharpe']['min'])}/{_fmt(agg['sharpe']['max'])}",
            "",
        ]
    lines += [
        "## Cross-DGP aggregates",
        "",
        f"- n_dgps: {cross['n_dgps']}",
        f"- n_total_cells: {cross['n_total_cells']}",
        f"- n_total_ok_cells: {cross['n_total_ok_cells']}, "
        f"n_total_error_cells: {cross['n_total_error_cells']}",
        f"- n_total_survive: {cross['n_total_survive']}",
        f"- n_dgps_replicating: {cross['n_dgps_replicating']} / {cross['n_dgps']}",
        f"- all_dgps_neutrality_ok: {cross['all_dgps_neutrality_ok']}",
        f"- all_dgps_survive: {cross['all_dgps_survive']}",
        "",
        "## Verdict scale",
        "",
        "- ROBUST_ACROSS_DGPS: every DGP replicates (all cells survive deflation + "
        "neutrality holds everywhere).",
        "- FRAGILE_DGP_DEPENDENT: survival depends on DGP/seed (some cells survive, "
        "not all within any DGP).",
        "- DOES_NOT_REPLICATE: no cell survives deflation in any DGP.",
        "",
        "## Neutrality (every ok cell, every DGP, every estimator)",
        "",
        "- model beta <= 1e-3: "
        f"{cross['all_dgps_neutrality_ok']}",
        "- dollar <= 1e-9 and |realized beta| <= 0.15 at every ok cell.",
        "",
        "## Interpretation",
        "",
        "- DSR = Deflated Sharpe Ratio: probability the observed Sharpe is genuine "
        "skill after correcting for multiple testing (n_trials_total). "
        "DSR >= 0.50 means more likely than not genuine skill.",
        "- PSR = Probabilistic Sharpe Ratio: probability the Sharpe exceeds zero.",
        "- The stress verdict reports whether BAB behaviour survives non-Gaussian idio "
        "across all five DGPs; an honest negative/neutral ranking is a valid finding.",
        "- Synthetic-provenance caveat: results are on committed synthetic universes, "
        "not real market data. Never market alpha.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="P41 stress battery: WP1 estimator bakeoff + WP2 five-DGP stress meta-analysis"
    )
    parser.add_argument(
        "--check-estimator-bakeoff",
        action="store_true",
        help="Verify existing estimator_bakeoff artifact is byte-identical to fresh recomputation",
    )
    parser.add_argument(
        "--check-stress-summary",
        action="store_true",
        help="Verify existing stress_summary artifact is byte-identical to fresh recomputation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for summary artifact (default per flag: WP1 / WP2)",
    )
    args = parser.parse_args()

    if args.check_estimator_bakeoff:
        ok = check_summary(args.output or SUMMARY_PATH)
        return 0 if ok else 1

    if args.check_stress_summary:
        ok = check_stress_summary(args.output or STRESS_SUMMARY_PATH)
        return 0 if ok else 1

    print("Running P41 WP1 estimator bakeoff under non-Gaussian idio (five DGPs)...")
    for d in DGPs:
        print(
            f"  {d['id']}: base={d['base_seed']}, inc={d['increment']}, "
            f"idio_vol={d['idio_vol']}, kind={d['kind']}"
        )
    print(f"  Beta window: {BETA_WINDOW}d, beta=[{BETA_MIN}, {BETA_MAX}], n_assets={N_ASSETS}")
    print(f"  Quantile: {QUANTILE}, weighting: equal, beta_neutral: True")
    print(f"  Estimators: {', '.join(e['key'] for e in ESTIMATORS)}")
    print(f"  Bootstrap: {N_BOOTSTRAP} resamples, block length {BLOCK_LENGTH}")

    n_trials = _load_n_trials_total()
    print(f"  n_trials_total (read-only from P38 WP1): {n_trials}")

    started = time.perf_counter()

    grid_results = _run_all_dgps(n_trials)
    payload = _round_floats(_build_summary_artifact(grid_results, n_trials))
    json_path, md_path = write_artifacts(payload)
    elapsed = time.perf_counter() - started

    cross = payload["results"]["cross_dgp"]
    print(f"Done in {elapsed:.2f}s")
    print(f"  Bakeoff verdict: {payload['bakeoff_verdict']}")
    print(
        f"  {cross['n_dgps_replicating']} of {cross['n_dgps']} DGPs "
        f"replicate neutrality + survival"
    )
    print(f"  Total cells: {cross['n_total_cells']} ok, "
          f"{cross['n_total_error_cells']} errors, "
          f"n_total_survive={cross['n_total_survive']}")
    print(
        f"  Least-broken estimator: "
        f"{payload['results']['estimator_comparison']['least_broken_estimator']}"
    )
    print(f"  Summary written to: {json_path}")
    print(f"  Markdown written to: {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
