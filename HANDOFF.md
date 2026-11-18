# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-18T23:26:48Z
- **Git state:** `main`. This session lands P20 WP4 (report + consistency test). Certify with `git log --oneline -3 && git status --short`.
- **P20 IS COMPLETE AND CERTIFIED. Do not reopen it.** All eight done-check items hold. Full gate at this HEAD: **6537 passed / 35 skipped / 100% (6644/6644)**.
- **P20 WP4 is LANDED:** `docs/BAB_RESEARCH_REPORT.md` + `tests/test_bab_p20_report_consistency.py` (12 tests). 237 published numeric cells, 100% matched to committed JSON; tables are byte-identical to JSON-only renderers; rank discipline and null honesty are enforced mechanically.
- **P20 artifacts are FROZEN.** `research_state/bab_p20/**` and `docs/BAB_RESEARCH_REPORT.md` may not be edited again: the WP4 test re-renders those tables from JSON and will fail on any drift. New work goes to `research_state/bab_p21/**`.
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral BAB trading system.
- **P19 CLOSED. P20 CLOSED. Never reopen either.**

**Handoff reviewed and confirmed as the single durable handoff. The binding initial task message below is the most relevant, timestamped, clear directive for the next agentic work session, prioritized from the repository name (`Crypto-Betting-Against-Beta`) and the measured state at HEAD. P20 proved the construction; P21 must now decide whether the result is signal or noise, and must make rank mode empirically evaluable without weakening its safety guards. Four bottlenecks that would otherwise stall or mislead the next session are removed below.**

---

# INITIAL TASK MESSAGE (BINDING — START HERE)

**Timestamp:** 2026-11-18T23:26:48Z · **Campaign:** P21 "Signal or noise" · **Lane:** A · **WP:** **P21 WP0 — deterministic wide synthetic universe with a planted BAB effect**

**One-sentence objective:** write `scripts/bab_synthetic_universe.py` that generates a deterministic, sha-pinned wide universe (`≥41` tradable assets + BTC benchmark, `≥600` return rows, fixed seed) in two variants — `planted` (alpha strictly decreasing in beta, so a beta-neutral BAB book has positive expected alpha) and `null` (identical betas and marginals, equal alphas, so expected BAB alpha is zero) — and commit `research_state/bab_p21/universe.json` + `universe.md` + `tests/test_bab_p21_synthetic_universe.py`.

**Why this and nothing else:** P20 closed with a report that honestly says the 9-asset fixture cannot evaluate rank mode and that its walk-forward OOS result is not evidence of profitability. That leaves two unanswerable questions: *does the BAB estimator recover a real effect when one exists?* and *is the P20 OOS result distinguishable from noise?* Neither can be answered on the committed 9-asset fixture. P21 WP0 builds the controlled test bed both questions require, with a **known ground truth** so recovery and false positives can be measured instead of argued. It is the critical path: WP1 (rank evaluation), WP2 (significance/deflation) and WP3 (cost surface) all consume this artifact.

**Prioritization basis:** the repository name names a strategy, not a dataset. A faithful implementation is worthless if the next session cannot answer "does it work when there is something to find, and does it stay quiet when there is not?" The existing fixture is a 9-asset synthetic random walk; rank mode is flattened there by the leg-beta floor and gross cap (correct behaviour), and a positive mean OOS Sharpe on a random walk is exactly the false positive P21 must kill. WP0 is the only open row and every other P21 lane depends on it.

---

## ROUTE YOUR SESSION IN 60 SECONDS (no prose debate, no idle)

Deliverable files are the claim. Run:

```bash
git ls-files scripts/bab_synthetic_universe.py scripts/bab_rank_eval.py scripts/bab_significance.py scripts/bab_cost_surface.py docs/BAB_SIGNAL_OR_NOISE.md research_state/bab_p21
```

| First file missing from that list | Your WP | You own (create + commit) |
|---|---|---|
| `scripts/bab_synthetic_universe.py` | **P21 WP0** | `scripts/bab_synthetic_universe.py`, `research_state/bab_p21/universe.{json,md}`, `tests/test_bab_p21_synthetic_universe.py` |
| `scripts/bab_rank_eval.py` | P21 WP1 | `scripts/bab_rank_eval.py`, `research_state/bab_p21/rank_eval.{json,md}`, `tests/test_bab_p21_rank_eval.py` |
| `scripts/bab_significance.py` | P21 WP2 | `scripts/bab_significance.py`, `research_state/bab_p21/significance.{json,md}`, `tests/test_bab_p21_significance.py` |
| `scripts/bab_cost_surface.py` | P21 WP3 | `scripts/bab_cost_surface.py`, `research_state/bab_p21/cost_surface.{json,md}`, `tests/test_bab_p21_cost_surface.py` |
| `docs/BAB_SIGNAL_OR_NOISE.md` | **P21 WP4** | `docs/BAB_SIGNAL_OR_NOISE.md`, `tests/test_bab_p21_report_consistency.py` |

Rules:
1. Never take a WP whose deliverable script already exists (`git ls-files`, or on disk and passing its test). Commit an uncommitted WP first, verify it, then take the next missing one.
2. Solo default: **WP0**. Then WP1, WP2, WP3, WP4 in order — WP1/WP2/WP3 all import WP0's artifact and must not regenerate it.
3. A partially finished WP is not locked. If files exist only in the working tree (not `git ls-files`) or the gate is red, you own finishing it.
4. Everything blocked? Repair the red gate first (`bash scripts/bab_quick.sh`), then take the first missing row.
5. Never end a session with prose. A landed WP = deliverable + artifact + acceptance test in **one** commit + green full gate.
6. **A documentation-only session is a failed session.** If a user asks for a handoff refresh, you must also land the next missing WP (or a tested slice) in the same turn — then update this file with what landed.

---

## MANDATORY FIRST ACTIONS (in order, ~4 minutes)

1. `git log --oneline -4 && git status --short` — locate yourself. Do not re-derive what this file certifies.
2. `bash scripts/bab_quick.sh` (≈20 s, must be GREEN). It bootstraps numpy/pandas/scipy/pytest/ruff from PyPI.
3. Confirm the P20 default baseline is still frozen (≈3 ms, must print `0.7057 -0.725 0.059`):
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
   If those differ by more than rounding, STOP and repair the tree before building anything.
4. Read `scripts/bab_breakeven.py` for artifact style (`json.dumps(..., indent=2, sort_keys=True)`, 6-dp rounding, pure `build_*` + `render_markdown` + `write_artifacts` + `main`), read `tests/test_bab_p20_report_consistency.py` for the WP4 number-matching discipline, and read `docs/BAB_RESEARCH_REPORT.md` §"What this does NOT prove". Then inspect `BABStrategy.run` signature and `strategies/betting_against_beta/data_loader.py` so the universe you generate is consumable **in memory** (`returns_df=`) with no product-code change.

---

## P21 WP0 — Wide synthetic universe with planted ground truth (SPECIFICATION)

### A. Deliverable — `scripts/bab_synthetic_universe.py`

Pure functions only (`build_universe`, `render_markdown`, `write_artifacts`, `main`), no network, no product-code edits, no fixture edits. Generate returns directly, deterministically:

1. **Parameters (module constants, published in `provenance`):** `ASSETS ≥ 41`, `ROWS ≥ 600`, `SEED` fixed, `benchmark="BTC"`, asset betas drawn from a documented deterministic rule and stored per asset, idiosyncratic vol documented per asset, `planted_alpha_spread` published as an annualized number.
2. **Two variants, same seed and same marginals:**
   - `planted`: each asset has `alpha_i` strictly decreasing in `beta_i` (Spearman correlation between beta and alpha is exactly `-1`), calibrated so the beta-neutral BAB long/short book has a documented positive expected alpha.
   - `null`: identical betas, identical idiosyncratic draws, `alpha_i` equal for every asset, so the same BAB book has zero expected alpha.
   The only difference between variants is the alpha vector; the test must prove that.
3. **Return construction:** `r_i,t = alpha_i + beta_i * r_m,t + eps_i,t`, with `r_m` and `eps` generated from the fixed seed. No NaNs, no infinite values, no missing rows. `research_state/bab_p21/universe.json` stores both return panels (rounded to 6 dp), the per-asset beta/alpha/vol vectors, the benchmark series, the variant names, and a sha256 of each serialized panel so a consumer can prove it read the committed data.
4. **Schema:** `bab_p21.universe/1`. `universe.md` is rendered from the same dict (asset count, row count, seed, planted vs null alpha range, panel shas) and contains no number that is not in the JSON.

### B. Test — `tests/test_bab_p21_synthetic_universe.py`

Must prove, mechanically:
1. **Determinism:** two `build_universe()` calls serialize byte-identically; the committed `universe.json` equals a fresh build (`json.dumps(..., indent=2, sort_keys=True) + "\n"`).
2. **Scale minimums:** `assets ≥ 41`, `return_rows ≥ 600`, both variants present, benchmark column present.
3. **Planted ground truth:** in `planted`, `spearman(beta, alpha) == -1` exactly and `alpha` is strictly decreasing in `beta`; in `null`, all alphas are equal. Assert the two variants share identical betas and identical idiosyncratic residuals row-for-row (prove the alpha vector is the only difference).
4. **Recovery in expectation (analytic, not backtest-dependent):** construct the beta-neutral equal-weight BAB book directly from the published weights of one `BABStrategy.run(returns_df=...)` call and assert `Σ w_i alpha_i > 0` on `planted` and `≈ 0` (documented tolerance) on `null`, while `Σ w_i = 0` and `Σ w_i beta_i ≈ 0` on both. This separates construction correctness from sampling noise.
5. **No leakage / no NaNs:** both panels are finite, shape `(return_rows, assets)`, and the benchmark is aligned to the same index.
6. **Markdown is JSON-derived:** every number in `universe.md` exists in `universe.json`.
7. **Runtime:** full build under 5 s; no network import.

### C. Scope boundaries
- Own **only** `scripts/bab_synthetic_universe.py`, `research_state/bab_p21/universe.{json,md}`, `tests/test_bab_p21_synthetic_universe.py` (+ this `HANDOFF.md`).
- Do **not** edit product code, the P20 fixture, any P20 artifact, or `docs/BAB_RESEARCH_REPORT.md`. Do not weaken the rank guards (`rank_min_leg_beta`, `rank_max_gross`). Do not create a second handoff doc.

### D. Commit rule
**One commit:** script + both artifacts + acceptance test + this `HANDOFF.md` + the ledger row. An artifact-only or script-only commit is a failed session. Never hand off mid-gate and never leave the tree red.

---

## P21 remaining WPs (consume WP0 read-only; do not regenerate it)

| WP | Deliverable script | Must prove |
|---|---|---|
| **WP1 — rank vs equal evaluation** | `scripts/bab_rank_eval.py` + `rank_eval.{json,md}` | On the `planted` universe rank and equal books are **both active** (active rows > 0; leg betas respect the floor, gross respects the cap) and both recover the planted alpha, with per-book `Σwβ≈0`. On `null` the recovery vanishes. Rank guards are never relaxed. Byte-identical reruns. |
| **WP2 — significance + deflation** | `scripts/bab_significance.py` + `significance.{json,md}` | Fixed-seed moving-block bootstrap of the OOS Sharpe (≥ 2000 resamples) on both variants; a deflated Sharpe correction for the 40-candidate grid; **null calibration**: the false-positive rate on `null` must be ≤ the documented nominal slack, and the `planted` effect must be detected. Hand-computed DSR unit case pinned in the test. |
| **WP3 — multi-component cost surface** | `scripts/bab_cost_surface.py` + `cost_surface.{json,md}` | Linear cost + borrow/funding + notional slippage; per-row costed performance is non-increasing in each component; nulls/censoring are reported with documented reasons, never as zero tolerances; byte-identical reruns. |
| **WP4 — honest verdict report** | `docs/BAB_SIGNAL_OR_NOISE.md` + `tests/test_bab_p21_report_consistency.py` | **100%** of published table numbers match P21 JSON fields at 6 dp (zero unmatched), tables are byte-identical to JSON-only renderers, explicit signal-vs-noise verdict, explicit statement that planted-universe recovery is a **controlled synthetic** result and not market evidence, and no re-run of any harness. |

Rules that keep P21 honest: recovery on a **planted synthetic** universe proves the *estimator* works; it is never market alpha. A `null`-universe positive result is a **bug**, not a finding. If a stated acceptance criterion is measured false, replace it with a provable per-row invariant and record the removal under "Bottlenecks removed" — do not weaken the test to pass.

---

## Ground truth @ HEAD (certified; the P20 fixture is a deterministic synthetic random walk)

- Default `w90 q0.3, tc=0.001, beta_neutral=True`: wealth `0.705655`, Sharpe `-0.725483`, realized β `+0.058754`, model β `1.51e-04`.
- `tests/fixtures/real_market_prices.csv`: **399 price rows → 398 return rows**, 2021-01-04 → 2022-07-15, seed `20261028`, deliberate gap `2021-09-17`, all-NaN `DEL`, 9 assets + BTC. **Not real market data.**
- P20 sweep: 80 rows, selects **no winner**. P20 walk-forward: 5 folds × 40 OOS rows, mean OOS Sharpe `1.305563`, fraction positive `0.6` — **not** evidence of profitability.
- P20 break-even: 10 rows, three non-positive uncosted Sharpe, one censored at the `0.01` ceiling; `None` is never zero.
- Rank mode on the 9-asset fixture is flattened to a zero book by the leg-beta floor and gross cap. That is why P21 generates its own universe; it does not mean the guards are wrong.
- `backtest["cumulative"]` is a **wealth index** (1.0 = start). Model beta and weights live on `BABResult.weights` / `BABResult.betas`, not in `result.backtest`.

**Honesty constraints (non-negotiable):**
1. Never present synthetic results as real profitability, and never quote planted-universe recovery as market alpha.
2. In-sample grid winners are not OOS evidence.
3. Rank mode is not empirically evaluable on the P20 fixture. It **is** evaluable on the P21 generated universe, and that result must be labelled controlled/synthetic.
4. A null or negative result is a valid, successful outcome. A fabricated positive is a failed session.

---

## Environment constraints (do not rediscover)

- **PyPI is reachable; the exchange API is not.** `bash scripts/bab_quick.sh` bootstraps `requirements.txt` + `ruff`. `https://api.exchange.coinbase.com` → **HTTP 403**; real-data ingestion is permanently external until a maintainer supplies a licensed CSV. Never put network calls in tests. Never make real-data ingestion a P21 task.
- Console scripts land in `~/.local/bin` → always `python3 -m pytest` / `python3 -m ruff`.
- `rg` is not installed → use `grep -rn` or editor search.
- `bash scripts/bab_quick.sh` ≈ 20 s. Full gate ≈ **137 s** with `BAB_GATE_MIN_COVERAGE=100`.
- Full-gate baseline at this HEAD: **6537 passed / 35 skipped / TOTAL 100% (6644/6644)**. It may only grow.
- `pytest --cov` in ad-hoc invocations can raise `ImportError: cannot load module more than once per process`; certify coverage with `scripts/bab_gate.sh`, never hand-rolled `--cov`.
- `scripts/` is an importable package (`scripts/__init__.py`) — tests import `from scripts import bab_breakeven`.

---

## Campaign P21 map — lanes, status, file ownership

One session owns exactly one WP for its turn. Two sessions must never take the same WP; **the committed deliverable files are the claim.**

| Lane | WPs in order | Owned files | Status |
|---|---|---|---|
| **A — Ground truth** | **WP0** | `scripts/bab_synthetic_universe.py`, `research_state/bab_p21/universe.{json,md}`, `tests/test_bab_p21_synthetic_universe.py` | **UNBLOCKED — start here** |
| **B — Rank evaluation** | WP1 | `scripts/bab_rank_eval.py`, `research_state/bab_p21/rank_eval.{json,md}`, `tests/test_bab_p21_rank_eval.py` | blocked on WP0 |
| **C — Statistics** | WP2 | `scripts/bab_significance.py`, `research_state/bab_p21/significance.{json,md}`, `tests/test_bab_p21_significance.py` | blocked on WP0 |
| **D — Execution realism** | WP3 | `scripts/bab_cost_surface.py`, `research_state/bab_p21/cost_surface.{json,md}`, `tests/test_bab_p21_cost_surface.py` | blocked on WP0 |
| **E — Reporting** | WP4 | `docs/BAB_SIGNAL_OR_NOISE.md`, `tests/test_bab_p21_report_consistency.py` | blocked on WP1–WP3 |

Rules: one WP per session; lanes B/C/D consume `universe.json` read-only and must never regenerate it; lane E reads JSON only and never re-runs a harness. P20 artifacts are frozen. Solo default: **WP0**.

---

## Campaign P21 done-check (all must hold)

1. `scripts/bab_synthetic_universe.py` exists; both variants are deterministic (hash-equal reruns), `≥41` assets, `≥600` rows; planted alpha/beta Spearman is exactly `-1`; the null variant differs only in alphas. **WP0.**
2. Rank and equal books are both active on the planted universe and respect the leg-beta floor + gross cap; recovery exists on planted and vanishes on null; no guard relaxed. **WP1.**
3. Fixed-seed block bootstrap + deflated Sharpe; null false-positive rate within documented slack; planted effect detected. **WP2.**
4. Multi-component cost surface with honest censoring/null reasons and per-row monotonicity. **WP3.**
5. `docs/BAB_SIGNAL_OR_NOISE.md` exists; **100%** of published numbers machine-checked against P21 JSON; explicit signal-vs-noise verdict; planted recovery labelled synthetic. **WP4.**
6. All `tests/test_bab_p21_*.py` pass; no existing test deleted/skipped/`xfail`-ed/weakened; coverage **100%** (6537/35 may only grow). **Every WP re-certifies.**
7. Full gate green: ruff PASS, reconcile GREEN, `bab_gate.sh` `BAB_GATE_MIN_COVERAGE=100` GREEN, 0 missed. **Every WP re-certifies.**

**Scoreboard command (run before declaring P21 done):**
```bash
git ls-files scripts/bab_synthetic_universe.py scripts/bab_rank_eval.py scripts/bab_significance.py scripts/bab_cost_surface.py docs/BAB_SIGNAL_OR_NOISE.md research_state/bab_p21
python3 -m pytest -q tests/test_bab_p21_*.py
```

---

## Work quantum — the minimum a session must produce (anti-shallow-work)

A session is **not** complete unless **all** of the following landed in one commit:

1. One complete WP from the routing table (or one tested slice of it with the exact remainder written in the ledger).
2. Its **script + committed artifact + acceptance test** (WP4: report + consistency test).
3. A hash-determinism assertion, not a "looks stable" claim.
4. `python3 -m ruff check .` PASS and `bash scripts/bab_quick.sh` GREEN; full gate once per WP boundary.
5. A ledger row below with UTC timestamp, HEAD, what landed, and the gate line.
6. **No documentation-only turn.** A handoff refresh must also land the next missing WP or a tested slice of it.

**Hard minimums that make a WP impossible to fake:** WP0 `≥41 assets, ≥600 rows, two variants, Σwᵢαᵢ>0 planted / ≈0 null, sha-pinned panels`; WP1 `active rows > 0 for both books, guard compliance, recovery on planted only`; WP2 `≥2000 resamples, fixed seed, DSR hand case, null FPR bound`; WP3 `≥3 cost components, per-row monotonicity, documented null reasons`; WP4 `100%` of published numbers matched, zero unmatched, no harness re-run. If you are writing prose instead of a test, you are avoiding the work — stop and take the next routing row.

## No-idle ladder (if the assigned WP is blocked, do the next rung — never end a session empty-handed)

1. WP0 feels large? Start with `build_universe` returning the dict and a determinism test; the planted/null alpha construction is a one-line alpha vector over a shared beta/residual draw.
2. Blocked on the recovery assertion? Compute `Σ wᵢαᵢ` from the published weights of one `run()` call — it is algebra, not a backtest, and it fails loudly if the construction is wrong.
3. Blocked on WP1 because rank books are flat? That is the fixture trap; on the WP0 universe leg betas must clear the `0.20` floor. If they do not, fix the universe parameters — never the guards.
4. Blocked on WP2 bootstrap? Implement a plain fixed-seed moving-block resampler over the OOS return vector; pin the block length in `provenance` and test determinism before adding the DSR.
5. Blocked on everything? Repair the gate and add one missing test in a P21 test file. Something landable always exists.

Every session must end with a committed **code/test/artifact** diff and a ledger row. If a WP is only partially done, commit the slice and write the exact remainder in its ledger row.

---

## Hard gates every session (repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

Inner loop: `bash scripts/bab_quick.sh` + `python3 -m pytest -q tests/test_bab_p21_*.py`. Full gate once per WP boundary; never hand off mid-gate. Never lower the coverage floor.

## Forbidden (automatic failure)
- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (WP4 artifacts count only **with** their consistency tests; a handoff refresh without a landed WP is not a session).
- Editing `research_state/bab_p20/**`, `docs/BAB_RESEARCH_REPORT.md`, or any P20 script (P20 is closed and frozen; edits break the WP4 consistency test).
- Weakening `rank_min_leg_beta` / `rank_max_gross` or the rank guard logic to make rank "active" on the fixture.
- Selecting parameters on the evaluation window and reporting the result as OOS.
- Describing any synthetic universe as real market data, or publishing a Sharpe without the provenance caveat.
- Quoting P21 planted-universe recovery as market alpha, or treating a `null`-universe positive result as a finding instead of a bug.
- Deleting, skipping, `xfail`-ing, or loosening existing tests; special-casing fixture filenames in product code.
- Reopening P19 annotation/coverage work or P20 evidence work, re-attempting CI workflow edits, adding new `P19-7` markers, type-annotation/style churn, broad refactors, network fetching, committing probe/debug scratch scripts, or creating parallel handoff docs.

---

## Bottlenecks removed (do not re-create)

- **[REMOVED 2026-11-18T23:26:48Z] P20 had no next row, so the old routing table would route every session to "everything done" and invite an idle/docs-only turn.** The routing table now starts at P21 WP0 and each row has a committed-file claim.
- **[REMOVED 2026-11-18T23:26:48Z] "Rank is not empirically evaluable" was a repo-wide dead end.** It is true only for the 9-asset P20 fixture, where the leg-beta floor and gross cap correctly flatten the book. P21 WP0 makes rank evaluable on a generated `≥41`-asset universe **without** touching the guards; the scope statement is now variant-specific.
- **[REMOVED 2026-11-18T23:26:48Z] A positive mean OOS Sharpe on a random walk looked like a result.** P20's aggregate (`mean_oos_sharpe 1.305563` on a pure synthetic random walk) is a false-positive demonstration. P21 WP2 makes a significance/deflation verdict mandatory before any positive claim, and WP0's `null` variant gives the false-positive calibration target.
- **[REMOVED 2026-11-18T23:26:48Z] P20 freeze ambiguity.** Editing P20 artifacts after WP4 would silently invalidate the number-matching test. P20 is now explicitly frozen; P21 writes only new files.
- **[REMOVED 2026-11-18T22:36:59Z] WP5's "cross-row monotonicity" acceptance criterion was mathematically false.** Cost drag is `tc * turnover`, so a higher uncosted Sharpe can break even sooner (measured: `(w60,q0.2)` `0.834694`/`0.004609` beats `(w90,q0.2)` `0.810267`/`0.005078`). Replaced with the provable per-row law: costed Sharpe is non-increasing in `tc`.
- **[REMOVED 2026-11-18T22:36:59Z] WP5's `[0, 0.01]` search range censors the best configuration.** `w180 q0.2` stays positive at `tc=0.01`; the harness reports a documented `None` (censored) instead of a meaningless bisection midpoint.
- **[REMOVED 2026-11-18T22:36:59Z] Three configurations have non-positive uncosted Sharpe**, so no break-even exists; reported as documented `None`, never as zero.
- **[REMOVED 2026-11-18T21:38:00Z] WP0 sat as "next" across four handoff refreshes.** Landed with 80 rows and hash-pinned artifacts.
- **[REMOVED 2026-11-18T21:18:00Z] WP choice was prose.** Artifact-based routing (`git ls-files`) decides the WP.
- **[PERMANENTLY EXTERNAL] P19-1 CI enforcement.** Agent tokens lack `workflows:write`; maintainer-only — never re-attempt, never list as a task.
- **[PERMANENTLY EXTERNAL] Real market data ingestion.** `api.exchange.coinbase.com` returns 403 from this environment; a licensed CSV is maintainer-supplied. Never a P21 task.

---

## Session ledger (append-only, concise)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-18T23:26:48Z | `27eb92d` + working tree | **P20 WP4 landed — P20 CLOSED (heavy work, not a refresh).** Added `docs/BAB_RESEARCH_REPORT.md` (provenance, construction, in-sample, walk-forward, costs/break-even, conclusion, limits, §9.1 rank discipline) and `tests/test_bab_p20_report_consistency.py` (12 tests: 237/237 published numeric cells matched to committed JSON, byte-identical JSON renderers, no stray prose number, no rank number, every null break-even documented). Opened **P21 "Signal or noise"** with WP0 (wide planted synthetic universe) as the binding next row and removed four stalling/misleading bottlenecks. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6537 passed / 35 skipped / 100% (6644/6644)** (136.55 s) |
| 2026-11-18T22:36:59Z | `4ad98ee` + working tree | **WP5 landed (heavy work, not a refresh).** Added `scripts/bab_breakeven.py` (pure `build_breakeven`, `bisect_break_even` with a 6-step trace, `render_markdown`, `write_artifacts`, `main`), wrote `breakeven.json` (10 rows, sha `6016abdb…`) and `breakeven.md`, added `tests/test_bab_p20_breakeven.py` (16 tests, including a bracket-halving invariant). Measured and removed two impossible spec criteria. Re-routed to **WP4, the only open row**. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6525 passed / 35 skipped / 100% (6644/6644)** (136.64 s) |
| 2026-11-18T22:30:27Z | `5299dbb` | Handoff review + binding initial task message refresh. Confirmed this is the single durable handoff. No code changes in this turn. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6509 passed / 35 skipped / 100% (6644/6644)** (138.92 s) |
| 2026-11-18T22:27:00Z | `5299dbb` | WP5 session start. No code changes in this turn. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6509 passed / 35 skipped / 100% (6644/6644)** (138.92 s) |
| 2026-11-18T22:17:00Z | `7e83a95` + working tree | **WP3 landed.** Added `scripts/bab_walk_forward.py`, 5×40 expanding walk-forward with train-only selection, artifacts, `tests/test_bab_p20_walk_forward.py` (10 tests). | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6509 passed / 35 skipped / 100% (6644/6644)** (138.92 s) |
| 2026-11-18T21:38:00Z | `14a3935` + working tree | **WP0 landed.** Added `scripts/bab_research_sweep.py`, `sweep.json` (80 rows, sha `ffb98c33…`), `sweep.md`, `tests/test_bab_p20_research_sweep.py` (10 tests). | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6499 passed / 35 skipped / 100% (6644/6644)** (134.25 s) |
| 2026-11-18T21:28:21Z | 0452bd1 | Handoff re-certification (documentation only). Corrected stale git-state. | ruff PASS; quick GREEN; baseline `0.7057 -0.725 0.059` |
| 2026-11-18T21:18:00Z | 7637fba | Handoff refresh (documentation only). Added artifact-based routing, de-collided WP5, JSON schemas for WP4. | ruff PASS; quick GREEN; full gate 6489/35/100% (129.4 s) |
| 2026-11-18T20:30:00Z | c565844 +1 | **WP2b landed.** Leg-beta floor + gross cap; rank fixture book 25 active / gross 51.09 → 0 active / gross 0.0. | ruff PASS; quick GREEN; full gate 6489/35/100% (129.8 s) |
| ≤2026-11-18T18:33:27Z | 33b84e2 | **WP1 landed.** Beta-neutral default, frozen-per-window hold, 17-test acceptance file, fidelity doc, README corrections, `--no-beta-neutral`. | 6462/35/100% after repair |
| ≤2026-11-18T14:19:40Z | f98eaa1 | **Opened P20.** Certified baseline; measured default-book beta −0.572 / −0.908. | GREEN 6445/35/100% |

---

## Proven closed (do not re-test, do not reopen)

P19-7 (222 broad/bare `except` handlers annotated, 0 unannotated), P19-2/3/4, P17-1/2, P18-1/2/3, kill-switch R4-B, bootstrap, reconciliation R5-B/R5-C, live-adapter two-key safety, 100% line coverage of `strategies/betting_against_beta`, Milestones 1–5 hygiene, **P20 WP0 (deterministic 80-row equal-weight sweep + hash-pinned artifacts + 10-test acceptance file)**, **P20 WP1 (beta-neutral default + frozen rebalance windows + fidelity doc + README correction)**, **P20 WP2 algebra (rank construction, exact 4-asset hand example, no-lookahead, equal-path byte-identity)**, **P20 WP2b (rank leg-beta floor + gross cap + wide-universe proof + fixture-flat scope)**, **P20 WP3 (walk-forward with train-only selection + anti-lookahead guards + 10-test acceptance file)**, **P20 WP5 (10-row break-even bisection, 6 fixed iterations, 16-test acceptance file, censoring and non-positive rows reported as documented nulls)**, **P20 WP4 (published report with 237/237 numbers machine-matched to committed JSON, JSON-only table renderers, rank discipline and null honesty enforced by 12 tests)**. `scripts/bab_except_inventory.py` is retained as a read-only audit tool; running it is not a deliverable.
