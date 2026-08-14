import pytest


@pytest.fixture(autouse=True)
def use_offline_market_data(monkeypatch):
    """Keep the test suite deterministic even when a developer has a real .env."""
    monkeypatch.setenv("MARKET_DATA_PROVIDER", "sample")
    monkeypatch.setenv("MARKET_DATA_API_KEY", "")
