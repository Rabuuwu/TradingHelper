from __future__ import annotations

from fastapi import FastAPI

from trading_helper import __version__
from trading_helper.config import load_settings
from trading_helper.ibkr.client import ibapi_available

app = FastAPI(title="TradingHelper", version=__version__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/status")
def status() -> dict[str, object]:
    settings = load_settings()
    return {
        "version": __version__,
        "mode": "paper" if settings.paper_trading else "live",
        "read_only": settings.ibkr_read_only,
        "ibapi_installed": ibapi_available(),
        "ibkr_endpoint": f"{settings.ibkr_host}:{settings.ibkr_port}",
        "automatic_order_execution": False,
    }
