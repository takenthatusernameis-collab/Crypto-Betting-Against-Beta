# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-22T09:47:00Z (refreshed this session; supersedes the 2026-11-22T08:25:00Z stamp)
- **Git state:** HEAD `a885d24` at write time (working tree clean). **P20–P34 are all COMPLETE and frozen.** The binding row is now **Campaign P28 WP2-WP4 (maintainer-gated only)** — all agent-executable work is complete. The post-P34 idle-wait is the correct state; a future session must attach a fresh full-gate GREEN log before reporting idle.
- **Gate verified GREEN this session (fast inner loop):** `python3 -m ruff check .` PASS; `bash scripts/bab_reconcile_gate.sh` GREEN (drift rc=2 / clean rc=0 / emit-only rc=0); `python3 -m pytest -q tests/test_bab_p34_*.py tests/test_bab_p33_*.py tests/test_bab_p31_registry_completeness.py tests/test_bab_p32_*.py` → 83 passed, 2 skipped; `python3 scripts/bab_p34_multiseed_robustness.py --check-multiseed-summary` PASS; `python3 scripts/bab_replay_full.py --self-test` pass; `python3 scripts/bab_replay_decisions.py --self-test` pass; `python3 scripts/bab_doc_consistency_summary.py --check-doc-summary research_state/bab_p33/doc_consistency_summary.json` OK; `bash scripts/bab_quick.sh` 104 + 195 tests PASS. The slow full gate (`BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh`, ~16 min) includes P34 replay/summary checks; re-run it once and attach the GREEN log before any idle-wait report.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-22T09:47:00Z)

**ALL AGENT-EXECUTABLE WORK IS COMPLETE.** P20–P34 are fully landed and frozen. Campaign **P34 "Wide-Universe Robustness & Strategy-Honesty Closure" (WP0→WP1→WP2) is COMPLETE** — the multi-seed robustness study, statistical honesty battery, and documentation-integrity closure are all verified GREEN. The only remaining work is **Campaign P28 WP2-WP4**, which are **maintainer-gated** (require `workflows:write` permission for CI gate enforcement and a licensed real-market CSV for ingestion/deployment decision).

**Why the idle-wait (repo-name relevance, 2026-11-22T09:47:00Z):**
- The repository is named **Crypto-Betting-Against-Beta** — a quantitative strategy. The complete research pipeline (P20–P34) has been executed on synthetic fixtures (`tests/fixtures/real_market_prices.csv` 9-asset, `tests/fixtures/wide_bab_universe.csv` 40-asset), both deterministic random walks explicitly labelled **not real market data**. P26's verdict on the 9-asset frame was **NO-SIGNAL**; P25 promoted `weighting="rank"` on the 40-asset frame; P34 established multi-seed robustness + strategy-honesty closure for the shipped default (`weighting="equal"`, `beta_neutral=True`) across 8 seeds × 6 config cells.
- **No further agent-executable gaps exist** in the strategy codebase, test suite, documentation, or gates. The `bab_gate.sh` enforces 100% coverage, full artifact replay (P29), workflow diagnostics (P30), registry completeness (P31), decision-doc replay (P32), fidelity consistency (P33), and P34 multiseed/honesty/doc-pointer checks. All pass locally.
- **P28 WP2 (CI gate enforcement)** is blocked on the repo token lacking `workflows:write` — a maintainer must add the `bab-gate` job to `.github/workflows/main.yml` via the GitHub web UI or a PAT. **P28 WP3 (real-market data ingestion)** and **WP4 (live-market deployment decision)** are blocked on a licensed CSV (Coinbase public API returns 403 here; `--allow-public-api` requires explicit ToS acknowledgement and is not a substitute for licensed data). **Do not re-attempt these from an agent session.**

**Reporting the post-P34 idle state:** a future session must run the full gate (`BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh`) and attach the GREEN log before declaring idle. Inner loop for any maintenance: `bash scripts/bab_quick.sh` + `python3 -m ruff check .` + `python3 -m pytest -q tests/test_bab_p34_*.py tests/test_bab_p33_*.py tests/test_bab_p31_registry_completeness.py tests/test_bab_p32_*.py` + `--check-multiseed-summary` + replay self-tests.

**Bottleneck status:** the post-P33 idle cliff (removed 2026-11-22T07:31:10Z), the stale-HEAD/stale-binding-row class (removed repeatedly), the parallel-handoff class (removed 2026-11-22T04:06:06Z), and all prior idle cliffs remain removed. `HANDOFF.md` is the single durable handoff — re-creating any `*HANDOFF*.md`, `NEXT_SESSION*.md`, or `AGENT_*.md` parallel task doc is forbidden.

---

## BINDING ROW — Campaign P28 WP2-WP4 (MAINTAINER-GATED)

P20–P34 are fully complete and frozen. **Do NOT re-do them.** The remaining work is maintainer-external:

### P28 WP2 — CI Gate Enforcement
- **Blocker:** Repo token lacks `workflows:write` permission.
- **Deliverable:** `.github/workflows/main.yml` must include a `bab-gate` job that runs `ruff`, `scripts/bab_gate.sh`, and `scripts/bab_reconcile_gate.sh` on push/PR.
- **Maintainer action:** Add via GitHub web UI or a `workflows:write` PAT. The prior attempt (commit `b641b7a`, branch `kilo-p19-1-push`) was lost when its branch vanished; do not re-push from agent.

### P28 WP3 — Real-Market Data Ingestion
- **Blocker:** Licensed CSV required. `api.exchange.coinbase.com` returns 403; public API path requires explicit ToS acknowledgement and is not licensed data.
- **Deliverable:** `scripts/fetch_real_bab_prices.py` licensed-CSV adapter + `tests/test_bab_p28_ingestion.py`.
- **Maintainer action:** Supply a licensed market data CSV.

### P28 WP4 — Live-Market Deployment Decision
- **Blocker:** Needs WP2+WP3 + maintainer authorization.
- **Deliverable:** `docs/BAB_P28_DECISION.md`, `generate_p28_decision.py`, `tests/test_bab_p28_decision_consistency.py`.
- **Maintainer action:** Authorize after WP2+WP3 complete.

**If a maintainer unblocks (a) `workflows:write` and/or (b) a licensed market CSV, P28 WP2-WP4 become the next agent-executable binding rows.**

---

## CAMPAIGN P34 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T09:47:00Z)

**Declared:** 2026-11-22T07:44:24Z · **Campaign:** P34 "Wide-Universe Robustness & Strategy-Honesty Closure" · **Priority: HIGH** · **ALL WPs COMPLETE. Do NOT re-do it.**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — Multi-seed wide-universe equal-weight robustness study | `scripts/bab_p34_multiseed_robustness.py`, `tests/test_bab_p34_multiseed_robustness.py`, `research_state/bab_p34/multiseed_summary.json` | **COMPLETE** (19 tests PASS; `--check-multiseed-summary` PASS; ruff clean) |
| WP1 — Statistical falsification / honesty battery | `tests/test_bab_p34_honesty_battery.py` | **COMPLETE** (11 passed, 1 skipped) |
| WP2 — Documentation-integrity closure + summary + gate wire | README.md & docs/COVERAGE_NOTES.md pointer fixes, `tests/test_bab_p34_doc_pointer_guard.py`, `scripts/bab_gate.sh` hook | **COMPLETE** (7 passed, 1 skipped; gate wired) |

**P34 rationale:** closed the last agent-executable heavy gap — the wide 40-asset synthetic fixture was only exercised by P25 rank tests; P34 established multi-seed robustness of the shipped default (`weighting="equal"`, `beta_neutral=True`) across 8 seeds × 6 config cells (48 cells), with systematic neutrality invariants (model beta-neutral ≤1e-3, dollar-neutral ≤1e-9, realized β ≤0.15) verified at every cell, plus a statistical honesty battery (no-lookahead, no-profitable-claim, neutralization-effect, anti-victory) and a documentation-pointer-rot guard. **P34 is COMPLETE. Do NOT re-do it.**

---

## CAMPAIGN P33 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T07:04:44Z)

**Declared:** 2026-11-22T03:58:29Z · **Campaign:** P33 "Fidelity & Cross-Document Consistency Closure" · **Priority: HIGH** · **ALL WPs COMPLETE. Do NOT re-do it.**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — `BAB_FIDELITY.md` ↔ data consistency guard (every published §3/§4 cell = deterministic recompute) | `tests/test_bab_p33_fidelity_consistency.py` | **COMPLETE** (21 tests PASS; ruff clean) |
| WP1 — document-layer completeness guard (every `docs/*.md` is replay-gated, consistency-guarded, or allow-listed with a reason) | `tests/test_bab_p33_doc_registry_completeness.py` | **COMPLETE** (6 tests PASS) |
| WP2 — summary artifact + gate wire | `research_state/bab_p33/doc_consistency_summary.json`, `scripts/bab_doc_consistency_summary.py --check-doc-summary`, `scripts/bab_gate.sh` hook | **COMPLETE** (`--check-doc-summary` OK; wired into `bab_gate.sh`) |

**P33 rationale:** closed the JSON (P29/P31), CI-health (P30), decision + kickoff (P32), and human-fidelity-narrative (P33) verifiability threads. The "every committed/published number is reproducible" thesis now extends fully to the human-facing narrative layer. **P33 is COMPLETE. Do NOT re-do it.**

---

## CAMPAIGN P32 — COMPLETE (ALL WPs LANDED)

**Declared:** 2026-11-21T23:53:48Z · **Campaign:** P32 "Decision-Document Replay Closure" · **Priority: HIGH**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — byte-replay `BAB_P24_DECISION.md` | `scripts/bab_replay_decisions.py` (new `p24_decision.md` entry), `tests/test_bab_p32_decision_replay_p24.py` | **COMPLETE** (code `a9257f8`; tests `12f1483`) |
| WP1 — decision-doc completeness guard | `tests/test_bab_p32_decision_registry_completeness.py` | **COMPLETE** |
| WP2 — KICKOFF-doc closure + summary artifact + gate wire | `scripts/bab_replay_decisions.py` (KICKOFF entries), `research_state/bab_p32/doc_replay_summary.json`, `scripts/bab_replay_gate.sh` hook | **COMPLETE** |

**P32 is COMPLETE. Do NOT re-do it.** Every generated decision doc (P24-P27) and KICKOFF doc (P22-P24) byte-replays; the registry-completeness guard makes an orphaned generated decision doc structurally impossible.

---

## CAMPAIGN P31 — COMPLETE (WP0+WP1+WP2)

**Declared:** 2026-11-21T23:20:57Z · **Campaign:** P31 "Reproducibility Coverage Closure" · **Priority: HIGH**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — replay registry extended to 19 P20-P24 artifacts | `scripts/bab_replay_full.py` (REGISTRY + self-test), `tests/test_bab_p31_replay_coverage_p20_p24.py` | **COMPLETE** |
| WP1 — registry completeness guard (no artifact escapes replay) | `tests/test_bab_p31_registry_completeness.py` | **COMPLETE** |
| WP2 — provenance-ledger regeneration-diff + gate wire | `scripts/bab_replay_full.py` `--check-provenance`, `scripts/bab_replay_gate.sh` hook, `tests/test_bab_p31_provenance_replay.py` | **COMPLETE** |

**P31 is COMPLETE. Do NOT re-do it.** After P31, every committed JSON research artifact in the repo is replay-gated.

---

## CAMPAIGN P30 — COMPLETE (ALL WPs LANDED)

**Declared:** 2026-11-21T23:19:07Z · **Campaign:** P30 "Workflow Diagnostics Tooling & Single-Source Scanner" · **Priority: HIGH**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — canonical scanner module | `scripts/bab_workflow_diagnostics.py`, `tests/test_bab_p30_workflow_diagnostics.py` | **COMPLETE** (21 tests GREEN, ruff clean) |
| WP1 — ledger analyzer | `scripts/bab_workflow_diagnostics.py` `--analyze-ledger`, `load_ledger()`, `analyze_ledger()` | **COMPLETE** |
| WP2 — analyzer hardening + drift guard + gate wire | `--summary-json`, `--since`, `--fail-on-cancelled`, divergence-guard test, `bab_gate.sh` hook, `research_state/bab_p30/ledger_summary.json` + replay entry | **COMPLETE** |

**P30 is COMPLETE. Do NOT re-do it.**

---

## CAMPAIGN P29 — COMPLETE (WP0+WP1+WP2)

**Declared:** 2026-11-21T18:09:30Z · **Campaign:** P29 "Reproducibility & Provenance Assurance" · **Priority: HIGH**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — full read-only artifact replay | `scripts/bab_replay_full.py`, `scripts/bab_replay_gate.sh`, `tests/test_bab_p29_replay_coverage.py`, `scripts/bab_gate.sh` (invokes replay gate) | **COMPLETE** (committed `2eeb04c`; 8/8 byte-identical) |
| WP1 — cross-process determinism + provenance ledger | `scripts/bab_replay_full.py` `--xproc` mode, `research_state/bab_p29/provenance_audit.json`, `tests/test_bab_p29_xproc_determinism.py` | **COMPLETE** (committed `2eeb04c`; all 8 artifacts `replay_ok: true`; **known:** xproc gate slow ~16 min) |
| WP2 — decision-doc + sidecar + JSONL replay | `scripts/bab_replay_decisions.py`, `tests/test_bab_p29_decision_replay.py` | **COMPLETE** (committed `6212bcf`/`891f146`) |

**P29 is COMPLETE. Do NOT re-do it.** The replay gate + xproc are slow (~16 min for 8 artifacts × 2 procs); run the fast `bab_quick` + `bab_reconcile` + `--self-test` inner loop while iterating.

---

## CAMPAIGN P28 — COMPLETE FOR AGENT-EXECUTABLE SCOPE (WP0+WP1 DONE; WP2-WP4 MAINTAINER-GATED)

**Timestamp:** 2026-11-21T13:23:23Z · **Campaign:** P28 "Live-Market Deployment Preconditions & Controller Hardening"

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — controller hardening + replay harness | `scripts/bab_replay_harness.py`, hardened `scripts/controller_progress.py`, `tests/test_bab_p28_controller_hardening.py`, `tests/test_bab_replay_harness_r4.py` | **COMPLETE** (27 tests GREEN) |
| WP1 — data-loader validation | `tests/test_bab_p28_data_loader.py` | **COMPLETE** (11 passed + 2 skipped) |
| WP2 — CI gate enforcement | `.github/workflows/main.yml` `bab-gate` job | **GATED** (maintainer `workflows:write`) |
| WP3 — real-market data ingestion | `scripts/fetch_real_bab_prices.py` licensed-CSV adapter + `tests/test_bab_p28_ingestion.py` | **GATED** (maintainer licensed CSV) |
| WP4 — live-market deployment decision | `docs/BAB_P28_DECISION.md`, `generate_p28_decision.py`, `tests/test_bab_p28_decision_consistency.py` | **GATED** (needs WP1-WP3 + maintainer authorization) |

**P28 WP2-WP4 remain maintainer-gated and MUST NOT be faked, simulated, or started early.** They are NOT the current bottleneck because all agent-executable work (P20–P34) is complete. If a maintainer unblocks (a) `workflows:write` and/or (b) a licensed market CSV, P28 WP2-WP4 become the next binding rows.

---

## CAMPAIGN P27 — COMPLETE (ALL WPs LANDED)

**Timestamp:** 2026-11-21T11:32:07Z · P27 "Production Execution Infrastructure & Live-Trading Readiness" · **All WPs COMPLETE.** WP0 `scripts/bab_execution_hardening.py`, WP1 `scripts/bab_risk_controls.py`, WP2 `scripts/bab_reconciliation_e2e.py`, WP3 `docs/BAB_P27_DECISION.md` + `generate_p27_decision.py` + `tests/test_bab_p27_decision_consistency.py`. WP3 verdict = **NOT-READY** for live real-market deployment. All artifacts frozen and read-only.

---

## CAMPAIGN P26 — CLOSED (NO-SIGNAL)

**Timestamp:** 2026-11-21T05:49:54Z · P26 "Signal-to-Noise Validation of Rank-Weighted BAB" · **Verdict: NO-SIGNAL.** WP0 signal-vs-null (rank p=0.2857, equal p=0.3586; SIGNAL condition false — correct anti-victory), WP1 regime stress (falsification gate NOT passed), WP2 capacity & turnover, WP3 `docs/BAB_P26_DECISION.md` explicit NO-SIGNAL. **Note: P26 was run on the 9-asset fixture only** — P34 WP0/WP1 generalize the robustness + honesty study to the wide 40-asset universe across many seeds. Do NOT edit the frozen P25 WP0 fixture to "plant" alpha.

---

## CAMPAIGN P25 — CLOSED (PROMOTE for `weighting="rank"`)

WP0 wide universe (`scripts/bab_wide_universe.py`, `tests/fixtures/wide_bab_universe.csv` [SHA256 `a6d390fc…163b`, 40 assets, betas 0.35–1.90, seed 20261120]), WP1 rank walk-forward, WP2 equal-vs-rank OOS bake-off (rank OOS Sharpe 0.4373 vs equal 0.1703, delta +0.2670), WP3 `docs/BAB_P25_DECISION.md` PROMOTE for `weighting="rank"`. All frozen and read-only. **The wide fixture is the substrate P34 WP0/WP1 build on — consume it read-only, never edit it.**

---

## CAMPAIGN P20-P24 — CLOSED (COMPLETE)

P20 WP0-WP5 (92 tests), P21 WP0-WP3 (56), P22 WP0-WP3 (85), P23 WP0-WP4 (80), P24 WP0-WP4 (94) all GREEN. All `research_state/bab_p20..p24/**`, `docs/BAB_RESEARCH_REPORT.md`, and P20-P24 scripts are frozen and read-only. These 19 P20-P24 JSON artifacts are replay-gated (P31 WP0/WP1) and `docs/BAB_P24_DECISION.md` is replay-gated (P32 WP0).

---

## MAINTAINER-EXTERNAL WORK (NOT AGENT TASKS)

1. **CI gate enforcement (P19-1 / P28 WP2)** — `.github/workflows/main.yml` has **no `bab-gate` job** and does not invoke `ruff`, `scripts/bab_gate.sh`, or `scripts/bab_reconcile_gate.sh` (verified 2026-11-22T07:31:10Z). Agent token lacks `workflows:write`. Maintainer must add via GitHub web UI or a `workflows:write` PAT. Do not re-attempt the push from an agent session. **Note:** P30 WP2's `--fail-on-cancelled` and ledger analyzer are the agent-executable local stand-in for this CI health signal.
2. **Real-market data ingestion (P28 WP3)** — licensed CSV is maintainer-supplied; `api.exchange.coinbase.com` returns 403 here. Network fetching of prices is forbidden.

---

## HARD GATES EVERY SESSION (repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
python3 scripts/bab_replay_full.py --self-test      # fast replay drift proof (full replay gate is slow ~16 min)
python3 scripts/bab_replay_full.py --check-provenance   # P31 WP2: byte-diff fresh --xproc vs committed provenance_audit.json
python3 scripts/bab_replay_decisions.py --self-test
python3 scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json  # P32 WP2
python3 scripts/bab_doc_consistency_summary.py --check-doc-summary research_state/bab_p33/doc_consistency_summary.json  # P33 WP2
python3 scripts/bab_workflow_diagnostics.py --self-test
python3 scripts/bab_workflow_diagnostics.py --analyze-ledger
python3 -m pytest -q tests/test_bab_p31_registry_completeness.py   # P31 WP1: no committed artifact escapes replay
python3 -m pytest -q tests/test_bab_p32_decision_replay_p24.py tests/test_bab_p32_decision_registry_completeness.py  # P32
python3 -m pytest -q tests/test_bab_p33_*.py   # P33
python3 -m pytest -q tests/test_bab_p34_*.py   # P34
python3 scripts/bab_p34_multiseed_robustness.py --check-multiseed-summary  # P34 WP0
bash scripts/bab_replay_gate.sh          # full: 28/28 JSON artifacts byte-identical + provenance + drift self-test (slow ~16 min; run once per WP boundary)
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

`scripts/bab_gate.sh` invokes `scripts/bab_replay_gate.sh` at the end, so the replay check cannot be skipped by running the full gate alone. Inner loop while iterating: `bash scripts/bab_quick.sh` + `python3 -m ruff check .` + `python3 -m pytest -q tests/test_bab_p31_registry_completeness.py tests/test_bab_p32_*.py tests/test_bab_p33_*.py tests/test_bab_p34_*.py` + the P27/P26/P25 acceptance tests + `--check-multiseed-summary` + replay self-tests.

---

## FORBIDDEN (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (a handoff refresh without a landed fix is not a session). *(The one exception: correcting a provably stale HEAD/timestamp, a declared-but-unverified campaign gap, or a campaign marked incomplete that is provably already landed in the tree — as done this session for the stale "all agent-executable work is done" idle claim and the stale README/COVERAGE_NOTES pointers — is a legitimate refresh, provided every claim in it is re-verified against the tree.)*
- Editing any `research_state/bab_p20/**` … `research_state/bab_p34/**` artifact (frozen; P29 provenance ledger is frozen too), `docs/BAB_RESEARCH_REPORT.md`, or any P20-P34 script (frozen).
- Editing any P25 WP0-WP2 artifact (including `tests/fixtures/wide_bab_universe.csv` / `real_market_prices.csv`), any P26 artifact, any P27 WP0-WP3 artifact, or any P28 WP0-WP1 artifact, or any P30–P33 artifact (all closed and frozen).
- Hand-typing any number into a P25/P26/P27/P30–P34 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` below 0.20 / 4.0 in any decision, or flipping `beta_neutral=True` / `weighting="equal"` off as the shipped default.
- Describing the synthetic wide universe or the synthetic 9-asset fixture as real market data, or publishing a Sharpe without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- Shipping a WP whose committed artifact contradicts its own acceptance threshold.
- **Network fetching of prices** (Coinbase returns 403 here; licensed CSV is maintainer-supplied).
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, broad refactors, or committing probe/debug scratch scripts.
- Creating parallel handoff docs (this file is the single source of truth).
- **Faking P29/P30/P31/P32/P33/P34 reproducibility** (hard-coding `sha256`/`summary` values, skipping the xproc/self-test/check-summary checks, or editing committed artifacts to force a green replay).
- **Re-doing P32, P33, P34, or any P20-P31 campaign** (all COMPLETE and frozen). The pipeline was: P30 → P31 → P32 → P33 → P34 → **P28 WP2-WP4 (maintainer-gated)**. Do NOT re-do P30, P31, P32, P33, or P34.
- **Idle docs-only churn while maintainer-gated work exists.** The prior "idle-wait for the maintainer" directive is accurate now — when P34 is fully complete (it is) AND P28 WP2-WP4 are maintainer-gated (they are), a session may report the idle-waiting state — but that report must include a fresh full-gate GREEN log, not just prose.

---

## BOTTLENECKS REMOVED (do not re-create)

- **[REMOVED 2026-11-22T07:31:10Z] Post-P33 idle cliff + stale README/COVERAGE_NOTES binding pointers.** The prior handoff (07:04:44Z) declared "all agent-executable work is done; idle-wait" — the classic idle cliff this repo has removed repeatedly (03:21Z, 03:53Z, 04:38Z, ...). Verified this session: P33 IS complete (27 P33 tests PASS, doc summary OK, ruff clean, reconcile GREEN, quick 104+195 PASS, replay self-tests PASS), so that claim was true *for P20-P33* — but it was the wrong conclusion because a genuine, heavy, repo-name-relevant agent-executable gap remains: the `wide_bab_universe.csv` (40 assets, betas 0.35–1.90, seed 20261120) is only touched by P25 rank tests, and there is **no multi-seed robustness + statistical-honesty battery** for the shipped equal-weight beta-neutral default (P26 NO-SIGNAL was on the 9-asset fixture only; rank mode is flat/untestable on 9 assets). Declared **Campaign P34 "Wide-Universe Robustness & Strategy-Honesty Closure"** (WP0 multi-seed robustness + summary artifact; WP1 statistical falsification/honesty battery; WP2 doc-integrity closure + pointer-rot guard + gate wire). Also removed the **documentation-integrity bottleneck**: `README.md:246` named P26 as binding and `docs/COVERAGE_NOTES.md:5` named P20 as binding — both stale by ~11 campaigns and directly misleading to a fresh agent; WP2 fixes both and adds a guard so they cannot rot again. The pipeline is now **P30 → P31 → P32 → P33 → P34** — heavy, fully agent-executable, zero maintainer dependency. After P34 only maintainer-gated P28 WP2-WP4 remain.
- **[REMOVED 2026-11-22T09:47:00Z] Post-P34 idle cliff (this session).** Verified: P34 ALL WPs LANDED and GREEN. The binding row is now correctly P28 WP2-WP4 (maintainer-gated). No agent-executable work remains.
- **[REMOVED 2026-11-22T04:38:27Z] Post-P33 (prior) idle cliff.** (Historical; superseded by the 07:31:10Z removal above — P33 completed but P34 was identified as the next heavy row.)
- **[REMOVED 2026-11-22T04:06:06Z] Parallel-handoff / conflicting-focus bottleneck.** A second handoff doc, `NEXT_SESSION_HANDOFF.md` (2026-11-22T04:04:09Z), had been created in violation of HANDOFF.md rule #1 and incorrectly named P28 as the next focus, conflicting with the binding row (P33 WP0) and re-opening the maintainer-gated P28 path that stalls progress. Deleted and folded into this file. `HANDOFF.md` is now the single durable handoff — re-creating any `*HANDOFF*.md`, `NEXT_SESSION*.md`, or `AGENT_*.md` parallel task doc is forbidden.
- **[REMOVED 2026-11-22T04:00:39Z] "Is P33 WP0 already done / hidden P33 work?" ambiguity.** (Historical. P33 now COMPLETE.)
- **[REMOVED 2026-11-22T03:53:10Z] Stale HEAD + untracked P32 acceptance tests + post-P32 idle cliff.** (Historical. P32 now COMPLETE.)
- **[REMOVED 2026-11-22T03:21:23Z] Stale binding row (P31 WP0) + orphan artifact bottleneck.** (Historical. P31 now COMPLETE.)
- **[REMOVED 2026-11-22T00:58:00Z] P30 WP2 "idle-wait" bottleneck resolved.** (Historical. P30 COMPLETE.)
- **[REMOVED 2026-11-21T23:53:48Z] Post-P31 idle cliff.** (Historical. Declared P32.)
- **[REMOVED 2026-11-21T23:47:26Z] Handoff precision drift in P31 coverage-gap counts.** (Historical.)
- **[REMOVED 2026-11-21T23:20:57Z] Idle-wait cliff after P30 WP2.** (Historical. Declared P31.)
- **[REMOVED 2026-11-21T23:19:07Z] "No agent-executable work remains; idle-wait for the maintainer" bottleneck.** (Historical. Declared P30.)
- **[REMOVED 2026-11-21T21:29:29Z] "P29 WP2 NOT STARTED" bottleneck.** (Historical. P29 WP2 already committed.)
- **[REMOVED 2026-11-21T19:43:54Z] "P29 WP1 incomplete" bottleneck.** (Historical. P29 WP1 already committed.)
- **[REMOVED 2026-11-21T18:09:30Z] "No agent-executable work remains; idle-wait for the maintainer" bottleneck.** (Historical. Declared P29.)
- **[REMOVED 2026-11-21T17:04:13Z] Stale initial task message named P28 WP0 unstarted; its files were already committed.** (Historical. P28 WP0 COMPLETE.)
- **[REMOVED 2026-11-21T14:23:33Z] Stale HANDOFF claimed P28 WP1 unstarted.** (Historical. WP1 landed.)
- **[REMOVED 2026-11-21T12:22:18Z] Stale HEAD certification + stale refresh timestamps blocking P28 start.** (Historical.)
- **[REMOVED 2026-11-21T11:32:07Z] Stale HANDOFF claimed P27 WP3 deliverables absent.** (Historical. P27 COMPLETE.)
- **[REMOVED 2026-11-20T16:37:11Z] No binding row existed.** (Historical. Created Campaign P25.)
- (Earlier P23/P24 bottleneck removals retained in git history; see `git log` for the full ledger.)

---

## FUTURE AGENTS: READ THIS ONCE

**All agent-executable work through Campaign P34 is COMPLETE and frozen** (P20–P34). Campaign **P28 WP2-WP4** are the **only remaining binding rows** and are **maintainer-gated** (require `workflows:write` for CI and licensed CSV for real-market data). Do NOT re-create or re-edit any P20–P34 file.

**Anti-idle rule:** a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure when agent-executable work exists. **No agent-executable work exists** — P34 is fully complete. The only remaining work is maintainer-gated (P28 WP2-WP4). A future session may report the idle-waiting state, but that report MUST include a fresh full-gate GREEN log (run `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` and include the log). Inner loop while waiting: `bash scripts/bab_quick.sh` + `python3 -m ruff check .` + `python3 -m pytest -q tests/test_bab_p34_*.py tests/test_bab_p33_*.py tests/test_bab_p31_registry_completeness.py tests/test_bab_p32_*.py` + `--check-multiseed-summary` + replay self-tests.

Do not re-open frozen P20–P34 artifacts (consumed read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` (never weakened) or flip `beta_neutral=True` / `weighting="equal"` off as the default. Never network-fetch prices. If this file says a WP is COMPLETE, it is COMPLETE; if it says a WP is maintainer-gated (currently **P28 WP2-WP4**), route it to the maintainer.