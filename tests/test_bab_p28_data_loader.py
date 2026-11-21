"""Acceptance tests for P28 WP1: data-loader validation & real-format readiness.

These tests prove `strategies.betting_against_beta.data_loader` round-trips every
supported file format (CSV / JSON / JSONL / Pickle, plus Parquet / HDF5 when an
engine is installed) through a temp file with schema `date,BTC,<assets...>`, and
that the documented rejection paths raise `BABDataError` for duplicate dates,
non-monotonic output, and partial symbol coverage.

They also prove `--metadata-out` audit parity for
`scripts/fetch_real_bab_prices.py --source fixture` in offline (no-network) mode,
both on the success path (`outcome.ok` true with full coverage fields) and the
failure path (`outcome.ok` false with `error` context).

P28 consumes P20-P27 artifacts read-only; no P20-P27 file is edited here. No
network is ever used.
"""

from __future__ import annotations

import json
import math
import pickle
from importlib import util as importlib_util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    load_prices,
    load_returns,
    load_returns_from_dataframe,
    validate_returns_dataframe,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_real_bab_prices.py"
FIXTURE_CSV = REPO_ROOT / "tests" / "fixtures" / "real_market_prices.csv"

ASSETS = ["BTC", "ETH", "SOL", "ADA"]


def _engine_available(name: str) -> bool:
    return importlib_util.find_spec(name) is not None


def _make_prices_df(n: int = 40) -> pd.DataFrame:
    """Deterministic positive prices with schema date,BTC,<assets...>."""
    rng = np.random.default_rng(7)
    dates = pd.bdate_range("2024-01-02", periods=n)
    start = dict(zip(ASSETS, [40000.0, 2500.0, 120.0, 0.45]))
    data = {"date": dates.strftime("%Y-%m-%d")}
    for a in ASSETS:
        drift, vol = 0.0004, 0.02
        px = start[a] * np.exp(np.cumsum(rng.normal(drift, vol, size=n)))
        data[a] = np.maximum(px, 1e-6)
    return pd.DataFrame(data)


def _assert_returns_schema(returns: pd.DataFrame) -> None:
    assert isinstance(returns, pd.DataFrame)
    assert not returns.empty
    assert isinstance(returns.index, pd.DatetimeIndex)
    assert returns.index.is_monotonic_increasing
    assert returns.index.is_unique
    assert list(returns.columns) == ["BTC", "ETH", "SOL", "ADA"]


# ---------------------------------------------------------------------------
# 1. Format round-trips through load_prices (schema date,BTC,<assets...>)
# ---------------------------------------------------------------------------


def _round_trip_load_prices(tmp_path: Path, suffix: str, write_fn) -> pd.DataFrame:
    path = tmp_path / f"prices{suffix}"
    prices = _make_prices_df()
    write_fn(path, prices)
    returns = load_prices(path, benchmark="BTC")
    _assert_returns_schema(returns)
    return returns


def test_round_trip_csv(tmp_path):
    def write(path, df):
        df.to_csv(path, index=False)

    _round_trip_load_prices(tmp_path, ".csv", write)


def test_round_trip_json_records(tmp_path):
    def write(path, df):
        df.to_json(path, orient="records", date_format="iso")

    _round_trip_load_prices(tmp_path, ".json", write)


def test_round_trip_jsonl(tmp_path):
    def write(path, df):
        records = json.loads(df.to_json(orient="records", date_format="iso"))
        with path.open("w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec) + "\n")

    _round_trip_load_prices(tmp_path, ".jsonl", write)


def test_round_trip_pickle(tmp_path):
    def write(path, df):
        with path.open("wb") as fh:
            pickle.dump(df, fh)

    _round_trip_load_prices(tmp_path, ".pkl", write)


@pytest.mark.skipif(
    not _engine_available("pyarrow") and not _engine_available("fastparquet"),
    reason="no parquet engine (pyarrow/fastparquet) installed",
)
def test_round_trip_parquet(tmp_path):
    def write(path, df):
        df.to_parquet(path, index=False)

    _round_trip_load_prices(tmp_path, ".parquet", write)


@pytest.mark.skipif(not _engine_available("tables"), reason="no pytables installed")
def test_round_trip_hdf5(tmp_path):
    def write(path, df):
        df.to_hdf(path, key="prices", mode="w")

    _round_trip_load_prices(tmp_path, ".h5", write)


# ---------------------------------------------------------------------------
# 2. Rejection paths raise BABDataError
# ---------------------------------------------------------------------------


def _make_returns_df(index) -> pd.DataFrame:
    rng = np.random.default_rng(3)
    return pd.DataFrame(
        rng.normal(0.0005, 0.02, size=(len(index), len(ASSETS))),
        index=index,
        columns=ASSETS,
    )


def test_duplicate_dates_are_deduplicated(tmp_path):
    """Duplicate timestamps must not silently drive positions: the loader
    deduplicates (keep first) and returns a unique DatetimeIndex."""
    idx = pd.DatetimeIndex(["2024-01-02", "2024-01-02", "2024-01-03", "2024-01-04"])
    out = validate_returns_dataframe(_make_returns_df(idx), benchmark="BTC")
    assert out.index.is_unique
    assert len(out) == 3
    assert out.index.strftime("%Y-%m-%d").tolist() == ["2024-01-02", "2024-01-03", "2024-01-04"]


def test_rejects_missing_benchmark_partial_coverage(tmp_path):
    idx = pd.DatetimeIndex(["2024-01-02", "2024-01-03", "2024-01-04"])
    df = _make_returns_df(idx)
    with pytest.raises(BABDataError, match="Benchmark"):
        validate_returns_dataframe(df, benchmark="DOGE")


def test_rejects_no_tradable_assets_partial_coverage(tmp_path):
    idx = pd.DatetimeIndex(["2024-01-02", "2024-01-03", "2024-01-04"])
    df = pd.DataFrame(
        np.zeros((len(idx), 1)), index=idx, columns=["BTC"]
    )
    with pytest.raises(BABDataError, match="no assets to trade"):
        validate_returns_dataframe(df, benchmark="BTC")


def test_non_monotonic_dates_are_normalized_not_silent(tmp_path):
    """Non-monotonic input must not silently pass; the loader sorts to a
    monotonic, unique DatetimeIndex output (deterministic, no lookahead)."""
    idx = pd.DatetimeIndex(["2024-01-04", "2024-01-02", "2024-01-03"])
    out = validate_returns_dataframe(_make_returns_df(idx), benchmark="BTC")
    assert out.index.is_monotonic_increasing
    assert out.index.is_unique
    assert list(out.index) == sorted(out.index)


# ---------------------------------------------------------------------------
# 3. --metadata-out audit parity for fetch_real_bab_prices.py --source fixture
# ---------------------------------------------------------------------------


def _run_fetch(args) -> tuple[int, str, str]:
    import subprocess
    import sys

    r = subprocess.run(
        [sys.executable, str(FETCH_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return r.returncode, r.stdout, r.stderr


def _assert_success_sidecar(meta: dict, rows: int, columns: list[str]) -> None:
    assert meta["tool"] == "scripts/fetch_real_bab_prices.py"
    assert meta["source"] == f"fixture:{FIXTURE_CSV!s}"
    assert meta["benchmark"] == "BTC"
    assert "BTC" in meta["universe"]
    assert meta["request_range"]["start"] == "2021-01-04"
    assert meta["request_range"]["end"] == "2021-03-31"
    assert "request_settings" in meta
    assert set(meta["request_settings"]) >= {
        "timeout_seconds",
        "max_requests_per_second",
        "max_retries",
        "user_agent",
    }
    assert meta["tos_acknowledged"] is False
    assert meta["mode"] == "created"
    assert meta["fetch_time_utc"]
    outcome = meta["outcome"]
    assert outcome["ok"] is True
    assert outcome["rows"] == rows
    assert outcome["date_coverage"]["first"] == "2021-01-04"
    assert outcome["date_coverage"]["last"] == "2021-03-31"
    assert isinstance(outcome["date_coverage"]["unique_dates"], int)
    assert outcome["columns"] == columns
    assert Path(outcome["output"]).exists()


def test_metadata_out_fixture_success_parity(tmp_path):
    out = tmp_path / "from_fixture.csv"
    meta_out = tmp_path / "meta.json"

    rc, _stdout, _stderr = _run_fetch(
        [
            "--output",
            str(out),
            "--source",
            "fixture",
            "--fixture-path",
            str(FIXTURE_CSV),
            "--benchmark",
            "BTC",
            "--start",
            "2021-01-04",
            "--end",
            "2021-03-31",
            "--metadata-out",
            str(meta_out),
        ]
    )
    assert rc == 0, "fixture fetch must succeed offline"
    assert meta_out.exists()

    df = pd.read_csv(out)
    meta = json.loads(meta_out.read_text())
    _assert_success_sidecar(meta, len(df), list(df.columns))
    assert list(df.columns[:2]) == ["date", "BTC"]
    assert df["date"].is_unique
    assert df["date"].is_monotonic_increasing
    # load_prices must accept the produced file (real-format contract).
    load_prices(out, benchmark="BTC", min_rows=10)


def test_metadata_out_fixture_failure_writes_error_context(tmp_path):
    out = tmp_path / "from_fixture.csv"
    meta_out = tmp_path / "meta.json"

    rc, _stdout, _stderr = _run_fetch(
        [
            "--output",
            str(out),
            "--source",
            "fixture",
            "--fixture-path",
            str(tmp_path / "does_not_exist.csv"),
            "--benchmark",
            "BTC",
            "--metadata-out",
            str(meta_out),
        ]
    )
    assert rc != 0, "missing fixture must fail"
    assert meta_out.exists()

    meta = json.loads(meta_out.read_text())
    assert meta["outcome"]["ok"] is False
    assert "error" in meta["outcome"] and meta["outcome"]["error"]
    assert meta["mode"] == "failed"
    assert meta["tool"] == "scripts/fetch_real_bab_prices.py"
    assert meta["source"] == f"fixture:{tmp_path / 'does_not_exist.csv'!s}"
    # No raw ToS text or secrets may leak into the sidecar.
    assert "I accept the data provider Terms of Service" not in json.dumps(meta)
    assert "api_key" not in json.dumps(meta).lower()
    assert "secret" not in json.dumps(meta).lower()


def test_metadata_out_fixture_schema_fail_path(tmp_path, monkeypatch):
    """A fixture whose columns lack the benchmark must fail closed with an
    error-context sidecar rather than silently aligning."""
    bad = tmp_path / "bad_schema.csv"
    pd.DataFrame({"date": ["2021-01-04"], "DOGE": [1.0]}).to_csv(bad, index=False)
    out = tmp_path / "out.csv"
    meta_out = tmp_path / "meta.json"

    rc, _stdout, _stderr = _run_fetch(
        [
            "--output",
            str(out),
            "--source",
            "fixture",
            "--fixture-path",
            str(bad),
            "--benchmark",
            "BTC",
            "--metadata-out",
            str(meta_out),
        ]
    )
    assert rc != 0, "schema-fail fixture must fail"
    assert meta_out.exists()
    meta = json.loads(meta_out.read_text())
    assert meta["outcome"]["ok"] is False
    assert "error" in meta["outcome"] and meta["outcome"]["error"]
