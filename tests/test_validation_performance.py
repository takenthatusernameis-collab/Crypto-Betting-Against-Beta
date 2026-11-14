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
        raise BABDataError("All columns are entirely NaN; no usable return data remains.")
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
        total = len(arr)
        if total > 0 and float(min_finite_fraction) > 0:
            frac = finite_count / total if total > 0 else 0.0
            if frac < float(min_finite_fraction):
                raise BABDataError(
                    f"Column '{col}' has insufficient finite data: "
                    f"{frac:.2%} < {float(min_finite_fraction):.2%}"
                )
        if (
            stale_run_threshold is not None
            and int(stale_run_threshold) > 0
            and finite_count >= int(stale_run_threshold)
        ):
            max_allowed_stale = max(int(stale_run_threshold), 50)
            max_run = dl._max_consecutive_equal_finite(arr)
            if max_run >= max_allowed_stale:
                raise BABDataError(
                    f"Stale/frozen data detected in column '{col}': "
                    f"{max_run} consecutive equal values"
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
        df = pd.DataFrame({"a": ["1", "2", "3"], "b": ["1.5", "2.5", "3.5"]}, dtype=object)
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


class TestMaxConsecutiveEqualFiniteOracle:
    """Randomized oracle for the bincount-based run-length detector (1-D)."""

    @staticmethod
    def _reference(arr):
        arr = np.asarray(arr, dtype=float)
        best = 0
        run = 0
        prev = None
        prev_finite = False
        for v in arr:
            fin = bool(np.isfinite(v))
            if fin and prev_finite and v == prev:
                run += 1
            else:
                run = 1
            if fin and run > best:
                best = run
            prev = v
            prev_finite = fin
        return best

    def test_random_arrays_match_oracle(self):
        rng = np.random.default_rng(1234)
        for _ in range(300):
            n = int(rng.integers(0, 60))
            arr = rng.normal(0.0, 1.0, size=n)
            if n:
                arr[rng.random(n) < 0.2] = np.nan
                arr[rng.random(n) < 0.1] = np.inf
                arr[rng.random(n) < 0.1] = -np.inf
                for _ in range(3):
                    i0 = int(rng.integers(0, n))
                    i1 = int(rng.integers(i0, n))
                    arr[i0 : i1 + 1] = 0.5
            assert dl._max_consecutive_equal_finite(arr) == self._reference(arr)

    def test_large_constant_and_alternating(self):
        assert dl._max_consecutive_equal_finite(np.zeros(5000)) == 5000
        assert dl._max_consecutive_equal_finite(np.tile([1.0, 2.0], 2500)) == 1


class TestMaxConsecutiveEqualFiniteFrameOracle:
    """Randomized oracle for the vectorized per-column run-length detector."""

    @staticmethod
    def _reference_frame(arr):
        arr = np.asarray(arr, dtype=float)
        if arr.ndim != 2:
            return np.array([dl._max_consecutive_equal_finite(arr)], dtype=np.int64)
        return np.array(
            [dl._max_consecutive_equal_finite(arr[:, j]) for j in range(arr.shape[1])],
            dtype=np.int64,
        )

    def test_random_frames_match_per_column_oracle(self):
        rng = np.random.default_rng(2026)
        for _ in range(200):
            n = int(rng.integers(0, 300))
            m = int(rng.integers(1, 20))
            arr = rng.normal(0.0, 1.0, size=(n, m))
            if n:
                arr[rng.random((n, m)) < 0.2] = np.nan
                arr[rng.random((n, m)) < 0.1] = np.inf
                arr[rng.random((n, m)) < 0.1] = -np.inf
                for _ in range(3):
                    j = int(rng.integers(0, m))
                    i0 = int(rng.integers(0, n))
                    i1 = int(rng.integers(i0, n))
                    arr[i0 : i1 + 1, j] = 0.5
            got = dl._max_consecutive_equal_finite_frame(arr)
            expected = self._reference_frame(arr)
            assert got.shape == expected.shape
            assert np.array_equal(got, expected)

    def test_edge_cases(self):
        assert np.array_equal(
            dl._max_consecutive_equal_finite_frame(np.zeros((5, 3))), np.array([5, 5, 5])
        )
        assert np.array_equal(
            dl._max_consecutive_equal_finite_frame(np.full((4, 2), np.nan)), np.array([0, 0])
        )
        assert np.array_equal(
            dl._max_consecutive_equal_finite_frame(np.tile([[1.0, 2.0]], (3, 1))),
            np.array([3, 3]),
        )
        # 1-D passthrough still works
        assert np.array_equal(
            dl._max_consecutive_equal_finite_frame(np.array([1.0, 1.0, np.nan, 1.0])),
            np.array([2]),
        )
        assert dl._max_consecutive_equal_finite_frame(np.zeros((0, 3))).shape == (3,)


class TestNumericFrameStaleBatchEquivalence:
    """The numeric fast path must raise on the same columns as the per-column oracle."""

    def _stale_columns(self, df, stale_run_threshold=None):
        try:
            dl._run_data_quality_campaign(df, stale_run_threshold=stale_run_threshold)
            return None
        except BABDataError as exc:
            return str(exc)

    def _oracle_stale_columns(self, df, stale_run_threshold=None):
        try:
            _oracle_quality(df, stale_run_threshold=stale_run_threshold)
            return None
        except BABDataError as exc:
            return str(exc)

    def test_stale_detection_matches_oracle(self):
        df = _numeric_frame(n_days=400, n_assets=10)
        df["FROZEN"] = 0.5
        df["ALSO_FROZEN"] = 1.0
        assert self._stale_columns(df) == self._oracle_stale_columns(df)

    def test_stale_multi_column_lowest_index_wins(self):
        df = _numeric_frame(n_days=400, n_assets=10)
        cols = list(df.columns)
        # Force stale runs in two columns; highest-index first in assignment order
        df[cols[7]] = 0.5
        df[cols[2]] = 1.0
        with pytest.raises(BABDataError) as excinfo:
            dl._run_data_quality_campaign(df)
        msg = str(excinfo.value)
        assert f"column '{cols[2]}'" in msg
        assert f"column '{cols[7]}'" not in msg
        # oracle must agree
        assert self._stale_columns(df) == self._oracle_stale_columns(df)

    def test_stale_run_at_threshold_boundary(self):
        n = 60
        idx = pd.bdate_range("2020-01-01", periods=n)
        rng = np.random.default_rng(1)
        df = pd.DataFrame(rng.normal(0, 0.01, size=(n, 2)), index=idx, columns=["A", "B"])
        # exactly threshold run in B only
        df.loc[df.index[:50], "B"] = 0.5
        with pytest.raises(BABDataError, match="column 'B'"):
            dl._run_data_quality_campaign(df, stale_run_threshold=50)
        # below threshold: 49-run should not trigger when threshold is 50
        df2 = pd.DataFrame(rng.normal(0, 0.01, size=(n, 2)), index=idx, columns=["A", "B"])
        df2.loc[df2.index[:49], "B"] = 0.5
        out = dl._run_data_quality_campaign(df2, stale_run_threshold=50)
        pd.testing.assert_frame_equal(out, df2)

    def test_stale_with_nans_and_inf_splits_runs(self):
        n = 200
        idx = pd.bdate_range("2020-01-01", periods=n)
        rng = np.random.default_rng(0)
        df = pd.DataFrame(rng.normal(0, 0.01, size=(n, 3)), index=idx, columns=["A", "B", "C"])
        # long equal run interrupted by NaN and inf so no segment >= 50
        df.loc[df.index[:30], "B"] = 1.0
        df.loc[df.index[30], "B"] = np.nan
        df.loc[df.index[31:61], "B"] = 1.0
        df.loc[df.index[61], "B"] = np.inf
        df.loc[df.index[62:92], "B"] = 1.0
        out = dl._run_data_quality_campaign(df)
        pd.testing.assert_frame_equal(out, df)

    def test_stale_vectorized_matches_oracle_randomized(self):
        rng = np.random.default_rng(20261113)
        for seed in range(40):
            n = int(rng.integers(60, 180))
            m = int(rng.integers(2, 8))
            idx = pd.bdate_range("2019-01-01", periods=n)
            data = rng.normal(0, 0.02, size=(n, m))
            cols = [f"C{i}" for i in range(m)]
            df = pd.DataFrame(data, index=idx, columns=cols)
            # inject some NaNs/inf and occasional long runs
            mask_nan = rng.random((n, m)) < 0.05
            df = df.mask(mask_nan)
            for _ in range(2):
                j = int(rng.integers(0, m))
                i0 = int(rng.integers(0, max(1, n - 10)))
                run = int(rng.integers(1, 70))
                df.iloc[i0 : min(n, i0 + run), j] = 0.123
            try:
                got = dl._run_data_quality_campaign(df)
                got_err = None
            except BABDataError as exc:
                got = None
                got_err = str(exc)
            try:
                exp = _oracle_quality(df)
                exp_err = None
            except BABDataError as exc:
                exp = None
                exp_err = str(exc)
            assert got_err == exp_err, f"seed={seed} got={got_err} exp={exp_err}"
            if got is not None:
                pd.testing.assert_frame_equal(got, exp)


class TestNumericFrameFastPathEquivalence:
    """Pin the numeric fast path in the campaign against the per-column oracle."""

    def test_all_numeric_frame_uses_numeric_path_matches_oracle(self):
        df = _numeric_frame(n_days=500, n_assets=40)
        got = dl._run_data_quality_campaign(df)
        expected = _oracle_quality(df)
        pd.testing.assert_frame_equal(got, expected)

    def test_numeric_stale_column_raise_matches_oracle(self):
        df = _numeric_frame(n_days=400, n_assets=10)
        df["FROZEN"] = 0.5
        with pytest.raises(BABDataError, match="Stale/frozen data"):
            dl._run_data_quality_campaign(df)
        with pytest.raises(BABDataError, match="Stale/frozen data"):
            _oracle_quality(df)

    def test_numeric_mixed_nan_and_finite_matches_oracle(self):
        df = _numeric_frame(n_days=300, n_assets=20)
        df.loc[df.index[:100], "A0"] = np.nan
        df.loc[df.index[:50], "A1"] = np.inf
        got = dl._run_data_quality_campaign(df, min_finite_fraction=0.5)
        expected = _oracle_quality(df, min_finite_fraction=0.5)
        pd.testing.assert_frame_equal(got, expected)

    def test_short_rows_numeric(self):
        df = _numeric_frame(n_days=1, n_assets=3)
        got = dl._run_data_quality_campaign(df)
        expected = _oracle_quality(df)
        pd.testing.assert_frame_equal(got, expected)


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

    def test_validate_returns_is_fast(self, numeric_frame):
        _, elapsed = _timed(dl.validate_returns_dataframe, numeric_frame)
        assert elapsed < 1.0, (
            f"validate_returns_dataframe took {elapsed:.3f}s for "
            f"{numeric_frame.shape}; performance regression"
        )
