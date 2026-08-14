#!/usr/bin/env python3
"""Run TradingHelper's autonomous strategy exclusively in its isolated PAPER account."""

import argparse
import fcntl
import json
import os
from pathlib import Path

from trading_helper.auto_paper import AutoPaperConfig, AutoPaperTrader
from trading_helper.logging_config import configure_logging
from trading_helper.main import build_service


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous TradingHelper PAPER experiment")
    parser.add_argument("--initial-cash", type=float, required=True)
    parser.add_argument("--interval", type=int, default=300)
    parser.add_argument("--minimum-score", type=int, default=70)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    configure_logging(os.getenv("LOG_LEVEL", "INFO"))
    service = build_service()
    lock_path = Path(f"{service.settings.database_path}.auto-paper.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock = lock_path.open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        raise SystemExit("Another auto PAPER trader is already running") from exc
    trader = AutoPaperTrader(
        service,
        AutoPaperConfig(
            initial_cash=args.initial_cash,
            interval_seconds=args.interval,
            minimum_score=args.minimum_score,
        ),
    )
    if args.status:
        print(json.dumps(trader.status(), indent=2))
    elif args.once:
        print(json.dumps(trader.cycle(), indent=2))
    else:
        trader.run_forever()


if __name__ == "__main__":
    main()
