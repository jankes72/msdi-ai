Opis:

Ten dokument definiuje zasady współpracy, rozwoju i wprowadzania zmian w projekcie SSI_SELF_DEVELOPMENT_ENGINE.

Jego zadaniem jest określenie jak człowiek oraz AI Development Agents mogą poprawnie uczestniczyć w rozwoju systemu, zachowując spójność architektury, jakości kodu oraz dokumentacji.

Dokument odpowiada na pytanie:

"Jak należy dodawać zmiany do SSI, aby system rozwijał się kontrolowanie i zgodnie z założoną architekturą?"

Rola dokumentu

CONTRIBUTING.md jest instrukcją rozwoju projektu.

Nie opisuje:

architektury systemu,
implementacji modułów,
szczegółów kodu.

Do tego służą:

DOCUMENTATION_CODE_ARCHITECTURE

DOCUMENTATION_SSI_SELF_DEVELOPMENT_ENGINE

PROJECT_BUILD_PLAN

CONTRIBUTING definiuje:

JAK PRACOWAĆ

↓

JAK DODAWAĆ ZMIANY

↓

JAK WERYFIKOWAĆ

↓

JAK ZACHOWAĆ JAKOŚĆ
Lokalizacja

Plik znajduje się w katalogu głównym:

CONTINUUM

│
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── DOCUMENTATION_VERSION.md
├── SYSTEM_DOCUMENTATION_MAP.md
└── AI_READING_ORDER.md
Cel dokumentu

CONTRIBUTING.md zapewnia:

jednolity proces pracy,
kontrolę jakości zmian,
ochronę architektury,
współpracę AI i człowieka,
spójność dokumentacji.
Główna zasada projektu

Żadna zmiana nie jest tylko zmianą kodu.

Każda zmiana jest:

CODE CHANGE

+

DOCUMENTATION CHANGE

+

KNOWLEDGE UPDATE

+

VERSION HISTORY
Proces wprowadzania zmian

Standardowy workflow:

REQUEST

↓

ANALYSIS

↓

DOCUMENTATION REVIEW

↓

IMPLEMENTATION PLAN

↓

CODE CHANGE

↓

TESTING

↓

VALIDATION

↓

DOCUMENTATION UPDATE

↓

CHANGELOG UPDATE

↓

MERGE
1. Przygotowanie zmiany

Przed rozpoczęciem pracy należy:

sprawdzić aktualny stan projektu,
przeczytać odpowiednią dokumentację,
określić zależności,
przygotować plan.

Schemat:

UNDERSTAND FIRST

↓

MODIFY SECOND
2. Praca AI Agentów

Każdy agent AI musi:

1.

READ CONTEXT


2.

CHECK DOCUMENTATION


3.

UNDERSTAND ARCHITECTURE


4.

CREATE PLAN


5.

IMPLEMENT CHANGE


6.

RUN VALIDATION


7.

UPDATE KNOWLEDGE
3. Zasady zmian architektury

Zmiany architektury wymagają:

analizy wpływu,
aktualizacji dokumentacji,
aktualizacji map zależności,
zapisania decyzji.

Proces:

ARCHITECTURE CHANGE

↓

IMPACT ANALYSIS

↓

DOCUMENT UPDATE

↓

IMPLEMENTATION
4. Zasady zmian kodu

Każdy kod musi:

posiadać odpowiedzialny moduł,
przestrzegać struktury projektu,
posiadać testy,
posiadać dokumentację.

Nie wolno:

dodawać przypadkowych plików,
omijać istniejącej architektury,
tworzyć duplikatów funkcji.
5. Standard dokumentacji

Każdy nowy moduł wymaga:

MODULE DESCRIPTION

↓

ARCHITECTURE DESCRIPTION

↓

INTERFACE DESCRIPTION

↓

IMPLEMENTATION NOTES

↓

TEST DESCRIPTION
6. Standard nazw

Wszystkie elementy muszą przestrzegać:

nazw katalogów,
nazw plików,
nazw klas,
nazw funkcji,
wersjonowania.

Źródło:

DOCUMENTATION_PROJECT_STRUCTURE

↓

FILE_NAMING_CONVENTION.md
7. Testowanie zmian

Każda zmiana musi przejść:

UNIT TESTS

↓

INTEGRATION TESTS

↓

SYSTEM VALIDATION

↓

REGRESSION CHECK
8. Code Review

Przed zatwierdzeniem:

Sprawdzane są:

ARCHITECTURE

↓

CODE QUALITY

↓

SECURITY

↓

PERFORMANCE

↓

DOCUMENTATION
9. Pull Request / Change Request

Każda większa zmiana powinna zawierać:

TITLE

↓

DESCRIPTION

↓

PURPOSE

↓

IMPLEMENTATION DETAILS

↓

TEST RESULTS

↓

DOCUMENTATION UPDATED
10. Obsługa błędów

Błędy należy zgłaszać jako:

BUG REPORT

↓

ANALYSIS

↓

FIX

↓

TEST

↓

CHANGELOG
11. Zasady bezpieczeństwa

Nie wolno:

dodawać haseł,
publikować kluczy,
usuwać mechanizmów bezpieczeństwa,
omijać kontroli dostępu.
12. Zasady pracy z dokumentacją

Dokumentacja jest obowiązkowa.

Zmiana:

NEW FEATURE

↓

DOCUMENTATION UPDATE

Bez dokumentacji zmiana jest niekompletna.

13. Współpraca wielu agentów AI

Przy wielu agentach:

DIRECTOR CORE

↓

TASK ASSIGNMENT

↓

SPECIALIZED AGENT

↓

RESULT VALIDATION

↓

KNOWLEDGE UPDATE
14. Zasady commitów

Commit powinien jasno opisywać zmianę.

Format:

TYPE: DESCRIPTION

Przykłady:

ADD: new memory module

FIX: database connection issue

UPDATE: documentation structure

REFACTOR: agent communication layer
15. Branch Strategy

Przykład:

main

│

├── feature/

├── fix/

├── documentation/

└── experiment/
16. Eksperymenty AI

Eksperymenty muszą posiadać:

OBJECTIVE

↓

HYPOTHESIS

↓

IMPLEMENTATION

↓

RESULT

↓

CONCLUSION
17. Zasada stabilności SSI

Nie rozwijamy systemu przez przypadkowe zmiany.

Proces:

PLAN

↓

IMPLEMENT

↓

VERIFY

↓

INTEGRATE
Integracja z dokumentacją
CONTRIBUTING.md

↓

README.md

↓

AI_READING_ORDER.md

↓

PROJECT_BUILD_PLAN

↓

IMPLEMENTATION
Powiązanie z innymi dokumentami
CONTRIBUTING.md

↓

CHANGELOG.md

↓

DOCUMENTATION_CODE_ARCHITECTURE

↓

PROJECT_BUILD_PLAN

↓

CODE_VERSIONING_STRATEGY
Zasady końcowe

Każdy uczestnik projektu musi przestrzegać:

1. Understand before changing

2. Document every change

3. Test every implementation

4. Preserve architecture

5. Maintain project memory

6. Improve system quality
Cel końcowy

CONTRIBUTING.md zapewnia, że SSI_SELF_DEVELOPMENT_ENGINE rozwija się w sposób:

kontrolowany,
przewidywalny,
dokumentowany,
skalowalny,
zgodny z architekturą.

Jest to instrukcja współpracy i rozwoju całego ekosystemu SSI dla ludzi oraz autonomicznych agentów AI.