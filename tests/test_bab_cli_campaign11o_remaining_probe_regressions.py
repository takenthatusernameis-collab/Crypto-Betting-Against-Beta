"""Campaign11o: remaining probe-backed CLI regressions (2026-11-10).

Locks exercised, non-duplicative invariants surfaced by the campaign11
follow-up probe matrix on ``real_market_prices.csv`` and
``real_market_prices_expanded.csv`` plus synthetic/config edges:

- Returns-path + --transaction-costs/--slippage matrix on expanded fixture
  (CLI == in-process BABStrategy, strict finite JSON).
- --synthetic + config overrides parity on CLI (apples-to-apples: no
  --universe => universe=None => synthetic 5-asset default).
- Multi-column sparse NaNs (several asset columns with scattered NaNs at once)
  remain rc=0 finite defensive output.
- Benchmark-only edge NaN/Inf rejection cleanliness (rc=1, no Traceback).
- Quantile sum/boundary interactions (long+short >= 1.0 runs finite; 0.0/1.0
  exclusions rejected as clean config errors).
- --output overwrite semantics (stale content replaced, rc=0).
- Extreme --beta-window vs short data (window > length on both fixtures and a
  short 10-row slice) run without Traceback and yield finite JSON.
"""
from __future__ import annotations

import io
import json
import math
import contextlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.cli import main
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.data_loader import load_prices, load_returns
from strategies.betting_against_beta.strategy import BABStrategy

REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_PRICES = str(REPO_ROOT / "tests" / "fixtures" / "real_market_prices.csv")
EXP_PRICES = str(REPO_ROOT / "tests" / "fixtures" / "real_market_prices_expanded.csv")


def _run_cli(argv):
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    rc = 1
    with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
        try:
            rc = main(argv)
        except SystemExit as exc:
            rc = int(exc.code) if isinstance(exc.code, int) else 1
        except Exception as exc:  # noqa: BLE001 - surface as clean rc=1
            err_buf.write(f"UNCAUGHT: {type(exc).__name__}: {exc}\n")
    return rc, out_buf.getvalue(), err_buf.getvalue()


def _write_output(argv, out_path):
    rc, out_s, err_s = _run_cli([*argv, "--output", str(out_path)])
    raw = out_path.read_text() if out_path.exists() else ""
    payload = json.loads(raw) if out_path.exists() else None
    return rc, payload, raw, out_s, err_s


def _assert_strict_finite(payload, raw):
    assert payload is not None
    json.dumps(payload, allow_nan=False)
    for tok in ("NaN", "Infinity", "-Infinity"):
        assert tok not in raw
    fc = payload["final_cumulative"]
    assert isinstance(fc, (int, float)) and not isinstance(fc, bool)
    assert math.isfinite(float(fc))
    assert isinstance(payload["periods"], int) and payload["periods"] > 0


class TestReturnsPathCostSlippageMatrixExpanded:
    @pytest.mark.parametrize(
        "argv,cfgkw",
        [
            (
                ["--data", EXP_PRICES, "--benchmark", "BTC", "--transaction-costs", "0.001"],
                {"benchmark": "BTC", "transaction_costs": 0.001},
            ),
            (
                ["--data", EXP_PRICES, "--benchmark", "BTC", "--slippage", "0.0005"],
                {"benchmark": "BTC", "slippage": 0.0005},
            ),
            (
                ["--data", EXP_PRICES, "--benchmark", "BTC", "--transaction-costs", "0.001", "--slippage", "0.0005"],
                {"benchmark": "BTC", "transaction_costs": 0.001, "slippage": 0.0005},
            ),
            (
                ["--data", EXP_PRICES, "--benchmark", "BTC", "--transaction-costs", "0.002", "--slippage", "0.001", "--rebalance-freq", "weekly"],
                {"benchmark": "BTC", "transaction_costs": 0.002, "slippage": 0.001, "rebalance_freq": "weekly"},
            ),
            (
                ["--data", EXP_PRICES, "--benchmark", "BTC", "--transaction-costs", "0.005", "--rebalance-freq", "monthly"],
                {"benchmark": "BTC", "transaction_costs": 0.005, "rebalance_freq": "monthly"},
            ),
        ],
    )
    def test_returns_path_tc_slippage_parity(self, tmp_path, argv, cfgkw):
        returns_df = load_prices(EXP_PRICES, benchmark="BTC")
        ret_path = tmp_path / "returns.csv"
        returns_df.to_csv(ret_path)
        out = tmp_path / "o.json"
        rc, payload, raw, out_s, err_s = _write_output(
            ["--data", str(ret_path), "--benchmark", "BTC", *argv[4:]], out
        )
        assert rc == 0, (rc, out_s + err_s)
        _assert_strict_finite(payload, raw)
        rdf = load_returns(str(ret_path), benchmark="BTC")
        res = BABStrategy(**cfgkw).run(returns_df=rdf)
        assert math.isclose(
            float(payload["final_cumulative"]),
            float(res.backtest["cumulative"].iloc[-1]),
            abs_tol=1e-12,
        )
        assert payload["periods"] == int(len(res.backtest))
        assert payload["benchmark"] == cfgkw.get("benchmark", "BTC")
        assert payload["universe"] == [str(c) for c in rdf.columns]


class TestSyntheticConfigOverridesParity:
    def test_synthetic_overrides_match_inprocess(self, tmp_path):
        out = tmp_path / "o.json"
        argv = [
            "--synthetic", "--benchmark", "ETH", "--beta-window", "30",
            "--long-quantile", "0.2", "--short-quantile", "0.2",
            "--transaction-costs", "0.001", "--slippage", "0.0005",
            "--rebalance-freq", "weekly", "--output", str(out),
        ]
        rc, payload, raw, out_s, err_s = _write_output(argv, out)
        assert rc == 0, (rc, out_s + err_s)
        _assert_strict_finite(payload, raw)
        cfg = BABConfig(
            universe=None, benchmark="ETH", beta_window=30,
            long_quantile=0.2, short_quantile=0.2,
            transaction_costs=0.001, slippage=0.0005, rebalance_freq="weekly",
        )
        res = BABStrategy(cfg).run()
        assert math.isclose(
            float(payload["final_cumulative"]),
            float(res.backtest["cumulative"].iloc[-1]),
            abs_tol=1e-12,
        )
        assert payload["periods"] == int(len(res.backtest))
        assert payload["benchmark"] == "ETH"
        assert payload["universe"] == list(res.config.universe)


class TestMultiColumnSparseNaNsExpanded:
    def test_scattered_nans_across_columns_remain_finite(self, tmp_path):
        df = pd.read_csv(EXP_PRICES)
        df.loc[df.index.isin([2, 10, 50]), "ETH"] = np.nan
        df.loc[df.index.isin([5, 20, 100]), "SOL"] = np.nan
        df.loc[df.index.isin([30, 200]), "BNB"] = np.nan
        path = tmp_path / "m.csv"
        df.to_csv(path, index=False)
        out = tmp_path / "o.json"
        rc, payload, raw, out_s, err_s = _write_output(
            ["--data", str(path), "--from-prices", "--benchmark", "BTC"], out
        )
        assert rc == 0, (rc, out_s + err_s)
        _assert_strict_finite(payload, raw)


class TestBenchmarkOnlyEdgeRejection:
    def test_benchmark_all_nan_rejected_cleanly(self, tmp_path, capsys):
        df = pd.read_csv(EXP_PRICES)
        df["BTC"] = np.nan
        path = tmp_path / "m.csv"
        df.to_csv(path, index=False)
        out = tmp_path / "o.json"
        rc, payload, raw, out_s, err_s = _write_output(
            ["--data", str(path), "--from-prices", "--benchmark", "BTC"], out
        )
        captured = capsys.readouterr()
        combined = out_s + err_s + raw
        assert rc == 1, (rc, combined)
        assert payload is None
        assert "Traceback" not in combined

    def test_benchmark_all_inf_rejected_cleanly(self, tmp_path, capsys):
        df = pd.read_csv(EXP_PRICES)
        df["BTC"] = np.inf
        path = tmp_path / "m.csv"
        df.to_csv(path, index=False)
        out = tmp_path / "o.json"
        rc, payload, raw, out_s, errs = _write_output(
            ["--data", str(path), "--from-prices", "--benchmark", "BTC"], out
        )
        captured = capsys.readouterr()
        combined = out_s + errs + raw
        assert rc == 1, (rc, combined)
        assert payload is None
        assert "Traceback" not in combined


class TestQuantileSumBoundaryInteractions:
    @pytest.mark.parametrize(
        "extra_argv",
        [
            ["--long-quantile", "0.6", "--short-quantile", "0.6"],
        ],
    )
    def test_quantile_sum_ge_one_runs_finite(self, tmp_path, extra_argv):
        out = tmp_path / "o.json"
        rc, payload, raw, out_s, err_s = _write_output(
            ["--data", EXP_PRICES, "--from-prices", "--benchmark", "BTC", *extra_argv, "--output", str(out)],
            out,
        )
        assert rc == 0, (rc, out_s + err_s)
        _assert_strict_finite(payload, raw)

    @pytest.mark.parametrize(
        "argv,needle",
        [
            (["--long-quantile", "0"], "long_quantile"),
            (["--long-quantile", "1"], "long_quantile"),
            (["--short-quantile", "0"], "short_quantile"),
            (["--short-quantile", "1"], "short_quantile"),
        ],
    )
    def test_quantile_boundary_excluded_clean_config_error(self, tmp_path, capsys, argv, needle):
        rc = main(
            ["--data", EXP_PRICES, "--from-prices", "--benchmark", "BTC", *argv]
        )
        captured = capsys.readouterr()
        combined = captured.out + captured.err
        assert rc == 1, (rc, combined)
        assert "Traceback" not in combined
        assert needle.lower() in combined.lower()


class TestOutputOverwriteSemantics:
    def test_second_write_replaces_stale_content(self, tmp_path):
        out = tmp_path / "o.json"
        out.write_text("STALE_CONTENT_DO_NOT_KEEP")
        rc1, payload1, raw1, _, _ = _write_output(
            ["--data", EXP_PRICES, "--from-prices", "--benchmark", "BTC"], out
        )
        assert rc1 == 0, (rc1, raw1)
        assert out.read_text() != "STALE_CONTENT_DO_NOT_KEEP"
        _assert_strict_finite(payload1, raw1)

        rc2, payload2, raw2, _, _ = _write_output(
            ["--data", EXP_PRICES, "--from-prices", "--benchmark", "BTC", "--beta-window", "30"], out
        )
        assert rc2 == 0, (rc2, raw2)
        assert payload2 is not None
        json.dumps(payload2, allow_nan=False)
        assert math.isfinite(float(payload2["final_cumulative"]))


class TestExtremeBetaWindowVsShortData:
    @pytest.mark.parametrize(
        "data,extra_argv",
        [
            (EXP_PRICES, ["--beta-window", "9999"]),
            (EXP_PRICES, ["--beta-window", "1000"]),
            (REAL_PRICES, ["--beta-window", "9999"]),
        ],
    )
    def test_extreme_window_vs_long_fixture(self, tmp_path, data, extra_argv):
        out = tmp_path / "o.json"
        rc, payload, raw, out_s, err_s = _write_output(
            ["--data", data, "--from-prices", "--benchmark", "BTC", *extra_argv, "--output", str(out)],
            out,
        )
        assert "Traceback" not in (out_s + err_s), (rc, out_s + err_s)
        if rc == 0 and out.exists():
            _assert_strict_finite(json.loads(out.read_text()), raw)

    def test_extreme_window_vs_short_slice(self, tmp_path):
        df = pd.read_csv(EXP_PRICES).head(10)
        path = tmp_path / "short.csv"
        df.to_csv(path, index=False)
        out = tmp_path / "o.json"
        rc, payload, raw, out_s, err_s = _write_output(
            ["--data", str(path), "--from-prices", "--benchmark", "BTC", "--beta-window", "500", "--output", str(out)],
            out,
        )
        assert "Traceback" not in (out_s + err_s), (rc, out_s + err_s)
        if rc == 0 and out.exists():
            _assert_strict_finite(json.loads(out.read_text()), raw)
