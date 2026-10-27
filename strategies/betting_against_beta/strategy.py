"""High-level Betting Against Beta (BAB) strategy entrypoint."""

from __future__ import annotations

from dataclasses import dataclass

from .backtest import run_backtest
from .beta import calculate_rolling_beta
from .config import BABConfig
from .data import generate_synthetic_returns
from .portfolio import construct_portfolio
from .signals import generate_bab_signals


@dataclass
class BABResult:
    """Output of running the BAB strategy."""

    config: BABConfig
    returns: object  # pd.DataFrame of input returns
    betas: object  # pd.DataFrame of rolling betas
    signals: object  # pd.DataFrame of long/short signals
    weights: object  # pd.DataFrame of portfolio weights
    backtest: object  # pd.DataFrame of backtest results


class BABStrategy:
    """Betting Against Beta strategy: long low-beta, short high-beta crypto assets.

    Pipeline:
        1. Estimate rolling beta of each asset vs the benchmark.
        2. Rank assets by beta each period.
        3. Go long the lowest-beta quantile, short the highest-beta quantile.
        4. Construct dollar-neutral (or long-only) equal weights.
        5. Backtest with one-day lagged weights (no lookahead).
    """

    def __init__(self, config: BABConfig | None = None) -> None:
        self.config = config or BABConfig()

    def run(self, returns_df: object | None = None) -> BABResult:  # noqa: ANN401
        """Run the full strategy pipeline and return results."""
        cfg = self.config
        if returns_df is None:
            returns_df = generate_synthetic_returns(
                n_days=252,
                n_assets=len(cfg.universe),
                asset_names=list(cfg.universe),
                benchmark_name=cfg.benchmark,
            )

        betas = calculate_rolling_beta(
            returns_df,
            cfg.benchmark,
            window=cfg.beta_window,
            min_obs=cfg.min_observations,
        )
        signals = generate_bab_signals(
            betas, long_quantile=cfg.long_quantile, short_quantile=cfg.short_quantile
        )
        weights = construct_portfolio(signals, dollar_neutral=cfg.dollar_neutral)
        backtest = run_backtest(returns_df, weights)

        return BABResult(
            config=cfg,
            returns=returns_df,
            betas=betas,
            signals=signals,
            weights=weights,
            backtest=backtest,
        )
