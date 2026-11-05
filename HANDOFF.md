# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T08:40:04Z
**Repo:** `Crypto-Betting-Against-Beta` — **BAB-only focus (non-negotiable).** Every action must increase `strategies/betting_against_beta/` correctness, robustness, adversarial handling, or coverage while keeping the gate GREEN. No sidetracks, no infra/controller detours, no history rewrites. Repo name = BAB strategy; prioritize by repo name.

## Verified state (this session)
- **Branch:** `main`, **working tree dirty** — one uncommitted bottleneck fix: `.github/workflows/main.yml` `stage_safe_changes` case list now includes `*/.github/workflows/*` to match Python `EXCLUDE_PATTERNS` in `scripts/controller_progress.py`. **COMMIT THIS WHEN AUTHORIZED** so the tree is clean and the gate stays green. Do not leave it lingering.
- **Gate:** **GREEN** — `bash scripts/bab_gate.sh` → EXIT=0, **2858 passed, 0 failed** (~4:14). The 2 RED controller tests (`test_controller_progress_accounting.py::TestStageSafeChangesPatternSync`) that failed last session are now fixed by the workflow pattern addition. Re-run after every meaningful batch: `export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH PYTHONPATH=$PWD && bash scripts/bab_gate.sh 2>&1 | tail -15` (allow up to 10 min).
- **Test inventory:** 2858 tests collected under `tests/`.
- **BAB package coverage (full gate run, 4418 stmts, 87%):**
  - `data_loader.py`: **79%** (1693 stmts, **352 missing**) — **PRIMARY BOTTLENECK**
  - `cli.py`: **61%** (318 stmts, **124 missing**) — **SECOND BOTTLENECK**
  - `backtest.py`: 80% (22 missing), `strategy.py`: 89% (32), `beta.py`: 92% (25), `signals.py`: 91% (11), `portfolio.py`: 93% (16), `sizing.py`: 98% (3)
  - `quality.py`/`shorting.py`/`data_sources.py`/`data.py`/`errors.py`/`attribution.py`: 100%; others >=98%
- **BAB-scope smoke:** `tests/test_bab_*.py` → all pass (0 failed).

## Bottlenecks removed this session
- Gate was RED (2 controller failures) because the workflow `stage_safe_changes` case list lacked the nested `*/.github/workflows/*` pattern that Python `EXCLUDE_PATTERNS` requires. Fixed in `.github/workflows/main.yml:1163`. Gate now GREEN. Remaining: commit the fix (authorized pending).

## Invariants (sacred)
- Weights lagged by 1 day (no lookahead).
- NaN/inf/NaT handled explicitly; never silently hide bad data.
- Raise `BABDataError` on parse/validation failures where contract requires it.
- Dollar-neutral by default; liquidity/transaction-cost/slippage semantics enforced.
- Keep public APIs stable; minimal implementation fixes only for branches unreachable by public API and demonstrably correct.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (MANDATORY, HEAVY WORK)

**You are continuing BAB hardening. Build momentum immediately. Remove bottlenecks. Do not explore unrelated code. Do not stop at partial progress.** Repo name is `Crypto-Betting-Against-Beta`, so BAB is the only priority.

### 0) Gate recon (do first — never edit blind)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH PYTHONPATH=$PWD
bash scripts/bab_gate.sh 2>&1 | tail -20
```
If **RED**: diagnose root cause and fix before anything else. The gate is GREEN only when this exits 0. (One uncommitted workflow fix in `.github/workflows/main.yml` is pending commit — commit it when authorized so the tree is clean.)

### 1) Campaign A — `strategies/betting_against_beta/data_loader.py` → target >= 90% (352 missing)
Inspect actual missing lines (gate coverage `-m` output), then hit highest-value branches via public loader APIs (`load_returns`, `load_prices`, `load_csv/json/jsonl/excel/parquet/pickle/hdf`, `validate_returns_dataframe`, coercion/normalization helpers):
- `_coerce_to_datetime_scalar` / datetime normalization: tz-aware/naive, epoch ns/us/ms/s, floats/strings, NaT/None/inf/nan, dayfirst, ISO/Z/offsets, ambiguous/invalid inputs.
- `_normalize_index`, index-vs-column datetime promotion, metadata column detection/drops.
- Exchange/long/wide format detection (Binance/CoinGecko-style), symbol+date(+price/return) pivots, duplicate handling.
- `_maybe_read_table`/dispatch/extension routing and parser error wrapping to `BABDataError`.
- `validate_returns_dataframe`: benchmark requirements, all-NaN/all-NaT, non-numeric coercion, insufficient columns/rows, object/string junk.
- Use `tmp_path`, `monkeypatch`, minimal fixtures; prefer tests over impl changes. If a branch is unreachable by public API, document why and make the smallest correct change only if justified.

**Work loop:** add focused tests → run targeted module tests → `bash scripts/bab_gate.sh` → keep GREEN → repeat.

Targeted coverage check:
```bash
python3 -m coverage run -m pytest tests/test_bab_data_loader*.py tests/test_betting_against_beta_data_loader*.py -q
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py' -m | tail -60
```
(Adjust selected tests to stay fast but representative; gate remains the final authority.)

### 2) Campaign B — `strategies/betting_against_beta/cli.py` → target >= 85% (124 missing)
Cover argparse flags/combos, `--dry-run` (must not execute backtest/side effects), `--from-prices`/`--synthetic`/`--data` validation, `--universe` parsing, output paths, exit codes/errors, `--version`.

### 3) Campaign C — harden core engines
Close high-value branches in `backtest.py` (22), `strategy.py` (32), `beta.py` (25), `signals.py` (11), `portfolio.py` (16), `sizing.py` (3). Add invariant/property tests: 1-day lag/no-lookahead, dollar neutrality, NaN/inf propagation, costs/slippage, benchmark edge cases.

### Binding rules
1. Recon first; never edit blind.
2. Gate after every meaningful batch; never commit/push RED.
3. BAB-only; prioritize by repo name.
4. Test-first for gaps; minimal correct impl changes only when necessary.
5. Zero regressions; preserve invariants and public API behavior.
6. No force-push/history rewrite.
7. **Update this HANDOFF** with new gate status, coverage numbers, completed targets, and the next concrete command/bottleneck. Keep it the single durable source of truth.

## Suggested immediate command
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta && export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH PYTHONPATH=$PWD && bash scripts/bab_gate.sh 2>&1 | tail -12; python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' -m 2>&1 | tail -40
```

**Start now at Campaign A. Close BAB data_loader bottlenecks with heavy, verifiable work.**
