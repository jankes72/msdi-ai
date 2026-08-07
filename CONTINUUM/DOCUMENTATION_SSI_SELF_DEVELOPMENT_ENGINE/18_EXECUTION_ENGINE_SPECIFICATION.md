SSI_SELF_DEVELOPMENT_ENGINE
Opis:

Ten dokument opisuje Execution Engine — silnik wykonawczy działu programistycznego SSI_SELF_DEVELOPMENT_ENGINE.

Execution Engine jest warstwą, która zamienia decyzje, plany i zadania przygotowane przez dyrektora oraz agentów w rzeczywiste operacje wykonywane na komputerze.

Jego zadaniem nie jest podejmowanie decyzji projektowych, ale bezpieczne wykonywanie zatwierdzonych działań.

1. ROLA EXECUTION ENGINE

Execution Engine odpowiada za:

wykonywanie operacji programistycznych,
komunikację z systemem operacyjnym,
obsługę plików,
uruchamianie testów,
wykonywanie poleceń,
zbieranie wyników,
raportowanie statusu.
2. MIEJSCE W ARCHITEKTURZE

Schemat:

SSI DIRECTOR

↓

PROGRAMMING DIRECTOR

↓

TASK QUEUE MANAGER

↓

AGENT COORDINATION SYSTEM

↓

EXECUTION ENGINE

↓

SYSTEM OPERATIONS
3. ZASADA DZIAŁANIA

Execution Engine nie tworzy własnych celów.

Otrzymuje:

konkretne zadanie,
instrukcję wykonania,
wymagane pliki,
ograniczenia.

Następnie wykonuje operację.

4. PRZYKŁADOWY PROCES

Zadanie:

"Utwórz moduł task_models.py"

Proces:

TASK RECEIVED

↓

CHECK REQUIREMENTS

↓

CREATE FILE

↓

WRITE CODE

↓

RUN TEST

↓

COLLECT RESULT

↓

REPORT
5. OBSŁUGA PLIKÓW

Execution Engine zarządza:

tworzeniem plików,
edycją plików,
usuwaniem plików,
sprawdzaniem struktury projektu.

Przykład:

CREATE:

tasks/task_models.py

CONTENT:

class Task:
    pass
6. SYSTEM WYKONYWANIA TESTÓW

Po zmianach:

CODE CHANGE

↓

TEST REQUEST

↓

EXECUTION ENGINE

↓

PYTHON TEST

↓

RESULT

Przykłady:

python tests/test_project_structure.py

python -m pytest
7. BEZPIECZEŃSTWO OPERACJI

Execution Engine kontroluje:

jakie polecenia mogą być wykonane,
jakie katalogi mogą być zmieniane,
czy operacja jest zgodna z zadaniem.
8. RAPORTOWANIE

Każda operacja generuje wynik:

{
"operation":"create_file",
"file":"tasks/task_models.py",
"status":"success",
"result":"created"
}
9. OBSŁUGA BŁĘDÓW

Jeżeli wystąpi problem:

Tworzony jest raport:

EXECUTION_ERROR_REPORT

Zawiera:

operację,
błąd,
moment wystąpienia,
możliwe rozwiązania.
10. INTEGRACJA Z PAMIĘCIĄ

Execution Engine zapisuje:

wykonane operacje,
błędy,
rozwiązania,
czas wykonania.

Dzięki temu system uczy się procedur.

11. PRACA Z MODELAMI OLLAMA

Model nie wykonuje wszystkiego sam.

Proces:

MODEL

↓

GENERUJE INSTRUKCJĘ

↓

EXECUTION ENGINE

↓

WYKONUJE

↓

MODEL OTRZYMUJE WYNIK
12. OBECNA WERSJA

Na jednym komputerze:

jedna operacja naraz,
jedna aktywna instancja modelu,
kolejka wykonania.
13. WERSJA SERWEROWA

Docelowo:

EXECUTION SERVER

↓

WORKER NODES

↓

TASK EXECUTION

↓

RESULT STORAGE
14. CEL KOŃCOWY

Execution Engine jest rękami działu programistycznego.

Dyrektor planuje.

Agenci analizują.

Programista tworzy.

Validation sprawdza.

Documentation opisuje.

Execution Engine wykonuje.