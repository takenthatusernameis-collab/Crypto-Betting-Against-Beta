# DURABLE HANDOFF — Crypto-Betting-Against-Beta
**Timestamp (UTC): 2026-11-26T08:51:25Z**
**Session:** Kilo General Agent Loop — P41 COMPLETE (WP1/WP2/WP3); **P42 OPEN (sole binding row)**
**Repository:** Crypto-Betting-Against-Beta (Betting Against Beta crypto quant research)
**Verified baseline (HEAD `01d3603`, re-verified this session at 08:51:25Z):**
- `python3 -m ruff check .` GREEN (`All checks passed!`).
- `bash scripts/bab_quick.sh` GREEN (targeted trio `104 passed`, smoke `195 passed`,
  `quick preflight OK`).
- `python3 scripts/bab_replay_decisions.py --subset p41_decision.md` GREEN (`OK p41_decision.md -> BAB_P41_DECISION.md`).
- `python3 -m pytest -q tests/test_bab_p41_decision_consistency.py` GREEN (13 passed).
- P32/P33 doc ledgers GREEN: `--check-doc-summary` returns `OK` for both
  `research_state/bab_p32/doc_replay_summary.json` and
  `research_state/bab_p33/doc_consistency_summary.json`.
- P42 charter `docs/BAB_P42_KICKOFF.md` is classified in the doc registry
  (`scripts/bab_doc_consistency_summary.py`, `tests/test_bab_p33_doc_registry_completeness.py`)
  and P42 is the allow-listed successor in `tests/test_bab_p34_doc_pointer_guard.py`.
- P42 artifacts (`scripts/bab_p42_power.py`, `research_state/bab_p42/`,
  `generate_p42_decision.py`, `tests/test_bab_p42_*`) are **absent** — P42 is genuinely open.
- **Full gate still owed this campaign:** `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh`
  must be run to completion (~39 min, 4 cores) before P42 is declared done. It is a
  long/background job — never under a 120 s foreground timeout.
**Supersedes:** all prior HANDOFF.md content.

---

## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT SESSION

> **Timestamped initial task (2026-11-26T08:51:25Z):** Execute **Campaign P42
> "Planted-Alpha Detectability Frontier & Minimum Detectable Effect," WP0 → WP3.**
> P20–P41 are frozen; P41 WP1/WP2/WP3 are complete and committed at HEAD `01d3603`.
> No new maintainer direction is present, so do not idle and do not invent a replacement
> campaign: P42 is a concrete, multi-file, verifiable, heavy workload (810-cell factorial
> grid + frontier meta-analysis + decision doc + gate wiring). Real-data ingestion, CI
> workflow changes, and live deployment remain maintainer-gated and out of scope.

The campaign charter is [`docs/BAB_P42_KICKOFF.md`](docs/BAB_P42_KICKOFF.md); read it
end-to-end before editing. It declares every constant (grid, seeds, planted-alpha
construction, acceptance thresholds). Do not tune seeds or parameters, do not rerun
P20–P41 to chase a result, and do not flip the shipped default (`weighting="equal"`,
`beta_neutral=True`, `beta_window=90`, rolling-OLS).

**BINDING ROW = Campaign P42**

### Step 0 — confirm the baseline and clear the doc ledgers
The P32/P33 ledgers were regenerated in a prior session; confirm they are still fresh, and
regenerate if not (never hand-edit JSON):

```bash
python3 scripts/bab_replay_decisions.py --summary-json research_state/bab_p32/doc_replay_summary.json
python3 scripts/bab_doc_consistency_summary.py --summary-json research_state/bab_p33/doc_consistency_summary.json
python3 scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json
python3 scripts/bab_doc_consistency_summary.py --check-doc-summary research_state/bab_p33/doc_consistency_summary.json
```

### Step 1 — build the power grid (WP1)
Create `scripts/bab_p42_power.py` with `--check-power-grid`, publishing
`research_state/bab_p42/power_grid.json` (schema `bab_p42.power_grid/1`) + `.md`
sidecar. Reuse the P41 DGP builders (`scripts/bab_p41_stress.py`) and the shipped
`strategies/betting_against_beta` estimators/metrics/portfolio; add only the
planted-drift layer declared in the charter. Grid = 3 breadths × 3 histories × 5 alpha
levels × 3 DGPs × 6 seeds = **810 cells**. Every cell reports `recovery_mean`,
`recovery_frac_positive`, `oos_sharpe`, `dsr`, `psr`, `survives_deflation`, `verdict`,
the three neutrality invariants, and `status`. The `alpha_annual=0` cells are the null
panel: recovery exactly 0 and false-survival rate ≤ 0.05.

### Step 2 — frontier meta-analysis (WP2)
Extend `scripts/bab_p42_power.py` with `--check-frontier-summary`, publishing
`research_state/bab_p42/frontier_summary.json` (schema
`bab_p42.frontier_summary/1`) + `.md`. For each `(n_assets, n_rows, dgp)` compute the
**minimum detectable effect** (smallest `alpha_annual` with ≥ 50% of seeds at DSR ≥ 0.50;
`censored` when none). Consolidated verdict ∈ {`DETECTABLE_WITHIN_GRID`,
`POWER_LIMITED_FRONTIER`, `NOT_DETECTABLE_IN_GRID`} — honest, may be negative.

### Step 3 — generate the decision document (WP3)
Create `generate_p42_decision.py` → `docs/BAB_P42_DECISION.md` using committed JSON
only. Mirror `generate_p41_decision.py` (`REPO_ROOT`, `SUMMARY_PATH`, `REPORT_PATH`,
`DECIMALS`, `_load`, `_cell`). Requirements: ≥ 100 matched numeric table cells, zero
unmatched cells; explicit verdict; include the strings `synthetic`,
`not real market data`, `not market profitability evidence`, `never market alpha`; every
published number resolves to a committed JSON leaf.

### Step 4 — add the decision-consistency acceptance test (WP3)
Create `tests/test_bab_p42_decision_consistency.py`, mirroring
`tests/test_bab_p41_decision_consistency.py`: table byte-identity, ≥ 100 matched numeric
cells, zero unmatched cells, explicit verdict/provenance strings, no harness
imports/calls, ruff clean. Binding deliverable, not optional extra coverage.

### Step 5 — register P42 in both replay layers (WP3)
- `scripts/bab_replay_decisions.py`: add `p42_decision.md` next to the P41 block
  (`module: "generate_p42_decision"`, `gen_dir: ROOT`, `kind: "decision"`, output
  `docs/BAB_P42_DECISION.md`).
- `scripts/bab_replay_full.py`: mirror the P41 JSON-only pattern with
  `module: "bab_p42_power"`, `build: "build_power_grid"`, `dir: "bab_p42"`,
  `name: "power_grid"`, `json_only: True`, `no_xproc: True`. This intentionally invokes
  the expensive grid build once during the final full replay; do not replace it with a
  vacuous loader and do not run `--check-power-grid` separately in the inner loop.
- Add `"p42_decision.md"` to `EXPECTED_NAMES` in
  `tests/test_bab_p29_decision_replay.py` and `"power_grid"` to `EXPECTED_NAMES` in
  `tests/test_bab_p29_replay_coverage.py`. Keep exact equality; do not loosen guards.

### Step 6 — wire the gate (WP3)
Add a `bab_p42` block to `scripts/bab_gate.sh` after P41. It must run the P42 power-grid
byte-check, the P42 decision tests, the P42 decision replay subset, and the P33
doc-summary check. Do not add the slow `--check-power-grid` command to
`scripts/bab_quick.sh`; the full replay gate covers the committed grid JSON once at final
verification.

### Step 7 — heavy verification (quick checks are not completion)
Fast inner loop while iterating:

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
python3 scripts/bab_replay_decisions.py --subset p42_decision.md
```

Then run the **mandatory full gate** to completion with the release coverage floor and a
long/background budget (it takes ~39 min on 4 cores):

```bash
BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

If the full gate exposes only the known P27 trailing-newline mutation, restore
`research_state/bab_p27/` with `git checkout -- research_state/bab_p27/` and rerun the
affected check. Do not lower coverage, delete tests, weaken exact registry equality, or
claim success from `bab_quick.sh` alone.

**Definition of done:** ruff GREEN; quick GREEN; P42 power-grid byte-check GREEN; P42
decision replay GREEN; P32/P33 ledger checks GREEN; `docs/BAB_P42_DECISION.md` matches
committed `power_grid.json`/`frontier_summary.json` with ≥ 100 matched numbers and zero
unmatched; P42 registered in replay/tests/gate; and
`BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` exits 0. Stop after WP3; do not
start maintainer-gated work.

---

## PROJECT STATE (frozen inputs, open P42)

| Phase | State | Evidence |
|---|---|---|
| P20–P40 | COMPLETE/FROZEN | Do not reopen; P32/P33 ledger maintenance above is guard upkeep only |
| P41 WP1 | COMPLETE | `estimator_bakeoff.json` + `.md`; byte-check PASS |
| P41 WP2 | COMPLETE | `stress_summary.json` + `.md`; 160 cells, 79 survive, 0/5 DGPs fully replicate, neutrality holds |
| P41 WP3 | COMPLETE | `generate_p41_decision.py`, `docs/BAB_P41_DECISION.md`, `tests/test_bab_p41_decision_consistency.py`, replay/gate registration all committed and GREEN |
| P42 WP0 | COMPLETE | `docs/BAB_P42_KICKOFF.md` |
| P42 WP1/WP2/WP3 | **OPEN — binding** | Power grid, frontier meta-analysis, decision doc + gate wire |

**Scientific finding (P41):** BAB survives pooled deflation on the primary Gaussian
fixture but is `FRAGILE_DGP_DEPENDENT` under non-Gaussian/regime-switching synthetic
DGPs. This is honest negative-leaning evidence, **not market alpha**.

**Open scientific gap (P42):** P21 recovered a planted 4% alpha on a wide Gaussian
universe, while P40/P41 found fragility on narrow non-Gaussian universes. P42 measures
the **detectability frontier** (minimum planted premium × breadth × history) so the
negative results can be attributed to power vs. genuine absence.

## BOTTLENECKS — RESOLVED OR CONTAINED

| Bottleneck | Status / next action |
|---|---|
| Stale handoff (declared P41 WP3 open, artifacts "absent") | **REMOVED** — P41 WP3 is complete; handoff rewritten to P42 |
| Stale HEAD hash in handoff (`f7c0cc0` vs actual `01d3603`) | **REMOVED** — handoff re-verified at HEAD `01d3603` this session |
| Full gate RED on 5 doc-pointer/registry guards | **REMOVED** — README/COVERAGE_NOTES repointed to P42; P34 successor allow-list extended to P40/P41/P42; P42 charter allow-listed; P33 ledger regenerated |
| P34-complete marker absent from handoff | **REMOVED** — `CAMPAIGN P34 — COMPLETE` present below |
| P32/P33 committed ledgers stale | **RESOLVED** — regenerated from registry; never hand-edit |
| Full gate exceeds one short tool window (~39 min) | **CONTAINED** — quick inner loop; full gate runs in background/long budget |
| Expensive P42 grid recompute | **CONTAINED** — once in final full replay, never in quick loop |
| Rank weighting | **CLOSED** — P36 proved worse; never reopen |
| CI workflow enforcement | **EXTERNAL** — maintainer-only `workflows:write`; do not burn a session |
| Full pytest mutates frozen P27 markdown | **CONTAINED** — restore only `research_state/bab_p27/` after the full run |

## CAMPAIGN LEDGER

- **CAMPAIGN P34 — COMPLETE** (multiseed robustness + honesty battery + doc pointer guard).
- **CAMPAIGN P41 — COMPLETE** (non-Gaussian & regime-switching synthetic stress battery).
- **CAMPAIGN P42 — ACTIVE BINDING ROW** (planted-alpha detectability frontier).

**Repository root:**
`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`

**END OF HANDOFF — first action: step 0 ledger confirmation, then implement P42 WP1→WP3
and finish only when the 100%-coverage full gate is GREEN.**