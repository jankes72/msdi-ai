Opis:

Ten dokument definiuje standard zarządzania zmiennymi środowiskowymi dla SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest opisanie jak system przechowuje, ładuje i wykorzystuje wartości konfiguracyjne zależne od środowiska uruchomieniowego, takie jak ścieżki, tryb pracy, dane dostępowe, ustawienia bezpieczeństwa oraz parametry runtime.

Dokument odpowiada na pytanie:

"Jak oddzielić konfigurację środowiska od kodu, aby SSI mogło działać w różnych warunkach bez modyfikowania programu?"

Cel dokumentu

11_ENVIRONMENT_VARIABLES_SPECIFICATION.md definiuje:

architekturę zmiennych środowiskowych,
standard nazewnictwa,
strukturę pliku .env,
hierarchię konfiguracji,
sposób ładowania wartości,
bezpieczeństwo sekretów,
konfigurację środowisk DEV/TEST/PROD,
walidację zmiennych,
zarządzanie zmianami.
Rola dokumentu

Dokument opisuje warstwę dynamicznej konfiguracji systemu SSI.

Architektura:

OPERATING SYSTEM

        │

        ▼

ENVIRONMENT VARIABLES

        │

        ▼

CONFIGURATION LOADER

        │

        ▼

SSI APPLICATION

        │

        ▼

RUNTIME BEHAVIOR
Miejsce dokumentacji
DOCUMENTATION_ENVIRONMENT_CONFIGURATION

├── 00_ENVIRONMENT_CONFIGURATION_INDEX.md
├── 01_DEVELOPMENT_ENVIRONMENT_SETUP.md
├── 02_OPERATING_SYSTEM_REQUIREMENTS.md
├── 03_PROGRAMMING_LANGUAGE_CONFIGURATION.md
├── 04_PYTHON_ENVIRONMENT_CONFIGURATION.md
├── 05_VIRTUAL_ENVIRONMENT_SETUP.md
├── 06_DEPENDENCY_MANAGEMENT.md
├── 07_MODEL_RUNTIME_CONFIGURATION.md
├── 08_DATABASE_ENVIRONMENT_SETUP.md
├── 09_STORAGE_CONFIGURATION.md
├── 10_CONFIGURATION_FILE_SYSTEM.md

↓

├── 11_ENVIRONMENT_VARIABLES_SPECIFICATION.md

↓

├── 12_RUNTIME_CONFIGURATION_SPECIFICATION.md
Definicja Environment Variables

Environment Variables to:

Dynamiczne wartości konfiguracyjne przekazywane do aplikacji przez środowisko wykonawcze, niezależne od kodu źródłowego.

Główna zasada

Kod:

CODE

nie zawiera:

PASSWORD
API KEY
PATH
ENVIRONMENT MODE

Zamiast tego:

CODE

↓

ENVIRONMENT VARIABLES

↓

RUNTIME CONFIGURATION
Architektura zmiennych SSI
              ENVIRONMENT SYSTEM

                     │

       ┌─────────────┼─────────────┐

       ▼             ▼             ▼

   SYSTEM VARS   SECURITY VARS   RUNTIME VARS

       │             │             │

       └─────────────┼─────────────┘

                     ▼

             SSI CONFIG LOADER

                     │

                     ▼

                APPLICATION
1. ENVIRONMENT VARIABLE CATEGORIES

Zmienne dzielą się na:

ENVIRONMENT VARIABLES

├── SYSTEM

├── APPLICATION

├── DATABASE

├── MODEL

├── STORAGE

├── SECURITY

├── LOGGING

├── DEVELOPMENT

└── AI RUNTIME
2. SYSTEM VARIABLES

Sterują podstawowym środowiskiem.

Przykład:

SSI_ENVIRONMENT=development

SSI_VERSION=1.0

SSI_MODE=development
3. APPLICATION VARIABLES

Konfigurują aplikację:

APP_NAME

APP_VERSION

APP_ROOT

APP_DEBUG

Przykład:

APP_ROOT=D:/SSI
APP_DEBUG=true
4. DATABASE VARIABLES

Przechowują konfigurację połączeń:

DATABASE_HOST

DATABASE_PORT

DATABASE_NAME

DATABASE_USER

DATABASE_PASSWORD

Schemat:

ENV VARIABLES

↓

DATABASE CONNECTOR

↓

DATABASE
5. MODEL RUNTIME VARIABLES

Sterują modelami AI:

MODEL_PATH

MODEL_CACHE_PATH

MODEL_DEVICE

MODEL_MEMORY_LIMIT

Przykład:

MODEL_DEVICE=GPU
6. STORAGE VARIABLES

Określają lokalizacje danych:

DATA_PATH

LOG_PATH

BACKUP_PATH

MEMORY_PATH

MODEL_PATH
7. SECURITY VARIABLES

Chronione dane:

SECRET_KEY

API_TOKEN

ENCRYPTION_KEY

ACCESS_TOKEN

Zasada:

SECRET DATA

≠

SOURCE CODE
8. LOGGING VARIABLES

Sterują systemem logów:

LOG_LEVEL

LOG_FORMAT

LOG_DIRECTORY

Przykład:

LOG_LEVEL=INFO
9. ENVIRONMENT FILE STRUCTURE

Standard:

SSI_PROJECT

├── .env

├── .env.development

├── .env.testing

└── .env.production
10. EXAMPLE ENV FILE

Przykład:

SSI_ENV=development

APP_DEBUG=true

MODEL_PATH=./models

DATABASE_HOST=localhost

LOG_LEVEL=INFO
11. VARIABLE NAMING CONVENTION

Standard:

UPPERCASE_WITH_UNDERSCORE

Przykłady:

Poprawnie:

MODEL_PATH
DATABASE_URL
SSI_VERSION

Niepoprawnie:

modelPath
database-url
12. CONFIGURATION PRIORITY

Hierarchia:

DEFAULT VALUES

↓

CONFIG FILES

↓

ENVIRONMENT VARIABLES

↓

RUNTIME OVERRIDE

↓

ACTIVE CONFIGURATION
13. ENVIRONMENT LOADING SYSTEM

Proces:

SYSTEM START

↓

READ ENV VARIABLES

↓

VALIDATE VALUES

↓

MERGE CONFIGURATION

↓

START APPLICATION
14. VALIDATION SYSTEM

Każda zmienna jest sprawdzana:

VARIABLE EXISTS

↓

TYPE CORRECT

↓

VALUE VALID

↓

PERMISSION OK

↓

ACCEPT
15. TYPE MANAGEMENT

Zmienne mogą posiadać typ:

STRING

INTEGER

BOOLEAN

PATH

LIST

SECRET

Przykład:

DEBUG_MODE=true

jest konwertowane:

bool
16. ENVIRONMENT PROFILES

SSI posiada profile:

ENVIRONMENTS

├── DEVELOPMENT

├── TESTING

├── STAGING

└── PRODUCTION

Każdy posiada własne wartości.

17. SECURITY MANAGEMENT

Zasady:

brak sekretów w repozytorium,
szyfrowanie wrażliwych wartości,
kontrola dostępu.

Schemat:

SECRET

↓

ENVIRONMENT

↓

APPLICATION

↓

USE
18. CHANGE MANAGEMENT

Zmiana zmiennej:

REQUEST

↓

ANALYSIS

↓

UPDATE

↓

VALIDATION

↓

DEPLOY
19. BACKUP AND RECOVERY

Backup obejmuje:

nazwy zmiennych,
strukturę,
dokumentację.

Nie:

jawne sekrety.
20. AUTOMATED ENVIRONMENT CHECK

SSI może posiadać kontroler:

ENVIRONMENT CHECKER

↓

SCAN VARIABLES

↓

REPORT ERRORS

↓

FIX SUGGESTIONS
Environment Variable Lifecycle
DEFINE

↓

STORE

↓

LOAD

↓

VALIDATE

↓

USE

↓

UPDATE

↓

REMOVE
Integracja z SSI

Zmienne środowiskowe sterują:

ENVIRONMENT VARIABLES

↓

CONFIGURATION SYSTEM

↓

RUNTIME

↓

MODELS

↓

DATABASE

↓

AGENTS

↓

SELF DEVELOPMENT ENGINE
Powiązanie z innymi dokumentami
11_ENVIRONMENT_VARIABLES_SPECIFICATION.md

↓

10_CONFIGURATION_FILE_SYSTEM.md

↓

12_RUNTIME_CONFIGURATION_SPECIFICATION.md

↓

SECURITY_CONFIGURATION.md

↓

DEPLOYMENT_ARCHITECTURE.md
Zasady Environment Variables SSI

System musi być:

1. Secure

2. Flexible

3. Externalized

4. Validated

5. Environment Independent
Cel końcowy

11_ENVIRONMENT_VARIABLES_SPECIFICATION.md definiuje mechanizm oddzielenia konfiguracji środowiska od kodu SSI_SELF_DEVELOPMENT_ENGINE.

Po zastosowaniu:

kod pozostaje niezależny od środowiska,
można uruchamiać SSI na różnych maszynach,
sekrety są chronione,
konfiguracja jest kontrolowana.

Jest to warstwa adaptacji SSI do różnych środowisk uruchomieniowych — fundament umożliwiający przenoszenie systemu między komputerami, serwerami i środowiskami produkcyjnymi bez zmiany kodu.