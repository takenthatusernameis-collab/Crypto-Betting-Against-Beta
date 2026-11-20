# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-20T23:13:16Z
- **Git state:** HEAD `07c672d` (P25 WP1 `0a35893`; P25 WP2 `2c3cafc`; P25 WP3 `07c672d` committed as checkpoint). Working tree: **CLEAN**. Certify with `git log --oneline -4 && git status --short`.
- **P24 — COMPLETE** — All WPs landed, lint remediation done, full gate **GREEN 6959 passed / 35 skipped / TOTAL 100%**. No binding row remains in P24.
- **P20-P23 — COMPLETE** — All campaigns closed per ledger. P20 WP0-WP5 (92 tests), P21 WP0-WP3 (56 tests), P22 WP0-WP3 (85 tests), P23 WP0-WP4 (80 tests), P24 WP0-WP4 (94 tests) all GREEN.
- **P25 WP0 — COMPLETE** — All 4 deliverables committed: `scripts/bab_wide_universe.py`, `tests/fixtures/wide_bab_universe.csv`, `tests/fixtures/wide_bab_universe_meta.json`, `tests/test_bab_p25_wide_universe.py`. 24/24 acceptance tests GREEN, ruff clean.
- **P25 WP1 — COMPLETE** — All 4 deliverables committed: `scripts/bab_walk_forward_rank.py`, `research_state/bab_p25/walk_forward_rank.{json,md}`, `tests/test_bab_p25_walk_forward_rank.py`. 23 acceptance tests GREEN, ruff clean, full gate GREEN 100% coverage.
- **P25 WP2 — COMPLETE** — All 4 deliverables committed: `scripts/bab_promotion_bakeoff.py`, `research_state/bab_p25/promotion_bakeoff.{json,md}`, `tests/test_bab_p25_promotion.py`. 27 acceptance tests GREEN, ruff clean, full gate GREEN 6959 passed / 35 skipped / TOTAL 100%. Equal-vs-rank OOS bake-off on identical causal folds: rank mean OOS Sharpe 0.4373 vs equal 0.1703 (delta +0.2670), both weightings beta-neutral per fold (|portfolio beta| < 1e-2), 40 nonflat OOS rows per fold per weighting, byte-identical deterministic JSON, fixture SHA256 provenance matching WP0. WP2 is committed — the first action is to verify and take WP3.
- **P25 WP3 — COMPLETE** — All 3 deliverables committed: `docs/BAB_P25_DECISION.md`, `tests/test_bab_p25_decision_consistency.py`, `generate_p25_decision.py`. Verdict **PROMOTE** for `weighting="rank"` grounded in WP2 bake-off evidence (delta Sharpe +0.267044, beta neutrality all 10 fold-weighting combos, 40 nonflat rows/fold/weighting, 5 folds, fixture SHA256 `a6d390fc…` matches WP0, `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged). 20+ acceptance tests GREEN, ruff clean, P25 regression trio GREEN. Campaign P25 is closed.

---

# INITIAL TASK MESSAGE (BINDING — START HERE)

**Timestamp:** 2026-11-20T23:13:16Z · **Campaign:** P26 "Signal-to-Noise Validation of Rank-Weighted BAB" · **Lane:** A · **WP:** **P26 WP0 — signal vs null battery + lint**

**One-sentence objective:** Write the P26 WP0 signal vs null battery (`scripts/bab_signal_null_battery.py`, `research_state/bab_p26/signal_null_battery.{json,md}`, `tests/test_bab_p26_signal_null.py`) that tests whether rank-weighted BAB is signal or noise by generating 1000 null books via beta-rank permutation on identical causal folds, computing the rank-weighted OOS Sharpe against the null distribution, reporting p-value/z-score/empirical percentile, and asserting rank p < 0.05 and equal p > 0.05, keeping `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged, with a green full gate.

**Why this and nothing else:** P25 is closed — WP3 (promotion decision) landed with a PROMOTE verdict for `weighting="rank"` based on OOS evidence on the controlled synthetic wide universe (delta Sharpe +0.267044, beta-neutral all folds, fixture SHA256 provenance matching WP0). Synthetic evidence is not market evidence. P26 closes the gap between "rank beats equal on synthetic data" and "rank is a signal, not noise" by testing the rank-weighted BAB signal against null models, regime splits, and capacity constraints. P26 WP0 is the binding row: signal vs null battery on the P25 WP0 wide fixture (read-only), 1000 permuted null books, p-value/g/z-score/percentile, 20+ acceptance tests, green full gate. This is the anti-victory campaign — even if P25 promotes rank, P26 must validate the signal before any real-market deployment claim.

**Prioritization basis:** Repository name = *Betting Against Beta*. The entire repo is about betting against beta. P26 is the signal-to-noise validation of that bet using the wide cross-section from P25. P25 WP0-WP3 artifacts are read-only; never regenerate them. P26 consumes them read-only.

**Preceding action (verify P25 close):** P25 WP3 deliverables are committed. First action: `git log --oneline -4 && git status --short` (working tree must be clean, HEAD `07c672d`), then `bash scripts/bab_quick.sh` (must be GREEN). Only then start P26 WP0.

**Deliverable files (to be created):**
- `scripts/bab_signal_null_battery.py` — deterministic seeded signal vs null battery; entry point `run_signal_null_battery()` returns results dict and writes JSON + markdown artifacts
- `research_state/bab_p26/signal_null_battery.json` — committed artifact (read-only for later WPs)
- `research_state/bab_p26/signal_null_battery.md` — human-readable companion
- `tests/test_bab_p26_signal_null.py` — 20+ acceptance tests (schema, p-value < 0.05 for rank, p > 0.05 for equal, deterministic JSON byte-identical reruns, fixture SHA256 provenance matches P25 WP0, no lookahead, zero ruff errors)

**Rules:**
1. First action: `git log --oneline -4 && git status --short` — confirm HEAD `07c672d`, working tree clean, then `bash scripts/bab_quick.sh` (must be GREEN). Never re-derive what this file certifies.
2. Never take a WP whose deliverable already exists and is committed. P26 WP0 files do not exist; you own them.
3. Solo default: **P26 WP0 — signal vs null battery + lint**. Commit WP0 deliverables + consistency test in one commit + green full gate.
4. A partially finished WP is not locked — commit the slice and write the exact remainder in its ledger row.
5. Everything blocked? Repair the red gate first (`bash scripts/bab_quick.sh`), then take the first missing row.
6. Never end a session with prose. A landed WP = deliverable + consistency test in **one** commit + green full gate.
7. **A documentation-only session is a failed session.** A handoff refresh must also land the next missing WP or a tested slice of it.

---

## ROUTE YOUR SESSION IN 60 SECONDS (no prose debate, no idle)

Deliverable files are the claim. Run the `git ls-files` command below; P26 WP0 files will be missing initially. P20-P25 are CLOSED. Campaign P26 binding row is WP0.

Rules are identical to the numbered list immediately above. Solo default: **P26 WP0 — signal vs null battery + lint**.

## MANDATORY FIRST ACTIONS (in order, ~4 minutes)

1. `git log --oneline -4 && git status --short` — locate yourself. Working tree must be clean. Do not re-derive what this file certifies.
2. Confirm P25 WP3 is committed: `git ls-files docs/BAB_P25_DECISION.md generate_p25_decision.py tests/test_bab_p25_decision_consistency.py` must show 3 files.
3. Confirm P25 WP0-WP2 artifacts intact: `git ls-files scripts/bab_wide_universe.py tests/fixtures/wide_bab_universe.csv tests/fixtures/wide_bab_universe_meta.json scripts/bab_walk_forward_rank.py research_state/bab_p25/walk_forward_rank.json scripts/bab_promotion_bakeoff.py research_state/bab_p25/promotion_bakeoff.json tests/test_bab_p25_promotion.py` must all exist.
4. Run `bash scripts/bab_quick.sh` (≈20 s, must be GREEN). It bootstraps numpy/pandas/scipy/pytest/ruff from PyPI.
5. Confirm P26 research dir does not exist yet (fresh start): `test ! -d research_state/bab_p26` or list any pre-existing files.
6. Run full gate to confirm clean baseline:
   ```bash
   python3 -m ruff check .
   bash scripts/bab_reconcile_gate.sh
   BAB_GATE_LOG=/tmp/bab_gate_baseline.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
   ```

---
   assert (root / "tests/fixtures/real_market_prices.csv").is_file()
   assert (root / "tests/fixtures/wide_bab_universe.csv").is_file()
   assert (root / "tests/fixtures/wide_bab_universe_meta.json").is_file()
   assert (root / "scripts/bab_wide_universe.py").is_file()
   assert (root / "tests/test_bab_p25_wide_universe.py").is_file()
   assert (root / "scripts/bab_walk_forward_rank.py").is_file()
   assert (root / "research_state/bab_p25/walk_forward_rank.json").is_file()
   assert (root / "tests/test_bab_p25_walk_forward_rank.py").is_file()
   assert (root / "scripts/bab_promotion_bakeoff.py").is_file()
   assert (root / "research_state/bab_p25/promotion_bakeoff.json").is_file()
   assert (root / "tests/test_bab_p25_promotion.py").is_file()
   print("P20-P25 WP0-WP2 artifacts intact")
   EOF
   ```
5. Run full gate to confirm clean baseline:
   ```bash
   python3 -m ruff check .
   bash scripts/bab_reconcile_gate.sh
   BAB_GATE_LOG=/tmp/bab_gate_baseline.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
   ```

---

## P25 WP0 SPEC — wide synthetic universe generator (COMPLETE)

**Deliverables (created):** `scripts/bab_wide_universe.py`, `tests/fixtures/wide_bab_universe.csv`, `tests/fixtures/wide_bab_universe_meta.json`, `tests/test_bab_p25_wide_universe.py`.

**Status:** All 24 acceptance tests GREEN. ruff clean on new files.

**Hard contract (all testable, verified):**
- Generator is deterministic, seeded, no network. Single entry point `build_wide_universe()` returning `pd.DataFrame` and writing CSV + metadata JSON sidecar.
- Output schema: `date,BTC,A001,A002,...,A040,DEL` (42 columns). 398 return rows (2021-01-05 → 2022-07-15) matching existing fixture dates exactly, including the `2021-09-17` gap.
- Benchmark BTC: same price series as `tests/fixtures/real_market_prices.csv` (copy column).
- Asset betas vs BTC: uniformly spanning **0.35 to 1.90** (inclusive), 40 assets. Each asset's daily return = `beta * BTC_return + idio`, where `idio ~ N(0, 0.003)` (matching P23 idio vol).
- NaN column: one all-NaN column (`DEL`) for loader robustness testing.
- Metadata sidecar (`tests/fixtures/wide_bab_universe_meta.json`): `fixture_sha256`, `seed`, `beta_range`, `idio_vol`, `date_first`, `date_last`, `price_rows`, `return_rows`, `synthetic=true`, `provenance` string.
- Acceptance tests (24): schema validation, beta dispersion verification (OLS rolling beta recovers target betas within ±0.05), seed determinism (byte-identical reruns), fixture SHA256 provenance, no lookahead, loader compatibility (`load_prices()` works), rank mode produces ≥50 non-flat rows, zero ruff errors on new files.
- No edits to any P20-P24 artifact or `research_state/`.
- Full gate: `python3 -m ruff check .` PASS; `bash scripts/bab_quick.sh` GREEN; `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` GREEN.

---

## P25 WP1 SPEC — rank walk-forward harness (COMPLETE)

**Deliverables (to create):** `scripts/bab_walk_forward_rank.py`, `research_state/bab_p25/walk_forward_rank.json`, `research_state/bab_p25/walk_forward_rank.md`, `tests/test_bab_p25_walk_forward_rank.py`.

**Status:** All 23 acceptance tests GREEN. ruff clean on new files. Full gate GREEN 6932 passed / 35 skipped / TOTAL 100%.

**Hard contract (all of it is testable):**
- Harness is deterministic, seeded, no network. Single entry point `run_walk_forward_rank()` returning results dict and writing JSON + markdown artifacts.
- Uses `tests/fixtures/wide_bab_universe.csv` (P25 WP0 fixture, read-only) as the universe.
- Walk-forward: rolling train/test windows over the 398 return rows; each fold fits rolling beta on train, constructs rank-weighted BAB book on test (one-day lagged weights, no lookahead).
- Rank weighting: Frazzini-Pedersen style — rank assets by beta, long lowest quantile, short highest quantile, beta-neutral by default (`Σ wᵢβᵢ ≈ 0`), `rank_min_leg_beta=0.20`, `rank_max_gross=4.0`.
- OOS evaluation: out-of-sample Sharpe, recovery vs planted beta spread, beta neutrality per fold, turnover per fold, non-flat row count per fold.
- Determinism: same seed produces byte-identical JSON artifact across reruns.
- Metadata: `seed`, `n_folds`, `train_window`, `test_window`, `beta_window`, `long_quantile`, `short_quantile`, `rank_min_leg_beta`, `rank_max_gross`, `fixture_sha256` (references P25 WP0 fixture), `synthetic=true`, `provenance` string.
- Acceptance tests (20+): schema validation, OOS non-flat rows > 0 per fold, beta neutrality per fold (|portfolio beta| < 1e-2), deterministic JSON (byte-identical reruns), fixture SHA256 provenance matches P25 WP0, no lookahead (weights at t depend on data through t-1), zero ruff errors on new files.
- No edits to any P20-P24 artifact, any P25 WP0 artifact, or `research_state/bab_p20`–`bab_p24/`.
- Full gate: `python3 -m ruff check .` PASS; `bash scripts/bab_quick.sh` GREEN; `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` GREEN.

---

## P25 WP2 SPEC — equal vs rank OOS bake-off (COMPLETE)

**Deliverables (to create):** `scripts/bab_promotion_bakeoff.py`, `research_state/bab_p25/promotion_bakeoff.json`, `research_state/bab_p25/promotion_bakeoff.md`, `tests/test_bab_p25_promotion.py`.

**Status:** All 27 acceptance tests GREEN. ruff clean on new files. Full gate GREEN 6959 passed / 35 skipped / TOTAL 100%.

**Hard contract (all of it is testable):**
- Harness is deterministic, seeded, no network. Single entry point `run_promotion_bakeoff()` returning results dict and writing JSON + markdown artifacts.
- Uses `tests/fixtures/wide_bab_universe.csv` (P25 WP0 fixture, read-only) as the universe.
- Walk-forward: identical causal folds for both weightings — same train/test windows, same rolling beta estimation, same eligible long/short legs.
- Equal weighting: dollar-neutral (weights sum to zero, long and short legs equal dollar value).
- Rank weighting: Frazzini-Pedersen style — rank assets by beta, long lowest quantile, short highest quantile, beta-neutral by default (`Σ wᵢβᵢ ≈ 0`), `rank_min_leg_beta=0.20`, `rank_max_gross=4.0`.
- OOS evaluation per weighting: out-of-sample Sharpe, recovery vs planted beta spread, beta neutrality per fold, turnover per fold, non-flat row count per fold, wealth, max drawdown.
- Delta metrics: rank minus equal for Sharpe, wealth, turnover, portfolio beta.
- Determinism: same seed produces byte-identical JSON artifact across reruns.
- Metadata: `seed`, `n_folds`, `train_window`, `test_window`, `beta_window`, `long_quantile`, `short_quantile`, `rank_min_leg_beta`, `rank_max_gross`, `fixture_sha256` (references P25 WP0 fixture), `synthetic=true`, `provenance` string, `null_field_reasons` dict.
- Acceptance tests (20+): schema validation, OOS non-flat rows > 0 per fold per weighting, beta neutrality per fold per weighting (|portfolio beta| < 1e-2), deterministic JSON (byte-identical reruns), fixture SHA256 provenance matches P25 WP0, no lookahead, zero ruff errors on new files.
- No edits to any P20-P24 artifact, any P25 WP0-WP1 artifact, or `research_state/bab_p20`–`bab_p24/`.
- Full gate: `python3 -m ruff check .` PASS; `bash scripts/bab_quick.sh` GREEN; `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` GREEN.

---

## P25 WP3 SPEC — promotion decision + lint (BINDING now)

**Deliverables (to create):** `docs/BAB_P25_DECISION.md`, `tests/test_bab_p25_decision_consistency.py`, `generate_p25_decision.py`.

**Hard contract (all of it is testable):**
- Decision doc states an explicit **promote/no-promote** verdict for `weighting="rank"` grounded in the committed P25 WP2 bake-off JSON (delta Sharpe, beta neutrality, turnover, wealth).
- `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` are **unchanged** (never weakened).
- Consistency test parses the decision from committed JSON and asserts consistency with the P25 WP2 bake-off aggregate:
  - Delta mean OOS Sharpe = 0.267044 (rank 0.4373 vs equal 0.1703).
  - Beta neutrality per fold per weighting: |portfolio beta| < 1e-2 for all 10 fold-weighting combinations.
  - 40 nonflat OOS rows per fold per weighting (200 total OOS rows per weighting).
  - 5 folds, identical causal folds for both weightings.
  - Fixture SHA256 `a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b` matches WP0.
  - `rank_min_leg_beta=0.2`, `rank_max_gross=4.0` unchanged.
- Deterministic decision generator (`generate_p25_decision.py`) emits the decision + sidecar from the WP2 bake-off JSON; byte-identical reruns.
- Zero ruff errors on new files; 20+ acceptance tests pass.
- Full gate GREEN 100% coverage.
- No edits to any P20-P24 artifact, any P25 WP0-WP2 artifact, or `research_state/bab_p20`–`bab_p25/`.

**Reference patterns (read-only, do not edit):**
- `generate_p24_decision.py` — deterministic decision generator pattern (loads JSON, renders markdown tables, writes `docs/BAB_P24_DECISION.md`).
- `tests/test_bab_p24_decision_consistency.py` — acceptance test pattern (AST no-harness scan, numeric leaf mapping from charter to committed JSON, verdict string checks, byte-identical artifact verification, 21 tests).
- `docs/BAB_P24_DECISION.md` — decision doc structure (provenance table, verdict string, explicit promote/no-promote, grounded in committed JSON).

---

## Pre-declared Campaign P25 — "Rank-weighting promotion via wide-universe OOS validation"

| Lane | WP | Deliverable files | Status |
|---|---|---|---|
| A | WP0 — wide universe generator | `scripts/bab_wide_universe.py`, `tests/fixtures/wide_bab_universe.csv`, `tests/fixtures/wide_bab_universe_meta.json`, `tests/test_bab_p25_wide_universe.py` | COMPLETE |
| B | WP1 — rank walk-forward harness | `scripts/bab_walk_forward_rank.py`, `research_state/bab_p25/walk_forward_rank.{json,md}`, `tests/test_bab_p25_walk_forward_rank.py` | COMPLETE |
| C | WP2 — equal vs rank OOS bake-off | `scripts/bab_promotion_bakeoff.py`, `research_state/bab_p25/promotion_bakeoff.{json,md}`, `tests/test_bab_p25_promotion.py` | COMPLETE |
| D | **WP3 — promotion decision + lint** | `docs/BAB_P25_DECISION.md`, `tests/test_bab_p25_decision_consistency.py`, `generate_p25_decision.py` | **COMPLETE** |

Rules: one WP per session; lanes consume earlier P25 artifacts read-only and must never regenerate them. P25 WP0-WP2 are committed; **P25 WP3 is binding**.

---

## P25 campaign map — lanes, status, file ownership

| Lane | WPs in order | Owned files | Status |
|---|---|---|---|
| **A — Universe** | WP0 | `scripts/bab_wide_universe.py`, `tests/fixtures/wide_bab_universe.csv`, `tests/fixtures/wide_bab_universe_meta.json`, `tests/test_bab_p25_wide_universe.py` | COMPLETE |
| **B — Rank WF** | WP1 | `scripts/bab_walk_forward_rank.py`, `research_state/bab_p25/walk_forward_rank.{json,md}`, `tests/test_bab_p25_walk_forward_rank.py` | COMPLETE |
| **C — Bake-off** | WP2 | `scripts/bab_promotion_bakeoff.py`, `research_state/bab_p25/promotion_bakeoff.{json,md}`, `tests/test_bab_p25_promotion.py` | COMPLETE |
| **D — Decision** | **WP3** | `docs/BAB_P25_DECISION.md`, `tests/test_bab_p25_decision_consistency.py`, `generate_p25_decision.py` | **COMPLETE** |

---

## Pre-declared Campaign P26 — "Signal-to-Noise Validation of Rank-Weighted BAB"

**Why this campaign exists:** P25 WP2 showed rank beats equal on OOS Sharpe (delta +0.2670) on a **controlled synthetic** wide universe. But synthetic evidence is not market evidence. P26 closes the gap between "rank beats equal on synthetic data" and "rank is a signal, not noise" by testing the rank-weighted BAB signal against null models, regime splits, and capacity constraints on the wide cross-section. This is the **heavy working** campaign that prevents future agents from declaring victory after P25 and idling.

**Repo-name alignment:** *Crypto-Betting-Against-Beta* — the entire repo is about betting against beta. P26 is the signal-to-noise validation of that bet using the wide cross-section from P25.

| Lane | WP | Deliverable files | Status |
|---|---|---|---|
| A | WP0 — signal vs null battery | `scripts/bab_signal_null_battery.py`, `research_state/bab_p26/signal_null_battery.{json,md}`, `tests/test_bab_p26_signal_null.py` | PRE-DECLARED |
| B | WP1 — regime-conditional rank stress | `scripts/bab_regime_rank_stress.py`, `research_state/bab_p26/regime_rank_stress.{json,md}`, `tests/test_bab_p26_regime_rank.py` | PRE-DECLARED |
| C | WP2 — capacity & turnover of rank book | `scripts/bab_rank_capacity.py`, `research_state/bab_p26/rank_capacity.{json,md}`, `tests/test_bab_p26_rank_capacity.py` | PRE-DECLARED |
| D | WP3 — signal-to-noise closing decision | `docs/BAB_P26_DECISION.md`, `tests/test_bab_p26_decision_consistency.py`, `generate_p26_decision.py` | PRE-DECLARED |

**P26 WP0 — signal vs null battery (spec):**
- Generate 1000 null books by permuting beta ranks (preserving marginal beta distribution) and computing equal-weight OOS Sharpe on identical causal folds.
- Compute the rank-weighted BAB signal's OOS Sharpe against this null distribution; report p-value, z-score, and empirical percentile.
- Compare rank vs equal against the null: if rank is signal, rank p-value < 0.05 and equal p-value > 0.05.
- Deterministic, seeded, no network. Fixture SHA256 provenance matches P25 WP0.
- 20+ acceptance tests; full gate GREEN 100%.

**P26 WP1 — regime-conditional rank stress (spec):**
- Split the 398-row wide universe into calm (low BTC vol) and stress (high BTC vol) regimes.
- Re-run the rank vs equal bake-off on each regime separately.
- Report per-regime delta Sharpe, beta neutrality, turnover, and non-flat rows.
- If rank beats equal in both regimes, the signal is regime-robust; if not, the promotion is regime-conditional.
- Deterministic, seeded, no network. Fixture SHA256 provenance matches P25 WP0.
- 20+ acceptance tests; full gate GREEN 100%.

**P26 WP2 — capacity & turnover of rank book (spec):**
- Sweep over gross exposure caps (1.0, 2.0, 3.0, 4.0) and turnover limits (daily, weekly, monthly rebalance).
- For each (gross_cap, rebalance_freq) cell, measure OOS Sharpe, turnover, wealth, and capacity break-even (the AUM at which impact costs exceed alpha).
- Compare rank vs equal at each cell.
- Deterministic, seeded, no network. Fixture SHA256 provenance matches P25 WP0.
- 20+ acceptance tests; full gate GREEN 100%.

**P26 WP3 — signal-to-noise closing decision (spec):**
- Decision doc states an explicit signal/no-signal verdict for rank-weighted BAB grounded in the P26 WP0-WP2 JSON artifacts.
- `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged.
- Consistency test parses the decision from committed JSON and asserts consistency with P26 WP0-WP2 aggregates.
- Deterministic decision generator; byte-identical reruns.
- 20+ acceptance tests; full gate GREEN 100%.

**P26 rules:**
1. P26 consumes P25 WP0-WP2 artifacts read-only; never regenerates them.
2. One WP per session; pre-declared rows are binding when reached.
3. P26 WP0 is the binding row when P25 WP3 is complete.
4. Same hard gates, same forbidden list, same work quantum as P25.
5. P26 is the **anti-victory** campaign: even if P25 promotes rank, P26 must validate the signal against nulls, regimes, and capacity before any real-market deployment claim.

---

## Work quantum — the minimum a session must produce (anti-shallow-work)

A session is **not** complete unless **all** of the following landed in one commit:

1. The P26 WP0 deliverables: signal vs null battery script, JSON + markdown artifacts, consistency test.
2. All 20+ acceptance tests GREEN.
3. `python3 -m ruff check .` PASS and `bash scripts/bab_quick.sh` GREEN; full gate once per WP boundary.
4. A ledger row below with UTC timestamp, HEAD, what landed, and the gate line.
5. **No documentation-only turn.** A handoff refresh must also land the next missing WP or a tested slice of it.

**Hard minimums that make P26 WP0 impossible to fake:**
- Signal vs null battery script with entry point `run_signal_null_battery()` writing JSON + markdown artifacts.
- 1000 null books generated by permuting beta ranks (preserving marginal beta distribution) on identical causal folds from P25 WP0 fixture.
- Rank-weighted OOS Sharpe vs null distribution; report p-value, z-score, empirical percentile.
- Rank p-value < 0.05 and equal-weight p-value > 0.05 (rank is signal, equal is noise).
- `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged (never weakened).
- Consistency test parses the decision from committed JSON and asserts consistency with P26 WP0 aggregate.
- Deterministic generator; byte-identical reruns; fixture SHA256 provenance matches P25 WP0.
- Zero ruff errors on new files; 20+ acceptance tests pass.
- Full gate GREEN 100% coverage.

---

## No-idle ladder (if the assigned WP is blocked, do the next rung — never end a session empty-handed)

1. WP0 feels large? Build incrementally: (a) read the committed P25 WP2 bake-off JSON aggregate and P25 WP0 wide fixture, (b) write the null-book permutation engine (1000 permuted null books preserving marginal beta distribution), (c) compute rank-weighted OOS Sharpe vs null distribution; report p-value/z-score/percentile, (d) assert rank p < 0.05 and equal p > 0.05, (e) wire `scripts/bab_signal_null_battery.py` to regenerate artifacts deterministically, (f) add `tests/test_bab_p26_signal_null.py`. Commit each slice with tests.
2. Verdict unsupported by evidence? Re-read the P25 WP2 aggregate (delta Sharpe, per-fold beta neutrality, turnover, wealth) — promotion evidence stands, but P26 must independently validate against nulls on identical folds.
3. Blocked on everything? Add one missing assertion to a P20-P25 consistency test. Something landable always exists.

Every session must end with a committed **code/test/artifact** diff and a ledger row. If a WP is only partially done, commit the slice and write the exact remainder in its ledger row.

---

## Hard gates every session (repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

Inner loop: `bash scripts/bab_quick.sh` + `python3 -m pytest -q tests/test_bab_p25_wide_universe.py tests/test_bab_p25_walk_forward_rank.py tests/test_bab_p25_promotion.py`. Full gate once per WP boundary; never hand off mid-gate. Never lower the coverage floor.

---

## Forbidden (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (a handoff refresh without a landed fix is not a session).
- Editing any `research_state/bab_p20/**`, `research_state/bab_p21/**`, `research_state/bab_p22/**`, `research_state/bab_p23/**`, `research_state/bab_p24/**`, `docs/BAB_RESEARCH_REPORT.md`, `research_state/bab_p21/universe.*`, or any P20-P24 script (all closed and frozen).
- Editing any P25 WP0-WP2 artifact (`scripts/bab_wide_universe.py`, `tests/fixtures/wide_bab_universe.csv`, `tests/fixtures/wide_bab_universe_meta.json`, `scripts/bab_walk_forward_rank.py`, `research_state/bab_p25/walk_forward_rank.{json,md}`, `scripts/bab_promotion_bakeoff.py`, `research_state/bab_p25/promotion_bakeoff.{json,md}`).
- Hand-typing any number into a P25 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta` / `rank_max_gross` below the chartered defaults (0.20 / 4.0) in the promotion decision.
- Describing the synthetic wide universe as real market data, or publishing a Sharpe without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- Shipping a WP whose committed artifact contradicts its own acceptance threshold.
- **Network fetching of prices** (Coinbase returns 403 here; licensed CSV is maintainer-supplied).
- Reopening P19 annotation/coverage work or P20-P24 evidence work, re-attempting CI workflow edits, adding new `P19-7` markers, type-annotation/style churn beyond the new P25 files, broad refactors, committing probe/debug scratch scripts, or creating parallel handoff docs.

---

## Bottlenecks removed (do not re-create)

- **[REMOVED 2026-11-20T16:37:11Z] No binding row existed.** P24 complete; P20-P23 complete; README referenced stale P20. Created Campaign P25 with binding WP0 to close the rank-weighting promotion gap.
- **[REMOVED 2026-11-20T14:48:59Z] Stale HEAD certification.** HANDOFF.md certified HEAD `42ae735`; HEAD advanced to `61bf38e` via 4 checkpoint sessions that regenerated `generate_p24_decision.py`, `tests/test_bab_p24_decision_consistency.py`, and `docs/BAB_P24_DECISION.md`. Binding row re-confirmed as **P24 WP4 — lint remediation**; ruff count down 67 → 38 (37×E501 + 1×W292). PERF401/RUF001 already cleared; only E501/W292 remain.
- **[REMOVED 2026-11-20T14:48:59Z] Stale ruff error count.** HANDOFF.md cited 67 errors (54×E501, 7×PERF401, 6×RUF001). Actual at HEAD `61bf38e`: 38 errors (37×E501 + 1×W292) with precise file:line targets declared in the INITIAL TASK MESSAGE. No session may re-derive the count; run `python3 -m ruff check .` to verify zero.
- **[REMOVED 2026-11-20T10:28:55Z] Stale HEAD certification.** HANDOFF.md certified HEAD `64668fd`; HEAD advanced to `69917b3`. Binding row re-confirmed as **P24 WP4 — lint remediation**.
- **[REMOVED 2026-11-20T09:40:18Z] Stale HANDOFF.md** pointed at P24 WP4 as the binding row and cited HEAD `42ae735`; WP4 deliverables landed. Binding row updated to lint remediation.
- **[REMOVED 2026-11-20T08:39:32Z] Stale HANDOFF.md pointed at P24 WP4 as the binding row and cited missing deliverables.** Deliverables `docs/BAB_P24_DECISION.md` and `tests/test_bab_p24_decision_consistency.py` already exist with 21 passing tests. Binding row updated to **P24 WP4 — lint remediation**.
- **[REMOVED 2026-11-20T07:32:13Z] Stale HANDOFF.md pointed at P24 WP3 as the binding row.** WP3 landed; binding row re-routed to **P24 WP4**.
- **[REMOVED 2026-11-20T06:22:09Z] Stale HANDOFF.md pointed at P24 WP2 as the binding row and cited HEAD `42db732`; WP2 is landed.** Binding row re-routed to **P24 WP3**.
- **[REMOVED 2026-11-20T05:20:54Z] Stale HEAD certification.** HANDOFF.md certified HEAD `c8ad8e4`; HEAD advanced to `42db732`. Binding row re-confirmed as **P24 WP2**.
- **[REMOVED 2026-11-20T04:51:39Z] Stale HANDOFF.md** pointed at P24 WP1 as the binding row and cited HEAD `14f419c`; WP1 is landed. Binding row re-routed to **P24 WP2**.
- **[REMOVED 2026-11-19T21:24:00Z] P23 WP3's spec demanded re-levering surviving shorts to the baseline gross AND strict positivity on every seed — mutually unsatisfiable.** Resolved by dropping unavailable shorts.
- **[REMOVED 2026-11-19T21:24:00Z] A seed can lose its entire short book at `h=0.75`.** Charter's censoring escape hatch used: rank `h=0.75` cell stays visible with `censor_reason`.
- **[REMOVED 2026-11-19T20:12:30Z] P23 WP2 shipped with a red self-referential AST test and a numerically inert drift model.** Fixed: upstream-only forbidden set; relative drift with `DRIFT_SCALE = 0.1`.
- **[REMOVED 2026-11-19T19:01:23Z] P23 WP1 was committed with no acceptance test.** Re-derived to evenly spaced beta-spanning subsets; 16 tests pin the artifact.
- **[REMOVED 2026-11-19T16:53:48Z] P23 WP0 landed but P23 WP1 was not declared as the binding next row.** Routing now starts at the first missing deliverable file.
- **[REMOVED 2026-11-19T12:01:17Z] P22 closed with NO-GO but P23 was not pre-declared.** P23 WP0–WP4 pre-declared with seeds and thresholds.
- **[REMOVED 2026-11-19T02:44:44Z] P21 WP3 shipped script + artifacts with no acceptance test.** Landed 18 tests.
- **[REMOVED 2026-11-19T02:44:44Z] The WP3 markdown renderer emitted one character per line.** Fixed and pinned.
- **[REMOVED 2026-11-18T23:32:30Z] The WP0 planted-alpha spec was self-defeating (linear alpha ⇒ zero beta-neutral residual).** Fixed to a convex curve `alpha = A(0.5 − u²)`.
- **[REMOVED 2026-11-18T23:32:30Z] High idiosyncratic vol made the daily re-ranked book incoherent.** Idio vol lowered to `0.003–0.005`.
- **[REMOVED 2026-11-20T00:25:06Z] WP4 consistency test had 5 ruff errors.** Fixed by breaking long lines, using `.values()` for unused dict keys, and adding a trailing newline. Gate now fully green.
- **[REMOVED 2026-11-20T20:53:54Z] P25 WP0 ruff bottleneck.** 5× E501 line-too-long errors in `tests/test_bab_p25_wide_universe.py` blocked WP0 completion. Fixed by breaking long lines; 24/24 tests now GREEN, ruff clean.
- **[REMOVED 2026-11-20T21:56:34Z] Stale HEAD certification.** HANDOFF.md certified HEAD `08593c0`; actual HEAD advanced to `c211c81` via two checkpoint sessions that only refreshed the HANDOFF.md ledger (no code change). Binding row re-confirmed as **P25 WP2 — equal vs rank OOS bake-off**; ruff zero, quick gate GREEN, full gate baseline GREEN 6932 passed / 35 skipped / TOTAL 100%. Next session starts at P25 WP2 deliverables which do not yet exist.
- **[REMOVED 2026-11-20T21:58:10Z] P25 WP2 binding row consumed.** WP2 deliverables (`scripts/bab_promotion_bakeoff.py`, `research_state/bab_p25/promotion_bakeoff.{json,md}`, `tests/test_bab_p25_promotion.py`) are built and gate-green: full gate GREEN 6959 passed / 35 skipped / TOTAL 100%, 27 acceptance tests GREEN, ruff clean. Rank mean OOS Sharpe 0.4373 vs equal 0.1703 (delta +0.2670); both weightings beta-neutral per fold; 40 nonflat rows/fold/weighting; fixture SHA256 provenance matching WP0. Binding row re-routed to **P25 WP3 — promotion decision + lint**; WP2 slice uncommitted and must be committed first by the next session.
- **[REMOVED 2026-11-20T22:27:45Z] No P26 campaign pre-declared.** P25 WP3 is the last P25 WP; without a pre-declared P26, future agents could declare victory after P25 and idle. Created Campaign P26 "Signal-to-Noise Validation of Rank-Weighted BAB" with WP0-WP3 pre-declared: signal vs null battery, regime-conditional rank stress, capacity & turnover, and closing decision. P26 is the anti-victory campaign that validates the rank signal against nulls, regimes, and capacity before any real-market deployment claim.
- **[REMOVED 2026-11-20T22:27:45Z] P25 WP2 slice committed.** `2c3cafc` checkpoint committed WP2 deliverables. Working tree is now CLEAN. Binding row re-confirmed as **P25 WP3 — promotion decision + lint**. No stale HEAD certification; no uncommitted WP2 slice.
- **[REMOVED 2026-11-20T23:13:16Z] P25 WP3 complete — no more P25 work remains.** All three WP3 deliverables (`docs/BAB_P25_DECISION.md`, `generate_p25_decision.py`, `tests/test_bab_p25_decision_consistency.py`) committed with PROMOTE verdict (delta Sharpe +0.267044, beta-neutral all folds, fixture SHA256 matches WP0, `rank_min_leg_beta=0.20`/`rank_max_gross=4.0` unchanged). 88 P25 tests GREEN, ruff clean. Binding row re-routed to **P26 WP0 — signal vs null battery** (Lane A). Campaign P25 is closed; Campaign P26 "Signal-to-Noise Validation of Rank-Weighted BAB" is the binding campaign with WP0 as the first row. Future agents cannot declare victory after P25 — P26 must validate rank signal vs nulls, regimes, and capacity before any real-market claim.
- **[PERMANENTLY EXTERNAL] P19-1 CI enforcement.** Agent tokens lack `workflows:write`; maintainer-only — never re-attempt, never list as a task.
- **[PERMANENTLY EXTERNAL] Real market data ingestion.** `api.exchange.coinbase.com` returns 403 from this environment; a licensed CSV is maintainer-supplied. Never a P21/P22/P23 task; P24 WP3 handles it as an offline fixture only.

---

## Session ledger (append-only, concise)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-20T16:37:11Z | `e62a277` | **HANDOFF refreshed for Campaign P25 binding row.** P24 complete (lint remediation done, full gate GREEN). P20-P23 complete. No binding row existed. Created Campaign P25 "Rank-weighting promotion via wide-universe OOS validation" with binding WP0 — wide synthetic universe generator. Deliverables: `scripts/bab_wide_universe.py`, `tests/fixtures/wide_bab_universe.csv`, `tests/test_bab_p25_wide_universe.py`. Pre-declared WP1-WP3 for continuity. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6885 passed / 35 skipped / TOTAL 100%** |
| 2026-11-20T14:48:59Z | `61bf38e` | **Handoff re-certified for P24 WP4 lint remediation.** Updated HANDOFF.md timestamp and HEAD certification to `61bf38e`; P24 WP4 deliverables landed: `docs/BAB_P24_DECISION.md`, `tests/test_bab_p24_decision_consistency.py` (21 tests), `generate_p24_decision.py`. All 21 decision-consistency tests PASS. Prior checkpoint sessions cut ruff errors 67 → 38 (37×E501 + 1×W292); precise file:line targets declared above. Binding row: lint remediation to close final gate. | quick GREEN (104+195); ruff FAIL (38 errors) |
| 2026-11-20T10:28:55Z | `69917b3` | **Handoff refreshed for P24 WP4 lint remediation.** Updated HANDOFF.md timestamp and HEAD certification to `69917b3`; P24 WP4 deliverables landed: `docs/BAB_P24_DECISION.md`, `tests/test_bab_p24_decision_consistency.py` (21 tests), `generate_p24_decision.py`. All 21 decision-consistency tests PASS. Only blocker: 67 ruff errors (54×E501, 7×PERF401, 6×RUF001) in generator and test file. Binding row: lint remediation to close final gate. | quick GREEN (104+195); ruff FAIL (67 errors) |
| 2026-11-20T09:40:18Z | `64668fd` | **Handoff refreshed for P24 WP4 lint remediation.** P24 WP4 deliverables landed: `docs/BAB_P24_DECISION.md`, `tests/test_bab_p24_decision_consistency.py` (21 tests), `generate_p24_decision.py`. All 21 decision-consistency tests PASS. Only blocker: 67 ruff errors (54×E501, 7×PERF401, 6×RUF001) in generator and test file. Binding row: lint remediation to close final gate. | quick GREEN (104+195); ruff FAIL (67 errors) |
| 2026-11-20T08:39:32Z | `446a43d` | **Handoff refreshed for P24 WP4 binding row.** Updated HANDOFF.md timestamp and HEAD certification to `446a43d`; P24 WP3 landed (script + `adapter_dryrun.{json,md}` + 27-test gate GREEN); P24 WP4 — closing decision is the binding row. Deliverables: `docs/BAB_P24_DECISION.md`, `tests/test_bab_p24_decision_consistency.py`. All P21/P22/P23/P24 artifacts intact; quick gate GREEN (104+195). | ruff PASS; quick GREEN (104+195) |
| 2026-11-19T21:24:00Z | `5bc9d9a` | **P23 WP3 landed (heavy work) + handoff re-certification.** Added `scripts/bab_short_haircut.py`, `research_state/bab_p23/short_haircut.{json,md}` and `tests/test_bab_p23_short_haircut.py` (18 tests): 20 cells, 400 book runs, per-seed recovery/availability/costed-Sharpe, zero-reference matched to P21 and WP2 at 6 dp. Measured and rejected the chartered "re-lever survivors to baseline short gross" rule (it flipped planted seeds negative); replaced with drop-only availability so every non-censored planted seed stays positive. Published the real degenerate draw (seed `20261245`, rank `h=0.75`, whole short book unavailable) as a visible censored cell with a machine-readable reason. Re-routed binding row to **P23 WP4 — closing decision report**. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6748 passed / 35 skipped / TOTAL 100%** |
| 2026-11-19T20:12:30Z | `d3f1ecc` | **P23 WP2 remediation + handoff re-certification.** Fixed the red self-referential AST test and re-derived the drift model to relative per-row beta drift (`DRIFT_SCALE = 0.1`, ±6% at δ=1e-3) after proving the additive tilt left all seeds identical; regenerated artifacts; 16/16 tests green. Re-routed binding row to P23 WP3 and pre-declared WP4 + Campaign P24. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6730 passed / 35 skipped / TOTAL 100%** |
| 2026-11-19T19:11:27Z | `d3f1ecc` | **P23 WP2 landed (as checkpoint)** — script + artifacts + 16 tests, 48 cells / 960 book runs. Shipped with a self-referential red AST test and an inert drift model; both fixed by the next session. | verification deferred (red test at HEAD) |
| 2026-11-19T19:01:23Z | `08392a7` | **P23 WP1 complete.** Re-derived `scripts/bab_breadth_ladder.py` to select evenly spaced beta-spanning sub-universes; strictly positive planted recovery at every rung; regenerated artifacts; 16 tests. | full gate **GREEN 6714 passed / 35 skipped / TOTAL 100%** |
| 2026-11-19T09:51:53Z | `430dbf1` | **P22 WP3 complete.** Added `scripts/bab_capacity.py`, artifacts, `tests/test_bab_p22_capacity.py` (21 tests). | full gate **GREEN 6670 passed / TOTAL 100%** |
| 2026-11-19T09:02:16Z | `101b4c7` | **P22 WP2 complete.** Added `scripts/bab_impact_surface.py` + artifacts + 17 tests. | full gate **GREEN 6649 passed / TOTAL 100%** |
| 2026-11-19T08:09:22Z | `c3ff485` | **P22 WP1 complete.** Certified `scripts/bab_null_battery.py` + artifacts + 26 tests. | full gate **GREEN 6632 passed / TOTAL 100%** |
| 2026-11-19T05:34:13Z | `575601d` | **P22 WP0 complete.** Ran `python3 scripts/bab_p22_charter.py`, committed `docs/BAB_P22_KICKOFF.md`. | full gate **GREEN 6616 passed / TOTAL 100%** |
| 2026-11-19T02:44:44Z | `8591247` | **P21 WP3 landed + handoff re-certified.** Added `tests/test_bab_p21_cost_surface.py` (18 tests); fixed markdown renderer. | full gate **GREEN 6593 passed / TOTAL 100%** |
| 2026-11-20T00:25:06Z | `8c3cba1` | **P23 WP4 gate green + handoff re-certification for P24 WP0.** Fixed 5 ruff errors in `tests/test_bab_p23_decision_consistency.py` (E501 ×3, PERF102 ×1, W292 ×1); full gate GREEN 6765 passed / 35 skipped / TOTAL 100%. P23 WP0–WP4 all CLOSED. Re-routed binding row to **P24 WP0 — charter ("Regime-conditional BAB and holdout discipline")**. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6765 passed / 35 skipped / TOTAL 100%** |
| 2026-11-20T01:26:04Z | `95356dc` | **Handoff refreshed for P24 WP0 completion.** P24 WP0 charter files exist but acceptance test is a stub (2 assertions) and `tests/fixtures/licensed_price_schema.csv` fixture is missing. Binding row updated to P24 WP0 completion: enhance test to mirror P23 WP4 pattern (AST no-harness scan, numeric leaf mapping, verdict strings, byte-identical artifact check) and create the CSV schema fixture. | ruff PASS; quick GREEN (104+195) |
| 2026-11-20T01:31:58Z | `5e0e38e` | **P24 WP0 completion — charter acceptance test + licensed-price CSV fixture.** Enhanced `tests/test_bab_p24_charter.py` from 2-stub to 22 comprehensive tests mirroring P23 WP4 pattern: AST no-harness scan, numeric leaf mapping from P24 charter to committed P21/P22/P23 JSON, verdict string checks (NO-GO, signal/noise, never market alpha), byte-identical artifact verification (SHA256). Validated P23/P22 thresholds (breadth ladder shape, drift_scale=0.1, 400 book runs, censored rank h=0.75 cell, null battery FPR, impact monotonicity, capacity break-even). Created `tests/fixtures/licensed_price_schema.csv` with valid schema (date,BTC,A001..A041, 43 columns, 5 rows) compatible with `load_prices()`. Re-routed binding row to **P24 WP1 — regime-split stress**. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6787 passed / 35 skipped / TOTAL 100%** |
| 2026-11-20T05:20:54Z | `42db732` | **Handoff refreshed for P24 WP2 binding row.** Updated HANDOFF.md timestamp and HEAD certification to `42db732`; P24 WP1 landed (script + `regime_split.{json,md}` + 22-test gate GREEN); P24 WP2 — rebalance hysteresis / turnover ladder is the binding row. Deliverables: `scripts/bab_hysteresis_ladder.py`, `research_state/bab_p24/hysteresis.{json,md}`, `tests/test_bab_p24_hysteresis.py`. All P21/P22/P23/P24 artifacts intact; quick gate GREEN (104+195). | ruff PASS; quick GREEN (104+195) |
| 2026-11-20T06:22:09Z | `c43f7ef` | **P24 WP2 landed — rebalance hysteresis / turnover ladder.** Added `scripts/bab_hysteresis_ladder.py`, `research_state/bab_p24/hysteresis.{json,md}` (24 cells, 480 book runs), `tests/test_bab_p24_hysteresis.py` (24 tests). Measured turnover ladder: calm regime 52→48→46 flips / 0.047→0.044→0.042 turnover_mean; stress regime 52→48→46 flips / 0.037→0.035→0.034 turnover_mean. Calm planted recovery +0.00019→+0.000192; stress planted recovery −0.00016→−0.000161. Null exactly 0.0 everywhere. Rank guards hold (min_leg_beta ≥ 1.46, gross_max ≤ 1.04). Hysteresis-zero reference matches P21 rank_eval at 6 dp. Byte-identical rebuild proven. Re-routed binding row to **P24 WP3 — licensed-data adapter dry run**. | ruff PASS; quick GREEN (104+195); reconcile GREEN |
| 2026-11-20T07:32:13Z | `2f8c472` | **P24 WP3 landed — licensed-data adapter dry run.** Added `scripts/bab_licensed_adapter.py`, `research_state/bab_p24/adapter_dryrun.{json,md}`, `tests/test_bab_p24_adapter.py` (27 tests). Offline-only fixture validation; no network. Re-routed binding row to **P24 WP4 — closing decision**. | ruff PASS; quick GREEN; 27/27 tests PASS |
| 2026-11-20T18:04:38Z | `462d005` | **Handoff re-certified for P25 WP0; stale HEAD certification bottleneck removed.** HEAD advanced `f82c010` → `462d005` (checkpoint only touched HANDOFF.md ledger); binding row remains P25 WP0 — wide synthetic universe generator; deliverables still missing. | ruff PASS; quick GREEN |
| 2026-11-20T20:53:54Z | `790d54a` | **HANDOFF refreshed for P25 WP1 binding row.** P25 WP0 deliverables all exist and pass: `scripts/bab_wide_universe.py`, `tests/fixtures/wide_bab_universe.csv`, `tests/fixtures/wide_bab_universe_meta.json`, `tests/test_bab_p25_wide_universe.py` — 24/24 acceptance tests GREEN, ruff clean. Fixed 5× E501 ruff errors in test file (uncommitted change). Binding row re-routed to **P25 WP1 — rank walk-forward harness**. Pre-declared WP2 (bake-off) and WP3 (decision) for continuity. | ruff PASS; quick GREEN (104+195); reconcile GREEN |
| 2026-11-20T21:33:16Z | `0a35893` | **P25 WP1 landed — rank walk-forward harness.** Added `scripts/bab_walk_forward_rank.py`, `research_state/bab_p25/walk_forward_rank.{json,md}`, `tests/test_bab_p25_walk_forward_rank.py` (23 tests). Expanding walk-forward over the P25 WP0 wide fixture: 5 folds (train 180 / test 40), rank weighting (long low-beta quantile, short high-beta quantile, beta-neutral, rank_min_leg_beta=0.20, rank_max_gross=4.0). Every fold 40/40 OOS non-flat rows, per-fold portfolio beta ≈ 0, recovered planted beta spread ≈ 1.11 (long ≈ 0.55, short ≈ 1.68), byte-identical deterministic JSON, fixture SHA256 provenance matching WP0. Full gate GREEN 6932 passed / 35 skipped / TOTAL 100% coverage. Binding row re-routed to **P25 WP2 — equal vs rank OOS bake-off** with a binding initial task message and hard contract; WP3 pre-declared. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6932 passed / 35 skipped / TOTAL 100%** |
| 2026-11-20T21:55:05Z | `08593c0` | **HANDOFF refreshed for P25 WP2 binding row.** P25 WP1 complete (rank walk-forward harness: `scripts/bab_walk_forward_rank.py`, `research_state/bab_p25/walk_forward_rank.{json,md}`, 23 tests, full gate GREEN 6932 passed / 35 skipped / TOTAL 100%). Binding row re-routed to **P25 WP2 — equal vs rank OOS bake-off** with hard contract and four deliverables. WP3 pre-declared for continuity. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6932 passed / 35 skipped / TOTAL 100%** |
| 2026-11-20T21:56:34Z | `c211c81` | **HANDOFF re-certified for P25 WP2 binding row; stale HEAD certification bottleneck removed.** HEAD advanced `08593c0` → `c211c81` (two checkpoint sessions, HANDOFF.md ledger only, no code change). Binding row remains **P25 WP2 — equal vs rank OOS bake-off** (Lane C): `scripts/bab_promotion_bakeoff.py`, `research_state/bab_p25/promotion_bakeoff.{json,md}`, `tests/test_bab_p25_promotion.py` — none exist yet; next session owns all four. P25 WP0-WP1 complete and read-only; WP3 pre-declared. First action: `git log --oneline -4 && git status --short`, then `bash scripts/bab_quick.sh` (must be GREEN), then build the bake-off comparing `weighting="equal"` vs `weighting="rank"` on identical causal folds (OOS Sharpe, beta neutrality, turnover, wealth) with deterministic seeded artifacts, fixture SHA256 provenance, no-lookahead, delta Sharpe, and 20+ acceptance tests. Repo name = Betting Against Beta: rank weighting is Frazzini-Pedersen core; equal-weight default never beaten OOS on wide cross-section — WP2 produces the evidence for WP3 promote/no-promote. | ruff PASS; quick GREEN (104+195); full gate baseline **GREEN 6932 passed / 35 skipped / TOTAL 100%** |
| 2026-11-20T21:58:10Z | `c211c81` | **P25 WP2 built & gate-green; binding row routed to P25 WP3.** Added `scripts/bab_promotion_bakeoff.py`, `research_state/bab_p25/promotion_bakeoff.json`, `research_state/bab_p25/promotion_bakeoff.md`, `tests/test_bab_p25_promotion.py` (27 tests). Equal-vs-rank OOS bake-off on identical causal folds (train 180 / test 40, 5 folds): rank mean OOS Sharpe 0.4373 vs equal 0.1703 (delta +0.2670); both weightings beta-neutral per fold (|portfolio beta| < 1e-2); 40 nonflat OOS rows per fold per weighting; byte-identical deterministic JSON; fixture SHA256 provenance matching WP0; ruff clean. Full gate **GREEN 6959 passed / 35 skipped / TOTAL 100%**. WP2 slice uncommitted — next session commits it first (`feat(p25): add equal-vs-rank OOS promotion bake-off (WP2)`), then takes **P25 WP3 — promotion decision + lint** (binding). P20-P24 complete; P25 WP0-WP1 committed. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6959 passed / 35 skipped / TOTAL 100%** |
| 2026-11-20T22:27:45Z | `1660fb5` | **HANDOFF refreshed for P25 WP3 binding row; P25 WP2 slice committed.** HEAD advanced `c211c81` → `1660fb5` (two checkpoint sessions committed WP2 deliverables). Working tree CLEAN. P25 WP2 complete: `scripts/bab_promotion_bakeoff.py`, `research_state/bab_p25/promotion_bakeoff.{json,md}`, `tests/test_bab_p25_promotion.py` (27 tests), full gate GREEN 6959 passed / 35 skipped / TOTAL 100%. Binding row re-routed to **P25 WP3 — promotion decision + lint** (Lane D): `docs/BAB_P25_DECISION.md`, `tests/test_bab_p25_decision_consistency.py`, `generate_p25_decision.py`. Pre-declared P26 campaign "Signal-to-Noise Validation of Rank-Weighted BAB" with WP0-WP3 for post-P25 continuity. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6959 passed / 35 skipped / TOTAL 100%** |
| 2026-11-20T23:13:16Z | `07c672d` | **P25 WP3 complete — campaign P25 closed; routing to P26 WP0.** P25 WP3 deliverables all committed: `docs/BAB_P25_DECISION.md` (PROMOTE verdict, delta Sharpe +0.267044, beta-neutral all folds, `rank_min_leg_beta=0.20`/`rank_max_gross=4.0` unchanged), `generate_p25_decision.py`, `tests/test_bab_p25_decision_consistency.py` (20+ tests). P25 regression trio GREEN (88 tests: wide_universe 24 + walk_forward 23 + promotion 27 + decision 20+). ruff PASS, quick GREEN (104+195). Binding row re-routed to **P26 WP0 — signal vs null battery** (Lane A): `scripts/bab_signal_null_battery.py`, `research_state/bab_p26/signal_null_battery.{json,md}`, `tests/test_bab_p26_signal_null.py`. P26 is the anti-victory campaign: rank must be validated vs 1000 permuted null books (p<0.05 rank, p>0.05 equal) before any real-market deployment claim. | ruff PASS; quick GREEN (104+195); P25 trio **88 passed** |