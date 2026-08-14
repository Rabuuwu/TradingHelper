# Testowanie

```bash
ruff check src tests
pytest --cov=trading_helper --cov-report=term-missing
```

CI używa Python 3.11/3.12 i wyłącznie fake/sample data. Testujemy wskaźniki, scoring,
risk, fractional sizing, koszty, cache/provider, portfolio, journal, alert outbox,
auth, SQLite, API ASGI, service pipeline i backtest. Prawdziwy provider ma osobny zestaw
testów kontraktowych poza CI oraz fixtures nagrane bez sekretów.

Definition of Done: kod, happy/error tests, dokumentacja, lint, coverage i działający
scenariusz. Target bieżący >=70%, docelowy >=80%. Soak test 14 dni pozostaje osobnym
kryterium operacyjnym.
