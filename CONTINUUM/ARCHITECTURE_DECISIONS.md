Opis:

Ten dokument definiuje historię oraz uzasadnienie najważniejszych decyzji architektonicznych podjętych podczas budowy SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest zachowanie informacji:

jakie decyzje architektoniczne zostały podjęte,
dlaczego zostały podjęte,
jakie problemy miały rozwiązać,
jakie były rozważane alternatywy,
jakie konsekwencje wynikają z tych decyzji.

Dokument odpowiada na pytanie:

"Dlaczego SSI został zaprojektowany właśnie w taki sposób?"

Rola dokumentu

ARCHITECTURE_DECISIONS.md jest pamięcią decyzji projektowych (Architecture Decision Record System).

Nie opisuje:

aktualnej struktury kodu,
instrukcji implementacji,
konfiguracji środowiska.

Opisuje:

DECISION

↓

REASON

↓

ALTERNATIVES

↓

CONSEQUENCES
Lokalizacja

Plik znajduje się w katalogu głównym:

CONTINUUM

│
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── ARCHITECTURE_DECISIONS.md
├── DOCUMENTATION_VERSION.md
├── SYSTEM_DOCUMENTATION_MAP.md
└── AI_READING_ORDER.md
Cel dokumentu

ARCHITECTURE_DECISIONS.md zapewnia:

pamięć architektoniczną projektu,
możliwość zrozumienia historii systemu,
ochronę przed powtarzaniem błędnych decyzji,
wsparcie dla AI podczas rozwoju,
kontrolę ewolucji SSI.
Dlaczego ten dokument jest potrzebny?

SSI jest systemem, który będzie rozwijany przez:

ludzi,
wiele agentów AI,
przyszłe wersje samego systemu.

Bez zapisu decyzji powstaje problem:

NOWY AGENT

↓

NIE ZNA POWODU DECYZJI

↓

ZMIENIA ARCHITEKTURĘ

↓

POWRÓT STARYCH PROBLEMÓW

ARCHITECTURE_DECISIONS zapobiega temu.

Struktura decyzji

Każda decyzja posiada format:

ADR NUMBER

↓

TITLE

↓

DATE

↓

STATUS

↓

CONTEXT

↓

DECISION

↓

ALTERNATIVES

↓

CONSEQUENCES
Format wpisu

Przykład:

# ADR-001

## Title

Separate Agent Memory From System Memory


## Date

2026-08-06


## Status

Accepted


## Context

SSI requires different memory types:

- agent experience,
- project knowledge,
- system state.


## Decision

Create independent memory layers:

AGENT MEMORY

PROJECT MEMORY

SYSTEM MEMORY


## Alternatives

Single universal memory database.


## Consequences

Positive:

- better separation,
- easier maintenance,
- improved retrieval.


Negative:

- more complex architecture.
Kategorie decyzji
1. SYSTEM ARCHITECTURE

Decyzje dotyczące:

głównych modułów,
granic systemu,
komunikacji.

Przykład:

SSI uses modular architecture instead of monolith.
2. AI ARCHITECTURE

Decyzje dotyczące:

agentów,
modeli,
pamięci AI,
workflow.

Przykład:

Agents operate through Director Core.
3. DATA ARCHITECTURE

Decyzje dotyczące:

baz danych,
pamięci,
wiedzy.

Przykład:

Knowledge storage separated from operational data.
4. CODE ARCHITECTURE

Decyzje dotyczące:

struktury kodu,
modułów,
interfejsów.
5. DEPLOYMENT ARCHITECTURE

Decyzje dotyczące:

środowiska,
kontenerów,
uruchamiania.
6. SECURITY ARCHITECTURE

Decyzje dotyczące:

dostępu,
ochrony danych,
kontroli agentów.
Status decyzji

Każda decyzja posiada status:

PROPOSED

↓

ACCEPTED

↓

IMPLEMENTED

↓

SUPERSEDED

↓

REJECTED
Proces podejmowania decyzji

Standard:

PROBLEM

↓

ANALYSIS

↓

OPTIONS

↓

DECISION

↓

IMPLEMENTATION

↓

REVIEW
Przykładowe decyzje SSI
ADR-001
Modularna architektura systemu

Decyzja:

SSI zostanie zbudowany jako zestaw niezależnych modułów.

Powód:

skalowanie,
łatwiejsza ewolucja,
możliwość wymiany komponentów.
ADR-002
Director Core jako centralny koordynator

Decyzja:

Agentami zarządza nadrzędny komponent Director Core.

Powód:

kontrola workflow,
zarządzanie zadaniami,
walidacja wyników.
ADR-003
Oddzielny system pamięci

Decyzja:

Pamięć systemu zostaje oddzielona od pamięci agentów.

Powód:

zachowanie kontekstu,
kontrola wiedzy,
możliwość uczenia.
ADR-004
Dokumentacja jako część systemu

Decyzja:

Dokumentacja jest traktowana jako projektowa pamięć SSI.

Powód:

AI musi rozumieć historię,
łatwiejszy rozwój,
brak utraty wiedzy.
Wykorzystanie przez AI

AI przed dużą zmianą powinno sprawdzić:

NEW CHANGE

↓

ARCHITECTURE_DECISIONS

↓

EXISTING CONSTRAINTS

↓

PLAN
Integracja z ewolucją systemu

Proces:

NEW IDEA

↓

ARCHITECTURE ANALYSIS

↓

DECISION RECORD

↓

IMPLEMENTATION

↓

CHANGELOG
Powiązanie z innymi dokumentami
ARCHITECTURE_DECISIONS.md

↓

README.md

↓

CONTRIBUTING.md

↓

CHANGELOG.md

↓

DOCUMENTATION_CODE_ARCHITECTURE

↓

SYSTEM_DOCUMENTATION_MAP.md
Zasady prowadzenia dokumentu
Każda duża decyzja musi być zapisana.
Nie usuwamy starych decyzji.
Zmienione decyzje otrzymują status SUPERSEDED.
Każda decyzja musi mieć uzasadnienie.
AI musi znać ograniczenia wynikające z decyzji.
Cel końcowy

ARCHITECTURE_DECISIONS.md zapewnia, że SSI_SELF_DEVELOPMENT_ENGINE posiada pamięć powodów stojących za własną architekturą.

Dzięki temu:

przyszli programiści rozumieją projekt,
AI nie niszczy wcześniejszych założeń,
decyzje są kontrolowane,
rozwój pozostaje spójny.

Jest to historyczna pamięć architektury SSI i fundament jego długoterminowej ewolucji.