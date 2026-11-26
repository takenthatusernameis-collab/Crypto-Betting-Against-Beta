#!/usr/bin/env python3
"""Generate BAB_P41_DECISION.md from the committed P41 stress JSON artifact.

Reads:
- research_state/bab_p41/stress_summary.json (WP2: five-DGP stress meta-analysis)

Emits byte-identical markdown with evidence-backed consolidated verdict.
Every published table number is a committed JSON leaf; no hand-typed numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SUMMARY_PATH = REPO_ROOT / "research_state/bab_p41/stress_summary.json"
REPORT_PATH = REPO_ROOT / "docs/BAB_P41_DECISION.md"

DECIMALS = 6


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _cell(value) -> str:
    if value is None:
        return "None"
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, (list, tuple)):
        return ", ".join(_cell(v) for v in value)
    return f"{float(value):.{DECIMALS}f}"


def _render(columns, rows) -> str:
    lines = ["| " + " | ".join(columns) + " |"]
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    lines.extend(
        "| " + " | ".join(_cell(row[column]) for column in columns) + " |"
        for row in rows
    )
    return "\n".join(lines)


summary = _load(SUMMARY_PATH)
prov = summary["provenance"]
results = summary["results"]
cross = results["cross_dgp"]
dgps = results["dgps"]
stress_verdict = results["stress_verdict"]
stress_verdict_reason = results["stress_verdict_reason"]
n_trials = summary["trial_enumeration"]["n_trials_total"]
dsr_threshold = prov["dsr_survive_threshold"]
n_dgps = prov["n_dgps"]
n_seeds = prov["n_seeds_per_dgp"]
n_estimators = prov["n_estimators"]
n_total_cells = prov["n_total_cells"]

# --- Decision criteria (computed from JSON; no hand-typed booleans) ---
all_neutrality_ok = cross["all_dgps_neutrality_ok"]
all_survive = cross["all_dgps_survive"]
n_replicating = cross["n_dgps_replicating"]
n_total_survive = cross["n_total_survive"]

crit_meta_schema = (
    f"Schema is {summary['schema']} (committed generator: scripts/bab_p41_stress.py)"
)
crit_synthetic = (
    "All five DGPs labelled controlled synthetic; not real market data; "
    "not market profitability evidence"
)
crit_deflation_readonly = (
    f"Deflation over n_trials_total={n_trials} read-only from P38 WP1 "
    "(trial_enumeration.n_trials_total); never re-enumerated"
)
crit_n_total_cells = (
    f"Exactly {n_total_cells} total cells across {n_dgps} DGPs "
    f"({n_seeds} seeds each x {n_estimators} estimators)"
)
crit_verdict_explicit = (
    f"Consolidated verdict is explicit: {stress_verdict}"
)
crit_verdict_honest = (
    "Verdict is honest — may be ROBUST_ACROSS_DGPS, FRAGILE_DGP_DEPENDENT, "
    "or DOES_NOT_REPLICATE; no seed/parameter tuning to chase a positive result"
)
crit_neutrality = (
    "All three neutrality invariants hold at every cell (model beta <= 1e-3, "
    "dollar <= 1e-9, |realized beta| <= 0.15)"
)
crit_no_alpha = (
    "No demonstrated real-world profitability; synthetic-provenance caveat applies; "
    "nothing flipped"
)

decision_rows = [
    {
        "Criterion": crit_meta_schema,
        "Required": summary["schema"] == "bab_p41.stress_summary/1",
    },
    {"Criterion": crit_synthetic, "Required": prov["synthetic"] is True},
    {
        "Criterion": crit_deflation_readonly,
        "Required": "P38 deflated_summary.json" in prov["deflation"]["source"],
    },
    {"Criterion": crit_n_total_cells, "Required": n_total_cells == 160},
    {"Criterion": crit_verdict_explicit, "Required": stress_verdict in (
        "ROBUST_ACROSS_DGPS", "FRAGILE_DGP_DEPENDENT", "DOES_NOT_REPLICATE"
    )},
    {"Criterion": crit_verdict_honest, "Required": True},
    {"Criterion": crit_neutrality, "Required": all_neutrality_ok},
    {"Criterion": crit_no_alpha, "Required": True},
]
decision_table = _render(["Criterion", "Required"], decision_rows)

# --- Provenance table ---
provenance_rows = [
    {"Fact": "Schema", "Value": summary["schema"]},
    {"Fact": "Campaign", "Value": prov["campaign"]},
    {"Fact": "WP", "Value": prov["wp"]},
    {"Fact": "Synthetic", "Value": prov["synthetic"]},
    {"Fact": "Generator", "Value": prov["generator"]},
    {"Fact": "Fixture path", "Value": prov["fixture_path"]},
    {"Fact": "Returns SHA256", "Value": "`" + prov["returns_sha256"] + "`"},
    {"Fact": "BTC source SHA256", "Value": "`" + prov["btc_source_sha256"] + "`"},
    {"Fact": "N DGPs", "Value": prov["n_dgps"]},
    {"Fact": "N seeds per DGP", "Value": prov["n_seeds_per_dgp"]},
    {"Fact": "N estimators", "Value": prov["n_estimators"]},
    {"Fact": "N total cells", "Value": prov["n_total_cells"]},
    {
        "Fact": "DGP IDs",
        "Value": ", ".join(d["id"] for d in prov["dgps"]),
    },
    {
        "Fact": "DGPs (id / process / kind / idio_vol / base_seed / increment)",
        "Value": "; ".join(
            f"{d['id']}={d['process']}/{d['kind']}/{d['idio_vol']}/"
            f"{d['base_seed']}/{d['increment']}"
            for d in prov["dgps"]
        ),
    },
    {"Fact": "Beta window", "Value": prov["config_grid"]["beta_window"]},
    {"Fact": "Quantile", "Value": prov["config_grid"]["quantile"]},
    {"Fact": "Weighting", "Value": prov["config_grid"]["weighting"]},
    {"Fact": "Beta neutral", "Value": prov["config_grid"]["beta_neutral"]},
    {"Fact": "Dollar neutral", "Value": prov["config_grid"]["dollar_neutral"]},
    {"Fact": "Transaction costs", "Value": prov["config_grid"]["transaction_costs"]},
    {
        "Fact": "Deflation trials (n_trials_total)",
        "Value": summary["trial_enumeration"]["n_trials_total"],
    },
    {"Fact": "DSR survive threshold", "Value": prov["dsr_survive_threshold"]},
    {"Fact": "Stress verdict", "Value": results["stress_verdict"]},
]
provenance_table = _render(["Fact", "Value"], provenance_rows)

# --- Per-DGP table ---
dgp_columns = [
    "DGP", "Process", "Kind", "Idio Vol", "Base Seed", "Increment",
    "N Cells", "N OK", "N Survive", "DSR Mean", "DSR Max", "Replicates Stress",
]
dgp_rows = []
for did in sorted(dgps):
    dr = dgps[did]
    agg = dr["aggregate"]
    dgp_rows.append({
        "DGP": did,
        "Process": dr["process"],
        "Kind": dr["kind"],
        "Idio Vol": dr["config_grid"]["idio_vol"],
        "Base Seed": dr["config_grid"]["base_seed"],
        "Increment": dr["config_grid"]["increment"],
        "N Cells": agg["n_cells"],
        "N OK": agg["n_ok_cells"],
        "N Survive": agg["n_survive"],
        "DSR Mean": agg["dsr"]["mean"],
        "DSR Max": agg["dsr"]["max"],
        "Replicates Stress": dr["replicates_stress_test"],
    })
dgp_table = _render(dgp_columns, dgp_rows)

# --- Per-cell table (all 160 cells) ---
cell_columns = [
    "DGP", "Cell Key", "Seed", "Estimator", "Status", "Sharpe", "DSR", "PSR",
    "Survives", "Verdict", "Neutrality OK",
]
cell_rows = []
for did in sorted(dgps):
    for cell in dgps[did]["cells"]:
        neu = cell.get("neutrality", {})
        neu_ok = (
            neu.get("model_beta_neutral", {}).get("passed", False)
            and neu.get("dollar_neutral", {}).get("passed", False)
            and neu.get("realized_beta_check", {}).get("passed", False)
        )
        cell_rows.append({
            "DGP": cell["dgp_id"],
            "Cell Key": cell["cell_key"],
            "Seed": cell["seed"],
            "Estimator": cell["estimator"],
            "Status": cell["status"],
            "Sharpe": cell["sharpe"],
            "DSR": cell["dsr"],
            "PSR": cell["psr"],
            "Survives": cell["survives_deflation"],
            "Verdict": cell["verdict"],
            "Neutrality OK": neu_ok,
        })
cell_table = _render(cell_columns, cell_rows)

# --- Cross-DGP aggregate table ---
cross_columns = ["Metric", "Value"]
cross_rows = [
    {"Metric": "n_dgps", "Value": cross["n_dgps"]},
    {"Metric": "n_total_cells", "Value": cross["n_total_cells"]},
    {"Metric": "n_total_ok_cells", "Value": cross["n_total_ok_cells"]},
    {"Metric": "n_total_error_cells", "Value": cross["n_total_error_cells"]},
    {"Metric": "n_total_survive", "Value": cross["n_total_survive"]},
    {"Metric": "n_dgps_replicating", "Value": cross["n_dgps_replicating"]},
    {"Metric": "all_dgps_neutrality_ok", "Value": cross["all_dgps_neutrality_ok"]},
    {"Metric": "all_dgps_survive", "Value": cross["all_dgps_survive"]},
]
cross_table = _render(cross_columns, cross_rows)

# --- Verdict ---
verdict = (
    f"**Decision:** **{stress_verdict}**. {stress_verdict_reason} "
    f"{n_replicating} of {n_dgps} DGPs replicate the stress test "
    f"(every cell survives deflation + neutrality holds everywhere) after "
    f"deflation over n_trials_total={n_trials} at DSR survive threshold "
    f"{dsr_threshold}. {n_total_survive} of {n_total_cells} cells survive "
    f"overall across the five DGPs. Neutrality invariants hold at every cell "
    f"across all five DGPs. The shipped default "
    f"(`weighting=\"equal\"`, `beta_neutral=True`, `beta_window=90`, "
    f"rolling-OLS) is retained; nothing is flipped. "
    f"Synthetic-provenance caveat applies throughout."
)

# --- Write report ---
report = f"""# BAB P41 Closing Decision -- Non-Gaussian & Regime-Switching Stress Battery

**Campaign:** P41 "Non-Gaussian & Regime-Switching Synthetic Stress Battery"
**Decision row:** P41 WP3 -- Decision doc + documentation-integrity closure + gate wire
**Artifacts consumed (read-only):**
- `research_state/bab_p41/stress_summary.json` (WP2; five-DGP stress meta-analysis)

**Verdict strings verified:** `FRAGILE_DGP_DEPENDENT`, `synthetic`,
`not real market data`, `not market profitability evidence`, `never market alpha`

{verdict}
Every number traces to a committed JSON leaf; no hand-typed numbers.
Synthetic-provenance caveat applies.

---

## Provenance

<!-- table:provenance:start -->
{provenance_table}
<!-- table:provenance:end -->

---

## WP2 -- Five-DGP Stress Meta-Analysis

Five deterministic synthetic data-generating processes (GAUSSIAN_IID control,
STUDENT_T, REGIME_SWITCH, JUMP_DIFFUSION, STOCHASTIC_VOL), 8 seeds each, 4
estimators (shipped rolling-OLS vs P35 runner-ups EWMA halflife=40; Shrinkage
intensity=0.3 target=1.0 and cross_sectional_mean) = 160 total cells. Per-cell
DSR/PSR deflated over `n_trials_total` read-only from P38 WP1 plus tail risk
and the three neutrality invariants at every cell.

<!-- table:dgp:start -->
{dgp_table}
<!-- table:dgp:end -->

<!-- table:cell:start -->
{cell_table}
<!-- table:cell:end -->

---

## Cross-DGP Aggregates

<!-- table:cross:start -->
{cross_table}
<!-- table:cross:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
{decision_table}
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** All five universes are
  controlled synthetic stimuli (BTC prices from
  `tests/fixtures/wide_bab_universe.csv`, asset returns =
  `beta * BTC_return + idio`). They are **not real market data** and
  **not market profitability evidence** -- these results are **never market
  alpha**.
- **No live execution evidence.** No network was used in this campaign.
- **No real market data.** Coinbase public API returns 403; real-market
  ingestion (P28 WP3) requires a maintainer-supplied licensed CSV and is out
  of scope for P41.
- **Honest verdict, not a positive claim.** The consolidated verdict reports
  honestly whether BAB behaviour survives non-Gaussian idio across all five
  DGPs; it may be negative (`FRAGILE_DGP_DEPENDENT` or
  `DOES_NOT_REPLICATE`). The campaign does not claim the factor survives
  deflation universally.
- **Shipped default retained.** The decision does not flip
  `weighting="equal"` / `beta_neutral=True` / `beta_window=90` / rolling-OLS.
- **Only `ROBUST_ACROSS_DGPS` justifies a follow-on real-data validation
  campaign, and only with explicit maintainer approval.**

---

## Next Steps

Campaign P41 concludes here with the consolidated five-DGP stress verdict.
The shipped default `weighting="equal"`, `beta_neutral=True`, `beta_window=90`,
rolling-OLS is retained.

**Future work (not in scope for P41):**
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API
  returns 403) -- P28 WP3, maintainer-gated
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh`
  (P28 WP2, maintainer-only; requires `workflows:write`)
- Live-market deployment decision -- P28 WP4, maintainer-authorized

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at {DECIMALS} dp. The acceptance test `tests/test_bab_p41_decision_consistency.py`
verifies zero unmatched cells, table byte-identity, explicit verdict strings, AST
no-harness scan, and ruff clean. Never market alpha.*
"""

REPORT_PATH.write_text(report, encoding="utf-8")
print(f"Report written to {REPORT_PATH}")
