# Autonomous PAPER strategy experiment

`scripts/auto_paper_trader.py` is a separate, deterministic client of TradingHelper.
It reads signals and market data from the central application but writes to dedicated
`auto_paper_*` tables. It never calls a broker, never places a real order and never
uses the user's manual/PAPER account.

## Rules

- The starting balance is inserted exactly once. A later run with a different value
  fails; there is no reset or deposit operation.
- It considers fresh `BUY_SETUP`, `STRONG_BUY_SETUP` and `EXCEPTIONAL_SETUP` signals,
  highest score first.
- Position size is limited by risk per trade, cash, portfolio exposure, single-position
  exposure, maximum open positions and the signal's recommended quantity.
- Entry and exit include the configured commission, minimum fee, FX, spread and slippage.
- A full position exits on SL/monotonic ATR trailing stop, TP1 or TP2. Every BUY, SELL,
  SKIP and lifecycle event is stored with its reason.
- The process stops only after equity reaches the bankruptcy threshold and no positions
  remain. A lack of a current setup is not bankruptcy; the process waits for later scans.
- Multiple instances are blocked by a process lock and a database constraint.

The objective is to measure and maximize results under the configured deterministic
strategy and risk rules. Profit is not guaranteed. Changing parameters during an
experiment changes what is being measured and should be recorded as a new code version.

## Run

One decision cycle:

```bash
python scripts/auto_paper_trader.py --initial-cash 100 --once
```

Continuous process, polling every five minutes while the market is open:

```bash
python scripts/auto_paper_trader.py --initial-cash 100 --interval 300
```

Current performance:

```bash
python scripts/auto_paper_trader.py --initial-cash 100 --status
```

The status contains cash, market value, equity, net P/L, return, open/closed trades,
win rate and profit factor.

## systemd

Set `AUTO_PAPER_INITIAL_CASH` once in `.env`, then install the separate unit:

```bash
sudo cp deploy/trading-helper-auto-paper.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now trading-helper-auto-paper
sudo systemctl status trading-helper-auto-paper
```

The normal `trading-helper.service` remains the source of signals and the dashboard.
Stopping the autonomous PAPER unit does not stop TradingHelper and does not alter its
recorded balance.

On a host with user lingering enabled, the included user unit avoids sudo and still
survives logout and reboot:

```bash
mkdir -p ~/.config/systemd/user
cp deploy/trading-helper-auto-paper-user.service ~/.config/systemd/user/trading-helper-auto-paper.service
systemctl --user daemon-reload
systemctl --user enable --now trading-helper-auto-paper
```
