import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import strategies.betting_against_beta.data_loader as dl


def test_probe_1853_load_returns_dataframe_prices_path():
    # load_returns 1853: DataFrame source detected as prices -> load_prices(df).
    df = pd.DataFrame(
        {"BTC": [100.0, 101.0, 102.0, 103.0], "ETH": [2000.0, 2010.0, 2020.0, 2030.0]},
        index=pd.date_range("2024-01-01", periods=4, freq="D"),
    )
    out = dl.load_returns(df)
    assert out.shape == (3, 2)


def test_probe_1868_load_returns_path_prices_path():
    # load_returns 1868: file path detected as prices -> load_prices(path).
    df = pd.DataFrame(
        {"BTC": [100.0, 101.0, 102.0], "ETH": [2000.0, 2010.0, 2020.0]},
        index=pd.date_range("2024-01-01", periods=3, freq="D"),
    )
    d = tempfile.mkdtemp()
    p = os.path.join(d, "prices.csv")
    df.to_csv(p)
    out = dl.load_returns(p)
    assert out.shape == (2, 2)
