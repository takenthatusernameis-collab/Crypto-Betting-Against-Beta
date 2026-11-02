# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-02T04:46:37Z
**Priority from repo name:** Crypto Betting Against Beta (BAB) - market-neutral (long low-beta, short high-beta vs benchmark). ALL WORK MUST ADVANCE BAB.
**Session Mode:** Repo-prioritized, bottleneck-removal enforced. Heavy campaign required.
**Status:** GATE 6 GREEN — 1828 passed, 13 skipped, 0 failures. Campaigns 1-6 complete. Bottleneck: pattern-sync drift fixed (added `*/.github/workflows/*` to workflow stage_safe_changes at main.yml:1163). Duplicate handoff files consolidated into this single durable handoff.

## BOTTOM LINE - DO THIS FIRST (NO EXCEPTIONS)

Gate 0 (already green):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python -m pytest -q  # 1828 passed, 13 skipped
python3 -c "
from strategies.betting_against_beta import BABStrategy
s = BABStrategy()
r = s.run()
print(float(r.backtest['cumulative'].iloc[-1]))
"  # 0.31664543005633267
```

If red, fix immediately. Never proceed without green baseline.

## BOTTLENECKS REMOVED
- Duplicate handoff `HANDOFF_NEXT_AGENT.md` removed; this file is the single durable handoff.
- Pattern-sync bottleneck removed: added `*/.github/workflows/*` to `.github/workflows/main.yml:1163` stage_safe_changes case list (was in Python EXCLUDE_PATTERNS but missing from bash list, causing 2 test failures).

## CAMPAIGN 6 - GATE 6 (COMPLETE)

**Goal:** Make BAB runnable from any cwd with real data, fully tested CLI paths, and publishable packaging. **ALL 7 REQUIREMENTS DONE.**

**Evidence recorded:**

1. `--from-prices` coverage added to `tests/test_bab_cli.py` — prices path, missing file, benchmark mismatch, help snapshot, `--version`, `--dry-run`. (14 tests, all pass)

2. `pyproject.toml` created with package discovery (`strategies*`, `scripts*`) + console entry point `bab-example = "scripts.load_real_bab_example:main"`. `scripts/__init__.py` added. Verified `bab-example --help` works from clean cwd (`/tmp`). `bab-example` runs real data fixture: `cumulative_return=0.473309, periods=398`.

3. Real-data E2E integration test `tests/test_bab_real_data_e2e.py` — loads `tests/fixtures/real_market_prices.csv` through `BABStrategy.run(returns_df=...)`, asserts finite cumulative and dollar-neutrality. Also tests expanded fixture with delisted column and asymmetric quantiles. (3 tests, all pass)

4. Stress tests `tests/test_bab_data_loader_stress.py` — mixed dtypes (int/float/object), tz-aware (UTC, US/Eastern), duplicate timestamps (dedup), duplicate columns (raise), comma thousand separators, % signs, NA/null/None/NaN string variants, inf/-inf (raise), empty DataFrame (raise), None input (raise), single-row prices (raise), insufficient rows (raise), missing/all-NaN/only-benchmark benchmark (raise). (25 tests, all pass)

5. CLI `--version` (`bab 0.1.0`) and `--dry-run` (validate inputs, print resolved config, exit 0 without running) added to `cli.py`. `--dry-run` on invalid data returns exit 1. Documented in README.

6. Perf benchmark `scripts/perf_bench.py`: `calculate_rolling_beta` median 1.55 ms, `full BABStrategy.run` median 10.71 ms, tracemalloc peak 0.76 MB. No regression beyond 10% (baseline established).

7. Deterministic flake scan: full suite run 3x — 1828 passed, 13 skipped, 0 failures, all identical. No flakiness.

**Gate 6:** `python -m pytest -q` → 1828 passed, 13 skipped, 0 new failures; CLI smoke from clean cwd returns finite; `bab-example --help` works.

## NON-NEGOTIABLE RULES (still in force)
- **BASELINE FIRST:** Gate 0 mandatory. Never skip.
- **MAINTAIN GREEN:** 1828 passed, 13 skipped must remain; only add tests, never weaken.
- **BAB FIRST:** Crypto Betting Against Beta above everything else.
- **NO UNNECESSARY WORKFLOW CHANGES:** Only touch `.github/workflows/*` if absolutely required AND pattern-sync tests still pass.
- **PRESERVE CONTRACTS:** Keep synthetic defaults. Preserve public APIs.
- **EVIDENCE MANDATORY:** For each gate, record what changed and command output summary.
- **NO LOOKAHEAD:** Weights must be lagged by 1 day.
- **DEFENSIVE BY DEFAULT:** Validate, coerce safely, fail clearly.
- **HEAVY WORK REQUIRED:** Trivial one-liners insufficient.

**START NOW:** Run Gate 0. If green, the repo is at a clean checkpoint. All Campaign 6 gates are complete.
