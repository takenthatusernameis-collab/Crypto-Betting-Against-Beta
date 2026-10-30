# HANDOFF - 2026-10-30T04:16:50Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T04:16:50Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen style Betting Against Beta for crypto markets)

GATE: python3 -m pytest -q MUST stay GREEN. Current state: 992 passed, 11 skipped. NO REGRESSIONS.
BOTTLENECKS REMOVED: pattern-sync drift fixed in `.github/workflows/main.yml` - added `*/.github/workflows/*` to stage_safe_changes. Controller suite 68/68 green.

CAMPAIGN: DRIVE BAB TO >=95% TOTAL COVERAGE WITH HEAVY WORK (>=4 FILES WITH REAL LOGIC/TESTS THIS SESSION). NO DOCS-ONLY CHANGES.

CURRENT COVERAGE GAPS (by uncovered lines, focus largest first):
1. data_loader.py (89%, 31 uncovered) - focus: _promote_datetime_column exception paths, _normalize_index tz fallback branches, _coerce_numeric edge cases, load_* exception wrapping
2. beta.py (88%, 28 uncovered) - focus: calculate_beta alignment paths, rolling beta edge cases, fallback paths
3. backtest.py (91%, 7 uncovered) - focus: cost model integration, aliases, edge alignments
4. portfolio.py (94%, 14 uncovered) - focus: constraints/leverage/shorting paths
5. quality.py (93%, 11 uncovered), regime.py (94%, 12 uncovered), shorting.py (95%, 9 uncovered)
6. signals.py (96%, 4 uncovered), metrics.py (96%, 5 uncovered), config.py (98%, 3 uncovered), costs.py (99%, 2 uncovered), strategy.py (97%, 5 uncovered)

FOCUS ORDER: data_loader.py -> beta.py -> backtest.py -> portfolio.py/quality.py/regime.py/shorting.py -> others. Add real tests with assertions for uncovered branches/paths. Heavy work required (>=4 files).

EXISTING CAMPAIGN TESTS (keep passing):
- tests/test_bab_data_loader_campaign.py
- tests/test_bab_beta_campaign.py
- tests/test_bab_strategy_campaign.py
- tests/test_bab_data_sources_campaign.py
- tests/test_bab_data_loader_campaign_heavy.py
- tests/test_bab_data_loader_deep.py

RULES (MANDATORY):
- TDD: failing test -> minimal impl/fix -> green. Deterministic/offline/seeded only. No network calls.
- NO bare except:. Enforce finiteness (no NaN/inf). Handle NaN/inf/zeros/mismatched shapes/dates/non-monotonic cases.
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile logic, beta window constraints, rank/decile logic.
- Validate after changes: `python3 -m pytest tests/test_betting_against_beta*.py -q` stays green AND `python3 -m pytest -q` stays green.
- ONLY update THIS HANDOFF.md. NO COMMITS unless explicitly asked.
- Focus on BAB strategy. Do not touch infra/workflows unless they break the BAB test gate.
- Add real tests with assertions for uncovered logic. Heavy work required (>=4 files).
- If blocked, remove the blocker before moving scope.
- Coverage target: >=95% total before declaring the campaign complete. Report coverage delta per batch.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- **Repository:** Crypto-Betting-Against-Beta
- **Strategy:** Betting Against Beta (BAB) for crypto - long low-beta assets, short high-beta assets vs benchmark (Frazzini–Pedersen methodology)
- **Core Modules:** strategies/betting_against_beta/ (all modules)
- **ABSOLUTE PRIORITY:** `strategies/betting_against_beta/` above everything else

## CURRENT STATE
- **Full Suite:** 992 passed, 11 skipped (GREEN)
- **BAB Tests:** all green
- **Bottlenecks:** Removed - pattern-sync fixed in `.github/workflows/main.yml` (added `*/.github/workflows/*`). Controller tests all pass (68/68).
- **Handoff Source:** Single durable handoff enforced. All other HANDOFF_*.md files are deprecated.
- **Coverage:** Campaign in progress targeting >=95%

## EXECUTION DIRECTIVES
- **Product-first:** BAB strategy is never deprioritized.
- **Heavy work:** >= 4 files with real logic/tests per session when working on strategy modules.
- **Quality over speed:** Correctness always wins. TDD discipline required.
- **Handoff discipline:** Only update THIS HANDOFF.md. Ignore older HANDOFF_*.md files.
- **No scope creep:** Only touch infra if it breaks the BAB gate.
- **Deterministic:** All tests must be deterministic/offline/seeded. No network calls.
- **Blocker removal:** If multiple sessions would be blocked/inefficient by a gate/infrastructure issue preventing BAB progress, fix that blocker first with minimal change, verify gates stay green, then resume BAB coverage campaign.
