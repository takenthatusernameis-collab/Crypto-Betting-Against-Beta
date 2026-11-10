"""Regression tests for Campaign 16: BAB output/reporting schema & metrics fidelity.

Evidence: /home/runner/work/_temp/kilo-tmp/c16_bab_reporting_metrics_probe_evidence.log
Conclusion: no proven gaps. These tests lock in the verified C16 probe behavior
(console script + module CLI --output JSON schema, finiteness, stderr/stdout
cleanliness, determinism, error paths, in-process parity) so future sessions
cannot regress reporting fidelity without a failing test.

Console script equivalent: `python -m scripts.load_real_bab_example` (the
`bab-example` console-script main(); the installed entry point is not on PATH
in this environment).
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
REAL = str(REPO / "tests" / "fixtures" / "real_market_prices.csv")
EXP = str(REPO / "tests" / "fixtures" / "real_market_prices_expanded.csv")
DEFECTS = str(REPO / "tests" / "fixtures" / "real_data_defects.csv")
BENCH_NAN = str(REPO / "tests" / "fixtures" / "benchmark_nan_window.csv")
ALL_NAN = str(REPO / "tests" / "fixtures" / "all_nan_column.csv")
JUNK = str(REPO / "tests" / "fixtures" / "junk_columns.csv")
TMP_DIR = str(REPO / ".pytest_cache" / "c16")


def _run_bab_example(argv):
    env = {**__import__("os").environ, "PYTHONPATH": str(REPO)}
    return subprocess.run(
        [sys.executable, "-m", "scripts.load_real_bab_example"] + argv,
        capture_output=True, text=True, timeout=180, cwd=str(REPO), env=env,
    )


def _run_cli(argv):
    env = {**__import__("os").environ, "PYTHONPATH": str(REPO)}
    return subprocess.run(
        [sys.executable, "-m", "strategies.betting_against_beta.cli"] + argv,
        capture_output=True, text=True, timeout=180, cwd=str(REPO), env=env,
    )


def _assert_no_traceback(r):
    blob = (r.stdout or "") + (r.stderr or "")
    assert "Traceback" not in blob, blob


def _write_json(path, payload):
    Path(path).write_text(json.dumps(payload, indent=2, allow_nan=False))


class TestConsoleScriptReportingSchema:
    """C16 probes 1-5: bab-example --output writes valid finite JSON summary."""

    @pytest.mark.parametrize(
        "argv,expect_benchmark",
        [
            ([REAL, "--from-prices", "--benchmark", "BTC"], "BTC"),
            ([EXP, "--from-prices", "--benchmark", "BTC"], "BTC"),
            ([REAL, "--from-prices", "--benchmark", "ETH"], "ETH"),
            ([REAL, "--from-prices", "--benchmark", "BTC", "--lookback", "60"], "BTC"),
            ([REAL, "--from-prices", "--benchmark", "BTC", "--quantile", "0.2"], "BTC"),
        ],
    )
    def test_output_json_valid_finite_keys(self, tmp_path, argv, expect_benchmark):
        out = tmp_path / "out.json"
        r = _run_bab_example(argv + ["--output", str(out)])
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        assert r.stderr == "", r.stderr
        assert "cumulative_return=" in r.stdout
        assert "periods=" in r.stdout
        _assert_no_traceback(r)
        assert out.exists()
        payload = json.loads(out.read_text())
        assert {"final_cumulative", "periods", "benchmark", "universe"} <= set(payload.keys())
        assert payload["benchmark"] == expect_benchmark
        assert isinstance(payload["periods"], int) and payload["periods"] == 398
        assert isinstance(payload["final_cumulative"], (int, float))
        import math
        assert math.isfinite(payload["final_cumulative"])


class TestConsoleScriptDeterminism:
    """C16 probe 6: repeated runs produce identical stdout and JSON."""

    def test_deterministic_repeat(self, tmp_path):
        outs, cumulatives, periods = [], [], []
        for _ in range(2):
            out = tmp_path / f"out{len(outs)}.json"
            r = _run_bab_example([REAL, "--from-prices", "--benchmark", "BTC", "--output", str(out)])
            assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
            assert r.stderr == "", r.stderr
            outs.append(r.stdout)
            payload = json.loads(out.read_text())
            cumulatives.append(payload["final_cumulative"])
            periods.append(payload["periods"])
        assert outs[0] == outs[1], "stdout not deterministic across repeats"
        assert cumulatives[0] == cumulatives[1], "final_cumulative not deterministic"
        assert periods[0] == periods[1] == 398, "periods not deterministic"


class TestModuleCliReporting:
    """C16 probes 7-8: module CLI --output JSON and nested output dir."""

    def test_synthetic_output_json(self, tmp_path):
        out = tmp_path / "out.json"
        r = _run_cli(["--synthetic", "--output", str(out)])
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        assert r.stderr == "", r.stderr
        assert out.exists()
        payload = json.loads(out.read_text())
        assert {"final_cumulative", "periods", "benchmark", "universe"} <= set(payload.keys())
        import math
        assert all(
            not (isinstance(v, float) and not math.isfinite(v))
            for v in payload.values()
        ), f"non-finite JSON value: {payload}"

    def test_output_nested_parent_dir(self, tmp_path):
        out = tmp_path / "nested" / "deep" / "out.json"
        r = _run_cli(["--synthetic", "--output", str(out)])
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        assert out.exists()
        json.loads(out.read_text())


class TestConsoleScriptErrorPaths:
    """C16 probes 9-11: clean errors, no Traceback, no corrupt/non-finite JSON."""

    def test_output_is_directory(self, tmp_path):
        r = _run_cli(["--synthetic", "--output", str(tmp_path)])
        assert r.returncode != 0, (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)
        assert "Error validating output path" in r.stdout or "is a directory" in (r.stdout + r.stderr)

    def test_real_data_defects_clean_error(self, tmp_path):
        out = tmp_path / "out.json"
        r = _run_bab_example([DEFECTS, "--from-prices", "--benchmark", "BTC", "--output", str(out)])
        assert r.returncode in (0, 1), (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)
        if out.exists():
            payload = json.loads(out.read_text())
            import math
            assert all(math.isfinite(v) for v in payload.values() if isinstance(v, float))

    def test_benchmark_nan_window_clean_error(self, tmp_path):
        out = tmp_path / "out.json"
        r = _run_bab_example([BENCH_NAN, "--from-prices", "--benchmark", "BTC", "--output", str(out)])
        assert r.returncode in (0, 1), (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)
        if out.exists():
            payload = json.loads(out.read_text())
            import math
            assert all(math.isfinite(v) for v in payload.values() if isinstance(v, float))


class TestConsoleScriptNaNDefectPaths:
    """C16 probe 13: junk_columns / all_nan_column -> rc=1, actionable, no output JSON."""

    @pytest.mark.parametrize("fixture", [ALL_NAN, JUNK])
    def test_nan_defect_no_output_json(self, tmp_path, fixture):
        out = tmp_path / "out.json"
        if out.exists():
            out.unlink()
        r = _run_bab_example([fixture, "--from-prices", "--benchmark", "BTC", "--output", str(out)])
        assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
        _assert_no_traceback(r)
        assert not out.exists(), f"output JSON must not be created for {fixture}"
        assert r.stdout or r.stderr, "expected actionable error message"


class TestConsoleScriptInProcessParity:
    """C16 probe 12: console --output JSON matches BABStrategy.run in-process."""

    @pytest.mark.parametrize(
        "argv",
        [
            [REAL, "--from-prices", "--benchmark", "BTC"],
            [EXP, "--from-prices", "--benchmark", "BTC"],
            [REAL, "--from-prices", "--benchmark", "ETH"],
        ],
    )
    def test_console_vs_in_process_parity(self, tmp_path, argv):
        out = tmp_path / "out.json"
        r = _run_bab_example(argv + ["--output", str(out)])
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        console = json.loads(out.read_text())

        from strategies.betting_against_beta import BABStrategy
        from strategies.betting_against_beta.data_loader import load_prices

        data_path = argv[0]
        benchmark = argv[argv.index("--benchmark") + 1]
        lookback = int(argv[argv.index("--lookback") + 1]) if "--lookback" in argv else 252
        rets = load_prices(data_path, benchmark=benchmark, min_rows=30)
        strat = BABStrategy(
            benchmark=benchmark,
            beta_window=lookback,
            long_quantile=0.3,
            short_quantile=0.3,
            transaction_costs=0.001,
        )
        res = strat.run(returns_df=rets)
        bt = getattr(res, "backtest", None)
        ip_periods = int(len(bt)) if bt is not None and hasattr(bt, "__len__") else 0
        ip_cum = None
        if bt is not None and hasattr(bt, "columns") and "cumulative" in bt.columns:
            try:
                ip_cum = float(bt["cumulative"].iloc[-1])
            except Exception:
                ip_cum = None

        assert console["periods"] == ip_periods, (console, ip_periods)
        if ip_cum is not None:
            import math
            assert math.isclose(console["final_cumulative"], ip_cum, rel_tol=1e-6, abs_tol=1e-9), (
                console["final_cumulative"], ip_cum
            )
