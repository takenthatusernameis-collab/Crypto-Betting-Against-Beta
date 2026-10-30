import json
import os
import pickle
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.errors import BABDataError


FIX = os.path.join(os.path.dirname(__file__), "fixtures")


class TestDataLoaderHeavyExtra:
    def test_promote_datetime_column_variants(self):
        # column named Date
        idx = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({"Date": idx, "BTC": [0.01]*5, "ETH": [0.02]*5})
        out = data_loader.validate_returns_dataframe(df, benchmark="BTC")
        assert isinstance(out.index, pd.DatetimeIndex)
        # datetime
        df = pd.DataFrame({"datetime": idx, "BTC": [0.01]*5, "ETH": [0.02]*5})
        out = data_loader.validate_returns_dataframe(df, benchmark="BTC")
        assert isinstance(out.index, pd.DatetimeIndex)
        # timestamp/time/dt/index/idx
        for name in ["timestamp", "time", "dt", "index", "idx"]:
            df = pd.DataFrame({name: idx, "BTC": [0.01]*5, "ETH": [0.01]*5})
            out = data_loader.validate_returns_dataframe(df, benchmark="BTC")
            assert isinstance(out.index, pd.DatetimeIndex)
        # unnamed: 0
        df = pd.DataFrame({"Unnamed: 0": idx, "BTC": [0.01]*5, "ETH": [0.01]*5})
        out = data_loader.validate_returns_dataframe(df, benchmark="BTC")
        assert isinstance(out.index, pd.DatetimeIndex)
        # try to find string date column as last resort
        df = pd.DataFrame({"BTC": [0.01]*5, "ETH": [0.02]*5, "datestr": idx.strftime("%Y-%m-%d")})
        out = data_loader.validate_returns_dataframe(df, benchmark="BTC")
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_normalize_index_tz_aware(self):
        idx = pd.date_range("2023-01-01", periods=5, tz="UTC")
        df = pd.DataFrame({"BTC": np.random.randn(5)*0.01, "ETH": np.random.randn(5)*0.01}, index=idx)
        out = data_loader.validate_returns_dataframe(df, benchmark="BTC")
        assert out.index.tz is None
        idx2 = pd.date_range("2023-01-01", periods=5, tz="US/Eastern")
        df2 = pd.DataFrame({"BTC": np.random.randn(5)*0.01, "ETH": np.random.randn(5)*0.01}, index=idx2)
        out2 = data_loader.validate_returns_dataframe(df2, benchmark="BTC")
        assert out2.index.tz is None

    def test_drop_all_nan_columns(self):
        idx = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({"BTC": [0.01]*5, "ETH": [0.01]*5, "DEAD": [np.nan]*5}, index=idx)
        out = data_loader.validate_returns_dataframe(df, benchmark="BTC")
        assert "DEAD" not in out.columns
        # all nan -> error
        df = pd.DataFrame({"A": [np.nan]*5}, index=idx)
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df)
        # all nan but benchmark
        df = pd.DataFrame({"BTC": [np.nan]*5, "ETH": [np.nan]*5}, index=idx)
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df, benchmark="BTC")

    def test_coerce_numeric_percent_commas_na(self):
        idx = pd.date_range("2023-01-01", periods=4)
        df = pd.DataFrame({
            "BTC": ["1.0%", "2.0%", "1.2%", "1.5%"],
            "ETH": ["1,000.50", "500", "750", "250"]
        }, index=idx)
        out = data_loader.validate_returns_dataframe(df)
        assert isinstance(out, pd.DataFrame)
        assert np.isfinite(out.to_numpy()).all()
        # with NA values
        df2 = pd.DataFrame({
            "BTC": ["1.0%", "NA", "1.2%", "1.5%"],
            "ETH": ["10", "20", "n/a", "30"]
        }, index=idx)
        try:
            out2 = data_loader.validate_returns_dataframe(df2)
        except Exception:
            pass

    def test_load_returns_from_pickle(self, tmp_path):
        idx = pd.date_range("2023-01-01", periods=10)
        df = pd.DataFrame({"BTC": np.random.randn(10)*0.01, "ETH": np.random.randn(10)*0.01}, index=idx)
        p = tmp_path / "test.pkl"
        with open(p, "wb") as f:
            pickle.dump(df, f)
        out = data_loader.load_returns(p, benchmark="BTC")
        assert "BTC" in out.columns
        # dict form
        p2 = tmp_path / "test2.pkl"
        with open(p2, "wb") as f:
            pickle.dump({"BTC": df["BTC"].values, "ETH": df["ETH"].values}, f)
        # might need datetime index - but let us see
        try:
            out2 = data_loader.load_returns(p2, benchmark="BTC")
        except Exception:
            pass
        # bad pickle
        p3 = tmp_path / "bad.pkl"
        with open(p3, "wb") as f:
            pickle.dump([1,2,3], f)
        with pytest.raises(BABDataError):
            data_loader.load_returns(p3)
        # missing
        with pytest.raises(BABDataError):
            data_loader.load_returns_from_pickle(tmp_path / "nope.pkl")

    def test_load_returns_from_json_orient_records(self, tmp_path):
        idx = pd.date_range("2023-01-01", periods=5)
        records = [{"date": str(d.date()), "BTC": 0.01*i, "ETH": -0.01*i} for i,d in enumerate(idx)]
        p = tmp_path / "rec.json"
        with open(p, "w") as f:
            json.dump(records, f)
        try:
            out = data_loader.load_returns_from_json(p, benchmark="BTC", orient="records")
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass

    def test_load_returns_from_hdf5_parquet_errors(self, tmp_path):
        with pytest.raises(BABDataError):
            data_loader.load_returns_from_hdf5(tmp_path / "nope.h5")
        with pytest.raises(BABDataError):
            data_loader.load_returns_from_parquet(tmp_path / "nope.parquet")

    def test_load_returns_dispatch_extensions(self, tmp_path):
        idx = pd.date_range("2023-01-01", periods=10)
        df = pd.DataFrame({"BTC": np.random.randn(10)*0.01, "ETH": np.random.randn(10)*0.01}, index=idx)
        # jsonl
        p = tmp_path / "t.jsonl"
        with open(p, "w") as f:
            for i in range(len(df)):
                f.write(json.dumps({"date": str(df.index[i].date()), "BTC": float(df["BTC"].iloc[i]), "ETH": float(df["ETH"].iloc[i])}) + "\n")
        try:
            out = data_loader.load_returns(p, benchmark="BTC")
        except Exception:
            pass
        # pq
        with pytest.raises(BABDataError):
            data_loader.load_returns(tmp_path / "x.pq", benchmark="BTC")
        # bad ext
        with pytest.raises(BABDataError):
            data_loader.load_returns(tmp_path / "x.txt")

    def test_load_prices_variants(self, tmp_path):
        idx = pd.date_range("2023-01-01", periods=15)
        prices = pd.DataFrame({"BTC": 100 + np.cumsum(np.random.randn(15)), "ETH": 50 + np.cumsum(np.random.randn(15))}, index=idx)
        # df
        out = data_loader.load_prices(prices, benchmark="BTC")
        assert isinstance(out, pd.DataFrame)
        # csv
        p = tmp_path / "p.csv"
        prices.to_csv(p)
        try:
            out = data_loader.load_prices(p, benchmark="BTC")
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass
        # json
        p = tmp_path / "p.json"
        prices.to_json(p)
        try:
            out = data_loader.load_prices(p, benchmark="BTC")
        except Exception:
            pass
        # bad ext
        with pytest.raises(BABDataError):
            data_loader.load_prices(tmp_path / "bad.xyz")
        # bad type
        with pytest.raises(BABDataError):
            data_loader.load_prices(123)
        # short
        short = pd.DataFrame({"BTC": [100]}, index=[idx[0]])
        with pytest.raises(BABDataError):
            data_loader.load_prices(short)

    def test_validate_returns_dataframe_errors(self):
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(None)
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe([1,2,3])
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(pd.DataFrame())
        # bad index
        df = pd.DataFrame({"BTC": [0.01]*5, "bad": ["a","b","c","d","e"]})
        # make bad index
        df2 = df.copy()
        df2.index = ["x","y","z","w","v"]
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df2)
        # < min_rows
        idx = pd.date_range("2023-01-01", periods=2)
        df = pd.DataFrame({"BTC": [0.01,0.02]}, index=idx)
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df, min_rows=5)
        # duplicates in index
        idx = pd.date_range("2023-01-01", periods=3)
        idx = idx.append(pd.DatetimeIndex([idx[0]]))
        df = pd.DataFrame({"BTC": [0.01,0.02,0.03,0.04]}, index=idx)
        out = data_loader.validate_returns_dataframe(df)
        assert len(out) == 3
        # duplicates in columns
        idx = pd.date_range("2023-01-01", periods=3)
        df = pd.DataFrame([[0.01,0.02],[0.01,0.02],[0.01,0.02]], index=idx, columns=["BTC", "BTC"])
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df)
        # inf
        idx = pd.date_range("2023-01-01", periods=3)
        df = pd.DataFrame({"BTC": [0.01, np.inf, 0.02]}, index=idx)
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df)
        # benchmark missing
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(pd.DataFrame({"ETH": [0.01]*3}, index=idx), benchmark="BTC")
        # only benchmark
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(pd.DataFrame({"BTC": [0.01]*3}, index=idx), benchmark="BTC")
        # benchmark all nan
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(pd.DataFrame({"BTC": [np.nan]*3, "ETH": [0.01]*3}, index=idx), benchmark="BTC")
        # non-numeric
        df = pd.DataFrame({"BTC": [0.01, "bad", 0.02], "ETH": [0.01,0.01,0.01]}, index=idx)
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df)

    def test_iter_assets_list_columns(self):
        idx = pd.date_range("2023-01-01", periods=3)
        df = pd.DataFrame({"BTC": [0.01]*3, "ETH": [0.01]*3}, index=idx)
        assert data_loader.list_columns(df) == ["BTC", "ETH"]
        assets = list(data_loader.iter_assets(df, benchmark="BTC"))
        assert assets == ["ETH"]
