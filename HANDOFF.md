# HANDOFF: Crypto-Betting-Against-Beta — Next Agentic Session

**Timestamp:** 2026-11-25T19:08:18Z
**Repository:** Crypto-Betting-Against-Beta
**Branch:** main (clean)
**Status:** Tests pass (3,700+), ruff clean. **P39 WP0 full-gate close-out: COMPLETE / GREEN** — verified per committed `docs/COVERAGE_NOTES.md` (2026-11-25T18:15:00Z, HEAD `098a3a4`): `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` exit 0, pytest TOTAL **100%** (0 missed / 6730 statements), `7675 passed / 39 skipped` in 3360.6s, replay gate + P30 + P33–P39 all GREEN. HEAD `5da4bcd` introduces **no source/test changes** since `098a3a4` (only the committed `scripts/bab_gate.sh` P30 quoting fix), so the green state holds. Campaign **P40** is now the binding row — **not yet started** (`docs/BAB_P40_DECISION.md` and `tests/test_bab_p4_decision_consistency.py` do not exist).

---

## Project Summary

Production-grade **Betting Against Beta (BAB)** quantitative strategy for crypto (Frazzini-Pedersen low-beta anomaly): long low-beta assets, short high-beta assets vs. a benchmark (default BTC), dollar-neutral equal-weight or rank-weighted construction.

**Core Pipeline:** load/validate returns → rolling beta (numpy-cached OLS) → rank by beta → long bottom quantile / short top quantile → dollar-neutral portfolio → backtest (1-day lag, no lookahead, costs/slippage, optional R3-A impact) → regime filter / beta-neutral / kill-switch / execution adapters.

**Key Modules:** `strategies/betting_against_beta/{strategy,config,beta,signals,portfolio,backtest,data_loader,execution,risk,regime,sizing,shorting,costs,reconciliation,quality,attribution,metrics}.py`

**CLI:** `bab` — `--data`, `--from-prices`, `--dry-run`, `--adapter paper|mock|live`, `--paper-trading`, `--reconcile`, `--health-check`, freshness guards.

---

## Current State (Verified)

| Check | Result |
|-------|--------|
| `pytest` (full suite) | **3,700+ tests PASS** |
| `ruff check .` | **CLEAN** |
| `mypy` | Not configured (no type annotations) |
| Git status | Clean, no uncommitted changes |
| P20–P38 campaigns | COMPLETE and frozen (do not reopen) |
| P39 WP0/WP1/WP2/WP3 | COMPLETE and frozen |
| **P39 WP0 — Full-Gate Close-Out** | **COMPLETE / GREEN** (verified, see `docs/COVERAGE_NOTES.md`) |
| **Campaign P40** | **BINDING — sole agent-executable row** |

**Blocked sessions:** None. The prior bottleneck was a stale `HANDOFF.md` claim that P39 WP0 was "not green," contradicting the committed `docs/COVERAGE_NOTES.md` green record. That contradiction is resolved: P39 WP0 is complete. Do **not** re-run the 56-minute full gate unless `strategies/` or `tests/` source changes; a fast smoke test suffices for re-confirmation.

---

## Binding Initial Task — Campaign P40 "Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict" (P0, MUST land first)

**This is the sole agent-executable binding row.** Per `README.md` "CI, gates, and safety": P20–P38 and P39 WP0–WP3 are complete/frozen; **Campaign P40 is the binding row until it lands.** P40 aggregates the P35–P39 decision evidence across all committed fixtures into a single consolidated factor verdict (does BAB survive deflation/tail-risk/regime across the 9-asset, 40-asset, and expanded synthetic fixtures?).

**Scope / files:** `tests/fixtures/real_market_prices.csv` (9 assets), `tests/fixtures/wide_bab_universe.csv` (40 assets), `tests/fixtures/real_market_prices_expanded.csv`; `docs/BAB_P35_DECISION.md`, `docs/BAB_P36_DECISION.md`, `docs/BAB_P37_DECISION.md`, `docs/BAB_P38_DECISION.md`, `docs/BAB_P39_DECISION.md`; `research_state/bab_p3{5,6,7,8,9}/`; `scripts/bab_p35_estimator_bakeoff.py`, `scripts/bab_p36_walk_forward.py`, `scripts/bab_p37_cost_surface.py`, `scripts/bab_p38_deflated_significance.py`, `scripts/bab_p38_tail_risk.py`, `scripts/bab_p39_regime_conditional.py`, `scripts/bab_p39_cross_fixture.py`.

**Required work packages (in order, none optional):**
1. **Multi-fixture re-run:** Re-run P35–P39 decision scripts/tests against each of the three fixtures; record per-fixture verdicts (survives/fails deflation, tail-risk, regime, cross-fixture).
2. **Meta-analysis:** Aggregate per-fixture results into a consolidated factor verdict document (`docs/BAB_P40_DECISION.md`) — robustness matrix, conditions under which BAB holds/breaks, honest caveats (synthetic fixtures are not real market data — never present as profitability evidence).
3. **Gate wire:** Add `tests/test_bab_p40_decision_consistency.py` + `--check-p40-summary` to `scripts/bab_gate.sh` post-pytest phases; ensure `bab_replay_gate.sh` still exits 0.
4. **Exit condition:** `docs/BAB_P40_DECISION.md` committed, consistency test passes, full gate (`BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh`) still GREEN with TOTAL 100%.

**Once P40 lands:** proceed to the P0–P2 heavy-work focus campaign below. Future agents **must not avoid** these; each is a force multiplier for production readiness.

---

## Follow-On Focus Campaign (P0–P2 heavy work — unavoidable)

Execute in priority order after P40.

### 1. Real-Data Production Hardening (P0)
**Files:** `strategies/betting_against_beta/data_loader.py`, `strategies/betting_against_beta/quality.py`, `tests/fixtures/real_market_prices_expanded.csv`, `scripts/fetch_real_bab_prices.py`
- Wire the real-data path through CLI → strategy → backtest → tear sheet as the **default documented workflow**.
- Add `scripts/fetch_real_data.py` pulling from a public crypto API (CoinGecko/Binance public endpoints) emitting the canonical CSV schema.
- Validate freshness guards (`--max-staleness-days`, `--max-gap-days`) on real data.
- **Gate:** `bab --data real_market_prices_expanded.csv --from-prices --output out.json` produces a finite, non-trivial tear sheet.

### 2. Walk-Forward / Rolling Validation Framework (P0)
**Files:** `scripts/bab_p36_walk_forward.py` (FROZEN — do not edit), `strategies/betting_against_beta/backtest.py`
- Implement a new `bab walk-forward` subcommand (or `--walk-forward` flag), separate from the frozen P36 script.
- Expanding/windowed train/test folds, beta re-estimated per training window, signals on test window (no lookahead), aggregate OOS metrics (Sharpe, max DD, turnover, hit rate), emit JSON summary + per-fold tear sheets.
- **Gate:** Pass on `real_market_prices_expanded.csv` with ≥ 4 folds, runtime < 60s.

### 3. Live Execution Adapter — CCXT Hardening (P1)
**Files:** `strategies/betting_against_beta/execution.py`, `strategies/betting_against_beta/cli.py` (`--adapter live`)
- Implement real order submission via CCXT: mark prices, order-book depth, exchange filters (min notional, lot size), `OrderIntent` → exchange params (market/limit, reduce-only), partial fills/rejects, rate-limit exponential backoff, structured `Fill` events for reconciliation (R5-B/C).
- Dry-run default; live only with explicit `--allow-live-execution --accept-terms=<token>`.
- **Gate:** `bab --adapter live --exchange binance --api-key-env X --api-secret-env Y --health-check` returns valid JSON with `connected: true`, `last_tick_age_ms < 5000`.

### 4. Regime-Aware Risk Overlay (P1)
**Files:** `strategies/betting_against_beta/regime.py`, `strategies/betting_against_beta/risk.py`
- Per-asset regime tilts (reduce short-leg size in high-vol, increase long-leg in trend-up), `KillSwitchEvent` telemetry in report/tear sheet, `max_drawdown_limit` integration test with synthetic crash.

### 5. Research: Alternative Beta Estimators & Factor Extensions (P2)
**Files:** `strategies/betting_against_beta/beta_estimators.py`, `strategies/betting_against_beta/beta.py`
- Implement Huber M-estimator and Kalman filter with `beta_method` config; A/B test harness comparing estimator OOS performance on real data.

### 6. Performance Optimization — Numba/JIT Hot Paths (P2)
**Files:** `strategies/betting_against_beta/beta.py` (`calculate_rolling_beta`), `strategies/betting_against_beta/backtest.py` (`run_backtest`)
- `@numba.njit` hot loops where safe; benchmark vs numpy cache; target ≥ 2x speedup on 5000x500 scale test.

---

## Non-Negotiable Constraints

1. **Never break byte-identical default path.** Any new feature (R3-A, R4-B, R5-A, regime, etc.) is opt-in via config flag; default `BABStrategy(config).run()` must produce identical output to current HEAD.
2. **Defensive error handling is the contract.** CLI/report paths swallow and coerce degenerate input (NaN, inf, empty frames). Do not add `try/except` enforcement that changes this semantics.
3. **Frozen scripts are immutable.** `scripts/bab_p36_*.py` — do not edit. Add new scripts instead.
4. **Strict JSON output.** All artifacts (`--output`, execution, reconciliation) serialize with `allow_nan=False`. Use `_json_safe` / `_json_default` helpers.
5. **No new dependencies without justification.** Current deps: numpy, pandas, scipy, pytest, hypothesis, ccxt (optional). Numba acceptable for P6.
6. **Synthetic fixtures are not real market data.** `tests/fixtures/real_market_prices.csv` and `wide_bab_universe.csv` are deterministic synthetic random walks — never present results on them as evidence of real profitability.

---

## Quick Start for Next Agent

```bash
# 1. Verify environment + confirm gate still green (fast smoke, not the 56-min full gate)
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python -m pytest tests/test_bab_backtest_contract_smoke.py -q  # 9 tests, ~1s
python -m strategies.betting_against_beta.cli --synthetic --dry-run

# 2. BINDING TASK — Campaign P40 (multi-fixture robustness meta-analysis)
# Re-run P35–P39 decision scripts across the 3 fixtures, write docs/BAB_P40_DECISION.md,
# add tests/test_bab_p40_decision_consistency.py + --check-p40-summary to scripts/bab_gate.sh,
# keep BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh GREEN (TOTAL 100%).

# 3. Re-confirm full gate only if source changed (else skip):
# BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh   # ~5-6 min; do not abort
# git checkout -- research_state/bab_p27/   # restore P27 touched files after a full run

# 4. Once P40 lands, real-data smoke test (P0 campaign)
python -m strategies.betting_against_beta.cli \
  --data tests/fixtures/real_market_prices_expanded.csv \
  --from-prices --output /tmp/bab_real.json \
  --rebalance-freq weekly --transaction-costs 0.001 --slippage 0.0005
```

---

## Escalation / Coordination

- **Board:** Post material findings via `board_post`; check `board_read` for peer updates before dependent work.
- **Diagnostics ledger:** `research_state/workflow_run_diagnostics.jsonl` — updated by CI on every completed run.
- **Kilo config:** `.config/kilo/kilo.json` (permission: allow). Agent Manager runs in `RUNNER_TEMP/kilo-home`.

---

**End of Handoff.** Next agent: execute Campaign P40 (multi-fixture robustness meta-analysis → consolidated factor verdict → gate wire), keeping the full gate green. Do not re-plan; the campaign is defined above. After P40, proceed to the P0–P2 heavy-work focus campaign (real-data hardening → walk-forward → live adapter → regime risk → alt beta estimators → numba perf).
