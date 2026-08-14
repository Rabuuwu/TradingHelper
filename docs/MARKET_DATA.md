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
limit 8 requestów/minutę, cache SQLite i obsługę HTTP 429. Darmowy plan ma limity, które
mogą się zmieniać; przed użyciem należy sprawdzić aktualny cennik i dostępność instrumentu.
Pole `MARKET_DATA_DELAY_MINUTES` pozwala jawnie oznaczyć feed jako opóźniony. Nawet przy
pustym polu aplikacja nadal wykrywa nieaktualność na podstawie czasu ostatniej świecy.

Nowy provider implementuje kontrakt w `market_data/provider.py`, pobiera sekret wyłącznie
z `.env` i musi mieć testy z mockiem bez prawdziwych requestów w CI. Broker nie jest
providerem wymaganym przez system.
