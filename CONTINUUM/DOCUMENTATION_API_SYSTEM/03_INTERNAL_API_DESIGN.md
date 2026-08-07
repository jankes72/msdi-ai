Opis:

Ten dokument definiuje szczegółowy projekt wewnętrznego API systemu SSI_SELF_DEVELOPMENT_ENGINE, czyli mechanizmu komunikacji wykorzystywanego wewnątrz samego systemu pomiędzy jego modułami, usługami i komponentami.

Jego zadaniem jest określenie, jak moduły SSI wywołują swoje funkcje, przekazują dane, wymieniają informacje o stanie oraz wykonują wspólne operacje bez bezpośredniego uzależniania się od implementacji innych komponentów.

Jeżeli:

01_API_ARCHITECTURE_OVERVIEW.md opisuje ogólną architekturę API,
02_MODULE_INTERFACE_MODEL.md opisuje standard pojedynczego modułu,

to:

03_INTERNAL_API_DESIGN.md opisuje dokładnie, jak te moduły komunikują się między sobą wewnątrz działającego systemu.

Cel dokumentu

03_INTERNAL_API_DESIGN.md odpowiada na pytania:

Jak wygląda komunikacja wewnętrzna SSI?
Jak jeden moduł wywołuje drugi?
Jak przekazywane są dane pomiędzy komponentami?
Jak wygląda struktura wywołań API?
Jak system kontroluje przepływ informacji?
Jak zachować modularność podczas rozwoju?
Rola dokumentu

Dokument jest podstawą dla:

implementacji Core System,
budowy usług wewnętrznych,
komunikacji agentów,
integracji modułów,
testów integracyjnych.

Hierarchia:

MODULE A

↓

INTERNAL API LAYER

↓

MODULE B

↓

SERVICE

↓

DATA
Główna zasada Internal API

Moduły SSI nie komunikują się bezpośrednio przez swoje wewnętrzne funkcje.

Nie:

DIRECTOR_CORE

↓

memory_manager.save()

Tylko:

DIRECTOR_CORE

↓

MEMORY_API

↓

MEMORY_SERVICE

↓

MEMORY_MANAGER
Architektura Internal API

Model:

              SSI CORE

                  |

          INTERNAL API BUS

                  |

--------------------------------

|          |          |          |

AGENT     TASK     MEMORY    PROJECT

SERVICE  SERVICE  SERVICE   SERVICE

|          |          |          |

DATABASE DATABASE DATABASE DATABASE
1. INTERNAL API BUS
Magistrala komunikacyjna

Centralny mechanizm przekazywania komunikatów.

Odpowiada za:

routing,
kolejkowanie,
przekazywanie danych,
kontrolę komunikacji.

Przykład:

REQUEST

↓

API BUS

↓

TARGET MODULE
2. SERVICE INTERFACE
Interfejs usługowy

Każdy moduł udostępnia swoje operacje jako usługę.

Przykład:

MEMORY_SERVICE


save()

search()

update()

delete()
3. REQUEST MODEL
Model żądania

Każde wywołanie posiada standardową strukturę:

REQUEST

{

request_id

source

target

action

parameters

context

timestamp

}
4. RESPONSE MODEL
Model odpowiedzi

Każda odpowiedź zawiera:

RESPONSE

{

request_id

status

result

metadata

error

}

5. INTERNAL API OPERATIONS
Typy operacji
CREATE

Tworzenie obiektu.

Przykład:

CREATE_TASK()
CREATE_AGENT()
CREATE_MEMORY()
READ

Pobieranie informacji.

Przykład:

GET_PROJECT_STATE()
GET_AGENT_STATUS()
UPDATE

Zmiana danych.

Przykład:

UPDATE_MEMORY()
UPDATE_TASK_STATUS()
DELETE

Usunięcie danych.

Operacja kontrolowana.

EXECUTE

Wykonanie działania.

Przykład:

RUN_ANALYSIS()
START_TRAINING()
6. INTERNAL EVENT SYSTEM

API obsługuje również zdarzenia.

Przykład:

TASK_COMPLETED

↓

EVENT BUS

↓

MEMORY UPDATE

↓

KNOWLEDGE ANALYSIS
7. CONTEXT PROPAGATION
Przekazywanie kontekstu

Każde wywołanie musi posiadać:

projekt,
zadanie,
agenta,
aktualny stan.

Przykład:

REQUEST

+

PROJECT_CONTEXT

+

TASK_CONTEXT

+

MEMORY_CONTEXT

8. INTERNAL API ROUTING
Routing komunikacji

System określa:

gdzie wysłać żądanie,
który moduł odpowiada,
jaki serwis wykona operację.

Schemat:

REQUEST

↓

ROUTER

↓

SERVICE

↓

MODULE
9. SERVICE DISCOVERY
Wykrywanie usług

System zna:

jakie moduły działają,
jakie API udostępniają,
jaki mają status.

Przykład:

MEMORY_SERVICE

STATUS:

ONLINE
10. INTERNAL API SECURITY
Zabezpieczenie komunikacji

Kontrola:

uprawnień,
źródła wywołania,
zakresu danych.

Proces:

CALL

↓

AUTHORIZATION

↓

VALIDATION

↓

EXECUTION
11. INTERNAL API LOGGING
Historia komunikacji

Zapisywane są:

wywołania,
odpowiedzi,
błędy,
czas wykonania.
12. ERROR HANDLING
Obsługa błędów

Standard:

REQUEST

↓

ERROR

↓

RECOVERY

↓

REPORT
13. ASYNCHRONOUS COMMUNICATION
Komunikacja asynchroniczna

Dla długich procesów:

Przykład:

START_TRAINING

↓

TASK_CREATED

↓

PROCESSING

↓

RESULT_EVENT
14. SYNCHRONOUS COMMUNICATION
Komunikacja natychmiastowa

Dla prostych operacji:

Przykład:

GET_STATUS()

↓

RETURN_STATUS()
15. INTERNAL API VERSIONING
Wersjonowanie

Każdy interfejs posiada wersję:

MEMORY_SERVICE_V1

↓

MEMORY_SERVICE_V2
Przykład przepływu wewnętrznego

Zlecenie budowy modułu:

DIRECTOR_CORE

↓

TASK_API

↓

TASK_MANAGER

↓

PROGRAMMER_AGENT

↓

CODE_MANAGER

↓

TEST_SYSTEM

↓

MEMORY_SYSTEM
Integracja z innymi dokumentami

03_INTERNAL_API_DESIGN.md współpracuje z:

02_MODULE_INTERFACE_MODEL.md

↓

04_AGENT_API_SPECIFICATION.md

↓

05_TASK_API_SPECIFICATION.md

↓

09_COMMUNICATION_API_SPECIFICATION.md

↓

11_EVENT_SYSTEM_API_SPECIFICATION.md

↓

13_REQUEST_RESPONSE_MODEL.md

↓

30_SYSTEM_INTEGRATION_SPECIFICATION.md
Cel końcowy

03_INTERNAL_API_DESIGN.md definiuje wewnętrzny układ komunikacyjny SSI_SELF_DEVELOPMENT_ENGINE.

Dzięki niemu system może:

łączyć wszystkie moduły,
wymieniać dane w kontrolowany sposób,
dodawać nowe komponenty,
izolować błędy,
rozwijać architekturę bez chaosu.

Dokument jest projektem wewnętrznej magistrali komunikacyjnej autonomicznego systemu AI.