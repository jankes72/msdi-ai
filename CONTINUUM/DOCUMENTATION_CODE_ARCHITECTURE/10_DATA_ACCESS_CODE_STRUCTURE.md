Opis:

Ten dokument definiuje strukturę kodu odpowiedzialną za dostęp do danych w systemie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest opisanie, w jaki sposób kod komunikuje się z bazami danych, magazynami plików, pamięcią systemową oraz innymi źródłami danych, zachowując separację pomiędzy logiką aplikacji a warstwą przechowywania informacji.

Dokument odpowiada na pytanie:

"Jak SSI zapisuje, odczytuje i zarządza danymi bez bezpośredniego powiązania logiki systemu z konkretną bazą danych?"

Cel dokumentu

10_DATA_ACCESS_CODE_STRUCTURE.md definiuje:

architekturę Data Access Layer,
strukturę repozytoriów,
modele danych,
adaptery baz danych,
dostęp do pamięci długoterminowej,
migracje danych,
cache,
synchronizację danych,
zasady bezpieczeństwa dostępu.
Rola dokumentu

Dokument opisuje warstwę znajdującą się pomiędzy:

SERVICE LAYER

↓

DATA ACCESS LAYER

↓

DATABASE / STORAGE
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

↓

08_RUNTIME_ARCHITECTURE.md

↓

09_SERVICE_LAYER_ARCHITECTURE.md

↓

10_DATA_ACCESS_CODE_STRUCTURE.md
Główna zasada Data Access Layer SSI

Żaden moduł biznesowy nie komunikuje się bezpośrednio z bazą danych.

Nie:

Agent

↓

Database

Poprawnie:

Agent

↓

AgentService

↓

AgentRepository

↓

Database Adapter

↓

Database
Definicja Data Access Layer

Data Access Layer to:

Warstwa odpowiedzialna za izolację systemu od sposobu przechowywania danych oraz zapewnienie jednolitego dostępu do informacji.

Architektura warstwy danych
DATA ACCESS LAYER

│
├── Models
│
├── Repositories
│
├── Data Mappers
│
├── Database Adapters
│
├── Query Builders
│
├── Cache Layer
│
├── Migration System
│
└── Backup System
Struktura katalogu

Standard:

database/

├── models/

│   ├── agent_model.py
│   ├── task_model.py
│   └── memory_model.py
│
├── repositories/

│   ├── agent_repository.py
│   ├── task_repository.py
│   └── memory_repository.py
│
├── adapters/

│   ├── sqlite_adapter.py
│   ├── postgres_adapter.py
│   └── file_adapter.py
│
├── migrations/

│
├── queries/

│
├── cache/

│
└── backup/
1. DATA MODELS
Odpowiedzialność:

Reprezentacja danych systemu.

Przykład:

class AgentModel:

    id: str

    name: str

    role: str

    status: str

Modele definiują:

pola,
typy danych,
relacje,
walidację podstawową.
2. REPOSITORY LAYER
Odpowiedzialność:

Abstrakcja operacji danych.

Repository ukrywa sposób zapisu.

Przykład:

class AgentRepository:

    def save(agent):
        pass

    def find(agent_id):
        pass

    def delete(agent_id):
        pass

Service nie wie:

czy dane są w SQL,
JSON,
Redis,
pliku.
3. DATABASE ADAPTERS
Odpowiedzialność:

Połączenie z konkretną technologią.

Przykład:

Repository

↓

Database Adapter

↓

SQLite

Obsługiwane mogą być:

SQLite,
PostgreSQL,
MongoDB,
pliki JSON,
pamięć lokalna.
4. DATA MAPPER
Odpowiedzialność:

Konwersja pomiędzy obiektami a danymi.

Schemat:

Object

↓

Mapper

↓

Database Record

Przykład:

AgentObject

↓

AgentMapper

↓

agent_table
5. QUERY BUILDER
Odpowiedzialność:

Tworzenie zapytań.

Przykład:

Search Agents

↓

Query Builder

↓

Database Query
6. CACHE LAYER
Odpowiedzialność:

Przyspieszanie dostępu.

Schemat:

Request

↓

Cache

↓

Database

Przechowuje:

często używane dane,
modele,
konfigurację,
aktywny stan.
7. MIGRATION SYSTEM
Odpowiedzialność:

Zmiany struktury danych.

Przykład:

Database v1

↓

Migration

↓

Database v2

Obsługuje:

dodawanie pól,
zmiany tabel,
aktualizacje schematu.
8. BACKUP SYSTEM
Odpowiedzialność:

Ochrona danych.

Schemat:

Database

↓

Backup Service

↓

Backup Storage

Backup obejmuje:

pamięć AI,
wiedzę,
konfigurację,
historię działania.
Typy danych SSI

System przechowuje:

1. SYSTEM DATA

2. AGENT DATA

3. TASK DATA

4. MEMORY DATA

5. KNOWLEDGE DATA

6. MESSAGE DATA

7. CONFIGURATION DATA

8. HISTORY DATA
Przepływ zapisu danych

Przykład:

Agent zapisuje doświadczenie.

Agent

↓

MemoryService

↓

MemoryRepository

↓

Data Mapper

↓

Database Adapter

↓

Storage
Przepływ odczytu danych
Request

↓

Service

↓

Repository

↓

Adapter

↓

Database

↓

Mapper

↓

Object
Data Access i Dependency Injection

Przykład:

class MemoryService:

    def __init__(
        self,
        repository
    ):
        self.repository = repository

Dzięki temu można zmienić:

SQLite

↓

PostgreSQL

bez zmiany:

MemoryService
Data Validation

Każdy zapis przechodzi:

Input

↓

Schema Validation

↓

Business Validation

↓

Save
Transaction Management

Operacje krytyczne:

BEGIN

↓

PROCESS

↓

COMMIT

↓

ROLLBACK
Error Handling danych

Obsługiwane błędy:

ConnectionError

ValidationError

StorageError

MigrationError
Data Access Logging

Rejestrowane:

Query

Time

Source

Result

Error
Data Security

Warstwa danych kontroluje:

szyfrowanie,
uprawnienia,
dostęp modułów,
audyt.
Data Access a Self Development Engine

Jednolita warstwa danych pozwala AI:

analizować strukturę danych,
optymalizować zapytania,
wykrywać nieużywane dane,
projektować migracje.

Proces:

Data Analysis

↓

Optimization Proposal

↓

Migration Plan

↓

Testing

↓

Deployment
Zasady projektowania Data Layer

Warstwa danych musi być:

1. Abstract

2. Secure

3. Consistent

4. Versioned

5. Recoverable
Powiązanie z kolejnymi dokumentami
10_DATA_ACCESS_CODE_STRUCTURE.md

↓

11_CONFIGURATION_CODE_ARCHITECTURE.md

↓

12_EXCEPTION_HANDLING_ARCHITECTURE.md

↓

13_LOGGING_AND_MONITORING_CODE.md
Cel końcowy

10_DATA_ACCESS_CODE_STRUCTURE.md definiuje fundament przechowywania i dostępu do danych SSI_SELF_DEVELOPMENT_ENGINE.

Po zastosowaniu zasad:

logika systemu jest odizolowana od bazy danych,
dane mają kontrolowany przepływ,
można wymieniać technologie przechowywania,
AI może bezpiecznie analizować i rozwijać strukturę danych.

Jest to warstwa pamięci technicznej SSI — mechanizm, który pozwala systemowi zapisywać, odzyskiwać i rozwijać swoją wiedzę oraz stan działania.