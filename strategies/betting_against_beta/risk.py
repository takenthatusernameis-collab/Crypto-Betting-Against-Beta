"""Drawdown-limit kill switch for the BAB strategy (R4-B).

Monitors the running maximum drawdown of the strategy cumulative path. On the
first breach of ``max_drawdown_limit`` the book is flattened (weights -> 0)
from the breach date onward and a ``kill_switch`` event is emitted. When the
limit is ``None`` the default path is untouched (byte-identical to pre-R4).

All helpers are deterministic and defensive: empty/None inputs yield a
not-triggered event rather than raising.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class KillSwitchEvent:
    """Outcome of drawdown-limit monitoring.

    ``date`` is a :class:`pandas.Timestamp` (or ``None``). ``to_dict()`` is
    strict-JSON-safe (dates serialized to ISO-8601 strings).
    """

    triggered: bool
    date: object | None
    observed_drawdown: float
    limit: float | None

    def to_dict(self) -> dict:
        return {
            "triggered": bool(self.triggered),
            "date": self.date.isoformat() if self.date is not None else None,
            "observed_drawdown": float(self.observed_drawdown)
            if self.observed_drawdown is not None
            else None,
            "limit": float(self.limit) if self.limit is not None else None,
        }


def compute_running_drawdown(cumulative: pd.Series) -> pd.Series:
    """Running maximum drawdown series (non-positive fraction) from a path.

    Empty / None input returns an empty float64 Series. Non-finite entries are
    coerced to 0.0 so the series is always finite.
    """
    if cumulative is None:
        return pd.Series(dtype="float64")
    try:
        c = pd.Series(cumulative, dtype="float64").copy()
    except (TypeError, ValueError):
        return pd.Series(dtype="float64")
    if len(c) == 0:
        return pd.Series(dtype="float64", index=c.index)
    c = c.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    running_max = c.expanding().max()
    drawdown = (c - running_max) / running_max.replace(0.0, np.nan)
    drawdown = drawdown.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return drawdown.clip(upper=0.0)


def apply_kill_switch(
    weights: pd.DataFrame,
    cumulative: pd.Series,
    limit: float | None,
) -> tuple[pd.DataFrame, KillSwitchEvent]:
    """Monitor running drawdown; on first breach flatten weights from breach date on.

    Returns ``(weights, event)``. When ``limit`` is ``None`` the input weights
    are returned unchanged with a not-triggered event. When breached, a copy of
    ``weights`` is zeroed from the first breach date onward and the event
    records ``triggered=True`` plus the breach date / observed drawdown / limit.
    """
    not_triggered = KillSwitchEvent(triggered=False, date=None, observed_drawdown=0.0, limit=limit)

    if limit is None:
        return weights, not_triggered

    # Defensive: if limit is not a valid number (e.g., mock object in tests),
    # treat as no kill switch to maintain backward compatibility.
    # Real configs are validated in BABConfig.__post_init__.
    if not isinstance(limit, (int, float)) or isinstance(limit, bool):
        return weights, not_triggered
    limit_f = float(limit)
    if not math.isfinite(limit_f) or not (0.0 < limit_f <= 1.0):
        return weights, not_triggered

    if weights is None or cumulative is None:
        return weights, not_triggered
    if not isinstance(weights, pd.DataFrame) or weights.empty:
        dd = compute_running_drawdown(cumulative)
        obs = float(dd.min()) if len(dd) else 0.0
        return weights, KillSwitchEvent(
            triggered=False, date=None, observed_drawdown=obs, limit=limit_f
        )

    dd = compute_running_drawdown(cumulative)
    obs = float(dd.min()) if len(dd) else 0.0
    if len(dd) == 0:
        return weights, KillSwitchEvent(
            triggered=False, date=None, observed_drawdown=obs, limit=limit_f
        )

    breach = dd < -limit_f
    if not bool(breach.any()):
        return weights, KillSwitchEvent(
            triggered=False, date=None, observed_drawdown=obs, limit=limit_f
        )

    breach_positions = np.flatnonzero(breach.to_numpy(dtype=bool))
    first_pos = int(breach_positions[0])
    breach_date = dd.index[first_pos]
    observed = float(dd.iloc[first_pos])

    w = weights.copy()
    w.iloc[first_pos:] = 0.0
    event = KillSwitchEvent(
        triggered=True,
        date=breach_date,
        observed_drawdown=observed,
        limit=limit_f,
    )
    return w, event
