"""Batch 44: targeted data_loader missing-line coverage."""
import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dlmod
from strategies.betting_against_beta.data_loader import BABDataError


class TestBatch44MissingLineTargets:

    def test_validate_returns_coerce_retry_appends_drops_1487_1490_exact(self, monkeypatch):
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=4),
            "BTC": [0.01, 0.02, -0.01, 0.03],
            "ETH": [0.02, -0.01, 0.01, 0.02],
            "JUNK": ["a", "b", "c", "d"],
        })
        calls = {"n": 0}
        orig_coerce = dlmod._coerce_numeric
        def bad_coerce(x):
            calls["n"] += 1
            if calls["n"] == 1:
                raise BABDataError("coerce fail")
            return orig_coerce(x)
        monkeypatch.setattr(dlmod, "_coerce_numeric", bad_coerce)
        # Also ensure _series_is_parseable returns False for JUNK
        orig_parseable = dlmod._series_is_parseable
        def fake_parseable(s):
            try:
                if getattr(s, "name", None) == "JUNK":
                    return False
            except Exception:
                pass
            return orig_parseable(s)
        monkeypatch.setattr(dlmod, "_series_is_parseable", fake_parseable)
        out = dlmod.validate_returns_dataframe(df.copy(), benchmark="BTC")
        assert "BTC" in out.columns
        assert "JUNK" not in out.columns
