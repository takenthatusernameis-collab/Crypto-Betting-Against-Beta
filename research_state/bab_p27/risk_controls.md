# P27 WP1 Risk Controls & Kill Switches

**Verdict:** GATES_TRIP

**Seed:** 20261121 | **Fixture SHA256:** a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b | **Synthetic:** True | **No network:** True

**Chartered (unchanged):** rank_min_leg_beta=0.2, rank_max_gross=4.0

## Risk limits

| Limit | Value |
|---|---|
| Max drawdown | 0.1 |
| Max position weight | 0.2 |
| Max gross exposure | 1.0 |
| Max position age (days) | 5 |

## Stress-scenario battery

| Scenario | Gate | Result |
|---|---|---|
| (a) drawdown breach | kill switch triggered | True |
| (a) drawdown breach | positions flattened | True |
| (a) risk manager | kill_switch event present | True |
| (a) risk manager | position_flattened event present | True |
| (e) limit=None | not triggered | True |
| (e) limit=None | weights unchanged | True |
| (b) per-leg weight > max | order_rejected | True |
| (c) gross exposure > max | limit_breach batch rejected | True |
| (d) position age > max | staleness limit_breach | True |

| All risk gates trip | risk_gates_all_trip | True |

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
  "provenance": "Deterministic synthetic risk-control campaign on the P25 WP0 wide fixture (read-only); not real market data and not evidence of real-market profitability. P27 consumes P20-P26 artifacts read-only.",
  "seed": 20261121,
  "synthetic": true,
  "universe": "BTC + A001..A040 (P25 WP0 wide fixture, read-only)"
}
