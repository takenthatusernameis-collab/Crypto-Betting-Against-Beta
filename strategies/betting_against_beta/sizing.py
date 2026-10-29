"""Dynamic position sizing for BAB strategy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
import pandas as pd

from .errors import BABDataError


class BABSizingError(BABDataError):
    """Raised when sizing parameters/inputs are invalid."""


class _BaseSizer:
    def __init__(self):
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False) and not name.startswith("_"):
            raise AttributeError(f"Cannot mutate frozen {self.__class__.__name__} attribute '{name}'")
        object.__setattr__(self, name, value)


@dataclass
class KellySizer(_BaseSizer):
    lookback: int = 60
    max_leverage: float = 1.0
    fraction: float = 1.0  # Kelly fraction multiplier

    def __post_init__(self):
        if not isinstance(self.lookback, int) or self.lookback < 1:
            raise BABSizingError("lookback must be >= 1")
        if not isinstance(self.max_leverage, (int, float)) or self.max_leverage <= 0:
            raise BABSizingError("max_leverage must be > 0")
        if not isinstance(self.fraction, (int, float)) or self.fraction < 0:
            raise BABSizingError("fraction must be >= 0")
        super().__init__()


@dataclass
class VolatilityTargetSizer(_BaseSizer):
    target_vol: float = 0.10  # annualized
    lookback: int = 60
    annualize: int = 252
    max_leverage: float = 2.0

    def __post_init__(self):
        if not isinstance(self.target_vol, (int, float)) or self.target_vol <= 0:
            raise BABSizingError("target_vol must be > 0")
        if not isinstance(self.lookback, int) or self.lookback < 1:
            raise BABSizingError("lookback must be >= 1")
        if not isinstance(self.annualize, int) or self.annualize < 1:
            raise BABSizingError("annualize must be >= 1")
        if not isinstance(self.max_leverage, (int, float)) or self.max_leverage <= 0:
            raise BABSizingError("max_leverage must be > 0")
        super().__init__()


@dataclass
class RiskParitySizer(_BaseSizer):
    lookback: int = 60
    max_leverage: float = 1.0
    target_vol: Optional[float] = None
    annualize: int = 252

    def __post_init__(self):
        if not isinstance(self.lookback, int) or self.lookback < 1:
            raise BABSizingError("lookback must be >= 1")
        if not isinstance(self.max_leverage, (int, float)) or self.max_leverage <= 0:
            raise BABSizingError("max_leverage must be > 0")
        if self.target_vol is not None and (not isinstance(self.target_vol, (int, float)) or self.target_vol <= 0):
            raise BABSizingError("target_vol must be > 0 when set")
        if not isinstance(self.annualize, int) or self.annualize < 1:
            raise BABSizingError("annualize must be >= 1")
        super().__init__()


def _get_base_weights(signals: pd.DataFrame) -> pd.DataFrame:
    """Construct equal-weight base portfolio from signals (dollar neutral)."""
    from .portfolio import construct_portfolio

    return construct_portfolio(signals, dollar_neutral=True)


def apply_position_sizing(signals: pd.DataFrame,
                          returns: pd.DataFrame = None,
                          betas: pd.DataFrame = None,
                          sizer: Union[KellySizer, VolatilityTargetSizer, RiskParitySizer, str] = None,
                          **kwargs) -> pd.DataFrame:
    """Apply position sizing to signals/returns and produce scaled weights."""
    if signals is None or not isinstance(signals, pd.DataFrame) or signals.empty:
        return pd.DataFrame()

    # Handle string shorthands
    if isinstance(sizer, str):
        s = str(sizer).lower()
        if s in ("kelly", "kelly_fraction"):
            sizer = KellySizer()
        elif s in ("vol_target", "volatility_target", "voltarget"):
            sizer = VolatilityTargetSizer()
        elif s in ("risk_parity", "riskparity", "rp"):
            sizer = RiskParitySizer()
        else:
            raise BABSizingError(f"Unknown sizer: {sizer}")

    base_w = _get_base_weights(signals)
    if returns is None:
        # No returns info; return base weights (clamped to finite)
        out = base_w.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        return out

    # Align
    returns = returns.copy()
    common_idx = base_w.index.intersection(returns.index)
    if len(common_idx) == 0:
        out = base_w.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        return out
    base_w = base_w.loc[common_idx]
    returns = returns.loc[common_idx]
    # ensure columns aligned
    for c in base_w.columns:
        if c not in returns.columns:
            returns[c] = 0.0
    returns = returns[base_w.columns]

    out = base_w.copy()

    if isinstance(sizer, KellySizer):
        lookback = int(sizer.lookback)
        max_lev = float(sizer.max_leverage)
        frac = float(sizer.fraction)
        out_arr = out.values.copy()
        base_arr = base_w.values
        for i in range(len(common_idx)):
            if i < lookback - 1:
                out_arr[i] = 0.0
                continue
            start = max(0, i - lookback + 1)
            hist_ret = returns.iloc[start:i + 1].values  # (T, A)
            base_hist = base_arr[start:i + 1]  # (T, A)
            port_hist = (hist_ret * base_hist).sum(axis=1)
            mu = port_hist.mean()
            sig = port_hist.std(ddof=0)
            if sig < 1e-18 or not np.isfinite(sig):
                k = 0.0
            else:
                k = frac * mu / (sig * sig) if (sig * sig) > 0 else 0.0
            k = np.clip(k, -max_lev, max_lev)
            out_arr[i] = base_arr[i] * k
        out = pd.DataFrame(out_arr, index=out.index, columns=out.columns)
    elif isinstance(sizer, VolatilityTargetSizer):
        lookback = int(sizer.lookback)
        target_vol = float(sizer.target_vol)
        annualize = int(sizer.annualize)
        max_lev = float(sizer.max_leverage)
        out_arr = out.values.copy()
        base_arr = base_w.values
        for i in range(len(common_idx)):
            if i < lookback - 1:
                out_arr[i] = 0.0
                continue
            start = max(0, i - lookback + 1)
            hist_ret = returns.iloc[start:i + 1].values
            base_hist = base_arr[start:i + 1]
            port_hist = (hist_ret * base_hist).sum(axis=1)
            sig_d = port_hist.std(ddof=0)
            if sig_d < 1e-18 or not np.isfinite(sig_d):
                scale = 0.0
            else:
                sig_ann = sig_d * np.sqrt(annualize)
                scale = target_vol / sig_ann if sig_ann > 0 else 0.0
            scale = np.clip(scale, 0.0, max_lev)
            out_arr[i] = base_arr[i] * scale
        out = pd.DataFrame(out_arr, index=out.index, columns=out.columns)
    elif isinstance(sizer, RiskParitySizer):
        lookback = int(sizer.lookback)
        max_lev = float(sizer.max_leverage)
        annualize = int(sizer.annualize)
        target_vol = getattr(sizer, "target_vol", None)
        out_arr = out.values.copy()
        base_arr = base_w.values
        for i in range(len(common_idx)):
            if i < lookback - 1:
                out_arr[i] = 0.0
                continue
            start = max(0, i - lookback + 1)
            hist_ret = returns.iloc[start:i + 1]
            vols = hist_ret.std(ddof=0)
            vols = vols.replace([np.inf, -np.inf], np.nan).fillna(1e-18)
            inv_vol = 1.0 / vols.values  # array
            # scale
            scale = 1.0
            if target_vol is not None:
                # approximate portfolio vol of risk-parity-like scaled base
                w_try = base_arr[start:i + 1] * inv_vol  # broadcast
                # normalize not strictly required; compute rough scale
                port_hist = (hist_ret.values * w_try).sum(axis=1)
                sig_d = port_hist.std(ddof=0)
                if sig_d > 1e-18 and np.isfinite(sig_d):
                    scale = float(target_vol) / (sig_d * np.sqrt(annualize))
            scale = np.clip(scale, 0.0, max_lev)
            out_arr[i] = base_arr[i] * inv_vol * scale
        out = pd.DataFrame(out_arr, index=out.index, columns=out.columns)

    out = out.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return out
