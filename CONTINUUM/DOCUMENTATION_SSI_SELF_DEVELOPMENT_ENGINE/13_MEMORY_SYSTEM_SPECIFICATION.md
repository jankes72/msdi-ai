SSI_SELF_DEVELOPMENT_ENGINE
Opis:

Ten dokument opisuje system pamięci wykorzystywany przez wszystkie elementy SSI_SELF_DEVELOPMENT_ENGINE.

Memory System jest dodatkową warstwą wiedzy działu programistycznego, która działa niezależnie od wbudowanej pamięci modelu językowego.

Celem systemu jest zapewnienie ciągłości pracy, zachowania doświadczenia oraz możliwości wykorzystania wcześniejszych rozwiązań.

Każdy pracownik AI w dziale posiada własny system pamięci dostosowany do swojej roli.

1. ROLA MEMORY SYSTEM

Memory System odpowiada za:

zapisywanie doświadczenia,
przechowywanie historii działań,
odzyskiwanie wcześniejszych rozwiązań,
analizę podobnych przypadków,
utrzymanie kontekstu projektu.

System pozwala agentowi sprawdzić:

"Czy wykonywałem już podobne zadanie?"

oraz:

"Jak zostało ono wcześniej rozwiązane?"

2. MIEJSCE W ARCHITEKTURZE

Przepływ:

MODEL AI

    ↓

MEMORY SYSTEM

    ↓

SHORT TERM MEMORY

    ↓

LONG TERM MEMORY

    ↓

OPERATION MEMORY

    ↓

PROJECT KNOWLEDGE
3. ZASADA DZIAŁANIA

Model językowy sam z siebie nie posiada pełnej historii projektu.

Dlatego przed wykonaniem zadania otrzymuje:

aktualny kontekst,
informacje z pamięci,
historię podobnych operacji,
wymagania zadania.

Dopiero wtedy podejmuje działanie.

4. RODZAJE PAMIĘCI

System posiada trzy główne warstwy:

1. SHORT TERM MEMORY

2. LONG TERM MEMORY

3. OPERATION MEMORY
5. SHORT TERM MEMORY
Cel:

Przechowywanie aktualnego kontekstu pracy.

Zawiera:

obecne zadanie,
aktualny etap,
ostatnie komunikaty,
aktywne decyzje,
tymczasowe informacje.

Przykład:

{
"current_task":"TASK_001",
"status":"development",
"current_file":"task_models.py",
"last_action":"created class"
}
6. LONG TERM MEMORY
Cel:

Przechowywanie trwałej wiedzy agenta.

Zawiera:

historię projektów,
poznane rozwiązania,
zasady pracy,
wcześniejsze decyzje.

Przykład:

{
"knowledge":
[
{
"problem":"JSON validation",
"solution":"python json.tool"
}
]
}
7. OPERATION MEMORY

Najważniejsza warstwa dla działu programistycznego.

Przechowuje historię wykonanych operacji.

Agent zapisuje:

co zrobił,
dlaczego,
jaki był wynik,
jakie błędy wystąpiły,
jak rozwiązano problem.

Przykład:

{
"operation":"Create Python module",
"files_created":
[
"tasks/task_models.py"
],
"result":"success",
"errors":[],
"solution":"standard class structure"
}
8. PAMIĘĆ KAŻDEGO AGENTA

Każdy agent posiada własną przestrzeń pamięci.

Struktura:

DEVELOPMENT_MEMORY/

agents/

    programmer_agent/

        short_term_memory.json
        long_term_memory.json
        operation_memory.json


    validation_agent/

        short_term_memory.json
        long_term_memory.json
        operation_memory.json


    documentation_agent/

        short_term_memory.json
        long_term_memory.json
        operation_memory.json
9. PAMIĘĆ DYREKTORA

Dyrektor posiada rozszerzoną pamięć.

Dodatkowo przechowuje:

historię całego projektu,
decyzje strategiczne,
plany rozwoju,
zależności między modułami.

Struktura:

DIRECTOR_MEMORY/

project_history.json

strategic_decisions.json

architecture_memory.json
10. WYSZUKIWANIE WIEDZY

Przed rozpoczęciem zadania agent wykonuje:

NEW TASK

↓

SEARCH MEMORY

↓

FIND SIMILAR CASE

↓

ANALYZE SOLUTION

↓

EXECUTE

Przykład:

Nowe zadanie:

"Utwórz moduł pamięci"

Agent sprawdza:

operation_memory.json

Znajduje:

"Podobny moduł został wykonany wcześniej."

Wykorzystuje:

strukturę,
sposób testowania,
rozwiązane problemy.
11. ZAPIS PO WYKONANIU ZADANIA

Po zakończeniu pracy agent zapisuje:

TASK COMPLETE

↓

UPDATE MEMORY

↓

SAVE OPERATION

↓

UPDATE KNOWLEDGE
12. SYSTEM UCZENIA SIĘ

Memory System pozwala na:

ograniczenie powtarzania błędów,
szybsze wykonywanie podobnych zadań,
budowanie doświadczenia.

Agent z czasem nie zaczyna od zera.

13. KONTROLA PAMIĘCI

Pamięć nie jest zmieniana przypadkowo.

Każdy zapis posiada:

źródło informacji,
datę,
autora,
powiązanie z zadaniem.

Przykład:

{
"source":"TASK_024",
"agent":"programmer_agent",
"date":"2026-08-06"
}
14. CZYSZCZENIE PAMIĘCI

System może wykonywać:

archiwizację,
kompresję,
usuwanie duplikatów.

Nie usuwa jednak:

ważnych decyzji,
historii błędów,
kluczowych rozwiązań.
15. INTEGRACJA Z MODELAMI OLLAMA

Model lokalny:

Qwen,
LLaMA,
inne modele Ollama,

otrzymują pamięć jako dodatkowy kontekst.

Schemat:

PROMPT

+

TASK CONTEXT

+

MEMORY RETRIEVAL

+

PROJECT DOCUMENTATION

↓

MODEL RESPONSE
16. PRZYSZŁA ROZBUDOWA

Aktualnie:

JSON MEMORY FILES

Docelowo:

VECTOR DATABASE

+

EMBEDDINGS

+

SEMANTIC SEARCH
17. CEL KOŃCOWY

Memory System tworzy doświadczenie całego działu programistycznego.

Dzięki niemu:

agenci pamiętają wcześniejszą pracę,
rozwiązania są ponownie wykorzystywane,
dyrektor zna historię projektu,
system rozwija się z każdym wykonanym zadaniem,
wiedza nie znika po restarcie modelu.

Memory System jest podstawą ciągłego rozwoju SSI_SELF_DEVELOPMENT_ENGINE.