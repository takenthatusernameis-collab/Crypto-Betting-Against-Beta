"""Quality-safety contract tests for ``validate_returns_dataframe``.

These pin the trading-critical data-quality contract:

* explicit ``stale_run_threshold`` / ``max_gap_days`` / ``max_return_abs`` are
  honored (the old ``max(threshold, 50)`` floor silently disabled them);
* ``quality`` may be a ``dict`` of per-call overrides and those overrides are
  applied (previously the dict was silently dropped);
* ``quality=True`` applies the documented safe defaults (20.0 / 7.0 / 3) rather
  than the old lenient 10000 / 3650 / 50;
* ``quality=False`` remains an explicit opt-out.

On the pre-fix revision every "rejects" assertion below failed because the
guards were inert. They now pass.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import (
    BABDataError,
    _run_data_quality_campaign,
    validate_returns_dataframe,
)


def _frozen_and_live(n: int = 8) -> pd.DataFrame:
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    live = np.linspace(0.02, 0.02 + 0.01 * n, n)
    return pd.DataFrame({"BTC": [0.01] * n, "ETH": live}, index=idx)


class TestExplicitThresholdHonored:
    def test_explicit_stale_run_threshold_rejects_short_run(self):
        df = _frozen_and_live(8)  # BTC has an 8-long frozen run
        with pytest.raises(BABDataError, match="Stale/frozen data"):
            validate_returns_dataframe(
                df, benchmark="ETH", quality=True, stale_run_threshold=3
            )

    def test_helper_honors_explicit_threshold_without_floor(self):
        df = _frozen_and_live(8)
        with pytest.raises(BABDataError, match="Stale/frozen data"):
            _run_data_quality_campaign(df, stale_run_threshold=3)

    def test_threshold_above_run_does_not_raise(self):
        df = _frozen_and_live(8)  # 8-long frozen run
        out = validate_returns_dataframe(
            df, benchmark="ETH", quality=True, stale_run_threshold=50
        )
        assert "BTC" in out.columns


class TestDictQualityOverrides:
    def test_dict_stale_run_threshold_is_honored(self):
        df = _frozen_and_live(8)
        with pytest.raises(BABDataError, match="Stale/frozen data"):
            validate_returns_dataframe(
                df, benchmark="ETH", quality={"stale_run_threshold": 3}
            )

    def test_dict_max_gap_days_is_honored(self):
        idx = list(pd.date_range("2020-01-01", periods=5, freq="D"))
        idx[3] = idx[2] + pd.Timedelta(days=30)
        df = pd.DataFrame(
            {"BTC": np.linspace(0.01, 0.05, 5), "ETH": np.linspace(0.02, 0.06, 5)},
            index=idx,
        )
        with pytest.raises(BABDataError, match="Data gap too large"):
            validate_returns_dataframe(
                df, benchmark="ETH", quality={"max_gap_days": 7}
            )

    def test_dict_max_return_abs_is_honored(self):
        df = _frozen_and_live(8)
        df.iloc[2, 0] = 100.0  # 10000% return in BTC
        with pytest.raises(BABDataError, match="Implausible return"):
            validate_returns_dataframe(
                df, benchmark="ETH", quality={"max_return_abs": 20.0}
            )

    def test_dict_duplicate_timestamps_allowed_drops_duplicates(self):
        idx = pd.to_datetime(["2020-01-01", "2020-01-01", "2020-01-02"])
        df = pd.DataFrame(
            {"BTC": [0.01, 0.02, 0.03], "ETH": [0.02, 0.03, 0.04]}, index=idx
        )
        out = validate_returns_dataframe(
            df, benchmark="ETH", quality={"allow_duplicate_timestamps": True}
        )
        assert isinstance(out, pd.DataFrame)
        assert not out.index.has_duplicates

    def test_explicit_kwarg_takes_precedence_over_dict(self):
        # Dict asks for a strict gap but the explicit kwarg (disabled) must win.
        idx = list(pd.date_range("2020-01-01", periods=5, freq="D"))
        idx[3] = idx[2] + pd.Timedelta(days=30)
        df = pd.DataFrame(
            {"BTC": np.linspace(0.01, 0.05, 5), "ETH": np.linspace(0.02, 0.06, 5)},
            index=idx,
        )
        out = validate_returns_dataframe(
            df,
            benchmark="ETH",
            quality={"max_gap_days": 7},
            max_gap_days=float("inf"),
        )
        assert "BTC" in out.columns


class TestSafeDefaultsAreEnforced:
    """P17-1: the default ``quality=True`` contract is now strict (20.0 / 7.0 / 3).

    The old ``TestLenientDefaultsAreHonored`` asserted the lax 10000/3650/50
    behavior; those assertions are inverted here. Callers may still opt out via
    ``quality=False`` or explicit ``math.inf``/``0`` values.
    """

    def test_default_rejects_frozen_column(self):
        df = _frozen_and_live(8)  # BTC has an 8-long frozen run
        with pytest.raises(BABDataError, match="Stale/frozen data"):
            validate_returns_dataframe(df, benchmark="ETH", quality=True)

    def test_default_rejects_implausible_return(self):
        df = _frozen_and_live(8)
        df.iloc[2, 0] = 100.0  # 10000% exceeds the safe default of 20.0
        with pytest.raises(BABDataError, match="Implausible return"):
            validate_returns_dataframe(df, benchmark="ETH", quality=True)

    def test_default_rejects_large_gap(self):
        idx = list(pd.date_range("2020-01-01", periods=5, freq="D"))
        idx[3] = idx[2] + pd.Timedelta(days=30)
        df = pd.DataFrame(
            {"BTC": np.linspace(0.01, 0.05, 5), "ETH": np.linspace(0.02, 0.06, 5)},
            index=idx,
        )
        with pytest.raises(BABDataError, match="Data gap too large"):
            validate_returns_dataframe(df, benchmark="ETH", quality=True)

    def test_explicit_kwarg_can_loosen_return_threshold(self):
        df = _frozen_and_live(8)
        df.iloc[2, 0] = 100.0
        out = validate_returns_dataframe(
            df, benchmark="ETH", quality=True, max_return_abs=200.0
        )
        assert "BTC" in out.columns

    def test_explicit_kwarg_can_disable_stale_check(self):
        df = _frozen_and_live(8)  # 8-long frozen run
        out = validate_returns_dataframe(
            df, benchmark="ETH", quality=True, stale_run_threshold=0
        )
        assert "BTC" in out.columns


class TestOptOutAndHappyPath:
    def test_quality_false_skips_campaign(self):
        df = _frozen_and_live(8)
        df.iloc[2, 0] = 100.0
        out = validate_returns_dataframe(
            df, benchmark="ETH", quality=False, stale_run_threshold=3
        )
        assert "BTC" in out.columns

    def test_clean_data_passes_defaults(self):
        idx = pd.date_range("2020-01-01", periods=30, freq="D")
        rng = np.random.default_rng(7)
        df = pd.DataFrame(
            {
                "BTC": rng.normal(0, 0.02, 30),
                "ETH": rng.normal(0, 0.02, 30),
                "MKT": rng.normal(0, 0.01, 30),
            },
            index=idx,
        )
        out = validate_returns_dataframe(df, benchmark="MKT", quality=True)
        assert list(out.columns) == ["BTC", "ETH", "MKT"]
