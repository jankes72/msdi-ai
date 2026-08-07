Opis:

Ten dokument definiuje standard komunikatów typu Command (polecenie / rozkaz wykonawczy) w systemie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie jak jeden element systemu może wydać konkretne polecenie innemu modułowi lub agentowi, jak wygląda struktura takiego polecenia, jakie dane są wymagane do wykonania operacji oraz jak kontrolowany jest proces realizacji komendy.

Jeżeli:

13_MESSAGE_REQUEST_RESPONSE_FORMAT.md definiuje zapytanie i oczekiwanie na odpowiedź,
14_MESSAGE_EVENT_FORMAT.md definiuje informowanie o zmianach,
15_MESSAGE_COMMAND_FORMAT.md definiuje wydawanie instrukcji wykonania działania,

to:

15_MESSAGE_COMMAND_FORMAT.md opisuje język sterowania SSI — standard, według którego moduły i agenci otrzymują konkretne zadania do wykonania.

Cel dokumentu

Dokument odpowiada na pytania:

Jak wygląda polecenie w SSI?
Kto może wydawać komendy?
Jak agent rozumie, co ma zrobić?
Jak przekazywane są parametry wykonania?
Jak kontrolować wykonanie polecenia?
Jak rozróżnić komendę od zwykłej informacji?
Jak obsługiwać błędne lub niedozwolone polecenia?
Rola dokumentu

Dokument jest podstawą dla:

Director Core,
Task Management System,
Agent Execution Engine,
Internal Orchestrator,
Command Router,
Automation Engine.
Główna zasada Command

Command nie pyta.

Command nakazuje wykonanie działania.

Przykład:

REQUEST:

"Jaki jest status agenta?"

COMMAND:

"Uruchom agenta walidacji."
Miejsce Command w systemie wiadomości
MESSAGE SYSTEM


REQUEST

↓

RESPONSE


EVENT

↓

NOTIFICATION


COMMAND

↓

ACTION
Architektura Command Flow
COMMAND SOURCE

      │

      ▼

COMMAND MESSAGE

      │

      ▼

COMMAND ROUTER

      │

      ▼

TARGET AGENT

      │

      ▼

EXECUTION ENGINE

      │

      ▼

RESULT EVENT
Główne komponenty
MESSAGE COMMAND SYSTEM

│
├── Command Object
│
├── Command Parser
│
├── Command Validator
│
├── Command Authorization
│
├── Command Executor
│
├── Command Tracker
│
└── Command History
1. COMMAND OBJECT

Podstawowa struktura komendy.

{
"command":
{
"command_id":"",
"type":"",
"action":"",
"target":"",
"parameters":{}
}
}
2. COMMAND_ID

Unikalny identyfikator.

Przykład:

CMD-00001

Służy do:

śledzenia,
logowania,
kontroli wykonania.
3. COMMAND_TYPE

Typ polecenia.

Przykłady:

CREATE

UPDATE

DELETE

START

STOP

EXECUTE

RESTART

CONFIGURE
4. COMMAND_ACTION

Konkretna operacja.

Przykłady:

CREATE_AGENT

LOAD_MODEL

TRAIN_MODEL

RUN_TEST

UPDATE_MEMORY

GENERATE_DOCUMENT
5. COMMAND_TARGET

Odbiorca komendy.

Przykład:

{
"target":
{
"type":"AGENT",
"id":"PROGRAMMER_AGENT"
}
}
6. COMMAND_PARAMETERS

Dane potrzebne do wykonania.

Przykład:

{
"parameters":
{
"model":"QWEN2.5-CODER",
"mode":"TRAIN"
}
}
Pełny przykład Command
{
"header":
{
"type":"COMMAND",
"sender":"DIRECTOR_CORE",
"receiver":"MODEL_MANAGER"
},

"command":
{
"command_id":"CMD-001",

"type":"START",

"action":"LOAD_MODEL",

"target":"MODEL_MANAGER",

"parameters":
{
"model":"QWEN2.5-CODER"
}
}
}
Typy komend
1. SYSTEM COMMAND

Komendy systemowe.

Przykłady:

START_SYSTEM

STOP_SYSTEM

RESTART_SYSTEM

UPDATE_CONFIG
2. AGENT COMMAND

Sterowanie agentami.

Przykłady:

CREATE_AGENT

START_AGENT

PAUSE_AGENT

REMOVE_AGENT
3. TASK COMMAND

Sterowanie zadaniami.

Przykłady:

CREATE_TASK

ASSIGN_TASK

CANCEL_TASK

RETRY_TASK
4. MODEL COMMAND

Sterowanie modelami AI.

Przykłady:

LOAD_MODEL

UNLOAD_MODEL

TRAIN_MODEL

EVALUATE_MODEL
5. MEMORY COMMAND

Sterowanie pamięcią.

Przykłady:

SAVE_MEMORY

SEARCH_MEMORY

COMPRESS_MEMORY

DELETE_MEMORY
6. KNOWLEDGE COMMAND

Sterowanie wiedzą.

Przykłady:

ADD_KNOWLEDGE

VALIDATE_KNOWLEDGE

UPDATE_KNOWLEDGE
Command Execution Lifecycle

Każda komenda przechodzi przez etapy:

CREATED

↓

VALIDATED

↓

AUTHORIZED

↓

QUEUED

↓

EXECUTING

↓

COMPLETED
Stany komendy
CREATED

Komenda została wygenerowana.

VALIDATED

Sprawdzono poprawność.

AUTHORIZED

Sprawdzono uprawnienia.

QUEUED

Czeka na wykonanie.

EXECUTING

Agent wykonuje.

COMPLETED

Wykonanie zakończone.

FAILED

Wystąpił błąd.

Command Authorization

Nie każdy moduł może wykonywać wszystkie komendy.

Przykład:

DIRECTOR_CORE

może:

CREATE_AGENT


PROGRAMMER_AGENT

nie może:
STOP_SYSTEM
Command Permission Levels
ROOT

SYSTEM_ADMIN

AGENT_MANAGER

WORKER_AGENT

READ_ONLY
Command Validation

Przed wykonaniem:

COMMAND RECEIVED

↓

CHECK FORMAT

↓

CHECK TARGET

↓

CHECK PARAMETERS

↓

CHECK PERMISSION

↓

EXECUTE
Command Dependencies

Niektóre komendy wymagają wcześniejszych działań.

Przykład:

Nie można:

START_AGENT

jeżeli:

AGENT_NOT_CREATED
Command Priority

Komendy posiadają priorytet.

Przykład:

STOP_SYSTEM

CRITICAL

natomiast:

GENERATE_REPORT

LOW
Command Retry

Przy błędzie:

COMMAND

↓

FAILED

↓

RETRY

↓

SUCCESS
Command Result

Po wykonaniu generowany jest wynik.

Przykład:

{
"command_result":
{
"command_id":"CMD001",

"status":"SUCCESS",

"output":
{
"agent_id":"VALIDATION001"
}
}
}
Command vs Event
Command:

Źródło mówi:

WYKONAJ

Przykład:

TRAIN_MODEL
Event:

System mówi:

STAŁO SIĘ

Przykład:

MODEL_TRAINING_COMPLETED
Command vs Request
Request:
Sprawdź model.
Command:
Uruchom trening modelu.
Command History

System zapisuje:

kto wydał komendę,
kiedy,
do kogo,
wynik.

Przykład:

{
"command_history":
{
"id":"CMD001",
"action":"CREATE_AGENT",
"result":"SUCCESS"
}
}
Command Learning

SSI może analizować:

które komendy często zawodzą,
które agenty wykonują je najlepiej,
ile czasu zajmuje wykonanie.

Przykład:

TRAIN_MODEL

AVG TIME:

35 min
Command Automation

Komendy mogą być generowane automatycznie.

Przykład:

EVENT:

MODEL_FAILED


↓

COMMAND:

RESTART_MODEL
Command Security

Chronione operacje:

DELETE_MEMORY

STOP_SYSTEM

RESET_DATABASE

wymagają:

wysokiego poziomu dostępu,
potwierdzenia,
logowania.
Integracja z innymi dokumentami

15_MESSAGE_COMMAND_FORMAT.md łączy się z:

03_MESSAGE_OBJECT_MODEL.md

↓

06_MESSAGE_HEADER_SPECIFICATION.md

↓

07_MESSAGE_PAYLOAD_SPECIFICATION.md

↓

09_MESSAGE_ROUTING_SYSTEM.md

↓

10_MESSAGE_QUEUE_SYSTEM.md

↓

11_MESSAGE_PRIORITY_SYSTEM.md

↓

12_MESSAGE_STATUS_LIFECYCLE.md

↓

13_MESSAGE_REQUEST_RESPONSE_FORMAT.md

↓

16_MESSAGE_AUTHORIZATION_SYSTEM.md

↓

17_MESSAGE_EXECUTION_PROTOCOL.md
Cel końcowy

15_MESSAGE_COMMAND_FORMAT.md definiuje język sterowania systemem SSI_SELF_DEVELOPMENT_ENGINE.

Po wdrożeniu:

Director Core może zarządzać całym systemem,
agenci mogą otrzymywać jasne instrukcje,
każde działanie jest kontrolowane,
komendy mają historię,
system może wykonywać autonomiczne procesy.

Jest to warstwa wykonawcza komunikacji SSI — mechanizm, dzięki któremu AI nie tylko wymienia informacje, ale realnie steruje własnym działaniem i rozwojem.