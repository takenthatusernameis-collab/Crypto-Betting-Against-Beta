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
    notional_usd: Optional[float] = None
    price: Optional[float] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "asset": self.asset,
            "target_weight": float(self.target_weight),
            "current_weight": float(self.current_weight),
            "order_weight": float(self.order_weight),
            "notional_usd": self.notional_usd,
            "price": self.price,
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

    Every intent fills in full at the intent's price (or target weight if no
    price). Records every submitted intent and produced fill. No slippage,
    no partial fills, no network — suitable for deterministic tests and
    paper-trading dry runs.
    """

    def __init__(self, prices_df: Optional[pd.DataFrame] = None) -> None:
        self.prices = prices_df
        self.submitted: list[OrderBatch] = []
        self.fills: list[dict] = []

    def submit_intents(self, batch: OrderBatch) -> list[dict]:
        self.submitted.append(batch)
        fills: list[dict] = []
        for intent in batch.intents:
            fill = {
                "date": intent.date,
                "asset": intent.asset,
                "filled_weight": float(intent.target_weight),
                "order_weight": float(intent.order_weight),
                "price": intent.price,
                "notional_usd": intent.notional_usd,
                "slippage": 0.0,
                "status": "filled",
            }
            fills.append(fill)
            self.fills.append(fill)  # kept for test inspection
        return fills  # returns fills for this batch only

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
                    "filled_weight": float(intent.target_weight),
                    "order_weight": float(intent.order_weight),
                    "price": intent.price,
                    "notional_usd": intent.notional_usd,
                    "slippage": 0.0,
                    "status": "filled",
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
            if c in price_map:
                p = price_map[c].get(date_key)
                if p is not None:
                    try:
                        price = float(p)
                        notional = abs(order_w) * price
                    except (TypeError, ValueError):
                        price = None
            intents.append(
                OrderIntent(
                    date=date_key,
                    asset=c,
                    target_weight=target,
                    current_weight=current,
                    order_weight=order_w,
                    notional_usd=notional,
                    price=price,
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
