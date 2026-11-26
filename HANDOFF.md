# DURABLE HANDOFF — Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-26T03:55:41Z
**Session:** Kilo General Agent Loop — Next Activation (Campaign P40 initial task — MANDATORY)
**Repository:** Crypto-Betting-Against-Beta (Betting Against Beta crypto quant research)
**Verified baseline:** HEAD `4a6f9d9`, working tree clean. Every claim below was re-checked
against the live repo this session: P40 is ABSENT (no `research_state/bab_p40/`, no
`scripts/bab_p40_*`, no `tests/test_bab_p40_*`, no `generate_p40_decision.py`, no
`docs/BAB_P40_DECISION.md`); P38 `campaign_verdict=SURVIVES_DEFLATION` with
`trial_enumeration.n_trials_total=552`; P39 regime `DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`;
P39 cross `DOES_NOT_REPLICATE`. All reference scripts/tests/registries named below exist.
**Supersedes:** all prior HANDOFF.md content. Campaign B / P37 regime-conditional is CLOSED.
P20–P39 are COMPLETE and FROZEN. The single binding campaign is **P40** below.

---

## READ FIRST — ANTI-SPIN CONTRACT (the reason this file keeps getting rewritten)

Recent sessions (commits `4ab4539`..`4a6f9d9`, ~8 sessions in one hour) changed **only this
file** and produced **zero** P40 artifacts. That is a FAILED session. Do not repeat it.

**The only acceptable outcome of the next session is P40 artifacts on disk plus passing fast
gates.** Concretely, a session is successful ONLY if all of these are true at exit:

1. `scripts/bab_p40_meta_analysis.py` exists and runs.
2. `research_state/bab_p40/meta_summary.json` and `.md` exist and are byte-stable.
3. `generate_p40_decision.py` exists and `docs/BAB_P40_DECISION.md` is generated from the JSON.
4. `tests/test_bab_p40_meta_analysis.py` and `tests/test_bab_p40_decision_consistency.py` pass.
5. The replay registries (`bab_replay_full.py`, `bab_replay_decisions.py`) and their guards
   (`test_bab_p29_replay_coverage.py`, `test_bab_p29_decision_replay.py`) include P40.
6. `bash scripts/bab_quick.sh` is GREEN and the targeted P40/registry pytest commands pass.

**Editing HANDOFF.md without landing items 1–6 is forbidden.** Do not commit a handoff-only
change. Do not spend the session re-validating frozen P20–P39, re-running the 56-minute gate,
or asking which option to pick. The work is fully specified below and a working blueprint
(`scripts/bab_p39_cross_fixture.py`) already exists — copy it and generalize. Execute.

---

## INITIAL TASK FOR THE NEXT SESSION (execute this, do not explore)

You are the next agentic work session for **Crypto-Betting-Against-Beta**. The repository's
core deliverable is a trustworthy BAB verdict for crypto. P38 says the factor survives pooled
deflation on one synthetic fixture; P39 WP1 finds high-vol regime failures and P39 WP2 finds
non-replication on a second fixture. **Your initial and only research task is to execute
Campaign P40: Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict.**

Start by creating `scripts/bab_p40_meta_analysis.py` by generalizing
`scripts/bab_p39_cross_fixture.py` (the closest working template) to the four fixed fixtures
below. P40 is a heavy, deterministic, offline research campaign with four work packages
(WP0–WP3), byte-stable artifacts, a decision document, replay registration, tests, and
fast-gate verification. Complete all four work packages and update this file with the outcome
before exiting. If the evidence is negative, publish the negative verdict honestly; do not
tune fixtures to chase a positive result.

**Binding definition of done:** WP0–WP3 all land; `research_state/bab_p40/meta_summary.json`
and `.md` are byte-stable; `docs/BAB_P40_DECISION.md` is generated from committed JSON;
`generate_p40_decision.py` and all new artifacts are replay-registered; the new consistency
and registry tests pass; `bash scripts/bab_quick.sh` is GREEN; and this HANDOFF.md records the
per-fixture DSR table, consolidated verdict, test evidence, and next state.

---

## PROJECT STATE SUMMARY (verified this session, HEAD `4a6f9d9`)

Systematic quantitative research implementing the **Betting Against Beta (BAB)** strategy
(Frazzini & Pedersen) for cryptocurrencies on deterministic synthetic fixtures. These are
**NOT real market data**; never present results as real-world profitability or market alpha.

**Phase status — P20–P39 are COMPLETE and FROZEN. Do not reopen.**

| Phase | Campaign | Verdict | Key Finding |
|-------|----------|---------|-------------|
| **P38 WP1** | Deflated Significance (n_trials=552) | **SURVIVES_DEFLATION** | Default (β=90,q=0.3,equal) DSR=0.921; best in-sample (β=180,q=0.2) DSR=0.944 |
| **P39 WP1** | Regime-Conditional Deflation | **DOES_NOT_SURVIVE_IN_SOME_REGIME** | `bear_mid_vol` 3/8 survive (DSR 0.35); `bull_high_vol`/`bull_mid_vol` 4/8 (DSR 0.53); low-vol regimes 5–6/8 |
| **P39 WP2** | Cross-Fixture Replication (2nd universe) | **DOES_NOT_REPLICATE** | Only 3/8 survive; mean DSR 0.396 (< 0.5) |
| **P39 WP0** | Full-Gate Close-Out (100% cov) | **GREEN (committed)** | `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` exit 0, TOTAL 100%, 7675 passed/39 skipped, ~56 min. Commit `098a3a4` is ancestor of HEAD. |
| **P36** | Rank-Weighted vs Equal-Weight | **RANK UNDERPERFORMS** | Negative Sharpe, higher vol, worse maxDD. Dead end — do not pursue. |

**One-line verdict:** BAB survives pooled deflation on the primary synthetic fixture but fails
in high-vol regimes and fails to replicate on a second independent fixture. P40 must resolve
this contradiction with a multi-fixture meta-analysis and one consolidated verdict.

---

## BOTTLENECKS — CURRENT STATUS (read before acting)

**Bottleneck 1 (RESOLVED): full gate cannot complete in one tool window.** P39 WP0 already ran
the full 100%-coverage gate GREEN and committed it. **Do NOT rerun `scripts/bab_gate.sh` to
verify P39 WP0.** If a future maintainer explicitly needs it, use `background_process monitor`
with `timeout: 600000` and re-invoke `logs`; a bare `bash` call can be killed mid-run and leave
spurious coverage-only failures plus P27/P30 newline side-effects. Restore those side-effects
with `git checkout -- research_state/bab_p27/ research_state/bab_p30/`.

**Bottleneck 2 (ACTIVE — the reason P40 is stuck): no P40 artifacts exist, and prior sessions
only rewrote this file.** `research_state/bab_p40/` does not exist, and no P40 generator/test/doc
is present. This is the gap the next session must close with heavy, real work. The exact P40
contract is below, and `scripts/bab_p39_cross_fixture.py` is a complete working blueprint.

**Bottleneck 3 (CLOSED): rank weighting.** P36 proved it strictly worse. Never reopen.

**Bottleneck 4 (CLOSED): regime coverage gap.** All six regimes have `n_ok_cells = 8` in
`research_state/bab_p39/regime_summary.json`; do not re-litigate the old bear_high_vol gap.

**Bottleneck 5 (EXTERNAL / maintainer-only): CI workflow enforcement is not agent-fixable.**
`.github/workflows/main.yml` does not invoke ruff/full gate/reconcile gate, and the repo token
lacks `workflows:write`. Do not burn a session trying to push a workflow change. Record it as a
maintainer action; local gates remain the agent-executable proof.

---

## NEXT FOCUS CAMPAIGN — MANDATORY, SINGLE TASK (NO EXPLORATION, NO OPTIONS)

### CAMPAIGN P40 (MANDATORY): Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict

**Goal:** Determine whether P38's pooled survival is a genuine factor property or an artifact
of one synthetic fixture, using at least four independent deterministic parameterizations and
a single honest consolidated verdict.

**Non-negotiable rules:**

- Do not reopen P20–P39 or edit frozen artifacts/scripts.
- Do not rerun the full 56-minute gate; P39 WP0 is already GREEN.
- Do not add synthetic fixtures beyond the four P40 fixtures specified below.
- Do not use real-data claims: all P40 inputs are synthetic and must be labelled as such.
- Do not tune seeds/parameters after seeing results to obtain a preferred verdict.
- Do not hand-edit generated JSON/Markdown; change generators and regenerate.
- Do not commit unless the user explicitly asks; leave the worktree ready for inspection.
- **Do not rewrite this HANDOFF.md without landing the artifacts (see Anti-Spin Contract).**

### WP0 — Implement the deterministic meta-analysis generator

Create `scripts/bab_p40_meta_analysis.py` as a standalone entry point. **Copy the structure of
`scripts/bab_p39_cross_fixture.py`** (it already implements the full pipeline: fixture build,
rolling-OLS beta, equal-weight beta/dollar-neutral portfolio, DSR/PSR deflation over the
read-only `n_trials_total=552`, tail metrics, neutrality invariants, rounding, byte-stable
JSON+Markdown, `--check-*` flag) and generalize the single fixture into the following **four
fixed fixtures** (8 seeds each; 32 total cells):

| Fixture | Base seed | Increment | Idio vol | Beta range | Assets | Role |
|---|---:|---:|---:|---:|---:|---|
| F1_PRIMARY | 20261120 | 1009 | 0.003 | 0.35–1.90 | 40 | P38/P39 WP1 primary parameterization |
| F2_P39_SECOND | 20270101 | 9973 | 0.006 | 0.20–2.40 | 32 | P39 WP2 second parameterization |
| F3_LOW_VOL_WIDE | 20280201 | 10009 | 0.002 | 0.25–2.10 | 36 | Low-idio, wider beta cross-section |
| F4_HIGH_VOL_NARROW | 20290301 | 10007 | 0.008 | 0.40–1.70 | 28 | High-idio, narrower beta cross-section |

For every fixture use 8 seeds (`base + increment * i`, `i=0..7`), the read-only BTC column from
`tests/fixtures/wide_bab_universe.csv`, asset returns `beta * BTC_return + seeded idio`, and the
shipped-default BAB config: beta_window=90, quantile=0.3, equal-weight, beta-neutral,
dollar-neutral, zero transaction costs. Compute per cell: Sharpe, DSR (deflate over the
read-only `n_trials_total=552` at JSON path `trial_enumeration.n_trials_total` in
`research_state/bab_p38/deflated_summary.json`), PSR, annualized volatility, max drawdown,
turnover, tail metrics consistent with P39, and all three neutrality invariants (model beta
<= 1e-3, dollar <= 1e-9, |realized beta| <= 0.15).

Aggregate per fixture and across fixtures: `n_cells`, `n_ok_cells`, `n_error_cells`,
`n_survive`, mean/min/max DSR/PSR/Sharpe, `all_survive`, `all_neutrality_ok`, and the fraction
of fixtures whose P38 pooled verdict (`SURVIVES_DEFLATION` + `ALL_NEUTRALITY_OK`) replicates.

Emit exactly one consolidated verdict from this fixed enum:

- `ROBUST_ACROSS_FIXTURES`: all four fixtures replicate the P38 pooled verdict.
- `FRAGILE_FIXTURE_DEPENDENT`: at least one but fewer than four fixtures replicate.
- `DOES_NOT_REPLICATE`: no fixture replicates.

Include an honest `campaign_verdict_reason` that cites the fixture counts and DSR evidence.
Use deterministic seeds, sorted JSON keys, fixed/rounded floats, and byte-stable Markdown.

### WP1 — Publish byte-stable research artifacts

Generate and commit-ready (do not commit unless asked):

- `research_state/bab_p40/meta_summary.json`
- `research_state/bab_p40/meta_summary.md`

The JSON must include schema `bab_p40.meta_analysis/1`, provenance (generator, campaign, WP,
synthetic caveat, fixture path, return/BTC SHA-256, exact seeds, exact config grid, neutrality
tolerances, bootstrap settings, DSR threshold, read-only deflation source), per-fixture results,
32 per-cell results, cross-fixture aggregates, and the consolidated verdict. The Markdown must
contain the per-fixture parameter table, per-cell DSR table, aggregate table, consolidated
verdict, and the synthetic-data caveat. Match the formatting style of existing
`research_state/bab_p*/*.json` and `.md` files.

### WP2 — Add the decision document and generator

Create `generate_p40_decision.py` and generate `docs/BAB_P40_DECISION.md` **only from the
committed P40 JSON**. Every published table number must be a JSON leaf; no hand-typed result
numbers. The document must state the explicit consolidated verdict, the per-fixture evidence,
the decision criteria, what P40 does not prove (no real-market alpha), and the next state.
Follow the structure of `generate_p39_decision.py` / `docs/BAB_P39_DECISION.md`.

### WP3 — Wire tests, replay registries, and fast verification

Add `tests/test_bab_p40_meta_analysis.py` and
`tests/test_bab_p40_decision_consistency.py` (mirror the P39 tests). Pin the schema, exact
fixture grid, 32-cell completeness, neutrality, DSR/PSR bounds, deterministic rebuild,
byte-identical `--check-meta-summary`, committed JSON/Markdown identity, decision-doc/JSON
consistency, and the no-harness/no-hand-edit guard. Add a ruff check for the new files.

Update the exact replay registries and their guards:

- `scripts/bab_replay_full.py`: register `bab_p40/meta_summary.json` as JSON-only,
  `no_xproc=True`, build `build_summary`.
- `tests/test_bab_p29_replay_coverage.py`: add `meta_summary` to `EXPECTED_NAMES`.
- `scripts/bab_replay_decisions.py`: register `p40_decision.md` from
  `generate_p40_decision` with output `docs/BAB_P40_DECISION.md`.
- `tests/test_bab_p29_decision_replay.py`: add `p40_decision.md` to `EXPECTED_NAMES`.
- `scripts/bab_gate.sh`: add a P40 block that runs `--check-meta-summary`, the two P40 test
  files, and the P40 decision replay/consistency check. Keep P39 and earlier blocks intact.
- If `scripts/bab_replay_decisions.py --check-doc-summary` changes the committed P32 summary,
  regenerate that summary through its generator and include it; do not hand-edit it.

Fast verification (required; do not run the full gate):

```bash
python -m pytest -x -q tests/test_bab_p40_meta_analysis.py tests/test_bab_p40_decision_consistency.py
python -m pytest -x -q tests/test_bab_p31_registry_completeness.py tests/test_bab_p32_decision_registry_completeness.py tests/test_bab_p29_replay_coverage.py tests/test_bab_p29_decision_replay.py
python scripts/bab_p40_meta_analysis.py --check-meta-summary
python scripts/bab_replay_decisions.py --subset p40_decision.md
bash scripts/bab_quick.sh
```

Restore any P27/P30 newline side-effects before finalizing. Do not claim completion until the
commands above pass and the artifacts are byte-stable.

---

## CONTEXT FOR NEXT AGENT

- **Repository root:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
- **KEY BLUEPRINT:** `scripts/bab_p39_cross_fixture.py` — a complete, working single-fixture
  generator (fixture build, beta, portfolio, DSR/PSR deflation, tail, neutrality, byte-stable
  JSON/MD, `--check-cross-fixture-summary`). Generalize its constants + loop to the four P40
  fixtures. Its `--check-cross-fixture-summary` flag is the naming model for `--check-meta-summary`.
- **Other prior scripts:** `scripts/bab_p39_regime_conditional.py` (regime labels),
  `scripts/bab_p38_deflated_significance.py` (DSR/deflation math; read-only n_trials).
- **Reference tests:** `tests/test_bab_p39_cross_fixture.py`,
  `tests/test_bab_p39_decision_consistency.py`, `tests/test_bab_p29_replay_coverage.py`,
  `tests/test_bab_p29_decision_replay.py`.
- **Key config:** `strategies/betting_against_beta/config.py` (BABConfig),
  `strategies/betting_against_beta/strategy.py` (BABStrategy).
- **Fixtures:** `tests/fixtures/wide_bab_universe.csv` (BTC + 40 synthetic assets,
  deterministic seed 20261120). All P40 fixtures are deterministic synthetic random walks.
- **Read-only trial count:** `n_trials_total=552` at `trial_enumeration.n_trials_total` in
  `research_state/bab_p38/deflated_summary.json` — never re-enumerate.
- **Fast verify:** `bash scripts/bab_quick.sh` plus the targeted P40/registry tests. **Not** the
  full gate.
- **Current artifacts:** `research_state/bab_p39/regime_summary.json` (high-vol failure),
  `research_state/bab_p39/cross_fixture_summary.json` (non-replication),
  `research_state/bab_p38/deflated_summary.json` (pooled survival).

---

## IF P40 PRODUCES AN HONEST NEGATIVE VERDICT

If the consolidated verdict is `DOES_NOT_REPLICATE` or `FRAGILE_FIXTURE_DEPENDENT`, that is a
valid, publishable honest result. Record it, write the P40 decision document, and set the next
state to a terminal summary consolidating P38–P40. Do not invent new fixtures or reopen frozen
phases to chase a positive result. Only `ROBUST_ACROSS_FIXTURES` justifies a follow-on real-data
validation campaign, and only with explicit maintainer approval; the committed
`tests/fixtures/real_market_prices.csv` is also synthetic.

---

**This handoff is durable. The next agent reads this file, executes Campaign P40 WP0–WP3 as the
initial task, completes the heavy work fully, verifies with the fast commands above, and updates
this file with the outcome before exiting. Do not run the full 56-minute gate. Do not reopen
P20–P39. Do NOT rewrite this file without landing P40 artifacts — a handoff-only commit is a
failed session.**