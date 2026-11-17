# Coverage notes (BAB product)

- **Measured (current, 2026-11-17T06:10Z):** **TOTAL 99%** line coverage for `strategies/betting_against_beta` (**14 missed / 6596 statements**) at Git HEAD `07f1741` with full gate **6268 passed / 35 skipped / 12 failed**. Re-measure and record date/HEAD in `HANDOFF.md` whenever the gate is re-run.
- **Historical note (superseded):** earlier measurements at HEAD `3a0a789` (99%, 64 missed / 6631) and `f513c0d` (99%, 48 missed / 6652) are obsolete — trust the live gate, not these lines.
- **Active coverage work is binding:** the **P19-5 campaign in [`HANDOFF.md`](../HANDOFF.md)** is the single source of truth. The 14 remaining missed statements are a correctness smell list: for each line add a behavior test that reaches it, or delete/justify with concrete unreachability proof. Do not lower the floor, add type annotations (ANN excluded), or refactor defensive try/except (BLE/TRY excluded). Hard floor: `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` must stay GREEN.
- **Residual misses on already-saturated modules** (e.g. `data_sources.py` 100%, `metrics.py` 100%, `portfolio.py` 100%, `replay.py` 100%): add tests only for a line shown to be reachable behavior or a real defect; otherwise justify as saturation residue.
- **Active engineering debt:** broad `except Exception` / direct silent `pass` in product modules. Narrowing/surfacing these with regressions is welcome alongside the P19-5 coverage work.
- **Toolchain bottleneck removed:** `scripts/bab_bootstrap.sh` installs missing Python deps before quick/gate; `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` fails closed when TOTAL is below the campaign floor.

(End of file - total 8 lines)