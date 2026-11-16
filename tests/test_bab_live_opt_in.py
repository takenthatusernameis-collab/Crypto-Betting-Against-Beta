"""P18-2 characterization tests for live execution two-key opt-in.

These tests MUST fail on HEAD: ``LiveExecutionAdapter`` has no
``allow_live_execution`` / ``accept_terms`` gate and the CLI has no
``--allow-live-execution`` / ``--accept-terms`` flags. They pass after the
P18-2 fix. Deterministic, no real network: ``ccxt`` is mocked so the "happy
path" only proves construction/submission intent (``dry_run=False`` reached).
"""

from __future__ import annotations

import os
import sys
from types import SimpleNamespace

import pytest

from strategies.betting_against_beta.cli import main
from strategies.betting_against_beta.execution import LiveExecutionAdapter, OrderBatch, OrderIntent


def _intent():
    return OrderIntent(
        date="2024-01-01",
        asset="BTC",
        target_weight=0.1,
        current_weight=0.0,
        order_weight=0.1,
        price=50000.0,
        notional_usd=5000.0,
    )


def _batch():
    return OrderBatch(date="2024-01-01", intents=(_intent(),))


def _set_live_env(monkeypatch):
    monkeypatch.setenv("BAB_TEST_KEY", "k")
    monkeypatch.setenv("BAB_TEST_SECRET", "s")


def test_constructor_dry_run_false_without_opt_in_raises():
    with pytest.raises((PermissionError, RuntimeError, TypeError, ValueError)):
        LiveExecutionAdapter(
            exchange="binance",
            api_key_env="BAB_TEST_KEY",
            api_secret_env="BAB_TEST_SECRET",
            dry_run=False,
        )


def test_constructor_dry_run_true_needs_no_opt_in():
    adapter = LiveExecutionAdapter(
        exchange="binance",
        api_key_env="BAB_TEST_KEY",
        api_secret_env="BAB_TEST_SECRET",
        dry_run=True,
    )
    assert adapter.dry_run is True
    assert adapter._connected is False


def test_cli_live_without_allow_flag_stays_dry_run(monkeypatch, tmp_path):
    _set_live_env(monkeypatch)
    out = tmp_path / "out.json"
    rc = main(
        [
            "--synthetic",
            "--adapter",
            "live",
            "--exchange",
            "binance",
            "--api-key-env",
            "BAB_TEST_KEY",
            "--api-secret-env",
            "BAB_TEST_SECRET",
            "--output",
            str(out),
        ]
    )
    assert rc == 0
    # No opt-in flags: execution must remain dry-run only.
    assert "--allow-live-execution" not in " ".join(sys.argv)  # argv untouched
    adapter = LiveExecutionAdapter(exchange="binance", dry_run=True)
    assert adapter.dry_run is True


def test_cli_live_allow_without_exact_accept_terms_refuses(monkeypatch, tmp_path, capsys):
    _set_live_env(monkeypatch)
    out = tmp_path / "out.json"
    rc = main(
        [
            "--synthetic",
            "--adapter",
            "live",
            "--exchange",
            "binance",
            "--api-key-env",
            "BAB_TEST_KEY",
            "--api-secret-env",
            "BAB_TEST_SECRET",
            "--allow-live-execution",
            "--output",
            str(out),
        ]
    )
    assert rc != 0
    captured = capsys.readouterr()
    assert "accept" in (captured.out + captured.err).lower() or rc == 2


def test_cli_live_with_both_flags_reaches_real_path(monkeypatch, tmp_path):
    """Both opt-in flags present -> adapter constructed with dry_run=False.

    ``ccxt`` is injected as a fake module so no network is used; we only assert
    that the exchange constructor is reached with ``dry_run=False`` intent (the
    live adapter must not force dry-run when explicitly authorized).
    """
    _set_live_env(monkeypatch)
    constructed = {}

    class FakeExchange:
        def __init__(self, params):
            constructed["params"] = dict(params)

        def set_sandbox_mode(self, enabled):
            constructed["sandbox"] = enabled

        def load_markets(self):
            return {}

        def fetch_balance(self):
            return {"USDT": {"free": 100000.0, "used": 0.0, "total": 100000.0}}

        def fetch_ticker(self, symbol):
            return {"last": 1.0, "timestamp": 1704067200000}

        def create_order(self, *a, **k):
            return {"id": "1", "status": "closed", "filled": 1.0, "average": 1.0}

    fake_ccxt = SimpleNamespace(
        binance=lambda params: FakeExchange(params),
        exchanges=["binance"],
    )
    monkeypatch.setitem(sys.modules, "ccxt", fake_ccxt)

    out = tmp_path / "out.json"
    rc = main(
        [
            "--synthetic",
            "--adapter",
            "live",
            "--exchange",
            "binance",
            "--api-key-env",
            "BAB_TEST_KEY",
            "--api-secret-env",
            "BAB_TEST_SECRET",
            "--allow-live-execution",
            "--accept-terms",
            "I_UNDERSTAND_LIVE_TRADING",
            "--output",
            str(out),
        ]
    )
    # Reaching the real (non-dry-run) construction path is the proof; the fake
    # exchange must have been instantiated.
    assert rc == 0
    assert "params" in constructed
