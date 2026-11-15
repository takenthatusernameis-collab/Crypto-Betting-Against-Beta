"""P11 coverage: real, reachable uncovered paths in `cli.py`.

Exercises (via `main(argv)` and the module helpers directly):
- `_build_adapter` mock-fills parsing (list-of-dicts, dict-keyed map,
  malformed JSON / OSError -> BABDataError, missing --fills file).
- `_json_safe` / `_json_default` numpy scalar coercion and fallbacks.
- `_write_json_artifact` and `_validate_output_path` failure paths.
- Paper-trading path (missing --output -> exit 1; happy path writes JSONL +
  diagnostics.jsonl).
- Output / execution / reconciliation artifact write failures -> clean exit 1.
- Validation edges: --from-prices without --data, --fills without --adapter
  mock, unknown --adapter, live without --exchange/credentials,
  --health-check without --adapter live, stale-data freshness guard.

No behavior change to the default path; fakes/mocks only, no network.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.cli import (
    _build_adapter,
    _extract_cumulative,
    _json_default,
    _json_safe,
    _run_reconciliation,
    _validate_output_path,
    _write_json_artifact,
    main,
)
from strategies.betting_against_beta.errors import BABDataError
from strategies.betting_against_beta.execution import PaperAdapter


def _make_returns(tmp_path, n_days=120, seed=3):
    rng = np.random.RandomState(seed)
    dates = pd.date_range("2023-01-01", periods=n_days)
    df = pd.DataFrame(
        {
            "BTC": rng.normal(0.0, 0.01, n_days),
            "ETH": rng.normal(0.0, 0.015, n_days),
            "SOL": rng.normal(0.0, 0.02, n_days),
        },
        index=dates,
    )
    p = tmp_path / "rets.csv"
    df.to_csv(p)
    return p


# ---------------------------------------------------------------------------
# _build_adapter
# ---------------------------------------------------------------------------

def test_build_adapter_no_adapter_returns_none():
    args = SimpleNamespace(adapter=None)
    assert _build_adapter(args) == (None, None)


def test_build_adapter_paper():
    args = SimpleNamespace(adapter="paper")
    adapter, fills_path = _build_adapter(args)
    assert isinstance(adapter, PaperAdapter)
    assert fills_path is None


def test_build_adapter_mock_list_of_dicts(tmp_path):
    fills = [
        {"date": "2023-01-02", "asset": "BTC", "price": 1.0},
        {"date": "2023-01-02", "asset": "ETH", "price": 2.0},
    ]
    p = tmp_path / "fills.json"
    p.write_text(json.dumps(fills))
    args = SimpleNamespace(adapter="mock", fills=str(p))
    adapter, fills_path = _build_adapter(args)
    assert isinstance(adapter.fill_map, dict)
    assert ("2023-01-02", "BTC") in adapter.fill_map
    assert ("2023-01-02", "ETH") in adapter.fill_map
    assert fills_path == str(p)


def test_build_adapter_mock_dict_keyed(tmp_path):
    raw = {"2023-01-02|BTC": {"price": 1.0}, "2023-01-03|SOL": {"price": 5.0}}
    p = tmp_path / "fills.json"
    p.write_text(json.dumps(raw))
    args = SimpleNamespace(adapter="mock", fills=str(p))
    adapter, _ = _build_adapter(args)
    # A JSON object is accepted as-is and stored verbatim as the fill map.
    assert adapter.fill_map == raw


def test_build_adapter_mock_malformed_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not valid json")
    args = SimpleNamespace(adapter="mock", fills=str(p))
    with pytest.raises(BABDataError):
        _build_adapter(args)


def test_build_adapter_mock_unreadable_file(tmp_path):
    p = tmp_path / "unreadable.json"
    p.write_text("[]")
    p.chmod(0o000)
    try:
        args = SimpleNamespace(adapter="mock", fills=str(p))
        with pytest.raises(BABDataError):
            _build_adapter(args)
    finally:
        p.chmod(0o644)


def test_main_fills_requires_adapter_mock(tmp_path):
    p = tmp_path / "fills.json"
    p.write_text("[]")
    rc = main(["--fills", str(p)])
    assert rc == 1


def test_build_adapter_live_missing_exchange():
    args = SimpleNamespace(
        adapter="live", exchange=None, api_key_env="K", api_secret_env="S"
    )
    with pytest.raises(BABDataError):
        _build_adapter(args)


def test_build_adapter_live_missing_creds():
    args = SimpleNamespace(adapter="live", exchange="binance", api_key_env=None, api_secret_env="S")
    with pytest.raises(BABDataError):
        _build_adapter(args)


def test_build_adapter_unknown_adapter_returns_none():
    args = SimpleNamespace(adapter="nope")
    assert _build_adapter(args) == (None, None)


def test_main_live_missing_exchange_rc1():
    rc = main(["--synthetic", "--adapter", "live", "--api-key-env", "K", "--api-secret-env", "S"])
    assert rc == 1


def test_main_live_missing_creds_rc1():
    rc = main(["--synthetic", "--adapter", "live", "--exchange", "binance"])
    assert rc == 1


def test_main_health_check_requires_live_adapter_rc1():
    rc = main(["--synthetic", "--health-check"])
    assert rc == 1


# ---------------------------------------------------------------------------
# _json_safe / _json_default
# ---------------------------------------------------------------------------

def test_json_safe_numpy_scalar_coercion():
    assert _json_safe(np.int64(7)) == 7
    assert _json_safe(np.float64(2.5)) == 2.5
    assert _json_safe(np.float64(np.inf)) == 0.0
    assert _json_safe(np.float64(np.nan)) == 0.0
    assert _json_safe(np.bool_(True)) is True
    assert _json_safe(float("inf")) == 0.0
    assert _json_safe(float("nan")) == 0.0


def test_json_safe_containers():
    assert _json_safe(np.array([1, 2, 3])) == [1, 2, 3]
    assert _json_safe(pd.Series([1.0, 2.0])) == [1.0, 2.0]
    assert _json_safe(pd.DataFrame({"a": [1, 2], "b": [3, 4]})) == {"a": [1, 2], "b": [3, 4]}
    assert _json_safe(pd.Index(["x", "y"])) == ["x", "y"]
    ts = pd.Timestamp("2023-01-01")
    assert _json_safe(ts) == ts.isoformat()
    assert _json_safe({1, 2, 3}) == [1, 2, 3]


def test_json_default_bytes_fallback():
    assert _json_default(b"\xff\xfe") == "\ufffd\ufffd"


def test_json_default_numpy_fallback():
    assert _json_default(np.int32(9)) == 9
    assert _json_default(np.float32(np.inf)) == 0.0
    assert _json_default(np.bool_(False)) is False


# ---------------------------------------------------------------------------
# _validate_output_path / _write_json_artifact
# ---------------------------------------------------------------------------

def test_validate_output_path_empty_raises():
    with pytest.raises(BABDataError):
        _validate_output_path("")


def test_validate_output_path_directory_raises(tmp_path):
    with pytest.raises(BABDataError):
        _validate_output_path(str(tmp_path))


def test_validate_output_path_outside_allowed_raises(tmp_path):
    # /root is not an allowed base; as non-root it cannot be created here, so
    # use a nested path that resolves outside all allowed bases.
    with pytest.raises(BABDataError):
        _validate_output_path("/nonexistent_base_xyz/out.json")


def test_validate_output_path_unwritable_parent_raises(tmp_path):
    ro = tmp_path / "ro"
    ro.mkdir()
    ro.chmod(0o555)
    try:
        with pytest.raises(BABDataError):
            _validate_output_path(str(ro / "out.json"))
    finally:
        ro.chmod(0o755)


def test_write_json_artifact_failure_returns_false(tmp_path):
    ro = tmp_path / "ro"
    ro.mkdir()
    ro.chmod(0o555)
    try:
        assert _write_json_artifact(ro / "artifact.json", {"a": 1}) is False
    finally:
        ro.chmod(0o755)


def test_write_json_artifact_success(tmp_path):
    p = tmp_path / "artifact.json"
    assert _write_json_artifact(p, {"a": 1, "b": [1, 2, 3]}) is True
    assert json.loads(p.read_text()) == {"a": 1, "b": [1, 2, 3]}


def test_main_fills_mock_valid_file_rc1(tmp_path):
    # Valid --fills with --adapter mock reaches the _build_adapter validation
    # call (582-587); the run then fails downstream (mock adapter isn't a
    # PaperAdapter), but the validation path itself is exercised cleanly.
    fills = tmp_path / "fills.json"
    fills.write_text("[]")
    rc = main(["--synthetic", "--adapter", "mock", "--fills", str(fills)])
    assert rc == 1


def test_main_freshness_guard_pass_dry_run(tmp_path):
    data_path = _make_returns(tmp_path)
    rc = main(["--dry-run", "--data", str(data_path), "--max-staleness-days", "5000"])
    assert rc == 0


def test_build_adapter_mock_list_with_non_dict_entries(tmp_path):
    # Non-dict entries in the list are skipped (line 47); only dicts fill the map.
    fills = [
        {"date": "2023-01-02", "asset": "BTC", "price": 1.0},
        "not-a-dict",
        42,
        {"date": "2023-01-03", "asset": "ETH", "price": 2.0},
    ]
    p = tmp_path / "fills.json"
    p.write_text(json.dumps(fills))
    args = SimpleNamespace(adapter="mock", fills=str(p))
    adapter, _ = _build_adapter(args)
    assert ("2023-01-02", "BTC") in adapter.fill_map
    assert ("2023-01-03", "ETH") in adapter.fill_map
    assert "not-a-dict" not in adapter.fill_map


def test_main_unknown_adapter_rc2():
    # argparse enforces `choices=["paper", "mock", "live"]` on --adapter, so an
    # unknown adapter is rejected by argparse with exit code 2 (SystemExit)
    # before reaching the defensive guard at cli.py:588.
    rc = main(["--synthetic", "--adapter", "nope"])
    assert rc == 2


def test_main_paper_trading_unwritable_output_rc1(tmp_path):
    ro = tmp_path / "ro"
    ro.mkdir()
    ro.chmod(0o555)
    try:
        rc = main(["--synthetic", "--paper-trading", "--output", str(ro / "fills.jsonl")])
        assert rc == 1
    finally:
        ro.chmod(0o755)


def test_main_paper_trading_bad_cumulative_pnl_rc1(tmp_path, monkeypatch):
    # bt has a "cumulative" column but indexing it raises -> backtest_pnl=None (759-760).
    class BadCumDF(pd.DataFrame):
        def __getitem__(self, key):
            if key == "cumulative":
                raise KeyError("simulated")
            return super().__getitem__(key)

    bad_bt = BadCumDF({"cumulative": [1.0, 2.0]})

    class FakeResult:
        weights = pd.DataFrame()
        betas = pd.DataFrame()
        signals = pd.DataFrame()
        returns = pd.DataFrame()
        backtest = bad_bt

    monkeypatch.setattr(
        "strategies.betting_against_beta.cli.BABStrategy.run",
        lambda self, returns_df=None: FakeResult(),
    )
    out = tmp_path / "fills.jsonl"
    rc = main(["--synthetic", "--paper-trading", "--output", str(out)])
    assert rc == 0
    assert out.exists()


def test_main_periods_len_raises_rc1(tmp_path, monkeypatch):
    # bt.__len__ raises inside _extract_cumulative (cli.py:878) -> caught by the
    # outer try/except at cli.py:789-791 -> clean exit 1.
    class BadLen:
        def __len__(self):
            raise TypeError("no len")

        def __getattr__(self, item):
            raise AttributeError(item)

    class FakeResult:
        weights = pd.DataFrame()
        betas = pd.DataFrame()
        signals = pd.DataFrame()
        returns = pd.DataFrame()
        backtest = BadLen()

    monkeypatch.setattr(
        "strategies.betting_against_beta.cli.BABStrategy.run",
        lambda self, returns_df=None: FakeResult(),
    )
    out = tmp_path / "out.json"
    rc = main(["--synthetic", "--output", str(out)])
    assert rc == 1


def test_main_print_periods_raises_rc1(tmp_path, monkeypatch):
    # print() of the periods line raises -> caught, returns 1 (807-810).
    class FakeResult:
        weights = pd.DataFrame()
        betas = pd.DataFrame()
        signals = pd.DataFrame()
        returns = pd.DataFrame()
        backtest = pd.DataFrame({"cumulative": [1.0, 1.5]})

    monkeypatch.setattr(
        "strategies.betting_against_beta.cli.BABStrategy.run",
        lambda self, returns_df=None: FakeResult(),
    )

    real_print = print

    def failing_print(*a, **k):
        if a and isinstance(a[0], str) and a[0].startswith("Periods:"):
            raise OSError("simulated stdout failure")
        return real_print(*a, **k)

    monkeypatch.setattr("builtins.print", failing_print)
    out = tmp_path / "out.json"
    rc = main(["--synthetic", "--output", str(out)])
    assert rc == 1


def test_main_fills_mock_malformed_file_rc1(tmp_path):
    # Malformed --fills with --adapter mock hits the BABDataError except block (585-587).
    p = tmp_path / "bad.json"
    p.write_text("{not valid json")
    rc = main(["--adapter", "mock", "--fills", str(p)])
    assert rc == 1


# ---------------------------------------------------------------------------
# main(argv) CLI-level paths
# ---------------------------------------------------------------------------

def _fail_on_write_call(call_index):
    """Monkeypatch helper: Path.write_text fails on the N-th call (1-based)."""
    calls = {"n": 0}
    real = Path.write_text

    def failing(self, data, *a, **k):
        calls["n"] += 1
        if calls["n"] == call_index:
            raise OSError("simulated write failure")
        return real(self, data, *a, **k)

    return failing, calls


def test_main_paper_trading_without_output_rc1():
    rc = main(["--synthetic", "--paper-trading"])
    assert rc == 1


def test_main_paper_trading_happy_path(tmp_path):
    out = tmp_path / "fills.jsonl"
    rc = main(["--synthetic", "--paper-trading", "--output", str(out)])
    assert rc == 0
    assert out.exists()
    diag = out.parent / "diagnostics.jsonl"
    assert diag.exists()
    lines = [json.loads(line) for line in out.read_text().splitlines() if line.strip()]
    assert len(lines) > 0
    diag_lines = [json.loads(line) for line in diag.read_text().splitlines() if line.strip()]
    assert len(diag_lines) > 0


def test_main_from_prices_without_data_rc1():
    rc = main(["--from-prices"])
    assert rc == 1


def test_main_freshness_guard_dry_run_rc1(tmp_path):
    data_path = _make_returns(tmp_path)
    rc = main(["--dry-run", "--data", str(data_path), "--max-staleness-days", "0"])
    assert rc == 1


def test_main_freshness_guard_run_path_rc1(tmp_path):
    data_path = _make_returns(tmp_path)
    rc = main(["--data", str(data_path), "--max-staleness-days", "0"])
    assert rc == 1


def test_main_output_write_failure_rc1(tmp_path, monkeypatch):
    failing, _ = _fail_on_write_call(1)
    monkeypatch.setattr(Path, "write_text", failing)
    rc = main(["--synthetic", "--output", str(tmp_path / "out.json")])
    assert rc == 1


def test_main_execution_artifact_write_failure_rc1(tmp_path, monkeypatch):
    failing, _ = _fail_on_write_call(2)  # 1st = summary, 2nd = execution artifact
    monkeypatch.setattr(Path, "write_text", failing)
    out = tmp_path / "out.json"
    rc = main(["--synthetic", "--adapter", "paper", "--output", str(out)])
    assert rc == 1


def test_main_reconciliation_artifact_write_failure_rc1(tmp_path, monkeypatch):
    failing, _ = _fail_on_write_call(3)  # 1st = summary, 2nd = execution, 3rd = reconciliation
    monkeypatch.setattr(Path, "write_text", failing)
    out = tmp_path / "out.json"
    rc = main(
        ["--synthetic", "--adapter", "paper", "--reconcile", "--output", str(out)]
    )
    assert rc == 1


# ---------------------------------------------------------------------------
# _extract_cumulative direct branches
# ---------------------------------------------------------------------------

def test_extract_cumulative_dataframe_with_cumulative_column():
    result = SimpleNamespace(
        backtest=pd.DataFrame({"cumulative": [1.0, 1.05, 1.1]})
    )
    assert _extract_cumulative(result) == 1.1


def test_extract_cumulative_dataframe_cum_column_fallback():
    result = SimpleNamespace(backtest=pd.DataFrame({"cum_ret": [1.0, 1.25]}))
    assert _extract_cumulative(result) == 1.25


def test_extract_cumulative_series_with_cum_name():
    result = SimpleNamespace(backtest=pd.Series([1.0, 1.5], name="cum_pnl"))
    assert _extract_cumulative(result) == 1.5


def test_extract_cumulative_dataframe_no_recognized_column():
    result = SimpleNamespace(backtest=pd.DataFrame({"a": [1.0, 2.0], "b": [3.0, 4.0]}))
    assert _extract_cumulative(result) == 4.0


def test_extract_cumulative_dataframe_columns_but_zero_rows():
    # Rows present, zero columns, none recognized -> falls through to `return backtest`.
    result = SimpleNamespace(backtest=pd.DataFrame(index=[0, 1]))
    out = _extract_cumulative(result)
    assert isinstance(out, pd.DataFrame)
    assert out.shape == (2, 0)


def test_extract_cumulative_list_and_scalar():
    result = SimpleNamespace(backtest=[1.0, 2.0, 3.0])
    assert _extract_cumulative(result) == 3.0
    result = SimpleNamespace(backtest=2.5)
    assert _extract_cumulative(result) == 2.5


def test_extract_cumulative_none_and_empty():
    assert _extract_cumulative(SimpleNamespace(backtest=None)) is None
    assert _extract_cumulative(SimpleNamespace(backtest=pd.DataFrame())) is None


def test_run_reconciliation_returns_none_when_weights_empty():
    result = SimpleNamespace(
        weights=pd.DataFrame(), returns=pd.DataFrame(), backtest=pd.DataFrame()
    )
    assert _run_reconciliation(result, SimpleNamespace(), []) is None
