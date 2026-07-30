# SPRINTY

---

# Sprint 1 – Audyt i przygotowanie integracji

### Zadanie

* Przeanalizuj wszystkie zależności V3 ↔ V4.
* Usuń błędne importy.
* Przygotuj strukturę katalogów integracyjnych.

### Wymagania

* Zgodność z `PROJECT_RULES.md`
* Nie zmieniać publicznego API bez uzasadnienia.
* Zachować kompatybilność wsteczną.

### Dziennik

Dodaj wpis do `PROJECT_JOURNAL.md`:

> Rozpoczęto implementację pełnej integracji V3 ↔ V4. Wykonano audyt architektury oraz przygotowano strukturę pod nowe komponenty.

---

# Sprint 2 – V3Config

### Zadanie

* Utwórz `V3Config`.
* Przenieś całą konfigurację integracyjną do jednej klasy.
* Dodaj walidację konfiguracji.

### Wymagania

* Zgodność z `PROJECT_RULES.md`
* Wszystkie wartości konfiguracyjne jako dataclass.

### Dziennik

> Dodano centralną konfigurację V3 odpowiedzialną za integrację z kolejnymi warstwami systemu.

---

# Sprint 3 – V3Integration

### Zadanie

* Zaimplementuj klasę `V3Integration`.
* Stwórz główny punkt wejścia integracji.
* Połącz MemoryManager, WorldManager oraz Intelligence.

### Wymagania

* Zgodność z `PROJECT_RULES.md`
* Zachować architekturę warstwową.

### Dziennik

> Dodano główny moduł integracyjny V3 odpowiedzialny za koordynację wszystkich komponentów.

---

# Sprint 4 – V3ToV4Bridge

### Zadanie

* Utwórz `V3ToV4Bridge`.
* Zaimplementuj eksport wiedzy z V3.
* Przygotuj konwersję struktur danych.

### Wymagania

* Zgodność z `PROJECT_RULES.md`
* Bridge nie może zawierać logiki agentów.

### Dziennik

> Dodano most komunikacyjny V3 → V4 odpowiedzialny za przekazywanie wiedzy. Implementacja obejmuje: transfer_knowledge(), ekstrakcję wiedzy z V3, konwersję światów do formatu V4, obsługę wzorców i subskrypcji agentów.
>
> **Status**: ✅ Zakończony (2026-07-28)

---

# Sprint 5 – Integracja World Integration

### Zadanie

* Rozbuduj `world_integration.py`.
* Dodaj obsługę SEND_TO_V4.
* Podłącz V3ToV4Bridge.

### Wymagania

* Zgodność z `PROJECT_RULES.md`
* Zachować pełną kompatybilność z V2.

### Dziennik

> Rozszerzono integrację światów o możliwość przekazywania danych do V4.

---

# Sprint 6 – Integracja Agent Core

### Zadanie

* Dodaj integrację V3 w `agent_core.py`.
* Udostępnij agentom World Memory.
* Udostępnij Pattern Memory.

### Wymagania

* Zgodność z `PROJECT_RULES.md`
* Agenci nie mogą bezpośrednio modyfikować pamięci V3.

### Dziennik

> Agenci V4 uzyskali dostęp do wiedzy zgromadzonej przez V3.

---

# Sprint 7 – Synchronizacja pamięci

### Zadanie

* Dodaj synchronizację pamięci V3 ↔ V4.
* Obsłuż aktualizacje wiedzy.
* Dodaj mechanizmy odświeżania.

### Wymagania

* Zgodność z `PROJECT_RULES.md`
* Synchronizacja musi być bezpieczna dla wielu agentów.

### Dziennik

> Dodano mechanizm synchronizacji wiedzy pomiędzy V3 i V4.

---

# Sprint 7.1 – Reprodukowalne środowisko uruchomieniowe

### Status

⏳ Do realizacji — priorytet P0

### Zadanie

* Ustal Python 3.11 jako wspieraną wersję interpretera.
* Dodaj `pyproject.toml` z konfiguracją projektu i narzędzi developerskich.
* Rozdziel zależności runtime, development i ML.
* Dodaj deterministyczny lockfile zależności.
* Przygotuj instrukcję utworzenia `.venv` i instalacji projektu z czystego checkoutu.
* Dodaj mały, wersjonowany fixture danych przeznaczony wyłącznie do testów.
* Zapewnij, że cały kod wymagany przez główny entrypoint jest śledzony przez Git.

### Wymagania

* Kod `pamiec_modeli_v2/**/*.py` nie może być wykluczony przez `.gitignore`.
* Dane, modele, archiwa i wyniki runtime nadal muszą pozostać ignorowane.
* `python -m pip check` musi kończyć się kodem `0`.
* Instalacja nie może zależeć od globalnego środowiska Python użytkownika.
* Dokumentacja uruchomienia musi używać rzeczywistej składni podkomend CLI.

### Kryteria akceptacji

- [ ] Czysty checkout daje się uruchomić według jednej udokumentowanej procedury.
- [ ] `python --version` zwraca wspieraną wersję 3.11.x.
- [ ] Instalacja z lockfile kończy się bez konfliktów zależności.
- [ ] Import `pamiec_modeli_v2.integration` działa bez ręcznej zmiany `PYTHONPATH`.
- [ ] Fixture danych jest wystarczający do smoke testu i nie zawiera danych produkcyjnych.

### Dziennik

> Status: oczekuje na implementację i potwierdzenie kryteriów akceptacji.

---

# Sprint 7.2 – Stabilizacja konfiguracji i przenośności

### Status

⏳ Do realizacji — priorytet P0

### Zadanie

* Napraw budowanie ścieżek w `SSI/config/paths.py`.
* Usuń podwójny prefiks `SSI/SSI`.
* Zastąp zakodowaną ścieżkę `D:\sts\aplikacjaTyperBetAi` konfiguracją przenośną.
* Usuń operacje I/O wykonywane podczas importu `warstwa5_generator`.
* Ujednolić konfigurację przez `pathlib.Path`.
* Domyślnie wyłącz feature flags modułów, które nie zostały zaimplementowane.
* Dodaj walidację konfiguracji podczas startu systemu.

### Wymagania

* Ścieżka główna projektu musi być ustalana względem pliku projektu albo jawnej zmiennej środowiskowej.
* Import modułu nie może tworzyć katalogów, plików ani handlerów logowania.
* Niezaimplementowane `strategy`, `laboratories`, `feedback` i `decision_engine` muszą mieć wartość `False`.
* Błędna konfiguracja musi powodować czytelny wyjątek z nazwą pola i wartością.

### Kryteria akceptacji

- [ ] `SSIPaths().get_absolute_path(...)` nie zwraca ścieżek zawierających `SSI/SSI`.
- [ ] Import wszystkich modułów `warstwa5_generator` działa poza komputerem autora.
- [ ] Testy ścieżek przechodzą na Windows i są niezależne od bieżącego katalogu roboczego.
- [ ] Uruchomienie import smoke nie zapisuje plików.
- [ ] Walidator odrzuca nieistniejące katalogi wymagane przez aktywne funkcje.

### Dziennik

> Status: oczekuje na implementację i potwierdzenie kryteriów akceptacji.

---

# Sprint 7.3 – Bezpieczeństwo współbieżności V4

### Status

⏳ Do realizacji — priorytet P0

### Zadanie

* Usuń zakleszczenie w `Agent.make_decision()`.
* Sprawdź ten sam wzorzec w `evaluate_result()` i `learn_from_experience()`.
* Zdefiniuj jedną politykę synchronizacji dla Agent, AgentManager, pamięci i osobowości.
* Ogranicz zakres sekcji krytycznych.
* Dodaj kontrolowane timeouty dla operacji agenta.
* Dodaj testy wielowątkowe synchronizacji V3 ↔ V4.

### Wymagania

* Metoda posiadająca lock nie może wywoływać publicznej metody próbującej przejąć ten sam niereentrantny lock.
* Każda operacja decyzyjna musi kończyć się sukcesem albo kontrolowanym błędem w określonym limicie czasu.
* Testy nie mogą polegać na `sleep()` jako mechanizmie synchronizacji.
* Błąd jednego agenta nie może blokować pozostałej populacji.
* Synchronizacja nie może pozwalać agentom bezpośrednio modyfikować pamięci V3.

### Kryteria akceptacji

- [ ] `make_decision()` kończy się w czasie krótszym niż 2 sekundy dla fixture testowego.
- [ ] `evaluate_result()` i `learn_from_experience()` nie powodują deadlocku.
- [ ] Test równoległej pracy minimum 10 agentów przechodzi deterministycznie.
- [ ] Timeout powoduje kontrolowany wyjątek i ustrukturyzowany log.
- [ ] Testy są uruchamiane wielokrotnie w CI w celu wykrywania race conditions.

### Dziennik

> Status: oczekuje na implementację; audyt wykazał reprodukowalne zakleszczenie przepływu decyzyjnego V4.

---

# Sprint 7.4 – Kontrakty i walidacja przepływu V2 → V3 → V4

### Status

⏳ Do realizacji — priorytet P0

### Zadanie

* Zdefiniuj wersjonowane kontrakty danych pomiędzy V2, V3 i V4.
* Ustal jeden `DataSplitPolicy` dla treningu, walidacji i obserwacji.
* Dodaj walidację wejścia i wyjścia każdej warstwy.
* Dodaj identyfikatory wersji datasetu, modelu, konfiguracji i wyniku.
* Zbuduj jeden cienki pionowy przepływ:
  `fixture → V2 → V3 → V4 → decyzja → wynik → feedback testowy`.
* Zdefiniuj politykę kompatybilności i migracji kontraktów.

### Wymagania

* Kontrakty nie mogą opierać się wyłącznie na niejawnych słownikach `Dict[str, Any]`.
* Każdy kontrakt musi mieć wersję, pola wymagane i walidację zakresów.
* Podział danych musi jawnie rozróżniać 50% trening, 10% walidację i 40% obserwację albo wskazywać inną zatwierdzoną politykę.
* Test nie może korzystać z danych produkcyjnych ani sieci.
* Ten sam input i seed muszą dawać powtarzalny wynik smoke testu.

### Kryteria akceptacji

- [ ] Kontrakty V2→V3 oraz V3→V4 posiadają testy pozytywne i negatywne.
- [ ] Niekompatybilna wersja danych jest odrzucana z czytelnym komunikatem.
- [ ] Pionowy smoke test przechodzi jedną komendą.
- [ ] Wynik zawiera lineage: wersję danych, modelu, konfiguracji i kodu.
- [ ] Polityka podziału danych jest identyczna w kodzie i dokumentacji.

### Dziennik

> Status: oczekuje na implementację i potwierdzenie kryteriów akceptacji.

---

# Sprint 7.5 – Obserwowalność i kontrola błędów

### Status

⏳ Do realizacji — priorytet P1

### Zadanie

* Wprowadź centralną konfigurację logowania.
* Zastąp `print()` w kodzie produkcyjnym loggerem.
* Zdefiniuj hierarchię wyjątków domenowych i infrastrukturalnych.
* Ogranicz szerokie `except Exception` do granic CLI i orchestracji.
* Dodaj health check oraz readiness check dla aktywnych modułów.
* Dodaj podstawowe metryki czasu, błędów, liczby decyzji i zużycia zasobów.
* Dodaj `correlation_id` dla pełnego przepływu V2→V4.

### Wymagania

* Logi muszą być zapisane w UTF-8 i mieć format strukturalny.
* Log nie może zawierać sekretów ani pełnych danych wejściowych użytkownika.
* Każdy przechwycony błąd krytyczny musi zachować traceback i prowadzić do niezerowego kodu procesu.
* Health check nie może zgłaszać modułu jako gotowego tylko na podstawie feature flag.

### Kryteria akceptacji

- [ ] Smoke test emituje wspólny `correlation_id` we wszystkich warstwach.
- [ ] Awaria zależności powoduje status `not ready`.
- [ ] CLI zwraca kod różny od zera dla błędów wykonania.
- [ ] Logi z polskimi znakami są poprawnie odczytywane jako UTF-8.
- [ ] Metryki rozróżniają sukces, kontrolowany błąd i timeout.

### Dziennik

> Status: oczekuje na implementację i potwierdzenie kryteriów akceptacji.

---

# Sprint 8 – Automatyczne testy i CI

### Status

⏳ Do realizacji — wcześniejsza deklaracja ukończenia nie została potwierdzona

### Zadanie

* Utwórz `tests/unit`, `tests/integration` oraz `tests/smoke`.
* Dodaj testy kontraktów i przepływu V2 → V3 → V4.
* Dodaj testy konfiguracji ścieżek, importów i entrypointów CLI.
* Zastąp wbudowane demonstracje właściwymi testami z asercjami.
* Napraw komendę `uruchom_system_v2.py test` albo zastąp ją wywołaniem pytest.
* Dodaj CI uruchamiane dla każdego pull requestu.
* Dodaj lint, type check, coverage, `pip check` i skan bezpieczeństwa.

### Wymagania

* Zgodność z `PROJECT_RULES.md`
* Wszystkie nowe klasy i poprawiane kontrakty muszą posiadać testy.
* Brak testów nie może być raportowany jako sukces.
* Każdy wyjątek podczas testów musi prowadzić do niezerowego kodu procesu.
* Testy muszą być deterministyczne i niezależne od sieci oraz danych produkcyjnych.
* CI musi używać izolowanego środowiska utworzonego z lockfile.
* Początkowa bramka coverage: pokrycie nie może spadać; dla krytycznych kontraktów docelowo minimum 80%.

### Kryteria akceptacji

- [ ] `python -m pytest` wykrywa i wykonuje testy.
- [ ] Testy unit, integration i smoke przechodzą na czystym checkout.
- [ ] Kontrolowany test awarii potwierdza niezerowy exit code.
- [ ] `compileall`, import smoke, lint, type check i `pip check` przechodzą.
- [ ] CI blokuje merge przy niepowodzeniu dowolnej bramki.
- [ ] Raport coverage jest publikowany jako artefakt CI.

### Dziennik

> Status skorygowany: audyt z 2026-07-30 nie znalazł test suite ani konfiguracji CI. Wbudowany runner kończy się błędem, ale zwraca kod `0`.

---

# Sprint 9 – Dokumentacja wykonywalna i źródło prawdy

### Status

⏳ Do realizacji — dokumentacja istnieje, lecz wymaga synchronizacji z implementacją

### Zadanie

* Utwórz `SSI_DOCUMENTATION/V3_V4_INTEGRATION.md`.
* Opisz faktyczną architekturę i wersjonowane kontrakty V2→V3→V4.
* Dodaj diagram przepływu danych i granice odpowiedzialności.
* Dodaj działające przykłady użycia zweryfikowane w CI.
* Zsynchronizuj statusy V2, V3 i V4 w README, mapie implementacji, dzienniku i sprintach.
* Przywróć `stuktura1.csv`–`stuktura4.csv` albo zastąp je wersjonowanym źródłem wymagań.
* Dodaj rejestr funkcjonalności ze statusami:
  `planned`, `implemented`, `tested`, `operational`.
* Dodaj ADR dla synchronizacji, persistence, polityki danych i granic modułów.

### Wymagania

* Zgodność z `PROJECT_RULES.md`
* Dokumentacja wyłącznie w języku polskim.
* Każda komenda w dokumentacji musi być automatycznie weryfikowana albo wskazana jako pseudokod.
* Status `tested` wymaga linku do testu, a `operational` do health checku i metryk.
* Dokumentacja nie może określać planowanego modułu jako aktywny.
* Wszystkie pliki tekstowe muszą używać UTF-8.

### Kryteria akceptacji

- [ ] Nie ma sprzecznych statusów V3 i V4 w dokumentacji.
- [ ] Każde wymaganie krytyczne ma identyfikator i powiązany test.
- [ ] Instrukcja uruchomienia działa na czystym checkout.
- [ ] Diagram odpowiada rzeczywistym importom i kierunkom przepływu.
- [ ] Kontrola linków, komend i kodowania przechodzi w CI.
- [ ] Dokument audytu pozostaje powiązany z pozycjami roadmapy.

### Dziennik

> Status skorygowany: dokumentacja architektoniczna jest rozbudowana, ale nie jest jeszcze zsynchronizowanym i wykonywalnym źródłem prawdy.

---

# Sprint 10 – Bramka gotowości do dalszego skalowania

### Status

⏳ Do realizacji — `NO-GO` według audytu z 2026-07-30

### Zadanie

* Wykonaj końcowy przegląd architektury.
* Usuń albo oznacz nieużywany i demonstracyjny kod.
* Ujednolić importy, konfigurację, logowanie i obsługę błędów.
* Zweryfikuj zgodność z dokumentacją.
* Przeprowadź pełny test pionowego przepływu V2→V3→V4.
* Wykonaj benchmark czasu i pamięci na reprezentatywnym fixture.
* Zweryfikuj zachowanie przy współbieżności i awarii zależności.
* Przeprowadź test backup/restore oraz migracji wersji kontraktu.
* Zamknij wszystkie ustalenia P0 audytu.
* Podejmij udokumentowaną decyzję `GO/NO-GO` przed implementacją V5.

### Wymagania

* Zgodność z `PROJECT_RULES.md`
* Nie pozostawiać kodu oznaczonego TODO ani FIX.
* Wszystkie bramki CI muszą przechodzić.
* Krytyczne kontrakty muszą mieć minimum 80% coverage.
* Nie może istnieć znany deadlock ani błąd maskowany kodem wyjścia `0`.
* Wszystkie aktywne moduły muszą posiadać health/readiness check.
* Benchmark musi mieć zatwierdzone limity czasu i pamięci.
* Dokumentacja i implementacja muszą mieć ten sam status funkcjonalności.

### Kryteria akceptacji

- [ ] Czysty checkout przechodzi bootstrap, testy i smoke test jedną udokumentowaną procedurą.
- [ ] Cały kod wymagany przez entrypoint jest śledzony przez Git.
- [ ] Przepływ V2→V3→V4 kończy się deterministyczną decyzją i feedbackiem.
- [ ] Test minimum 10 współbieżnych agentów przechodzi bez deadlocku.
- [ ] `pip check`, lint, type check, testy i skan bezpieczeństwa przechodzą.
- [ ] Health checks, logi i metryki potwierdzają gotowość operacyjną.
- [ ] Zespół zatwierdził raport zamknięcia ryzyk P0/P1.
- [ ] Decyzja `GO` ma dowody; brak dowodów automatycznie oznacza `NO-GO`.

### Dziennik

> Status skorygowany: projekt nie spełnia obecnie bramki skalowania. Sprint zostanie zamknięty dopiero po spełnieniu wszystkich kryteriów akceptacji i udokumentowaniu decyzji `GO`.
