# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-13T06:30:30Z
- **HEAD:** `1ace2b50 chore: capture completed workflow run diagnostics`
- **Gate (verified this session):** `bash scripts/bab_gate.sh` → **5140 passed / 35 skipped / RC=0** (2026-11-13T06:30Z; re-run before/after any change).
- **Env fixed:** container had no Python deps; `pip install -r requirements.txt` done (numpy/pandas/scipy/pytest/hypothesis). `coverage` optional.
- **Binding next action (initial task):** **Ship Step 3e stale-run vectorization** in `strategies/betting_against_beta/data_loader.py` — replace the per-column Python loop at `:1483-1498` with the existing dead helper `_max_consecutive_equal_finite_frame` (`:1328`), preserving exact raise-ordering/messages; add oracle tests; full gate RC=0; then Step 3f (`beta.py:331`, `portfolio.py:43`, `backtest.py:9`). No measurement-only churn. No commits unless explicitly requested.