"""Unit tests for the BAB data loader and validation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    iter_assets,
    list_columns,
    load_returns,
    load_returns_from_csv,
    load_returns_from_dataframe,
    load_returns_from_hdf5,
    load_returns_from_json,
    load_returns_from_parquet,
    load_returns_from_pickle,
    validate_returns_dataframe,
)


def _valid_df(rows: int = 30, benchmark: str = "BTC", assets=("ETH", "SOL")) -> pd.DataFrame:
    idx = pd.date_range("2023-01-01", periods=rows, freq="D")
    data = {benchmark: np.random.default_rng(1).normal(0, 0.01, rows)}
    for a in assets:
        data[a] = np.random.default_rng(2).normal(0, 0.01, rows)
    return pd.DataFrame(data, index=idx)


class TestValidateReturnsDataFrame:
    def test_valid_df_passes(self):
        df = _valid_df()
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert isinstance(out, pd.DataFrame)
        assert len(out) == len(df)

    def test_none_raises(self):
        with pytest.raises(BABDataError):
            validate_returns_dataframe(None)

    def test_non_dataframe_raises(self):
        with pytest.raises(BABDataError):
            validate_returns_dataframe([1, 2, 3])  # type: ignore[arg-type]

    def test_empty_raises(self):
        with pytest.raises(BABDataError):
            validate_returns_dataframe(pd.DataFrame())

    def test_string_index_normalized(self):
        df = _valid_df()
        df.index = [d.strftime("%Y-%m-%d") for d in df.index]
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_unsorted_index_sorted(self):
        df = _valid_df()
        df = df.iloc[::-1]
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert out.index.equals(out.index.sort_values())

    def test_duplicate_columns_raise(self):
        df = _valid_df()
        df.columns = ["BTC", "ETH", "ETH"]
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")

    def test_non_numeric_raises(self):
        df = _valid_df()
        # Build an object-dtyped column with a string in it so the validator's
        # numeric coercion path actually sees the bad value.
        bad_col = df["BTC"].astype(object)
        bad_col.iloc[0] = "abc"
        df["BTC"] = bad_col
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")

    def test_inf_raises(self):
        df = _valid_df()
        df.iloc[0, 0] = np.inf
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")

    def test_missing_benchmark_raises(self):
        df = _valid_df()
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="MISSING")

    def test_only_benchmark_raises(self):
        df = pd.DataFrame({"BTC": np.random.default_rng(3).normal(0, 0.01, 30)},
                          index=pd.date_range("2023-01-01", periods=30, freq="D"))
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")

    def test_min_rows_enforced(self):
        df = _valid_df(rows=5)
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC", min_rows=10)


class TestLoaders:
    def test_load_returns_from_csv(self, tmp_path: Path):
        df = _valid_df()
        path = tmp_path / "returns.csv"
        df.to_csv(path)
        out = load_returns_from_csv(path, benchmark="BTC")
        assert "BTC" in out.columns
        assert "ETH" in out.columns

    def test_load_returns_from_csv_missing_file(self, tmp_path: Path):
        with pytest.raises(BABDataError):
            load_returns_from_csv(tmp_path / "nope.csv", benchmark="BTC")

    def test_load_returns_from_csv_bad_data(self, tmp_path: Path):
        path = tmp_path / "bad.csv"
        path.write_text("BTC,ETH\nabc,def\n1,2\n")
        with pytest.raises(BABDataError):
            load_returns_from_csv(path, benchmark="BTC")

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("pyarrow")
        and not __import__("importlib").util.find_spec("fastparquet"),
        reason="pyarrow or fastparquet required for parquet tests",
    )
    def test_load_returns_from_parquet_happy_path(self, tmp_path: Path):
        df = _valid_df()
        path = tmp_path / "returns.parquet"
        df.to_parquet(path)
        out = load_returns_from_parquet(path, benchmark="BTC")
        assert "BTC" in out.columns
        assert "ETH" in out.columns
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_load_returns_from_parquet_missing_file(self, tmp_path: Path):
        with pytest.raises(BABDataError):
            load_returns_from_parquet(tmp_path / "nope.parquet", benchmark="BTC")

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("pyarrow")
        and not __import__("importlib").util.find_spec("fastparquet"),
        reason="pyarrow or fastparquet required for parquet tests",
    )
    def test_load_returns_from_parquet_bad_schema_raises(self, tmp_path: Path):
        # Write parquet that loads but fails validation (non-numeric in bad form)
        path = tmp_path / "bad.parquet"
        bad = pd.DataFrame({"BTC": ["a", "b"], "ETH": [1, 2]}, index=pd.date_range("2023-01-01", periods=2, freq="D"))
        try:
            bad.to_parquet(path)
        except Exception:
            pytest.skip("Cannot write parquet for bad schema test")
        with pytest.raises(BABDataError):
            load_returns_from_parquet(path, benchmark="BTC")

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("tables"),
        reason="tables (PyTables) required for hdf5 tests",
    )
    def test_load_returns_from_hdf5_happy_path(self, tmp_path: Path):
        df = _valid_df()
        path = tmp_path / "returns.h5"
        try:
            df.to_hdf(path, key="returns", mode="w")
        except Exception:
            pytest.skip("Cannot write hdf5")
        out = load_returns_from_hdf5(path, benchmark="BTC", key="returns")
        assert "BTC" in out.columns
        assert "ETH" in out.columns
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_load_returns_from_hdf5_missing_file(self, tmp_path: Path):
        with pytest.raises(BABDataError):
            load_returns_from_hdf5(tmp_path / "nope.h5", benchmark="BTC")

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("tables"),
        reason="tables (PyTables) required for hdf5 tests",
    )
    def test_load_returns_from_hdf5_bad_schema_raises(self, tmp_path: Path):
        path = tmp_path / "bad.h5"
        bad = pd.DataFrame({"BTC": ["a", "b"], "ETH": [1, 2]}, index=pd.date_range("2023-01-01", periods=2, freq="D"))
        try:
            bad.to_hdf(path, key="returns", mode="w")
        except Exception:
            pytest.skip("Cannot write hdf5 for bad schema test")
        with pytest.raises(BABDataError):
            load_returns_from_hdf5(path, benchmark="BTC", key="returns")

    def test_load_returns_from_pickle_happy_path(self, tmp_path: Path):
        df = _valid_df()
        path = tmp_path / "returns.pkl"
        df.to_pickle(path)
        out = load_returns_from_pickle(path, benchmark="BTC")
        assert "BTC" in out.columns
        assert "ETH" in out.columns

    def test_load_returns_from_pickle_missing_file(self, tmp_path: Path):
        with pytest.raises(BABDataError):
            load_returns_from_pickle(tmp_path / "nope.pkl", benchmark="BTC")

    def test_load_returns_from_pickle_bad_schema_raises(self, tmp_path: Path):
        path = tmp_path / "bad.pkl"
        bad = pd.DataFrame({"BTC": ["a", "b"], "ETH": [1, 2]}, index=pd.date_range("2023-01-01", periods=2, freq="D"))
        bad.to_pickle(path)
        with pytest.raises(BABDataError):
            load_returns_from_pickle(path, benchmark="BTC")

    def test_load_returns_from_pickle_dict(self, tmp_path: Path):
        df = _valid_df()
        path = tmp_path / "returns_dict.pkl"
        with open(path, "wb") as f:
            import pickle

            pickle.dump({col: df[col].values for col in df.columns}, f)
        # dict without index - index may be parsed; but easier to also include index
        path2 = tmp_path / "returns_dict2.pkl"
        payload = {col: list(df[col].values) for col in df.columns}
        payload["index"] = [d.strftime("%Y-%m-%d") for d in df.index]
        with open(path2, "wb") as f:
            import pickle

            pickle.dump(payload, f)
        out = load_returns_from_pickle(path2, benchmark="BTC")
        assert "BTC" in out.columns

    def test_load_returns_from_json(self, tmp_path: Path):
        df = _valid_df()
        path = tmp_path / "returns.json"
        # object-of-arrays form
        payload = {col: list(df[col].values) for col in df.columns}
        payload["index"] = [d.strftime("%Y-%m-%d") for d in df.index]
        path.write_text(json.dumps(payload))
        out = load_returns_from_json(path, benchmark="BTC")
        assert "BTC" in out.columns
        assert len(out) == len(df)

    def test_load_returns_from_json_missing_file(self, tmp_path: Path):
        with pytest.raises(BABDataError):
            load_returns_from_json(tmp_path / "nope.json", benchmark="BTC")

    def test_load_returns_from_dataframe(self):
        df = _valid_df()
        out = load_returns_from_dataframe(df, benchmark="BTC")
        assert len(out) == len(df)

    def test_load_returns_dispatch_csv(self, tmp_path: Path):
        df = _valid_df()
        path = tmp_path / "returns.csv"
        df.to_csv(path)
        out = load_returns(path, benchmark="BTC")
        assert "BTC" in out.columns

    def test_load_returns_dispatch_parquet(self, tmp_path: Path):
        if not __import__("importlib").util.find_spec("pyarrow") and not __import__("importlib").util.find_spec("fastparquet"):
            pytest.skip("no parquet engine")
        df = _valid_df()
        path = tmp_path / "returns.parquet"
        df.to_parquet(path)
        out = load_returns(path, benchmark="BTC")
        assert "BTC" in out.columns

    def test_load_returns_dispatch_hdf5(self, tmp_path: Path):
        if not __import__("importlib").util.find_spec("tables"):
            pytest.skip("no hdf5 engine")
        df = _valid_df()
        path = tmp_path / "returns.h5"
        try:
            df.to_hdf(path, key="returns", mode="w")
        except Exception:
            pytest.skip("cannot write hdf5")
        out = load_returns(path, benchmark="BTC", key="returns")
        assert "BTC" in out.columns

    def test_load_returns_dispatch_pickle(self, tmp_path: Path):
        df = _valid_df()
        path = tmp_path / "returns.pkl"
        df.to_pickle(path)
        out = load_returns(path, benchmark="BTC")
        assert "BTC" in out.columns

    def test_load_returns_dispatch_dataframe(self):
        df = _valid_df()
        out = load_returns(df, benchmark="BTC")
        assert len(out) == len(df)

    def test_load_returns_unsupported_extension(self, tmp_path: Path):
        with pytest.raises(BABDataError):
            load_returns(tmp_path / "file.txt", benchmark="BTC")


class TestHelpers:
    def test_list_columns_sorted(self):
        df = _valid_df()
        cols = list_columns(df)
        assert cols == sorted(df.columns)

    def test_iter_assets_excludes_benchmark(self):
        df = _valid_df()
        assets = list(iter_assets(df, benchmark="BTC"))
        assert "BTC" not in assets
        assert "ETH" in assets


class TestIntegrationWithStrategy:
    """End-to-end: feed a CSV through the strategy and ensure it runs."""

    def test_strategy_runs_on_csv(self, tmp_path: Path):
        from strategies.betting_against_beta import BABConfig, BABStrategy

        df = _valid_df(rows=120, benchmark="BTC", assets=("ETH", "SOL", "BNB", "XRP"))
        path = tmp_path / "returns.csv"
        df.to_csv(path)

        cfg = BABConfig(
            benchmark="BTC",
            beta_window=60,
            min_observations=30,
            data_source=str(path),
        )
        strategy = BABStrategy(cfg)
        result = strategy.run()
        assert "returns" in result.backtest.columns
        assert "cumulative" in result.backtest.columns
        assert len(result.backtest) == len(df)
        # Universe should be derived from the CSV columns.
        assert set(strategy.config.universe) == set(df.columns)

    def test_strategy_runs_on_dataframe(self):
        from strategies.betting_against_beta import BABConfig, BABStrategy

        df = _valid_df(rows=120, benchmark="BTC", assets=("ETH", "SOL", "BNB"))
        cfg = BABConfig(benchmark="BTC", beta_window=60, min_observations=30)
        strategy = BABStrategy(cfg)
        result = strategy.run(returns_df=df)
        assert len(result.backtest) == len(df)

    def test_strategy_invalid_data_raises(self):
        from strategies.betting_against_beta import BABConfig, BABStrategy

        bad = pd.DataFrame({"BTC": ["a", "b"]}, index=[0, 1])
        cfg = BABConfig(benchmark="BTC")
        strategy = BABStrategy(cfg)
        with pytest.raises(BABDataError):
            strategy.run(returns_df=bad)


class TestAllNanColumnDropping:
    """Delisted/untradable assets (all-NaN columns) must be dropped
    deterministically rather than letting NaNs propagate into betas."""

    def test_all_nan_column_is_dropped(self):
        idx = pd.date_range("2023-01-01", periods=10, freq="D")
        df = pd.DataFrame(
            {
                "BTC": np.random.default_rng(1).normal(0, 0.01, 10),
                "ETH": np.random.default_rng(2).normal(0, 0.01, 10),
                "DEL": [np.nan] * 10,
            },
            index=idx,
        )
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert "DEL" not in out.columns
        assert "BTC" in out.columns
        assert "ETH" in out.columns

    def test_all_columns_nan_raises(self):
        idx = pd.date_range("2023-01-01", periods=10, freq="D")
        df = pd.DataFrame(
            {"BTC": [np.nan] * 10, "ETH": [np.nan] * 10}, index=idx
        )
        with pytest.raises(BABDataError):
            validate_returns_dataframe(df, benchmark="BTC")

    def test_mixed_nan_and_finite_kept(self):
        idx = pd.date_range("2023-01-01", periods=10, freq="D")
        df = pd.DataFrame(
            {
                "BTC": np.random.default_rng(1).normal(0, 0.01, 10),
                "ETH": [np.nan] * 5 + list(np.random.default_rng(2).normal(0, 0.01, 5)),
            },
            index=idx,
        )
        out = validate_returns_dataframe(df, benchmark="BTC")
        assert "ETH" in out.columns  # partially-NaN column is not all-NaN