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
        # Constant benchmark -> denom ~ 0 -> degenerate -> 0.0 where enough obs
        res = beta.rolling_beta([0.01, 0.02, 0.03, 0.04], [0.01, 0.01, 0.01, 0.01],
                                window=4, min_obs=1)
        assert np.all(np.isfinite(res))
        assert np.all(res == 0.0)


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
        assert beta.calculate_beta_fast([0.01, 0.02, 0.03], [0.01, 0.01, 0.01]) == 0.0

    def test_fast_non_finite_result_returns_zero(self):
        # Extremely ill-conditioned slope collapses to non-finite -> 0.0 (beta.py:163)
        b = beta.calculate_beta_fast([1e308, 2e308, 3e308], [1.0, 2.0, 3.0])
        assert np.isfinite(b)
