# BAB P24 Closing Decision — Regime-Conditional BAB and Holdout Discipline

**Campaign:** P24 "Regime-conditional BAB and holdout discipline"
**Decision row:** P24 WP4 — closing decision
**Artifacts consumed (read-only):**
- `research_state/bab_p24/charter.json`
- `research_state/bab_p24/adapter_dryrun.json`
- `research_state/bab_p24/hysteresis.json`
- `research_state/bab_p24/regime_split.json`
- `research_state/bab_p23/charter.json`
- `research_state/bab_p23/breadth_ladder.json`
- `research_state/bab_p23/beta_drift.json`
- `research_state/bab_p23/short_haircut.json`
- `research_state/bab_p22/null_battery.json`
- `research_state/bab_p21/rank_eval.json`

**Verdict strings verified:** `signal`, `noise`, `no-go for market`, `controlled synthetic`, `not market evidence`

**Decision:** **NO-GO for market** — this campaign does not prove a demonstrated profitable strategy for real-world deployment. This is a **decision-grade** closing verdict: every published number traces to a committed JSON leaf, and the planted universe is labelled **controlled synthetic** throughout.

---

## Provenance

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Charter schema | bab_p24.charter/1 |
| Adapter dryrun schema | bab_p24.adapter_dryrun/1 |
| Hysteresis schema | bab_p24.hysteresis/1 |
| Regime split schema | bab_p24.regime_split/1 |
| Campaign | P24 |
| Charter title | Regime-conditional BAB and holdout discipline |
| Certified by prior campaign | True |
| Universe seed | 20261118 |
| Synthetic | True |
| Licensed data required | True |
| Not market evidence | True |
| Artifact gated | True |
| Nominal slack | 0.050000 |
| Planted panel sha256 | `aae2a70ebcf81b3a9e2dd5f314933c439194fef8a7be1da34930e2c271a93fda` |
| Null panel sha256 | `b7732c152564c87606a6a47eac39a543344cbcd4b8e974f4780be35671953b1b` |
| Reference panel shas matched | True |
| Adapter fixture valid | True |
| Adapter network used | False |
| Adapter dry run | True |
| Adapter synthetic | True |
| Hysteresis zero reference matches P21 | True |
| Hysteresis turnover monotone non-increasing | True |
| Regime grid min met | True |
| Stress regime planted negative | True |
| Breadth ladder rungs | 5 |
| Beta drift cells | 48 |
| Beta drift scale | 0.100000 |
| Short haircut book runs | 400 |
| Short haircut censored cells | 2 |
| Null battery FPR rate | 0.050000 |
| Null battery max abs recovery | 0.000000 |
<!-- table:provenance:end -->

---

## Licensed-Data Adapter Dry Run

The licensed-data adapter validates the offline CSV fixture (`tests/fixtures/licensed_price_schema.csv`) against the P21 universe contract and the P24 charter. No network is used; the adapter runs in dry-run mode with synthetic data.

<!-- table:adapter:start -->
| fixture_path | fixture_sha256 | rows | columns | date_start | valid | dry_run | network_used | synthetic | no_go_for_market | not_market_evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tests/fixtures/licensed_price_schema.csv | `3dd449d6ccbc8f9b4f52f1b424b9791fd963d41d2fec78939f14329f97cd74ce` | 5 | 43 | 2024-01-02 | True | True | False | True | True | True |
<!-- table:adapter:end -->

---

## Rebalance Hysteresis / Turnover Ladder

Hysteresis bands of 0.05, 0.10, and 0.15 were tested across calm and stress regimes with both equal and rank weighting. Tighter hysteresis bands produce more regime flips and higher turnover. The turnover ladder is monotone non-increasing as hysteresis widens.

<!-- table:hysteresis:start -->
| regime | hysteresis | weighting | variant | active_rows_min | recovery_mean | recovery_min | recovery_positive_seed_fraction | regime_flips_mean | turnover_mean | turnover_total | wealth_mean | gross_sharpe_mean | gross_max | min_leg_beta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| calm | 0.050000 | equal | planted | 541 | 0.000190 | 0.000190 | 1.000000 | 52.000000 | 0.047145 | 28.287065 | 1.106570 | 4.680954 | 1.036020 | 1.461772 |
| calm | 0.050000 | equal | null | 541 | 0.000000 | 0.000000 | 0.000000 | 52.000000 | 0.047145 | 28.287065 | 0.998582 | -0.061797 | 1.036020 | 1.461772 |
| calm | 0.050000 | rank | planted | 541 | 0.000190 | 0.000190 | 1.000000 | 52.000000 | 0.047145 | 28.287065 | 1.106570 | 4.680954 | 1.036020 | 1.461772 |
| calm | 0.050000 | rank | null | 541 | 0.000000 | 0.000000 | 0.000000 | 52.000000 | 0.047145 | 28.287065 | 0.998582 | -0.061797 | 1.036020 | 1.461772 |
| calm | 0.100000 | equal | planted | 541 | 0.000191 | 0.000191 | 1.000000 | 48.000000 | 0.043793 | 26.275902 | 1.106237 | 4.687032 | 1.036523 | 1.461772 |
| calm | 0.100000 | equal | null | 541 | 0.000000 | 0.000000 | 0.000000 | 48.000000 | 0.043793 | 26.275902 | 0.997710 | -0.103003 | 1.036523 | 1.461772 |
| calm | 0.100000 | rank | planted | 541 | 0.000191 | 0.000191 | 1.000000 | 48.000000 | 0.043793 | 26.275902 | 1.106237 | 4.687032 | 1.036523 | 1.461772 |
| calm | 0.100000 | rank | null | 541 | 0.000000 | 0.000000 | 0.000000 | 48.000000 | 0.043793 | 26.275902 | 0.997710 | -0.103003 | 1.036523 | 1.461772 |
| calm | 0.150000 | equal | planted | 541 | 0.000192 | 0.000192 | 1.000000 | 46.000000 | 0.042129 | 25.277443 | 1.107064 | 4.725230 | 1.036523 | 1.461772 |
| calm | 0.150000 | equal | null | 541 | 0.000000 | 0.000000 | 0.000000 | 46.000000 | 0.042129 | 25.277443 | 0.998056 | -0.086861 | 1.036523 | 1.461772 |
| calm | 0.150000 | rank | planted | 541 | 0.000192 | 0.000192 | 1.000000 | 46.000000 | 0.042129 | 25.277443 | 1.107064 | 4.725230 | 1.036523 | 1.461772 |
| calm | 0.150000 | rank | null | 541 | 0.000000 | 0.000000 | 0.000000 | 46.000000 | 0.042129 | 25.277443 | 0.998056 | -0.086861 | 1.036523 | 1.461772 |
| stress | 0.050000 | equal | planted | 541 | -0.000160 | -0.000160 | 0.000000 | 52.000000 | 0.037042 | 22.225271 | 0.908464 | -6.979323 | 0.743608 | 1.464354 |
| stress | 0.050000 | equal | null | 541 | 0.000000 | 0.000000 | 0.000000 | 52.000000 | 0.037042 | 22.225271 | 0.990243 | -0.730612 | 0.743608 | 1.464354 |
| stress | 0.050000 | rank | planted | 541 | -0.000160 | -0.000160 | 0.000000 | 52.000000 | 0.037042 | 22.225271 | 0.908464 | -6.979323 | 0.743608 | 1.464354 |
| stress | 0.050000 | rank | null | 541 | 0.000000 | 0.000000 | 0.000000 | 52.000000 | 0.037042 | 22.225271 | 0.990243 | -0.730612 | 0.743608 | 1.464354 |
| stress | 0.100000 | equal | planted | 541 | -0.000161 | -0.000161 | 0.000000 | 48.000000 | 0.034741 | 20.844402 | 0.909539 | -6.916945 | 0.743608 | 1.464354 |
| stress | 0.100000 | equal | null | 541 | 0.000000 | 0.000000 | 0.000000 | 48.000000 | 0.034741 | 20.844402 | 0.991888 | -0.605881 | 0.743608 | 1.464354 |
| stress | 0.100000 | rank | planted | 541 | -0.000161 | -0.000161 | 0.000000 | 48.000000 | 0.034741 | 20.844402 | 0.909539 | -6.916945 | 0.743608 | 1.464354 |
| stress | 0.100000 | rank | null | 541 | 0.000000 | 0.000000 | 0.000000 | 48.000000 | 0.034741 | 20.844402 | 0.991888 | -0.605881 | 0.743608 | 1.464354 |
| stress | 0.150000 | equal | planted | 541 | -0.000161 | -0.000161 | 0.000000 | 46.000000 | 0.033611 | 20.166474 | 0.909611 | -6.899948 | 0.743608 | 1.464354 |
| stress | 0.150000 | equal | null | 541 | 0.000000 | 0.000000 | 0.000000 | 46.000000 | 0.033611 | 20.166474 | 0.992290 | -0.574093 | 0.743608 | 1.464354 |
| stress | 0.150000 | rank | planted | 541 | -0.000161 | -0.000161 | 0.000000 | 46.000000 | 0.033611 | 20.166474 | 0.909611 | -6.899948 | 0.743608 | 1.464354 |
| stress | 0.150000 | rank | null | 541 | 0.000000 | 0.000000 | 0.000000 | 46.000000 | 0.033611 | 20.166474 | 0.992290 | -0.574093 | 0.743608 | 1.464354 |
<!-- table:hysteresis:end -->

---

## Regime-Split Stress Test

The regime grid defines **calm** (beta_window=120, quantiles=0.25, hysteresis=0.05) and **stress** (beta_window=60, quantiles=0.35, hysteresis=0.05). Planted recovery is strictly positive in calm and negative in stress; null recovery is exactly zero in both.

<!-- table:regime:start -->
| regime | beta_window | long_quantile | short_quantile | hysteresis | weighting | variant | active_rows_min | recovery_mean | recovery_min | recovery_positive_seed_fraction | gross_sharpe_mean | wealth_mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| calm | 120 | 0.250000 | 0.250000 | 0.050000 | equal | planted | 541 | 0.000190 | 0.000190 | 1.000000 | 4.680954 | 1.106570 |
| calm | 120 | 0.250000 | 0.250000 | 0.050000 | equal | null | 541 | 0.000000 | 0.000000 | 0.000000 | -0.061797 | 0.998582 |
| calm | 120 | 0.250000 | 0.250000 | 0.050000 | rank | planted | 541 | 0.000190 | 0.000190 | 1.000000 | 4.680954 | 1.106570 |
| calm | 120 | 0.250000 | 0.250000 | 0.050000 | rank | null | 541 | 0.000000 | 0.000000 | 0.000000 | -0.061797 | 0.998582 |
| calm | 120 | 0.250000 | 0.250000 | 0.100000 | equal | planted | 541 | 0.000191 | 0.000191 | 1.000000 | 4.687032 | 1.106237 |
| calm | 120 | 0.250000 | 0.250000 | 0.100000 | equal | null | 541 | 0.000000 | 0.000000 | 0.000000 | -0.103003 | 0.997710 |
| calm | 120 | 0.250000 | 0.250000 | 0.100000 | rank | planted | 541 | 0.000191 | 0.000191 | 1.000000 | 4.687032 | 1.106237 |
| calm | 120 | 0.250000 | 0.250000 | 0.100000 | rank | null | 541 | 0.000000 | 0.000000 | 0.000000 | -0.103003 | 0.997710 |
| calm | 120 | 0.250000 | 0.250000 | 0.150000 | equal | planted | 541 | 0.000192 | 0.000192 | 1.000000 | 4.725230 | 1.107064 |
| calm | 120 | 0.250000 | 0.250000 | 0.150000 | equal | null | 541 | 0.000000 | 0.000000 | 0.000000 | -0.086861 | 0.998056 |
| calm | 120 | 0.250000 | 0.250000 | 0.150000 | rank | planted | 541 | 0.000192 | 0.000192 | 1.000000 | 4.725230 | 1.107064 |
| calm | 120 | 0.250000 | 0.250000 | 0.150000 | rank | null | 541 | 0.000000 | 0.000000 | 0.000000 | -0.086861 | 0.998056 |
| stress | 60 | 0.350000 | 0.350000 | 0.050000 | equal | planted | 541 | -0.000160 | -0.000160 | 0.000000 | -6.979323 | 0.908464 |
| stress | 60 | 0.350000 | 0.350000 | 0.050000 | equal | null | 541 | 0.000000 | 0.000000 | 0.000000 | -0.730612 | 0.990243 |
| stress | 60 | 0.350000 | 0.350000 | 0.050000 | rank | planted | 541 | -0.000160 | -0.000160 | 0.000000 | -6.979323 | 0.908464 |
| stress | 60 | 0.350000 | 0.350000 | 0.050000 | rank | null | 541 | 0.000000 | 0.000000 | 0.000000 | -0.730612 | 0.990243 |
| stress | 60 | 0.350000 | 0.350000 | 0.100000 | equal | planted | 541 | -0.000161 | -0.000161 | 0.000000 | -6.916945 | 0.909539 |
| stress | 60 | 0.350000 | 0.350000 | 0.100000 | equal | null | 541 | 0.000000 | 0.000000 | 0.000000 | -0.605881 | 0.991888 |
| stress | 60 | 0.350000 | 0.350000 | 0.100000 | rank | planted | 541 | -0.000161 | -0.000161 | 0.000000 | -6.916945 | 0.909539 |
| stress | 60 | 0.350000 | 0.350000 | 0.100000 | rank | null | 541 | 0.000000 | 0.000000 | 0.000000 | -0.605881 | 0.991888 |
| stress | 60 | 0.350000 | 0.350000 | 0.150000 | equal | planted | 541 | -0.000161 | -0.000161 | 0.000000 | -6.899948 | 0.909611 |
| stress | 60 | 0.350000 | 0.350000 | 0.150000 | equal | null | 541 | 0.000000 | 0.000000 | 0.000000 | -0.574093 | 0.992290 |
| stress | 60 | 0.350000 | 0.350000 | 0.150000 | rank | planted | 541 | -0.000161 | -0.000161 | 0.000000 | -6.899948 | 0.909611 |
| stress | 60 | 0.350000 | 0.350000 | 0.150000 | rank | null | 541 | 0.000000 | 0.000000 | 0.000000 | -0.574093 | 0.992290 |
<!-- table:regime:end -->

---

## Breadth Ladder (P23)

Five rungs spanning 9 to 41 assets, all with strictly positive planted recovery. Null recovery is exactly zero.

<!-- table:breadth:start -->
| breadth | variant | weighting | active_rows | recovery_mean | recovery_frac_positive | gross_max | min_leg_beta | gross_sharpe | wealth |
|---|---|---|---|---|---|---|---|---|---|
| 9 | planted | equal | 541 | 0.000852 | 1.000000 | 0.881117 | 1.364515 | 11.849343 | 1.627791 |
| 9 | planted | rank | 541 | 0.019102 | 1.000000 | 2.627291 | 0.466667 | 38.472484 | 31548.052226 |
| 9 | null | equal | 541 | 0.000000 | 0.000000 | 0.881117 | 1.364515 | 0.696904 | 1.027840 |
| 9 | null | rank | 541 | 0.000000 | 0.000000 | 2.627291 | 0.466667 | 0.935453 | 1.155184 |
| 17 | planted | equal | 541 | 0.000574 | 1.000000 | 0.908097 | 1.412831 | 9.352958 | 1.378100 |
| 17 | planted | rank | 541 | 0.018663 | 1.000000 | 2.558507 | 0.475200 | 41.365882 | 23997.088351 |
| 17 | null | equal | 541 | 0.000000 | 0.000000 | 0.908097 | 1.412831 | 0.323055 | 1.010705 |
| 17 | null | rank | 541 | 0.000000 | 0.000000 | 2.558507 | 0.475200 | 0.873485 | 1.108250 |
| 25 | planted | equal | 541 | 0.000426 | 1.000000 | 0.901197 | 1.430700 | 8.609136 | 1.285226 |
| 25 | planted | rank | 541 | 0.018240 | 1.000000 | 2.507432 | 0.487347 | 42.600863 | 19120.623173 |
| 25 | null | equal | 541 | 0.000000 | 0.000000 | 0.901197 | 1.430700 | 0.738474 | 1.021241 |
| 25 | null | rank | 541 | 0.000000 | 0.000000 | 2.507432 | 0.487347 | 0.980300 | 1.104535 |
| 33 | planted | equal | 541 | 0.000310 | 0.996303 | 0.837902 | 1.444941 | 7.549534 | 1.190974 |
| 33 | planted | rank | 541 | 0.017361 | 1.000000 | 2.428612 | 0.505455 | 43.961525 | 11367.799782 |
| 33 | null | equal | 541 | 0.000000 | 0.000000 | 0.837902 | 1.444941 | 0.324571 | 1.007344 |
| 33 | null | rank | 541 | 0.000000 | 0.000000 | 2.428612 | 0.505455 | 0.569659 | 1.045939 |
| 41 | planted | equal | 541 | 0.000261 | 0.996303 | 0.837141 | 1.447792 | 7.034781 | 1.167118 |
| 41 | planted | rank | 541 | 0.017360 | 1.000000 | 2.414949 | 0.507692 | 44.378201 | 11401.093638 |
| 41 | null | equal | 541 | 0.000000 | 0.000000 | 0.837141 | 1.447792 | 0.639801 | 1.013905 |
| 41 | null | rank | 541 | 0.000000 | 0.000000 | 2.414949 | 0.507692 | 0.649924 | 1.049395 |
<!-- table:breadth:end -->

---

## Beta Drift Grid (P23)

48 cells across 4 beta windows x 3 drift thresholds x 2 variants x 2 weightings. Drift scale = 0.1 (±6% at δ=1e-3). Zero-drift reference matches P21 at 6 dp.

<!-- table:drift:start -->
| beta_window | drift_threshold | variant | weighting | active_rows_min | recovery_mean | recovery_min | recovery_positive_seed_fraction | gross_max | min_leg_beta |
|---|---|---|---|---|---|---|---|---|---|
| 60 | 0.000100 | planted | equal | 541 | 0.000255 | 0.000247 | 1.000000 | 0.000000 | 0.000000 |
| 60 | 0.000100 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 60 | 0.000100 | planted | rank | 541 | 0.017359 | 0.017347 | 1.000000 | 2.441366 | 0.507692 |
| 60 | 0.000100 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.441366 | 0.507692 |
| 60 | 0.000500 | planted | equal | 541 | 0.000261 | 0.000234 | 1.000000 | 0.000000 | 0.000000 |
| 60 | 0.000500 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 60 | 0.000500 | planted | rank | 541 | 0.017349 | 0.017290 | 1.000000 | 2.444202 | 0.507692 |
| 60 | 0.000500 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.444202 | 0.507692 |
| 60 | 0.001000 | planted | equal | 541 | 0.000261 | 0.000201 | 1.000000 | 0.000000 | 0.000000 |
| 60 | 0.001000 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 60 | 0.001000 | planted | rank | 541 | 0.017331 | 0.017216 | 1.000000 | 2.447716 | 0.507692 |
| 60 | 0.001000 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.447716 | 0.507692 |
| 90 | 0.000100 | planted | equal | 541 | 0.000262 | 0.000256 | 1.000000 | 0.000000 | 0.000000 |
| 90 | 0.000100 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 90 | 0.000100 | planted | rank | 541 | 0.017358 | 0.017347 | 1.000000 | 2.415569 | 0.507692 |
| 90 | 0.000100 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.415569 | 0.507692 |
| 90 | 0.000500 | planted | equal | 541 | 0.000262 | 0.000234 | 1.000000 | 0.000000 | 0.000000 |
| 90 | 0.000500 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 90 | 0.000500 | planted | rank | 541 | 0.017347 | 0.017293 | 1.000000 | 2.422654 | 0.507692 |
| 90 | 0.000500 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.422654 | 0.507692 |
| 90 | 0.001000 | planted | equal | 541 | 0.000263 | 0.000206 | 1.000000 | 0.000000 | 0.000000 |
| 90 | 0.001000 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 90 | 0.001000 | planted | rank | 541 | 0.017330 | 0.017219 | 1.000000 | 2.431671 | 0.507692 |
| 90 | 0.001000 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.431671 | 0.507692 |
| 120 | 0.000100 | planted | equal | 541 | 0.000262 | 0.000255 | 1.000000 | 0.000000 | 0.000000 |
| 120 | 0.000100 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 120 | 0.000100 | planted | rank | 541 | 0.017362 | 0.017351 | 1.000000 | 2.410854 | 0.510833 |
| 120 | 0.000100 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.410854 | 0.510833 |
| 120 | 0.000500 | planted | equal | 541 | 0.000263 | 0.000233 | 1.000000 | 0.000000 | 0.000000 |
| 120 | 0.000500 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 120 | 0.000500 | planted | rank | 541 | 0.017352 | 0.017301 | 1.000000 | 2.412671 | 0.507692 |
| 120 | 0.000500 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.412671 | 0.507692 |
| 120 | 0.001000 | planted | equal | 541 | 0.000266 | 0.000206 | 1.000000 | 0.000000 | 0.000000 |
| 120 | 0.001000 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 120 | 0.001000 | planted | rank | 541 | 0.017336 | 0.017230 | 1.000000 | 2.414938 | 0.507692 |
| 120 | 0.001000 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.414938 | 0.507692 |
| 180 | 0.000100 | planted | equal | 541 | 0.000263 | 0.000258 | 1.000000 | 0.000000 | 0.000000 |
| 180 | 0.000100 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 180 | 0.000100 | planted | rank | 541 | 0.017367 | 0.017358 | 1.000000 | 2.398736 | 0.510833 |
| 180 | 0.000100 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.398736 | 0.510833 |
| 180 | 0.000500 | planted | equal | 541 | 0.000263 | 0.000235 | 1.000000 | 0.000000 | 0.000000 |
| 180 | 0.000500 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 180 | 0.000500 | planted | rank | 541 | 0.017359 | 0.017312 | 1.000000 | 2.401045 | 0.510833 |
| 180 | 0.000500 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.401045 | 0.510833 |
| 180 | 0.001000 | planted | equal | 541 | 0.000269 | 0.000213 | 1.000000 | 0.000000 | 0.000000 |
| 180 | 0.001000 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 180 | 0.001000 | planted | rank | 541 | 0.017345 | 0.017249 | 1.000000 | 2.404112 | 0.510833 |
| 180 | 0.001000 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.404112 | 0.510833 |
<!-- table:drift:end -->

### Drift Zero Reference (matches P21 at 6 dp)

<!-- table:drift_zero_reference:start -->
| variant | weighting | committed_p21_recovery | drift_zero_recovery | matches_at_6dp |
|---|---|---|---|---|
| null | equal | 0.000000 | 0.000000 | True |
| null | rank | 0.000000 | 0.000000 | True |
| planted | equal | 0.000261 | 0.000261 | True |
| planted | rank | 0.017360 | 0.017360 | True |
<!-- table:drift_zero_reference:end -->

---

## Short Haircut Ladder (P23)

20 cells across 5 haircut levels x 2 variants x 2 weightings. 400 book runs. Censored cell at rank h=0.75 with `censor_reason = "no_active_rows_after_short_availability_restriction"`, active_rows_min=0, degenerate_rows_max=541. Zero-haircut reference matches P21 and WP2 at 6 dp. The degenerate draw is real and published: seed `20261245` (index 4 of 20) holds zero of 12 shorts at h=0.75 (0.75¹² ≈ 3.2% draw), so its entire short book is unavailable; its `per_seed_degenerate_rows` is 541 and its `per_seed_active_rows` is 0. Every other seed keeps a positive short book, and every non-censored planted seed has strictly positive recovery.

<!-- table:haircut:start -->
| haircut | variant | weighting | active_rows_min | availability_mean | short_survival_mean | recovery_mean | recovery_min | recovery_positive_seed_fraction | costed_sharpe_mean | costed_sharpe_non_increasing | censored | censor_reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.000000 | planted | equal | 541 | 1.000000 | 1.000000 | 0.000261 | 0.000261 | 1.000000 | 7.034781 | True | False | None |
| 0.000000 | null | equal | 541 | 1.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.639801 | True | False | None |
| 0.000000 | planted | rank | 541 | 1.000000 | 1.000000 | 0.017360 | 0.017360 | 1.000000 | 44.378201 | True | False | None |
| 0.000000 | null | rank | 541 | 1.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.649924 | True | False | None |
| 0.100000 | planted | equal | 541 | 0.904878 | 0.895833 | 0.000357 | 0.000179 | 1.000000 | -993.970148 | True | False | None |
| 0.100000 | null | equal | 541 | 0.904878 | 0.895833 | 0.000000 | 0.000000 | 0.000000 | -1011.674983 | True | False | None |
| 0.100000 | planted | rank | 541 | 0.904878 | 0.888462 | 0.017103 | 0.016528 | 1.000000 | -69.059967 | True | False | None |
| 0.100000 | null | rank | 541 | 0.904878 | 0.888462 | 0.000000 | 0.000000 | 0.000000 | -316.091723 | True | False | None |
| 0.250000 | planted | equal | 541 | 0.734146 | 0.718750 | 0.000517 | 0.000228 | 1.000000 | -2495.477541 | True | False | None |
| 0.250000 | null | equal | 541 | 0.734146 | 0.718750 | 0.000000 | 0.000000 | 0.000000 | -2530.147157 | True | False | None |
| 0.250000 | planted | rank | 541 | 0.734146 | 0.665385 | 0.016615 | 0.016052 | 1.000000 | -239.217220 | True | False | None |
| 0.250000 | null | rank | 541 | 0.734146 | 0.665385 | 0.000000 | 0.000000 | 0.000000 | -791.204195 | True | False | None |
| 0.500000 | planted | equal | 541 | 0.479268 | 0.452083 | 0.000836 | 0.000372 | 1.000000 | -4997.989862 | True | False | None |
| 0.500000 | null | equal | 541 | 0.479268 | 0.452083 | 0.000000 | 0.000000 | 0.000000 | -5060.934115 | True | False | None |
| 0.500000 | planted | rank | 541 | 0.479268 | 0.411538 | 0.016103 | 0.015449 | 1.000000 | -522.812641 | True | False | None |
| 0.500000 | null | rank | 541 | 0.479268 | 0.411538 | 0.000000 | 0.000000 | 0.000000 | -1583.058313 | True | False | None |
| 0.750000 | planted | equal | 541 | 0.228049 | 0.225000 | 0.001129 | 0.000955 | 1.000000 | -7500.502184 | True | False | None |
| 0.750000 | null | equal | 541 | 0.228049 | 0.225000 | 0.000000 | 0.000000 | 0.000000 | -7591.721073 | True | False | None |
| 0.750000 | planted | rank | 0 | 0.228049 | 0.207692 | 0.014816 | 0.000000 | 0.950000 | -806.408062 | True | True | no_active_rows_after_short_availability_restriction |
| 0.750000 | null | rank | 0 | 0.228049 | 0.207692 | 0.000000 | 0.000000 | 0.000000 | -2374.912432 | True | True | no_active_rows_after_short_availability_restriction |
<!-- table:haircut:end -->

### Haircut Zero Reference (matches P21 and WP2 at 6 dp)

<!-- table:haircut_zero_reference:start -->
| variant | weighting | committed_p21_recovery | committed_wp2_drift_zero_recovery | haircut_zero_recovery | matches_p21_at_6dp | matches_wp2_at_6dp |
|---|---|---|---|---|---|---|
| null | equal | 0.000000 | 0.000000 | 0.000000 | True | True |
| null | rank | 0.000000 | 0.000000 | 0.000000 | True | True |
| planted | equal | 0.000261 | 0.000261 | 0.000261 | True | True |
| planted | rank | 0.017360 | 0.017360 | 0.017360 | True | True |
<!-- table:haircut_zero_reference:end -->

---

## Null Battery (P22)

False positive rate at alpha ≤ 0.05; max absolute recovery ≤ 1e-10.

<!-- table:null_battery:start -->
| seed | variant | weighting | active_rows | recovery_mean | recovery_frac_positive | gross_max | gross_sharpe | p_value | significant |
|---|---|---|---|---|---|---|---|---|---|
| 20261120 | planted | equal | 541 | 0.000234 | 1.000000 | 0.841277 | 5.847385 | None | False |
| 20261120 | planted | rank | 541 | 0.017281 | 1.000000 | 2.403662 | 44.312973 | None | False |
| 20261120 | null | equal | 541 | 0.000000 | 0.000000 | 0.841277 | -0.311248 | 0.714500 | False |
| 20261120 | null | rank | 541 | 0.000000 | 0.000000 | 2.403662 | 0.192302 | 0.365000 | False |
| 20261121 | planted | equal | 541 | 0.000252 | 1.000000 | 0.826009 | 6.236204 | None | False |
| 20261121 | planted | rank | 541 | 0.017348 | 1.000000 | 2.397835 | 44.207555 | None | False |
| 20261121 | null | equal | 541 | 0.000000 | 0.000000 | 0.826009 | -0.304673 | 0.639000 | False |
| 20261121 | null | rank | 541 | 0.000000 | 0.000000 | 2.397835 | -0.023217 | 0.516500 | False |
| 20261122 | planted | equal | 541 | 0.000246 | 1.000000 | 0.826232 | 5.769030 | None | False |
| 20261122 | planted | rank | 541 | 0.017323 | 1.000000 | 2.414525 | 44.352461 | None | False |
| 20261122 | null | equal | 541 | 0.000000 | 0.000000 | 0.826232 | -0.538605 | 0.741000 | False |
| 20261122 | null | rank | 541 | 0.000000 | 0.000000 | 2.414525 | -0.008430 | 0.501000 | False |
| 20261123 | planted | equal | 541 | 0.000264 | 1.000000 | 0.840125 | 6.942790 | None | False |
| 20261123 | planted | rank | 541 | 0.017393 | 1.000000 | 2.426150 | 44.035125 | None | False |
| 20261123 | null | equal | 541 | 0.000000 | 0.000000 | 0.840125 | 0.055382 | 0.473500 | False |
| 20261123 | null | rank | 541 | 0.000000 | 0.000000 | 2.426150 | -0.942137 | 0.899000 | False |
| 20261124 | planted | equal | 541 | 0.000259 | 1.000000 | 0.826680 | 7.488539 | None | False |
| 20261124 | planted | rank | 541 | 0.017310 | 1.000000 | 2.434553 | 43.999594 | None | False |
| 20261124 | null | equal | 541 | 0.000000 | 0.000000 | 0.826680 | 0.713294 | 0.150000 | False |
| 20261124 | null | rank | 541 | 0.000000 | 0.000000 | 2.434553 | -0.097618 | 0.595000 | False |
| 20261125 | planted | equal | 541 | 0.000232 | 1.000000 | 0.820002 | 5.966391 | None | False |
| 20261125 | planted | rank | 541 | 0.017234 | 1.000000 | 2.389016 | 44.050481 | None | False |
| 20261125 | null | equal | 541 | 0.000000 | 0.000000 | 0.820002 | 0.108230 | 0.503500 | False |
| 20261125 | null | rank | 541 | 0.000000 | 0.000000 | 2.389016 | 0.261310 | 0.347500 | False |
| 20261126 | planted | equal | 541 | 0.000256 | 1.000000 | 0.837900 | 6.875194 | None | False |
| 20261126 | planted | rank | 541 | 0.017373 | 1.000000 | 2.433786 | 43.984911 | None | False |
| 20261126 | null | equal | 541 | 0.000000 | 0.000000 | 0.837900 | -0.169524 | 0.606000 | False |
| 20261126 | null | rank | 541 | 0.000000 | 0.000000 | 2.433786 | -1.155615 | 0.903500 | False |
| 20261127 | planted | equal | 541 | 0.000248 | 1.000000 | 0.852805 | 6.954164 | None | False |
| 20261127 | planted | rank | 541 | 0.017278 | 1.000000 | 2.403753 | 44.649212 | None | False |
| 20261127 | null | equal | 541 | 0.000000 | 0.000000 | 0.852805 | 0.564512 | 0.156000 | False |
| 20261127 | null | rank | 541 | 0.000000 | 0.000000 | 2.403753 | 1.192924 | 0.009000 | True |
| 20261128 | planted | equal | 541 | 0.000253 | 1.000000 | 0.832930 | 6.924856 | None | False |
| 20261128 | planted | rank | 541 | 0.017413 | 1.000000 | 2.427171 | 44.281850 | None | False |
| 20261128 | null | equal | 541 | 0.000000 | 0.000000 | 0.832930 | 0.294281 | 0.333000 | False |
| 20261128 | null | rank | 541 | 0.000000 | 0.000000 | 2.427171 | 0.321756 | 0.308500 | False |
| 20261129 | planted | equal | 541 | 0.000257 | 1.000000 | 0.837322 | 6.808841 | None | False |
| 20261129 | planted | rank | 541 | 0.017380 | 1.000000 | 2.403749 | 44.474850 | None | False |
| 20261129 | null | equal | 541 | 0.000000 | 0.000000 | 0.837322 | 0.297174 | 0.261500 | False |
| 20261129 | null | rank | 541 | 0.000000 | 0.000000 | 2.403749 | -0.360951 | 0.676500 | False |
| 20261130 | planted | equal | 541 | 0.000237 | 0.970425 | 0.838984 | 5.842153 | None | False |
| 20261130 | planted | rank | 541 | 0.017330 | 1.000000 | 2.418523 | 44.332305 | None | False |
| 20261130 | null | equal | 541 | 0.000000 | 0.000000 | 0.838984 | -0.369068 | 0.609500 | False |
| 20261130 | null | rank | 541 | 0.000000 | 0.000000 | 2.418523 | 0.653305 | 0.100500 | False |
| 20261131 | planted | equal | 541 | 0.000249 | 1.000000 | 0.834057 | 6.465222 | None | False |
| 20261131 | planted | rank | 541 | 0.017297 | 1.000000 | 2.404381 | 44.368443 | None | False |
| 20261131 | null | equal | 541 | 0.000000 | 0.000000 | 0.834057 | 0.179330 | 0.410500 | False |
| 20261131 | null | rank | 541 | 0.000000 | 0.000000 | 2.404381 | 0.628225 | 0.136500 | False |
| 20261132 | planted | equal | 541 | 0.000234 | 1.000000 | 0.824699 | 6.219985 | None | False |
| 20261132 | planted | rank | 541 | 0.017298 | 1.000000 | 2.408694 | 44.225266 | None | False |
| 20261132 | null | equal | 541 | 0.000000 | 0.000000 | 0.824699 | 0.381937 | 0.339500 | False |
| 20261132 | null | rank | 541 | 0.000000 | 0.000000 | 2.408694 | -0.148436 | 0.524000 | False |
| 20261133 | planted | equal | 541 | 0.000231 | 0.972274 | 0.830700 | 7.237063 | None | False |
| 20261133 | planted | rank | 541 | 0.017234 | 1.000000 | 2.412368 | 44.400419 | None | False |
| 20261133 | null | equal | 541 | 0.000000 | 0.000000 | 0.830700 | 1.288970 | 0.024500 | True |
| 20261133 | null | rank | 541 | 0.000000 | 0.000000 | 2.412368 | -0.473363 | 0.726000 | False |
| 20261134 | planted | equal | 541 | 0.000254 | 1.000000 | 0.835266 | 6.447972 | None | False |
| 20261134 | planted | rank | 541 | 0.017328 | 1.000000 | 2.416256 | 44.069394 | None | False |
| 20261134 | null | equal | 541 | 0.000000 | 0.000000 | 0.835266 | 0.062595 | 0.423500 | False |
| 20261134 | null | rank | 541 | 0.000000 | 0.000000 | 2.416256 | 0.271827 | 0.368500 | False |
| 20261135 | planted | equal | 541 | 0.000206 | 0.924214 | 0.829920 | 5.672354 | None | False |
| 20261135 | planted | rank | 541 | 0.017227 | 1.000000 | 2.379311 | 44.331047 | None | False |
| 20261135 | null | equal | 541 | 0.000000 | 0.000000 | 0.829920 | 0.519202 | 0.223000 | False |
| 20261135 | null | rank | 541 | 0.000000 | 0.000000 | 2.379311 | 0.491636 | 0.226000 | False |
| 20261136 | planted | equal | 541 | 0.000251 | 1.000000 | 0.835938 | 6.033065 | None | False |
| 20261136 | planted | rank | 541 | 0.017238 | 1.000000 | 2.404111 | 44.744873 | None | False |
| 20261136 | null | equal | 541 | 0.000000 | 0.000000 | 0.835938 | -0.551676 | 0.812000 | False |
| 20261136 | null | rank | 541 | 0.000000 | 0.000000 | 2.404111 | -2.047595 | 0.999000 | False |
| 20261137 | planted | equal | 541 | 0.000247 | 1.000000 | 0.831335 | 7.120104 | None | False |
| 20261137 | planted | rank | 541 | 0.017273 | 1.000000 | 2.431443 | 44.540424 | None | False |
| 20261137 | null | equal | 541 | 0.000000 | 0.000000 | 0.831335 | 0.989214 | 0.050500 | False |
| 20261137 | null | rank | 541 | 0.000000 | 0.000000 | 2.431443 | -0.807706 | 0.906500 | False |
| 20261138 | planted | equal | 541 | 0.000221 | 0.968577 | 0.828055 | 5.552134 | None | False |
| 20261138 | planted | rank | 541 | 0.017241 | 1.000000 | 2.402421 | 44.551385 | None | False |
| 20261138 | null | equal | 541 | 0.000000 | 0.000000 | 0.828055 | -0.202465 | 0.548500 | False |
| 20261138 | null | rank | 541 | 0.000000 | 0.000000 | 2.402421 | -0.664954 | 0.847000 | False |
| 20261139 | planted | equal | 541 | 0.000245 | 1.000000 | 0.820614 | 5.557763 | None | False |
| 20261139 | planted | rank | 541 | 0.017307 | 1.000000 | 2.396454 | 43.992235 | None | False |
| 20261139 | null | equal | 541 | 0.000000 | 0.000000 | 0.820614 | -1.125581 | 0.934500 | False |
| 20261139 | null | rank | 541 | 0.000000 | 0.000000 | 2.396454 | -0.060205 | 0.484500 | False |
<!-- table:null_battery:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| Explicit signal-or-noise verdict | True |
| NO-GO for market | True |
| No harness re-run | True |
| Planted recovery labelled controlled synthetic | True |
| Numbers matched minimum | 100 |
| Unmatched cells maximum | 0 |
| Regime grid minimum | 2 |
| Hysteresis band grid minimum | 3 |
| Turnover monotone non-increasing | True |
| Adapter valid offline | True |
| Nominal slack | 0.050000 |
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** The planted universe is a controlled synthetic stimulus with a convex alpha curve (`alpha = A(0.5 - u²)`), idiosyncratic vol 0.003-0.005, and a known ground truth. It is **not real market data** and **not market profitability evidence**.
- **No out-of-sample validation.** All results are in-sample on the planted panel (seed 20261118). The holdout discipline (P24 charter: `holdout_before_tuning = true`) prevents parameter selection on the evaluation window.
- **No walk-forward / OOS harness.** Campaign P24 closes without a walk-forward/out-of-sample harness. The default book is dollar-neutral only and carries a large negative benchmark beta (measured -0.57 at default config, -0.91 at q=0.2 on the committed fixture).
- **No Frazzini-Pedersen rank weighting with beta scaling.** The rank path is documented in `docs/BAB_FIDELITY.md` §9 but is **not empirically evaluable** on the committed 9-asset synthetic fixture. The shipped default remains equal-weight.
- **No live execution evidence.** The licensed-data adapter (P24 WP3) validated only an offline CSV fixture. The live adapter (`--adapter live`) is dry-run by default and requires explicit two-key opt-in (`--allow-live-execution` and `--accept-terms I_UNDERSTAND_LIVE_TRADING`). No network was used in this campaign.

---

## Next Steps

Campaign P24 concludes here. The NO-GO verdict is restated from P23/P24 charters and validated against every committed JSON artifact. All planted recovery is labelled **controlled synthetic** — never market alpha. The regime-conditional BAB hypothesis is **not supported** by the evidence: stress regime planted recovery is negative, and the calibrated hysteresis ladder only reduces turnover without recovering positive expectancy in stress.

**Future work** (not in scope for P24):
- Walk-forward / out-of-sample harness
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API returns 403)
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh` (P19-1, maintainer-only — agent tokens lack `workflows:write`)
- Frazzini-Pedersen rank-weighted / beta-scaled construction on a wider universe

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON leaf at 6 dp. The acceptance test `tests/test_bab_p24_decision_consistency.py` verifies zero unmatched cells, ≥100 machine-checked cells, byte-identical table rendering, AST no-harness scan, and explicit verdict strings.*
