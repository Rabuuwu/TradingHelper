from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from trading_helper.market_data.models import CandleBatch, MarketStatus, Quote, SymbolInfo


class ProviderError(RuntimeError):
    """Base error safe to expose as provider state without leaking credentials."""


class ProviderTimeout(ProviderError):
    pass


class ProviderRateLimited(ProviderError):
    pass


class MarketDataProvider(ABC):
    name: str

    @abstractmethod
    def get_quote(self, symbol: str) -> Quote: ...

    @abstractmethod
    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 300,
    ) -> CandleBatch: ...

    @abstractmethod
    def get_symbol_info(self, symbol: str) -> SymbolInfo: ...

    @abstractmethod
    def search_symbols(self, query: str) -> list[SymbolInfo]: ...

    @abstractmethod
    def get_market_status(self) -> MarketStatus: ...

    def get_bulk_quotes(self, symbols: list[str]) -> list[Quote]:
        return [self.get_quote(symbol) for symbol in symbols]
