"""Campaign11n: expanded-fixture probe-backed regressions (2026-11-10T04:xxZ).

Locks exercised, non-duplicative invariants surfaced by campaign11m-followup
probe matrix on ``real_market_prices_expanded.csv`` and related edges:
- CLI-vs-in-process parity for additional from-prices/returns flag combos and
  alternate benchmark on expanded fixture.
- Universe handling: space-separated CLI tokens are accepted; comma-in-single-arg
  form is treated as a literal token (exercised behavior, no overlap -> clean rc=1).
- Non-finite/degenerate edges: negative price producing degenerate finite output
  (cumulative==0.0, periods reduced) remains JSON-safe; constant/frozen price
  columns are rejected cleanly; first/last/benchmark NaN and all-NaN non-benchmark
  columns remain defensively finite where exercised.
- Dry-run with valid data never writes output; nested output parent dirs created.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.cli import main
from strategies.betting_against_beta.data_loader import load_prices, load_returns
from strategies.betting_against_beta.strategy import BABStrategy

REPO_ROOT = Path(__file__).resolve().parents[1]
EXP_PRICES = str(REPO_ROOT / "tests" / "fixtures" / "real_market_prices_expanded.csv")


def _run_cli(argv, out_path: Path):
    rc = main([*argv, "--output", str(out_path)])
    raw = out_path.read_text() if out_path.exists() else ""
    payload = json.loads(raw) if out_path.exists() else None
    return rc, payload, raw


def _assert_strict_finite(payload, raw):
    assert payload is not None
    json.dumps(payload, allow_nan=False)
    for tok in ("NaN", "Infinity", "-Infinity"):
        assert tok not in raw
    fc = payload["final_cumulative"]
    assert isinstance(fc, (int, float)) and not isinstance(fc, bool)
    assert math.isfinite(float(fc))
    assert isinstance(payload["periods"], int) and payload["periods"] > 0


class TestExpandedParity:
    @pytest.mark.parametrize(
        "cli_args,cfgkw,loader",
        [
            (["--data", EXP_PRICES, "--from-prices", "--benchmark", "BTC"],
             {"benchmark": "BTC"}, lambda: load_prices(EXP_PRICES, benchmark="BTC")),
            (["--data", EXP_PRICES, "--from-prices", "--benchmark", "BTC", "--beta-window", "30"],
             {"benchmark": "BTC", "beta_window": 30}, lambda: load_prices(EXP_PRICES, benchmark="BTC")),
            (["--data", EXP_PRICES, "--from-prices", "--benchmark", "BTC", "--rebalance-freq", "weekly"],
             {"benchmark": "BTC", "rebalance_freq": "weekly"}, lambda: load_prices(EXP_PRICES, benchmark="BTC")),
            (["--data", EXP_PRICES, "--from-prices", "--benchmark", "BTC", "--rebalance-freq", "monthly"],
             {"benchmark": "BTC", "rebalance_freq": "monthly"}, lambda: load_prices(EXP_PRICES, benchmark="BTC")),
            (["--data", EXP_PRICES, "--from-prices", "--benchmark", "BTC", "--long-quantile", "0.2", "--short-quantile", "0.2"],
             {"benchmark": "BTC", "long_quantile": 0.2, "short_quantile": 0.2}, lambda: load_prices(EXP_PRICES, benchmark="BTC")),
            (["--data", EXP_PRICES, "--from-prices", "--benchmark", "ETH"],
             {"benchmark": "ETH"}, lambda: load_prices(EXP_PRICES, benchmark="ETH")),
            (["--data", EXP_PRICES, "--benchmark", "BTC"],
             {"benchmark": "BTC"}, lambda: load_returns(EXP_PRICES, benchmark="BTC")),
            (["--data", EXP_PRICES, "--benchmark", "BTC", "--rebalance-freq", "weekly", "--transaction-costs", "0.001"],
             {"benchmark": "BTC", "rebalance_freq": "weekly", "transaction_costs": 0.001}, lambda: load_returns(EXP_PRICES, benchmark="BTC")),
        ],
    )
    def test_cli_matches_inprocess(self, tmp_path, cli_args, cfgkw, loader):
        rc, payload, raw = _run_cli(cli_args, tmp_path / "o.json")
        assert rc == 0
        _assert_strict_finite(payload, raw)
        returns = loader()
        strat = BABStrategy(**cfgkw)
        res = strat.run(returns_df=returns)
        assert math.isclose(float(payload["final_cumulative"]), float(res.backtest["cumulative"].iloc[-1]), abs_tol=1e-12)
        assert payload["periods"] == int(len(res.backtest))
        assert payload["benchmark"] == cfgkw.get("benchmark", "BTC")
        assert payload["universe"] == [str(c) for c in returns.columns]


class TestUniverseHandlingExpanded:
    def test_space_separated_tokens_select_subset(self, tmp_path):
        rc, payload, raw = _run_cli(
            ["--data", EXP_PRICES, "--from-prices", "--benchmark", "BTC", "--universe", "ETH", "SOL", "BNB"],
            tmp_path / "o.json",
        )
        assert rc == 0
        _assert_strict_finite(payload, raw)
        assert payload["universe"] == ["ETH", "SOL", "BNB"]

    def test_comma_single_arg_is_literal_token_and_rejected_cleanly(self, tmp_path):
        out = tmp_path / "o.json"
        rc = main(["--data", EXP_PRICES, "--from-prices", "--benchmark", "BTC", "--universe", "ETH,SOL,BNB", "--output", str(out)])
        assert rc == 1
        assert not out.exists()

    def test_dry_run_valid_does_not_write_output(self, tmp_path):
        out = tmp_path / "o.json"
        rc = main(["--data", EXP_PRICES, "--from-prices", "--benchmark", "BTC", "--dry-run", "--output", str(out)])
        assert rc == 0
        assert not out.exists()

    def test_nested_output_parent_created(self, tmp_path):
        out = tmp_path / "a" / "b" / "o.json"
        rc, payload, raw = _run_cli(["--data", EXP_PRICES, "--from-prices", "--benchmark", "BTC"], out)
        assert rc == 0
        assert out.exists()
        _assert_strict_finite(payload, raw)


class TestNonFiniteDegenerateExpanded:
    def _write(self, tmp_path, df):
        p = tmp_path / "m.csv"
        df.to_csv(p, index=False)
        return str(p)

    def test_negative_price_yields_finite_degenerate_summary(self, tmp_path):
        df = pd.read_csv(EXP_PRICES)
        df.loc[10, "ETH"] = -1.0
        path = self._write(tmp_path, df)
        rc, payload, raw = _run_cli(["--data", path, "--from-prices", "--benchmark", "BTC"], tmp_path / "o.json")
        assert rc == 0
        assert payload is not None
        json.dumps(payload, allow_nan=False)
        for tok in ("NaN", "Infinity", "-Infinity"):
            assert tok not in raw
        assert math.isfinite(float(payload["final_cumulative"]))
        assert payload["periods"] == 397

    def test_constant_column_rejected_cleanly(self, tmp_path):
        df = pd.read_csv(EXP_PRICES)
        df["SOL"] = 20.0
        path = self._write(tmp_path, df)
        out = tmp_path / "o.json"
        rc = main(["--data", path, "--from-prices", "--benchmark", "BTC", "--output", str(out)])
        assert rc == 1
        assert not out.exists()

    @pytest.mark.parametrize("col,row", [("ETH", 0), ("SOL", -1), ("BTC", 0)])
    def test_edge_row_nans_remain_finite(self, tmp_path, col, row):
        df = pd.read_csv(EXP_PRICES)
        df.loc[df.index[row], col] = np.nan
        path = self._write(tmp_path, df)
        rc, payload, raw = _run_cli(["--data", path, "--from-prices", "--benchmark", "BTC"], tmp_path / "o.json")
        assert rc == 0
        _assert_strict_finite(payload, raw)

    def test_all_nan_non_benchmark_column_remains_finite(self, tmp_path):
        df = pd.read_csv(EXP_PRICES)
        df["AVAX"] = np.nan
        path = self._write(tmp_path, df)
        rc, payload, raw = _run_cli(["--data", path, "--from-prices", "--benchmark", "BTC"], tmp_path / "o.json")
        assert rc == 0
        _assert_strict_finite(payload, raw)
