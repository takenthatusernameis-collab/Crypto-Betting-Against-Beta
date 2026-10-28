"""Transaction cost model for BAB backtesting.

Deterministic, crypto-realistic transaction costs expressed as a fraction of
portfolio value per period:

  * linear fee + bid-ask spread on turnover (notional traded)
  * square-root market impact scaled by ADV liquidity:
      impact = coeff * sqrt(min(|trade_notional| / adv, participation_cap))
  * short borrow costs: annualized fee charged pro-rata per day on short notional

All rate parameters are fractions (e.g. 0.001 = 10 bps = 0.10%). Costs are
non-negative and never leak NaN/inf; missing price/ADV data skips the impact
term for that asset rather than failing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union

import numpy as np
import pandas as pd


class BABCostError(ValueError):
    """Raised when a transaction cost model is misconfigured."""


@dataclass(frozen=False)
class TransactionCostModel:
    """Parameters for realistic transaction costs.

    Portfolio value is treated as 1.0 unit, so weights double as notional
    fractions and participation = |weight_delta| * price / adv.
    """

    # Linear execution fee as fraction of one-way notional traded.
    linear_fee: float = 0.001
    # Bid-ask spread cost charged on one-way notional traded.
    bid_ask_bps: float = 0.0005
    # Square-root market-impact coefficient (fraction of traded notional at
    # unit participation).
    impact_coefficient: float = 0.0005
    # Max participation of ADV allowed in a single trade (fraction).
    participation_cap: float = 0.10
    # Annualized borrow fee for short positions (fraction per year).
    borrow_bps_per_year: float = 0.02
    # Fixed fee charged as fraction of portfolio in any period with turnover.
    fixed_fee_per_trade: float = 0.0
    trading_days_per_year: int = 252
    # Per-asset average daily volume in dollars (dict/Series/DataFrame).
    # When absent, the square-root impact term is skipped for those assets.
    adv_usd: Optional[Union[dict, pd.Series, pd.DataFrame]] = None

    def __post_init__(self) -> None:
        self._validate()
        try:
            object.__setattr__(self, "_frozen", True)
        except Exception:
            pass

    def __setattr__(self, name: str, value) -> None:
        if getattr(self, "_frozen", False) and name != "_frozen":
            raise AttributeError(
                f"Cannot mutate frozen TransactionCostModel attribute '{name}'"
            )
        object.__setattr__(self, name, value)

    def _validate(self) -> None:
        errors: list[str] = []
        for name in (
            "linear_fee",
            "bid_ask_bps",
            "impact_coefficient",
            "borrow_bps_per_year",
            "fixed_fee_per_trade",
        ):
            value = getattr(self, name)
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or value < 0
            ):
                errors.append(f"{name} must be a non-negative number, got {value!r}")
        cap = self.participation_cap
        if not isinstance(cap, (int, float)) or isinstance(cap, bool) or not (0 < cap <= 1):
            errors.append(f"participation_cap must be in (0, 1], got {cap!r}")
        td = self.trading_days_per_year
        if not isinstance(td, int) or isinstance(td, bool) or td < 1:
            errors.append(f"trading_days_per_year must be a positive int, got {td!r}")
        if errors:
            raise BABCostError("; ".join(errors))


def _adv_series(adv_usd: Optional[Union[dict, pd.Series, pd.DataFrame]]) -> Optional[pd.Series]:
    """Normalize adv_usd to an asset-indexed Series, or None when unavailable."""
    if adv_usd is None:
        return None
    if isinstance(adv_usd, dict):
        return pd.Series(adv_usd, dtype="float64")
    if isinstance(adv_usd, pd.Series):
        return adv_usd.astype("float64")
    if isinstance(adv_usd, pd.DataFrame):
        return adv_usd.astype("float64")
    return None


def _clean_frame(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    if df is None:
        return None
    df = pd.DataFrame(df)
    if df.empty:
        return None
    return df.replace([np.inf, -np.inf], np.nan)


def compute_transaction_costs(
    weights,
    weights_prev,
    prices: Optional[pd.DataFrame] = None,
    model: Optional[TransactionCostModel] = None,
    adv_usd: Optional[Union[dict, pd.Series, pd.DataFrame]] = None,
) -> pd.Series:
    """Per-period transaction costs as a fraction of portfolio value.

    Parameters
    ----------
    weights : DataFrame
        Target weights (index = dates, columns = assets).
    weights_prev : DataFrame
        Previous period's weights. First period trades from zero when absent.
    prices : DataFrame, optional
        Asset prices aligned to ``weights``; required for the impact term.
    model : TransactionCostModel, optional
        Cost parameters. Defaults to a zero-cost model.
    adv_usd : dict/Series/DataFrame, optional
        Average daily volume in dollars per asset (optionally time-varying as a
        DataFrame aligned to ``weights``).

    Returns
    -------
    pd.Series
        Non-negative cost per period (fraction of portfolio). Subtract from
        portfolio returns.
    """
    if model is None:
        model = TransactionCostModel(
            linear_fee=0.0, bid_ask_bps=0.0, impact_coefficient=0.0,
            borrow_bps_per_year=0.0, fixed_fee_per_trade=0.0,
        )

    if weights is None:
        return pd.Series(dtype=float)
    weights = _clean_frame(weights)
    if weights is None or len(weights.columns) == 0:
        return pd.Series(0.0, index=getattr(weights, "index", []), dtype=float)

    weights = weights.fillna(0.0)

    if weights_prev is None:
        weights_prev = pd.DataFrame(
            0.0, index=weights.index, columns=weights.columns
        )
    else:
        weights_prev = _clean_frame(weights_prev)
        if weights_prev is None:
            weights_prev = pd.DataFrame(
                0.0, index=weights.index, columns=weights.columns
            )
        else:
            weights_prev = weights_prev.reindex(
                index=weights.index, columns=weights.columns, fill_value=0.0
            ).fillna(0.0)

    index = weights.index
    columns = weights.columns

    turnover = (weights - weights_prev).abs().sum(axis=1)

    # Linear fee + bid-ask on one-way notional traded.
    rate = float(model.linear_fee) + float(model.bid_ask_bps)
    costs = rate * turnover

    # Square-root market impact: |dw| * coeff * sqrt(min(|dw| * price / adv, cap)).
    prices = _clean_frame(prices)
    adv_input = model.adv_usd if adv_usd is None else adv_usd
    adv_series = _adv_series(adv_input)
    if (
        prices is not None
        and adv_series is not None
        and float(model.impact_coefficient) > 0
    ):
        prices = prices.reindex(index=index, columns=columns)
        if isinstance(adv_series, pd.DataFrame):
            adv_aligned = adv_series.reindex(index=index, columns=columns)
        else:
            adv_aligned = pd.DataFrame(
                np.tile(
                    adv_series.reindex(columns).to_numpy(dtype=float),
                    (len(index), 1),
                ),
                index=index,
                columns=columns,
            )
        trade = (weights - weights_prev).abs()
        participation = trade * prices / adv_aligned
        participation = participation.clip(
            upper=float(model.participation_cap)
        ).fillna(0.0)
        impact = (
            trade
            * float(model.impact_coefficient)
            * np.sqrt(participation.values)
        )
        costs = costs + impact.sum(axis=1).fillna(0.0)

    # Short borrow: annualized fee pro-rata per day on short notional held.
    daily_borrow = float(model.borrow_bps_per_year) / float(model.trading_days_per_year)
    if daily_borrow > 0:
        short_notional = (-weights).clip(lower=0.0).sum(axis=1)
        costs = costs + short_notional * daily_borrow

    # Fixed fee in any period with turnover.
    if float(model.fixed_fee_per_trade) > 0:
        costs = costs + float(model.fixed_fee_per_trade) * (turnover > 0).astype(float)

    costs = costs.replace([np.inf, -np.inf], np.nan).fillna(0.0).clip(lower=0.0)
    return pd.Series(costs.values, index=index, name="transaction_costs")
