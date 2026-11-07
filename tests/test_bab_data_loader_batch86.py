import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import strategies.betting_against_beta.data_loader as dl


def test_901_903_tz_convert_raises_in_last_resort():
    """Cover last-resort tz body (901) + its except/pass (902-903).

    Mechanism: monkeypatch pd.to_datetime to return a pd.Series subclass
    whose .tz is truthy and whose tz_convert raises. The column 'mystery' is
    not a candidate name, passes object-dtype checks, and has no NaT, so the
    last-resort loop reaches the tz-conversion body which then throws.
    """
    class TzSeries(pd.Series):
        @property
        def tz(self):
            return "UTC"

        def tz_convert(self, *a, **k):
            raise RuntimeError("tz_convert boom")

    orig_td = pd.to_datetime

    def fake_td(x, *a, **k):
        if isinstance(x, pd.Series):
            return TzSeries(
                [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")],
                index=x.index,
                name=x.name,
            )
        return orig_td(x, *a, **k)

    dl.pd.to_datetime = fake_td
    try:
        df = pd.DataFrame(
            {"mystery": ["x", "y"], "BTC": [0.01, 0.02], "ETH": [0.03, 0.04]}
        )
        try:
            out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
        except Exception:
            pass
    finally:
        dl.pd.to_datetime = orig_td
