Opis:

Ten dokument definiuje standardy nazewnictwa plików, katalogów, modułów, klas, funkcji oraz elementów konfiguracyjnych w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest zapewnienie jednolitego sposobu tworzenia nazw w całym systemie, tak aby projekt pozostał czytelny, skalowalny i łatwy do rozwijania przez ludzi oraz agentów AI.

Dokument odpowiada na pytanie:

"Jak nazywamy elementy projektu, aby każdy od razu wiedział, czym są i gdzie należą?"

Cel dokumentu

04_FILE_NAMING_CONVENTION.md definiuje:

standard nazw katalogów,
standard nazw plików Python,
standard nazw klas,
standard nazw funkcji,
standard nazw zmiennych,
standard nazw konfiguracji,
standard nazw dokumentacji,
standard nazw testów,
standard nazw wersji.
Rola dokumentu

Dokument jest podstawą organizacji kodu.

Bez jednolitego nazewnictwa powstaje chaos:

Przykład złej organizacji:

Message.py

messageSystem.py

MSG_HANDLER.py

handle_msg_v2_final.py

Poprawnie:

message_system.py

message_handler.py

message_router.py
Główna zasada

Nazwa elementu musi informować:

czym jest,
do czego służy,
gdzie należy.

Schemat:

TYPE + PURPOSE

Przykład:

message_router.py

memory_manager.py

agent_registry.py
1. ZASADY NAZW KATALOGÓW
Standard:
UPPER_CASE_WITH_UNDERSCORE

Przykłady:

CORE/

MESSAGE_SYSTEM/

MEMORY_SYSTEM/

EVOLUTION_ENGINE/
Powód:

Główne moduły systemu są łatwe do rozpoznania.

Zabronione:

Nie używamy:

message-system

messageSystem

message system
2. ZASADY NAZW PLIKÓW PYTHON
Standard:
snake_case.py
Przykłady:

Poprawnie:

message_router.py

memory_manager.py

agent_controller.py

workflow_engine.py

Niepoprawnie:

MessageRouter.py

MemoryManager.py

routerFILE.py
3. NAZWY MODUŁÓW

Moduł powinien opisywać swoją funkcję.

Schemat:

<nazwa_funkcji>.py

Przykłady:

authentication.py

validation.py

scheduler.py

storage.py

Dla większych modułów:

message_core.py

memory_core.py

agent_core.py
4. NAZWY KLAS
Standard:
PascalCase

Przykłady:

class MessageRouter:
    pass


class MemoryManager:
    pass


class AgentRegistry:
    pass

Reguła:

Klasa = rzeczownik.

Poprawnie:

Message
Router
MemoryManager

Nie:

ProcessMessage
DoMemory
5. NAZWY FUNKCJI
Standard:
snake_case

Przykłady:

create_message()

send_request()

load_memory()

validate_agent()

Funkcja powinna oznaczać czynność.

Schemat:

czasownik + obiekt

Przykłady:

create_task

load_model

save_memory

analyze_message
6. NAZWY ZMIENNYCH
Standard:
snake_case

Przykłady:

message_id

agent_state

task_status

memory_data

Nie używać:

x

temp

data1

bez konkretnego znaczenia.

7. NAZWY STAŁYCH
Standard:
UPPER_CASE

Przykład:

MAX_MESSAGE_SIZE = 4096

DEFAULT_TIMEOUT = 30
8. NAZWY PLIKÓW KONFIGURACYJNYCH
Standard:
<nazwa>_config.format

Przykłady:

system_config.json

database_config.json

model_config.json

security_config.json
9. NAZWY DOKUMENTACJI
Standard SSI:
NN_NAME_DESCRIPTION.md

Przykłady:

00_PROJECT_STRUCTURE_INDEX.md

01_MESSAGE_ARCHITECTURE.md

02_DATABASE_MODEL.md

Zasada:

NUMER + OPIS
10. NAZWY TESTÓW
Standard:
test_<moduł>.py

Przykłady:

test_message_system.py

test_agent_manager.py

test_memory_storage.py

Dla konkretnej funkcji:

test_message_router.py
11. NAZWY LOGÓW
Standard:
<nazwa_systemu>_<typ>.log

Przykłady:

system_error.log

message_activity.log

evolution_history.log
12. NAZWY ID ELEMENTÓW SYSTEMU

Każdy obiekt posiada identyfikator.

Format:

TYPE_NUMBER

Przykłady:

Wiadomość:

MSG_000001

Agent:

AGENT_000001

Zadanie:

TASK_000001
13. NAZWY WERSJI

Standard:

MAJOR.MINOR.PATCH

Przykład:

1.0.0

1.2.5

2.0.0

Znaczenie:

MAJOR
duża zmiana architektury


MINOR
nowa funkcja


PATCH
poprawka
14. NAZWY BRANCHY GIT

Standard:

type/name

Przykłady:

feature/message-system

feature/new-agent

fix/database-error

docs/api-update
15. STRUKTURA NAZW MODUŁÓW SSI

Przykład:

MESSAGE_SYSTEM/

message_core.py

message_router.py

message_validator.py

Klasy:

MessageCore

MessageRouter

MessageValidator

Funkcje:

create_message()

route_message()

validate_message()
16. ZASADA BRAKU DUPLIKACJI

Nie tworzymy:

message_new.py

message_new2.py

message_final.py

message_final_v2.py

Zamiast tego:

message.py

version_control.py
17. ZASADA ROZSZERZANIA

Jeżeli moduł rośnie:

Źle:

MESSAGE_SYSTEM/

100 plików

Poprawnie:

MESSAGE_SYSTEM/

├── routing/
├── validation/
├── storage/
├── security/
18. STANDARD DLA AGENTÓW AI

Ponieważ SSI będzie rozwijany również przez agentów:

Każdy agent musi móc przewidzieć:

nazwa folderu

↓

nazwa pliku

↓

nazwa klasy

↓

nazwa funkcji

Przykład:

MEMORY_SYSTEM/

memory_manager.py

MemoryManager

load_memory()
Powiązanie z innymi dokumentami
01_PROJECT_FILE_STRUCTURE_BOOTSTRAP.md

↓

02_ROOT_DIRECTORY_MAP.md

↓

03_FOLDER_RESPONSIBILITY_MAP.md

↓

04_FILE_NAMING_CONVENTION.md

↓

05_MODULE_LOCATION_MAP.md

↓

06_MODULE_DEPENDENCY_MAP.md
Cel końcowy

04_FILE_NAMING_CONVENTION.md zapewnia, że cały projekt SSI_SELF_DEVELOPMENT_ENGINE posiada jeden spójny język nazewnictwa.

Po zastosowaniu zasad:

każdy plik jest przewidywalny,
każdy moduł jest czytelny,
agenci AI mogą łatwiej analizować kod,
projekt może rosnąć bez utraty organizacji.

Jest to standard języka projektu SSI — zbiór zasad, dzięki którym cała architektura pozostaje uporządkowana podczas wieloletniego rozwoju systemu.