"""Performance & regression tests for returns-DataFrame validation hot paths.

Guards the two per-column validation loops that dominated ``BABStrategy.run``
after the beta/portfolio optimizations:

* ``data_loader._drop_all_nan_columns`` -- all-NaN column removal.
* ``data_loader._run_data_quality_campaign`` -- finite-fraction / stale-run
  checks.

Both now have a vectorized numeric fast path. These tests assert the fast path
is *exactly* equivalent to an explicit per-column oracle across representative
and edge-case frames (including mixed dtypes), and add a non-flaky guard so the
vectorization cannot silently regress.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.data_loader import _series_is_parseable, _strip_units_and_parse
from strategies.betting_against_beta.errors import BABDataError


def _timed(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return result, time.perf_counter() - start


def _oracle_drop_all_nan(df: pd.DataFrame) -> pd.DataFrame:
    """Explicit per-column oracle mirroring the documented semantics."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return df
    keep = []
    for col in df.columns:
        numeric = pd.to_numeric(df[col], errors="coerce")
        arr = numeric.to_numpy(dtype=float)
        if np.isfinite(arr).any():
            keep.append(col)
            continue
        if not df[col].isna().all():
            keep.append(col)
            continue
    if not keep:
        raise BABDataError(
            "All columns are entirely NaN; no usable return data remains."
        )
    return df[keep]


def _oracle_quality(
    df: pd.DataFrame,
    max_return_abs=None,
    max_gap_days=None,
    stale_run_threshold=None,
    min_finite_fraction=None,
    allow_duplicate_timestamps=False,
) -> pd.DataFrame:
    """Explicit per-column oracle for the finite-fraction / stale-run checks.

    Only the column checks are mirrored; the structural parts of the real
    campaign (index normalization, dedupe, implausible-return / gap guards) are
    exercised through the public wrapper in the campaign tests. Here we compare
    against the helper on a frame that is already structurally clean.
    """
    cleaned = df.copy()
    if stale_run_threshold is None:
        stale_run_threshold = 50
    if min_finite_fraction is None:
        min_finite_fraction = 0.0
    for col in cleaned.columns:
        arr = pd.to_numeric(cleaned[col], errors="coerce").to_numpy(dtype=float)
        finite_count = int(np.isfinite(arr).sum())
        total = int(len(arr))
        if total > 0 and float(min_finite_fraction) > 0:
            frac = finite_count / total if total > 0 else 0.0
            if frac < float(min_finite_fraction):
                raise BABDataError(
                    f"Column '{col}' has insufficient finite data: {frac:.2%} < {float(min_finite_fraction):.2%}"
                )
        if stale_run_threshold is not None and int(stale_run_threshold) > 0 and finite_count >= int(stale_run_threshold):
            max_allowed_stale = max(int(stale_run_threshold), 50)
            max_run = dl._max_consecutive_equal_finite(arr)
            if max_run >= max_allowed_stale:
                raise BABDataError(
                    f"Stale/frozen data detected in column '{col}': {max_run} consecutive equal values"
                )
    return cleaned


def _oracle_series_is_parseable(series):
    """Explicit per-cell oracle for _series_is_parseable semantics."""
    try:
        total = 0
        parseable = 0
        for v in series:
            if v is None:
                parseable += 1
                continue
            if isinstance(v, float) and np.isnan(v):
                parseable += 1
                continue
            total += 1
            try:
                _strip_units_and_parse(v)
                parseable += 1
            except Exception:
                continue
        if total == 0:
            return True
        return parseable >= max(1, int(total * 0.5))
    except Exception:
        return False


def _numeric_frame(n_days=500, n_assets=30, seed=11, inject=None):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2018-01-01", periods=n_days)
    cols = [f"A{i}" for i in range(n_assets - 1)] + ["BTC"]
    data = rng.normal(0.0004, 0.016, size=(n_days, n_assets))
    df = pd.DataFrame(data, index=idx, columns=cols)
    if inject is not None:
        inject(df)
    return df


class TestDropAllNaNColumnsEquivalence:
    def _assert_same(self, df):
        got = dl._drop_all_nan_columns(df)
        expected = _oracle_drop_all_nan(df)
        pd.testing.assert_frame_equal(got, expected)

    def test_numeric_frame_matches_oracle(self):
        df = _numeric_frame()
        df["ALL_NAN"] = np.nan
        df["PARTIAL"] = np.nan
        df.loc[df.index[:10], "PARTIAL"] = 1.0
        self._assert_same(df)

    def test_mixed_dtypes_match_oracle(self):
        df = pd.DataFrame(
            {
                "a": [1.0, 2.0, 3.0],
                "all_nan": [np.nan, np.nan, np.nan],
                "inf": [np.inf, -np.inf, 2.0],
                "strs": ["1", "2", "3"],
                "junk": ["x", "y", "z"],
                "none": [None, None, None],
            }
        )
        self._assert_same(df)

    def test_all_nan_object_column_with_nonnull_is_kept(self):
        # object all-NaN but carrying non-null data must be preserved (fallback)
        df = pd.DataFrame({"a": [1.0, 2.0], "b": pd.Series([None, None], dtype=object)})
        self._assert_same(df)

    def test_all_columns_nan_raises(self):
        df = pd.DataFrame({"a": [np.nan, np.nan], "b": [np.nan, np.nan]})
        with pytest.raises(BABDataError):
            dl._drop_all_nan_columns(df)
        with pytest.raises(BABDataError):
            _oracle_drop_all_nan(df)

    def test_empty_passthrough(self):
        df = pd.DataFrame()
        pd.testing.assert_frame_equal(dl._drop_all_nan_columns(df), df)


class TestQualityCampaignEquivalence:
    def _assert_same(self, df, **kw):
        got = dl._run_data_quality_campaign(df, **kw)
        expected = _oracle_quality(df, **kw)
        pd.testing.assert_frame_equal(got, expected)

    def test_numeric_frame_matches_oracle_default(self):
        self._assert_same(_numeric_frame())

    def test_min_finite_fraction_raise_matches_oracle(self):
        df = _numeric_frame()
        df.loc[df.index[:400], "A3"] = np.nan  # ~80% finite
        with pytest.raises(BABDataError, match="insufficient finite data"):
            dl._run_data_quality_campaign(df, min_finite_fraction=0.9)
        with pytest.raises(BABDataError, match="insufficient finite data"):
            _oracle_quality(df, min_finite_fraction=0.9)

    def test_stale_run_raise_matches_oracle(self):
        df = _numeric_frame(n_days=400)
        df["FROZEN"] = 0.5  # 400 identical finite values >= 50
        with pytest.raises(BABDataError, match="Stale/frozen data"):
            dl._run_data_quality_campaign(df)
        with pytest.raises(BABDataError, match="Stale/frozen data"):
            _oracle_quality(df)

    def test_stale_run_none_threshold_skips(self):
        df = _numeric_frame(n_days=400)
        df["FROZEN"] = 0.5
        got = dl._run_data_quality_campaign(df, stale_run_threshold=0)
        pd.testing.assert_frame_equal(got, df)

    def test_mixed_object_frame_falls_back_safely(self):
        # Object dtype exercises the slow per-column fallback branch; it must
        # still complete without raising on coercible object columns.
        df = pd.DataFrame(
            {"a": ["1", "2", "3"], "b": ["1.5", "2.5", "3.5"]}, dtype=object
        )
        out = dl._run_data_quality_campaign(df)
        assert list(out.columns) == ["a", "b"]


class TestSeriesIsParseableEquivalence:
    def _assert_same(self, series):
        assert _series_is_parseable(series) == _oracle_series_is_parseable(series)

    def test_representative_cases_match_oracle(self):
        cases = [
            pd.Series([1, 2, 3.5]),
            pd.Series(["1", "2", "3"]),
            pd.Series(["$1", "2%", "1,000.5", "€3"]),
            pd.Series(["1,5", "1.000,50"]),
            pd.Series([None, np.nan, "NA", "n/a", ""]),
            pd.Series(["abc", "def"]),
            pd.Series(["--", "-"]),
            pd.Series(["1.2.3", "1e", "1..2"]),
            pd.Series(["1", "abc", "2%", "1.2.3", None]),
            pd.Series([None, np.nan]),
            pd.Series([], dtype=object),
            pd.Series(["1", "2", "abc", "def"]),  # 50% boundary
            pd.Series(["1", "abc", "def", "ghi"]),  # below 50%
        ]
        for s in cases:
            self._assert_same(s)

    def test_large_numeric_string_column_matches_oracle(self):
        rng = np.random.default_rng(7)
        s = pd.Series(rng.normal(0, 0.02, 5000).astype(str))
        self._assert_same(s)

    def test_large_object_with_units_and_garbage_matches_oracle(self):
        vals = ["$1.2", "2%", "abc", "1,000.5", "1.5", "1.2.3", None, np.nan, "NA"]
        s = pd.Series(vals * 300)
        self._assert_same(s)


class TestValidationPerformance:
    N_DAYS = 2000
    N_ASSETS = 100

    @pytest.fixture(scope="class")
    def numeric_frame(self):
        return _numeric_frame(n_days=self.N_DAYS, n_assets=self.N_ASSETS)

    def test_drop_all_nan_is_fast(self, numeric_frame):
        _, elapsed = _timed(dl._drop_all_nan_columns, numeric_frame)
        assert elapsed < 2.0, (
            f"_drop_all_nan_columns took {elapsed:.3f}s for "
            f"{numeric_frame.shape}; performance regression"
        )

    def test_quality_campaign_is_fast(self, numeric_frame):
        _, elapsed = _timed(dl._run_data_quality_campaign, numeric_frame)
        assert elapsed < 3.0, (
            f"_run_data_quality_campaign took {elapsed:.3f}s for "
            f"{numeric_frame.shape}; performance regression"
        )