"""Campaign11l: evidence-backed CLI output parity + error-path cleanliness.

Probed 2026-11-10T02:04Z @ HEAD 27574e0:
- CLI --output summary matches in-process BABStrategy on real fixture for
  exercised flag combinations (default, universe subset, benchmark-in-universe,
  transaction_costs+slippage): final_cumulative (exact float), periods,
  benchmark, universe all match; JSON strict (no NaN/Infinity tokens).
- Error paths are clean (rc=1, no Traceback) for malformed/missing inputs and
  dry-run invalid combos probed.

Locks these invariants with non-duplicative, evidence-backed regressions.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from strategies.betting_against_beta.cli import main
from strategies.betting_against_beta.data_loader import load_prices
from strategies.betting_against_beta.strategy import BABStrategy

REAL_PRICES = "tests/fixtures/real_market_prices.csv"


def _run_cli_main(argv: list[str], out_path: Path):
    rc = main([*argv, "--output", str(out_path)])
    payload = json.loads(out_path.read_text()) if out_path.exists() else None
    return rc, payload


def _assert_clean_json(payload: dict, raw: str):
    json.dumps(payload, allow_nan=False)
    for tok in ("NaN", "Infinity", "-Infinity"):
        assert tok not in raw
    fc = payload["final_cumulative"]
    assert isinstance(fc, (int, float)) and not isinstance(fc, bool)
    assert math.isfinite(float(fc))
    assert isinstance(payload["periods"], int) and payload["periods"] > 0


class TestCliOutputParityRealFixture:
    @pytest.mark.parametrize(
        "argv,cfgkw",
        [
            (
                ["--data", REAL_PRICES, "--from-prices", "--benchmark", "BTC"],
                {"benchmark": "BTC"},
            ),
            (
                [
                    "--data",
                    REAL_PRICES,
                    "--from-prices",
                    "--benchmark",
                    "BTC",
                    "--universe",
                    "ETH",
                    "SOL",
                    "BNB",
                ],
                {"benchmark": "BTC", "universe": ["ETH", "SOL", "BNB"]},
            ),
            (
                [
                    "--data",
                    REAL_PRICES,
                    "--from-prices",
                    "--benchmark",
                    "BTC",
                    "--universe",
                    "BTC",
                    "ETH",
                    "SOL",
                ],
                {"benchmark": "BTC", "universe": ["BTC", "ETH", "SOL"]},
            ),
            (
                [
                    "--data",
                    REAL_PRICES,
                    "--from-prices",
                    "--benchmark",
                    "BTC",
                    "--transaction-costs",
                    "0.001",
                    "--slippage",
                    "0.0005",
                ],
                {"benchmark": "BTC", "transaction_costs": 0.001, "slippage": 0.0005},
            ),
        ],
    )
    def test_output_summary_matches_inprocess_strategy(self, tmp_path, argv, cfgkw):
        out = tmp_path / "out.json"
        rc, payload = _run_cli_main(argv, out)
        assert rc == 0
        assert payload is not None
        raw = out.read_text()
        _assert_clean_json(payload, raw)

        returns_df = load_prices(REAL_PRICES, benchmark=cfgkw.get("benchmark", "BTC"))
        res = BABStrategy(**cfgkw).run(returns_df=returns_df)
        in_fc = float(res.backtest["cumulative"].iloc[-1])

        assert payload["final_cumulative"] == in_fc
        assert payload["periods"] == len(res.backtest)
        assert payload["benchmark"] == res.config.benchmark
        assert payload["universe"] == list(res.config.universe)


class TestCliErrorPathCleanliness:
    @pytest.mark.parametrize(
        "argv,needle",
        [
            (["--universe", "   ", "--synthetic"], "universe"),
            (["--data", "/no/such/file.csv", "--benchmark", "BTC"], "not found"),
            (["--data", ".", "--benchmark", "BTC"], "directory"),
            (["--output", ".", "--synthetic"], "directory"),
            (
                ["--data", REAL_PRICES, "--from-prices", "--benchmark", "NOPE"],
                "Benchmark",
            ),
            (["--beta-window", "0", "--synthetic"], "beta_window"),
            (["--long-quantile", "-0.1", "--synthetic"], "long_quantile"),
            (["--short-quantile", "1.5", "--synthetic"], "short_quantile"),
            (["--dry-run", "--output", ".", "--synthetic"], "directory"),
            (["--dry-run", "--data", ".", "--from-prices"], "INVALID"),
        ],
    )
    def test_error_paths_rc1_no_traceback(self, argv, needle, capsys):
        rc = main(argv)
        captured = capsys.readouterr()
        assert rc == 1, f"expected rc=1 argv={argv} got {rc} out={captured.out}"
        assert "Traceback" not in captured.out
        assert "Traceback" not in captured.err
        combined = (captured.out + captured.err).lower()
        assert needle.lower() in combined
