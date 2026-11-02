# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-02T05:47:58Z
**Priority from repo name:** CRYPTO BETTING AGAINST BETA (BAB) - Market-neutral long low-beta / short high-beta vs benchmark. ALL WORK MUST DIRECTLY ADVANCE BAB.
**Session Mode:** Repo-prioritized, bottleneck-removal enforced. Heavy campaign MANDATORY.
**Status:** ALL TESTS GREEN - 1828 passed, 13 skipped, 0 failures. Gate 0 verified. Bottlenecks eliminated.

## BOTTOM LINE - RUN GATE 0 FIRST, NO EXCEPTIONS

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python -m pytest -q  # MUST be: 1828 passed, 13 skipped
python3 -c "
from strategies.betting_against_beta import BABStrategy
s = BABStrategy()
r = s.run()
print(float(r.backtest['cumulative'].iloc[-1]))
"  # MUST be ~0.31664543005633267
```

**If red → fix before doing anything else.**

## IMMEDIATE TASK FOR NEXT SESSION (START HERE - HEAVY WORK REQUIRED)

**CAMPAIGN 7: PRODUCTION HARDENING FOR REAL CRYPTO DATA**

Do NOT do cosmetic changes. Do heavy, verifiable work in these areas:

### PRIORITY 1 - CRITICAL (DO FIRST)
1. **Exchange-format loader support** - Extend `strategies/betting_against_beta/data_loader.py` to robustly handle common exchange CSV formats (CoinGecko exports, Binance OHLCV/price CSVs, Coinbase exports). Add flexible column mapping (date/time/open/high/low/close/adj_close/volume), handle symbol case, auto-detect price vs returns. Add tests.
2. **Multi-source normalization** - Create/extend utilities to normalize different schemas into the canonical datetime index + numeric columns format expected by validator. Make it defensive against whitespace, units, etc.
3. **Robust datetime parsing** - Harden `_promote_datetime_column` and `_normalize_index` for more formats (epoch seconds/ms, mixed timezones, dayfirst, etc.). All existing behavior must be preserved.

### PRIORITY 2 - CRITICAL (DATA QUALITY)
4. **Comprehensive data quality checks** - Add validation for gaps, duplicate timestamps across assets, stale data, implausible returns (|r| > X), missing benchmark coverage. Return clear `BABDataError` messages.
5. **Survivorship bias awareness** - Add utilities to handle delistings better (already partially handled). Ensure behavior is explicit and tested.
6. **Timezone/alignments** - Test cross-timezone datasets. Ensure no lookahead - weights lagged by 1 day is already enforced; verify no regressions.

### PRIORITY 3 - HIGH (PERFORMANCE & SCALABILITY)
7. **Profile & optimize** - Profile `calculate_rolling_beta` in `strategies/betting_against_beta/beta.py`. Vectorize bottlenecks without changing API/results. Add perf tests or extend `scripts/perf_bench.py`.
8. **Large dataset testing** - Add tests with larger synthetic data (multi-year, 500+ assets) to catch memory issues. Ensure reasonable performance.
9. **Efficient I/O** - Improve loaders for large files where easy wins exist.

### PRIORITY 4 - HIGH (RISK/REALISM)
10. **Transaction costs realism** - Extend cost modeling (market impact/slippage tiers). Maintain backward compat.
11. **Risk controls** - Add position/leverage limits, max drawdown monitoring hooks. Integrate cleanly.
12. **Attribution & metrics** - Expand `metrics.py`/`attribution.py` with Sharpe, Sortino, Calmar, max DD, turnover, hit rate as appropriate.

### PRIORITY 5 - MANDATORY (TEST COVERAGE)
13. **Property-based tests** - Add hypothesis tests for dollar-neutrality, weight bounds, no lookahead, idempotency where applicable.
14. **Stress tests** - Correlation regime shifts, extreme vol, missing data patterns matching real exchanges.
15. **CLI integration tests** - Test `--from-prices`, `bab-example`, real file formats end-to-end.

## EXECUTION RULES (NON-NEGOTIABLE)
- **Gate 0 first. ALWAYS.** Confirm green baseline before any change.
- **Maintain green.** Keep 1828 passed + 13 skipped. Add tests, don't weaken them.
- **BAB-first.** Every change must advance Crypto Betting Against Beta.
- **No workflow changes unless absolutely necessary.** If touching `.github/workflows/*`, pattern-sync tests must pass (they do now).
- **Preserve APIs/contracts.** Synthetic defaults must remain. Public APIs stable unless absolutely required with full coverage.
- **No lookahead.** Weights must be lagged by 1 day. This is invariant.
- **Defensive by default.** Validate inputs, fail with clear errors.
- **Heavy work only.** Trivial edits are insufficient. Tackle substantial improvements.
- **Evidence required.** For each major change, verify tests still pass and core behavior unchanged.

## KEY FILES
- `strategies/betting_against_beta/data_loader.py` - Data loading/validation (prime target)
- `strategies/betting_against_beta/beta.py`, `strategy.py`, `portfolio.py` - Core
- `strategies/betting_against_beta/cli.py`, `scripts/` - CLI/examples
- `tests/test_bab_*` - All BAB tests (must stay green)

## START NOW
1. Run Gate 0 (confirm green)
2. Pick ONE concrete item from Priority 1 and implement it fully with tests
3. Run tests after each change - never let them go red
4. Repeat with heavy work until substantial progress on real-data robustness
