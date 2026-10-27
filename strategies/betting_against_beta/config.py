"""Configuration for Betting Against Beta strategy."""

from dataclasses import dataclass
from typing import List


@dataclass
class BABConfig:
    """Configuration for BAB strategy."""
    universe: List[str] = None
    benchmark: str = "BTC"
    beta_window: int = 90  # days for rolling beta calculation
    rebalance_freq: str = "daily"
    long_quantile: float = 0.3  # go long bottom beta quantile
    short_quantile: float = 0.3  # go short top beta quantile
    dollar_neutral: bool = True
    min_observations: int = 60

    def __post_init__(self):
        if self.universe is None:
            self.universe = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT"]
