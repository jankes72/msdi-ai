Opis:

Ten dokument definiuje standard komunikatów typu Error (błąd / wyjątek systemowy) w systemie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie jak system zgłasza problemy, jak opisuje błędy, jak przekazuje informacje o przyczynie awarii, jak klasyfikuje poziom zagrożenia oraz jak umożliwia agentom i modułom wykonanie odpowiedniej reakcji naprawczej.

Jeżeli:

13_MESSAGE_REQUEST_RESPONSE_FORMAT.md definiuje pytanie i odpowiedź,
14_MESSAGE_EVENT_FORMAT.md definiuje zdarzenia systemowe,
15_MESSAGE_COMMAND_FORMAT.md definiuje polecenia wykonawcze,
16_MESSAGE_NOTIFICATION_FORMAT.md definiuje informowanie o zmianach,
17_MESSAGE_ERROR_FORMAT.md definiuje komunikację o problemach,

to:

17_MESSAGE_ERROR_FORMAT.md jest systemem alarmowym SSI — mechanizmem wykrywania, opisywania, przekazywania i obsługi błędów całego ekosystemu AI.

Cel dokumentu

Dokument odpowiada na pytania:

Jak wygląda komunikat błędu?
Jak sklasyfikować błąd?
Kto powinien otrzymać informację?
Czy błąd wymaga natychmiastowej reakcji?
Jak przekazać szczegóły diagnostyczne?
Jak uruchomić procedurę naprawczą?
Jak zapisać historię błędów?
Rola dokumentu

Dokument jest podstawą dla:

Error Handling System,
Recovery System,
Monitoring System,
Logging System,
Agent Coordination System,
Self Improvement Loop,
Debugging System.
Główna zasada Error Message

Błąd nie jest tylko informacją:

"coś nie działa"

Błąd musi zawierać:

co się stało,
gdzie się stało,
dlaczego,
jak poważne jest,
co należy zrobić.
Miejsce Error w systemie wiadomości
MESSAGE SYSTEM


REQUEST

↓

RESPONSE


EVENT

↓

REACTION


COMMAND

↓

ACTION


ERROR

↓

RECOVERY
Architektura Error Flow
MODULE FAILURE

      │

      ▼

ERROR GENERATOR

      │

      ▼

ERROR MESSAGE

      │

      ▼

ERROR ROUTER

      │

 ┌────┼────────┐

 ▼    ▼        ▼

LOG  MEMORY  RECOVERY
Główne komponenty
MESSAGE ERROR SYSTEM

│
├── Error Detector
│
├── Error Object
│
├── Error Classifier
│
├── Error Router
│
├── Recovery Manager
│
├── Error Logger
│
└── Error Analyzer
1. ERROR OBJECT

Podstawowa struktura błędu.

{
"error":
{
"error_id":"",
"type":"",
"severity":"",
"source":"",
"description":"",
"context":"",
"solution":""
}
}
2. ERROR_ID

Unikalny identyfikator.

Przykład:

ERR-00001

Używany do:

śledzenia,
analizy,
historii.
3. ERROR_TYPE

Typ błędu.

Przykłady:

SYSTEM_ERROR

MODULE_ERROR

AGENT_ERROR

DATA_ERROR

MODEL_ERROR

SECURITY_ERROR

COMMUNICATION_ERROR
4. ERROR_SEVERITY

Poziom krytyczności.

CRITICAL

Najwyższe zagrożenie.

Przykłady:

DATABASE_CORRUPTION

SYSTEM_CRASH

SECURITY_BREACH

Reakcja:

NATYCHMIASTOWA
HIGH

Poważny problem.

Przykłady:

MODEL_FAILED

AGENT_UNAVAILABLE

TASK_BLOCKED
MEDIUM

Problem wymagający uwagi.

Przykłady:

PERFORMANCE_DROP

TIMEOUT
LOW

Informacyjny problem.

Przykład:

OPTIONAL_SERVICE_FAILED
5. ERROR_SOURCE

Źródło błędu.

Przykład:

DIRECTOR_CORE

MEMORY_MANAGER

MODEL_MANAGER

PROGRAMMER_AGENT
6. ERROR_DESCRIPTION

Opis problemu.

Przykład:

Model QWEN nie został załadowany.
7. ERROR_CONTEXT

Informacje pomocnicze.

Przykład:

{
"context":
{
"task_id":"TASK001",
"agent":"MODEL_AGENT",
"operation":"LOAD_MODEL"
}
}
8. ERROR_STACK

Informacje techniczne.

Przykład:

FILE:

model_loader.py

LINE:

120
Typy błędów
1. SYSTEM ERROR

Problemy całego systemu.

Przykłady:

SYSTEM_START_FAILED

CONFIG_INVALID

RUNTIME_CRASH
2. MODULE ERROR

Problem konkretnego modułu.

Przykłady:

MODULE_LOAD_FAILED

MODULE_NOT_FOUND
3. AGENT ERROR

Problemy agentów.

Przykłady:

AGENT_CRASH

AGENT_TIMEOUT

AGENT_INVALID_RESPONSE
4. DATA ERROR

Problemy danych.

Przykłady:

INVALID_DATA

CORRUPTED_FILE

MISSING_DATA
5. MODEL ERROR

Problemy AI.

Przykłady:

MODEL_LOAD_FAILED

TRAINING_FAILED

INFERENCE_ERROR
6. COMMUNICATION ERROR

Problemy komunikacji.

Przykłady:

MESSAGE_LOST

ROUTE_NOT_FOUND

DELIVERY_TIMEOUT
7. SECURITY ERROR

Problemy bezpieczeństwa.

Przykłady:

UNAUTHORIZED_ACCESS

INVALID_PERMISSION

SECURITY_VIOLATION
Error Lifecycle
DETECTED

↓

CREATED

↓

CLASSIFIED

↓

ROUTED

↓

HANDLED

↓

RECOVERED

↓

ARCHIVED
Stany błędu
DETECTED

System zauważył problem.

ANALYZING

Trwa analiza.

HANDLING

Uruchomiono obsługę.

RECOVERING

Trwa naprawa.

RESOLVED

Problem rozwiązany.

CLOSED

Zamknięty w historii.

Error Routing

Przykład:

MODEL_ERROR

↓

MODEL_MANAGER

↓

RECOVERY_AGENT

Błąd bezpieczeństwa:

SECURITY_ERROR

↓

SYSTEM_CORE

↓

SECURITY_MANAGER
Error Priority

Każdy błąd otrzymuje priorytet.

Przykład:

SECURITY_BREACH

CRITICAL

natomiast:

MINOR_WARNING

LOW
Error Response

Po wykryciu błędu system może wysłać:

Event
ERROR_OCCURRED
Notification
SYSTEM_WARNING
Command
START_RECOVERY
Przykład pełnego Error Message
{
"header":
{
"type":"ERROR",
"source":"MODEL_MANAGER"
},

"error":
{
"error_id":"ERR001",

"type":"MODEL_ERROR",

"severity":"HIGH",

"description":
"Model nie został załadowany",

"context":
{
"model":"QWEN2.5-CODER",
"operation":"LOAD"
},

"recovery":
{
"action":"RETRY_LOAD"
}
}
}
Error Recovery

System może wykonywać:

ERROR

↓

ANALYSIS

↓

RECOVERY PLAN

↓

COMMAND

↓

FIX

Przykład:

MODEL_LOAD_FAILED

↓

RETRY_LOAD_MODEL

↓

MODEL_AVAILABLE
Error Retry Policy

System określa:

ile prób,
odstęp czasowy,
alternatywną metodę.

Przykład:

{
"max_retry":3,
"delay":"60s"
}
Error Learning

SSI analizuje:

częstotliwość błędów,
przyczyny,
skuteczność napraw.

Przykład:

ERROR:

MEMORY_FAILURE


CAUSE:

LOW_STORAGE


SOLUTION:

AUTO_CLEANUP
Error Memory

Błędy są zapisywane w pamięci:

historia,
rozwiązania,
wzorce.

Przykład:

PROBLEM

↓

SOLUTION

↓

FUTURE PREVENTION
Error Security

Błędy mogą zawierać wrażliwe dane.

Dlatego:

ograniczenie dostępu,
maskowanie danych,
kontrola logów.
Integracja z innymi dokumentami

17_MESSAGE_ERROR_FORMAT.md łączy się z:

03_MESSAGE_OBJECT_MODEL.md

↓

04_MESSAGE_FORMAT_SPECIFICATION.md

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

15_MESSAGE_COMMAND_FORMAT.md

↓

18_MESSAGE_RECOVERY_PROTOCOL.md

↓

ERROR_HANDLING_SYSTEM_SPECIFICATION.md

↓

SELF_IMPROVEMENT_LOOP.md
Cel końcowy

17_MESSAGE_ERROR_FORMAT.md definiuje system odporności SSI_SELF_DEVELOPMENT_ENGINE na błędy.

Po wdrożeniu:

każdy problem ma standardowy format,
błędy są klasyfikowane,
system sam reaguje,
historia awarii jest zachowana,
AI może uczyć się na własnych problemach.

Jest to układ odpornościowy SSI — mechanizm, który wykrywa uszkodzenia, reaguje na nie i pomaga systemowi rozwijać się poprzez analizę własnych błędów.