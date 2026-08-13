from __future__ import annotations


def atr_trailing_stop(current_price: float, atr_value: float, multiplier: float, previous_stop: float | None = None) -> float:
    if current_price <= 0 or atr_value <= 0 or multiplier <= 0:
        raise ValueError("current_price, atr_value and multiplier must be positive")
    candidate = current_price - atr_value * multiplier
    if previous_stop is not None:
        candidate = max(candidate, previous_stop)
    return round(candidate, 4)
