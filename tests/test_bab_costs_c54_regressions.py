"""C54 Step 2 regression suite for ``strategies/betting_against_beta.costs``.

Covers the narrowing of the broad ``except Exception`` in
``apply_costs`` (costs.py:281) to ``except TypeError``.

Before this change the cost-adjustment block swallowed *every* exception
(including a corrupt/misaligned ``tc`` index) and returned ``returns``
unchanged — a silent wrong-data path.  After the change only the genuine
non-subtractable-returns case (TypeError on object-dtype arithmetic) falls
through; any other failure in the block now surfaces to the caller.
"""

from __future__ import annotations

from unittest import mock

import pandas as pd
import pytest

from strategies.betting_against_beta.costs import apply_costs


def _idx(n: int = 3) -> pd.DatetimeIndex:
    return pd.date_range("2023-01-01", periods=n, freq="D")


def test_apply_costs_surfaces_non_typeerror_in_adjustment_block():
    """A non-TypeError raised inside the adjustment block must propagate.

    Previously this was silently swallowed by ``except Exception: pass`` and
    ``returns`` was returned unchanged — masking a corrupt cost index.
    """
    returns = pd.DataFrame({"x": [0.01, 0.02, 0.03]}, index=_idx())
    tc = pd.Series([0.001, 0.001, 0.001], index=_idx())
    with (
        mock.patch.object(pd.Series, "reindex", side_effect=ValueError("corrupt index")),
        pytest.raises(ValueError, match="corrupt index"),
    ):
        apply_costs(returns, transaction_costs=tc)


def test_apply_costs_object_dtype_returns_still_falls_through():
    """The narrowed ``except TypeError`` preserves the object-dtype fallback.

    A non-numeric returns object cannot be cost-subtracted; it must still be
    returned unchanged (the valid-path behavior the TypeError guard exists for).
    """
    returns = pd.Series(["a", "b", "c"], index=_idx())
    tc = pd.Series([0.001, 0.001, 0.001], index=_idx())
    out = apply_costs(returns, transaction_costs=tc)
    pd.testing.assert_series_equal(out, returns)


def test_apply_costs_valid_dataframe_adjustment_unchanged():
    """Valid path: DataFrame with a single numeric column is cost-adjusted."""
    returns = pd.DataFrame({"x": [0.01, 0.02, 0.03]}, index=_idx())
    tc = pd.Series([0.001, 0.001, 0.001], index=_idx())
    out = apply_costs(returns, transaction_costs=tc)
    assert out["x"].iloc[0] == pytest.approx(0.009)


def test_apply_costs_valid_series_adjustment_unchanged():
    """Valid path: Series returns are cost-adjusted."""
    returns = pd.Series([0.01, 0.02, 0.03], index=_idx())
    tc = pd.Series([0.001, 0.001, 0.001], index=_idx())
    out = apply_costs(returns, transaction_costs=tc)
    assert out.iloc[0] == pytest.approx(0.009)


def test_apply_costs_zero_costs_returns_unchanged():
    """No transaction_costs and no weights -> returns returned as-is."""
    returns = pd.Series([0.01, 0.02, 0.03], index=_idx())
    out = apply_costs(returns)
    pd.testing.assert_series_equal(out, returns)
