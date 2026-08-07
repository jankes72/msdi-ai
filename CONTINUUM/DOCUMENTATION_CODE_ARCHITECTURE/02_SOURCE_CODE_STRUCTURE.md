Opis:

Ten dokument definiuje fizyczną strukturę kodu źródłowego systemu SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie:

gdzie znajduje się kod aplikacji,
jak rozmieszczone są katalogi źródłowe,
jak organizowane są pliki Python,
gdzie znajdują się moduły, usługi, modele, interfejsy i testy,
jak wygląda standardowa struktura każdego komponentu.

Dokument odpowiada na pytanie:

"Jak dokładnie wygląda układ plików i katalogów, w których znajduje się kod SSI?"

Cel dokumentu

02_SOURCE_CODE_STRUCTURE.md definiuje:

główny katalog kodu,
strukturę folderów src,
rozmieszczenie modułów,
standard organizacji plików,
zasady tworzenia nowych komponentów.
Rola dokumentu

Dokument jest przejściem pomiędzy:

ARCHITEKTURA LOGICZNA

↓

FIZYCZNA STRUKTURA KODU

↓

IMPLEMENTACJA
Miejsce w dokumentacji
00_CODE_ARCHITECTURE_INDEX.md

↓

01_CODE_ARCHITECTURE_OVERVIEW.md

↓

02_SOURCE_CODE_STRUCTURE.md

↓

03_MODULE_INTERNAL_ARCHITECTURE.md
Główna zasada struktury kodu

SSI nie jest organizowane według pojedynczych plików.

Jest organizowane według:

SYSTEM

↓

MODULE

↓

COMPONENT

↓

FILE

↓

CLASS

↓

FUNCTION
Główna struktura projektu kodu

Docelowa struktura:

SSI_SELF_DEVELOPMENT_ENGINE/

│
├── src/
│
├── tests/
│
├── config/
│
├── data/
│
├── logs/
│
├── scripts/
│
├── tools/
│
└── documentation/
1. KATALOG src/
Odpowiedzialność:

Główny katalog kodu źródłowego.

Zawiera całą implementację SSI.

Struktura:

src/

├── core/
├── api/
├── message_system/
├── agents/
├── tasks/
├── memory/
├── knowledge/
├── database/
├── models/
├── workflow/
├── security/
├── evolution/
└── utils/
2. src/core/
Odpowiedzialność:

Jądro systemu.

Struktura:

core/

├── system_core.py
├── runtime.py
├── lifecycle.py
├── state_manager.py
├── event_manager.py
└── exceptions.py

Zawiera:

start systemu,
inicjalizację,
zarządzanie stanem,
podstawowe mechanizmy.
3. src/api/
Odpowiedzialność:

Warstwa komunikacji zewnętrznej i wewnętrznej.

Struktura:

api/

├── api_core.py
├── router.py
├── request.py
├── response.py
│
└── interfaces/
    ├── agent_api.py
    ├── memory_api.py
    ├── task_api.py
    └── knowledge_api.py
4. src/message_system/
Odpowiedzialność:

System komunikatów.

Struktura:

message_system/

├── core/
│   └── message_core.py
│
├── routing/
│   └── message_router.py
│
├── queue/
│   └── message_queue.py
│
├── validation/
│   └── message_validator.py
│
├── models/
│   └── message_model.py
│
└── exceptions/
5. src/agents/
Odpowiedzialność:

System agentów AI.

Struktura:

agents/

├── core/
│   └── agent_core.py
│
├── manager/
│   └── agent_manager.py
│
├── registry/
│   └── agent_registry.py
│
├── implementations/
│
│   ├── director_agent.py
│   ├── programmer_agent.py
│   ├── validator_agent.py
│
└── models/
6. src/tasks/
Odpowiedzialność:

System zarządzania zadaniami.

Struktura:

tasks/

├── task_manager.py
├── task_queue.py
├── task_scheduler.py
├── task_executor.py
└── task_model.py
7. src/memory/
Odpowiedzialność:

Pamięć SSI.

Struktura:

memory/

├── core/
│
├── short_term/
│
├── long_term/
│
├── episodic/
│
├── semantic/
│
├── retrieval/
│
├── consolidation/
└── models/
8. src/knowledge/
Odpowiedzialność:

System wiedzy.

Struktura:

knowledge/

├── knowledge_core.py
├── knowledge_graph.py
├── inference_engine.py
├── rule_engine.py
└── models/
9. src/database/
Odpowiedzialność:

Warstwa dostępu do danych.

Struktura:

database/

├── connection.py
├── database_manager.py
├── repositories/
├── migrations/
└── models/
10. src/models/
Odpowiedzialność:

Obsługa modeli AI.

Struktura:

models/

├── model_manager.py
├── model_loader.py
├── model_router.py
├── model_registry.py
└── providers/
11. src/workflow/
Odpowiedzialność:

Orkiestracja procesów.

Struktura:

workflow/

├── workflow_engine.py
├── workflow_manager.py
├── workflow_state.py
└── execution_engine.py
12. src/security/
Odpowiedzialność:

Bezpieczeństwo.

Struktura:

security/

├── authentication.py
├── authorization.py
├── encryption.py
├── permissions.py
└── audit.py
13. src/evolution/
Odpowiedzialność:

Samorozwój systemu.

Struktura:

evolution/

├── analyzer.py
├── improvement_engine.py
├── proposal_generator.py
├── migration_manager.py
└── rollback_manager.py
14. src/utils/
Odpowiedzialność:

Wspólne narzędzia.

Przykłady:

utils/

├── helpers.py
├── validators.py
├── converters.py
└── constants.py
Struktura testów
tests/

├── unit/

├── integration/

├── system/

├── performance/

└── regression/
Struktura konfiguracji
config/

├── system_config.yaml
├── database_config.yaml
├── model_config.yaml
├── security_config.yaml
└── logging_config.yaml
Struktura danych
data/

├── raw/

├── processed/

├── memory/

├── knowledge/

└── backups/
Struktura logów
logs/

├── system/

├── agents/

├── messages/

├── errors/

└── evolution/
Zasady organizacji kodu
1. Jeden moduł = jedna odpowiedzialność

Przykład:

Dobrze:

memory_manager.py

Źle:

everything_manager.py
2. Brak kodu poza src

Kod aplikacji znajduje się tylko:

src/
3. Każdy moduł posiada:
module/

├── code
├── models
├── interfaces
├── exceptions
└── tests
4. Dokumentacja podąża za kodem

Zmiana struktury kodu wymaga aktualizacji:

MODULE_LOCATION_MAP
MODULE_DEPENDENCY_MAP
SOURCE_CODE_STRUCTURE
Przygotowanie pod AI Self Development

Struktura musi umożliwiać agentom:

znalezienie kodu,
analizę modułu,
ocenę zależności,
zaproponowanie zmian.

Schemat:

AI Agent

↓

Code Map

↓

Module Analysis

↓

Change Proposal

↓

Validation
Powiązanie z kolejnymi dokumentami
02_SOURCE_CODE_STRUCTURE.md

↓

03_MODULE_INTERNAL_ARCHITECTURE.md

↓

04_CLASS_AND_OBJECT_MODEL.md

↓

05_FUNCTION_AND_METHOD_STRUCTURE.md
Cel końcowy

02_SOURCE_CODE_STRUCTURE.md definiuje fizyczną mapę kodu SSI_SELF_DEVELOPMENT_ENGINE.

Po wdrożeniu zasad:

każdy plik ma swoje miejsce,
każdy moduł ma określoną strukturę,
kod jest skalowalny,
agenci AI mogą analizować projekt,
rozwój systemu pozostaje kontrolowany.

Jest to plan katalogów i plików źródłowych SSI — fundament, na którym będzie powstawała właściwa implementacja systemu.