from __future__ import annotations

import os
from unittest.mock import patch

from trading_helper.desktop_app import prepare_user_data, user_data_dir


def test_desktop_first_run_seeds_config_and_keeps_it_private(tmp_path):
    resources = tmp_path / "resources"
    (resources / "config").mkdir(parents=True)
    (resources / "config" / "settings.example.yaml").write_text("app: {}\n")
    (resources / ".env.example").write_text("MARKET_DATA_PROVIDER=sample\n")
    data = tmp_path / "Application Support" / "TradingHelper"

    prepare_user_data(data, resources)

    assert (data / "config" / "settings.yaml").read_text() == "app: {}\n"
    env_file = data / ".env"
    assert env_file.read_text() == "MARKET_DATA_PROVIDER=sample\n"
    if os.name == "posix":
        assert os.stat(env_file).st_mode & 0o777 == 0o600


def test_windows_user_data_uses_roaming_appdata(tmp_path):
    data_dir = user_data_dir("win32", {"APPDATA": str(tmp_path / "Roaming")})

    assert data_dir == tmp_path / "Roaming" / "TradingHelper"


def test_windows_user_data_has_home_fallback(tmp_path):
    with patch("trading_helper.desktop_app.Path.home", return_value=tmp_path):
        data_dir = user_data_dir("win32", {})

    assert data_dir == tmp_path / "AppData" / "Roaming" / "TradingHelper"


def test_desktop_first_run_never_overwrites_user_configuration(tmp_path):
    resources = tmp_path / "resources"
    (resources / "config").mkdir(parents=True)
    (resources / "config" / "settings.example.yaml").write_text("app: {}\n")
    (resources / ".env.example").write_text("MARKET_DATA_PROVIDER=sample\n")
    data = tmp_path / "Application Support" / "TradingHelper"
    config_dir = data / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "settings.yaml").write_text("app:\n  language: en\n")
    (data / ".env").write_text("MARKET_DATA_PROVIDER=twelve_data\n")

    prepare_user_data(data, resources)

    assert (config_dir / "settings.yaml").read_text() == "app:\n  language: en\n"
    assert (data / ".env").read_text() == "MARKET_DATA_PROVIDER=twelve_data\n"


def test_desktop_first_run_uses_packaged_defaults_when_project_files_are_absent(tmp_path):
    resources = tmp_path / "empty-resources"
    resources.mkdir()
    data = tmp_path / "Application Support" / "TradingHelper"

    prepare_user_data(data, resources)

    assert (data / "config" / "settings.yaml").is_file()
    assert (data / ".env").is_file()
