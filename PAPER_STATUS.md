# ACTIVE PAPER STATUS — BAB $100 USDT

**BOOTSTRAPPING · PAPER ONLY · NO LIVE ORDERS**

**Correct workflow:** [Open active workflow](https://github.com/takenthatusernameis-collab/Crypto-Betting-Against-Beta/actions/workflows/bab-paper-cycle.yml)

- Account: `mexc-usdt-forward-bab-100usdt-v1`
- Strategy generation: `crypto-bab-low-beta-long-high-beta-short-v1`
- Starting capital: **100.00000000 USDT**
- Account state: **INITIALIZED — FORWARD PAPER**
- Last report build: 2026-11-26 22:07:03 UTC
- Latest workflow run: [45902126190](https://github.com/takenthatusernameis-collab/Crypto-Betting-Against-Beta/actions/runs/45902126190) · run #8, attempt 1 · success · workflow_dispatch
- Latest processed daily candle: —
- Latest account event: 2026-11-26 22:06:43 UTC
- Primary execution journal: [PAPER_TRADE_JOURNAL.md](PAPER_TRADE_JOURNAL.md)


## MEXC market-data coverage

- Coverage state: **BOOTSTRAPPING**
- Active cross-margin contracts: 1169
- USDT-settled eligible contracts: 1087
- New histories completed this run: 150
- Histories remaining: 119
- API failures: 0
- Latest completed daily bar (UTC ms): 1795564800000
- Portfolio decision status: `BLOCKED_INCOMPLETE_MARKET_DATA`

Portfolio changes remain blocked until the full active cross-section has the required current daily history.

### Provisional BAB ranking preview

Not execution-approved until full-universe coverage passes.

**Lowest-beta long candidates**
- AKE_USDT: β(BTC)=-3.360082498561552
- SOXS_USDT: β(BTC)=-2.3547501277232388
- SKDD_USDT: β(BTC)=-1.7142559678544846

**Highest-beta short candidates**
- SI_USDT: β(BTC)=4.3222668131466095
- MSTU_USDT: β(BTC)=3.8421547490514065
- CATE_USDT: β(BTC)=3.253992605505298
## Current performance

| Metric | Value |
|---|---:|
| Initial capital | 100.00000000 USDT |
| **NAV** | **100.00000000 USDT** |
| Total return | +0.000% |
| Cash | 100.00000000 USDT |
| Unrealized P&L | +0.00000000 USDT |
| Fees paid | 0.00000000 USDT |
| Confirmed funding | +0.00000000 USDT |
| Gross exposure | 0.000× NAV |
| Net exposure | 0.000× NAV |
| Current drawdown from risk-window peak | +0.000% |
| Lifetime / cross-session maximum drawdown | +0.000% |
| Worst risk-session maximum drawdown | +0.000% |
| Sharpe ratio | Unavailable — sample gate not met |
| Sortino ratio | Unavailable — sample gate not met |
| Annualized daily volatility | Unavailable — sample gate not met |

### Maximum drawdown by risk session

| Session start (UTC) | Starting NAV | Latest NAV | Max drawdown | Marks |
|---|---:|---:|---:|---:|
| 2026-11-26 00:00:00 UTC | 100.00000000 | 100.00000000 | +0.000% | 7 |

## Open positions

| Symbol | Side | Quantity | Entry price | Mark | Notional (USDT) |
|---|---|---:|---:|---:|---:|
| No open positions yet | — | — | — | — | — |

## Primary path — equal exposure

The live forward-paper strategy sizes the long and short legs independently toward equal USDT notional (approximately 1× NAV per leg before lot rounding).

![Equal-exposure strategy equity curve](equal_exposure_equity_curve.svg)

## Alternative path — volatility-weighted sizing

This chart is a **visual-only counterfactual**, not an executed account. It reuses the primary strategy’s exact selected symbols, sides and rebalance timestamps; only the notional split changes. No alternative trade journal is created.

At each rebalance, the quieter leg receives the larger share using inverse 30-completed-day realized volatility. The leverage overlay is the ratio of equal-exposure pair volatility to the inverse-volatility pair’s base estimated volatility. It increases modeled gross exposure only when the alternative has lower estimated volatility. Estimates use only data available at that rebalance.

- Latest long / short allocation: **50.0% / 50.0%** of alternative gross notional.
- Latest volatility-matching leverage multiplier: **1.000×**.
- Estimated base volatility reduction before leverage: **+0.00%**.
- Volatility observations used: **0**; status: `AWAITING_FIRST_PAIR`.

![Inverse-volatility alternative equity curve](alternative_path_equity_curve.svg)

**Model limitations:** the counterfactual scales observed primary entry/exit fees and funding by shadow notional. It does not model additional nonlinear market impact, depth constraints, liquidation limits or exchange leverage caps for larger hypothetical exposure. It is not an executable leverage recommendation.

## Next workflow action

The latest completed UTC daily candle is waiting for full-universe history coverage; no portfolio decision has been consumed.

The daily-candle watermark is not advanced by this report. Only the paper workflow can consume a completed candle after full-history and execution gates pass. A blocked or incomplete run remains visible.

## Historical separation

The v3 $50 USDT generation and its preliminary snapshots are archived and excluded from this account’s NAV, returns, equity curves and metrics. The immutable event ledger remains intact.

## Alternative-path reconstruction notes

- No reconstruction warnings.

This is the compact live status page. The former detailed v3 report is retained under `archive/2026-11-18/` for audit purposes only.
