"""Probe: real coercer np.datetime64('NaT') passthrough -> dayfirst block 227-247."""
import coverage

cov = coverage.Coverage(source=['strategies.betting_against_beta'])
cov.start()

import numpy as np
import pandas as pd
from strategies.betting_against_beta.data_loader import _normalize_index, _coerce_to_datetime_scalar

# Confirm real coercer behavior
for v in [np.datetime64('NaT'), pd.NaT]:
    try:
        r = _coerce_to_datetime_scalar(v)
        print('coercer', repr(v), '->', repr(r))
    except Exception as e:
        print('coercer', repr(v), 'RAISES', type(e).__name__)

# Object index mixing valid dates and np.datetime64('NaT')
idx = pd.Index(['2021-01-01', np.datetime64('NaT'), '2021-01-03'], dtype=object)
df = pd.DataFrame({'a': [1, 2, 3]}, index=idx)
try:
    out = _normalize_index(df.copy())
    print('SUCCESS, out index:', list(out.index), 'len', len(out))
except Exception as e:
    print('RAISED', type(e).__name__, e)

cov.stop()
cov.save()
data = cov.get_data()
for f in data.measured_files():
    if f.endswith('data_loader.py'):
        executed = sorted(l for l in range(215, 261) if l in data.lines(f))
        print('Executed 215-260:', executed)
        missing = sorted(l for l in range(215, 261) if l not in data.lines(f))
        print('Missing 215-260:', missing)