"""CLI numeric/reporting invariants (campaign11 slice e, evidence-first).

Verifies CLI --output JSON summary stays finite/strict and (where deterministic
and cheap) matches strategy/CLI-extracted semantics: periods, final_cumulative
tail parity for deterministic synthetic configs, and --universe subset contract.
No production changes; uses committed fixtures + synthetic only.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.cli import main
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.data_loader import load_prices, load_returns

PRICE_FIXTURES = [
    "tests/fixtures/real_market_prices.csv",
    "tests/fixtures/real_market_prices_expanded.csv",
]
RETURNS_FIXTURE = "tests/fixtures/returns.json"


def _cli_run(argv):
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "o.json"
        rc = main([*argv, "--output", str(out)])
        payload = json.loads(out.read_text()) if out.exists() else None
        return rc, payload


def _assert_summary_finite_strict(payload: dict) -> None:
    assert isinstance(payload, dict)
    # strict JSON already enforced by CLI (allow_nan=False); re-serialize as guard
    json.dumps(payload, allow_nan=False)
    fc = payload["final_cumulative"]
    assert isinstance(fc, (int, float)) and not isinstance(fc, bool)
    assert math.isfinite(float(fc))
    assert np.isfinite(float(fc))
    assert isinstance(payload["periods"], int)
    assert payload["periods"] > 0
    assert isinstance(payload["benchmark"], str)
    assert isinstance(payload["universe"], list)


class TestDeterministicSyntheticParity:
    """CLI output parity with strategy semantics for fixed synthetic config.

    Parity target is BABConfig/BABStrategy with the same effective CLI args
    (universe=None => config default synthetic universe) — evidence: CLI uses
    BABConfig(universe=None, ...) for --synthetic and produces identical
    cumulative/periods to BABStrategy(BABConfig(...)).run().
    """

    @staticmethod
    def _strategy_for_cli_synthetic(**overrides):
        base = dict(
            universe=None,
            benchmark="BTC",
            beta_window=90,
            long_quantile=0.3,
            short_quantile=0.3,
            rebalance_freq="daily",
            transaction_costs=0.0,
            slippage=0.0,
        )
        base.update(overrides)
        return BABStrategy(BABConfig(**base)).run()

    @pytest.mark.parametrize(
        "extra_argv,overrides",
        [
            (
                [
                    "--synthetic", "--beta-window", "30", "--benchmark", "BTC",
                    "--long-quantile", "0.3", "--short-quantile", "0.3",
                    "--rebalance-freq", "daily", "--transaction-costs", "0.0",
                    "--slippage", "0.0",
                ],
                dict(
                    benchmark="BTC", beta_window=30, long_quantile=0.3,
                    short_quantile=0.3, rebalance_freq="daily",
                    transaction_costs=0.0, slippage=0.0,
                ),
            ),
            (
                ["--synthetic", "--beta-window", "30", "--benchmark", "BTC"],
                dict(benchmark="BTC", beta_window=30),
            ),
        ],
    )
    def test_periods_and_final_cumulative_match_strategy(self, extra_argv, overrides):
        rc, payload = _cli_run(extra_argv)
        assert rc == 0
        _assert_summary_finite_strict(payload)
        result = self._strategy_for_cli_synthetic(**overrides)
        assert payload["periods"] == len(result.backtest)
        tail = float(result.backtest["cumulative"].iloc[-1])
        assert math.isfinite(tail)
        # CLI coerces via _coerce_finite_scalar; finite tail must round-trip exactly as float.
        assert payload["final_cumulative"] == pytest.approx(tail, rel=0, abs=1e-12)
        assert payload["benchmark"] == overrides["benchmark"]

    def test_universe_subset_reflected_and_stable(self):
        argv = [
            "--synthetic", "--beta-window", "30", "--benchmark", "BTC",
            "--universe", "BTC", "ETH", "SOL",
        ]
        rc1, p1 = _cli_run(argv)
        rc2, p2 = _cli_run(argv)
        assert rc1 == rc2 == 0
        _assert_summary_finite_strict(p1)
        assert p1["universe"] == ["BTC", "ETH", "SOL"]
        assert p1["periods"] == p2["periods"]
        assert p1["final_cumulative"] == p2["final_cumulative"]
        result = BABStrategy(
            benchmark="BTC", beta_window=30, universe=["BTC", "ETH", "SOL"],
        ).run()
        assert p1["periods"] == len(result.backtest)
        assert p1["final_cumulative"] == pytest.approx(
            float(result.backtest["cumulative"].iloc[-1]), rel=0, abs=1e-12,
        )


class TestFixtureNumericInvariants:
    """CLI summary finite/strict across committed fixtures; periods parity when stable."""

    @pytest.mark.parametrize("fixture", PRICE_FIXTURES)
    def test_price_fixture_cli_summary_finite_and_periods_parity(self, fixture):
        argv = [
            "--data", fixture, "--from-prices", "--benchmark", "BTC",
            "--beta-window", "90",
        ]
        rc, payload = _cli_run(argv)
        assert rc == 0
        _assert_summary_finite_strict(payload)
        df = load_prices(fixture, benchmark="BTC", min_rows=BABConfig().min_rows)
        result = BABStrategy(benchmark="BTC", beta_window=90).run(returns_df=df)
        assert payload["periods"] == len(result.backtest)
        tail = float(result.backtest["cumulative"].iloc[-1])
        assert math.isfinite(tail)
        assert payload["final_cumulative"] == pytest.approx(tail, rel=0, abs=1e-12)
        assert payload["benchmark"] == "BTC"

    def test_returns_fixture_cli_summary_finite_and_periods_parity(self):
        argv = ["--data", RETURNS_FIXTURE, "--benchmark", "BTC"]
        rc, payload = _cli_run(argv)
        assert rc == 0
        _assert_summary_finite_strict(payload)
        df = load_returns(RETURNS_FIXTURE, benchmark="BTC", min_rows=BABConfig().min_rows)
        result = BABStrategy(benchmark="BTC").run(returns_df=df)
        assert payload["periods"] == len(result.backtest)
        tail = float(result.backtest["cumulative"].iloc[-1])
        assert math.isfinite(tail)
        assert payload["final_cumulative"] == pytest.approx(tail, rel=0, abs=1e-12)

    @pytest.mark.parametrize(
        "argv",
        [
            pytest.param(
                ["--data", RETURNS_FIXTURE, "--benchmark", "BTC"], id="returns",
            ),
            pytest.param(
                ["--data", PRICE_FIXTURES[0], "--from-prices", "--benchmark", "BTC"],
                id="prices",
            ),
            pytest.param(
                ["--data", PRICE_FIXTURES[1], "--from-prices", "--benchmark", "BTC"],
                id="prices-expanded",
            ),
            pytest.param(["--synthetic", "--beta-window", "30"], id="synthetic"),
        ],
    )
    def test_json_numeric_fields_finite_no_nan_inf_tokens(self, argv):
        rc, payload = _cli_run(argv)
        assert rc == 0
        _assert_summary_finite_strict(payload)
        raw = json.dumps(payload, allow_nan=False)
        assert "NaN" not in raw
        assert "Infinity" not in raw
        assert "-Infinity" not in raw
