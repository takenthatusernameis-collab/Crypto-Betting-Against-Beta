"""High-level Betting Against Beta (BAB) strategy entrypoint."""

from __future__ import annotations

from dataclasses import dataclass

from .backtest import run_backtest
from .beta import calculate_rolling_beta
from .config import BABConfig
from .data import generate_synthetic_returns
from .data_loader import load_returns
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
        1. Load/validate returns (synthetic by default, or from a CSV/JSON/DataFrame).
        2. Estimate rolling beta of each asset vs the benchmark.
        3. Rank assets by beta each period.
        4. Go long the lowest-beta quantile, short the highest-beta quantile.
        5. Construct dollar-neutral (or long-only) equal weights.
        6. Backtest with one-day lagged weights (no lookahead).
    """

    def __init__(self, config: BABConfig | None = None) -> None:
        self.config = config or BABConfig()

    def _load_returns(self, returns_df: object | None) -> "pd.DataFrame":  # noqa: ANN401
        """Resolve the returns DataFrame, validating it for the pipeline."""
        import pandas as pd  # local import keeps module import light

        cfg = self.config
        if returns_df is not None:
            # Explicit override wins over config.data_source.
            return load_returns(
                returns_df,
                benchmark=cfg.benchmark,
                min_rows=cfg.min_rows,
            )

        if cfg.data_source is not None:
            return load_returns(
                cfg.data_source,
                benchmark=cfg.benchmark,
                min_rows=cfg.min_rows,
            )

        universe = list(cfg.universe) if cfg.universe else None
        n_assets = len(universe) if universe else 5
        return generate_synthetic_returns(
            n_days=cfg.synthetic_n_days,
            n_assets=n_assets,
            asset_names=universe,
            benchmark_name=cfg.benchmark,
            seed=cfg.synthetic_seed,
        )

    def run(self, returns_df: object | None = None) -> BABResult:  # noqa: ANN401
        """Run the full strategy pipeline and return results."""
        cfg = self.config
        returns = self._load_returns(returns_df)

        # Resolve the effective universe from the validated data and persist it so
        # downstream consumers (reports, diagnostics) see the actual tradable
        # set rather than the configured default.
        effective_universe = cfg.resolved_universe(list(returns.columns))
        if not effective_universe:
            raise ValueError(
                "No tradable assets remain after intersecting the configured "
                f"universe {cfg.universe} with data columns {list(returns.columns)}"
            )
        cfg.universe = effective_universe

        betas = calculate_rolling_beta(
            returns,
            cfg.benchmark,
            window=cfg.beta_window,
            min_obs=cfg.min_observations,
        )
        signals = generate_bab_signals(
            betas, long_quantile=cfg.long_quantile, short_quantile=cfg.short_quantile
        )
        weights = construct_portfolio(signals, dollar_neutral=cfg.dollar_neutral)
        # Explicit finiteness guard
        try:
            import numpy as _np
            weights = weights.replace([_np.inf, -_np.inf], _np.nan).fillna(0.0)
            if hasattr(weights, 'values') and not _np.isfinite(weights.values).all():
                # coerce
                weights_arr = weights.values
                weights_arr[~_np.isfinite(weights_arr)] = 0.0
                weights = type(weights)(weights_arr, index=weights.index, columns=weights.columns)
        except Exception:
            pass
        backtest = run_backtest(returns, weights, transaction_costs=cfg.transaction_costs)

        return BABResult(
            config=cfg,
            returns=returns,
            betas=betas,
            signals=signals,
            weights=weights,
            backtest=backtest,
        )