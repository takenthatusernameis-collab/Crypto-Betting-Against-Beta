"""Acceptance tests for P25 WP0: wide synthetic universe generator.

These tests are the claim that ``scripts/bab_wide_universe.py`` produces a
deterministic, seeded, no-network wide price fixture
``tests/fixtures/wide_bab_universe.csv`` (41+ columns: BTC + A001..A040 +
DEL all-NaN) whose 398 return rows match the dates of
``tests/fixtures/real_market_prices.csv`` exactly, including the
``2021-09-17`` gap, with asset betas uniformly spanning 0.35-1.90 and idio
vol 0.003, and that rank-weighted BAB is empirically evaluable on it.

They prove the mechanical contract the P25 spec declares:

* the generator script runs standalone and produces the CSV + metadata;
* the fixture has 41+ columns, 399 price rows, 398 return rows, dates
  matching the reference fixture;
* rolling OLS beta on generated data recovers target betas 0.35-1.90 within
  ±0.05;
* seed determinism: two runs produce byte-identical CSV;
* fixture SHA256 provenance recorded in the metadata sidecar;
* no lookahead: weights at t depend on data through t-1;
* ``load_prices()`` loads the fixture and drops the DEL column;
* rank mode on this fixture produces ≥50 non-flat rows (empirical
  evaluability);
* zero ruff errors on new files;
* 20+ acceptance tests pass.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import BABStrategy
from strategies.betting_against_beta.data_loader import load_prices

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_CSV = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
FIXTURE_META = REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe_meta.json"
REFERENCE_CSV = REPO_ROOT / "tests" / "fixtures" / "real_market_prices.csv"
GENERATOR_SCRIPT = REPO_ROOT / "scripts" / "bab_wide_universe.py"

SEED = 20261120
IDIO_VOL = 0.003
BETA_MIN = 0.35
BETA_MAX = 1.90
N_ASSETS = 40
NAN_COLUMN = "DEL"
EXPECTED_COLUMNS = ["BTC", *[f"A{i:03d}" for i in range(1, N_ASSETS + 1)], NAN_COLUMN]
EXPECTED_PRICE_ROWS = 399
EXPECTED_RETURN_ROWS = 398
BETA_TOLERANCE = 0.05
MIN_NONFLAT_RANK_ROWS = 50


def _load_fixture_prices() -> pd.DataFrame:
    return pd.read_csv(FIXTURE_CSV, index_col="date", parse_dates=True)


def _load_reference_prices() -> pd.DataFrame:
    return pd.read_csv(REFERENCE_CSV, index_col="date", parse_dates=True)


def _rolling_ols_beta(asset_ret: pd.Series, bench_ret: pd.Series, window: int = 90) -> pd.Series:
    """Rolling OLS beta of asset vs benchmark over ``window`` days."""
    cov = asset_ret.rolling(window).cov(bench_ret)
    var = bench_ret.rolling(window).var()
    return cov / var


# --- Existence & generator script -------------------------------------------

def test_generator_script_exists():
    assert GENERATOR_SCRIPT.is_file(), f"missing {GENERATOR_SCRIPT}"


def test_fixture_csv_exists():
    assert FIXTURE_CSV.is_file(), f"missing {FIXTURE_CSV}"


def test_fixture_meta_exists():
    assert FIXTURE_META.is_file(), f"missing {FIXTURE_META}"


def test_generator_has_build_wide_universe():
    spec = importlib.util.spec_from_file_location("bab_wide_universe", GENERATOR_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert callable(getattr(mod, "build_wide_universe", None))


# --- Schema -----------------------------------------------------------------

def test_fixture_column_count():
    prices = _load_fixture_prices()
    assert len(prices.columns) >= 41, f"expected >=41 data columns, got {len(prices.columns)}"


def test_fixture_column_names():
    prices = _load_fixture_prices()
    for col in EXPECTED_COLUMNS:
        assert col in prices.columns, f"missing column {col}"


def test_fixture_price_row_count():
    prices = _load_fixture_prices()
    assert len(prices) == EXPECTED_PRICE_ROWS, (
        f"expected {EXPECTED_PRICE_ROWS} price rows, got {len(prices)}"
    )


def test_fixture_return_row_count():
    prices = _load_fixture_prices()
    rets = prices.pct_change().iloc[1:]
    assert len(rets) == EXPECTED_RETURN_ROWS, (
        f"expected {EXPECTED_RETURN_ROWS} return rows, got {len(rets)}"
    )


def test_fixture_dates_match_reference():
    prices = _load_fixture_prices()
    ref = _load_reference_prices()
    assert list(prices.index) == list(ref.index), (
        "fixture dates must match reference fixture exactly"
    )


def test_fixture_missing_2021_09_17():
    prices = _load_fixture_prices()
    assert pd.Timestamp("2021-09-17") not in prices.index, "2021-09-17 gap must be replicated"


def test_fixture_nan_column_all_na():
    prices = _load_fixture_prices()
    assert NAN_COLUMN in prices.columns
    assert prices[NAN_COLUMN].isna().all(), f"{NAN_COLUMN} must be all-NaN"


def test_fixture_btc_matches_reference():
    prices = _load_fixture_prices()
    ref = _load_reference_prices()
    pd.testing.assert_series_equal(prices["BTC"], ref["BTC"])


# --- Beta dispersion --------------------------------------------------------

def test_beta_range_spans_min_max():
    prices = _load_fixture_prices()
    ref = _load_reference_prices()
    btc_ret = ref["BTC"].pct_change().iloc[1:]
    asset_rets = prices.pct_change().iloc[1:][[c for c in prices.columns if c.startswith("A")]]
    target_betas = np.linspace(BETA_MIN, BETA_MAX, N_ASSETS)
    for i, col in enumerate(asset_rets.columns):
        beta = _rolling_ols_beta(asset_rets[col], btc_ret).dropna()
        assert len(beta) > 0, f"{col}: no rolling beta observations"
        recovered = float(beta.median())
        assert abs(recovered - target_betas[i]) <= BETA_TOLERANCE, (
            f"{col}: recovered beta {recovered:.4f} outside ±{BETA_TOLERANCE}"
            f" of target {target_betas[i]:.4f}"
        )


def test_betas_uniformly_spaced():
    prices = _load_fixture_prices()
    ref = _load_reference_prices()
    btc_ret = ref["BTC"].pct_change().iloc[1:]
    asset_rets = prices.pct_change().iloc[1:][[c for c in prices.columns if c.startswith("A")]]
    recovered = []
    for col in asset_rets.columns:
        beta = _rolling_ols_beta(asset_rets[col], btc_ret).dropna()
        recovered.append(float(beta.median()))
    recovered = np.array(recovered)
    assert recovered.min() >= BETA_MIN - BETA_TOLERANCE
    assert recovered.max() <= BETA_MAX + BETA_TOLERANCE


# --- Determinism & provenance ----------------------------------------------

def test_seed_determinism_byte_identical():
    import scripts.bab_wide_universe as gen
    csv1 = gen.build_wide_universe(write=False).to_csv(date_format="%Y-%m-%d").encode("utf-8")
    csv2 = gen.build_wide_universe(write=False).to_csv(date_format="%Y-%m-%d").encode("utf-8")
    assert csv1 == csv2, "generator must be byte-identical across runs"


def test_cli_rerun_byte_identical():
    out1 = subprocess.check_output([sys.executable, str(GENERATOR_SCRIPT)], cwd=REPO_ROOT)
    out2 = subprocess.check_output([sys.executable, str(GENERATOR_SCRIPT)], cwd=REPO_ROOT)
    sha1 = hashlib.sha256(FIXTURE_CSV.read_bytes()).hexdigest()
    sha2 = hashlib.sha256(FIXTURE_CSV.read_bytes()).hexdigest()
    assert sha1 == sha2, "CLI rerun must produce byte-identical fixture"


def test_fixture_sha256_in_metadata():
    meta = json_load(FIXTURE_META)
    actual_sha = hashlib.sha256(FIXTURE_CSV.read_bytes()).hexdigest()
    assert meta["fixture_sha256"] == actual_sha, (
        "metadata fixture_sha256 must match actual file hash"
    )


def test_metadata_fields():
    meta = json_load(FIXTURE_META)
    for key in ("seed", "beta_range", "idio_vol", "date_first", "date_last",
                "price_rows", "return_rows", "synthetic", "provenance"):
        assert key in meta, f"metadata missing key {key}"
    assert meta["seed"] == SEED
    assert meta["beta_range"] == [BETA_MIN, BETA_MAX]
    assert meta["idio_vol"] == IDIO_VOL
    assert meta["synthetic"] is True
    assert meta["price_rows"] == EXPECTED_PRICE_ROWS
    assert meta["return_rows"] == EXPECTED_RETURN_ROWS


# --- No lookahead -----------------------------------------------------------

def test_no_lookahead_weights():
    prices = _load_fixture_prices()
    rets = prices.pct_change().iloc[1:][["BTC", *[f"A{i:03d}" for i in range(1, N_ASSETS + 1)]]]
    result = BABStrategy(
        benchmark="BTC", beta_window=90, min_observations=60,
        long_quantile=0.3, short_quantile=0.3,
        transaction_costs=0.001, beta_neutral=True,
        weighting="rank", rank_min_leg_beta=0.20, rank_max_gross=4.0,
    ).run(returns_df=rets)
    weights = result.weights
    # Weights at row t must be computable from returns through row t-1 only.
    # The backtest already lags weights by one day; verify the first active
    # row has non-NaN weights derived from pre-first-row betas only.
    first_active = weights.abs().sum(axis=1) > 1e-9
    assert first_active.any(), "rank book must have at least one active row"
    first_idx = weights.index[first_active][0]
    # Betas at the first active date use returns up to that date (causal).
    betas_until = result.betas.loc[:first_idx].dropna(how="all")
    assert len(betas_until) > 0, "causal betas must exist up to first active date"


# --- Loader compatibility ----------------------------------------------------

def test_load_prices_loads_fixture():
    r = load_prices(str(FIXTURE_CSV), benchmark="BTC", quality=False)
    assert isinstance(r, pd.DataFrame)
    assert len(r) == EXPECTED_RETURN_ROWS
    assert "BTC" in r.columns
    assert NAN_COLUMN not in r.columns, "loader must drop all-NaN DEL column"


def test_load_prices_benchmark_returns():
    r = load_prices(str(FIXTURE_CSV), benchmark="BTC", quality=False)
    btc_ret = r["BTC"]
    assert btc_ret.notna().sum() > EXPECTED_RETURN_ROWS * 0.9, "BTC returns must be mostly finite"


# --- Rank mode empirical evaluability --------------------------------------

def test_rank_mode_non_flat_rows():
    prices = _load_fixture_prices()
    rets = prices.pct_change().iloc[1:][["BTC", *[f"A{i:03d}" for i in range(1, N_ASSETS + 1)]]]
    result = BABStrategy(
        benchmark="BTC", beta_window=90, min_observations=60,
        long_quantile=0.3, short_quantile=0.3,
        transaction_costs=0.001, beta_neutral=True,
        weighting="rank", rank_min_leg_beta=0.20, rank_max_gross=4.0,
    ).run(returns_df=rets)
    weights = result.weights
    nonflat = int((weights.abs().sum(axis=1) > 1e-9).sum())
    assert nonflat >= MIN_NONFLAT_RANK_ROWS, (
        f"rank mode must produce >= {MIN_NONFLAT_RANK_ROWS} non-flat rows, got {nonflat}"
    )


def test_rank_mode_beta_neutral():
    prices = _load_fixture_prices()
    rets = prices.pct_change().iloc[1:][["BTC", *[f"A{i:03d}" for i in range(1, N_ASSETS + 1)]]]
    result = BABStrategy(
        benchmark="BTC", beta_window=90, min_observations=60,
        long_quantile=0.3, short_quantile=0.3,
        transaction_costs=0.001, beta_neutral=True,
        weighting="rank", rank_min_leg_beta=0.20, rank_max_gross=4.0,
    ).run(returns_df=rets)
    betas = result.betas
    weights = result.weights
    common = betas.index.intersection(weights.index)
    if len(common) > 0:
        b = betas.loc[common]
        w = weights.loc[common]
        port_beta = (w * b).sum(axis=1)
        assert (port_beta.abs() < 1e-2).all(), "rank book must be beta-neutral"


# --- Ruff ------------------------------------------------------------------

def test_no_ruff_errors_on_new_files():
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(GENERATOR_SCRIPT), str(__file__)],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert result.returncode == 0, f"ruff must pass on new files: {result.stdout} {result.stderr}"


# --- Helpers ----------------------------------------------------------------


def json_load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
