"""C54 Step 2 regressions: surfacing silent ``except Exception: pass`` in cli.py.

Locks in the behavior that corrupt cumulative extraction now raises (and the CLI
surfaces it as rc=1 with a message) instead of silently fabricating a 1.0
cumulative return, and that ``_json_safe`` never returns a potentially
non-serializable object on an isoformat failure.
"""

from __future__ import annotations

from types import SimpleNamespace

import pandas as pd
import pytest

from strategies.betting_against_beta import cli


class _CorruptCumDF(pd.DataFrame):
    """DataFrame whose ``cumulative`` column cannot be read."""

    @property
    def _constructor(self):
        return _CorruptCumDF

    def __getitem__(self, key):
        if key == "cumulative":
            raise RuntimeError("corrupted cumulative column")
        return super().__getitem__(key)


class _BadCumSeries:
    """Series named like a cumulative column whose ``iloc[-1]`` fails."""

    name = "cumulative"
    iloc = None

    def __len__(self):
        return 5


class _BadLastCell:
    """Object with columns/iloc whose last-cell access fails."""

    columns = ["returns"]
    shape = (1, 1)
    iloc = None

    def __len__(self):
        return 1


def test_extract_cumulative_raises_on_corrupted_cumulative_column():
    df = _CorruptCumDF({"cumulative": [1.0, 2.0], "cum_x": [1.0, 9.9]})
    with pytest.raises(RuntimeError, match="corrupted cumulative column"):
        cli._extract_cumulative(SimpleNamespace(backtest=df))


def test_extract_cumulative_raises_on_cum_named_series_bad_iloc():
    with pytest.raises(TypeError):
        cli._extract_cumulative(SimpleNamespace(backtest=_BadCumSeries()))


def test_extract_cumulative_raises_on_bad_last_cell():
    with pytest.raises(TypeError):
        cli._extract_cumulative(SimpleNamespace(backtest=_BadLastCell()))


def test_extract_cumulative_valid_cumulative_column_unchanged():
    df = pd.DataFrame({"cumulative": [1.0, 1.1, 1.3]})
    assert cli._extract_cumulative(SimpleNamespace(backtest=df)) == 1.3


def test_extract_cumulative_valid_no_cum_column_unchanged():
    df = pd.DataFrame({"returns": [0.0, 0.1, 0.2]})
    assert cli._extract_cumulative(SimpleNamespace(backtest=df)) == 0.2


def test_main_cumulative_extraction_failure_surfaces_rc1(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "_extract_cumulative",
        lambda r: (_ for _ in ()).throw(RuntimeError("cum boom")),
    )
    rc = cli.main(["--synthetic"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "Error extracting cumulative return: cum boom" in out


def test_main_synthetic_still_prints_cumulative(capsys):
    rc = cli.main(["--synthetic"])
    assert rc == 0
    assert "Final cumulative return:" in capsys.readouterr().out


def test_json_safe_isoformat_fail_returns_str_not_raw():
    class HasIso:
        def isoformat(self):
            raise ValueError("no")

        def __str__(self):
            return "STRINGIFIED"

    out = cli._json_safe(HasIso())
    assert out == "STRINGIFIED"


def test_json_safe_valid_timestamp_unchanged():
    ts = pd.Timestamp("2024-01-01")
    out = cli._json_safe(ts)
    assert out == "2024-01-01T00:00:00"
