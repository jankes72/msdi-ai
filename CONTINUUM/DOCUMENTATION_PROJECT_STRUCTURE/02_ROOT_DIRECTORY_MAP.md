Opis:

Ten dokument definiuje mapę głównego katalogu projektu SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest przedstawienie wszystkich elementów znajdujących się na najwyższym poziomie repozytorium oraz określenie ich odpowiedzialności w całej architekturze systemu.

Dokument odpowiada na pytanie:

"Jak wygląda mapa głównego poziomu projektu i za co odpowiada każdy główny katalog?"

Cel dokumentu

02_ROOT_DIRECTORY_MAP.md definiuje:

strukturę katalogu głównego,
znaczenie każdego folderu,
granice odpowiedzialności modułów,
powiązanie katalogów z architekturą SSI,
zasady organizacji najwyższego poziomu projektu.
Rola dokumentu

Dokument jest mapą nawigacyjną całego repozytorium.

Każdy programista, agent AI lub moduł systemu powinien móc na jego podstawie określić:

gdzie znajduje się dany komponent,
gdzie należy dodać nowe elementy,
którego katalogu nie należy naruszać.
Główny katalog projektu
SSI_SELF_DEVELOPMENT_ENGINE/

Jest to root całego systemu.

Wszystkie elementy SSI muszą znajdować się wewnątrz tego katalogu.

Struktura ROOT
SSI_SELF_DEVELOPMENT_ENGINE/

│
├── CONFIG/
├── CORE/
├── MESSAGE_SYSTEM/
├── AGENT_SYSTEM/
├── TASK_SYSTEM/
├── MEMORY_SYSTEM/
├── KNOWLEDGE_SYSTEM/
├── DATABASE/
├── API/
├── WORKFLOW_ENGINE/
├── MODEL_SYSTEM/
├── SECURITY/
├── EVOLUTION_ENGINE/
├── LOGS/
├── DATA/
├── DOCUMENTATION/
├── TESTS/
├── TOOLS/
└── RUN/
Mapa odpowiedzialności
CONFIG/
Odpowiedzialność:

Centralna konfiguracja systemu.

Zawiera:

ustawienia SSI,
konfigurację modeli,
parametry baz danych,
ustawienia bezpieczeństwa,
konfigurację logowania.

Nie zawiera:

kodu wykonywalnego,
danych użytkowych.
CORE/
Odpowiedzialność:

Centralne jądro systemu.

Odpowiada za:

start systemu,
cykl życia,
zarządzanie stanem,
inicjalizację modułów,
komunikację bazową.

CORE jest najwyższym poziomem wykonawczym.

MESSAGE_SYSTEM/
Odpowiedzialność:

System komunikacji SSI.

Odpowiada za:

format wiadomości,
routing,
kolejki,
zdarzenia,
komunikację między modułami.

Jest odpowiednikiem "układu nerwowego" systemu.

AGENT_SYSTEM/
Odpowiedzialność:

Zarządzanie agentami AI.

Odpowiada za:

tworzenie agentów,
rejestr agentów,
stany agentów,
współpracę agentów.
TASK_SYSTEM/
Odpowiedzialność:

Zarządzanie zadaniami.

Odpowiada za:

tworzenie zadań,
kolejkę zadań,
planowanie,
wykonywanie,
historię zadań.
MEMORY_SYSTEM/
Odpowiedzialność:

Pamięć systemu.

Odpowiada za:

przechowywanie doświadczeń,
odzyskiwanie informacji,
konsolidację pamięci.
KNOWLEDGE_SYSTEM/
Odpowiedzialność:

Warstwa wiedzy.

Odpowiada za:

reprezentację wiedzy,
graf wiedzy,
reguły,
analizę zależności,
wnioskowanie.
DATABASE/
Odpowiedzialność:

Trwałe przechowywanie danych.

Odpowiada za:

modele danych,
połączenia,
migracje,
backupy.
API/
Odpowiedzialność:

Interfejs komunikacyjny systemu.

Odpowiada za:

komunikację modułów,
kontrakty API,
request/response,
wersjonowanie.
WORKFLOW_ENGINE/
Odpowiedzialność:

Sterowanie procesami.

Odpowiada za:

przepływy pracy,
stany procesów,
wykonywanie sekwencji działań.
MODEL_SYSTEM/
Odpowiedzialność:

Obsługa modeli AI.

Odpowiada za:

rejestr modeli,
ładowanie modeli,
wybór modelu,
zarządzanie zasobami AI.
SECURITY/
Odpowiedzialność:

Bezpieczeństwo całego systemu.

Odpowiada za:

uwierzytelnianie,
autoryzację,
szyfrowanie,
kontrolę dostępu,
audyt.
EVOLUTION_ENGINE/
Odpowiedzialność:

Mechanizm samorozwoju SSI.

Odpowiada za:

analizę systemu,
wykrywanie problemów,
generowanie ulepszeń,
testowanie zmian,
migrację wersji.
LOGS/
Odpowiedzialność:

Przechowywanie historii działania.

Zawiera:

logi systemowe,
logi wiadomości,
błędy,
historię ewolucji.
DATA/
Odpowiedzialność:

Dane robocze systemu.

Zawiera:

dane wejściowe,
dane przetworzone,
embeddingi,
dane pomocnicze.
DOCUMENTATION/
Odpowiedzialność:

Pełna dokumentacja SSI.

Struktura:

DOCUMENTATION/

├── PROJECT_STRUCTURE/
├── DATABASE/
├── API/
├── MESSAGE_SYSTEM/
├── MEMORY/
├── AGENTS/
└── EVOLUTION/
TESTS/
Odpowiedzialność:

Kontrola jakości.

Zawiera:

testy jednostkowe,
integracyjne,
systemowe,
regresji.
TOOLS/
Odpowiedzialność:

Narzędzia pomocnicze.

Zawiera:

migracje,
diagnostykę,
benchmarki,
administrację.
RUN/
Odpowiedzialność:

Sterowanie uruchomieniem systemu.

Zawiera:

start,
stop,
restart,
monitoring.
Zasada komunikacji katalogów

Architektura zależności:

                 CORE

                  |

     ----------------------------

     |          |              |

MESSAGE    DATABASE       SECURITY

     |

 -----------------

 |               |

AGENT        TASK

 |

MEMORY

 |

KNOWLEDGE

 |

EVOLUTION
Zasada granic odpowiedzialności

Każdy katalog:

posiada własną odpowiedzialność,
nie przejmuje funkcji innych modułów,
komunikuje się przez API lub Message System.

Przykład:

Niedozwolone:

AGENT_SYSTEM
    |
    └── bezpośredni zapis do DATABASE

Poprawnie:

AGENT_SYSTEM

↓

API

↓

DATABASE
Reguły rozbudowy ROOT

Dodanie nowego głównego modułu wymaga:

aktualizacji 02_ROOT_DIRECTORY_MAP.md,
określenia odpowiedzialności,
określenia zależności,
dodania dokumentacji,
zatwierdzenia architektury.
Powiązanie z innymi dokumentami
01_PROJECT_FILE_STRUCTURE_BOOTSTRAP.md

↓

02_ROOT_DIRECTORY_MAP.md

↓

03_FOLDER_RESPONSIBILITY_MAP.md

↓

05_MODULE_LOCATION_MAP.md

↓

06_MODULE_DEPENDENCY_MAP.md
Cel końcowy

02_ROOT_DIRECTORY_MAP.md tworzy mapę głównego terenu SSI.

Po przeczytaniu dokumentu wiadomo:

jakie istnieją główne obszary systemu,
gdzie znajduje się każdy moduł,
jaka jest jego rola,
jakie są granice odpowiedzialności.

Jest to pierwsza mapa nawigacyjna całego repozytorium SSI_SELF_DEVELOPMENT_ENGINE.