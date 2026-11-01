"""Targeted edge-branch coverage for beta.py (P0, 89%).

Hits the defensive branches the existing suite does not reach:
empty rolling inputs, disjoint Series alignment, and degenerate fast-path
inputs. Real assertions on shape/dtype/finiteness only.
"""

import numpy as np
import pandas as pd

from strategies.betting_against_beta import beta


class TestRollingBetaEmptyInput:
    def test_rolling_beta_empty_arrays(self):
        # n == 0 -> empty NaN-filled array via the series path
        res = beta.rolling_beta(np.array([], dtype=float), np.array([], dtype=float))
        assert isinstance(res, np.ndarray)
        assert res.shape == (0,)

    def test_rolling_beta_single_point_below_min_obs(self):
        res = beta.rolling_beta([0.01], [0.005], window=90, min_obs=60)
        assert res.shape == (1,)
        assert np.isnan(res[0])

    def test_rolling_beta_degenerate_constant_benchmark(self):
        # Constant benchmark -> denom ~ 0 -> degenerate -> NaN (undefined beta),
        # consistent with calculate_beta / calculate_beta_fast /
        # metrics.strategy_beta which all return NaN for a zero-variance
        # benchmark.  A synthetic 0.0 would be treated as a real (low) beta by
        # the ranking and silently corrupt the long/short selection.
        res = beta.rolling_beta([0.01, 0.02, 0.03, 0.04], [0.01, 0.01, 0.01, 0.01],
                                window=4, min_obs=1)
        assert np.all(np.isnan(res))


class TestCalculateBetaAlignment:
    def test_series_alignment_disjoint_indexes_returns_nan(self):
        # unequal lengths + Series -> alignment branch; disjoint indexes -> empty -> np.nan (beta.py:85)
        asset = pd.Series([0.01, 0.02], index=[0, 1])
        bench = pd.Series([0.005, 0.01, 0.015], index=[10, 11, 12])
        assert np.isnan(beta.calculate_beta(asset, bench))

    def test_series_alignment_one_common_point_below_min_obs(self):
        asset = pd.Series([0.01, 0.02], index=[0, 1])
        bench = pd.Series([0.005, 0.01], index=[1, 2])
        assert np.isnan(beta.calculate_beta(asset, bench, min_obs=5))

    def test_numpy_array_length_mismatch_truncates(self):
        asset = np.array([0.01, 0.02, 0.03, 0.04])
        bench = np.array([0.005, 0.01])
        b = beta.calculate_beta(asset, bench)
        assert np.isfinite(b)


class TestCalculateBetaFast:
    def test_fast_all_non_finite_returns_nan(self):
        assert np.isnan(beta.calculate_beta_fast([np.nan, np.nan], [0.01, 0.02]))

    def test_fast_empty_input_returns_nan(self):
        assert np.isnan(beta.calculate_beta_fast([], []))

    def test_fast_constant_benchmark(self):
        # Zero-variance benchmark -> NaN (undefined beta), consistent with
        # calculate_beta and metrics.strategy_beta.
        assert np.isnan(beta.calculate_beta_fast([0.01, 0.02, 0.03], [0.01, 0.01, 0.01]))

    def test_fast_non_finite_result_returns_nan(self):
        # Extremely ill-conditioned slope collapses to non-finite -> NaN
        # (undefined beta), consistent with calculate_beta which also returns
        # NaN for a non-finite lstsq result (beta.py:137-138).
        b = beta.calculate_beta_fast([1e308, 2e308, 3e308], [1.0, 2.0, 3.0])
        assert np.isnan(b)
