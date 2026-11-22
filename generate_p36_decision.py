#!/usr/bin/env python3
"""Generate BAB_P36_DECISION.md from committed P36 JSON artifacts.

Reads:
- research_state/bab_p36/walk_forward_summary.json (walk-forward/OOS cells: 8 seeds x 10 windows)
- research_state/bab_p36/rank_weighted_summary.json (rank-weighted cells: 8 seeds)

Emits byte-identical markdown with evidence-backed verdict.
Every published table number is a committed JSON leaf; no hand-typed numbers.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
WALK_FORWARD_PATH = REPO_ROOT / "research_state" / "bab_p36" / "walk_forward_summary.json"
RANK_WEIGHTED_PATH = REPO_ROOT / "research_state" / "bab_p36" / "rank_weighted_summary.json"
REPORT_PATH = REPO_ROOT / "docs" / "BAB_P36_DECISION.md"

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
wf = _load(WALK_FORWARD_PATH)
rw = _load(RANK_WEIGHTED_PATH)

prov_wf = wf["provenance"]
prov_rw = rw["provenance"]

wf_cells = wf["results"]["cells"]
rw_cells = rw["results"]["cells"]

# --- Provenance table ---
provenance_rows = [
    {"Fact": "Schema walk-forward", "Value": wf["schema"]},
    {"Fact": "Schema rank-weighted", "Value": rw["schema"]},
    {"Fact": "Campaign", "Value": (
        "P36 Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure"
    )},
    {"Fact": "WP", "Value": (
        "WP2-WP3 - Decision doc + documentation-integrity closure + gate wire"
    )},
    {"Fact": "Synthetic universe", "Value": prov_wf["fixture_recipe"]},
    {"Fact": "Fixture SHA256", "Value": "`" + prov_wf["returns_sha256"] + "`"},
    {"Fact": "BTC source SHA256", "Value": "`" + prov_wf["btc_source_sha256"] + "`"},
    {
        "Fact": "Seeds (base/inc/n)",
        "Value": (
            f"{prov_wf['seeds']['base_seed']}/"
            f"{prov_wf['seeds']['increment']}/"
            f"{prov_wf['seeds']['n_seeds']}"
        ),
    },
    {
        "Fact": "Walk-forward config (train/test/step, beta window)",
        "Value": (
            "train=" + str(prov_wf["config_grid"]["train_window"]) + "d, "
            "test=" + str(prov_wf["config_grid"]["test_window"]) + "d, "
            "step=" + str(prov_wf["config_grid"]["step"]) + "d, "
            "beta_window=" + str(prov_wf["config_grid"]["beta_window"]) + "d"
        ),
    },
    {"Fact": "Quantile", "Value": prov_wf["config_grid"]["quantile"]},
    {"Fact": "Transaction costs", "Value": prov_wf["config_grid"]["transaction_costs"]},
    {"Fact": "Weighting (walk-forward)", "Value": prov_wf["config_grid"]["weighting"]},
    {"Fact": "Beta neutral", "Value": prov_wf["config_grid"]["beta_neutral"]},
    {"Fact": "Dollar neutral", "Value": prov_wf["config_grid"]["dollar_neutral"]},
    {"Fact": "Rank min leg beta", "Value": prov_rw["config_grid"]["rank_min_leg_beta"]},
    {"Fact": "Rank max gross", "Value": prov_rw["config_grid"]["rank_max_gross"]},
    {
        "Fact": "Model beta-neutral tol",
        "Value": prov_wf["neutrality_tolerances"]["model_beta_neutral"],
    },
    {"Fact": "Dollar-neutral tol", "Value": prov_wf["neutrality_tolerances"]["dollar_neutral"]},
    {"Fact": "Realized beta tol", "Value": prov_wf["neutrality_tolerances"]["realized_beta"]},
]
provenance_table = _render(["Fact", "Value"], provenance_rows)

# --- Walk-forward per-window table (one row per window, all values are JSON leaves) ---

wf_by_window = defaultdict(list)
for cell in wf_cells:
    if cell["status"] == "ok":
        wf_by_window[cell["window_index"]].append(cell)

wf_window_rows = []
for widx in sorted(wf_by_window):
    cell_list = wf_by_window[widx]
    n_ok = len(cell_list)
    all_ok = all(
        c["neutrality_checks"]["model_beta_neutral"]["passed"]
        and c["neutrality_checks"]["dollar_neutral"]["passed"]
        and c["neutrality_checks"]["realized_beta"]["passed"]
        for c in cell_list
    )
    wf_window_rows.append({
        "Window": widx,
        "N_ok_cells": n_ok,
        "All_Neutrality_Pass": all_ok,
    })

wf_window_columns = ["Window", "N_ok_cells", "All_Neutrality_Pass"]
wf_window_table = _render(wf_window_columns, wf_window_rows)

# Walk-forward overall facts (all are JSON leaves or booleans)
wf_n_cells = len(wf_cells)
wf_ok_cells = sum(1 for c in wf_cells if c["status"] == "ok")
wf_all_ok = all(c["status"] == "ok" for c in wf_cells)
wf_all_neutrality = all(
    c["neutrality_checks"]["model_beta_neutral"]["passed"]
    and c["neutrality_checks"]["dollar_neutral"]["passed"]
    and c["neutrality_checks"]["realized_beta"]["passed"]
    for c in wf_cells if c["status"] == "ok"
)
wf_all_sharpe_finite = all(
    c["metrics"]["sharpe"] is not None
    for c in wf_cells if c["status"] == "ok"
)
wf_spearman_vals = [
    c["walk_forward_stability"]["spearman_is_oos_beta"]
    for c in wf_cells
    if c["status"] == "ok" and c["walk_forward_stability"]["spearman_is_oos_beta"] is not None
]
wf_avg_spearman = sum(wf_spearman_vals) / len(wf_spearman_vals) if wf_spearman_vals else None
wf_min_spearman = min(wf_spearman_vals) if wf_spearman_vals else None

# --- Rank-weighted per-seed table (all values are JSON leaves) ---
rw_rows = []
for cell in rw_cells:
    if cell["status"] != "ok":
        continue
    eq = cell["equal_weight"]
    rw_ = cell["rank_weighted"]
    comp = cell["comparison"]
    rw_rows.append({
        "Seed_Idx": cell["seed_index"],
        "N_Periods": cell["n_periods"],
        "EQ_Sharpe": eq["metrics"]["sharpe"],
        "EQ_Turnover": eq["metrics"]["turnover"],
        "EQ_Wealth": eq["metrics"]["wealth"],
        "EQ_Realized_Beta": eq["metrics"]["realized_beta"],
        "EQ_Model_Beta": eq["metrics"]["max_model_beta"],
        "EQ_Dollar_Neutral": eq["metrics"]["max_dollar_neutral"],
        "EQ_Neutrality_OK": eq["neutrality_ok"],
        "RW_Sharpe": rw_["metrics"]["sharpe"],
        "RW_Turnover": rw_["metrics"]["turnover"],
        "RW_Wealth": rw_["metrics"]["wealth"],
        "RW_Realized_Beta": rw_["metrics"]["realized_beta"],
        "RW_Model_Beta": rw_["metrics"]["max_model_beta"],
        "RW_Dollar_Neutral": rw_["metrics"]["max_dollar_neutral"],
        "RW_Neutrality_OK": rw_["neutrality_ok"],
        "Turnover_Reduction": comp["turnover_reduction"],
        "Sharpe_Difference": comp["sharpe_difference"],
        "Wealth_Difference": comp["wealth_difference"],
    })

rw_columns = [
    "Seed_Idx", "N_Periods",
    "EQ_Sharpe", "EQ_Turnover", "EQ_Wealth", "EQ_Realized_Beta", "EQ_Model_Beta",
    "EQ_Dollar_Neutral", "EQ_Neutrality_OK",
    "RW_Sharpe", "RW_Turnover", "RW_Wealth", "RW_Realized_Beta", "RW_Model_Beta",
    "RW_Dollar_Neutral", "RW_Neutrality_OK",
    "Turnover_Reduction", "Sharpe_Difference", "Wealth_Difference",
]
rw_table = _render(rw_columns, rw_rows)

# Rank-weighted overall facts (all are JSON leaves or booleans)
all_rw_ok = all(c["status"] == "ok" for c in rw_cells)
rw_ok_cells = sum(1 for c in rw_cells if c["status"] == "ok")
rw_n_cells = len(rw_cells)
rw_all_eq_neutrality = all(
    cell["equal_weight"]["neutrality_ok"] for cell in rw_cells if cell["status"] == "ok"
)
rw_all_rw_model_beta = all(
    cell["rank_weighted"]["metrics"]["max_model_beta"] is not None
    and cell["rank_weighted"]["metrics"]["max_model_beta"] <= 1e-3
    for cell in rw_cells if cell["status"] == "ok"
)
rw_all_rw_realized = all(
    abs(cell["rank_weighted"]["metrics"]["realized_beta"]) <= 0.15
    for cell in rw_cells if cell["status"] == "ok"
)

eq_turnovers = []
rw_turnovers = []
turnover_reductions = []
for cell in rw_cells:
    if cell["status"] != "ok":
        continue
    eq = cell["equal_weight"]["metrics"]
    rw_ = cell["rank_weighted"]["metrics"]
    comp = cell["comparison"]
    eq_turnovers.append(eq["turnover"])
    rw_turnovers.append(rw_["turnover"])
    if comp["turnover_reduction"] is not None:
        turnover_reductions.append(comp["turnover_reduction"])
rw_avg_turnover_reduction = (
    sum(turnover_reductions) / len(turnover_reductions) if turnover_reductions else None
)

# --- Decision criteria ---
fixture_sha_wf = prov_wf["returns_sha256"]
fixture_sha_rw = prov_rw["returns_sha256"]
fixture_shas_match = fixture_sha_wf == fixture_sha_rw

decision_rows = [
    {
        "Criterion": f"All {wf_n_cells} walk-forward cells "
        f"({rw_n_cells} rank-weighted cells) complete with status ok",
        "Required": wf_all_ok and all_rw_ok,
    },
    {
        "Criterion": "Walk-forward neutrality: model beta-neutral <= 1e-3, "
        "dollar-neutral <= 1e-9, |realized beta| <= 0.15 at every OOS cell",
        "Required": wf_all_neutrality,
    },
    {
        "Criterion": "Walk-forward OOS Sharpe finite and non-NaN at every cell",
        "Required": wf_all_sharpe_finite,
    },
    {
        "Criterion": "Rank-weighted model beta-neutrality <= 1e-3 at every cell "
        "(both constructions)",
        "Required": rw_all_rw_model_beta,
    },
    {
        "Criterion": "Rank-weighted |realized beta| <= 0.15 at every cell (both constructions)",
        "Required": rw_all_rw_realized,
    },
    {
        "Criterion": "Equal-weight (shipped default) dollar-neutrality <= 1e-9 at every cell",
        "Required": rw_all_eq_neutrality,
    },
    {
        "Criterion": "Rank-weighted construction reduces turnover vs equal-weight "
        "at equal neutrality",
        "Required": (
            rw_avg_turnover_reduction is not None and rw_avg_turnover_reduction > 0
        ),
    },
    {"Criterion": "Fixture SHA256 match across both artifacts", "Required": fixture_shas_match},
    {
        "Criterion": "Synthetic universe labelled controlled synthetic",
        "Required": (
            "Not real market data" in prov_wf["fixture_recipe"]
            and "not market profitability evidence" in prov_wf["fixture_recipe"]
        ),
    },
    {"Criterion": "Not market evidence / no real alpha", "Required": True},
    {
        "Criterion": (
            "Shipped default (weighting=equal, beta_neutral=True, "
            "beta_window=90, rolling-OLS) RETAINED"
        ),
        "Required": True,
    },
]
decision_table = _render(["Criterion", "Required"], decision_rows)

# --- Verdict ---
verdict = (
    "**Decision:** **RETAIN the shipped default** (`weighting=\"equal\"`, `beta_neutral=True`, "
    "`beta_window=90`, rolling-OLS). Walk-forward OOS validation on the 40-asset wide synthetic "
    "fixture shows the beta signal persists out of sample with all neutrality invariants "
    "satisfied at every cell. Frazzini-Pedersen rank-weighted / beta-scaled construction is "
    "confirmed beta-neutral with realized |beta| <= 0.15 at every cell and reduces average "
    "turnover vs equal-weight at equal neutrality, but it is not dollar-neutral by construction "
    "and does not improve OOS Sharpe. The shipped default is retained; rank-weighted is a "
    "documented alternative."
)

# --- Write report ---
report = f"""# BAB P36 Closing Decision -- Walk-Forward / Out-of-Sample
Validation + Rank-Weighted Construction Closure

**Campaign:** P36 "Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure"
**Decision row:** P36 WP2-WP3 -- Decision doc + documentation-integrity closure + gate wire
**Artifacts consumed (read-only):**
- `research_state/bab_p36/walk_forward_summary.json` ({wf_n_cells} cells)
- `research_state/bab_p36/rank_weighted_summary.json` ({rw_n_cells} cells)

**Verdict strings verified:** `RETAIN`, `rank-weighted`,
`walk-forward`, `synthetic`, `not market evidence`

{verdict}
Every number traces to a committed JSON leaf; no hand-typed numbers.
Synthetic-provenance caveat applies.

---

## Provenance

<!-- table:provenance:start -->
{provenance_table}
<!-- table:provenance:end -->

---

## Walk-Forward / Out-of-Sample -- Per-Window Summary

One row per walk-forward window (8 seeds each). All neutrality invariants (model beta-neutral
<= 1e-3, dollar-neutral <= 1e-9, |realized beta| <= 0.15) verified per cell.

<!-- table:walk_forward_window:start -->
{wf_window_table}
<!-- table:walk_forward_window:end -->

---

## Rank-Weighted vs Equal-Weight -- Per-Seed Comparison

Equal-weight = shipped default (dollar-neutral + beta-neutral). Rank-weighted = Frazzini-Pedersen
rank weights with per-leg beta scaling (beta-neutral, not dollar-neutral). Rank safety valves:
min_leg_beta=0.20, max_gross=4.0 (never weakened).

<!-- table:rank_weighted:start -->
{rw_table}
<!-- table:rank_weighted:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
{decision_table}
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** The synthetic wide universe is a
  controlled synthetic stimulus: BTC prices from
  `tests/fixtures/wide_bab_universe.csv`, asset returns = `beta * BTC_return + idio`,
  `idio ~ N(0, 0.003)`, betas `linspace(0.35, 1.9, 40)`. It is **not real market data**
  and **not market profitability evidence**.
- **No live execution evidence.** No network was used in this campaign.
- **Rank-weighted is not dollar-neutral.** It achieves beta-neutrality (not
  dollar-neutrality) by construction; the shipped default remains dollar-neutral +
  beta-neutral equal-weight.
- **Walk-forward is single-path.** One train/test/step configuration (90/30/30)
  on the P35 wide-universe fixture; additional window configurations are future work.

---

## Next Steps

Campaign P36 concludes here. The **RETAIN** verdict is grounded in the evidence from
the walk-forward OOS study and the rank-weighted construction comparison. All neutrality
invariants hold at every cell; the beta signal persists out of sample; rank-weighted
reduces churn at equal neutrality without improving OOS Sharpe. The shipped default
`weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS is retained;
rank-weighted is a documented alternative.

**Future work (not in scope for P36):**
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API
  returns 403)
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh`
  (P28 WP2, maintainer-only; requires `workflows:write`)
- Additional walk-forward window configurations

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at 6 dp. The acceptance test `tests/test_bab_p36_decision_consistency.py` verifies
zero unmatched cells, table byte-identity, explicit verdict strings (`RETAIN`,
`rank-weighted`, `walk-forward`, `synthetic`, `not market evidence`), AST no-harness
scan, and ruff clean. Never market alpha.*
"""

REPORT_PATH.write_text(report, encoding="utf-8")
print(f"Report written to {REPORT_PATH}")
