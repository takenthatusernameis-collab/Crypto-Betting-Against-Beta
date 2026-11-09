"""Campaign11 slice (h): defensive JSON/serialization invariant + malformed fixture runs.

Evidence: CLI writes `--output` via `_json_safe` (sanitize-first) then
`json.dumps(..., default=_json_default, allow_nan=False)`. `_json_safe` leaves
`np.datetime64` unchanged (no isoformat attr) but `_json_default` stringifies it;
np.void/bytes stringify; non-finite `np.floating`/float are coerced to 0.0 by
`_json_safe` while `_json_default` alone would stringify some cases — the
`_json_safe`-first ordering is the safety invariant. No production changes.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.cli import (
    _build_output_summary,
    _coerce_finite_scalar,
    _json_default,
    _json_safe,
    main,
)
from strategies.betting_against_beta.config import BABConfig
from strategies.betting_against_beta.strategy import BABStrategy


class TestJsonSafetyInvariant:
    def test_output_path_uses_safe_first_for_nested_exotic_types(self, tmp_path):
        """Prove _json_safe-first produces allow_nan=False-safe JSON for exotic payloads."""
        obj = {
            "dt64": np.datetime64("2024-01-02"),
            "void": np.void(b"ab"),
            "bytes": b"hi",
            "inf": np.float64(np.inf),
            "nan": np.float64(np.nan),
            "neg_inf": float("-inf"),
            "arr": np.array([1.0, np.nan, np.inf]),
            "nested": [{"t": np.datetime64("2024-01-03"), "v": np.float64(-np.inf)}],
            "ts": pd.Timestamp("2024-01-04T00:00:00Z"),
            "idx": pd.Index(["BTC", "ETH"]),
            "ser": pd.Series([np.nan, 1.5], name="x"),
        }
        payload = _json_safe(obj)
        dumped = json.dumps(payload, default=_json_default, allow_nan=False)
        for tok in ("NaN", "Infinity", "-Infinity"):
            assert tok not in dumped
        parsed = json.loads(dumped)
        assert parsed["inf"] == 0.0
        assert parsed["nan"] == 0.0
        assert parsed["neg_inf"] == 0.0
        assert parsed["arr"] == [1.0, 0.0, 0.0]

    def test_json_default_alone_datetime64_stringifies(self):
        # Evidence for invariant: default handles np.datetime64 via str fallback (no isoformat).
        v = np.datetime64("2024-01-02")
        out = _json_default(v)
        assert isinstance(out, str)
        assert "2024-01-02" in out

    def test_json_safe_coerces_nonfinite_np_floating(self):
        assert _json_safe(np.float64(np.inf)) == 0.0
        assert _json_safe(np.float32(np.nan)) == 0.0
        assert math.isfinite(_json_safe(np.float64(1.25)))

    def test_coerce_finite_scalar_nonfinite_defaults(self):
        assert _coerce_finite_scalar(np.nan) == 1.0
        assert _coerce_finite_scalar(np.inf, default=2.0) == 2.0
        assert _coerce_finite_scalar(None, default=3.0) == 3.0


class TestMalformedCommittedFixturesCli:
    @pytest.mark.parametrize(
        "path",
        [
            "tests/fixtures/all_nan_column.csv",
            "tests/fixtures/benchmark_nan_window.csv",
            "tests/fixtures/junk_columns.csv",
            "tests/fixtures/real_data_defects.csv",
            "tests/fixtures/messy_returns.csv",
            "tests/fixtures/non_monotonic_dates.csv",
            "tests/fixtures/returns.json",
        ],
    )
    def test_dry_run_committed_fixture_clean(self, path, capsys):
        rc = main(["--dry-run", "--data", path])
        out = capsys.readouterr().out
        assert rc == 0, out
        assert "INVALID" not in out
        assert "Traceback" not in out

    def test_degenerate_metrics_run_finite_output(self, tmp_path, capsys):
        outp = tmp_path / "deg.json"
        rc = main(["--data", "tests/fixtures/degenerate_metrics.csv", "--benchmark", "BTC", "--output", str(outp)])
        out = capsys.readouterr().out
        assert rc == 0, out
        assert "Traceback" not in out
        payload = json.loads(outp.read_text())
        json.dumps(payload, allow_nan=False)
        assert math.isfinite(float(payload["final_cumulative"]))
        assert payload["periods"] == 5

    def test_real_data_defects_run_finite_output(self, tmp_path, capsys):
        outp = tmp_path / "defects.json"
        rc = main([
            "--data", "tests/fixtures/real_data_defects.csv",
            "--benchmark", "BTC", "--output", str(outp),
        ])
        out = capsys.readouterr().out
        assert rc == 0, out
        assert "Traceback" not in out
        payload = json.loads(outp.read_text())
        json.dumps(payload, allow_nan=False)
        fc = payload["final_cumulative"]
        assert isinstance(fc, (int, float)) and not isinstance(fc, bool)
        assert math.isfinite(float(fc))
        assert isinstance(payload["periods"], int)

    def test_from_prices_not_a_price_file_clean_error_or_valid(self, capsys):
        # returns.json is not a prices file; CLI should be clean (valid/error, no traceback).
        rc = main(["--dry-run", "--data", "tests/fixtures/returns.json", "--from-prices"])
        out = capsys.readouterr().out
        assert "Traceback" not in out
        assert rc in (0, 1)
