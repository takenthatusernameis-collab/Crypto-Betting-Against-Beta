# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Update this file only. There is no pointer file; `AGENT_HANDOFF.md` was deleted 2026-11-18T14:19:40Z. Delete any other `*HANDOFF*.md` on sight. Do not create parallel session/handoff docs.

- **Timestamp (UTC):** 2026-11-18T14:43:40Z
- **Git state:** HEAD `1a70054` on `main`; clean before this refresh. The only dirty file after this session is **this handoff** (plus generated `.coverage`/caches, which are ignored). There is **no uncommitted product work**.
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral BAB trading system (ingest → beta → signals → portfolio → backtest → execution → ops).
- **P19 is CLOSED.** All broad-`except` handlers annotated, scratch scripts removed, coverage complete. Do not reopen P19 for any reason; there is no P19 work left.

**NEXT SESSION — START HERE:** execute **Campaign P20, Lane B / WP1** (make the beta-neutral default real and rebalance-aware). If `tests/test_bab_p20_beta_neutral_default.py` and the `docs/BAB_FIDELITY.md` fidelity section already exist on HEAD, skip WP1 and take the lowest incomplete WP in your lane. Read the binding section below before touching code.

# INITIAL TASK MESSAGE (BINDING — START HERE)

## Campaign P20 — "Make the repo actually Betting Against Beta": beta-neutral construction + faithful FP weighting + walk-forward OOS evaluation

**Why this campaign (inferred from the repo name and from measured defects):** the project is named *Betting Against Beta*, but the shipped default book is **dollar-neutral only and carries a large negative market beta**. Measured at HEAD `1a70054` on the committed fixture: default config produces **book beta ≈ −0.572** (q=0.2: **−0.908**) and a **−68.6%** total loss while BTC buy-and-hold makes **+109.7%**. That is not a market-neutral BAB factor; it is a leveraged short-crypto book wearing a BAB label. On top of that, there is **no out-of-sample / walk-forward harness anywhere in the repo** (`grep -rniE "walk.?forward|out.?of.?sample|holdout"` → 0 hits), and the portfolio is **equal-weight ±1.0**, not the Frazzini–Pedersen rank-weighted, beta-scaled construction. Every prior phase hardened *defensive* code; **zero** effort has measured whether the strategy is what its name claims. This is the highest-value remaining work in this repository.

**This campaign is heavy work by construction.** Each session must land committed **code/test diffs plus a reproducible research artifact**. Handoff-only, README-only, gate-only, count-only, or "analysis-only" commits are **automatic FAILED sessions**. If you cannot finish a WP in one session, commit a working vertical slice (code + test + artifact) and record the exact remainder; do **not** commit only notes.

**First actions (mandatory, in order):**
1. `git log --oneline -5 && git status --short` — locate yourself; do not re-measure what this file already certifies.
2. `find research_state/bab_p20 -type f 2>/dev/null` and `ls tests/test_bab_p20_*.py 2>/dev/null` — presence of a WP's deliverable files means that WP is already landed; skip it.
3. Pick the **lowest-numbered incomplete WP in your lane** (lanes below). Never do another lane's WP.
4. Run `bash scripts/bab_quick.sh` before editing. Run the full gate only at a WP boundary.
5. Append a ledger row and refresh this file's timestamp before finishing.

## Ground truth @`1a70054` (measured and re-verified this session — do not re-derive by guessing)

Reproduce exactly:

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

| Config (fixture, 398 rows, 2021-01-05 → 2022-07-15, costs 10 bps) | Wealth index | Sharpe | Ann. vol | Max DD | **Book beta** | Turnover | Gross |
|---|---|---|---|---|---|---|---|---|
| **DEFAULT** w90 min60 q0.3, `beta_neutral=False` | 0.3136 (−68.6%) | **−1.418** | 0.446 | −0.758 | **−0.572** | 0.201 | 1.704 |
| same + `beta_neutral=True` | 0.7057 (−29.4%) | −0.725 | 0.258 | −0.413 | **+0.059** | 0.264 | 1.144 |
| w90 q0.2, `beta_neutral=False` | 0.4214 (−57.9%) | −0.680 | 0.567 | −0.634 | **−0.908** | 0.126 | 1.704 |
| w90 q0.2, `beta_neutral=True` | 1.3093 (+30.9%) | +0.649 | 0.366 | −0.227 | +0.006 | 0.234 | 1.429 |
| BTC buy-and-hold | 2.0975 (+109.7%) | +1.756 | 0.291 | — | 1.000 | — | — |

**Honesty constraints baked into the ground truth:**
1. `tests/fixtures/real_market_prices.csv` is **NOT real market data**. `scripts/generate_real_market_fixture.py` says: "The prices are deterministic random walks (fixed seed) so the fixture is reproducible." It also carries a deliberate date gap (2021-09-17) and a fully-NaN `DEL` column. **Never** describe results on it as evidence of real-world profitability.
2. The q=0.2 / `beta_neutral=True` row is **in-sample and not evidence of edge**. Do not select parameters by in-sample Sharpe and report it as a result. That is precisely what WP3 exists to prevent.
3. `backtest["cumulative"]` is a **wealth index** (1.0 = start), not a return. `final_cumulative − 1` is the total return. Past summaries that printed it as "cum" without subtracting 1 were ambiguous.

### Measured WP1 blast radius (this session — do not rediscover)

Flipping **only** `config.py:99` from `beta_neutral=False` to `True` and running the full suite yields **12 failed, 6433 passed, 35 skipped** (348.94 s). The failures are not random; they fall into three classes:

| Class | Tests | Cause | Required fix |
|---|---|---|---|
| A. CLI numeric goldens | `test_bab_cli_campaign17.py::test_console_vs_in_process_parity` (3), `test_bab_cli_campaign18.py::test_report_metrics_finite_strict_json` (3) | They hard-code final wealth computed under the old default (`0.4563`, `0.5312`, `2.1987`). | Pin these cases to an **explicit** `beta_neutral=False` where the test's subject is CLI parsing/reporting; update a golden only where the test's subject is the new default, and state that in the commit. |
| B. Exception-path mocks | `test_bab_p19_7_strategy_exceptions.py::test_site836_weight_cleanup_failure_surfaces_babdataerror`, `test_bab_strategy_c54_regressions.py::test_double_finiteness_failure_surfaces_babdataerror`, `test_bab_strategy_c54_regressions.py::test_single_finiteness_failure_still_falls_back`, `test_bab_strategy_coverage_campaign4.py::test_run_finiteness_fallback_double_failure_surfaces` | Enabling beta-neutral makes the mock target (`replace`/`to_numpy` boom) execute in a path it was not written for. | Add explicit `beta_neutral=False` so the test still targets its original exception path. This is preservation, not weakening. |
| C. Rebalance-window invariance | `test_bab_strategy_deep_coverage.py::TestStrategyRebalanceFreq::test_monthly_rebalance`, `test_betting_against_beta.py::TestMultiDayRebalance::test_weights_constant_within_rebalance_window_weekly` | **Real semantic defect:** `enforce_beta_neutrality` runs every day, so enabling it changes weights *inside* a weekly/monthly rebalance window. | WP1 must make correction **rebalance-aware**: compute/freeze the neutralized book on rebalance dates and hold it between them. Do not "fix" this by disabling the tests. |

This blast radius is the main reason WP1 must be a design change, not a one-line default flip.

### Environment constraints (do not waste a session rediscovering)

- **Network is blocked.** `https://api.exchange.coinbase.com` returns **HTTP 403** from this runner. The real-data fetch path is **permanently external** until a maintainer supplies a licensed CSV. Never add network calls to tests or campaign acceptance.
- `rg` is **not installed**; use `grep -rn` or the editor search tools.
- Full gate ≈ 3–6 min on 4 cores; fixture strategy pipeline ≈ 3 ms. Feedback is fast enough that skipping verification is unjustifiable.
- Baseline tests: **6445 passed / 35 skipped / 0 failed**, **100%** coverage (6562/6562 statements), verified this session at `1a70054` (206.50 s). The count may only grow.

## Parallel lanes and file ownership (bottleneck removal)

Run these lanes concurrently without colliding. A session owns exactly one lane for its whole turn.

| Lane | Work packages (in order) | Owned files (do not edit outside ownership) |
|---|---|---|
| **A — Research/evaluation** | WP0 → WP3 → WP5 | `scripts/bab_research_sweep.py`, `scripts/bab_walk_forward.py`, `research_state/bab_p20/**`, `tests/test_bab_p20_research_sweep.py`, `tests/test_bab_p20_walk_forward.py`, `tests/test_bab_p20_breakeven.py`, `docs/BAB_RESEARCH_REPORT.md` (with WP4) |
| **B — Strategy fidelity** | WP1 → WP2 | `strategies/betting_against_beta/config.py`, `portfolio.py`, `strategy.py`, `docs/BAB_FIDELITY.md`, `tests/test_bab_p20_beta_neutral_default.py`, `tests/test_bab_p20_rank_weighting.py` |
| **C — Reporting/consistency** | WP4 only, after WP3 and WP2 are committed | `docs/BAB_RESEARCH_REPORT.md`, `tests/test_bab_p20_report_consistency.py` |

Rules:
- Lane A must not edit product code; Lane B must not edit research scripts or `research_state/`.
- If Lane A needs the `weighting` field, it starts only after WP2 is committed; until then use the existing equal-weight path.
- WP4 is a merge point, not a free session: it must publish **both** fidelity numbers and OOS numbers and machine-check them.
- Two sessions must never work on the same WP. The committed deliverable files are the claim. If a WP's files already exist, move to the next WP in your lane.

**Solo-session default (use when only one agent is active): start WP1, not WP0.** WP1 is the repo-name-defining correctness defect. WP0 is a supporting harness for Lane A and may run concurrently, but an evidence harness alone cannot substitute for fixing the product default. A session that finishes only WP0 is valid work but does **not** close the campaign.

## Work packages — execute in order, one WP per committed slice minimum

### WP0 — Evidence harness (research only; ~1 session)
- Create `scripts/bab_research_sweep.py`: deterministic sweep over `beta_window ∈ {30,60,90,120,180}`, `q ∈ {0.2,0.3}`, `tc ∈ {0,0.001,0.0025,0.005}`, `beta_neutral ∈ {False,True}`; emit `research_state/bab_p20/sweep.json` **and** a markdown table rendered from that JSON.
- Requirements: no network; fixed fixture; sorted key order; floats rounded to 6 dp; output byte-identical across runs.
- **Acceptance:** `tests/test_bab_p20_research_sweep.py` proves (a) the script runs in <10 s, (b) two runs produce identical SHA-256, (c) the JSON schema has every row's `wealth/sharpe/beta/gross/turnover`, (d) the markdown table's numbers are generated from the JSON (no hand-typed digits).

### WP1 — Kill the beta-blind default (correctness; highest priority)
- Default `BABConfig` (`config.py:99`) sets `beta_neutral = False`. The default book must not be a −0.572-beta short-crypto proxy.
- Change the default so a default-configured run yields a beta-neutral book **when betas are available**, while preserving dollar-neutrality, flat rows, gross limits, missing-beta behavior, and **rebalance-window invariance** (see class C above).
- Prefer a single canonical switch in `BABConfig` plus the existing `enforce_beta_neutrality` path. Do **not** special-case the fixture or silently zero out exposure.
- **Acceptance:** new `tests/test_bab_p20_beta_neutral_default.py` asserts, on the committed fixture and on a synthetic frame, that `|metrics.strategy_beta(rets, benchmark)| ≤ 0.06` for the default config at q∈{0.2,0.3} and w∈{60,90,120}; asserts `|sum(weights)| ≤ 1e-9`; asserts weekly/monthly rebalance books are constant between rebalance dates; and asserts an explicit `beta_neutral=False` reproduces today's exact returns byte-for-byte.
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
1. Default-config book beta `|β| ≤ 0.06` on the fixture at q∈{0.2,0.3}, w∈{60,90,120}, with a committed test; weekly/monthly rebalance invariance preserved; explicit opt-out reproduces old numbers exactly.
2. `scripts/bab_research_sweep.py`, `scripts/bab_walk_forward.py` exist, are deterministic (hash-equal reruns), and their JSON artifacts are committed under `research_state/bab_p20/`.
3. `docs/BAB_FIDELITY.md`, `docs/BAB_RESEARCH_REPORT.md` exist; every published number is machine-checked against JSON.
4. `tests/test_bab_p20_*.py` all pass; **no existing test is deleted, skipped, `xfail`-ed, or weakened** (baseline 6445 passed / 35 skipped may only grow).
5. Full gate green: ruff PASS, reconcile GREEN, `bab_gate.sh` TOTAL 100% with 0 missed.
6. The README's "dollar-neutral by default" BAB claim is corrected to state the beta-neutral default and cite the fidelity doc.

## P21 preview (deferred — activate only after every P20 done-check above passes)

Do not start P21 while P20 is open. When P20 closes, the next campaign is **P21 — "Execution-grade BAB"** with these non-optional work packages:
- **P21-1 Real-data adapter:** ingest a maintainer-supplied, license-compliant daily OHLCV CSV (no network in-session); produce `research_state/p21/real_data_provenance.json` and rerun WP3/WP5 unchanged. If no real CSV exists, the deliverable is a validated import contract + fixture-shaped synthetic fallback clearly labeled, not a profitability claim.
- **P21-2 Capacity/liquidity model:** per-asset ADV/participation limits and a square-root impact curve wired into `cost_model`; tests must show size scaling and reject books exceeding participation caps.
- **P21-3 Execution realism:** deterministic paper-trading soak over ≥250 rebalances with replay, reconciliation, and restart/resume; assert modeled-vs-executed drift within tolerance.
- **P21-4 Robustness matrix:** regime × cost × rebalance-frequency × weighting sweep with OOS-only conclusions and a machine-checked report.

P21 exists so no future session can idle after P20. Its exact acceptance criteria are intentionally not written yet; derive them from the P20 pattern (deterministic script + committed artifact + consistency test + honest report).

## Bottlenecks removed this session (do not re-create)
- **[FIXED] Stale git state / phantom dirty tree.** Previous handoff pointed at `f98eaa1` and claimed uncommitted doc changes. Actual HEAD is `1a70054`; the doc changes are committed. This file now states the real state.
- **[REMOVED] WP1 hidden test explosion.** Measured the exact 12-failure blast radius and classified it (goldens, exception mocks, rebalance invariance). Future sessions no longer need a 6-minute probe to discover it.
- **[SURFACED] Daily correction vs rebalance windows.** Enabling the existing enforcement naively breaks the weekly/monthly contract. WP1 must make neutralization rebalance-aware; this is now binding.
- **[REMOVED] Lane collisions.** Research and product work are split into disjoint lanes with explicit file ownership; two sessions can progress concurrently without editing the same files.
- **[REMOVED] Real-data rabbit hole.** Coinbase public API is 403 from this runner; real-data work is explicitly external and deferred to P21.
- **[REMOVED] Duplicate handoff state.** `AGENT_HANDOFF.md` is gone; this is the only durable handoff.
- **[PERMANENTLY EXTERNAL] P19-1 CI enforcement.** Agent tokens lack `workflows:write`; `.github/workflows/main.yml` does not invoke ruff/gates. Maintainer-only. **Never re-attempt, never list as a session task.**
- **[VERIFIED] Gate speed.** Full gate ≈ 3–6 min on 4 cores; strategy pipeline ≈ 3 ms on the fixture. Performance is not the bottleneck.

## Hard gates every session (repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate_handoff.log bash scripts/bab_gate.sh
```

Inner loop for product edits: `bash scripts/bab_quick.sh` + `python3 -m pytest -q tests/test_bab_p20_*.py`. Run the **full gate once per WP boundary**, never hand off an in-progress gate. Never lower the coverage floor.

## Forbidden (automatic failure)
- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (WP0 and WP4 artefacts count only **with** their consistency tests).
- Selecting parameters on the evaluation window, then reporting the result as an OOS finding.
- Describing the synthetic fixture as real market data, or publishing a Sharpe without the synthetic provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests to make P20 pass; special-casing fixture filenames in product code.
- "Fixing" rebalance-invariance failures by turning off beta-neutral correction in tests instead of making the product rebalance-aware.
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, or adding new `P19-7` markers.
- Type-annotation/style churn, broad refactors, network data fetching, committing probe/debug scratch scripts, or creating parallel handoff docs.

## Session ledger (append-only, concise)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-18T14:43:40Z | 1a70054 | **Campaign refresh.** Re-verified ground truth (q0.2/q0.3, bn on/off). Measured WP1 blast radius: flipping default to `beta_neutral=True` alone → **12 failed / 6433 passed / 35 skipped**, classified into goldens (6), exception mocks (4), rebalance-window invariance (2). Added parallel lanes + file ownership, rebalance-aware WP1 requirement, network-403 note, and P21 preview. No product code changed. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate GREEN **6445 passed / 35 skipped / TOTAL 100%, 206.50 s** |
| 2026-11-18T14:19:40Z | f98eaa1 | **Opened P20.** Certified baseline (6445/35/100%, reconcile GREEN, ruff PASS). Measured default-book beta −0.572 (q0.3) / −0.908 (q0.2); confirmed no walk-forward/OOS harness; confirmed equal-weight ±1.0 construction; flagged synthetic-fixture provenance. Deleted duplicate `AGENT_HANDOFF.md`, fixed stale README binding step. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate GREEN 6445 passed / 35 skipped / TOTAL 100% |
| 2026-11-18T13:20:00Z | f55e570 | P19-7 finished: 7 handlers annotated with A/B evidence + tests; 13 scratch scripts removed (Milestone 5). | full gate GREEN (6445 / 35 / 100%) |
| 2026-11-18T12:26:31Z | 1272f25 | Corrected stale "8 Milestone-4 sites" target; fixed RED ruff gate. | ruff PASS; quick GREEN; reconcile GREEN |
| ≤2026-11-17T14:46:59Z | 73e4db2 | All four original stakes closed; `strategies/betting_against_beta` 100% line coverage. | 6282 passed / 35 skipped |

## Proven closed (do not re-test, do not reopen)
- P19-7 (all broad/bare `except` handlers annotated repo-wide: 222 handlers, 0 unannotated), P19-2/3/4, P17-1/2, P18-1/2/3, kill-switch R4-B, bootstrap, reconciliation R5-B/R5-C, live-adapter two-key safety, 100% line coverage of `strategies/betting_against_beta` (6562/6562 statements).
- Milestone 1–5 hygiene. `scripts/bab_except_inventory.py` is retained as a read-only audit tool; running it is not a deliverable.
