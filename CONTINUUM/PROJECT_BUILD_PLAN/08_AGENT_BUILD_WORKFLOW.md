Opis:

Ten dokument definiuje sposób organizacji pracy agentów AI podczas procesu budowy SSI_SELF_DEVELOPMENT_ENGINE.

Jego celem jest opisanie, jak poszczególni agenci współpracują ze sobą, jak przekazują zadania, jaka jest kolejność wykonywania pracy oraz jak wygląda pełny cykl realizacji zadania od otrzymania polecenia aż do zakończenia i zapisania wiedzy.

Dokument jest instrukcją działania dla całego zespołu agentów AI.

Nie opisuje pojedynczego agenta, ale cały proces współpracy między agentami.

Cel dokumentu

08_AGENT_BUILD_WORKFLOW.md odpowiada na pytania:

Jak agent otrzymuje zadanie?
Kto decyduje, który agent pracuje?
W jakiej kolejności działają agenci?
Jak przekazywane są informacje?
Jak uniknąć wykonywania wielu sprzecznych operacji jednocześnie?
Jak wygląda kontrola pracy agentów?
Główna zasada pracy agentów

Agenci AI nie działają niezależnie i chaotycznie.

Cały system działa według kontrolowanego przepływu:

DIRECTOR

↓

TASK QUEUE

↓

SELECT AGENT

↓

EXECUTE TASK

↓

VALIDATION

↓

DOCUMENTATION

↓

MEMORY UPDATE
Zasada kolejki pracy

Najważniejszą zasadą jest:

Jeden proces wykonawczy w danym momencie.

Nie uruchamia się wielu modeli AI jednocześnie bez kontroli.

Powód:

ograniczenia sprzętowe,
możliwość konfliktów,
utrata kontekstu,
sprzeczne zmiany.

Przykład:

Nie:

PROGRAMMER AGENT
        +
VALIDATION AGENT
        +
DOCUMENTATION AGENT

wszyscy pracują jednocześnie

Poprawnie:

TASK QUEUE

↓

PROGRAMMER AGENT

↓

VALIDATION AGENT

↓

DOCUMENTATION AGENT
Główny cykl pracy agenta

Każde zadanie przechodzi przez określony workflow.

ETAP 1 — TASK RECEIVED

Otrzymanie zadania.

Źródło:

SSI DIRECTOR

lub

PROGRAMMING DIRECTOR

Informacje:

cel,
wymagania,
priorytet,
ograniczenia.
ETAP 2 — TASK ANALYSIS

Analiza zadania.

Agent sprawdza:

dokumentację,
istniejący kod,
pamięć projektu,
zależności.

Proces:

TASK

↓

ANALYSIS

↓

UNDERSTANDING
ETAP 3 — TASK PLANNING

Tworzenie planu wykonania.

Plan zawiera:

kroki działania,
potrzebne pliki,
wymagane moduły,
sposób testowania.
ETAP 4 — AGENT SELECTION

Dyrektor wybiera odpowiedniego agenta.

Przykład:

ANALYSIS TASK

↓

ARCHITECTURE AGENT


CODE TASK

↓

PROGRAMMER AGENT


TEST TASK

↓

VALIDATION AGENT
ETAP 5 — EXECUTION

Agent wykonuje swoją część pracy.

Może:

tworzyć pliki,
analizować,
pisać kod,
wykonywać testy.

Każda operacja jest rejestrowana.

ETAP 6 — VALIDATION

Po wykonaniu zadanie jest sprawdzane.

Kontrola:

poprawność działania,
zgodność z wymaganiami,
brak konfliktów.
ETAP 7 — DOCUMENTATION UPDATE

Po zaakceptowaniu:

aktualizowane są:

dokumenty,
historia zmian,
wiedza projektu.
ETAP 8 — MEMORY UPDATE

System zapisuje doświadczenie.

Schemat:

TASK RESULT

↓

LESSON

↓

MEMORY

↓

FUTURE USE
Role agentów w workflow
Director Agent

Odpowiada za:

decyzje,
priorytety,
przydzielanie pracy.

Nie wykonuje kodu.

Requirement Analysis Agent

Odpowiada za:

analizę wymagań,
określenie celu,
przygotowanie specyfikacji.
Architecture Agent

Odpowiada za:

projekt systemu,
zależności,
strukturę.
Programmer Agent

Odpowiada za:

implementację,
modyfikację kodu,
tworzenie plików.
Validation Agent

Odpowiada za:

testy,
kontrolę jakości,
wykrywanie błędów.
Documentation Agent

Odpowiada za:

aktualizację dokumentacji,
opis zmian,
utrzymanie wiedzy.
Communication między agentami

Agenci nie komunikują się bezpośrednio chaotycznie.

Komunikacja odbywa się przez system:

COMMUNICATION SYSTEM

↓

MESSAGE PROTOCOL

↓

TARGET AGENT

Każdy komunikat posiada:

nadawcę,
odbiorcę,
cel,
dane,
status.
Zarządzanie konfliktem

Jeżeli dwa zadania wymagają tego samego zasobu:

system:

blokuje konflikt,
ustala kolejność,
wykonuje zadania po kolei.

Przykład:

TASK A

edytuje file.py


TASK B

chce edytować file.py

Decyzja:

QUEUE CONTROL

↓

TASK A

↓

TASK B
Statusy zadania

Każde zadanie posiada stan:

CREATED

↓

ANALYZING

↓

PLANNED

↓

EXECUTING

↓

VALIDATING

↓

COMPLETED

↓

MEMORY STORED
Awaria agenta

Jeżeli agent nie wykona zadania:

System:

zapisuje błąd,
zachowuje stan,
analizuje problem,
przekazuje ponownie lub zmienia strategię.

Schemat:

ERROR

↓

ANALYSIS

↓

RECOVERY

↓

RETRY
Integracja z innymi dokumentami

08_AGENT_BUILD_WORKFLOW.md współpracuje z:

07_CODE_IMPLEMENTATION_RULES

↓

09_TASK_IMPLEMENTATION_SEQUENCE

↓

11_BUILD_VALIDATION_PLAN

↓

12_TESTING_IMPLEMENTATION_PLAN

↓

14_MEMORY_AND_KNOWLEDGE_BUILD_PLAN
Cel końcowy

08_AGENT_BUILD_WORKFLOW.md zapewnia, że cały zespół AI działa jak jeden kontrolowany dział programistyczny.

Dzięki temu:

zadania są wykonywane w kolejności,
agenci nie powodują chaosu,
każdy agent zna swoją rolę,
informacje nie giną,
system zachowuje historię pracy,
budowa może być kontynuowana nawet po przerwie.

Dokument jest procedurą operacyjną współpracy całego zespołu agentów AI podczas tworzenia SSI_SELF_DEVELOPMENT_ENGINE.