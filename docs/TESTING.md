# Strategia testów

## Warstwy

### 1. Unit tests
Dotyczą czystej logiki: wskaźniki, scoring, risk manager, trailing stop, konfiguracja i persistence. Nie wymagają IBKR ani internetu.

### 2. Integration tests — Paper Trading

- connect/disconnect,
- account summary,
- positions,
- historical bars,
- reconnect,
- błędny port / brak Gateway,
- brak uprawnień do market data.

Nigdy nie używamy konta Live do CI.

### 3. Backtest tests

Sprawdzają brak look-ahead, deterministyczny wynik, koszty i poprawne zamykanie pozycji na danych testowych.

### 4. Soak test

Minimum 14 dni na Paper: uptime, reconnecty, pamięć/CPU, alerty, duplikaty i brakujące dane.

## Komendy

```bash
make lint
make test
pytest --cov=trading_helper --cov-report=html
```

## Definition of Done dla funkcji

- [ ] kod działa,
- [ ] błędne wejście jest obsłużone,
- [ ] unit test happy path,
- [ ] unit test edge/error path,
- [ ] lint przechodzi,
- [ ] dokumentacja/config zaktualizowane,
- [ ] jeśli dotyczy IBKR — test Paper.
