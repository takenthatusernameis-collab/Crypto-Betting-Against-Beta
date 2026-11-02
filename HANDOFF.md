# HANDOFF - Crypto-Betting-Against-Beta

**Created:** 2026-11-02T01:05:46Z
**Last updated:** 2026-11-02T01:07:11Z
**Session:** Campaign kickoff - enforce BAB-first heavy work (Data Pipeline Hardening is the blocking gate)
**Status:** ALL TESTS PASSING (1792 passed, 13 skipped). Baseline re-confirmed green after fixing pattern-sync regression.

## Project Priority (Crypto Betting Against Beta)
Repository focus: **Crypto Betting Against Beta (BAB)** - market-neutral strategy going long low-beta crypto, short high-beta crypto vs benchmark (default BTC). All work must advance the BAB strategy (data, beta, signals/portfolio/backtest, integration, tests). Do not drift to unrelated infra unless it directly unblocks BAB.

## Bottlenecks Removed (this session)
- **Pattern sync enforced:** `*/.github/workflows/*` added to `.github/workflows/main.yml` `stage_safe_changes()` list to match `scripts/controller_progress.py:EXCLUDE_PATTERNS`. Pattern-sync tests now pass; full suite is green (1792 passed, 13 skipped). No further workflow drift tolerated.

## CLEAR INITIAL TASK FOR NEXT AGENT (DO THIS FIRST - NO EXCEPTIONS)
The baseline (Gate 0) is confirmed green. Proceed immediately to **Campaign 1: Data Pipeline Hardening** (the blocking gate). Do not start any other campaign.

First, re-confirm the baseline one more time:
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python -m pytest -q  # MUST be 1792 passed, 13 skipped
python3 -c "from strategies.betting_against_beta import BABStrategy; s=BABStrategy(); r=s.run(); print(float(r.backtest['cumulative'].iloc[-1]))"  # MUST produce a float
```
If anything deviates, fix the regression before touching Campaign 1. The baseline is a hard gate.

Then begin **Campaign 1: Data Pipeline Hardening** (see below) and do not stop until Gate 1 passes:
```bash
python -m pytest tests/test_bab_data_loader*.py -v
```
**Goal:** Make the data path robust for real prices while keeping synthetic defaults intact. This is the bottleneck that will block real-data runs and is the most impactful next step for BAB.

- [ ] **Audit loaders:** Review `strategies/betting_against_beta/data_loader.py` and `strategies/betting_against_beta/data_sources.py` end-to-end. Fix edge cases (CSV/JSON/parquet/HDF5/pickle), enforce clear errors, and avoid silent corruption.
- [ ] **Validation:** Ensure datetime normalization, numeric coercion, duplicate column/index handling, index alignment across assets/benchmark, and min-history enforcement. Match behavior to existing campaign specs.
- [ ] **Real data contract:** Define/document expected schema (columns, index tz/naive, asset symbols) and add a minimal, concrete example script (e.g. `scripts/load_real_bab_example.py` or equivalent) showing how to swap `returns_df` into `BABStrategy.run()`. Do **not** remove synthetic defaults.
- [ ] **Defensive I/O:** Add/strengthen guards for missing files, empty frames, all-NaN columns, and insufficient observations per asset/benchmark.

**MANDATORY GATE 1 (must pass):**
```bash
python -m pytest tests/test_bab_data_loader*.py -v
```
All data loader tests must pass. If none exist but the campaign surfaces gaps, add minimal tests only where necessary to lock behavior (without deleting existing tests).

### Campaign 2: Beta Calculation Robustness & Performance (GATE)
**Goal:** Hardening rolling OLS against real messy data and removing avoidable perf bottlenecks without changing public API.

- [ ] **Edge cases:** Stress `strategies/betting_against_beta/beta.py` (NaN/inf/object arrays, mismatched lengths, insufficient windows). Ensure `calculate_beta` and `calculate_rolling_beta` are deterministic and return sane values (flat/zero-weight safe) on bad inputs.
- [ ] **Numerics:** Guard against division by zero, degenerate variance/covariance, and dtype issues. Do not change function signatures.
- [ ] **Perf:** Run `python scripts/perf_bench.py` and identify concrete hotspots in rolling windows. Prefer vectorization (pandas/numpy) where safe. Benchmark before/after and only optimize if it doesn't change behavior.
- [ ] **Coverage:** Ensure all beta campaign tests pass and fix any discovered gaps with minimal, targeted changes.

**MANDATORY GATE 2 (must pass):**
```bash
python -m pytest tests/test_bab_beta_campaign*.py -v
```

### Campaign 3: Signals/Portfolio/Backtest Correctness (GATE)
**Goal:** Lock in no-lookahead, correct ranking/weighting, and numeric stability under stress.

- [ ] **No-lookahead:** Verify weights are lagged by 1 day in `backtest.py`; transaction costs applied to turnover correctly; portfolio remains dollar-neutral (long/short weights sum to ~0).
- [ ] **Ranking/ties:** Test quantile stability, tie-breaking, and behavior for small universes (edge counts). Ensure lowest-beta quantile long, highest-beta short per config.
- [ ] **Numerics:** Audit for division by zero, inf/nan propagation, NaN/insufficient history producing flat (zero-weight) periods as intended.
- [ ] **Integration:** Spot check `signals.py` + `portfolio.py` + `backtest.py` against existing `tests/test_betting_against_beta.py` expectations.

**MANDATORY GATE 3 (must pass):**
```bash
python -m pytest tests/test_betting_against_beta*.py -v
```

### Campaign 4: Strategy Integration, CLI & Docs (GATE)
**Goal:** Make BAB usable end-to-end with custom configs and real data, and document the real-data swap clearly.

- [ ] **End-to-end:** Test `BABStrategy.run()` with custom configs, empty/short data, benchmark variations, and transaction costs. Ensure it returns sensible objects and doesn't crash on edge cases.
- [ ] **CLI:** If `strategies/betting_against_beta/cli.py` exists, make it usable (argparse, config loading, help/examples). If missing but useful for running campaigns/experiments, add a minimal CLI without overengineering.
- [ ] **Docs:** Update `README.md` with concrete examples (custom universe/benchmark, real data swap using the contract from Campaign 1, transaction costs). Keep it short and actionable.
- [ ] **Smoke test:** Verify the quick-start example still works with default config.

**MANDATORY GATE 4 (must pass):**
```bash
python -c "from strategies.betting_against_beta import BABStrategy; s=BABStrategy(); r=s.run(); print(float(r.backtest['cumulative'].iloc[-1]))"
```

### Campaign 5: Full Suite Hygiene & Flake Scan (FINAL GATE - DO NOT SKIP)
**Goal:** Restore/maintain full green and eliminate any introduced flakiness.

- [ ] **Full suite:** Run full pytest and fix any regressions introduced by campaigns 1-4. Do not weaken assertions.
- [ ] **Flakiness:** Scan for non-determinism (random seeds). If found, seed or fix.
- [ ] **Perf awareness:** Note slow tests from summary; only optimize if clearly bottlenecking and behavior-preserving.
- [ ] **Final verification:** Confirm strategy quick-start still works.

**MANDATORY GATE 5 (must pass):**
```bash
python -m pytest -q  # MUST be 1792 passed, 13 skipped
python3 -c "from strategies.betting_against_beta import BABStrategy; s=BABStrategy(); r=s.run(); print(float(r.backtest['cumulative'].iloc[-1]))"
```

## Rules for Next Agent (STRICT)
- **BASELINE FIRST:** Gate 0 (initial task) is mandatory. Never skip it.
- **GATE ENFORCEMENT:** Complete gates in order. Do not move to next campaign until current gate passes.
- **MAINTAIN GREEN:** All 1792 passing, 13 skipped must remain. Never break existing passing tests.
- **PROJECT-FIRST:** Prioritize BAB strategy work above all else.
- **HEAVY WORK REQUIRED:** Do the full campaign sequence above. Trivial one-line fixes alone are not sufficient.
- **NO UNNECESSARY WORKFLOW CHANGES:** Only change `.github/workflows/*` if absolutely required to unblock BAB and pattern-sync tests still pass.
- **CONCRETE DELIVERABLES:** Each campaign item must be completed with evidence (gate output). Document what changed and why.
- **DEFENSIVE CHANGES:** Keep synthetic defaults intact. Preserve public APIs unless there's no other way and all affected tests are updated with justification.
