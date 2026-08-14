# Operacje 24/7

Tryby: `scan-once` (jeden skan), `worker` (scheduler), `api` (tylko web), `run`
(zalecane: scheduler + API/PWA), `backup` i `self-check`.

Health: `/health` sprawdza proces, `/ready` bazę/provider, `/status` pokazuje uptime,
market, provider, scheduler oraz timestampy zapisane w system state. Event log odpowiada
na pytanie, czy scanner i alerty działały w nocy. SSE `/events/stream` aktualizuje klientów.

## Tailscale first

1. Zainstaluj Tailscale na serwerze i urządzeniach.
2. Ustaw `APP_HOST` na adres Tailscale serwera albo kontrolowane `0.0.0.0` z firewallem.
3. Włącz `AUTH_ENABLED=true`.
4. Otwieraj `http://100.x.x.x:8787` wyłącznie w prywatnym tailnecie.

Hash hasła generuj interaktywnie przez
`python -m trading_helper.main hash-password`, aby hasło nie trafiło do historii shella.

Nie otwieraj portu routera. Dla domeny publicznej zastosuj HTTPS reverse proxy i dodatkowe
zabezpieczenia. Tailscale i auth nie zastępują aktualizacji systemu oraz backupu.

## Monitoring i recovery

Monitoruj `/ready`, wiek `last_market_data_update`, `last_successful_scan`,
`last_position_monitor`, `last_notification`, stan schedulera, miejsce na dysku i ntfy.
Systemd restartuje proces po awarii. Alerty PENDING/FAILED są ponawiane do pięciu razy.

`GET /soak/status` raportuje kolejne dni zdrowej pracy. Wynik `PASSED` pojawia się wyłącznie
po 14 różnych, kolejnych dniach bez obserwacji UNHEALTHY. Test przyspieszony nie zastępuje
rzeczywistego upływu czasu.

Backup SQLite wykonuje `python -m trading_helper.main backup`; timer robi go codziennie
i stosuje retencję z YAML. Przy odtwarzaniu zatrzymaj usługę, zachowaj uszkodzoną bazę,
skopiuj backup do ścieżki `TRADING_HELPER_DB` i ponownie uruchom usługę.
