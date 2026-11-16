# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-16T01:00:30Z (this refresh)
- **Repo identity:** `Crypto-Betting-Against-Beta` — a **crypto market-neutral trading system** (ingest → beta → signals → portfolio → backtest → execution → ops) implementing the Frazzini–Pedersen *Betting Against Beta* strategy. The highest-stakes code is the **data-quality contract** that decides whether frozen, gapped, or implausible market data reaches beta estimation → portfolio construction → execution.
- **Git HEAD (verified this refresh):** `99a841b` (`chore(kilo): checkpoint agent session`); working tree clean; `python3 -m ruff check .` → `All checks passed!`
- **Gate evidence (live-verified this refresh 2026-11-16T01:00Z at HEAD `99a841b`):** `bash scripts/bab_gate.sh` → **GREEN**: **6,153 passed, 35 skipped in 132.01s**, TOTAL **99%** (6,643 statements, 91 missed). Re-run the gate after every change and trust live output over this note.
- **Toolchain:** `python3 3.12.3`; `ruff 0.17.5`; numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt via `bash scripts/bab_bootstrap.sh` (auto-invoked by quick/gate).

## INITIAL TASK MESSAGE (START HERE, 2026-11-16T01:00:30Z) — BINDING (DO NOT IGNORE)

**Campaign P17 — Make the data-quality gate safe-by-default in the actual trading pipeline. This is the next session's sole focus and the only authorized starting point. Start at P17-1 immediately.**

Do **NOT**: restart P16/P17-1/P17-2 already-done work, re-triage the coverage map, create a parallel handoff doc, or spend the session on analysis/handoff/formatting/coverage-only work. **Analysis-only, handoff-only, formatting-only, and coverage-chasing turns are failed sessions.** Ship real production fixes with proof tests.

**Why this campaign (priority derived from repo identity):** this is a trading system, not a coverage exercise. A wrong/lax data-quality gate lets frozen or corrupt market data silently drive real positions. P16 fixed the *plumbing* (explicit `stale_run_threshold` no longer floored at 50; dict `quality` now parsed; `BABDataError` propagates from beta). **But the default safety posture is still unsafe and — critically — the actual trading entrypoints bypass the quality campaign entirely.** That is the live bottleneck.

### Live-verified current state (reproduce before editing)

- Explicit thresholds now honored: `stale_run_threshold=3` rejects a 4–49 equal-value run; dict `{"stale_run_threshold": 3}` is parsed. ✅ (P16 done)
- **Default `quality=True` is still "very lenient":** `_run_data_quality_campaign` (`data_loader.py:1536-1541`) uses `max_return_abs=10_000.0`, `max_gap_days=3650.0`, `stale_run_threshold=50`. A 100% (10,000%) single-period return and an 8-day frozen run **pass silently** by default. The `validate_returns_dataframe` docstring was *updated to match* the lenient behavior (data_loader.py:1715-1731), so docs and impl no longer contradict — but the defaults are still unsafe for production. ⚠️
- **The real pipeline never passes strict thresholds.** `BABStrategy._load_returns` (`strategy.py:236-246`) and the CLI (`cli.py:633-637`, `cli.py:710-714`) call `load_returns`/`load_prices` with **no** quality thresholds, so every real run inherits the lenient defaults. ⚠️ (open bottleneck)
- **`load_prices` hardcodes `quality=False`** on both its load and final validation (`data_loader.py:2391, 2412, 2433`), so the price→returns path runs **no quality campaign at all** — gaps, frozen prices, and absurd returns reach the strategy unchecked. ⚠️ (open bottleneck)

### P17-1 (execute first) — strict, explicit safety defaults + wire them through the real pipeline

1. **Characterization tests first (must FAIL on HEAD, pass after fix).** Add to `tests/test_bab_quality_threshold_contract.py` (or a new `tests/test_bab_pipeline_safety_contract.py`):
   - default `quality=True` **rejects** a 100% return (`df.iloc[2,0]=100.0`) with `BABDataError` match `Implausible return`;
   - default `quality=True` **rejects** a >7-day gap;
   - `BABStrategy(returns_df=frozen_df).run()` raises `BABDataError` (frozen column) — proving the pipeline actually enforces the gate;
   - CLI dry-run with a frozen/implausible CSV exits non-zero.
   Run them and record the RED failures in the ledger. A test that cannot fail is worse than no test.
2. **Reconcile defaults to the safe contract.** In `_run_data_quality_campaign` (data_loader.py:1536-1541) change `None` defaults to `max_return_abs=20.0`, `max_gap_days=7.0`, `stale_run_threshold=3`. Update the docstring (data_loader.py:1715-1731) and the inline comments that justify the old lenient `10000/3650/50`. Keep `quality=False` as the explicit opt-out and keep threshold `0` disabling the stale check.
3. **Stop bypassing the gate in the real pipeline.** Thread explicit, safe thresholds through `BABStrategy._load_returns` and the CLI loaders so `run()` and `--from-prices`/`--data` actually enforce them (pass a strict `quality` dict or explicit kwargs from config/CLI defaults). Make `load_prices` validate its converted returns with the quality campaign **on** (not `quality=False`), using safe defaults, unless the caller explicitly opts out.
4. **Fix the tests that encode the old lax contract, not the fix.** Search and update every caller/test that assumes 10000/3650/50: `tests/test_bab_quality_threshold_contract.py` (`TestLenientDefaultsAreHonored` currently *asserts* the lax behavior — invert it), the robustness/stress suites that feed degenerate constant columns, and `tests/test_validation_performance.py` oracle (`_oracle_quality`). A test that masks the fix is a defect.
5. **No undocumented escape hatch.** Do not re-add a lenient default or a `max(...,50)` floor. If full-gate compatibility coupling is unavoidable, keep the stricter behavior, document the migration, and put any compatibility switch behind an explicit opt-in kwarg.
6. **Proof obligation:** for *each* changed guard (return/gap/stale default + pipeline wiring + `load_prices` gate), record one test that is RED on HEAD and GREEN after, with exact commands/results in the ledger.

### P17-2 — convert remaining reachable bucket-B edges into targeted behavior tests

Only after P17-1. Use fakes/mocks; add behavior assertions, not smoke tests; rerun the full gate per batch. The 91 missed statements are a checklist, not the goal:

- `execution.py:139-141` Timestamp-key fallback; `182-185` Timestamp-indexed ADV; `555-556` non-finite numpy float JSON sanitize (`allow_nan=False`).
- `portfolio.py:152-153` extreme-weight clipping; `170-177` dollar-neutral `need_fix` renorm under one-sided underflow.
- `cli.py:589-590` unknown adapter; `746-748` invalid output path.
- `reconciliation.py:309` empty-column early return.
- `data_sources.py:480-481, 499-500, 507-508` timezone/format edges.
- `data_loader.py` (37 lines) mixed-dtype slow path, finite-fraction boundary, stale-run boundary, datetime dayfirst retry/error wrap, multi-source fallback chains (280-292, 666-667, 718-719), empty/malformed CSV (422-423, 837-838), batch fetch error paths.
- `signals.py:37` object dtype after numeric coercion.

### P17-3 — delete or justify bucket-C dead branches

Do not add tests to "buy" coverage. Candidates: `beta.py` 125, 163, 170-171, 189, 435-436, 552-556; `execution.py:1287-1288`; `portfolio.py:180`; `metrics.py:94`; `signals.py:75`; `reconciliation.py:82-83`; `replay.py:172`; `cli.py:803-804`. Delete only with a concrete unreachability proof in the commit/test rationale; otherwise document why defensive. **Never delete reachable safety behavior.**

### P17-4 — prove performance, then continue to the next real defect

Run `python3 scripts/perf_baseline.py --check` (rerun once if noisy), record exact metrics, refresh this file with timestamp/HEAD/tree/ledger/coverage evidence, then immediately start the next real correctness or safety defect. **Never stop at "campaign complete."**

### Hard gates every session (repo root, in order)

```bash
python3 -m ruff check .                 # must pass
bash scripts/bab_gate.sh                # full suite + coverage, must be GREEN (~2.5 min)
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh   # P14 release floor must hold
```

### Non-goals (do not pursue)

- ❌ Adding type annotations (ANN excluded by policy).
- ❌ Refactoring defensive try/except patterns (BLE/TRY excluded).
- ❌ Lowering the coverage floor — add tests, don't lower the bar.
- ❌ Coverage-against-dead-lines turns substituting for correctness work (see P17-3).

### Bottleneck removal status

- ✅ Gate runs parallel by default (`-n $(nproc) --dist loadscope`, coverage core=sysmon) — ~2.2 min vs ~16 min serial; verified this refresh.
- ✅ `scripts/bab_bootstrap.sh` auto-installs missing deps — no manual setup.
- ✅ No flaky tests; the 35 skipped are explicit `pytest.mark.skip` (known gaps).
- ✅ P16 correctness plumbing done: explicit thresholds honored, dict `quality` parsed, `BABDataError` propagates from beta; ruff clean; gate GREEN at `99a841b`.
- ⚠️ **Open bottleneck (P17-1 fixes it):** the quality gate is strict only when a caller explicitly opts in; `BABStrategy`/CLI pass no thresholds and `load_prices` hardcodes `quality=False` — so **production runs enforce no implausible-return / gap / frozen-data guard**. This is the single most dangerous remaining gap in the repo.
- ⚠️ Stale-handoff bottleneck removed: this refresh re-stamped HEAD/`gate` evidence (previous file cited HEAD `65fe0d3` and a 00:09:32Z gate that no longer matched `99a841b`); a future agent would have chased a dead baseline.

### Session ledger (append one line per session; keep it honest)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-16T01:00:30Z | 99a841b | Handoff refresh: live-verified `ruff` clean + gate GREEN (6,153 passed / 35 skipped / 132.01s / 99%) at HEAD `99a841b`; confirmed P16-3 landed (explicit thresholds + dict parsing) and that lenient defaults + un-wired pipeline/`load_prices quality=False` remain; restamped binding campaign **P17** (safe-by-default quality gate wired through strategy/CLI). No code change this turn. | GREEN @01:00:30Z |

---

**Next agent**: Start with P17-1, step 1 — write the RED characterization tests and confirm they fail on HEAD (`99a841b`). Then fix in order (safe defaults → wire through `BABStrategy`/CLI/`load_prices` → update lax-contract tests). Rerun `bash scripts/bab_gate.sh` after each fix and keep it GREEN. Then proceed to P17-2. Record your session line in the ledger before finishing.