"""Campaign11 slice (g): targeted edge/error robustness (evidence-first).

Covers adversarial-but-plausible backtest shapes the CLI already defends
against (Series, ndarray, non-finite cumulative tail, empty DataFrame-like
length edge) at the CLI/strategy boundary via monkeypatch, plus BABDataError
propagation from real-data load paths. No production changes.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import cli as cli_mod
from strategies.betting_against_beta.cli import main
from strategies.betting_against_beta.errors import BABDataError

PRICES = "tests/fixtures/real_market_prices.csv"


def _run_with_output(argv, monkeypatch_result):
    """Run CLI with synthetic path but monkeypatched strategy result."""

    class FakeStrategy:
        def __init__(self, config):
            self.config = config

        def run(self, returns_df=None):
            return monkeypatch_result

    import tempfile

    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "out.json"
        # monkeypatch in cli module
        orig = cli_mod.BABStrategy
        cli_mod.BABStrategy = FakeStrategy
        try:
            rc = main([*argv, "--output", str(out)])
        finally:
            cli_mod.BABStrategy = orig
        payload = json.loads(out.read_text()) if out.exists() else None
        return rc, payload, out.exists()


def _assert_strict_finite(payload):
    assert payload is not None
    json.dumps(payload, allow_nan=False)
    for tok in ("NaN", "Infinity", "-Infinity"):
        assert tok not in json.dumps(payload)
    fc = payload["final_cumulative"]
    assert isinstance(fc, (int, float)) and not isinstance(fc, bool)
    assert math.isfinite(float(fc))
    assert isinstance(payload["periods"], int) and payload["periods"] >= 0
    assert isinstance(payload["benchmark"], str)
    assert isinstance(payload["universe"], list)


class TestAdversarialBacktestShapes:
    def test_backtest_series_unnamed_survives_finite_output(self):
        # Unnamed Series (no 'cum' name): extraction returns object; CLI coerces to default.
        res = SimpleNamespace(backtest=pd.Series([1.0, 1.05, 1.1]))
        rc, payload, wrote = _run_with_output(["--synthetic"], res)
        assert rc == 0 and wrote
        _assert_strict_finite(payload)
        assert payload["periods"] == 3

    def test_backtest_series_named_cumulative(self):
        res = SimpleNamespace(backtest=pd.Series([1.0, 1.23], name="cumulative"))
        rc, payload, _ = _run_with_output(["--synthetic"], res)
        assert rc == 0
        _assert_strict_finite(payload)
        assert payload["final_cumulative"] == pytest.approx(1.23)
        assert payload["periods"] == 2

    def test_backtest_ndarray_survives(self):
        res = SimpleNamespace(backtest=np.array([1.0, 1.5, 2.0]))
        rc, payload, _ = _run_with_output(["--synthetic"], res)
        assert rc == 0
        _assert_strict_finite(payload)
        assert payload["periods"] == 3

    def test_cumulative_nan_tail_coerced_finite(self):
        df = pd.DataFrame({"returns": [0.1, -0.1], "cumulative": [1.1, np.nan]})
        res = SimpleNamespace(backtest=df)
        rc, payload, _ = _run_with_output(["--synthetic"], res)
        assert rc == 0
        _assert_strict_finite(payload)
        assert payload["periods"] == 2

    def test_cumulative_inf_tail_coerced_finite(self):
        df = pd.DataFrame({"cumulative": [1.0, np.inf]})
        res = SimpleNamespace(backtest=df)
        rc, payload, _ = _run_with_output(["--synthetic"], res)
        assert rc == 0
        _assert_strict_finite(payload)

    def test_empty_dataframe_periods_zero_finite(self):
        res = SimpleNamespace(backtest=pd.DataFrame())
        rc, payload, _ = _run_with_output(["--synthetic"], res)
        assert rc == 0
        _assert_strict_finite(payload)
        assert payload["periods"] == 0

    def test_list_backtest(self):
        res = SimpleNamespace(backtest=[1.0, 1.1, 0.9])
        rc, payload, _ = _run_with_output(["--synthetic"], res)
        assert rc == 0
        _assert_strict_finite(payload)
        assert payload["final_cumulative"] == pytest.approx(0.9)
        assert payload["periods"] == 3

    def test_scalar_backtest(self):
        res = SimpleNamespace(backtest=1.234)
        rc, payload, _ = _run_with_output(["--synthetic"], res)
        assert rc == 0
        _assert_strict_finite(payload)


class TestBABDataErrorPropagation:
    def test_real_data_missing_benchmark_clean_error(self, capsys):
        rc = main(["--data", PRICES, "--benchmark", "NO_SUCH_BENCH"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "Error running strategy" in out or "Error" in out
        # must not be a raw traceback in stdout
        assert "Traceback" not in out

    def test_dry_run_real_data_missing_benchmark_clean(self, capsys):
        rc = main(["--dry-run", "--data", PRICES, "--benchmark", "NO_SUCH_BENCH"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "INVALID" in out or "Error" in out
        assert "Traceback" not in out

    def test_strategy_generic_exception_wrapped_to_error(self, monkeypatch, capsys):
        class BadStrategy:
            def __init__(self, config):
                pass

            def run(self, returns_df=None):
                raise RuntimeError("boom-generic")

        monkeypatch.setattr(cli_mod, "BABStrategy", BadStrategy)
        rc = main(["--synthetic"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "Error running strategy" in out
        assert "Traceback" not in out

    def test_strategy_babdataerror_clean(self, monkeypatch, capsys):
        class BadStrategy:
            def __init__(self, config):
                pass

            def run(self, returns_df=None):
                raise BABDataError("bab-boom")

        monkeypatch.setattr(cli_mod, "BABStrategy", BadStrategy)
        rc = main(["--synthetic"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "bab-boom" in out
        assert "Traceback" not in out
