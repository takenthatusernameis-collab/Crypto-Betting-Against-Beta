# NEXT SESSION INITIAL TASK MESSAGE
**Timestamp (UTC):** 2026-11-16T13:37:47Z
**Repo:** `Crypto-Betting-Against-Beta` — Crypto market-neutral trading system implementing Frazzini–Pedersen **Betting Against Beta (BAB)** strategy. Highest-stakes paths: (1) real orders placed, (2) live fills match model, (3) real-data ingest accepts only trade-fit data.

---

## BINDING START POINT — READ THIS FIRST

**P19-1 IS LOCALLY COMMITTED BUT PUSH-BLOCKED BY GH `workflows` PERMISSION. UNBLOCK THIS FIRST. DO NOT START P19-2.**

- Commit `de9eeac` (branch `kilo-recovery-session-105`) adds the **`bab-gate` CI job** to `.github/workflows/main.yml:42-98` (checkout@v7.0.1, setup-python@v7.1.0, bootstrap, ruff, `bab_gate.sh @98.5%`, 99.5% fail-closed proof, `bab_reconcile_gate.sh`). The `kilo` job is gated via `needs: bab-gate`.
- Working tree on `main` has the **unstaged modification byte-identical to `de9eeac`**.
- `de9eeac` is **NOT on `origin/main`** — HEAD `3707ee5` == `origin/main` lacks the `bab-gate` job.
- **Root cause:** repo-scoped `GITHUB_TOKEN` has `actions: read, contents: write` — **no `workflows:write`**. GitHub rejects pushes to `.github/workflows/*`. Controller checkpoint staging also strips workflow files.
- **All local gates GREEN:** `ruff` clean, `bab_reconcile_gate.sh` GREEN (drift RC=2, clean/emit-only RC=0), `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` GREEN (6215 passed, 35 skipped, 99% coverage). `BAB_GATE_MIN_COVERAGE=99.5` RED fail-closed proven.

---

## P19-1 DoD (MUST COMPLETE BEFORE P19-2)

1. **Obtain push access to `.github/workflows/main.yml`** — a maintainer with `workflows` write permission pushes `de9eeac` (or cherry-picks it onto `origin/main`), OR the workflow is amended via GitHub web UI, OR a PAT/scoped token with `workflows:write` is used for this single push. **Do not weaken or remove the `bab-gate` job.**
2. **Verify persistence:** after push, confirm `git ls-remote origin refs/heads/main` returns the SHA of `de9eeac` (remote SHA must match the commit carrying `bab-gate`).
3. **Watch `bab-gate` CI job on `origin/main`** and confirm GREEN (ruff clean, suite 6215/35/99%, reconcile gate GREEN, 99.5% fail-closed proven).
4. **Only then proceed to P19-2.**

> The work is fully preserved and verified locally. The next agent's only remaining P19-1 action is the push + CI verification. Do not re-run gates or re-edit the workflow.

---

## P19-2 — REAL-DATA INGEST + LIVE-FILL FIDELITY HARDENING (BLOCKED until P19-1 DoD)

Prioritized to repo identity: **real orders → fills match model → data fit to trade**.

### P19-2a — `scripts/fetch_real_bab_prices.py` network path (fetch_real_bab_prices.py:412, `_http_get_json`/`_rate_limit_wait`)
Add deterministic offline (monkeypatched transport, **no real network**) tests proving:
- 429 with `Retry-After` honored/retried/bounded
- Transient 5xx (500/502/503/504) retried with backoff then fail loudly after `COINBASE_PUBLIC_MAX_RETRIES`
- Network/URLError/timeout retries bounded then fail loudly with **no offline/synthetic fallback**
- Non-200/parse errors fail loudly
- ToS/opt-in gating (`--allow-public-api` + exact `--accept-terms`) enforced **before any request**

### P19-2b — Live-fill/model reconciliation fidelity
Cover `execution.py` missed lines **139-141, 182-185, 563-564** with behavior tests driving realistic CCXT-shaped/fill-like inputs (string/Decimal/NaN prices, Timestamp/date-key lookup edge cases, non-finite/numpy scalar JSON sanitization) and prove reconciliation/cost gate remains fail-closed and within tolerance on valid data. `execution.py:1295-1296` still needs independent reachability proof.

### P19-2c — `--health-check` JSON contract
`cli.py:760-770` — ensure contract proves **single strict-JSON object** on success (machine-parseable, `allow_nan=False`) and **documented non-zero/error behavior** when `--health-check` used without `--adapter live` (lock/document intentionally).

---

## P19-3 — CLOSE 89-LINE CORRECTNESS GAP *CORRECTLY* (after P19-2)

89 missed statements = **correctness smell list**, not a coverage chore. For each line: add a behavior test that reaches it, or delete/justify with concrete unreachability proof. Do not lower floor, do not add type annotations, do not refactor defensive try/except (BLE/TRY excluded by policy).

Missed lines to re-verify live before acting:
- `beta.py`: 125, 163, 170-171, 189, 435-436, 552-556 (12)
- `data_loader.py`: 280-292, 296-297, 315-316, 422-423, 666-667, 718-719, 837-838, 1355, 1615, 1654-1655, 1660-1662, 1676-1681, 1958-1959, 2762-2763 (34)
- `execution.py`: 139-141, 182-185, 563-564, 1295-1296 (11)
- `cli.py`: 75, 657-658, 836-838, 893-894 (8)
- `portfolio.py`: 152-153, 170-177, 180 (11)
- `data_sources.py`: 480-481, 499-500, 507-508 (6)
- `reconciliation.py`: 82-83, 309 (3)
- `signals.py`: 37, 75 (2)
- `metrics.py`: 94 (1)
- `replay.py`: 172 (1)

**Claims needing independent proof (do not inherit):** `execution.py:1295-1296`, `portfolio.py:180`, `cli.py:657-658`, `data_loader.py:1355`, `data_loader.py:1654-1655`. Prior spot-check suggested `portfolio.py:180` likely unreachable via public API — prove or cover, don't guess.

---

## VERIFIED COMPLETION STATE (DO NOT REDO)
- P17-1: safe data-quality defaults (20/7/3), `load_prices` runs quality campaign by default, `tests/test_bab_pipeline_safety_contract.py` present
- P17-2: `tests/test_bab_p17_2_targeted_gaps.py` repaired to match actual APIs
- P18-1: `evaluate_reconciliation_gate` in `reconciliation.py`; CLI `--reconcile-tolerance`/`--reconcile-max-mismatch` (exit 2 on breach); `tests/test_bab_reconciliation_gate.py` green
- P18-2: `LiveExecutionAdapter` requires `allow_live_execution=True` + exact `accept_terms='I_UNDERSTAND_LIVE_TRADING'` for `dry_run=False`; CLI flags wired; `tests/test_bab_live_opt_in.py` green
- P18-3: `scripts/bab_reconcile_gate.sh` exists and locally proven (drift RC=2, clean/emit-only RC=0)
- P19-1: **committed locally as `de9eeac`, push blocked** — `bab-gate` job added, `kilo` job gated via `needs: bab-gate`
- Kill switch (R4-B): `tests/test_bab_drawdown_kill_switch_r4.py` — verify only

---

## HARD GATES EVERY SESSION (REPO ROOT, IN ORDER)
```bash
python3 -m ruff check .                 # must pass
bash scripts/bab_reconcile_gate.sh      # reconciliation fail-closed, must be GREEN
bash scripts/bab_gate.sh                # full suite + coverage, must be GREEN
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh   # release floor must hold
```

---

## NON-GOALS (DO NOT PURSUE)
- ❌ Handoff-only sessions or refreshing this file without shipping code/tests/workflow changes
- ❌ Claiming CI enforcement without observed RED/GREEN evidence in CI/workflow runs
- ❌ Lowering the coverage floor — add tests, don't lower the bar
- ❌ Adding type annotations (ANN excluded by policy)
- ❌ Refactoring defensive try/except patterns (BLE/TRY excluded)
- ❌ Coverage-chasing *instead of* correctness/production fixes
- ❌ Adding a second diagnostics collector or parallel handoff docs

---

## BOTTLENECK REMOVAL STATUS
- ✅ Single durable handoff: only `HANDOFF.md` (+ pointer `AGENT_HANDOFF.md`)
- ✅ Recovery bundle preserved: `/tmp/kilo-recovery-session-105.bundle` + branch `kilo-recovery-session-105` at pre-recovery HEAD `2b72ed8`
- ✅ Checkpoint commits persisted: rebased `71bdccc`+`2b72ed8` onto `ace159e`, pushed to `origin/main` `a9b061b`, remote SHA verified
- ✅ No merge bottleneck: `main` synced to `origin/main` at `3707ee5`
- ✅ Bottleneck diagnosed and pre-staged: P19-1 `bab-gate` change committed as `de9eeac` on `kilo-recovery-session-105` AND present as unstaged worktree changes on `main` matching `de9eeac` byte-for-byte; ready to push the moment `workflows` write access exists
- ⏳ **PENDING** P19-1: `de9eeac` cannot be pushed by repo-scoped token (no `workflows:write`). Needs maintainer push, web UI amendment, or PAT with `workflows:write`. P19-2/P19-3 remain blocked until `de9eeac` is GREEN on `origin/main`.

---

## SESSION LEDGER (append one line per session; keep it honest)
| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-16T13:29:57Z | 3707ee5 | State refresh: main==origin/main at 3707ee5, P19-1 commit de9eeac local only, push blocked by workflows permission | GREEN local; push blocked |
| **NEXT SESSION** | **?** | **UNBLOCK P19-1 PUSH → VERIFY CI GREEN → START P19-2** | **TARGET: GREEN on origin/main** |

---

**START HERE. UNBLOCK THE PUSH. VERIFY CI. THEN P19-2. NO EXCEPTIONS.**