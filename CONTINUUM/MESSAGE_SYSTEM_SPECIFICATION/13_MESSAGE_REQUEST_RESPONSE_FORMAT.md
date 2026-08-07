Opis:

Ten dokument definiuje standard komunikacji typu Request–Response (żądanie–odpowiedź) w systemie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie jak jeden moduł, agent lub komponent wysyła zapytanie do drugiego elementu systemu, jak wygląda struktura żądania, jak generowana jest odpowiedź, jak powiązać odpowiedź z konkretnym żądaniem oraz jak obsługiwać sukces, błędy i oczekiwanie na wynik.

Jeżeli:

06_MESSAGE_HEADER_SPECIFICATION.md definiuje nagłówek wiadomości,
07_MESSAGE_PAYLOAD_SPECIFICATION.md definiuje dane przesyłane w wiadomości,
08_MESSAGE_CONTEXT_MODEL.md definiuje kontekst operacji,
12_MESSAGE_STATUS_LIFECYCLE.md definiuje życie wiadomości,

to:

13_MESSAGE_REQUEST_RESPONSE_FORMAT.md definiuje dialog pomiędzy elementami SSI — jak jeden komponent pyta, a drugi odpowiada.

Cel dokumentu

Dokument odpowiada na pytania:

Jak wygląda żądanie do innego modułu?
Jak wygląda odpowiedź?
Jak system wie, do którego zapytania należy odpowiedź?
Jak przekazywane są wyniki?
Jak obsługiwane są błędy?
Jak działa komunikacja synchroniczna i asynchroniczna?
Rola dokumentu

Dokument jest podstawą dla:

Internal API,
Agent Communication System,
Task Management System,
Memory API,
Knowledge API,
Module Interface Layer.
Główna zasada Request–Response

Komunikacja składa się z dwóch wiadomości:

REQUEST

↓

PROCESSING

↓

RESPONSE

Przykład:

DIRECTOR_CORE:

"Utwórz nowego agenta"

        ↓

PROGRAMMER_AGENT:

"Wykonano, agent utworzony"
Architektura Request–Response
REQUEST FLOW


SENDER

  │

  ▼

REQUEST MESSAGE

  │

  ▼

TARGET MODULE

  │

  ▼

PROCESSING

  │

  ▼

RESPONSE MESSAGE

  │

  ▼

ORIGINAL SENDER
Struktura Request

Podstawowy model:

{
"request":
{
"request_id":"",
"operation":"",
"parameters":{},
"expected_response":"",
"timeout":""
}
}
1. REQUEST_ID
Identyfikator żądania

Każde żądanie posiada unikalny numer.

Przykład:

REQ-00001

Cel:

śledzenie,
powiązanie odpowiedzi,
debugowanie.
2. OPERATION
Operacja do wykonania

Określa działanie.

Przykłady:

CREATE_AGENT

GET_STATUS

LOAD_MEMORY

RUN_ANALYSIS

VALIDATE_CODE
3. PARAMETERS
Parametry operacji

Dane potrzebne do wykonania.

Przykład:

{
"parameters":
{
"agent_type":"PROGRAMMER",
"version":"1.0"
}
}
4. EXPECTED_RESPONSE
Oczekiwany typ odpowiedzi

Określa czego oczekuje nadawca.

Przykłady:

STATUS

RESULT

DATA

CONFIRMATION

ERROR
5. TIMEOUT
Limit czasu oczekiwania

Przykład:

{
"timeout":"30s"
}

Po przekroczeniu:

TIMEOUT_ERROR
Struktura Response

Podstawowy model:

{
"response":
{
"request_id":"",
"status":"",
"result":{},
"message":"",
"error":""
}
}
1. REQUEST_ID

Najważniejszy element.

Łączy:

REQUEST

REQ-100

↓

RESPONSE

REQ-100

System wie:

"To jest odpowiedź na to konkretne pytanie."

2. RESPONSE_STATUS

Status odpowiedzi.

Możliwe:

SUCCESS

FAILED

PARTIAL

TIMEOUT

REJECTED
3. RESULT

Wynik działania.

Przykład:

{
"result":
{
"agent_created":true,
"id":"AGENT001"
}
}
4. MESSAGE

Opis tekstowy.

Przykład:

Agent został utworzony poprawnie.
5. ERROR

Informacja o błędzie.

Przykład:

{
"error":
{
"code":"AGENT_EXISTS",
"description":"Agent already registered"
}
}
Pełny przykład Request
{
"header":
{
"type":"REQUEST",
"sender":"DIRECTOR_CORE",
"receiver":"AGENT_MANAGER"
},

"request":
{
"request_id":"REQ-001",

"operation":"CREATE_AGENT",

"parameters":
{
"type":"VALIDATION_AGENT"
},

"timeout":"60s"
}
}
Pełny przykład Response
{
"header":
{
"type":"RESPONSE",
"sender":"AGENT_MANAGER",
"receiver":"DIRECTOR_CORE"
},

"response":
{
"request_id":"REQ-001",

"status":"SUCCESS",

"result":
{
"agent_id":"VALIDATION_001"
}
}
}
Typy komunikacji Request–Response
1. SYNCHRONOUS REQUEST
Oczekiwanie na odpowiedź

Schemat:

REQUEST

↓

WAIT

↓

RESPONSE

Używane dla:

pobrania danych,
sprawdzenia statusu,
walidacji.
2. ASYNCHRONOUS REQUEST
Odpowiedź później

Schemat:

REQUEST

↓

ACCEPTED

↓

PROCESSING

↓

EVENT RESPONSE

Używane dla:

treningu modeli,
budowy modułów,
dużych analiz.
3. STREAM RESPONSE
Wielokrotne odpowiedzi

Przykład:

REQUEST

↓

PROGRESS 10%

↓

PROGRESS 50%

↓

COMPLETED

Używane dla:

długich procesów.
Request Priority

Żądania również posiadają priorytet.

Przykład:

{
"priority":"HIGH"
}
Request Context

Request może zawierać:

projekt,
zadanie,
agenta,
historię.

Przykład:

{
"context":
{
"task_id":"TASK100",
"phase":"BUILD"
}
}
Request Validation

Przed wykonaniem:

REQUEST RECEIVED

↓

CHECK FORMAT

↓

CHECK PERMISSION

↓

CHECK TARGET

↓

EXECUTE
Response Validation

System sprawdza:

REQUEST_ID EXISTS

STATUS VALID

RESULT FORMAT OK

SENDER AUTHORIZED
Obsługa błędów

Przykłady:

Brak modułu
MODULE_NOT_FOUND
Brak uprawnień
ACCESS_DENIED
Przekroczony czas
REQUEST_TIMEOUT
Niepoprawne dane
INVALID_PARAMETERS
Request Retry

Jeżeli odpowiedź nie nadejdzie:

REQUEST

↓

TIMEOUT

↓

RETRY

↓

RESPONSE
Request History

System zapisuje:

kto pytał,
o co pytał,
kiedy,
jaka była odpowiedź.

Przykład:

{
"request_history":
{
"REQ001":
{
"operation":"CREATE_AGENT",
"result":"SUCCESS"
}
}
}
AI Learning z Request–Response

SSI może analizować:

które pytania są częste,
które moduły odpowiadają wolno,
które operacje zawodzą.

Przykład:

OPERATION:

CREATE_AGENT

SUCCESS RATE:

98%
Integracja z innymi dokumentami

13_MESSAGE_REQUEST_RESPONSE_FORMAT.md łączy się z:

03_MESSAGE_OBJECT_MODEL.md

↓

04_MESSAGE_FORMAT_SPECIFICATION.md

↓

06_MESSAGE_HEADER_SPECIFICATION.md

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

14_MESSAGE_ERROR_HANDLING_SYSTEM.md

↓

API_INTERFACE_SPECIFICATION.md
Cel końcowy

13_MESSAGE_REQUEST_RESPONSE_FORMAT.md definiuje standard dialogu pomiędzy komponentami SSI_SELF_DEVELOPMENT_ENGINE.

Po wdrożeniu:

każdy moduł może zadawać pytania innym modułom,
odpowiedzi są jednoznacznie powiązane,
system może działać synchronicznie i asynchronicznie,
błędy są kontrolowane,
komunikacja jest przewidywalna i skalowalna.

Jest to język rozmowy wewnętrznej SSI — mechanizm, dzięki któremu agenci i moduły mogą współpracować jak jeden zintegrowany organizm AI.