from __future__ import annotations

import numpy as np
import pandas as pd

REQUIRED_OHLCV = {"open", "high", "low", "close", "volume"}


def validate_ohlcv(frame: pd.DataFrame) -> None:
    missing = REQUIRED_OHLCV.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing OHLCV columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("OHLCV frame is empty")


def ema(series: pd.Series, span: int) -> pd.Series:
    if span <= 0:
        raise ValueError("EMA span must be positive")
    return series.astype(float).ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    if period <= 0:
        raise ValueError("RSI period must be positive")
    values = series.astype(float)
    delta = values.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    result = 100 - (100 / (1 + rs))
    return result.where(avg_loss != 0, 100.0)


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    values = series.astype(float)
    fast_line = ema(values, fast)
    slow_line = ema(values, slow)
    macd_line = fast_line - slow_line
    signal_line = ema(macd_line, signal)
    return pd.DataFrame({"macd": macd_line, "signal": signal_line, "histogram": macd_line - signal_line}, index=series.index)


def atr(frame: pd.DataFrame, period: int = 14) -> pd.Series:
    validate_ohlcv(frame)
    high = frame["high"].astype(float)
    low = frame["low"].astype(float)
    close = frame["close"].astype(float)
    previous_close = close.shift(1)
    true_range = pd.concat([(high - low), (high - previous_close).abs(), (low - previous_close).abs()], axis=1).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def volume_ratio(volume: pd.Series, period: int = 20) -> pd.Series:
    if period <= 0:
        raise ValueError("Volume period must be positive")
    values = volume.astype(float)
    average = values.rolling(period).mean()
    return values / average.replace(0, np.nan)
