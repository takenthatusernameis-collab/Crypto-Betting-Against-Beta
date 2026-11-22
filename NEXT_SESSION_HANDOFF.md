# NEXT SESSION HANDOFF — Crypto Betting Against Beta (BAB)
**Timestamp:** 2026-11-22T04:04:09Z
**Repository:** Crypto-Betting-Against-Beta
**Branch/State:** Mainline, all campaigns P20–P32 artifacts committed and replay-verified

---

## 🎯 EXECUTIVE SUMMARY: WHERE WE ARE

| Campaign | Status | Verdict | Key Artifact |
|----------|--------|---------|--------------|
| **P20** | ✅ Done | Research sweep / walk-forward / breakeven | `bab_p20/*.json` |
| **P21** | ✅ Done | Universe / cost surface / rank eval / significance | `bab_p21/*.json` |
| **P22** | ✅ Done | Capacity / impact surface / null battery (charter) | `bab_p22/*.json` |
| **P23** | ✅ Done | Beta drift / breadth ladder / short haircut (charter) | `bab_p23/*.json` |
| **P24** | ✅ Done | Hysteresis / regime split / adapter dry-run (decision) | `docs/BAB_P24_DECISION.md` |
| **P25** | ✅ Done | **PROMOTE** rank-weighting via wide-universe OOS | `docs/BAB_P25_DECISION.md` |
| **P26** | ✅ Done | **NO-SIGNAL** on no-alpha synthetic fixture | `docs/BAB_P26_DECISION.md` |
| **P27** | ✅ Done | **NOT-READY** production infra ready, but no signal + no license | `docs/BAB_P27_DECISION.md`, `p27_decision_sidecar.json` |
| **P28** | ❌ **MISSING** | — | — |
| **P29** | ✅ Done | Provenance audit: 8/8 artifacts replay OK | `bab_p29/provenance_audit.json` |
| **P30** | ✅ Done | Workflow diagnostics: 50 runs, all errored (expected) | `bab_p30/ledger_summary.json` |
| **P31** | ❌ **MISSING** | — | — |
| **P32** | ✅ Done | Doc replay summary: 7/7 decision+kickoff docs byte-identical | `bab_p32/doc_replay_summary.json` |

**Critical Constraint:** P26 returned **NO-SIGNAL** (rank p=0.285714, equal p=0.358641; regime stress Assertion B fails; capacity premium is mechanical idio spread).
**Consequence:** No real-market deployment claim is made. P27 infrastructure is production-grade on paper/dry-run but gated by `no_market_data_license: true` and `p26_signal_verdict: "NO-SIGNAL"`.

---

## 🧱 BOTTLENECKS REMOVED / INFRASTRUCTURE IN PLACE

1. **Deterministic replay harness** (`scripts/bab_replay_decisions.py`) — byte-identical regeneration of all decision docs, KICKOFF docs, and P27 JSONL sidecars. Exit code 0 on clean tree.
2. **Provenance audit** (`scripts/bab_replay_full.py`) — verifies 8/8 research artifacts replay against committed fixture SHA256.
3. **Document replay summary** (`bab_p32/doc_replay_summary.json`) — 7/7 decision+kickoff docs confirmed byte-identical.
4. **Production-grade risk controls & reconciliation** (P27 WP0–WP2) — kill-switch, position limits, staleness, E2E fill/cost reconciliation with drift gates, all tripping on synthetic stress paths.
5. **No network / no lookahead / synthetic-labelled** — every artifact is auditable, deterministic, and explicitly **not market evidence**.

---

## 🚀 NEXT FOCUS CAMPAIGN: P28 — "MECHANICS-ONLY PLANTED-ALPHA FIXTURE"

**Mandate from P26 Next Steps (verbatim):**
> "Do not edit the frozen P25 WP0 fixture to 'plant' alpha to force SIGNAL; if a mechanics-only planted-alpha fixture is desired, it is a NEW campaign (P28) with its own frozen fixture, clearly labelled 'planted mechanics, not market evidence.'"

### P28 Charter (must be defined by next session)
| Work Package | Objective |
|--------------|-----------|
| **WP0** | Generate a **new frozen fixture** `tests/fixtures/planted_alpha_bab_universe.csv` with known cross-sectional alpha planted (e.g., `r = beta·r_BTC + alpha_signal + idio`, `alpha_signal` correlated with rank). Fixture SHA256 committed, seed fixed, labelled `planted_mechanics: true`, `not_market_evidence: true`. |
| **WP1** | Re-run **signal vs null battery** (P26 WP0) on planted fixture → expect **SIGNAL** verdict (p_rank < 0.05, p_equal > 0.05). |
| **WP2** | Re-run **regime stress** (P26 WP1) on planted fixture → expect falsification gate to pass. |
| **WP3** | Re-run **capacity & turnover** (P26 WP2) on planted fixture → validate rank premium survives capacity. |
| **WP4** | **Closing decision doc** `docs/BAB_P28_DECISION.md` + sidecar JSON with explicit `SIGNAL` verdict, all criteria traced to committed JSON leaves. |

**Why P28 now:** It isolates the *mechanics* of the rank-weighted BAB pipeline (signal detection, regime stress, capacity) under a known-alpha ground truth, without conflating with real-market evidence. This is the **only** way to validate the pipeline end-to-end before licensed data arrives.

---

## 🔜 FOLLOW-ON CAMPAIGN: P31 — "LICENSED MARKET DATA INTEGRATION"

**Prerequisite:** Maintainer supplies licensed market data fixture (Coinbase/other — never network-fetch; Coinbase returns 403).
**Scope:**
- WP0: Ingest licensed fixture → freeze SHA256, label `licensed_market_data: true`.
- WP1: Re-run P25/P26/P27 pipeline on licensed fixture → produce **real-market** signal verdict.
- WP2: If SIGNAL on licensed data → P27 `NOT-READY` → `READY` transition with live health check `dry_run=false` (explicit opt-in).
- WP3: Decision doc `docs/BAB_P31_DECISION.md` with explicit `SIGNAL` / `NO-SIGNAL` on **real market data**.

**Gate:** P31 **cannot start** until licensed fixture is provided. Do not simulate. Do not fetch.

---

## 🛠 IMMEDIATE ACTIONABLE TASKS FOR NEXT SESSION

### 1. Create P28 Campaign Scaffold (HIGH PRIORITY)
```bash
# Create charter script (mirror bab_p22_charter.py pattern)
# scripts/bab_p28_charter.py
#   - build_charter(): defines WP0–WP4, seeds, fixture paths, labels
#   - render_markdown(): emits docs/BAB_P28_KICKOFF.md
#   - write_artifacts(): writes research_state/bab_p28/charter.json + .md

# Create planted-alpha fixture generator
# scripts/generate_planted_alpha_fixture.py
#   - deterministic, seed=20261122 (or next unused)
#   - plants alpha_signal ~ N(0.0005, 0.0001) correlated with rank percentile
#   - outputs: tests/fixtures/planted_alpha_bab_universe.csv + _meta.json
#   - commits SHA256 to charter
```

### 2. Wire P28 into Replay Harness
- Add `p28_kickoff.md` and `p28_decision.md` entries to `REGISTRY` in `scripts/bab_replay_decisions.py`.
- Add `generate_p28_decision.py` (reads P28 WP0–WP3 JSON, renders decision doc).

### 3. Run P28 WP0–WP3 Scripts (can parallelize)
- `bab_signal_null_battery.py` → `research_state/bab_p28/signal_null_battery.json`
- `bab_p26_regime_stress.py` (adapted) → `research_state/bab_p28/regime_stress.json`
- `bab_rank_capacity.py` (adapted) → `research_state/bab_p28/rank_capacity.json`

### 4. Generate P28 Decision Doc
- `generate_p28_decision.py` → `docs/BAB_P28_DECISION.md` + `research_state/bab_p28/p28_decision_sidecar.json`
- Verify `replay_ok: true` via `bab_replay_decisions.py --subset p28_decision.md,p28_kickoff.md`

---

## 🔒 NON-NEGOTIABLE RULES (ENFORCED BY REPLAY HARNESS)

1. **Never edit frozen fixtures** (P25 WP0 `wide_bab_universe.csv`, P28 WP0 `planted_alpha_bab_universe.csv`). New fixture = new campaign.
2. **Never network-fetch** market data. Licensed data is maintainer-supplied only.
3. **Every number in decision docs** must trace to a committed JSON leaf (6 dp). Replay harness enforces byte-identity.
4. **Verdict strings** must be explicit: `SIGNAL` / `NO-SIGNAL` / `PROMOTE` / `NOT-READY` / `READY` / `controlled synthetic` / `planted mechanics, not market evidence` / `licensed market data`.
5. **No lookahead** — rolling betas through t-1 only; stress paths synthetic.
6. **Synthetic label** — every artifact carries `"synthetic": true` (or `"licensed_market_data": true` for P31+).

---

## 📂 KEY FILES TO READ FIRST IN NEXT SESSION

| File | Purpose |
|------|---------|
| `scripts/bab_p22_charter.py` | Template for P28 charter (WP structure, rendering, artifact writing) |
| `scripts/generate_p26_decision.py` | Template for `generate_p28_decision.py` (reads 3 JSON, renders tables, decision criteria) |
| `scripts/bab_signal_null_battery.py` | WP0 signal vs null battery — adapt for P28 planted fixture |
| `scripts/bab_p26_regime_stress.py` | WP1 regime stress — adapt for P28 planted fixture |
| `scripts/bab_rank_capacity.py` | WP2 capacity — adapt for P28 planted fixture |
| `scripts/bab_replay_decisions.py` | Replay registry — add P28 entries |
| `research_state/bab_p26/signal_null_battery.json` | Example WP0 output structure |
| `research_state/bab_p26/regime_stress.json` | Example WP1 output structure |
| `research_state/bab_p26/rank_capacity.json` | Example WP2 output structure |

---

## ✅ DEFINITION OF DONE FOR NEXT SESSION

- [ ] `scripts/bab_p28_charter.py` created, emits `docs/BAB_P28_KICKOFF.md` + `research_state/bab_p28/charter.json`
- [ ] `scripts/generate_planted_alpha_fixture.py` created, emits `tests/fixtures/planted_alpha_bab_universe.csv` + `_meta.json` with committed SHA256
- [ ] P28 WP0–WP3 scripts executed, 3 JSON artifacts committed to `research_state/bab_p28/`
- [ ] `generate_p28_decision.py` created, emits `docs/BAB_P28_DECISION.md` + `p28_decision_sidecar.json` with `SIGNAL` verdict
- [ ] `bab_replay_decisions.py --subset p28_decision.md,p28_kickoff.md` exits 0 (byte-identical replay)
- [ ] `bab_replay_full.py` (or P29-style provenance audit) confirms P28 artifacts replay against planted fixture SHA256

---

## 🎯 STRATEGIC NOTE

**This project is blocked on real-market signal validation until licensed data arrives.**
P28 is the **only productive work** that unblocks pipeline mechanics validation without violating the "no planted alpha on frozen fixture" rule.
**Do not** start P31, do not simulate market data, do not weaken `rank_min_leg_beta`/`rank_max_gross` to force a verdict.
**Do** build P28 rigorously — it is the mechanics proof that the pipeline *would* detect signal if it existed.

---

*Generated by session at 2026-11-22T04:04:09Z. This handoff is durable — commit it to the repo if desired.*