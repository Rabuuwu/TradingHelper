# TradingHelper

Lokalny, lekki asystent do analizy rynku i monitorowania portfela z integracją Interactive Brokers (IBKR).

> **Status:** fundament projektu / Paper Trading first. TradingHelper nie wykonuje automatycznie transakcji. Decyzja i złożenie zlecenia pozostają po stronie użytkownika.

## Cel

TradingHelper ma działać 24/7 na komputerze z Linuxem bez lokalnego modelu AI. System ma:

- pobierać dane rachunku i rynku przez oficjalne TWS API IBKR,
- skanować zdefiniowany universe instrumentów,
- liczyć wskaźniki techniczne i scoring setupów 0–100,
- wyliczać wielkość pozycji, ryzyko, SL/TP i risk/reward,
- monitorować otwarte pozycje i wirtualny trailing stop,
- wysyłać powiadomienia na telefon przez ntfy,
- zapisywać historię sygnałów i zdarzeń w SQLite,
- udostępniać lokalne API/panel WWW,
- umożliwiać backtesting przed użyciem strategii przy realnym kapitale.

## Zasady bezpieczeństwa V1

1. Tylko konto **IBKR Paper Trading** podczas developmentu i testów integracyjnych.
2. W IB Gateway/TWS pozostawione **Read-Only API**.
3. Brak kodu do `placeOrder`, `cancelOrder` lub automatycznej egzekucji.
4. Sekrety i lokalne dane nie trafiają do Git (`.env`, SQLite, logi).
5. Każda strategia musi przejść testy jednostkowe, backtest i okres paper trading przed oznaczeniem jako gotowa.

## Stack

- Python 3.11+
- oficjalne Interactive Brokers TWS API (`ibapi` instalowane z paczki IBKR)
- IB Gateway na Linuxie
- FastAPI + Uvicorn — lokalne API/panel
- pandas + NumPy — analiza danych
- SQLite — dane lokalne
- ntfy — powiadomienia mobilne
- pytest + Ruff — testy i jakość kodu
- GitHub Actions — CI

## Struktura

```text
TradingHelper/
├── .github/workflows/ci.yml
├── config/settings.example.yaml
├── docs/
├── scripts/
├── src/trading_helper/
├── tests/
├── .env.example
├── .gitignore
├── Makefile
└── pyproject.toml
```

## Szybki start

Pełna instrukcja: [docs/SETUP_LINUX.md](docs/SETUP_LINUX.md) i [docs/IBKR_SETUP.md](docs/IBKR_SETUP.md).

```bash
git clone https://github.com/Rabuuwu/TradingHelper.git
cd TradingHelper
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
cp .env.example .env
cp config/settings.example.yaml config/settings.yaml
make test
python -m trading_helper.main self-check
python -m trading_helper.main init-db
```

Oficjalny pakiet `ibapi` instalujemy osobno z katalogu `source/pythonclient` pobranej paczki TWS API:

```bash
./scripts/install_ibapi.sh ~/IBJts/source/pythonclient
```

## Dokumenty sterujące projektem

- **Cele:** [docs/GOALS.md](docs/GOALS.md)
- **Wymagania:** [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)
- **Checklista/roadmapa:** [docs/ROADMAP.md](docs/ROADMAP.md)
- **Architektura:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Testy:** [docs/TESTING.md](docs/TESTING.md)
- **Bezpieczeństwo:** [docs/SECURITY.md](docs/SECURITY.md)
- **Specyfikacja strategii:** [docs/STRATEGY_SPEC.md](docs/STRATEGY_SPEC.md)
- **Operacje 24/7:** [docs/OPERATIONS.md](docs/OPERATIONS.md)

## Disclaimer

TradingHelper jest narzędziem analitycznym. Scoring, alerty i poziomy ryzyka nie gwarantują wyniku inwestycji i nie zastępują własnej oceny ryzyka.

---

Projekt został stworzony przy wykorzystaniu narzędzi sztucznej inteligencji (SI) wspomagających projektowanie, tworzenie kodu i dokumentacji.
