"""Campaign11 slice (i): defensive CLI boundary invariants (proven, no production bug).

Probed this session (HEAD `7b4f89f`): `_json_safe`-first +
`json.dumps(..., default=_json_default, allow_nan=False)` stays `allow_nan=False`
-safe for `pd.NaT`, `datetime.date`/`time`, `np.complexfloating`, `Decimal` NaN/inf,
`pd.NA`, and nested containers; `_coerce_finite_scalar` returns a finite default for
`pd.NA`, `Decimal` NaN/inf, `None`, `np.nan`; `_extract_cumulative` never raises on
malformed backtest objects (Series/list/scalar/ndarray/empty); `--from-prices` on a
returns-like fixture is clean (rc 0/1, no traceback). No production edit is justified
(the bug-fix rule requires a proven bug). These tests LOCK IN the invariants so no
future change can silently regress the CLI JSON/finite boundary without failing.
"""
from __future__ import annotations

import datetime
import json
import math
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.cli import (
    _build_output_summary,
    _coerce_finite_scalar,
    _extract_cumulative,
    _json_default,
    _json_safe,
    main,
)
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.strategy import BABStrategy


class TestJsonSafetyInvariantSliceI:
    @pytest.mark.parametrize(
        "value",
        [
            pd.NaT,
            datetime.date(2026, 11, 9),
            datetime.time(12, 0, 0),
            np.complex64(1 + 2j),
            np.complex128(1 + 2j),
            np.float64(np.nan),
            np.float64(np.inf),
            np.float64(-np.inf),
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        ],
    )
    def test_json_safe_then_dumps_allow_nan_false_scalar(self, value):
        # Core invariant: _json_safe-first + allow_nan=False must not raise.
        payload = _json_safe(value)
        dumped = json.dumps(payload, default=_json_default, allow_nan=False)
        parsed = json.loads(dumped)  # round-trips as valid JSON
        if isinstance(parsed, (int, float)) and not isinstance(parsed, bool):
            assert math.isfinite(parsed)

    def test_json_safe_nested_pdnat_datetime_complex_decimal(self):
        obj = {
            "nat": pd.NaT,
            "date": datetime.date(2026, 1, 1),
            "time": datetime.time(1, 2, 3),
            "complex": np.complex128(3 + 4j),
            "decimal_nan": Decimal("NaN"),
            "nested": {"a": [pd.NaT, datetime.date(2026, 2, 2), np.complex64(1j)]},
        }
        payload = _json_safe(obj)
        dumped = json.dumps(payload, default=_json_default, allow_nan=False)
        parsed = json.loads(dumped)  # round-trips; Decimal("NaN") -> quoted "NaN" string
        assert parsed["nat"] == "NaT"
        assert parsed["decimal_nan"] == "NaN"
        assert isinstance(parsed["nested"]["a"], list)

    def test_coerce_finite_scalar_nullable_and_decimal(self):
        assert _coerce_finite_scalar(pd.NA) == 1.0
        assert _coerce_finite_scalar(pd.NA, default=0.0) == 0.0
        assert _coerce_finite_scalar(Decimal("NaN")) == 1.0
        assert _coerce_finite_scalar(Decimal("Infinity"), default=7.0) == 7.0
        assert _coerce_finite_scalar(Decimal("-Infinity")) == 1.0
        assert _coerce_finite_scalar(None) == 1.0
        assert math.isfinite(_coerce_finite_scalar(np.nan))


class TestExtractCumulativeNeverRaises:
    @pytest.mark.parametrize(
        "backtest",
        [
            pd.Series([np.nan, np.inf], name="cumulative"),
            pd.Series([1.0, 2.0]),
            [np.nan, np.inf, 3.0],
            np.array([np.nan, np.inf]),
            5.0,
            None,
            object(),
        ],
    )
    def test_extract_cumulative_never_raises(self, backtest):
        def make_result(bt):
            class FakeResult:
                pass

            FakeResult.backtest = bt
            return FakeResult()

        # Must not raise; result is None or a finite-coercible scalar handled by caller.
        try:
            out = _extract_cumulative(make_result(backtest))
        except Exception:  # pragma: no cover - defensive; probe showed no raise path
            pytest.fail(f"_extract_cumulative raised for {backtest!r}")
        # Coercion through the CLI path must yield a finite default when non-finite.
        cum_out = _coerce_finite_scalar(out, default=1.0)
        assert math.isfinite(cum_out)


class TestBuildOutputSummaryExoticConfig:
    def test_build_output_summary_exotic_universe_benchmark(self, tmp_path):
        class FakeConfig:
            universe = [None, b"bytes_asset", np.float64(np.inf), pd.NaT, object()]
            benchmark = np.float64(np.inf)

        class FakeResult:
            backtest = pd.DataFrame({"cumulative": [1.0, np.nan, np.inf]})

        summary = _build_output_summary(FakeResult(), FakeConfig(), cum_out=np.inf)
        payload = _json_safe(summary)
        dumped = json.dumps(payload, default=_json_default, allow_nan=False)
        for tok in ("NaN", "Infinity", "-Infinity"):
            assert tok not in dumped
        parsed = json.loads(dumped)
        assert math.isfinite(float(parsed["final_cumulative"]))
        assert isinstance(parsed["universe"], list)


class TestFromPricesReturnsLikeFixtureClean:
    def test_from_prices_on_returns_json_no_traceback(self, capsys):
        rc = main(
            [
                "--dry-run",
                "--data",
                "tests/fixtures/returns.json",
                "--from-prices",
                "--benchmark",
                "BTC",
            ]
        )
        out = capsys.readouterr().out
        assert "Traceback" not in out
        assert rc in (0, 1)
