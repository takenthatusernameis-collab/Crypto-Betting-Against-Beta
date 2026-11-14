import pandas as pd

from strategies.betting_against_beta.data_loader import _normalize_asset_name, load_returns


def test_normalize_asset_name_all_unit_tokens_restores_original_953():
    assert _normalize_asset_name("USD") == "USD"
    assert _normalize_asset_name("USDT") == "USDT"
    assert _normalize_asset_name("price") == "PRICE"
    assert _normalize_asset_name("dollar token") == "DOLLAR TOKEN"


def test_normalize_columns_all_unit_column_hits_953(tmp_path):
    df = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "USD": [0.1, 0.2], "BTC": [0.3, 0.4]})
    p = tmp_path / "r.csv"
    df.to_csv(p, index=False)
    out = load_returns(str(p), benchmark="BTC")
    assert "BTC" in out.columns
