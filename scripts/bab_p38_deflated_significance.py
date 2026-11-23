#!/usr/bin/env python3
"""P38 WP1 — Deflated / multiple-testing-adjusted significance over the full search.

Deterministic, offline runner that:

  1. Enumerates the total effective number of trials (n_trials_total) searched
      across the campaign lineage (P20 grid + P21-P37 variant cells + P36 folds),
     derived read-only from committed artifacts — never invented.
  2. Runs the shipped default (weighting="equal", beta_neutral=True,
     beta_window=90) and the best in-sample config (highest-Sharpe row of the
     committed P20 sweep) on the P35/P37 wide synthetic fixture (40 assets,
     8 seeds).
  3. Computes DSR + PSR for both configs against n_trials_total, plus the
     trials-adjusted p-value and the minimum-backtest-length implication.
  4. Publishes research_state/bab_p38/deflated_summary.json (+ .md sidecar).

The honest verdict string is mandatory and may be negative:
SURVIVES_DEFLATION or DOES_NOT_SURVIVE_DEFLATION. Every number traces to a
committed JSON leaf; synthetic-provenance caveat required.

Emits --check-deflated-summary for byte-diff verification.
All data is deterministic synthetic; not real market data.
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

# --- Constants matching the P35/P36/P37 wide universe recipe ---
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

# Neutrality tolerances (per HANDOFF.md P36/P37)
MODEL_BETA_NEUTRAL_TOL = 1e-3
DOLLAR_NEUTRAL_TOL = 1e-9
REALIZED_BETA_TOL = 0.15

WEIGHT_THRESHOLD = 1e-10

# Bootstrap settings for sigma0 (std of Sharpe under the null), mirroring P21.
N_BOOTSTRAP = 2000
BLOCK_LENGTH = 20
BOOTSTRAP_SEED = 20261123

# DSR verdict threshold: DSR >= 0.50 means more likely than not genuine skill
# after multiple-testing deflation.
DSR_SURVIVE_THRESHOLD = 0.50

SCHEMA_VERSION = "bab_p38.deflated_significance/1"
SUMMARY_PATH = _REPO_ROOT / "research_state" / "bab_p38" / "deflated_summary.json"
MARKDOWN_PATH = _REPO_ROOT / "research_state" / "bab_p38" / "deflated_summary.md"

# Committed artifact paths (read-only) used for trial enumeration.
P20_SWEEP_PATH = _REPO_ROOT / "research_state" / "bab_p20" / "sweep.json"
TRIAL_ARTIFACTS = [
    _REPO_ROOT / "research_state" / "bab_p25" / "promotion_bakeoff.json",
    _REPO_ROOT / "research_state" / "bab_p25" / "walk_forward_rank.json",
    _REPO_ROOT / "research_state" / "bab_p26" / "signal_null_battery.json",
    _REPO_ROOT / "research_state" / "bab_p26" / "regime_stress.json",
    _REPO_ROOT / "research_state" / "bab_p26" / "rank_capacity.json",
    _REPO_ROOT / "research_state" / "bab_p35" / "estimator_bakeoff_summary.json",
    _REPO_ROOT / "research_state" / "bab_p35" / "signal_stability_summary.json",
    _REPO_ROOT / "research_state" / "bab_p36" / "walk_forward_summary.json",
    _REPO_ROOT / "research_state" / "bab_p36" / "rank_weighted_summary.json",
    _REPO_ROOT / "research_state" / "bab_p37" / "cost_surface_summary.json",
    _REPO_ROOT / "research_state" / "bab_p37" / "capacity_summary.json",
    _REPO_ROOT / "research_state" / "bab_p37" / "turnover_summary.json",
]


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


# --- Strategy pipeline ---


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


# --- Per-config per-seed runner ---


def _run_config_for_seed(
    returns_df: pd.DataFrame,
    seed: int,
    seed_idx: int,
    beta_window: int,
    quantile: float,
    transaction_costs: float,
) -> dict:
    betas = estimate_rolling_ols_beta(
        returns_df, "BTC", window=beta_window, min_obs=min(60, beta_window)
    )

    valid_betas = betas.dropna(how="all", subset=ASSET_COLUMNS)
    if len(valid_betas) == 0:
        return {
            "cell_key": f"seed_{seed_idx}",
            "seed_index": seed_idx,
            "seed": seed,
            "status": "error",
            "error": "no valid beta estimates",
        }

    valid_returns = returns_df.loc[valid_betas.index]
    valid_betas_aligned = valid_betas[[*ASSET_COLUMNS, "BTC"]]

    weights = _base_weights(valid_returns, valid_betas_aligned, quantile)
    strat_returns = _compute_strat_returns(weights, valid_returns, transaction_costs)
    bench_returns = valid_returns["BTC"]

    sr = sharpe_ratio(strat_returns)
    ann_vol = annualized_volatility(strat_returns)
    max_dd = max_drawdown(strat_returns)
    tr = total_return(strat_returns)
    turn = turnover(weights)
    realized_beta = strategy_beta(strat_returns, bench_returns)
    wealth = final_cumulative(strat_returns)

    strat_returns_list = [float(x) for x in strat_returns.to_numpy(dtype=float)]

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
        "realized_beta": round(float(realized_beta), 12) if np.isfinite(realized_beta) else None,
        "neutrality_ok": (
            realized_beta is not None
            and np.isfinite(realized_beta)
            and abs(realized_beta) <= REALIZED_BETA_TOL
        ),
        "strat_returns": strat_returns_list,
        "status": "ok",
    }


def _run_config_all_seeds(
    beta_window: int, quantile: float, transaction_costs: float
) -> dict:
    all_cells = []
    for seed_idx in range(N_SEEDS):
        seed = SEED_BASE + SEED_INCREMENT * seed_idx
        returns_df = _build_wide_universe_for_seed(seed)
        try:
            cell = _run_config_for_seed(
                returns_df, seed, seed_idx, beta_window, quantile, transaction_costs
            )
            all_cells.append(cell)
        except Exception as e:
            all_cells.append({
                "cell_key": f"seed_{seed_idx}",
                "seed_index": seed_idx,
                "seed": seed,
                "status": "error",
                "error": str(e),
            })
    return {"cells": all_cells, "beta_window": beta_window, "quantile": quantile}


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


def _significance_for_config(
    cells: list[dict], n_trials: int, beta_window: int, quantile: float
) -> dict:
    """Compute DSR + PSR for one config across its seed cells.

    Pools the per-seed strategy returns, estimates skewness/kurtosis from the
    pooled returns, and derives sigma0 (SE of Sharpe under the null) from a
    fixed-seed moving-block bootstrap of the centred pooled returns — mirroring
    the P21 methodology.
    """
    ok_cells = [c for c in cells if c["status"] == "ok"]
    if not ok_cells:
        return {
            "beta_window": beta_window,
            "quantile": quantile,
            "n_seed_cells": len(cells),
            "n_ok_cells": 0,
            "status": "no_ok_cells",
        }

    sharpes = [c["sharpe"] for c in ok_cells if c["sharpe"] is not None]
    mean_sharpe = float(np.mean(sharpes)) if sharpes else None
    total_periods = sum(c["n_periods"] for c in ok_cells)

    # Pool the per-seed strategy returns into one series for moment estimation
    # and the centred bootstrap that yields sigma0.
    pooled = np.concatenate(
        [np.array(c["strat_returns"], dtype=float) for c in ok_cells if "strat_returns" in c]
    )
    if len(pooled) < 2:
        return {
            "beta_window": beta_window,
            "quantile": quantile,
            "n_seed_cells": len(cells),
            "n_ok_cells": len(ok_cells),
            "status": "insufficient_returns",
        }

    gamma, kappa = _sample_moments(pooled)

    # sigma0: SE of Sharpe under the null, from centred moving-block bootstrap.
    boot_centred = _moving_block_bootstrap(
        pooled, N_BOOTSTRAP, BLOCK_LENGTH, BOOTSTRAP_SEED, center=True
    )
    sigma0 = float(np.std(boot_centred, ddof=1))
    if not np.isfinite(sigma0) or sigma0 <= 0.0:
        # Fallback to the analytical SE of Sharpe if bootstrap degenerates.
        se_sr_sq = (
            1.0 + 0.5 * gamma * mean_sharpe ** 2 + 0.25 * (kappa - 1.0) * mean_sharpe ** 4
        ) / max(total_periods - 1, 1)
        sigma0 = math.sqrt(max(se_sr_sq, 1e-18))

    sr_obs = mean_sharpe if mean_sharpe is not None else 0.0

    dsr = _deflated_sharpe(sr_obs, 0.0, n_trials, sigma0, gamma, kappa)
    psr = _probabilistic_sharpe(sr_obs, gamma, kappa, total_periods, sr_bench=0.0)

    # Trials-adjusted p-value: 1 - DSR (probability the observed Sharpe is
    # noise given n_trials).
    trials_adjusted_p = 1.0 - dsr

    # Minimum backtest length: T such that PSR >= 0.50 given the observed SR.
    # PSR(T) = 0.50 iff SE(SR) = |SR| (the PSR=0.50 boundary). Solve:
    #   (1 + 0.5*gamma*SR^2 + 0.25*(kappa-1)*SR^4) / (T-1) = SR^2
    t_min = None
    if sr_obs != 0.0:
        numerator = (
            1.0 + 0.5 * gamma * sr_obs ** 2 + 0.25 * (kappa - 1.0) * sr_obs ** 4
        )
        if numerator > 0:
            t_min = math.ceil(numerator / sr_obs ** 2) + 1

    survives = bool(dsr >= DSR_SURVIVE_THRESHOLD)

    return {
        "beta_window": beta_window,
        "quantile": quantile,
        "n_seed_cells": len(cells),
        "n_ok_cells": len(ok_cells),
        "mean_sharpe": round(float(sr_obs), 6) if sr_obs is not None else None,
        "total_periods": total_periods,
        "n_trials": n_trials,
        "sigma0": round(float(sigma0), 10),
        "gamma": round(float(gamma), 6),
        "kappa": round(float(kappa), 6),
        "dsr": round(float(dsr), 6),
        "psr": round(float(psr), 6),
        "trials_adjusted_p_value": round(float(trials_adjusted_p), 6),
        "min_backtest_length_for_psr_0_50": t_min,
        "survives_deflation": survives,
        "verdict": "SURVIVES_DEFLATION" if survives else "DOES_NOT_SURVIVE_DEFLATION",
        "status": "ok",
    }


# --- Trial enumeration (read-only from committed artifacts) ---


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _count_cells(payload: dict) -> int:
    results = payload.get("results", {})
    cells = results.get("cells", [])
    return len(cells)


def _count_cost_surface_trials(payload: dict) -> int:
    """Cost surface: each seed cell has turnover x cost sub-cells."""
    total = 0
    for cell in payload.get("results", {}).get("cells", []):
        n_turnover = len(cell.get("cells", []))
        n_cost = 0
        for tc in cell.get("cells", []):
            n_cost = max(n_cost, len(tc.get("cost_rows", [])))
        total += n_turnover * n_cost
    return total


def enumerate_n_trials_total() -> dict:
    """Derive n_trials_total read-only from committed artifacts.

    Returns a dict with the per-campaign breakdown and the total.
    """
    breakdown: dict[str, int] = {}

    # P20: the in-sample grid (grid.configurations = 80).
    p20 = _load_json(P20_SWEEP_PATH)
    n_p20 = int(p20.get("grid", {}).get("configurations", 0))
    breakdown["P20_in_sample_grid"] = n_p20

    # P21-P37 variant cells from committed artifacts (read-only).
    for path in TRIAL_ARTIFACTS:
        label = path.parent.name + "/" + path.stem
        payload = _load_json(path)
        if "cost_surface" in path.name:
            breakdown[label] = _count_cost_surface_trials(payload)
        else:
            breakdown[label] = _count_cells(payload)

    n_trials_total = sum(breakdown.values())
    return {
        "n_trials_total": n_trials_total,
        "breakdown": breakdown,
        "note": (
            "Derived read-only from committed P20-P37 artifacts: P20 grid "
            "configurations plus distinct config cells evaluated across P25-P37 "
            "variant artifacts. Not invented; each term traces to a committed "
            "JSON leaf."
        ),
    }


# --- Best in-sample config from P20 sweep ---


def _best_insample_config() -> dict:
    """Read the committed P20 sweep and return the highest-Sharpe row's params."""
    sweep = _load_json(P20_SWEEP_PATH)
    rows = sweep.get("rows", [])
    best = max(rows, key=lambda r: float(r.get("sharpe", float("-inf"))))
    return {
        "beta_window": int(best["beta_window"]),
        "long_quantile": float(best["long_quantile"]),
        "short_quantile": float(best["short_quantile"]),
        "beta_neutral": bool(best["beta_neutral"]),
        "transaction_costs": float(best["transaction_costs"]),
        "weighting": str(best.get("weighting", "equal")),
        "insample_sharpe": float(best["sharpe"]),
        "insample_wealth": float(best["wealth"]),
    }


# --- Summary artifact ---


def _build_summary_artifact(
    default_results: dict,
    best_results: dict,
    trial_info: dict,
    best_config: dict,
) -> dict:
    base_returns = _build_wide_universe_for_seed(SEED_BASE)
    returns_bytes = base_returns.to_csv(date_format="%Y-%m-%d").encode("utf-8")
    returns_sha256 = hashlib.sha256(returns_bytes).hexdigest()

    btc_prices = _load_btc_prices()
    btc_sha256 = hashlib.sha256(
        btc_prices.to_numpy(dtype=float).tobytes()
    ).hexdigest()

    n_trials = trial_info["n_trials_total"]

    summary = {
        "schema": SCHEMA_VERSION,
        "provenance": {
            "generator": "scripts/bab_p38_deflated_significance.py",
            "campaign": "P38 Deflated Significance & Tail-Risk Closure",
            "wp": "WP1 - Deflated / multiple-testing-adjusted significance",
            "synthetic": True,
            "note": (
                "Deterministic synthetic wide universe (P35 wide-universe recipe). "
                "BTC prices from tests/fixtures/wide_bab_universe.csv. "
                "Asset returns = beta * BTC_return + idio, idio ~ N(0, 0.003), "
                "betas linspace(0.35, 1.9, 40). Not real market data; not market "
                "profitability evidence. The verdict is honest and may be negative."
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
        },
        "trial_enumeration": trial_info,
        "best_insample_config": best_config,
        "results": {
            "shipped_default": default_results,
            "best_insample_config": best_results,
        },
    }

    # Campaign-level verdict: both configs must survive deflation.
    default_survives = default_results.get("verdict") == "SURVIVES_DEFLATION"
    best_survives = best_results.get("verdict") == "SURVIVES_DEFLATION"
    summary["campaign_verdict"] = (
        "SURVIVES_DEFLATION" if (default_survives and best_survives)
        else "DOES_NOT_SURVIVE_DEFLATION"
    )
    summary["campaign_verdict_reason"] = (
        "Shipped default and best in-sample config both have DSR >= "
        f"{DSR_SURVIVE_THRESHOLD} after deflation over n_trials_total={n_trials}."
        if (default_survives and best_survives)
        else "At least one of the shipped default / best in-sample config has "
        f"DSR < {DSR_SURVIVE_THRESHOLD} after deflation over n_trials_total={n_trials}."
    )

    return summary


def write_summary(summary: dict, path: Path = SUMMARY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_summary(path: Path = SUMMARY_PATH) -> bool:
    if not path.exists():
        print(f"Summary artifact not found: {path}")
        return False

    trial_info = enumerate_n_trials_total()
    best_config = _best_insample_config()

    default_results = _run_config_all_seeds(BETA_WINDOW, QUANTILE, 0.0)
    default_sig = _significance_for_config(
        default_results["cells"], trial_info["n_trials_total"], BETA_WINDOW, QUANTILE
    )

    bw = best_config["beta_window"]
    q = best_config["long_quantile"]
    best_results = _run_config_all_seeds(bw, q, best_config["transaction_costs"])
    best_sig = _significance_for_config(
        best_results["cells"], trial_info["n_trials_total"], bw, q
    )

    fresh_summary = _build_summary_artifact(
        default_sig, best_sig, trial_info, best_config
    )

    expected_bytes = path.read_bytes()
    actual_bytes = json.dumps(fresh_summary, indent=2, sort_keys=True).encode("utf-8") + b"\n"

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


def build_summary() -> dict:
    """Build the deterministic summary artifact (read-only; does not write to disk)."""
    trial_info = enumerate_n_trials_total()
    best_config = _best_insample_config()

    default_results = _run_config_all_seeds(BETA_WINDOW, QUANTILE, 0.0)
    default_sig = _significance_for_config(
        default_results["cells"], trial_info["n_trials_total"], BETA_WINDOW, QUANTILE
    )

    bw = best_config["beta_window"]
    q = best_config["long_quantile"]
    best_results = _run_config_all_seeds(bw, q, best_config["transaction_costs"])
    best_sig = _significance_for_config(
        best_results["cells"], trial_info["n_trials_total"], bw, q
    )

    return _build_summary_artifact(default_sig, best_sig, trial_info, best_config)


def render_markdown(payload: dict) -> str:
    trial = payload["trial_enumeration"]
    best_cfg = payload["best_insample_config"]
    campaign = payload["campaign_verdict"]
    results = payload["results"]

    def _fmt_num(v, decimals=6):
        if v is None:
            return "None"
        if isinstance(v, bool):
            return "True" if v else "False"
        return f"{float(v):.{decimals}f}"

    lines = [
        "# BAB P38 WP1 — Deflated / Multiple-Testing-Adjusted Significance",
        "",
        f"Schema `{payload['schema']}`. Controlled synthetic stimulus: not real market "
        "data and not market profitability evidence. The verdict is honest and may "
        "be negative.",
        "",
        f"**Campaign verdict:** **{campaign}**",
        f"**Reason:** {payload['campaign_verdict_reason']}",
        "",
        "## Trial enumeration (read-only from committed artifacts)",
        "",
        f"Total effective number of trials searched across the campaign lineage: "
        f"**{trial['n_trials_total']}**.",
        "",
        "| Campaign / artifact | Trials |",
        "|---|---|",
    ]
    for label, count in sorted(trial["breakdown"].items()):
        lines.append(f"| {label} | {count} |")
    lines += [
        "",
        "Each term traces to a committed JSON leaf (P20 grid configurations plus "
        "distinct config cells evaluated across P25-P37 variant artifacts). "
        "Nothing is invented.",
        "",
        "## Best in-sample config (from committed P20 sweep)",
        "",
        "| Parameter | Value |",
        "|---|---|",
        f"| beta_window | {best_cfg['beta_window']} |",
        f"| long_quantile | {_fmt_num(best_cfg['long_quantile'])} |",
        f"| short_quantile | {_fmt_num(best_cfg['short_quantile'])} |",
        f"| beta_neutral | {best_cfg['beta_neutral']} |",
        f"| transaction_costs | {_fmt_num(best_cfg['transaction_costs'])} |",
        f"| weighting | {best_cfg['weighting']} |",
        f"| in-sample Sharpe (P20 sweep) | {_fmt_num(best_cfg['insample_sharpe'])} |",
        f"| in-sample wealth (P20 sweep) | {_fmt_num(best_cfg['insample_wealth'])} |",
        "",
        "## Results — shipped default vs best in-sample config",
        "",
    ]

    for label in ("shipped_default", "best_insample_config"):
        r = results[label]
        lines.append(f"### {label.replace('_', ' ').title()}")
        lines.append("")
        lines.append(
            f"- beta_window: {r.get('beta_window')}, quantile: {_fmt_num(r.get('quantile'))}"
        )
        lines.append(f"- n_seed_cells: {r.get('n_seed_cells')}, n_ok_cells: {r.get('n_ok_cells')}")
        lines.append(f"- mean_sharpe: {_fmt_num(r.get('mean_sharpe'))}")
        lines.append(f"- total_periods: {r.get('total_periods')}")
        lines.append(f"- n_trials (deflation): {r.get('n_trials')}")
        lines.append(f"- sigma0: {_fmt_num(r.get('sigma0'), 10)}")
        lines.append(f"- gamma: {_fmt_num(r.get('gamma'))}")
        lines.append(f"- kappa: {_fmt_num(r.get('kappa'))}")
        lines.append(f"- DSR: {_fmt_num(r.get('dsr'))}")
        lines.append(f"- PSR: {_fmt_num(r.get('psr'))}")
        lines.append(f"- trials-adjusted p-value: {_fmt_num(r.get('trials_adjusted_p_value'))}")
        lines.append(
            f"- min backtest length for PSR=0.50: "
            f"{r.get('min_backtest_length_for_psr_0_50')}"
        )
        lines.append(f"- survives_deflation: {r.get('survives_deflation')}")
        lines.append(f"- verdict: **{r.get('verdict')}**")
        lines.append("")

    lines += [
        "---",
        "",
        "## Interpretation",
        "",
        "- DSR = Deflated Sharpe Ratio: probability the observed Sharpe is genuine "
        "skill after correcting for the multiple trials searched (n_trials_total). "
        "DSR >= 0.50 means more likely than not genuine skill.",
        "- PSR = Probabilistic Sharpe Ratio: probability the Sharpe exceeds zero "
        "(analytical, Bailey & Lopez de Prado).",
        "- trials-adjusted p-value = 1 - DSR: probability the result is noise given "
        "the number of trials.",
        "- min backtest length for PSR=0.50: approximate backtest length T at which "
        "the standard error of Sharpe equals the observed Sharpe (PSR = 0.50 "
        "boundary).",
        "",
        "Synthetic-provenance caveat: results are on the committed synthetic wide "
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
        description="P38 WP1 deflated / multiple-testing-adjusted significance"
    )
    parser.add_argument(
        "--check-deflated-summary",
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

    if args.check_deflated_summary:
        ok = check_summary(args.output)
        return 0 if ok else 1

    print("Running P38 WP1 deflated / multiple-testing-adjusted significance...")
    print(f"  Seeds: {N_SEEDS} (base={SEED_BASE}, inc={SEED_INCREMENT})")
    print(f"  Beta window (default): {BETA_WINDOW}d, quantile: {QUANTILE}")
    print(f"  Bootstrap: {N_BOOTSTRAP} resamples, block length {BLOCK_LENGTH}")

    trial_info = enumerate_n_trials_total()
    best_config = _best_insample_config()

    print(f"  n_trials_total: {trial_info['n_trials_total']}")
    print(f"  Best in-sample config: beta_window={best_config['beta_window']}, "
          f"quantile={best_config['long_quantile']}, "
          f"insample_sharpe={best_config['insample_sharpe']:.4f}")

    started = time.perf_counter()

    default_results = _run_config_all_seeds(BETA_WINDOW, QUANTILE, 0.0)
    default_sig = _significance_for_config(
        default_results["cells"], trial_info["n_trials_total"], BETA_WINDOW, QUANTILE
    )

    bw = best_config["beta_window"]
    q = best_config["long_quantile"]
    best_results = _run_config_all_seeds(bw, q, best_config["transaction_costs"])
    best_sig = _significance_for_config(
        best_results["cells"], trial_info["n_trials_total"], bw, q
    )

    payload = _build_summary_artifact(default_sig, best_sig, trial_info, best_config)
    json_path, md_path = write_artifacts(payload)
    elapsed = time.perf_counter() - started

    print(f"Done in {elapsed:.2f}s")
    print(f"  Shipped default: DSR={default_sig['dsr']} PSR={default_sig['psr']} "
          f"verdict={default_sig['verdict']}")
    print(f"  Best in-sample:    DSR={best_sig['dsr']} PSR={best_sig['psr']} "
          f"verdict={best_sig['verdict']}")
    print(f"  Campaign verdict: {payload['campaign_verdict']}")
    print(f"  Summary written to: {json_path}")
    print(f"  Markdown written to: {md_path}")

    if payload["campaign_verdict"] != "SURVIVES_DEFLATION":
        print("NOTE: campaign does not survive deflation — honest negative verdict.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
