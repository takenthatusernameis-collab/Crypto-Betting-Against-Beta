import numpy as np
import pandas as pd

from strategies.betting_against_beta.data_loader import load_prices


def test_load_prices_metadata_drop_inner_exception_1928_1929():
    dates = pd.date_range("2024-01-01", periods=5)
    df = pd.DataFrame(
        {
            "date": dates,
            "BTC": [100.0, 101.0, 102.0, 103.0, 104.0],
            "ETH": [50.0, 51.0, 52.0, 53.0, 54.0],
            "meta": [0.0, 2.0, 4.0, 6.0, 8.0],
        }
    )

    import strategies.betting_against_beta.data_loader as dl

    orig = np.allclose

    def boom(*a, **k):
        if "rtol" in k or "atol" in k:
            return orig(*a, **k)
        if len(a) >= 2:
            try:
                a0 = np.asarray(a[0], dtype=float)
                if a0.shape == (4,) and list(a0) == [2.0, 2.0, 2.0, 2.0]:
                    raise RuntimeError("forced")
            except RuntimeError:
                raise
            except Exception:
                pass
        return orig(*a, **k)

    dl.np.allclose = boom
    try:
        result = load_prices(df, benchmark="BTC")
    finally:
        dl.np.allclose = orig

    assert "BTC" in result.columns
    assert "ETH" in result.columns
