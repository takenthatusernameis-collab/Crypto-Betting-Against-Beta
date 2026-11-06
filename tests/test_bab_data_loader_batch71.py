import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import numpy as np
import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

# Batch 71: measured-delta probe. Covers line 400 (_coerce_to_datetime_scalar
# str-epoch seconds non-integer, outer branch: av < 1e9) via a direct call.
# Baseline miss 109 -> 107 (-1 with batch72 line 84).

def test_400_str_epoch_seconds_noninteger_outer():
    ts = dl._coerce_to_datetime_scalar('170000000.5')
    assert ts is not None
