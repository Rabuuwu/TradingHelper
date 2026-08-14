from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CostProfile:
    name: str
    commission_buy: float = 0.0
    commission_sell: float = 0.0
    minimum_fee: float = 0.0
    fx_percent: float = 0.0
    spread_percent: float = 0.0
    slippage_percent: float = 0.0

    @classmethod
    def from_mapping(cls, name: str, data: dict[str, Any]) -> CostProfile:
        return cls(
            name=name,
            **{
                field: float(data.get(field, 0))
                for field in (
                    "commission_buy",
                    "commission_sell",
                    "minimum_fee",
                    "fx_percent",
                    "spread_percent",
                    "slippage_percent",
                )
            },
        )


@dataclass(frozen=True)
class CostEstimate:
    gross_expected_profit: float
    estimated_fees: float
    estimated_fx_cost: float
    estimated_spread_cost: float
    estimated_slippage: float
    estimated_total_cost: float
    expected_net_profit: float
    cost_to_expected_profit_ratio: float


class FeeCalculator:
    def __init__(self, profile: CostProfile) -> None:
        self.profile = profile

    def estimate(
        self, entry_price: float, target_price: float, quantity: float, *, requires_fx: bool = False
    ) -> CostEstimate:
        if entry_price <= 0 or target_price <= entry_price or quantity <= 0:
            raise ValueError("entry, target and quantity must describe a positive long trade")
        entry_value = entry_price * quantity
        exit_value = target_price * quantity
        gross = exit_value - entry_value
        buy_fee = max(self.profile.commission_buy, self.profile.minimum_fee)
        sell_fee = max(self.profile.commission_sell, self.profile.minimum_fee)
        fees = buy_fee + sell_fee
        fx = (entry_value + exit_value) * self.profile.fx_percent / 100 if requires_fx else 0.0
        spread = entry_value * self.profile.spread_percent / 100
        slippage = (entry_value + exit_value) * self.profile.slippage_percent / 100
        total = fees + fx + spread + slippage
        ratio = total / gross * 100 if gross else float("inf")
        return CostEstimate(
            *(
                round(value, 4)
                for value in (
                    gross,
                    fees,
                    fx,
                    spread,
                    slippage,
                    total,
                    gross - total,
                    ratio,
                )
            )
        )
