# HANDOFF - Crypto-Betting-Against-Beta

**Created:** 2026-11-02T00:01:07Z
**Session:** Controller pattern-sync bottleneck REMOVED (staged .github/workflows/* nested pattern)
**Status:** ALL TESTS PASSING (1792 passed, 13 skipped)

## Project Priority (Crypto Betting Against Beta)
Repository focus: **Crypto Betting Against Beta (BAB)** - market-neutral strategy going long low-beta crypto, short high-beta crypto vs benchmark (default BTC). Prioritize work that advances the BAB strategy implementation, data/robustness, performance, and test coverage of campaign-heavy paths.

## Bottlenecks Removed
- **Pattern sync fixed**: Added `*/.github/workflows/*` to `.github/workflows/main.yml` `stage_safe_changes()` to match `scripts/controller_progress.py:EXCLUDE_PATTERNS`. All controller progress accounting tests green.

## HEAVY FOCUS CAMPAIGN (do not avoid this work)
Execute these in order - each item is concrete and verifiable.

### Campaign 1: Data Pipeline Hardening (Critical for real data)
- [ ] **Audit data loaders**: Review `strategies/betting_against_beta/data_loader.py` and `data_sources.py` end-to-end. Fix any edge cases around CSV/JSON/parquet/HDF5/pickle with proper errors.
- [ ] **Validation**: Ensure datetime normalization, numeric coercion, duplicate column/index handling, min history enforcement. Leverage existing campaign tests as spec.
- [ ] **Real data path**: Add/verify a simple example script to load real prices (document expected schema). Keep synthetic defaults intact.

**Verify:** `python -m pytest tests/test_bab_data_loader*.py -v`

### Campaign 2: Beta Calculation Robustness & Performance
- [ ] **Rolling beta edge cases**: Stress `beta.py` (NaN/inf/object arrays/mismatched lengths). Ensure `calculate_rolling_beta` and `calculate_beta` behave deterministically; add guards without changing public API.
- [ ] **Perf profiling**: Run `python scripts/perf_bench.py` and identify hotspots in rolling windows. Consider vectorization where safe (pandas/numpy). Don't break existing tests.
- [ ] **Campaign coverage**: Ensure heavy beta campaign tests all pass and add minimal fixes only if gaps found.

**Verify:** `python -m pytest tests/test_bab_beta_campaign*.py -v`

### Campaign 3: Signals/Portfolio/Backtest Correctness
- [ ] **No-lookahead**: Verify weights are lagged by 1 day in backtest; transaction costs applied correctly; dollar-neutral long/short.
- [ ] **Quantile stability**: Test tie-breaking/ranking behavior for small universes and edge cases.
- [ ] **Cumulative/math**: Check for division by zero, inf/nan propagation. Strategy should return sensible objects on bad inputs.

**Verify:** `python -m pytest tests/test_betting_against_beta*.py -v`

### Campaign 4: Strategy Integration & CLI
- [ ] **End-to-end**: Test `BABStrategy.run()` with custom configs, empty/short data, benchmark variations.
- [ ] **CLI**: If `strategies/betting_against_beta/cli.py` exists, make it usable (argparse, config loading). Add help/examples. If missing but useful, add minimal CLI without overengineering.
- [ ] **Docs**: Update README with concrete examples (custom universe/benchmark, real data swap, costs).

**Verify:** `python -c "from strategies.betting_against_beta import BABStrategy; s=BABStrategy(); r=s.run(); print(r.backtest['cumulative'].iloc[-1])"`

### Campaign 5: Test Suite Hygiene (Large Suite Management)
- [ ] **Full green**: Maintain `python -m pytest -q` green. Targeted runs for debugging.
- [ ] **Flakiness**: Watch for any non-determinism (random seeds). Fix if found.
- [ ] **Perf**: Note slow tests from summary; optimize only if clearly bottlenecking without changing behavior.

**Verify:** `python -m pytest -q`

## Quick Start (MUST DO FIRST)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python -m pytest -q  # expect 1792 passed, 13 skipped
python3 -c "from strategies.betting_against_beta import BABStrategy; s=BABStrategy(); r=s.run(); print(float(r.backtest['cumulative'].iloc[-1]))"
```

## Rules for Next Agent
- **MAINTAIN GREEN**: Never break existing passing tests. All 1792 must stay passing.
- **PROJECT-FIRST**: Prioritize BAB strategy work over unrelated changes.
- **HEAVY WORK**: Do the campaigns above - don't stop at trivial fixes.
- **NO WORKFLOW CHANGES** unless absolutely necessary and pattern-sync tests still pass.
- **CONCRETE DELIVERABLES**: Each campaign item should be completed with verification.
