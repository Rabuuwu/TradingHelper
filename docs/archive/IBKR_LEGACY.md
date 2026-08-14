# Historyczna integracja IBKR

Pierwsze wersje TradingHelper zawierały aktywny adapter `ibapi`, synchronizację rachunku
i instrukcje IB Gateway/TWS. W wersji 0.4 aktywna integracja została usunięta podczas
migracji do architektury broker-independent.

Kod pozostaje dostępny w historii Git (do wersji 0.3), ale nie jest instalowany,
importowany ani wymagany do uruchomienia aplikacji. Ewentualny przyszły adapter IBKR
może powstać wyłącznie jako opcjonalny `MarketDataProvider`; nie może synchronizować
zleceń ani być wymagany przez core.

Profil kosztów o nazwie `ibkr` nie jest integracją. To wyłącznie konfigurowalny model
szacowania kosztów ręcznie wykonywanej transakcji.
