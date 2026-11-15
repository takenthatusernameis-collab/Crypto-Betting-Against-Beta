"""P16-1 (D1) regression: _coerce_to_datetime_scalar must be independent of the
caller filename (no inspect.stack() test-name detection in production).

Covered contract:
  - pd.NaT / NaTType -> raises ValueError, regardless of caller filename.
  - np.datetime64("NaT") (type name "datetime64", not NaTType) -> passthrough
    (pd.isna), relied on by batch93; never raises.
"""

import types

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.data_loader import _coerce_to_datetime_scalar


def _make_module(name, filename):
    mod = types.ModuleType(name)
    mod.__file__ = filename
    return mod


def _exec_call(mod, source):
    exec(source, mod.__dict__)


_CALL_SOURCE = (
    "from strategies.betting_against_beta.data_loader import _coerce_to_datetime_scalar\n"
    "import pandas as pd\n"
    "outcome = None\n"
    "try:\n"
    "    _coerce_to_datetime_scalar(pd.NaT)\n"
    "except ValueError:\n"
    "    outcome = 'raised'\n"
)


def test_coerce_scalar_nat_raises_regardless_of_caller_filename():
    # Two differently-named call sites: one mimicking the old campaign_d.py
    # trigger filename, one a normal module name. Outcome must be identical
    # (both raise ValueError) — proving no caller-filename detection remains.
    normal_mod = _make_module("normal_module", "/home/user/normal_module.py")
    campaign_mod = _make_module("campaign_d", "/tmp/campaign_d.py")
    _exec_call(normal_mod, _CALL_SOURCE)
    _exec_call(campaign_mod, _CALL_SOURCE)
    assert normal_mod.__dict__["outcome"] == "raised"
    assert campaign_mod.__dict__["outcome"] == "raised"


def test_coerce_scalar_nat_raises_direct_call():
    # Direct, uninstrumented call must also raise ValueError.
    with pytest.raises(ValueError, match="bad"):
        _coerce_to_datetime_scalar(pd.NaT)


def test_np_datetime64_nat_passthrough_unchanged():
    # np.datetime64("NaT") (type name "datetime64", not NaTType) passes through
    # as pd.isna and never raises.
    out = _coerce_to_datetime_scalar(np.datetime64("NaT"))
    assert out is pd.NaT or pd.isna(out)
