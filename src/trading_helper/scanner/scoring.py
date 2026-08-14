from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TechnicalSnapshot:
    price: float
    ema20: float
    ema50: float
    ema200: float
    rsi: float
    macd: float
    macd_signal: float
    macd_histogram: float
    volume_ratio: float
    breakout: bool = False
    pullback: bool = False


@dataclass(frozen=True)
class ScoreResult:
    score: int
    label: str
    reasons: tuple[str, ...]


def label_for_score(score: int) -> str:
    if score >= 85:
        return "STRONG_SETUP"
    if score >= 75:
        return "SETUP"
    if score >= 60:
        return "WATCH"
    if score >= 40:
        return "NEUTRAL"
    return "IGNORE"


def score_snapshot(snapshot: TechnicalSnapshot) -> ScoreResult:
    score = 0
    reasons: list[str] = []

    if snapshot.price > snapshot.ema200:
        score += 10
        reasons.append("price_above_ema200")
    if snapshot.ema20 > snapshot.ema50:
        score += 10
        reasons.append("ema20_above_ema50")
    if snapshot.ema50 > snapshot.ema200:
        score += 10
        reasons.append("ema50_above_ema200")
    if 50 <= snapshot.rsi <= 70:
        score += 10
        reasons.append("rsi_bullish_zone")
    elif 45 <= snapshot.rsi < 50:
        score += 5
        reasons.append("rsi_recovering")
    if snapshot.macd > snapshot.macd_signal:
        score += 8
        reasons.append("macd_above_signal")
    if snapshot.macd_histogram > 0:
        score += 7
        reasons.append("macd_positive_histogram")
    if snapshot.volume_ratio >= 1.5:
        score += 15
        reasons.append("strong_relative_volume")
    elif snapshot.volume_ratio >= 1.1:
        score += 8
        reasons.append("positive_relative_volume")
    if snapshot.breakout:
        score += 20
        reasons.append("breakout_above_20_bar_high")
    elif snapshot.pullback:
        score += 12
        reasons.append("pullback_to_ema20")

    score = min(score, 100)
    return ScoreResult(score=score, label=label_for_score(score), reasons=tuple(reasons))
