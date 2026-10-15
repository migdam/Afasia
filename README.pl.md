# Afasia: ćwiczenia mowy dla osób z afazją

[🇬🇧 English version](README.md)

Aplikacja internetowa do ćwiczenia słów i zdań po udarze lub urazie mózgu. Osoby z afazją ćwiczą w niej samodzielnie, równolegle z terapią u logopedy, a terapeuci widzą, kto ćwiczy. Interfejs jest dostępny po polsku i po angielsku.

> **Stan: wczesna faza rozwoju. Nie do użytku klinicznego.**
> Ćwiczenia są tymczasowe i nie sprawdził ich jeszcze żaden logopeda, ćwiczenia są po polsku i po angielsku, a braki wymienione w części [Znane ograniczenia](#znane-ograniczenia) nadal istnieją. Postęp prac jest w [`loop/BACKLOG.md`](loop/BACKLOG.md).

## Co już działa

Konta, sesje ćwiczeń, informacja zwrotna, wyniki, wykres postępów i panel administratora są sprawdzane testami automatycznymi (zob. [Rozwój](#rozwój)). Eksport, planowanie sesji i układ na telefon nie mają jeszcze testów.

- **Konta.** Rejestracja, logowanie, wylogowanie i zmiana hasła na stronie Konto. Odświeżenie strony nie kończy zalogowania. Hasła są haszowane algorytmem bcrypt, a logowanie korzysta z tokenów JWT. Zalogowanie kończy się po 30 minutach bez korzystania z aplikacji, a najpóźniej 12 godzin po zalogowaniu.
- **Sesje ćwiczeń** po 5–50 ćwiczeń, na poziomie łatwym, średnim lub trudnym:
  - *Nazywanie słów*: przeczytaj krótki opis („A pet that barks and wags its tail”) i wpisz słowo.
  - *Uzupełnianie zdań*: wybierz słowo, które kończy zdanie.

  Po każdej odpowiedzi pojawia się „Poprawnie! Świetna robota!” albo prawidłowa odpowiedź. Serwer liczy wynik sesji, gdy przyjdzie ostatnia odpowiedź. Ćwiczenia z błędną odpowiedzią wracają w następnej sesji tego samego rodzaju, poziomu i języka; zajmują w niej najwyżej połowę. Ćwiczenia z dobrą odpowiedzią wracają po coraz dłuższych przerwach (2, 4, 8, potem 16 dni) albo po 1 dniu, jeśli potrzebna była pomoc.
- **Postępy.** Punkty za poprawne odpowiedzi, serie dni z ćwiczeniami, których nie przerywa dzień czy dwa przerwy, trzy odznaki (pierwsza sesja, seria 7 i 30 dni), strona postępów z podsumowaniem i wykresem trafności oraz eksport do CSV i PDF.
- **Planowanie.** Można zaplanować przyszłe sesje. Aplikacja jeszcze o nich nie przypomina.
- **Panel terapeuty/administratora.** Lista wszystkich pacjentów, aktywowanie i dezaktywowanie kont. Rejestracja w aplikacji zawsze tworzy konto pacjenta; konta personelu zakłada się na serwerze (zob. [Konta personelu](#konta-personelu)).
- **Interfejs.** Polski i angielski, motyw jasny i ciemny, układ na telefon i komputer.

### Co jeszcze nie działa

- **Wymowa.** Odsłuchanie wzoru, nagranie, odsłuchanie siebie i własna ocena („Udało się” / „Jeszcze nie”); decyduje ocena osoby ćwiczącej. Rozpoznawanie mowy przeglądarki, jeśli jest dozwolone, tylko podpowiada, co usłyszało. Odsłuchiwanie nagrań przez logopedę nie jest jeszcze możliwe.
- **Rozpoznawanie obrazów** nie ma ćwiczeń, więc aplikacja go nie oferuje.
- **Obrazków ani nagrań** jeszcze nie ma. Ćwiczenia nazywania używają opisów.
- **Praca offline** nie jest obsługiwana: każde ćwiczenie wymaga połączenia z serwerem. Aplikacja instalowała kiedyś service worker, który zatrzymywał starą wersję kodu i zapamiętywał dane osobowe; został wycofany, a `sw.js` usuwa go wraz z jego pamięcią podręczną z przeglądarek, które wciąż go mają.

## Szybki start (praca nad kodem)

Potrzebujesz Pythona 3.11 i Gita.

```bash
git clone <to repozytorium>
cd Afasia

# Backend: http://localhost:8000 (dokumentacja API: http://localhost:8000/docs)
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.template ../.env     # potem ustaw SECRET_KEY: openssl rand -hex 32
python -m app.main
```

```bash
# Frontend, w drugim terminalu: http://localhost:3000
cd frontend
python3 -m http.server 3000
```

Otwieraj aplikację pod adresem `http://localhost:3000`, a nie `http://127.0.0.1:3000`. Ciasteczko logowania pochodzi z `localhost:8000`, a przeglądarka odsyła je tylko stronom z tej samej witryny (domyślnie dozwolone są też tylko adresy `localhost`).

Frontend znajduje API przez `frontend/js/config.js`. Jego Content-Security-Policy (w `frontend/index.html`) pozwala stronie łączyć się tylko z własnym adresem i lokalnymi portami deweloperskimi, więc skrypt wstrzyknięty do strony nie wyśle danych gdzie indziej. Jeśli API stoi pod innym adresem, dopisz go tam do `connect-src`. Konfiguracja Dockera trzyma API pod tym samym adresem, a nginx wysyła dodatkowo surowszą politykę.

Backend czyta `.env` z katalogu głównego repozytorium, niezależnie od tego, skąd go uruchomisz. Nieznane mu ustawienia pomija, więc ten sam plik służy też Docker Compose. Podczas pracy nad kodem bazą danych jest SQLite (`backend/aphasia_app.db`).

## Uruchamianie w Dockerze

Potrzebujesz Dockera z Compose v2.

```bash
cp .env.template .env           # ustaw SECRET_KEY i POSTGRES_PASSWORD
docker compose up --build
```

- Aplikacja: http://localhost:3000. nginx serwuje frontend i przekazuje `/api` do backendu.
- API bezpośrednio: http://localhost:8000, tylko z tego komputera. Backend ufa nagłówkowi `X-Forwarded-For` od nginx, żeby rozróżniać klientów (`FORWARDED_ALLOW_IPS`), więc jego port nie może być dostępny z zewnątrz.
- Dane są w PostgreSQL, w wolumenie Dockera.
- Bez tych dwóch sekretów `docker compose up` się nie uruchomi.
- Każde ustawienie z tabeli poniżej jest brane z `.env`, z wyjątkiem `DATABASE_URL`, `UPLOAD_DIR`, `HOST` i `PORT`, które ustala konfiguracja Dockera. `.env.template` włącza `DEBUG`; poza własnym komputerem ustaw `DEBUG=false`.
- Za proxy, które podgląda ruch TLS, ustaw `PIP_CA_FILE` na jego pakiet certyfikatów CA, żeby budowanie obrazu mogło pobrać pakiety z PyPI.

`scripts/docker-smoke.sh` buduje i uruchamia osobną kopię całości, rejestruje się i loguje przez nginx, a potem wszystko usuwa.

## Konta personelu

Rejestracja w aplikacji zawsze tworzy konto pacjenta. Konta administratorów i terapeutów zakłada się na serwerze, w katalogu `backend/`, z tymi samymi ustawieniami co backend:

```bash
python -m app.cli create-user --username ada --email ada@example.com --role admin
python -m app.cli set-role tess therapist      # zmiana roli istniejącego konta
python -m app.cli delete-old-recordings --days 365   # usuń teraz nagrania starsze niż rok
```

`create-user` pyta o hasło, które musi mieć co najmniej 12 znaków, więc nie trafia ono do historii poleceń. W Dockerze uruchom te same polecenia jako `docker compose exec backend python -m app.cli …`.

## Konfiguracja

Skopiuj `.env.template` do `.env` w katalogu głównym repozytorium. Ustawienia:

| Ustawienie | Domyślnie | Znaczenie |
|---|---|---|
| `SECRET_KEY` | (wymagane) | Podpisuje tokeny logowania. Co najmniej 32 losowe bajty (`openssl rand -hex 32`). Aplikacja nie uruchomi się z krótszym kluczem ani z przykładem z `.env.template`. |
| `DATABASE_URL` | `sqlite:///./aphasia_app.db` | Dowolny adres SQLAlchemy, np. `postgresql://użytkownik:hasło@host/baza` |
| `BACKEND_CORS_ORIGINS` | `http://localhost:3000,http://localhost:8000` | Adresy stron (oddzielone przecinkami), które mogą wywoływać API |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Po ilu minutach bez korzystania z aplikacji kończy się zalogowanie (aplikacja odnawia je, gdy jest używana) |
| `LOGIN_MAX_HOURS` | `12` | Po ilu godzinach od zalogowania zalogowanie kończy się mimo wszystko |
| `LOGIN_MAX_FAILURES`, `LOGIN_MAX_FAILURES_PER_ACCOUNT`, `LOGIN_LOCK_MINUTES` | `5`, `50`, `15` | Ile błędnych haseł wolno podać dla jednej nazwy użytkownika z jednego adresu klienta oraz dla konta ze wszystkich adresów łącznie w ciągu tylu minut; potem logowanie musi poczekać (429) |
| `RECORDING_RETENTION_DAYS` | `0` | Usuwaj nagrania starsze niż tyle dni, przy starcie i potem codziennie; `0` przechowuje je, dopóki osoba ich nie usunie lub nie usunie konta. Przekazywane także przez Docker Compose |
| `LEVEL_WINDOW`, `LEVEL_UP_SCORE`, `LEVEL_DOWN_SCORE` | `3`, `85`, `50` | Kiedy tablica proponuje inny poziom: po tylu ukończonych sesjach jednego rodzaju na jednym poziomie trudniejszy, gdy ich średnia to co najmniej `LEVEL_UP_SCORE` %, a łatwiejszy, gdy jest niższa niż `LEVEL_DOWN_SCORE` %. Wartości tymczasowe, oczekują na ocenę kliniczną |
| `STREAK_REST_DAYS` | `2` | Ile dni przerwy z rzędu nie przerywa serii; `2` pozwala ćwiczyć w poniedziałki, środy i piątki. Wartość tymczasowa, oczekuje na ocenę kliniczną |
| `COOKIE_SECURE` | `true` | Wysyłaj ciasteczko logowania tylko przez HTTPS (przeglądarki dopuszczają też `http://localhost`). Ustaw `false` tylko do testów przez zwykłe HTTP na innym hoście. |
| `DEBUG`, `HOST`, `PORT` | `false`, `0.0.0.0`, `8000` | Opcje serwera. `.env.template` włącza `DEBUG` na potrzeby pracy nad kodem (więcej szczegółów w dziennikach i automatyczne przeładowanie); w innych miejscach zostaw go wyłączonego |
| `UPLOAD_DIR`, `MAX_UPLOAD_SIZE` | `./uploads`, 10 MB | Gdzie trafiają nagrania głosu |
| `POSTGRES_PASSWORD`, `FRONTEND_PORT`, `BACKEND_PORT`, `PIP_CA_FILE` | | Tylko dla Docker Compose |

## API

FastAPI udostępnia interaktywną dokumentację pod `/docs` i `/redoc`. Wszystkie adresy zaczynają się od `/api/v1`. Wszystkie oprócz rejestracji, logowania i wylogowania wymagają zalogowania. Rejestracja, logowanie i `/auth/refresh` ustawiają token jako ciasteczko httpOnly `access_token` (ścieżka `/api`, `SameSite=Strict`) i podają, kiedy został wydany i kiedy wygasa (`issued_at`, `expires_at`). Zwracają go też w treści odpowiedzi, z wyjątkiem odnowienia przez ciasteczko, żeby skrypty na stronie nigdy go nie widziały. Token można wysłać w nagłówku `Authorization: Bearer <token>` albo jako to ciasteczko. Żądania, które coś zmieniają za pomocą ciasteczka, muszą też mieć nagłówek `X-Requested-With`, inaczej dostają 403; to ochrona przed fałszowaniem żądań z innych stron (CSRF). Brakujący lub nieprawidłowy token daje 401. Czas jest w UTC: API wysyła go z `+00:00`, a czas bez przesunięcia traktuje jako UTC.

| Obszar | Adresy |
|---|---|
| Konta | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh` (odnawia zalogowanie), `POST /auth/logout` (kończy to zalogowanie na serwerze i usuwa ciasteczko; inne urządzenia pozostają zalogowane), `POST /users/password` (zmiana hasła: wymaga obecnego; pozostałe zalogowania się kończą, a to dostaje nowy token) |
| Sesje | `POST /therapy/sessions` (`num_exercises` od 1 do 50; formularz oferuje od 5 do 50), `GET /therapy/sessions`, `GET /therapy/sessions/{id}`, `GET /therapy/sessions/{id}/exercises` |
| Wybór słowa | `POST /therapy/exercises/{id}/choices`: cztery słowa do wyboru zamiast pisania (nazywanie); poprawna odpowiedź wybrana z listy zachowuje najwyżej połowę punktów (oczekuje na ocenę kliniczną) |
| Kafelki z literami | `POST /therapy/exercises/{id}/tiles`: litery odpowiedzi w losowej kolejności, do ułożenia słowa zamiast pisania (nazywanie); punktowane jak wybór słowa |
| Podpowiedzi | `POST /therapy/exercises/{id}/hint`: kolejna podpowiedź do nazywania (1 do czego służy, 2 pierwsza litera, 3 całe słowo); mniej punktów za każdą użytą podpowiedź (proporcje oczekują na ocenę kliniczną) |
| Odpowiedzi | `POST /therapy/exercises/{id}/answer` (wyrozumiale: wielkość liter, spacje, interpunkcja i brak polskich znaków się nie liczą; `almost` oznacza drobną pomyłkę): jedna odpowiedź na ćwiczenie. Odpowiedź serwera zawiera prawidłową odpowiedź, a ostatnia odpowiedź kończy sesję i ją ocenia. |
| Wyniki | `POST /therapy/sessions/{id}/complete`: wynik ukończonej sesji, policzony przez serwer |
| Twoje dane | `GET`/`PUT /users/profile`, `GET /users/progress`, `GET /users/badges`, `GET /users/progress/export/csv`, `GET /users/progress/export/pdf` |
| Planowanie | `GET`/`POST /users/scheduled-sessions`, `DELETE /users/scheduled-sessions/{id}` |
| Nagrania | `POST /users/audio/upload` (tylko po wyrażeniu zgody, inaczej 403), `GET /users/audio/{id}` |
| Twoje dane | `GET /users/me/export`: wszystko, co jest o Tobie zapisane, jako plik JSON do pobrania (bez skrótu hasła i ścieżek plików); `DELETE /users/me` z `{"password": ...}`: usuwa konto i wszystko, co jest o Tobie zapisane, łącznie z plikami nagrań |
| Strefa czasowa | `GET`/`PUT /users/time-zone`: `{"time_zone": "Europe/Warsaw"}` (nazwa IANA albo `null`), wysyłana przez przeglądarkę; według niej liczy się dni serii, a gdy jej brak, według UTC |
| Zgody | `GET`/`PUT /users/consents`: `recordings` i `speech_recognition`, każda `true`, `false` albo `null` (jeszcze nie pytano) |
| Administrator | `GET /admin/stats`, `GET /admin/users`, `GET /admin/users/{id}/sessions`, `PUT /admin/users/{id}/activate`, `PUT /admin/users/{id}/deactivate` |

`GET /health` odpowiada bez logowania; `GET /health/detailed` sprawdza też bazę danych (503, gdy nie może się z nią połączyć) i nie pokazuje ustawień.

## Struktura projektu

```
backend/          Aplikacja FastAPI (app/), testy (tests/), zależności
frontend/         index.html, css/, js/ (czysty JavaScript, bez kompilacji), nginx.conf
e2e/              Testy w przeglądarce (Playwright)
scripts/          check.sh (wszystkie testy), smoke.sh (szybki start z README), docker-smoke.sh
docs/             Przewodniki dla użytkowników (po polsku i po angielsku)
loop/             Pętla ulepszeń: zasady, backlog, dziennik
docker-compose.yml, .env.template
```

## Rozwój

```bash
scripts/check.sh
```

To jedyne sprawdzenie, które musi przejść przed każdym commitem. Samo przygotowuje swoje środowisko (`.venv-check`) i uruchamia:
- sprawdzenie zależności backendu pod kątem znanych podatności (pip-audit);
- linter;
- testy backendu;
- powyższy szybki start w osobnej kopii repozytorium;
- testy w przeglądarce, które obejmują rejestrację, całe sesje po polsku i po angielsku, informację zwrotną, wykres postępów i panel administratora.

Wkład w projekt: zgłoś problem albo pull request. Utrzymuj `scripts/check.sh` na zielono, do każdej zmiany dodaj test, a to README i [wersję angielską](README.md) aktualizuj razem.

Aplikację ulepsza się małymi, przetestowanymi krokami według opisanej pętli. Zob. [`loop/README.md`](loop/README.md).

## Znane ograniczenia

Zanim ktokolwiek zacznie polegać na tej aplikacji, trzeba naprawić co najmniej poniższe. Każdy punkt jest w [`loop/BACKLOG.md`](loop/BACKLOG.md).

- **Bezpieczeństwo**
  - Nie ma resetu „nie pamiętam hasła” ani sposobu na wylogowanie naraz ze wszystkich urządzeń bez zmiany hasła.
  - Limity błędnych haseł są trzymane w pamięci: każdy proces serwera liczy osobno, a restart je kasuje. Za serwerem pośredniczącym klienci są rozróżniani tylko wtedy, gdy serwer ufa jego nagłówkowi `X-Forwarded-For` (konfiguracja Docker tak robi); w przeciwnym razie wszyscy dzielą jeden licznik na nazwę użytkownika. Czy wartości 5 i 50 pasują osobom z afazją, to otwarte pytanie (backlog H7).
- **Prywatność:** nagrania i rozpoznawanie mowy wymagają zgody, o którą aplikacja pyta. Na stronie Konto można pobrać lub usunąć wszystkie swoje dane. Informacja o prywatności (`frontend/privacy.html`, PL i EN, z odnośnikami na stronie logowania i stronie Konto) opisuje, co robi kod; kto prowadzi aplikację, podstawa prawna, miejsce hostingu i kontakt są oznaczone „[do uzupełnienia]”, dopóki ktoś o nich nie zdecyduje (backlog H4, H5). Aplikacja przechowuje dane o zdrowiu.
- **Role:** każdy terapeuta widzi i może dezaktywować wszystkich pacjentów. Terapeuci nie są jeszcze powiązani ze swoimi pacjentami (P1-3b).
- **Treść kliniczna:** po polsku i po angielsku, w `backend/content/` i sprawdzana przy starcie aplikacji: 30 pojęć do nazywania, 12 zdań do uzupełnienia i 9 zwrotów do powtórzenia. Wszystkie są tymczasowe i niesprawdzone przez logopedę. Nie ma obrazków ani nagrań. Na czym powinien opierać się każdy rodzaj ćwiczeń, ze sprawdzoną bibliografią, opisuje [`docs/clinical/README.pl.md`](docs/clinical/README.pl.md); ten dokument także oczekuje na ocenę kliniczną.
- **Dostępność** nie została zbadana, a zasady projektowania przyjaznego osobom z afazją z [`loop/PROMPT.md`](loop/PROMPT.md) nie są jeszcze spełnione. Na przykład czytanie na głos działa tylko wtedy, gdy urządzenie ma własny głos dla danego języka.
- **Kwestie prawne:** nie oceniono, czy aplikacja jest wyrobem medycznym w rozumieniu przepisów UE.
- **Wdrażanie:** nie ma jeszcze ciągłej integracji (CI).

## Licencja

Licencja nie została jeszcze wybrana. Do tego czasu wszelkie prawa należą do autorów.
