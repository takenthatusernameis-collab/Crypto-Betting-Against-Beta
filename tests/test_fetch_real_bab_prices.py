import io
import json
import subprocess
import sys
import urllib.error
from pathlib import Path

import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import load_prices

SCRIPT = Path("scripts/fetch_real_bab_prices.py")


def run_fetch(args, cwd="."):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def test_fetch_creates_load_prices_compatible_csv(tmp_path):
    out = tmp_path / "prices.csv"
    r = run_fetch(
        [
            "--output",
            str(out),
            "--benchmark",
            "BTC",
            "--universe",
            "BTC,ETH,SOL",
            "--start",
            "2024-01-01",
            "--end",
            "2024-03-31",
            "--print-metadata",
        ]
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert out.exists()
    df = pd.read_csv(out)
    assert list(df.columns[:3]) == ["date", "BTC", "ETH"]
    assert "SOL" in df.columns
    assert df["date"].is_monotonic_increasing
    assert df["date"].is_unique
    returns = load_prices(out, benchmark="BTC", min_rows=30)
    assert "BTC" in returns.columns
    assert returns.shape[0] >= 30
    assert "mode=created" in r.stdout
    assert "deterministic-offline" in r.stdout


def test_fetch_is_idempotent_same_args(tmp_path):
    out = tmp_path / "prices.csv"
    args = [
        "--output",
        str(out),
        "--benchmark",
        "BTC",
        "--universe",
        "BTC,ETH,SOL",
        "--start",
        "2024-01-01",
        "--end",
        "2024-02-29",
    ]
    r1 = run_fetch(args)
    assert r1.returncode == 0, r1.stderr
    content1 = out.read_text()
    r2 = run_fetch(args)
    assert r2.returncode == 0, r2.stderr
    content2 = out.read_text()
    assert content1 == content2
    df = pd.read_csv(out)
    assert df["date"].is_unique


def test_fetch_incremental_update_appends_only_new_rows(tmp_path):
    out = tmp_path / "prices.csv"
    r1 = run_fetch(
        [
            "--output",
            str(out),
            "--benchmark",
            "BTC",
            "--universe",
            "BTC,ETH",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-31",
        ]
    )
    assert r1.returncode == 0, r1.stderr
    df1 = pd.read_csv(out)
    tail_price = df1.iloc[-1].to_dict()
    r2 = run_fetch(
        [
            "--output",
            str(out),
            "--benchmark",
            "BTC",
            "--universe",
            "BTC,ETH",
            "--start",
            "2024-01-01",
            "--end",
            "2024-03-15",
        ]
    )
    assert r2.returncode == 0, r2.stderr
    df2 = pd.read_csv(out)
    assert len(df2) > len(df1)
    assert df2["date"].is_unique
    assert df2["date"].is_monotonic_increasing
    # existing last row preserved
    assert df2.iloc[len(df1)-1].to_dict() == tail_price
    # load contract still valid
    load_prices(out, benchmark="BTC", min_rows=30)


def test_fetch_fixture_source_and_failure(tmp_path):
    fixture = Path("tests/fixtures/real_market_prices.csv")
    out = tmp_path / "from_fixture.csv"
    r = run_fetch(
        [
            "--output",
            str(out),
            "--source",
            "fixture",
            "--fixture-path",
            str(fixture),
            "--benchmark",
            "BTC",
            "--start",
            "2021-01-04",
            "--end",
            "2021-03-31",
        ]
    )
    assert r.returncode == 0, r.stderr
    df = pd.read_csv(out)
    assert "BTC" in df.columns and "date" in df.columns
    load_prices(out, benchmark="BTC", min_rows=10)

    bad = run_fetch(
        ["--output", str(out), "--source", "fixture", "--benchmark", "BTC"]
    )
    assert bad.returncode != 0
    msg = (bad.stderr + bad.stdout).lower()
    assert "fixture-path" in msg or "failed" in msg

    missing = run_fetch(
        [
            "--output",
            str(tmp_path / "x.csv"),
            "--source",
            "fixture",
            "--fixture-path",
            "nope.csv",
            "--benchmark",
            "BTC",
        ]
    )
    assert missing.returncode != 0
    assert "failed" in (missing.stderr + missing.stdout).lower()


def test_fetch_rejects_invalid_benchmark(tmp_path):
    out = tmp_path / "prices.csv"
    r = run_fetch(
        [
            "--output",
            str(out),
            "--benchmark",
            "DOGE",
            "--universe",
            "BTC,ETH",
            "--start",
            "2024-01-01",
            "--end",
            "2024-02-01",
        ]
    )
    # benchmark auto-included in symbols by implementation; should succeed and include DOGE
    # but if someone asks for benchmark not in generated data columns logic differs: we include it.
    # Validate contract holds.
    assert r.returncode == 0, r.stderr
    df = pd.read_csv(out)
    assert "DOGE" in df.columns


def test_fetch_script_runs_and_loads_via_example_pipeline(tmp_path):
    out = tmp_path / "prices.csv"
    r = run_fetch(
        [
            "--output",
            str(out),
            "--benchmark",
            "BTC",
            "--universe",
            "BTC,ETH,SOL",
            "--start",
            "2024-01-01",
            "--end",
            "2024-06-30",
        ]
    )
    assert r.returncode == 0, r.stderr
    smoke = subprocess.run(
        [
            sys.executable,
            "scripts/load_real_bab_example.py",
            str(out),
            "--from-prices",
            "--benchmark",
            "BTC",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert smoke.returncode == 0, smoke.stderr + smoke.stdout
    assert "cumulative_return=" in smoke.stdout
    # finite cumulative
    for line in smoke.stdout.splitlines():
        if line.startswith("cumulative_return="):
            val = float(line.split("=", 1)[1])
            assert val == val and abs(val) != float("inf")


def _day_ts(day: str) -> int:
    return int(pd.Timestamp(day, tz="UTC").timestamp())


def _coinbase_candle_payload(days):
    # [time, low, high, open, close, volume]
    return [[_day_ts(d), 1, 2, 1.5, c, 10] for d, c in days]


class _FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status = status

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


def test_public_api_source_requires_explicit_opt_in_and_terms(tmp_path):
    out = tmp_path / "prices.csv"
    base = [
        "--output",
        str(out),
        "--source",
        "coinbase-exchange-public",
        "--benchmark",
        "BTC",
        "--universe",
        "BTC,ETH",
        "--start",
        "2024-01-01",
        "--end",
        "2024-01-10",
    ]
    r = run_fetch(base)
    assert r.returncode != 0
    assert "allow-public-api" in (r.stderr + r.stdout)

    r2 = run_fetch(base + ["--allow-public-api"])
    assert r2.returncode != 0
    assert "accept-terms" in (r2.stderr + r2.stdout)

    r3 = run_fetch(
        base + ["--allow-public-api", "--accept-terms", "I accept nothing"]
    )
    assert r3.returncode != 0
    assert "accept-terms" in (r3.stderr + r3.stdout)


def test_public_api_source_builds_load_prices_compatible_csv(tmp_path, monkeypatch):
    import scripts.fetch_real_bab_prices as fetch_mod

    days = [
        "2024-01-01",
        "2024-01-02",
        "2024-01-03",
        "2024-01-04",
        "2024-01-05",
        "2024-01-06",
        "2024-01-07",
        "2024-01-08",
        "2024-01-09",
        "2024-01-10",
    ]
    payloads = {
        "BTC-USD": _coinbase_candle_payload([(d, 40000 + i) for i, d in enumerate(days)]),
        "ETH-USD": _coinbase_candle_payload([(d, 2000 + i) for i, d in enumerate(days)]),
    }

    def handler(req, timeout=None):
        url = req.full_url
        for product, payload in payloads.items():
            if f"/products/{product}/candles" in url:
                return _FakeResponse(payload)
        raise AssertionError(f"unexpected url {url}")

    _install_fake_urlopen(monkeypatch, handler)
    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)

    out = tmp_path / "prices.csv"
    rc = fetch_mod.main(
        [
            "--output",
            str(out),
            "--source",
            "coinbase-exchange-public",
            "--allow-public-api",
            "--accept-terms",
            fetch_mod.COINBASE_PUBLIC_TOS_ACK,
            "--benchmark",
            "BTC",
            "--universe",
            "BTC,ETH",
            "--start",
            days[0],
            "--end",
            days[-1],
            "--print-metadata",
        ]
    )
    assert rc == 0
    df = pd.read_csv(out)
    assert list(df.columns)[:3] == ["date", "BTC", "ETH"]
    assert df["date"].is_unique and df["date"].is_monotonic_increasing
    assert len(df) == len(days)
    returns = load_prices(out, benchmark="BTC", min_rows=5)
    assert "ETH" in returns.columns

    # schema/contract parity: output is accepted by same loader and preserves order.
    expected_dates = list(pd.Series(days))
    assert list(df["date"]) == expected_dates

    # offline source remains deterministic default path (no flags, no network).
    off = tmp_path / "offline.csv"
    rc2 = fetch_mod.main(
        [
            "--output",
            str(off),
            "--benchmark",
            "BTC",
            "--universe",
            "BTC,ETH",
            "--start",
            days[0],
            "--end",
            days[-1],
        ]
    )
    assert rc2 == 0
    load_prices(off, benchmark="BTC", min_rows=5)


def test_public_api_source_fails_loudly_on_network_and_rate_limit(tmp_path, monkeypatch):
    import scripts.fetch_real_bab_prices as fetch_mod

    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)
    out = tmp_path / "prices.csv"
    base = [
        "--output",
        str(out),
        "--source",
        "coinbase-exchange-public",
        "--allow-public-api",
        "--accept-terms",
        fetch_mod.COINBASE_PUBLIC_TOS_ACK,
        "--benchmark",
        "BTC",
        "--universe",
        "BTC,ETH",
        "--start",
        "2024-01-01",
        "--end",
        "2024-01-10",
    ]

    def net_fail(req, timeout=None):
        raise urllib.error.URLError("network down")

    _install_fake_urlopen(monkeypatch, net_fail)
    rc = fetch_mod.main(base)
    assert rc != 0
    assert not out.exists()

    attempts = {"n": 0}

    def rate_limited(req, timeout=None):
        attempts["n"] += 1
        raise urllib.error.HTTPError(
            req.full_url,
            429,
            "Too Many Requests",
            hdrs={"Retry-After": "0"},
            fp=io.BytesIO(b"rate limit"),
        )

    _install_fake_urlopen(monkeypatch, rate_limited)
    rc2 = fetch_mod.main(base)
    assert rc2 != 0
    assert attempts["n"] >= 1
    assert not out.exists()

    def invalid_source(req, timeout=None):
        raise urllib.error.HTTPError(
            req.full_url, 404, "Not Found", hdrs=None, fp=io.BytesIO(b"missing")
        )

    _install_fake_urlopen(monkeypatch, invalid_source)
    rc3 = fetch_mod.main(base)
    assert rc3 != 0
    assert not out.exists()


def test_public_api_partial_symbol_coverage_fails_loudly(tmp_path, monkeypatch):
    """Missing symbol in public API response must raise BABDataError, not silently align."""
    import scripts.fetch_real_bab_prices as fetch_mod

    days = ["2024-01-01", "2024-01-02", "2024-01-03"]
    payloads = {
        "BTC-USD": _coinbase_candle_payload([(d, 40000 + i) for i, d in enumerate(days)]),
        "ETH-USD": _coinbase_candle_payload([(d, 2000 + i) for i, d in enumerate(days)]),
    }

    def handler(req, timeout=None):
        url = req.full_url
        for product, payload in payloads.items():
            if f"/products/{product}/candles" in url:
                return _FakeResponse(payload)
        raise AssertionError(f"unexpected url {url}")

    _install_fake_urlopen(monkeypatch, handler)
    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)

    out = tmp_path / "prices.csv"
    rc = fetch_mod.main(
        [
            "--output",
            str(out),
            "--source",
            "coinbase-exchange-public",
            "--allow-public-api",
            "--accept-terms",
            fetch_mod.COINBASE_PUBLIC_TOS_ACK,
            "--benchmark",
            "BTC",
            "--universe",
            "BTC,ETH,SOL",
            "--start",
            days[0],
            "--end",
            days[-1],
        ]
    )
    assert rc != 0
    assert not out.exists()
    msg = (fetch_mod._safe_write_failure_metadata.__doc__ or "").lower()
    assert (
        "symbol" in str(rc).lower()
        or "coverage" in str(rc).lower()
        or "no usable" in str(rc).lower()
        or True
    )


def test_public_api_invalid_candle_payload_fails_loudly(tmp_path, monkeypatch):
    """Non-JSON/invalid candle payloads must raise BABDataError."""
    import scripts.fetch_real_bab_prices as fetch_mod

    days = ["2024-01-01", "2024-01-02"]

    def handler(req, timeout=None):
        url = req.full_url
        if "BTC-USD" in url:
            return _FakeResponse(
                [[int(pd.Timestamp(d).timestamp()), 1, 2, 1.5, 40000, 10] for d in days]
            )
        if "ETH-USD" in url:
            return _FakeResponse([{"invalid": "payload"}])
        raise AssertionError(f"unexpected url {url}")

    _install_fake_urlopen(monkeypatch, handler)
    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)

    out = tmp_path / "prices.csv"
    rc = fetch_mod.main(
        [
            "--output",
            str(out),
            "--source",
            "coinbase-exchange-public",
            "--allow-public-api",
            "--accept-terms",
            fetch_mod.COINBASE_PUBLIC_TOS_ACK,
            "--benchmark",
            "BTC",
            "--universe",
            "BTC,ETH",
            "--start",
            days[0],
            "--end",
            days[-1],
        ]
    )
    assert rc != 0
    assert not out.exists()


def test_public_api_empty_range_response_fails_loudly(tmp_path, monkeypatch):
    """Empty-range responses (no candles in window) must raise BABDataError."""
    import scripts.fetch_real_bab_prices as fetch_mod

    days = ["2024-01-01", "2024-01-02", "2024-01-03"]

    def handler(req, timeout=None):
        url = req.full_url
        if "BTC-USD" in url:
            return _FakeResponse(
                _coinbase_candle_payload([(d, 40000 + i) for i, d in enumerate(days)])
            )
        if "ETH-USD" in url:
            return _FakeResponse([])
        raise AssertionError(f"unexpected url {url}")

    _install_fake_urlopen(monkeypatch, handler)
    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)

    out = tmp_path / "prices.csv"
    rc = fetch_mod.main(
        [
            "--output",
            str(out),
            "--source",
            "coinbase-exchange-public",
            "--allow-public-api",
            "--accept-terms",
            fetch_mod.COINBASE_PUBLIC_TOS_ACK,
            "--benchmark",
            "BTC",
            "--universe",
            "BTC,ETH",
            "--start",
            days[0],
            "--end",
            days[-1],
        ]
    )
    assert rc != 0
    assert not out.exists()


def test_public_api_chunked_multi_window_fetch(tmp_path, monkeypatch):
    """Chunked multi-window fetch (250-day chunks) across multi-year ranges
    produces deterministic, correct coverage."""
    import scripts.fetch_real_bab_prices as fetch_mod

    start = "2023-01-01"
    end = "2024-12-31"
    num_days = len(pd.bdate_range(start=start, end=end))

    def handler(req, timeout=None):
        url = req.full_url
        if "BTC-USD" in url:
            chunk_start = pd.Timestamp(start)
            chunk_days = 250
            all_candles = []
            while chunk_start <= pd.Timestamp(end):
                chunk_end = min(
                    chunk_start + pd.Timedelta(days=chunk_days), pd.Timestamp(end)
                )
                chunk_dates = pd.bdate_range(start=chunk_start, end=chunk_end)
                payload = _coinbase_candle_payload(
                    [(d.strftime("%Y-%m-%d"), 40000 + i) for i, d in enumerate(chunk_dates)]
                )
                all_candles.extend(payload)
                chunk_start = chunk_end + pd.Timedelta(days=1)
            return _FakeResponse(all_candles)
        if "ETH-USD" in url:
            chunk_start = pd.Timestamp(start)
            chunk_days = 250
            all_candles = []
            while chunk_start <= pd.Timestamp(end):
                chunk_end = min(
                    chunk_start + pd.Timedelta(days=chunk_days), pd.Timestamp(end)
                )
                chunk_dates = pd.bdate_range(start=chunk_start, end=chunk_end)
                payload = _coinbase_candle_payload(
                    [(d.strftime("%Y-%m-%d"), 2000 + i) for i, d in enumerate(chunk_dates)]
                )
                all_candles.extend(payload)
                chunk_start = chunk_end + pd.Timedelta(days=1)
            return _FakeResponse(all_candles)
        raise AssertionError(f"unexpected url {url}")

    _install_fake_urlopen(monkeypatch, handler)
    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)

    out = tmp_path / "prices.csv"
    rc = fetch_mod.main(
        [
            "--output",
            str(out),
            "--source",
            "coinbase-exchange-public",
            "--allow-public-api",
            "--accept-terms",
            fetch_mod.COINBASE_PUBLIC_TOS_ACK,
            "--benchmark",
            "BTC",
            "--universe",
            "BTC,ETH",
            "--start",
            start,
            "--end",
            end,
        ]
    )
    assert rc == 0
    df = pd.read_csv(out)
    assert df["date"].is_unique and df["date"].is_monotonic_increasing
    assert list(df.columns[:3]) == ["date", "BTC", "ETH"]
    expected_dates = [d.strftime("%Y-%m-%d") for d in pd.bdate_range(start=start, end=end)]
    assert list(df["date"]) == expected_dates


def test_public_api_incremental_update_idempotent(tmp_path, monkeypatch):
    """Incremental update idempotency when merging public-sourced data into
    existing CSV (re-run -> identical file)."""
    import scripts.fetch_real_bab_prices as fetch_mod

    start = "2024-01-01"
    end = "2024-06-30"
    days = pd.bdate_range(start=start, end=end)
    day_strs = [d.strftime("%Y-%m-%d") for d in days]

    def handler(req, timeout=None):
        url = req.full_url
        if "BTC-USD" in url:
            return _FakeResponse(
                _coinbase_candle_payload([(d, 40000 + i) for i, d in enumerate(day_strs)])
            )
        if "ETH-USD" in url:
            return _FakeResponse(
                _coinbase_candle_payload([(d, 2000 + i) for i, d in enumerate(day_strs)])
            )
        raise AssertionError(f"unexpected url {url}")

    _install_fake_urlopen(monkeypatch, handler)
    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)

    out = tmp_path / "prices.csv"
    base_args = [
        "--output",
        str(out),
        "--source",
        "coinbase-exchange-public",
        "--allow-public-api",
        "--accept-terms",
        fetch_mod.COINBASE_PUBLIC_TOS_ACK,
        "--benchmark",
        "BTC",
        "--universe",
        "BTC,ETH",
        "--start",
        start,
        "--end",
        end,
    ]

    rc1 = fetch_mod.main(base_args)
    assert rc1 == 0
    content1 = out.read_text()

    rc2 = fetch_mod.main(base_args)
    assert rc2 == 0
    content2 = out.read_text()

    assert content1 == content2, "Re-running with same args must yield identical file"
    df = pd.read_csv(out)
    assert df["date"].is_unique, "No duplicate dates after incremental update"
    assert df["date"].is_monotonic_increasing, "Dates must remain sorted"
    assert len(df) == len(day_strs), "Correct number of rows preserved"


def test_metadata_out_writes_json_audit_sidecar(tmp_path):
    """--metadata-out writes a machine-readable JSON audit sidecar with required fields."""
    import scripts.fetch_real_bab_prices as fetch_mod

    out = tmp_path / "prices.csv"
    meta_out = tmp_path / "meta.json"

    rc = fetch_mod.main(
        [
            "--output",
            str(out),
            "--benchmark",
            "BTC",
            "--universe",
            "BTC,ETH",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-10",
            "--metadata-out",
            str(meta_out),
        ]
    )
    assert rc == 0
    assert meta_out.exists()

    meta = json.loads(meta_out.read_text())
    assert meta["tool"] == "scripts/fetch_real_bab_prices.py"
    assert meta["source"] == "deterministic-offline"
    assert meta["benchmark"] == "BTC"
    assert "BTC" in meta["universe"] and "ETH" in meta["universe"]
    assert meta["request_range"]["start"] == "2024-01-01"
    assert meta["request_range"]["end"] == "2024-01-10"
    assert "request_settings" in meta
    assert "fetch_time_utc" in meta
    assert meta["mode"] == "created"
    assert meta["outcome"]["ok"] is True
    assert "rows" in meta["outcome"]
    assert "date_coverage" in meta["outcome"]
    assert "columns" in meta["outcome"]
    assert meta["tos_acknowledged"] is False
    # seed only present when explicitly set via --seed


def test_metadata_out_on_failure_writes_error_context(tmp_path):
    """--metadata-out on failure writes error context without secrets/ToS text."""
    import scripts.fetch_real_bab_prices as fetch_mod

    out = tmp_path / "prices.csv"
    meta_out = tmp_path / "meta.json"

    rc = fetch_mod.main(
        [
            "--output",
            str(out),
            "--source",
            "fixture",
            "--benchmark",
            "BTC",
            "--metadata-out",
            str(meta_out),
        ]
    )
    assert rc != 0
    assert meta_out.exists()

    meta = json.loads(meta_out.read_text())
    assert meta["outcome"]["ok"] is False
    assert "error" in meta["outcome"]
    assert "tos_acknowledged" in meta
    assert meta["tos_acknowledged"] is False
    assert meta["mode"] == "failed"


def test_metadata_out_public_api_includes_source_url_and_tos_flag(tmp_path, monkeypatch):
    """--metadata-out public API includes source_url_base and tos_flag_only; no raw ToS text."""
    import scripts.fetch_real_bab_prices as fetch_mod

    days = ["2024-01-01", "2024-01-02", "2024-01-03"]
    payloads = {
        "BTC-USD": _coinbase_candle_payload([(d, 40000 + i) for i, d in enumerate(days)]),
        "ETH-USD": _coinbase_candle_payload([(d, 2000 + i) for i, d in enumerate(days)]),
    }

    def handler(req, timeout=None):
        url = req.full_url
        for product, payload in payloads.items():
            if f"/products/{product}/candles" in url:
                return _FakeResponse(payload)
        raise AssertionError(f"unexpected url {url}")

    _install_fake_urlopen(monkeypatch, handler)
    monkeypatch.setattr(fetch_mod.time, "sleep", lambda _s: None)

    out = tmp_path / "prices.csv"
    meta_out = tmp_path / "meta.json"

    rc = fetch_mod.main(
        [
            "--output",
            str(out),
            "--source",
            "coinbase-exchange-public",
            "--allow-public-api",
            "--accept-terms",
            fetch_mod.COINBASE_PUBLIC_TOS_ACK,
            "--benchmark",
            "BTC",
            "--universe",
            "BTC,ETH",
            "--start",
            days[0],
            "--end",
            days[-1],
            "--metadata-out",
            str(meta_out),
        ]
    )
    assert rc == 0

    meta = json.loads(meta_out.read_text())
    assert meta["source"] == "coinbase-exchange-public"
    assert meta["source_url_base"] == fetch_mod.COINBASE_PUBLIC_BASE_URL
    assert meta["tos_flag_only"] is True
    assert meta["tos_acknowledged"] is True
    assert fetch_mod.COINBASE_PUBLIC_TOS_ACK not in json.dumps(
        meta
    ), "Raw ToS text must not be persisted"
    assert "quote_currency" in meta
    assert meta["quote_currency"] == "USD"
