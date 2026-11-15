"""P14 coverage campaign for ``data_loader.py``.

Targets the missed branches listed in HANDOFF.md P14-A:
dayfirst/unparseable index -> ``BABDataError``; NaT/None/inf scalar coercion;
exchange-format fallback; empty asset token; all-NaN columns; parseable-series
pending count; quality campaign finite/stale branches; finite-count fallback;
freshness reference/tz fallbacks.

Only temp files / fakes are used. No network, no credentials.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _coerce_to_datetime_scalar,
    _detect_and_normalize_exchange_format,
    _drop_all_nan_columns,
    _max_consecutive_equal_finite,
    _max_consecutive_equal_finite_frame,
    _normalize_asset_name,
    _normalize_index,
    _promote_datetime_column,
    _run_data_quality_campaign,
    _series_is_parseable,
    _strip_units_and_parse,
    load_prices,
    load_returns,
    validate_freshness,
)


def _tmp_csv(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / name
    p.write_text(text)
    return p


def _make_df(index, **cols) -> pd.DataFrame:
    df = pd.DataFrame(cols)
    df.index = index
    return df


# ---------------------------------------------------------------------------
# NaT / None / inf scalar coercion (_coerce_to_datetime_scalar)
# ---------------------------------------------------------------------------
def test_coerce_scalar_nat_raises():
    with pytest.raises(ValueError):
        _coerce_to_datetime_scalar(pd.NaT)


def test_coerce_scalar_none_raises():
    with pytest.raises(ValueError):
        _coerce_to_datetime_scalar(None)


def test_coerce_scalar_nan_raises():
    with pytest.raises(ValueError):
        _coerce_to_datetime_scalar(float("nan"))


def test_coerce_scalar_inf_raises():
    with pytest.raises(ValueError):
        _coerce_to_datetime_scalar(float("inf"))


def test_coerce_scalar_nan_string_raises():
    with pytest.raises(ValueError):
        _coerce_to_datetime_scalar("nan")


def test_coerce_scalar_empty_string_raises():
    with pytest.raises(ValueError):
        _coerce_to_datetime_scalar("")


def test_coerce_scalar_valid_epoch_string():
    out = _coerce_to_datetime_scalar("1609459200")
    assert isinstance(out, pd.Timestamp)


# ---------------------------------------------------------------------------
# _normalize_index: dayfirst and unparseable -> BABDataError
# ---------------------------------------------------------------------------
def test_normalize_index_unparseable_raises():
    df = _make_df(["not-a-date", "also-not-a-date"], a=[1.0, 2.0])
    with pytest.raises(BABDataError):
        _normalize_index(df)


def test_normalize_index_dayfirst_branch():
    # 13 cannot be a month; forces the dayfirst fallback path.
    df = _make_df(pd.Index(["13/01/2021", "14/02/2021"]), a=[1.0, 2.0])
    out = _normalize_index(df)
    assert isinstance(out.index, pd.DatetimeIndex)


# ---------------------------------------------------------------------------
# Exchange format fallback (_detect_and_normalize_exchange_format)
# ---------------------------------------------------------------------------
def test_exchange_format_fallback_no_price_key(tmp_path):
    # Close key missing -> fallback path (lines 697-698 / 749-750).
    df = pd.DataFrame(
        {"timestamp": pd.date_range("2021-01-01", periods=3, freq="D"), "last": [1.0, 2.0, 3.0]}
    )
    out = _detect_and_normalize_exchange_format(df.copy())
    assert isinstance(out, pd.DataFrame)


def test_exchange_format_unparseable_index_returns_original():
    df = pd.DataFrame({"date": ["x", "y", "z"], "close": [1.0, 2.0, 3.0]})
    out = _detect_and_normalize_exchange_format(df.copy())
    assert isinstance(out, pd.DataFrame)


# ---------------------------------------------------------------------------
# _promote_datetime_column fallback (line 868-869)
# ---------------------------------------------------------------------------
def test_promote_datetime_column_exception_path():
    df = pd.DataFrame(
        {"date": pd.to_datetime(["2021-01-01", "2021-01-02"]), "close": [1.0, 2.0]}
    )
    out = _promote_datetime_column(df.copy())
    assert isinstance(out, pd.DataFrame)


# ---------------------------------------------------------------------------
# _normalize_asset_name: empty token (line 1032)
# ---------------------------------------------------------------------------
def test_normalize_asset_name_empty_token():
    # Repeated separators exercise the token-skip branch (line 1032).
    assert _normalize_asset_name("BTC--USDT") == "BTC"


# ---------------------------------------------------------------------------
# _drop_all_nan_columns: all-NaN -> BABDataError (line 1268)
# ---------------------------------------------------------------------------
def test_drop_all_nan_columns_raises():
    df = pd.DataFrame({"a": [np.nan, np.nan], "b": [np.nan, np.nan]})
    with pytest.raises(BABDataError):
        _drop_all_nan_columns(df)


# ---------------------------------------------------------------------------
# _series_is_parseable: pending-count short-circuit (line 1391)
# ---------------------------------------------------------------------------
def test_series_is_parseable_pending_short_false():
    # Non-parseable cells with too few parseable cells -> False.
    assert _series_is_parseable(pd.Series(["a", "b", "c"])) is False


def test_series_is_parseable_pending_true():
    s = pd.Series(["1.0", "2.0", "3.0", np.nan])
    assert _series_is_parseable(s) is True


# ---------------------------------------------------------------------------
# _run_data_quality_campaign: fast path + finite/stale branches
# ---------------------------------------------------------------------------
def test_quality_campaign_fast_path_finite_all():
    df = pd.DataFrame(
        {"a": [1.0, 2.0, 3.0, 4.0], "b": [5.0, 6.0, 7.0, 8.0]},
        index=pd.date_range("2021-01-01", periods=4, freq="D"),
    )
    out = _run_data_quality_campaign(df, min_finite_fraction=0.5)
    assert len(out) == 4


def test_quality_campaign_insufficient_finite_raises():
    df = pd.DataFrame(
        {"a": [1.0, np.nan, np.nan, np.nan], "b": [5.0, 6.0, 7.0, 8.0]},
        index=pd.date_range("2021-01-01", periods=4, freq="D"),
    )
    with pytest.raises(BABDataError):
        _run_data_quality_campaign(df, min_finite_fraction=0.75)


def test_quality_campaign_stale_run_raises():
    # Long run of identical finite values trips the stale-run check.
    df = pd.DataFrame(
        {"a": [1.0] * 60, "b": list(range(60))},
        index=pd.date_range("2021-01-01", periods=60, freq="D"),
    )
    with pytest.raises(BABDataError):
        _run_data_quality_campaign(df, stale_run_threshold=3, min_finite_fraction=0.0)


def test_max_consecutive_equal_finite_frame():
    arr = np.array([1.0, 1.0, 2.0, 2.0, 2.0, 3.0])
    assert _max_consecutive_equal_finite_frame(arr) == 3


# ---------------------------------------------------------------------------
# finite-count fallback (lines 1958-1959)
# ---------------------------------------------------------------------------
def test_finite_count_fallback_path():
    # Non-numeric frame forces the per-column apply fallback.
    df = pd.DataFrame(
        {"a": ["1.0", "2.0", "3.0"], "b": ["4.0", "5.0", "6.0"]},
        index=pd.date_range("2021-01-01", periods=3, freq="D"),
    )
    out = _run_data_quality_campaign(df, min_finite_fraction=0.0)
    assert len(out) == 3


# ---------------------------------------------------------------------------
# validate_freshness: reference / tz fallbacks
# ---------------------------------------------------------------------------
def test_validate_freshness_reference_parse_fallback():
    # reference_date that raises TypeError/ValueError -> now() fallback (2742-2743).
    df = pd.DataFrame(
        {"a": [1.0, 2.0]}, index=pd.date_range("2026-01-01", periods=2, freq="D")
    )
    assert validate_freshness(df, max_staleness_days=1000.0, reference_date="not-a-date") is True


def test_validate_freshness_tz_convert_none_branch():
    # tz-aware reference triggers tz_convert(None) (line 2747).
    df = pd.DataFrame(
        {"a": [1.0, 2.0]}, index=pd.date_range("2026-01-01", periods=2, freq="D")
    )
    ref = pd.Timestamp("2026-01-05", tz="UTC")
    assert validate_freshness(df, max_staleness_days=1000.0, reference_date=ref) is True


def test_validate_freshness_last_date_tz_branch():
    # tz-aware last_date triggers the tz_convert branch (lines 2756-2757).
    df = pd.DataFrame(
        {"a": [1.0, 2.0]},
        index=pd.DatetimeIndex(["2026-01-01", "2026-01-02"]).tz_localize("UTC"),
    )
    assert validate_freshness(df, max_staleness_days=1000.0) is True


def test_validate_freshness_recent_passes():
    df = pd.DataFrame(
        {"a": [1.0, 2.0]}, index=pd.date_range("2026-01-01", periods=2, freq="D")
    )
    assert validate_freshness(df, max_staleness_days=1000.0, reference_date="2026-01-02") is True


# ---------------------------------------------------------------------------
# load_returns dispatch guards
# ---------------------------------------------------------------------------
def test_load_returns_none_raises():
    with pytest.raises(BABDataError):
        load_returns(None)


def test_load_returns_missing_file_raises(tmp_path):
    with pytest.raises(BABDataError):
        load_returns(tmp_path / "does_not_exist.csv")


def test_load_returns_directory_raises(tmp_path):
    d = tmp_path / "adir"
    d.mkdir()
    with pytest.raises(BABDataError):
        load_returns(d)


def test_load_returns_unsupported_extension_raises(tmp_path):
    p = _tmp_csv(tmp_path, "weird.xyz", "a,b\n1,2\n")
    with pytest.raises(BABDataError):
        load_returns(p)


def test_load_prices_all_nan_column_dropped(tmp_path):
    p = _tmp_csv(
        tmp_path,
        "prices.csv",
        "date,BTC,ETH,SOL\n2021-01-01,100,,50\n2021-01-02,101,,51\n2021-01-03,102,,52\n",
    )
    out = load_prices(p, benchmark="BTC")
    assert "ETH" not in out.columns
    assert "SOL" in out.columns


def test_strip_units_and_parse_percent_and_comma():
    assert _strip_units_and_parse("1,000.5") == 1000.5
    assert _strip_units_and_parse("2%") == 0.02
    assert math.isnan(_strip_units_and_parse("n/a"))


def test_validate_freshness_empty_returns_true():
    assert validate_freshness(pd.DataFrame()) is True


def test_validate_freshness_none_returns_true():
    assert validate_freshness(None) is True
