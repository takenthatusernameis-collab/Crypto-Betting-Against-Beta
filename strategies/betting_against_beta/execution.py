"""Execution adapter abstraction for BAB strategy (R5-A).

Defines an order-intent dataclass and an ExecutionAdapter interface with
paper + injectable/mock implementations. When BABStrategy is constructed
without an adapter (default), run() behaves exactly as before — byte-identical
default path. When an adapter is configured, order intents are generated from
period-to-period weight changes and submitted to the adapter; fills are
recorded on the result for downstream reconciliation (R5-B / R5-C).

No network is used by any implementation.
"""

from __future__ import annotations

import contextlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class OrderIntent:
    """A single asset's order intent for a period.

    Strict-JSON-safe: every field is a primitive (str, float, int, bool, None)
    or a dict of primitives.
    """

    date: str
    asset: str
    target_weight: float
    current_weight: float
    order_weight: float  # target_weight - current_weight
    requested_weight: float | None = None  # = order_weight; what the adapter is asked to fill
    notional_usd: float | None = None
    price: float | None = None
    adv_usd: float | None = None  # average daily volume in USD for this asset
    max_participation: float | None = None  # participation cap in (0,1]
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.requested_weight is None:
            object.__setattr__(self, "requested_weight", self.order_weight)

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "asset": self.asset,
            "target_weight": float(self.target_weight),
            "current_weight": float(self.current_weight),
            "order_weight": float(self.order_weight),
            "requested_weight": float(self.requested_weight),
            "notional_usd": self.notional_usd,
            "price": self.price,
            "adv_usd": self.adv_usd,
            "max_participation": self.max_participation,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class OrderBatch:
    """All order intents for a single period (date)."""

    date: str
    intents: tuple[OrderIntent, ...] = ()

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "intents": [i.to_dict() for i in self.intents],
        }


@runtime_checkable
class ExecutionAdapter(Protocol):
    """Adapter interface for order-intent submission / execution abstraction.

    Implementations must be deterministic and must not perform network I/O.
    """

    def submit_intents(self, batch: OrderBatch) -> list[dict]:
        """Submit order intents for one period; return per-intent fill records."""
        ...

    def flush(self) -> list[dict]:
        """Flush buffered fills; return any remaining fill records."""
        ...


_DEFAULT_MAX_PARTICIPATION = 0.10


class PaperAdapter:
    """Deterministic paper-trading adapter.

    Default path (no ``prices_df``/``adv_usd``/``partial_fill``): every intent
    fills in full at the intent's price, slippage = 0.0, status = "filled" —
    byte-identical to the pre-R5-E behavior.

    Realism path (``partial_fill=True`` with ``prices_df`` and ``adv_usd``
    supplied): deterministic partial-fill modeling via a ``max_participation``
    cap, plus sqrt-impact slippage.  Fill records expose
    ``requested_weight``, ``filled_weight``, ``fill_ratio``, ``order_weight``,
    ``notional_usd``, ``price``, ``slippage``, ``status``, and an explicit
    ``reason`` where applicable.
    """

    def __init__(
        self,
        prices_df: pd.DataFrame | None = None,
        adv_usd: object | None = None,
        partial_fill: bool = False,
        max_participation: float = _DEFAULT_MAX_PARTICIPATION,
    ) -> None:
        self.prices = prices_df
        self.adv_usd = adv_usd
        self.partial_fill = bool(partial_fill)
        self.max_participation = float(max_participation)
        self.submitted: list[OrderBatch] = []
        self.fills: list[dict] = []

    def _price_for(self, date_key: str, asset: str) -> float | None:
        if self.prices is None or asset not in self.prices.columns:
            return None
        try:
            sub = self.prices[asset]
            if date_key in sub.index:
                v = sub.loc[date_key]
                return float(v) if pd.notna(v) else None
            ts = pd.Timestamp(date_key)
            if ts in sub.index:
                v = sub.loc[ts]
                return float(v) if pd.notna(v) else None
        except (TypeError, ValueError, KeyError):
            pass
        return None

    def _adv_for(self, date_key: str, asset: str) -> float | None:
        if self.adv_usd is None:
            return None
        try:
            if isinstance(self.adv_usd, dict):
                v = self.adv_usd.get(asset)
                return float(v) if v is not None else None
            if isinstance(self.adv_usd, pd.Series):
                if asset in self.adv_usd.index:
                    v = self.adv_usd.loc[asset]
                    return float(v) if v is not None and pd.notna(v) else None
                # A date-indexed Series (per-period ADV) is matched by date.
                return self._adv_from_frame_value(self.adv_usd, date_key)
            if isinstance(self.adv_usd, pd.DataFrame):
                if asset in self.adv_usd.columns:
                    return self._adv_from_frame_value(self.adv_usd[asset], date_key)
                if asset in self.adv_usd.index:
                    return self._adv_from_frame_value(self.adv_usd.loc[asset], date_key)
        except (TypeError, ValueError, KeyError):
            pass
        return None

    @staticmethod
    def _adv_from_frame_value(sub, date_key: str) -> float | None:
        """Look up one ADV value by ISO date, then by Timestamp, else None."""
        try:
            if date_key in sub.index:
                v = sub.loc[date_key]
                if isinstance(v, pd.Series):
                    v = v.iloc[0]
                return float(v) if v is not None and pd.notna(v) else None
        except (TypeError, ValueError, KeyError):
            pass
        try:
            ts = pd.Timestamp(date_key)
            if ts in sub.index:
                v = sub.loc[ts]
                if isinstance(v, pd.Series):
                    v = v.iloc[0]
                return float(v) if v is not None and pd.notna(v) else None
        except (TypeError, ValueError, KeyError):
            pass
        return None

    def submit_intents(self, batch: OrderBatch) -> list[dict]:
        self.submitted.append(batch)
        fills: list[dict] = []
        for intent in batch.intents:
            date_key = intent.date
            asset = intent.asset
            order_w = float(intent.order_weight)
            requested_w = float(intent.requested_weight)
            # Intent-level data (populated by order_batches_from_weights) takes
            # precedence; adapter-level prices_df/adv_usd are fallbacks.
            price = intent.price
            if price is None and self.prices is not None:
                price = self._price_for(date_key, asset)
            notional = intent.notional_usd
            if notional is None and price is not None:
                notional = abs(order_w) * price
            adv = intent.adv_usd
            if adv is None and self.adv_usd is not None:
                adv = self._adv_for(date_key, asset)
            max_participation = intent.max_participation
            if max_participation is None:
                max_participation = self.max_participation

            # Realism path: intent carries price + adv_usd + max_participation
            # (populated by order_batches_from_weights) and notional is positive.
            # Otherwise default full-fill / zero-slippage behavior
            # (byte-identical to pre-R5-E).
            realism = (
                self.partial_fill
                and price is not None
                and adv is not None
                and adv > 0
                and max_participation is not None
                and notional is not None
                and notional > 0
            )

            if not realism:
                fill = {
                    "date": date_key,
                    "asset": asset,
                    "requested_weight": requested_w,
                    "filled_weight": order_w,
                    "fill_ratio": 1.0,
                    "order_weight": order_w,
                    "notional_usd": notional,
                    "price": price,
                    "adv_usd": adv,
                    "max_participation": max_participation,
                    "participation": (
                        float(notional / adv)
                        if adv is not None and adv > 0 and notional is not None
                        else None
                    ),
                    "slippage": 0.0,
                    "status": "filled",
                    "reason": None,
                }
            else:
                participation = notional / adv
                if participation > max_participation:
                    fill_ratio = max(max_participation / participation, 1e-12)
                    fill_ratio = min(fill_ratio, 1.0)
                else:
                    fill_ratio = 1.0
                filled_w = order_w * fill_ratio
                slip = 0.0005 * math.sqrt(min(participation, max_participation))
                slip = min(slip, 0.01)
                status = "partial" if fill_ratio < 1.0 - 1e-12 else "filled"
                reason = "participation_cap" if status == "partial" else None
                fill = {
                    "date": date_key,
                    "asset": asset,
                    "requested_weight": requested_w,
                    "filled_weight": filled_w,
                    "fill_ratio": float(fill_ratio),
                    "order_weight": order_w,
                    "notional_usd": notional,
                    "price": price,
                    "adv_usd": adv,
                    "max_participation": max_participation,
                    "participation": float(participation),
                    "slippage": float(slip),
                    "status": status,
                    "reason": reason,
                }
            fills.append(fill)
            self.fills.append(fill)
        return fills

    def flush(self) -> list[dict]:
        # All fills are already returned by submit_intents; nothing buffered.
        return []


class MockAdapter:
    """Injectable mock adapter for tests.

    Records every submitted intent. Returns canned fills from a
    ``fill_map`` keyed by ``(date, asset)``, or from a ``fill_fn`` callable
    receiving the ``OrderIntent``. Falls back to a full-fill paper fill when
    neither provides a fill for an intent.
    """

    def __init__(
        self,
        fill_map: dict | None = None,
        fill_fn=None,
    ) -> None:
        self.fill_map = dict(fill_map or {})
        self.fill_fn = fill_fn
        self.submitted: list[OrderBatch] = []
        self.fills: list[dict] = []

    def submit_intents(self, batch: OrderBatch) -> list[dict]:
        self.submitted.append(batch)
        fills: list[dict] = []
        for intent in batch.intents:
            key = (intent.date, intent.asset)
            if self.fill_fn is not None:
                fill = self.fill_fn(intent)
            elif key in self.fill_map:
                fill = dict(self.fill_map[key])
            else:
                fill = {
                    "date": intent.date,
                    "asset": intent.asset,
                    "requested_weight": float(intent.requested_weight),
                    "filled_weight": float(intent.order_weight),
                    "fill_ratio": 1.0,
                    "order_weight": float(intent.order_weight),
                    "price": intent.price,
                    "notional_usd": intent.notional_usd,
                    "slippage": 0.0,
                    "status": "filled",
                    "reason": None,
                }
            fills.append(fill)
            self.fills.append(fill)  # kept for test inspection
        return fills  # returns fills for this batch only

    def flush(self) -> list[dict]:
        # All fills are already returned by submit_intents; nothing buffered.
        return []


def configure_paper_adapter(adapter: PaperAdapter, strategy) -> PaperAdapter:
    """Populate a bare ``PaperAdapter`` from the strategy's resolved config.

    R5-E consumes the already-shipped R3 cost-model knobs so the adapter layer
    stops being a stub: ``prices``/``adv_usd`` come from the config-resolved
    cost model, and ``partial_fill``/``max_participation`` come from the config.
    Never overrides values the caller set explicitly on the adapter.

    Returns the same adapter for convenient inline construction.
    """
    cfg = getattr(strategy, "config", None)
    if cfg is None:
        return adapter
    resolver = getattr(strategy, "_resolve_cost_model", None)
    prices = adv = None
    if callable(resolver):
        try:
            _model, prices, adv = resolver(cfg)
        except Exception:
            prices = adv = None
    if prices is None:
        prices = getattr(cfg, "prices", None)
    if adv is None:
        adv = getattr(cfg, "adv_usd", None)
    if adapter.prices is None:
        adapter.prices = prices
    if adapter.adv_usd is None:
        adapter.adv_usd = adv
    cfg_partial = bool(getattr(cfg, "partial_fill", False))
    if cfg_partial:
        adapter.partial_fill = True
    # Only adopt the config cap when the caller left the adapter at its
    # default; an explicitly chosen cap wins over the config value.
    cfg_cap = getattr(cfg, "max_participation", None)
    if cfg_cap is not None and adapter.max_participation == _DEFAULT_MAX_PARTICIPATION:
        with contextlib.suppress(TypeError, ValueError):
            adapter.max_participation = float(cfg_cap)
    return adapter


def _date_key(date) -> str:
    """Canonical ISO-8601 date key shared by intents, batches and fills."""
    try:
        return pd.Timestamp(date).isoformat()
    except Exception:
        return str(date)


def _finite(value, default=0.0):
    """Coerce ``value`` to a finite float, returning ``default`` on failure.

    The try/except lives outside any loop so it does not trigger PERF203.
    """
    try:
        v = float(value)
    except (TypeError, ValueError):
        return default
    return v if math.isfinite(v) else default


def _as_timestamp(value):
    """Coerce ``value`` to a Timestamp, returning None on failure.

    Kept out of loop bodies to avoid PERF203.
    """
    try:
        return pd.Timestamp(value)
    except Exception:
        return None


def order_batches_from_weights(
    weights: pd.DataFrame,
    prices_df: pd.DataFrame | None = None,
    adv_usd: object | None = None,
    max_participation: float | None = None,
) -> list[OrderBatch]:
    """Build deterministic OrderBatch list from a weights DataFrame.

    One batch per date. For each non-zero weight change (target - previous),
    emit an OrderIntent. Columns are sorted for deterministic ordering. Prices
    and ADV are looked up per (date, asset) when provided.

    Strict-JSON-safe output: dates serialized to ISO-8601 strings; all numeric
    values are finite floats or None.
    """
    if not isinstance(weights, pd.DataFrame) or weights.empty:
        return []

    w = weights.sort_index()
    cols = [str(c) for c in sorted(w.columns)]
    idx = list(w.index)
    n = len(idx)

    # Align prices to weights universe (sorted, deterministic). Keyed by the
    # same ISO-8601 date string used on OrderIntent, so lookups always hit.
    price_map: dict = {}
    if prices_df is not None:
        prices = prices_df.sort_index()
        for c in cols:
            if c in prices.columns:
                sub = prices[c].reindex(idx)
                price_map[c] = {_date_key(k): v for k, v in sub.to_dict().items()}

    # Align adv_usd to weights universe (sorted, deterministic). Supports
    # dict (asset-indexed), Series (asset-indexed), or DataFrame (date x asset).
    adv_map: dict = {}
    if adv_usd is not None:
        try:
            if isinstance(adv_usd, dict):
                for c in cols:
                    v = adv_usd.get(c)
                    if v is not None:
                        with contextlib.suppress(TypeError, ValueError):
                            adv_map[c] = float(v)
            elif isinstance(adv_usd, pd.Series):
                for c in cols:
                    if c in adv_usd.index:
                        v = adv_usd.loc[c]
                        with contextlib.suppress(TypeError, ValueError):
                            adv_map[c] = float(v)
            elif isinstance(adv_usd, pd.DataFrame):
                adv_df = adv_usd.sort_index()
                for c in cols:
                    if c in adv_df.columns:
                        sub = adv_df[c].reindex(idx)
                        adv_map[c] = {_date_key(k): v for k, v in sub.to_dict().items()}
        except Exception:
            adv_map = {}

    batches: list[OrderBatch] = []
    prev = dict.fromkeys(cols, 0.0)
    for t in range(n):
        date = idx[t]
        try:
            date_key = pd.Timestamp(date).isoformat()
        except Exception:
            date_key = str(date)
        row_w = w.iloc[t]
        intents: list[OrderIntent] = []
        for c in cols:
            try:
                target = float(row_w[c])
            except (TypeError, ValueError):
                target = 0.0
            if not math.isfinite(target):
                target = 0.0
            current = prev.get(c, 0.0)
            order_w = target - current
            if order_w == 0.0:
                prev[c] = target
                continue
            notional = None
            price = None
            intent_adv = None
            if c in price_map:
                p = price_map[c].get(date_key)
                if p is not None:
                    try:
                        price = float(p)
                        notional = abs(order_w) * price
                    except (TypeError, ValueError):
                        price = None
            if c in adv_map:
                adv_entry = adv_map[c]
                intent_adv = adv_entry.get(date_key) if isinstance(adv_entry, dict) else adv_entry
                if intent_adv is not None:
                    try:
                        intent_adv = float(intent_adv)
                    except (TypeError, ValueError):
                        intent_adv = None
            intents.append(
                OrderIntent(
                    date=date_key,
                    asset=c,
                    target_weight=target,
                    current_weight=current,
                    order_weight=order_w,
                    requested_weight=order_w,
                    notional_usd=notional,
                    price=price,
                    adv_usd=intent_adv,
                    max_participation=max_participation,
                )
            )
            prev[c] = target
        if intents:
            batches.append(OrderBatch(date=date_key, intents=tuple(intents)))
    return batches


def _sanitize_for_json(obj):
    """Recursively coerce to strict-JSON-safe primitives."""
    if obj is None:
        return None
    if isinstance(obj, bool):
        return bool(obj)
    if isinstance(obj, int):
        return int(obj)
    if isinstance(obj, float):
        return 0.0 if not math.isfinite(obj) else float(obj)
    if isinstance(obj, str):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(v) for v in obj]
    if isinstance(obj, dict):
        return {str(k): _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, (pd.Series, pd.Index)):
        return [_sanitize_for_json(v) for v in obj.tolist()]
    try:
        import numpy as _np

        if isinstance(obj, _np.ndarray):
            return [_sanitize_for_json(v) for v in obj.tolist()]
        if isinstance(obj, (_np.integer,)):
            return int(obj)
        if isinstance(obj, (_np.floating,)):
            f = float(obj)
            return 0.0 if not math.isfinite(f) else f
        if isinstance(obj, (_np.bool_,)):
            return bool(obj)
    except ImportError:
        pass
    return str(obj)


def execution_payload_to_json(payload: dict) -> str:
    """Serialize an execution payload to strict JSON (allow_nan=False)."""
    return json.dumps(_sanitize_for_json(payload), indent=2, default=str, allow_nan=False)


# ---------------------------------------------------------------------------
# P8: canonical execution types + paper-trading engine
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Order:
    """A single timestamped order emitted by the paper-trading engine.

    Strict-JSON-safe: every field is a primitive or a dict of primitives.
    """

    date: str
    asset: str
    side: str  # "buy" | "sell"
    weight: float  # signed target weight for this asset
    price: float | None = None
    notional_usd: float | None = None
    status: str = "pending"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "asset": self.asset,
            "side": self.side,
            "weight": float(self.weight),
            "price": self.price,
            "notional_usd": self.notional_usd,
            "status": self.status,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class Fill:
    """A single simulated fill emitted by the paper-trading engine."""

    date: str
    asset: str
    side: str
    weight: float  # filled weight
    price: float | None = None
    notional_usd: float | None = None
    slippage: float = 0.0
    status: str = "filled"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "asset": self.asset,
            "side": self.side,
            "weight": float(self.weight),
            "price": self.price,
            "notional_usd": self.notional_usd,
            "slippage": float(self.slippage),
            "status": self.status,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class StrategyDiagnostics:
    """Per-rebalance signal/regime diagnostics.

    Emitted once per rebalance date; persisted to diagnostics.jsonl alongside
    paper fills and included in ExecutionReport.
    """

    date: str
    beta_mean: float | None = None
    beta_median: float | None = None
    beta_std: float | None = None
    beta_min: float | None = None
    beta_max: float | None = None
    long_beta_boundary: float | None = None
    short_beta_boundary: float | None = None
    long_assets: list[str] = field(default_factory=list)
    short_assets: list[str] = field(default_factory=list)
    n_long: int = 0
    n_short: int = 0
    turnover: float | None = None
    hhi: float | None = None
    beta_neutrality_error: float | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "beta_mean": self.beta_mean,
            "beta_median": self.beta_median,
            "beta_std": self.beta_std,
            "beta_min": self.beta_min,
            "beta_max": self.beta_max,
            "long_beta_boundary": self.long_beta_boundary,
            "short_beta_boundary": self.short_beta_boundary,
            "long_assets": list(self.long_assets),
            "short_assets": list(self.short_assets),
            "n_long": int(self.n_long),
            "n_short": int(self.n_short),
            "turnover": self.turnover,
            "hhi": self.hhi,
            "beta_neutrality_error": self.beta_neutrality_error,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ExecutionReport:
    """Deterministic execution report produced by PaperExecutionEngine."""

    mode: str
    n_orders: int
    n_fills: int
    orders: list[Order] = field(default_factory=list)
    fills: list[Fill] = field(default_factory=list)
    diagnostics: list[StrategyDiagnostics] = field(default_factory=list)
    pnl: float | None = None
    backtest_pnl: float | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "n_orders": int(self.n_orders),
            "n_fills": int(self.n_fills),
            "orders": [o.to_dict() for o in self.orders],
            "fills": [f.to_dict() for f in self.fills],
            "diagnostics": [d.to_dict() for d in self.diagnostics],
            "pnl": self.pnl,
            "backtest_pnl": self.backtest_pnl,
            "metadata": self.metadata,
        }


def _write_jsonl(path, records) -> None:
    """Write strict-JSON-safe records, one per line, creating parent dirs."""
    out = Path(path)
    parent = out.parent
    if str(parent) and str(parent) != ".":
        parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(_sanitize_for_json(rec), allow_nan=False) + "\n")


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return float(default)
        f = float(value)
        return f if math.isfinite(f) else float(default)
    except (TypeError, ValueError):
        return float(default)


class PaperExecutionEngine:
    """Deterministic paper-trading engine (dry-run, no network).

    Consumes BABStrategy weights, emits timestamped orders/fills to a local
    JSONL log, computes per-rebalance StrategyDiagnostics, and reconciles
    paper P&L against the backtest. Reuses OrderIntent/OrderBatch/PaperAdapter.
    """

    def __init__(
        self,
        mode: str = "paper",
        prices_df: pd.DataFrame | None = None,
        adv_usd: object | None = None,
        partial_fill: bool = False,
        max_participation: float = _DEFAULT_MAX_PARTICIPATION,
        log_path: str | Path | None = None,
        diagnostics_path: str | Path | None = None,
    ) -> None:
        if mode != "paper":
            raise ValueError(f"PaperExecutionEngine only supports mode='paper', got {mode!r}")
        self.mode = mode
        self.max_participation = float(max_participation)
        self.adapter = PaperAdapter(
            prices_df=prices_df,
            adv_usd=adv_usd,
            partial_fill=partial_fill,
            max_participation=max_participation,
        )
        self.log_path = Path(log_path) if log_path else None
        self.diagnostics_path = Path(diagnostics_path) if diagnostics_path else None
        self.orders: list[Order] = []
        self.fills: list[Fill] = []
        self.diagnostics: list[StrategyDiagnostics] = []

    def _diagnostics_for_date(
        self,
        date_key: str,
        weights_row,
        betas_row,
        prev_weights: dict,
    ) -> StrategyDiagnostics:
        w: dict = {}
        for asset in weights_row.index:
            w[asset] = _finite(weights_row[asset])
        long_assets = sorted(a for a, v in w.items() if v > 0)
        short_assets = sorted(a for a, v in w.items() if v < 0)
        turnover = sum(abs(v - prev_weights.get(a, 0.0)) for a, v in w.items())
        gross = sum(abs(v) for v in w.values())
        hhi = sum((v / gross) ** 2 for v in w.values()) if gross > 0 else 0.0

        beta_mean = beta_median = beta_std = beta_min = beta_max = None
        long_beta_boundary = short_beta_boundary = None
        beta_neutrality_error = None
        if betas_row is not None:
            bv: dict = {}
            try:
                assets = list(betas_row.index)
            except AttributeError:
                assets = []
            for a in assets:
                bv[a] = _finite(betas_row[a])
            if bv:
                vals = sorted(bv.values())
                n = len(vals)
                beta_mean = float(np.mean(vals))
                beta_median = float(np.median(vals))
                beta_std = float(np.std(vals))
                beta_min = float(vals[0])
                beta_max = float(vals[-1])
                li = max(0, min(n - 1, int(n * 0.3)))
                si = max(0, min(n - 1, int(n * (1 - 0.3))))
                long_beta_boundary = float(vals[li])
                short_beta_boundary = float(vals[si])
                port_beta = sum(w.get(a, 0.0) * bv.get(a, 0.0) for a in bv)
                beta_neutrality_error = abs(port_beta)

        return StrategyDiagnostics(
            date=date_key,
            beta_mean=_safe_float(beta_mean),
            beta_median=_safe_float(beta_median),
            beta_std=_safe_float(beta_std),
            beta_min=_safe_float(beta_min),
            beta_max=_safe_float(beta_max),
            long_beta_boundary=_safe_float(long_beta_boundary),
            short_beta_boundary=_safe_float(short_beta_boundary),
            long_assets=long_assets,
            short_assets=short_assets,
            n_long=len(long_assets),
            n_short=len(short_assets),
            turnover=_safe_float(turnover),
            hhi=_safe_float(hhi),
            beta_neutrality_error=_safe_float(beta_neutrality_error),
        )

    def _paper_pnl(self, returns_df) -> float | None:
        if (
            returns_df is None
            or not isinstance(returns_df, pd.DataFrame)
            or returns_df.empty
            or not self.fills
        ):
            return None
        ret = returns_df.sort_index()
        dates = list(ret.index)
        import bisect

        total = 0.0
        for f in self.fills:
            try:
                ts = pd.Timestamp(f.date)
            except Exception:
                continue
            j = bisect.bisect_right(dates, ts)
            if j >= len(dates):
                continue
            nxt = dates[j]
            asset = f.asset
            if asset not in ret.columns:
                continue
            try:
                r = float(ret.loc[nxt, asset])
            except (KeyError, TypeError, ValueError):
                continue
            if not math.isfinite(r):
                continue
            total += float(f.weight) * r
        return _safe_float(total)

    def _persist(self, report: ExecutionReport) -> None:
        if self.log_path is not None:
            _write_jsonl(self.log_path, [f.to_dict() for f in self.fills])
        if self.diagnostics_path is not None:
            _write_jsonl(self.diagnostics_path, [d.to_dict() for d in self.diagnostics])

    def execute(
        self,
        weights_df: pd.DataFrame,
        betas_df: pd.DataFrame | None = None,
        signals_df: pd.DataFrame | None = None,
        returns_df: pd.DataFrame | None = None,
        backtest_pnl: float | None = None,
    ) -> ExecutionReport:
        """Run paper execution over ``weights_df`` and return an ExecutionReport.

        One order per non-zero weight change; fills simulated by the PaperAdapter
        (full fill at intent price by default, participation-capped partial
        fills when prices/adv_usd are configured). Diagnostics are computed per
        rebalance date and both fills and diagnostics are persisted to JSONL.
        """
        if not isinstance(weights_df, pd.DataFrame) or weights_df.empty:
            report = ExecutionReport(
                mode=self.mode, n_orders=0, n_fills=0, backtest_pnl=backtest_pnl
            )
            self._persist(report)
            return report

        w = weights_df.sort_index()
        cols = [str(c) for c in sorted(w.columns)]
        w = w[cols]
        idx = list(w.index)
        n = len(idx)

        betas = None
        if betas_df is not None and not betas_df.empty:
            betas = betas_df.sort_index()
            try:
                betas = betas.reindex(index=idx)
            except Exception:
                betas = None

        batches = order_batches_from_weights(w, max_participation=self.max_participation)
        batch_by_date = {b.date: b for b in batches}

        prev: dict = dict.fromkeys(cols, 0.0)
        for t in range(n):
            date = idx[t]
            ts = _as_timestamp(date)
            date_key = ts.isoformat() if ts is not None else str(date)
            row_w = w.iloc[t]
            cur: dict = {c: _finite(row_w[c]) for c in cols}

            betas_row = None
            if betas is not None and ts is not None and ts in betas.index:
                betas_row = betas.loc[ts]
            self.diagnostics.append(
                self._diagnostics_for_date(date_key, pd.Series(cur), betas_row, prev)
            )

            batch = batch_by_date.get(date_key)
            if batch is not None:
                fills = self.adapter.submit_intents(batch)
                for intent, fill in zip(batch.intents, fills):
                    side = "buy" if intent.order_weight > 0 else "sell"
                    self.orders.append(
                        Order(
                            date=intent.date,
                            asset=intent.asset,
                            side=side,
                            weight=intent.order_weight,
                            price=intent.price,
                            notional_usd=intent.notional_usd,
                            status="pending",
                        )
                    )
                    fill_weight = fill.get("filled_weight", 0.0)
                    fill_side = "buy" if fill_weight > 0 else "sell"
                    self.fills.append(
                        Fill(
                            date=fill.get("date", date_key),
                            asset=fill.get("asset", intent.asset),
                            side=fill_side,
                            weight=float(fill_weight or 0.0),
                            price=fill.get("price"),
                            notional_usd=fill.get("notional_usd"),
                            slippage=float(fill.get("slippage", 0.0) or 0.0),
                            status=fill.get("status", "filled"),
                        )
                    )
            prev = cur

        self.adapter.flush()
        report = ExecutionReport(
            mode=self.mode,
            n_orders=len(self.orders),
            n_fills=len(self.fills),
            orders=list(self.orders),
            fills=list(self.fills),
            diagnostics=list(self.diagnostics),
            pnl=self._paper_pnl(returns_df),
            backtest_pnl=backtest_pnl,
        )
        self._persist(report)
        return report
