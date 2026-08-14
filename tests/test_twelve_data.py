
import pytest

from trading_helper.market_data.provider import ProviderError, ProviderRateLimited
from trading_helper.market_data.twelve_data import TwelveDataProvider


class Response:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("http error")

    def json(self):
        return self.payload


class Session:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.responses.pop(0)


def test_twelve_data_candles_populate_quote_and_info_cache():
    session = Session(
        [
            Response(
                {
                    "meta": {
                        "symbol": "NVDA",
                        "currency": "USD",
                        "exchange": "NASDAQ",
                        "type": "Common Stock",
                    },
                    "values": [
                        {
                            "datetime": "2026-08-13 14:00:00",
                            "open": "180",
                            "high": "185",
                            "low": "179",
                            "close": "184",
                            "volume": "1000",
                        },
                        {
                            "datetime": "2026-08-13 15:00:00",
                            "open": "184",
                            "high": "187",
                            "low": "183",
                            "close": "186",
                            "volume": "1200",
                        },
                    ],
                }
            )
        ]
    )
    provider = TwelveDataProvider("secret", session=session, requests_per_minute=1_000_000)
    batch = provider.get_candles("nvda", "1h", limit=2)
    assert list(batch.frame["close"]) == [184, 186]
    assert provider.get_quote("NVDA").price == 186
    assert provider.get_symbol_info("NVDA").exchange == "NASDAQ"
    assert len(session.calls) == 1
    assert session.calls[0][1]["headers"]["Authorization"] == "apikey secret"
    assert "secret" not in session.calls[0][0]


def test_twelve_data_explicit_delay_and_rate_limit():
    session = Session([Response({}, status_code=429)])
    provider = TwelveDataProvider(
        "secret", session=session, delay_minutes=15, requests_per_minute=1_000_000
    )
    with pytest.raises(ProviderRateLimited):
        provider.get_quote("AAPL")


def test_twelve_data_requires_key():
    with pytest.raises(ProviderError):
        TwelveDataProvider("  ")


def test_twelve_data_market_status_accepts_top_level_list():
    session = Session([Response([{"name": "NASDAQ", "is_market_open": True}])])
    provider = TwelveDataProvider("secret", session=session, requests_per_minute=1_000_000)
    assert provider.get_market_status().status in {"OPEN", "CLOSED"}
    assert session.calls == []
