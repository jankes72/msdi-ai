Opis:

Ten dokument definiuje szczegółową specyfikację API systemu zdarzeń (Event System API) w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie, w jaki sposób system wykrywa, tworzy, przesyła, obsługuje oraz reaguje na zdarzenia zachodzące wewnątrz całego ekosystemu SSI.

System zdarzeń jest mechanizmem, który pozwala modułom i agentom reagować na zmiany bez konieczności ciągłego sprawdzania stanu innych komponentów.

Jeżeli:

09_COMMUNICATION_API_SPECIFICATION.md opisuje przesyłanie komunikatów,
03_INTERNAL_API_DESIGN.md opisuje komunikację pomiędzy modułami,
12_COMMUNICATION_SYSTEM_SPECIFICATION.md opisuje mechanizm komunikacji,

to:

11_EVENT_SYSTEM_API_SPECIFICATION.md definiuje system reakcji na zmiany zachodzące w SSI.

Cel dokumentu

11_EVENT_SYSTEM_API_SPECIFICATION.md odpowiada na pytania:

Co jest zdarzeniem w SSI?
Jak moduł tworzy nowe zdarzenie?
Jak inne moduły otrzymują informację o zmianie?
Jak agenci reagują automatycznie?
Jak przechowywana jest historia zdarzeń?
Jak obsługiwane są błędne lub niepełne zdarzenia?
Jak budować autonomiczne reakcje systemu?
Rola dokumentu

Dokument jest podstawą dla:

Event Manager,
Message System,
Agent Coordination System,
Workflow Engine,
Automation Layer,
Self Development Loop.

Hierarchia:

SYSTEM ACTION

↓

EVENT API

↓

EVENT MANAGER

↓

EVENT ROUTER

↓

SUBSCRIBERS

↓

REACTION
Główna zasada Event System API

System nie musi stale pytać:

"Czy coś się zmieniło?"

Zamiast tego otrzymuje informację:

"Coś się wydarzyło."

Nie:

DIRECTOR_CORE

↓

CHECK EVERY MODULE

Tylko:

MODULE

↓

EVENT CREATED

↓

EVENT SYSTEM

↓

INTERESTED MODULES
Architektura Event System API
                 SSI CORE

                    |

             EVENT SYSTEM API

                    |

--------------------------------

|              |               |

EVENT        EVENT           EVENT

MANAGER      BUS             HANDLER

                    |

--------------------------------

AGENTS     MODULES     SERVICES
Typy zdarzeń w SSI
1. SYSTEM EVENTS
Zdarzenia systemowe

Dotyczą działania całego SSI.

Przykłady:

SYSTEM_STARTED

SYSTEM_STOPPED

SYSTEM_ERROR

SYSTEM_UPDATE
2. AGENT EVENTS
Zdarzenia agentów

Przykłady:

AGENT_CREATED

AGENT_READY

AGENT_BUSY

AGENT_COMPLETED

AGENT_FAILED
3. TASK EVENTS
Zdarzenia zadań

Przykłady:

TASK_CREATED

TASK_ASSIGNED

TASK_STARTED

TASK_COMPLETED

TASK_FAILED
4. MEMORY EVENTS
Zdarzenia pamięci

Przykłady:

MEMORY_CREATED

MEMORY_UPDATED

MEMORY_VALIDATED
5. KNOWLEDGE EVENTS
Zdarzenia wiedzy

Przykłady:

KNOWLEDGE_ADDED

KNOWLEDGE_UPDATED

KNOWLEDGE_CONFLICT
6. PROJECT EVENTS
Zdarzenia projektu

Przykłady:

MODULE_CREATED

BUILD_STARTED

VERSION_RELEASED
Model zdarzenia SSI

Każde zdarzenie posiada:

{
"event_id":"",
"type":"",
"source":"",
"target":"",
"payload":"",
"context":"",
"priority":"",
"timestamp":"",
"status":""
}
EVENT CREATION API
Tworzenie zdarzeń

Operacja:

CREATE_EVENT()

Przykład:

TASK_MANAGER

↓

CREATE_EVENT

TASK_COMPLETED
EVENT PUBLISH API
Publikowanie zdarzeń

Wysyła zdarzenie do systemu.

Operacja:

PUBLISH_EVENT()

Schemat:

EVENT

↓

EVENT BUS

↓

SUBSCRIBERS
EVENT SUBSCRIPTION API
Subskrypcja zdarzeń

Moduł może powiedzieć:

"Powiadom mnie, gdy wydarzy się X."

Operacje:

SUBSCRIBE_EVENT()

UNSUBSCRIBE_EVENT()

LIST_SUBSCRIPTIONS()
Przykład:
MEMORY_MANAGER

SUBSCRIBE:

KNOWLEDGE_CREATED

Po utworzeniu wiedzy:

KNOWLEDGE_CREATED

↓

MEMORY_MANAGER NOTIFIED
EVENT ROUTING API
Kierowanie zdarzeń

Odpowiada za:

znalezienie odbiorców,
przekazanie zdarzenia,
kontrolę priorytetu.

Schemat:

EVENT

↓

ROUTER

↓

HANDLER
EVENT HANDLER API
Obsługa reakcji

Każde zdarzenie może wywołać akcję.

Przykład:

TASK_COMPLETED

↓

VALIDATION_AGENT

↓

CHECK RESULT
EVENT FILTER API
Filtrowanie zdarzeń

Pozwala reagować tylko na ważne informacje.

Przykład:

IF:

priority = HIGH

THEN:

execute handler
EVENT PRIORITY SYSTEM

Poziomy:

CRITICAL

HIGH

NORMAL

LOW
EVENT QUEUE API
Kolejka zdarzeń

Obsługuje:

oczekujące wydarzenia,
kolejność,
retry.

Operacje:

QUEUE_EVENT()

GET_NEXT_EVENT()

REMOVE_EVENT()
EVENT HISTORY API
Historia zdarzeń

Przechowuje:

wszystkie wydarzenia,
reakcje,
skutki.

Operacje:

GET_EVENT_HISTORY()

SEARCH_EVENTS()
EVENT STATE API

Status zdarzenia:

CREATED

↓

PUBLISHED

↓

RECEIVED

↓

PROCESSED

↓

ARCHIVED
EVENT ERROR HANDLING API

Obsługa problemów:

brak odbiorcy,
nieudana reakcja,
konflikt.

Proces:

ERROR

↓

RETRY

↓

ALTERNATIVE_HANDLER

↓

REPORT
EVENT SECURITY API

Chroni system przed:

fałszywymi zdarzeniami,
nieautoryzowanymi akcjami.

Proces:

EVENT

↓

VALIDATION

↓

AUTHORIZATION

↓

PROCESS
EVENT MEMORY INTEGRATION

Każde ważne zdarzenie może zostać zapamiętane.

Schemat:

EVENT HISTORY

↓

ANALYSIS

↓

MEMORY

↓

KNOWLEDGE
EVENT AUTOMATION API

Pozwala tworzyć automatyczne reakcje.

Przykład:

IF:

BUILD_COMPLETED


THEN:

RUN_TESTS
Przykład pełnego przepływu

Budowa modułu zakończona:

PROGRAMMER_AGENT

↓

CREATE_EVENT()

MODULE_COMPLETED

↓

EVENT SYSTEM API

↓

VALIDATION_AGENT

↓

TESTING_SYSTEM

↓

MEMORY_UPDATE
Integracja z innymi dokumentami

11_EVENT_SYSTEM_API_SPECIFICATION.md współpracuje z:

09_COMMUNICATION_API_SPECIFICATION.md

↓

12_COMMUNICATION_SYSTEM_SPECIFICATION.md

↓

17_AGENT_COORDINATION_SYSTEM_SPECIFICATION.md

↓

18_EXECUTION_ENGINE_SPECIFICATION.md

↓

28_SELF_IMPROVEMENT_LOOP_SPECIFICATION.md

↓

30_SYSTEM_INTEGRATION_SPECIFICATION.md
Cel końcowy

11_EVENT_SYSTEM_API_SPECIFICATION.md definiuje mechanizm reakcji i synchronizacji całego SSI_SELF_DEVELOPMENT_ENGINE.

Dzięki niemu system może:

reagować automatycznie,
synchronizować moduły,
uruchamiać procesy po zdarzeniach,
budować autonomiczne workflow,
analizować historię działania.

Dokument jest systemem nerwowym reakcji autonomicznego środowiska AI, który pozwala SSI działać dynamicznie zamiast tylko wykonywać polecenia.