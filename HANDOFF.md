# HANDOFF - 2026-10-29T23:32:46Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T23:32:46Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: BAB strategy in strategies/betting_against_beta/ > everything else.
GATE: python3 -m pytest -q must be green (currently 916 passed, 8 skipped). If not, fix workflow/controller pattern drift or config validation regressions first.
CAMPAIGN: Push ALL strategies/betting_against_beta/ modules to >=95% coverage. NO DOCS-ONLY WORK.
START: costs.py (17%) FIRST (biggest gap). Then attribution.py, metrics.py, quality.py, regime.py, cli.py, sizing.py. Cover uncovered branches: NaN/inf/zeros/mismatched shapes/dates/non-monotonic, finiteness, bounds.
REQUIREMENTS: Touch >=4 files with real logic/tests. TDD: failing test → understand → minimal impl → green. No bare except:. Deterministic/offline/seeded. Enforce finiteness. Preserve behavior.
VALIDATE: coverage for strategies/betting_against_beta/*, full suite green. Update THIS HANDOFF.md only. NO COMMITS unless asked. HEAVY WORK MANDATORY.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- **Repository:** Crypto-Betting-Against-Beta
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark, Frazzini–Pedersen style
- **ABSOLUTE PRIORITY:** BAB strategy code in strategies/betting_against_beta/ > everything else

## BOTTLENECKS REMOVED
- Workflow/controller pattern sync fixed (*/.github/workflows/* added to stage_safe_changes)
- Config bugs fixed (vol_percentiles default None semantics, finiteness checks, resolved_universe None handling)
- Baseline restored green (916 passed, 8 skipped)

## COVERAGE GAPS (PRIORITY)
1. costs.py (17%) - transaction costs/slippage/turnover
2. attribution.py (17%), metrics.py (12%), quality.py (7%), regime.py (0%), cli.py (0%), sizing.py (20%)
3. data_sources.py (42%), data_loader.py (48%), signals.py (45%), strategy.py (50%), portfolio.py (54%), shorting.py (61%), backtest.py (66%), config.py (73%), beta.py (83%)

## MANDATORY RULES
- Product-first: strategies/betting_against_beta/ is always priority
- Heavy work: >=4 files with real logic/tests per session when working on strategy
- TDD, no bare except:, enforce finiteness, deterministic/offline/seeded
- Always keep suite green
- Only HANDOFF.md updated; no commits unless asked
- Ignore older HANDOFF_*.md files
