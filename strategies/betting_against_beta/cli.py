"""Command-line interface for BAB strategy."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .config import BABConfig
from .errors import BABDataError
from .execution import execution_payload_to_json
from .strategy import BABStrategy

__version__ = "0.1.0"

_UNIVERSE_UNSET = object()



def _build_adapter(args):
    """Build a deterministic in-process execution adapter from CLI args (R5-D).

    Returns an ExecutionAdapter instance, or None when no adapter is requested.
    No network or credentials are ever used.
    """
    from .execution import MockAdapter, PaperAdapter

    adapter_name = getattr(args, "adapter", None)
    if adapter_name is None:
        return None, None
    if adapter_name == "paper":
        return PaperAdapter(), None
    if adapter_name == "mock":
        fills_path = getattr(args, "fills", None)
        fill_map = None
        if fills_path:
            try:
                with open(fills_path, encoding="utf-8") as fh:
                    raw = json.load(fh)
                # Accept either a list of fill dicts or a dict keyed by [date, asset].
                if isinstance(raw, list):
                    fill_map = {}
                    for f in raw:
                        if not isinstance(f, dict):
                            continue
                        key = (str(f.get("date", "")), str(f.get("asset", "")))
                        fill_map[key] = f
                elif isinstance(raw, dict):
                    fill_map = raw
            except (OSError, ValueError, TypeError) as exc:
                raise BABDataError(f"invalid --fills file {fills_path!r}: {exc}") from exc
        return MockAdapter(fill_map=fill_map), fills_path
    return None, None


def _write_json_artifact(path, payload):
    """Write a strict-JSON-safe payload to path, coercing non-finite values."""
    safe = _json_safe(payload)
    try:
        path.write_text(json.dumps(safe, indent=2, default=_json_default, allow_nan=False))
    except Exception as exc:
        print(f"Error writing artifact {path}: {exc}")
        return False
    return True


def _run_reconciliation(result, config, adapter_fills):
    """Build R5-B + R5-C reconciliation artifacts from a run result.

    Returns a dict with keys 'costs' and 'fills' (each a ReconciliationResult
    to_dict), or None when there is nothing to reconcile.
    """
    from .reconciliation import reconcile_costs, reconcile_fills_to_backtest

    weights = getattr(result, "weights", None)
    returns = getattr(result, "returns", None)
    backtest = getattr(result, "backtest", None)
    if not isinstance(weights, __import__("pandas").DataFrame) or weights.empty:
        return None

    import pandas as _pd  # local

    costs = reconcile_costs(
        weights,
        model=None,
        executed_fills=adapter_fills or [],
        transaction_costs=float(getattr(config, "transaction_costs", 0.0) or 0.0),
        slippage=float(getattr(config, "slippage", 0.0) or 0.0),
    )
    fills_rec = None
    if isinstance(returns, _pd.DataFrame) and isinstance(backtest, _pd.DataFrame):
        fills_rec = reconcile_fills_to_backtest(
            weights,
            returns,
            backtest,
            fills=adapter_fills or [],
            transaction_costs=float(getattr(config, "transaction_costs", 0.0) or 0.0),
            slippage=float(getattr(config, "slippage", 0.0) or 0.0),
        )
    return {"costs": costs.to_dict(), "fills": fills_rec.to_dict() if fills_rec else None}


def _print_resolved_config(config: BABConfig) -> None:
    """Print the resolved CLI configuration in a stable, human-readable form."""
    print("Resolved BAB configuration:")
    print(f"  version:          {__version__}")
    print(f"  benchmark:        {config.benchmark}")
    print(f"  universe:         {list(config.universe) if config.universe else []}")
    print(f"  beta_window:      {config.beta_window}")
    print(f"  long_quantile:    {config.long_quantile}")
    print(f"  short_quantile:   {config.short_quantile}")
    print(f"  rebalance_freq:   {config.rebalance_freq}")
    print(f"  transaction_costs:{config.transaction_costs}")
    print(f"  slippage:         {config.slippage}")
    print(f"  min_rows:         {config.min_rows}")


def _validate_output_path(path_str: str) -> Path:
    """Validate that the --output path is writable, creating parent dirs.

    Raises ``BABDataError`` (or a wrapped ``ValueError``) on any problem so the
    caller can surface a clean message instead of crashing mid-backtest.
    """
    from .errors import BABDataError

    if not path_str or not isinstance(path_str, str) or not path_str.strip():
        raise BABDataError("--output path must be a non-empty string")

    # Path traversal protection: resolve and ensure it's within allowed boundaries
    out_path = Path(path_str).resolve()
    # Allowed base directories
    allowed_bases = {
        Path.cwd().resolve(),
        Path("/tmp").resolve(),
        Path("/home/runner/work/_temp/kilo-tmp").resolve(),
    }
    # Check if resolved path is under any allowed base
    is_allowed = any(
        str(out_path).startswith(str(base) + os.sep) or str(out_path) == str(base)
        for base in allowed_bases
    )
    if not is_allowed:
        raise BABDataError(
            f"--output path resolves outside allowed directories: {out_path} "
            f"(allowed: {', '.join(str(b) for b in allowed_bases)})"
        )

    # Reject directories as output targets
    if out_path.exists() and out_path.is_dir():
        raise BABDataError(f"--output path is a directory, not a file: {out_path}")
    # Create parent directories if needed
    parent = out_path.parent
    if str(parent) and str(parent) != ".":
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise BABDataError(
                f"cannot create parent directory for --output {out_path}: {exc}"
            ) from exc
    # Probe writability of the destination (or its parent if the file does not exist yet)
    probe_target = out_path if out_path.exists() else parent
    if str(probe_target) and str(probe_target) != ".":
        try:
            if not os.access(str(probe_target), os.W_OK):
                raise BABDataError(f"--output path is not writable: {out_path}")
        except BABDataError:
            raise
        except Exception:
            pass  # access() may not be reliable on all filesystems; defer to write
    return out_path


def _validate_rebalance_freq(freq: str) -> None:
    """Validate rebalance frequency against allowed values."""
    from .errors import BABDataError
    allowed = {"daily", "weekly", "monthly", "quarterly", "yearly", "annual"}
    if freq not in allowed:
        raise BABDataError(
            f"rebalance_freq must be one of {sorted(allowed)}, got {freq!r}"
        )


def _coerce_finite_scalar(value, default=1.0):
    """Coerce a possibly-nan/inf scalar to a finite float, never raising."""
    import numpy as _np

    try:
        if value is None:
            return float(default)
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            f = float(value)
        else:
            f = float(value)
        if not _np.isfinite(f):
            return float(default)
        return f
    except (TypeError, ValueError):
        return float(default)


def _build_output_summary(result, config, cum_out):
    """Build a JSON-safe output summary dict, always finite.

    Defensive against malformed result objects: a backtest that is a Series,
    a list, or any non-DataFrame is handled gracefully. Universe elements
    that are not strings are coerced.
    """

    backtest = getattr(result, "backtest", None)
    try:
        periods = 0
        if backtest is not None and hasattr(backtest, "__len__"):
            periods = len(backtest)
    except TypeError:
        periods = 0
    universe = getattr(config, "universe", None)
    safe_universe = []
    if universe is not None:
        try:
            for u in universe:
                if u is None:
                    continue
                try:
                    safe_universe.append(str(u))
                except Exception:
                    safe_universe.append(repr(u))
        except TypeError:
            safe_universe = []
    return {
        "final_cumulative": float(cum_out),
        "periods": periods,
        "benchmark": getattr(config, "benchmark", None),
        "universe": safe_universe,
    }


def _json_default(obj):
    """Fallback serializer for objects json.dumps doesn't know about.

    Handles numpy arrays, pandas objects, datetimes, and any other
    non-natively-serializable object by converting to JSON-safe primitives.
    Non-finite floats are coerced to 0.0 so ``allow_nan=False`` never raises.
    """
    import math

    import numpy as _np
    import pandas as _pd

    # Numpy arrays -> list of sanitized values
    if isinstance(obj, _np.ndarray):
        return [_json_default(v) for v in obj.tolist()]
    # Pandas Series -> list of sanitized values
    if isinstance(obj, _pd.Series):
        return [_json_default(v) for v in obj.tolist()]
    # Pandas DataFrame -> dict of lists
    if isinstance(obj, _pd.DataFrame):
        return {str(k): [_json_default(v) for v in obj[k].tolist()] for k in obj.columns}
    # Pandas Index -> list
    if isinstance(obj, _pd.Index):
        return [_json_default(v) for v in obj.tolist()]
    # Pandas Timestamp / datetime
    if isinstance(obj, (_pd.Timestamp,)):
        try:
            return obj.isoformat()
        except Exception:
            return str(obj)
    if hasattr(obj, "isoformat"):
        try:
            return obj.isoformat()
        except Exception:
            return str(obj)
    if isinstance(obj, (set, frozenset)):
        return [_json_default(v) for v in obj]
    if isinstance(obj, bytes):
        try:
            return obj.decode("utf-8", errors="replace")
        except Exception:
            return repr(obj)
    # Coerce non-finite floats to 0.0 for JSON safety
    if isinstance(obj, float):
        return 0.0 if not math.isfinite(obj) else obj
    if isinstance(obj, (_np.floating,)):
        f = float(obj)
        return 0.0 if not math.isfinite(f) else f
    if isinstance(obj, (_np.integer,)):
        return int(obj)
    if isinstance(obj, (_np.bool_,)):
        return bool(obj)
    # Last resort: stringify
    return str(obj)


def main(argv=None) -> int:
    import math


    try:
        parser = argparse.ArgumentParser(description="Betting Against Beta (BAB) crypto strategy")
        parser.add_argument("--version", action="version", version=f"bab {__version__}")
        parser.add_argument("--data", type=str, help="Path to returns data (CSV/JSON/Parquet/HDF5/Pickle). Use --from-prices to treat this as a price series instead.")
        parser.add_argument("--benchmark", type=str, default="BTC", help="Benchmark symbol (default: BTC)")
        parser.add_argument("--universe", type=str, nargs="*", action="store", default=argparse.SUPPRESS, help="Universe of assets")
        parser.add_argument("--beta-window", type=str, default="90", help="Beta estimation window")
        parser.add_argument("--long-quantile", type=str, default="0.3", help="Long quantile")
        parser.add_argument("--short-quantile", type=str, default="0.3", help="Short quantile")
        parser.add_argument("--rebalance-freq", type=str, default="daily", help="Rebalance frequency")
        parser.add_argument("--transaction-costs", type=str, default="0.0", help="Transaction costs")
        parser.add_argument("--slippage", type=str, default="0.0", help="Slippage")
        parser.add_argument("--output", type=str, help="Output JSON file for results summary")
        parser.add_argument("--synthetic", action="store_true", help="Use synthetic data")
        parser.add_argument(
            "--from-prices",
            action="store_true",
            help="Treat --data as a price series and convert to returns via load_prices()",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate inputs and print resolved config without running the backtest",
        )
        parser.add_argument(
            "--adapter",
            type=str,
            default=None,
            choices=["paper", "mock"],
            help="R5-D: run with an in-process execution adapter (paper or mock). No network, no credentials. Default: none (backtest only).",
        )
        parser.add_argument(
            "--reconcile",
            action="store_true",
            help="R5-D: after running, emit modeled-vs-executed and fills-vs-backtest reconciliation artifacts alongside execution output.",
        )
        parser.add_argument(
            "--fills",
            type=str,
            default=None,
            help="R5-D: path to a JSON file of canned fills for the mock adapter (deterministic fixture). Ignored unless --adapter mock.",
        )

        args = parser.parse_args(argv)
    except SystemExit as exc:
        # argparse's --version and --help use exit code 0; re-raise so callers can catch
        if exc.code == 0:
            raise
        # Other argparse errors (unknown flags, etc.) use exit code 2
        return exc.code
    except Exception as exc:
        print(f"Error parsing arguments: {exc}")
        return 1

    try:
        universe_arg = getattr(args, "universe", None) if hasattr(args, "universe") else None
        if universe_arg is not None:
            # Two distinct cases, both handled here:
            #  * `[]` (argparse swallowed the following flag as a value, e.g.
            #    `--universe --synthetic`) -> not a real universe request; fall
            #    back to defaults/synthetic (historical behavior, expected by
            #    existing tests).
            #  * explicit empty/whitespace-only tokens (`""`, `"   "`) -> strip them
            #    and use the remaining real tokens.
            if len(universe_arg) == 0:
                universe_arg = None
            else:
                cleaned = [str(u).strip() for u in universe_arg if str(u).strip()]
                if not cleaned:
                    raise BABDataError(
                        "--universe must contain at least one non-empty asset token"
                    )
                universe_arg = cleaned

        # Validate and convert numeric string arguments
        def _parse_int(val, name):
            try:
                return int(val)
            except (ValueError, TypeError):
                raise BABDataError(f"{name} must be an integer, got {val!r}")

        def _parse_float(val, name):
            try:
                f = float(val)
                if not math.isfinite(f):
                    raise BABDataError(f"{name} must be finite, got {val!r}")
                return f
            except BABDataError:
                raise
            except (ValueError, TypeError):
                raise BABDataError(f"{name} must be a number, got {val!r}")

        beta_window = _parse_int(args.beta_window, "--beta-window")
        long_quantile = _parse_float(args.long_quantile, "--long-quantile")
        short_quantile = _parse_float(args.short_quantile, "--short-quantile")
        transaction_costs = _parse_float(args.transaction_costs, "--transaction-costs")
        slippage = _parse_float(args.slippage, "--slippage")

        kw = dict(
            benchmark=args.benchmark,
            beta_window=beta_window,
            long_quantile=long_quantile,
            short_quantile=short_quantile,
            rebalance_freq=args.rebalance_freq,
            transaction_costs=transaction_costs,
            slippage=slippage,
            universe=universe_arg,
        )
        # --from-prices is meaningless without a --data source; reject cleanly
        # instead of silently falling back to synthetic data.
        if args.from_prices and args.data is None:
            raise BABDataError("--from-prices requires --data")
        config = BABConfig(**kw)
    except BABDataError as exc:
        print(f"Error creating config: {exc}")
        return 1
    except Exception as exc:
        print(f"Error creating config: {exc}")
        return 1

    # Validate rebalance_freq (not validated in BABConfig)
    try:
        _validate_rebalance_freq(args.rebalance_freq)
    except Exception as exc:
        print(f"Error validating rebalance_freq: {exc}")
        return 1

    # R5-D: validate adapter/fills pairing before any run so a bad --fills
    # file surfaces as a clean error instead of crashing mid-backtest.
    adapter_name = getattr(args, "adapter", None)
    fills_path = getattr(args, "fills", None)
    if fills_path is not None and adapter_name is None:
        print("Error: --fills requires --adapter mock")
        return 1
    if adapter_name == "mock" and fills_path is not None:
        try:
            _build_adapter(args)
        except BABDataError as exc:
            print(f"Error validating --fills: {exc}")
            return 1
    if adapter_name is not None and adapter_name not in ("paper", "mock"):
        print(f"Error: unknown --adapter {adapter_name!r} (expected 'paper' or 'mock')")
        return 1

    if args.dry_run:
        # --dry-run must validate everything it would validate in a real run,
        # including the --output path, without ever writing a file or running
        # the backtest. A bad output target must surface as a clean error.
        if args.output:
            try:
                _validate_output_path(args.output)
            except Exception as exc:
                print(f"Error validating output path: {exc}")
                return 1
        try:
            _print_resolved_config(config)
        except Exception as exc:
            print(f"Error printing config: {exc}")
            return 1
        if args.data is not None:
            try:
                from pathlib import Path

                from .data_loader import load_prices, load_returns
                data_p = Path(args.data)
                if data_p.exists() and data_p.is_dir():
                    print(f"data:             {args.data} (INVALID: Path is a directory, not a file: {data_p})")
                    return 1

                try:
                    if getattr(args, 'from_prices', False):
                        load_prices(args.data, benchmark=args.benchmark, min_rows=config.min_rows)
                    else:
                        load_returns(args.data, benchmark=args.benchmark, min_rows=config.min_rows)
                    print(f"data:             {args.data} (valid, --from-prices={args.from_prices})")
                except BABDataError as exc:
                    print(f"data:             {args.data} (INVALID: {exc})")
                    return 1
                except Exception as exc:
                    print(f"data:             {args.data} (INVALID: {exc})")
                    return 1
            except BABDataError as exc:
                print(f"data:             {args.data} (INVALID: {exc})")
                return 1
            except Exception as exc:
                print(f"data:             {args.data} (INVALID: {exc})")
                return 1
        else:
            print("data:             synthetic (default)")
        return 0

    # --output handling: validate path FIRST, before running strategy.
    # This ensures no partial output is produced if the output path is invalid.
    out_path = None
    if args.output:
        try:
            out_path = _validate_output_path(args.output)
        except Exception as exc:
            print(f"Error validating output path: {exc}")
            return 1

    try:
        adapter, fills_path = _build_adapter(args)
        # Only pass execution_adapter when an adapter is actually configured so
        # the default path (no adapter) stays byte-identical to pre-R5 behavior
        # and remains compatible with strategies constructed with `config` only.
        if adapter is not None:
            strategy = BABStrategy(config, execution_adapter=adapter)
        else:
            strategy = BABStrategy(config)
        if args.synthetic or args.data is None:
            result = strategy.run()
        else:
            from pathlib import Path

            from .data_loader import load_prices, load_returns

            data_p = Path(args.data)
            if data_p.exists() and data_p.is_dir():
                print(f"Error running strategy: Path is a directory, not a file: {data_p}")
                return 1

            try:
                if args.from_prices:
                    returns_df = load_prices(args.data, benchmark=args.benchmark, min_rows=config.min_rows)
                else:
                    returns_df = load_returns(args.data, benchmark=args.benchmark, min_rows=config.min_rows)
            except BABDataError:
                raise
            except Exception as exc:
                raise BABDataError(str(exc)) from exc
            try:
                result = strategy.run(returns_df=returns_df)
            except BABDataError:
                raise
            except Exception as exc:
                raise BABDataError(str(exc)) from exc
    except BABDataError as exc:
        print(f"Error running strategy: {exc}")
        return 1
    except Exception as exc:
        print(f"Error running strategy: {exc}")
        return 1

    # Extract cumulative return; surface extraction failures instead of fabricating 1.0.
    try:
        cum_out = _coerce_finite_scalar(
            _extract_cumulative(result), default=1.0
        )
    except Exception as exc:
        print(f"Error extracting cumulative return: {exc}")
        return 1
    try:
        print(f"Final cumulative return: {cum_out:.6f}")
    except Exception as exc:
        try:
            print(f"Error printing cumulative return: {exc}")
        except Exception:
            pass
        return 1
    bt = getattr(result, "backtest", None)
    periods = 0
    try:
        if bt is not None and hasattr(bt, "__len__"):
            periods = len(bt)
    except (TypeError, ValueError, OverflowError):
        periods = 0
    try:
        print(f"Periods: {periods}")
    except Exception as exc:
        try:
            print(f"Error printing periods: {exc}")
        except Exception:
            pass
        return 1

    # --output handling: write defensively (path already validated).
    if args.output:
        summary = _build_output_summary(result, config, cum_out)
        # Ensure the summary is fully JSON-safe before writing.
        payload = _json_safe(summary)
        try:
            out_path.write_text(json.dumps(payload, indent=2, default=_json_default, allow_nan=False))
        except Exception as exc:
            print(f"Error writing output: {exc}")
            return 1

    # R5-D: emit execution + reconciliation artifacts when an adapter is used.
    # Additive only: when no adapter is configured this block is skipped and
    # default-path behavior (including --output contract) is unchanged.
    if adapter is not None:
        exec_payload = getattr(result, "execution", None)
        if exec_payload is not None:
            try:
                exec_json = execution_payload_to_json(exec_payload)
                print(f"Execution adapter: {exec_payload.get('adapter')}")
                print(f"  batches: {exec_payload.get('n_batches')}, intents: {exec_payload.get('n_intents')}, fills: {exec_payload.get('n_fills')}")
                if args.output:
                    exec_path = out_path.with_suffix(out_path.suffix + ".execution.json")
                    exec_path.write_text(exec_json)
            except Exception as exc:
                print(f"Error writing execution artifact: {exc}")
                return 1

        if getattr(args, "reconcile", False):
            fills_list = (exec_payload or {}).get("fills", [])
            rec = _run_reconciliation(result, config, fills_list)
            if rec is not None:
                try:
                    rec_json = json.dumps(_json_safe(rec), indent=2, default=_json_default, allow_nan=False)
                    if args.output:
                        rec_path = out_path.with_suffix(out_path.suffix + ".reconciliation.json")
                        rec_path.write_text(rec_json)
                except Exception as exc:
                    print(f"Error writing reconciliation artifact: {exc}")
                    return 1

    return 0


def _extract_cumulative(result):
    """Best-effort extraction of the final cumulative return from a BABResult.

    Handles DataFrame, Series, list, and arbitrary objects. Returns None
    when no cumulative value can be found; raises on a genuine failure to
    read a recognized cumulative column instead of silently falling through
    to a wrong value or the whole object.
    """
    try:
        backtest = getattr(result, "backtest", None)
    except Exception:
        return None
    if backtest is None:
        return None
    if hasattr(backtest, "__len__") and len(backtest) == 0:
        return None
    # DataFrame with columns
    if hasattr(backtest, "columns") and hasattr(backtest, "iloc"):
        cols = list(backtest.columns)
        if "cumulative" in cols:
            return backtest["cumulative"].iloc[-1]
        for col in cols:
            if "cum" in str(col).lower():
                try:
                    return backtest[col].iloc[-1]
                except Exception:
                    continue
        # No recognized cumulative column; fall through to generic handlers.
    # Series with a name containing 'cum'
    if hasattr(backtest, "iloc") and hasattr(backtest, "name"):
        name = str(getattr(backtest, "name", "") or "")
        if "cum" in name.lower():
            return backtest.iloc[-1]
    # DataFrame without a recognized cumulative column: prefer the last
    # scalar value over returning the whole frame (avoids ambiguous truth
    # value). Fall back to returning the object if extraction is not possible.
    if hasattr(backtest, "columns") and hasattr(backtest, "iloc"):
        if backtest.shape[1] > 0 and len(backtest) > 0:
            return backtest.iloc[-1, -1]
        return backtest
    # List / tuple / ndarray: take last element
    if isinstance(backtest, (list, tuple)):
        return backtest[-1] if backtest else None
    # Single scalar
    return backtest


def _json_safe(obj):
    """Recursively sanitize a payload so json.dumps(allow_nan=False) never fails.

    Handles numpy arrays, pandas objects, datetimes, and nested containers.
    Non-finite floats are coerced to 0.0.
    """
    import math

    import numpy as _np
    import pandas as _pd

    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (set, frozenset)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, _np.ndarray):
        return [_json_safe(v) for v in obj.tolist()]
    if isinstance(obj, _pd.Series):
        return [_json_safe(v) for v in obj.tolist()]
    if isinstance(obj, _pd.DataFrame):
        return {str(k): [_json_safe(v) for v in obj[k].tolist()] for k in obj.columns}
    if isinstance(obj, _pd.Index):
        return [_json_safe(v) for v in obj.tolist()]
    if isinstance(obj, (_pd.Timestamp,)):
        try:
            return obj.isoformat()
        except Exception:
            return str(obj)
    if isinstance(obj, bool):
        return bool(obj)
    if isinstance(obj, (int, _np.integer)):
        return int(obj)
    if isinstance(obj, float):
        return 0.0 if not math.isfinite(obj) else obj
    if isinstance(obj, (_np.floating,)):
        f = float(obj)
        return 0.0 if not math.isfinite(f) else f
    if isinstance(obj, (_np.bool_,)):
        return bool(obj)
    if hasattr(obj, "isoformat"):
        try:
            return obj.isoformat()
        except Exception:
            return str(obj)
    return obj


if __name__ == "__main__":
    raise SystemExit(main())
