from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from trading_helper.database import Repository, utc_now
from trading_helper.portfolio import ManualPortfolioService, PositionInput


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
        open_paper = self.repository.rows(
            "SELECT COUNT(*) count FROM manual_positions WHERE mode='PAPER' AND status='OPEN'"
        )[0]["count"]
        if open_paper:
            raise ValueError("Close paper positions before resetting the paper account")
        self.repository.execute("DELETE FROM paper_ledger")
        self.repository.execute(
            """UPDATE paper_accounts SET currency=?,initial_cash=?,cash_balance=?,
            realized_pnl=0,updated_at=? WHERE id=1""",
            (self.currency, initial_cash, initial_cash, utc_now()),
        )

    def buy(self, order: PaperBuy) -> int:
        if order.price <= 0 or order.quantity <= 0 or order.account_fx_rate <= 0:
            raise ValueError("Paper buy price, quantity and FX rate must be positive")
        gross = order.price * order.quantity * order.account_fx_rate
        total = gross + order.fees_account_currency
        account = self.account()
        if total > account["cash_balance"] + 1e-9:
            raise ValueError(
                f"Insufficient paper cash: required {total:.2f} {self.currency}, "
                f"available {account['cash_balance']:.2f} {self.currency}"
            )
        position_id = ManualPortfolioService(self.repository).simulate(
            PositionInput(
                order.symbol.upper(),
                "SIMULATION",
                order.price,
                order.quantity,
                order.instrument_currency.upper(),
                datetime.now(UTC).isoformat(),
                order.stop_price,
                order.target_price,
                order.target_price_2,
                f"Paper buy from signal {order.signal_id}" if order.signal_id else "Paper buy",
                "PAPER",
            )
        )
        self.repository.execute(
            "UPDATE trades SET fees=?,signal_score_at_entry=? WHERE position_id=?",
            (order.fees_account_currency / order.account_fx_rate, order.signal_score, position_id),
        )
        self.repository.execute(
            "UPDATE paper_accounts SET cash_balance=cash_balance-?,updated_at=? WHERE id=1",
            (total, utc_now()),
        )
        self.repository.execute(
            """INSERT INTO paper_ledger(timestamp,transaction_type,symbol,position_id,signal_id,
            quantity,price,gross_value,fees,cash_change,currency,notes)
            VALUES(?,'BUY',?,?,?,?,?,?,?,?,?,?)""",
            (
                utc_now(),
                order.symbol.upper(),
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
        return position_id

    def sell(
        self,
        position_id: int,
        exit_price: float,
        account_fx_rate: float,
        fees_account_currency: float,
    ) -> dict[str, float]:
        rows = self.repository.rows(
            """SELECT * FROM manual_positions WHERE id=? AND mode='PAPER'
            AND status='OPEN'""",
            (position_id,),
        )
        if not rows:
            raise ValueError("Open paper position not found")
        if exit_price <= 0 or account_fx_rate <= 0:
            raise ValueError("Paper sell price and FX rate must be positive")
        position = rows[0]
        gross = exit_price * position["quantity"] * account_fx_rate
        proceeds = gross - fees_account_currency
        buy = self.repository.rows(
            "SELECT cash_change FROM paper_ledger WHERE position_id=? AND transaction_type='BUY'",
            (position_id,),
        )[0]
        realized = proceeds + float(buy["cash_change"])
        ManualPortfolioService(self.repository).close(
            position_id,
            exit_price,
            fees_account_currency / account_fx_rate,
        )
        self.repository.execute(
            """UPDATE paper_accounts SET cash_balance=cash_balance+?,
            realized_pnl=realized_pnl+?,updated_at=? WHERE id=1""",
            (proceeds, realized, utc_now()),
        )
        self.repository.execute(
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
