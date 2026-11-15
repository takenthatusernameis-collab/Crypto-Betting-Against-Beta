"""P14-B: execution.py coverage push.

Targets missed branches/lines with fakes/mocks only — no network, no
credentials, no real live execution. Preserves dry-run-safe defaults.
"""

from __future__ import annotations

import builtins
import json
import math
import sys
import types

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.execution import (
    CCXTConnector,
    ExecutionReport,
    LiveExecutionAdapter,
    LiveExecutionReport,
    LiveFill,
    LiveOrder,
    Order,
    OrderBatch,
    OrderIntent,
    PaperAdapter,
    PaperExecutionEngine,
    StrategyDiagnostics,
    _as_timestamp,
    _date_key,
    _finite,
    _safe_float,
    _sanitize_for_json,
    _write_jsonl,
    configure_paper_adapter,
    execution_payload_to_json,
    order_batches_from_weights,
)


def _intent(asset="BTC", order_weight=0.1, date="2024-01-01T00:00:00", **kw):
    return OrderIntent(
        date=date,
        asset=asset,
        target_weight=kw.get("target_weight", order_weight),
        current_weight=kw.get("current_weight", 0.0),
        order_weight=order_weight,
        requested_weight=kw.get("requested_weight", order_weight),
        notional_usd=kw.get("notional_usd"),
        price=kw.get("price"),
        adv_usd=kw.get("adv_usd"),
        max_participation=kw.get("max_participation"),
        metadata=kw.get("metadata", {}),
    )


# --- PaperAdapter price/ADV lookup fallbacks (139-141,164-166,177-178,182-187) ---


def test_paper_price_for_timestamp_fallback_and_nan():
    idx = pd.to_datetime(["2024-01-01"])
    prices = pd.DataFrame({"BTC": [100.0], "ETH": [np.nan]}, index=idx)
    pa = PaperAdapter(prices_df=prices)
    assert pa._price_for("2024-01-01T00:00:00", "BTC") == 100.0
    assert pa._price_for("2024-01-01T00:00:00", "ETH") is None
    assert pa._price_for("2024-01-01T00:00:00", "XRP") is None


def test_paper_price_for_exception_path():
    class BadIndex:
        def __contains__(self, item):
            raise TypeError("boom")

    class BadSeries:
        columns = ["BTC"]

        def __getitem__(self, k):
            return self

        @property
        def index(self):
            return BadIndex()

    class BadPrices:
        columns = ["BTC"]

        def __getitem__(self, k):
            return BadSeries()

    pa = PaperAdapter(prices_df=BadPrices())
    assert pa._price_for("2024-01-01", "BTC") is None


def test_paper_adv_for_dict_series_dataframe_and_exceptions():
    pa = PaperAdapter(adv_usd={"BTC": 1e6, "ETH": None})
    assert pa._adv_for("2024-01-01", "BTC") == 1e6
    assert pa._adv_for("2024-01-01", "ETH") is None

    pa = PaperAdapter(adv_usd=pd.Series({"BTC": 2e6, "ETH": np.nan}))
    assert pa._adv_for("2024-01-01", "BTC") == 2e6
    assert pa._adv_for("2024-01-01", "ETH") is None

    date_idx = pd.to_datetime(["2024-01-01"])
    pa = PaperAdapter(adv_usd=pd.Series([3e6], index=date_idx))
    assert pa._adv_for("2024-01-01T00:00:00", "BTC") == 3e6

    adv_df = pd.DataFrame({"BTC": [4e6], "ETH": [np.nan]}, index=date_idx)
    pa = PaperAdapter(adv_usd=adv_df)
    assert pa._adv_for("2024-01-01T00:00:00", "BTC") == 4e6
    assert pa._adv_for("2024-01-01T00:00:00", "ETH") is None

    adv_df2 = pd.DataFrame([[5e6]], index=["BTC"], columns=date_idx)
    pa = PaperAdapter(adv_usd=adv_df2)
    assert pa._adv_for("2024-01-01T00:00:00", "BTC") == 5e6
    assert PaperAdapter(adv_usd=None)._adv_for("2024-01-01", "BTC") is None


def test_paper_adv_for_exception_path():
    class BadSeries(pd.Series):
        @property
        def _constructor(self):
            return BadSeries

    s = BadSeries({"BTC": 1.0})
    pa = PaperAdapter(adv_usd=s)
    orig = type(s).index
    try:
        type(s).index = property(lambda self: (_ for _ in ()).throw(TypeError("x")))
        assert pa._adv_for("2024-01-01", "BTC") is None
    finally:
        type(s).index = orig


def test_adv_from_frame_value_series_and_timestamp_fallback_and_exceptions():
    date_idx = pd.to_datetime(["2024-01-01"])
    sub = pd.DataFrame({"v": [7e6]}, index=["2024-01-01T00:00:00"])
    assert PaperAdapter._adv_from_frame_value(sub["v"], "2024-01-01T00:00:00") == 7e6

    sub2 = pd.Series([8e6], index=date_idx)
    assert PaperAdapter._adv_from_frame_value(sub2, "2024-01-01T00:00:00") == 8e6

    class SeriesLike(pd.Series):
        @property
        def _constructor(self):
            return SeriesLike

    sub4 = pd.Series([SeriesLike([10e6])], index=date_idx)
    assert PaperAdapter._adv_from_frame_value(sub4, "2024-01-01T00:00:00") == 10e6

    sub5 = pd.Series([np.nan], index=date_idx)
    assert PaperAdapter._adv_from_frame_value(sub5, "2024-01-01T00:00:00") is None
    class Bad:
        @property
        def index(self):
            raise TypeError("boom")

    assert PaperAdapter._adv_from_frame_value(Bad(), "2024-01-01") is None


# --- date/timestamp/finite helpers (380-381,403-404) ---


def test_date_key_and_as_timestamp_fallbacks():
    assert _date_key("2024-01-01").startswith("2024-01-01")
    assert _date_key(object())
    assert _as_timestamp("2024-01-01") is not None
    assert _as_timestamp(object()) is None
    assert _finite("1.5") == 1.5
    assert _finite("bad", 3.0) == 3.0
    assert _finite(float("inf"), 2.0) == 2.0


# --- order_batches_from_weights edge/error branches (463-464,472-473,479-480,505-506) ---


def test_order_batches_empty_and_non_dataframe():
    assert order_batches_from_weights(pd.DataFrame()) == []
    assert order_batches_from_weights(None) == []  # type: ignore[arg-type]


def test_order_batches_adv_exception_and_bad_dates_and_values():
    idx = [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")]
    w = pd.DataFrame({"BTC": ["bad", float("nan")], "ETH": [0.5, 0.5]}, index=idx)

    class Boom:
        pass

    batches = order_batches_from_weights(w, adv_usd=Boom())
    assert isinstance(batches, list)

    adv_idx = pd.to_datetime(["2024-01-02"])
    adv_df = pd.DataFrame({"BTC": ["bad"], "ETH": [1e6]}, index=adv_idx)
    prices = pd.DataFrame({"BTC": ["bad"], "ETH": [100.0]}, index=["2024-01-02"])
    batches2 = order_batches_from_weights(
        pd.DataFrame({"BTC": [0.1], "ETH": [0.2]}, index=["2024-01-02"]),
        prices_df=prices,
        adv_usd=adv_df,
    )
    assert len(batches2) >= 1
    intents = [i for b in batches2 for i in b.intents]
    btc = next(i for i in intents if i.asset == "BTC")
    assert btc.price is None


def test_order_batches_series_adv_and_zero_change_skipped():
    idx = pd.to_datetime(["2024-01-01", "2024-01-02"])
    w = pd.DataFrame({"BTC": [0.1, 0.1], "ETH": [0.0, 0.2]}, index=idx)
    adv_s = pd.Series({"BTC": 1e6, "ETH": "bad"})
    batches = order_batches_from_weights(w, adv_usd=adv_s)
    assert sum(len(b.intents) for b in batches) == 2
    eth_intents = [i for b in batches for i in b.intents if i.asset == "ETH"]
    assert eth_intents[0].adv_usd is None


# --- sanitize/json edges (555-556,559-560) ---


def test_sanitize_for_json_numpy_and_nonfinite_and_importerror(monkeypatch):
    assert _sanitize_for_json(np.int64(5)) == 5
    assert _sanitize_for_json(np.float64(1.5)) == 1.5
    assert _sanitize_for_json(np.float64(np.inf)) == 0.0
    assert _sanitize_for_json(np.bool_(True)) is True
    assert _sanitize_for_json(np.array([1, np.nan])) == [1, 0.0]
    assert _sanitize_for_json(pd.Timestamp("2024-01-01")) == "2024-01-01T00:00:00"
    assert _sanitize_for_json(pd.Series([1, 2])) == [1, 2]
    assert _sanitize_for_json(pd.Index([1, 2])) == [1, 2]
    payload = {"x": np.float64(2.0), "y": (1, 2)}
    s = execution_payload_to_json(payload)
    assert json.loads(s)["x"] == 2.0

    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "numpy":
            raise ImportError("no numpy")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    assert isinstance(_sanitize_for_json(object()), str)

# --- PaperExecutionEngine diagnostics/pnl/persist edges (783-784,836-848,851,985,1019) ---


def test_paper_engine_empty_weights_and_persist(tmp_path):
    eng = PaperExecutionEngine(
        log_path=tmp_path / "fills.jsonl", diagnostics_path=tmp_path / "diag.jsonl"
    )
    report = eng.execute(pd.DataFrame(), backtest_pnl=1.23)
    assert isinstance(report, ExecutionReport)
    assert report.n_orders == 0 and report.backtest_pnl == 1.23
    assert (tmp_path / "fills.jsonl").exists()
    assert (tmp_path / "diag.jsonl").exists()


def test_paper_engine_betas_no_index_and_pnl_edge_cases():
    idx = pd.to_datetime(["2024-01-01", "2024-01-02"])

    class RowNoIndex(pd.Series):
        @property
        def _constructor(self):
            return RowNoIndex

        @property
        def index(self):
            raise AttributeError("no index")

    eng = PaperExecutionEngine()
    diag = eng._diagnostics_for_date(
        "2024-01-01T00:00:00", pd.Series({"BTC": 0.5}), RowNoIndex([1.0]), {"BTC": 0.0}
    )
    assert isinstance(diag, StrategyDiagnostics)

    eng2 = PaperExecutionEngine()
    assert eng2._paper_pnl(None) is None
    assert eng2._paper_pnl(pd.DataFrame()) is None
    eng2.fills = [  # type: ignore[assignment]
        types.SimpleNamespace(date="not-a-date", asset="BTC", weight=1.0),
        types.SimpleNamespace(date="2024-01-02T00:00:00", asset="XRP", weight=1.0),
        types.SimpleNamespace(date="2024-01-01T00:00:00", asset="BTC", weight=1.0),
        types.SimpleNamespace(date="2024-01-01T00:00:00", asset="ETH", weight=1.0),
    ]
    ret = pd.DataFrame({"BTC": [np.nan, np.inf], "ETH": [0.1, 0.2]}, index=idx)
    pnl = eng2._paper_pnl(ret)
    assert pnl is not None and math.isfinite(pnl)

    eng3 = PaperExecutionEngine()
    weights2 = pd.DataFrame({"BTC": [0.1, -0.1]}, index=idx)
    betas2 = pd.DataFrame(
        {"BTC": [1.0, 1.1]},
        index=[pd.Timestamp("2099-01-01"), pd.Timestamp("2099-01-02")],
    )
    report = eng3.execute(weights2, betas_df=betas2, returns_df=ret, backtest_pnl=0.0)
    assert report.n_fills >= 1


def test_safe_float_and_write_jsonl(tmp_path):
    assert _safe_float(None, 5) == 5.0
    assert _safe_float("bad", 3) == 3.0
    assert _safe_float(float("inf"), 1) == 1.0
    out = tmp_path / "nested" / "x.jsonl"
    _write_jsonl(out, [{"a": np.int64(1)}, {"b": math.nan}])
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["a"] == 1


def test_configure_paper_adapter_paths():
    pa = PaperAdapter()
    assert configure_paper_adapter(pa, types.SimpleNamespace(config=None)) is pa

    class Cfg:
        partial_fill = True
        max_participation = 0.25
        prices = pd.DataFrame({"BTC": [1.0]})
        adv_usd = {"BTC": 100.0}

    strat = types.SimpleNamespace(config=Cfg())
    strat._resolve_cost_model = lambda cfg: (_ for _ in ()).throw(RuntimeError("boom"))
    out = configure_paper_adapter(PaperAdapter(), strat)
    assert out.partial_fill is True
    assert out.prices is not None and out.adv_usd is not None
    assert out.max_participation == 0.25

    pa2 = PaperAdapter(max_participation=0.05)
    configure_paper_adapter(pa2, strat)
    assert pa2.max_participation == 0.05


def test_live_order_fill_report_to_dict():
    lo = LiveOrder("k", "2024-01-01", "BTC", "buy", 1.0)
    assert lo.to_dict()["idempotency_key"] == "k"
    lf = LiveFill("k", "2024-01-01", "BTC", "buy", 1.0, status="partial", reason="r")
    d = lf.to_dict()
    assert d["status"] == "partial" and d["reason"] == "r"


class FakeExchange:
    def __init__(self, config=None, raise_on_create=False):
        self.config = config or {}
        self.raise_on_create = raise_on_create
        self.loaded = False
        self.closed = False

    def load_markets(self):
        self.loaded = True
        return {"BTC/USDT": {}}

    def close(self):
        self.closed = True

    def create_order(self, **kw):
        if self.raise_on_create:
            raise RuntimeError("reject")
        return {"filled": 1.0, "average": 100.0, "cost": 100.0, "status": "closed"}

    def fetch_balance(self):
        return {"ok": True}

    def fetch_ticker(self, symbol):
        return {"last": 1.0, "symbol": symbol}


def test_ccxt_import_error(monkeypatch):
    conn = CCXTConnector("binance", dry_run=True)
    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "ccxt":
            raise ImportError("missing")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(RuntimeError):
        conn.connect()

def test_ccxt_connect_disconnect_dry_and_real_and_cancel_status(monkeypatch):
    fake_ccxt = types.SimpleNamespace(binance=lambda config: FakeExchange(config))
    monkeypatch.setitem(sys.modules, "ccxt", fake_ccxt)

    conn = CCXTConnector(
        "binance", api_key="k", api_secret="s", api_password="p", dry_run=True, testnet=True
    )
    conn.connect()
    assert conn.is_connected()
    conn.connect()
    order = LiveOrder("i1", "2024-01-01", "BTC", "buy", 1.0, price=100.0, notional_usd=100.0)
    fill = conn.submit_order(order)
    assert fill.status == "filled" and fill.metadata.get("dry_run") is True
    assert conn.get_order_status("i1") is not None
    fill2 = conn.submit_order(order)
    assert fill2.status == "rejected"
    assert conn.cancel_order("i1") is True
    assert conn.get_order_status("i1").status == "cancelled"
    assert conn.cancel_order("missing") is False
    assert "USDT" in conn.fetch_balance()
    assert conn.fetch_ticker("BTC/USDT")["last"] == 1.0
    conn.disconnect()
    assert not conn.is_connected()

    fake_ccxt2 = types.SimpleNamespace(binance=lambda config: FakeExchange(config))
    monkeypatch.setitem(sys.modules, "ccxt", fake_ccxt2)
    conn2 = CCXTConnector("binance", api_key="k", api_secret="s", dry_run=False)
    conn2.connect()
    assert conn2._exchange.loaded is True
    order2 = LiveOrder("", "2024-01-01", "BTC", "buy", 1.0, price=100.0, notional_usd=100.0)
    fill3 = conn2.submit_order(order2)
    assert fill3.status == "filled"
    assert conn2.fetch_balance() == {"ok": True}
    assert conn2.fetch_ticker("BTC/USDT")["symbol"] == "BTC/USDT"
    assert conn2.cancel_order(fill3.idempotency_key) is False
    conn2.disconnect()

    fake_ccxt3 = types.SimpleNamespace(
        binance=lambda config: FakeExchange(config, raise_on_create=True)
    )
    monkeypatch.setitem(sys.modules, "ccxt", fake_ccxt3)
    conn3 = CCXTConnector("binance", dry_run=False)
    conn3.connect()
    fill4 = conn3.submit_order(LiveOrder("i3", "2024-01-01", "BTC", "buy", 1.0))
    assert fill4.status == "rejected"

    fake_ccxt4 = types.SimpleNamespace()
    monkeypatch.setitem(sys.modules, "ccxt", fake_ccxt4)
    conn4 = CCXTConnector("nope", dry_run=True)
    with pytest.raises(ValueError):
        conn4.connect()


def test_ccxt_not_connected_guards():
    conn = CCXTConnector("binance", dry_run=True)
    with pytest.raises(RuntimeError):
        conn.submit_order(LiveOrder("i", "2024-01-01", "BTC", "buy", 1.0))
    with pytest.raises(RuntimeError):
        conn.fetch_balance()
    with pytest.raises(RuntimeError):
        conn.fetch_ticker("BTC/USDT")
    assert conn.cancel_order("x") is False
    assert conn.get_order_status("x") is None
    assert conn._asset_to_symbol("btc") == "BTC/USDT"


class StubConnector:
    def __init__(self, status="filled"):
        self.status = status
        self.connected = False
        self.submitted = []

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def is_connected(self):
        return self.connected

    def submit_order(self, order: LiveOrder) -> LiveFill:
        self.submitted.append(order)
        return LiveFill(
            order.idempotency_key,
            order.date,
            order.asset,
            order.side,
            order.weight,
            price=order.price,
            notional_usd=order.notional_usd,
            slippage=0.0,
            status=self.status,
            reason=None,
            metadata={"max_participation": order.max_participation},
        )

    def cancel_order(self, idem_key):
        return False

    def get_order_status(self, idem_key):
        return None

    def fetch_balance(self):
        return {}

    def fetch_ticker(self, symbol):
        return {}


def test_live_adapter_partial_rejected_flush_health_disconnect():
    batch = OrderBatch("2024-01-01T00:00:00", (_intent("BTC", 0.2), _intent("ETH", -0.1)))
    conn = StubConnector(status="partial")
    adapter = LiveExecutionAdapter(connector=conn, dry_run=True)
    fills = adapter.submit_intents(batch)
    assert all(f["status"] == "partial" and f["fill_ratio"] == 0.5 for f in fills)
    assert fills[1]["side"] == "sell" and fills[1]["filled_weight"] < 0
    assert adapter.flush() == []
    assert adapter.get_submitted() and adapter.get_fills()
    h = adapter.health_check()
    assert h["connected"] is True and h["n_fills"] == 2
    adapter.disconnect()
    assert adapter.health_check()["connected"] is False

    conn2 = StubConnector(status="rejected")
    adapter2 = LiveExecutionAdapter(connector=conn2)
    fills2 = adapter2.submit_intents(batch)
    assert all(f["status"] == "rejected" and f["fill_ratio"] == 0.0 for f in fills2)


class RejectRiskManager:
    def __init__(self, mode="asset"):
        self.mode = mode
        self._kill_switch_triggered = False

    def pre_trade_check(self, batch, current_positions, cumulative, date):
        if self.mode == "asset":
            return types.SimpleNamespace(
                allowed=True,
                rejected_intents=[{"asset": "BTC", "reason": "too_big"}],
            )
        if self.mode == "portfolio":
            return types.SimpleNamespace(
                allowed=False,
                rejected_intents=[{"asset": "portfolio", "reason": "breach"}],
            )
        if self.mode == "kill":
            self._kill_switch_triggered = True
            return types.SimpleNamespace(allowed=False, rejected_intents=[])
        return types.SimpleNamespace(allowed=True, rejected_intents=[])


def test_live_adapter_risk_rejections():
    batch = OrderBatch("2024-01-01T00:00:00", (_intent("BTC", 0.2), _intent("ETH", -0.1)))
    adapter = LiveExecutionAdapter(
        connector=StubConnector(), risk_manager=RejectRiskManager("asset")
    )
    fills = adapter.submit_intents(batch)
    assert fills[0]["status"] == "rejected" and fills[0]["reason"] == "too_big"
    assert fills[1]["status"] in ("filled", "partial", "rejected")

    adapter2 = LiveExecutionAdapter(
        connector=StubConnector(), risk_manager=RejectRiskManager("portfolio")
    )
    fills2 = adapter2.submit_intents(batch)
    assert all(
        f["status"] == "rejected" and f["reason"] == "portfolio_limit_breach" for f in fills2
    )

    adapter3 = LiveExecutionAdapter(
        connector=StubConnector(), risk_manager=RejectRiskManager("kill")
    )
    fills3 = adapter3.submit_intents(batch)
    assert all(f["status"] == "rejected" for f in fills3)


def test_live_adapter_env_credentials_and_lazy_connector(monkeypatch):
    monkeypatch.setenv("K1", "k")
    monkeypatch.setenv("S1", "s")
    monkeypatch.setenv("P1", "p")
    adapter = LiveExecutionAdapter(
        api_key_env="K1",
        api_secret_env="S1",
        api_password_env="P1",
        connector=StubConnector(),
    )
    assert adapter._api_key == "k"
    assert adapter._api_secret == "s"
    assert adapter._api_password == "p"
    pos = pd.Series({"BTC": 1.0})
    adapter2 = LiveExecutionAdapter(connector=StubConnector(), current_positions=pos)
    assert adapter2.current_positions is not pos


# --- execution.py remaining missed branches ---
# 139-141, 182-185, 463-464, 472-473, 555-556, 591, 692, 847-848,
# 1047, 1281, 1386, 1389


def test_price_for_timestamp_fallback_object_index():
    # string date_key not in Index-of-Timestamps; Timestamp fallback hits (139-141)
    idx = pd.Index([pd.Timestamp("2024-01-01")])
    prices = pd.DataFrame({"BTC": [100.0]}, index=idx)
    pa = PaperAdapter(prices_df=prices)
    assert pa._price_for("2024-01-01", "BTC") == 100.0


def test_adv_from_frame_value_timestamp_and_series_branch():
    # Timestamp fallback path (182-185) incl. isinstance-Series branch (183-184)
    sub = pd.DataFrame({"x": [1e6]}, index=pd.Index([pd.Timestamp("2024-01-01")]))
    assert PaperAdapter._adv_from_frame_value(sub, "2024-01-01") == 1e6


def test_order_batches_adv_map_exception_path():
    # adv_usd DataFrame whose sort_index raises -> adv_map = {} (463-464)
    idx = [pd.Timestamp("2024-01-01")]
    w = pd.DataFrame({"BTC": [0.1]}, index=idx)
    df = pd.DataFrame({"BTC": [1e6]}, index=idx)
    df.sort_index = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("nope"))
    batches = order_batches_from_weights(w, adv_usd=df)
    assert isinstance(batches, list)


def test_order_batches_bad_date_key_fallback():
    # pd.Timestamp(date) raises -> date_key = str(date) (472-473)
    w = pd.DataFrame({"BTC": [0.1]}, index=["bad-date-string"])
    batches = order_batches_from_weights(w)
    assert isinstance(batches, list)


def test_sanitize_for_json_nonfinite_numpy_float():
    assert _sanitize_for_json(np.float64(np.nan)) == 0.0
    assert _sanitize_for_json(np.float64(-np.inf)) == 0.0


def test_order_to_dict():
    o = Order(
        date="2024-01-01",
        asset="BTC",
        side="buy",
        weight=0.5,
        price=100.0,
        notional_usd=50.0,
    )
    d = o.to_dict()
    assert d["date"] == "2024-01-01" and d["asset"] == "BTC" and d["weight"] == 0.5


def test_execution_report_to_dict():
    eng = PaperExecutionEngine()
    report = eng.execute(pd.DataFrame(), backtest_pnl=1.23)
    d = report.to_dict()
    assert d["backtest_pnl"] == 1.23 and d["n_orders"] == 0 and d["mode"] == "paper"


def test_paper_pnl_non_convertible_return_value():
    # ret.loc[nxt, asset] raises ValueError -> continue (847-848)
    eng = PaperExecutionEngine()
    eng.fills = [  # type: ignore[assignment]
        types.SimpleNamespace(date="2023-12-31T00:00:00", asset="BTC", weight=1.0)
    ]
    ret = pd.DataFrame(
        {"BTC": ["bad", 0.1]}, index=pd.to_datetime(["2024-01-01", "2024-01-02"])
    )
    pnl = eng._paper_pnl(ret)
    assert pnl is not None and math.isfinite(pnl)


def test_live_execution_report_to_dict():
    report = LiveExecutionReport(mode="live", exchange="kraken", n_orders=1, n_fills=1)
    d = report.to_dict()
    assert d["mode"] == "live" and d["exchange"] == "kraken" and d["n_orders"] == 1


def test_cancel_order_dry_run_cache_miss(monkeypatch):
    fake_ccxt = types.SimpleNamespace(binance=lambda config: FakeExchange(config))
    monkeypatch.setitem(sys.modules, "ccxt", fake_ccxt)
    conn = CCXTConnector("binance", dry_run=True)
    conn.connect()
    conn._idempotency_keys.add("ghost-key")  # in keys, not in order cache
    assert conn.cancel_order("ghost-key") is False  # 1281


def test_ensure_connected_early_return_and_create_connector(monkeypatch):
    fake_ccxt = types.SimpleNamespace(binance=lambda config: FakeExchange(config))
    monkeypatch.setitem(sys.modules, "ccxt", fake_ccxt)
    adapter = LiveExecutionAdapter(exchange="binance", dry_run=True)
    assert adapter.connector is None and adapter._connected is False
    # early return when already connected (1386)
    adapter._connected = True
    adapter._ensure_connected()
    assert adapter.connector is None
    # create-connector path (1388-1389)
    adapter2 = LiveExecutionAdapter(exchange="binance", dry_run=True)
    adapter2._ensure_connected()
    assert adapter2._connected is True
    assert isinstance(adapter2.connector, CCXTConnector)
    assert adapter2.connector.is_connected()
