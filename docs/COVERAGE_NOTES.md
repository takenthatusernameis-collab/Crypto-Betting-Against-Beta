# Coverage notes (BAB product)

- **Measured:** 96% line coverage for `strategies/betting_against_beta` (4815 statements, 185 missed) at HEAD `45563ba` with full suite gate **5590 passed / 35 skipped / RC=0** (no per-file ignores). Record refresh date/HEAD in `HANDOFF.md` when re-measured.
- **Residual misses are defensive fallbacks, not a probe campaign:**
  - `backtest.py`: 13-19, 25-28, 107-108, 150-176
  - `beta.py`: 124, 149-150, 162, 169-170, 188, 215-218, 315-328, 372-386, 435-436, 544-558
  - `cli.py`: 205-206, 208, 210, 313, 433-434, 441-442, 445-450, 505
  - `data_loader.py`: 47-48, 238-248, 250-251, 272-273, 330, 342-346, 407-408, 645-646, 698-699, 795-796, 957, 1125, 1130-1131, 1244, 1479-1480, 1490, 1519-1520, 1525-1526, 1531-1533, 1538-1547, 1777-1778
  - `metrics.py`: 99, 144, 147, 150; `portfolio.py`: 134-135, 152-159, 162; `signals.py`: 37, 75; `config.py`: 163, 174-175; `costs.py`: 59-60; `strategy.py`: 234-237, 239, 253-256, 261
- **Policy:** probe-count quotas are abolished. Do not append "no reduction identified" logs. Add tests only for a residual line shown to be reachable behavior or a real defect; otherwise treat as saturation residue.
- **Active engineering debt:** broad `except Exception` / direct silent `pass` in product modules. Prioritize narrowing/surfacing with regressions over coverage-chasing.