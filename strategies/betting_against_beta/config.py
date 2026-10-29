"""Configuration for Betting Against Beta strategy."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional


def _is_finite_number(value) -> bool:
    """Return True if ``value`` converts to a finite float, never raising."""
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


class BABConfigError(ValueError):
    """Raised when BABConfig fields are out of their valid ranges."""


@dataclass(frozen=False)
class BABConfig:
    """Configuration for BAB strategy."""
    universe: Optional[List[str]] = None
    benchmark: str = "BTC"
    beta_window: int = 90  # days for rolling beta calculation
    rebalance_freq: str = "daily"
    long_quantile: float = 0.3  # go long bottom beta quantile
    short_quantile: float = 0.3  # go short top beta quantile
    dollar_neutral: bool = True
    min_observations: int = 60
    # Data source configuration. When None, synthetic data is generated.
    # Otherwise pass a path (CSV/JSON) or a pandas DataFrame to BABStrategy.run().
    data_source: Optional[object] = None
    # Minimum number of return rows required when loading real data.
    min_rows: int = 2
    # Transaction costs as a fraction of turnover (applied in backtest).
    transaction_costs: float = 0.0
    # Slippage as a fraction of turnover (applied in backtest).
    slippage: float = 0.0
    # Liquidity/participation constraints (lightweight guards; no-op if data absent)
    max_turnover: Optional[float] = None  # max daily turnover (sum of |Δw|/2 or total turnover) if enforced
    max_position_size: Optional[float] = None  # max |weight| per asset
    max_total_turnover: Optional[float] = None  # alias for max_turnover
    # Rolling beta parameters.
    rolling_min_window: int = 60
    # Seed for synthetic data generation.
    synthetic_seed: int = 42
    # Number of synthetic days generated when no data source is provided.
    synthetic_n_days: int = 252
    # Optional fixed universe override when loading from a data source.
    # When None, the universe is derived from the data columns.
    universe_override: Optional[List[str]] = None
    # Dynamic position sizing (optional): instance of sizer or string shorthand
    position_sizer: Optional[object] = None
    # Shorting constraints (borrow costs, availability, caps)
    shorting_constraints: Optional[object] = None
    # Regime detection parameters
    regime_filter: bool = False
    regime_method: str = "vol"  # "vol" | "trend" | "combined"
    vol_window: int = 20
    vol_use_ewma: bool = False
    vol_thresholds: Optional[tuple[float, ...]] = None  # fixed vol band edges (low, high)
    vol_percentiles: Optional[tuple[float, float]] = (0.33, 0.66)  # percentile band edges
    vol_hysteresis: float = 0.0  # regime-change hysteresis margin in [0, 1]
    trend_ma_window: int = 50
    trend_z_window: Optional[int] = None  # z-score window for trend regime (None => moving average)
    regime_scale_high: float = 0.5  # scale applied in high-risk regime
    regime_scale_low: float = 1.0   # scale applied in low-risk regime
    # Beta-neutral enforcement parameters
    beta_neutral: bool = False
    beta_neutral_enforcement: bool = False
    beta_target: float = 0.0
    beta_tolerance: float = 1e-4
    max_beta_drift: float = 1e-4
    tracking_error_tolerance: Optional[float] = None
    tracking_error_limit: Optional[float] = None
    enable_tracking_error_monitoring: bool = False
    beta_neutral_correction: bool = True
    beta_neutral_adjustment: bool = True

    def __post_init__(self):
        if self.universe is None:
            object.__setattr__(self, "universe", ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT"])
        # Normalize shorting_constraints if passed as dict
        try:
            if isinstance(self.shorting_constraints, dict):
                from . import shorting as _shorting
                object.__setattr__(self, "shorting_constraints", _shorting.ShortingConstraints(**self.shorting_constraints))
        except Exception:
            pass
        self._validate_ranges()
        # Freeze after validation to prevent downstream mutation
        try:
            object.__setattr__(self, "_frozen", True)
        except Exception:
            pass

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False) and name != "_frozen":
            raise AttributeError(f"Cannot mutate frozen BABConfig attribute '{name}'")
        object.__setattr__(self, name, value)

    def _validate_ranges(self) -> None:
        """Validate numeric ranges with helpful errors; never silently coerce."""
        errors: list[str] = []

        if not isinstance(self.beta_window, int) or isinstance(self.beta_window, bool):
            errors.append(f"beta_window must be an int, got {type(self.beta_window).__name__}")
        elif self.beta_window < 1:
            errors.append(f"beta_window must be >= 1, got {self.beta_window}")

        if not isinstance(self.min_observations, int) or isinstance(self.min_observations, bool):
            errors.append(
                f"min_observations must be an int, got {type(self.min_observations).__name__}"
            )
        elif self.min_observations < 1:
            errors.append(f"min_observations must be >= 1, got {self.min_observations}")

        if not isinstance(self.min_rows, int) or isinstance(self.min_rows, bool):
            errors.append(f"min_rows must be an int, got {type(self.min_rows).__name__}")
        elif self.min_rows < 1:
            errors.append(f"min_rows must be >= 1, got {self.min_rows}")

        if not isinstance(self.synthetic_n_days, int) or isinstance(self.synthetic_n_days, bool):
            errors.append(
                f"synthetic_n_days must be an int, got {type(self.synthetic_n_days).__name__}"
            )
        elif self.synthetic_n_days < 2:
            errors.append(f"synthetic_n_days must be >= 2, got {self.synthetic_n_days}")

        if not isinstance(self.synthetic_seed, int) or isinstance(self.synthetic_seed, bool):
            errors.append(
                f"synthetic_seed must be an int, got {type(self.synthetic_seed).__name__}"
            )

        if not isinstance(self.vol_window, int) or isinstance(self.vol_window, bool):
            errors.append(f"vol_window must be an int, got {type(self.vol_window).__name__}")
        elif self.vol_window < 10:
            errors.append(f"vol_window must be >= 10, got {self.vol_window}")

        if not isinstance(self.trend_ma_window, int) or isinstance(self.trend_ma_window, bool):
            errors.append(f"trend_ma_window must be an int, got {type(self.trend_ma_window).__name__}")
        elif self.trend_ma_window < 1:
            errors.append(f"trend_ma_window must be >= 1, got {self.trend_ma_window}")

        if self.trend_z_window is not None:
            if not isinstance(self.trend_z_window, int) or isinstance(self.trend_z_window, bool):
                errors.append(f"trend_z_window must be an int or None, got {type(self.trend_z_window).__name__}")
            elif self.trend_z_window < 1:
                errors.append(f"trend_z_window must be >= 1 when set, got {self.trend_z_window}")

        if not isinstance(self.regime_filter, bool):
            errors.append(f"regime_filter must be a bool, got {type(self.regime_filter).__name__}")

        if self.regime_method not in ("vol", "trend", "combined"):
            errors.append(f"regime_method must be one of 'vol', 'trend', 'combined', got {self.regime_method!r}")

        if not isinstance(self.vol_use_ewma, bool):
            errors.append(f"vol_use_ewma must be a bool, got {type(self.vol_use_ewma).__name__}")

        # Volatility thresholds: positive band edges, sorted when two are given.
        if self.vol_thresholds is not None:
            if not isinstance(self.vol_thresholds, (tuple, list)) or len(self.vol_thresholds) == 0:
                errors.append("vol_thresholds must be a non-empty tuple/list of positive floats")
            else:
                for i, v in enumerate(self.vol_thresholds):
                    if not isinstance(v, (int, float)) or isinstance(v, bool) or not _is_finite_number(v):
                        errors.append(f"vol_thresholds[{i}] must be a positive finite float, got {v!r}")
                    elif float(v) <= 0:
                        errors.append(f"vol_thresholds[{i}] must be > 0, got {v}")
                if len(self.vol_thresholds) >= 2 and not all(
                    float(self.vol_thresholds[i]) < float(self.vol_thresholds[i + 1])
                    for i in range(len(self.vol_thresholds) - 1)
                ):
                    errors.append("vol_thresholds must be strictly increasing")

        # Volatility percentiles: two values in (0, 1), ascending.
        if self.vol_percentiles is not None:
            if not isinstance(self.vol_percentiles, (tuple, list)) or len(self.vol_percentiles) != 2:
                errors.append("vol_percentiles must be a tuple/list of two floats in (0, 1)")
            else:
                for i, v in enumerate(self.vol_percentiles):
                    if not isinstance(v, (int, float)) or isinstance(v, bool) or not (0.0 < float(v) < 1.0):
                        errors.append(f"vol_percentiles[{i}] must be in (0, 1), got {v!r}")
                if float(self.vol_percentiles[0]) >= float(self.vol_percentiles[1]):
                    errors.append("vol_percentiles must be ascending (p_low < p_high)")

        if not isinstance(self.vol_hysteresis, (int, float)) or isinstance(self.vol_hysteresis, bool):
            errors.append(f"vol_hysteresis must be numeric, got {type(self.vol_hysteresis).__name__}")
        elif not (0.0 <= float(self.vol_hysteresis) <= 1.0):
            errors.append(f"vol_hysteresis must be in [0, 1], got {self.vol_hysteresis}")

        for name in ("regime_scale_high", "regime_scale_low"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"{name} must be numeric, got {type(value).__name__}")
            elif not _is_finite_number(value) or float(value) <= 0:
                errors.append(f"{name} must be a positive finite number, got {value}")

        # Beta-neutral params
        for name in ("beta_neutral", "beta_neutral_enforcement", "beta_neutral_correction", "beta_neutral_adjustment", "enable_tracking_error_monitoring"):
            value = getattr(self, name)
            if not isinstance(value, bool):
                errors.append(f"{name} must be a bool, got {type(value).__name__}")

        for name in ("beta_target", "beta_tolerance", "max_beta_drift"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"{name} must be numeric, got {type(value).__name__}")
            elif not _is_finite_number(value):
                errors.append(f"{name} must be finite, got {value}")
            elif float(value) < 0:
                errors.append(f"{name} must be >= 0, got {value}")

        for name in ("tracking_error_tolerance", "tracking_error_limit"):
            value = getattr(self, name)
            if value is None:
                continue
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"{name} must be numeric or None, got {type(value).__name__}")
            elif not _is_finite_number(value) or float(value) < 0:
                errors.append(f"{name} must be a non-negative finite number when set, got {value}")
        # be forced when they contradict; require at least one vol band source.
        if self.vol_thresholds is not None and self.vol_percentiles is not None:
            errors.append("set only one of vol_thresholds or vol_percentiles, not both")

        for name in ("long_quantile", "short_quantile"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"{name} must be numeric, got {type(value).__name__}")
            elif not (0.0 < value < 1.0):
                errors.append(f"{name} must be in (0, 1), got {value}")

        for name in ("transaction_costs", "slippage"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"{name} must be numeric, got {type(value).__name__}")
            elif value < 0:
                errors.append(f"{name} must be >= 0, got {value}")

        for name in ("max_turnover", "max_position_size", "max_total_turnover", "rolling_min_window"):
            value = getattr(self, name)
            if value is None:
                continue
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"{name} must be numeric or None, got {type(value).__name__}")
            elif value <= 0:
                errors.append(f"{name} must be > 0 when set, got {value}")

        if not isinstance(self.rebalance_freq, str) or not self.rebalance_freq.strip():
            errors.append("rebalance_freq must be a non-empty string")

        if self.benchmark is None or not isinstance(self.benchmark, str) or not self.benchmark.strip():
            errors.append("benchmark must be a non-empty string")

        if errors:
            raise BABConfigError("; ".join(errors))

    def resolved_universe(self, returns_columns: list[str] | None = None) -> List[str]:
        """Return the effective universe.

        - If ``universe_override`` is set, use it (intersected with available columns).
        - Else if ``universe`` is set, use it (intersected with available columns).
        - Else derive from the returns columns, excluding the benchmark.
        """
        if returns_columns is None:
            return list(self.universe) if self.universe else []

        available = [str(c) for c in returns_columns]
        if self.universe_override is not None:
            candidate = [a for a in self.universe_override if a in available]
            return candidate or available
        if self.universe is not None:
            candidate = [a for a in self.universe if a in available]
            if candidate:
                return candidate
        return [c for c in available if c != self.benchmark]