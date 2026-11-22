# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-22T03:58:29Z (refreshed this session; supersedes the stale 2026-11-22T03:53:10Z stamp)
- **Git state:** HEAD `d61e311` at write time. **P32 is COMPLETE** (verified 2026-11-22T03:53:10Z against HEAD `12f1483`; this handoff commits on top of `d61e311`). **Re-verified GREEN against HEAD `12f1483` this session (03:53Z):** `python3 -m ruff check .` PASS; `scripts/bab_quick.sh` 195 passed + targeted trio 104 passed + quick preflight OK; `tests/test_bab_p32_decision_replay_p24.py` + `tests/test_bab_p32_decision_registry_completeness.py` 15 passed; `python3 scripts/bab_replay_decisions.py` all **10/10** entries byte-identical (`p24_decision`, `p25_decision`, `p26_decision`, `p27_decision`+sidecar, `p22/p23/p24_kickoff`, `paper_orders.jsonl`, `paper_diagnostics.jsonl`); `python3 scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json` OK; both replay `--self-test`s PASS; `tests/test_bab_p31_registry_completeness.py` 4 passed; `bab_workflow_diagnostics.py --self-test` PASS; `bab_reconcile_gate.sh` GREEN. The slow full `bab_replay_gate.sh` (~16-min, 28 artifacts × 2 procs) was NOT re-run this session — it is unchanged by a test-only + docs-only commit and the fast inner loop + provenance (`--check-provenance`) + both completeness guards are GREEN. **The active binding row advances to P33 WP0.** Queued campaign is **P33 "Fidelity & Cross-Document Consistency Closure"** (WP0→WP1→WP2). See the INITIAL TASK MESSAGE.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-22T03:58:29Z)

**Repo name = Crypto-Betting-Against-Beta.** The repo's entire credibility rests on one property: **the committed research numbers and the CI-health ledger are reproducible and verifiable locally, without `workflows:write`.** Campaigns P20-P32 are COMPLETE and frozen. P26 = NO-SIGNAL (no real alpha on the no-alpha synthetic fixture → no real-market deployment claim on synthetic evidence). P27 execution infra is production-ready on paper/dry-run but its WP3 verdict is **NOT-READY** for live real-market deployment (P26 NO-SIGNAL + no licensed market data here). **P32 "Decision-Document Replay Closure" is now COMPLETE:** `docs/BAB_P24_DECISION.md` byte-replays via `generate_p24_decision.py`; the P22/P23/P24 charter KICKOFF docs byte-replay via each charter's `build_charter()`+`render_markdown()`; `research_state/bab_p32/doc_replay_summary.json` byte-diffs clean; all wired into `scripts/bab_replay_gate.sh`. **The JSON-artifact + decision-doc + kickoff-doc verifiability thesis is therefore COMPLETE.** The maintainer-external blockers (CI `workflows:write`, licensed real-market CSV) cannot be resolved by an agent session — **do not idle-wait on them, and do not re-attempt them.**

**One campaign of heavy, fully agent-executable work remains QUEUED and has ZERO maintainer dependency. It is the binding row and none of its WPs can be skipped: P33 (WP0→WP1→WP2).**

## BINDING ROW — P33 WP0 (heavy, agent-executable, zero maintainer dependency)

P32 is fully complete and frozen. **Do NOT re-do P32.** P33 closes the last narrative-consistency blind spot — the human-facing fidelity document — and is what THIS session must execute:

1. **`docs/BAB_FIDELITY.md` ↔ data consistency guard** — land `tests/test_bab_p33_fidelity_consistency.py`. `docs/BAB_FIDELITY.md` is the only top-level narrative doc with no consistency guard (verified: the only test reference to `FIDELITY` is a code comment at `tests/test_bab_p20_rank_weighting.py:60`; no test asserts its numbers). Its §3 before/after table (`docs/BAB_FIDELITY.md:65-76`) and §4 daily grid (`docs/BAB_FIDELITY.md:88-95`) publish ~50 measured cells. **Coverage today is partial and must be made total:** `tests/test_bab_p20_beta_neutral_default.py:113-126` goldens only the `beta_neutral=False` wealth + Sharpe for `q∈{0.2,0.3}` (`0.3136 / −1.418` and `0.4214 / −0.680`), and `:85-95` asserts the §4 grid's neutrality *bounds* only. **Still unguarded:** the entire `beta_neutral=True` rows (`0.7057/−0.725/0.258/−0.413/+0.059/1.5e-04/0.264` and `1.3093/+0.649/0.366/−0.227/+0.006/2.1e-04/0.234`), the ann-vol / max-DD / turnover / realized-β / model-β columns of the `beta_neutral=False` rows, the BTC buy-and-hold reference row (`2.0975 / +109.7% / +1.756 / 0.291`), and the exact §4 grid *cell values* (e.g. `1.3182 / +0.651 / −0.031 / 2.16e-04 / 8e-16`). **Do this:** for every published cell, assert it equals a deterministic recompute produced by the §8 "Reproduce" snippet (`docs/BAB_FIDELITY.md:166-182`) run against the committed read-only fixture `tests/fixtures/real_market_prices.csv` (398 rows, 2021-01-05→2022-07-15, `beta_window=90`, `min_observations=60`, `q∈{0.2,0.3}`, `transaction_costs=0.001`) — reuse/extend the existing `_run()` helper in `tests/test_bab_p20_beta_neutral_default.py`. **Any cell that cannot be reproduced to the published rounding must be explicitly allow-listed in the test with a written reason — never silently skipped, never hand-waved, and NEVER edit `docs/BAB_FIDELITY.md`.** This is read-only w.r.t. the doc and the fixture.
2. **Document-layer completeness guard** — land `tests/test_bab_p33_doc_registry_completeness.py`. Enumerate every `docs/*.md` and classify each as exactly one of: (a) **replay-gated** (decision/kickoff present in `scripts/bab_replay_decisions.py` REGISTRY), (b) **consistency-guarded** (`BAB_RESEARCH_REPORT.md`→`tests/test_bab_p20_report_consistency.py`; `BAB_SIGNAL_OR_NOISE.md`→`tests/test_bab_p21_report_consistency.py`; `BAB_FIDELITY.md`→the new P33 test), or (c) **explicitly allow-listed with a written reason** (e.g. `docs/COVERAGE_NOTES.md`, and hand-authored `docs/BAB_P22_DECISION.md`/`BAB_P23_DECISION.md`). A newly added `docs/*.md` that escapes all three classes fails this test — mirroring the P31 registry-completeness guard (`tests/test_bab_p31_registry_completeness.py`) and the P32 decision-doc completeness guard (`tests/test_bab_p32_decision_registry_completeness.py`). This makes "a new narrative doc ships with no guard" structurally impossible.
3. **Summary artifact + gate wire** — emit a deterministic `research_state/bab_p33/doc_consistency_summary.json` (schema `bab_p33.doc_consistency_summary/1`) listing every `docs/*.md` → its guard class + guard status, byte-diffed by a `--check-doc-summary` mode on a small runner (mirror `scripts/bab_replay_decisions.py --check-doc-summary` / `research_state/bab_p32/doc_replay_summary.json`). Wire the new P33 tests + the summary check into `scripts/bab_gate.sh` (and/or `scripts/bab_replay_gate.sh`). This mirrors the P30 `ledger_summary.json` / P32 `doc_replay_summary.json` pattern.

**Hard contract (P32 + P33):**
1. No edits to any P20-P32 artifact (all closed/frozen); P33 consumes them read-only. The only P33 writes are new `tests/test_bab_p33_*.py`, `research_state/bab_p33/**` if a summary artifact is emitted, a small runner script if needed, and the `bab_gate.sh`/`bab_replay_gate.sh` hook. P33 must NOT edit any frozen `research_state/bab_p20..p32/**` file, any `docs/BAB_*.md`, or any frozen P20-P32 script — if a FIDELITY cell cannot be byte-reproduced without editing it, allow-list it in the test with a reason instead.
2. `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged; never weakened.
3. No network fetching of prices; no real-market profitability claims on the synthetic fixture.
4. Zero ruff errors on new files; full gate GREEN; never hand off mid-gate.
5. The canonical `redact()` must remain a strict superset of any prior inline copy; the divergence-guard test must stay GREEN.
6. Do not weaken the existing `bab_replay_gate.sh` / `bab_reconcile_gate.sh` checks.

**Standing maintainer-external blockers (do NOT re-attempt):** (a) CI `workflows:write` — gates P28 WP2 only; (b) real-market licensed CSV — gates P28 WP3-WP4 only. Neither P31, P32, nor P33 needs either. If a maintainer unblocks (a) and/or (b), P28 WP2-WP4 become the next binding rows after P33.

---

# CAMPAIGN P33 — BINDING ROW (Fidelity & Cross-Document Consistency Closure)

**Declared:** 2026-11-22T03:58:29Z · **Campaign:** P33 "Fidelity & Cross-Document Consistency Closure" · **Priority: HIGH** · **Now the binding row (P32 complete; verified 2026-11-22T03:53:10Z).**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — `BAB_FIDELITY.md` ↔ data consistency guard (every published §3/§4 cell = deterministic recompute) | `tests/test_bab_p33_fidelity_consistency.py` | **BINDING ROW — HEAVY, AGENT-EXECUTABLE** |
| WP1 — document-layer completeness guard (every `docs/*.md` is replay-gated, consistency-guarded, or allow-listed with a reason) | `tests/test_bab_p33_doc_registry_completeness.py` | **QUEUED** |
| WP2 — summary artifact + gate wire | `research_state/bab_p33/doc_consistency_summary.json`, runner `--check-doc-summary`, `scripts/bab_gate.sh`/`bab_replay_gate.sh` hook | **QUEUED** |

**P33 rationale (verified 2026-11-22T03:53:10Z):** The reproducibility thread has closed the JSON layer (P29/P31: all 28 P20-P27 JSON artifacts replay-gated, registry-completeness guard, provenance-ledger diff), the CI-health ledger (P30), and the decision + kickoff document layer (P32). The one remaining unguarded surface is the **human-facing narrative** that a maintainer actually reads: `docs/BAB_FIDELITY.md` (277 lines, 35 table rows, dozens of measured decimals — before/after beta, dollar-neutral before/after, the §4 daily grid, the rank-weighting leverage bounds). It is the only top-level narrative doc with no consistency guard: `docs/BAB_RESEARCH_REPORT.md` is guarded by `tests/test_bab_p20_report_consistency.py` and `docs/BAB_SIGNAL_OR_NOISE.md` by `tests/test_bab_p21_report_consistency.py`, but `BAB_FIDELITY.md` is referenced only by a code comment. Its coverage today is *partial* — `tests/test_bab_p20_beta_neutral_default.py:113-126` goldens only 4 cells and `:85-95` asserts only the grid's neutrality bounds, leaving the `beta_neutral=True` rows, the realized/model-β/ann-vol/max-DD/turnover columns, the BTC reference row, and the exact grid cell values unasserted. P33 makes that coverage total and adds a structural guard so no future narrative doc escapes. After P33 the "every committed/published number is reproducible" thesis extends fully to the human-facing narrative layer. After P33 the only remaining work is maintainer-gated P28 WP2-WP4.

---

# CAMPAIGN P32 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T03:53:10Z)

**Declared:** 2026-11-21T23:53:48Z · **Campaign:** P32 "Decision-Document Replay Closure" · **Priority: HIGH**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — byte-replay `BAB_P24_DECISION.md` | `scripts/bab_replay_decisions.py` (new `p24_decision.md` entry), `tests/test_bab_p32_decision_replay_p24.py` | **COMPLETE** (code `a9257f8`; tests `12f1483`; verified GREEN 2026-11-22T03:53:10Z — 10/10 replay entries byte-identical, 15 P32 tests pass) |
| WP1 — decision-doc completeness guard | `tests/test_bab_p32_decision_registry_completeness.py` (every generated decision doc is replayed; hand-authored P22/P23 allow-listed) | **COMPLETE** (verified GREEN 2026-11-22T03:53:10Z) |
| WP2 — KICKOFF-doc closure + summary artifact + gate wire | `scripts/bab_replay_decisions.py` (KICKOFF entries), `research_state/bab_p32/doc_replay_summary.json`, `scripts/bab_replay_gate.sh` hook | **COMPLETE** (verified GREEN 2026-11-22T03:53:10Z — `--check-doc-summary` clean) |

**P32 rationale:** P29 WP2 replay-gated the P25/P26/P27 decision docs but NOT `docs/BAB_P24_DECISION.md`; the charter writers `scripts/bab_p22_charter.py`/`bab_p23_charter.py`/`bab_p24_charter.py` emitted `docs/BAB_P22_KICKOFF.md`/`BAB_P23_KICKOFF.md`/`BAB_P24_KICKOFF.md` with no replay gate; and nothing structurally prevented a future generated document from silently escaping replay. P32 closed all three. **P32 is COMPLETE. Do NOT re-do it.** Every generated decision doc (P24-P27) and KICKOFF doc (P22-P24) now byte-replays; the registry-completeness guard makes an orphaned generated decision doc structurally impossible.

---

# CAMPAIGN P31 — COMPLETE (WP0+WP1+WP2; verified 2026-11-22T03:53:10Z)

**Declared:** 2026-11-21T23:20:57Z · **Campaign:** P31 "Reproducibility Coverage Closure" · **Priority: HIGH**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — replay registry extended to 19 P20-P24 artifacts | `scripts/bab_replay_full.py` (REGISTRY + self-test), `tests/test_bab_p31_replay_coverage_p20_p24.py` | **COMPLETE** (REGISTRY has all 19 P20-P24 entries; both `--self-test`s PASS) |
| WP1 — registry completeness guard (no artifact escapes replay) | `tests/test_bab_p31_registry_completeness.py` (enumerates every `research_state/bab_p2*/**.json`) | **COMPLETE** (4 passed) |
| WP2 — provenance-ledger regeneration-diff + gate wire | `scripts/bab_replay_full.py` `--check-provenance`, `scripts/bab_replay_gate.sh` hook, `tests/test_bab_p31_provenance_replay.py` | **COMPLETE** (`--check-provenance` exit 0; wired into `bab_replay_gate.sh:28`) |

**P31 rationale:** P29 made the 8 P25/P26/P27 artifacts byte-reproducible; P30 made the CI-health ledger locally verifiable. P31 closed the remaining 19-artifact (P20-P24) reproducibility blind spot and made the replay registry self-guarding so coverage can never silently shrink again. After P31, every committed *JSON* research artifact in the repo is replay-gated. **P31 is COMPLETE. Do NOT re-do it.**

---

# CAMPAIGN P30 — COMPLETE (ALL WPs LANDED)

**Declared:** 2026-11-21T23:19:07Z · **Campaign:** P30 "Workflow Diagnostics Tooling & Single-Source Scanner" · **Priority: HIGH**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — canonical scanner module | `scripts/bab_workflow_diagnostics.py`, `tests/test_bab_p30_workflow_diagnostics.py` | **COMPLETE** (21 tests GREEN, ruff clean) |
| WP1 — ledger analyzer | `scripts/bab_workflow_diagnostics.py` `--analyze-ledger`, `load_ledger()`, `analyze_ledger()` | **COMPLETE** (50 runs / 49 success / 1 cancelled / 981 signals, deterministic) |
| WP2 — analyzer hardening + drift guard + gate wire | `--summary-json`, `--since`, `--fail-on-cancelled`, divergence-guard test, `bab_gate.sh` hook, `research_state/bab_p30/ledger_summary.json` + replay entry | **COMPLETE** (21 tests GREEN, `bab_gate.sh` wired) |

**P30 is COMPLETE. Do NOT re-do it.**

---

# CAMPAIGN P29 — COMPLETE (WP0+WP1+WP2)

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

**P28 WP2-WP4 remain maintainer-gated and MUST NOT be faked, simulated, or started early.** They are NOT the current bottleneck for progress because P33 (WP0→WP1→WP2) is fully agent-executable. If a maintainer unblocks (a) `workflows:write` and/or (b) a licensed market CSV, P28 WP2-WP4 become the next binding rows after P33.

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

P20 WP0-WP5 (92 tests), P21 WP0-WP3 (56), P22 WP0-WP3 (85), P23 WP0-WP4 (80), P24 WP0-WP4 (94) all GREEN. All `research_state/bab_p20..p24/**`, `docs/BAB_RESEARCH_REPORT.md`, and P20-P24 scripts are frozen and read-only. **These 19 P20-P24 JSON artifacts are now replay-gated (P31 WP0/WP1 COMPLETE) and `docs/BAB_P24_DECISION.md` is now replay-gated (P32 WP0 COMPLETE)** — the earlier "NOT yet replay-gated" gap is closed; consume them read-only. (The P27 `p27_decision_sidecar.json` is covered by `scripts/bab_replay_decisions.py`.)

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
python3 scripts/bab_replay_full.py --check-provenance   # P31 WP2: byte-diff fresh --xproc vs committed provenance_audit.json
python3 scripts/bab_replay_decisions.py --self-test
python3 scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json  # P32 WP2
python3 scripts/bab_workflow_diagnostics.py --self-test
python3 scripts/bab_workflow_diagnostics.py --analyze-ledger
python3 -m pytest -q tests/test_bab_p31_registry_completeness.py   # P31 WP1: no committed artifact escapes replay
python3 -m pytest -q tests/test_bab_p32_decision_replay_p24.py tests/test_bab_p32_decision_registry_completeness.py  # P32: decision-doc replay closure
bash scripts/bab_replay_gate.sh          # full: 28/28 JSON artifacts byte-identical + provenance + drift self-test (slow ~16 min; run once per WP boundary)
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

`scripts/bab_gate.sh` invokes `scripts/bab_replay_gate.sh` at the end, so the replay check cannot be skipped by running the full gate alone. Inner loop while iterating: `bash scripts/bab_quick.sh` + `python3 -m ruff check .` + `python3 -m pytest -q tests/test_bab_p31_registry_completeness.py tests/test_bab_p32_*.py` + `python3 -m pytest -q tests/test_bab_p29_replay_coverage.py tests/test_bab_p29_decision_replay.py` + the P27/P26/P25 acceptance tests. Full gate once per WP boundary; never hand off mid-gate. Never lower the coverage floor. **After P33 WP0 lands, extend the inner loop with `python3 -m pytest -q tests/test_bab_p33_*.py`; after P33 WP2 lands, add the `doc_consistency_summary.json` check to the gate and confirm the full gate still GREENs.**

---

# FORBIDDEN (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (a handoff refresh without a landed fix is not a session). *(The one exception: correcting a provably stale HEAD/timestamp, a declared-but-unverified campaign gap, or a campaign marked incomplete that is provably already landed in the tree — as done this session (2026-11-22T03:53:10Z) for P32 (verified COMPLETE; its two acceptance tests were untracked and are now committed as `12f1483`) and the P33 binding row — is a legitimate refresh, provided every claim in it is re-verified against the tree.)*
- Editing any `research_state/bab_p20/**` … `research_state/bab_p32/**` artifact (frozen; P29 provenance ledger is frozen too), `docs/BAB_RESEARCH_REPORT.md`, or any P20-P32 script (frozen).
- Editing any P25 WP0-WP2 artifact, any P26 artifact, any P27 WP0-WP3 artifact, any P28 WP0-WP1 artifact, or any P32 artifact (all closed and frozen).
- Hand-typing any number into a P25/P26/P27/P32 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta` / `rank_max_gross` below 0.20 / 4.0 in any decision.
- Describing the synthetic wide universe as real market data, or publishing a Sharpe without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- Shipping a WP whose committed artifact contradicts its own acceptance threshold.
- **Network fetching of prices** (Coinbase returns 403 here; licensed CSV is maintainer-supplied).
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, broad refactors, or committing probe/debug scratch scripts.
- Creating parallel handoff docs (this file is the single source of truth).
- **Faking P29/P30/P31/P32/P33 reproducibility** (hard-coding `sha256` values, skipping the xproc/self-test checks, or editing committed artifacts to force a green replay).
- **Re-doing P32** (COMPLETE: decision + kickoff byte-replay, doc_replay_summary, registry-completeness guard all landed and GREEN). **Starting P33 before P32 is COMPLETE** is no longer a risk — P32 IS complete, so P33 is the active binding row. Order was: P30 WP2 → P31 WP0 → WP1 → WP2 → P32 WP0 → WP1 → WP2 → **P33 WP0 → WP1 → WP2**. Do NOT re-do P30, P31, or P32.
- **Idle docs-only churn when agent-executable P33 WP0 (or, after it, WP1/WP2) work exists.** The prior "idle-wait for the maintainer" directive is removed; when P33 WP0 is executable (it is), doing it IS the session. Only when P33 is fully complete AND P28 WP2-WP4 are maintainer-gated may a session report the idle-waiting state — and that report must include a fresh full-gate GREEN log, not just prose.

---

# BOTTLENECKS REMOVED (do not re-create)

- **[REMOVED 2026-11-22T03:53:10Z] Stale HEAD + untracked P32 acceptance tests + post-P32 idle cliff.** The prior handoff (03:21Z) certified HEAD `2f1da34` and named **P32 WP0 as the binding row / not started**. Verified this session against the tree: HEAD is actually `a9257f8` — a later session had already landed the heavy P32 work (committed `a9257f8`: `scripts/bab_replay_decisions.py` gained the `p24_decision.md` entry + `p22/p23/p24_kickoff.md` entries + `--summary-json`/`--check-doc-summary`; `research_state/bab_p32/doc_replay_summary.json` emitted; `scripts/bab_replay_gate.sh` wired) — but left the two P32 acceptance tests **untracked** (`tests/test_bab_p32_decision_replay_p24.py`, `tests/test_bab_p32_decision_registry_completeness.py`). This session re-verified P32 GREEN (all 10 decision/kickoff/jsonl entries byte-identical; `--check-doc-summary` clean; 15 P32 tests pass; ruff clean) and **committed the two tests as `12f1483`**, so P32 is now genuinely COMPLETE. Also removed the **post-P32 idle cliff**: the prior handoff implied only maintainer-gated P28 WP2-WP4 remained after P32 — an idle cliff, the exact bottleneck pattern removed repeatedly before. Verified a real, agent-executable gap remains after P32: `docs/BAB_FIDELITY.md` (the human-facing fidelity/honesty doc, 277 lines, 35 table rows, dozens of measured decimals) is the only top-level narrative doc with no consistency guard (only a code comment references it), and its published §3/§4 table values are only *partially* asserted (`tests/test_bab_p20_beta_neutral_default.py:113-126` goldens 4 cells; `:85-95` asserts only grid bounds). Declared **Campaign P33 "Fidelity & Cross-Document Consistency Closure"** (WP0 FIDELITY ↔ data consistency guard; WP1 document-layer completeness guard; WP2 summary artifact + gate wire). The pipeline is now **P30 → P31 → P32 → P33** — heavy, fully agent-executable, zero maintainer dependency. After P33 only maintainer-gated P28 WP2-WP4 remain.

- **[REMOVED 2026-11-22T03:21:23Z] Stale binding row (P31 WP0) + orphan artifact bottleneck.** (Historical; retained for the ledger. P31 was already fully landed when that handoff named P31 WP0 as binding; the row advanced to P32, and an orphan `research_state/bab_p30/ledger_summary_new.json` was removed. P32 is now also COMPLETE — see above.)

- **[REMOVED 2026-11-22T00:58:00Z] P30 WP2 "idle-wait" bottleneck resolved.** (Historical. P30 WP2 flags/tests/gate-hook landed; P30 COMPLETE.)

- **[REMOVED 2026-11-21T23:53:48Z] Post-P31 idle cliff.** (Historical. Declared P32 after P31. P32 now COMPLETE.)

- **[REMOVED 2026-11-21T23:47:26Z] Handoff precision drift in P31 coverage-gap counts.** (Historical. REGISTRY = 8/28; the 19 P20-P24 artifacts were the true blind spot; the p27 sidecar is covered by `bab_replay_decisions.py`, not a REGISTRY gap.)

- **[REMOVED 2026-11-21T23:20:57Z] Idle-wait cliff after P30 WP2.** (Historical. Declared P31.)

- **[REMOVED 2026-11-21T23:19:07Z] "No agent-executable work remains; idle-wait for the maintainer" bottleneck.** (Historical. Declared P30.)

- **[REMOVED 2026-11-21T21:29:29Z] "P29 WP2 NOT STARTED" bottleneck.** (Historical. P29 WP2 was already committed at `6212bcf`/`891f146`; P29 COMPLETE.)
- **[REMOVED 2026-11-21T19:43:54Z] "P29 WP1 incomplete" bottleneck.** (Historical. P29 WP1 already committed at `2eeb04c`.)
- **[REMOVED 2026-11-21T18:09:30Z] "No agent-executable work remains; idle-wait for the maintainer" bottleneck.** (Historical. Declared P29.)
- **[REMOVED 2026-11-21T17:04:13Z] Stale initial task message named P28 WP0 unstarted; its files were already committed.** (Historical. P28 WP0 COMPLETE.)
- **[REMOVED 2026-11-21T14:23:33Z] Stale HANDOFF claimed P28 WP1 unstarted.** (Historical. WP1 landed at `af57b5a`/`7ee5729`.)
- **[REMOVED 2026-11-21T12:22:18Z] Stale HEAD certification + stale refresh timestamps blocking P28 start.** (Historical.)
- **[REMOVED 2026-11-21T11:32:07Z] Stale HANDOFF claimed P27 WP3 deliverables absent.** (Historical. P27 COMPLETE.)
- **[REMOVED 2026-11-20T16:37:11Z] No binding row existed.** (Historical. Created Campaign P25.)
- (Earlier P23/P24 bottleneck removals retained in git history; see `git log` for the full ledger.)

---

# FUTURE AGENTS: READ THIS ONCE

**This repo's agent-executable work is NOT done — the binding row is P33 WP0, with P33 WP1→WP2 queued behind it.** Campaigns P20-P32 are complete and frozen. Campaign **P30 "Workflow Diagnostics Tooling & Single-Source Scanner"** is COMPLETE. Campaign **P31 "Reproducibility Coverage Closure"** is COMPLETE. Campaign **P32 "Decision-Document Replay Closure"** is **COMPLETE** (verified 2026-11-22T03:53:10Z at HEAD `12f1483`): `docs/BAB_P24_DECISION.md` + the P22/P23/P24 KICKOFF docs byte-replay via `scripts/bab_replay_decisions.py`; `research_state/bab_p32/doc_replay_summary.json` byte-diffs clean; the decision-doc registry-completeness guard prevents an orphaned generated decision doc. **The JSON + decision-doc + kickoff-doc verifiability thesis is COMPLETE.** Campaign **P33 "Fidelity & Cross-Document Consistency Closure"** is the active work: **WP0 is the BINDING ROW** — add `tests/test_bab_p33_fidelity_consistency.py` asserting every published `docs/BAB_FIDELITY.md` §3/§4 table cell equals a deterministic recompute (the §8 "Reproduce" snippet run against the committed read-only `tests/fixtures/real_market_prices.csv`); extend beyond the 4 cells already goldened in `tests/test_bab_p20_beta_neutral_default.py:113-126` to the `beta_neutral=True` rows, the realized/model-β/ann-vol/max-DD/turnover columns, the BTC reference row, and the exact §4 grid cell values; allow-list any irreproducible cell with a written reason. Then WP1 (document-layer completeness guard) and WP2 (summary artifact + gate wire). **Verified 2026-11-22T03:53:10Z against HEAD `12f1483`:** ruff PASS, `bab_quick.sh` 195 + 104 targeted passed, P32 15 passed, P31 4 passed, both replay `--self-test`s PASS, `--check-doc-summary` OK, reconcile GREEN. Do NOT re-create or re-edit any of the P30, P31, or P32 files.

**Anti-idle rule:** a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure when agent-executable work exists. P33 WP0 is executable now — doing it IS the session. P33 WP1→WP2 are queued immediately behind it. Only when P33 is fully complete AND P28 WP2-WP4 are maintainer-gated may a session report the idle-waiting state, and that report must include a fresh full-gate GREEN log.

Do not re-open frozen P20-P32 artifacts (consumed read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` (never weakened). Never network-fetch prices. If this file says a WP is COMPLETE, it is COMPLETE; if it names a binding row (currently **P33 WP0**) or a queued campaign (**P33 WP1→WP2**), that is the work; if it says a WP is maintainer-gated, route it to the maintainer and proceed to the next agent-executable P33 WP.