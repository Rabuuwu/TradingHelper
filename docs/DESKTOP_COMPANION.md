# Desktop Companion

Na macOS zalecana jest teraz kompletna aplikacja desktopowa z dashboardem w osadzonym
oknie, lokalnym API, schedulerem i panelem OCR:

```bash
bash scripts/build_macos_app.sh
open dist/macos/TradingHelper.app
```

Po zbudowaniu aplikację można otwierać z Findera bez Terminala. Konfiguracja i baza
pozostają w `~/Library/Application Support/TradingHelper`. Budowanie wymaga macOS,
środowiska `.venv` i Xcode Command Line Tools; aplikacja nie jest podpisana do dystrybucji.
Helper OCR jest kompilowany podczas budowania aplikacji i dołączany do bundle, więc
pierwsze uruchomienie nie czeka na lokalną kompilację Swift.
Diagnostyka wykrywania OCR trafia do `~/Library/Application Support/TradingHelper/logs/desktop-app.log`;
zapisuje aplikację przeglądarki i informację, czy tytuł pasuje do TradingView, bez
zapisywania pełnych tytułów kart ani rozpoznanego tekstu. Gdy macOS zwraca pusty
tytuł okna (co zdarza się w Firefoxie), aplikacja lokalnie sprawdza tekst z widocznego
okna i kontynuuje tylko wtedy, gdy OCR potwierdzi TradingView.

## Aplikacja desktopowa na Windows

Build możesz uruchomić w PowerShell na Windows z zainstalowanym Pythonem 3.12:

```powershell
./scripts/build_windows_app.ps1
```

Wynikiem jest `dist/windows/TradingHelper-windows-x64.zip`. Możesz też pobrać ten
artifact z ukończonego workflow **Windows desktop build** w GitHub Actions. Rozpakuj
całe archiwum do jednego folderu i uruchom `TradingHelper.exe`. Aplikacja osadza
dashboard w oknie WebView2; jeśli runtime WebView2 nie jest dostępny w systemie,
zainstaluj Microsoft Edge WebView2 Runtime.

Windowsowe dane użytkownika znajdują się w `%APPDATA%\TradingHelper`, w tym ustawienia,
baza SQLite i `logs\desktop-app.log`. Aktualizacja aplikacji nie usuwa tych danych.
Lokalny OCR okna TradingView działa wyłącznie na macOS; na Windows dashboard działa,
ale panel OCR informuje o niedostępności tej funkcji.

Niższe instrukcje opisują starszy, lekki companion działający z osobnym centralnym API.

Opcjonalny klient Tkinter korzysta z centralnego API, a na macOS może dodatkowo lokalnie
odczytywać tekst z wybranego okna przeglądarki. OCR jest tylko podglądem widocznych
informacji: nie wysyła ani nie zapisuje zrzutów, tekstu, symboli lub cen i nie zasila
sygnałów, strategii ani zleceń. Wartość jest przybliżonym wynikiem OCR — sprawdź ją na
wykresie. Companion nie zawiera logiki transakcyjnej.

Obsługuje ONLINE/OFFLINE/AUTH ERROR, automatyczny reconnect, top setups, portfolio,
mini mode i opcjonalne Always On Top.

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

## Odczyt ceny z widocznego wykresu (macOS)

Uruchom companion na Macu i otwórz TradingView w obsługiwanej przeglądarce. Companion
automatycznie wyszukuje widoczne okno z „TradingView” w tytule i odczytuje je co około
2,5 sekundy. Nie trzeba wybierać okna ani włączać OCR. Jeśli masz kilka otwartych okien
TradingView, odczytywane jest pierwsze widoczne okno zwrócone przez macOS. Companion
czyta wyłącznie okna przeglądarek rozpoznane po tytule TradingView; przy braku takiego
okna czeka i ponawia wykrywanie.

OCR używa lokalnego frameworka Vision z macOS; przy pierwszym użyciu macOS może poprosić
o dostęp do nagrywania ekranu. Przyznaj go aplikacji, z której uruchamiasz companion (na
przykład Terminalowi), w **Ustawienia systemowe → Prywatność i ochrona → Nagrywanie
ekranu**, a potem uruchom companion ponownie. Przy błędzie dostępu automatyczne próby
wznawiają się co 10 sekund.

Funkcja wymaga macOS 12 lub nowszego. W aplikacji desktopowej helper jest dołączony
do paczki; uruchomienia developerskie kompilują go do `~/Library/Caches/TradingHelper`
przy pierwszym użyciu i ponownie po zmianie źródła. Na Windows/Linux panel
OCR poinformuje, że funkcja wymaga macOS; odczyt się tam nie uruchomi.

Rozpoznane dane i obraz pozostają wyłącznie w pamięci companionu. Warunki TradingView
ograniczają użycie danych do wyświetlania; ten podgląd nie służy do zautomatyzowanego
przetwarzania, generowania sygnałów ani podejmowania decyzji transakcyjnych.
