Opis:

Ten dokument jest mapą zależności całej dokumentacji projektu SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest pokazanie AI oraz człowiekowi, jak wszystkie obszary dokumentacji są ze sobą połączone, jaka jest ich hierarchia oraz jaki przepływ wiedzy obowiązuje w systemie.

Dokument pełni rolę mapy architektury informacji — nie opisuje szczegółowo modułów, ale pokazuje, gdzie znajduje się dana wiedza i jak należy się po niej poruszać.

Cel dokumentu

SYSTEM_DOCUMENTATION_MAP.md odpowiada na pytania:

Jak podzielona jest dokumentacja projektu?
Który dokument opisuje konkretny obszar?
Jakie dokumenty zależą od siebie?
Jaka jest kolejność analizy informacji?
Gdzie AI powinno szukać odpowiedzi?
Jak połączyć specyfikację, zasady AI i plan budowy?
Rola dokumentu w systemie

Jest to drugi poziom po README.md.

Schemat:

README.md

↓

SYSTEM_DOCUMENTATION_MAP.md

↓

SPECIFIC DOCUMENTATION AREA

↓

IMPLEMENTATION
Główna struktura wiedzy

Cała dokumentacja SSI jest podzielona na trzy główne warstwy:

SSI_DOCUMENTATION

│
├── SYSTEM SPECIFICATION
│
├── AI DEVELOPMENT RULES
│
└── BUILD EXECUTION PLAN
WARSTWA 1 — SYSTEM SPECIFICATION
DOCUMENTATION_SSI_SELF_DEVELOPMENT_ENGINE

Cel:

Opisuje co budujemy.

Zawiera kompletną specyfikację systemu.

Struktura:

DOCUMENTATION_SSI_SELF_DEVELOPMENT_ENGINE

│
├── ARCHITECTURE
│
├── CORE SYSTEMS
│
├── AGENTS
│
├── MEMORY
│
├── EXECUTION
│
├── KNOWLEDGE
│
├── TESTING
│
└── INTEGRATION

Przykładowe powiązania:

ARCHITECTURE_OVERVIEW

↓

DIRECTOR_CORE

↓

ORCHESTRATOR

↓

TASK_SYSTEM

↓

AGENTS

↓

MEMORY

↓

EXECUTION
WARSTWA 2 — AI DEVELOPMENT SYSTEM
DOCUMENTATION_AI_DEVELOPMENT_SYSTEM

Cel:

Opisuje jak AI ma pracować z projektem.

Nie opisuje kodu.

Opisuje zasady działania AI.

Struktura:

DOCUMENTATION_AI_DEVELOPMENT_SYSTEM

│
├── CONTEXT MANAGEMENT
│
├── DOCUMENT RULES
│
├── KNOWLEDGE NAVIGATION
│
├── BUILD PROCESS
│
├── AGENT RULES
│
├── MEMORY RULES
│
└── SECURITY

Przepływ:

AI REQUEST

↓

CONTEXT ANALYSIS

↓

DOCUMENT SEARCH

↓

DECISION

↓

ACTION
WARSTWA 3 — PROJECT BUILD PLAN
PROJECT_BUILD_PLAN

Cel:

Opisuje jak system zostanie wykonany.

Struktura:

PROJECT_BUILD_PLAN

│
├── OBJECTIVES
│
├── PHASES
│
├── MODULE ORDER
│
├── DEPENDENCIES
│
├── IMPLEMENTATION
│
├── TESTING
│
├── DEPLOYMENT
│
└── CHANGE MANAGEMENT

Przepływ budowy:

PLAN

↓

IMPLEMENTATION

↓

TEST

↓

VALIDATION

↓

DEPLOYMENT
Mapa zależności głównych dokumentów
PROJECT_OVERVIEW

        ↓

ARCHITECTURE_OVERVIEW

        ↓

SYSTEM_SPECIFICATIONS

        ↓

AI_OPERATION_RULES

        ↓

BUILD_PLAN

        ↓

IMPLEMENTATION

        ↓

VALIDATION

        ↓

SYSTEM_EVOLUTION
Mapa przepływu wiedzy

Informacja w systemie przechodzi przez:

IDEA

↓

DOCUMENTATION

↓

ARCHITECTURE

↓

IMPLEMENTATION

↓

TEST

↓

RESULT

↓

MEMORY

↓

KNOWLEDGE
Mapa dla agentów AI

Każdy agent korzysta z innych dokumentów.

Director Agent

Czyta:

ARCHITECTURE

+

BUILD PLAN

+

PROJECT STATE

Cel:

Planowanie pracy.

Programmer Agent

Czyta:

MODULE SPECIFICATION

+

CODE RULES

+

TASK

Cel:

Implementacja.

Validation Agent

Czyta:

TESTING SYSTEM

+

VALIDATION PLAN

Cel:

Kontrola jakości.

Documentation Agent

Czyta:

DOCUMENTATION RULES

+

SYSTEM MAP

Cel:

Aktualizacja wiedzy.

Zasada wyszukiwania informacji

AI nie przeszukuje całej dokumentacji losowo.

Proces:

QUESTION

↓

IDENTIFY DOMAIN

↓

OPEN RELATED MAP

↓

READ SPECIFICATION

↓

EXECUTE ACTION
Przykład użycia

Zadanie:

Dodaj nowego agenta AI.

AI sprawdza:

SYSTEM_DOCUMENTATION_MAP

↓

AGENT SYSTEM

↓

AGENT SPECIFICATION

↓

TASK MANAGEMENT

↓

BUILD PLAN

↓

IMPLEMENTATION
Aktualizacja mapy

Jeżeli powstaje nowy system:

np.

SECURITY ENGINE

należy:

dodać dokument specyfikacji,
dodać połączenia,
określić zależności,
zaktualizować mapę.
Integracja z innymi dokumentami

SYSTEM_DOCUMENTATION_MAP.md współpracuje z:

README.md

↓

AI_READING_ORDER.md

↓

00_DOCUMENTATION_INDEX.md

↓

PROJECT_OVERVIEW.md

↓

PROJECT_BUILD_PLAN
Cel końcowy

SYSTEM_DOCUMENTATION_MAP.md zapewnia, że SSI_SELF_DEVELOPMENT_ENGINE posiada uporządkowaną strukturę wiedzy.

Dzięki temu AI:

wie gdzie szukać informacji,
rozumie zależności,
nie traci kontekstu,
analizuje dokumentację warstwowo,
może samodzielnie nawigować po projekcie.

Dokument jest mapą pamięci projektowej całego systemu dokumentacji SSI_SELF_DEVELOPMENT_ENGINE.