import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from strategies.betting_against_beta.config import BABConfig, BABConfigError
from strategies.betting_against_beta.data_loader import load_prices
from strategies.betting_against_beta.strategy import BABStrategy

REAL = "tests/fixtures/real_market_prices.csv"


def _run_cli(args, cwd=None):
    cmd = [sys.executable, "-m", "strategies.betting_against_beta.cli"] + list(args)
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return cmd, p


@pytest.fixture(scope="module")
def real_returns():
    return load_prices(REAL, benchmark="BTC")


# 1-5: config validation edges must raise clean BABConfigError
def test_c19_config_beta_window_zero_clean():
    with pytest.raises(BABConfigError, match="beta_window"):
        BABConfig(beta_window=0)


@pytest.mark.parametrize("q", [0.0, 1.0])
def test_c19_config_long_quantile_bounds_clean(q):
    with pytest.raises(BABConfigError, match="long_quantile"):
        BABConfig(long_quantile=q)


def test_c19_config_short_quantile_zero_clean():
    with pytest.raises(BABConfigError, match="short_quantile"):
        BABConfig(short_quantile=0.0)


def test_c19_config_negative_transaction_costs_clean():
    with pytest.raises(BABConfigError, match="transaction_costs"):
        BABConfig(transaction_costs=-0.001)


def test_c19_config_vol_thresholds_and_percentiles_both_set_clean():
    with pytest.raises(BABConfigError, match="set only one"):
        BABConfig(vol_thresholds=[0.1], vol_percentiles=[50])


# 6: transaction-cost monotonic drag and finite metrics/backtest
def test_c19_cost_monotonic_drag_finite(real_returns):
    finals = []
    for c in [0.0, 0.0005, 0.001, 0.005]:
        res = BABStrategy(benchmark="BTC", transaction_costs=c).run(returns_df=real_returns.copy())
        bt = res.backtest
        assert len(bt) == 398
        for col in bt.columns:
            assert np.all(np.isfinite(bt[col].to_numpy(dtype=float)))
        finals.append(float(bt["cumulative"].iloc[-1]))
    assert all(finals[i] >= finals[i + 1] - 1e-12 for i in range(len(finals) - 1))


# 7: slippage drag positive and finite
def test_c19_slippage_drag_positive_finite(real_returns):
    res0 = BABStrategy(benchmark="BTC", slippage=0.0, transaction_costs=0.0).run(returns_df=real_returns.copy())
    res1 = BABStrategy(benchmark="BTC", slippage=0.001, transaction_costs=0.0).run(returns_df=real_returns.copy())
    for res in (res0, res1):
        bt = res.backtest
        for col in bt.columns:
            assert np.all(np.isfinite(bt[col].to_numpy(dtype=float)))
    assert float(res0.backtest["slippage_drag"].sum()) == 0.0
    assert float(res1.backtest["slippage_drag"].sum()) > 0.0
    # net cumulative under slippage should not exceed gross/no-slippage path
    assert float(res1.backtest["cumulative"].iloc[-1]) <= float(res0.backtest["cumulative"].iloc[-1]) + 1e-12


# 8: explicit universe with no data overlap -> clean BABConfigError
def test_c19_universe_no_overlap_clean_error(real_returns):
    with pytest.raises(BABConfigError, match="no overlap"):
        BABStrategy(benchmark="BTC", universe=["ZZZ", "YYY"]).run(returns_df=real_returns.copy())


# 9: rebalance freq behavior, neutrality, finite, deterministic
@pytest.mark.parametrize("freq", ["daily", "weekly", "monthly"])
def test_c19_rebalance_freq_finite_neutral_deterministic(real_returns, freq):
    outs = []
    for _ in range(2):
        res = BABStrategy(benchmark="BTC", rebalance_freq=freq).run(returns_df=real_returns.copy())
        bt, w = res.backtest, res.weights
        assert len(bt) == 398
        for col in bt.columns:
            assert np.all(np.isfinite(bt[col].to_numpy(dtype=float)))
        assert np.all(np.isfinite(w.to_numpy(dtype=float)))
        rsmax = float(np.max(np.abs(w.sum(axis=1).to_numpy(dtype=float))))
        assert rsmax < 1e-9
        outs.append((bt["cumulative"].to_numpy(dtype=float).copy(), w.to_numpy(dtype=float).copy()))
    assert np.allclose(outs[0][0], outs[1][0], equal_nan=False)
    assert np.allclose(outs[0][1], outs[1][1], equal_nan=False)


# 10: valid shorting constraints run cleanly, finite, neutral, shorts present
def test_c19_shorting_constraints_valid_finite_neutral(real_returns):
    res = BABStrategy(
        benchmark="BTC",
        shorting_constraints={"max_short_weight": 0.5, "max_short_notional_per_asset": 1.0},
    ).run(returns_df=real_returns.copy())
    bt, w = res.backtest, res.weights
    for col in bt.columns:
        assert np.all(np.isfinite(bt[col].to_numpy(dtype=float)))
    assert np.all(np.isfinite(w.to_numpy(dtype=float)))
    assert float(np.max(np.abs(w.sum(axis=1).to_numpy(dtype=float)))) < 1e-9
    assert bool((w.to_numpy(dtype=float) < -1e-12).any())


# 11: feasible max_position_size bounded and finite
def test_c19_max_position_size_feasible_bounded_finite(real_returns):
    res = BABStrategy(benchmark="BTC", max_position_size=0.5).run(returns_df=real_returns.copy())
    bt, w = res.backtest, res.weights
    for col in bt.columns:
        assert np.all(np.isfinite(bt[col].to_numpy(dtype=float)))
    assert np.all(np.isfinite(w.to_numpy(dtype=float)))
    assert float(np.max(np.abs(w.to_numpy(dtype=float)))) <= 0.5 + 1e-9


# 12-15: CLI output, nested dir creation, dry-run dir error, determinism
def test_c19_cli_output_strict_json_and_keys(tmp_path):
    outp = tmp_path / "out.json"
    cmd, p = _run_cli(["--data", REAL, "--from-prices", "--benchmark", "BTC", "--output", str(outp)])
    assert p.returncode == 0, (cmd, p.stdout, p.stderr)
    assert p.stderr == ""
    assert "Traceback" not in p.stdout and "Traceback" not in p.stderr
    obj = json.loads(outp.read_text())
    json.dumps(obj, allow_nan=False)
    assert set(obj.keys()) == {"final_cumulative", "periods", "benchmark", "universe"}
    assert obj["periods"] == 398
    assert obj["benchmark"] == "BTC"
    assert isinstance(obj["universe"], list) and len(obj["universe"]) > 0
    assert math.isfinite(float(obj["final_cumulative"]))


def test_c19_cli_output_nested_dir_created(tmp_path):
    outp = tmp_path / "nested" / "deep" / "out.json"
    cmd, p = _run_cli(["--data", REAL, "--from-prices", "--benchmark", "BTC", "--output", str(outp)])
    assert p.returncode == 0, (cmd, p.stdout, p.stderr)
    assert outp.exists()
    obj = json.loads(outp.read_text())
    json.dumps(obj, allow_nan=False)
    assert obj["periods"] == 398


def test_c19_cli_dry_run_output_dir_clean_error(tmp_path):
    cmd, p = _run_cli(["--dry-run", "--data", REAL, "--from-prices", "--benchmark", "BTC", "--output", str(tmp_path)])
    assert p.returncode == 1, (cmd, p.stdout, p.stderr)
    assert "Traceback" not in p.stdout and "Traceback" not in p.stderr
    assert "is a directory" in (p.stdout + p.stderr)


def test_c19_cli_determinism_stdout_and_json(tmp_path):
    outs = []
    files = []
    for i in range(2):
        outp = tmp_path / f"out{i}.json"
        cmd, p = _run_cli(["--data", REAL, "--from-prices", "--benchmark", "BTC", "--output", str(outp)])
        assert p.returncode == 0, (cmd, p.stdout, p.stderr)
        outs.append(p.stdout)
        files.append(outp.read_bytes())
    assert outs[0] == outs[1]
    assert files[0] == files[1]
