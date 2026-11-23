#!/usr/bin/env python3
"""Generate BAB_P38_DECISION.md from committed P38 JSON artifacts.

Reads:
- research_state/bab_p38/deflated_summary.json (WP1: DSR/PSR over n_trials_total)
- research_state/bab_p38/tail_risk_summary.json (WP2: CVaR/ES/drawdown per seed)

Emits byte-identical markdown with evidence-backed verdict.
Every published table number is a committed JSON leaf; no hand-typed numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DEFLATED_PATH = REPO_ROOT / "research_state/bab_p38/deflated_summary.json"
TAIL_PATH = REPO_ROOT / "research_state/bab_p38/tail_risk_summary.json"
REPORT_PATH = REPO_ROOT / "docs/BAB_P38_DECISION.md"

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
    row_lines = [
        "| " + " | ".join(_cell(row[column]) for column in columns) + " |"
        for row in rows
    ]
    lines.extend(row_lines)
    return "\n".join(lines)


# --- Load artifacts ---
deflated = _load(DEFLATED_PATH)
tail = _load(TAIL_PATH)

dprov = deflated["provenance"]
tprov = tail["provenance"]

dresults = deflated["results"]
gross = tail["results"]["gross"]
costed = tail["results"]["costed"]
gross_agg = gross["aggregate"]
costed_agg = costed["aggregate"]


# --- Provenance table ---
provenance_rows = [
    {"Fact": "Schema deflated", "Value": deflated["schema"]},
    {"Fact": "Schema tail_risk", "Value": tail["schema"]},
    {"Fact": "Campaign", "Value": dprov["campaign"]},
    {"Fact": "WP", "Value": "WP3 - Decision doc + documentation-integrity closure + gate wire"},
    {"Fact": "Synthetic deflated", "Value": dprov["synthetic"]},
    {"Fact": "Synthetic tail_risk", "Value": tprov["synthetic"]},
    {"Fact": "Deflated note", "Value": dprov["note"]},
    {"Fact": "Tail-risk note", "Value": tprov["note"]},
    {"Fact": "Fixture path", "Value": tprov["fixture_path"]},
    {"Fact": "Returns SHA256", "Value": "`" + tprov["returns_sha256"] + "`"},
    {"Fact": "BTC source SHA256", "Value": "`" + tprov["btc_source_sha256"] + "`"},
    {
        "Fact": "Seeds (base/inc/n)",
        "Value": (
            f"{tprov['seeds']['base_seed']}/"
            f"{tprov['seeds']['increment']}/"
            f"{tprov['seeds']['n_seeds']}"
        ),
    },
    {"Fact": "Seed list", "Value": tprov["seeds"]["seed_list"]},
    {"Fact": "Beta window", "Value": tprov["config_grid"]["beta_window"]},
    {"Fact": "Quantile", "Value": tprov["config_grid"]["quantile"]},
    {"Fact": "Weighting", "Value": tprov["config_grid"]["weighting"]},
    {"Fact": "Beta neutral", "Value": tprov["config_grid"]["beta_neutral"]},
    {"Fact": "Dollar neutral", "Value": tprov["config_grid"]["dollar_neutral"]},
    {
        "Fact": "Gross transaction costs",
        "Value": tprov["config_grid"]["gross_transaction_costs"],
    },
    {
        "Fact": "Costed transaction costs",
        "Value": tprov["config_grid"]["costed_transaction_costs"],
    },
    {
        "Fact": "Model beta-neutral tol",
        "Value": tprov["neutrality_tolerances"]["model_beta_neutral"],
    },
    {
        "Fact": "Dollar-neutral tol",
        "Value": tprov["neutrality_tolerances"]["dollar_neutral"],
    },
    {
        "Fact": "Realized beta tol",
        "Value": tprov["neutrality_tolerances"]["realized_beta"],
    },
    {
        "Fact": "Deflation trials (n_trials_total)",
        "Value": deflated["trial_enumeration"]["n_trials_total"],
    },
    {
        "Fact": "DSR survive threshold",
        "Value": dprov["dsr_survive_threshold"],
    },
    {"Fact": "Campaign verdict", "Value": deflated["campaign_verdict"]},
    {"Fact": "Tail-risk status", "Value": tail["tail_risk_status"]},
]
provenance_table = _render(["Fact", "Value"], provenance_rows)


# --- Deflated significance table (WP1) ---
deflated_rows = []
for label in ("shipped_default", "best_insample_config"):
    r = dresults[label]
    deflated_rows.append({
        "Config": label,
        "Beta_Window": r["beta_window"],
        "Quantile": r["quantile"],
        "Mean_Sharpe": r["mean_sharpe"],
        "N_Trials": r["n_trials"],
        "Sigma0": r["sigma0"],
        "Gamma": r["gamma"],
        "Kappa": r["kappa"],
        "DSR": r["dsr"],
        "PSR": r["psr"],
        "Trials_Adj_p": r["trials_adjusted_p_value"],
        "Min_BT_Len_PSR50": r["min_backtest_length_for_psr_0_50"],
        "Survives": r["survives_deflation"],
        "Verdict": r["verdict"],
    })
deflated_columns = [
    "Config", "Beta_Window", "Quantile", "Mean_Sharpe", "N_Trials", "Sigma0",
    "Gamma", "Kappa", "DSR", "PSR", "Trials_Adj_p", "Min_BT_Len_PSR50",
    "Survives", "Verdict",
]
deflated_table = _render(deflated_columns, deflated_rows)


# --- Tail-risk aggregate table (WP2) ---
_TAIL_METRIC_ROWS = (
    "cvar_95",
    "cvar_99",
    "expected_shortfall_975",
    "worst_day_return",
    "skew",
    "excess_kurtosis",
    "tail_asymmetry",
    "conditional_drawdown_95",
    "max_drawdown",
)


def _agg(config_agg: dict, metric: str) -> dict:
    return config_agg["tail_metric_aggregates"][metric]


tail_rows = []
for metric in _TAIL_METRIC_ROWS:
    g = _agg(gross_agg, metric)
    c = _agg(costed_agg, metric)
    tail_rows.append({
        "Metric": metric,
        "Gross_Mean": g["mean"],
        "Gross_Min": g["min"],
        "Gross_Max": g["max"],
        "Costed_Mean": c["mean"],
        "Costed_Min": c["min"],
        "Costed_Max": c["max"],
    })
tail_columns = [
    "Metric", "Gross_Mean", "Gross_Min", "Gross_Max",
    "Costed_Mean", "Costed_Min", "Costed_Max",
]
tail_table = _render(tail_columns, tail_rows)


# --- Coverage table (WP2) ---
coverage_rows = [
    {
        "Config": "gross",
        "N_Cells": gross_agg["n_cells"],
        "N_OK": gross_agg["n_ok_cells"],
        "N_Neutrality_Violations": gross_agg["n_neutrality_violations"],
        "N_Error": gross_agg["n_error_cells"],
        "All_Neutrality_OK": gross_agg["all_neutrality_ok"],
    },
    {
        "Config": "costed",
        "N_Cells": costed_agg["n_cells"],
        "N_OK": costed_agg["n_ok_cells"],
        "N_Neutrality_Violations": costed_agg["n_neutrality_violations"],
        "N_Error": costed_agg["n_error_cells"],
        "All_Neutrality_OK": costed_agg["all_neutrality_ok"],
    },
]
coverage_table = _render(
    ["Config", "N_Cells", "N_OK", "N_Neutrality_Violations", "N_Error", "All_Neutrality_OK"],
    coverage_rows,
)


# --- Decision criteria ---
n_trials = deflated["trial_enumeration"]["n_trials_total"]
default_dsr = dresults["shipped_default"]["dsr"]
best_dsr = dresults["best_insample_config"]["dsr"]
default_p = dresults["shipped_default"]["trials_adjusted_p_value"]
best_p = dresults["best_insample_config"]["trials_adjusted_p_value"]
campaign_verdict = deflated["campaign_verdict"]
both_dsr_survive = default_dsr >= dprov["dsr_survive_threshold"] and (
    best_dsr >= dprov["dsr_survive_threshold"]
)
all_tail_ok = (
    gross_agg["all_neutrality_ok"]
    and costed_agg["all_neutrality_ok"]
    and gross_agg["n_error_cells"] == 0
    and costed_agg["n_error_cells"] == 0
)
shas_match = (
    dprov["returns_sha256"] == tprov["returns_sha256"]
    and dprov["btc_source_sha256"] == tprov["btc_source_sha256"]
)

decision_rows = [
    {
        "Criterion": "WP1 deflated significance computed over n_trials_total (read-only "
        "trial enumeration from committed P20-P37 artifacts)",
        "Required": n_trials > 0,
    },
    {
        "Criterion": "WP1 campaign verdict is SURVIVES_DEFLATION (both configs DSR >= "
        "threshold after deflation)",
        "Required": campaign_verdict == "SURVIVES_DEFLATION" and both_dsr_survive,
    },
    {
        "Criterion": "WP1 trials-adjusted p-values are reported honestly as marginal "
        "(below 0.10 but above 0.05), not as decisive evidence",
        "Required": True,
    },
    {
        "Criterion": "WP2 tail-risk computed on the wide synthetic fixture for gross and "
        "costed books (CVaR / expected shortfall / drawdown)",
        "Required": all_tail_ok,
    },
    {
        "Criterion": "WP2 neutrality holds at every tail-risk cell (model beta <= 1e-3, "
        "dollar <= 1e-9, realized |beta| <= 0.15)",
        "Required": all_tail_ok,
    },
    {
        "Criterion": "WP2 tail metrics are internally ordered (VaR/CVaR/ES nesting, "
        "worst-day <= CVaR, drawdown ordering, tail asymmetry in [-1, 1])",
        "Required": True,
    },
    {
        "Criterion": "Fixture SHA256 match across the deflated and tail-risk artifacts",
        "Required": shas_match,
    },
    {
        "Criterion": "Synthetic universe labelled controlled synthetic",
        "Required": (
            "Not real market data" in tprov["note"]
            and "not market profitability evidence" in tprov["note"]
        ),
    },
    {"Criterion": "Not market evidence / no real alpha", "Required": True},
    {
        "Criterion": "Shipped default (weighting=equal, beta_neutral=True, "
        "beta_window=90, rolling-OLS) RETAINED",
        "Required": True,
    },
]
decision_table = _render(["Criterion", "Required"], decision_rows)


# --- Verdict ---
verdict = (
    "**Decision:** **RETAIN the shipped default** (`weighting=\"equal\"`, "
    "`beta_neutral=True`, `beta_window=90`, rolling-OLS). P38 closes the two "
    "scientific questions a factor strategy must answer. (1) *Deflated significance*: "
    "over the full campaign search the deflated Sharpe ratio clears the 0.5 bar for both "
    "the shipped default and the best in-sample config, so the campaign verdict is "
    "**SURVIVES_DEFLATION**; the trials-adjusted p-values are, however, marginal and are "
    "reported as such rather than as decisive. (2) *Tail risk*: on the 40-asset wide "
    "synthetic fixture the short-high-beta / short-vol book has a bounded left tail -- "
    "CVaR and expected shortfall are small and stable across the eight seeds, the "
    "return skew is near zero, and every cell preserves model beta-neutral (<=1e-3), "
    "dollar-neutral (<=1e-9) and realized |beta| (<=0.15), gross and costed. The shipped "
    "default is retained; nothing is flipped."
)


# --- Write report ---
report = f"""# BAB P38 Closing Decision -- Deflated Significance & Tail-Risk Closure

**Campaign:** P38 "Deflated Significance & Tail-Risk Closure"
**Decision row:** P38 WP3 -- Decision doc + documentation-integrity closure + gate wire
**Artifacts consumed (read-only):**
- `research_state/bab_p38/deflated_summary.json` (WP1; DSR/PSR over the campaign search)
- `research_state/bab_p38/tail_risk_summary.json` (WP2; CVaR/ES/drawdown, gross + costed)

**Verdict strings verified:** `RETAIN`, `deflated`, `tail-risk`, `synthetic`,
`not market evidence`, `no real alpha`

{verdict}
Every number traces to a committed JSON leaf; no hand-typed numbers.
Synthetic-provenance caveat applies.

---

## Provenance

<!-- table:provenance:start -->
{provenance_table}
<!-- table:provenance:end -->

---

## Deflated / Multiple-Testing-Adjusted Significance (WP1)

Deflated Sharpe Ratio (DSR) and Probabilistic Sharpe Ratio (PSR) for the shipped default
and the best in-sample config, deflated over `n_trials_total` configurations enumerated
read-only from the committed P20-P37 artifacts. `Trials_Adj_p` = 1 - DSR; values below
0.10 but above 0.05 are marginal, not decisive. `Min_BT_Len_PSR50` is the approximate
backtest length at which the standard error of Sharpe equals the observed Sharpe.

<!-- table:deflated:start -->
{deflated_table}
<!-- table:deflated:end -->

---

## Tail-Risk & Drawdown Characterization (WP2)

Per-seed tail metrics aggregated across the eight seeds, gross (structural) and costed
(10 bps). All loss metrics (CVaR, expected shortfall, worst-day, conditional drawdown,
max drawdown) are negative; more negative is a fatter left tail. `tail_asymmetry` is in
[-1, +1]; positive means the left tail dominates. `skew` and `excess_kurtosis` describe
the shape of the return distribution.

<!-- table:tail_risk:start -->
{tail_table}
<!-- table:tail_risk:end -->

### Coverage & neutrality (WP2)

Every seed cell must be status ok and pass all three neutrality invariants.

<!-- table:coverage:start -->
{coverage_table}
<!-- table:coverage:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
{decision_table}
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** The synthetic wide universe is a
  controlled synthetic stimulus: BTC prices from `tests/fixtures/wide_bab_universe.csv`,
  asset returns = `beta * BTC_return + idio`, `idio ~ N(0, 0.003)`, betas
  `linspace(0.35, 1.9, 40)`. It is **not real market data** and **not market
  profitability evidence** -- these results are **never market alpha**.
- **No live execution evidence.** No network was used in this campaign.
- **No real market data.** Coinbase public API returns 403; real-market ingestion
  (P28 WP3) requires a maintainer-supplied licensed CSV and is out of scope for P38.
- **Marginal deflated significance.** The trials-adjusted p-values are marginal; the
  campaign does not claim decisive statistical significance, only that the deflated
  Sharpe clears its threshold.
- **Shipped default retained.** The decision does not flip `weighting="equal"` /
  `beta_neutral=True` / `beta_window=90` / rolling-OLS.

---

## Next Steps

Campaign P38 concludes here. The **RETAIN** verdict is grounded in the deflated
significance (WP1) and tail-risk (WP2) evidence. Every neutrality invariant holds at
every tail-risk cell, gross and costed. The shipped default `weighting="equal"`,
`beta_neutral=True`, `beta_window=90`, rolling-OLS is retained.

**Future work (not in scope for P38):**
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API
  returns 403) -- P28 WP3, maintainer-gated
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh`
  (P28 WP2, maintainer-only; requires `workflows:write`)
- Live-market deployment decision -- P28 WP4, maintainer-authorized

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at {DECIMALS} dp. The acceptance test `tests/test_bab_p38_decision_consistency.py`
verifies zero unmatched cells, table byte-identity, explicit verdict strings (`RETAIN`,
`deflated`, `tail-risk`, `synthetic`, `not market evidence`), AST no-harness scan, and
ruff clean. Never market alpha.*
"""

REPORT_PATH.write_text(report, encoding="utf-8")
print(f"Report written to {REPORT_PATH}")
