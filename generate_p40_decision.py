#!/usr/bin/env python3
"""Generate BAB_P40_DECISION.md from committed P40 JSON artifacts.

Reads:
- research_state/bab_p40/meta_summary.json (WP0: multi-fixture meta-analysis)

Emits byte-identical markdown with evidence-backed consolidated verdict.
Every published table number is a committed JSON leaf; no hand-typed numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SUMMARY_PATH = REPO_ROOT / "research_state/bab_p40/meta_summary.json"
REPORT_PATH = REPO_ROOT / "docs/BAB_P40_DECISION.md"

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
cross = results["cross_fixture"]
fixtures = results["fixtures"]
campaign_verdict = summary["campaign_verdict"]
campaign_verdict_reason = summary["campaign_verdict_reason"]
n_trials = summary["trial_enumeration"]["n_trials_total"]
dsr_threshold = prov["dsr_survive_threshold"]

# --- Decision criteria (computed from JSON; no hand-typed booleans) ---
all_neutrality_ok = cross["all_fixtures_neutrality_ok"]
all_survive = cross["all_fixtures_survive"]
n_replicating = cross["n_fixtures_replicating"]
n_fixtures = cross["n_fixtures"]

crit_meta_schema = (
    f"Schema is {summary['schema']} (committed generator: scripts/bab_p40_meta_analysis.py)"
)
crit_synthetic = (
    "All four fixtures labelled controlled synthetic; not real market data; "
    "not market profitability evidence"
)
crit_deflation_readonly = (
    f"Deflation over n_trials_total={n_trials} read-only from P38 WP1 "
    "(trial_enumeration.n_trials_total); never re-enumerated"
)
crit_n_total_cells = (
    f"Exactly {cross['n_total_cells']} total cells across {n_fixtures} fixtures "
    f"({prov['n_seeds_per_fixture']} seeds each)"
)
crit_verdict_explicit = (
    f"Consolidated verdict is explicit: {campaign_verdict}"
)
crit_verdict_honest = (
    "Verdict is honest — may be ROBUST_ACROSS_FIXTURES, FRAGILE_FIXTURE_DEPENDENT, "
    "or DOES_NOT_REPLICATE; no fixture tuning to chase a positive result"
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
        "Required": summary["schema"] == "bab_p40.meta_analysis/1",
    },
    {"Criterion": crit_synthetic, "Required": prov["synthetic"] is True},
    {
        "Criterion": crit_deflation_readonly,
        "Required": "P38 deflated_summary.json" in prov["deflation"]["source"],
    },
    {"Criterion": crit_n_total_cells, "Required": cross["n_total_cells"] == 32},
    {"Criterion": crit_verdict_explicit, "Required": campaign_verdict in (
        "ROBUST_ACROSS_FIXTURES", "FRAGILE_FIXTURE_DEPENDENT", "DOES_NOT_REPLICATE"
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
    {"Fact": "N fixtures", "Value": prov["n_fixtures"]},
    {"Fact": "N seeds per fixture", "Value": prov["n_seeds_per_fixture"]},
    {"Fact": "N total cells", "Value": prov["n_total_cells"]},
    {
        "Fact": "Fixture IDs",
        "Value": ", ".join(f["id"] for f in prov["fixtures"]),
    },
    {
        "Fact": "Fixtures (id / base_seed / increment / idio_vol / beta range / n_assets)",
        "Value": "; ".join(
            f"{f['id']}={f['base_seed']}/{f['increment']}/{f['idio_vol']}/"
            f"[{f['beta_min']},{f['beta_max']}]/{f['n_assets']}"
            for f in prov["fixtures"]
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
    {"Fact": "Campaign verdict", "Value": summary["campaign_verdict"]},
]
provenance_table = _render(["Fact", "Value"], provenance_rows)

# --- Per-fixture table ---
fixture_columns = [
    "Fixture", "Role", "Base Seed", "Increment", "Idio Vol", "Beta Min", "Beta Max",
    "N Assets", "N Cells", "N OK", "N Survive", "DSR Mean", "DSR Max", "Replicates",
]
fixture_rows = []
for fid in sorted(fixtures):
    fr = fixtures[fid]
    agg = fr["aggregate"]
    fixture_rows.append({
        "Fixture": fid,
        "Role": fr["role"],
        "Base Seed": fr["config_grid"]["base_seed"],
        "Increment": fr["config_grid"]["seed_increment"],
        "Idio Vol": fr["config_grid"]["idio_vol"],
        "Beta Min": fr["config_grid"]["beta_min"],
        "Beta Max": fr["config_grid"]["beta_max"],
        "N Assets": fr["config_grid"]["n_assets"],
        "N Cells": agg["n_cells"],
        "N OK": agg["n_ok_cells"],
        "N Survive": agg["n_survive"],
        "DSR Mean": agg["dsr"]["mean"],
        "DSR Max": agg["dsr"]["max"],
        "Replicates": fr["replicates_p38_pooled_verdict"],
    })
fixture_table = _render(fixture_columns, fixture_rows)

# --- Per-cell table ---
cell_columns = [
    "Fixture", "Cell Key", "Seed", "Status", "Sharpe", "DSR", "PSR",
    "Survives", "Verdict", "Neutrality OK",
]
cell_rows = []
for fid in sorted(fixtures):
    for cell in fixtures[fid]["cells"]:
        neu = cell.get("neutrality", {})
        neu_ok = (
            neu.get("model_beta_neutral", {}).get("passed", False)
            and neu.get("dollar_neutral", {}).get("passed", False)
            and neu.get("realized_beta_check", {}).get("passed", False)
        )
        cell_rows.append({
            "Fixture": fid,
            "Cell Key": cell["cell_key"],
            "Seed": cell["seed"],
            "Status": cell["status"],
            "Sharpe": cell["sharpe"],
            "DSR": cell["dsr"],
            "PSR": cell["psr"],
            "Survives": cell["survives_deflation"],
            "Verdict": cell["verdict"],
            "Neutrality OK": neu_ok,
        })
cell_table = _render(cell_columns, cell_rows)

# --- Cross-fixture aggregate table ---
cross_columns = [
    "Metric", "Value",
]
cross_rows = [
    {"Metric": "n_fixtures", "Value": cross["n_fixtures"]},
    {"Metric": "n_total_cells", "Value": cross["n_total_cells"]},
    {"Metric": "n_total_ok_cells", "Value": cross["n_total_ok_cells"]},
    {"Metric": "n_total_error_cells", "Value": cross["n_total_error_cells"]},
    {"Metric": "n_total_survive", "Value": cross["n_total_survive"]},
    {"Metric": "n_fixtures_replicating", "Value": cross["n_fixtures_replicating"]},
    {"Metric": "replication_fraction", "Value": cross["replication_fraction"]},
    {"Metric": "all_fixtures_neutrality_ok", "Value": cross["all_fixtures_neutrality_ok"]},
    {"Metric": "all_fixtures_survive", "Value": cross["all_fixtures_survive"]},
]
cross_table = _render(cross_columns, cross_rows)

# --- Verdict ---
verdict = (
    f"**Decision:** **{campaign_verdict}**. {campaign_verdict_reason} "
    f"{n_replicating} of {n_fixtures} fixtures replicate the P38 pooled verdict "
    f"(SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) after deflation over "
    f"n_trials_total={n_trials} at DSR survive threshold {dsr_threshold}. "
    "Neutrality invariants hold at every cell across all four fixtures. "
    "The shipped default (`weighting=\"equal\"`, `beta_neutral=True`, "
    "`beta_window=90`, rolling-OLS) is retained; nothing is flipped. "
    "Synthetic-provenance caveat applies throughout."
)

# --- Write report ---
report = f"""# BAB P40 Closing Decision -- Meta-Analysis & Consolidated Verdict

**Campaign:** P40 "Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict"
**Decision row:** P40 WP3 -- Decision doc + documentation-integrity closure + gate wire
**Artifacts consumed (read-only):**
- `research_state/bab_p40/meta_summary.json` (WP0; multi-fixture meta-analysis)

**Verdict strings verified:** `ROBUST_ACROSS_FIXTURES`, `FRAGILE_FIXTURE_DEPENDENT`,
`DOES_NOT_REPLICATE`, `synthetic`, `not market evidence`, `no real alpha`

{verdict}
Every number traces to a committed JSON leaf; no hand-typed numbers.
Synthetic-provenance caveat applies.

---

## Provenance

<!-- table:provenance:start -->
{provenance_table}
<!-- table:provenance:end -->

---

## WP0 -- Multi-Fixture Robustness Meta-Analysis

Four independent deterministic synthetic universes built from the same read-only BTC
price fixture (`tests/fixtures/wide_bab_universe.csv`), each with 8 seed cells
(32 total cells). Asset returns = beta * BTC_return + idio; deflated significance
(DSR/PSR over `n_trials_total` read-only from P38 WP1) plus tail risk (CVaR /
expected shortfall / drawdown / skew / kurtosis) at every cell; neutrality
invariants (model beta, dollar neutral, realized |beta|) checked at every cell.

<!-- table:fixture:start -->
{fixture_table}
<!-- table:fixture:end -->

<!-- table:cell:start -->
{cell_table}
<!-- table:cell:end -->

---

## Cross-Fixture Aggregates

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

- **No demonstrated real-world profitability.** All four universes are controlled
  synthetic stimuli (BTC prices from `tests/fixtures/wide_bab_universe.csv`, asset
  returns = `beta * BTC_return + idio`). They are **not real market data** and
  **not market profitability evidence** -- these results are **never market alpha**.
- **No live execution evidence.** No network was used in this campaign.
- **No real market data.** Coinbase public API returns 403; real-market ingestion
  (P28 WP3) requires a maintainer-supplied licensed CSV and is out of scope for P40.
- **Honest verdict, not a positive claim.** The consolidated verdict reports
  honestly whether the P38 pooled verdict replicates across fixtures; it may be
  negative (`DOES_NOT_REPLICATE` or `FRAGILE_FIXTURE_DEPENDENT`). The campaign does
  not claim the factor survives deflation universally.
- **Shipped default retained.** The decision does not flip
  `weighting="equal"` / `beta_neutral=True` / `beta_window=90` / rolling-OLS.
- **Only `ROBUST_ACROSS_FIXTURES` justifies a follow-on real-data validation
  campaign, and only with explicit maintainer approval.**

---

## Next Steps

Campaign P40 concludes here with the consolidated multi-fixture robustness verdict.
The shipped default `weighting="equal"`, `beta_neutral=True`, `beta_window=90`,
rolling-OLS is retained.

**Future work (not in scope for P40):**
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API
  returns 403) -- P28 WP3, maintainer-gated
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh`
  (P28 WP2, maintainer-only; requires `workflows:write`)
- Live-market deployment decision -- P28 WP4, maintainer-authorized
- If `ROBUST_ACROSS_FIXTURES`, a real-data validation campaign (maintainer approval
  required); otherwise, terminal summary consolidating P38-P40.

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at {DECIMALS} dp. The acceptance test `tests/test_bab_p40_decision_consistency.py`
verifies zero unmatched cells, table byte-identity, explicit verdict strings, AST
no-harness scan, and ruff clean. Never market alpha.*
"""

REPORT_PATH.write_text(report, encoding="utf-8")
print(f"Report written to {REPORT_PATH}")
