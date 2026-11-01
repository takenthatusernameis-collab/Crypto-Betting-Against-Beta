# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
# MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

**HANDOFF_TIMESTAMP:** 2026-11-01T07:37:26Z
**REPO:** Crypto-Betting-Against-Beta
**PRIORITY:** BAB-FIRST (strategies/betting_against_beta/) — betting_against_beta inferred from repo name

---

## >>> COPY/PASTE THIS AS THE VERY FIRST MESSAGE TO NEXT AGENT <<<

```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE | COVERAGE MAXIMIZED | NO IDLE TURNS
TIMESTAMP: 2026-11-01T07:37:26Z

VERIFIED STATE (2026-11-01T07:37:26Z):
- BAB suite: 1318 passed, 7 skipped, 0 failed (FULLY GREEN, RC=0)
- Coverage ceiling reached: 98% total, 45 misses across 2549 stmts — ALL provably unreachable dead code (do NOT chase)
- Per-module known ceilings: beta.py 94% (16 unreachable), data_loader.py 97% (9), portfolio.py 97% (8), strategy.py 98% (3), signals.py 98% (2), config/costs/metrics/regime smaller unreachable counts. Bottlenecks removed.
- Non-BAB: 2 pre-existing infra failures in test_controller_progress_accounting.py — must not increase.

BOTTLENECKS: NONE HITABLE. Every cycle must be substantive BAB work.

CAMPAIGN: HEAVY HARDENING — NO IDLE TURNS. Every turn must produce substantive BAB changes. Treat coverage ceiling as hard dead-end.

IMMEDIATE ACTIONS (CONCRETE, DO IN ORDER):
1. GATE FIRST: run BAB suite+coverage gate (commands below). Confirm GREEN.
2. ADVERSARIAL E2E SWEEP (HEAVY): add/strengthen tests for multi-asset, regime shifts, quantile/decile extremes, NaN/inf/mixed dtypes, sparse history, single-asset/universe shrink, all-long/all-short, min-history, liquidity shocks. Validate 1-day lag, dollar-neutrality, finiteness end-to-end.
3. NUMERICAL HARDENING: stress rolling beta (winsorization/clipping/EPS/re-normalization/residuals), portfolio sizing under degeneracy, signals/deciles/quantiles edge cases. Add property-style checks where cheap and deterministic.
4. INVARIANT AUDIT: verify (1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking, finiteness, BAB-specific errors, no bare except:). Fix minimally with tests.
5. FAILURE MODES: cover data quality gaps, missing columns/indexing/alignment, benchmark edges, cost/transaction edges. Deterministic fixtures only.

MANDATE (STRICT):
1. GATE FIRST EVERY TURN: run BAB suite+coverage gate. Must stay GREEN (>=1318 passed, >=7 skipped, 0 failed). Coverage >=98% / <=45 misses. NO REGRESSIONS.
2. DO NOT CHASE UNREACHABLE: 45 misses documented unreachable — reject with evidence, move to hardening.
3. NO IDLE/DOCS-ONLY/FILE-COUNT. EVERY TURN substantive BAB work OR explicit evidence why impossible.
4. Non-BAB only if DIRECTLY blocks BAB gate with evidence.
5. Preserve invariants, enforce finiteness, BAB-specific errors, NO bare except:. No semantic changes to pass coverage.
6. MOMENTUM REQUIRED: if tests missing for identified edge case, write them + harden code minimally. Never stop at explanation.

VERIFICATION COMMANDS (RUN FIRST):
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
rm -f .coverage
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 - <<'PYEOF'
import glob,sys,coverage,pytest
ROOT="/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta"
sys.path.insert(0,ROOT)
files=sorted(glob.glob(ROOT+"/tests/test_bab*.py"))+[ROOT+"/tests/test_betting_against_beta_costs.py",ROOT+"/tests/test_betting_against_beta.py"]
cov=coverage.Coverage(source=[ROOT+"/strategies/betting_against_beta"],data_file=None)
cov.start()
rc=pytest.main(["-q","-p","no:cacheprovider"]+files)
cov.stop()
cov.report(show_missing=True)
raise SystemExit(rc)
PYEOF
PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:$PWD python3 -m pytest -q -p no:cacheprovider tests/test_bab*.py tests/test_betting_against_beta_costs.py tests/test_betting_against_beta.py 2>&1 | tail -2

RULES: GATE GREEN ALWAYS. NO CHASING UNREACHABLE (ceiling 98%). HEAVY WORK MANDATORY. MOMENTUM REQUIRED. END ONLY IF GATE GREEN + SUBSTANTIVE BAB HARDENING/TESTS DONE OR BLOCKED WITH EVIDENCE.
```

## BOTTLENECKS REMOVED (unreachable — do not chase)
- beta.py (16): guards/returns/LinAlgError unreachable for finite inputs (94% ceiling)
- config.py (2), costs.py (2), strategy.py (3): freeze-except/unreachable guards
- data_loader.py (9), metrics.py (2), portfolio.py (8), signals.py (2), regime.py (1): all unreachable

## INVARIANTS
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta>=60 default, ranking
- Finiteness, BAB-specific errors, no bare except:
- Deterministic offline tests
- >=1318 passed, >=7 skipped, 0 failed
- Coverage 98% / 45 misses (must not increase)
- Pre-existing non-BAB failures must not increase

## HANDOFF METADATA
- Single durable handoff. Campaign: heavy BAB hardening (adversarial E2E/integration/stress/robustness/performance/edge cases/invariant enforcement). Coverage dead-end. Momentum mandatory. Start with copied message above.
- Last verified: 2026-11-01T07:37:26Z (1318 passed, 7 skipped, 0 failed, 98% cover / 45 misses; non-BAB infra baseline unchanged at 2 pre-existing failures in test_controller_progress_accounting.py).
