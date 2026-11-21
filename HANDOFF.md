# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-21T23:20:57Z (refreshed this session)
- **Git state:** HEAD `a76948e`. Working tree clean. **P30 WP0+WP1 LANDED and VERIFIED GREEN this session** — `scripts/bab_workflow_diagnostics.py` (canonical scanner + full secret redaction + `--self-test` + `--analyze-ledger` + `--scan-log`) and `tests/test_bab_p30_workflow_diagnostics.py` (12 acceptance tests GREEN, ruff clean). Binding row = **P30 WP2**; the queued next campaign is **P31 "Reproducibility Coverage Closure"** (declared below so a landed P30 can never fall into an idle-wait cliff). See the INITIAL TASK MESSAGE.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-21T23:20:57Z)

**Repo name = Crypto-Betting-Against-Beta.** The repo's entire credibility rests on one property: **the committed research numbers and the CI-health ledger are reproducible and verifiable locally, without `workflows:write`**. Research campaigns P20-P29 are COMPLETE and frozen. P26 = NO-SIGNAL (no real alpha on the no-alpha synthetic fixture → no real-market deployment claim on synthetic evidence). P27 execution infra is production-ready on paper/dry-run but its WP3 verdict is **NOT-READY** for live real-market deployment (P26 NO-SIGNAL + no licensed market data here). The maintainer-external blockers (CI `workflows:write`, licensed real-market CSV) cannot be resolved by an agent session — **do not idle-wait on them, and do not re-attempt them.**

**Two campaigns of heavy, fully agent-executable work are QUEUED and ZERO maintainer dependency. Do them in order; neither can be skipped.**

## BINDING ROW — P30 WP2 (heavy, agent-executable, zero maintainer dependency)

WP0+WP1 are committed and verified GREEN this session. **Do NOT re-do WP0/WP1.** WP2 is the remaining heavy work and it is what THIS session must execute:

1. **Ledger analyzer CLI hardening** — add `--summary-json PATH` (write the analysis to a committed `research_state/bab_p30/ledger_summary.json` deterministically — sorted keys, no wall-clock-derived fields except the explicit `analyzed_at_utc` stamp), `--since RUN_ID` (filter runs with `run_id >= RUN_ID`), and `--fail-on-cancelled` (exit non-zero if any run is cancelled — a local stand-in for the CI health signal the repo token cannot get from `workflows:write`; the committed ledger has exactly 1 cancelled run of 50). Land acceptance tests for all three flags.
2. **Divergence guard test** — a test that proves the canonical module's `redact()` is a strict superset of the old weak inline test copy. **Verified drift baseline this session:** `tests/test_workflow_diagnostics_scanner.py` `redact()` does ANSI-strip + truncate ONLY (no bearer / GitHub-token / JWT / secret-assignment / URL-secret / long-value redaction), while `scripts/bab_workflow_diagnostics.py` `redact()` (and the workflow YAML at `.github/workflows/main.yml:161-169`) redact all six classes. The guard must fail the gate if a weaker redactor is ever reintroduced into the scanner test or any future copy. This is the anti-drift contract that motivated P30.
3. **Wire into `bab_gate.sh`** — invoke `scripts/bab_workflow_diagnostics.py --self-test` and `--analyze-ledger` at the end of the full gate (mirrors how `bab_replay_gate.sh` is wired at `scripts/bab_gate.sh:145-147`), so the scanner drift proof and ledger analysis cannot be skipped by running the full gate alone.
4. **Ledger summary artifact + replay entry** — emit `research_state/bab_p30/ledger_summary.json` (deterministic) and add a P30 replay entry so `--analyze-ledger` output is reproducibility-checked like the P25-P27 artifacts.

## QUEUED NEXT CAMPAIGN — P31 "Reproducibility Coverage Closure" (declared so P30→P31 is seamless)

**Why this exists (verified gap this session):** `scripts/bab_replay_full.py` `REGISTRY` covers only **8 of ~28 committed research artifacts** — all of P25/P26/P27 (8) but **ZERO of P20-P24** (20 committed JSON artifacts under `research_state/bab_p20/**` … `research_state/bab_p24/**`). Those P20-P24 artifacts are "frozen and read-only" but are **NOT reproducibility-checked by any replay gate**. The repo's central thesis — "every committed number is reproducible" — therefore has a 20-artifact blind spot, and the completeness test `tests/test_bab_p29_replay_coverage.py::test_registry_covers_all_generated_artifacts` only asserts the registry equals a hardcoded 8-name set — it does NOT assert the registry covers *every committed research artifact*, so a newly added artifact could silently escape replay forever. Additionally the P29 provenance ledger (`research_state/bab_p29/provenance_audit.json`) is written by `--xproc` but never byte-diffed against a frozen copy on a fresh run.

**Feasibility (verified):** every P20-P24 generator already exposes a deterministic `build_*(fixture_path)` / `build_*()` entry point plus `render_markdown()` (e.g. `bab_research_sweep.build_sweep`, `bab_walk_forward.build_walk_forward`, `bab_breakeven.build_breakeven`, `bab_synthetic_universe.build_universe`, `bab_significance.build_significance`, `bab_rank_eval.build_rank_eval`, `bab_cost_surface.build_cost_surface`, `bab_p22_charter.build_charter`, `bab_null_battery.build_null_battery`, `bab_impact_surface.build_impact_surface`, `bab_capacity.build_capacity`, `bab_p23_charter.build_charter`, `bab_breadth_ladder.build_breadth_ladder`, `bab_beta_drift.build_beta_drift`, `bab_short_haircut.build_short_haircut`, `bab_p24_charter.build_charter`, `bab_licensed_adapter.build_adapter_dryrun`, `bab_hysteresis_ladder.build_hysteresis_ladder`, `bab_regime_split.build_regime_split`). The replay harness pattern already works; P31 extends the registry to P20-P24, adds the completeness guard, and freezes the provenance ledger via a regeneration-diff.

**P31 WPs (execute after P30 WP2 is COMPLETE — do NOT start P31 before P30 WP2 lands):**
- **P31 WP0** — extend `scripts/bab_replay_full.py` `REGISTRY` to all committed P20-P24 artifacts (module + `build_*` + dir + name), byte-diff each regenerated JSON/MD against the committed file read-only; add a cheap-subset drift self-test; land `tests/test_bab_p31_replay_coverage_p20_p24.py`. Some P20-P24 generators have inter-artifact dependencies (e.g. `build_charter` reads prior payloads) — replay must pass `fixture_path` / upstream payloads exactly as the original `main()` did so bytes match; if a generator cannot be made byte-reproducible without editing the frozen artifact, record it as a documented exception in the test rather than editing the artifact.
- **P31 WP1** — registry completeness guard: a test that enumerates every `*.json` under `research_state/bab_p2*/` and fails if any committed research artifact is not covered by the replay registry (or explicitly allow-listed with a written reason). This makes the 8/28 blind spot structurally impossible to re-create.
- **P31 WP2** — provenance-ledger regeneration-diff: add a `--check-provenance` mode (or equivalent) that regenerates the provenance audit from a fresh `--xproc` run into a temp path and byte-diffs it against the committed `research_state/bab_p29/provenance_audit.json` (modulo nothing — it must be fully deterministic); wire it into `bab_replay_gate.sh`; land acceptance tests.

**Hard contract (P30 + P31):**
1. No edits to any P20-P29 artifact (all closed/frozen); P30/P31 consume them read-only. The only P30 writes are new `scripts/*`, new `tests/test_bab_p30_*.py`, `research_state/bab_p30/**`, and the `bab_gate.sh` hook. The only P31 writes are `scripts/bab_replay_full.py` (registry + provenance check), new `tests/test_bab_p31_*.py`, the `bab_replay_gate.sh` hook, and `research_state/bab_p31/**` if a summary artifact is emitted. P31 must NOT edit any frozen `research_state/bab_p20..p29/**` file — if a P20-P24 artifact cannot be byte-reproduced without editing it, document the exception in a test instead.
2. `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged; never weakened.
3. No network fetching of prices; no real-market profitability claims on the synthetic fixture.
4. Zero ruff errors on new files; full gate GREEN; never hand off mid-gate.
5. The canonical `redact()` must remain a strict superset of any prior inline copy; the divergence-guard test must stay GREEN.
6. Do not weaken the existing `bab_replay_gate.sh` / `bab_reconcile_gate.sh` checks.

**Standing maintainer-external blockers (do NOT re-attempt):** (a) CI `workflows:write` — gates P28 WP2 only; (b) real-market licensed CSV — gates P28 WP3-WP4 only. Neither P30 nor P31 needs either. If a maintainer unblocks (a) and/or (b), P28 WP2-WP4 become the next binding rows after P31.

---

# CAMPAIGN P30 — BINDING ROW (WP0+WP1 COMPLETE; WP2 HEAVY WORK REMAINS)

**Declared:** 2026-11-21T23:19:07Z · **Campaign:** P30 "Workflow Diagnostics Tooling & Single-Source Scanner" · **Priority: HIGH** (the repo's bet-against-beta evidence is only as trustworthy as its CI-health ledger is locally verifiable; the scanner that produces that ledger had no single source of truth and the test copies drifted weaker than the workflow copy)

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — canonical scanner module | `scripts/bab_workflow_diagnostics.py`, `tests/test_bab_p30_workflow_diagnostics.py` (redaction + scan + self-test classes) | **COMPLETE** (committed this session; 12 tests GREEN, ruff clean — re-verified GREEN 2026-11-21T23:20:57Z) |
| WP1 — ledger analyzer | `scripts/bab_workflow_diagnostics.py` `--analyze-ledger`, `load_ledger()`, `analyze_ledger()` | **COMPLETE** (committed this session; 50 runs / 49 success / 1 cancelled / 981 signals, deterministic — re-verified GREEN 2026-11-21T23:20:57Z) |
| WP2 — analyzer hardening + drift guard + gate wire | `--summary-json`, `--since`, `--fail-on-cancelled`, divergence-guard test, `bab_gate.sh` hook, `research_state/bab_p30/ledger_summary.json` + replay entry | **BINDING ROW — HEAVY, AGENT-EXECUTABLE** |

**WP0 detail (COMPLETE — do not redo):** `scripts/bab_workflow_diagnostics.py` is the single source of truth for the log-scanning + secret-redaction logic the Kilo workflow embeds inline. `redact()` mirrors the workflow's full redactor (ANSI strip + bearer/GitHub-token/JWT/secret-assignment/URL-secret/long-value redaction + truncate). `scan_log_lines()` skips echoed workflow source (cyan ANSI command echo) and flags the kilo invalid-argument abort/edit patterns in addition to the general ERROR_RE. `--self-test` proves: clean log → no signals, traceback → signal, secret → redacted, re-scan of redacted excerpt → no re-exposure. **Verified GREEN this session:** `--self-test` exit 0, 12 tests pass, ruff clean.

**WP1 detail (COMPLETE — do not redo):** `--analyze-ledger` / `load_ledger()` / `analyze_ledger()` read `research_state/workflow_run_diagnostics.jsonl` read-only and emit a deterministic summary (`runs_total`, `unique_run_ids`, `runs_with_errors`, `total_error_signals`, `by_conclusion`, `by_status`, `analyzed_at_utc`). Determinism holds modulo the explicit timestamp. **Verified this session:** 50 runs, 49 success / 1 cancelled, 981 error signals. `research_state/bab_p30/` does NOT exist yet (WP2 has not emitted the summary artifact) — this is the proof WP2 is genuinely unstarted.

**WP2 detail (BINDING — the heavy work):** see the INITIAL TASK MESSAGE P30 WP2 list above. The goal is to make the ledger analysis CI-grade locally (summary artifact, since/cancelled filtering, gate wiring) and to lock in the anti-drift contract so the scanner can never silently weaken again. This is the work future agents MUST do next — it is heavy, agent-executable, and directly serves the repo's verifiability thesis.

---

# CAMPAIGN P31 — QUEUED NEXT (Reproducibility Coverage Closure)

**Declared:** 2026-11-21T23:20:57Z · **Campaign:** P31 "Reproducibility Coverage Closure" · **Priority: HIGH** · **Queued behind P30 WP2 (do NOT start until P30 WP2 is COMPLETE).**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — replay registry extended to P20-P24 (20 artifacts) | `scripts/bab_replay_full.py` (REGISTRY + self-test), `tests/test_bab_p31_replay_coverage_p20_p24.py` | **QUEUED** |
| WP1 — registry completeness guard (no artifact escapes replay) | `tests/test_bab_p31_registry_completeness.py` (enumerates every `research_state/bab_p2*/**.json`) | **QUEUED** |
| WP2 — provenance-ledger regeneration-diff + gate wire | `scripts/bab_replay_full.py` `--check-provenance`, `scripts/bab_replay_gate.sh` hook, `tests/test_bab_p31_provenance_replay.py` | **QUEUED** |

**P31 rationale:** P29 made the 8 P25/P26/P27 artifacts byte-reproducible; P30 made the CI-health ledger locally verifiable. P31 closes the remaining 20-artifact reproducibility blind spot (all P20-P24) and makes the replay registry self-guarding so coverage can never silently shrink again. After P31, every committed research artifact in the repo is replay-gated — the verifiability thesis is then complete modulo the two maintainer-external blockers (which gate only P28 WP2-WP4, not P31).

---

# CAMPAIGN P29 — COMPLETE (WP0 COMPLETE; WP1 COMPLETE; WP2 COMPLETE)

**Declared:** 2026-11-21T18:09:30Z · **Campaign:** P29 "Reproducibility & Provenance Assurance" · **Priority: HIGH**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — full read-only artifact replay | `scripts/bab_replay_full.py`, `scripts/bab_replay_gate.sh`, `tests/test_bab_p29_replay_coverage.py`, `scripts/bab_gate.sh` (invokes replay gate) | **COMPLETE** (committed `2eeb04c`; 8/8 byte-identical, 9 tests GREEN, ruff clean) |
| WP1 — cross-process determinism + provenance ledger | `scripts/bab_replay_full.py` `--xproc` mode, `research_state/bab_p29/provenance_audit.json`, `tests/test_bab_p29_xproc_determinism.py` | **COMPLETE** (committed `2eeb04c`; all 8 artifacts `replay_ok: true`; **known:** xproc gate slow ~16 min) |
| WP2 — decision-doc + sidecar + JSONL replay | `scripts/bab_replay_decisions.py`, `tests/test_bab_p29_decision_replay.py` | **COMPLETE** (committed `891f146`/`6212bcf`; all 6 artifacts byte-identical, wired into `bab_replay_gate.sh`) |

**P29 is COMPLETE. Do NOT re-do it.** The replay gate + xproc are slow (~16 min for 8 artifacts × 2 procs); run the fast `bab_quick` + `bab_reconcile` + `--self-test` inner loop while iterating. P28 WP0+WP1 COMPLETE; P28 WP2-WP4 maintainer-gated. No `research_state/**` P20-P29 modified.

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

**P28 WP2-WP4 remain maintainer-gated and MUST NOT be faked, simulated, or started early.** They are NOT the current bottleneck for progress because P30 WP2 (and then P31) are fully agent-executable. If a maintainer unblocks (a) `workflows:write` and/or (b) a licensed market CSV, P28 WP2-WP4 become the next binding rows after P31.

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

P20 WP0-WP5 (92 tests), P21 WP0-WP3 (56), P22 WP0-WP3 (85), P23 WP0-WP4 (80), P24 WP0-WP4 (94) all GREEN. All `research_state/bab_p20..p24/**`, `docs/BAB_RESEARCH_REPORT.md`, and P20-P24 scripts are frozen and read-only. **NOTE (P31 driver):** these 20 P20-P24 JSON artifacts are frozen but NOT yet replay-gated — P31 WP0/WP1 close that gap without editing any frozen artifact.

---

# MAINTAINER-EXTERNAL WORK (NOT AGENT TASKS)

1. **CI gate enforcement (P19-1 / P28 WP2)** — `bab-gate` job / `ruff` / `bab_gate.sh` / `bab_reconcile_gate.sh` in `.github/workflows/main.yml`: agent token lacks `workflows:write`. Maintainer must add via GitHub web UI or a `workflows:write` PAT. Do not re-attempt the push from an agent session. **Note:** P30 WP2's `--fail-on-cancelled` and ledger analyzer are the agent-executable local stand-in for this CI health signal until the maintainer unblocks.
2. **Real-market data ingestion (P28 WP3)** — licensed CSV is maintainer-supplied; `api.exchange.coinbase.com` returns 403 here. Network fetching of prices is forbidden.

---

# HARD GATES EVERY SESSION (repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
python3 scripts/bab_replay_full.py --self-test      # fast replay drift proof (full replay gate is slow ~16 min)
python3 scripts/bab_replay_decisions.py --self-test
python3 scripts/bab_workflow_diagnostics.py --self-test
python3 scripts/bab_workflow_diagnostics.py --analyze-ledger
bash scripts/bab_replay_gate.sh          # full: 8/8 artifacts byte-identical + drift self-test (slow ~16 min; run once per WP boundary)
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

`scripts/bab_gate.sh` invokes `scripts/bab_replay_gate.sh` at the end, so the replay check cannot be skipped by running the full gate alone. Inner loop while iterating: `bash scripts/bab_quick.sh` + `python3 -m pytest -q tests/test_bab_p30_workflow_diagnostics.py` + `python3 -m pytest -q tests/test_bab_p29_replay_coverage.py tests/test_bab_p29_decision_replay.py` + the P27/P26/P25 acceptance tests. Full gate once per WP boundary; never hand off mid-gate. Never lower the coverage floor. **After P30 WP2 lands, add `python3 scripts/bab_workflow_diagnostics.py --self-test` + `--analyze-ledger` to the `bab_gate.sh` hook (P30 WP2 deliverable) and confirm the full gate still GREENs.**

---

# FORBIDDEN (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (a handoff refresh without a landed fix is not a session).
- Editing any `research_state/bab_p20/**` … `research_state/bab_p29/**` artifact (frozen; P29 provenance ledger is frozen too), `docs/BAB_RESEARCH_REPORT.md`, or any P20-P29 script (frozen).
- Editing any P25 WP0-WP2 artifact, any P26 artifact, any P27 WP0-WP3 artifact, or any P28 WP0-WP1 artifact (all closed and frozen).
- Hand-typing any number into a P25/P26/P27 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta` / `rank_max_gross` below 0.20 / 4.0 in any decision.
- Describing the synthetic wide universe as real market data, or publishing a Sharpe without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- Shipping a WP whose committed artifact contradicts its own acceptance threshold.
- **Network fetching of prices** (Coinbase returns 403 here; licensed CSV is maintainer-supplied).
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, broad refactors, or committing probe/debug scratch scripts.
- Creating parallel handoff docs (this file is the single source of truth).
- **Faking P29/P30/P31 reproducibility** (hard-coding `sha256` values, skipping the xproc/self-test checks, or editing committed artifacts to force a green replay).
- **Starting P31 before P30 WP2 is COMPLETE.** P31 consumes P30's replay entry and ledger summary; doing P31 first would create a dependency inversion. P30 WP2 → P31 WP0 → WP1 → WP2.
- **Idle docs-only churn when agent-executable P30 WP2 (or, after it, P31) work exists.** The prior "idle-wait for the maintainer" directive is removed; when P30 WP2 is executable, doing it IS the session. Only when P30 AND P31 are fully complete AND P28 WP2-WP4 are maintainer-gated may a session report the idle-waiting state — and that report must include a fresh full-gate GREEN log, not just prose.

---

# BOTTLENECKS REMOVED (do not re-create)

- **[REMOVED 2026-11-21T23:20:57Z] Idle-wait cliff after P30 WP2.** The prior handoff bound the next session to P30 WP2 but queued no further agent-executable campaign, so a session that landed WP2 would have faced a "nothing executable remains; idle-wait for the maintainer" cliff — the exact bottleneck pattern removed twice before. Fixed: declared **Campaign P31 "Reproducibility Coverage Closure"** with WP0-WP2 (extend replay registry to the 20 unregistered P20-P24 artifacts; registry completeness guard; provenance-ledger regeneration-diff). Verified the P31 gap is real and the work feasible: `scripts/bab_replay_full.py` REGISTRY covers only 8/28 committed research artifacts (P25/P26/P27 only; zero P20-P24), the completeness test only checks a hardcoded 8-name set, the provenance ledger is never byte-diffed against a frozen copy, and every P20-P24 generator already exposes a deterministic `build_*()` + `render_markdown()`. P31 is heavy, fully agent-executable, and zero maintainer dependency. After P30 WP2, doing P31 IS the session — significant progress continues with no cliff.

- **[REMOVED 2026-11-21T23:19:07Z] "No agent-executable work remains; idle-wait for the maintainer" bottleneck.** The prior handoff certified all work done and told the next agent to idle-wait on P28 WP2-WP4 maintainer gates, treating those as a repo-wide stop. That was the inefficiency: it ignored that verifying CI health from the committed `research_state/workflow_run_diagnostics.jsonl` ledger (50 runs) is heavy, fully agent-executable work requiring no maintainer unblock, no frozen-artifact edits, and no network — and that the scanner logic producing that ledger had no single source of truth (3 hand-copied copies: workflow YAML + 2 inline test copies) with the test copies' `redact()` a weaker subset of the workflow's. Fixed: declared **Campaign P30 "Workflow Diagnostics Tooling & Single-Source Scanner"** with WP0-WP2, landed **WP0+WP1** this session (`scripts/bab_workflow_diagnostics.py` canonical scanner with full redaction + `--self-test` + ledger analyzer; 12 tests GREEN, ruff clean; verified 50 runs / 49 success / 1 cancelled / 981 signals deterministic), and set the binding row to **P30 WP2** (analyzer hardening + drift-guard test + gate wire) — fully agent-executable with zero maintainer dependency. Significant progress continues now.

- **[REMOVED 2026-11-21T21:29:29Z] "P29 WP2 NOT STARTED" bottleneck.** The prior handoff certified WP2 as NOT STARTED and claimed `scripts/bab_replay_decisions.py` / `tests/test_bab_p29_decision_replay.py` did not exist. They were already committed at `6212bcf` / `891f146`: all 6 artifacts (3 decision docs + `p27_decision_sidecar.json` + 2 JSONL sidecars) replay byte-identically, 10 tests GREEN, ruff clean, wired into `scripts/bab_replay_gate.sh`. WP2 is COMPLETE. All P29 WPs (WP0, WP1, WP2) are now done; no agent-executable P29 work remains.

- **[REMOVED 2026-11-21T19:43:54Z] "P29 WP1 incomplete" bottleneck.** The prior handoff declared P29 WP1 as the binding row, but implementation was already committed at `2eeb04c`: `scripts/bab_replay_full.py --xproc`, `research_state/bab_p29/provenance_audit.json` (all 8 artifacts `replay_ok: true`), `tests/test_bab_p29_xproc_determinism.py`. WP1 is COMPLETE. Binding row moved to P29 WP2 (decision-doc + JSONL sidecar replay).
- **[REMOVED 2026-11-21T18:09:30Z] "No agent-executable work remains; idle-wait for the maintainer" bottleneck.** The prior handoff declared the binding row NONE and told the next agent to idle-wait, treating the P28 WP2-WP4 maintainer gates as a repo-wide stop. That was the inefficiency: it ignored that reproducibility of the committed evidence is itself heavy, agent-executable work. Fixed: declared **Campaign P29 "Reproducibility & Provenance Assurance"** with WP0-WP2, landed **WP0** this session (full read-only 8-artifact replay + `--self-test` drift proof + gate wired into `bab_gate.sh`; verified 8/8 byte-identical, 9 tests GREEN, ruff clean), and set the binding row to **P29 WP1** (cross-process determinism + provenance ledger) — fully agent-executable with zero maintainer dependency. Significant progress continues now.
- **[REMOVED 2026-11-21T17:04:13Z] Stale initial task message named P28 WP0 unstarted; its files were already committed.** Marked WP0 COMPLETE, forbade re-creating it, set binding row to P28 WP1.
- **[REMOVED 2026-11-21T14:23:33Z] Stale HANDOFF claimed P28 WP1 unstarted.** WP1 landed at `af57b5a`/`7ee5729`; binding row updated.
- **[REMOVED 2026-11-21T12:22:18Z] Stale HEAD certification + stale refresh timestamps blocking P28 start.** Re-verified gates GREEN and P28 unstarted; binding row P28 WP0 → WP1.
- **[REMOVED 2026-11-21T11:32:07Z] Stale HANDOFF claimed P27 WP3 deliverables absent.** They exist and are complete; P27 marked COMPLETE.
- **[REMOVED 2026-11-20T16:37:11Z] No binding row existed.** Created Campaign P25 with binding WP0.
- (Earlier P23/P24 bottleneck removals retained in git history; see `git log` for the full ledger.)

---

# FUTURE AGENTS: READ THIS ONCE

**This repo's agent-executable work is NOT done — the binding row is P30 WP2, with P31 queued behind it.** Campaigns P20-P29 are complete and frozen. Campaign **P30 "Workflow Diagnostics Tooling & Single-Source Scanner"** is the active work: **WP0 is COMPLETE** — `scripts/bab_workflow_diagnostics.py` (canonical scanner, full secret redaction, `--self-test`) + `tests/test_bab_p30_workflow_diagnostics.py` (12 tests); **WP1 is COMPLETE** — `--analyze-ledger` / `load_ledger()` / `analyze_ledger()` (50 runs, 49 success / 1 cancelled, 981 signals, deterministic); **WP2 is the BINDING ROW** — analyzer hardening (`--summary-json`, `--since`, `--fail-on-cancelled`), divergence-guard test, `bab_gate.sh` wire, `research_state/bab_p30/ledger_summary.json` + replay entry. Execute WP2; do NOT re-do WP0/WP1. **After WP2 lands, execute P31** ("Reproducibility Coverage Closure": extend replay registry to the 20 unregistered P20-P24 artifacts, add a registry completeness guard, add a provenance-ledger regeneration-diff). **Verified 2026-11-21T23:20:57Z:** ruff PASS on P30 files, `bab_workflow_diagnostics --self-test` PASS, `--analyze-ledger` GREEN (50 runs), `tests/test_bab_p30_workflow_diagnostics.py` 12 passed. Do NOT re-create or re-edit any of the WP0/WP1 files.

**Anti-idle rule:** a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure when agent-executable work exists. P30 WP2 is executable now — doing it IS the session. P31 is queued immediately behind it. Only when BOTH P30 and P31 are fully complete AND P28 WP2-WP4 are maintainer-gated may a session report the idle-waiting state, and that report must include a fresh full-gate GREEN log.

Do not re-open frozen P20-P29 artifacts (consumed read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` (never weakened). Never network-fetch prices. If this file says a WP is COMPLETE, it is COMPLETE; if it names a binding row (currently **P30 WP2**) or a queued campaign (**P31**), that is the work; if it says a WP is maintainer-gated, route it to the maintainer and proceed to the next agent-executable P30/P31 WP.