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
            median_gap = gaps.median()
            if pd.isna(median_gap):
                report["index"]["gaps"] = {"count": 0, "large_gaps": 0}
            else:
                large_gaps = gaps[gaps > median_gap * 2]
                report["index"]["gaps"] = {
                    "count": int(large_gaps.count()),
                    "large_gaps": int(large_gaps.count()),
                    "median_gap": str(median_gap),
                }
    else:
        report["index"]["gaps"] = {"count": 0}

    report["columns"] = []
    for col in df.columns:
        col_data = df[col]
        try:
            numeric = pd.to_numeric(col_data, errors="coerce")
            arr = numeric.to_numpy(dtype=float)
        except Exception:
            arr = np.array([np.nan] * len(col_data))

        finite_mask = np.isfinite(arr)
        finite_arr = arr[finite_mask] if np.any(finite_mask) else np.array([])

        outlier_info = {}
        if len(finite_arr) >= 3:
            # Z-score based outliers
            mean_f = np.mean(finite_arr)
            std_f = np.std(finite_arr)
            if std_f > 0:
                z_scores = np.abs((finite_arr - mean_f) / std_f)
                outlier_info["zscore_outliers"] = int(np.sum(z_scores > 3))
            # IQR based outliers
            q1, q3 = np.percentile(finite_arr, [25, 75])
            iqr = q3 - q1
            if iqr > 0:
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                outlier_info["iqr_outliers"] = int(np.sum((finite_arr < lower) | (finite_arr > upper)))
            elif std_f > 0:  # fallback if iqr is 0
                outlier_info["iqr_outliers"] = outlier_info.get("zscore_outliers", 0)

        # Stale data detection (consecutive equal values)
        stale_count = 0
        if len(arr) > 1:
            # Check for consecutive equal finite values
            for i in range(1, len(arr)):
                if np.isfinite(arr[i]) and np.isfinite(arr[i - 1]) and arr[i] == arr[i - 1]:
                    stale_count += 1

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
            "outliers": outlier_info,
            "stale_consecutive": int(stale_count),
        })

    report["summary"] = {
        "total_missing": sum(c["missing"] for c in report["columns"]),
        "all_finite": all(c["missing"] == 0 and c["inf"] == 0 for c in report["columns"]),
        "has_issues": any(
            c["missing_pct"] > 0.01 or c["inf"] > 0 or
            c.get("outliers", {}).get("zscore_outliers", 0) > 0 or
            c.get("stale_consecutive", 0) > len(df) * 0.05
            for c in report["columns"]
        ),
        "has_duplicates": bool(report["index"]["has_duplicates"]),
        "large_gaps": report["index"]["gaps"].get("large_gaps", 0) if isinstance(report["index"].get("gaps"), dict) else 0,
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


def detect_gaps(df: pd.DataFrame, max_gap_multiplier: float = 2.0) -> dict[str, Any]:
    """Detect time gaps in datetime index."""
    if not isinstance(df.index, pd.DatetimeIndex) or len(df.index) < 2:
        return {"gaps": [], "count": 0}

    gaps = df.index.to_series().diff()
    median_gap = gaps.median()
    if pd.isna(median_gap) or median_gap == 0:
        return {"gaps": [], "count": 0}

    large_gaps = gaps[gaps > median_gap * max_gap_multiplier]
    gap_details = []
    for idx, gap_val in large_gaps.items():
        gap_details.append({
            "after": str(df.index[df.index.get_loc(idx) - 1] if df.index.get_loc(idx) > 0 else idx),
            "gap": str(gap_val),
            "gap_days": gap_val.total_seconds() / 86400 if hasattr(gap_val, 'total_seconds') else float(gap_val),
        })
    return {"gaps": gap_details, "count": len(gap_details)}


def detect_outliers(df: pd.DataFrame, method: str = "zscore", threshold: float = 3.0) -> dict[str, Any]:
    """Detect outliers using z-score or IQR method."""
    results = {}
    for col in df.columns:
        try:
            numeric = pd.to_numeric(df[col], errors="coerce")
            arr = numeric.to_numpy(dtype=float)
            finite_mask = np.isfinite(arr)
            finite_arr = arr[finite_mask]
            if len(finite_arr) < 3:
                results[col] = {"outliers": [], "count": 0}
                continue

            if method == "zscore":
                mean_f = np.mean(finite_arr)
                std_f = np.std(finite_arr)
                if std_f == 0:
                    results[col] = {"outliers": [], "count": 0}
                    continue
                z_scores = np.abs((finite_arr - mean_f) / std_f)
                outlier_indices = np.where(z_scores > threshold)[0]
                results[col] = {
                    "outliers": outlier_indices.tolist(),
                    "count": int(len(outlier_indices)),
                    "values": finite_arr[outlier_indices].tolist() if len(outlier_indices) > 0 else []
                }
            elif method == "iqr":
                q1, q3 = np.percentile(finite_arr, [25, 75])
                iqr = q3 - q1
                if iqr == 0:
                    results[col] = {"outliers": [], "count": 0}
                    continue
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                outlier_indices = np.where((finite_arr < lower) | (finite_arr > upper))[0]
                results[col] = {
                    "outliers": outlier_indices.tolist(),
                    "count": int(len(outlier_indices)),
                    "values": finite_arr[outlier_indices].tolist() if len(outlier_indices) > 0 else []
                }
            else:
                results[col] = {"outliers": [], "count": 0}
        except Exception:
            results[col] = {"outliers": [], "count": 0}
    return results


def detect_stale_data(df: pd.DataFrame, threshold: int = 3) -> dict[str, Any]:
    """Detect consecutive identical values (stale/frozen data)."""
    results = {}
    for col in df.columns:
        try:
            arr = pd.to_numeric(df[col], errors="coerce").to_numpy(dtype=float)
            stale_runs = []
            if len(arr) > 1:
                current_run = 1
                for i in range(1, len(arr)):
                    if np.isfinite(arr[i]) and np.isfinite(arr[i - 1]) and arr[i] == arr[i - 1]:
                        current_run += 1
                    else:
                        if current_run >= threshold:
                            stale_runs.append({"length": current_run, "end_index": i - 1})
                        current_run = 1
                if current_run >= threshold:
                    stale_runs.append({"length": current_run, "end_index": len(arr) - 1})
            results[col] = {"stale_runs": stale_runs, "count": len(stale_runs)}
        except Exception:
            results[col] = {"stale_runs": [], "count": 0}
    return results


def detect_volume_anomalies(df: pd.DataFrame, volume_cols: list[str] | None = None, threshold: float = 5.0) -> dict[str, Any]:
    """Detect volume anomalies (spikes/crashes). Assumes volume data if columns named volume/vol."""
    if volume_cols is None:
        volume_cols = [c for c in df.columns if str(c).lower() in ('volume', 'vol', 'turnover')]

    results = {}
    for col in volume_cols:
        if col not in df.columns:
            continue
        try:
            arr = pd.to_numeric(df[col], errors="coerce").to_numpy(dtype=float)
            finite_mask = np.isfinite(arr)
            finite_arr = arr[finite_mask]
            if len(finite_arr) < 3:
                results[col] = {"anomalies": [], "count": 0}
                continue
            median = np.median(finite_arr)
            if median == 0:
                results[col] = {"anomalies": [], "count": 0}
                continue
            # Ratio-based detection
            ratios = arr / median if median != 0 else arr
            anomaly_mask = (ratios > threshold) | (ratios < (1 / threshold))
            anomaly_indices = np.where(anomaly_mask & finite_mask)[0]
            results[col] = {
                "anomalies": anomaly_indices.tolist(),
                "count": int(len(anomaly_indices)),
                "ratio_threshold": threshold,
            }
        except Exception:
            results[col] = {"anomalies": [], "count": 0}
    return results


def detect_duplicate_timestamps(df: pd.DataFrame) -> dict[str, Any]:
    """Detect duplicate timestamps in index."""
    if hasattr(df.index, 'has_duplicates'):
        has_dups = bool(df.index.has_duplicates)
        if has_dups:
            dup_mask = df.index.duplicated(keep=False)
            dup_indices = df.index[dup_mask].tolist()
            return {"has_duplicates": True, "count": int(dup_mask.sum()), "duplicates": dup_indices[:100]}  # limit output
        return {"has_duplicates": False, "count": 0}
    return {"has_duplicates": False, "count": 0}


def compute_quality(df: pd.DataFrame) -> pd.DataFrame:
    """Compute quality scores for each column/row. Returns DataFrame for compatibility."""
    report = data_quality_report(df)
    if report.get("error"):
        return pd.DataFrame({"error": [report["error"]]})

    # Build quality metrics DataFrame
    results = []
    for col_info in report.get("columns", []):
        score = 1.0
        if col_info.get("missing_pct", 0) > 0:
            score -= col_info["missing_pct"] * 0.5
        if col_info.get("inf", 0) > 0:
            score -= min(0.3, col_info["inf"] / len(df) if len(df) > 0 else 0.3)
        if col_info.get("outliers", {}).get("zscore_outliers", 0) > 0:
            score -= min(0.2, col_info["outliers"]["zscore_outliers"] / len(df) if len(df) > 0 else 0.2)
        if col_info.get("stale_consecutive", 0) > len(df) * 0.05:
            score -= 0.1
        score = max(0.0, score)
        results.append({
            "column": col_info["name"],
            "quality_score": score,
            "missing_pct": col_info.get("missing_pct", 0),
            "completeness": 1.0 - col_info.get("missing_pct", 0),
        })

    if not results:
        return pd.DataFrame()
    return pd.DataFrame(results)
