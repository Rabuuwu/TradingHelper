# Cele

TradingHelper to broker-independent, single-user assistant działający stale na Linuxie.
Ma obserwować rynek przez wymienny provider danych, tworzyć audytowalne sygnały,
monitorować ręczne/paper pozycje, prowadzić journal i dostarczać stan wszystkim klientom.

## Kryterium MVP

- działa offline na sample data bez brokera,
- pełny cykl provider -> cache -> signal -> API/PWA działa po restarcie,
- pozycje manual/paper mają P/L i wirtualny trailing stop,
- ntfy działa bez otwartego dashboardu,
- stare/opóźnione dane są zawsze oznaczone,
- żadna ścieżka nie wykonuje transakcji,
- testy, lint i dokumentacja są zielone.

## Poza zakresem

Automatyczne zlecenia, logowanie do XTB, nieoficjalne API brokera, scraping/klikanie,
HFT, lokalne LLM oraz publiczne wystawienie bez TLS/auth.
