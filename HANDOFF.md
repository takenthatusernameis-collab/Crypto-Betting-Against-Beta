# DURABLE HANDOFF — Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-26T06:16:37Z
**Session:** Kilo General Agent Loop — P41 WP1 COMPLETE; P41 WP2 COMPLETE; **P41 WP3 OPEN (sole binding row)**
**Repository:** Crypto-Betting-Against-Beta (Betting Against Beta crypto quant research)
**Verified baseline (before this handoff edit, HEAD `f4ab1fa`, clean tree):**
- `python3 -m ruff check .` GREEN.
- `python3 scripts/bab_p41_stress.py --check-estimator-bakeoff` PASS (byte-identical).
- `bash scripts/bab_quick.sh` GREEN (299 passed).
- `generate_p41_decision.py`, `docs/BAB_P41_DECISION.md`, and
  `tests/test_bab_p41_decision_consistency.py` are absent.
- **Current full-gate blockers found this session:** committed
  `research_state/bab_p32/doc_replay_summary.json` and
  `research_state/bab_p33/doc_consistency_summary.json` both FAIL their
  `--check-*-summary` commands at HEAD. They are stale generated ledgers, not
  permission to idle; steps 0 and 5 below remove them.
**Supersedes:** all prior HANDOFF.md content.

---

## READ FIRST — INITIAL TASK FOR THE NEXT SESSION

Execute **Campaign P41 "Non-Gaussian & Regime-Switching Synthetic Stress
Battery," WP3: Decision Doc + Gate Wire.** P20–P40 are frozen; P41 WP1/WP2 are
complete and frozen. No new maintainer direction is present, so do not idle and
do not invent a replacement campaign: WP3 is a concrete, multi-file, verifiable,
heavy workload. Real-data ingestion, CI workflow changes, and live deployment
remain maintainer-gated and are out of scope.

The campaign charter is [`docs/BAB_P41_KICKOFF.md`](docs/BAB_P41_KICKOFF.md);
read it end-to-end before editing. The committed read-only WP2 source of truth is
`research_state/bab_p41/stress_summary.json` (schema
`bab_p41.stress_summary/1`, verdict `FRAGILE_DGP_DEPENDENT`). Do not tune seeds
or parameters, do not rerun WP0–WP2 to chase a result, and do not flip the
shipped default (`weighting="equal"`, `beta_neutral=True`, `beta_window=90`,
rolling-OLS).

### Step 0 — remove the stale-ledger bottleneck immediately

Regenerate the P32 document replay ledger from the current registry, then verify
it. Do not hand-edit the JSON:

```bash
python3 scripts/bab_replay_decisions.py --summary-json research_state/bab_p32/doc_replay_summary.json
python3 scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json
```

The P33 ledger is regenerated in step 5, after the P41 registry/allow-list
changes, so it is not written twice.

### Step 1 — generate the decision document

Create `generate_p41_decision.py` → `docs/BAB_P41_DECISION.md` using committed
JSON only. Mirror `generate_p40_decision.py` (`REPO_ROOT`, `SUMMARY_PATH`,
`REPORT_PATH`, `DECIMALS`, `_load`, `_cell`). Requirements:

- Reproduce the WP2 evidence with **at least 100 matched numeric table cells and
  zero unmatched cells**.
- State the explicit verdict `FRAGILE_DGP_DEPENDENT` and retain the shipped
  default; include the strings `synthetic`, `not real market data`,
  `not market profitability evidence`, and `never market alpha`.
- Every published number must resolve to a committed JSON leaf; no hand-typed
  performance numbers.

### Step 2 — add the decision-consistency acceptance test

Create `tests/test_bab_p41_decision_consistency.py`, mirroring
`tests/test_bab_p40_decision_consistency.py`. It must prove table byte-identity,
≥100 matched numeric cells, zero unmatched cells, explicit verdict/provenance
strings, no harness imports/calls, and ruff cleanliness. This test is a binding
deliverable, not optional extra coverage.

### Step 3 — register P41 in both replay layers

- In `scripts/bab_replay_decisions.py`, add `p41_decision.md` next to the P40
  block: `module: "generate_p41_decision"`, `gen_dir: ROOT`,
  `kind: "decision"`, output `docs/BAB_P41_DECISION.md`.
- In `scripts/bab_replay_full.py`, mirror the P40 JSON-only pattern with
  `module: "bab_p41_stress"`, `build: "build_stress_summary"`,
  `dir: "bab_p41"`, `name: "stress_summary"`, `json_only: True`,
  `no_xproc: True`. This intentionally invokes the expensive stress build once
  during the final full replay; do not replace it with a vacuous JSON loader and
  do not run `--check-stress-summary` separately in the inner loop.
- Add `"p41_decision.md"` to `EXPECTED_NAMES` in
  `tests/test_bab_p29_decision_replay.py` and `"stress_summary"` to
  `EXPECTED_NAMES` in `tests/test_bab_p29_replay_coverage.py`. Keep exact
  equality; do not loosen the guards.

### Step 4 — wire the gate

Add a `bab_p41` block to `scripts/bab_gate.sh` after P40. It must run the P41
estimator byte-check, the P41 estimator/decision tests, the P41 decision replay
subset, and the P33 doc-summary check. Do not add the slow
`--check-stress-summary` command to `bab_quick.sh`; the full replay gate covers
the committed stress JSON once at final verification.

### Step 5 — classify and regenerate the doc ledgers

Add `docs/BAB_P41_KICKOFF.md` to `ALLOW_LIST` in
`scripts/bab_doc_consistency_summary.py` with a written reason: it is the
hand-authored binding charter, while the generated P41 decision is replay-gated.
Then regenerate and verify both ledgers:

```bash
python3 scripts/bab_replay_decisions.py --summary-json research_state/bab_p32/doc_replay_summary.json
python3 scripts/bab_doc_consistency_summary.py --summary-json research_state/bab_p33/doc_consistency_summary.json
python3 scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json
python3 scripts/bab_doc_consistency_summary.py --check-doc-summary research_state/bab_p33/doc_consistency_summary.json
```

### Step 6 — heavy verification (quick checks are not completion)

Run the fast inner loop while iterating:

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
python3 scripts/bab_replay_decisions.py --subset p41_decision.md
```

Then run the **mandatory full gate** to completion, with the release coverage
floor and a long/background budget rather than a 120-second foreground timeout:

```bash
BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

If the full gate exposes only the known P27 trailing-newline mutation, restore
`research_state/bab_p27/` with `git checkout -- research_state/bab_p27/` and
rerun the affected check. Do not lower coverage, delete tests, weaken exact
registry equality, or claim success from `bab_quick.sh` alone.

**Definition of done:** ruff GREEN; quick GREEN; P41 decision replay GREEN;
P32/P33 ledger checks GREEN; `docs/BAB_P41_DECISION.md` matches committed
`stress_summary.json` with ≥100 matched numbers and zero unmatched; P41 is
registered in replay/tests/gate; and `BAB_GATE_MIN_COVERAGE=100 bash
scripts/bab_gate.sh` exits 0. Stop after WP3; do not start maintainer-gated work.

---

## PROJECT STATE (frozen inputs, open WP3)

| Phase | State | Evidence |
|---|---|---|
| P20–P40 | COMPLETE/FROZEN | Do not reopen; P32/P33 ledger maintenance above is guard upkeep only |
| P41 WP1 | COMPLETE | `estimator_bakeoff.json` + `.md`; byte-check PASS |
| P41 WP2 | COMPLETE | `stress_summary.json` + `.md`; 160 cells, 79 survive, 0/5 DGPs fully replicate, neutrality holds |
| P41 WP3 | **OPEN — binding** | Decision generator/test, replay registration, gate wire, ledger regeneration, full gate |

**Scientific finding:** BAB survives pooled deflation on the primary Gaussian
fixture but is `FRAGILE_DGP_DEPENDENT` under non-Gaussian/regime-switching
synthetic DGPs. This is honest negative-leaning evidence, **not market alpha**.

## BOTTLENECKS — RESOLVED OR CONTAINED

| Bottleneck | Status / next action |
|---|---|
| Stale handoff HEAD `47f6c6e` | **REMOVED** — rebased to `f4ab1fa` with fresh green checks |
| P32/P33 committed ledgers stale | **OPEN, step 0/5** — regenerate from registry; never hand-edit |
| Full gate exceeds one short tool window | **CONTAINED** — quick inner loop; full gate runs in background/long budget |
| Expensive P41 stress recompute | **CONTAINED** — once in final full replay, never in quick loop |
| P41 WP3 acceptance test omitted | **REMOVED** — step 2 is explicit and binding |
| “Terminal / no campaign remains” framing | **REMOVED** — WP3 is mandatory; no idle fallback |
| Rank weighting | **CLOSED** — P36 proved worse; never reopen |
| CI workflow enforcement | **EXTERNAL** — maintainer-only `workflows:write`; do not burn a session |
| Full pytest mutates frozen P27 markdown | **CONTAINED** — restore only `research_state/bab_p27/` after the full run |

**Repository root:**
`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`

**END OF HANDOFF — first action: step 0 ledger regeneration, then implement P41
WP3 and finish only when the 100%-coverage full gate is GREEN.**