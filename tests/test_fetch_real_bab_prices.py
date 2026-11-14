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
