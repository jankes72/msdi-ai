Opis:

Ten dokument definiuje zasady tworzenia, modyfikowania oraz utrzymywania kodu źródłowego w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego celem jest zapewnienie, aby cały kod tworzony przez agentów AI był spójny, czytelny, bezpieczny, możliwy do rozwijania oraz zgodny z architekturą systemu.

Dokument określa nie tylko sposób pisania kodu, ale również proces podejmowania decyzji programistycznych przez AI, aby agent nie tworzył przypadkowych rozwiązań, tylko działał według ustalonych standardów.

Cel dokumentu

07_CODE_IMPLEMENTATION_RULES.md odpowiada na pytania:

Jak AI ma tworzyć kod?
Jak wygląda standard programowania w projekcie?
Jak dzielić kod na moduły?
Jak dokumentować funkcje i klasy?
Jak wykonywać zmiany w istniejącym kodzie?
Jak unikać błędów architektonicznych?
Jak zapewnić możliwość dalszego rozwoju systemu?
Główna zasada implementacji

Kod nie jest tworzony jako pojedyncze rozwiązanie.

Każdy element musi pasować do całej architektury.

Schemat:

REQUIREMENT

↓

ANALYSIS

↓

DESIGN

↓

IMPLEMENTATION

↓

TEST

↓

DOCUMENTATION

↓

MEMORY UPDATE

AI nie przechodzi bezpośrednio od problemu do kodu.

Zasada pierwszeństwa architektury

Przed napisaniem kodu AI musi sprawdzić:

czy istnieje już podobny moduł,
czy funkcja nie jest już zaimplementowana,
gdzie powinien znajdować się nowy element,
jakie komponenty zostaną dotknięte.

Proces:

CHECK EXISTING SYSTEM

↓

PLAN CHANGE

↓

IMPLEMENT
Zasada modułowości

Każdy moduł powinien posiadać jedną główną odpowiedzialność.

Nie tworzymy:

ONE FILE:

task handling

+

memory

+

communication

+

validation

Tworzymy:

TASK MODULE

MEMORY MODULE

COMMUNICATION MODULE

VALIDATION MODULE
Zasada separacji odpowiedzialności

Kod powinien być podzielony według funkcji:

Przykład:

director_core.py

↓

decyzje dyrektora


task_manager.py

↓

zarządzanie zadaniami


memory_manager.py

↓

obsługa pamięci

Jeden komponent nie powinien przejmować odpowiedzialności innych.

Standard tworzenia pliku

Każdy nowy plik powinien posiadać:

nazwę zgodną ze strukturą projektu,
opis celu,
autora/agenta tworzącego,
wersję,
zależności,
dokumentację funkcji.

Przykład:

"""
Module:
task_manager.py

Purpose:
Task lifecycle management.

Version:
1.0
"""
Standard klas

Każda klasa powinna mieć jasno określoną rolę.

Przykład:

Poprawnie:

class TaskManager:
    """
    Manages task creation and lifecycle.
    """

Niepoprawnie:

class SystemManager:
    """
    Does everything.
    """
Standard funkcji

Każda funkcja powinna:

mieć jedno zadanie,
posiadać opis,
posiadać określone wejście,
posiadać określone wyjście.

Przykład:

def create_task(task_data):
    """
    Creates new task object.

    Input:
        task_data

    Output:
        Task object
    """
Zasada czytelności kodu

Kod tworzony przez AI musi być zrozumiały dla:

innych agentów,
przyszłych wersji AI,
człowieka programisty.

Obowiązuje:

jasne nazwy zmiennych,
brak nieopisanych skrótów,
komentarze przy złożonej logice.
Zasada kompatybilności wstecznej

Zmiana kodu nie może niszczyć istniejących funkcji.

Przed zmianą AI musi sprawdzić:

kto korzysta z danego modułu,
jakie dane są przekazywane,
czy istnieją zależności.

Proces:

OLD VERSION

↓

IMPACT ANALYSIS

↓

CHANGE

↓

TEST

↓

APPROVE
Zarządzanie błędami

Każdy moduł musi posiadać obsługę błędów.

Nie:

except:
    pass

Poprawnie:

try:
    execute_task()

except Exception as error:
    log_error(error)

Błędy muszą być:

zapisane,
opisane,
możliwe do analizy.
Logowanie operacji

Ważne działania muszą być zapisywane.

Przykłady:

wykonanie zadania,
zmiana pliku,
decyzja agenta,
błąd systemu.

Schemat:

ACTION

↓

LOG

↓

MEMORY

↓

KNOWLEDGE
Zasada testowania kodu

Kod nie jest uznany za gotowy bez sprawdzenia.

Proces:

CREATE CODE

↓

UNIT TEST

↓

INTEGRATION TEST

↓

VALIDATION

↓

ACCEPT
Zasada dokumentowania zmian

Każda większa zmiana wymaga aktualizacji:

dokumentacji technicznej,
mapy zależności,
pamięci projektu,
historii zmian.
Zasada używania istniejącej wiedzy

Przed implementacją AI powinno sprawdzić:

historię podobnych operacji,
wcześniejsze rozwiązania,
zapisane wzorce.

Proces:

NEW PROBLEM

↓

SEARCH MEMORY

↓

FIND SIMILAR CASE

↓

ADAPT SOLUTION
Ograniczenia AI podczas programowania

Agent programistyczny nie może:

zmieniać architektury bez zgody,
usuwać krytycznych plików,
ignorować dokumentacji,
pomijać testów,
tworzyć duplikatów istniejących funkcji.
Standard wersjonowania

Każdy moduł posiada:

numer wersji,
historię zmian,
kompatybilność.

Przykład:

{
"module":"TaskManager",
"version":"1.2",
"changes":"added priority handling"
}
Integracja z innymi dokumentami

07_CODE_IMPLEMENTATION_RULES.md współpracuje z:

06_DIRECTORY_STRUCTURE_PLAN

↓

08_AGENT_BUILD_WORKFLOW

↓

11_BUILD_VALIDATION_PLAN

↓

16_BUILD_CHANGE_MANAGEMENT
Cel końcowy

07_CODE_IMPLEMENTATION_RULES.md zapewnia, że kod tworzony przez AI będzie rozwijany w sposób kontrolowany i profesjonalny.

Dzięki temu:

każdy agent tworzy kod według tych samych zasad,
projekt pozostaje uporządkowany,
zmiany są bezpieczne,
system można rozwijać przez wiele lat,
przyszłe wersje AI mogą łatwo zrozumieć istniejący kod.

Dokument stanowi standard programistyczny całego SSI_SELF_DEVELOPMENT_ENGINE.