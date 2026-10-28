"""Configuration for Betting Against Beta strategy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
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
    # Rolling beta parameters.
    rolling_min_window: int = 60
    # Seed for synthetic data generation.
    synthetic_seed: int = 42
    # Number of synthetic days generated when no data source is provided.
    synthetic_n_days: int = 252
    # Optional fixed universe override when loading from a data source.
    # When None, the universe is derived from the data columns.
    universe_override: Optional[List[str]] = None

    def __post_init__(self):
        if self.universe is None:
            self.universe = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT"]

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