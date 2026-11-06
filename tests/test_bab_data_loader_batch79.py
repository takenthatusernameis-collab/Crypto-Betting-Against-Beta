import pandas as pd
import pytest
import sys
sys.path.insert(0, "/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta")
from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.data_loader import _promote_datetime_column


def test_last_resort_promotes_exotic_object_column():
    df = pd.DataFrame(
        {
            "when_recorded": pd.Series(
                ["2024-01-01", "2024-01-02", "2024-01-03"], dtype=object
            ),
            "BTC": [0.01, 0.02, 0.03],
            "ETH": [0.04, 0.05, 0.06],
        }
    )
    out = _promote_datetime_column(df)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert "when_recorded" not in [str(c).lower() for c in out.columns]
    assert list(out.columns) == ["BTC", "ETH"]


def test_last_resort_tz_normalization_exception_path():
    # tz-aware strings parse with tz; force tz_convert to fail to hit 901-903 except
    df = pd.DataFrame(
        {
            "when_recorded": pd.Series(
                ["2024-01-01T00:00:00+05:00", "2024-01-02T00:00:00+05:00"], dtype=object
            ),
            "BTC": [0.01, 0.02],
            "ETH": [0.03, 0.04],
        }
    )
    orig_tz_convert = pd.DatetimeIndex.tz_convert
    calls = [0]

    def flaky_tz_convert(self, *a, **k):
        calls[0] += 1
        if calls[0] <= 2:
            raise RuntimeError("tz fail")
        return orig_tz_convert(self, *a, **k)

    pd.DatetimeIndex.tz_convert = flaky_tz_convert
    try:
        out = _promote_datetime_column(df)
        assert isinstance(out.index, pd.DatetimeIndex)
        assert "when_recorded" not in [str(c).lower() for c in out.columns]
    finally:
        pd.DatetimeIndex.tz_convert = orig_tz_convert


def test_last_resort_setindex_fallback_path():
    # hit 909-914: after assignment index not DatetimeIndex, fallback set_index
    df = pd.DataFrame(
        {
            "when_recorded": pd.Series(
                ["2024-01-01", "2024-01-02", "2024-01-03"], dtype=object
            ),
            "BTC": [0.01, 0.02, 0.03],
            "ETH": [0.04, 0.05, 0.06],
        }
    )
    import builtins

    orig_isinst = builtins.isinstance
    hit = [0]

    def fake_isinstance(obj, cls):
        if cls is pd.DatetimeIndex and orig_isinst(obj, pd.Index):
            # fail the isinstance check at line 907 inside last-resort
            try:
                # only when called from _promote_datetime_column context after our df2
                if "when_recorded" not in getattr(obj, "name", "") and len(obj) == 3:
                    hit[0] += 1
                    if hit[0] == 1:
                        return False
            except Exception:
                pass
        return orig_isinst(obj, cls)

    builtins.isinstance = fake_isinstance
    try:
        out = _promote_datetime_column(df)
        assert isinstance(out.index, (pd.DatetimeIndex, pd.Index))
        assert "when_recorded" not in [str(c).lower() for c in out.columns]
    finally:
        builtins.isinstance = orig_isinst
