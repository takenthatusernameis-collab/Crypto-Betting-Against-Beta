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
from dataclasses import dataclass, field

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
    # P19-7: Class A (total contract) — non-coercible input -> empty series
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


# ---------------------------------------------------------------------------
# P9: Production-grade Risk Manager
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RiskLimits:
    """Risk limits for position and portfolio management.

    All limits are expressed as absolute values (non-negative).
    """

    max_gross_exposure: float = 1.0  # Maximum sum of absolute weights
    max_net_exposure: float = 1.0  # Maximum net weight (long - short)
    max_position_weight: float = 0.2  # Maximum weight per single asset
    max_position_age_days: int | None = None  # Maximum days a position can be held
    max_drawdown: float | None = None  # Maximum portfolio drawdown (0-1)
    max_daily_turnover: float | None = None  # Maximum daily turnover as fraction of portfolio
    max_concentration: float | None = None  # Maximum HHI concentration (0-1)
    allowed_assets: list[str] | None = None  # Whitelist of allowed assets
    blocked_assets: list[str] | None = None  # Blacklist of blocked assets

    def __post_init__(self) -> None:
        for field_name in (
            "max_gross_exposure",
            "max_net_exposure",
            "max_position_weight",
            "max_drawdown",
            "max_daily_turnover",
            "max_concentration",
        ):
            value = getattr(self, field_name)
            if value is not None:
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    raise ValueError(f"{field_name} must be a number, got {type(value)}")
                if not math.isfinite(value) or value < 0:
                    raise ValueError(f"{field_name} must be finite and non-negative, got {value}")
        if self.max_position_age_days is not None and (
            not isinstance(self.max_position_age_days, int) or self.max_position_age_days < 1
        ):
            raise ValueError("max_position_age_days must be a positive integer")


@dataclass(frozen=True)
class RiskEvent:
    """Risk event emitted by RiskManager.

    Strict-JSON-safe: every field is a primitive or a dict of primitives.
    """

    timestamp: str
    event_type: str  # "limit_breach" | "kill_switch" | "order_rejected" | "position_flattened"
    severity: str  # "info" | "warning" | "critical"
    message: str
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
        }


@dataclass(frozen=True)
class PreTradeCheckResult:
    """Result of a pre-trade risk check.

    Attributes:
        allowed: Whether the order batch is allowed as-is.
        modified_intents: Modified order intents if any (None means no changes).
        rejected_intents: Indices of rejected intents with reasons.
        events: Risk events generated during the check.
    """

    allowed: bool
    modified_intents: list[dict] | None = None
    rejected_intents: list[dict] = field(default_factory=list)
    events: list[RiskEvent] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "modified_intents": self.modified_intents,
            "rejected_intents": self.rejected_intents,
            "events": [e.to_dict() for e in self.events],
        }


def _finite(value, default=0.0):
    """Coerce value to finite float."""
    try:
        v = float(value)
    # P19-7: Class A (total contract) — non-coercible value -> default
    except (TypeError, ValueError):
        return default
    return v if math.isfinite(v) else default


def _compute_gross_exposure(weights: pd.Series) -> float:
    """Compute gross exposure (sum of absolute weights)."""
    return float(weights.abs().sum())


def _compute_net_exposure(weights: pd.Series) -> float:
    """Compute net exposure (sum of weights)."""
    return float(weights.sum())


def _compute_hhi(weights: pd.Series) -> float:
    """Compute Herfindahl-Hirschman Index (concentration)."""
    gross = _compute_gross_exposure(weights)
    if gross == 0:
        return 0.0
    return float(((weights.abs() / gross) ** 2).sum())


def _compute_turnover(current: pd.Series, target: pd.Series) -> float:
    """Compute turnover between current and target weights."""
    all_assets = set(current.index) | set(target.index)
    cur = current.reindex(all_assets, fill_value=0.0)
    tgt = target.reindex(all_assets, fill_value=0.0)
    return float((tgt - cur).abs().sum())


class RiskManager:
    """Production-grade risk manager for BAB strategy.

    Enforces per-asset, per-side, and portfolio-level limits.
    Integrates with PaperExecutionEngine and LiveExecutionAdapter via
    pre_trade_check(order_batch, current_positions, risk_limits).
    """

    def __init__(
        self,
        limits: RiskLimits | None = None,
        kill_switch_enabled: bool = True,
        current_prices: pd.DataFrame | None = None,
    ) -> None:
        self.limits = limits or RiskLimits()
        self.kill_switch_enabled = kill_switch_enabled
        self.current_prices = current_prices
        self.events: list[RiskEvent] = []
        self._position_ages: dict[str, int] = {}  # asset -> days held
        self._last_prices: dict[str, float] = {}
        self._kill_switch_triggered = False

    def _emit_event(
        self,
        event_type: str,
        severity: str,
        message: str,
        details: dict | None = None,
    ) -> RiskEvent:
        """Emit a risk event."""
        from pandas import Timestamp
        event = RiskEvent(
            timestamp=Timestamp.now(tz="UTC").isoformat(),
            event_type=event_type,
            severity=severity,
            message=message,
            details=details or {},
        )
        self.events.append(event)
        return event

    def _check_asset_limits(self, asset: str, target_weight: float) -> list[str]:
        """Check per-asset limits. Returns list of violation messages."""
        violations = []
        max_pos = self.limits.max_position_weight
        if abs(target_weight) > max_pos:
            violations.append(
                f"Asset {asset} weight {target_weight:.4f} exceeds max "
                f"position weight {max_pos:.4f}"
            )
        if self.limits.allowed_assets and asset not in self.limits.allowed_assets:
            violations.append(f"Asset {asset} not in allowed assets list")
        if self.limits.blocked_assets and asset in self.limits.blocked_assets:
            violations.append(f"Asset {asset} is blocked")
        return violations

    def _check_portfolio_limits(self, target_weights: pd.Series) -> list[str]:
        """Check portfolio-level limits. Returns list of violation messages."""
        violations = []
        gross = _compute_gross_exposure(target_weights)
        if gross > self.limits.max_gross_exposure:
            violations.append(
                f"Gross exposure {gross:.4f} exceeds max {self.limits.max_gross_exposure:.4f}"
            )
        net = _compute_net_exposure(target_weights)
        if abs(net) > self.limits.max_net_exposure:
            violations.append(
                f"Net exposure {net:.4f} exceeds max {self.limits.max_net_exposure:.4f}"
            )
        if self.limits.max_concentration is not None:
            hhi = _compute_hhi(target_weights)
            if hhi > self.limits.max_concentration:
                violations.append(
                    f"Concentration (HHI) {hhi:.4f} exceeds max {self.limits.max_concentration:.4f}"
                )
        return violations

    def _check_position_age(self, target_weights: pd.Series, date: str) -> list[str]:
        """Check position age limits. Returns list of violation messages."""
        violations = []
        if self.limits.max_position_age_days is None:
            return violations
        for asset, weight in target_weights.items():
            if weight != 0:
                self._position_ages[asset] = self._position_ages.get(asset, 0) + 1
                if self._position_ages[asset] > self.limits.max_position_age_days:
                    violations.append(
                        f"Asset {asset} position age {self._position_ages[asset]} days "
                        f"exceeds max {self.limits.max_position_age_days} days"
                    )
            else:
                self._position_ages.pop(asset, None)
        return violations

    def _check_drawdown(self, cumulative: pd.Series) -> tuple[bool, float]:
        """Check drawdown limit. Returns (breached, observed_drawdown)."""
        if self.limits.max_drawdown is None:
            return False, 0.0
        dd = compute_running_drawdown(cumulative)
        if len(dd) == 0:
            return False, 0.0
        obs = float(dd.min())
        breached = obs < -self.limits.max_drawdown
        return breached, obs

    def _check_daily_turnover(
        self, current_weights: pd.Series, target_weights: pd.Series
    ) -> tuple[bool, float]:
        """Check daily turnover limit. Returns (breached, turnover)."""
        if self.limits.max_daily_turnover is None:
            return False, 0.0
        turnover = _compute_turnover(current_weights, target_weights)
        breached = turnover > self.limits.max_daily_turnover
        return breached, turnover

    def pre_trade_check(
        self,
        order_batch,  # OrderBatch from execution module
        current_positions: pd.Series,
        cumulative: pd.Series | None = None,
        date: str | None = None,
    ) -> PreTradeCheckResult:
        """Pre-trade risk check for an order batch.

        Args:
            order_batch: OrderBatch containing OrderIntents for the period.
            current_positions: Current portfolio weights (asset -> weight).
            cumulative: Optional cumulative PnL series for drawdown check.
            date: Optional date string for position age tracking.

        Returns:
            PreTradeCheckResult with allowed/modified/rejected intents and events.
        """
        rejected = []
        events = []

        # Build target weights from order batch
        target_weights = current_positions.copy()
        for intent in order_batch.intents:
            target_weights[intent.asset] = intent.target_weight

        # Check asset-level limits
        for intent in order_batch.intents:
            violations = self._check_asset_limits(intent.asset, intent.target_weight)
            for v in violations:
                rejected.append(
                    {
                        "asset": intent.asset,
                        "reason": v,
                        "original_weight": intent.target_weight,
                    }
                )
                events.append(
                    self._emit_event(
                        "order_rejected",
                        "warning",
                        f"Asset limit violation for {intent.asset}",
                        {"asset": intent.asset, "violation": v},
                    )
                )

        # Remove rejected intents from target
        for r in rejected:
            target_weights[r["asset"]] = current_positions.get(r["asset"], 0.0)

        # Check portfolio-level limits
        port_violations = self._check_portfolio_limits(target_weights)
        for v in port_violations:
            events.append(
                self._emit_event(
                    "limit_breach",
                    "warning",
                    v,
                    {"limit_type": "portfolio"},
                )
            )
            # Reject the entire batch on portfolio limit breach
            rejected.append(
                {
                    "asset": "portfolio",
                    "reason": v,
                    "original_weight": 0.0,
                }
            )

        # Check position age
        if date is not None:
            age_violations = self._check_position_age(target_weights, date)
            events.extend(
                self._emit_event(
                    "limit_breach",
                    "warning",
                    v,
                    {"limit_type": "position_age"},
                )
                for v in age_violations
            )

        # Check drawdown
        if cumulative is not None:
            dd_breached, obs = self._check_drawdown(cumulative)
            if dd_breached:
                events.append(
                    self._emit_event(
                        "kill_switch",
                        "critical",
                        f"Drawdown limit breached: {obs:.4f} > {self.limits.max_drawdown:.4f}",
                        {"observed_drawdown": obs, "limit": self.limits.max_drawdown},
                    )
                )
                if self.kill_switch_enabled:
                    self._kill_switch_triggered = True
                    # Flatten all positions
                    target_weights = pd.Series(0.0, index=target_weights.index)
                    events.append(
                        self._emit_event(
                            "position_flattened",
                            "critical",
                            "Kill switch triggered: all positions flattened",
                            {"drawdown": obs, "limit": self.limits.max_drawdown},
                        )
                    )

        # Check daily turnover
        if date is not None:
            turnover_breached, turnover = self._check_daily_turnover(
                current_positions, target_weights
            )
            if turnover_breached:
                events.append(
                    self._emit_event(
                        "limit_breach",
                        "warning",
                        f"Daily turnover {turnover:.4f} exceeds max "
                        f"{self.limits.max_daily_turnover:.4f}",
                        {"turnover": turnover, "limit": self.limits.max_daily_turnover},
                    )
                )

        # Determine if any modifications were made
        has_modifications = not target_weights.equals(current_positions)
        modified_intents = None
        if has_modifications:
            modified_intents = []
            for asset in target_weights.index:
                if target_weights[asset] != current_positions.get(asset, 0.0):
                    modified_intents.append(
                        {
                            "asset": asset,
                            "original_weight": current_positions.get(asset, 0.0),
                            "adjusted_weight": target_weights[asset],
                        }
                    )

        allowed = len(rejected) == 0 and not self._kill_switch_triggered

        return PreTradeCheckResult(
            allowed=allowed,
            modified_intents=modified_intents,
            rejected_intents=rejected,
            events=events,
        )

    def check_kill_switch(self, cumulative: pd.Series) -> tuple[bool, KillSwitchEvent]:
        """Check if kill switch should be triggered based on drawdown.

        Returns (triggered, KillSwitchEvent).
        """
        if not self.kill_switch_enabled or self.limits.max_drawdown is None:
            return False, KillSwitchEvent(
                triggered=False, date=None, observed_drawdown=0.0, limit=None
            )
        breached, obs = self._check_drawdown(cumulative)
        if breached:
            self._kill_switch_triggered = True
            from pandas import Timestamp
            event = KillSwitchEvent(
                triggered=True,
                date=Timestamp.now(tz="UTC"),
                observed_drawdown=obs,
                limit=self.limits.max_drawdown,
            )
            self._emit_event(
                "kill_switch",
                "critical",
                f"Drawdown kill switch triggered: {obs:.4f}",
                {"observed_drawdown": obs, "limit": self.limits.max_drawdown},
            )
            return True, event
        return False, KillSwitchEvent(
            triggered=False, date=None, observed_drawdown=obs, limit=self.limits.max_drawdown
        )

    def flatten_positions(self, current_positions: pd.Series) -> pd.Series:
        """Flatten all positions (emergency kill switch).

        Returns zero weights for all assets.
        """
        self._emit_event(
            "position_flattened",
            "critical",
            "Emergency position flattening triggered",
            {"assets": list(current_positions.index)},
        )
        return pd.Series(0.0, index=current_positions.index)

    def get_events(self, since: str | None = None) -> list[RiskEvent]:
        """Get risk events, optionally filtered by timestamp."""
        if since is None:
            return list(self.events)
        from pandas import Timestamp
        since_ts = Timestamp(since)
        return [e for e in self.events if Timestamp(e.timestamp) >= since_ts]

    def clear_events(self) -> None:
        """Clear the event log."""
        self.events.clear()

    def update_prices(self, prices: pd.DataFrame) -> None:
        """Update current prices for mark-to-market."""
        self.current_prices = prices
        if prices is not None and not prices.empty:
            try:
                latest = prices.iloc[-1]
                for asset, price in latest.items():
                    if pd.notna(price):
                        self._last_prices[asset] = float(price)
            # P19-7: Class A (total contract) — malformed price row -> keep prior prices
            except Exception:
                pass

    def get_position_value(self, positions: pd.Series) -> float:
        """Get current portfolio value using latest prices."""
        if self.current_prices is None or self.current_prices.empty:
            return 0.0
        try:
            latest = self.current_prices.iloc[-1]
            value = 0.0
            for asset, weight in positions.items():
                if asset in latest.index:
                    price = latest[asset]
                    if pd.notna(price):
                        value += float(weight) * float(price)
            return value
        except Exception:  # P19-7: Class A (total contract) — non-finite/malformed value -> 0.0
            return 0.0
