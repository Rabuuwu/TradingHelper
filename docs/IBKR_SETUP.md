# IBKR — konfiguracja Paper Trading i TWS API

## Założenie

Na serwerze Linux preferujemy **IB Gateway**, ponieważ jest lżejszy i przeznaczony głównie do pracy z API. TWS może być wygodniejszy podczas pierwszej konfiguracji i diagnostyki.

## 1. Konto Paper

Development prowadzimy na Paper Trading.

## 2. IB Gateway / TWS

Pobierz aktualną wersję Stable albo Latest z oficjalnej strony Interactive Brokers dla Linuxa.

| Program | Live | Paper |
|---|---:|---:|
| TWS | 7496 | 7497 |
| IB Gateway | 4001 | 4002 |

Port zawsze musi zgadzać się z konfiguracją samego TWS/IB Gateway.

## 3. Ustawienia API

W Global Configuration → API → Settings:

- włącz socket clients,
- **Read-Only API pozostaw włączone** dla TradingHelper V1,
- ogranicz połączenia do localhost,
- sprawdź Socket Port,
- podczas diagnostyki można włączyć API message log.

## 4. Oficjalny Python TWS API

Pobierz oficjalną paczkę TWS API od IBKR, rozpakuj ją, a następnie z katalogu `source/pythonclient`:

```bash
python -m pip install .
```

Lub użyj:

```bash
./scripts/install_ibapi.sh ~/IBJts/source/pythonclient
```

## 5. `.env`

Dla IB Gateway Paper:

```dotenv
IBKR_HOST=127.0.0.1
IBKR_PORT=4002
IBKR_CLIENT_ID=17
IBKR_PAPER_TRADING=true
IBKR_READ_ONLY=true
```

## 6. Dane rynkowe

Nie zakładamy, że konto ma realtime. TradingHelper ma raportować tryb danych. Dla wielu instrumentów realtime/historical przez API wymaga odpowiednich uprawnień/subskrypcji. Na etapie uruchomienia możemy pracować z delayed data, jeśli jest dostępne.

## 7. Reconnect i sesje

TWS/IB Gateway wymagają okresowych restartów/ponownego uwierzytelnienia. Aplikacja ma mieć reconnect, healthcheck i alert o utracie połączenia.

## Oficjalne źródła

- https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/
- https://ibkrcampus.com/campus/trading-lessons/installing-configuring-tws-for-the-api/
- https://ibkrcampus.com/campus/ibkr-api-page/market-data-subscriptions/
