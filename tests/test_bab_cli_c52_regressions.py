"""C52 regression tests: proven gaps found by adversarial probes."""

from __future__ import annotations

import types

import pandas as pd

from strategies.betting_against_beta.cli import _extract_cumulative


def test_extract_cumulative_dataframe_no_cum_column_returns_last_scalar():
    """C52-012: a DataFrame backtest with no cumulative/cum column should not
    be returned as a whole DataFrame (ambiguous truth value); return last scalar."""
    result = types.SimpleNamespace(
        backtest=pd.DataFrame({"other": [1.0, 1.3], "returns": [0.0, 0.1]})
    )
    assert _extract_cumulative(result) == 0.1


def test_extract_cumulative_dataframe_single_non_cum_column():
    result = types.SimpleNamespace(backtest=pd.DataFrame({"other": [1.0, 1.3]}))
    assert _extract_cumulative(result) == 1.3
