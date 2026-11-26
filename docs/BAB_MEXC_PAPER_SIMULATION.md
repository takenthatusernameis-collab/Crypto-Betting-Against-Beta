# BAB MEXC Forward Paper Simulation

## Purpose and strategy

This workflow runs an independent, paper-only MEXC USDT perpetual simulation. It reuses the public MEXC market-data, execution-cost, funding, immutable event-ledger, recovery and snapshot architecture maintained in the `high-vs-low` paper project. The BAB repository supplies the signal.

At each newly completed UTC daily candle, the strategy estimates each eligible USDT perpetual's 90-observation rolling OLS beta to BTC using at least 60 aligned daily returns. The lowest-beta eligible contract is the long; the highest-beta eligible contract is the short. The selected contracts must be distinct. The benchmark itself is excluded from trading. The daily candle watermark and one-decision-per-bar guard prevent duplicate portfolio decisions.

## Portfolio paths

- **Main path:** the engine's actual equal-notional two-leg paper portfolio.
- **Alternative path:** an inverse-volatility shadow equity curve replayed from the same selected pairs, decision timestamps and event ledger, using the 30-observation volatility sizing profile from the established MEXC simulation. It is a separately calculated equity path, not a second set of exchange orders or a second independent execution ledger.

## Cadence

The workflow has an intended `*/5 * * * *` GitHub Actions schedule. This is best-effort scheduling, not a five-minute service-level guarantee. Every invocation checks the MEXC server clock and completed daily-bar watermark. A new completed daily candle permits a single portfolio decision after required data coverage is complete; intervening invocations use the engine's snapshot-only path to mark equity, funding and risk without recomputing rankings or resizing ordinary positions.

At a daily decision, the BAB runner refreshes the required rolling 90-day candle window for the complete active USDT-settled cross-section in one pass. It does not inherit the high-vs-low engine's lifetime-history requirement: BAB needs at most 90 daily return observations, and requires at least 60 aligned returns. The runner uses the established MEXC contract discovery, all-market ticker subscription, public candle client, execution-cost checks, immutable state ledger, funding handling and reporting paths. Its public candle requests are spaced 0.12 seconds apart (8.3 requests/second), below MEXC's documented 20-requests-per-two-seconds limit.

Contracts without at least 61 consecutive completed daily closes through the decision bar (for example, newly listed contracts) are explicitly excluded from that ranking, without blocking otherwise valid candidates. A low-beta research candidate whose 3x-ATR long stop would be non-positive is retained in the research ranking but removed from the executable long list; the shared pair selector rechecks this condition during retries of a frozen daily signal. A public API request failure, missing market-wide ticker coverage, or unavailable BTC benchmark remains fail-closed; the ranking is not published as a successful trading decision using a partial API response. The full-universe refresh is persisted to the market-data branch and the portfolio decision remains once per completed UTC daily bar.

## Data and execution assumptions

- Public MEXC Futures contract-v1 endpoints only.
- Active cross-margin perpetual discovery; only USDT-settled contracts enter the paper account.
- Paper fills use public order-book depth, contract quantity rules, exchange fee metadata and slippage/shortfall checks.
- Confirmed perpetual funding cashflows are applied to the paper ledger.
- No API keys, private endpoints, wallet access, testnet, or live exchange orders.
- Independent 100 USDT initial paper NAV and account namespace.
- Market-data partitions are persisted on the `market-data` branch; immutable paper events are persisted on the `state` branch.

The BAB beta ranking is not the canonical leverage-scaled Frazzini–Pedersen BAB factor portfolio: it is a single-contract low-beta-long/high-beta-short implementation of the repository's documented BAB signal direction. Performance remains forward-paper evidence, not proof of a profitable live strategy.
