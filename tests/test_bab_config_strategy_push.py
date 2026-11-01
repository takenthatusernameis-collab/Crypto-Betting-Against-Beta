"""Targeted coverage push for the remaining hitable BAB branches.

Targets:
  - config.py:113  _validate_ranges min_observations non-int append

Documented as unreachable (do not chase; plain dataclass has no slots, so the
freeze `object.__setattr__` never raises, and the run() empty-universe guard is
preceded by _load_returns rejecting empty frames):
  - config.py:95-96   freeze except
  - costs.py:59-60    freeze except
  - strategy.py:181   empty-universe ValueError (guarded by _load_returns)
  - strategy.py:188-189 setattr fallback
  - signals.py:37     to_numeric never yields object dtype with errors="coerce"
  - signals.py:75     reference n==0 continue (clean is never empty here)
  - metrics.py:97,114 ; portfolio.py:39-40,164-169 ; beta.py (all) ;
    data_loader.py:44,192-193,311-313,340-342 (all previously documented)
"""

from __future__ import annotations

import pytest

from strategies.betting_against_beta.config import BABConfig, BABConfigError


def test_config_min_observations_non_int_hits_validation_append():
    # config.py:112-115 min_observations must be an int; 1.5 is not.
    with pytest.raises(BABConfigError):
        BABConfig(min_observations=1.5)
