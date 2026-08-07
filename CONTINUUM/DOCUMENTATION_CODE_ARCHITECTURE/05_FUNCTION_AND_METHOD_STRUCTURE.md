Opis:

Ten dokument definiuje standard projektowania funkcji i metod w systemie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest opisanie, jak tworzyć funkcje, metody klas, procedury wewnętrzne oraz operacje wykonywane przez komponenty systemu.

Dokument odpowiada na pytanie:

"Jak powinny wyglądać funkcje i metody SSI, jakie mają odpowiedzialności oraz jak komunikują się między elementami systemu?"

Cel dokumentu

05_FUNCTION_AND_METHOD_STRUCTURE.md definiuje:

standard tworzenia funkcji,
standard tworzenia metod klas,
nazewnictwo funkcji,
parametry wejściowe,
wartości zwracane,
obsługę błędów,
dokumentowanie funkcji,
poziomy dostępu,
zasady testowania.
Rola dokumentu

Dokument jest przejściem:

CLASS DESIGN

↓

METHOD DESIGN

↓

FUNCTION IMPLEMENTATION

↓

EXECUTABLE CODE
Miejsce w dokumentacji
00_CODE_ARCHITECTURE_INDEX.md

↓

01_CODE_ARCHITECTURE_OVERVIEW.md

↓

02_SOURCE_CODE_STRUCTURE.md

↓

03_MODULE_INTERNAL_ARCHITECTURE.md

↓

04_CLASS_AND_OBJECT_MODEL.md

↓

05_FUNCTION_AND_METHOD_STRUCTURE.md

↓

06_INTERFACE_IMPLEMENTATION_MODEL.md
Główna zasada projektowania funkcji SSI

Każda funkcja musi posiadać:

CLEAR PURPOSE

+

DEFINED INPUT

+

DEFINED OUTPUT

+

CONTROLLED SIDE EFFECTS

+

ERROR HANDLING
Model funkcji SSI

Standard:

def function_name(
    input_data,
    configuration
):
    """
    Function description
    """

    validate()

    process()

    return result
Odpowiedzialność funkcji

Jedna funkcja = jedna główna odpowiedzialność.

Poprawnie:
validate_message()

save_memory()

calculate_priority()
Niepoprawnie:
process_everything()
Typy funkcji w SSI

Funkcje dzielą się na:

1. CORE FUNCTIONS

2. SERVICE FUNCTIONS

3. VALIDATION FUNCTIONS

4. DATA FUNCTIONS

5. EVENT FUNCTIONS

6. UTILITY FUNCTIONS
1. CORE FUNCTIONS
Lokalizacja:
module/core/
Odpowiedzialność:

Główna logika modułu.

Przykład:

execute_task()

initialize_system()

process_message()
2. SERVICE FUNCTIONS
Lokalizacja:
module/services/
Odpowiedzialność:

Operacje dostępne dla innych modułów.

Przykład:

create_agent()

store_memory()

load_model()
3. VALIDATION FUNCTIONS
Lokalizacja:
module/validators/
Odpowiedzialność:

Sprawdzanie poprawności danych.

Przykład:

validate_agent()

validate_task()

validate_message()
4. DATA FUNCTIONS
Lokalizacja:
repositories/
Odpowiedzialność:

Operacje na danych.

Przykład:

save()

load()

delete()

search()
5. EVENT FUNCTIONS
Lokalizacja:
events/
Odpowiedzialność:

Reakcje na zdarzenia.

Przykład:

on_agent_created()

on_task_completed()

on_memory_updated()
6. UTILITY FUNCTIONS
Lokalizacja:
utils/
Odpowiedzialność:

Pomocnicze operacje.

Przykład:

convert_data()

generate_id()

format_timestamp()
Struktura metody klasy

Metoda klasy powinna wyglądać:

class Agent:

    def execute_task(self, task):

        self.validate(task)

        result = self.process(task)

        self.update_state()

        return result
Rodzaje metod klas
Constructor Methods

Tworzenie obiektu.

Przykład:

__init__()
State Methods

Zmiana stanu obiektu.

Przykład:

change_status()
update_state()
Action Methods

Wykonywanie działań.

Przykład:

execute()

process()

run()
Query Methods

Pobieranie informacji.

Przykład:

get_status()

get_history()

get_configuration()
Nazewnictwo funkcji

SSI stosuje konwencję:

snake_case

Poprawnie:

create_agent()

load_memory()

send_message()

Nie:

CreateAgent()

loadMemory()
Nazwy funkcji muszą określać działanie

Dobre:

calculate_score()

validate_request()

update_memory()

Złe:

data()

manager()

process()
Parametry funkcji

Parametry powinny być:

minimalne,
jasno określone,
typowane.

Przykład:

def create_task(
    task_name: str,
    priority: int,
    owner_id: str
) -> Task:
Typowanie danych

SSI wykorzystuje type hints.

Przykład:

def load_agent(
    agent_id: str
) -> Agent:
Wartości zwracane

Każda funkcja powinna jasno określać wynik.

Przykład:

def validate_message(
    message
) -> bool:
Unikanie efektów ubocznych

Funkcja powinna:

INPUT

↓

PROCESS

↓

OUTPUT

Nie:

FUNCTION

↓

DATABASE

↓

GLOBAL STATE

↓

CONFIG CHANGE

↓

LOGGING

bez jawnego określenia.

Obsługa błędów funkcji

Każda funkcja musi definiować:

możliwe błędy,
sposób obsługi,
komunikat błędu.

Przykład:

try:

    process_task()

except TaskError:

    handle_error()
Dokumentowanie funkcji

Każda publiczna funkcja posiada opis:

def send_message(message):
    """
    Sends message through
    Message System.

    Args:
        message:
            Message object

    Returns:
        MessageResult
    """
Funkcje publiczne i prywatne
Publiczne:

Dostępne dla innych modułów.

Przykład:

create_agent()
Prywatne:

Tylko wewnątrz modułu.

Przykład:

_validate_internal_state()
Funkcje asynchroniczne

SSI wspiera operacje długotrwałe:

Przykład:

async def train_model():

    await execute_training()

Zastosowanie:

modele AI,
komunikacja,
kolejki,
zadania.
Funkcje event-driven

System wykorzystuje zdarzenia:

def on_message_received(event):

    process(event)
Testowanie funkcji

Każda funkcja powinna posiadać test:

function

↓

unit test

↓

integration test

Przykład:

test_create_agent()

test_invalid_task()

test_message_validation()
Przygotowanie pod AI Self Development

Jednolita struktura funkcji pozwala agentom AI:

analizować kod,
rozpoznawać działanie funkcji,
generować nowe metody,
wykrywać błędy.

Proces:

Function Analysis

↓

Dependency Mapping

↓

Improvement Proposal

↓

Code Generation

↓

Testing
Powiązanie z kolejnymi dokumentami
05_FUNCTION_AND_METHOD_STRUCTURE.md

↓

06_INTERFACE_IMPLEMENTATION_MODEL.md

↓

07_CODE_EXECUTION_FLOW.md

↓

08_RUNTIME_ARCHITECTURE.md
Cel końcowy

05_FUNCTION_AND_METHOD_STRUCTURE.md definiuje standard tworzenia najmniejszej jednostki wykonawczej SSI — funkcji i metod.

Po zastosowaniu zasad:

kod jest czytelny,
funkcje mają jasne zadania,
zależności są kontrolowane,
testowanie jest możliwe,
AI może analizować i rozwijać kod.

Jest to specyfikacja zachowania kodu SSI na poziomie pojedynczych operacji wykonywanych przez system.