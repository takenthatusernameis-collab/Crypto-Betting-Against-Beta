# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-02T04:05:14Z
**Priority from repo name:** Crypto Betting Against Beta (BAB) - market-neutral (long low-beta, short high-beta vs benchmark). ALL WORK MUST ADVANCE BAB.
**Session Mode:** Repo-prioritized, bottleneck-removal enforced. Heavy campaign required.
**Status:** ALL 5 GATES GREEN — FULL SUITE 1792 passed, 13 skipped. Campaigns 1-5 complete. No regressions. Bottleneck: duplicate handoff files consolidated into this single durable handoff.

## BOTTOM LINE - DO THIS FIRST (NO EXCEPTIONS)

Gate 0 (already green):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python -m pytest -q  # 1792 passed, 13 skipped
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
- Pattern-sync bottleneck previously removed (`*/.github/workflows/*` in `.github/workflows/main.yml:1163`).

## HEAVY FORCED CAMPAIGN 6: REAL-DATA END-TO-END & PACKAGING (GATE 6)

### CAMPAIGN 6 - GATE 6 (COMPLETE IN ORDER, NO TRIVIAL WORK)
**Goal:** Make BAB runnable from any cwd with real data, fully tested CLI paths, and publishable packaging.
**Focus:** `tests/test_bab_cli.py`, `scripts/load_real_bab_example.py`, `strategies/betting_against_beta/cli.py`, packaging config, `tests/test_bab_data_loader*.py`.
**Must do (all required, evidence mandatory):**
1. Add `--from-prices` coverage to `tests/test_bab_cli.py` (returns path and prices path, invalid args, missing file, benchmark mismatch, help output snapshot).
2. Make `scripts/load_real_bab_example.py` runnable without `PYTHONPATH` by adding `pyproject.toml` (or `setup.py`) with package discovery + console entry point `bab-example`; verify from a clean cwd.
3. Add a real-data end-to-end integration test using `tests/fixtures/real_market_prices.csv` through `BABStrategy.run(returns_df=...)` asserting finite cumulative and dollar-neutrality.
4. Stress-test `load_prices`/`load_returns` on mixed dtypes, timezone-aware timestamps, duplicate rows, comma/%-formatted numerics, NA strings, inf, empty frames; assert clear errors.
5. Add CLI `--version` and `--dry-run` (validate inputs, print resolved config, exit 0) without changing existing behavior; document in README.
6. Run perf benchmark `scripts/perf_bench.py` before/after; record numbers; no regression beyond 10%.
7. Run deterministic flake scan (repeat full suite 3x) and record pass counts.

**Gate 6:** `python -m pytest -q` → 1792+ passed, 0 new failures; CLI smoke from clean cwd returns finite; `bab-example --help` works. Record changes + output.

## NON-NEGOTIABLE RULES (still in force)
- **BASELINE FIRST:** Gate 0 mandatory. Never skip.
- **MAINTAIN GREEN:** 1792 passed, 13 skipped must remain; only add tests, never weaken.
- **BAB FIRST:** Crypto Betting Against Beta above everything else.
- **NO UNNECESSARY WORKFLOW CHANGES:** Only touch `.github/workflows/*` if absolutely required AND pattern-sync tests still pass.
- **PRESERVE CONTRACTS:** Keep synthetic defaults. Preserve public APIs.
- **EVIDENCE MANDATORY:** For each gate, record what changed and command output summary.
- **NO LOOKAHEAD:** Weights must be lagged by 1 day.
- **DEFENSIVE BY DEFAULT:** Validate, coerce safely, fail clearly.
- **HEAVY WORK REQUIRED:** Trivial one-liners insufficient.

**START NOW:** Run Gate 0. If green, begin Campaign 6 immediately. Do not stop until Gate 6 passes.
