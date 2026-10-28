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
        for i in range(len(common_idx)):
            if i < lookback - 1:
                out.iloc[i] = out.iloc[i] * 0.0  # or keep small; but make finite
                continue
            hist_ret = returns.iloc[max(0, i - lookback + 1):i + 1]
            # crude Kelly approx on portfolio series if possible
            port_hist = (hist_ret * base_w.iloc[max(0, i - lookback + 1):i + 1].values).sum(axis=1)
            mu = port_hist.mean()
            sig = port_hist.std(ddof=0)
            if sig < 1e-18 or not np.isfinite(sig):
                k = 0.0
            else:
                k = frac * mu / (sig * sig) if (sig * sig) > 0 else 0.0
            k = np.clip(k, -max_lev, max_lev)
            out.iloc[i] = base_w.iloc[i] * k
    elif isinstance(sizer, VolatilityTargetSizer):
        lookback = int(sizer.lookback)
        target_vol = float(sizer.target_vol)
        annualize = int(sizer.annualize)
        max_lev = float(sizer.max_leverage)
        for i in range(len(common_idx)):
            if i < lookback - 1:
                out.iloc[i] = base_w.iloc[i] * 0.0
                continue
            hist_ret = returns.iloc[max(0, i - lookback + 1):i + 1]
            port_hist = (hist_ret * base_w.iloc[max(0, i - lookback + 1):i + 1].values).sum(axis=1)
            sig_d = port_hist.std(ddof=0)
            if sig_d < 1e-18 or not np.isfinite(sig_d):
                scale = 0.0
            else:
                sig_ann = sig_d * np.sqrt(annualize)
                scale = target_vol / sig_ann if sig_ann > 0 else 0.0
            scale = np.clip(scale, 0.0, max_lev)
            out.iloc[i] = base_w.iloc[i] * scale
    elif isinstance(sizer, RiskParitySizer):
        lookback = int(sizer.lookback)
        max_lev = float(sizer.max_leverage)
        annualize = int(sizer.annualize)
        target_vol = getattr(sizer, "target_vol", None)
        for i in range(len(common_idx)):
            if i < lookback - 1:
                out.iloc[i] = base_w.iloc[i] * 0.0
                continue
            hist_ret = returns.iloc[max(0, i - lookback + 1):i + 1]
            # inverse vol weighting on base positions
            vols = hist_ret.std(ddof=0)
            vols = vols.replace([np.inf, -np.inf], np.nan).fillna(1e-18)
            inv_vol = 1.0 / vols
            inv_vol = inv_vol / inv_vol.sum() * (base_w.iloc[i].abs().sum()) if base_w.iloc[i].abs().sum() > 0 else inv_vol
            # apply directional signs from base weights
            signed = base_w.iloc[i].copy()
            # simple risk parity scaling
            w_rp = signed.abs()  # start from base magnitudes
            # better: scale by inv vol per asset contribution roughly
            scale = 1.0
            if target_vol is not None:
                port_hist = (hist_ret * (base_w.iloc[max(0, i - lookback + 1):i + 1] * inv_vol).values).sum(axis=1)  # rough
                sig_d = port_hist.std(ddof=0)
                if sig_d > 1e-18 and np.isfinite(sig_d):
                    scale = float(target_vol) / (sig_d * np.sqrt(annualize))
            scale = np.clip(scale, 0.0, max_lev)
            # blend
            out.iloc[i] = base_w.iloc[i] * inv_vol * scale
    else:
        raise BABSizingError("Unknown sizer type")

    out = out.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return out
