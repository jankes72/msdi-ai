Opis:

Ten dokument definiuje szczegółową specyfikację API systemu zarządzania zadaniami (Task API) w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie, jak system tworzy, opisuje, przydziela, monitoruje, wykonuje oraz zamyka zadania wykonywane przez agentów AI i moduły systemowe.

Jeżeli:

05_TASK_DATA_MODEL.md opisuje strukturę danych zadania,
TASK_MANAGEMENT_SYSTEM_SPECIFICATION.md opisuje logikę zarządzania zadaniami,
04_AGENT_API_SPECIFICATION.md opisuje komunikację z agentami,

to:

05_TASK_API_SPECIFICATION.md definiuje sposób, w jaki cały system komunikuje się z mechanizmem zadań.

Cel dokumentu

05_TASK_API_SPECIFICATION.md odpowiada na pytania:

Jak tworzone jest nowe zadanie?
Jak zadanie trafia do odpowiedniego agenta?
Jak system śledzi postęp pracy?
Jak zadanie zmienia status?
Jak raportowany jest wynik?
Jak obsługiwane są błędy wykonania?
Jak AI może analizować historię wykonanych zadań?
Rola dokumentu

Dokument jest podstawą dla:

Director Core,
Task Queue Manager,
Agent System,
Execution Engine,
Validation System,
Memory System.

Hierarchia:

DIRECTOR CORE

↓

TASK API

↓

TASK MANAGER

↓

TASK QUEUE

↓

AGENT EXECUTION

↓

RESULT
Główna zasada Task API

Zadanie w SSI nie jest tylko poleceniem.

Jest pełnym obiektem posiadającym:

cel,
wymagania,
kontekst,
wykonawcę,
priorytet,
historię,
wynik.

Model:

TASK

{

IDENTITY

OBJECTIVE

CONTEXT

ASSIGNMENT

EXECUTION

RESULT

MEMORY

}
Architektura Task API
              SSI CORE

                  |

              TASK API

                  |

--------------------------------

|             |                |

TASK        QUEUE          AGENT

MANAGER     MANAGER        SYSTEM

                  |

             EXECUTION ENGINE
1. TASK CREATION API
Tworzenie zadania

Pozwala systemowi tworzyć nowe zadania.

Operacje:

CREATE_TASK()

DUPLICATE_TASK()

IMPORT_TASK()

Przykład:

CREATE_TASK

INPUT:

name:

Create Memory Module


priority:

HIGH


OUTPUT:

task_id:

TASK-001
2. TASK IDENTIFICATION API
Identyfikacja zadania

Każde zadanie posiada:

ID,
nazwę,
wersję,
właściciela.

Przykład:

TASK_ID:

TASK-001


OWNER:

DIRECTOR_CORE
3. TASK DESCRIPTION API
Opis zadania

Zawiera:

cel,
wymagania,
ograniczenia,
oczekiwany rezultat.

Przykład:

OBJECTIVE:

Implement API module


REQUIREMENTS:

Documentation + Tests
4. TASK ASSIGNMENT API
Przydzielanie zadania

Łączy zadanie z wykonawcą.

Operacje:

ASSIGN_TASK()

CHANGE_ASSIGNEE()

REMOVE_ASSIGNMENT()

Przepływ:

TASK

↓

TASK API

↓

PROGRAMMER_AGENT
5. TASK PRIORITY API
Zarządzanie priorytetem

Poziomy:

CRITICAL

HIGH

NORMAL

LOW

Operacje:

SET_PRIORITY()

GET_PRIORITY()
6. TASK STATUS API
Zarządzanie stanem zadania

Cykl życia:

CREATED

↓

PLANNED

↓

ASSIGNED

↓

RUNNING

↓

VALIDATION

↓

COMPLETED

↓

ARCHIVED

Operacje:

GET_STATUS()

UPDATE_STATUS()
7. TASK EXECUTION API
Uruchamianie wykonania

Operacje:

START_TASK()

PAUSE_TASK()

RESUME_TASK()

STOP_TASK()
8. TASK PROGRESS API
Monitorowanie postępu

System zapisuje:

procent wykonania,
aktualny etap,
wykonane kroki.

Przykład:

TASK:

Build API


PROGRESS:

65%

Operacje:

UPDATE_PROGRESS()

GET_PROGRESS()
9. TASK RESULT API
Obsługa wyników

Każde zadanie zwraca rezultat.

Operacje:

SUBMIT_RESULT()

GET_RESULT()

VALIDATE_RESULT()

Model:

TASK

↓

RESULT

↓

VALIDATION

↓

MEMORY
10. TASK DEPENDENCY API
Zależności zadań

Pozwala budować kolejność pracy.

Przykład:

TASK A

↓

TASK B

↓

TASK C

Operacje:

ADD_DEPENDENCY()

CHECK_DEPENDENCY()
11. TASK QUEUE API
Kolejka zadań

Obsługuje:

oczekujące zadania,
kolejność,
priorytety.

Operacje:

ADD_TO_QUEUE()

GET_NEXT_TASK()

REMOVE_TASK()
12. TASK CONTEXT API
Kontekst zadania

Każde zadanie posiada:

projekt,
dokumentację,
wymagania,
historię.

Schemat:

TASK

+

PROJECT CONTEXT

+

MEMORY CONTEXT

+

AGENT CONTEXT
13. TASK ERROR API
Obsługa błędów

Przypadki:

brak wykonania,
błąd agenta,
konflikt wymagań.

Proces:

ERROR

↓

ANALYSIS

↓

RETRY

↓

FAILURE REPORT
14. TASK HISTORY API
Historia zadań

Przechowuje:

przebieg pracy,
decyzje,
wyniki.

Operacje:

GET_HISTORY()

STORE_EVENT()
15. TASK MEMORY INTEGRATION API
Połączenie z pamięcią

Po zakończeniu:

TASK RESULT

↓

ANALYSIS

↓

MEMORY UPDATE

↓

KNOWLEDGE EXTRACTION
16. TASK SECURITY API
Kontrola dostępu

Sprawdza:

kto może tworzyć zadania,
kto może je wykonywać,
kto może zmieniać status.
17. TASK VERSIONING API
Wersjonowanie

Obsługuje zmiany:

TASK VERSION 1

↓

TASK VERSION 2
Przykład pełnego procesu
DIRECTOR_CORE

↓

CREATE_TASK()

↓

TASK_MANAGER

↓

ASSIGN_TASK()

↓

PROGRAMMER_AGENT

↓

EXECUTION

↓

RESULT

↓

VALIDATION_AGENT

↓

MEMORY_UPDATE
Integracja z innymi dokumentami

05_TASK_API_SPECIFICATION.md współpracuje z:

05_TASK_DATA_MODEL.md

↓

11_TASK_QUEUE_MANAGER_SPECIFICATION.md

↓

04_AGENT_API_SPECIFICATION.md

↓

13_REQUEST_RESPONSE_MODEL.md

↓

14_ERROR_HANDLING_API.md

↓

17_API_TESTING_SPECIFICATION.md
Cel końcowy

05_TASK_API_SPECIFICATION.md definiuje centralny interfejs zarządzania pracą w SSI_SELF_DEVELOPMENT_ENGINE.

Dzięki niemu system może:

tworzyć zadania,
planować wykonanie,
przydzielać pracę agentom,
kontrolować postęp,
analizować wyniki,
uczyć się na podstawie wykonanych działań.

Dokument jest systemem nerwowym procesu pracy autonomicznego środowiska AI.