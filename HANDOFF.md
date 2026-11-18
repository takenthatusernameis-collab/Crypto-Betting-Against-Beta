# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-18T20:30:00Z
- **Git state:** `main`, clean tree. Head is the WP2b commit that carries this file; its parent is `c565844`. Certify with `git log --oneline -4 && git status --short`.
- **P20 WP1 is LANDED at `33b84e2`** (beta-neutral default + frozen-per-window hold + acceptance file + `docs/BAB_FIDELITY.md` + README correction + CLI `--no-beta-neutral`).
- **P20 WP2 algebra is LANDED at `01eb301`** (opt-in `weighting="rank"`, exact 4-asset hand weights, no-lookahead, equal path byte-identical).
- **P20 WP2b is LANDED by this session.** Rank mode now has a leg-beta floor and a gross cap: a violating row is flat, never rescaled. Committed files: `config.py` (two fields + validation at `config.py:389-409`), `portfolio.py` (`_validate_rank_bounds` at `portfolio.py:53`, guard in `construct_rank_weights` at `portfolio.py:292`), `strategy.py` (forwarded from both `run()` and `dry_run()` at `strategy.py:416-417` / `757-758`), `tests/test_bab_p20_rank_weighting.py` (27 collected cases), `docs/BAB_FIDELITY.md` §9.1, README claim.
- **Measured effect of WP2b:** on the committed 9-asset fixture (`beta_window=90`, `q=0.3`, `tc=10bps`) rank mode goes from 25 active rows / gross up to **51.09** / worst day **−196.8%** / wealth `~1.5e-24` to **0 active rows / gross 0.0 / all-zero returns / cumulative 1.0** for daily, weekly and monthly. The 4-asset hand example is unchanged to `1e-12`. Rank is therefore *bounded but not empirically evaluable* on this fixture.
- **Baseline locks at HEAD (do not re-measure):** `beta_neutral: bool = True` (`config.py:99`); `weighting: str = "equal"` (`config.py:54`); `rank_min_leg_beta: float = 0.20` / `rank_max_gross: float = 4.0` (`config.py:57-58`); `construct_rank_weights(signals_df, betas, min_leg_beta=0.20, max_gross=4.0)` (`portfolio.py:292`); equal path still `0.7057` wealth / `−0.725` Sharpe / `+0.059` realized beta. **WP1, WP2 and WP2b are closed — never re-derive or re-open them.**
- **P20 remaining:** **WP0 (next, lane A)**, then WP3, WP5 (lane A), then WP4 (lane C). WP2b is done.
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral BAB trading system (ingest → beta → signals → portfolio → backtest → execution → ops).
- **P19 CLOSED.** Coverage complete, handlers annotated, scratch scripts removed. Never reopen.

---

# INITIAL TASK MESSAGE (BINDING — START HERE)

**Timestamp:** 2026-11-18T20:30:00Z · **Campaign:** P20 — "Make the repo actually Betting Against Beta" · **Lane:** A · **WP:** **WP0 — deterministic evidence harness**

**One-sentence objective:** build `scripts/bab_research_sweep.py`, commit `research_state/bab_p20/sweep.json` plus a markdown table rendered *from* that JSON, and prove with `tests/test_bab_p20_research_sweep.py` that reruns are byte-identical, every row carries the required metrics, the markdown contains no hand-typed digits, and the whole sweep runs in under 10 seconds — using `weighting="equal"` only.

**Why this and nothing else:** WP1/WP2/WP2b closed the strategy-fidelity path: the default book is beta-neutral, the frozen-window hold is real, and rank mode can no longer lever 51x. What the repository still lacks is **evidence infrastructure**. No committed sweep, no walk-forward, no break-even, no report. A repo named `Crypto-Betting-Against-Beta` cannot claim fidelity and then publish numbers from ad-hoc probes. WP0 is the first load-bearing evidence artifact; WP3/WP5/WP4 all consume the same deterministic pattern. Do not reopen product code.

**The deliverable is exact. You are NOT being asked to invent a research agenda or to improve the strategy.**

---

## MANDATORY FIRST ACTIONS (in order, ~4 minutes)

1. `git log --oneline -4 && git status --short` — locate yourself. Do not re-derive what this file certifies.
2. `bash scripts/bab_quick.sh` (≈20 s, must be GREEN). It also bootstraps numpy/pandas/scipy/pytest/ruff from PyPI; on a fresh runner raw `python3` snippets fail with `ModuleNotFoundError: numpy` until this has run once. Console scripts land in `~/.local/bin` (not on `PATH`) — always `python3 -m pytest`, `python3 -m ruff`.
3. Confirm the certified equal-weight baseline before touching anything (≈3 ms, must print `0.7057 -0.725 0.059`):
   ```bash
   python3 - <<'EOF'
   from strategies.betting_against_beta.data_loader import load_prices
   from strategies.betting_against_beta import BABStrategy, metrics
   r = load_prices("tests/fixtures/real_market_prices.csv", benchmark="BTC")
   o = BABStrategy(benchmark="BTC", beta_window=90, min_observations=60,
                   long_quantile=0.3, short_quantile=0.3,
                   transaction_costs=0.001).run(returns_df=r)
   rets = o.backtest["returns"]
   print(round(float(o.backtest["cumulative"].iloc[-1]), 4),
         round(float(metrics.sharpe_ratio(rets)), 3),
         round(float(metrics.strategy_beta(rets, r["BTC"])), 3))
   EOF
   ```
   If those differ by more than rounding, STOP and repair the tree before building the harness.
4. Read `research_state/perf_baseline_real_fixture.json` and `scripts/perf_baseline.py` for the artifact style, then read `docs/BAB_FIDELITY.md` §9.1. Do **not** add rank to the sweep.

---

## WP0 — design (apply exactly)

### A. Script — `scripts/bab_research_sweep.py`
- Deterministic in-process sweep over:
  - `beta_window ∈ {30, 60, 90, 120, 180}`
  - `long_quantile = short_quantile ∈ {0.2, 0.3}`
  - `transaction_costs ∈ {0.0, 0.001, 0.0025, 0.005}`
  - `beta_neutral ∈ {False, True}`
  - `weighting="equal"` only (80 configurations).
- Fixed `benchmark="BTC"`, `min_observations=60`, daily rebalance, committed fixture `tests/fixtures/real_market_prices.csv`.
- No network. No `Date.now`-dependent output. Iterate the grid in sorted order; serialize with sorted keys.
- Floats rounded to **6 decimal places** in the JSON. `beta_window=180` rows are descriptive/in-sample only and must be marked as such in the artifact metadata, not silently treated as OOS.
- Each result row must carry at least: `beta_window`, `long_quantile`, `short_quantile`, `transaction_costs`, `beta_neutral`, `wealth`, `sharpe`, `model_beta`, `realized_beta`, `gross`, `turnover`.
- Outputs:
  - `research_state/bab_p20/sweep.json` — provenance (`synthetic_fixture`, fixed seed, deliberate 2021-09-17 gap, all-NaN `DEL` column), grid, and rows.
  - `research_state/bab_p20/sweep.md` — table rendered **from the JSON object in memory**, never retyped.
- A public `build_sweep()` (pure, returns the dict) plus a `main()` that writes both files. The test suite calls `build_sweep()` directly.

### B. Test — `tests/test_bab_p20_research_sweep.py`
Must prove, with no hand-waving:
1. **Runtime:** one full sweep completes in **< 10 s** on the CI runner.
2. **Determinism:** two independent `build_sweep()` calls serialize to byte-identical JSON and SHA-256; two separate script runs produce identical file hashes.
3. **Completeness:** exactly `5 × 2 × 4 × 2 = 80` rows, every row has all required fields, every numeric field is finite (or explicitly `None` with a documented reason), and the fixture provenance string is present.
4. **Markdown integrity:** parse every numeric token in `sweep.md` and assert each appears in the JSON at the same 6-dp precision; assert the markdown was regenerated from JSON (compare against a fresh render).
5. **No rank leakage:** `weighting` is `"equal"` in every row; no rank/floor/cap field appears.
6. **Artifact contract:** `sweep.json` parses with `json.load`; top-level keys are stable; rerunning `main()` is idempotent on disk.

### C. Scope boundaries
- Do **not** edit `config.py`, `portfolio.py`, `strategy.py`, or any product module.
- Do **not** add rank to the sweep, do not publish a rank Sharpe/wealth, do not call the fixture real market data.
- Do **not** hand-type any number into `sweep.md`; render it.
- Do **not** create a second handoff or a parallel task doc.

### D. Commit rule
**One commit:** `scripts/bab_research_sweep.py` + `research_state/bab_p20/sweep.json` + `research_state/bab_p20/sweep.md` + `tests/test_bab_p20_research_sweep.py` (+ optional one-line README link). A script-only, artifact-only, or test-only commit is an automatic failed session. Never hand off mid-gate and never leave the tree red.

---

## Ground truth @ HEAD (certified; fixture is a deterministic synthetic random walk)

`tests/fixtures/real_market_prices.csv`: 398 rows, 2021-01-05 → 2022-07-15, costs 10 bps, `beta_window=90`, `min_observations=60`, 9 assets (BTC benchmark). **Not real market data.**

| Config | Wealth | Sharpe | Realized β | Max model β | Notes |
|---|---|---|---|---|---|
| **DEFAULT** w90 q0.3 (`beta_neutral=True`, daily) | 0.7057 (−29.4%) | −0.725 | +0.059 | 1.5e-04 | shipped default |
| w90 q0.2, post-WP1 | 1.3093 (+30.9%) | +0.649 | +0.006 | 2.1e-04 | in-sample only |
| w90 q0.3 weekly, equal | 0.8049 | −0.447 | +0.049 | 9.4e-02 | held-row drift |
| w90 q0.3 monthly, equal | 1.1492 | +0.496 | +0.083 | 1.2e-01 | held-row drift |
| w90 q0.3, opt-out (`beta_neutral=False`) | 0.3136 (−68.6%) | −1.418 | −0.572 | 1.11 | pre-WP1 behaviour |
| BTC buy-and-hold | 2.0975 (+109.7%) | +1.756 | 1.000 | — | benchmark |
| **rank** w90 q0.3, all frequencies | **1.0** | **not meaningful** | — | 0.0 | **WP2b flattens every row** |

Model beta and book weights live on `BABResult.weights` / `BABResult.betas` (NOT in `result.backtest`). Model beta = `(W * betas.reindex(columns=W.columns).fillna(0.0)).sum(axis=1)`. `backtest["cumulative"]` is a **wealth index** (1.0 = start); `final − 1` is total return. `backtest` keys: `cost_drag, cumulative, gross_return, returns, slippage_drag`.

**Honesty constraints (non-negotiable):**
1. Never present fixture results as real profitability. It is a fixed-seed random walk with a deliberate 2021-09-17 gap and an all-NaN `DEL` column.
2. The q0.2 row is **in-sample**. Never report in-sample selection as OOS — WP3 exists to prevent that.
3. **Rank mode is not empirically evaluable on this fixture.** Never quote a rank Sharpe/wealth. WP2b makes it safe/flat, not meaningful.
4. A null/negative OOS result is a valid, successful outcome. A fabricated positive is a failed session.

---

## Environment constraints (do not rediscover)

- **PyPI is reachable; the exchange API is not.** `bash scripts/bab_quick.sh` bootstraps `requirements.txt` + `ruff`. `https://api.exchange.coinbase.com` → **HTTP 403**; real-data ingestion is permanently external until a maintainer supplies a licensed CSV. Never put network calls in tests.
- Console scripts land in `~/.local/bin` → always `python3 -m pytest` / `python3 -m ruff`.
- `rg` not installed → use `grep -rn` or editor search.
- `bash scripts/bab_quick.sh` ≈ 20 s (ruff + 104 + 195). Full gate ≈ 130 s with `BAB_GATE_MIN_COVERAGE=100`. Fixture pipeline ≈ 3 ms. Verification is never the bottleneck.
- Full-gate baseline after WP2b: **6489 passed / 35 skipped / TOTAL 100% (6644/6644)**. It may only grow.
- `pytest --cov` in ad-hoc invocations can raise `ImportError: cannot load module more than once per process`; certify coverage with `scripts/bab_gate.sh`, never hand-rolled `--cov`.

---

## Campaign P20 map — lanes, status, file ownership

One session owns exactly one WP for its turn. Two sessions must never take the same WP; **the committed deliverable files are the claim**.

| Lane | WPs in order | Owned files | Status |
|---|---|---|---|
| **A — Research/evaluation** | **WP0 (now)** → WP3 → WP5 | `scripts/bab_research_sweep.py`, `scripts/bab_walk_forward.py`, `research_state/bab_p20/**`, `tests/test_bab_p20_research_sweep.py`, `tests/test_bab_p20_walk_forward.py`, `tests/test_bab_p20_breakeven.py` | WP0 ⬅ |
| **C — Reporting/consistency** | WP4 after WP0+WP3+WP2b | `docs/BAB_RESEARCH_REPORT.md`, `tests/test_bab_p20_report_consistency.py` | not started |
| **B — Strategy fidelity** | WP1 ✅, WP2 ✅, WP2b ✅ | `config.py`, `portfolio.py`, `strategy.py`, `docs/BAB_FIDELITY.md`, `tests/test_bab_p20_rank_weighting.py` | **closed** |

Rules: Lane A never edits product code; Lane B never edits research scripts or `research_state/`. **Solo default: WP0. If two sessions run concurrently: one takes WP0, one takes WP3 — the file sets are disjoint (`bab_research_sweep.*` vs `bab_walk_forward.*`).** Both must use `weighting="equal"` only.

### WP3 — Walk-forward / OOS harness (the anti-cherry-pick gate)
`scripts/bab_walk_forward.py`: rolling-origin splits, **5 folds**, parameter selection **only** on train, evaluation **only** on untouched test → `research_state/bab_p20/walk_forward.json` (per-fold selected params, OOS Sharpe/vol/mdd/turnover/beta; aggregate mean/median and fraction of folds with positive Sharpe) + rendered markdown. Feasible split on the 398-row fixture: `train=180` rows, then `5 × 40` test rows (ends at row 380), `beta_window ∈ {30,60,90,120}`, `min_observations=60`, `weighting="equal"`. **Do not use `beta_window=180` in WP3.** **Acceptance:** `tests/test_bab_p20_walk_forward.py` proves `max(train_index) < min(test_index)` for every fold; a planted `t+1` lookahead trap is detected and rejected; deterministic rerun hash equality; ≥40 test observations per fold.

### WP5 — Cost/turnover realism and break-even
Extend the sweep with the cost level at which OOS Sharpe crosses zero (bisection over `tc ∈ [0, 0.01]`, 6 iterations, deterministic), turnover per rebalance, gross exposure → `research_state/bab_p20/breakeven.json`. **Acceptance:** break-even cost monotone non-increasing in reported Sharpe, deterministic, and `tc=0` reproduces uncosted Sharpe within `1e-12`.

### WP4 — Honest reporting + provenance (merge point)
`docs/BAB_RESEARCH_REPORT.md` states fixture provenance (deterministic random walk, fixed seed, deliberate gap, NaN column), in-sample vs OOS distinction, cost assumptions, explicit conclusion, a "What this does NOT prove" section, and the §9.1 statement that rank mode is **not empirically evaluable** on this universe (no rank performance numbers may appear as results). **Acceptance:** `tests/test_bab_p20_report_consistency.py` parses the markdown tables and asserts every published number equals its JSON field; asserts the provenance sentence is present. Do **not** rename fixture files.

---

## Campaign P20 done-check (all must hold)

1. Default-config book: `max|Σ wᵢβᵢ| ≤ 1e-3` (daily, 6 grid points), `|realized β| ≤ 0.15` grid-wide (`≤0.07` at `w∈{90,120}`), committed test, weekly/monthly invariance, explicit opt-out byte-identical. **DONE (WP1).**
2. `weighting="rank"` exists, is opt-in, matches the hand weights to `1e-12`, unit-beta legs, zero total beta on rebalance rows, equal path byte-identical, no-lookahead proof. **DONE (WP2).**
3. Rank path is **numerically bounded**: leg-beta floor + gross cap flatten pathological rows, hand example unchanged, wide-universe proof, fixture-flat documented. **DONE (WP2b).**
4. `scripts/bab_research_sweep.py` + `scripts/bab_walk_forward.py` exist, deterministic (hash-equal reruns), JSON artifacts committed under `research_state/bab_p20/`. **WP0/WP3.**
5. `docs/BAB_RESEARCH_REPORT.md` exists; every published number machine-checked against JSON; no rank performance claim. **WP4.**
6. All `tests/test_bab_p20_*.py` pass; no existing test deleted/skipped/`xfail`-ed/weakened; coverage **100%** (6489/35 may only grow). **WP0 re-certifies.**
7. Full gate green: ruff PASS, reconcile GREEN, `bab_gate.sh` `BAB_GATE_MIN_COVERAGE=100` GREEN, 0 missed. **WP0 re-certifies.**
8. README no longer claims "dollar-neutral by default" as if that were BAB; it cites the fidelity doc and states rank is not empirically evaluable on the fixture. **DONE (WP1/WP2/WP2b).**

## P21 preview (deferred — activate only after all P20 checks pass)
**P21 — "Execution-grade BAB":** (1) real-data adapter for a maintainer-supplied licensed CSV, no network in-session, `research_state/p21/real_data_provenance.json`, rerun WP3/WP5 unchanged — if no CSV exists, deliver a validated import contract + clearly-labelled synthetic fallback, never a profitability claim; (2) capacity/liquidity model — per-asset ADV participation caps + square-root impact wired into `cost_model`, tests proving size scaling and rejection above caps; (3) execution realism — deterministic paper-trading soak over ≥250 rebalances with replay, reconciliation, restart/resume, modeled-vs-executed drift within tolerance; (4) robustness matrix — regime × cost × rebalance-frequency × weighting sweep, OOS-only conclusions, machine-checked report. Derive acceptance criteria from the P20 pattern (deterministic script + committed artifact + consistency test + honest report).

---

## No-idle ladder (if the assigned WP is blocked, do the next rung — never end a session empty-handed)

1. Blocked on the sweep shape? The grid and row fields are fixed in WP0 §A. There is no ambiguity to resolve.
2. Blocked on runtime <10 s? Cache the loaded fixture once per `build_sweep()` and reuse it across all 80 configs; do **not** reload the CSV per config.
3. Blocked on markdown/no-hand-typed-digits proof? Render the table with a single formatter from the JSON rows, then have the test re-render and compare strings.
4. Blocked on WP0 for any other reason? Take **WP3** — its fold geometry and acceptance tests are fully specified above and its files are disjoint.
5. Blocked on everything? Add the WP0 `sweep.json` schema validation test (80 rows, required fields, provenance, sorted keys) and commit it with the fixture-loading helper. Something landable always exists.

Every session must end with a committed **code/test/artifact** diff and a ledger row. If a WP is only partially done, commit the slice and write the exact remainder in its ledger row.

---

## Hard gates every session (repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

Inner loop: `bash scripts/bab_quick.sh` + `python3 -m pytest -q tests/test_bab_p20_*.py`. Full gate once per WP boundary; never hand off mid-gate. Never lower the coverage floor.

## Forbidden (automatic failure)
- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (WP0/WP4 artifacts count only **with** their consistency tests).
- Selecting parameters on the evaluation window and reporting the result as OOS.
- Describing the synthetic fixture as real market data, or publishing a Sharpe without the provenance caveat.
- Quoting rank-mode wealth/Sharpe from the 9-asset fixture as performance, or adding rank to the WP0/WP3 sweeps.
- Rescaling a rank row to satisfy the gross cap (breaks unit leg betas) or silently widening eligibility to negative betas.
- Deleting, skipping, `xfail`-ing, or loosening existing tests; special-casing fixture filenames in product code.
- "Fixing" rebalance-invariance failures by turning off beta correction in tests instead of making the product rebalance-aware.
- Reintroducing the retracted WP2 gate "zero dollars **and** unit-beta legs" (impossible in general; see ledger row of 2026-11-18T19:21:09Z).
- Running `enforce_beta_neutrality` on a rank book (it flips signs).
- Promoting `weighting="rank"` to the default without WP3 OOS evidence.
- Updating the CLI golden numbers, or chasing the retracted `|realized β| ≤ 0.06` / `≤ 0.10` grid-wide gates — both are measurement artefacts.
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, type-annotation/style churn, broad refactors, network fetching, committing probe/debug scratch scripts, or creating parallel handoff docs.

---

## Bottlenecks removed (do not re-create)

- **[REMOVED 2026-11-18T20:30:00Z] Rank mode 51x-levered and detonated the book.** WP2b landed the leg-beta floor (`0.20`) + gross cap (`4.0`): fixture rank book is now **0/398 active rows**, gross `0.0`, cumulative `1.0`; the 4-asset hand example is unchanged. Measured before/after in `docs/BAB_FIDELITY.md` §9.1.
- **[REMOVED 2026-11-18T20:30:00Z] Rank invariants were proved on a fixture with no rank dispersion.** The two fixture-based invariant tests are re-pointed to a deterministic 40-asset synthetic panel (true betas `0.35 … 1.90`) and every assertion is preserved; a new fixture-flat test pins the 9-asset scope statement.
- **[REMOVED 2026-11-18T20:30:00Z] §9.1 described the safety valves in present tense before they existed.** The implementation now matches the document; `rank_min_leg_beta` / `rank_max_gross` are real config fields with validation and both strategy call sites forward them.
- **[REMOVED 2026-11-18T20:30:00Z] The previous handoff still declared WP2b "next".** WP2b is committed; this initial task is now WP0 only.
- **[REMOVED earlier] The handoff still declared WP2 "next" after WP2 had landed.** A next session would have re-implemented or reverted it.
- **[REMOVED earlier] The prior WP2 hand table was arithmetically wrong.** The correct values from scores `[1.5, 0.5, 0.5, 1.5]` are `d = [3/4, 1/4]`, `e = [1/4, 3/4]`, `β_L = 23/40`, `β_H = 3/2`, weights `30/23, 10/23, −1/6, −1/2`, net `74/69`. Never re-assert `16/29` or `109/96`.
- **[REMOVED earlier] WP2 landed RED.** Mock config missing `weighting`; 6 uncovered statements. Gate restored to 100%.
- **[REMOVED earlier] Rank leg-sum guards were provably duplicate dead code.** Collapsed to one live guard with the identity documented.
- **[REMOVED earlier] Unclosed markdown fence in `docs/BAB_FIDELITY.md` §9.** Closed while adding §9.1.
- **[REMOVED earlier] Stale handoff claimed WP1 was unlanded.** Re-certified from the committed tree at `33b84e2`.
- **[REMOVED earlier] WP1 coverage regression** (TOTAL 99%, 8 missed statements) — two class-B finiteness-guard tests pinned to `beta_neutral=False`; restored to 100%.
- **[REMOVED earlier] WP2 acceptance gate was infeasible** — "zero dollars + unit-beta legs" cannot both hold under leg-level inverse-beta scaling unless `β_L = β_H`; corrected gate is unit-beta legs + zero model beta, with net cash exposure documented.
- **[REMOVED earlier] WP1 hidden test explosion** — blast radius measured (10 tests), fix landed.
- **[REMOVED earlier] Daily correction vs rebalance windows** — resolved by the frozen-window hold.
- **[REMOVED earlier] Lane collisions** — lanes A/B/C with disjoint file ownership.
- **[REMOVED earlier] Real-data rabbit hole** — Coinbase API is 403 here; deferred to P21.
- **[REMOVED earlier] Duplicate durable task docs** — deleted; this file is the single source of truth.
- **[REMOVED earlier] Fresh-runner dependency trap** — documented above.
- **[PERMANENTLY EXTERNAL] P19-1 CI enforcement.** Agent tokens lack `workflows:write`; maintainer-only — never re-attempt, never list as a task.

---

## Session ledger (append-only, concise)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-18T20:30:00Z | c565844 +1 | **WP2b landed.** Added `rank_min_leg_beta` / `rank_max_gross` config validation; floored/flattened rank rows in `construct_rank_weights`; forwarded from `run()` + `dry_run()`; re-pointed the two rank invariants to a 40-asset synthetic panel; added floor/cap/validation/fixture-flat tests; updated §9.1 + README. Rank on fixture: 25 active / gross 51.09 → 0 active / gross 0.0, cumulative 1.0. Opened WP0. | ruff PASS; quick GREEN; full gate **GREEN 6489 passed / 35 skipped / 100% (6644/6644)** (129.8 s) |
| 2026-11-18T20:24:09Z | c565844 | **WP2 verified landed; red gate repaired; WP2b opened.** Corrected the stale hand table, fixed the mock-config failure, proved the duplicate leg-sum guard dead, added 3 coverage tests, measured/wrote the 51x rank pathology. | GREEN 6473/35/100% (6623/6623) |
| 2026-11-18T19:21:09Z | 33b84e2 | **WP1 verified landed; coverage regression repaired; WP2 de-risked.** Retracted the infeasible "zero-dollar + unit-beta legs" gate; specified the FP rank construction and a feasible WP3 5×40 split. | GREEN 6462/35/100% (6566/6566) |
| 2026-11-18T18:33:27Z | 33b84e2 | **WP1 landed.** Beta-neutral default, frozen-per-window hold, 17-test acceptance file, fidelity doc, README corrections, `--no-beta-neutral`. | 6462/35/100% after repair |
| ≤2026-11-18T18:22:06Z | e376564 | WP1 de-risked on a scratch copy; duplicate task doc deleted; bot diagnostics ignored. | GREEN 6445/35/100% |
| ≤2026-11-18T14:47:47Z | 3393f8d | Handoff consolidation; grid measured; rebalance-aware fix pinned. | GREEN 6445/35/100% |
| ≤2026-11-18T14:43:40Z | 1a70054 | Campaign refresh; lanes + file ownership; network-403 note; P21 preview. | GREEN 6445/35/100% |
| ≤2026-11-18T14:19:40Z | f98eaa1 | **Opened P20.** Certified baseline; measured default-book beta −0.572 / −0.908. | GREEN 6445/35/100% |
| 2026-11-18T13:20:00Z | f55e570 | P19-7 finished: 7 handlers annotated; 13 scratch scripts removed. | GREEN 6445/35/100% |
| ≤2026-11-17T14:46:59Z | 73e4db2 | Original stakes closed; `strategies/betting_against_beta` 100% coverage. | 6282/35 |

## Proven closed (do not re-test, do not reopen)
P19-7 (222 broad/bare `except` handlers annotated, 0 unannotated), P19-2/3/4, P17-1/2, P18-1/2/3, kill-switch R4-B, bootstrap, reconciliation R5-B/R5-C, live-adapter two-key safety, 100% line coverage of `strategies/betting_against_beta`, Milestones 1–5 hygiene, **P20 WP1 (beta-neutral default + frozen rebalance windows + fidelity doc + README correction)**, **P20 WP2 algebra (rank construction, exact 4-asset hand example, no-lookahead, equal-path byte-identity)**, **P20 WP2b (rank leg-beta floor + gross cap + wide-universe proof + fixture-flat scope)**. `scripts/bab_except_inventory.py` is retained as a read-only audit tool; running it is not a deliverable.
