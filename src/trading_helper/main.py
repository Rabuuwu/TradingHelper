from __future__ import annotations

from trading_helper.config import load_settings


def main() -> None:
    settings = load_settings()

    mode = "PAPER" if settings.paper_trading else "LIVE"
    print("TradingHelper 0.1.0")
    print(f"IBKR mode: {mode}")
    print(f"IBKR endpoint: {settings.ibkr_host}:{settings.ibkr_port}")
    print("Automatic order execution: DISABLED")


if __name__ == "__main__":
    main()
