"""Campaign 9 — BAB script/tooling hardening tests.

Covers CLI/script contracts, deterministic outputs/fixtures, and error paths for:
- scripts/bab_backtest_report.py
- scripts/load_real_bab_example.py
- scripts/generate_real_market_fixture.py
- scripts/perf_bench.py

Bug fixes require evidence + regression; .github/workflows untouched.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
FIXTURES = REPO_ROOT / "tests" / "fixtures"


def _run(
    script: Path, args: list[str], *, cwd: Path | None = None, timeout: int = 180
) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        p for p in (str(REPO_ROOT), os.environ.get("PYTHONPATH", "")) if p
    )
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd or REPO_ROOT),
        timeout=timeout,
    )


def _make_returns(rows: int = 300) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    idx = pd.date_range("2022-01-01", periods=rows, freq="D")
    bench = rng.normal(0.0005, 0.02, rows)
    data = {"BTC": bench}
    for i, a in enumerate(["ETH", "SOL", "BNB", "XRP", "ADA"]):
        data[a] = (0.5 + 0.4 * i) * bench + rng.normal(0, 0.01, rows)
    return pd.DataFrame(data, index=idx)


# ---------------------------------------------------------------------------
# scripts/bab_backtest_report.py
# ---------------------------------------------------------------------------


class TestBabBacktestReportCampaign9:
    SCRIPT = SCRIPTS / "bab_backtest_report.py"

    def test_relative_data_source_resolves_from_repo_root_regression(self):
        """Regression: script used undefined REPO_ROOT (not _REPO_ROOT) for relative paths.
        Evidence: NameError when relative --data-source hit line using REPO_ROOT.
        Fix: use _REPO_ROOT. Run from /tmp with relative fixture path resolved via repo root."""
        result = _run(
            self.SCRIPT,
            [
                "--data-source",
                "tests/fixtures/real_data_defects.csv",
                "--beta-window",
                "3",
                "--min-observations",
                "2",
                "--json",
            ],
            cwd=Path("/tmp"),
        )
        assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
        payload = json.loads(result.stdout)
        assert "metrics" in payload

    def test_returns_alias_flag(self, tmp_path: Path):
        csv = tmp_path / "r.csv"
        _make_returns().to_csv(csv)
        result = _run(self.SCRIPT, ["--returns", str(csv), "--json"])
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["config"]["data_source"] == str(csv)

    def test_data_source_directory_rejected_json(self, tmp_path: Path):
        result = _run(self.SCRIPT, ["--data-source", str(tmp_path), "--json"])
        assert result.returncode != 0
        payload = json.loads(result.stdout)
        assert "error" in payload
        assert "metrics" in payload

    def test_data_source_directory_rejected_human(self, tmp_path: Path):
        result = _run(self.SCRIPT, ["--data-source", str(tmp_path)])
        assert result.returncode != 0
        assert "Error" in result.stderr or "directory" in (result.stdout + result.stderr).lower()

    def test_json_output_has_no_nan_inf_tokens(self):
        result = _run(self.SCRIPT, ["--json"])
        assert result.returncode == 0, result.stderr
        assert "NaN" not in result.stdout
        assert "Infinity" not in result.stdout
        json.loads(result.stdout)  # strict parse

    def test_synthetic_data_source_string_treated_as_none(self):
        result = _run(self.SCRIPT, ["--data-source", "synthetic", "--json"])
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["config"]["data_source"] is None

    def test_empty_data_source_string_treated_as_none(self):
        result = _run(self.SCRIPT, ["--data-source", "", "--json"])
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["config"]["data_source"] is None

    def test_importable_main_returns_int(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO_ROOT)
        # Run in-process via -c to test module contract
        code = ("import sys; sys.path.insert(0,'.'); "
                "from scripts.bab_backtest_report import main; "
                "rc=main(['--json']); print('RC',rc)")
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=env,
            timeout=120,
        )
        assert r.returncode == 0, r.stderr
        assert "RC 0" in r.stdout

    def test_sanitize_metrics_helper(self):
        code = (
            "import sys, math; sys.path.insert(0,'.'); "
            "from scripts.bab_backtest_report import _sanitize_metrics; "
            "m=_sanitize_metrics({'a': float('nan'), 'b': float('inf'), "
            "'c': -float('inf'), 'd': 1.5, 'e': 'x', 'f': True}); "
            "print(m['a'], m['b'], m['c'], m['d'], m['e'], m['f'])"
        )
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )
        assert r.returncode == 0, r.stderr
        parts = r.stdout.strip().split()
        assert parts[0] == "0.0" and parts[1] == "0.0" and parts[2] == "0.0" and parts[3] == "1.5"

    def test_dumps_json_rejects_nan_tokens(self):
        code = (
            "import sys, json; sys.path.insert(0,'.'); "
            "from scripts.bab_backtest_report import _dumps_json; "
            "s=_dumps_json({'x': float('nan'), 'y': [float('inf')]}); "
            "print('NaN' in s, 'Infinity' in s); json.loads(s)"
        )
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )
        assert r.returncode == 0, r.stderr
        assert "False False" in r.stdout

    def test_missing_file_human_error_path(self, tmp_path: Path):
        result = _run(self.SCRIPT, ["--data-source", str(tmp_path / "nope.csv")])
        assert result.returncode != 0
        assert result.stderr.strip() or result.stdout.strip()


# ---------------------------------------------------------------------------
# scripts/load_real_bab_example.py
# ---------------------------------------------------------------------------


class TestLoadRealBabExampleCampaign9:
    SCRIPT = SCRIPTS / "load_real_bab_example.py"

    def test_runs_on_returns_fixture(self, tmp_path: Path):
        csv = tmp_path / "r.csv"
        _make_returns(300).to_csv(csv)
        result = _run(
            self.SCRIPT,
            [
                str(csv),
                "--benchmark",
                "BTC",
                "--min-rows",
                "30",
                "--lookback",
                "60",
                "--quantile",
                "0.3",
            ],
        )
        assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
        assert "cumulative_return=" in result.stdout
        assert "periods=" in result.stdout
        # parse cumulative
        for line in result.stdout.splitlines():
            if line.startswith("cumulative_return="):
                val = float(line.split("=", 1)[1])
                assert math.isfinite(val)

    def test_runs_from_prices_flag(self):
        result = _run(
            self.SCRIPT,
            [
                str(FIXTURES / "real_market_prices.csv"),
                "--from-prices",
                "--benchmark",
                "BTC",
                "--min-rows",
                "30",
                "--lookback",
                "60",
            ],
        )
        assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
        assert "cumulative_return=" in result.stdout

    def test_missing_file_exits_cleanly(self, tmp_path: Path):
        result = _run(self.SCRIPT, [str(tmp_path / "missing.csv")])
        assert result.returncode != 0
        assert "not found" in (result.stdout + result.stderr).lower()

    def test_directory_path_exits_cleanly(self, tmp_path: Path):
        result = _run(self.SCRIPT, [str(tmp_path)])
        assert result.returncode != 0
        assert "directory" in (result.stdout + result.stderr).lower()

    def test_data_validation_failure_surfaces_babdataerror(self, tmp_path: Path):
        bad = tmp_path / "bad.csv"
        bad.write_text("x,y\n1,2\n")
        result = _run(self.SCRIPT, [str(bad), "--benchmark", "BTC"])
        assert result.returncode != 0
        assert "failed" in (result.stdout + result.stderr).lower() or "Error" in (
            result.stdout + result.stderr
        )

    def test_deterministic_output_on_same_input(self):
        args = [
            str(FIXTURES / "real_market_prices.csv"),
            "--from-prices",
            "--benchmark",
            "BTC",
            "--min-rows",
            "30",
            "--lookback",
            "60",
        ]
        r1 = _run(self.SCRIPT, args)
        r2 = _run(self.SCRIPT, args)
        assert r1.returncode == 0 and r2.returncode == 0, r1.stderr
        assert r1.stdout == r2.stdout

    def test_universe_override(self):
        result = _run(
            self.SCRIPT,
            [
                str(FIXTURES / "real_market_prices.csv"),
                "--from-prices",
                "--benchmark",
                "BTC",
                "--min-rows",
                "30",
                "--lookback",
                "60",
                "--universe",
                "ETH",
                "SOL",
                "BNB",
            ],
        )
        assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"


# ---------------------------------------------------------------------------
# scripts/generate_real_market_fixture.py
# ---------------------------------------------------------------------------


class TestGenerateRealMarketFixtureCampaign9:
    SCRIPT = SCRIPTS / "generate_real_market_fixture.py"

    def test_importable_main_and_constants(self):
        code = (
            "import sys; sys.path.insert(0,'.'); "
            "from scripts import generate_real_market_fixture as g; "
            "print(g.ASSETS[0], g.DELISTED, g.SEED, g.GAP_DATE, g.N_DAYS)"
        )
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )
        assert r.returncode == 0, r.stderr
        assert "BTC DEL 20261028 2021-09-17 400" in r.stdout

    def test_deterministic_generation_to_custom_out(self, tmp_path: Path, monkeypatch):
        # Run generation logic in-process by monkeypatching OUT
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO_ROOT)
        out = tmp_path / "fixture.csv"
        code = f"""
import sys; sys.path.insert(0,'.')
import scripts.generate_real_market_fixture as g
g.OUT = r'{out}'
g.main()
"""
        r1 = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=env,
            timeout=60,
        )
        assert r1.returncode == 0, r1.stderr
        b1 = out.read_bytes()
        r2 = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=env,
            timeout=60,
        )
        assert r2.returncode == 0, r2.stderr
        assert out.read_bytes() == b1
        df = pd.read_csv(out)
        assert "date" in df.columns
        assert "BTC" in df.columns and "DEL" in df.columns
        assert df["DEL"].isna().all()
        assert "2021-09-17" not in df["date"].astype(str).values
        assert len(df) == 399  # 400 bdays minus gap

    def test_committed_fixture_matches_generator_contract(self):
        """The committed fixture should satisfy the generator's invariants
    (shape/columns/gap/delisted)."""
        df = pd.read_csv(FIXTURES / "real_market_prices.csv")
        assert df.columns[0] == "date"
        for a in ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT", "LINK", "DEL"]:
            assert a in df.columns
        assert df["DEL"].isna().all()
        assert "2021-09-17" not in df["date"].astype(str).values


# ---------------------------------------------------------------------------
# scripts/perf_bench.py
# ---------------------------------------------------------------------------


class TestPerfBenchCampaign9:
    SCRIPT = SCRIPTS / "perf_bench.py"

    def test_make_returns_shape_and_columns(self):
        code = (
            "import sys; sys.path.insert(0,'.'); "
            "from scripts.perf_bench import _make_returns; "
            "df=_make_returns(10, 5); print(df.shape, list(df.columns)[0])"
        )
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=60,
        )
        assert r.returncode == 0, r.stderr
        assert "(10, 5)" in r.stdout and "BTC" in r.stdout

    def test_time_helper_returns_positive_float(self):
        code = (
            "import sys; sys.path.insert(0,'.'); "
            "from scripts.perf_bench import _time; "
            "t=_time(lambda: sum(range(100)), repeats=3); print(t >= 0)"
        )
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )
        assert r.returncode == 0, r.stderr
        assert "True" in r.stdout

    def test_main_runs_end_to_end_small_scope(self):
    """Run main() in-process with small synthetic inputs by invoking script;
    allow generous timeout.
    The script uses fixed sizes (720x12) which should complete quickly in this env."""
        result = _run(self.SCRIPT, [], timeout=300)
        assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
        out = result.stdout
        assert "shape=" in out
        assert "calculate_rolling_beta" in out
        assert "full BABStrategy.run" in out
        assert "tracemalloc peak" in out
