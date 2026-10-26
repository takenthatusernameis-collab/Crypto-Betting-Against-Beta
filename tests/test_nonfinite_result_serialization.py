#!/usr/bin/env python3
"""Tests for nonfinite result serialization.

The Kilo agent loop must serialize intermediate results to JSON-safe
formats for persistence. Nonfinite floats (NaN, Infinity, -Infinity)
are not valid JSON and must be sanitized before serialization.
"""

from __future__ import annotations

import json
import math
from typing import Any

import pytest


def sanitize_nonfinite(obj: Any) -> Any:
    """Recursively replace nonfinite floats with sentinel strings for JSON safety."""
    if isinstance(obj, float):
        if math.isnan(obj):
            return "NaN"
        if math.isinf(obj):
            return "Infinity" if obj > 0 else "-Infinity"
        return obj
    if isinstance(obj, dict):
        return {k: sanitize_nonfinite(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_nonfinite(v) for v in obj]
    return obj


def is_json_safe(obj: Any) -> bool:
    """Return True if obj can be serialized to JSON without error."""
    try:
        json.dumps(obj, allow_nan=False)
        return True
    except (TypeError, ValueError):
        return False


class TestSanitizeNonfinite:
    """Tests for the nonfinite sanitizer."""

    def test_nan_becomes_string(self) -> None:
        assert sanitize_nonfinite(math.nan) == "NaN"

    def test_positive_infinity(self) -> None:
        assert sanitize_nonfinite(math.inf) == "Infinity"

    def test_negative_infinity(self) -> None:
        assert sanitize_nonfinite(-math.inf) == "-Infinity"

    def test_finite_float_unchanged(self) -> None:
        assert sanitize_nonfinite(3.14) == 3.14
        assert sanitize_nonfinite(-0.0) == -0.0

    def test_int_unchanged(self) -> None:
        assert sanitize_nonfinite(42) == 42

    def test_dict_with_nan(self) -> None:
        result = sanitize_nonfinite({"a": math.nan, "b": 1.0})
        assert result == {"a": "NaN", "b": 1.0}

    def test_nested_structure(self) -> None:
        obj = {"results": [math.inf, {"inner": math.nan}], "count": 2}
        result = sanitize_nonfinite(obj)
        assert result == {"results": ["Infinity", {"inner": "NaN"}], "count": 2}

    def test_none_handling(self) -> None:
        assert sanitize_nonfinite(None) is None

    def test_string_handling(self) -> None:
        assert sanitize_nonfinite("hello") == "hello"


class TestJsonSafety:
    """Tests for JSON serialization safety."""

    def test_nan_is_not_json_safe(self) -> None:
        assert is_json_safe(math.nan) is False

    def test_infinity_is_not_json_safe(self) -> None:
        assert is_json_safe(math.inf) is False

    def test_finite_is_json_safe(self) -> None:
        assert is_json_safe(1.0) is True

    def test_sanitized_nan_is_json_safe(self) -> None:
        assert is_json_safe(sanitize_nonfinite(math.nan)) is True

    def test_sanitized_infinity_is_json_safe(self) -> None:
        assert is_json_safe(sanitize_nonfinite(math.inf)) is True

    def test_round_trip_serialization(self) -> None:
        """Sanitized values should survive a JSON round-trip."""
        original = {"loss": math.nan, "accuracy": 0.95, "grad_norm": math.inf}
        sanitized = sanitize_nonfinite(original)
        serialized = json.dumps(sanitized)
        deserialized = json.loads(serialized)
        assert deserialized["loss"] == "NaN"
        assert deserialized["accuracy"] == 0.95
        assert deserialized["grad_norm"] == "Infinity"


class TestEdgeCases:
    """Edge case tests for serialization."""

    def test_zero_and_negative_zero(self) -> None:
        assert sanitize_nonfinite(0.0) == 0.0
        # -0.0 is finite, should be preserved.
        assert sanitize_nonfinite(-0.0) == -0.0

    def test_very_large_finite(self) -> None:
        val = 1e308
        assert sanitize_nonfinite(val) == val

    def test_empty_containers(self) -> None:
        assert sanitize_nonfinite([]) == []
        assert sanitize_nonfinite({}) == {}

    def test_mixed_types(self) -> None:
        obj = [1, "two", 3.0, math.nan, {"nested": math.inf}]
        result = sanitize_nonfinite(obj)
        assert result == [1, "two", 3.0, "NaN", {"nested": "Infinity"}]