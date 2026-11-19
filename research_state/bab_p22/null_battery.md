# BAB P22 WP1 — null battery over the chartered seeds

Schema `bab_p22.null_battery/1`. Controlled synthetic stimulus with known ground truth: not real market data and not market profitability evidence.

20 chartered seeds; reference seed 20261118 reproduces the committed P21 panels: True; bootstrap 2000 resamples, block length 20.

## Battery summary (from per-seed records only)

- Null books: 40; planted books: 40
- Null recovery max abs: 0.000000
- Null recovery exactly zero every seed: True (40/40 books)
- False-positive count: 2/40 (rate 0.050000, expected 2.000000, declared bound 4, within bound True)
- Planted recovery positive fraction (equal): 1.000000, (rank): 1.000000
- Planted recovery min (equal): 0.000206, (rank): 0.017227
- Planted recovery exceeds null max: True

## Per-seed books

| seed | variant | weighting | active_rows | gross_mean_active | recovery_mean | oos_sharpe | p_value | significant |
|---|---|---|---|---|---|---|---|---|
| 20261120 | planted | equal | 541 | 0.802491 | 0.000234 | 5.847385 | n/a | False |
| 20261120 | planted | rank | 541 | 2.358113 | 0.017281 | 44.312973 | n/a | False |
| 20261120 | null | equal | 541 | 0.802491 | 0.000000 | -0.311248 | 0.714500 | False |
| 20261120 | null | rank | 541 | 2.358113 | 0.000000 | 0.192302 | 0.365000 | False |
| 20261121 | planted | equal | 541 | 0.811040 | 0.000252 | 6.236204 | n/a | False |
| 20261121 | planted | rank | 541 | 2.366698 | 0.017348 | 44.207555 | n/a | False |
| 20261121 | null | equal | 541 | 0.811040 | 0.000000 | -0.304673 | 0.639000 | False |
| 20261121 | null | rank | 541 | 2.366698 | 0.000000 | -0.023217 | 0.516500 | False |
| 20261122 | planted | equal | 541 | 0.805848 | 0.000246 | 5.769030 | n/a | False |
| 20261122 | planted | rank | 541 | 2.363705 | 0.017323 | 44.352461 | n/a | False |
| 20261122 | null | equal | 541 | 0.805848 | 0.000000 | -0.538605 | 0.741000 | False |
| 20261122 | null | rank | 541 | 2.363705 | 0.000000 | -0.008430 | 0.501000 | False |
| 20261123 | planted | equal | 541 | 0.816301 | 0.000264 | 6.942790 | n/a | False |
| 20261123 | planted | rank | 541 | 2.372698 | 0.017393 | 44.035125 | n/a | False |
| 20261123 | null | equal | 541 | 0.816301 | 0.000000 | 0.055382 | 0.473500 | False |
| 20261123 | null | rank | 541 | 2.372698 | 0.000000 | -0.942137 | 0.899000 | False |
| 20261124 | planted | equal | 541 | 0.806973 | 0.000259 | 7.488539 | n/a | False |
| 20261124 | planted | rank | 541 | 2.362197 | 0.017310 | 43.999594 | n/a | False |
| 20261124 | null | equal | 541 | 0.806973 | 0.000000 | 0.713294 | 0.150000 | False |
| 20261124 | null | rank | 541 | 2.362197 | 0.000000 | -0.097618 | 0.595000 | False |
| 20261125 | planted | equal | 541 | 0.801447 | 0.000232 | 5.966391 | n/a | False |
| 20261125 | planted | rank | 541 | 2.352340 | 0.017234 | 44.050481 | n/a | False |
| 20261125 | null | equal | 541 | 0.801447 | 0.000000 | 0.108230 | 0.503500 | False |
| 20261125 | null | rank | 541 | 2.352340 | 0.000000 | 0.261310 | 0.347500 | False |
| 20261126 | planted | equal | 541 | 0.812656 | 0.000256 | 6.875194 | n/a | False |
| 20261126 | planted | rank | 541 | 2.370386 | 0.017373 | 43.984911 | n/a | False |
| 20261126 | null | equal | 541 | 0.812656 | 0.000000 | -0.169524 | 0.606000 | False |
| 20261126 | null | rank | 541 | 2.370386 | 0.000000 | -1.155615 | 0.903500 | False |
| 20261127 | planted | equal | 541 | 0.815630 | 0.000248 | 6.954164 | n/a | False |
| 20261127 | planted | rank | 541 | 2.357703 | 0.017278 | 44.649212 | n/a | False |
| 20261127 | null | equal | 541 | 0.815630 | 0.000000 | 0.564512 | 0.156000 | False |
| 20261127 | null | rank | 541 | 2.357703 | 0.000000 | 1.192924 | 0.009000 | True |
| 20261128 | planted | equal | 541 | 0.811164 | 0.000253 | 6.924856 | n/a | False |
| 20261128 | planted | rank | 541 | 2.375463 | 0.017413 | 44.281850 | n/a | False |
| 20261128 | null | equal | 541 | 0.811164 | 0.000000 | 0.294281 | 0.333000 | False |
| 20261128 | null | rank | 541 | 2.375463 | 0.000000 | 0.321756 | 0.308500 | False |
| 20261129 | planted | equal | 541 | 0.808274 | 0.000257 | 6.808841 | n/a | False |
| 20261129 | planted | rank | 541 | 2.371407 | 0.017380 | 44.474850 | n/a | False |
| 20261129 | null | equal | 541 | 0.808274 | 0.000000 | 0.297174 | 0.261500 | False |
| 20261129 | null | rank | 541 | 2.371407 | 0.000000 | -0.360951 | 0.676500 | False |
| 20261130 | planted | equal | 541 | 0.816773 | 0.000237 | 5.842153 | n/a | False |
| 20261130 | planted | rank | 541 | 2.365118 | 0.017330 | 44.332305 | n/a | False |
| 20261130 | null | equal | 541 | 0.816773 | 0.000000 | -0.369068 | 0.609500 | False |
| 20261130 | null | rank | 541 | 2.365118 | 0.000000 | 0.653305 | 0.100500 | False |
| 20261131 | planted | equal | 541 | 0.812943 | 0.000249 | 6.465222 | n/a | False |
| 20261131 | planted | rank | 541 | 2.360571 | 0.017297 | 44.368443 | n/a | False |
| 20261131 | null | equal | 541 | 0.812943 | 0.000000 | 0.179330 | 0.410500 | False |
| 20261131 | null | rank | 541 | 2.360571 | 0.000000 | 0.628225 | 0.136500 | False |
| 20261132 | planted | equal | 541 | 0.804300 | 0.000234 | 6.219985 | n/a | False |
| 20261132 | planted | rank | 541 | 2.360518 | 0.017298 | 44.225266 | n/a | False |
| 20261132 | null | equal | 541 | 0.804300 | 0.000000 | 0.381937 | 0.339500 | False |
| 20261132 | null | rank | 541 | 2.360518 | 0.000000 | -0.148436 | 0.524000 | False |
| 20261133 | planted | equal | 541 | 0.810007 | 0.000231 | 7.237063 | n/a | False |
| 20261133 | planted | rank | 541 | 2.352801 | 0.017234 | 44.400419 | n/a | False |
| 20261133 | null | equal | 541 | 0.810007 | 0.000000 | 1.288970 | 0.024500 | True |
| 20261133 | null | rank | 541 | 2.352801 | 0.000000 | -0.473363 | 0.726000 | False |
| 20261134 | planted | equal | 541 | 0.814419 | 0.000254 | 6.447972 | n/a | False |
| 20261134 | planted | rank | 541 | 2.364829 | 0.017328 | 44.069394 | n/a | False |
| 20261134 | null | equal | 541 | 0.814419 | 0.000000 | 0.062595 | 0.423500 | False |
| 20261134 | null | rank | 541 | 2.364829 | 0.000000 | 0.271827 | 0.368500 | False |
| 20261135 | planted | equal | 541 | 0.810460 | 0.000206 | 5.672354 | n/a | False |
| 20261135 | planted | rank | 541 | 2.352544 | 0.017227 | 44.331047 | n/a | False |
| 20261135 | null | equal | 541 | 0.810460 | 0.000000 | 0.519202 | 0.223000 | False |
| 20261135 | null | rank | 541 | 2.352544 | 0.000000 | 0.491636 | 0.226000 | False |
| 20261136 | planted | equal | 541 | 0.812579 | 0.000251 | 6.033065 | n/a | False |
| 20261136 | planted | rank | 541 | 2.352764 | 0.017238 | 44.744873 | n/a | False |
| 20261136 | null | equal | 541 | 0.812579 | 0.000000 | -0.551676 | 0.812000 | False |
| 20261136 | null | rank | 541 | 2.352764 | 0.000000 | -2.047595 | 0.999000 | False |
| 20261137 | planted | equal | 541 | 0.811278 | 0.000247 | 7.120104 | n/a | False |
| 20261137 | planted | rank | 541 | 2.357534 | 0.017273 | 44.540424 | n/a | False |
| 20261137 | null | equal | 541 | 0.811278 | 0.000000 | 0.989214 | 0.050500 | False |
| 20261137 | null | rank | 541 | 2.357534 | 0.000000 | -0.807706 | 0.906500 | False |
| 20261138 | planted | equal | 541 | 0.806239 | 0.000221 | 5.552134 | n/a | False |
| 20261138 | planted | rank | 541 | 2.353346 | 0.017241 | 44.551385 | n/a | False |
| 20261138 | null | equal | 541 | 0.806239 | 0.000000 | -0.202465 | 0.548500 | False |
| 20261138 | null | rank | 541 | 2.353346 | 0.000000 | -0.664954 | 0.847000 | False |
| 20261139 | planted | equal | 541 | 0.806852 | 0.000245 | 5.557763 | n/a | False |
| 20261139 | planted | rank | 541 | 2.362015 | 0.017307 | 43.992235 | n/a | False |
| 20261139 | null | equal | 541 | 0.806852 | 0.000000 | -1.125581 | 0.934500 | False |
| 20261139 | null | rank | 541 | 2.362015 | 0.000000 | -0.060205 | 0.484500 | False |

Method: rebuilds the P21 planted/null universe per chartered seed, runs the shipped BABStrategy for equal and rank weighting, reports null recovery (must be exactly zero) and a bootstrap false-positive rate, and proves the reference seed reproduces the committed P21 panel sha256 values; never imports or calls a P21 build_* harness.

Caveat: A null-universe positive result is a bug, not a finding. Planted recovery on this controlled synthetic universe proves the estimator works; it is never market alpha. NO-GO for market deployment until a maintainer supplies a licensed price series.
