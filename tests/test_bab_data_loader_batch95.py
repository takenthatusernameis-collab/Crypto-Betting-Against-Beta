"""Batch 95: `_drop_metadata_columns` sequential-int inner check (1926-1927).

The strict-tolerance branch at 1915-1918 uses
``np.allclose(diffs, 1.0, rtol=0, atol=1e-9)`` while the inner check at
1924-1926 uses the default ``np.allclose(np.diff(vals[finite]), 1.0)``
(atol=1e-8). A value like ``3.000000005`` makes the strict predicate False
(1917) but the default-tolerance predicate True (1926), so the previously
"subsumed" inner branch at 1926-1927 is reachable.
"""

import numpy as np
import pandas as pd

from strategies.betting_against_beta.data_loader import _drop_metadata_columns


def test_1926_1927_sequential_int_inner_check_default_tolerance():
    # Strict (1917, atol=1e-9) fails; default (1926, atol=1e-8) succeeds.
    # Use a column name NOT in the junk-name set ({'extracol','unwanted','junk',
    # 'extra','garbage'}) so the drop must come from the sequential-int check.
    vals = [0.0, 1.0, 2.0, 3.000000005]
    df = pd.DataFrame({"seq": vals, "BTC": [100.0, 101.0, 102.0, 103.0]})
    result = _drop_metadata_columns(df.copy())
    assert "seq" not in result.columns
    assert "BTC" in result.columns


def test_1926_1927_via_load_prices_path():
    """End-to-end through load_prices to exercise the same code path."""
    import tempfile, os
    from strategies.betting_against_beta.data_loader import load_prices

    vals = [0.0, 1.0, 2.0, 3.000000005]
    df = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
            "seq": vals,
            "BTC": [100.0, 101.0, 102.0, 103.0],
            "ETH": [50.0, 51.0, 52.0, 53.0],
        }
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False
    ) as f:
        df.to_csv(f.name, index=False)
        path = f.name
    try:
        result = load_prices(path, benchmark="BTC")
        assert "seq" not in result.columns
        assert "BTC" in result.columns
    finally:
        os.unlink(path)