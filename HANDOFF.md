# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-18T23:32:30Z
- **Git state:** `main`. This session lands P21 WP0 (deterministic wide universe with planted ground truth). Certify with `git log --oneline -3 && git status --short`.
- **P21 WP0 IS LANDED WITH `14` NEW PASSING TESTS.** `scripts/bab_synthetic_universe.py`, `research_state/bab_p21/universe.{json,md}`, `tests/test_bab_p21_synthetic_universe.py`.
- **P20 IS COMPLETE AND CERTIFIED. Do not reopen it.** `research_state/bab_p20/**` and `docs/BAB_RESEARCH_REPORT.md` are frozen: the WP4 test re-renders those tables from JSON and fails on any drift.
- **Full gate at this HEAD + working tree: 6551 passed / 35 skipped / 100% (6644/6644)**.
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral BAB trading system.

**Handoff reviewed and confirmed as the single durable handoff. The binding initial task message below is the most relevant, timestamped, clear directive for the next agentic work session, prioritized from the repository name (`Crypto-Betting-Against-Beta`) and the measured state at HEAD. P20 proved the construction. P21 WP0 now supplies a controlled universe with known ground truth. P21 must use it to decide whether the strategy recovers a real effect when one exists and stays quiet when none does. Three bottlenecks that would otherwise stall or mislead the next session are removed below — including a math trap that silently zeroed the planted effect.**

---

# INITIAL TASK MESSAGE (BINDING — START HERE)

**Timestamp:** 2026-11-18T23:32:30Z · **Campaign:** P21 "Signal or noise" · **Lane:** B · **WP:** **P21 WP1 — rank vs equal evaluation on the planted universe**

**One-sentence objective:** write `scripts/bab_rank_eval.py` that loads the committed `research_state/bab_p21/universe.json` read-only, runs the shipped `BABStrategy` twice per variant (`weighting="equal"` and `weighting="rank"`, identical non-weighting config), and proves on the `planted` variant that **both books are active and both recover the planted alpha with a beta-neutral book**, while on the `null` variant the recovery vanishes — then commit `research_state/bab_p21/rank_eval.{json,md}` and `tests/test_bab_p21_rank_eval.py`.

**Why this and nothing else:** WP0 landed a 41-asset, 600-row universe where the planted alpha is strictly decreasing in beta and the null variant differs only in the alpha vector. It also settled the test bed's stability: with idiosyncratic vol at `0.003–0.005` every active row's equal-weight book recovers positive planted alpha (mean `≈ +2.6e-4` daily on gross `≈ 0.81`), while the null book recovers exactly zero and still earns a positive backtest Sharpe by chance (`≈ 0.64`) — the false positive P21 must kill. The one remaining unmeasured claim is whether **rank weighting** (opt-in Frazzini–Pedersen, currently untested empirically because the 9-asset P20 fixture flattens it) behaves like the equal book on a universe where its guards can actually clear. WP1 is the first consumer of WP0 and the prerequisite for WP2 (significance) and WP4 (verdict).

**Prioritization basis:** the repository name names a strategy, not a dataset. P20 closed with a report that honestly says rank mode is not empirically evaluable on its fixture and that its walk-forward OOS result is not evidence of profitability. WP0 removed the first limitation by generating a universe where rank mode can be active without touching `rank_min_leg_beta` or `rank_max_gross`. WP1 must now measure rank vs equal on that universe and publish per-book recovery, activity, and guard compliance. Until that exists, any statement about rank weighting is prose.

---

## ROUTE YOUR SESSION IN 60 SECONDS (no prose debate, no idle)

Deliverable files are the claim. Run:

```bash
git ls-files scripts/bab_rank_eval.py scripts/bab_significance.py scripts/bab_cost_surface.py docs/BAB_SIGNAL_OR_NOISE.md research_state/bab_p21
```

| First file missing from that list | Your WP | You own (create + commit) |
|---|---|---|
| `scripts/bab_rank_eval.py` | **P21 WP1** | `scripts/bab_rank_eval.py`, `research_state/bab_p21/rank_eval.{json,md}`, `tests/test_bab_p21_rank_eval.py` |
| `scripts/bab_significance.py` | P21 WP2 | `scripts/bab_significance.py`, `research_state/bab_p21/significance.{json,md}`, `tests/test_bab_p21_significance.py` |
| `scripts/bab_cost_surface.py` | P21 WP3 | `scripts/bab_cost_surface.py`, `research_state/bab_p21/cost_surface.{json,md}`, `tests/test_bab_p21_cost_surface.py` |
| `docs/BAB_SIGNAL_OR_NOISE.md` | **P21 WP4** | `docs/BAB_SIGNAL_OR_NOISE.md`, `tests/test_bab_p21_report_consistency.py` |

Rules:
1. Never take a WP whose deliverable script already exists (`git ls-files`, or on disk and passing its test). Commit an uncommitted WP first, verify it, then take the next missing one.
2. Solo default: **WP1**. Then WP2, WP3, WP4 in order — all consume WP0's committed artifact read-only and must not regenerate it.
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
4. Confirm the P21 WP0 artifact is intact and matches a fresh build (≈0.1 s, must print nothing and exit 0):
   ```bash
   python3 - <<'EOF'
   import json
   from scripts import bab_synthetic_universe as u
   fresh = json.dumps(u.build_universe(), indent=2, sort_keys=True) + "\n"
   committed = open("research_state/bab_p21/universe.json", encoding="utf-8").read()
   assert committed == fresh, "P21 universe.json drifted from its generator"
   print("P21 universe intact")
   EOF
   ```
5. Read `scripts/bab_synthetic_universe.py` (artifact style: pure `build_universe`, `build_returns_frame`, `render_markdown`, `write_artifacts`, `main`; 6-dp rounding; sha-pinned panels) and `tests/test_bab_p21_synthetic_universe.py` (the recovery-bar pattern you will extend). Then read `strategies/betting_against_beta/portfolio.py::construct_rank_weights` and `enforce_beta_neutrality` so you can state exactly which guards the rank book must respect.

---

## P21 WP0 — LANDED (do not redo, do not edit the artifact)

Committed files (14 tests, all passing):
- `scripts/bab_synthetic_universe.py`
- `research_state/bab_p21/universe.json` (1.0 MB, both panels + vectors + shas)
- `research_state/bab_p21/universe.md` (rendered from the JSON)
- `tests/test_bab_p21_synthetic_universe.py`

Certified facts at this HEAD:
- `41` assets `A001..A041` + `BTC` benchmark, `600` return rows, seed `20261118`, business-day index from `2024-01-02`.
- Betas `0.30 .. 2.70` evenly spaced; idiosyncratic vol `0.0030 .. 0.0050` evenly spaced; benchmark drift `0.0002` / vol `0.02`.
- Planted daily alpha `= (4.0 / 252) * (0.5 - u^2)` where `u = rank / 40`; null alpha `= 0` for every asset.
- Spearman(beta, planted alpha) is exactly `-1`; null alphas are all equal; betas, vols, benchmark draws and residual draws are shared row-for-row (the alpha vector is the only difference).
- Panel sha256: planted `aae2a70ebcf81b3a9e2dd5f314933c439194fef8a7be1da34930e2c271a93fda`, null `b7732c152564c87606a6a47eac39a543344cbcd4b8e974f4780be35671953b1b`.
- Strategy on this universe (`beta_window=90`, `min_obs=60`, `q=0.3/0.3`, `beta_neutral=True`): 541 active rows, gross `≈ 0.81`, `Σw = 0` to `2.6e-15`, `Σwβ` (true betas, BTC β=1) `≤ 0.0092`, mean active-row `Σwα = +2.6e-4` on planted and exactly `0` on null. 99.6% of planted rows are individually positive; the **mean-weight** book is the certified recovery statistic.
- Null backtest Sharpe is `≈ 0.64` on a zero-alpha universe — this is the calibrated false positive WP2 must explain, not a finding.

**WP0 artifact is read-only for all later WPs.** Editing `universe.json` without regenerating it breaks `test_committed_json_matches_fresh_build`; regenerating it after any WP1–WP3 result is published silently invalidates that result. If a universe parameter genuinely must change, bump the campaign and re-run every consumer.

---

## P21 WP1 — Rank vs equal evaluation (SPECIFICATION)

### A. Deliverable — `scripts/bab_rank_eval.py`

Pure functions only (`build_rank_eval`, `render_markdown`, `write_artifacts`, `main`), no network, no product-code edits, no universe regeneration.

1. **Load** `research_state/bab_p21/universe.json` read-only. Build the two frames with `scripts.bab_synthetic_universe.build_returns_frame(variant, payload)`. Record the panel sha256 each row consumed.
2. **Run four books**: `(variant, weighting) ∈ {planted, null} × {equal, rank}` with identical non-weighting config — `benchmark="BTC"`, `beta_window=90`, `min_observations=60`, `long_quantile=0.3`, `short_quantile=0.3`, `transaction_costs=0.0`, `universe=<41 assets>`, `beta_neutral=True`. Rank rows must use the shipped guard defaults (`rank_min_leg_beta=0.20`, `rank_max_gross=4.0`); never override them.
3. **Per book publish**: `variant`, `weighting`, `active_rows` (gross > 1e-12), `total_rows`, `gross_mean_active`, `gross_max`, `long_leg_beta_mean`, `short_leg_beta_mean`, `min_leg_beta`, `dollar_imbalance_max = max|Σw|`, `beta_exposure_max = max|Σwβ|` (true betas, BTC β=1), `recovery_mean = Σw̄α` where `w̄` is the mean active-row weight vector, `recovery_frac_positive` (active rows with `Σwα > 0`), and `panel_sha256`.
4. **Schema** `bab_p21.rank_eval/1`; provenance includes the universe seed, universe panel shas, config, `rank_min_leg_beta`, `rank_max_gross`, the recovery estimator definition, and the synthetic-only caveat. `rank_eval.md` is rendered from the same dict and contains no number absent from the JSON.

### B. Test — `tests/test_bab_p21_rank_eval.py`

Must prove, mechanically:
1. **Committed JSON equals a fresh build** (`json.dumps(..., indent=2, sort_keys=True) + "\n"`), and two builds serialize byte-identically.
2. **Activity:** on `planted`, both `equal` and `rank` have `active_rows > 0`. This is the central WP1 claim: rank mode is empirically evaluable on the WP0 universe. Never relax a guard to make it true.
3. **Guard compliance:** for every active row of every rank book, `min_leg_beta ≥ 0.20` (computed from true betas over the assets actually held on each leg) and `gross ≤ 4.0`. Assert `BABConfig().rank_min_leg_beta == 0.20` and `rank_max_gross == 4.0` so a silent default change fails the suite.
4. **Book neutrality:** every active row of both equal and rank books has `|Σw| < 1e-12` and `|Σwβ| < documented tolerance` (use the WP0 measured bound `0.0092`; a tolerance of `0.02` is acceptable, document why).
5. **Recovery:** on `planted`, `recovery_mean > 1e-5` for **both** books; on `null`, `|recovery_mean| < 1e-15` for both. More precisely: equal-planted and rank-planted are both strictly positive and rank/null and equal/null are both exactly zero.
6. **No drift:** `universe.json` sha256 is unchanged by the harness (re-read after `main()`), and no WP1 code path writes to `research_state/bab_p21/universe.*`.
7. **Markdown is JSON-derived:** every numeric token in `rank_eval.md` appears in `rank_eval.json`; the committed md equals `render_markdown(payload)`.
8. **Runtime** under 20 s; no network import.

### C. Scope boundaries
- Own **only** `scripts/bab_rank_eval.py`, `research_state/bab_p21/rank_eval.{json,md}`, `tests/test_bab_p21_rank_eval.py` (+ this `HANDOFF.md`).
- Do **not** edit product code, the P20 fixture/artifacts/report, the P21 universe artifact, or the rank guards. Do not create a second handoff doc.

### D. Commit rule
**One commit:** script + both artifacts + acceptance test + this `HANDOFF.md` + the ledger row. An artifact-only or script-only commit is a failed session. Never hand off mid-gate and never leave the tree red.

---

## P21 remaining WPs (consume WP0 read-only; do not regenerate it)

| WP | Deliverable script | Must prove |
|---|---|---|
| **WP2 — significance + deflation** | `scripts/bab_significance.py` + `significance.{json,md}` | Fixed-seed moving-block bootstrap of the OOS Sharpe (≥ 2000 resamples) on both variants; a deflated Sharpe correction for the 40-candidate P20 grid; **null calibration**: the false-positive rate on `null` must be ≤ the documented nominal slack, and the `planted` effect must be detected. Hand-computed DSR unit case pinned in the test. |
| **WP3 — multi-component cost surface** | `scripts/bab_cost_surface.py` + `cost_surface.{json,md}` | Linear cost + borrow/funding + notional slippage; per-row costed performance is non-increasing in each component; nulls/censoring are reported with documented reasons, never as zero tolerances; byte-identical reruns. |
| **WP4 — honest verdict report** | `docs/BAB_SIGNAL_OR_NOISE.md` + `tests/test_bab_p21_report_consistency.py` | **100%** of published table numbers match P21 JSON fields at 6 dp (zero unmatched), tables are byte-identical to JSON-only renderers, explicit signal-vs-noise verdict, explicit statement that planted-universe recovery is a **controlled synthetic** result and not market evidence, and no re-run of any harness. |

Rules that keep P21 honest: recovery on a **planted synthetic** universe proves the *estimator* works; it is never market alpha. A `null`-universe positive result is a **bug**, not a finding. If a stated acceptance criterion is measured false, replace it with a provable per-row invariant and record the removal under "Bottlenecks removed" — do not weaken the test to pass.

---

## Ground truth @ HEAD (certified)

- Default P20 book on the 9-asset fixture: `w90 q0.3, tc=0.001, beta_neutral=True`: wealth `0.705655`, Sharpe `-0.725483`, realized β `+0.058754`, model β `1.51e-04`.
- `tests/fixtures/real_market_prices.csv`: **399 price rows → 398 return rows**, 2021-01-04 → 2022-07-15, seed `20261028`, deliberate gap `2021-09-17`, all-NaN `DEL`, 9 assets + BTC. **Not real market data.**
- P20 sweep: 80 rows, selects **no winner**. P20 walk-forward: 5 folds × 40 OOS rows, mean OOS Sharpe `1.305563`, fraction positive `0.6` — **not** evidence of profitability.
- P20 break-even: 10 rows, three non-positive uncosted Sharpe, one censored at the `0.01` ceiling; `None` is never zero.
- P21 WP0 universe: see the landed section above. 41 assets, 600 rows, seed `20261118`, planted recovery `+2.6e-4` daily, null recovery exactly `0`, null backtest Sharpe `≈ 0.64`.
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
- `bash scripts/bab_quick.sh` ≈ 20 s. Full gate ≈ **140 s** with `BAB_GATE_MIN_COVERAGE=100`.
- Full-gate baseline at this HEAD: **6551 passed / 35 skipped / TOTAL 100% (6644/6644)**. It may only grow.
- `pytest --cov` in ad-hoc invocations can raise `ImportError: cannot load module more than once per process`; certify coverage with `scripts/bab_gate.sh`, never hand-rolled `--cov`.
- `scripts/` is an importable package (`scripts/__init__.py`) — tests import `from scripts import bab_breakeven` / `bab_synthetic_universe`.
- Python floor is `>=3.9`: no `zip(strict=True)`, no `match`, no `X | Y` runtime unions outside `from __future__ import annotations` files.

---

## Campaign P21 map — lanes, status, file ownership

One session owns exactly one WP for its turn. Two sessions must never take the same WP; **the committed deliverable files are the claim.**

| Lane | WPs in order | Owned files | Status |
|---|---|---|---|
| **A — Ground truth** | WP0 | `scripts/bab_synthetic_universe.py`, `research_state/bab_p21/universe.{json,md}`, `tests/test_bab_p21_synthetic_universe.py` | **DONE (14 tests)** |
| **B — Rank evaluation** | **WP1** | `scripts/bab_rank_eval.py`, `research_state/bab_p21/rank_eval.{json,md}`, `tests/test_bab_p21_rank_eval.py` | **UNBLOCKED — start here** |
| **C — Statistics** | WP2 | `scripts/bab_significance.py`, `research_state/bab_p21/significance.{json,md}`, `tests/test_bab_p21_significance.py` | blocked on WP1 (can be developed in parallel, must not regenerate WP0) |
| **D — Execution realism** | WP3 | `scripts/bab_cost_surface.py`, `research_state/bab_p21/cost_surface.{json,md}`, `tests/test_bab_p21_cost_surface.py` | blocked on WP0 only — may run after WP1 lands |
| **E — Reporting** | WP4 | `docs/BAB_SIGNAL_OR_NOISE.md`, `tests/test_bab_p21_report_consistency.py` | blocked on WP1–WP3 |

Rules: one WP per session; lanes B/C/D consume `universe.json` read-only and must never regenerate it; lane E reads JSON only and never re-runs a harness. P20 artifacts are frozen. Solo default: **WP1**.

---

## Campaign P21 done-check (all must hold)

1. `scripts/bab_synthetic_universe.py` exists; both variants are deterministic (hash-equal reruns), `≥41` assets, `≥600` rows; planted alpha/beta Spearman is exactly `-1`; the null variant differs only in alphas. **WP0 — DONE.**
2. Rank and equal books are both active on the planted universe and respect the leg-beta floor + gross cap; recovery exists on planted and vanishes on null; no guard relaxed. **WP1.**
3. Fixed-seed block bootstrap + deflated Sharpe; null false-positive rate within documented slack; planted effect detected. **WP2.**
4. Multi-component cost surface with honest censoring/null reasons and per-row monotonicity. **WP3.**
5. `docs/BAB_SIGNAL_OR_NOISE.md` exists; **100%** of published numbers machine-checked against P21 JSON; explicit signal-vs-noise verdict; planted recovery labelled synthetic. **WP4.**
6. All `tests/test_bab_p21_*.py` pass; no existing test deleted/skipped/`xfail`-ed/weakened; coverage **100%** (6551/35 may only grow). **Every WP re-certifies.**
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

**Hard minimums that make a WP impossible to fake:** WP1 `active_rows > 0` for equal and rank on planted, per-row guard compliance (`min_leg_beta ≥ 0.20`, `gross ≤ 4.0`), recovery on planted and exactly zero on null for both books; WP2 `≥2000` resamples, fixed seed, DSR hand case, null FPR bound; WP3 `≥3` cost components, per-row monotonicity, documented null reasons; WP4 `100%` of published numbers matched, zero unmatched, no harness re-run. If you are writing prose instead of a test, you are avoiding the work — stop and take the next routing row.

## No-idle ladder (if the assigned WP is blocked, do the next rung — never end a session empty-handed)

1. WP1 feels large? Land `build_rank_eval` returning the four-row dict plus a committed-JSON determinism test first; the rank/equal runs are two `BABStrategy` calls with `weighting=` swapped.
2. Blocked on guard compliance? Compute leg betas from the *true* universe betas over the assets actually held (`w != 0`), not from rolling estimates; the static bound is what the test must pin, and the rolling-imbalance bound is published separately.
3. Blocked because a rank row is flat? That is the P20 fixture trap, not a guard bug. Check that the WP0 universe is intact (mandatory action 4) and that you passed `universe=<41 assets>`; if the row is still flat, publish the documented reason and fix the *book selection inputs*, never `rank_min_leg_beta` / `rank_max_gross`.
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
- Editing `research_state/bab_p20/**`, `docs/BAB_RESEARCH_REPORT.md`, `research_state/bab_p21/universe.*`, or any P20 script (P20 is closed and frozen; edits break the WP4 consistency test).
- Weakening `rank_min_leg_beta` / `rank_max_gross` or the rank guard logic to make rank "active" on any fixture.
- Replacing the planted convex alpha curve with a linear one (`alpha = a + b·beta`): that makes a beta-neutral book's expected alpha identically zero.
- Selecting parameters on the evaluation window and reporting the result as OOS.
- Describing any synthetic universe as real market data, or publishing a Sharpe without the provenance caveat.
- Quoting P21 planted-universe recovery as market alpha, or treating a `null`-universe positive result as a finding instead of a bug.
- Deleting, skipping, `xfail`-ing, or loosening existing tests; special-casing fixture filenames in product code.
- Reopening P19 annotation/coverage work or P20 evidence work, re-attempting CI workflow edits, adding new `P19-7` markers, type-annotation/style churn, broad refactors, network fetching, committing probe/debug scratch scripts, or creating parallel handoff docs.

---

## Bottlenecks removed (do not re-create)

- **[REMOVED 2026-11-18T23:32:30Z] The WP0 planted-alpha spec as written was mathematically self-defeating.** Requiring alpha strictly decreasing in beta *and* calibrating it linearly makes `alpha = a + b·beta`; then for any dollar-neutral (`Σw=0`), beta-neutral (`Σwβ=0`) book, `Σwα = aΣw + bΣwβ = 0` exactly — the planted effect would be invisible to the estimator under test. Fixed by using a monotone but **convex** curve `alpha = A(0.5 - u²)` (Spearman still exactly `-1`), which leaves a measurable positive residual after beta neutralization. Do not "simplify" this to a line.
- **[REMOVED 2026-11-18T23:32:30Z] High idiosyncratic vol made the daily re-ranked book incoherent.** With idio vol `0.012` the beta estimate error (`≈0.06`) matched the beta spacing (`0.06`), so leg membership flipped daily and the mean-weight recovery was noise (`min Σwα` negative). Lowering idio vol to `0.003–0.005` makes every active planted row individually positive (`min ≈ +2.1e-5`), so the recovery assertion is provable row-wise rather than only in expectation.
- **[REMOVED 2026-11-18T23:32:30Z] "Rank has no test bed" survived WP0 as a prose claim.** WP0 now ships `41` assets with betas `0.30–2.70`, so leg betas clear the `0.20` floor by construction and the rank book can be active without touching a guard. WP1 is the measurement.
- **[REMOVED 2026-11-18T23:26:48Z] P20 had no next row, so the old routing table would route every session to "everything done" and invite an idle/docs-only turn.** The routing table now starts at P21 WP1 (WP0 landed) and each row has a committed-file claim.
- **[REMOVED 2026-11-18T23:26:48Z] A positive mean OOS Sharpe on a random walk looked like a result.** P20's aggregate (`mean_oos_sharpe 1.305563` on a pure synthetic random walk) is a false-positive demonstration. The P21 `null` universe reproduces the same illusion (`Sharpe ≈ 0.64` at zero true alpha); WP2 makes a significance/deflation verdict mandatory before any positive claim.
- **[REMOVED 2026-11-18T22:36:59Z] WP5's "cross-row monotonicity" acceptance criterion was mathematically false.** Cost drag is `tc * turnover`, so a higher uncosted Sharpe can break even sooner (measured: `(w60,q0.2)` `0.834694`/`0.004609` beats `(w90,q0.2)` `0.810267`/`0.005078`). Replaced with the provable per-row law: costed Sharpe is non-increasing in `tc`.
- **[REMOVED 2026-11-18T22:36:59Z] WP5's `[0, 0.01]` search range censors the best configuration.** `w180 q0.2` stays positive at `tc=0.01`; the harness reports a documented `None` (censored) instead of a meaningless bisection midpoint.
- **[REMOVED 2026-11-18T21:38:00Z] WP0 sat as "next" across four handoff refreshes.** Landed with 80 rows and hash-pinned artifacts.
- **[REMOVED 2026-11-18T21:18:00Z] WP choice was prose.** Artifact-based routing (`git ls-files`) decides the WP.
- **[PERMANENTLY EXTERNAL] P19-1 CI enforcement.** Agent tokens lack `workflows:write`; maintainer-only — never re-attempt, never list as a task.
- **[PERMANENTLY EXTERNAL] Real market data ingestion.** `api.exchange.coinbase.com` returns 403 from this environment; a licensed CSV is maintainer-supplied. Never a P21 task.

---

## Session ledger (append-only, concise)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-18T23:32:30Z | `bca90fb` + working tree | **P21 WP0 landed (heavy work, not a refresh).** Added `scripts/bab_synthetic_universe.py` (41 assets, 600 rows, seed `20261118`, planted/null variants, sha-pinned panels), `research_state/bab_p21/universe.{json,md}` (planted sha `aae2a70e…`), and `tests/test_bab_p21_synthetic_universe.py` (14 tests: determinism, committed==fresh, Spearman `-1`, variants differ only in alpha, neutrality, planted recovery `+2.6e-4` / null exactly `0`). Measured and removed the **affine-alpha trap** (a linear planted alpha is identically invisible to a beta-neutral book) and the **high-idio-vol instability** that made daily re-ranking noise dominate recovery. Re-routed to **WP1** as the only unblocked row. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6551 passed / 35 skipped / 100% (6644/6644)** (140.40 s) |
| 2026-11-18T23:26:48Z | `27eb92d` + working tree | **P20 WP4 landed — P20 CLOSED.** Added `docs/BAB_RESEARCH_REPORT.md` and `tests/test_bab_p20_report_consistency.py` (12 tests, 237/237 numeric cells matched). Opened P21 with WP0 as the binding next row. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6537 passed / 35 skipped / 100% (6644/6644)** (136.55 s) |
| 2026-11-18T22:36:59Z | `4ad98ee` + working tree | **WP5 landed.** `scripts/bab_breakeven.py` + `breakeven.{json,md}` + 16 tests. Removed two impossible spec criteria. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6525 passed / 35 skipped / 100% (6644/6644)** (136.64 s) |
| 2026-11-18T22:30:27Z | `5299dbb` | Handoff review + binding initial task message refresh. No code changes. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6509 passed / 35 skipped / 100% (6644/6644)** (138.92 s) |
| 2026-11-18T22:17:00Z | `7e83a95` + working tree | **WP3 landed.** `scripts/bab_walk_forward.py`, 5×40 expanding walk-forward, 10 tests. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6509 passed / 35 skipped / 100% (6644/6644)** (138.92 s) |
| 2026-11-18T21:38:00Z | `14a3935` + working tree | **WP0 landed.** `scripts/bab_research_sweep.py`, 80-row sweep, 10 tests. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6499 passed / 35 skipped / 100% (6644/6644)** (134.25 s) |
| 2026-11-18T21:28:21Z | 0452bd1 | Handoff re-certification (documentation only). Corrected stale git-state. | ruff PASS; quick GREEN; baseline `0.7057 -0.725 0.059` |
| 2026-11-18T21:18:00Z | 7637fba | Handoff refresh (documentation only). Artifact-based routing, de-collided WP5, JSON schemas for WP4. | ruff PASS; quick GREEN; full gate 6489/35/100% (129.4 s) |
| 2026-11-18T20:30:00Z | c565844 +1 | **WP2b landed.** Leg-beta floor + gross cap; rank fixture book 25 active / gross 51.09 → 0 active / gross 0.0. | ruff PASS; quick GREEN; full gate 6489/35/100% (129.8 s) |
| ≤2026-11-18T18:33:27Z | 33b84e2 | **WP1 landed.** Beta-neutral default, frozen-per-window hold, 17-test acceptance file, fidelity doc, README corrections, `--no-beta-neutral`. | 6462/35/100% after repair |
| ≤2026-11-18T14:19:40Z | f98eaa1 | **Opened P20.** Certified baseline; measured default-book beta −0.572 / −0.908. | GREEN 6445/35/100% |

---

## Proven closed (do not re-test, do not reopen)

P19-7 (222 broad/bare `except` handlers annotated, 0 unannotated), P19-2/3/4, P17-1/2, P18-1/2/3, kill-switch R4-B, bootstrap, reconciliation R5-B/R5-C, live-adapter two-key safety, 100% line coverage of `strategies/betting_against_beta`, Milestones 1–5 hygiene, **P20 WP0 (deterministic 80-row equal-weight sweep + hash-pinned artifacts + 10-test acceptance file)**, **P20 WP1 (beta-neutral default + frozen rebalance windows + fidelity doc + README correction)**, **P20 WP2 algebra (rank construction, exact 4-asset hand example, no-lookahead, equal-path byte-identity)**, **P20 WP2b (rank leg-beta floor + gross cap + wide-universe proof + fixture-flat scope)**, **P20 WP3 (walk-forward with train-only selection + anti-lookahead guards + 10-test acceptance file)**, **P20 WP5 (10-row break-even bisection, 6 fixed iterations, 16-test acceptance file, censoring and non-positive rows reported as documented nulls)**, **P20 WP4 (published report with 237/237 numbers machine-matched to committed JSON, JSON-only table renderers, rank discipline and null honesty enforced by 12 tests)**, **P21 WP0 (41-asset / 600-row planted+null universe, convex monotone alpha, sha-pinned panels, 14-test acceptance file, planted recovery `+2.6e-4`, null recovery exactly `0`)**. `scripts/bab_except_inventory.py` is retained as a read-only audit tool; running it is not a deliverable.
