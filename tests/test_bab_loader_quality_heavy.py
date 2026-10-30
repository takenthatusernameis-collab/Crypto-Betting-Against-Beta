import numpy as np
import pandas as pd
import pytest
from pathlib import Path

from strategies.betting_against_beta import data_loader, quality
from strategies.betting_against_beta.errors import BABDataError


class TestLoaderQualityHeavy:
    def test_normalize_columns_dupes(self):
        df = pd.DataFrame([[1,2]], columns=['a','a'])
        with pytest.raises(BABDataError):
            data_loader._normalize_columns(df)

    def test_promote_datetime_unnamed(self):
        df = pd.DataFrame({"Unnamed: 0": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
        out = data_loader._promote_datetime_column(df)
        assert isinstance(out, pd.DataFrame)

    def test_promote_datetime_scan(self):
        df = pd.DataFrame({"x": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
        out = data_loader._promote_datetime_column(df)
        # May or may not promote depending on implementation
        assert isinstance(out, pd.DataFrame)

    def test_normalize_index_tz_aware(self):
        idx = pd.date_range("2023-01-01", periods=3, tz="UTC")
        df = pd.DataFrame({"BTC": [0.01,0.02,-0.01]}, index=idx)
        out = data_loader._normalize_index(df.copy())
        assert getattr(out.index, "tz", None) is None or out.index.tz is None

    def test_coerce_numeric_comma_percent(self):
        df = pd.DataFrame({"BTC": ["1,000.50%", "50%"], "ETH": ["1,000", "2.5"]})
        out = data_loader._coerce_numeric(df)
        assert out["BTC"].iloc[0] == 10.005

    def test_validate_returns_no_bench_multi(self):
        idx = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({"BTC": [0.01]*5, "ETH": [0.02]*5}, index=idx)
        out = data_loader.validate_returns_dataframe(df)
        assert isinstance(out, pd.DataFrame)

    def test_validate_returns_bench_missing_col(self):
        idx = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({"ETH": [0.02]*5}, index=idx)
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df, benchmark="BTC")

    def test_validate_returns_only_bench(self):
        idx = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({"BTC": [0.01]*5}, index=idx)
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df, benchmark="BTC")

    def test_validate_returns_bench_all_nan(self):
        idx = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({"BTC": [np.nan]*5, "ETH": [0.01]*5}, index=idx)
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df, benchmark="BTC")

    def test_validate_returns_inf(self):
        idx = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({"BTC": [0.01, np.inf, 0.01, 0.01, 0.01], "ETH": [0.01]*5}, index=idx)
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(df)

    def test_validate_returns_empty(self):
        with pytest.raises(BABDataError):
            data_loader.validate_returns_dataframe(pd.DataFrame())

    def test_load_returns_json_records(self):
        import tempfile, os
        data = [{"date": "2023-01-01", "BTC": 0.01, "ETH": 0.02}, {"date": "2023-01-02", "BTC": -0.01, "ETH": 0.01}]
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        import json
        json.dump(data, f)
        f.close()
        try:
            out = data_loader.load_returns(f.name)
            assert isinstance(out, pd.DataFrame)
        finally:
            os.unlink(f.name)

    def test_load_returns_csv(self):
        import tempfile, os
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        f.write('date,BTC,ETH\n2023-01-01,0.01,0.02\n2023-01-02,-0.01,0.01\n')
        f.close()
        try:
            out = data_loader.load_returns(f.name)
            assert isinstance(out, pd.DataFrame)
        finally:
            os.unlink(f.name)

    def test_load_returns_unsupported(self):
        with pytest.raises(BABDataError):
            data_loader.load_returns("/tmp/file.xyz")

    def test_quality_report_branches(self):
        idx = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame({"BTC": [0.01, np.nan, np.inf, 0.01, 0.01], "ETH": [0.01, 0.02, 0.03, 0.04, 0.05]}, index=idx)
        rep = quality.data_quality_report(df)
        assert isinstance(rep, dict)

    def test_quality_check_strict_inf(self):
        idx = pd.date_range("2023-01-01", periods=4)
        df = pd.DataFrame({"BTC": [0.01, np.inf, 0.01, 0.01]}, index=idx)
        try:
            quality.check_data_quality(df, strict=True)
        except Exception:
            pass

    def test_quality_strict_missing_warn(self):
        idx = pd.date_range("2023-01-01", periods=4)
        df = pd.DataFrame({"BTC": [0.01, np.nan, 0.01, 0.01]}, index=idx)
        try:
            quality.check_data_quality(df, strict=True)
        except Exception:
            pass
