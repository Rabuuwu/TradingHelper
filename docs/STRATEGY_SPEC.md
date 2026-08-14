# Strategia i scoring

Score mierzy jakość deterministycznego setupu, nie prawdopodobieństwo zysku.

- Trend 0–25: EMA20>50 (8), EMA50>200 (8), cena>EMA200 (5), struktura (4).
- Momentum 0–20: RSI (5), MACD (5), ROC (5), price momentum (5).
- Volume 0–15: spike (6), OBV (4), rosnący wolumen (5).
- Volatility 0–10: użyteczny ATR (5), Bollinger context (5).
- Setup 0–20: breakout (8), pullback (5), support (7).
- Risk 0–10: R:R>=2 (5), R:R>=3 (kolejne 5).

Klasy: IGNORE 0–39, WATCH 40–59, INTERESTING 60–69, BUY_SETUP 70–79,
STRONG_BUY_SETUP 80–89, EXCEPTIONAL_SETUP 90–100.

Każdy zapis ma breakdown, reasons, warnings, timestamp, provider, delay, pełny snapshot
wskaźników i plan. Domyślnie trend pochodzi z 1D, setup z 1H. Backtest wchodzi dopiero
na następnym barze, aby ograniczyć lookahead. Wagi są hipotezą do kalibracji walk-forward.
