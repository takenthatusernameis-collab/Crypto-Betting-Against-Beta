# NEXT SESSION — BINDING INITIAL TASK MESSAGE
**Timestamp (UTC):** 2026-11-18T14:44:17Z
**HEAD:** `1a70054` on `main` (clean; only this file is new)
**Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral BAB trading system

---

## START HERE: Execute Campaign P20, Lane B / WP1

**Objective:** Make the beta-neutral default real and rebalance-aware.

**Why (inferred from repo name + measured defects):**
- Project is named **Betting Against Beta** but the shipped default book is **dollar-neutral only** with **book beta ≈ −0.572** (q=0.3) / **−0.908** (q=0.2) on the committed fixture.
- Default config produces **−68.6%** total loss while BTC buy-and-hold makes **+109.7%**.
- **Zero** walk-forward / out-of-sample harness exists (`grep -rniE "walk.?forward|out.?of.?sample|holdout"` → 0 hits).
- Portfolio is **equal-weight ±1.0**, not Frazzini–Pedersen rank-weighted, beta-scaled construction.
- This is the highest-value remaining work in the repository.

---

## MANDATORY FIRST ACTIONS (in order)

1. `git log --oneline -5 && git status --short` — locate yourself; do not re-measure ground truth.
2. `find research_state/bab_p20 -type f 2>/dev/null` and `ls tests/test_bab_p20_*.py 2>/dev/null` — if `test_bab_p20_beta_neutral_default.py` and `docs/BAB_FIDELITY.md` fidelity section exist, **skip WP1** and take the lowest incomplete WP in Lane B.
3. Run `bash scripts/bab_quick.sh` before editing.
4. Append a ledger row to `HANDOFF.md` and refresh its timestamp before finishing.

---

## WP1 SCOPE — "Kill the beta-blind default" (correctness; highest priority)

### The Change
- `config.py:99`: default `BABConfig` has `beta_neutral = False`. Change so a default-configured run yields a **beta-neutral book when betas are available**, preserving:
  - Dollar-neutrality, flat rows, gross limits, missing-beta behavior
  - **Rebalance-window invariance** (critical — see blast radius below)

### Measured Blast Radius (do not rediscover)
Flipping only `config.py:99` to `True` → **12 failed, 6433 passed, 35 skipped** (348.94 s):

| Class | Tests | Cause | Required Fix |
|-------|-------|-------|--------------|
| A. CLI numeric goldens | `test_bab_cli_campaign17.py::test_console_vs_in_process_parity` (3), `test_bab_cli_campaign18.py::test_report_metrics_finite_strict_json` (3) | Hard-code final wealth under old default | Pin these to explicit `beta_neutral=False`; update golden only where test subject is the new default |
| B. Exception-path mocks | 4 tests in `test_bab_p19_7_strategy_exceptions.py`, `test_bab_strategy_c54_regressions.py`, `test_bab_strategy_coverage_campaign4.py` | Beta-neutral enables mock target in unintended path | Add explicit `beta_neutral=False` to preserve original exception path |
| C. **Rebalance-window invariance (real semantic defect)** | `test_bab_strategy_deep_coverage.py::TestStrategyRebalanceFreq::test_monthly_rebalance`, `test_betting_against_beta.py::TestMultiDayRebalance::test_weights_constant_within_rebalance_window_weekly` | `enforce_beta_neutrality` runs daily, changing weights inside weekly/monthly windows | **WP1 MUST make correction rebalance-aware:** compute/freeze neutralized book on rebalance dates, hold between them. Do not disable tests. |

### Acceptance Criteria (all must hold)
1. New `tests/test_bab_p20_beta_neutral_default.py` asserts on committed fixture + synthetic frame:
   - `|metrics.strategy_beta(rets, benchmark)| ≤ 0.06` for default config at q∈{0.2,0.3}, w∈{60,90,120}
   - `|sum(weights)| ≤ 1e-9` (dollar-neutral)
   - Weekly/monthly rebalance books constant between rebalance dates
   - Explicit `beta_neutral=False` reproduces today's exact returns byte-for-byte
2. `docs/BAB_FIDELITY.md` states before/after beta, Sharpe, wealth, and exact config diff
3. README "Approach" bullet claiming "dollar-neutral by default" corrected to state beta-neutral default + cite fidelity doc
4. **No existing test deleted, skipped, xfail-ed, or weakened** (baseline 6445 passed / 35 skipped may only grow)
5. Full gate green: ruff PASS, reconcile GREEN, `bab_gate.sh` TOTAL 100% with 0 missed

---

## GROUND TRUTH @ `1a70054` (do not re-derive)

```bash
python3 - <<'EOF'
from strategies.betting_against_beta.data_loader import load_prices
from strategies.betting_against_beta import BABStrategy, metrics
r = load_prices("tests/fixtures/real_market_prices.csv", benchmark="BTC")
for q in (0.2, 0.3):
    for bn in (False, True):
        o = BABStrategy(benchmark="BTC", beta_window=90, min_observations=60,
                        long_quantile=q, short_quantile=q,
                        transaction_costs=0.001, beta_neutral=bn).run(returns_df=r)
        rets = o.backtest["returns"]
        print(q, bn, round(float(o.backtest["cumulative"].iloc[-1]), 4),
              round(float(metrics.sharpe_ratio(rets)), 3),
              round(float(metrics.strategy_beta(rets, r["BTC"])), 3))
EOF
```

| Config | Wealth index | Sharpe | Book beta |
|--------|--------------|--------|-----------|
| DEFAULT w90 min60 q0.3, `beta_neutral=False` | 0.3136 (−68.6%) | −1.418 | **−0.572** |
| same + `beta_neutral=True` | 0.7057 (−29.4%) | −0.725 | **+0.059** |
| w90 q0.2, `beta_neutral=False` | 0.4214 (−57.9%) | −0.680 | **−0.908** |
| w90 q0.2, `beta_neutral=True` | 1.3093 (+30.9%) | +0.649 | +0.006 |
| BTC buy-and-hold | 2.0975 (+109.7%) | +1.756 | 1.000 |

**Honesty constraints:** Fixture is deterministic random walk (not real data); q=0.2/bn=True is in-sample not evidence of edge; cumulative is wealth index (1.0 = start).

---

## ENVIRONMENT CONSTRAINTS (do not waste session rediscovering)

- **Network blocked:** Coinbase API returns HTTP 403 — real-data fetch permanently external until maintainer supplies licensed CSV
- `rg` not installed; use `grep -rn` or editor search
- Full gate ≈ 3–6 min on 4 cores; fixture pipeline ≈ 3 ms
- Baseline: **6445 passed / 35 skipped / 0 failed**, **100% coverage** (6562/6562 statements)

---

## PARALLEL LANES (bottleneck removal)

| Lane | Work Packages | Owned Files |
|------|---------------|-------------|
| **A — Research** | WP0 → WP3 → WP5 | `scripts/bab_research_sweep.py`, `scripts/bab_walk_forward.py`, `research_state/bab_p20/**`, `tests/test_bab_p20_research_sweep.py`, `tests/test_bab_p20_walk_forward.py`, `tests/test_bab_p20_breakeven.py` |
| **B — Strategy fidelity** | **WP1 → WP2** | `strategies/betting_against_beta/config.py`, `portfolio.py`, `strategy.py`, `docs/BAB_FIDELITY.md`, `tests/test_bab_p20_beta_neutral_default.py`, `tests/test_bab_p20_rank_weighting.py` |
| **C — Reporting** | WP4 (after WP3+WP2) | `docs/BAB_RESEARCH_REPORT.md`, `tests/test_bab_p20_report_consistency.py` |

**Rules:** Lane A no product code; Lane B no research scripts; WP4 merge point; never two sessions on same WP.

**Solo-session default:** Start **WP1**, not WP0. WP1 is the repo-name-defining correctness defect.

---

## HARD GATES EVERY SESSION (repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate_handoff.log bash scripts/bab_gate.sh
```

Inner loop: `bash scripts/bab_quick.sh` + `python3 -m pytest -q tests/test_bab_p20_*.py`. Full gate once per WP boundary.

---

## FORBIDDEN (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits
- Selecting params on evaluation window then reporting as OOS
- Describing synthetic fixture as real market data
- Deleting, skipping, xfail-ing, or loosening existing tests
- "Fixing" rebalance invariance by turning off beta-neutral in tests instead of making product rebalance-aware
- Reopening P19, CI workflow edits, type-annotation/style churn, network data fetching, parallel handoff docs

---

## CAMPAIGN P20 DONE (all must hold)

1. Default-config book beta `|β| ≤ 0.06` on fixture at q∈{0.2,0.3}, w∈{60,90,120} with committed test; weekly/monthly rebalance invariance preserved; explicit opt-out reproduces old numbers exactly
2. `scripts/bab_research_sweep.py`, `scripts/bab_walk_forward.py` exist, deterministic (hash-equal reruns), JSON artifacts committed under `research_state/bab_p20/`
3. `docs/BAB_FIDELITY.md`, `docs/BAB_RESEARCH_REPORT.md` exist; every published number machine-checked against JSON
4. All `tests/test_bab_p20_*.py` pass; no existing test deleted/weakened
5. Full gate green: ruff PASS, reconcile GREEN, `bab_gate.sh` TOTAL 100% with 0 missed
6. README corrected to state beta-neutral default + cite fidelity doc

---

**This is heavy work by construction.** Each session must land committed code/test diffs + reproducible research artifact. Handoff-only commits are automatic FAILED sessions. If WP1 cannot finish in one session, commit a working vertical slice (code + test + artifact) and record exact remainder.