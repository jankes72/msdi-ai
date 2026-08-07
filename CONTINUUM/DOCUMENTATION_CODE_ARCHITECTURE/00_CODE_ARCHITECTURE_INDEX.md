Opis:

Ten dokument jest głównym indeksem dokumentacji architektury kodu SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest przedstawienie całego zestawu dokumentów opisujących wewnętrzną budowę kodu systemu, sposób organizacji implementacji, zależności pomiędzy warstwami kodu oraz standardy tworzenia komponentów.

Dokument jest punktem wejścia do całego działu:

DOCUMENTATION_CODE_ARCHITECTURE/
Cel dokumentu

00_CODE_ARCHITECTURE_INDEX.md definiuje:

strukturę dokumentacji kodu,
kolejność czytania dokumentów,
zakres każdego dokumentu,
zależności pomiędzy dokumentami,
miejsce architektury kodu w całym SSI.
Rola dokumentu

Dokument odpowiada na pytanie:

"Jak jest zorganizowana dokumentacja opisująca wewnętrzną budowę kodu SSI?"

Miejsce w całej dokumentacji SSI

Architektura kodu znajduje się pomiędzy projektem logicznym a implementacją.

Schemat:

SYSTEM CONCEPT
        |
        ↓
SYSTEM ARCHITECTURE
        |
        ↓
PROJECT STRUCTURE
        |
        ↓
CODE ARCHITECTURE
        |
        ↓
SYSTEM INTEGRATION
        |
        ↓
SOURCE CODE
        |
        ↓
TESTS
Cel całego działu

Folder:

DOCUMENTATION_CODE_ARCHITECTURE/

opisuje przejście:

ARCHITECTURE

↓

MODULE DESIGN

↓

CLASS DESIGN

↓

FUNCTION DESIGN

↓

IMPLEMENTATION RULES
Zakres dokumentacji

Struktura:

DOCUMENTATION_CODE_ARCHITECTURE/

├── 00_CODE_ARCHITECTURE_INDEX.md
├── 01_CODE_ARCHITECTURE_OVERVIEW.md
├── 02_SOURCE_CODE_STRUCTURE.md
├── 03_MODULE_INTERNAL_ARCHITECTURE.md
├── 04_CLASS_AND_OBJECT_MODEL.md
├── 05_FUNCTION_AND_METHOD_STRUCTURE.md
├── 06_INTERFACE_IMPLEMENTATION_MODEL.md
├── 07_CODE_EXECUTION_FLOW.md
├── 08_RUNTIME_ARCHITECTURE.md
├── 09_SERVICE_LAYER_ARCHITECTURE.md
├── 10_DATA_ACCESS_CODE_STRUCTURE.md
├── 11_CONFIGURATION_CODE_ARCHITECTURE.md
├── 12_EXCEPTION_HANDLING_ARCHITECTURE.md
├── 13_LOGGING_AND_DEBUG_ARCHITECTURE.md
├── 14_TEST_CODE_ARCHITECTURE.md
├── 15_CODE_QUALITY_RULES.md
├── 16_CODE_REFACTORING_RULES.md
├── 17_CODE_VERSIONING_STRATEGY.md
└── 18_CODE_EVOLUTION_ARCHITECTURE.md
Kolejność czytania

Dokumentacja została zaprojektowana jako proces:

Poziom 1 — Ogólna architektura kodu
01_CODE_ARCHITECTURE_OVERVIEW.md

Opisuje:

warstwy kodu,
główne zasady,
organizację systemu.
Poziom 2 — Struktura fizyczna
02_SOURCE_CODE_STRUCTURE.md

Opisuje:

katalogi kodu,
rozmieszczenie plików,
organizację źródeł.
Poziom 3 — Budowa modułów
03_MODULE_INTERNAL_ARCHITECTURE.md

Opisuje:

wnętrze modułów,
komponenty,
odpowiedzialności.
Poziom 4 — Model obiektowy
04_CLASS_AND_OBJECT_MODEL.md

Opisuje:

klasy,
obiekty,
relacje.
Poziom 5 — Implementacja
05_FUNCTION_AND_METHOD_STRUCTURE.md

Opisuje:

funkcje,
metody,
standard kodowania.
Poziom 6 — Integracja kodu
06_INTERFACE_IMPLEMENTATION_MODEL.md

Opisuje:

połączenie modułów,
implementację API,
kontrakty.
Poziom 7 — Wykonanie systemu
07_CODE_EXECUTION_FLOW.md
08_RUNTIME_ARCHITECTURE.md

Opisuje:

start systemu,
przepływ wykonania,
działanie runtime.
Poziom 8 — Warstwy techniczne
09_SERVICE_LAYER_ARCHITECTURE.md
10_DATA_ACCESS_CODE_STRUCTURE.md
11_CONFIGURATION_CODE_ARCHITECTURE.md

Opisuje:

usługi,
dane,
konfigurację.
Poziom 9 — Stabilność kodu
12_EXCEPTION_HANDLING_ARCHITECTURE.md
13_LOGGING_AND_DEBUG_ARCHITECTURE.md
14_TEST_CODE_ARCHITECTURE.md

Opisuje:

błędy,
diagnostykę,
testowanie.
Poziom 10 — Rozwój kodu
15_CODE_QUALITY_RULES.md
16_CODE_REFACTORING_RULES.md
17_CODE_VERSIONING_STRATEGY.md
18_CODE_EVOLUTION_ARCHITECTURE.md

Opisuje:

utrzymanie,
zmiany,
rozwój.
Powiązanie z innymi działami dokumentacji
Poprzednie warstwy:
DOCUMENTATION_PROJECT_STRUCTURE

↓

DOCUMENTATION_CODE_ARCHITECTURE
Następne warstwy:
DOCUMENTATION_CODE_ARCHITECTURE

↓

DOCUMENTATION_SYSTEM_INTEGRATION

↓

PROJECT_BUILD_PLAN
Relacja z implementacją

Dokumentacja kodu jest mapą dla:

programistów,
agentów AI,
systemu samorozwoju SSI.

Schemat:

CODE DOCUMENTATION

↓

IMPLEMENTATION DECISION

↓

SOURCE CODE

↓

TEST VALIDATION
Zasady działu CODE_ARCHITECTURE
1. Kod zawsze wynika z architektury

Nie tworzymy plików bez wcześniejszego określenia:

odpowiedzialności,
lokalizacji,
zależności.
2. Moduły pozostają niezależne

Każdy moduł posiada:

własne klasy,
własne funkcje,
własne testy,
własne interfejsy.
3. Dokumentacja jest częścią kodu

Każda duża zmiana kodu wymaga aktualizacji:

architektury,
zależności,
przepływu wykonania.
Docelowy efekt

Po ukończeniu:

DOCUMENTATION_CODE_ARCHITECTURE/

SSI posiada kompletny opis:

SYSTEM

↓

MODULES

↓

FILES

↓

CLASSES

↓

FUNCTIONS

↓

EXECUTION
Cel końcowy

00_CODE_ARCHITECTURE_INDEX.md jest mapą całej architektury kodu SSI_SELF_DEVELOPMENT_ENGINE.

Stanowi pierwszy dokument, który należy przeczytać przed analizą implementacji.

Jego zadaniem jest zapewnienie, że kod SSI nie powstaje jako zbiór przypadkowych plików, lecz jako zaprojektowany, modularny i rozwijalny system.