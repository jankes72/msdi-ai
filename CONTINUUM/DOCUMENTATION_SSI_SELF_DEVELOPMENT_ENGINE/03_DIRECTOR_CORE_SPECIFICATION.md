SSI_SELF_DEVELOPMENT_ENGINE
DIRECTOR CORE SPECIFICATION
1. Cel dokumentu

Dokument opisuje specyfikację modułu DIRECTOR_CORE.

DIRECTOR_CORE jest centralnym modułem zarządzającym działem programistycznym SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem nie jest bezpośrednie tworzenie kodu.

Jego zadaniem jest:

rozumienie otrzymanych celów,
analiza wymagań,
zarządzanie procesem,
podejmowanie decyzji organizacyjnych,
kontrola realizacji zadań,
komunikacja z głównym SSI.
2. Rola DIRECTOR_CORE

DIRECTOR_CORE pełni funkcję dyrektora działu programistycznego.

Jest warstwą pośrednią pomiędzy:

głównym SSI,
zespołem wykonawczym,
agentami,
systemem pamięci.

Przepływ informacji:

GŁÓWNY SSI
     |
     |
DIRECTOR_CORE
     |
     |
INTERNAL_ORCHESTRATOR
     |
     |
AGENTS
     |
     |
RESULTS
     |
     |
DIRECTOR_CORE
3. Główne zadania DIRECTOR_CORE
3.1 Odbiór wymagań

Director otrzymuje informacje dotyczące:

nowych funkcji,
zmian systemowych,
problemów,
potrzeb rozwoju.

Nie otrzymuje tylko instrukcji technicznych.

Otrzymuje cel.

Przykład:

Nie:

"napisz plik Python"

Tylko:

"potrzebujemy systemu zarządzania zadaniami dla działu programistycznego".

Director określa sposób realizacji.

3.2 Analiza zadania

Po otrzymaniu zadania Director wykonuje analizę:

czego dotyczy problem,
jakie moduły są potrzebne,
jakie są zależności,
jakie zasoby są wymagane,
jaki będzie zakres pracy.

Wynikiem jest wstępny plan działania.

3.3 Planowanie

Director dzieli większe cele na mniejsze zadania.

Przykład:

Cel:

"Stworzyć system agentów programistycznych."

Podział:

Dokumentacja architektury.
System pamięci.
System komunikacji.
Zarządzanie agentami.
Wykonawca kodu.
Testy.
Integracja.

Każdy etap otrzymuje własne zadanie.

3.4 Zarządzanie priorytetami

Director kontroluje kolejkę projektów.

Każde zadanie posiada:

ważność,
pilność,
zależności,
wymagany czas.

Director może:

zatwierdzić rozpoczęcie,
odłożyć zadanie,
zmienić kolejność,
poprosić o dodatkowe informacje.
4. Kontakt z głównym SSI

Director posiada kanał komunikacji z głównym SSI.

Raportuje:

postęp prac,
problemy,
wymagane decyzje,
zakończone etapy.

Jeżeli problem wymaga decyzji człowieka, Director generuje zgłoszenie.

5. Kontakt z człowiekiem

Nie wszystkie decyzje mogą być wykonywane autonomicznie.

Director przekazuje do człowieka:

kwestie wymagające oceny,
niejasne wymagania,
decyzje biznesowe,
wybór źródeł danych,
zatwierdzenie kierunku.

Człowiek jest nadrzędnym punktem decyzyjnym.

6. Współpraca z INTERNAL_ORCHESTRATOR

Director nie zarządza bezpośrednio każdym agentem.

Przekazuje zadania do:

DIRECTOR_CORE
        |
        |
INTERNAL_ORCHESTRATOR
        |
        |
AGENTS

Orchestrator odpowiada za wykonanie.

Director odpowiada za decyzję.

7. System pamięci DIRECTOR_CORE

Director posiada własną pamięć.

Struktura:

DIRECTOR_MEMORY

├── SHORT_TERM_MEMORY
│
├── LONG_TERM_MEMORY
│
├── PROJECT_HISTORY
│
└── DECISION_HISTORY
7.1 SHORT_TERM_MEMORY

Przechowuje aktualną sytuację:

obecne zadania,
aktywne projekty,
bieżące decyzje.
7.2 LONG_TERM_MEMORY

Przechowuje:

doświadczenie,
wcześniejsze rozwiązania,
zasady działania.
7.3 PROJECT_HISTORY

Historia projektów:

wykonane etapy,
problemy,
rozwiązania,
wyniki.
7.4 DECISION_HISTORY

Historia decyzji dyrektora:

dlaczego podjęto decyzję,
jakie były alternatywy,
jaki był rezultat.
8. Zasada działania DIRECTOR_CORE

Director działa według procesu:

RECEIVE
   |
ANALYZE
   |
PLAN
   |
PRIORITIZE
   |
ASSIGN
   |
MONITOR
   |
VERIFY
   |
REPORT
9. Ograniczenia DIRECTOR_CORE

Director nie może:

samodzielnie zmieniać głównej architektury SSI,
ignorować ustalonych zasad systemu,
wykonywać niezatwierdzonych zmian,
tworzyć chaosu poprzez równoległe zadania.

Każda zmiana musi posiadać uzasadnienie.

10. Przyszły rozwój

W przyszłości DIRECTOR_CORE może otrzymać:

bardziej zaawansowane planowanie,
analizę kosztów obliczeniowych,
przewidywanie czasu wykonania,
ocenę ryzyka,
automatyczne wykrywanie zależności.
11. Podsumowanie

DIRECTOR_CORE jest mózgiem organizacyjnym SSI_SELF_DEVELOPMENT_ENGINE.

Nie jest programistą.

Nie jest wykonawcą.

Jest systemem zarządzania, który:

rozumie cele,
tworzy plany,
kontroluje wykonanie,
wykorzystuje pamięć,
komunikuje się z SSI,
zapewnia uporządkowany rozwój działu.

Jego zadaniem jest sprawienie, aby dział programistyczny działał jak prawdziwy, zorganizowany zespół IT.