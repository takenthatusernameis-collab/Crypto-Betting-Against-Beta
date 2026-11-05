# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T07:42:33Z
**Repo priority (non-negotiable):** `strategies/betting_against_beta/` only. This repo is Betting Against Beta (crypto); every action must increase BAB correctness, robustness, or coverage while keeping the full gate GREEN. No sidetracks, no infra detours, no history rewrites.

## Current state (verified)
- **Branch:** `main`, clean working tree, up to date with `origin/main`.
- **Gate:** `bash scripts/bab_gate.sh` — **GREEN** (2818 tests passed, exit 0; after fixing workflow sync for controller tests).
- **Latest gate coverage (BAB package):** 87% total.
  - `data_loader.py`: **78-79%** (1693 stmts, ~356-364 missing) — **PRIMARY BOTTLENECK**
  - `cli.py`: **61%** (318 stmts, 124 missing) — **SECOND BOTTLENECK**
  - `backtest.py`: 80% (109 stmts, 22 missing)
  - `strategy.py`: 89% (297 stmts, 32 missing)
  - `beta.py`: 92% (320 stmts, 25 missing)
  - `signals.py`: 91%, `portfolio.py`: 93%, `sizing.py`: 98%, `costs.py`: 98%, others >=99%/100%
- **No blocking artifacts found** (`research_state/` contains only `workflow_run_diagnostics.jsonl`; no lock/stale/blocker files).

## Invariants (sacred — never violate)
- Weights lagged by 1 day (no lookahead).
- NaN/inf/NaT handled explicitly; no silent coercion that hides data errors.
- Raise `BABDataError` on parse/validation failures where the API contract requires it.
- Dollar-neutral by default; liquidity/transaction-cost/slippage semantics enforced.
- Public APIs stable unless a minimal, correct fix is required for an unreachable-by-public-API branch.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (EXECUTE IMMEDIATELY)

**You are continuing BAB hardening. Do heavy, unrelenting work. Do not explore unrelated code. Do not stop at “good enough.” Remove bottlenecks.**

### Step 0 — Recon (mandatory, before any edit)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
bash scripts/bab_gate.sh 2>&1 | tail -12
```
If **RED**: diagnose and fix root cause immediately. Gate must be **GREEN** after every change batch.

### Campaign 1 (immediate) — `data_loader.py` → target >= 90%
**File:** `strategies/betting_against_beta/data_loader.py` (356+ missing lines). Prioritize high-value uncovered paths by actual execution:
- `_coerce_to_datetime_scalar`: edge cases (tz-aware/naive, epoch magnitudes ns/us/ms/s, floats/strings, NaT/None/inf/nan, dayfirst, ISO/Z/offsets) - add tests using public APIs where possible.
- `_normalize_index`, `_detect_and_normalize_exchange_format`, `_promote_datetime_column`, `_maybe_read_table` and loader dispatch (`load_csv/json/jsonl/excel/parquet/pickle/hdf/load_returns/load_prices`).
- Long/wide format detection (Binance/CoinGecko style), symbol+date+price pivots, index-vs-column promotion.
- `validate_returns_dataframe`, normalization/coercion edge cases, metadata column drops, all-NaN/all-NaT rejection paths.
- Error wrapping to `BABDataError`. Use `tmp_path`/`monkeypatch`, minimal fixtures. Change implementation only if truly unreachable by public API and fix is minimal/correct.

**Loop:** add focused tests → run targeted tests → `bash scripts/bab_gate.sh` → keep GREEN → repeat until >=90% or only genuinely low-value/unreachable branches remain (document rationale).

### Campaign 2 (after Campaign 1 advances) — `cli.py` → target >= 85%
**File:** `strategies/betting_against_beta/cli.py` (124 missing). Cover argparse paths, `--dry-run` (no side effects), validation/errors, output/exit codes, all flags.

### Campaign 3 (harden core engines)
Close remaining high-value branches in `backtest.py`, `strategy.py`, `beta.py`, `signals.py`, `portfolio.py`, `sizing.py`, `shorting.py`. Add invariant/property tests for lag/no-lookahead, neutrality, NaN propagation, costs/slippage.

## Binding execution rules
1. **Recon first.** Never edit blind.
2. **Test-first for coverage gaps;** minimal impl changes only when necessary.
3. **Gate after every batch.** Never leave/commit RED.
4. **BAB-only focus.** Prioritize strictly by repo name.
5. **Zero regressions.** Preserve all passing tests and invariants.
6. **No history rewriting / no force-push.**
7. **Update this HANDOFF** if you make material progress (new coverage/gate numbers, next concrete targets, blockers removed). Keep it the single durable source of truth.

## Suggested immediate command sequence
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH PYTHONPATH=$PWD
bash scripts/bab_gate.sh 2>&1 | tail -12
python -m coverage report --include='strategies/betting_against_beta/data_loader.py' -m | tail -40
# then add targeted tests for highest-value missing branches in data_loader.py, rerun gate
```

**Start now at Campaign 1. Build momentum. Close the BAB bottlenecks.**
