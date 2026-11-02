# HANDOFF - Crypto-Betting-Against-Beta

**Created:** 2026-11-02T01:14:12Z
**Last updated:** 2026-11-02T01:14:12Z
**Inferred priority from repo name:** Crypto Betting Against Beta (BAB) - market-neutral (long low-beta, short high-beta vs benchmark). ALL WORK MUST ADVANCE BAB.
**Session Mode:** Repo-prioritized, bottleneck-removal enforced. Heavy campaign required.
**Status:** BASELINE GREEN (1792 passed, 13 skipped). Ready for forced heavy execution.

## Project Priority (Crypto Betting Against Beta)
Focus exclusively on **Betting Against Beta for crypto**: universe selection, benchmark (default BTC), rolling beta vs benchmark, rank by beta -> long lowest-beta quantile / short highest-beta quantile (default 30/30), dollar-neutral equal-weight, one-day lagged weights, transaction costs. Do not drift to unrelated infra. Only touch workflows/configs if strictly necessary to unblock BAB and must not break pattern-sync.

## Bottlenecks Removed (Current State)
- **Pattern sync:** `.github/workflows/*` included in `stage_safe_changes()` to match `scripts/controller_progress.py:EXCLUDE_PATTERNS` (regression fixed). Enforced.
- **Data loader coverage:** Extensive loader/validation tests present and passing (232 passed across loader suites).
- **Baseline intact:** Full suite green at 1792 passed, 13 skipped.

## SINGLE CLEAR INITIAL TASK FOR NEXT AGENT (DO FIRST - NO EXCEPTIONS)
You MUST establish and lock the baseline before doing ANY heavy work. This is a hard gate.

### GATE 0 - BASELINE LOCK (MANDATORY)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python -m pytest -q  # MUST return: 1792 passed, 13 skipped
python3 -c "
from strategies.betting_against_beta import BABStrategy
s = BABStrategy()
r = s.run()
print(float(r.backtest['cumulative'].iloc[-1]))
"  # MUST produce a finite float
```
If either check fails, fix regressions immediately. Do not proceed.

## FORCED HEAVY CAMPAIGN - "REAL DATA HARDENING + RIGOR" (NO ESCAPE HATCH)
This campaign is designed to force substantial, non-trivial work. Complete in strict order. Each gate must pass with evidence.

### CAMPAIGN 1: DATA PIPELINE TO REAL DATA (HARDENING) - GATE 1
**Goal:** Make real-price/returns ingestion bulletproof while keeping synthetic defaults untouched.

**Tasks (MUST DO ALL):**
- [ ] **Audit end-to-end:** Review `strategies/betting_against_beta/data_loader.py`, `strategies/betting_against_beta/data_sources.py`, `strategies/betting_against_beta/data.py`. Document any gaps in schema, alignment, coercion.
- [ ] **Harden validation:** Enforce datetime normalization (tz-aware -> UTC naive), duplicate handling, column stripping, all-NaN column drop, numeric coercion (commas/%, NA strings), inf rejection, benchmark presence + finiteness, min-rows.
- [ ] **Multi-format robustness:** Test/strengthen CSV/JSON/parquet/HDF5/pickle paths. Clear errors with actionable messages (no silent failures).
- [ ] **Alignment guarantees:** Ensure asset/benchmark index alignment, sorted index, no index/column duplicates causing leakage or misalignment.
- [ ] **Real-data contract:** Create/complete `scripts/load_real_bab_example.py` showing concrete swap of `returns_df` into `BABStrategy.run()` with real CSV example. Include schema doc in docstring/comments.
- [ ] **Defensive I/O:** Handle missing files, empty frames, all-NaN, insufficient history per asset/benchmark.

**GATE 1 (MANDATORY):**
```bash
python -m pytest tests/test_bab_data_loader*.py -v  # all must pass
```
**Evidence required:** Summary of changes + gate output.

### CAMPAIGN 2: BETA ROBUSTNESS & PERFORMANCE - GATE 2
**Goal:** Eliminate numerical fragility and real perf issues without changing public API.

**Tasks (MUST DO ALL):**
- [ ] **Edge hardening:** Stress `beta.py` (NaN/inf/object, length mismatch, tiny windows). `calculate_beta` and `calculate_rolling_beta` must be deterministic, safe (flat/zero-weights on bad inputs).
- [ ] **Numerics:** Guard div-by-zero, degenerate cov/var, dtype coercion. No signature changes.
- [ ] **Vectorize/optimize:** Run `python scripts/perf_bench.py`. Find hotspots, optimize with numpy/pandas safely. Benchmark before/after with numbers.
- [ ] **Regression lock:** Fix any beta-related gaps found.

**GATE 2 (MANDATORY):**
```bash
python -m pytest tests/test_bab_beta_campaign*.py -v  # all must pass
```
**Evidence required:** perf_bench before/after + gate output.

### CAMPAIGN 3: SIGNALS/PORTFOLIO/BACKTEST CORRECTNESS - GATE 3
**Goal:** Lock no-lookahead, ranking, weighting, costs, dollar-neutrality under stress.

**Tasks (MUST DO ALL):**
- [ ] **No-lookahead:** Verify 1-day lag in `backtest.py`, turnover/cost application, weights shifted correctly.
- [ ] **Ranking/ties/small universes:** Quantile stability, tie-breaking, edge counts, lowest-beta long / highest-beta short.
- [ ] **Numerics:** NaN/inf handling, flat periods on insufficient history.
- [ ] **Stress integration:** Test with custom configs, costs on/off, small/large universes.

**GATE 3 (MANDATORY):**
```bash
python -m pytest tests/test_betting_against_beta*.py -v  # all must pass (core BAB tests)
```
**Evidence required:** explicit verification of lag + neutrality + gate output.

### CAMPAIGN 4: STRATEGY INTEGRATION, CLI, DOCS - GATE 4
**Goal:** Make BAB fully usable end-to-end with real data and clear docs.

**Tasks (MUST DO ALL):**
- [ ] **End-to-end hardening:** `BABStrategy.run()` with custom universe/benchmark/costs/quantiles, short/empty/messy data.
- [ ] **CLI:** Ensure `strategies/betting_against_beta/cli.py` is functional (argparse, help, examples). If gaps, fix/add minimally.
- [ ] **Docs:** Update `README.md` with concrete real-data swap example using Campaign 1 contract, custom config, costs. Keep actionable.
- [ ] **Smoke:** Quick-start must still work.

**GATE 4 (MANDATORY):**
```bash
python -c "from strategies.betting_against_beta import BABStrategy; s=BABStrategy(); r=s.run(); print(float(r.backtest['cumulative'].iloc[-1]))"  # finite float
```
**Evidence required:** CLI help/smoke + README update notes + gate output.

### CAMPAIGN 5: FULL SUITE HYGIENE & FLAKE SCAN - FINAL GATE (DO NOT SKIP)
**Goal:** Absolute green, no regressions, no flakiness.

**Tasks (MUST DO ALL):**
- [ ] **Full suite:** Run full pytest. Fix every regression introduced (no weakening assertions).
- [ ] **Determinism:** Hunt for randomness; seed if found.
- [ ] **Perf scan:** Note slow tests; only optimize if blocking and behavior-preserving.
- [ ] **Final verification:** Strategy quick-start confirmed.

**GATE 5 (MANDATORY - FINAL):**
```bash
python -m pytest -q  # MUST be 1792 passed, 13 skipped
python3 -c "from strategies.betting_against_beta import BABStrategy; s=BABStrategy(); r=s.run(); print(float(r.backtest['cumulative'].iloc[-1]))"  # MUST be finite
```
**Evidence required:** Full suite summary + final smoke output.

## RULES FOR NEXT AGENT (STRICT - NON-NEGOTIABLE)
- **BASELINE FIRST:** Gate 0 is mandatory. Never skip.
- **GATE ENFORCEMENT:** Complete in order 1-5. Do not advance until current gate passes.
- **MAINTAIN GREEN:** 1792 passed, 13 skipped must remain. Never break existing passing tests.
- **BAB FIRST:** Crypto Betting Against Beta above everything else.
- **HEAVY WORK REQUIRED:** Trivial one-liners are insufficient. Do the full campaign with concrete deliverables.
- **NO UNNECESSARY WORKFLOW CHANGES:** Only touch `.github/workflows/*` if absolutely required to unblock BAB AND pattern-sync tests still pass.
- **PRESERVE CONTRACTS:** Keep synthetic defaults. Preserve public APIs unless no alternative exists AND all affected tests updated with justification.
- **EVIDENCE MANDATORY:** For each gate, record what changed and command output summary.
- **NO LOOKAHEAD:** Never introduce lookahead. Weights must be lagged by 1 day.
- **DEFENSIVE BY DEFAULT:** Validate, coerce safely, fail clearly.

**START NOW:** Run Gate 0. If green, begin Campaign 1 immediately. Do not stop until Gate 5 passes.
