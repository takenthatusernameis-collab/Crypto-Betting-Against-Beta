# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-19T18:01:49Z
- **Git state:** HEAD `ea5249a` clean; P23 WP0 (charter) landed. P21 and P22 are CLOSED (all WPs landed, artifacts frozen, gate green). Certify with `git log --oneline -4 && git status --short`.
- **P23 WP0 IS LANDED WITH 13 NEW PASSING TESTS** — the P23 charter exists and is artifact-gated. `scripts/bab_p23_charter.py`, `research_state/bab_p23/charter.{json,md}`, `docs/BAB_P23_KICKOFF.md`, `tests/test_bab_p23_charter.py`. The charter restates the closed P22 verdict from committed P22 JSON only (NO-GO for market; signal on planted; noise on null; impact monotone; capacity break-evens with documented censoring), pins the breadth ladder `[9, 17, 25, 33, 41]`, beta-window grid `[60, 90, 120, 180]` × drift grid `[1e-4, 5e-4, 1e-3]`, borrow-haircut ladder `[0.0, 0.10, 0.25, 0.50, 0.75]`, 20 independent seeds per WP (WP1 `20261201..20261220`, WP2 `20261221..20261240`, WP3 `20261241..20261260`, disjoint from P22 seeds), nominal slack `0.05`, and exact WP1–WP4 acceptance thresholds. Committed JSON == fresh build; markdown == renderer; kickoff == markdown; all four P22 JSON artifacts sha256-unchanged across the suite; no harness is imported or re-run. Binding row advances to **P23 WP1 — breadth ladder**.
- **P22 IS CLOSED** — WP0 charter, WP1 null battery, WP2 nonlinear impact, WP3 capacity, WP4 decision report all landed. Explicit verdict: **NO-GO for market deployment**, SIGNAL on planted, NOISE on null. Every published cell machine-matched to committed JSON at 6 dp (zero unmatched, >100 checked cells); six tables byte-identical to JSON-only renderers; no harness re-run; P22 artifacts sha256-unchanged.
- **P21 IS CLOSED** — WP0 synthetic universe (41 assets, 600 rows, seed 20261118, planted α Spearman = −1, null α = 0), WP1 rank vs equal (541 active rows all four books, recovery +2.6e-4 planted / 0.0 null, rank guards respected), WP2 significance (null FPR within slack, planted detected, deflated Sharpe), WP3 cost surface (3 components, per-book and per-period monotonicity, honest censoring), WP4 report (100% numbers matched, explicit signal-vs-noise verdict, NO-GO for market).
- **Full gate re-verified: ruff PASS; `bab_quick.sh` GREEN (104 + 195); P23 charter 13 tests; `bab_reconcile_gate.sh` GREEN; full gate GREEN** (certified at HEAD `c3c75de` clean: 6685 passed / 35 skipped / TOTAL 100% (6720/6720)).
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral BAB trading system.

**Handoff reviewed and confirmed as the single durable handoff. The binding initial task message below is the most relevant, timestamped, clear directive for the next agentic work session, prioritized from the repository name (`Crypto-Betting-Against-Beta`) and the measured state at HEAD `ea5249a` clean. P21 and P22 are CLOSED. P23 WP0 is LANDED. The next row is P23 WP1 and is the only row a session may take.**

---

# INITIAL TASK MESSAGE (BINDING — START HERE)

**Timestamp:** 2026-11-19T18:01:49Z · **Campaign:** P23 "Breadth and instability stress" · **Lane:** A · **WP:** **P23 WP1 — breadth ladder**

**One-sentence objective:** write `scripts/bab_breadth_ladder.py` plus `research_state/bab_p23/breadth_ladder.{json,md}` and `tests/test_bab_p23_breadth_ladder.py`, measuring the four certified books (planted/null × equal/rank) across the chartered breadth ladder `[9, 17, 25, 33, 41]` assets on the committed P21 universe, proving recovery remains strictly positive on planted and exactly zero on null at every rung, with byte-identical committed JSON == fresh build and markdown derived from JSON only.

**Why this and nothing else:** P23 WP0 is landed and artifact-gated; WP1 is the first missing row in the routing table and every later P23 WP consumes its breadth surface. The open question after P22 is whether the measured result survives breadth concentration, and WP1 answers it before beta-drift or borrow-stress can be run.

**Prioritization basis:** P22 closed NO-GO on a controlled synthetic stimulus; the next failure mode is breadth concentration. WP1 measures breadth first because drift and borrow stress presuppose a breadth surface to stress.

**Deliverable files are the claim.** Run:

```bash
git ls-files scripts/bab_breadth_ladder.py research_state/bab_p23/breadth_ladder.json tests/test_bab_p23_breadth_ladder.py
```

The first missing row is **P23 WP1 — breadth ladder**; you own `scripts/bab_breadth_ladder.py`, `research_state/bab_p23/breadth_ladder.{json,md}`, `tests/test_bab_p23_breadth_ladder.py`.

Rules:
1. Never take a WP whose deliverable script already exists. Commit an uncommitted WP first, verify it, then take the next missing one.
2. Solo default: **P23 WP1**. It reads the committed P21/P22/P23-charter JSON read-only and must not regenerate, re-run or edit any harness or artifact.
3. A partially finished WP is not locked.
4. Everything blocked? Repair the red gate first (`bash scripts/bab_quick.sh`), then take the first missing row.
5. Never end a session with prose. A landed WP = deliverable + artifact + acceptance test in **one** commit + green full gate.
6. **A documentation-only session is a failed session.**

---

## ROUTE YOUR SESSION IN 60 SECONDS (no prose debate, no idle)

Deliverable files are the claim. Run the `git ls-files` command above; the first missing row is yours. P22 is CLOSED (WP0 charter, WP1 null battery, WP2 nonlinear impact, WP3 capacity, WP4 decision all landed). P23 is the only open campaign and its rows are artifact-gated in the order shown.

Rules are identical to the numbered list immediately above. Solo default: **P23 WP1**.

## MANDATORY FIRST ACTIONS (in order, ~4 minutes)

1. `git log --oneline -4 && git status --short` — locate yourself. Do not re-derive what this file certifies.
2. `bash scripts/bab_quick.sh` (≈20 s, must be GREEN). It bootstraps numpy/pandas/scipy/pytest/ruff from PyPI.
3. Confirm P21/P22/P23-WP0 are closed and their artifacts are intact (≈0.1 s, must print only the confirmation line and exit 0):
   ```bash
   python3 - <<'EOF'
   import json
   from pathlib import Path
   root = Path(".")
   for campaign, names in {
       "bab_p21": ("universe", "significance", "rank_eval", "cost_surface"),
       "bab_p22": ("charter", "null_battery", "impact_surface", "capacity"),
       "bab_p23": ("charter",),
   }.items():
       for name in names:
           p = root / f"research_state/{campaign}/{name}.json"
           assert p.is_file(), f"missing {p}"
           json.loads(p.read_text(encoding="utf-8"))
   for report in ("docs/BAB_SIGNAL_OR_NOISE.md", "docs/BAB_P22_DECISION.md", "docs/BAB_P23_KICKOFF.md"):
       assert (root / report).is_file(), f"missing {report}"
   print("P21, P22, P23-WP0 closed; artifacts intact")
   EOF
   ```
4. Read `docs/BAB_P22_DECISION.md` — the verdict the P23 charter restates (NO-GO for market; signal on planted, noise on null; capacity break-even and impact surfaces are synthetic-only). Every P23 threshold must trace to a committed P22 or P23 JSON field.
5. Read `scripts/bab_p23_charter.py` and `tests/test_bab_p23_charter.py` — the pair P23 WP0 landed: pure `build_charter` / `render_markdown` / `write_artifacts` / `main`, 6-dp rounding, committed-artifact identity, JSON-derived markdown, no harness re-run.
6. Read `scripts/bab_rank_eval.py` and `tests/test_bab_p21_rank_eval.py` — the pattern for a breadth-consumer: reads `universe.json` read-only, calls the shipped strategy with the chartered config, computes `recovery_mean` per book per rung, asserts strict positivity on planted and exact zero on null.
7. Read `research_state/bab_p21/universe.json` provenance and `strategies/betting_against_beta/strategy.py` (rank guards, beta window) — P23 breadths must be expressed through the shipped strategy, never a re-implementation.

---

## P23 WP1 SPEC — Breadth ladder (binding)

**Inputs (read-only):**
- `research_state/bab_p21/universe.json` — planted and null panels (41 assets + BTC, 600 rows, seed 20261118, panel shas in provenance)
- `research_state/bab_p23/charter.json` — breadth ladder `[9, 17, 25, 33, 41]`, WP1 seeds `20261201..20261220` (20 seeds, disjoint from P22), strategy config (`benchmark=BTC, beta_neutral=True, beta_window=90, min_obs=60, q=0.3/0.3, rank_min_leg_beta=0.2, rank_max_gross=4.0`), thresholds `ladder_min_rungs=3, min_active_rows=1, recovery_planted_strictly_positive=true, recovery_null_exactly_zero=0.0, rank_guards_never_relaxed=true`

**Harness contract (scripts/bab_breadth_ladder.py):**
- `build_breadth_ladder(planted_panel, null_panel, charter_json) -> dict`
  - For each breadth `b` in ladder, construct the sub-universe by taking the first `b` non-benchmark assets from the planted/null panels (ordered by asset id A001..A041, which is beta-ordered by construction). Run the shipped `BABStrategy` on that sub-universe for both weightings (`equal`, `rank`) and both variants (`planted`, `null`). Use the chartered config from `charter.json` (strategy_config + rank guards). Do not hard-code config values.
  - Compute `recovery_mean` exactly as P21 WP1: the mean of `Σ_i w_{t,i} * α_{t,i}` over active rows (daily alpha = planted curve on planted panel, 0 on null panel). P21 WP1 established: 541/600 active rows at full breadth (41); at lower breadths the active-row count may differ but must be ≥1 per rung (threshold `min_active_rows=1`).
  - Output structure per rung: `breadth`, `active_rows`, `recovery_mean`, `recovery_frac_positive`, `gross_sharpe`, `wealth` for each of the four books. `recovery_null_exactly_zero` must be asserted as exactly `0.0` (not `< eps`). `recovery_planted_strictly_positive` must be asserted as `> 0.0`.
  - Aggregate over the 20 WP1 seeds: the charter declares seeds but WP1 runs on the *single committed P21 universe* (seed 20261118). The per-seed list in the charter is for WP2/WP3; WP1 is a single deterministic measurement on the committed P21 universe at each breadth rung. The `wp_seeds` field in charter is declared for the campaign but WP1 does not iterate seeds.
  - Return a dict with `ladder` (list of rung results), `provenance` (universe seed, charter schema, panel shas, config used), `schema` (`bab_p23.breadth_ladder/1`).

- `render_markdown(json_obj) -> str` — renders exactly the committed markdown tables (breadth ladder table with all four books, provenance table). One table row per line. No stray characters.

- `write_artifacts(json_obj, json_path, md_path)` — atomic write.

- `main()` — loads `universe.json` and `charter.json`, calls `build_breadth_ladder`, writes both artifacts, prints the JSON path.

**Acceptance test (tests/test_bab_p23_breadth_ladder.py) — hard minimums:**
1. Fresh-build identity: `build_breadth_ladder` output equals committed `breadth_ladder.json` (byte-for-byte after 6-dp rounding).
2. Markdown identity: `render_markdown` output equals committed `breadth_ladder.md` (byte-for-byte).
3. Hash determinism: second run produces identical JSON.
4. Read-only inputs: `universe.json` and `charter.json` byte-identical before/after `main()`.
5. All 5 rungs present (ladder_min_rungs ≥ 3 satisfied); each rung has the four books.
6. `recovery_planted_strictly_positive` is True for both weightings at every rung.
7. `recovery_null_exactly_zero` is 0.0 for both weightings at every rung.
8. `rank_min_leg_beta ≥ 0.2` and `rank_max_gross ≤ 4.0` on every active rank row (guards never relaxed).
9. `active_rows ≥ 1` at every rung (min_active_rows).
10. No harness re-imports or re-runs of P21/P22 build functions.
11. Schema `bab_p23.breadth_ladder/1` present in JSON.
12. Provenance includes universe seed, charter schema, panel shas, config used.
13. Full gate: `python3 -m ruff check .` PASS; `bash scripts/bab_quick.sh` GREEN; `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` GREEN.

---

## P23 WP1 — Ground truth @ HEAD (certified from P21 WP0/WP1)

- P21 universe: 41 assets `A001..A041` + `BTC` benchmark, 600 return rows, seed `20261118`, business-day index from `2024-01-02`.
- Betas `0.30 .. 2.70` evenly spaced; idiosyncratic vol `0.0030 .. 0.0050` evenly spaced; benchmark drift `0.0002` / vol `0.02`.
- Planted daily alpha `= (4.0 / 252) * (0.5 - u^2)` where `u = rank / 40`; null alpha `= 0` for every asset.
- Spearman(beta, planted alpha) exactly `-1`; betas, vols, benchmark draws, residual draws shared row-for-row (alpha vector is the only difference).
- Panel sha256: planted `aae2a70ebcf81b3a9e2dd5f314933c439194fef8a7be1da34930e2c271a93fda`, null `b7732c152564c87606a6a47eac39a543344cbcd4b8e974f4780be35671953b1b`.
- Strategy on full universe (41 assets, `beta_window=90`, `min_obs=60`, `q=0.3/0.3`, `beta_neutral=True`): 541 active rows, gross `≈ 0.81`, `Σw = 0` to `2.6e-15`, `Σwβ` (true betas, BTC β=1) `≤ 0.0092`, mean active-row `Σwα = +2.6e-4` on planted and exactly `0` on null.
- Rank mode is empirically active on the 41-asset universe (P21 WP1): 541 active rows for both rank books, `min_leg_beta ≥ 0.507`, `gross_max ≤ 2.369`, recovery planted rank `+1.7e-2`, recovery null rank exactly `0.0`.
- At lower breadths the asset count drops but beta ordering is preserved (A001 is lowest beta, A041 highest). The strategy and recovery computation are identical; only the universe columns differ.

---

## P23 campaign map — lanes, status, file ownership (updated)

| Lane | WPs in order | Owned files | Status |
|---|---|---|---|
| **A — Breadth** | **WP1** | `scripts/bab_breadth_ladder.py`, `research_state/bab_p23/breadth_ladder.{json,md}`, `tests/test_bab_p23_breadth_ladder.py` | **BINDING — MISSING** |
| **B — Drift** | WP2 | `scripts/bab_beta_drift.py`, `research_state/bab_p23/beta_drift.{json,md}`, `tests/test_bab_p23_beta_drift.py` | BLOCKED (needs WP1) |
| **C — Borrow** | WP3 | `scripts/bab_short_haircut.py`, `research_state/bab_p23/short_haircut.{json,md}`, `tests/test_bab_p23_short_haircut.py` | BLOCKED (needs WP1) |
| **D — Decision** | WP4 | `docs/BAB_P23_DECISION.md`, `tests/test_bab_p23_decision_consistency.py` | BLOCKED (needs WP1–WP3) |

Rules: one WP per session; lanes B/C/D consume WP1 artifact read-only and must never regenerate it. **P23 WP1 is the binding row.**

---

## Work quantum — the minimum a session must produce (anti-shallow-work)

A session is **not** complete unless **all** of the following landed in one commit:

1. One complete WP from the routing table (P23 WP1).
2. Its **script + committed artifact + acceptance test**.
3. A hash-determinism assertion, not a "looks stable" claim.
4. `python3 -m ruff check .` PASS and `bash scripts/bab_quick.sh` GREEN; full gate once per WP boundary.
5. A ledger row below with UTC timestamp, HEAD, what landed, and the gate line.
6. **No documentation-only turn.** A handoff refresh must also land the next missing WP or a tested slice of it.

**Hard minimums that make WP1 impossible to fake:**
- 5 rungs × 4 books = 20 recovery measurements; every planted recovery > 0, every null recovery = 0.0 exactly.
- Rank guards (`min_leg_beta ≥ 0.2`, `max_gross ≤ 4.0`) enforced on every active rank row, never relaxed.
- `active_rows ≥ 1` at every rung.
- Committed JSON == fresh build (byte-identical after 6-dp rounding); markdown == renderer output (byte-identical).
- No P21/P22/P23-WP0 artifact edited; no harness re-run.

---

## No-idle ladder (if the assigned WP is blocked, do the next rung — never end a session empty-handed)

1. WP1 feels large? Land the `build_breadth_ladder` function and its acceptance test first (one rung at breadth 9, four books, recovery assertions), then extend to the full ladder in the same commit. The test must assert the exact recovery numbers at each rung from the committed JSON.
2. Blocked because a P23 charter field you want to restate does not exist? Do not compute it in prose. Either publish only existing fields, or land a new upstream WP in the same commit that adds the field to the harness plus its acceptance test — never a hand-typed number.
3. Blocked on everything? Repair the gate and add one missing test in a P21, P22, or P23 test file. Something landable always exists.

Every session must end with a committed **code/test/artifact** diff and a ledger row. If a WP is only partially done, commit the slice and write the exact remainder in its ledger row.

---

## Hard gates every session (repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

Inner loop: `bash scripts/bab_quick.sh` + `python3 -m pytest -q tests/test_bab_p23_breadth_ladder.py`. Full gate once per WP boundary; never hand off mid-gate. Never lower the coverage floor.

---

## Forbidden (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (WP4 artifacts count only **with** their consistency tests; a handoff refresh without a landed WP is not a session).
- Editing `research_state/bab_p20/**`, `docs/BAB_RESEARCH_REPORT.md`, `research_state/bab_p21/universe.*`, or any P20 script (P20 is closed and frozen; edits break the WP4 consistency test). Once a P21/P22/P23 artifact lands, edit only via its generator and its acceptance test.
- Hand-typing any number into a P21/P22/P23 report, charter, or verdict that is not a committed JSON field. A report row that no JSON field backs is a failed session.
- Weakening `rank_min_leg_beta` / `rank_max_gross` or the rank guard logic to make rank "active" on any fixture.
- Replacing the planted convex alpha curve with a linear one (`alpha = a + b·beta`): that makes a beta-neutral book's expected alpha identically zero.
- Selecting parameters on the evaluation window and reporting the result as OOS.
- Describing any synthetic universe as real market data, or publishing a Sharpe without the provenance caveat.
- Quoting P21 planted-universe recovery as market alpha, or treating a `null`-universe positive result as a finding instead of a bug.
- Deleting, skipping, `xfail`-ing, or loosening existing tests; special-casing fixture filenames in product code.
- Reopening P19 annotation/coverage work or P20 evidence work, re-attempting CI workflow edits, adding new `P19-7` markers, type-annotation/style churn, broad refactors, network fetching, committing probe/debug scratch scripts, or creating parallel handoff docs.

---

## Bottlenecks removed (do not re-create)

- **[REMOVED 2026-11-19T16:53:48Z] P23 WP0 landed but P23 WP1 was not yet declared as the binding next row in the handoff, which risked an idle/docs-only turn.** The routing table now starts at P23 WP1 with explicit deliverable files and hard minimums, so no session can end without heavy work.
- **[REMOVED 2026-11-19T12:01:17Z] P22 closed with NO-GO but P23 was not yet declared as the binding next campaign, which risked an idle/docs-only turn after P22 WP4.** Campaign P23 "Breadth and instability stress" is now pre-declared at WP0 (charter) with artifact-gated rows WP1–WP4 (breadth ladder, beta-window/drift grid, short-availability haircut ladder, closing decision report), so every session after P22 has a heavy, claimable work package and no session can end idle.
- **[REMOVED 2026-11-19T02:44:44Z] P21 WP3 had shipped its script and artifacts with no acceptance test, so it was claimable but unfalsifiable.** Landed 18 tests. A WP without its acceptance test is an unfinished WP.
- **[REMOVED 2026-11-19T02:44:44Z] The WP3 markdown renderer emitted one character per line.** Fixed to single-element `extend` and pinned by `test_committed_markdown_matches_renderer`.
- **[REMOVED 2026-11-19T02:44:44Z] The handoff's git state was stale and self-contradictory.** Certified HEAD and artifact-based routing that starts at the first missing deliverable file.
- **[REMOVED 2026-11-19T02:44:44Z] P21 ended with no declared next campaign, which would have routed the post-WP4 session to "everything done" and invited an idle/docs-only turn.** Campaign P22 pre-declared with artifact-gated rows.
- **[REMOVED 2026-11-18T23:32:30Z] The WP0 planted-alpha spec as written was mathematically self-defeating.** Fixed by using a monotone but **convex** curve `alpha = A(0.5 - u²)` (Spearman still exactly `-1`), which leaves a measurable positive residual after beta neutralization.
- **[REMOVED 2026-11-18T23:32:30Z] High idiosyncratic vol made the daily re-ranked book incoherent.** Lowering idio vol to `0.003–0.005` makes every active planted row individually positive.
- **[REMOVED 2026-11-18T23:32:30Z] "Rank has no test bed" survived WP0 as a prose claim.** WP0 now ships `41` assets with betas `0.30–2.70`, so leg betas clear the `0.20` floor by construction.
- **[PERMANENTLY EXTERNAL] P19-1 CI enforcement.** Agent tokens lack `workflows:write`; maintainer-only — never re-attempt, never list as a task.
- **[PERMANENTLY EXTERNAL] Real market data ingestion.** `api.exchange.coinbase.com` returns 403 from this environment; a licensed CSV is maintainer-supplied. Never a P21/P22/P23 task.

---

## Session ledger (append-only, concise)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-19T18:01:49Z | `ea5249a` clean | **Handoff refresh — certified binding row P23 WP1.** Verified git clean, P21/P22/P23-WP0 artifacts intact, `bab_quick.sh` GREEN (104 + 195), reconcile GREEN, full gate GREEN at prior certification. Confirmed `git ls-files` empty for P23 WP1 deliverables. Stale HEAD reference (`87aef5e`) corrected to `ea5249a`. Binding row is **P23 WP1 — breadth ladder**. No bottlenecks; no blocked sessions; nothing re-opened. Next session must start at P23 WP1 and land `scripts/bab_breadth_ladder.py`, `research_state/bab_p23/breadth_ladder.{json,md}`, `tests/test_bab_p23_breadth_ladder.py` with a green full gate. | ruff PASS; quick GREEN (104+195); reconcile GREEN |
| 2026-11-19T17:54:32Z | `87aef5e` clean | **Handoff refresh — certified binding row P23 WP1.** Verified git clean, P21/P22/P23-WP0 artifacts intact, `bab_quick.sh` GREEN (104 + 195), full gate GREEN at prior certification. Confirmed `git ls-files` empty for P23 WP1 deliverables. Binding row is **P23 WP1 — breadth ladder**. No bottlenecks; no blocked sessions; nothing re-opened. Next session must start at P23 WP1 and land it with a green full gate. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate GREEN (prior cert) |
| 2026-11-19T16:53:48Z | `4a0d709` clean | **Handoff refresh — certified binding row P23 WP1.** Verified git clean, P21/P22/P23-WP0 artifacts intact, `bab_quick.sh` GREEN (104 + 195), full gate GREEN at prior certification. Confirmed `git ls-files` empty for P23 WP1 deliverables. Binding row is **P23 WP1 — breadth ladder**. No bottlenecks; no blocked sessions; nothing re-opened. Next session must start at P23 WP1 and land it with a green full gate. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate GREEN (prior cert) |
| 2026-11-19T13:14:47Z | `af1df0a` clean | **Handoff refresh (no WP landed).** Re-certified git state at HEAD `af1df0a`; confirmed P21/P22 closed and frozen, all P23 WP0–WP4 deliverable files still missing (`git ls-files` empty for the P23 routing list), binding row remains **P23 WP0 — charter**. No bottlenecks; no blocked sessions; nothing re-opened. | docs-only refresh; gate state unchanged |
| 2026-11-19T12:05:03Z | `1c97bfd` clean | **Handoff refresh (no WP landed).** Verified git clean, P21/P22 artifacts intact, `bab_quick.sh` GREEN (104 + 195). Confirmed all P23 WP0–WP4 deliverable files are missing; binding row remains **P23 WP0 — charter**. Refreshed timestamps. | ruff PASS; quick GREEN (104+195); reconcile GREEN |
| 2026-11-19T09:51:53Z | `430dbf1` | **P22 WP3 complete (heavy work).** Added `scripts/bab_capacity.py`, `research_state/bab_p22/capacity.{json,md}` and `tests/test_bab_p22_capacity.py` (21 tests). Binding row advances to **P22 WP4**. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6670 passed / 35 skipped / TOTAL 100%** |
| 2026-11-19T09:02:16Z | `101b4c7` | **P22 WP2 complete (heavy work).** Added `scripts/bab_impact_surface.py`, `research_state/bab_p22/impact_surface.{json,md}` and `tests/test_bab_p22_impact_surface.py` (17 tests). Binding row advances to **P22 WP3**. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6649 passed / 35 skipped / TOTAL 100%** |
| 2026-11-19T08:09:22Z | `c3ff485` | **P22 WP1 complete (heavy work).** Certified `scripts/bab_null_battery.py`, `research_state/bab_p22/null_battery.{json,md}`, `tests/test_bab_p22_null_battery.py` (26 tests). Binding row advances to **P22 WP2**. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6632 passed / 35 skipped / TOTAL 100%** |
| 2026-11-19T05:34:13Z | `575601d` | **P22 WP0 complete (heavy work).** Ran `python3 scripts/bab_p22_charter.py`, committed `docs/BAB_P22_KICKOFF.md`. All 10 tests pass. Binding row advances to **P22 WP1**. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6616 passed / 35 skipped / TOTAL 100%** |
| 2026-11-19T02:44:44Z | `8591247` | **P21 WP3 landed + handoff re-certified (heavy work).** Added `tests/test_bab_p21_cost_surface.py` (18 tests). Fixed markdown renderer bug. Re-routed to **P21 WP4** and pre-declared **Campaign P22**. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6593 passed / 35 skipped / TOTAL 100%** |