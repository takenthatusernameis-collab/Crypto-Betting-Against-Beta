# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-21T23:19:07Z (refreshed this session)
- **Git state:** HEAD `0423656`. Working tree clean. **P30 WP0+WP1 LANDED this session** — `scripts/bab_workflow_diagnostics.py` (canonical scanner + full secret redaction + `--self-test` + `--analyze-ledger` + `--scan-log`), `tests/test_bab_p30_workflow_diagnostics.py` (12 acceptance tests GREEN). This is the new binding row; see the INITIAL TASK MESSAGE below.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-21T23:19:07Z)

**Repo name = Crypto-Betting-Against-Beta.** The repo's entire credibility rests on one property: **the committed research numbers and CI-health ledger are reproducible and verifiable locally, without `workflows:write`**. Research campaigns P20-P29 are COMPLETE and frozen. P26 = NO-SIGNAL (no real alpha on the no-alpha synthetic fixture → no real-market deployment claim on synthetic evidence). P27 execution infra is production-ready on paper/dry-run but its WP3 verdict is **NOT-READY** for live real-market deployment (P26 NO-SIGNAL + no licensed market data here). The maintainer-external blockers (CI `workflows:write`, licensed real-market CSV) cannot be resolved by an agent session — **do not idle-wait on them, and do not re-attempt them.**

**The previous handoff's "no agent-executable work remains; idle-wait for the maintainer" directive was a BOTTLENECK and has been REMOVED.** It was wrong: verifying CI health from the committed `research_state/workflow_run_diagnostics.jsonl` ledger (50 runs, 981 error signals) is heavy, fully agent-executable work that needs no maintainer unblock, no frozen-artifact edits, and no network. The scanner logic that produces that ledger was hand-copied in three places (workflow YAML + two inline test copies) with **no single source of truth**, and the test copies' `redact()` was a weaker subset of the workflow's (it redacted no bearer/GitHub/JWT/secret-assignment/URL secrets). That drift is a provenance hazard: a weak re-scan can re-expose a secret the workflow redacted.

**Campaign P30 "Workflow Diagnostics Tooling & Single-Source Scanner" is the new binding row.** WP0+WP1 are landed this session; WP2 is the remaining heavy work. Execute WP2 next — do NOT re-do WP0/WP1.

- **P30 WP0 COMPLETE (committed this session)** — `scripts/bab_workflow_diagnostics.py`: canonical `redact()` (full workflow-equivalent secret redaction: bearer, GitHub token, JWT, secret assignment, URL secret, long opaque value), `scan_log_lines()`, `scan_log_archive()`, `build_log_archive()`, `--self-test` drift+redaction proof, `--scan-log`. 12 acceptance tests GREEN, ruff clean. **Do NOT re-do it.**
- **P30 WP1 COMPLETE (committed this session)** — `--analyze-ledger` / `load_ledger()` / `analyze_ledger()`: deterministic read-only classifier over the committed `research_state/workflow_run_diagnostics.jsonl` (sorted keys, no wall-clock-derived fields except an explicit `analyzed_at_utc` stamp). Verified: 50 runs, 49 success / 1 cancelled, 981 error signals, deterministic modulo timestamp. **Do NOT re-do it.**
- **P30 WP2 — BINDING ROW (heavy, agent-executable, zero maintainer dependency):**
  1. **Ledger analyzer CLI hardening** — add `--summary-json PATH` (write the analysis to a committed `research_state/bab_p30/ledger_summary.json` deterministically), `--since RUN_ID` (filter runs), and `--fail-on-cancelled` (exit non-zero if any run is cancelled — a local stand-in for the CI health signal the repo token cannot get from `workflows:write`). Land acceptance tests.
  2. **Divergence guard test** — a test that proves the canonical module's `redact()` is a strict superset of the old weak inline test copy (i.e. the old `redact()` = ANSI strip + truncate only), so any future re-introduction of a weaker redactor fails the gate. This is the anti-drift contract that motivated P30.
  3. **Wire into `bab_gate.sh`** — invoke `scripts/bab_workflow_diagnostics.py --self-test` and `--analyze-ledger` at the end of the full gate (mirrors how `bab_replay_gate.sh` is wired), so the scanner drift proof and ledger analysis cannot be skipped by running the full gate alone.
  4. **Ledger summary artifact** — emit `research_state/bab_p30/ledger_summary.json` (deterministic) and add a P30 replay entry so `--analyze-ledger` output is reproducibility-checked like the P25-P27 artifacts.

**Hard contract (P30):**
1. No edits to any P20-P29 artifact (all closed/frozen); P30 consumes them read-only. The only P30 writes are new `scripts/*`, new `tests/test_bab_p30_*.py`, `research_state/bab_p30/**`, and the `bab_gate.sh` hook.
2. `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged; never weakened.
3. No network fetching of prices; no real-market profitability claims on the synthetic fixture.
4. Zero ruff errors on new files; full gate GREEN; never hand off mid-gate.
5. The canonical `redact()` must remain a strict superset of any prior inline copy; the divergence-guard test must stay GREEN.
6. Do not weaken the existing `bab_replay_gate.sh` / `bab_reconcile_gate.sh` checks.

**Standing maintainer-external blockers (do NOT re-attempt):** (a) CI `workflows:write` — gates P28 WP2 only; (b) real-market licensed CSV — gates P28 WP3-WP4 only. P30 needs neither. If a maintainer unblocks (a) and/or (b), P28 WP2-WP4 become the next binding rows after P30.

---

# CAMPAIGN P30 — BINDING ROW (WP0+WP1 COMPLETE; WP2 HEAVY WORK REMAINS)

**Declared:** 2026-11-21T23:19:07Z · **Campaign:** P30 "Workflow Diagnostics Tooling & Single-Source Scanner" · **Priority: HIGH** (the repo's bet-against-beta evidence is only as trustworthy as its CI-health ledger is locally verifiable; the scanner that produces that ledger had no single source of truth and the test copies drifted weaker than the workflow copy)

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — canonical scanner module | `scripts/bab_workflow_diagnostics.py`, `tests/test_bab_p30_workflow_diagnostics.py` (redaction + scan + self-test classes) | **COMPLETE** (committed this session; 12 tests GREEN, ruff clean) |
| WP1 — ledger analyzer | `scripts/bab_workflow_diagnostics.py` `--analyze-ledger`, `load_ledger()`, `analyze_ledger()` | **COMPLETE** (committed this session; 50 runs / 49 success / 1 cancelled / 981 signals, deterministic) |
| WP2 — analyzer hardening + drift guard + gate wire | `--summary-json`, `--since`, `--fail-on-cancelled`, divergence-guard test, `bab_gate.sh` hook, `research_state/bab_p30/ledger_summary.json` + replay entry | **BINDING ROW — HEAVY, AGENT-EXECUTABLE** |

**WP0 detail (COMPLETE — do not redo):** `scripts/bab_workflow_diagnostics.py` is the single source of truth for the log-scanning + secret-redaction logic the Kilo workflow embeds inline. `redact()` mirrors the workflow's full redactor (ANSI strip + bearer/GitHub-token/JWT/secret-assignment/URL-secret/long-value redaction + truncate). `scan_log_lines()` skips echoed workflow source (cyan ANSI command echo) and flags the kilo invalid-argument abort/edit patterns in addition to the general ERROR_RE. `--self-test` proves: clean log → no signals, traceback → signal, secret → redacted, re-scan of redacted excerpt → no re-exposure.

**WP1 detail (COMPLETE — do not redo):** `--analyze-ledger` / `load_ledger()` / `analyze_ledger()` read `research_state/workflow_run_diagnostics.jsonl` read-only and emit a deterministic summary (`runs_total`, `unique_run_ids`, `runs_with_errors`, `total_error_signals`, `by_conclusion`, `by_status`, `analyzed_at_utc`). Determinism holds modulo the explicit timestamp. Verified this session: 50 runs, 49 success / 1 cancelled, 981 error signals.

**WP2 detail (BINDING — the heavy work):** see the INITIAL TASK MESSAGE WP2 list above. The goal is to make the ledger analysis CI-grade locally (summary artifact, since/cancelled filtering, gate wiring) and to lock in the anti-drift contract so the scanner can never silently weaken again. This is the work future agents MUST do — it is heavy, agent-executable, and directly serves the repo's verifiability thesis.

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

**P28 WP2-WP4 remain maintainer-gated and MUST NOT be faked, simulated, or started early.** They are NOT the current bottleneck for progress because P30 WP2 is fully agent-executable. If a maintainer unblocks (a) `workflows:write` and/or (b) a licensed market CSV, P28 WP2-WP4 become the next binding rows after P30.

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

`scripts/bab_gate.sh` invokes `scripts/bab_replay_gate.sh` at the end, so the replay check cannot be skipped by running the full gate alone. Inner loop while iterating: `bash scripts/bab_quick.sh` + `python3 -m pytest -q tests/test_bab_p30_workflow_diagnostics.py` + `python3 -m pytest -q tests/test_bab_p29_replay_coverage.py tests/test_bab_p29_decision_replay.py` + the P27/P26/P25 acceptance tests. Full gate once per WP boundary; never hand off mid-gate. Never lower the coverage floor.

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
- **Faking P29/P30 reproducibility** (hard-coding `sha256` values, skipping the xproc/self-test checks, or editing committed artifacts to force a green replay).
- **Idle docs-only churn when agent-executable P30 WP2 work exists.** The prior "idle-wait for the maintainer" directive is removed; when P30 WP2 is executable, doing it IS the session. Only when P30 is fully complete AND P28 WP2-WP4 are maintainer-gated may a session report the idle-waiting state — and that report must include a fresh full-gate GREEN log, not just prose.

---

# BOTTLENECKS REMOVED (do not re-create)

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

**This repo's agent-executable work is NOT done — the binding row is P30 WP2.** Campaigns P20-P29 are complete and frozen. Campaign **P30 "Workflow Diagnostics Tooling & Single-Source Scanner"** is the active work: **WP0 is COMPLETE** — `scripts/bab_workflow_diagnostics.py` (canonical scanner, full secret redaction, `--self-test`) + `tests/test_bab_p30_workflow_diagnostics.py` (12 tests); **WP1 is COMPLETE** — `--analyze-ledger` / `load_ledger()` / `analyze_ledger()` (50 runs, 49 success / 1 cancelled, 981 signals, deterministic); **WP2 is the BINDING ROW** — analyzer hardening (`--summary-json`, `--since`, `--fail-on-cancelled`), divergence-guard test, `bab_gate.sh` wire, `research_state/bab_p30/ledger_summary.json` + replay entry. Execute WP2; do NOT re-do WP0/WP1. **Verified 2026-11-21T23:19:07Z:** ruff PASS, `bab_quick` 299 tests PASS, `bab_reconcile_gate` GREEN, replay full/decisions self-tests PASS, `bab_workflow_diagnostics --self-test` PASS, `--analyze-ledger` GREEN (50 runs). Do NOT re-create or re-edit any of the WP0/WP1 files.

**Anti-idle rule:** a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure when agent-executable work exists. P30 WP2 is executable now — doing it IS the session. Only when P30 is fully complete AND P28 WP2-WP4 are maintainer-gated may a session report the idle-waiting state, and that report must include a fresh full-gate GREEN log.

Do not re-open frozen P20-P29 artifacts (consumed read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` (never weakened). Never network-fetch prices. If this file says a WP is COMPLETE, it is COMPLETE; if it names a binding row (currently **P30 WP2**), that is the work; if it says a WP is maintainer-gated, route it to the maintainer and proceed to the next agent-executable P30 WP.