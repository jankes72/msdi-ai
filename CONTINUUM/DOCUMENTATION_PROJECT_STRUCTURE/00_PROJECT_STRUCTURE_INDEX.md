Opis:

Ten dokument jest głównym indeksem dokumentacji dotyczącej struktury projektu SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest przedstawienie mapy całego działu PROJECT_STRUCTURE, określenie kolejności czytania dokumentów oraz pokazanie zależności pomiędzy dokumentami opisującymi fizyczną organizację projektu.

Dokument pełni rolę punktu wejścia do architektury plików i katalogów SSI.

Cel dokumentu

00_PROJECT_STRUCTURE_INDEX.md definiuje:

strukturę dokumentacji projektu,
kolejność analizy dokumentów,
zakres każdego dokumentu,
zależności między elementami struktury,
miejsce PROJECT_STRUCTURE w całej architekturze SSI.
Rola dokumentu

Ten dokument jest pierwszym miejscem, do którego trafia osoba rozwijająca SSI.

Odpowiada na pytanie:

"Gdzie znajduje się informacja o organizacji całego projektu?"

Miejsce w architekturze dokumentacji
DOCUMENTATION/

│
├── DATABASE_DOCUMENTATION/
│
├── API_DOCUMENTATION/
│
├── MESSAGE_SYSTEM_DOCUMENTATION/
│
└── PROJECT_STRUCTURE_DOCUMENTATION/
        │
        └── 00_PROJECT_STRUCTURE_INDEX.md
Zakres PROJECT_STRUCTURE

Ten dział opisuje fizyczną organizację:

katalogów,
plików,
modułów,
zależności,
kolejności budowy.

Nie opisuje:

logiki biznesowej,
algorytmów,
implementacji funkcji.
Główna zasada

Struktura projektu musi być znana zanim powstanie kod.

Proces:

ARCHITECTURE DESIGN

↓

PROJECT STRUCTURE

↓

MODULE PLACEMENT

↓

CODE IMPLEMENTATION

↓

TESTING
Dokumenty w sekcji PROJECT_STRUCTURE
01_PROJECT_FILE_STRUCTURE_BOOTSTRAP.md
Cel:

Opisuje utworzenie pierwszego fizycznego szkieletu projektu.

Zawiera:

katalog główny,
podstawowe foldery,
pierwsze pliki,
strukturę startową.
02_ROOT_DIRECTORY_MAP.md
Cel:

Opisuje główny katalog projektu.

Pokazuje:

SSI_SELF_DEVELOPMENT_ENGINE/

CORE/

MESSAGE_SYSTEM/

MEMORY_SYSTEM/

AGENT_SYSTEM/

oraz odpowiedzialność każdego elementu.

03_FOLDER_RESPONSIBILITY_MAP.md
Cel:

Opisuje rolę każdego folderu.

Przykład:

CORE/

Odpowiedzialność:

- runtime
- lifecycle
- system state
04_FILE_NAMING_CONVENTION.md
Cel:

Definiuje standard nazewnictwa.

Obejmuje:

pliki Python,
klasy,
moduły,
konfiguracje,
dokumentację.

Przykład:

message_router.py

MemoryManager

system_config.json
05_MODULE_LOCATION_MAP.md
Cel:

Pokazuje gdzie znajduje się każda funkcjonalność.

Przykład:

Message Routing

↓

MESSAGE_SYSTEM/routing/

↓

message_router.py
06_MODULE_DEPENDENCY_MAP.md
Cel:

Opisuje zależności pomiędzy modułami.

Pokazuje:

kto może korzystać z którego modułu,
kierunek komunikacji,
granice odpowiedzialności.

Przykład:

AGENT_SYSTEM

↓

MESSAGE_SYSTEM

↓

MEMORY_SYSTEM
07_BUILD_ORDER_PLAN.md
Cel:

Opisuje kolejność tworzenia systemu.

Przykład:

FAZA 1

PROJECT STRUCTURE


FAZA 2

CORE


FAZA 3

DATABASE


FAZA 4

MESSAGE SYSTEM


FAZA 5

MEMORY


FAZA 6

AGENTS


FAZA 7

EVOLUTION
Mapa zależności dokumentów
00_PROJECT_STRUCTURE_INDEX

          |

          ▼

01_PROJECT_FILE_STRUCTURE_BOOTSTRAP

          |

          ▼

02_ROOT_DIRECTORY_MAP

          |

          ▼

03_FOLDER_RESPONSIBILITY_MAP

          |

          ▼

04_FILE_NAMING_CONVENTION

          |

          ▼

05_MODULE_LOCATION_MAP

          |

          ▼

06_MODULE_DEPENDENCY_MAP

          |

          ▼

07_BUILD_ORDER_PLAN
Powiązanie z kodem

Dokumentacja PROJECT_STRUCTURE opisuje późniejszy układ:

SSI_SELF_DEVELOPMENT_ENGINE/

├── CORE/

├── MESSAGE_SYSTEM/

├── MEMORY_SYSTEM/

├── KNOWLEDGE_SYSTEM/

├── AGENT_SYSTEM/

├── TASK_SYSTEM/

├── DATABASE/

├── API/

├── EVOLUTION_ENGINE/
Powiązanie z innymi dokumentacjami
DATABASE

Opisuje:

modele danych,
przechowywanie informacji.
API

Opisuje:

komunikację między modułami.
MESSAGE_SYSTEM

Opisuje:

format i przepływ wiadomości.
PROJECT_STRUCTURE

Opisuje:

gdzie fizycznie znajdują się wszystkie elementy.
Przepływ projektowania SSI
SYSTEM IDEA

↓

ARCHITECTURE DOCUMENTATION

↓

DATABASE DESIGN

↓

API DESIGN

↓

MESSAGE DESIGN

↓

PROJECT STRUCTURE

↓

CODE IMPLEMENTATION

↓

TESTING

↓

EVOLUTION
Cel końcowy

00_PROJECT_STRUCTURE_INDEX.md zapewnia, że cały projekt SSI_SELF_DEVELOPMENT_ENGINE posiada jedno centralne miejsce nawigacji po swojej strukturze.

Po wykonaniu tego dokumentu każdy uczestnik projektu wie:

jakie dokumenty opisują strukturę,
gdzie znaleźć informacje,
jak wygląda organizacja projektu,
jaka jest kolejność budowy.

Jest to mapa architektoniczna repozytorium SSI — punkt startowy dla całego procesu implementacji systemu.