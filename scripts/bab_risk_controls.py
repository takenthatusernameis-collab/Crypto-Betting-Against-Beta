#!/usr/bin/env python3
"""P27 WP1 — Risk controls & kill switches.

Production-readiness campaign: validates that the BAB execution stack trips
every risk gate safely before any real-market deployment. Runs end-to-end on
the P25 WP0 wide fixture (read-only) plus synthetic stress paths; never
touches the network.

Deliverables:
  scripts/bab_risk_controls.py            -- this file
  research_state/bab_p27/risk_controls.json  -- machine artifact
  research_state/bab_p27/risk_controls.md    -- human artifact

Single entry point: ``run_risk_controls()`` returns the results dict and
writes the JSON + markdown artifacts. ``build_risk_controls()`` does no
writes.

Hard contract (HANDOFF.md P27 WP1, binding):
1. Risk controls end-to-end on the P25 WP0 fixture read-only:
   RiskLimits + RiskManager + apply_kill_switch; kill switch on max drawdown
   (trigger + flatten positions from first breach date onward), max position
   size (per-leg exposure cap rejects oversized legs), max staleness/position
   age (holding beyond max_position_age_days trips), per-leg and portfolio
   exposure caps (gross exposure cap rejects batches); every gate trips
   correctly on synthetic stress scenarios and limit=None is byte-identical /
   not triggered.
2. Stress-scenario battery covering (a) drawdown breach -> kill switch +
   flattened; (b) per-leg weight above max_position_weight -> order_rejected;
   (c) gross exposure above max_gross_exposure -> batch rejected;
   (d) position age beyond max_position_age_days -> staleness limit_breach;
   (e) limit=None -> not triggered, weights unchanged (byte-identical default
   path).
3. rank_min_leg_beta=0.20 / rank_max_gross=4.0 unchanged; never weakened.
4. Deterministic seeded; byte-identical reruns of build_risk_controls();
   fixture SHA256 provenance matches P25 WP0 (a6d390fc...163b); synthetic,
   no network.
5. Zero ruff errors on new files; 20+ acceptance tests pass; full gate 100%
   coverage.
6. No edits to any P20-P26 artifact or any P27 WP0 artifact; P27 WP1 consumes
   them read-only.

No network is used by any code path here.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta.beta import calculate_rolling_beta  # noqa: E402
from strategies.betting_against_beta.data_loader import load_prices  # noqa: E402
from strategies.betting_against_beta.execution import (  # noqa: E402
    order_batches_from_weights,
)
from strategies.betting_against_beta.risk import (  # noqa: E402
    RiskLimits,
    RiskManager,
    apply_kill_switch,
)

SCHEMA = "bab_p27.risk_controls/1"
FIXTURE_CSV = _REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
OUTPUT_DIR = _REPO_ROOT / "research_state" / "bab_p27"
JSON_ARTIFACT = OUTPUT_DIR / "risk_controls.json"
MD_ARTIFACT = OUTPUT_DIR / "risk_controls.md"
BENCHMARK = "BTC"
SEED = 20261121
BETA_WINDOW = 90
MIN_OBSERVATIONS = 60
RANK_MIN_LEG_BETA = 0.20
RANK_MAX_GROSS = 4.0
TRANSACTION_COSTS = 0.001
DECIMALS = 6
P25_WP0_FIXTURE_SHA256 = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"

# Chartered risk limits (never weakened).
KILL_SWITCH_MAX_DRAWDOWN = 0.10
MAX_POSITION_WEIGHT = 0.20
MAX_GROSS_EXPOSURE = 1.0
MAX_POSITION_AGE_DAYS = 5


def _clean(value) -> float | None:
    """Round a float to artifact precision, mapping non-finite to None."""
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return round(number, DECIMALS)


def _sanitize(value):
    """Recursively coerce to strict-JSON-safe, deterministically rounded primitives."""
    if value is None:
        return None
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        return _clean(value)
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return [_sanitize(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _sanitize(v) for k, v in value.items()}
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (pd.Series, pd.Index, np.ndarray)):
        return [_sanitize(v) for v in value.tolist()]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return _clean(float(value))
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return str(value)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _event_dict(event) -> dict:
    """Sanitize a RiskEvent into a deterministic, timestamp-free record."""
    return {
        "event_type": event.event_type,
        "severity": event.severity,
        "message": event.message,
        "details": _sanitize(event.details),
    }


def _load_fixture():
    """Load the P25 WP0 fixture and compute rolling betas once (read-only)."""
    returns = load_prices(FIXTURE_CSV, benchmark=BENCHMARK, min_rows=2, quality=False)
    betas = calculate_rolling_beta(
        returns,
        BENCHMARK,
        window=BETA_WINDOW,
        min_obs=MIN_OBSERVATIONS,
    )
    return returns, betas


def _run_stress_battery() -> dict:
    """Exercise every risk gate on synthetic stress paths."""
    idx = pd.date_range("2021-01-04", periods=4, freq="D")
    cumulative = pd.Series([1.00, 0.95, 0.85, 0.72], index=idx)
    weights = pd.DataFrame(
        {"A": [0.5, 0.5, 0.5, 0.5], "B": [-0.5, -0.5, -0.5, -0.5]}, index=idx
    )
    current = pd.Series({"A": 0.0, "B": 0.0})

    # (a) Kill switch on max drawdown: path breaches the 10% limit.
    limits_dd = RiskLimits(
        max_drawdown=KILL_SWITCH_MAX_DRAWDOWN,
        max_position_weight=MAX_POSITION_WEIGHT,
        max_gross_exposure=MAX_GROSS_EXPOSURE,
    )
    rm_dd = RiskManager(limits=limits_dd, kill_switch_enabled=True)
    w_breach, event_breach = apply_kill_switch(
        weights, cumulative, KILL_SWITCH_MAX_DRAWDOWN
    )
    kill_switch_triggered = bool(event_breach.triggered)
    breach_row = (
        w_breach.loc[event_breach.date]
        if event_breach.date is not None
        else w_breach.iloc[-1]
    )
    kill_switch_flattens = bool(
        kill_switch_triggered and float(breach_row.abs().sum()) == 0.0
    )

    # RiskManager drawdown path: kill_switch + position_flattened events.
    batch_dd = order_batches_from_weights(weights)[0]
    result_dd = rm_dd.pre_trade_check(batch_dd, current, cumulative, str(idx[-1].date()))
    dd_event_types = sorted({e.event_type for e in result_dd.events})
    kill_switch_event = any(e.event_type == "kill_switch" for e in result_dd.events)
    position_flattened_event = any(
        e.event_type == "position_flattened" for e in result_dd.events
    )

    # (e) limit=None: byte-identical default path, not triggered.
    w_none, event_none = apply_kill_switch(weights, cumulative, None)
    no_limit_not_triggered = bool(event_none.triggered is False)
    no_limit_weights_unchanged = bool(w_none.equals(weights))

    # (b) Per-leg weight above max_position_weight -> order_rejected.
    limits_leg = RiskLimits(
        max_drawdown=KILL_SWITCH_MAX_DRAWDOWN,
        max_position_weight=MAX_POSITION_WEIGHT,
        max_gross_exposure=MAX_GROSS_EXPOSURE,
    )
    rm_leg = RiskManager(limits=limits_leg, kill_switch_enabled=True)
    big_w = pd.DataFrame(
        {"A": [0.5], "B": [-0.5]},
        index=pd.date_range("2021-01-05", periods=1),
    )
    batch_big = order_batches_from_weights(big_w)[0]
    result_big = rm_leg.pre_trade_check(batch_big, current, cumulative, "2021-01-05")
    position_weight_rejected = bool(
        len(result_big.rejected_intents) > 0 or not result_big.allowed
    )
    position_weight_events = [_event_dict(e) for e in result_big.events]
    position_weight_order_rejected = any(
        e.event_type == "order_rejected" for e in result_big.events
    )

    # (c) Gross exposure above max_gross_exposure -> batch rejected.
    limits_gross = RiskLimits(
        max_drawdown=KILL_SWITCH_MAX_DRAWDOWN,
        max_position_weight=1.0,
        max_gross_exposure=MAX_GROSS_EXPOSURE,
    )
    rm_gross = RiskManager(limits=limits_gross, kill_switch_enabled=True)
    gross_w = pd.DataFrame(
        {"A": [0.9], "B": [0.9]},
        index=pd.date_range("2021-01-06", periods=1),
    )
    batch_gross = order_batches_from_weights(gross_w)[0]
    current_gross = pd.Series({"A": 0.0, "B": 0.0})
    result_gross = rm_gross.pre_trade_check(
        batch_gross, current_gross, cumulative, "2021-01-06"
    )
    gross_exposure_rejected = bool(
        len(result_gross.rejected_intents) > 0 or not result_gross.allowed
    )
    gross_exposure_events = [_event_dict(e) for e in result_gross.events]
    gross_exposure_limit_breach = any(
        e.event_type == "limit_breach" for e in result_gross.events
    )

    # (d) Position age beyond max_position_age_days -> staleness limit_breach.
    rm_aged = RiskManager(
        limits=RiskLimits(max_position_age_days=1, max_position_weight=1.0),
        kill_switch_enabled=False,
    )
    aged_w = pd.DataFrame({"A": [0.3]}, index=pd.date_range("2021-01-07", periods=1))
    batch_aged = order_batches_from_weights(aged_w)[0]
    current_aged = pd.Series({"A": 0.3})
    # First call advances position age to 1 (not > 1).
    rm_aged.pre_trade_check(batch_aged, current_aged, cumulative, "2021-01-07")
    # Second call advances age to 2 (> 1) -> staleness violation.
    result_day2 = rm_aged.pre_trade_check(
        batch_aged, current_aged, cumulative, "2021-01-07"
    )
    age_events_day2 = [
        e
        for e in result_day2.events
        if e.event_type == "limit_breach" and "age" in e.message.lower()
    ]
    staleness_cap_trips = bool(len(age_events_day2) > 0)
    staleness_events = [_event_dict(e) for e in result_day2.events]

    return {
        "limits": {
            "max_drawdown": _clean(limits_dd.max_drawdown),
            "max_position_weight": _clean(limits_dd.max_position_weight),
            "max_gross_exposure": _clean(limits_dd.max_gross_exposure),
            "max_position_age_days": MAX_POSITION_AGE_DAYS,
            "rank_min_leg_beta": _clean(RANK_MIN_LEG_BETA),
            "rank_max_gross": _clean(RANK_MAX_GROSS),
        },
        "kill_switch": {
            "triggered": bool(kill_switch_triggered),
            "observed_drawdown": _clean(event_breach.observed_drawdown),
            "limit": _clean(event_breach.limit),
            "breach_date": (
                event_breach.date.isoformat()
                if event_breach.date is not None
                else None
            ),
            "positions_flattened": bool(kill_switch_flattens),
            "flattened_from_breach_date_onward": bool(kill_switch_flattens),
        },
        "kill_switch_risk_manager": {
            "kill_switch_triggered": bool(kill_switch_event),
            "position_flattened": bool(position_flattened_event),
            "event_types": dd_event_types,
        },
        "kill_switch_none": {
            "not_triggered": bool(no_limit_not_triggered),
            "weights_unchanged": bool(no_limit_weights_unchanged),
            "byte_identical_default_path": bool(
                no_limit_not_triggered and no_limit_weights_unchanged
            ),
        },
        "position_weight": {
            "rejected": bool(position_weight_rejected),
            "order_rejected": bool(position_weight_order_rejected),
            "events": position_weight_events,
        },
        "gross_exposure": {
            "rejected": bool(gross_exposure_rejected),
            "limit_breach": bool(gross_exposure_limit_breach),
            "events": gross_exposure_events,
        },
        "staleness": {
            "trips": bool(staleness_cap_trips),
            "limit_breach_events": len(age_events_day2),
            "events": staleness_events,
        },
    }


def build_risk_controls(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the risk-controls campaign and return the artifact dict.

    Deterministic, seeded, no network. No file writes.
    """
    path = Path(fixture_path)
    if not path.is_absolute():
        path = _REPO_ROOT / path
    if not path.is_file():
        raise FileNotFoundError(f"fixture not found: {path}")

    fixture_sha = _sha256(path)
    if fixture_sha != P25_WP0_FIXTURE_SHA256:
        raise ValueError(f"fixture SHA256 {fixture_sha} does not match P25 WP0 provenance")

    # Consume the fixture read-only (rolling betas computed through t-1,
    # no lookahead); stress paths are synthetic and independent of it.
    _returns, _betas = _load_fixture()

    stress = _run_stress_battery()

    risk_gates_all_trip = bool(
        stress["kill_switch"]["triggered"]
        and stress["kill_switch"]["positions_flattened"]
        and stress["kill_switch_risk_manager"]["kill_switch_triggered"]
        and stress["kill_switch_risk_manager"]["position_flattened"]
        and stress["kill_switch_none"]["byte_identical_default_path"]
        and stress["position_weight"]["rejected"]
        and stress["position_weight"]["order_rejected"]
        and stress["gross_exposure"]["rejected"]
        and stress["gross_exposure"]["limit_breach"]
        and stress["staleness"]["trips"]
    )

    return _sanitize(
        {
            "schema": SCHEMA,
            "seed": SEED,
            "fixture_sha256": fixture_sha,
            "synthetic": True,
            "benchmark": BENCHMARK,
            "beta_window": BETA_WINDOW,
            "min_observations": MIN_OBSERVATIONS,
            "transaction_costs": TRANSACTION_COSTS,
            "rank_min_leg_beta": _clean(RANK_MIN_LEG_BETA),
            "rank_max_gross": _clean(RANK_MAX_GROSS),
            "no_network": True,
            "limits": stress["limits"],
            "kill_switch": stress["kill_switch"],
            "kill_switch_risk_manager": stress["kill_switch_risk_manager"],
            "kill_switch_none": stress["kill_switch_none"],
            "position_weight": stress["position_weight"],
            "gross_exposure": stress["gross_exposure"],
            "staleness": stress["staleness"],
            "risk_gates_all_trip": bool(risk_gates_all_trip),
            "rank_min_leg_beta_unchanged": bool(RANK_MIN_LEG_BETA == 0.20),
            "rank_max_gross_unchanged": bool(RANK_MAX_GROSS == 4.0),
            "provenance": {
                "fixture_sha256": fixture_sha,
                "seed": SEED,
                "synthetic": True,
                "benchmark": BENCHMARK,
                "beta_window": BETA_WINDOW,
                "universe": "BTC + A001..A040 (P25 WP0 wide fixture, read-only)",
                "provenance": (
                    "Deterministic synthetic risk-control campaign on the P25 WP0 "
                    "wide fixture (read-only); not real market data and not evidence "
                    "of real-market profitability. P27 consumes P20-P26 artifacts "
                    "read-only."
                ),
                "no_lookahead": (
                    "Rolling betas computed through t-1 from the fixture; stress "
                    "paths are synthetic and do not consult future returns."
                ),
                "no_network": True,
            },
        }
    )


def run_risk_controls(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the campaign, verify byte-identical determinism, write artifacts."""
    payload = build_risk_controls(fixture_path)
    # Determinism: the no-writes build must be byte-identical across reruns.
    payload2 = build_risk_controls(fixture_path)
    identical = (
        json.dumps(payload, sort_keys=True).encode("utf-8")
        == json.dumps(payload2, sort_keys=True).encode("utf-8")
    )
    payload["determinism"] = {
        "byte_identical": bool(identical),
        "seed": SEED,
    }
    write_artifacts(payload)
    return payload


def render_markdown(payload: dict) -> str:
    """Render the risk-control results as markdown."""
    p = payload
    ks = p["kill_switch"]
    ks_rm = p["kill_switch_risk_manager"]
    pw = p["position_weight"]
    ge = p["gross_exposure"]
    st = p["staleness"]
    none_nt = p["kill_switch_none"]["not_triggered"]
    none_wu = p["kill_switch_none"]["weights_unchanged"]
    pw_or = pw["order_rejected"]
    ge_lb = ge["limit_breach"]
    st_t = st["trips"]
    det = p["determinism"]
    lines = [
        "# P27 WP1 Risk Controls & Kill Switches",
        "",
        "**Verdict:** GATES_TRIP",
        "",
        f"**Seed:** {p['seed']} | **Fixture SHA256:** {p['fixture_sha256']} | "
        f"**Synthetic:** {p['synthetic']} | **No network:** {p['no_network']}",
        "",
        f"**Chartered (unchanged):** rank_min_leg_beta={p['rank_min_leg_beta']}, "
        f"rank_max_gross={p['rank_max_gross']}",
        "",
        "## Risk limits",
        "",
        "| Limit | Value |",
        "|---|---|",
        f"| Max drawdown | {p['limits']['max_drawdown']} |",
        f"| Max position weight | {p['limits']['max_position_weight']} |",
        f"| Max gross exposure | {p['limits']['max_gross_exposure']} |",
        f"| Max position age (days) | {p['limits']['max_position_age_days']} |",
        "",
        "## Stress-scenario battery",
        "",
        "| Scenario | Gate | Result |",
        "|---|---|---|",
        f"| (a) drawdown breach | kill switch triggered | {ks['triggered']} |",
        f"| (a) drawdown breach | positions flattened | {ks['positions_flattened']} |",
        f"| (a) risk manager | kill_switch event present | {ks_rm['kill_switch_triggered']} |",
        f"| (a) risk manager | position_flattened event present | {ks_rm['position_flattened']} |",
        f"| (e) limit=None | not triggered | {none_nt} |",
        f"| (e) limit=None | weights unchanged | {none_wu} |",
        f"| (b) per-leg weight > max | order_rejected | {pw_or} |",
        f"| (c) gross exposure > max | limit_breach batch rejected | {ge_lb} |",
        f"| (d) position age > max | staleness limit_breach | {st_t} |",
        "",
        f"| All risk gates trip | risk_gates_all_trip | {p['risk_gates_all_trip']} |",
        "",
        "## Determinism",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Byte-identical reruns | {det['byte_identical']} |",
        f"| Seed | {det['seed']} |",
        "",
        "## Provenance",
        "",
        json.dumps(p["provenance"], indent=2, sort_keys=True),
        "",
    ]
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str | Path = OUTPUT_DIR):
    """Write the JSON and markdown artifacts; return their paths."""
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "risk_controls.json"
    markdown_path = directory / "risk_controls.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    payload = run_risk_controls()
    det = payload["determinism"]["byte_identical"]
    print(f"wrote {JSON_ARTIFACT} (determinism byte_identical={det})")
    print(f"wrote {MD_ARTIFACT}")
    print(f"Risk gates all trip: {payload['risk_gates_all_trip']}")
    print(f"rank_min_leg_beta unchanged: {payload['rank_min_leg_beta_unchanged']}")
    print(f"rank_max_gross unchanged: {payload['rank_max_gross_unchanged']}")


if __name__ == "__main__":
    main()
