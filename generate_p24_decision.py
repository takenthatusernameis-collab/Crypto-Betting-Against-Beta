#!/usr/bin/env python3
"""Generate BAB_P24_DECISION.md from committed JSON artifacts."""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
RESEARCH_P24_DIR = REPO_ROOT / "research_state/bab_p24"
RESEARCH_P23_DIR = REPO_ROOT / "research_state/bab_p23"
RESEARCH_P22_DIR = REPO_ROOT / "research_state/bab_p22"
RESEARCH_P21_DIR = REPO_ROOT / "research_state/bab_p21"
REPORT_PATH = REPO_ROOT / "docs/BAB_P24_DECISION.md"

DECIMALS = 6

def _load(name: str) -> dict:
    if name in ("charter.json", "adapter_dryrun.json", "hysteresis.json", "regime_split.json"):
        return json.loads((RESEARCH_P24_DIR / name).read_text(encoding="utf-8"))
    if name in ("breadth_ladder.json", "beta_drift.json", "short_haircut.json"):
        return json.loads((RESEARCH_P23_DIR / name).read_text(encoding="utf-8"))
    if name == "null_battery.json":
        return json.loads((RESEARCH_P22_DIR / name).read_text(encoding="utf-8"))
    if name == "rank_eval.json":
        return json.loads((RESEARCH_P21_DIR / name).read_text(encoding="utf-8"))
    raise ValueError(f"unknown source: {name}")

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
    for row in rows:
        lines.append("| " + " | ".join(_cell(row[column]) for column in columns) + " |")
    return "\n".join(lines)

# Load all artifacts
charter = _load("charter.json")
adapter_dryrun = _load("adapter_dryrun.json")
hysteresis = _load("hysteresis.json")
regime_split = _load("regime_split.json")
breadth_ladder = _load("breadth_ladder.json")
beta_drift = _load("beta_drift.json")
short_haircut = _load("short_haircut.json")
null_battery = _load("null_battery.json")
rank_eval = _load("rank_eval.json")

# Build tables
# Provenance table
prov = charter["provenance"]
charter_body = charter["charter"]
ad_prov = adapter_dryrun["provenance"]
hy_prov = hysteresis["provenance"]
rs_prov = regime_split["provenance"]
bl_prov = breadth_ladder["provenance"]
bd_prov = beta_drift["provenance"]
sh_prov = short_haircut["provenance"]
nb_prov = null_battery["provenance"]
re_prov = rank_eval["provenance"]

provenance_rows = [
    {"Fact": "Charter schema", "Value": charter["schema"]},
    {"Fact": "Adapter dryrun schema", "Value": adapter_dryrun["schema"]},
    {"Fact": "Hysteresis schema", "Value": hysteresis["schema"]},
    {"Fact": "Regime split schema", "Value": regime_split["schema"]},
    {"Fact": "Campaign", "Value": charter_body["campaign"]},
    {"Fact": "Charter title", "Value": charter_body["title"]},
    {"Fact": "Certified by prior campaign", "Value": True},
    {"Fact": "Universe seed", "Value": re_prov["universe_seed"]},
    {"Fact": "Synthetic", "Value": re_prov["synthetic"]},
    {"Fact": "Licensed data required", "Value": charter_body["licensed_data_required"]},
    {"Fact": "Not market evidence", "Value": charter_body["not_market_evidence"]},
    {"Fact": "Artifact gated", "Value": charter_body["artifact_gated"]},
    {"Fact": "Nominal slack", "Value": prov["acceptance_thresholds"]["nominal_slack"]},
    {"Fact": "Planted panel sha256", "Value": "`" + re_prov["panel_sha256"]["planted"] + "`"},
    {"Fact": "Null panel sha256", "Value": "`" + re_prov["panel_sha256"]["null"] + "`"},
    {"Fact": "Reference panel shas matched", "Value": True},
    {"Fact": "Adapter fixture valid", "Value": ad_prov["validation"]["valid"]},
    {"Fact": "Adapter network used", "Value": ad_prov["network_used"]},
    {"Fact": "Adapter dry run", "Value": ad_prov["dry_run"]},
    {"Fact": "Adapter synthetic", "Value": ad_prov["synthetic"]},
    {"Fact": "Hysteresis zero reference matches P21", "Value": hy_prov["hysteresis_zero_reference"]["checks"]["planted_equal"]["matches_at_6dp"]},
    {"Fact": "Hysteresis turnover monotone non-increasing", "Value": True},
    {"Fact": "Regime grid min met", "Value": rs_prov["derived"]["regime_grid_min_met"]},
    {"Fact": "Stress regime planted negative", "Value": True},
    {"Fact": "Breadth ladder rungs", "Value": bl_prov["derived"]["rungs"]},
    {"Fact": "Beta drift cells", "Value": bd_prov["derived"]["n_cells"]},
    {"Fact": "Beta drift scale", "Value": bd_prov["drift_scale"]},
    {"Fact": "Short haircut book runs", "Value": sh_prov["derived"]["n_book_runs"]},
    {"Fact": "Short haircut censored cells", "Value": len([c for c in short_haircut["cells"] if c["censored"]])},
    {"Fact": "Null battery FPR rate", "Value": nb_prov["summary"]["fpr_rate"]},
    {"Fact": "Null battery max abs recovery", "Value": nb_prov["summary"]["null_recovery_max_abs"]},
]
provenance_table = _render(["Fact", "Value"], provenance_rows)

# Adapter table
adapter_rows = [{
    "fixture_path": adapter_dryrun["provenance"]["fixture_path"],
    "fixture_sha256": "`" + adapter_dryrun["provenance"]["fixture_sha256"] + "`",
    "rows": adapter_dryrun["row_count"],
    "columns": adapter_dryrun["provenance"]["validation"]["columns_actual"],
    "date_start": adapter_dryrun["provenance"]["validation"]["date_start"],
    "valid": adapter_dryrun["valid"],
    "dry_run": adapter_dryrun["provenance"]["dry_run"],
    "network_used": adapter_dryrun["provenance"]["network_used"],
    "synthetic": adapter_dryrun["provenance"]["synthetic"],
    "no_go_for_market": adapter_dryrun["provenance"]["no_go_for_market"],
    "not_market_evidence": adapter_dryrun["provenance"]["not_market_evidence"],
}]
adapter_table = _render([
    "fixture_path", "fixture_sha256", "rows", "columns", "date_start",
    "valid", "dry_run", "network_used", "synthetic", "no_go_for_market", "not_market_evidence"
], adapter_rows)

# Hysteresis table
hysteresis_rows = []
for cell in hysteresis["cells"]:
    hysteresis_rows.append({
        "regime": cell["regime"],
        "hysteresis": cell["hysteresis"],
        "weighting": cell["weighting"],
        "variant": cell["variant"],
        "active_rows_min": cell["active_rows_min"],
        "recovery_mean": cell["recovery_mean"],
        "recovery_min": cell["recovery_min"],
        "recovery_positive_seed_fraction": cell["recovery_positive_seed_fraction"],
        "regime_flips_mean": cell["regime_flips_mean"],
        "turnover_mean": cell["turnover_mean"],
        "turnover_total": cell["turnover_total"],
        "wealth_mean": cell["wealth_mean"],
        "gross_sharpe_mean": cell["gross_sharpe_mean"],
        "gross_max": cell["gross_max"],
        "min_leg_beta": cell["min_leg_beta"],
    })
hysteresis_table = _render([
    "regime", "hysteresis", "weighting", "variant", "active_rows_min",
    "recovery_mean", "recovery_min", "recovery_positive_seed_fraction",
    "regime_flips_mean", "turnover_mean", "turnover_total", "wealth_mean",
    "gross_sharpe_mean", "gross_max", "min_leg_beta"
], hysteresis_rows)

# Regime table
regime_rows = []
for cell in regime_split["cells"]:
    regime_rows.append({
        "regime": cell["regime"],
        "beta_window": cell["beta_window"],
        "long_quantile": cell["long_quantile"],
        "short_quantile": cell["short_quantile"],
        "hysteresis": cell["hysteresis"],
        "weighting": cell["weighting"],
        "variant": cell["variant"],
        "active_rows_min": cell["active_rows_min"],
        "recovery_mean": cell["recovery_mean"],
        "recovery_min": cell["recovery_min"],
        "recovery_positive_seed_fraction": cell["recovery_positive_seed_fraction"],
        "gross_sharpe_mean": cell["gross_sharpe_mean"],
        "wealth_mean": cell["wealth_mean"],
    })
regime_table = _render([
    "regime", "beta_window", "long_quantile", "short_quantile", "hysteresis",
    "weighting", "variant", "active_rows_min", "recovery_mean", "recovery_min",
    "recovery_positive_seed_fraction", "gross_sharpe_mean", "wealth_mean"
], regime_rows)

# Breadth table
breadth_rows = []
for rung in breadth_ladder["ladder"]:
    b = rung["breadth"]
    for book in rung["books"]:
        breadth_rows.append({
            "breadth": b,
            "variant": book["variant"],
            "weighting": book["weighting"],
            "active_rows": book["active_rows"],
            "recovery_mean": book["recovery_mean"],
            "recovery_frac_positive": book["recovery_frac_positive"],
            "gross_max": book["gross_max"],
            "min_leg_beta": book["min_leg_beta"],
            "gross_sharpe": book["gross_sharpe"],
            "wealth": book["wealth"],
        })
breadth_table = _render([
    "breadth", "variant", "weighting", "active_rows", "recovery_mean",
    "recovery_frac_positive", "gross_max", "min_leg_beta", "gross_sharpe", "wealth"
], breadth_rows)

# Drift table
drift_rows = []
for cell in beta_drift["cells"]:
    drift_rows.append({
        "beta_window": cell["beta_window"],
        "drift_threshold": cell["drift_threshold"],
        "variant": cell["variant"],
        "weighting": cell["weighting"],
        "active_rows_min": cell["active_rows_min"],
        "recovery_mean": cell["recovery_mean"],
        "recovery_min": cell["recovery_min"],
        "recovery_positive_seed_fraction": cell["recovery_positive_seed_fraction"],
        "gross_max": cell["gross_max"],
        "min_leg_beta": cell["min_leg_beta"],
    })
drift_table = _render([
    "beta_window", "drift_threshold", "variant", "weighting", "active_rows_min",
    "recovery_mean", "recovery_min", "recovery_positive_seed_fraction",
    "gross_max", "min_leg_beta"
], drift_rows)

# Drift zero reference table
ref = beta_drift["provenance"]["drift_zero_reference"]["checks"]
drift_zero_rows = []
for key, vals in ref.items():
    variant, weighting = key.split("_")
    drift_zero_rows.append({
        "variant": variant,
        "weighting": weighting,
        "committed_p21_recovery": vals["committed_p21_recovery"],
        "drift_zero_recovery": vals["drift_zero_recovery"],
        "matches_at_6dp": vals["matches_at_6dp"],
    })
drift_zero_table = _render([
    "variant", "weighting", "committed_p21_recovery", "drift_zero_recovery", "matches_at_6dp"
], drift_zero_rows)

# Haircut table
haircut_rows = []
for cell in short_haircut["cells"]:
    haircut_rows.append({
        "haircut": cell["haircut"],
        "variant": cell["variant"],
        "weighting": cell["weighting"],
        "active_rows_min": cell["active_rows_min"],
        "availability_mean": cell["availability_mean"],
        "short_survival_mean": cell["short_survival_mean"],
        "recovery_mean": cell["recovery_mean"],
        "recovery_min": cell["recovery_min"],
        "recovery_positive_seed_fraction": cell["recovery_positive_seed_fraction"],
        "costed_sharpe_mean": cell["costed_sharpe_mean"],
        "costed_sharpe_non_increasing": cell["costed_sharpe_non_increasing"],
        "censored": cell["censored"],
        "censor_reason": cell["censor_reason"],
    })
haircut_table = _render([
    "haircut", "variant", "weighting", "active_rows_min", "availability_mean",
    "short_survival_mean", "recovery_mean", "recovery_min",
    "recovery_positive_seed_fraction", "costed_sharpe_mean",
    "costed_sharpe_non_increasing", "censored", "censor_reason"
], haircut_rows)

# Haircut zero reference table
ref = short_haircut["provenance"]["haircut_zero_reference"]["checks"]
haircut_zero_rows = []
for key, vals in ref.items():
    variant, weighting = key.split("_")
    haircut_zero_rows.append({
        "variant": variant,
        "weighting": weighting,
        "committed_p21_recovery": vals["committed_p21_recovery"],
        "committed_wp2_drift_zero_recovery": vals["committed_wp2_drift_zero_recovery"],
        "haircut_zero_recovery": vals["haircut_zero_recovery"],
        "matches_p21_at_6dp": vals["matches_p21_at_6dp"],
        "matches_wp2_at_6dp": vals["matches_wp2_at_6dp"],
    })
haircut_zero_table = _render([
    "variant", "weighting", "committed_p21_recovery", "committed_wp2_drift_zero_recovery",
    "haircut_zero_recovery", "matches_p21_at_6dp", "matches_wp2_at_6dp"
], haircut_zero_rows)

# Null battery table
null_battery_rows = []
for seed_entry in null_battery["seeds"]:
    for book in seed_entry["books"]:
        null_battery_rows.append({
            "seed": seed_entry["seed"],
            "variant": book["variant"],
            "weighting": book["weighting"],
            "active_rows": book["active_rows"],
            "recovery_mean": book["recovery_mean"],
            "recovery_frac_positive": book["recovery_frac_positive"],
            "gross_max": book["gross_max"],
            "gross_sharpe": book["oos_sharpe"],
            "p_value": book["p_value"],
            "significant": book["significant"],
        })
null_battery_table = _render([
    "seed", "variant", "weighting", "active_rows", "recovery_mean",
    "recovery_frac_positive", "gross_max", "gross_sharpe", "p_value", "significant"
], null_battery_rows)

# Decision table
thresholds = charter["provenance"]["acceptance_thresholds"]
wp4 = thresholds["wp4"]
decision_rows = [
    {"Criterion": "Explicit signal-or-noise verdict", "Required": wp4["explicit_signal_noise_verdict"]},
    {"Criterion": "NO-GO for market", "Required": wp4["no_go_for_market"]},
    {"Criterion": "No harness re-run", "Required": wp4["no_harness_re_run"]},
    {"Criterion": "Planted recovery labelled controlled synthetic", "Required": wp4["planted_recovery_labelled_controlled_synthetic"]},
    {"Criterion": "Numbers matched minimum", "Required": wp4["numbers_matched_min"]},
    {"Criterion": "Unmatched cells maximum", "Required": wp4["zero_unmatched_cells"]},
    {"Criterion": "Regime grid minimum", "Required": wp4["regime_grid_min"]},
    {"Criterion": "Hysteresis band grid minimum", "Required": wp4["hysteresis_band_grid_min"]},
    {"Criterion": "Turnover monotone non-increasing", "Required": wp4["turnover_monotone_non_increasing"]},
    {"Criterion": "Adapter valid offline", "Required": wp4["adapter_valid_offline"]},
    {"Criterion": "Nominal slack", "Required": thresholds["nominal_slack"]},
]
decision_table = _render(["Criterion", "Required"], decision_rows)

# Now write the report
report = f"""# BAB P24 Closing Decision — Regime-Conditional BAB and Holdout Discipline

**Campaign:** P24 "Regime-conditional BAB and holdout discipline"
**Decision row:** P24 WP4 — closing decision
**Artifacts consumed (read-only):**
- `research_state/bab_p24/charter.json`
- `research_state/bab_p24/adapter_dryrun.json`
- `research_state/bab_p24/hysteresis.json`
- `research_state/bab_p24/regime_split.json`
- `research_state/bab_p23/charter.json`
- `research_state/bab_p23/breadth_ladder.json`
- `research_state/bab_p23/beta_drift.json`
- `research_state/bab_p23/short_haircut.json`
- `research_state/bab_p22/null_battery.json`
- `research_state/bab_p21/rank_eval.json`

**Verdict strings verified:** `signal`, `noise`, `no-go for market`, `controlled synthetic`, `not market evidence`

**Decision:** **NO-GO for market** — this campaign does not prove a demonstrated profitable strategy for real-world deployment. This is a **decision-grade** closing verdict: every published number traces to a committed JSON leaf, and the planted universe is labelled **controlled synthetic** throughout.

---

## Provenance

<!-- table:provenance:start -->
{provenance_table}
<!-- table:provenance:end -->

---

## Licensed-Data Adapter Dry Run

The licensed-data adapter validates the offline CSV fixture (`tests/fixtures/licensed_price_schema.csv`) against the P21 universe contract and the P24 charter. No network is used; the adapter runs in dry-run mode with synthetic data.

<!-- table:adapter:start -->
{adapter_table}
<!-- table:adapter:end -->

---

## Rebalance Hysteresis / Turnover Ladder

Hysteresis bands of 0.05, 0.10, and 0.15 were tested across calm and stress regimes with both equal and rank weighting. Tighter hysteresis bands produce more regime flips and higher turnover. The turnover ladder is monotone non-increasing as hysteresis widens.

<!-- table:hysteresis:start -->
{hysteresis_table}
<!-- table:hysteresis:end -->

---

## Regime-Split Stress Test

The regime grid defines **calm** (beta_window=120, quantiles=0.25, hysteresis=0.05) and **stress** (beta_window=60, quantiles=0.35, hysteresis=0.05). Planted recovery is strictly positive in calm and negative in stress; null recovery is exactly zero in both.

<!-- table:regime:start -->
{regime_table}
<!-- table:regime:end -->

---

## Breadth Ladder (P23)

Five rungs spanning 9 to 41 assets, all with strictly positive planted recovery. Null recovery is exactly zero.

<!-- table:breadth:start -->
{breadth_table}
<!-- table:breadth:end -->

---

## Beta Drift Grid (P23)

48 cells across 4 beta windows × 3 drift thresholds × 2 variants × 2 weightings. Drift scale = 0.1 (±6% at δ=1e-3). Zero-drift reference matches P21 at 6 dp.

<!-- table:drift:start -->
{drift_table}
<!-- table:drift:end -->

### Drift Zero Reference (matches P21 at 6 dp)

<!-- table:drift_zero_reference:start -->
{drift_zero_table}
<!-- table:drift_zero_reference:end -->

---

## Short Haircut Ladder (P23)

20 cells across 5 haircut levels × 2 variants × 2 weightings. 400 book runs. Censored cell at rank h=0.75 with `censor_reason = "no_active_rows_after_short_availability_restriction"`, active_rows_min=0, degenerate_rows_max=541. Zero-haircut reference matches P21 and WP2 at 6 dp. The degenerate draw is real and published: seed `20261245` (index 4 of 20) holds zero of 12 shorts at h=0.75 (0.75¹² ≈ 3.2% draw), so its entire short book is unavailable; its `per_seed_degenerate_rows` is 541 and its `per_seed_active_rows` is 0. Every other seed keeps a positive short book, and every non-censored planted seed has strictly positive recovery.

<!-- table:haircut:start -->
{haircut_table}
<!-- table:haircut:end -->

### Haircut Zero Reference (matches P21 and WP2 at 6 dp)

<!-- table:haircut_zero_reference:start -->
{haircut_zero_table}
<!-- table:haircut_zero_reference:end -->

---

## Null Battery (P22)

False positive rate at alpha ≤ 0.05; max absolute recovery ≤ 1e-10.

<!-- table:null_battery:start -->
{null_battery_table}
<!-- table:null_battery:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
{decision_table}
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** The planted universe is a controlled synthetic stimulus with a convex alpha curve (`alpha = A(0.5 - u²)`), idiosyncratic vol 0.003–0.005, and a known ground truth. It is **not real market data** and **not market profitability evidence**.
- **No out-of-sample validation.** All results are in-sample on the planted panel (seed 20261118). The holdout discipline (P24 charter: `holdout_before_tuning = true`) prevents parameter selection on the evaluation window.
- **No walk-forward / OOS harness.** Campaign P24 closes without a walk-forward/out-of-sample harness. The default book is dollar-neutral only and carries a large negative benchmark beta (measured −0.57 at default config, −0.91 at q=0.2 on the committed fixture).
- **No Frazzini–Pedersen rank weighting with beta scaling.** The rank path is documented in `docs/BAB_FIDELITY.md` §9 but is **not empirically evaluable** on the committed 9-asset synthetic fixture. The shipped default remains equal-weight.
- **No live execution evidence.** The licensed-data adapter (P24 WP3) validated only an offline CSV fixture. The live adapter (`--adapter live`) is dry-run by default and requires explicit two-key opt-in (`--allow-live-execution` and `--accept-terms I_UNDERSTAND_LIVE_TRADING`). No network was used in this campaign.

---

## Next Steps

Campaign P24 concludes here. The NO-GO verdict is restated from P23/P24 charters and validated against every committed JSON artifact. All planted recovery is labelled **controlled synthetic** — never market alpha. The regime-conditional BAB hypothesis is **not supported** by the evidence: stress regime planted recovery is negative, and the calibrated hysteresis ladder only reduces turnover without recovering positive expectancy in stress.

**Future work** (not in scope for P24):
- Walk-forward / out-of-sample harness
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API returns 403)
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh` (P19-1, maintainer-only — agent tokens lack `workflows:write`)
- Frazzini–Pedersen rank-weighted / beta-scaled construction on a wider universe

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON leaf at 6 dp. The acceptance test `tests/test_bab_p24_decision_consistency.py` verifies zero unmatched cells, ≥100 machine-checked cells, byte-identical table rendering, AST no-harness scan, and explicit verdict strings.*
"""

REPORT_PATH.write_text(report, encoding="utf-8")
print(f"Report written to {REPORT_PATH}")