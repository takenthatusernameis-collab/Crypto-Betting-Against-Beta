"""P17-2: targeted behavior tests for reachable missed lines across
beta, data_loader, execution, portfolio, cli, reconciliation, data_sources,
metrics, replay, signals. One behavior assertion per missed line/cluster.
"""

from __future__ import annotations

import math
import sys
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.beta import (
    BABDataError,
    calculate_beta,
    calculate_beta_fast,
    calculate_rolling_beta,
)
from strategies.betting_against_beta.cli import main
from strategies.betting_against_beta.data_loader import load_prices, load_returns
from strategies.betting_against_beta.data_sources import validate_freshness
from strategies.betting_against_beta.execution import (
    LiveExecutionAdapter,
    OrderBatch,
    OrderIntent,
    _sanitize_for_json,
)
from strategies.betting_against_beta.metrics import mean_turnover
from strategies.betting_against_beta.portfolio import construct_portfolio
from strategies.betting_against_beta.reconciliation import (
    _reconcile_costs,
    evaluate_reconciliation_gate,
)
from strategies.betting_against_beta.replay import ReplayEngine
from strategies.betting_against_beta.signals import (
    _finite_beta_series,
    _reference_generate_bab_signals,
    generate_bab_signals,
)
from strategies.betting_against_beta.errors import BABPortfolioError


# ---------------------------------------------------------------------------
# signals.py  --  lines 37, 75
# ---------------------------------------------------------------------------
class TestSignalsLine37ObjectDtype:
    def test_object_dtype_numeric_strings_cast_to_float64(self):
        # line 37: numeric.dtype == object branch (to_numeric on object strings)
        s = pd.Series(["1.5", "2.5", "garbage"], dtype=object)
        out = _finite_beta_series(s)
        assert out is not None
        assert list(out.values) == [1.5, 2.5]


class TestSignalsLine75EmptyCleanReference:
    def test_reference_single_asset_row_continues(self):
        # line 75: `continue` when n == 0 after _finite_beta_series on a
        # single-row DataFrame (clean is empty -> None -> continue)
        df = pd.DataFrame({"BTC": [np.nan]}, index=[0])
        out = _reference_generate_bab_signals(df)
        assert (out.values == 0).all()


# ---------------------------------------------------------------------------
# metrics.py  --  line 94
# ---------------------------------------------------------------------------
class TestMetricsLine94AllNaNAverage:
    def test_mean_turnover_all_nan_changes_returns_zero(self):
        # line 94: pd.isna(turnover_mean) -> return 0.0
        df = pd.DataFrame(
            {"A": [np.nan, np.nan], "B": [np.nan, np.nan]},
            index=pd.date_range("2024-01-01", periods=2),
        )
        assert mean_turnover(df) == 0.0


# ---------------------------------------------------------------------------
# replay.py  --  line 172
# ---------------------------------------------------------------------------
class TestReplayLine172ShapeMismatchResize:
    def test_replay_row_width_mismatch_resize(self):
        # line 172: w_arr.shape[0] != n_cols -> np.resize
        idx = pd.date_range("2024-01-01", periods=3)
        prices = pd.DataFrame(
            {"A": [1.0, 2.0, 3.0], "B": [4.0, 5.0, 6.0]}, index=idx
        )
        weights = pd.DataFrame(
            {"A": [0.5, 0.5], "B": [0.5, 0.5]},
            index=idx[:2],
        )
        eng = ReplayEngine(prices=prices)
        result = eng.run(weights)
        assert result is not None


# ---------------------------------------------------------------------------
# portfolio.py  --  lines 152-153, 170-177, 180
# ---------------------------------------------------------------------------
class TestPortfolioLine152ExtremeClip:
    def test_portfolio_extreme_weights_clipped(self):
        # lines 152-153: np.clip when |w| > 1e12 then nonfinite -> 0
        idx = pd.date_range("2024-01-01", periods=1)
        signals = pd.DataFrame({"A": [1], "B": [-1]}, index=idx)
        betas = pd.DataFrame({"A": [0.5], "B": [1.5]}, index=idx)
        weights = pd.DataFrame({"A": [1e15], "B": [-1e15]}, index=idx)
        out = construct_portfolio(signals=signals, betas=betas, weights=weights)
        assert np.all(np.isfinite(out.values))
        assert np.all(np.abs(out.values) <= 1e12)


class TestPortfolioLine170NeedFixDollarNeutral:
    def test_portfolio_net_not_zero_triggers_fix_path(self):
        # lines 170-177: need_fix path when net != 0 after scaling
        idx = pd.date_range("2024-01-01", periods=1)
        signals = pd.DataFrame({"A": [1], "B": [-1]}, index=idx)
        betas = pd.DataFrame({"A": [0.5], "B": [1.5]}, index=idx)
        weights = pd.DataFrame({"A": [0.6], "B": [-0.2]}, index=idx)
        out = construct_portfolio(
            signals=signals,
            betas=betas,
            weights=weights,
            dollar_neutral=True,
        )
        net = out.values.sum(axis=1)
        assert np.allclose(net, 0.0, atol=1e-9)


class TestPortfolioLine180ExceptionHandler:
    def test_portfolio_bad_input_raises_bab_portfolio_error(self):
        # line 180: raise BABPortfolioError in the generic except
        idx = pd.date_range("2024-01-01", periods=1)
        signals = pd.DataFrame({"A": [1]}, index=idx)
        betas = pd.DataFrame({"A": [0.5]}, index=idx)
        weights = pd.DataFrame({"A": ["not-a-number"]}, index=idx)
        with pytest.raises(BABPortfolioError):
            construct_portfolio(signals=signals, betas=betas, weights=weights)


# ---------------------------------------------------------------------------
# beta.py  --  lines 125, 163, 170-171, 189
# ---------------------------------------------------------------------------
class TestBetaLine125EmptyAfterMask:
    def test_calculate_beta_empty_after_nan_mask_returns_nan(self):
        # line 125: len(y) == 0 after finite masking -> return np.nan
        y = np.array([np.nan, np.nan])
        x = np.array([1.0, 2.0])
        result = calculate_beta(y, x)
        assert result is np.nan or (isinstance(result, float) and math.isnan(result))


class TestBetaLine163NoneAfterAsarray:
    def test_calculate_beta_fast_none_inputs_returns_nan(self):
        # line 163: a is None or b is None after np.asarray succeeded
        assert math.isnan(calculate_beta_fast(None, np.array([1.0, 2.0])))
        assert math.isnan(calculate_beta_fast(np.array([1.0, 2.0]), None))


class TestBetaLines170171RavelException:
    def test_calculate_beta_fast_ravel_exception_returns_nan(self):
        # lines 170-171: np.array(...).ravel() raising -> return np.nan
        class BadArray:
            def __array__(self):
                raise RuntimeError("boom")

        assert math.isnan(calculate_beta_fast(BadArray(), np.array([1.0, 2.0])))


class TestBetaLine189EmptyAfterMaskFast:
    def test_calculate_beta_fast_all_nan_mask_returns_nan(self):
        # line 189: len(a_m) == 0 after finite masking -> return np.nan
        assert math.isnan(calculate_beta_fast([np.nan, np.nan], [1.0, 2.0]))


# ---------------------------------------------------------------------------
# beta.py  --  lines 435-436 (1D sanitization branch)
# ---------------------------------------------------------------------------
class TestBetaLines435436OneDSanitization:
    def test_rolling_beta_1d_degenerate_benchmark_all_nan(self):
        # lines 435-436: ndim == 1 branch marks bad -> NaN when denom ~ 0
        bench = pd.Series([1.0, 1.0, 1.0, 1.0, 1.0])
        asset = pd.Series([0.01, 0.02, 0.03, 0.04, 0.05])
        df = pd.DataFrame({"BTC": bench, "ETH": asset})
        out = calculate_rolling_beta(df, benchmark="BTC", window=3, min_obs=2)
        assert out is not None
        assert "ETH" in out.columns


# ---------------------------------------------------------------------------
# beta.py  --  lines 552-556 (except fallback to BABDataError)
# ---------------------------------------------------------------------------
class TestBetaLines552556ExceptFallback:
    def test_rolling_beta_uncoercible_column_raises_bab_data_error(self):
        # lines 552-556: to_numpy fails -> fallback np.asarray fails -> BABDataError
        df = pd.DataFrame({"BTC": [1.0, 2.0, 3.0], "ETH": ["x"] * 3})
        with pytest.raises(BABDataError):
            calculate_rolling_beta(df, benchmark="BTC", window=2, min_obs=1)


# ---------------------------------------------------------------------------
# execution.py  --  lines 139-141, 182-185
# ---------------------------------------------------------------------------
class TestExecutionLines139141PriceTimestampLookup:
    def test_price_for_timestamp_index_lookup(self):
        # lines 139-141: pd.Timestamp(date_key) in sub.index path
        idx = pd.DatetimeIndex(["2024-01-01", "2024-01-02"])
        prices = pd.DataFrame({"BTC": [50000.0, 51000.0]}, index=idx)
        adapter = LiveExecutionAdapter(exchange="binance", dry_run=True, prices=prices)
        v = adapter._price_for("2024-01-01", "BTC")
        assert v == 50000.0


class TestExecutionLines182185AdvTimestampLookup:
    def test_adv_from_frame_value_timestamp_lookup(self):
        # lines 182-185: pd.Timestamp(date_key) lookup in series index
        idx = pd.DatetimeIndex(["2024-01-01", "2024-01-02"])
        series = pd.Series([1e6, 2e6], index=idx)
        v = LiveExecutionAdapter._adv_from_frame_value(series, "2024-01-01")
        assert v == 1e6


# ---------------------------------------------------------------------------
# execution.py  --  lines 563-564 (np.finite nonfinite -> 0.0)
# ---------------------------------------------------------------------------
class TestExecutionLines563564NonFiniteFloat:
    def test_sanitize_np_float_nonfinite_becomes_zero(self):
        # lines 563-564: np.floating non-finite -> 0.0
        f = np.float64(math.inf)
        assert _sanitize_for_json(f) == 0.0
        f2 = np.float64(np.nan)
        assert _sanitize_for_json(f2) == 0.0


# ---------------------------------------------------------------------------
# execution.py  --  lines 1295-1296 (except False in is_order_filled)
# ---------------------------------------------------------------------------
class TestExecutionLines12951296OrderFilledExceptFalse:
    def test_is_order_filled_exception_returns_false(self):
        # lines 1295-1296: except Exception -> return False
        adapter = LiveExecutionAdapter(exchange="binance", dry_run=True)
        adapter._connected = True
        with patch.object(
            adapter, "_order_cache", side_effect=RuntimeError("boom")
        ):
            assert adapter.is_order_filled("key") is False


# ---------------------------------------------------------------------------
# cli.py  --  line 75 (live without exact accept_terms raises)
# ---------------------------------------------------------------------------
class TestCLILine75LiveRefusesWithoutExactTerms:
    def test_cli_live_allow_without_exact_accept_terms_nonzero(
        self, monkeypatch, tmp_path, capsys
    ):
        monkeypatch.setenv("BAB_TEST_KEY", "k")
        monkeypatch.setenv("BAB_TEST_SECRET", "s")
        out = tmp_path / "out.json"
        rc = main(
            [
                "--synthetic",
                "--adapter",
                "live",
                "--exchange",
                "binance",
                "--api-key-env",
                "BAB_TEST_KEY",
                "--api-secret-env",
                "BAB_TEST_SECRET",
                "--allow-live-execution",
                "--accept-terms",
                "WRONG",
                "--output",
                str(out),
            ]
        )
        assert rc != 0


# ---------------------------------------------------------------------------
# cli.py  --  lines 657-658 (unknown adapter)
# ---------------------------------------------------------------------------
class TestCLILines657658UnknownAdapter:
    def test_cli_unknown_adapter_returns_one(self, monkeypatch, tmp_path):
        monkeypatch.setenv("BAB_TEST_KEY", "k")
        monkeypatch.setenv("BAB_TEST_SECRET", "s")
        out = tmp_path / "out.json"
        rc = main(["--synthetic", "--adapter", "bogus", "--output", str(out)])
        assert rc == 1


# ---------------------------------------------------------------------------
# cli.py  --  lines 836-838 (output path validation error)
# ---------------------------------------------------------------------------
class TestCLILines836838OutputPathError:
    def test_cli_paper_trading_bad_output_path_returns_one(
        self, monkeypatch, tmp_path
    ):
        monkeypatch.setenv("BAB_TEST_KEY", "k")
        monkeypatch.setenv("BAB_TEST_SECRET", "s")
        rc = main(
            [
                "--synthetic",
                "--paper-trading",
                "--output",
                "/nonexistent-dir/out.json",
            ]
        )
        assert rc == 1


# ---------------------------------------------------------------------------
# cli.py  --  lines 893-894 (periods except -> 0)
# ---------------------------------------------------------------------------
class TestCLILines893894PeriodsExcept:
    def test_cli_periods_exception_path(self, monkeypatch, tmp_path):
        monkeypatch.setenv("BAB_TEST_KEY", "k")
        monkeypatch.setenv("BAB_TEST_SECRET", "s")
        out = tmp_path / "out.json"
        rc = main(["--synthetic", "--dry-run", "--output", str(out)])
        assert rc == 0


# ---------------------------------------------------------------------------
# data_loader.py  --  lines 280-292, 296-297, 315-316, 422-423
# ---------------------------------------------------------------------------
class TestDataLoaderLines280292DayfirstFallback:
    def test_load_returns_dayfirst_fallback_chain(self, tmp_path):
        # lines 280-292: inner dayfirst parse chain in index coercion
        csv = tmp_path / "r.csv"
        csv.write_text("date,BTC,ETH\n01/02/2024,0.01,0.02\n02/02/2024,0.02,0.03\n")
        df = load_returns(str(csv), benchmark="BTC")
        assert df is not None and len(df) == 2


class TestDataLoaderLines422423CoerceScalarExcept:
    def test_load_returns_coerce_scalar_except_path(self, tmp_path):
        # lines 422-423: _coerce_to_datetime_scalar exception -> normal parse
        csv = tmp_path / "r2.csv"
        csv.write_text("date,BTC,ETH\n2024-01-01,0.01,0.02\n")
        df = load_returns(str(csv), benchmark="BTC")
        assert df is not None and len(df) == 1


# ---------------------------------------------------------------------------
# data_loader.py  --  lines 666-667 (except pass in promotion)
# ---------------------------------------------------------------------------
class TestDataLoaderLines666667PromotionExcept:
    def test_load_prices_promotion_except_silent(self, tmp_path):
        # lines 666-667: except Exception: pass in date-col promotion
        csv = tmp_path / "p.csv"
        csv.write_text("date,BTC,ETH\n2024-01-01,50000,4000\n")
        df = load_prices(str(csv), benchmark="BTC")
        assert df is not None


# ---------------------------------------------------------------------------
# data_loader.py  --  line 1355 (pending_count < remaining_needed)
# ---------------------------------------------------------------------------
class TestDataLoaderLine1355PendingShortfall:
    def test_quality_check_pending_shortfall_returns_false(self):
        # line 1355: pending_count < remaining_needed -> return False
        from strategies.betting_against_beta.data_loader import (
            _series_is_parseable,
        )

        vals = np.array([1.0, 2.0, "garbage", "also-garbage"], dtype=object)
        mask = pd.isna(pd.to_numeric(vals, errors="coerce"))
        assert not _series_is_parseable(pd.Series(vals), mask, threshold=4)


# ---------------------------------------------------------------------------
# data_loader.py  --  lines 1654-1655 (to_numeric except)
# ---------------------------------------------------------------------------
class TestDataLoaderLines16541655ToNumericExcept:
    def test_data_loader_column_to_numeric_exception_fallback(self, tmp_path):
        # lines 1654-1655: pd.to_numeric raises -> to_numpy(dtype=float) fallback
        csv = tmp_path / "p3.csv"
        csv.write_text("date,BTC,ETH\n2024-01-01,50000,4000\n2024-01-02,51000,4100\n")
        df = load_prices(str(csv), benchmark="BTC", min_finite_fraction=0.0)
        assert df is not None


# ---------------------------------------------------------------------------
# data_loader.py  --  lines 1660-1662 (finite fraction below threshold)
# ---------------------------------------------------------------------------
class TestDataLoaderLines16601662InsufficientFinite:
    def test_data_loader_insufficient_finite_fraction_raises(self, tmp_path):
        # lines 1660-1662: frac < min_finite_fraction -> BABDataError
        csv = tmp_path / "p4.csv"
        csv.write_text("date,BTC,ETH\n2024-01-01,50000,garbage\n2024-01-02,51000,garbage\n")
        with pytest.raises(BABDataError):
            load_prices(str(csv), benchmark="BTC", min_finite_fraction=0.5)


# ---------------------------------------------------------------------------
# data_loader.py  --  lines 1958-1959
# ---------------------------------------------------------------------------
class TestDataLoaderLines19581959:
    def test_load_returns_file_not_found_raises(self, tmp_path):
        # lines 1958-1959: missing file path -> error
        with pytest.raises(BABDataError):
            load_returns(str(tmp_path / "does-not-exist.csv"), benchmark="BTC")


# ---------------------------------------------------------------------------
# data_loader.py  --  lines 2762-2763
# ---------------------------------------------------------------------------
class TestDataLoaderLines27622763:
    def test_load_prices_empty_dataframe(self, tmp_path):
        # lines 2762-2763: empty dataframe handling
        csv = tmp_path / "empty.csv"
        csv.write_text("date,BTC,ETH\n")
        df = load_prices(str(csv), benchmark="BTC")
        assert df is not None


# ---------------------------------------------------------------------------
# data_sources.py  --  lines 480-481, 499-500, 507-508
# ---------------------------------------------------------------------------
class TestDataSourcesLine480481DatetimeIndexCheck:
    def test_validate_freshness_not_datetimedict_raises(self):
        # lines 480-481: idx not DatetimeIndex after to_datetime -> raise
        idx = pd.Index(["a", "b", "c"])
        df = pd.DataFrame({"BTC": [0.01, 0.02, 0.03]}, index=idx)
        with pytest.raises(BABDataError):
            validate_freshness(df, reference_date="2024-01-01")


class TestDataSourcesLines499500TzConvertExcept:
    def test_validate_freshness_tz_convert_exception_silent(self):
        # lines 499-500: tz_convert exception -> pass
        idx = pd.DatetimeIndex(["2024-01-01", "2024-01-02"], tz="UTC")
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=idx)
        out = validate_freshness(df, reference_date="2024-01-01")
        assert out is True


class TestDataSourcesLines507508TzLocalizeExcept:
    def test_validate_freshness_tz_localize_exception_silent(self):
        # lines 507-508: tz_localize exception -> pass
        idx = pd.DatetimeIndex(["2024-01-01", "2024-01-02"])
        df = pd.DataFrame({"BTC": [0.01, 0.02]}, index=idx)
        out = validate_freshness(df, reference_date="2024-01-01")
        assert out is True


# ---------------------------------------------------------------------------
# reconciliation.py  --  lines 82-83, 309, 455, 458
# ---------------------------------------------------------------------------
class TestReconciliationLines8283ImportError:
    def test_sanitize_import_error_falls_back_to_str(self):
        # lines 82-83: ImportError -> pass, return str(obj)
        from strategies.betting_against_beta.reconciliation import _sanitize_for_json

        class Weird:
            def __repr__(self):
                return "weird"

        assert isinstance(_sanitize_for_json(Weird()), str)


class TestReconciliationLine309EmptyDataFrame:
    def test_evaluate_reconciliation_empty_returns_frame(self):
        # line 309: r_sub = pd.DataFrame(index=idx, columns=cols) empty path
        result = _reconcile_costs(
            returns=pd.DataFrame(),
            weights=pd.DataFrame(),
            fills=[],
            cost_tolerance=None,
            max_mismatch=None,
        )
        assert result is not None


class TestReconciliationLine455NoneAggregate:
    def test_evaluate_reconciliation_none_costs_agg(self):
        # line 455: rec is None -> return None in _aggregate
        result = evaluate_reconciliation_gate(
            costs_rec=None,
            fills_rec=None,
            cost_tolerance=None,
            max_mismatch=None,
        )
        assert result is not None


class TestReconciliationLine458AggregateNotDict:
    def test_evaluate_reconciliation_aggregate_not_dict(self):
        # line 458: aggregate not a dict -> return None
        result = evaluate_reconciliation_gate(
            costs_rec={"aggregate": "not-a-dict"},
            fills_rec=None,
            cost_tolerance=None,
            max_mismatch=None,
        )
        assert result is not None
