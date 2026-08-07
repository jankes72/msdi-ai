Opis:

Ten dokument definiuje system wersjonowania wiadomości (Message Versioning System) w architekturze SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie jak system zarządza zmianami formatów komunikatów, jak zachowuje kompatybilność pomiędzy różnymi wersjami modułów, agentów i usług oraz jak umożliwia rozwój komunikacji bez zatrzymywania całego systemu.

Jeżeli:

18_MESSAGE_VALIDATION_RULES.md sprawdza czy wiadomość jest poprawna,
19_MESSAGE_SECURITY_MODEL.md chroni komunikację,
20_MESSAGE_AUTHENTICATION_SYSTEM.md potwierdza tożsamość nadawcy,
21_MESSAGE_ENCRYPTION_RULES.md chroni zawartość wiadomości,
22_MESSAGE_VERSIONING_SYSTEM.md odpowiada za ewolucję standardu komunikacji,

to:

22_MESSAGE_VERSIONING_SYSTEM.md jest mechanizmem rozwoju protokołu SSI — pozwala systemowi zmieniać się i ulepszać bez utraty kompatybilności pomiędzy jego elementami.

Cel dokumentu

Dokument definiuje:

sposób numerowania wersji wiadomości,
zasady zmian protokołu,
kompatybilność pomiędzy wersjami,
migrację starych formatów,
obsługę przestarzałych wiadomości,
kontrolę zmian komunikacji.
Rola dokumentu

Dokument jest podstawą dla:

Message Protocol System,
API Versioning,
Module Integration,
Agent Communication Layer,
Migration System,
Backward Compatibility System.
Główna zasada Versioning

Komunikacja SSI nie jest stała.

System rozwija się.

Dlatego każda wiadomość posiada wersję:

MESSAGE

+

VERSION

+

FORMAT RULES

+

COMPATIBILITY
Dlaczego wersjonowanie jest potrzebne?

Przykład:

Wersja 1:

{
"agent":"PROGRAMMER"
}

Nowa wersja:

{
"agent":
{
"id":"001",
"role":"PROGRAMMER"
}
}

Bez wersji:

STARY MODUŁ ≠ NOWY MODUŁ

Z wersją:

VERSION 1 → VERSION 2

system wie jak obsłużyć zmianę.

Architektura Versioning
MESSAGE

↓

VERSION DETECTOR

↓

COMPATIBILITY CHECK

↓

MIGRATION ENGINE

↓

PROCESS MESSAGE
Główne komponenty
MESSAGE VERSIONING SYSTEM

│
├── Version Registry
│
├── Version Validator
│
├── Compatibility Manager
│
├── Migration Engine
│
├── Deprecation Manager
│
├── Schema History
│
└── Version Audit Log
1. MESSAGE VERSION HEADER

Każda wiadomość posiada wersję.

Przykład:

{
"message_version":"1.0"
}
Pełny przykład:
{
"header":
{
"type":"COMMAND",
"version":"2.1"
}
}
2. VERSION NUMBERING MODEL

SSI używa schematu:

MAJOR.MINOR.PATCH

Przykład:

2.5.3
MAJOR VERSION

Duża zmiana.

Przykład:

1.x.x

↓

2.x.x

Oznacza:

zmiana struktury,
brak pełnej kompatybilności.
MINOR VERSION

Dodanie funkcji.

Przykład:

2.1

↓

2.2

Oznacza:

nowe pola,
nowe możliwości,
kompatybilność zachowana.
PATCH VERSION

Poprawka.

Przykład:

2.2.1

↓

2.2.2

Oznacza:

poprawki błędów,
brak zmian struktury.
3. VERSION REGISTRY

Centralna baza wersji.

Przechowuje:

dostępne wersje,
obsługiwane formaty,
status.

Przykład:

{
"message_type":"COMMAND",

"versions":
[
"1.0",
"1.1",
"2.0"
]
}
4. COMPATIBILITY MODEL

System sprawdza:

czy odbiorca rozumie wiadomość.

Schemat:

MESSAGE VERSION

↓

TARGET VERSION

↓

COMPARE

↓

ALLOW / MIGRATE / REJECT
Typy kompatybilności
FULL COMPATIBILITY

Pełna obsługa.

Przykład:

MESSAGE 2.1

TARGET 2.1
BACKWARD COMPATIBILITY

Nowy system rozumie stare wiadomości.

Przykład:

SYSTEM 2.0

obsługuje

MESSAGE 1.0
FORWARD COMPATIBILITY

Stary system częściowo rozumie nowe wiadomości.

NO COMPATIBILITY

Wymagana migracja.

5. VERSION MIGRATION SYSTEM

Jeżeli wersja jest stara:

OLD MESSAGE

↓

MIGRATION ENGINE

↓

NEW FORMAT

Przykład:

Stara wiadomość:

{
"agent":"001"
}

Po migracji:

{
"agent_id":"001"
}
6. MESSAGE SCHEMA HISTORY

System przechowuje historię zmian.

Przykład:

MESSAGE COMMAND

v1.0

↓

v1.5

↓

v2.0
7. DEPRECATED VERSION SYSTEM

Stare wersje mogą zostać wycofane.

Przykład:

VERSION 1.0

STATUS:

DEPRECATED
Status wersji
ACTIVE

SUPPORTED

DEPRECATED

DISABLED

REMOVED
8. VERSION VALIDATION

Przed przetworzeniem:

MESSAGE

↓

READ VERSION

↓

CHECK SUPPORT

↓

MIGRATE OR PROCESS
9. VERSION CONFLICT HANDLING

Przykład:

Agent wymaga:

VERSION 3.0

System posiada:

VERSION 2.0

Rezultat:

VERSION_CONFLICT
10. VERSION ERROR TYPES

Przykłady:

UNSUPPORTED_VERSION

INVALID_VERSION_FORMAT

MIGRATION_FAILED

VERSION_CONFLICT
11. VERSION UPDATE PROCESS

Proces aktualizacji:

NEW VERSION CREATED

↓

TESTING

↓

VALIDATION

↓

DEPLOYMENT

↓

OLD VERSION SUPPORT
12. VERSION TESTING

Każda nowa wersja jest testowana:

schema test,
compatibility test,
migration test,
security test.
13. VERSION SECURITY

Zmiana wersji nie może:

ominąć zabezpieczeń,
zmienić uprawnień,
usunąć kontroli.
14. VERSION WITH AGENTS

Każdy agent posiada:

{
"supported_messages":
[
"COMMAND v1",
"COMMAND v2"
]
}
Przykład:

Agent:

PROGRAMMER_AGENT

SUPPORT:

MESSAGE COMMAND 2.x
15. VERSION LEARNING

SSI może analizować:

które wersje są używane,
które są problematyczne,
kiedy migrować.
Przykład pełnej wiadomości
{
"header":
{
"type":"COMMAND",

"message_version":"2.1"
},

"compatibility":
{
"minimum_receiver_version":"2.0"
},

"payload":
{
"action":"CREATE_AGENT"
}
}
Integracja z innymi dokumentami

22_MESSAGE_VERSIONING_SYSTEM.md łączy się z:

04_MESSAGE_FORMAT_SPECIFICATION.md

↓

06_MESSAGE_HEADER_SPECIFICATION.md

↓

07_MESSAGE_PAYLOAD_SPECIFICATION.md

↓

18_MESSAGE_VALIDATION_RULES.md

↓

19_MESSAGE_SECURITY_MODEL.md

↓

21_MESSAGE_ENCRYPTION_RULES.md

↓

23_MESSAGE_PROTOCOL_EVOLUTION.md

↓

API_VERSIONING_SYSTEM.md

↓

SYSTEM_MIGRATION_PLAN.md
Cel końcowy

22_MESSAGE_VERSIONING_SYSTEM.md definiuje mechanizm ewolucji komunikacji SSI_SELF_DEVELOPMENT_ENGINE.

Po wdrożeniu:

system może rozwijać protokół,
stare moduły mogą nadal działać,
zmiany są kontrolowane,
migracje są bezpieczne,
komunikacja pozostaje stabilna.

Jest to mechanizm DNA komunikacji SSI — pozwala systemowi zmieniać swoją strukturę, uczyć się nowych sposobów komunikacji i rozwijać się bez utraty ciągłości działania.