"""Batch 96: targeted probes for remaining data_loader miss lines.

Covers 1319-1320 (quality-check to_numeric/to_numpy fallback).
Other probes (268-269, 403-404, 43-44, 953) are structural-dead; see
docs/unreachable_proofs.md batch96 notes.
"""
from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pandas as pd

from strategies.betting_against_beta import data_loader as dl


def test_1319_1320_quality_to_numeric_to_numpy_raises_falls_back():
    """1319-1320: pd.to_numeric(...).to_numpy raises -> fallback to_series to_numpy."""
    df = pd.DataFrame(
        {"BTC": [0.01, 0.02, np.nan], "ETH": [0.03, 0.04, 0.05]},
        index=pd.date_range("2021-01-01", periods=3, tz="UTC"),
    )
    orig = pd.to_numeric

    class BadNum:
        def to_numpy(self, *a, **k):
            raise RuntimeError("to_numpy boom")

    def fake_to_numeric(arg, *a, **k):
        # Force the fallback only for the BTC column quality pass.
        if getattr(arg, "name", None) == "BTC":
            return BadNum()
        return orig(arg, *a, **k)

    with patch("strategies.betting_against_beta.data_loader.pd.to_numeric", side_effect=fake_to_numeric):
        out = dl.validate_returns_dataframe(df, benchmark="BTC", min_rows=1, quality=True)
    assert list(out.columns) == ["BTC", "ETH"]
    assert len(out) == 3
