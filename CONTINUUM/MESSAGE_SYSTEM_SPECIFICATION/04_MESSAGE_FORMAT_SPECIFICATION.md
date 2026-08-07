Opis:

Ten dokument definiuje szczegółowy standard technicznego formatu komunikatów (Message Format Specification) w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie dokładnego sposobu zapisu, struktury oraz wymagań dotyczących każdej wiadomości przesyłanej pomiędzy agentami, modułami i usługami SSI.

Jeżeli:

03_MESSAGE_OBJECT_MODEL.md definiuje z czego składa się komunikat jako obiekt logiczny,
05_MESSAGE_TYPE_SYSTEM.md definiuje jakie rodzaje komunikatów istnieją,
06_MESSAGE_HEADER_SPECIFICATION.md definiuje nagłówek wiadomości,

to:

04_MESSAGE_FORMAT_SPECIFICATION.md definiuje konkretny standard zapisu komunikatu, który każdy element SSI musi rozumieć.

Cel dokumentu

Dokument odpowiada na pytania:

Jak wygląda prawidłowy komunikat SSI?
Jakie pola są obowiązkowe?
Jakie dane są opcjonalne?
Jak agent odczytuje wiadomość?
Jak system waliduje poprawność formatu?
Jak komunikaty są zapisywane i przesyłane?
Rola dokumentu

Dokument jest podstawą dla:

Message Builder,
Message Parser,
Message Validator,
Message Router,
API Communication Layer,
Agent Communication System.
Główna zasada formatu

Każdy komunikat SSI musi posiadać jednolity standard.

Nie:

dowolny tekst

Tylko:

STANDARD MESSAGE OBJECT

+

DEFINED STRUCTURE

+

VALIDATION RULES
Podstawowa struktura komunikatu

Standardowy komunikat:

{
 "message_id":"",
 "message_type":"",
 "version":"",
 "header":{},
 "routing":{},
 "context":{},
 "payload":{},
 "security":{},
 "status":"",
 "metadata":{}
}
Warstwy komunikatu

Komunikat składa się z:

MESSAGE

│
├── IDENTITY
│
├── HEADER
│
├── ROUTING
│
├── CONTEXT
│
├── PAYLOAD
│
├── SECURITY
│
├── STATUS
│
└── METADATA
1. MESSAGE IDENTITY
Identyfikacja wiadomości

Każdy komunikat posiada unikalny numer.

Przykład:

{
"message_id":"MSG-000001"
}

Służy do:

śledzenia,
logowania,
powiązań.
2. MESSAGE TYPE

Określa rodzaj komunikacji.

Przykład:

{
"message_type":"TASK_REQUEST"
}

Dopuszczalne typy:

COMMAND

REQUEST

RESPONSE

EVENT

NOTIFICATION

ERROR
3. MESSAGE VERSION

Każdy format posiada wersję.

Przykład:

{
"version":"1.0"
}

Cel:

kompatybilność,
migracje,
rozwój systemu.
4. HEADER FORMAT

Nagłówek techniczny.

Przykład:

{
"header":
{
"sender":"DIRECTOR_CORE",
"receiver":"PROGRAMMER_AGENT",
"timestamp":"",
"priority":"HIGH"
}
}

Zawiera:

nadawcę,
odbiorcę,
czas,
priorytet.
5. ROUTING FORMAT

Informacje dla systemu komunikacji.

Przykład:

{
"routing":
{
"destination":"PROGRAMMER_AGENT",
"delivery_mode":"QUEUE"
}
}

Określa:

gdzie wysłać,
jak dostarczyć,
jaki kanał użyć.
6. CONTEXT FORMAT

Kontekst AI.

Przykład:

{
"context":
{
"project":"SSI",
"task":"BUILD_API",
"session":"001"
}
}

Pozwala agentowi rozumieć:

sytuację,
cel,
powiązania.
7. PAYLOAD FORMAT

Główna zawartość.

Przykład:

{
"payload":
{
"action":"CREATE_FILE",
"parameters":
{
"name":"router.py"
}
}
}

Payload może zawierać:

polecenia,
dane,
wyniki,
konfiguracje.
8. SECURITY FORMAT

Informacje bezpieczeństwa.

Przykład:

{
"security":
{
"level":"SYSTEM",
"authorization":"VALID"
}
}
9. STATUS FORMAT

Stan wiadomości.

Przykład:

{
"status":"PROCESSING"
}

Możliwe wartości:

CREATED

VALIDATED

QUEUED

SENT

RECEIVED

PROCESSING

COMPLETED

FAILED
10. METADATA FORMAT

Dodatkowe informacje.

Przykład:

{
"metadata":
{
"tags":[
"BUILD",
"AI"
]
}
}
Pełny przykład komunikatu SSI
{
 "message_id":"MSG-10001",

 "message_type":"COMMAND",

 "version":"1.0",

 "header":
 {
  "sender":"DIRECTOR_CORE",
  "receiver":"PROGRAMMER_AGENT",
  "priority":"HIGH",
  "timestamp":"2026-08-06"
 },

 "routing":
 {
  "delivery_mode":"QUEUE"
 },

 "context":
 {
  "project":"SSI_SELF_DEVELOPMENT_ENGINE",
  "task":"CREATE_MESSAGE_ROUTER"
 },

 "payload":
 {
  "action":"CREATE_MODULE",
  "module":"message_router.py"
 },

 "security":
 {
  "level":"SYSTEM"
 },

 "status":"CREATED"
}
Reguły obowiązkowe

Każdy komunikat musi posiadać:

Wymagane pola
message_id

message_type

version

sender

receiver

timestamp

payload

status
Pola opcjonalne
metadata

attachments

references

history

analytics
Walidacja formatu

Przed wysłaniem:

MESSAGE CREATED

↓

FORMAT CHECK

↓

SCHEMA VALIDATION

↓

SECURITY CHECK

↓

SEND
Obsługa błędnego formatu

Jeżeli komunikat jest niepoprawny:

INVALID MESSAGE

↓

ERROR MESSAGE

↓

LOG

↓

REJECT
Format odpowiedzi

Każdy REQUEST musi posiadać RESPONSE.

Schemat:

REQUEST

↓

PROCESSING

↓

RESPONSE

Przykład:

REQUEST:

{
"action":"GET_MEMORY"
}

Response:

{
"status":"SUCCESS",
"data":{}
}
Format EVENT

Zdarzenia posiadają:

{
"type":"EVENT",
"name":"TASK_COMPLETED",
"data":{}
}
Format ERROR

Błędy posiadają:

{
"type":"ERROR",
"code":"",
"message":"",
"source":""
}
Kompatybilność

Format musi umożliwiać:

starsze wersje,
nowe pola,
migrację.

Przykład:

MESSAGE V1

↓

PARSER

↓

MESSAGE V2
Integracja z innymi systemami
API System
API REQUEST

↓

MESSAGE FORMAT

↓

MODULE
Agent System
AGENT

↓

MESSAGE

↓

AGENT
Memory System
MESSAGE

↓

STORAGE

↓

KNOWLEDGE
Zasady projektowe

Format komunikatu musi być:

Jednolity

Każdy moduł używa tego samego standardu.

Rozszerzalny

Można dodawać nowe pola.

Wersjonowany

Zmiany nie niszczą systemu.

Czytelny dla AI

Agent musi rozumieć znaczenie danych.

Możliwy do analizy

Każdy komunikat może być źródłem wiedzy.

Integracja z dokumentacją

04_MESSAGE_FORMAT_SPECIFICATION.md łączy się z:

03_MESSAGE_OBJECT_MODEL.md

↓

05_MESSAGE_TYPE_SYSTEM.md

↓

06_MESSAGE_HEADER_SPECIFICATION.md

↓

07_MESSAGE_PAYLOAD_SPECIFICATION.md

↓

18_MESSAGE_VALIDATION_RULES.md

↓

22_MESSAGE_VERSIONING_SYSTEM.md

↓

24_MESSAGE_LOGGING_SYSTEM.md
Cel końcowy

04_MESSAGE_FORMAT_SPECIFICATION.md ustanawia oficjalny język komunikacji SSI_SELF_DEVELOPMENT_ENGINE.

Po wdrożeniu:

każdy agent mówi tym samym formatem,
każdy moduł rozumie wiadomości,
komunikacja jest przewidywalna,
błędy są wykrywalne,
system może się rozwijać bez chaosu.

Jest to odpowiednik protokołu nerwowego SSI — standardu, według którego wszystkie elementy sztucznej inteligencji wymieniają informacje.