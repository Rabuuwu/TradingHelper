from trading_helper.scanner.scoring import TechnicalSnapshot, score_snapshot


def test_strong_snapshot_scores_bullish_components() -> None:
    result = score_snapshot(
        TechnicalSnapshot(
            price=120,
            ema20=115,
            ema50=110,
            ema200=100,
            rsi=60,
            macd=2,
            macd_signal=1,
            macd_histogram=1,
            volume_ratio=1.6,
        )
    )
    assert result.score == 70
    assert result.label == "WATCH"
    assert "price_above_ema200" in result.reasons
