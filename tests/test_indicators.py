import pandas as pd

from trading_helper.scanner.indicators import atr, ema, macd, rsi, volume_ratio


def test_indicators_return_aligned_series() -> None:
    close = pd.Series(range(1, 251), dtype=float)
    frame = pd.DataFrame(
        {
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": pd.Series([1000 + i for i in range(250)], dtype=float),
        }
    )
    assert len(ema(close, 20)) == 250
    assert len(rsi(close)) == 250
    assert list(macd(close).columns) == ["macd", "signal", "histogram"]
    assert atr(frame).iloc[-1] > 0
    assert volume_ratio(frame["volume"]).iloc[-1] > 0
