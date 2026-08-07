Opis:

Ten dokument definiuje model implementacji interfejsów w systemie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest opisanie, w jaki sposób moduły systemu udostępniają swoje funkcje, jak komunikują się ze sobą oraz jak realizowane są kontrakty pomiędzy komponentami kodu.

Dokument odpowiada na pytanie:

"Jak moduły SSI komunikują się ze sobą bez bezpośrednego uzależnienia od swojej wewnętrznej implementacji?"

Cel dokumentu

06_INTERFACE_IMPLEMENTATION_MODEL.md definiuje:

strukturę interfejsów,
kontrakty pomiędzy modułami,
publiczne punkty dostępu,
implementację API wewnętrznego,
adaptery,
abstrakcje,
zasady zależności pomiędzy komponentami.
Rola dokumentu

Dokument jest przejściem:

MODULE DESIGN

↓

INTERFACE DESIGN

↓

IMPLEMENTATION

↓

MODULE COMMUNICATION
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

↓

05_FUNCTION_AND_METHOD_STRUCTURE.md

↓

06_INTERFACE_IMPLEMENTATION_MODEL.md

↓

07_CODE_EXECUTION_FLOW.md
Główna zasada interfejsów SSI

Moduły nie komunikują się przez swoje wnętrze.

Komunikacja odbywa się przez:

PUBLIC INTERFACE

↓

SERVICE CONTRACT

↓

IMPLEMENTATION
Przykład problemu
Niepoprawnie:

Agent korzysta bezpośrednio z pamięci:

from memory.core.internal_memory import InternalMemory

memory = InternalMemory()
memory.save(data)

Problem:

Agent zna szczegóły pamięci.
Zmiana Memory System niszczy zależności.
Poprawnie:

Agent korzysta z interfejsu:

memory_service.save(data)

Schemat:

AGENT

↓

MemoryInterface

↓

MemoryService

↓

MemoryCore

↓

Database
Definicja interfejsu

Interfejs SSI jest:

Publiczną definicją sposobu korzystania z modułu bez znajomości jego wewnętrznej implementacji.

Przykład:

class MemoryInterface:

    def save_memory(
        self,
        memory
    ):
        pass
Warstwy interfejsów

Architektura posiada kilka poziomów:

EXTERNAL INTERFACE

↓

SYSTEM INTERFACE

↓

MODULE INTERFACE

↓

INTERNAL INTERFACE
1. EXTERNAL INTERFACE
Odpowiedzialność:

Kontakt ze światem zewnętrznym.

Przykłady:

REST API

CLI

Web Interface

External Services
2. SYSTEM INTERFACE
Odpowiedzialność:

Komunikacja głównych części SSI.

Przykład:

Agent System

↓

Task API

↓

Task System
3. MODULE INTERFACE
Odpowiedzialność:

Komunikacja pomiędzy modułami.

Przykład:

MemoryInterface

TaskInterface

KnowledgeInterface
4. INTERNAL INTERFACE
Odpowiedzialność:

Komunikacja wewnątrz modułu.

Przykład:

MemoryService

↓

MemoryRepository
Struktura interfejsu modułu

Standard:

module/

├── interfaces/

│
├── contracts/

│
├── adapters/

│
└── implementations/
Przykład:
MEMORY_SYSTEM/

├── interfaces/

│   └── memory_interface.py


├── contracts/

│   └── memory_contract.py


├── implementations/

│   └── memory_service.py


└── adapters/

    └── database_adapter.py
Interface vs Implementation

Rozdzielenie:

INTERFACE

=
CO system oferuje


IMPLEMENTATION

=
JAK system to wykonuje
Przykład

Interfejs:

class TaskInterface:

    def create_task():
        pass

Implementacja:

class TaskService(TaskInterface):

    def create_task():

        save_task()

        notify_agent()

        return task
Kontrakty komunikacyjne

Każdy interfejs posiada kontrakt.

Kontrakt definiuje:

INPUT

↓

PROCESS RULES

↓

OUTPUT

↓

ERRORS

Przykład:

create_task()

INPUT:
TaskRequest


OUTPUT:
TaskObject


ERROR:
InvalidTaskError
Dependency Injection

SSI wykorzystuje kontrolowane dostarczanie zależności.

Nie:

class Agent:

    memory = MemoryService()

Poprawnie:

class Agent:

    def __init__(
        self,
        memory_service
    ):
        self.memory = memory_service

Korzyści:

testowanie,
wymiana implementacji,
mniejsze zależności.
Adapter Pattern

SSI używa adapterów do integracji.

Przykład:

AI MODEL

↓

ModelAdapter

↓

Ollama

↓

Local Model
Repository Interface

Dostęp do danych przez kontrakt:

Service

↓

Repository Interface

↓

Database Implementation

Przykład:

class AgentRepository:

    def save(agent):
        pass

    def find(id):
        pass
Event Interfaces

Komunikacja zdarzeniowa:

Module A

↓

Event Interface

↓

Event Bus

↓

Module B

Przykład:

AgentCreatedEvent()
API Internal Interface

Moduły mogą posiadać własne API:

Memory API

Task API

Knowledge API

Agent API
Wersjonowanie interfejsów

Każdy interfejs posiada wersję:

MemoryInterface

v1.0

↓

v1.1

↓

v2.0

Zasada:

Zmiana nie może niszczyć istniejących klientów.

Walidacja interfejsów

Każdy interfejs posiada:

Schema Validation

Contract Tests

Compatibility Tests
Testowanie interfejsów

Struktura:

Interface

↓

Implementation

↓

Integration Test

Przykład:

MemoryInterfaceTest

MemoryServiceTest

MemoryIntegrationTest
Interfejsy a Self Development Engine

Dla SSI jest to kluczowe.

AI może zmienić implementację:

OLD IMPLEMENTATION

↓

NEW IMPLEMENTATION

bez zmiany:

PUBLIC INTERFACE

Proces:

Analyze Interface

↓

Create New Implementation

↓

Run Contract Tests

↓

Replace Component

Zasady projektowania interfejsów

Każdy interfejs musi być:

1. Small

2. Clear

3. Stable

4. Versioned

5. Testable
Powiązanie z kolejnymi dokumentami
06_INTERFACE_IMPLEMENTATION_MODEL.md

↓

07_CODE_EXECUTION_FLOW.md

↓

08_RUNTIME_ARCHITECTURE.md

↓

09_SERVICE_LAYER_ARCHITECTURE.md
Cel końcowy

06_INTERFACE_IMPLEMENTATION_MODEL.md definiuje system połączeń pomiędzy modułami SSI.

Po zastosowaniu zasad:

moduły są luźno powiązane,
implementacje można wymieniać,
system można rozwijać bez przebudowy całości,
agenci AI mogą bezpiecznie modyfikować kod.

Jest to warstwa kontraktów SSI — mechanizm, który pozwala tysiącom komponentów współpracować jako jeden spójny system.