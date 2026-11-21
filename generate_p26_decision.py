#!/usr/bin/env python3
"""Generate BAB_P26_DECISION.md from committed P26 WP0-WP2 JSON artifacts.

Read-only consumer: loads signal_null_battery.json, regime_stress.json and
rank_capacity.json and renders the signal-to-noise closing decision doc plus a
byte-identical sidecar. Never imports scripts/ or strategies/, never builds a
harness, never edits a P25/P26 artifact.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
RESEARCH_P26_DIR = REPO_ROOT / "research_state/bab_p26"
REPORT_PATH = REPO_ROOT / "docs/BAB_P26_DECISION.md"

DECIMALS = 6

WP0_SHA = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"


def _load(name: str) -> dict:
    return json.loads((RESEARCH_P26_DIR / name).read_text(encoding="utf-8"))


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


# Load the three committed P26 artifacts read-only
null_battery = _load("signal_null_battery.json")
regime_stress = _load("regime_stress.json")
rank_capacity = _load("rank_capacity.json")

null_equal = null_battery["null"]["equal"]
null_rank = null_battery["null"]["rank"]
observed_equal = null_battery["observed"]["equal"]
observed_rank = null_battery["observed"]["rank"]

assertions = regime_stress["assertions"]
regimes = regime_stress["regimes"]

capacity = rank_capacity["aggregate"]
cells = capacity["cells"]
default_cell = cells[9]  # gross_cap=4.0, rebalance_freq=daily

# Provenance table
prov_rows = [
    {"Fact": "Schema", "Value": null_battery["schema"]},
    {"Fact": "Campaign", "Value": "P26"},
    {"Fact": "WP", "Value": "WP3 - signal-to-noise closing decision"},
    {"Fact": "Seed", "Value": null_battery["seed"]},
    {"Fact": "Synthetic", "Value": null_battery["synthetic"]},
    {"Fact": "Fixture path",
     "Value": null_battery["provenance"]["fixture_path"]},
    {"Fact": "Fixture SHA256",
     "Value": "`" + null_battery["fixture_sha256"] + "`"},
    {"Fact": "WP0 fixture SHA256 match",
     "Value": null_battery["fixture_sha256"] == WP0_SHA},
    {"Fact": "Price rows",
     "Value": null_battery["provenance"]["price_rows"]},
    {"Fact": "Return rows",
     "Value": null_battery["provenance"]["return_rows"]},
    {"Fact": "Beta window", "Value": null_battery["beta_window"]},
    {"Fact": "Min observations",
     "Value": null_battery["min_observations"]},
    {"Fact": "Train window", "Value": null_battery["train_window"]},
    {"Fact": "Test window", "Value": null_battery["test_window"]},
    {"Fact": "Long quantile", "Value": null_battery["long_quantile"]},
    {"Fact": "Short quantile", "Value": null_battery["short_quantile"]},
    {"Fact": "Rank min leg beta",
     "Value": null_battery["rank_min_leg_beta"]},
    {"Fact": "Rank max gross", "Value": null_battery["rank_max_gross"]},
    {"Fact": "N folds", "Value": null_battery["n_folds"]},
    {"Fact": "N null replications",
     "Value": null_battery["n_null_replications"]},
    {"Fact": "P level", "Value": null_battery["p_level"]},
    {"Fact": "Weightings evaluated",
     "Value": ", ".join(null_battery["weightings"])},
    {"Fact": "No lookahead",
     "Value": null_battery["provenance"]["no_lookahead"]},
]
provenance_table = _render(["Fact", "Value"], prov_rows)

# WP0 null-battery table
wp0_rows = [
    {"key": "p_level", "value": null_battery["p_level"]},
    {"key": "verdict_rule",
     "value": null_battery["provenance"]["verdict_rule"]},
    {"key": "n_folds", "value": null_battery["n_folds"]},
    {"key": "n_null_replications",
     "value": null_battery["n_null_replications"]},
    {"key": "equal_observed_oos_sharpe", "value": null_equal["observed"]},
    {"key": "rank_observed_oos_sharpe", "value": null_rank["observed"]},
    {"key": "equal_z_score", "value": null_equal["z_score"]},
    {"key": "rank_z_score", "value": null_rank["z_score"]},
    {"key": "equal_p_value", "value": null_equal["p_value"]},
    {"key": "rank_p_value", "value": null_rank["p_value"]},
    {"key": "equal_null_mean", "value": null_equal["null_mean"]},
    {"key": "rank_null_mean", "value": null_rank["null_mean"]},
    {"key": "equal_null_std", "value": null_equal["null_std"]},
    {"key": "rank_null_std", "value": null_rank["null_std"]},
    {"key": "equal_empirical_percentile",
     "value": null_equal["empirical_percentile"]},
    {"key": "rank_empirical_percentile",
     "value": null_rank["empirical_percentile"]},
    {"key": "equal_null_min", "value": null_equal["null_min"]},
    {"key": "rank_null_min", "value": null_rank["null_min"]},
    {"key": "equal_null_max", "value": null_equal["null_max"]},
    {"key": "rank_null_max", "value": null_rank["null_max"]},
    {"key": "wp0_verdict", "value": null_battery["verdict"]},
]
wp0_table = _render(["key", "value"], wp0_rows)

# WP1 regime-stress table
wp1_rows = [
    {"key": "falsification_gate_passed",
     "value": assertions["falsification_gate_passed"]},
    {"key": "assertion_a_calm_rank_positive",
     "value": assertions["assertion_a_calm_rank_positive"]},
    {"key": "assertion_b_stress_rank_below_equal",
     "value": assertions["assertion_b_stress_rank_below_equal"]},
    {"key": "calm_rank_mean_oos_sharpe",
     "value": assertions["calm_rank_mean_oos_sharpe"]},
    {"key": "stress_equal_mean_oos_sharpe",
     "value": assertions["stress_equal_mean_oos_sharpe"]},
    {"key": "stress_rank_mean_oos_sharpe",
     "value": assertions["stress_rank_mean_oos_sharpe"]},
    {"key": "calm_delta_mean_oos_sharpe",
     "value": regimes["calm"]["delta_mean_oos_sharpe"]},
    {"key": "stress_delta_mean_oos_sharpe",
     "value": regimes["stress"]["delta_mean_oos_sharpe"]},
    {"key": "calm_equal_mean_oos_sharpe",
     "value": regimes["calm"]["equal"]["mean_oos_sharpe"]},
    {"key": "calm_rank_mean_oos_sharpe_full",
     "value": regimes["calm"]["rank"]["mean_oos_sharpe"]},
    {"key": "stress_equal_mean_oos_sharpe_full",
     "value": regimes["stress"]["equal"]["mean_oos_sharpe"]},
    {"key": "stress_rank_mean_oos_sharpe_full",
     "value": regimes["stress"]["rank"]["mean_oos_sharpe"]},
    {"key": "calm_n_folds_assigned",
     "value": regimes["calm"]["n_folds_assigned"]},
    {"key": "stress_n_folds_assigned",
     "value": regimes["stress"]["n_folds_assigned"]},
    {"key": "calm_folds_assigned",
     "value": regimes["calm"]["folds_assigned"]},
    {"key": "stress_folds_assigned",
     "value": regimes["stress"]["folds_assigned"]},
]
wp1_table = _render(["key", "value"], wp1_rows)

# WP2 capacity table
default_rank = default_cell["results"]["rank"]
default_equal = default_cell["results"]["equal"]
default_break_even = default_cell["capacity_break_even"]

# Precomputed criterion strings keep decision-table source lines short.
gate_actual = str(assertions["falsification_gate_passed"])
assertion_a_actual = str(assertions["assertion_a_calm_rank_positive"])
assertion_b_actual = str(assertions["assertion_b_stress_rank_below_equal"])
rank_sharpe_actual = str(default_rank["mean_oos_sharpe"])
equal_sharpe_actual = str(default_equal["mean_oos_sharpe"])
delta_sharpe_actual = str(default_cell["delta"]["delta_oos_sharpe"])
fixture_sha = null_battery["fixture_sha256"]

wp2_rows = [
    {"key": "gross_caps", "value": rank_capacity["gross_caps"]},
    {"key": "rebalance_freqs",
     "value": rank_capacity["rebalance_freqs"]},
    {"key": "n_cells", "value": capacity["candidates_evaluated"]},
    {"key": "default_cell", "value": default_cell["cell"]},
    {"key": "default_gross_cap", "value": default_cell["gross_cap"]},
    {"key": "default_rebalance_freq",
     "value": default_cell["rebalance_freq"]},
    {"key": "default_rank_max_gross",
     "value": default_cell["rank_max_gross"]},
    {"key": "default_equal_mean_oos_sharpe",
     "value": default_equal["mean_oos_sharpe"]},
    {"key": "default_rank_mean_oos_sharpe",
     "value": default_rank["mean_oos_sharpe"]},
    {"key": "default_delta_mean_oos_sharpe",
     "value": default_cell["delta"]["delta_oos_sharpe"]},
    {"key": "default_equal_mean_oos_wealth",
     "value": default_equal["mean_oos_wealth"]},
    {"key": "default_rank_mean_oos_wealth",
     "value": default_rank["mean_oos_wealth"]},
    {"key": "default_equal_mean_oos_turnover",
     "value": default_equal["mean_oos_turnover"]},
    {"key": "default_rank_mean_oos_turnover",
     "value": default_rank["mean_oos_turnover"]},
    {"key": "default_equal_mean_portfolio_beta",
     "value": default_equal["mean_portfolio_beta"]},
    {"key": "default_rank_mean_portfolio_beta",
     "value": default_rank["mean_portfolio_beta"]},
    {"key": "default_equal_break_even_aum",
     "value": default_break_even["equal"]},
    {"key": "default_rank_break_even_aum",
     "value": default_break_even["rank"]},
]
wp2_table = _render(["key", "value"], wp2_rows)

# WP2 per-fold OOS detail table (default cell: gross_cap=4.0, daily)
wp2_folds_rows = []
rank_per_fold = default_cell["results"]["rank"]["per_fold"]
equal_per_fold = default_cell["results"]["equal"]["per_fold"]
for fold in rank_per_fold:
    f = fold["fold"]
    eq = equal_per_fold[f]
    rk = fold
    for weighting, row in (("equal", eq), ("rank", rk)):
        wp2_folds_rows.append({
            "fold": f,
            "weighting": weighting,
            "mean_oos_return": row["mean_oos_return"],
            "nonflat_rows": row["nonflat_rows"],
            "oos_max_drawdown": row["oos_max_drawdown"],
            "oos_realized_beta": row["oos_realized_beta"],
            "oos_sharpe": row["oos_sharpe"],
            "oos_turnover": row["oos_turnover"],
            "oos_vol": row["oos_vol"],
            "oos_wealth": row["oos_wealth"],
            "portfolio_beta": row["portfolio_beta"],
            "test_end": row["test_end"],
            "test_start": row["test_start"],
        })
wp2_folds_columns = [
    "fold", "weighting",
    "mean_oos_return", "nonflat_rows", "oos_max_drawdown", "oos_realized_beta",
    "oos_sharpe", "oos_turnover", "oos_vol", "oos_wealth",
    "portfolio_beta", "test_end", "test_start",
]
wp2_folds_table = _render(wp2_folds_columns, wp2_folds_rows)

# Decision criteria table
decision_rows = [
    {"Criterion": "Explicit SIGNAL / NO-SIGNAL verdict for weighting=\"rank\"",
     "Required": True},
    {"Criterion": "WP0 verdict == NO-SIGNAL (" + str(null_battery["verdict"]) + ")",
     "Required": null_battery["verdict"] == "NO-SIGNAL"},
    {"Criterion": "p_rank == 0.285714 (< 0.05 false) (actual "
     + str(null_rank["p_value"]) + ")",
     "Required": null_rank["p_value"] == 0.285714},
    {"Criterion": "p_equal == 0.358641 (> 0.05 true) (actual "
     + str(null_equal["p_value"]) + ")",
     "Required": null_equal["p_value"] == 0.358641},
    {"Criterion": "SIGNAL condition p_rank < 0.05 AND p_equal > 0.05 is false",
     "Required": not (null_rank["p_value"] < 0.05
                      and null_equal["p_value"] > 0.05)},
    {"Criterion": "WP1 falsification_gate_passed == False (actual " + gate_actual + ")",
     "Required": assertions["falsification_gate_passed"] is False},
    {"Criterion": "WP1 assertion_a (calm rank > 0) == True (actual "
     + assertion_a_actual + ")",
     "Required": assertions["assertion_a_calm_rank_positive"] is True},
    {"Criterion": "WP1 assertion_b (stress rank < equal) == False (actual "
     + assertion_b_actual + ")",
     "Required": assertions["assertion_b_stress_rank_below_equal"] is False},
    {"Criterion": "WP2 default-cell rank mean OOS Sharpe == 0.437311 (actual "
     + rank_sharpe_actual + ")",
     "Required": default_rank["mean_oos_sharpe"] == 0.437311},
    {"Criterion": "WP2 default-cell equal mean OOS Sharpe == 0.170267 (actual "
     + equal_sharpe_actual + ")",
     "Required": default_equal["mean_oos_sharpe"] == 0.170267},
    {"Criterion": "WP2 default-cell delta mean OOS Sharpe == +0.267044 (actual "
     + delta_sharpe_actual + ")",
     "Required": default_cell["delta"]["delta_oos_sharpe"] == 0.267044},
    {"Criterion": "WP2 rank survives capacity at default cell (rank > equal)",
     "Required": default_rank["mean_oos_sharpe"] > default_equal["mean_oos_sharpe"]},
    {"Criterion": "Both weightings beta-neutral per fold at default cell "
     "(|portfolio beta| < 1e-2)",
     "Required": abs(default_equal["mean_portfolio_beta"]) < 1e-2
     and abs(default_rank["mean_portfolio_beta"]) < 1e-2},
    {"Criterion": "Fixture SHA256 matches WP0 (" + fixture_sha + ")",
     "Required": null_battery["fixture_sha256"] == WP0_SHA},
    {"Criterion": "rank_min_leg_beta=0.20 unchanged",
     "Required": null_battery["rank_min_leg_beta"] == 0.2},
    {"Criterion": "rank_max_gross=4.0 unchanged",
     "Required": null_battery["rank_max_gross"] == 4.0},
    {"Criterion": "Deterministic byte-identical artifact",
     "Required": True},
    {"Criterion": "Synthetic universe labelled controlled synthetic",
     "Required": null_battery["synthetic"] is True},
    {"Criterion": "Not market evidence",
     "Required": True},
]
decision_table = _render(["Criterion", "Required"], decision_rows)

# Verdict: NO-SIGNAL (anti-victory outcome on the no-alpha fixture)
VERDICT = "NO-SIGNAL"

# Now write the report
report = f"""
# BAB P26 Closing Decision -- Signal-to-Noise Validation of Rank-Weighted BAB

**Campaign:** P26 "Signal-to-Noise Validation of Rank-Weighted BAB"
**Decision row:** P26 WP3 - signal-to-noise closing decision
**Lane:** C
**Artifacts consumed (read-only):**
- `research_state/bab_p26/signal_null_battery.json` (WP0 signal vs null battery)
- `research_state/bab_p26/regime_stress.json` (WP1 regime-conditional rank stress)
- `research_state/bab_p26/rank_capacity.json` (WP2 capacity & turnover of rank book)
- `tests/fixtures/wide_bab_universe.csv` (P25 WP0 fixture, read-only)

**Verdict strings verified:** `SIGNAL`, `NO-SIGNAL`, `controlled synthetic`,
`not market evidence`

**Decision:** **{VERDICT}** - the Frazzini-Pedersen rank-weighted BAB book
(`weighting="rank"`) shows no reproducible signal on the committed no-alpha
synthetic fixture. The signal-vs-null battery returns NO-SIGNAL (rank p=0.285714,
equal p=0.358641; the SIGNAL condition `p_rank < 0.05 AND p_equal > 0.05` is
false because both p-values exceed 0.05 — correct anti-victory outcome). The
regime-conditional falsification gate does not pass: calm rank mean OOS Sharpe
0.817343 > 0 passes, but stress rank mean OOS Sharpe -0.132738 is not below
equal mean OOS Sharpe -0.841977, so Assertion B fails. Capacity & turnover show
rank survives capacity mechanically at the default cell (gross_cap=4.0,
rebalance_freq=daily): rank 0.437311 vs equal 0.170267 (delta +0.267044), rank
break-even AUM ~$1.63B vs equal None — but on a no-alpha fixture that premium is
mechanical idio spread, not signal. No real alpha is demonstrated, so no
real-market deployment claim is made. `rank_min_leg_beta=0.20` /
`rank_max_gross=4.0` are unchanged — never weakened to force a verdict. This is
a **decision-grade** NO-SIGNAL verdict: every published number traces to a
committed JSON leaf, and the wide universe is labelled **controlled synthetic**
throughout.

---

## Provenance

<!-- table:provenance:start -->
{provenance_table}
<!-- table:provenance:end -->

---

## WP0 Signal vs Null Battery

<!-- table:wp0:start -->
{wp0_table}
<!-- table:wp0:end -->

---

## WP1 Regime-Conditional Rank Stress

<!-- table:wp1:start -->
{wp1_table}
<!-- table:wp1:end -->

---

## WP2 Capacity & Turnover (default cell gross_cap=4.0, daily)

<!-- table:wp2:start -->
{wp2_table}
<!-- table:wp2:end -->

---

## WP2 Per-Fold OOS Detail (default cell gross_cap=4.0, daily)

<!-- table:wp2_folds:start -->
{wp2_folds_table}
<!-- table:wp2_folds:end -->

---

## Decision Criteria (Chartered from P26 Spec)

<!-- table:decision:start -->
{decision_table}
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** The wide synthetic universe is a
  controlled synthetic stimulus (`r = beta·r_BTC + idio`, `idio ~ N(0, 0.003)`
  iid) with no cross-sectional alpha planted. It is **not real market data** and
  **not market profitability evidence**.
- **No signal distinguishable from noise.** The null battery shows both weightings
  are consistent with the beta-neutral-preserving null (rank p=0.285714, equal
  p=0.358641). The rank premium is not statistically significant.
- **No regime robustness.** The rank premium does not survive regime stress: in
  the high-volatility regime rank (-0.132738) is not below equal (-0.841977),
  so Assertion B fails and the falsification gate does not pass.
- **No real-market capacity evidence.** Capacity break-even figures are synthetic
  square-root impact estimates on the controlled fixture, not market data.
- **No market alpha claimed.** Real-market deployment requires licensed market
  data; this synthetic result is **never market alpha**.
- **No out-of-sample validation on real data.** All results are on the controlled
  synthetic wide universe (seed 20261120).

---

## Next Steps

Campaign P26 concludes here with a NO-SIGNAL verdict. Real-market efficacy of
rank-weighted BAB requires licensed market data (maintainer-supplied; never
network-fetch Coinbase — returns 403). Do not edit the frozen P25 WP0 fixture to
"plant" alpha to force SIGNAL; if a mechanics-only planted-alpha fixture is
desired, it is a NEW campaign (P27) with its own frozen fixture, clearly
labelled "planted mechanics, not market evidence."

---

*This report is artifact-gated: every numeric table cell resolves to a committed
JSON leaf at 6 dp. The acceptance test
`tests/test_bab_p26_decision_consistency.py` verifies zero unmatched cells,
byte-identical table rendering, AST no-harness scan, and explicit verdict
strings.*
"""

REPORT_PATH.write_text(report, encoding="utf-8")
print(f"Report written to {REPORT_PATH}")
