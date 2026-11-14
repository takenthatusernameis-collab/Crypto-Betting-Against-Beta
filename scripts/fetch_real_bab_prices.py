#!/usr/bin/env python3
"""Deterministic fetch/update pipeline for BAB real-format price data.

This script produces/updates a CSV in the exact schema consumed by
`strategies.betting_against_beta.data_loader.load_prices` and
`scripts/load_real_bab_example.py --from-prices`:
  - `date` column (ISO YYYY-MM-DD), sorted ascending, unique
  - benchmark column present (default BTC)
  - numeric price columns per asset

Data source and licensing:
  - Default source: `deterministic-offline` synthetic market-walk generator
    embedded in this repository (reproducible, no network, no credentials,
    no third-party data licensing concerns). It is intended for reproducible
    local/research runs and CI/offline environments.
  - Optional source: `fixture` copies from a local fixture/path you provide
    (`--fixture-path`) and can incrementally extend it deterministically.
  - This script NEVER performs silent network fetches. Non-deterministic or
    unavailable external sources fail loudly with an explicit error and a
    suggested offline alternative.

Idempotent incremental updates:
  - If output exists, existing rows are preserved in order for dates already
    present (no history corruption). New rows are appended only for dates
    strictly after the existing last date (or missing dates when merging a
    validated source frame), deduped by date, sorted, and validated.
  - Re-running with the same arguments yields the same file content.

Example:
  python scripts/fetch_real_bab_prices.py --output data/real_bab_prices.csv \
    --universe BTC,ETH,SOL,BNB,XRP,ADA,AVAX,DOT,LINK --benchmark BTC \
    --start 2021-01-04 --end 2022-07-15
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.betting_against_beta.data_loader import (  # noqa: E402
    BABDataError,
    load_prices,
)

DEFAULT_UNIVERSE = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT", "LINK"]
DEFAULT_STARTS = {
    "BTC": 32000.0,
    "ETH": 1900.0,
    "SOL": 35.0,
    "BNB": 420.0,
    "XRP": 0.55,
    "ADA": 1.20,
    "AVAX": 55.0,
    "DOT": 14.0,
    "LINK": 22.0,
}
DEFAULT_PARAMS = {
    "BTC": (0.0004, 0.018),
    "ETH": (0.0006, 0.024),
    "SOL": (0.0008, 0.035),
    "BNB": (0.0005, 0.028),
    "XRP": (0.0004, 0.030),
    "ADA": (0.0005, 0.032),
    "AVAX": (0.0007, 0.038),
    "DOT": (0.0004, 0.030),
    "LINK": (0.0005, 0.033),
}


def _parse_symbols(raw: str | None, benchmark: str) -> list[str]:
    if raw is None:
        symbols = list(DEFAULT_UNIVERSE)
    else:
        symbols = [s.strip() for s in raw.split(",") if s.strip()]
    if not symbols:
        raise BABDataError("--universe must contain at least one symbol")
    out: list[str] = []
    seen: set[str] = set()
    for s in symbols:
        if s not in seen:
            out.append(s)
            seen.add(s)
    if benchmark not in seen:
        out.insert(0, benchmark)
    return out


def _stable_seed(symbols: list[str], start: str, benchmark: str) -> int:
    base = 20261028
    key = "|".join([benchmark, start, *symbols])
    h = sum((i + 1) * ord(c) for i, c in enumerate(key))
    return (base + h) % (2**31 - 1)


def _generate_prices(
    symbols: list[str],
    start: str,
    end: str,
    benchmark: str,
    seed: int | None = None,
) -> pd.DataFrame:
    if benchmark not in symbols:
        raise BABDataError(f"benchmark {benchmark!r} must be included in symbols")
    dates = pd.bdate_range(start=start, end=end)
    if len(dates) == 0:
        raise BABDataError("date range produced no business days")
    use_seed = (
        _stable_seed(symbols, str(dates[0].date()), benchmark)
        if seed is None
        else int(seed)
    )
    rng = np.random.default_rng(use_seed)
    data: dict[str, np.ndarray] = {}
    for name in symbols:
        drift, vol = DEFAULT_PARAMS.get(name, (0.0005, 0.03))
        start_px = float(DEFAULT_STARTS.get(name, 10.0 + (abs(hash(name)) % 100)))
        log_ret = rng.normal(drift, vol, size=len(dates))
        if len(dates) >= 30:
            shock_idx = rng.choice(
                len(dates), size=max(1, len(dates) // 150), replace=False
            )
            log_ret[shock_idx] += rng.normal(0, 0.04, size=len(shock_idx))
        prices = start_px * np.exp(np.cumsum(log_ret))
        data[name] = np.maximum(prices, 1e-8)
    df = pd.DataFrame(data, index=dates)
    df.index.name = "date"
    out = df.reset_index()
    out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
    return out


def _read_price_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise BABDataError(f"input file not found: {path}")
    df = pd.read_csv(path)
    if "date" not in [str(c).strip().lower() for c in df.columns]:
        df = df.rename(columns={df.columns[0]: "date"})
    colmap = {c: ("date" if str(c).strip().lower() == "date" else c) for c in df.columns}
    df = df.rename(columns=colmap)
    df["date"] = pd.to_datetime(df["date"], errors="raise").dt.strftime("%Y-%m-%d")
    return df


def _validate_schema_contract(
    df: pd.DataFrame, benchmark: str, symbols: list[str] | None = None
) -> pd.DataFrame:
    if "date" not in df.columns:
        raise BABDataError("price data must contain a 'date' column")
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="raise").dt.strftime("%Y-%m-%d")
    out = (
        out.drop_duplicates(subset=["date"], keep="first")
        .sort_values("date")
        .reset_index(drop=True)
    )
    cols_lower = {str(c).strip().lower(): c for c in out.columns}
    if benchmark.lower() not in cols_lower:
        raise BABDataError(f"benchmark column {benchmark!r} missing from price data")
    bench_col = cols_lower[benchmark.lower()]
    other_cols = [c for c in out.columns if c not in ("date", bench_col)]
    if symbols is not None:
        desired = [s for s in symbols if s != benchmark]
        extras = [c for c in other_cols if c not in desired]
        ordered = [c for c in desired if c in out.columns] + extras
        out = out[["date", bench_col, *ordered]]
    else:
        out = out[["date", bench_col, *other_cols]]
    load_prices(out, benchmark=benchmark, min_rows=2)
    return out


def _incremental_update(
    existing: pd.DataFrame, new: pd.DataFrame, benchmark: str
) -> pd.DataFrame:
    all_cols = ["date"]
    for src in (existing.columns, new.columns):
        for c in src:
            if c == "date":
                continue
            if c not in all_cols:
                all_cols.append(c)
    # keep benchmark early
    if benchmark in all_cols[1:]:
        all_cols = ["date", benchmark] + [c for c in all_cols[1:] if c != benchmark]
    ex = existing.reindex(columns=all_cols)
    nw = new.reindex(columns=all_cols)
    existing_dates = set(ex["date"].astype(str))
    nw_new = nw[~nw["date"].astype(str).isin(existing_dates)].copy()
    merged = pd.concat([ex, nw_new], ignore_index=True)
    merged["date"] = pd.to_datetime(merged["date"], errors="raise").dt.strftime("%Y-%m-%d")
    merged = (
        merged.drop_duplicates(subset=["date"], keep="first")
        .sort_values("date")
        .reset_index(drop=True)
    )
    return _validate_schema_contract(merged, benchmark=benchmark)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch/update deterministic real-format BAB price data"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path (real-format, load_prices-compatible)",
    )
    parser.add_argument(
        "--benchmark", default="BTC", help="Benchmark symbol column (default: BTC)"
    )
    parser.add_argument(
        "--universe",
        default=None,
        help="Comma-separated symbols/universe (benchmark auto-included)",
    )
    parser.add_argument("--start", default="2021-01-04", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default="2022-07-15", help="End date YYYY-MM-DD")
    parser.add_argument(
        "--source",
        default="deterministic-offline",
        choices=["deterministic-offline", "fixture"],
        help="Data source (external/network sources fail loudly; not supported).",
    )
    parser.add_argument(
        "--fixture-path",
        default=None,
        help="Local CSV path when --source fixture (must be load_prices-compatible)",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Optional deterministic RNG seed override"
    )
    parser.add_argument(
        "--print-metadata", action="store_true", help="Print source/coverage metadata"
    )
    args = parser.parse_args(argv)

    try:
        symbols = _parse_symbols(args.universe, args.benchmark)
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if args.source == "fixture":
            if not args.fixture_path:
                raise BABDataError("--source fixture requires --fixture-path")
            src_df = _read_price_csv(Path(args.fixture_path))
            src_df = _validate_schema_contract(src_df, benchmark=args.benchmark, symbols=symbols)
            mask = (pd.to_datetime(src_df["date"]) >= pd.to_datetime(args.start)) & (
                pd.to_datetime(src_df["date"]) <= pd.to_datetime(args.end)
            )
            new_df = src_df.loc[mask].reset_index(drop=True)
            if new_df.empty:
                raise BABDataError("fixture source produced no rows in requested date range")
            source_name = f"fixture:{args.fixture_path}"
            source_license = (
                "user-provided local fixture; verify licensing/ToS before redistribution"
            )
        elif args.source == "deterministic-offline":
            new_df = _generate_prices(
                symbols, args.start, args.end, args.benchmark, seed=args.seed
            )
            new_df = _validate_schema_contract(
                new_df, benchmark=args.benchmark, symbols=symbols
            )
            source_name = "deterministic-offline (embedded reproducible generator, no network)"
            source_license = (
                "repository-generated synthetic market data (no third-party data license)"
            )
        else:
            raise BABDataError(
                f"unsupported/unavailable source {args.source!r}; "
                "use --source deterministic-offline or --source fixture"
            )

        if out_path.exists():
            existing = _read_price_csv(out_path)
            existing = _validate_schema_contract(existing, benchmark=args.benchmark)
            final_df = _incremental_update(existing, new_df, benchmark=args.benchmark)
            mode = "updated"
        else:
            final_df = _validate_schema_contract(
                new_df, benchmark=args.benchmark, symbols=symbols
            )
            mode = "created"

        load_prices(final_df, benchmark=args.benchmark, min_rows=2)
        final_df.to_csv(out_path, index=False)

        if args.print_metadata:
            print(f"mode={mode}")
            print(f"output={out_path}")
            print(f"source={source_name}")
            print(f"license={source_license}")
            print(f"benchmark={args.benchmark}")
            print(f"rows={len(final_df)}")
            print(f"start={final_df['date'].iloc[0]}")
            print(f"end={final_df['date'].iloc[-1]}")
            print(f"columns={','.join(map(str, final_df.columns))}")
        return 0
    except BABDataError as exc:
        print(f"Data fetch/update failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Data fetch/update failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
