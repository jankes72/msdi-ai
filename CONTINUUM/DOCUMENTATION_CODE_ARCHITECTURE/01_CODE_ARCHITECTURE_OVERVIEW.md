Opis:

Ten dokument definiuje ogólną architekturę kodu systemu SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest opisanie, jak zorganizowany jest cały kod systemu na poziomie logicznym, jakie istnieją warstwy, jakie są główne zasady projektowe oraz jak poszczególne części kodu współpracują ze sobą.

Dokument odpowiada na pytanie:

"Jak wygląda ogólny projekt kodu SSI i jakie zasady obowiązują podczas jego tworzenia?"

Cel dokumentu

01_CODE_ARCHITECTURE_OVERVIEW.md definiuje:

główne warstwy kodu,
podział odpowiedzialności,
architekturę modułową,
przepływ zależności,
zasady komunikacji kodu,
sposób rozszerzania systemu.
Rola dokumentu

Dokument jest mapą logiczną implementacji SSI.

Poprzednie dokumenty mówiły:

GDZIE znajduje się moduł

oraz:

ZA CO odpowiada moduł

Ten dokument opisuje:

JAK moduły są zbudowane jako kod
Miejsce w architekturze SSI

Schemat:

SYSTEM IDEA

↓

SYSTEM ARCHITECTURE

↓

PROJECT STRUCTURE

↓

CODE ARCHITECTURE

↓

SOURCE CODE
Główna zasada architektury kodu

SSI jest budowane jako:

MODULAR SYSTEM

+

SERVICE BASED ARCHITECTURE

+

INTERFACE DRIVEN DESIGN

+

EVENT COMMUNICATION
Główne warstwy kodu SSI

Architektura kodu składa się z sześciu głównych poziomów:

┌────────────────────────────┐
│     APPLICATION LAYER      │
│  Agenci, zadania, workflow │
└──────────────┬─────────────┘
               │
┌──────────────▼─────────────┐
│      SERVICE LAYER         │
│ Memory, Model, Knowledge   │
└──────────────┬─────────────┘
               │
┌──────────────▼─────────────┐
│      MODULE LAYER          │
│ Core, Message, Agent       │
└──────────────┬─────────────┘
               │
┌──────────────▼─────────────┐
│    INTERFACE LAYER         │
│ API, Events, Messages      │
└──────────────┬─────────────┘
               │
┌──────────────▼─────────────┐
│      DATA LAYER            │
│ Database, Storage          │
└────────────────────────────┘
1. APPLICATION LAYER
Lokalizacja:
AGENT_SYSTEM/

TASK_SYSTEM/

WORKFLOW_ENGINE/
Odpowiedzialność:

Warstwa realizująca działania systemu.

Zawiera:

agentów AI,
wykonywanie zadań,
procesy decyzyjne,
workflow.
Przykład:
Agent otrzymuje zadanie

↓

Analizuje

↓

Tworzy plan

↓

Wysyła komunikaty
2. SERVICE LAYER
Lokalizacja:
MEMORY_SYSTEM/

KNOWLEDGE_SYSTEM/

MODEL_SYSTEM/
Odpowiedzialność:

Dostarcza usługi dla innych modułów.

Przykłady:

MemoryService

KnowledgeService

ModelService
Zasada:

Moduły nie implementują własnej pamięci lub modeli.

Korzystają z usług.

3. MODULE LAYER
Lokalizacja:
CORE/

MESSAGE_SYSTEM/

SECURITY/
Odpowiedzialność:

Podstawowe mechanizmy systemu.

Przykłady:

SystemCore

MessageRouter

SecurityManager
4. INTERFACE LAYER
Lokalizacja:
API/

MESSAGE_SYSTEM/
Odpowiedzialność:

Łączenie modułów.

Zapewnia:

kontrakty,
komunikację,
walidację,
wersjonowanie.
5. DATA LAYER
Lokalizacja:
DATABASE/

DATA/
Odpowiedzialność:

Trwałe dane.

Zawiera:

modele danych,
repozytoria,
migracje,
backup.
6. CONTROL LAYER
Lokalizacja:
CORE/

CONFIG/

SECURITY/
Odpowiedzialność:

Kontrola działania systemu.

Obejmuje:

konfigurację,
stan,
bezpieczeństwo,
monitoring.
Zasada zależności kodu

Poprawny kierunek:

APPLICATION

↓

SERVICES

↓

MODULES

↓

INTERFACES

↓

DATA

Niedozwolone:

DATABASE

↓

AGENT LOGIC

lub:

MEMORY

↓

TASK EXECUTION
Architektura modułowa

Każdy moduł posiada własną strukturę:

MODULE_NAME/

├── core/
├── services/
├── models/
├── interfaces/
├── exceptions/
├── tests/
└── README.md
Przykład modułu
AGENT_SYSTEM
AGENT_SYSTEM/

├── core/

│   └── agent_core.py

├── services/

│   └── agent_service.py

├── models/

│   └── agent_model.py

├── interfaces/

│   └── agent_api.py

├── exceptions/

│   └── agent_errors.py

└── tests/
Model komunikacji kodu

Moduły nie wywołują się przypadkowo.

Schemat:

MODULE A

↓

INTERFACE

↓

MESSAGE/API

↓

MODULE B

Przykład:

Agent

↓

Message API

↓

Memory System
Standard tworzenia nowego modułu

Każdy nowy moduł musi posiadać:

1. Core logic

2. Service layer

3. Interface

4. Data model

5. Exception handling

6. Tests

7. Documentation
Rozdzielenie odpowiedzialności

Przykład:

Agent:

Może:

✅ planować
✅ podejmować decyzje
✅ komunikować się

Nie może:

❌ zapisywać bezpośrednio do bazy
❌ zarządzać modelem danych

Database:

Może:

✅ przechowywać dane
✅ wykonywać zapytania

Nie może:

❌ wykonywać logiki AI

Przygotowanie pod Self Development Engine

Architektura musi umożliwiać:

ANALYSIS

↓

CODE UNDERSTANDING

↓

CHANGE PROPOSAL

↓

TEST

↓

DEPLOYMENT

Dlatego każdy element kodu musi być:

nazwany,
opisany,
odizolowany,
testowalny.
Powiązanie z kolejnymi dokumentami
00_CODE_ARCHITECTURE_INDEX.md

↓

01_CODE_ARCHITECTURE_OVERVIEW.md

↓

02_SOURCE_CODE_STRUCTURE.md

↓

03_MODULE_INTERNAL_ARCHITECTURE.md

↓

04_CLASS_AND_OBJECT_MODEL.md
Cel końcowy

01_CODE_ARCHITECTURE_OVERVIEW.md definiuje fundamentalny model budowy kodu SSI_SELF_DEVELOPMENT_ENGINE.

Po zastosowaniu zasad:

kod jest modularny,
zależności są kontrolowane,
każdy komponent ma swoje miejsce,
system może być rozwijany przez ludzi oraz agentów AI.

Jest to mapa konstrukcyjna kodu SSI — opis tego, jak z pojedynczych modułów powstaje jeden spójny system programistyczny.