"""Regression tests for Campaign 11ab: CLI surface edges.

Proven gaps (evidence: /home/runner/work/_temp/kilo-tmp/c11_cli_surface_probe_evidence.log):
- --from-prices without --data silently fell back to synthetic (rc=0, misleading);
  now rejected cleanly (rc=1, no Traceback).

Covered no-gap areas (explicit "no proven gaps", evidence-backed):
- --version alone / with data / with synthetic -> rc=0, prints version.
- --output unwritable path / existing directory -> rc=1, no Traceback.
- --output nonexistent parent dir -> rc=0, parents created, file written.
- empty / whitespace-only --universe -> rc=1, no Traceback.
- unknown flag -> rc=2; --help -> rc=0; nonexistent --data -> rc=1.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
REAL = str(REPO / "tests" / "fixtures" / "real_market_prices.csv")


def _run(argv):
    env = {**__import__("os").environ, "PYTHONPATH": str(REPO)}
    return subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli"] + argv,
        capture_output=True, text=True, timeout=120, cwd=str(REPO), env=env,
    )


def _assert_no_traceback(r):
    blob = (r.stdout or "") + (r.stderr or "")
    assert "Traceback" not in blob, blob


class TestFromPricesRequiresData:
    """Proven gap: --from-prices without --data must not silently run synthetic."""

    def test_from_prices_without_data_rejected(self):
        r = _run(["--from-prices", "--benchmark", "BTC"])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        assert "--from-prices requires --data" in r.stdout
        _assert_no_traceback(r)

    def test_from_prices_without_data_dry_run_rejected(self):
        r = _run(["--dry-run", "--from-prices", "--benchmark", "BTC"])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        assert "--from-prices requires --data" in r.stdout
        _assert_no_traceback(r)

    def test_from_prices_with_data_still_ok(self):
        r = _run(["--data", REAL, "--from-prices", "--benchmark", "BTC"])
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        assert "Final cumulative return" in r.stdout


class TestCliVersionEdges:
    def test_version_alone(self):
        r = _run(["--version"])
        assert r.returncode == 0
        assert r.stdout.strip() == "bab 0.1.0"
        _assert_no_traceback(r)

    def test_version_with_data(self):
        r = _run(["--version", "--data", REAL, "--from-prices"])
        assert r.returncode == 0
        assert r.stdout.strip() == "bab 0.1.0"

    def test_version_with_synthetic(self):
        r = _run(["--version", "--synthetic"])
        assert r.returncode == 0
        assert r.stdout.strip() == "bab 0.1.0"


class TestCliOutputEdges:
    def test_output_unwritable(self):
        r = _run(["--synthetic", "--output", "/root/unwritable_c11ab/out.json"])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)

    def test_output_is_directory(self):
        r = _run(["--synthetic", "--output", "/tmp"])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)

    def test_output_nonexistent_parent_created(self):
        out = Path("/tmp/c11ab_nonexistent_parent/deep/out.json")
        if out.exists():
            out.unlink()
        try:
            r = _run(["--synthetic", "--output", str(out)])
            assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
            assert out.exists()
            payload = json.loads(out.read_text())
            assert "final_cumulative" in payload
        finally:
            if out.exists():
                out.unlink()
            parent = out.parent
            # best-effort cleanup of empty created dirs
            for p in [parent, parent.parent]:
                try:
                    p.rmdir()
                except OSError:
                    pass


class TestCliUniverseEdges:
    @pytest.mark.parametrize("universe_arg", ["", "   "])
    def test_universe_empty_or_whitespace_rejected(self, universe_arg):
        r = _run(["--synthetic", "--universe", universe_arg])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        assert "--universe must contain at least one non-empty asset token" in r.stdout
        _assert_no_traceback(r)


class TestCliArgparseEdges:
    def test_unknown_flag(self):
        r = _run(["--bogus"])
        assert r.returncode == 2
        _assert_no_traceback(r)

    def test_help_alone(self):
        r = _run(["--help"])
        assert r.returncode == 0
        assert "Betting Against Beta" in r.stdout


class TestCliDataEdges:
    def test_nonexistent_data_rejected(self):
        r = _run(["--data", "/nonexistent_c11ab.csv", "--from-prices"])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)

    def test_dry_run_output_unwritable(self):
        r = _run(["--dry-run", "--synthetic", "--output", "/root/unwritable_c11ab/out.json"])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)
