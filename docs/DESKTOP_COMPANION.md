# Desktop Companion

Opcjonalny lekki klient Tkinter dla Windows/Linux korzysta wyłącznie z centralnego API.
Nie zawiera skanera ani logiki transakcyjnej. Obsługuje ONLINE/OFFLINE/AUTH ERROR,
automatyczny reconnect, top setups, portfolio, mini mode i opcjonalne Always On Top.

```bash
TRADING_HELPER_SERVER_URL=http://100.x.x.x:8787 trading-helper-companion
```

Kliknięcie Dashboard otwiera PWA. Gdy serwer zwróci `AUTH ERROR`, Companion pokazuje
formularz logowania. Hasło nie jest zapisywane na dysku; klient zachowuje wyłącznie
cookie sesji w pamięci procesu. Po zalogowaniu automatycznie ponawia pobranie stanu.

Na komputerze klienckim trzeba sklonować repozytorium i zainstalować sam pakiet. Backend,
scanner ani baza nie muszą i nie powinny być tam uruchamiane:

```bash
git clone https://github.com/Rabuuwu/TradingHelper.git
cd TradingHelper
python -m venv .venv
source .venv/bin/activate
pip install -e .
TRADING_HELPER_SERVER_URL=http://100.x.x.x:8787 trading-helper-companion
```

Na Linuxie GUI wymaga systemowego pakietu `python3-tk`. Windowsowy instalator Pythona
zwykle zawiera Tkinter. System tray i natywne popupy pozostają rozszerzeniem; Always On
Top, Mini Mode, reconnect, status, setupy, portfolio i logowanie działają bez nich.
Companion nigdy nie wykonuje BUY/SELL.
