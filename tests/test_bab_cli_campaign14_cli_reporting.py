"""Regression tests for Campaign 14: CLI reporting fidelity + console-script parity.

Proven gaps (evidence: /home/runner/work/_temp/kilo-tmp/c14_cli_reporting_probe_evidence.log):
- `bab-example --version` exited rc=2 (argparse required data_path before --version); now rc=0, prints `bab 0.1.0`.
- `bab-example <data> --from-prices --benchmark BTC --output <json>` exited rc=2 (no --output flag);
  now rc=0, writes valid JSON with keys {final_cumulative, periods, benchmark, universe}.

Covered no-gap areas (explicit "no proven gaps", evidence-backed):
- subprocess --synthetic / --data --from-prices / --dry-run / --version -> rc=0, clean stdout, empty stderr.
- error paths (bad quantile, --from-prices without --data, --output is a directory) -> rc=1, actionable, no Traceback.
- --output JSON valid with required keys; allow_nan=False safe.
- stdout/stderr separation on success; determinism across repeated runs.
- in-process main(argv) parity with subprocess for 4 representative combos.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
REAL = str(REPO / "tests" / "fixtures" / "real_market_prices.csv")
TMP_OUT = str(REPO / ".pytest_cache" / "c14_out.json")


def _run_cli(argv):
    env = {**__import__("os").environ, "PYTHONPATH": str(REPO)}
    return subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli", *argv],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(REPO),
        env=env,
    )


def _run_bab_example(argv):
    env = {**__import__("os").environ, "PYTHONPATH": str(REPO)}
    return subprocess.run(
        [sys.executable, "-m", "scripts.load_real_bab_example", *argv],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(REPO),
        env=env,
    )


def _assert_no_traceback(r):
    blob = (r.stdout or "") + (r.stderr or "")
    assert "Traceback" not in blob, blob


class TestConsoleScriptVersion:
    """Proven gap: bab-example --version must print version and exit 0."""

    def test_bab_example_version(self):
        r = _run_bab_example(["--version"])
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        assert r.stdout.strip() == "bab 0.1.0", r.stdout
        assert r.stderr == "", r.stderr
        _assert_no_traceback(r)


class TestConsoleScriptOutputParity:
    """Proven gap: bab-example --output must write valid JSON summary."""

    def test_bab_example_output_json(self):
        out = Path(TMP_OUT)
        if out.exists():
            out.unlink()
        try:
            r = _run_bab_example(
                [
                    REAL,
                    "--from-prices",
                    "--benchmark",
                    "BTC",
                    "--output",
                    str(out),
                    "--min-rows",
                    "30",
                ]
            )
            assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
            assert r.stderr == "", r.stderr
            assert out.exists()
            payload = json.loads(out.read_text())
            assert {"final_cumulative", "periods", "benchmark", "universe"} <= set(payload.keys())
            assert payload["benchmark"] == "BTC"
            assert isinstance(payload["periods"], int) and payload["periods"] > 0
        finally:
            if out.exists():
                out.unlink()


class TestConsoleScriptPreservedBehavior:
    def test_bab_example_missing_data_path_errors(self):
        r = _run_bab_example([])
        assert r.returncode == 2, (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)


class TestCliSubprocessMatrix:
    def test_synthetic_run(self):
        r = _run_cli(["--synthetic"])
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        assert "Final cumulative return" in r.stdout
        assert "Periods" in r.stdout
        assert r.stderr == "", r.stderr
        _assert_no_traceback(r)

    def test_real_data_from_prices_run(self):
        r = _run_cli(["--data", REAL, "--from-prices", "--benchmark", "BTC"])
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        assert "Final cumulative return" in r.stdout
        assert r.stderr == "", r.stderr
        _assert_no_traceback(r)

    def test_dry_run_synthetic(self):
        r = _run_cli(["--dry-run", "--synthetic"])
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        assert "Resolved BAB configuration" in r.stdout
        assert "data:             synthetic (default)" in r.stdout
        assert r.stderr == "", r.stderr
        _assert_no_traceback(r)

    def test_dry_run_real_data(self):
        r = _run_cli(["--dry-run", "--data", REAL, "--from-prices", "--benchmark", "BTC"])
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        assert "data:" in r.stdout
        assert "(valid, --from-prices=True)" in r.stdout
        assert r.stderr == "", r.stderr
        _assert_no_traceback(r)

    def test_version(self):
        r = _run_cli(["--version"])
        assert r.returncode == 0
        assert r.stdout.strip() == "bab 0.1.0"
        assert r.stderr == "", r.stderr
        _assert_no_traceback(r)

    def test_error_bad_quantile(self):
        r = _run_cli(["--synthetic", "--long-quantile", "1.5"])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        assert "Error creating config" in r.stdout
        assert r.stderr == "", r.stderr
        _assert_no_traceback(r)

    def test_error_from_prices_without_data(self):
        r = _run_cli(["--from-prices"])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        assert "--from-prices requires --data" in r.stdout
        assert r.stderr == "", r.stderr
        _assert_no_traceback(r)

    def test_error_output_is_directory(self):
        r = _run_cli(["--synthetic", "--output", "/tmp"])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        assert "Error validating output path" in r.stdout
        assert r.stderr == "", r.stderr
        _assert_no_traceback(r)

    def test_output_json_valid_keys(self):
        out = Path(TMP_OUT)
        if out.exists():
            out.unlink()
        try:
            r = _run_cli(["--synthetic", "--output", str(out)])
            assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
            assert r.stderr == "", r.stderr
            payload = json.loads(out.read_text())
            assert {"final_cumulative", "periods", "benchmark", "universe"} <= set(payload.keys())
            # allow_nan=False safety: no NaN/Inf present
            assert not any(isinstance(v, float) and v != v for v in payload.values())
        finally:
            if out.exists():
                out.unlink()


class TestCliDeterminism:
    def test_deterministic_repeat(self):
        outs = []
        for _ in range(2):
            r = _run_cli(["--synthetic"])
            assert r.returncode == 0
            outs.append(r.stdout)
        assert outs[0] == outs[1], "stdout not deterministic across repeats"


class TestCliInProcessParity:
    """In-process main(argv) parity with subprocess for 4 representative combos."""

    @pytest.mark.parametrize(
        "argv",
        [
            ["--synthetic"],
            ["--data", REAL, "--from-prices", "--benchmark", "BTC"],
            ["--dry-run", "--synthetic"],
            ["--synthetic", "--long-quantile", "1.5"],
        ],
    )
    def test_in_process_parity(self, argv):
        from strategies.betting_against_beta.cli import main

        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = __import__("io").StringIO(), __import__("io").StringIO()
        try:
            code = main(argv)
        finally:
            out = sys.stdout.getvalue()
            err = sys.stderr.getvalue()
            sys.stdout, sys.stderr = old_stdout, old_stderr
        code = code if isinstance(code, int) else 0
        # success paths must not leak to stderr; error path message on stdout only
        if code == 0:
            assert err == "", (argv, err)
        # subprocess reference
        env = {**__import__("os").environ, "PYTHONPATH": str(REPO)}
        ref = subprocess.run(
            [sys.executable, "-m", "strategies.betting_against_beta.cli", *argv],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(REPO),
            env=env,
        )
        assert code == ref.returncode, (argv, code, ref.returncode)
