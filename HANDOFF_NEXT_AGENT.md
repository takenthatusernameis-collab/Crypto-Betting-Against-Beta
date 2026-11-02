# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-02T03:02:03Z
**Priority from repo name:** Crypto Betting Against Beta (BAB) - market-neutral (long low-beta, short high-beta vs benchmark). ALL WORK MUST ADVANCE BAB.
**Session Mode:** Repo-prioritized, bottleneck-removal enforced. Heavy campaign required.
**Status:** BASELINE GREEN (1792 passed, 13 skipped). Pattern sync fixed. All gates verified.

## BOTTOM LINE - DO THIS FIRST (NO EXCEPTIONS)

Run Gate 0 immediately:
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python -m pytest -q  # MUST return: 1792 passed, 13 skipped
python3 -c "
from strategies.betting_against_beta import BABStrategy
s = BABStrategy()
r = s.run()
print(float(r.backtest['cumulative'].iloc[-1]))
"  # MUST produce finite float
```

If red, fix immediately. Never proceed without green baseline.

## BOTTLECKS REMOVED
- **Pattern sync:** Fixed `.github/workflows/main.yml` `stage_safe_changes()` to include `*/.github/workflows/*` (nested variant). Both Python `EXCLUDE_PATTERNS` and workflow now in sync. All controller pattern-sync tests pass.
- **Baseline:** Full suite 1792 passed, 13 skipped. Data loader/beta/BAB/core tests all green.

## HEAVY FORCED CAMPAIGN (COMPLETE IN ORDER)

### CAMPAIGN 1: DATA PIPELINE TO REAL DATA (HARDENING) - GATE 1
**Goal:** Bulletproof real-price/returns ingestion, keep synthetic defaults untouched.
**Focus:** `strategies/betting_against_beta/data_loader.py`, `data_sources.py`, `data.py`, `strategy.py` integration.
**Must do:** audit gaps, harden validation (tz-aware->UTC naive, duplicates, column strip, all-NaN drop, numeric coercion with commas/%, NA strings, inf rejection), multi-format robustness (CSV/JSON/parquet/HDF5/pickle), alignment guarantees (sorted index, no dupes, asset/benchmark aligned), create/update `scripts/load_real_bab_example.py` showing swap of `returns_df` into `BABStrategy.run()` with real CSV schema doc, defensive I/O.
**Gate 1:** `python -m pytest tests/test_bab_data_loader*.py -v` → all pass. Record changes + output.

### CAMPAIGN 2: BETA ROBUSTNESS & PERFORMANCE - GATE 2
**Goal:** Eliminate numerical fragility, optimize perf without API changes.
**Focus:** `strategies/betting_against_beta/beta.py`
**Must do:** stress NaN/inf/object/length mismatches/tiny windows (deterministic/safe → flat/zero weights), guard div-by-zero/degenerate cov/var/dtype coercion, run `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python scripts/perf_bench.py` before/after optimization with numbers, vectorize safely.
**Gate 2:** `python -m pytest tests/test_bab_beta_campaign*.py -v` → all pass. Record perf before/after + output.

### CAMPAIGN 3: SIGNALS/PORTFOLIO/BACKTEST CORRECTNESS - GATE 3
**Goal:** Lock no-lookahead, ranking, weighting, costs, dollar-neutrality under stress.
**Focus:** `signals.py`, `portfolio.py`, `backtest.py`
**Must do:** verify 1-day lag in backtest, turnover/cost application/weight shift, ranking/ties/small universes, quantile stability, lowest-beta long/highest-beta short, NaN/inf → flat periods, stress custom configs/costs on/off/small/large universes.
**Gate 3:** `python -m pytest tests/test_betting_against_beta*.py -v` → all pass. Explicitly verify lag+neutrality.

### CAMPAIGN 4: STRATEGY INTEGRATION, CLI, DOCS - GATE 4
**Goal:** Make BAB fully usable end-to-end with real data and clear docs.
**Focus:** `strategy.py`, `cli.py`, `README.md`
**Must do:** harden `BABStrategy.run()` with custom universe/benchmark/costs/quantiles/short/empty/messy data, ensure CLI functional (argparse/help/examples) fix if gaps, update README with concrete real-data swap example using Campaign 1 contract + custom config + costs, quick-start must work.
**Gate 4:** `python -c "from strategies.betting_against_beta import BABStrategy; s=BABStrategy(); r=s.run(); print(float(r.backtest['cumulative'].iloc[-1]))"` → finite. Record CLI help/smoke + README notes.

### CAMPAIGN 5: FULL SUITE HYGIENE & FLAKE SCAN - FINAL GATE
**Goal:** Absolute green, no regressions/flakiness.
**Must do:** full pytest, fix all regressions (no weakening assertions), hunt randomness/seed if found, note slow tests only if blocking and behavior-preserving, confirm quick-start.
**Gate 5 (MANDATORY):** `python -m pytest -q` → `1792 passed, 13 skipped` AND smoke test finite. Record full summary.

## NON-NEGOTIABLE RULES
- **BASELINE FIRST:** Gate 0 mandatory. Never skip.
- **GATE ENFORCEMENT:** Complete 1-5 in order. Don't advance until current gate passes.
- **MAINTAIN GREEN:** 1792 passed, 13 skipped must remain. Never break existing passing tests.
- **BAB FIRST:** Crypto Betting Against Beta above everything else.
- **HEAVY WORK REQUIRED:** Trivial one-liners insufficient. Full campaign with concrete deliverables.
- **NO UNNECESSARY WORKFLOW CHANGES:** Only touch `.github/workflows/*` if absolutely required to unblock BAB AND pattern-sync tests still pass.
- **PRESERVE CONTRACTS:** Keep synthetic defaults. Preserve public APIs unless no alternative AND all affected tests updated with justification.
- **EVIDENCE MANDATORY:** For each gate, record what changed and command output summary.
- **NO LOOKAHEAD:** Weights must be lagged by 1 day. Never introduce lookahead.
- **DEFENSIVE BY DEFAULT:** Validate, coerce safely, fail clearly.

**START NOW:** Run Gate 0. If green, begin Campaign 1 immediately. Do not stop until Gate 5 passes.
