"""CLI tests for `strategies/betting_against_beta/cli.py`."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.cli import main


def _make_returns(tmp_path, n_days=200, seed=7):
    rng = np.random.RandomState(seed)
    dates = pd.date_range("2023-01-01", periods=n_days)
    df = pd.DataFrame(
        {
            "BTC": rng.normal(0.0, 0.01, n_days),
            "ETH": rng.normal(0.0, 0.015, n_days),
            "SOL": rng.normal(0.0, 0.02, n_days),
        },
        index=dates,
    )
    p = tmp_path / "rets.csv"
    df.to_csv(p)
    return p


def _make_prices(tmp_path, n_days=200, seed=7):
    rng = np.random.RandomState(seed)
    dates = pd.date_range("2023-01-01", periods=n_days)
    base = 100.0 + np.cumsum(rng.normal(0.0, 1.0, n_days))
    df = pd.DataFrame(
        {
            "BTC": base,
            "ETH": base * 0.8 + rng.normal(0.0, 0.5, n_days),
            "SOL": base * 0.5 + rng.normal(0.0, 0.3, n_days),
        },
        index=dates,
    )
    p = tmp_path / "prices.csv"
    df.to_csv(p)
    return p


def test_cli_main_synthetic_defaults(tmp_path):
    out = tmp_path / "out.json"
    rc = main(["--synthetic", "--output", str(out), "--benchmark", "BTC"])
    assert rc == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert set(data) == {"final_cumulative", "periods", "benchmark", "universe"}
    assert data["benchmark"] == "BTC"
    assert isinstance(data["periods"], int) and data["periods"] > 0
    assert isinstance(data["final_cumulative"], float)


def test_cli_main_csv_input(tmp_path):
    data_path = _make_returns(tmp_path)
    out = tmp_path / "out.json"
    rc = main(["--data", str(data_path), "--output", str(out)])
    assert rc == 0
    data = json.loads(out.read_text())
    assert data["benchmark"] == "BTC"
    assert data["periods"] > 0


def test_cli_main_custom_universe_and_quantiles(tmp_path):
    data_path = _make_returns(tmp_path)
    rc = main(
        [
            "--data",
            str(data_path),
            "--benchmark",
            "ETH",
            "--universe",
            "BTC",
            "SOL",
            "--long-quantile",
            "0.2",
            "--short-quantile",
            "0.2",
            "--transaction-costs",
            "0.001",
            "--slippage",
            "0.0005",
        ]
    )
    assert rc == 0


def test_cli_main_no_output_flag(tmp_path):
    data_path = _make_returns(tmp_path)
    rc = main(["--data", str(data_path)])
    assert rc == 0


def test_cli_main_weekly_rebalance(tmp_path):
    data_path = _make_returns(tmp_path)
    rc = main(["--data", str(data_path), "--rebalance-freq", "weekly"])
    assert rc == 0


def test_cli_main_returns_df_path_none_uses_synthetic(tmp_path):
    # --data omitted => synthetic path (args.data is None)
    rc = main([])
    assert rc == 0


def test_cli_from_prices_real_prices_path(tmp_path):
    prices_path = _make_prices(tmp_path)
    rc = main(["--data", str(prices_path), "--from-prices", "--benchmark", "BTC"])
    assert rc == 0


def test_cli_from_prices_missing_file(tmp_path):
    missing = tmp_path / "does_not_exist.csv"
    rc = main(["--data", str(missing), "--from-prices", "--benchmark", "BTC"])
    assert rc == 1


def test_cli_from_prices_benchmark_mismatch(tmp_path):
    prices_path = _make_prices(tmp_path)
    rc = main(["--data", str(prices_path), "--from-prices", "--benchmark", "NOTPRESENT"])
    assert rc == 1


def test_cli_help_output_snapshot(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "Betting Against Beta" in captured.out
    assert "--from-prices" in captured.out
    assert "--dry-run" in captured.out
    assert "--version" in captured.out


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "bab 0.1.0" in captured.out


def test_cli_dry_run_synthetic(tmp_path):
    out = tmp_path / "out.json"
    rc = main(["--dry-run", "--synthetic", "--benchmark", "BTC"])
    assert rc == 0
    assert not out.exists()


def test_cli_dry_run_valid_prices(tmp_path):
    prices_path = _make_prices(tmp_path)
    rc = main(["--dry-run", "--data", str(prices_path), "--from-prices", "--benchmark", "BTC"])
    assert rc == 0


def test_cli_dry_run_invalid_data(tmp_path):
    missing = tmp_path / "nope.csv"
    rc = main(["--dry-run", "--data", str(missing), "--benchmark", "BTC"])
    assert rc == 1
