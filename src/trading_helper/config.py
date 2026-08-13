from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    ibkr_host: str
    ibkr_port: int
    ibkr_client_id: int
    paper_trading: bool
    database_path: str
    ntfy_enabled: bool
    ntfy_server: str
    ntfy_topic: str


def load_settings() -> Settings:
    load_dotenv()

    return Settings(
        ibkr_host=os.getenv("IBKR_HOST", "127.0.0.1"),
        ibkr_port=int(os.getenv("IBKR_PORT", "7497")),
        ibkr_client_id=int(os.getenv("IBKR_CLIENT_ID", "1")),
        paper_trading=os.getenv("IBKR_PAPER_TRADING", "true").lower() == "true",
        database_path=os.getenv("TRADING_HELPER_DB", "data/trading_helper.db"),
        ntfy_enabled=os.getenv("NTFY_ENABLED", "false").lower() == "true",
        ntfy_server=os.getenv("NTFY_SERVER", "https://ntfy.sh"),
        ntfy_topic=os.getenv("NTFY_TOPIC", ""),
    )
