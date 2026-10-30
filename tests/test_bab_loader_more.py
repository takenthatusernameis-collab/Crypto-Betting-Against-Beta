import numpy as np
import pandas as pd
import pytest
from pathlib import Path

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.errors import BABDataError


class TestLoaderMore:
    def test_normalize_index_duplicates(self):
        idx = pd.DatetimeIndex([pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-01')])
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=idx)
        out = data_loader._normalize_index(df)
        assert isinstance(out, pd.DataFrame)

    def test_promote_datetime_column_name_match(self):
        df = pd.DataFrame({"Date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out, pd.DataFrame)

    def test_coerce_numeric_percent_european(self):
        df = pd.DataFrame({"BTC": ["1,5%"]})  # comma decimal style? rare
        try:
            out = data_loader._coerce_numeric(df)
        except Exception:
            pass

    def test_coerce_numeric_object_mixed(self):
        df = pd.DataFrame({"BTC": [0.01, "0.02", " 0.03% "]})
        out = data_loader._coerce_numeric(df)
        assert len(out) == 3

    def test_drop_all_nan_cols(self):
        df = pd.DataFrame({"BTC": [0.01, 0.02], "ETH": [np.nan, np.nan]})
        out = data_loader._drop_all_nan_columns(df)
        assert "ETH" not in out.columns

    def test_load_prices_csv_to_returns(self):
        import tempfile, os
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        f.write('date,BTC,ETH\n2023-01-01,100,50\n2023-01-02,101,51\n2023-01-03,102,50\n')
        f.close()
        try:
            out = data_loader.load_prices(f.name)
            assert isinstance(out, pd.DataFrame)
        finally:
            os.unlink(f.name)

    def test_load_returns_from_json(self):
        import tempfile, os, json
        data = [{"date": "2023-01-01", "BTC": 0.01}, {"date": "2023-01-02", "BTC": 0.02}]
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(data, f)
        f.close()
        try:
            out = data_loader.load_returns_from_json(f.name)
            assert isinstance(out, pd.DataFrame)
        finally:
            os.unlink(f.name)

    def test_load_returns_from_parquet_fake(self):
        try:
            data_loader.load_returns_from_parquet('/no/such/file.parquet')
        except Exception:
            pass

    def test_prices_to_returns_short(self):
        df = pd.DataFrame({"BTC": [100]})
        with pytest.raises(BABDataError):
            data_loader._prices_to_returns(df)

    def test_prices_to_returns_inf(self):
        df = pd.DataFrame({"BTC": [100, 0, 101]})
        out = data_loader._prices_to_returns(df)
        assert isinstance(out, pd.DataFrame)
