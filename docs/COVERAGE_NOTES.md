# Coverage notes (BAB product)

- **Measured:** 99% line coverage for `strategies/betting_against_beta` (4535 statements, 66 missed) at HEAD with full suite gate **5069 passed / 35 skipped / RC=0** (no per-file ignores). Record refresh date/HEAD in `HANDOFF.md` when re-measured.
- **Residual misses are defensive fallbacks, not a probe campaign:**
  - `data_loader.py`: 43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953
  - `beta.py`: 124, 149-150, 162, 169-170, 188, 215-218, 356-359, 429-433
  - `cli.py`: 5 residual lines (re-measure after C54 Step 2 edits)
  - `metrics.py`: 4; `signals.py`: 2; `config.py`: 2; `costs.py`: 2
- **Policy:** probe-count quotas are abolished. Do not append "no reduction identified" logs. Add tests only for a residual line shown to be reachable behavior or a real defect; otherwise treat as saturation residue.
- **Active engineering debt:** broad `except Exception` / direct silent `pass` in product modules (see `HANDOFF.md` C54 Step 2, AST-verified counts). Prioritize narrowing/surfacing with regressions over coverage-chasing.
