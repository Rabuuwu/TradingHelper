import pytest

from trading_helper.risk.manager import calculate_position_size


def test_position_size_limits_loss_to_configured_risk() -> None:
    result = calculate_position_size(
        portfolio_value=10_000,
        risk_percent=1,
        entry_price=100,
        stop_price=95,
    )

    assert result.quantity == 20
    assert result.capital_required == 2_000
    assert result.maximum_loss == 100


def test_stop_must_be_below_entry_for_long_position() -> None:
    with pytest.raises(ValueError):
        calculate_position_size(10_000, 1, 100, 101)
