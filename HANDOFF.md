# HANDOFF: Crypto-Betting-Against-Beta — Next Agentic Session

**Timestamp:** 2026-11-25T18:52:24Z
**Repository:** Crypto-Betting-Against-Beta
**Branch:** main (clean)
**Status:** Tests pass (3,700+), ruff clean. **P39 WP0 full-gate close-out is NOT yet green** (100% coverage gate was running/stalled in prior sessions; see `research_state/workflow_run_diagnostics.jsonl` and leftover `bab_gate_p39w0*.log` artifacts).

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
| P39 WP1/WP2/WP3 | COMPLETE and frozen |
| **P39 WP0 — Full-Gate Close-Out** | **OPEN / BINDING** (not yet green) |

**Blocked sessions:** None active, but the gatekeeper (P39 WP0) is unclosed — every prior session that reached it left the 100% coverage gate incomplete. Do not treat the suite being green as "done"; coverage floor is the hard gate.

---

## Binding Initial Task — P39 WP0 "Full-Gate Close-Out" (P0, MUST land first)

**This is the sole agent-executable binding row.** Per `README.md` "CI, gates, and safety": P20–P38 and P39 WP1–WP3 are complete/frozen; **P39 WP0 is the sole agent-executable binding row until the full gate lands GREEN.** After P39 WP0, Campaign P40 ("Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict") becomes binding.

**Required command:**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

**Gate criteria (all must hold, exit 0):**
1. Full suite (~5,800 tests across 423 files) passes.
2. Coverage `TOTAL == 100%` for `strategies.betting_against_beta` (enforced via `BAB_GATE_MIN_COVERAGE=100`).
3. All post-pytest phases GREEN: replay gate (P29 WP0), workflow diagnostics (P30), P33/P34/P35/P36/P37/P38/P39 decision-consistency + summary checks.

**Known caveats / bottlenecks to remove:**
- The gate is slow under coverage (~5–6 min expected with xdist/sysmon; prior runs stalled at ~35% for 10+ min). **Do not abort mid-run.** Use a large timeout and `BAB_GATE_JOBS`; let it run to completion.
- A full gate appends one trailing newline to frozen `research_state/bab_p27/{risk_controls,reconciliation_e2e}.md` (P27 `run_*()` tests write to committed paths). **Restore with `git checkout -- research_state/bab_p27/` after a full run** so the tree stays clean.
- `ccxt` is optional; live-adapter tests skip without it (do not install ccxt just for the gate unless a test requires it).
- `.github/workflows/main.yml` does **not** invoke ruff/bab_gate/bab_reconcile_gate (repo token lacks `workflows:write`; a maintainer must add the `bab-gate` job via web UI). Do **not** re-attempt the CI push from an agent session.

**Exit condition for this task:** `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` exits 0 with TOTAL 100% coverage and every phase GREEN. Only then is P39 WP0 complete.

---

## Follow-On Focus Campaign (P40 + HANDOFF P0–P2 heavy work)

Once P39 WP0 is green, execute these in priority order. Future agents **must not avoid** these; each is a force multiplier for production readiness.

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
# 1. Verify environment
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python -m pytest tests/test_bab_backtest_contract_smoke.py -q  # 9 tests, ~1s
python -m strategies.betting_against_beta.cli --synthetic --dry-run

# 2. BINDING TASK — run the full gate to 100% coverage (P39 WP0)
BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh   # expect ~5-6 min; do not abort
# then restore the P27 touched files:
git checkout -- research_state/bab_p27/

# 3. Once green, real-data smoke test (P0 campaign)
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

**End of Handoff.** Next agent: execute P39 WP0 (`BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh`) to green, restore `research_state/bab_p27/`, then proceed to the P0 follow-on campaign (real-data hardening → walk-forward). Do not re-plan; the campaign is defined above.
