from trading_helper.config import Settings
from trading_helper.database import Repository
from trading_helper.market_data.credits import ApiCreditBudget
from trading_helper.market_data.provider import MarketDataProvider, ProviderError
from trading_helper.market_data.sample import SampleMarketDataProvider
from trading_helper.market_data.twelve_data import TwelveDataProvider


def create_provider(
    settings: Settings, repository: Repository | None = None
) -> MarketDataProvider:
    if settings.market_data_provider == "sample":
        return SampleMarketDataProvider()
    if settings.market_data_provider == "twelve_data":
        budget = (
            ApiCreditBudget(
                repository,
                "twelve_data",
                settings.provider_daily_credit_limit,
                settings.provider_credit_reserve,
            )
            if repository
            else None
        )
        if budget:
            budget.bootstrap_from_scan_history()
        return TwelveDataProvider(
            settings.provider_api_key,
            delay_minutes=settings.provider_delay_minutes,
            requests_per_minute=settings.provider_requests_per_minute,
            credit_budget=budget,
        )
    raise ProviderError(
        f"Unknown market data provider '{settings.market_data_provider}'. "
        "Use 'sample' or 'twelve_data'."
    )
