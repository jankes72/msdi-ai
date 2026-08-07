Opis:

Ten dokument definiuje docelową strukturę katalogów i plików projektu SSI_SELF_DEVELOPMENT_ENGINE.

Jego celem jest określenie, gdzie znajdują się poszczególne elementy systemu, jak organizowane są moduły, gdzie przechowywany jest kod, dokumentacja, pamięć, konfiguracja oraz dane operacyjne.

Dokument zapewnia, że AI podczas budowy systemu tworzy elementy w odpowiednich miejscach i zachowuje spójną organizację projektu od pierwszego etapu implementacji.

Cel dokumentu

06_DIRECTORY_STRUCTURE_PLAN.md odpowiada na pytania:

Jak wygląda struktura katalogów projektu?
Gdzie znajduje się kod źródłowy?
Gdzie przechowywana jest pamięć AI?
Gdzie znajdują się dokumenty?
Gdzie zapisuje się historię operacji?
Jak AI ma odnaleźć potrzebne pliki?
Główna zasada organizacji

Projekt nie jest pojedynczym katalogiem z losowymi plikami.

Każdy element posiada określone miejsce.

Schemat:

PROJECT ROOT

↓

SYSTEM MODULES

↓

DATA

↓

MEMORY

↓

DOCUMENTATION

↓

LOGS

↓

TESTS
Główna struktura projektu

Przykładowa struktura:

SSI_SELF_DEVELOPMENT_ENGINE
│
├── CONFIG
│
├── CORE
│
├── DIRECTOR
│
├── AGENTS
│
├── TASK_SYSTEM
│
├── EXECUTION_ENGINE
│
├── MEMORY
│
├── KNOWLEDGE
│
├── DOCUMENTATION
│
├── TESTS
│
├── LOGS
│
├── DATA
│
└── RUNTIME
1. CONFIG
Konfiguracja systemu

Przechowuje:

ustawienia projektu,
konfigurację modeli AI,
parametry działania,
środowisko pracy.

Przykład:

CONFIG

├── system_config.json
├── model_config.json
└── runtime_config.json
2. CORE
Fundament systemu

Zawiera podstawowe mechanizmy:

inicjalizację,
komunikację bazową,
wspólne klasy,
obsługę systemu.

Przykład:

CORE

├── system.py
├── interfaces.py
└── base_classes.py
3. DIRECTOR
Dyrektor działu programistycznego

Odpowiada za:

decyzje,
planowanie,
zarządzanie pracą.

Struktura:

DIRECTOR

├── director_core.py
├── director_memory.json
└── director_state.json
4. AGENTS
Agenci AI

Każdy agent posiada własny katalog.

Przykład:

AGENTS

├── PROGRAMMER_AGENT
│
├── VALIDATION_AGENT
│
├── DOCUMENTATION_AGENT
│
├── ARCHITECTURE_AGENT
│
└── TESTING_AGENT

Każdy agent posiada:

agent.py

memory/

config/

logs/
5. TASK_SYSTEM
Zarządzanie zadaniami

Zawiera:

tworzenie zadań,
kolejkę,
statusy,
historię.

Struktura:

TASK_SYSTEM

├── task_manager.py
├── queue_manager.py
├── tasks/
└── history/
6. EXECUTION_ENGINE
Wykonywanie operacji

Odpowiada za:

wykonywanie poleceń,
operacje na plikach,
uruchamianie procesów.

Struktura:

EXECUTION_ENGINE

├── execution_engine.py
├── operation_manager.py
└── executor_logs/
7. MEMORY
System pamięci AI

Każdy element pamięci posiada własną strukturę.

MEMORY

├── SHORT_TERM
│
├── LONG_TERM
│
├── OPERATIONS
│
└── HISTORY

Przechowuje:

bieżący kontekst,
doświadczenia,
decyzje,
historię.
8. KNOWLEDGE
Baza wiedzy

Struktura:

KNOWLEDGE

├── PROJECT_KNOWLEDGE
├── PATTERNS
├── SOLUTIONS
└── VALIDATED_KNOWLEDGE
9. DOCUMENTATION
Dokumentacja projektu

Zawiera:

DOCUMENTATION

├── AI_DOCUMENTATION_SYSTEM

├── PROJECT_BUILD_PLAN

├── SYSTEM_SPECIFICATIONS

└── REPORTS
10. TESTS
Testowanie

Przechowuje:

testy jednostkowe,
testy integracyjne,
raporty wyników.

Struktura:

TESTS

├── UNIT_TESTS

├── INTEGRATION_TESTS

└── TEST_RESULTS
11. LOGS
Historia działania

Zawiera:

logi agentów,
błędy,
operacje,
komunikację.

Struktura:

LOGS

├── SYSTEM_LOGS

├── AGENT_LOGS

├── ERROR_LOGS

└── AUDIT_LOGS
12. RUNTIME
Dane działania systemu

Przechowuje:

aktualny stan,
aktywne procesy,
sesje.

Przykład:

RUNTIME

├── current_state.json
├── active_tasks.json
└── sessions/
Zasady tworzenia plików

Każdy nowy plik musi posiadać:

określone miejsce,
właściciela modułu,
opis odpowiedzialności,
powiązanie z dokumentacją.
Zasada separacji danych

Kod i dane nie powinny być mieszane.

Nie:

module.py
memory.json
logs.txt

w jednym katalogu.

Poprawnie:

CODE

MEMORY

LOGS

DATA
Przygotowanie pod przyszły serwer

Struktura jest projektowana tak, aby później można było przenieść system na serwer.

Obecnie:

LOCAL COMPUTER

↓

FILES

Docelowo:

SERVER

↓

SERVICES

↓

DATABASES

↓

AI MODELS
Integracja z innymi dokumentami

06_DIRECTORY_STRUCTURE_PLAN.md współpracuje z:

04_MODULE_IMPLEMENTATION_PLAN

↓

05_COMPONENT_DEPENDENCY_MAP

↓

07_CODE_IMPLEMENTATION_RULES

↓

13_DEPLOYMENT_AND_RUNTIME_PLAN
Cel końcowy

06_DIRECTORY_STRUCTURE_PLAN.md zapewnia jednolitą organizację całego SSI_SELF_DEVELOPMENT_ENGINE.

Dzięki temu AI:

zawsze wie, gdzie tworzyć pliki,
nie miesza modułów,
zachowuje porządek projektu,
łatwo odnajduje informacje,
może rozwijać system lokalnie, a później przenieść go na serwer.

Dokument stanowi podstawowy schemat organizacyjny całej infrastruktury projektu.