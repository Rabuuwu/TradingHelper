# Bezpieczeństwo

Twarda zasada: TradingHelper nie wykonuje transakcji. Nie ma loginu brokera, API XTB,
scrapingu, klikania, `placeOrder`, auto-buy ani auto-sell.

Sekrety providera, ntfy, hash hasła i session secret są tylko w `.env`. Public settings
nie zwracają sekretów. Hasło jest weryfikowane bcrypt; sesja używa losowego tokenu w
HttpOnly/SameSite cookie, `Secure` pod HTTPS. Sesje w pamięci wygasają po 24 godzinach.

Domyślnie API słucha na `127.0.0.1`. Rekomendowany remote access to Tailscale. Przy
nasłuchu na prywatnym interfejsie włącz auth. Dostęp publiczny wymaga reverse proxy,
HTTPS, firewall/rate limiting i osobnego przeglądu bezpieczeństwa.

PWA nie cache'uje endpointów sygnałów/statusu i pokazuje SERVER OFFLINE. Każdy sygnał
ujawnia provider, timestamp i delayed/stale warnings.
