from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime

from trading_helper.scanner.scanners import ScannerSnapshot

LABELS = (
    (90, "EXCEPTIONAL_SETUP"),
    (80, "STRONG_BUY_SETUP"),
    (70, "BUY_SETUP"),
    (60, "INTERESTING"),
    (40, "WATCH"),
    (0, "IGNORE"),
)


@dataclass(frozen=True)
class SignalScore:
    score: int
    classification: str
    breakdown: dict[str, int]
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    data_timestamp: datetime


def classify(score: int) -> str:
    return next(label for threshold, label in LABELS if score >= threshold)


def score_setup(
    snapshot: ScannerSnapshot,
    *,
    risk_reward: float,
    data_timestamp: datetime,
    is_delayed: bool = False,
    delay_minutes: int | None = None,
) -> SignalScore:
    reasons: list[str] = []
    warnings: list[str] = []

    def points(check: bool, value: int, reason: str) -> int:
        if check:
            reasons.append(reason)
            return value
        return 0

    trend = sum(
        (
            points(snapshot.ema20 > snapshot.ema50, 8, "EMA20 above EMA50"),
            points(snapshot.ema50 > snapshot.ema200, 8, "EMA50 above EMA200"),
            points(snapshot.price > snapshot.ema200, 5, "Price above EMA200"),
            points(snapshot.trend_structure, 4, "Higher-high/higher-low structure"),
        )
    )
    momentum = sum(
        (
            points(50 <= snapshot.rsi <= 70, 5, "RSI in constructive zone"),
            points(snapshot.macd > snapshot.macd_signal, 5, "MACD above signal"),
            points(snapshot.roc > 0, 5, "Positive rate of change"),
            points(snapshot.price_momentum, 5, "Positive price momentum"),
        )
    )
    volume = sum(
        (
            points(snapshot.volume_ratio >= 1.5, 6, "Relative volume spike"),
            points(snapshot.obv_rising, 4, "OBV rising"),
            points(snapshot.growing_volume, 5, "Recent volume growing"),
        )
    )
    volatility = sum(
        (
            points(1 <= snapshot.atr_percent <= 8, 5, "Usable ATR range"),
            points(
                snapshot.price >= snapshot.bollinger_upper or snapshot.bollinger_bandwidth < 0.1,
                5,
                "Bollinger expansion/squeeze context",
            ),
        )
    )
    setup = sum(
        (
            points(snapshot.breakout, 8, "Breakout above 20-bar high"),
            points(snapshot.pullback, 5, "Pullback near EMA20"),
            points(snapshot.near_support, 7, "Price near 20-bar support"),
        )
    )
    risk = points(risk_reward >= 2, 5, "Risk/reward at least 2")
    risk += points(risk_reward >= 3, 5, "Risk/reward at least 3")
    breakdown = {
        "trend": trend,
        "momentum": momentum,
        "volume": volume,
        "volatility": volatility,
        "setup": setup,
        "risk": risk,
    }
    score = min(sum(breakdown.values()), 100)
    if is_delayed:
        warnings.append(
            f"Market data is delayed{f' by {delay_minutes} minutes' if delay_minutes else ''}"
        )
    if snapshot.rsi > 70:
        warnings.append("RSI indicates a potentially overbought market")
    return SignalScore(
        score, classify(score), breakdown, tuple(reasons), tuple(warnings), data_timestamp
    )


def snapshot_details(snapshot: ScannerSnapshot) -> dict[str, object]:
    return asdict(snapshot)
