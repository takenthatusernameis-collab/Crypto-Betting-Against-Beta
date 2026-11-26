#!/usr/bin/env python3
"""P40 — Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict.

Deterministic, offline runner that generalizes the single-fixture P39 WP2
cross-fixture pipeline (scripts/bab_p39_cross_fixture.py) to FOUR fixed
deterministic synthetic fixtures (8 seeds each; 32 total cells):

    Fixture grid:
      F1_PRIMARY        base 20261120 inc 1009 idio 0.003 beta 0.35-1.90 40 assets
      F2_P39_SECOND     base 20270101 inc 9973 idio 0.006 beta 0.20-2.40 32 assets
      F3_LOW_VOL_WIDE   base 20280201 inc 10009 idio 0.002 beta 0.25-2.10 36 assets
      F4_HIGH_VOL_NARROW base 20290301 inc 10007 idio 0.008 beta 0.40-1.70 28 assets

    Roles: F1 = P38/P39 WP1 primary parameterization; F2 = P39 WP2 second;
    F3 = low-idio wider beta cross-section; F4 = high-idio narrow cross-section.

For every cell it recomputes deflated significance (DSR/PSR deflated over the
read-only n_trials_total=552 from P38 WP1), tail risk, and the three
neutrality invariants on the shipped-default BAB config
(beta_window=90, quantile=0.3, equal-weight, beta-neutral, dollar-neutral,
zero transaction costs), then aggregates per fixture and across fixtures and
emits exactly one consolidated verdict:

    ROBUST_ACROSS_FIXTURES      all four fixtures replicate the P38 pooled verdict
    FRAGILE_FIXTURE_DEPENDENT   at least one but fewer than four replicate
    DOES_NOT_REPLICATE          no fixture replicates

A fixture "replicates" the P38 pooled verdict (SURVIVES_DEFLATION +
ALL_NEUTRALITY_OK) when every cell is status ok, neutrality holds at every
cell, and every cell survives deflation (DSR >= 0.50).

Publishes research_state/bab_p40/meta_summary.json (+ .md sidecar).
Emits --check-meta-summary for byte-diff verification.
All data is deterministic synthetic; not real market data. The verdict is
honest — it may be negative.
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

# --- Fixed P40 fixture grid (do not tune after seeing results) ---
FIXTURES = [
    {
        "id": "F1_PRIMARY",
        "base_seed": 20261120,
        "increment": 1009,
        "idio_vol": 0.003,
        "beta_min": 0.35,
        "beta_max": 1.90,
        "n_assets": 40,
        "role": "P38/P39 WP1 primary parameterization",
    },
    {
        "id": "F2_P39_SECOND",
        "base_seed": 20270101,
        "increment": 9973,
        "idio_vol": 0.006,
        "beta_min": 0.20,
        "beta_max": 2.40,
        "n_assets": 32,
        "role": "P39 WP2 second parameterization",
    },
    {
        "id": "F3_LOW_VOL_WIDE",
        "base_seed": 20280201,
        "increment": 10009,
        "idio_vol": 0.002,
        "beta_min": 0.25,
        "beta_max": 2.10,
        "n_assets": 36,
        "role": "Low-idio, wider beta cross-section",
    },
    {
        "id": "F4_HIGH_VOL_NARROW",
        "base_seed": 20290301,
        "increment": 10007,
        "idio_vol": 0.008,
        "beta_min": 0.40,
        "beta_max": 1.70,
        "n_assets": 28,
        "role": "High-idio, narrower beta cross-section",
    },
]

N_SEEDS = 8
FIXTURE_PATH = _REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"

BETA_WINDOW = 90
QUANTILE = 0.3

# Neutrality tolerances (per HANDOFF.md P34/P36/P37/P38/P39)
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

WEIGHT_THRESHOLD = 1e-10

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

SCHEMA_VERSION = "bab_p40.meta_analysis/1"
SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p40" / "meta_summary.json"
MARKDOWN_PATH = _REPO_ROOT / "research_state" / "bab_p40" / "meta_summary.md"

TAIL_LEVELS = (95.0, 99.0)
ES_LEVEL = 975.0

# --- Universe / reference ---


def _load_btc_prices() -> pd.Series:
    df = pd.read_csv(FIXTURE_PATH, index_col="date", parse_dates=True)
    df.index = pd.DatetimeIndex(df.index)
    if "BTC" not in df.columns:
        raise ValueError(f"wide universe fixture missing BTC column: {list(df.columns)}")
    return df["BTC"].astype(float)


def _build_wide_universe_for_seed(
    seed: int, idio_vol: float, beta_min: float, beta_max: float, n_assets: int
) -> pd.DataFrame:
    """Build synthetic wide universe: asset returns = beta * BTC_return + seeded idio.

    BTC prices are loaded read-only from tests/fixtures/wide_bab_universe.csv.
    Not real market data; not market profitability evidence.
    """
    btc_prices = _load_btc_prices()
    btc_returns = btc_prices.pct_change().iloc[1:]
    btc_return_dates = btc_returns.index

    rng = np.random.default_rng(seed)
    betas = np.linspace(beta_min, beta_max, n_assets)

    n_returns = len(btc_return_dates)
    idio = rng.normal(loc=0.0, scale=idio_vol, size=(n_assets, n_returns))

    asset_returns = np.vstack([
        beta * btc_returns.to_numpy(dtype=float) + idio[i]
        for i, beta in enumerate(betas)
    ])

    asset_columns = [f"A{i:03d}" for i in range(1, n_assets + 1)]
    returns_df = pd.DataFrame(
        asset_returns.T,
        index=btc_return_dates,
        columns=asset_columns,
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


# --- Neutrality invariants ---


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


# --- Per-seed cell runner (pooled; no regime split — mirrors P38 deflated + tail) ---


def _run_seed_cell(
    returns_df: pd.DataFrame,
    seed: int,
    seed_idx: int,
    asset_columns: list[str],
    n_trials: int,
) -> dict:
    """Run one seed cell: deflated significance + tail risk + neutrality."""
    betas = estimate_rolling_ols_beta(
        returns_df, "BTC", window=BETA_WINDOW, min_obs=min(60, BETA_WINDOW)
    )

    valid_betas = betas.dropna(how="all", subset=asset_columns)
    if len(valid_betas) == 0:
        return {
            "cell_key": f"seed_{seed_idx}",
            "seed_index": seed_idx,
            "seed": seed,
            "status": "error",
            "error": "no valid beta estimates",
        }

    valid_returns = returns_df.loc[valid_betas.index]
    valid_betas_aligned = valid_betas[[*asset_columns, "BTC"]]

    weights = _base_weights(valid_returns, valid_betas_aligned, QUANTILE)
    strat_returns = _compute_strat_returns(weights, valid_returns, transaction_costs=0.0)
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

    status = "ok" if (model_beta_ok and dollar_ok and realized_ok) else "neutrality_violation"

    return {
        "cell_key": f"seed_{seed_idx}",
        "seed_index": seed_idx,
        "seed": seed,
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


def _run_all_seeds(fixture: dict, n_trials: int) -> dict:
    cells = []
    for seed_idx in range(N_SEEDS):
        seed = fixture["base_seed"] + fixture["increment"] * seed_idx
        returns_df = _build_wide_universe_for_seed(
            seed,
            fixture["idio_vol"],
            fixture["beta_min"],
            fixture["beta_max"],
            fixture["n_assets"],
        )
        asset_columns = [f"A{i:03d}" for i in range(1, fixture["n_assets"] + 1)]
        try:
            cells.append(
                _run_seed_cell(returns_df, seed, seed_idx, asset_columns, n_trials)
            )
        except Exception as exc:  # pragma: no cover - defensive
            cells.append({
                "cell_key": f"seed_{seed_idx}",
                "seed_index": seed_idx,
                "seed": seed,
                "status": "error",
                "error": str(exc),
            })
    return {"cells": cells}


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
    return {
        "n_cells": len(cells),
        "n_ok_cells": len(ok),
        "n_error_cells": sum(1 for c in cells if c.get("status") == "error"),
        "n_neutrality_violations": sum(
            1 for c in cells if c.get("status") == "neutrality_violation"
        ),
        "all_neutrality_ok": all(
            c.get("status") == "ok" for c in cells
        ),
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


def _fixture_replicates(agg: dict) -> bool:
    """A fixture replicates the P38 pooled verdict (SURVIVES_DEFLATION +
    ALL_NEUTRALITY_OK) when every cell is ok, neutrality holds everywhere,
    and every cell survives deflation."""
    return bool(
        agg["all_neutrality_ok"]
        and agg["all_survive"]
        and agg["n_error_cells"] == 0
        and agg["n_ok_cells"] > 0
    )


# --- Summary artifact ---


def _load_n_trials_total() -> int:
    """Read-only: n_trials_total from the committed P38 deflated summary."""
    payload = json.loads(P38_DEFLATED_PATH.read_text(encoding="utf-8"))
    return int(payload["trial_enumeration"]["n_trials_total"])


def _build_summary_artifact(fixture_results: dict, n_trials: int) -> dict:
    btc_prices = _load_btc_prices()
    btc_sha256 = hashlib.sha256(btc_prices.to_numpy(dtype=float).tobytes()).hexdigest()

    fixture_entries = []
    for fid, fr in fixture_results.items():
        fixture_cfg = next(f for f in FIXTURES if f["id"] == fid)
        base_returns = _build_wide_universe_for_seed(
            fixture_cfg["base_seed"],
            fixture_cfg["idio_vol"],
            fixture_cfg["beta_min"],
            fixture_cfg["beta_max"],
            fixture_cfg["n_assets"],
        )
        returns_sha256 = hashlib.sha256(
            base_returns.to_csv(date_format="%Y-%m-%d").encode("utf-8")
        ).hexdigest()
        agg = _aggregate(fr["cells"])
        replicate = _fixture_replicates(agg)
        fixture_entries.append({
            "id": fid,
            "role": fixture_cfg["role"],
            "provenance": {
                "base_seed": fixture_cfg["base_seed"],
                "increment": fixture_cfg["increment"],
                "n_seeds": N_SEEDS,
                "seed_list": [
                    fixture_cfg["base_seed"] + fixture_cfg["increment"] * i
                    for i in range(N_SEEDS)
                ],
                "idio_vol": fixture_cfg["idio_vol"],
                "beta_min": fixture_cfg["beta_min"],
                "beta_max": fixture_cfg["beta_max"],
                "n_assets": fixture_cfg["n_assets"],
                "returns_sha256": returns_sha256,
                "fixture_path": str(FIXTURE_PATH),
            },
            "results": {
                "cells": fr["cells"],
                "aggregate": agg,
            },
            "replicates_p38_pooled_verdict": replicate,
        })

    cross_fixture = _aggregate(
        [c for fr in fixture_results.values() for c in fr["cells"]]
    )
    n_replicate = sum(
        1 for e in fixture_entries if e["replicates_p38_pooled_verdict"]
    )

    if n_replicate == len(fixture_entries):
        campaign_verdict = "ROBUST_ACROSS_FIXTURES"
    elif n_replicate > 0:
        campaign_verdict = "FRAGILE_FIXTURE_DEPENDENT"
    else:
        campaign_verdict = "DOES_NOT_REPLICATE"

    summary = {
        "schema": SCHEMA_VERSION,
        "provenance": {
            "generator": "scripts/bab_p40_meta_analysis.py",
            "campaign": "P40 Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict",
            "wp": "WP0 - Deterministic meta-analysis generator (four fixtures, 32 cells)",
            "synthetic": True,
            "note": (
                "Four deterministic synthetic wide universes built from the same "
                "read-only BTC price fixture (tests/fixtures/wide_bab_universe.csv). "
                "Asset returns = beta * BTC_return + seeded idiosyncratic noise. "
                "Not real market data; not market profitability evidence. Pooled "
                "per-seed cells (no regime split): deflated significance "
                "(DSR/PSR over n_trials_total read-only from P38 WP1) plus tail risk "
                "(CVaR/expected shortfall/drawdown/skew/kurtosis) and neutrality "
                "invariants. Campaign verdict reports whether the P38 pooled verdict "
                "(SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) replicates across fixtures."
            ),
            "fixtures": [
                {
                    "id": e["id"],
                    "role": e["role"],
                    "config": {
                        "base_seed": e["provenance"]["base_seed"],
                        "increment": e["provenance"]["increment"],
                        "n_seeds": e["provenance"]["n_seeds"],
                        "seed_list": e["provenance"]["seed_list"],
                        "idio_vol": e["provenance"]["idio_vol"],
                        "beta_min": e["provenance"]["beta_min"],
                        "beta_max": e["provenance"]["beta_max"],
                        "n_assets": e["provenance"]["n_assets"],
                    },
                    "returns_sha256": e["provenance"]["returns_sha256"],
                    "replicates_p38_pooled_verdict": e["replicates_p38_pooled_verdict"],
                }
                for e in fixture_entries
            ],
            "btc_source_sha256": btc_sha256,
            "config_grid": {
                "beta_window": BETA_WINDOW,
                "quantile": QUANTILE,
                "weighting": "equal",
                "beta_neutral": True,
                "dollar_neutral": True,
                "transaction_costs": 0.0,
                "n_seeds_per_fixture": N_SEEDS,
                "n_fixtures": len(FIXTURES),
                "n_cells_total": len(FIXTURES) * N_SEEDS,
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
            "fixtures": {e["id"]: e["results"] for e in fixture_entries},
            "cross_fixture": cross_fixture,
        },
        "campaign_verdict": campaign_verdict,
        "campaign_verdict_reason": (
            f"{n_replicate} of {len(fixture_entries)} fixtures replicate the P38 pooled "
            f"verdict (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) after deflation over "
            f"n_trials_total={n_trials}; consolidated verdict {campaign_verdict}."
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
    fixture_results = {}
    for fixture in FIXTURES:
        fixture_results[fixture["id"]] = _run_all_seeds(fixture, n_trials)
    return _round_floats(_build_summary_artifact(fixture_results, n_trials))


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


def render_markdown(payload: dict) -> str:
    prov = payload["provenance"]
    results = payload["results"]
    cross = results["cross_fixture"]
    lines = [
        "# BAB P40 — Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict",
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
        f"- Fixtures: {prov['config_grid']['n_fixtures']} deterministic synthetic "
        "wide universes, "
        f"{prov['config_grid']['n_seeds_per_fixture']} seeds each, "
        f"{prov['config_grid']['n_cells_total']} cells total",
        f"- beta_window: {prov['config_grid']['beta_window']}d, quantile: "
        f"{_fmt(prov['config_grid']['quantile'])}",
        f"- weighting: {prov['config_grid']['weighting']}, beta_neutral: "
        f"{prov['config_grid']['beta_neutral']}, dollar_neutral: "
        f"{prov['config_grid']['dollar_neutral']}, transaction_costs: "
        f"{_fmt(prov['config_grid']['transaction_costs'])}",
        f"- DSR survive threshold: {_fmt(prov['dsr_survive_threshold'])} "
        "(DSR >= 0.50 means more likely than not genuine skill after deflation)",
        f"- Bootstrap: {prov['bootstrap']['n_resamples']} resamples, block length "
        f"{prov['bootstrap']['block_length']}, seed {prov['bootstrap']['seed']}",
        "",
        "## Trial enumeration (read-only from P38 WP1)",
        "",
        f"Deflation over n_trials_total = **{payload['trial_enumeration']['n_trials_total']}**, "
        "read-only from research_state/bab_p38/deflated_summary.json "
        "(trial_enumeration.n_trials_total). Never re-enumerated or invented here.",
        "",
        "## Fixture grid (fixed; not tuned)",
        "",
        "| Fixture | Base seed | Incr | Idio vol | Beta range | Assets | Replicates | Role |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for entry in prov["fixtures"]:
        cfg = entry["config"]
        lines.append(
            f"| {entry['id']} | {cfg['base_seed']} | {cfg['increment']} | "
            f"{_fmt(cfg['idio_vol'])} | [{_fmt(cfg['beta_min'])}, "
            f"{_fmt(cfg['beta_max'])}] | {cfg['n_assets']} | "
            f"{entry['replicates_p38_pooled_verdict']} | {entry['role']} |"
        )
    lines += [
        "",
        "- BTC prices read-only from tests/fixtures/wide_bab_universe.csv "
        "(the same deterministic random-walk fixture as P38/P39).",
        "- Asset returns = beta * BTC_return + idio, seeded per fixture; "
        "neutrality invariants (model beta <= 1e-3, dollar <= 1e-9, "
        "|realized beta| <= 0.15) checked at every cell.",
        "- Not real market data; not market profitability evidence.",
        "",
        "## Per-cell results (pooled; no regime split)",
        "",
        "| Fixture | Seed | N periods | Sharpe | DSR | PSR | Survives | Verdict | Neutrality |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for fid in [f["id"] for f in FIXTURES]:
        cells = results["fixtures"][fid]["cells"]
        for cell in cells:
            neu = cell.get("neutrality", {})
            neu_ok = (
                neu.get("model_beta_neutral", {}).get("passed", False)
                and neu.get("dollar_neutral", {}).get("passed", False)
                and neu.get("realized_beta_check", {}).get("passed", False)
            )
            lines.append(
                f"| {fid} | {cell.get('seed')} | {cell.get('n_periods')} | "
                f"{_fmt(cell.get('sharpe'))} | {_fmt(cell.get('dsr'))} | "
                f"{_fmt(cell.get('psr'))} | {cell.get('survives_deflation')} | "
                f"{cell.get('verdict')} | {neu_ok} |"
            )
    lines += [
        "",
        "## Per-fixture aggregates",
        "",
        "| Fixture | Cells | Ok | Errors | All neu | Survive | DSR mean | DSR min | DSR max |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for fid in [f["id"] for f in FIXTURES]:
        entry = next(e for e in prov["fixtures"] if e["id"] == fid)
        agg = results["fixtures"][fid]["aggregate"]
        lines.append(
            f"| {fid} | {agg['n_cells']} | {agg['n_ok_cells']} | "
            f"{agg['n_error_cells']} | {agg['n_neutrality_violations']} | "
            f"{agg['all_neutrality_ok']} | {agg['all_survive']} | "
            f"{agg['n_survive']} | {_fmt(agg['dsr']['mean'])} | "
            f"{_fmt(agg['dsr']['min'])} | {_fmt(agg['dsr']['max'])} |"
        )
    lines += [
        "",
        "## Cross-fixture aggregate (all 32 cells)",
        "",
        f"- n_cells: {cross['n_cells']}, n_ok_cells: {cross['n_ok_cells']}, "
        f"n_error_cells: {cross['n_error_cells']}, "
        f"n_neutrality_violations: {cross['n_neutrality_violations']}",
        f"- all_neutrality_ok: {cross['all_neutrality_ok']}",
        f"- all_survive: {cross['all_survive']}, any_survive: {cross['any_survive']}, "
        f"n_survive: {cross['n_survive']}",
        f"- DSR mean/min/max: {_fmt(cross['dsr']['mean'])}/"
        f"{_fmt(cross['dsr']['min'])}/{_fmt(cross['dsr']['max'])}",
        f"- PSR mean/min/max: {_fmt(cross['psr']['mean'])}/"
        f"{_fmt(cross['psr']['min'])}/{_fmt(cross['psr']['max'])}",
        f"- Sharpe mean/min/max: {_fmt(cross['sharpe']['mean'])}/"
        f"{_fmt(cross['sharpe']['min'])}/{_fmt(cross['sharpe']['max'])}",
        f"- Fixtures replicating P38 pooled verdict: "
        f"{sum(1 for e in prov['fixtures'] if e['replicates_p38_pooled_verdict'])} "
        f"of {len(prov['fixtures'])}",
        "",
        "## Neutrality (every cell)",
        "",
        f"- model beta <= {MODEL_BETA_NEUTRAL_TOL}: "
        f"{cross['neutrality']['all_model_beta_ok']}",
        f"- dollar <= {DOLLAR_NEUTRAL_TOL}: {cross['neutrality']['all_dollar_ok']}",
        f"- |realized beta| <= {REALIZED_BETA_TOL}: {cross['neutrality']['all_realized_ok']}",
        "",
        "## Interpretation",
        "",
        "- DSR = Deflated Sharpe Ratio: probability the observed Sharpe is genuine "
        "skill after correcting for the multiple trials searched (n_trials_total). "
        "DSR >= 0.50 means more likely than not genuine skill.",
        "- PSR = Probabilistic Sharpe Ratio: probability the Sharpe exceeds zero "
        "(analytical, Bailey & Lopez de Prado).",
        "- A fixture replicates the P38 pooled verdict (SURVIVES_DEFLATION + "
        "ALL_NEUTRALITY_OK) when every cell is status ok, neutrality holds at every "
        "cell, and every cell survives deflation.",
        "- Consolidated verdict: ROBUST_ACROSS_FIXTURES (all four replicate), "
        "FRAGILE_FIXTURE_DEPENDENT (one to three replicate), or DOES_NOT_REPLICATE "
        "(none replicate).",
        "- This is a multi-fixture robustness test, not an in-sample fit: if the "
        "P38 pooled verdict holds on all four independently parameterized synthetic "
        "universes, the result is a property of the factor; if it holds on some, the "
        "verdict is fixture-dependent; if on none, the P38 verdict does not replicate.",
        "- Synthetic-provenance caveat: results are on committed synthetic universes "
        "(BTC prices + seeded idiosyncratic noise), not real market data. "
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
        description="P40 multi-fixture robustness meta-analysis"
    )
    parser.add_argument(
        "--check-meta-summary",
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

    if args.check_meta_summary:
        ok = check_summary(args.output)
        return 0 if ok else 1

    print("Running P40 multi-fixture robustness meta-analysis...")
    print(f"  Fixtures: {len(FIXTURES)} x {N_SEEDS} seeds = {len(FIXTURES) * N_SEEDS} cells")
    print(f"  Beta window: {BETA_WINDOW}d, quantile: {QUANTILE}")
    print(f"  Bootstrap: {N_BOOTSTRAP} resamples, block length {BLOCK_LENGTH}")

    n_trials = _load_n_trials_total()
    print(f"  n_trials_total (read-only from P38 WP1): {n_trials}")

    started = time.perf_counter()

    payload = build_summary()
    json_path, md_path = write_artifacts(payload)
    elapsed = time.perf_counter() - started

    cross = payload["results"]["cross_fixture"]
    n_replicate = sum(
        1 for e in payload["provenance"]["fixtures"]
        if e["replicates_p38_pooled_verdict"]
    )
    print(f"Done in {elapsed:.2f}s")
    print(f"  Campaign verdict: {payload['campaign_verdict']}")
    print(f"  Fixtures replicating P38 pooled verdict: {n_replicate} of {len(FIXTURES)}")
    print(
        f"  Cells: {cross['n_cells']} total, {cross['n_ok_cells']} ok, "
        f"{cross['n_error_cells']} errors, "
        f"{cross['n_neutrality_violations']} neutrality violations"
    )
    print(f"  all_neutrality_ok={cross['all_neutrality_ok']}, "
          f"all_survive={cross['all_survive']}, n_survive={cross['n_survive']}")
    print(f"  DSR mean={cross['dsr']['mean']}, PSR mean={cross['psr']['mean']}")
    print(f"  Summary written to: {json_path}")
    print(f"  Markdown written to: {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
