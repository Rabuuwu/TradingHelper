# TradingHelper

Lokalny asystent do analizy rynku i monitorowania portfela z integracją Interactive Brokers (IBKR).

## Założenia projektu

TradingHelper ma działać lokalnie na Linuxie i wspierać decyzje inwestycyjne bez użycia lokalnego modelu AI. System analizuje dane rynkowe, ocenia setupy, monitoruje otwarte pozycje, liczy ryzyko oraz wysyła powiadomienia na telefon. Transakcje pozostają ręczne po stronie użytkownika.

## Główne funkcje V1

- połączenie z kontem IBKR w trybie paper trading,
- synchronizacja podstawowych danych portfela,
- skaner rynku,
- analiza EMA, RSI, MACD, ATR i wolumenu,
- scoring setupów 0-100,
- risk manager,
- wirtualny trailing stop i alerty sprzedażowe,
- powiadomienia przez ntfy,
- lokalna baza SQLite,
- backtesting strategii,
- lokalny panel WWW w późniejszym etapie.

## Bezpieczeństwo

Projekt nie powinien przechowywać haseł, tokenów ani innych sekretów w repozytorium. Dane konfiguracyjne wrażliwe należy trzymać wyłącznie w lokalnym pliku `.env`, który jest ignorowany przez Git.

Na początku integracja z IBKR ma działać wyłącznie w trybie paper trading. Automatyczne składanie zleceń nie jest częścią V1.

## Architektura

```text
TradingHelper/
├── config/
│   └── settings.example.yaml
├── data/
├── src/
│   └── trading_helper/
│       ├── alerts/
│       ├── ibkr/
│       ├── risk/
│       ├── scanner/
│       ├── config.py
│       └── main.py
├── tests/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Uruchomienie lokalne

```bash
git clone https://github.com/Rabuuwu/TradingHelper.git
cd TradingHelper
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
python -m trading_helper.main
```

## Plan rozwoju

1. Fundament projektu i konfiguracja.
2. Połączenie z IBKR Paper Trading.
3. Pobieranie pozycji, salda i danych rynkowych.
4. Wskaźniki techniczne i scoring.
5. Risk manager i monitoring pozycji.
6. ntfy i alerty mobilne.
7. Backtesting.
8. Lokalny panel WWW.
9. Długotrwałe testy paper trading.
10. Dopiero później użycie przy realnym kapitale.

## Ważne

TradingHelper jest narzędziem analitycznym. Wynik skanera lub scoring nie jest gwarancją zysku ani rekomendacją inwestycyjną.
