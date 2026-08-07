Opis:

Ten dokument definiuje model kontekstu komunikatu (Message Context Model) w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie jakie informacje otaczające wiadomość muszą być przechowywane i przekazywane razem z komunikatem, aby agent lub moduł SSI mógł poprawnie zrozumieć znaczenie otrzymanych danych, podjąć właściwą decyzję oraz zachować ciągłość działania systemu.

Jeżeli:

06_MESSAGE_HEADER_SPECIFICATION.md odpowiada za dane techniczne komunikatu,
07_MESSAGE_PAYLOAD_SPECIFICATION.md odpowiada za właściwe dane i polecenia,
08_MESSAGE_CONTEXT_MODEL.md odpowiada za otoczenie informacyjne, w którym ta wiadomość istnieje,

to:

08_MESSAGE_CONTEXT_MODEL.md definiuje pamięć sytuacyjną komunikatu — czyli wszystko, co AI musi wiedzieć, aby właściwie zinterpretować wiadomość.

Cel dokumentu

Dokument odpowiada na pytania:

Dlaczego dana wiadomość została wysłana?
W jakim projekcie działa?
Z jakim zadaniem jest związana?
Jakie wcześniejsze działania miały miejsce?
Jakie decyzje doprowadziły do tego komunikatu?
Jak agent ma interpretować otrzymane dane?
Jak zachować ciągłość procesu AI?
Rola dokumentu

Dokument jest podstawą dla:

Agent Reasoning System,
Memory System,
Task Management System,
Knowledge System,
Message Processing Engine,
Decision Engine.
Główna zasada Context Model

Sama wiadomość nie zawsze wystarcza.

Przykład:

Bez kontekstu:

CREATE MODULE

AI nie wie:

jaki moduł,
dla jakiego projektu,
dlaczego,
według jakiej architektury.

Z kontekstem:

PROJECT:
SSI_SELF_DEVELOPMENT_ENGINE

TASK:
BUILD MESSAGE SYSTEM

GOAL:
CREATE ROUTER MODULE

AI rozumie sytuację.

Miejsce Context w komunikacie
MESSAGE

│
├── HEADER
│
├── ROUTING
│
├── CONTEXT  ← sytuacja
│
├── PAYLOAD  ← dane
│
├── SECURITY
│
└── STATUS
Struktura Context Object

Podstawowy model:

{
"context":
{
"project":"",
"task":"",
"session":"",
"agent_state":"",
"conversation":"",
"history":"",
"knowledge":"",
"memory_reference":""
}
}
Warstwy kontekstu
CONTEXT

│
├── PROJECT CONTEXT
│
├── TASK CONTEXT
│
├── AGENT CONTEXT
│
├── SESSION CONTEXT
│
├── MEMORY CONTEXT
│
├── KNOWLEDGE CONTEXT
│
└── TEMPORAL CONTEXT
1. PROJECT CONTEXT
Kontekst projektu

Określa środowisko działania.

Zawiera:

nazwę projektu,
wersję,
etap budowy,
moduł.

Przykład:

{
"project":
{
"name":"SSI_SELF_DEVELOPMENT_ENGINE",
"version":"V1",
"phase":"MESSAGE_SYSTEM"
}
}
2. TASK CONTEXT
Kontekst zadania

Łączy wiadomość z konkretnym procesem.

Zawiera:

ID zadania,
cel,
status.

Przykład:

{
"task":
{
"id":"TASK-1001",
"name":"CREATE_MESSAGE_ROUTER",
"status":"RUNNING"
}
}
3. AGENT CONTEXT
Stan agenta

Informuje:

kto wykonuje,
jaki posiada stan,
jakie ma możliwości.

Przykład:

{
"agent":
{
"id":"PROGRAMMER_AGENT",
"state":"WORKING"
}
}
4. SESSION CONTEXT
Kontekst sesji

Określa aktualną sesję pracy.

Zawiera:

session ID,
rozpoczęcie,
historię interakcji.

Przykład:

{
"session_id":"SESSION-001"
}
5. CONVERSATION CONTEXT
Historia komunikacji

Łączy wiadomości.

Przykład:

MESSAGE 001

↓

MESSAGE 002

↓

MESSAGE 003

Pozwala AI zachować ciągłość.

6. MEMORY CONTEXT
Powiązanie z pamięcią

Wskazuje informacje z pamięci systemowej.

Przykład:

{
"memory_reference":
[
"MEMORY-001",
"MEMORY-002"
]
}
7. KNOWLEDGE CONTEXT
Powiązanie z wiedzą

Informuje, jakie zasoby wiedzy wykorzystać.

Przykład:

{
"knowledge_reference":
{
"domain":"MESSAGE_ARCHITECTURE"
}
}
8. TEMPORAL CONTEXT
Kontekst czasu

Pozwala rozumieć kolejność zdarzeń.

Zawiera:

czas utworzenia,
poprzednie zdarzenia,
deadline.
9. ENVIRONMENT CONTEXT
Środowisko wykonania

Opisuje warunki.

Przykład:

{
"environment":
{
"runtime":"PYTHON",
"system":"WINDOWS"
}
}
10. DECISION CONTEXT
Kontekst decyzji

Bardzo ważny dla autonomicznego AI.

Przechowuje:

dlaczego podjęto decyzję,
jakie były alternatywy,
jakie kryteria zastosowano.

Przykład:

{
"decision_reason":
"Selected architecture A because of scalability"
}
Pełny przykład Context Object
{
"context":
{

"project":
{
"name":"SSI_SELF_DEVELOPMENT_ENGINE",
"phase":"MESSAGE_SYSTEM"
},

"task":
{
"id":"TASK-001",
"name":"CREATE_MESSAGE_ROUTER"
},

"agent":
{
"id":"PROGRAMMER_AGENT",
"state":"EXECUTING"
},

"memory_reference":
[
"MEMORY-100"
],

"knowledge_reference":
[
"MESSAGE_ARCHITECTURE"
],

"session":
"SESSION-01"

}
}
Context podczas komunikacji agentów

Przykład:

Bez Context:
DIRECTOR:

Zbuduj router

Agent:

?
Z Context:
PROJECT:
SSI ENGINE

TASK:
MESSAGE SYSTEM

GOAL:
CREATE ROUTING MODULE

RULES:
USE MESSAGE ARCHITECTURE V1

Agent:

Rozumiem zadanie.
Context i pamięć AI

Context umożliwia:

odtwarzanie sytuacji,
uczenie się,
analizowanie decyzji.

Proces:

MESSAGE

↓

CONTEXT

↓

MEMORY

↓

KNOWLEDGE
Context Compression

Dla dużych projektów:

Nie przechowuje się całej historii.

System używa:

FULL HISTORY

↓

SUMMARY

↓

REFERENCE

Przykład:

{
"context_summary":"Previous API design completed"
}
Context Validation

System sprawdza:

PROJECT EXISTS

TASK EXISTS

AGENT VALID

MEMORY AVAILABLE

KNOWLEDGE AVAILABLE
Context Security

Nie każdy agent widzi cały kontekst.

Poziomy:

PUBLIC

PROJECT

AGENT

SYSTEM

ROOT
Context Evolution

Model może się rozwijać:

CONTEXT V1

↓

CONTEXT V2

↓

CONTEXT INTELLIGENT

Dodawane mogą być:

emocjonalny stan agenta,
doświadczenie,
reputacja,
historia decyzji.
Integracja z innymi dokumentami

08_MESSAGE_CONTEXT_MODEL.md łączy się z:

03_MESSAGE_OBJECT_MODEL.md

↓

07_MESSAGE_PAYLOAD_SPECIFICATION.md

↓

13_MESSAGE_REQUEST_RESPONSE_MODEL.md

↓

16_MESSAGE_MEMORY_INTEGRATION.md

↓

17_MESSAGE_KNOWLEDGE_INTEGRATION.md

↓

20_AGENT_CONTEXT_SYSTEM.md

↓

30_MESSAGE_EVOLUTION_PLAN.md
Cel końcowy

08_MESSAGE_CONTEXT_MODEL.md definiuje świadomość sytuacyjną komunikacji SSI_SELF_DEVELOPMENT_ENGINE.

Po wdrożeniu:

agenci nie otrzymują tylko danych,
rozumieją sytuację,
pamiętają historię,
mogą podejmować lepsze decyzje,
komunikacja staje się inteligentna.

Jest to warstwa pamięci krótkoterminowej komunikacji SSI — mechanizm, który sprawia, że wiadomość ma znaczenie, a nie jest tylko zbiorem danych.