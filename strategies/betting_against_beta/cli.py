"""Command-line interface for BAB strategy."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np

from .config import BABConfig
from .strategy import BABStrategy
from .errors import BABDataError

__version__ = "0.1.0"

_UNIVERSE_UNSET = object()



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
    import math
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
    import numpy as _np

    backtest = getattr(result, "backtest", None)
    try:
        periods = 0
        if backtest is not None and hasattr(backtest, "__len__"):
            periods = int(len(backtest))
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
            pass
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
    import os
    import math
    import numpy as _np

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
                from .data_loader import load_returns, load_prices
                from pathlib import Path
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
        strategy = BABStrategy(config)
        if args.synthetic or args.data is None:
            result = strategy.run()
        else:
            from .data_loader import load_prices, load_returns
            from pathlib import Path

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

    # Extract cumulative return defensively; never let a bad value crash the CLI.
    try:
        cum_out = _coerce_finite_scalar(
            _extract_cumulative(result), default=1.0
        )
    except Exception:
        cum_out = 1.0
    try:
        print(f"Final cumulative return: {cum_out:.6f}")
        bt = getattr(result, "backtest", None)
        try:
            periods = int(len(bt)) if bt is not None and hasattr(bt, "__len__") else 0
        except Exception:
            periods = 0
        print(f"Periods: {periods}")
    except Exception:
        pass

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

    return 0


def _extract_cumulative(result):
    """Best-effort extraction of the final cumulative return from a BABResult.

    Handles DataFrame, Series, list, and arbitrary objects. Returns None
    (never raises) when no cumulative value can be found.
    """
    try:
        backtest = getattr(result, "backtest", None)
        if backtest is None:
            return None
        if hasattr(backtest, "__len__") and len(backtest) == 0:
            return None
        # DataFrame with columns
        if hasattr(backtest, "columns") and hasattr(backtest, "iloc"):
            cols = list(backtest.columns)
            if "cumulative" in cols:
                try:
                    return backtest["cumulative"].iloc[-1]
                except Exception:
                    pass
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
                try:
                    return backtest.iloc[-1]
                except Exception:
                    pass
        # DataFrame without a recognized cumulative column: prefer the last
        # scalar value over returning the whole frame (avoids ambiguous truth
        # value). Fall back to returning the object if extraction is not possible.
        if hasattr(backtest, "columns") and hasattr(backtest, "iloc"):
            try:
                if backtest.shape[1] > 0 and len(backtest) > 0:
                    return backtest.iloc[-1, -1]
            except Exception:
                pass
            return backtest
        # List / tuple / ndarray: take last element
        if isinstance(backtest, (list, tuple)):
            return backtest[-1] if backtest else None
        # Single scalar
        return backtest
    except Exception:
        return None


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
            pass
    return obj


if __name__ == "__main__":
    raise SystemExit(main())
