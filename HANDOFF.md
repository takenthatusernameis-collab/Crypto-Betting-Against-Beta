# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session)
**Time:** 2026-11-02T15:27:18Z | **Repo priority:** Crypto Betting Against Beta (BAB). All work must advance BAB.
**Gate 0 baseline:** PARTIAL (135 passed, 20 failed, 6 skipped). Bottleneck: data-quality implausible-return threshold (20) rejects legitimate price-derived/exchange fixtures.
**Bottlenecks removed:** load_returns_from_csv/json now accept & forward `quality`; load_prices skips quality on final returns. Remaining failures in datetime/exchange tests calling validate with quality=True on price-like data.
**FIRST ACTION:** Run Gate 0. Then fix data-quality campaign: either raise/normalize implausible-return handling for price-derived returns, or make datetime/exchange tests pass quality=False. Heavy work mandatory; maintain green.
**Timestamp:** 2026-11-02T15:27:18Z
**Priority from repo name:** CRYPTO BETTING AGAINST BETA (BAB).
