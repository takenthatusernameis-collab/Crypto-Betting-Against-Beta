# DURABLE HANDOFF — Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-25T19:16:05Z
**Session:** Kilo General Agent Loop — Next Activation
**Repository:** Crypto-Betting-Against-Beta (Betting Against Beta crypto quant research)

---

## PROJECT STATE SUMMARY

This is a systematic quantitative research project implementing the **Betting Against Beta (BAB)** strategy (Frazzini & Pedersen) for cryptocurrencies. The codebase has progressed through **P20–P39+** research phases with deterministic synthetic fixtures and extensive test campaigns (70+ test files, 50+ scripts).

**Critical Verdicts (Latest Completed Phases):**

| Phase | Campaign | Verdict | Key Finding |
|-------|----------|---------|-------------|
| **P38** | Deflated Significance (n_trials=552) | **SURVIVES_DEFLATION** | Default config (β_window=90, quantile=0.3, equal-weight) passes; best in-sample (β_window=180, quantile=0.2) also passes |
| **P39 WP1** | Regime-Conditional + Tail Risk | **DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME** | `bear_high_vol`: 8/8 seeds insufficient periods (<30); `bull_high_vol`: 5/8 seeds fail deflation (DSR < 0.5, negative Sharpe) |
| **P39 WP2** | Cross-Fixture Replication (2nd synthetic universe) | **DOES_NOT_REPLICATE** | Only 3/8 seeds survive deflation; mean DSR = 0.396 (< 0.5 threshold) |
| **P36** | Rank-Weighted vs Equal-Weight | **RANK UNDERPERFORMS** | Rank weighting: negative Sharpe (−0.55), higher vol (3.4% vs 0.66%), worse maxDD (−5.5% vs −0.8%) |

**The strategy survives pooled deflation (P38) but fails when conditioned on high-volatility regimes and fails to replicate on a second independent synthetic parameterization.**

---

## IMMEDIATE BOTTLENOCKS REMOVING PROGRESS

**Bottleneck 1 (PRIMARY — must fix first): Regime Coverage Gap**
`bear_high_vol` has only 9 periods per seed across all 8 seeds (need ≥30). `bear_mid_vol` has 29 periods per seed (need ≥30). Both regimes are completely unevaluable (`n_ok_cells = 0`). The synthetic fixture recipe (P35 wide-universe) does not generate enough bear-high-vol periods.

**Fix (mandatory step 1):** Modify `scripts/bab_p39_regime_conditional.py` to produce ≥30 periods in `bear_high_vol` per seed. Options: extend the BTC price series in `tests/fixtures/wide_bab_universe.csv`, adjust `REGIME_LOOKBACK` / regime labeling boundaries, or reduce `MIN_PERIODS_PER_REGIME` with documented justification. Do not create new synthetic fixtures without a documented reason tied to this regime gap.

**Bottleneck 2 (secondary): High-Vol Failure Mode**
`bull_high_vol` consistently produces negative Sharpe (−1.86 to −0.41 across seeds; mean DSR = 0.412, only 3/8 survive). Beta estimation noise + idiosyncratic vol swamps signal in high-vol regimes.

**Bottleneck 3 (blocked, do not pursue): Cross-Fixture Non-Replication**
Second universe yields mean DSR = 0.396. P38 pooled verdict is fragile to universe parameterization. Defer until Bottleneck 1 is resolved.

**Bottleneck 4 (dead end, closed): Rank Weighting Dead End**
P36 proves rank weighting is strictly worse. Do not pursue rank-weighting as a fix.

---

## NEXT FOCUS CAMPAIGN — MANDATORY, SINGLE TASK

The next agent **must** execute the following campaign as the initial task. No "exploration," no picking among options. Complete fully and produce a JSON + MD artifact in `research_state/`. Update this HANDOFF.md with the outcome before exiting.

### CAMPAIGN A (MANDATORY): Regime Fix + Re-Run P39 WP1

**Goal:** Fix the `bear_high_vol` insufficient-periods bottleneck and re-evaluate regime-conditional deflation on the BAB strategy for crypto.

**Steps (execute in order, do not skip):**

1. **Remove the regime coverage bottleneck.** Inspect `scripts/bab_p39_regime_conditional.py` lines 74-76 (`REGIME_LOOKBACK = 20`, `MIN_PERIODS_PER_REGIME = 30`) and `_regime_labels()` (lines 221-275). Modify the script so that `bear_high_vol` produces ≥30 periods per seed across all 8 seeds. Verify by running the script and confirming `n_ok_cells == 8` for `bear_high_vol` in the output artifact.

2. **Re-run the full P39 WP1 campaign:** `python scripts/bab_p39_regime_conditional.py`

3. **Success criterion:** All 6 regimes have `n_ok_cells == 8` and `n_survive ≥ 6` (75% survival) with `all_survive` verdict, **OR** an honest negative verdict with a documented root cause per regime. The verdict may be negative — report it honestly, do not overclaim.

4. **Write artifact:** `research_state/bab_p39/regime_summary_v2.json` + `.md` (byte-stable: deterministic seeds, sorted keys, fixed decimals).

5. **Verify tests pass:** `python -m pytest -x -q` before claiming completion.

6. **Commit:** `git commit` the artifact with message: `chore(research): P39 regime fix + re-run WP1 — <verdict>`

7. **Update this HANDOFF.md** with the outcome (verdict, root cause, next steps) before exiting.

**Why this campaign is mandatory (repo-name prioritization):** The repository is `Crypto-Betting-Against-Beta` — its core deliverable is the BAB strategy for crypto. P38 showed the strategy survives pooled deflation, but P39 WP1 exposed that it fails in high-volatility regimes and cannot be evaluated in bear-high-vol due to insufficient data. Fixing the regime coverage gap is the highest-leverage, most repo-aligned work because it unblocks the entire regime-conditional validity assessment. Without it, no campaign can credibly claim the strategy is (or isn't) viable for crypto.

---

## EXECUTION CONSTRAINTS

- **No new synthetic fixtures** without a documented reason tied to the `bear_high_vol` regime gap.
- **No "try X and see" loops** — the campaign above has a binary success criterion.
- **Artifacts must be byte-stable**: deterministic seeds, sorted keys, fixed decimals (see existing `research_state/bab_p*/*.json`).
- **Tests must pass**: `python -m pytest -x -q` before claiming completion.
- **Git commit** the artifact with message: `chore(research): P39 regime fix + re-run WP1 — <verdict>`.
- **Update this HANDOFF.md** with the outcome before exiting.

---

## CONTEXT FOR NEXT AGENT

- **Repository root**: `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
- **Key script**: `scripts/bab_p39_regime_conditional.py` (entry point for Campaign A)
- **Key config**: `strategies/betting_against_beta/config.py` (BABConfig), `strategies/betting_against_beta/strategy.py` (BABStrategy)
- **Fixture**: `tests/fixtures/wide_bab_universe.csv` (BTC + 40 synthetic assets, deterministic seed 20261120)
- **Run command**: `python scripts/<script>.py` (all scripts are standalone entry points)
- **Test command**: `python -m pytest -x -q` (full suite ~3 min; use `-k` for subsets)
- **Current artifact**: `research_state/bab_p39/regime_summary.json` (shows `bear_high_vol` = 8/8 insufficient, `n_ok_cells = 0`)

---

## IF CAMPAIGN A FARES NEGATIVELY

If Campaign A produces an honest negative verdict (documented with root cause per regime), proceed to **Campaign B** (P37 Capacity/Turnover/Cost Surface Deep-Dive) as the next mandatory task, then **Campaign D** (P35 Signal Stability / Estimator Bakeoff) to address the high-vol failure mode. Only if A, B, and D all produce honest negative verdicts should the next session write a terminal summary artifact (`research_state/TERMINAL_SUMMARY.json`) and stop further synthetic research.

---

**This handoff is durable. The next agent reads this file, executes Campaign A as the initial task, completes it fully, and updates this file with the outcome before exiting.**
