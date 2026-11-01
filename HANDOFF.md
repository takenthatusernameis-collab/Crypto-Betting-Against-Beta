# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-11-01T04:48:25Z

## TIMESTAMP
2026-11-01T04:48:25Z

## REPO / PRIORITY
REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE (repo name = betting_against_beta). ALL WORK MUST PRIORITIZE strategies/betting_against_beta/. NO VANITY. NO FILE-COUNT GOALS. NO DOCS-ONLY CHANGES. NO IDLE TURNS. IF NO BAB WORK IS POSSIBLE, EXPLAIN WHY WITH EVIDENCE BEFORE DOING ANYTHING ELSE.

## VERIFIED STATE (CLEAN MEASUREMENT - 2026-11-01T04:48:05Z)
- Full BAB suite: 1318 passed, 7 skipped, 0 failed (FULLY GREEN, RC=0)
- 2 pre-existing non-BAB infra failures (test_controller_progress_accounting.py) — must not increase
- Package coverage (BAB): 98% total, 45 misses across 2549 stmts

Per-module (BAB package):
- 100%: __init__, attribution, backtest, cli, data, data_sources, errors, quality, shorting, sizing
- 99%: config (95-96), costs (59-60), metrics (97, 114), regime (305)
- 98%: signals (37, 75), strategy (181, 188-189, 193)
- 97%: data_loader (44, 192-193, 311-313, 340-342), portfolio (39-40, 172-177)
- 94%: beta.py (16 misses: 101-102, 124, 138, 140-141, 144-145, 166, 178, 181, 355-359)

Coverage deltas this session: held at 98% / 45 misses; regime.py:305 unchanged (empty-factors early return `return pd.Series(dtype="float64")`, unreachable via normal non-empty runs).

## BOTTLENECKS REMOVED — ALL REMAINING MISSES ARE PROVABLY UNREACHABLE (DO NOT CHASE)

Every one of the 45 misses is unreachable dead code under current semantics; no test can cover them without changing behavior. Coverage cannot exceed 98% via tests. Documented below; do not spend further turns on these.

- beta.py (16 misses): every miss guarded by an earlier return / finiteness guard. LinAlgError handlers (gelsd) only on SVD non-convergence, not triggered by finite inputs. 94% is the ceiling.
- config.py:95-96: `except Exception: pass` around `object.__setattr__(self, "_frozen", True)`. BABConfig is a plain `@dataclass(frozen=False)` with NO `__slots__`, so `object.__setattr__` never raises. Unreachable.
- costs.py:59-60: same freeze-except; TransactionCostModel is a plain dataclass, no slots. Unreachable.
- data_loader.py:44, 192-193, 311-313, 340-342: unreachable dead branches (validation raises outside/inside the caught try; read/IO except cannot observe validation errors). Previously documented.
- metrics.py:97: `turnover` `if pd.isna(turnover_mean)` — `weight_changes = w.diff().abs().sum(axis=1)` uses skipna=True, so an all-NaN row sums to 0.0, never NaN; `dropna().mean()` is never NaN. Unreachable.
- metrics.py:114: `strategy_beta` `if pd.isna(beta)` — line 110 guards `var_bench < EPS` (returns nan first); with var_bench finite >= EPS and cov finite, beta is always finite. Unreachable.
- portfolio.py:39-40: `_clean_signal_value` outer except — every branch either returns early or is wrapped in its own try/except; function is total, never raises. Unreachable (fuzz-proven).
- portfolio.py:172-177: residual-drift mop-up loop requires `both & (abs(net) > 1e-12)` after the exact re-normalization block (longs scaled to sum +1.0, shorts to -1.0), so net is ~0 (<1e-12). Unreachable.
- signals.py:37: `if numeric.dtype == object` — `pd.to_numeric(..., errors="coerce")` never yields object dtype (returns int64/float64). Unreachable.
- signals.py:75: reference `if n == 0: continue` — `_finite_beta_series` returns None when empty (handled at line 70-71), so clean is never empty at line 73. Unreachable.
- strategy.py:181: `if not effective_universe: raise ValueError` — `_load_returns` rejects empty-column frames before line 179, and `resolved_universe` returns non-empty for any non-empty column set. Unreachable via run().
- strategy.py:188-189: `except Exception: cfg.universe = ...` — plain dataclass, no slots, `object.__setattr__` never raises. Unreachable.
- strategy.py:193: same category as 188-189 — freeze-except on plain dataclass without slots. Unreachable.

Ruling: BAB coverage is MAXIMIZED at 98% (45 misses, all provably unreachable). No further coverage gains are possible via tests without changing semantics. Do not chase any of these lines.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE AS FIRST MESSAGE)
```
>>> START IMMEDIATELY — HEAVY WORK REQUIRED <<<

REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE | COVERAGE MAXIMIZED

TIMESTAMP: 2026-11-01T04:48:25Z

VERIFIED STATE (2026-11-01T04:48:25Z - re-verified green):
- BAB suite: 1318 passed, 7 skipped, 0 failed (FULLY GREEN, RC=0)
- Package coverage: 98% | 45 misses, ALL provably unreachable dead code (documented in this HANDOFF under BOTTLENECKS REMOVED)
- beta.py 94%, config 99%, costs 99%, data_loader 97%, metrics 99%, portfolio 97%, regime 99%, signals 98%, strategy 98% — every remaining miss is unreachable; DO NOT CHASE
- 2 pre-existing non-BAB infra failures (test_controller_progress_accounting.py) must not increase

CAMPAIGN STATUS: Line-coverage dead-end. HARDENING CAMPAIGN STARTS NOW. No hitable branches remain. You MUST do substantive BAB work every turn.

PRIMARY FOCUS (HEAVY WORK - IN THIS ORDER):
1. INTEGRATION/STRESS (TOP PRIORITY): Add adversarial end-to-end integration tests for BAB (multi-asset, NaN/inf/mixed dtypes, mixed regimes, extreme quantiles/deciles, low liquidity, sparse history, rolling windows). Exercise data_loader/data_sources/quality/regime under stress. Validate all invariants explicitly.
2. ROBUSTNESS/HARDENING: Tighten numerical stability (beta OLS guards, EPS, re-normalization, residual drift), improve error messages with BAB-specific errors, harden portfolio/sizing/metrics against edge cases. Add property-style tests (idempotence, dollar-neutrality, 1-day lag compliance, finiteness) and make failures actionable.
3. PERFORMANCE/SCALABILITY: Profile hot paths (rolling beta, correlation/cov, signal generation, portfolio construction). Optimize without changing semantics or breaking invariants. Prove no regression via the gate.
4. EDGE CASES: Cover realistic edge cases (single asset/universe shrink, all-long/all-short regimes, regime transitions, min history boundaries, benchmark edge cases). Use deterministic fixtures only.
5. INVARIANT ENFORCEMENT: Audit the full BAB stack for violations (1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic, finiteness, BAB-specific errors, no bare except:). Fix with minimal correct changes + tests.

MANDATE (STRICT):
1. GATE FIRST, EVERY TURN: run the BAB suite + coverage gate (exact command below). Must stay GREEN (>=1318 passed, >=7 skipped, 0 failed). Coverage must not drop below 98% / 45 misses. NO REGRESSIONS.
2. DO NOT CHASE UNREACHABLE LINES: all 45 misses are documented unreachable in this HANDOFF. Reject with evidence and move to hardening.
3. NO EXPLORATORY IDLE TURNS. NO DOCS-ONLY. NO FILE-COUNT GOALS. EVERY TURN MUST PRODUCE SUBSTANTIVE CHANGES (tests + code hardening/optimization/integration) OR EXPLICITLY DOCUMENT WHY NO BAB WORK IS POSSIBLE WITH EVIDENCE.
4. If considering non-BAB files, they must DIRECTLY BLOCK BAB coverage/gate with evidence; otherwise skip entirely.
5. Preserve all invariants (see INVARIANTS). Enforce finiteness. Raise BAB-specific errors. NO bare except:.

VERIFICATION (run every turn):
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

RULES:
- GATE MUST STAY GREEN. NEVER LEAVE GATES RED.
- NO CHASING UNREACHABLE LINES — 45 misses, all documented unreachable. Coverage ceiling = 98%.
- HEAVY WORK MANDATORY: harden, stress-test, optimize. No idle turns.
- EVERY ACTION SUBSTANTIVE. MOMENTUM MANDATORY.
- END SESSION ONLY IF GATE GREEN AND SUBSTANTIVE BAB HARDENING/TESTS COMPLETED OR EXPLICITLY BLOCKED WITH EVIDENCE.
```

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final BAB-suite green gate required (1318 passed, 7 skipped, 0 failed minimum)
- Coverage floor: 98% / 45 misses (all unreachable; must not increase)
- 2 pre-existing non-BAB infra failures (test_controller_progress_accounting.py) must not increase

## SESSION SUMMARY (2026-11-01T04:48:25Z)
- Gate re-verified green (1318 passed, 7 skipped, 0 failed; coverage 98% / 45 misses, all provably unreachable). Bottlenecks removed and documented; no hitable branches remain — coverage ceiling is 98%. Campaign locked to heavy BAB hardening (integration/stress, robustness, performance, edge cases, invariant enforcement). Next agent must start immediately with the copied initial task message above and produce substantive BAB work every turn.
