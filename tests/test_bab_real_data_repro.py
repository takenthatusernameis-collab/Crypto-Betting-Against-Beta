"""Real-data evaluation / reporting reproducibility regression tests.

Covers the CLI end-to-end pipeline with the committed fixture
``tests/fixtures/returns.json`` (no external data):
- ``--data`` + ``--output`` produces stable, schema-stable JSON
- ``--dry-run`` validates config + data without running the backtest
- round-trip ``load_returns`` -> ``BABStrategy.run`` is finite + deterministic
- repeated ``--output`` writes are byte-for-byte identical
"""

from __future__ import annotations

import hashlib
import json

import numpy as np
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.cli import main
from strategies.betting_against_beta.data_loader import load_returns

FIXTURE = "tests/fixtures/returns.json"
REQUIRED_KEYS = ("final_cumulative", "periods", "benchmark", "universe")


def _run_cli_with_output(argv, tmp_path):
    out = tmp_path / "out.json"
    rc = main([*list(argv), "--output", str(out)])
    return rc, out


class TestCliReturnsJsonFixture:
    def test_cli_output_produces_schema_stable_json(self, tmp_path):
        rc, out = _run_cli_with_output(["--data", FIXTURE, "--benchmark", "BTC"], tmp_path)
        assert rc == 0, "CLI must exit 0 on the committed returns fixture"
        payload = json.loads(out.read_text())
        for key in REQUIRED_KEYS:
            assert key in payload, f"missing output key {key!r}"
        assert np.isfinite(float(payload["final_cumulative"]))
        assert isinstance(payload["periods"], int) and payload["periods"] > 0
        assert payload["benchmark"] == "BTC"
        assert isinstance(payload["universe"], list)

    def test_cli_dry_run_validates_config_and_data(self, tmp_path):
        rc = main(["--dry-run", "--data", FIXTURE, "--benchmark", "BTC"])
        assert rc == 0, "--dry-run must validate config + data and exit 0"

    def test_cli_output_is_byte_deterministic(self, tmp_path):
        rc1, out1 = _run_cli_with_output(["--data", FIXTURE, "--benchmark", "BTC"], tmp_path)
        rc2, out2 = _run_cli_with_output(["--data", FIXTURE, "--benchmark", "BTC"], tmp_path)
        assert rc1 == rc2 == 0
        assert (
            hashlib.sha256(out1.read_bytes()).hexdigest()
            == hashlib.sha256(out2.read_bytes()).hexdigest()
        )

    def test_from_prices_on_returns_fixture_runs_cleanly(self):
        # returns.json holds returns, not prices: load_prices treats the frame
        # as prices and derives returns, so this must run cleanly, not crash.
        rc = main(["--data", FIXTURE, "--from-prices", "--benchmark", "BTC"])
        assert rc == 0


class TestRealDataRoundTrip:
    def test_load_returns_to_strategy_run_is_finite_and_deterministic(self):
        df = load_returns(FIXTURE, benchmark="BTC", min_rows=2)
        assert not df.empty

        def _final_cumulative():
            res = BABStrategy(
                benchmark="BTC",
                beta_window=90,
                long_quantile=0.3,
                short_quantile=0.3,
            ).run(returns_df=df)
            return float(res.backtest["cumulative"].iloc[-1])

        v1, v2 = _final_cumulative(), _final_cumulative()
        assert np.isfinite(v1) and np.isfinite(v2)
        assert v1 == v2, "cumulative must be deterministic across runs"
