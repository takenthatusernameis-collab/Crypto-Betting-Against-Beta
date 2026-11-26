# DURABLE HANDOFF — Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-26T01:58:00Z
**Session:** Kilo General Agent Loop — Next Activation (Campaign P40 initial task — MANDATORY)
**Repository:** Crypto-Betting-Against-Beta (Betting Against Beta crypto quant research)
**Supersedes:** all prior HANDOFF.md content. The previous file described a stale
"Campaign B / P37 regime-conditional" plan that was superseded by P39 WP0 and is
now CLOSED. Do not execute Campaign B. The single binding campaign is **P40** below.

---

## PROJECT STATE SUMMARY (verified this session, HEAD `4ab4539`)

Systematic quantitative research implementing the **Betting Against Beta (BAB)**
strategy (Frazzini & Pedersen) for cryptocurrencies, on deterministic synthetic
fixtures (NOT real market data — never present results as real profitability).

**Phase status — P20–P39 are COMPLETE and FROZEN. Do not reopen.**

| Phase | Campaign | Verdict | Key Finding |
|-------|----------|---------|-------------|
| **P38 WP1** | Deflated Significance (n_trials=552) | **SURVIVES_DEFLATION** | Default (β=90,q=0.3,equal) DSR=0.921; best in-sample (β=180,q=0.2) DSR=0.944 |
| **P39 WP1** | Regime-Conditional Deflation | **DOES_NOT_SURVIVE_IN_SOME_REGIME** | `bear_mid_vol` 3/8 survive (DSR 0.35); `bull_high_vol`/`bull_mid_vol` 4/8 (DSR 0.53); low-vol regimes 5–6/8 |
| **P39 WP2** | Cross-Fixture Replication (2nd universe) | **DOES_NOT_REPLICATE** | Only 3/8 survive; mean DSR 0.396 (< 0.5) |
| **P39 WP0** | Full-Gate Close-Out (100% cov) | **GREEN (committed)** | `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` exit 0, TOTAL 100%, 7675 passed/39 skipped, ~56 min. Commit `098a3a4` is ancestor of HEAD. |
| **P36** | Rank-Weighted vs Equal-Weight | **RANK UNDERPERFORMS** | Negative Sharpe, higher vol, worse maxDD. Dead end — do not pursue. |

**One-line verdict:** The BAB factor survives pooled deflation (P38) on the primary
synthetic fixture but **fails in high-vol regimes (P39 WP1) and fails to replicate
on a second independent fixture (P39 WP2)**. P39 WP0 (the 100%-coverage full gate)
is DONE and committed — that bottleneck is removed.

---

## BOTTLENECKS — CURRENT STATUS (read before acting)

**Bottleneck 1 (RESOLVED this session): "Full gate cannot complete."**
The full gate (`BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh`) takes ~56 min
and exceeds any single tool-call window. It is GREEN when allowed to finish
(coverage notes + commit `098a3a4`). **Do NOT re-run the full gate to "verify" P39
WP0 — it is already committed GREEN.** If you must run it, use the
`background_process` `monitor` action with `timeout: 600000` and re-invoke `logs`
until the process exits; a bare `bash` call WILL be killed mid-run and leave the
working tree with spurious coverage-only failures and P27/P30 newline side-effects
(restore with `git checkout -- research_state/`).

**Bottleneck 2 (ACTIVE — the reason P40 is stuck): No P40 artifacts exist.**
`research_state/bab_p40/` does not exist. P40 is the sole binding agent-executable
row (README line 246, COVERAGE_NOTES line 7). Nothing has been started. This is the
gap the next session must close with heavy, real work (below).

**Bottleneck 3 (CLOSED): Rank weighting.** P36 proved it strictly worse. Never reopen.

**Bottleneck 4 (CLOSED): Regime coverage gap.** The old "bear_high_vol only 9 periods"
gap is fixed — all 6 regimes have `n_ok_cells = 8` in
`research_state/bab_p39/regime_summary.json`.

---

## NEXT FOCUS CAMPAIGN — MANDATORY, SINGLE TASK (NO EXPLORATION, NO OPTIONS)

The next agent **must** execute **Campaign P40** as the initial task. This is the
single source of truth. **Do not** explore, do not pick among options, do not reopen
P20–P39 (frozen), do not re-run the full gate for P39 WP0 (done). Complete P40 fully
and produce byte-stable JSON + MD artifacts in `research_state/bab_p40/`. Update this
HANDOFF.md with the outcome before exiting.

### CAMPAIGN P40 (MANDATORY): Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict

**Goal:** Resolve the central open question left by P38/P39 — *is the BAB factor's
pooled survival (P38) a genuine factor property, or an artifact of a single synthetic
fixture?* P39 WP2 showed non-replication on ONE second fixture (mean DSR 0.396). P40
must generalize this to a **multi-fixture meta-analysis** across several independent
synthetic parameterizations and emit a single consolidated verdict.

**Steps (execute in order, do not skip):**

1. **Create `scripts/bab_p40_meta_analysis.py`** (standalone entry point, deterministic)
   that:
   - Reuses the P39 WP1 regime labels + P39 WP2 cross-fixture generator as the base.
   - Defines **≥ 4 independent synthetic fixtures** varying at minimum: seed base,
     idio_vol, beta grid range, n_assets (e.g. the P39 WP2 fixture + 3 new ones). Each
     fixture is a deterministic seeded random walk — document the exact parameters.
   - For each (fixture, seed) cell: runs the shipped-default BAB config (β=90, q=0.3,
     equal-weight, beta+dollar neutral), computes Sharpe, DSR (deflate over the
     read-only `n_trials_total=552` from `bab_p38/deflated_summary.json`), PSR, and
     neutrality invariants.
   - Aggregates per-fixture and across-fixture: n_survive, mean/min/max DSR,
     fraction of fixtures where the pooled P38 verdict replicates.
   - Emits a **consolidated factor verdict** with a fixed enum, e.g.
     `ROBUST_ACROSS_FIXTURES` / `FRAGILE_FIXTURE_DEPENDENT` / `DOES_NOT_REPLICATE`.

2. **Produce byte-stable artifacts:** `research_state/bab_p40/meta_summary.json` +
   `meta_summary.md` (deterministic seeds, sorted keys, fixed decimals — match the
   formatting of existing `research_state/bab_p*/*.json`). Include a per-fixture
   parameter table and the consolidated verdict + honest reason.

3. **Add a consistency test** `tests/test_bab_p40_decision_consistency.py` mirroring
   `tests/test_bab_p38_decision_consistency.py` / `test_bab_p39_*` (schema pinned,
   committed JSON matches fresh build, byte-identical rebuild, markdown matches
   renderer). Register it in the P31/P32 decision registry if those tests require it.

4. **Verify (fast, NOT the full gate):**
   - `python -m pytest -x -q tests/test_bab_p40_decision_consistency.py` passes.
   - `python -m pytest -x -q tests/test_bab_p31_registry_completeness.py tests/test_bab_p32_decision_registry_completeness.py` still pass (registry not broken).
   - `bash scripts/bab_quick.sh` is GREEN (ruff + targeted trio + smoke, ~10s).
   - **Do NOT run the full 56-min gate.** It is already GREEN at HEAD for P39 WP0.

5. **Commit:** `git commit` with message
   `chore(research): P40 multi-fixture robustness meta-analysis — <consolidated verdict>`.
   Restore any P27/P30 newline side-effects first (`git checkout -- research_state/bab_p27/ research_state/bab_p30/`).

6. **Update this HANDOFF.md** with the P40 outcome (per-fixture DSR table, consolidated
   verdict, next steps) before exiting.

**Why P40 is mandatory (repo-name prioritization):** The repo is
`Crypto-Betting-Against-Beta` — its core deliverable is a *trustworthy* BAB verdict for
crypto. P38 says "survives" on one fixture; P39 WP2 says "does not replicate" on a
second. P40 is the only campaign that resolves this contradiction with a
multi-fixture meta-analysis and a single consolidated verdict. Without it, no honest
claim about the factor can be made. This is the highest-leverage, most repo-aligned work.

---

## EXECUTION CONSTRAINTS

- **No new synthetic fixtures** beyond the ≥4 P40 fixtures, each justified by the
  robustness question (vary seed/idio_vol/beta-grid/n_assets). Document every parameter.
- **No "try X and see" loops** — P40 has a binary success criterion (byte-stable
  meta_summary.{json,md} + consolidated verdict + passing consistency test).
- **Artifacts byte-stable:** deterministic seeds, sorted keys, fixed decimals.
- **Do NOT run the full `bab_gate.sh`** — it is ~56 min, already GREEN for P39 WP0, and
  gets killed mid-run by tool timeouts (leaving spurious failures + P27/P30 side-effects).
  Use `bab_quick.sh` + the targeted P40/registry tests for verification.
- **Tests must pass** before claiming completion.
- **Git commit** the artifacts with the P40 message above.
- **Update this HANDOFF.md** with the outcome before exiting.

---

## CONTEXT FOR NEXT AGENT

- **Repository root:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
- **Key prior scripts:** `scripts/bab_p39_regime_conditional.py` (regime labels),
  `scripts/bab_p39_cross_fixture.py` (2nd-fixture generator — extend to ≥4 fixtures),
  `scripts/bab_p38_deflated_significance.py` (DSR/deflation math — reuse, read-only n_trials).
- **Reference consistency test:** `tests/test_bab_p38_decision_consistency.py`.
- **Key config:** `strategies/betting_against_beta/config.py` (BABConfig),
  `strategies/betting_against_beta/strategy.py` (BABStrategy).
- **Fixtures:** `tests/fixtures/wide_bab_universe.csv` (BTC + 40 synthetic assets,
  deterministic seed 20261120). P39 WP2 uses a 2nd parameterization (seed base 20270101,
  idio_vol 0.006, 32 assets, beta 0.2–2.4).
- **Read-only trial count:** `n_trials_total=552` from
  `research_state/bab_p38/deflated_summary.json` — never re-enumerate.
- **Run command:** `python scripts/<script>.py` (standalone entry points).
- **Fast verify:** `bash scripts/bab_quick.sh` (~10s) + targeted pytest. **Not** the full gate.
- **Current artifacts:** `research_state/bab_p39/regime_summary.json` (high-vol failure),
  `research_state/bab_p39/cross_fixture_summary.json` (non-replication),
  `research_state/bab_p38/deflated_summary.json` (pooled survival).

---

## IF P40 PRODUCES AN HONEST NEGATIVE VERDICT

If P40's consolidated verdict is `DOES_NOT_REPLICATE` / `FRAGILE_FIXTURE_DEPENDENT`,
that is a valid, publishable honest result — record it and proceed to write a terminal
summary artifact `research_state/TERMINAL_SUMMARY.json` consolidating P38–P40, then
stop further synthetic research. Do NOT invent new fixtures or reopen frozen phases to
chase a positive result. Only a `ROBUST_ACROSS_FIXTURES` verdict justifies a follow-on
real-data validation campaign (and only with explicit maintainer approval, since
`tests/fixtures/real_market_prices.csv` is also synthetic — see README line 246).

---

**This handoff is durable. The next agent reads this file, executes Campaign P40 as the
initial task, completes it fully with heavy real work, and updates this file with the
outcome before exiting. Do not run the full 56-min gate. Do not reopen P20–P39.**