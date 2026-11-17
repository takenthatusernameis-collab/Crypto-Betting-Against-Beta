# NEXT AGENTIC SESSION — BINDING TASK MESSAGE
**Timestamp (UTC):** 2026-11-17T15:45:00Z
**Repo:** `Crypto-Betting-Against-Beta` — Frazzini–Pedersen *Betting Against Beta* crypto market-neutral trading system
**Git HEAD:** `73e4db2` on `main` (clean tree; only `HANDOFF.md` and `tests/test_bab_p19_7_exception_hardening.py` changed since GREEN baseline `5ed651f`)

---

## 🎯 MISSION: P19-7 Milestone 1 — COMPLETE THE 8 REMAINING `except Exception` SITES IN `execution.py`
**Non-negotiable:** Behavior-preserving only. Every site → **(A) intentional contract** (inline invariant + regression test) **OR** **(B) narrowed/surfaced** (regression test proving identical happy-path + failure now surfaces). **Full gate + 98.5% floor GREEN after module completion.**

### PRIORITIZATION BY REPO IDENTITY (LIVE-MONEY-FIRST — NEVER REORDER)
**10 of 18 Milestone-1 sites are ALREADY DONE** with inline invariants + regression tests passing:
- `reconciliation.py` (1 site) — **DONE** (Class A total contract)
- `data_sources.py` (3 sites) — **DONE** (Class A surfacing ×2, Class B surfacing ×1)
- `portfolio.py` (6 sites) — **DONE** (Class A total ×1, Class B removed ×3, Class B surface ×1, Class A surfacing ×1)

**Remaining work: 8 sites in `execution.py` only** — this is the largest and most complex module, do it last per the module-by-module order.

---

## 📋 MILESTONE 1 SITE LEDGER (FILL REMAINING 8 ROWS — CLASSIFICATION + LOCKING TEST + STATUS)

| # | Site | Current Behavior (Ground-Truthed) | Classification (A/B) | Locking Test (Name + File) | Status |
|---|------|-----------------------------------|----------------------|----------------------------|--------|
| 1 | `execution.py:346` | `configure_paper_adapter`: cost-model resolver raises → `prices=adv=None`, then cfg fallback | | | **TODO** |
| 2 | `execution.py:375` | `_date_key`: `pd.Timestamp(date).isoformat()` else `str(date)` | | | **TODO** |
| 3 | `execution.py:398` | `_as_timestamp`: `pd.Timestamp(value)` else `None` | | | **TODO** |
| 4 | `execution.py:458` | `order_batches_from_weights`: adv-map build fails → `adv_map={}` | | | **TODO** |
| 5 | `execution.py:467` | per-row `date_key` fallback `str(date)` | | | **TODO** |
| 6 | `execution.py:831` | `_paper_pnl`: fill date unparseable → `continue` (fill skipped) | | | **TODO** |
| 7 | `execution.py:888` | `execute`: betas reindex fails → `betas=None` | | | **TODO** |
| 8 | `execution.py:1250` | `CCXTConnector.submit_order`: live order exception → `LiveFill(status="rejected", reason=...)` | | | **TODO** |

**DONE sites (do not re-touch):**
| # | Site | Classification | Locking Test | Status |
|---|------|----------------|--------------|--------|
| 9 | `reconciliation.py:131` | **A (total)** | `test_date_key_fallback_contract` in `test_bab_p19_7_reconciliation_exceptions.py` | **DONE** |
| 10 | `data_sources.py:376` | **A (surfaced)** | `test_ticker_fetch_failure_surfaces_babdataerror` in `test_bab_p19_7_exception_hardening.py` | **DONE** |
| 11 | `data_sources.py:478` | **A (surfaced)** | `test_unparseable_object_index_surfaces_babdataerror` in `test_bab_p19_7_exception_hardening.py` | **DONE** |
| 12 | `data_sources.py:506` | **B (surface)** | `test_tz_failure_surfaces_instead_of_silent_fallback` in `test_bab_p19_7_exception_hardening.py` | **DONE** |
| 13 | `portfolio.py:30` | **A (total)** | `test_clean_signal_value_total_contract` in `test_bab_p19_7_portfolio_exceptions.py` | **DONE** |
| 14 | `portfolio.py:107` | **B (removed)** | unreachable — `pd.to_numeric(errors="coerce")` never raises | **DONE** |
| 15 | `portfolio.py:110` | **B (removed)** | unreachable — removed with #14 | **DONE** |
| 16 | `portfolio.py:115` | **B (removed)** | unreachable — removed with #14 | **DONE** |
| 17 | `portfolio.py:118` | **B (surface)** | `test_portfolio_construction_surfaces_on_coercion_failure` in `test_bab_p19_7_portfolio_exceptions.py` | **DONE** |
| 18 | `portfolio.py:165` | **A (surfaced)** | `test_portfolio_construction_failure_surfaces_babportfolioerror` in `test_bab_p19_7_portfolio_exceptions.py` | **DONE** |

---

## ⚡ FAST INNER LOOP (USE IT — DO NOT RUN FULL GATE AFTER EVERY EDIT)
```bash
# Quick sanity (~seconds): ruff + targeted trio + smoke
bash scripts/bab_quick.sh

# Targeted for execution module:
python3 -m pytest -q tests/test_bab_execution_p14_coverage.py tests/test_bab_execution_integration_r5.py tests/test_bab_execution_*.py
```

---

## ✅ HARD GATES (MACHINE-CHECKABLE DONE — RUN IN ORDER AT MODULE BOUNDARY)
```bash
python3 -m ruff check .
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate.log bash scripts/bab_gate.sh          # ~145s on 4 cores
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh             # never lower floor
```
**Evidence:** `grep -nE "^TOTAL\|failed\|passed\|skipped" /tmp/bab_gate.log`

---

## 🔒 ANTI-AVOIDANCE CONTRACT (AUTOMATIC FAILURE IF VIOLATED)
- **Handoff-only commit = automatic failure.** This milestone is NOT done until diff contains **substantive product `.py` + test changes** for all **8 remaining sites in `execution.py`**.
- Every remaining row in the ledger above **must** have Classification + Locking Test filled and the regression test committed.
- **Module-by-module only.** Finish all 8 sites in `execution.py` → run full gate + 98.5% floor GREEN → record before/after broad/silent counts.
- **Do not re-touch** the 10 DONE sites (reconciliation, data_sources, portfolio) — they are closed with tests passing.

---

## 📂 TEST HOMES & NAMING CONVENTION
| Module | Test Files | New Test File Pattern |
|--------|------------|----------------------|
| `execution.py` | `tests/test_bab_execution_*.py` | `tests/test_bab_p19_7_execution_exceptions.py` |

---

## 🚫 FORBIDDEN (AUTOMATIC FAILURE)
- Handoff-only commit / restating brief as deliverable / stopping after analysis without closing sites with tests
- Lowering coverage floor or adding ANN/type-style churn
- Deleting intentional leave-in-place contracts without concrete proof
- Touching 100%-closed safety paths without regression test + gate-green proof
- Re-touching the 2 rewritten tests at `tests/test_bab_data_loader_coverage_gaps.py` (~L6636, ~L8249)
- Mass-refactoring all 231 sites in one pass
- Editing `.github/workflows/*` (maintainer-only)
- Creating parallel handoff docs or committing probe/debug scratch scripts

---

## 📊 AUTHORITATIVE BASELINE (RE-RUN THIS SESSION — CODE UNCHANGED SINCE `5ed651f`)
- **Full gate @2026-11-17T14:46:59Z:** 6282 passed / 35 skipped / 0 failed / 6572 stmts / 0 missed / **100%** (145.15s, 4 cores, xdist)
- `ruff check .` → **PASS**
- `bab_reconcile_gate.sh` → **GREEN** (drift rc=2, clean rc=0, emit-only rc=0)
- `BAB_GATE_MIN_COVERAGE=98.5` floor **met by TOTAL 100%**
- **Quick gate @2026-11-17T15:45Z:** ruff PASS + 104 targeted + 195 smoke = **GREEN**
- **data_sources.py tests @2026-11-17T15:45Z:** `test_bab_p19_7_exception_hardening.py` — **5/5 PASS**

---

## 🎬 START HERE — FIRST ACTION
```bash
# 1. Verify baseline (should be clean)
git status --short --branch

# 2. Start with execution.py (8 sites) — largest module, do it last per module order
#    Test file: tests/test_bab_p19_7_execution_exceptions.py (create new)
#    Run: bash scripts/bab_quick.sh → pytest -q tests/test_bab_execution_*.py
#    Gate: Full gate + 98.5% floor at module boundary (after all 8 sites)

# Site-by-site order within execution.py (suggested simplest first):
#   1. execution.py:375  (_date_key - similar to reconciliation.py pattern)
#   2. execution.py:398  (_as_timestamp - similar pattern)
#   3. execution.py:467  (per-row date_key - similar pattern)
#   4. execution.py:346  (cost-model resolver fallback)
#   5. execution.py:458  (adv-map build fails)
#   6. execution.py:831  (fill date unparseable - Class B surface)
#   7. execution.py:888  (betas reindex fails)
#   8. execution.py:1250 (live order exception - Class A surfaced)
```

**DO NOT HAND OFF UNTIL ALL 8 REMAINING SITES IN `execution.py` ARE CLOSED WITH TESTS AND THE FULL GATE IS GREEN.**

---

*This is the single durable task message. Update `HANDOFF.md` ledger as you close each site. No parallel docs.*