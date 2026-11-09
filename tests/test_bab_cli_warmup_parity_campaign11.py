"""Campaign11 slice (k): warmup/cumulative tail parity under leading NaNs.

HANDOFF item 3 target: "JSON summary parity when backtest has leading warmup
NaNs in cumulative (`_extract_cumulative`/coercion) — verify on a crafted
finite-leading-warmup case".

Probe (2026-11-09, HEAD `d5fd66f`, /tmp/probe_warmup_parity.py) showed the
contract already holds: `_extract_cumulative` reads the *last* row of the
cumulative column regardless of leading NaNs, `_coerce_finite_scalar` preserves
finite tail values, and the CLI summary stays strict-finite with tail parity
intact for warmup lengths 0/1/3/5. No production edit is justified (the
bug-fix rule requires a proven bug, and none exists).

This module LOCKS that invariant so a future refactor that regressed
`_extract_cumulative` ordering or the coercion default cannot silently break
the CLI JSON boundary.
"""
from __future__ import annotations

import datetime
import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.cli import (
    _build_output_summary,
    _coerce_finite_scalar,
    _extract_cumulative,
    _json_default,
    _json_safe,
)
from strategies.betting_against_beta.config import BABConfig


def _make_result(n_warmup: int, tail_value: float) -> SimpleNamespace:
    """Craft a BABResult-like object whose cumulative has leading NaN warmup."""
    idx = pd.date_range("2024-01-01", periods=n_warmup + 5, freq="D")
    cum = [np.nan] * n_warmup + [1.0, 1.02, 1.01, 0.99, tail_value]
    df = pd.DataFrame({"returns": [0.0] * len(idx), "cumulative": cum}, index=idx)
    r = SimpleNamespace()
    r.backtest = df
    r.config = BABConfig(benchmark="BTC", universe=["BTC", "ETH"])
    return r


class TestWarmupCumulativeTailParity:
    @pytest.mark.parametrize("n_warmup", [0, 1, 3, 5, 10])
    @pytest.mark.parametrize("tail_value", [1.05, 0.87, 1.5])
    def test_tail_value_preserved_through_extract_and_coerce(self, n_warmup, tail_value):
        res = _make_result(n_warmup, tail_value)
        extracted = _extract_cumulative(res)
        coerced = _coerce_finite_scalar(extracted, default=1.0)
        assert math.isfinite(coerced)
        assert coerced == pytest.approx(tail_value)

    @pytest.mark.parametrize("n_warmup", [0, 1, 3, 5])
    def test_summary_json_strict_finite_with_parity(self, n_warmup):
        res = _make_result(n_warmup, tail_value=1.05)
        cum_out = _coerce_finite_scalar(_extract_cumulative(res), default=1.0)
        summary = _build_output_summary(res, res.config, cum_out)
        payload = _json_safe(summary)
        dumped = json.dumps(payload, default=_json_default, allow_nan=False)
        for tok in ("NaN", "Infinity", "-Infinity"):
            assert tok not in dumped
        parsed = json.loads(dumped)
        assert math.isfinite(float(parsed["final_cumulative"]))
        assert parsed["final_cumulative"] == pytest.approx(1.05)
        assert parsed["periods"] == n_warmup + 5
        assert parsed["benchmark"] == "BTC"
        assert isinstance(parsed["universe"], list)

    def test_all_warmup_nan_yields_finite_default(self):
        # If the entire cumulative column is NaN (degenerate), the CLI path
        # must still produce a strict-finite summary (default 1.0), never raise.
        idx = pd.date_range("2024-01-01", periods=4, freq="D")
        df = pd.DataFrame({"returns": [0.0] * 4, "cumulative": [np.nan] * 4}, index=idx)
        res = SimpleNamespace(backtest=df, config=BABConfig(benchmark="BTC", universe=["BTC"]))
        cum_out = _coerce_finite_scalar(_extract_cumulative(res), default=1.0)
        assert math.isfinite(cum_out)
        summary = _build_output_summary(res, res.config, cum_out)
        payload = _json_safe(summary)
        dumped = json.dumps(payload, default=_json_default, allow_nan=False)
        for tok in ("NaN", "Infinity", "-Infinity"):
            assert tok not in dumped
        assert math.isfinite(float(json.loads(dumped)["final_cumulative"]))

    def test_leading_warmup_does_not_shift_periods_count(self):
        # periods must reflect the full backtest length (incl. warmup rows),
        # not only the finite tail — the CLI counts len(backtest).
        for n_warmup in (0, 2, 7):
            res = _make_result(n_warmup, tail_value=1.0)
            cum_out = _coerce_finite_scalar(_extract_cumulative(res), default=1.0)
            summary = _build_output_summary(res, res.config, cum_out)
            payload = _json_safe(summary)
            assert payload["periods"] == n_warmup + 5