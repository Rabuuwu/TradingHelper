# Architektura

## Przepływ

```text
IB Gateway / TWS
      │
      │ TWS API socket
      ▼
IBKR Adapter ───────► Portfolio Cache
      │                    │
      ▼                    ▼
Market Data ──► Scanner ─► Signal Engine
                  │             │
                  ▼             ▼
              Indicators    Risk Manager
                  │             │
                  └──────┬──────┘
                         ▼
                  Decision Snapshot
                    │          │
                    ▼          ▼
                  SQLite      ntfy
                    │
                    ▼
               FastAPI / UI
```

## Granice modułów

### `ibkr/`
Jedyny moduł znający szczegóły TWS API. Nie może zawierać logiki scoringu ani strategii. V1 jest read-only.

### `scanner/`
Czysta logika analityczna. Przyjmuje DataFrame OHLCV i zwraca wynik. Dzięki temu można użyć tego samego kodu w live scannerze i backteście.

### `risk/`
Wylicza wielkość pozycji i ryzyko. Nie pobiera danych z sieci.

### `alerts/`
Adapter ntfy. Otrzymuje gotową wiadomość/zdarzenie i je publikuje.

### `database.py`
Persistence SQLite. Kod strategii nie powinien pisać SQL bezpośrednio.

### `api.py`
Warstwa prezentacji. Nie zawiera strategii.

## Zasada read-only

W V1 nie istnieje warstwa order execution. Jeżeli kiedyś powstanie, ma być oddzielnym modułem z osobną flagą feature, osobnymi testami i osobnym przeglądem bezpieczeństwa.

## Procesy

Pierwsza wersja może działać jako jeden proces Python. W przyszłości można rozdzielić collector/synchronizer, scanner, API/dashboard i scheduler. Na pojedynczym komputerze i SQLite monolit modularny jest prostszy i wystarczający.
