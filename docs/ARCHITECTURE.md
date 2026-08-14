# Architektura

```text
MarketDataProvider -> SQLite cache -> indicators -> scanners -> signal engine
                                               |          |
                                               |          +-> risk/cost/feasibility
                                               +-> manual portfolio monitor
                                                          |
SQLite (source of truth) <- scheduler <- alerts/ntfy <- events
          |
FastAPI + SSE + PWA  <---- Tailscale/HTTPS ----> browser/phone/optional client
```

Backend Linux jest jedynym source of truth. Klienci nie uruchamiają skanera i nie
przechowują osobnych portfeli. PWA może być zamknięta, a scheduler i ntfy nadal działają.

## Granice

- `market_data/`: kontrakt, modele provenance, provider, cache, retry; nie zna strategii.
- `scanner/`: czysta matematyka pandas/numpy; brak sieci, bazy i powiadomień.
- `signal_engine.py`: deterministyczne punkty, klasyfikacja i wyjaśnienia.
- `risk/`: sizing, R:R, koszty i feasibility; brak brokera.
- `portfolio.py`, `journal.py`: pozycje wpisane przez użytkownika lub paper mode.
- `service.py`: orkiestracja skanów, monitora i scheduler 24/7.
- `database.py`: wersjonowany, kompatybilny schemat SQLite.
- `api.py`, `web/`: kliencka warstwa HTTP/SSE/PWA, bez logiki tradingowej.

Nie istnieje warstwa order execution. Provider danych nie jest brokerem i nie może
otrzymać metod `buy`, `sell`, `placeOrder`, logowania do brokera ani automatyzacji UI.

Historyczny adapter IBKR usunięto z runtime; opis migracji jest w `docs/archive/`.
