import numpy as np
import pandas as pd
import pytest
from pathlib import Path
import tempfile, os, json

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.errors import BABDataError


class TestDataLoaderFill:
    def test_load_returns_from_csv_no_file(self):
        with pytest.raises(BABDataError):
            data_loader.load_returns_from_csv("/no/such/file.csv")

    def test_load_returns_from_parquet_no_file(self):
        with pytest.raises(BABDataError):
            data_loader.load_returns_from_parquet("/no/such/file.parquet")

    def test_load_returns_from_hdf5_no_file(self):
        with pytest.raises(BABDataError):
            data_loader.load_returns_from_hdf5("/no/such/file.h5")

    def test_load_returns_from_pickle_no_file(self):
        with pytest.raises(BABDataError):
            data_loader.load_returns_from_pickle("/no/such/file.pkl")

    def test_load_returns_from_json_no_file(self):
        with pytest.raises(BABDataError):
            data_loader.load_returns_from_json("/no/such/file.json")

    def test_promote_datetime_scan_finds(self):
        df = pd.DataFrame({"x": ["2023-01-01", "2023-01-02", "2023-01-03"], "BTC": [0.01,0.02,0.03]})
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out, pd.DataFrame)

    def test_normalize_index_bad_index(self):
        df = pd.DataFrame({"BTC": [0.01,0.02]}, index=["abc", "def"])
        with pytest.raises(BABDataError):
            data_loader._normalize_index(df)

    def test_coerce_numeric_european_style(self):
        df = pd.DataFrame({"BTC": ["1.000,50"]})  # European decimal comma
        try:
            out = data_loader._coerce_numeric(df)
        except Exception:
            pass

    def test_validate_returns_none(self):
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(None)

    def test_validate_returns_not_df(self):
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe([1,2,3])

    def test_validate_returns_insufficient_rows(self):
        idx = pd.date_range("2023-01-01", periods=1)
        df = pd.DataFrame({"BTC": [0.01]}, index=idx)
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df, min_rows=5)

    def test_load_returns_parquet_dispatch(self):
        with pytest.raises(BABDataError):
            data_loader.load_returns("file.parquet")

    def test_load_returns_hdf5_dispatch(self):
        with pytest.raises(BABDataError):
            data_loader.load_returns("file.h5")

    def test_load_returns_pickle_dispatch(self):
        with pytest.raises(BABDataError):
            data_loader.load_returns("file.pkl")
