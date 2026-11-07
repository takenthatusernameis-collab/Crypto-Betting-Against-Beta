"""Batch 93: dayfirst last-ditch block (227-233, 245) via np.datetime64('NaT') passthrough.

The production `_coerce_to_datetime_scalar` returns `pd.NaT` (does NOT raise) for
`np.datetime64('NaT')` — verified directly. When an object index mixes valid date
strings with `np.datetime64('NaT')`, the elementwise coercion at 218-224 succeeds
(returning NaT for the NaT entry), so `df.index.isna().any()` becomes True and the
dayfirst last-ditch block at 227-247 is entered for the first time in the aggregate.
"""
import numpy as np
import pandas as pd

from strategies.betting_against_beta import data_loader as dl
from strategies.betting_against_beta.data_loader import _normalize_index


def test_227_245_dayfirst_block_via_np_datetime64_nat():
    # Object index mixing valid ISO dates with np.datetime64('NaT').
    # The real coercer returns NaT (not raise) for np.datetime64('NaT'), so the
    # NaT guard at 225 is True and the dayfirst block (227-247) is entered.
    idx = pd.Index(
        ["2021-01-01", np.datetime64("NaT"), "2021-01-03"], dtype=object
    )
    df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=idx)
    out = _normalize_index(df.copy())
    assert isinstance(out.index, pd.DatetimeIndex)
    # NaT row dropped at 291-295; valid rows survive.
    assert len(out) == 2
    assert list(out.index) == [
        pd.Timestamp("2021-01-01"),
        pd.Timestamp("2021-01-03"),
    ]


def test_coercer_nat_passthrough_contract():
    # Documented contract: np.datetime64('NaT') -> pd.NaT (no raise); pd.NaT raises.
    assert pd.isna(dl._coerce_to_datetime_scalar(np.datetime64("NaT")))
    try:
        dl._coerce_to_datetime_scalar(pd.NaT)
        raise AssertionError("expected pd.NaT to raise")
    except ValueError:
        pass


def test_92_93_outer_except_via_series_iter_raises():
    # Line 92-93: inner `except Exception: pass` in _coerce_series_to_datetime_index.
    # `coerced` is a pd.Series subclass whose __iter__ raises, escaping the
    # elementwise loop at 76-91 (the only unguarded statement there) and reaching
    # the inner except at 92-93. Execution then continues at 94-97 and returns True.
    class BadIter(pd.Series):
        def __iter__(self):
            raise RuntimeError("boom-iter")

    df = pd.DataFrame({"date": [1, 2], "BTC": [1.0, 2.0]})
    coerced = BadIter([pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")])
    assert dl._coerce_series_to_datetime_index(df, "date", coerced) is True