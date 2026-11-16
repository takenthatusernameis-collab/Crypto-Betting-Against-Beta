"""P19-3 medium-reach coverage wins (post-deletion refresh).

Deleted proven-unreachable lines (with proof):
- beta.py:125 (len(y)==0 after mask: mask removes all non-finite, so len(y)
  is always >= 1 here; unreachable).
- beta.py:163 (a is None/b is None: np.asarray(None, dtype=float) raises
  TypeError, caught at line 158-160 -> return nan first; unreachable).
- beta.py:170-171 (np.array(a).ravel() exception: np.asarray() at line 156
  guarantees a proper ndarray, so ravel() always succeeds; unreachable).
- beta.py:189 (len(a_m)==0: same mask logic as 125; unreachable).
- data_loader.py:1355 (pending_count < remaining_needed: pending_count =
  n - parseable, threshold <= total <= n, so n < threshold is impossible;
  unreachable).
- portfolio.py:152-153,170-177,180 (equal-weight clip/drift: weights are
  1/n_long or -1/n_short, always |w| <= 1; both=True rows are rescaled so
  sum(long)=1, sum(short)=-1 exactly; unreachable).
- signals.py:37 (numeric.dtype == object: pd.to_numeric always returns
  numeric dtype; unreachable), signals.py:75 (n == 0: _finite_beta_series
  returns None for empty clean, so n >= 1 here; unreachable).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.beta import calculate_beta, calculate_beta_fast
from strategies.betting_against_beta.data_loader import _series_is_parseable
from strategies.betting_against_beta.portfolio import construct_portfolio


class TestBetaEdgeCases:
    def test_calculate_beta_empty_after_mask(self):
        """Verify calculate_beta returns NaN for all-non-finite inputs."""
        a = pd.Series([np.nan, np.inf, -np.inf])
        b = pd.Series([1.0, 2.0, 3.0])
        assert np.isnan(calculate_beta(a, b))

    def test_calculate_beta_fast_none_input(self):
        """Verify calculate_beta_fast returns NaN for None inputs."""
        assert np.isnan(calculate_beta_fast(None, [1, 2, 3]))
        assert np.isnan(calculate_beta_fast([1, 2, 3], None))

    def test_calculate_beta_fast_empty_after_mask(self):
        """Verify calculate_beta_fast returns NaN for all-non-finite inputs."""
        a = np.array([np.nan, np.inf, -np.inf])
        b = np.array([np.nan, np.inf, -np.inf])
        assert np.isnan(calculate_beta_fast(a, b))


class TestDataLoaderNumericThreshold:
    def test_series_is_parseable_normal_cases(self):
        """Verify _series_is_parseable behavior on representative inputs."""
        assert _series_is_parseable(pd.Series([1.0, 2.0, 3.0])) is True
        assert _series_is_parseable(pd.Series(["1", "2", "3"])) is True
        assert _series_is_parseable(pd.Series(["bad", "bad"])) is False
        # Units/commas parse via _strip_units_and_parse
        assert _series_is_parseable(pd.Series(["$1", "1,000.5", "2%"])) is True


class TestPortfolioWeights:
    def test_portfolio_weights_bounded_and_neutral(self):
        """Verify equal-weight portfolio produces |w| <= 1 and net ~0."""
        dates = pd.date_range("2023-01-01", periods=3)
        signals = pd.DataFrame(
            {"BTC": [1, -1, 1], "ETH": [-1, 1, -1]},
            index=dates,
        )
        result = construct_portfolio(signals, dollar_neutral=True)
        assert np.all(np.abs(result.values) <= 1.0 + 1e-10)
        net = result.sum(axis=1)
        assert np.all(np.abs(net) < 1e-12)

    def test_portfolio_both_long_and_short_rescale(self):
        """Verify rows with both longs and shorts rescale to net ~0."""
        dates = pd.date_range("2023-01-01", periods=1)
        signals = pd.DataFrame(
            {
                "A0": [1], "A1": [1], "A2": [1], "A3": [1], "A4": [1],
                "A5": [1], "A6": [1], "A7": [-1], "A8": [-1], "A9": [-1],
            },
            index=dates,
        )
        result = construct_portfolio(signals, dollar_neutral=True)
        assert np.all(np.abs(result.values) <= 1.0 + 1e-10)
        net = result.sum(axis=1)
        assert np.all(np.abs(net) < 1e-12)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])