SSI_SELF_DEVELOPMENT_ENGINE
ARCHITECTURE OVERVIEW
1. Cel dokumentu

Ten dokument opisuje wewnętrzną architekturę SSI_SELF_DEVELOPMENT_ENGINE.

Dokument określa:

główne komponenty systemu,
zależności między nimi,
przepływ informacji,
sposób komunikacji,
odpowiedzialność poszczególnych modułów.

Dokument dotyczy wyłącznie działu programistycznego SSI_SELF_DEVELOPMENT_ENGINE.

Nie opisuje całej architektury SSI.

2. Główna architektura

SSI_SELF_DEVELOPMENT_ENGINE składa się z kilku współpracujących warstw:

GŁÓWNY SSI
      |
      |
DIRECTOR CORE
      |
      |
INTERNAL ORCHESTRATOR
      |
      |
TASK MANAGEMENT
      |
      |
AGENT SYSTEM
      |
      |
EXECUTION LAYER
      |
      |
VALIDATION + MEMORY + DOCUMENTATION

Każda warstwa posiada określone zadanie.

3. DIRECTOR CORE
Rola

Director Core jest głównym modułem decyzyjnym działu.

Odpowiada za:

odbiór wymagań,
analizę celu,
określenie priorytetów,
zatwierdzanie planu,
komunikację z głównym SSI.

Director Core nie wykonuje bezpośrednio kodu.

Jego rolą jest zarządzanie procesem.

4. INTERNAL ORCHESTRATOR
Rola

Internal Orchestrator jest systemem sterowania wykonaniem.

Jego zadaniem jest:

obsługa kolejki,
kontrolowanie kolejności,
przydzielanie pracy agentom,
monitorowanie statusów.

Orchestrator odpowiada za to, aby system wykonywał zadania w kontrolowany sposób.

5. TASK MANAGEMENT SYSTEM
Rola

Task Management odpowiada za przechowywanie i obsługę zadań.

Każde zadanie posiada:

ID,
nazwę,
opis,
priorytet,
status,
wymagane zasoby,
przypisanego wykonawcę.

Przykładowe statusy:

CREATED
ANALYZING
PLANNED
WAITING
RUNNING
TESTING
COMPLETED
FAILED
6. SYSTEM AGENTÓW

Agenci są wyspecjalizowanymi wykonawcami.

Każdy agent posiada:

swoją rolę,
własny kontekst,
własną pamięć,
historię działań,
zasady działania.

Agent nie otrzymuje całej wiedzy systemu.

Otrzymuje tylko informacje potrzebne do wykonania konkretnego zadania.

7. WARSTWA WYKONAWCZA

Warstwa wykonawcza odpowiada za realizację działań.

Przykłady:

tworzenie plików,
generowanie kodu,
analiza danych,
wykonywanie testów,
aktualizacja dokumentacji.

Każda operacja musi zostać zapisana w historii.

8. SYSTEM PAMIĘCI

Każdy element systemu posiada własną pamięć.

Struktura:

MEMORY

├── SHORT_TERM
│
├── LONG_TERM
│
└── OPERATION_HISTORY
Short Term Memory

Informacje aktualnego zadania.

Long Term Memory

Wiedza zdobyta podczas wcześniejszych działań.

Operation History

Historia wykonanych operacji.

9. SYSTEM KOMUNIKACJI

Komunikacja odbywa się poprzez określone kanały.

Przepływ:

SSI
 |
DIRECTOR
 |
ORCHESTRATOR
 |
AGENT
 |
RESULT
 |
REPORT
 |
DIRECTOR
 |
SSI

Każda komunikacja posiada zapis.

10. Zasada pojedynczego wykonania

System stosuje zasadę:

"Jedno zadanie - jeden kontrolowany proces."

Nie wykonuje wielu niezależnych operacji bez kontroli.

Powody:

stabilność,
kontrola jakości,
ograniczenie błędów,
ograniczenie zużycia zasobów.
11. Praca lokalna i przyszła praca serwerowa

Aktualna wersja systemu działa lokalnie.

Modele uruchamiane są przez środowisko lokalne, np. Ollama.

Architektura jest jednak przygotowana do przyszłego działania serwerowego.

Zmiana środowiska wykonawczego nie zmienia logiki systemu.

Zmienia się jedynie warstwa uruchamiania modeli.

12. Zasada rozwoju

SSI_SELF_DEVELOPMENT_ENGINE rozwija się etapami.

Każdy etap:

posiada dokumentację,
posiada plan,
posiada implementację,
posiada test,
posiada raport.

System rozwija się poprzez kontrolowane dodawanie nowych możliwości.