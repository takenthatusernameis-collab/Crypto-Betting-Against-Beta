# HANDOFF - 2026-10-30T01:25:00Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T01:25:00Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else. Repo identity = Crypto-Betting-Against-Beta (BAB crypto).

GATE: python3 -m pytest -q must stay GREEN. Current state: 914 passed, 8 skipped (2 infra pattern tests just fixed). Do NOT break the suite.

CAMPAIGN: DRIVE BAB TO >=95% COVERAGE WITH HEAVY WORK (>=4 FILES WITH REAL LOGIC/TESTS PER SESSION). NO DOCS-ONLY.

START ORDER (focus gaps):
1. costs.py (17% missing?) — fill remaining uncovered lines (59-60). Strengthen finiteness/edge cases.
2. attribution.py — add more edge cases (zeros/NaN/alignment/mismatched shapes). Ensure trade_attribution/attribution_totals robust.
3. metrics.py — cover remaining gaps (71,97,174,187-188). Degenerate cases, NaN/inf, empty frames.
4. quality.py — cover remaining (30,47-48,132,187-188,211-212,245-246,259).
5. regime.py — cover remaining (111,139-140,175-177,181-182,185,188,190,217). Deterministic/offline.
6. cli.py — cover remaining (63). CLI paths with no network I/O.
7. sizing.py — cover gaps + bounds/finiteness.
8. backtest/strategy/data_loader/data_sources/beta/portfolio/signals/shorting/config as needed to hit >=95% overall for strategies/betting_against_beta.

RULES:
- TDD: failing test -> understand -> minimal impl -> green. Deterministic/offline/seeded.
- NO bare except:. Enforce finiteness (no NaN/inf). Handle NaN/inf/zeros/mismatched shapes/dates/non-monotonic cases.
- Preserve: one-day lag, dollar-neutral where applicable, quantile logic, beta window constraints.
- Validate: coverage for strategies/betting_against_beta/* AND full suite stays green.
- ONLY update THIS HANDOFF.md. NO COMMITS unless explicitly asked.
- DO NOT get distracted by infra/workflows unless actively breaking BAB gate.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- **Repository:** Crypto-Betting-Against-Beta
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (Frazzini–Pedersen style)
- **ABSOLUTE PRIORITY:** `strategies/betting_against_beta/` above all else

## BOTTLENECKS REMOVED
- **Workflow/controller pattern sync:** Fixed `.github/workflows/main.yml` stage_safe_changes to include `*/.github/workflows/*` matching `scripts/controller_progress.py` EXCLUDE_PATTERNS. All pattern sync tests pass.
- **Suite gate restored:** `python3 -m pytest -q` = 914 passed, 8 skipped (after fixes). Controller-progress tests all pass (68/68).

## ACTIVE COVERAGE TARGETS (EXECUTE IN ORDER)
1. **costs.py** — cover remaining uncovered lines; strengthen finiteness/edge cases.
2. **attribution.py** — expand edge case coverage (zeros/NaN/alignment/mismatched shapes).
3. **metrics.py** — cover remaining gaps; degenerate cases.
4. **quality.py** — cover remaining rejection/edge paths.
5. **regime.py** — cover remaining gaps; deterministic/offline.
6. **cli.py** — cover remaining CLI path.
7. **sizing.py** — cover bounds + finiteness + edge cases.

## MANDATORY RULES (ENFORCED)
- **Product-first:** BAB strategy is never deprioritized.
- **Heavy work:** >= 4 files with real logic/tests per session when on strategy.
- **Quality:** TDD, no bare except:, enforce finiteness, deterministic/offline/seeded.
- **Stability:** Always keep suite green. If forced to choose between speed and correctness, choose correctness.
- **Handoff discipline:** Only update `HANDOFF.md`. Ignore older `HANDOFF_*.md`. No commits unless asked.
- **No scope creep:** If infra is not blocking the BAB gate, do not touch it.
