"""Data loading and validation for BAB strategy.

Provides loaders for CSV/JSON price or return data and a strict validator that
ensures the consumed DataFrame matches the shape the strategy pipeline expects
(datetime index, numeric columns, no duplicates, benchmark present).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


class BABDataError(ValueError):
    """Raised when input data fails validation for the BAB strategy."""


def _normalize_index(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce the index to a sorted DatetimeIndex, raising on unparseable rows."""
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except (ValueError, TypeError) as exc:
            raise BABDataError(
                f"Index could not be parsed as datetime: {exc}"
            ) from exc
    df = df.sort_index()
    if not isinstance(df.index, pd.DatetimeIndex):
        raise BABDataError("Index is not a DatetimeIndex after normalization")
    # Remove duplicate timestamps to avoid ambiguous alignment
    if df.index.has_duplicates:
        df = df[~df.index.duplicated(keep="first")]
    return df


def _promote_datetime_column(df: pd.DataFrame) -> pd.DataFrame:
    """If a single column looks like a datetime, promote it to the index.

    Detection order:
      1. A column whose name matches a common timestamp alias.
      2. A column whose name is the default CSV index placeholder (empty or
         "Unnamed: 0") and whose values all parse as datetime.
      3. Any single column whose values all parse as datetime and that is not
         the only remaining column (so we never strip the last data column).

    An asset literally named "time" is treated as data, not a timestamp, unless
    it is the only non-data column present.
    """
    if isinstance(df.index, pd.DatetimeIndex):
        return df

    candidate_names = {"date", "datetime", "timestamp", "time", "dt", "index", "idx"}
    lowered = {str(c).strip().lower(): c for c in df.columns}
    name_match = next((lowered[n] for n in candidate_names if n in lowered), None)
    if name_match is not None:
        return df.set_index(name_match)

    unnamed = [c for c in df.columns if str(c).strip() == "" or str(c).strip().lower() == "unnamed: 0"]
    if len(unnamed) == 1 and len(df.columns) > 1:
        col = unnamed[0]
        try:
            parsed = pd.to_datetime(df[col], errors="raise")
        except (ValueError, TypeError):
            parsed = None
        if parsed is not None and not parsed.isna().any():
            return df.set_index(col)

    # Last resort: a column whose values are all strings that parse as datetime,
    # and which would leave at least one data column behind. We deliberately
    # skip non-string columns so numeric returns are never mistaken for dates.
    if len(df.columns) > 1:
        for col in df.columns:
            if not pd.api.types.is_string_dtype(df[col]):
                continue
            try:
                parsed = pd.to_datetime(df[col], errors="raise")
            except (ValueError, TypeError):
                continue
            if not parsed.isna().any():
                return df.set_index(col)
    return df


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce columns to strings and strip whitespace; raise on duplicates."""
    df.columns = [str(c).strip() for c in df.columns]
    dupes = df.columns[df.columns.duplicated()].tolist()
    if dupes:
        raise BABDataError(f"Duplicate column names after normalization: {sorted(set(dupes))}")
    return df


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce every cell to float, raising on non-numeric garbage."""
    try:
        df = df.astype("float64")
    except (ValueError, TypeError) as exc:
        raise BABDataError(f"Non-numeric values present in returns data: {exc}") from exc
    return df


def validate_returns_dataframe(
    df: pd.DataFrame,
    benchmark: str | None = None,
    min_rows: int = 1,
) -> pd.DataFrame:
    """Validate that ``df`` is a usable returns DataFrame.

    Checks performed:
      * non-empty
      * datetime index (normalized and sorted)
      * string column names, no duplicates
      * all-numeric cells
      * no inf values
      * at least ``min_rows`` observations
      * benchmark column present when ``benchmark`` is provided
      * at least one asset column besides the benchmark

    Returns a cleaned, validated copy.
    """
    if df is None:
        raise BABDataError("Returns DataFrame is None")
    if not isinstance(df, pd.DataFrame):
        raise BABDataError(f"Expected pandas DataFrame, got {type(df).__name__}")

    cleaned = df.copy()
    if cleaned.empty:
        raise BABDataError("Returns DataFrame is empty")

    cleaned = _promote_datetime_column(cleaned)
    cleaned = _normalize_columns(cleaned)
    cleaned = _normalize_index(cleaned)

    if len(cleaned) < min_rows:
        raise BABDataError(
            f"Insufficient rows: got {len(cleaned)}, need at least {min_rows}"
        )

    cleaned = _coerce_numeric(cleaned)

    if np.isinf(cleaned.to_numpy()).any():
        raise BABDataError("Returns DataFrame contains infinite values")

    if benchmark is not None:
        if benchmark not in cleaned.columns:
            raise BABDataError(
                f"Benchmark '{benchmark}' not found in columns: {list(cleaned.columns)}"
            )
        # An all-NaN benchmark makes beta estimation impossible; refuse loudly
        # instead of letting NaNs propagate silently into betas and weights.
        bench_series = cleaned[benchmark]
        if not np.isfinite(bench_series.to_numpy()).any():
            raise BABDataError(
                f"Benchmark '{benchmark}' has no finite return values; "
                "cannot estimate betas against it"
            )
        non_benchmark = [c for c in cleaned.columns if c != benchmark]
        if not non_benchmark:
            raise BABDataError(
                f"Only the benchmark column '{benchmark}' is present; no assets to trade"
            )

    return cleaned


def load_returns_from_csv(
    path: str | Path,
    benchmark: str | None = None,
    min_rows: int = 1,
    **kwargs,
) -> pd.DataFrame:
    """Load returns from a CSV file and validate it.

    The CSV must have a datetime column as the first column (or a column named
    by ``index_col``) and numeric columns for each asset/benchmark.
    """
    csv_path = Path(path)
    if not csv_path.exists():
        raise BABDataError(f"CSV file not found: {csv_path}")
    try:
        df = pd.read_csv(csv_path, **kwargs)
    except (pd.errors.ParserError, OSError, UnicodeDecodeError) as exc:
        raise BABDataError(f"Failed to read CSV {csv_path}: {exc}") from exc

    return validate_returns_dataframe(df, benchmark=benchmark, min_rows=min_rows)


def load_returns_from_json(
    path: str | Path,
    benchmark: str | None = None,
    min_rows: int = 1,
    orient: str = "columns",
    **kwargs,
) -> pd.DataFrame:
    """Load returns from a JSON file (object-of-arrays or records) and validate it."""
    json_path = Path(path)
    if not json_path.exists():
        raise BABDataError(f"JSON file not found: {json_path}")
    try:
        with json_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise BABDataError(f"Failed to read JSON {json_path}: {exc}") from exc

    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
    if orient == "records":
        df = df.T  # records: list of {date: ..., ...} -> columns as dates

    return validate_returns_dataframe(df, benchmark=benchmark, min_rows=min_rows)


def load_returns_from_dataframe(
    df: pd.DataFrame,
    benchmark: str | None = None,
    min_rows: int = 1,
) -> pd.DataFrame:
    """Validate an in-memory DataFrame (thin wrapper around validation)."""
    return validate_returns_dataframe(df, benchmark=benchmark, min_rows=min_rows)


def load_returns(
    source: str | Path | pd.DataFrame,
    benchmark: str | None = None,
    min_rows: int = 1,
    **kwargs,
) -> pd.DataFrame:
    """Dispatch to the appropriate loader based on the type of ``source``.

    - ``str``/``Path`` ending in ``.csv`` -> CSV loader
    - ``str``/``Path`` ending in ``.json`` -> JSON loader
    - ``pd.DataFrame`` -> DataFrame loader
    """
    if isinstance(source, pd.DataFrame):
        return load_returns_from_dataframe(source, benchmark=benchmark, min_rows=min_rows)

    path = Path(source)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return load_returns_from_csv(path, benchmark=benchmark, min_rows=min_rows, **kwargs)
    if suffix in (".json", ".jsonl"):
        return load_returns_from_json(path, benchmark=benchmark, min_rows=min_rows, **kwargs)
    raise BABDataError(f"Unsupported data source extension: {suffix!r} for {path}")


def list_columns(df: pd.DataFrame) -> list[str]:
    """Return sorted column names (helper for diagnostics)."""
    return sorted(str(c) for c in df.columns)


def iter_assets(df: pd.DataFrame, benchmark: str | None = None) -> Iterable[str]:
    """Yield asset column names, optionally excluding the benchmark."""
    for col in df.columns:
        name = str(col)
        if benchmark is not None and name == benchmark:
            continue
        yield name