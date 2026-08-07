Opis:

Ten dokument definiuje standard komunikatów typu Notification (powiadomienie) w systemie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie jak system przekazuje informacje o ważnych zmianach, stanach, ostrzeżeniach i aktualizacjach, które wymagają poinformowania innych modułów lub agentów, ale nie wymagają bezpośredniego wykonania działania jak Command ani odpowiedzi jak Request.

Jeżeli:

13_MESSAGE_REQUEST_RESPONSE_FORMAT.md definiuje pytanie i odpowiedź,
14_MESSAGE_EVENT_FORMAT.md definiuje zdarzenia systemowe,
15_MESSAGE_COMMAND_FORMAT.md definiuje polecenia wykonawcze,
16_MESSAGE_NOTIFICATION_FORMAT.md definiuje informowanie zainteresowanych komponentów,

to:

16_MESSAGE_NOTIFICATION_FORMAT.md opisuje system komunikatów informacyjnych SSI — mechanizm przekazywania świadomości o stanie systemu bez wymuszania natychmiastowej akcji.

Cel dokumentu

Dokument odpowiada na pytania:

Czym różni się Notification od Event?
Kiedy system wysyła powiadomienie?
Kto powinien otrzymać informację?
Jak wygląda struktura Notification?
Jak obsługiwać ostrzeżenia?
Jak informować agentów o zmianach?
Jak przechowywać historię powiadomień?
Rola dokumentu

Dokument jest podstawą dla:

Agent Communication System,
Monitoring System,
User Interface Layer,
Dashboard System,
Logging System,
Alert Management System,
Knowledge System.
Główna zasada Notification

Notification oznacza:

"Informuję cię, że coś jest ważne, ale nie wymagam od ciebie konkretnego działania."

Przykład:

MODEL_VERSION_UPDATED

Odbiorca może:

zapisać informację,
zaktualizować wiedzę,
zignorować.
Różnica między typami wiadomości
COMMAND

Nakazuje:

Wykonaj działanie

Przykład:

RESTART_MODEL
REQUEST

Pyta:

Podaj informację

Przykład:

GET_MODEL_STATUS
EVENT

Informuje:

Coś się wydarzyło

Przykład:

MODEL_TRAINING_COMPLETED
NOTIFICATION

Informuje:

Powinieneś wiedzieć

Przykład:

NEW_MODEL_AVAILABLE
Miejsce Notification w systemie
MESSAGE SYSTEM


COMMAND

↓

ACTION


REQUEST

↓

ANSWER


EVENT

↓

REACTION


NOTIFICATION

↓

AWARENESS
Architektura Notification
SOURCE MODULE

      │

      ▼

NOTIFICATION GENERATOR

      │

      ▼

NOTIFICATION MESSAGE

      │

      ▼

MESSAGE ROUTER

      │

 ┌────┼────┐

 ▼    ▼    ▼

AGENT MEMORY KNOWLEDGE
Główne komponenty
MESSAGE NOTIFICATION SYSTEM

│
├── Notification Generator
│
├── Notification Object
│
├── Notification Router
│
├── Subscription Manager
│
├── Notification Priority Manager
│
├── Notification Storage
│
└── Notification History
1. NOTIFICATION OBJECT

Podstawowa struktura.

{
"notification":
{
"id":"",
"type":"",
"source":"",
"target":"",
"message":"",
"metadata":{}
}
}
2. NOTIFICATION_ID

Unikalny identyfikator.

Przykład:

NOTIFY-00001

Służy do:

śledzenia,
historii,
audytu.
3. NOTIFICATION_TYPE

Typ informacji.

Przykłady:

INFO

WARNING

UPDATE

CHANGE

REMINDER

ALERT
4. SOURCE

Źródło powiadomienia.

Przykład:

MODEL_MANAGER

MEMORY_SYSTEM

DIRECTOR_CORE

VALIDATION_AGENT
5. TARGET

Odbiorca.

Może być:

Jeden agent
PROGRAMMER_AGENT
Grupa
ALL_DEVELOPMENT_AGENTS
Cały system
SYSTEM_BROADCAST
6. MESSAGE CONTENT

Treść informacji.

Przykład:

{
"message":
"Model QWEN został zaktualizowany"
}
7. METADATA

Dodatkowe informacje.

Przykład:

{
"version":"2.0",
"time":"2026-08-06"
}
Typy Notification
1. SYSTEM NOTIFICATION

Informacje systemowe.

Przykłady:

SYSTEM_STARTED

SYSTEM_UPDATE_AVAILABLE

CONFIG_CHANGED
2. AGENT NOTIFICATION

Dotyczy agentów.

Przykłady:

AGENT_READY

AGENT_STATUS_CHANGED

NEW_AGENT_AVAILABLE
3. TASK NOTIFICATION

Dotyczy pracy.

Przykłady:

TASK_ASSIGNED

TASK_DELAYED

TASK_COMPLETED
4. MODEL NOTIFICATION

Dotyczy AI.

Przykłady:

MODEL_UPDATED

MODEL_AVAILABLE

MODEL_DEPRECATED
5. MEMORY NOTIFICATION

Dotyczy pamięci.

Przykłady:

MEMORY_UPDATED

MEMORY_COMPRESSED

MEMORY_ARCHIVED
6. KNOWLEDGE NOTIFICATION

Dotyczy wiedzy.

Przykłady:

KNOWLEDGE_ADDED

KNOWLEDGE_UPDATED

KNOWLEDGE_VALIDATED
Notification Priority

Nie wszystkie informacje są tak samo ważne.

Poziomy:

CRITICAL

HIGH

NORMAL

LOW

INFO

Przykład:

SECURITY_WARNING

>

DOCUMENT_UPDATED
Notification Lifecycle
CREATED

↓

VALIDATED

↓

ROUTED

↓

DELIVERED

↓

READ

↓

ARCHIVED
Stany Notification
CREATED

Powiadomienie wygenerowane.

SENT

Wysłane.

DELIVERED

Dotarło.

READ

Odbiorca zapoznał się.

ACKNOWLEDGED

Odbiorca potwierdził.

ARCHIVED

Zapisane w historii.

Notification Subscription

Agenci mogą wybierać informacje.

Przykład:

MEMORY_AGENT

SUBSCRIBE:

MEMORY_UPDATED
Notification Filtering

Filtry:

typ,
źródło,
priorytet,
projekt.

Przykład:

{
"type":"MODEL_UPDATE",
"priority":"HIGH"
}
Notification vs Event

Bardzo ważne rozróżnienie:

Event

Systemowy fakt:

MODEL_TRAINING_FINISHED
Notification

Informacja dla odbiorcy:

Nowy model jest dostępny do użycia

Czyli:

EVENT

↓

GENERUJE

↓

NOTIFICATION
Przykładowy przepływ

Model zakończył trening:

MODEL_MANAGER

↓

EVENT:

MODEL_TRAINED


↓

NOTIFICATION:

NEW_MODEL_AVAILABLE


↓

AGENTS
Notification History

System zapisuje:

kiedy wysłano,
komu,
czy odczytano.

Przykład:

{
"id":"NOT001",
"type":"UPDATE",
"target":"PROGRAMMER_AGENT",
"read":true
}
Notification Storage

Powiadomienia mogą być przechowywane:

tymczasowo,
w bazie,
w pamięci długoterminowej.
Notification Security

Kontrola:

kto może wysyłać,
kto może odbierać,
jakie dane są widoczne.

Przykład:

SYSTEM_SECURITY_ALERT

widoczny tylko:

SYSTEM_CORE
DIRECTOR_CORE
Notification Automation

Powiadomienia mogą uruchamiać reakcje.

Przykład:

NOTIFICATION:

NEW_MODEL_AVAILABLE


↓

MODEL_MANAGER

LOAD MODEL
Notification Learning

SSI może analizować:

które informacje są ważne,
które są ignorowane,
które agenty potrzebują danych.

Przykład:

AGENT A

IGNORES:

90% NOTIFICATIONS

System może zmienić subskrypcję.

Pełny przykład Notification
{
"header":
{
"type":"NOTIFICATION",
"source":"MODEL_MANAGER"
},

"notification":
{
"id":"NOTIFY001",

"type":"UPDATE",

"priority":"NORMAL",

"message":
{
"model":"QWEN2.5-CODER",
"status":"AVAILABLE"
}
}
}
Integracja z innymi dokumentami

16_MESSAGE_NOTIFICATION_FORMAT.md łączy się z:

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

11_MESSAGE_PRIORITY_SYSTEM.md

↓

12_MESSAGE_STATUS_LIFECYCLE.md

↓

14_MESSAGE_EVENT_FORMAT.md

↓

17_MESSAGE_BROADCAST_SYSTEM.md

↓

18_MESSAGE_SUBSCRIPTION_SYSTEM.md
Cel końcowy

16_MESSAGE_NOTIFICATION_FORMAT.md definiuje warstwę świadomości informacyjnej SSI_SELF_DEVELOPMENT_ENGINE.

Po wdrożeniu:

agenci wiedzą, co dzieje się w systemie,
moduły mogą reagować na zmiany,
informacje są filtrowane,
komunikacja nie jest przeciążona,
każdy element otrzymuje tylko potrzebne dane.

Jest to system powiadamiania organizmu SSI — mechanizm, który pozwala wszystkim częściom AI utrzymywać wspólną świadomość aktualnego stanu systemu bez ciągłego odpytywania.