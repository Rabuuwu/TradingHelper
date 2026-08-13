# Wymagania

## Funkcjonalne

### FR-01 — IBKR
- połączenie z TWS/IB Gateway przez oficjalne TWS API,
- tryb Paper jako domyślny,
- odczyt statusu połączenia,
- odczyt rachunku i pozycji,
- pobieranie danych historycznych/rynkowych zgodnie z uprawnieniami konta,
- brak metod wykonujących zlecenia w V1.

### FR-02 — Scanner
- konfigurowalny universe,
- niezależna analiza każdego instrumentu,
- EMA 20/50/200, RSI 14, MACD, ATR 14 i względny wolumen,
- scoring 0–100,
- progi WATCH i ALERT w konfiguracji.

### FR-03 — Risk Manager
- ryzyko jako % portfela,
- maksymalna strata w walucie rachunku,
- wielkość pozycji na podstawie entry i stop,
- minimalny R:R,
- limity ekspozycji,
- walidacja niepoprawnych danych wejściowych.

### FR-04 — Position Monitor
- monitoring ceny względem entry i stop,
- wirtualny trailing stop oparty o ATR,
- stop nigdy nie przesuwa się w gorszą stronę dla pozycji long,
- alert po naruszeniu poziomu.

### FR-05 — Powiadomienia
- ntfy,
- poziomy priorytetu,
- deduplikacja powtarzających się alertów,
- brak tokenów/topiców w repo.

### FR-06 — Persistence
- SQLite,
- sygnały, pozycje/cache pozycji, alerty i przebiegi skanera,
- migracje schematu od pierwszej stabilnej wersji.

### FR-07 — API/UI
- endpoint `/health`,
- endpoint `/status`,
- później portfolio, opportunities, signals i history,
- domyślnie bind tylko do `127.0.0.1`.

### FR-08 — Backtesting
- ten sam kod wskaźników/scoringu co w live scannerze,
- brak look-ahead bias,
- uwzględnienie kosztów w modelu testowym,
- metryki: liczba transakcji, win rate, expectancy, profit factor, max drawdown.

## Niefunkcjonalne

### NFR-01 — Bezpieczeństwo
- `.env` ignorowany przez Git,
- API IBKR Read-Only w fazie V1,
- aplikacja nie wystawia publicznego portu bez świadomej konfiguracji,
- logi nie zawierają haseł ani sekretów.

### NFR-02 — Stabilność
- reconnect po utracie IBKR,
- timeouty na requestach zewnętrznych,
- kontrolowany shutdown,
- izolacja błędów pojedynczego symbolu.

### NFR-03 — Testowalność
- logika domenowa niezależna od API IBKR,
- minimum 80% coverage dla modułów `risk`, `scanner`, `indicators`, `trailing`,
- integracja IBKR testowana osobno na Paper.

### NFR-04 — Wydajność
- brak GPU,
- skaner projektowany pod pracę na CPU,
- brak konieczności uruchamiania modeli AI,
- SQLite dla jednej lokalnej instancji.

## Ograniczenia danych

Dostępność danych live/historical zależy od uprawnień i subskrypcji IBKR. System musi rozróżniać dane live, delayed i brak danych oraz nigdy nie ukrywać tego przed użytkownikiem.
