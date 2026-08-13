# Checklista projektu

To jest główna checklista, której trzymamy się przy rozwoju. Punkt oznaczamy jako ukończony dopiero po kodzie, testach i krótkiej dokumentacji.

## 0. Repo i bezpieczeństwo
- [x] Utworzyć repozytorium GitHub.
- [x] Dodać `.gitignore` i `.env.example`.
- [x] Zdefiniować cele, wymagania i architekturę.
- [x] Dodać podstawowe testy i CI.
- [ ] Ustawić repo jako Private.
- [ ] Włączyć ochronę gałęzi `main` po ustabilizowaniu CI.

## 1. Środowisko Linux
- [ ] Sklonować repo na Linuxa.
- [ ] Zainstalować Python 3.11+ i `python3-venv`.
- [ ] Utworzyć `.venv`.
- [ ] `pip install -e '.[dev]'`.
- [ ] Skopiować `.env.example` do `.env`.
- [ ] Skopiować `settings.example.yaml` do `settings.yaml`.
- [ ] Uruchomić `make lint`, `make test` i `self-check`.

## 2. IBKR Paper + TWS API
- [ ] Konto IBKR aktywne.
- [ ] Aktywować Paper Trading.
- [ ] Zainstalować IB Gateway na Linuxie.
- [ ] Pobrać oficjalne TWS API.
- [ ] Zainstalować `ibapi` z `source/pythonclient`.
- [ ] Włączyć socket clients.
- [ ] Zostawić Read-Only API włączone.
- [ ] Ustawić localhost-only.
- [ ] Potwierdzić port Paper (IBG domyślnie 4002).
- [ ] Test połączenia i reconnectu.

## 3. Portfolio sync
- [ ] Account summary.
- [ ] Lista pozycji.
- [ ] Cache pozycji w SQLite.
- [ ] Obsługa pustego portfela i disconnectu.
- [ ] Test integracyjny Paper.

## 4. Dane rynkowe
- [ ] Rozpoznanie subskrypcji danych.
- [ ] Jawne LIVE/DELAYED/FROZEN.
- [ ] Historical bars.
- [ ] Walidacja brakujących świec.
- [ ] Cache i kontrola pacing.

## 5. Wskaźniki
- [x] Fundament EMA/RSI/MACD/ATR/volume ratio.
- [ ] Testy referencyjne.
- [ ] Support/resistance.
- [ ] Breakout detector.
- [ ] Pullback detector.
- [ ] Trend regime.

## 6. Scoring
- [x] Bazowy scoring 0–100.
- [ ] Pełne wyjaśnienie punktacji.
- [ ] Kalibracja wag przez backtest.
- [ ] Progi WATCH/ALERT.
- [ ] Blokada sygnału przy niekompletnych danych.

## 7. Risk Manager
- [x] Position sizing.
- [x] Bazowe R:R.
- [ ] Limit pojedynczej pozycji.
- [ ] Limit ekspozycji portfela i sektorowy.
- [ ] Dzienne ryzyko/strata.
- [ ] Waluta rachunku i FX conversion.

## 8. Trailing stop / exit helper
- [x] Bazowy trailing ATR.
- [ ] Break-even rules.
- [ ] Partial TP suggestions.
- [ ] Exit score.
- [ ] Alert naruszenia trailing stop.
- [ ] Deduplikacja alertów.

## 9. ntfy
- [x] Klient ntfy.
- [ ] Prywatny losowy topic.
- [ ] Test PUSH.
- [ ] Alert BUY/WATCH/risk/exit/trailing/health.

## 10. SQLite i historia
- [x] Schemat początkowy.
- [ ] Warstwa repository.
- [ ] Migracje.
- [ ] Retencja i eksport CSV.

## 11. Lokalne API i panel
- [x] `/health` i `/status`.
- [ ] `/portfolio`, `/opportunities`, `/signals`, `/history`.
- [ ] Dashboard light mode.
- [ ] Widok szczegółów setupu.
- [ ] Responsywny widok telefonu.

## 12. Backtesting
- [ ] Silnik backtestu.
- [ ] Koszty/prowizje/slippage.
- [ ] Walk-forward split.
- [ ] Win rate, profit factor, expectancy, max drawdown.
- [ ] Raport strategii.

## 13. CI / jakość
- [x] pytest.
- [x] Ruff.
- [x] GitHub Actions.
- [ ] Coverage >= 80% dla logiki domenowej.
- [ ] Integracyjne markerem `integration`.
- [ ] Pre-commit hooks.

## 14. Paper soak test
- [ ] Minimum 14 dni ciągłego działania.
- [ ] Zero nieobsłużonych crashy.
- [ ] Analiza alertów i opóźnień danych.
- [ ] Raport z testu.

## 15. Gotowość do realnego kapitału
- [ ] Wszystkie krytyczne testy zielone.
- [ ] Strategia ma zaakceptowany backtest + paper test.
- [ ] Ustalony maksymalny risk/trade.
- [ ] Backup SQLite i monitoring.
- [ ] Nadal brak automatycznych zleceń.
