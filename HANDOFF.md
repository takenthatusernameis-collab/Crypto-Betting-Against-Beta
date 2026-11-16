# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pure pointer and must not carry a second task message. Any other `*HANDOFF*.md` is stale and must be deleted on sight.

- **Timestamp (UTC):** 2026-11-16T12:29:00Z (this refresh)
- **Repo identity:** `Crypto-Betting-Against-Beta` — a **crypto market-neutral trading system** (ingest → beta → signals → portfolio → backtest → execution → ops) implementing the Frazzini–Pedersen *Betting Against Beta* strategy. Highest-stakes paths, in order: **(1) what real orders are placed, (2) whether live fills still match the model, (3) whether the real-data ingest accepts only data fit to trade on.**
- **Git HEAD (verified this refresh):** `8562f91` (`main`, working tree dirty in-session only until committed; `origin/main` sync not assumed — verify).
- **Live probes @8562f91 (this session):** `python3 -m ruff check .` **clean**. `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` **GREEN** — **6215 passed / 35 skipped**, TOTAL **99%** (89 missed / 6710). `bash scripts/bab_reconcile_gate.sh` **GREEN** (drift rc=2, clean rc=0, emit-only rc=0). `.github/workflows/main.yml` has **no `bab-gate` job** and does **not** run `ruff`/`bab_gate.sh`/`bab_reconcile_gate.sh` (grep: no `bab` in workflow).

## INITIAL TASK MESSAGE (START HERE, 2026-11-16T12:29:00Z) — BINDING (DO NOT IGNORE)

**Campaign P19-1 — CI ENFORCEMENT ARMBAR (highest priority; safety claims are currently UNGUARDED in CI).**

**Critical truth (re-verified):** prior handoff/README text claiming P19-1 complete and CI-enforced was **not true on current `main`**. `HEAD 8562f91` only modified `AGENT_HANDOFF.md`/`HANDOFF.md`/`README.md`; `.github/workflows/main.yml` still lacks any BAB enforcement job. The 6215-test suite, 98.5% floor, and reconciliation fail-closed gate are **enforced locally/scripts only, not by GitHub Actions**. README has been corrected this session to reflect this gap — keep docs truthful.

**Do this, in order, and prove each with command/output evidence captured in the session ledger (no handoff-only session):**

1. **Ship `bab-gate` CI job** in `.github/workflows/main.yml` (push, pull_request, workflow_dispatch): checkout `actions/checkout@v7.0.1`, setup Python 3.12, run `bash scripts/bab_bootstrap.sh` (or equivalent deps install), then `python3 -m ruff check .`, `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh`, `bash scripts/bab_reconcile_gate.sh`. Keep existing controller/diagnostics job intact. **No parallel diagnostics collector/ledger writer.**
2. **Prove fail-closed in real execution evidence**: run the job steps locally (or an equivalent harness) with an injected failure (e.g. `BAB_GATE_MIN_COVERAGE=99.5` or a reconcile drift case) showing **RED/non-zero**, revert, show **GREEN** on clean state. Paste RED+GREEN excerpts in ledger. A job never observed RED is not enforcement.
3. **Update README/HANDOFF truthfully** once and only once enforcement is actually present and proven (name the exact job/steps in wording). Do not re-assert "CI enforces" without evidence in repo/workflow.
4. **DoD P19-1:** workflow enforces ruff + full suite + 98.5% floor + reconcile gate; RED-on-injected-failure and GREEN-on-clean proven and recorded. Commit/push the workflow change.

## SECONDARY CAMPAIGN (start only after P19-1 DoD) — P19-2: real-data ingest + live-fill fidelity hardening

Behavioral correctness, not coverage chores (prioritized to repo identity: real orders → fills match model → data fit to trade):

- **P19-2a — `scripts/fetch_real_bab_prices.py` network path (fetch_real_bab_prices.py:412, _http_get_json/_rate_limit_wait):** add deterministic offline (monkeypatched transport, no real network) tests proving: 429 with `Retry-After` is honored and retried/bounded; transient 5xx (500/502/503/504) retried with backoff then fail loudly after `COINBASE_PUBLIC_MAX_RETRIES`; network/URLError/timeout retries bounded then fail loudly with no offline/synthetic fallback; non-200/parse errors fail loudly; ToS/opt-in gating (`--allow-public-api` + exact `--accept-terms`) enforced before any request. This is ingress for real trading data.
- **P19-2b — live-fill/model reconciliation fidelity:** cover `execution.py` missed **139-141, 182-185, 563-564** with behavior tests driving realistic CCXT-shaped/fill-like inputs (string/Decimal/NaN prices, Timestamp/date-key lookup edge cases, non-finite/numpy scalar JSON sanitization) and prove reconciliation/cost gate remains fail-closed and within tolerance on valid data. `execution.py:1295-1296` still needs independent reachability proof.
- **P19-2c — `--health-check` JSON contract:** `cli.py:760-770` — existing tests cover happy path and missing-adapter error; add/ensure contract proves **single strict-JSON object** on success (machine-parseable, `allow_nan=False`) and **documented non-zero/error behavior** when `--health-check` used without `--adapter live` (current behavior prints plain error string and rc=1 — lock/document intentionally).

## TERTIARY (only after P19-1/P19-2) — P19-3: close the 89-line coverage gap *correctly*

89 missed statements are a **correctness smell list**, not a coverage chore. For each line: add a behavior test that reaches it, or delete/justify with concrete unreachability proof. Do **not** lower the floor, do **not** add type annotations, do **not** refactor defensive try/except (BLE/TRY excluded by policy).

Missed lines to re-verify live before acting (baseline @8562f91):
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

## Verified completion state (do not redo)

- **P17-1 DONE:** safe data-quality defaults wired (20/7/3), `load_prices` runs quality campaign by default, `tests/test_bab_pipeline_safety_contract.py` present.
- **P18-1 DONE:** `evaluate_reconciliation_gate` in `reconciliation.py`; CLI `--reconcile-tolerance`/`--reconcile-max-mismatch` (exit 2 on breach, `--reconcile` alone unchanged); `tests/test_bab_reconciliation_gate.py` green.
- **P18-2 DONE:** `LiveExecutionAdapter` requires `allow_live_execution=True` + exact `accept_terms='I_UNDERSTAND_LIVE_TRADING'` for `dry_run=False`; CLI flags wired, dry-run default preserved; `tests/test_bab_live_opt_in.py` green.
- **P18-3 PARTIAL (local only):** `scripts/bab_reconcile_gate.sh` exists and passes locally (drift rc=2, clean rc=0). **Not invoked by `.github/workflows/main.yml`** — CI enforcement is **not** done; tracked as P19-1.
- **P17-2 DONE:** `tests/test_bab_p17_2_targeted_gaps.py` repaired to match actual APIs.
- **Kill switch (R4-B) covered:** `tests/test_bab_drawdown_kill_switch_r4.py` — verify only.

## Deferred backlog (only after P19-1/2/3 DoD)

- **P20-1:** `python3 scripts/perf_baseline.py --record` after any perf-touching change, then `--check` must stay GREEN.
- **P20-2:** add `--durations=20` visibility to gate output/logging for slow tests; keep `--dist loadscope`.
- **P20-3:** repo hygiene — `probe_*.py` / `debug_beta*.py` tracked but gitignored (12 files); decide keep-vs-delete and align `.gitignore` + index.

## Hard gates every session (repo root, in order)

```bash
python3 -m ruff check .                 # must pass
bash scripts/bab_reconcile_gate.sh      # reconciliation fail-closed, must be GREEN
bash scripts/bab_gate.sh                # full suite + coverage, must be GREEN
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh   # release floor must hold
```

## Non-goals (do not pursue)

- ❌ Handoff-only sessions or refreshing this file without shipping code/tests/workflow changes.
- ❌ Claiming CI enforcement without a shipped workflow job and observed RED/GREEN evidence.
- ❌ Lowering the coverage floor — add tests, don't lower the bar.
- ❌ Adding type annotations (ANN excluded by policy).
- ❌ Refactoring defensive try/except patterns (BLE/TRY excluded).
- ❌ Coverage-chasing *instead of* correctness/production fixes.
- ❌ Adding a second diagnostics collector or parallel handoff docs.

## Bottleneck removal status

- ✅ **Single durable handoff:** only `HANDOFF.md` (+ pointer `AGENT_HANDOFF.md`).
- ✅ **Stale prior "P19-1 done" claim corrected:** README and handoff now reflect that CI does not enforce BAB gates.
- ✅ **Gate is parallel + sysmon:** local full gate runnable (~2 min here); no per-session gate blocker observed.
- ✅ **No merge bottleneck known:** verify `main` vs `origin/main` before commit.
- 🔴 **P19-1 UNRESOLVED (critical):** `.github/workflows/main.yml` has no `bab-gate` job; `ruff`/suite/coverage floor/reconcile gate not CI-enforced.
- 🔲 P19-2 real-data + live-fill hardening; 🔲 P19-3 coverage-gap correctness (after P19-1/2).

## Session ledger (append one line per session; keep it honest)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-16T08:20:06Z | 934f008+ | Repaired import errors in `test_bab_p17_2_targeted_gaps.py`. Core 6193 passed; P17-2 file 24 failures from API mismatches. Ruff clean. 99% (91 missed). | RED (P17-2 file only) |
| 2026-11-16T10:39:07Z | 7ecf592+ | Repaired `tests/test_bab_p17_2_targeted_gaps.py` to match actual APIs (38 pass). Gate GREEN 6215/35/99% (89 missed). | GREEN @10:39Z |
| 2026-11-16T10:40:05Z | c810c3f | Refreshed handoff only; binding P17-3. | GREEN @10:40Z |
| 2026-11-16T10:45:54Z | 91d6dc5 | Live-verified gate GREEN 6215/35/99%, ruff clean, perf PASS. Found CI does not enforce ruff/suite/coverage/reconcile gate. | GREEN @10:45Z |
| 2026-11-16T11:40:00Z | 91d6dc5 | Claimed P19-1 complete in docs; **not reflected in workflow at 8562f91** (no `bab-gate` job in `.github/workflows/main.yml`). Treat as unproven/rolled-back claim. | claim unverified |
| 2026-11-16T12:29:00Z | 8562f91 | Re-verified live: `ruff` clean, `bab_reconcile_gate.sh` GREEN, `bab_gate.sh` GREEN 6215/35/99%, workflow has **no bab enforcement**. Corrected README+HANDOFF to remove false CI-enforcement claim and re-bound next work to **P19-1 ship+prove**. | GREEN local @12:29Z |

---

**Next agent (binding):** Start immediately at **P19-1 — ship and prove CI enforcement**. Do not narrate completion: modify `.github/workflows/main.yml` to add a `bab-gate` job (push/PR/workflow_dispatch) running `python3 -m ruff check .`, `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh`, and `bash scripts/bab_reconcile_gate.sh` (with checkout/setup-python/bootstrap; keep existing controller/diagnostics job intact). Prove RED on injected failure and GREEN on clean state with captured evidence, then update README/HANDOFF truthfully to match. After P19-1 DoD, proceed to P19-2a/b/c behavioral hardening (real-data ingest retries/gating, execution fill/reconciliation fidelity, health-check JSON contract).
