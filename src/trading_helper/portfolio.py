from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from trading_helper.database import Repository, utc_now
from trading_helper.market_data.cache import CachedMarketData
from trading_helper.risk.trailing import atr_trailing_stop
from trading_helper.scanner.indicators import atr


@dataclass(frozen=True)
class PositionInput:
    symbol: str
    broker: str
    entry_price: float
    quantity: float
    currency: str
    entry_date: str
    stop_price: float | None = None
    target_price: float | None = None
    target_price_2: float | None = None
    notes: str = ""
    mode: str = "MANUAL"


class ManualPortfolioService:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def list(self, include_closed: bool = False) -> list[dict[str, Any]]:
        where = "" if include_closed else " WHERE status='OPEN'"
        return self.repository.rows(f"SELECT * FROM manual_positions{where} ORDER BY id DESC")

    def add(self, position: PositionInput) -> int:
        if position.entry_price <= 0 or position.quantity <= 0:
            raise ValueError("entry_price and quantity must be positive")
        if position.stop_price is not None and position.stop_price >= position.entry_price:
            raise ValueError("stop must be below entry for a long position")
        position_id = self.repository.execute(
            """INSERT INTO manual_positions(symbol,broker,mode,entry_price,quantity,currency,
            entry_date,stop_price,target_price,target_price_2,highest_price,notes,updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                position.symbol.upper(),
                position.broker,
                position.mode,
                position.entry_price,
                position.quantity,
                position.currency.upper(),
                position.entry_date,
                position.stop_price,
                position.target_price,
                position.target_price_2,
                position.entry_price,
                position.notes,
                utc_now(),
            ),
        )
        self.repository.execute(
            """INSERT INTO trades(position_id,symbol,broker,status,entry_date,entry_price,
            quantity,currency,notes) VALUES(?,?,?,'OPEN',?,?,?,?,?)""",
            (
                position_id,
                position.symbol.upper(),
                position.broker,
                position.entry_date,
                position.entry_price,
                position.quantity,
                position.currency.upper(),
                position.notes,
            ),
        )
        self.repository.event(
            "position_created",
            f"Position created for {position.symbol.upper()}",
            details={"position_id": position_id, "mode": position.mode},
        )
        return position_id

    def update(self, position_id: int, changes: dict[str, Any]) -> None:
        allowed = {"broker", "quantity", "stop_price", "target_price", "target_price_2", "notes"}
        values = {key: value for key, value in changes.items() if key in allowed}
        if not values:
            raise ValueError("No editable position fields supplied")
        if "quantity" in values and float(values["quantity"]) <= 0:
            raise ValueError("quantity must be positive")
        assignments = ",".join(f"{key}=?" for key in values)
        self.repository.execute(
            f"UPDATE manual_positions SET {assignments},updated_at=? WHERE id=?",
            (*values.values(), utc_now(), position_id),
        )

    def delete(self, position_id: int) -> None:
        self.repository.execute(
            "UPDATE manual_positions SET status='CANCELLED',updated_at=? WHERE id=?",
            (utc_now(), position_id),
        )
        self.repository.execute(
            "UPDATE trades SET status='CANCELLED' WHERE position_id=? AND status='OPEN'",
            (position_id,),
        )

    def close(
        self, position_id: int, exit_price: float, fees: float = 0.0, exit_date: str | None = None
    ) -> None:
        rows = self.repository.rows("SELECT * FROM manual_positions WHERE id=?", (position_id,))
        if not rows or rows[0]["status"] != "OPEN":
            raise ValueError("Open position not found")
        position = rows[0]
        pnl = (exit_price - position["entry_price"]) * position["quantity"] - fees
        pnl_percent = pnl / (position["entry_price"] * position["quantity"]) * 100
        closed_at = exit_date or datetime.now(UTC).isoformat()
        self.repository.execute(
            "UPDATE manual_positions SET status='CLOSED',updated_at=? WHERE id=?",
            (utc_now(), position_id),
        )
        self.repository.execute(
            """UPDATE trades SET status='CLOSED',exit_date=?,exit_price=?,fees=?,pnl=?,
            pnl_percent=? WHERE position_id=? AND status='OPEN'""",
            (closed_at, exit_price, fees, pnl, pnl_percent, position_id),
        )

    def simulate(self, position: PositionInput) -> int:
        return self.add(
            PositionInput(**{**position.__dict__, "broker": "SIMULATION", "mode": "PAPER"})
        )


class PositionMonitor:
    def __init__(
        self, repository: Repository, market_data: CachedMarketData, atr_multiplier: float = 2.5
    ) -> None:
        self.repository = repository
        self.market_data = market_data
        self.atr_multiplier = atr_multiplier

    def run(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for position in ManualPortfolioService(self.repository).list():
            quote = self.market_data.get_quote(position["symbol"])
            candles = self.market_data.get_candles(position["symbol"], "1h", 220)
            atr_value = float(atr(candles.frame).iloc[-1])
            highest = max(position["highest_price"], quote.price)
            trailing = atr_trailing_stop(
                highest, atr_value, self.atr_multiplier, position["trailing_stop"]
            )
            status = "HOLD"
            if quote.price <= trailing:
                status = "TRAILING_STOP_WARNING"
            elif position["stop_price"] and quote.price <= position["stop_price"]:
                status = "EXIT_WARNING"
            elif position["target_price"] and quote.price >= position["target_price"]:
                status = "TAKE_PROFIT"
            elif (quote.price - trailing) / quote.price <= 0.02:
                status = "WATCH_EXIT"
            pnl = (quote.price - position["entry_price"]) * position["quantity"]
            pnl_percent = (quote.price / position["entry_price"] - 1) * 100
            active_stop = max(
                value for value in (position["stop_price"], trailing) if value is not None
            )
            distance_to_stop = (quote.price - active_stop) / quote.price * 100
            distance_to_target = None
            if position["target_price"]:
                distance_to_target = (position["target_price"] - quote.price) / quote.price * 100
            self.repository.execute(
                """UPDATE manual_positions SET highest_price=?,trailing_stop=?,current_price=?,
                pnl=?,pnl_percent=?,distance_to_stop_percent=?,distance_to_target_percent=?,
                monitor_status=?,last_price_at=?,updated_at=? WHERE id=?""",
                (
                    highest,
                    trailing,
                    quote.price,
                    pnl,
                    pnl_percent,
                    distance_to_stop,
                    distance_to_target,
                    status,
                    quote.provenance.timestamp.isoformat(),
                    utc_now(),
                    position["id"],
                ),
            )
            result = {
                **position,
                "current_price": quote.price,
                "pnl": round(pnl, 4),
                "pnl_percent": round(pnl_percent, 2),
                "atr": atr_value,
                "trailing_stop": trailing,
                "monitor_status": status,
                "distance_to_stop_percent": round(distance_to_stop, 2),
                "distance_to_target_percent": (
                    round(distance_to_target, 2) if distance_to_target is not None else None
                ),
                "data_timestamp": quote.provenance.timestamp.isoformat(),
                "is_delayed": quote.provenance.is_delayed,
            }
            results.append(result)
            self.repository.event(
                "position_updated",
                f"{position['symbol']}: {status}",
                details={
                    "position_id": position["id"],
                    "pnl": round(pnl, 4),
                    "current_price": quote.price,
                },
            )
            if status != "HOLD":
                self.repository.event(
                    "position_warning",
                    f"{position['symbol']}: {status}",
                    "WARNING",
                    {"position_id": position["id"]},
                )
        self.repository.set_state("last_position_monitor", utc_now())
        return results
