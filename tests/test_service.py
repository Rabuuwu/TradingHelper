from trading_helper.config import Settings, StrategySettings
from trading_helper.database import Repository
from trading_helper.market_data.sample import SampleMarketDataProvider
from trading_helper.service import TradingHelperService


def make_settings(database_path: str) -> Settings:
    return Settings(
        app_host="127.0.0.1",
        app_port=8787,
        database_path=database_path,
        settings_file="unused",
        market_data_provider="sample",
        provider_api_key="",
        ntfy_enabled=False,
        ntfy_server="https://ntfy.sh",
        ntfy_topic="",
        auth_enabled=False,
        auth_username="",
        auth_password_hash="",
        session_secret="",
    )


def test_scan_pipeline_persists_market_data_and_signals(tmp_path) -> None:
    settings = make_settings(str(tmp_path / "db.sqlite"))
    strategy = StrategySettings.from_mapping({"universe": {"symbols": ["AAPL"]}})
    service = TradingHelperService(
        settings,
        strategy,
        SampleMarketDataProvider(),
        {"costs": {"profiles": {"custom": {}}}},
    )
    summary = service.scan_once()
    repository = Repository(settings.database_path)
    assert summary["succeeded"] == 1
    assert repository.rows("SELECT symbol FROM signals") == [{"symbol": "AAPL"}]
    assert repository.rows("SELECT COUNT(*) count FROM candles")[0]["count"] >= 300
    signal = repository.rows("SELECT recommended_quantity,data_source FROM signals")[0]
    assert signal["recommended_quantity"] > 0
    assert signal["data_source"] == "sample"
