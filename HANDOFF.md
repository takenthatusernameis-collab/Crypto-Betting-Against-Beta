# DURABLE HANDOFF — Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-25T19:08:46Z
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

## IMMEDIATE BOTTLENECKS REMOVING PROGRESS

1. **Regime Coverage Gap**: `bear_high_vol` has only 9 periods per seed (need ≥30). The synthetic fixture recipe (P35 wide-universe) does not generate enough bear-high-vol regimes. Fix: adjust synthetic data generation or relax `min_periods_per_regime`.

2. **High-Vol Failure Mode**: `bull_high_vol` consistently produces negative Sharpe (−1.86 to −0.41 across seeds). The BAB signal degrades when BTC trend is up but volatility is high. Root cause: beta estimation noise + idiosyncratic vol swamps signal.

3. **Cross-Fixture Non-Replication**: Second universe (idio_vol=0.006, beta range 0.2–2.4, 32 assets) yields mean DSR=0.396. The P38 pooled verdict is fragile to universe parameterization.

4. **Rank Weighting Dead End**: P36 proves rank weighting is strictly worse on synthetic data. Do not pursue rank-weighting as a fix.

---

## NEXT FOCUS CAMPAIGN — MANDATORY WORK

The next agent **must** execute one of the following campaigns (pick exactly one, complete fully, produce artifact). No "exploration" — ship a JSON + MD artifact to `research_state/`.

### OPTION A: Regime Fix + Re-Run P39 WP1 (Highest Priority)
**Goal:** Fix the `bear_high_vol` insufficient-periods problem and re-evaluate regime-conditional deflation.

**Steps:**
1. Modify `scripts/bab_p39_regime_conditional.py` or the synthetic fixture generator to produce ≥30 periods in `bear_high_vol` per seed (e.g., extend BTC price series, adjust regime labeling, or increase `synthetic_n_days`).
2. Re-run the full P39 WP1 campaign: `python scripts/bab_p39_regime_conditional.py`.
3. **Success criterion**: All 6 regimes have `n_ok_cells == 8` and `n_survive ≥ 6` (75% survival) with `all_survive` verdict, OR honest negative verdict with documented root cause per regime.
4. Write artifact: `research_state/bab_p39/regime_summary_v2.json` + `.md`.

### OPTION B: P37 Capacity/Turnover/Cost Surface Deep-Dive
**Goal:** Quantify exactly where the strategy breaks under realistic costs and capacity constraints.

**Steps:**
1. Run `scripts/bab_p37_cost_surface.py` (cost surface across participation rates).
2. Run `scripts/bab_p37_capacity.py` (break-even via bisection on P22 impact surface).
3. Run `scripts/bab_p37_turnover.py` (turnover decomposition).
4. Synthesize: At what participation rate / ADV does the default config (β_window=90, equal-weight) cross zero Sharpe? Is the break-even capacity > $1M, $10M, $100M?
5. Write artifact: `research_state/bab_p37/capacity_synthesis.json` + `.md` with a single table: config → break-even ADV → max deployable AUM.

### OPTION C: P24 Licensed Adapter — Real Data Integration
**Goal:** Replace synthetic fixture with a maintainer-supplied licensed price series and run the full P38/P39 pipeline on real data.

**Steps:**
1. Use `scripts/bab_licensed_adapter.py` to dry-run the adapter (see `research_state/bab_p24/adapter_dryrun.json`).
2. Obtain/configure a licensed CSV (maintainer action required — document the exact schema expected).
3. Run `scripts/bab_p38_deflated_significance.py` with `data_source` pointing to real prices.
4. Run `scripts/bab_p39_regime_conditional.py` on real data.
5. **Success criterion**: Real-data verdict (SURVIVES / DOES_NOT_SURVIVE) with full neutrality audit.
6. Write artifact: `research_state/bab_p24/real_data_verdict.json` + `.md`.

### OPTION D: P35 Signal Stability / Estimator Bakeoff
**Goal:** Test alternative beta estimators (EWMA, robust, shrinkage) to fix high-vol degradation.

**Steps:**
1. Run `scripts/bab_p35_estimator_bakeoff.py` (already has artifact: `research_state/bab_p35/estimator_bakeoff_summary.json`).
2. Run `scripts/bab_p35_signal_stability.py` (artifact: `research_state/bab_p35/signal_stability_summary.json`).
3. Identify which estimator (if any) improves `bull_high_vol` Sharpe from negative to positive while preserving `bear_low_vol` performance.
4. Integrate winning estimator into `strategies/betting_against_beta/beta_estimators.py` and re-run P39 WP1.
5. Write artifact: `research_state/bab_p35/estimator_integration.json` + `.md`.

---

## EXECUTION CONSTRAINTS

- **No new synthetic fixtures** without a documented reason tied to a specific regime gap.
- **No "try X and see" loops** — each campaign above has a binary success criterion.
- **Artifacts must be byte-stable**: deterministic seeds, sorted keys, fixed decimals (see existing `research_state/bab_p*/*.json`).
- **Tests must pass**: `python -m pytest -x -q` before claiming completion.
- **Git commit** the artifact with message: `chore(research): P## <campaign> — <verdict>`.

---

## CONTEXT FOR NEXT AGENT

- **Repository root**: `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
- **Key scripts**: `scripts/bab_p39_regime_conditional.py`, `scripts/bab_p37_*.py`, `scripts/bab_p35_*.py`, `scripts/bab_licensed_adapter.py`
- **Key configs**: `strategies/betting_against_beta/config.py` (BABConfig), `strategies/betting_against_beta/strategy.py` (BABStrategy)
- **Fixture**: `tests/fixtures/wide_bab_universe.csv` (BTC + 40 synthetic assets, deterministic seed 20261120)
- **Run command**: `python scripts/<script>.py` (all scripts are standalone entry points)
- **Test command**: `python -m pytest -x -q` (full suite ~3 min; use `-k` for subsets)

---

## IF ALL CAMPAIGNS FAIL

If Options A–D all produce honest negative verdicts (documented with root causes), the next session must:
1. Write a **terminal summary** artifact: `research_state/TERMINAL_SUMMARY.json` with:
   - All campaign verdicts (P20–P39)
   - Root cause taxonomy (regime coverage, estimator noise, universe fragility, cost capacity)
   - Recommendation: **STOP** (strategy not viable on synthetic crypto) or **PIVOT** (requires real data + maintainer licensed feed)
2. No further synthetic research — the evidence is sufficient.

---

**This handoff is durable. The next agent reads this file, picks ONE option, executes it completely, and updates this file with the outcome before exiting.**