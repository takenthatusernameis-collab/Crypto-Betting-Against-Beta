"""Modeled-vs-executed cost reconciliation and fill backtest reconciliation (R5-B / R5-C).

Compares modeled transaction costs (costs.py / TransactionCostModel) against
supplied executed-fill data, emitting per-period and aggregate deltas as a
strict-JSON-safe artifact. Also produces realized PnL / cost / equity series
from a fill / execution log and compares to the model backtest for the same
weights / prices window, surfacing mismatches explicitly.

All outputs are deterministic and strict-JSON-safe. No live data or network
is used.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from .costs import TransactionCostModel, compute_transaction_costs


@dataclass(frozen=True)
class ReconciliationResult:
    """Strict-JSON-safe reconciliation artifact (R5-B + R5-C)."""

    schema_version: str
    n_periods: int
    per_period: list[dict]
    aggregate: dict
    checksum: str

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "n_periods": self.n_periods,
            "per_period": self.per_period,
            "aggregate": self.aggregate,
            "checksum": self.checksum,
        }


def _checksum(payload: dict) -> str:
    payload_no_sum = {k: v for k, v in payload.items() if k != "checksum"}
    canonical = json.dumps(payload_no_sum, sort_keys=True, default=str, allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _sanitize(obj):
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
        return [_sanitize(v) for v in obj]
    if isinstance(obj, dict):
        return {str(k): _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, (pd.Series, pd.Index, np.ndarray)):
        return [_sanitize(v) for v in obj.tolist()]
    try:
        import numpy as _np  # noqa: WPS433

        if isinstance(obj, _np.integer):
            return int(obj)
        if isinstance(obj, _np.floating):
            f = float(obj)
            return 0.0 if not math.isfinite(f) else f
        if isinstance(obj, _np.bool_):
            return bool(obj)
    except ImportError:
        pass
    return str(obj)


def _fill_executed_weight(fill: dict) -> float:
    """Realized traded weight for a fill record.

    The execution adapters (R5-A/R5-E) emit ``filled_weight``/``fill_ratio``;
    the canonical R5-B/R5-C fill schema carries ``order_weight`` only. Use the
    explicit realized field when present, otherwise fall back to the ordered
    weight so legacy/canonical fills keep their shipped semantics. A rejected
    fill (``status`` indicating no execution) counts as zero traded weight.
    """
    status = str(fill.get("status", "") or "").lower()
    if status in {"rejected", "cancelled", "canceled", "unfilled", "failed"}:
        return 0.0
    for key in ("filled_weight", "fill_ratio", "order_weight"):
        if key in fill and fill.get(key) is not None:
            try:
                value = float(fill.get(key))
            except (TypeError, ValueError):
                continue
            if math.isfinite(value):
                if key == "fill_ratio":
                    requested = fill.get("requested_weight")
                    if requested is None:
                        requested = fill.get("order_weight", 0.0)
                    try:
                        return value * float(requested or 0.0)
                    except (TypeError, ValueError):
                        return 0.0
                return value
    return 0.0


def _fill_cost(fill: dict, transaction_costs: float, slippage: float) -> float:
    """Cost of a single fill as a fraction of portfolio value.

    Weights are fractions of a $1.0 portfolio, so cost fraction =
    |executed_weight| * (tx_rate + slippage_rate). Uses the realized executed
    weight (``filled_weight`` when the adapter reports partial fills), falling
    back to the ordered weight for canonical fill records, so partial/rejected
    fills are costed at what was actually executed.
    """
    executed_w = abs(_fill_executed_weight(fill))
    tx = float(fill.get("transaction_costs", transaction_costs) or transaction_costs)
    slip = float(fill.get("slippage", slippage) or slippage)
    return executed_w * (tx + slip)


def _date_key(date) -> str:
    try:
        return pd.Timestamp(date).isoformat()
    except Exception:
        return str(date)


def reconcile_costs(
    weights: pd.DataFrame,
    prices: Optional[pd.DataFrame] = None,
    adv_usd: Optional[object] = None,
    model: Optional[TransactionCostModel] = None,
    executed_fills: Optional[list[dict]] = None,
    transaction_costs: float = 0.0,
    slippage: float = 0.0,
) -> ReconciliationResult:
    """Compare modeled costs vs executed fills.

    Modeled cost per period = compute_transaction_costs(weights, weights_prev, prices, model, adv_usd)
    Executed cost per period = sum over fills on that date of fill cost.

    Deltas = executed - modeled per period. Aggregate = totals, mean, max abs,
    mismatch count (> 1e-12).
    """
    if model is None:
        model = TransactionCostModel(
            linear_fee=0.0, bid_ask_bps=0.0, impact_coefficient=0.0,
            borrow_bps_per_year=0.0, fixed_fee_per_trade=0.0,
        )

    empty_agg = {
        "n_periods": 0,
        "modeled_total": 0.0,
        "executed_total": 0.0,
        "delta_total": 0.0,
        "delta_mean": 0.0,
        "delta_max_abs": 0.0,
        "n_mismatches": 0,
    }
    if not isinstance(weights, pd.DataFrame) or weights.empty:
        payload = {
            "schema_version": "r5-reconcile-1",
            "n_periods": 0,
            "per_period": [],
            "aggregate": empty_agg,
        }
        return ReconciliationResult(
            schema_version="r5-reconcile-1",
            n_periods=0,
            per_period=[],
            aggregate=empty_agg,
            checksum=_checksum(payload),
        )

    w = weights.sort_index()
    idx = list(w.index)

    # Modeled costs per period.
    weights_prev = w.shift(1).fillna(0.0)
    modeled_series = compute_transaction_costs(w, weights_prev, prices, model, adv_usd=adv_usd)
    modeled_series = modeled_series.reindex(idx).fillna(0.0)

    # Executed costs grouped by date.
    executed_by_date: dict[str, float] = {}
    if executed_fills:
        for fill in executed_fills:
            date = _date_key(fill.get("date", ""))
            executed_by_date[date] = executed_by_date.get(date, 0.0) + _fill_cost(
                fill, transaction_costs, slippage
            )

    per_period: list[dict] = []
    deltas: list[float] = []
    for t in range(len(idx)):
        date = idx[t]
        date_key = _date_key(date)
        m = float(modeled_series.iloc[t]) if t < len(modeled_series) else 0.0
        e = executed_by_date.get(date_key, 0.0)
        delta = e - m
        deltas.append(delta)
        per_period.append(
            {
                "date": date_key,
                "modeled_cost": m,
                "executed_cost": e,
                "delta": delta,
            }
        )

    deltas_arr = np.array(deltas, dtype=float)
    aggregate = {
        "n_periods": len(deltas),
        "modeled_total": float(modeled_series.sum()),
        "executed_total": float(sum(d["executed_cost"] for d in per_period)),
        "delta_total": float(deltas_arr.sum()),
        "delta_mean": float(deltas_arr.mean()) if len(deltas_arr) else 0.0,
        "delta_max_abs": float(np.max(np.abs(deltas_arr))) if len(deltas_arr) else 0.0,
        "n_mismatches": int((np.abs(deltas_arr) > 1e-12).sum()),
    }

    payload = {
        "schema_version": "r5-reconcile-1",
        "n_periods": len(deltas),
        "per_period": per_period,
        "aggregate": aggregate,
    }
    return ReconciliationResult(
        schema_version="r5-reconcile-1",
        n_periods=len(deltas),
        per_period=per_period,
        aggregate=aggregate,
        checksum=_checksum(payload),
    )


def reconcile_fills_to_backtest(
    weights: pd.DataFrame,
    returns: pd.DataFrame,
    backtest: pd.DataFrame,
    fills: Optional[list[dict]] = None,
    transaction_costs: float = 0.0,
    slippage: float = 0.0,
) -> ReconciliationResult:
    """Compare realized equity from fills vs model backtest equity (R5-C).

    Replays fills period by period: realized return = lagged_weights dot
    period_returns minus fill costs. Compares cumulative equity to the model
    backtest's cumulative column. Surplus mismatches are surfaced in
    per-period delta and aggregate n_mismatches.
    """
    empty_agg = {
        "n_periods": 0,
        "model_final_equity": 1.0,
        "realized_final_equity": 1.0,
        "delta_final": 0.0,
        "max_delta_abs": 0.0,
        "n_mismatches": 0,
    }
    if not isinstance(weights, pd.DataFrame) or weights.empty:
        payload = {
            "schema_version": "r5-fill-reconcile-1",
            "n_periods": 0,
            "per_period": [],
            "aggregate": empty_agg,
        }
        return ReconciliationResult(
            schema_version="r5-fill-reconcile-1",
            n_periods=0,
            per_period=[],
            aggregate=empty_agg,
            checksum=_checksum(payload),
        )

    w = weights.sort_index()
    r = returns.sort_index()
    cols = [c for c in w.columns if c in r.columns]
    if not cols:
        cols = [str(c) for c in w.columns]

    idx = list(w.index)
    n = len(idx)

    # Per-period returns matrix aligned to weights universe.
    if cols:
        r_sub = r[cols].reindex(idx)
    else:
        r_sub = pd.DataFrame(index=idx, columns=cols)
    r_arr = r_sub.to_numpy(dtype=float)
    r_arr = np.where(np.isfinite(r_arr), r_arr, 0.0)

    # Fill costs grouped by date.
    fill_costs_by_date: dict[str, float] = {}
    # Per-(date, asset) traded weight actually realized, and the ordered
    # (requested) weight for the same trade, so realized positions can deviate
    # from the target-weight replay by exactly the unfilled/partial remainder.
    filled_by_date: dict[str, dict[str, float]] = {}
    ordered_by_date: dict[str, dict[str, float]] = {}
    if fills:
        for fill in fills:
            date = _date_key(fill.get("date", ""))
            asset = str(fill.get("asset", ""))
            filled_w = _fill_executed_weight(fill)
            try:
                ordered_w = float(fill.get("order_weight", 0.0) or 0.0)
            except (TypeError, ValueError):
                ordered_w = 0.0
            fill_costs_by_date[date] = fill_costs_by_date.get(date, 0.0) + _fill_cost(
                fill, transaction_costs, slippage
            )
            if asset:
                filled_by_date.setdefault(date, {})
                filled_by_date[date][asset] = (
                    filled_by_date[date].get(asset, 0.0) + filled_w
                )
                ordered_by_date.setdefault(date, {})
                ordered_by_date[date][asset] = (
                    ordered_by_date[date].get(asset, 0.0) + ordered_w
                )

    # Model backtest equity.
    model_cumulative = None
    if isinstance(backtest, pd.DataFrame) and "cumulative" in backtest.columns:
        model_cumulative = backtest["cumulative"].reindex(idx).fillna(1.0)

    # Realized replay mirrors the model backtest (``backtest.py``): positions
    # are lagged one period (no lookahead) and equity compounds identically via
    # ``exp(cumsum(log1p(net)))``. Baseline is the target-weight book; fills
    # then deviate realized positions from target by the unfilled /
    # partially-filled remainder (ordered - filled), so full fills with no cost
    # drag track the model exactly while partial and rejected fills surface in
    # the realized equity curve. Fill-level costs are subtracted on top.
    per_period: list[dict] = []
    deltas: list[float] = []
    equity_value = 1.0
    prev_w = np.zeros(len(cols), dtype=float)
    target_w = np.zeros(len(cols), dtype=float)
    col_pos = {c: j for j, c in enumerate(cols)}
    for t in range(n):
        date = idx[t]
        date_key = _date_key(date)
        row_w = w.iloc[t]
        for c in cols:
            try:
                target_w[col_pos[c]] = float(row_w[c])
            except (TypeError, ValueError):
                target_w[col_pos[c]] = 0.0
        # Realized positions start at target, then absorb the fill shortfall.
        realized_w = target_w.copy()
        date_filled = filled_by_date.get(date_key, {})
        date_ordered = ordered_by_date.get(date_key, {})
        for asset in set(date_filled) | set(date_ordered):
            if asset not in col_pos:
                continue
            shortfall = date_ordered.get(asset, 0.0) - date_filled.get(asset, 0.0)
            if shortfall:
                realized_w[col_pos[asset]] -= shortfall
        # Lag positions one period, matching the model backtest.
        period_ret = float(np.dot(prev_w, r_arr[t]))
        if not math.isfinite(period_ret):
            period_ret = 0.0
        cost = fill_costs_by_date.get(date_key, 0.0)
        net_ret = period_ret - cost
        if not math.isfinite(net_ret):
            net_ret = 0.0
        net_ret = max(net_ret, -1.0 + 1e-12)
        equity_value = equity_value * math.exp(math.log1p(net_ret))
        if not math.isfinite(equity_value) or equity_value <= 0:
            equity_value = 1.0
        prev_w = realized_w

        model_eq = 1.0
        if model_cumulative is not None and t < len(model_cumulative):
            model_eq = float(model_cumulative.iloc[t])
        delta = equity_value - model_eq
        deltas.append(delta)
        per_period.append(
            {
                "date": date_key,
                "model_equity": model_eq,
                "realized_equity": float(equity_value),
                "delta": delta,
            }
        )

    deltas_arr = np.array(deltas, dtype=float)
    aggregate = {
        "n_periods": n,
        "model_final_equity": float(model_cumulative.iloc[-1]) if model_cumulative is not None else 1.0,
        "realized_final_equity": float(equity_value),
        "delta_final": float(deltas_arr[-1]) if len(deltas_arr) else 0.0,
        "max_delta_abs": float(np.max(np.abs(deltas_arr))) if len(deltas_arr) else 0.0,
        "n_mismatches": int((np.abs(deltas_arr) > 1e-9).sum()),
    }

    payload = {
        "schema_version": "r5-fill-reconcile-1",
        "n_periods": n,
        "per_period": per_period,
        "aggregate": aggregate,
    }
    return ReconciliationResult(
        schema_version="r5-fill-reconcile-1",
        n_periods=n,
        per_period=per_period,
        aggregate=aggregate,
        checksum=_checksum(payload),
    )
