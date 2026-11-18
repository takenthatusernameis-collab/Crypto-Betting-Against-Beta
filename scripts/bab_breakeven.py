#!/usr/bin/env python3
"""Deterministic P20 WP5 cost/turnover break-even harness for the BAB strategy.

For every beta-neutral equal-weight configuration in the committed WP0 sweep
grid, this harness finds the transaction cost ``tc`` at which the backtest
Sharpe ratio crosses zero. The crossing is located with a fixed, deterministic
6-iteration bisection over ``tc in [0.0, 0.01]`` -- never an early exit, never a
caller-supplied bound.

Two artifacts are written from the same in-memory dict:

  research_state/bab_p20/breakeven.json  -- rows + provenance
  research_state/bab_p20/breakeven.md    -- table rendered from that dict

The sweep is consumed read-only (``build_sweep``) so the uncosted Sharpe of
every row is the same number the WP0 artifact publishes. Rank weighting is
intentionally absent: it is not empirically evaluable on this 9-asset universe
(docs/BAB_FIDELITY.md section 9.1). The fixture is a deterministic synthetic
random walk, never real market data.

Usage:
  python3 scripts/bab_breakeven.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.bab_research_sweep import build_sweep  # noqa: E402
from strategies.betting_against_beta import BABStrategy, metrics  # noqa: E402
from strategies.betting_against_beta.data_loader import load_prices  # noqa: E402

SCHEMA = "bab_p20.breakeven/1"
FIXTURE_PATH = "tests/fixtures/real_market_prices.csv"
OUTPUT_DIR = "research_state/bab_p20"
BENCHMARK = "BTC"
MIN_OBSERVATIONS = 60
WEIGHTING = "equal"
BETA_NEUTRAL = True
TC_LO = 0.0
TC_HI = 0.01
BISECTION_ITERATIONS = 6
DECIMALS = 6

ROW_FIELDS = (
    "beta_window",
    "long_quantile",
    "short_quantile",
    "break_even_tc",
    "uncosted_sharpe",
    "sharpe_at_break_even",
    "turnover_at_break_even",
    "gross_at_break_even",
)

COMPANION_FIELDS = (
    "break_even_tc",
    "sharpe_at_break_even",
    "turnover_at_break_even",
    "gross_at_break_even",
)

_PROVENANCE_KEYS = (
    "fixture_path",
    "fixture_sha256",
    "price_rows",
    "return_rows",
    "date_first",
    "date_last",
    "synthetic",
    "seed",
    "known_gap",
    "nan_columns",
    "synthetic_fixture",
)

REASON_NON_POSITIVE = (
    "uncosted Sharpe is non-positive: the strategy loses money before costs, "
    "so no positive cost tolerance exists"
)
REASON_NO_CROSSING = (
    "costed Sharpe stays positive through the upper search bound, so the zero "
    "crossing lies beyond the tested cost range"
)


def _clean(value):
    """Round a float to the artifact precision, mapping non-finite to None."""
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return round(number, DECIMALS)


def _resolve(path: str) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = _REPO_ROOT / resolved
    return resolved


def _run_config(returns: pd.DataFrame, beta_window: int, quantile: float,
                transaction_costs: float) -> dict:
    """Run one beta-neutral equal-weight configuration; return raw metrics."""
    result = BABStrategy(
        benchmark=BENCHMARK,
        beta_window=beta_window,
        min_observations=MIN_OBSERVATIONS,
        long_quantile=quantile,
        short_quantile=quantile,
        transaction_costs=transaction_costs,
        beta_neutral=BETA_NEUTRAL,
    ).run(returns_df=returns)
    weights = result.weights
    return {
        "sharpe": float(metrics.sharpe_ratio(result.backtest["returns"])),
        "turnover": float(metrics.turnover(weights)),
        "gross": float(weights.abs().sum(axis=1).max()),
    }


def bisect_break_even(evaluate, lo: float = TC_LO, hi: float = TC_HI,
                      iterations: int = BISECTION_ITERATIONS) -> dict:
    """Locate the zero crossing of a decreasing Sharpe curve by fixed bisection.

    Exactly ``iterations`` evaluations are performed: ``mid = (lo + hi) / 2``,
    ``sharpe(mid) > 0`` moves ``lo``, otherwise ``hi``. The answer is
    ``(lo + hi) / 2`` after the final iteration. ``trace`` records every step so
    callers can prove the iteration count instead of trusting a claim.
    """
    lo = float(lo)
    hi = float(hi)
    iterations = int(iterations)
    if iterations < 1:
        raise ValueError("iterations must be >= 1")
    if not hi > lo:
        raise ValueError("hi must be greater than lo")

    trace = []
    for _ in range(iterations):
        mid = (lo + hi) / 2.0
        sharpe = float(evaluate(mid))
        trace.append({"lo": lo, "hi": hi, "mid": mid, "sharpe": sharpe})
        if sharpe > 0.0:
            lo = mid
        else:
            hi = mid

    return {
        "tc": (lo + hi) / 2.0,
        "lo": lo,
        "hi": hi,
        "iterations": iterations,
        "trace": trace,
    }


def _uncosted_sharpe_index(sweep: dict) -> dict:
    """Map ``(beta_window, quantile)`` to the sweep's zero-cost Sharpe."""
    index = {}
    for row in sweep["rows"]:
        if row["weighting"] != WEIGHTING or not row["beta_neutral"]:
            continue
        if row["long_quantile"] != row["short_quantile"]:
            continue
        if row["transaction_costs"] != 0.0:
            continue
        index[(row["beta_window"], row["long_quantile"])] = row["sharpe"]
    return index


def _provenance(sweep: dict, null_field_reasons: dict) -> dict:
    """Reuse WP0 fixture facts, plus the break-even method and null reasons."""
    source = sweep["provenance"]
    provenance = {key: source[key] for key in _PROVENANCE_KEYS}
    provenance["method"] = (
        "6-iteration bisection over tc in [0, 0.01] on the equal-weight "
        "beta-neutral grid"
    )
    provenance["weighting"] = WEIGHTING
    provenance["beta_neutral"] = BETA_NEUTRAL
    provenance["bisection"] = {
        "lo": TC_LO,
        "hi": TC_HI,
        "iterations": BISECTION_ITERATIONS,
        "rule": (
            "mid=(lo+hi)/2; sharpe(mid)>0 makes lo=mid, otherwise hi=mid; "
            "break_even_tc=(lo+hi)/2 after exactly 6 evaluations"
        ),
    }
    provenance["metric_definitions"] = {
        "break_even_tc": (
            "transaction cost in [0, 0.01] at which the backtest Sharpe crosses "
            "zero, located by 6 fixed bisection iterations"
        ),
        "uncosted_sharpe": "sweep Sharpe at transaction_costs=0.0 for the same configuration",
        "sharpe_at_break_even": "backtest Sharpe evaluated at the reported break_even_tc",
        "turnover_at_break_even": "mean one-way turnover of the book at break_even_tc",
        "gross_at_break_even": "max over rows of sum_i |w_i| at break_even_tc",
    }
    provenance["null_field_reasons"] = null_field_reasons
    return provenance


def build_breakeven(fixture_path: str = FIXTURE_PATH) -> dict:
    """Run the break-even bisection and return the artifact dict. No file writes."""
    path = _resolve(fixture_path)
    returns = load_prices(path, benchmark=BENCHMARK)
    sweep = build_sweep(fixture_path)

    uncosted = _uncosted_sharpe_index(sweep)
    rows = []
    null_field_reasons = {}

    for beta_window, quantile in sorted(uncosted):
        result = bisect_break_even(
            lambda tc, _bw=beta_window, _q=quantile: _run_config(
                returns, _bw, _q, tc
            )["sharpe"]
        )
        uncosted_sharpe = uncosted[(beta_window, quantile)]
        row = {
            "beta_window": int(beta_window),
            "long_quantile": _clean(quantile),
            "short_quantile": _clean(quantile),
            "break_even_tc": None,
            "uncosted_sharpe": _clean(uncosted_sharpe),
            "sharpe_at_break_even": None,
            "turnover_at_break_even": None,
            "gross_at_break_even": None,
        }

        if uncosted_sharpe <= 0.0:
            null_field_reasons[f"{beta_window}|{_clean(quantile)}"] = {
                "fields": list(COMPANION_FIELDS),
                "reason": REASON_NON_POSITIVE,
            }
        elif result["hi"] == TC_HI:
            null_field_reasons[f"{beta_window}|{_clean(quantile)}"] = {
                "fields": list(COMPANION_FIELDS),
                "reason": REASON_NO_CROSSING,
            }
        else:
            detail = _run_config(returns, beta_window, quantile, result["tc"])
            row["break_even_tc"] = _clean(result["tc"])
            row["sharpe_at_break_even"] = _clean(detail["sharpe"])
            row["turnover_at_break_even"] = _clean(detail["turnover"])
            row["gross_at_break_even"] = _clean(detail["gross"])

        rows.append(row)

    return {
        "schema": SCHEMA,
        "provenance": _provenance(sweep, null_field_reasons),
        "rows": rows,
    }


def _format(value) -> str:
    if value is None:
        return "None"
    return f"{float(value):.{DECIMALS}f}"


def render_markdown(payload: dict) -> str:
    """Render the break-even rows as a markdown table derived from the dict."""
    provenance = payload["provenance"]
    lines = [
        "# BAB P20 WP5 — cost/turnover break-even",
        "",
        (
            f"Fixture: `{provenance['fixture_path']}` "
            f"(sha256 `{provenance['fixture_sha256']}`), "
            f"{provenance['date_first']} -> {provenance['date_last']}."
        ),
        (
            "The fixture is a deterministic synthetic random walk with a fixed "
            "seed and a deliberate data gap: **not real market data**, and none "
            "of these numbers are real-world profitability evidence."
        ),
        f"Method: {provenance['method']}.",
        (
            "Weighting: equal. Beta-neutral: True. `None` marks rows with no zero "
            "crossing inside the tested cost range; each reason is recorded in "
            "`provenance.null_field_reasons`."
        ),
        "",
        "| " + " | ".join(ROW_FIELDS) + " |",
        "|" + "|".join("---" for _ in ROW_FIELDS) + "|",
    ]
    for row in payload["rows"]:
        cells = []
        for column in ROW_FIELDS:
            value = row[column]
            if isinstance(value, int) and not isinstance(value, bool):
                cells.append(str(value))
            else:
                cells.append(_format(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def write_artifacts(payload: dict, output_dir: str = OUTPUT_DIR) -> tuple[Path, Path]:
    """Write the JSON and markdown artifacts; return their paths."""
    directory = _resolve(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "breakeven.json"
    markdown_path = directory / "breakeven.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    payload = build_breakeven()
    json_path, markdown_path = write_artifacts(payload)
    print(f"wrote {json_path} ({len(payload['rows'])} rows)")
    print(f"wrote {markdown_path}")


if __name__ == "__main__":
    main()
