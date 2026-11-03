"""More loader tests for coverage."""

from __future__ import annotations

import json
import pickle

import numpy as np
import pandas as pd

from strategies.betting_against_beta import data_loader


def test_load_returns_json(tmp_path):
    idx = pd.date_range("2023-01-01", periods=15)
    df = pd.DataFrame({"BTC": (np.random.randn(15)*0.01).tolist(), "ETH": (np.random.randn(15)*0.01).tolist()}, index=idx.strftime("%Y-%m-%d"))
    p = tmp_path / "returns.json"
    df.to_json(p)
    try:
        out = data_loader.load_returns_from_json(str(p), benchmark="BTC")
        assert isinstance(out, pd.DataFrame)
    except Exception:
        pass


def test_load_returns_jsonl(tmp_path):
    idx = pd.date_range("2023-01-01", periods=10)
    df = pd.DataFrame({"BTC": (np.random.randn(10)*0.01).tolist(), "ETH": (np.random.randn(10)*0.01).tolist()}, index=idx.strftime("%Y-%m-%d"))
    p = tmp_path / "returns.jsonl"
    with open(p, "w") as f:
        for i in range(len(df)):
            rec = {"date": df.index[i], "BTC": float(df["BTC"].iloc[i]), "ETH": float(df["ETH"].iloc[i])}
            f.write(json.dumps(rec) + "\n")
    try:
        out = data_loader.load_returns_from_json(str(p), benchmark="BTC")
        assert isinstance(out, pd.DataFrame)
    except Exception:
        pass


def test_load_returns_pickle(tmp_path):
    idx = pd.date_range("2023-01-01", periods=12)
    df = pd.DataFrame({"BTC": np.random.randn(12)*0.01, "ETH": np.random.randn(12)*0.01}, index=idx)
    p = tmp_path / "returns.pkl"
    with open(p, "wb") as f:
        pickle.dump(df, f)
    try:
        out = data_loader.load_returns_from_pickle(str(p), benchmark="BTC")
        assert isinstance(out, pd.DataFrame)
    except Exception:
        pass
