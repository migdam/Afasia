# Afasia: ćwiczenia mowy dla osób z afazją

[🇬🇧 English version](README.md)

Aplikacja internetowa do ćwiczenia słów i zdań po udarze lub urazie mózgu. Osoby z afazją ćwiczą w niej samodzielnie, równolegle z terapią u logopedy, a terapeuci widzą, kto ćwiczy. Interfejs jest dostępny po polsku i po angielsku.

> **Stan: wczesna faza rozwoju. Nie do użytku klinicznego.**
> Ćwiczenia są tymczasowe i nie sprawdził ich jeszcze żaden logopeda, treść ćwiczeń jest tylko po angielsku, a prace nad bezpieczeństwem wymienione w części [Znane ograniczenia](#znane-ograniczenia) nie są skończone. Postęp prac jest w [`loop/BACKLOG.md`](loop/BACKLOG.md).

## Co już działa

Konta, sesje ćwiczeń, informacja zwrotna, wyniki, wykres postępów i panel administratora są sprawdzane testami automatycznymi (zob. [Rozwój](#rozwój)). Eksport, planowanie sesji i układ na telefon nie mają jeszcze testów.

- **Konta.** Rejestracja, logowanie i wylogowanie. Po odświeżeniu strony nadal jesteś zalogowany. Hasła są szyfrowane algorytmem bcrypt, a logowanie korzysta z tokenów JWT ważnych 30 minut.
- **Sesje ćwiczeń** po 5–50 ćwiczeń, na poziomie łatwym, średnim lub trudnym:
  - *Nazywanie słów*: przeczytaj krótki opis („A pet that barks and wags its tail”) i wpisz słowo.
  - *Uzupełnianie zdań*: wybierz słowo, które kończy zdanie.

  Po każdej odpowiedzi pojawia się „Poprawnie! Świetna robota!” albo prawidłowa odpowiedź. Serwer liczy wynik sesji, gdy przyjdzie ostatnia odpowiedź.
- **Postępy.** Punkty za poprawne odpowiedzi, codzienne serie, trzy odznaki (pierwsza sesja, seria 7 i 30 dni), strona postępów z podsumowaniem i wykresem trafności oraz eksport do CSV i PDF.
- **Planowanie.** Można zaplanować przyszłe sesje. Aplikacja jeszcze o nich nie przypomina.
- **Panel terapeuty/administratora.** Lista wszystkich pacjentów, aktywowanie i dezaktywowanie kont. Rejestracja w aplikacji zawsze tworzy konto pacjenta; konta personelu zakłada się na serwerze (zob. [Konta personelu](#konta-personelu)).
- **Interfejs.** Polski i angielski, motyw jasny i ciemny, układ na telefon i komputer.

### Co jeszcze nie działa

- **Wymowa.** Można się nagrać, ale odpowiedź ocenia wbudowane rozpoznawanie mowy przeglądarki. W większości przeglądarek ono nie działa, a mowy osób z afazją nie rozpoznaje wiarygodnie. Ten typ ćwiczeń jest projektowany od nowa (backlog P2-7).
- **Rozpoznawanie obrazów** nie ma ćwiczeń, więc aplikacja go nie oferuje.
- **Obrazków ani nagrań** jeszcze nie ma. Ćwiczenia nazywania używają opisów.
- **Praca offline.** Service worker zapamiętuje pliki aplikacji, ale każde ćwiczenie wymaga połączenia z serwerem.

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

Backend czyta `.env` z katalogu głównego repozytorium, niezależnie od tego, skąd go uruchomisz. Nieznane mu ustawienia pomija, więc ten sam plik służy też Docker Compose. Podczas pracy nad kodem bazą danych jest SQLite (`backend/aphasia_app.db`).

## Uruchamianie w Dockerze

Potrzebujesz Dockera z Compose v2.

```bash
cp .env.template .env           # ustaw SECRET_KEY i POSTGRES_PASSWORD
docker compose up --build
```

- Aplikacja: http://localhost:3000. nginx serwuje frontend i przekazuje `/api` do backendu.
- API bezpośrednio: http://localhost:8000.
- Dane są w PostgreSQL, w wolumenie Dockera.
- Bez tych dwóch sekretów `docker compose up` się nie uruchomi.
- Za proxy, które podgląda ruch TLS, ustaw `PIP_CA_FILE` na jego pakiet certyfikatów CA, żeby budowanie obrazu mogło pobrać pakiety z PyPI.

`scripts/docker-smoke.sh` buduje i uruchamia osobną kopię całości, rejestruje się i loguje przez nginx, a potem wszystko usuwa.

## Konta personelu

Rejestracja w aplikacji zawsze tworzy konto pacjenta. Konta administratorów i terapeutów zakłada się na serwerze, w katalogu `backend/`, z tymi samymi ustawieniami co backend:

```bash
python -m app.cli create-user --username ada --email ada@example.com --role admin
python -m app.cli set-role tess therapist      # zmiana roli istniejącego konta
```

`create-user` pyta o hasło, które musi mieć co najmniej 12 znaków, więc nie trafia ono do historii poleceń. W Dockerze uruchom te same polecenia jako `docker compose exec backend python -m app.cli …`.

## Konfiguracja

Skopiuj `.env.template` do `.env` w katalogu głównym repozytorium. Ustawienia:

| Ustawienie | Domyślnie | Znaczenie |
|---|---|---|
| `SECRET_KEY` | (wymagane) | Podpisuje tokeny logowania. Co najmniej 32 losowe bajty (`openssl rand -hex 32`). |
| `DATABASE_URL` | `sqlite:///./aphasia_app.db` | Dowolny adres SQLAlchemy, np. `postgresql://użytkownik:hasło@host/baza` |
| `BACKEND_CORS_ORIGINS` | `http://localhost:3000,http://localhost:8000` | Adresy stron (oddzielone przecinkami), które mogą wywoływać API |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Jak długo trwa zalogowanie |
| `DEBUG`, `HOST`, `PORT` | `true`, `0.0.0.0`, `8000` | Opcje serwera |
| `UPLOAD_DIR`, `MAX_UPLOAD_SIZE` | `./uploads`, 10 MB | Gdzie trafiają nagrania głosu |
| `POSTGRES_PASSWORD`, `FRONTEND_PORT`, `BACKEND_PORT`, `PIP_CA_FILE` | | Tylko dla Docker Compose |

## API

FastAPI udostępnia interaktywną dokumentację pod `/docs` i `/redoc`. Wszystkie adresy zaczynają się od `/api/v1`. Wszystkie oprócz rejestracji i logowania wymagają nagłówka `Authorization: Bearer <token>`. Brakujący lub nieprawidłowy token daje 401.

| Obszar | Adresy |
|---|---|
| Konta | `POST /auth/register`, `POST /auth/login` |
| Sesje | `POST /therapy/sessions`, `GET /therapy/sessions`, `GET /therapy/sessions/{id}`, `GET /therapy/sessions/{id}/exercises` |
| Odpowiedzi | `POST /therapy/exercises/{id}/answer`: jedna odpowiedź na ćwiczenie. Odpowiedź serwera zawiera prawidłową odpowiedź, a ostatnia odpowiedź kończy sesję i ją ocenia. |
| Wyniki | `POST /therapy/sessions/{id}/complete`: wynik ukończonej sesji, policzony przez serwer |
| Twoje dane | `GET`/`PUT /users/profile`, `GET /users/progress`, `GET /users/badges`, `GET /users/progress/export/csv`, `GET /users/progress/export/pdf` |
| Planowanie | `GET`/`POST /users/scheduled-sessions`, `DELETE /users/scheduled-sessions/{id}` |
| Nagrania | `POST /users/audio/upload`, `GET /users/audio/{id}` |
| Administrator | `GET /admin/stats`, `GET /admin/users`, `GET /admin/users/{id}/sessions`, `PUT /admin/users/{id}/activate`, `PUT /admin/users/{id}/deactivate` |

`GET /health` odpowiada bez logowania.

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
  - Tokeny logowania są przechowywane w `localStorage`, a zalogowanie trwa stałe 30 minut (P1-5b).
  - Limit błędnych haseł (5 na nazwę użytkownika w ciągu 15 minut) jest trzymany w pamięci: każdy proces serwera liczy osobno, a restart go kasuje.
- **Prywatność:** brak informacji o prywatności, zgody przed nagrywaniem oraz możliwości eksportu i usunięcia swoich danych (P1-6). Aplikacja przechowuje dane o zdrowiu.
- **Role:** każdy terapeuta widzi i może dezaktywować wszystkich pacjentów. Terapeuci nie są jeszcze powiązani ze swoimi pacjentami (P1-3b).
- **Treść kliniczna:** kilka tymczasowych ćwiczeń po angielsku, niesprawdzonych przez logopedę. Nie ma obrazków ani nagrań.
- **Dostępność** nie została zbadana, a zasady projektowania przyjaznego osobom z afazją z [`loop/PROMPT.md`](loop/PROMPT.md) nie są jeszcze spełnione. Na przykład aplikacja nadal sama przechodzi dalej po 2 sekundach.
- **Kwestie prawne:** nie oceniono, czy aplikacja jest wyrobem medycznym w rozumieniu przepisów UE.
- **Wdrażanie:** nie ma jeszcze ciągłej integracji (CI).

## Licencja

Licencja nie została jeszcze wybrana. Do tego czasu wszelkie prawa należą do autorów.
