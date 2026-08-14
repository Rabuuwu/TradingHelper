from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from trading_helper.database import Repository, utc_now


@dataclass(frozen=True)
class PaperBuy:
    symbol: str
    price: float
    quantity: float
    instrument_currency: str
    account_fx_rate: float
    fees_account_currency: float
    stop_price: float | None = None
    target_price: float | None = None
    target_price_2: float | None = None
    signal_id: int | None = None
    signal_score: int | None = None
    entry_date: str | None = None
    strategy: str = ""
    notes: str = ""


class PaperPortfolioService:
    def __init__(self, repository: Repository, initial_cash: float, currency: str) -> None:
        self.repository = repository
        self.currency = currency.upper()
        self.ensure_account(initial_cash)

    def ensure_account(self, initial_cash: float) -> None:
        if initial_cash <= 0:
            raise ValueError("Paper portfolio value must be positive")
        self.repository.execute(
            """INSERT OR IGNORE INTO paper_accounts(id,currency,initial_cash,cash_balance,
            realized_pnl,updated_at) VALUES(1,?,?,?,0,?)""",
            (self.currency, initial_cash, initial_cash, utc_now()),
        )

    def account(self) -> dict[str, Any]:
        return self.repository.rows("SELECT * FROM paper_accounts WHERE id=1")[0]

    def reset(self, initial_cash: float) -> None:
        if initial_cash <= 0:
            raise ValueError("Paper portfolio value must be positive")
        with self.repository.transaction() as connection:
            open_paper = connection.execute(
                "SELECT COUNT(*) FROM manual_positions WHERE mode='PAPER' AND status='OPEN'"
            ).fetchone()[0]
            if open_paper:
                raise ValueError("Close paper positions before resetting the paper account")
            connection.execute("DELETE FROM paper_ledger")
            connection.execute(
                """UPDATE paper_accounts SET currency=?,initial_cash=?,cash_balance=?,
                realized_pnl=0,updated_at=? WHERE id=1""",
                (self.currency, initial_cash, initial_cash, utc_now()),
            )

    def buy(self, order: PaperBuy) -> int:
        if order.price <= 0 or order.quantity <= 0 or order.account_fx_rate <= 0:
            raise ValueError("Paper buy price, quantity and FX rate must be positive")
        gross = order.price * order.quantity * order.account_fx_rate
        total = gross + order.fees_account_currency
        symbol = order.symbol.upper()
        currency = order.instrument_currency.upper()
        entered_at = order.entry_date or datetime.now(UTC).isoformat()
        origin = f"Paper buy from signal {order.signal_id}" if order.signal_id else "Paper buy"
        notes = f"{origin}. {order.notes.strip()}" if order.notes.strip() else origin
        with self.repository.transaction() as connection:
            account = connection.execute(
                "SELECT cash_balance FROM paper_accounts WHERE id=1"
            ).fetchone()
            available = float(account[0])
            if total > available + 1e-9:
                raise ValueError(
                    f"Insufficient paper cash: required {total:.2f} {self.currency}, "
                    f"available {available:.2f} {self.currency}"
                )
            cursor = connection.execute(
                """INSERT INTO manual_positions(symbol,broker,mode,entry_price,quantity,currency,
                entry_date,stop_price,target_price,target_price_2,highest_price,notes,updated_at)
                VALUES(?,'SIMULATION','PAPER',?,?,?,?,?,?,?,?,?,?)""",
                (
                    symbol,
                    order.price,
                    order.quantity,
                    currency,
                    entered_at,
                    order.stop_price,
                    order.target_price,
                    order.target_price_2,
                    order.price,
                    notes,
                    utc_now(),
                ),
            )
            position_id = int(cursor.lastrowid)
            connection.execute(
                """INSERT INTO trades(position_id,symbol,broker,status,entry_date,entry_price,
                quantity,currency,fees,strategy,signal_score_at_entry,notes)
                VALUES(?,?,?,'OPEN',?,?,?,?,?,?,?,?)""",
                (
                    position_id,
                    symbol,
                    "SIMULATION",
                    entered_at,
                    order.price,
                    order.quantity,
                    currency,
                    order.fees_account_currency / order.account_fx_rate,
                    order.strategy.strip(),
                    order.signal_score,
                    notes,
                ),
            )
            connection.execute(
                "UPDATE paper_accounts SET cash_balance=cash_balance-?,updated_at=? WHERE id=1",
                (total, utc_now()),
            )
            connection.execute(
                """INSERT INTO paper_ledger(timestamp,transaction_type,symbol,position_id,signal_id,
            quantity,price,gross_value,fees,cash_change,currency,notes)
            VALUES(?,'BUY',?,?,?,?,?,?,?,?,?,?)""",
                (
                    utc_now(),
                    symbol,
                    position_id,
                    order.signal_id,
                    order.quantity,
                    order.price,
                    gross,
                    order.fees_account_currency,
                    -total,
                    self.currency,
                    "SIMULATION ONLY",
                ),
            )
            connection.execute(
                """INSERT INTO app_events(created_at,event_type,level,message,details_json)
                VALUES(?,'position_created','INFO',?,?)""",
                (
                    utc_now(),
                    f"Position created for {symbol}",
                    json.dumps({"position_id": position_id, "mode": "PAPER"}),
                ),
            )
        return position_id

    def sell(
        self,
        position_id: int,
        exit_price: float,
        account_fx_rate: float,
        fees_account_currency: float,
    ) -> dict[str, float]:
        if exit_price <= 0 or account_fx_rate <= 0:
            raise ValueError("Paper sell price and FX rate must be positive")
        closed_at = datetime.now(UTC).isoformat()
        with self.repository.transaction() as connection:
            position_row = connection.execute(
                """SELECT * FROM manual_positions WHERE id=? AND mode='PAPER'
                AND status='OPEN'""",
                (position_id,),
            ).fetchone()
            if not position_row:
                raise ValueError("Open paper position not found")
            position = dict(position_row)
            gross = exit_price * position["quantity"] * account_fx_rate
            proceeds = gross - fees_account_currency
            buy = connection.execute(
                """SELECT cash_change FROM paper_ledger
                WHERE position_id=? AND transaction_type='BUY'""",
                (position_id,),
            ).fetchone()
            if not buy:
                raise ValueError("Paper buy ledger entry not found")
            realized = proceeds + float(buy[0])
            fees_instrument = fees_account_currency / account_fx_rate
            pnl_instrument = (exit_price - position["entry_price"]) * position[
                "quantity"
            ] - fees_instrument
            pnl_percent = pnl_instrument / (position["entry_price"] * position["quantity"]) * 100
            connection.execute(
                "UPDATE manual_positions SET status='CLOSED',updated_at=? WHERE id=?",
                (utc_now(), position_id),
            )
            connection.execute(
                """UPDATE trades SET status='CLOSED',exit_date=?,exit_price=?,fees=fees+?,
                pnl=?,pnl_percent=? WHERE position_id=? AND status='OPEN'""",
                (closed_at, exit_price, fees_instrument, pnl_instrument, pnl_percent, position_id),
            )
            connection.execute(
                """UPDATE paper_accounts SET cash_balance=cash_balance+?,
            realized_pnl=realized_pnl+?,updated_at=? WHERE id=1""",
                (proceeds, realized, utc_now()),
            )
            connection.execute(
                """INSERT INTO paper_ledger(timestamp,transaction_type,symbol,position_id,
            quantity,price,gross_value,fees,cash_change,currency,notes)
            VALUES(?,'SELL',?,?,?,?,?,?,?,?,?)""",
                (
                    utc_now(),
                    position["symbol"],
                    position_id,
                    position["quantity"],
                    exit_price,
                    gross,
                    fees_account_currency,
                    proceeds,
                    self.currency,
                    "SIMULATION ONLY",
                ),
            )
        return {"proceeds": round(proceeds, 4), "realized_pnl": round(realized, 4)}

    def ledger(self, limit: int = 200) -> list[dict[str, Any]]:
        return self.repository.rows(
            "SELECT * FROM paper_ledger ORDER BY timestamp DESC LIMIT ?", (limit,)
        )
