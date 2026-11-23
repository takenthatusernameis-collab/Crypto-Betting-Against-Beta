# BAB P21 WP1 — rank vs equal evaluation on the planted universe

Schema `bab_p21.rank_eval/1`. Controlled synthetic stimulus with known ground truth: not real market data and not market profitability evidence.

Universe seed 20261118; variants null, planted; config: {"benchmark": "BTC", "beta_neutral": true, "beta_window": 90, "long_quantile": 0.3, "min_observations": 60, "rank_max_gross": 4.0, "rank_min_leg_beta": 0.2, "short_quantile": 0.3, "transaction_costs": 0.0, "universe": ["A001", "A002", "A003", "A004", "A005", "A006", "A007", "A008", "A009", "A010", "A011", "A012", "A013", "A014", "A015", "A016", "A017", "A018", "A019", "A020", "A021", "A022", "A023", "A024", "A025", "A026", "A027", "A028", "A029", "A030", "A031", "A032", "A033", "A034", "A035", "A036", "A037", "A038", "A039", "A040", "A041"]}

| variant | weighting | active_rows | gross_mean_active | gross_max | long_leg_beta_mean | short_leg_beta_mean | min_leg_beta | dollar_imbalance_max | beta_exposure_max | recovery_mean | recovery_frac_positive | panel_sha256 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planted | equal | 541 | 0.814150529863 | 0.8371411639771037 | 1.4697738518657317 | 1.530489099931 | 1.447791783745 | 2.3349377986647823e-15 | 0.009139976606021213 | 0.000261 | 0.996303 | aae2a70ebcf81b3a9e2dd5f314933c439194fef8a7be1da34930e2c271a93fda |
| planted | rank | 541 | 2.368528140528 | 2.414948797881462 | 0.5108317337314564 | 2.488670671596 | 0.507692307692 | 1.6128444466324412 | 0.030479817377582152 | 0.01736 | 1.0 | aae2a70ebcf81b3a9e2dd5f314933c439194fef8a7be1da34930e2c271a93fda |
| null | equal | 541 | 0.814150529863 | 0.8371411639771077 | 1.4697738518657317 | 1.530489099931 | 1.447791783745 | 2.3436114160446664e-15 | 0.009139976606021588 | 0.0 | 0.0 | b7732c152564c87606a6a47eac39a543344cbcd4b8e974f4780be35671953b1b |
| null | rank | 541 | 2.368528140528 | 2.4149487978814625 | 0.5108317337314564 | 2.488670671596 | 0.507692307692 | 1.6128444466324414 | 0.03047981737758232 | 0.0 | 0.0 | b7732c152564c87606a6a47eac39a543344cbcd4b8e974f4780be35671953b1b |
