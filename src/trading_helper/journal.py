from __future__ import annotations

from typing import Any

from trading_helper.database import Repository


class TradeJournal:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def list(self) -> list[dict[str, Any]]:
        return self.repository.rows("SELECT * FROM trades ORDER BY id DESC")

    def update(self, trade_id: int, changes: dict[str, Any]) -> None:
        allowed = {
            "status",
            "exit_date",
            "exit_price",
            "fees",
            "strategy",
            "signal_score_at_entry",
            "notes",
        }
        values = {key: value for key, value in changes.items() if key in allowed}
        if not values:
            raise ValueError("No editable trade fields supplied")
        assignments = ",".join(f"{key}=?" for key in values)
        self.repository.execute(
            f"UPDATE trades SET {assignments} WHERE id=?", (*values.values(), trade_id)
        )

    def statistics(self) -> dict[str, float | int]:
        trades = self.repository.rows(
            "SELECT pnl FROM trades WHERE status='CLOSED' AND pnl IS NOT NULL"
        )
        values = [float(trade["pnl"]) for trade in trades]
        wins = [value for value in values if value > 0]
        losses = [value for value in values if value < 0]
        total = len(values)
        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        average_win = gross_profit / len(wins) if wins else 0.0
        average_loss = sum(losses) / len(losses) if losses else 0.0
        return {
            "total_trades": total,
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / total * 100, 2) if total else 0.0,
            "average_win": round(average_win, 4),
            "average_loss": round(average_loss, 4),
            "profit_factor": round(gross_profit / gross_loss, 4) if gross_loss else 0.0,
            "expectancy": round(sum(values) / total, 4) if total else 0.0,
            "net_pnl": round(sum(values), 4),
        }
