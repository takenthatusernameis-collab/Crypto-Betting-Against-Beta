"""Cross-version determinism regression for P38/P39 artifact generation (P39 WP0).

Contract (from HANDOFF.md P39 WP0):

* ``_round_floats`` produces byte-identical JSON regardless of trailing-ULP
  noise: signed zero ``-0.0`` is normalized to ``0.0`` and floats are rounded
  to 12 significant digits.
* ``strategies.betting_against_beta.reconciliation._checksum`` rounds before
  hashing, so payloads that differ only by ~1 ULP (or by signed zero) hash to
  the same SHA-256. A deliberately un-round-tripped float is shown to diverge,
  which is exactly the drift the canonicalization prevents.
* The pure ``build_*()`` summary builders are deterministic: re-running them
  twice yields byte-identical JSON.

These are regression guards for the determinism layer, not new evidence. They
do not write artifacts and use only committed/synthetic inputs.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER_SCRIPT = REPO_ROOT / "scripts" / "bab_p39_regime_conditional.py"

from scripts import bab_p39_regime_conditional as p39regime
from strategies.betting_against_beta import reconciliation


# --------------------------------------------------------------------------- #
# _round_floats: signed-zero normalization + 12-sig-fig rounding
# --------------------------------------------------------------------------- #
def test_round_floats_normalizes_signed_zero():
    assert p39regime._round_floats(-0.0) == 0.0
    assert math.copysign(1.0, p39regime._round_floats(-0.0)) == 1.0
    # Nested containers preserve the normalization.
    nested = p39regime._round_floats({"a": [-0.0, {"b": -0.0}]})
    assert nested == {"a": [0.0, {"b": 0.0}]}
    assert math.copysign(1.0, nested["a"][1]["b"]) == 1.0


def test_round_floats_is_twelve_significant_digits():
    raw = 0.1234567890123456
    expected = float(f"{raw:.12g}")
    assert p39regime._round_floats(raw) == expected
    # Non-finite values pass through unchanged.
    assert math.isnan(p39regime._round_floats(float("nan")))
    assert math.isinf(p39regime._round_floats(float("inf")))


def test_round_floats_makes_json_byte_identical():
    noisy = {"x": math.nextafter(0.1, 1.0), "y": -0.0, "z": [1.0000000000000002]}
    clean = {"x": 0.1, "y": 0.0, "z": [1.0]}
    noisy_bytes = json.dumps(p39regime._round_floats(noisy), sort_keys=True)
    clean_bytes = json.dumps(p39regime._round_floats(clean), sort_keys=True)
    assert noisy_bytes == clean_bytes


def test_unrounded_float_would_diverge():
    """The un-round-tripped payload must differ, proving rounding is load-bearing."""
    raw = {"x": math.nextafter(0.1, 1.0)}
    rounded = p39regime._round_floats(raw)
    assert json.dumps(raw, sort_keys=True) != json.dumps(rounded, sort_keys=True)


# --------------------------------------------------------------------------- #
# reconciliation._checksum: round-before-hash stability
# --------------------------------------------------------------------------- #
def test_checksum_stable_under_ulp_perturbation():
    a = {"alpha": 0.1, "beta": 1.0 / 3.0, "gamma": [1.0, 2.0]}
    b = {
        "alpha": math.nextafter(0.1, 1.0),
        "beta": math.nextafter(1.0 / 3.0, 1.0),
        "gamma": [math.nextafter(1.0, 1.0), 2.0],
    }
    assert reconciliation._checksum(a) == reconciliation._checksum(b)


def test_checksum_stable_under_signed_zero():
    assert reconciliation._checksum({"x": -0.0}) == reconciliation._checksum({"x": 0.0})


def test_checksum_ignores_embedded_checksum_key():
    payload = {"a": 1.0, "b": 2.0}
    with_sum = dict(payload, checksum="deadbeef")
    assert reconciliation._checksum(payload) == reconciliation._checksum(with_sum)


def test_checksum_is_deterministic_sha256():
    payload = {"a": 0.1, "b": [1.0, 2.0]}
    first = reconciliation._checksum(payload)
    second = reconciliation._checksum(payload)
    assert first == second
    assert len(first) == 64
    int(first, 16)  # valid hex


def test_unrounded_payload_checksum_would_diverge():
    """A payload whose floats are NOT canonicalized hashes differently.

    This demonstrates that the round-before-hash step in ``_checksum`` is what
    makes near-identical float payloads converge; without it the SHA-256 differs.
    """
    a = {"x": 0.1}
    b = {"x": math.nextafter(0.1, 1.0)}
    raw_a = hashlib.sha256(
        json.dumps(a, sort_keys=True, allow_nan=False).encode("utf-8")
    ).hexdigest()
    raw_b = hashlib.sha256(
        json.dumps(b, sort_keys=True, allow_nan=False).encode("utf-8")
    ).hexdigest()
    assert raw_a != raw_b, "test premise broken: raw JSON must differ"
    assert reconciliation._checksum(a) == reconciliation._checksum(b)


# --------------------------------------------------------------------------- #
# Pure build_*() byte-identity (re-run twice)
# --------------------------------------------------------------------------- #
def test_regime_summary_build_is_byte_identical_across_runs():
    first = json.dumps(p39regime.build_summary(), indent=2, sort_keys=True)
    second = json.dumps(p39regime.build_summary(), indent=2, sort_keys=True)
    assert first == second


def test_runner_script_exists():
    assert RUNNER_SCRIPT.is_file(), f"missing {RUNNER_SCRIPT}"


def test_no_ruff_errors_on_new_files():
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(__file__)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"ruff must pass: {result.stdout} {result.stderr}"
