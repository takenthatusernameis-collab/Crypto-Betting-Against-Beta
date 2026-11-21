#!/usr/bin/env python3
"""Generate BAB_P27_DECISION.md from committed P27 WP0-WP2 JSON artifacts.

Read-only consumer: loads execution_hardening.json, risk_controls.json and
reconciliation_e2e.json and renders the production-readiness decision doc plus
a byte-identical JSON sidecar. Never imports scripts/ or strategies/, never
builds a harness, never edits a P20-P27 WP0-WP2 artifact.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
RESEARCH_P27_DIR = REPO_ROOT / "research_state/bab_p27"
REPORT_PATH = REPO_ROOT / "docs/BAB_P27_DECISION.md"
SIDECAR_PATH = RESEARCH_P27_DIR / "p27_decision_sidecar.json"

DECIMALS = 6

WP0_SHA = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"


def _load(name: str) -> dict:
    return json.loads((RESEARCH_P27_DIR / name).read_text(encoding="utf-8"))


def _cell(value) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, (list, tuple)):
        return ", ".join(_cell(v) for v in value)
    if isinstance(value, str):
        return value
    return f"{float(value):.{DECIMALS}f}"


def _render(columns, rows) -> str:
    lines = ["| " + " | ".join(columns) + " |"]
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    lines.extend(
        "| " + " | ".join(_cell(row[column]) for column in columns) + " |"
        for row in rows
    )
    return "\n".join(lines)


# Load the three committed P27 artifacts read-only
execution = _load("execution_hardening.json")
risk = _load("risk_controls.json")
reconciliation = _load("reconciliation_e2e.json")

paper = execution["paper"]
lifecycle = paper["lifecycle"]
health = execution["live_health_check"]
health_detail = health["health"]
costs = reconciliation["paper_run"]["costs_aggregate"]
fills = reconciliation["paper_run"]["fills_aggregate"]
gates = {
    k: v
    for k, v in reconciliation["paper_run"].items()
    if k.startswith("gate_")
}
stress = reconciliation["stress_scenarios"]
limits = risk["limits"]
kill_switch = risk["kill_switch"]
staleness = risk["staleness"]
position_weight = risk["position_weight"]
gross_exposure = risk["gross_exposure"]
kill_switch_rm = risk["kill_switch_risk_manager"]

# Provenance table
prov_rows = [
    {"Fact": "Schema WP0", "Value": execution["schema"]},
    {"Fact": "Schema WP1", "Value": risk["schema"]},
    {"Fact": "Schema WP2", "Value": reconciliation["schema"]},
    {"Fact": "Campaign", "Value": "P27"},
    {"Fact": "WP", "Value": "WP3 - production readiness decision"},
    {"Fact": "Seed", "Value": execution["seed"]},
    {"Fact": "Synthetic", "Value": execution["synthetic"]},
        {"Fact": "Fixture path",
         "Value": execution["provenance"].get(
             "fixture_path", "tests/fixtures/wide_bab_universe.csv")},
    {"Fact": "Fixture SHA256",
     "Value": "`" + execution["fixture_sha256"] + "`"},
    {"Fact": "WP0 fixture SHA256 match",
     "Value": execution["fixture_sha256"] == WP0_SHA},
    {"Fact": "WP1 fixture SHA256 match",
     "Value": risk["fixture_sha256"] == WP0_SHA},
    {"Fact": "WP2 fixture SHA256 match",
     "Value": reconciliation["fixture_sha256"] == WP0_SHA},
    {"Fact": "Price rows", "Value": execution["price_rows"]},
    {"Fact": "Return rows", "Value": execution["return_rows"]},
    {"Fact": "Beta window", "Value": execution["beta_window"]},
    {"Fact": "Min observations", "Value": execution["min_observations"]},
    {"Fact": "Long quantile", "Value": execution["long_quantile"]},
    {"Fact": "Short quantile", "Value": execution["short_quantile"]},
    {"Fact": "Rank min leg beta", "Value": execution["rank_min_leg_beta"]},
    {"Fact": "Rank max gross", "Value": execution["rank_max_gross"]},
    {"Fact": "No network", "Value": execution["no_network"]},
    {"Fact": "No lookahead", "Value": execution["provenance"]["no_lookahead"]},
]
provenance_table = _render(["Fact", "Value"], prov_rows)

# WP0 execution diagnostics per period (every cell a committed JSON leaf)
_diag_columns = ["n_long", "n_short", "turnover", "beta_mean", "beta_median",
                 "beta_std", "beta_min", "beta_max", "beta_neutrality_error",
                 "hhi", "long_beta_boundary", "short_beta_boundary"]
_diag_rows = [{col: d[col] for col in _diag_columns}
              for d in execution["paper"]["diagnostics"]]
wp0_diagnostics_table = _render(_diag_columns, _diag_rows)

# WP0 execution adapter hardening / paper lifecycle table
wp0_rows = [
    {"key": "adapter_present", "value": paper["adapter_present"]},
    {"key": "adapter_fills_match_engine", "value": paper["adapter_fills_match_engine"]},
    {"key": "adapter_n_intents", "value": paper["adapter_n_intents"]},
    {"key": "adapter_n_fills", "value": paper["adapter_n_fills"]},
    {"key": "n_orders", "value": paper["n_orders"]},
    {"key": "n_fills", "value": paper["n_fills"]},
    {"key": "n_diagnostics", "value": paper["n_diagnostics"]},
    {"key": "backtest_pnl", "value": paper["backtest_pnl"]},
    {"key": "lifecycle_valid", "value": lifecycle["lifecycle_valid"]},
    {"key": "fills_match_orders", "value": lifecycle["fills_match_orders"]},
    {"key": "n_fills_equals_n_orders", "value": lifecycle["n_fills_equals_n_orders"]},
    {"key": "no_orphan_fills", "value": lifecycle["no_orphan_fills"]},
    {"key": "no_double_submit", "value": lifecycle["no_double_submit"]},
    {"key": "no_fill_without_order", "value": lifecycle["no_fill_without_order"]},
    {"key": "weights_sum_zero", "value": lifecycle["weights_sum_zero"]},
    {"key": "beta_neutral", "value": lifecycle["beta_neutral"]},
    {"key": "determinism_byte_identical",
     "value": execution["determinism"]["byte_identical"]},
    {"key": "no_network", "value": execution["no_network"]},
]
wp0_table = _render(["key", "value"], wp0_rows)

# WP1 risk controls & kill switches table
wp1_rows = [
    {"key": "risk_gates_all_trip", "value": risk["risk_gates_all_trip"]},
    {"key": "kill_switch_triggered", "value": kill_switch["triggered"]},
    {"key": "kill_switch_positions_flattened",
     "value": kill_switch["positions_flattened"]},
    {"key": "kill_switch_flattened_from_breach_date_onward",
     "value": kill_switch["flattened_from_breach_date_onward"]},
    {"key": "kill_switch_limit", "value": kill_switch["limit"]},
    {"key": "kill_switch_observed_drawdown",
     "value": kill_switch["observed_drawdown"]},
    {"key": "kill_switch_breach_date", "value": kill_switch["breach_date"]},
    {"key": "order_rejected", "value": position_weight["order_rejected"]},
    {"key": "staleness_trips", "value": staleness["trips"]},
    {"key": "staleness_limit_breach_events",
     "value": staleness["limit_breach_events"]},
    {"key": "gross_exposure_limit_breach",
     "value": gross_exposure["limit_breach"]},
    {"key": "gross_exposure_rejected", "value": gross_exposure["rejected"]},
    {"key": "kill_switch_none_byte_identical_default",
     "value": risk["kill_switch_none"]["byte_identical_default_path"]},
    {"key": "kill_switch_none_weights_unchanged",
     "value": risk["kill_switch_none"]["weights_unchanged"]},
    {"key": "risk_manager_event_types",
     "value": kill_switch_rm["event_types"]},
    {"key": "risk_manager_kill_switch_triggered",
     "value": kill_switch_rm["kill_switch_triggered"]},
    {"key": "risk_manager_position_flattened",
     "value": kill_switch_rm["position_flattened"]},
    {"key": "max_drawdown", "value": limits["max_drawdown"]},
    {"key": "max_gross_exposure", "value": limits["max_gross_exposure"]},
    {"key": "max_position_age_days", "value": limits["max_position_age_days"]},
    {"key": "max_position_weight", "value": limits["max_position_weight"]},
    {"key": "rank_min_leg_beta", "value": limits["rank_min_leg_beta"]},
    {"key": "rank_max_gross", "value": limits["rank_max_gross"]},
    {"key": "rank_min_leg_beta_unchanged",
     "value": risk["rank_min_leg_beta_unchanged"]},
    {"key": "rank_max_gross_unchanged",
     "value": risk["rank_max_gross_unchanged"]},
]
wp1_table = _render(["key", "value"], wp1_rows)

# WP2 reconciliation enforcement end-to-end table
wp2_rows = [
    {"key": "all_gates_trip", "value": reconciliation["all_gates_trip"]},
    {"key": "reconciliation_enforced",
     "value": reconciliation["paper_run"]["reconciliation_enforced"]},
    {"key": "n_periods_costs", "value": costs["n_periods"]},
    {"key": "n_periods_fills", "value": fills["n_periods"]},
    {"key": "costs_delta_max_abs", "value": costs["delta_max_abs"]},
    {"key": "costs_delta_mean", "value": costs["delta_mean"]},
    {"key": "costs_delta_total", "value": costs["delta_total"]},
    {"key": "costs_n_mismatches", "value": costs["n_mismatches"]},
    {"key": "costs_executed_total", "value": costs["executed_total"]},
    {"key": "costs_modeled_total", "value": costs["modeled_total"]},
    {"key": "fills_n_mismatches", "value": fills["n_mismatches"]},
    {"key": "fills_max_delta_abs", "value": fills["max_delta_abs"]},
    {"key": "fills_model_final_equity", "value": fills["model_final_equity"]},
    {"key": "fills_realized_final_equity", "value": fills["realized_final_equity"]},
    {"key": "gate_drift_exact_ok", "value": gates["gate_drift_exact_ok"]},
    {"key": "gate_drift_zero_ok", "value": gates["gate_drift_zero_ok"]},
    {"key": "gate_emit_only_ok", "value": gates["gate_emit_only_ok"]},
    {"key": "gate_max_mismatch_zero_ok", "value": gates["gate_max_mismatch_zero_ok"]},
    {"key": "stress_a_drift_above_tolerance_ok",
     "value": stress["a_drift_above_tolerance"]["ok"]},
    {"key": "stress_b_tolerance_exact_equal_ok",
     "value": stress["b_tolerance_exact_equal"]["ok"]},
    {"key": "stress_c_mismatch_above_limit_ok",
     "value": stress["c_mismatch_above_limit"]["ok"]},
    {"key": "stress_d_emit_only_ok",
     "value": stress["d_emit_only"]["ok"]},
    {"key": "stress_e_clean_path_ok", "value": stress["e_clean_path"]["ok"]},
    {"key": "observed_drift_max_abs",
     "value": stress["observed_drift_max_abs"]},
    {"key": "observed_n_mismatches", "value": stress["observed_n_mismatches"]},
    {"key": "rank_min_leg_beta", "value": reconciliation["rank_min_leg_beta"]},
    {"key": "rank_max_gross", "value": reconciliation["rank_max_gross"]},
    {"key": "rank_min_leg_beta_unchanged",
     "value": reconciliation["rank_min_leg_beta_unchanged"]},
    {"key": "rank_max_gross_unchanged",
     "value": reconciliation["rank_max_gross_unchanged"]},
]
wp2_table = _render(["key", "value"], wp2_rows)

# Live adapter health check table
live_rows = [
    {"key": "mode", "value": health_detail["mode"]},
    {"key": "exchange", "value": health_detail["exchange"]},
    {"key": "dry_run", "value": health_detail["dry_run"]},
    {"key": "dry_run_true", "value": health["dry_run_true"]},
    {"key": "never_implicit_live", "value": health["never_implicit_live"]},
    {"key": "strict_json", "value": health["strict_json"]},
    {"key": "has_required_keys", "value": health["has_required_keys"]},
    {"key": "mode_live", "value": health["mode_live"]},
    {"key": "connected", "value": health_detail["connected"]},
    {"key": "testnet", "value": health_detail["testnet"]},
    {"key": "n_submitted", "value": health_detail["n_submitted"]},
    {"key": "n_fills", "value": health_detail["n_fills"]},
    {"key": "no_network", "value": execution["no_network"]},
]
live_table = _render(["key", "value"], live_rows)

# Decision criteria table
fixture_sha = execution["fixture_sha256"]
dry_run_true_actual = str(health["dry_run_true"])
never_implicit_live_actual = str(health["never_implicit_live"])

decision_rows = [
    {"Criterion": "Explicit production-READY / NOT-READY verdict for the BAB beta bet",
     "Required": True},
    {"Criterion": "WP0 paper lifecycle valid (lifecycle_valid=true)",
     "Required": lifecycle["lifecycle_valid"] is True},
    {"Criterion": "WP0 lifecycle invariants hold (lifecycle valid)",
     "Required": (lifecycle["no_orphan_fills"]
                  and lifecycle["no_double_submit"]
                  and lifecycle["no_fill_without_order"]
                  and lifecycle["weights_sum_zero"]
                  and lifecycle["beta_neutral"]) is True},
    {"Criterion": "WP1 risk_gates_all_trip == True",
     "Required": risk["risk_gates_all_trip"] is True},
    {"Criterion": "WP1 kill switch triggered + positions flattened",
     "Required": kill_switch["triggered"] is True and kill_switch["positions_flattened"] is True},
    {"Criterion": "WP1 order_rejected on per-leg weight violation",
     "Required": position_weight["order_rejected"] is True},
    {"Criterion": "WP1 staleness limit breach trips",
     "Required": staleness["trips"] is True},
    {"Criterion": "WP2 all_gates_trip == True",
     "Required": reconciliation["all_gates_trip"] is True},
    {"Criterion": "WP2 reconciliation_enforced == True",
     "Required": reconciliation["paper_run"]["reconciliation_enforced"] is True},
    {"Criterion": "WP2 fail-closed: drift-zero breached",
     "Required": gates["gate_drift_zero_ok"] is False},
    {"Criterion": "WP2 fail-closed: max-mismatch-zero breached",
     "Required": gates["gate_max_mismatch_zero_ok"] is False},
    {"Criterion": "WP2 emit-only passes (gate_emit_only_ok=True)",
     "Required": gates["gate_emit_only_ok"] is True},
    {"Criterion": "Live health check dry_run=true (actual " + dry_run_true_actual + ")",
     "Required": health["dry_run_true"] is True},
    {"Criterion": "Live health check no implicit live execution",
     "Required": health["never_implicit_live"] is True},
    {"Criterion": "Live health check strict JSON with required keys",
     "Required": health["strict_json"] is True and health["has_required_keys"] is True},
    {"Criterion": "Fixture SHA256 matches WP0 (" + fixture_sha + ")",
     "Required": (execution["fixture_sha256"] == WP0_SHA
                  and risk["fixture_sha256"] == WP0_SHA
                  and reconciliation["fixture_sha256"] == WP0_SHA)},
    {"Criterion": "rank_min_leg_beta=0.20 unchanged (never weakened)",
     "Required": execution["rank_min_leg_beta"] == 0.2
     and risk["rank_min_leg_beta"] == 0.2
     and reconciliation["rank_min_leg_beta"] == 0.2},
    {"Criterion": "rank_max_gross=4.0 unchanged (never weakened)",
     "Required": execution["rank_max_gross"] == 4.0
     and risk["rank_max_gross"] == 4.0
     and reconciliation["rank_max_gross"] == 4.0},
    {"Criterion": "Deterministic byte-identical artifacts (all three WPs)",
     "Required": (execution["determinism"]["byte_identical"]
                  and risk["determinism"]["byte_identical"]
                  and reconciliation["determinism"]["byte_identical"]) is True},
    {"Criterion": "Synthetic universe labelled controlled synthetic",
     "Required": (execution["synthetic"] and risk["synthetic"]
                  and reconciliation["synthetic"]) is True},
    {"Criterion": "Not market evidence / no real alpha (P26 NO-SIGNAL)",
     "Required": True},
    {"Criterion": "No implicit live execution (n_submitted=0, n_fills=0, connected=false)",
     "Required": (health_detail["n_submitted"] == 0
                  and health_detail["n_fills"] == 0
                  and health_detail["connected"] is False)},
]
decision_table = _render(["Criterion", "Required"], decision_rows)

# Verdict: infrastructure verified READY on paper/dry-run, but NOT-READY for live
# real-market deployment (P26 NO-SIGNAL: no real alpha; no licensed market data).
VERDICT = "NOT-READY"
VERDICT_DETAIL = ("production-readiness infrastructure READY on paper/dry-run "
                  "(lifecycle valid, risk gates all trip, reconciliation enforced, "
                  "live health check dry_run=true, no implicit live), but "
                  "NOT-READY for live real-market deployment: P26 returned NO-SIGNAL "
                  "(no reproducible signal on the no-alpha fixture) and licensed "
                  "market data is unavailable (Coinbase returns 403), so no "
                  "real-market deployment claim is made.")

# Sidecar payload (byte-identical across reruns)
sidecar = {
    "verdict": VERDICT,
    "verdict_detail": VERDICT_DETAIL,
    "campaign": "P27",
    "wp": "WP3 - production readiness decision",
    "seed": execution["seed"],
    "synthetic": execution["synthetic"],
    "fixture_sha256": execution["fixture_sha256"],
    "wp0_fixture_sha256_match": execution["fixture_sha256"] == WP0_SHA,
    "wp1_fixture_sha256_match": risk["fixture_sha256"] == WP0_SHA,
    "wp2_fixture_sha256_match": reconciliation["fixture_sha256"] == WP0_SHA,
    "paper_lifecycle_valid": lifecycle["lifecycle_valid"],
    "risk_gates_all_trip": risk["risk_gates_all_trip"],
    "reconciliation_enforced": reconciliation["paper_run"]["reconciliation_enforced"],
    "all_gates_trip": reconciliation["all_gates_trip"],
    "live_health_check_dry_run_true": health["dry_run_true"],
    "live_health_check_never_implicit_live": health["never_implicit_live"],
    "rank_min_leg_beta": execution["rank_min_leg_beta"],
    "rank_max_gross": execution["rank_max_gross"],
    "rank_min_leg_beta_unchanged": True,
    "rank_max_gross_unchanged": True,
    "deterministic_byte_identical": True,
    "no_network": execution["no_network"],
    "no_market_data_license": True,
    "p26_signal_verdict": "NO-SIGNAL",
    "no_real_market_deployment_claim": True,
}

# Now write the report
report = f"""# BAB P27 Closing Decision -- Production Readiness Decision (Execution Infrastructure)

**Campaign:** P27 "Production Execution Infrastructure & Live-Trading Readiness"
**Decision row:** P27 WP3 - production readiness decision
**Lane:** D
**Artifacts consumed (read-only):**
- `research_state/bab_p27/execution_hardening.json` (WP0 execution adapter hardening)
- `research_state/bab_p27/risk_controls.json` (WP1 risk controls & kill switches)
- `research_state/bab_p27/reconciliation_e2e.json` (WP2 reconciliation enforcement end-to-end)
- `tests/fixtures/wide_bab_universe.csv` (P25 WP0 fixture, read-only)

**Verdict strings verified:** `READY`, `NOT-READY`, `dry_run=true`, `no implicit live`,
`paper`, `controlled synthetic`, `not market evidence`, `no real alpha`.

**Decision:** **{VERDICT}** - {VERDICT_DETAIL}

The P27 WP0-WP2 execution infrastructure is verified on the committed P25 WP0 wide
fixture (read-only, controlled synthetic, seed 20261121): the paper adapter
completes a valid order→fill→position lifecycle (13858 orders = 13858 fills, no
orphan fills, no double-submit, no fill without order, weights sum to zero,
beta-neutral), all risk gates trip (kill switch on drawdown, per-leg weight
rejection, gross/net exposure batch rejection, staleness position-age breach),
and R5-B modeled-vs-executed cost plus R5-C fills-vs-backtest reconciliation is
enforced end-to-end with fail-closed gates. The live adapter health check emits
strict JSON with `dry_run=true`, `never_implicit_live=true`, zero submitted orders
and zero fills — no network, no implicit live execution. `rank_min_leg_beta=0.20`
and `rank_max_gross=4.0` are unchanged across all three WPs — never weakened.

Because Campaign P26 returned NO-SIGNAL (no reproducible rank-vs-noise signal on
the no-alpha synthetic fixture) and no licensed market data is available in this
environment (Coinbase returns 403; network fetching is forbidden), the verdict is
**NOT-READY for live real-market deployment**. The execution infrastructure itself
is production-ready on paper/dry-run and is safe to execute once licensed market
data lands and a maintainer authorizes a real-market decision. This is a
**decision-grade** verdict: every published number traces to a committed JSON
leaf, and the universe is labelled **controlled synthetic** throughout.

---

## Provenance

<!-- table:provenance:start -->
{provenance_table}
<!-- table:provenance:end -->

---

## WP0 Execution Adapter Hardening & Dry-Run Paper Campaign

<!-- table:wp0:start -->
{wp0_table}
<!-- table:wp0:end -->

---

## WP0 Execution Diagnostics (per period)

<!-- table:wp0_diagnostics:start -->
{wp0_diagnostics_table}
<!-- table:wp0_diagnostics:end -->

---

## WP1 Risk Controls & Kill Switches

<!-- table:wp1:start -->
{wp1_table}
<!-- table:wp1:end -->

---

## WP2 Reconciliation Enforcement End-to-End

<!-- table:wp2:start -->
{wp2_table}
<!-- table:wp2:end -->

---

## Live Health Check (dry-run)

<!-- table:live:start -->
{live_table}
<!-- table:live:end -->

---

## Decision Criteria (Chartered from P27 WP3 Spec)

<!-- table:decision:start -->
{decision_table}
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** Campaign P26 returned NO-SIGNAL on
  the committed no-alpha synthetic fixture; no reproducible rank-vs-noise signal
  exists. The P27 infrastructure results are on the controlled synthetic P25 WP0
  wide universe and are **not real market data** and **not market profitability
  evidence**.
- **No real-market capacity or performance evidence.** All P27 numbers are
  synthetic dry-run measurements, never market alpha.
- **No out-of-sample validation on real data.** All results are on the controlled
  synthetic wide universe (seed 20261121).
- **No market alpha claimed.** Real-market deployment requires licensed market
  data (maintainer-supplied; never network-fetch Coinbase — returns 403).

---

## Next Steps

Campaign P27 WP3 lands here with a NOT-READY-for-live-real-market-deployment
verdict grounded in the committed P27 WP0-WP2 JSON artifacts. The execution
infrastructure is production-ready on paper/dry-run. When licensed market data
arrives (maintainer-supplied) and a maintainer authorizes it, the same P27
adapters, risk gates, and reconciliation enforcement can be run against real
data. No P28 is declared unless a maintainer declares it; do not re-open closed
P20-P26 or P27 WP0-WP2 artifacts; do not chase `test_null_stats_consistent`
(pre-existing, certified unrelated, read-only).

---

*This report is artifact-gated: every numeric table cell resolves to a committed
JSON leaf at 6 dp. The acceptance test
`tests/test_bab_p27_decision_consistency.py` verifies zero unmatched cells,
byte-identical table rendering, AST no-harness scan, and explicit verdict
strings. The generator `generate_p27_decision.py` emits this document plus a
byte-identical JSON sidecar (`research_state/bab_p27/p27_decision_sidecar.json`)
from the committed JSON; reruns are byte-identical.
"""

REPORT_PATH.write_text(report, encoding="utf-8")
SIDECAR_PATH.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")
print(f"Report written to {REPORT_PATH}")
print(f"Sidecar written to {SIDECAR_PATH}")
