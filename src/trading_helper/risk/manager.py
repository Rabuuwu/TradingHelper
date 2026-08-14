from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class PositionSizing:
    quantity: float
    capital_required: float
    maximum_loss: float
    risk_per_share: float


def calculate_position_size(
    portfolio_value: float,
    risk_percent: float,
    entry_price: float,
    stop_price: float,
    max_position_value: float | None = None,
    fractional: bool = False,
    precision: int = 4,
) -> PositionSizing:
    if portfolio_value <= 0:
        raise ValueError("portfolio_value must be greater than zero")
    if not 0 < risk_percent <= 100:
        raise ValueError("risk_percent must be between 0 and 100")
    if entry_price <= 0 or stop_price <= 0:
        raise ValueError("prices must be greater than zero")
    if stop_price >= entry_price:
        raise ValueError("stop_price must be below entry_price for a long position")

    risk_budget = portfolio_value * (risk_percent / 100)
    risk_per_share = entry_price - stop_price
    raw_quantity = risk_budget / risk_per_share
    affordable_value = portfolio_value if max_position_value is None else max_position_value
    if affordable_value <= 0:
        raise ValueError("max_position_value must be greater than zero")
    raw_quantity = min(raw_quantity, affordable_value / entry_price)
    quantity = round(raw_quantity, precision) if fractional else math.floor(raw_quantity)

    return PositionSizing(
        quantity=quantity,
        capital_required=round(quantity * entry_price, 2),
        maximum_loss=round(quantity * risk_per_share, 2),
        risk_per_share=round(risk_per_share, 4),
    )


@dataclass(frozen=True)
class TradeFeasibility:
    status: str
    feasible: bool
    sizing: PositionSizing
    reason: str


def check_trade_feasibility(
    portfolio_value: float,
    available_capital: float,
    risk_percent: float,
    entry_price: float,
    stop_price: float,
    max_position_percent: float,
    *,
    fractional: bool,
    estimated_total_cost: float = 0.0,
    expected_gross_profit: float = 0.0,
    max_cost_to_profit_percent: float = 30.0,
) -> TradeFeasibility:
    max_position = min(available_capital, portfolio_value * max_position_percent / 100)
    sizing = calculate_position_size(
        portfolio_value,
        risk_percent,
        entry_price,
        stop_price,
        max_position_value=max_position,
        fractional=fractional,
    )
    if sizing.quantity <= 0:
        return TradeFeasibility(
            "TRADE_REJECTED_CAPITAL", False, sizing, "Capital is too small for the minimum position"
        )
    if expected_gross_profit <= 0:
        return TradeFeasibility(
            "TRADE_REJECTED_REWARD", False, sizing, "Expected gross profit must be positive"
        )
    cost_ratio = estimated_total_cost / expected_gross_profit * 100
    if cost_ratio > max_cost_to_profit_percent:
        return TradeFeasibility(
            "TRADE_REJECTED_COSTS",
            False,
            sizing,
            f"Costs consume {cost_ratio:.1f}% of expected profit",
        )
    return TradeFeasibility("FEASIBLE", True, sizing, "Trade fits configured limits")


def risk_reward_ratio(entry_price: float, stop_price: float, target_price: float) -> float:
    if stop_price >= entry_price:
        raise ValueError("stop_price must be below entry_price")
    if target_price <= entry_price:
        raise ValueError("target_price must be above entry_price")
    return (target_price - entry_price) / (entry_price - stop_price)
