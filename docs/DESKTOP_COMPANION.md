# Desktop Companion

Opcjonalny lekki klient Tkinter dla Windows/Linux korzysta wyłącznie z centralnego API.
Nie zawiera skanera ani logiki transakcyjnej. Obsługuje ONLINE/OFFLINE/AUTH ERROR,
automatyczny reconnect, top setups, portfolio, mini mode i opcjonalne Always On Top.

```bash
TRADING_HELPER_SERVER_URL=http://100.x.x.x:8787 trading-helper-companion
```

Kliknięcie Dashboard otwiera PWA. Przy auth klient udostępnia metodę login, ale obecny
minimalny interfejs nie ma jeszcze formularza logowania ani system tray/popups — są to
świadomie pozostawione rozszerzenia po stabilizacji API. Companion nigdy nie wykonuje
BUY/SELL.
