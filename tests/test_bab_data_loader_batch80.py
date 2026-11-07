import pandas as pd
import pytest
from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.data_loader import _run_data_quality_campaign


def test_dq_campaign_tz_localize_fallback_1257_1258():
    """Force tz_convert AND tz_localize to fail so the 1257-1258 except fires.

    Reachable via a tz-aware DatetimeIndex where both ``tz_convert("UTC")``
    and ``tz_localize(None)`` raise (tight scoped monkeypatch of
    ``DatetimeIndex.tz_convert`` / ``tz_localize``). The outer except at
    1257-1258 swallows and the index keeps its tz.
    """
    idx = pd.date_range("2024-01-01", periods=5, freq="D", tz="UTC")
    df = pd.DataFrame(
        {"BTC": [0.01, 0.02, 0.03, 0.04, 0.05], "ETH": [0.02, 0.03, 0.04, 0.05, 0.06]},
        index=idx,
    )
    orig_tc = pd.DatetimeIndex.tz_convert
    orig_tl = pd.DatetimeIndex.tz_localize

    def boom_tc(self, *a, **k):
        raise RuntimeError("tz_convert boom")

    def boom_tl(self, *a, **k):
        raise RuntimeError("tz_localize boom")

    pd.DatetimeIndex.tz_convert = boom_tc
    pd.DatetimeIndex.tz_localize = boom_tl
    try:
        out = _run_data_quality_campaign(df.copy())
        assert isinstance(out.index, pd.DatetimeIndex)
        assert out.index.tz is not None
    finally:
        pd.DatetimeIndex.tz_convert = orig_tc
        pd.DatetimeIndex.tz_localize = orig_tl