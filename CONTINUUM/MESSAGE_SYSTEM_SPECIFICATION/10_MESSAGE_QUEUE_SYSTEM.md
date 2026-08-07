Opis:

Ten dokument definiuje system kolejek komunikatów (Message Queue System) w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie jak wiadomości są przechowywane tymczasowo pomiędzy wysłaniem a wykonaniem, jak system zarządza oczekującymi zadaniami, jak kontroluje kolejność obsługi, priorytety, przeciążenia oraz niezawodność komunikacji pomiędzy agentami i modułami SSI.

Jeżeli:

09_MESSAGE_ROUTING_SYSTEM.md odpowiada za dokąd wiadomość ma trafić,
10_MESSAGE_QUEUE_SYSTEM.md odpowiada za gdzie wiadomość czeka i jak jest obsługiwana,
11_MESSAGE_DELIVERY_SYSTEM.md będzie odpowiadał za faktyczne dostarczenie wiadomości,

to:

10_MESSAGE_QUEUE_SYSTEM.md definiuje pamięć operacyjną komunikacji SSI — miejsce, w którym wiadomości oczekują na wykonanie i są zarządzane przez system.

Cel dokumentu

Dokument odpowiada na pytania:

Gdzie przechowywane są wiadomości przed wykonaniem?
Jak wiele wiadomości może oczekiwać jednocześnie?
Jak ustalana jest kolejność wykonania?
Jak obsługiwać wiele agentów?
Co dzieje się, gdy agent jest zajęty?
Jak odzyskać wiadomości po awarii?
Jak monitorować stan kolejek?
Rola dokumentu

Dokument jest podstawą dla:

Message Router,
Task Management System,
Agent Execution Engine,
Runtime System,
Persistence Layer,
Monitoring System.
Główna zasada Message Queue

Komunikat nie musi być wykonany natychmiast.

Przepływ:

MESSAGE CREATED

↓

ROUTER

↓

QUEUE

↓

AGENT AVAILABLE

↓

EXECUTION
Dlaczego potrzebna jest kolejka?

Bez kolejki:

DIRECTOR

↓

PROGRAMMER AGENT

Problem:

agent może być zajęty,
wiadomość może zostać utracona,
brak historii,
brak kontroli.

Z kolejką:

DIRECTOR

↓

PROGRAMMER_QUEUE

↓

PROGRAMMER_AGENT

Korzyści:

niezawodność,
kontrola,
skalowanie,
historia.
Architektura Message Queue System
                MESSAGE QUEUE SYSTEM


MESSAGE INPUT

      │

      ▼

QUEUE MANAGER

      │

 ┌────┼─────────┐

 ▼    ▼         ▼

TASK  AGENT   EVENT

QUEUE QUEUE   QUEUE

 │     │        │

 ▼     ▼        ▼

WORKER WORKER SUBSCRIBER

Główne komponenty
MESSAGE QUEUE SYSTEM

│
├── Queue Manager
│
├── Queue Storage
│
├── Priority Scheduler
│
├── Consumer Manager
│
├── Retry Manager
│
├── Dead Letter Queue
│
└── Queue Monitor
1. QUEUE MANAGER
Zarządca kolejek

Główna funkcja:

tworzenie kolejek,
usuwanie,
obsługa wiadomości,
kontrola stanu.

Przykład:

CREATE QUEUE

↓

PROGRAMMER_QUEUE
2. QUEUE TYPES

SSI posiada różne typy kolejek.

AGENT QUEUE

Kolejka dla konkretnego agenta.

Przykład:

PROGRAMMER_AGENT_QUEUE

Zawiera:

zadania,
polecenia,
odpowiedzi.
TASK QUEUE

Kolejka zadań.

Przykład:

TASK_EXECUTION_QUEUE

Zawiera:

nowe zadania,
oczekujące procesy.
EVENT QUEUE

Kolejka zdarzeń.

Przykład:

EVENT_PROCESSING_QUEUE
SYSTEM QUEUE

Dla komunikatów systemowych.

Przykład:

SYSTEM_CONTROL_QUEUE
3. QUEUE MESSAGE STATES

Każda wiadomość posiada stan:

CREATED

↓

QUEUED

↓

PROCESSING

↓

COMPLETED

↓

ARCHIVED

Możliwe błędy:

FAILED

↓

RETRY

↓

DEAD_LETTER
4. MESSAGE PRIORITY QUEUE

Kolejka obsługuje priorytety.

Przykład:

QUEUE


CRITICAL

HIGH

NORMAL

LOW

BACKGROUND

Przykład:

Błąd bezpieczeństwa:

CRITICAL

wykonuje się przed:

BACKGROUND ANALYSIS
5. FIFO QUEUE

Standardowa kolejność:

First In First Out

Przykład:

MESSAGE 1

MESSAGE 2

MESSAGE 3

Wykonanie:

1 → 2 → 3
6. TASK SCHEDULING

Kolejka może planować wykonanie.

Przykład:

TASK

priority=HIGH

deadline=12:00

System ustala:

EXECUTION ORDER
7. MESSAGE LOCKING

Zapobiega podwójnemu wykonaniu.

Proces:

MESSAGE

↓

LOCK

↓

EXECUTE

↓

UNLOCK
8. CONSUMER SYSTEM

Agent pobiera wiadomości.

Schemat:

QUEUE

↓

CONSUMER

↓

AGENT

↓

EXECUTION

Przykład:

PROGRAMMER_AGENT

subscribes:

PROGRAMMER_QUEUE
9. QUEUE LOAD MANAGEMENT

Kontrola obciążenia.

System sprawdza:

ilość wiadomości,
czas oczekiwania,
dostępność agentów.

Przykład:

QUEUE SIZE:

10000

↓

START MORE WORKERS
10. RETRY SYSTEM

Jeżeli wykonanie się nie powiedzie:

MESSAGE

↓

FAILED

↓

RETRY 1

↓

RETRY 2

↓

SUCCESS

Konfiguracja:

{
"max_retry":3,
"delay":"30s"
}
11. DEAD LETTER QUEUE
Kolejka martwych wiadomości

Dla problematycznych komunikatów.

Proces:

FAILED MESSAGE

↓

DEAD LETTER QUEUE

↓

ANALYSIS

↓

RECOVERY
12. QUEUE PERSISTENCE

Kolejki mogą być:

Tymczasowe

Dane znikają po wykonaniu.

Trwałe

Dane zapisują się w bazie.

Przykład:

MESSAGE

↓

DATABASE

↓

QUEUE RECOVERY
13. QUEUE DATABASE MODEL

Przykład:

{
"queue_id":"",
"message_id":"",
"status":"",
"priority":"",
"created":"",
"processed":""
}
14. QUEUE MONITORING

System obserwuje:

długość kolejki,
czas oczekiwania,
błędy,
wydajność.

Przykład:

PROGRAMMER_QUEUE

WAITING:

25

PROCESSING:

3

FAILED:

1
15. QUEUE SECURITY

Kontrola:

kto może wysłać,
kto może odebrać,
kto może usunąć.

Przykład:

MEMORY_AGENT

CAN READ:

MEMORY_QUEUE

CAN WRITE:

MEMORY_QUEUE
Przykładowy przepływ

Budowa modułu:

DIRECTOR_CORE

↓

COMMAND MESSAGE

↓

MESSAGE ROUTER

↓

PROGRAMMER_QUEUE


PROGRAMMER_AGENT

↓

TAKES MESSAGE


EXECUTION


RESPONSE

↓

DIRECTOR_QUEUE
Przykładowa struktura kolejki
{
"queue":
{
"name":"PROGRAMMER_QUEUE",

"messages":
[
{
"id":"MSG001",
"priority":"HIGH",
"status":"WAITING"
}
]
}
}
Obsługa awarii
Agent offline
MESSAGE

↓

QUEUE

↓

WAIT

↓

AGENT ONLINE

↓

EXECUTION
Restart systemu
SYSTEM STOP

↓

SAVE QUEUES

↓

SYSTEM START

↓

RESTORE QUEUES
Integracja z innymi dokumentami

10_MESSAGE_QUEUE_SYSTEM.md łączy się z:

03_MESSAGE_OBJECT_MODEL.md

↓

06_MESSAGE_HEADER_SPECIFICATION.md

↓

09_MESSAGE_ROUTING_SYSTEM.md

↓

11_MESSAGE_DELIVERY_SYSTEM.md

↓

12_MESSAGE_EVENT_SYSTEM.md

↓

18_MESSAGE_ERROR_HANDLING.md

↓

DATABASE_MESSAGE_STORAGE.md

↓

MONITORING_SYSTEM.md
Cel końcowy

10_MESSAGE_QUEUE_SYSTEM.md definiuje mechanizm niezawodnego przechowywania i zarządzania komunikacją SSI_SELF_DEVELOPMENT_ENGINE.

Po wdrożeniu:

żadna ważna wiadomość nie zostanie utracona,
agenci mogą pracować niezależnie,
system może obsługiwać tysiące zadań,
komunikacja jest odporna na awarie,
historia przepływu pozostaje dostępna.

Jest to pamięć robocza systemu komunikacji SSI — miejsce, gdzie zadania i informacje czekają, aż odpowiedni element AI będzie gotowy je przetworzyć.