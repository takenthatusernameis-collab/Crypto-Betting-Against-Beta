# NEXT AGENTIC SESSION — BINDING TASK MESSAGE
**Timestamp (UTC):** 2026-11-17T14:56:31Z
**Repo:** `Crypto-Betting-Against-Beta` — Frazzini–Pedersen *Betting Against Beta* crypto market-neutral trading system
**Git HEAD:** `73e4db2` on `main` (clean tree; only `HANDOFF.md` changed since GREEN baseline `5ed651f`)

---

## 🎯 MISSION: P19-7 Milestone 1 — HARDEN 18 BROAD `except Exception` SITES
**Non-negotiable:** Behavior-preserving only. Every site → **(A) intentional contract** (inline invariant + regression test) **OR** **(B) narrowed/surfaced** (regression test proving identical happy-path + failure now surfaces). **Module-by-module; full gate + 98.5% floor GREEN after each module.**

### PRIORITIZATION BY REPO IDENTITY (LIVE-MONEY-FIRST — NEVER REORDER)
1. `reconciliation.py` (1 site) — cost reconciliation, fills-to-backtest gate
2. `data_sources.py` (3 sites) — real-time feed freshness, ticker fetch, tz conversion
3. `portfolio.py` (6 sites) — signal cleaning, portfolio construction, beta neutrality
4. `execution.py` (8 sites) — cost-model resolver, date keys, ADV map, fill parsing, beta reindex, live order submission

---

## 📋 MILESTONE 1 SITE LEDGER (FILL EVERY ROW — CLASSIFICATION + LOCKING TEST + STATUS)

| # | Site | Current Behavior (Ground-Truthed) | Classification (A/B) | Locking Test (Name + File) | Status |
|---|------|-----------------------------------|----------------------|----------------------------|--------|
| 1 | `reconciliation.py:131` | `_date_key`: `pd.Timestamp(date).isoformat()` else `str(date)` | | | |
| 2 | `data_sources.py:376` | `CCXTFeed.fetch_latest`: ticker fetch fails → `raise BABDataError(...) from exc` | | | |
| 3 | `data_sources.py:478` | `validate_freshness`: `pd.to_datetime(idx)` fails → `raise BABDataError` | | | |
| 4 | `data_sources.py:506` | `validate_freshness`: tz convert fails → `idx_utc=idx` (silent fallback) | | | |
| 5 | `portfolio.py:30` | `_clean_signal_value`: `int(f)` fails → `0` | | | |
| 6 | `portfolio.py:107` | inner `apply(pd.to_numeric)` fails → retry | | | |
| 7 | `portfolio.py:110` | nested retry fails → per-column coerce | | | |
| 8 | `portfolio.py:115` | per-column coerce fails → `0.0` | | | |
| 9 | `portfolio.py:118` | outer coerce fails → **return all-zero frame** (hides defect) | | | |
| 10 | `portfolio.py:165` | build fails → `raise BABPortfolioError(...) from exc` | | | |
| 11 | `execution.py:346` | `configure_paper_adapter`: cost-model resolver raises → `prices=adv=None`, then cfg fallback | | | |
| 12 | `execution.py:375` | `_date_key`: `pd.Timestamp(date).isoformat()` else `str(date)` | | | |
| 13 | `execution.py:398` | `_as_timestamp`: `pd.Timestamp(value)` else `None` | | | |
| 14 | `execution.py:458` | `order_batches_from_weights`: adv-map build fails → `adv_map={}` | | | |
| 15 | `execution.py:467` | per-row `date_key` fallback `str(date)` | | | |
| 16 | `execution.py:831` | `_paper_pnl`: fill date unparseable → `continue` (fill skipped) | | | |
| 17 | `execution.py:888` | `execute`: betas reindex fails → `betas=None` | | | |
| 18 | `execution.py:1250` | `CCXTConnector.submit_order`: live order exception → `LiveFill(status="rejected", reason=...)` | | | |

---

## ⚡ FAST INNER LOOP (USE IT — DO NOT RUN FULL GATE AFTER EVERY EDIT)
```bash
# Quick sanity (~seconds): ruff + targeted trio + smoke
bash scripts/bab_quick.sh

# Targeted per module (run the relevant file):
# reconciliation → pytest -q tests/test_bab_reconciliation*.py
# data_sources   → pytest -q tests/test_bab_data_sources*.py
# portfolio      → pytest -q tests/test_bab_portfolio*.py
# execution      → pytest -q tests/test_bab_execution*.py
```

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
- **Handoff-only commit = automatic failure.** This milestone is NOT done until diff contains **substantive product `.py` + test changes** for all 18 sites.
- Every row in the ledger above **must** have Classification + Locking Test filled and the regression test committed.
- Even sites already surfacing correctly (e.g., `data_sources.py:376`) are **Class A** and **still need a regression test pinning the surfacing behavior**.
- **Module-by-module only.** Finish all sites in one module → run full gate + 98.5% floor GREEN → record before/after broad/silent counts → move to next module.
- **Order:** `reconciliation.py` (1) → `data_sources.py` (3) → `portfolio.py` (6) → `execution.py` (8) — smallest/simplest first.

---

## 📂 TEST HOMES & NAMING CONVENTION
| Module | Test Files | New Test File Pattern |
|--------|------------|----------------------|
| `reconciliation.py` | `tests/test_bab_reconciliation*.py` | `tests/test_bab_p19_7_reconciliation_exceptions.py` |
| `data_sources.py` | `tests/test_bab_data_sources*.py` | `tests/test_bab_p19_7_data_sources_exceptions.py` |
| `portfolio.py` | `tests/test_bab_portfolio*.py` | `tests/test_bab_p19_7_portfolio_exceptions.py` |
| `execution.py` | `tests/test_bab_execution*.py` | `tests/test_bab_p19_7_execution_exceptions.py` |

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

---

## 🎬 START HERE — FIRST ACTION
```bash
# 1. Verify baseline (should be clean)
git status --short --branch

# 2. Start with reconciliation.py (1 site) — smallest module
#    Edit: strategies/betting_against_beta/reconciliation.py:131 (_date_key)
#    Test: Add to tests/test_bab_p19_7_reconciliation_exceptions.py
#    Run: bash scripts/bab_quick.sh → pytest -q tests/test_bab_reconciliation*.py
#    Gate: Full gate + 98.5% floor at module boundary
```

**DO NOT HAND OFF UNTIL ALL 18 SITES ARE CLOSED WITH TESTS AND THE FULL GATE IS GREEN.**

---

*This is the single durable task message. Update `HANDOFF.md` ledger as you close each site. No parallel docs.*