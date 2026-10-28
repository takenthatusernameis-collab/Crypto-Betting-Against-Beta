"""Data quality checks for BAB strategy."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def data_quality_report(df: pd.DataFrame) -> dict[str, Any]:
    """Generate a comprehensive data quality report."""
    if df is None or not isinstance(df, pd.DataFrame):
        return {"error": "invalid_input"}

    report: dict[str, Any] = {}
    report["shape"] = {"rows": int(df.shape[0]), "cols": int(df.shape[1])}
    report["index"] = {
        "type": type(df.index).__name__,
        "is_datetime": isinstance(df.index, pd.DatetimeIndex),
        "has_duplicates": bool(df.index.has_duplicates) if hasattr(df.index, "has_duplicates") else False,
    }
    if isinstance(df.index, pd.DatetimeIndex):
        report["index"]["start"] = str(df.index.min())
        report["index"]["end"] = str(df.index.max())
        if len(df.index) > 1:
            gaps = df.index.to_series().diff()
            report["index"]["gaps"] = {
                "count": int((gaps > gaps.median() * 2).sum()) if len(gaps.dropna()) > 0 else 0,
            }

    report["columns"] = []
    for col in df.columns:
        col_data = df[col]
        try:
            numeric = pd.to_numeric(col_data, errors="coerce")
            arr = numeric.to_numpy(dtype=float)
        except Exception:
            arr = np.array([np.nan] * len(col_data))

        finite_mask = np.isfinite(arr)
        report["columns"].append({
            "name": str(col),
            "dtype": str(col_data.dtype),
            "missing": int((~finite_mask).sum()),
            "missing_pct": float((~finite_mask).sum() / len(arr)) if len(arr) > 0 else 1.0,
            "zeros": int((arr == 0).sum()) if len(arr) > 0 else 0,
            "inf": int((~np.isfinite(arr)).sum() - np.isnan(arr).sum()) if len(arr) > 0 else 0,
            "min": float(np.nanmin(arr)) if np.any(finite_mask) else None,
            "max": float(np.nanmax(arr)) if np.any(finite_mask) else None,
            "mean": float(np.nanmean(arr)) if np.any(finite_mask) else None,
            "std": float(np.nanstd(arr)) if np.any(finite_mask) and np.sum(finite_mask) > 1 else None,
        })

    report["summary"] = {
        "total_missing": sum(c["missing"] for c in report["columns"]),
        "all_finite": all(c["missing"] == 0 and c["inf"] == 0 for c in report["columns"]),
        "has_issues": any(c["missing_pct"] > 0.01 or c["inf"] > 0 for c in report["columns"]),
    }

    return report


def check_data_quality(df: pd.DataFrame, strict: bool = False) -> bool:
    """Check data quality, optionally raising on issues."""
    report = data_quality_report(df)
    if report.get("error"):
        if strict:
            raise ValueError(report["error"])
        return False

    if strict and report["summary"]["has_issues"]:
        raise ValueError(f"Data quality issues detected: {report['summary']}")

    return report["summary"]["all_finite"] or not report["summary"]["has_issues"]
