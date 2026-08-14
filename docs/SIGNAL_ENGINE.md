# Signal engine

Pipeline analizuje trend timeframe i setup timeframe, buduje jednolity snapshot,
plan entry/SL/TP, sizing, koszty i scoring. Signal zapisuje instrument, score/class,
breakdown, reasons, warnings, wskaźniki, timeframe, provider, timestamp/delay,
feasibility i cost estimate.

Sygnał jest analizą, nie instrukcją. Alert zawsze przypomina o sprawdzeniu ceny u brokera.
Delayed i stale data są jawne. Klasy dla pozycji (HOLD/WATCH_EXIT/TAKE_PROFIT/
TRAILING_STOP_WARNING/EXIT_WARNING) są niezależne od klas nowych setupów.
