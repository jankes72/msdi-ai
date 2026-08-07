03_MODULE_INTERNAL_ARCHITECTURE.md
Opis:

Ten dokument definiuje wewnętrzną architekturę każdego modułu kodu SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest opisanie, jak pojedynczy moduł jest zbudowany od środka, jakie posiada warstwy wewnętrzne, jakie komponenty może zawierać oraz jak powinien organizować własną logikę.

Dokument odpowiada na pytanie:

"Jak wygląda budowa wewnętrzna pojedynczego modułu SSI?"

Cel dokumentu

03_MODULE_INTERNAL_ARCHITECTURE.md definiuje:

standard budowy modułów,
wewnętrzny podział odpowiedzialności,
strukturę katalogów modułów,
relacje pomiędzy komponentami,
zasady komunikacji wewnętrznej,
zasady rozszerzania modułów.
Rola dokumentu

Dokument jest przejściem:

SYSTEM ARCHITECTURE

↓

MODULE ARCHITECTURE

↓

CLASS DESIGN

↓

IMPLEMENTATION
Miejsce w dokumentacji
00_CODE_ARCHITECTURE_INDEX.md

↓

01_CODE_ARCHITECTURE_OVERVIEW.md

↓

02_SOURCE_CODE_STRUCTURE.md

↓

03_MODULE_INTERNAL_ARCHITECTURE.md

↓

04_CLASS_AND_OBJECT_MODEL.md
Główna zasada modułu SSI

Każdy moduł jest samodzielną jednostką posiadającą:

OWN LOGIC

+

OWN INTERFACES

+

OWN DATA MODELS

+

OWN VALIDATION

+

OWN TESTS
Definicja modułu

Moduł SSI to:

Zamknięta funkcjonalnie jednostka kodu realizująca określoną odpowiedzialność systemową.

Przykład:

MEMORY_SYSTEM

=

moduł odpowiedzialny za pamięć
Standardowa struktura modułu

Każdy większy moduł powinien posiadać strukturę:

MODULE_NAME/

├── core/
│
├── services/
│
├── interfaces/
│
├── models/
│
├── repositories/
│
├── validators/
│
├── exceptions/
│
├── events/
│
├── config/
│
├── tests/
│
└── README.md
Warstwy wewnętrzne modułu
1. CORE LAYER
Lokalizacja:
module/core/
Odpowiedzialność:

Główna logika modułu.

Zawiera:

podstawowe klasy,
główne mechanizmy,
kontrolę działania.

Przykład:

MemoryCore

MessageCore

AgentCore
2. SERVICE LAYER
Lokalizacja:
module/services/
Odpowiedzialność:

Udostępnianie funkcji modułu innym elementom systemu.

Przykład:

MemoryService

AgentService

TaskService

Schemat:

External Module

↓

Service

↓

Core Logic
3. INTERFACE LAYER
Lokalizacja:
module/interfaces/
Odpowiedzialność:

Kontrolowany dostęp do modułu.

Zawiera:

API,
kontrakty,
adaptery.

Przykład:

agent_interface.py

memory_interface.py
4. MODEL LAYER
Lokalizacja:
module/models/
Odpowiedzialność:

Definicje obiektów danych.

Przykład:

class Agent:

class MemoryEntry:

class Task:
5. REPOSITORY LAYER
Lokalizacja:
module/repositories/
Odpowiedzialność:

Dostęp do danych.

Schemat:

Service

↓

Repository

↓

Database

Moduł nie komunikuje się bezpośrednio z bazą.

6. VALIDATION LAYER
Lokalizacja:
module/validators/
Odpowiedzialność:

Sprawdzanie poprawności danych.

Przykład:

MessageValidator

TaskValidator

AgentValidator
7. EVENT LAYER
Lokalizacja:
module/events/
Odpowiedzialność:

Obsługa zdarzeń.

Przykład:

AgentCreated

TaskCompleted

MemoryUpdated
8. EXCEPTION LAYER
Lokalizacja:
module/exceptions/
Odpowiedzialność:

Błędy modułu.

Przykład:

class AgentNotFoundError

class InvalidMessageError
Przykład pełnego modułu
AGENT_SYSTEM
AGENT_SYSTEM/

├── core/

│   └── agent_core.py


├── services/

│   └── agent_service.py


├── interfaces/

│   └── agent_api.py


├── models/

│   └── agent_model.py


├── repositories/

│   └── agent_repository.py


├── validators/

│   └── agent_validator.py


├── events/

│   └── agent_events.py


├── exceptions/

│   └── agent_errors.py


└── tests/
Przepływ wewnętrzny modułu

Standard:

INPUT

↓

INTERFACE

↓

VALIDATION

↓

SERVICE

↓

CORE

↓

REPOSITORY

↓

OUTPUT
Przykład wykonania

Agent otrzymuje zadanie:

Task API

↓

TaskValidator

↓

TaskService

↓

TaskCore

↓

TaskRepository

↓

Database
Zasady komunikacji wewnętrznej
Moduły wewnętrzne:

Mogą komunikować się przez:

SERVICE

API

EVENT

Nie przez:

bezpośredni import prywatnej klasy

Przykład złego rozwiązania:

from memory.core.internal_manager import InternalMemory

Poprawnie:

from memory.services import MemoryService
Zasada enkapsulacji

Wewnętrzne elementy modułu są prywatne.

Dostęp publiczny:

module/interfaces/
module/services/

Ukryte:

module/core/internal/
Standard nowego modułu

Każdy nowy moduł musi określić:

1. Main responsibility

2. Public interfaces

3. Internal components

4. Data models

5. Events

6. Exceptions

7. Tests
Przykład zależności

Poprawnie:

AGENT_SYSTEM

↓

MemoryService

↓

MEMORY_SYSTEM

↓

MemoryRepository

↓

DATABASE

Niepoprawnie:

AGENT_SYSTEM

↓

DATABASE.connection.py
Przygotowanie pod AI Self Development

Jednolita struktura modułów pozwala agentom AI:

znaleźć logikę,
rozpoznać odpowiedzialność,
analizować błędy,
proponować zmiany.

Proces:

Module Discovery

↓

Structure Analysis

↓

Dependency Analysis

↓

Modification Proposal

↓

Testing
Powiązanie z kolejnymi dokumentami
03_MODULE_INTERNAL_ARCHITECTURE.md

↓

04_CLASS_AND_OBJECT_MODEL.md

↓

05_FUNCTION_AND_METHOD_STRUCTURE.md

↓

06_INTERFACE_IMPLEMENTATION_MODEL.md
Cel końcowy

03_MODULE_INTERNAL_ARCHITECTURE.md definiuje standard budowy każdego modułu SSI_SELF_DEVELOPMENT_ENGINE.

Po zastosowaniu zasad:

moduły są niezależne,
kod jest przewidywalny,
każdy komponent ma swoje miejsce,
rozbudowa systemu jest bezpieczna,
agenci AI mogą analizować strukturę kodu.

Jest to szablon konstrukcyjny modułu SSI — definicja, jak z pojedynczych plików powstaje profesjonalny komponent systemu.