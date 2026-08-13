from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from trading_helper.scanner.indicators import atr, ema, macd, rsi, validate_ohlcv, volume_ratio
from trading_helper.scanner.scoring import ScoreResult, TechnicalSnapshot, score_snapshot


@dataclass(frozen=True)
class ScanResult:
    symbol: str
    price: float
    atr: float
    scoring: ScoreResult


def analyze(symbol: str, frame: pd.DataFrame) -> ScanResult:
    validate_ohlcv(frame)
    if len(frame) < 200:
        raise ValueError("At least 200 OHLCV rows are required")

    close = frame["close"].astype(float)
    ema20 = ema(close, 20)
    ema50 = ema(close, 50)
    ema200 = ema(close, 200)
    rsi14 = rsi(close, 14)
    macd_frame = macd(close)
    atr14 = atr(frame, 14)
    volume20 = volume_ratio(frame["volume"], 20)

    snapshot = TechnicalSnapshot(
        price=float(close.iloc[-1]),
        ema20=float(ema20.iloc[-1]),
        ema50=float(ema50.iloc[-1]),
        ema200=float(ema200.iloc[-1]),
        rsi=float(rsi14.iloc[-1]),
        macd=float(macd_frame["macd"].iloc[-1]),
        macd_signal=float(macd_frame["signal"].iloc[-1]),
        macd_histogram=float(macd_frame["histogram"].iloc[-1]),
        volume_ratio=float(volume20.iloc[-1]),
    )
    values = [
        snapshot.price,
        snapshot.ema20,
        snapshot.ema50,
        snapshot.ema200,
        snapshot.rsi,
        snapshot.macd,
        snapshot.macd_signal,
        snapshot.macd_histogram,
        snapshot.volume_ratio,
        float(atr14.iloc[-1]),
    ]
    if any(pd.isna(value) for value in values):
        raise ValueError("Latest indicator snapshot contains missing values")

    return ScanResult(
        symbol=symbol.upper(),
        price=snapshot.price,
        atr=float(atr14.iloc[-1]),
        scoring=score_snapshot(snapshot),
    )
