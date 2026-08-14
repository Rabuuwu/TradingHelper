from trading_helper.config import Settings
from trading_helper.market_data.provider import MarketDataProvider, ProviderError
from trading_helper.market_data.sample import SampleMarketDataProvider
from trading_helper.market_data.twelve_data import TwelveDataProvider


def create_provider(settings: Settings) -> MarketDataProvider:
    if settings.market_data_provider == "sample":
        return SampleMarketDataProvider()
    if settings.market_data_provider == "twelve_data":
        return TwelveDataProvider(
            settings.provider_api_key,
            delay_minutes=settings.provider_delay_minutes,
        )
    raise ProviderError(
        f"Unknown market data provider '{settings.market_data_provider}'. "
        "Use 'sample' or 'twelve_data'."
    )
