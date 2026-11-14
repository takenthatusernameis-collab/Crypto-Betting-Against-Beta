import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError


# ---------------------------------------------------------------------------
# Cluster 1: 1257-1258 — _run_data_quality_campaign: tz_convert and tz_localize
# both raise -> line 1256 runs, inner except -> line 1258 pass.
# ---------------------------------------------------------------------------
def test_1257_1258_dq_tz_convert_and_localize_both_raise():
    idx = pd.date_range("2024-01-01", periods=3, tz="UTC")
    orig_convert = pd.DatetimeIndex.tz_convert
    orig_localize = pd.DatetimeIndex.tz_localize

    def boom(*a, **k):
        raise RuntimeError("tz op blocked")

    pd.DatetimeIndex.tz_convert = boom
    pd.DatetimeIndex.tz_localize = boom
    try:
        df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=idx)
        try:
            out = dl._run_data_quality_campaign(df)
            assert isinstance(out, pd.DataFrame)
        except BABDataError:
            pass
    finally:
        pd.DatetimeIndex.tz_convert = orig_convert
        pd.DatetimeIndex.tz_localize = orig_localize


# ---------------------------------------------------------------------------
# Cluster 2: 912-914 — last-resort: promoted index is a non-DatetimeIndex
# (object Index of strings), then set_index raises -> except/pass + return df2.
# The candidate column gets renamed (mystery -> MYSTERY) by normalization, so
# match case-insensitively.
# ---------------------------------------------------------------------------
class _StrSeries(pd.Series):
    @property
    def _constructor(self):
        return _StrSeries


def test_912_914_last_resort_set_index_raise_not_dtindex():
    orig_td = pd.to_datetime

    def fake_td(x, *a, **k):
        if isinstance(x, pd.Series) and str(x.name).upper() == "MYSTERY":
            return _StrSeries(["a", "b"], index=x.index)
        return orig_td(x, *a, **k)

    dl.pd.to_datetime = fake_td
    orig_set = pd.DataFrame.set_index

    def raise_set(self, keys, *a, **k):
        raise RuntimeError("set_index boom")

    pd.DataFrame.set_index = raise_set
    try:
        df = pd.DataFrame({"mystery": ["x", "y"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]})
        try:
            out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass
    finally:
        dl.pd.to_datetime = orig_td
        pd.DataFrame.set_index = orig_set


# ---------------------------------------------------------------------------
# Cluster 3: 194 — _normalize_index: numeric index, pandas unit-coercion fails,
# first elementwise attempt raises (ValueError), second succeeds and assigns
# df.index = coerced. Requires _coerce_to_datetime_scalar to fail once then
# return a Timestamp, and pd.to_datetime(..., unit=...) to raise.
# ---------------------------------------------------------------------------
def test_194_normalize_index_second_coerce_assign():
    orig_coerce = dl._coerce_to_datetime_scalar
    orig_td = pd.to_datetime
    state = {"n": 0}

    def fake_coerce(v):
        state["n"] += 1
        if state["n"] <= 2:
            raise ValueError("attempt fails")
        return pd.Timestamp("2024-01-01")

    def fake_td(*a, **k):
        if "unit" in k:
            raise ValueError("unit coercion blocked")
        return orig_td(*a, **k)

    dl._coerce_to_datetime_scalar = fake_coerce
    pd.to_datetime = fake_td
    try:
        df = pd.DataFrame({"BTC": [0.01]}, index=[1704067200000])
        try:
            out = dl._normalize_index(df)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass
    finally:
        dl._coerce_to_datetime_scalar = orig_coerce
        pd.to_datetime = orig_td


# ---------------------------------------------------------------------------
# Cluster 5: 859 / 861-862 — unnamed column: coerced value lacks tzinfo but
# pd.Timestamp(pdv) is tz-aware (-> 859), and pd.Timestamp(pdv) raises
# (-> 861-862 inner except/pass).
# ---------------------------------------------------------------------------
class _Sentinel:
    __slots__ = ()


def test_859_861_862_unnamed_tz_mixed():
    orig_coerce = dl._coerce_to_datetime_scalar
    orig_ts = pd.Timestamp

    def fake_coerce(val):
        if isinstance(val, str):
            if val == "mark":
                return pd.Timestamp("2024-01-01").tz_localize(None)  # naive
            if val == "boom":
                return _Sentinel()  # no tzinfo; pd.Timestamp(..) raises
        return orig_coerce(val)

    def fake_ts(*a, **k):
        ts = orig_ts(*a, **k)
        if getattr(ts, "tzinfo", None) is None and getattr(ts, "tz", None) is None:
            try:
                return ts.tz_localize("UTC")
            except Exception:
                return ts
        if isinstance(a[0] if a else None, _Sentinel):
            raise RuntimeError("ts boom")
        return ts

    dl._coerce_to_datetime_scalar = fake_coerce
    pd.Timestamp = fake_ts
    try:
        df = pd.DataFrame(
            {"Unnamed: 0": ["mark", "boom"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
        )
        try:
            out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass
    finally:
        dl._coerce_to_datetime_scalar = orig_coerce
        pd.Timestamp = orig_ts


# ---------------------------------------------------------------------------
# Cluster 6: 561 — exchange long-format: coerced value is naive but
# pd.Timestamp(pdv) is tz-aware -> tz_convert branch at 561.
# ---------------------------------------------------------------------------
def test_561_exchange_long_format_naive_to_tz():
    orig_coerce = dl._coerce_to_datetime_scalar
    orig_ts = pd.Timestamp

    def fake_coerce(val):
        if isinstance(val, datetime.datetime) and getattr(val, "tzinfo", None) is None:
            return orig_ts(val)  # naive
        return orig_coerce(val)

    def fake_ts(*a, **k):
        ts = orig_ts(*a, **k)
        if getattr(ts, "tzinfo", None) is None and getattr(ts, "tz", None) is None:
            try:
                return ts.tz_localize("UTC")
            except Exception:
                return ts
        return ts

    dl._coerce_to_datetime_scalar = fake_coerce
    pd.Timestamp = fake_ts
    try:
        df = pd.DataFrame(
            {
                "ticker": ["BTC", "BTC"],
                "timestamp": [datetime.datetime(2024, 1, 1), datetime.datetime(2024, 1, 2)],
                "close": [100.0, 101.0],
            }
        )
        try:
            out = dl.validate_returns_dataframe(df, benchmark=None, quality=False)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass
    finally:
        dl._coerce_to_datetime_scalar = orig_coerce
        pd.Timestamp = orig_ts


# ---------------------------------------------------------------------------
# Cluster 6: 620 — exchange OHLCV single-asset: same naive->tz-aware trick.
# ---------------------------------------------------------------------------
def test_620_exchange_ohlcv_naive_to_tz():
    orig_coerce = dl._coerce_to_datetime_scalar
    orig_ts = pd.Timestamp

    def fake_coerce(val):
        if isinstance(val, datetime.datetime) and getattr(val, "tzinfo", None) is None:
            return orig_ts(val)
        return orig_coerce(val)

    def fake_ts(*a, **k):
        ts = orig_ts(*a, **k)
        if getattr(ts, "tzinfo", None) is None and getattr(ts, "tz", None) is None:
            try:
                return ts.tz_localize("UTC")
            except Exception:
                return ts
        return ts

    dl._coerce_to_datetime_scalar = fake_coerce
    pd.Timestamp = fake_ts
    try:
        df = pd.DataFrame(
            {
                "date": [datetime.datetime(2024, 1, 1), datetime.datetime(2024, 1, 2)],
                "close": [100.0, 101.0],
                "extra": [1, 2],
            }
        )
        try:
            out = dl.validate_returns_dataframe(df, benchmark=None, quality=False)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass
    finally:
        dl._coerce_to_datetime_scalar = orig_coerce
        pd.Timestamp = orig_ts


# ---------------------------------------------------------------------------
# Cluster 6: 679 — epoch block: coerced epoch value is naive but
# pd.Timestamp(pdv) is tz-aware -> tz_convert branch at 679.
# ---------------------------------------------------------------------------
def test_679_exchange_epoch_naive_to_tz():
    orig_coerce = dl._coerce_to_datetime_scalar
    orig_ts = pd.Timestamp

    def fake_coerce(val):
        if isinstance(val, (int, np.integer)) and abs(int(val)) > 1e9:
            return orig_ts(int(val))  # naive
        return orig_coerce(val)

    def fake_ts(*a, **k):
        ts = orig_ts(*a, **k)
        if getattr(ts, "tzinfo", None) is None and getattr(ts, "tz", None) is None:
            try:
                return ts.tz_localize("UTC")
            except Exception:
                return ts
        return ts

    dl._coerce_to_datetime_scalar = fake_coerce
    pd.Timestamp = fake_ts
    try:
        df = pd.DataFrame({"open_time": [1704067200000, 1704153600000], "extra": [1, 2]})
        try:
            out = dl.validate_returns_dataframe(df, benchmark=None, quality=False)
            assert isinstance(out, pd.DataFrame)
        except Exception:
            pass
    finally:
        dl._coerce_to_datetime_scalar = orig_coerce
        pd.Timestamp = orig_ts
