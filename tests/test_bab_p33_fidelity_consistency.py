"""Acceptance tests for P33 WP0: BAB_FIDELITY.md data-consistency guard.

Contract (from HANDOFF.md P33 WP0):

* Every published cell of ``docs/BAB_FIDELITY.md`` §3 (before/after tables at
  q=0.3 and q=0.2) and §4 (daily ``beta_window x quantile`` grid) MUST equal a
  deterministic recompute produced by the §8 "Reproduce" snippet run against
  the committed read-only fixture ``tests/fixtures/real_market_prices.csv``
  (398 rows, 2021-01-05 -> 2022-07-15, ``beta_window=90``, ``min_observations=60``,
  ``q in {0.2, 0.3}``, ``transaction_costs=0.001``).
* The BTC buy-and-hold reference row (§3) is also asserted against the same
  fixture's BTC column.
* ``docs/BAB_FIDELITY.md`` is the only top-level narrative doc with no prior
  consistency guard (the prior coverage in
  ``tests/test_bab_p20_beta_neutral_default.py:113-126`` goldened only the 4
  ``beta_neutral=False`` wealth+Sharpe cells and ``:85-95`` asserted only the
  §4 grid's neutrality *bounds*). This test makes the coverage total: the
  ``beta_neutral=True`` rows, the ann-vol / max-DD / turnover / realized-beta /
  model-beta columns, the BTC reference row, and the exact §4 grid cell values
  are all now pinned to a deterministic recompute.
* Any cell that cannot be byte-reproduced to the published rounding MUST be
  explicitly allow-listed here with a written reason -- never silently skipped,
  never hand-waved, and NEVER edit ``docs/BAB_FIDELITY.md``.

This test is read-only w.r.t. the doc and the fixture. The fixture is a
deterministic synthetic random walk, not real market data; nothing here is
evidence of real profitability.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from strategies.betting_against_beta import BABStrategy, metrics
from strategies.betting_against_beta.data_loader import load_prices

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL = str(REPO_ROOT / "tests" / "fixtures" / "real_market_prices.csv")

# Published table cells that cannot be byte-reproduced to the published
# rounding. Each maps a logical cell id -> (published_text, recompute_value,
# written_reason). They are asserted to be *within float-noise* of the recompute
# rather than byte-equal, with the reason recorded here so nothing is silently
# skipped.
#
# The §4 "max|Σw|" column is published as float-residue (8e-16 / 5e-16 / 9e-16);
# the actual dollar-neutrality gate is ``max_t |Σ_i w_{t,i}| <= 1e-9`` (see
# ``docs/BAB_FIDELITY.md`` §4 acceptance gates and
# ``tests/test_bab_p20_beta_neutral_default.py``). The e-16 residues are the
# IEEE-754 cancellation floor of summing weights that are constructed to sum to
# zero; they are not separately reproducible digits and are therefore
# allow-listed as float-noise and asserted against the real gate instead.
FLOAT_NOISE_ALLOW_LIST: dict[str, str] = {
    "§4/60/0.2/max|Σw|": (
        "published 8e-16 is the IEEE-754 cancellation floor of weights that sum "
        "to zero by construction; not a separately reproducible digit. Real gate "
        "is max_t |Σ_i w_{t,i}| <= 1e-9 (asserted below)."
    ),
    "§4/60/0.3/max|Σw|": (
        "published 5e-16 is the IEEE-754 cancellation floor; real gate is "
        "max_t |Σ_i w_{t,i}| <= 1e-9."
    ),
    "§4/90/0.2/max|Σw|": (
        "published 9e-16 is the IEEE-754 cancellation floor; real gate is "
        "max_t |Σ_i w_{t,i}| <= 1e-9."
    ),
    "§4/90/0.3/max|Σw|": (
        "published 5e-16 is the IEEE-754 cancellation floor; real gate is "
        "max_t |Σ_i w_{t,i}| <= 1e-9."
    ),
    "§4/120/0.2/max|Σw|": (
        "published 9e-16 is the IEEE-754 cancellation floor; real gate is "
        "max_t |Σ_i w_{t,i}| <= 1e-9."
    ),
    "§4/120/0.3/max|Σw|": (
        "published 5e-16 is the IEEE-754 cancellation floor; real gate is "
        "max_t |Σ_i w_{t,i}| <= 1e-9."
    ),
}


@pytest.fixture(scope="module")
def prices():
    return load_prices(REAL, benchmark="BTC")


def _model_beta(result):
    """Per-period model beta ``sum_i w_{t,i} beta_{t,i}`` (matches §3/§4 def)."""
    weights = result.weights
    betas = result.betas.reindex(columns=weights.columns).fillna(0.0)
    return (weights * betas).sum(axis=1)


def _row(result, prices):
    """Recompute the §3/§4 cell tuple for one strategy result.

    Returns a dict of the seven published §3 quantities (wealth, sharpe,
    ann_vol, max_dd, realized_beta, model_beta_max, turnover). ``model_beta_max``
    is ``max_t |Σ_i w_{t,i} beta_{t,i}|`` per the §4 definition.
    """
    rets = result.backtest["returns"]
    cum = result.backtest["cumulative"]
    return {
        "wealth": float(cum.iloc[-1]),
        "sharpe": float(metrics.sharpe_ratio(rets)),
        "ann_vol": float(metrics.annualized_volatility(rets)),
        "max_dd": float(metrics.max_drawdown(cum)),
        "realized_beta": float(metrics.strategy_beta(rets, prices["BTC"])),
        "model_beta_max": float(_model_beta(result).abs().max()),
        "turnover": float(metrics.turnover(result.weights)),
    }


def _run(prices, *, q, beta_neutral, window=90, rebalance_freq="daily"):
    strat = BABStrategy(
        benchmark="BTC",
        beta_window=window,
        min_observations=60,
        long_quantile=q,
        short_quantile=q,
        transaction_costs=0.001,
        rebalance_freq=rebalance_freq,
        beta_neutral=beta_neutral,
    )
    return strat.run(returns_df=prices)


# Published §3 table cells (docs/BAB_FIDELITY.md:65-76). Each entry is
# (q, beta_neutral) -> dict of column -> published value at the doc's rounding.
# Values transcribed verbatim from docs/BAB_FIDELITY.md §3; the test recomputes
# and compares at the doc's stated rounding (wealth 4dp, sharpe/ann_vol/max_dd/
# realized_beta 3dp, model_beta 3 sig figs, turnover 3dp).
SECTION_3 = {
    (0.3, False): {
        "wealth": 0.3136,
        "sharpe": -1.418,
        "ann_vol": 0.446,
        "max_dd": -0.758,
        "realized_beta": -0.572,
        "model_beta_max": 1.11,
        "turnover": 0.201,
    },
    (0.3, True): {
        "wealth": 0.7057,
        "sharpe": -0.725,
        "ann_vol": 0.258,
        "max_dd": -0.413,
        "realized_beta": 0.059,
        "model_beta_max": 1.5e-04,
        "turnover": 0.264,
    },
    (0.2, False): {
        "wealth": 0.4214,
        "sharpe": -0.680,
        "ann_vol": 0.567,
        "max_dd": -0.634,
        "realized_beta": -0.908,
        "model_beta_max": 1.48,
        "turnover": 0.126,
    },
    (0.2, True): {
        "wealth": 1.3093,
        "sharpe": 0.649,
        "ann_vol": 0.366,
        "max_dd": -0.227,
        "realized_beta": 0.006,
        "model_beta_max": 2.1e-04,
        "turnover": 0.234,
    },
}

# Rounding per column, matching how docs/BAB_FIDELITY.md §3 presents each cell.
ROUNDING = {
    "wealth": 4,
    "sharpe": 3,
    "ann_vol": 3,
    "max_dd": 3,
    "realized_beta": 3,
    "model_beta_max": None,  # compared at the doc's significant-figure rounding below
    "turnover": 3,
}


def _sig_figs(x: float) -> int:
    """Count significant figures in a published literal (e.g. 1.5e-04 -> 2)."""
    if x == 0.0:
        return 1
    import math

    s = f"{x:.10e}".split("e")[0]  # mantissa, e.g. '1.5000000000'
    digits = s.replace("-", "").replace(".", "").rstrip("0")
    return max(len(digits), 1)


def _assert_matches_published(
    column: str, recompute: float, published: float, context: str,
    rounding: dict[str, int | None],
) -> None:
    """Assert ``recompute`` equals ``published`` at the published cell's precision.

    The doc displays the ``model_beta_max`` column with inconsistent
    significant-figure counts (e.g. §3 bn=True shows ``1.5e-04`` / ``2.1e-04``
    at 2 sig figs, while §4 shows ``1.51e-04`` at 3 sig figs). Rather than
    force a single rounding function, we compare at the half-ULP of the
    *published* value's last significant digit. This is faithful to the doc
    (it reproduces exactly what the doc printed) without editing the doc.
    """
    if recompute == published:
        return
    if column == "model_beta_max":
        if published == 0.0:
            assert recompute == 0.0, f"{context}: expected 0.0, got {recompute!r}"
            return
        import math

        exp = math.floor(math.log10(abs(published)))
        half_ulp = 0.5 * 10.0 ** (exp - (_sig_figs(published) - 1))
        assert abs(recompute - published) <= half_ulp + 1e-18, (
            f"{context} column {column!r}: published {published!r} "
            f"(sig-figs={_sig_figs(published)}, half-ULP={half_ulp!r}) but "
            f"recompute is {recompute!r} (delta {recompute - published!r}). "
            f"NEVER edit the doc; allow-list with a written reason if the "
            f"published cell is irreproducible."
        )
        return
    ndigits = rounding[column]
    assert round(recompute, ndigits) == published, (
        f"{context} column {column!r}: published {published!r} but recompute "
        f"rounds to {round(recompute, ndigits)!r} (raw {recompute!r}). NEVER "
        f"edit the doc; allow-list with a written reason if the published cell "
        f"is irreproducible."
    )


# Published §4 daily grid (docs/BAB_FIDELITY.md:88-95). Each entry is
# (window, q) -> dict of column -> published value. The "max|Σw|" column is
# float-noise and handled via FLOAT_NOISE_ALLOW_LIST + the real ≤1e-9 gate.
SECTION_4 = {
    (60, 0.2): {
        "wealth": 1.3182,
        "sharpe": 0.651,
        "realized_beta": -0.031,
        "model_beta_max": 2.16e-04,
    },
    (60, 0.3): {
        "wealth": 0.4387,
        "sharpe": -1.905,
        "realized_beta": 0.121,
        "model_beta_max": 1.45e-04,
    },
    (90, 0.2): {
        "wealth": 1.3093,
        "sharpe": 0.649,
        "realized_beta": 0.006,
        "model_beta_max": 2.13e-04,
    },
    (90, 0.3): {
        "wealth": 0.7057,
        "sharpe": -0.725,
        "realized_beta": 0.059,
        "model_beta_max": 1.51e-04,
    },
    (120, 0.2): {
        "wealth": 1.3708,
        "sharpe": 0.734,
        "realized_beta": -0.011,
        "model_beta_max": 1.91e-04,
    },
    (120, 0.3): {
        "wealth": 1.1130,
        "sharpe": 0.389,
        "realized_beta": 0.028,
        "model_beta_max": 1.38e-04,
    },
}

SECTION_4_ROUNDING = {
    "wealth": 4,
    "sharpe": 3,
    "realized_beta": 3,
    "model_beta_max": None,
}


# ---------------------------------------------------------------------------
# §3 before/after tables
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("q,beta_neutral", list(SECTION_3.keys()))
def test_section3_every_published_cell_reproduces(prices, q, beta_neutral):
    result = _run(prices, q=q, beta_neutral=beta_neutral)
    recompute = _row(result, prices)
    published = SECTION_3[(q, beta_neutral)]

    for column, published_value in published.items():
        _assert_matches_published(
            column,
            recompute[column],
            published_value,
            f"docs/BAB_FIDELITY.md §3 (q={q}, beta_neutral={beta_neutral})",
            ROUNDING,
        )


def test_section3_btc_buy_and_hold_reference_row(prices):
    """The §3 BTC buy-and-hold reference row (docs/BAB_FIDELITY.md:69)."""
    btc = prices["BTC"]
    wealth = float((1.0 + btc).cumprod().iloc[-1])
    sharpe = float(metrics.sharpe_ratio(btc))
    ann_vol = float(metrics.annualized_volatility(btc))
    realized_beta = float(metrics.strategy_beta(btc, btc))

    assert round(wealth, 4) == pytest.approx(2.0975, abs=1e-12)
    assert round(sharpe, 3) == pytest.approx(1.756, abs=1e-12)
    assert round(ann_vol, 3) == pytest.approx(0.291, abs=1e-12)
    # BTC beta vs itself is exactly 1.0 by construction.
    assert round(realized_beta, 3) == pytest.approx(1.000, abs=1e-12)


# ---------------------------------------------------------------------------
# §4 daily grid
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("window,q", list(SECTION_4.keys()))
def test_section4_every_published_cell_reproduces(prices, window, q):
    result = _run(prices, q=q, beta_neutral=True, window=window)
    recompute = _row(result, prices)
    published = SECTION_4[(window, q)]

    for column, published_value in published.items():
        _assert_matches_published(
            column,
            recompute[column],
            published_value,
            f"docs/BAB_FIDELITY.md §4 (beta_window={window}, q={q})",
            SECTION_4_ROUNDING,
        )


@pytest.mark.parametrize("window,q", list(SECTION_4.keys()))
def test_section4_dollar_neutrality_gate_holds(prices, window, q):
    """The §4 ``max|Σw|`` cells are float-noise; the real gate is ``<= 1e-9``.

    Each ``max|Σw|`` cell is allow-listed in FLOAT_NOISE_ALLOW_LIST with a
    written reason. Here we assert the actual dollar-neutrality gate the doc
    states in its §4 acceptance gates (``max_t |Σ_i w_{t,i}| <= 1e-9``).
    """
    cell_id = f"§4/{window}/{q}/max|Σw|"
    assert cell_id in FLOAT_NOISE_ALLOW_LIST, (
        f"{cell_id} is allow-listed but missing a written reason"
    )
    result = _run(prices, q=q, beta_neutral=True, window=window)
    dollar_sum_max = float(result.weights.sum(axis=1).abs().max())
    assert dollar_sum_max <= 1e-9, (
        f"§4 (beta_window={window}, q={q}) dollar-neutrality gate violated: "
        f"max_t |Σ_i w_{{t,i}}| = {dollar_sum_max!r} > 1e-9"
    )


def test_section4_realized_beta_grid_wide_gate(prices):
    """§4 acceptance gate: ``|realized β| <= 0.15`` grid-wide, ``<= 0.07`` for w in {90,120}."""
    for window, q in SECTION_4:
        result = _run(prices, q=q, beta_neutral=True, window=window)
        realized = metrics.strategy_beta(result.backtest["returns"], prices["BTC"])
        assert abs(realized) <= 0.15, (
            f"§4 (beta_window={window}, q={q}) realized beta {realized!r} "
            f"exceeds the grid-wide <= 0.15 gate"
        )
        if window in (90, 120):
            assert abs(realized) <= 0.07, (
                f"§4 (beta_window={window}, q={q}) realized beta {realized!r} "
                f"exceeds the <= 0.07 gate for window in {{90,120}}"
            )


def test_section4_model_beta_gate(prices):
    """§4 acceptance gate: ``max_t |Σ_i w_{t,i} beta_{t,i}| <= 1e-3`` at every grid point."""
    for window, q in SECTION_4:
        result = _run(prices, q=q, beta_neutral=True, window=window)
        model_beta_max = float(_model_beta(result).abs().max())
        assert model_beta_max <= 1e-3, (
            f"§4 (beta_window={window}, q={q}) model beta max {model_beta_max!r} "
            f"exceeds the <= 1e-3 gate"
        )


# ---------------------------------------------------------------------------
# Allow-list integrity
# ---------------------------------------------------------------------------


def test_float_noise_allow_list_is_total():
    """Every published §4 ``max|Σw|`` cell must be allow-listed with a reason."""
    published_grid_cells = {
        f"§4/{window}/{q}/max|Σw|" for (window, q) in SECTION_4
    }
    assert set(FLOAT_NOISE_ALLOW_LIST) == published_grid_cells, (
        f"FLOAT_NOISE_ALLOW_LIST keys {set(FLOAT_NOISE_ALLOW_LIST)} do not "
        f"match the published §4 grid cells {published_grid_cells}"
    )
    for cell_id, reason in FLOAT_NOISE_ALLOW_LIST.items():
        assert reason, f"allow-listed cell {cell_id} has no written reason"


# ---------------------------------------------------------------------------
# Hygiene
# ---------------------------------------------------------------------------


def test_no_ruff_errors_on_new_files():
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(__file__)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert ruff.returncode == 0, f"ruff must pass: {ruff.stdout} {ruff.stderr}"
