"""Regression tests for Campaign 11s: CLI validation adversarial edges.

Covers dry-run vs run parity on universe comma-splitting gaps proven in heavy campaign.
"""

import subprocess
import sys
import pytest

REAL = "tests/fixtures/real_market_prices.csv"


def run_cli(args, dry_run=False):
    cmd = [sys.executable, "-m", "strategies.betting_against_beta.cli", "--data", REAL, "--benchmark", "BTC"]
    if dry_run:
        cmd.append("--dry-run")
    cmd.extend(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


class TestUniverseCommaSplitting:
    """Universe comma tokens accepted by dry-run but rejected at run-time.

    These are proven gaps: dry-run validates config creation only, but does not
    validate that the universe tokens exist in the data columns. The run path
    performs overlap checking and fails cleanly when no overlap exists.
    """

    @pytest.mark.parametrize("universe_arg", [
        "BTC, ETH",       # comma with space
        "BTC,,ETH",       # double comma
        ",",              # single comma only
        ", ,",            # comma-space-comma
    ])
    def test_universe_comma_token_dry_run_allows(self, universe_arg):
        """Dry-run accepts comma-containing universe tokens (config creation succeeds)."""
        rc, out, err = run_cli(["--universe", universe_arg], dry_run=True)
        assert rc == 0, f"dry-run should accept config for '{universe_arg}': {err}"
        assert "Resolved BAB configuration" in out
        # Universe shows as single token (comma not split in dry-run)
        assert universe_arg in out or universe_arg.strip() in out

    @pytest.mark.parametrize("universe_arg", [
        "BTC, ETH",
        "BTC,,ETH",
        ",",
        ", ,",
    ])
    def test_universe_comma_token_run_rejects_no_overlap(self, universe_arg):
        """Run rejects comma-containing universe tokens (no overlap with data columns)."""
        rc, out, err = run_cli(["--universe", universe_arg], dry_run=False)
        assert rc == 1, f"run should reject '{universe_arg}': {out}"
        assert "has no overlap with data columns" in out
        assert "Traceback" not in out
        assert "Error running strategy" in out


class TestUniverseWhitespaceOnly:
    """Universe whitespace-only tokens rejected at config creation (both dry-run and run)."""

    @pytest.mark.parametrize("universe_arg", ["  ", "\t", "\n"])
    def test_universe_whitespace_only_rejected_both(self, universe_arg):
        """Whitespace-only universe rejected at config creation in both dry-run and run."""
        dry_rc, dry_out, dry_err = run_cli(["--universe", universe_arg], dry_run=True)
        run_rc, run_out, run_err = run_cli(["--universe", universe_arg], dry_run=False)

        assert dry_rc == 1, f"dry-run should reject whitespace-only: {dry_err}"
        assert run_rc == 1, f"run should reject whitespace-only: {run_err}"
        assert "--universe must contain at least one non-empty asset token" in dry_out
        assert "--universe must contain at least one non-empty asset token" in run_out


class TestValidationParityBaseline:
    """Baseline validation parity checks that must remain green."""

    def test_valid_universe_parity(self):
        """Valid universe shows parity between dry-run and run."""
        dry_rc, dry_out, dry_err = run_cli(["--universe", "BTC", "ETH"], dry_run=True)
        run_rc, run_out, run_err = run_cli(["--universe", "BTC", "ETH"], dry_run=False)

        assert dry_rc == 0
        assert run_rc == 0
        assert "Resolved BAB configuration" in dry_out
        assert "Final cumulative return" in run_out

    def test_invalid_rebalance_freq_empty_parity(self):
        """Empty rebalance-freq rejected in both dry-run and run."""
        dry_rc, dry_out, dry_err = run_cli(["--rebalance-freq", ""], dry_run=True)
        run_rc, run_out, run_err = run_cli(["--rebalance-freq", ""], dry_run=False)

        assert dry_rc == 1
        assert run_rc == 1
        assert "rebalance_freq must be a non-empty string" in dry_out
        assert "rebalance_freq must be a non-empty string" in run_out

    def test_negative_beta_window_parity(self):
        """Negative beta-window rejected in both dry-run and run."""
        dry_rc, dry_out, dry_err = run_cli(["--beta-window", "-1"], dry_run=True)
        run_rc, run_out, run_err = run_cli(["--beta-window", "-1"], dry_run=False)

        assert dry_rc == 1
        assert run_rc == 1
        assert "beta_window must be >= 1" in dry_out
        assert "beta_window must be >= 1" in run_out

    def test_negative_quantile_parity(self):
        """Negative quantile rejected in both dry-run and run."""
        dry_rc, dry_out, dry_err = run_cli(["--long-quantile", "-0.1"], dry_run=True)
        run_rc, run_out, run_err = run_cli(["--long-quantile", "-0.1"], dry_run=False)

        assert dry_rc == 1
        assert run_rc == 1
        assert "long_quantile must be in (0, 1)" in dry_out
        assert "long_quantile must be in (0, 1)" in run_out

    def test_negative_costs_parity(self):
        """Negative transaction costs rejected in both dry-run and run."""
        dry_rc, dry_out, dry_err = run_cli(["--transaction-costs", "-0.001"], dry_run=True)
        run_rc, run_out, run_err = run_cli(["--transaction-costs", "-0.001"], dry_run=False)

        assert dry_rc == 1
        assert run_rc == 1
        assert "transaction_costs must be >= 0" in dry_out
        assert "transaction_costs must be >= 0" in run_out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])