from datetime import UTC, datetime

from trading_helper.scanner.scanners import ScannerSnapshot
from trading_helper.signal_engine import score_setup


def strong_snapshot() -> ScannerSnapshot:
    return ScannerSnapshot(
        price=120,
        ema20=115,
        ema50=110,
        ema200=100,
        rsi=60,
        macd=2,
        macd_signal=1,
        macd_histogram=1,
        atr=3,
        atr_percent=2.5,
        volume_ratio=1.8,
        obv_rising=True,
        roc=4,
        bollinger_lower=100,
        bollinger_upper=119,
        bollinger_bandwidth=0.08,
        trend_structure=True,
        price_momentum=True,
        growing_volume=True,
        breakout=True,
        pullback=True,
        near_support=True,
    )


def test_scoring_has_exact_breakdown_and_explanation() -> None:
    result = score_setup(strong_snapshot(), risk_reward=3, data_timestamp=datetime.now(UTC))
    assert result.score == 100
    assert result.classification == "EXCEPTIONAL_SETUP"
    assert result.breakdown == {
        "trend": 25,
        "momentum": 20,
        "volume": 15,
        "volatility": 10,
        "setup": 20,
        "risk": 10,
    }
    assert result.reasons


def test_delayed_data_is_always_disclosed() -> None:
    result = score_setup(
        strong_snapshot(),
        risk_reward=2,
        data_timestamp=datetime.now(UTC),
        is_delayed=True,
        delay_minutes=15,
    )
    assert "delayed" in result.warnings[0]
