"""Deterministic paper-trading replay harness for BAB results (R4-C).

``ReplayHarness`` replays a :class:`BABResult`'s weights against a price /
returns fixture deterministically, recording per-period orders, fills, and
costs, and emitting a reproducible artifact (stable schema + SHA-256
checksum). Two runs on identical inputs produce byte-identical artifacts;
the artifact is strict-JSON-safe and contains no wall-clock or randomness.
"""

from __future__ import annotations

import hashlib
import json
import math

import numpy as np
import pandas as pd

from .strategy import BABResult


class ReplayHarness:
    """Replay a BABResult's weights against prices/returns, recording orders/fills/costs.

    Parameters
    ----------
    result:
        A :class:`BABResult` (typically from :meth:`BABStrategy.run`) whose
        ``weights`` frame is replayed.
    prices_df:
        Optional price DataFrame (datetime index, asset columns). When given,
        fills are valued at these prices and per-period P&L / equity is computed
        from price changes. When omitted, the result's ``returns`` frame is used
        directly for equity.
    returns_df:
        Optional simple-returns DataFrame used for equity when ``prices_df`` is
        omitted. Defaults to ``result.returns``.
    transaction_costs:
        Flat cost fraction applied to one-way turnover per period (default 0.0).
    slippage:
        Flat slippage fraction applied to one-way turnover per period (default 0.0).
    """

    SCHEMA_VERSION = "r4-replay-1"

    def __init__(
        self,
        result: BABResult,
        prices_df: pd.DataFrame | None = None,
        returns_df: pd.DataFrame | None = None,
        transaction_costs: float = 0.0,
        slippage: float = 0.0,
    ) -> None:
        if result is None or not isinstance(result, BABResult):
            raise ValueError("ReplayHarness requires a BABResult instance")
        self.result = result
        self.weights = result.weights
        self.returns = returns_df if returns_df is not None else getattr(result, "returns", None)
        self.prices = prices_df
        self.transaction_costs = float(transaction_costs or 0.0)
        self.slippage = float(slippage or 0.0)
        self._config_snapshot = self._snapshot_config(result.config)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def replay(self) -> dict:
        """Run the replay and return the artifact dict (with checksum).

        The artifact is strict-JSON-safe and deterministic: identical inputs
        yield byte-identical output (same checksum).
        """
        orders, fills, costs, equity = self._replay_periods()
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "config_snapshot": self._config_snapshot,
            "n_periods": len(orders),
            "orders": orders,
            "fills": fills,
            "costs": costs,
            "equity": equity,
        }
        checksum = self._checksum(payload)
        payload["checksum"] = checksum
        return payload

    def artifact(self) -> dict:
        """Alias for :meth:`replay` (kept for API symmetry)."""
        return self.replay()

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _snapshot_config(self, cfg) -> dict:
        """Deterministic, JSON-safe snapshot of the config used for the run."""
        snap = {
            "benchmark": getattr(cfg, "benchmark", None),
            "beta_window": getattr(cfg, "beta_window", None),
            "long_quantile": getattr(cfg, "long_quantile", None),
            "short_quantile": getattr(cfg, "short_quantile", None),
            "dollar_neutral": bool(getattr(cfg, "dollar_neutral", True)),
            "transaction_costs": self.transaction_costs,
            "slippage": self.slippage,
            "universe": [str(u) for u in (getattr(cfg, "universe", []) or [])],
        }
        return self._sanitize(snap)

    def _replay_periods(self) -> tuple[list, list, list, list]:
        """Walk periods in index order, recording orders/fills/costs/equity.

        Orders are per-period weight changes (target - previous). Fills assume
        full execution at target weight (paper trading, no partial fill modeling
        beyond the configured cost/slippage drag). Costs are flat fractions of
        one-way turnover. Equity compounds period returns (from prices or
        returns) net of costs. All column alignment is deterministic (sorted,
        intersected with the weights universe).
        """
        w = self.weights
        if not isinstance(w, pd.DataFrame) or w.empty:
            empty = []
            return empty, empty, empty, [1.0]

        w = w.sort_index()
        cols = [str(c) for c in w.columns]
        idx = list(w.index)
        n = len(idx)
        n_cols = len(cols)

        # Align prices / returns to the weights universe (deterministic order).
        price_ret = None  # (n, n_cols) float array of per-period returns per col
        if self.prices is not None:
            prices = self.prices.sort_index()
            price_cols = [str(c) for c in prices.columns]
            avail = [c for c in cols if c in price_cols]
            if len(avail) > 0 and len(prices) > 0:
                p_sub = prices.reindex(index=idx, columns=avail)
                p_arr = p_sub.to_numpy(dtype=float)
                with np.errstate(divide="ignore", invalid="ignore"):
                    rets_arr = p_arr[1:] / p_arr[:-1] - 1.0
                rets_arr = np.where(np.isfinite(rets_arr), rets_arr, 0.0)
                # Build (n, n_cols): first period 0.0, then returns; missing cols -> 0.
                price_ret = np.zeros((n, n_cols), dtype=float)
                col_pos = {c: j for j, c in enumerate(cols)}
                for j, c in enumerate(avail):
                    price_ret[1:, col_pos[c]] = rets_arr[:, j]
        elif self.returns is not None:
            rets = self.returns.sort_index()
            ret_cols = [str(c) for c in rets.columns]
            avail = [c for c in cols if c in ret_cols]
            if len(avail) > 0 and len(rets) > 0:
                r_sub = rets.reindex(index=idx, columns=avail)
                r_arr = r_sub.to_numpy(dtype=float)
                r_arr = np.where(np.isfinite(r_arr), r_arr, 0.0)
                price_ret = np.zeros((n, n_cols), dtype=float)
                col_pos = {c: j for j, c in enumerate(cols)}
                for j, c in enumerate(avail):
                    price_ret[:, col_pos[c]] = r_arr[:, j]

        orders: list = []
        fills: list = []
        costs: list = []
        equity: list = []

        prev_w = np.zeros(n_cols, dtype=float)
        equity_value = 1.0
        for t in range(n):
            date = idx[t]
            date_key = self._date_key(date)
            row_w = w.iloc[t]
            w_arr = np.asarray(row_w, dtype=float)
            if w_arr.shape[0] != n_cols:
                w_arr = np.resize(w_arr, n_cols)
            if not np.all(np.isfinite(w_arr)):
                w_arr = np.where(np.isfinite(w_arr), w_arr, 0.0)

            order_arr = w_arr - prev_w
            turnover = float(np.abs(order_arr).sum())

            # Orders / fills: only nonzero changes, deterministic column order.
            order_entries = {}
            fill_entries = {}
            for j, col in enumerate(cols):
                ov = float(order_arr[j])
                if ov == 0.0:
                    continue
                order_entries[col] = ov
                fill_entries[col] = ov  # paper fill at target weight
            orders.append({"date": date_key, "orders": order_entries})
            fills.append({"date": date_key, "fills": fill_entries})

            # Costs: flat fraction of one-way turnover.
            period_cost = turnover * (self.transaction_costs + self.slippage)
            costs.append({"date": date_key, "turnover": turnover, "cost": period_cost})

            # Period return: lagged weights dot current-period returns (no lookahead).
            period_ret = 0.0
            if price_ret is not None:
                r_row = price_ret[t]
                period_ret = float(np.dot(prev_w, r_row))
            period_ret = float(period_ret) if math.isfinite(period_ret) else 0.0
            period_ret = period_ret - period_cost

            equity_value = equity_value * (1.0 + period_ret)
            if not math.isfinite(equity_value):
                equity_value = 1.0
            equity.append({"date": date_key, "equity": float(equity_value)})

            prev_w = w_arr

        return orders, fills, costs, equity

    @staticmethod
    def _date_key(date) -> str:
        """Serialize a date/Timestamp deterministically (ISO-8601)."""
        try:
            ts = pd.Timestamp(date)
            return ts.isoformat()
        except Exception:
            return str(date)

    @staticmethod
    def _checksum(payload: dict) -> str:
        """SHA-256 over canonical JSON (sorted keys, no checksum field)."""
        payload_no_sum = {k: v for k, v in payload.items() if k != "checksum"}
        canonical = json.dumps(payload_no_sum, sort_keys=True, default=str, allow_nan=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _sanitize(obj):
        """Recursively coerce to strict-JSON-safe primitives (finite only)."""
        import math

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
            return [ReplayHarness._sanitize(v) for v in obj]
        if isinstance(obj, dict):
            return {str(k): ReplayHarness._sanitize(v) for k, v in obj.items()}
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, (pd.Series, pd.Index, np.ndarray)):
            return [ReplayHarness._sanitize(v) for v in obj.tolist()]
        return str(obj)
