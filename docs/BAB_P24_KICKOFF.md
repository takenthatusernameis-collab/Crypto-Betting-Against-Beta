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
