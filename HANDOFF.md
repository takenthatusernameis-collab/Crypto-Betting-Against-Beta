# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-03T10:02:57Z | **Repo priority:** Crypto Betting Against Beta (BAB). ALL work must advance BAB under `strategies/betting_against_beta/`. Nothing else takes precedence. Repo name DEMANDS heavy implementation work on BAB - do not deviate.

**MANDATORY GATE:** Run `bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED, FIX IT BEFORE DOING ANYTHING ELSE. Gate runs ALL `tests/test_*.py` with coverage on `strategies/betting_against_beta/`. Full suite is large - be patient.

## IMMEDIATE BOTTLENECKS TO CLEAR (if any block progress)
1. **Test/runtime environment** - Ensure deps available (pandas, numpy, scipy, pytest, coverage). If missing, install minimally without changing repo config.
2. **Any RED tests** - Fix failures first, do not add features until GREEN.
3. **Import/syntax errors** - Fix immediately.

## CURRENT FOCUS CAMPAIGN (MAXIMUM AGGRESSION - HEAVY WORK REQUIRED)

### Campaign D - Data loader & quality (HIGHEST PRIORITY - BIGGEST UNHARDENED SURFACE)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` and `quality.py` against every adversarial case.
**Targets (attack systematically):**
1. `_normalize_index` - numeric epochs (s/ms/us/ns), mixed tz, NaT, duplicates, elementwise coercion, all fallbacks (lines ~102-261). Find gaps.
2. `_coerce_to_datetime_scalar` - all epoch magnitudes, strings, floats, NaN/inf, bad formats, timezone naive/aware.
3. `_detect_and_normalize_exchange_format` - long/wide/OHLCV, date column detection, pivot paths, column promotion, guard logic.
4. `load_returns_from_*` - CSV/JSON/JSONL/Parquet/HDF5/Pickle. All orients, encodings, dtypes, empty/malformed.
5. `_run_data_quality_campaign`, filling/imputation paths, min-finite-fraction, stale-run branches.
6. Add defensive guards everywhere. Make errors via `BABDataError` with clean messages.

### Campaign C - CLI/reporting (SECOND PRIORITY)
**Objective:** Make CLI and reporting bulletproof.
**Targets:**
1. `strategies/betting_against_beta/cli.py` - adversarial args, `--dry-run`, `--output` path safety, JSON strictness, all data loading combos.
2. `scripts/bab_backtest_report.py` - aliases, directory rejection, strict JSON, NaN/inf handling, error paths.

### Campaign B - Strategy/backtest/core (THIRD - MAINTAIN VIGILANCE)
**Objective:** Lookahead safety, finiteness, numerical stability. Audit divisions/log/sqrt/extreme values.

## EXECUTION PLAN (NON-NEGOTIABLE ORDER)
1. **Gate first:** `bash scripts/bab_gate.sh` → must be GREEN. If not, diagnose and fix before proceeding.
2. **Attack Campaign D aggressively:** Read data_loader.py thoroughly. Run data loader tests, find untested branches. Harden without changing public APIs.
3. **Attack Campaign C:** Harden CLI/reporting.
4. **Gate after EVERY meaningful change:** Run gate frequently. NEVER checkpoint with RED gate.
5. **Heavy implementation:** Add guards, validation, edge case handling. This repo demands substantial hardening work.
6. **Update handoff if stopping:** If you must stop, update THIS file with exact progress, files modified, failing cases, next concrete steps (file:line), gate status.

## INVARIANTS (NEVER VIOLATE)
- **Repo priority:** Crypto Betting Against Beta. `strategies/betting_against_beta/` + tests FIRST.
- **Gate is law:** `bash scripts/bab_gate.sh` must exit 0 before ending session/checkpoint.
- **Full coverage:** Gate runs ALL `test_*.py` under `tests/`.
- **Lookahead forbidden:** Weights must be lagged by 1 day.
- **Finiteness required:** Handle NaN/inf explicitly.
- **No workflow changes** unless absolutely necessary to fix blocking gate issue.
- **Preserve API compatibility.**
- **Heavy work mandatory** given repo name.

## PROGRESS SNAPSHOT (2026-11-03T10:02:57Z)
- Handoff refreshed with explicit aggressive campaign focused on data_loader hardening (biggest surface). Previous bottlenecks fixed per history. Gate status unknown at write time - MUST verify first.
