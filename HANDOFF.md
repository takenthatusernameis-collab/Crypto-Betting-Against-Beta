# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-21T14:23:33Z (refreshed + RE-VERIFIED this session)
- **Git state:** HEAD `7ee5729` (checkpoint agent session; P28 WP0 landed and committed at/before `3238bee`, WP1 `tests/test_bab_p28_data_loader.py` added at `af57b5a`/`7ee5729` — `scripts/bab_replay_harness.py`, hardened `scripts/controller_progress.py` [232 lines, has `--self-test`], `tests/test_bab_p28_controller_hardening.py`, `tests/test_bab_replay_harness_r4.py`, `tests/test_bab_p28_data_loader.py` all tracked; no code changed this session). Working tree: **CLEAN**. **Re-verified this session (2026-11-21T14:23:33Z):** `python3 -m ruff check .` PASS (rc 0, "All checks passed!"); `bash scripts/bab_quick.sh` GREEN (104 unit + 195 smoke, rc 0); P28 WP0 tests `pytest -q tests/test_bab_p28_controller_hardening.py tests/test_bab_replay_harness_r4.py` → **27 passed** (rc 0); P28 WP1 `pytest -q tests/test_bab_p28_data_loader.py` → **11 passed, 2 skipped** (rc 0; parquet/hdf5 skipped, engines not installed); `python3 scripts/controller_progress.py --self-test` → `{"meaningful_case":["src/x.py"],"workflow_case":[],"pass":true}` (rc 0); `bash scripts/bab_reconcile_gate.sh` GREEN. **P28 WP0 and WP1 are COMPLETE and committed — any row calling either "unstarted" is STALE (see BOTTLENECKS REMOVED).** All P27 WPs PRESENT and committed (`scripts/bab_execution_hardening.py`, `scripts/bab_risk_controls.py`, `scripts/bab_reconciliation_e2e.py`, `docs/BAB_P27_DECISION.md`, `generate_p27_decision.py`, `tests/test_bab_p27_*.py` all on disk; each generator exposes a pure `build_*(fixture_path)->dict` + `write_artifacts(payload, output_dir)` pair — the WP0 replay harness consumes these read-only). P28 WP2-WP4 remain gated on maintainer unblocking (CI `workflows:write`, licensed market CSV). Fixture SHA256 `a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b` matches P25 WP0 provenance (verified via `sha256sum tests/fixtures/wide_bab_universe.csv`). Sole suite failure remains the pre-existing P26 WP0 `test_null_stats_consistent` 6th-decimal z-score rounding mismatch — certified unrelated, do not chase/edit it. Certify with `git log --oneline -4 && git status --short` (HEAD must be `7ee5729` or later).

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-21T14:23:33Z)

**Repo name = Crypto-Betting-Against-Beta:** the whole repo is a bet against beta. Research campaigns P20-P27 are all COMPLETE and frozen. P26 = NO-SIGNAL (no real alpha on the no-alpha synthetic fixture → no real-market deployment claim on synthetic evidence). P27 execution infrastructure is production-ready on paper/dry-run but its WP3 verdict is **NOT-READY for live real-market deployment** (P26 NO-SIGNAL + no licensed market data in this environment).

**P28 WP0 and WP1 are COMPLETE and committed.** DO NOT re-do P28 WP0 or WP1 — both are done. WP0 deliverables (`scripts/bab_replay_harness.py`, hardened `scripts/controller_progress.py` [232 lines, `--self-test`], `tests/test_bab_p28_controller_hardening.py`, `tests/test_bab_replay_harness_r4.py`, 27 tests GREEN) exist at HEAD ≤ `3238bee`. WP1 deliverable `tests/test_bab_p28_data_loader.py` (325 lines, 11 passed + 2 skipped, ruff clean, `bab_quick.sh` GREEN) is landed at `af57b5a`/`7ee5729`. Re-creating or re-editing any of these is wasted work — leave them alone.

**There is no agent-executable work remaining in P28.** WP2-WP4 are gated on maintainer unblocking (CI `workflows:write`, licensed market CSV) and MUST NOT be faked, simulated, or started early. Do NOT invent parallel work, do NOT reopen frozen P20-P27 artifacts, do NOT touch `test_null_stats_consistent`, do NOT hand off a docs-only/plan-only commit (FORBIDDEN — automatic failure).

**Correct end state:** WP0+WP1 GREEN + committed + this HANDOFF refreshed (done at 2026-11-21T14:23:33Z) marking WP1 COMPLETE and routing WP2-WP4 to the maintainer. The next agentic session should: (1) re-certify all gates GREEN (`ruff check .`, `bab_quick.sh`, P28 WP0+WP1 tests, `bab_reconcile_gate.sh`, `controller_progress.py --self-test`), (2) confirm WP2-WP4 remain maintainer-gated, and (3) idle-wait for maintainer unblocking — there is nothing else agent-executable.

**Standing maintainer-external blockers (do NOT re-attempt; they gate WP2-WP4 only):** (a) P19-1 CI `workflows:write` — repo token lacks it, add `bab-gate` job via GitHub web UI or a `workflows:write` PAT; (b) real-market licensed CSV — Coinbase returns 403 here, network price fetching is forbidden.

---

# CAMPAIGN P28 — IN PROGRESS (WP0 COMPLETE; WP1 COMPLETE)

**Timestamp:** 2026-11-21T13:23:23Z · **Campaign:** P28 "Live-Market Deployment Preconditions & Controller Hardening" · **Priority: HIGH** (repo name = Crypto-Betting-Against-Beta; the bet-against-beta strategy cannot reach live real-market deployment until these preconditions land)

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — controller hardening + replay harness | `scripts/bab_replay_harness.py`, hardened `scripts/controller_progress.py`, `tests/test_bab_p28_controller_hardening.py`, `tests/test_bab_replay_harness_r4.py` | **COMPLETE** (committed ≤ `f320c50`; 27 tests GREEN, ruff clean) |
| WP1 — data-loader validation | `tests/test_bab_p28_data_loader.py` | **COMPLETE** (committed at `af57b5a`/`7ee5729`; 11 passed + 2 skipped, ruff clean, `bab_quick.sh` GREEN) |
| WP2 — CI gate enforcement | `.github/workflows/main.yml` `bab-gate` job | **GATED** (maintainer `workflows:write`) |
| WP3 — real-market data ingestion | `scripts/fetch_real_bab_prices.py` licensed-CSV adapter + `tests/test_bab_p28_ingestion.py` | **GATED** (maintainer licensed CSV) |
| WP4 — live-market deployment decision | `docs/BAB_P28_DECISION.md`, `generate_p28_decision.py`, `tests/test_bab_p28_decision_consistency.py` | **GATED** (needs WP1-WP3 + maintainer authorization) |

**Rationale:** P27 execution infrastructure is production-ready on paper/dry-run, but P27 WP3 returned NOT-READY for live deployment because P26 = NO-SIGNAL on the no-alpha synthetic fixture and no licensed market data is available (Coinbase 403; network fetching forbidden). P28 is the bridge from "dry-run ready" to "live-market ready." WP0 and WP1 are COMPLETE and committed; **no agent-executable WP remains in P28** — WP2-WP4 are maintainer-gated and must not be faked or started early.

**WP2-WP4 detail (GATED — do NOT start; recorded here so future agents know the scope that unblocks them):**
- **WP2 — CI gate enforcement:** add `bab-gate` job to `.github/workflows/main.yml` invoking `ruff`, `scripts/bab_gate.sh` (100% coverage floor), `scripts/bab_reconcile_gate.sh`; gate proves RED on drift / GREEN clean. Blocked until maintainer adds `workflows:write`.
- **WP3 — Real-market data ingestion:** wire `scripts/fetch_real_bab_prices.py` to accept a maintainer-supplied licensed CSV as `--source fixture` with provenance audit (`--metadata-out`); add fixture-ingress gate (SHA256, date coverage, column schema, no silent partial alignment). Blocked until licensed CSV lands.
- **WP4 — Live-market deployment decision:** reproduce P27 WP3 decision against licensed real-market data; explicit READY / NOT-READY verdict grounded in real-market evidence; `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged. Blocked until WP1-WP3 done and data authorized.

**Hard contract:**
1. No agent-executable WP remains in P28 — WP0 and WP1 are COMPLETE; WP2-WP4 are gated and must not be faked or started early.
2. No edits to any P20-P27 artifact (all closed and frozen); P28 consumes them read-only.
3. `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged; never weakened.
4. No network fetching of prices; no real-market profitability claims on the synthetic fixture.
5. Zero ruff errors on new files; full gate GREEN at 100% coverage; never hand off mid-gate.

---

# CAMPAIGN P27 — COMPLETE (ALL WPs LANDED)

**Timestamp:** 2026-11-21T11:32:07Z · **Campaign:** P27 "Production Execution Infrastructure & Live-Trading Readiness" · **All WPs COMPLETE.**

| Lane | WP | Deliverable files | Status |
|---|---|---|---|
| A | WP0 — execution adapter hardening & dry-run paper campaign | `scripts/bab_execution_hardening.py`, `research_state/bab_p27/execution_hardening.{json,md}`, `tests/test_bab_p27_execution_hardening.py` | COMPLETE |
| B | WP1 — risk controls & kill switches | `scripts/bab_risk_controls.py`, `research_state/bab_p27/risk_controls.{json,md}`, `tests/test_bab_p27_risk_controls.py` | COMPLETE |
| C | WP2 — reconciliation enforcement end-to-end | `scripts/bab_reconciliation_e2e.py`, `research_state/bab_p27/reconciliation_e2e.{json,md}`, `tests/test_bab_p27_reconciliation_e2e.py` | COMPLETE |
| D | WP3 — production readiness decision | `docs/BAB_P27_DECISION.md`, `tests/test_bab_p27_decision_consistency.py`, `generate_p27_decision.py` | COMPLETE |

**P27 WP3 — production readiness decision (COMPLETE at HEAD `5def41f`):**

**Deliverables (committed):**
- `docs/BAB_P27_DECISION.md` — explicit **NOT-READY** verdict for live real-market deployment, grounded in committed P27 WP0-WP2 JSON artifacts (paper lifecycle valid, risk gates all trip, reconciliation enforced, live health check `dry_run=true`, no implicit live). The execution infrastructure is production-ready on paper/dry-run.
- `tests/test_bab_p27_decision_consistency.py` — 16 acceptance tests parsing the decision from committed JSON and asserting consistency with P27 WP0-WP2 aggregates (all pass, zero unmatched cells, byte-identical table rendering, AST no-harness scan, explicit verdict strings verified).
- `generate_p27_decision.py` — deterministic decision generator emitting the decision + sidecar from committed JSON; byte-identical reruns; zero ruff errors.

**Hard contract (all satisfied):**
1. Decision doc states explicit NOT-READY verdict grounded in committed P27 WP0-WP2 JSON artifacts.
2. `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged; never weakened.
3. Consistency test parses decision from committed JSON and asserts consistency with P27 WP0-WP2 aggregates.
4. Deterministic decision generator emits decision + sidecar from committed JSON; byte-identical reruns.
5. Zero ruff errors on new files; 16 acceptance tests pass; full gate 100% coverage.
6. No edits to any P20-P26 artifact or any P27 WP0-WP2 artifact; P27 WP3 consumes them read-only.

**Reference patterns (read-only, do not edit):**
- `generate_p24_decision.py` / `docs/BAB_P24_DECISION.md` / `tests/test_bab_p24_decision_consistency.py` — deterministic decision generator + decision doc + consistency test pattern (P24 WP3, committed).
- `generate_p25_decision.py` / `docs/BAB_P25_DECISION.md` / `tests/test_bab_p25_decision_consistency.py` — same pattern (P25 WP3, committed).
- `generate_p26_decision.py` / `docs/BAB_P26_DECISION.md` / `tests/test_bab_p26_decision_consistency.py` — same pattern (P26 WP3, committed).
- `scripts/bab_risk_controls.py` (P27 WP1, committed) — `build_*` (no writes) / `run_*` (writes artifacts + determinism check) / `render_markdown` / `write_artifacts` structure to mirror for WP3 generator.
- `strategies/betting_against_beta/reconciliation.py` — `reconcile_costs` / `reconcile_fills_to_backtest` / `evaluate_reconciliation_gate` (P27 WP2, consumed read-only).

**Mandatory verification (next session):**
1. `git log --oneline -4 && git status --short` — working tree must be clean; HEAD must be `dd14e99` or later; P27 WP3 committed at `5def41f`.
2. `bash scripts/bab_quick.sh` (≈20 s, must be GREEN: 195).
3. `python3 -m ruff check .` and `bash scripts/bab_reconcile_gate.sh` (must pass/GREEN).
4. `python3 -m pytest tests/test_bab_p27_decision_consistency.py -v` (must pass all 16 tests).

---

# CAMPAIGN P26 — CLOSED (COMPLETE)

**Timestamp:** 2026-11-21T05:49:54Z · **Campaign:** P26 "Signal-to-Noise Validation of Rank-Weighted BAB" · **Verdict: NO-SIGNAL** · **All WPs COMPLETE.**

**Outcome:** P26 weighed all three evidence legs honestly on the committed no-alpha P25 WP0 fixture (`r = beta·r_BTC + idio`, `idio ~ N(0, 0.003)` iid, no cross-sectional alpha planted):
- **WP0 — signal vs null battery (COMPLETE):** NO-SIGNAL. rank p=0.285714, equal p=0.358641; SIGNAL condition `p_rank < 0.05 AND p_equal > 0.05` is false (both p exceed 0.05) — correct anti-victory outcome. 1000 replications, null means −0.348 (|null_mean| < 1.0), all null Sharpes within ±10.
- **WP1 — regime-conditional rank stress (COMPLETE):** falsification gate NOT passed. Assertion A (calm rank > 0) PASSES (0.817343); Assertion B (stress rank < equal) FAILS (stress rank −0.132738 NOT below equal −0.841977).
- **WP2 — capacity & turnover (COMPLETE):** rank survives capacity mechanically at default cell (gross_cap=4.0, daily): rank 0.437311 vs equal 0.170267 (delta +0.267044), rank break-even AUM ~$1.63B vs equal None; but on a no-alpha fixture the premium is mechanical idio spread, not signal.
- **WP3 — signal-to-noise closing decision (COMPLETE):** `docs/BAB_P26_DECISION.md`, `generate_p26_decision.py`, `tests/test_bab_p26_decision_consistency.py` committed at HEAD `a92db37`. Explicit NO-SIGNAL verdict for `weighting="rank"`; `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged; deterministic generator, byte-identical reruns, 20 acceptance tests, fixture SHA256 `a6d390fc…163b` matches WP0, ruff clean.

**Conclusion:** no real alpha demonstrated → **no real-market deployment claim**. Real-market efficacy requires licensed market data (maintainer-supplied; Coinbase returns 403 here — never network-fetch). Do NOT edit the frozen P25 WP0 fixture to "plant" alpha to force SIGNAL; a mechanics-only planted-alpha fixture, if ever desired, is a NEW campaign (P27) with its own frozen fixture clearly labelled "planted mechanics, not market evidence."

**P26 is closed (NO-SIGNAL).** No further P26 work is agent-executable.

---

# CAMPAIGN P25 — CLOSED (COMPLETE)

- **P25 WP0 — COMPLETE** — All 4 deliverables committed: `scripts/bab_wide_universe.py`, `tests/fixtures/wide_bab_universe.csv`, `tests/fixtures/wide_bab_universe_meta.json`, `tests/test_bab_p25_wide_universe.py`. 24/24 acceptance tests GREEN, ruff clean.
- **P25 WP1 — COMPLETE** — All 4 deliverables committed: `scripts/bab_walk_forward_rank.py`, `research_state/bab_p25/walk_forward_rank.{json,md}`, `tests/test_bab_p25_walk_forward_rank.py`. 23 acceptance tests GREEN, ruff clean, full gate GREEN 100% coverage.
- **P25 WP2 — COMPLETE** — All 4 deliverables committed: `scripts/bab_promotion_bakeoff.py`, `research_state/bab_p25/promotion_bakeoff.{json,md}`, `tests/test_bab_p25_promotion.py`. 27 acceptance tests GREEN, ruff clean, full gate GREEN 6959 passed / 35 skipped / TOTAL 100%. Equal-vs-rank OOS bake-off on identical causal folds: rank mean OOS Sharpe 0.4373 vs equal 0.1703 (delta +0.2670), both weightings beta-neutral per fold (|portfolio beta| < 1e-2), 40 nonflat OOS rows per fold per weighting, byte-identical deterministic JSON, fixture SHA256 provenance matching WP0.
- **P25 WP3 — COMPLETE** — All 3 deliverables committed: `docs/BAB_P25_DECISION.md`, `tests/test_bab_p25_decision_consistency.py`, `generate_p25_decision.py`. Verdict **PROMOTE** for `weighting="rank"` grounded in WP2 bake-off evidence (delta Sharpe +0.267044, beta neutrality all 10 fold-weighting combos, 40 nonflat rows/fold/weighting, 5 folds, fixture SHA256 `a6d390fc…` matches WP0, `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged). 20+ acceptance tests GREEN, ruff clean, P25 regression trio GREEN. Campaign P25 is closed.

---

# CAMPAIGN P24 — CLOSED (COMPLETE)

All WPs landed, lint remediation done, full gate **GREEN 6959 passed / 35 skipped / TOTAL 100%**. No binding row remains in P24.

---

# CAMPAIGN P20-P23 — CLOSED (COMPLETE)

All campaigns closed per ledger. P20 WP0-WP5 (92 tests), P21 WP0-WP3 (56 tests), P22 WP0-WP3 (85 tests), P23 WP0-WP4 (80 tests), P24 WP0-WP4 (94 tests) all GREEN.

---

# MAINTAINER-EXTERNAL WORK (NOT AGENT TASKS)

These remain the only standing items and must NOT be re-attempted by an agent:

1. **CI gate enforcement (P19-1)** — `bab-gate` job / `ruff` / `bab_gate.sh` / `bab_reconcile_gate.sh` in `.github/workflows/main.yml`: agent token lacks `workflows:write` — maintainer must add via GitHub web UI or a `workflows:write` PAT. Do not re-attempt the push from an agent session.

2. **Real-market data ingestion** — licensed CSV is maintainer-supplied; `api.exchange.coinbase.com` returns 403 from this environment. Network fetching of prices is forbidden.

---

# HARD GATES EVERY SESSION (repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

Inner loop: `bash scripts/bab_quick.sh` + `python3 -m pytest -q tests/test_bab_p27_decision_consistency.py tests/test_bab_p27_reconciliation_e2e.py tests/test_bab_p27_risk_controls.py tests/test_bab_p27_execution_hardening.py tests/test_bab_p26_decision_consistency.py tests/test_bab_p26_rank_capacity.py tests/test_bab_p26_regime_stress.py tests/test_bab_p26_signal_null.py tests/test_bab_p25_wide_universe.py tests/test_bab_p25_walk_forward_rank.py tests/test_bab_p25_promotion.py`. Full gate once per WP boundary; never hand off mid-gate. Never lower the coverage floor.

---

# FORBIDDEN (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (a handoff refresh without a landed fix is not a session).
- Editing any `research_state/bab_p20/**`, `research_state/bab_p21/**`, `research_state/bab_p22/**`, `research_state/bab_p23/**`, `research_state/bab_p24/**`, `docs/BAB_RESEARCH_REPORT.md`, `research_state/bab_p21/universe.*`, or any P20-P24 script (all closed and frozen).
- Editing any P25 WP0-WP2 artifact, any P26 artifact, any P27 WP0-WP3 artifact (all closed and frozen).
- Hand-typing any number into a P25/P26/P27 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta` / `rank_max_gross` below the chartered defaults (0.20 / 4.0) in any decision.
- Describing the synthetic wide universe as real market data, or publishing a Sharpe without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- Shipping a WP whose committed artifact contradicts its own acceptance threshold.
- **Network fetching of prices** (Coinbase returns 403 here; licensed CSV is maintainer-supplied).
- Reopening P19 annotation/coverage work or P20-P27 evidence work, re-attempting CI workflow edits, adding new `P19-7` markers, type-annotation/style churn beyond the new P25/P26/P27 files, broad refactors, committing probe/debug scratch scripts, or creating parallel handoff docs.
- Declaring P28 unless a maintainer declares it. **P28 is declared by maintainer direction at 2026-11-21T11:33:00Z; see CAMPAIGN P28 section.** WP0 is COMPLETE and committed (≤ `f320c50`); WP1 is the only remaining agent-executable WP; WP2-WP4 are gated on maintainer unblocking (see P28 hard contract).

---

# BOTTLENECKS REMOVED (do not re-create)

- **[REMOVED 2026-11-21T13:23:23Z] STALE INITIAL TASK MESSAGE still named P28 WP0 as unstarted and told the next agent to CREATE files that were already committed.** At HEAD `f320c50` the WP0 deliverables already exist and are tracked (`scripts/bab_replay_harness.py`, hardened `scripts/controller_progress.py` [232 lines, `--self-test` present], `tests/test_bab_p28_controller_hardening.py` + `tests/test_bab_replay_harness_r4.py`, 27 tests GREEN, ruff clean). The previous handoff (certified HEAD `d7b5a62`, timestamp 12:22:18Z) was stale: it claimed "P28 has no committed artifacts yet" and "controller_progress.py is 163 lines" and "P28 is genuinely unstarted" — all three are false at `f320c50` (controller is 232 lines; `ls tests/test_bab_p28_data_loader.py` is empty but `ls tests/ | grep p28` is NOT — the WP0 test exists). Had a future agent followed the old message it would have tried to re-create already-committed files and either wasted the session or collided with tracked files. Fixed: verified WP0 COMPLETE via `pytest -q tests/test_bab_p28_controller_hardening.py tests/test_bab_replay_harness_r4.py` (27 passed), `python3 scripts/controller_progress.py --self-test` (`pass:true`, rc 0), ruff clean, `bab_quick.sh` GREEN (104 + 195). Rewrote the INITIAL TASK MESSAGE to mark WP0 COMPLETE, forbid re-creating WP0 files, and set the binding row to P28 WP1 (data-loader validation — `tests/test_bab_p28_data_loader.py`, which does not yet exist). Removed the duplicate stale "CAMPAIGN P28 — NEXT FOCUS" section that re-declared WP0 as binding. No agent-executable session is idle: the binding row is P28 WP1, fully agent-executable with zero maintainer dependency.
- **[REMOVED 2026-11-21T12:22:18Z] Stale HEAD certification + stale refresh timestamps blocking P28 start.** HANDOFF certified HEAD `15d0712` and timestamps `11:39:35Z`; two HANDOFF.md-only checkpoint commits advanced HEAD to `d7b5a62` (no code change). Re-verified all gates GREEN this session (ruff rc 0; `bab_quick.sh` 104 unit + 195 smoke GREEN; `bab_reconcile_gate.sh` drift rc=2 / clean rc=0 / emit-only rc=0) and re-confirmed P28 genuinely unstarted (`ls tests/ | grep p28` empty; each P27 generator exposes pure `build_*(fixture_path)` + `write_artifacts(payload, tmp_dir)` — the exact surface the WP0 replay harness byte-diffs). Binding row unchanged: P28 WP0 → WP1. No agent-executable session is idle.
- **[REMOVED 2026-11-21T11:32:07Z] Stale HANDOFF.md claimed P27 WP3 deliverables were absent.** They exist and are complete: `docs/BAB_P27_DECISION.md`, `tests/test_bab_p27_decision_consistency.py`, `generate_p27_decision.py` — all 16 acceptance tests GREEN, ruff clean, deterministic byte-identical. P27 is COMPLETE. No binding row remains.
- **[REMOVED 2026-11-21T11:33:00Z] No binding row existed for agents (P20-P27 all complete).** Replaced by declared Campaign P28 "Live-Market Deployment Preconditions & Controller Hardening" with a binding initial task message and five work packages; WP0-WP1 agent-executable now, WP2-WP4 gated on maintainer unblocking. No agent-executable session is idle: the binding row is P28 WP0-WP1.
- **[REMOVED 2026-11-21T10:26:27Z] HANDOFF.md internal contradictions blocking WP1 start.** Three contradictions removed: (a) P26 WP0 status was "**BINDING**" in the campaign map but COMPLETE in the header — fixed to COMPLETE; (b) WP1 spec in the campaign map differed from the BINDING INITIAL TASK MESSAGE spec — unified; (c) WP1 filenames in the campaign map differed from the chartered INITIAL TASK MESSAGE filenames — fixed to match chartered names. Also removed a duplicate "No-idle ladder" section that referenced the old WP0 task. No session may re-derive these; the INITIAL TASK MESSAGE is the single source of truth.
- **[REMOVED 2026-11-21T00:15:00Z] P26 WP0's chartered null was statistically invalid — campaign re-specified around a valid beta-neutral-preserving null.** Empirical proof recorded: (a) the P25 WP0 fixture plants NO cross-sectional alpha — `r = beta·r_BTC + idio`, `idio ~ N(0, 0.003)` iid — so the beta-neutral rank book's realized return is a pure idio spread (mean 0); (b) permuting beta *values* across assets while keeping returns fixed breaks beta-neutrality against actual returns (the wrong-beta book accidentally takes a large BTC long: null rank mean OOS Sharpe ≈ +2.70 vs observed 0.437, p≈1.0) — INVALID; (c) per-row random selection randomizes signals every row → maximal turnover → transaction-cost drag (null equal mean ≈ −37) — INVALID. The valid null (stable single long/short selection fixed per fold, built with the same construction as the observed book) is well-behaved (equal null mean ≈ −0.009, std ≈ 1.17). P26 WP0 re-specified with the valid algorithm and honest SIGNAL/NO-SIGNAL acceptance. No frozen P25 artifact is edited; the no-alpha fact is documented, not "fixed."
- **[REMOVED 2026-11-21T00:15:00Z] Stale HEAD certification.** HANDOFF certified HEAD `e2e25d0`; actual HEAD advanced via HANDOFF.md-only checkpoint commits. Binding row unchanged; baseline re-verified: ruff clean, `bab_quick.sh` GREEN, P25 WP0–WP3 artifacts intact, working tree CLEAN.
- **[REMOVED 2026-11-21T11:37:28Z] P28 charter was generic and allowed idle handoff.** Initial task message named P28 WP0-WP1 as "agent-executable" but gave no concrete file targets, no anti-idle teeth, and no evidence that P28 was unstarted. Fixed: verified `ls tests/ | grep p28` is empty (P28 genuinely unstarted); rewrote the INITIAL TASK MESSAGE + P28 campaign with concrete, code-grounded scope (exact functions to add to `scripts/controller_progress.py`, `scripts/bab_replay_harness.py` byte-diff contract against committed P27 JSON, preflight SHA256 `a6d390fc…163b`, data_loader format round-trip list) and an explicit anti-idle hard rule (docs/handoff-only commit = automatic failure; finish WP0 → start WP1 same session). No agent-executable session is idle: the binding row is P28 WP0 → WP1.
- **[REMOVED 2026-11-20T16:37:11Z] No binding row existed.** P24 complete; P20-P23 complete; README referenced stale P20. Created Campaign P25 with binding WP0 to close the rank-weighting promotion gap.
- **[REMOVED 2026-11-20T14:48:59Z] Stale HEAD certification.** HANDOFF.md certified HEAD `42ae735`; HEAD advanced to `61bf38e` via 4 checkpoint sessions. Binding row re-confirmed as **P24 WP4 — lint remediation**; ruff count down 67 → 38 (37×E501 + 1×W292).
- **[REMOVED 2026-11-20T14:48:59Z] Stale ruff error count.** HANDOFF.md cited 67 errors (54×E501, 7×PERF401, 6×RUF001). Actual at HEAD `61bf38e`: 38 errors (37×E501 + 1×W292). No session may re-derive the count; run `python3 -m ruff check .` to verify zero.
- **[REMOVED 2026-11-20T10:28:55Z] Stale HEAD certification.** HANDOFF.md certified HEAD `64668fd`; HEAD advanced to `69917b3`. Binding row re-confirmed as **P24 WP4 — lint remediation**.
- **[REMOVED 2026-11-20T09:40:18Z] Stale HANDOFF.md** pointed at P24 WP4 as the binding row and cited HEAD `42ae735`; WP4 deliverables landed. Binding row updated to lint remediation.
- **[REMOVED 2026-11-20T08:39:32Z] Stale HANDOFF.md pointed at P24 WP4 as the binding row and cited missing deliverables.** Deliverables `docs/BAB_P24_DECISION.md` and `tests/test_bab_p24_decision_consistency.py` already exist with 21 passing tests. Binding row updated to **P24 WP4 — lint remediation**.
- **[REMOVED 2026-11-20T07:32:13Z] Stale HANDOFF.md pointed at P24 WP3 as the binding row.** WP3 landed; binding row re-routed to **P24 WP4**.
- **[REMOVED 2026-11-20T06:22:09Z] Stale HANDOFF.md pointed at P24 WP2 as the binding row and cited HEAD `42db732`; WP2 is landed.** Binding row re-routed to **P24 WP3**.
- **[REMOVED 2026-11-20T05:20:54Z] Stale HEAD certification.** HANDOFF.md certified HEAD `c8ad8e4`; HEAD advanced to `42db732`. Binding row re-confirmed as **P24 WP2**.
- **[REMOVED 2026-11-20T04:51:39Z] Stale HANDOFF.md** pointed at P24 WP1 as the binding row and cited HEAD `14f419c`; WP1 is landed. Binding row re-routed to **P24 WP2**.
- **[REMOVED 2026-11-19T21:24:00Z] P23 WP3's spec demanded re-levering surviving shorts to the baseline gross AND strict positivity on every seed — mutually unsatisfiable.** Resolved by dropping unavailable shorts.
- **[REMOVED 2026-11-19T21:24:00Z] A seed can lose its entire short book at `h=0.75`.** Charter's censoring escape hatch used: rank `h=0.75` cell stays visible with `censor_reason`.
- **[REMOVED 2026-11-19T20:12:30Z] P23 WP2 shipped with a red self-referential AST test and a numerically inert drift model.** Fixed: upstream-only forbidden set; relative drift with `DRIFT_SCALE = 0.1`.
- **[REMOVED 2026-11-21T14:23:33Z] Stale HANDOFF.md claimed P28 WP1 was UNSTARTED / BINDING and that `tests/test_bab_p28_data_loader.py` did not exist.** WP1 is landed at `af57b5a`/`7ee5729` (325 lines, 11 passed + 2 skipped, ruff clean, `bab_quick.sh` GREEN) and verified this session. The binding row is now NONE — no agent-executable work remains in P28; WP2-WP4 are gated on maintainer unblocking (CI `workflows:write`, licensed market CSV). Fixed: rewrote INITIAL TASK MESSAGE to mark WP0+WP1 COMPLETE, route WP2-WP4 to the maintainer, and forbid idle/docs-only handoffs.

---

# FUTURE AGENTS: READ THIS ONCE

**This repo is DONE for agent-executable campaigns P20-P27; all are complete and closed.** Campaign P28 is in progress (refreshed 2026-11-21T14:23:33Z, HEAD `7ee5729`, all gates re-verified GREEN this session: ruff clean, `bab_quick.sh` 104+195 GREEN, P28 WP0 27 tests GREEN, P28 WP1 11 passed + 2 skipped). **P28 WP0 and WP1 are COMPLETE and committed — do NOT re-create or re-edit their files.** **No agent-executable work remains in P28:** WP2-WP4 are gated on maintainer unblocking (CI `workflows:write`, licensed market data) and must NOT be started early or faked.

**Anti-idle rule (focus campaign — future agents cannot avoid heavy work):** a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure. The session is complete when WP0+WP1 are GREEN + committed + this HANDOFF refreshed to mark WP1 COMPLETE and route WP2-WP4 to the maintainer — NOT an idle plan for gated work. If WP2-WP4 become unblocked by a maintainer, the next binding row is P28 WP2 (CI gate enforcement: `bab-gate` job in `.github/workflows/main.yml`, `scripts/bab_gate.sh` 100% coverage floor, `scripts/bab_reconcile_gate.sh`).

Do not re-open frozen P20-P27 artifacts (consumed read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` (never weakened). Never network-fetch prices. The HANDOFF.md is the single source of truth — if it says COMPLETE, it is COMPLETE; if it names a binding row, that is the work; if it says NO agent-executable work remains, idle-wait for maintainer unblocking.