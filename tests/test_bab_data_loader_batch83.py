import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError


class EmptyBoomDF(pd.DataFrame):
    _n = 0

    @property
    def _constructor(self):
        return EmptyBoomDF

    @property
    def empty(self):
        EmptyBoomDF._n += 1
        if EmptyBoomDF._n == 1:
            return False
        raise RuntimeError("empty boom")


def test_1591_1592_csv_empty_after_read_raises():
    """Line 1591-1592: df.empty raises non-BABDataError on second check."""
    orig = pd.read_csv

    def fake_read(*a, **k):
        return EmptyBoomDF({"date": ["2024-01-01"], "BTC": [0.01]})

    pd.read_csv = fake_read
    EmptyBoomDF._n = 0
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
        f.write("date,BTC\n2024-01-01,0.01\n")
        p = f.name
    try:
        with pytest.raises(Exception):
            dl.load_returns_from_csv(p, benchmark="BTC", quality=False)
    finally:
        pd.read_csv = orig
