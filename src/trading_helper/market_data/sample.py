from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

from trading_helper.market_data.models import (
    CandleBatch,
    DataProvenance,
    MarketStatus,
    Quote,
    SymbolInfo,
)
from trading_helper.market_data.provider import MarketDataProvider


class SampleMarketDataProvider(MarketDataProvider):
    """Deterministic offline provider for setup, demos and CI. Never performs network I/O."""

    name = "sample"
    _symbols = {
        "AAPL": "Apple Inc.",
        "AMD": "Advanced Micro Devices",
        "MSFT": "Microsoft Corp.",
        "NVDA": "NVIDIA Corp.",
        "SPY": "SPDR S&P 500 ETF Trust",
    }

    def __init__(self, *, delayed: bool = False, now: datetime | None = None) -> None:
        self.delayed = delayed
        self.now = now

    def _now(self) -> datetime:
        return self.now or datetime.now(UTC)

    def _provenance(self) -> DataProvenance:
        delay = 15 if self.delayed else None
        timestamp = self._now() - timedelta(minutes=delay or 0)
        return DataProvenance(self.name, timestamp, self.delayed, delay)

    def get_quote(self, symbol: str) -> Quote:
        batch = self.get_candles(symbol, "1h", limit=220)
        return Quote(symbol.upper(), float(batch.frame["close"].iloc[-1]), "USD", batch.provenance)

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 300,
    ) -> CandleBatch:
        symbol = symbol.upper()
        limit = max(20, min(limit, 5000))
        minutes = {"15m": 15, "1h": 60, "4h": 240, "1d": 1440}.get(timeframe)
        if minutes is None:
            raise ValueError(f"Unsupported sample timeframe: {timeframe}")
        seed = int(hashlib.sha256(symbol.encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        end_time = end or self._provenance().timestamp
        index = pd.date_range(end=end_time, periods=limit, freq=f"{minutes}min", tz="UTC")
        base = 25 + seed % 175
        trend = np.linspace(0, base * 0.25, limit)
        noise = rng.normal(0, base * 0.006, limit).cumsum()
        close = np.maximum(base + trend + noise, 1.0)
        open_values = np.r_[close[0], close[:-1]]
        spread = np.maximum(np.abs(rng.normal(base * 0.005, base * 0.002, limit)), 0.01)
        volume = rng.integers(500_000, 3_000_000, limit).astype(float)
        frame = pd.DataFrame(
            {
                "open": open_values,
                "high": np.maximum(open_values, close) + spread,
                "low": np.minimum(open_values, close) - spread,
                "close": close,
                "volume": volume,
            },
            index=index,
        )
        return CandleBatch(symbol, timeframe, frame, self._provenance())

    def get_symbol_info(self, symbol: str) -> SymbolInfo:
        symbol = symbol.upper()
        return SymbolInfo(
            symbol,
            self._symbols.get(symbol, symbol),
            "ETF" if symbol == "SPY" else "STOCK",
            "USD",
            "SAMPLE",
            True,
        )

    def search_symbols(self, query: str) -> list[SymbolInfo]:
        query = query.casefold()
        return [
            self.get_symbol_info(symbol)
            for symbol, name in self._symbols.items()
            if query in symbol.casefold() or query in name.casefold()
        ]

    def get_market_status(self) -> MarketStatus:
        now = self._now()
        return MarketStatus("SAMPLE", "SIMULATION", now)
