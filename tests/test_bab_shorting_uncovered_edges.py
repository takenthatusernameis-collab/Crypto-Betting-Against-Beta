import pandas as pd
import pytest

from strategies.betting_against_beta import shorting


def test_apply_shorting_constraints_frozen_negative_caps_raise():
    # Line ~208: per-asset cap negative when passed via mutated frozen constraints
    sc = shorting.ShortingConstraints()
    object.__setattr__(sc, "_frozen", False)
    object.__setattr__(sc, "max_short_notional_per_asset", -0.1)
    object.__setattr__(sc, "_frozen", True)
    df = pd.DataFrame({"A": [-0.5]})
    with pytest.raises(shorting.BABShortingError):
        shorting.apply_shorting_constraints(df, sc)

    # Line ~219: total exposure cap negative
    sc2 = shorting.ShortingConstraints()
    object.__setattr__(sc2, "_frozen", False)
    object.__setattr__(sc2, "max_short_exposure", -0.1)
    object.__setattr__(sc2, "_frozen", True)
    df2 = pd.DataFrame({"A": [-0.5]})
    with pytest.raises(shorting.BABShortingError):
        shorting.apply_shorting_constraints(df2, sc2)
