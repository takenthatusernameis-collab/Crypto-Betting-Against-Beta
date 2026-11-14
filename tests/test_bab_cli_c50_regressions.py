"""Regression tests for C50 proven gaps fixed in cli.py."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import cli as CLI


class TestCliJsonSerializationC50:
    """Regression tests for _json_default/_json_safe non-finite float coercion."""

    def test_json_default_numpy_array_inf_nan_coerced_to_zero(self):
        arr = np.array([1.0, np.inf, -np.inf, np.nan])
        out = CLI._json_default(arr)
        assert isinstance(out, list)
        assert len(out) == 4
        assert out[0] == 1.0
        assert out[1] == 0.0  # inf -> 0.0
        assert out[2] == 0.0  # -inf -> 0.0
        assert out[3] == 0.0  # nan -> 0.0

    def test_json_default_dataframe_inf_coerced_to_zero(self):
        df = pd.DataFrame({"a": [1, 2, np.inf], "b": ["x", "y", "z"]})
        out = CLI._json_default(df)
        assert isinstance(out, dict)
        assert "a" in out
        assert "b" in out
        assert out["a"][2] == 0.0  # inf -> 0.0

    def test_json_safe_nested_inf_nan_coerced_to_zero(self):
        obj = {"x": [1.0, np.nan], "y": {"z": float("inf")}, "w": (1, 2, -np.inf)}
        out = CLI._json_safe(obj)
        assert out["x"][1] == 0.0
        assert out["y"]["z"] == 0.0
        assert out["w"][2] == 0.0

    def test_json_safe_numpy_integer_and_bool_preserved(self):
        arr_int = np.array([1, 2, 3], dtype=np.int64)
        arr_bool = np.array([True, False], dtype=np.bool_)
        out_int = CLI._json_safe(arr_int)
        out_bool = CLI._json_safe(arr_bool)
        assert out_int == [1, 2, 3]
        assert out_bool == [True, False]


class TestCliArgParsingC50:
    """Regression tests for CLI argument validation returning rc=1."""

    def _run_cli(self, args):
        import io
        from contextlib import redirect_stderr, redirect_stdout

        buf_o, buf_e = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(buf_o), redirect_stderr(buf_e):
                rc = CLI.main(args)
        except SystemExit as exc:
            rc = exc.code
        return rc, buf_o.getvalue(), buf_e.getvalue()

    def test_beta_window_non_integer_returns_rc1(self):
        rc, out, err = self._run_cli(["--synthetic", "--beta-window", "not_a_number"])
        assert rc == 1, f"expected rc=1, got {rc}: {out} {err}"
        assert "must be an integer" in out + err

    def test_long_quantile_non_float_returns_rc1(self):
        rc, out, err = self._run_cli(["--synthetic", "--long-quantile", "not_a_number"])
        assert rc == 1, f"expected rc=1, got {rc}: {out} {err}"

    def test_short_quantile_non_float_returns_rc1(self):
        rc, out, err = self._run_cli(["--synthetic", "--short-quantile", "not_a_number"])
        assert rc == 1, f"expected rc=1, got {rc}: {out} {err}"

    def test_transaction_costs_inf_returns_rc1(self):
        rc, out, err = self._run_cli(["--synthetic", "--transaction-costs", "inf"])
        assert rc == 1, f"expected rc=1, got {rc}: {out} {err}"
        assert "must be finite" in out + err

    def test_transaction_costs_nan_returns_rc1(self):
        rc, out, err = self._run_cli(["--synthetic", "--transaction-costs", "nan"])
        assert rc == 1, f"expected rc=1, got {rc}: {out} {err}"

    def test_slippage_inf_returns_rc1(self):
        rc, out, err = self._run_cli(["--synthetic", "--slippage", "inf"])
        assert rc == 1, f"expected rc=1, got {rc}: {out} {err}"

    def test_unknown_flag_returns_rc2(self):
        rc, out, err = self._run_cli(["--bogus"])
        assert rc == 2, f"expected rc=2, got {rc}: {out} {err}"

    def test_version_flag_raises_system_exit_zero(self):
        # --version uses argparse's action="version" which calls sys.exit(0)
        with pytest.raises(SystemExit) as exc_info:
            CLI.main(["--version"])
        assert exc_info.value.code == 0

    def test_help_flag_raises_system_exit_zero(self):
        # --help uses argparse's action="help" which calls sys.exit(0)
        with pytest.raises(SystemExit) as exc_info:
            CLI.main(["--help"])
        assert exc_info.value.code == 0


class TestCliUniverseValidationC50:
    """Regression tests for --universe empty token stripping."""

    def _run_cli(self, args):
        import io
        from contextlib import redirect_stderr, redirect_stdout

        buf_o, buf_e = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(buf_o), redirect_stderr(buf_e):
                rc = CLI.main(args)
        except SystemExit as exc:
            rc = exc.code
        return rc, buf_o.getvalue(), buf_e.getvalue()

    def test_universe_with_empty_tokens_strips_and_succeeds(self):
        rc, out, err = self._run_cli(["--synthetic", "--universe", "BTC", "", "ETH", "   "])
        assert rc == 0, f"expected rc=0, got {rc}: {out} {err}"

    def test_universe_all_empty_tokens_returns_rc1(self):
        rc, out, err = self._run_cli(["--synthetic", "--universe", "", "   "])
        assert rc == 1, f"expected rc=1, got {rc}: {out} {err}"
        assert "must contain at least one non-empty asset token" in out + err

    def test_universe_followed_by_flag_uses_synthetic(self):
        # argparse with nargs='*' swallows the following flag as a value,
        # producing an empty list. That is *not* an explicit empty-token
        # request; the historical behavior (fall back to defaults/synthetic)
        # is preserved here so `--universe --synthetic` still runs.
        rc, out, err = self._run_cli(["--universe", "--synthetic"])
        assert rc == 0, f"expected rc=0, got {rc}: {out} {err}"


class TestCliOutputValidationC50:
    """Regression tests for --output path validation."""

    def test_validate_output_path_symlink_outside_allowed_base_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            link = Path(td) / "out.json"
            link.symlink_to("/etc/passwd")
            with pytest.raises(Exception):
                CLI._validate_output_path(str(link))

    def test_validate_output_path_permission_denied_parent_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td) / "noperm"
            parent.mkdir()
            parent.chmod(0o000)
            try:
                out_file = parent / "out.json"
                with pytest.raises(Exception):
                    CLI._validate_output_path(str(out_file))
            finally:
                parent.chmod(0o755)

    def test_dry_run_validates_output_path(self):
        import io
        from contextlib import redirect_stderr, redirect_stdout

        buf_o, buf_e = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(buf_o), redirect_stderr(buf_e):
                rc = CLI.main(["--synthetic", "--output", "/proc/nonexistent/x.json", "--dry-run"])
        except SystemExit as exc:
            rc = exc.code
        assert rc == 1, f"expected rc=1, got {rc}"


class TestCliCoerceFiniteScalarC50:
    """Regression tests for _coerce_finite_scalar."""

    def test_bool_true_coerces_to_1_0(self):
        assert CLI._coerce_finite_scalar(True, default=5.0) == 1.0

    def test_bool_false_coerces_to_0_0(self):
        assert CLI._coerce_finite_scalar(False, default=5.0) == 0.0


class TestCliRebalanceFreqC50:
    """Regression tests for _validate_rebalance_freq."""

    def test_quarterly_yearly_annual_accepted(self):
        CLI._validate_rebalance_freq("quarterly")
        CLI._validate_rebalance_freq("yearly")
        CLI._validate_rebalance_freq("annual")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
