from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    app_host: str
    app_port: int
    database_path: str
    settings_file: str
    ibkr_host: str
    ibkr_port: int
    ibkr_client_id: int
    paper_trading: bool
    ibkr_read_only: bool
    ntfy_enabled: bool
    ntfy_server: str
    ntfy_topic: str


def _as_bool(value: str, default: bool) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        app_host=os.getenv("APP_HOST", "127.0.0.1"),
        app_port=int(os.getenv("APP_PORT", "8787")),
        database_path=os.getenv("TRADING_HELPER_DB", "data/trading_helper.db"),
        settings_file=os.getenv("SETTINGS_FILE", "config/settings.yaml"),
        ibkr_host=os.getenv("IBKR_HOST", "127.0.0.1"),
        ibkr_port=int(os.getenv("IBKR_PORT", "4002")),
        ibkr_client_id=int(os.getenv("IBKR_CLIENT_ID", "17")),
        paper_trading=_as_bool(os.getenv("IBKR_PAPER_TRADING", "true"), True),
        ibkr_read_only=_as_bool(os.getenv("IBKR_READ_ONLY", "true"), True),
        ntfy_enabled=_as_bool(os.getenv("NTFY_ENABLED", "false"), False),
        ntfy_server=os.getenv("NTFY_SERVER", "https://ntfy.sh").rstrip("/"),
        ntfy_topic=os.getenv("NTFY_TOPIC", ""),
    )


def load_strategy_config(path: str | None = None) -> dict[str, Any]:
    settings = load_settings()
    target = Path(path or settings.settings_file)
    if not target.exists():
        example = Path("config/settings.example.yaml")
        if example.exists():
            target = example
        else:
            raise FileNotFoundError(f"Missing settings file: {target}")
    with target.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("Root YAML configuration must be a mapping")
    return data
