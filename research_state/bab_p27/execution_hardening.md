# P27 WP0 Execution Adapter Hardening & Dry-Run Paper Campaign

**Verdict:** HARDENED

**Seed:** 20261121 | **Fixture SHA256:** a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b | **Synthetic:** True | **No network:** True

**Chartered (unchanged):** rank_min_leg_beta=0.2, rank_max_gross=4.0

## Paper adapter end-to-end (`--adapter paper` / `--paper-trading`)

| Check | Value |
|---|---|
| Orders emitted | 13858 |
| Fills emitted | 13858 |
| Diagnostics rows | 398 |
| BABStrategy+PaperAdapter present | True |
| Adapter fills == engine fills | True |
| Backtest PnL | 0.001215 |

| Lifecycle check | Result |
|---|---|
| No double-submit | True |
| No orphan fills | True |
| No fill without order | True |
| n_fills == n_orders | True |
| Weights sum to zero | True |
| Beta-neutral (sum w_i*beta_i ~= 0) | True |
| Lifecycle valid | True |

## Dry-run live adapter health check

| Check | Result |
|---|---|
| Strict JSON | True |
| Has required keys | True |
| dry_run=true | True |
| mode=live | True |
| Never implicit live execution | True |

## Risk controls

| Check | Result |
|---|---|
| Kill switch triggered on drawdown breach | True |
| Kill switch flattens positions | True |
| Kill switch limit=None not triggered | True |
| Kill switch limit=None weights unchanged | True |
| Max position weight rejected | True |
| Gross exposure cap rejected | True |
| Position age/staleness cap trips | True |
| All risk gates trip | True |

## Reconciliation enforcement (R5-B + R5-C)

| Check | Result |
|---|---|
| Emit-only gate passes | True |
| Drift gate breached (tolerance=0.0) | True |
| Max-mismatch gate breached | True |
| Reconciliation enforced | True |

## Determinism

| Byte-identical reruns | True |
| Seed | 20261121 |

## Provenance

{
  "date_first": "2021-01-05",
  "date_last": "2022-07-15",
  "fixture_sha256": "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b",
  "no_lookahead": "Weights at row t depend on data through t-1 via the one-day backtest lag and rolling betas computed through t-1; the OOS return at row t is never used to weight itself.",
  "provenance": "Deterministic synthetic P25 WP0 wide universe; not real market data and not evidence of real-market profitability. P27 consumes P20-P26 artifacts read-only.",
  "rank_rule": "Equal-weight dollar-neutral + beta-neutral book (rank_min_leg_beta=0.2, rank_max_gross=4.0 recorded as chartered defaults, never weakened).",
  "seed": 20261121,
  "synthetic": true,
  "universe": "BTC + A001..A040 (DEL all-NaN column dropped by loader)",
  "weightings": [
    "equal"
  ]
}

