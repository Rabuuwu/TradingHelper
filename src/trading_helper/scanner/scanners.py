from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from trading_helper.scanner.indicators import atr, bollinger_bands, ema, macd, obv, roc, rsi


@dataclass(frozen=True)
class ScannerSnapshot:
    price: float
    ema20: float
    ema50: float
    ema200: float
    rsi: float
    macd: float
    macd_signal: float
    macd_histogram: float
    atr: float
    atr_percent: float
    volume_ratio: float
    obv_rising: bool
    roc: float
    bollinger_lower: float
    bollinger_upper: float
    bollinger_bandwidth: float
    trend_structure: bool
    price_momentum: bool
    growing_volume: bool
    breakout: bool
    pullback: bool
    near_support: bool


def build_snapshot(frame: pd.DataFrame) -> ScannerSnapshot:
    if len(frame) < 200:
        raise ValueError("At least 200 complete candles are required")
    close = frame["close"].astype(float)
    volume = frame["volume"].astype(float)
    ema20, ema50, ema200 = ema(close, 20), ema(close, 50), ema(close, 200)
    rsi14, macd_values, atr14 = rsi(close), macd(close), atr(frame)
    roc12, bands, obv_values = roc(close), bollinger_bands(close), obv(close, volume)
    volume_average = volume.rolling(20).mean()
    previous_high = frame["high"].astype(float).iloc[-21:-1].max()
    support = frame["low"].astype(float).iloc[-21:-1].min()
    values = [
        ema20.iloc[-1],
        ema50.iloc[-1],
        ema200.iloc[-1],
        rsi14.iloc[-1],
        atr14.iloc[-1],
        roc12.iloc[-1],
        bands["lower"].iloc[-1],
    ]
    if any(pd.isna(value) for value in values):
        raise ValueError("Latest indicator snapshot contains missing values")
    price = float(close.iloc[-1])
    return ScannerSnapshot(
        price=price,
        ema20=float(ema20.iloc[-1]),
        ema50=float(ema50.iloc[-1]),
        ema200=float(ema200.iloc[-1]),
        rsi=float(rsi14.iloc[-1]),
        macd=float(macd_values["macd"].iloc[-1]),
        macd_signal=float(macd_values["signal"].iloc[-1]),
        macd_histogram=float(macd_values["histogram"].iloc[-1]),
        atr=float(atr14.iloc[-1]),
        atr_percent=float(atr14.iloc[-1] / price * 100),
        volume_ratio=float(volume.iloc[-1] / volume_average.iloc[-1]),
        obv_rising=bool(obv_values.iloc[-1] > obv_values.iloc[-10]),
        roc=float(roc12.iloc[-1]),
        bollinger_lower=float(bands["lower"].iloc[-1]),
        bollinger_upper=float(bands["upper"].iloc[-1]),
        bollinger_bandwidth=float(bands["bandwidth"].iloc[-1]),
        trend_structure=bool(
            frame["high"].iloc[-20:-10].max() < frame["high"].iloc[-10:].max()
            and frame["low"].iloc[-20:-10].min() < frame["low"].iloc[-10:].min()
        ),
        price_momentum=bool(price > close.iloc[-10]),
        growing_volume=bool(volume.iloc[-5:].mean() > volume.iloc[-20:-5].mean()),
        breakout=bool(price > previous_high),
        pullback=bool(price > ema50.iloc[-1] and abs(price - ema20.iloc[-1]) / price <= 0.02),
        near_support=bool(0 <= (price - support) / price <= 0.04),
    )


def trend_scanner(snapshot: ScannerSnapshot) -> dict[str, bool]:
    return {
        "ema20_above_ema50": snapshot.ema20 > snapshot.ema50,
        "ema50_above_ema200": snapshot.ema50 > snapshot.ema200,
        "price_above_ema200": snapshot.price > snapshot.ema200,
        "trend_structure": snapshot.trend_structure,
    }


def momentum_scanner(snapshot: ScannerSnapshot) -> dict[str, bool]:
    return {
        "healthy_rsi": 50 <= snapshot.rsi <= 70,
        "macd_bullish": snapshot.macd > snapshot.macd_signal,
        "positive_roc": snapshot.roc > 0,
        "price_momentum": snapshot.price_momentum,
    }


def volume_scanner(snapshot: ScannerSnapshot) -> dict[str, bool]:
    return {
        "volume_spike": snapshot.volume_ratio >= 1.5,
        "obv_rising": snapshot.obv_rising,
        "growing_volume": snapshot.growing_volume,
    }


def breakout_scanner(snapshot: ScannerSnapshot) -> bool:
    return snapshot.breakout


def pullback_scanner(snapshot: ScannerSnapshot) -> bool:
    return snapshot.pullback
