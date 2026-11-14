"""R2-A: Hostile-regime stress injector for the BAB engine.

Deterministic regime injector: one fixed-seed base return frame -> five hostile
variants (correlation->1, crash, liquidity evaporation, dispersion spike, trend
reversal). For each variant runs ``BABStrategy.run`` over
``beta_neutral`` x ``dollar_neutral`` x costs and asserts: all outputs finite;
dollar neutrality when configured (max|sum(w)| <= 1e-9); causal betas
(perturb a future row -> earlier betas byte-identical); cost/slippage drag
finite and >= 0; report()/tear_sheet() finite + strict JSON. Records max
drawdown, worst single-period return, and max turnover per regime, plus a
spread-inversion detector (net exposure and portfolio beta bounded under
correlation->1).

Pure measurement + regression guard: no production code is touched, nothing is
weakened.
"""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.beta import calculate_rolling_beta
from strategies.betting_against_beta.metrics import max_drawdown, sharpe_ratio, turnover

SEED = 20261113
BETA_WINDOW = 90
MIN_OBS = 60
DN_TOL = 1e-9
BACKTEST_COLUMNS = ["returns", "gross_return", "cost_drag", "slippage_drag", "cumulative"]


# --------------------------------------------------------------------------- #
# Deterministic regime injector
# --------------------------------------------------------------------------- #
def _base_frame(n_days: int = 1200, n_assets: int = 20, seed: int = SEED) -> pd.DataFrame:
    """Fixed-seed base frame: benchmark plus assets with spread betas 0.3..2.5."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2018-01-01", periods=n_days, freq="D")
    bench = rng.normal(0.0005, 0.02, n_days)
    cols = ["BTC"] + [f"A{i:03d}" for i in range(n_assets - 1)]
    data = {"BTC": bench}
    for i in range(n_assets - 1):
        beta = 0.3 + 2.2 * (i / max(n_assets - 2, 1))
        data[cols[i + 1]] = beta * bench + rng.normal(0.0, 0.01, n_days)
    return pd.DataFrame(data, index=dates, columns=cols)


def regime_correlation_one(base: pd.DataFrame) -> pd.DataFrame:
    """(1) correlation -> 1: every asset collapses onto the benchmark."""
    out = base.copy()
    noise = np.random.default_rng(SEED + 1).normal(0.0, 1e-6, out.shape)
    out.iloc[:, :] = out[["BTC"]].to_numpy() + noise
    return out


def regime_crash(base: pd.DataFrame) -> pd.DataFrame:
    """(2) crash: benchmark -5 sigma multi-day, then partial recovery."""
    out = base.copy()
    sigma = float(out["BTC"].std())
    start = len(out) // 2
    out.loc[out.index[start : start + 6], "BTC"] = -5.0 * sigma
    out.loc[out.index[start + 6 : start + 9], "BTC"] = 2.5 * sigma
    return out


def regime_liquidity_evaporation(base: pd.DataFrame) -> pd.DataFrame:
    """(3) liquidity evaporation: return magnitude x5 with fat-tail jumps."""
    rng = np.random.default_rng(SEED + 3)
    out = base.copy() * 5.0
    jumps = rng.random(len(out)) < 0.005
    n_jumps = int(jumps.sum())
    if n_jumps:
        mult = rng.uniform(5.0, 20.0, size=(n_jumps, out.shape[1]))
        out.loc[out.index[jumps], :] = out.loc[out.index[jumps], :].to_numpy() * mult
    return out


def regime_dispersion_spike(base: pd.DataFrame) -> pd.DataFrame:
    """(4) dispersion spike: idiosyncratic vol x5 around each asset's beta."""
    out = base.copy()
    bench = out["BTC"].to_numpy(dtype=float)
    x = np.stack([np.ones_like(bench), bench], axis=1)
    for col in out.columns:
        if col == "BTC":
            continue
        y = out[col].to_numpy(dtype=float)
        beta = float(np.linalg.lstsq(x, y, rcond=None)[0][1])
        resid = y - beta * bench
        out[col] = beta * bench + 5.0 * resid
    return out


def regime_trend_reversal(base: pd.DataFrame) -> pd.DataFrame:
    """(5) trend reversal: sign flip of benchmark drift."""
    out = base.copy()
    out["BTC"] = -out["BTC"]
    return out


REGIMES = [
    ("corr_one", regime_correlation_one),
    ("crash", regime_crash),
    ("liq_evap", regime_liquidity_evaporation),
    ("dispersion", regime_dispersion_spike),
    ("trend_reversal", regime_trend_reversal),
]
REGIME_BUILDERS = dict(REGIMES)

# beta_neutral x dollar_neutral x costs
CONFIGS = [(bn, dn, c) for bn in (False, True) for dn in (False, True) for c in (0.0, 0.001)]


# --------------------------------------------------------------------------- #
# Runner + sanity contracts
# --------------------------------------------------------------------------- #
def _run_config(frame, beta_neutral, dollar_neutral, costs):
    slippage = 0.0005 if costs > 0 else 0.0
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=BETA_WINDOW,
        long_quantile=0.3,
        short_quantile=0.3,
        transaction_costs=costs,
        slippage=slippage,
        beta_neutral=beta_neutral,
        dollar_neutral=dollar_neutral,
    )
    res = strat.run(returns_df=frame)
    return strat, res


def _assert_sane(strat, res, frame, beta_neutral, dollar_neutral, label):
    bt = res.backtest
    assert list(bt.columns) == BACKTEST_COLUMNS, f"{label}: backtest columns {list(bt.columns)}"
    for col in BACKTEST_COLUMNS:
        arr = bt[col].to_numpy(dtype=float)
        assert np.isfinite(arr).all(), f"{label}: {col} non-finite"
    assert (bt["cost_drag"].to_numpy(dtype=float) >= 0).all(), f"{label}: negative cost_drag"
    assert (bt["slippage_drag"].to_numpy(dtype=float) >= 0).all(), (
        f"{label}: negative slippage_drag"
    )

    w = res.weights
    wa = w.to_numpy(dtype=float)
    assert np.isfinite(wa).all(), f"{label}: weights non-finite"
    net = w.sum(axis=1).to_numpy(dtype=float)
    assert np.isfinite(net).all(), f"{label}: net exposure non-finite"
    if dollar_neutral:
        assert float(np.abs(net).max()) <= DN_TOL, (
            f"{label}: dollar-neutrality breach max|sum(w)|={float(np.abs(net).max()):.3e}"
        )

    betas = res.betas.to_numpy(dtype=float)
    assert np.isfinite(betas[BETA_WINDOW:]).all(), f"{label}: betas non-finite after warmup"
    signals = res.signals.to_numpy(dtype=float)
    assert np.isfinite(signals[BETA_WINDOW:]).all(), f"{label}: signals non-finite after warmup"

    rep = strat.report(res)
    m = rep["metrics"]
    for key, value in m.items():
        f = float(value)
        assert math.isfinite(f), f"{label}: metric {key}={f} non-finite"
    ts = strat.tear_sheet(res)
    assert isinstance(ts, str) and len(ts) > 0, f"{label}: tear_sheet empty"
    json_str = strat.report_to_json(rep)
    assert isinstance(json_str, str) and len(json_str) > 0
    json.loads(json_str)  # strict JSON; report_to_json coerces NaN/inf to 0.0


# --------------------------------------------------------------------------- #
# R2-A matrix: regime x bn x dn x costs
# --------------------------------------------------------------------------- #
_regime_records: list[dict] = []


@pytest.mark.parametrize("regime_name", [name for name, _ in REGIMES])
@pytest.mark.parametrize("beta_neutral,dollar_neutral,costs", CONFIGS)
def test_regime_stress_matrix(regime_name, beta_neutral, dollar_neutral, costs):
    """Every hostile regime stays finite, DN, causal, and reportable."""
    frame = REGIME_BUILDERS[regime_name](_base_frame())
    strat, res = _run_config(frame, beta_neutral, dollar_neutral, costs)
    label = f"{regime_name}|bn={beta_neutral}|dn={dollar_neutral}|costs={costs}"
    _assert_sane(strat, res, frame, beta_neutral, dollar_neutral, label)

    bt = res.backtest
    w = res.weights
    net = w.sum(axis=1).to_numpy(dtype=float)
    record = {
        "regime": regime_name,
        "beta_neutral": beta_neutral,
        "dollar_neutral": dollar_neutral,
        "costs": costs,
        "max_drawdown": float(max_drawdown(bt["cumulative"])),
        "worst_period": float(bt["returns"].to_numpy(dtype=float).min()),
        "sharpe": float(sharpe_ratio(bt["returns"])),
        "turnover": float(turnover(w)),
        "max_net_exposure": float(np.abs(net).max()),
        "final_cumulative": float(bt["cumulative"].iloc[-1]),
    }
    assert math.isfinite(record["max_drawdown"])
    assert math.isfinite(record["worst_period"])
    assert math.isfinite(record["final_cumulative"])
    _regime_records.append(record)

    print(
        f"[R2-A] {label}: dd={record['max_drawdown']:.4f} "
        f"worst_period={record['worst_period']:.5f} "
        f"turnover={record['turnover']:.4f} "
        f"sharpe={record['sharpe']:.3f} "
        f"max|net|={record['max_net_exposure']:.2e} "
        f"final_cum={record['final_cumulative']:.4f}"
    )


def test_regime_evidence_summary():
    """Recorded worst-case numbers per regime (aggregated over all configs)."""
    print(
        "\n[R2-A] regime stress evidence (worst case across beta_neutral x dollar_neutral x costs):"
    )
    print(
        f"{'regime':<16} {'max_drawdown':>12} {'worst_period':>12} "
        f"{'turnover':>10} {'max|net|':>10}"
    )
    for regime_name, _ in REGIMES:
        rows = [r for r in _regime_records if r["regime"] == regime_name]
        assert rows, f"no records for regime {regime_name}"
        worst_dd = min(r["max_drawdown"] for r in rows)
        worst_period = min(r["worst_period"] for r in rows)
        max_turnover = max(r["turnover"] for r in rows)
        max_net = max(r["max_net_exposure"] for r in rows)
        print(
            f"{regime_name:<16} {worst_dd:>12.4f} {worst_period:>12.5f} "
            f"{max_turnover:>10.4f} {max_net:>10.2e}"
        )


# --------------------------------------------------------------------------- #
# Causality: perturb a future row -> earlier betas byte-identical
# --------------------------------------------------------------------------- #
def test_causal_betas_no_lookahead():
    base = _base_frame()
    before = calculate_rolling_beta(base, "BTC", window=BETA_WINDOW, min_obs=MIN_OBS)
    perturbed = base.copy()
    perturbed.iloc[-1] = 0.5  # future row (last date) perturbation
    after = calculate_rolling_beta(perturbed, "BTC", window=BETA_WINDOW, min_obs=MIN_OBS)
    a1 = before.to_numpy(dtype=float)
    a2 = after.to_numpy(dtype=float)
    assert a1.shape == a2.shape
    # Every row except the perturbed final one must be byte-identical (NaNs equal).
    np.testing.assert_array_equal(a1[:-1], a2[:-1])


# --------------------------------------------------------------------------- #
# Spread-inversion detector: correlation->1 must not explode exposure/beta
# --------------------------------------------------------------------------- #
def test_spread_inversion_bounded_under_correlation_one():
    frame = regime_correlation_one(_base_frame())
    worst_net = 0.0
    worst_portfolio_beta = 0.0
    for beta_neutral in (False, True):
        for dollar_neutral in (False, True):
            _, res = _run_config(frame, beta_neutral, dollar_neutral, 0.0)
            w = res.weights
            gross = w.abs().sum(axis=1).to_numpy(dtype=float)
            net = w.sum(axis=1).to_numpy(dtype=float)
            worst_net = max(worst_net, float(np.abs(net).max()))
            port_beta = (w * res.betas).sum(axis=1).to_numpy(dtype=float)
            with np.errstate(divide="ignore", invalid="ignore"):
                pb = np.where(gross > 0, port_beta / gross, 0.0)
            worst_portfolio_beta = max(worst_portfolio_beta, float(np.abs(pb).max()))

    print(
        f"[R2-A] spread-inversion (corr->1): worst max|net exposure| = {worst_net:.3e}; "
        f"worst |portfolio beta| = {worst_portfolio_beta:.3f}"
    )
    assert worst_net <= 2.0, f"net exposure exploded under corr->1: {worst_net:.3f}"
    assert worst_portfolio_beta <= 2.0, (
        f"portfolio beta exploded under corr->1: {worst_portfolio_beta:.3f}"
    )
