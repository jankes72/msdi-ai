Opis:

Ten dokument opisuje specyfikację agenta walidacyjnego (Validation Agent) działającego w ramach SSI_SELF_DEVELOPMENT_ENGINE.

Validation Agent jest niezależnym kontrolerem jakości działu programistycznego.

Jego zadaniem nie jest tworzenie kodu, lecz sprawdzanie, czy wykonane zadania spełniają wymagania, czy kod działa poprawnie oraz czy zmiany nie naruszają struktury projektu.

1. ROLA VALIDATION AGENT

Validation Agent odpowiada za:

sprawdzanie poprawności wykonanych zadań,
uruchamianie testów,
analizę błędów,
kontrolę zgodności ze specyfikacją,
wykrywanie niepotrzebnych zmian,
przygotowanie raportu jakości.

Główna zasada:

Programmer Agent tworzy rozwiązanie. Validation Agent sprawdza, czy rozwiązanie jest poprawne.

2. MIEJSCE W ARCHITEKTURZE

Przepływ:

PROGRAMMER AGENT
        |
        ↓
VALIDATION AGENT
        |
        ↓
RESULT REPORT
        |
        ↓
DIRECTOR AGENT

Validation Agent działa niezależnie od programisty.

Nie zatwierdza własnych zmian.

3. CEL AGENTA

Validation Agent ma zapewnić:

stabilność systemu,
brak przypadkowych zmian,
zgodność z dokumentacją,
wykrywanie błędów przed przejściem dalej.
4. PROCES WALIDACJI

Proces:

RECEIVE RESULT
        |
        ↓
LOAD REQUIREMENTS
        |
        ↓
CHECK FILES
        |
        ↓
RUN TESTS
        |
        ↓
ANALYZE ERRORS
        |
        ↓
CREATE REPORT
5. OTRZYMANIE ZADANIA DO SPRAWDZENIA

Validation Agent otrzymuje:

opis zadania,
pierwotne wymagania,
listę zmienionych plików,
kod wygenerowany przez programistę,
wynik testów wykonanych przez programistę.

Przykład:

TASK:

Create Task Model

FILES:

tasks/task_models.py

PROGRAMMER RESULT:

DONE
6. SPRAWDZENIE STRUKTURY PROJEKTU

Pierwszy etap:

Sprawdzenie:

czy wymagany plik istnieje,
czy znajduje się w odpowiednim katalogu,
czy nazwa jest poprawna,
czy nie utworzono dodatkowych elementów.

Przykład:

Wymagano:

tasks/task_models.py

Agent sprawdza:

PASS:
tasks/task_models.py exists

FAIL:
extra_file.py created
7. WALIDACJA KODU

Validation Agent analizuje:

składnię,
importy,
zależności,
zgodność klas i funkcji,
błędy wykonania.

Przykład:

Sprawdzenie:

from tasks.task_models import Task

Jeżeli import działa:

PASS

Jeżeli występuje błąd:

FAIL
8. TESTY AUTOMATYCZNE

Agent uruchamia odpowiednie testy:

Przykłady:

Test struktury:

python tests/test_project_structure.py

Test modułu:

python -c "from tasks.task_models import Task"

Test integracji:

python tests/test_task_system.py
9. ANALIZA BŁĘDÓW

Jeżeli test nie przejdzie, Validation Agent nie naprawia kodu.

Tworzy raport:

VALIDATION FAILED

TASK:
Create Task Model

ERROR:
ImportError

LOCATION:
tasks/task_models.py

CAUSE:
Missing class Task

ACTION:
Return to Programmer Agent
10. SYSTEM OCENY

Każde zadanie otrzymuje status:

PASSED

Wszystko poprawne.

STATUS:
VALIDATED
FAILED

Wykryto problem.

STATUS:
REJECTED
BLOCKED

Nie można kontynuować bez decyzji.

STATUS:
WAITING_DECISION
11. PAMIĘĆ VALIDATION AGENT

Validation Agent posiada własną pamięć.

Struktura:

DEVELOPMENT_MEMORY/

agents/

validation/

├── short_term_memory.json
├── long_term_memory.json
└── validation_history.json
12. HISTORIA WALIDACJI

Zapisywane są:

testowane moduły,
wykryte błędy,
typowe problemy,
poprawne rozwiązania.

Przykład:

{
 "module":"task_system",
 "error":"missing_import",
 "solution":"add_module_import",
 "result":"success"
}

Dzięki temu agent z czasem szybciej wykrywa powtarzające się problemy.

13. WSPÓŁPRACA Z PROGRAMMER AGENT

Schemat:

PROGRAMMER:

"Zrobiłem zadanie"


        ↓


VALIDATION:

"Sprawdzam"


        ↓


VALIDATION:

PASS → dalej

FAIL → zwrot do programisty
14. ZAKAZ SAMODZIELNEGO PROGRAMOWANIA

Validation Agent:

Nie:

tworzy nowych funkcji,
poprawia kodu za programistę,
zmienia architektury,
dodaje własnych rozwiązań.

Jego rola:

kontrola jakości, nie implementacja.

15. RAPORT KOŃCOWY

Przykład:

VALIDATION REPORT

TASK:
Create Task Model

FILES CHECK:
PASS

CODE CHECK:
PASS

TESTS:
PASS

MEMORY:
UPDATED

FINAL STATUS:
APPROVED
CEL KOŃCOWY

Validation Agent tworzy drugą warstwę kontroli w dziale programistycznym.

Dzięki niemu system:

nie przyjmuje błędnego kodu,
wykrywa problemy wcześniej,
zachowuje jakość projektu,
buduje historię doświadczeń,
może rozwijać się bez utraty kontroli.