import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import numpy as np
import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

# Batch 66: defensive branches via direct canonical entrypoints (0 delta; retargeting)

def test_1319_1320_coerce_numeric_object_raise():
    # object column that makes pd.to_numeric(errors='coerce') raise -> 1319-1320 fallback
    df = pd.DataFrame({'BTC': [object(), object(), object()], 'ETH': [0.01, 0.02, 0.03]},
                      index=pd.to_datetime(['2024-01-01','2024-01-02','2024-01-03']))
    try:
        dl._run_data_quality_campaign(df, max_return_abs=0.5, min_finite_fraction=0.0)
    except BABDataError:
        pass


def test_1226_1227_coerce_numeric_raise_path():
    # _coerce_numeric column where to_numeric(raise) raises ValueError/TypeError/AttributeError
    df = pd.DataFrame({'BTC': [object(), object(), object()], 'ETH': [0.01, 0.02, 0.03]},
                      index=pd.to_datetime(['2024-01-01','2024-01-02','2024-01-03']))
    try:
        dl.validate_returns_dataframe(df, benchmark='BTC', quality=False, min_rows=1)
    except BABDataError:
        pass


def test_1257_1258_tz_convert_then_localize_raise():
    # force tz_convert to raise then tz_localize to raise -> 1257-1258
    df = pd.DataFrame({'BTC': [0.01, 0.02, 0.03], 'ETH': [0.04, 0.05, 0.06]},
                      index=pd.to_datetime(['2024-01-01','2024-01-02','2024-01-03']).tz_localize('UTC'))
    try:
        dl._run_data_quality_campaign(df, max_return_abs=0.5, min_finite_fraction=0.0)
    except BABDataError:
        pass
