# NEXT AGENTIC WORK SESSION HANDOFF
**Timestamp:** 2026-11-16T01:04:16Z
**Project:** Crypto-Betting-Against-Beta (Betting Against Beta - BAB strategy for crypto)
**Repository:** /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta

---

## PROJECT STATUS SUMMARY

### ✅ GREEN - GATE PASSING
- **Test Suite:** 6,153 passed, 35 skipped (0 failed)
- **Coverage:** 99% TOTAL (exceeds 98.5% floor)
- **Gate Script:** `scripts/bab_gate.sh` - passes with `BAB_GATE_MIN_COVERAGE=98.5`
- **Runtime:** ~4 min serial, ~5-6 min parallel (pytest-xdist loadscope)

### 📊 COVERAGE GAPS (Priority Order)

| Module | Coverage | Missing Lines | Key Areas |
|--------|----------|---------------|-----------|
| `portfolio.py` | 95% | 11 | Risk checks (L152-153, 170-177, 180), beta neutrality edge cases |
| `beta.py` | 97% | 12 | Degenerate beta handling (L125, 163, 170-171, 189, 435-436, 552-556) |
| `data_loader.py` | 98% | 37 | Date coercion edge cases (L280-292, 296-297, 315-316, 422-423, 666-667, 718-719, 837-838, 1355, 1609, 1648-1649, 1654-1656, 1667-1675, 1951-1952, 2746-2747) |
| `data_sources.py` | 98% | 6 | Exchange API error paths (L480-481, 499-500, 507-508) |
| `execution.py` | 99% | 11 | Order fill edge cases (L139-141, 182-185, 555-556, 1287-1288) |
| `reconciliation.py` | 98% | 3 | Position reconciliation gaps (L82-83, 309) |
| `signals.py` | 98% | 2 | Signal generation edge cases (L37, 75) |
| `cli.py` | 99% | 7 | CLI error reporting (L589-590, 746-748, 803-804) |

---

## TOP 3 BOTTLENECKS TO REMOVE

### 1. DATA_LOADER COVERAGE GAPS (37 lines)
**File:** `strategies/betting_against_beta/data_loader.py`
**Impact:** Core data ingestion - any gap risks silent data corruption
**Action:** Add tests for:
- `_coerce_series_to_datetime_index` failure paths (L125-148)
- `_normalize_index` numeric index parsing edge cases (L169-246)
- `_coerce_to_datetime_scalar` NaT/None/float edge cases (L357-512)
- `_detect_and_normalize_exchange_format` long-format pivot failures (L574-667)
- `_promote_datetime_column` conservative promotion logic (L743-758)
- `_drop_all_nan_columns` all-NaN DataFrame handling (L1199-1200)
- `_strip_units_and_parse` malformed numeric strings (L1299-1300)

### 2. PORTFOLIO RISK CHECKS (11 lines)
**File:** `strategies/betting_against_beta/portfolio.py`
**Impact:** Risk management - uncovered paths = untested constraint violations
**Action:** Add tests for:
- Position size limit enforcement (L196-198)
- Turnover limit with previous weights (L217-219)
- Gross/net exposure limits (L243-250)
- Beta neutrality correction with degenerate betas (L342-366)

### 3. BETA CALCULATION DEGENERATE CASES (12 lines)
**File:** `strategies/betting_against_beta/beta.py`
**Impact:** Core alpha signal - beta estimation errors propagate to weights
**Action:** Add tests for:
- `calculate_beta` all-NaN mask (L125)
- `calculate_beta_fast` empty/None input guards (L163, 170-171, 189)
- `calculate_rolling_beta` degenerate benchmark per-window (L435-436)
- Fallback path `_calc_rolling_beta_series` error handling (L552-556)

---

## MANDATORY NEXT FOCUS CAMPAIGN

### Campaign: **ACHIEVE 100% COVERAGE - CLOSE ALL GAPS**

**Non-negotiable deliverables for next session:**
1. **Zero missing lines** across all 8 modules with <100% coverage
2. **No new test files** - extend existing campaign tests (`test_bab_*_campaign*.py`)
3. **Preserve gate performance** - tests must complete within existing 6-min parallel budget
4. **No coverage floor reduction** - 98.5% is minimum, target is 100%

**Test Strategy:**
- Target the specific line numbers above with hypothesis-based property tests
- Use existing test patterns: `test_bab_beta_deep_final.py`, `test_bab_data_loader_campaign_d_final_push.py`
- Each gap needs 1-3 focused tests covering the exact branch

**Validation:**
```bash
BAB_GATE_SERIAL=1 BAB_GATE_MIN_COVERAGE=99.0 ./scripts/bab_gate.sh
# Must pass with 100% TOTAL coverage
```

---

## CONTEXT FOR FUTURE AGENTS

### Architecture
```
strategies/betting_against_beta/
├── beta.py          # Rolling beta estimation (OLS, vectorized)
├── data_loader.py   # CSV/JSON/exchange format normalization
├── portfolio.py     # Equal-weight long/short + risk checks + beta neutrality
├── execution.py     # Order simulation, slippage, fill models
├── signals.py       # Signal generation from beta ranks
├── sizing.py        # Position sizing logic
├── costs.py         # Transaction cost models
├── metrics.py       # Performance attribution
├── backtest.py      # Backtest orchestration
├── config.py        # BABConfig dataclass
├── strategy.py      # BABStrategy main entry point
├── cli.py           # CLI commands (backtest, report, dry-run)
└── *.py             # quality, regime, shorting, reconciliation, data_sources, replay
```

### Key Invariants (DO NOT BREAK)
- **Beta neutrality:** Portfolio beta → 0 via minimum-norm correction
- **Dollar neutrality:** Long weight = |Short weight| per rebalance
- **No lookahead:** All calculations use only data available at t
- **NaN propagation:** Invalid inputs → NaN, never synthetic 0.0
- **Deterministic:** Same seed = same results (hypothesis derandomized)

### Performance Baselines (from `scripts/perf_baseline.py`)
- Full backtest (100 assets, 2 years): <2s
- Beta estimation (1000 assets, 5000 obs): <500ms
- Data loading (100 CSV files): <1s

---

## IF BLOCKED OR INEFFICIENT

### Common Blockers & Resolutions
| Blocker | Resolution |
|---------|------------|
| Gate timeout (>10 min) | Use `BAB_GATE_SERIAL=1` for debugging, `BAB_GATE_JOBS=8` for speed |
| Coverage stuck at 99% | Check `term-missing` output - target exact line numbers |
| Hypothesis flaky | Run with `--hypothesis-show-statistics` - add `@example` for edge cases |
| Data loader test explosion | Consolidate into `test_bab_data_loader_campaign_d_final_push.py` pattern |

### Escalation Path
1. Run `scripts/bab_r4_preflight.py` - validates core invariants
2. Run `scripts/bab_r2_preflight.py` - validates beta parity
3. Check `probe_beta_94_v7.py` for beta numerics debugging
4. If all else fails: `git bisect` on `tests/` directory

---

## COMMANDS FOR NEXT SESSION

```bash
# Quick validation (30s)
BAB_GATE_SERIAL=1 python -m pytest tests/test_bab_beta_deep_final.py -v

# Targeted gap closure (2-3 min each)
BAB_GATE_SERIAL=1 python -m pytest tests/test_bab_data_loader_campaign_d_final_push.py -v --cov=strategies.betting_against_beta.data_loader --cov-report=term-missing
BAB_GATE_SERIAL=1 python -m pytest tests/test_bab_portfolio_coverage_campaign.py -v --cov=strategies.betting_against_beta.portfolio --cov-report=term-missing
BAB_GATE_SERIAL=1 python -m pytest tests/test_bab_beta_deep_coverage.py -v --cov=strategies.betting_against_beta.beta --cov-report=term-missing

# Full gate with higher floor (6 min)
BAB_GATE_SERIAL=1 BAB_GATE_MIN_COVERAGE=99.5 ./scripts/bab_gate.sh

# Final verification (100% target)
BAB_GATE_SERIAL=1 BAB_GATE_MIN_COVERAGE=100 ./scripts/bab_gate.sh
```

---

**HANDOFF COMPLETE** - Next agent MUST achieve 100% coverage. No exceptions. No floor lowering. Heavy working required.