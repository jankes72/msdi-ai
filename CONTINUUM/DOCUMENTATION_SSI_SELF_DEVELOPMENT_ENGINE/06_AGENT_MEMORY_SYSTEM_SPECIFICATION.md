SSI_SELF_DEVELOPMENT_ENGINE
Cel dokumentu:

określenie, jak każdy agent przechowuje informacje,
opisanie podziału pamięci krótkotrwałej i długotrwałej,
opisanie dodatkowej pamięci operacyjnej w plikach JSON,
określenie sposobu odzyskiwania wiedzy z poprzednich działań,
zapewnienie ciągłości pracy agentów pomimo ograniczeń modelu językowego.

Dokument opisuje, że każdy pracownik AI posiada własną przestrzeń pamięci:

dyrektor działu,
manager kolejki zadań,
programista wykonawczy,
tester,
analityk,
dokumentalista,
inne wyspecjalizowane role.

Każdy agent posiada trzy warstwy pamięci:

1. SHORT TERM MEMORY

Pamięć krótkotrwała.

Przechowuje aktualny kontekst pracy:

obecne zadanie,
aktualny etap projektu,
ostatnie decyzje,
bieżące problemy,
informacje przekazane przez inne agenty.

Przykład:

INTERNAL_CONTEXT/
 └── agents/
      └── developer/
           └── short_term_memory.json

Ta pamięć jest używana podczas aktualnego procesu wykonywania zadania.

2. LONG TERM MEMORY

Pamięć długotrwała.

Przechowuje:

doświadczenie agenta,
wykonane projekty,
rozwiązane problemy,
sprawdzone schematy działania,
wcześniejsze decyzje architektoniczne.

Przykład:

DEVELOPMENT_MEMORY/
 └── agents/
      └── developer/
           └── long_term_memory.json

Dzięki temu agent nie zaczyna każdej pracy od zera.

3. OPERATION MEMORY

Pamięć operacji.

Najważniejsza warstwa dla działu programistycznego.

Przechowuje historię wykonanych działań:

jakie zadanie zostało wykonane,
jaki problem wystąpił,
jakie rozwiązanie zastosowano,
jaki był wynik testów,
jakie pliki zostały zmienione.

Przykład:

DEVELOPMENT_MEMORY/
 └── operations/
      └── operation_history.json

Przykład wpisu:

{
 "operation":"create_task_system",
 "problem":"missing_task_queue",
 "solution":"created_task_manager",
 "result":"success",
 "files_changed":[
   "tasks/task_manager.py"
 ]
}
SYSTEM WYSZUKIWANIA DOŚWIADCZEŃ

Przed rozpoczęciem nowego zadania agent nie wykonuje wszystkiego od początku.

Proces:

Otrzymuje zadanie.
Analizuje wymagania.
Przeszukuje pamięć operacji.
Szuka podobnych przypadków.
Wykorzystuje wcześniejsze rozwiązania.
Dostosowuje je do obecnego problemu.

Przykład:

Agent otrzymuje:

"Utwórz system kolejki zadań."

Sprawdza:

operation_history.json

Znajduje:

"Tworzono wcześniej system kolejki modeli."

Agent wykorzystuje wcześniejsze doświadczenie zamiast projektować od początku.

INDYWIDUALNA PAMIĘĆ AGENTÓW

Każdy agent posiada własną pamięć.

Nie ma jednej wspólnej pamięci roboczej.

Dzięki temu:

programista pamięta kod,
tester pamięta błędy,
dokumentalista pamięta strukturę dokumentacji,
dyrektor pamięta decyzje projektowe.
ROLA MODELU JĘZYKOWEGO

Model Ollama sam z siebie nie posiada trwałej pamięci.

Dlatego system SSI_SELF_DEVELOPMENT_ENGINE dostarcza mu:

aktualny prompt,
pamięć krótką,
pamięć długą,
historię operacji,
dokumentację projektu.

Model działa jako "mózg wykonawczy", natomiast pamięć systemowa znajduje się poza modelem.

CEL SYSTEMU PAMIĘCI

Stworzenie środowiska, w którym agent:

rozwija doświadczenie,
uczy się na poprzednich działaniach,
nie powtarza tych samych błędów,
zachowuje ciągłość pracy,
może rozwijać własne procedury.