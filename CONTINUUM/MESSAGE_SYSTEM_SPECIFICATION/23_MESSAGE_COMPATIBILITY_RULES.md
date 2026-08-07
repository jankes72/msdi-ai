Opis:

Ten dokument definiuje zasady kompatybilności wiadomości (Message Compatibility Rules) w systemie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie w jaki sposób różne wersje modułów, agentów, modeli i usług mogą ze sobą współpracować, jak system rozpoznaje zgodność komunikatów oraz jak obsługuje różnice pomiędzy starszymi i nowszymi elementami architektury.

Jeżeli:

18_MESSAGE_VALIDATION_RULES.md sprawdza czy wiadomość jest poprawna,
20_MESSAGE_AUTHENTICATION_SYSTEM.md sprawdza kto wysłał wiadomość,
21_MESSAGE_ENCRYPTION_RULES.md chroni dane wiadomości,
22_MESSAGE_VERSIONING_SYSTEM.md definiuje wersje protokołu,
23_MESSAGE_COMPATIBILITY_RULES.md definiuje czy różne elementy SSI mogą się ze sobą porozumieć,

to:

23_MESSAGE_COMPATIBILITY_RULES.md jest warstwą współpracy SSI — mechanizmem, który pozwala różnym generacjom modułów i agentów działać razem bez konfliktów.

Cel dokumentu

Dokument definiuje:

zasady zgodności wiadomości,
kompatybilność wersji,
kompatybilność agentów,
kompatybilność modułów,
reguły migracji danych,
zachowanie przy niezgodnościach.
Rola dokumentu

Dokument jest podstawą dla:

Message Versioning System,
API Integration Layer,
Module Communication Layer,
Agent Coordination System,
Migration Engine,
System Evolution Engine.
Główna zasada kompatybilności

SSI musi działać jako rozwijający się organizm.

Nowy komponent nie może automatycznie niszczyć starego.

Schemat:

STARY MODUŁ

+

NOWY MODUŁ

↓

COMPATIBILITY CHECK

↓

COMMUNICATION
Dlaczego kompatybilność jest potrzebna?

Przykład:

SSI V1:

{
"agent":"PROGRAMMER"
}

SSI V2:

{
"agent_id":"PROGRAMMER",
"role":"CODER"
}

Bez kompatybilności:

V1 ❌ V2

Z systemem kompatybilności:

V1

↓

ADAPTER

↓

V2
Architektura Compatibility System
MESSAGE

↓

VERSION CHECK

↓

SCHEMA CHECK

↓

COMPATIBILITY ENGINE

↓

ADAPTER / ACCEPT / REJECT
Główne komponenty
MESSAGE COMPATIBILITY SYSTEM

│
├── Compatibility Engine
│
├── Version Matcher
│
├── Schema Comparator
│
├── Adapter Layer
│
├── Migration Handler
│
├── Capability Registry
│
└── Compatibility Logger
1. COMPATIBILITY ENGINE

Centralny moduł decyzyjny.

Odpowiada:

"Czy odbiorca rozumie tę wiadomość?"

Przykład:

MESSAGE:

COMMAND v2.0


TARGET:

AGENT v2.1


RESULT:

COMPATIBLE
2. VERSION COMPATIBILITY

Sprawdzanie wersji.

Przykład:

MESSAGE VERSION:

2.0


RECEIVER VERSION:

2.5

Wynik:

SUPPORTED
3. COMPATIBILITY MATRIX

System posiada mapę zgodności.

Przykład:

Wiadomość	Odbiorca	Status
v1.0	v1.0	OK
v1.0	v2.0	OK
v2.0	v1.0	MIGRATE
v3.0	v1.0	BLOCK
4. BACKWARD COMPATIBILITY

Nowy system obsługuje stare wiadomości.

Przykład:

NEW AGENT

↓

READ OLD MESSAGE

Przykład:

SSI V5 może obsłużyć:

MESSAGE v3
MESSAGE v4
MESSAGE v5
5. FORWARD COMPATIBILITY

Starszy system może częściowo obsłużyć nowe wiadomości.

Przykład:

Nowe pole:

{
"agent":"001",
"new_feature":true
}

Stary system:

IGNORE UNKNOWN FIELD
6. STRICT COMPATIBILITY

Niektóre komunikaty wymagają pełnej zgodności.

Przykłady:

bezpieczeństwo,
baza danych,
krytyczne komendy.

Przykład:

DELETE_DATABASE

↓

ONLY EXACT VERSION
7. FLEXIBLE COMPATIBILITY

Niektóre wiadomości mogą być elastyczne.

Przykłady:

status,
informacje,
raporty.
8. MESSAGE CAPABILITY MODEL

Każdy komponent deklaruje możliwości.

Przykład:

{
"agent":"MODEL_AGENT",

"supports":
[
"COMMAND_v1",
"COMMAND_v2",
"EVENT_v3"
]
}
9. FEATURE NEGOTIATION

Moduły mogą uzgadniać możliwości.

Przykład:

AGENT A:

OBSŁUGUJĘ MESSAGE v2


AGENT B:

JA TEŻ


RESULT:

USE v2
10. SCHEMA COMPATIBILITY

Porównanie struktur danych.

Sprawdzane:

pola wymagane,
typy danych,
format,
zależności.

Przykład:

Stara struktura:

{
"id":"001"
}

Nowa:

{
"id":"001",
"name":"agent"
}

Kompatybilne:

YES
11. BREAKING CHANGES

Niektóre zmiany niszczą kompatybilność.

Przykłady:

Zmiana:

agent_id

↓

agent_identifier

lub:

Usunięcie pola:

permission_level
12. COMPATIBILITY LEVELS

Poziomy:

FULL

PARTIAL

ADAPTER_REQUIRED

INCOMPATIBLE
FULL

Bez zmian.

MESSAGE

↓

PROCESS
PARTIAL

Część danych obsługiwana.

ADAPTER_REQUIRED

Potrzebna transformacja.

INCOMPATIBLE

Odrzucenie.

13. ADAPTER SYSTEM

Adapter tłumaczy formaty.

Schemat:

MESSAGE v1

↓

ADAPTER

↓

MESSAGE v2

Przykład:

V1:

{
"agent":"001"
}


↓

V2:

{
"agent_id":"001"
}
14. COMPATIBILITY FAILURE

Typy błędów:

VERSION_CONFLICT

SCHEMA_MISMATCH

UNSUPPORTED_FEATURE

MIGRATION_FAILED

INCOMPATIBLE_TARGET
15. COMPATIBILITY ERROR FLOW
MESSAGE

↓

CHECK

↓

FAIL

↓

COMPATIBILITY_ERROR

↓

MIGRATION

lub

REJECT
16. COMPATIBILITY TESTING

Każda zmiana musi przejść:

test starej wersji,
test nowej wersji,
test migracji,
test integracji.
17. COMPATIBILITY WITH AGENTS

Agent posiada deklarację:

{
"name":"PROGRAMMER_AGENT",

"message_support":
[
"COMMAND_1.0",
"COMMAND_2.0"
]
}
18. COMPATIBILITY WITH MODELS

Modele AI również posiadają wersje.

Przykład:

MODEL:

QWEN2.5-CODER


SUPPORT:

MODEL_MESSAGE v2
19. AUTOMATIC COMPATIBILITY HANDLING

SSI może sam zdecydować:

MESSAGE v1

↓

DETECT OLD FORMAT

↓

RUN ADAPTER

↓

PROCESS
20. COMPATIBILITY LEARNING

System analizuje:

najczęstsze konflikty,
potrzebne adaptery,
problemy migracji.

Przykład:

80%

MESSAGE v1


↓

AUTO MIGRATION SUCCESS
Przykład pełnej wiadomości
{
"header":
{
"type":"COMMAND",
"version":"2.0"
},

"compatibility":
{
"minimum_receiver_version":"1.5",

"migration_allowed":true
},

"command":
{
"action":"CREATE_AGENT"
}
}
Integracja z innymi dokumentami

23_MESSAGE_COMPATIBILITY_RULES.md łączy się z:

22_MESSAGE_VERSIONING_SYSTEM.md

↓

18_MESSAGE_VALIDATION_RULES.md

↓

09_MESSAGE_ROUTING_SYSTEM.md

↓

15_MESSAGE_COMMAND_FORMAT.md

↓

16_MESSAGE_NOTIFICATION_FORMAT.md

↓

17_MESSAGE_ERROR_FORMAT.md

↓

24_MESSAGE_MIGRATION_SYSTEM.md

↓

API_COMPATIBILITY_SYSTEM.md

↓

SYSTEM_EVOLUTION_ENGINE.md
Cel końcowy

23_MESSAGE_COMPATIBILITY_RULES.md definiuje mechanizm współistnienia różnych generacji SSI.

Po wdrożeniu:

nowe moduły mogą współpracować ze starymi,
aktualizacje nie niszczą systemu,
wiadomości są automatycznie tłumaczone,
konflikty są wykrywane,
rozwój SSI jest ciągły.

Jest to mechanizm ewolucyjny komunikacji SSI — pozwala systemowi rosnąć, zmieniać architekturę i ulepszać własne moduły bez utraty stabilności całego organizmu AI.