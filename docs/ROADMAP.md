# Roadmapa

DONE oznacza kod + testy + dokumentację + działający scenariusz.

- [x] 0. Repository/security — ignore sekretów, hard rule bez transakcji, historia migracji.
- [x] 1. Core architecture — centralny backend i rozdzielone warstwy.
- [x] 2. MarketDataProvider — kontrakt, sample provider, retry i provenance.
- [x] 3. Market data/cache — SQLite candles/quotes/symbols i indeksy.
- [x] 4. Indicators — EMA/RSI/MACD/ATR/Bollinger/volume/OBV/ROC z testami.
- [x] 5. Scanner — multi-timeframe i zunifikowane skanery bazowe.
- [x] 6. Signal scoring — model 0–100, breakdown/reasons/warnings.
- [x] 7. Risk Manager — R:R, fractional sizing i limity małego kapitału.
- [x] 8. Cost model — profile YAML, pełne koszty i feasibility.
- [x] 9. Manual portfolio — manual i paper positions w SQLite/API.
- [x] 10. Position monitor — P/L, ATR, trailing i statusy ostrzeżeń.
- [x] 11. Trailing stop — wirtualny, nigdy automatycznie w dół.
- [x] 12. Trade journal — OPEN/CLOSED/CANCELLED i statystyki.
- [x] 13. Notifications — ntfy outbox, retry i deduplikacja per świeca.
- [x] 14. REST API — wymagane CRUD, health/ready/status, SSE i auth.
- [x] 15. PWA Dashboard — responsive light mode, details, offline state, live SSE.
- [x] 16. Backtesting — bazowy engine bez entry lookahead i z kosztami.
- [x] 17. CI/test coverage — Python 3.11/3.12, lint, testy, coverage >=70%.
- [ ] 18. Paper simulation — kod/API gotowe; potrzebna pełna sesja walidacyjna.
- [ ] 19. 14-day soak test — wymaga rzeczywistego upływu 14 dni.
- [ ] 20. First controlled live test with small capital — dopiero po backteście i soak teście.

## Dalsze prace

- rzeczywisty provider danych z testami kontraktowymi i dokumentacją limitów,
- kalibracja strategii walk-forward, FX provider i session calendar,
- trwałe sesje/auth rate limiting oraz HTTPS reverse proxy,
- opcjonalny desktop companion/tray po ustabilizowaniu API,
- automatyczny raport soak/watchdog i coverage docelowo >=80%.
