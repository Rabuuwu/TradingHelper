from __future__ import annotations

import argparse
import getpass
import ipaddress
import json
import os
import tempfile
import threading
from pathlib import Path

import uvicorn

from trading_helper import __version__
from trading_helper.api import configure_service
from trading_helper.auth import hash_password
from trading_helper.backup import backup_database
from trading_helper.config import load_settings, load_strategy_config, load_strategy_settings
from trading_helper.database import Repository, init_database
from trading_helper.logging_config import configure_logging
from trading_helper.service import TradingHelperService
from trading_helper.soak import run_accelerated_paper_soak


def build_service() -> TradingHelperService:
    return TradingHelperService(
        load_settings(), load_strategy_settings(), raw_config=load_strategy_config()
    )


def ensure_safe_bind(host: str, auth_enabled: bool) -> None:
    if host == "localhost":
        return
    try:
        local_only = ipaddress.ip_address(host).is_loopback
    except ValueError:
        local_only = False
    if not local_only and not auth_enabled:
        raise RuntimeError(
            "Refusing non-loopback bind while AUTH_ENABLED is false. "
            "Enable authentication for Tailscale or remote access."
        )


def self_check() -> int:
    settings = load_settings()
    strategy = load_strategy_settings()
    service = build_service()
    print(f"TradingHelper {__version__}")
    print("Architecture: BROKER-INDEPENDENT")
    print(f"Market data provider: {service.provider.name}")
    print(f"Universe: {', '.join(strategy.symbols)}")
    print(f"Database: {settings.database_path}")
    print(f"Authentication: {'ENABLED' if settings.auth_enabled else 'DISABLED'}")
    print("Automatic order execution: NOT IMPLEMENTED")
    for warning in service.self_check():
        print(f"WARNING: {warning}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="trading-helper")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("self-check", "init-db", "api", "run", "scan-once", "worker", "backup"):
        sub.add_parser(name)
    soak_parser = sub.add_parser("paper-soak")
    soak_parser.add_argument("--cycles", type=int, default=1000)
    password_parser = sub.add_parser("hash-password")
    password_parser.add_argument("password", nargs="?")
    args = parser.parse_args()
    settings = load_settings()
    configure_logging(os.getenv("LOG_LEVEL", "INFO"))

    if args.command == "self-check":
        raise SystemExit(self_check())
    if args.command == "init-db":
        init_database(settings.database_path)
        print(f"Database initialized: {Path(settings.database_path)}")
        return
    if args.command == "hash-password":
        password = args.password
        if password is None:
            password = getpass.getpass("Password: ")
            confirmation = getpass.getpass("Repeat password: ")
            if password != confirmation:
                raise SystemExit("Passwords do not match")
        print(hash_password(password))
        return
    if args.command == "backup":
        config = load_strategy_config().get("backup", {})
        target = backup_database(
            settings.database_path,
            config.get("directory", "data/backups"),
            int(config.get("retention_days", 14)),
        )
        print(f"Backup created: {target}")
        return
    if args.command == "paper-soak":
        with tempfile.TemporaryDirectory(prefix="trading-helper-soak-") as directory:
            report = run_accelerated_paper_soak(
                Repository(str(Path(directory) / "soak.sqlite")), args.cycles
            )
        print(json.dumps(report, indent=2))
        if report["status"] != "PASSED":
            raise SystemExit(1)
        return
    if args.command == "api":
        ensure_safe_bind(settings.app_host, settings.auth_enabled)
        uvicorn.run("trading_helper.api:app", host=settings.app_host, port=settings.app_port)
        return

    service = build_service()
    if args.command == "scan-once":
        summary = service.scan_once()
        print(f"Scan {summary['run_id']}: ok={summary['succeeded']}, failed={summary['failed']}")
        return
    if args.command == "worker":
        service.run_forever()
        return
    configure_service(service)
    ensure_safe_bind(settings.app_host, settings.auth_enabled)
    api_thread = threading.Thread(
        target=uvicorn.run,
        kwargs={
            "app": "trading_helper.api:app",
            "host": settings.app_host,
            "port": settings.app_port,
            "reload": False,
        },
        name="web-api",
        daemon=True,
    )
    api_thread.start()
    service.run_forever()


if __name__ == "__main__":
    main()
