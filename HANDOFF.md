# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pure pointer and must not carry a second task message. Any other `*HANDOFF*.md` is stale and must be deleted on sight.

- **Timestamp (UTC):** 2026-11-16T18:42:46Z (this refresh)
- **Repo identity:** `Crypto-Betting-Against-Beta` — a **crypto market-neutral trading system** (ingest → beta → signals → portfolio → backtest → execution → ops) implementing the Frazzini–Pedersen *Betting Against Beta* strategy. Highest-stakes paths, in order: **(1) what real orders are placed, (2) whether live fills still match the model, (3) whether the real-data ingest accepts only data fit to trade on.**
- **Git state:** local HEAD `b81ba35` == `origin/main` `b81ba35` (sync verified this session). Working tree clean; no unstaged changes. Currently on `main`.
- **Live gate evidence (this session):** `python3 -m ruff check .` → clean; `bash scripts/bab_reconcile_gate.sh` → GREEN (drift rc=2, clean rc=0, emit-only rc=0); `scripts/bab_gate.sh` → **GREEN 6215 passed / 35 skipped / 99% (89 missed)**.

---

## INITIAL TASK MESSAGE (START HERE, 2026-11-16T18:42:46Z) — BINDING (DO NOT IGNORE)

**EXECUTE P19-2 NOW: REAL-DATA INGEST + LIVE-FILL FIDELITY HARDENING. Ship behavior tests this session. Do NOT do a handoff-only pass. Do NOT re-attempt the CI workflow push.**

**Why this is the start (read the two bullets below before touching anything):**
1. **P19-1 is dead and was the bottleneck — do not resurrect it.** The previous campaign hard-blocked *all* correctness work behind pushing a `bab-gate` job into `.github/workflows/main.yml`. That push is **impossible for any agent session**: the repo-scoped `GITHUB_TOKEN` has `actions: read, contents: write` only (see `.github/workflows/main.yml` `permissions:` block), so GitHub rejects any workflow-file write with `refusing to allow a GitHub App to create or update workflow ... without workflows permission`. The commit carrying it (`b641b7a` on branch `kilo-p19-1-push`) **no longer exists anywhere in this repo** — not on any local/remote branch, no dangling object. Multiple sessions burned their entire budget re-attempting this un-winnable push while P19-2/P19-3 sat blocked. **CI-enforcement is now an explicitly-tracked MAINTAINER follow-up (see "Deferred / external"), not a gate on agent work.** If you feel the urge to "fix CI", stop — read that section instead.
2. **P19-2/P19-3 need no external access and are the repo's identity.** They are pure local behavior-test work against the highest-stakes paths (real orders, fills matching the model, ingest accepting only trade-fit data). They are 100% completable now. Do them.

**P19-2 deliverables (ship tests, keep every hard gate GREEN):**

- **P19-2a — `scripts/fetch_real_bab_prices.py` network path.** Add deterministic, offline (monkeypatched transport, **no real network**) tests for `_http_get_json` / `_rate_limit_wait` (see `fetch_real_bab_prices.py:261-290`, retry cap `COINBASE_PUBLIC_MAX_RETRIES` at line 71) proving:
  - 429 with `Retry-After` is honored/retried/bounded.
  - Transient 5xx (500/502/503/504) retried with backoff, then fail loudly after `COINBASE_PUBLIC_MAX_RETRIES`.
  - Network/`URLError`/timeout retries bounded, then fail loudly with **no offline/synthetic fallback**.
  - Non-200 / parse errors fail loudly.
  - ToS/opt-in gating (`--allow-public-api` + exact `--accept-terms`) is enforced **before any request is sent**.
- **P19-2b — live-fill/model reconciliation fidelity.** Cover the still-missed `execution.py` branches **139-141, 182-185, 563-564** with behavior tests driving realistic CCXT-shaped/fill-like inputs (string/Decimal/NaN prices, `Timestamp`/date-key lookup edge cases, non-finite / numpy-scalar JSON sanitization). Prove reconciliation + cost gate stay fail-closed and within tolerance on valid data. `execution.py:1295-1296` still needs an independent reachability proof (see P19-3).
- **P19-2c — `--health-check` JSON contract.** `cli.py` around the health-check block (`cli.py:757-770`): prove **single strict-JSON object** on success (machine-parseable, `allow_nan=False`) and the **documented non-zero/error path** when `--health-check` is used without `--adapter live` (this is intentional lock-and-document, not a bug to "fix").

**Hard rule:** every new test must **raise or hold** the 99% floor — never lower it, never add type annotations (ANN excluded by policy), never refactor defensive try/except (BLE/TRY excluded). When P19-2 is GREEN, proceed to P19-3 (89-line correctness gap). Append one honest line to the session ledger at the bottom.

---

## P19-3 — CLOSE 89-LINE CORRECTNESS GAP *CORRECTLY* (after P19-2)

89 missed statements are a **correctness smell list**, not a coverage chore. For each line: add a behavior test that reaches it, or delete/justify with concrete unreachability proof. Do **not** lower the floor, do **not** add type annotations, do **not** refactor defensive try/except (BLE/TRY excluded by policy).

Missed lines **re-verified live this session (6215 passed / 89 missed / 99%):**
- `beta.py`: 125, 163, 170-171, 189, 435-436, 552-556 (12)
- `data_loader.py`: 280-292, 296-297, 315-316, 422-423, 666-667, 718-719, 837-838, 1355, 1615, 1654-1655, 1660-1662, 1676-1681, 1958-1959, 2762-2763 (34)
- `execution.py`: 139-141, 182-185, 563-564, 1295-1296 (11) — covered by P19-2b, plus 1295-1296 proof
- `cli.py`: 75, 657-658, 836-838, 893-894 (8)
- `portfolio.py`: 152-153, 170-177, 180 (11)
- `data_sources.py`: 480-481, 499-500, 507-508 (6)
- `reconciliation.py`: 82-83, 309 (3)
- `signals.py`: 37, 75 (2)
- `metrics.py`: 94 (1)
- `replay.py`: 172 (1)

Claims needing **independent proof** (do not inherit): `execution.py:1295-1296`, `portfolio.py:180`, `cli.py:657-658`, `data_loader.py:1355`, `data_loader.py:1654-1655`. Prior spot-check suggested `portfolio.py:180` is likely unreachable via the public API — prove or cover it, don't guess.

---

## Verified completion state (do not redo)

- **P17-1 DONE:** safe data-quality defaults wired (20/7/3); `load_prices` runs the quality campaign by default; `tests/test_bab_pipeline_safety_contract.py` present.
- **P17-2 DONE:** `tests/test_bab_p17_2_targeted_gaps.py` repaired to match actual APIs (38 pass).
- **P18-1 DONE:** `evaluate_reconciliation_gate` in `reconciliation.py`; CLI `--reconcile-tolerance`/`--reconcile-max-mismatch` (exit 2 on breach; `--reconcile` alone unchanged); `tests/test_bab_reconciliation_gate.py` green.
- **P18-2 DONE:** `LiveExecutionAdapter` requires `allow_live_execution=True` + exact `accept_terms='I_UNDERSTAND_LIVE_TRADING'` for `dry_run=False`; CLI flags wired, dry-run default preserved; `tests/test_bab_live_opt_in.py` green.
- **P18-3 DONE:** `scripts/bab_reconcile_gate.sh` exists and locally proven (drift rc=2, clean/emit-only rc=0). Re-verified GREEN this session.
- **Kill switch (R4-B) covered:** `tests/test_bab_drawdown_kill_switch_r4.py` — verify only.
- **Toolchain bootstrap:** `scripts/bab_bootstrap.sh` installs missing deps (numpy/pandas/scipy/pytest/pytest-cov/xdist/hypothesis/coverage/ccxt/ruff); safe to run on any fresh runner.

---

## Deferred / external (do NOT let these block agent work)

- **P19-1 (CI ENFORCEMENT) — MAINTAINER FOLLOW-UP, not an agent task.** Adding a `bab-gate` job (ruff + suite + 98.5% coverage floor + reconcile gate) to `.github/workflows/main.yml` requires `workflows: write` permission that no agent session can obtain. A prior commit (`b641b7a`, branch `kilo-p19-1-push`) was lost when its branch vanished. **Do not re-attempt the push, do not re-create the branch in the agent loop.** A maintainer must add the `bab-gate` job via the GitHub web UI or a `workflows:write` PAT. This never blocks P19-2/P19-3.
- **P20-1:** `python3 scripts/perf_baseline.py --record` after any perf-touching change; `--check` must stay GREEN.
- **P20-2:** add `--durations=20` visibility to gate output/logging for slow tests; keep `--dist loadscope`.
- **P20-3:** repo hygiene — `probe_*.py` / `debug_beta*.py` tracked but gitignored (12 files); decide keep-vs-delete and align `.gitignore` + index.

---

## Hard gates every session (repo root, in order)

```bash
python3 -m ruff check .                 # must pass
bash scripts/bab_reconcile_gate.sh      # reconciliation fail-closed, must be GREEN
bash scripts/bab_gate.sh                # full suite + coverage, must be GREEN
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh   # release floor must hold
```

---

## Non-goals (do not pursue)

- ❌ Handoff-only sessions or refreshing this file without shipping code/tests.
- ❌ Re-attempting the `.github/workflows/*` push (impossible without `workflows:write`) — see Deferred.
- ❌ Claiming CI enforcement without observed RED/GREEN evidence in real CI runs.
- ❌ Lowering the coverage floor — add tests, don't lower the bar.
- ❌ Adding type annotations (ANN excluded by policy).
- ❌ Refactoring defensive try/except patterns (BLE/TRY excluded).
- ❌ Coverage-chasing *instead of* correctness/production fixes.
- ❌ Adding a second diagnostics collector or parallel handoff docs.

---

## Bottleneck removal status (this refresh)

- [DONE] Single durable handoff: only `HANDOFF.md` (+ pointer `AGENT_HANDOFF.md`).
- [DONE] **Removed the false P19-1 hard-blocker:** the workflow-push campaign was structurally un-winnable by agents and consumed whole sessions. P19-1 is reclassified as a maintainer follow-up; P19-2/P19-3 are unblocked and are now the binding start.
- [DONE] Verified `main` == `origin/main` at `b81ba35`; working tree clean.
- [DONE] Local gates re-verified GREEN this session (ruff clean; reconcile GREEN; gate 6215/35/99%).
- [EXTERNAL] P19-1 CI enforcement: requires maintainer `workflows:write` (web UI or PAT). Non-blocking.

---

## Session ledger (append one line per session; keep it honest)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-16T08:20:06Z | 934f008+ | Repaired import errors in `test_bab_p17_2_targeted_gaps.py`. Core 6193 passed; P17-2 file 24 failures from API mismatches. Ruff clean. 99% (91 missed). | RED (P17-2 file only) |
| 2026-11-16T10:39:07Z | 7ecf592+ | Repaired `tests/test_bab_p17_2_targeted_gaps.py` to match actual APIs (38 pass). Gate GREEN 6215/35/99% (89 missed). | GREEN @10:39Z |
| 2026-11-16T10:45:54Z | 91d6dc5 | Live-verified gate GREEN 6215/35/99%, ruff clean, perf PASS. Found CI does not enforce ruff/suite/coverage/reconcile gate. | GREEN @10:45Z |
| 2026-11-16T12:50:00Z | de9eeac | P19-1 bab-gate job committed locally; push rejected by GitHub `workflows` permission. | GREEN local; push blocked |
| 2026-11-16T13:39:35Z | d23011e | State refresh; P19-1 push still blocked; P19-2/P19-3 BLOCKED behind it. | GREEN local; push blocked |
| 2026-11-16T18:42:46Z | b81ba35 (= origin/main) | **Bottleneck removed.** P19-1 commit `b641b7a` confirmed GONE (no branch, no dangling commit); reclassified P19-1 as maintainer-only follow-up, unblocked P19-2. Live-verified: ruff clean; reconcile GREEN; gate 6215/35/99% (89 missed). Bound next work to **P19-2 real-data ingest + live-fill fidelity**. | GREEN local |