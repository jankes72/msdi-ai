Opis:

Ten dokument definiuje szczegółową specyfikację API systemu komunikacji (Communication API) w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie, w jaki sposób wszystkie elementy SSI wymieniają informacje: agenci, moduły, silniki systemowe oraz zewnętrzne komponenty. Dokument definiuje standard przesyłania wiadomości, obsługę komunikacji, routing, priorytety, historię oraz kontrolę poprawności przekazywanych danych.

Jeżeli:

08_COMMUNICATION_DATA_MODEL.md opisuje strukturę danych komunikacji,
12_COMMUNICATION_SYSTEM_SPECIFICATION.md opisuje działanie systemu komunikacji,
03_INTERNAL_API_DESIGN.md opisuje wewnętrzną komunikację modułów,

to:

09_COMMUNICATION_API_SPECIFICATION.md definiuje oficjalny interfejs, przez który cały SSI przesyła i odbiera informacje.

Cel dokumentu

09_COMMUNICATION_API_SPECIFICATION.md odpowiada na pytania:

Jak agent wysyła wiadomość do innego agenta?
Jak moduły wymieniają informacje?
Jak system kieruje komunikaty do właściwego odbiorcy?
Jak wygląda standard wiadomości?
Jak obsługiwane są błędy komunikacji?
Jak przechowywana jest historia wymiany informacji?
Jak zapewnić niezawodną komunikację całego systemu?
Rola dokumentu

Dokument jest podstawą dla:

Agent Communication System,
Message Manager,
Event System,
Agent Coordination System,
Internal API Bus,
Director Core.

Hierarchia:

SSI CORE

↓

COMMUNICATION API

↓

MESSAGE SYSTEM

↓

ROUTER

↓

AGENTS / MODULES / SERVICES
Główna zasada Communication API

Komunikacja w SSI nie polega na bezpośrednim wywoływaniu funkcji.

Każda informacja jest przekazywana jako kontrolowany komunikat.

Nie:

AGENT A

↓

AGENT B FUNCTION()

Tylko:

AGENT A

↓

COMMUNICATION API

↓

MESSAGE ROUTER

↓

AGENT B
Architektura Communication API
                  SSI CORE

                     |

              COMMUNICATION API

                     |

-----------------------------------

|              |                  |

MESSAGE      EVENT             ROUTING

MANAGER      SYSTEM            ENGINE

                     |

-----------------------------------

AGENTS     MODULES     SERVICES
Typy komunikacji
1. AGENT TO AGENT API
Komunikacja pomiędzy agentami

Umożliwia:

wymianę informacji,
przekazywanie wyników,
konsultacje,
współpracę.

Operacje:

SEND_AGENT_MESSAGE()

RECEIVE_MESSAGE()

REPLY_MESSAGE()

Przykład:

ARCHITECT_AGENT

↓

SEND_MESSAGE()

↓

PROGRAMMER_AGENT
2. MODULE TO MODULE API
Komunikacja modułów

Pozwala:

przekazywać dane,
uruchamiać procesy,
informować o stanie.

Przykład:

TASK_MANAGER

↓

COMMUNICATION API

↓

MEMORY_MANAGER
3. SYSTEM EVENT API
Komunikacja zdarzeniowa

System reaguje na wydarzenia.

Przykłady:

TASK_COMPLETED

AGENT_CREATED

MEMORY_UPDATED

BUILD_FINISHED

Przepływ:

EVENT

↓

EVENT BUS

↓

SUBSCRIBED MODULES
4. BROADCAST API
Komunikacja grupowa

Pozwala wysłać informację do wielu odbiorców.

Operacja:

BROADCAST_MESSAGE()

Przykład:

DIRECTOR_CORE

↓

ALL_AGENTS

"New system rule added"
5. DIRECT MESSAGE API
Wiadomość prywatna

Komunikacja jeden-do-jednego.

Operacje:

SEND_MESSAGE()

GET_MESSAGE()

ACKNOWLEDGE_MESSAGE()
Model wiadomości SSI

Każda wiadomość posiada:

{
"message_id":"",
"sender":"",
"receiver":"",
"type":"",
"priority":"",
"payload":"",
"context":"",
"timestamp":"",
"validation":""
}
MESSAGE TYPE SYSTEM

Rodzaje wiadomości:

COMMAND

Polecenie wykonania.

Przykład:

RUN_TASK
REQUEST

Zapytanie o dane.

Przykład:

GET_MEMORY_CONTEXT
RESPONSE

Odpowiedź.

Przykład:

TASK_RESULT
EVENT

Informacja o zmianie.

Przykład:

AGENT_READY
NOTIFICATION

Powiadomienie.

Przykład:

SYSTEM_UPDATE_AVAILABLE
MESSAGE ROUTING API
System kierowania wiadomości

Odpowiada za:

znalezienie odbiorcy,
wybór kanału,
priorytet.

Schemat:

MESSAGE

↓

ROUTER

↓

TARGET
MESSAGE PRIORITY SYSTEM

Poziomy:

CRITICAL

HIGH

NORMAL

LOW

Przykład:

Błąd systemu:

CRITICAL

Informacja:

LOW
MESSAGE QUEUE API
Kolejkowanie wiadomości

Obsługuje:

oczekujące wiadomości,
kolejność,
retry.

Operacje:

ADD_MESSAGE()

GET_NEXT_MESSAGE()

REMOVE_MESSAGE()
MESSAGE STATUS API

Każda wiadomość posiada stan:

CREATED

↓

SENT

↓

DELIVERED

↓

READ

↓

PROCESSED
COMMUNICATION CONTEXT API

Każdy komunikat może zawierać:

projekt,
zadanie,
agenta,
pamięć.

Schemat:

MESSAGE

+

PROJECT CONTEXT

+

TASK CONTEXT

+

AGENT CONTEXT
COMMUNICATION SECURITY API

Kontroluje:

nadawcę,
odbiorcę,
uprawnienia,
integralność danych.

Proces:

MESSAGE

↓

AUTH CHECK

↓

VALIDATION

↓

DELIVERY
COMMUNICATION ERROR API

Obsługa problemów:

brak odbiorcy,
timeout,
błędny format,
odrzucona wiadomość.

Schemat:

ERROR

↓

ANALYSIS

↓

RETRY

↓

FAILURE REPORT
COMMUNICATION LOGGING API

Zapisuje:

historię wiadomości,
czas przesłania,
błędy,
reakcje.
COMMUNICATION MEMORY INTEGRATION

Ważne dla samorozwoju.

System może zapisywać:

skuteczne strategie komunikacji,
historię współpracy agentów,
problemy komunikacyjne.

Schemat:

MESSAGE HISTORY

↓

ANALYSIS

↓

MEMORY UPDATE

↓

KNOWLEDGE
COMMUNICATION VERSIONING API

Obsługuje zmiany protokołów:

MESSAGE_PROTOCOL_V1

↓

MESSAGE_PROTOCOL_V2
Przykład pełnego przepływu

Agent programista kończy zadanie:

PROGRAMMER_AGENT

↓

SEND_MESSAGE()

↓

COMMUNICATION API

↓

DIRECTOR_CORE

↓

TASK_COMPLETED EVENT

↓

MEMORY UPDATE

↓

KNOWLEDGE EXTRACTION
Integracja z innymi dokumentami

09_COMMUNICATION_API_SPECIFICATION.md współpracuje z:

08_COMMUNICATION_DATA_MODEL.md

↓

12_COMMUNICATION_SYSTEM_SPECIFICATION.md

↓

11_EVENT_SYSTEM_API_SPECIFICATION.md

↓

12_MESSAGE_PROTOCOL_SPECIFICATION.md

↓

04_AGENT_API_SPECIFICATION.md

↓

17_AGENT_COORDINATION_SYSTEM_SPECIFICATION.md

↓

30_SYSTEM_INTEGRATION_SPECIFICATION.md
Cel końcowy

09_COMMUNICATION_API_SPECIFICATION.md definiuje system nerwowy SSI_SELF_DEVELOPMENT_ENGINE.

Dzięki niemu system może:

komunikować agentów,
przekazywać zadania,
synchronizować moduły,
reagować na zdarzenia,
budować współpracę wielu autonomicznych komponentów.

Dokument jest oficjalnym protokołem komunikacji całego ekosystemu AI.