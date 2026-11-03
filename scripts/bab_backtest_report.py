#!/usr/bin/env python3
"""End-to-end BAB backtest report.

Runs the BAB strategy (synthetic data by default, or from a CSV/JSON file or
DataFrame passed via --data-source) and prints a human-readable performance
report. With --json, emits a machine-readable summary.

Examples:
    python3 scripts/bab_backtest_report.py
    python3 scripts/bab_backtest_report.py --data-source returns.csv --benchmark BTC
    python3 scripts/bab_backtest_report.py --data-source returns.csv --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure the repository root is importable when this script is executed
# directly (``python scripts/bab_backtest_report.py``) rather than as a
# module. Without this, ``from strategies.betting_against_beta import ...``
# fails with ModuleNotFoundError because Python prepends the script's own
# directory (``scripts/``) to sys.path, not the repository root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pandas as pd

from strategies.betting_against_beta import BABConfig, BABStrategy
from strategies.betting_against_beta import metrics
from strategies.betting_against_beta.errors import BABDataError


def _sanitize_metrics(summary: dict) -> dict:
    """Coerce every metric to a finite JSON-safe scalar.

    NaN / inf values are replaced with 0.0 so the machine-readable report
    never emits a non-finite number, even on degenerate or messy inputs.
    """
    import math

    sanitized: dict = {}
    for key, value in summary.items():
        if isinstance(value, (int, float)):
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                sanitized[key] = 0.0
            else:
                sanitized[key] = value
        elif isinstance(value, bool):
            sanitized[key] = bool(value)
        else:
            sanitized[key] = 0.0
    return sanitized


def _dumps_json(payload: dict) -> str:
    """Serialize payload to a strict JSON string with no NaN/inf tokens.

    ``json.dumps`` with the default ``allow_nan=True`` emits bare ``NaN`` /
    ``Infinity`` / ``-Infinity`` tokens, which are not valid JSON per RFC 8259
    and are rejected by strict parsers (Go, Rust, browsers' JSON.parse in
    some modes). We sanitize the payload first and then disallow NaN so the
    output is always machine-parseable.
    """
    import math

    def _clean(obj):
        if isinstance(obj, dict):
            return {str(k): _clean(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_clean(v) for v in obj]
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return 0.0
        return obj

    cleaned = _clean(payload)
    return json.dumps(cleaned, indent=2, default=str, allow_nan=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BAB backtest report")
    parser.add_argument(
        "--data-source",
        default=None,
        help="Path to a CSV/JSON returns file, or 'synthetic' (default).",
    )
    parser.add_argument(
        "--returns-csv",
        default=None,
        dest="returns_csv",
        help="Alias for --data-source pointing at a CSV returns file.",
    )
    parser.add_argument(
        "--returns",
        default=None,
        dest="returns",
        help="Alias for --data-source pointing at a returns file.",
    )
    parser.add_argument("--benchmark", default="BTC", help="Benchmark asset column name.")
    parser.add_argument("--beta-window", type=int, default=90)
    parser.add_argument("--min-observations", type=int, default=60)
    parser.add_argument("--long-quantile", type=float, default=0.3)
    parser.add_argument("--short-quantile", type=float, default=0.3)
    parser.add_argument("--transaction-costs", type=float, default=0.0)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON report.")
    return parser


def _empty_summary() -> dict:
    """Return a sanitized, all-zero summary used when metrics cannot be computed."""
    return _sanitize_metrics({
        "final_cumulative": 1.0,
        "total_return": 0.0,
        "sharpe_ratio": 0.0,
        "annualized_volatility": 0.0,
        "max_drawdown": 0.0,
        "turnover": 0.0,
        "strategy_beta": 0.0,
        "n_observations": 0,
    })


def _safe_get(obj, *keys, default=None):
    """Walk a nested mapping/attribute chain without raising."""
    current = obj
    for key in keys:
        try:
            if isinstance(current, dict):
                if key not in current:
                    return default
                current = current[key]
            elif hasattr(current, "__getitem__"):
                current = current[key]
            else:
                current = getattr(current, key)
        except (KeyError, IndexError, TypeError, AttributeError):
            return default
    return current


def _compute_rebalances(weights) -> int:
    """Count non-all-NaN rebalance rows defensively."""
    try:
        if weights is None:
            return 0
        if hasattr(weights, "dropna"):
            return int(len(weights.dropna(how="all")))
        return int(len(weights))
    except Exception:
        return 0


def _compute_summary(strategy, result) -> dict:
    """Compute metrics defensively; never raise from this helper."""
    try:
        returns = _safe_get(result, "backtest", "returns", default=None)
        weights = _safe_get(result, "weights", default=None)
        benchmark = _safe_get(strategy, "config", "benchmark", default="BTC")
        benchmark_returns = _safe_get(result, "returns", benchmark, default=None)
        if benchmark_returns is None and isinstance(returns, pd.DataFrame):
            benchmark_returns = returns.get(benchmark)
        if returns is None or weights is None:
            return _empty_summary()
        try:
            summary = metrics.summary(
                returns,
                weights_df=weights,
                benchmark_returns=benchmark_returns,
            )
        except Exception:
            return _empty_summary()
        if not isinstance(summary, dict):
            return _empty_summary()
        return _sanitize_metrics(summary)
    except Exception:
        return _empty_summary()


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"Error parsing arguments: {exc}", file=sys.stderr)
        return 2

    try:
        # --returns-csv / --returns are explicit aliases for the CSV data path;
        # they win over --data-source so callers can pass either flag interchangeably.
        data_source = args.returns_csv or args.returns or args.data_source
        data_source = None if data_source in (None, "", "synthetic") else data_source
        try:
            cfg = BABConfig(
                benchmark=args.benchmark,
                beta_window=args.beta_window,
                min_observations=args.min_observations,
                long_quantile=args.long_quantile,
                short_quantile=args.short_quantile,
                transaction_costs=args.transaction_costs,
                data_source=data_source,
            )
        except Exception as exc:
            raise BABDataError(str(exc)) from exc
        strategy = BABStrategy(cfg)
        result = strategy.run()
    except BABDataError as exc:
        if getattr(args, "json", False):
            try:
                print(_dumps_json({"error": str(exc), "metrics": _empty_summary()}))
            except Exception:
                print('{"error": "report_failed"}')
            return 1
        print(f"Error generating report: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        if getattr(args, "json", False):
            try:
                print(_dumps_json({"error": str(exc), "metrics": _empty_summary()}))
            except Exception:
                print('{"error": "report_failed"}')
            return 1
        print(f"Error generating report: {exc}", file=sys.stderr)
        return 1

    summary = _compute_summary(strategy, result)
    rebalances = _compute_rebalances(_safe_get(result, "weights", default=None))

    if getattr(args, "json", False):
        payload = {
            "config": {
                "universe": list(getattr(strategy.config, "universe", []) or []),
                "benchmark": getattr(strategy.config, "benchmark", "BTC"),
                "beta_window": getattr(strategy.config, "beta_window", 90),
                "min_observations": getattr(strategy.config, "min_observations", 60),
                "long_quantile": getattr(strategy.config, "long_quantile", 0.3),
                "short_quantile": getattr(strategy.config, "short_quantile", 0.3),
                "transaction_costs": getattr(strategy.config, "transaction_costs", 0.0),
                "data_source": getattr(strategy.config, "data_source", None),
            },
            "rebalances": rebalances,
            "metrics": summary,
        }
        try:
            print(_dumps_json(payload))
        except Exception as exc:
            print(_dumps_json({"error": f"serialization_failed: {exc}", "metrics": _empty_summary()}))
            return 1
        return 0

    try:
        print("=" * 60)
        source_desc = "synthetic data" if data_source is None else f"data source: {data_source}"
        print(f"BAB STRATEGY BACKTEST REPORT ({source_desc})")
        print("=" * 60)
        print(f"Universe: {', '.join(getattr(strategy.config, 'universe', []) or [])}")
        print(f"Benchmark: {getattr(strategy.config, 'benchmark', 'BTC')}")
        print(f"Beta window: {getattr(strategy.config, 'beta_window', 90)} days (min {getattr(strategy.config, 'min_observations', 60)} obs)")
        print(f"Long/Short quantiles: {getattr(strategy.config, 'long_quantile', 0.3)}/{getattr(strategy.config, 'short_quantile', 0.3)}")
        print(f"Rebalances: {rebalances}")
        print("-" * 60)
        print(f"Final Cumulative: {summary['final_cumulative']:.4f}x ({summary['total_return']:.2%})")
        print(f"Sharpe Ratio (ann.): {summary['sharpe_ratio']:.4f}")
        print(f"Annualized Volatility: {summary['annualized_volatility']:.2%}")
        print(f"Max Drawdown: {summary['max_drawdown']:.2%}")
        print(f"Turnover (avg): {summary['turnover']:.4f}")
        print(f"Strategy Beta vs {getattr(strategy.config, 'benchmark', 'BTC')}: {summary['strategy_beta']:.4f}")
        print(f"Observations: {summary['n_observations']}")
        print("=" * 60)
    except Exception as exc:
        print(f"Error printing report: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())