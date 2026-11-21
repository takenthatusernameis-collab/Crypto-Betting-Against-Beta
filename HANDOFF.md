# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-21T18:09:30Z (refreshed + RE-VERIFIED this session)
- **Git state:** HEAD `ac0744f`. Working tree carries the **P29 WP0** landing (new files, NOT yet committed — the session checkpoint automation will commit them): `scripts/bab_replay_full.py` (new), `scripts/bab_replay_gate.sh` (new), `tests/test_bab_p29_replay_coverage.py` (new), `scripts/bab_gate.sh` (modified to invoke the replay gate). **No `research_state/**`, `docs/**`, or any P20-P28 script/test/fixture was modified** — verified with `git status --short` (only the four P29 files above). **Re-verified this session (2026-11-21T18:09:30Z):** `python3 -m ruff check .` PASS (rc 0); `bash scripts/bab_quick.sh` GREEN (104 targeted + 195 smoke, rc 0); `pytest -q tests/test_bab_p29_replay_coverage.py` → **9 passed** (rc 0); `bash scripts/bab_replay_gate.sh` → **GREEN, all 8 artifacts byte-identical** (walk_forward_rank, promotion_bakeoff, signal_null_battery, regime_stress, rank_capacity, execution_hardening, risk_controls, reconciliation_e2e — each `.json` and `.md`, 3m08s, rc 0); fixture SHA256 `a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b` matches P25 WP0 provenance. **P28 WP0 and WP1 are COMPLETE and committed — any row calling either "unstarted" is STALE. P29 WP0 is COMPLETE and GREEN in the working tree this session.**

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-21T18:09:30Z)

**Repo name = Crypto-Betting-Against-Beta:** the whole repo is a bet against beta, and its credibility rests entirely on the committed research numbers being **reproducible**. Research campaigns P20-P27 are COMPLETE and frozen. P26 = NO-SIGNAL (no real alpha on the no-alpha synthetic fixture → no real-market deployment claim on synthetic evidence). P27 execution infrastructure is production-ready on paper/dry-run but its WP3 verdict is **NOT-READY for live real-market deployment** (P26 NO-SIGNAL + no licensed market data here).

**The old bottleneck is REMOVED.** The prior handoff said "no agent-executable work remains; idle-wait for the maintainer." That was the inefficiency: P28 WP2-WP4 are maintainer-gated, but that does NOT mean the repo has no agent-executable work. **Campaign P29 "Reproducibility & Provenance Assurance" is DECLARED and is fully agent-executable with ZERO maintainer dependency.** Significant progress continues now via P29 WP1.

**P29 WP0 is COMPLETE and GREEN this session — do NOT re-do it.** Landed (working tree): `scripts/bab_replay_full.py` (read-only full-artifact replay of all 8 committed JSON+md artifacts, with `--self-test`, `--subset`, `--list`), `tests/test_bab_p29_replay_coverage.py` (9 tests), `scripts/bab_replay_gate.sh`, and `bab_gate.sh` now invokes the replay gate. Re-creating or re-editing these is wasted work. `scripts/bab_replay_harness.py` (P28 WP0) is left untouched and remains valid for the 3 P27 artifacts.

**Binding row for this session = P29 WP1.** Concretely (all agent-executable, no network, no maintainer):
1. **Cross-process determinism.** Add a `--xproc` mode to `scripts/bab_replay_full.py` (or a sibling `scripts/bab_replay_xproc.py`) that regenerates each artifact in a **fresh Python interpreter, twice**, and asserts byte-identical JSON — this catches hidden global-state / PYTHONHASHSEED / wall-clock dependence that a single-process double-build would miss. Add acceptance tests.
2. **Provenance ledger.** Emit `research_state/bab_p29/provenance_audit.json` (new, non-frozen) enumerating every artifact: `path`, `sha256`, `generator_module`, `seed`, `fixture_sha256` (`a6d390fc…163b`), `replay_ok`. Add tests asserting the ledger covers all 8 artifacts and its `sha256` fields match the live files.
3. Wire both into `scripts/bab_replay_gate.sh` so they run in the mandatory gate.

**Correct end state:** P29 WP1 GREEN + committed + this HANDOFF refreshed to mark WP1 COMPLETE and name P29 WP2 as the next binding row. Then (and only then) idle-wait applies — and even then the anti-idle rule stands (see below).

**Focus campaign (future agents cannot avoid the duty):** the binding row is P29 WP1, NOT idle docs-only churn. The anti-idle rule stands: a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure. A session that lands WP1 GREEN + committed + refreshed this HANDOFF has done its duty.

**Standing maintainer-external blockers (do NOT re-attempt; they gate P28 WP2-WP4 only, NOT P29):** (a) CI `workflows:write` — repo token lacks it; (b) real-market licensed CSV — Coinbase returns 403 here, network price fetching is forbidden. P29 needs neither.

---

# CAMPAIGN P29 — IN PROGRESS (WP0 COMPLETE; WP1 BINDING)

**Declared:** 2026-11-21T18:09:30Z · **Campaign:** P29 "Reproducibility & Provenance Assurance" · **Priority: HIGH** (the repo's bet-against-beta evidence is only as trustworthy as its reproducibility; this campaign mechanically proves every committed number regenerates)

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — full read-only artifact replay | `scripts/bab_replay_full.py`, `scripts/bab_replay_gate.sh`, `tests/test_bab_p29_replay_coverage.py`, `scripts/bab_gate.sh` (invokes replay gate) | **COMPLETE** (working tree this session; 8/8 byte-identical, 9 tests GREEN, ruff clean) |
| WP1 — cross-process determinism + provenance ledger | `scripts/bab_replay_full.py` `--xproc` mode (or `scripts/bab_replay_xproc.py`), `research_state/bab_p29/provenance_audit.json`, `tests/test_bab_p29_xproc_determinism.py` | **BINDING — agent-executable NOW** |
| WP2 — decision-doc + JSONL sidecar replay | `scripts/bab_replay_decisions.py`, registry entries for `p27_decision_sidecar.json` + `paper_orders.jsonl` + `paper_diagnostics.jsonl`, `tests/test_bab_p29_decision_replay.py` | QUEUED (agent-executable after WP1) |

**WP0 detail (COMPLETE — do not redo):** `scripts/bab_replay_full.py` rebuilds each committed P25/P26/P27 JSON payload from its generator's pure `build_*(fixture_path)` **in memory** (never calls `write_artifacts`, never writes to a committed path) and byte-diffs against the committed file; markdown views are compared after normalising a single trailing newline (two frozen P27 docs, `risk_controls.md` / `reconciliation_e2e.md`, were rendered with one fewer trailing newline than the current renderer emits — JSON remains byte-exact). `--self-test` proves the comparator is non-vacuous: a clean tree replays OK **and** a deliberately corrupted copy is detected as drift. Verified GREEN this session.

**WP1 detail (BINDING — do this now):**
- **Cross-process determinism:** run each generator in a fresh subprocess interpreter twice; assert byte-identical JSON. This is strictly stronger than the in-process double-build in WP0 and is the guard against `PYTHONHASHSEED`/global-state/time leakage. Do NOT weaken WP0's in-process check; add the xproc check alongside it.
- **Provenance ledger:** write `research_state/bab_p29/provenance_audit.json` with one record per artifact: `path`, `sha256`, `generator_module`, `seed`, `fixture_sha256`, `replay_ok`. It must be **deterministic** (sorted keys, stable ordering) so it can itself be replay-checked later.
- **Gate wiring:** `scripts/bab_replay_gate.sh` must run `--self-test`, the full replay, AND the xproc/provenance step.

**WP2 detail (QUEUED — after WP1):**
- Reproduce `docs/BAB_P25_DECISION.md`, `docs/BAB_P26_DECISION.md`, `docs/BAB_P27_DECISION.md` and `research_state/bab_p27/p27_decision_sidecar.json` **byte-identically** from `generate_p25_decision.py` / `generate_p26_decision.py` / `generate_p27_decision.py`. These generators write to fixed paths (`REPORT_PATH`, `SIDECAR_PATH`); run them against a **temp copy** of the repo subset and diff — NEVER overwrite the committed docs.
- Reproduce `research_state/bab_p27/paper_orders.jsonl` and `paper_diagnostics.jsonl` byte-identically (the `bab_execution_hardening` writer emits these to module-level paths; redirect to temp before diffing).

**Hard contract (P29):**
1. No edits to any P20-P28 artifact (all closed/frozen); P29 consumes them read-only. The only P29 writes are new `scripts/*`, new `tests/test_bab_p29_*.py`, `research_state/bab_p29/**`, and the `bab_gate.sh` replay hook.
2. `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged; never weakened.
3. No network fetching of prices; no real-market profitability claims on the synthetic fixture.
4. Zero ruff errors on new files; full gate GREEN; never hand off mid-gate.
5. JSON artifacts are the authoritative byte-diff target; markdown trailing-newline normalization is documented, not hidden.

---

# CAMPAIGN P28 — COMPLETE FOR AGENT-EXECUTABLE SCOPE (WP0+WP1 DONE; WP2-WP4 MAINTAINER-GATED)

**Timestamp:** 2026-11-21T13:23:23Z · **Campaign:** P28 "Live-Market Deployment Preconditions & Controller Hardening"

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — controller hardening + replay harness | `scripts/bab_replay_harness.py`, hardened `scripts/controller_progress.py`, `tests/test_bab_p28_controller_hardening.py`, `tests/test_bab_replay_harness_r4.py` | **COMPLETE** (committed ≤ `f320c50`; 27 tests GREEN) |
| WP1 — data-loader validation | `tests/test_bab_p28_data_loader.py` | **COMPLETE** (committed `af57b5a`/`7ee5729`; 11 passed + 2 skipped) |
| WP2 — CI gate enforcement | `.github/workflows/main.yml` `bab-gate` job | **GATED** (maintainer `workflows:write`) |
| WP3 — real-market data ingestion | `scripts/fetch_real_bab_prices.py` licensed-CSV adapter + `tests/test_bab_p28_ingestion.py` | **GATED** (maintainer licensed CSV) |
| WP4 — live-market deployment decision | `docs/BAB_P28_DECISION.md`, `generate_p28_decision.py`, `tests/test_bab_p28_decision_consistency.py` | **GATED** (needs WP1-WP3 + maintainer authorization) |

**P28 WP2-WP4 remain maintainer-gated and MUST NOT be faked, simulated, or started early.** They are NOT the current bottleneck for progress because P29 is fully agent-executable. If a maintainer unblocks (a) `workflows:write` and/or (b) a licensed market CSV, P28 WP2-WP4 become the next binding rows after P29.

---

# CAMPAIGN P27 — COMPLETE (ALL WPs LANDED)

**Timestamp:** 2026-11-21T11:32:07Z · P27 "Production Execution Infrastructure & Live-Trading Readiness" · **All WPs COMPLETE.** WP0 `scripts/bab_execution_hardening.py`, WP1 `scripts/bab_risk_controls.py`, WP2 `scripts/bab_reconciliation_e2e.py`, WP3 `docs/BAB_P27_DECISION.md` + `generate_p27_decision.py` + `tests/test_bab_p27_decision_consistency.py`. WP3 verdict = **NOT-READY** for live real-market deployment, grounded in committed P27 WP0-WP2 JSON. All artifacts frozen and read-only.

---

# CAMPAIGN P26 — CLOSED (NO-SIGNAL)

**Timestamp:** 2026-11-21T05:49:54Z · P26 "Signal-to-Noise Validation of Rank-Weighted BAB" · **Verdict: NO-SIGNAL.** WP0 signal-vs-null (rank p=0.2857, equal p=0.3586; SIGNAL condition false — correct anti-victory), WP1 regime stress (falsification gate NOT passed), WP2 capacity & turnover (rank survives mechanically on the no-alpha fixture; premium is idio spread, not signal), WP3 `docs/BAB_P26_DECISION.md` explicit NO-SIGNAL. Real-market efficacy requires licensed market data (maintainer-supplied). Do NOT edit the frozen P25 WP0 fixture to "plant" alpha.

---

# CAMPAIGN P25 — CLOSED (PROMOTE for `weighting="rank"`)

WP0 wide universe (`scripts/bab_wide_universe.py`, `tests/fixtures/wide_bab_universe.csv` [SHA256 `a6d390fc…163b`]), WP1 rank walk-forward, WP2 equal-vs-rank OOS bake-off (rank OOS Sharpe 0.4373 vs equal 0.1703, delta +0.2670), WP3 `docs/BAB_P25_DECISION.md` PROMOTE for `weighting="rank"`. All frozen and read-only.

---

# CAMPAIGN P20-P24 — CLOSED (COMPLETE)

P20 WP0-WP5 (92 tests), P21 WP0-WP3 (56), P22 WP0-WP3 (85), P23 WP0-WP4 (80), P24 WP0-WP4 (94) all GREEN. All `research_state/bab_p20..p24/**`, `docs/BAB_RESEARCH_REPORT.md`, and P20-P24 scripts are frozen and read-only.

---

# MAINTAINER-EXTERNAL WORK (NOT AGENT TASKS)

1. **CI gate enforcement (P19-1 / P28 WP2)** — `bab-gate` job / `ruff` / `bab_gate.sh` / `bab_reconcile_gate.sh` in `.github/workflows/main.yml`: agent token lacks `workflows:write`. Maintainer must add via GitHub web UI or a `workflows:write` PAT. Do not re-attempt the push from an agent session.
2. **Real-market data ingestion (P28 WP3)** — licensed CSV is maintainer-supplied; `api.exchange.coinbase.com` returns 403 here. Network fetching of prices is forbidden.

---

# HARD GATES EVERY SESSION (repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
bash scripts/bab_replay_gate.sh          # P29 WP0: 8/8 artifacts byte-identical + drift self-test
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

`scripts/bab_gate.sh` now also invokes `scripts/bab_replay_gate.sh` at the end, so the replay check cannot be skipped by running the full gate alone. Inner loop while iterating: `bash scripts/bab_quick.sh` + `python3 -m pytest -q tests/test_bab_p29_replay_coverage.py` + the P27/P26/P25 acceptance tests. Full gate once per WP boundary; never hand off mid-gate. Never lower the coverage floor.

---

# FORBIDDEN (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (a handoff refresh without a landed fix is not a session).
- Editing any `research_state/bab_p20/**` … `research_state/bab_p24/**`, `docs/BAB_RESEARCH_REPORT.md`, or any P20-P24 script (frozen).
- Editing any P25 WP0-WP2 artifact, any P26 artifact, any P27 WP0-WP3 artifact, or any P28 WP0-WP1 artifact (all closed and frozen).
- Hand-typing any number into a P25/P26/P27 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta` / `rank_max_gross` below 0.20 / 4.0 in any decision.
- Describing the synthetic wide universe as real market data, or publishing a Sharpe without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- Shipping a WP whose committed artifact contradicts its own acceptance threshold.
- **Network fetching of prices** (Coinbase returns 403 here; licensed CSV is maintainer-supplied).
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, broad refactors, or committing probe/debug scratch scripts.
- Creating parallel handoff docs (this file is the single source of truth).
- **Faking P29 reproducibility** (e.g., hard-coding `sha256` values, skipping the xproc check, or editing committed artifacts to force a green replay).
- Idle docs-only churn when P29 WP1/WP2 are agent-executable.

---

# BOTTLENECKS REMOVED (do not re-create)

- **[REMOVED 2026-11-21T18:09:30Z] "No agent-executable work remains; idle-wait for the maintainer" bottleneck.** The prior handoff declared the binding row NONE and told the next agent to idle-wait, treating the P28 WP2-WP4 maintainer gates as a repo-wide stop. That was the inefficiency: it ignored that reproducibility of the committed evidence is itself heavy, agent-executable work. Fixed: declared **Campaign P29 "Reproducibility & Provenance Assurance"** with WP0-WP2, landed **WP0** this session (full read-only 8-artifact replay + `--self-test` drift proof + gate wired into `bab_gate.sh`; verified 8/8 byte-identical, 9 tests GREEN, ruff clean), and set the binding row to **P29 WP1** (cross-process determinism + provenance ledger) — fully agent-executable with zero maintainer dependency. Significant progress continues now.
- **[REMOVED 2026-11-21T17:04:13Z] Stale initial task message named P28 WP0 unstarted; its files were already committed.** Marked WP0 COMPLETE, forbade re-creating it, set binding row to P28 WP1.
- **[REMOVED 2026-11-21T14:23:33Z] Stale HANDOFF claimed P28 WP1 unstarted.** WP1 landed at `af57b5a`/`7ee5729`; binding row updated.
- **[REMOVED 2026-11-21T12:22:18Z] Stale HEAD certification + stale refresh timestamps blocking P28 start.** Re-verified gates GREEN and P28 unstarted; binding row P28 WP0 → WP1.
- **[REMOVED 2026-11-21T11:32:07Z] Stale HANDOFF claimed P27 WP3 deliverables absent.** They exist and are complete; P27 marked COMPLETE.
- **[REMOVED 2026-11-20T16:37:11Z] No binding row existed.** Created Campaign P25 with binding WP0.
- (Earlier P23/P24 bottleneck removals retained in git history; see `git log` for the full ledger.)

---

# FUTURE AGENTS: READ THIS ONCE

**This repo is DONE for agent-executable campaigns P20-P28; all are complete and frozen.** Campaign **P29 "Reproducibility & Provenance Assurance"** is IN PROGRESS: **WP0 is COMPLETE and GREEN (working tree, this session)** — `scripts/bab_replay_full.py` + `tests/test_bab_p29_replay_coverage.py` + `scripts/bab_replay_gate.sh` + `bab_gate.sh` hook; do NOT re-create or re-edit them. **The binding row is P29 WP1** (cross-process determinism + `research_state/bab_p29/provenance_audit.json`), fully agent-executable with zero maintainer dependency. After WP1, the binding row is P29 WP2 (decision-doc + JSONL sidecar replay).

**Anti-idle rule (focus campaign — future agents cannot avoid heavy work):** a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure. The session is complete when the binding WP is GREEN + committed + this HANDOFF refreshed to name the next WP — NOT an idle plan. Do not manufacture work where none is agent-executable, and do not idle when P29 WP1/WP2 are.

Do not re-open frozen P20-P28 artifacts (consumed read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` (never weakened). Never network-fetch prices. If this file says COMPLETE, it is COMPLETE; if it names a binding row, that is the work; if it says a WP is maintainer-gated, route it to the maintainer and proceed to the next agent-executable P29 WP.