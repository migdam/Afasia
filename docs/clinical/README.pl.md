# Podstawy kliniczne

[English](README.md)

> **Status: oczekuje na ocenę kliniczną.** Żaden logopeda ani neurologopeda nie ocenił jeszcze tego dokumentu, sposobu działania ćwiczeń ani żadnego ćwiczenia (backlog H1). Dopóki nie zatwierdzi ich osoba z odpowiednimi kwalifikacjami, wszystko, co tu opisano, jest planem, a nie zaleceniem klinicznym.

Aplikacja służy do ćwiczeń między spotkaniami z logopedą. Wspiera terapię, a nie ją zastępuje, i nie twierdzi niczego o skuteczności ani o leczeniu (zasada C6 w [`loop/PROMPT.md`](../../loop/PROMPT.md)).

## Co mówią badania, w skrócie

- **Terapia logopedyczna pomaga.** Przegląd Cochrane obejmujący 57 badań (Brady i in., 2016) wykazał, że terapia logopedyczna poprawia komunikację w codziennym życiu w porównaniu z brakiem terapii. Korzyści z bardziej intensywnej terapii zaciemniało to, że więcej osób z niej rezygnowało.
- **Ćwiczenia na komputerze pomagają w odnajdywaniu ćwiczonych słów, ale nie w rozmowie.** W badaniu Big CACTUS (Palmer i in., 2019; 278 osób z przewlekłą afazją po udarze) pół roku samodzielnych ćwiczeń na komputerze w domu, ze słowami wybranymi dla każdej osoby, poprawiło odnajdywanie tych słów. Nie poprawiło rozmowy ani jakości życia.

Dlatego aplikacja musi:

- pozwalać ćwiczyć **własne słowa**: słowa i zdjęcia wybrane razem z pacjentem, opiekunem lub logopedą (zasada C2; jeszcze tego nie ma, backlog P2-2);
- nigdy nie twierdzić, że ćwiczenia w niej poprawiają rozmowę.

## Rodzaje ćwiczeń

Każdy rodzaj ćwiczeń, który zna aplikacja: co robi dziś i na czym powinien się opierać.

### Nazywanie słów (`word_naming`)

- **Dziś:** aplikacja pokazuje krótki opis, np. „Małe zwierzę domowe, które mruczy i miauczy”, a osoba wpisuje słowo. Od P2-2a pojęcia są w `backend/content/concepts.json`, po polsku i po angielsku, a sesje są w języku danej osoby. Nie ma jeszcze obrazków (H2), więc opis zastępuje obrazek. Polecenie nigdy nie zawiera odpowiedzi (C4, sprawdza to `backend/tests/test_content.py`).
- **Podstawa:** ćwiczenie nazywania przy trudnościach z odnajdywaniem słów (anomii), z pomocą podawaną stopniowo:
  - **Hierarchia podpowiedzi:** gdy słowo nie przychodzi, podaje się podpowiedzi po kolei, od najmniejszej do największej pomocy (Linebaugh, Shisler i Lehner, 2005). Zaplanowane jako backlog P2-3: podpowiedź znaczeniowa, potem pierwsza głoska lub litera, potem całe słowo do powtórzenia.
  - **Analiza cech semantycznych (SFA):** omawianie cech przedmiotu, takich jak kategoria, zastosowanie, miejsce i właściwości, by pomóc przywołać jego nazwę (Boyle i Coelho, 1995: opis jednego przypadku).
  - **Analiza komponentów fonologicznych (PCA):** to samo podejście, ale z dźwiękami słowa, np. jego pierwszą głoską i liczbą sylab (Leonard, Rochon i Laird, 2008).
- **Od P2-3:** przycisk Podpowiedź podaje podpowiedzi po jednej: cechy (grupa, zastosowanie, miejsce), potem pierwszą literę, potem całe słowo. Poziom podpowiedzi jest zapisywany, a poprawna odpowiedź zachowuje 100/75/50/25% punktów po 0–3 podpowiedziach (tymczasowe proporcje, oczekują na ocenę).
- **Braki:** nie ma jeszcze pierwszej głoski w formie nagrania (H3) ani obrazków. Ćwiczenia są tymczasowe.

### Uzupełnianie zdań (`sentence_completion`)

- **Dziś:** zdanie z luką („Niebo jest ___”) i cztery słowa do wyboru, za każdym razem w innej kolejności. Wszystkie cztery pasują do luki gramatycznie; tylko jedno pasuje znaczeniem. Ćwiczenia są w `backend/content/sentences.json`, po polsku i po angielsku.
- **Podstawa:** żadne z uznanych podejść opisanych w tym dokumencie nie jest zadaniem polegającym na uzupełnianiu luki z wyborem odpowiedzi. Bliższym wzorem pracy na poziomie zdania jest **VNeST (Verb Network Strengthening Treatment)**, w którym ćwiczy się przywoływanie wyrazów treściowych w zdaniach budowanych wokół czasownika: kto wykonuje czynność i na czym (Edmonds, Nadeau i Kiran, 2009). Czy przebudować ten rodzaj ćwiczeń w tym kierunku, powinien ocenić logopeda.
- **Braki:** podstawa obecnego zadania: [citation needed].

### Wymowa (`pronunciation`)

- **Dziś:** słowo lub zwrot do powiedzenia („Powiedz: Cześć”; `backend/content/phrases.json`, po polsku i po angielsku), które osoba nagrywa. Odpowiedź ocenia rozpoznawanie mowy przeglądarki, jeśli osoba się na nie zgodzi.
- **Podstawa:** powtarzanie słów i zwrotów to częste zadanie w terapii [citation needed].
- **Braki:** rozpoznawanie mowy zawodzi przy mowie osób z afazją, więc nie może być jedynym sędzią; osoba powinna móc sama ocenić swoją wypowiedź albo nagranie powinien odsłuchać logopeda (zasada C5; backlog P2-7).

### Rozpoznawanie obrazów (`image_recognition`)

- **Dziś:** niedostępne. Nie ma obrazków (H2), więc ten rodzaj nie ma ćwiczeń.
- **Podstawa:** planowane dopasowywanie słowa do obrazka (rozumienie ze słuchu lub czytanie) [citation needed].

### Planowane: trening skryptów

Ćwiczenie krótkich, ważnych dla danej osoby wypowiedzi z codziennych rozmów, aż zaczną przychodzić bez wysiłku (Youmans, Holland, Muñoz i Bourgeois, 2005: dwie osoby z afazją niepłynną). W tym badaniu obie osoby opanowały swoje skrypty. Na ile przenosi się to na inne wypowiedzi, jest mniej jasne [citation needed]. Tego jeszcze nie ma w aplikacji.

## Model treści

Backlog P2-2 zastępuje ćwiczenia zapisane w kodzie wersjonowanymi plikami z treścią. Każde ćwiczenie powinno zawierać:

- język;
- rodzaj oraz docelowe słowo lub zwrot;
- polecenie;
- podpowiedzi, w kolejności;
- obrazek lub nagranie, ze źródłem i licencją (`frontend/assets/CREDITS.md`);
- cechy, które czynią je łatwiejszym lub trudniejszym;
- stan oceny: „oczekuje na ocenę kliniczną”, dopóki nie zatwierdzi go wskazana z imienia i nazwiska osoba, z datą.

## Jak ocenia się treść

1. Nowe lub zmienione ćwiczenia oznacza się jako „oczekuje na ocenę kliniczną” (zasada C7).
2. Logopeda z odpowiednimi kwalifikacjami ocenia je w obu językach (backlog H1). Ćwiczenia po polsku muszą być napisane naturalną polszczyzną, a nie przetłumaczone słowo w słowo.
3. Dopiero wtedy oznacza się je jako zatwierdzone, z osobą oceniającą i datą. Automatyczna pętla, która rozwija ten projekt, nigdy niczego nie zatwierdza.

## Bibliografia

Sprawdzono 15 października 2026 r. w rekordach wydawców i repozytoriów. Pełnych tekstów nie czytano; to, co dokument mówi o każdym badaniu, ogranicza się do informacji z tych rekordów. Inicjały autorów podano tylko tam, gdzie były w rekordach.

- Boyle & Coelho (1995). Application of semantic feature analysis as a treatment for aphasic dysnomia. *American Journal of Speech-Language Pathology, 4*(4), 94–98. https://doi.org/10.1044/1058-0360.0404.94
- Brady, M. C., Kelly, H., Godwin, J., Enderby, P., & Campbell, P. (2016). Speech and language therapy for aphasia following stroke. *Cochrane Database of Systematic Reviews*, 2016(6), CD000425. https://doi.org/10.1002/14651858.CD000425.pub4
- Edmonds, Nadeau & Kiran (2009). Effect of Verb Network Strengthening Treatment (VNeST) on lexical retrieval of content words in sentences in persons with aphasia. *Aphasiology, 23*(3), 402–424. https://doi.org/10.1080/02687030802291339
- Leonard, C., Rochon, E., & Laird, L. (2008). Treating naming impairments in aphasia: Findings from a phonological components analysis treatment. *Aphasiology, 22*(9), 923–947. (DOI niesprawdzony).
- Linebaugh, C. W., Shisler, R., & Lehner, L. (2005). Cueing hierarchies and word retrieval: A therapy program. *Aphasiology, 19*(1), 77–92. (DOI niesprawdzony).
- Palmer, R., et al. (2019). Self-managed, computerised speech and language therapy for patients with chronic aphasia post-stroke compared with usual care or attention control (Big CACTUS): a multicentre, single-blinded, randomised controlled trial. *The Lancet Neurology, 18*(9), 821–833. https://doi.org/10.1016/S1474-4422(19)30192-9
- Youmans, Holland, Muñoz & Bourgeois (2005). Script training and automaticity in two individuals with aphasia. *Aphasiology, 19*(3–5), 435–450. https://doi.org/10.1080/02687030444000877
