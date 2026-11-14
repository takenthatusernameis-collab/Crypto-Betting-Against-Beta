#!/usr/bin/env python3
"""Deterministic fetch/update pipeline for BAB real-format price data.

This script produces/updates a CSV in the exact schema consumed by
`strategies.betting_against_beta.data_loader.load_prices` and
`scripts/load_real_bab_example.py --from-prices`:
  - `date` column (ISO YYYY-MM-DD), sorted ascending, unique
  - benchmark column present (default BTC)
  - numeric price columns per asset

Data sources and licensing/ToS:
  - Default: `deterministic-offline` synthetic market-walk generator embedded
    in this repository (reproducible, no network, no credentials, no
    third-party data licensing concerns). This is the only default path.
  - `fixture`: copies from a local fixture/path you provide (`--fixture-path`)
    and can incrementally extend it deterministically.
  - Explicit opt-in: `coinbase-exchange-public` fetches daily candles from the
    public Coinbase Exchange market-data endpoint (no auth, no API key).
    Network use is NEVER implicit: you must pass
    `--source coinbase-exchange-public --allow-public-api --accept-terms
    "I accept the data provider Terms of Service and rate limits"`.
    The script enforces bounded rate-limit pacing, fails loudly on
    network/HTTP/rate-limit/ToS/invalid-source/parse errors, and never silently
    falls back to bad or synthetic data. Review Coinbase's current Terms of
    Service, market-data policies, and rate limits before use; data
    redistribution may be restricted by the provider.

Idempotent incremental updates:
  - If output exists, existing rows are preserved in order for dates already
    present (no history corruption). New rows are appended only for dates
    strictly after the existing last date (or missing dates when merging a
    validated source frame), deduped by date, sorted, and validated.
  - Re-running with the same arguments yields the same file content for
    deterministic sources.

Example:
  python scripts/fetch_real_bab_prices.py --output data/real_bab_prices.csv \
    --universe BTC,ETH,SOL,BNB,XRP,ADA,AVAX,DOT,LINK --benchmark BTC \
    --start 2021-01-04 --end 2022-07-15
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
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

COINBASE_PUBLIC_SOURCE = "coinbase-exchange-public"
COINBASE_PUBLIC_BASE_URL = "https://api.exchange.coinbase.com"
COINBASE_PUBLIC_TOS_ACK = "I accept the data provider Terms of Service and rate limits"
COINBASE_PUBLIC_MAX_REQUESTS_PER_SECOND = 3.0
COINBASE_PUBLIC_DEFAULT_TIMEOUT = 20.0
COINBASE_PUBLIC_MAX_RETRIES = 2
COINBASE_PUBLIC_USER_AGENT = "crypto-bab-research-fetch/1.0"

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


def _parse_iso_date(value: str, flag: str) -> datetime:
    try:
        dt = datetime.strptime(str(value), "%Y-%m-%d")
    except Exception as exc:
        raise BABDataError(f"{flag} must be YYYY-MM-DD: {value!r}") from exc
    return dt.replace(tzinfo=timezone.utc)


def _enforce_public_api_opt_in(
    source: str, allow_public_api: bool, accept_terms: str | None
) -> None:
    if not allow_public_api:
        raise BABDataError(
            f"--source {source} requires explicit opt-in --allow-public-api; "
            "network fetches are disabled by default. "
            "Use --source deterministic-offline for the offline path."
        )
    if accept_terms != COINBASE_PUBLIC_TOS_ACK:
        raise BABDataError(
            f"--source {source} requires explicit ToS/rate-limit acknowledgement "
            f"via --accept-terms {COINBASE_PUBLIC_TOS_ACK!r}. "
            "Review provider Terms of Service and rate limits before use."
        )


def _coinbase_product(symbol: str, quote_currency: str) -> str:
    sym = str(symbol).strip().upper()
    quote = str(quote_currency).strip().upper()
    if not sym or not quote:
        raise BABDataError("symbol and quote currency must be non-empty")
    return f"{sym}-{quote}"


def _rate_limit_wait(
    last_request_at: float | None, max_requests_per_second: float
) -> float:
    if max_requests_per_second <= 0:
        raise BABDataError("--max-requests-per-second must be > 0")
    min_interval = 1.0 / float(max_requests_per_second)
    now = time.monotonic()
    if last_request_at is not None:
        sleep_for = min_interval - (now - last_request_at)
        if sleep_for > 0:
            time.sleep(sleep_for)
            now = time.monotonic()
    return now


def _http_get_json(
    url: str,
    timeout: float,
    max_requests_per_second: float,
    last_request_at: float | None,
    retries: int = COINBASE_PUBLIC_MAX_RETRIES,
) -> tuple[object, float]:
    attempt = 0
    while True:
        attempt += 1
        last_request_at = _rate_limit_wait(last_request_at, max_requests_per_second)
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": COINBASE_PUBLIC_USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=float(timeout)) as resp:
                status = getattr(resp, "status", None) or resp.getcode()
                body = resp.read()
            if status != 200:
                raise BABDataError(f"HTTP {status} from public API: {url}")
            try:
                return json.loads(body.decode("utf-8")), last_request_at
            except Exception as exc:
                raise BABDataError(f"invalid JSON from public API: {url}") from exc
        except urllib.error.HTTPError as exc:
            status = int(getattr(exc, "code", 0) or 0)
            headers = getattr(exc, "headers", None) or {}
            retry_after = headers.get("Retry-After")
            body_msg = ""
            try:
                body_msg = exc.read().decode("utf-8", errors="replace")[:200]
            except Exception:
                body_msg = ""
            if status == 429:
                if attempt > retries:
                    raise BABDataError(
                        f"public API rate limit (HTTP 429) after retries for {url}"
                        + (f": {body_msg}" if body_msg else "")
                    ) from exc
                wait_s = 1.0
                try:
                    if retry_after is not None:
                        wait_s = max(wait_s, float(retry_after))
                except Exception:
                    wait_s = 1.0
                time.sleep(wait_s)
                continue
            if status in {500, 502, 503, 504} and attempt <= retries:
                time.sleep(0.5 * attempt)
                continue
            raise BABDataError(
                f"public API HTTP error {status} for {url}"
                + (f": {body_msg}" if body_msg else "")
            ) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt > retries:
                raise BABDataError(
                    f"network error contacting public API {url}: {exc}. "
                    "No offline fallback was used; retry later or use "
                    "--source deterministic-offline/fixture."
                ) from exc
            time.sleep(0.5 * attempt)
            continue


def _fetch_coinbase_candles(
    product: str,
    start: datetime,
    end: datetime,
    timeout: float,
    max_requests_per_second: float,
    last_request_at: float | None,
) -> tuple[list, float]:
    params = urllib.parse.urlencode(
        {
            "granularity": "86400",
            "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    )
    url = f"{COINBASE_PUBLIC_BASE_URL}/products/{urllib.parse.quote(product)}/candles?{params}"
    payload, last_request_at = _http_get_json(
        url,
        timeout=timeout,
        max_requests_per_second=max_requests_per_second,
        last_request_at=last_request_at,
    )
    if not isinstance(payload, list):
        raise BABDataError(
            f"unexpected public API response for {product}: expected candle list"
        )
    return payload, last_request_at


def _coinbase_candles_to_daily_close(
    payload: list, product: str, start_date: str, end_date: str
) -> pd.Series:
    rows: dict[str, float] = {}
    for item in payload:
        if not isinstance(item, (list, tuple)) or len(item) < 5:
            raise BABDataError(f"invalid candle row for {product}: {item!r}")
        ts_raw, _low, _high, _open, close = item[0], item[1], item[2], item[3], item[4]
        try:
            day = datetime.fromtimestamp(float(ts_raw), tz=timezone.utc).strftime(
                "%Y-%m-%d"
            )
        except Exception as exc:
            raise BABDataError(
                f"invalid candle timestamp for {product}: {ts_raw!r}"
            ) from exc
        try:
            close_v = float(close)
        except Exception as exc:
            raise BABDataError(f"invalid candle close for {product} on {day}") from exc
        if not np.isfinite(close_v) or close_v <= 0:
            raise BABDataError(f"non-positive/non-finite close for {product} on {day}")
        if day < start_date or day > end_date:
            continue
        # Coinbase returns buckets in reverse-ish order across windows; keep the
        # latest-seen close for the UTC day (deterministic overwrite by parse order
        # is avoided by explicit day key replacement only when absent).
        rows.setdefault(day, close_v)
    if not rows:
        raise BABDataError(
            f"public API returned no usable daily candles for {product} in "
            f"{start_date}..{end_date}"
        )
    s = pd.Series(rows, name=product.split("-")[0], dtype="float64")
    s.index = pd.Index(sorted(s.index), name="date")
    return s.sort_index()


def _fetch_coinbase_exchange_public(
    symbols: list[str],
    start: str,
    end: str,
    benchmark: str,
    quote_currency: str,
    allow_public_api: bool,
    accept_terms: str | None,
    timeout: float,
    max_requests_per_second: float,
) -> pd.DataFrame:
    _enforce_public_api_opt_in(
        COINBASE_PUBLIC_SOURCE, allow_public_api=allow_public_api, accept_terms=accept_terms
    )
    start_dt = _parse_iso_date(start, "--start")
    end_dt = _parse_iso_date(end, "--end")
    if end_dt < start_dt:
        raise BABDataError("--end must be >= --start")
    # Coinbase candles endpoint takes [start,end) ISO windows; request in chunks.
    chunk_days = 250
    all_series: list[pd.Series] = []
    last_request_at: float | None = None
    for symbol in symbols:
        product = _coinbase_product(symbol, quote_currency)
        chunk_start = start_dt
        candles: list = []
        while chunk_start <= end_dt:
            chunk_end_exclusive = min(
                end_dt + timedelta(days=1), chunk_start + timedelta(days=chunk_days)
            )
            payload, last_request_at = _fetch_coinbase_candles(
                product=product,
                start=chunk_start,
                end=chunk_end_exclusive,
                timeout=timeout,
                max_requests_per_second=max_requests_per_second,
                last_request_at=last_request_at,
            )
            candles.extend(payload)
            chunk_start = chunk_end_exclusive
        series = _coinbase_candles_to_daily_close(
            candles, product=product, start_date=start, end_date=end
        )
        series.name = symbol
        all_series.append(series)
    out = pd.concat(all_series, axis=1)
    if benchmark not in out.columns:
        raise BABDataError(
            f"public API result missing benchmark column {benchmark!r}"
        )
    # Keep rows where all requested symbols have data to satisfy strict loader
    # contract and avoid silent partial alignment.
    before = len(out)
    out = out.dropna(how="any")
    if out.empty:
        raise BABDataError(
            "public API fetch produced no rows with complete symbol coverage; "
            "check symbol availability on the chosen public market"
        )
    if len(out) < 2:
        raise BABDataError(
            "public API fetch produced insufficient rows for returns computation"
        )
    df = out.reset_index().rename(columns={"index": "date"})
    df["date"] = pd.to_datetime(df["date"], errors="raise").dt.strftime("%Y-%m-%d")
    if df["date"].duplicated().any():
        raise BABDataError("public API fetch produced duplicate dates")
    if not df["date"].is_monotonic_increasing:
        df = df.sort_values("date").reset_index(drop=True)
    if len(df) != before:
        # Inform via returned frame shape only; caller prints metadata.
        pass
    cols = ["date", benchmark] + [c for c in symbols if c != benchmark and c in df.columns]
    return df[cols]


def _safe_write_failure_metadata(args, error: str) -> None:
    """Best-effort failure metadata write; never raises from the error path."""
    if not args.metadata_out:
        return
    try:
        meta = _build_metadata(
            args=args, mode="failed", final_df=None, error=error
        )
    except Exception:
        # Even metadata construction can fail (bad args); skip silently rather
        # than mask the original fetch/update error.
        return
    try:
        _write_metadata(args, meta)
    except Exception:
        return


def _write_metadata(args, meta: dict) -> None:
    """Write the JSON audit sidecar if --metadata-out was requested."""
    if not args.metadata_out:
        return
    out_path = Path(args.metadata_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, sort_keys=True)
        fh.write("\n")


def _build_metadata(
    *,
    args,
    mode: str,
    final_df: pd.DataFrame | None,
    error: str | None = None,
) -> dict:
    """Build a machine-readable audit trail dict (no secrets/ToS text)."""
    symbols = _parse_symbols(args.universe, args.benchmark)
    # Validate date args (raises BABDataError on bad format) — results unused here.
    _parse_iso_date(args.start, "--start")
    _parse_iso_date(args.end, "--end")
    meta: dict = {
        "tool": "scripts/fetch_real_bab_prices.py",
        "source": args.source,
        "benchmark": args.benchmark,
        "universe": symbols,
        "request_range": {"start": args.start, "end": args.end},
        "quote_currency": getattr(args, "quote_currency", "USD"),
        "request_settings": {
            "timeout_seconds": float(args.request_timeout),
            "max_requests_per_second": float(args.max_requests_per_second),
            "max_retries": COINBASE_PUBLIC_MAX_RETRIES,
            "user_agent": COINBASE_PUBLIC_USER_AGENT,
        },
        "tos_acknowledged": bool(args.accept_terms == COINBASE_PUBLIC_TOS_ACK)
        if args.source == COINBASE_PUBLIC_SOURCE
        else False,
        "fetch_time_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": mode,
    }
    if args.source == COINBASE_PUBLIC_SOURCE:
        meta["source_url_base"] = COINBASE_PUBLIC_BASE_URL
        meta["tos_flag_only"] = True
    if args.source == "fixture" and args.fixture_path:
        meta["source"] = f"fixture:{args.fixture_path}"
    if args.seed is not None:
        meta["seed"] = int(args.seed)
    if final_df is not None:
        meta["outcome"] = {
            "ok": True,
            "rows": len(final_df),
            "date_coverage": {
                "first": str(final_df["date"].iloc[0]),
                "last": str(final_df["date"].iloc[-1]),
                "unique_dates": int(final_df["date"].nunique()),
            },
            "columns": [str(c) for c in final_df.columns],
            "output": str(Path(args.output).resolve()),
        }
    else:
        meta["outcome"] = {"ok": False, "error": error or "unknown error"}
    return meta


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
        choices=["deterministic-offline", "fixture", COINBASE_PUBLIC_SOURCE],
        help=(
            "Data source. Default deterministic-offline (no network). "
            f"{COINBASE_PUBLIC_SOURCE} is an explicit no-auth public API opt-in "
            "requiring --allow-public-api and --accept-terms."
        ),
    )
    parser.add_argument(
        "--fixture-path",
        default=None,
        help="Local CSV path when --source fixture (must be load_prices-compatible)",
    )
    parser.add_argument(
        "--allow-public-api",
        action="store_true",
        help=(
            f"Required explicit opt-in for --source {COINBASE_PUBLIC_SOURCE}; "
            "without this flag network fetches are refused."
        ),
    )
    parser.add_argument(
        "--accept-terms",
        default=None,
        help=(
            f"Required for --source {COINBASE_PUBLIC_SOURCE}; must exactly match: "
            f"{COINBASE_PUBLIC_TOS_ACK!r}"
        ),
    )
    parser.add_argument(
        "--quote-currency",
        default="USD",
        help=(
            f"Quote currency for --source {COINBASE_PUBLIC_SOURCE} product pairs "
            "(default: USD)."
        ),
    )
    parser.add_argument(
        "--request-timeout",
        type=float,
        default=COINBASE_PUBLIC_DEFAULT_TIMEOUT,
        help=(
            f"HTTP timeout seconds for --source {COINBASE_PUBLIC_SOURCE} "
            f"(default: {COINBASE_PUBLIC_DEFAULT_TIMEOUT})."
        ),
    )
    parser.add_argument(
        "--max-requests-per-second",
        type=float,
        default=COINBASE_PUBLIC_MAX_REQUESTS_PER_SECOND,
        help=(
            f"Rate-limit pacing cap for --source {COINBASE_PUBLIC_SOURCE} "
            f"(default: {COINBASE_PUBLIC_MAX_REQUESTS_PER_SECOND})."
        ),
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Optional deterministic RNG seed override"
    )
    parser.add_argument(
        "--print-metadata", action="store_true", help="Print source/coverage metadata"
    )
    parser.add_argument(
        "--metadata-out",
        default=None,
        help=(
            "Write a machine-readable JSON audit sidecar with source, pacing, "
            "coverage, and outcome/error context. Never persists raw ToS text or secrets."
        ),
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
        elif args.source == COINBASE_PUBLIC_SOURCE:
            new_df = _fetch_coinbase_exchange_public(
                symbols=symbols,
                start=args.start,
                end=args.end,
                benchmark=args.benchmark,
                quote_currency=args.quote_currency,
                allow_public_api=args.allow_public_api,
                accept_terms=args.accept_terms,
                timeout=args.request_timeout,
                max_requests_per_second=args.max_requests_per_second,
            )
            new_df = _validate_schema_contract(
                new_df, benchmark=args.benchmark, symbols=symbols
            )
            source_name = (
                f"{COINBASE_PUBLIC_SOURCE} ({COINBASE_PUBLIC_BASE_URL}, no-auth public API)"
            )
            source_license = (
                "Coinbase Exchange public market data; subject to provider Terms of "
                "Service/rate limits and possible redistribution restrictions"
            )
        else:
            raise BABDataError(
                f"unsupported/unavailable source {args.source!r}; "
                "use --source deterministic-offline, --source fixture, or "
                f"--source {COINBASE_PUBLIC_SOURCE} with explicit opt-in flags"
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

        _write_metadata(args, _build_metadata(args=args, mode=mode, final_df=final_df))

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
        _safe_write_failure_metadata(args, str(exc))
        return 1
    except Exception as exc:
        print(f"Data fetch/update failed: {exc}", file=sys.stderr)
        _safe_write_failure_metadata(args, str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
