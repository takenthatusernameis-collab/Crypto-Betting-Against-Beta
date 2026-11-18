# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Update this file only. There is no pointer file; `AGENT_HANDOFF.md` was deleted 2026-11-18T14:19:40Z. Delete any other `*HANDOFF*.md` on sight. Do not create parallel session/handoff docs.

- **Timestamp (UTC):** 2026-11-18T14:19:40Z
- **Git state:** HEAD `f98eaa1` on `main`; working tree dirty with **handoff-only doc changes** from this session (`HANDOFF.md` rewrite, `README.md` stale-step fix, deletion of `AGENT_HANDOFF.md`). **Commit this as step 0** — it is documentation, not product code.
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral BAB trading system (ingest → beta → signals → portfolio → backtest → execution → ops).
- **P19 is CLOSED.** All 7 remaining broad-`except` handlers annotated, 13 root scratch scripts removed, gate green. Do not reopen P19 for any reason; there is no P19 work left.

# INITIAL TASK MESSAGE (BINDING — START HERE)

## Campaign P20 — "Make the repo actually Betting Against Beta": beta-neutral construction + faithful FP weighting + walk-forward OOS evaluation

**Why this campaign (inferred from the repo name and from measured defects):** the project is named *Betting Against Beta*, but the shipped default book is **dollar-neutral only and carries a large negative market beta**. Measured at HEAD `f98eaa1` on the committed fixture: default config produces **book beta ≈ −0.57** (q=0.2: **−0.91**) and a **−68.6%** total loss while BTC buy-and-hold makes **+109.7%**. That is not a market-neutral BAB factor; it is a leveraged short-crypto book wearing a BAB label. On top of that, there is **no out-of-sample / walk-forward harness anywhere in the repo** (`grep -rniE "walk.?forward|out.?of.?sample|holdout"` → 0 hits), and the portfolio is **equal-weight ±1.0**, not the Frazzini–Pedersen rank-weighted, beta-scaled construction. Every prior phase hardened *defensive* code; **zero** effort has measured whether the strategy is what its name claims. This is the highest-value remaining work in this repository.

**This campaign is heavy work by construction.** Each session must land committed **product/test diffs plus a reproducible research artifact**. Handoff-only, README-only, gate-only, count-only, or "analysis-only" commits are **automatic FAILED sessions**.

## Ground truth @`f98eaa1` (measured this session — do not re-derive by guessing)

Reproduce exactly:

```bash
python3 - <<'EOF'
from strategies.betting_against_beta.data_loader import load_prices
from strategies.betting_against_beta import BABStrategy, metrics
r = load_prices("tests/fixtures/real_market_prices.csv", benchmark="BTC")
for bn in (False, True):
    o = BABStrategy(benchmark="BTC", beta_window=90, min_observations=60,
                    long_quantile=0.3, short_quantile=0.3,
                    transaction_costs=0.001, beta_neutral=bn).run(returns_df=r)
    rets = o.backtest["returns"]
    print(bn, "wealth", round(float(o.backtest["cumulative"].iloc[-1]), 4),
          "sharpe", round(float(metrics.sharpe_ratio(rets)), 3),
          "beta", round(float(metrics.strategy_beta(rets, r["BTC"])), 3))
EOF
```

| Config (fixture, 398 rows, 2021-01-05 → 2022-07-15, costs 10 bps) | Wealth index | Sharpe | Ann. vol | Max DD | **Book beta** | Turnover | Gross |
|---|---|---|---|---|---|---|---|
| **DEFAULT** w90 min60 q0.3, `beta_neutral=False` | 0.3136 (−68.6%) | **−1.418** | 0.446 | −0.758 | **−0.572** | 0.201 | 1.704 |
| same + `beta_neutral=True` | 0.7057 (−29.4%) | −0.725 | 0.258 | −0.413 | **+0.059** | 0.264 | 1.144 |
| w90 q0.2, `beta_neutral=False` | 0.4214 (−57.9%) | −0.680 | 0.567 | −0.634 | **−0.908** | 0.126 | 1.704 |
| w90 q0.2, `beta_neutral=True` | 1.3093 (+30.9%) | +0.649 | 0.366 | −0.227 | +0.006 | 0.234 | 1.429 |
| BTC buy-and-hold | 2.0975 (+109.7%) | +1.756 | 0.291 | — | 1.000 | — | — |

Also verified at HEAD: `python3 -m ruff check .` PASS; `bash scripts/bab_quick.sh` GREEN (104 + 195); `bash scripts/bab_reconcile_gate.sh` GREEN; full gate `bab_gate.sh` **GREEN — 6445 passed / 35 skipped / 0 failed, TOTAL 6562 stmts, 0 missed, 100%**.

**Honesty constraints baked into the ground truth:**
1. `tests/fixtures/real_market_prices.csv` is **NOT real market data**. `scripts/generate_real_market_fixture.py` says: "The prices are deterministic random walks (fixed seed) so the fixture is reproducible." It also carries a deliberate date gap (2021-09-17) and a fully-NaN `DEL` column. **Never** describe results on it as evidence of real-world profitability.
2. The q=0.2 / `beta_neutral=True` row above is **in-sample and not evidence of edge**. Do not select parameters by in-sample Sharpe and report it as a result. That is precisely what WP3 exists to prevent.
3. `backtest["cumulative"]` is a **wealth index** (1.0 = start), not a return. `final_cumulative − 1` is the total return. Past summaries that printed it as "cum" without subtracting 1 were ambiguous.

## Work packages — execute in order, one WP per commit minimum

### WP0 — Evidence harness (no product change; ~1 session)
- Create `scripts/bab_research_sweep.py`: deterministic sweep over `beta_window ∈ {30,60,90,120,180}`, `q ∈ {0.2,0.3}`, `tc ∈ {0,0.001,0.0025,0.005}`, `beta_neutral ∈ {False,True}`; emit `research_state/bab_p20/sweep.json` **and** a markdown table rendered from that JSON.
- Requirements: no network; fixed fixture; sorted key order; floats rounded to 6 dp; output byte-identical across runs (add a hash assertion in the test).
- **Acceptance:** `tests/test_bab_p20_research_sweep.py` proves (a) the script runs in <10 s, (b) two runs produce identical SHA-256, (c) the JSON schema has every row's `wealth/sharpe/beta/gross/turnover`, (d) the markdown table's numbers are generated from the JSON (no hand-typed digits).

### WP1 — Kill the beta-blind default (correctness; highest priority)
- Default `BABConfig` (`config.py:99`) sets `beta_neutral = False`. The default book must not be a −0.57-beta short-crypto proxy.
- Change the default so a default-configured run yields a beta-neutral book **when betas are available**, preserving all existing contracts (dollar-neutrality, flat rows, gross limits, missing-beta behavior). Prefer a single canonical switch in `BABConfig` plus the existing `enforce_beta_neutrality` path; do **not** special-case the fixture or silently zero out exposure.
- **Acceptance:** new `tests/test_bab_p20_beta_neutral_default.py` asserts, on the committed fixture and on a synthetic frame, that `|metrics.strategy_beta(rets, benchmark)| ≤ 0.06` for the default config at q∈{0.2,0.3} and w∈{60,90,120}; asserts dollar-neutrality `|sum(weights)| ≤ 1e-9` is preserved; and asserts an explicit opt-out still reproduces today's exact numbers (byte-for-byte on returns) so the change is auditable.
- **Acceptance (docs):** `docs/BAB_FIDELITY.md` states before/after beta, Sharpe, wealth, and the exact config diff. Update the README "Approach" bullet that currently claims "dollar-neutral by default" as if that were BAB.
- **Do not** "fix" this by only editing docs. The code default must change.

### WP2 — Faithful Frazzini–Pedersen weighting (opt-in first)
- Add `weighting: "equal" | "rank"` to config (default `"equal"` in WP2; WP3/WP4 may promote it only with OOS evidence). Implement rank-weighted construction: rank assets by beta each period, weight ∝ |rank − mean(rank)|, long leg scaled by `1/β_L` and short leg by `1/β_H` so each leg has unit beta before neutralization, then apply the dollar- and beta-neutral constraints.
- **Acceptance:** `tests/test_bab_p20_rank_weighting.py` contains a hand-computed 4-asset example (betas 0.5/0.8/1.2/1.6) whose expected weights match to `1e-12`; a test that rank weights sum to zero dollars and unit-beta legs within `1e-9`; a test that non-finite/insufficient betas degrade to the documented flat-row contract; a no-lookahead test proving weights at `t` depend only on betas computed from data `< t`.
- **Acceptance:** equal-weight path remains byte-identical to HEAD for a fixed seed/config (regression guard).

### WP3 — Walk-forward / OOS harness (the anti-cherry-pick gate)
- Create `scripts/bab_walk_forward.py`: rolling-origin splits over the fixture (≥5 folds), parameter selection **only** on each train window, evaluation **only** on the untouched test window; emit `research_state/bab_p20/walk_forward.json` (per-fold selected params, OOS Sharpe/vol/mdd/turnover/beta, aggregate mean/median and fraction of folds with positive Sharpe) and a rendered markdown table.
- **Acceptance:** `tests/test_bab_p20_walk_forward.py` proves (a) no leakage — for every fold `max(train_index) < min(test_index)`; (b) a planted lookahead trap (a signal that peeks at `t+1`) is detected and rejected by the harness; (c) deterministic rerun hash equality; (d) each fold has ≥40 test observations.
- **Acceptance:** `docs/BAB_RESEARCH_REPORT.md` publishes the OOS table **including the case where the edge is absent**. A negative/null OOS result is a valid, successful campaign outcome; a fabricated positive is a failed session.

### WP4 — Honest reporting + provenance (do not skip)
- `docs/BAB_RESEARCH_REPORT.md` must state: fixture provenance (deterministic random walk, fixed seed, deliberate gap and NaN column), in-sample vs OOS distinction, cost assumptions, and the explicit conclusion. Add a "What this does NOT prove" section.
- **Acceptance:** `tests/test_bab_p20_report_consistency.py` parses the markdown tables and asserts every published number equals the corresponding JSON field (no hand-typed drift); asserts the provenance sentence is present.
- Rename-or-relabel only via docs/headers; **do not** rename fixture files (many tests reference the path).

### WP5 — Cost / turnover realism and break-even
- Extend the sweep to report the **cost level at which OOS Sharpe crosses zero** (bisection over tc ∈ [0, 0.01], 6 iterations, deterministic), plus turnover per rebalance and gross exposure. Add `research_state/bab_p20/breakeven.json`.
- **Acceptance:** test asserts break-even cost is monotone non-increasing in reported Sharpe, is deterministic, and that `tc=0` reproduces the uncosted Sharpe within `1e-12`.

## Machine-checkable campaign done (all must hold)
1. Default-config book beta `|β| ≤ 0.06` on the fixture at q∈{0.2,0.3}, w∈{60,90,120}, with a committed test — **and** the explicit opt-out still reproduces old numbers exactly.
2. `scripts/bab_research_sweep.py`, `scripts/bab_walk_forward.py` exist, are deterministic (hash-equal reruns), and their JSON artifacts are committed under `research_state/bab_p20/`.
3. `docs/BAB_FIDELITY.md`, `docs/BAB_RESEARCH_REPORT.md` exist; every number in them is machine-checked against the JSON.
4. `tests/test_bab_p20_*.py` all pass; **no existing test is deleted, skipped, or weakened** to make the campaign pass (baseline: 6445 passed / 35 skipped — this count may only grow).
5. Full gate green: ruff PASS, reconcile GREEN, `bab_gate.sh` TOTAL 100% with 0 missed.

## Bottlenecks removed this session (do not re-create)
- **[REMOVED] Duplicate handoff state.** `AGENT_HANDOFF.md` carried its own competing status block ("P19-7 COMPLETE") and instructions. Deleted. `HANDOFF.md` is now the only durable handoff.
- **[REMOVED] Stale README binding step pointing back to closed P19-3/P19-1 coverage work** and stale gate numbers (6244 / 99%). README now points at P20 and states the verified 6445 / 100% baseline.
- **[REMOVED] Idle-session trap.** P19 was complete, so previous sessions could only re-timestamp and re-run gates. There is now a five-WP campaign with measurable deliverables and an explicit anti-idle failure rule.
- **[PERMANENTLY EXTERNAL] P19-1 CI enforcement.** Agent tokens lack `workflows:write`; `.github/workflows/main.yml` does not invoke ruff/gates. Maintainer-only. **Never re-attempt, never list as a session task.**
- **[VERIFIED, NOT A BLOCKER] Gate speed.** Full gate ≈ 207 s on 4 cores; strategy pipeline ≈ 3 ms on the fixture (`research_state/perf_baseline_real_fixture.json`). Performance is not the bottleneck — feedback is fast, so there is no excuse for skipping verification.

## Hard gates every session (repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate_handoff.log bash scripts/bab_gate.sh
```

Inner loop for product edits: `bash scripts/bab_quick.sh` + `python3 -m pytest -q tests/test_bab_p20_*.py`. Run the **full gate once per WP boundary**, never hand off an in-progress gate. Never lower the coverage floor.

## Forbidden (automatic failure)
- Handoff-only / docs-only / gate-only / analysis-only commits (WP0 and WP4 artefacts count only **with** their consistency tests).
- Selecting parameters on the evaluation window, then reporting the result as an OOS finding.
- Describing the synthetic fixture as real market data, or publishing a Sharpe without the synthetic provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests to make P20 pass; special-casing fixture filenames in product code.
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, or adding new `P19-7` markers.
- Type-annotation/style churn, broad refactors, network data fetching, committing probe/debug scratch scripts, or creating parallel handoff docs.

## Session ledger (append-only, concise)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-18T14:19:40Z | f98eaa1 | **Opened P20.** Certified baseline (6445/35/100%, reconcile GREEN, ruff PASS). Measured default-book beta −0.572 (q0.3) / −0.908 (q0.2) vs "market-neutral" claim; confirmed no walk-forward/OOS harness exists; confirmed equal-weight ±1.0 construction; flagged synthetic-fixture provenance. Deleted duplicate `AGENT_HANDOFF.md`, fixed stale README binding step, replaced idle P19 handoff with a 5-WP campaign + anti-idle rules. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate GREEN 6445 passed / 35 skipped / TOTAL 100% |
| 2026-11-18T13:20:00Z | f55e570 | P19-7 finished: 7 handlers annotated with A/B evidence + tests; 13 scratch scripts removed (Milestone 5). | full gate GREEN (6445 / 35 / 100%) |
| 2026-11-18T12:26:31Z | 1272f25 | Corrected stale "8 Milestone-4 sites" target; fixed RED ruff gate. | ruff PASS; quick GREEN; reconcile GREEN |
| ≤2026-11-17T14:46:59Z | 73e4db2 | All four original stakes closed; `strategies/betting_against_beta` 100% line coverage. | 6282 passed / 35 skipped |

## Proven closed (do not re-test, do not reopen)
- P19-7 (all broad/bare `except` handlers annotated repo-wide: 222 handlers, 0 unannotated), P19-2/3/4, P17-1/2, P18-1/2/3, kill-switch R4-B, bootstrap, reconciliation R5-B/R5-C, live-adapter two-key safety, 100% line coverage of `strategies/betting_against_beta` (6562/6562 statements).
- Milestone 1–5 hygiene. `scripts/bab_except_inventory.py` is retained as a read-only audit tool; running it is not a deliverable.
