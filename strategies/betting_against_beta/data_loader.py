"""Data loading and validation for BAB strategy.

Provides loaders for CSV/JSON price or return data and a strict validator that
ensures the consumed DataFrame matches the shape the strategy pipeline expects
(datetime index, numeric columns, no duplicates, benchmark present).
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


class BABDataError(ValueError):
    """Raised when input data fails validation for the BAB strategy."""


_EXCHANGE_DATE_KEYS = {"date", "datetime", "time", "timestamp", "open time", "close time", "candle_begin_time", "unix", "epoch", "t"}
_EXCHANGE_PRICE_KEYS = {"close", "adj close", "adj_close", "closing price", "price", "last", "weighted price", "vwap"}
_EXCHANGE_OPEN_KEYS = {"open", "open price"}
_EXCHANGE_HIGH_KEYS = {"high", "high price"}
_EXCHANGE_LOW_KEYS = {"low", "low price"}
_EXCHANGE_VOL_KEYS = {"volume", "vol", "base volume", "quote volume", "trading volume", "volume btc", "volume usd"}
_EXCHANGE_SYMBOL_KEYS = {"symbol", "ticker", "pair", "market", "asset", "coin", "currency"}


def _normalize_index(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce the index to a sorted DatetimeIndex, raising on unparseable rows."""
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            # Try epoch handling first for numeric indexes
            idx = df.index
            # Check if numeric
            try:
                if pd.api.types.is_numeric_dtype(idx):
                    # Heuristic: if values look like epoch
                    sample = idx[0] if len(idx) > 0 else 0
                    try:
                        sv = float(sample)
                        if sv > 1e12:  # ms
                            df.index = pd.to_datetime(idx, unit='ms')
                        elif sv > 1e9:  # seconds
                            df.index = pd.to_datetime(idx, unit='s')
                        elif sv > 1e6:  # smaller epoch
                            df.index = pd.to_datetime(idx, unit='s')
                        else:
                            df.index = pd.to_datetime(idx, errors="raise")
                    except Exception:
                        df.index = pd.to_datetime(idx, errors="raise")
                else:
                    df.index = pd.to_datetime(idx, errors="raise")
            except Exception:
                df.index = pd.to_datetime(idx, errors="raise")
        except (ValueError, TypeError) as exc:
            raise BABDataError(
                f"Index could not be parsed as datetime: {exc}"
            ) from exc
    # Handle timezone-aware indexes deterministically: convert to UTC, then
    # strip the tz so downstream code sees a consistent naive UTC representation.
    if isinstance(df.index, pd.DatetimeIndex) and getattr(df.index, "tz", None) is not None:
        try:
            df.index = df.index.tz_convert("UTC").tz_localize(None)
        except (TypeError, AttributeError, ValueError):
            try:
                df.index = df.index.tz_localize(None)
            except (TypeError, AttributeError, ValueError):
                pass
    df = df.sort_index()
    if not isinstance(df.index, pd.DatetimeIndex):
        raise BABDataError("Index is not a DatetimeIndex after normalization")
    # Remove duplicate timestamps to avoid ambiguous alignment
    if df.index.has_duplicates:
        df = df[~df.index.duplicated(keep="first")]
    return df


def _coerce_to_datetime_scalar(val):
    """Try to coerce various epoch formats to datetime."""
    try:
        if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
            raise ValueError("bad")
        if isinstance(val, str):
            s = val.strip()
            if s.lower() in {"", "na", "n/a", "nan", "null", "none"}:
                raise ValueError("bad")
            # Try epoch seconds/milliseconds
            # If all digits (and maybe minus)
            try:
                # epoch ms?
                # heuristics
                if s.isdigit() or (s[0] in '+-' and s[1:].isdigit()):
                    num = int(float(s))
                    if num > 1e12:  # ms
                        return pd.to_datetime(num, unit="ms", utc=True)
                    elif num > 1e9:  # seconds
                        return pd.to_datetime(num, unit="s", utc=True)
                    else:
                        return pd.to_datetime(num, unit="s", utc=True)
            except Exception:
                pass
            # try normal parse
            return pd.to_datetime(s, utc=True)
        if isinstance(val, (int, np.integer)):
            v = int(val)
            if v > 1e12:
                return pd.to_datetime(v, unit="ms", utc=True)
            elif v > 1e9:
                return pd.to_datetime(v, unit="s", utc=True)
            else:
                return pd.to_datetime(v, unit="s", utc=True)
        if isinstance(val, (float, np.floating)):
            v = float(val)
            if np.isnan(v) or np.isinf(v):
                raise ValueError("bad")
            if v > 1e12:
                return pd.to_datetime(int(v) if v.is_integer() else v, unit="ms", utc=True)
            elif v > 1e9:
                return pd.to_datetime(v, unit="s", utc=True)
            else:
                return pd.to_datetime(v, unit="s", utc=True)
        return pd.to_datetime(val, utc=True)
    except Exception:
        raise


def _detect_and_normalize_exchange_format(df: pd.DataFrame) -> pd.DataFrame:
    """Detect common exchange CSV formats (CoinGecko, Binance, Coinbase) and normalize."""
    if df.empty or not isinstance(df, pd.DataFrame):
        return df
    df = df.copy()
    df = _normalize_columns(df)
    cols = [str(c).strip().lower() for c in df.columns]
    colmap = {str(c).strip().lower(): c for c in df.columns}

    # If index already datetime, still might need column normalization
    # Try to detect wide format where each column is a symbol with prices? Or long format
    # Handle long format: columns like symbol/ticker + date + close/price
    symbol_col = None
    for k in _EXCHANGE_SYMBOL_KEYS:
        if k in colmap:
            symbol_col = colmap[k]
            break
    date_col = None
    for k in _EXCHANGE_DATE_KEYS:
        if k in colmap:
            date_col = colmap[k]
            break
    # Binance often has 'Open time' as epoch ms or string
    if date_col is None:
        # look for columns containing 'time'/'date'
        for c in df.columns:
            cl = str(c).strip().lower()
            if 'time' in cl or cl == 'date' or cl == 'timestamp':
                date_col = c
                break

    price_col = None
    for k in _EXCHANGE_PRICE_KEYS:
        if k in colmap:
            price_col = colmap[k]
            break
    # If no explicit close/price, maybe 'adj close' etc already handled
    if price_col is None:
        for c in df.columns:
            cl = str(c).strip().lower()
            if cl == 'close' or cl.endswith('close') or cl == 'last price' or cl == 'price':
                price_col = c
                break

    open_col = next((colmap[k] for k in _EXCHANGE_OPEN_KEYS if k in colmap), None)
    high_col = next((colmap[k] for k in _EXCHANGE_HIGH_KEYS if k in colmap), None)
    low_col = next((colmap[k] for k in _EXCHANGE_LOW_KEYS if k in colmap), None)

    # If it's long format (symbol + date + price) -> pivot to wide prices
    if symbol_col is not None and date_col is not None and price_col is not None:
        try:
            # normalize date
            try:
                parsed_dates = df[date_col].apply(_coerce_to_datetime_scalar)
                parsed = []
                for pdv in parsed_dates:
                    try:
                        if hasattr(pdv, 'tzinfo') and pdv.tzinfo is not None:
                            pdv = pdv.tz_convert('UTC').tz_localize(None)
                        else:
                            try:
                                pdt = pd.Timestamp(pdv)
                                if getattr(pdt, 'tzinfo', None) is not None:
                                    pdt = pdt.tz_convert('UTC').tz_localize(None)
                                parsed.append(pdt)
                                continue
                            except Exception:
                                pass
                    except Exception:
                        pass
                    try:
                        pdt = pd.to_datetime(pdv)
                        if getattr(pdt, 'tz', None) is not None:
                            pdt = pdt.tz_convert('UTC').tz_localize(None)
                        parsed.append(pdt)
                    except Exception:
                        parsed.append(pdv)
                tmp = df.copy()
                tmp['_dt'] = parsed
            except Exception:
                tmp = df.copy()
                tmp['_dt'] = pd.to_datetime(tmp[date_col], errors='coerce', utc=True)
                try:
                    tmp['_dt'] = tmp['_dt'].dt.tz_convert('UTC').dt.tz_localize(None)
                except Exception:
                    try:
                        tmp['_dt'] = tmp['_dt'].dt.tz_localize(None)
                    except Exception:
                        pass
            # get symbol values (normalize case)
            tmp['_sym'] = tmp[symbol_col].astype(str).str.strip()
            # pivot
            pivoted = tmp.pivot_table(index='_dt', columns='_sym', values=price_col, aggfunc='last')
            pivoted.index.name = None
            pivoted.columns = [str(c).strip() for c in pivoted.columns]
            return pivoted
        except Exception:
            pass
    # OHLCV wide format for single asset (no symbol column) - use Close/Adj Close as price
    if date_col is not None and symbol_col is None:
        try:
            # prefer adjusted close, then close
            price_choice = None
            for k in ['adj close', 'adj_close', 'adjusted close', 'close_price']:
                if k in colmap:
                    price_choice = colmap[k]
                    break
            if price_choice is None and 'close' in colmap:
                price_choice = colmap['close']
            elif price_choice is None and price_col in df.columns:
                price_choice = price_col
            if price_choice is not None:
                try:
                    tmp = df.copy()
                    parsed_dates = tmp[date_col].apply(_coerce_to_datetime_scalar)
                    parsed = []
                    for pdv in parsed_dates:
                        try:
                            if hasattr(pdv, 'tzinfo') and pdv.tzinfo is not None:
                                pdv = pdv.tz_convert('UTC').tz_localize(None)
                            else:
                                try:
                                    pdt = pd.Timestamp(pdv)
                                    if getattr(pdt, 'tzinfo', None) is not None:
                                        pdt = pdt.tz_convert('UTC').tz_localize(None)
                                    parsed.append(pdt)
                                    continue
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        try:
                            pdt = pd.to_datetime(pdv)
                            if getattr(pdt, 'tz', None) is not None:
                                pdt = pdt.tz_convert('UTC').tz_localize(None)
                            parsed.append(pdt)
                        except Exception:
                            parsed.append(pdv)
                    # If the Close column might be named as a symbol in some formats? Or just keep as Close
                    # Try to infer symbol from common patterns - sometimes 'symbol' in filename not here; also check if other cols look like symbols
                    tmp_out = tmp[[price_choice]].copy()
                    tmp_out.index = parsed
                    tmp_out.index.name = None
                    tmp_out.columns = [str(c).strip() for c in tmp_out.columns]
                    # Normalize column name case for common names
                    return tmp_out
                except Exception:
                    pass
        except Exception:
            pass

    # If we have date column but index not set, promote it with better parsing
    if date_col is not None and not isinstance(df.index, pd.DatetimeIndex):
        # For simple cases that might expect string index preservation, be conservative
        # Only do heavy coercion if values look like epoch numbers
        try:
            sample = df[date_col].iloc[0] if len(df[date_col]) > 0 else None
            do_coerce = False
            if isinstance(sample, str):
                s = str(sample).strip()
                if s.isdigit() or (len(s) > 0 and s[0] in '+-' and s[1:].isdigit()):
                    do_coerce = True
                elif len(s) > 10 and any(c.isdigit() for c in s) and ':' in s:
                    do_coerce = False  # let pandas handle normally in other code paths
                else:
                    do_coerce = False
            elif isinstance(sample, (int, np.integer, float, np.floating)) and not isinstance(sample, bool):
                v = float(sample)
                if not np.isnan(v) and (abs(v) > 1e9):  # likely epoch
                    do_coerce = True
                else:
                    do_coerce = False
            else:
                do_coerce = False
            if not do_coerce:
                return df  # let original promotion logic handle
        except Exception:
            pass

    # If OHLCV format with Close/Adj Close, prefer Close for prices
    if price_col is not None and price_col in df.columns:
        # If there might be multiple columns but we want to use close as price series for each asset?
        # For wide format, each column is asset - if they are prices (close), fine. Also sometimes Coinbase has different naming
        pass

    # Normalize column names to be more consistent (symbol case handling)
    new_cols = []
    for c in df.columns:
        nc = str(c).strip()
        # common mappings
        cl = nc.lower()
        if cl in {'adj close', 'adj_close'}:
            new_cols.append('Close' if False else nc)  # keep as-is
        new_cols.append(nc)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _promote_datetime_column(df: pd.DataFrame) -> pd.DataFrame:
    """If a single column looks like a datetime, promote it to the index."""
    if isinstance(df.index, pd.DatetimeIndex):
        return df

    # Try exchange normalization first for better format support
    try:
        df2 = _detect_and_normalize_exchange_format(df)
        if isinstance(df2.index, pd.DatetimeIndex):
            return df2
        df = df2
    except Exception:
        pass

    candidate_names = {"date", "datetime", "timestamp", "time", "dt", "index", "idx", "open time", "close time", "snapped_at", "snapped at", "dateutc", "candle time"}
    lowered = {str(c).strip().lower(): c for c in df.columns}
    name_match = next((lowered[n] for n in candidate_names if n in lowered), None)
    if name_match is not None:
        try:
            df = df.set_index(name_match)
            return df
        except (ValueError, TypeError, KeyError):
            pass

    unnamed = [c for c in df.columns if str(c).strip() == "" or str(c).strip().lower() == "unnamed: 0"]
    if len(unnamed) == 1 and len(df.columns) > 1:
        col = unnamed[0]
        try:
            parsed = pd.to_datetime(df[col], errors="raise")
        except (ValueError, TypeError):
            parsed = None
        if parsed is not None and not parsed.isna().any():
            return df.set_index(col)

    # Last resort: promote any remaining object/string column that parses as
    # datetime. Skip a named date-like column already attempted via set_index
    # above so a failed set_index is not silently bypassed by the backdoor.
    if len(df.columns) > 1:
        tried = {name_match} if name_match is not None else set()
        for col in df.columns:
            if col in tried:
                continue
            if not pd.api.types.is_string_dtype(df[col]) and not pd.api.types.is_object_dtype(df[col]):
                continue
            try:
                try:
                    coerced = df[col].apply(_coerce_to_datetime_scalar)
                    if coerced is not None:
                        coerced_series = coerced
                        # check not all na
                        try:
                            if not getattr(coerced_series, "isna", lambda: pd.Series([True]))().all():
                                df2 = df.copy()
                                df2.index = coerced_series
                                df2 = df2.drop(columns=[col])
                                return df2
                        except Exception:
                            pass
                except Exception:
                    pass
                parsed = pd.to_datetime(df[col], errors="raise")
            except (ValueError, TypeError):
                continue
            if parsed is not None and hasattr(parsed, "isna") and not parsed.isna().any():
                try:
                    return df.set_index(col)
                except (ValueError, TypeError, KeyError):
                    continue
    return df


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce columns to strings and strip whitespace; raise on duplicates."""
    df.columns = [str(c).strip() for c in df.columns]
    dupes = df.columns[df.columns.duplicated()].tolist()
    if dupes:
        raise BABDataError(f"Duplicate column names after normalization: {sorted(set(dupes))}")
    return df


def _drop_all_nan_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop columns that are entirely NaN (delisted or untradable assets).

    A column with no finite values contributes nothing to beta estimation or
    ranking, and keeping it would let NaNs propagate into signals/weights.
    """
    if df.empty:
        return df
    keep = []
    for col in df.columns:
        try:
            # Convert to numeric to be safe
            numeric = pd.to_numeric(df[col], errors="coerce")
            arr = numeric.to_numpy(dtype=float)
            if np.isfinite(arr).any():
                keep.append(col)
            # else drop if all NaN/inf
        except (ValueError, TypeError):
            keep.append(col)
            continue
    if len(keep) == len(df.columns):
        return df
    if not keep:
        raise BABDataError("All columns are entirely NaN; no tradable assets remain")
    return df[keep]


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce every cell to float, raising on non-numeric garbage."""
    try:
        # First pass: try direct astype for efficiency
        try:
            if not isinstance(df, pd.DataFrame):
                raise TypeError(f"Expected DataFrame, got {type(df).__name__}")
            df = df.astype("float64")
            return df
        except BABDataError:
            raise
        except (ValueError, TypeError):
            pass
        # Second pass: coerce with to_numeric to catch things like commas, but fail loudly if unparseable
        if not isinstance(df, pd.DataFrame):
            raise BABDataError(f"Expected DataFrame, got {type(df).__name__}")
        df_clean = df.copy()
        for col in df_clean.columns:
            series = df_clean[col]
            # If it's object dtype, look for string patterns
            if series.dtype == object or pd.api.types.is_string_dtype(series):
                # Replace commas if they appear as thousand separators (simple heuristic)
                def clean_val(x):
                    if isinstance(x, str):
                        cleaned = x.strip()
                        # Check for explicit NA markers
                        lower = cleaned.lower()
                        if lower in {'na', 'n/a', 'nan', 'none', 'null', '#n/a', '#na', 'missing'}:
                            return np.nan
                        # Handle cases like "1,000.50"
                        if ',' in cleaned and '.' in cleaned:
                            cleaned = cleaned.replace(',', '')
                        elif ',' in cleaned and cleaned.count(',') == 1 and len(cleaned.split(',')[-1]) <= 3:
                            # Could be decimal or thousand sep - if ends with 2-3 digits maybe decimal in some locales? But less common for returns
                            # Try decimal comma first if it's European style - but safer to also try removing if it causes issues?
                            # Default: remove commas (thousand sep)
                            cleaned = cleaned.replace(',', '')
                        elif ',' in cleaned:
                            cleaned = cleaned.replace(',', '')
                        # Handle percent signs: "1.5%" -> 0.015, "150%" -> 1.5
                        if cleaned.endswith('%'):
                            try:
                                num = float(cleaned[:-1].strip()) / 100.0
                                return num
                            except (ValueError, TypeError):
                                return np.nan
                        return cleaned
                    return x
                try:
                    cleaned_series = series.apply(clean_val)
                    converted = pd.to_numeric(cleaned_series, errors='raise')
                    df_clean[col] = converted.astype('float64')
                except Exception as exc:
                    raise BABDataError(f"Non-numeric values present in returns data: {exc}") from exc
            else:
                try:
                    df_clean[col] = pd.to_numeric(series, errors='raise').astype('float64')
                except Exception as exc:
                    raise BABDataError(f"Non-numeric values present in returns data: {exc}") from exc
        return df_clean
    except BABDataError:
        raise
    except (ValueError, TypeError, AttributeError) as exc:
        raise BABDataError(f"Non-numeric values present in returns data: {exc}") from exc


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
    try:
        cleaned = _normalize_index(cleaned)
    except BABDataError:
        raise
    except (ValueError, TypeError) as exc:
        raise BABDataError(str(exc)) from exc

    if len(cleaned) < min_rows:
        raise BABDataError(
            f"Insufficient rows: got {len(cleaned)}, need at least {min_rows}"
        )

    cleaned = _coerce_numeric(cleaned)

    # Drop columns that are entirely NaN (delisted/untradable assets) before
    # the inf check so they cannot propagate NaNs into beta estimation.
    cleaned = _drop_all_nan_columns(cleaned)

    if np.isinf(cleaned.to_numpy()).any():
        raise BABDataError("Returns DataFrame contains infinite values")

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
    try:
        cleaned = _normalize_index(cleaned)
    except BABDataError:
        raise
    except (ValueError, TypeError) as exc:
        raise BABDataError(str(exc)) from exc

    if len(cleaned) < min_rows:
        raise BABDataError(
            f"Insufficient rows: got {len(cleaned)}, need at least {min_rows}"
        )

    cleaned = _coerce_numeric(cleaned)

    # Drop columns that are entirely NaN (delisted/untradable assets) before
    # the inf check so they cannot propagate NaNs into beta estimation.
    cleaned = _drop_all_nan_columns(cleaned)

    if np.isinf(cleaned.to_numpy()).any():
        raise BABDataError("Returns DataFrame contains infinite values")

    # Handle symbol case-insensitively for benchmark
    if benchmark is not None:
        bench_found = None
        if benchmark in cleaned.columns:
            bench_found = benchmark
        else:
            # case-insensitive match
            bench_map = {str(c).strip().lower(): c for c in cleaned.columns}
            if str(benchmark).strip().lower() in bench_map:
                bench_found = bench_map[str(benchmark).strip().lower()]
                # rename to original benchmark case for consistency if requested? or just match
        if bench_found is None:
            raise BABDataError(
                f"Benchmark '{benchmark}' not found in columns: {list(cleaned.columns)}"
            )
        # If different case, optionally normalize column name to match requested benchmark? Keep compatible
        if bench_found != benchmark and benchmark in cleaned.columns is False:
            # try to rename
            try:
                cleaned = cleaned.rename(columns={bench_found: benchmark})
                bench_found = benchmark
            except Exception:
                pass
        if benchmark not in cleaned.columns:
            # final check
            bench_map = {str(c).strip().lower(): c for c in cleaned.columns}
            if str(benchmark).strip().lower() in bench_map:
                bf = bench_map[str(benchmark).strip().lower()]
                cleaned = cleaned.rename(columns={bf: benchmark})
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

    # Per-asset minimum history: an asset with too few finite observations
    # cannot be reliably ranked and would produce degenerate betas. Use the
    # caller-supplied ``min_rows`` floor so small test fixtures still validate
    # while real-data consumers can enforce a higher bar.
    finite_counts = pd.DataFrame(cleaned).apply(lambda s: int(np.isfinite(s.to_numpy()).sum()))
    short = finite_counts[finite_counts < min_rows]
    if len(short) > 0:
        details = ", ".join(f"{col}={int(n)}" for col, n in short.sort_values().items())
        raise BABDataError(
            f"Insufficient finite history for {len(short)} asset(s) "
            f"(need >= {min_rows} finite rows): {details}"
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
        read_kwargs = dict(kwargs)
        read_kwargs.setdefault("low_memory", False)
        df = pd.read_csv(csv_path, **read_kwargs)
    except (pd.errors.ParserError, OSError, UnicodeDecodeError, ValueError) as exc:
        raise BABDataError(f"Failed to read CSV {csv_path}: {exc}") from exc
    if df is None or df.empty:
        raise BABDataError(f"Empty CSV file: {csv_path}")

    return validate_returns_dataframe(df, benchmark=benchmark, min_rows=min_rows)


def load_returns_from_parquet(
    path: str | Path,
    benchmark: str | None = None,
    min_rows: int = 1,
    **kwargs,
) -> pd.DataFrame:
    """Load returns from a Parquet file and validate it."""
    pq_path = Path(path)
    if not pq_path.exists():
        raise BABDataError(f"Parquet file not found: {pq_path}")
    try:
        try:
            df = pd.read_parquet(pq_path, **kwargs)
        except Exception as exc:
            raise BABDataError(
                f"Failed to read Parquet {pq_path}: {exc}. "
                "Install 'pyarrow' or 'fastparquet' to enable parquet support."
            ) from exc
    except BABDataError:
        raise
    except (OSError, ValueError) as exc:
        raise BABDataError(f"Failed to read Parquet {pq_path}: {exc}") from exc
    return validate_returns_dataframe(df, benchmark=benchmark, min_rows=min_rows)


def load_returns_from_hdf5(
    path: str | Path,
    benchmark: str | None = None,
    min_rows: int = 1,
    key: str | None = None,
    **kwargs,
) -> pd.DataFrame:
    """Load returns from an HDF5 file and validate it."""
    h5_path = Path(path)
    if not h5_path.exists():
        raise BABDataError(f"HDF5 file not found: {h5_path}")
    try:
        try:
            if key is not None:
                df = pd.read_hdf(h5_path, key=key, **kwargs)
            else:
                df = pd.read_hdf(h5_path, **kwargs)
        except Exception as exc:
            raise BABDataError(
                f"Failed to read HDF5 {h5_path}: {exc}. "
                "Install 'tables' to enable hdf5 support."
            ) from exc
    except BABDataError:
        raise
    except (OSError, ValueError) as exc:
        raise BABDataError(f"Failed to read HDF5 {h5_path}: {exc}") from exc
    return validate_returns_dataframe(df, benchmark=benchmark, min_rows=min_rows)


def load_returns_from_pickle(
    path: str | Path,
    benchmark: str | None = None,
    min_rows: int = 1,
    **kwargs,
) -> pd.DataFrame:
    """Load returns from a pickle file and validate it."""
    pkl_path = Path(path)
    if not pkl_path.exists():
        raise BABDataError(f"Pickle file not found: {pkl_path}")
    try:
        with pkl_path.open("rb") as handle:
            obj = pickle.load(handle)
        if isinstance(obj, pd.DataFrame):
            df = obj
        elif isinstance(obj, dict):
            df = pd.DataFrame(obj)
        else:
            raise BABDataError(f"Unsupported pickle object type: {type(obj).__name__}")
    except BABDataError:
        raise
    except (OSError, pickle.UnpicklingError, ValueError, TypeError) as exc:
        raise BABDataError(f"Failed to read pickle {pkl_path}: {exc}") from exc
    return validate_returns_dataframe(df, benchmark=benchmark, min_rows=min_rows)


def load_returns_from_json(
    path: str | Path,
    benchmark: str | None = None,
    min_rows: int = 1,
    orient: str = "columns",
    **kwargs,
) -> pd.DataFrame:
    """Load returns from a JSON file and validate it.

    Supports ``columns`` (object-of-arrays), ``records`` (list of dicts),
    ``split`` (``{"columns": [...], "index": [...], "data": [...]}``), and
    ``table`` orients. Datetime columns/index are promoted automatically.
    """
    json_path = Path(path)
    if not json_path.exists():
        raise BABDataError(f"JSON file not found: {json_path}")
    suffix = json_path.suffix.lower()
    try:
        if suffix == ".jsonl":
            # JSON Lines: one JSON object per line
            records = []
            with json_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        raise BABDataError(f"Failed to read JSONL {json_path}: {exc}") from exc
            if not records:
                raise BABDataError(f"Empty JSONL file: {json_path}")
            data = records
            orient = kwargs.get("orient", "records")
        else:
            with json_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
    except BABDataError:
        raise
    except (OSError, json.JSONDecodeError) as exc:
        raise BABDataError(f"Failed to read JSON {json_path}: {exc}") from exc

    # Build a DataFrame from the parsed JSON, handling the common orients
    # explicitly so we don't drop rows or misalign columns.
    if isinstance(data, pd.DataFrame):
        df = data
    elif orient == "records":
        df = pd.DataFrame(data)
        df = _promote_datetime_column(df)
        df = _normalize_columns(df)
        try:
            df = _normalize_index(df)
        except Exception:
            pass
        return validate_returns_dataframe(df, benchmark=benchmark, min_rows=min_rows)
    elif orient == "split":
        # {"columns": [...], "index": [...], "data": [[...], ...]}
        if not isinstance(data, dict) or "data" not in data:
            raise BABDataError(
                "JSON with orient='split' must contain 'columns', 'index', and 'data' keys"
            )
        df = pd.DataFrame(data=data["data"], columns=data.get("columns"))
        if "index" in data and data["index"] is not None:
            df.index = data["index"]
    elif orient == "index":
        # {col: {timestamp: value, ...}, ...}
        df = pd.DataFrame(data)
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index, errors="raise")
            except (ValueError, TypeError):
                pass
    else:
        # columns / table / anything else pandas understands
        df = pd.DataFrame(data)

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
    - ``str``/``Path`` ending in ``.json``/.jsonl -> JSON loader
    - ``str``/``Path`` ending in ``.parquet``/.pq -> Parquet loader
    - ``str``/``Path`` ending in ``.h5``/.hdf5/.hdf -> HDF5 loader
    - ``str``/``Path`` ending in ``.pkl``/.pickle -> Pickle loader
    - ``pd.DataFrame`` -> DataFrame loader
    """
    if source is None:
        raise BABDataError("Data source is None")
    if isinstance(source, pd.DataFrame):
        return load_returns_from_dataframe(source, benchmark=benchmark, min_rows=min_rows)

    path = Path(source)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return load_returns_from_csv(path, benchmark=benchmark, min_rows=min_rows, **kwargs)
    if suffix in (".json", ".jsonl"):
        return load_returns_from_json(path, benchmark=benchmark, min_rows=min_rows, **kwargs)
    if suffix in (".parquet", ".pq"):
        return load_returns_from_parquet(path, benchmark=benchmark, min_rows=min_rows, **kwargs)
    if suffix in (".h5", ".hdf5", ".hdf"):
        key = kwargs.pop("key", None)
        return load_returns_from_hdf5(path, benchmark=benchmark, min_rows=min_rows, key=key, **kwargs)
    if suffix in (".pkl", ".pickle"):
        return load_returns_from_pickle(path, benchmark=benchmark, min_rows=min_rows, **kwargs)
    raise BABDataError(f"Unsupported data source extension: {suffix!r} for {path}")


def _prices_to_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert a price DataFrame to simple returns.

    The first row is dropped (no prior price to compare against). Returns are
    finite by construction: any inf produced by a zero-price day is coerced to
    NaN and any all-NaN columns are dropped later by validation.
    """
    if df.shape[0] < 2:
        raise BABDataError(
            f"Price series too short for return computation: {df.shape[0]} rows, need >= 2"
        )
    ret = df.pct_change().iloc[1:]
    ret = ret.replace([np.inf, -np.inf], np.nan)
    return ret


def load_prices(
    source: str | Path | pd.DataFrame,
    benchmark: str | None = None,
    min_rows: int = 2,
    **kwargs,
) -> pd.DataFrame:
    """Load a price CSV/JSON/DataFrame and convert it to a returns DataFrame.

    Prices are accepted as-is (a date column promoted to the index, numeric
    columns per asset/benchmark). The loader computes ``pct_change`` to produce
    returns, then validates the result through :func:`validate_returns_dataframe`.

    A price fixture with date gaps and an all-NaN (delisted) column is handled:
    gaps become NaN returns that beta estimation tolerates, and the delisted
    column is dropped by validation.
    """
    if isinstance(source, pd.DataFrame):
        prices = load_returns_from_dataframe(
            source, benchmark=None, min_rows=min_rows
        )
    elif isinstance(source, (str, Path)):
        path = Path(source)
        suffix = path.suffix.lower()
        if suffix == ".csv":
            prices = load_returns_from_csv(path, benchmark=None, min_rows=min_rows, **kwargs)
        elif suffix in (".json", ".jsonl"):
            prices = load_returns_from_json(path, benchmark=None, min_rows=min_rows, **kwargs)
        else:
            raise BABDataError(f"Unsupported price source extension: {suffix!r} for {path}")
    else:
        raise BABDataError(f"Unsupported price source type: {type(source).__name__}")

    returns = _prices_to_returns(prices)
    return validate_returns_dataframe(returns, benchmark=benchmark, min_rows=min_rows)


def _is_likely_returns(df: pd.DataFrame) -> bool:
    """Heuristic to detect if DataFrame contains returns vs prices."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return False
    try:
        # Try numeric
        arr = df.select_dtypes(include=[np.number]).to_numpy()
        if arr.size == 0:
            return False
        # Returns are usually small in magnitude, prices larger
        absmax = np.nanmax(np.abs(arr))
        # Also check if values look like pct changes (-0.5 to 0.5 typical)
        if absmax < 10:  # likely returns
            return True
        return False
    except Exception:
        return False


def detect_price_or_returns(
    source: str | Path | pd.DataFrame,
    **kwargs,
) -> str:
    """Auto-detect whether source contains prices or returns."""
    if isinstance(source, pd.DataFrame):
        df = source
    else:
        path = Path(source)
        suffix = path.suffix.lower()
        if suffix == ".csv":
            try:
                read_kwargs = dict(kwargs)
                read_kwargs.setdefault("low_memory", False)
                df = pd.read_csv(path, **read_kwargs)
            except Exception:
                return "unknown"
        elif suffix in (".json", ".jsonl"):
            try:
                if suffix == ".jsonl":
                    records = []
                    with path.open("r", encoding="utf-8") as handle:
                        for line in handle:
                            line = line.strip()
                            if not line or line.startswith("#"):
                                continue
                            try:
                                records.append(json.loads(line))
                            except Exception:
                                continue
                    df = pd.DataFrame(records) if records else pd.DataFrame()
                else:
                    with path.open("r", encoding="utf-8") as handle:
                        data = json.load(handle)
                    if isinstance(data, pd.DataFrame):
                        df = data
                    elif isinstance(data, dict):
                        # try common forms
                        df = pd.DataFrame(data)
                    elif isinstance(data, list):
                        df = pd.DataFrame(data)
                    else:
                        df = pd.DataFrame()
            except Exception:
                return "unknown"
        else:
            return "unknown"
    if _is_likely_returns(df):
        return "returns"
    return "prices"


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

# Alias for convenience
load_returns_from_prices = load_prices
load_price_data = load_prices
detect_source_type = detect_price_or_returns
