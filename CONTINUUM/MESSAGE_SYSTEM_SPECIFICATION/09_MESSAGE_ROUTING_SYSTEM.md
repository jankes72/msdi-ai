Opis:

Ten dokument definiuje system routingu komunikatów (Message Routing System) w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie jak komunikaty przemieszczają się wewnątrz systemu SSI, jak wybierany jest odbiorca, jak działa przekazywanie wiadomości pomiędzy agentami i modułami oraz jak system kontroluje cały przepływ komunikacji.

Jeżeli:

06_MESSAGE_HEADER_SPECIFICATION.md definiuje adres komunikatu,
07_MESSAGE_PAYLOAD_SPECIFICATION.md definiuje zawartość wiadomości,
08_MESSAGE_CONTEXT_MODEL.md definiuje kontekst wiadomości,

to:

09_MESSAGE_ROUTING_SYSTEM.md definiuje mechanizm transportu komunikatów — czyli "układ nerwowy", który decyduje którędy wiadomość ma przejść i do kogo trafić.

Cel dokumentu

Dokument odpowiada na pytania:

Jak SSI znajduje odbiorcę wiadomości?
Jak agent otrzymuje komunikat?
Jak działa kolejka wiadomości?
Jak wybierana jest ścieżka komunikacji?
Jak obsługiwać wiele agentów jednocześnie?
Jak monitorować przepływ komunikatów?
Jak odzyskać wiadomość po błędzie?
Rola dokumentu

Dokument jest podstawą dla:

Message Router,
Message Queue Manager,
Agent Communication Layer,
Event System,
Task Execution Engine,
Runtime System.
Główna zasada routingu

Komunikat nie trafia bezpośrednio do odbiorcy.

Przepływ:

MESSAGE

↓

ROUTER

↓

QUEUE

↓

TARGET MODULE

↓

PROCESSING
Architektura routingu
                    SSI MESSAGE SYSTEM


             MESSAGE CREATED

                    │

                    ▼

            MESSAGE ROUTER

                    │

        ┌───────────┼───────────┐

        ▼           ▼           ▼

     AGENT       MODULE      EVENT

     QUEUE       QUEUE       STREAM

        │           │           │

        ▼           ▼           ▼

   EXECUTION    SERVICE     SUBSCRIBERS

Główne komponenty

System routingu składa się z:

MESSAGE ROUTING SYSTEM

│
├── Message Router
│
├── Routing Rules Engine
│
├── Message Queue Manager
│
├── Delivery Manager
│
├── Priority Manager
│
├── Retry Manager
│
└── Routing Monitor
1. MESSAGE ROUTER
Główny element systemu

Odpowiada za:

odebranie wiadomości,
analizę nagłówka,
wybór celu,
przekazanie dalej.

Proces:

MESSAGE

↓

READ HEADER

↓

CHECK DESTINATION

↓

SELECT ROUTE

↓

SEND
2. ROUTING RULES ENGINE
Silnik zasad routingu

Określa:

gdzie wysłać wiadomość,
jakim kanałem,
z jakim priorytetem.

Przykład:

TYPE:

TASK_REQUEST


RULE:

SEND TO TASK_MANAGER
Przykładowe reguły
COMMAND
COMMAND

↓

EXECUTION AGENT
MEMORY REQUEST
REQUEST

+

MEMORY_QUERY

↓

MEMORY_MANAGER
ERROR
ERROR

↓

ERROR_HANDLER
3. MESSAGE QUEUE SYSTEM
Kolejki wiadomości

Każdy moduł może posiadać własną kolejkę.

Przykład:

MESSAGE_QUEUE


├── DIRECTOR_QUEUE

├── PROGRAMMER_QUEUE

├── MEMORY_QUEUE

├── VALIDATOR_QUEUE

└── SYSTEM_QUEUE
Zadania kolejki:
przechowywanie wiadomości,
kolejność wykonania,
kontrola obciążenia,
ponawianie prób.
4. DELIVERY MANAGER
Zarządzanie dostarczeniem

Kontroluje:

czy wiadomość dotarła,
czy została odebrana,
czy została wykonana.

Cykl:

CREATED

↓

QUEUED

↓

SENT

↓

DELIVERED

↓

PROCESSED
5. PRIORITY ROUTING
Routing według ważności

System może zmieniać kolejność.

Przykład:

Krytyczny błąd:

CRITICAL ERROR

↓

FIRST EXECUTION

Zwykłe zadanie:

BACKGROUND TASK

↓

WAIT
6. DIRECT ROUTING
Bezpośrednia komunikacja

Schemat:

AGENT A

↓

AGENT B

Używane dla:

szybkich odpowiedzi,
prostych operacji.
7. QUEUE ROUTING
Przez kolejkę

Schemat:

AGENT A

↓

QUEUE

↓

AGENT B

Zalety:

odporność,
skalowanie,
historia.
8. BROADCAST ROUTING
Rozsyłanie

Jedna wiadomość do wielu odbiorców.

Przykład:

EVENT:

SYSTEM_UPDATE


↓

ALL AGENTS
9. EVENT ROUTING

Dla zdarzeń:

EVENT

↓

EVENT BUS

↓

SUBSCRIBERS

Przykład:

MODEL_TRAINED

↓

MODEL_MANAGER

↓

KNOWLEDGE_SYSTEM
Routing według typu wiadomości
Typ	Odbiorca
COMMAND	Agent wykonawczy
REQUEST	Moduł usługowy
RESPONSE	Nadawca żądania
EVENT	Subskrybenci
ERROR	Error Handler
SYSTEM	Core
Routing według agenta

Przykład:

PROGRAMMER_AGENT

↓

CODE_TASK_QUEUE
VALIDATION_AGENT

↓

TEST_QUEUE
MEMORY_AGENT

↓

MEMORY_QUEUE
Routing Context-Aware

SSI może wybierać trasę na podstawie kontekstu.

Przykład:

TASK:

BUILD API


PROJECT:

SSI V5


PHASE:

DEVELOPMENT

Router wybiera:

ARCHITECT_AGENT
Routing Intelligence

W przyszłości router może analizować:

historię agentów,
skuteczność,
obciążenie,
reputację.

Przykład:

AGENT A

90% SUCCESS


AGENT B

60% SUCCESS


↓

WYBIERZ AGENTA A
Retry System

Jeżeli dostarczenie nie powiedzie się:

SEND

↓

FAILED

↓

RETRY

↓

SUCCESS
Dead Letter Queue

Nieobsłużone wiadomości:

FAILED MESSAGE

↓

DEAD LETTER QUEUE

↓

ANALYSIS
Routing Security

Router sprawdza:

czy nadawca ma prawo wysłać,
czy odbiorca może odebrać,
czy wiadomość jest bezpieczna.
Routing Logging

Każda wiadomość zapisuje:

MESSAGE_ID

SOURCE

DESTINATION

TIME

ROUTE

STATUS
Przykład pełnego przepływu

Zadanie tworzenia modułu:

DIRECTOR_CORE

↓

COMMAND:
CREATE_MODULE


MESSAGE ROUTER

↓

PROGRAMMER_AGENT_QUEUE


PROGRAMMER_AGENT

↓

RESPONSE:
MODULE_CREATED


MESSAGE ROUTER

↓

VALIDATION_AGENT


VALIDATION_AGENT

↓

EVENT:
MODULE_VALIDATED
Walidacja routingu

System sprawdza:

TARGET EXISTS

ROUTE EXISTS

AGENT AVAILABLE

PERMISSION OK

QUEUE AVAILABLE
Awaria routingu

Przykłady:

Brak odbiorcy
ROUTE_NOT_FOUND
Agent offline
TARGET_UNAVAILABLE
Przekroczony czas
DELIVERY_TIMEOUT
Integracja z innymi dokumentami

09_MESSAGE_ROUTING_SYSTEM.md łączy się z:

03_MESSAGE_OBJECT_MODEL.md

↓

04_MESSAGE_FORMAT_SPECIFICATION.md

↓

06_MESSAGE_HEADER_SPECIFICATION.md

↓

10_MESSAGE_QUEUE_SYSTEM.md

↓

11_MESSAGE_DELIVERY_SYSTEM.md

↓

12_MESSAGE_EVENT_SYSTEM.md

↓

19_MESSAGE_SECURITY_MODEL.md

↓

24_MESSAGE_LOGGING_SYSTEM.md
Cel końcowy

09_MESSAGE_ROUTING_SYSTEM.md definiuje mechanizm przemieszczania informacji w SSI_SELF_DEVELOPMENT_ENGINE.

Po wdrożeniu:

każdy komunikat znajdzie właściwego odbiorcę,
system będzie obsługiwał wielu agentów,
komunikacja będzie odporna na błędy,
można będzie skalować liczbę modułów,
AI będzie mogła autonomicznie zarządzać przepływem pracy.

Jest to system nerwowy SSI — mechanizm, który nie tylko przesyła informacje, ale inteligentnie kieruje je do właściwych części całego organizmu AI.