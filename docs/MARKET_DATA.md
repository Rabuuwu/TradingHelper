# Market data

`MarketDataProvider` udostępnia quote, candles, symbol info/search, market status i bulk
quotes. Modele mają `source`, `timestamp`, `is_delayed`, `delay_minutes`. Cache SQLite
unika zbędnych requestów; retry ma exponential backoff. Adapter musi stosować timeout,
rate limit i zwracać wyłącznie kompletne świece.

Provider `sample` jest deterministyczny, offline i służy wyłącznie do demonstracji/CI.
Nie przedstawia prawdziwego rynku. Nieznany provider zatrzymuje self-check czytelnym błędem.

Opcjonalny provider `twelve_data` korzysta z oficjalnego REST API Twelve Data. Uruchomienie:

```dotenv
MARKET_DATA_PROVIDER=twelve_data
MARKET_DATA_API_KEY=klucz_z_panelu_twelve_data
MARKET_DATA_DELAY_MINUTES=
```

Klucz jest wysyłany w nagłówku `Authorization`, nigdy w URL. Adapter ma timeout, retry,
limit 7 requestów/minutę, cache SQLite i obsługę HTTP 429. Darmowy plan ma limity, które
mogą się zmieniać; przed użyciem należy sprawdzić aktualny cennik i dostępność instrumentu.
Pole `MARKET_DATA_DELAY_MINUTES` pozwala jawnie oznaczyć feed jako opóźniony. Nawet przy
pustym polu aplikacja nadal wykrywa nieaktualność na podstawie czasu ostatniej świecy.

Ten sam adapter dostarcza kursy par walutowych do `FxRateService`. Kurs jest cache'owany
w tabeli `fx_rates` domyślnie przez 360 minut. API ujawnia kurs, źródło, timestamp i
status; przy awarii providera system korzysta z jawnie oznaczonego fallbacku YAML.

Nowy provider implementuje kontrakt w `market_data/provider.py`, pobiera sekret wyłącznie
z `.env` i musi mieć testy z mockiem bez prawdziwych requestów w CI. Broker nie jest
providerem wymaganym przez system.

## Budżet Twelve Data

Domyślny plan jest chroniony trwałym licznikiem SQLite: 800 kredytów na dobę, z czego
automatyczne zadania mogą wykorzystać 720. Pozostałe 80 stanowi rezerwę bezpieczeństwa.
Licznik przeżywa restart i jest dostępny w `/market/credits` oraz `/status`. Wyczerpanie
budżetu daje kontrolowany `ProviderRateLimited`, bez bezcelowych ponownych prób.

Cache jest izolowany przez `data_source`; uruchomienie realnego providera usuwa wyłącznie
stare SAMPLE candles/quotes, nigdy portfolio, trades ani sygnały. TTL: 15m=12 minut,
1h=55 minut, 4h=3h50m, 1d=20 godzin. Status sesji USA jest liczony lokalnie w strefie
`America/New_York`, więc odświeżanie dashboardu nie zużywa kredytów.

Scheduler Twelve Data wykonuje skan nie częściej niż raz na godzinę podczas sesji oraz
jeden skan po zamknięciu. Monitoring pozycji poza sesją działa raz dziennie. Przy pięciu
symbolach typowy koszt skanera to około 45 kredytów dziennie, plus wykresy na żądanie i
quote otwartych pozycji.
