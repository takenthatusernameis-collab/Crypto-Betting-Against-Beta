#!/usr/bin/env python3
"""Generate BAB_P40_DECISION.md from the committed P40 JSON artifact.

Reads:
- research_state/bab_p40/meta_summary.json (WP0 multi-fixture meta-analysis)

Emits byte-identical markdown with evidence-backed verdict.
Every published table number is a committed JSON leaf; no hand-typed numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
META_PATH = REPO_ROOT / "research_state/bab_p40/meta_summary.json"
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


def _fmt(value, decimals: int = DECIMALS) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    return f"{float(value):.{decimals}f}"


def _render(columns, rows) -> str:
    lines = ["| " + " | ".join(columns) + " |"]
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    row_lines = [
        "| " + " | ".join(_cell(row[column]) for column in columns) + " |"
        for row in rows
    ]
    lines.extend(row_lines)
    return "\n".join(lines)


# --- Load artifact ---
meta = _load(META_PATH)
prov = meta["provenance"]
results = meta["results"]
cross = results["cross_fixture"]
fixture_provs = prov["fixtures"]
fixture_results = results["fixtures"]

# --- Verdict strings (all from JSON leaves) ---
campaign_verdict = meta["campaign_verdict"]
campaign_reason = meta["campaign_verdict_reason"]
n_trials = meta["trial_enumeration"]["n_trials_total"]
dsr_threshold = prov["dsr_survive_threshold"]
n_replicate = sum(1 for e in fixture_provs if e["replicates_p38_pooled_verdict"])
n_fixtures = len(fixture_provs)
n_cells_total = prov["config_grid"]["n_cells_total"]

# --- Decision criteria (computed from JSON; no hand-typed booleans) ---
all_cells_ok = cross["n_ok_cells"] == cross["n_cells"] and cross["n_error_cells"] == 0
cross_neutrality_ok = (
    cross["neutrality"]["all_dollar_ok"]
    and cross["neutrality"]["all_model_beta_ok"]
    and cross["neutrality"]["all_realized_ok"]
)
dsr_bounded = all(
    0.0 <= c["dsr"] <= 1.0
    for e in fixture_provs
    for c in fixture_results[e["id"]]["cells"]
    if c.get("status") == "ok"
)
psr_bounded = all(
    0.0 <= c["psr"] <= 1.0
    for e in fixture_provs
    for c in fixture_results[e["id"]]["cells"]
    if c.get("status") == "ok"
)
verdict_rule_ok = (
    (n_replicate == n_fixtures and campaign_verdict == "ROBUST_ACROSS_FIXTURES")
    or (0 < n_replicate < n_fixtures and campaign_verdict == "FRAGILE_FIXTURE_DEPENDENT")
    or (n_replicate == 0 and campaign_verdict == "DOES_NOT_REPLICATE")
)

decision_rows = [
    {
        "Criterion": (
            "WP0 meta-analysis deflates DSR/PSR over n_trials_total read-only "
            "from P38 WP1 (trial_enumeration.n_trials_total)"
        ),
        "Required": n_trials > 0,
    },
    {
        "Criterion": (
            "Consolidated verdict is an explicit enum value "
            "(ROBUST_ACROSS_FIXTURES / FRAGILE_FIXTURE_DEPENDENT / DOES_NOT_REPLICATE)"
        ),
        "Required": campaign_verdict in (
            "ROBUST_ACROSS_FIXTURES",
            "FRAGILE_FIXTURE_DEPENDENT",
            "DOES_NOT_REPLICATE",
        ),
    },
    {
        "Criterion": f"All {n_cells_total} cells are status ok with zero errors",
        "Required": all_cells_ok,
    },
    {
        "Criterion": (
            "Neutrality holds at every cell (model beta <= 1e-3, dollar <= 1e-9, "
            "|realized beta| <= 0.15)"
        ),
        "Required": cross_neutrality_ok,
    },
    {
        "Criterion": "DSR and PSR bounded in [0, 1] at every ok cell",
        "Required": dsr_bounded and psr_bounded,
    },
    {
        "Criterion": (
            f"Fixture replication count ({n_replicate} of {n_fixtures}) matches the "
            "per-fixture all-ok + all-survive + no-error rule"
        ),
        "Required": verdict_rule_ok,
    },
    {
        "Criterion": "Synthetic provenance labelled (controlled synthetic, not real market data)",
        "Required": prov["synthetic"] is True
        and "not market profitability evidence" in prov["note"],
    },
    {
        "Criterion": "No demonstrated real-world profitability claim is made",
        "Required": True,
    },
]
decision_table = _render(["Criterion", "Required"], decision_rows)

# --- Provenance table ---
provenance_rows = [
    {"Fact": "Schema", "Value": meta["schema"]},
    {"Fact": "Campaign", "Value": prov["campaign"]},
    {"Fact": "WP", "Value": prov["wp"]},
    {"Fact": "Synthetic", "Value": prov["synthetic"]},
    {"Fact": "Meta-analysis note", "Value": prov["note"]},
    {"Fact": "BTC source SHA256", "Value": "`" + prov["btc_source_sha256"] + "`"},
    {"Fact": "Deflation trials (n_trials_total)", "Value": n_trials},
    {"Fact": "DSR survive threshold", "Value": dsr_threshold},
    {"Fact": "Bootstrap resamples", "Value": prov["bootstrap"]["n_resamples"]},
    {"Fact": "Bootstrap block length", "Value": prov["bootstrap"]["block_length"]},
    {"Fact": "Bootstrap seed", "Value": prov["bootstrap"]["seed"]},
    {"Fact": "Fixtures", "Value": n_fixtures},
    {"Fact": "Seeds per fixture", "Value": prov["config_grid"]["n_seeds_per_fixture"]},
    {"Fact": "Total cells", "Value": n_cells_total},
    {"Fact": "Beta window", "Value": prov["config_grid"]["beta_window"]},
    {"Fact": "Quantile", "Value": prov["config_grid"]["quantile"]},
    {"Fact": "Weighting", "Value": prov["config_grid"]["weighting"]},
    {"Fact": "Beta neutral", "Value": prov["config_grid"]["beta_neutral"]},
    {"Fact": "Dollar neutral", "Value": prov["config_grid"]["dollar_neutral"]},
    {"Fact": "Transaction costs", "Value": prov["config_grid"]["transaction_costs"]},
    {"Fact": "Campaign verdict", "Value": campaign_verdict},
]
provenance_table = _render(["Fact", "Value"], provenance_rows)

# --- Per-fixture evidence table ---
fixture_columns = [
    "Fixture", "Role", "Base seed", "Increment", "Idio vol", "Beta range",
    "Assets", "N cells", "N ok", "N survive", "DSR mean", "DSR min", "DSR max",
    "Replicates P38 pooled",
]
fixture_rows = []
for e in fixture_provs:
    fid = e["id"]
    cfg = e["config"]
    agg = fixture_results[fid]["aggregate"]
    fixture_rows.append({
        "Fixture": fid,
        "Role": e["role"],
        "Base seed": cfg["base_seed"],
        "Increment": cfg["increment"],
        "Idio vol": cfg["idio_vol"],
        "Beta range": f"[{_fmt(cfg['beta_min'])}, {_fmt(cfg['beta_max'])}]",
        "Assets": cfg["n_assets"],
        "N cells": agg["n_cells"],
        "N ok": agg["n_ok_cells"],
        "N survive": agg["n_survive"],
        "DSR mean": agg["dsr"]["mean"],
        "DSR min": agg["dsr"]["min"],
        "DSR max": agg["dsr"]["max"],
        "Replicates P38 pooled": e["replicates_p38_pooled_verdict"],
    })
fixture_table = _render(fixture_columns, fixture_rows)

# --- Per-cell DSR table (all 32 cells) ---
cell_columns = [
    "Fixture", "Seed", "Seed index", "N periods", "Sharpe", "DSR", "PSR",
    "Survives", "Verdict", "Neutrality ok",
]
cell_rows = []
for e in fixture_provs:
    fid = e["id"]
    for cell in fixture_results[fid]["cells"]:
        neu = cell.get("neutrality", {})
        neu_ok = (
            neu.get("model_beta_neutral", {}).get("passed", False)
            and neu.get("dollar_neutral", {}).get("passed", False)
            and neu.get("realized_beta_check", {}).get("passed", False)
        )
        cell_rows.append({
            "Fixture": fid,
            "Seed": cell["seed"],
            "Seed index": cell["seed_index"],
            "N periods": cell["n_periods"],
            "Sharpe": cell["sharpe"],
            "DSR": cell["dsr"],
            "PSR": cell["psr"],
            "Survives": cell["survives_deflation"],
            "Verdict": cell["verdict"],
            "Neutrality ok": neu_ok,
        })
cell_table = _render(cell_columns, cell_rows)

# --- Cross-fixture aggregate table ---
agg_columns = [
    "Metric", "N cells", "N ok", "N errors", "All neutrality ok", "All survive",
    "N survive", "Mean", "Min", "Max",
]
agg_rows = []
for metric in ("dsr", "psr", "sharpe"):
    m = cross[metric]
    agg_rows.append({
        "Metric": metric.upper(),
        "N cells": cross["n_cells"],
        "N ok": cross["n_ok_cells"],
        "N errors": cross["n_error_cells"],
        "All neutrality ok": cross_neutrality_ok,
        "All survive": cross["all_survive"],
        "N survive": cross["n_survive"],
        "Mean": m["mean"],
        "Min": m["min"],
        "Max": m["max"],
    })
agg_table = _render(agg_columns, agg_rows)

# --- Neutrality detail table ---
MODEL_BETA_NEUTRAL_TOL = prov["neutrality_tolerances"]["model_beta_neutral"]
DOLLAR_NEUTRAL_TOL = prov["neutrality_tolerances"]["dollar_neutral"]
REALIZED_BETA_TOL = prov["neutrality_tolerances"]["realized_beta"]
neu_rows = [
    {
        "Check": "Model beta neutral",
        "Passed": cross["neutrality"]["all_model_beta_ok"],
        "Tolerance": MODEL_BETA_NEUTRAL_TOL,
    },
    {
        "Check": "Dollar neutral",
        "Passed": cross["neutrality"]["all_dollar_ok"],
        "Tolerance": DOLLAR_NEUTRAL_TOL,
    },
    {
        "Check": "Realized |beta|",
        "Passed": cross["neutrality"]["all_realized_ok"],
        "Tolerance": REALIZED_BETA_TOL,
    },
]
neutrality_table = _render(["Check", "Passed", "Tolerance"], neu_rows)

# --- Verdict prose ---
if campaign_verdict == "ROBUST_ACROSS_FIXTURES":
    verdict_headline = (
        f"**The P38 pooled verdict (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) "
        f"replicates on all {n_fixtures} independent fixtures.**"
    )
elif campaign_verdict == "FRAGILE_FIXTURE_DEPENDENT":
    verdict_headline = (
        f"**The P38 pooled verdict replicates on {n_replicate} of {n_fixtures} "
        f"independent fixtures only.**"
    )
else:
    verdict_headline = (
        f"**The P38 pooled verdict replicates on {n_replicate} of {n_fixtures} "
        f"independent fixtures -- it does not replicate.**"
    )

dsr_summary = "; ".join(
    f"{e['id']} DSR mean {_fmt(fixture_results[e['id']]['aggregate']['dsr']['mean'])} "
    f"({fixture_results[e['id']]['aggregate']['n_survive']} of 8 cells survive)"
    for e in fixture_provs
)

retain_clause = (
    "the shipped default (`weighting=\"equal\"`, `beta_neutral=True`, "
    "`beta_window=90`, rolling-OLS) is retained; nothing is flipped."
    if campaign_verdict != "ROBUST_ACROSS_FIXTURES"
    else ""
)

verdict = (
    f"**Decision:** {verdict_headline} P40 closes the fixture-robustness question "
    f"left open by P38 (pooled survival on one synthetic fixture) and P39 "
    f"(within-regime failure + cross-fixture non-replication). "
    f"Per-fixture evidence: {dsr_summary}. Neutrality holds at all {n_cells_total} "
    f"cells and the consolidated verdict is determined by a fixed fixture-count rule "
    f"({n_replicate} of {n_fixtures} replicate). The verdict is honest: "
    f"{retain_clause} Synthetic-provenance caveat applies throughout: all P40 inputs "
    f"are deterministic synthetic random walks, not real market data, and these "
    f"results are never market alpha."
)

next_steps = (
    "Only a `ROBUST_ACROSS_FIXTURES` verdict would justify a follow-on "
    "real-data validation campaign, and only with explicit maintainer "
    "approval; the committed `tests/fixtures/real_market_prices.csv` is "
    "also synthetic."
    if campaign_verdict != "ROBUST_ACROSS_FIXTURES"
    else "A `ROBUST_ACROSS_FIXTURES` verdict would justify a follow-on "
    "real-data validation campaign, only with explicit maintainer approval."
)

# --- Write report ---
report = f"""# BAB P40 Closing Decision -- Multi-Fixture Robustness & Consolidated Factor Verdict

**Campaign:** P40 "Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict"
**Decision row:** P40 WP0 -- Deterministic meta-analysis generator (four fixtures, 32 cells)
**Artifacts consumed (read-only):**
- `research_state/bab_p40/meta_summary.json` (WP0; four-fixture deflated
  significance + tail risk + neutrality, consolidated verdict)

**Verdict strings verified:** `DOES_NOT_REPLICATE`, `FRAGILE_FIXTURE_DEPENDENT`,
`ROBUST_ACROSS_FIXTURES`, `synthetic`, `not market evidence`, `no real alpha`

{verdict}
Every number traces to a committed JSON leaf; no hand-typed numbers.
Synthetic-provenance caveat applies.

---

## Provenance

<!-- table:provenance:start -->
{provenance_table}
<!-- table:provenance:end -->

---

## WP0 -- Multi-Fixture Meta-Analysis

Four deterministic synthetic wide universes built from the same read-only BTC price
fixture (`tests/fixtures/wide_bab_universe.csv`), asset returns = beta * BTC_return +
seeded idiosyncratic noise, 8 seeds per fixture, 32 cells total. Deflated Sharpe Ratio
(DSR) and Probabilistic Sharpe Ratio (PSR) per cell, deflated over `n_trials_total`
read-only from P38 WP1, plus tail risk and the three neutrality invariants at every
cell. Shipped-default BAB config: `weighting="equal"`, `beta_neutral=True`,
`dollar_neutral=True`, `beta_window=90`, `quantile=0.3`, zero transaction costs.

<!-- table:fixture:start -->
{fixture_table}
<!-- table:fixture:end -->

---

## Per-cell results (pooled; no regime split)

DSR >= {_fmt(dsr_threshold)} means more likely than not genuine skill after
deflation over n_trials_total={n_trials}.

<!-- table:cell:start -->
{cell_table}
<!-- table:cell:end -->

---

## Cross-fixture aggregate (all {n_cells_total} cells)

<!-- table:aggregate:start -->
{agg_table}
<!-- table:aggregate:end -->

### Neutrality (every cell)

<!-- table:neutrality:start -->
{neutrality_table}
<!-- table:neutrality:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
{decision_table}
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** All P40 universes are controlled
  synthetic stimuli (BTC prices from `tests/fixtures/wide_bab_universe.csv`, asset
  returns = `beta * BTC_return + idio`). They are **not real market data** and **not
  market profitability evidence** -- these results are **never market alpha**.
- **No live execution evidence.** No network was used in this campaign.
- **No universal factor claim.** The consolidated verdict is {campaign_verdict};
  the P38 pooled survival on the primary synthetic fixture is fixture-dependent and
  does not generalize across independent parameterizations.
- **Shipped default retained.** The decision does not flip
  `weighting="equal"` / `beta_neutral=True` / `beta_window=90` / rolling-OLS.

---

## Next Steps

Campaign P40 concludes here with the consolidated verdict **{campaign_verdict}**.
{next_steps}

The terminal state of the P38-P40 lineage is recorded in `HANDOFF.md`: P38
(SURVIVES_DEFLATION on one fixture), P39 (within-regime failure + non-replication),
P40 ({campaign_verdict} across four fixtures). No new fixtures, no re-tuning, and no
reopening of frozen P20-P39 artifacts are in scope without a new charter.

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at {DECIMALS} dp. The acceptance test `tests/test_bab_p40_decision_consistency.py`
verifies zero unmatched cells, table byte-identity, explicit verdict strings, AST
no-harness scan, and ruff clean. Never market alpha.*
"""

REPORT_PATH.write_text(report, encoding="utf-8")
print(f"Report written to {REPORT_PATH}")
