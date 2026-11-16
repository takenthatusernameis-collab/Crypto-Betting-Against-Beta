# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pure pointer and must not carry a second task message. Any other `*HANDOFF*.md` is stale and must be deleted on sight.

- **Timestamp (UTC):** 2026-11-16T12:57:00Z (this refresh)
- **Repo identity:** `Crypto-Betting-Against-Beta` — a **crypto market-neutral trading system** (ingest → beta → signals → portfolio → backtest → execution → ops) implementing the Frazzini–Pedersen *Betting Against Beta* strategy. Highest-stakes paths, in order: **(1) what real orders are placed, (2) whether live fills still match the model, (3) whether the real-data ingest accepts only data fit to trade on.**
- **Git HEAD:** `71bdccc` (local commits ahead of `origin/main` `ace159e` by 2: `de9eeac` + `71bdccc`; **NOT pushed** — see blocker below). Working tree clean. All local hard gates GREEN (ruff, reconcile, 98.5% gate 6215/35/99%, 99.5% fail-closed RED). Remote persistence NOT claimed — remote SHA `ace159e` != local HEAD `71bdccc`.
- **Live probes this session:** `python3 -m ruff check .` **clean**. `bash scripts/bab_reconcile_gate.sh` **GREEN** (drift rc=2, clean/emit-only rc=0). `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` **GREEN** — **6215 passed / 35 skipped**, TOTAL **99%** (89 missed). `BAB_GATE_MIN_COVERAGE=99.5 bash scripts/bab_gate.sh` **RED** (rc=1, floor not met — fail-closed proven). **`bab-gate` job IS NOW PRESENT in `.github/workflows/main.yml`** (lines 42-98) and gates the `kilo` job via `needs: bab-gate`.

## INITIAL TASK MESSAGE (START HERE, 2026-11-16T12:57:00Z) — BINDING (DO NOT IGNORE)

**P19-1 — CI ENFORCEMENT COMMITTED LOCALLY, PUSH BLOCKED BY GH `workflows` PERMISSION — UNBLOCK THIS FIRST. SAME-RUN RECOVERY (session 93): bounded remote checkpoint persistence failed; this is a NEW session in the SAME active run, not a request to end the workflow. Current local HEAD `71bdccc`; last known remote-tracking SHA `ace159e`; failed-session HEAD was `71bdccc`. Preserve all existing local commits (`de9eeac`, `71bdccc`) and work; do not reset or discard them. Do not rewrite history unless a confirmed root cause requires it, and then only after preserving a recovery bundle and documenting the rollback plan.**

P19-1 is **locally proven AND committed** (HEAD `71bdccc`, 2 commits ahead of `origin/main`: `de9eeac` `ci: ship P19-1 bab-gate enforcement job` and `71bdccc` `chore(kilo): checkpoint agent session`). The `bab-gate` job exists in `.github/workflows/main.yml` and gates `kilo` via `needs: bab-gate`. The push was **rejected by GitHub**:

```
! [remote rejected] main -> main (refusing to allow a GitHub App to create or update workflow `.github/workflows/main.yml` without `workflows` permission)
```

**Root cause (diagnosed this session):** the repo-scoped `GITHUB_TOKEN` cannot write workflow files by design (`main.yml:25-26`, `permissions` block). The controller's checkpoint stage also strips `.github/workflows/*` from new checkpoint staging (`main.yml:1183-1185`). Repeated bounded push retries already failed (session 93) and will keep failing — do **not** burn the checkpoint budget re-pushing this ref.

**Working tree restored to HEAD this session.** An uncommitted change that removed the `bab-gate` job from `.github/workflows/main.yml` was discarded — that workaround is forbidden (it weakens the gate). Working tree is now clean at `71bdccc`.

To complete P19-1 DoD:

1. **Obtain push access to `.github/workflows/main.yml`** — a maintainer with `workflows` write permission pushes `71bdccc`, OR the workflow is amended via the GitHub web UI, OR a PAT/scoped token with `workflows:write` is used for this single push. Do **not** work around this by removing the `bab-gate` job or weakening the gate. This blocker cannot be removed locally.
2. **Verify persistence:** only after the push, confirm `git ls-remote origin refs/heads/main` returns `71bdccc` (remote SHA must match local HEAD). Do **not** claim persistence until the remote SHA matches.
3. **Watch the `bab-gate` CI job on `origin/main`** and confirm GREEN (ruff clean, suite 6215/35/99%, reconcile gate GREEN, 99.5% fail-closed proven).
4. **Do not proceed to P19-2 until `bab-gate` is observed GREEN on `origin/main`.**

The work is **fully preserved and verified locally**; the next agent's only remaining P19-1 action is the push + CI verification. Do **not** re-run the gates or re-edit the workflow; they are done.

---


P19-1 is locally proven (ruff clean, bab_gate.sh GREEN @99%, bab_reconcile_gate.sh GREEN) but the workflow **lacks the enforcement job**. Ship it now:

1. **Edit `.github/workflows/main.yml`** to add a `bab-gate` job (push/pull_request/workflow_dispatch) that runs:
   - `actions/checkout@v7.0.1`
   - Python 3.12 setup
   - `bash scripts/bab_bootstrap.sh`
   - `python3 -m ruff check .`
   - `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh`
   - `bash scripts/bab_reconcile_gate.sh`
   Keep the existing `kilo` job intact.

2. **Verify locally** (evidence required in session ledger):
   - `python3 -m ruff check .` → clean
   - `bash scripts/bab_reconcile_gate.sh` → GREEN (drift rc=2, clean/emit-only rc=0)
   - `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` → GREEN (6215 passed / 35 skipped / 99%)
   - `BAB_GATE_MIN_COVERAGE=99.5 bash scripts/bab_gate.sh` → **RED** (floor not met, proves fail-closed)

3. **Commit + push** the workflow change. Watch CI run and confirm `bab-gate` job GREEN on `main`.

**Do not proceed to P19-2 until P19-1 CI job is GREEN on `origin/main`.**

---

## P19-2 — REAL-DATA INGEST + LIVE-FILL FIDELITY HARDENING (after P19-1 DoD)

Behavioral correctness, not coverage chores (prioritized to repo identity: real orders → fills match model → data fit to trade):

1. **P19-2a — `scripts/fetch_real_bab_prices.py` network path (fetch_real_bab_prices.py:412, `_http_get_json`/`_rate_limit_wait`):** add deterministic offline (monkeypatched transport, no real network) tests proving:
   - 429 with `Retry-After` honored/retried/bounded
   - Transient 5xx (500/502/503/504) retried with backoff then fail loudly after `COINBASE_PUBLIC_MAX_RETRIES`
   - Network/URLError/timeout retries bounded then fail loudly with **no offline/synthetic fallback**
   - Non-200/parse errors fail loudly
   - ToS/opt-in gating (`--allow-public-api` + exact `--accept-terms`) enforced **before any request**

2. **P19-2b — live-fill/model reconciliation fidelity:** cover `execution.py` missed **139-141, 182-185, 563-564** with behavior tests driving realistic CCXT-shaped/fill-like inputs (string/Decimal/NaN prices, Timestamp/date-key lookup edge cases, non-finite/numpy scalar JSON sanitization) and prove reconciliation/cost gate remains fail-closed and within tolerance on valid data. `execution.py:1295-1296` still needs independent reachability proof.

3. **P19-2c — `--health-check` JSON contract:** `cli.py:760-770` — ensure contract proves **single strict-JSON object** on success (machine-parseable, `allow_nan=False`) and **documented non-zero/error behavior** when `--health-check` used without `--adapter live` (lock/document intentionally).

---

## P19-3 — CLOSE 89-LINE CORRECTNESS GAP *CORRECTLY* (after P19-2)

89 missed statements are a **correctness smell list**, not a coverage chore. For each line: add a behavior test that reaches it, or delete/justify with concrete unreachability proof. Do **not** lower the floor, do **not** add type annotations, do **not** refactor defensive try/except (BLE/TRY excluded by policy).

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

Claims needing **independent proof** (do not inherit): `execution.py:1295-1296`, `portfolio.py:180`, `cli.py:657-658`, `data_loader.py:1355`, `data_loader.py:1654-1655`. Prior spot-check suggested `portfolio.py:180` likely unreachable via public API — prove or cover, don't guess.

---

## Verified completion state (do not redo)

- **P17-1 DONE:** safe data-quality defaults wired (20/7/3), `load_prices` runs quality campaign by default, `tests/test_bab_pipeline_safety_contract.py` present.
- **P17-2 DONE:** `tests/test_bab_p17_2_targeted_gaps.py` repaired to match actual APIs.
- **P18-1 DONE:** `evaluate_reconciliation_gate` in `reconciliation.py`; CLI `--reconcile-tolerance`/`--reconcile-max-mismatch` (exit 2 on breach, `--reconcile` alone unchanged); `tests/test_bab_reconciliation_gate.py` green.
- **P18-2 DONE:** `LiveExecutionAdapter` requires `allow_live_execution=True` + exact `accept_terms='I_UNDERSTAND_LIVE_TRADING'` for `dry_run=False`; CLI flags wired, dry-run default preserved; `tests/test_bab_live_opt_in.py` green.
- **P18-3 DONE:** `scripts/bab_reconcile_gate.sh` exists and locally proven (drift rc=2, clean/emit-only rc=0).
- **P19-1 DONE (committed, push blocked):** `bab-gate` job added to `.github/workflows/main.yml`; `kilo` job gated via `needs: bab-gate`. Commits `de9eeac` + `71bdccc` local, **2 ahead of `origin/main`**; requires maintainer `workflows` write access (or PAT with `workflows:write`) to push and observe CI GREEN. All local gates GREEN (ruff clean, reconcile GREEN, gate 6215/35/99%, gate RED @99.5% fail-closed proven).
- **Kill switch (R4-B) covered:** `tests/test_bab_drawdown_kill_switch_r4.py` — verify only.

---

## Deferred backlog (only after P19-1/2/3 DoD)

- **P20-1:** `python3 scripts/perf_baseline.py --record` after any perf-touching change, then `--check` must stay GREEN.
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

- ❌ Handoff-only sessions or refreshing this file without shipping code/tests/workflow changes.
- ❌ Claiming CI enforcement without observed RED/GREEN evidence in CI/workflow runs.
- ❌ Lowering the coverage floor — add tests, don't lower the bar.
- ❌ Adding type annotations (ANN excluded by policy).
- ❌ Refactoring defensive try/except patterns (BLE/TRY excluded).
- ❌ Coverage-chasing *instead of* correctness/production fixes.
- ❌ Adding a second diagnostics collector or parallel handoff docs.

---

## Bottleneck removal status

- ✅ **Single durable handoff:** only `HANDOFF.md` (+ pointer `AGENT_HANDOFF.md`).
- ✅ **Stale prior "P19-1 done" claim corrected:** workflow does NOT enforce BAB gates; HANDOFF now reflects truth.
- ✅ **Gate is parallel + sysmon:** local full gate runnable (~2 min here); no per-session gate blocker observed.
- ✅ **No merge bottleneck known:** `main` synced to `origin/main`.
- ✅ **P19-1 (next):** ship `bab-gate` CI job to `.github/workflows/main.yml`, prove GREEN on `origin/main`.
- 🔲 **P19-2:** real-data ingest retries/gating + execution fill/reconciliation fidelity + `--health-check` JSON contract.
- 🔲 **P19-3:** coverage-gap correctness (after P19-2).

---

## Push blocker (P19-1)

The repo-scoped `GITHUB_TOKEN` cannot write `.github/workflows/*` — GitHub refuses with:

```
! [remote rejected] main -> main (refusing to allow a GitHub App to create or update workflow `.github/workflows/main.yml` without `workflows` permission)
```

**Diagnosed root cause (this session):** this is by design (`main.yml:25-26`, `permissions` block). Additionally, the controller's checkpoint stage strips `.github/workflows/*` from new checkpoint staging (`main.yml:1183-1185`), so the controller itself cannot push a `main` ref that carries a workflow-file change. Both commits `de9eeac` and `71bdccc` modify `.github/workflows/main.yml`, so the entire ref update is rejected; no part of `main` can be pushed until the workflow-file change reaches `origin/main` by another authorized path.

To finish P19-1 DoD a maintainer with `workflows` write permission must push `71bdccc`, or amend the workflow via the GitHub web UI, or use a PAT/scoped token with `workflows:write` for this single push. Do **not** weaken the gate or delete the job to work around this. Until the push is remotely verified (`git ls-remote origin refs/heads/main` == `71bdccc`), persistence is NOT claimed and P19-2 must not start.

---

## Session ledger (append one line per session; keep it honest)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-16T08:20:06Z | 934f008+ | Repaired import errors in `test_bab_p17_2_targeted_gaps.py`. Core 6193 passed; P17-2 file 24 failures from API mismatches. Ruff clean. 99% (91 missed). | RED (P17-2 file only) |
| 2026-11-16T10:39:07Z | 7ecf592+ | Repaired `tests/test_bab_p17_2_targeted_gaps.py` to match actual APIs (38 pass). Gate GREEN 6215/35/99% (89 missed). | GREEN @10:39Z |
| 2026-11-16T10:40:05Z | c810c3f | Refreshed handoff only; binding P17-3. | GREEN @10:40Z |
| 2026-11-16T10:45:54Z | 91d6dc5 | Live-verified gate GREEN 6215/35/99%, ruff clean, perf PASS. Found CI does not enforce ruff/suite/coverage/reconcile gate. | GREEN @10:45Z |
| 2026-11-16T11:40:00Z | 91d6dc5 | Claimed P19-1 complete in docs; **not reflected in workflow at 8562f91** (no `bab-gate` job in `.github/workflows/main.yml`). Treat as unproven/rolled-back claim. | claim unverified |
| 2026-11-16T12:29:00Z | 8562f91 | Re-verified live: `ruff` clean, `bab_reconcile_gate.sh` GREEN, `bab_gate.sh` GREEN 6215/35/99%, workflow has **no bab enforcement**. Corrected README+HANDOFF to remove false CI-enforcement claim and re-bound next work to **P19-1 ship+prove**. | GREEN local @12:29Z |
| 2026-11-16T12:34:01Z | 8562f91 | HANDOFF refreshed (P19-1 claimed shipped but uncommitted). | — |
| 2026-11-16T12:39:43Z | 700d2af | **Truth refresh:** working tree clean, HEAD=700d2af, workflow **still lacks `bab-gate` job**. P19-1 NOT shipped. Re-bound initial task to **P19-1 ship CI enforcement first**. | GREEN local |
| 2026-11-16T12:50:00Z | de9eeac | **P19-1 SHIPPED (committed, push blocked).** Added `bab-gate` job to `.github/workflows/main.yml:42-98` (checkout@7.0.1, setup-python@7.1.0, bootstrap, ruff, `bab_gate.sh @98.5%`, 99.5% fail-closed proof step, `bab_reconcile_gate.sh`); `kilo` job now gated via `needs: bab-gate`. Live-verified: ruff clean, reconcile GREEN, gate GREEN 6215/35/99%, gate RED @99.5% (fail-closed proven). Committed `de9eeac`. **Push rejected by GitHub policy** — repo-scoped token lacks `workflows` write permission; commit is local, 1 ahead of origin/main, working tree clean. Requires maintainer `workflows` access to push. | GREEN local; push blocked |

---

**Next agent (binding):** Start immediately at **P19-1 — SHIP CI ENFORCEMENT** (add `bab-gate` job to `.github/workflows/main.yml`, prove GREEN locally, commit, push, verify GREEN on `origin/main`). Do not narrate completion: edit workflow → run hard gates locally → capture command evidence → commit/push → watch CI → update ledger/HANDOFF truthfully. Only after P19-1 CI job is GREEN on `origin/main`, proceed to **P19-2** (real-data ingest + live-fill fidelity hardening: 2a fetch_real_bab_prices.py network tests, 2b execution.py fill/reconciliation fidelity, 2c --health-check JSON contract), then P19-3 correctness closure of remaining 89 missed lines.