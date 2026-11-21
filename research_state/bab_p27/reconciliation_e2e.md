# P27 WP2 Reconciliation Enforcement End-to-End

**Verdict:** ALL_GATES_TRIP

**Seed:** 20261121 | **Fixture SHA256:** a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b | **Synthetic:** True | **No network:** True

**Chartered (unchanged):** rank_min_leg_beta=0.2, rank_max_gross=4.0

## Real paper run (P25 WP0 fixture, read-only)

| Check | Result |
|---|---|
| Emit-only gate passes | True |
| Emit-only violations | 0 |
| Drift gate breached (tolerance=0.0) | True |
| Drift violations | 2 |
| Tolerance exactly equal to drift passes | True |
| Max-mismatch gate breached (limit=0) | True |
| Max-mismatch violations | 1 |
| Observed cost drift max_abs | 0.000762 |
| Observed cost n_mismatches | 338 |
| Observed fills n_mismatches | 0 |
| Reconciliation enforced | True |

## Stress-scenario battery (synthetic drift paths)

| Scenario | Gate | ok | violations | drift_max_abs | n_mismatches |
|---|---|---|---|---|---|
| (a) drift above tolerance | fail-closed | False | 2 | 0.002 | 5 |
| (b) tolerance exactly equal | pass | True | 0 | 0.002 | 5 |
| (c) mismatch above limit | fail-closed | False | 1 | 0.002 | 5 |
| (d) emit-only | pass | True | 0 | 0.002 | 5 |
| (e) clean path | pass | True | 0 | 0.0 | 0 |

| Observed synthetic drift max_abs | 0.002 |
| Observed synthetic n_mismatches | 5 |

## Determinism

| Check | Result |
|---|---|
| Byte-identical reruns | True |
| Seed | 20261121 |

## Provenance

{
  "benchmark": "BTC",
  "beta_window": 90,
  "fixture_sha256": "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b",
  "no_lookahead": "Rolling betas computed through t-1 from the fixture; stress paths are synthetic and do not consult future returns.",
  "no_network": true,
  "provenance": "Deterministic synthetic reconciliation-enforcement campaign on the P25 WP0 wide fixture (read-only); not real market data and not evidence of real-market profitability. P27 consumes P20-P26 artifacts read-only.",
  "seed": 20261121,
  "synthetic": true,
  "universe": "BTC + A001..A040 (P25 WP0 wide fixture, read-only)"
}
