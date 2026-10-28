"""Shorting constraints for BAB strategy.

Models annualized borrow costs, borrow availability per asset, and hard caps
on short exposure / short notional. Can be integrated into portfolio
construction via :func:`apply_shorting_constraints`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Union

import numpy as np
import pandas as pd

from .errors import BABDataError


class BABShortingError(BABDataError):
    """Raised when shorting constraints are violated in strict mode."""


@dataclass(frozen=False)
class ShortingConstraints:
    """Configuration for shorting constraints and borrow costs."""

    # Annualized borrow cost in fraction (e.g. 0.02 = 2% per year). Can be dict
    # per-asset or a single float.
    default_borrow_bps_per_year: float = 0.02
    borrow_bps_per_year: Optional[Union[float, Dict[str, float]]] = None
    # Whether an asset is borrowable. Defaults to True for all.
    borrowable: Optional[Dict[str, bool]] = None
    # Hard caps on short exposure.
    max_short_exposure: Optional[float] = None  # total short notional as fraction of portfolio
    max_short_leverage: Optional[float] = None  # alias for max_short_exposure
    max_short_notional_per_asset: Optional[float] = None  # per-asset short notional cap
    max_short_weight: Optional[float] = None  # alias for per-asset cap
    # If True, raise on violations (unborrowable short, exceeding caps depending on policy).
    strict: bool = False

    def __post_init__(self) -> None:
        # Accept aliases
        if self.max_short_leverage is not None and self.max_short_exposure is None:
            object.__setattr__(self, "max_short_exposure", self.max_short_leverage)
        if self.max_short_weight is not None and self.max_short_notional_per_asset is None:
            object.__setattr__(self, "max_short_notional_per_asset", self.max_short_weight)
        # Normalize borrow_bps_per_year dict if passed
        if isinstance(self.borrow_bps_per_year, (int, float)) and not isinstance(self.borrow_bps_per_year, bool):
            object.__setattr__(self, "borrow_bps_per_year", {"*": float(self.borrow_bps_per_year)})
        self._validate()
        try:
            object.__setattr__(self, "_frozen", True)
        except Exception:
            pass

    def __setattr__(self, name: str, value) -> None:
        if getattr(self, "_frozen", False) and name != "_frozen":
            raise AttributeError(f"Cannot mutate frozen ShortingConstraints attribute '{name}'")
        object.__setattr__(self, name, value)

    def _validate(self) -> None:
        errors = []
        if not isinstance(self.default_borrow_bps_per_year, (int, float)) or isinstance(self.default_borrow_bps_per_year, bool) or self.default_borrow_bps_per_year < 0:
            errors.append("default_borrow_bps_per_year must be non-negative")
        for name in ("max_short_exposure", "max_short_leverage", "max_short_notional_per_asset", "max_short_weight"):
            val = getattr(self, name)
            if val is None:
                continue
            if not isinstance(val, (int, float)) or isinstance(val, bool) or val < 0:
                errors.append(f"{name} must be non-negative")
        if isinstance(self.borrow_bps_per_year, dict):
            for k, v in self.borrow_bps_per_year.items():
                if not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0:
                    errors.append("borrow_bps_per_year values must be non-negative")
        if self.borrowable is not None and not isinstance(self.borrowable, dict):
            errors.append("borrowable must be a dict")
        if errors:
            raise BABShortingError("; ".join(errors))

    def is_borrowable(self, asset: str) -> bool:
        if self.borrowable is None:
            return True
        if asset in self.borrowable:
            return bool(self.borrowable[asset])
        # check wildcard
        if "*" in self.borrowable:
            return bool(self.borrowable["*"])
        return True

    def borrow_bps(self, asset: str) -> float:
        if isinstance(self.borrow_bps_per_year, dict):
            if asset in self.borrow_bps_per_year:
                return float(self.borrow_bps_per_year[asset])
            if "*" in self.borrow_bps_per_year:
                return float(self.borrow_bps_per_year["*"])
        return float(self.default_borrow_bps_per_year)

    def borrow_rate_annual(self, asset: str) -> float:
        return self.borrow_bps(asset)


# Alias
BorrowConstraints = ShortingConstraints


def _clean_df(df):
    if df is None:
        return None
    df = pd.DataFrame(df)
    if df.empty:
        return None
    return df.replace([np.inf, -np.inf], np.nan)


def apply_shorting_constraints(signals_or_weights, constraints: Optional[ShortingConstraints] = None,
                                **kwargs):
    """Apply shorting constraints to signals/weights.

    Accepts signals (e.g. -1/0/1) or weights; returns weights DataFrame.
    """
    if constraints is None:
        # allow passing as first arg dict/config style? be flexible
        if isinstance(signals_or_weights, ShortingConstraints):
            constraints = signals_or_weights
            # no data? return empty
            return pd.DataFrame()
        # check kwargs
        if "shorting_constraints" in kwargs:
            sc = kwargs["shorting_constraints"]
            if isinstance(sc, dict):
                constraints = ShortingConstraints(**sc)
            elif isinstance(sc, ShortingConstraints):
                constraints = sc
            else:
                constraints = ShortingConstraints()
        elif "constraints" in kwargs:
            sc = kwargs["constraints"]
            if isinstance(sc, dict):
                constraints = ShortingConstraints(**sc)
            elif isinstance(sc, ShortingConstraints):
                constraints = sc
            else:
                constraints = ShortingConstraints()
        else:
            # if nothing passed, maybe try to infer from dict
            constraints = ShortingConstraints()
    elif isinstance(constraints, dict):
        constraints = ShortingConstraints(**constraints)

    df = _clean_df(signals_or_weights)
    if df is None or len(df.columns) == 0:
        return pd.DataFrame() if signals_or_weights is None else pd.DataFrame(index=getattr(signals_or_weights, "index", []), columns=getattr(signals_or_weights, "columns", []))

    # Work on copy
    weights = df.copy().astype(float).fillna(0.0)

    # Convert signals to weights if values are in {-1,0,1}
    # Heuristic: if all non-zero values are in {-1,1}, treat as signals
    vals = weights.values.flatten()
    nonzero = vals[~np.isclose(vals, 0.0)]
    if len(nonzero) > 0:
        # check if integer-like in {-1,1}
        is_signal_like = True
        for v in nonzero[:1000]:  # sample
            iv = round(float(v))
            if iv not in (-1, 0, 1) or not np.isclose(v, iv):
                is_signal_like = False
                break
        if is_signal_like:
            # convert like construct_portfolio (dollar neutral by default)
            out = pd.DataFrame(0.0, index=weights.index, columns=weights.columns)
            for idx in weights.index:
                row = weights.loc[idx]
                # count longs/shorts
                longs = row[row > 0]
                shorts = row[row < 0]
                n_long = int((row > 0).sum())
                n_short = int((row < 0).sum())
                if n_long > 0 and n_short > 0:
                    long_w = 1.0 / n_long
                    short_w = -1.0 / n_short
                    for c in weights.columns:
                        v = row[c]
                        if v > 0:
                            out.at[idx, c] = long_w
                        elif v < 0:
                            out.at[idx, c] = short_w
                elif n_long > 0:
                    long_w = 1.0 / n_long
                    for c in weights.columns:
                        if row[c] > 0:
                            out.at[idx, c] = long_w
                elif n_short > 0:
                    short_w = -1.0 / n_short
                    for c in weights.columns:
                        if row[c] < 0:
                            out.at[idx, c] = short_w
            weights = out

    # Enforce constraints row by row
    for idx in weights.index:
        row = weights.loc[idx].copy()

        # Check borrowability first
        for c in weights.columns:
            if row[c] < 0:  # short
                if not constraints.is_borrowable(c):
                    if getattr(constraints, "strict", False):
                        raise BABShortingError(f"Asset {c} not borrowable")
                    else:
                        row[c] = 0.0  # remove short if not strict

        # Per-asset short cap
        per_asset_cap = constraints.max_short_notional_per_asset
        if per_asset_cap is not None:
            cap = float(per_asset_cap)
            if cap < 0:
                raise BABShortingError("max_short_notional_per_asset must be non-negative")
            for c in weights.columns:
                if row[c] < 0:
                    if abs(row[c]) > cap + 1e-12:
                        row[c] = -cap  # scale down to cap

        # Total short exposure cap
        total_cap = constraints.max_short_exposure if constraints.max_short_exposure is not None else constraints.max_short_leverage
        if total_cap is not None:
            cap = float(total_cap)
            if cap < 0:
                raise BABShortingError("max_short_exposure must be non-negative")
            short_notional = float((-row).clip(lower=0.0).sum())
            if short_notional > cap + 1e-12 and short_notional > 1e-18:
                scale = cap / short_notional
                for c in weights.columns:
                    if row[c] < 0:
                        row[c] = row[c] * scale

        weights.loc[idx] = row

    # Final cleanup
    weights = weights.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return weights


# Common API names
enforce_shorting_constraints = apply_shorting_constraints
apply_borrow_constraints = apply_shorting_constraints
