from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass(frozen=True)
class DataProvenance:
    source: str
    timestamp: datetime
    is_delayed: bool = False
    delay_minutes: int | None = None


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: float
    currency: str
    provenance: DataProvenance


@dataclass(frozen=True)
class SymbolInfo:
    symbol: str
    name: str
    asset_type: str
    currency: str
    exchange: str = ""
    fractional_supported: bool = True


@dataclass(frozen=True)
class MarketStatus:
    market: str
    status: str
    as_of: datetime


@dataclass(frozen=True)
class CandleBatch:
    symbol: str
    timeframe: str
    frame: pd.DataFrame
    provenance: DataProvenance
