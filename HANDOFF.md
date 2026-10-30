# HANDOFF - 2026-10-30T00:23:22Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T00:23:22Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else. Repo identity = Crypto-Betting-Against-Beta (BAB crypto).

GATE: python3 -m pytest -q must stay GREEN (916 passed, 8 skipped). If red, fix minimal regression before expanding coverage.

CAMPAIGN: DRIVE BAB TO >=95% COVERAGE WITH HEAVY WORK.
START: costs.py (17%) FIRST.
THEN: attribution.py (17%) -> metrics.py (12%) -> quality.py (7%) -> regime.py (0%) -> cli.py (0%) -> sizing.py (20%)
THEN: close remaining gaps on data_sources.py (42%), data_loader.py (48%), signals.py (45%), strategy.py (50%), portfolio.py (54%), shorting.py (61%), backtest.py (66%), config.py (73%), beta.py (83%)

RULES:
- Touch >= 4 FILES with real logic/tests per session. No docs-only commits.
- TDD: failing test -> understand -> minimal impl -> green. Deterministic/offline/seeded.
- NO bare except:. Enforce finiteness. Handle NaN/inf/zeros/mismatched shapes/dates/non-monotonic cases.
- One-day lag, dollar-neutral where applicable, quantile logic, beta window constraints must be preserved.
- Validate with coverage for strategies/betting_against_beta/* AND full suite.
- Only update THIS HANDOFF.md. NO COMMITS unless explicitly asked.
- DO NOT get distracted by infra/workflows unless they are actively breaking the BAB gate.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- **Repository:** Crypto-Betting-Against-Beta
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (Frazzini–Pedersen style)
- **ABSOLUTE PRIORITY:** `strategies/betting_against_beta/` above all else

## BOTTLENECKS REMOVED
- **Workflow/controller pattern sync:** Added `*/.github/workflows/*` to `.github/workflows/main.yml` stage_safe_changes/exclusion + meaningful-progress detection to stay in lock-step with `scripts/controller_progress.py` EXCLUDE_PATTERNS.
- **Suite gate restored:** Controller-progress tests fixed; `python3 -m pytest -q` = 916 passed, 8 skipped.
- **Baseline restored:** `python3 -m pytest -q` = 916 passed, 8 skipped.
- **Config robustness:** `vol_percentiles` default None semantics, finiteness checks, `resolved_universe` None handling corrected.

## ACTIVE COVERAGE TARGETS (EXECUTE IN ORDER)
1. **costs.py (17%)** — turnover/slippage/transaction costs. Cover edge cases and ensure finiteness.
2. **attribution.py (17%)** — PnL decomposition. Cover zeros, NaN, alignment.
3. **metrics.py (12%)** — Sharpe/vol/drawdown/turnover etc. Cover degenerate cases.
4. **quality.py (7%)** — data quality gates. Cover all rejection paths.
5. **regime.py (0%)** — new coverage required. Implement minimal tests + harden impl to be deterministic/offline.
6. **cli.py (0%)** — minimal CLI paths with no network I/O; test args/config/exit paths.
7. **sizing.py (20%)** — leverages/constraints. Cover bounds + finiteness.

## MANDATORY RULES (ENFORCED)
- **Product-first:** BAB strategy is never deprioritized.
- **Heavy work:** >= 4 files with real logic/tests per session when on strategy.
- **Quality:** TDD, no bare except:, enforce finiteness, deterministic/offline/seeded.
- **Stability:** Always keep suite green. If forced to choose between speed and correctness, choose correctness.
- **Handoff discipline:** Only update `HANDOFF.md`. Ignore older `HANDOFF_*.md`. No commits unless asked.
- **No scope creep:** If infra is not blocking the BAB gate, do not touch it.
