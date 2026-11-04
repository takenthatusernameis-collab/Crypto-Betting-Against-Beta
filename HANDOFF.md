# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-04T17:33:03Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**Priority:** strategies/betting_against_beta/ - HEAVY, relentless implementation and hardening

## INITIAL TASK MESSAGE (for next agentic session - EXECUTE FIRST)
**Time:** 2026-11-04T17:33:03Z
**MANDATE:** The repository NAME is a directive. ALL work MUST advance BAB under `strategies/betting_against_beta/`. Do NOT deviate to unrelated work. Build the focus campaign so that future agents cannot avoid doing heavy work.

**STEP 0 (GATE - EXECUTE BEFORE ANYTHING ELSE):**
1. `bash scripts/bab_gate.sh` MUST exit 0 (GREEN). If RED, STOP ALL FEATURE WORK AND FIX THE GATE FIRST.
2. Confirm gate is clean. Do not trust old handoff status - verify.

**STEP 1 (PRIMARY CAMPAIGN D - HEAVY):**
Drive `strategies/betting_against_beta/data_loader.py` from **74%** to **>=90%** with zero API breaks, zero test regressions, and gate GREEN after every batch. Do not stop until done. This is the path to eliminating remaining coverage gaps.

## MANDATORY GATE (LAW)
1. **IMMEDIATELY** run: `bash scripts/bab_gate.sh`
2. It MUST exit 0 (GREEN).
3. If gate goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE.
4. Gate runs ALL `tests/test_*.py` with coverage on `strategies/betting_against_beta`. Be patient - full suite takes ~2-3 min.
5. NEVER checkpoint with RED. Working tree must be clean at checkpoint time.

## GATE STATUS AT HANDOFF:** GREEN (2207 passed, 18 skipped). Verified at 2026-11-04T17:33Z.

## BOTTLENECKS TO ELIMINATE (IF PRESENT)
- **Workflow sync:** FIXED AND VERIFIED. `*/.github/workflows/*` was missing from `.github/workflows/main.yml` bash `stage_safe_changes` list (line 1163), causing `tests/test_controller_progress_accounting.py` to fail. Added the pattern to the bash case list. Gate now GREEN.
- **Push/persistence:** local == origin/main. No pending commits. Working tree clean (this fix is staged in HANDOFF.md only - commit before checkpoint).
- **Missing dev dependency:** `hypothesis` and `coverage` are declared in `requirements.txt`; ensure installed.
- **Gate hygiene:** Any new tests must not break gate.
- **Coverage accounting:** Track coverage deltas per batch against `data_loader.py` specifically.

## PRIMARY CAMPAIGN - D: data_loader.py HARDENING (DO NOT STOP UNTIL >=90%)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` (1669 stmts). Drive coverage from **74% (431 missing)** to **>=90%** with zero API breaks. Heavy work required.

**Recon (start here):**
```bash
pip install -r requirements.txt
PYTHONPATH=$PWD python3 -m coverage run -m pytest -q tests/test_*data_loader*.py tests/test_bab_data_loader*.py
PYTHONPATH=$PWD python3 -m coverage report -m strategies/betting_against_beta/data_loader.py
```

**Attack order (by branch density/impact):**
1. **`_normalize_index`** - numeric epoch magnitude branches (ns/us/ms/s), floats/strings/ints, mixed scales, empty/numeric/object fallbacks, all-NA coercion paths
2. **`_coerce_to_datetime_scalar`** - string epoch detection, large/small magnitudes, NaN/inf/None/NaT, tz-aware/naive, dayfirst, malformed digit strings
3. **`_promote_datetime_column` / `_detect_and_normalize_exchange_format`** - long/wide/ohlcv formats, CoinGecko/Binance variants, unnamed columns, tz normalization, pivot paths
4. **`_coerce_numeric`, `_strip_units_and_parse`, `_normalize_columns`, `_series_is_parseable`, `_drop_all_nan_columns`** - units/currency/commas/percent/European decimals, NA markers, duplicate detection
5. **Loaders/validation** - `load_returns*` all formats (CSV/JSON/JSONL/Parquet/HDF5/Pickle/DataFrame), `load_prices`, `detect_price_or_returns`, `validate_returns_dataframe` all error paths raising `BABDataError`; also `normalize_schema`, quality campaign branches
6. **Helper paths** - `_drop_metadata_columns`, `_prices_to_returns`, tz conversions, error messages

**Execution (NON-NEGOTIABLE):**
1. **Recon** - Run recon commands above to identify exact missing lines/branches.
2. **Adversarial tests** - Write tests hitting EVERY branch in `tests/test_bab_data_loader*.py` or new targeted files. Cover all `BABDataError` paths. Tests must be comprehensive and heavy.
3. **Harden minimally** - Only change implementation if truly untestable via public APIs. Preserve all public APIs and behavior. Always raise `BABDataError` with clear messages.
4. **Gate after EVERY batch** - `bash scripts/bab_gate.sh` MUST exit 0. Be patient with full suite (~2-3 min).
5. **Converge** - Do NOT move to other campaigns until `data_loader.py >= 90%` AND gate is GREEN.

## QUEUED (AFTER CAMPAIGN D >=90% GREEN)
- **CAMPAIGN C:** CLI/reporting (`cli.py`, `scripts/bab_backtest_report.py`) if gaps emerge
- **CAMPAIGN B:** Core/backtest/strategy only on regressions

## INVARIANTS
- BAB under `strategies/betting_against_beta/` FIRST
- `bash scripts/bab_gate.sh` must exit 0 before ending/checkpoint
- Full suite via gate (all tests)
- Weights lagged by 1 day (no lookahead)
- Handle NaN/inf explicitly
- No breaking API changes
- Heavy hardening required - no shortcuts
- Raise `BABDataError` on bad/parse failures

## PROGRESS SNAPSHOT (2026-11-04T17:33:03Z)
- **Git HEAD:** local == origin/main. Branch `main`, up to date with `origin/main`.
- **Gate:** GREEN (2207 passed, 18 skipped). Verified at 17:33Z after workflow-sync fix.
- **Coverage:** 85% total; data_loader.py **74% (431 missing)** - PRIMARY TARGET (need >=90%).
- **Working tree:** clean except HANDOFF.md update (workflow sync fix in `.github/workflows/main.yml` line 1163).

**ACTION:** Run gate first (confirm GREEN). Immediately start Campaign D recon and drive data_loader.py to >=90% with relentless gate discipline. Do heavy work - cover every missed branch.
