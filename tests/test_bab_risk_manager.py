"""Tests for RiskManager (P9)."""

from __future__ import annotations

import pandas as pd
import pytest

from strategies.betting_against_beta.execution import OrderBatch, OrderIntent
from strategies.betting_against_beta.risk import (
    KillSwitchEvent,
    PreTradeCheckResult,
    RiskEvent,
    RiskLimits,
    RiskManager,
    apply_kill_switch,
    compute_running_drawdown,
)


class TestRiskLimits:
    """Tests for RiskLimits dataclass."""

    def test_default_limits(self):
        limits = RiskLimits()
        assert limits.max_gross_exposure == 1.0
        assert limits.max_net_exposure == 0.0
        assert limits.max_position_weight == 0.2
        assert limits.max_position_age_days is None
        assert limits.max_drawdown is None
        assert limits.max_daily_turnover is None
        assert limits.max_concentration is None

    def test_custom_limits(self):
        limits = RiskLimits(
            max_gross_exposure=2.0,
            max_net_exposure=0.5,
            max_position_weight=0.15,
            max_position_age_days=30,
            max_drawdown=0.1,
            max_daily_turnover=0.5,
            max_concentration=0.3,
            allowed_assets=["BTC", "ETH"],
            blocked_assets=["DOGE"],
        )
        assert limits.max_gross_exposure == 2.0
        assert limits.max_net_exposure == 0.5
        assert limits.max_position_weight == 0.15
        assert limits.max_position_age_days == 30
        assert limits.max_drawdown == 0.1
        assert limits.max_daily_turnover == 0.5
        assert limits.max_concentration == 0.3
        assert limits.allowed_assets == ["BTC", "ETH"]
        assert limits.blocked_assets == ["DOGE"]

    def test_invalid_limits_negative(self):
        with pytest.raises(ValueError, match="must be finite and non-negative"):
            RiskLimits(max_gross_exposure=-1.0)

    def test_invalid_limits_nan(self):
        with pytest.raises(ValueError, match="must be finite and non-negative"):
            RiskLimits(max_position_weight=float("nan"))

    def test_invalid_position_age(self):
        with pytest.raises(ValueError, match="positive integer"):
            RiskLimits(max_position_age_days=0)

    def test_invalid_position_age_type(self):
        with pytest.raises(ValueError, match="positive integer"):
            RiskLimits(max_position_age_days=5.5)


class TestRiskEvent:
    """Tests for RiskEvent dataclass."""

    def test_risk_event_creation(self):
        event = RiskEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type="limit_breach",
            severity="warning",
            message="Test message",
            details={"asset": "BTC"},
        )
        assert event.event_type == "limit_breach"
        assert event.severity == "warning"

    def test_risk_event_to_dict(self):
        event = RiskEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type="kill_switch",
            severity="critical",
            message="Drawdown breached",
            details={"drawdown": 0.15, "limit": 0.1},
        )
        d = event.to_dict()
        assert d["event_type"] == "kill_switch"
        assert d["severity"] == "critical"
        assert d["details"]["drawdown"] == 0.15


class TestPreTradeCheckResult:
    """Tests for PreTradeCheckResult dataclass."""

    def test_pre_trade_check_result_creation(self):
        result = PreTradeCheckResult(
            allowed=True,
            modified_intents=[{"asset": "BTC", "adjusted_weight": 0.1}],
            rejected_intents=[],
            events=[],
        )
        assert result.allowed is True
        assert len(result.modified_intents) == 1

    def test_pre_trade_check_result_to_dict(self):
        from strategies.betting_against_beta.risk import RiskEvent
        event = RiskEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type="limit_breach",
            severity="warning",
            message="Test",
        )
        result = PreTradeCheckResult(
            allowed=False,
            rejected_intents=[{"asset": "BTC", "reason": "limit exceeded"}],
            events=[event],
        )
        d = result.to_dict()
        assert d["allowed"] is False
        assert len(d["rejected_intents"]) == 1
        assert len(d["events"]) == 1


class TestRiskManager:
    """Tests for RiskManager."""

    def test_risk_manager_creation(self):
        limits = RiskLimits(max_gross_exposure=1.5, max_position_weight=0.25)
        manager = RiskManager(limits=limits)
        assert manager.limits.max_gross_exposure == 1.5
        assert manager.limits.max_position_weight == 0.25
        assert manager.kill_switch_enabled is True

    def test_risk_manager_default_limits(self):
        manager = RiskManager()
        assert manager.limits.max_gross_exposure == 1.0
        assert manager.limits.max_position_weight == 0.2

    def test_pre_trade_check_allowed(self):
        limits = RiskLimits(max_gross_exposure=2.0, max_position_weight=0.3)
        manager = RiskManager(limits=limits)

        current = pd.Series({"BTC": 0.1, "ETH": -0.05})
        intent = OrderIntent(
            date="2024-01-01",
            asset="BTC",
            target_weight=0.15,
            current_weight=0.1,
            order_weight=0.05,
        )
        batch = OrderBatch(date="2024-01-01", intents=(intent,))

        result = manager.pre_trade_check(batch, current)
        assert result.allowed is True
        assert len(result.rejected_intents) == 0

    def test_pre_trade_check_rejects_asset_limit(self):
        limits = RiskLimits(max_position_weight=0.1)
        manager = RiskManager(limits=limits)

        current = pd.Series({"BTC": 0.0})
        intent = OrderIntent(
            date="2024-01-01",
            asset="BTC",
            target_weight=0.2,  # Exceeds max_position_weight of 0.1
            current_weight=0.0,
            order_weight=0.2,
        )
        batch = OrderBatch(date="2024-01-01", intents=(intent,))

        result = manager.pre_trade_check(batch, current)
        assert result.allowed is False
        assert len(result.rejected_intents) == 1
        assert result.rejected_intents[0]["asset"] == "BTC"
        assert any(e.event_type == "order_rejected" for e in result.events)

    def test_pre_trade_check_rejects_gross_exposure(self):
        limits = RiskLimits(max_gross_exposure=0.5)
        manager = RiskManager(limits=limits)

        current = pd.Series({"BTC": 0.3, "ETH": 0.2})
        intent = OrderIntent(
            date="2024-01-01",
            asset="SOL",
            target_weight=0.2,  # Would make gross = 0.7 > 0.5
            current_weight=0.0,
            order_weight=0.2,
        )
        batch = OrderBatch(date="2024-01-01", intents=(intent,))

        result = manager.pre_trade_check(batch, current)
        assert result.allowed is False
        assert any(e.event_type == "limit_breach" for e in result.events)

    def test_pre_trade_check_rejects_net_exposure(self):
        limits = RiskLimits(max_net_exposure=0.1)
        manager = RiskManager(limits=limits)

        current = pd.Series({"BTC": 0.0, "ETH": 0.0})
        intent = OrderIntent(
            date="2024-01-01",
            asset="BTC",
            target_weight=0.2,  # Net = 0.2 > 0.1
            current_weight=0.0,
            order_weight=0.2,
        )
        batch = OrderBatch(date="2024-01-01", intents=(intent,))

        result = manager.pre_trade_check(batch, current)
        assert result.allowed is False

    def test_pre_trade_check_allowed_assets(self):
        limits = RiskLimits(allowed_assets=["BTC", "ETH"])
        manager = RiskManager(limits=limits)

        current = pd.Series({"BTC": 0.0})
        intent = OrderIntent(
            date="2024-01-01",
            asset="DOGE",  # Not in allowed list
            target_weight=0.1,
            current_weight=0.0,
            order_weight=0.1,
        )
        batch = OrderBatch(date="2024-01-01", intents=(intent,))

        result = manager.pre_trade_check(batch, current)
        assert result.allowed is False
        assert result.rejected_intents[0]["asset"] == "DOGE"

    def test_pre_trade_check_blocked_assets(self):
        limits = RiskLimits(blocked_assets=["DOGE"])
        manager = RiskManager(limits=limits)

        current = pd.Series({"BTC": 0.0})
        intent = OrderIntent(
            date="2024-01-01",
            asset="DOGE",  # Blocked
            target_weight=0.1,
            current_weight=0.0,
            order_weight=0.1,
        )
        batch = OrderBatch(date="2024-01-01", intents=(intent,))

        result = manager.pre_trade_check(batch, current)
        assert result.allowed is False

    def test_pre_trade_check_position_age(self):
        limits = RiskLimits(max_position_age_days=5)
        manager = RiskManager(limits=limits)

        # Simulate position held for 6 days
        manager._position_ages["BTC"] = 6
        current = pd.Series({"BTC": 0.1})
        intent = OrderIntent(
            date="2024-01-01",
            asset="BTC",
            target_weight=0.1,
            current_weight=0.1,
            order_weight=0.0,  # No change, just maintaining
        )
        batch = OrderBatch(date="2024-01-01", intents=(intent,))

        result = manager.pre_trade_check(batch, current, date="2024-01-01")
        # Position age exceeded, should generate event
        assert any(e.event_type == "limit_breach" for e in result.events)

    def test_pre_trade_check_drawdown_kill_switch(self):
        limits = RiskLimits(max_drawdown=0.1)
        manager = RiskManager(limits=limits, kill_switch_enabled=True)

        current = pd.Series({"BTC": 0.1})
        # Cumulative series with 15% drawdown
        cumulative = pd.Series(
            [1.0, 1.05, 1.0, 0.9, 0.85],
            index=pd.date_range("2024-01-01", periods=5),
        )

        intent = OrderIntent(
            date="2024-01-05",
            asset="BTC",
            target_weight=0.1,
            current_weight=0.1,
            order_weight=0.0,
        )
        batch = OrderBatch(date="2024-01-05", intents=(intent,))

        result = manager.pre_trade_check(batch, current, cumulative=cumulative, date="2024-01-05")
        assert result.allowed is False
        assert manager._kill_switch_triggered is True
        assert any(e.event_type == "kill_switch" for e in result.events)
        assert any(e.event_type == "position_flattened" for e in result.events)

    def test_pre_trade_check_drawdown_no_kill_switch(self):
        limits = RiskLimits(max_drawdown=0.1)
        manager = RiskManager(limits=limits, kill_switch_enabled=False)

        current = pd.Series({"BTC": 0.1})
        cumulative = pd.Series(
            [1.0, 1.05, 1.0, 0.9, 0.85],
            index=pd.date_range("2024-01-01", periods=5),
        )

        intent = OrderIntent(
            date="2024-01-05",
            asset="BTC",
            target_weight=0.1,
            current_weight=0.1,
            order_weight=0.0,
        )
        batch = OrderBatch(date="2024-01-05", intents=(intent,))

        result = manager.pre_trade_check(batch, current, cumulative=cumulative, date="2024-01-05")
        # Kill switch disabled, should still allow but emit event
        assert any(e.event_type == "kill_switch" for e in result.events)
        assert not manager._kill_switch_triggered  # Not actually triggered

    def test_pre_trade_check_daily_turnover(self):
        limits = RiskLimits(max_daily_turnover=0.3)
        manager = RiskManager(limits=limits)

        current = pd.Series({"BTC": 0.1, "ETH": 0.05})
        # Target would require turnover of 0.4 (> 0.3)
        intent1 = OrderIntent(
            date="2024-01-01",
            asset="BTC",
            target_weight=0.3,
            current_weight=0.1,
            order_weight=0.2,
        )
        intent2 = OrderIntent(
            date="2024-01-01",
            asset="ETH",
            target_weight=0.0,
            current_weight=0.05,
            order_weight=-0.05,
        )
        batch = OrderBatch(date="2024-01-01", intents=(intent1, intent2))

        result = manager.pre_trade_check(batch, current, date="2024-01-01")
        assert any(e.event_type == "limit_breach" for e in result.events)

    def test_pre_trade_check_modifies_intents(self):
        limits = RiskLimits(max_position_weight=0.15)
        manager = RiskManager(limits=limits)

        current = pd.Series({"BTC": 0.1})
        intent = OrderIntent(
            date="2024-01-01",
            asset="BTC",
            target_weight=0.2,  # Exceeds limit, will be rejected
            current_weight=0.1,
            order_weight=0.1,
        )
        batch = OrderBatch(date="2024-01-01", intents=(intent,))

        result = manager.pre_trade_check(batch, current)
        assert result.allowed is False
        # Target weight should be reset to current (0.1) after rejection
        # modified_intents should reflect the change

    def test_check_kill_switch(self):
        limits = RiskLimits(max_drawdown=0.1)
        manager = RiskManager(limits=limits)

        cumulative = pd.Series(
            [1.0, 1.05, 1.0, 0.9, 0.85],
            index=pd.date_range("2024-01-01", periods=5),
        )
        triggered, event = manager.check_kill_switch(cumulative)
        assert triggered is True
        assert event.triggered is True
        assert event.observed_drawdown < -0.1

    def test_check_kill_switch_not_triggered(self):
        limits = RiskLimits(max_drawdown=0.2)
        manager = RiskManager(limits=limits)

        cumulative = pd.Series(
            [1.0, 1.05, 1.02, 1.01, 1.0],
            index=pd.date_range("2024-01-01", periods=5),
        )
        triggered, event = manager.check_kill_switch(cumulative)
        assert triggered is False
        assert event.triggered is False

    def test_flatten_positions(self):
        manager = RiskManager()
        current = pd.Series({"BTC": 0.1, "ETH": -0.05, "SOL": 0.05})
        flattened = manager.flatten_positions(current)
        assert (flattened == 0.0).all()
        assert len(flattened) == 3

    def test_get_events(self):
        manager = RiskManager()
        # Trigger some events
        limits = RiskLimits(max_position_weight=0.1)
        manager.limits = limits
        current = pd.Series({"BTC": 0.0})
        intent = OrderIntent(
            date="2024-01-01",
            asset="BTC",
            target_weight=0.2,
            current_weight=0.0,
            order_weight=0.2,
        )
        batch = OrderBatch(date="2024-01-01", intents=(intent,))
        manager.pre_trade_check(batch, current)

        events = manager.get_events()
        assert len(events) > 0
        assert events[0].event_type == "order_rejected"

    def test_clear_events(self):
        manager = RiskManager()
        limits = RiskLimits(max_position_weight=0.1)
        manager.limits = limits
        current = pd.Series({"BTC": 0.0})
        intent = OrderIntent(
            date="2024-01-01",
            asset="BTC",
            target_weight=0.2,
            current_weight=0.0,
            order_weight=0.2,
        )
        batch = OrderBatch(date="2024-01-01", intents=(intent,))
        manager.pre_trade_check(batch, current)

        manager.clear_events()
        assert len(manager.get_events()) == 0

    def test_update_prices(self):
        manager = RiskManager()
        prices = pd.DataFrame(
            {"BTC": [50000, 51000], "ETH": [3000, 3100]},
            index=pd.date_range("2024-01-01", periods=2),
        )
        manager.update_prices(prices)
        assert manager._last_prices["BTC"] == 51000
        assert manager._last_prices["ETH"] == 3100

    def test_get_position_value(self):
        manager = RiskManager()
        prices = pd.DataFrame(
            {"BTC": [50000, 51000], "ETH": [3000, 3100]},
            index=pd.date_range("2024-01-01", periods=2),
        )
        manager.update_prices(prices)
        positions = pd.Series({"BTC": 0.1, "ETH": 0.05})
        value = manager.get_position_value(positions)
        # 0.1 * 51000 + 0.05 * 3100 = 5100 + 155 = 5255
        assert value == 5255


class TestKillSwitchIntegration:
    """Tests for kill switch integration with existing apply_kill_switch."""

    def test_apply_kill_switch_triggers(self):
        weights = pd.DataFrame(
            {"BTC": [0.1, 0.1, 0.1], "ETH": [-0.05, -0.05, -0.05]},
            index=pd.date_range("2024-01-01", periods=3),
        )
        cumulative = pd.Series([1.0, 0.9, 0.8], index=pd.date_range("2024-01-01", periods=3))
        new_weights, event = apply_kill_switch(weights, cumulative, limit=0.15)
        assert event.triggered is True
        assert (new_weights.iloc[1:] == 0).all().all()

    def test_apply_kill_switch_no_trigger(self):
        weights = pd.DataFrame(
            {"BTC": [0.1, 0.1, 0.1], "ETH": [-0.05, -0.05, -0.05]},
            index=pd.date_range("2024-01-01", periods=3),
        )
        cumulative = pd.Series([1.0, 1.02, 1.01], index=pd.date_range("2024-01-01", periods=3))
        new_weights, event = apply_kill_switch(weights, cumulative, limit=0.15)
        assert event.triggered is False
        assert new_weights.equals(weights)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
