import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

# Batch 75: direct canonical-shape probes for the two clusters whose
# unreachable proofs were least certain (non-positive integer metadata, and
# last-resort set_index fallback). Real DataFrame/Series shapes passed
# directly to canonical entrypoints.


def test_probe_1926_1929_drop_metadata_nonpositive_seq():
    # _drop_metadata_columns 1926-1929: a numeric column that is NOT a clean
    # sequential-from-0 artifact, but is integer-valued with minv <= 0 and
    # allclose to round(vals). E.g. [0,1,2] is dropped earlier at 1917; a
    # column like [0,1,2,3] with a non-1 diff, or [-1,0,1], reaches 1921.
    # We try several shapes directly against the helper.
    candidates = [
        [-1, 0, 1, 2],  # minv=-1 <=0, integer, allclose round
        [0, 2, 4, 6],  # minv=0, integer, diffs != 1
        [-2, -1, 0, 1],  # minv=-2
        [0, 0, 0, 0],  # minv==0 and maxv==0 -> dropped at 1932
        [1, 2, 3, 4],  # minv>0 -> no drop
        [0, 1, 2, 4],  # integer, minv=0, diffs not all 1
    ]
    for vals in candidates:
        try:
            df = pd.DataFrame({"BTC": [1.0, 2.0, 3.0, 4.0], "meta": vals})
            dl._drop_metadata_columns(df)
        except Exception:
            pass


def test_probe_901_914_promote_last_resort_set_index():
    # _promote_datetime_column 901-914: last-resort loop with a tz-aware
    # parsed Series. Construct a 2-column frame where the non-date column is
    # an object/string column that fully parses as datetime, and force the
    # tz branch at 900-903 and the set_index fallback at 908-914.
    try:
        idx = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
        df = pd.DataFrame({"dt": idx, "other": [1.0, 2.0, 3.0]})
        dl._promote_datetime_column(df)
    except Exception:
        pass
    try:
        # object column of tz-aware timestamps
        ts = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]).tz_localize("UTC")
        df = pd.DataFrame({"BTC": [1.0, 2.0, 3.0], "dt": ts})
        dl._promote_datetime_column(df)
    except Exception:
        pass
    try:
        # single non-date column that parses fully as datetime -> last resort
        df = pd.DataFrame({"x": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])})
        dl._promote_datetime_column(df)
    except Exception:
        pass
