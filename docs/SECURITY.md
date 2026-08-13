# Bezpieczeństwo

## Sekrety

Do GitHub nie trafiają hasła IBKR, tokeny, prywatne topic ntfy, `.env`, lokalne bazy danych ani logi zawierające dane rachunku.

## IBKR

V1 używa połączenia read-only. W ustawieniach TWS/IB Gateway pozostawiamy Read-Only API. Kod V1 nie implementuje wykonywania zleceń.

## Sieć

FastAPI domyślnie nasłuchuje tylko na `127.0.0.1`. Dostęp z telefonu/poza domem będziemy realizować dopiero przez kontrolowany mechanizm, a nie przez przypadkowe wystawienie portu do internetu.

## Powiadomienia

Topic ntfy traktujemy jak sekret, jeśli korzystamy z publicznego serwera. Używamy długiej losowej nazwy lub później self-hosted ntfy z uwierzytelnianiem.

## Logowanie

Nie logujemy pełnych danych uwierzytelniających. API logów IBKR nie publikujemy bez anonimizacji.

## Dependency policy

Oficjalne TWS API pobieramy z IBKR; nie zastępujemy go losowym wrapperem tylko dlatego, że jest łatwiejszy do zainstalowania.
