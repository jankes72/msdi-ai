Opis:

Ten dokument definiuje szczegółową specyfikację API systemu pamięci (Memory API) w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie, w jaki sposób wszystkie moduły systemu, agenci AI oraz procesy wewnętrzne uzyskują dostęp do pamięci, zapisują doświadczenia, wyszukują informacje, aktualizują wiedzę oraz wykorzystują historię działania systemu do dalszego rozwoju.

Jeżeli:

03_MEMORY_DATABASE_DESIGN.md opisuje strukturę bazy pamięci,
13_MEMORY_SYSTEM_SPECIFICATION.md opisuje mechanizm działania pamięci,
07_MEMORY_INTEGRATION_RULES.md opisuje zasady łączenia pamięci z AI,

to:

06_MEMORY_API_SPECIFICATION.md definiuje oficjalny interfejs, przez który cały system korzysta z pamięci.

Cel dokumentu

06_MEMORY_API_SPECIFICATION.md odpowiada na pytania:

Jak agent zapisuje doświadczenie?
Jak AI wyszukuje wcześniejsze informacje?
Jak system pobiera kontekst projektu?
Jak aktualizowana jest pamięć?
Jak chroniona jest pamięć przed błędnymi zapisami?
Jak moduły komunikują się z systemem pamięci?
Rola dokumentu

Dokument jest podstawą dla:

Memory Manager,
Agent System,
Knowledge System,
Learning Engine,
Director Core,
Self Development Engine.

Hierarchia:

 id="memoryapi01"
SYSTEM

↓

MEMORY API

↓

MEMORY SERVICE

↓

MEMORY ENGINE

↓

MEMORY DATABASE
Główna zasada Memory API

Pamięć SSI nie jest zwykłym magazynem danych.

Jest aktywnym systemem przechowywania doświadczenia.

Model:

 id="memoryapi02"
OBSERVATION

↓

ANALYSIS

↓

MEMORY ENTRY

↓

RETRIEVAL

↓

NEW DECISION
Architektura Memory API
 id="memoryapi03"
                 SSI CORE

                    |

               MEMORY API

                    |

--------------------------------

|              |               |

SHORT TERM   WORKING       LONG TERM

MEMORY       MEMORY        MEMORY

                    |

             MEMORY DATABASE
Typy pamięci obsługiwane przez API
1. SHORT TERM MEMORY API
Pamięć krótkoterminowa

Przechowuje:

aktualny kontekst,
bieżące rozmowy,
tymczasowe informacje.

Operacje:

CREATE_CONTEXT()

GET_CURRENT_CONTEXT()

CLEAR_CONTEXT()
2. WORKING MEMORY API
Pamięć robocza

Przechowuje:

aktualnie wykonywane zadania,
aktywne decyzje,
procesy analizy.

Operacje:

STORE_WORKING_DATA()

UPDATE_WORKING_STATE()

GET_ACTIVE_CONTEXT()
3. LONG TERM MEMORY API
Pamięć długoterminowa

Przechowuje:

doświadczenia,
rozwiązania,
wzorce,
historię systemu.

Operacje:

SAVE_MEMORY()

SEARCH_MEMORY()

RETRIEVE_MEMORY()
4. EXPERIENCE MEMORY API
Pamięć doświadczeń

Zapisuje:

wykonane działania,
wyniki,
błędy,
sukcesy.

Przykład:

EXPERIENCE:

Problem solved

Solution:

Architecture update

Result:

Success
5. PROJECT MEMORY API
Pamięć projektowa

Przechowuje:

strukturę projektu,
decyzje architektoniczne,
historię zmian.
6. AGENT MEMORY API
Pamięć agentów

Każdy agent może posiadać:

własne doświadczenia,
historię pracy,
preferowane strategie.
Podstawowe operacje Memory API
SAVE_MEMORY()
Zapis informacji

Przykład:

SAVE_MEMORY

INPUT:

content

type

source

importance
GET_MEMORY()
Pobranie informacji

Przykład:

GET_MEMORY

INPUT:

memory_id
SEARCH_MEMORY()
Wyszukiwanie

Pozwala znaleźć:

podobne doświadczenia,
wcześniejsze rozwiązania,
kontekst.
UPDATE_MEMORY()
Aktualizacja pamięci

Zmienia istniejące wpisy.

Proces:

REQUEST

↓

VALIDATION

↓

UPDATE

↓

LOG
DELETE_MEMORY()
Usuwanie

Operacja ograniczona.

Wymaga:

uprawnień,
logowania,
walidacji.
MEMORY QUERY MODEL

Zapytanie do pamięci:

{
"query":"",
"context":"",
"type":"",
"limit":"",
"priority":""
}
MEMORY RESPONSE MODEL

Odpowiedź:

{
"memory_id":"",
"content":"",
"confidence":"",
"source":"",
"timestamp":""
}
MEMORY CONTEXT API

Najważniejsza funkcja dla AI.

Pozwala pobrać:

informacje o projekcie,
poprzednie decyzje,
historię działań.

Schemat:

CURRENT TASK

+

PROJECT MEMORY

+

EXPERIENCE MEMORY

+

KNOWLEDGE

=

AI CONTEXT
MEMORY VALIDATION API

Każdy zapis może zostać sprawdzony.

Proces:

NEW MEMORY

↓

VALIDATION

↓

QUALITY CHECK

↓

STORE
MEMORY IMPORTANCE MODEL

Każda informacja posiada wagę:

CRITICAL

HIGH

NORMAL

LOW
MEMORY RELATION API

Pozwala łączyć informacje.

Przykład:

MEMORY A

↓

RELATED TO

↓

MEMORY B
MEMORY EVENT SYSTEM

Pamięć generuje zdarzenia:

MEMORY_CREATED

MEMORY_UPDATED

MEMORY_VALIDATED

MEMORY_ARCHIVED
MEMORY SECURITY API

Chroni dane:

kontrola dostępu,
historia zmian,
walidacja źródeł.
MEMORY VERSIONING API

Każdy ważny wpis może posiadać wersje:

MEMORY_V1

↓

MEMORY_V2

↓

MEMORY_V3
Przykład działania

Agent programista rozwiązuje problem:

PROGRAMMER_AGENT

↓

SAVE_EXPERIENCE()

↓

MEMORY API

↓

MEMORY ENGINE

↓

MEMORY DATABASE

↓

FUTURE RETRIEVAL
Integracja z innymi dokumentami

06_MEMORY_API_SPECIFICATION.md współpracuje z:

03_MEMORY_DATABASE_DESIGN.md

↓

13_MEMORY_SYSTEM_SPECIFICATION.md

↓

06_AGENT_MEMORY_SYSTEM_SPECIFICATION.md

↓

07_MEMORY_INTEGRATION_RULES.md

↓

07_KNOWLEDGE_API_SPECIFICATION.md

↓

28_SELF_IMPROVEMENT_LOOP_SPECIFICATION.md
Cel końcowy

06_MEMORY_API_SPECIFICATION.md definiuje interfejs pamięci całego SSI_SELF_DEVELOPMENT_ENGINE.

Dzięki niemu system może:

zapamiętywać doświadczenia,
odzyskiwać wcześniejsze rozwiązania,
budować kontekst dla AI,
uczyć się na podstawie historii,
rozwijać własną wiedzę.

Dokument jest mechanizmem dostępu do pamięci długoterminowej autonomicznego systemu AI.