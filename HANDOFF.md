# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T07:32:01Z
**Repo priority (non-negotiable):** `strategies/betting_against_beta/` only. This repo is Betting Against Beta (crypto); every action must increase BAB correctness, robustness, or coverage while keeping the full gate GREEN. No sidetracks, no infra detours, no history rewrites.

## Current state (verified)
- **Branch:** `main`, clean working tree, up to date with `origin/main`.
- **Gate:** `bash scripts/bab_gate.sh` — **GREEN** (178 test files, 2818 tests passed, exit 0).
- **Latest gate coverage (BAB package):** 87% total.
  - `data_loader.py`: **79%** (1693 stmts, 356 missing) — **PRIMARY BOTTLENECK**
  - `cli.py`: **61%** (318 stmts, 124 missing) — **SECOND BOTTLENECK**
  - `backtest.py`: 80% (109 stmts, 22 missing)
  - `strategy.py`: 89% (297 stmts, 32 missing)
  - `signals.py`: 91%, `beta.py`: 92%, `portfolio.py`: 93%, `sizing.py`: 98%, `costs.py`: 98%, `config.py`/`metrics.py`/`regime.py`: 99%, `attribution.py`/`data.py`/`data_sources.py`/`errors.py`/`quality.py`/`shorting.py`: 100%
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
**File:** `strategies/betting_against_beta/data_loader.py` (356 missing lines per last gate).
**Attack uncovered branches via adversarial/public-API tests first:**
- `_coerce_to_datetime_scalar` / datetime coercion edge cases (tz-aware/naive, mixed types, epoch-like floats/strings, NaT, invalid inputs, `errors`/format handling).
- `_normalize_index`, `_detect_and_normalize_exchange_format`, `_promote_datetime_column`, `_maybe_read_table`.
- All loader paths: `load_csv/load_json/load_jsonl/load_excel/load_parquet/load_pickle/load_hdf/load_returns/load_prices` (path/IO errors, malformed payloads, missing/extra columns, duplicate indices, index-vs-column datetime promotion, non-numeric/inf/NaN handling, benchmark/universe validation).
- `validate_returns_dataframe` and error wrapping to `BABDataError`.
- Use `tmp_path`, `monkeypatch`, minimal fixtures; avoid brittle implementation-coupled tests. Change implementation only if a branch is truly unreachable and the fix is minimal/correct.

**Loop:** add focused tests → run targeted tests → run full `bab_gate.sh` → keep GREEN → repeat until >=90% or only genuinely low-value/unreachable branches remain (document why).

### Campaign 2 (after Campaign 1 materially advances) — `cli.py` → target >= 85%
**File:** `strategies/betting_against_beta/cli.py` (124 missing).
Cover argparse/dispatch paths and validation/errors: `--data`, `--benchmark`, `--universe`, `--beta-window`, `--long-quantile`, `--short-quantile`, `--rebalance-freq`, `--transaction-costs`, `--slippage`, `--output`, `--synthetic`, `--from-prices`, `--dry-run`, `--version`, bad combos, missing files, exit codes, dry-run no-side-effects behavior. Use `capsys`/`monkeypatch`/`tmp_path`; test via public CLI entrypoints.

### Campaign 3 (harden core engines)
`backtest.py`, `strategy.py`, `beta.py`, `signals.py`, `portfolio.py`, `sizing.py`, `shorting.py`: close remaining high-value branches; add invariant/property tests for lag/no-lookahead, neutrality, NaN propagation, cost/slippage semantics where useful.

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
