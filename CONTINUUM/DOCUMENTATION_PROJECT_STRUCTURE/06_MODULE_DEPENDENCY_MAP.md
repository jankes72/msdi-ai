Opis:

Ten dokument definiuje mapę zależności pomiędzy wszystkimi modułami systemu SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie:

które moduły mogą komunikować się ze sobą,
które moduły mogą korzystać z innych modułów,
jaki jest kierunek zależności,
gdzie znajdują się granice architektury,
których połączeń należy unikać.

Dokument odpowiada na pytanie:

"Kto od kogo zależy i jak przepływa komunikacja w całym systemie?"

Cel dokumentu

06_MODULE_DEPENDENCY_MAP.md definiuje:

hierarchię zależności modułów,
kierunek komunikacji,
poziomy architektury,
zależności wymagane,
zależności zabronione,
zasady rozbudowy systemu.
Rola dokumentu

Dokument chroni architekturę SSI przed chaosem zależności.

Bez kontroli moduły zaczynają tworzyć przypadkowe połączenia:

Źle:

AGENT_SYSTEM
      |
      ↓
DATABASE
      |
      ↓
MESSAGE_SYSTEM
      |
      ↓
CORE

Powstaje sprzężenie wszystkiego ze wszystkim.

Poprawnie:

CORE

 ↓

API / MESSAGE_SYSTEM

 ↓

MODULES

 ↓

DATABASE
Główna zasada architektury

SSI wykorzystuje zasadę:

HIGH LEVEL MODULES
        |
        ↓
INTERFACE LAYER
        |
        ↓
LOW LEVEL SERVICES

Czyli:

Moduł nie powinien bezpośrednio ingerować w wnętrze innego modułu.

Warstwy systemu

Architektura zależności:

                    CORE
                      |
                      |
              ----------------
              |              |
             API       MESSAGE_SYSTEM
              |
   ------------------------------------
   |          |          |            |
AGENTS     TASKS     MEMORY     KNOWLEDGE
   |          |          |            |
   ------------------------------------
                    |
               DATABASE
                    |
               STORAGE
POZIOM 1 — CORE LAYER
Lokalizacja:
CORE/
Odpowiedzialność:

Najwyższy poziom sterowania.

CORE może znać:

CORE

↓

MESSAGE_SYSTEM

↓

API

↓

DATABASE

↓

SECURITY
CORE zarządza:
startem systemu,
inicjalizacją,
stanem,
cyklem życia.
CORE nie zawiera:

❌ logiki agentów
❌ logiki pamięci
❌ logiki wiedzy

POZIOM 2 — COMMUNICATION LAYER

Obejmuje:

MESSAGE_SYSTEM/

API/
MESSAGE_SYSTEM
Zależności:

Może korzystać z:

MESSAGE_SYSTEM

↓

SECURITY

↓

DATABASE
Nie może:

❌ sterować agentami
❌ wykonywać zadań
❌ podejmować decyzji

API
Zależności:
API

↓

MESSAGE_SYSTEM

↓

MODULE INTERFACES

API jest bramą komunikacyjną.

POZIOM 3 — INTELLIGENCE MODULES

Obejmuje:

AGENT_SYSTEM

TASK_SYSTEM

MEMORY_SYSTEM

KNOWLEDGE_SYSTEM
AGENT_SYSTEM
Może korzystać z:
AGENT_SYSTEM

↓

MESSAGE_SYSTEM

↓

MEMORY_SYSTEM

↓

KNOWLEDGE_SYSTEM

↓

TASK_SYSTEM
Nie może:

❌ bezpośrednio zapisywać do DATABASE

Poprawnie:

AGENT

↓

MEMORY_API

↓

DATABASE
TASK_SYSTEM
Może korzystać z:
TASK_SYSTEM

↓

AGENT_SYSTEM

↓

MESSAGE_SYSTEM

↓

WORKFLOW_ENGINE
Odpowiada za:
planowanie,
wykonanie,
kontrolę zadań.
MEMORY_SYSTEM
Może korzystać z:
MEMORY_SYSTEM

↓

DATABASE

↓

KNOWLEDGE_SYSTEM
Nie steruje:

❌ agentami
❌ workflow

KNOWLEDGE_SYSTEM
Może korzystać z:
KNOWLEDGE_SYSTEM

↓

DATABASE

↓

MEMORY_SYSTEM
Odpowiada za:
analizę,
relacje,
wiedzę.
POZIOM 4 — DATA LAYER

Obejmuje:

DATABASE/
DATA/
DATABASE
Zależności:

DATABASE nie zależy od:

❌ AGENT_SYSTEM
❌ TASK_SYSTEM
❌ MEMORY_SYSTEM

DATABASE jest usługą.

POZIOM 5 — CONTROL SYSTEMS

Obejmuje:

WORKFLOW_ENGINE/

MODEL_SYSTEM/

EVOLUTION_ENGINE/

SECURITY/
WORKFLOW_ENGINE

Może korzystać z:

WORKFLOW_ENGINE

↓

TASK_SYSTEM

↓

AGENT_SYSTEM

↓

MESSAGE_SYSTEM
MODEL_SYSTEM

Może korzystać z:

MODEL_SYSTEM

↓

AGENT_SYSTEM

↓

DATABASE

Odpowiada za:

modele,
wybór modelu,
zarządzanie AI.
SECURITY
Zależność:

Security jest usługą globalną.

Może być używane przez:

SECURITY

↓

CAŁY SYSTEM
EVOLUTION_ENGINE

Najwyższy moduł rozwojowy.

Może analizować:

EVOLUTION_ENGINE

↓

CORE

↓

MODULES

↓

LOGS

↓

TESTS
Pełna mapa zależności
                         CORE
                           |
                           |
                         API
                           |
                 MESSAGE_SYSTEM
                           |
        ---------------------------------
        |              |                |
   AGENT_SYSTEM   TASK_SYSTEM    WORKFLOW_ENGINE
        |
        |
 ----------------------------
 |                          |
MEMORY_SYSTEM        KNOWLEDGE_SYSTEM
        |
        |
    DATABASE
        |
      STORAGE


MODEL_SYSTEM
        |
        |
    AGENT_SYSTEM


EVOLUTION_ENGINE
        |
        |
   ALL MODULES


SECURITY
        |
        |
   ALL MODULES
Zależności zabronione
1. Moduły biznesowe → DATABASE

Nie:

AGENT_SYSTEM
        |
        ↓
DATABASE

Tak:

AGENT_SYSTEM

↓

API

↓

DATABASE
2. MESSAGE_SYSTEM → AGENT LOGIC

Nie:

MESSAGE_SYSTEM

↓

Agent decision

Message tylko przekazuje.

3. DATABASE → SYSTEM LOGIC

Nie:

DATABASE

↓

Task execution
Reguła nowych modułów

Każdy nowy moduł musi określić:

1. Kto może go wywołać

2. Z czego korzysta

3. Z czego nie korzysta

4. Jak komunikuje się z resztą systemu
Przykład dodania nowego modułu

Nowy:

RESEARCH_ENGINE/

Przed dodaniem:

Analiza:

RESEARCH_ENGINE

↓

MESSAGE_SYSTEM

↓

KNOWLEDGE_SYSTEM

↓

MEMORY_SYSTEM

Dokumentacja:

odpowiedzialność,
lokalizacja,
zależności,
API.
Powiązanie dokumentów
00_PROJECT_STRUCTURE_INDEX

↓

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

06_MODULE_DEPENDENCY_MAP.md zapewnia, że SSI_SELF_DEVELOPMENT_ENGINE rozwija się jako modularny system, a nie zbiór przypadkowo połączonych plików.

Po zastosowaniu zasad:

każdy moduł ma jasno określone zależności,
komunikacja jest kontrolowana,
zmiany nie niszczą całego systemu,
architektura pozostaje skalowalna.

Jest to mapa przepływu zależności SSI — dokument określający, jak wszystkie części systemu współpracują bez tworzenia chaosu architektonicznego.