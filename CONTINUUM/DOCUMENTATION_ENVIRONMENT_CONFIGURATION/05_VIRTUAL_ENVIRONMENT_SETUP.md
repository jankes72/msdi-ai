Opis:

Ten dokument definiuje proces tworzenia, konfiguracji i zarządzania izolowanym środowiskiem Python Virtual Environment dla SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest opisanie jak odseparować środowisko SSI od systemowego Pythona oraz zapewnić kontrolę nad wszystkimi bibliotekami, wersjami i zależnościami projektu.

Dokument odpowiada na pytanie:

"Jak stworzyć niezależne środowisko wykonawcze, w którym SSI może rozwijać się bez konfliktów z systemem?"

Cel dokumentu

05_VIRTUAL_ENVIRONMENT_SETUP.md definiuje:

strukturę środowiska virtualnego,
proces tworzenia środowiska,
aktywację i dezaktywację,
instalację zależności,
izolację bibliotek,
zarządzanie wersjami,
odtwarzanie środowiska,
walidację poprawności działania.
Rola dokumentu

Dokument opisuje warstwę izolacji wykonawczej SSI.

Architektura:

OPERATING SYSTEM

        │

        ▼

SYSTEM PYTHON

        │

        ▼

VIRTUAL ENVIRONMENT

        │

        ▼

SSI PYTHON RUNTIME

        │

        ▼

APPLICATION
Miejsce dokumentacji
DOCUMENTATION_ENVIRONMENT_CONFIGURATION

├── 00_ENVIRONMENT_CONFIGURATION_INDEX.md
├── 01_DEVELOPMENT_ENVIRONMENT_SETUP.md
├── 02_OPERATING_SYSTEM_REQUIREMENTS.md
├── 03_PROGRAMMING_LANGUAGE_CONFIGURATION.md
├── 04_PYTHON_ENVIRONMENT_CONFIGURATION.md

↓

├── 05_VIRTUAL_ENVIRONMENT_SETUP.md

↓

├── 06_DEPENDENCY_MANAGEMENT.md
Definicja Virtual Environment

Virtual Environment to:

Izolowana przestrzeń wykonawcza Python zawierająca własny interpreter, biblioteki oraz konfigurację wymaganą przez SSI.

Cel izolacji

Bez virtual environment:

SYSTEM PYTHON

├── Project A

├── Project B

└── SSI

Problemy:

konflikty wersji,
różne biblioteki,
niestabilne środowisko.

Z virtual environment:

SYSTEM PYTHON

        │

        ├── PROJECT A ENV

        ├── PROJECT B ENV

        └── SSI ENV

              │

              ├── Libraries

              ├── Models

              └── Runtime
1. ENVIRONMENT STRUCTURE

Standardowa struktura:

SSI_PROJECT

│

├── .venv

│    ├── Scripts

│    ├── Lib

│    └── Include

│

├── src

├── config

├── models

├── data

├── tests

└── requirements.txt
2. ENVIRONMENT CREATION

Proces tworzenia:

Python Installed

↓

Create Virtual Environment

↓

Activate Environment

↓

Install Dependencies

↓

Validate
3. ENVIRONMENT NAMING STANDARD

Standard:

.venv

lub:

ssi_env

Zasada:

Jedna instalacja projektu = jedno środowisko.

4. ACTIVATION PROCESS

Aktywacja:

Developer

↓

Activate Environment

↓

Python Points To .venv

↓

SSI Runtime Ready

Po aktywacji:

python

↓

.venv/python

5. DEACTIVATION PROCESS

Wyjście ze środowiska:

SSI Environment

↓

Deactivate

↓

Return To System Python
6. PACKAGE ISOLATION

Każda biblioteka SSI znajduje się wewnątrz:

.venv

↓

site-packages

↓

SSI Libraries

Korzyści:

brak konfliktów,
kontrola wersji,
możliwość odtworzenia.
7. DEPENDENCY INSTALLATION

Biblioteki instalowane są do:

Virtual Environment

↓

Package Manager

↓

SSI Dependencies

Źródło:

requirements.txt
8. ENVIRONMENT REPRODUCTION

Środowisko musi być odtwarzalne.

Proces:

Clean Machine

↓

Install Python

↓

Create .venv

↓

Install Requirements

↓

Same SSI Environment
9. MULTIPLE ENVIRONMENT SUPPORT

SSI posiada profile:

ENVIRONMENTS

├── development

├── testing

├── staging

└── production
Development

Do:

pisania kodu,
eksperymentów,
debugowania.
Testing

Do:

testów automatycznych,
walidacji zmian.
Production

Do:

stabilnej pracy systemu.
10. ENVIRONMENT CONFIGURATION

Virtual environment współpracuje z:

konfiguracją projektu,
zmiennymi środowiskowymi,
plikami ustawień.

Schemat:

.venv

+

CONFIG

+

ENV VARIABLES

=

SSI Runtime
11. ENVIRONMENT VARIABLES

Przykłady:

SSI_ENV=development

SSI_ROOT=/project/path

MODEL_PATH=/models

DATA_PATH=/data
12. PYTHON PATH MANAGEMENT

Środowisko kontroluje:

import modułów,
ścieżki projektu,
dostęp bibliotek.

Model:

PYTHON PATH

↓

MODULE DISCOVERY

↓

SSI COMPONENTS
13. DEBUG ENVIRONMENT

Virtual environment wspiera:

debugowanie,
testowanie,
analizę błędów.

Proces:

ERROR

↓

DEBUG MODE

↓

ANALYSIS

↓

FIX
14. SECURITY RULES

Środowisko musi:

być lokalnie kontrolowane,
posiadać znane źródła pakietów,
nie zawierać nieautoryzowanych bibliotek.
15. BACKUP ENVIRONMENT

Nie kopiuje się całego .venv.

Zapisywane są:

requirements.txt

+

Configuration

+

Environment Metadata
16. CLEAN REBUILD PROCESS

W przypadku problemu:

Remove .venv

↓

Create New .venv

↓

Install Dependencies

↓

Run Validation
17. ENVIRONMENT VALIDATION

Kontrola:

✓ Environment Exists

✓ Python Version

✓ Packages Installed

✓ Imports Work

✓ SSI Starts
18. AUTOMATION SUPPORT

Docelowo:

SSI może automatycznie:

wykrywać brak środowiska,
tworzyć .venv,
instalować zależności,
sprawdzać poprawność.

Schemat:

Environment Missing

↓

Bootstrap Agent

↓

Create Environment

↓

Validate
Virtual Environment Lifecycle
CREATE

↓

CONFIGURE

↓

INSTALL

↓

ACTIVATE

↓

RUN

↓

UPDATE

↓

REBUILD
Integracja z SSI

Virtual Environment zapewnia:

PYTHON

↓

DEPENDENCIES

↓

AI MODELS

↓

AGENTS

↓

SSI CORE
Powiązanie z innymi dokumentami
05_VIRTUAL_ENVIRONMENT_SETUP.md

↓

06_DEPENDENCY_MANAGEMENT.md

↓

07_MODEL_RUNTIME_CONFIGURATION.md

↓

14_ENVIRONMENT_VALIDATION_CHECKLIST.md

↓

DOCUMENTATION_CODE_ARCHITECTURE
Zasady Virtual Environment SSI

Środowisko musi być:

1. Isolated

2. Reproducible

3. Controlled

4. Portable

5. Validated
Cel końcowy

05_VIRTUAL_ENVIRONMENT_SETUP.md definiuje mechanizm izolacji środowiska Python dla SSI_SELF_DEVELOPMENT_ENGINE.

Po zastosowaniu:

SSI posiada własne środowisko wykonawcze,
biblioteki są kontrolowane,
konflikty zależności są eliminowane,
system można łatwo odtworzyć na innej maszynie.

Jest to warstwa bezpieczeństwa i stabilności środowiska Python — fundament umożliwiający długoterminowy rozwój SSI bez degradacji infrastruktury technicznej.