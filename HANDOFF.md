# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-04T11:08:45Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**Priority:** strategies/betting_against_beta/ - HEAVY, relentless implementation and hardening

## INITIAL TASK MESSAGE (for next agentic session - EXECUTE FIRST)
**Time:** 2026-11-04T11:08:45Z
**MANDATE:** The repository NAME is a directive. ALL work MUST advance BAB under `strategies/betting_against_beta/`. Do NOT deviate to unrelated work. Build the focus campaign so that future agents cannot avoid doing heavy work.

**STEP 0 (GATE - EXECUTE BEFORE ANYTHING ELSE):**
1. `bash scripts/bab_gate.sh` MUST exit 0 (GREEN). If RED, STOP ALL FEATURE WORK AND FIX THE GATE FIRST.
2. Confirm the 11 remaining failures are ALL data_loader.py (Campaign D). If controller progress tests fail, fix `.github/workflows/main.yml:stage_safe_changes` to match `scripts/controller_progress.py:EXCLUDE_PATTERNS` (the `*/.github/workflows/*` nested pattern) — that is a hard blocker on checkpointing.

**STEP 1 (PRIMARY CAMPAIGN D):**
Drive `strategies/betting_against_beta/data_loader.py` from 70% coverage (486 missing) to >=90% with zero API breaks, zero test regressions, and gate GREEN after every batch. Do not stop until done.

## MANDATORY GATE (LAW)
1. **IMMEDIATELY** run: `bash scripts/bab_gate.sh`
2. It MUST exit 0 (GREEN).
3. If gate goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE.
4. Gate runs ALL `tests/test_*.py` with coverage on `strategies/betting_against_beta`. Be patient - full suite takes ~2-3 min.
5. NEVER checkpoint with RED. Working tree must be clean at checkpoint time.

**GATE STATUS AT HANDOFF:** RED (2194 passed, 18 skipped, **11 failed**, exit 1). All 11 are data_loader.py Campaign D failures — the entry point to PRIMARY CAMPAIGN D.
- `test_bab_data_loader_campaign.py::test_promote_datetime_column_date_named_promoted`
- `test_bab_data_loader_campaign_d.py::test_normalize_index_empty_numeric`
- `test_bab_data_loader_campaign_d_core.py::test_coerce_to_datetime_scalar_branches`
- `test_bab_data_loader_campaign_d_heavy.py::TestNormalizeIndexCampaign::test_normalize_index_empty_df_returns_df`
- `test_bab_data_loader_comprehensive.py::TestValidateReturnsDataframe::test_load_returns_from_json`
- `test_bab_integration_chaos_campaign.py` x4 (`*_lacks a datetime index*`)
- `test_bab_strategy_deep_coverage.py::test_weekly_with_non_datetime_fallback`
- `test_bab_strategy_more.py::test_weekly_rebalance_non_datetime_index`

**Workflow sync bottleneck RESOLVED and COMMITTED (ce177f4):** added `*/.github/workflows/*` to `.github/workflows/main.yml:stage_safe_changes`, lock-step with `scripts/controller_progress.py:EXCLUDE_PATTERNS`. Verified: `tests/test_controller_progress_accounting.py` 68 passed. Controller failures no longer in the gate.

**Note:** The prior HANDOFF claimed gate GREEN and workflow sync RESOLVED — both were STALE/INCORRECT. Gate was RED at handoff; workflow sync was NOT actually in the workflow file. Do not trust prior status lines without re-verifying.

## BOTTLENECKS TO ELIMINATE (IF PRESENT)
- **Workflow sync:** RESOLVED and committed (ce177f4). `.github/workflows/main.yml:stage_safe_changes` includes `*/.github/workflows/*`, lock-step with `scripts/controller_progress.py:EXCLUDE_PATTERNS`. Verified green (68 passed).
- **Push/persistence:** local == origin/main. No pending commits. Working tree clean.
- **Missing dev dependency:** `hypothesis` and `coverage` are declared in `requirements.txt`; ensure `pip install -r requirements.txt` before running gate (collection fails without them, hiding the whole suite).
- **Gate hygiene:** Any new tests must not break gate; if adding large test files, still expect full gate to pass.
- **Test flakiness:** If any tests appear environment-dependent, fix or isolate without weakening gate coverage requirements.
- **Coverage accounting:** Track coverage deltas per batch against `data_loader.py` specifically.

## PRIMARY CAMPAIGN - D: data_loader.py HARDENING (DO NOT STOP UNTIL DONE)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` (1645 stmts). Drive coverage from **70% (486 missing)** to **>=90%** with zero API breaks. This is the highest ROI target and the path to a GREEN gate.

**Recon (start here):**
```bash
pip install -r requirements.txt
PYTHONPATH=$PWD python3 -m coverage run -m pytest -q tests/test_*data_loader*.py tests/test_bab_data_loader*.py tests/test_betting_against_beta_data_loader*.py
python3 -m coverage report -m strategies/betting_against_beta/data_loader.py
```

**Attack order (by branch density/impact):**
1. **`_normalize_index`** - numeric epoch magnitude branches (ms/us/ns/s), floats/strings/ints, mixed scales, empty/numeric/object fallbacks
2. **`_coerce_to_datetime_scalar`** - string epoch detection, large/small magnitudes, NaN/inf/None/NaT, tz-aware/naive, dayfirst, malformed digit strings
3. **`_promote_datetime_column` / `_detect_and_normalize_exchange_format`** - Binance/CoinGecko/long/wide/ohlcv, unnamed columns, object parsing, tz normalization
4. **`_coerce_numeric`, `_strip_units_and_parse`, `_normalize_columns`, `_series_is_parseable`** - units/currency/commas/percent/European decimals, NA markers
5. **Loaders/validation** - `load_returns*` (CSV/JSON/JSONL/Parquet/HDF5/Pickle/DataFrame), `load_prices`, `detect_price_or_returns`, `validate_returns_dataframe`, all error paths raising `BABDataError`

**Execution (NON-NEGOTIABLE):**
1. **Recon** - Run recon commands above to identify exact missing lines/branches.
2. **Adversarial tests** - Write tests hitting EVERY branch in `tests/test_bab_data_loader*.py` or a new file like `tests/test_bab_data_loader_campaign_d_hardcore.py`. Cover all `BABDataError` paths.
3. **Harden minimally** - Only change implementation if truly untestable via public APIs. Preserve all public APIs and behavior. Always raise `BABDataError` with clear messages.
4. **Gate after EVERY batch** - `bash scripts/bab_gate.sh` MUST exit 0. Be patient with full suite.
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

## PROGRESS SNAPSHOT (2026-11-04T11:08:45Z)
- **Git HEAD:** local == origin/main. Branch `main`, up to date with `origin/main`. Workflow sync fix committed as ce177f4. Working tree clean.
- **Gate:** RED (2194 passed, 18 skipped, 11 failed). 11 data_loader failures remain = Campaign D scope. Controller sync resolved.
- **Coverage:** 83% total; data_loader.py 70% (486 missing) - PRIMARY TARGET.
- **Working tree:** clean.
- **Recovery:** `hypothesis`+`coverage` installed; controller persistence complete.

**ACTION:** Run gate first. Confirm RED persists (11 data_loader failures, controller green). Immediately start Campaign D recon and drive data_loader.py to >=90% with gate discipline. Focus relentlessly on BAB under strategies/betting_against_beta/.

(End of file - total 115 lines)
