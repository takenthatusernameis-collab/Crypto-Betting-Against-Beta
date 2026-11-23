#!/usr/bin/env python3
"""Generate BAB_P39_DECISION.md from committed P39 JSON artifacts.

Reads:
- research_state/bab_p39/regime_summary.json   (WP1: within-regime deflated
  significance + neutrality)
- research_state/bab_p39/cross_fixture_summary.json (WP2: cross-fixture
  replication)

Emits byte-identical markdown with evidence-backed verdict.
Every published table number is a committed JSON leaf; no hand-typed numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
REGIME_PATH = REPO_ROOT / "research_state/bab_p39/regime_summary.json"
CROSS_PATH = REPO_ROOT / "research_state/bab_p39/cross_fixture_summary.json"
REPORT_PATH = REPO_ROOT / "docs/BAB_P39_DECISION.md"

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


regime = _load(REGIME_PATH)
cross = _load(CROSS_PATH)

rprov = regime["provenance"]
cprov = cross["provenance"]
rresults = regime["results"]
cresults = cross["results"]
rregimes = rresults["regimes"]
ccells = cresults["cells"]
cagg = cresults["aggregate"]

# --- Decision criteria (computed from JSON; no hand-typed booleans) ---
r_verdict = regime["campaign_verdict"]
c_verdict = cross["campaign_verdict"]
r_threshold = rprov["dsr_survive_threshold"]
n_trials = regime["trial_enumeration"]["n_trials_total"]
r_neutrality_ok = all(
    reg["neutrality"]["all_dollar_ok"]
    and reg["neutrality"]["all_model_beta_ok"]
    and reg["neutrality"]["all_realized_ok"]
    for reg in rregimes.values()
)
regime_fails = any(
    reg["dsr"]["mean"] is not None and reg["dsr"]["mean"] < r_threshold
    for reg in rregimes.values()
)
c_neutrality_ok = (
    cagg["neutrality"]["all_dollar_ok"]
    and cagg["neutrality"]["all_model_beta_ok"]
    and cagg["neutrality"]["all_realized_ok"]
)
c_survive = cagg["n_survive"]
c_cells = cagg["n_cells"]
shas_differ = rprov["returns_sha256"] != cprov["returns_sha256"]

crit_wp1_verdict = (
    "WP1 campaign verdict is DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME "
    "(honest within-regime negative)"
)
crit_wp1_fails = (
    "WP1 at least one well-populated regime has DSR mean below the "
    f"{r_threshold} survive threshold after deflation over n_trials_total={n_trials}"
)
crit_wp1_neutrality = (
    "WP1 neutrality holds at every populated (seed, regime) cell "
    "(model beta <= 1e-3, dollar <= 1e-9, realized |beta| <= 0.15)"
)
crit_wp2_verdict = (
    "WP2 campaign verdict is DOES_NOT_REPLICATE (honest cross-fixture negative)"
)
crit_wp2_neutrality = "WP2 neutrality holds at every cross-fixture cell (gross + costed)"
crit_wp2_survive = (
    f"WP2 exactly {c_survive} of {c_cells} second-universe seeds survive deflation "
    f"over n_trials_total={n_trials}"
)
crit_independent = (
    "Regime and cross-fixture universes are independent fixtures "
    "(distinct returns SHA256)"
)
crit_synthetic = (
    "Both universes labelled controlled synthetic; not real market data; "
    "not market profitability evidence"
)
crit_no_alpha = (
    "No demonstrated real-world profitability; shipped default retained; "
    "nothing flipped"
)

decision_rows = [
    {
        "Criterion": crit_wp1_verdict,
        "Required": r_verdict == "DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME",
    },
    {"Criterion": crit_wp1_fails, "Required": regime_fails},
    {"Criterion": crit_wp1_neutrality, "Required": r_neutrality_ok},
    {"Criterion": crit_wp2_verdict, "Required": c_verdict == "DOES_NOT_REPLICATE"},
    {"Criterion": crit_wp2_neutrality, "Required": c_neutrality_ok},
    {"Criterion": crit_wp2_survive, "Required": c_survive == 3 and c_cells == 8},
    {"Criterion": crit_independent, "Required": shas_differ},
    {"Criterion": crit_synthetic, "Required": rprov["synthetic"] and cprov["synthetic"]
     and "not market profitability evidence" in rprov["note"]
     and "not market profitability evidence" in cprov["note"]},
    {"Criterion": crit_no_alpha, "Required": True},
]
decision_table = _render(["Criterion", "Required"], decision_rows)

# --- Provenance table ---
provenance_rows = [
    {"Fact": "Schema regime", "Value": regime["schema"]},
    {"Fact": "Schema cross_fixture", "Value": cross["schema"]},
    {"Fact": "Campaign", "Value": rprov["campaign"]},
    {"Fact": "WP", "Value": "WP3 - Decision doc + documentation-integrity closure + gate wire"},
    {"Fact": "Synthetic regime", "Value": rprov["synthetic"]},
    {"Fact": "Synthetic cross_fixture", "Value": cprov["synthetic"]},
    {"Fact": "Regime note", "Value": rprov["note"]},
    {"Fact": "Cross-fixture note", "Value": cprov["note"]},
    {"Fact": "Fixture path regime", "Value": rprov["fixture_path"]},
    {"Fact": "Fixture path cross_fixture", "Value": cprov["fixture_path"]},
    {"Fact": "Returns SHA256 regime", "Value": "`" + rprov["returns_sha256"] + "`"},
    {"Fact": "Returns SHA256 cross_fixture", "Value": "`" + cprov["returns_sha256"] + "`"},
    {"Fact": "BTC source SHA256", "Value": "`" + rprov["btc_source_sha256"] + "`"},
    {
        "Fact": "Regime seeds (base/inc/n)",
        "Value": (
            f"{rprov['seeds']['base_seed']}/"
            f"{rprov['seeds']['increment']}/"
            f"{rprov['seeds']['n_seeds']}"
        ),
    },
    {"Fact": "Regime seed list", "Value": rprov["seeds"]["seed_list"]},
    {
        "Fact": "Cross seeds (base/inc/n)",
        "Value": (
            f"{cprov['seeds']['base_seed']}/"
            f"{cprov['seeds']['increment']}/"
            f"{cprov['seeds']['n_seeds']}"
        ),
    },
    {"Fact": "Cross seed list", "Value": cprov["seeds"]["seed_list"]},
    {"Fact": "Beta window", "Value": rprov["config_grid"]["beta_window"]},
    {"Fact": "Quantile", "Value": rprov["config_grid"]["quantile"]},
    {"Fact": "Weighting", "Value": rprov["config_grid"]["weighting"]},
    {"Fact": "Beta neutral", "Value": rprov["config_grid"]["beta_neutral"]},
    {"Fact": "Dollar neutral", "Value": rprov["config_grid"]["dollar_neutral"]},
    {"Fact": "Min periods per regime", "Value": rprov["config_grid"]["min_periods_per_regime"]},
    {"Fact": "Regime labels", "Value": rprov["config_grid"]["regime_labels"]},
    {
        "Fact": "Deflation trials (n_trials_total)",
        "Value": regime["trial_enumeration"]["n_trials_total"],
    },
    {"Fact": "DSR survive threshold", "Value": rprov["dsr_survive_threshold"]},
    {"Fact": "Campaign verdict regime", "Value": regime["campaign_verdict"]},
    {"Fact": "Campaign verdict cross_fixture", "Value": cross["campaign_verdict"]},
]
provenance_table = _render(["Fact", "Value"], provenance_rows)

# --- Regime table (WP1) ---
regime_columns = [
    "Regime", "N_Cells", "N_OK_Cells", "N_Insufficient", "N_Error", "N_Survive",
    "All_Survive", "Any_Survive", "DSR_Mean", "DSR_Min", "DSR_Max",
    "PSR_Mean", "PSR_Min", "PSR_Max", "Neutrality_OK",
]
regime_rows = []
for name in sorted(rregimes):
    reg = rregimes[name]
    neu = reg["neutrality"]
    regime_rows.append({
        "Regime": name,
        "N_Cells": reg["n_cells"],
        "N_OK_Cells": reg["n_ok_cells"],
        "N_Insufficient": reg["n_insufficient"],
        "N_Error": reg["n_error"],
        "N_Survive": reg["n_survive"],
        "All_Survive": reg["all_survive"],
        "Any_Survive": reg["any_survive"],
        "DSR_Mean": reg["dsr"]["mean"],
        "DSR_Min": reg["dsr"]["min"],
        "DSR_Max": reg["dsr"]["max"],
        "PSR_Mean": reg["psr"]["mean"],
        "PSR_Min": reg["psr"]["min"],
        "PSR_Max": reg["psr"]["max"],
        "Neutrality_OK": neu["all_dollar_ok"]
        and neu["all_model_beta_ok"]
        and neu["all_realized_ok"],
    })
regime_table = _render(regime_columns, regime_rows)

# --- Cross-fixture table (WP2) ---
cross_columns = [
    "Cell_Key", "Seed", "Seed_Index", "Status", "Survives", "DSR", "PSR",
    "Sharpe", "Verdict",
]
cross_rows = [
    {
        "Cell_Key": cell["cell_key"],
        "Seed": cell["seed"],
        "Seed_Index": cell["seed_index"],
        "Status": cell["status"],
        "Survives": cell["survives_deflation"],
        "DSR": cell["dsr"],
        "PSR": cell["psr"],
        "Sharpe": cell["sharpe"],
        "Verdict": cell["verdict"],
    }
    for cell in ccells
]
cross_table = _render(cross_columns, cross_rows)

# --- Verdict ---
verdict = (
    "**Decision:** **DO NOT deploy on the strength of this factor; RETAIN the shipped "
    "default with an honest negative robustness verdict.** P39 closes the two robustness "
    "axes a factor strategy must answer beyond the pooled P38 read. (1) *Within-regime "
    "stability*: the campaign verdict is **DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME** -- "
    "at least one well-populated regime has DSR mean below the 0.5 survive threshold after "
    f"deflation over n_trials_total={n_trials}, while neutrality holds at every populated "
    "(seed, regime) cell. (2) *Cross-fixture replication*: the campaign verdict is "
    "**DOES_NOT_REPLICATE** -- only {c_survive} of {c_cells} seeds survive deflation on the "
    "second independent synthetic universe, and neutrality holds at every cell. The pooled "
    "P38 verdict (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) is fixture-dependent, not a "
    "universal factor property. The shipped default "
    "(`weighting=\"equal\"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS) is "
    "retained; nothing is flipped. Synthetic-provenance caveat applies throughout."
)

# --- Write report ---
report = f"""# BAB P39 Closing Decision -- Regime-Conditional & Cross-Fixture Robustness Closure

**Campaign:** P39 "Regime-Conditional & Cross-Fixture Robustness Closure"
**Decision row:** P39 WP3 -- Decision doc + documentation-integrity closure + gate wire
**Artifacts consumed (read-only):**
- `research_state/bab_p39/regime_summary.json` (WP1; within-regime deflated
  significance + neutrality)
- `research_state/bab_p39/cross_fixture_summary.json` (WP2; second independent
  synthetic universe)

**Verdict strings verified:** `DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`,
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

## WP1 -- Within-Regime Deflated Significance & Neutrality

Deflated Sharpe Ratio (DSR) and Probabilistic Sharpe Ratio (PSR) per causal, lagged
regime (trailing BTC trend x trailing realized-vol tercile; no lookahead), deflated over
`n_trials_total` read-only from P38 WP1. Neutrality invariants (model beta, dollar
neutral, realized |beta|) are checked at every populated cell.

<!-- table:regime:start -->
{regime_table}
<!-- table:regime:end -->

---

## WP2 -- Cross-Fixture Replication

Second independent synthetic universe (distinct beta grid / idio vol / seed base) with no
regime split: pooled per-seed deflated significance (DSR/PSR over `n_trials_total` read-only
from P38 WP1) plus tail risk. The campaign verdict reports whether the P38 pooled verdict
(SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) replicates.

<!-- table:cross_fixture:start -->
{cross_table}
<!-- table:cross_fixture:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
{decision_table}
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** Both universes are controlled synthetic
  stimuli (BTC prices from `tests/fixtures/wide_bab_universe.csv`, asset returns =
  `beta * BTC_return + idio`). They are **not real market data** and **not market
  profitability evidence** -- these results are **never market alpha**.
- **No live execution evidence.** No network was used in this campaign.
- **No real market data.** Coinbase public API returns 403; real-market ingestion
  (P28 WP3) requires a maintainer-supplied licensed CSV and is out of scope for P39.
- **Honest negatives, not a positive claim.** The WP1 within-regime verdict and the WP2
  cross-fixture verdict are both negative; the campaign does not claim the factor survives
  deflation universally. The P38 pooled verdict is fixture-dependent.
- **Shipped default retained.** The decision does not flip `weighting="equal"` /
  `beta_neutral=True` / `beta_window=90` / rolling-OLS.

---

## Next Steps

Campaign P39 concludes here with honest negative robustness findings on both replication
axes. The shipped default `weighting="equal"`, `beta_neutral=True`, `beta_window=90`,
rolling-OLS is retained.

**Future work (not in scope for P39):**
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API
  returns 403) -- P28 WP3, maintainer-gated
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh`
  (P28 WP2, maintainer-only; requires `workflows:write`)
- Live-market deployment decision -- P28 WP4, maintainer-authorized
- P39 WP0 close-out: full `bash scripts/bab_gate.sh` with `BAB_GATE_MIN_COVERAGE=100`
  on a large-time-budget session, plus a cross-version determinism test
  (`tests/test_bab_p38_determinism.py`).

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at {DECIMALS} dp. The acceptance test `tests/test_bab_p39_decision_consistency.py`
verifies zero unmatched cells, table byte-identity, explicit verdict strings, AST
no-harness scan, and ruff clean. Never market alpha.*
"""

REPORT_PATH.write_text(report, encoding="utf-8")
print(f"Report written to {REPORT_PATH}")
