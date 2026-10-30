"""Offline edge-case tests for BAB return-data normalization and loaders."""

from __future__ import annotations

import pickle

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _coerce_numeric,
    _drop_all_nan_columns,
    _normalize_index,
    _promote_datetime_column,
    load_returns_from_hdf5,
    load_returns_from_parquet,
    load_returns_from_pickle,
    validate_returns_dataframe,
)


def _valid_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {"BTC": [0.01, 0.02, 0.03], "ETH": [0.02, 0.01, 0.04]},
        index=pd.date_range("2026-01-01", periods=3, freq="D"),
    )


def test_timezone_normalization_sorts_and_deduplicates_in_utc():
    frame = pd.DataFrame(
        {"BTC": [0.02, 0.01, 0.03], "ETH": [0.01, 0.02, 0.04]},
        index=pd.DatetimeIndex(
            [
                "2026-01-02T00:00:00+02:00",
                "2026-01-01T22:00:00+00:00",
                "2026-01-03T00:00:00+02:00",
            ]
        ),
    )

    normalized = _normalize_index(frame)

    assert normalized.index.tz is None
    assert normalized.index.is_monotonic_increasing
    assert not normalized.index.has_duplicates
    assert len(normalized) == 2


def test_duplicate_column_names_after_whitespace_normalization_raise():
    frame = _valid_frame()
    frame.columns = ["BTC", " ETH "]
    frame["ETH"] = frame.pop(" ETH ")

    duplicated = pd.concat([frame, frame.iloc[:, [1]]], axis=1)
    duplicated.columns = ["BTC", " ETH ", "ETH"]

    with pytest.raises(BABDataError, match="Duplicate column names"):
        validate_returns_dataframe(duplicated)


def test_unparseable_index_is_wrapped_as_bab_data_error():
    frame = pd.DataFrame({"BTC": [0.01, 0.02], "ETH": [0.02, 0.03]}, index=["bad-a", "bad-b"])

    with pytest.raises(BABDataError, match="Index could not be parsed"):
        validate_returns_dataframe(frame)


def test_datetime_promotion_keeps_unparseable_unnamed_column_for_validation():
    frame = pd.DataFrame(
        {
            "": ["not-a-date", "still-not-a-date"],
            "BTC": [0.01, 0.02],
            "ETH": [0.02, 0.03],
        }
    )

    promoted = _promote_datetime_column(frame.copy())

    assert "" in promoted.columns
    assert not isinstance(promoted.index, pd.DatetimeIndex)


def test_numeric_coercion_rejects_unrecognized_text():
    frame = pd.DataFrame({"BTC": ["0.01", "not-a-return"]})

    with pytest.raises(BABDataError, match="Non-numeric values"):
        _coerce_numeric(frame)


def test_corrupt_pickle_is_reported_as_bab_data_error(tmp_path):
    path = tmp_path / "corrupt.pkl"
    path.write_bytes(b"not a pickle payload")

    with pytest.raises(BABDataError, match="Failed to read pickle"):
        load_returns_from_pickle(path)


def test_drop_all_nan_columns_keeps_non_numeric_uncoercible_column():
    frame = pd.DataFrame({"BTC": [0.01, 0.02], "RAW": [["x"], ["y"]]})

    result = _drop_all_nan_columns(frame)

    assert list(result.columns) == ["BTC", "RAW"]


def test_coerce_numeric_handles_thousands_and_percent_text():
    frame = pd.DataFrame(
        {"BTC": ["1,000.50%", "2,000.00%"], "ETH": ["1.5%", "2.5%"]}
    )

    result = _coerce_numeric(frame)

    assert result.loc[0, "BTC"] == pytest.approx(10.005)
    assert result.loc[1, "BTC"] == pytest.approx(20.0)
    assert result.loc[0, "ETH"] == pytest.approx(0.015)


def test_validation_rejects_benchmark_only_frame():
    frame = pd.DataFrame(
        {"BTC": [0.01, 0.02]},
        index=pd.date_range("2026-01-01", periods=2, freq="D"),
    )

    with pytest.raises(BABDataError, match="no assets to trade"):
        validate_returns_dataframe(frame, benchmark="BTC")


def test_validation_rejects_benchmark_without_finite_values():
    frame = pd.DataFrame(
        {"BTC": [np.nan, np.nan], "ETH": [0.01, 0.02]},
        index=pd.date_range("2026-01-01", periods=2, freq="D"),
    )

    with pytest.raises(BABDataError, match="no finite return values"):
        validate_returns_dataframe(frame, benchmark="BTC")


def test_parquet_loader_validates_successful_read(tmp_path, monkeypatch):
    path = tmp_path / "returns.parquet"
    path.touch()
    expected = _valid_frame()
    monkeypatch.setattr(pd, "read_parquet", lambda _path, **_kwargs: expected.copy())

    result = load_returns_from_parquet(path, benchmark="BTC")

    assert list(result.columns) == ["BTC", "ETH"]
    assert len(result) == 3


def test_hdf_loader_passes_requested_key_and_validates_result(tmp_path, monkeypatch):
    path = tmp_path / "returns.h5"
    path.touch()
    calls = {}

    def fake_read_hdf(_path, key=None, **_kwargs):
        calls["key"] = key
        return _valid_frame()

    monkeypatch.setattr(pd, "read_hdf", fake_read_hdf)

    result = load_returns_from_hdf5(path, benchmark="BTC", key="prices")

    assert calls["key"] == "prices"
    assert result.shape == (3, 2)


def test_pickle_loader_accepts_dictionary_payload(tmp_path):
    path = tmp_path / "returns.pkl"
    with path.open("wb") as handle:
        pickle.dump(
            {
                "date": ["2026-01-01", "2026-01-02", "2026-01-03"],
                "BTC": [0.01, 0.02, 0.03],
                "ETH": [0.02, 0.01, 0.04],
            },
            handle,
        )

    result = load_returns_from_pickle(path, benchmark="BTC")

    assert result.shape == (3, 2)
    assert isinstance(result.index, pd.DatetimeIndex)
