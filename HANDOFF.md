# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-18T20:16:33Z
- **Git state:** `main`. WP1 of P20 is **LANDED** at `33b84e2` (config flip + frozen-per-window hold + `tests/test_bab_p20_beta_neutral_default.py` + `docs/BAB_FIDELITY.md` + README correction + CLI `--no-beta-neutral`). This refresh adds **only** two class-B coverage pins in `tests/test_bab_p19_7_strategy_exceptions.py` (restoring 100% coverage) and this file — **product code is byte-identical to `33b84e2`**. Certify with `git log --oneline -3 && git status --short`.
- **Baseline locks at HEAD:** `beta_neutral: bool = True` (`config.py:99`); `_apply_rebalance(weights, rebalance_freq)` hold present at **both** correction sites (`strategy.py:518-519`, `822-823`); `docs/BAB_FIDELITY.md` and `tests/test_bab_p20_beta_neutral_default.py` exist. **WP1 is closed — never redo it.**
- **P20 remaining:** **WP2 (next)**, WP0, WP3, WP4, WP5. No `weighting` field exists yet (`grep -n "weighting" strategies/betting_against_beta/config.py` → no hits). No `scripts/bab_research_sweep.py`, `scripts/bab_walk_forward.py`, or `research_state/bab_p20/` exists.
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral BAB trading system (ingest → beta → signals → portfolio → backtest → execution → ops).
- **P19 CLOSED.** Coverage complete, handlers annotated, scratch scripts removed. Never reopen.

---

# INITIAL TASK MESSAGE (BINDING — START HERE)

**Timestamp:** 2026-11-18T20:16:33Z · **Campaign:** P20 — "Make the repo actually Betting Against Beta" · **Lane:** B (solo default) · **WP:** **WP2**

**One-sentence objective:** add faithful Frazzini–Pedersen **rank weighting** as an opt-in `weighting="rank"` path (default stays `"equal"`), landing `config.py` + `portfolio.py` + `strategy.py` + `tests/test_bab_p20_rank_weighting.py` + `docs/BAB_FIDELITY.md` §9 in **one** commit, with the hand-computed 4-asset weights below matching to `1e-12`.

**Why this and nothing else:** WP1 made the default book beta-neutral, but construction is still equal-weight ±1.0 per leg. That is **not** the Frazzini–Pedersen BAB construction: FP ranks assets by beta, gives larger weights to the extreme ranks, and scales each leg by `1/β_leg` so the long leg has beta `+1` and the short leg has beta `−1`. The repo name claims BAB; WP2 is the last fidelity gap before any OOS claim (WP3) can mean anything. Do **not** promote rank weighting to the default — promotion requires OOS evidence that does not exist yet.

**The design is fully specified and hand-verified below. You are NOT being asked to invent it or re-derive the algebra.** Implement it, run the gates, update the doc.

---

## MANDATORY FIRST ACTIONS (in order, ~3 minutes)

1. `git log --oneline -3 && git status --short` — locate yourself. Do not re-derive what this file certifies.
2. `grep -n "weighting" strategies/betting_against_beta/config.py` — if it prints a `weighting` field, WP2 has landed: take **WP0** (lane A spec below) instead. Never spend a session only reading.
3. `bash scripts/bab_quick.sh` (≈20 s, must be GREEN). **It also bootstraps numpy/pandas/scipy/pytest/ruff from PyPI** — on a fresh runner raw `python3` snippets fail with `ModuleNotFoundError: numpy` *until* this has run once. Console scripts land in `~/.local/bin`, which is not on `PATH`; use `python3 -m pytest` / `python3 -m ruff`, never bare `pytest`/`ruff`.
4. Confirm the gap in one command:
   ```bash
   grep -n "weighting" strategies/betting_against_beta/config.py strategies/betting_against_beta/portfolio.py   # must print nothing
   ```

---

## WP2 — Faithful Frazzini–Pedersen rank weighting (verified plan, apply it)

### 0. Corrected acceptance gate (read this before coding)

The old WP2 line "rank weights sum to zero dollars **and** unit-beta legs" is **mathematically infeasible** and is retracted. With leg-level inverse-beta scaling, the book is

```
w_L = d_L / β_L ,  w_H = -d_H / β_H ,  Σd_L = Σd_H = 1
```

so total beta is exactly `1 - 1 = 0`, while the net dollar exposure is

```
Σw = 1/β_L - 1/β_H
```

Dollar neutrality would require `β_L = β_H`, which does not hold in general (hand example below: `β_L = 16/29`, `β_H = 96/65`). **FP's factor is beta-neutral, not dollar-neutral; the net dollar exposure is funded by cash/borrow.** Therefore WP2 gates are:

- each leg's beta is exactly `±1` (`Σ_L w β = +1`, `Σ_H w β = −1`) within `1e-12`;
- total model beta is exactly `0` within `1e-12` **on the row where weights are formed** (i.e. rebalance rows when holding);
- the documented net dollar exposure is `1/β_L − 1/β_H`, **not** zero — pin it in the test rather than pretending otherwise;
- default `weighting="equal"` remains unchanged; rank mode is opt-in.

Do **not** route rank weights through `enforce_beta_neutrality`: that min-norm correction can flip long/short signs on a strongly tilted book (verified: on the hand example it produces `A = −0.0033`, `D = +0.2177`, residual beta `0.163`). Rank construction is already beta-neutral by construction; correction must be **skipped** in rank mode.

### 1. Product change — three files

**A. `config.py`** — add next to `rebalance_freq` (line ~51):

```python
    # Portfolio construction: "equal" (shipped default) or "rank"
    # (Frazzini-Pedersen rank weighting; beta-neutral legs, opt-in only).
    weighting: str = "equal"
```

Validation (in `_validate_ranges`, alongside `rebalance_freq`): `weighting` must be a string in `{"equal", "rank"}`; otherwise append an error so construction raises loudly. Do not silently coerce.

**B. `portfolio.py`** — add `construct_rank_weights(signals_df, betas)` plus optional args `betas=None, weighting="equal"` on `construct_portfolio`. `weighting="equal"` must take the existing branch **byte-identically**. For `"rank"`:

For each row `t`:
1. Eligible assets = selected by signal (`±1`) **and** `beta` finite and `> 0`.
2. If fewer than 1 eligible long **or** fewer than 1 eligible short → **all-zero row** (documented flat contract).
3. Rank eligible betas ascending with `pandas.rank(method="average")`; `m = mean(rank)`.
4. Score: long `a_i = m − rank_i`; short `a_j = rank_j − m` (both `>= 0`; an asset at the mean gets 0).
5. Dollar-normalize each leg: `d_i = a_i / Σ_L a`, `e_j = a_j / Σ_H a`. Degenerate zero-sum leg → flat row.
6. Leg betas `β_L = Σ_L d_i b_i`, `β_H = Σ_H e_j b_j`. If either is non-finite or `<= 0` → flat row.
7. Return `w_i = d_i / β_L` (long), `w_j = −e_j / β_H` (short). No beta correction afterwards.

Expose it publicly (no leading underscore) so the hand-computed test can call it directly. Keep signal cleaning identical to the equal branch (`trunc` semantics).

**C. `strategy.py`** — pass `weighting` and `betas` into `construct_portfolio` in `run()` (and `dry_run()` if it constructs weights). When `weighting == "rank"`:
- **skip** the `enforce_beta_neutrality` block entirely;
- still freeze the book inside weekly/monthly windows with `_apply_rebalance(weights, rebalance_freq)` (same hold WP1 added — rank weights are computed per day and would otherwise drift);
- do **not** change costs/turnover ordering or `_apply_rebalance`.

### 2. Hand-computed 4-asset example (exact, put these in the test)

Signals `A,B = +1` (long), `C,D = −1` (short); betas `A=0.5, B=0.8, C=1.2, D=1.6`.

- ranks `[0, 1, 2, 3]`, `m = 1.5`, scores `[1.5, 0.5, 0.5, 1.5]`
- dollar-normalized legs: `d = [24/29, 5/29]`, `e = [4/13, 9/13]`
- `β_L = 16/29 ≈ 0.5517241379310345`, `β_H = 96/65 ≈ 1.476923076923077`
- final weights:

| asset | exact | decimal |
|---|---|---|
| A | `3/2` | `1.5` |
| B | `5/16` | `0.3125` |
| C | `−5/24` | `−0.20833333333333331` |
| D | `−15/32` | `−0.46875` |

- leg betas `+1.0` / `−1.0`; total beta `0.0` (to floating noise)
- net dollar exposure `109/96 ≈ 1.1354166666666667` (= `1/β_L − 1/β_H`); long dollars `1.8125`, short dollars `−0.6770833333333333`

### 3. Test file — `tests/test_bab_p20_rank_weighting.py` (minimum set)

1. **`test_hand_computed_four_asset_rank_weights`** — call `construct_rank_weights` directly; assert the four exact fractions to `1e-12`, leg betas `±1` to `1e-12`, total beta `0` to `1e-12`, net dollars `109/96` to `1e-12`.
2. **`test_rank_book_is_beta_neutral_on_rebalance_rows`** — `BABStrategy(weighting="rank", rebalance_freq="weekly"|"monthly")` on the committed fixture; with `mask = strategy_mod._rebalance_mask(weights.index, freq)`, assert `max|Σ w β| ≤ 1e-12` on `mask` rows and the frozen-hold identity `weights.loc[~mask] == weights.where(mask).ffill().fillna(0).loc[~mask]` exactly. Held-row drift is expected and must **not** be asserted to zero.
3. **`test_rank_beats_equal_on_leg_beta_scaling`** — on the same fixture, rank mode's long/short leg betas are `±1` at each rebalance date (within `1e-12`); equal mode's are not.
4. **`test_equal_weight_path_byte_identical`** — explicit `weighting="equal"` reproduces the post-WP1 default exactly (weights frame identical; final wealth identical to `1e-12`). This is the no-regression gate.
5. **`test_rank_degenerate_rows_are_flat`** — non-finite betas, a leg with all `beta <= 0`, an empty long/short leg, and an empty signals frame all yield all-zero rows and never raise.
6. **`test_rank_no_lookahead`** — compute weights on the full frame and on a frame truncated at `t`; the weight row at `t` must be identical. Rank/leg scaling may use only betas at `t`.
7. **`test_invalid_weighting_surfaces`** — `BABConfig(weighting="bogus")` and a bad direct `construct_portfolio(weighting=...)` raise (`BABDataError`/config error); no silent fallback.
8. **No existing test deleted, skipped, `xfail`-ed, or loosened.** Baseline **6462 passed / 35 skipped** may only grow.

### 4. Docs acceptance

Append **§9 Rank weighting (opt-in, WP2)** to `docs/BAB_FIDELITY.md`: the construction formulas, the hand example table, the honest statement that FP legs are beta-neutral but **not** dollar-neutral (cash/borrow funds the net), that `weighting="equal"` remains the shipped default, and that rank is **not** promoted without OOS evidence from WP3. Update the §7 bullet that currently says rank weighting is "that is WP2" so the doc no longer describes landed work as future work. README stays truthful: it describes the default (equal-weight, beta-neutral); optionally add one clause that `weighting="rank"` is available as an opt-in research path — do not claim it is the default.

### 5. Commit rule

**One commit:** `config.py` + `portfolio.py` + `strategy.py` + `tests/test_bab_p20_rank_weighting.py` + `docs/BAB_FIDELITY.md` (+ optional one-line README). A docs-only / test-only / gate-only commit is an automatic failed session. Never leave the tree red; if the doc is unfinished, commit the green product+test slice and record the exact doc remainder in the ledger.

---

## Ground truth @`33b84e2` (certified 2026-11-18T19:21Z; do not re-measure)

Fixture `tests/fixtures/real_market_prices.csv`: 398 rows, 2021-01-05 → 2022-07-15, deterministic **synthetic** random walk, costs 10 bps, `beta_window=90`, `min_observations=60`.

| Config | Wealth | Sharpe | Ann. vol | Max DD | Realized β | Model β (max) | Turnover |
|---|---|---|---|---|---|---|---|
| **DEFAULT** w90 q0.3, post-WP1 (`beta_neutral=True`) | 0.7057 (−29.4%) | −0.725 | 0.258 | −0.413 | +0.059 | 1.5e-04 | 0.264 |
| w90 q0.2, post-WP1 | 1.3093 (+30.9%) | +0.649 | 0.366 | −0.227 | +0.006 | 2.1e-04 | 0.234 |
| w90 q0.3, opt-out (`beta_neutral=False`) | 0.3136 (−68.6%) | −1.418 | 0.446 | −0.758 | −0.572 | 1.11 | 0.201 |
| w90 q0.2, opt-out | 0.4214 (−57.9%) | −0.680 | 0.567 | −0.634 | −0.908 | 1.48 | 0.126 |
| BTC buy-and-hold | 2.0975 (+109.7%) | +1.756 | 0.291 | — | 1.000 | — | — |

- Full gate at current HEAD: **6462 passed / 35 skipped / 0 failed**, **TOTAL 100%** (6566/6566), `BAB_GATE_MIN_COVERAGE=100` GREEN. This refresh restored the last 8 statements (the two class-B finiteness-guard tests had to be pinned to `beta_neutral=False`, because the new default sanitizes planted `inf`/`NaN` before the guard).
- WP1 invariants are locked by `tests/test_bab_p20_beta_neutral_default.py` (17 tests): daily model β `≤1e-3` on the `w∈{60,90,120} × q∈{0.2,0.3}` grid; realized β `≤0.15` grid-wide and `≤0.07` at `w∈{90,120}`; `|Σw| ≤ 1e-9`; weekly/monthly frozen-hold + β-neutral on rebalance rows only; opt-out byte-identical.

Reproduce the core measurement (≈3 ms **after** `bash scripts/bab_quick.sh`):
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

Model beta and book weights live on `BABResult.weights` / `BABResult.betas` (NOT in `result.backtest`). Model beta = `(W * betas.reindex(columns=W.columns).fillna(0.0)).sum(axis=1)`.

**Honesty constraints (non-negotiable):**
1. The fixture is **not real market data**. `scripts/generate_real_market_fixture.py` builds deterministic random walks with a fixed seed, plus a deliberate 2021-09-17 gap and an all-NaN `DEL` column. Never present results on it as evidence of real profitability.
2. The q0.2 / `beta_neutral=True` row is **in-sample, not evidence of edge**. Never select parameters in-sample and report as OOS — that is what WP3 exists to prevent.
3. `backtest["cumulative"]` is a **wealth index** (1.0 = start), not a return. `final − 1` is total return.
4. **A null/negative OOS result is a valid, successful campaign outcome.** A fabricated positive is a failed session.

---

## Environment constraints (do not rediscover)

- **PyPI is reachable; the exchange API is not.** `bash scripts/bab_quick.sh` bootstraps `requirements.txt` + `ruff` automatically. `https://api.exchange.coinbase.com` → **HTTP 403**: real-data ingestion is permanently external until a maintainer supplies a licensed CSV. Never put network calls in tests.
- Console scripts land in `~/.local/bin` (not on `PATH`) → always invoke `python3 -m pytest` / `python3 -m ruff`.
- `rg` not installed → use `grep -rn` or the editor search tools.
- `bash scripts/bab_quick.sh` ≈ 20 s (ruff + 104 + 195). Full gate ≈ 2–4 min (measured 130.8 s with `BAB_GATE_MIN_COVERAGE=100`). Fixture pipeline ≈ 3 ms. Verification is never the bottleneck.
- `pytest --cov` can hit `ImportError: cannot load module more than once per process` in ad-hoc invocations; use the gate script (`scripts/bab_gate.sh`) for coverage certification instead of hand-rolled `--cov`.

---

## Campaign P20 map — lanes and file ownership

One session owns exactly one lane for its whole turn. Two sessions must never take the same WP; **the committed deliverable files are the claim**.

| Lane | WPs in order | Owned files |
|---|---|---|
| **A — Research/evaluation** | WP0 → WP3 → WP5 | `scripts/bab_research_sweep.py`, `scripts/bab_walk_forward.py`, `research_state/bab_p20/**`, `tests/test_bab_p20_research_sweep.py`, `tests/test_bab_p20_walk_forward.py`, `tests/test_bab_p20_breakeven.py` |
| **B — Strategy fidelity** | **WP2 (now)** | `strategies/betting_against_beta/{config,portfolio,strategy}.py`, `docs/BAB_FIDELITY.md`, `tests/test_bab_p20_rank_weighting.py` |
| **C — Reporting/consistency** | WP4 only, after WP3 + WP2 are committed | `docs/BAB_RESEARCH_REPORT.md`, `tests/test_bab_p20_report_consistency.py` |

Rules: Lane A never edits product code; Lane B never edits research scripts or `research_state/`. WP4 must publish **both** fidelity and OOS numbers and machine-check them. **Solo-session default: WP2. If two sessions run concurrently: one takes WP2 (lane B), one takes WP0 (lane A).**

### WP0 — Evidence harness (lane A, can run concurrently)
`scripts/bab_research_sweep.py`: deterministic sweep over `beta_window ∈ {30,60,90,120,180}`, `q ∈ {0.2,0.3}`, `tc ∈ {0,0.001,0.0025,0.005}`, `beta_neutral ∈ {False,True}` → `research_state/bab_p20/sweep.json` + a markdown table rendered **from** that JSON. Sorted keys, floats at 6 dp, byte-identical reruns, no network. **Acceptance:** `tests/test_bab_p20_research_sweep.py` proves runtime <10 s, identical SHA-256 across runs, every row carries `wealth/sharpe/beta/gross/turnover`, and no hand-typed digits in the markdown. Include a `model_beta` and `realized_beta` column per row — that is the evidence for the estimation-error finding. `beta_window=180` in WP0 is descriptive/in-sample only.

### WP3 — Walk-forward / OOS harness (the anti-cherry-pick gate)
`scripts/bab_walk_forward.py`: rolling-origin splits, **5 folds**, parameter selection **only** on train, evaluation **only** on untouched test → `research_state/bab_p20/walk_forward.json` (per-fold selected params, OOS Sharpe/vol/mdd/turnover/beta; aggregate mean/median and fraction of folds with positive Sharpe) + rendered markdown. Feasible split on the 398-row fixture: `train=180` rows, then `5 × 40` test rows (ends at row 380), `beta_window ∈ {30,60,90,120}`, `min_observations=60`. **Do not use `beta_window=180` in WP3** — it cannot satisfy 5×40 out-of-sample rows with a 180+60 warmup on this fixture. **Acceptance:** `tests/test_bab_p20_walk_forward.py` proves `max(train_index) < min(test_index)` for every fold; a planted `t+1` lookahead trap is detected and rejected; deterministic rerun hash equality; ≥40 test observations per fold.

### WP4 — Honest reporting + provenance (merge point)
`docs/BAB_RESEARCH_REPORT.md` states fixture provenance (deterministic random walk, fixed seed, deliberate gap, NaN column), in-sample vs OOS distinction, cost assumptions, explicit conclusion, and a "What this does NOT prove" section. **Acceptance:** `tests/test_bab_p20_report_consistency.py` parses the markdown tables and asserts every published number equals its JSON field; asserts the provenance sentence is present. Do **not** rename fixture files (many tests reference the path).

### WP5 — Cost/turnover realism and break-even
Extend the sweep with the cost level at which OOS Sharpe crosses zero (bisection over `tc ∈ [0, 0.01]`, 6 iterations, deterministic), turnover per rebalance, gross exposure → `research_state/bab_p20/breakeven.json`. **Acceptance:** break-even cost monotone non-increasing in reported Sharpe, deterministic, and `tc=0` reproduces uncosted Sharpe within `1e-12`.

---

## Campaign P20 done-check (all six must hold)

1. Default-config book: `max|Σ wᵢβᵢ| ≤ 1e-3` (daily, all 6 grid points) and `|realized β| ≤ 0.15` grid-wide (`≤0.07` at `w∈{90,120}`), committed test, weekly/monthly invariance preserved, explicit opt-out byte-identical to pre-WP1. **DONE.**
2. `weighting="rank"` exists, is opt-in, matches the hand-computed weights to `1e-12`, gives unit-beta legs and zero total beta on rebalance rows, keeps `weighting="equal"` byte-identical, and has a no-lookahead proof. **WP2.**
3. `scripts/bab_research_sweep.py` + `scripts/bab_walk_forward.py` exist, deterministic (hash-equal reruns), JSON artifacts committed under `research_state/bab_p20/`. **WP0/WP3.**
4. `docs/BAB_RESEARCH_REPORT.md` exists; every published number machine-checked against JSON. **WP4.**
5. All `tests/test_bab_p20_*.py` pass; no existing test deleted, skipped, `xfail`-ed, or weakened; coverage stays **100%** (baseline 6462/35 may only grow).
6. Full gate green: ruff PASS, reconcile GREEN, `bab_gate.sh` with `BAB_GATE_MIN_COVERAGE=100` GREEN, 0 missed.
7. README no longer claims "dollar-neutral by default" as if that were BAB; it cites the fidelity doc. **DONE.**

## P21 preview (deferred — activate only after all P20 checks pass)
Do not start P21 while P20 is open. **P21 — "Execution-grade BAB":** (1) real-data adapter for a maintainer-supplied licensed CSV, no network in-session, `research_state/p21/real_data_provenance.json`, rerun WP3/WP5 unchanged — if no CSV exists, deliver a validated import contract + clearly-labelled synthetic fallback, never a profitability claim; (2) capacity/liquidity model — per-asset ADV participation caps + square-root impact wired into `cost_model`, tests proving size scaling and rejection above caps; (3) execution realism — deterministic paper-trading soak over ≥250 rebalances with replay, reconciliation, restart/resume, modeled-vs-executed drift within tolerance; (4) robustness matrix — regime × cost × rebalance-frequency × weighting sweep, OOS-only conclusions, machine-checked report. Acceptance criteria are intentionally unwritten; derive them from the P20 pattern (deterministic script + committed artifact + consistency test + honest report).

---

## No-idle ladder (if an assigned WP is blocked, do the next rung — never end a session empty-handed)

1. Blocked on WP2 semantics? You are not — the algebra, the corrected gate, and the exact hand weights are above. Implement `construct_rank_weights`, add the 7 tests, run them.
2. Blocked on the 4-asset exactness? Use the fractions in §2 verbatim (`3/2`, `5/16`, `−5/24`, `−15/32`); assert against `fractions.Fraction`, not decimals.
3. Blocked on WP2 integration? Take **WP0** (lane A) — a deterministic sweep + hash test is always landable and needs no product code.
4. Blocked on data/network? Nothing needs network. Reread "Environment constraints" — the answer is no.
5. Blocked on everything? Add the missing `weighting` config validation + its two-line regression test. Something landable always exists.

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
- Deleting, skipping, `xfail`-ing, or loosening existing tests; special-casing fixture filenames in product code.
- "Fixing" rebalance-invariance failures by turning off beta-neutral correction in tests instead of making the product rebalance-aware.
- Reintroducing the retracted WP2 gate "zero dollars **and** unit-beta legs": impossible in general (see §0); rank mode is beta-neutral with documented net cash exposure.
- Running `enforce_beta_neutrality` on a rank book (it flips signs); rank construction is beta-neutral by construction.
- Promoting `weighting="rank"` to the default without WP3 OOS evidence.
- Updating the CLI golden numbers, or chasing the retracted `|realized β| ≤ 0.06` / `≤ 0.10` grid-wide gates — both are measurement artefacts, documented above.
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, type-annotation/style churn, broad refactors, network fetching, committing probe/debug scratch scripts, or creating parallel handoff docs.

---

## Bottlenecks removed (do not re-create)

- **[REMOVED 2026-11-18T19:21:09Z] Stale handoff claimed WP1 was unlanded.** HEAD `33b84e2` already contains the full WP1 product + test + doc + README change. The next session would have re-applied it or reverted it. Re-certified from the committed tree and rewrote the initial task to WP2.
- **[REMOVED 2026-11-18T19:21:09Z] WP1 landed with a coverage regression (TOTAL 99%, 8 missed statements).** Two class-B tests (`test_sites6_7_finiteness_guard_clamps_nonfinite`, `test_sites8_9_dry_run_finiteness_guard_degrades`) still used the new default, whose beta correction sanitizes the planted `inf`/`NaN` before the finiteness guard can execute. Pinned both to `beta_neutral=False`; full gate restored to **100% (6566/6566)** with `BAB_GATE_MIN_COVERAGE=100` GREEN.
- **[REMOVED 2026-11-18T19:21:09Z] WP2 acceptance gate was infeasible.** "Zero dollars + unit-beta legs" cannot both hold under leg-level inverse-beta scaling unless `β_L = β_H`; proof and corrected gates in WP2 §0. Also corrected the WP3 split so 5×40 OOS rows fit the 398-row fixture (`beta_window ≤ 120`, `train=180`).
- **[REMOVED earlier] WP1 hidden test explosion.** Blast radius classified exactly (6 goldens / 4 exception mocks / 2 invariance) and re-measured with the real fix (10 total).
- **[REMOVED earlier] Daily correction vs rebalance windows.** Resolved by Hunk B and landed.
- **[REMOVED earlier] Lane collisions.** Lanes A/B/C with disjoint file ownership.
- **[REMOVED earlier] Real-data rabbit hole.** Coinbase API is 403 here; real data is external, deferred to P21.
- **[REMOVED earlier] Duplicate durable task docs.** `NEXT_SESSION_TASK.md` / `AGENT_HANDOFF.md` deleted; this file is the single source of truth.
- **[REMOVED earlier] Bot diagnostics artefact untracked + ignored.** `research_state/workflow_run_diagnostics.jsonl` is gitignored; `*.egg-info/` ignored.
- **[REMOVED earlier] Fresh-runner dependency trap documented.** Raw `python3` snippets fail until `scripts/bab_quick.sh` bootstraps PyPI deps once; console scripts land outside `PATH`.
- **[PERMANENTLY EXTERNAL] P19-1 CI enforcement.** Agent tokens lack `workflows:write`; `.github/workflows/main.yml` does not invoke ruff/gates. Maintainer-only — never re-attempt, never list as a task.

---

## Session ledger (append-only, concise)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-18T19:21:09Z | 33b84e2 | **WP1 verified landed; coverage regression repaired; WP2 de-risked.** Found WP1 already committed at HEAD (config flip, frozen-window hold at both sites, 17-test P20 acceptance file, `BAB_FIDELITY.md`, README corrections, CLI opt-out). Re-certified invariants. Found WP1's pin list missed two class-B finiteness-guard tests, leaving 8 statements uncovered (TOTAL 99%); pinned both to `beta_neutral=False` → 100%. Retracted the infeasible WP2 "zero-dollar + unit-beta legs" gate with proof; specified the exact FP rank construction, the 4-asset hand weights (`3/2, 5/16, −5/24, −15/32`), the degenerate contracts, the no-lookahead test, and a feasible WP3 5×40 split. Product code unchanged. | ruff PASS; quick GREEN (104+195); full gate **GREEN 6462 passed / 35 skipped / 100% (6566/6566)** with `BAB_GATE_MIN_COVERAGE=100` (130.8 s) |
| 2026-11-18T18:33:27Z | 33b84e2 | **WP1 landed.** Flipped `beta_neutral` default to `True`; added frozen-per-window hold at both correction sites; added `tests/test_bab_p20_beta_neutral_default.py` (17 tests) + `docs/BAB_FIDELITY.md`; corrected README lines 14/24; added `--no-beta-neutral` to the example script; applied 4 class-B pins. Left two guard tests unpinned → 8 uncovered statements. | 6462 passed / 35 skipped; TOTAL 99% (8 missed) — repaired at 19:21Z |
| 2026-11-18T18:22:06Z | e376564 | **WP1 de-risked + handoff refreshed.** Prototyped the full WP1 fix on a scratch copy, measured the 6-point `w×q` grid, verified class-C invariance green and exactly 10 remaining failures, verified all four pins and byte-identical goldens/opt-out numbers, then reverted. Corrected two infeasible acceptance gates. Deleted duplicate `NEXT_SESSION_TASK.md`; untracked+ignored 768 KB bot diagnostics and `egg-info/`. | ruff PASS; quick GREEN; full gate GREEN 6445 passed / 35 skipped / 100% at `e376564` |
| 2026-11-18T14:47:47Z | 3393f8d | **Handoff consolidation + bottleneck removal.** Folded duplicate task doc into this file; measured the full beta-neutral grid; retracted the infeasible 0.06-as-written gate; pinned the rebalance-aware fix to exact insertion points. | ruff PASS; quick GREEN; reconcile baseline unchanged (6445/35/100%) |
| 2026-11-18T14:43:40Z | 1a70054 | Campaign refresh: re-verified ground truth, measured WP1 blast radius (12F/6433P/35S), added lanes + file ownership, network-403 note, P21 preview. | ruff PASS; quick GREEN; reconcile GREEN; full gate GREEN 6445/35/100% |
| 2026-11-18T14:19:40Z | f98eaa1 | **Opened P20.** Certified baseline; measured default-book beta −0.572 / −0.908; confirmed no walk-forward harness; confirmed equal-weight ±1.0. | ruff PASS; quick GREEN; reconcile GREEN; full gate GREEN 6445/35/100% |
| 2026-11-18T13:20:00Z | f55e570 | P19-7 finished: 7 handlers annotated with A/B evidence + tests; 13 scratch scripts removed. | full gate GREEN (6445/35/100%) |
| 2026-11-18T12:26:31Z | 1272f25 | Corrected stale "8 Milestone-4 sites" target; fixed RED ruff gate. | ruff PASS; quick GREEN; reconcile GREEN |
| ≤2026-11-17T14:46:59Z | 73e4db2 | All four original stakes closed; `strategies/betting_against_beta` 100% line coverage. | 6282 passed / 35 skipped |

## Proven closed (do not re-test, do not reopen)
P19-7 (222 broad/bare `except` handlers annotated, 0 unannotated), P19-2/3/4, P17-1/2, P18-1/2/3, kill-switch R4-B, bootstrap, reconciliation R5-B/R5-C, live-adapter two-key safety, 100% line coverage of `strategies/betting_against_beta`, Milestones 1–5 hygiene, **P20 WP1 (beta-neutral default + frozen rebalance windows + fidelity doc + README correction)**. `scripts/bab_except_inventory.py` is retained as a read-only audit tool; running it is not a deliverable.
