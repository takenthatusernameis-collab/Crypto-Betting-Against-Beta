"""Deep coverage tests for BABConfig validation and resolution."""

from __future__ import annotations

import pytest

from strategies.betting_against_beta.config import BABConfig, BABConfigError, _is_finite_number


class TestIsFiniteNumber:
    def test_non_finite_and_non_numeric_return_false(self):
        assert _is_finite_number(float("inf")) is False
        assert _is_finite_number(float("-inf")) is False
        assert _is_finite_number(float("nan")) is False
        assert _is_finite_number("not-a-number") is False
        assert _is_finite_number(None) is False
        assert _is_finite_number([1, 2]) is False

    def test_finite_numbers_return_true(self):
        assert _is_finite_number(1.0) is True
        assert _is_finite_number(0) is True
        assert _is_finite_number(1e-300) is True


class TestFrozenMutation:
    def test_frozen_config_attribute_mutation_raises(self):
        cfg = BABConfig()
        with pytest.raises(AttributeError):
            cfg.beta_window = 100


class TestIntegerFieldValidation:
    @pytest.mark.parametrize(
        "kw",
        [
            dict(min_rows="x"),
            dict(min_rows=0),
            dict(synthetic_n_days="x"),
            dict(synthetic_n_days=1),
            dict(synthetic_seed="x"),
            dict(vol_window="x"),
            dict(vol_window=5),
            dict(trend_ma_window="x"),
            dict(trend_ma_window=0),
            dict(trend_z_window="x"),
            dict(trend_z_window=0),
        ],
    )
    def test_invalid_integer_fields_raise(self, kw):
        with pytest.raises(BABConfigError):
            BABConfig(**kw)


class TestBoolAndEnumValidation:
    @pytest.mark.parametrize(
        "kw",
        [
            dict(regime_filter="yes"),
            dict(regime_method="invalid"),
            dict(vol_use_ewma="yes"),
        ],
    )
    def test_invalid_bool_and_method_fields_raise(self, kw):
        with pytest.raises(BABConfigError):
            BABConfig(**kw)


class TestVolThresholds:
    @pytest.mark.parametrize(
        "kw,msg_fragment",
        [
            (dict(vol_thresholds="x"), "vol_thresholds must be a non-empty"),
            (dict(vol_thresholds=[]), "vol_thresholds must be a non-empty"),
            (dict(vol_thresholds=("a",)), "vol_thresholds\\[0\\] must be a positive finite"),
            (dict(vol_thresholds=(0.0,)), "vol_thresholds\\[0\\] must be > 0"),
            (dict(vol_thresholds=(0.5, 0.4)), "vol_thresholds must be strictly increasing"),
        ],
    )
    def test_invalid_vol_thresholds_raise(self, kw, msg_fragment):
        with pytest.raises(BABConfigError, match=msg_fragment):
            BABConfig(**kw)

    def test_valid_vol_thresholds(self):
        cfg = BABConfig(vol_thresholds=(0.2, 0.8))
        assert cfg.vol_thresholds == (0.2, 0.8)


class TestVolPercentiles:
    @pytest.mark.parametrize(
        "kw",
        [
            dict(vol_percentiles=(0.5,)),
            dict(vol_percentiles=(0.5, 0.5, 0.5)),
            dict(vol_percentiles=(0.0, 0.5)),
            dict(vol_percentiles=(0.5, 1.0)),
            dict(vol_percentiles=(0.6, 0.4)),
            dict(vol_percentiles="x"),
        ],
    )
    def test_invalid_vol_percentiles_raise(self, kw):
        with pytest.raises(BABConfigError):
            BABConfig(**kw)


class TestVolHysteresis:
    @pytest.mark.parametrize("value", ["x", None, -0.1, 1.1])
    def test_invalid_vol_hysteresis_raise(self, value):
        with pytest.raises(BABConfigError):
            BABConfig(vol_hysteresis=value)


class TestRegimeScales:
    @pytest.mark.parametrize("kw", [dict(regime_scale_high="x"), dict(regime_scale_low=0.0), dict(regime_scale_high=float("nan"))])
    def test_invalid_regime_scales_raise(self, kw):
        with pytest.raises(BABConfigError):
            BABConfig(**kw)


class TestBetaNeutralBools:
    @pytest.mark.parametrize(
        "kw",
        [
            dict(beta_neutral="yes"),
            dict(beta_neutral_enforcement="yes"),
            dict(beta_neutral_correction="yes"),
            dict(beta_neutral_adjustment="yes"),
            dict(enable_tracking_error_monitoring="yes"),
        ],
    )
    def test_beta_neutral_flags_must_be_bool(self, kw):
        with pytest.raises(BABConfigError):
            BABConfig(**kw)


class TestBetaTargets:
    @pytest.mark.parametrize(
        "kw",
        [
            dict(beta_target="x"),
            dict(beta_tolerance=float("inf")),
            dict(max_beta_drift=-1.0),
        ],
    )
    def test_invalid_beta_targets_raise(self, kw):
        with pytest.raises(BABConfigError):
            BABConfig(**kw)


class TestTrackingError:
    @pytest.mark.parametrize(
        "kw",
        [
            dict(tracking_error_tolerance="x"),
            dict(tracking_error_limit=-0.1),
            dict(tracking_error_tolerance=float("nan")),
        ],
    )
    def test_invalid_tracking_error_raise(self, kw):
        with pytest.raises(BABConfigError):
            BABConfig(**kw)


class TestMutuallyExclusiveVolBands:
    def test_vol_thresholds_and_percentiles_together_raise(self):
        with pytest.raises(BABConfigError, match="set only one of"):
            BABConfig(vol_thresholds=(0.2, 0.8), vol_percentiles=(0.33, 0.66))


class TestQuantilesAndCosts:
    @pytest.mark.parametrize(
        "kw",
        [
            dict(long_quantile="x"),
            dict(short_quantile=0.0),
            dict(short_quantile=1.0),
            dict(transaction_costs="x"),
            dict(slippage=-0.1),
            dict(transaction_costs=float("inf")),
        ],
    )
    def test_invalid_quantiles_and_costs_raise(self, kw):
        with pytest.raises(BABConfigError):
            BABConfig(**kw)


class TestTurnoverAndLimits:
    @pytest.mark.parametrize(
        "kw",
        [
            dict(max_turnover="x"),
            dict(max_position_size=0.0),
            dict(max_total_turnover=-1.0),
            dict(rolling_min_window="x"),
            dict(rolling_min_window=0.0),
        ],
    )
    def test_invalid_turnover_limits_raise(self, kw):
        with pytest.raises(BABConfigError):
            BABConfig(**kw)


class TestStrings:
    @pytest.mark.parametrize(
        "kw",
        [
            dict(rebalance_freq=""),
            dict(rebalance_freq=None),
            dict(benchmark=""),
            dict(benchmark=None),
        ],
    )
    def test_invalid_string_fields_raise(self, kw):
        with pytest.raises(BABConfigError):
            BABConfig(**kw)


class TestShortingConstraintsNormalization:
    def test_shorting_constraints_dict_normalized(self):
        cfg = BABConfig(shorting_constraints={"max_short_exposure": 0.5})
        from strategies.betting_against_beta import shorting

        assert isinstance(cfg.shorting_constraints, shorting.ShortingConstraints)
        assert cfg.shorting_constraints.max_short_exposure == 0.5

    def test_shorting_constraints_invalid_dict_swallowed(self):
        cfg = BABConfig(shorting_constraints={"max_short_exposure": -0.1})
        assert cfg.shorting_constraints is None or isinstance(
            cfg.shorting_constraints, dict
        )


class TestResolvedUniverse:
    def test_derives_from_columns_minus_benchmark(self):
        cfg = BABConfig(universe=None, universe_override=None)
        assert cfg.resolved_universe(["BTC", "ETH", "SOL"]) == ["ETH", "SOL"]

    def test_universe_intersected_with_columns(self):
        cfg = BABConfig(universe=["BTC", "ETH", "MISSING"])
        assert cfg.resolved_universe(["BTC", "ETH"]) == ["BTC", "ETH"]

    def test_universe_override_used_when_set(self):
        cfg = BABConfig(universe_override=["XRP", "ADA"])
        assert cfg.resolved_universe(["BTC", "XRP", "ADA"]) == ["XRP", "ADA"]

    def test_universe_override_no_overlap_returns_available(self):
        cfg = BABConfig(universe_override=["ZZZ"])
        assert cfg.resolved_universe(["BTC", "ETH"]) == ["BTC", "ETH"]

    def test_no_columns_returns_universe(self):
        cfg = BABConfig(universe=["BTC", "ETH"])
        assert cfg.resolved_universe(None) == ["BTC", "ETH"]
