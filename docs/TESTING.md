# Testowanie

```bash
ruff check src tests
pytest --cov=trading_helper --cov-report=term-missing
```

CI używa Python 3.11/3.12 i wyłącznie fake/sample data. Testujemy wskaźniki, scoring,
risk, fractional sizing, koszty, cache/provider, portfolio, journal, alert outbox,
auth, SQLite, API ASGI, service pipeline i backtest. Prawdziwy provider ma osobny zestaw
testów kontraktowych poza CI oraz fixtures nagrane bez sekretów.

Przegląd ryzyk i wykonane poprawki opisuje
[audyt techniczny z 2026-10-15](AUDIT_2026-10-15.md). Testy objęły m.in. limity list API,
uprawnienia i integralność backupu, retry providera, cache krótkich serii, blokadę
równoległych skanów oraz przypisanie ceny OCR do nagłówka wykresu.

Lokalne testy E2E uruchamiają tymczasowy serwer ASGI na wolnym porcie, aby prawdziwa
przeglądarka mogła zainstalować Service Workera i pobrać jego zasoby. Używają Chromium
Playwright, a gdy jego binarium nie jest dostępne na macOS, uruchamiają Google Chrome przez
LaunchServices (`open`) i łączą się z nim przez CDP. Ten sposób omija awarię Chrome w
`HIServices/TransformProcessType`, która występuje przy bezpośrednim uruchomieniu binarium
aplikacji. Jeśli sandbox blokuje lokalne porty, testy E2E są pomijane; pełną kontrolę można
wykonać z normalnego terminala.

Job E2E instaluje Chromium przez Playwright i sprawdza dashboard w prawdziwej przeglądarce,
w tym stored-XSS oraz brak prywatnych endpointów w Cache Storage. Workflow Security uruchamia
`pip-audit` i CodeQL. Przyspieszony test księgowości PAPER:

```bash
python -m trading_helper.main paper-soak --cycles 1000
python scripts/auto_paper_trader.py --initial-cash 100 --once
```

Nie zastępuje on rzeczywistego 14-dniowego testu czasu pracy. Jego stan zbiera watchdog i
udostępnia `GET /soak/status`.

Definition of Done: kod, happy/error tests, dokumentacja, lint, coverage i działający
scenariusz. Target bieżący >=70%, docelowy >=80%. Soak test 14 dni pozostaje osobnym
kryterium operacyjnym.
