# DURABLE HANDOFF — Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-26T00:34:14Z
**Session:** Kilo General Agent Loop — Next Activation (Campaign B initial task)
**Repository:** Crypto-Betting-Against-Beta (Betting Against Beta crypto quant research)

---

## PROJECT STATE SUMMARY

This is a systematic quantitative research project implementing the **Betting Against Beta (BAB)** strategy (Frazzini & Pedersen) for cryptocurrencies. The codebase has progressed through **P20–P39+** research phases with deterministic synthetic fixtures and extensive test campaigns (70+ test files, 50+ scripts).

**Critical Verdicts (Latest Completed Phases):**

| Phase | Campaign | Verdict | Key Finding |
|-------|----------|---------|-------------|
| **P38** | Deflated Significance (n_trials=552) | **SURVIVES_DEFLATION** | Default config (β_window=90, quantile=0.3, equal-weight) passes; best in-sample (β_window=180, quantile=0.2) also passes |
| **P39 WP1** | Regime-Conditional + Tail Risk | **DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME** | `bull_high_vol`: 4/8 seeds survive (mean DSR=0.53, mean Sharpe≈0); `bear_mid_vol`: 3/8 seeds survive (mean DSR=0.35, negative Sharpe); `bull_mid_vol`: 4/8 survive (mean DSR=0.53). Low-vol regimes survive well (5-6/8). |
| **P39 WP2** | Cross-Fixture Replication (2nd synthetic universe) | **DOES_NOT_REPLICATE** | Only 3/8 seeds survive deflation; mean DSR = 0.396 (< 0.5 threshold) |
| **P36** | Rank-Weighted vs Equal-Weight | **RANK UNDERPERFORMS** | Rank weighting: negative Sharpe (−0.55), higher vol (3.4% vs 0.66%), worse maxDD (−5.5% vs −0.8%) |

**The strategy survives pooled deflation (P38) but fails when conditioned on high-volatility regimes and fails to replicate on a second independent synthetic parameterization.**

---

## CURRENT STATE CORRECTION

**IMPORTANT:** The previous HANDOFF.md (timestamp 2026-11-25T22:49:34Z) claimed a "Regime Coverage Gap" where `bear_high_vol` had only 9 periods per seed. **That bottleneck is ALREADY FIXED.** The current committed artifact at `research_state/bab_p39/regime_summary.json` shows:

- **All 6 regimes have `n_ok_cells = 8`** (all 8 seeds well-populated)
- `bear_high_vol`: 30 periods/seed, 6/8 survive, mean DSR=0.70
- `bear_mid_vol`: 39 periods/seed, 3/8 survive, mean DSR=0.35
- `bear_low_vol`: 48 periods/seed, 6/8 survive, mean DSR=0.68
- `bull_high_vol`: 69 periods/seed, 4/8 survive, mean DSR=0.53, **mean Sharpe ≈ 0**
- `bull_mid_vol`: 82 periods/seed, 4/8 survive, mean DSR=0.53
- `bull_low_vol`: 69 periods/seed, 5/8 survive, mean DSR=0.63

**The regime coverage gap is RESOLVED. The current blocker is the HIGH-VOL FAILURE MODE.**

---

## IMMEDIATE BOTTLENECKS REMOVING PROGRESS

**Bottleneck 1 (PRIMARY — must fix now): High-Vol Failure Mode**
`bull_high_vol` consistently produces near-zero or negative Sharpe (−1.86 to +3.3 across seeds; mean DSR = 0.53, only 4/8 survive). `bear_mid_vol` also fails (mean DSR = 0.35, only 3/8 survive). Beta estimation noise + idiosyncratic vol swamps signal in high-vol regimes. This is the core reason the strategy fails regime-conditional deflation.

**Bottleneck 2 (secondary): Cross-Fixture Non-Replication**
Second universe yields mean DSR = 0.396. P38 pooled verdict is fragile to universe parameterization. Defer until Bottleneck 1 is resolved.

**Bottleneck 3 (dead end, closed): Rank Weighting Dead End**
P36 proves rank weighting is strictly worse. Do not pursue rank-weighting as a fix.

---

## EXISTING P37 ARTIFACTS (NOT REGIME-CONDITIONAL — NEED EXTENSION)

The `research_state/bab_p37/` directory already contains three summary artifacts, but they analyze the **full sample without regime conditioning**:

1. **`capacity_summary.json`** — Market-impact participation-rate break-even across 8 seeds (break-even impacts range 0.7–5.6bp; seeds 3, 4, 6 have negative costed Sharpe even at zero impact)
2. **`turnover_summary.json`** — Hysteresis no-trade band validation (turnover reduction confirmed, monotonicity holds)
3. **`cost_surface_summary.json`** — Cost x turnover surface (monotonicity verified across cost grid)

**These are necessary but insufficient.** They do not break down by P39 regimes (`bull_high_vol`, `bear_mid_vol`, etc.). The high-vol failure mode requires a **regime-conditional** P37 analysis.

---

## NEXT FOCUS CAMPAIGN — MANDATORY, SINGLE TASK

The next agent **must** execute the following campaign as the initial task. No "exploration," no picking among options. Complete fully and produce a JSON + MD artifact in `research_state/`. Update this HANDOFF.md with the outcome before exiting.

### CAMPAIGN B (MANDATORY): P37 Capacity/Turnover/Cost Surface Deep-Dive — Diagnose & Mitigate High-Vol Failure (REGIME-CONDITIONAL)

**Goal:** Diagnose *why* the BAB signal collapses in high-volatility regimes (`bull_high_vol`, `bear_mid_vol`) by extending the existing P37 analyses to be **regime-conditional**, using the same regime labels, seeds, and fixture as P39 WP1.

**Steps (execute in order, do not skip):**

1. **Create a new regime-conditional P37 script** (e.g., `scripts/bab_p37_regime_capacity.py`) that:
   - Uses the same 8 seeds, same P35 wide-universe fixture, same regime labels as P39 WP1 (`scripts/bab_p39_regime_conditional.py`)
   - For each (seed, regime) cell: computes turnover, gross leverage, transaction cost drag at varying cost levels (0bp, 1bp, 5bp, 10bp, 20bp)
   - Computes capacity limits: at what AUM does the strategy's own flow impact returns in each regime?
   - Analyzes beta estimation stability in high-vol regimes: rolling beta estimation error (vs true beta) per regime; tests if `BETA_WINDOW=90` is too short (noisy) or too long (stale) for high-vol; tests alternative estimators (shrinkage, EWMA, Kalman) within high-vol regimes only

2. **Produce diagnostic artifact:** `research_state/bab_p37/capacity_cost_surface_v2.json` + `.md` (byte-stable: deterministic seeds, sorted keys, fixed decimals) that:
   - Identifies the primary driver of high-vol failure (turnover? beta noise? cost drag? idiosyncratic vol?)
   - Recommends a *specific, testable* mitigation (e.g., "increase beta_window to 180 in high_vol", "add vol-targeting", "widen quantile to 0.4 in high_vol", "add minimum holding period")
   - OR honestly documents that no simple fix exists within current architecture

3. **Verify tests pass:** `python -m pytest -x -q` before claiming completion.

4. **Commit:** `git commit` the artifact with message: `chore(research): P37 regime-conditional capacity/cost surface deep-dive — <finding>`

5. **Update this HANDOFF.md** with the outcome (root cause, recommended mitigation, next steps) before exiting.

**Why this campaign is mandatory (repo-name prioritization):** The repository is `Crypto-Betting-Against-Beta` — its core deliverable is the BAB strategy for crypto. P39 WP1 proved the strategy fails in high-vol regimes. P37 (Capacity/Turnover/Cost Surface) is the *only* existing campaign designed to diagnose execution/structural drivers of failure. Without this **regime-conditional** diagnosis, no mitigation can be credibly designed. This is the highest-leverage, most repo-aligned work.

---

## EXECUTION CONSTRAINTS

- **No new synthetic fixtures** without a documented reason tied to the high-vol failure mode.
- **No "try X and see" loops** — the campaign above has a binary success criterion (diagnostic artifact with root cause + testable mitigation).
- **Artifacts must be byte-stable**: deterministic seeds, sorted keys, fixed decimals (see existing `research_state/bab_p*/*.json`).
- **Tests must pass**: `python -m pytest -x -q` before claiming completion.
- **Git commit** the artifact with message: `chore(research): P37 regime-conditional capacity/cost surface deep-dive — <finding>`.
- **Update this HANDOFF.md** with the outcome before exiting.

---

## CONTEXT FOR NEXT AGENT

- **Repository root**: `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
- **Key prior script**: `scripts/bab_p39_regime_conditional.py` (produced current regime_summary.json)
- **Reference scripts**: `scripts/bab_p37_capacity.py`, `scripts/bab_p37_turnover.py`, `scripts/bab_p37_cost_surface.py` (adapt for regime-conditioning)
- **Key config**: `strategies/betting_against_beta/config.py` (BABConfig), `strategies/betting_against_beta/strategy.py` (BABStrategy)
- **Fixture**: `tests/fixtures/wide_bab_universe.csv` (BTC + 40 synthetic assets, deterministic seed 20261120)
- **Run command**: `python scripts/<script>.py` (all scripts are standalone entry points)
- **Test command**: `python -m pytest -x -q` (full suite ~3 min; use `-k` for subsets)
- **Current artifact**: `research_state/bab_p39/regime_summary.json` (shows high-vol failure mode with full per-seed, per-regime breakdown)
- **Existing P37 artifacts**: `research_state/bab_p37/capacity_summary.json`, `turnover_summary.json`, `cost_surface_summary.json` (full-sample, NOT regime-conditional)

---

## IF CAMPAIGN B FARES NEGATIVELY

If Campaign B produces an honest negative verdict (no actionable mitigation found for high-vol failure), proceed to **Campaign D** (P35 Signal Stability / Estimator Bakeoff) as the next mandatory task to address the beta estimation noise in high-vol regimes. Only if B and D both produce honest negative verdicts should the next session write a terminal summary artifact (`research_state/TERMINAL_SUMMARY.json`) and stop further synthetic research.

---

**This handoff is durable. The next agent reads this file, executes Campaign B as the initial task, completes it fully, and updates this file with the outcome before exiting.**