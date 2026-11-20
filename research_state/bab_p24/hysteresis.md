# BAB P24 WP2 — rebalance hysteresis / turnover ladder

Schema `bab_p24.hysteresis/1`. Controlled synthetic stimulus with known ground truth: not real market data and not market profitability evidence.

Universe seed 20261118; P23 charter schema `bab_p23.charter/1`; P24 charter schema `bab_p24.charter/1`.
Regime model: Volatility regime detection via classify_volatility_regimes_percentile with vol_hysteresis from hysteresis_band_grid; regime_filter applies a single causal scalar scale factor per date (minimum across assets) via regime_scale_scalar, preserving dollar-neutrality exactly. Calm regime uses beta_window=120, quantiles=0.25; stress regime uses beta_window=60, quantiles=0.35..

| regime | hysteresis | weighting | variant | recovery_mean | turnover_mean | turnover_max | regime_flips_mean | active_rows_min | min_leg_beta | gross_max | gross_sharpe_mean | wealth_mean | beta_window | long_quantile | short_quantile |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| calm | 0.05 | equal | planted | 0.00019 | 0.047145 | 1.021539 | 52.0 | 541 | 1.461772 | 1.03602 | 4.680954 | 1.10657 | 120 | 0.25 | 0.25 |
| calm | 0.05 | equal | null | 0.0 | 0.047145 | 1.021539 | 52.0 | 541 | 1.461772 | 1.03602 | -0.061797 | 0.998582 | 120 | 0.25 | 0.25 |
| calm | 0.05 | rank | planted | 0.00019 | 0.047145 | 1.021539 | 52.0 | 541 | 1.461772 | 1.03602 | 4.680954 | 1.10657 | 120 | 0.25 | 0.25 |
| calm | 0.05 | rank | null | 0.0 | 0.047145 | 1.021539 | 52.0 | 541 | 1.461772 | 1.03602 | -0.061797 | 0.998582 | 120 | 0.25 | 0.25 |
| calm | 0.1 | equal | planted | 0.000191 | 0.043793 | 1.021539 | 48.0 | 541 | 1.461772 | 1.036523 | 4.687032 | 1.106237 | 120 | 0.25 | 0.25 |
| calm | 0.1 | equal | null | 0.0 | 0.043793 | 1.021539 | 48.0 | 541 | 1.461772 | 1.036523 | -0.103003 | 0.99771 | 120 | 0.25 | 0.25 |
| calm | 0.1 | rank | planted | 0.000191 | 0.043793 | 1.021539 | 48.0 | 541 | 1.461772 | 1.036523 | 4.687032 | 1.106237 | 120 | 0.25 | 0.25 |
| calm | 0.1 | rank | null | 0.0 | 0.043793 | 1.021539 | 48.0 | 541 | 1.461772 | 1.036523 | -0.103003 | 0.99771 | 120 | 0.25 | 0.25 |
| calm | 0.15 | equal | planted | 0.000192 | 0.042129 | 1.021539 | 46.0 | 541 | 1.461772 | 1.036523 | 4.72523 | 1.107064 | 120 | 0.25 | 0.25 |
| calm | 0.15 | equal | null | 0.0 | 0.042129 | 1.021539 | 46.0 | 541 | 1.461772 | 1.036523 | -0.086861 | 0.998056 | 120 | 0.25 | 0.25 |
| calm | 0.15 | rank | planted | 0.000192 | 0.042129 | 1.021539 | 46.0 | 541 | 1.461772 | 1.036523 | 4.72523 | 1.107064 | 120 | 0.25 | 0.25 |
| calm | 0.15 | rank | null | 0.0 | 0.042129 | 1.021539 | 46.0 | 541 | 1.461772 | 1.036523 | -0.086861 | 0.998056 | 120 | 0.25 | 0.25 |
| stress | 0.05 | equal | planted | -0.00016 | 0.037042 | 0.711838 | 52.0 | 541 | 1.464354 | 0.743608 | -6.979323 | 0.908464 | 60 | 0.35 | 0.35 |
| stress | 0.05 | equal | null | 0.0 | 0.037042 | 0.711838 | 52.0 | 541 | 1.464354 | 0.743608 | -0.730612 | 0.990243 | 60 | 0.35 | 0.35 |
| stress | 0.05 | rank | planted | -0.00016 | 0.037042 | 0.711838 | 52.0 | 541 | 1.464354 | 0.743608 | -6.979323 | 0.908464 | 60 | 0.35 | 0.35 |
| stress | 0.05 | rank | null | 0.0 | 0.037042 | 0.711838 | 52.0 | 541 | 1.464354 | 0.743608 | -0.730612 | 0.990243 | 60 | 0.35 | 0.35 |
| stress | 0.1 | equal | planted | -0.000161 | 0.034741 | 0.711838 | 48.0 | 541 | 1.464354 | 0.743608 | -6.916945 | 0.909539 | 60 | 0.35 | 0.35 |
| stress | 0.1 | equal | null | 0.0 | 0.034741 | 0.711838 | 48.0 | 541 | 1.464354 | 0.743608 | -0.605881 | 0.991888 | 60 | 0.35 | 0.35 |
| stress | 0.1 | rank | planted | -0.000161 | 0.034741 | 0.711838 | 48.0 | 541 | 1.464354 | 0.743608 | -6.916945 | 0.909539 | 60 | 0.35 | 0.35 |
| stress | 0.1 | rank | null | 0.0 | 0.034741 | 0.711838 | 48.0 | 541 | 1.464354 | 0.743608 | -0.605881 | 0.991888 | 60 | 0.35 | 0.35 |
| stress | 0.15 | equal | planted | -0.000161 | 0.033611 | 0.711838 | 46.0 | 541 | 1.464354 | 0.743608 | -6.899948 | 0.909611 | 60 | 0.35 | 0.35 |
| stress | 0.15 | equal | null | 0.0 | 0.033611 | 0.711838 | 46.0 | 541 | 1.464354 | 0.743608 | -0.574093 | 0.99229 | 60 | 0.35 | 0.35 |
| stress | 0.15 | rank | planted | -0.000161 | 0.033611 | 0.711838 | 46.0 | 541 | 1.464354 | 0.743608 | -6.899948 | 0.909611 | 60 | 0.35 | 0.35 |
| stress | 0.15 | rank | null | 0.0 | 0.033611 | 0.711838 | 46.0 | 541 | 1.464354 | 0.743608 | -0.574093 | 0.99229 | 60 | 0.35 | 0.35 |
