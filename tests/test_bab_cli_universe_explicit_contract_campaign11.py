"""Campaign11 slice (k): explicit --universe contract hardening (evidence-first).

Two production defects found by probe this session (HEAD `57e6f13`, clean) and
fixed with minimal regression tests:

1. **Empty/whitespace-only `--universe` tokens silently dropped the whole
   explicit universe.** `cli.py` collapsed `--universe ""` / `"   "` to
   `universe=None`, so the run fell back to the data-derived default universe
   and *reported a universe the caller never asked for* (e.g. `--universe ""`
   reported the full default set instead of erroring). Now any explicit
   `--universe` with no surviving non-empty tokens raises a clean
   `BABConfigError` (rc=1, no traceback). The distinct argparse case
   `--universe --synthetic` (empty list from flag-swallowing) still falls back
   to synthetic — that is preserved, not a regression.

2. **Explicit non-default universe with zero overlap silently fell back to the
   data-derived universe.** `config.py:resolved_universe` returned
   `[c for c in available if c != benchmark]` when the configured universe had
   no overlap with the data columns, so `--universe DOGE` on a fixture without
   DOGE reported the full default universe (BTC, ETH, ...) rather than the
   requested (empty) universe. Now `resolved_universe` raises `BABConfigError`
   for an explicit non-default universe with zero overlap.

Both fixes are end-to-end at the CLI boundary; the two old fallback tests that
asserted the buggy behavior were updated to assert the corrected contract.
No gate-closed module (`beta.py`, `data_loader.py`) was touched.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
REAL = "tests/fixtures/real_market_prices.csv"


def _run_cli(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli", *argv],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
    )


def _out_json(path: Path) -> dict:
    return json.loads(path.read_text())


class TestUniverseEmptyTokenCleanError:
    """--universe with only empty/whitespace tokens must fail cleanly."""

    @pytest.mark.parametrize("token", ["", "   ", "\t"])
    def test_empty_token_rejects(self, tmp_path: Path, token: str):
        out = tmp_path / "out.json"
        res = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--universe", token, "--output", str(out),
        ])
        assert res.returncode == 1, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        assert "Traceback" not in (res.stdout + res.stderr)
        assert "at least one non-empty asset token" in res.stdout

    def test_mixed_empty_and_real_keeps_real(self, tmp_path: Path):
        # Empty tokens are stripped; surviving real tokens are honored.
        out = tmp_path / "out.json"
        res = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--universe", "", "ETH", "   ", "SOL", "--output", str(out),
        ])
        assert res.returncode == 0, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        assert "Traceback" not in (res.stdout + res.stderr)
        d = _out_json(out)
        assert d["universe"] == ["ETH", "SOL"]

    def test_universe_followed_by_flag_uses_synthetic(self, tmp_path: Path):
        # argparse with nargs='*' swallows the following flag as a value,
        # producing an empty list. That is *not* an explicit empty-token
        # request; the historical behavior (fall back to defaults/synthetic)
        # is preserved here so `--universe --synthetic` still runs.
        out = tmp_path / "out.json"
        res = _run_cli(["--universe", "--synthetic", "--output", str(out)])
        assert res.returncode == 0, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        assert "Traceback" not in (res.stdout + res.stderr)


class TestUniverseZeroOverlapCleanError:
    """Explicit non-default universe with zero overlap must fail cleanly."""

    def test_all_absent_tokens_reject(self, tmp_path: Path):
        out = tmp_path / "out.json"
        res = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--universe", "DOGE", "ZZZ", "--output", str(out),
        ])
        assert res.returncode == 1, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        assert "Traceback" not in (res.stdout + res.stderr)
        assert "no overlap" in res.stdout

    def test_present_token_not_dropped_to_default(self, tmp_path: Path):
        # Regression anchor: --universe LINK (present in data) must report
        # LINK only, not the default universe.
        out = tmp_path / "out.json"
        res = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC",
            "--universe", "LINK", "--output", str(out),
        ])
        assert res.returncode == 0, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        d = _out_json(out)
        assert d["universe"] == ["LINK"]

    def test_omitted_universe_unchanged(self, tmp_path: Path):
        # Omitting --universe still derives the default universe (no regression).
        out = tmp_path / "out.json"
        res = _run_cli([
            "--data", REAL, "--from-prices", "--benchmark", "BTC", "--output", str(out),
        ])
        assert res.returncode == 0, f"rc={res.returncode}\n{res.stderr}\n{res.stdout}"
        d = _out_json(out)
        assert d["universe"] == ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT"]