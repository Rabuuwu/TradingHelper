from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from trading_helper.database import Repository, utc_now
from trading_helper.service import TradingHelperService

LOGGER = logging.getLogger(__name__)
BUY_LABELS = ("BUY_SETUP", "STRONG_BUY_SETUP", "EXCEPTIONAL_SETUP")


@dataclass(frozen=True)
class AutoPaperConfig:
    initial_cash: float
    interval_seconds: int = 300
    minimum_score: int = 70
    signal_max_age_hours: int = 36
    bankruptcy_threshold: float = 0.01


class AutoPaperTrader:
    """Deterministic, simulation-only strategy runner with an immutable starting balance."""

    def __init__(self, service: TradingHelperService, config: AutoPaperConfig) -> None:
        if config.initial_cash <= 0 or config.interval_seconds < 30:
            raise ValueError(
                "Initial cash must be positive and interval must be at least 30 seconds"
            )
        self.service = service
        self.repository: Repository = service.repository
        self.strategy = service.strategy
        self.config = config
        self._ensure_account()

    def _ensure_account(self) -> None:
        existing = self.repository.rows("SELECT * FROM auto_paper_accounts WHERE id=1")
        if existing:
            if abs(float(existing[0]["initial_cash"]) - self.config.initial_cash) > 1e-9:
                raise ValueError(
                    "Auto PAPER account already exists with a different starting balance; "
                    "top-ups and resets are intentionally disabled"
                )
            return
        now = utc_now()
        self.repository.execute(
            """INSERT INTO auto_paper_accounts(id,currency,initial_cash,cash_balance,
            realized_pnl,status,created_at,updated_at) VALUES(1,?,?,?,0,'RUNNING',?,?)""",
            (
                self.strategy.portfolio_currency,
                self.config.initial_cash,
                self.config.initial_cash,
                now,
                now,
            ),
        )
        self._decision("START", reason="Created immutable auto PAPER account")

    def account(self) -> dict[str, Any]:
        return self.repository.rows("SELECT * FROM auto_paper_accounts WHERE id=1")[0]

    def positions(self, status: str = "OPEN") -> list[dict[str, Any]]:
        return self.repository.rows(
            "SELECT * FROM auto_paper_positions WHERE status=? ORDER BY id", (status,)
        )

    def _fee(self, value: float, side: str, requires_fx: bool, fx_rate: float) -> float:
        profile = self.service.fee_calculator.profile
        commission = profile.commission_buy if side == "BUY" else profile.commission_sell
        percent = profile.slippage_percent
        if side == "BUY":
            percent += profile.spread_percent
        if requires_fx:
            percent += profile.fx_percent
        return (max(commission, profile.minimum_fee) + value * percent / 100) * fx_rate

    def _equity(self, quotes: dict[str, float] | None = None) -> tuple[float, float]:
        account = self.account()
        market_value = 0.0
        quotes = quotes or {}
        for position in self.positions():
            price = quotes.get(position["symbol"])
            if price is None:
                price = self.service.market_data.get_quote(position["symbol"]).price
            fx = self.service.fx.get_rate(position["currency"], account["currency"])
            market_value += price * float(position["quantity"]) * fx.rate
        return float(account["cash_balance"]) + market_value, market_value

    def _decision(
        self,
        action: str,
        *,
        reason: str,
        symbol: str | None = None,
        signal_id: int | None = None,
        position_id: int | None = None,
        price: float | None = None,
        quantity: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        account = self.account()
        try:
            equity, _ = self._equity()
        except Exception:
            equity = float(account["cash_balance"])
        self.repository.execute(
            """INSERT INTO auto_paper_decisions(created_at,action,symbol,signal_id,
            position_id,price,quantity,account_cash,account_equity,reason,details_json)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (
                utc_now(),
                action,
                symbol,
                signal_id,
                position_id,
                price,
                quantity,
                account["cash_balance"],
                equity,
                reason,
                json.dumps(details or {}),
            ),
        )

    def _skip_once(self, signal: dict[str, Any], reason: str) -> None:
        existing = self.repository.rows(
            """SELECT 1 present FROM auto_paper_decisions
            WHERE action='SKIP' AND signal_id=? AND reason=? LIMIT 1""",
            (signal["id"], reason),
        )
        if not existing:
            self._decision(
                "SKIP",
                reason=reason,
                symbol=signal["symbol"],
                signal_id=signal["id"],
            )

    def _close(self, position: dict[str, Any], price: float, reason: str) -> None:
        account = self.account()
        fx = self.service.fx.get_rate(position["currency"], account["currency"])
        value = price * float(position["quantity"])
        fee = self._fee(value, "SELL", position["currency"] != account["currency"], fx.rate)
        proceeds = value * fx.rate - fee
        initial_cost = (
            float(position["entry_price"])
            * float(position["quantity"])
            * float(position["entry_fx_rate"])
            + float(position["entry_fee"])
        )
        pnl = proceeds - initial_cost
        now = utc_now()
        with self.repository.transaction() as connection:
            connection.execute(
                """UPDATE auto_paper_positions SET status='CLOSED',exit_date=?,exit_price=?,
                exit_fx_rate=?,exit_fee=?,exit_reason=?,realized_pnl=?,updated_at=? WHERE id=?
                AND status='OPEN'""",
                (now, price, fx.rate, fee, reason, pnl, now, position["id"]),
            )
            connection.execute(
                """UPDATE auto_paper_accounts SET cash_balance=cash_balance+?,
                realized_pnl=realized_pnl+?,updated_at=? WHERE id=1""",
                (proceeds, pnl, now),
            )
        self._decision(
            "SELL",
            reason=reason,
            symbol=position["symbol"],
            signal_id=position["signal_id"],
            position_id=position["id"],
            price=price,
            quantity=position["quantity"],
            details={"fee": fee, "proceeds": proceeds, "realized_pnl": pnl},
        )

    def _monitor_positions(self) -> dict[str, float]:
        quotes: dict[str, float] = {}
        for position in self.positions():
            quote = self.service.market_data.get_quote(position["symbol"])
            price = quote.price
            quotes[position["symbol"]] = price
            highest = max(float(position["highest_price"]), price)
            atr = float(position["atr"])
            atr_stop = (
                highest - atr * self.strategy.atr_stop_multiplier
                if atr > 0
                else float(position["trailing_stop"])
            )
            trailing = max(float(position["trailing_stop"]), atr_stop)
            self.repository.execute(
                """UPDATE auto_paper_positions SET highest_price=?,trailing_stop=?,updated_at=?
                WHERE id=? AND status='OPEN'""",
                (highest, trailing, utc_now(), position["id"]),
            )
            if price <= trailing:
                self._close(position, price, "STOP_OR_TRAILING")
            elif position["target_price_2"] and price >= float(position["target_price_2"]):
                self._close(position, price, "TAKE_PROFIT_2")
            elif price >= float(position["target_price"]):
                self._close(position, price, "TAKE_PROFIT_1")
        return quotes

    def _latest_candidates(self) -> list[dict[str, Any]]:
        cutoff = (datetime.now(UTC) - timedelta(hours=self.config.signal_max_age_hours)).isoformat()
        placeholders = ",".join("?" for _ in BUY_LABELS)
        return self.repository.rows(
            f"""SELECT s.* FROM signals s JOIN
            (SELECT symbol,MAX(id) id FROM signals GROUP BY symbol) latest ON latest.id=s.id
            WHERE s.score>=? AND s.label IN ({placeholders}) AND s.created_at>=?
            ORDER BY s.score DESC,s.id DESC""",
            (self.config.minimum_score, *BUY_LABELS, cutoff),
        )

    def _open(
        self, signal: dict[str, Any], price: float, equity: float, exposure: float
    ) -> str | None:
        account = self.account()
        details = json.loads(signal.get("details_json") or "{}")
        currency = str(details.get("currency") or "USD").upper()
        fx = self.service.fx.get_rate(currency, account["currency"])
        stop = float(signal["stop_price"] or 0)
        target = float(signal["target_price"] or 0)
        if stop <= 0 or stop >= price or target <= price:
            return "INVALID_TRADE_PLAN"
        available_cash = float(account["cash_balance"])
        risk_budget = equity * self.strategy.max_risk_per_trade_percent / 100
        risk_per_share = (price - stop) * fx.rate
        exposure_room = max(
            0.0,
            equity * self.strategy.max_portfolio_exposure_percent / 100 - exposure,
        )
        position_cap = min(
            available_cash,
            exposure_room,
            equity * self.strategy.max_single_position_percent / 100,
        )
        quantity = min(risk_budget / risk_per_share, position_cap / (price * fx.rate))
        suggested = float(signal["recommended_quantity"] or 0)
        if suggested > 0:
            quantity = min(quantity, suggested)
        if not self.strategy.fractional_shares:
            quantity = int(quantity)
        quantity = round(quantity, 6)
        if quantity <= 0:
            return "NO_FEASIBLE_POSITION_SIZE"
        requires_fx = currency != account["currency"]
        fee = self._fee(price * quantity, "BUY", requires_fx, fx.rate)
        total = price * quantity * fx.rate + fee
        if total > available_cash:
            quantity = max(0.0, (available_cash - fee) / (price * fx.rate))
            quantity = round(quantity, 6) if self.strategy.fractional_shares else int(quantity)
            total = price * quantity * fx.rate + fee
        if quantity <= 0 or total > available_cash + 1e-9:
            return "INSUFFICIENT_CASH_AFTER_COSTS"
        indicators = details.get("indicators") or {}
        atr = max(0.0, float(indicators.get("atr") or 0))
        now = utc_now()
        with self.repository.transaction() as connection:
            cursor = connection.execute(
                """INSERT INTO auto_paper_positions(symbol,signal_id,status,entry_date,
                entry_price,quantity,currency,entry_fx_rate,entry_fee,stop_price,trailing_stop,
                target_price,target_price_2,highest_price,atr,signal_score,updated_at)
                VALUES(?,?,'OPEN',?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    signal["symbol"], signal["id"], now, price, quantity, currency, fx.rate,
                    fee, stop, stop, target, signal["target_price_2"], price, atr,
                    signal["score"], now,
                ),
            )
            position_id = int(cursor.lastrowid)
            connection.execute(
                """UPDATE auto_paper_accounts SET cash_balance=cash_balance-?,updated_at=?
                WHERE id=1""",
                (total, now),
            )
        self._decision(
            "BUY",
            reason=f"Score {signal['score']} {signal['label']}",
            symbol=signal["symbol"],
            signal_id=signal["id"],
            position_id=position_id,
            price=price,
            quantity=quantity,
            details={"fee": fee, "total": total, "stop": stop, "target": target},
        )
        return None

    def cycle(self) -> dict[str, Any]:
        if self.account()["status"] != "RUNNING":
            return self.status()
        quotes = self._monitor_positions()
        equity, exposure = self._equity(quotes)
        if equity <= self.config.bankruptcy_threshold and not self.positions():
            self.repository.execute(
                """UPDATE auto_paper_accounts SET status='BANKRUPT',cash_balance=0,
                updated_at=? WHERE id=1""",
                (utc_now(),),
            )
            self._decision("STOP", reason="Account reached bankruptcy threshold")
            return self.status()
        open_positions = self.positions()
        open_symbols = {row["symbol"] for row in open_positions}
        bought_signals = {
            row["signal_id"]
            for row in self.repository.rows(
                "SELECT DISTINCT signal_id FROM auto_paper_positions WHERE signal_id IS NOT NULL"
            )
        }
        for signal in self._latest_candidates():
            if len(open_positions) >= self.strategy.max_open_positions:
                break
            if signal["symbol"] in open_symbols or signal["id"] in bought_signals:
                continue
            if str(signal.get("feasibility_status") or "").startswith("TRADE_REJECTED"):
                self._skip_once(signal, signal["feasibility_status"])
                continue
            quote = self.service.market_data.get_quote(signal["symbol"])
            price = quote.price
            entry_high = float(signal["entry_high"] or 0)
            if entry_high and price > entry_high:
                self._skip_once(signal, "PRICE_ABOVE_ENTRY_ZONE")
                continue
            rejection = self._open(signal, price, equity, exposure)
            if rejection is None:
                open_positions = self.positions()
                open_symbols.add(signal["symbol"])
                equity, exposure = self._equity()
            else:
                self._skip_once(signal, rejection)
        return self.status()

    def status(self) -> dict[str, Any]:
        account = self.account()
        equity, market_value = self._equity()
        closed = self.repository.rows(
            "SELECT realized_pnl FROM auto_paper_positions WHERE status='CLOSED'"
        )
        profits = [float(row["realized_pnl"] or 0) for row in closed]
        wins = sum(value > 0 for value in profits)
        gross_profit = sum(value for value in profits if value > 0)
        gross_loss = abs(sum(value for value in profits if value < 0))
        return {
            "status": account["status"],
            "currency": account["currency"],
            "initial_cash": round(float(account["initial_cash"]), 4),
            "cash": round(float(account["cash_balance"]), 4),
            "market_value": round(market_value, 4),
            "equity": round(equity, 4),
            "net_pnl": round(equity - float(account["initial_cash"]), 4),
            "return_percent": round((equity / float(account["initial_cash"]) - 1) * 100, 4),
            "open_positions": len(self.positions()),
            "closed_trades": len(closed),
            "wins": wins,
            "losses": len(closed) - wins,
            "win_rate": round(wins / len(closed) * 100, 2) if closed else 0.0,
            "profit_factor": (
                round(gross_profit / gross_loss, 4) if gross_loss else None
            ),
        }

    def run_forever(self) -> None:
        while self.account()["status"] == "RUNNING":
            try:
                market = self.service.provider.get_market_status().status
                if market in {"OPEN", "SIMULATION"}:
                    LOGGER.info("auto_paper_cycle", extra=self.cycle())
                else:
                    LOGGER.info("auto_paper_market_closed", extra={"market": market})
            except Exception:
                LOGGER.exception("auto_paper_cycle_failed")
            time.sleep(self.config.interval_seconds)
