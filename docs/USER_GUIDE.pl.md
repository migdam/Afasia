# Przewodnik użytkownika

[🇬🇧 Guide in English](USER_GUIDE.md)

Ten przewodnik opisuje aplikację w jej obecnej postaci: wczesnej wersji do wypróbowania, nie do użytku klinicznego (zob. [README](../README.pl.md)). Aplikacja ma wspierać pracę z logopedą, a nie ją zastępować.

## Zanim zaczniesz

- **Przeglądarka:** aktualny Chrome, Edge, Firefox lub Safari na komputerze, tablecie albo telefonie. Aplikacja jest testowana w Chrome.
- **Adres:** poda go osoba, która uruchamia aplikację, np. `http://localhost:3000`.
- **Mikrofon:** potrzebny tylko do ćwiczeń wymowy, które jeszcze nie działają niezawodnie (zob. [Wymowa](#wymowa)).

## Język i motyw

Przyciski w prawym górnym rogu każdego ekranu:
- **EN / PL** przełącza język między angielskim a polskim.
- **🌙 / ☀️** przełącza między motywem jasnym a ciemnym.

Przeglądarka zapamiętuje oba wybory.

Same ćwiczenia są na razie po angielsku, w obu wersjach językowych. Po wybraniu polskiego kilka komunikatów nadal jest też po angielsku: okienka z komunikatami, „Completed” na liście sesji i przyciski w panelu administratora.

## Twoje konto

**Rejestracja:**
1. Kliknij **Zarejestruj się** pod formularzem logowania.
2. Wpisz e-mail, nazwę użytkownika, imię i nazwisko (nieobowiązkowo) oraz hasło.
3. Kliknij **Zarejestruj się**. Od razu zobaczysz swoją tablicę.

**Logowanie:** wpisz nazwę użytkownika i hasło, a potem kliknij **Zaloguj się**.

**Wylogowanie:** kliknij **Wyloguj** w prawym górnym rogu. Formularz logowania zostaje wyczyszczony, więc następna osoba nie zobaczy, co wpisano.

Zalogowanie trwa 30 minut. Po tym czasie przy następnym otwarciu lub odświeżeniu strony trzeba zalogować się ponownie. Nie ma jeszcze opcji „nie pamiętam hasła”.

## Tablica

Na górze są trzy liczby:
- **Punkty:** zob. [Punkty, serie i odznaki](#punkty-serie-i-odznaki).
- **Seria:** ile dni z rzędu kończysz sesję.
- **Odznaki:** ile odznak już masz.

Pod nimi:
- **Rozpocznij nową sesję:** zacznij ćwiczyć.
- **Zaplanowane sesje:** sesje zaplanowane na później.
- **Ostatnie sesje:** pięć ostatnich sesji z wynikami.

Pasek na dole przełącza między **Tablicą** a **Postępem**. Terapeuci i administratorzy widzą tam też **Administratora**.

## Ćwiczenie

1. W części **Rozpocznij nową sesję** wybierz:
   - **Typ ćwiczenia:** Nazywanie słów, Uzupełnianie zdań albo Wymowa.
   - **Poziom trudności:** Łatwy, Średni albo Trudny.
   - **Liczbę ćwiczeń:** od 5 do 50. Na początek dobre są krótkie sesje, po 5–10 ćwiczeń.
2. Kliknij **Rozpocznij**.
3. Odpowiedz na ćwiczenie i kliknij **Zatwierdź**.
4. Zobaczysz **„Poprawnie! Świetna robota!”** albo **„Nie tym razem. Prawidłowa odpowiedź: …”**, z prawidłową odpowiedzią pogrubioną.
5. Po 2 sekundach samo pojawi się następne ćwiczenie.

Na górze ekranu ćwiczenia:
- **Wyjdź** kończy sesję. Aplikacja poprosi o potwierdzenie. Przerwana sesja zostaje nieukończona i nie liczy się do wyników.
- Licznik i pasek pokazują, ile już za tobą, np. **3/10**.
- Zegar pokazuje, ile trwa sesja. Nie ma limitu czasu.

Po ostatnim ćwiczeniu pojawia się wynik, np. „Session complete! Score: 80%” (ten komunikat jest jeszcze po angielsku), i wracasz na tablicę.

### Nazywanie słów

Czytasz krótki opis codziennej rzeczy, np. „A pet that barks and wags its tail” (zwierzę domowe, które szczeka i macha ogonem). Wpisz jej nazwę (**dog**) w polu i kliknij **Zatwierdź**.

Odpowiedź musi się dokładnie zgadzać. Nie liczą się tylko wielkość liter i spacje na początku i końcu. Obrazków jeszcze nie ma.

### Uzupełnianie zdań

Czytasz zdanie z luką, np. „The sky is ___”. Kliknij pasujące słowo, a potem **Zatwierdź**. Jeśli klikniesz **Zatwierdź** bez wyboru, aplikacja poprosi najpierw o odpowiedź („Please provide an answer”).

### Wymowa

Widzisz słowo lub zwrot do powiedzenia, np. „Say: Hello”. Kliknij **Nagraj**, powiedz je, kliknij przycisk jeszcze raz, żeby zakończyć nagrywanie, a potem **Zatwierdź**. Za pierwszym razem przeglądarka zapyta o zgodę na użycie mikrofonu.

**To jeszcze nie działa niezawodnie.** Odpowiedź ocenia wbudowane rozpoznawanie mowy przeglądarki. W większości przeglądarek jest ono niedostępne, a tam, gdzie działa, nie radzi sobie z mową osób z afazją. Często poprawna odpowiedź zostaje uznana za błędną. Ten typ ćwiczeń jest projektowany od nowa.

### Rozpoznawanie obrazów

Jeszcze niedostępne: nie ma ćwiczeń tego typu, więc aplikacja ich nie oferuje.

## Punkty, serie i odznaki

- **Punkty:** każda poprawna odpowiedź daje 10 punktów na poziomie Łatwym, 20 na Średnim i 30 na Trudnym. Punkty dolicza się po ukończeniu sesji.
- **Seria:** kończenie sesji w kolejne dni buduje serię. Dni liczy się według czasu UTC, więc tuż po północy w Polsce może to być jeszcze poprzedni dzień.
- **Odznaki:** za pierwszą ukończoną sesję, za serię 7 dni i za serię 30 dni.

## Twój postęp

Kliknij **Postęp** na dolnym pasku. Zobaczysz:
- **Wszystkie sesje:** ukończone sesje.
- **Średnią dokładność:** jaka część wszystkich odpowiedzi była poprawna.
- **Całkowity czas:** czas od początku każdej ukończonej sesji do ostatniej odpowiedzi, w godzinach.
- **Najdłuższą serię.**
- **Postęp w czasie:** wykres wyników sesji z ostatnich 30 dni.
- **Zdobyte odznaki.**

**Eksportuj CSV** pobiera wszystkie ukończone sesje jako plik arkusza kalkulacyjnego. **Eksportuj PDF** pobiera krótki raport z podsumowaniem i 10 ostatnimi sesjami. Każdy z nich możesz przekazać logopedzie.

## Planowanie sesji

Kliknij **Dodaj harmonogram** na tablicy. Podaj tytuł, datę i godzinę, typ ćwiczenia i poziom trudności, a potem kliknij **Zaplanuj**. Nadchodzące sesje są na tablicy, a **Usuń** usuwa wybraną.

Aplikacja jeszcze nie przypomina o zaplanowanych sesjach. Sesję trzeba też rozpocząć samodzielnie, w części **Rozpocznij nową sesję**.

## Dla terapeutów i administratorów

**Administrator** na dolnym pasku pokazuje:
- liczbę pacjentów, aktywnych pacjentów i ukończonych sesji oraz odsetek poprawnych odpowiedzi wszystkich użytkowników;
- wszystkich pacjentów z adresem e-mail i punktami;
- przycisk **Deactivate** przy każdym aktywnym pacjencie: dezaktywowany pacjent nie może się zalogować, dopóki nie klikniesz **Activate**.

Na razie każdy terapeuta widzi wszystkich pacjentów. Rejestracja zawsze tworzy konto pacjenta; konta terapeutów i administratorów zakłada osoba, która uruchamia serwer (zob. README).

## Twoje dane

Wszystko, co robisz, jest zapisywane na serwerze, na którym działa aplikacja: konto, odpowiedzi, nagrania i wyniki. Informacja o prywatności, zgoda przed nagrywaniem oraz możliwość pobrania lub usunięcia wszystkich swoich danych są planowane, ale jeszcze ich nie ma. Jeśli chcesz usunąć swoje dane, poproś o to osobę, która uruchamia aplikację.

## Gdy coś nie działa

| Co się dzieje | Co zrobić |
|---|---|
| „Incorrect username or password” | Sprawdź pisownię i Caps Lock. W nazwie użytkownika liczy się wielkość liter. |
| „Inactive user” | Twoje konto zostało dezaktywowane. Zapytaj logopedę lub administratora. |
| Wracasz na stronę logowania | Minęło 30 minut zalogowania. Zaloguj się ponownie. |
| „Failed to start session” | Serwer może nie działać. Spróbuj później albo powiadom osobę, która uruchamia aplikację. |
| „Please provide an answer” | Przed **Zatwierdź** wpisz słowo albo wybierz odpowiedź. |
| Mikrofon nie działa | Zezwól na mikrofon w ustawieniach strony w przeglądarce i odśwież stronę. Wymowa i tak działa zawodnie (zob. wyżej). |

## Pytania

Zapytaj osobę, która uruchamia dla ciebie aplikację, albo zgłoś problem w repozytorium projektu.
