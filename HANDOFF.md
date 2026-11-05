# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T09:23:35Z
**Repo:** `Crypto-Betting-Against-Beta` — **BAB-only focus (non-negotiable).** Every action must increase `strategies/betting_against_beta/` correctness, robustness, adversarial handling, or coverage while keeping the gate GREEN. No sidetracks. Repo name = BAB strategy; prioritize by repo name.

## SAME-RUN RECOVERY (session 39) — persistence failure diagnosed & safely remediated (historical)

- **Context:** Previous worker sessions (37/39 path) ended with **bounded remote checkpoint persistence failed**. This is a **new worker session in the SAME active GitHub Actions run** — do **not** end the workflow. **Controller will retry persistence of all local-ahead commits after this session; do not claim persistence until remote SHA matches.**
- **Preservation (no reset/discard):** All prior local commits preserved via **recovery bundle** `/home/runner/work/_temp/kilo-recovery-41953654776-1.bundle` (**verified OK**, complete history; contains `refs/heads/main=2627694`, `origin/main=847d8d8`) and backup refs **`backup/pre-persistence-fix-20261105` / tag `backup-session39-20261105` → `2627694f95d7587f9cf0b981eda576788ae5b3db`**. No force-push. No history rewrite beyond the local-only pushability fix below (bundled/refs preserved first; rollback = `git reset --hard backup/pre-persistence-fix-20261105`).
- **Root cause (confirmed):** Local history included commit **`8f165a3`** which modified **`.github/workflows/main.yml`**. Push rejected: `refusing to allow a GitHub App to create or update workflow \`.github/workflows/main.yml\` without \`workflows\` permission`. Credential/permission constraint on workflow paths, not transport failure.
- **Safe remedy (materially different, evidence-justified):** (1) verified bundle + backup refs; (2) saved workflow delta as `/home/runner/work/_temp/workflow-stage-safe-sync-8f165a3.patch` for an operator with `workflows` permission to apply later; (3) rebuilt local-ahead tip as **non-workflow, pushable commits** preserving HANDOFF progress; **Net pushable delta vs origin/main is HANDOFF.md only** — controller can persist it.
- **Local HEAD (this session):** `9df2be1 docs(handoff): session 39 same-run recovery — diagnose workflow-push block, preserve bundle/refs, keep gate GREEN`. **`origin/main`:** `9df2be1` (in sync with HEAD). **No pushable commits pending except uncommitted workflow change below.**

## Verified state (this session)

- **Recon:** `git status` shows only ` M .github/workflows/main.yml` (uncommitted, see bottleneck below); `git fetch origin main` OK; `git push --dry-run`/transport usable for non-workflow commits. HEAD == origin/main.
- **Controller tests:** `python3 -m pytest -q tests/test_controller_progress_accounting.py` → **68 passed**.
- **BAB gate:** `bash scripts/bab_gate.sh` → **2858 passed, 0 failed, exit 0, 87% total coverage.** **GREEN.** Next agent **MUST confirm `bash scripts/bab_gate.sh` exit 0 / 0 failures before/alongside new BAB work.**
- **Coverage bottlenecks (last verified baseline):** `data_loader.py` **79% (352 missing, PRIMARY)**, `cli.py` **61% (124 missing, SECONDARY)**, `backtest.py` 80% (22), `strategy.py` 89% (32), `beta.py` 92% (25), `signals.py` 91% (11), `portfolio.py` 93% (16), `sizing.py` 98% (3). Re-measure after gate.

## Bottlenecks (remove to unblock significant progress)

1. **Workflow file cannot be committed/pushed with current token.** `.github/workflows/main.yml` has an uncommitted modification (stage_safe_changes EXCLUDE_PATTERNS sync). Push will be rejected (workflows permission). **Do not commit `.github/workflows/*` with this token.** The delta is backed up at `/home/runner/work/_temp/workflow-stage-safe-sync-8f165a3.patch` — an operator with `workflows` permission must apply it. **This does not block BAB work** (BAB work never touches workflow files); leave it uncommitted and move on.
2. **Coverage gaps in `data_loader.py` (PRIMARY, 352 missing lines) and `cli.py` (SECONDARY, 124 missing lines).** These are the highest-value missing branches. Remove via test-first campaigns (see Campaign A/B below). Prefer tests over impl changes; smallest correct impl change only if demonstrably justified.

## Invariants (sacred)

- Weights **lagged by 1 day** (no lookahead).
- NaN/inf/NaT handled explicitly; never silently hide bad data.
- Raise `BABDataError` on parse/validation failures where contract requires it.
- Dollar-neutral by default; liquidity/transaction-cost/slippage semantics enforced.
- Keep public APIs stable; minimal implementation fixes only for branches unreachable by public API and demonstrably correct.
- Gate GREEN after every meaningful batch; never commit RED.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (MANDATORY, HEAVY WORK)

**You are continuing BAB hardening. This is not a light triage session. Preserve commits, confirm gate GREEN, then execute a heavy multi-batch BAB campaign. Do not explore unrelated code. Do not stop at partial progress. Do not claim remote persistence. Never commit `.github/workflows/*` with the current token.**

### 0) Recon + gate (do first — never edit blind)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH PYTHONPATH=$PWD
git status --short
git log --oneline -4
git fetch origin main >/dev/null 2>&1 || true
git rev-parse HEAD origin/main 2>&1 || true
python3 -m pytest -q tests/test_controller_progress_accounting.py
bash scripts/bab_gate.sh 2>&1 | tail -15
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py,strategies/betting_against_beta/backtest.py,strategies/betting_against_beta/strategy.py,strategies/betting_against_beta/beta.py' -m 2>&1 | tail -60
```
- Gate is GREEN only at **exit 0, 0 failures**. If RED, fix root cause before BAB work. Never commit/push workflow files. Do not claim remote persistence.

### 1) Campaign A — `strategies/betting_against_beta/data_loader.py` → target >= 90% (close highest-value missing branches)
Inspect actual missing lines (`coverage report -m`), then hit branches via **public loader APIs** (`load_returns`, `load_prices`, `load_csv/json/jsonl/excel/parquet/pickle/hdf`, `validate_returns_dataframe`, coercion/normalization helpers as exposed). Prioritize:
- `_coerce_to_datetime_scalar` / datetime normalization: tz-aware/naive, epoch ns/us/ms/s, floats/strings, NaT/None/inf/nan, dayfirst, ISO/Z/offsets, ambiguous/invalid inputs.
- `_normalize_index`, index-vs-column datetime promotion, metadata column detection/drops.
- Exchange/long/wide format detection (Binance/CoinGecko-style), symbol+date(+price/return) pivots, duplicate handling.
- `_maybe_read_table`/dispatch/extension routing and parser error wrapping to `BABDataError`.
- `validate_returns_dataframe`: benchmark requirements, all-NaN/all-NaT, non-numeric coercion, insufficient columns/rows, object/string junk.
- Use `tmp_path`, `monkeypatch`, minimal fixtures; **prefer tests over impl changes**. If a branch is unreachable by public API, document why; smallest correct impl change only if demonstrably justified.

**Work loop (non-negotiable):** add focused tests → run targeted module tests → `bash scripts/bab_gate.sh` → keep GREEN → repeat in batches. **Do not stop at one file/module.** Commit BAB progress in small, gate-green chunks when authorized (non-workflow files only).

Targeted check:
```bash
python3 -m coverage run -m pytest tests/test_bab_data_loader*.py tests/test_betting_against_beta_data_loader*.py -q
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py' -m | tail -100
```

### 2) Campaign B — `strategies/betting_against_beta/cli.py` → target >= 85% (~124 missing)
Cover argparse flags/combos, `--dry-run` (must not execute backtest/side effects), `--from-prices`/`--synthetic`/`--data` validation, `--universe` parsing, output paths, exit codes/errors, `--version`.

### 3) Campaign C — harden core engines
Close high-value branches in `backtest.py` (22), `strategy.py` (32), `beta.py` (25), `signals.py` (11), `portfolio.py` (16), `sizing.py` (3). Add invariant/property tests: 1-day lag/no-lookahead, dollar neutrality, NaN/inf propagation, costs/slippage, benchmark edge cases.

## Binding rules
1. Recon first; never edit blind.
2. Gate after every meaningful batch; never commit RED.
3. BAB-only; prioritize by repo name.
4. Test-first for gaps; minimal correct impl changes only when necessary.
5. Zero regressions; preserve invariants and public API behavior.
6. No force-push/history rewrite. Preserve recovery bundle/local commits/backup refs.
7. **Never commit `.github/workflows/*` with the current token** — push will be rejected; operator must apply `/home/runner/work/_temp/workflow-stage-safe-sync-8f165a3.patch` with `workflows` permission.
8. **Update this HANDOFF** with new UTC timestamp, gate status, coverage numbers, commits, and the next concrete command/bottleneck. Keep it the single durable source of truth.

## Suggested immediate command
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta && export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH PYTHONPATH=$PWD && git status --short && python3 -m pytest -q tests/test_controller_progress_accounting.py && bash scripts/bab_gate.sh 2>&1 | tail -15
```

**Start now: confirm GREEN, then execute Campaign A on `data_loader.py` in heavy, verifiable batches.**
