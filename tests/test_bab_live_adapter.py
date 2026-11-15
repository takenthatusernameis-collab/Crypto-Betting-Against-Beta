"""Tests for LiveExecutionAdapter (P9)."""

from __future__ import annotations

import json
import os

import pandas as pd
import pytest

from strategies.betting_against_beta.cli import main
from strategies.betting_against_beta.execution import (
    CCXTConnector,
    LiveExecutionAdapter,
    LiveFill,
    LiveOrder,
    OrderBatch,
    OrderIntent,
)
from strategies.betting_against_beta.risk import RiskLimits, RiskManager


class TestLiveOrder:
    """Tests for LiveOrder dataclass."""

    def test_live_order_creation(self):
        order = LiveOrder(
            idempotency_key="test-key-123",
            date="2024-01-01",
            asset="BTC",
            side="buy",
            weight=0.1,
            price=50000.0,
            notional_usd=5000.0,
        )
        assert order.idempotency_key == "test-key-123"
        assert order.asset == "BTC"
        assert order.side == "buy"
        assert order.weight == 0.1

    def test_live_order_to_dict(self):
        order = LiveOrder(
            idempotency_key="test-key",
            date="2024-01-01",
            asset="ETH",
            side="sell",
            weight=0.05,
        )
        d = order.to_dict()
        assert d["idempotency_key"] == "test-key"
        assert d["asset"] == "ETH"
        assert d["side"] == "sell"
        assert d["weight"] == 0.05


class TestLiveFill:
    """Tests for LiveFill dataclass."""

    def test_live_fill_creation(self):
        fill = LiveFill(
            idempotency_key="test-key-123",
            date="2024-01-01",
            asset="BTC",
            side="buy",
            weight=0.1,
            price=50000.0,
            notional_usd=5000.0,
            status="filled",
        )
        assert fill.idempotency_key == "test-key-123"
        assert fill.status == "filled"

    def test_live_fill_to_dict(self):
        fill = LiveFill(
            idempotency_key="test-key",
            date="2024-01-01",
            asset="ETH",
            side="sell",
            weight=0.05,
            status="partial",
            reason="participation_cap",
        )
        d = fill.to_dict()
        assert d["status"] == "partial"
        assert d["reason"] == "participation_cap"


class TestCCXTConnector:
    """Tests for CCXTConnector (dry-run mode)."""

    def test_connector_creation_dry_run(self):
        connector = CCXTConnector(
            exchange_name="binance",
            dry_run=True,
        )
        assert connector.exchange_name == "binance"
        assert connector.dry_run is True
        assert connector.is_connected() is False

    def test_connect_disconnect_dry_run(self):
        connector = CCXTConnector(exchange_name="binance", dry_run=True)
        connector.connect()
        assert connector.is_connected() is True
        connector.disconnect()
        assert connector.is_connected() is False

    def test_submit_order_dry_run(self):
        connector = CCXTConnector(exchange_name="binance", dry_run=True)
        connector.connect()

        order = LiveOrder(
            idempotency_key="idem-1",
            date="2024-01-01",
            asset="BTC",
            side="buy",
            weight=0.1,
            price=50000.0,
            notional_usd=5000.0,
        )
        fill = connector.submit_order(order)

        assert fill.idempotency_key == "idem-1"
        assert fill.asset == "BTC"
        assert fill.side == "buy"
        assert fill.weight == 0.1
        assert fill.status == "filled"
        assert fill.metadata.get("dry_run") is True

    def test_idempotency_key_reuse(self):
        connector = CCXTConnector(exchange_name="binance", dry_run=True)
        connector.connect()

        order = LiveOrder(
            idempotency_key="idem-same",
            date="2024-01-01",
            asset="BTC",
            side="buy",
            weight=0.1,
        )
        fill1 = connector.submit_order(order)
        fill2 = connector.submit_order(order)  # Same idempotency key

        assert fill1.idempotency_key == fill2.idempotency_key
        assert fill2.status == "rejected"
        assert fill2.reason == "duplicate_idempotency_key"

    def test_cancel_order_dry_run(self):
        connector = CCXTConnector(exchange_name="binance", dry_run=True)
        connector.connect()

        order = LiveOrder(
            idempotency_key="idem-cancel",
            date="2024-01-01",
            asset="BTC",
            side="buy",
            weight=0.1,
        )
        connector.submit_order(order)
        result = connector.cancel_order("idem-cancel")
        assert result is True

        fill = connector.get_order_status("idem-cancel")
        assert fill.status == "cancelled"

    def test_get_order_status(self):
        connector = CCXTConnector(exchange_name="binance", dry_run=True)
        connector.connect()

        order = LiveOrder(
            idempotency_key="idem-status",
            date="2024-01-01",
            asset="BTC",
            side="buy",
            weight=0.1,
        )
        connector.submit_order(order)
        fill = connector.get_order_status("idem-status")
        assert fill is not None
        assert fill.idempotency_key == "idem-status"

        # Non-existent key
        assert connector.get_order_status("non-existent") is None

    def test_fetch_balance_dry_run(self):
        connector = CCXTConnector(exchange_name="binance", dry_run=True)
        connector.connect()
        balance = connector.fetch_balance()
        assert "USDT" in balance
        assert balance["USDT"]["free"] == 100000.0

    def test_fetch_ticker_dry_run(self):
        connector = CCXTConnector(exchange_name="binance", dry_run=True)
        connector.connect()
        ticker = connector.fetch_ticker("BTC/USDT")
        assert ticker["last"] == 1.0
        assert "timestamp" in ticker

    def test_invalid_exchange(self):
        connector = CCXTConnector(exchange_name="invalid_exchange_xyz", dry_run=True)
        with pytest.raises(ValueError, match="not supported by CCXT"):
            connector.connect()


class TestLiveExecutionAdapter:
    """Tests for LiveExecutionAdapter (dry-run mode)."""

    def test_adapter_creation(self):
        adapter = LiveExecutionAdapter(
            exchange="binance",
            api_key_env="TEST_API_KEY",
            api_secret_env="TEST_API_SECRET",
            dry_run=True,
        )
        assert adapter.exchange_name == "binance"
        assert adapter.dry_run is True

    def test_adapter_requires_env_vars(self):
        # Should not raise during creation, but will fail at connect if env vars not set
        adapter = LiveExecutionAdapter(
            exchange="binance",
            api_key_env="NONEXISTENT_KEY",
            api_secret_env="NONEXISTENT_SECRET",
            dry_run=True,
        )
        # In dry_run, it doesn't actually need the credentials
        adapter._ensure_connected()
        assert adapter._connected is True

    def test_submit_intents_dry_run(self):
        adapter = LiveExecutionAdapter(
            exchange="binance",
            api_key_env="TEST_KEY",
            api_secret_env="TEST_SECRET",
            dry_run=True,
        )

        intent = OrderIntent(
            date="2024-01-01",
            asset="BTC",
            target_weight=0.1,
            current_weight=0.0,
            order_weight=0.1,
            price=50000.0,
            notional_usd=5000.0,
        )
        batch = OrderBatch(date="2024-01-01", intents=(intent,))

        fills = adapter.submit_intents(batch)
        assert len(fills) == 1
        fill = fills[0]
        assert fill["asset"] == "BTC"
        assert fill["filled_weight"] == 0.1
        assert fill["status"] == "filled"
        assert fill["exchange"] == "binance"
        assert "idempotency_key" in fill

    def test_submit_multiple_intents(self):
        adapter = LiveExecutionAdapter(
            exchange="binance",
            api_key_env="TEST_KEY",
            api_secret_env="TEST_SECRET",
            dry_run=True,
        )

        intents = [
            OrderIntent(
                date="2024-01-01",
                asset="BTC",
                target_weight=0.1,
                current_weight=0.0,
                order_weight=0.1,
            ),
            OrderIntent(
                date="2024-01-01",
                asset="ETH",
                target_weight=-0.05,
                current_weight=0.0,
                order_weight=-0.05,
            ),
        ]
        batch = OrderBatch(date="2024-01-01", intents=tuple(intents))

        fills = adapter.submit_intents(batch)
        assert len(fills) == 2
        assert fills[0]["asset"] == "BTC"
        assert fills[1]["asset"] == "ETH"
        assert fills[0]["side"] == "buy"
        assert fills[1]["side"] == "sell"

    def test_flush_returns_empty(self):
        adapter = LiveExecutionAdapter(
            exchange="binance",
            api_key_env="TEST_KEY",
            api_secret_env="TEST_SECRET",
            dry_run=True,
        )
        assert adapter.flush() == []

    def test_health_check(self):
        adapter = LiveExecutionAdapter(
            exchange="binance",
            api_key_env="TEST_KEY",
            api_secret_env="TEST_SECRET",
            dry_run=True,
        )
        health = adapter.health_check()
        assert health["mode"] == "live"
        assert health["exchange"] == "binance"
        assert health["connected"] is False
        assert health["dry_run"] is True

    def test_health_check_after_connect(self):
        adapter = LiveExecutionAdapter(
            exchange="binance",
            api_key_env="TEST_KEY",
            api_secret_env="TEST_SECRET",
            dry_run=True,
        )
        adapter._ensure_connected()
        health = adapter.health_check()
        assert health["connected"] is True

    def test_disconnect(self):
        adapter = LiveExecutionAdapter(
            exchange="binance",
            api_key_env="TEST_KEY",
            api_secret_env="TEST_SECRET",
            dry_run=True,
        )
        adapter._ensure_connected()
        adapter.disconnect()
        assert adapter._connected is False


class TestLiveExecutionAdapterCLI:
    """Tests for CLI integration with live adapter."""

    def test_cli_live_adapter_requires_exchange(self):
        import argparse

        from strategies.betting_against_beta.cli import _build_adapter

        args = argparse.Namespace(
            adapter="live",
            exchange=None,
            api_key_env="KEY",
            api_secret_env="SECRET",
            api_password_env=None,
            testnet=False,
            fills=None,
        )
        with pytest.raises(Exception, match="--exchange is required"):
            _build_adapter(args)

    def test_cli_live_adapter_requires_credentials(self):
        import argparse

        from strategies.betting_against_beta.cli import _build_adapter

        args = argparse.Namespace(
            adapter="live",
            exchange="binance",
            api_key_env=None,
            api_secret_env="SECRET",
            api_password_env=None,
            testnet=False,
            fills=None,
        )
        with pytest.raises(Exception, match="--api-key-env and --api-secret-env are required"):
            _build_adapter(args)

    def test_cli_live_adapter_creates_adapter(self):
        import argparse

        from strategies.betting_against_beta.cli import _build_adapter

        # Set dummy env vars
        os.environ["TEST_BAB_API_KEY"] = "dummy"
        os.environ["TEST_BAB_API_SECRET"] = "dummy"

        try:
            args = argparse.Namespace(
                adapter="live",
                exchange="binance",
                api_key_env="TEST_BAB_API_KEY",
                api_secret_env="TEST_BAB_API_SECRET",
                api_password_env=None,
                testnet=False,
                fills=None,
            )
            adapter, _ = _build_adapter(args)
            assert adapter is not None
            assert isinstance(adapter, LiveExecutionAdapter)
        finally:
            os.environ.pop("TEST_BAB_API_KEY", None)
            os.environ.pop("TEST_BAB_API_SECRET", None)


class TestLiveExecutionAdapterRiskGating:
    """Tests for optional RiskManager pre-trade gating on LiveExecutionAdapter.

    Risk gating is opt-in: when no ``risk_manager`` is wired, behavior is
    byte-identical to the default path.  When wired, breached intents/batches
    are rejected explicitly (``status="rejected"``) with no silent fallback.
    """

    def _make_adapter(self, **kwargs):
        kw = dict(
            exchange="binance",
            api_key_env="KEY",
            api_secret_env="SECRET",
            dry_run=True,
        )
        kw.update(kwargs)
        return LiveExecutionAdapter(**kw)

    def _intent(
        self,
        asset="BTC",
        order_weight=0.1,
        target_weight=0.1,
        current_weight=0.0,
        price=50000.0,
    ):
        return OrderIntent(
            date="2024-01-01",
            asset=asset,
            target_weight=target_weight,
            current_weight=current_weight,
            order_weight=order_weight,
            price=price,
            notional_usd=abs(order_weight) * price,
        )

    def test_no_risk_manager_preserves_default_behavior(self):
        adapter = self._make_adapter()
        batch = OrderBatch(date="2024-01-01", intents=(self._intent(),))
        fills = adapter.submit_intents(batch)
        assert len(fills) == 1
        assert fills[0]["status"] == "filled"
        assert fills[0]["filled_weight"] == 0.1

    def test_rejects_asset_position_limit(self):
        limits = RiskLimits(max_position_weight=0.05)
        manager = RiskManager(limits=limits)
        adapter = self._make_adapter(risk_manager=manager)
        intent = self._intent(order_weight=0.2, target_weight=0.2)  # exceeds 0.05
        batch = OrderBatch(date="2024-01-01", intents=(intent,))
        fills = adapter.submit_intents(batch)
        assert len(fills) == 1
        assert fills[0]["status"] == "rejected"
        assert fills[0]["filled_weight"] == 0.0
        assert fills[0]["reason"]

    def test_rejects_portfolio_gross_exposure_whole_batch(self):
        positions = pd.Series({"BTC": 0.0, "ETH": 0.0})
        limits = RiskLimits(max_gross_exposure=0.1)
        manager = RiskManager(limits=limits)
        adapter = self._make_adapter(risk_manager=manager, current_positions=positions)
        btc = self._intent(asset="BTC", order_weight=0.1, target_weight=0.1)
        eth = self._intent(asset="ETH", order_weight=0.1, target_weight=0.1)
        batch = OrderBatch(date="2024-01-01", intents=(btc, eth))
        fills = adapter.submit_intents(batch)
        assert len(fills) == 2
        assert all(f["status"] == "rejected" for f in fills)
        assert all(f["filled_weight"] == 0.0 for f in fills)

    def test_kill_switch_rejects_all(self):
        limits = RiskLimits(max_drawdown=0.1)
        manager = RiskManager(limits=limits, kill_switch_enabled=True)
        cumulative = pd.Series(
            [1.0, 0.9, 0.8], index=pd.date_range("2024-01-01", periods=3)
        )
        adapter = self._make_adapter(
            risk_manager=manager,
            current_positions=pd.Series({"BTC": 0.0}),
            cumulative=cumulative,
        )
        intent = self._intent()
        batch = OrderBatch(date="2024-01-05", intents=(intent,))
        fills = adapter.submit_intents(batch)
        assert len(fills) == 1
        assert fills[0]["status"] == "rejected"
        assert manager._kill_switch_triggered is True


class TestLiveExecutionAdapterHealthJSON:
    """Tests that live-adapter health output is strict-JSON-safe."""

    def test_health_check_dict_is_strict_json(self):
        adapter = self._make_adapter_health()
        health = adapter.health_check()
        # Strict serialization: no NaN/Infinity tokens permitted.
        payload = json.dumps(health, allow_nan=False)
        obj = json.loads(payload)
        assert obj["mode"] == "live"
        assert obj["exchange"] == "binance"
        assert obj["dry_run"] is True

    def _make_adapter_health(self):
        return LiveExecutionAdapter(
            exchange="binance",
            api_key_env="KEY",
            api_secret_env="SECRET",
            dry_run=True,
        )


def test_cli_health_check_emits_strict_json(capsys, monkeypatch):
    """``--health-check`` prints one strict JSON object (machine-parseable)."""
    monkeypatch.setenv("BAB_TEST_KEY", "dummy")
    monkeypatch.setenv("BAB_TEST_SECRET", "dummy")
    rc = main(
        [
            "--adapter",
            "live",
            "--exchange",
            "binance",
            "--api-key-env",
            "BAB_TEST_KEY",
            "--api-secret-env",
            "BAB_TEST_SECRET",
            "--health-check",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert payload["mode"] == "live"
    assert payload["exchange"] == "binance"
    assert payload["dry_run"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
