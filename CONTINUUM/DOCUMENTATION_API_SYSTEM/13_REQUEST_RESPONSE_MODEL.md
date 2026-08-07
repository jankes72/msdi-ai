Opis:

Ten dokument definiuje standardowy model wymiany informacji typu Request → Response używany w całym systemie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie, jak moduły, agenci i usługi tworzą żądania, jak system je przetwarza oraz jak generowane są odpowiedzi w sposób jednolity, przewidywalny i możliwy do kontroli.

Jeżeli:

12_MESSAGE_PROTOCOL_SPECIFICATION.md opisuje format wiadomości,
03_INTERNAL_API_DESIGN.md opisuje komunikację wewnętrzną,
04_AGENT_API_SPECIFICATION.md, 05_TASK_API_SPECIFICATION.md, 06_MEMORY_API_SPECIFICATION.md opisują konkretne API,

to:

13_REQUEST_RESPONSE_MODEL.md definiuje podstawowy mechanizm rozmowy pomiędzy wszystkimi komponentami SSI: "kto pyta, o co pyta, kto odpowiada i w jaki sposób".

Cel dokumentu

13_REQUEST_RESPONSE_MODEL.md odpowiada na pytania:

Jak wygląda każde żądanie w SSI?
Jak system identyfikuje operację?
Jak przekazywany jest kontekst?
Jak wygląda poprawna odpowiedź?
Jak obsługiwane są błędne odpowiedzi?
Jak śledzić pełną historię wykonania?
Jak zapewnić kompatybilność wszystkich API?
Rola dokumentu

Dokument jest podstawą dla:

wszystkich API SSI,
Communication System,
Agent System,
Task System,
Memory System,
Database System,
Event System.

Hierarchia:

MODULE / AGENT

↓

REQUEST

↓

API LAYER

↓

SERVICE

↓

PROCESSING

↓

RESPONSE
Główna zasada Request/Response

Każda operacja w SSI odbywa się poprzez standardowy cykl:

REQUEST

↓

VALIDATION

↓

PROCESSING

↓

RESULT

↓

RESPONSE

System nigdy nie przekazuje "luźnych" danych.

Każda akcja musi posiadać:

identyfikator,
źródło,
cel,
operację,
kontekst,
dane.
Architektura Request/Response
                 SSI COMPONENT

                       |

                 REQUEST MODEL

                       |

                 API PROCESSOR

                       |

              SERVICE EXECUTION

                       |

                 RESPONSE MODEL

                       |

                 REQUESTER
REQUEST MODEL
Model żądania

Każde wywołanie posiada standardową strukturę:

{
"request_id":"",
"request_type":"",
"source":"",
"target":"",
"action":"",
"context":"",
"parameters":"",
"timestamp":"",
"priority":"",
"security_token":""
}
1. REQUEST_ID
Identyfikator żądania

Każde zapytanie otrzymuje unikalny numer.

Przykład:

REQ-2026-00001

Służy do:

śledzenia procesu,
logowania,
debugowania.
2. REQUEST_TYPE
Typ żądania

Rodzaje:

COMMAND REQUEST

Polecenie wykonania.

Przykład:

START_TRAINING
QUERY REQUEST

Zapytanie o dane.

Przykład:

GET_MEMORY_CONTEXT
CREATE REQUEST

Tworzenie obiektu.

Przykład:

CREATE_TASK
UPDATE REQUEST

Zmiana danych.

Przykład:

UPDATE_PROJECT_STATE
DELETE REQUEST

Usunięcie danych.

3. SOURCE
Źródło żądania

Określa:

kto wysłał,
jaki moduł,
jaki agent.

Przykład:

PROGRAMMER_AGENT
4. TARGET
Cel żądania

Określa odbiorcę.

Przykład:

MEMORY_SERVICE
5. ACTION
Operacja

Co ma zostać wykonane.

Przykład:

SEARCH_MEMORY
6. CONTEXT
Kontekst wykonania

Najważniejszy element dla AI.

Zawiera:

projekt,
zadanie,
agenta,
historię.

Przykład:

PROJECT:

SSI_ENGINE


TASK:

API_BUILD
7. PARAMETERS
Dane wejściowe

Przekazywane informacje.

Przykład:

{
"query":"memory API",
"limit":10
}
RESPONSE MODEL
Model odpowiedzi

Każda odpowiedź posiada:

{
"response_id":"",
"request_id":"",
"status":"",
"result":"",
"metadata":"",
"execution_time":"",
"error":"",
"timestamp":""
}
RESPONSE STATUS SYSTEM

Statusy:

SUCCESS

↓

PROCESSING

↓

WARNING

↓

ERROR

↓

FAILED
SUCCESS RESPONSE

Poprawne wykonanie.

Przykład:

{
"status":"SUCCESS",
"result":"Task completed"
}
ERROR RESPONSE

Błąd wykonania.

Przykład:

{
"status":"ERROR",
"error_code":"MODULE_UNAVAILABLE",
"message":"Memory service offline"
}
ASYNCHRONOUS REQUEST MODEL

Dla długich operacji.

Przykład:

Trening modelu:

REQUEST

↓

TASK_CREATED

↓

PROCESSING

↓

EVENT

↓

FINAL_RESPONSE
SYNCHRONOUS REQUEST MODEL

Dla szybkich operacji.

Przykład:

GET_STATUS()

↓

RETURN_STATUS()
REQUEST VALIDATION SYSTEM

Każde żądanie przechodzi:

REQUEST

↓

FORMAT CHECK

↓

AUTH CHECK

↓

PARAMETER CHECK

↓

EXECUTION
REQUEST ROUTING SYSTEM

Odpowiada za:

znalezienie odpowiedniego API,
przekazanie operacji.

Schemat:

REQUEST

↓

ROUTER

↓

SERVICE
REQUEST PRIORITY SYSTEM

Poziomy:

CRITICAL

HIGH

NORMAL

LOW

Przykład:

Awaria systemu:

CRITICAL REQUEST
REQUEST TIMEOUT MANAGEMENT

Kontrola czasu.

Proces:

START

↓

PROCESS

↓

TIME LIMIT

↓

SUCCESS / TIMEOUT
REQUEST RETRY SYSTEM

Ponowienie operacji:

REQUEST

↓

FAILED

↓

RETRY

↓

SUCCESS
REQUEST HISTORY SYSTEM

Każde żądanie może być zapisane:

kto wysłał,
kiedy,
wynik,
czas wykonania.
REQUEST SECURITY MODEL

Kontrola:

uprawnień,
źródła,
integralności.

Schemat:

REQUEST

↓

AUTHORIZATION

↓

VALIDATION

↓

EXECUTION
REQUEST MEMORY INTEGRATION

System może zapisywać:

ważne decyzje,
wyniki,
wzorce komunikacji.

Schemat:

REQUEST HISTORY

↓

ANALYSIS

↓

MEMORY

↓

KNOWLEDGE
Przykład pełnego działania

Agent pyta pamięć o rozwiązanie:

PROGRAMMER_AGENT

↓

REQUEST

GET_MEMORY_CONTEXT

↓

MEMORY_API

↓

MEMORY_ENGINE

↓

RESPONSE

↓

RESULT
Integracja z innymi dokumentami

13_REQUEST_RESPONSE_MODEL.md współpracuje z:

12_MESSAGE_PROTOCOL_SPECIFICATION.md

↓

03_INTERNAL_API_DESIGN.md

↓

04_AGENT_API_SPECIFICATION.md

↓

05_TASK_API_SPECIFICATION.md

↓

06_MEMORY_API_SPECIFICATION.md

↓

07_KNOWLEDGE_API_SPECIFICATION.md

↓

10_DATABASE_API_SPECIFICATION.md

↓

17_API_TESTING_SPECIFICATION.md
Cel końcowy

13_REQUEST_RESPONSE_MODEL.md definiuje uniwersalny język komunikacji operacyjnej całego SSI_SELF_DEVELOPMENT_ENGINE.

Dzięki niemu każdy element systemu może:

wysyłać żądania,
otrzymywać odpowiedzi,
śledzić wykonanie,
obsługiwać błędy,
zachować spójność komunikacji.

Dokument jest fundamentalnym kontraktem komunikacyjnym pomiędzy wszystkimi API autonomicznego systemu AI.