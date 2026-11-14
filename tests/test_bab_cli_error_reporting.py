"""CLI error-path/reporting robustness (campaign11 slice d).

Evidence-first against current CLI behavior:
- --dry-run --data <missing> prints resolved config, reports INVALID, rc=1.
- --output pointing at an existing directory -> _validate_output_path rc=1.
- --output under an unwritable parent (best-effort chmod) -> rc=1.
- Nonexistent --data in a real run -> rc=1 with actionable error.
No external data; uses synthetic/fixtures and tmp_path only.
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

from strategies.betting_against_beta.cli import main


def test_dry_run_missing_data_returns_nonzero_and_no_crash(capsys):
    rc = main(["--dry-run", "--data", "/tmp/bab_campaign11_missing_data_xyz.csv"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "INVALID" in out or "Error" in out or "not found" in out.lower()


def test_dry_run_missing_data_from_prices_returns_nonzero(capsys):
    rc = main(
        [
            "--dry-run",
            "--from-prices",
            "--data",
            "/tmp/bab_campaign11_missing_prices_xyz.csv",
            "--benchmark",
            "BTC",
        ]
    )
    assert rc == 1
    out = capsys.readouterr().out
    assert "INVALID" in out or "not found" in out.lower()


def test_output_path_is_existing_directory_fails_cleanly(tmp_path, capsys):
    out_dir = tmp_path / "as_dir"
    out_dir.mkdir()
    rc = main(["--synthetic", "--output", str(out_dir), "--beta-window", "30"])
    assert rc == 1
    captured = capsys.readouterr().out
    assert "directory" in captured.lower() or "Error" in captured
    assert out_dir.is_dir()
    assert not (out_dir / "out.json").exists()


def test_dry_run_output_path_is_existing_directory_fails_cleanly(tmp_path, capsys):
    out_dir = tmp_path / "as_dir"
    out_dir.mkdir()
    rc = main(["--dry-run", "--synthetic", "--output", str(out_dir), "--beta-window", "30"])
    assert rc == 1
    captured = capsys.readouterr().out
    assert "directory" in captured.lower() or "Error" in captured


def test_output_path_unwritable_parent_best_effort(tmp_path, capsys):
    ro = tmp_path / "ro"
    ro.mkdir()
    os.chmod(ro, stat.S_IRUSR | stat.S_IXUSR)
    target = ro / "out.json"
    try:
        rc = main(["--synthetic", "--output", str(target), "--beta-window", "30"])
        if os.access(str(ro), os.W_OK):
            pytest.skip("filesystem did not enforce read-only directory permissions")
        assert rc == 1
        out = capsys.readouterr().out
        assert "Error" in out or "writable" in out.lower() or "output" in out.lower()
        assert not target.exists()
    finally:
        os.chmod(ro, stat.S_IRWXU)


def test_nonexistent_data_real_run_returns_nonzero(capsys):
    rc = main(["--data", "/tmp/bab_campaign11_missing_real_xyz.csv", "--benchmark", "BTC"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "Error" in out or "not found" in out.lower() or "INVALID" in out


def test_successful_synthetic_output_schema_stable_with_explicit_flags(tmp_path):
    out = tmp_path / "out.json"
    rc = main(
        [
            "--synthetic",
            "--output",
            str(out),
            "--benchmark",
            "BTC",
            "--beta-window",
            "30",
            "--long-quantile",
            "0.3",
            "--short-quantile",
            "0.3",
            "--rebalance-freq",
            "daily",
            "--transaction-costs",
            "0.0",
            "--slippage",
            "0.0",
        ]
    )
    assert rc == 0
    payload = json.loads(out.read_text())
    for key in ("final_cumulative", "periods", "benchmark", "universe"):
        assert key in payload
    assert payload["benchmark"] == "BTC"
    assert payload["periods"] > 0


def test_dry_run_valid_prices_fixture_rc0(tmp_path, capsys):
    # Evidence-first: CLI accepts --dry-run --data <existing fixture> --from-prices
    rc = main(
        [
            "--dry-run",
            "--data",
            "tests/fixtures/real_market_prices.csv",
            "--from-prices",
            "--benchmark",
            "BTC",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "valid" in out.lower() or "Resolved" in out


def test_dry_run_data_directory_returns_nonzero(tmp_path, capsys):
    data_dir = tmp_path / "prices.csv"  # name like file but is dir
    data_dir.mkdir()
    rc = main(["--dry-run", "--data", str(data_dir), "--from-prices"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "INVALID" in out or "directory" in out.lower() or "Error" in out
