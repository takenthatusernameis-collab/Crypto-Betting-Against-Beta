# BAB P39 WP1 — Regime-Conditional Deflated Significance & Tail Risk

Schema `bab_p39.regime_conditional/1`. Controlled synthetic stimulus: not real market data and not market profitability evidence. The verdict is honest and may be negative.

**Campaign verdict:** **DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME**
**Reason:** At least one well-populated (seed, regime) cell has DSR < 0.5 after deflation over n_trials_total=552, or neutrality fails at some cell; honest negative verdict.

## Setup

- Seeds: 8 (base=20261120, increment=1009)
- beta_window: 90d, quantile: 0.300000
- weighting: equal, beta_neutral: True, dollar_neutral: True
- regime lookback: 20d, min periods per regime: 30
- regime labels: bull_low_vol, bull_mid_vol, bull_high_vol, bear_low_vol, bear_mid_vol, bear_high_vol

## Regime definition (causal, lagged, no lookahead)

- trend[t]: sign of mean BTC return over the trailing 20d window ending at t-1 (bull if > 0, else bear).
- vol[t]: std of BTC return over the trailing 20d window ending at t-1.
- vol tercile[t]: expanding percentile of vol[t] within vol[0:t+1] (low / mid / high).
- regime[t] = trend[t] x vol tercile[t]; the label at t uses only data strictly before t.

## Trial enumeration (read-only from P38 WP1)

Deflation over n_trials_total = **552**, read-only from research_state/bab_p38/deflated_summary.json (trial_enumeration.n_trials_total). Never re-enumerated or invented here.

## Per-regime results (aggregated across the eight seeds)

| Regime | N cells | N OK | N survive | DSR mean | PSR mean | Survive all |
|---|---|---|---|---|---|---|
| bull_low_vol | 8 | 8 | 7 | 0.838955 | 0.874266 | False |
| bull_mid_vol | 8 | 8 | 5 | 0.605503 | 0.622470 | False |
| bull_high_vol | 8 | 8 | 3 | 0.412219 | 0.375007 | False |
| bear_low_vol | 8 | 8 | 5 | 0.613467 | 0.626873 | False |
| bear_mid_vol | 8 | 0 | 0 | None | None | True |
| bear_high_vol | 8 | 0 | 0 | None | None | True |

## Neutrality (every cell)

| Regime | model beta <= 1e-3 | dollar <= 1e-9 | |realized beta| <= 0.15 |
|---|---|---|---|
| bull_low_vol | True | True | True |
| bull_mid_vol | True | True | True |
| bull_high_vol | True | True | True |
| bear_low_vol | True | True | True |
| bear_mid_vol | True | True | True |
| bear_high_vol | True | True | True |

## Interpretation

- DSR = Deflated Sharpe Ratio: probability the observed Sharpe is genuine skill after correcting for the multiple trials searched (n_trials_total). DSR >= 0.50 means more likely than not genuine skill.
- PSR = Probabilistic Sharpe Ratio: probability the Sharpe exceeds zero (analytical, Bailey & Lopez de Prado).
- CVaR/expected-shortfall/drawdown characterize the left tail within each regime; neutrality invariants hold at every cell.
- Regimes are causal and lagged: no lookahead, so this is a genuine out-of-sample stability test, not an in-sample fit.
- Synthetic-provenance caveat: results are on the committed synthetic wide universe (BTC prices + seeded idiosyncratic noise), not real market data. Never market alpha.
