# BAB P21 WP0 — wide synthetic universe with planted ground truth

Schema `bab_p21.universe/1`. 41 tradable assets plus benchmark `BTC`, 600 return rows, seed 20261118.
**Controlled synthetic stimulus with known ground truth: not real market data and not market profitability evidence.**

Betas in [0.3, 2.7]; idiosyncratic vol in [0.003, 0.005]; planted annual alpha spread 4.0 with exponent 2.0.
The two variants share betas, idiosyncratic vols, benchmark draws and residual draws; only the alpha vector differs.

| variant | alpha_min | alpha_max | panel_sha256 |
|---|---|---|---|
| planted | -0.007937 | 0.007937 | aae2a70ebcf81b3a9e2dd5f314933c439194fef8a7be1da34930e2c271a93fda |
| null | 0.0 | 0.0 | b7732c152564c87606a6a47eac39a543344cbcd4b8e974f4780be35671953b1b |
