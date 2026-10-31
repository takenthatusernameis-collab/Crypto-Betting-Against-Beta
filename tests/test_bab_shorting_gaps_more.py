import pandas as pd
import numpy as np
import pytest

from strategies.betting_against_beta import shorting
from strategies.betting_against_beta.errors import BABDataError


def test_shorting_mutate_frozen():
    sc = shorting.ShortingConstraints()
    with pytest.raises(AttributeError):
        sc.default_borrow_bps_per_year = 0.03


def test_shorting_postinit_aliases():
    sc = shorting.ShortingConstraints(max_short_leverage=0.5)
    assert sc.max_short_exposure == 0.5
    sc2 = shorting.ShortingConstraints(max_short_weight=0.3)
    assert sc2.max_short_notional_per_asset == 0.3


def test_borrow_bps_scalar_normalized():
    sc = shorting.ShortingConstraints(borrow_bps_per_year=0.07)
    assert sc.borrow_bps("X") == 0.07


def test_validate_bad_types():
    with pytest.raises(shorting.BABShortingError):
        shorting.ShortingConstraints(default_borrow_bps_per_year=-1)
    with pytest.raises(shorting.BABShortingError):
        shorting.ShortingConstraints(max_short_exposure=-0.1)
    with pytest.raises(shorting.BABShortingError):
        shorting.ShortingConstraints(max_short_notional_per_asset=-0.1)
    with pytest.raises(shorting.BABShortingError):
        shorting.ShortingConstraints(max_short_leverage=-0.1)
    with pytest.raises(shorting.BABShortingError):
        shorting.ShortingConstraints(max_short_weight=-0.1)
    with pytest.raises(shorting.BABShortingError):
        shorting.ShortingConstraints(borrow_bps_per_year={"A": -0.1})
    with pytest.raises(shorting.BABShortingError):
        shorting.ShortingConstraints(borrowable="bad")


def test_borrowable_wildcard_and_fallback():
    sc = shorting.ShortingConstraints(borrowable={"*": False})
    assert sc.is_borrowable("BTC") is False
    sc = shorting.ShortingConstraints(borrowable={"BTC": True})
    assert sc.is_borrowable("ETH") is True  # not in dict, no wildcard -> True


def test_borrow_bps_dict_wildcard():
    sc = shorting.ShortingConstraints(borrow_bps_per_year={"ETH": 0.1})
    assert sc.borrow_bps("ETH") == 0.1
    assert sc.borrow_bps("BTC") == 0.02
    sc2 = shorting.ShortingConstraints(borrow_bps_per_year={"*": 0.03})
    assert sc2.borrow_bps("X") == 0.03
    assert sc2.borrow_rate_annual("X") == 0.03


def test_apply_first_arg_is_sc_empty():
    out = shorting.apply_shorting_constraints(shorting.ShortingConstraints())
    assert isinstance(out, pd.DataFrame)


def test_apply_empty_df():
    out = shorting.apply_shorting_constraints(pd.DataFrame())
    assert isinstance(out, pd.DataFrame)


def test_apply_none():
    out = shorting.apply_shorting_constraints(None)
    assert isinstance(out, pd.DataFrame)


def test_apply_with_index_but_empty_clean():
    df = pd.DataFrame(index=[0], columns=[])
    out = shorting.apply_shorting_constraints(df)
    assert isinstance(out, pd.DataFrame)


def test_apply_signal_conversion_long_only():
    df = pd.DataFrame({"A": [1], "B": [1]})
    out = shorting.apply_shorting_constraints(df)
    assert isinstance(out, pd.DataFrame)


def test_apply_signal_conversion_short_only():
    df = pd.DataFrame({"A": [-1], "B": [-1]})
    out = shorting.apply_shorting_constraints(df)
    assert isinstance(out, pd.DataFrame)


def test_apply_kwargs_paths():
    df = pd.DataFrame({"A": [-1.0], "B": [1.0]})
    out = shorting.apply_shorting_constraints(df, shorting_constraints={"max_short_exposure": 0.5})
    assert isinstance(out, pd.DataFrame)
    out = shorting.apply_shorting_constraints(df, shorting_constraints=shorting.ShortingConstraints(max_short_exposure=0.5))
    assert isinstance(out, pd.DataFrame)
    out = shorting.apply_shorting_constraints(df, shorting_constraints="bad")
    assert isinstance(out, pd.DataFrame)


def test_apply_constraints_arg_paths():
    df = pd.DataFrame({"A": [-1.0], "B": [1.0]})
    out = shorting.apply_shorting_constraints(df, constraints={"max_short_exposure": 0.5})
    assert isinstance(out, pd.DataFrame)
    out = shorting.apply_shorting_constraints(df, constraints=shorting.ShortingConstraints(max_short_exposure=0.5))
    assert isinstance(out, pd.DataFrame)
    out = shorting.apply_shorting_constraints(df, constraints="bad")
    assert isinstance(out, pd.DataFrame)


def test_apply_borrowable_non_strict_removes():
    df = pd.DataFrame({"A": [-1.0], "B": [1.0]})
    sc = shorting.ShortingConstraints(borrowable={"A": False}, strict=False)
    out = shorting.apply_shorting_constraints(df, sc)
    assert out["A"].iloc[0] == 0.0


def test_apply_borrowable_strict_raises():
    df = pd.DataFrame({"A": [-1.0], "B": [1.0]})
    sc = shorting.ShortingConstraints(borrowable={"A": False}, strict=True)
    with pytest.raises(shorting.BABShortingError):
        shorting.apply_shorting_constraints(df, sc)


def test_apply_per_asset_cap():
    df = pd.DataFrame({"A": [-1.0], "B": [1.0]})
    sc = shorting.ShortingConstraints(max_short_notional_per_asset=0.3)
    out = shorting.apply_shorting_constraints(df, sc)
    assert abs(out["A"].iloc[0]) <= 0.3 + 1e-10


def test_apply_total_cap():
    df = pd.DataFrame({"A": [-0.5], "B": [-0.5], "C": [1.0]})
    sc = shorting.ShortingConstraints(max_short_exposure=0.5)
    out = shorting.apply_shorting_constraints(df, sc)
    total_short = (-out).clip(lower=0).sum(axis=1).iloc[0]
    assert total_short <= 0.5 + 1e-10


def test_aliases():
    assert shorting.BorrowConstraints is shorting.ShortingConstraints
    assert shorting.enforce_shorting_constraints is shorting.apply_shorting_constraints
    assert shorting.apply_borrow_constraints is shorting.apply_shorting_constraints


def test_apply_clean_infs():
    df = pd.DataFrame({"A": [-1.0, np.inf], "B": [1.0, -np.inf]})
    out = shorting.apply_shorting_constraints(df)
    assert np.isfinite(out.values).all()


def test_apply_weights_not_signals():
    # values not in {-1,0,1} -> treated as weights
    df = pd.DataFrame({"A": [0.5], "B": [-0.3]})
    out = shorting.apply_shorting_constraints(df)
    assert isinstance(out, pd.DataFrame)


def test_apply_per_asset_cap_negative_in_apply():
    df = pd.DataFrame({"A": [-1.0], "B": [1.0]})
    sc = shorting.ShortingConstraints()
    # bypass validation? can't easily mutate frozen; but pass constraints dict with bad value
    with pytest.raises(shorting.BABShortingError):
        shorting.apply_shorting_constraints(df, constraints={"max_short_notional_per_asset": -0.1})


def test_apply_total_cap_negative_in_apply():
    df = pd.DataFrame({"A": [-1.0], "B": [1.0]})
    with pytest.raises(shorting.BABShortingError):
        shorting.apply_shorting_constraints(df, constraints={"max_short_exposure": -0.1})


def test_apply_with_inf_nan_cleanup():
    df = pd.DataFrame({"A": [-1.0], "B": [1.0]})
    out = shorting.apply_shorting_constraints(df)
    assert np.isfinite(out.values).all()


def test_apply_df_with_cols_but_becomes_empty_after_clean_path():
    df = pd.DataFrame({"A": [np.inf], "B": [-np.inf]})
    # clean will replace inf with nan, then fillna 0
    out = shorting.apply_shorting_constraints(df)
    assert isinstance(out, pd.DataFrame)


def test_apply_signal_like_non_intish():
    df = pd.DataFrame({"A": [0.5, 0], "B": [0.5, 0]})  # weights
    out = shorting.apply_shorting_constraints(df)
    assert isinstance(out, pd.DataFrame)


def test_apply_signal_like_mixed_signals_and_weights():
    df = pd.DataFrame({"A": [-1.0, 0.3], "B": [1.0, -0.2]})
    out = shorting.apply_shorting_constraints(df)
    assert isinstance(out, pd.DataFrame)


def test_apply_signal_like_all_nonzero_but_not_intlike():
    df = pd.DataFrame({"A": [0.5], "B": [0.5]})
    out = shorting.apply_shorting_constraints(df)
    assert isinstance(out, pd.DataFrame)


def test_apply_constraints_passed_as_second_arg_dict():
    df = pd.DataFrame({"A": [-1.0], "B": [1.0]})
    out = shorting.apply_shorting_constraints(df, {"max_short_exposure": 0.5})
    assert isinstance(out, pd.DataFrame)


def test_apply_constraints_passed_as_second_arg_bad():
    df = pd.DataFrame({"A": [-1.0], "B": [1.0]})
    out = shorting.apply_shorting_constraints(df, "x")
    assert isinstance(out, pd.DataFrame)


def test_apply_constraints_passed_as_second_arg_obj():
    df = pd.DataFrame({"A": [-1.0], "B": [1.0]})
    out = shorting.apply_shorting_constraints(df, shorting.ShortingConstraints(max_short_exposure=0.5))
    assert isinstance(out, pd.DataFrame)


def test_apply_with_multirow_signals_mixed():
    df = pd.DataFrame({"A": [-1.0, 0.5], "B": [1.0, -0.5]})
    out = shorting.apply_shorting_constraints(df)
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 2
