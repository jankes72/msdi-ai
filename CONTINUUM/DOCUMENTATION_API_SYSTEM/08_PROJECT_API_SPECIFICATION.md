Opis:

Ten dokument definiuje szczegółową specyfikację API systemu zarządzania projektami (Project API) w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie, w jaki sposób SSI tworzy, analizuje, monitoruje, rozwija oraz zarządza projektami, modułami, strukturą kodu, dokumentacją i stanem budowy systemu poprzez jednolity interfejs API.

Jeżeli:

07_PROJECT_DATA_MODEL.md opisuje strukturę danych projektu,
PROJECT_BUILD_PLAN opisuje plan budowy systemu,
20_PROJECT_ANALYSIS_SYSTEM_SPECIFICATION.md opisuje analizę projektu,

to:

08_PROJECT_API_SPECIFICATION.md definiuje sposób, w jaki wszystkie moduły SSI komunikują się z systemem zarządzania projektami.

Cel dokumentu

08_PROJECT_API_SPECIFICATION.md odpowiada na pytania:

Jak system tworzy nowy projekt?
Jak przechowywany jest stan projektu?
Jak AI analizuje strukturę projektu?
Jak monitorowany jest postęp budowy?
Jak moduły pobierają informacje o projekcie?
Jak zarządzane są wersje projektu?
Jak system śledzi rozwój własnej architektury?
Rola dokumentu

Dokument jest podstawą dla:

Director Core,
Project Manager,
Architecture Agent,
Documentation Agent,
Development Engine,
Knowledge System.

Hierarchia:

 id="project_api01"
SSI CORE

↓

PROJECT API

↓

PROJECT MANAGER

↓

PROJECT ANALYSIS ENGINE

↓

PROJECT STORAGE
Główna zasada Project API

Projekt w SSI nie jest tylko folderem z kodem.

Jest obiektem systemowym posiadającym:

strukturę,
cel,
moduły,
dokumentację,
historię,
stan rozwoju,
zależności.

Model:

 id="project_api02"
PROJECT

{

IDENTITY

OBJECTIVE

STRUCTURE

MODULES

DOCUMENTATION

STATE

VERSION

HISTORY

}
Architektura Project API
 id="project_api03"
                 SSI CORE

                    |

              PROJECT API

                    |

--------------------------------

|              |               |

PROJECT     ANALYSIS       VERSION

MANAGER     ENGINE         CONTROL

                    |

              PROJECT STORAGE
Typy zarządzanych danych projektu
1. PROJECT IDENTITY API
Tożsamość projektu

Przechowuje:

nazwę,
identyfikator,
wersję,
właściciela.

Przykład:

PROJECT_ID:

SSI_ENGINE

VERSION:

1.0
2. PROJECT STRUCTURE API
Struktura projektu

Obsługuje:

katalogi,
pliki,
moduły,
komponenty.

Operacje:

GET_STRUCTURE()

UPDATE_STRUCTURE()

ANALYZE_STRUCTURE()
3. PROJECT MODULE API
Zarządzanie modułami

Pozwala:

dodawać moduły,
usuwać,
sprawdzać zależności.

Operacje:

ADD_MODULE()

REMOVE_MODULE()

GET_MODULE_INFO()
4. PROJECT STATE API
Stan projektu

System śledzi:

etap budowy,
aktywne zadania,
ukończone elementy.

Przykład:

PROJECT STATE:

BUILDING

PHASE:

API DEVELOPMENT

PROGRESS:

35%
5. PROJECT ANALYSIS API
Analiza projektu

Umożliwia:

skanowanie struktury,
wykrywanie braków,
analizę zależności.

Operacje:

ANALYZE_PROJECT()

CHECK_DEPENDENCIES()

GENERATE_REPORT()
6. PROJECT DOCUMENTATION API
Zarządzanie dokumentacją

Obsługuje:

dokumenty,
wersje,
indeksy.

Operacje:

ADD_DOCUMENT()

UPDATE_DOCUMENT()

SEARCH_DOCUMENT()
7. PROJECT BUILD API
Zarządzanie procesem budowy

Kontroluje:

etapy,
sprinty,
zadania implementacyjne.

Operacje:

START_BUILD_PHASE()

GET_BUILD_STATUS()

COMPLETE_PHASE()
8. PROJECT VERSION API
Wersjonowanie projektu

Obsługuje:

PROJECT_V1

↓

PROJECT_V2

↓

PROJECT_V3

Operacje:

CREATE_VERSION()

COMPARE_VERSION()

ROLLBACK_VERSION()
9. PROJECT DEPENDENCY API
Zależności projektu

Przechowuje:

zależności modułów,
wymagane komponenty,
kolejność budowy.

Przykład:

CORE

↓

API

↓

AGENTS

↓

MEMORY
10. PROJECT CONTEXT API
Kontekst projektu dla AI

Najważniejszy element.

Udostępnia:

cel projektu,
aktualny stan,
historię zmian,
wymagania.

Schemat:

TASK

+

PROJECT STATE

+

DOCUMENTATION

+

MEMORY

=

PROJECT CONTEXT
11. PROJECT EVENT API
Zdarzenia projektu

System generuje:

PROJECT_CREATED

MODULE_ADDED

BUILD_STARTED

VERSION_CREATED

PROJECT_UPDATED
12. PROJECT SEARCH API
Wyszukiwanie informacji

Pozwala znaleźć:

moduły,
dokumenty,
zadania,
decyzje.

Operacja:

SEARCH_PROJECT()
13. PROJECT METRICS API
Statystyki projektu

Monitoruje:

ilość modułów,
postęp,
błędy,
czas budowy.

Operacje:

GET_METRICS()

GENERATE_REPORT()
14. PROJECT SECURITY API
Ochrona projektu

Kontroluje:

dostęp,
uprawnienia,
krytyczne zmiany.

Proces:

REQUEST

↓

AUTHORIZATION

↓

CHANGE APPROVAL

↓

EXECUTION
15. PROJECT BACKUP API
Kopie projektu

Integruje się z:

backup system,
recovery system.

Operacje:

CREATE_PROJECT_BACKUP()

RESTORE_PROJECT()
Model zapytania Project API
{
"request_id":"",
"project_id":"",
"action":"",
"context":"",
"parameters":""
}
Model odpowiedzi Project API
{
"request_id":"",
"status":"",
"result":"",
"metadata":"",
"error":""
}
Przykład działania

AI chce sprawdzić stan budowy:

DIRECTOR_CORE

↓

GET_PROJECT_STATE()

↓

PROJECT API

↓

PROJECT MANAGER

↓

RETURN STATUS

↓

DECISION
Integracja z innymi dokumentami

08_PROJECT_API_SPECIFICATION.md współpracuje z:

07_PROJECT_DATA_MODEL.md

↓

20_PROJECT_ANALYSIS_SYSTEM_SPECIFICATION.md

↓

31_AI_DEVELOPMENT_DOCUMENTATION_SPECIFICATION.md

↓

05_TASK_API_SPECIFICATION.md

↓

06_MEMORY_API_SPECIFICATION.md

↓

30_SYSTEM_INTEGRATION_SPECIFICATION.md
Cel końcowy

08_PROJECT_API_SPECIFICATION.md definiuje interfejs zarządzania całym środowiskiem projektowym SSI_SELF_DEVELOPMENT_ENGINE.

Dzięki niemu system może:

rozumieć własną strukturę,
monitorować rozwój,
analizować kod i dokumentację,
zarządzać etapami budowy,
kontrolować ewolucję projektu.

Dokument jest centrum komunikacji pomiędzy AI a własnym środowiskiem rozwoju systemu.