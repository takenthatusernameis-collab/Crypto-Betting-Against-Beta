# INITIAL TASK MESSAGE — Binding for Next Agentic Session

**Timestamp:** 2026-11-19T13:14:47Z · **Campaign:** P23 "Breadth and instability stress" · **Lane:** A · **WP:** **P23 WP0 — charter**

---

## One-sentence objective

Write `scripts/bab_p23_charter.py` plus `research_state/bab_p23/charter.{json,md}`, `docs/BAB_P23_KICKOFF.md` and `tests/test_bab_p23_charter.py`, producing a machine-readable charter that (a) restates the closed P22 decision (NO-GO for market) from the committed P22 JSON only — no hand-typed numbers, (b) pins the P23 breadth ladder, beta-window/drift grid, short-availability haircut ladder, per-work-package seeds and the exact acceptance thresholds consumed by WP1–WP4, and (c) proves committed JSON == fresh build and markdown derived from JSON only.

---

## Why this and nothing else

- P21 and P22 are closed and frozen; the repository name names a market-neutral strategy, and the open question after P22 is whether the measured result survives breadth and instability, not whether the estimator is calibrated.
- P23 is offline and heavy by construction: every WP is artifact-gated, so prose-only sessions fail the routing table.
- WP0 is the only missing row and every later P23 WP consumes its pinned constants.

---

## Prioritization basis

P22 closed with a NO-GO that rests on a controlled synthetic stimulus. The next failure mode for a betting-against-beta book is instability: breadth concentration, beta-estimation drift, and short-side scarcity in crypto. P23 measures exactly those, and WP0 must pin the grids and thresholds before any of them can be run.

---

## Deliverable files are the claim

Run this to verify the first missing row:

```bash
git ls-files \
  scripts/bab_p23_charter.py \
  tests/test_bab_p23_charter.py \
  docs/BAB_P23_KICKOFF.md \
  research_state/bab_p23/charter.json \
  scripts/bab_breadth_ladder.py \
  research_state/bab_p23/breadth_ladder.json \
  scripts/bab_beta_drift.py \
  research_state/bab_p23/beta_drift.json \
  scripts/bab_borrow_stress.py \
  research_state/bab_p23/borrow_stress.json \
  docs/BAB_P23_DECISION.md
```

| First file missing from that list | Your WP | You own (create + commit) |
|---|---|---|
| `scripts/bab_p23_charter.py` | **P23 WP0** | `scripts/bab_p23_charter.py`, `research_state/bab_p23/charter.{json,md}`, `docs/BAB_P23_KICKOFF.md`, `tests/test_bab_p23_charter.py` |
| `scripts/bab_breadth_ladder.py` | **P23 WP1** | `scripts/bab_breadth_ladder.py`, `research_state/bab_p23/breadth_ladder.{json,md}`, `tests/test_bab_p23_breadth_ladder.py` |
| `scripts/bab_beta_drift.py` | **P23 WP2** | `scripts/bab_beta_drift.py`, `research_state/bab_p23/beta_drift.{json,md}`, `tests/test_bab_p23_beta_drift.py` |
| `scripts/bab_borrow_stress.py` | **P23 WP3** | `scripts/bab_borrow_stress.py`, `research_state/bab_p23/borrow_stress.{json,md}`, `tests/test_bab_p23_borrow_stress.py` |
| `docs/BAB_P23_DECISION.md` | **P23 WP4** | `docs/BAB_P23_DECISION.md`, `tests/test_bab_p23_decision_consistency.py` |

---

## Rules (non-negotiable)

1. **Never take a WP whose deliverable script already exists** (`git ls-files`, or on disk and passing its test). Commit an uncommitted WP first, verify it, then take the next missing one.
2. **Solo default: P23 WP0.** It reads the committed P21/P22 JSON read-only and must not regenerate, re-run or edit any P21/P22 harness or artifact.
3. A partially finished WP is not locked. If files exist only in the working tree (not `git ls-files`) or the gate is red, you own finishing it.
4. **Everything blocked?** Repair the red gate first (`bash scripts/bab_quick.sh`), then take the first missing row.
5. **Never end a session with prose.** A landed WP = deliverable + artifact + acceptance test in **one** commit + green full gate.
6. **A documentation-only session is a failed session.** A handoff refresh must also land the next missing WP (or a tested slice) in the same turn — then update this file with what landed.

---

## MANDATORY FIRST ACTIONS (in order, ~4 minutes)

1. `git log --oneline -4 && git status --short` — locate yourself. Do not re-derive what HANDOFF.md certifies.
2. `bash scripts/bab_quick.sh` (≈20 s, must be GREEN). It bootstraps numpy/pandas/scipy/pytest/ruff from PyPI.
3. Confirm P21/P22 are closed and their artifacts are intact (≈0.1 s):
   ```bash
   python3 - <<'EOF'
   import json
   from pathlib import Path
   root = Path(".")
   for campaign, names in {
       "bab_p21": ("universe", "significance", "rank_eval", "cost_surface"),
       "bab_p22": ("charter", "null_battery", "impact_surface", "capacity"),
   }.items():
       for name in names:
           p = root / f"research_state/{campaign}/{name}.json"
           assert p.is_file(), f"missing {p}"
           json.loads(p.read_text(encoding="utf-8"))
   for report in ("docs/BAB_SIGNAL_OR_NOISE.md", "docs/BAB_P22_DECISION.md"):
       assert (root / report).is_file(), f"missing {report}"
   print("P21 and P22 closed; artifacts intact")
   EOF
   ```
4. Read `docs/BAB_P22_DECISION.md` — the verdict the P23 charter restates (NO-GO for market; signal on planted, noise on null; capacity break-even and impact surfaces are synthetic-only). Every P23 threshold must trace to a committed P22 or P23 JSON field.
5. Read `scripts/bab_p22_charter.py` and `tests/test_bab_p22_charter.py` — the pair P23 WP0 must follow: pure `build_charter` / `render_markdown` / `write_artifacts` / `main`, 6-dp rounding, committed-artifact identity, JSON-derived markdown, no harness re-run.
6. Read `scripts/bab_capacity.py` and `tests/test_bab_p22_capacity.py` — the pattern for a heavy, fixed-iteration surface harness with documented censoring and a pinned sign test.
7. Read `research_state/bab_p21/universe.json` provenance and `strategies/betting_against_beta/strategy.py` (rank guards, beta window) — P23 breadths, drift grids and borrow haircuts must be expressed through the shipped strategy, never a re-implementation.

---

## P23 WP0 — Charter: what it must contain

The charter payload (schema `bab_p23.charter/1`) must include:

### 1. P22 verdict restated from committed P22 JSON only
- Read `research_state/bab_p22/{charter,null_battery,impact_surface,capacity}.json` read-only
- Restate: NO-GO for market; signal on planted, noise on null; capacity break-evens; impact monotonicity
- **Zero hand-typed numbers** — every cell comes from a committed P22 JSON field or is a charter-declared constant

### 2. P23 charter constants (declared here, not derived)
- **Breadth ladder** (asset counts for P23 WP1): e.g., `[9, 17, 25, 33, 41]`
- **Beta-window/drift grid** (for P23 WP2): e.g., `beta_window ∈ {60, 90, 120, 180}` × `drift_threshold ∈ {1e-4, 5e-4, 1e-3}`
- **Short-availability haircut ladder** (for P23 WP3): e.g., `haircut ∈ {0.0, 0.10, 0.25, 0.50, 0.75}`
- **Per-WP seeds**: ≥ 20 independent seeds each for WP1–WP3 (declare lists explicitly)
- **Nominal slack**: 0.05 (same as P22)
- **Acceptance thresholds** consumed by WP1–WP4 (exact values, not ranges)

### 3. WPs in order (binding sequence)
```
P23 WP0 — charter
P23 WP1 — breadth ladder
P23 WP2 — beta-window/drift grid
P23 WP3 — short-availability haircut ladder
P23 WP4 — decision report (must keep NO-GO in force)
```

### 4. Proof requirements
- Committed `charter.json` == fresh `build_charter()` (byte-identical)
- `charter.md` == `render_markdown(payload)` (byte-identical)
- `docs/BAB_P23_KICKOFF.md` == `charter.md`
- No import or re-run of any P21/P22 `build_*` harness
- AST check: no imports from `scripts` or `strategies`, no calls to `build_*` except `build_charter`

---

## Hard gates every session (repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

Inner loop: `bash scripts/bab_quick.sh` + `python3 -m pytest -q tests/test_bab_p23_charter.py`. Full gate once per WP boundary; never hand off mid-gate. Never lower the coverage floor.

---

## Forbidden (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits
- Hand-typing any number into the charter, report, or verdict that is not a committed JSON field
- Editing any `research_state/bab_p21/**`, `research_state/bab_p22/**`, or P20 artifacts
- Reopening P21, P22, P20, or any prior campaign
- Weakening rank guards (`rank_min_leg_beta` / `rank_max_gross`) to make rank "active"
- Describing any synthetic universe as real market data
- Quoting P21 planted-universe recovery as market alpha
- Creating parallel handoff docs (`*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`)

---

## Work quantum — minimum a session must produce

A session is **not** complete unless **all** of the following landed in one commit:

1. One complete WP from the routing table (or one tested slice with exact remainder in ledger)
2. Its **script + committed artifact + acceptance test**
3. A hash-determinism assertion, not a "looks stable" claim
4. `python3 -m ruff check .` PASS and `bash scripts/bab_quick.sh` GREEN; full gate once per WP boundary
5. A ledger row with UTC timestamp, HEAD, what landed, and the gate line
6. **No documentation-only turn**

---

## If P23 WP0 feels large — no-idle ladder

1. Land the JSON-only table renderers first (one function per table, taking committed P22 JSON and returning markdown) with a test that rendered table equals renderer output byte-for-byte
2. If a P22 JSON field you want to restate does not exist: do not compute it in prose. Either publish only existing fields, or land a new upstream WP in the same commit that adds the field to the harness plus its acceptance test
3. If the charter looks "too positive": that is the P22 verdict you must restate explicitly — signal on planted, noise on null, NO-GO for market. Publish the null/calibration evidence next to it
4. Blocked on everything? Repair the gate and add one missing test in a P21 or P22 test file. Something landable always exists.

---

**This is the single durable handoff. The binding initial task is P23 WP0. The next session must start here and land it.**