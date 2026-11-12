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


def test_cli_output_path_relative_no_parent_dir(tmp_path, monkeypatch):
    # branches 50->58 and 59->67: parent is "." so mkdir and os.access are skipped
    monkeypatch.chdir(tmp_path)
    out = tmp_path / "rel_out.json"
    rc = main(["--synthetic", "--output", "rel_out.json", "--benchmark", "BTC"])
    assert rc == 0
    assert out.exists()


def test_cli_output_path_is_directory(tmp_path):
    rc = main(["--synthetic", "--output", str(tmp_path), "--benchmark", "BTC"])
    assert rc == 1


def test_cli_extract_cumulative_no_matching_column():
    # branch 370->369: DataFrame with columns but no 'cumulative'/'cum' col falls through
    from strategies.betting_against_beta.cli import _extract_cumulative

    class FakeDF:
        columns = ["returns", "weights"]
        iloc = None  # hasattr is True, but no col matches so __getitem__ never called

        def __getitem__(self, key):
            raise AssertionError("should not reach __getitem__")

    class FakeResult:
        backtest = FakeDF()

    # A DataFrame whose last-cell access fails must surface instead of
    # falling through and returning the whole object.
    with pytest.raises(AttributeError):
        _extract_cumulative(FakeResult())


def test_cli_extract_cumulative_series_cum_name_raises():
    # lines 381-382: Series whose name contains 'cum' but iloc[-1] raises -> falls through
    from strategies.betting_against_beta.cli import _extract_cumulative

    class BadSeries:
        name = "cumulative"
        iloc = None

        def __getitem__(self, key):
            raise IndexError("boom")

        def __len__(self):
            return 5  # must be > 0 to skip the empty early-return at line 359

    # A cum-named Series whose iloc[-1] fails must surface instead of falling
    # through and returning the raw object.
    class FakeResult:
        backtest = BadSeries()

    with pytest.raises(TypeError):
        _extract_cumulative(FakeResult())
