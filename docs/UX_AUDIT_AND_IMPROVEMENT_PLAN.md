# Audyt UX i plan uproszczenia TradingHelper

Status planu: uproszczony interfejs wdrożony; część kontroli automatycznych i wizualnych czeka na dostępne środowisko testowe.

Ten dokument jest checklistą roboczą. Podczas wdrażania należy odhaczać tylko punkty
spełniające zapisane kryteria, aktualizować status i dopisywać wynik kontroli.

## Postęp wdrożenia

- [x] Główna nawigacja ma trzy codzienne widoki; watchlista, stan systemu i ustawienia są w sekcji „Więcej”.
- [x] Przebudowano pulpit, portfel, aktywność, watchlistę, ustawienia i szczegóły sygnału z responsywnym układem oraz stanami ładowania/błędu/pustych danych.
- [x] Dodano dostępne nazwy, aktywną nawigację, obsługę klawiaturą, dialogi i komunikaty formularzy; usunięto natywne `alert()`.
- [x] Błąd historii wykresu nie zasłania listy pozycji; pusty wykres opisuje brak historii portfela.
- [x] Potwierdzenie resetu PAPER pokazuje bieżącą gotówkę i liczbę otwartych pozycji.
- [x] Zaktualizowano regresje Playwright dla nawigacji, błędów, resetu, autoryzacji i XSS.
- [ ] Uruchomić pytest, ruff i scenariusze Playwright po udostępnieniu zależności oraz przeglądarki.
- [ ] Obejrzeć układ desktopowy i mobilny w prawdziwej przeglądarce; screenshoty nie zostały jeszcze wykonane.

## Zakres i stan bazowy

- [x] Sprawdzono strukturę repozytorium, README, architekturę, wymagania, roadmapę,
  operacje, bezpieczeństwo i strategię testów.
- [x] Przejrzano dashboard, portfel, dziennik, watchlistę, zdarzenia, ustawienia,
  szczegóły sygnału i mobilne style w `src/trading_helper/web/`.
- [x] Przejrzano główne endpointy i ochronę API w `src/trading_helper/api.py`.
- [x] Potwierdzono, że repozytorium nie miało lokalnych zmian przed audytem.
- [x] Sprawdzono dostępność zależności przed testami; globalnie nie ma `pytest` ani
  `ruff`, a repo nie miało własnego środowiska.
- [x] Utworzono ignorowane przez Git `.venv` i próbowano zainstalować `.[dev]`.
- [ ] Testy i lint przed zmianami były niedostępne: instalacja wymaga dostępu do
  indeksu pakietów, ale środowisko nie rozwiązuje jego hosta (`nodename nor servname
  provided`).
- [x] `python3 -m compileall -q src tests` — składnia plików Python przechodzi.

## Najważniejsze ustalenia

### Priorytet 1 — uprościć codzienny przepływ

- Dashboard zawiera głównie listę sygnałów. Nie prowadzi użytkownika od „co wymaga
  uwagi” przez wyjaśnienie ryzyka do następnego kroku.
- Sześć równorzędnych zakładek (`Pulpit`, `Portfel`, `Dziennik`, `Obserwowane`,
  `System`, `Ustawienia`) rozprasza główne zadania. Na telefonie sześć przycisków
  konkuruje o miejsce w dolnym pasku.
- Widok szczegółów sygnału łączy wykres, wskaźniki, plan, koszty, ostrzeżenia i długi
  formularz PAPER w jednym oknie. Najczęstsza decyzja nie ma wyraźnej hierarchii.
- Przycisk „Symuluj wejście” najpierw pokazuje `alert()` i odsyła do pulpitu zamiast
  otworzyć konkretny, zrozumiały przepływ.

### Priorytet 2 — wyjaśnić stan danych i konsekwencje akcji

- Karta sygnału wyróżnia score, ale nie pokazuje czasu danych ani ogólnej świeżości;
  ostrzeżenie `is_delayed` jest techniczne i występuje po angielsku. Stan stale jest
  dostępny dopiero w szczegółach/innym statusie.
- Stan serwera jest małym przyciskiem, a szczegóły zdrowia ukrywają się po kliknięciu.
  Użytkownik może pomylić połączenie z serwerem ze świeżością danych rynkowych.
- „Ustaw / resetuj PAPER” nie objaśnia na formularzu skutków zmiany kapitału. API
  odrzuca reset przy otwartych pozycjach, ale UI powinien tę regułę pokazać przed
  wysłaniem formularza i czytelnie przedstawić błąd walidacji.
- Błędy wielu operacji formularzy kończą się nieobsłużonym wyjątkiem, bez widocznego
  komunikatu przy polu lub formularzu. `alert()` używany jest też po symulacji kupna.

### Priorytet 3 — dostępność, spójność i utrzymanie

- Nawigacja nie ogłasza aktywnego widoku semantyką `aria-current`/tab; dialog sygnału
  ma przycisk zamknięcia bez dostępnej nazwy. Kontrolki wykresu i etykiety statusów
  wymagają pełnej obsługi klawiaturą i czytnikiem ekranu.
- Tłumaczenia PL/EN są niepełne: część pól i ostrzeżeń jest wpisana na sztywno po
  polsku lub angielsku.
- `app.js` jest skondensowany do bardzo długich linii i miesza transport API,
  renderowanie, nawigację oraz obsługę formularzy; zwiększa to ryzyko regresji.
- Wykres zależy od zewnętrznego CDN. Przy braku biblioteki pojawia się techniczny
  komunikat; trzeba zapewnić czytelny fallback i utrzymać wyraźne oznaczenie źródła.
- Widoki list nie pokazują spójnych stanów ładowania, błędu i odświeżania. Zdarzenia
  mogą odświeżyć dashboard/status, lecz pozostałe ekrany nie mają jednolitej reguły.

## Docelowy, prostszy układ

- [ ] **Pulpit** jako ekran startowy: stan połączenia, świeżość danych, wymagające
  uwagi pozycje/ostrzeżenia i krótka lista najlepszych setupów z jasnym CTA „Szczegóły”.
- [ ] **Portfel** jako jeden widok pozycji ręcznych i PAPER, z czytelnym rozdzieleniem
  trybu, wartości, wyniku i alertów wyjścia. Reset konta PAPER w sekcji zaawansowanej
  z potwierdzeniem i komunikatem o otwartych pozycjach.
- [ ] **Aktywność** jako połączony widok dziennika i zdarzeń, z prostym filtrem
  „Transakcje / System”, zamiast dwóch osobnych głównych zakładek.
- [ ] Watchlista jako filtr/sekcja pulpitu lub widok drugorzędny, bez utraty możliwości
  dodawania i usuwania symboli.
- [ ] Ustawienia techniczne i status zdrowia w widoku drugorzędnym. Na małym ekranie
  najwyżej 4 główne pozycje nawigacji; reszta dostępna w „Więcej”.
- [ ] Szczegóły sygnału w dwóch poziomach: najpierw decyzja i ryzyko (świeżość, score,
  entry/SL/TP, R:R, ostrzeżenia), dalej rozwijane wykres/wskaźniki/koszty. Symulacja
  PAPER dostępna jako osobny, wyraźny krok z podsumowaniem kwoty i ryzyka.

## Checklist wdrożeniowa

### A. Fundament interfejsu

- [x] Uporządkować `index.html` i nawigację: trzy główne widoki oraz dostęp do reszty w „Więcej”;
  zachować dostęp do każdej istniejącej funkcji.
- [x] Dodać wspólny komponent komunikatów: ładowanie, brak danych, błąd, sukces i
  ponowienie; usunąć natywne `alert()` z normalnych przepływów.
- [ ] Rozdzielić logikę `app.js` na czytelne sekcje/moduły (API, stan/nawigacja,
  renderowanie widoków i formularze) bez dodawania frameworka bez potrzeby.
- [x] Zapewnić etykiety PL/EN i formatowanie kwot, dat, statusów oraz wartości
  nieznanych; nie pokazywać statusu nieaktualnego jako aktualnego.
- [x] Poprawić semantykę nagłówków, labeli, focus, dialogów i obsługę
  klawiaturą; oznaczać aktywną nawigację i komunikaty statusu dostępnie.
- [ ] Sprawdzić wąski telefon, tablet i desktop; nawigacja mobilna ma być czytelna i
  nie zasłaniać formularzy ani głównej akcji.

### B. Pulpit i sygnały

- [ ] Ustawić hierarchię pulpitu według pilności: problemy/ostrzeżenia, świeżość,
  najlepsze setupy, ostatni skan.
- [x] Dla kart pokazywać symbol, etykietę, cenę wraz z
  walutą, timestamp/provenance i zrozumiałą odznakę danych opóźnionych/starych.
- [x] Dodać wyszukiwanie watchlisty bez przeładowania ekranu; pusty stan ma
  podpowiadać dodanie symbolu lub uruchomienie skanu.
- [ ] Zamienić nieprowadzący donikąd przycisk „Symuluj wejście” na akcję dostępną
  dopiero przy konkretnym setupie albo usunąć go z pulpitu.
- [ ] Uporządkować dialog szczegółów: podsumowanie i ryzyko na górze, wykres jako
  główna wizualizacja, wskaźniki/koszty w rozwijanych sekcjach, walidacja błędów.
- [x] Pokazać fallback wykresu przy braku biblioteki/CDN i informację o czasie oraz
  źródle danych bez technicznego żargonu.

### C. Portfel, symulacja i aktywność

- [x] Oddzielić dane ręczne i symulowane wizualnie, bez sugerowania, że PAPER jest
  realną pozycją lub zleceniem brokerskim.
- [x] Przed resetem PAPER wyjaśnić skutek, pokazać saldo/otwarte pozycje i wymagać
  jednoznacznego potwierdzenia; błędy API prezentować przy formularzu.
- [x] Połączyć historię transakcji i dziennik zdarzeń w „Aktywności” z filtrem i
  czytelnym opisem zamiast surowych typów zdarzeń.
- [ ] Dodać przejścia kontekstowe: sygnał → symulacja/pozycja, pozycja → szczegóły,
  zdarzenie → powiązany symbol, jeśli backend ma odpowiednie dane.
- [x] Ograniczyć długie listy przez przewijanie i zachować czytelne puste
  stany.

### D. Stabilność i sprawdzenie

- [x] Zachować istniejące API, dane, historie, PWA i granicę bezpieczeństwa: aplikacja
  nie wykonuje transakcji u brokera.
- [ ] Testować błędy sieci, 401, pusty wynik, stare/opóźnione dane, wolny CDN, brak
  wykresu, błędne formularze, aktywną pozycję podczas resetu oraz reconnect SSE.
- [x] Zaktualizować testy Playwright dla uproszczonej nawigacji i głównych przepływów;
  zweryfikować XSS, auth i brak cache prywatnych endpointów.
- [ ] Uruchomić `ruff check src tests`, pełne `pytest` i E2E Playwright; zapisać wynik
  oraz każdy znany limit środowiska.
- [ ] Wykonać kontrolę wizualną desktop + telefon i przejrzeć stany ładowania, błędu,
  pustej listy, ostrzeżeń oraz otwartego szczegółu sygnału.

## Kolejność realizacji

1. Fundamenty, nawigacja i komunikaty (A).
2. Pulpit i szczegóły sygnałów (B).
3. Portfel, PAPER i aktywność (C).
4. Dostępność, regresje i pełna weryfikacja (D).

## Notatki z weryfikacji

- `python3 -m pip install -e '.[dev]'`: nie powiodło się, bo przy instalacji
  `setuptools>=69` pip nie mógł rozwiązać hosta indeksu pakietów. Próba nie zmieniła
  zależności projektu; lokalne `.venv` jest ignorowane przez Git.
- `ruff check src tests`: nieuruchomione — `ruff` nie jest zainstalowany, a brak
  dostępu do indeksu uniemożliwił instalację.
- `pytest -q`: nieuruchomione — `pytest` nie jest zainstalowany, a brak dostępu do
  indeksu uniemożliwił instalację.
- `python3 -m compileall -q src tests`: zakończone poprawnie.
- `git diff --check` — bez błędów whitespace.
- JavaScript `app.js` sprawdzony parserem JavaScriptCore — poprawna składnia.
- HTML sprawdzony parserem: 76 unikalnych ID, brak niejawnego typu przycisków; tytuł dialogu sygnału jest dynamicznie renderowany przed otwarciem.
- Kontroli wizualnej w przeglądarce nie wykonano; screenshotów nie zapisano.
