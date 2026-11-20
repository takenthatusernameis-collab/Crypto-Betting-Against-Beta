# BAB P24 WP0

{
  "schema": "bab_p24.charter/1",
  "provenance": {
    "generator": "scripts/bab_p24_charter.py",
    "synthetic": true,
    "note": "Controlled synthetic stimulus: not real market data.",
    "p23_source_schema": "bab_p23.charter/1",
    "universe_seed": 20261118,
    "no_go_for_market": true,
    "licensed_data_required": true,
    "p22_verdict": {
      "capacity": {
        "null_equal": {
          "bracket_halving_verified": true,
          "break_even_coefficient": 0.010507,
          "censor_reason": null,
          "censored": false,
          "gross_sharpe": 0.639801,
          "variant": "null",
          "weighting": "equal"
        },
        "null_rank": {
          "bracket_halving_verified": true,
          "break_even_coefficient": 0.015268,
          "censor_reason": null,
          "censored": false,
          "gross_sharpe": 0.649924,
          "variant": "null",
          "weighting": "rank"
        },
        "planted_equal": {
          "bracket_halving_verified": true,
          "break_even_coefficient": 0.097478,
          "censor_reason": null,
          "censored": false,
          "gross_sharpe": 7.034781,
          "variant": "planted",
          "weighting": "equal"
        },
        "planted_rank": {
          "bracket_halving_verified": false,
          "break_even_coefficient": null,
          "censor_reason": "no_negative_sharpe_at_max_coefficient",
          "censored": true,
          "gross_sharpe": 44.378201,
          "variant": "planted",
          "weighting": "rank"
        }
      },
      "impact": {
        "null_equal": {
          "gross_sharpe": 0.639801,
          "monotone": true,
          "period_wise_non_increasing": true,
          "variant": "null",
          "weighting": "equal"
        },
        "null_rank": {
          "gross_sharpe": 0.649924,
          "monotone": true,
          "period_wise_non_increasing": true,
          "variant": "null",
          "weighting": "rank"
        },
        "planted_equal": {
          "gross_sharpe": 7.034781,
          "monotone": true,
          "period_wise_non_increasing": true,
          "variant": "planted",
          "weighting": "equal"
        },
        "planted_rank": {
          "gross_sharpe": 44.378201,
          "monotone": true,
          "period_wise_non_increasing": true,
          "variant": "planted",
          "weighting": "rank"
        }
      },
      "no_go_for_market": true,
      "noise_on_null": true,
      "nominal_slack": 0.05,
      "null_battery": {
        "fpr_count": 2,
        "fpr_denominator": 40,
        "fpr_max_count_declared": 4,
        "fpr_rate": 0.05,
        "fpr_within_declared_bound": true,
        "n_null_books": 40,
        "n_planted_books": 40,
        "n_seeds": 20,
        "null_recovery_exactly_zero_every_seed": true,
        "null_recovery_max_abs": 0.0,
        "null_recovery_zero_books": 40,
        "null_sharpe_max": 1.28897,
        "planted_recovery_exceeds_null_max": true,
        "planted_recovery_min": {
          "equal": 0.000206,
          "rank": 0.017227
        },
        "planted_recovery_positive_fraction": {
          "equal": 1.0,
          "rank": 1.0
        },
        "planted_sharpe_min": 5.552134
      },
      "p22_charter_verdict": "SIGNAL on the planted controlled-synthetic universe; NOISE on the null universe; NO-GO for market deployment.",
      "signal_on_planted": true,
      "verdict": "NO-GO for market deployment"
    },
    "acceptance_thresholds": {
      "nominal_slack": 0.05,
      "wp4": {
        "explicit_signal_noise_verdict": true,
        "no_go_for_market": true,
        "no_harness_re_run": true,
        "planted_recovery_labelled_controlled_synthetic": true,
        "numbers_matched_min": 100,
        "zero_unmatched_cells": 0,
        "regime_grid_min": 2,
        "hysteresis_band_grid_min": 3,
        "turnover_monotone_non_increasing": true,
        "adapter_valid_offline": true
      }
    }
  },
  "charter": {
    "campaign": "P24",
    "title": "Regime-conditional BAB and holdout discipline",
    "binding_row": "P24 WP0",
    "artifact_gated": true,
    "not_market_evidence": true,
    "licensed_data_required": true,
    "regime_grid": [
      "calm",
      "stress"
    ],
    "holdout_before_tuning": true,
    "hysteresis_band_grid": [
      0.05,
      0.1,
      0.15
    ],
    "licensed_price_csv_schema": "tests/fixtures/licensed_price_schema.csv",
    "wps_in_order": [
      "P24 WP0 \u2014 charter"
    ]
  }
}
