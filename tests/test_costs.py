import pytest

from trading_helper.risk.costs import CostProfile, FeeCalculator


def test_fee_calculator_exposes_cost_breakdown() -> None:
    calculator = FeeCalculator(
        CostProfile(
            "test",
            commission_buy=1,
            commission_sell=1,
            fx_percent=0.5,
            spread_percent=0.1,
            slippage_percent=0.05,
        )
    )
    result = calculator.estimate(100, 110, 0.5, requires_fx=True)
    assert result.gross_expected_profit == 5
    assert result.estimated_total_cost > 2
    assert result.expected_net_profit < result.gross_expected_profit


def test_fee_calculator_rejects_invalid_trade() -> None:
    with pytest.raises(ValueError):
        FeeCalculator(CostProfile("test")).estimate(100, 90, 1)
