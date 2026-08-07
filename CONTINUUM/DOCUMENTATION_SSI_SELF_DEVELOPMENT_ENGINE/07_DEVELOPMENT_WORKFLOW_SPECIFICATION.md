SSI_SELF_DEVELOPMENT_ENGINE
Opis:

Ten dokument opisuje cały proces pracy działu programistycznego SSI_SELF_DEVELOPMENT_ENGINE.

Celem dokumentu jest zdefiniowanie standardowego przepływu informacji i wykonywania zadań od momentu otrzymania zlecenia aż do zakończenia pracy i przekazania raportu.

Dział programistyczny działa jako niezależna jednostka wykonawcza, która otrzymuje cele i wymagania, a następnie samodzielnie organizuje proces ich realizacji.

DEVELOPMENT WORKFLOW

Proces składa się z następujących etapów:

INCOMING REQUEST
        |
        ↓
DIRECTOR ANALYSIS
        |
        ↓
TASK PLANNING
        |
        ↓
TASK QUEUE
        |
        ↓
AGENT EXECUTION
        |
        ↓
VALIDATION
        |
        ↓
DOCUMENTATION
        |
        ↓
REPORT
1. OTRZYMANIE ZADANIA

Źródłem zadania jest:

dyrektor główny SSI,
użytkownik,
wewnętrzny agent SSI,
system zapotrzebowania na nowe funkcje.

Dział programistyczny nie otrzymuje polecenia typu:

"napisz kod w Pythonie".

Otrzymuje:

cel,
wymaganie funkcjonalne,
problem do rozwiązania,
oczekiwany rezultat.

Przykład:

"System potrzebuje mechanizmu zarządzania zadaniami agentów."

2. ANALIZA DYREKTORA DZIAŁU

Po otrzymaniu informacji zadanie trafia do dyrektora działu programistycznego.

Dyrektor analizuje:

czego dotyczy zadanie,
jakie moduły będą potrzebne,
jakie istniejące elementy można wykorzystać,
jakie są zależności,
jakie zasoby będą wymagane.

Sprawdza również:

pamięć długotrwałą,
historię poprzednich projektów,
dokumentację systemu.
3. PLANOWANIE ZADANIA

Dyrektor dzieli duże zadanie na mniejsze elementy.

Przykład:

Zadanie:

"Stworzyć system zarządzania agentami."

Podział:

TASK 1
Projekt struktury danych

TASK 2
System kolejki

TASK 3
Komunikacja agentów

TASK 4
Testy

TASK 5
Dokumentacja

Każde zadanie otrzymuje:

opis,
priorytet,
wymagania,
przewidywany czas,
wymagane zasoby.
4. SYSTEM KOLEJKI ZADAŃ

Wszystkie zadania trafiają do kolejki.

System nie wykonuje wielu dużych operacji jednocześnie.

Powód:

ograniczone zasoby sprzętowe,
kontrola jakości,
brak konfliktów między zmianami,
zachowanie porządku projektu.

Przykład:

QUEUE

1. TASK_CREATE_MEMORY
   STATUS: RUNNING

2. TASK_CREATE_AGENT
   STATUS: WAITING

3. TASK_UPDATE_DOCUMENTATION
   STATUS: WAITING
5. MANAGER KOLEJKI

Za kolejkę odpowiada osobny agent zarządzający.

Jego zadania:

kontrola kolejności,
uruchamianie odpowiedniego wykonawcy,
zatrzymywanie konfliktowych operacji,
aktualizacja statusów.

Manager kolejki nie tworzy kodu.

Jego rolą jest organizacja pracy.

6. WYBÓR AGENTA WYKONAWCZEGO

Po rozpoczęciu zadania system wybiera odpowiedniego agenta.

Przykłady:

Programista:

developer_agent

Tester:

validation_agent

Dokumentacja:

documentation_agent

Analiza:

research_agent

Każdy agent posiada:

własną pamięć,
własne procedury,
własną historię działań.
7. PRZYGOTOWANIE KONTEKSTU

Przed wykonaniem zadania agent otrzymuje:

opis zadania,
wymagania,
dokumentację,
aktualną strukturę projektu,
pamięć krótkotrwałą,
pamięć długotrwałą,
historię podobnych operacji.

Powstaje dynamiczny prompt wykonawczy.

8. WYKONANIE ZADANIA

Agent wykonuje tylko przydzielone zadanie.

Zasady:

nie zmienia architektury bez zgody,
nie tworzy dodatkowych elementów,
nie wykonuje przyszłych etapów,
raportuje problemy.

Przykład:

Otrzymał:

"Utwórz model zadania."

Wykonuje tylko:

tasks/task_models.py

Nie tworzy:

dodatkowych klas,
nowych katalogów,
własnych rozwiązań.
9. WALIDACJA

Po zakończeniu pracy następuje sprawdzenie.

Testy obejmują:

istnienie plików,
poprawność kodu,
zgodność ze specyfikacją,
integrację z projektem.

Jeżeli test przejdzie:

STATUS:
SUCCESS

Jeżeli nie:

STATUS:
FAILED
10. AKTUALIZACJA PAMIĘCI

Po wykonaniu zadania system zapisuje:

wykonane operacje,
napotkane problemy,
rozwiązania,
zmienione pliki,
wyniki testów.

Informacje trafiają do:

DEVELOPMENT_MEMORY

Dzięki temu przyszłe zadania mogą korzystać z doświadczenia.

11. DOKUMENTACJA

Każda większa zmiana posiada dokumentację:

co zostało zrobione,
dlaczego zostało zrobione,
jak działa,
jak używać.

Dokumentacja jest przekazywana dalej do systemu SSI.

12. RAPORT KOŃCOWY

Po zakończeniu procesu dyrektor działu otrzymuje raport:

TASK:
Create Task System

STATUS:
COMPLETED

FILES:
tasks/task_models.py

TEST:
PASSED

MEMORY:
UPDATED

Następnie dyrektor przekazuje informację do głównego SSI.

ZASADA GŁÓWNA WORKFLOW

Dział programistyczny działa według zasady:

Plan → Podział → Kolejka → Wykonanie → Test → Dokumentacja → Pamięć → Raport

Każde zadanie przechodzi przez pełny cykl.

System nie działa chaotycznie i nie wykonuje wielu niekontrolowanych zmian jednocześnie.

Następny logiczny dokument:

08_PROGRAMMER_AGENT_SPECIFICATION.md

Opisuje konkretnego agenta programistę:

jak dostaje zadania,
jak generuje kod,
jak korzysta z pamięci,
jak komunikuje problemy,
jak współpracuje z testerem i dyrektorem.