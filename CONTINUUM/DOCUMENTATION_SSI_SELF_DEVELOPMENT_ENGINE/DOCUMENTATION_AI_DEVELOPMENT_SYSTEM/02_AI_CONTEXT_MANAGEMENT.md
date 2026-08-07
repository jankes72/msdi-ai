DOCUMENTATION_AI_DEVELOPMENT_SYSTEM
Opis:

Ten dokument definiuje sposób zarządzania kontekstem pracy modeli AI w systemie SSI_SELF_DEVELOPMENT_ENGINE.

Jego celem jest określenie, w jaki sposób agenci AI otrzymują informacje potrzebne do wykonania zadań, jak unikać przeciążenia kontekstu oraz jak zapewnić ciągłość pracy pomiędzy kolejnymi operacjami.

Dokument opisuje zasady dostarczania wiedzy do modeli AI tak, aby mogły działać jako wyspecjalizowani pracownicy systemu, a nie jako jednorazowe generatory odpowiedzi.

Cel dokumentu

02_AI_CONTEXT_MANAGEMENT.md odpowiada na pytania:

Jak AI otrzymuje informacje potrzebne do pracy?
Jak wybierane są dokumenty przekazywane do modelu?
Jak zarządzać ograniczonym oknem kontekstowym?
Jak zachować ciągłość projektu?
Jak oddzielić informacje chwilowe od trwałej wiedzy?
Główna zasada zarządzania kontekstem

Model AI nie powinien otrzymywać całej wiedzy systemu jednocześnie.

Zamiast tego system stosuje warstwowe dostarczanie informacji:

CAŁA WIEDZA SSI

↓

INDEKS DOKUMENTACJI

↓

KONKRETNY MODUŁ

↓

AKTUALNE ZADANIE

↓

KONTEKST OPERACYJNY

AI otrzymuje tylko te informacje, które są potrzebne w danym momencie.

Problem ograniczonego kontekstu

Każdy model językowy posiada ograniczoną ilość informacji, które może jednocześnie analizować.

Przeciążenie kontekstu powoduje:

utratę ważnych informacji,
pomijanie szczegółów,
błędne decyzje,
mieszanie różnych zadań,
spadek jakości kodu.

Dlatego SSI wykorzystuje system zarządzania kontekstem.

Warstwy kontekstu AI

System wykorzystuje kilka poziomów informacji.

1. Kontekst systemowy

Najwyższy poziom informacji.

Zawiera:

wizję SSI,
główne cele,
zasady działania,
architekturę ogólną.

Przykład:

SSI_SELF_DEVELOPMENT_ENGINE

↓

system autonomicznego rozwoju oprogramowania
2. Kontekst działu

Informacje dotyczące konkretnego oddziału.

Przykład:

Dział programistyczny:

zasady pracy,
dostępne narzędzia,
role agentów,
procedury.
3. Kontekst agenta

Informacje potrzebne konkretnemu agentowi.

Przykład:

Programmer Agent:

generowanie kodu,
standardy programowania,
sposób komunikacji.

Validation Agent:

testowanie,
analiza błędów,
kontrola jakości.
4. Kontekst zadania

Najbardziej aktualne informacje.

Zawiera:

aktualne zadanie,
wymagania,
pliki do zmiany,
oczekiwany rezultat.
5. Kontekst pamięci operacyjnej

Informacje z wcześniejszych działań.

Przykłady:

podobne wykonane zadania,
wcześniejsze rozwiązania,
znane problemy.
Struktura przekazywania informacji

Przed wykonaniem zadania AI otrzymuje:

SYSTEM CONTEXT

+

AGENT CONTEXT

+

TASK CONTEXT

+

RELEVANT MEMORY

+

REQUIRED DOCUMENTATION

Dopiero wtedy wykonuje operację.

Zarządzanie pamięcią krótkotrwałą

Pamięć krótkotrwała przechowuje:

aktualną rozmowę,
obecne zadanie,
bieżące decyzje,
tymczasowe wyniki.

Przykład:

{
"current_task":"create task queue",
"status":"implementation",
"temporary_notes":[]
}

Po zakończeniu zadania informacje mogą zostać przetworzone do pamięci długotrwałej.

Zarządzanie pamięcią długotrwałą

Pamięć długotrwała przechowuje:

ważne decyzje,
rozwiązania,
historię projektów,
wiedzę operacyjną.

Przykład:

{
"operation":"created configuration module",
"solution":"used JSON configuration files",
"result":"successful"
}
Kontekst dynamiczny

Kontekst AI nie jest stały.

Jest budowany dynamicznie przed każdą operacją.

Proces:

NOWE ZADANIE

↓

ANALIZA WYMAGAŃ

↓

WYBÓR INFORMACJI

↓

BUDOWA KONTEKSTU

↓

URUCHOMIENIE MODELU

↓

ANALIZA WYNIKU
Zasada minimalnego wymaganego kontekstu

AI powinno otrzymać:

najmniejszą ilość informacji potrzebną do poprawnego wykonania zadania.

Nie:

Załaduj całą dokumentację.

Tylko:

Załaduj dokumentację dotyczącą tego modułu i jego zależności.

Historia kontekstu

System zapisuje:

jakie informacje zostały użyte,
jakie dokumenty były aktywne,
jaki model wykonywał zadanie,
jaki był rezultat.

Pozwala to później analizować jakość procesu.

Kontrola jakości kontekstu

Przed wysłaniem zadania do modelu system sprawdza:

czy posiada wymagane informacje,
czy dokumentacja jest aktualna,
czy nie brakuje zależności,
czy zadanie jest jednoznaczne.
Integracja z innymi systemami

System zarządzania kontekstem współpracuje z:

DOCUMENTATION SYSTEM

↓

MEMORY SYSTEM

↓

TASK MANAGEMENT SYSTEM

↓

DIRECTOR SYSTEM

↓

AGENT SYSTEM
Cel końcowy

02_AI_CONTEXT_MANAGEMENT.md definiuje mechanizm, który pozwala SSI_SELF_DEVELOPMENT_ENGINE wykorzystywać modele językowe efektywnie pomimo ograniczeń ich pamięci roboczej.

Dzięki temu AI:

nie traci kontekstu projektu,
otrzymuje tylko potrzebne informacje,
może pracować etapami,
może rozwijać system długoterminowo,
może korzystać z wcześniejszych doświadczeń.