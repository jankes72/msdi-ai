# SSI V5 - MASTER SYSTEM FLOW ARCHITECTURE

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** DRAFT  
**Autor:** Mistral Vibe - CLI Coding Agent  
**Typ dokumentu:** ARCHITEKTURA SYSTEMOWA - PODSTAWOWY PRZEPLYW  

---

## 1. PODSUMOWANIE EXECUTIVE

Ten dokument definiuje **Master System Flow** - glowna mape przeplywu systemu SSI V5 od danych wejsciowych (V1) przez wszystkie warstwy przetwarzania az do zapisania stanu i rozpozczecia kolejnego cyklu. Jest to **dokument bazowy**, na ktorym opieraja sie wszystkie pozostale dokumenty architektury systemowej.

**Kluczowe cechy:**
- Pelna mapa przeplywu: V1->V5->Orchestration->Information Flow->Modules->Memory->Decision->Save State->Next Cycle
- Integracja wszystkich istniejacych modułow (Runtime Controller, State Manager, Scheduler, Agents, Collectors)
- Zgodnosc z ograniczeniami sprzetowymi (1 aktywny model LLM na raz)
- Obsluga obu trybow: Test Mode (10 cykli, 60 iteracji) i Production Mode (5 godzin ciagłej pracy)

---

## 2. GLOWNE KONCEPCJE

### 2.1. Definicja System Flow
**System Flow** to sekwencyjny przeplyw danych, stanow i decyzji przez wszystkie warstwy systemu SSI V5.

### 2.2. Zasady Przeplywu
- **Zasada Sekwencyjnosci:** Jedna operacja na raz (ograniczenie sprzetowe)
- **Zasada Izolacji:** Kazdy agent pracuje niezaleznie w swoim cyklu
- **Zasada Kontekstu:** Wszystkie decyzje oparte na aktualnym stanie systemu
- **Zasada Pamieci:** Kazda warstwa aktualizuje swoja pamiec po przetwarzaniu
- **Zasada Sygnalow:** Sygnaly bledow i stanu przeplywaja w obie strony

### 2.3. Typy Przeplywow
| Typ Przeplywu | Opis | Kierunek |
|---------------|------|----------|
| DATA FLOW | Przetwarzanie danych surowych | V1 -> V2 -> V3 -> V4 |
| CONTROL FLOW | Kontrola wykonania | Runtime Controller -> Agents |
| MEMORY FLOW | Aktualizacja pamieci | Agenci -> Memory Store |
| SIGNAL FLOW | Sygnaly stanu i bledow | Dwukierunkowy |
| DECISION FLOW | Proces decyzyjny | V4 -> Strategy Lab -> Decision Engine |

---

## 3. PELNA MAPA PRZEPLYWU SYSTEMU

### 3.1. Makro Przeplyw (High-Level View)

V1 DATA SYSTEM (pobieranieKursow.py, pobieranieWynikow.py, dodawanieWynikow.py)
    |
    v
V2 MODEL LABORATORY (siec_01_zmiana_kursow, siec_02_amplituda, siec_03_tempo, siec_04_synchronizacja)
    | (60% training, 40% observation)
    v
V3 WORLD MEMORY SYSTEM (World Memory, Group Memory, Pattern Memory, Historical Results)
    | (V3 NIE podejmuje decyzji - tworzy mape wiedzy)
    v
V4 AGENT EVOLUTION (6 agentow: 01-06, kazdy z wlasna pamiecia i osobowoscia)
    | (Kazdy agent: Wczytaj pamiec -> Pobierz dane -> Porownaj -> Analiza -> Decyzja -> Zapis doswiadczenia -> Aktualizacja historii)
    v
V5 SYSTEM ORCHESTRATION (Runtime Controller + State Manager + Scheduler + Agent Manager)
    | (Orchestrator zarzadza kolejka: MODEL START -> WORK -> SAVE MEMORY -> MODEL STOP -> NEXT MODEL)
    v
INFORMATION FLOW CONTROLLER (Collector Manager + Input Layer + Output Layer + Signal Management)
    | (Zbieranie danych z V2, V3, V4, External -> Przetwarzanie sygnalow -> Dostarczenie do modulow)
    v
MODULES & LABORATORIES
    ├── Decision Engine (Ocena decyzji: trafnosci x kurs x powtarzalnosc x stabilnosc - ryzyko)
    ├── Strategy Laboratory (Production Strategies + Experimental Strategies: Pomysl -> Test -> Ocena -> Ranking -> Akceptacja)
    ├── Memory Evolution System (Cykl: DOSWIADCZENIE -> PAMIEC SUROWA -> DOJRZEWANIE -> OBSERWACJA -> OCENA -> RANKING -> STRATEGIA -> SLAD DOSWIADCZENIA)
    ├── AI Lab Request Pipeline (MAIN SSI -> AI LAB REQUEST QUEUE -> DRUGI KOMPUTER -> WYNIK -> SSI MEMORY)
    ├── Prompt Management System (Kategorie: system_prompts, agent_prompts, developer_prompts, laboratory_prompts)
    └── Developer Input Architecture (PROGRAMISTA -> Developer Command Interface -> Governance -> Information Flow Controller -> Orchestrator -> Modul)
    v
MEMORY & STATE PERSISTENCE
    ├── Agent Memory (JSON Files: PERSONALITY, BEHAVIOR, STRATEGY, HISTORY)
    └── System State (State Manager: RuntimeState, AgentState, MemoryState, CollectorState)
    v
SAVE STATE & NEXT CYCLE
    ├── Save Runtime State to JSON
    ├── Save Agent Memory for all agents
    ├── Increment Cycle Counter
    └── Check: If Test Mode (10 cycles) or Production Mode (5 hours) -> Continue or Shutdown

---

## 4. WARSTWY SYSTEMU I ICH ODPOWIEDZIALNOSC

### 4.1. V1 Data System
**Odpowiedzialnosc:** Pobieranie surowych danych, archiwizacja, przygotowywanie do przetwarzania
**Składniki:** pobieranieKursow.py, pobieranieWynikow.py, dodawanieWynikow.py, generatorDataBase.py, generatorDataBaseTrendAnalisAll.py
**Dane Wyjsciowe:** kursy_przygotowane.csv, bazy danych z cechami
**Integracja:** Dostarcza dane do V2 (60% trening, 40% obserwacja)

### 4.2. V2 Model Laboratory
**Odpowiedzialnosc:** Tworzenie wielu modeli interpretujacych swiat
**Zasada 60/40:** 60% danych trening + walidacja, 40% obserwacja i wykrywanie wzorców
**Modele:** siec_01_zmiana_kursow, siec_02_amplituda, siec_03_tempo, siec_04_synchronizacja, RandomForest
**Integracja:** Wejscie: V1, Wyjscie: Modele do V3

### 4.3. V3 World Memory System
**Odpowiedzialnosc:** Budowa mapy wiedzy o swiatach, pamięciach i wzorcach
**V3 NIE podejmuje decyzji** - Tworzy jedynie srodowisko wiedzy
**Komponenty:** World Memory, Group Memory, Pattern Memory, Historical Results, System tagowania (7 kategorii), Analiza ekonomiczna
**Swiaty:** zmiana_kursow, dynamiki, klasyfikacji, relacji
**Integracja:** Wejscie: Modele z V2, Wyjscie: Wiedza do V4

### 4.4. V4 Autonomous Agent Evolution
**Odpowiedzialnosc:** Tworzenie autonomicznych jednostek decyzyjnych, ewolucja osobowosci
**Kluczowa Zasada:** V4 NIE zastępuje V3. V4 jest warstwa wykonujaca decyzje na podstawie wiedzy z V2 i V3.
**Pierwsza Populacja:** Agent 1 (Analityk), Agent 2 (Strateg W'artosci), Agent 3 (Eksperymentator)
**Cykl Agenta:** Wczytaj pamiec -> Pobierz dane -> Porownaj STARA WIEDZA + NOWE DANE -> Analiza -> Decyzja -> Zapis doswiadczenia -> Aktualizacja historii

### 4.5. V5 System Orchestration
**Odpowiedzialnosc:** Zarzadzanie cyklem pracy calego systemu, koordynacja pracy agentow
**Komponenty (z SSI/v5/runtime/):**
- RuntimeController: Glowna petla sterowania, inicjalizacja, zarzadzanie cyklem, kontrola agentow, integracja z collectorami, zapis stanu
- StateManager: Zarzadzanie stanem (RuntimeState, AgentState, MemoryState, CollectorState)
- Scheduler: Planowanie zadan, zarzadzanie kolejka (CycleConfig), koordynacja sekwencyjna
- AgentManager: Zarzadzanie 6 agentami (01-06), kontrola kolejnosci wykonania

---

## 5. OGRANICZENIA SPRZETOWE

**WAZNE:** Tylko 1 aktywny model LLM na raz. Modele nie dzialaja jednoczesnie.

**Orchestrator zarzadza kolejka:**
MODEL A START -> WORK -> SAVE MEMORY -> MODEL A STOP ->
MODEL B START -> WORK -> SAVE MEMORY -> MODEL B STOP ->
MODEL C START -> ...

**Sekwencja dla 6 agentow:**
1. Agent 01: MODEL START
2. Agent 01: WORK (cykl agenta)
3. Agent 01: SAVE MEMORY
4. Agent 01: MODEL STOP
5. Agent 02: MODEL START (tylko gdy Agent 01 MODEL STOP)
6. Agent 02: WORK
7. Agent 02: SAVE MEMORY
8. Agent 02: MODEL STOP
9. ... (powtarzaj dla Agent 03-06)

**Zapewnia:** RuntimeController + Scheduler

---

## 6. INPUT LAYER ARCHITECTURE

**Odpowiedzialnosc:** Zbieranie danych z roznorodnych zrodel, normalizacja, walidacja, dostarczanie do odpowiednich modulow

**Komponenty (z SSI/v5/input_layer/):**
- CollectorManager: Glowny manager collectorow, koordynacja pracy V2, V3, V4, External
- V2Collector: Zbieranie danych swiatowych, integracja z V2 Model Laboratory
- V3Collector: Zbieranie bazy wiedzy, integracja z V3 World Memory System
- V4Collector: Zbieranie danych o agentach, integracja z V4 Agent Evolution
- ExternalCollector: Zbieranie danych zewnetrznych

**Przeplyw danych:**
CollectorManager
├── V2Collector -> V2 Model Laboratory
├── V3Collector -> V3 World Memory System
├── V4Collector -> V4 Agent Evolution
└── ExternalCollector -> External Sources

---

## 7. MODULES I LABORATORIA

### 7.1. Decision Engine
**Odpowiedzialnosc:** Ostateczna ocena decyzji agentow, wybór najlepszych opcji, optymalizacja strategii
**Formula Oceny:** Wartosc Decyzji = trafnosci x kurs x powtarzalnosc x stabilnosc - ryzyko

### 7.2. Strategy Laboratory
**Odpowiedzialnosc:** Zarzadzanie strategiami produkcyjnymi i eksperymentalnymi
**Proces:** Pomysl -> Test -> Ocena -> Ranking -> Akceptacja
**Typy:** Production Strategies (rankingowane, uzywane) + Experimental Strategies (nowe pomysly, testy)
**Integracja:** Kazdy agent ma wlasny ranking strategii. Agenci NIE kopiuja strategii innych - moga analizowac i tworzyc wlasne ulepszenia.

### 7.3. Memory Evolution System
**Odpowiedzialnosc:** Ewolucja pamieci od surowych doswiadczen do aktywnej wiedzy
**Cykl Pamieci:** DOSWIADCZENIE -> PAMIEC SUROWA -> DOJRZEWANIE -> OBSERWACJA -> OCENA -> RANKING -> STRATEGIA -> SLAD DOSWIADCZENIA
**Stany Pamieci:** NOWA -> DOJRZEWAJACA -> OBSERWOWANA -> ANALIZOWANA -> AKTYWNA -> ARCHIWALNA
**Dwuwarstwowa Pamiec:** Global Memory (wspolna wiedza) + Private Notebook (prywatne hipotezy)

### 7.4. AI Lab Request Pipeline
**Odpowiedzialnosc:** Zarzadzanie zadaniami do drugiego komputera (AI Laboratory)
**Przeplyw:** MAIN SSI -> AI LAB REQUEST QUEUE -> DRUGI KOMPUTER -> WYNIK -> SSI MEMORY
**Ograniczenia:** Drugi komputer NIE dziala stale, aktywowany tylko na zadanie
**Zgodnosc z ograniczeniem sprzetowym:** Drugi komputer traktowany jak kolejny model w kolejce (MODEL START -> WORK -> SAVE MEMORY -> MODEL STOP)

### 7.5. Prompt Management System
**Odpowiedzialnosc:** Zarzadzanie promptami z kategoriami: system_prompts, agent_prompts, developer_prompts, laboratory_prompts
**Atrybuty Promptu:** prompt_id, autor, wersja, cel, wynik, historia

### 7.6. Developer Input Architecture
**Odpowiedzialnosc:** Przetwarzanie poden programisty
**Przeplyw:** PROGRAMISTA -> Developer Command Interface -> Governance Validation -> Information Flow Controller -> Orchestrator -> Modul
**Zasada:** Programista NIE komunikuje sie bezposrednio z modulami

---

## 8. ZARZADZANIE PAMIECIA

### 8.1. Agent Memory Structure
Kazdy agent posiada **wlasna pamiec** organizowana w 4 typach:

**1. PERSONALITY Memory**
- Parametry osobowosci: cechy, wektor ewolucji
- Historia zmian osobowosci
- Wplyw doswiadczen na charakter

**2. BEHAVIOR Memory**
- Decyzje: historia, kontekst, wyniki
- Predykcje: hipotezy, weryfikacja, celnosc
- Katalog wynikow: klasyfikacja, ocena
- Ranking strategii: liczba uzyc, sukcesy, porazki, skutecznosc, pewnosc, wplyw

**3. STRATEGY Memory**
- Strategie produkcyjne: ranking, parametry, wyniki
- Strategie eksperymentalne: pomysly, testy, ocena
- Historia strategii: ewolucja, adaptacja

**4. HISTORY Memory**
- Historia sukcesow i bledow
- Statystyki: trafnosc, skutecznosc, powtarzalnosc
- Kontekst historyczny

### 8.2. System Memory vs Agent Memory
| Aspekt | System Memory | Agent Memory |
|--------|---------------|--------------|
| Zakres | Globalny | Indywidualny |
| Udostepnianie | Wspolne | Prywatne |
| Aktualizacja | Centralna | Przez agenta |
| Zawartosc | Potwierdzona wiedza | Hipotezy, doswiadczenia |
| Trwalosc | Dlugoterminowa | Dlugoterminowa |

---

## 9. SYGNALY I KOMUNIKACJA

### 9.1. Typy Sygnalow
| Typ Sygnalu | Opis | Kierunek | Priorytet |
|------------|------|----------|-----------|
| DECISION_SIGNAL | Decyzja agenta | Agent -> Decision Engine | High |
| ERROR_SIGNAL | Blad przetwarzania | Module -> System | Critical |
| MEMORY_UPDATE | Aktualizacja pamieci | Agent -> Memory | Medium |
| STRATEGY_REQUEST | Zadanie testu strategii | Agent -> Strategy Lab | Low |
| AI_LAB_REQUEST | Zadanie do AI Lab | Module -> AI Lab Queue | Medium |
| STATE_CHANGE | Zmiana stanu systemu | System -> All | High |
| SHUTDOWN_REQUEST | Zadanie zatrzymania | External -> System | Critical |

---

## 10. TEST MODE VS PRODUCTION MODE

### 10.1. Test Mode
- 10 cykli pelnych
- 60 iteracji (6 agentow x 10 cykli)
- Szybkie wykonanie
- Pelna weryfikacja systemu
- Warunek zakonczenia: 10 cykli

### 10.2. Production Mode
- 5 godzin ciagłej pracy
- Ciagłe cykle
- Pelna funkcjonalnosc
- Zapis stanu po kazdym cyklu
- Warunek zakonczenia: 5 godzin

---

## 11. INTEGRACJA Z ISTNIEJACYMI MODULAMI

### 11.1. Runtime Controller Integration
**runtime_controller.py** implementuje:
- initialize() -> Inicjalizacja systemu
- start_cycle() -> Rozpoczecie cyklu
- run_cycle() -> Wykonanie cyklu
- save_state() -> Zapis stanu
- load_previous_state() -> Wczytanie poprzedniego stanu
- shutdown() -> Zatrzymanie systemu
- get_status() -> Pobranie statusu

### 11.2. Agent Runtime Integration
**agent_runtime.py** implementuje cykl agenta:
1. Wczytaj pamiec
2. Pobierz dane (V2, V3, V4, External)
3. Porownaj: STARA WIEDZA + NOWE DANE
4. Analiza
5. Decyzja
6. Zapis doswiadczenia
7. Aktualizacja historii

### 11.3. State Manager Integration
**state_manager.py** zarzadza:
- RuntimeState: stan systemu runtime
- AgentState: stan kazdego agenta
- MemoryState: stan pamieci
- CollectorState: stan collectorow

---

## 12. HIERARCHIA DOKUMENTOW

```
SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md (Ten dokument - PODSTAWA)
├── 01_SYSTEM_SIGNAL_ARCHITECTURE.md
│   └── input -> PROCESS -> OUTPUT -> SIGNAL -> MEMORY UPDATE
├── 02_DEVELOPER_INPUT_ARCHITECTURE.md
│   └── PROGRAMISTA -> Developer Command Interface -> Governance -> ...
├── 03_PROMPT_MANAGEMENT_SYSTEM.md
│   └── Zarzadzanie promptami: ID, autor, wersja, cel, wynik, historia
├── 04_AGENT_MEMORY_BEHAVIOR_EVOLUTION.md
│   ├── Ewolucja zachowania agentow
│   └── Pamiec: decyzji, predykcji, strategii, bledow, sukcesow, eksperymentow
├── 05_STRATEGY_LABORATORY_ARCHITECTURE.md
│   ├── Production Strategies + Experimental Strategies
│   └── Pomysl -> Test -> Ocena -> Ranking -> Akceptacja
└── 06_AI_LAB_REQUEST_PIPELINE.md
    └── MAIN SSI -> AI LAB REQUEST QUEUE -> DRUGI KOMPUTER -> WYNIK -> SSI MEMORY
```

---

## 13. ELEMENTY NIE DO PRZEBUDOWY

**Zgodnie ze zleceniem, NIE przebudowywac:**
- Teacher Architecture
- Agent System
- Memory Ecosystem
- Information Flow
- System Orchestration
- System Governance
- V1/V5 Lifecycle

**Nowe dokumenty sa warstwa uzupelniajaca do istniejecej privilegii.**

---

## 14. KOLEJNOSC TWORZENIA DOKUMENTOW

1. SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md (Ten dokument) ✅
2. 01_SYSTEM_SIGNAL_ARCHITECTURE.md
3. 02_DEVELOPER_INPUT_ARCHITECTURE.md
4. 03_PROMPT_MANAGEMENT_SYSTEM.md
5. 04_AGENT_MEMORY_BEHAVIOR_EVOLUTION.md
6. 05_STRATEGY_LABORATORY_ARCHITECTURE.md
7. 06_AI_LAB_REQUEST_PIPELINE.md

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** DRAFT - Gotowy do przegladu  
**Autor:** Mistral Vibe - CLI Coding Agent  
**Nastepny dokument:** 01_SYSTEM_SIGNAL_ARCHITECTURE.md  

---

**Powiazane Dokumenty:**
- SSI_V5_CURRENT_STATE_AUDIT.md
- SSI_V5_ARCHITECTURE_PHASE_REPORT.md
- SSI/v5/runtime/runtime_controller.py
- SSI/v5/runtime/state_manager.py
- SSI/v5/agents/agent_runtime.py
