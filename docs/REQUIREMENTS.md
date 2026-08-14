# Wymagania

## Funkcjonalne

1. Wymienny MarketDataProvider: quote, candles, symbol info/search, market status, bulk quotes.
2. Cache SQLite z source/timestamp/delay oraz indeksami symbol/timeframe/timestamp.
3. Universe, watchlist i aktywne pozycje jako niezależne zbiory symboli.
4. Multi-timeframe indicators/scanners oraz wyjaśnialny score 0–100.
5. Risk, fractional sizing, konfigurowalne koszty i feasibility dla małego kapitału.
6. Manual i paper portfolio, saldo PAPER, ledger BUY/SELL, equity, P/L, SL/TP,
   trailing i exit warnings. PAPER nigdy nie wysyła zlecenia do brokera.
7. Trade journal oraz statystyki.
8. ntfy/outbox, deduplikacja, retry i event log.
9. FastAPI, SSE i PWA używane z jednej centralnej instancji.
10. Scheduler, health/readiness/status, backup oraz systemd.

## Niefunkcjonalne

- brak jakiegokolwiek order execution i automatyzacji brokera,
- deterministyczna/testowalna logika bez modeli generatywnych,
- brak requestów zewnętrznych w CI,
- sekrety wyłącznie w `.env`, bez ekspozycji przez API,
- localhost/Tailscale first, auth bcrypt/cookie, HTTPS przed publicznym dostępem,
- błąd symbolu nie zatrzymuje całego skanu,
- dane delayed/stale są jawne,
- Linux/SQLite bez wymaganego Dockera lub zewnętrznych serwerów.
