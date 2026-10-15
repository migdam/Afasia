# Przewodnik użytkownika

[🇬🇧 Guide in English](USER_GUIDE.md)

Ten przewodnik opisuje aplikację w jej obecnej postaci: wczesnej wersji do wypróbowania, nie do użytku klinicznego (zob. [README](../README.pl.md)). Aplikacja ma wspierać pracę z logopedą, a nie ją zastępować.

## Zanim zaczniesz

- **Przeglądarka:** aktualny Chrome, Edge, Firefox lub Safari na komputerze, tablecie albo telefonie. Aplikacja jest testowana w Chrome.
- **Adres:** poda go osoba, która uruchamia aplikację, np. `http://localhost:3000`.
- **Mikrofon:** potrzebny tylko do ćwiczeń wymowy, które jeszcze nie działają niezawodnie (zob. [Wymowa](#wymowa)).

## Język i motyw

Przyciski w prawym górnym rogu każdego ekranu:
- **A+** powiększa cały tekst. Kliknij jeszcze raz, żeby wrócić do zwykłej wielkości.
- **EN / PL** przełącza język między angielskim a polskim.
- **🌙 / ☀️** przełącza między motywem jasnym a ciemnym.

Przeglądarka zapamiętuje te wybory.

Ćwiczenia są w wybranym języku. Po wybraniu polskiego kilka słów nadal jest też po angielsku: „Completed” na liście sesji i przyciski w panelu administratora.

## Twoje konto

**Rejestracja:**
1. Kliknij **Zarejestruj się** pod formularzem logowania.
2. Wpisz e-mail, nazwę użytkownika, imię i nazwisko (nieobowiązkowo) oraz hasło (co najmniej 8 znaków).
3. Kliknij **Zarejestruj się**. Od razu zobaczysz swoją tablicę.

**Logowanie:** wpisz nazwę użytkownika i hasło, a potem kliknij **Zaloguj się**.

**Wylogowanie:** kliknij **Wyloguj** w prawym górnym rogu albo na dole strony **Konto**. Na telefonie przycisk jest tylko na stronie Konto, żeby górny pasek był niski. Formularz logowania zostaje wyczyszczony, więc następna osoba nie zobaczy, co wpisano.

Dopóki korzystasz z aplikacji, zalogowanie trwa. Po 30 minutach bez korzystania z niej albo 12 godzinach od zalogowania trzeba zalogować się ponownie. Nie ma jeszcze opcji „nie pamiętam hasła”.

**Zmiana hasła:** dotknij **Konto** na dole ekranu. Wpisz obecne hasło i nowe, mające co najmniej 8 znaków, a potem kliknij **Zmień hasło**. Komunikat pod przyciskiem powie, czy się udało. Na tym urządzeniu zalogowanie trwa dalej, ale na innych trzeba zalogować się ponownie nowym hasłem.

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
5. Nie spiesz się. Kiedy zechcesz, kliknij **Dalej**. Po ostatnim ćwiczeniu przycisk nazywa się **Zobacz wynik**.

Na górze ekranu ćwiczenia:
- **Wyjdź** kończy sesję. Aplikacja najpierw zapyta: wybierz **Zostań** albo **Wyjdź**. Przerwana sesja zostaje nieukończona i nie liczy się do wyników.
- Licznik i pasek pokazują, ile już za tobą, np. **3/10**.
- Nie ma zegara ani limitu czasu.

Po ostatnim ćwiczeniu kliknij **Zobacz wynik**: wracasz na tablicę, a komunikat u góry mówi np. „Sesja zakończona. Twój wynik: 80%.”. Kliknij **OK**, żeby go zamknąć.

### Nazywanie słów

Czytasz krótki opis codziennej rzeczy, np. „Zwierzę, które szczeka i merda ogonem”. Wpisz jej nazwę (**pies**) w polu i kliknij **Zatwierdź**.

Odpowiedź musi się dokładnie zgadzać. Nie liczą się tylko wielkość liter i spacje na początku i końcu; niektóre słowa mają też inne przyjmowane odpowiedzi, np. **auto** zamiast **samochód**. Obrazków jeszcze nie ma.

**🔊 Przeczytaj**, pod pytaniem, pod każdą podpowiedzią i pod komunikatem, czyta tekst na głos. Taki sam przycisk mają komunikaty, pytania w okienkach i objaśnienia w innych miejscach aplikacji. Korzysta tylko z głosów na Twoim urządzeniu; jeśli nie ma żadnego w Twoim języku, przycisk się nie pojawia.

**Jeśli słowo nie przychodzi**, kliknij **Podpowiedź**. Każde kliknięcie daje trochę więcej pomocy: najpierw do czego służy rzecz i gdzie się ją znajduje, potem pierwszą literę, a na końcu całe słowo. Poprawna odpowiedź po podpowiedziach daje mniej punktów, a komunikat mówi, ile podpowiedzi użyto.

### Uzupełnianie zdań

Czytasz zdanie z luką, np. „Niebo jest ___”. Kliknij pasujące słowo, a potem **Zatwierdź**. Jeśli klikniesz **Zatwierdź** bez wyboru, aplikacja poprosi najpierw o odpowiedź („Najpierw wybierz lub wpisz odpowiedź.”).

### Wymowa

Widzisz słowo lub zwrot do powiedzenia, np. „Powiedz: Cześć”. Kliknij **Nagraj**, powiedz je, kliknij przycisk jeszcze raz, żeby zakończyć nagrywanie, a potem **Zatwierdź**. Za pierwszym razem aplikacja zapyta, czy może przechowywać nagrania (zob. [Twoje dane](#twoje-dane)), a przeglądarka poprosi o zgodę na użycie mikrofonu. Mikrofon jest włączony tylko podczas nagrywania: wyłącza się, gdy zakończysz nagrywanie, wyjdziesz z sesji albo się wylogujesz, a przeglądarka przestaje pokazywać, że jest używany.

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

Wszystko, co robisz, jest zapisywane na serwerze, na którym działa aplikacja: konto, odpowiedzi i wyniki. Nagrania są przechowywane tylko za Twoją zgodą. Gdy pierwszy raz klikniesz **Nagraj**, aplikacja zapyta, czy może przechowywać nagrania; jeśli odpowiesz „Nie”, mikrofon pozostanie wyłączony. Przed użyciem rozpoznawania mowy przeglądarki, które może wysłać Twój głos do firmy, która stworzyła przeglądarkę, aplikacja zapyta osobno. Obie odpowiedzi możesz w każdej chwili zmienić w części **Twoje zgody** na stronie **Konto**. W części **Twoje dane** na stronie **Konto** możesz:

- **Pobierz moje dane:** zapisuje wszystko, co aplikacja o Tobie przechowuje, w jednym pliku (JSON).
- **Usuń moje konto:** po wpisaniu hasła usuwa konto, odpowiedzi, wyniki i nagrania. Nie da się tego cofnąć.

Odnośnik **Informacja o prywatności**, na stronie logowania i na stronie Konto, wyjaśnia, co aplikacja przechowuje, w jakim celu i kto to widzi.

## Gdy coś nie działa

| Co się dzieje | Co zrobić |
|---|---|
| „Nazwa użytkownika lub hasło są nieprawidłowe.” | Sprawdź pisownię i Caps Lock. W nazwie użytkownika liczy się wielkość liter. |
| „To konto jest wyłączone.” | Twoje konto zostało dezaktywowane. Zapytaj logopedę lub administratora. |
| „Zbyt wiele błędnych haseł.” | Po 5 błędnych hasłach logowanie na to konto z Twojego urządzenia jest wstrzymane na maksymalnie 15 minut. Odczekaj i spróbuj ponownie. |
| Wracasz na stronę logowania | Zalogowanie wygasło po 30 minutach bez korzystania z aplikacji albo 12 godzinach od zalogowania. Zaloguj się ponownie. |
| „Nie udało się rozpocząć sesji.” | Serwer może nie działać. Spróbuj później albo powiadom osobę, która uruchamia aplikację. |
| „Najpierw wybierz lub wpisz odpowiedź.” | Przed **Zatwierdź** wpisz słowo albo wybierz odpowiedź. |
| Mikrofon nie działa | Zezwól na mikrofon w ustawieniach strony w przeglądarce i odśwież stronę. Wymowa i tak działa zawodnie (zob. wyżej). |

## Pytania

Zapytaj osobę, która uruchamia dla ciebie aplikację, albo zgłoś problem w repozytorium projektu.
