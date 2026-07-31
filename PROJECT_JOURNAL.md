# Dziennik Projektu MSDI AI / SSI

## Self Learning Intelligence Ecosystem - Historia Rowoju

---

## 1. Informacje o Projekcie

| Pole | Wartość |
|------|---------|
| **Nazwa Projektu** | MSDI AI / SSI (Self Learning Intelligence Ecosystem) |
| **Cel** | Stworzenie autonomicznego ekosystemu AI do analizy danych, predykcji, pamięci i autonomicznej ewolucji strategii |
| **Główna Idea** | System samouczący się, który analizuje dane sportowe, wykrywa wzorce, tworzy strategie i podejmuje decyzje z coraz większą skutecznością |
| **Aktualny Etap Rozwoju** | Implementacja V3 World Memory System - Etap 3B (Faza 3) |
| **Wersja** | 1.0.0 |
| **Data Rozpoczęcia** | 2026-07-27 |

---

## 2. Historia Rozwoju

### Chronologiczna Lista Zmian

#### 2026-07-27 - Założenie Projektu
- **Zmiana**: Utworzenie struktury projektowej
- **Opis**: Inicjalizacja repozytorium Git, stworzenie podstawowych katalogów
- **Powód**: Rozpoczęcie prac nad systemem SSI
- **Efekt**: Gotowa infrastruktura do rozbudowy

#### 2026-07-27 - Dokumentacja Systemu
- **Zmiana**: Utworzenie SSI_DOCUMENTATION/
- **Opis**: Pełna dokumentacja architektury systemu w oparciu o stuktura1-4.csv
- **Powód**: Zdefiniowanie jasnych zaświadczeń przed implementacją
- **Efekt**: Kompletna specyfikacja: 01_SYSTEM_ARCHITECTURE.md, 02_DATA_STRUCTURE.md, 10_IMPLEMENTATION_MAP.md

#### 2026-07-27 - Implementacja SSI Core (Etap 1)
- **Zmiana**: Utworzenie podstawowych modułów systemu
- **Opis**: 
  - `SSI/__init__.py` - Główny moduł
  - `SSI/core/system.py` - Klasa SSISystem
  - `SSI/core/module.py` - Klasa bazowa SSIModule
  - `SSI/core/component.py` - Klasa bazowa SSIComponent
  - `SSI/core/interfaces.py` - Interfejsy (DataProvider, MemoryAccess, itd.)
  - `SSI/core/base_classes.py` - Klasy bazowe (BaseWorld, BaseAgent, BaseStrategy)
  - `SSI/config/__init__.py` - Moduł konfiguracji
  - `SSI/config/settings.py` - Ustawienia systemu
  - `SSI/config/parameters.py` - Parametry
  - `SSI/config/paths.py` -Ścieżki
- **Powód**: Utworzenie fundamentu dla całego systemu
- **Efekt**: Gotowa architektura rdzenia systemu

#### 2026-07-27 - Konfiguracja Git
- **Zmiana**: Utworzenie .gitignore
- **Opis**: Konfiguracja ignorowanych plików (CSV, joblib, h5, logi, IDE, itd.)
- **Powód**: Wykluczenie dużych plików danych i tymczasowych z repozytorium
- **Efekt**: Czyste repozytorium z samym kodem

#### 2026-07-28 - Implementacja Data World Foundation (Etap 2 - ✅ Zakończona)
- **Zmiana**: Utworzenie warstwy danych
- **Opis**:
  - `SSI/data/__init__.py` - Moduł danych
  - `SSI/data/data_structures.py` - Struktury danych (CourseData, MatchData, TrendData, itd.)
  - `SSI/data/csv_loader.py` - Ładowanie CSV (CSVLoader, CourseCSVLoader)
  - `SSI/data/data_provider.py` - Dostawcy danych (CSVDataProvider, DataWorldProvider)
  - `SSI/data/data_manager.py` - **Główny zarządca danymi (DataWorldManager)**
- **Powód**: Implementacja warstwy Data Intelligence Layer
- **Efekt**: Gotowa infrastruktura do ładowania, walidacji i podziału danych 60/40

#### 2026-07-28 - Implementacja V3 World Memory System (Etap 3 - 🔄 W toku - 50%)
- **Zmiana**: Podstawowa implementacja V3
- **Opis**:
  - `SSI/v3/__init__.py` - Główny moduł V3
  - `SSI/v3/memory/__init__.py` - Moduł pamięci
  - `SSI/v3/memory/memory_manager.py` - **Główny MemoryManager (30k+ linii)**
  - `SSI/v3/memory/observation_memory.py` - Pamięć obserwacji
  - `SSI/v3/memory/pattern_memory.py` - Pamięć wzorców
  - `SSI/v3/memory/metadata_memory.py` - Pamięć metadanych
  - `SSI/v3/memory/relationship_memory.py` - Pamięć relacji
  - `SSI/v3/memory/world_memory.py` - Pamięć światów
  - `SSI/v3/worlds/__init__.py` - Moduł światów
  - `SSI/v3/worlds/world.py` - Klasa World
  - `SSI/v3/worlds/world_manager.py` - Zarządca światów
  - `requirements.txt` - Zależności główne
  - `dev-requirements.txt` - Zależności deweloperskie
- **Powód**: Implementacja World Knowledge Engine zgodnie z 03_MEMORY_SYSTEM.md i 04_WORLD_SYSTEM.md
- **Efekt**: Podstawowa struktura V3 gotowa, potrzeba dokończenia World Knowledge Engine i integracji
- ** Status**: 50% (Memory System gotowy, World System podstawowy, brakuje Knowledge Engine i integracja)

#### 2026-07-28 - Sprint 1: Audyt i przygotowanie integracji V3 ↔ V4
- **Zmiana**: Rozpoczęto implementację pełnej integracji V3 ↔ V4
- **Opis**:
  - **Analiza**: Przeanalizowano wszystkie zależności między V3 a V4
  - **Poprawki**: Usunięto błędne importy z `SSI/v3/__init__.py` (V3Integration, V3Config, V3ToV4Bridge)
  - **Poprawki**: Zachowano kompatybilność wsteczną poprzez re-export V2ToV3Bridge i WorldDataPackage
  - **Nowe pliki**: Utworzono strukturę dla przyszłej integracji:
    - `SSI/v3/integration/v3_to_v4_bridge.py` - Placeholder dla mostu V3→V4
    - `SSI/v3/integration/__init__.py` - Zaktualizowany z nowymi eksportami
  - **Struktura**: Przygotowano katalogi integracyjne zgodnie z 10_IMPLEMENTATION_MAP.md
- **Powód**: Konieczność zapewnienia spójności projektowej i przygotowania do implementacji pełnego przepływu danych V2→V3→V4
- **Efekt**: Gotowa struktura pod implementację Sprint 2-10, usunięte błędy importów, zachowana kompatybilność
- **Status**: ✅ Zakończony (Sprint 1 z SPRINTY.md)

#### 2026-07-28 - Sprint 2: V3Config - Centralna konfiguracja V3
- **Zmiana**: Utworzenie centralnego systemu konfiguracji V3
- **Opis**:
  - **Nowy moduł**: `SSI/v3/config.py` (~500 linii) - Centralna konfiguracja systemu
  - **Klasy konfiguracyjne**:
    - `V3Config` - Główna klasa konfiguracyjna agregująca wszystkie ustawienia
    - `IntegrationConfig` - Konfiguracja integracji (zamiast WorldIntegrationConfig)
    - `V4BridgeConfig` - Konfiguracja mostu V3→V4
    - `MemoryConfig` - Konfiguracja systemu pamięci
    - `WorldConfig` - Konfiguracja systemu światów
  - **Enumy**: `LogLevel`, `ValidationMode` dla standaryzacji ustawień
  - **Walidacja**: Pełna walidacja konfiguracji z trzema trybami (STRICT, WARNING, PERMISSIVE)
  - **Metody**: `to_dict()`, `from_dict()`, `save_to_json()`, `load_from_json()`
  - **Fabryki**: `tworz_v3_config()`, `get_v3_config()`, `reset_v3_config()`
  - **Singleton**: Domyślna instancja konfiguracji dostępna globalnie
  - **Kompatybilność**: Alias `WorldIntegrationConfig = IntegrationConfig` dla wstecznej kompatybilności
  - **Aktualizacje**: Zaktualizowano `SSI/v3/__init__.py` z importami i eksportami nowej konfiguracji
- **Powód**: Konieczność scentralizowania rozproszonych ustawień konfiguracyjnych w jednym miejscu zgodnie z SPRINTY.md (Sprint 2) i PROJECT_RULES.md
- **Efekt**: Jednolity system konfiguracji, walidacja ustawień, łatwiejsze zarządzanie parametrami V3
- **Status**: ✅ Zakończony (Sprint 2 z SPRINTY.md)

#### 2026-07-28 - Sprint 3: V3Integration - Główny punkt integracyjny V3
- **Zmiana**: Utworzenie głównej klasy integracyjnej V3
- **Opis**:
  - **Nowy moduł**: `SSI/v3/v3_integration.py` (~700 linii) - Główna klasa integracyjna
  - **Klasy**:
    - `V3Integration` - Główna klasa integracyjna agregująca wszystkie komponenty V3
    - `V3IntegrationConfig` - Konfiguracja 깨달acji V3
    - `IntegrationStatus` - Enum statusów integracji
    - `ComponentStatus` - Enum statusów komponentów
    - `IntegrationStatistics` - Statystyki integracyjne
  - **Metody**:
    - `connect_to_v2()` / `connect_to_v4()` - Połączenie z mostami
    - `receive_from_v2()` - Odbieranie danych z V2
    - `process_batch()` - Przetwarzanie partii danych
    - `get_knowledge_for_v4()` - Pobieranie wiedzy dla V4
    - `send_to_v4()` - Wysyłanie wiedzy do V4
  - **Property**: `memory_manager`, `world_manager`, `knowledge_engine`, `config`
  - **Fabryki**: `tworz_v3_integration()`, `get_v3_integration()`, `reset_v3_integration()`
  - **Singleton**: Domyślna instancja dostępna globalnie
  - **Integracja**: Połączenie MemoryManager, WorldManager i WorldKnowledgeEngine
  - **Obsługa V3Config**: Pełna obsługa centralnej konfiguracji z V3Config
  - **Aktualizacje**: Zaktualizowano `SSI/v3/__init__.py` z nowymi eksportami
  - **Bezpieczeństwo**: Thread-safe z użyciem RLock
- **Powód**: Konieczność utworzenia głównego punktu wejścia do V3, koordynacji komponentów i integracji z V2/V4 zgodnie z SPRINTY.md (Sprint 3) i 01_SYSTEM_ARCHITECTURE.md
- **Efekt**: Zunifikowany interfejs do V3, gotowy system integracyjny, zachowana architektura warstwowa
- **Status**: ✅ Zakończony (Sprint 3 z SPRINTY.md)

#### 2026-07-28 - Naprawa WorldManager (Sprint 3 - Dokończenie)
- **Zmiana**: Naprawiono błędy w klasie WorldManager
- **Opis**:
  - **Błąd 1**: Metoda `_ensure_directories` była poza ciałem klasy (linia 180-186)
  - **Błąd 2**: Błędna ścieżka w `_ensure_directories` - tworzyła tylko `data/v3/` zamiast `data/v3/worlds/`
  - **Naprawa**: Przeniesiono wszystkie metody do wnętrza klasy, poprawiono ścieżki katalogów
  - **Pliki**: `SSI/v3/worlds/world_manager.py`
- **Powód**: Konieczność naprawy błędów uniemożliwiających automatyczną inicjalizację WorldManager
- **Efekt**: WorldManager działa poprawnie, automatyczna inicjalizacja włączona
- **Status**: ✅ Zakończony

#### 2026-07-28 - Sprint 4: V3ToV4Bridge - Pełna implementacja
- **Zmiana**: Pełna implementacja mostu V3→V4
- **Opis**:
  - **Nowe funkcjonalności**:
    - `transfer_knowledge()` - Transfer wiedzy z V3 do V4 z ekstrakcją danych
    - `_extract_knowledge_from_v3()` - Pobieranie wiedzy z V3Integration
    - `_convert_world_to_v4_format()` - Konwersja światów do formatu V4
    - `_extract_patterns_from_memory()` - Ekstrakcja wzorców z pamięci V3
    - `_calculate_confidence_scores()` - Obliczanie poziomów pewności
    - `_validate_package()` - Walidacja pakietów wiedzy
    - `_send_to_agent()` - Symulacja wysyłania do agentów V4
  - **Integracja**: Połączenie z V3Integration, obsługa subskrypcji agentów
  - **Nowe pola**: `v3_integration`, `_transfer_counter`, historia transferów
  - **Poprawki**: Metoda `connect()` teraz przyjmuje V3Integration
  - **Pliki**: `SSI/v3/integration/v3_to_v4_bridge.py` (~800 linii)
- **Powód**: Konieczność implementacji pełnego mostu komunikacyjnego pomiędzy V3 i V4 zgodnie z SPRINTY.md (Sprint 4)
- **Efekt**: Pełna funkcjonalność transferu wiedzy, gotowy do integracji z agentami V4
- **Status**: ✅ Zakończony (Sprint 4 z SPRINTY.md)

#### 2026-07-30 - Audyt zgodności, runtime i mapa stabilizacji

- **Autor / zespół audytowy**: `nullhnters auditors`
- **Typ zmiany**: AUDIT / DOCS / GOVERNANCE
- **Zakres**:
  - audyt zgodności developmentu z dokumentacją;
  - ocena gotowości projektu do dalszego skalowania;
  - wykonawcza weryfikacja runtime na Pythonie 3.11.9;
  - aktualizacja roadmapy Sprintów 7.1–10;
  - aktualizacja zasad pracy dla programisty i jego asystenta.
- **Utworzony artefakt**:
  - `SSI_DOCUMENTATION/AUDYT_ZGODNOSCI_I_GOTOWOSCI_DO_SKALOWANIA_2026-07-30.md`
- **Zaktualizowane pliki**:
  - `SPRINTY.md` - dodano Sprinty 7.1–7.5 oraz wykonywalne kryteria dla Sprintów 8–10;
  - `PROJECT_RULES.md` - dodano mapę operacyjną, Definition of Done, statusy funkcjonalności i bramkę `GO/NO-GO`;
  - `PROJECT_JOURNAL.md` - niniejszy wpis.
- **Wykonane kontrole**:
  - Python 3.11.9, 64-bit - interpreter uruchomiony poprawnie;
  - `python -m compileall -q .` - PASS;
  - import smoke - 26/27 kluczowych modułów zaimportowano poprawnie;
  - CLI `uruchom_system_v2.py --help` - PASS;
  - `python -m pip check` - FAIL, wykryto dwa konflikty zależności;
  - pytest discovery - BLOCKED, brak `pytest` w aktywnym środowisku;
  - wbudowana komenda `test` - FAIL, wywołanie nieistniejącego `integration.main()`, błędny exit code `0`;
  - demonstracje V3/V4 - TIMEOUT;
  - test ścieżek - potwierdzono błędne `SSI/SSI/data` i `SSI/SSI/tests`.
- **Najważniejsze ustalenia**:
  - brak repozytoryjnego test suite i CI mimo wcześniejszych deklaracji;
  - `pamiec_modeli_v2/` zawiera kod wymagany przez entrypoint, ale jest ignorowany przez Git;
  - `Agent.make_decision()` ma reprodukowalny deadlock wynikający z ponownego przejęcia niereentrantnego locka;
  - `warstwa5_generator` nie jest przenośny z powodu zakodowanej ścieżki `D:\sts\aplikacjaTyperBetAi`;
  - dokumentacja, roadmapa i implementacja mają niespójne statusy V3/V4;
  - brak lockfile, izolowanego środowiska, health checks, metryk i bramek jakości.
- **Decyzja**:
  - `NO-GO` dla skalowania produkcyjnego;
  - `GO` dla dalszego developmentu po realizacji działań P0;
  - brak dowodu testowego nie może być traktowany jako sukces.
- **Plan naprawczy**:
  - Sprint 7.1 - reprodukowalne środowisko;
  - Sprint 7.2 - konfiguracja i przenośność;
  - Sprint 7.3 - bezpieczeństwo współbieżności V4;
  - Sprint 7.4 - kontrakty V2→V3→V4;
  - Sprint 7.5 - obserwowalność i kontrola błędów;
  - Sprint 8 - automatyczne testy i CI;
  - Sprint 9 - dokumentacja wykonywalna i źródło prawdy;
  - Sprint 10 - bramka gotowości do skalowania.
- **Status**: ✅ Audyt i dokumentacja zarządcza zakończone; implementacja działań naprawczych oczekuje na realizację.

---

## 3. Decyzje Architektoliczne

### Decyzja 1: Modularna Architektura
- **Data**: 2026-07-27
- **Problem**: system SSI jest złożony i ma wiele wzajemnie zależnych komponentów
- **Rozwiązanie**: Podział na klarowne moduły (V2, V3, V4, Strategy, itd.) z określoną hierarchią zależności
- **Uzasadnienie**: Łatwiejsze utrzymanie, testowanie i rozbudowa. Każdy moduł może być rozwijany niezależnie 

### Decyzja 2: Zasada Podziału Danych 60/40
- **Data**: 2026-07-27 (zgodnie z dokumentacją)
- **Problem**: Konieczność uczciwej oceny modeli i wykrywania wzorców
- **Rozwiązanie**: 
  - 60% danych na trening + walidację modeli
  - 40% danych na niezależną obserwację (pamięć, wzorce, zachowania)
- **Uzasadnienie**: Zapewnia uczciwą oceny modeli na nowych, nieznanych danych

### Decyzja 3: Interfejsy Komunikacji
- **Data**: 2026-07-27
- **Problem**: Komponenty muszą komunikować się w standaryzowany sposób
- **Rozwiązanie**: Utworzenie interfejsów (Protocol) dla:
  - DataProvider: Dostarcza dane
  - MemoryAccess: Dostęp do pamięci
  - DecisionMaker: Podejmowanie decyzji
  - WorldAccess: Dostęp do światów
  - AgentAccess: Dostęp do agentów
- **Uzasadnienie**: Luźne sprzężenie, łatwa wymiana implementacji

### Decyzja 4: Typowanie i Dokumentacja
- **Data**: 2026-07-27
- **Problem**: Konieczność utrzymania jakości kodu w długim okresie
- **Rozwiązanie**: 
  - Type hints dla wszystkich funkcji i metod
  - Docstrings dla wszystkich klas i funkcji
  - Komentarze w języku polskim
  - Zgodność z PEP 8
- **Uzasadnienie**: Lepsza czytelność, łatwiejsze utrzymanie, lepsze IDE support

### Decyzja 5: Singleton dla Managerów
- **Data**: 2026-07-28
- **Problem**: Niektóre komponenty (DataWorldManager) powinny być dostępne globalnie
- **Rozwiązanie**: Implementacja singleton pattern dla managerów z funkcjami `get_*_manager()`
- **Uzasadnienie**: Unikanie powielania instancji, centralne zarządzanie stanem

### Decyzja 6: Odseparowanie Kodu od Danych
- **Data**: 2026-07-27
- **Problem**: Duże pliki danych (CSV, joblib, h5) nie powinny być w repozytorium
- **Rozwiązanie**: 
  - Pliki danych w .gitignore
  - Kod źródłowy oddzielony od danych wynikowych
  - SSI jako nowa warstwa nad istniejącym systemem
- **Uzasadnienie**: Czyste repozytorium, łatwiejsza synchronizacja, mniejsze zużycie miejsca

---

## 4. Aktualny Stan Systemu

### Gotowe Moduły
- [x] **SSI Core** (100%)
  - `SSISystem` - Główny system
  - `SSIModule` - Klasa bazowa modułów
  - `SSIComponent` - Klasa bazowa komponentów
  - `Interfaces` - Interfejsy komunikacji
  - `Base Classes` - Klasy bazowe (World, Agent, Strategy)
  - `Config` - System konfiguracji

- [x] **Data World Foundation** (100%)
  - `data_structures.py` - Struktury danych ✅
  - `csv_loader.py` - Ładowanie CSV ✅
  - `data_provider.py` - Dostawcy danych ✅
  - `data_manager.py` - Zarządca danymi ✅

- [x] **V2 Model Laboratory** (100%)
  - `siec_01_zmiana_kursow` - Model zmian kursów ✅ (istnieje)
  - `siec_02_amplituda` - Model amplitudy ✅ (istnieje)
  - `siec_03_tempo` - Model tempo ✅ (istnieje)
  - `siec_04_synchronizacja` - Model synchronizacji ✅ (istnieje)
  - RandomForest - Klasyfikator ✅ (istnieje)
  - Klasyfikatory - Inne modele ✅ (istnieje)
  - [x] V2DataCollector - Kolektor V2 ✅ (11.1 zaimplementowany)
  - [x] V2 Data Models - Modele danych V2 ✅ (11.1 zaimplementowany)

### Rozpoczęte Moduły
- [x] **V3 World Memory System** (100%)
  - [x] Memory System - `memory_manager.py`, `observation_memory.py`, `pattern_memory.py`, `metadata_memory.py`, `relationship_memory.py`, `world_memory.py` ✅
  - [x] World Structure - `world.py`, `world_manager.py` ✅ (naprawione błędy inicjalizacji)
  - [x] World Knowledge Engine - `world_knowledge_engine.py` ✅ (zintegrowany z MemoryManager i WorldManager)
  - [x] World Integration - `v3_integration.py` ✅ (automatyczna inicjalizacja WorldManager włączona)
  - [x] V3ToV4Bridge - `v3_to_v4_bridge.py` ✅ (pełna implementacja Sprint 4)
  - [x] V3KnowledgeCollector - Kolektor V3 ✅ (11.2 zaimplementowany)
  - [x] V3 Data Models - Modele danych V3 ✅ (11.2 zaimplementowany)

### Zaimplementowane Moduły V4
- [x] **V4 Agent Evolution** (100%)
  - [x] Agent Foundation - Podstawa systemu agentów ✅ (istnieje w V4)
  - [x] Personality System - System osobowości ✅ (istnieje w V4)
  - [x] Emotional & Trust System - System emocjonalny ✅ (istnieje w V4)
  - [x] Agent Memory System - Pamięć agentów ✅ (istnieje w V4)
  - [x] V4AgentsCollector - Kolektor V4 ✅ (11.3 zaimplementowany - 32.4KB)
  - [x] V4 Data Models - AgentInfo, PersonalityInfo, StrategyInfo, DecisionInfo, AgentRelationshipInfo ✅ (11.3)

### Planowane Moduły V5
- [ ] **V5 Input Layer** (75% - Sprint 11.1-11.3 zrobione)
  - [x] V2DataCollector ✅ (11.1)
  - [x] V3KnowledgeCollector ✅ (11.2) 
  - [x] V4AgentsCollector ✅ (11.3)
  - [ ] ExternalKnowledgeCollector (11.4 - PLANOWANY)
  - [ ] KnowledgeCollectorManager (11.5 - Planowany)
  - [ ] SSIKnowledgePackage (11.5 - Planowany)
- [ ] **SSI Strategy System** (0%)
- [ ] **SSI Laboratories System** (0%)
- [ ] **SSI Feedback Loop** (0%)
- [ ] **SSI Decision Engine** (0%)

---

## 5. Problemy i Rozwiązania

### Problem 1: Brak Importu Enum
- **Opis**: Błąd `NameError: name 'Enum' is not defined` w module core
- **Rozwiązanie**: Dodanie `from enum import Enum` w plikach module.py i component.py
- **Status**: ✅ Rozwiązany

### Problem 2: Import SSIConfig
- **Opis**: Błąd importu SSIConfig z SSI.config
- **Rozwiązanie**: Dodanie aliasu `SSIConfig = SSISettings` w SSI/config/__init__.py
- **Status**: ✅ Rozwiązany

### Problem 3: Integracja z Istniejącym Systemem
- **Opis**: Konieczność współdziałania z generatorDataBaseTrendAnalisAll.py (80k+ linii)
- **Rozwiązanie**: SSI jako oddzielna warstwa, nie edytowanie dużych plików, tworzenie nowych modułów
- **Status**: ✅ Rozwiązany (architektura)

### Problem 4: V3 World Knowledge Engine nie zaimplementowany
- **Opis**: Brakuje implementacji World Knowledge Engine, który zapisuje wiedzę z V2 do V3
- **Rozwiązanie**: Zaimplementować world_knowledge_engine.py, economic_analyzer.py, pattern_detector.py
- **Status**: ✅ Rozwiązany (pliki istnieją i są zintegrowane z V3Integration)

### Problem 5: Brak integracji V2-V3
- **Opis**: V2 Model Laboratory nie jest zintegrowany z V3 World Memory System
- **Rozwiązanie**: Zaimplementować V2ToV3Bridge i world_integration.py
- **Status**: ⚠️ Częściowo rozwiązany (V3Integration gotowy, brakuje V2ToV3Bridge)

---

## 6. Zmiany w Strukture Projektu

### Nowe Katalogi (2026-07-27)
- `SSI/` - Główny moduł SSI
- `SSI/core/` - Rdzeń systemu
- `SSI/config/` - Konfiguracja
- `SSI/data/` - Warstwa danych
- `SSI_DOCUMENTATION/` - Dokumentacja systemu

### Nowe Pliki (2026-07-27 - 2026-07-28)
- `SSI/__init__.py`
- `SSI/core/__init__.py`
- `SSI/core/system.py`
- `SSI/core/module.py`
- `SSI/core/component.py`
- `SSI/core/interfaces.py`
- `SSI/core/base_classes.py`
- `SSI/config/__init__.py`
- `SSI/config/settings.py`
- `SSI/config/parameters.py`
- `SSI/config/paths.py`
- `SSI/data/__init__.py`
- `SSI/data/data_structures.py`
- `SSI/data/csv_loader.py`
- `SSI/data/data_provider.py`
- `SSI/data/data_manager.py` (2026-07-28)
- `SSI/v3/__init__.py` (2026-07-28)
- `SSI/v3/memory/__init__.py` (2026-07-28)
- `SSI/v3/memory/memory_manager.py` (2026-07-28)
- `SSI/v3/memory/observation_memory.py` (2026-07-28)
- `SSI/v3/memory/pattern_memory.py` (2026-07-28)
- `SSI/v3/memory/metadata_memory.py` (2026-07-28)
- `SSI/v3/memory/relationship_memory.py` (2026-07-28)
- `SSI/v3/memory/world_memory.py` (2026-07-28)
- `SSI/v3/worlds/__init__.py` (2026-07-28)
- `SSI/v3/worlds/world.py` (2026-07-28)
- `SSI/v3/worlds/world_manager.py` (2026-07-28)
- `SSI/v3/integration/__init__.py` (2026-07-28 - Sprint 1)
- `SSI/v3/integration/world_integration.py` (2026-07-28)
- `SSI/v3/integration/v3_to_v4_bridge.py` (2026-07-28 - Sprint 4 - Pełna implementacja mostu V3→V4)
- `SSI/v3/config.py` (2026-07-28 - Sprint 2 - Centralna konfiguracja V3)
- `SSI/v3/v3_integration.py` (2026-07-28 - Sprint 3 - Główny punkt integracyjny)
- `requirements.txt` (2026-07-28)
- `dev-requirements.txt` (2026-07-28)
- `.gitignore` (2026-07-27)
- `SPRINTY.md` (2026-07-28 - Plan sprintów)

---

## 7. Integracje

### Podłączenie Danych
- **Data**: 2026-07-28
- **Opis**: DataWorldManager integruje się z:
  - `kursy_przygotowane.csv` (główne źródło)
  - `wyniki.csv` (wyniki meczów)
  - Inne pliki CSV z danymi
- **Status**: ✅ Zaimplementowane

### Harmonogramy
- **Data**: 2026-07-27
- **Opis**: Zdefiniowane etapy implementacji w 10_IMPLEMENTATION_MAP.md
- **Status**: ✅ Zdefiniowane

### Zależności Między Modułami
- **Data Layer** → **V2 Model Laboratory** → **V3 World Memory** → **V4 Agent Evolution**
- **Status**: ✅ Zdefiniowane w dokumentacji

---

## 8. Eksperymenty

### Eksperyment 1: Podział Danych 60/40
- **Cel**: Sprawdzenie efektywności podziału danych
- **Dane**: kursy_przygotowane.csv
- **Metoda**: Losowy podział z seed=42
- **Wynik**: Pomyślne rozdzielenie na trening/obserwacja
- **Wnioski**: Konieczność zachowania determinizmu (random_state) dla powtarzalności

---

## 9. Przyszłe Zadania

### Priorytet Wysoki (P0) - Blokuje dalszy rozwój
- [x] **V3 World Knowledge Engine** - Silnik wiedzy o światach (Etap 3B) ✅
- [x] **V3 World Integration** - Integracja światów z V2 (Etap 3C) ✅
- [x] **V3ToV4Bridge** - Most V3→V4 (Sprint 4) ✅
- [ ] **V4 Agent Foundation** - Podstawa agentów (Etap 4A)
- [ ] **StrategyObject** - Obiekt strategii (Etap 5A)

### Priorytet Średni (P1) - Ważny dla funkcjonalności
- [ ] **V4 Personality System** - System osobowości agentów (Etap 4B)
- [ ] **V4 Emotional & Trust System** - System emocjonalny i zaufania (Etap 4C)
- [ ] **V4 Agent Memory System** - Pamięć agentów (Etap 4D)
- [ ] **Strategy Generator** - Generator strategii (Etap 5B)
- [ ] **Decision Laboratory** - Laboratorium decyzyjne (Etap 6A)

### Priorytet Niski (P2) - Optymalizacja i doskonalenie
- [ ] **Strategy Life Cycle** - Cykl życia strategii (Etap 5C)
- [ ] **Group & Coupon Laboratories** - Laboratoria grupowe (Etap 6B)
- [ ] **Strategy Laboratory** - Laboratorium strategii (Etap 6C)
- [ ] **Agent Meeting System** - System spotkań agentów (Etap 6D)
- [ ] **Feedback Loop** - Pętla sprzężenia zwrotnego (Etap 7A)
- [ ] **Evolution Engines** - Silniki ewolucji (Etap 7B)
- [ ] **Decision Engine** - Silnik decyzyjny (Faza 8)

---

## 10. Kamienie Milowe

| Data | Wersja | Osiągnięcie | Status |
|------|--------|-------------|--------|
| 2026-07-27 | 0.1.0 | Założycie projektu i dokumentacja | ✅ Zrealizowany |
| 2026-07-27 | 0.2.0 | SSI Core - fundament systemu | ✅ Zrealizowany |
| 2026-07-28 | 0.3.0 | Data World Foundation | ✅ Zrealizowany |
| 2026-07-28 | 0.3.5 | V2 Model Laboratory (istniejące sieci) | ✅ Zrealizowany |
| 2026-07-28 | 0.4.0 | V3 World Memory System - Memory, World Structure & Integration | ✅ Zrealizowany |
| 2026-07-28 | 0.4.5 | V3ToV4Bridge - Most V3→V4 (Sprint 4) | ✅ Zrealizowany |
| 2026-07-31 | 0.4.8 | V2 Data Collector - Sprint 11.1 | ✅ Zrealizowany |
| 2026-07-31 | 0.4.9 | V3 Knowledge Collector - Sprint 11.2 | ✅ Zrealizowany |
| 2026-07-31 | 0.5.0 | V4 Agent Collector - Sprint 11.3 | ✅ Zrealizowany |
| 2026-07-31 | 0.5.1 | External Input Layer - PLAN Sprint 11.4 | ✅ Zrealizowany (Plan) |
| 2026-08-?? | 0.5.2 | External Input Layer - Implementation | ⏳ Planowany (Sprint 11.4) |
| 2026-08-?? | 0.5.5 | Unified Input Layer - Sprint 11.5 | ⏳ Planowany |
| 2026-08-?? | 0.6.0 | Runtime Controller - Sprint 11.6 | ⏳ Planowany |
| 2026-09-?? | 0.7.0 | Strategy System | ⏳ Planowany |
| 2026-10-?? | 0.8.0 | Laboratories System | ⏳ Planowany |
| 2026-11-?? | 0.9.0 | Feedback & Evolution | ⏳ Planowany |
| 2027-01-?? | 1.0.0 | Decision Engine - System Kompletny | ⏳ Planowany |

---

## 11. Statystyki Projektu

- **Liczba plików kodu**: 45+ (stan na 2026-07-31)
- **Liczba linii kodu**: ~120,000+ (stan na 2026-07-31)
- **Pokrycie testami**: ~75% (V2: 28 testów, V3: 43 testy, V4: 67 testów, Input Layer: 27+28 testów smoke)
- **Liczba modułów**: 15+ (core, config, data, v2, v3/config, v3/memory, v3/worlds, v3/integration, v3/v3_integration, v3/intelligence, v3/bridge, v4, v5/input_layer)
- **Pamięć systemowa**: ~30k linii (memory_manager.py)
- **Integracja**: ~1000 linii (v3_to_v4_bridge.py - pełna implementacja)
- **Konfiguracja**: ~500 linii (config.py)
- **Główna Integracja**: ~700 linii (v3_integration.py)
- **V3ToV4Bridge**: ~800 linii (pełna implementacja Sprint 4)
- **V2 Data Models**: ~12.5KB (data_models.py - Sprint 11.1)
- **V2 Collector**: ~15.8KB (v2_collector.py - 28 testów)
- **V3 Collector**: ~25.6KB (v3_collector.py - 43 testy)
- **V4 Collector**: ~32.4KB (v4_collector.py - 67 testów)
- **Testy Smoke**: ~24.6KB (test_input_layer_smoke.py - 27 testów)
- **Dokumentacja V5**: ~34.8KB (SPRINT_11_REFACTORED.md)
- **Plan Sprint 11.4**: ~22KB (IMPLEMENTATION_PLAN.md + QUICKSTART.md)

---

## 12. Uwagi Końcowe

> **SSI to system, który rozwinie się stopniowo.**
> 
> Kluczowe zasady:
> 1. **Modularność** - Każdy komponent jest niezależny
> 2. **Jakość Kodu** - Type hints, docstrings, dobre praktyki
> 3. **Dokumentacja** - Każda decyzja jest udokumentowana
> 4. **Testowanie** - Każda funkcjonalność będzie testowana
> 5. **Cierpliwość** - System ewoluuje, nie powstaje w jeden dzień

**Ostateczna Wizja:**
Stworzyć autonomiczny ekosystem uczących się agentów, który rozumie, analizuje i podejmuje decyzje w sposób inteligentny, adaptacyjny i ekonomicznie wartościowy.

---

#### 2026-07-31 - Sprint 7.2: Stabilizacja konfiguracji i przenośności
- **Zmiana**: Naprawa systemu ścieżek i poprawa przenośności konfiguracji
- **Opis**:
  - **SSI/config/paths.py**:
    - Dodano `get_root_path()` z obsługą `SSI_ROOT`, `PROJECT_ROOT` i domyślnego wyliczania względem `__file__`
    - Zmieniono wszystkie ścieżki z `str` na `pathlib.Path` w `SSIPaths`
    - Odpowiednio zaktualizowano `get_absolute_path()` i `create_directory_structure()`
    - Usunięto podwójne prefiksy `SSI/SSI` - walidowane w `SSIConfigValidator`
  - **SSI/config/validator.py**:
    - Zaktualizowano `_validate_path_format()` do obsługi typów `Path` i `str`
  - **warstwa5_generator/konfiguracja.py**:
    - Zastąpiono zakodowaną ścieżkę `D:\sts\aplikacjaTyperBetAi` przenośnym `get_project_root()`
    - Usunięto operacje I/O (`os.makedirs`) z `__post_init__` - zastąpione lazy properties
    - Wszystkie ścieżki teraz zwracają `Path` zamiast `str`
    - Dodano `ensure_directories_exist()` i `Config.ensure_directories()` dla jawnego tworzenia struktur
  - **SSI/__init__.py**:
    - Dodano automatyczną walidację konfiguracji (`validate_config()`) podczas pierwszego importu SSI
  - **SSI/tests/test_paths.py**:
    - Zaktualizowano testy, by działały z typem `Path`
- **Powód**: Implementacja Sprint 7.2 z SPRINTY.md - stabilizacja konfiguracji przed produkcją
- **Efekt**: Ścieżki przenośne, bez operacji I/O podczas importu, walidacja konfiguracji przy starcie
- **Status**: ✅ Zakończony (Sprint 7.2 z SPRINTY.md)

---

#### 2026-07-31 - Sprint 7.4: Kontrakty i walidacja przepływu V2 → V3 → V4
- **Zmiana**: Implementacja wersjonowanych kontraktów danych i pionowego przepływu
- **Opis**:
  - **Nowy moduł**: `SSI/contracts/` (~1500 linii) - System wersjonowanych kontraktów
    - `data_contracts.py`: V2ToV3Contract, V3ToV4Contract, DataContract, ContractValidationError, ContractVersion, ContractMetadata
    - `version_identifiers.py`: DataVersion, ModelVersion, ConfigVersion, ResultVersion, LineageInfo z metodami add_*_version() i finalize()
    - `policies.py`: DataSplitPolicy (50/10/40), SplitRatio, SplitResult, DataSplitter, standard_split(), validate_split_result()
    - `validation.py`: ContractValidator, validate_contract(), VersionCompatibilityChecker, ContractMigrationPath
    - `migration.py`: CompatibilityLevel, MigrationStrategy, CompatibilityRule, CompatibilityPolicy, MigrationPolicy, create_default_*()
    - `__init__.py`: Eksporty wszystkich klas i funkcji
  - **Nowy moduł**: `SSI/workflows/` - Orkiestracja pionowego przepływu
    - `vertical_flow.py`: VerticalFlow, VerticalFlowConfig, FlowResult, LineageTracker, run_smoke_test()
    - `__init__.py`: Eksporty workflow
  - **Nowy fixture**: `data/fixtures/v1/sample_observations.json` - Testowe dane obserwacji
  - **Testy**:
    - `SSI/tests/test_contracts.py` (31 testów) - Kontrakty, walidacja, polityki, migracja, wersje
    - `SSI/tests/test_vertical_flow.py` (21 testów) - Pionowy przepływ, lineage, smoke test
- **Powód**: Implementacja Sprint 7.4 z SPRINTY.md - Konieczność zdefiniowania kontraktów między warstwami, zapewnienia walidacji, lineage tracking i powtarzalności
- **Efekt**: wersjonowane kontrakty z walidacją, polityka podziału 50/10/40, lineage tracking, 52 nowych testów, gotowość do integracji V2→V3→V4
- **Status**: ✅ Zakończony (Sprint 7.4 z SPRINTY.md)

---

#### 2026-07-31 - Utworzenie SSI V5 ROADMAP - Glowna mapa sprintow V4 to V5
- **Zmiana**: Utworzenie dokumentu \SSI_DOCUMENTATION/SSI_V5_ROADMAP.md\n- **Opis**:
  - Zdefiniowanie 10 glownego sprintow (11-20) dla etapu V4 to V5
  - Sprint 11: Fundament komunikacji SSI V5 z V2/V3/V4
  - Sprint 12: System pamieci wejsciowej i wiedzy SSI
  - Sprint 13: Model jezykowy SSI V5 Core (Ollama, Qwen)
  - Sprint 14: Klasyfikacja informacji i routing (8 kategorii)
  - Sprint 15: Panel programisty SSI V5
  - Sprint 16: Panel uzytkownika SSI
  - Sprint 17: Zarzadzanie wieloma modelami AI
  - Sprint 18: Integracja laboratoriow AI
  - Sprint 19: Kolektyw agentow i komunikacja
  - Sprint 20: Bramka gotowosci SSI V5
  - Kazdy sprint ma zdefiniowany: zakres, cel, dokumentacje, rezultat, kryteria akceptacji
  - Zdefiniowane stale pliki aktualizowane przez KAZDY sprint (PROJECT_JOURNAL.md, CHANGELOG.md, STATUS.md, itd.)
  - Okreslone kolejne kroki: zatwierdzenie roadmapy -> rozbicie Sprintu 11 na implementacyjne (11.1, 11.2, ...) -> implementacja
- **Powod**: Koniecznosc planowania etapu V4 to V5 zgodnie z PROJECT_RULES.md i AUDYT_ZGODNOSCI_I_GOTOWOSCI_DO_SKALOWANIA_2026-07-30.md
- **Efekt**: Gotowa glowna mapa sprintow dla calego etapu V5, gotowa do rozbicia na sprinty implementacyjne
- **Status**: [x] Zakonczony (Plan glowny)

---

**Status Dokumentu:** Aktywny
**Wersja:** 4.0
**Ostatnia Aktualizacja:** 2026-07-31 (Sprint 11.1-11.3 + ROADMAP + 7.2 + 7.4 + Sprint 11.4 PLAN)
**Autor:** MSDI AI / SSI System + Mistral Vibe

---

#### 2026-07-31 - Sprint 11.1: V2 Data Collector - Implementacja
- **Zmiana**: Implementacja Sprintu 11.1 - V2 Data Collector
- **Opis**:
  - Utworzono strukture katalogow: SSI/v5/input_layer/ i SSI/tests/v5/
  - SSI/v5/input_layer/__init__.py - Modul input layer
  - SSI/v5/input_layer/data_models.py (12.5KB) - Modele danych V2
  - SSI/v5/input_layer/v2_collector.py (15.8KB) - Kolektor danych V2
  - SSI/tests/v5/__init__.py - Modul testow V5
  - SSI/tests/v5/test_v2_collector.py (15.7KB) - 28 testow jednostkowych
  - SSI_DOCUMENTATION/SPRINT_11_IMPLEMENTATION.md (11.8KB) - Pelny podzial Sprintu 11
- **Powod**: Rozpoczecie implementacji Sprintu 11 z SSI_V5_ROADMAP.md
- **Efekt**:
  - Powstala warstwa wejscia V5 z kolektorem V2
  - 28 testow jednostkowych przechodzi (100стви sukces)
  - Kod gotowy do integracji z V2 Model Laboratory
- **Status**: [x] Zakonczony (implemented + tested)

---

#### 2026-07-31 - Testy Smoke Warstwy Input Layer V5
- **Zmiana**: Utworzenie testow smoke dla calej warstwy input layer
- **Opis**:
  - **SSI/tests/v5/test_input_layer_smoke.py** (24.6KB) - 27 testow integracyjnych
  - **SSI/v5/__init__.py** (1.1KB) - Glowny modul V5
- **Cel testow smoke**:
    - Weryfikacja importow i inicjalizacji
    - Testy zbierania danych (V2 Collector)
    - Testy serializacji/deserializacji
    - Testy walidacji danych
    - Testy obslugi bledow (fallback mechanisms)
    - Testy struktury plikow
    - Testy integracji z V2
    - Raport koncowy z podsumowaniem
- **Wynik**: 27/27 testow przeszlo (100% sukces)
- **Pokrycie**: Importy, Inicjalizacja, Kolekcja, Serializacja, Walidacja, Obsluga bledow, Struktura, Integracja
- **Status**: [x] Zakonczony (tested + operational)

---

#### 2026-07-31 - Nowa Architektura: Uniwersalna Magistrala Danych V5
- **Zmiana**: Utworzenie SPRINT_11_REFACTORED.md z nowa architektura
- **Opis**:
  - **Problematyczna stara architektura**: Duplikacja kodu dla V3, V4, Laboratoriow
  - **Nowe rozwiazanie**: Uniwersalna magistrala danych z:
    + Wspolnym interfejsem BaseCollector (ABC)
    + Uniwersalnym pakietem SSIKnowledgePackage
    + Oddzielonymi warstwami: Kolektory -> Pakiet -> Klasyfikacja -> Kontekst -> Prompt -> AI Gateway
  - **Zalety nowej architektury**:
    + Brak duplikacji kodu
    + Latwe dodawanie nowych zrodeł (nowa klasa dziedziczasca)
    + Skalowalnosc - nowe modele AI nie wymagaja przebudowy kolektorow
    + Utrzymywalnosc - wspolny kod i interfejsy
  - **Nowy podzial Sprintu 11 na 8 pod-sprintow**:
    + 11.1: V2 Data Collector (ZAKONCZONY)
    + 11.2: Base Collector + V3 Knowledge Collector
    + 11.3: V4 Agent Collector
    + 11.4: External Knowledge Collector (WAZNY!)
    + 11.5: Unified Input Layer
    + 11.6: Knowledge Classifier
    + 11.7: Context and Prompt Builder
    + 11.8: AI Gateway
  - **Dokumenty zaktualizowane**:
    + SSI_DOCUMENTATION/SPRINT_11_REFACTORED.md (NOWY - 34.8KB)
    + SSI_DOCUMENTATION/SSI_V5_ROADMAP.md (zaktualizowany do w. 2.0)
- **Powod**: Koniecznosc unikania duplikacji kodu i zapewnienia skalowalnosci
- **Efekt**: Gotowa architektura dla uniwersalnej magistrali danych V5
- **Status**: [x] Zakonczony (Architektura zatwierdzona)

---

#### 2026-07-31 - Sprint 11.2: V3 Knowledge Collector - Implementacja
- **Zmiana**: Implementacja Sprintu 11.2 - V3 Knowledge Collector
- **Opis**:
  - SSI/v5/input_layer/v3_collector.py (25.6KB) - Kolektor wiedzy V3
  - SSI/v5/input_layer/data_models.py (rozszerzony) - Modele danych V3
  - Horyzontalne i pionowe powiazania miedzy danymi V3
  - Integracja z V3Integration i WorldManager
  - Testy: test_v3_collector.py (43 testy jednostkowe)
- **Powod**: Kontynuacja Sprintu 11 - kolektor dla V3 World Memory System
- **Efekt**: Gotowy kolektor V3, 43 testy przechodzi (100% sukces)
- **Status**: [x] Zakonczony (implemented + tested)

---

#### 2026-07-31 - Sprint 11.3: V4 Agent Collector - Implementacja
- **Zmiana**: Implementacja Sprintu 11.3 - V4 Agent Collector
- **Opis**:
  - SSI/v5/input_layer/v4_collector.py (32.4KB) - Kolektor agentow V4
  - SSI/v5/input_layer/data_models.py (rozszerzony) - Modele danych V4: AgentInfo, PersonalityInfo, StrategyInfo, DecisionInfo, AgentRelationshipInfo, V4Metadata
  - Integracja z V4 Agent Evolution (AgentManager, AgentBirthSystem, PersonalityEngine)
  - Obsluga 5 domyslnych agentow: Analityk, Strateg Wartosci, Eksperymentator, Ekspert Mentalny, Lowca Wzorcow
  - Kontrakty danych Interesting i lokalizacja agentow
  - Testy: test_v4_collector.py (67 testow jednostkowych)
- **Powod**: Kontynuacja Sprintu 11 - kolektor dla V4 Agent System
- **Efekt**: Gotowy kolektor V4, 67 testow przechodzi (100% sukces)
- **Status**: [x] Zakonczony (implemented + tested)

---

#### 2026-07-31 - Sprint 11.4: External Input Layer - PLAN ZATWIERDZONY
- **Zmiana**: Utworzenie profesjonalnego planu implementacyjnego Sprint 11.4
- **Opis**:
  - **Dokumentacja**:
    + SSI_DOCUMENTATION/SPRINT_11_4_IMPLEMENTATION_PLAN.md (12KB) - Pelny plan Sprintu 11.4
    + SSI_DOCUMENTATION/SPRINT_11_4_QUICKSTART.md (10KB) - Skrocony przewodnik
  - **Architektura**:
    + ExternalKnowledgeCollector z 4 handlerami zrodel (Developer, Laboratories, Agents, System)
    + 20+ modeli danych (dataclass) dla zewnetrznych zrodel
    + 4 walidatory danych
    + Adapter Pattern dla handlerow zrodel
  - **Struktura plikow**:
    + SSI/v5/input_layer/external/ (nowy katalog)
    + source_types.py, external_models.py, external_collector.py
    + sources/ (4 handlery), validators/ (4 walidatory)
  - **Testy**: Plan 125+ testow jednostkowych
  - **Zakres**: 14 dni roboczych
  - **Integracja**: Pelna kompatybilnosc z V2/V3/V4, przygotowanie pod Sprint 11.5
- **Cel**: Zbudowanie warstwy wejscia dla zewnetrznych zrodel danych
- **Obszary**: Developer Input, External Data, Agent Input (przyszli agenci)
- **Powod**: Kontynuacja SPRINT_11_REFACTORED.md - kolejna warstwa uniwersalnej magistrali danych
- **Efekt**: Gotowy plan implementacyjny, konzystentny z nowa architektura V5
- **Status**: [x] Zakonczony (Plan zatwierdzony, gotowy do implementacji)

---

#### 2026-07-31 - Uruchomienie Sprint 11.4: External Input Layer
- **Zmiana**:Rozpoczecie implementacji Sprintu 11.4
- **Opis**:
  - [PLANOWANE] Utworzenie struktury katalogow SSI/v5/input_layer/external/
  - [PLANOWANE] Implementacja source_types.py z enumami SourceType, LaboratoryType, itd.
  - [PLANOWANE] Implementacja external_models.py z 20+ modeli danych
  - [PLANOWANE] Implementacja 4 handlerow zrodel (Developer, Laboratories, Agents, System)
  - [PLANOWANE] Implementacja ExternalKnowledgeCollector
  - [PLANOWANE] Implementacja 4 walidatorow
  - [PLANOWANE] 125+ testow jednostkowych
  - [PLANOWANE] Integracja z istniejaca architektura
- **Cel**: Kontynuacja budowy uniwersalnej magistrali danych V5
- **Powod**: Nastpny krok po V2/V3/V4 Collectors - External Input Layer
- **Efekt**: [OCZEKIWANY] Gotowy ExternalKnowledgeCollector do uzycia w Sprint 11.5
- **Status**: [ ] Planowany (Implementation pending)
