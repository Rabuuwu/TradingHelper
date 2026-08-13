from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class PositionSizing:
    quantity: int
    capital_required: float
    maximum_loss: float
    risk_per_share: float


def calculate_position_size(
    portfolio_value: float,
    risk_percent: float,
    entry_price: float,
    stop_price: float,
) -> PositionSizing:
    if portfolio_value <= 0:
        raise ValueError("portfolio_value must be greater than zero")
    if not 0 < risk_percent <= 100:
        raise ValueError("risk_percent must be between 0 and 100")
    if entry_price <= 0 or stop_price <= 0:
        raise ValueError("prices must be greater than zero")
    if stop_price >= entry_price:
        raise ValueError("stop_price must be below entry_price for a long position")

    maximum_loss = portfolio_value * (risk_percent / 100)
    risk_per_share = entry_price - stop_price
    quantity = math.floor(maximum_loss / risk_per_share)

    return PositionSizing(
        quantity=quantity,
        capital_required=round(quantity * entry_price, 2),
        maximum_loss=round(quantity * risk_per_share, 2),
        risk_per_share=round(risk_per_share, 4),
    )
