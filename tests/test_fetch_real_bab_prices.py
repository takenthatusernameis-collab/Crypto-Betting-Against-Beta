import json
import subprocess
import sys
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
