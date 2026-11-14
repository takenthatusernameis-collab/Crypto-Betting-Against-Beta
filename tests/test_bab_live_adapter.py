"""Tests for LiveExecutionAdapter (P9)."""

from __future__ import annotations

import os

import pytest

from strategies.betting_against_beta.execution import (
    CCXTConnector,
    LiveExecutionAdapter,
    LiveFill,
    LiveOrder,
    OrderBatch,
    OrderIntent,
)


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
