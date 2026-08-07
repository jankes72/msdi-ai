Opis:

Ten dokument definiuje oficjalną kolejność analizowania dokumentacji projektu SSI_SELF_DEVELOPMENT_ENGINE przez sztuczną inteligencję.

Jego celem jest zapewnienie, że AI nie rozpoczyna pracy od przypadkowego dokumentu, tylko najpierw buduje pełny obraz systemu, rozumie architekturę, zasady działania oraz proces budowy.

Dokument rozwiązuje jeden z największych problemów modeli AI — ograniczony kontekst i możliwość utraty zależności między informacjami.

Cel dokumentu

AI_READING_ORDER.md odpowiada na pytania:

Od czego AI ma rozpocząć analizę?
Jakie dokumenty są podstawowe?
Jakie dokumenty należy przeczytać przed implementacją?
Jak AI ma odzyskiwać kontekst projektu?
Jak uniknąć błędnych decyzji wynikających z niepełnej wiedzy?
Główna zasada

AI nie czyta całej dokumentacji jednocześnie.

Obowiązuje model warstwowy:

GLOBAL UNDERSTANDING

↓

SYSTEM UNDERSTANDING

↓

TASK UNDERSTANDING

↓

IMPLEMENTATION KNOWLEDGE

↓

EXECUTION
Kolejność czytania dokumentacji
PHASE 0 — SYSTEM ENTRY
Cel:

Zrozumienie gdzie znajduje się AI.

Pierwsze dokumenty:

README.md

↓

SYSTEM_DOCUMENTATION_MAP.md

↓

DOCUMENTATION_VERSION.md

AI poznaje:

strukturę dokumentacji,
podział wiedzy,
aktualną wersję projektu.
PHASE 1 — PROJECT UNDERSTANDING
Cel:

Zrozumienie celu całego systemu.

Czytane dokumenty:

PROJECT_OVERVIEW.md

↓

02_ARCHITECTURE_OVERVIEW.md

AI poznaje:

czym jest SSI,
główne komponenty,
ogólną architekturę.
PHASE 2 — SYSTEM COMPONENT UNDERSTANDING
Cel:

Poznanie wszystkich głównych elementów.

Kolejność:

DIRECTOR_CORE

↓

ORCHESTRATOR

↓

TASK_MANAGEMENT

↓

AGENT_SYSTEM

↓

MEMORY_SYSTEM

↓

EXECUTION_ENGINE

Dokumenty:

03_DIRECTOR_CORE_SPECIFICATION.md

04_INTERNAL_ORCHESTRATOR_SPECIFICATION.md

05_TASK_MANAGEMENT_SYSTEM_SPECIFICATION.md

06_AGENT_MEMORY_SYSTEM_SPECIFICATION.md

11_TASK_QUEUE_MANAGER_SPECIFICATION.md

18_EXECUTION_ENGINE_SPECIFICATION.md
PHASE 3 — AI OPERATION UNDERSTANDING
Cel:

Poznanie zasad pracy AI.

Czytane:

DOCUMENTATION_AI_DEVELOPMENT_SYSTEM

↓

00_DOCUMENTATION_INDEX.md

↓

02_AI_CONTEXT_MANAGEMENT.md

↓

05_AI_BUILD_PROCESS.md

↓

10_TASK_EXECUTION_PROTOCOL.md

↓

11_AI_DECISION_RULES.md

AI uczy się:

jak analizować zadania,
jak podejmować decyzje,
jak zarządzać kontekstem.
PHASE 4 — DEVELOPMENT PROCESS UNDERSTANDING
Cel:

Poznanie procesu budowania.

Czytane:

PROJECT_BUILD_PLAN

↓

00_BUILD_PLAN_INDEX.md

↓

01_PROJECT_BUILD_OBJECTIVE.md

↓

02_SYSTEM_BUILD_OVERVIEW.md

↓

03_BUILD_PHASES.md

AI poznaje:

kolejność budowy,
etapy,
zależności.
PHASE 5 — TASK SPECIFIC READING
Cel:

Czytanie tylko potrzebnej wiedzy.

Zasada:

AI nie ładuje wszystkiego.

Przykład:

Zadanie:

Dodaj system testów.

AI czyta:

TESTING_SYSTEM_SPECIFICATION

↓

12_TESTING_IMPLEMENTATION_PLAN

↓

BUILD_VALIDATION_PLAN

↓

CODE_RULES
PHASE 6 — IMPLEMENTATION PREPARATION

Przed kodowaniem AI sprawdza:

TASK

↓

RELATED DOCUMENTS

↓

DEPENDENCIES

↓

CURRENT SYSTEM STATE

↓

IMPLEMENTATION PLAN
PHASE 7 — EXECUTION

Dopiero wtedy:

PLAN

↓

CODE

↓

TEST

↓

VALIDATE

↓

DOCUMENT
Mechanizm odzyskiwania kontekstu

Jeżeli AI utraci kontekst:

Nie zaczyna od początku.

Wykonuje:

CURRENT TASK

↓

SYSTEM MAP

↓

RELATED DOCUMENT

↓

CURRENT STATE

↓

CONTINUE
Priorytet dokumentów

Nie wszystkie dokumenty mają taki sam poziom ważności.

Hierarchia:


LEVEL 1

README
SYSTEM MAP


↓

LEVEL 2

ARCHITECTURE
SPECIFICATIONS


↓

LEVEL 3

AI RULES


↓

LEVEL 4

BUILD PLAN


↓

LEVEL 5

IMPLEMENTATION DETAILS
Zasada minimalnego kontekstu

AI pobiera tylko potrzebne informacje.

Proces:

TASK

↓

FIND DOMAIN

↓

LOAD DOCUMENTS

↓

EXECUTE

Korzyści:

mniejsze zużycie kontekstu,
większa dokładność,
mniej błędnych decyzji.
Integracja z pamięcią AI

Po wykonaniu zadania:

TASK RESULT

↓

DOCUMENT UPDATE

↓

MEMORY SAVE

↓

KNOWLEDGE UPDATE
Integracja z innymi dokumentami

AI_READING_ORDER.md współpracuje z:

README.md

↓

SYSTEM_DOCUMENTATION_MAP.md

↓

02_AI_CONTEXT_MANAGEMENT.md

↓

04_KNOWLEDGE_NAVIGATION_SYSTEM.md

↓

05_AI_BUILD_PROCESS.md
Cel końcowy

AI_READING_ORDER.md zapewnia, że SSI_SELF_DEVELOPMENT_ENGINE posiada kontrolowany sposób zdobywania wiedzy.

Dzięki temu AI:

nie gubi kontekstu,
nie czyta przypadkowych informacji,
rozumie zależności,
pobiera tylko potrzebną wiedzę,
może samodzielnie pracować z dużą dokumentacją.

Dokument jest algorytmem nauki i nawigacji po wiedzy projektowej dla AI.