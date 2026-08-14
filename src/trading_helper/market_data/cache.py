from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd

from trading_helper.database import Repository
from trading_helper.market_data.models import CandleBatch, DataProvenance, Quote
from trading_helper.market_data.provider import MarketDataProvider
from trading_helper.market_data.resilience import RateLimiter, with_retry


class CachedMarketData:
    def __init__(
        self, provider: MarketDataProvider, repository: Repository, ttl_seconds: int = 300
    ) -> None:
        self.provider = provider
        self.repository = repository
        self.ttl = timedelta(seconds=ttl_seconds)
        self.rate_limiter = RateLimiter()

    def get_quote(self, symbol: str, *, force: bool = False) -> Quote:
        cached = self.repository.latest_quote(symbol)
        if cached and not force:
            fetched = datetime.fromisoformat(cached["fetched_at"])
            if datetime.now(UTC) - fetched <= self.ttl:
                provenance = DataProvenance(
                    cached["data_source"],
                    datetime.fromisoformat(cached["timestamp"]),
                    bool(cached["is_delayed"]),
                    cached["delay_minutes"],
                )
                return Quote(cached["symbol"], cached["price"], cached["currency"], provenance)
        self.rate_limiter.wait()
        quote = with_retry(lambda: self.provider.get_quote(symbol))
        self.repository.save_quote(quote)
        return quote

    def get_candles(
        self, symbol: str, timeframe: str, limit: int = 300, *, force: bool = False
    ) -> CandleBatch:
        cached = self.repository.cached_candles(symbol, timeframe, limit)
        if len(cached) >= limit and not force:
            fetched = datetime.fromisoformat(cached[-1]["fetched_at"])
            if datetime.now(UTC) - fetched <= self.ttl:
                frame = pd.DataFrame(cached).set_index("timestamp")
                frame = frame[["open", "high", "low", "close", "volume"]]
                provenance = DataProvenance(
                    cached[-1]["data_source"],
                    datetime.fromisoformat(cached[-1]["timestamp"]),
                    bool(cached[-1]["is_delayed"]),
                    cached[-1]["delay_minutes"],
                )
                return CandleBatch(symbol.upper(), timeframe, frame, provenance)
        self.rate_limiter.wait()
        batch = with_retry(lambda: self.provider.get_candles(symbol, timeframe, limit=limit))
        self.repository.save_candles(
            batch.symbol,
            batch.timeframe,
            batch.frame,
            batch.provenance.source,
            batch.provenance.is_delayed,
            batch.provenance.delay_minutes,
        )
        return batch
