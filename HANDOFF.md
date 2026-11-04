# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-04T06:47:25Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**Priority:** strategies/betting_against_beta/ - HEAVY, relentless implementation and hardening

## INITIAL TASK MESSAGE (for next agentic session - EXECUTE FIRST)
**Time:** 2026-11-04T06:47:25Z
**MANDATE:** The repository NAME is a directive. ALL work MUST advance BAB under `strategies/betting_against_beta/`. Do NOT deviate to unrelated work. Build the focus campaign so that future agents cannot avoid doing heavy work.

### MANDATORY GATE (LAW)
1. **IMMEDIATELY** run: `bash scripts/bab_gate.sh`
2. It MUST exit 0 (GREEN).
3. If gate goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE.
4. Gate runs ALL `tests/test_*.py` with coverage on `strategies/betting_against_beta/`. Be patient - full suite takes time.
5. NEVER checkpoint with RED. Working tree must be clean at checkpoint time.

**GATE STATUS AT HANDOFF:** GREEN (2234 passed, 20 skipped, exit 0). Gate bottleneck RESOLVED this session: `.github/workflows/main.yml:stage_safe_changes` was missing the `*/.github/workflows/*` nested pattern; added it to match `scripts/controller_progress.py:EXCLUDE_PATTERNS`. The two lists are now in lock-step. Gate is GREEN.

### BOTTLENECKS TO ELIMINATE (IF PRESENT)
- **Workflow sync:** RESOLVED. Both `scripts/controller_progress.py` EXCLUDE_PATTERNS and `.github/workflows/main.yml:stage_safe_changes` now include `*/.github/workflows/*`. Gate GREEN.
- **Push/persistence:** GitHub App token cannot push workflow file changes. When checkpointing, ensure only non-workflow changes or handle workflow changes separately. The controller retries persistence; do not claim persistence until remote SHA matches.
- **Gate hygiene:** Any new tests must not break gate; if adding large test files, still expect full gate to pass.
- **Test flakiness:** If any tests appear environment-dependent, fix or isolate without weakening gate coverage requirements.
- **Coverage accounting:** Track coverage deltas per batch against data_loader.py specifically.

### PRIMARY CAMPAIGN - D: data_loader.py HARDENING (DO NOT STOP UNTIL DONE)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` (1522 stmts). Drive coverage from **74% (402 missing)** to **>=90%** with zero API breaks. This is the highest ROI target.

**Recon (start here):**
```bash
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

### QUEUED (AFTER CAMPAIGN D >=90% GREEN)
- **CAMPAIGN C:** CLI/reporting (`cli.py`, `scripts/bab_backtest_report.py`) if gaps emerge
- **CAMPAIGN B:** Core/backtest/strategy only on regressions

### INVARIANTS
- BAB under `strategies/betting_against_beta/` FIRST
- `bash scripts/bab_gate.sh` must exit 0 before ending/checkpoint
- Full suite via gate (all tests)
- Weights lagged by 1 day (no lookahead)
- Handle NaN/inf explicitly
- No breaking API changes
- Heavy hardening required - no shortcuts
- Raise `BABDataError` on bad/parse failures

### PROGRESS SNAPSHOT (2026-11-04T06:47:25Z)
- **Git HEAD:** local ahead of origin/main (workflow file changes cannot be pushed by GitHub App; controller will retry persistence).
- **Gate:** GREEN (2234 passed, 20 skipped, exit 0). Verified this session.
- **Coverage:** 85% total; data_loader.py 74% (402 missing) - PRIMARY TARGET
- **Working tree:** clean (after workflow fix)
- **Recovery:** Recovery bundles/patches saved. Controller will retry persistence of local-ahead commits after this session; do not claim persistence until remote SHA matches.

**ACTION:** Run gate first. If GREEN, immediately start Campaign D recon and drive data_loader.py to >=90% with gate discipline. Focus relentlessly on BAB under strategies/betting_against_beta/.

(End of file - total 71 lines)