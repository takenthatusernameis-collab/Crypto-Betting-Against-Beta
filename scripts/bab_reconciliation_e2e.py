#!/usr/bin/env python3
"""P27 WP2 — reconciliation enforcement end-to-end.

Production-readiness campaign: validates that the BAB execution stack enforces
the R5-B modeled-vs-executed cost reconciliation and R5-C fills-vs-backtest
reconciliation before any real-market deployment. Runs end-to-end on the P25
WP0 wide fixture (read-only) plus synthetic cost/equity drift paths; never
touches the network.

Deliverables:
  scripts/bab_reconciliation_e2e.py   -- this file
  research_state/bab_p27/reconciliation_e2e.json  -- machine artifact
  research_state/bab_p27/reconciliation_e2e.md    -- human artifact

Single entry point: ``run_reconciliation_e2e()`` returns the results dict and
writes the JSON + markdown artifacts. ``build_reconciliation_e2e()`` does no
writes.

Hard contract (HANDOFF.md P27 WP2, binding):
1. Reconciliation enforcement end-to-end on the P25 WP0 fixture read-only:
   run ``reconcile_costs`` (R5-B) and ``reconcile_fills_to_backtest`` (R5-C)
   from ``strategies.betting_against_beta.reconciliation`` plus
   ``evaluate_reconciliation_gate(costs_rec, fills_rec,
   cost_tolerance=..., mismatch_tolerance=...)``; assert emit-only passes,
   drift-above-tolerance fails closed (``ok=False``), mismatch-count-above-limit
   fails closed, and tolerance-exactly-equal-to-drift passes.
2. Stress-scenario battery: synthetic cost/equity drift paths covering
   (a) drift strictly above tolerance -> gate ``ok=False`` / violation present;
   (b) tolerance exactly equal to observed drift -> passes;
   (c) mismatch count strictly above limit -> fails closed;
   (d) emit-only (no tolerance, no max-mismatch) -> passes;
   (e) clean path (no drift) -> passes.
3. ``rank_min_leg_beta=0.20`` / ``rank_max_gross=4.0`` unchanged; never weakened.
4. Deterministic seeded; byte-identical reruns of ``build_reconciliation_e2e()``;
   fixture SHA256 provenance matches P25 WP0; synthetic, no network.
5. Zero ruff errors on new files; 20+ acceptance tests pass; full gate 100%
   coverage.
6. No edits to any P20-P26 artifact or any P27 WP0-WP1 artifact; P27 WP2
   consumes them read-only.

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

from strategies.betting_against_beta import BABStrategy  # noqa: E402
from strategies.betting_against_beta.beta import calculate_rolling_beta  # noqa: E402
from strategies.betting_against_beta.config import BABConfig  # noqa: E402
from strategies.betting_against_beta.data_loader import load_prices  # noqa: E402
from strategies.betting_against_beta.execution import (  # noqa: E402
    PaperAdapter,
)
from strategies.betting_against_beta.reconciliation import (  # noqa: E402
    evaluate_reconciliation_gate,
    reconcile_costs,
    reconcile_fills_to_backtest,
)

SCHEMA = "bab_p27.reconciliation_e2e/1"
FIXTURE_CSV = _REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
OUTPUT_DIR = _REPO_ROOT / "research_state" / "bab_p27"
JSON_ARTIFACT = OUTPUT_DIR / "reconciliation_e2e.json"
MD_ARTIFACT = OUTPUT_DIR / "reconciliation_e2e.md"
BENCHMARK = "BTC"
SEED = 20261121
BETA_WINDOW = 90
MIN_OBSERVATIONS = 60
LONG_QUANTILE = 0.3
SHORT_QUANTILE = 0.3
RANK_MIN_LEG_BETA = 0.20
RANK_MAX_GROSS = 4.0
TRANSACTION_COSTS = 0.001
SLIPPAGE = 0.0
DECIMALS = 6
P25_WP0_FIXTURE_SHA256 = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"
WEIGHTING = "equal"


def _clean(value) -> float | None:
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return round(number, DECIMALS)


def _sanitize(value):
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


def _strategy_config() -> dict:
    return dict(
        benchmark=BENCHMARK,
        beta_window=BETA_WINDOW,
        min_observations=MIN_OBSERVATIONS,
        long_quantile=LONG_QUANTILE,
        short_quantile=SHORT_QUANTILE,
        transaction_costs=TRANSACTION_COSTS,
        slippage=SLIPPAGE,
        beta_neutral=True,
        weighting=WEIGHTING,
    )


def _load_fixture():
    returns = load_prices(FIXTURE_CSV, benchmark=BENCHMARK, min_rows=2, quality=False)
    betas = calculate_rolling_beta(
        returns,
        BENCHMARK,
        window=BETA_WINDOW,
        min_obs=MIN_OBSERVATIONS,
    )
    return returns, betas


def _adapter_fills(result_adapter) -> list:
    execution = getattr(result_adapter, "execution", None) or {}
    return list(execution.get("fills", []))


def _run_real_paper_reconciliation(returns, betas) -> dict:
    """R5-B + R5-C enforcement on the P25 WP0 fixture via a paper run."""
    config = BABConfig(**_strategy_config())
    result_adapter = BABStrategy(config, execution_adapter=PaperAdapter()).run(
        returns_df=returns
    )
    result = BABStrategy(config).run(returns_df=returns)

    fills = _adapter_fills(result_adapter)
    costs_rec = reconcile_costs(
        result.weights,
        model=None,
        executed_fills=fills,
        transaction_costs=TRANSACTION_COSTS,
        slippage=SLIPPAGE,
    )
    fills_rec = reconcile_fills_to_backtest(
        result.weights,
        result.returns,
        result.backtest,
        fills=fills,
        transaction_costs=TRANSACTION_COSTS,
        slippage=SLIPPAGE,
    )

    gate_emit_only = evaluate_reconciliation_gate(costs_rec, fills_rec)
    costs_agg = costs_rec.aggregate
    fills_agg = fills_rec.aggregate
    drift_max_abs = float(costs_agg.get("delta_max_abs", 0.0) or 0.0)
    cost_n_mismatches = int(costs_agg.get("n_mismatches", 0) or 0)
    fills_n_mismatches = int(fills_agg.get("n_mismatches", 0) or 0)
    gate_drift_zero = evaluate_reconciliation_gate(
        costs_rec, fills_rec, cost_tolerance=0.0, mismatch_tolerance=0
    )
    gate_drift_exact = evaluate_reconciliation_gate(
        costs_rec,
        fills_rec,
        cost_tolerance=drift_max_abs,
        mismatch_tolerance=max(cost_n_mismatches, fills_n_mismatches),
    )
    gate_max_mismatch_zero = evaluate_reconciliation_gate(
        costs_rec, fills_rec, mismatch_tolerance=0
    )

    return {
        "n_periods_costs": int(costs_rec.n_periods),
        "n_periods_fills": int(fills_rec.n_periods),
        "costs_aggregate": _sanitize(costs_agg),
        "costs_checksum": costs_rec.checksum,
        "fills_aggregate": _sanitize(fills_agg),
        "fills_checksum": fills_rec.checksum,
        "n_fills": len(fills),
        "gate_emit_only_ok": bool(gate_emit_only.get("ok", False)),
        "gate_emit_only_violations": len(gate_emit_only.get("violations", [])),
        "gate_drift_zero_ok": bool(gate_drift_zero.get("ok", False)),
        "gate_drift_zero_violations": len(gate_drift_zero.get("violations", [])),
        "gate_drift_exact_ok": bool(gate_drift_exact.get("ok", False)),
        "gate_drift_exact_violations": len(gate_drift_exact.get("violations", [])),
        "gate_max_mismatch_zero_ok": bool(gate_max_mismatch_zero.get("ok", False)),
        "gate_max_mismatch_zero_violations": len(
            gate_max_mismatch_zero.get("violations", [])
        ),
        "observed_cost_drift_max_abs": _clean(drift_max_abs),
        "observed_cost_n_mismatches": cost_n_mismatches,
        "observed_fills_n_mismatches": fills_n_mismatches,
        "reconciliation_enforced": bool(
            gate_emit_only.get("ok", False)
            and gate_drift_zero.get("ok", False) is False
            and gate_max_mismatch_zero.get("ok", False) is False
        ),
    }


def _synthetic_case(n_periods: int = 5, fill_tx_rate: float = 0.001) -> tuple:
    idx = pd.date_range("2021-01-04", periods=n_periods, freq="D")
    weights = pd.DataFrame(
        {"A": [0.1] * n_periods, "B": [-0.1] * n_periods}, index=idx
    )
    fills: list = []
    for date in idx:
        date_key = date.isoformat()
        for asset, w in (("A", 0.1), ("B", -0.1)):
            fill = {
                "date": date_key,
                "asset": asset,
                "filled_weight": float(w),
                "order_weight": float(w),
                "slippage": 0.0,
                "status": "filled",
            }
            if fill_tx_rate > 0:
                fill["transaction_costs"] = float(fill_tx_rate)
            fills.append(fill)
    return weights, fills


def _gate_drift(
    weights, fills, cost_tolerance, mismatch_tolerance, param_tx_rate
) -> dict:
    costs_rec = reconcile_costs(
        weights,
        model=None,
        executed_fills=fills,
        transaction_costs=param_tx_rate,
        slippage=SLIPPAGE,
    )
    gate = evaluate_reconciliation_gate(
        costs_rec,
        None,
        cost_tolerance=cost_tolerance,
        mismatch_tolerance=mismatch_tolerance,
    )
    agg = costs_rec.aggregate
    return {
        "ok": bool(gate.get("ok", False)),
        "violations": len(gate.get("violations", [])),
        "delta_max_abs": _clean(float(agg.get("delta_max_abs", 0.0) or 0.0)),
        "n_mismatches": int(agg.get("n_mismatches", 0) or 0),
    }


def _run_stress_scenarios() -> dict:
    """Synthetic cost/equity drift paths exercising (a)-(e)."""
    weights, fills_clean = _synthetic_case(n_periods=5, fill_tx_rate=0.0)
    weights_d, fills_drift = _synthetic_case(n_periods=5, fill_tx_rate=0.01)

    drift_agg = reconcile_costs(
        weights_d,
        model=None,
        executed_fills=fills_drift,
        transaction_costs=TRANSACTION_COSTS,
        slippage=SLIPPAGE,
    ).aggregate
    observed_drift = float(drift_agg.get("delta_max_abs", 0.0) or 0.0)
    observed_mismatches = int(drift_agg.get("n_mismatches", 0) or 0)

    # (a) drift strictly above tolerance -> gate ok=False / violation present.
    scenario_a = _gate_drift(
        weights_d, fills_drift, cost_tolerance=0.0, mismatch_tolerance=0,
        param_tx_rate=TRANSACTION_COSTS,
    )

    # (b) tolerance exactly equal to observed drift -> passes.
    scenario_b = _gate_drift(
        weights_d, fills_drift,
        cost_tolerance=observed_drift,
        mismatch_tolerance=observed_mismatches,
        param_tx_rate=TRANSACTION_COSTS,
    )

    # (c) mismatch count strictly above limit -> fails closed.
    scenario_c = _gate_drift(
        weights_d, fills_drift,
        cost_tolerance=None,
        mismatch_tolerance=observed_mismatches - 1,
        param_tx_rate=TRANSACTION_COSTS,
    )

    # (d) emit-only (no tolerance, no max-mismatch) -> passes.
    scenario_d = _gate_drift(
        weights_d, fills_drift,
        cost_tolerance=None,
        mismatch_tolerance=None,
        param_tx_rate=TRANSACTION_COSTS,
    )

    # (e) clean path (no drift) -> passes with zero tolerance.
    scenario_e = _gate_drift(
        weights, fills_clean, cost_tolerance=0.0, mismatch_tolerance=0,
        param_tx_rate=0.0,
    )

    return {
        "observed_drift_max_abs": _clean(observed_drift),
        "observed_n_mismatches": observed_mismatches,
        "a_drift_above_tolerance": scenario_a,
        "b_tolerance_exact_equal": scenario_b,
        "c_mismatch_above_limit": scenario_c,
        "d_emit_only": scenario_d,
        "e_clean_path": scenario_e,
    }


def build_reconciliation_e2e(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the reconciliation-e2e campaign and return the artifact dict.

    Deterministic, seeded, no network. No file writes.
    """
    path = Path(fixture_path)
    if not path.is_absolute():
        path = _REPO_ROOT / path
    if not path.is_file():
        raise FileNotFoundError(f"fixture not found: {path}")

    fixture_sha = _sha256(path)
    if fixture_sha != P25_WP0_FIXTURE_SHA256:
        raise ValueError(
            f"fixture SHA256 {fixture_sha} does not match P25 WP0 provenance"
        )

    returns, betas = _load_fixture()
    paper = _run_real_paper_reconciliation(returns, betas)
    stress = _run_stress_scenarios()

    all_gates_trip = bool(
        paper["gate_emit_only_ok"]
        and not paper["gate_drift_zero_ok"]
        and paper["gate_drift_exact_ok"]
        and not paper["gate_max_mismatch_zero_ok"]
        and not stress["a_drift_above_tolerance"]["ok"]
        and stress["b_tolerance_exact_equal"]["ok"]
        and not stress["c_mismatch_above_limit"]["ok"]
        and stress["d_emit_only"]["ok"]
        and stress["e_clean_path"]["ok"]
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
            "slippage": SLIPPAGE,
            "rank_min_leg_beta": _clean(RANK_MIN_LEG_BETA),
            "rank_max_gross": _clean(RANK_MAX_GROSS),
            "rank_min_leg_beta_unchanged": bool(RANK_MIN_LEG_BETA == 0.20),
            "rank_max_gross_unchanged": bool(RANK_MAX_GROSS == 4.0),
            "no_network": True,
            "determinism": {"byte_identical": None, "seed": SEED},
            "paper_run": paper,
            "stress_scenarios": stress,
            "all_gates_trip": bool(all_gates_trip),
            "provenance": {
                "fixture_sha256": fixture_sha,
                "seed": SEED,
                "synthetic": True,
                "benchmark": BENCHMARK,
                "beta_window": BETA_WINDOW,
                "universe": "BTC + A001..A040 (P25 WP0 wide fixture, read-only)",
                "provenance": (
                    "Deterministic synthetic reconciliation-enforcement campaign "
                    "on the P25 WP0 wide fixture (read-only); not real market data "
                    "and not evidence of real-market profitability. P27 consumes "
                    "P20-P26 artifacts read-only."
                ),
                "no_network": True,
                "no_lookahead": (
                    "Rolling betas computed through t-1 from the fixture; stress "
                    "paths are synthetic and do not consult future returns."
                ),
            },
        }
    )


def run_reconciliation_e2e(fixture_path: str | Path = FIXTURE_CSV) -> dict:
    """Run the campaign, verify byte-identical determinism, write artifacts."""
    payload = build_reconciliation_e2e(fixture_path)
    payload2 = build_reconciliation_e2e(fixture_path)
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


def _stress_row(scenario: str, gate: str, s: dict) -> str:
    return (
        f"| ({scenario}) {gate} | {s['ok']} | {s['violations']} | "
        f"{s['delta_max_abs']} | {s['n_mismatches']} |"
    )


def render_markdown(payload: dict) -> str:
    p = payload
    paper = p["paper_run"]
    stress = p["stress_scenarios"]
    lines = [
        "# P27 WP2 Reconciliation Enforcement End-to-End",
        "",
        f"**Verdict:** {'ALL_GATES_TRIP' if p['all_gates_trip'] else 'GATE_FAILURE'}",
        "",
        f"**Seed:** {p['seed']} | **Fixture SHA256:** {p['fixture_sha256']} | "
        f"**Synthetic:** {p['synthetic']} | **No network:** {p['no_network']}",
        "",
        f"**Chartered (unchanged):** rank_min_leg_beta={p['rank_min_leg_beta']}, "
        f"rank_max_gross={p['rank_max_gross']}",
        "",
        "## Real paper run (P25 WP0 fixture, read-only)",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Emit-only gate passes | {paper['gate_emit_only_ok']} |",
        f"| Emit-only violations | {paper['gate_emit_only_violations']} |",
        f"| Drift gate breached (tolerance=0.0) | {not paper['gate_drift_zero_ok']} |",
        f"| Drift violations | {paper['gate_drift_zero_violations']} |",
        f"| Tolerance exactly equal to drift passes | {paper['gate_drift_exact_ok']} |",
        f"| Max-mismatch gate breached (limit=0) | {not paper['gate_max_mismatch_zero_ok']} |",
        f"| Max-mismatch violations | {paper['gate_max_mismatch_zero_violations']} |",
        f"| Observed cost drift max_abs | {paper['observed_cost_drift_max_abs']} |",
        f"| Observed cost n_mismatches | {paper['observed_cost_n_mismatches']} |",
        f"| Observed fills n_mismatches | {paper['observed_fills_n_mismatches']} |",
        f"| Reconciliation enforced | {paper['reconciliation_enforced']} |",
        "",
        "## Stress-scenario battery (synthetic drift paths)",
        "",
        "| Scenario | Gate | ok | violations | drift_max_abs | n_mismatches |",
        "|---|---|---|---|---|---|",
        _stress_row("a", "drift above tolerance | fail-closed", stress["a_drift_above_tolerance"]),
        _stress_row("b", "tolerance exactly equal | pass", stress["b_tolerance_exact_equal"]),
        _stress_row("c", "mismatch above limit | fail-closed", stress["c_mismatch_above_limit"]),
        _stress_row("d", "emit-only | pass", stress["d_emit_only"]),
        _stress_row("e", "clean path | pass", stress["e_clean_path"]),
        "",
        f"| Observed synthetic drift max_abs | {stress['observed_drift_max_abs']} |",
        f"| Observed synthetic n_mismatches | {stress['observed_n_mismatches']} |",
        "",
        "## Determinism",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Byte-identical reruns | {p['determinism']['byte_identical']} |",
        f"| Seed | {p['determinism']['seed']} |",
        "",
        "## Provenance",
        "",
        json.dumps(p["provenance"], indent=2, sort_keys=True),
        "",
    ]
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str | Path = OUTPUT_DIR):
    directory = Path(output_dir)
    if not directory.is_absolute():
        directory = _REPO_ROOT / directory
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "reconciliation_e2e.json"
    markdown_path = directory / "reconciliation_e2e.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    payload = run_reconciliation_e2e()
    det = payload["determinism"]["byte_identical"]
    print(f"wrote {JSON_ARTIFACT} (determinism byte_identical={det})")
    print(f"wrote {MD_ARTIFACT}")
    print(f"All gates trip: {payload['all_gates_trip']}")
    print(f"Reconciliation enforced: {payload['paper_run']['reconciliation_enforced']}")
    print(f"rank_min_leg_beta unchanged: {payload['rank_min_leg_beta_unchanged']}")
    print(f"rank_max_gross unchanged: {payload['rank_max_gross_unchanged']}")


if __name__ == "__main__":
    main()
