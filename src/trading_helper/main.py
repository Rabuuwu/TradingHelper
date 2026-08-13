from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import uvicorn

from trading_helper import __version__
from trading_helper.config import load_settings, load_strategy_config
from trading_helper.database import init_database


def self_check() -> int:
    settings = load_settings()
    strategy = load_strategy_config()
    ibapi_installed = importlib.util.find_spec("ibapi") is not None
    print(f"TradingHelper {__version__}")
    print(f"Paper trading: {settings.paper_trading}")
    print(f"IBKR read-only expected: {settings.ibkr_read_only}")
    print(f"IBKR endpoint: {settings.ibkr_host}:{settings.ibkr_port}")
    print(f"Official ibapi installed: {ibapi_installed}")
    print(f"Strategy sections: {', '.join(sorted(strategy.keys()))}")
    print(f"Database: {settings.database_path}")
    print("Automatic order execution: DISABLED")
    if not settings.paper_trading or not settings.ibkr_read_only:
        return 2
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="trading-helper")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("self-check")
    sub.add_parser("init-db")
    sub.add_parser("api")
    args = parser.parse_args()
    settings = load_settings()
    if args.command == "self-check":
        raise SystemExit(self_check())
    if args.command == "init-db":
        init_database(settings.database_path)
        print(f"Database initialized: {Path(settings.database_path)}")
        return
    if args.command == "api":
        uvicorn.run("trading_helper.api:app", host=settings.app_host, port=settings.app_port, reload=False)


if __name__ == "__main__":
    main()
