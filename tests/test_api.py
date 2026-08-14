from fastapi import Response

from trading_helper.api import (
    PublicSettingsUpdate,
    WatchlistInput,
    _decode_signal,
    add_watchlist,
    dashboard,
    delete_watchlist,
    health,
    public_settings,
    ready,
    status,
    update_public_settings,
    watchlist,
)


def test_health() -> None:
    assert health()["status"] == "ok"


def test_core_api_handlers_work_without_broker(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRADING_HELPER_DB", str(tmp_path / "api.db"))
    monkeypatch.setenv("SETTINGS_FILE", "config/settings.example.yaml")

    assert ready(Response())["status"] == "ready"
    assert status()["server"] == "ONLINE"
    assert public_settings()["provider"] == "sample"
    assert "PLN" in public_settings()["supported_currencies"]
    assert str(dashboard().path).endswith("index.html")


def test_signal_values_are_converted_to_selected_display_currency(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRADING_HELPER_DB", str(tmp_path / "api.db"))
    monkeypatch.setenv("SETTINGS_FILE", "config/settings.example.yaml")
    update_public_settings(PublicSettingsUpdate(display_currency="PLN"))
    row = {
        "price": 100.0,
        "entry_low": 99.0,
        "reasons_json": "[]",
        "warnings_json": "[]",
        "breakdown_json": "{}",
        "details_json": '{"currency":"USD"}',
    }
    decoded = _decode_signal(row)
    assert decoded["instrument_currency"] == "USD"
    assert decoded["display_currency"] == "PLN"
    assert decoded["display_values"]["price"] == 400.0
    assert decoded["fx_rate_source"] == "CONFIGURED_NOT_LIVE"


def test_watchlist_can_be_added_and_removed(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRADING_HELPER_DB", str(tmp_path / "api.db"))
    monkeypatch.setenv("SETTINGS_FILE", "config/settings.example.yaml")
    add_watchlist(WatchlistInput(symbol="nvda", notes="wybicie"))
    assert [(item["symbol"], item["notes"]) for item in watchlist()] == [("NVDA", "wybicie")]
    delete_watchlist("nvda")
    assert watchlist() == []
