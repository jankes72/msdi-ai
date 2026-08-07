Opis:

Ten dokument definiuje system typów komunikatów (Message Type System) w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie jakie rodzaje wiadomości mogą istnieć w systemie, jakie mają znaczenie, kiedy są używane, kto może je tworzyć, kto może je odbierać oraz jak system interpretuje ich przeznaczenie.

Jeżeli:

03_MESSAGE_OBJECT_MODEL.md definiuje strukturę pojedynczego komunikatu,
04_MESSAGE_FORMAT_SPECIFICATION.md definiuje techniczny zapis wiadomości,
05_MESSAGE_TYPE_SYSTEM.md definiuje znaczenie i klasyfikację komunikatów,

to:

05_MESSAGE_TYPE_SYSTEM.md jest słownikiem języka komunikacji SSI — określa, jakie "zdania" system AI może między sobą wymieniać.

Cel dokumentu

Dokument odpowiada na pytania:

Jakie typy komunikatów istnieją?
Kiedy używać COMMAND, REQUEST, EVENT lub RESPONSE?
Jak agent rozpoznaje intencję wiadomości?
Jak system rozdziela różne rodzaje komunikacji?
Jak dodawać nowe typy wiadomości?
Jak kontrolować kompatybilność komunikatów?
Rola dokumentu

Dokument jest podstawą dla:

Message Router,
Message Handler,
Agent Communication System,
Event System,
Task Management System,
Validation System.
Główna zasada

Każdy komunikat musi posiadać określony typ.

Nie:

MESSAGE

"zrób coś"

Tylko:

MESSAGE

TYPE:

COMMAND

INTENT:

CREATE_MODULE

Typ mówi systemowi:

co to jest,
jak to obsłużyć,
kto powinien reagować.
Hierarchia typów komunikatów
MESSAGE

│
├── COMMAND
│
├── REQUEST
│
├── RESPONSE
│
├── EVENT
│
├── NOTIFICATION
│
├── ERROR
│
└── SYSTEM MESSAGE
1. COMMAND MESSAGE
Komunikat polecenia

Cel:

Nakazuje wykonanie określonej operacji.

Model:

COMMAND

↓

ACTION

↓

EXECUTION

Przykłady:

CREATE_FILE

BUILD_MODULE

RUN_TEST

UPDATE_CONFIG

START_AGENT

Przykład:

{
"type":"COMMAND",
"action":"CREATE_MODULE",
"target":"PROGRAMMER_AGENT"
}
Zastosowanie

Używane przez:

Director Core,
Orchestrator,
Task Manager.
2. REQUEST MESSAGE
Komunikat zapytania

Cel:

Prośba o informacje lub wykonanie operacji wymagającej odpowiedzi.

Model:

REQUEST

↓

PROCESS

↓

RESPONSE

Przykłady:

GET_MEMORY

SEARCH_KNOWLEDGE

GET_AGENT_STATUS

LOAD_PROJECT_STATE

Przykład:

{
"type":"REQUEST",
"action":"GET_MEMORY",
"target":"MEMORY_MANAGER"
}
3. RESPONSE MESSAGE
Odpowiedź na żądanie

Cel:

Przekazanie wyniku wykonania REQUEST.

Model:

REQUEST

↓

RESPONSE

Przykłady:

SUCCESS

DATA_RETURNED

TASK_RESULT

VALIDATION_RESULT

Przykład:

{
"type":"RESPONSE",
"status":"SUCCESS",
"data":{}
}
4. EVENT MESSAGE
Komunikat zdarzenia

Cel:

Informowanie systemu o zmianie stanu.

Nie wymaga bezpośredniej odpowiedzi.

Model:

EVENT

↓

SUBSCRIBERS

Przykłady:

AGENT_STARTED

TASK_COMPLETED

MODEL_TRAINED

VERSION_CREATED

ERROR_DETECTED

Przykład:

{
"type":"EVENT",
"name":"TASK_COMPLETED"
}
5. NOTIFICATION MESSAGE
Powiadomienie

Cel:

Przekazanie informacji.

Nie jest poleceniem.

Przykłady:

SYSTEM_UPDATE

WARNING

STATUS_CHANGE

INFORMATION

Przykład:

{
"type":"NOTIFICATION",
"message":"New model available"
}
6. ERROR MESSAGE
Komunikat błędu

Cel:

Przekazanie informacji o problemie.

Model:

ERROR

↓

ANALYSIS

↓

RECOVERY

Przykłady:

MODULE_FAILURE

INVALID_MESSAGE

ACCESS_DENIED

TIMEOUT

Przykład:

{
"type":"ERROR",
"code":"API_001",
"message":"Connection failed"
}
7. SYSTEM MESSAGE
Komunikaty wewnętrzne systemu

Używane przez:

Core,
Runtime,
Infrastructure.

Przykłady:

SYSTEM_BOOT

SYSTEM_SHUTDOWN

HEALTH_CHECK

SYNC_REQUEST
Typy specjalistyczne

Poza podstawowymi typami SSI może posiadać rozszerzenia.

TASK MESSAGE

Komunikaty dotyczące zadań.

Przykłady:

TASK_CREATED

TASK_ASSIGNED

TASK_PROGRESS

TASK_COMPLETED
AGENT MESSAGE

Komunikacja agentów.

Przykłady:

AGENT_REGISTER

AGENT_REQUEST

AGENT_RESPONSE
MEMORY MESSAGE

Komunikacja pamięci.

Przykłady:

STORE_MEMORY

RETRIEVE_MEMORY

UPDATE_MEMORY
KNOWLEDGE MESSAGE

Komunikacja wiedzy.

Przykłady:

ADD_KNOWLEDGE

VALIDATE_KNOWLEDGE

QUERY_KNOWLEDGE
MESSAGE TYPE STRUCTURE

Każdy typ posiada definicję:

{
"type_id":"",
"name":"",
"category":"",
"purpose":"",
"sender_rules":"",
"receiver_rules":"",
"payload_schema":"",
"security_level":""
}
MESSAGE TYPE LIFECYCLE

Przykład:

COMMAND:

CREATED

↓

VALIDATED

↓

QUEUED

↓

EXECUTED

↓

COMPLETED

EVENT:

CREATED

↓

PUBLISHED

↓

CONSUMED

↓

ARCHIVED
Reguły wyboru typu

System wybiera typ według celu.

Przykład:

Chcesz wykonać akcję:

COMMAND

Chcesz pobrać dane:

REQUEST

Informujesz o zmianie:

EVENT

Przekazujesz wynik:

RESPONSE

Informujesz o problemie:

ERROR
Message Router a typ wiadomości

Router wykorzystuje typ do decyzji:

MESSAGE TYPE

↓

ROUTING RULE

↓

TARGET

Przykład:

ERROR

↓

ERROR_HANDLER
TASK_REQUEST

↓

TASK_MANAGER
Walidacja typów

System sprawdza:

czy typ istnieje,
czy nadawca może go wysłać,
czy odbiorca obsługuje typ,
czy payload pasuje.
Rozszerzanie systemu typów

Nowy typ:

CREATE TYPE

↓

DEFINE SCHEMA

↓

REGISTER

↓

TEST

↓

ENABLE
Przykładowa komunikacja SSI

Proces budowy modułu:

DIRECTOR

↓

COMMAND:
CREATE_MODULE


PROGRAMMER_AGENT

↓

RESPONSE:
MODULE_CREATED


SYSTEM

↓

EVENT:
MODULE_AVAILABLE


VALIDATOR

↓

REQUEST:
CHECK_MODULE


VALIDATOR

↓

RESPONSE:
VALIDATION_SUCCESS
Integracja z innymi dokumentami

05_MESSAGE_TYPE_SYSTEM.md łączy się z:

03_MESSAGE_OBJECT_MODEL.md

↓

04_MESSAGE_FORMAT_SPECIFICATION.md

↓

06_MESSAGE_HEADER_SPECIFICATION.md

↓

13_MESSAGE_REQUEST_RESPONSE_FORMAT.md

↓

14_MESSAGE_EVENT_FORMAT.md

↓

15_MESSAGE_COMMAND_FORMAT.md

↓

17_MESSAGE_ERROR_FORMAT.md

↓

18_MESSAGE_VALIDATION_RULES.md
Cel końcowy

05_MESSAGE_TYPE_SYSTEM.md definiuje język komunikacji SSI_SELF_DEVELOPMENT_ENGINE.

Po wdrożeniu:

każdy komunikat ma jasne znaczenie,
agenci wiedzą jak reagować,
router może inteligentnie kierować wiadomości,
system może analizować komunikację,
nowe moduły mogą korzystać ze wspólnego standardu.

Jest to system gramatyki komunikacyjnej SSI — zbiór zasad określający, jakie informacje mogą być przekazywane pomiędzy autonomicznymi elementami AI i jak powinny być interpretowane.