# NEXT AGENTIC WORK SESSION HANDOFF
**Timestamp:** 2026-11-16T01:17:06Z
**Project:** Crypto-Betting-Against-Beta (Betting Against Beta - BAB strategy for crypto)
**Repository:** /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta

---

## CANONICAL DURABLE HANDOFF → [`HANDOFF.md`](HANDOFF.md)

**READ HANDOFF.md IN FULL BEFORE STARTING.** It is the single source of truth.

### Current Binding Task (from HANDOFF.md INITIAL TASK MESSAGE @ 2026-11-16T01:03:44Z)

**Campaign P17 — Make the data-quality gate safe-by-default in the actual trading pipeline.**

**Sole focus: P17-1 (execute first, do not advance until Definition of Done is fully checked)**

---

### P17-1 — Strict, explicit safety defaults + wire them through the real pipeline

**Why (priority from repo identity):** This is a trading system, not a coverage exercise. A wrong/lax data-quality gate lets frozen or corrupt market data silently drive real positions. P16 fixed the plumbing but the default safety posture is still unsafe and the real trading entrypoints bypass the quality campaign entirely.

**Live-verified bottlenecks at HEAD `dc58017`:**
- Default `quality=True` uses `max_return_abs=10_000.0`, `max_gap_days=3650.0`, `stale_run_threshold=50` — 100% returns and 8-day frozen runs pass silently
- `BABStrategy._load_returns` and CLI loaders pass **no** quality thresholds → inherit lenient defaults
- `load_prices` hardcodes `quality=False` on all loads → price→returns path runs **no quality campaign at all**

**Non-negotiable steps (in order):**

1. **Characterization tests first (must FAIL on HEAD, pass after fix).** Add to `tests/test_bab_pipeline_safety_contract.py`:
   - Default `quality=True` **rejects** 100% return with `BABDataError` match `Implausible return`
   - Default `quality=True` **rejects** >7-day gap
   - `BABStrategy(returns_df=frozen_df).run()` raises `BABDataError` (frozen column)
   - CLI dry-run with frozen/implausible CSV exits non-zero
   - *Run them, record RED failures in ledger. A test that cannot fail is worse than no test.*

2. **Reconcile defaults to safe contract** in `_run_data_quality_campaign` (`data_loader.py:1537-1541`):
   - Change `None` defaults to `max_return_abs=20.0`, `max_gap_days=7.0`, `stale_run_threshold=3`
   - Update docstring lenient-default paragraphs in `validate_returns_dataframe` (`data_loader.py:1679+`)
   - Keep `quality=False` as explicit opt-out; keep threshold `0` disabling stale check

3. **Stop bypassing the gate in the real pipeline:**
   - Thread explicit safe thresholds through `BABStrategy._load_returns` and CLI loaders
   - Make `load_prices` validate converted returns with quality campaign **ON** (not `quality=False`), using safe defaults, unless caller explicitly opts out

4. **Fix tests encoding old lax contract:**
   - Invert `TestLenientDefaultsAreHonored` in `tests/test_bab_quality_threshold_contract.py` (line 113)
   - Update robustness/stress suites and `tests/test_validation_performance.py` oracle (`_oracle_quality`)
   - *A test that masks the fix is a defect.*

5. **No undocumented escape hatch.** No lenient default re-add, no `max(...,50)` floor.

6. **Proof obligation:** For each changed guard, record one test that is RED on HEAD and GREEN after, with exact commands/results in ledger.

---

### Definition of Done for P17-1 (all must be true)

- [ ] RED characterization tests committed/run; failures recorded in ledger
- [ ] `data_loader.py` defaults are `20.0 / 7.0 / 3`; docstring/comments match
- [ ] `BABStrategy.run()` and CLI enforce gate (no lenient bypass); `load_prices` runs campaign ON by default
- [ ] `TestLenientDefaultsAreHonored` inverted; no test asserts old lax contract
- [ ] `python3 -m ruff check .` clean AND `bash scripts/bab_gate.sh` GREEN (≥ 6,153 passed / 35 skipped, 99%)
- [ ] One RED→GREEN proof per changed guard recorded in ledger

---

### Hard Gates Every Session (run in order, repo root)

```bash
python3 -m ruff check .                 # must pass
bash scripts/bab_gate.sh                # full suite + coverage, must be GREEN (~2.2 min)
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh   # P14 release floor must hold
```

---

### Non-Goals (DO NOT PURSUE)

- ❌ Adding type annotations (ANN excluded by policy)
- ❌ Refactoring defensive try/except patterns (BLE/TRY excluded)
- ❌ Lowering the coverage floor — add tests, don't lower the bar
- ❌ **Coverage-only work substituting for correctness work** (HANDOFF.md: "Analysis-only, handoff-only, formatting-only, and coverage-chasing turns are failed sessions")

---

### Session Ledger (append one line per session; keep it honest)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-16T01:00:30Z | 99a841b | Handoff refresh: live-verified `ruff` clean + gate GREEN (6,153 passed / 35 skipped / 132.01s / 99%) at HEAD `99a841b`; confirmed P16-3 landed; restamped binding campaign **P17** | GREEN @01:00:30Z |
| 2026-11-16T01:03:44Z | dc58017 | Handoff re-verification: `ruff` clean + gate GREEN (6,153 passed / 35 skipped / 131.89s / 99%) at HEAD `dc58017`; re-confirmed open bottlenecks; re-stamped binding **P17-1** with Definition of Done | GREEN @01:01:20Z |
| 2026-11-16T01:17:06Z | dc58017 | **This session:** Synchronized NEXT_SESSION_HANDOFF.md to canonical HANDOFF.md; confirmed P17-1 is binding initial task | — |

---

**NEXT AGENT: Start with P17-1, step 1 — write RED characterization tests in `tests/test_bab_pipeline_safety_contract.py` and confirm they fail on HEAD (`dc58017`). Then fix in order. Rerun `bash scripts/bab_gate.sh` after each fix and keep it GREEN. Only move to P17-2 once P17-1 Definition of Done is fully checked. Record your session line in the ledger before finishing.**