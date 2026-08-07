DOCUMENTATION_AI_DEVELOPMENT_SYSTEM
Opis:

Ten dokument definiuje standard tworzenia dokumentacji dla systemu SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest ustalenie jednolitej struktury wszystkich dokumentów, aby zarówno człowiek, jak i modele AI mogły szybko odnajdywać informacje, rozumieć zależności oraz wykorzystywać dokumentację podczas procesu budowy i rozwoju systemu.

Dokument określa zasady organizacji informacji, format dokumentów oraz wymagania dotyczące tworzenia dokumentacji przeznaczonej do pracy z AI.

Cel dokumentu

03_DOCUMENT_STRUCTURE_RULES.md odpowiada na pytania:

Jak powinien wyglądać każdy dokument SSI?
Jak dzielić informacje, aby AI łatwo je przetwarzało?
Jak unikać zbyt dużych i nieczytelnych dokumentów?
Jak zapewnić spójność całej dokumentacji?
Jak tworzyć dokumenty możliwe do dalszego rozwijania?
Główna zasada

Każdy dokument w SSI musi posiadać jasno określony cel.

Jeden dokument opisuje:

jeden system,
jeden moduł,
jeden proces,
jedną odpowiedzialność.

Nie tworzymy dokumentów zawierających wiele niezależnych tematów.

Zasada modularności dokumentacji

Dokumentacja jest budowana podobnie jak kod programu.

Nie tworzymy:

JEDEN_OGROMNY_DOKUMENT.md

Tworzymy:

SYSTEM

↓

MODUŁY

↓

FUNKCJE

↓

SZCZEGÓŁY

Przykład:

MEMORY_SYSTEM

├── MEMORY_OVERVIEW.md
├── SHORT_TERM_MEMORY.md
├── LONG_TERM_MEMORY.md
└── OPERATION_HISTORY.md
Standardowy format dokumentu

Każdy dokument powinien posiadać następującą strukturę:

1. Nazwa dokumentu

Określa czego dotyczy dokument.

Przykład:

TASK_QUEUE_MANAGER_SPECIFICATION
2. Opis

Krótka informacja:

czym jest element,
dlaczego istnieje,
jaka jest jego rola.
3. Cel

Opisuje:

jaki problem rozwiązuje,
jaki rezultat ma osiągnąć.
4. Odpowiedzialność

Określa:

za co odpowiada moduł,
jakie zadania wykonuje.
5. Zakres działania

Opisuje:

co obejmuje,
czego nie obejmuje.

Przykład:

Odpowiada:
- kolejność wykonywania zadań.

Nie odpowiada:
- generowanie kodu.
6. Dane wejściowe

Opisuje informacje wymagane do działania.

Przykład:

INPUT:

- task_description
- priority
- requirements
7. Dane wyjściowe

Opisuje rezultaty działania.

Przykład:

OUTPUT:

- task_status
- execution_result
- logs
8. Proces działania

Opisuje logikę działania.

Format:

START

↓

ANALIZA

↓

OPERACJA

↓

WYNIK

↓

ZAPIS
9. Integracje

Opisuje połączenia z innymi elementami.

Przykład:

TASK_QUEUE_MANAGER

współpracuje z:

- DIRECTOR_CORE
- PROGRAMMER_AGENT
- VALIDATION_AGENT
10. Dane przechowywane

Opisuje:

pliki,
JSON,
bazę danych,
pamięć.
11. Przykłady użycia

Pozwala AI szybciej zrozumieć zastosowanie.

12. Powiązane dokumenty

Każdy dokument powinien wskazywać dalsze źródła wiedzy.

Przykład:

Related:

- MEMORY_SYSTEM_SPECIFICATION
- TASK_MANAGEMENT_SYSTEM_SPECIFICATION
Zasady wielkości dokumentów

Dokumenty powinny być dzielone tak, aby AI mogło je łatwo analizować.

Zasady:

jeden główny temat na dokument,
unikanie powtarzania tych samych informacji,
dzielenie dużych opisów na mniejsze części,
tworzenie indeksów dla większych obszarów.
Hierarchia dokumentacji

Dokumentacja posiada poziomy:

POZIOM 1
SYSTEM

↓

POZIOM 2
DZIAŁ

↓

POZIOM 3
MODUŁ

↓

POZIOM 4
FUNKCJA

↓

POZIOM 5
IMPLEMENTACJA
Nazewnictwo plików

Nazwy muszą być:

jednoznaczne,
opisowe,
stałe.

Format:

NUMER_NAZWA_TYP.md

Przykłady:

05_TASK_MANAGEMENT_SYSTEM_SPECIFICATION.md

13_MEMORY_SYSTEM_SPECIFICATION.md

24_TESTING_SYSTEM_SPECIFICATION.md
Zasada aktualizacji dokumentacji

Każda zmiana systemu wymaga aktualizacji dokumentacji.

Proces:

ZMIANA KODU

↓

AKTUALIZACJA DOKUMENTACJI

↓

AKTUALIZACJA WERSJI

↓

ZAPIS HISTORII
Dokumentacja jako źródło prawdy

W SSI dokumentacja jest nadrzędnym źródłem informacji o projekcie.

Kod może się zmieniać.

Dokumentacja określa:

dlaczego coś istnieje,
jak powinno działać,
jakie są założenia.
Przygotowanie dokumentów dla AI

Dokument powinien być:

logicznie podzielony,
pozbawiony niepotrzebnych informacji,
jednoznaczny,
opisujący relacje,
zawierający przykłady.

AI musi móc odpowiedzieć:

Co to jest?
Po co istnieje?
Jak działa?
Z czym współpracuje?
Gdzie znaleźć więcej informacji?
Cel końcowy

03_DOCUMENT_STRUCTURE_RULES.md zapewnia, że cała dokumentacja SSI_SELF_DEVELOPMENT_ENGINE będzie tworzona w jednolity sposób i będzie skutecznie wykorzystywana przez modele AI.

Dzięki tym zasadom dokumentacja staje się nie tylko opisem projektu, ale uporządkowaną bazą wiedzy umożliwiającą długoterminowy rozwój systemu.