# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-19T08:04:04Z
- **Git state:** `main` at `575601d` (clean tree); `d9175e3..575601d` landed P22 WP0 (`scripts/bab_p22_charter.py`, `tests/test_bab_p22_charter.py`, `research_state/bab_p22/charter.{json,md}`, `docs/BAB_P22_KICKOFF.md`, 10 tests). P21 WP0–WP4 all committed with passing acceptance suites. Certify with `git log --oneline -4 && git status --short`.
- **P21 WP4 IS LANDED WITH 13 NEW PASSING TESTS.** `docs/BAB_SIGNAL_OR_NOISE.md` + `tests/test_bab_p21_report_consistency.py`. Explicit verdict: SIGNAL on planted (recovery +2.6e-4 equal / +1.7e-2 rank, p=0.0000 both), NOISE on null (p 0.1635/0.2680 >= 0.05, not significant), costed Sharpe non-increasing in all three components for all four books, every table number machine-checked against committed P21 JSON at 6 dp with zero unmatched cells, planted recovery labelled controlled synthetic and not market evidence, NO-GO for market deployment. P21 is CLOSED — do not reopen WP0–WP4.
- **P21 WP3 IS LANDED WITH 18 NEW PASSING TESTS.** `scripts/bab_cost_surface.py`, `research_state/bab_p21/cost_surface.{json,md}`, `tests/test_bab_p21_cost_surface.py`. Three cost components (linear transaction cost, borrow/funding, notional slippage), zero-cost baseline, per-book **and** per-period non-increasing costed Sharpe for all four books, total-cost linearity, documented censoring (`surfaces=None`, never a zero tolerance), byte-identical reruns. The renderer bug that emitted one character per line is fixed and pinned by `test_committed_markdown_matches_renderer`.
- **P21 WP2 IS LANDED WITH 12 NEW PASSING TESTS.** `scripts/bab_significance.py`, `research_state/bab_p21/significance.{json,md}`, `tests/test_bab_p21_significance.py`. Null calibrated (`p_value` 0.1635/0.2680 >= 0.05, not significant), planted detected (`p_value` 0.0000, CI excludes zero), deflated Sharpe computed for the 40-candidate P20 grid (hand-computed DSR unit case pinned: 0.948765).
- **P21 WP1 IS LANDED WITH 12 NEW PASSING TESTS.** `scripts/bab_rank_eval.py`, `research_state/bab_p21/rank_eval.{json,md}`, `tests/test_bab_p21_rank_eval.py`. Do not reopen WP1.
- **P20 IS COMPLETE AND CERTIFIED. Do not reopen it.** `research_state/bab_p20/**` and `docs/BAB_RESEARCH_REPORT.md` are frozen: the WP4 test re-renders those tables from JSON and fails on any drift.
- **P21 WP0 IS LANDED AND FROZEN.** `scripts/bab_synthetic_universe.py`, `research_state/bab_p21/universe.{json,md}`, `tests/test_bab_p21_synthetic_universe.py`. Do not edit or regenerate `universe.*`.
- **Full gate at this HEAD: P21 69 tests pass; quick gate GREEN (195 passed); P22 WP0 landed — full gate GREEN 6616 passed / 35 skipped / 100% (6644/6644). P22 WP0 is COMPLETE (charter script + test + charter.json/md + BAB_P22_KICKOFF.md). The binding row advances to P22 WP1 — null battery (>=20 seeds).
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral BAB trading system.

**Handoff reviewed and confirmed as the single durable handoff. The binding initial task message below is the most relevant, timestamped, clear directive for the next agentic work session, prioritized from the repository name (`Crypto-Betting-Against-Beta`) and the measured state at HEAD `575601d`. P21 is CLOSED (WP0 universe, WP1 rank vs equal, WP2 significance/deflation, WP3 cost surface, WP4 verdict all landed and committed). Campaign P21 answered "is the estimator calibrated and cost-aware on a controlled universe?" — yes, with an honest NO-GO for market. The next campaign is P22 "Decision-grade validation" and its binding row is now **P22 WP1 — null battery (>=20 seeds)** (P22 WP0 charter landed at `575601d`). Bottlenecks that stalled or mis-routed sessions are removed below; Campaign P22 is pre-declared with artifact-gated rows so no session can end idle.**

---

# INITIAL TASK MESSAGE (BINDING — START HERE)

**Timestamp:** 2026-11-19T08:04:04Z · **Campaign:** P22 "Decision-grade validation" · **Lane:** F · **WP:** **P22 WP1 — null battery (>=20 seeds)**

**One-sentence objective:** write `scripts/bab_null_battery.py`, `research_state/bab_p22/null_battery.{json,md}` and `tests/test_bab_p22_null_battery.py` that run the P22 null battery over the 20 chartered seeds (20261120..20261139), consume the P21 committed artifacts and charter constants read-only, restate per-seed null outcomes and aggregate null calibration, assert committed JSON equals a fresh build, derive markdown from JSON only, and never re-run or edit any P21 harness.

**Why this and nothing else:** P21 WP0–WP4 are landed, committed and frozen. The repository name names a strategy, not a dataset, and P21 deliberately cannot answer "would this survive repeated null universes, nonlinear impact, or capacity?" — that is Campaign P22. P22 is deliberately offline and heavy; every WP is artifact-gated, so a session that only writes prose fails the routing table. WP0 is the only P22 row that may be taken now (P21 WP4 has landed, unblocking P22). Until the charter lands, P22 cannot start and no future session can reproduce the P21 verdict basis or run the ≥20-seed null battery.

**Prioritization basis:** the repository name names a strategy, not a dataset. P21 closed honestly (P20: no winner, OOS not profitability; P21 WP1: rank recovers more planted alpha; WP2: null calibrated, planted detected; WP3: costs cannot manufacture the effect; WP4: verdict stated and test-enforced with NO-GO for market). The one thing missing before P22 can run is the machine-readable charter that restates the P21 verdict from committed JSON and pins the P22 seeds/thresholds. Without it, P22 WP1–WP4 have no acceptance criteria to consume.

**Deliverable files are the claim.** Run:

```bash
git ls-files scripts/bab_p22_charter.py tests/test_bab_p22_charter.py docs/BAB_P22_KICKOFF.md research_state/bab_p22
```

| First file missing from that list | Your WP | You own (create + commit) |
|---|---|---|
| `scripts/bab_p22_charter.py` | **P22 WP0** | `scripts/bab_p22_charter.py`, `research_state/bab_p22/charter.{json,md}`, `docs/BAB_P22_KICKOFF.md`, `tests/test_bab_p22_charter.py` |
| `scripts/bab_null_battery.py` | **P22 WP1** | `scripts/bab_null_battery.py`, `research_state/bab_p22/null_battery.{json,md}`, `tests/test_bab_p22_null_battery.py` |
| `scripts/bab_impact_surface.py` | **P22 WP2** | `scripts/bab_impact_surface.py`, `research_state/bab_p22/impact_surface.{json,md}`, `tests/test_bab_p22_impact_surface.py` |
| `scripts/bab_capacity.py` | **P22 WP3** | `scripts/bab_capacity.py`, `research_state/bab_p22/capacity.{json,md}`, `tests/test_bab_p22_capacity.py` |
| `docs/BAB_P22_DECISION.md` | **P22 WP4** | `docs/BAB_P22_DECISION.md`, `tests/test_bab_p22_decision_consistency.py` |

Rules:
1. Never take a WP whose deliverable script already exists (`git ls-files`, or on disk and passing its test). Commit an uncommitted WP first, verify it, then take the next missing one.
2. Solo default: **P22 WP0**. It reads the committed P21 JSON only; it must not regenerate, re-run or edit any P21 harness output.
3. A partially finished WP is not locked. If files exist only in the working tree (not `git ls-files`) or the gate is red, you own finishing it.
4. Everything blocked? Repair the red gate first (`bash scripts/bab_quick.sh`), then take the first missing row.
5. Never end a session with prose. A landed WP = deliverable + artifact + acceptance test in **one** commit + green full gate.
6. **A documentation-only session is a failed session.** A handoff refresh must also land the next missing WP (or a tested slice) in the same turn — then update this file with what landed.

---

## ROUTE YOUR SESSION IN 60 SECONDS (no prose debate, no idle)

Deliverable files are the claim. Run:

```bash
git ls-files scripts/bab_p22_charter.py tests/test_bab_p22_charter.py docs/BAB_P22_KICKOFF.md research_state/bab_p22/charter.json scripts/bab_null_battery.py research_state/bab_p22/null_battery.json
```

| First file missing from that list | Your WP | You own (create + commit) |
|---|---|---|
| `scripts/bab_p22_charter.py` | **P22 WP0** | `scripts/bab_p22_charter.py`, `research_state/bab_p22/charter.{json,md}`, `docs/BAB_P22_KICKOFF.md`, `tests/test_bab_p22_charter.py` |
| `scripts/bab_null_battery.py` | **P22 WP1** | `scripts/bab_null_battery.py`, `research_state/bab_p22/null_battery.{json,md}`, `tests/test_bab_p22_null_battery.py` |
| `scripts/bab_impact_surface.py` | **P22 WP2** | `scripts/bab_impact_surface.py`, `research_state/bab_p22/impact_surface.{json,md}`, `tests/test_bab_p22_impact_surface.py` |
| `scripts/bab_capacity.py` | **P22 WP3** | `scripts/bab_capacity.py`, `research_state/bab_p22/capacity.{json,md}`, `tests/test_bab_p22_capacity.py` |
| `docs/BAB_P22_DECISION.md` | **P22 WP4** | `docs/BAB_P22_DECISION.md`, `tests/test_bab_p22_decision_consistency.py` |

Rules:
1. Never take a WP whose deliverable script already exists (`git ls-files`, or on disk and passing its test). Commit an uncommitted WP first, verify it, then take the next missing one.
2. Solo default: **P22 WP0**, then Campaign P22 WP1. WP0 reads committed P21 JSON only and never re-runs a harness.
3. A partially finished WP is not locked. If files exist only in the working tree (not `git ls-files`) or the gate is red, you own finishing it.
4. Everything blocked? Repair the red gate first (`bash scripts/bab_quick.sh`), then take the first missing row.
5. Never end a session with prose. A landed WP = deliverable + artifact + acceptance test in **one** commit + green full gate.
6. **A documentation-only session is a failed session.** If a user asks for a handoff refresh, you must also land the next missing WP (or a tested slice) in the same turn — then update this file with what landed.

---

## MANDATORY FIRST ACTIONS (in order, ~4 minutes)

1. `git log --oneline -4 && git status --short` — locate yourself. Do not re-derive what this file certifies.
2. `bash scripts/bab_quick.sh` (≈20 s, must be GREEN). It bootstraps numpy/pandas/scipy/pytest/ruff from PyPI.
3. Confirm P21 is closed and WP4 artifacts are intact (≈0.1 s, must print nothing and exit 0):
   ```bash
   python3 - <<'EOF'
   import json
   from pathlib import Path
   root = Path(".")
   for name in ("universe", "significance", "rank_eval", "cost_surface"):
       p = root / f"research_state/bab_p21/{name}.json"
       assert p.is_file(), f"missing {p}"
       json.loads(p.read_text(encoding="utf-8"))
   report = root / "docs/BAB_SIGNAL_OR_NOISE.md"
   assert report.is_file(), "missing P21 verdict report"
   print("P21 closed; WP4 artifacts intact")
   EOF
   ```
4. Read `scripts/bab_cost_surface.py` and `tests/test_bab_p21_cost_surface.py` — that pair is the artifact style P22 WP0 must follow: pure `build_*` / `render_markdown` / `write_artifacts`, 6-dp rounding, committed-artifact identity, JSON-derived markdown, and a documented-reason path for every null. Then read `significance.json`, `rank_eval.json`, `universe.json` and `cost_surface.json` end to end; every number the P22 charter restates must already be a field in one of them.
5. Read `docs/BAB_SIGNAL_OR_NOISE.md` — the P21 verdict the charter must restate (signal on planted, noise on null, NO-GO for market, every table JSON-derived).

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

## P21 WP1 — Rank vs equal evaluation (LANDED)

Committed files (12 tests, all passing):
- `scripts/bab_rank_eval.py`
- `research_state/bab_p21/rank_eval.json`
- `research_state/bab_p21/rank_eval.md`
- `tests/test_bab_p21_rank_eval.py`

Certified facts at this HEAD:
- Four books measured on the committed WP0 universe (read-only): `(planted, null) x (equal, rank)`, identical config `benchmark=BTC, beta_window=90, min_obs=60, q=0.3/0.3, tc=0.0, beta_neutral=True`, rank guards `rank_min_leg_beta=0.20`, `rank_max_gross=4.0` never overridden.
- `541` active rows for **all four books** (planted equal, planted rank, null equal, null rank). Rank mode is empirically active — not flattened — on the WP0 41-asset universe.
- `gross_mean_active ≈ 0.814` for both equal books; `≈ 2.369` for both rank books (rank weights concentrate on extreme-beta legs).
- `min_leg_beta ≥ 0.507` for rank books (above the `0.20` floor); `gross_max ≤ 2.369` (below the `4.0` cap). Guards respected, never relaxed.
- `dollar_imbalance_max < 1e-12` for equal books (dollar-neutral). Rank books are **beta-neutral but not dollar-neutral** (README §5): long leg sums to `1/beta_L`, short leg to `-1/beta_H`, which differ unless `beta_L == beta_H`. Dollar-neutrality asserted only for equal; beta-neutrality asserted for both.
- `beta_exposure_max < 0.05` for all four books (true betas, BTC β=1). The `0.05` bound (not `0.02`) reflects that rank-mode neutrality is constructed against rolling/estimated betas, so true-beta exposure carries estimation error; `0.05` is still a tight beta-neutrality bound.
- `recovery_mean` on planted: equal `+2.6e-4`, rank `+1.7e-2` — both strictly positive, both above `1e-5`. Rank overweighting extreme-beta legs recovers more planted alpha.
- `recovery_mean` on null: exactly `0.0` for both books. `recovery_frac_positive = 0` on null.
- Schema `bab_p21.rank_eval/1`; provenance includes universe seed, panel shas, config, guard defaults, recovery estimator definition, synthetic-only caveat. `rank_eval.md` rendered from JSON; no number absent from JSON.
- Runtime `≈ 0.2 s`; no network import; `universe.json` byte-identical before and after `main()`.

**WP1 artifact is read-only for WP2–WP4.** Do not edit `rank_eval.{json,md}` or `bab_rank_eval.py` after landing; regenerating invalidates WP1 results.

---

## P21 WP3 — Multi-component cost surface (LANDED)

Committed files (18 tests, all passing):
- `scripts/bab_cost_surface.py`
- `research_state/bab_p21/cost_surface.json`
- `research_state/bab_p21/cost_surface.md`
- `tests/test_bab_p21_cost_surface.py`

Certified facts at this HEAD:
- Four books measured on the committed WP0 universe (read-only): `(planted, null) x (equal, rank)`, identical zero-cost config (`benchmark=BTC, beta_window=90, min_obs=60, q=0.3/0.3, tc=0.0, slippage=0.0, beta_neutral=True`), rank guards `rank_min_leg_beta=0.20`, `rank_max_gross=4.0` never overridden. WP1 `rank_eval.json` is read-only and sha-cross-checked.
- Three cost components, each with a `0.0` baseline and an ascending grid: `linear_transaction_cost` `[0, 0.00025, 0.0005, 0.001, 0.002, 0.005, 0.01]`, `borrow_funding` `[0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]`, `notional_slippage` `[0, 0.00005, 0.0001, 0.00025, 0.0005, 0.001, 0.002]`.
- Gross Sharpe: planted/equal `7.034781`, planted/rank `44.378201`, null/equal `0.639801`, null/rank `0.649924`. All four books have `541/600` active rows and are uncensored.
- Per-book **and** per-period costed Sharpe is non-increasing in every component level for all four books (`monotonicity` and `period_wise_non_increasing` all `true`). Cost drag and total cost are non-decreasing; final cumulative wealth is non-increasing; `level=0` reproduces the gross book exactly; total cost is linear in the level.
- Censoring is a real code path, not prose: the acceptance test monkeypatches a zero book and asserts `censored=True`, `surfaces=None`, and a non-empty documented `inactive_book: ...` reason. A censored book never carries a zero tolerance.
- Runtime `≈ 0.2 s`; no network import; `universe.json` and `rank_eval.json` byte-identical before and after `main()`.
- `render_markdown` is pinned to the committed markdown. The pre-landing renderer called `lines.extend(<string>)` and emitted one character per line; it now emits one table row per line and the test fails on any regression.

**WP3 artifact is read-only for WP4.** Do not edit `cost_surface.{json,md}` or `bab_cost_surface.py` after landing; WP4 must read these numbers, not recompute them.

---

## P21 remaining WPs (consume WP0–WP3 read-only; do not regenerate them)

| WP | Deliverable script | Must prove |
|---|---|---|
| **WP2 — significance + deflation** | `scripts/bab_significance.py` + `significance.{json,md}` | **DONE.** Fixed-seed moving-block bootstrap of the OOS Sharpe (≥ 2000 resamples) on both variants; a deflated Sharpe correction for the 40-candidate P20 grid; **null calibration** (null `p_value` 0.1635/0.2680 >= 0.05, not significant) and the `planted` effect detected (planted `p_value` 0.0000, CI excludes zero). Hand-computed DSR unit case pinned in the test. |
| **WP3 — multi-component cost surface** | `scripts/bab_cost_surface.py` + `cost_surface.{json,md}` | **DONE (18 tests).** Linear cost + borrow/funding + notional slippage; per-book and per-period costed performance non-increasing in every component; total-cost linearity; censoring reported with documented reasons (never zero tolerances); byte-identical reruns. |
| **WP4 — honest verdict report** | `docs/BAB_SIGNAL_OR_NOISE.md` + `tests/test_bab_p21_report_consistency.py` | **100%** of published table numbers match P21 JSON fields at 6 dp (zero unmatched), tables are byte-identical to JSON-only renderers, explicit signal-vs-noise verdict, explicit statement that planted-universe recovery is a **controlled synthetic** result and not market evidence, and no re-run of any harness. **Unblocked — start here.** |

Rules that keep P21 honest: recovery on a **planted synthetic** universe proves the *estimator* works; it is never market alpha. A `null`-universe positive result is a **bug**, not a finding. If a stated acceptance criterion is measured false, replace it with a provable per-row invariant and record the removal under "Bottlenecks removed" — do not weaken the test to pass.

---

## Ground truth @ HEAD (certified)

- Default P20 book on the 9-asset fixture: `w90 q0.3, tc=0.001, beta_neutral=True`: wealth `0.705655`, Sharpe `-0.725483`, realized β `+0.058754`, model β `1.51e-04`.
- `tests/fixtures/real_market_prices.csv`: **399 price rows → 398 return rows**, 2021-01-04 → 2022-07-15, seed `20261028`, deliberate gap `2021-09-17`, all-NaN `DEL`, 9 assets + BTC. **Not real market data.**
- P20 sweep: 80 rows, selects **no winner**. P20 walk-forward: 5 folds × 40 OOS rows, mean OOS Sharpe `1.305563`, fraction positive `0.6` — **not** evidence of profitability.
- P20 break-even: 10 rows, three non-positive uncosted Sharpe, one censored at the `0.01` ceiling; `None` is never zero.
- P21 WP0 universe: see the landed section above. 41 assets, 600 rows, seed `20261118`, planted recovery `+2.6e-4` daily, null recovery exactly `0`, null backtest Sharpe `≈ 0.64`.
- P21 WP3 cost surface: gross Sharpe planted `7.034781` / `44.378201` (equal/rank), null `0.639801` / `0.649924`; 541/600 active rows for all four books; every component monotone per book and per period; censoring path tested with a documented reason.
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
- Full-gate baseline at this HEAD: **6593 passed / 35 skipped / TOTAL 100% (6644/6644)**. It may only grow.
- `pytest --cov` in ad-hoc invocations can raise `ImportError: cannot load module more than once per process`; certify coverage with `scripts/bab_gate.sh`, never hand-rolled `--cov`.
- `scripts/` is an importable package (`scripts/__init__.py`) — tests import `from scripts import bab_breakeven` / `bab_synthetic_universe`.
- Python floor is `>=3.9`: no `zip(strict=True)`, no `match`, no `X | Y` runtime unions outside `from __future__ import annotations` files.

---

## Campaign P21 map — lanes, status, file ownership

One session owns exactly one WP for its turn. Two sessions must never take the same WP; **the committed deliverable files are the claim.**

| Lane | WPs in order | Owned files | Status |
|---|---|---|---|
| **A — Ground truth** | WP0 | `scripts/bab_synthetic_universe.py`, `research_state/bab_p21/universe.{json,md}`, `tests/test_bab_p21_synthetic_universe.py` | **DONE (14 tests)** |
| **B — Rank evaluation** | **WP1** | `scripts/bab_rank_eval.py`, `research_state/bab_p21/rank_eval.{json,md}`, `tests/test_bab_p21_rank_eval.py` | **DONE (12 tests)** |
| **C — Statistics** | **WP2** | `scripts/bab_significance.py`, `research_state/bab_p21/significance.{json,md}`, `tests/test_bab_p21_significance.py` | **DONE (12 tests)** |
| **D — Execution realism** | **WP3** | `scripts/bab_cost_surface.py`, `research_state/bab_p21/cost_surface.{json,md}`, `tests/test_bab_p21_cost_surface.py` | **DONE (18 tests)** |
| **E — Reporting** | WP4 | `docs/BAB_SIGNAL_OR_NOISE.md`, `tests/test_bab_p21_report_consistency.py` | **DONE (13 tests)** |

Rules: one WP per session; lanes B/C/D consume `universe.json` read-only and must never regenerate it; lane E reads JSON only and never re-runs a harness. P20 artifacts are frozen. **P21 is CLOSED (WP0–WP4 all DONE). Solo default: P22 WP0.**

---

## Campaign P21 done-check (all must hold)

1. `scripts/bab_synthetic_universe.py` exists; both variants are deterministic (hash-equal reruns), `≥41` assets, `≥600` rows; planted alpha/beta Spearman is exactly `-1`; the null variant differs only in alphas. **WP0 — DONE.**
2. Rank and equal books are both active on the planted universe (541 rows each) and respect the leg-beta floor + gross cap; recovery exists on planted and vanishes on null; no guard relaxed. **WP1 — DONE.**
3. Fixed-seed block bootstrap + deflated Sharpe; null false-positive rate within documented slack; planted effect detected. **WP2 — DONE.**
4. Multi-component cost surface with honest censoring/null reasons and per-book plus per-period monotonicity. **WP3 — DONE (18 tests).**
5. `docs/BAB_SIGNAL_OR_NOISE.md` exists; **100%** of published numbers machine-checked against P21 JSON; explicit signal-vs-noise verdict; planted recovery labelled synthetic; NO-GO for market. **WP4 — DONE (13 tests).**
6. All `tests/test_bab_p21_*.py` pass (69 tests); no existing test deleted/skipped/`xfail`-ed/weakened; coverage **100%** (P21 69/69; full gate re-certified after P22 WP0 lands). **Every WP re-certifies.**
7. Full gate green: ruff PASS, reconcile GREEN, `bab_gate.sh` `BAB_GATE_MIN_COVERAGE=100` GREEN, 0 missed. **Every WP re-certifies.**

**Scoreboard command (run before declaring P21 done):**
```bash
git ls-files scripts/bab_synthetic_universe.py scripts/bab_rank_eval.py scripts/bab_significance.py scripts/bab_cost_surface.py docs/BAB_SIGNAL_OR_NOISE.md tests/test_bab_p21_report_consistency.py research_state/bab_p21
python3 -m pytest -q tests/test_bab_p21_*.py
```

---

## Campaign P22 — Decision-grade validation (pre-declared; do not idle after P21)

P21 answers "is the estimator calibrated and cost-aware on a controlled universe?". It cannot answer "would this survive repeated null universes, nonlinear impact, or capacity?". P22 is deliberately offline and heavy; every WP is artifact-gated, so a session that only writes prose fails the routing table. **Never claim P22 is market evidence: no licensed real-market CSV exists in this environment (permanently external).**

| WP | Deliverable | Must prove (hard minimums) |
|---|---|---|
| **P22 WP0 — charter** | `scripts/bab_p22_charter.py`, `research_state/bab_p22/charter.json`, `docs/BAB_P22_KICKOFF.md`, `tests/test_bab_p22_charter.py` | Machine-readable charter that restates the P21 verdict from committed JSON (no hand-typed numbers), pins the P22 null-battery seed list (≥20 seeds), nominal slack, and the exact acceptance thresholds consumed by WP1–WP4; committed JSON == fresh build; markdown/charter numbers derived from JSON. |
| **P22 WP1 — null battery** | `scripts/bab_null_battery.py`, `research_state/bab_p22/null_battery.{json,md}`, `tests/test_bab_p22_null_battery.py` | Runs the planted/null universe over **≥20 independent seeds** from the WP0 charter; null recovery is exactly `0` for every seed (a non-zero null is a bug); empirical false-positive rate is computed as `#significant/null seeds / n` and published even when it exceeds slack; planted recovery is strictly positive on the documented fraction; byte-identical reruns. |
| **P22 WP2 — nonlinear impact** | `scripts/bab_impact_surface.py`, `research_state/bab_p22/impact_surface.{json,md}`, `tests/test_bab_p22_impact_surface.py` | Square-root market-impact model (drag ∝ participation^1.5) layered on the committed WP3 exposure series; `coefficient=0` reproduces the linear baseline exactly; per-book and per-period costed Sharpe is non-increasing in the impact coefficient; censoring is a documented reason, never a zero tolerance; byte-identical reruns. |
| **P22 WP3 — capacity / break-even** | `scripts/bab_capacity.py`, `research_state/bab_p22/capacity.{json,md}`, `tests/test_bab_p22_capacity.py` | Per-book participation-rate break-even via fixed-iteration bisection; each bracket provably halves every iteration; non-crossing cases are censored with a documented reason, never a midpoint; per-row zero-crossing sign test pinned. |
| **P22 WP4 — decision report** | `docs/BAB_P22_DECISION.md`, `tests/test_bab_p22_decision_consistency.py` | Explicit GO/NO-GO with **NO-GO on synthetic-only evidence** stated as the required verdict until a maintainer supplies licensed data; **100%** of published numbers machine-matched to P22 JSON at 6 dp (zero unmatched); tables rendered from JSON only; no harness re-run; no P21 artifact edited. |

P22 rules: one WP per session; **P21 WP4 has landed, so P22 WP0 is the binding row** and is the only row a session may take now; every later row consumes earlier P22 JSON read-only and must not regenerate it. If a measured acceptance criterion is false, publish the false result with a documented reason and keep the invariant that is provable; never weaken a test to pass. Add `research_state/bab_p22/**` to the freeze list once each artifact lands.

---

## Work quantum — the minimum a session must produce (anti-shallow-work)

A session is **not** complete unless **all** of the following landed in one commit:

1. One complete WP from the routing table (or one tested slice of it with the exact remainder written in the ledger).
2. Its **script + committed artifact + acceptance test** (WP4: report + consistency test).
3. A hash-determinism assertion, not a "looks stable" claim.
4. `python3 -m ruff check .` PASS and `bash scripts/bab_quick.sh` GREEN; full gate once per WP boundary.
5. A ledger row below with UTC timestamp, HEAD, what landed, and the gate line.
6. **No documentation-only turn.** A handoff refresh must also land the next missing WP or a tested slice of it.

**Hard minimums that make a WP impossible to fake:** WP1 `active_rows > 0` for equal and rank on planted, per-row guard compliance (`min_leg_beta ≥ 0.20`, `gross ≤ 4.0`), recovery on planted and exactly zero on null for both books; WP2 `≥2000` resamples, fixed seed, DSR hand case, null FPR bound; WP3 `≥3` cost components, per-book and per-period monotonicity, documented null reasons; WP4 `100%` of published numbers matched, zero unmatched, no harness re-run, and a one-line GO/NO-GO verdict whose basis is a machine-checked field; **P22 WP0 charter** restates the P21 verdict from committed JSON only (no hand-typed numbers), pins ≥20 null-battery seeds, nominal slack and the exact WP1–WP4 acceptance thresholds, committed JSON == fresh build, markdown derived from JSON. If you are writing prose instead of a test, you are avoiding the work — stop and take the next routing row.

## No-idle ladder (if the assigned WP is blocked, do the next rung — never end a session empty-handed)

1. P22 WP0 charter feels large? Land the JSON-only table renderers first (one function per table, taking the committed P21 payload and returning markdown) with a test that the rendered table equals the report table byte-for-byte; then add the narrative verdict. The narrative may not contain a number that is not already a rendered cell.
2. Blocked because a P21 JSON field you want to restate does not exist? Do not compute it in prose. Either publish only existing fields, or land a new upstream WP in the same commit that adds the field to the harness plus its acceptance test — never a hand-typed number.
3. Blocked because the charter looks "too positive"? That is the P21 verdict you must restate explicitly: signal on planted, noise on null, NO-GO for market. Publish the null/calibration evidence next to it.
4. Blocked on P22 WP0? Take the P21 done-check: re-certify `git ls-files ... research_state/bab_p21` + `pytest -q tests/test_bab_p21_*.py` (69 tests) and confirm the gate is green; the charter is unblocked and artifact-gated.
5. Blocked on everything? Repair the gate and add one missing test in a P21 or P22 test file. Something landable always exists.

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
- Editing `research_state/bab_p20/**`, `docs/BAB_RESEARCH_REPORT.md`, `research_state/bab_p21/universe.*`, or any P20 script (P20 is closed and frozen; edits break the WP4 consistency test). Once a P22 artifact lands, edit only via its generator and its acceptance test.
- Hand-typing any number into a P21/P22 report, charter, or verdict that is not a committed JSON field. A report row that no JSON field backs is a failed session.
- Weakening `rank_min_leg_beta` / `rank_max_gross` or the rank guard logic to make rank "active" on any fixture.
- Replacing the planted convex alpha curve with a linear one (`alpha = a + b·beta`): that makes a beta-neutral book's expected alpha identically zero.
- Selecting parameters on the evaluation window and reporting the result as OOS.
- Describing any synthetic universe as real market data, or publishing a Sharpe without the provenance caveat.
- Quoting P21 planted-universe recovery as market alpha, or treating a `null`-universe positive result as a finding instead of a bug.
- Deleting, skipping, `xfail`-ing, or loosening existing tests; special-casing fixture filenames in product code.
- Reopening P19 annotation/coverage work or P20 evidence work, re-attempting CI workflow edits, adding new `P19-7` markers, type-annotation/style churn, broad refactors, network fetching, committing probe/debug scratch scripts, or creating parallel handoff docs.

---

## Bottlenecks removed (do not re-create)

- **[REMOVED 2026-11-19T02:44:44Z] P21 WP3 had shipped its script and artifacts with no acceptance test, so it was claimable but unfalsifiable.** `scripts/bab_cost_surface.py` and `research_state/bab_p21/cost_surface.{json,md}` were tracked, but `tests/test_bab_p21_cost_surface.py` did not exist. Landed 18 tests (fresh-build identity, markdown identity, hash determinism, read-only inputs, three components with zero baseline, per-book and per-period monotonicity, cost linearity, exposure non-negativity, documented censoring). A WP without its acceptance test is an unfinished WP — routing rule 3 now says so explicitly.
- **[REMOVED 2026-11-19T02:44:44Z] The WP3 markdown renderer emitted one character per line.** `render_markdown` called `lines.extend(<formatted string>)`, which iterates the string instead of appending the row; a fresh render did not match the committed markdown even though the JSON did. Fixed to a single-element `extend` and pinned by `test_committed_markdown_matches_renderer`. If a renderer and its artifact disagree, fix the renderer, never the artifact text.
- **[REMOVED 2026-11-19T02:44:44Z] The handoff's git state was stale and self-contradictory.** It claimed WP2 "awaits a commit" and listed a 6563/6575 gate baseline while the tree already contained WP3 artifacts. Certified HEAD `8591247`, one baseline **6593 passed / 35 skipped / 100% (6644/6644)**, and artifact-based routing that starts at WP4.
- **[REMOVED 2026-11-19T02:44:44Z] P21 ended with no declared next campaign, which would have routed the post-WP4 session to "everything done" and invited an idle/docs-only turn.** Campaign P22 (charter, ≥20-seed null battery, nonlinear impact, capacity break-even, decision report) is pre-declared with artifact-gated rows and hard minimums, so no session can end without heavy work.
- **[REMOVED 2026-11-18T23:32:30Z] The WP0 planted-alpha spec as written was mathematically self-defeating.** Requiring alpha strictly decreasing in beta *and* calibrating it linearly makes `alpha = a + b·beta`; then for any dollar-neutral (`Σw=0`), beta-neutral (`Σwβ=0`) book, `Σwα = aΣw + bΣwβ = 0` exactly — the planted effect would be invisible to the estimator under test. Fixed by using a monotone but **convex** curve `alpha = A(0.5 - u²)` (Spearman still exactly `-1`), which leaves a measurable positive residual after beta neutralization. Do not "simplify" this to a line.
- **[REMOVED 2026-11-18T23:32:30Z] High idiosyncratic vol made the daily re-ranked book incoherent.** With idio vol `0.012` the beta estimate error (`≈0.06`) matched the beta spacing (`0.06`), so leg membership flipped daily and the mean-weight recovery was noise (`min Σwα` negative). Lowering idio vol to `0.003–0.005` makes every active planted row individually positive (`min ≈ +2.1e-5`), so the recovery assertion is provable row-wise rather than only in expectation.
- **[REMOVED 2026-11-18T23:32:30Z] "Rank has no test bed" survived WP0 as a prose claim.** WP0 now ships `41` assets with betas `0.30–2.70`, so leg betas clear the `0.20` floor by construction and the rank book can be active without touching a guard. WP1 is the measurement.
- **[REMOVED 2026-11-18T23:26:48Z] P20 had no next row, so the old routing table would route every session to "everything done" and invite an idle/docs-only turn.** The routing table now starts at P21 WP1 (WP0 landed) and each row has a committed-file claim.
- **[REMOVED 2026-11-18T23:26:48Z] A positive mean OOS Sharpe on a random walk looked like a result.** P20's aggregate (`mean_oos_sharpe 1.305563` on a pure synthetic random walk) is a false-positive demonstration. The P21 `null` universe reproduces the same illusion (`Sharpe ≈ 0.64` at zero true alpha); WP2 makes a significance/deflation verdict mandatory before any positive claim.
- **[REMOVED 2026-11-18T22:36:59Z] WP5's "cross-row monotonicity" acceptance criterion was mathematically false.** Cost drag is `tc * turnover`, so a higher uncosted Sharpe can break even sooner (measured: `(w60,q0.2)` `0.834694`/`0.004609` beats `(w90,q0.2)` `0.810267`/`0.005078`). Replaced with the provable per-row law: costed Sharpe is non-increasing in `tc`.
- **[REMOVED 2026-11-18T22:36:59Z] WP5's `[0, 0.01]` search range censors the best configuration.** `w180 q0.2` stays positive at `tc=0.01`; the harness reports a documented `None` (censored) instead of a meaningless bisection midpoint.
- **[REMOVED 2026-11-18T21:38:00Z] WP0 sat as "next" across four handoff refreshes.** Landed with 80 rows and hash-pinned artifacts.
- **[REMOVED 2026-11-18T23:32:30Z] WP0 sat as "next" across four handoff refreshes.** Landed with 80 rows and hash-pinned artifacts.
- **[REMOVED 2026-11-18T21:18:00Z] WP choice was prose.** Artifact-based routing (`git ls-files`) decides the WP.
- **[REMOVED 2026-11-19T00:29:44Z] Rank mode is not dollar-neutral.** `construct_rank_weights` makes the book beta-neutral by construction (long leg sums to `1/beta_L`, short leg to `-1/beta_H`), so `|Σw|` is non-zero for rank books. The HANDOFF WP1 spec initially asserted dollar neutrality for both weightings; corrected to assert dollar neutrality only for equal and beta-neutrality (`|Σwβ| < 0.05`) for both, using true betas. The `0.05` bound (not `0.02`) reflects rolling-beta estimation error in rank mode. Do not weaken this to make rank look dollar-neutral.
- **[PERMANENTLY EXTERNAL] P19-1 CI enforcement.** Agent tokens lack `workflows:write`; maintainer-only — never re-attempt, never list as a task.
- **[PERMANENTLY EXTERNAL] Real market data ingestion.** `api.exchange.coinbase.com` returns 403 from this environment; a licensed CSV is maintainer-supplied. Never a P21 task.

---

## Session ledger (append-only, concise)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-19T05:34:13Z | `575601d` | **P22 WP0 complete (heavy work, not a refresh).** The previous session committed `scripts/bab_p22_charter.py`, `tests/test_bab_p22_charter.py`, `research_state/bab_p22/charter.{json,md}` but never ran `main()`, so `docs/BAB_P22_KICKOFF.md` was missing — the WP was not actually landed. Ran `python3 scripts/bab_p22_charter.py` (0.006s), which regenerated `charter.json`/`charter.md` byte-identical and emitted `docs/BAB_P22_KICKOFF.md` (identical to `charter.md`). Committed `docs/BAB_P22_KICKOFF.md`. All 10 `tests/test_bab_p22_charter.py` pass; charter restates the P21 verdict from committed JSON only (no hand-typed numbers), pins 20 null-battery seeds, nominal slack 0.05, and WP1-WP4 acceptance thresholds. Bottleneck removed: P22 WP0 was claimable-but-unlanded; now fully landed and artifact-gated. Binding row advances to **P22 WP1 — null battery (>=20 seeds)**. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6616 passed / 35 skipped / 100% (6644/6644)** (144.11 s) |
| 2026-11-19T02:44:44Z | `8591247` | **P21 WP3 landed + handoff re-certified (heavy work, not a refresh).** Added `tests/test_bab_p21_cost_surface.py` (18 tests: fresh-build JSON identity, committed markdown == renderer, hash determinism, WP0/WP1 read-only byte-identity, three cost components with a zero baseline, all four books active `541/600` and uncensored, per-book and per-period non-increasing costed Sharpe, cost drag/total cost monotone, total-cost linearity in the level, zero-level == gross book, exposure-series hand case, documented censoring reason with `surfaces=None`). Fixed `render_markdown` character-per-line bug. Re-routed to **P21 WP4** and pre-declared **Campaign P22**. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6593 passed / 35 skipped / 100% (6644/6644)** (144.96 s) |
| 2026-11-19T00:29:44Z | `d39dfba` + working tree | **P21 WP1 landed (heavy work, not a refresh).** Added `scripts/bab_rank_eval.py` (pure `build_rank_eval`, `render_markdown`, `write_artifacts`, `main`), `research_state/bab_p21/rank_eval.{json,md}` (4-book eval: planted/null x equal/rank), and `tests/test_bab_p21_rank_eval.py` (12 tests: committed==fresh, determinism, guard defaults pinned, both books active on planted with 541 rows each, rank guards respected `min_leg_beta >= 0.507 > 0.20` and `gross_max <= 2.369 < 4.0`, beta neutrality `|Σwβ| < 0.05` for both weightings, dollar neutrality `|Σw| < 1e-12` for equal only, planted recovery `+2.6e-4` equal / `+1.7e-2` rank, null recovery exactly `0`, markdown JSON-derived, runtime < 1 s). Corrected the WP1 spec error: rank mode is beta-neutral but not dollar-neutral (README §5), so dollar-neutrality is asserted for equal only; true-beta exposure tolerance set to `0.05` for rank due to rolling-beta estimation error. Removed the "rank has no test bed" bottleneck — rank is empirically measurable on WP0's 41-asset universe. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6563 passed / 35 skipped / 100% (6644/6644)** (141.72 s) |
| 2026-11-19T01:31:28Z | `c92c641` + working tree | **P21 WP2 landed (heavy work, not a refresh).** Added `scripts/bab_significance.py` (pure `build_significance`, `render_markdown`, `write_artifacts`, `main`; fixed-seed moving-block bootstrap, 2000 resamples, block length 20, seed 20261119; deflated Sharpe for the 40-candidate P20 grid), `research_state/bab_p21/significance.{json,md}`, and `tests/test_bab_p21_significance.py` (12 tests: committed==fresh, determinism, universe read-only / panel sha integrity, null calibrated `p_value` 0.1635/0.2680 >= 0.05 not significant, planted detected `p_value` 0.0000 with CI excluding zero, `null_calibrated=True`/`planted_detected=True`, DSR hand-computed unit case pinned 0.948765, markdown JSON-derived). Removed the "uncalibrated signal" bottleneck — WP2 makes a significance/deflation verdict mandatory before any positive claim. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6575 passed / 35 skipped / 100% (6644/6644)** (142.30 s) |
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

P19-7 (222 broad/bare `except` handlers annotated, 0 unannotated), P19-2/3/4, P17-1/2, P18-1/2/3, kill-switch R4-B, bootstrap, reconciliation R5-B/R5-C, live-adapter two-key safety, 100% line coverage of `strategies/betting_against_beta`, Milestones 1–5 hygiene, **P20 WP0 (deterministic 80-row equal-weight sweep + hash-pinned artifacts + 10-test acceptance file)**, **P20 WP1 (beta-neutral default + frozen rebalance windows + fidelity doc + README correction)**, **P20 WP2 algebra (rank construction, exact 4-asset hand example, no-lookahead, equal-path byte-identity)**, **P20 WP2b (rank leg-beta floor + gross cap + wide-universe proof + fixture-flat scope)**, **P20 WP3 (walk-forward with train-only selection + anti-lookahead guards + 10-test acceptance file)**, **P20 WP5 (10-row break-even bisection, 6 fixed iterations, 16-test acceptance file, censoring and non-positive rows reported as documented nulls)**, **P20 WP4 (published report with 237/237 numbers machine-matched to committed JSON, JSON-only table renderers, rank discipline and null honesty enforced by 12 tests)**, **P21 WP0 (41-asset / 600-row planted+null universe, convex monotone alpha, sha-pinned panels, 14-test acceptance file, planted recovery `+2.6e-4`, null recovery exactly `0`)**, **P21 WP1 (rank vs equal evaluation on the planted universe: 541 active rows for all four books, rank guards respected, planted recovery `+2.6e-4` equal / `+1.7e-2` rank, null recovery exactly `0`, beta neutrality `|Σwβ| < 0.05` for both weightings, dollar neutrality `|Σw| < 1e-12` for equal only)**, **P21 WP3 (three-component cost surface: 541/600 active rows for all four books, per-book and per-period non-increasing costed Sharpe in every component, documented censoring path, byte-identical reruns, 18-test acceptance file)**. `scripts/bab_except_inventory.py` is retained as a read-only audit tool; running it is not a deliverable.
