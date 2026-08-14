from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from trading_helper.risk.costs import FeeCalculator
from trading_helper.scanner.scanners import build_snapshot
from trading_helper.signal_engine import score_setup


@dataclass(frozen=True)
class BacktestReport:
    total_trades: int
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: float
    max_drawdown: float
    sharpe: float
    expectancy: float
    net_return: float


def run_backtest(
    frame: pd.DataFrame,
    fee_calculator: FeeCalculator,
    entry_score: int = 70,
    holding_bars: int = 10,
) -> BacktestReport:
    if len(frame) < 220 + holding_bars:
        raise ValueError("Backtest requires enough history for indicators and forward exits")
    returns: list[float] = []
    cursor = 200
    while cursor + holding_bars < len(frame):
        history = frame.iloc[:cursor]
        snapshot = build_snapshot(history)
        score = score_setup(snapshot, risk_reward=3, data_timestamp=history.index[-1])
        if score.score >= entry_score:
            entry = float(frame["open"].iloc[cursor])
            exit_price = float(frame["close"].iloc[cursor + holding_bars])
            if exit_price > entry:
                costs = fee_calculator.estimate(entry, exit_price, 1)
                returns.append(costs.expected_net_profit)
            else:
                # Costs still reduce a losing trade; calculate them from notional directly.
                profile = fee_calculator.profile
                estimated = max(profile.commission_buy, profile.minimum_fee)
                estimated += max(profile.commission_sell, profile.minimum_fee)
                estimated += entry * (profile.spread_percent + 2 * profile.slippage_percent) / 100
                returns.append(exit_price - entry - estimated)
            cursor += holding_bars
        cursor += 1
    if not returns:
        return BacktestReport(0, 0, 0, 0, 0, 0, 0, 0, 0)
    wins = [value for value in returns if value > 0]
    losses = [value for value in returns if value < 0]
    equity = np.cumsum(returns)
    peaks = np.maximum.accumulate(np.r_[0.0, equity])
    drawdowns = peaks[1:] - equity
    standard_deviation = float(np.std(returns, ddof=1)) if len(returns) > 1 else 0
    sharpe = (
        float(np.mean(returns) / standard_deviation * math.sqrt(252)) if standard_deviation else 0
    )
    gross_loss = abs(sum(losses))
    return BacktestReport(
        len(returns),
        round(len(wins) / len(returns) * 100, 2),
        round(sum(wins) / len(wins), 4) if wins else 0,
        round(sum(losses) / len(losses), 4) if losses else 0,
        round(sum(wins) / gross_loss, 4) if gross_loss else 0,
        round(float(drawdowns.max(initial=0)), 4),
        round(sharpe, 4),
        round(float(np.mean(returns)), 4),
        round(sum(returns), 4),
    )
