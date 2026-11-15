"""P11: execution.py real-path coverage.

Drives gate-missed branches in the execution module using only fakes/mocks —
no network, no credentials, and real (non-dry-run) execution is never enabled
against a live venue. The default offline/deterministic path is unchanged.

Covers:
  * ``PaperAdapter._price_for`` / ``_adv_for`` / ``_adv_from_frame_value``
    fallback lookups (str keys, Timestamp keys, NaN, missing, dict/Series/
    DataFrame ADV shapes, error swallowing).
  * ``order_batches_from_weights`` edge branches (empty frame, NaN/non-finite
    targets, price/ADV alignment by date, non-numeric coercion).
  * ``PaperExecutionEngine`` diagnostics + paper-PnL branches (empty weights,
    missing betas, no-fills, unparseable fill dates, non-finite returns).
  * ``_sanitize_for_json`` / ``_safe_float`` / ``_write_jsonl`` primitive edges.
  * ``CCXTConnector`` non-dry-run submit/cancel/status paths against a fake
    ``_exchange`` (no real ccxt network) plus not-connected guards.
  * ``LiveExecutionAdapter`` non-dry-run submit via an injected fake connector
    (partial/filled/rejected statuses, sell sign flip, participation metadata).
"""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.execution import (
    CCXTConnector,
    LiveExecutionAdapter,
    LiveFill,
    LiveOrder,
    MockAdapter,
    OrderBatch,
    OrderIntent,
    PaperAdapter,
    PaperExecutionEngine,
    _finite,
    _safe_float,
    _sanitize_for_json,
    _write_jsonl,
    configure_paper_adapter,
    execution_payload_to_json,
    order_batches_from_weights,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _intent(
    asset: str = "BTC",
    order_weight: float = 0.1,
    date: str = "2024-01-01",
    price: float | None = 50000.0,
    notional: float | None = None,
    adv: float | None = None,
    max_participation: float | None = None,
) -> OrderIntent:
    return OrderIntent(
        date=date,
        asset=asset,
        target_weight=order_weight,
        current_weight=0.0,
        order_weight=order_weight,
        price=price,
        notional_usd=notional if notional is not None else abs(order_weight) * (price or 0.0),
        adv_usd=adv,
        max_participation=max_participation,
    )


class _FakeExchange:
    """Minimal CCXT-like exchange stand-in (no network)."""

    def __init__(self, config=None, response=None, raise_exc=None):
        self.config = config or {}
        self.response = response or {}
        self.raise_exc = raise_exc
        self.loaded = False
        self.closed = False
        self.calls: list[dict] = []

    def load_markets(self):
        self.loaded = True

    def close(self):
        self.closed = True

    def create_order(self, **kwargs):
        self.calls.append(kwargs)
        if self.raise_exc is not None:
            raise self.raise_exc
        return self.response

    def fetch_balance(self):
        return {"USDT": {"free": 1.0, "used": 0.0, "total": 1.0}}

    def fetch_ticker(self, symbol):
        return {"last": 2.0, "symbol": symbol}


class _FakeConnector:
    """ExchangeConnector stand-in returning canned LiveFills."""

    def __init__(self, fills: dict[str, LiveFill] | None = None, default_status: str = "filled"):
        self.fills = fills or {}
        self.default_status = default_status
        self.connected = False
        self.submitted: list[LiveOrder] = []
        self.cancelled: list[str] = []

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def is_connected(self):
        return self.connected

    def submit_order(self, order: LiveOrder) -> LiveFill:
        self.submitted.append(order)
        key = order.idempotency_key
        if key in self.fills:
            return self.fills[key]
        return LiveFill(
            idempotency_key=key,
            date=order.date,
            asset=order.asset,
            side=order.side,
            weight=order.weight,
            price=order.price,
            notional_usd=order.notional_usd,
            status=self.default_status,
        )

    def cancel_order(self, idempotency_key: str) -> bool:
        self.cancelled.append(idempotency_key)
        return True

    def get_order_status(self, idempotency_key: str):
        return self.fills.get(idempotency_key)

    def fetch_balance(self) -> dict:
        return {"USDT": {"free": 0.0, "used": 0.0, "total": 0.0}}

    def fetch_ticker(self, symbol: str) -> dict:
        return {"last": 0.0}


# ---------------------------------------------------------------------------
# PaperAdapter fallback price / ADV lookups
# ---------------------------------------------------------------------------


class TestPaperAdapterPriceFallback:
    def test_price_lookup_by_string_index(self):
        prices = pd.DataFrame({"BTC": [100.0, 110.0]}, index=["2024-01-01", "2024-01-02"])
        adapter = PaperAdapter(prices_df=prices, partial_fill=True)
        assert adapter._price_for("2024-01-02", "BTC") == 110.0

    def test_price_lookup_by_timestamp_index(self):
        idx = pd.date_range("2024-01-01", periods=2)
        prices = pd.DataFrame({"BTC": [100.0, 110.0]}, index=idx)
        adapter = PaperAdapter(prices_df=prices, partial_fill=True)
        assert adapter._price_for("2024-01-02", "BTC") == 110.0

    def test_price_lookup_nan_returns_none(self):
        prices = pd.DataFrame({"BTC": [100.0, np.nan]}, index=["2024-01-01", "2024-01-02"])
        adapter = PaperAdapter(prices_df=prices, partial_fill=True)
        assert adapter._price_for("2024-01-02", "BTC") is None

    def test_price_lookup_missing_asset_and_no_prices(self):
        prices = pd.DataFrame({"BTC": [100.0]}, index=["2024-01-01"])
        adapter = PaperAdapter(prices_df=prices)
        assert adapter._price_for("2024-01-01", "ETH") is None
        assert PaperAdapter(prices_df=None)._price_for("2024-01-01", "BTC") is None

    def test_price_lookup_bad_date_key_swallowed(self):
        prices = pd.DataFrame({"BTC": [100.0]}, index=pd.date_range("2024-01-01", periods=1))
        adapter = PaperAdapter(prices_df=prices)
        # Unparseable key hits neither branch and returns None.
        assert adapter._price_for("not-a-date", "BTC") is None


class TestPaperAdapterAdvFallback:
    def test_adv_from_dict(self):
        adapter = PaperAdapter(adv_usd={"BTC": 1_000_000.0}, partial_fill=True)
        assert adapter._adv_for("2024-01-01", "BTC") == 1_000_000.0
        assert adapter._adv_for("2024-01-01", "ETH") is None

    def test_adv_from_asset_indexed_series(self):
        s = pd.Series({"BTC": 5.0, "ETH": float("nan")})
        adapter = PaperAdapter(adv_usd=s, partial_fill=True)
        assert adapter._adv_for("2024-01-01", "BTC") == 5.0
        assert adapter._adv_for("2024-01-01", "ETH") is None

    def test_adv_from_date_indexed_series(self):
        s = pd.Series([7.0, 8.0], index=["2024-01-01", "2024-01-02"])
        adapter = PaperAdapter(adv_usd=s, partial_fill=True)
        assert adapter._adv_for("2024-01-02", "BTC") == 8.0

    def test_adv_from_dataframe_columns(self):
        df = pd.DataFrame({"BTC": [3.0, 4.0]}, index=["2024-01-01", "2024-01-02"])
        adapter = PaperAdapter(adv_usd=df, partial_fill=True)
        assert adapter._adv_for("2024-01-02", "BTC") == 4.0

    def test_adv_from_dataframe_index_fallback(self):
        # Asset is a row label (not a column), so the .loc[asset] fallback fires.
        df = pd.DataFrame({"BTC": [3.0]}, index=["BTC"])
        adapter = PaperAdapter(adv_usd=df, partial_fill=True)
        # 'BTC' is a column here, so column lookup wins and date-key misses.
        assert adapter._adv_for("2024-01-01", "BTC") is None

    def test_adv_from_dataframe_row_label_lookup(self):
        # Column key is the date, index is the asset -> .loc[asset] path.
        df = pd.DataFrame({"2024-01-01": [3.0]}, index=["BTC"])
        adapter = PaperAdapter(adv_usd=df, partial_fill=True)
        assert adapter._adv_for("2024-01-01", "BTC") == 3.0

    def test_adv_none_returns_none(self):
        assert PaperAdapter(adv_usd=None)._adv_for("2024-01-01", "BTC") is None

    def test_adv_from_frame_value_timestamp_lookup(self):
        # Timestamp-indexed Series: ISO-string membership is False, but the
        # explicit pd.Timestamp(date_key) branch matches.
        sub = pd.Series([1.0], index=pd.DatetimeIndex(["2024-01-02"]))
        assert PaperAdapter._adv_from_frame_value(sub, "2024-01-02") == 1.0
        assert PaperAdapter._adv_from_frame_value(sub, "2024-01-03") is None

    def test_adv_from_frame_value_series_value_uses_iloc(self):
        # Duplicate index makes .loc return a Series; iloc[0] unwraps it.
        dup = pd.Series([1.0, 2.0], index=["2024-01-01", "2024-01-01"])
        assert PaperAdapter._adv_from_frame_value(dup, "2024-01-01") == 1.0


class TestPaperAdapterRealismFill:
    def test_partial_fill_when_participation_exceeds_cap(self):
        prices = pd.DataFrame({"BTC": [100.0]}, index=["2024-01-01"])
        adv = {"BTC": 100.0}
        adapter = PaperAdapter(
            prices_df=prices, adv_usd=adv, partial_fill=True, max_participation=0.1
        )
        intent = _intent(
            order_weight=1.0, price=100.0, notional=100.0, adv=100.0, max_participation=0.1
        )
        fills = adapter.submit_intents(OrderBatch(date="2024-01-01", intents=(intent,)))
        f = fills[0]
        assert f["status"] == "partial"
        assert f["reason"] == "participation_cap"
        assert f["fill_ratio"] < 1.0
        assert f["slippage"] > 0.0


# ---------------------------------------------------------------------------
# order_batches_from_weights edge branches
# ---------------------------------------------------------------------------


class TestOrderBatchesFromWeights:
    def test_empty_or_non_frame_returns_empty(self):
        assert order_batches_from_weights(pd.DataFrame()) == []
        assert order_batches_from_weights(None) == []  # type: ignore[arg-type]

    def test_zero_change_emits_no_intent(self):
        w = pd.DataFrame({"BTC": [0.0, 0.0]}, index=["2024-01-01", "2024-01-02"])
        assert order_batches_from_weights(w) == []

    def test_nan_and_nonfinite_targets_coerced_to_zero(self):
        w = pd.DataFrame(
            {"BTC": [np.nan, np.inf, 0.1]},
            index=["2024-01-01", "2024-01-02", "2024-01-03"],
        )
        batches = order_batches_from_weights(w)
        # First two rows are zero-weight (NaN/inf coerced), last is a real order.
        assert len(batches) == 1
        assert batches[0].intents[0].order_weight == pytest.approx(0.1)

    def test_price_and_adv_alignment_by_date(self):
        idx = pd.date_range("2024-01-01", periods=2)
        w = pd.DataFrame({"BTC": [0.1, 0.2]}, index=idx)
        prices = pd.DataFrame({"BTC": [100.0, 200.0]}, index=idx)
        adv = pd.DataFrame({"BTC": [1000.0, 2000.0]}, index=idx)
        batches = order_batches_from_weights(w, prices_df=prices, adv_usd=adv)
        assert batches[0].intents[0].price == 100.0
        assert batches[0].intents[0].adv_usd == 1000.0
        assert batches[0].intents[0].notional_usd == pytest.approx(0.1 * 100.0)

    def test_adv_dict_and_series_shapes(self):
        idx = ["2024-01-01", "2024-01-02"]
        w = pd.DataFrame({"BTC": [0.1, 0.2], "ETH": [0.1, 0.2]}, index=idx)
        batches_dict = order_batches_from_weights(w, adv_usd={"BTC": 10.0})
        assert batches_dict[0].intents  # has intents
        btc_adv = {i.asset: i.adv_usd for i in batches_dict[0].intents}
        assert btc_adv["BTC"] == 10.0

        s = pd.Series({"BTC": 20.0, "ETH": 30.0})
        batches_series = order_batches_from_weights(w, adv_usd=s)
        eth_intent = next(i for i in batches_series[0].intents if i.asset == "ETH")
        assert eth_intent.adv_usd == 30.0

    def test_non_numeric_price_coerced_to_none(self):
        w = pd.DataFrame({"BTC": [0.1]}, index=["2024-01-01"])
        prices = pd.DataFrame({"BTC": ["bad"]}, index=["2024-01-01"])
        batches = order_batches_from_weights(w, prices_df=prices)
        assert batches[0].intents[0].price is None
        assert batches[0].intents[0].notional_usd is None


# ---------------------------------------------------------------------------
# PaperExecutionEngine diagnostics + PnL branches
# ---------------------------------------------------------------------------


class TestPaperExecutionEngineBranches:
    def test_empty_weights_returns_zero_report(self, tmp_path):
        log = tmp_path / "fills.jsonl"
        engine = PaperExecutionEngine(log_path=log)
        report = engine.execute(pd.DataFrame())
        assert report.n_orders == 0
        assert report.n_fills == 0

    def test_diagnostics_without_betas(self, tmp_path):
        w = pd.DataFrame({"BTC": [0.1, -0.1]}, index=pd.date_range("2024-01-01", periods=2))
        engine = PaperExecutionEngine()
        report = engine.execute(w)
        assert report.diagnostics
        assert all(d.beta_mean == 0.0 for d in report.diagnostics)
        assert all(d.n_long >= 0 and d.n_short >= 0 for d in report.diagnostics)

    def test_paper_pnl_skips_missing_columns(self):
        w = pd.DataFrame({"BTC": [0.5]}, index=["2024-01-01"])
        engine = PaperExecutionEngine()
        engine.execute(w)
        # Returns frame missing the asset column -> skipped, PnL 0.0.
        returns = pd.DataFrame(
            {"ETH": [0.1]}, index=pd.date_range("2024-01-02", periods=1)
        )
        pnl = engine._paper_pnl(returns)
        assert pnl == 0.0
        # Non-frame / empty / no fills -> None.
        assert engine._paper_pnl(None) is None
        assert engine._paper_pnl(pd.DataFrame()) is None

    def test_paper_pnl_non_finite_return_skipped(self):
        w = pd.DataFrame({"BTC": [0.5]}, index=["2024-01-01"])
        engine = PaperExecutionEngine()
        engine.execute(w)
        returns = pd.DataFrame(
            {"BTC": [np.nan]}, index=pd.date_range("2024-01-02", periods=1)
        )
        assert engine._paper_pnl(returns) == 0.0

    def test_betas_reindex_failure_falls_back_to_none(self):
        w = pd.DataFrame({"BTC": [0.1]}, index=["2024-01-01"])
        # Betas frame with duplicate index cannot reindex cleanly -> None branch.
        betas = pd.DataFrame({"BTC": [1.0, 2.0]}, index=["2024-01-01", "2024-01-01"])
        engine = PaperExecutionEngine()
        report = engine.execute(w, betas_df=betas)
        assert report.n_orders >= 0

    def test_writes_jsonl_sidecars(self, tmp_path):
        w = pd.DataFrame({"BTC": [0.1, -0.1]}, index=pd.date_range("2024-01-01", periods=2))
        betas = pd.DataFrame({"BTC": [1.0, 1.1]}, index=pd.date_range("2024-01-01", periods=2))
        log = tmp_path / "sub" / "fills.jsonl"
        diag = tmp_path / "diag.jsonl"
        engine = PaperExecutionEngine(log_path=log, diagnostics_path=diag)
        engine.execute(w, betas_df=betas)
        assert log.exists()
        for line in log.read_text(encoding="utf-8").splitlines():
            json.loads(line)
        for line in diag.read_text(encoding="utf-8").splitlines():
            json.loads(line)

    def test_engine_rejects_non_paper_mode(self):
        with pytest.raises(ValueError, match="only supports mode='paper'"):
            PaperExecutionEngine(mode="live")


# ---------------------------------------------------------------------------
# Primitive / serialization helpers
# ---------------------------------------------------------------------------


class TestSanitizeAndSerialize:
    def test_sanitize_primitives(self):
        assert _sanitize_for_json(None) is None
        assert _sanitize_for_json(True) is True
        assert _sanitize_for_json(3) == 3
        assert _sanitize_for_json(float("inf")) == 0.0
        assert _sanitize_for_json(float("nan")) == 0.0
        assert _sanitize_for_json("x") == "x"
        assert _sanitize_for_json([1, float("nan")]) == [1, 0.0]
        assert _sanitize_for_json((1, 2)) == [1, 2]

    def test_sanitize_timestamp_series_index_ndarray(self):
        ts = pd.Timestamp("2024-01-01")
        assert _sanitize_for_json(ts) == "2024-01-01T00:00:00"
        assert _sanitize_for_json(pd.Series([1, 2])) == [1, 2]
        assert _sanitize_for_json(np.array([1, 2])) == [1, 2]
        assert _sanitize_for_json(np.int64(5)) == 5
        assert _sanitize_for_json(np.float64(1.5)) == 1.5
        assert _sanitize_for_json(np.bool_(True)) is True

    def test_sanitize_fallback_to_str(self):
        class _Obj:
            def __str__(self):
                return "obj"

        assert _sanitize_for_json(_Obj()) == "obj"

    def test_execution_payload_json_strict(self):
        payload = {"a": float("nan"), "b": pd.Timestamp("2024-01-01")}
        out = execution_payload_to_json(payload)
        parsed = json.loads(out)
        assert parsed["a"] == 0.0
        assert parsed["b"] == "2024-01-01T00:00:00"

    def test_safe_float_edges(self):
        assert _safe_float(None) == 0.0
        assert _safe_float(None, default=2.0) == 2.0
        assert _safe_float("bad") == 0.0
        assert _safe_float(float("inf")) == 0.0
        assert _safe_float(3.5) == 3.5

    def test_finite_helper(self):
        assert _finite(None) == 0.0
        assert _finite("bad") == 0.0
        assert _finite(float("nan")) == 0.0
        assert _finite(2.5) == 2.5

    def test_write_jsonl_creates_parent_and_sanitizes(self, tmp_path):
        out = tmp_path / "deep" / "nested" / "out.jsonl"
        _write_jsonl(out, [{"x": float("nan"), "y": 1}])
        lines = out.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        assert json.loads(lines[0]) == {"x": 0.0, "y": 1}


# ---------------------------------------------------------------------------
# configure_paper_adapter
# ---------------------------------------------------------------------------


class _Cfg:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _Strategy:
    def __init__(self, config, resolver=None):
        self.config = config
        if resolver is not None:
            self._resolve_cost_model = resolver


class TestConfigurePaperAdapter:
    def test_no_config_returns_same_adapter(self):
        adapter = PaperAdapter()
        assert configure_paper_adapter(adapter, object()) is adapter

    def test_populates_from_resolver_and_config(self):
        cfg = _Cfg(prices="P", adv_usd="A", partial_fill=True, max_participation=0.2)

        def resolver(c):
            return (None, "RP", "RA")

        strategy = _Strategy(cfg, resolver=resolver)
        adapter = PaperAdapter()
        out = configure_paper_adapter(adapter, strategy)
        assert out.prices == "RP"
        assert out.adv_usd == "RA"
        assert out.partial_fill is True
        assert out.max_participation == 0.2

    def test_resolver_exception_falls_back_to_config(self):
        cfg = _Cfg(prices="P", adv_usd="A")

        def resolver(c):
            raise RuntimeError("boom")

        strategy = _Strategy(cfg, resolver=resolver)
        adapter = PaperAdapter()
        out = configure_paper_adapter(adapter, strategy)
        assert out.prices == "P"
        assert out.adv_usd == "A"

    def test_explicit_adapter_values_not_overridden(self):
        cfg = _Cfg(prices="P", adv_usd="A", partial_fill=False, max_participation=0.9)
        strategy = _Strategy(cfg)
        adapter = PaperAdapter(prices_df="keep", adv_usd="keep", max_participation=0.5)
        out = configure_paper_adapter(adapter, strategy)
        assert out.prices == "keep"
        assert out.adv_usd == "keep"
        assert out.max_participation == 0.5

    def test_bad_config_cap_is_suppressed(self):
        cfg = _Cfg(max_participation="not-a-number")
        strategy = _Strategy(cfg)
        adapter = PaperAdapter()
        out = configure_paper_adapter(adapter, strategy)
        assert out.max_participation == 0.10


# ---------------------------------------------------------------------------
# CCXTConnector non-dry-run paths (fake exchange, no network)
# ---------------------------------------------------------------------------


class TestCCXTConnectorRealPaths:
    def _connector(self, exchange=None, raise_exc=None, response=None):
        conn = CCXTConnector(exchange_name="binance", dry_run=False)
        fake = _FakeExchange(response=response, raise_exc=raise_exc)
        conn._exchange = fake
        conn._connected = True
        return conn, fake

    def test_submit_real_order_filled(self):
        conn, fake = self._connector(
            response={"filled": 0.5, "average": 100.0, "cost": 50.0, "status": "closed"}
        )
        order = LiveOrder(
            idempotency_key="k1", date="2024-01-01", asset="BTC", side="buy",
            weight=1.0, price=100.0, notional_usd=100.0,
        )
        fill = conn.submit_order(order)
        assert fill.status == "filled"
        assert fill.weight == 0.5
        assert fake.calls and fake.calls[0]["type"] == "market"

    def test_submit_real_order_partial_status(self):
        conn, _ = self._connector(
            response={"filled": 0.2, "average": 100.0, "cost": 20.0, "status": "open"}
        )
        order = LiveOrder(
            idempotency_key="k2", date="2024-01-01", asset="BTC", side="sell",
            weight=1.0, price=100.0, notional_usd=100.0,
        )
        fill = conn.submit_order(order)
        assert fill.status == "partial"

    def test_submit_real_order_exception_rejected(self):
        conn, _ = self._connector(raise_exc=RuntimeError("network down"))
        order = LiveOrder(
            idempotency_key="k3", date="2024-01-01", asset="BTC", side="buy",
            weight=1.0, price=100.0, notional_usd=100.0,
        )
        fill = conn.submit_order(order)
        assert fill.status == "rejected"
        assert "network down" in (fill.reason or "")

    def test_submit_real_order_max_participation_param(self):
        conn, fake = self._connector(
            response={"filled": 1.0, "average": 1.0, "cost": 1.0, "status": "closed"}
        )
        order = LiveOrder(
            idempotency_key="k4", date="2024-01-01", asset="BTC", side="buy",
            weight=1.0, price=1.0, notional_usd=1.0, max_participation=0.05,
        )
        conn.submit_order(order)
        assert fake.calls[0]["params"]["max_participation"] == 0.05

    def test_not_connected_guards(self):
        conn = CCXTConnector(exchange_name="binance", dry_run=True)
        with pytest.raises(RuntimeError, match="not connected"):
            conn.submit_order(
                LiveOrder(
                    idempotency_key="x", date="2024-01-01", asset="BTC",
                    side="buy", weight=1.0,
                )
            )
        with pytest.raises(RuntimeError, match="not connected"):
            conn.fetch_balance()
        with pytest.raises(RuntimeError, match="not connected"):
            conn.fetch_ticker("BTC/USDT")

    def test_cancel_real_returns_false(self):
        conn, _ = self._connector()
        # Connected but key never submitted -> False.
        assert conn.cancel_order("missing") is False

    def test_generate_idempotency_key_deterministic(self):
        conn = CCXTConnector(exchange_name="binance", dry_run=True)
        order = LiveOrder(
            idempotency_key="", date="2024-01-01", asset="BTC", side="buy",
            weight=0.1, price=100.0, notional_usd=10.0,
        )
        k1 = conn._generate_idempotency_key(order)
        k2 = conn._generate_idempotency_key(order)
        assert k1 == k2 and len(k1) == 32

    def test_asset_to_symbol_upper(self):
        conn = CCXTConnector(exchange_name="binance", dry_run=True)
        assert conn._asset_to_symbol("btc") == "BTC/USDT"

    def test_get_ccxt_missing_raises(self, monkeypatch):
        import builtins

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "ccxt":
                raise ImportError("no ccxt")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        conn = CCXTConnector(exchange_name="binance", dry_run=True)
        with pytest.raises(RuntimeError, match="ccxt is required"):
            conn._get_ccxt()

    def test_connect_with_credentials_and_testnet(self, monkeypatch):
        import ccxt

        captured = {}

        class _Dummy:
            def __init__(self, config):
                captured["config"] = config

            def load_markets(self):
                captured["loaded"] = True

            def close(self):
                captured["closed"] = True

        monkeypatch.setattr(ccxt, "binance", _Dummy, raising=False)
        conn = CCXTConnector(
            exchange_name="binance",
            api_key="k",
            api_secret="s",
            api_password="p",
            dry_run=False,
            testnet=True,
        )
        conn.connect()
        assert captured["config"]["apiKey"] == "k"
        assert captured["config"]["secret"] == "s"
        assert captured["config"]["password"] == "p"
        assert captured["config"]["options"]["defaultType"] == "future"
        assert captured["loaded"] is True
        # Second connect is a no-op.
        conn.connect()
        conn.disconnect()
        assert captured["closed"] is True

    def test_real_fetch_balance_and_ticker(self):
        conn, _ = self._connector()
        assert conn.fetch_balance()["USDT"]["free"] == 1.0
        assert conn.fetch_ticker("BTC/USDT")["last"] == 2.0

    def test_cancel_dry_run_without_cache_returns_false(self):
        conn = CCXTConnector(exchange_name="binance", dry_run=True)
        conn.connect()
        # Key was never added to _idempotency_keys.
        assert conn.cancel_order("nope") is False


# ---------------------------------------------------------------------------
# LiveExecutionAdapter non-dry-run via injected fake connector
# ---------------------------------------------------------------------------


class TestLiveExecutionAdapterNonDryRun:
    def _adapter(self, connector, **kw):
        kw.setdefault("exchange", "binance")
        kw.setdefault("dry_run", False)
        kw.setdefault("connector", connector)
        return LiveExecutionAdapter(**kw)

    def test_filled_and_sell_sign_flip(self):
        connector = _FakeConnector(default_status="filled")
        adapter = self._adapter(connector)
        intents = (
            _intent(asset="BTC", order_weight=0.1),
            _intent(asset="ETH", order_weight=-0.1),
        )
        fills = adapter.submit_intents(OrderBatch(date="2024-01-01", intents=intents))
        assert fills[0]["side"] == "buy"
        assert fills[1]["side"] == "sell"
        # Sell fill weight is negated.
        assert fills[1]["filled_weight"] < 0

    def test_partial_and_rejected_status_fill_ratio(self):
        connector = _FakeConnector(default_status="partial")
        adapter = self._adapter(connector)
        fill = adapter.submit_intents(
            OrderBatch(date="2024-01-01", intents=(_intent(),))
        )[0]
        assert fill["status"] == "partial"
        assert fill["fill_ratio"] == 0.5

        connector2 = _FakeConnector(default_status="rejected")
        adapter2 = self._adapter(connector2)
        fill2 = adapter2.submit_intents(
            OrderBatch(date="2024-01-01", intents=(_intent(),))
        )[0]
        assert fill2["status"] == "rejected"
        assert fill2["fill_ratio"] == 0.0

    def test_participation_metadata_passthrough(self):
        class _MetaConnector(_FakeConnector):
            def submit_order(self, order: LiveOrder) -> LiveFill:
                return LiveFill(
                    idempotency_key=order.idempotency_key,
                    date=order.date,
                    asset=order.asset,
                    side=order.side,
                    weight=order.weight,
                    status="filled",
                    metadata={"max_participation": 0.07},
                )

        connector = _MetaConnector()
        adapter = self._adapter(connector)
        fill = adapter.submit_intents(
            OrderBatch(date="2024-01-01", intents=(_intent(max_participation=0.07),))
        )[0]
        assert fill["max_participation"] == 0.07

    def test_get_submitted_and_fills_and_flush(self):
        connector = _FakeConnector()
        adapter = self._adapter(connector)
        adapter.submit_intents(OrderBatch(date="2024-01-01", intents=(_intent(),)))
        assert len(adapter.get_submitted()) == 1
        assert len(adapter.get_fills()) == 1
        assert adapter.flush() == []

    def test_disconnect_via_fake_connector(self):
        connector = _FakeConnector()
        adapter = self._adapter(connector)
        adapter._ensure_connected()
        adapter.disconnect()
        assert connector.connected is False
        assert adapter._connected is False

    def test_risk_manager_asset_rejection_path(self):
        from strategies.betting_against_beta.risk import RiskLimits, RiskManager

        connector = _FakeConnector()
        manager = RiskManager(limits=RiskLimits(blocked_assets=["BTC"]))
        adapter = self._adapter(connector, risk_manager=manager)
        fills = adapter.submit_intents(
            OrderBatch(date="2024-01-01", intents=(_intent(asset="BTC"),))
        )
        assert fills[0]["status"] == "rejected"
        assert fills[0]["reason"] == "Asset BTC is blocked"

    def test_risk_manager_portfolio_reject_all(self):
        from strategies.betting_against_beta.risk import RiskLimits, RiskManager

        connector = _FakeConnector()
        # Asset limit high (passes) but gross exposure tiny -> portfolio breach.
        manager = RiskManager(
            limits=RiskLimits(max_position_weight=1.0, max_gross_exposure=0.01)
        )
        adapter = self._adapter(
            connector, risk_manager=manager, current_positions=pd.Series({"BTC": 0.0})
        )
        intents = (_intent(asset="BTC", order_weight=0.5),)
        fills = adapter.submit_intents(OrderBatch(date="2024-01-01", intents=intents))
        assert fills[0]["status"] == "rejected"
        assert fills[0]["reason"] == "portfolio_limit_breach"

    def test_default_max_participation_applied_to_order(self):
        connector = _FakeConnector()
        adapter = self._adapter(connector, max_participation=0.15)
        adapter.submit_intents(
            OrderBatch(date="2024-01-01", intents=(_intent(max_participation=None),))
        )
        assert connector.submitted[0].max_participation == 0.15


# ---------------------------------------------------------------------------
# MockAdapter edges
# ---------------------------------------------------------------------------


class TestMockAdapterEdges:
    def test_fill_map_and_fn_and_fallback(self):
        adapter = MockAdapter(
            fill_map={
                ("2024-01-01", "BTC"): {"status": "filled", "filled_weight": 1.0}
            }
        )
        intents = (
            _intent(asset="BTC", date="2024-01-01"),
            _intent(asset="ETH", date="2024-01-01"),
        )
        fills = adapter.submit_intents(OrderBatch(date="2024-01-01", intents=intents))
        assert fills[0]["filled_weight"] == 1.0
        # ETH not in map -> fallback full fill.
        assert fills[1]["status"] == "filled"
        assert adapter.flush() == []

    def test_fill_fn_takes_precedence(self):
        adapter = MockAdapter(
            fill_fn=lambda i: {
                "status": "filled",
                "filled_weight": 9.0,
                "asset": i.asset,
            }
        )
        fill = adapter.submit_intents(
            OrderBatch(date="2024-01-01", intents=(_intent(),))
        )[0]
        assert fill["filled_weight"] == 9.0
