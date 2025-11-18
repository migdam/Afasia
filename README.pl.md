# 🗣️ Aplikacja Terapii Mowy dla Afazji

[![Licencja: MIT](https://img.shields.io/badge/Licencja-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-witamy-brightgreen.svg)](http://makeapullrequest.com)

> **Gotowa do produkcji aplikacja webowa do terapii mowy, zaprojektowana dla pacjentów z afazją, obsługująca język polski i angielski.**

[🇬🇧 **English Version** / Wersja Angielska →](README.md)

---

## 📖 Spis Treści

- [Przegląd](#-przegląd)
- [Funkcje](#-funkcje)
- [Zrzuty Ekranu](#-zrzuty-ekranu)
- [Szybki Start](#-szybki-start)
- [Instalacja](#-instalacja)
- [Użytkowanie](#-użytkowanie)
- [Dokumentacja API](#-dokumentacja-api)
- [Architektura](#-architektura)
- [Konfiguracja](#-konfiguracja)
- [Wdrożenie](#-wdrożenie)
- [Współpraca](#-współpraca)
- [Licencja](#-licencja)
- [Wsparcie](#-wsparcie)

---

## 🌟 Przegląd

Aplikacja Terapii Mowy dla Afazji to kompleksowa platforma webowa zaprojektowana, aby pomóc osobom z afazją poprawić ich umiejętności komunikacyjne poprzez interaktywne ćwiczenia i śledzenie postępów. Zbudowana z wykorzystaniem nowoczesnych technologii i najlepszych praktyk, zapewnia płynne doświadczenie zarówno dla pacjentów, jak i terapeutów.

### Czym jest Afazja?

Afazja to zaburzenie komunikacji, które wpływa na zdolność osoby do mówienia, rozumienia, czytania i pisania. Zwykle występuje po udarze mózgu lub urazie głowy. Ta aplikacja pomaga pacjentom ćwiczyć i poprawiać ich umiejętności językowe poprzez ustrukturyzowane sesje terapeutyczne.

### Dla kogo jest ta aplikacja?

- **Pacjenci**: Osoby z afazją pragnące poprawić swoje umiejętności komunikacyjne
- **Logopedzi**: Specjaliści monitorujący postępy pacjentów i zarządzający planami terapii
- **Opiekunowie**: Członkowie rodziny wspierający pacjentów z afazją w procesie powrotu do zdrowia
- **Placówki Medyczne**: Kliniki i szpitale oferujące usługi terapii mowy

---

## ✨ Funkcje

### Podstawowa Funkcjonalność

#### 🎯 **Interaktywne Sesje Terapeutyczne**
- **Nazywanie Słów**: Ćwiczenia rozpoznawania wizualnego i nazywania z obrazkami
- **Uzupełnianie Zdań**: Ćwiczenia wypełniania luk z opcjami wielokrotnego wyboru
- **Rozpoznawanie Obrazów**: Dopasowywanie obrazów do właściwych słów
- **Ćwiczenie Wymowy**: Nagrywanie i ocena wzorców mowy

#### 📊 **Śledzenie Postępów**
- Monitorowanie wydajności w czasie rzeczywistym
- Wizualne wykresy postępów i analityka
- Śledzenie wskaźnika dokładności w czasie
- Historia sesji ze szczegółowymi statystykami

#### 👤 **Zarządzanie Użytkownikami**
- Bezpieczne uwierzytelnianie za pomocą tokenów JWT
- Personalizacja profilu osobistego
- Ustawienia preferencji językowych (Polski/Angielski)
- Kontrola dostępu oparta na rolach (Pacjent, Terapeuta, Administrator)

### 🚀 12 Ulepszonych Funkcji

#### 1. **🎤 Nagrywanie Głosu do Ćwiczenia Wymowy**
Nagrywaj swoje próby wymowy za pomocą mikrofonu urządzenia. System przechowuje nagrania do późniejszego przeglądu i oceny.

**Korzyści:**
- Ćwicz we własnym tempie
- Przeglądaj wcześniejsze próby
- Śledź poprawę wymowy
- Otrzymuj opinię od terapeutów

#### 2. **🖼️ Rozpoznawanie Słów Oparte na Obrazach**
Uczenie się wizualne poprzez wysokiej jakości obrazy połączone z ćwiczeniami słownymi.

**Korzyści:**
- Wzmocnione skojarzenia pamięciowe
- Kontekst wizualny dla lepszego uczenia się
- Odpowiednie dla różnych typów afazji
- Angażujące i interaktywne

#### 3. **📈 Poziomy Trudności (Łatwy, Średni, Trudny)**
Adaptacyjne uczenie się z trzema poziomami trudności dopasowanymi do Twojego poziomu umiejętności.

**Łatwy**: Proste, powszechne słowa i podstawowe zdania
**Średni**: Umiarkowane słownictwo i złożone zdania
**Trudny**: Zaawansowane słowa i wymagające ćwiczenia

#### 4. **🎮 System Gryfikacji**
Pozostań zmotywowany dzięki elementom przypominającym grę:

- **Punkty**: Zdobywaj punkty na podstawie dokładności i trudności
- **Odznaki**: Odblokuj osiągnięcia (Pierwsza Sesja, Seria Tygodniowa, Seria Miesięczna, Perfekcjonista, Oddany, Mistrz)
- **Serie**: Buduj codzienne nawyki praktyki dzięki śledzeniu serii
- **Rankingi**: (Widok administratora) Zobacz postępy całej platformy

#### 5. **📊 Panel Analityki Postępów**
Wizualizuj swoje postępy za pomocą:

- Interaktywnych wykresów liniowych pokazujących dokładność w czasie
- Łączna liczba ukończonych sesji
- Średni procent dokładności
- Całkowity czas praktyki
- Informacje o seriach
- Wyświetlanie kolekcji odznak

#### 6. **🔊 Odtwarzanie Audio do Wymowy**
Słuchaj prawidłowej wymowy przed próbami ćwiczeń.

**Funkcje:**
- Nagrania native speakerów
- Opcje wolnej/normalnej prędkości
- Powtarzalne odtwarzanie
- Wsparcie wielu języków

#### 7. **🌙 Tryb Ciemny**
Przyjazny dla oczu ciemny motyw do komfortowego długiego użytkowania.

**Funkcje:**
- Płynne przejścia motywów
- Zapisywanie trwałych preferencji
- Zmniejszone zmęczenie oczu
- Lepsze współczynniki kontrastu
- Przełączanie jednym kliknięciem

#### 8. **📅 System Planowania Sesji**
Planuj swoje sesje terapeutyczne z wyprzedzeniem.

**Funkcje:**
- Integracja z kalendarzem
- Ustaw preferowany czas i datę
- Powiadomienia przypominające (w przyszłości)
- Zobacz wszystkie zaplanowane sesje
- Łatwe zarządzanie i zmiana terminu

#### 9. **📄 Eksport Raportów Postępów (PDF/CSV)**
Generuj kompleksowe raporty dla terapeutów lub osobistych zapisów.

**Eksport CSV**: Szczegółowe dane do analizy w arkuszu kalkulacyjnym
**Eksport PDF**: Profesjonalnie sformatowane raporty

**Zawartość Raportu:**
- Historia sesji
- Trendy dokładności
- Czas spędzony na ćwiczeniach
- Punkty i osiągnięcia
- Podział ćwiczeń według typu

#### 10. **👨‍⚕️ Panel Administratora dla Terapeutów**
Kompleksowe narzędzia dla profesjonalistów medycznych.

**Funkcje:**
- Statystyki całej platformy
- Zarządzanie pacjentami
- Wyświetlanie postępów wszystkich użytkowników
- Aktywacja/deaktywacja kont
- Monitorowanie wskaźników zaangażowania
- Eksport raportów pacjentów

#### 11. **📱 Tryb Offline (Progresywna Aplikacja Webowa)**
Ćwicz nawet bez połączenia z internetem.

**Funkcje:**
- Instalacja na ekranie głównym
- Pamięć podręczna offline
- Synchronizacja w tle
- Doświadczenie podobne do aplikacji
- Nie wymaga sklepu z aplikacjami

#### 12. **🎙️ Ocena Mowy na Tekst**
Automatyczna ocena dokładności wymowy.

**Funkcje:**
- Transkrypcja w czasie rzeczywistym
- Punktacja dokładności
- Metryki pewności
- Wsparcie wielu języków (PL/EN)
- Szczegółowa opinia zwrotna

---

## 📸 Zrzuty Ekranu

### Logowanie i Panel

```
┌─────────────────────────────────────┐
│  🗣️ Terapia Afazji        🌙 PL ⚙️ │
├─────────────────────────────────────┤
│                                     │
│     Witamy w Terapii Afazji         │
│   Interaktywne ćwiczenia            │
│       logopedyczne                  │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Login: ________________     │   │
│  │ Hasło: ________________     │   │
│  │                             │   │
│  │      [Zaloguj się]          │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

### Widok Panelu

```
┌─────────────────────────────────────┐
│ Panel                               │
├─────────────────────────────────────┤
│ ⭐ Punkty  🔥 Seria  🏆 Odznaki     │
│    1,250       14        6          │
├─────────────────────────────────────┤
│ Rozpocznij Nową Sesję               │
│ Typ: [Nazywanie Słów ▼]             │
│ Trudność: [Średni ▼]                │
│ Ćwiczenia: [10]                     │
│ [Start]                             │
├─────────────────────────────────────┤
│ Ostatnie Sesje                      │
│ ✓ Nazywanie Słów - Średni | 85%    │
│ ✓ Wymowa - Łatwy | 92%             │
│ ✓ Uzupełnij Zdania - Trudny | 78% │
└─────────────────────────────────────┘
```

---

## 🚀 Szybki Start

### Wymagania Wstępne

Upewnij się, że masz zainstalowane:

- **Python 3.8+** ([Pobierz](https://www.python.org/downloads/))
- **Git** ([Pobierz](https://git-scm.com/downloads))
- **Node.js** (opcjonalnie, dla narzędzi deweloperskich)

### Sklonuj Repozytorium

```bash
git clone https://github.com/twojnazwa/aplikacja-terapii-afazji.git
cd aplikacja-terapii-afazji
```

### Uruchom Serwer Backend

```bash
# Przejdź do katalogu backend
cd backend

# Utwórz środowisko wirtualne
python -m venv venv

# Aktywuj środowisko wirtualne
# Na Linux/Mac:
source venv/bin/activate
# Na Windows:
venv\Scripts\activate

# Zainstaluj zależności
pip install -r requirements.txt

# Skonfiguruj zmienne środowiskowe
cp ../.env.template ../.env
# Edytuj .env i ustaw SECRET_KEY (wygeneruj: openssl rand -hex 32)

# Uruchom serwer
python -m app.main
```

API będzie dostępne pod adresem: **http://localhost:8000**

### Uruchom Serwer Frontend

```bash
# Otwórz nowy terminal
cd frontend

# Serwuj za pomocą wbudowanego serwera Python
python -m http.server 3000

# Lub użyj Node.js
npx serve -p 3000
```

Aplikacja będzie dostępna pod adresem: **http://localhost:3000**

### Uzyskaj Dostęp do Aplikacji

1. Otwórz przeglądarkę i przejdź do **http://localhost:3000**
2. Kliknij "Zarejestruj się", aby utworzyć nowe konto
3. Zaloguj się przy użyciu swoich poświadczeń
4. Rozpocznij swoją pierwszą sesję terapeutyczną!

---

## 📥 Instalacja

### Metoda 1: Docker (Zalecana dla Produkcji)

```bash
# Upewnij się, że Docker i Docker Compose są zainstalowane

# Uruchom wszystkie usługi
docker-compose up --build

# Aplikacja będzie dostępna pod adresem:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Dokumentacja API: http://localhost:8000/docs
```

### Metoda 2: Instalacja Ręczna

#### Konfiguracja Backend

1. **Utwórz Środowisko Wirtualne**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Zainstaluj Zależności**
   ```bash
   pip install -r requirements.txt
   ```

3. **Skonfiguruj Środowisko**
   ```bash
   cp ../.env.template ../.env
   ```

   Edytuj `.env` i skonfiguruj:
   ```env
   SECRET_KEY=twoj-sekretny-klucz  # Wygeneruj: openssl rand -hex 32
   DATABASE_URL=sqlite:///./aphasia_app.db
   BACKEND_CORS_ORIGINS=http://localhost:3000
   ```

4. **Uruchom Serwer**
   ```bash
   python -m app.main
   ```

#### Konfiguracja Frontend

1. **Przejdź do Frontend**
   ```bash
   cd frontend
   ```

2. **Serwuj Pliki Statyczne**
   ```bash
   # Opcja 1: Python
   python -m http.server 3000

   # Opcja 2: Node.js
   npx serve -p 3000
   ```

---

## 💡 Użytkowanie

### Dla Pacjentów

#### 1. **Utwórz Konto**
- Kliknij "Zarejestruj się" na stronie logowania
- Wypełnij swój email, nazwę użytkownika i hasło
- Wybierz preferowany język (Polski lub Angielski)
- Kliknij "Zarejestruj się"

#### 2. **Rozpocznij Sesję Terapeutyczną**
- Z panelu wybierz "Rozpocznij Nową Sesję"
- Wybierz typ ćwiczenia (Nazywanie Słów, Uzupełnianie Zdań, itp.)
- Wybierz poziom trudności (Łatwy, Średni lub Trudny)
- Ustaw liczbę ćwiczeń (5-50)
- Kliknij "Start"

#### 3. **Wykonaj Ćwiczenia**
- Przeczytaj uważnie pytanie
- Dla wielokrotnego wyboru: Kliknij poprawną odpowiedź
- Dla wprowadzania tekstu: Wpisz swoją odpowiedź
- Dla wymowy: Kliknij przycisk nagrywania i mów
- Kliknij "Zatwierdź", gdy będziesz gotowy
- Otrzymaj natychmiastową opinię

#### 4. **Śledź Swoje Postępy**
- Kliknij "Postęp" w menu nawigacji
- Zobacz swoje statystyki i wykresy
- Zobacz zdobyte odznaki
- Eksportuj raporty dla swojego terapeuty

#### 5. **Zaplanuj Przyszłe Sesje**
- Kliknij "Dodaj Harmonogram" na panelu
- Wybierz datę i godzinę
- Wybierz typ ćwiczenia i trudność
- Kliknij "Zaplanuj"

### Dla Terapeutów/Administratorów

#### 1. **Dostęp do Panelu Administratora**
- Zaloguj się za pomocą poświadczeń administratora
- Kliknij "Administrator" w menu nawigacji

#### 2. **Monitoruj Pacjentów**
- Zobacz łączną liczbę użytkowników i aktywnych użytkowników
- Zobacz statystyki całej platformy
- Sprawdź postępy indywidualnych pacjentów

#### 3. **Zarządzaj Użytkownikami**
- Zobacz wszystkich zarejestrowanych pacjentów
- Aktywuj lub dezaktywuj konta
- Uzyskaj dostęp do historii sesji pacjentów

#### 4. **Generuj Raporty**
- Eksportuj statystyki platformy
- Pobieraj raporty postępów pacjentów
- Analizuj skuteczność terapii

---

## 📚 Dokumentacja API

### Dokumentacja Interaktywna

Po uruchomieniu backendu, uzyskaj dostęp do interaktywnej dokumentacji API:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Schemat OpenAPI**: http://localhost:8000/openapi.json

### Główne Punkty Końcowe

#### Uwierzytelnianie

| Metoda | Punkt Końcowy | Opis |
|--------|---------------|------|
| POST | `/api/v1/auth/register` | Zarejestruj nowego użytkownika |
| POST | `/api/v1/auth/login` | Zaloguj użytkownika |

**Przykładowe Żądanie Logowania:**
```json
{
  "username": "jankowalski",
  "password": "bezpiecznehaslo123"
}
```

**Odpowiedź:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "jankowalski",
    "email": "jan@example.com",
    "total_points": 0,
    "current_streak": 0
  }
}
```

#### Sesje Terapeutyczne

| Metoda | Punkt Końcowy | Opis |
|--------|---------------|------|
| POST | `/api/v1/therapy/sessions` | Utwórz nową sesję |
| GET | `/api/v1/therapy/sessions` | Wyświetl sesje użytkownika |
| GET | `/api/v1/therapy/sessions/{id}` | Pobierz szczegóły sesji |
| GET | `/api/v1/therapy/sessions/{id}/exercises` | Pobierz ćwiczenia sesji |
| POST | `/api/v1/therapy/exercises/{id}/answer` | Prześlij odpowiedź ćwiczenia |
| POST | `/api/v1/therapy/sessions/{id}/complete` | Oznacz sesję jako ukończoną |

**Przykład Tworzenia Sesji:**
```json
{
  "title": "Poranna Praktyka",
  "exercise_type": "word_naming",
  "difficulty": "medium",
  "language": "pl",
  "num_exercises": 10
}
```

#### Zarządzanie Użytkownikami

| Metoda | Punkt Końcowy | Opis |
|--------|---------------|------|
| GET | `/api/v1/users/profile` | Pobierz profil użytkownika |
| PUT | `/api/v1/users/profile` | Zaktualizuj profil |
| GET | `/api/v1/users/progress` | Pobierz statystyki postępów |
| GET | `/api/v1/users/badges` | Pobierz zdobyte odznaki |
| GET | `/api/v1/users/scheduled-sessions` | Pobierz zaplanowane sesje |
| POST | `/api/v1/users/scheduled-sessions` | Zaplanuj nową sesję |
| GET | `/api/v1/users/progress/export/csv` | Eksportuj raport CSV |
| GET | `/api/v1/users/progress/export/pdf` | Eksportuj raport PDF |

#### Administrator

| Metoda | Punkt Końcowy | Opis |
|--------|---------------|------|
| GET | `/api/v1/admin/stats` | Pobierz statystyki platformy |
| GET | `/api/v1/admin/users` | Wyświetl wszystkich użytkowników |
| GET | `/api/v1/admin/users/{id}/sessions` | Pobierz sesje użytkownika |
| PUT | `/api/v1/admin/users/{id}/activate` | Aktywuj użytkownika |
| PUT | `/api/v1/admin/users/{id}/deactivate` | Dezaktywuj użytkownika |

### Uwierzytelnianie

Wszystkie punkty końcowe (oprócz rejestracji i logowania) wymagają uwierzytelniania JWT. Dołącz token w nagłówku Authorization:

```
Authorization: Bearer <twoj-token-tutaj>
```

---

## 🏗️ Architektura

### Stos Technologiczny

#### Backend
- **Framework**: FastAPI (Python)
- **Baza Danych**: SQLAlchemy ORM z SQLite (dev) / PostgreSQL (prod)
- **Uwierzytelnianie**: Tokeny JWT z passlib/bcrypt
- **Walidacja**: Modele Pydantic
- **Logowanie**: Structlog
- **Dokumentacja**: OpenAPI/Swagger

#### Frontend
- **HTML5**: Semantyczne, dostępne znaczniki
- **CSS3**: Nowoczesne stylowanie z Grid i Flexbox
- **JavaScript**: Vanilla ES6+ z modułami
- **PWA**: Service Workers dla wsparcia offline
- **Wykresy**: Niestandardowa implementacja Canvas API
- **Audio**: Web Audio API, MediaRecorder API
- **Mowa**: Web Speech API dla rozpoznawania

#### Infrastruktura
- **Konteneryzacja**: Docker & Docker Compose
- **Serwer WWW**: Nginx (dla frontendu)
- **Baza Danych**: PostgreSQL (produkcja)
- **Buforowanie**: Pamięć podręczna Service Worker

---

## ⚙️ Konfiguracja

### Zmienne Środowiskowe

Utwórz plik `.env` w katalogu głównym (użyj `.env.template` jako odniesienia):

```env
# Konfiguracja Serwera
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Bezpieczeństwo
SECRET_KEY=twoj-sekretny-klucz  # Wygeneruj: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Baza Danych
DATABASE_URL=sqlite:///./aphasia_app.db
# Produkcja: postgresql://uzytkownik:haslo@localhost/aphasia_db

# CORS (oddzielone przecinkami)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Przesyłanie Plików
MAX_UPLOAD_SIZE=10485760  # 10MB
UPLOAD_DIR=./uploads

# Email (opcjonalnie)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=twoj-email@gmail.com
SMTP_PASSWORD=twoje-haslo-aplikacji
SMTP_FROM=noreply@terapia-afazji.app
```

---

## 🚢 Wdrożenie

### Wdrożenie Docker (Zalecane)

1. **Sklonuj repozytorium**
   ```bash
   git clone https://github.com/twojnazwa/aplikacja-terapii-afazji.git
   cd aplikacja-terapii-afazji
   ```

2. **Skonfiguruj środowisko**
   ```bash
   cp .env.template .env
   # Edytuj .env wartościami produkcyjnymi
   ```

3. **Uruchom usługi**
   ```bash
   docker-compose up -d
   ```

4. **Uzyskaj dostęp do aplikacji**
   - Frontend: http://twoja-domena.com
   - Backend: http://twoja-domena.com:8000

---

## 🤝 Współpraca

Witamy wkłady! Prosimy o przestrzeganie tych wytycznych:

### Rozpoczęcie

1. **Forkuj repozytorium**
2. **Sklonuj swój fork**
   ```bash
   git clone https://github.com/twojnazwa/aplikacja-terapii-afazji.git
   ```
3. **Utwórz gałąź**
   ```bash
   git checkout -b feature/nazwa-twojej-funkcji
   ```

### Wytyczne Deweloperskie

- Przestrzegaj PEP 8 dla kodu Python
- Używaj ESLint dla kodu JavaScript
- Pisz znaczące komunikaty commitów
- Dodawaj testy dla nowych funkcji
- Aktualizuj dokumentację

---

## 📄 Licencja

Ten projekt jest licencjonowany na licencji MIT - zobacz plik [LICENSE](LICENSE) dla szczegółów.

---

## 💬 Wsparcie

### Uzyskiwanie Pomocy

- **Dokumentacja**: Sprawdź folder [docs](docs/)
- **Problemy**: Zgłaszaj błędy lub proś o funkcje na [GitHub Issues](https://github.com/twojnazwa/aplikacja-terapii-afazji/issues)
- **Dyskusje**: Zadawaj pytania w [GitHub Discussions](https://github.com/twojnazwa/aplikacja-terapii-afazji/discussions)

### Kontakt

- **Email**: wsparcie@terapia-afazji.app
- **Strona WWW**: https://terapia-afazji.app

---

## 🙏 Podziękowania

- Zespół FastAPI za doskonały framework
- Profesjonaliści terapii mowy, którzy udzielili wskazówek
- Społeczność open source za cenne narzędzia
- Wszyscy współtwórcy i wspierający

---

## 📊 Status Projektu

- ✅ **Wersja**: 1.0.0
- ✅ **Status**: Gotowy do Produkcji
- ✅ **Ostatnia Aktualizacja**: 2024
- ✅ **Utrzymywany**: Tak

---

## 🗺️ Plan Rozwoju

### Wersja 1.1 (Planowana)
- [ ] Sesje terapii wideo
- [ ] Pokoje terapii grupowej
- [ ] Natywne aplikacje mobilne
- [ ] Ulepszona analiza mowy AI

### Wersja 1.2 (Przyszłość)
- [ ] Niestandardowe tworzenie ćwiczeń
- [ ] Portal rodziny/opiekuna
- [ ] Rozszerzenie treści wielojęzycznych
- [ ] Integracja z EHR

---

**Stworzone z ❤️ dla społeczności afazji**

[⬆ Powrót na górę](#-aplikacja-terapii-mowy-dla-afazji)
