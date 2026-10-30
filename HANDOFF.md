# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) — 2026-10-30T23:53:10Z

## TIMESTAMP
2026-10-30T23:53:10Z

## INITIAL TASK MESSAGE FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY #1: strategies/betting_against_beta/beta.py | REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE
CRUSH beta.py UNCOVERED BRANCHES NOW. CURRENT: 89% (~29 MISS).
TARGET: beta.py >= 95% | BAB TOTAL >= 97%.
DO NOT TOUCH FILES FOR VANITY. CHANGE ONLY SMALLEST SET NEEDED FOR REAL UNCOVERED BRANCHES.
HIT HARD LINES: estimate_betas fallthroughs/aliases/clamps; calculate_beta alignment/disjoint/mask/min_obs/linalg/constant_x/None; calculate_beta_fast masks/degenerate/nonfinite/LinAlgError/empty/min_obs; _calc_rolling_beta_series degenerate/insufficient/empty; calculate_rolling_beta bad_cols/bench conversion/outer except/_finalize_betas.
PROVE WITH COVERAGE: run PYTHONPATH=$PWD python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q --cov=strategies.betting_against_beta.beta --cov-report=term-missing
ADD REAL TESTS WITH ASSERTIONS OR MINIMAL DEFENSIVE FIXES. NO DOCS-ONLY. NO FILE-COUNT GOAL.
FULL SUITE MUST STAY GREEN. BAB SUITE MUST STAY GREEN.
DO HEAVY WORK. NO DELAY.
```

## CAMPAIGN OBJECTIVE
Maximize BAB coverage to >=97% starting with beta.py (biggest gap). Every turn must produce substantive test/logic changes that cover uncovered branches. No churn.

## VERIFIED GATES (CURRENT)
- Full suite: GREEN (1416 passed, 11 skipped)
- BAB suite: GREEN (1256 passed, 11 skipped)
- BAB total coverage: ~96% (2514 stmts / ~106 miss)
- PRIMARY BOTTLENECK: strategies/betting_against_beta/beta.py — 89% (~29 misses)

## EXACT NEXT STEPS
1. `cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta && PYTHONPATH=$PWD python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q --cov=strategies.betting_against_beta.beta --cov-report=term-missing`
2. Identify 5-10 highest-value uncovered lines from term-missing (focus estimate_betas, calculate_beta, calculate_beta_fast, _calc_rolling_beta_series, calculate_rolling_beta).
3. Write REAL tests in existing test files (or minimal new test files) with concrete assertions hitting those exact branches. If a branch cannot be safely hit by tests without weakening invariants, fix the test strategy or add minimal safe defensive handling only if it matches existing BAB behavior.
4. Re-run focused coverage on beta.py. Repeat until beta.py >= 95%. Then reassess next bottleneck (data_loader.py 94%, quality.py 95%).
5. Before ending, run full BAB suite + full suite to confirm GREEN.

## INVARIANTS (MUST PRESERVE)
- 1-day lag, dollar-neutral where applicable, quantiles/deciles, beta window >= 60 default, ranking logic
- Finiteness enforced, raise BAB-specific errors, no bare except:
- Deterministic offline tests
- Final full-suite green gate required

## BOTTLENECK ELIMINATION PROTOCOL
- BAB-FIRST. Heavy substantive work every session.
- Change smallest set of files needed. File count is NOT a metric.
- If stall on beta.py (no new branch hitable safely), move to next highest leverage (data_loader.py/quality.py) with same rigor.
- Never leave gates red. If you make changes, verify gates immediately.
