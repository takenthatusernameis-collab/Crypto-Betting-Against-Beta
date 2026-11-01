# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)
# MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

**HANDOFF_TIMESTAMP:** 2026-11-01T06:33:29Z
**REPO:** Crypto-Betting-Against-Beta
**PRIORITY:** BAB-FIRST (strategies/betting_against_beta/) — betting_against_beta inferred from repo name

---

## >>> COPY/PASTE THIS AS THE VERY FIRST MESSAGE TO NEXT AGENT <<<

```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE | COVERAGE MAXIMIZED
TIMESTAMP: 2026-11-01T06:33:29Z

VERIFIED STATE (2026-11-01T06:33:29Z - re-verified green):
- BAB suite: 1318 passed, 7 skipped, 0 failed (FULLY GREEN, RC=0)
- Package coverage (BAB): 98% total, 45 misses across 2549 stmts — ALL provably unreachable dead code
- Per-module: beta.py 94% (16 unreachable), config.py 99% (2 unreachable), costs.py 99% (2 unreachable), data_loader.py 97% (9 unreachable), metrics.py 99% (2 unreachable), portfolio.py 97% (8 unreachable), regime.py 99% (1 unreachable), signals.py 98% (2 unreachable), strategy.py 98% (3 unreachable) — DO NOT CHASE
- 2 pre-existing non-BAB infra failures (test_controller_progress_accounting.py) must not increase

BOTTLENECKS: REMOVED. Coverage ceiling 98%. No hitable branches remain. No staged/blocked changes (git clean, only untracked __pycache__).

CAMPAIGN: HEAVY HARDENING — NO IDLE TURNS. Every turn must produce substantive BAB changes.

PRIMARY FOCUS (IN ORDER):
1. INTEGRATION/STRESS: Adversarial E2E (multi-asset, NaN/inf/mixed dtypes, mixed regimes, extreme quantiles/deciles, low liquidity, sparse history, rolling). Stress data_loader/data_sources/quality/regime. Validate invariants.
2. ROBUSTNESS/HARDENING: Numerical stability (beta OLS, EPS, re-normalization, residual drift), BAB-specific errors, harden portfolio/sizing/metrics. Property-style (idempotence, dollar-neutrality, 1-day lag, finiteness).
3. PERFORMANCE/SCALABILITY: Profile hot paths (rolling beta/cov/corr, signals, portfolio). Optimize without semantic changes; prove no regression.
4. EDGE CASES: single asset/universe shrink, all-long/all-short, regime transitions, min history, benchmark edges (deterministic fixtures).
5. INVARIANT ENFORCEMENT: Audit (1-day lag, dollar-neutral, quantiles/deciles, beta>=60, ranking, finiteness, BAB errors, no bare except:). Fix minimally + tests.

MANDATE (STRICT):
1. GATE FIRST EVERY TURN: run BAB suite+coverage gate. Must stay GREEN (>=1318 passed, >=7 skipped, 0 failed). Coverage >=98% / <=45 misses. NO REGRESSIONS.
2. DO NOT CHASE UNREACHABLE: 45 misses documented unreachable — reject with evidence, move to hardening.
3. NO IDLE/DOCS-ONLY/FILE-COUNT. EVERY TURN substantive BAB work OR explicit evidence why impossible.
4. Non-BAB only if DIRECTLY blocks BAB gate with evidence.
5. Preserve invariants, enforce finiteness, BAB-specific errors, NO bare except:.

VERIFICATION:
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
- Single durable handoff. Campaign: heavy BAB hardening (integration/stress/robustness/performance/edge cases/invariant enforcement). Coverage dead-end. Momentum mandatory. Start with copied message above.
- Last verified: 2026-11-01T06:33:29Z (1318 passed, 7 skipped, 0 failed, 98% cover / 45 misses; non-BAB infra baseline unchanged at 2 pre-existing failures in test_controller_progress_accounting.py).
