Opis:

Ten dokument definiuje system wersjonowania całej dokumentacji projektu SSI_SELF_DEVELOPMENT_ENGINE.

Jego celem jest zapewnienie kontroli nad zmianami w dokumentacji, śledzenie rozwoju wiedzy projektowej oraz umożliwienie AI określenia, czy korzysta z aktualnych informacji podczas analizy i budowy systemu.

Dokument pełni rolę metadanych całego ekosystemu dokumentacji.

Cel dokumentu

DOCUMENTATION_VERSION.md odpowiada na pytania:

Jaka jest aktualna wersja dokumentacji?
Kiedy została wykonana ostatnia aktualizacja?
Jakie elementy zostały zmienione?
Czy dokumentacja jest zgodna ze stanem systemu?
Czy AI pracuje na aktualnej wiedzy?
Jaka wersja dokumentacji obowiązuje podczas budowy?
Rola dokumentu

Dokument jest sprawdzany jako jeden z pierwszych elementów podczas startu systemu AI.

Proces:

AI START

↓

READ DOCUMENTATION_VERSION

↓

CHECK VERSION

↓

LOAD KNOWLEDGE

↓

BEGIN WORK
Przykładowa struktura
{
    "system": "SSI_SELF_DEVELOPMENT_ENGINE",
    "documentation_name": "SSI_DOCUMENTATION",
    "version": "1.0.0",
    "status": "ACTIVE",
    "last_update": "2026-08-06",
    "phase": "DOCUMENTATION_FOUNDATION"
}
System wersjonowania

Dokumentacja korzysta z wersjonowania:

MAJOR.MINOR.PATCH

Przykład:

1.2.3
MAJOR VERSION
Duża zmiana

Zmienia podstawową strukturę systemu.

Przykłady:

zmiana architektury,
dodanie nowej warstwy systemu,
przebudowa głównych modułów.

Przykład:

1.0.0

↓

2.0.0
MINOR VERSION
Rozszerzenie funkcji

Dodanie nowych elementów bez niszczenia istniejącej struktury.

Przykłady:

nowy agent,
nowy system pamięci,
nowy dokument specyfikacji.

Przykład:

1.0.0

↓

1.1.0
PATCH VERSION
Drobne poprawki

Zmiany nie wpływające na architekturę.

Przykłady:

poprawa opisu,
korekta błędów,
aktualizacja przykładów.

Przykład:

1.1.0

↓

1.1.1
Statusy dokumentacji

Dokumentacja posiada status.

DEVELOPMENT

Dokumentacja tworzona.

STATUS:

DEVELOPMENT
REVIEW

Dokumentacja sprawdzana.

STATUS:

UNDER REVIEW
ACTIVE

Dokumentacja zatwierdzona.

STATUS:

ACTIVE
DEPRECATED

Dokumentacja nieaktualna.

STATUS:

DEPRECATED
Historia zmian dokumentacji

Każda aktualizacja jest zapisywana.

Przykład:

{
    "version":"1.1.0",
    "date":"2026-08-10",
    "changes":[
        "Added Agent Coordination documentation",
        "Updated architecture map"
    ]
}
Powiązanie wersji dokumentacji z kodem

Dokumentacja musi odpowiadać wersji systemu.

Przykład:

DOCUMENTATION

VERSION 1.0


SYSTEM CODE

VERSION 1.0

Nie powinno istnieć:

DOCUMENTATION 2.0

+

CODE 1.0

bo AI może otrzymać błędną wiedzę.

Kontrola zgodności

Przed rozpoczęciem pracy AI sprawdza:

DOCUMENTATION VERSION

↓

SYSTEM VERSION

↓

COMPATIBILITY CHECK

↓

ALLOW EXECUTION
Dokumentacja jako pamięć systemowa

W SSI dokumentacja jest traktowana jako część pamięci długoterminowej.

Schemat:

CHANGE

↓

DOCUMENT UPDATE

↓

VERSION UPDATE

↓

KNOWLEDGE UPDATE
Integracja z innymi dokumentami

DOCUMENTATION_VERSION.md współpracuje z:

README.md

↓

SYSTEM_DOCUMENTATION_MAP.md

↓

AI_READING_ORDER.md

↓

DOCUMENTATION_EVOLUTION.md

↓

CHANGE_MANAGEMENT_SYSTEM_SPECIFICATION.md
Cel końcowy

DOCUMENTATION_VERSION.md zapewnia, że SSI_SELF_DEVELOPMENT_ENGINE zawsze posiada kontrolowaną i aktualną bazę wiedzy.

Dzięki temu AI:

wie, z jakiej dokumentacji korzysta,
wykrywa nieaktualne informacje,
śledzi rozwój projektu,
zachowuje historię zmian,
może bezpiecznie rozwijać system.

Dokument jest systemem kontroli wersji wiedzy projektowej SSI_SELF_DEVELOPMENT_ENGINE.