# Cele projektu TradingHelper

## Cel główny

Zbudować lokalnego asystenta tradingowego działającego na Linuxie, który **bez AI** automatycznie obserwuje rynek i rachunek IBKR, przelicza dane oraz informuje użytkownika o potencjalnych okazjach i ryzyku, ale **nie składa zleceń**.

## Cele funkcjonalne

1. Automatyczna synchronizacja stanu rachunku i pozycji z IBKR.
2. Skanowanie określonego universe akcji/ETF-ów.
3. Obliczanie EMA, RSI, MACD, ATR, wolumenu i późniejszych wskaźników.
4. Jednolity scoring setupu 0–100 wraz z wyjaśnieniem punktacji.
5. Wyliczanie entry, proponowanego SL, TP, risk/reward i maksymalnej wielkości pozycji.
6. Monitorowanie otwartych pozycji i wirtualnego trailing stopu.
7. Alerty PUSH na telefon przez ntfy.
8. Historia sygnałów, skanów, alertów i pozycji w SQLite.
9. Backtesting strategii na danych historycznych.
10. Lokalny panel WWW do podglądu portfela, setupów, historii i stanu systemu.

## Cele jakościowe

- system ma być deterministyczny i możliwy do audytu,
- każda decyzja skryptu ma mieć czytelne powody,
- restart aplikacji nie może usuwać historii,
- błąd jednego tickera nie może zatrzymać całego skanera,
- utrata połączenia z IBKR ma być wykrywana i raportowana,
- brak danych nie może być interpretowany jako sygnał BUY/SELL,
- wszystkie moduły logiki finansowej muszą mieć testy jednostkowe.

## Poza zakresem V1

- automatyczne kupowanie/sprzedawanie,
- HFT i strategie sekundowe,
- modele ML/LLM,
- kopiowanie transakcji innych osób,
- handel z dźwignią jako domyślny tryb,
- obchodzenie ograniczeń lub zabezpieczeń IBKR.

## Kryterium ukończenia MVP

MVP uznajemy za gotowe, gdy system na koncie Paper Trading potrafi przez co najmniej 14 dni działać stabilnie, synchronizować portfolio, skanować universe, zapisywać wyniki, wysyłać alerty i nie generować nieobsłużonych wyjątków w normalnym trybie działania.
