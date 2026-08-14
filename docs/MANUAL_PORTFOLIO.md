# Manual portfolio i simulation

Pozycja zawiera symbol, broker jako etykietę, entry, fractional quantity, currency, datę,
opcjonalne SL/TP i notes. `mode=MANUAL` opisuje pozycję wykonaną ręcznie u brokera;
`mode=PAPER` tworzy lokalną symulację. System nigdy nie wysyła zlecenia.

Monitor pobiera quote/candles, liczy P/L, najwyższą cenę, ATR trailing oraz HOLD,
WATCH_EXIT, TAKE_PROFIT, TRAILING_STOP_WARNING lub EXIT_WARNING. Trailing long może
pozostać bez zmian albo wzrosnąć. Zamknięcie pozycji aktualizuje journal i statystyki.
