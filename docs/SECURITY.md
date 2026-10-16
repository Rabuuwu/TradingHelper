# Bezpieczeństwo

Twarda zasada: TradingHelper nie wykonuje transakcji. Nie ma loginu brokera, API XTB,
scrapingu, klikania, `placeOrder`, auto-buy ani auto-sell.

Sekrety providera, ntfy, hash hasła i session secret są tylko w `.env`. Public settings
nie zwracają sekretów. Hasło jest weryfikowane bcrypt; sesja używa losowego tokenu w
HttpOnly/SameSite cookie, `Secure` pod HTTPS. W SQLite przechowywany jest wyłącznie HMAC
tokenu wykorzystujący `SESSION_SECRET`; sesje przeżywają restart i wygasają po 24 godzinach.
Pięć błędnych prób dla pary użytkownik/klient w 15 minut powoduje blokadę HTTP 429.

Listy dziennika i alertów mają limit 1–500 rekordów. `/ready` pozostaje publicznym
endpointem diagnostycznym, ale przy błędzie bazy zwraca wyłącznie ogólny stan
`database: unavailable`; szczegóły trafiają do logu serwera. Polecenie generowania
hasha zawsze pobiera hasło przez ukryty prompt, bez argumentu CLI.

Frontend escapuje dane API przed wstawieniem do HTML. Service worker cache'uje wyłącznie
jawnie dozwolone statyczne assety i nigdy nie zapisuje prywatnych odpowiedzi API.

Domyślnie API słucha na `127.0.0.1`. Rekomendowany remote access to Tailscale. Przy
nasłuchu na prywatnym interfejsie włącz auth. Dostęp publiczny wymaga reverse proxy,
HTTPS, firewall/rate limiting i osobnego przeglądu bezpieczeństwa.

Backupy SQLite są zapisywane z uprawnieniami `0600`, w katalogu `0700`; po utworzeniu
przechodzą `PRAGMA integrity_check`, a retencja nie może być ujemna. Uprawnienia
chronią przed innymi kontami lokalnymi, ale nie szyfrują dysku ani kopii. Używaj
szyfrowania dysku/backupów i przechowuj kopie poza hostem.

PWA nie cache'uje endpointów sygnałów/statusu i pokazuje SERVER OFFLINE. Każdy sygnał
ujawnia provider, timestamp i delayed/stale warnings.
