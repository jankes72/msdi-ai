Opis:

Ten dokument definiuje szczegółową specyfikację API warstwy baz danych (Database API) w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie, w jaki sposób wszystkie moduły systemu uzyskują bezpieczny i kontrolowany dostęp do danych przechowywanych w bazach, bez bezpośredniego połączenia z warstwą danych.

Jeżeli:

DATABASE_DOCUMENTATION opisuje architekturę i strukturę baz danych,
03_DATABASE_MEMORY_DESIGN.md opisuje organizację danych pamięci,
02_DATA_MODEL_SPECIFICATION.md opisuje modele danych,
03_INTERNAL_API_DESIGN.md opisuje komunikację wewnętrzną,

to:

10_DATABASE_API_SPECIFICATION.md definiuje warstwę pośrednią, która pozwala modułom SSI korzystać z danych w sposób kontrolowany, bezpieczny i skalowalny.

Cel dokumentu

10_DATABASE_API_SPECIFICATION.md odpowiada na pytania:

Jak moduły pobierają dane z bazy?
Jak zapisywane są nowe informacje?
Jak kontrolować dostęp do danych?
Jak wykonywać operacje CRUD?
Jak walidować dane przed zapisem?
Jak zabezpieczyć integralność informacji?
Jak zmienić typ bazy danych bez przebudowy całego systemu?
Rola dokumentu

Dokument jest podstawą dla:

Database Manager,
Memory System,
Knowledge System,
Agent System,
Project System,
Backup System.

Hierarchia:

SSI MODULE

↓

DATABASE API

↓

DATABASE SERVICE

↓

DATABASE ENGINE

↓

DATABASE STORAGE
Główna zasada Database API

Żaden moduł SSI nie komunikuje się bezpośrednio z bazą danych.

Nie:

AGENT

↓

SQL DATABASE

Tylko:

AGENT

↓

MEMORY API

↓

DATABASE API

↓

DATABASE ENGINE

↓

STORAGE
Architektura Database API
                 SSI CORE

                    |

              DATABASE API

                    |

--------------------------------

|              |               |

QUERY        DATA          SECURITY

ENGINE       SERVICE       LAYER

                    |

              DATABASE SYSTEM
Warstwy Database API
1. DATA ACCESS LAYER
Warstwa dostępu do danych

Odpowiada za:

komunikację z bazą,
wykonywanie operacji,
mapowanie danych.
2. DATABASE SERVICE LAYER
Warstwa usług danych

Udostępnia modułom:

zapis,
odczyt,
wyszukiwanie,
aktualizację.
3. DATABASE CONTROL LAYER
Kontrola operacji

Zarządza:

uprawnieniami,
walidacją,
logowaniem.
Podstawowe operacje Database API
CREATE_RECORD()
Tworzenie danych

Dodaje nowy rekord.

Przykład:

CREATE_RECORD

INPUT:

entity

data

metadata
GET_RECORD()
Pobranie danych

Pobiera konkretny obiekt.

Przykład:

GET_RECORD

INPUT:

record_id
SEARCH_RECORDS()
Wyszukiwanie

Pozwala znaleźć dane według:

parametrów,
filtrów,
kontekstu.
UPDATE_RECORD()
Aktualizacja danych

Proces:

REQUEST

↓

VALIDATION

↓

UPDATE

↓

LOG
DELETE_RECORD()
Usuwanie danych

Operacja kontrolowana.

Wymaga:

uprawnień,
historii,
potwierdzenia.
DATABASE QUERY API
Obsługa zapytań

Pozwala wykonywać:

wyszukiwanie,
filtrowanie,
sortowanie.

Model:

{
"entity":"",
"filter":"",
"limit":"",
"sort":"",
"context":""
}
DATABASE RESPONSE MODEL

Odpowiedź:

{
"status":"",
"records":"",
"metadata":"",
"timestamp":"",
"error":""
}
DATABASE ENTITY API
Zarządzanie obiektami danych

Obsługiwane encje:

AGENT

TASK

MEMORY

KNOWLEDGE

PROJECT

MESSAGE

EVENT
DATABASE TRANSACTION API
Transakcje danych

Zapewnia:

spójność,
bezpieczeństwo operacji.

Model:

BEGIN

↓

OPERATION

↓

VALIDATE

↓

COMMIT

lub:

ROLLBACK
DATABASE VALIDATION API
Walidacja danych

Przed zapisem:

NEW DATA

↓

SCHEMA CHECK

↓

QUALITY CHECK

↓

SAVE
DATABASE MIGRATION API
Migracje struktury

Obsługuje:

zmiany tabel,
nowe pola,
aktualizacje modeli.

Przykład:

DATABASE_V1

↓

MIGRATION

↓

DATABASE_V2
DATABASE VERSIONING API
Historia danych

Pozwala zachować:

poprzednie wersje,
zmiany,
autora zmian.
DATABASE BACKUP API
Kopie danych

Operacje:

CREATE_BACKUP()

RESTORE_BACKUP()

CHECK_BACKUP()
DATABASE SECURITY API
Ochrona danych

Kontroluje:

dostęp,
role,
uprawnienia,
szyfrowanie.

Schemat:

REQUEST

↓

AUTHORIZATION

↓

DATA ACCESS
DATABASE LOGGING API
Historia operacji

Rejestruje:

kto wykonał zmianę,
kiedy,
jakie dane zmieniono.
DATABASE CACHE API
Przyspieszenie dostępu

Obsługuje:

często używane dane,
szybkie odczyty,
synchronizację.
DATABASE EVENT API

Zmiany w bazie mogą generować zdarzenia:

RECORD_CREATED

RECORD_UPDATED

RECORD_DELETED

Przykład:

MEMORY_UPDATED

↓

KNOWLEDGE_ANALYSIS
DATABASE ERROR API

Obsługa błędów:

brak połączenia,
konflikt danych,
błąd zapisu.

Proces:

ERROR

↓

RECOVERY

↓

REPORT
Przykład pełnego przepływu

Agent zapisuje doświadczenie:

PROGRAMMER_AGENT

↓

MEMORY_API

↓

DATABASE_API

↓

CREATE_RECORD()

↓

DATABASE

↓

CONFIRMATION
Integracja z innymi dokumentami

10_DATABASE_API_SPECIFICATION.md współpracuje z:

00_DATABASE_DOCUMENTATION_INDEX.md

↓

01_DATABASE_ARCHITECTURE_OVERVIEW.md

↓

02_DATA_MODEL_SPECIFICATION.md

↓

03_MEMORY_DATABASE_DESIGN.md

↓

06_MEMORY_API_SPECIFICATION.md

↓

07_KNOWLEDGE_API_SPECIFICATION.md

↓

10_DATABASE_BACKUP_AND_RECOVERY.md

↓

17_API_TESTING_SPECIFICATION.md
Cel końcowy

10_DATABASE_API_SPECIFICATION.md definiuje bezpieczną warstwę komunikacji pomiędzy systemem SSI a jego bazami danych.

Dzięki niemu system może:

zarządzać wszystkimi danymi,
chronić integralność informacji,
wymieniać bazę danych bez zmiany modułów,
kontrolować dostęp,
tworzyć historię zmian.

Dokument jest warstwą abstrakcji danych, która pozwala autonomicznemu systemowi AI rozwijać się bez utraty kontroli nad własną pamięcią i wiedzą.