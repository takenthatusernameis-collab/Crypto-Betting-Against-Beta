import pandas as pd
import pytest

from strategies.betting_against_beta import data_loader as dl


def _base_df():
    return pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        'btc': [0.01, 0.02, 0.03, 0.01, 0.02],
        'ETH': [0.04, 0.05, 0.06, 0.04, 0.05],
    })


def test_validate_benchmark_first_rename_exception_1530_1531(monkeypatch):
    orig = pd.DataFrame.rename
    calls = {'n': 0}

    def bad(self, *a, **k):
        cols = k.get('columns') or {}
        if isinstance(cols, dict) and cols == {'BTC': 'btc'}:
            calls['n'] += 1
            if calls['n'] == 1:
                raise RuntimeError('boom1530')
        return orig(self, *a, **k)

    monkeypatch.setattr(pd.DataFrame, 'rename', bad)
    out = dl.validate_returns_dataframe(_base_df(), benchmark='btc', min_rows=1)
    assert 'btc' in [str(c).lower() for c in out.columns]
    assert len(out) == 5


def test_validate_benchmark_second_remap_1533_1536(monkeypatch):
    orig = pd.DataFrame.rename
    calls = {'n': 0}

    def bad(self, *a, **k):
        cols = k.get('columns') or {}
        if isinstance(cols, dict) and cols == {'BTC': 'btc'}:
            calls['n'] += 1
            raise RuntimeError('boom1530')
        return orig(self, *a, **k)

    monkeypatch.setattr(pd.DataFrame, 'rename', bad)
    with pytest.raises((RuntimeError, dl.BABDataError, KeyError)):
        dl.validate_returns_dataframe(_base_df(), benchmark='btc', min_rows=1)


def test_normalize_schema_metadata_drop_outer_except_2192_2193(monkeypatch):
    orig = pd.DataFrame.drop

    def bad(self, *a, **k):
        cols = k.get('columns')
        if cols is None and a:
            cols = a[0]
        if isinstance(cols, (list, tuple, set)) and 'junk' in [str(c).lower() for c in list(cols)]:
            raise RuntimeError('boom2192')
        return orig(self, *a, **k)

    monkeypatch.setattr(pd.DataFrame, 'drop', bad)
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'BTC': [0.01, 0.02],
        'ETH': [0.03, 0.04],
        'junk': ['', ''],
    })
    out = dl.normalize_schema(df)
    assert 'BTC' in out.columns and 'ETH' in out.columns
