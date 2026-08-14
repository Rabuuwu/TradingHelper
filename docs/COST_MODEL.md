# Cost model

Profile `xtb`, `ibkr` i `custom` w YAML są wyłącznie edytowalnymi założeniami kosztów,
nie integracjami. Stawki zmieniają się — użytkownik musi je zweryfikować i aktualizować.

Model obsługuje commission buy/sell, minimum fee, FX %, spread i slippage. Wynik zawiera
gross expected profit, fees, FX, spread, slippage, total cost, net profit oraz udział
kosztów w oczekiwanym zysku. Feasibility odrzuca plan jako `TRADE_REJECTED_COSTS`, gdy
próg YAML zostanie przekroczony. Manualne `fx_rates_to_portfolio` są awaryjnym
fallbackiem; brak kursu generuje warning.

Dashboard zawsze pokazuje walutę instrumentu przy cenie źródłowej. Użytkownik może
wybrać w Settings walutę prezentacji spośród kursów `fx_rates_to_portfolio`; API zwraca
równolegle `display_values`, walutę i użyty współczynnik. Przy providerze Twelve Data
aplikacja pobiera parę walutową, zapisuje ją w SQLite i pokazuje źródło, timestamp
oraz status `LIVE` lub `STALE`. Fallback ma jawny status `YAML_CONFIG/FALLBACK`.
