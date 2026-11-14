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

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Optional, Protocol, runtime_checkable

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
    requested_weight: Optional[float] = None  # = order_weight; what the adapter is asked to fill
    notional_usd: Optional[float] = None
    price: Optional[float] = None
    adv_usd: Optional[float] = None  # average daily volume in USD for this asset
    max_participation: Optional[float] = None  # participation cap in (0,1]
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
        prices_df: Optional[pd.DataFrame] = None,
        adv_usd: Optional[object] = None,
        partial_fill: bool = False,
        max_participation: float = 0.10,
    ) -> None:
        self.prices = prices_df
        self.adv_usd = adv_usd
        self.partial_fill = bool(partial_fill)
        self.max_participation = float(max_participation)
        self.submitted: list[OrderBatch] = []
        self.fills: list[dict] = []

    def _price_for(self, date_key: str, asset: str) -> Optional[float]:
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

    def _adv_for(self, date_key: str, asset: str) -> Optional[float]:
        if self.adv_usd is None:
            return None
        try:
            if isinstance(self.adv_usd, dict):
                v = self.adv_usd.get(asset)
                return float(v) if v is not None else None
            if isinstance(self.adv_usd, pd.Series):
                v = self.adv_usd.get(asset)
                return float(v) if v is not None and pd.notna(v) else None
            if isinstance(self.adv_usd, pd.DataFrame):
                if asset in self.adv_usd.columns:
                    sub = self.adv_usd[asset]
                    if date_key in sub.index:
                        v = sub.loc[date_key]
                        return float(v) if pd.notna(v) else None
                    try:
                        ts = pd.Timestamp(date_key)
                        if ts in sub.index:
                            v = sub.loc[ts]
                            return float(v) if pd.notna(v) else None
                    except Exception:
                        pass
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
                price is not None
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
        fill_map: Optional[dict] = None,
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


def order_batches_from_weights(
    weights: pd.DataFrame,
    prices_df: Optional[pd.DataFrame] = None,
    adv_usd: Optional[object] = None,
    max_participation: Optional[float] = None,
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

    # Align prices to weights universe (sorted, deterministic).
    price_map: dict = {}
    if prices_df is not None:
        prices = prices_df.sort_index()
        for c in cols:
            if c in prices.columns:
                sub = prices[c].reindex(idx)
                price_map[c] = sub.to_dict()

    # Align adv_usd to weights universe (sorted, deterministic). Supports
    # dict (asset-indexed), Series (asset-indexed), or DataFrame (date x asset).
    adv_map: dict = {}
    if adv_usd is not None:
        try:
            if isinstance(adv_usd, dict):
                for c in cols:
                    v = adv_usd.get(c)
                    if v is not None:
                        try:
                            adv_map[c] = float(v)
                        except (TypeError, ValueError):
                            pass
            elif isinstance(adv_usd, pd.Series):
                for c in cols:
                    if c in adv_usd.index:
                        v = adv_usd.loc[c]
                        try:
                            adv_map[c] = float(v)
                        except (TypeError, ValueError):
                            pass
            elif isinstance(adv_usd, pd.DataFrame):
                adv_df = adv_usd.sort_index()
                for c in cols:
                    if c in adv_df.columns:
                        sub = adv_df[c].reindex(idx)
                        adv_map[c] = sub.to_dict()
        except Exception:
            adv_map = {}

    batches: list[OrderBatch] = []
    prev = {c: 0.0 for c in cols}
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
                if isinstance(adv_entry, dict):
                    intent_adv = adv_entry.get(date_key)
                else:
                    intent_adv = adv_entry
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
        import numpy as _np  # noqa: WPS433

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
