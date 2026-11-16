# Agent Handoff — 2026-11-16T04:42:58Z

## Project: Crypto-Betting-Against-Beta
**Repository**: `Crypto-Betting-Against-Beta`
**Description**: Controller infrastructure + Betting Against Beta (BAB) strategy for crypto. Market-neutral strategy going long low-beta / short high-beta assets vs BTC benchmark using Frazzini-Pedersen approach.

## Current State (Verified)
- **Tests**: 6,163 passed, 35 skipped (`pytest -n auto`)
- **Lint**: `ruff check .` — clean
- **Type check**: No mypy/pyright configured (optional)
- **Strategy pipeline**: Fully implemented (config → beta → signals → portfolio → backtest → execution adapters)
- **CLI**: Complete with `--adapter paper|mock|live`, `--dry-run`, `--paper-trading`, `--health-check`, `--reconcile`

## Critical Blocker (Must Fix First)
**Test Failure**: `tests/test_controller_progress_accounting.py::TestStageSafeChangesPatternSync`

### Root Cause
Pattern drift between Python `EXCLUDE_PATTERNS` (`scripts/controller_progress.py:26-71`) and bash `stage_safe_changes` case pattern (`.github/workflows/main.yml:1163`).

| Pattern | Python `EXCLUDE_PATTERNS` | Bash `stage_safe_changes` |
|---------|---------------------------|---------------------------|
| `.github/workflows/*` | ✅ | ✅ |
| `*/.github/workflows/*` (nested) | ✅ | ❌ **MISSING** |

The test `test_python_patterns_are_subset_of_workflow` fails because Python excludes nested workflow paths but the bash case pattern does not. The test comment claims "nested workflow paths are covered by the force-restore guard" but the force-restore at line 1184-1185 only targets `.github/workflows` at repository root:

```bash
git restore --source="$base_sha" --staged --worktree -- .github/workflows
git clean -fd -- .github/workflows
```

### Required Fix
Update `.github/workflows/main.yml` line 1184-1185 to handle nested workflow directories:

```bash
# Line 1184-1185: ADD nested variant
git restore --source="$base_sha" --staged --worktree -- .github/workflows */.github/workflows >/dev/null 2>&1 || true
git clean -fd -- .github/workflows */.github/workflows >/dev/null 2>&1 || true
```

**AND** add the nested pattern to the `stage_safe_changes` case statement (line 1163) for defense-in-depth:

```bash
# Line 1163: ADD | */.github/workflows/*
case "$changed_path" in
  .github/workflows/*|*/.github/workflows/*|.venv/*|...
```

### Verification
After fix, run:
```bash
python3 -m pytest tests/test_controller_progress_accounting.py::TestStageSafeChangesPatternSync -v
```

---

## Next Focus Campaign (Heavy Work — No Avoidance)
Once the blocker is resolved, the next agent **must** execute this campaign. No optional tasks.

### Campaign: Production Hardening & Observability
**Objective**: Close remaining gaps between backtest and live execution paths.

#### 1. Live Execution Adapter — Network Integration Tests
**Files**: `strategies/betting_against_beta/execution.py`, `tests/test_bab_live_adapter.py`
- Current: `LiveExecutionAdapter` is dry-run only (no network, simulated fills)
- **Task**: Add optional `--live-execute` flag (env-gated, explicit opt-in) that hits real CCXT endpoints
- **Safety**: Never implicit; requires `--allow-live-execution` + exact `--accept-terms` (mirror `fetch_real_bab_prices.py` pattern)
- **Test**: New `test_bab_live_adapter_real_execution.py` with mocked CCXT responses + 1 integration test marked `@pytest.mark.live` (opt-in)

#### 2. Reconciliation Completeness (R5-B/R5-C)
**Files**: `strategies/betting_against_beta/reconciliation.py`, `strategies/betting_against_beta/cli.py:90-123`
- Current: `reconcile_costs` and `reconcile_fills_to_backtest` exist but CLI `--reconcile` only emits artifacts
- **Task**: Add CI gate — fail workflow if reconciliation drift > threshold (configurable: `--reconcile-tolerance`)
- **Metric**: Modeled cost vs executed cost; fills vs backtest P&L delta
- **Test**: `test_bab_reconciliation_ci_gate.py` — inject drift, assert non-zero exit

#### 3. Data Freshness & Quality Gates (P8/P17-1)
**Files**: `strategies/betting_against_beta/data_loader.py`, `strategies/betting_against_beta/cli.py:205-226`
- Current: `--max-staleness-days` / `--max-gap-days` flags exist; `_safe_quality` dict hardcoded in CLI
- **Task**: Promote thresholds to `BABConfig` fields; add `--quality-profile strict|loose|off` to CLI
- **Test**: `test_bab_quality_gate_config.py` — config-driven quality rejects frozen/gapped data

#### 4. Kill Switch Integration Test (R4-B)
**Files**: `strategies/betting_against_beta/risk.py`, `strategies/betting_against_beta/strategy.py:547-581`
- Current: `apply_kill_switch` truncates weights on MDD breach; re-runs backtest
- **Gap**: No test verifies kill-switch triggers on realistic drawdown path
- **Task**: Add `test_bab_kill_switch_trigger.py` — synthetic path breaching `max_drawdown_limit`, assert weights flatten post-breach, cumulative P&L matches expectation

#### 5. Performance Baseline Enforcement
**Files**: `scripts/perf_baseline.py`, `research_state/perf_baseline_real_fixture.json`
- Current: Baseline recorded (beta ~0.48ms, full ~3.2ms on 398×9 fixture)
- **Task**: Add `pytest --perf-baseline` gate in CI; fail if median regression > 15%
- **Test**: `test_bab_perf_regression_gate.py` — compare current run vs stored baseline

---

## Architecture Notes for Next Agent
- **Entry point**: `BABStrategy.run()` (strategy.py:324) — single method runs full pipeline
- **Config**: `BABConfig` (config.py) — all knobs; supports dict shorthands for sizers/constraints
- **Execution adapters** (execution.py): `PaperAdapter` (deterministic JSONL), `MockAdapter` (fixture fills), `LiveExecutionAdapter` (CCXT, dry-run default)
- **Data loader** (data_loader.py): `load_returns`/`load_prices` — CSV/JSON/Parquet/HDF5/Pickle; quality validation
- **Beta calc** (beta.py): Vectorized rolling OLS with NaN-safe cumulative sums; benchmark beta = 1.0
- **Signals** (signals.py): Quantile ranking → long/short; NaN betas → flat (0 weight)
- **Portfolio** (portfolio.py): Equal-weight, dollar-neutral; turnover/risk limits optional
- **Backtest** (backtest.py): One-day lagged weights; flat costs + R3-A realistic cost model (impact/participation)
- **Metrics** (metrics.py): Sharpe, max DD, turnover, strategy beta, attribution (gross/cost/slippage/net)

## Key Files to Read First
1. `strategies/betting_against_beta/strategy.py` — pipeline orchestration
2. `strategies/betting_against_beta/beta.py` — core numerics
3. `strategies/betting_against_beta/execution.py` — adapter interfaces
4. `.github/workflows/main.yml` — controller loop + checkpoint logic
5. `scripts/controller_progress.py` — progress accounting (fix target)

## Anti-Patterns to Avoid
- ❌ Adding new test files without running full suite (`pytest -n auto`)
- ❌ Modifying `EXCLUDE_PATTERNS` without updating workflow bash pattern (and vice versa)
- ❌ Silent fallbacks — this codebase fails loudly (`BABDataError`) on bad input
- ❌ Skipping the blocker fix — workflow will continue failing diagnostics

## Success Criteria for This Handoff
1. Blocker test passes (`TestStageSafeChangesPatternSync`)
2. Campaign item 1 (Live Adapter real execution) has failing test written (TDD)
3. Campaign item 2 (Reconciliation CI gate) has failing test written
4. All 6,163+ tests still pass

---

**Next agent**: Start with the blocker fix. Then pick Campaign Item 1 and write the failing test first. Do not proceed to implementation until the test fails for the right reason.