Opis:

Ten dokument definiuje odpowiedzialność każdego folderu w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie dlaczego dany katalog istnieje, jakie zadania realizuje, jakie elementy może zawierać oraz czego nie powinien zawierać.

Dokument jest rozwinięciem:

02_ROOT_DIRECTORY_MAP.md

który pokazuje gdzie znajdują się foldery, natomiast ten dokument opisuje:

"Za co dokładnie odpowiada każdy folder i jakie są jego granice."

Cel dokumentu

03_FOLDER_RESPONSIBILITY_MAP.md definiuje:

odpowiedzialność każdego katalogu,
zakres działania modułów,
granice pomiędzy systemami,
zasady organizacji kodu,
zasady dodawania nowych elementów.
Rola dokumentu

Dokument zapobiega chaosowi architektury.

Bez tego dokumentu z czasem powstaje problem:

CORE zaczyna robić wszystko

MESSAGE_SYSTEM zapisuje dane

AGENT_SYSTEM zarządza bazą

DATABASE wykonuje logikę biznesową

Po zastosowaniu zasad:

KAŻDY FOLDER = JEDNA ODPOWIEDZIALNOŚĆ
Główna zasada architektury

Każdy moduł SSI posiada:

własny zakres,
własną odpowiedzialność,
własne granice.

Schemat:

MODULE

↓

RESPONSIBILITY

↓

IMPLEMENTATION

↓

INTERFACE
Mapa odpowiedzialności folderów
CONFIG/
Główna odpowiedzialność:

Konfiguracja systemu

Folder przechowuje wszystkie ustawienia sterujące SSI.

Może zawierać:
pliki JSON,
YAML,
ustawienia środowiska,
parametry systemowe.

Przykład:

CONFIG/

system_config.json

model_config.json

database_config.json
Nie może zawierać:

❌ kodu Python
❌ logiki systemowej
❌ danych użytkownika

CORE/
Główna odpowiedzialność:

Centralne jądro wykonawcze SSI

Odpowiada za:
uruchamianie systemu,
inicjalizację modułów,
zarządzanie stanem,
cykl życia.
Może komunikować się z:
CORE

↓

WSZYSTKIE MODUŁY
Nie może zawierać:

❌ logiki specjalistycznej agentów
❌ logiki pamięci
❌ logiki wiadomości

MESSAGE_SYSTEM/
Główna odpowiedzialność:

Komunikacja wewnętrzna systemu

Odpowiada za:
wiadomości,
zdarzenia,
routing,
kolejki,
protokoły.
Może zawierać:
message.py

router.py

queue.py

validator.py
Nie może:

❌ wykonywać zadań
❌ podejmować decyzji AI
❌ przechowywać głównej pamięci

AGENT_SYSTEM/
Główna odpowiedzialność:

Zarządzanie inteligentnymi wykonawcami

Odpowiada za:
agentów,
role,
osobowości,
współpracę.
Może zawierać:
agents/

director_agent.py

planner_agent.py
Nie może:

❌ zarządzać bazą danych
❌ definiować globalnych protokołów

TASK_SYSTEM/
Główna odpowiedzialność:

Zarządzanie pracą systemu

Odpowiada za:
zadania,
harmonogram,
kolejki,
wykonanie.
Nie może:

❌ tworzyć agentów
❌ zarządzać pamięcią

MEMORY_SYSTEM/
Główna odpowiedzialność:

Pamięć doświadczeń SSI

Odpowiada za:
zapis wspomnień,
wyszukiwanie,
konsolidację.
Typy pamięci:
SHORT TERM

LONG TERM

EPISODIC

SEMANTIC
Nie może:

❌ wykonywać zadań
❌ sterować agentami

KNOWLEDGE_SYSTEM/
Główna odpowiedzialność:

Reprezentacja wiedzy

Odpowiada za:
wiedzę,
relacje,
reguły,
wnioskowanie.
Nie może:

❌ przechowywać logów systemowych
❌ zarządzać komunikacją

DATABASE/
Główna odpowiedzialność:

Warstwa trwałego przechowywania

Odpowiada za:
modele danych,
połączenia,
migracje.
Nie może:

❌ zawierać logiki biznesowej
❌ wykonywać decyzji AI

API/
Główna odpowiedzialność:

Kontrakty komunikacyjne

Odpowiada za:
interfejsy,
request,
response,
wersje API.
Nie może:

❌ wykonywać logiki modułów

WORKFLOW_ENGINE/
Główna odpowiedzialność:

Sterowanie procesami

Odpowiada za:
przepływy,
stany,
orkiestrację.
MODEL_SYSTEM/
Główna odpowiedzialność:

Obsługa modeli AI

Odpowiada za:
ładowanie modeli,
wybór modeli,
zarządzanie modelami.
SECURITY/
Główna odpowiedzialność:

Ochrona systemu

Odpowiada za:
autoryzację,
uwierzytelnianie,
szyfrowanie,
audyt.
EVOLUTION_ENGINE/
Główna odpowiedzialność:

Samorozwój systemu

Odpowiada za:
analizę,
ulepszenia,
eksperymenty,
migracje.
LOGS/
Główna odpowiedzialność:

Historia działania systemu

Odpowiada za:
zdarzenia,
błędy,
komunikację,
audyt.
DATA/
Główna odpowiedzialność:

Dane robocze

Odpowiada za:
dane wejściowe,
przetworzone dane,
cache.
DOCUMENTATION/
Główna odpowiedzialność:

Wiedza projektowa

Odpowiada za:
architekturę,
specyfikacje,
instrukcje.
TESTS/
Główna odpowiedzialność:

Kontrola jakości

Odpowiada za:
testy,
walidację,
regresję.
TOOLS/
Główna odpowiedzialność:

Narzędzia administracyjne

Odpowiada za:
migracje,
diagnostykę,
konserwację.
RUN/
Główna odpowiedzialność:

Operacje systemowe

Odpowiada za:
start,
stop,
restart,
monitoring.
Reguła dodawania nowego folderu

Nowy folder może powstać tylko gdy:

NOWA FUNKCJA

↓

NOWA ODPOWIEDZIALNOŚĆ

↓

NOWY MODUŁ

↓

NOWY FOLDER

Nie tworzymy folderów:

bez celu,
dla pojedynczego pliku,
jako tymczasowych magazynów.
Relacja z pozostałą dokumentacją
01_PROJECT_FILE_STRUCTURE_BOOTSTRAP

↓

02_ROOT_DIRECTORY_MAP

↓

03_FOLDER_RESPONSIBILITY_MAP

↓

04_FILE_NAMING_CONVENTION

↓

05_MODULE_LOCATION_MAP

↓

06_MODULE_DEPENDENCY_MAP
Cel końcowy

03_FOLDER_RESPONSIBILITY_MAP.md zapewnia, że SSI_SELF_DEVELOPMENT_ENGINE pozostaje uporządkowany podczas rozwoju.

Po wdrożeniu zasad:

każdy folder ma jasną rolę,
moduły nie mieszają odpowiedzialności,
rozwój jest skalowalny,
nowe funkcje mają swoje właściwe miejsce.

Jest to mapa granic architektonicznych SSI — dokument określający, gdzie kończy się jeden system i zaczyna drugi.