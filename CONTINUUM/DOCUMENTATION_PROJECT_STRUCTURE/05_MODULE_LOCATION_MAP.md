Opis:

Ten dokument definiuje dokładną lokalizację wszystkich modułów systemu SSI_SELF_DEVELOPMENT_ENGINE w strukturze projektu.

Jego zadaniem jest stworzenie mapy:

"Jaki moduł znajduje się gdzie fizycznie i jakie pliki odpowiadają za jego działanie?"

Dokument jest rozwinięciem:

03_FOLDER_RESPONSIBILITY_MAP.md

oraz:

04_FILE_NAMING_CONVENTION.md

Poprzednie dokumenty określały:

co istnieje,
za co odpowiada,
jak nazywać elementy.

Ten dokument określa:

gdzie dokładnie znajduje się każdy element.
Cel dokumentu

05_MODULE_LOCATION_MAP.md definiuje:

lokalizację głównych modułów,
lokalizację podmodułów,
lokalizację plików odpowiedzialnych za funkcje,
mapowanie architektury logicznej na strukturę fizyczną,
standard umieszczania nowych komponentów.
Rola dokumentu

Dokument jest mapą adresową SSI.

Odpowiada na pytanie:

"Jeżeli chcę zmienić daną funkcję systemu, gdzie mam szukać kodu?"

Zasada główna

Każdy element architektury posiada:

MODUŁ

↓

LOKALIZACJA

↓

PLIK

↓

ODPOWIEDZIALNOŚĆ

Przykład:

Message Routing

↓

MESSAGE_SYSTEM/routing/

↓

message_router.py

↓

Obsługa kierowania wiadomości
Główna mapa modułów
SSI_SELF_DEVELOPMENT_ENGINE/

│
├── CORE/
│
├── MESSAGE_SYSTEM/
│
├── AGENT_SYSTEM/
│
├── TASK_SYSTEM/
│
├── MEMORY_SYSTEM/
│
├── KNOWLEDGE_SYSTEM/
│
├── DATABASE/
│
├── API/
│
├── WORKFLOW_ENGINE/
│
├── MODEL_SYSTEM/
│
├── SECURITY/
│
└── EVOLUTION_ENGINE/
1. CORE MODULE
Lokalizacja:
CORE/
Główne pliki:
CORE/

├── system_core.py
├── runtime.py
├── lifecycle.py
├── state_manager.py
├── event_manager.py
└── health_monitor.py
Odpowiedzialność:
Plik	Funkcja
system_core.py	główne jądro systemu
runtime.py	środowisko wykonawcze
lifecycle.py	start/stop systemu
state_manager.py	zarządzanie stanem
event_manager.py	obsługa zdarzeń
2. MESSAGE SYSTEM MODULE
Lokalizacja:
MESSAGE_SYSTEM/
Struktura:
MESSAGE_SYSTEM/

├── message_core.py
├── message_object.py
├── message_factory.py
│
├── headers/
├── payload/
├── types/
├── routing/
├── queue/
├── validation/
├── security/
├── storage/
├── analysis/
└── evolution/
Najważniejsze lokalizacje:
Tworzenie wiadomości:
MESSAGE_SYSTEM/

message_factory.py
Routing:
MESSAGE_SYSTEM/

routing/

message_router.py
Walidacja:
MESSAGE_SYSTEM/

validation/

message_validator.py
Historia:
MESSAGE_SYSTEM/

storage/

history_storage.py
3. AGENT SYSTEM MODULE
Lokalizacja:
AGENT_SYSTEM/
Struktura:
AGENT_SYSTEM/

├── agent_core.py
├── agent_manager.py
├── agent_registry.py
├── agent_state.py
├── agent_memory.py
│
└── agents/

    ├── director_agent.py
    ├── planner_agent.py
    ├── programmer_agent.py
    ├── analyst_agent.py
    └── validator_agent.py
Odpowiedzialność:
Element	Lokalizacja
zarządzanie agentami	agent_manager.py
rejestr	agent_registry.py
konkretni agenci	agents/
4. TASK SYSTEM MODULE
Lokalizacja:
TASK_SYSTEM/
Pliki:
task_core.py

task_manager.py

task_queue.py

task_scheduler.py

task_executor.py
5. MEMORY SYSTEM MODULE
Lokalizacja:
MEMORY_SYSTEM/
Struktura:
MEMORY_SYSTEM/

├── memory_core.py
├── memory_manager.py
│
├── short_term/
├── long_term/
├── episodic/
├── semantic/
├── consolidation/
└── retrieval/
Mapowanie:
Funkcja	Lokalizacja
zarządzanie pamięcią	memory_manager.py
pamięć krótka	short_term/
pamięć długa	long_term/
wyszukiwanie	retrieval/
6. KNOWLEDGE SYSTEM MODULE
Lokalizacja:
KNOWLEDGE_SYSTEM/
Pliki:
knowledge_core.py

knowledge_manager.py

knowledge_graph.py

rule_engine.py

inference_engine.py
7. DATABASE MODULE
Lokalizacja:
DATABASE/
Struktura:
DATABASE/

├── database_manager.py
├── connection.py
│
├── models/
│
├── migrations/
│
└── backups/
Modele:
DATABASE/models/

message_model.py

agent_model.py

task_model.py

memory_model.py

knowledge_model.py
8. API MODULE
Lokalizacja:
API/
Struktura:
API/

├── api_core.py
├── api_router.py
├── request_model.py
├── response_model.py
├── error_handler.py
│
└── interfaces/

    ├── agent_api.py
    ├── message_api.py
    ├── memory_api.py
    ├── knowledge_api.py
    └── database_api.py
9. WORKFLOW ENGINE
Lokalizacja:
WORKFLOW_ENGINE/
Pliki:
workflow_core.py

workflow_manager.py

workflow_state.py

execution_engine.py
10. MODEL SYSTEM
Lokalizacja:
MODEL_SYSTEM/
Pliki:
model_manager.py

model_loader.py

model_router.py

model_registry.py

model_memory.py
11. SECURITY MODULE
Lokalizacja:
SECURITY/
Pliki:
authentication.py

authorization.py

encryption.py

permissions.py

audit_system.py
12. EVOLUTION ENGINE
Lokalizacja:
EVOLUTION_ENGINE/
Pliki:
evolution_core.py

evolution_manager.py

analyzer.py

proposal_generator.py

simulator.py

tester.py

migration.py

rollback.py
Mapa wyszukiwania funkcji

Przykłady:

"Chcę zmienić komunikaty"

Szukam:

MESSAGE_SYSTEM/
"Chcę zmienić pamięć"

Szukam:

MEMORY_SYSTEM/
"Chcę dodać nowego agenta"

Szukam:

AGENT_SYSTEM/agents/
"Chcę zmienić model AI"

Szukam:

MODEL_SYSTEM/
"Chcę zmienić sposób działania procesu"

Szukam:

WORKFLOW_ENGINE/
Reguła dodawania nowych modułów

Nowy moduł musi posiadać:

1. Lokalizację

2. Odpowiedzialność

3. Dokumentację

4. Interfejs

5. Testy
Powiązanie dokumentów
01_PROJECT_FILE_STRUCTURE_BOOTSTRAP

↓

02_ROOT_DIRECTORY_MAP

↓

03_FOLDER_RESPONSIBILITY_MAP

↓

04_FILE_NAMING_CONVENTION

↓

05_MODULE_LOCATION_MAP

↓

06_MODULE_DEPENDENCY_MAP

↓

07_BUILD_ORDER_PLAN
Cel końcowy

05_MODULE_LOCATION_MAP.md tworzy dokładną mapę fizycznego rozmieszczenia systemu SSI.

Po przeczytaniu dokumentu wiadomo:

gdzie znajduje się każdy moduł,
gdzie szukać konkretnej funkcji,
gdzie dodawać nowe elementy,
jak zachować porządek podczas rozwoju.

Jest to adresownik całego kodu SSI_SELF_DEVELOPMENT_ENGINE — mapa przejścia od architektury do konkretnego pliku implementacji.