# DELAY-ELIMINATION OVERRIDE — 2026-10-30

The existing instruction to “TOUCH >= 4 FILES” is an artificial throughput constraint. It can encourage unrelated edits and increase review/test time without improving BAB correctness. Supersede it as follows:

- Change only the smallest set of production/test files needed to address a demonstrated uncovered branch or defect. File count is not a success metric.
- Work one coherent branch family at a time. Run focused tests and module coverage immediately; run BAB suite after a related batch; run the full suite once at the milestone/final gate, not after every trivial test addition.
- Do not chase unreachable or structurally dead branches. Prove why a branch is unreachable under current imports/contracts, record it, and move to the next meaningful gap.
- If beta.py's remaining misses are not safely testable without weakening invariants, switch to the next highest-leverage module rather than repeatedly re-deriving the same coverage report.
- Keep one durable next task. Avoid timestamp-only handoff churn and repeated full test/coverage passes when HEAD and relevant files are unchanged.

Preserve BAB mathematics, lagging, neutrality, finiteness, benchmark/ranking invariants, deterministic offline tests, and the final full-suite green gate. This is an efficiency improvement, not a reduction in test rigor.

---

# HANDOFF - 2026-10-30T20:51:25Z (SINGLE DURABLE HANDOFF) - BETA.PY BOTTLENECK CRUSH

## TIMESTAMP
2026-10-30T20:51:25Z

## INITIAL TASK MESSAGE FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY #1: strategies/betting_against_beta/beta.py | REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE
ATTACK beta.py UNCOVERED BRANCHES (89%, ~29 MISS). CRUSH HARDEST FIRST.
CHANGE ONLY SMALLEST NEEDED FILES; NO FILE-COUNT METRIC; NO DOCS-ONLY; NO TRIVIAL-ONLY.
TARGETS: beta.py >= 95% | TOTAL BAB >= 97%.
FULL SUITE MUST STAY GREEN. BAB SUITE MUST STAY GREEN.
FOCUS: estimate_betas fallthroughs/aliases, calculate_beta alignment/disjoint/mask/min_obs/linalg, calculate_beta_fast masks/degenerate/nonfinite/LinAlgError, _calc_rolling_beta_series degenerate/insufficient/empty, calculate_rolling_beta bad_cols/bench conversion/outer except/_finalize_betas.
MEASURE WITH COVERAGE, PROVE DELTA. DO HEAVY WORK.
```

## CAMPAIGN OBJECTIVE (NON-NEGOTIABLE)
Push BAB coverage toward >=97% by crushing beta.py (primary bottleneck). Momentum required - heavy substantive work every session.

## CURRENT STATE (VERIFIED)
- Full Suite: GREEN (1416 passed, 11 skipped)
- BAB tests (test_betting_against_beta*.py + test_bab_*.py): GREEN (1244 passed, 11 skipped)
- BAB coverage: ~96% (2514 stmts / ~106 miss)
- PRIMARY BOTTLENECK: beta.py 89% (29 misses)

## WORK COMPLETED THIS SESSION
- Verified gates and coverage focus on beta.py
- Exercised/validated branches (estimate_betas aliases/clamps, rolling_beta Series/list/bad/fallback/empty/degenerate, calculate_beta alignment/disjoint/mismatch/masks/min_obs/constant x/None raises, calculate_beta_fast masks/degenerate/empty/min_obs/nonfinite/bad inputs, _calc_rolling_beta_series empty/degenerate/insufficient, calculate_rolling_beta errors/bad_cols/bench object conversion/outer path)
- All gates remain GREEN after validation runs

## NEXT ACTIONS (EXACT)
1. Run coverage on beta.py: `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q --cov=strategies.betting_against_beta.beta --cov-report=term-missing`
2. Add REAL tests hitting remaining uncovered lines in beta.py (focus lines ~44-56,90-130,151,163,165-170,103,113,123,125-126,129-130,249-253,343-347). Put tests in existing test files or new ones with substantive assertions.
3. If needed, add minimal defensive logic without changing behavior/invariants.
4. Change smallest needed files (no file-count metric). Keep gates green. Re-measure.

## NON-NEGOTIABLE GATES
```bash
PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest -q
PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q
```

## BOTTLENECK ELIMINATED THIS SESSION
- Fixed workflow stage_safe_changes missing nested `*/.github/workflows/*` pattern (2 controller tests red); gates restored.

## BOTTLENECK ELIMINATION PROTOCOL
- BAB-FIRST, heavy work, real assertions, deterministic/offline
- Preserve invariants (1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window>=60 default, ranking). Enforce finiteness. Raise BAB errors. No bare except:
- Rotate on stall to data_loader.py (94%) or quality.py (95%)
- Never leave gates red

## COVERAGE SNAPSHOT
| Module | Stmts | Miss | Cover | Priority |
|---|---|---|---|---|
| beta.py | 275 | 29 | 89% | P0-CRITICAL |
| data_loader.py | 287 | 17 | 94% | P0 |
| quality.py | 183 | 10 | 95% | P0 |
| portfolio.py | 223 | 13 | 94% | P2 |
| regime.py | 186 | 12 | 94% | P2 |
| backtest.py | 74 | 2 | 97% | P1 |
| shorting.py | 172 | 9 | 95% | P4 |
| signals.py | 113 | 2 | 98% | P3 |
| strategy.py | 198 | 3 | 98% | P3 |
| config.py | 199 | 3 | 98% | P3 |
| costs.py | 150 | 2 | 99% | P4 |
| metrics.py | 132 | 4 | 97% | P4 |
| cli.py | 34 | 0 | 100% | P3 |
| sizing.py | 163 | 0 | 100% | P4 |
| data_sources.py | 67 | 0 | 100% | P2 |
| attribution.py | 37 | 0 | 100% | OK |
| data.py | 15 | 0 | 100% | OK |
| errors.py | 2 | 0 | 100% | OK |
| __init__.py | 4 | 0 | 100% | OK |

PROJECT IDENTITY: Crypto-Betting-Against-Beta | BAB (Frazzini-Pedersen) for crypto - long low-beta, short high-beta vs benchmark (default BTC) | Core: strategies/betting_against_beta/
