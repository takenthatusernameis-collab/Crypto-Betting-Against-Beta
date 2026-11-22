# Coverage notes (BAB product)

- **Measured (current, 2026-11-18T19:21Z, HEAD `33b84e2` + coverage pins):** **TOTAL 100%** line coverage for `strategies/betting_against_beta` (**0 missed / 6566 statements**) with full gate **6462 passed / 35 skipped / 0 failed** and `BAB_GATE_MIN_COVERAGE=100` GREEN. Re-measure and record date/HEAD in `HANDOFF.md` whenever the gate is re-run.
- **Historical note (superseded):** earlier measurements — 99% / 14 missed @`07f1741`, 99% / 5 missed (only `beta.py:544-548`) @`f9dd8ca`, and 99% / 8 missed @`33b84e2` before the class-B `beta_neutral=False` pins — are obsolete; trust the live gate, not these lines.
- **Active work is binding:** **Campaign P36 "Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure"** in [`HANDOFF.md`](../HANDOFF.md) is the single source of truth (P20–P35 COMPLETE and frozen). Coverage is saturated at 100%; do not lower the floor, add type annotations (ANN excluded), or refactor for style alone. Hard floor: `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` must stay GREEN.
- **Residual misses on already-saturated modules** (e.g. `data_sources.py` 100%, `metrics.py` 100%, `portfolio.py` 100%, `replay.py` 100%): add tests only for a line shown to be reachable behavior or a real defect; otherwise justify as saturation residue.
- **Active engineering debt:** none in coverage; P35 focus is beta-estimation robustness + signal-stability (see `HANDOFF.md`). Narrowing/surfacing broad `except Exception` sites is out of scope until P35 closes.
- **Toolchain bottleneck removed:** `scripts/bab_bootstrap.sh` installs missing Python deps before quick/gate; `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` fails closed when TOTAL is below 100%.

(End of file - total 8 lines)