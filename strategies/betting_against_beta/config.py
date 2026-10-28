"""Configuration for Betting Against Beta strategy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


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