from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any

from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from trading_helper import __version__
from trading_helper.auth import AuthManager
from trading_helper.config import load_settings, load_strategy_config, load_strategy_settings
from trading_helper.database import Repository, utc_now
from trading_helper.journal import TradeJournal
from trading_helper.portfolio import ManualPortfolioService, PositionInput
from trading_helper.service import TradingHelperService

app = FastAPI(title="TradingHelper", version=__version__)
STATIC_DIR = Path(__file__).parent / "web"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

_settings = load_settings()
_auth = AuthManager(_settings)
_service: TradingHelperService | None = None
_started_at = datetime.now(UTC)


def configure_service(service: TradingHelperService) -> None:
    global _service
    _service = service


def service() -> TradingHelperService:
    global _service
    if _service is None:
        _service = TradingHelperService(load_settings(), load_strategy_settings())
    return _service


def repository() -> Repository:
    return Repository(load_settings().database_path)


def require_auth(session: Annotated[str | None, Cookie(alias="th_session")] = None) -> None:
    if not _auth.valid(session):
        raise HTTPException(status_code=401, detail="Authentication required")


class LoginInput(BaseModel):
    username: str
    password: str


class WatchlistInput(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    notes: str = Field(default="", max_length=500)


class PositionCreate(BaseModel):
    symbol: str
    broker: str = "MANUAL"
    entry_price: float = Field(gt=0)
    quantity: float = Field(gt=0)
    currency: str = "USD"
    entry_date: str
    stop_price: float | None = None
    target_price: float | None = None
    target_price_2: float | None = None
    notes: str = ""
    mode: str = "MANUAL"


class PositionUpdate(BaseModel):
    broker: str | None = None
    quantity: float | None = Field(default=None, gt=0)
    stop_price: float | None = None
    target_price: float | None = None
    target_price_2: float | None = None
    notes: str | None = None


class TradeUpdate(BaseModel):
    status: str | None = None
    exit_date: str | None = None
    exit_price: float | None = None
    fees: float | None = None
    strategy: str | None = None
    signal_score_at_entry: int | None = Field(default=None, ge=0, le=100)
    notes: str | None = None


class PublicSettingsUpdate(BaseModel):
    scanner_enabled: bool | None = None
    scan_interval_seconds: int | None = Field(default=None, ge=60)
    risk_percent: float | None = Field(default=None, gt=0, le=10)
    portfolio_value: float | None = Field(default=None, gt=0)
    notification_enabled: bool | None = None
    cost_profile: str | None = None
    display_currency: str | None = Field(default=None, min_length=3, max_length=3)
    language: str | None = Field(default=None, min_length=2, max_length=2)


def _decode_signal(row: dict[str, Any]) -> dict[str, Any]:
    for source, target in (
        ("reasons_json", "reasons"),
        ("warnings_json", "warnings"),
        ("breakdown_json", "breakdown"),
        ("details_json", "details"),
    ):
        try:
            row[target] = json.loads(row.pop(source, "null"))
        except json.JSONDecodeError:
            row[target] = None
    strategy = load_strategy_settings()
    details = row.get("details") or {}
    instrument_currency = str(details.get("currency", strategy.portfolio_currency)).upper()
    display_currency = _runtime_public_setting("display_currency", strategy.portfolio_currency)
    display_currency = str(display_currency).upper()
    rates = strategy.fx_rates_to_portfolio
    instrument_rate = rates.get(instrument_currency)
    display_rate = rates.get(display_currency)
    row["instrument_currency"] = instrument_currency
    row["display_currency"] = display_currency
    row["fx_rate_source"] = "CONFIGURED_NOT_LIVE"
    if instrument_rate and display_rate:
        conversion = instrument_rate / display_rate
        monetary_fields = (
            "price",
            "entry_low",
            "entry_high",
            "stop_price",
            "target_price",
            "target_price_2",
            "estimated_total_cost",
            "expected_net_profit",
        )
        row["display_values"] = {
            field: round(float(row[field]) * conversion, 4)
            for field in monetary_fields
            if row.get(field) is not None
        }
        row["display_fx_rate"] = round(conversion, 6)
    else:
        row["display_values"] = None
        row.setdefault("warnings", []).append(
            f"Missing configured FX rate for {instrument_currency} or {display_currency}"
        )
    return row


def _runtime_public_setting(key: str, default: Any) -> Any:
    rows = repository().rows("SELECT value FROM app_settings WHERE key=?", (key,))
    if not rows:
        return default
    try:
        return json.loads(rows[0]["value"])
    except (TypeError, json.JSONDecodeError):
        return default


@app.get("/")
def dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/ready")
def ready(response: Response) -> dict[str, Any]:
    repo = repository()
    try:
        repo.rows("SELECT 1")
    except Exception as exc:
        response.status_code = 503
        return {"status": "unhealthy", "database": str(exc)}
    watchdog = repo.rows("SELECT value FROM system_state WHERE key='watchdog'")
    watchdog_state = watchdog[0]["value"] if watchdog else "STARTING"
    degraded = watchdog_state == "DEGRADED"
    if degraded:
        response.status_code = 503
    return {
        "status": "degraded" if degraded else "ready",
        "database": "ok",
        "provider": service().provider.name,
        "watchdog": watchdog_state,
    }


@app.post("/auth/login")
def login(data: LoginInput, response: Response, request: Request) -> dict[str, str]:
    token = _auth.login(data.username, data.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    response.set_cookie(
        "th_session",
        token,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
        max_age=86400,
    )
    return {"status": "ok"}


@app.post("/auth/logout", dependencies=[Depends(require_auth)])
def logout(
    response: Response, session: Annotated[str | None, Cookie(alias="th_session")] = None
) -> dict[str, str]:
    _auth.logout(session)
    response.delete_cookie("th_session")
    return {"status": "ok"}


@app.get("/status", dependencies=[Depends(require_auth)])
def status() -> dict[str, Any]:
    repo = repository()
    state = repo.rows("SELECT key,value,updated_at FROM system_state ORDER BY key")
    state_map = {item["key"]: item["value"] for item in state}
    market = service().provider.get_market_status()
    quote_state = repo.rows(
        "SELECT is_delayed,delay_minutes,timestamp FROM quotes ORDER BY fetched_at DESC LIMIT 1"
    )
    data_status = "NO_DATA"
    if quote_state:
        data_status = "DELAYED" if quote_state[0]["is_delayed"] else "CURRENT"
        timestamp = datetime.fromisoformat(quote_state[0]["timestamp"])
        if (datetime.now(UTC) - timestamp).total_seconds() > 3600:
            data_status = "STALE"
    return {
        "version": __version__,
        "server": "ONLINE",
        "uptime_seconds": int((datetime.now(UTC) - _started_at).total_seconds()),
        "market": market.status,
        "data_status": data_status,
        "provider": service().provider.name,
        "database": "OK",
        "scheduler": next(
            (item["value"] for item in state if item["key"] == "scheduler"), "NOT_STARTED"
        ),
        "state": state,
        "last_market_data_update": state_map.get("last_market_data_update"),
        "last_successful_scan": state_map.get("last_successful_scan"),
        "last_position_monitor": state_map.get("last_position_monitor"),
        "last_notification": state_map.get("last_notification"),
        "automatic_order_execution": False,
    }


@app.get("/signals", dependencies=[Depends(require_auth)])
def signals(limit: int = 100, min_score: int = 0) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 500))
    rows = repository().rows(
        "SELECT * FROM signals WHERE score>=? ORDER BY id DESC LIMIT ?", (min_score, limit)
    )
    return [_decode_signal(row) for row in rows]


@app.get("/signals/{symbol}", dependencies=[Depends(require_auth)])
def signal_details(symbol: str) -> dict[str, Any]:
    rows = repository().rows(
        "SELECT * FROM signals WHERE symbol=? ORDER BY id DESC LIMIT 1", (symbol.upper(),)
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Signal not found")
    return _decode_signal(rows[0])


@app.get("/watchlist", dependencies=[Depends(require_auth)])
def watchlist() -> list[dict[str, Any]]:
    return repository().rows("SELECT * FROM watchlist ORDER BY symbol")


@app.post("/watchlist", dependencies=[Depends(require_auth)], status_code=201)
def add_watchlist(data: WatchlistInput) -> dict[str, str]:
    repo = repository()
    symbol = data.symbol.upper()
    info = service().provider.get_symbol_info(symbol)
    repo.upsert_symbol(
        symbol, info.name, info.asset_type, info.currency, info.exchange, service().provider.name
    )
    repo.execute(
        "INSERT OR REPLACE INTO watchlist(symbol,notes,created_at) VALUES(?,?,?)",
        (symbol, data.notes, utc_now()),
    )
    return {"symbol": symbol}


@app.delete("/watchlist/{symbol}", dependencies=[Depends(require_auth)], status_code=204)
def delete_watchlist(symbol: str) -> None:
    repository().execute("DELETE FROM watchlist WHERE symbol=?", (symbol.upper(),))


@app.get("/portfolio", dependencies=[Depends(require_auth)])
def portfolio(monitor: bool = False) -> list[dict[str, Any]]:
    rows = service().monitor_positions() if monitor else ManualPortfolioService(repository()).list()
    strategy = load_strategy_settings()
    display_currency = str(
        _runtime_public_setting("display_currency", strategy.portfolio_currency)
    ).upper()
    display_rate = strategy.fx_rates_to_portfolio.get(display_currency)
    for row in rows:
        source_currency = str(row["currency"]).upper()
        source_rate = strategy.fx_rates_to_portfolio.get(source_currency)
        row["display_currency"] = display_currency
        row["fx_rate_source"] = "CONFIGURED_NOT_LIVE"
        if source_rate and display_rate:
            conversion = source_rate / display_rate
            row["display_entry_value"] = round(row["entry_price"] * row["quantity"] * conversion, 4)
            row["display_pnl"] = (
                round(row["pnl"] * conversion, 4) if row.get("pnl") is not None else None
            )
    return rows


@app.post("/portfolio", dependencies=[Depends(require_auth)], status_code=201)
def add_position(data: PositionCreate) -> dict[str, int]:
    payload = PositionInput(**data.model_dump())
    manager = ManualPortfolioService(repository())
    position_id = manager.simulate(payload) if data.mode == "PAPER" else manager.add(payload)
    return {"id": position_id}


@app.put("/portfolio/{position_id}", dependencies=[Depends(require_auth)])
def update_position(position_id: int, data: PositionUpdate) -> dict[str, str]:
    ManualPortfolioService(repository()).update(position_id, data.model_dump(exclude_none=True))
    return {"status": "updated"}


@app.delete("/portfolio/{position_id}", dependencies=[Depends(require_auth)], status_code=204)
def delete_position(position_id: int) -> None:
    ManualPortfolioService(repository()).delete(position_id)


@app.get("/trades", dependencies=[Depends(require_auth)])
def trades() -> dict[str, Any]:
    journal = TradeJournal(repository())
    return {"items": journal.list(), "statistics": journal.statistics()}


@app.post("/trades", dependencies=[Depends(require_auth)], status_code=201)
def create_trade(data: PositionCreate) -> dict[str, int]:
    return add_position(data)


@app.put("/trades/{trade_id}", dependencies=[Depends(require_auth)])
def update_trade(trade_id: int, data: TradeUpdate) -> dict[str, str]:
    TradeJournal(repository()).update(trade_id, data.model_dump(exclude_none=True))
    return {"status": "updated"}


@app.get("/scanner/status", dependencies=[Depends(require_auth)])
def scanner_status() -> list[dict[str, Any]]:
    return repository().rows("SELECT * FROM scan_runs ORDER BY id DESC LIMIT 20")


@app.post("/scanner/run", dependencies=[Depends(require_auth)])
def scanner_run() -> dict[str, int]:
    return service().scan_once()


@app.get("/settings/public", dependencies=[Depends(require_auth)])
def public_settings() -> dict[str, Any]:
    strategy = load_strategy_settings()
    config = load_strategy_config()
    overrides = repository().rows("SELECT key,value,updated_at FROM app_settings")
    return {
        "provider": load_settings().market_data_provider,
        "symbols": strategy.symbols,
        "scan_interval_seconds": strategy.scan_interval_seconds,
        "risk_percent": strategy.max_risk_per_trade_percent,
        "portfolio_value": strategy.portfolio_value,
        "portfolio_currency": strategy.portfolio_currency,
        "display_currency": _runtime_public_setting(
            "display_currency", strategy.portfolio_currency
        ),
        "supported_currencies": sorted(strategy.fx_rates_to_portfolio),
        "fx_rate_source": "YAML_CONFIG_NOT_LIVE",
        "language": _runtime_public_setting(
            "language", config.get("app", {}).get("language", "pl")
        ),
        "supported_languages": ["pl", "en"],
        "cost_profile": strategy.cost_profile,
        "auth_enabled": load_settings().auth_enabled,
        "overrides": overrides,
    }


@app.put("/settings/public", dependencies=[Depends(require_auth)])
def update_public_settings(data: PublicSettingsUpdate) -> dict[str, str]:
    repo = repository()
    values = data.model_dump(exclude_none=True)
    if "display_currency" in values:
        currency = values["display_currency"].upper()
        if currency not in load_strategy_settings().fx_rates_to_portfolio:
            raise HTTPException(status_code=422, detail="Unsupported display currency")
        values["display_currency"] = currency
    if "language" in values and values["language"] not in {"pl", "en"}:
        raise HTTPException(status_code=422, detail="Unsupported language")
    for key, value in values.items():
        repo.execute(
            """INSERT INTO app_settings(key,value,updated_at) VALUES(?,?,?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
            (key, json.dumps(value), utc_now()),
        )
    repo.event("settings_updated", "Public runtime settings updated")
    return {"status": "updated"}


@app.get("/events", dependencies=[Depends(require_auth)])
def events(limit: int = 100) -> list[dict[str, Any]]:
    return repository().rows("SELECT * FROM app_events ORDER BY id DESC LIMIT ?", (limit,))


@app.get("/alerts", dependencies=[Depends(require_auth)])
def alerts(limit: int = 100) -> list[dict[str, Any]]:
    return repository().rows("SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,))


@app.get("/events/stream", dependencies=[Depends(require_auth)])
async def event_stream(request: Request, after_id: int = 0) -> StreamingResponse:
    async def generate():
        cursor = after_id
        while not await request.is_disconnected():
            rows = repository().rows(
                "SELECT * FROM app_events WHERE id>? ORDER BY id LIMIT 100", (cursor,)
            )
            for row in rows:
                cursor = row["id"]
                yield f"id: {cursor}\nevent: update\ndata: {json.dumps(row)}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(generate(), media_type="text/event-stream")
