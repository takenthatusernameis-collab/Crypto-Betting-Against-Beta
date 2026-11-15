"""P12-D coverage campaign for risk.py and data_sources.py final gaps.

Covers real missed branches with fakes/mocks only (no network, no credentials):
risk.py drawdown/kill-switch, RiskManager limits and pre-trade checks, and
data_sources.py feed health/gaps, CCXT/WebSocket connect paths, ticker fetch
error handling, and DataFrame freshness validation. No production logic is
modified.
"""

from __future__ import annotations

from unittest import mock

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_sources import (
    BABDataError as DS_BABDataError,
)
from strategies.betting_against_beta.data_sources import (
    CCXTFeed,
    FeedHealth,
    RealtimeFeed,
    WebSocketFeed,
    validate_freshness,
)
from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.risk import (
    RiskLimits,
    RiskManager,
    _compute_gross_exposure,
    _compute_hhi,
    _compute_net_exposure,
    _compute_turnover,
    _finite,
    apply_kill_switch,
    compute_running_drawdown,
)

# ---------------------------------------------------------------------------
# compute_running_drawdown
# ---------------------------------------------------------------------------

def test_compute_running_drawdown_none():
    assert compute_running_drawdown(None).empty


def test_compute_running_drawdown_unconvertible():
    class Weird:
        pass
    assert compute_running_drawdown(Weird()).empty


def test_compute_running_drawdown_empty():
    out = compute_running_drawdown(pd.Series(dtype="float64"))
    assert out.empty


def test_compute_running_drawdown_normal():
    c = pd.Series([1.0, 1.1, 0.9, 0.5, 1.05])
    dd = compute_running_drawdown(c)
    assert (dd <= 0.0).all()
    assert dd.iloc[0] == 0.0


# ---------------------------------------------------------------------------
# apply_kill_switch
# ---------------------------------------------------------------------------

def _cum(breach=False):
    if breach:
        # Path that breaches a 0.2 drawdown limit.
        return pd.Series([1.0, 0.9, 0.7, 0.4, 0.5], index=pd.date_range("2023-01-01", periods=5))
    return pd.Series([1.0, 1.1, 1.05, 1.02], index=pd.date_range("2023-01-01", periods=4))


def _weights():
    return pd.DataFrame({"BTC": [0.5, -0.5, 0.5, -0.5]}, index=_cum().index)


def test_apply_kill_switch_limit_none():
    w, ev = apply_kill_switch(_weights(), _cum(), limit=None)
    assert not ev.triggered
    pd.testing.assert_frame_equal(w, _weights())


def test_apply_kill_switch_invalid_limits():
    for bad in (True, "0.5", float("nan"), float("inf"), 0.0, 1.5, -0.1):
        _w, ev = apply_kill_switch(_weights(), _cum(), limit=bad)
        assert not ev.triggered


def test_apply_kill_switch_weights_none_or_empty():
    _w, ev = apply_kill_switch(None, _cum(), limit=0.2)
    assert not ev.triggered
    _w2, ev2 = apply_kill_switch(pd.DataFrame(), _cum(), limit=0.2)
    assert not ev2.triggered


def test_apply_kill_switch_empty_drawdown():
    _w, ev = apply_kill_switch(_weights(), pd.Series(dtype="float64"), limit=0.2)
    assert not ev.triggered


def test_apply_kill_switch_no_breach():
    _w, ev = apply_kill_switch(_weights(), _cum(breach=False), limit=0.2)
    assert not ev.triggered


def test_apply_kill_switch_breach_flattens():
    cum = _cum(breach=True)
    w = _weights()
    out, ev = apply_kill_switch(w, cum, limit=0.2)
    assert ev.triggered
    assert ev.date is not None
    assert ev.limit == 0.2
    assert ev.observed_drawdown < -0.2
    # Weights zeroed from breach date onward.
    breach_pos = out.index.get_loc(ev.date)
    assert (out.iloc[breach_pos:] == 0.0).all().all()


# ---------------------------------------------------------------------------
# RiskLimits validation
# ---------------------------------------------------------------------------

def test_risk_limits_validation_errors():
    with pytest.raises(ValueError, match="must be a number"):
        RiskLimits(max_gross_exposure="big")
    with pytest.raises(ValueError, match="finite and non-negative"):
        RiskLimits(max_gross_exposure=-1.0)
    with pytest.raises(ValueError, match="positive integer"):
        RiskLimits(max_position_age_days=0)


# ---------------------------------------------------------------------------
# RiskManager helpers
# ---------------------------------------------------------------------------

def test_finite_and_exposure_helpers():
    assert _finite(np.nan) == 0.0
    assert _finite("abc") == 0.0
    assert _finite(1.5) == 1.5
    s = pd.Series([0.5, -0.3, 0.2])
    assert _compute_gross_exposure(s) == 1.0
    assert abs(_compute_net_exposure(s) - 0.4) < 1e-12
    assert _compute_hhi(pd.Series(dtype="float64")) == 0.0
    cur = pd.Series({"BTC": 0.5, "ETH": -0.5})
    tgt = pd.Series({"BTC": 0.8, "ETH": -0.2})
    assert _compute_turnover(cur, tgt) > 0


# ---------------------------------------------------------------------------
# RiskManager pre_trade_check branches
# ---------------------------------------------------------------------------

def _intent(asset, weight):
    return type("Intent", (), {"asset": asset, "target_weight": weight})()


def _batch(intents):
    return type("Batch", (), {"intents": intents})()


def test_pre_trade_check_asset_limit_rejection():
    mgr = RiskManager(RiskLimits(max_position_weight=0.1))
    res = mgr.pre_trade_check(_batch([_intent("BTC", 0.5)]), pd.Series({"BTC": 0.0}))
    assert not res.allowed
    assert len(res.rejected_intents) == 1
    assert len(res.events) >= 1


def test_pre_trade_check_portfolio_limit_rejects_batch():
    mgr = RiskManager(RiskLimits(max_position_weight=1.0, max_gross_exposure=0.5))
    res = mgr.pre_trade_check(
        _batch([_intent("BTC", 0.4), _intent("ETH", 0.4)]), pd.Series({"BTC": 0.0, "ETH": 0.0})
    )
    assert not res.allowed
    # Portfolio limit breach adds rejection with asset="portfolio"
    # and emits a limit_breach event
    assert len(res.events) >= 1
    assert any(e.event_type == "limit_breach" and e.severity == "warning" for e in res.events)
    assert any(r.get("asset") == "portfolio" for r in res.rejected_intents)
    # The rejection is added to rejected_intents with asset="portfolio"
    # but the code also checks if rejected is empty for allowed - so we just verify events


def test_pre_trade_check_position_age_violation():
    mgr = RiskManager(RiskLimits(max_position_age_days=1))
    # First day: position starts, age 1, not > 1 yet OK.
    res = mgr.pre_trade_check(
        _batch([_intent("BTC", 0.2)]), pd.Series({"BTC": 0.0}), date="2023-01-01"
    )
    assert res.allowed
    # Second day same position: age 2 > 1 -> violation (emits warning event, doesn't reject)
    res2 = mgr.pre_trade_check(
        _batch([_intent("BTC", 0.2)]), pd.Series({"BTC": 0.2}), date="2023-01-02"
    )
    # Position age violation adds warning event but doesn't reject the trade
    assert res2.allowed
    assert any("position age" in e.message for e in res2.events)
    assert any(e.event_type == "limit_breach" and e.severity == "warning" for e in res2.events)


def test_pre_trade_check_drawdown_kill_switch_flattens():
    mgr = RiskManager(RiskLimits(max_drawdown=0.2), kill_switch_enabled=True)
    cum = pd.Series([1.0, 0.9, 0.7, 0.4], index=pd.date_range("2023-01-01", periods=4))
    res = mgr.pre_trade_check(
        _batch([_intent("BTC", 0.2)]), pd.Series({"BTC": 0.0}), cumulative=cum
    )
    assert not res.allowed
    assert mgr._kill_switch_triggered
    assert any(e.event_type == "kill_switch" for e in res.events)
    assert any(e.event_type == "position_flattened" for e in res.events)


def test_pre_trade_check_turnover_breach():
    mgr = RiskManager(RiskLimits(max_position_weight=1.0, max_daily_turnover=0.1))
    res = mgr.pre_trade_check(
        _batch([_intent("BTC", 0.9)]), pd.Series({"BTC": 0.0}), date="2023-01-01"
    )
    # Turnover breach emits warning event but doesn't reject the trade
    assert res.allowed
    assert any("turnover" in e.message.lower() for e in res.events)
    assert any(e.event_type == "limit_breach" for e in res.events)


def test_pre_trade_check_allowed_when_clean():
    mgr = RiskManager(RiskLimits(max_position_weight=1.0))
    res = mgr.pre_trade_check(_batch([_intent("BTC", 0.2)]), pd.Series({"BTC": 0.0}))
    assert res.allowed


def test_check_kill_switch_disabled_or_no_limit():
    mgr = RiskManager(RiskLimits(max_drawdown=None), kill_switch_enabled=False)
    triggered, ev = mgr.check_kill_switch(pd.Series([1.0, 0.9]))
    assert not triggered
    assert not ev.triggered


def test_flatten_positions_and_events():
    mgr = RiskManager()
    out = mgr.flatten_positions(pd.Series({"BTC": 0.5, "ETH": -0.3}))
    assert (out == 0.0).all()
    assert len(mgr.get_events()) >= 1
    mgr.clear_events()
    assert mgr.get_events() == []


def test_update_prices_exception_swallowed():
    mgr = RiskManager()
    # Pass a DataFrame-like object that passes `prices is not None and not prices.empty`
    # but fails at `prices.iloc[-1]`
    class BadFrame:
        def __bool__(self):
            return True
        @property
        def empty(self):
            return False
        def __getattr__(self, name):
            if name == "iloc":
                raise AttributeError("no iloc")
            raise AttributeError(name)
    mgr.update_prices(BadFrame())  # exception path swallowed
    assert mgr.get_position_value(pd.Series({"BTC": 0.5})) == 0.0


def test_get_position_value_none_or_empty_prices():
    mgr = RiskManager()
    assert mgr.get_position_value(pd.Series({"BTC": 0.5})) == 0.0
    mgr.update_prices(pd.DataFrame())
    assert mgr.get_position_value(pd.Series({"BTC": 0.5})) == 0.0


def test_get_position_value_exception_path():
    mgr = RiskManager()
    # Set current_prices to a DataFrame-like that has .empty=False but fails at .iloc[-1]
    class BadFrame:
        @property
        def empty(self):
            return False
        def __getattr__(self, name):
            if name == "iloc":
                raise AttributeError("no iloc")
            raise AttributeError(name)
    mgr.current_prices = BadFrame()
    assert mgr.get_position_value(pd.Series({"BTC": 0.5})) == 0.0


# ---------------------------------------------------------------------------
# data_sources.py feed health / gaps (gap_seconds branch)
# ---------------------------------------------------------------------------

def test_feed_health_gap_seconds_with_multiple_ticks():
    feed = RealtimeFeed(["BTC", "ETH"], max_staleness_seconds=200.0, max_gap_seconds=100.0)
    feed._connected = True
    now = 1_000_000.0
    feed.validate_freshness(
        {
            "BTC": {"price": 1.0, "timestamp": now - 100},
            "ETH": {"price": 2.0, "timestamp": now - 50},
        },
        now=now,
    )
    # Second validate_freshness call creates a gap between ticks for BTC.
    feed.validate_freshness(
        {
            "BTC": {"price": 1.0, "timestamp": now - 10},
            "ETH": {"price": 2.0, "timestamp": now - 50},
        },
        now=now,
    )
    health = feed.health_check()
    assert isinstance(health, FeedHealth)
    assert health.gap_seconds is not None


def test_feed_health_missing_symbol_and_stale_tick():
    feed = RealtimeFeed(["BTC"], max_staleness_seconds=200.0)
    feed._connected = True
    with pytest.raises(DS_BABDataError, match="Missing data for required symbol"):
        feed.validate_freshness({}, now=1_000_000.0)
    # Timestamp is 999999 seconds old, well within 200s staleness limit
    feed.validate_freshness({"BTC": {"price": 1.0, "timestamp": 999999.0}}, now=1_000_000.0)
    # Now make it stale
    with pytest.raises(DS_BABDataError, match="Staleness SLA violation"):
        feed.validate_freshness({"BTC": {"price": 1.0, "timestamp": 1.0}}, now=1_000_000.0)


# ---------------------------------------------------------------------------
# CCXTFeed connect paths (dry-run, no network)
# ---------------------------------------------------------------------------

def test_ccxt_connect_already_connected_returns():
    feed = CCXTFeed(["BTC"], dry_run=True)
    feed._connected = True
    # Should return early without touching ccxt.
    feed.connect()
    assert feed._connected


@mock.patch("strategies.betting_against_beta.data_sources.CCXTFeed._get_ccxt")
def test_ccxt_connect_config_includes_creds_and_testnet(mock_get_ccxt):
    mock_ccxt = mock.MagicMock()
    mock_exchange_class = mock.MagicMock()
    mock_ccxt.binance = mock_exchange_class
    mock_get_ccxt.return_value = mock_ccxt
    feed = CCXTFeed(
        ["BTC"], exchange="binance", dry_run=True, api_key="k", api_secret="s", testnet=True
    )
    feed.connect()
    # exchange_class(config) was constructed; verify construct call args.
    constructed = mock_exchange_class.call_args
    assert constructed is not None
    cfg = constructed.args[0]
    assert cfg["enableRateLimit"] is True
    assert cfg["apiKey"] == "k"
    assert cfg["secret"] == "s"
    assert cfg["options"] == {"defaultType": "future"}
    assert feed._connected


@mock.patch("strategies.betting_against_beta.data_sources.CCXTFeed._get_ccxt")
def test_ccxt_fetch_latest_non_dry_run_fetch_error(mock_get_ccxt):
    mock_ccxt = mock.MagicMock()
    mock_exchange = mock.MagicMock()
    mock_ccxt.binance.return_value = mock_exchange
    mock_exchange.fetch_ticker.side_effect = RuntimeError("down")
    mock_get_ccxt.return_value = mock_ccxt
    feed = CCXTFeed(["BTC"], exchange="binance", dry_run=False, api_key="k")
    feed.connect()
    assert feed._connected
    with pytest.raises(DS_BABDataError, match="Failed to fetch ticker for BTC"):
        feed.fetch_latest()
    assert feed._error == "down"


# ---------------------------------------------------------------------------
# WebSocketFeed connect already-connected early return
# ---------------------------------------------------------------------------

class _ConcreteWS(WebSocketFeed):
    def _connect_ws(self):
        pass

    def _disconnect_ws(self):
        pass

    def _on_message(self, message):
        pass


def test_websocket_connect_already_connected_returns():
    feed = _ConcreteWS(["BTC"], url="wss://example")
    feed._connected = True
    feed.connect()
    assert feed._connected


# ---------------------------------------------------------------------------
# validate_freshness (DataFrame) branches
# ---------------------------------------------------------------------------

def test_validate_freshness_none_or_empty():
    with pytest.raises(DS_BABDataError, match="Empty returns data"):
        validate_freshness(None)
    with pytest.raises(DS_BABDataError, match="Empty returns data"):
        validate_freshness(pd.DataFrame())


def test_validate_freshness_numeric_index_rejected():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=[0, 1])
    with pytest.raises(DS_BABDataError, match="Index cannot be parsed as datetime"):
        validate_freshness(df)


def test_validate_freshness_unparseable_index():
    df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=["not-a-date", "also-not"])
    with pytest.raises(DS_BABDataError, match="Index cannot be parsed as datetime"):
        validate_freshness(df)


def test_validate_freshness_reference_date_unparseable():
    df = pd.DataFrame({"BTC": [0.01]}, index=pd.date_range("2023-01-01", periods=1))
    with pytest.raises(DS_BABDataError, match="reference_date cannot be parsed as datetime"):
        validate_freshness(df, reference_date="not-a-date")


def test_validate_freshness_passes_with_fixed_reference():
    df = pd.DataFrame({"BTC": [0.01]}, index=pd.date_range("2023-01-01", periods=1))
    assert validate_freshness(df, reference_date="2023-01-02") is True


def test_validate_freshness_stale_raises():
    df = pd.DataFrame({"BTC": [0.01]}, index=pd.date_range("2020-01-01", periods=1))
    with pytest.raises(DS_BABDataError, match="Data staleness"):
        validate_freshness(df, reference_date="2023-01-02")
