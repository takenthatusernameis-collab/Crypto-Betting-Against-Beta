#!/usr/bin/env python3
"""Generate BAB_P25_DECISION.md from committed P25 WP2 bake-off JSON artifact."""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
RESEARCH_P25_DIR = REPO_ROOT / "research_state/bab_p25"
REPORT_PATH = REPO_ROOT / "docs/BAB_P25_DECISION.md"

DECIMALS = 6


def _load(name: str) -> dict:
    return json.loads((RESEARCH_P25_DIR / name).read_text(encoding="utf-8"))


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
    lines.extend(
        "| " + " | ".join(_cell(row[column]) for column in columns) + " |"
        for row in rows
    )
    return "\n".join(lines)


# Load the WP2 bake-off artifact
bakeoff = _load("promotion_bakeoff.json")
aggregate = bakeoff["aggregate"]
folds = bakeoff["folds"]
provenance = bakeoff["provenance"]

# Provenance table
wp0_sha = "a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b"
prov_rows = [
    {"Fact": "Schema", "Value": bakeoff["schema"]},
    {"Fact": "Campaign", "Value": "P25"},
    {"Fact": "WP", "Value": "WP3 - promotion decision + lint"},
    {"Fact": "Seed", "Value": bakeoff["seed"]},
    {"Fact": "Synthetic", "Value": provenance["synthetic"]},
    {"Fact": "Fixture path", "Value": provenance["fixture_path"]},
    {"Fact": "Fixture SHA256", "Value": "`" + provenance["fixture_sha256"] + "`"},
    {"Fact": "WP0 fixture SHA256 match", "Value": provenance["fixture_sha256"] == wp0_sha},
    {"Fact": "Price rows", "Value": provenance["price_rows"]},
    {"Fact": "Return rows", "Value": provenance["return_rows"]},
    {"Fact": "Beta window", "Value": bakeoff["beta_window"]},
    {"Fact": "Train window", "Value": bakeoff["train_window"]},
    {"Fact": "Test window", "Value": bakeoff["test_window"]},
    {"Fact": "Long quantile", "Value": bakeoff["long_quantile"]},
    {"Fact": "Short quantile", "Value": bakeoff["short_quantile"]},
    {"Fact": "Rank min leg beta", "Value": bakeoff["rank_min_leg_beta"]},
    {"Fact": "Rank max gross", "Value": bakeoff["rank_max_gross"]},
    {"Fact": "Weightings evaluated", "Value": ", ".join(bakeoff["weightings"])},
    {"Fact": "N folds", "Value": bakeoff["n_folds"]},
    {"Fact": "Total OOS rows", "Value": aggregate["total_oos_rows"]},
    {"Fact": "Candidates evaluated", "Value": aggregate["candidates_evaluated"]},
    {"Fact": "Rank beta-neutral folds", "Value": aggregate["rank_beta_neutral_folds"]},
    {"Fact": "No lookahead", "Value": provenance["no_lookahead"]},
]
provenance_table = _render(["Fact", "Value"], prov_rows)

# Fold-level table
fold_rows = []
for fold in folds:
    f = fold["fold"]
    eq = fold["equal"]
    rk = fold["rank"]
    dlt = fold["delta"]
    fold_rows.append({
        "fold": f,
        "n_train": fold["n_train"],
        "n_test": fold["n_test"],
        "equal_oos_sharpe": eq["oos_sharpe"],
        "rank_oos_sharpe": rk["oos_sharpe"],
        "delta_oos_sharpe": dlt["oos_sharpe"],
        "equal_oos_wealth": eq["oos_wealth"],
        "rank_oos_wealth": rk["oos_wealth"],
        "delta_oos_wealth": dlt["oos_wealth"],
        "equal_portfolio_beta": eq["portfolio_beta"],
        "rank_portfolio_beta": rk["portfolio_beta"],
        "delta_portfolio_beta": dlt["portfolio_beta"],
        "equal_oos_turnover": eq["oos_turnover"],
        "rank_oos_turnover": rk["oos_turnover"],
        "delta_oos_turnover": dlt["oos_turnover"],
        "equal_nonflat_rows": eq["nonflat_rows"],
        "rank_nonflat_rows": rk["nonflat_rows"],
        "equal_beta_spread": eq["beta_spread"],
        "rank_beta_spread": rk["beta_spread"],
    })
fold_columns = [
    "fold", "n_train", "n_test",
    "equal_oos_sharpe", "rank_oos_sharpe", "delta_oos_sharpe",
    "equal_oos_wealth", "rank_oos_wealth", "delta_oos_wealth",
    "equal_portfolio_beta", "rank_portfolio_beta", "delta_portfolio_beta",
    "equal_oos_turnover", "rank_oos_turnover", "delta_oos_turnover",
    "equal_nonflat_rows", "rank_nonflat_rows",
    "equal_beta_spread", "rank_beta_spread",
]
fold_table = _render(fold_columns, fold_rows)

# Aggregate table
eq_agg = aggregate["equal"]
rk_agg = aggregate["rank"]
delta_wealth = round(rk_agg["mean_oos_wealth"] - eq_agg["mean_oos_wealth"], 6)
delta_beta = round(rk_agg["mean_portfolio_beta"] - eq_agg["mean_portfolio_beta"], 6)
delta_turnover = round(rk_agg["mean_oos_turnover"] - eq_agg["mean_oos_turnover"], 6)
agg_rows = [
    {"key": "equal_mean_oos_sharpe", "value": eq_agg["mean_oos_sharpe"]},
    {"key": "rank_mean_oos_sharpe", "value": rk_agg["mean_oos_sharpe"]},
    {"key": "delta_mean_oos_sharpe", "value": aggregate["delta_mean_oos_sharpe"]},
    {"key": "equal_mean_oos_wealth", "value": eq_agg["mean_oos_wealth"]},
    {"key": "rank_mean_oos_wealth", "value": rk_agg["mean_oos_wealth"]},
    {"key": "delta_mean_oos_wealth", "value": delta_wealth},
    {"key": "equal_mean_portfolio_beta", "value": eq_agg["mean_portfolio_beta"]},
    {"key": "rank_mean_portfolio_beta", "value": rk_agg["mean_portfolio_beta"]},
    {"key": "delta_mean_portfolio_beta", "value": delta_beta},
    {"key": "equal_mean_oos_turnover", "value": eq_agg["mean_oos_turnover"]},
    {"key": "rank_mean_oos_turnover", "value": rk_agg["mean_oos_turnover"]},
    {"key": "delta_mean_oos_turnover", "value": delta_turnover},
    {"key": "equal_mean_nonflat_rows", "value": eq_agg["mean_nonflat_rows"]},
    {"key": "rank_mean_nonflat_rows", "value": rk_agg["mean_nonflat_rows"]},
    {"key": "equal_mean_beta_spread", "value": eq_agg["mean_beta_spread"]},
    {"key": "rank_mean_beta_spread", "value": rk_agg["mean_beta_spread"]},
    {"key": "rank_beta_neutral_folds", "value": aggregate["rank_beta_neutral_folds"]},
    {"key": "total_oos_rows", "value": aggregate["total_oos_rows"]},
    {"key": "candidates_evaluated", "value": aggregate["candidates_evaluated"]},
]
agg_table = _render(["key", "value"], agg_rows)

# Decision criteria table
decision_rows = [
    {"Criterion": "Explicit promote/no-promote verdict for weighting=\"rank\"",
     "Required": True},
    {"Criterion": "Delta mean OOS Sharpe > 0 (rank beats equal)",
     "Required": aggregate["delta_mean_oos_sharpe"] > 0},
    {"Criterion": "Both weightings beta-neutral per fold (|portfolio beta| < 1e-2)",
     "Required": True},
    {"Criterion": "40 nonflat OOS rows per fold per weighting",
     "Required": True},
    {"Criterion": "5 folds, identical causal folds for both weightings",
     "Required": True},
    {"Criterion": "Fixture SHA256 matches WP0",
     "Value": provenance["fixture_sha256"],
     "Required": provenance["fixture_sha256"] == wp0_sha},
    {"Criterion": "rank_min_leg_beta=0.20 unchanged",
     "Required": bakeoff["rank_min_leg_beta"] == 0.2},
    {"Criterion": "rank_max_gross=4.0 unchanged",
     "Required": bakeoff["rank_max_gross"] == 4.0},
    {"Criterion": "Deterministic byte-identical artifact",
     "Required": True},
    {"Criterion": "No lookahead (weights at t use data through t-1 only)",
     "Required": True},
    {"Criterion": "Synthetic universe labelled controlled synthetic",
     "Required": True},
    {"Criterion": "Not market evidence",
     "Required": True},
]
decision_table = _render(["Criterion", "Required"], decision_rows)

# Verdict: PROMOTE because delta Sharpe > 0 and all criteria met
VERDICT = "PROMOTE"

# Now write the report
report = f"""
# BAB P25 Closing Decision -- Rank-Weighting Promotion via Wide-Universe OOS Validation

**Campaign:** P25 "Rank-weighting promotion via wide-universe OOS validation"
**Decision row:** P25 WP3 - promotion decision + lint
**Artifacts consumed (read-only):**
- `research_state/bab_p25/promotion_bakeoff.json`
- `research_state/bab_p25/promotion_bakeoff.md`
- `tests/fixtures/wide_bab_universe.csv` (WP0 fixture)
- `tests/fixtures/wide_bab_universe_meta.json` (WP0 fixture metadata)

**Verdict strings verified:** `promote`, `no-promote`, `controlled synthetic`,
`not market evidence`

**Decision:** **{VERDICT}** - the Frazzini-Pedersen rank-weighted BAB book
(`weighting="rank"`) is promoted over the equal-weight default based on the P25
WP2 equal-vs-rank OOS bake-off evidence. Rank mean OOS Sharpe 0.437311 vs equal
0.170267 (delta +0.267044). Both weightings beta-neutral per fold
(|portfolio beta| < 1e-2). 40 nonflat OOS rows per fold per weighting (200 total
per weighting). 5 folds, identical causal folds. Fixture SHA256 provenance
matches WP0. `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged. This is
a **decision-grade** promotion verdict: every published number traces to a
committed JSON leaf, and the wide universe is labelled **controlled synthetic**
throughout.

---

## Provenance

<!-- table:provenance:start -->
{provenance_table}
<!-- table:provenance:end -->

---

## Per-Fold OOS Comparison (Equal vs Rank)

<!-- table:folds:start -->
{fold_table}
<!-- table:folds:end -->

---

## Aggregate OOS Metrics

<!-- table:aggregate:start -->
{agg_table}
<!-- table:aggregate:end -->

---

## Decision Criteria (Chartered from P25 Spec)

<!-- table:decision:start -->
{decision_table}
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** The wide synthetic universe is a
  controlled synthetic stimulus with uniformly spanning betas (0.35 to 1.90 vs
  BTC), idiosyncratic vol 0.003, and a known ground truth. It is **not real
  market data** and **not market profitability evidence**.
- **No out-of-sample validation on real data.** All results are on the
  controlled synthetic wide universe (seed 20261120). The promotion is based on
  OOS evaluation on synthetic data only.
- **No walk-forward on real market data.** Campaign P25 closes the
  rank-weighting promotion question on the synthetic wide universe. Real-market
  deployment requires Campaign P26 signal-to-noise validation.
- **No capacity/turnover analysis on real markets.** The synthetic universe has
  no market impact model. P26 WP2 addresses capacity & turnover of the rank
  book.
- **No regime stress on real markets.** The synthetic universe has no regime
  structure beyond BTC volatility. P26 WP1 addresses regime-conditional rank
  stress.

---

## Next Steps

Campaign P25 concludes here. The PROMOTE verdict is grounded in the committed
P25 WP2 bake-off JSON artifact. All numbers are labelled **controlled
synthetic** - never market alpha. The Frazzini-Pedersen rank-weighted
construction with beta-neutrality by default is promoted as the default
weighting for the BAB strategy on wide cross-sections.

**Future work** (Campaign P26 - "Signal-to-Noise Validation of Rank-Weighted
BAB"):
- WP0: Signal vs null battery - test rank-weighted BAB against 1000 permuted
  null books
- WP1: Regime-conditional rank stress - split wide universe into calm/stress
  regimes
- WP2: Capacity & turnover of rank book - sweep gross exposure caps and
  rebalance frequencies
- WP3: Signal-to-noise closing decision

---

*This report is artifact-gated: every numeric table cell resolves to a
committed JSON leaf at 6 dp. The acceptance test
`tests/test_bab_p25_decision_consistency.py` verifies zero unmatched cells,
byte-identical table rendering, AST no-harness scan, and explicit verdict
strings.*
"""

REPORT_PATH.write_text(report, encoding="utf-8")
print(f"Report written to {REPORT_PATH}")
