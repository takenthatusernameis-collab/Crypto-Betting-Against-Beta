# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T08:33:06Z
**HEAD:** `f26f8007d89bb026256ece037adb33e36f9c8cff` (working tree **clean**)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (`README.md`, `strategies/betting_against_beta/`).
**Gate (verified this session, NOT copied):** `bash scripts/bab_gate.sh` → **5145 passed, 35 skipped, RC=0** (301.70s, 2026-11-13T08:29Z, python 3.12.3; `coverage` not installed → gate runs without a coverage report). **Re-run the gate before and after any shipped change and record the new result.**

> **INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T08:33:06Z) — BINDING, HEAVY WORK REQUIRED (NO EXCUSES):**
>
> **CORRECTION FIRST — DO NOT optimize the already-optimized.** The previous handoff told you to "optimize `calculate_rolling_beta` at `beta.py:331` (~12.1 ms)". **That premise is stale and wrong.** The 12.1 ms figure was the *naive* pre-optimization baseline; the vectorized implementation **already shipped** and now measures **0.62 ms** on the standard 720×12 fixture (see "Measured baselines" below). Same for `construct_portfolio` (0.39 ms) and `run_backtest` (1.48 ms) — all three already carry the "hoisted / redundant-copy-removed / second-shift-avoided" optimizations described in code comments. Re-implementing them is forbidden churn. Read `beta.py:389-558`, `portfolio.py:43-120`, `backtest.py:9-163` before touching anything.
>
> **Your actual job: find and ship the next real win, on a larger/realistic workload, where the existing perf tests do NOT yet guard.** The current perf tests use 720–2000 rows × 12–120 assets. There is unmeasured headroom at production scale. Concretely:
>
> 1. **Scale up and re-baseline** with a realistic fixture (e.g. 2500 trading days × 40–60 assets, the default universe size and multi-year history) and measure warm medians for `calculate_rolling_beta`, `construct_portfolio`, `run_backtest`, and end-to-end `BABStrategy.run()` (`strategies/betting_against_beta/strategy.py:211`). Report the real per-stage distribution — do not trust the small-fixture numbers in this file as the production truth.
> 2. **Profile** (`cProfile`/`py-spy` if available) to locate where time actually goes at that scale. The likely hot spots at large N are: per-asset Python loops in `beta.py`'s mixed-dtype / bad-column fallback path (`beta.py:481-520`), `_write_book` / turnover fan-out in `portfolio.py`, and per-column `fillna`/`diff`/`reindex` in `backtest.py` (`:57-120`).
> 3. **Ship one end-to-end stage optimization** with: oracle-equivalence tests (identical values, NaN/inf/degeneracy/min_obs, tolerance 1e-12, unchanged error messages and ordering), a **generous, CI-stable perf-ceiling test** in the style of `tests/test_beta_performance.py` / `test_portfolio_performance.py` / `test_validation_performance.py` (add to the matching file, or a new `tests/test_*_performance.py`), then targeted tests, then full `bash scripts/bab_gate.sh` RC=0. Record before/after warm medians + delta here.
> 4. If a stage genuinely has no win after an attempted implementation, record the evidence (what changed, the numbers) and move immediately to the next candidate. Do NOT stop the session at measurement/profiling only.
>
> **Secondary (only if the above yields nothing — it is small):** the whole-frame `pd.api.types.is_numeric_dtype` check in `_run_data_quality_campaign` (`data_loader.py:1468` fast path / `:1080` per-column path) is already largely done (Step 3e). The only residual idea is a minor fast-path consolidation; treat it as low-value and only if it is provably safe with oracle tests.

## Measured baselines (THIS environment, 2026-11-13T08:31Z — trustworthy)
Fixture: 720 bdays × 12 assets (`scripts/perf_bench.py` `_make_returns`), warm medians (median of 7 reps after warmup):
- `calculate_rolling_beta` — **0.62 ms** (NOT 12.1 ms; 12.1 was the naive baseline, optimization shipped)
- `construct_portfolio` — **0.39 ms**
- `run_backtest` — **1.48 ms**
- `BABStrategy.run` — **3.90 ms**

These are small-fixture numbers. **The whole point of the next session is to measure at production scale (2500×40-60) and find the win the small fixture hides.**

## What is ALREADY shipped (do NOT reopen without a new reproducible failure + evidence)
- `beta.py` `calculate_rolling_beta`: 2-D stacked `_rolling_sum` pass, hoisted benchmark rolling sums, single `to_numpy(dtype=float)`, per-column finiteness classification in one vectorized pass (`:412-520`). Comments at `:443-458`, `:475-480`.
- `portfolio.py` `construct_portfolio`: removed redundant `signals_df.copy()` (`:83-85`), single `to_numpy(dtype=float)` (`:85`/`:96`), `np.trunc` on array (`:99`); `_write_book` vectorized DN path (`:304-330`).
- `backtest.py` `run_backtest`: reuses `w_shifted` for turnover, avoiding a second `shift` allocation (`:62-78`).
- `data_loader.py` `_run_data_quality_campaign`: vectorized `_max_consecutive_equal_finite_frame` stale-run scan with lowest-column-index-first raise semantics (`:1489`), numeric fast path (`:1467-1498`).
- Prior completed campaigns C42–C54 (see git log `git log --oneline | head -40`): full-suite gate discipline, broad-silent audit, `beta.py` perf (`8c2830a`), `construct_portfolio` DN vectorization (`83ff28e`), `validate_returns_dataframe` numeric fast path (`c40dd50`), `_series_is_parseable` vectorized (`43a2313`), `docs/COVERAGE_NOTES.md`.

## Environment / bottlenecks (current)
- **Deps:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis present. `coverage` **not installed** (gate still runs, no coverage report); install only if needed: `pip install coverage`.
- **No active blocker:** working tree clean at `f26f800`, gate green (5145 passed / 35 skipped / RC=0), perf suites green (44 passed).
- **Friction:** full gate ~5 min. Run targeted perf tests first; gate is mandatory before/after shipped code.
- **Scratch:** use `/home/runner/work/_temp/kilo-tmp/` for new probe scripts. Do NOT add tracked `probe*`/`debug*`/`ast_probe.py` at repo root (existing ones are scratch, do not edit/commit).

## Anti-churn / execution rules (binding)
- **Ship code, not commentary:** progress = measured win + oracle tests + perf-ceiling test + green gate + recorded deltas.
- **Do not** re-optimize the already-shipped stages listed above.
- **No** re-profiling of old recorded baselines except as before/after measurements for code you change now.
- **No** probe-count campaigns, C-number rotation, or "no reduction identified" artifacts that do not pin real behavior/perf needs.
- **No** reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`) as current failures.
- If a stage yields no measurable win after a genuine implementation attempt, document evidence and immediately move to the next stage; do not stop the session.

## Session exit requirements (mandatory)
1. Targeted tests for changed code, then `bash scripts/bab_gate.sh` → RC=0 (record pass/skip/RC/time).
2. Record per-stage before/after warm medians + delta, or evidenced no-win with next action taken.
3. Refresh this file: timestamp, HEAD, gate result, shipped changes, remaining candidates/status.
4. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
5. Commit nothing unless explicitly requested.

## Locks / prohibitions
- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (root-level probe/debug scripts, `.cov_ds`, `.cov_target` are scratch); use `/home/runner/work/_temp/kilo-tmp/` for new scratch.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, `tests/test_bab_*_c5*_regressions.py`, or `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**