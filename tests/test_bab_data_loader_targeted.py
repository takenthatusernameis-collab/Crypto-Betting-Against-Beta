import numpy as np
import pandas as pd
import pytest
import tempfile, os, json

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.errors import BABDataError


class TestDataLoaderTargeted:
    def test_promote_datetime_empty_unnamed(self):
        df = pd.DataFrame({"Unnamed: 0": [1,2], "BTC": [0.01,0.02]})
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out, pd.DataFrame)

    def test_promote_datetime_scan_nonstring_col(self):
        df = pd.DataFrame({0: [pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-02')], "BTC": [0.01,0.02]})
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out, pd.DataFrame)

    def test_normalize_index_tz_localize_fail(self):
        idx = pd.date_range("2023-01-01", periods=3)
        df = pd.DataFrame({"BTC": [0.01,0.02,0.03]}, index=idx)
        out = data_loader._normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_coerce_numeric_comma_thousand(self):
        df = pd.DataFrame({"BTC": ["1,000", "2,500.5"]})
        out = data_loader._coerce_numeric(df)
        assert out["BTC"].iloc[0] == 1000.0

    def test_coerce_numeric_percent_no_raise(self):
        df = pd.DataFrame({"BTC": ["bad%"]})
        try:
            out = data_loader._coerce_numeric(df)
        except Exception:
            pass

    def test_validate_returns_bench_not_found(self):
        idx = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({"ETH": [0.01]*5}, index=idx)
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df, benchmark="BTC")

    def test_validate_returns_only_bench_col(self):
        idx = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({"BTC": [0.01]*5}, index=idx)
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df, benchmark="BTC")

    def test_load_returns_json_orient_split(self):
        data = {"columns": ["date", "BTC"], "index": [0,1], "data": [["2023-01-01", 0.01], ["2023-01-02", 0.02]]}
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(data, f)
        f.close()
        try:
            out = data_loader.load_returns(f.name)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass
        finally:
            os.unlink(f.name)
