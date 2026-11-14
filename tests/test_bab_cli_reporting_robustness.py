"""CLI/reporting output robustness (campaign11 slice a).

Covers --output path handling, schema stability across all committed fixtures
+ synthetic, dry-run behavior, and byte-determinism — no external data.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.cli import __version__, main
from strategies.betting_against_beta.config import BABConfig

PRICE_FIXTURES = [
    "tests/fixtures/real_market_prices.csv",
    "tests/fixtures/real_market_prices_expanded.csv",
]
RETURNS_FIXTURE = "tests/fixtures/returns.json"
REQUIRED_KEYS = ("final_cumulative", "periods", "benchmark", "universe")


def _parse_output(out: Path) -> dict:
    payload = json.loads(out.read_text())
    for key in REQUIRED_KEYS:
        assert key in payload, f"missing key {key!r}"
    assert np.isfinite(float(payload["final_cumulative"]))
    assert isinstance(payload["periods"], int) and payload["periods"] > 0
    assert isinstance(payload["universe"], list)
    return payload


class TestOutputPathRobustness:
    def test_nested_output_path_created(self, tmp_path):
        out = tmp_path / "a" / "b" / "c" / "out.json"
        rc = main(["--synthetic", "--output", str(out), "--beta-window", "30"])
        assert rc == 0
        assert out.exists()
        _parse_output(out)

    def test_overwrite_existing_file_deterministic(self, tmp_path):
        out = tmp_path / "out.json"
        out.write_text('{"stale": true}')
        rc1 = main(["--synthetic", "--output", str(out), "--beta-window", "30"])
        assert rc1 == 0
        b1 = out.read_bytes()
        p1 = json.loads(b1)
        assert "stale" not in p1
        rc2 = main(["--synthetic", "--output", str(out), "--beta-window", "30"])
        assert rc2 == 0
        b2 = out.read_bytes()
        assert b1 == b2, "overwrite must produce byte-identical output"


class TestSchemaStabilityAllSources:
    @pytest.mark.parametrize(
        "argv_factory",
        [
            pytest.param(
                lambda out: [
                    "--data",
                    RETURNS_FIXTURE,
                    "--benchmark",
                    "BTC",
                    "--output",
                    str(out),
                ],
                id="returns.json",
            ),
            pytest.param(
                lambda out: [
                    "--data",
                    PRICE_FIXTURES[0],
                    "--from-prices",
                    "--benchmark",
                    "BTC",
                    "--output",
                    str(out),
                ],
                id="real_market_prices.csv",
            ),
            pytest.param(
                lambda out: [
                    "--data",
                    PRICE_FIXTURES[1],
                    "--from-prices",
                    "--benchmark",
                    "BTC",
                    "--output",
                    str(out),
                ],
                id="real_market_prices_expanded.csv",
            ),
            pytest.param(
                lambda out: [
                    "--synthetic",
                    "--beta-window",
                    "30",
                    "--output",
                    str(out),
                ],
                id="synthetic",
            ),
        ],
    )
    def test_schema_finite_and_deterministic(self, argv_factory, tmp_path):
        out1 = tmp_path / "a.json"
        out2 = tmp_path / "b.json"
        rc1 = main(argv_factory(out1))
        rc2 = main(argv_factory(out2))
        assert rc1 == rc2 == 0
        p1 = _parse_output(out1)
        p2 = _parse_output(out2)
        assert p1["final_cumulative"] == p2["final_cumulative"]
        assert p1["periods"] == p2["periods"]
        assert p1["benchmark"] == p2["benchmark"]
        assert out1.read_bytes() == out2.read_bytes()

    @pytest.mark.parametrize(
        "argv_factory",
        [
            pytest.param(
                lambda out: ["--data", RETURNS_FIXTURE, "--benchmark", "BTC", "--output", str(out)],
                id="returns.json",
            ),
            pytest.param(
                lambda out: [
                    "--data",
                    PRICE_FIXTURES[0],
                    "--from-prices",
                    "--benchmark",
                    "BTC",
                    "--output",
                    str(out),
                ],
                id="real_market_prices.csv",
            ),
            pytest.param(
                lambda out: [
                    "--data",
                    PRICE_FIXTURES[1],
                    "--from-prices",
                    "--benchmark",
                    "BTC",
                    "--output",
                    str(out),
                ],
                id="real_market_prices_expanded.csv",
            ),
            pytest.param(
                lambda out: ["--synthetic", "--beta-window", "30", "--output", str(out)],
                id="synthetic",
            ),
        ],
    )
    def test_output_types_stable(self, argv_factory, tmp_path):
        out = tmp_path / "out.json"
        assert main(argv_factory(out)) == 0
        p = json.loads(out.read_text())
        assert isinstance(p["final_cumulative"], float)
        assert isinstance(p["periods"], int)
        assert isinstance(p["benchmark"], str)
        assert isinstance(p["universe"], list)
        assert all(isinstance(u, str) for u in p["universe"])


class TestDryRunBehavior:
    def test_dry_run_synthetic_rc0(self):
        rc = main(["--dry-run", "--synthetic", "--beta-window", "30"])
        assert rc == 0

    def test_dry_run_output_not_written(self, tmp_path):
        out = tmp_path / "should_not_exist.json"
        rc = main(["--dry-run", "--synthetic", "--output", str(out), "--beta-window", "30"])
        assert rc == 0
        assert not out.exists(), "--dry-run --output must not create the file"

    def test_dry_run_output_existing_not_overwritten(self, tmp_path):
        out = tmp_path / "keep.json"
        out.write_text("sentinel")
        rc = main(["--dry-run", "--synthetic", "--output", str(out), "--beta-window", "30"])
        assert rc == 0
        assert out.read_text() == "sentinel"


class TestReadmeCliContract:
    """README↔CLI contract (campaign11 slice c, parse/smoke only)."""

    README_FLAGS = [
        "--data",
        "--from-prices",
        "--benchmark",
        "--dry-run",
        "--output",
        "--synthetic",
        "--version",
        "--universe",
        "--beta-window",
        "--long-quantile",
        "--short-quantile",
        "--rebalance-freq",
        "--transaction-costs",
        "--slippage",
    ]

    def test_readme_flags_accepted_by_argparse(self):
        # Parse-only: build parser same shape as CLI exposes; use --dry-run/--version smokes.
        # --dry-run --synthetic exercises most flags path without data.
        rc = main(
            [
                "--dry-run",
                "--synthetic",
                "--benchmark",
                "BTC",
                "--beta-window",
                "30",
                "--long-quantile",
                "0.3",
                "--short-quantile",
                "0.3",
                "--rebalance-freq",
                "daily",
                "--transaction-costs",
                "0.0",
                "--slippage",
                "0.0",
            ]
        )
        assert rc == 0

    def test_version_flag_exits_zero(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["--version"])
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert __version__ in out

    def test_version_matches_module(self):
        from strategies.betting_against_beta import cli

        assert cli.__version__ == __version__
        assert __version__ == "0.1.0"

    @pytest.mark.parametrize("flag", README_FLAGS)
    def test_flag_present_in_readme(self, flag):
        readme = Path("README.md").read_text()
        assert flag in readme, f"README missing documented flag {flag}"


class TestNumericInvariantsRealFixtures:
    """Strategy/backtest numeric invariants on real fixtures (campaign11 slice b)."""

    @pytest.mark.parametrize("fixture", PRICE_FIXTURES)
    def test_backtest_index_and_cumulative_invariants(self, fixture):
        from strategies.betting_against_beta.data_loader import load_prices

        df = load_prices(fixture, benchmark="BTC")
        result = BABStrategy(benchmark="BTC", beta_window=90).run(returns_df=df)
        bt = result.backtest
        assert bt.index.is_monotonic_increasing
        cum = bt["cumulative"]
        assert np.isfinite(float(cum.iloc[0])), "first cumulative must be finite"
        assert np.isfinite(float(cum.iloc[-1])), "last cumulative must be finite"
        assert np.all(np.isfinite(cum.to_numpy(dtype=float)))

    @pytest.mark.parametrize("fixture", PRICE_FIXTURES)
    def test_weights_finite_when_present(self, fixture):
        from strategies.betting_against_beta.data_loader import load_prices

        df = load_prices(fixture, benchmark="BTC")
        result = BABStrategy(benchmark="BTC", beta_window=90).run(returns_df=df)
        if result.weights is not None:
            arr = result.weights.to_numpy(dtype=float)
            # NaN weights may appear for warmup; Inf must not.
            assert not np.any(np.isinf(arr))
