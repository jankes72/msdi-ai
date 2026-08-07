Opis:

Ten dokument definiuje szczegółowy protokół wymiany wiadomości (Message Protocol) używany w systemie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie dokładnego formatu, zasad przesyłania, interpretacji, walidacji i obsługi komunikatów wymienianych pomiędzy agentami AI, modułami systemowymi oraz usługami wewnętrznymi SSI.

Jeżeli:

09_COMMUNICATION_API_SPECIFICATION.md opisuje interfejs komunikacji,
11_EVENT_SYSTEM_API_SPECIFICATION.md opisuje system zdarzeń,
03_INTERNAL_API_DESIGN.md opisuje wewnętrzną komunikację modułów,

to:

12_MESSAGE_PROTOCOL_SPECIFICATION.md definiuje dokładny "język", którym wszystkie elementy SSI porozumiewają się między sobą.

Cel dokumentu

12_MESSAGE_PROTOCOL_SPECIFICATION.md odpowiada na pytania:

Jak wygląda pojedyncza wiadomość SSI?
Jak agent rozumie komunikat od innego agenta?
Jak system rozróżnia polecenie, zapytanie i odpowiedź?
Jak sprawdzana jest poprawność wiadomości?
Jak zapewnić kompatybilność komunikacji w przyszłości?
Jak wersjonować protokół wiadomości?
Rola dokumentu

Dokument jest podstawą dla:

Communication System,
Message Manager,
Agent Communication Layer,
Event System,
API Gateway,
Internal Communication Bus.

Hierarchia:

MESSAGE SOURCE

↓

MESSAGE PROTOCOL

↓

COMMUNICATION SYSTEM

↓

MESSAGE ROUTER

↓

MESSAGE RECEIVER
Główna zasada Message Protocol

W SSI każda informacja przesyłana pomiędzy komponentami musi posiadać standardową strukturę.

Nie:

"Zrób zadanie"

Tylko:

MESSAGE OBJECT

{

WHO

TO WHOM

WHAT

WHY

CONTEXT

DATA

RESULT

}
Architektura protokołu wiadomości
                 SSI SYSTEM

                     |

              MESSAGE PROTOCOL

                     |

----------------------------------

|              |                 |

HEADER       PAYLOAD          METADATA

                     |

              MESSAGE HANDLER

Struktura wiadomości SSI

Każdy komunikat posiada:

{
"message_id":"",
"message_type":"",
"version":"",
"sender":"",
"receiver":"",
"timestamp":"",
"priority":"",
"context":"",
"payload":"",
"security":"",
"status":""
}
1. MESSAGE HEADER
Nagłówek wiadomości

Zawiera podstawowe informacje:

identyfikator,
typ,
wersję,
nadawcę,
odbiorcę.

Przykład:

MESSAGE_ID:

MSG-001


TYPE:

TASK_REQUEST
2. MESSAGE ID SYSTEM
Identyfikacja wiadomości

Każda wiadomość posiada unikalny identyfikator.

Przykład:

MSG-2026-00001

Pozwala:

śledzić komunikację,
wykrywać duplikaty,
analizować historię.
3. MESSAGE TYPE SYSTEM
Typy komunikatów
COMMAND

Polecenie wykonania.

Przykład:

START_AGENT
REQUEST

Prośba o wykonanie operacji.

Przykład:

GET_MEMORY
RESPONSE

Odpowiedź.

Przykład:

MEMORY_RESULT
EVENT

Informacja o zmianie.

Przykład:

TASK_COMPLETED
NOTIFICATION

Powiadomienie.

Przykład:

SYSTEM_UPDATE
4. MESSAGE PAYLOAD
Dane wiadomości

Zawiera właściwą treść.

Przykład:

{
"task_id":"TASK-001",
"action":"BUILD_MODULE"
}
5. MESSAGE CONTEXT
Kontekst wiadomości

Każda wiadomość może zawierać:

projekt,
zadanie,
agenta,
pamięć.

Przykład:

PROJECT:

SSI_ENGINE


TASK:

API_IMPLEMENTATION
6. MESSAGE ROUTING INFORMATION
Informacje dla routera

Określają:

gdzie wysłać wiadomość,
jaką drogą,
jaki priorytet.
7. MESSAGE PRIORITY MODEL

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
8. MESSAGE STATUS MODEL

Cykl życia wiadomości:

CREATED

↓

VALIDATED

↓

SENT

↓

DELIVERED

↓

PROCESSED

↓

ARCHIVED
9. MESSAGE VALIDATION SYSTEM

Każda wiadomość przechodzi kontrolę:

MESSAGE

↓

FORMAT CHECK

↓

SOURCE CHECK

↓

SECURITY CHECK

↓

DELIVERY
10. MESSAGE ACKNOWLEDGEMENT SYSTEM

Potwierdzenie odbioru.

Typy:

RECEIVED

PROCESSING

COMPLETED

FAILED
11. MESSAGE RESPONSE PROTOCOL

Każde żądanie może posiadać odpowiedź.

Schemat:

REQUEST

↓

PROCESSING

↓

RESPONSE

Przykład:

GET_AGENT_STATUS

↓

AGENT_STATUS_RESPONSE
12. MESSAGE ERROR PROTOCOL

Obsługa błędów:

Przykład:

{
"status":"ERROR",
"error_code":"AGENT_NOT_AVAILABLE",
"message":"Target offline"
}
13. MESSAGE RETRY SYSTEM

Obsługa ponownego wysłania.

Proces:

SEND

↓

FAIL

↓

RETRY

↓

SUCCESS / ERROR
14. MESSAGE PRIORITY QUEUE

Wiadomości są wykonywane według ważności.

Przykład:

CRITICAL ERROR

↓

NORMAL TASK

↓

LOW NOTIFICATION
15. MESSAGE SECURITY MODEL

Chroni:

autentyczność,
integralność,
poufność.

Proces:

MESSAGE

↓

AUTHENTICATION

↓

VALIDATION

↓

EXECUTION
16. MESSAGE VERSIONING

Protokół posiada wersje:

MESSAGE_PROTOCOL_V1

↓

MESSAGE_PROTOCOL_V2

Pozwala:

rozwijać system,
zachować kompatybilność.
17. MESSAGE LOGGING SYSTEM

Każda wiadomość może być zapisana:

kto wysłał,
kiedy,
do kogo,
jaki był rezultat.
18. MESSAGE MEMORY INTEGRATION

Ważne komunikaty mogą zostać zapamiętane.

Przykład:

MESSAGE HISTORY

↓

ANALYSIS

↓

MEMORY

↓

KNOWLEDGE
Przykład komunikacji agentów

Architekt analizuje projekt:

ARCHITECT_AGENT

↓

MESSAGE_PROTOCOL

TYPE:

TASK_REQUEST


↓

PROGRAMMER_AGENT

↓

MESSAGE RESPONSE

TYPE:

TASK_ACCEPTED
Przykład pełnego przepływu
DIRECTOR_CORE

↓

CREATE MESSAGE

↓

MESSAGE PROTOCOL

↓

COMMUNICATION API

↓

MESSAGE ROUTER

↓

AGENT

↓

RESPONSE MESSAGE

↓

MEMORY UPDATE
Integracja z innymi dokumentami

12_MESSAGE_PROTOCOL_SPECIFICATION.md współpracuje z:

09_COMMUNICATION_API_SPECIFICATION.md

↓

11_EVENT_SYSTEM_API_SPECIFICATION.md

↓

04_AGENT_API_SPECIFICATION.md

↓

05_TASK_API_SPECIFICATION.md

↓

13_REQUEST_RESPONSE_MODEL.md

↓

14_API_SECURITY_SPECIFICATION.md

↓

17_API_TESTING_SPECIFICATION.md
Cel końcowy

12_MESSAGE_PROTOCOL_SPECIFICATION.md definiuje wspólny język komunikacji całego SSI_SELF_DEVELOPMENT_ENGINE.

Dzięki niemu system może:

wymieniać informacje pomiędzy agentami,
kontrolować przepływ danych,
zapewnić kompatybilność modułów,
analizować historię komunikacji,
rozwijać własną architekturę bez chaosu.

Dokument jest standardem komunikacji wszystkich autonomicznych elementów AI w SSI.