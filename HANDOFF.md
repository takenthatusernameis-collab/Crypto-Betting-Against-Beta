# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-16T00:55:30Z (this refresh)
- **Repo:** `Crypto-Betting-Against-Beta` — a **crypto market-neutral trading system** (data ingestion → beta → signals → portfolio → backtest → execution → ops) implementing the Frazzini–Pedersen *Betting Against Beta* strategy.
- **Git HEAD (verified this refresh):** `65fe0d3` (`chore(kilo): checkpoint agent session`)
- **Working tree at refresh:** clean (`git status` clean vs `origin/main`); `python3 -m ruff check .` → `All checks passed!`
- **Gate evidence (last live-verified 2026-11-16T00:09:32Z at HEAD `65fe0d3`, not rerun this refresh):** `bash scripts/bab_gate.sh` → **GREEN**: 6,140 passed, 35 skipped in **132.94s** (parallel, xdist loadscope, coverage core=sysmon); TOTAL **99%** (6,630 statements, 91 missed). Floor `BAB_GATE_MIN_COVERAGE=98.5` would pass. Re-run `bash scripts/bab_gate.sh` before/after any code change and trust live output over this note.
- **Toolchain:** `python3 3.12.3`; `ruff 0.17.5`; numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt via `bash scripts/bab_bootstrap.sh` (auto-invoked by quick/gate).

## INITIAL TASK MESSAGE (START HERE, 2026-11-16T00:55:30Z) — BINDING (DO NOT IGNORE)

**Campaign P16 — Trading-Critical Correctness & Safety Hardening. This is the next session's sole focus and the only authorized starting point. Start at P16-3 immediately. Do NOT restart P16-1/P16-2, re-triage the A/B/C map, create parallel handoff docs, or spend the session on analysis/handoff-only work.**

Priority rationale (derived from the repo's identity): this is a **crypto trading system**, not a coverage exercise. The data-quality gate decides whether frozen, gapped, or implausible market data reaches beta estimation → portfolio construction → execution. That makes the quality contract the highest-stakes code in the repo. **Line-coverage percentages are a trailing metric, not the goal.** Ship real production fixes with proof tests every session. **Analysis-only, handoff-only, formatting-only, and coverage-chasing turns are failed sessions.**

### P16-3 (highest priority — execute first) — honor quality-safety thresholds, safety-first

The data-quality contract is currently **unsafe and self-contradictory**. Live-verified at HEAD `65fe0d3` (reproduce with the two probes below before editing):

- **Doc/impl contradiction.** `validate_returns_dataframe` docstring (`data_loader.py:1697-1719`) promises defaults `stale_run_threshold=3`, `max_gap_days=7.0`, `max_return_abs=20.0`. The implementation (`data_loader.py:1536-1541`) uses `10_000.0`, `3650.0`, `50` ("very lenient").
- **Explicit thresholds are ignored.** Both quality paths clamp the allowance with `max_allowed_stale = max(int(stale_run_threshold), 50)` — fast path `data_loader.py:1622-1636`, slow path `data_loader.py:1656-1668`. An explicit `stale_run_threshold=3` therefore **cannot** reject a 4–49 equal-value run.
- **Dict `quality` is silently dropped (worse than a type error).** `quality` is typed `bool` (`data_loader.py:1679`) and dispatched by truthiness only (`data_loader.py:1895`). **There is no dict parsing anywhere in the module.** Six tests already pass `quality={"stale_run_threshold": 3}` / `{"max_gap_days": 2}` / `{"allow_duplicate_timestamps": ...}` (all in `tests/test_bab_data_loader_coverage_gaps.py`, lines 5402, 5719, 5727, 5738), and those tests wrap the call in `contextlib.suppress(BABDataError)` / `try/except pass` — they **pass trivially whether or not the dict is honored**. Caller intent is lost silently.

**Reproduce (run from repo root):**

```bash
python3 - <<'EOF'
import pandas as pd
from strategies.betting_against_beta import data_loader as dl
idx = pd.date_range("2020-01-01", periods=8, freq="D")
df = pd.DataFrame({"BTC":[0.01]*8, "ETH":[0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09]}, index=idx)
for label, kw in [
    ("explicit threshold=3 (direct)", dict(quality=True, stale_run_threshold=3)),
    ("dict quality threshold=3",      dict(quality={"stale_run_threshold": 3})),
]:
    try:
        dl.validate_returns_dataframe(df.copy(), benchmark="ETH", **kw)
        print(f"{label}: NO RAISE  <-- BUG (8-long frozen BTC run not rejected)")
    except Exception as e:
        print(f"{label}: rejected {type(e).__name__}")
EOF
```

**Fix, in this order:**

1. **Characterization tests first.** Add tests that pin *current* behavior for: (a) a 10000% return, (b) a 100-day gap, (c) a 4–49 equal-value run with explicit `stale_run_threshold=3`, (d) the fast numeric path, (e) `quality` passed as a dict. These must fail on HEAD for the cases you are about to fix and pass after. Replace the `contextlib.suppress`/`try: ... except: pass` wrappers in `tests/test_bab_data_loader_coverage_gaps.py:5708-5739` with real assertions — a test that cannot fail is worse than no test.
2. **Remove the 50-run floor.** Delete `max(int(stale_run_threshold), 50)` in both paths (`data_loader.py:1623`, `:1662`) so an explicit threshold is honored. Keep the `finite_count >= threshold` / `int(stale_run_threshold) > 0` guards intact (threshold `0` still disables).
3. **Reconcile defaults with the docstring.** When `quality` is truthy and a threshold arg is `None`, use the documented safe defaults (`max_return_abs=20.0`, `max_gap_days=7.0`, `stale_run_threshold=3`) instead of `10000/3650/50`. Update the inline comments at `data_loader.py:1848-1854` that justify the lenient `10000` threshold — that justification is now wrong.
4. **Parse dict `quality`.** Accept `quality` as `bool | dict`. When it is a dict, treat it as per-call overrides merged under the explicit kwargs (`{max_return_abs, max_gap_days, stale_run_threshold, min_finite_fraction, allow_duplicate_timestamps}`), with explicit function kwargs taking precedence. Preserve `quality=False` as the explicit opt-out. `quality=True` must not silently disable the documented guards.
5. **Treat old-contract tests as regressions to update, not contracts to preserve.** Search every caller/test before flipping defaults: `validate_returns_dataframe`, `_run_data_quality_campaign`, the real-data loaders (`load_returns*`, `load_prices*`), backtests, and the performance oracles in `tests/test_validation_performance.py` (`_oracle_quality` at lines 54-97 and the `stale_run_threshold=50` references) — those must be updated to the new semantics or they will mask the fix.
6. **No undocumented global escape hatch.** If the full gate exposes unavoidable compatibility coupling, keep the stricter behavior, document the deliberate migration, and isolate any compatibility switch behind an explicit opt-in kwarg. Do **not** re-add a lenient default or a `max(...,50)` floor.
7. **Proof obligation:** one test that fails on HEAD and passes after the fix, for *each* changed guard (defaults, 50-run floor, dict parsing). Record exact commands/results in the ledger below.

### P16-4 — convert remaining reachable bucket-B edges into targeted behavior tests

Use fakes/mocks only; batch by module and rerun the full gate after each batch. Add behavior assertions, not coverage-only smoke tests. If an edge is now unreachable, prove it and move it to bucket C. These are the 91 statements the 2026-11-16T00:00:00Z refresh catalogued — useful as a checklist, but **only after P16-3 correctness work**:

- `execution.py:139-141` Timestamp-key fallback with a string `date_key`; `execution.py:182-185` Timestamp-indexed ADV sub-frame; `execution.py:555-556` non-finite numpy float JSON sanitization with `allow_nan=False`.
- `portfolio.py:152-153` extreme-weight clipping; `portfolio.py:170-177` dollar-neutral `need_fix` renormalization under one-sided underflow.
- `cli.py:589-590` unknown adapter; `cli.py:746-748` invalid output path.
- `reconciliation.py:309` empty-column early return.
- `data_sources.py:480-481, 499-500, 507-508` timezone/format edges.
- `data_loader.py` (37 lines) mixed-dtype slow path, finite-fraction boundary, stale-run boundary, adversarial datetime dayfirst retry/error wrap, multi-source fallback chains (280-292, 666-667, 718-719), empty/malformed CSV (422-423, 837-838), batch fetch error paths (1355, 1609, 1644-1670, 1916-1917, 2711-2712).
- `signals.py:37` object dtype after numeric coercion.

### P16-5 — delete or justify bucket-C dead branches

Do not add tests to "buy" coverage. Candidates: `beta.py` 125, 163, 170-171, 189, 435-436, 552-556; `execution.py:1287-1288`; `portfolio.py:180`; `metrics.py:94`; `signals.py:75`; `reconciliation.py:82-83`; `replay.py:172`; `cli.py:803-804`. Delete only with a concrete unreachability proof in the test/commit rationale; otherwise leave and document why it is defensive/dead. Never delete reachable safety behavior.

### P16-6 — prove performance, then continue to the next real defect

Run `python3 scripts/perf_baseline.py --check` (rerun once if noisy), record exact metrics, refresh this file with timestamp/HEAD/tree/ledger/coverage evidence, then immediately start the next real correctness or safety defect. **Never stop at "campaign complete."**

### Hard gates every session (run from repo root, in order)

```bash
python3 -m ruff check .                 # must pass
bash scripts/bab_gate.sh                # full suite + coverage, must be GREEN (~2.5 min)
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh   # P14 release floor must hold
```

### Non-goals (do not pursue)

- ❌ Adding type annotations (ANN rules excluded by policy).
- ❌ Refactoring defensive try/except patterns (BLE/TRY rules excluded).
- ❌ Lowering the coverage floor — add tests, don't lower the bar.
- ❌ Coverage-against-dead-lines turns that substitute for correctness work (see P16-5).

### Bottleneck removal status

- ✅ Gate runs parallel by default (`-n $(nproc) --dist loadscope`, coverage core=sysmon) — ~2.2 min vs ~16 min serial; verified this refresh.
- ✅ `scripts/bab_bootstrap.sh` auto-installs missing deps — no manual setup.
- ✅ No flaky tests; the 35 skipped are explicit `pytest.mark.skip` (known gaps).
- ✅ Stale-pointer bottleneck removed: `AGENT_HANDOFF.md` is now a pure pointer to this file; the previous session's pointer referenced a P16 campaign body that no longer existed — a future agent would have chased a dead reference.
- ⚠️ Open bottleneck being fixed by P16-3: the quality gate cannot honor explicit thresholds (50-run floor) or dict overrides — i.e., safety configuration is silently inert in production paths.

### Session ledger (append one line per session; keep it honest)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-16T00:55:30Z | 65fe0d3 | Handoff refresh: confirmed single durable handoff (`HANDOFF.md`) + pointer, working tree clean, `ruff` clean; re-stamped binding P16-3 initial task (no parallel docs, no re-triage). Did not rerun full gate (last live GREEN 2026-11-16T00:09:32Z, 6,140 passed / 35 skipped / 132.94s / 99%). | last GREEN @00:09:32Z |
| 2026-11-16T00:09:32Z | 65fe0d3 | Handoff refresh: verified gate GREEN (6,140 passed / 35 skipped / 132.94s / 99%); updated timestamp/evidence; P16-3 remains binding initial task | GREEN |
| 2026-11-16T00:08:54Z | 65fe0d3 | Handoff consolidation: restored P16 correctness-first campaign as the binding initial task message; re-verified gate GREEN live (6,140 passed / 35 skipped / 132.68s / 99%); fixed stale pointer | GREEN |

---

**Next agent**: Start with P16-3, step 1 — write the five characterization tests and run the two-line repro probe above. Confirm the bug reproduces, then fix in order (floor → defaults → dict parsing). After each fix, rerun `bash scripts/bab_gate.sh` and keep it GREEN. Then proceed to P16-4. Record your session line in the ledger before finishing.