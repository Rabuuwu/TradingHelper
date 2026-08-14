import pytest

from trading_helper.risk.manager import (
    calculate_position_size,
    check_trade_feasibility,
    risk_reward_ratio,
)


def test_position_size_limits_loss_to_configured_risk() -> None:
    result = calculate_position_size(10_000, 1, 100, 95)
    assert result.quantity == 20
    assert result.capital_required == 2_000
    assert result.maximum_loss == 100


def test_stop_must_be_below_entry_for_long_position() -> None:
    with pytest.raises(ValueError):
        calculate_position_size(10_000, 1, 100, 101)


def test_risk_reward_ratio() -> None:
    assert risk_reward_ratio(100, 95, 115) == 3


def test_position_size_does_not_exceed_available_capital() -> None:
    result = calculate_position_size(10_000, 1, 100, 99.9)
    assert result.quantity == 100
    assert result.capital_required == 10_000


def test_fractional_sizing_supports_small_portfolio() -> None:
    result = calculate_position_size(25, 1, 100, 95, fractional=True)
    assert result.quantity == 0.05


def test_trade_is_rejected_when_costs_consume_reward() -> None:
    result = check_trade_feasibility(
        100,
        100,
        1,
        100,
        95,
        100,
        fractional=True,
        estimated_total_cost=1,
        expected_gross_profit=2,
        max_cost_to_profit_percent=30,
    )
    assert result.status == "TRADE_REJECTED_COSTS"
