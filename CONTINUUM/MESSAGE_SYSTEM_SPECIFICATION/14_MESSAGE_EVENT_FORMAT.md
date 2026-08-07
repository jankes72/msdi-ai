Opis:

Ten dokument definiuje standard komunikatów typu Event (zdarzenie) w systemie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie jak system informuje inne moduły i agentów, że w środowisku SSI zaszło określone zdarzenie, jak wygląda struktura takiej wiadomości, jak są obsługiwani subskrybenci oraz jak system reaguje na zmiany stanu bez konieczności ciągłego wysyłania zapytań.

Jeżeli:

13_MESSAGE_REQUEST_RESPONSE_FORMAT.md definiuje dialog pytanie → odpowiedź,
14_MESSAGE_EVENT_FORMAT.md definiuje informowanie o zdarzeniach,

to:

14_MESSAGE_EVENT_FORMAT.md opisuje mechanizm "sygnałów" SSI — sposób, w jaki system sam informuje elementy o ważnych zmianach.

Cel dokumentu

Dokument odpowiada na pytania:

Czym jest zdarzenie w SSI?
Kiedy system generuje Event?
Jak wygląda struktura komunikatu Event?
Kto otrzymuje informacje o zdarzeniu?
Jak agenci reagują na wydarzenia?
Jak przechowywać historię zdarzeń?
Jak budować automatyczną reakcję systemu?
Rola dokumentu

Dokument jest podstawą dla:

Event System,
Message Router,
Agent Coordination System,
Memory System,
Knowledge System,
Automation Engine,
Monitoring System.
Główna zasada Event

Request mówi:

"Wykonaj coś."

Response mówi:

"Wynik wykonania."

Event mówi:

"Coś się wydarzyło."

Przykład:

MODEL_TRAINING_COMPLETED

Nie jest to pytanie.

Nie jest to polecenie.

Jest to informacja dla systemu.

Miejsce Event w komunikacji
MESSAGE SYSTEM


REQUEST

↓

RESPONSE


EVENT

↓

SUBSCRIBERS
Architektura Event System
EVENT SOURCE

      │

      ▼

EVENT GENERATOR

      │

      ▼

EVENT MESSAGE

      │

      ▼

EVENT ROUTER

      │

 ┌────┼─────┐

 ▼    ▼     ▼

AGENT MEMORY KNOWLEDGE
Główne komponenty
MESSAGE EVENT SYSTEM

│
├── Event Generator
│
├── Event Object
│
├── Event Router
│
├── Subscription Manager
│
├── Event Handler
│
├── Event Storage
│
└── Event Analyzer
1. EVENT OBJECT

Podstawowa jednostka zdarzenia.

Struktura:

{
"event":
{
"event_id":"",
"type":"",
"source":"",
"time":"",
"data":{}
}
}
2. EVENT_ID

Unikalny identyfikator.

Przykład:

EVENT-00001

Umożliwia:

śledzenie,
historię,
analizę.
3. EVENT_TYPE

Typ zdarzenia.

Przykłady:

SYSTEM_STARTED

TASK_CREATED

TASK_COMPLETED

MODEL_TRAINED

AGENT_CREATED

ERROR_OCCURRED

MEMORY_UPDATED
4. EVENT_SOURCE

Źródło zdarzenia.

Przykład:

MODEL_MANAGER

TASK_MANAGER

MEMORY_SYSTEM

VALIDATION_AGENT
5. EVENT_TIMESTAMP

Czas wystąpienia.

Przykład:

{
"time":
"2026-08-06T12:00:00"
}
6. EVENT_DATA

Dane związane ze zdarzeniem.

Przykład:

{
"event_data":
{
"model":"QWEN7B",
"status":"TRAINED"
}
}
Typy Event
1. SYSTEM EVENTS

Zdarzenia systemowe.

Przykłady:

SYSTEM_BOOT

SYSTEM_SHUTDOWN

CONFIG_CHANGED
2. AGENT EVENTS

Dotyczą agentów.

Przykłady:

AGENT_CREATED

AGENT_READY

AGENT_OFFLINE

AGENT_FAILED
3. TASK EVENTS

Dotyczą zadań.

Przykłady:

TASK_CREATED

TASK_STARTED

TASK_COMPLETED

TASK_FAILED
4. MODEL EVENTS

Dotyczą modeli AI.

Przykłady:

MODEL_LOADED

MODEL_TRAINED

MODEL_UPDATED

MODEL_RETIRED
5. MEMORY EVENTS

Dotyczą pamięci.

Przykłady:

MEMORY_CREATED

MEMORY_UPDATED

MEMORY_COMPRESSED
6. KNOWLEDGE EVENTS

Dotyczą wiedzy.

Przykłady:

KNOWLEDGE_ADDED

KNOWLEDGE_VALIDATED

KNOWLEDGE_UPDATED
Event Payload

Event posiada własne dane:

{
"event":
{
"type":"TASK_COMPLETED",

"payload":
{
"task_id":"TASK001",
"result":"SUCCESS"
}
}
}
Event vs Request
Request:
Agent A

↓

"Sprawdź status modelu"
Event:
Model Manager

↓

"Model został załadowany"
Event Subscription System

Agenci mogą subskrybować zdarzenia.

Przykład:

VALIDATION_AGENT

SUBSCRIBE:

CODE_CHANGED

Po zdarzeniu:

CODE_CHANGED

↓

VALIDATION_AGENT

↓

START TEST
Event Filtering

Nie każdy agent otrzymuje wszystko.

Filtry:

typ,
źródło,
projekt,
priorytet.

Przykład:

{
"subscribe":
{
"event":"MODEL_TRAINED",
"source":"MODEL_MANAGER"
}
}
Event Priority

Niektóre zdarzenia są ważniejsze.

Przykład:

SECURITY_BREACH

>

DOCUMENT_UPDATED
Event Processing Lifecycle
EVENT_CREATED

↓

EVENT_VALIDATED

↓

EVENT_ROUTED

↓

EVENT_DELIVERED

↓

EVENT_HANDLED

↓

EVENT_ARCHIVED
Event Handler

Każdy agent może posiadać reakcje.

Przykład:

EVENT:

TASK_FAILED


HANDLER:

CREATE_RECOVERY_TASK
Automatyczne reakcje

Przykład:

DATABASE_ERROR

↓

EVENT

↓

RECOVERY_AGENT

↓

BACKUP_RESTORE
Event Storage

System zapisuje:

ID,
typ,
źródło,
czas,
odbiorców,
reakcję.

Przykład:

{
"event_history":
{
"id":"EVENT001",
"type":"MODEL_TRAINED",
"handled":true
}
}
Event Replay

Możliwość ponownego odtworzenia zdarzeń.

Przykład:

EVENT HISTORY

↓

REPLAY

↓

RESTORE STATE

Zastosowanie:

recovery,
testy,
analiza.
Event Security

Kontrola:

kto może generować event,
kto może odbierać,
kto może reagować.

Przykład:

ONLY SYSTEM_CORE

CAN CREATE:

SYSTEM_SHUTDOWN
Event Learning

SSI może analizować:

częstotliwość zdarzeń,
reakcje agentów,
skuteczność obsługi.

Przykład:

TASK_FAILED

↓

RECOVERY_SUCCESS:

95%
Przykładowy pełny Event
{
"header":
{
"type":"EVENT",
"source":"MODEL_MANAGER"
},

"event":
{
"event_id":"EVENT-001",

"type":"MODEL_TRAINED",

"timestamp":"2026-08-06T12:00:00",

"payload":
{
"model":"QWEN2.5-CODER",
"accuracy":"92%"
}
}
}
Integracja z innymi dokumentami

14_MESSAGE_EVENT_FORMAT.md łączy się z:

03_MESSAGE_OBJECT_MODEL.md

↓

04_MESSAGE_FORMAT_SPECIFICATION.md

↓

07_MESSAGE_PAYLOAD_SPECIFICATION.md

↓

08_MESSAGE_CONTEXT_MODEL.md

↓

09_MESSAGE_ROUTING_SYSTEM.md

↓

10_MESSAGE_QUEUE_SYSTEM.md

↓

12_MESSAGE_STATUS_LIFECYCLE.md

↓

15_MESSAGE_BROADCAST_SYSTEM.md

↓

16_MESSAGE_SUBSCRIPTION_SYSTEM.md

↓

MEMORY_EVENT_SYSTEM.md

↓

KNOWLEDGE_UPDATE_SYSTEM.md
Cel końcowy

14_MESSAGE_EVENT_FORMAT.md definiuje mechanizm reaktywnej komunikacji SSI_SELF_DEVELOPMENT_ENGINE.

Po wdrożeniu:

moduły nie muszą stale pytać o stan systemu,
ważne zmiany są automatycznie rozsyłane,
agenci mogą reagować samodzielnie,
system może budować automatyczne workflow,
historia zdarzeń pozostaje dostępna.

Jest to system nerwowy reakcji SSI — mechanizm, który pozwala całemu organizmowi AI zauważać zmiany i natychmiast na nie reagować.