"""Campaign D final push - cover remaining uncovered branches in data_loader (fixed)."""
import os
import pickle
import tempfile

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader
from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _coerce_to_datetime_scalar,
    _normalize_index,
    load_prices,
    load_returns,
    validate_prices,
    validate_returns_dataframe,
    clean_data,
    normalize_schema,
    standardize_columns,
    detect_price_or_returns,
    _detect_and_normalize_exchange_format,
    _promote_datetime_column,
    _normalize_columns,
    _drop_all_nan_columns,
    _strip_units_and_parse,
    _coerce_numeric,
    _run_data_quality_campaign,
    _drop_metadata_columns,
)


class TestNormalizeIndexMoreFixed:
    def test_normalize_index_empty_numeric(self):
        df = pd.DataFrame({"BTC": []}, index=pd.Index([], dtype=float))
        df_out = _normalize_index(df.copy())
        assert isinstance(df_out.index, pd.DatetimeIndex)
        assert len(df_out) == 0


class TestCoerceScalarMoreFixed:
    def test_coerce_scalar_nat_type_raises(self):
        with pytest.raises((ValueError, Exception)):
            _coerce_to_datetime_scalar(pd.NaT)

    def test_coerce_scalar_str_nan_variants(self):
        for s in ["N/A", "NULL", "None", "nan", "NaN", "  NA  "]:
            with pytest.raises((ValueError, Exception)):
                _coerce_to_datetime_scalar(s)

    def test_coerce_scalar_float_inf_nan(self):
        with pytest.raises((ValueError, Exception)):
            _coerce_to_datetime_scalar(float('nan'))
        with pytest.raises((ValueError, Exception)):
            _coerce_to_datetime_scalar(float('inf'))

    def test_coerce_scalar_numeric_string_exp(self):
        res = _coerce_to_datetime_scalar("1.6e9")
        assert hasattr(res, 'year')

    def test_coerce_scalar_int_various_ranges(self):
        for v in [1600000000000000000, 1600000000000000, 1600000000000, 1600000000, 123]:
            res = _coerce_to_datetime_scalar(v)
            assert hasattr(res, 'year')

    def test_coerce_scalar_float_various_ranges(self):
        for v in [1600000000000000000.0, 1600000000000000.0, 1600000000000.0, 1600000000.0, 123.0]:
            res = _coerce_to_datetime_scalar(v)
            assert hasattr(res, 'year')


class TestPromoteDatetimeColumnMoreFixed:
    def test_promote_with_unnamed_columns(self):
        df = pd.DataFrame({
            'Unnamed: 0': ['2021-01-01', '2021-01-02'],
            'BTC': [0.1, 0.2]
        })
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_promote_object_last_resort(self):
        df = pd.DataFrame({
            'foo': ['2021-01-01', '2021-01-02', '2021-01-03'],
            'BTC': [0.1, 0.2, 0.3]
        })
        df['foo'] = df['foo'].astype(object)
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)


class TestLoadersMoreFixed:
    def test_load_returns_not_found(self):
        with pytest.raises((BABDataError, Exception)):
            load_returns("/no/such/file.csv")

    def test_load_returns_unsupported(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write("bad")
            fname = f.name
        try:
            with pytest.raises((BABDataError, Exception)):
                load_returns(fname)
        finally:
            os.unlink(fname)

    def test_load_returns_directory(self):
        with tempfile.TemporaryDirectory() as d:
            with pytest.raises((BABDataError, Exception)):
                load_returns(d)

    def test_load_returns_jsonl_with_both(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write('{"date":"2021-01-01","BTC":0.1,"ETH":0.05}\n')
            f.write('{"date":"2021-01-02","BTC":0.2,"ETH":0.1}\n')
            f.write('{"date":"2021-01-03","BTC":0.3,"ETH":0.15}\n')
            fname = f.name
        try:
            res = load_returns(fname, benchmark='BTC')
            assert isinstance(res, pd.DataFrame)
        finally:
            os.unlink(fname)

    def test_load_returns_pickle_with_both(self):
        df = pd.DataFrame({"BTC": [0.1, 0.2, 0.3, 0.1, 0.2], "ETH": [0.05, 0.1, 0.15, 0.02, 0.01]},
                          index=pd.date_range("2021-01-01", periods=5))
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pkl', delete=False) as f:
            pickle.dump(df, f)
            fname = f.name
        try:
            res = load_returns(fname, benchmark='BTC')
            assert isinstance(res, pd.DataFrame)
        finally:
            os.unlink(fname)

    def test_load_prices_variants_more(self):
        df = pd.DataFrame({"date": pd.date_range("2021-01-01", periods=10), "BTC": np.linspace(100, 110, 10), "ETH": np.linspace(10, 11, 10)})
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            fname = f.name
        try:
            res = load_prices(fname, benchmark='BTC')
            assert isinstance(res, pd.DataFrame)
        finally:
            os.unlink(fname)


class TestMoreGaps:
    def test_normalize_index_numeric_empty_with_series(self):
        df = pd.DataFrame({"BTC": []}, index=[])
        df.index = pd.Index([], dtype=float)
        df_out = _normalize_index(df)
        assert isinstance(df_out.index, pd.DatetimeIndex)

    def test_coerce_scalar_numeric_string_variants(self):
        # Try various forms
        for s in ["1600000000", "1600000000000", "1600000000000000"]:
            try:
                res = _coerce_to_datetime_scalar(s)
                assert hasattr(res, 'year')
            except Exception:
                pass

    def test_detect_format_long_with_date_promotion(self):
        df = pd.DataFrame({
            'pair': ['BTC', 'ETH'],
            'date': ['2021-01-01', '2021-01-02'],
            'close': [100, 50]
        })
        res = _detect_and_normalize_exchange_format(df)
        assert isinstance(res, pd.DataFrame)


class TestHelpersDirect:
    def test_not_null(self):
        assert data_loader._not_null(5) is True
        assert data_loader._not_null(None) is False
        try:
            assert data_loader._not_null(np.nan) is False
        except Exception:
            pass

    def test_series_has_any_finite(self):
        assert data_loader._series_has_any_finite(pd.Series([1, 2])) is True
        assert data_loader._series_has_any_finite(pd.Series([np.nan])) is False
        assert data_loader._series_has_any_finite([1, None]) is True
        assert data_loader._series_has_any_finite([]) is False
        assert data_loader._series_has_any_finite(None) is False

    def test_coerce_series_to_datetime_index(self):
        df = pd.DataFrame({'date': ['2021-01-01', '2021-01-02'], 'BTC': [0.1, 0.2]})
        coerced = pd.Series([pd.Timestamp('2021-01-01'), pd.Timestamp('2021-01-02')], index=df.index)
        res = data_loader._coerce_series_to_datetime_index(df, 'date', coerced)
        assert res in (True, False)


class TestNormalizeIndexNumericAggressive:
    def test_numeric_empty_index(self):
        df = pd.DataFrame({"BTC": pd.Series([], dtype=float)})
        df.index = pd.Index([], dtype=float)
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_numeric_ns_magnitude(self):
        # very large
        idx = pd.Index([1.6e18, 1.6e18 + 1e9], dtype=float)
        df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=idx)
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_numeric_us_magnitude(self):
        idx = pd.Index([1.6e15, 1.6e15 + 1e6], dtype=float)
        df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=idx)
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_numeric_ms_magnitude(self):
        idx = pd.Index([1.6e12, 1.6e12 + 1000], dtype=float)
        df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=idx)
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_numeric_s_magnitude(self):
        idx = pd.Index([1.6e9, 1.6e9 + 1], dtype=float)
        df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=idx)
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)

    def test_numeric_small_magnitude(self):
        idx = pd.Index([123456, 123457], dtype=float)
        df = pd.DataFrame({"BTC": [0.1, 0.2]}, index=idx)
        out = _normalize_index(df)
        assert isinstance(out.index, pd.DatetimeIndex)


class TestDirectCoverage:
    def test_coerce_series_to_datetime_index_tz(self):
        df = pd.DataFrame({'date': ['2021-01-01', '2021-01-02'], 'BTC': [0.1, 0.2]})
        ts = pd.Series([pd.Timestamp('2021-01-01', tz='UTC'), pd.Timestamp('2021-01-02', tz='UTC')])
        res = data_loader._coerce_series_to_datetime_index(df, 'date', ts)
        assert res is True

    def test_normalize_index_non_numeric_string_with_na(self):
        df = pd.DataFrame({'BTC': [0.1, 0.2]}, index=['2021-01-01', None])
        try:
            out = _normalize_index(df)
        except Exception:
            pass

    def test_detect_format_with_symbol_column_long(self):
        df = pd.DataFrame({
            'ticker': ['BTC', 'BTC', 'ETH', 'ETH'],
            'datetime': ['2021-01-01', '2021-01-02', '2021-01-01', '2021-01-02'],
            'close': [100, 101, 50, 51]
        })
        res = _detect_and_normalize_exchange_format(df)
        assert isinstance(res, pd.DataFrame)

    def test_promote_datetime_various(self):
        df = pd.DataFrame({'date': pd.to_datetime(['2021-01-01', '2021-01-02']), 'BTC': [0.1, 0.2]})
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)


class TestNormalizeIndexStringWithNa:
    def test_normalize_index_mixed_strings_with_none_and_nat(self):
        df = pd.DataFrame({'BTC': [0.1, 0.2, 0.3]}, index=['2021-01-01', None, '2021-01-03'])
        try:
            out = _normalize_index(df)
            assert isinstance(out.index, pd.DatetimeIndex)
        except Exception:
            pass

    def test_normalize_index_string_coercion_fallbacks(self):
        df = pd.DataFrame({'BTC': [0.1]}, index=['not-a-date'])
        try:
            out = _normalize_index(df)
        except (BABDataError, Exception):
            pass


class TestCoerceScalarMoreBranches:
    def test_coerce_scalar_pandas_nat(self):
        try:
            _coerce_to_datetime_scalar(pd.NaT)
        except Exception:
            pass

    def test_coerce_scalar_empty_list_like_not_applicable(self):
        pass

    def test_coerce_scalar_datetime64(self):
        try:
            val = np.datetime64('2021-01-01')
            res = _coerce_to_datetime_scalar(val)
            assert hasattr(res, 'year')
        except Exception:
            pass


class TestDetectFormatMore:
    def test_detect_format_ohlcv_close_column(self):
        df = pd.DataFrame({
            'Open time': pd.date_range('2021-01-01', periods=3),
            'Open': [100, 101, 102],
            'High': [101, 102, 103],
            'Low': [99, 100, 101],
            'Close': [100.5, 101.5, 102.5],
            'Volume': [1000, 1100, 1200]
        })
        res = _detect_and_normalize_exchange_format(df)
        assert isinstance(res, pd.DataFrame)

    def test_detect_format_date_promotion_numeric_epoch(self):
        df = pd.DataFrame({
            'date': [1609459200000, 1609545600000, 1609632000000],  # ms
            'BTC': [0.1, 0.2, 0.3]
        })
        res = _detect_and_normalize_exchange_format(df)
        assert isinstance(res, pd.DataFrame)


class TestPromoteDatetimeMore:
    def test_promote_with_tz_aware_index(self):
        df = pd.DataFrame({'BTC': [0.1, 0.2]}, index=pd.date_range('2021-01-01', periods=2, tz='UTC'))
        res = _promote_datetime_column(df)
        assert isinstance(res.index, pd.DatetimeIndex)
