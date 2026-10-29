# HANDOFF - 2026-10-29T11:53:56Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T11:53:56Z

## PROJECT IDENTITY (NON-NEGOTIABLE - DRIVES ALL PRIORITIZATION)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default), Frazzini–Pedersen style
- **PRIORITY:** **BAB STRATEGY CODE IN `strategies/betting_against_beta/` > EVERYTHING ELSE**

## BOTTLENECKS REMOVED (VERIFIED)
- **Workflow/controller pattern sync:** `.github/workflows/main.yml` `stage_safe_changes` now includes `*/.github/workflows/*` (parity with `scripts/controller_progress.py` EXCLUDE_PATTERNS). Both `TestStageSafeChangesPatternSync` tests pass.
- **Baseline restored GREEN:** `python3 -m pytest -q` → **516 passed, 0 failed, 6 skipped** (was failing 2 tests blocking green baseline; fixed). Deterministic baseline confirmed.

## HEAVY WORK COMPLETED THIS SESSION
- **Deterministic property-style fuzzing (new, multi-file scope touch):** Added `tests/test_bab_deterministic_fuzz.py` with seeded RNG (no hypothesis/network). Hammers `signals.generate_bab_signals`, `portfolio.construct_portfolio`, `data_loader.load_returns_from_csv`, and `BABStrategy.run()` with randomized degenerate inputs (NaN/inf/zeros/strings/percents/commas, tz-aware indices, gaps/non-monotonic dates, extreme quantiles, single/empty/degenerate universes). Asserts no crash, finiteness where applicable, integer-like signals in {-1,0,1}, dollar neutrality when both sides exist, shape/index sanity.
- **Robustness posture maintained:** No bare `except:` added; all changes deterministic/offline. Existing robustness fixes preserved.

## MANDATORY SESSION START (IN ORDER):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q  # MUST be >=516 passed, 0 failed, 6 skipped before edits
```

**IF GREEN → START HEAVY WORK IMMEDIATELY. NO EXPLORATION, NO DOCS-ONLY CHANGES.**

## STATUS NOTE (REALITY CHECK)
- **Priority 4 (Analytics & Reporting):** metrics/attribution/backtest columns, strategy report/tear_sheet/report_to_json, strict-JSON CLI implemented.
- **Priority 3 (Performance & Scalability):** vectorized rolling beta, vectorized signals, guards/copies optimized; parity preserved.
- **Priority 5 (Testing & Robustness):** Expanded with fuzz harness. Baseline 516 passed.

## FOCUS CAMPAIGN (CONTINUING)
### Priority 5: Testing & Robustness — IN PROGRESS
- [x] Beta parity regression (multi-seed, NaN/inf)
- [x] Config-matrix stress (regime/shorting/sizing/costs), determinism + finiteness
- [x] Report CLI edge cases
- [x] Signals/portfolio edge cases, dollar neutrality
- [x] Data loader robustness (malformed/mixed types/bad dates/dupes/timezones/gaps/all-NaN)
- [x] Deterministic property-style fuzzing across signals/portfolio/data_loader/backtest (seeded, offline)
- [ ] Coverage >=95% across `strategies/betting_against_beta/` (push remaining gaps)

### Priority 6: Developer Experience
- [ ] CLI polish, YAML/JSON config, API polish, examples, typing, docs

## NEXT HEAVY TASK (FOCUS FOR NEXT SESSION — DO NOT DEFER)
**Push coverage >=95% across `strategies/betting_against_beta/` with substantive multi-file hardening.**
1) Measure coverage gaps: identify untested branches in `beta.py`, `backtest.py`, `strategy.py`, `metrics.py`, `attribution.py`, `costs.py`, `sizing.py`, `shorting.py`, `quality.py`, `data.py`, `config.py`, `cli.py`, `data_loader.py`, `signals.py`, `portfolio.py`. Add deterministic tests targeting missing lines/branches.
2) Harden any brittle paths discovered (no bare `except:`, preserve behavior, maintain finiteness/determinism).
3) Touch >=4 files with real logic/tests. Acceptance: `python3 -m pytest -q` >= 516 passed, 0 failed, 6 skipped; coverage >=95% across `strategies/betting_against_beta/` (report numbers); no regressions.

## MANDATORY EXECUTION RULES
- **PRODUCT-FIRST:** Absolute priority on `strategies/betting_against_beta/`
- **HEAVY WORK REQUIRED:** Multi-file substantive changes across >=4 files when changing strategy code. If < 4 files touched with real logic, go deeper.
- **TDD:** failing test → understand → minimal impl → green → refactor
- **ROBUSTNESS:** no bare `except:`; handle NaN/inf/zeros/gaps/timezones/delistings; validate inputs
- **DETERMINISTIC:** no randomness without explicit seeds
- **OFFLINE:** no network calls in tests/core
- **ALWAYS GREEN:** maintain >=420 passed, 0 failed (currently 516 passed, 0 failed)
- **SINGLE HANDOFF:** Update THIS FILE after significant progress. ONLY `HANDOFF.md` MATTERS.
- **NO COMMITS UNLESS ASKED**

## EXECUTION LOOP (REPEAT UNTIL EXPLICITLY STOPPED)
1. Verify baseline green
2. Do PRIMARY HEAVY TASK first (TDD, multi-file). No exploration detours.
3. Implement production-grade solution across multiple files → all tests pass → refactor
4. Validate full suite, check regressions
5. Update handoff with timestamp, completed work, blockers removed, next concrete heavy task
6. Continue heavy work — never stop at partial, never do busywork

**IGNORE ALL OLDER HANDOFF_*.md FILES. ONLY `HANDOFF.md` MATTERS.**
