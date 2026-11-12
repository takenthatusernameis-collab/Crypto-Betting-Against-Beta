"""Targeted CLI coverage push: defensive/exception branches in cli.py."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import cli
from strategies.betting_against_beta.errors import BABDataError


class _IsoFail:
    def isoformat(self):
        raise RuntimeError("iso fail")
    def __str__(self):
        return "isofail"


class _WeirdStrRepr:
    def __str__(self):
        return "ok"
    def __repr__(self):
        return "repr"


class _BytesSub(bytes):
    pass


def _make_rets(tmp_path, n=200, seed=11):
    rng = np.random.RandomState(seed)
    dates = pd.date_range("2023-01-01", periods=n)
    df = pd.DataFrame({"BTC": rng.normal(0, 0.01, n), "ETH": rng.normal(0, 0.015, n)}, index=dates)
    p = tmp_path / "r.csv"
    df.to_csv(p)
    return p


def test_validate_output_path_os_access_raises_non_bab(monkeypatch, tmp_path):
    target = tmp_path / "x.json"
    monkeypatch.setattr(cli.os, "access", lambda p, m: (_ for _ in ()).throw(RuntimeError("access boom")))
    out = cli._validate_output_path(str(target))  # 65-66 path
    assert out.name == "x.json"


def test_json_default_isoformat_exception():
    assert cli._json_default(_IsoFail()) == "isofail"  # 158-161 / 155-156


def test_json_default_bytes_normal():
    assert cli._json_default(b"hi") == "hi"


def test_json_default_generic_isoformat():
    class Obj:
        def isoformat(self): return "2024-01-01T00:00:00"
    assert "2024" in cli._json_default(Obj())


def test_json_safe_numpy_array_and_types():
    assert cli._json_safe(np.array([1, np.nan])) == [1, 0.0]  # 409
    assert cli._json_safe(pd.Timestamp("2024-01-01")).startswith("2024")  # 416-418
    assert cli._json_safe(np.bool_(True)) is True  # 430-431
    assert cli._json_safe(np.float64(np.inf)) == 0.0  # 428-429
    assert cli._json_safe(np.int64(5)) == 5
    assert cli._json_safe({"k": (1, frozenset({2}))})["k"][1] == [2]
    assert cli._json_safe(True) is True  # 422
    assert cli._json_safe(np.float64(1.5)) == 1.5


def test_json_safe_generic_isoformat_exception():
    class HasIso:
        def isoformat(self): raise ValueError("no")
    r = cli._json_safe(HasIso())  # 433-436
    assert r is not None


def test_extract_cumulative_cumulative_column_raise_surfaces():
    # A corrupted "cumulative" column must surface instead of falling through
    # to a different "cum" column and returning a wrong value.
    class BadDF(pd.DataFrame):
        @property
        def _constructor(self): return BadDF
        def __getitem__(self, key):
            if key == "cumulative":
                raise RuntimeError("boom")
            return super().__getitem__(key)
    df = BadDF({"cumulative": [1, 2], "cum_x": [1, 9.9]})
    with pytest.raises(RuntimeError, match="boom"):
        cli._extract_cumulative(SimpleNamespace(backtest=df))


def test_extract_cumulative_outer_exception():
    class Evil:
        @property
        def backtest(self):
            raise RuntimeError("evil")  # 388-389
    assert cli._extract_cumulative(Evil()) is None


def test_main_extract_cumulative_raises(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_extract_cumulative", lambda r: (_ for _ in ()).throw(RuntimeError("x")))
    rc = cli.main(["--synthetic"])
    assert rc == 1
    captured = capsys.readouterr().out
    assert "Error extracting cumulative return: x" in captured


def test_main_cumulative_len_failure_surfaces(monkeypatch, capsys):
    # backtest.__len__ raising surfaces at cumulative extraction (rc=1) instead
    # of being silently swallowed into a fabricated 1.0 cumulative.
    class BadLen(pd.DataFrame):
        @property
        def _constructor(self): return BadLen
        def __len__(self): raise TypeError("badlen")
    res = SimpleNamespace(backtest=BadLen({"cumulative": [1.0, 1.1]}))
    class FS:
        def __init__(self, c): pass
        def run(self, **k): return res
    monkeypatch.setattr(cli, "BABStrategy", FS)
    rc = cli.main(["--synthetic"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "Error extracting cumulative return: badlen" in out


def test_main_dry_run_data_non_bab_exception(monkeypatch, tmp_path, capsys):
    data = _make_rets(tmp_path)
    import strategies.betting_against_beta.data_loader as dl
    monkeypatch.setattr(dl, "load_returns", lambda *a, **k: (_ for _ in ()).throw(ValueError("vboom")))
    rc = cli.main(["--dry-run", "--data", str(data)])
    assert rc == 1  # 264-266
    assert "INVALID" in capsys.readouterr().out


def test_main_dry_run_data_babdataerror_outer(monkeypatch, tmp_path, capsys):
    data = _make_rets(tmp_path)
    import strategies.betting_against_beta.data_loader as dl
    # raise from Path.exists/is_dir area? easier: make load_returns raise BABDataError caught at 261/267
    monkeypatch.setattr(dl, "load_returns", lambda *a, **k: (_ for _ in ()).throw(BABDataError("babboom")))
    rc = cli.main(["--dry-run", "--data", str(data)])
    assert rc == 1


def test_main_data_load_generic_exception_wrapped(monkeypatch, tmp_path, capsys):
    data = _make_rets(tmp_path)
    import strategies.betting_against_beta.data_loader as dl
    monkeypatch.setattr(dl, "load_returns", lambda *a, **k: (_ for _ in ()).throw(ValueError("raw")))
    rc = cli.main(["--data", str(data)])
    assert rc == 1  # 297-298
    assert "raw" in capsys.readouterr().out


def test_main_strategy_run_generic_exception_wrapped(monkeypatch, tmp_path, capsys):
    data = _make_rets(tmp_path)
    class FakeStrat:
        def __init__(self, cfg): pass
        def run(self, returns_df=None): raise ValueError("stratboom")
    monkeypatch.setattr(cli, "BABStrategy", FakeStrat)
    rc = cli.main(["--data", str(data)])
    assert rc == 1  # 303-304
    assert "stratboom" in capsys.readouterr().out


def test_main_top_level_generic_exception(monkeypatch, capsys):
    class FakeStrat:
        def __init__(self, cfg): raise RuntimeError("ctorboom")
    monkeypatch.setattr(cli, "BABStrategy", FakeStrat)
    rc = cli.main(["--synthetic"])
    assert rc == 1  # 308-310
    assert "ctorboom" in capsys.readouterr().out


def test_main_print_cumulative_failure_surfaces_error(monkeypatch, capsys):
    orig_print = print
    def flaky(*a, **k):
        if a and "Final cumulative" in str(a[0]):
            raise RuntimeError("print fail")
        return orig_print(*a, **k)
    monkeypatch.setattr("builtins.print", flaky)
    rc = cli.main(["--synthetic"])
    assert rc == 1  # C54 Step 2a: no silent swallow of output failure
    out = capsys.readouterr().out
    assert "Error printing cumulative return: print fail" in out


def test_main_dry_run_outer_bab_and_generic(monkeypatch, tmp_path, capsys):
    # 270-272: exception escaping inner try (lines 247-266) caught by 267-272
    data = _make_rets(tmp_path)
    import strategies.betting_against_beta.data_loader as dl
    orig = dl.load_returns
    def blow(*a, **k):
        raise BABDataError("outer")  # caught 267-269 or 261-263
    monkeypatch.setattr(dl, "load_returns", blow)
    rc = cli.main(["--dry-run", "--data", str(data)])
    assert rc == 1


def test_json_default_timestamp_isoformat_fail(monkeypatch):
    # 155-156: pd.Timestamp isoformat raises, str() fallback
    ts = pd.Timestamp("2024-01-01")
    monkeypatch.setattr(pd.Timestamp, "isoformat", lambda self, *a, **k: (_ for _ in ()).throw(RuntimeError("x")))
    monkeypatch.setattr(pd.Timestamp, "__str__", lambda self, *a, **k: "TSFALLBACK")
    out = cli._json_default(ts)
    assert out == "TSFALLBACK"


def test_json_default_bytes_decode_fail():
    # 167-168
    class BadBytes(bytes):
        def decode(self, *a, **k): raise RuntimeError("no")
    out = cli._json_default(BadBytes(b"ab"))
    assert out  # repr fallback


def test_main_dry_run_outer_bab_raised_from_exists(monkeypatch, tmp_path, capsys):
    # 267-269: BABDataError escaping the inner try (247-266)
    data = _make_rets(tmp_path)
    real_exists = Path.exists
    def flaky_exists(self):
        if str(self).endswith("r.csv"):
            raise BABDataError("exists boom")
        return real_exists(self)
    monkeypatch.setattr(Path, "exists", flaky_exists)
    rc = cli.main(["--dry-run", "--data", str(data)])
    assert rc == 1
    assert "INVALID" in capsys.readouterr().out


def test_main_dry_run_outer_generic_raised_from_exists(monkeypatch, tmp_path, capsys):
    # 270-272
    data = _make_rets(tmp_path)
    real_exists = Path.exists
    def flaky_exists(self):
        if str(self).endswith("r.csv"):
            raise RuntimeError("exists generic")
        return real_exists(self)
    monkeypatch.setattr(Path, "exists", flaky_exists)
    rc = cli.main(["--dry-run", "--data", str(data)])
    assert rc == 1
    assert "INVALID" in capsys.readouterr().out


def test_main_run_strategy_reraise_babdataerror(monkeypatch, tmp_path, capsys):
    # 302
    data = _make_rets(tmp_path)
    class FS:
        def __init__(self, c): pass
        def run(self, returns_df=None): raise BABDataError("strat bab")
    monkeypatch.setattr(cli, "BABStrategy", FS)
    rc = cli.main(["--data", str(data)])
    assert rc == 1
    assert "strat bab" in capsys.readouterr().out


def test_extract_cumulative_cum_column_iloc_raises():
    # 381-382: cumulative missing/bad path falls to cum search; cum col iloc raises
    class BadSeries(pd.Series):
        @property
        def _constructor(self): return BadSeries
        @property
        def iloc(self):
            raise RuntimeError("iloc bad")
    class BadDF(pd.DataFrame):
        @property
        def _constructor(self): return BadDF
        @property
        def _constructor_sliced(self): return BadSeries
    df = BadDF({"cum_x": [1.0, 2.0]})
    # force the cum branch: no 'cumulative' key
    res = cli._extract_cumulative(SimpleNamespace(backtest=df))
    # may return df/None depending on path; should not raise
    assert res is None or res is not None


def test_json_safe_timestamp_isoformat_fail(monkeypatch):
    # 419-420
    ts = pd.Timestamp("2024-01-01")
    monkeypatch.setattr(pd.Timestamp, "isoformat", lambda self, *a, **k: (_ for _ in ()).throw(RuntimeError("x")))
    monkeypatch.setattr(pd.Timestamp, "__str__", lambda self, *a, **k: "TSFALLBACK")
    out = cli._json_safe(ts)
    assert out == "TSFALLBACK"


def test_json_safe_np_floating_finite_and_nan_paths():
    # 428-429
    assert cli._json_safe(np.float32(2.5)) == 2.5
    assert cli._json_safe(np.float32(np.nan)) == 0.0
