Opis:

Ten dokument definiuje szczegółową specyfikację nagłówka komunikatu (Message Header Specification) w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie jakie informacje techniczne i sterujące znajdują się w nagłówku każdej wiadomości, jak system identyfikuje komunikat, kto go wysłał, dokąd ma trafić, jaki ma priorytet oraz jak powinien być przetwarzany przez infrastrukturę komunikacyjną SSI.

Jeżeli:

03_MESSAGE_OBJECT_MODEL.md opisuje cały obiekt wiadomości,
04_MESSAGE_FORMAT_SPECIFICATION.md opisuje pełny format komunikatu,
05_MESSAGE_TYPE_SYSTEM.md opisuje rodzaje wiadomości,

to:

06_MESSAGE_HEADER_SPECIFICATION.md definiuje "kopertę" komunikatu — część, która pozwala systemowi prawidłowo rozpoznać, przesłać i obsłużyć wiadomość zanim zostanie odczytana jej właściwa zawartość.

Cel dokumentu

Dokument odpowiada na pytania:

Jak wygląda nagłówek komunikatu?
Jak system identyfikuje wiadomość?
Jak rozpoznać nadawcę i odbiorcę?
Jak określić ważność komunikatu?
Jak kontrolować wersje komunikacji?
Jak router podejmuje decyzję o przesłaniu wiadomości?
Jak monitorować przepływ komunikatów?
Rola dokumentu

Dokument jest podstawą dla:

Message Builder,
Message Router,
Message Queue Manager,
Message Validator,
Logging System,
Security System.
Główna zasada nagłówka

Payload mówi:

"Co zawiera wiadomość?"

Header mówi:

"Czym jest wiadomość i jak system ma ją obsłużyć?"

Przykład:

HEADER

↓

kto wysłał?

do kogo?

kiedy?

jak ważne?

jaką wersją?

jaką drogą?
Struktura nagłówka

Ogólny model:

{
"header":
{
"message_id":"",
"message_type":"",
"version":"",
"sender":"",
"receiver":"",
"timestamp":"",
"priority":"",
"routing_key":"",
"correlation_id":"",
"security_level":""
}
}
Architektura Header
MESSAGE

│
├── HEADER
│
│   ├── IDENTITY
│   ├── SOURCE
│   ├── DESTINATION
│   ├── TIMING
│   ├── PRIORITY
│   ├── ROUTING
│   ├── VERSION
│   └── SECURITY
│
└── PAYLOAD
1. MESSAGE_ID
Unikalny identyfikator wiadomości

Każda wiadomość posiada własne ID.

Przykład:

MSG-2026-000001

Cel:

śledzenie,
logowanie,
debugowanie,
audyt.
2. MESSAGE_TYPE
Typ komunikatu

Określa kategorię wiadomości.

Przykład:

{
"message_type":"COMMAND"
}

Wykorzystywane przez:

router,
handler,
validator.
3. MESSAGE_VERSION
Wersja formatu

Określa wersję protokołu.

Przykład:

{
"version":"1.0"
}

Cel:

kompatybilność,
migracje,
rozwój systemu.
4. SENDER
Nadawca wiadomości

Określa źródło komunikatu.

Może być:

agent,
moduł,
system.

Przykłady:

DIRECTOR_CORE

PROGRAMMER_AGENT

MEMORY_MANAGER
5. RECEIVER
Odbiorca wiadomości

Określa cel.

Może być:

pojedynczy agent,
moduł,
grupa.

Przykład:

VALIDATION_AGENT
6. TIMESTAMP
Znacznik czasu

Określa moment utworzenia.

Przykład:

2026-08-06T12:00:00

Wykorzystanie:

kolejność zdarzeń,
analiza historii,
synchronizacja.
7. PRIORITY
Priorytet wiadomości

Określa kolejność obsługi.

Poziomy:

CRITICAL

HIGH

NORMAL

LOW

BACKGROUND

Przykłady:

Błąd bezpieczeństwa:

CRITICAL

Analiza danych:

BACKGROUND
8. ROUTING_KEY
Klucz routingu

Pomaga routerowi znaleźć drogę.

Przykład:

{
"routing_key":"TASK.PROCESS.CREATE"
}

Router:

ROUTING_KEY

↓

DESTINATION
9. CORRELATION_ID
Powiązanie komunikatów

Łączy wiadomości należące do jednej operacji.

Przykład:

REQUEST

CORRELATION_ID:

TASK-1001


RESPONSE

CORRELATION_ID:

TASK-1001

Dzięki temu system wie:

"ta odpowiedź dotyczy tego zapytania".

10. PARENT_MESSAGE_ID
Powiązanie z poprzednią wiadomością

Przykład:

MESSAGE A

↓

MESSAGE B

(parent=A)

Pozwala tworzyć historię komunikacji.

11. DELIVERY_MODE
Sposób dostarczenia

Możliwe tryby:

DIRECT

QUEUE

BROADCAST

EVENT_STREAM
12. SECURITY_LEVEL
Poziom bezpieczeństwa

Przykład:

PUBLIC

INTERNAL

SYSTEM

CRITICAL

Określa wymagany poziom ochrony.

13. AUTHORIZATION_DATA
Dane autoryzacyjne

Może zawierać:

token,
podpis,
uprawnienia.
14. TRACE_INFORMATION
Dane śledzenia

Umożliwia analizę przepływu.

Przykład:

TRACE:

DIRECTOR

↓

ROUTER

↓

AGENT

↓

RESULT
Pełny przykład Header
{
"header":
{
"message_id":"MSG-000001",

"message_type":"COMMAND",

"version":"1.0",

"sender":"DIRECTOR_CORE",

"receiver":"PROGRAMMER_AGENT",

"timestamp":"2026-08-06T12:00:00",

"priority":"HIGH",

"routing_key":"BUILD.MODULE",

"correlation_id":"TASK-1001",

"security_level":"SYSTEM"
}
}
Proces obsługi Header

Przed dostarczeniem:

MESSAGE RECEIVED

↓

READ HEADER

↓

CHECK TYPE

↓

CHECK SOURCE

↓

CHECK DESTINATION

↓

CHECK SECURITY

↓

ROUTE MESSAGE
Header a Message Router

Router wykorzystuje:

receiver,
routing_key,
priority,
delivery_mode.

Przykład:

HEADER

↓

ROUTER

↓

QUEUE

↓

AGENT
Header a Security System

Security sprawdza:

kto wysłał,
czy może wysłać,
czy odbiorca może odebrać.
Header a Logging System

Nagłówek pozwala zapisać:

czas,
źródło,
cel,
typ,
status.
Header a Memory System

Można analizować:

kto podejmował decyzje,
kiedy,
jak często,
w jakim kontekście.
Walidacja Header

System sprawdza:

MESSAGE_ID EXISTS

TYPE VALID

SENDER REGISTERED

RECEIVER AVAILABLE

VERSION SUPPORTED

SECURITY ACCEPTED
Błędy Header

Przykłady:

Brak odbiorcy
INVALID_RECEIVER
Nieobsługiwana wersja
UNSUPPORTED_VERSION
Brak uprawnień
AUTHORIZATION_FAILED
Integracja z innymi dokumentami

06_MESSAGE_HEADER_SPECIFICATION.md łączy się z:

03_MESSAGE_OBJECT_MODEL.md

↓

04_MESSAGE_FORMAT_SPECIFICATION.md

↓

05_MESSAGE_TYPE_SYSTEM.md

↓

09_MESSAGE_ROUTING_SYSTEM.md

↓

10_MESSAGE_QUEUE_SYSTEM.md

↓

19_MESSAGE_SECURITY_MODEL.md

↓

22_MESSAGE_VERSIONING_SYSTEM.md

↓

24_MESSAGE_LOGGING_SYSTEM.md
Cel końcowy

06_MESSAGE_HEADER_SPECIFICATION.md definiuje system identyfikacji i sterowania komunikacją SSI_SELF_DEVELOPMENT_ENGINE.

Po wdrożeniu:

każda wiadomość jest rozpoznawalna,
router wie gdzie ją wysłać,
system wie jak ją obsłużyć,
bezpieczeństwo może ją zweryfikować,
historia komunikacji może być odtworzona.

Jest to adres i metadane każdego komunikatu — warstwa, dzięki której SSI wie kto mówi, do kogo mówi, kiedy mówi i jak ważna jest dana informacja.