"""P19-3 hard-reach coverage wins using real APIs:
execution.py:140-141,182-185 (PaperAdapter Timestamp fallbacks);
cli.py:75 (allow_live_execution terms mismatch), 836-838 (output path
validation), 893-894 (len() exception in period counting)."""

from __future__ import annotations

import argparse
from unittest import mock

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.cli import _build_adapter, main
from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.execution import (
    LiveExecutionAdapter,
    OrderBatch,
    OrderIntent,
    PaperAdapter,
)


class TestExecutionTimestampFallbacks:
    def test_price_for_timestamp_fallback(self):
        """execution.py:140-141 (pd.Timestamp(date_key) in sub.index path)."""
        dates = pd.date_range("2023-01-02", periods=2)
        prices = pd.DataFrame({"BTC": [100.0, 101.0]}, index=dates)
        adapter = PaperAdapter(prices_df=prices)
        # date_key as ISO string is not literally in the index, but the
        # Timestamp(date_key) conversion matches the first index entry.
        v = adapter._price_for("2023-01-02", "BTC")
        assert v == 100.0

    def test_adv_for_timestamp_fallback(self):
        """execution.py:182-185 (ADV lookup via pd.Timestamp(date_key))."""
        dates = pd.date_range("2023-01-02", periods=2)
        adv = pd.Series([1_000_000.0, 1_100_000.0], index=dates, name="ADV")
        adapter = PaperAdapter(adv_usd=adv)
        v = adapter._adv_for("2023-01-02", "BTC")
        assert v == 1_000_000.0

    def test_price_for_returns_none_when_no_match(self):
        """execution.py:142-144 (final return None after both lookups fail)."""
        dates = pd.date_range("2023-01-02", periods=2)
        prices = pd.DataFrame({"BTC": [100.0, 101.0]}, index=dates)
        adapter = PaperAdapter(prices_df=prices)
        assert adapter._price_for("1999-01-01", "BTC") is None


class TestCLILiveTermsMismatch:
    def test_allow_live_execution_terms_mismatch_raises(self):
        """cli.py:75 (accept_terms != _LIVE_ACCEPT_TERMS -> BABDataError)."""
        args = argparse.Namespace(
            adapter="live",
            exchange="binance",
            api_key_env="BAB_TEST_KEY",
            api_secret_env="BAB_TEST_SECRET",
            api_password_env=None,
            testnet=False,
            allow_live_execution=True,
            accept_terms="WRONG_TERMS",
        )
        with pytest.raises(BABDataError):
            _build_adapter(args)


class TestCLIOutputPathValidation:
    def test_paper_trading_bad_output_path_exits_1(self, capsys):
        """cli.py:836-838 (output path outside allowed dirs -> rc=1)."""
        bad = "/nonexistent-root-xyz/out.jsonl"
        rc = main(
            [
                "--synthetic",
                "--paper-trading",
                "--output",
                bad,
            ]
        )
        assert rc == 1
        captured = capsys.readouterr()
        assert "Error validating output path" in captured.out

    def test_paper_trading_parent_is_file_exits_1(self, capsys, tmp_path, monkeypatch):
        """cli.py:836-838 (output path under cwd but parent is a file -> mkdir
        raises NotADirectoryError -> BABDataError -> rc=1)."""
        monkeypatch.chdir(tmp_path)
        blocker = tmp_path / "blocker"
        blocker.write_text("not a directory")
        rc = main(
            [
                "--synthetic",
                "--paper-trading",
                "--output",
                "blocker/sub/out.jsonl",
            ]
        )
        assert rc == 1
        captured = capsys.readouterr()
        assert "Error validating output path" in captured.out


class TestCLILenException:
    def test_period_count_len_exception_handled(self, capsys):
        """cli.py:893-894 (len(bt) raises TypeError/ValueError -> periods=0)."""
        # Patch BABStrategy.run to return a result whose backtest __len__ raises.
        from strategies.betting_against_beta import cli as cli_mod
        from strategies.betting_against_beta.strategy import BABConfig, BABResult

        class BadBacktest:
            """Has a cumulative column (so _extract_cumulative returns a
            finite scalar via backtest["cumulative"].iloc[-1]) and a
            working __len__ for the line-990 empty check, but the later
            len(bt) call at cli.py:892-894 is made to raise by patching
            __len__ to raise after the first call."""

            columns = ["cumulative"]

            def __getitem__(self, col):
                class _Col:
                    def iloc(self_inner, idx):
                        return 1.0

                return _Col()

            def __len__(self):
                # First call (line 990 empty-check) returns 0; subsequent
                # calls raise to exercise the cli.py:893-894 except branch.
                if getattr(self, "_len_called", False):
                    raise TypeError("len() not supported")
                self._len_called = True
                return 0

        fake = BABResult.__new__(BABResult)
        fake.config = BABConfig()
        fake.weights = None
        fake.returns = None
        fake.betas = None
        fake.signals = None
        fake.backtest = BadBacktest()

        with mock.patch.object(
            cli_mod.BABStrategy, "run", return_value=fake
        ):
            rc = main(["--synthetic"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Periods: 0" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
