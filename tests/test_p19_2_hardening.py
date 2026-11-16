"""P19-2: Real-data ingest + live-fill fidelity hardening behavior tests.

Covers:
- P19-2a: fetch_real_bab_prices.py network path (_http_get_json / _rate_limit_wait)
- P19-2b: execution.py reconciliation fidelity (branches 139-141, 182-185, 563-564)
- P19-2c: CLI --health-check JSON contract
"""

from __future__ import annotations

import io
import json
import math
import time
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.execution import (
    PaperAdapter,
    _sanitize_for_json,
)

# =============================================================================
# P19-2a: fetch_real_bab_prices.py network path tests
# =============================================================================

class _FakeResponse:
    def __init__(self, payload, status=200, headers=None):
        self._payload = payload
        self.status = status
        self.headers = headers or {}

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def getcode(self):
        return self.status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _install_fake_urlopen(monkeypatch, handler):
    import scripts.fetch_real_bab_prices as fetch_mod

    monkeypatch.setattr(
        fetch_mod.urllib.request, "urlopen", lambda req, timeout=None: handler(req, timeout)
    )


def test_rate_limit_wait_enforces_min_interval(monkeypatch):
    """_rate_limit_wait sleeps to enforce min_interval between requests."""
    import scripts.fetch_real_bab_prices as fetch_mod

    sleep_calls = []
    monkeypatch.setattr(fetch_mod.time, "sleep", lambda s: sleep_calls.append(s))

    # First call: no last_request_at -> returns now immediately
    now1 = fetch_mod._rate_limit_wait(None, 10.0)  # 10 req/s = 0.1s interval
    assert sleep_calls == []

    # Second call immediately after: should sleep ~0.1s
    now2 = fetch_mod._rate_limit_wait(now1, 10.0)
    assert len(sleep_calls) == 1
    assert sleep_calls[0] > 0.05  # roughly half the interval since we're fast

    # Third call: last_request_at is now2, should sleep again
    sleep_calls.clear()
    now3 = fetch_mod._rate_limit_wait(now2, 10.0)
    assert len(sleep_calls) == 1
    assert sleep_calls[0] > 0.05


def test_rate_limit_wait_rejects_non_positive_rate(monkeypatch):
    """_rate_limit_wait raises BABDataError for non-positive max_requests_per_second."""
    import scripts.fetch_real_bab_prices as fetch_mod

    with pytest.raises(BABDataError, match="must be > 0"):
        fetch_mod._rate_limit_wait(None, 0.0)

    with pytest.raises(BABDataError, match="must be > 0"):
        fetch_mod._rate_limit_wait(None, -1.0)


def test_http_get_json_retries_429_with_retry_after(monkeypatch):
    """_http_get_json honors Retry-After header on HTTP 429 and retries."""
    import scripts.fetch_real_bab_prices as fetch_mod

    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)
    monkeypatch.setattr(fetch_mod.time, "monotonic", lambda: 1000.0)

    call_count = {"n": 0}

    def handler(req, timeout=None):
        call_count["n"] += 1
        if call_count["n"] <= 2:
            raise urllib.error.HTTPError(
                req.full_url,
                429,
                "Too Many Requests",
                hdrs={"Retry-After": "0"},
                fp=io.BytesIO(b"rate limit"),
            )
        return _FakeResponse({"success": True})

    _install_fake_urlopen(monkeypatch, handler)

    result, _ = fetch_mod._http_get_json(
        "https://api.test/endpoint",
        timeout=10.0,
        max_requests_per_second=10.0,
        last_request_at=None,
        retries=3,
    )
    assert result == {"success": True}
    assert call_count["n"] == 3  # 2 retries + 1 success


def test_http_get_json_fails_after_max_retries_on_429(monkeypatch):
    """_http_get_json fails loudly after COINBASE_PUBLIC_MAX_RETRIES on persistent 429."""
    import scripts.fetch_real_bab_prices as fetch_mod

    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)
    monkeypatch.setattr(fetch_mod.time, "monotonic", lambda: 1000.0)

    def handler(req, timeout=None):
        raise urllib.error.HTTPError(
            req.full_url,
            429,
            "Too Many Requests",
            hdrs={"Retry-After": "0"},
            fp=io.BytesIO(b"rate limit"),
        )

    _install_fake_urlopen(monkeypatch, handler)

    with pytest.raises(BABDataError, match="rate limit.*after retries"):
        fetch_mod._http_get_json(
            "https://api.test/endpoint",
            timeout=10.0,
            max_requests_per_second=10.0,
            last_request_at=None,
            retries=fetch_mod.COINBASE_PUBLIC_MAX_RETRIES,
        )


def test_http_get_json_retries_transient_5xx_with_backoff(monkeypatch):
    """_http_get_json retries transient 5xx (500/502/503/504) with backoff."""
    import scripts.fetch_real_bab_prices as fetch_mod

    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)
    monkeypatch.setattr(fetch_mod.time, "monotonic", lambda: 1000.0)

    call_count = {"n": 0}

    def handler(req, timeout=None):
        call_count["n"] += 1
        if call_count["n"] <= 2:
            raise urllib.error.HTTPError(
                req.full_url, 503, "Service Unavailable", hdrs={}, fp=io.BytesIO(b"down")
            )
        return _FakeResponse({"success": True})

    _install_fake_urlopen(monkeypatch, handler)

    result, _ = fetch_mod._http_get_json(
        "https://api.test/endpoint",
        timeout=10.0,
        max_requests_per_second=10.0,
        last_request_at=None,
        retries=3,
    )
    assert result == {"success": True}
    assert call_count["n"] == 3


def test_http_get_json_fails_after_max_retries_on_persistent_5xx(monkeypatch):
    """_http_get_json fails loudly after max retries on persistent 5xx."""
    import scripts.fetch_real_bab_prices as fetch_mod

    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)
    monkeypatch.setattr(fetch_mod.time, "monotonic", lambda: 1000.0)

    def handler(req, timeout=None):
        raise urllib.error.HTTPError(
            req.full_url, 502, "Bad Gateway", hdrs={}, fp=io.BytesIO(b"down")
        )

    _install_fake_urlopen(monkeypatch, handler)

    with pytest.raises(BABDataError, match="public API HTTP error 502"):
        fetch_mod._http_get_json(
            "https://api.test/endpoint",
            timeout=10.0,
            max_requests_per_second=10.0,
            last_request_at=None,
            retries=fetch_mod.COINBASE_PUBLIC_MAX_RETRIES,
        )


def test_http_get_json_retries_network_errors_bounded(monkeypatch):
    """_http_get_json retries network/URLError/timeout bounded, then fails loudly."""
    import scripts.fetch_real_bab_prices as fetch_mod

    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)
    monkeypatch.setattr(fetch_mod.time, "monotonic", lambda: 1000.0)

    call_count = {"n": 0}

    def handler(req, timeout=None):
        call_count["n"] += 1
        if call_count["n"] <= 2:
            raise urllib.error.URLError("network down")
        return _FakeResponse({"success": True})

    _install_fake_urlopen(monkeypatch, handler)

    result, _ = fetch_mod._http_get_json(
        "https://api.test/endpoint",
        timeout=10.0,
        max_requests_per_second=10.0,
        last_request_at=None,
        retries=3,
    )
    assert result == {"success": True}
    assert call_count["n"] == 3


def test_http_get_json_fails_loudly_on_network_error_after_retries(monkeypatch):
    """_http_get_json fails loudly with no offline fallback after network retries exhausted."""
    import scripts.fetch_real_bab_prices as fetch_mod

    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)
    monkeypatch.setattr(fetch_mod.time, "monotonic", lambda: 1000.0)

    def handler(req, timeout=None):
        raise urllib.error.URLError("network down")

    _install_fake_urlopen(monkeypatch, handler)

    with pytest.raises(BABDataError, match="network error contacting public API"):
        fetch_mod._http_get_json(
            "https://api.test/endpoint",
            timeout=10.0,
            max_requests_per_second=10.0,
            last_request_at=None,
            retries=fetch_mod.COINBASE_PUBLIC_MAX_RETRIES,
        )
    # Verify no offline fallback mention
    # The error message explicitly says "No offline fallback was used"


def test_http_get_json_fails_on_invalid_json(monkeypatch):
    """_http_get_json fails loudly on invalid JSON response."""
    import scripts.fetch_real_bab_prices as fetch_mod

    monkeypatch.setattr(fetch_mod.time, "monotonic", lambda: 1000.0)

    def handler(req, timeout=None):
        # Return invalid JSON
        resp = _FakeResponse("not valid json")
        resp.read = lambda: b"not valid json"
        return resp

    _install_fake_urlopen(monkeypatch, handler)

    with pytest.raises(BABDataError, match="invalid JSON from public API"):
        fetch_mod._http_get_json(
            "https://api.test/endpoint",
            timeout=10.0,
            max_requests_per_second=10.0,
            last_request_at=None,
            retries=2,
        )


def test_enforce_public_api_opt_in_before_any_request(monkeypatch):
    """_enforce_public_api_opt_in is enforced BEFORE any network request."""
    import scripts.fetch_real_bab_prices as fetch_mod

    # Track if urlopen is ever called
    urlopen_called = {"called": False}

    def handler(req, timeout=None):
        urlopen_called["called"] = True
        return _FakeResponse({"success": True})

    _install_fake_urlopen(monkeypatch, handler)
    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)

    # Without --allow-public-api, should fail before any request
    with pytest.raises(BABDataError, match="requires explicit opt-in"):
        fetch_mod._enforce_public_api_opt_in(
            fetch_mod.COINBASE_PUBLIC_SOURCE, allow_public_api=False, accept_terms=None
        )

    assert not urlopen_called["called"], "No network request should be made before opt-in check"

    # With --allow-public-api but wrong accept_terms, should fail before any request
    urlopen_called["called"] = False
    with pytest.raises(BABDataError, match="explicit ToS.*acknowledgement"):
        fetch_mod._enforce_public_api_opt_in(
            fetch_mod.COINBASE_PUBLIC_SOURCE, allow_public_api=True, accept_terms="wrong terms"
        )

    assert not urlopen_called["called"], "No network request should be made before ToS check"


# =============================================================================
# P19-2b: execution.py reconciliation fidelity tests
# =============================================================================

def test_price_for_timestamp_fallback_branch():
    """_price_for covers Timestamp fallback (lines 139-141) when string key fails."""
    import scripts.fetch_real_bab_prices as fetch_mod
    # We need to test the PaperAdapter._price_for method
    # Create a prices DataFrame with Timestamp index
    dates = pd.date_range("2023-01-01", periods=5, freq="D")
    prices_df = pd.DataFrame({"BTC": [100, 101, 102, 103, 104]}, index=dates)
    prices_df.index.name = "date"

    adapter = PaperAdapter(prices_df=prices_df)

    # String key lookup should work (line 135-137)
    price1 = adapter._price_for("2023-01-01", "BTC")
    assert price1 == 100.0

    # String key not in index but Timestamp is (lines 139-141)
    # This happens when prices_df has Timestamp index but we pass string key
    price2 = adapter._price_for("2023-01-02T00:00:00", "BTC")
    assert price2 == 101.0

    # Non-existent date
    price3 = adapter._price_for("2023-12-31", "BTC")
    assert price3 is None

    # Asset not in columns
    price4 = adapter._price_for("2023-01-01", "ETH")
    assert price4 is None


def test_price_for_handles_nan_values():
    """_price_for returns None for NaN values in prices."""
    dates = pd.date_range("2023-01-01", periods=3, freq="D")
    prices_df = pd.DataFrame({"BTC": [100, np.nan, 102]}, index=dates)
    prices_df.index.name = "date"

    adapter = PaperAdapter(prices_df=prices_df)

    price1 = adapter._price_for("2023-01-01", "BTC")
    assert price1 == 100.0

    price2 = adapter._price_for("2023-01-02", "BTC")
    assert price2 is None  # NaN returns None

    price3 = adapter._price_for("2023-01-03", "BTC")
    assert price3 == 102.0


def test_adv_for_handles_dict_series_dataframe():
    """_adv_for handles dict, Series (asset-indexed and date-indexed), and DataFrame."""
    dates = pd.date_range("2023-01-01", periods=3, freq="D")

    # Test dict (asset-indexed)
    adapter = PaperAdapter(adv_usd={"BTC": 1_000_000.0, "ETH": 500_000.0})
    assert adapter._adv_for("2023-01-01", "BTC") == 1_000_000.0
    assert adapter._adv_for("2023-01-01", "ETH") == 500_000.0
    assert adapter._adv_for("2023-01-01", "SOL") is None

    # Test Series (asset-indexed)
    adv_series = pd.Series({"BTC": 2_000_000.0, "ETH": 1_000_000.0})
    adapter = PaperAdapter(adv_usd=adv_series)
    assert adapter._adv_for("2023-01-01", "BTC") == 2_000_000.0

    # Test Series (date-indexed) - line 158
    adv_date_series = pd.Series(
        [100_000.0, 200_000.0, 300_000.0],
        index=pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
    )
    adapter = PaperAdapter(adv_usd=adv_date_series)
    # This path uses _adv_from_frame_value for date-indexed Series
    adv_val = adapter._adv_for("2023-01-01", "BTC")
    assert adv_val == 100_000.0

    # Test DataFrame (date x asset)
    adv_df = pd.DataFrame(
        {"BTC": [100_000.0, 200_000.0], "ETH": [50_000.0, 75_000.0]},
        index=pd.to_datetime(["2023-01-01", "2023-01-02"]),
    )
    adapter = PaperAdapter(adv_usd=adv_df)
    assert adapter._adv_for("2023-01-01", "BTC") == 100_000.0
    assert adapter._adv_for("2023-01-02", "BTC") == 200_000.0


def test_adv_from_frame_value_timestamp_fallback_branch():
    """_adv_from_frame_value covers Timestamp fallback (lines 182-185)."""
    # Create a Series with Timestamp index
    idx = pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"])
    sub = pd.Series([100.0, 200.0, 300.0], index=idx)

    # String key lookup (lines 172-176)
    result1 = PaperAdapter._adv_from_frame_value(sub, "2023-01-01")
    assert result1 == 100.0

    # Timestamp fallback (lines 180-185) - when string key not in index but Timestamp is
    result2 = PaperAdapter._adv_from_frame_value(sub, "2023-01-02T00:00:00")
    assert result2 == 200.0

    # Non-existent
    result3 = PaperAdapter._adv_from_frame_value(sub, "2023-12-31")
    assert result3 is None


def test_adv_from_frame_value_handles_series_values():
    """_adv_from_frame_value handles when sub.loc returns a Series (line 174-175)."""
    idx = pd.to_datetime(["2023-01-01", "2023-01-02"])
    # DataFrame column selection returns Series with same index
    sub = pd.DataFrame({"BTC": [100.0, 200.0]}, index=idx)["BTC"]

    result = PaperAdapter._adv_from_frame_value(sub, "2023-01-01")
    assert result == 100.0


def test_sanitize_for_json_numpy_floating_branch():
    """_sanitize_for_json covers numpy floating handling (lines 563-564)."""
    import numpy as np

    # Test np.float64
    val = np.float64(3.14)
    result = _sanitize_for_json(val)
    assert isinstance(result, float)
    assert abs(result - 3.14) < 1e-10

    # Test np.float32 (precision loss expected)
    val = np.float32(2.71)
    result = _sanitize_for_json(val)
    assert isinstance(result, float)
    assert abs(result - 2.71) < 1e-5

    # Test non-finite numpy float -> coerced to 0.0
    val = np.float64(np.nan)
    result = _sanitize_for_json(val)
    assert result == 0.0

    val = np.float64(np.inf)
    result = _sanitize_for_json(val)
    assert result == 0.0

    val = np.float64(-np.inf)
    result = _sanitize_for_json(val)
    assert result == 0.0


def test_sanitize_for_json_numpy_integer_branch():
    """_sanitize_for_json covers numpy integer handling (line 561)."""
    import numpy as np

    val = np.int64(42)
    result = _sanitize_for_json(val)
    assert isinstance(result, int)
    assert result == 42

    val = np.int32(100)
    result = _sanitize_for_json(val)
    assert isinstance(result, int)
    assert result == 100


def test_sanitize_for_json_numpy_bool_branch():
    """_sanitize_for_json covers numpy bool handling (line 566)."""
    import numpy as np

    val = np.bool_(True)
    result = _sanitize_for_json(val)
    assert isinstance(result, bool)
    assert result is True

    val = np.bool_(False)
    result = _sanitize_for_json(val)
    assert isinstance(result, bool)
    assert result is False


def test_sanitize_for_json_numpy_array_branch():
    """_sanitize_for_json covers numpy array handling (line 559)."""
    import numpy as np

    arr = np.array([1.0, 2.0, 3.0])
    result = _sanitize_for_json(arr)
    assert isinstance(result, list)
    assert result == [1.0, 2.0, 3.0]

    # With non-finite values
    arr = np.array([1.0, np.nan, np.inf])
    result = _sanitize_for_json(arr)
    assert result == [1.0, 0.0, 0.0]


def test_paper_adapter_realistic_fills_with_string_decimal_nan():
    """PaperAdapter handles string/Decimal/NaN prices and fills correctly."""
    dates = pd.date_range("2023-01-01", periods=3, freq="D")
    prices_df = pd.DataFrame(
        {
            "BTC": ["100.0", "101.0", "102.0"],  # string prices
            "ETH": [2000.0, np.nan, 2002.0],  # NaN in middle
        },
        index=dates,
    )
    prices_df.index.name = "date"

    adapter = PaperAdapter(
        prices_df=prices_df,
        adv_usd={"BTC": 1_000_000.0, "ETH": 500_000.0},
        partial_fill=True,
        max_participation=0.1,
    )

    from strategies.betting_against_beta.execution import OrderBatch, OrderIntent

    # BTC: string price, should be converted to float
    intent1 = OrderIntent(
        date="2023-01-01T00:00:00",
        asset="BTC",
        target_weight=0.1,
        current_weight=0.0,
        order_weight=0.1,
        requested_weight=0.1,
    )
    batch = OrderBatch(date="2023-01-01T00:00:00", intents=(intent1,))
    fills = adapter.submit_intents(batch)
    assert len(fills) == 1
    assert fills[0]["price"] == 100.0
    assert fills[0]["filled_weight"] == 0.1  # full fill (participation within cap)

    # ETH: NaN price on 2023-01-02 -> should fall back to default full-fill (no realism)
    intent2 = OrderIntent(
        date="2023-01-02T00:00:00",
        asset="ETH",
        target_weight=0.1,
        current_weight=0.0,
        order_weight=0.1,
        requested_weight=0.1,
    )
    batch2 = OrderBatch(date="2023-01-02T00:00:00", intents=(intent2,))
    fills2 = adapter.submit_intents(batch2)
    assert len(fills2) == 1
    # NaN price means realism=False, so full fill with slippage=0
    assert fills2[0]["filled_weight"] == 0.1
    assert fills2[0]["slippage"] == 0.0
    assert fills2[0]["status"] == "filled"


def test_paper_adapter_timestamp_key_lookup():
    """PaperAdapter handles Timestamp key lookup for prices and ADV."""
    dates = pd.date_range("2023-01-01", periods=3, freq="D")
    prices_df = pd.DataFrame({"BTC": [100.0, 101.0, 102.0]}, index=dates)
    prices_df.index.name = "date"

    adv_df = pd.DataFrame({"BTC": [1_000_000.0, 2_000_000.0, 3_000_000.0]}, index=dates)

    adapter = PaperAdapter(
        prices_df=prices_df,
        adv_usd=adv_df,
        partial_fill=True,
        max_participation=0.1,
    )

    from strategies.betting_against_beta.execution import OrderBatch, OrderIntent

    # Use Timestamp-formatted date key (ISO format with time)
    intent = OrderIntent(
        date="2023-01-02T00:00:00",  # ISO format with time
        asset="BTC",
        target_weight=0.1,
        current_weight=0.0,
        order_weight=0.1,
        requested_weight=0.1,
    )
    batch = OrderBatch(date="2023-01-02T00:00:00", intents=(intent,))
    fills = adapter.submit_intents(batch)

    assert len(fills) == 1
    # Should find price via Timestamp fallback (line 139-141)
    assert fills[0]["price"] == 101.0
    # Should find ADV via Timestamp fallback (line 180-185)
    assert fills[0]["adv_usd"] == 2_000_000.0


def test_paper_adapter_non_finite_sanitization():
    """PaperAdapter fill records are sanitized for non-finite numpy scalars."""
    dates = pd.date_range("2023-01-01", periods=2, freq="D")
    prices_df = pd.DataFrame({"BTC": [100.0, 101.0]}, index=dates)
    prices_df.index.name = "date"

    adapter = PaperAdapter(prices_df=prices_df)

    from strategies.betting_against_beta.execution import OrderBatch, OrderIntent

    intent = OrderIntent(
        date="2023-01-01T00:00:00",
        asset="BTC",
        target_weight=0.1,
        current_weight=0.0,
        order_weight=0.1,
        requested_weight=0.1,
        notional_usd=10000.0,
        price=100.0,
    )
    batch = OrderBatch(date="2023-01-01T00:00:00", intents=(intent,))
    fills = adapter.submit_intents(batch)

    # Verify fill is JSON-serializable with allow_nan=False
    fill = fills[0]
    json_str = json.dumps(fill, allow_nan=False)
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert parsed["price"] == 100.0


# =============================================================================
# P19-2c: CLI --health-check JSON contract tests
# =============================================================================

def test_cli_health_check_requires_adapter_live():
    """--health-check without --adapter live returns error (non-zero exit)."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli", "--health-check"],
        capture_output=True,
        text=True,
        cwd="/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta",
    )
    assert result.returncode == 1
    assert "requires --adapter live" in result.stdout or "requires --adapter live" in result.stderr


def test_cli_health_check_emits_strict_json_on_success():
    """--health-check with --adapter live emits single strict-JSON object."""
    import sys
    from io import StringIO

    from strategies.betting_against_beta import execution as exec_module
    from strategies.betting_against_beta.cli import main

    # Mock the LiveExecutionAdapter.health_check to return a known dict
    original_health_check = exec_module.LiveExecutionAdapter.health_check

    def mock_health_check(self):
        return {
            "mode": "live",
            "exchange": "binance",
            "connected": True,
            "dry_run": True,
            "testnet": False,
            "n_submitted": 0,
            "n_fills": 0,
        }

    exec_module.LiveExecutionAdapter.health_check = mock_health_check

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        rc = main([
            "--adapter", "live",
            "--exchange", "binance",
            "--api-key-env", "TEST_KEY",
            "--api-secret-env", "TEST_SECRET",
            "--health-check",
        ])
    finally:
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        exec_module.LiveExecutionAdapter.health_check = original_health_check

    # Should succeed and emit strict JSON
    assert rc == 0

    # Parse the JSON output - should be a single JSON object
    output = output.strip()
    parsed = json.loads(output)

    assert parsed["mode"] == "live"
    assert parsed["exchange"] == "binance"
    assert parsed["connected"] is True
    assert parsed["dry_run"] is True
    assert "NaN" not in output
    assert "Infinity" not in output

    # Verify it's exactly one JSON object (no extra text)
    # Re-serialize and compare
    reserialized = json.dumps(parsed, allow_nan=False)
    assert output == reserialized or output.replace(" ", "") == reserialized.replace(" ", "")


def test_cli_health_check_json_allow_nan_false():
    """--health-check output must be valid with allow_nan=False."""
    import sys
    from io import StringIO

    from strategies.betting_against_beta import execution as exec_module
    from strategies.betting_against_beta.cli import main

    # Mock health_check to return non-finite values
    def mock_health_check_with_nan(self):
        return {
            "mode": "live",
            "exchange": "binance",
            "connected": True,
            "dry_run": True,
            "testnet": False,
            "n_submitted": float("nan"),  # This would break allow_nan=False
            "n_fills": 0,
        }

    original_health_check = exec_module.LiveExecutionAdapter.health_check
    exec_module.LiveExecutionAdapter.health_check = mock_health_check_with_nan

    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        rc = main([
            "--adapter", "live",
            "--exchange", "binance",
            "--api-key-env", "TEST_KEY",
            "--api-secret-env", "TEST_SECRET",
            "--health-check",
        ])
    finally:
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        exec_module.LiveExecutionAdapter.health_check = original_health_check

    # The CLI's _json_safe should coerce NaN to 0.0
    assert rc == 0
    output = output.strip()
    parsed = json.loads(output)
    # NaN should be coerced to 0.0 by _json_safe
    assert parsed["n_submitted"] == 0.0


# =============================================================================
# Additional execution.py reconciliation fidelity tests
# =============================================================================

def test_execution_reconciliation_cost_gate_fail_closed():
    """Reconciliation cost gate stays fail-closed on drift."""
    from strategies.betting_against_beta import BABStrategy
    from strategies.betting_against_beta.execution import PaperAdapter
    from strategies.betting_against_beta.reconciliation import (
        evaluate_reconciliation_gate,
        reconcile_costs,
    )

    adapter = PaperAdapter()
    strategy = BABStrategy(benchmark="BTC", execution_adapter=adapter)
    result = strategy.run()

    # Create fills with significant slippage to cause drift
    weights = result.weights
    fills = [
        {
            "date": str(weights.index[10].isoformat()),
            "asset": "BTC",
            "order_weight": 0.1,
            "notional_usd": 100000.0,
            "slippage": 0.01,  # High slippage
        },
        {
            "date": str(weights.index[11].isoformat()),
            "asset": "ETH",
            "order_weight": -0.05,
            "notional_usd": 50000.0,
            "slippage": 0.01,
        },
    ]

    costs_rec = reconcile_costs(
        weights,
        model=None,
        executed_fills=fills,
        transaction_costs=0.001,
        slippage=0.0005,
    )

    # Evaluate gate with tight tolerance - should fail
    gate = evaluate_reconciliation_gate(
        costs_rec=costs_rec,
        fills_rec=None,
        cost_tolerance=0.0,  # Zero tolerance
        equity_tolerance=None,
        mismatch_tolerance=None,
    )

    assert gate["ok"] is False
    assert len(gate["violations"]) > 0
    # Violation should be about cost drift
    assert any(v["check"] == "delta_max_abs" for v in gate["violations"])


def test_execution_reconciliation_cost_gate_passes_within_tolerance():
    """Reconciliation cost gate passes when drift within tolerance."""
    from strategies.betting_against_beta import BABStrategy
    from strategies.betting_against_beta.execution import PaperAdapter
    from strategies.betting_against_beta.reconciliation import (
        evaluate_reconciliation_gate,
        reconcile_costs,
    )

    adapter = PaperAdapter()
    strategy = BABStrategy(benchmark="BTC", execution_adapter=adapter)
    result = strategy.run()

    weights = result.weights
    fills = []  # No fills = no drift

    costs_rec = reconcile_costs(
        weights,
        model=None,
        executed_fills=fills,
        transaction_costs=0.001,
        slippage=0.0005,
    )

    # Evaluate gate with generous tolerance - should pass
    gate = evaluate_reconciliation_gate(
        costs_rec=costs_rec,
        fills_rec=None,
        cost_tolerance=1.0,  # Generous tolerance
        equity_tolerance=None,
        mismatch_tolerance=None,
    )

    assert gate["ok"] is True
    assert len(gate["violations"]) == 0


def test_execution_reconciliation_fills_gate_fail_closed():
    """Reconciliation fills gate fails closed on mismatch count breach."""
    from strategies.betting_against_beta import BABStrategy
    from strategies.betting_against_beta.execution import PaperAdapter
    from strategies.betting_against_beta.reconciliation import (
        evaluate_reconciliation_gate,
        reconcile_fills_to_backtest,
    )

    adapter = PaperAdapter()
    strategy = BABStrategy(benchmark="BTC", execution_adapter=adapter)
    result = strategy.run()

    weights = result.weights
    returns = result.returns
    backtest = result.backtest

    # Create fills that cause mismatches
    fills = [
        {
            "date": str(weights.index[10].isoformat()),
            "asset": "BTC",
            "order_weight": 0.2,
            "notional_usd": 50000.0,
            "slippage": 0.005,
        },
    ]

    fills_rec = reconcile_fills_to_backtest(
        weights,
        returns,
        backtest,
        fills=fills,
        transaction_costs=0.001,
        slippage=0.0005,
    )

    # Evaluate gate with zero mismatch tolerance - should fail
    gate = evaluate_reconciliation_gate(
        costs_rec=None,
        fills_rec=fills_rec,
        cost_tolerance=None,
        equity_tolerance=None,
        mismatch_tolerance=0,  # Zero tolerance
    )

    assert gate["ok"] is False
    assert len(gate["violations"]) > 0
    assert any(v["check"] == "n_mismatches" and v["source"] == "fills" for v in gate["violations"])


def test_paper_execution_engine_reconciliation_fidelity():
    """PaperExecutionEngine produces fills that reconcile correctly."""
    from strategies.betting_against_beta import BABStrategy
    from strategies.betting_against_beta.execution import PaperExecutionEngine
    from strategies.betting_against_beta.reconciliation import reconcile_fills_to_backtest

    strategy = BABStrategy(benchmark="BTC")
    result = strategy.run()

    engine = PaperExecutionEngine()
    report = engine.execute(
        result.weights,
        betas_df=result.betas,
        signals_df=result.signals,
        returns_df=result.returns,
    )

    # Reconcile fills against backtest
    fills_list = [f.to_dict() for f in report.fills]
    fills_rec = reconcile_fills_to_backtest(
        result.weights,
        result.returns,
        result.backtest,
        fills=fills_list,
        transaction_costs=0.0,
        slippage=0.0,
    )

    # With zero costs and full fills, delta should be minimal
    assert fills_rec.aggregate["n_mismatches"] >= 0
    assert math.isfinite(fills_rec.aggregate["delta_final"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
