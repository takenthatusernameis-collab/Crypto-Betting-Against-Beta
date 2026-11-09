"""Real-data CLI/reporting reproducibility on committed price fixtures.

Covers the end-to-end path with ``real_market_prices*.csv`` (no external data):
- ``load_prices`` -> ``BABStrategy.run`` finite + deterministic cumulative
- CLI ``--data --from-prices --output`` → rc=0, schema-stable JSON
- repeated ``--output`` writes byte-for-byte identical
- ``--dry-run --data --from-prices`` → rc=0
"""
from __future__ import annotations

import hashlib
import json

import numpy as np
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.cli import main
from strategies.betting_against_beta.data_loader import load_prices

PRICE_FIXTURES = [
    "tests/fixtures/real_market_prices.csv",
    "tests/fixtures/real_market_prices_expanded.csv",
]
REQUIRED_KEYS = ("final_cumulative", "periods", "benchmark", "universe")


def _cli_price_argv(fixture, *, output=None, dry_run=False):
    argv = ["--data", fixture, "--from-prices", "--benchmark", "BTC"]
    if dry_run:
        argv = ["--dry-run"] + argv
    if output is not None:
        argv += ["--output", str(output)]
    return argv


class TestRealDataPriceRoundTrip:
    @pytest.mark.parametrize("fixture", PRICE_FIXTURES)
    def test_load_prices_to_strategy_run_finite_and_deterministic(self, fixture):
        df = load_prices(fixture, benchmark="BTC")

        def _cum():
            res = BABStrategy(benchmark="BTC", beta_window=90).run(returns_df=df)
            return float(res.backtest["cumulative"].iloc[-1])

        v1, v2 = _cum(), _cum()
        assert np.isfinite(v1) and np.isfinite(v2)
        assert v1 == v2, f"cumulative must be deterministic for {fixture}"

    @pytest.mark.parametrize("fixture", PRICE_FIXTURES)
    def test_cli_output_schema_stable_and_finite(self, fixture, tmp_path):
        out = tmp_path / "out.json"
        rc = main(_cli_price_argv(fixture, output=out))
        assert rc == 0, f"CLI must exit 0 for {fixture}"
        payload = json.loads(out.read_text())
        for key in REQUIRED_KEYS:
            assert key in payload, f"missing output key {key!r} for {fixture}"
        assert np.isfinite(float(payload["final_cumulative"]))
        assert isinstance(payload["periods"], int) and payload["periods"] > 0
        assert payload["benchmark"] == "BTC"
        assert isinstance(payload["universe"], list)

    @pytest.mark.parametrize("fixture", PRICE_FIXTURES)
    def test_cli_output_byte_deterministic(self, fixture, tmp_path):
        out1 = tmp_path / "a.json"
        out2 = tmp_path / "b.json"
        rc1 = main(_cli_price_argv(fixture, output=out1))
        rc2 = main(_cli_price_argv(fixture, output=out2))
        assert rc1 == rc2 == 0
        h1 = hashlib.sha256(out1.read_bytes()).hexdigest()
        h2 = hashlib.sha256(out2.read_bytes()).hexdigest()
        assert h1 == h2, f"output must be byte-identical for {fixture}"

    @pytest.mark.parametrize("fixture", PRICE_FIXTURES)
    def test_cli_dry_run_validates(self, fixture):
        rc = main(_cli_price_argv(fixture, dry_run=True))
        assert rc == 0, f"--dry-run must exit 0 for {fixture}"
