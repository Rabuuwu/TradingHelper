# TradingHelper

Broker-independent Trading Assistant działający 24/7 na jednym serwerze Linux.
Analizuje dane rynkowe, tworzy wyjaśnialne sygnały, monitoruje ręczne i symulowane
pozycje oraz wysyła alerty. Broker (XTB, IBKR, Trading212 lub inny) służy wyłącznie
do ręcznego wykonania decyzji użytkownika.

> TradingHelper nigdy nie loguje się do brokera, nie klika w jego aplikacji i nie
> posiada funkcji automatycznego kupna, sprzedaży ani składania zleceń.

## Co działa

- neutralny `MarketDataProvider` z provenance, retry, rate-limit-ready API i SQLite cache,
- offline `SampleMarketDataProvider`, dzięki któremu start nie wymaga brokera ani internetu,
- multi-timeframe: trend 1D i setup 1H (konfigurowalne),
- EMA20/50/200, RSI, MACD, ATR, Bollinger Bands, relative volume, OBV i ROC,
- deterministyczny scoring 0–100 z breakdown, reasons, warnings i statusem danych,
- entry zone, SL, TP1/TP2, R:R, fractional sizing i trade feasibility dla kapitału 100 PLN,
- konfigurowalne profile kosztów XTB/IBKR/custom (profile nie są integracjami),
- ręczne portfolio, paper/simulation positions, trailing ATR i trade journal,
- SQLite, outbox alertów ntfy z retry, event log, scheduler, watchdog-ready status i backup,
- FastAPI, SSE live updates, responsywny dashboard instalowalny jako PWA,
- opcjonalne single-user auth bcrypt + HttpOnly cookie,
- systemd i bezpieczny zdalny dostęp przez Tailscale.

## Szybki start bez brokera

```bash
git clone https://github.com/Rabuuwu/TradingHelper.git
cd TradingHelper
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
cp .env.example .env
cp config/settings.example.yaml config/settings.yaml
pytest
ruff check src tests
python -m trading_helper.main self-check
python -m trading_helper.main init-db
python -m trading_helper.main scan-once
python -m trading_helper.main run
```

Dashboard: `http://127.0.0.1:8787`. Polecenie `run` uruchamia centralny backend,
scheduler i web UI. Zamknięcie przeglądarki nie zatrzymuje analiz ani ntfy.

## Najważniejsze endpointy

- `GET /health`, `/ready`, `/status`
- `GET /signals`, `/signals/{symbol}`
- `GET|POST|DELETE /watchlist`
- `GET|POST|PUT|DELETE /portfolio`
- `GET /portfolio/history`, `GET|PUT /paper/account`
- `POST /paper/buy`, `POST /paper/sell` (wyłącznie lokalna symulacja)
- `GET /market/candles/{symbol}`
- `GET|POST|PUT /trades`
- `GET /scanner/status`, `POST /scanner/run`
- `GET|PUT /settings/public`
- `GET /events`, `GET /events/stream` (SSE)

## Bezpieczny zdalny dostęp

Domyślny bind to `127.0.0.1`. Do telefonu i innych komputerów rekomendowany jest
Tailscale, bez publicznego port-forwardingu. Przy nasłuchu na prywatnym interfejsie
włącz `AUTH_ENABLED=true`. Publiczny Internet wymaga dodatkowo HTTPS reverse proxy.
Szczegóły: [docs/OPERATIONS.md](docs/OPERATIONS.md) i
[docs/SECURITY.md](docs/SECURITY.md).

## Dokumentacja

- [Architektura](docs/ARCHITECTURE.md)
- [Market data](docs/MARKET_DATA.md)
- [Signal engine](docs/SIGNAL_ENGINE.md)
- [Manual portfolio](docs/MANUAL_PORTFOLIO.md)
- [Cost model](docs/COST_MODEL.md)
- [Roadmapa](docs/ROADMAP.md)
- [Linux/operacje](docs/SETUP_LINUX.md), [testy](docs/TESTING.md)

## Disclaimer

TradingHelper jest narzędziem analitycznym i nie gwarantuje wyników. Użytkownik sam
ocenia i ręcznie wykonuje każdą transakcję. Score oznacza jakość setupu według reguł,
a nie prawdopodobieństwo sukcesu. Dane mogą być opóźnione lub nieaktualne; przed
transakcją należy sprawdzić bieżącą cenę w aplikacji brokera.

---

Projekt został stworzony przy wykorzystaniu narzędzi sztucznej inteligencji (SI)
wspomagających projektowanie, tworzenie kodu i dokumentacji.
