Opis:

Ten dokument definiuje szczegółową specyfikację zawartości właściwej komunikatu (Message Payload Specification) w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie jakie dane mogą znajdować się wewnątrz wiadomości, jak są strukturyzowane, jak są interpretowane przez odbiorcę oraz jakie zasady obowiązują przy przekazywaniu informacji pomiędzy agentami, modułami i systemami SSI.

Jeżeli:

06_MESSAGE_HEADER_SPECIFICATION.md definiuje informacje sterujące komunikatem,
07_MESSAGE_PAYLOAD_SPECIFICATION.md definiuje właściwą treść komunikatu,
08_MESSAGE_CONTEXT_MODEL.md definiuje kontekst, w którym wiadomość istnieje,

to:

07_MESSAGE_PAYLOAD_SPECIFICATION.md definiuje "dane merytoryczne" komunikatu — czyli co system faktycznie przekazuje do wykonania, analizy lub zapisania.

Cel dokumentu

Dokument odpowiada na pytania:

Czym jest Payload?
Jak wygląda struktura danych komunikatu?
Jakie rodzaje danych mogą być przesyłane?
Jak agent interpretuje zawartość wiadomości?
Jak walidować poprawność danych?
Jak przekazywać wyniki działań?
Jak obsługiwać różne formaty danych?
Rola dokumentu

Dokument jest podstawą dla:

Message Builder,
Message Parser,
Agent Execution Engine,
Task System,
API Layer,
Memory System,
Knowledge System.
Główna zasada Payload

Header mówi:

"Kto, kiedy i gdzie przesyła wiadomość?"

Payload mówi:

"Co dokładnie trzeba zrobić lub jakie dane zostały przekazane?"

Przykład:

HEADER:

DIRECTOR_CORE
→
PROGRAMMER_AGENT


PAYLOAD:

CREATE FILE:
message_router.py
Miejsce Payload w komunikacie
MESSAGE

│
├── HEADER
│
├── ROUTING
│
├── CONTEXT
│
├── PAYLOAD  ← dane właściwe
│
├── SECURITY
│
└── STATUS
Podstawowa struktura Payload

Standard:

{
"payload":
{
"action":"",
"parameters":{},
"data":{},
"result":{},
"attachments":[]
}
}
Elementy Payload
1. ACTION
Akcja do wykonania

Określa główne działanie.

Przykłady:

CREATE

UPDATE

DELETE

ANALYZE

VALIDATE

EXECUTE

SEARCH

Przykład:

{
"action":"CREATE_MODULE"
}
2. PARAMETERS
Parametry działania

Dane potrzebne do wykonania operacji.

Przykład:

{
"parameters":
{
"module_name":"message_router",
"language":"python"
}
}
3. INPUT DATA
Dane wejściowe

Informacje przekazane do procesu.

Przykład:

{
"input_data":
{
"file":"config.yaml",
"version":"1.0"
}
}
4. OUTPUT DATA
Wynik działania

Dane zwracane po wykonaniu.

Przykład:

{
"output_data":
{
"status":"completed",
"file_created":true
}
}
5. COMMAND PARAMETERS

Dla komunikatów typu COMMAND.

Przykład:

{
"payload":
{
"command":"BUILD_MODULE",
"target":"MEMORY_SYSTEM"
}
}
6. REQUEST PARAMETERS

Dla zapytań.

Przykład:

{
"payload":
{
"query":"GET_AGENT_STATUS",
"agent_id":"AGENT_001"
}
}
7. RESPONSE DATA

Dla odpowiedzi.

Przykład:

{
"payload":
{
"success":true,
"result":
{
"status":"READY"
}
}
}
8. EVENT DATA

Dla zdarzeń.

Przykład:

{
"payload":
{
"event_name":"TASK_COMPLETED",
"task_id":"TASK_100"
}
}
9. ERROR DATA

Dla błędów.

Przykład:

{
"payload":
{
"error_code":"MODULE_FAILURE",
"description":"Loading failed"
}
}
Typy danych Payload

Payload może zawierać:

Dane tekstowe

Przykład:

{
"name":"SSI_ENGINE"
}
Dane liczbowe

Przykład:

{
"priority":10
}
Dane logiczne

Przykład:

{
"validated":true
}
Listy

Przykład:

{
"agents":
[
"DIRECTOR",
"PROGRAMMER"
]
}
Obiekty zagnieżdżone

Przykład:

{
"task":
{
"id":"100",
"type":"BUILD"
}
}
Payload dla Agentów

Agent otrzymuje:

MESSAGE

↓

PAYLOAD

↓

UNDERSTAND INTENT

↓

EXECUTE ACTION

Przykład:

{
"action":"WRITE_CODE",
"parameters":
{
"file":"router.py",
"language":"python"
}
}
Payload dla Task System

Przykład:

{
"task":
{
"id":"TASK-001",
"name":"Create API",
"requirements":[
"router",
"validator"
]
}
}
Payload dla Memory System

Przykład:

{
"memory":
{
"type":"EXPERIENCE",
"content":"Agent solved validation problem"
}
}
Payload dla Knowledge System

Przykład:

{
"knowledge":
{
"concept":"MESSAGE_ROUTING",
"source":"AGENT_ANALYSIS"
}
}
Walidacja Payload

Przed wykonaniem:

PAYLOAD RECEIVED

↓

SCHEMA CHECK

↓

DATA TYPE CHECK

↓

PERMISSION CHECK

↓

EXECUTION
Reguły poprawnego Payload

Payload musi być:

Jednoznaczny

Jedna akcja = jeden cel.

Samoopisowy

AI musi rozumieć znaczenie danych.

Walidowalny

Dane muszą posiadać określony format.

Rozszerzalny

Możliwość dodawania nowych pól.

Kompatybilny

Starsze moduły muszą móc obsługiwać starsze wersje.

Przykład pełnego Payload
{
"payload":
{
"action":"CREATE_AGENT",

"parameters":
{
"agent_type":"VALIDATION_AGENT",
"version":"1.0"
},

"input_data":
{
"requirements":
[
"code_review",
"testing"
]
},

"expected_result":
{
"agent_registered":true
}
}
}
Obsługa dużych danych

Dla dużych informacji Payload może zawierać referencję.

Nie:

{
"data":"500MB_CONTENT"
}

Tylko:

{
"data_reference":
{
"storage":"MEMORY_DATABASE",
"id":"DATA_001"
}
}
Attachment System

Payload może posiadać załączniki:

Przykłady:

pliki,
dokumenty,
modele,
raporty.

Struktura:

{
"attachments":
[
{
"type":"FILE",
"name":"model.py",
"location":"storage/path"
}
]
}
Payload Security

Dane mogą posiadać:

poziom dostępu,
klasyfikację,
ograniczenia.

Przykład:

{
"classification":"INTERNAL_AI_DATA"
}
Payload a Memory

System może analizować:

jakie dane były przesyłane,
jakie decyzje wykonano,
jakie wyniki uzyskano.

Proces:

PAYLOAD

↓

ANALYSIS

↓

MEMORY

↓

KNOWLEDGE
Payload Evolution

Payload musi obsługiwać rozwój:

PAYLOAD V1

↓

PAYLOAD V2

↓

PAYLOAD V3

Bez niszczenia istniejących modułów.

Integracja z innymi dokumentami

07_MESSAGE_PAYLOAD_SPECIFICATION.md łączy się z:

03_MESSAGE_OBJECT_MODEL.md

↓

04_MESSAGE_FORMAT_SPECIFICATION.md

↓

05_MESSAGE_TYPE_SYSTEM.md

↓

06_MESSAGE_HEADER_SPECIFICATION.md

↓

08_MESSAGE_CONTEXT_MODEL.md

↓

13_MESSAGE_REQUEST_RESPONSE_FORMAT.md

↓

17_MESSAGE_ERROR_FORMAT.md

↓

27_MESSAGE_KNOWLEDGE_EXTRACTION.md
Cel końcowy

07_MESSAGE_PAYLOAD_SPECIFICATION.md definiuje standard danych przesyłanych wewnątrz SSI_SELF_DEVELOPMENT_ENGINE.

Po wdrożeniu:

każdy agent otrzymuje dane w przewidywalnej formie,
moduły rozumieją przekazywane informacje,
zadania mogą być automatycznie wykonywane,
wyniki mogą być analizowane i zapisywane,
system może rozwijać swoją wiedzę na podstawie komunikacji.

Jest to zawartość informacyjna układu nerwowego SSI — miejsce, gdzie faktycznie przekazywana jest wiedza, polecenia i wyniki działania całego systemu AI.