SSI_SELF_DEVELOPMENT_ENGINE
Opis:

Ten dokument opisuje Requirement Analysis Agent — agenta odpowiedzialnego za analizę wymagań w ramach SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest odbieranie informacji o nowych potrzebach systemu, analizowanie ich oraz przygotowanie dokładnego opisu wymagań przed rozpoczęciem projektowania i programowania.

Agent działa jako pierwsza warstwa analizy technicznej.

Nie tworzy kodu.

Jego zadaniem jest zrozumienie co ma zostać zbudowane i jakie warunki musi spełniać rozwiązanie.

1. ROLA REQUIREMENT ANALYSIS AGENT

Agent odpowiada za:

analizę nowych zgłoszeń,
rozpoznanie celu zadania,
określenie wymagań funkcjonalnych,
określenie wymagań technicznych,
wykrywanie brakujących informacji,
przygotowanie dokumentu wymagań.
2. MIEJSCE W ARCHITEKTURZE

Schemat:

SSI DIRECTOR

↓

PROGRAMMING DIRECTOR

↓

PROJECT ANALYSIS SYSTEM

↓

REQUIREMENT ANALYSIS AGENT

↓

TASK MANAGEMENT SYSTEM

↓

PROGRAMMER AGENT
3. GŁÓWNE ZADANIE AGENTA

Agent odpowiada na pytania:

Co użytkownik/system chce osiągnąć?
Jaki problem ma zostać rozwiązany?
Jak powinno działać rozwiązanie?
Jakie dane są potrzebne?
Jakie są ograniczenia?
4. PROCES ANALIZY WYMAGAŃ

Proces:

NEW REQUEST

↓

INPUT ANALYSIS

↓

GOAL IDENTIFICATION

↓

FUNCTIONAL REQUIREMENTS

↓

TECHNICAL REQUIREMENTS

↓

MISSING INFORMATION CHECK

↓

REQUIREMENT DOCUMENT
5. ANALIZA WEJŚCIA

Agent otrzymuje:

opis problemu,
informacje od dyrektora SSI,
dokumentację systemu,
istniejącą architekturę,
wcześniejsze rozwiązania.

Przykład:

Informacja:

"Potrzebujemy systemu zarządzania agentami"

Agent analizuje:

Cel:
Kontrola pracy wielu agentów.

Potrzebne funkcje:
- rejestracja agentów,
- status pracy,
- komunikacja,
- kolejka zadań.
6. WYMAGANIA FUNKCJONALNE

Agent określa:

Co system musi robić.

Przykład:

SYSTEM MUSI:

- przyjmować zadania,
- przypisywać zadania agentom,
- zapisywać historię,
- raportować wyniki.
7. WYMAGANIA TECHNICZNE

Agent określa:

Jak rozwiązanie powinno działać.

Przykład:

Wymagania:

- Python,
- JSON jako pierwsza warstwa pamięci,
- kompatybilność z Ollama,
- integracja z Memory System.
8. WYKRYWANIE BRAKUJĄCYCH INFORMACJI

Agent sprawdza:

Czy można rozpocząć pracę.

Jeżeli brakuje danych:

Tworzy:

REQUIREMENT_CLARIFICATION_REQUEST

Przykład:

Problem:

Nie określono źródła danych.

Wymagana decyzja:

Które API ma być użyte?
9. DOKUMENT WYMAGAŃ

Agent generuje:

REQUIREMENT_DOCUMENT.md

Zawartość:

1. Cel projektu

2. Opis problemu

3. Wymagane funkcje

4. Ograniczenia

5. Zależności

6. Kryteria akceptacji
10. KRYTERIA AKCEPTACJI

Agent definiuje:

Jak sprawdzić, czy zadanie jest wykonane.

Przykład:

System uznaje się za gotowy gdy:

✓ moduł działa

✓ testy przechodzą

✓ dokumentacja istnieje

✓ integracja działa
11. WSPÓŁPRACA Z PROJECT ANALYSIS SYSTEM

Project Analysis System:

analizuje cały projekt.

Requirement Analysis Agent:

analizuje dokładne wymagania konkretnego zadania.

Schemat:

PROJECT ANALYSIS

"Budujemy system agentów"


↓

REQUIREMENT ANALYSIS

"System musi posiadać:
- rejestr agentów
- komunikację
- kolejkę"
12. WSPÓŁPRACA Z PROGRAMMER AGENT

Programmer Agent nie dostaje surowego pomysłu.

Otrzymuje:

TASK

+

REQUIREMENTS

+

ARCHITECTURE RULES

+

DOCUMENTATION

Dzięki temu kodowanie odbywa się według planu.

13. PAMIĘĆ REQUIREMENT AGENTA

Agent posiada własną pamięć:

DEVELOPMENT_MEMORY/

REQUIREMENTS/

├── requirements_history.json

├── solved_requirements.json

├── failed_requirements.json

└── patterns.json
14. WYKORZYSTANIE HISTORII

Przy podobnym zadaniu:

NEW REQUIREMENT

↓

SEARCH MEMORY

↓

FIND SIMILAR CASE

↓

ADAPT SOLUTION
15. INTEGRACJA Z MEMORY SYSTEM

Agent posiada:

Pamięć krótkotrwałą:

Aktualne zadanie.

Pamięć długotrwałą:

Historia analiz.

Pamięć operacyjną:

Zapis wykonanych procesów.

16. PRACA Z MODELAMI LLM

Model otrzymuje:

SYSTEM ROLE

+

PROJECT CONTEXT

+

CURRENT REQUIREMENT

+

MEMORY

+

RULES

Dzięki temu agent działa jako specjalista, a nie zwykły chatbot.

17. RAPORTOWANIE

Po analizie agent tworzy:

REQUIREMENT_ANALYSIS_REPORT.json

Przykład:

{
"task":"Agent communication system",
"complexity":"medium",
"missing_information":false,
"ready_for_development":true
}
18. OBECNA IMPLEMENTACJA

Pierwsza wersja:

Python,
JSON,
Markdown,
lokalny model Ollama,
pliki pamięci.
19. WERSJA DOCELOWA

Docelowo:

AUTONOMOUS REQUIREMENT ENGINE

+

SEMANTIC ANALYSIS

+

KNOWLEDGE GRAPH

+

AUTOMATIC SPECIFICATION GENERATION
20. CEL KOŃCOWY

Requirement Analysis Agent jest pierwszym analitykiem technicznym działu programistycznego.

Jego zadaniem jest zamiana ogólnego pomysłu:

"Potrzebujemy nowego narzędzia"

na dokładne wymaganie:

"System musi posiadać konkretne moduły, funkcje, dane wejściowe, sposób działania oraz kryteria zakończenia."

Dzięki temu programiści i pozostali agenci otrzymują jasne zadania, a rozwój SSI_SELF_DEVELOPMENT_ENGINE odbywa się kontrolowanie i bez chaosu.