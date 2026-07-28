# SSI System Architecture
## Pełna Architektura Techniczna Self Learning Intelligence Ecosystem

[TAGS: ARCHITECTURE, MODULE, COMPONENT, DEPENDENCY, FLOW]

---

## 1. Hierarchia Systemu SSI

### 1.1 Pełny Przepływ Architektury

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA INTELLIGENCE LAYER                      │ [DATA]
│  Źródło: pobieranieKursow.py, pobieranieWynikow.py, dodawanieWynikow.py │
│  Generatory: generatorDataBase.py, generatorDataBaseTrendAnalisAll.py│
│  Wyjście: kursy_przygotowane.csv, wyniki, historia zdarzeń          │
└──────────────────────────────┬──────────────────────────────────┘
                                ↓ [DEPENDENCY: DATA → V2]
┌─────────────────────────────────────────────────────────────────┐
│                         V2 — MODEL LABORATORY                        │ [MODULE]
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  MODELE:                                                   ││
│  │  - siec_01_zmiana_kursow (Świat zmian kursów)                ││
│  │  - siec_02_amplituda (Świat amplitudy)                       ││
│  │  - siec_03_tempo (Świat dynamiki)                          ││
│  │  - siec_04_synchronizacja (Świat synchronizacji)            ││
│  │  - RandomForest                                           ││
│  │  - Klasyfikatory                                          ││
│  └─────────────────────────────────────────────────────────────┘│
│  Podział danych: 60% trening + 40% niezależna obserwacja          │
│  Cel: Wiele sposobów interpretacji świata                         │
└──────────────────────────────┬──────────────────────────────────┘
                                ↓ [DEPENDENCY: V2 → V3]
┌─────────────────────────────────────────────────────────────────┐
│                      V3 — WORLD MEMORY SYSTEM                       │ [MODULE]
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  ŚWIATY:                                                   ││
│  │  - Świat zmian kursów (zmiana_1, zmiana_X, zmiana_2)       ││
│  │  - Świat dynamiki (amplituda, tempo, wahania, synchronizacja)││
│  │  - Świat klasyfikacji (log_start, log_koniec, relacje)       ││
│  └─────────────────────────────────────────────────────────────┘│
│  PAMIĘCI:                                                      │
│  - World Memory (pamięć światów)                             │
│  - Group Memory (pamięć grup)                                │
│  - Pattern Memory (pamięć wzorców)                           │
│  - Historical Results (historia wyników)                     │
│  METADANE:                                                   │
│  - Tagowanie (7 kategorii: wynik, zachowanie, skuteczność,       │
│    odchylenia, ekonomia, zależności, strategiczne)           │
│  - Zależności między światami                                │
│  - Analiza ekonomiczna (wartość oczekiwana, kurs, ryzyko)      │
│  - Odwrócone wzorce                                         │
│  V3 NIE podejmuje decyzji. Tworzy mapę wiedzy.                  │
└──────────────────────────────┬──────────────────────────────────┘
                                ↓ [DEPENDENCY: V3 → V4]
┌─────────────────────────────────────────────────────────────────┐
│                   V4 — AUTONOMOUS AGENT EVOLUTION                  │ [MODULE]
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  AGENT BIRTH SYSTEM:                                      ││
│  │  - Utworzenie agenta → nadanie parametrów → inicjalizacja    ││
│  │    osobowości → dodanie do ROOM_CORE → rozpoczęcie ewolucji  ││
│  └─────────────────────────────────────────────────────────────┘│
│  PIERWSZA POPULACJA (3 agenci):                              │
│  - Agent 1: Analityk (wysoka analiza, wysoka ostrożność)        │
│  - Agent 2: Strateg Wartości (akceptacja ryzyka, analiza kursu)  │
│  - Agent 3: Eksperymentator (ciekawość, testowanie hipotez)      │
│  ROOM_CORE: Pokój narodzin i komunikacji                        │
│  V4 korzysta z: World Memory, Group Memory, Pattern Memory,     │
│  Historical Results, Model Evaluation, Strategy Engine, Feedback Loop│
└──────────────────────────────┬──────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LABORATORIA DECYZYJNE                           │ [MODULE]
│  ┌────────────────┬────────────────┬────────────────┐          │
│  │ Laboratorium    │ Laboratorium    │ Laboratorium    │          │
│  │ świata          │ grup            │ kuponów         │          │
│  ├────────────────┼────────────────┼────────────────┤          │
│  │ - wybór świata  │ - ilość meczy   │ - ilość grup    │          │
│  │ - wybór modelu  │ - poziom ryzyka  │ - kombinacje     │          │
│  │ - wybór danych  │ - układ grup    │ - opłacalność    │          │
│  │ - wybór strategi│                 │ - ryzyko całk.   │          │
│  └────────────────┴────────────────┴────────────────┘          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Laboratorium strategii:                                    ││
│  │  - Tworzenie nowych strategii                             ││
│  │  - Testowanie strategii                                   ││
│  │  - Rozwój strategii                                       ││
│  └─────────────────────────────────────────────────────────────┘│
└──────────────────────────────┬──────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                    STRATEGY INTELLIGENCE ENGINE                   │ [MODULE]
│  StrategyObject:                                              │
│  - strategy_id, world_reference, model_reference               │
│  - features, training_data, prediction_generator                 │
│  - parameters, results_history, value_score, status             │
│  Generator strategii:                                         │
│  - stare strategie + nowa wiedza + doświadczenie → nowa strategia│
│  Cykl życia strategii:                                       │
│  NARODZINY → NOWA → TEST → DOJRZEWANIE → OBSERWACJA →            │
│  ANALIZA → RANKING → AKTYWNA → SPADEK → ARCHIWUM                │
│  System ligi: A+ → A → B → C → D                                │
│  Experience Trace: pełna historia strategii (nigdy nie usuwana) │
└──────────────────────────────┬──────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                   MEMORY EVOLUTION SYSTEM                         │ [MODULE]
│  Cykl pamięci:                                                │
│  DOŚWIADCZENIE → PAMIĘĆ SUROWA → DOJRZEWANIE → OBSERWACJA →   │
│  OCENA → RANKING → STRATEGIA → ŚLAD DOŚWIADCZENIA               │
│  Stany pamięci: NOWA → DOJRZEWAJĄCA → OBSERWOWANA →             │
│  ANALIZOWANA → AKTYWNA → ARCHIWALNA                             │
│  DWUWARSTWOWA PAMIĘĆ:                                        │
│  - Global Memory (wspólna, potwierdzona wiedza)                 │
│  - Private Notebook (prywatne hipotezy, pomysły)               │
└──────────────────────────────┬──────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DECISION ENGINE                              │ [MODULE]
│  - Wybór decyzji                                             │
│  - Ocena wartości: trafność × kurs × powtarzalność × stabilność - ryzyko│
│  - Optymalizacja strategii                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Szczegółowa Architektura Warstw

### 2.1 Warstwa 1: Data Intelligence Layer

**[MODULE]**
- **Cel:** Pobieranie, archiwizacja i przygotowywanie danych pierwotnych
- **Odpowiedzialność:**
  - Pobieranie kursów i wyników
  - Archiwizacja historyczna
  - Generowanie baz danych
  - Przygotowywanie trendów i cech
- **Składniki:**
  - `pobieranieKursow.py` - Pobieranie kursów bukmacherskich
  - `pobieranieWynikow.py` - Pobieranie wyników meczów
  - `dodawanieWynikow.py` - Dodawanie wyników do historii
  - `generatorDataBase.py` - Generowanie bazy danych meczów
  - `generatorDataBaseTrendAnalisAll.py` - Analiza trendów
- **Dane Wyjściowe:**
  - `kursy_przygotowane.csv` - Kursy gotowe do analizy
  - Bazy danych z cechami i parametrami
  - Historia zdarzeń i zmian

**[TAGS: DATA, MODULE, FLOW]**

---

### 2.2 Warstwa 2: V2 Model Laboratory

**[MODULE]**
- **Cel:** Tworzenie wielu modeli interpretujących świat
- **Odpowiedzialność:**
  - Szkolenie modeli na 60% danych
  - Niezależna obserwacja na 40% danych
  - Każdy model tworzy własny świat interpretacji
- **Modele:**
  - `siec_01_zmiana_kursow` - Analiza zmian kursów (1, X, 2)
  - `siec_02_amplituda` - Analiza amplitudy zmian
  - `siec_03_tempo` - Analiza tempa zmian
  - `siec_04_synchronizacja` - Analiza synchronizacji kursów
  - RandomForest - Klasyfikator lasu losowego
  - Inne klasyfikatory
- **Zasada 60/40:**
  - 60% danych: trening + walidacja
  - 40% danych: NIE uczy modelu, służy do obserwacji, tworzenia pamięci, wykrywania wzorców

**[TAGS: MODEL, MODULE, FLOW, DEPENDENCY]**

---

### 2.3 Warstwa 3: V3 World Knowledge Engine

**[MODULE]**
- **Cel:** Budowa mapy wiedzy o światach, pamięciach i wzorcach
- **Odpowiedzialność:**
  - Tworzenie światów wiedzy
  - Budowa pamięci świata
  - Generowanie metadanych
  - Tagowanie informacji
  - Analiza zależności
  - Wykrywanie odwróconych wzorców
- **V3 NIE podejmuje decyzji** - Tworzy jedynie środowisko wiedzy
- **Komponenty:**
  - World Memory - Pamięć światów
  - Metadane modeli
  - System tagowania (7 kategorii)
  - Analiza ekonomiczna
  - Wartość oczekiwana (EV)

** ŚWIATY V3:**
- Świat zmian kursów: `zmiana_1`, `zmiana_X`, `zmiana_2`
- Świat dynamiki: `amplituda_1`, `amplituda_X`, `amplituda_2`, `tempo_1`, `tempo_X`, `tempo_2`, `synchronizacja`, `max_wahanie_1`, `max_wahanie_X`, `max_wahanie_2`
- Świat klasyfikacji: `log_start_1`, `log_start_X`, `log_start_2`, `log_koniec_1`, `log_koniec_X`, `log_koniec_2`
- Świat relacji: `ratio_1X_start`, `ratio_1_2_start`, `ratio_X2_start`, `ratio_1X_koniec`, `ratio_1_2_koniec`, `ratio_X2_koniec`

**[TAGS: WORLD, MEMORY, MODULE, ARCHITECTURE]**

---

### 2.4 Warstwa 4: V4 Autonomous Agent Evolution

**[MODULE]**
- **Cel:** Tworzenie autonomicznych jednostek decyzyjnych
- **Odpowiedzialność:**
  - Narodziny agentów
  - Ewolucja osobowości
  - System zaufania między agentami
  - Podejmowanie decyzji na podstawie wiedzy z V3
- **Zależności:**
  - World Memory (z V3)
  - Group Memory (z V3)
  - Pattern Memory (z V3)
  - Historical Results (z V3)
  - Model Evaluation (z V2)
  - Strategy Engine
  - Feedback Loop
- **Kluczowa Zasada:** V4 NIE zastępuje V3. V4 jest warstwą wykonującą decyzje na podstawie wiedzy zgromadzonej przez V2 i V3.

**[TAGS: AGENT, MODULE, EVOLUTION, ARCHITECTURE, DEPENDENCY]**

---

## 3. Mechanizmy Przetwarzania

### 3.1 Przepływ Danych (Data Flow)

**[FLOW]**
```
Data Layer (CSV files)
  ↓
V2 Model Laboratory (Training 60% / Observation 40%)
  ↓
V3 World Memory System (Worlds, Memories, Metadata, Patterns)
  ↓↓↓
  └──> V4 Agent Evolution (Agents analyze and make decisions)
        ↓
  ┌─────────────────────────────────────────────┐
  │ Laboratoria (Decision, Group, Coupon, Strategy)│
  └──────────────────────┬──────────────────────┘
                         ↓
                  Strategy Intelligance Engine
                         ↓
                  Memory Evolution System
                         ↓
                  Decision Engine
                         ↓
                  Results & New Experiences
                         ↓
                  Back to V4 Agents (Evolution)
```

### 3.2 Zależności Międzykomponentowe

**[DEPENDENCY]**

| Komponent | Zależy od | Dostarcza do |
|-----------|-----------|---------------|
| V2 Model Laboratory | Data Layer | V3 World Memory System |
| V3 World Memory System | V2 Model Laboratory | V4 Agent Evolution |
| V4 Agent Evolution | V3, V2 | Decision Laboratories |
| Decision Laboratories | V4, V3 | Strategy Engine |
| Strategy Engine | Decision Laboratories | Memory Evolution |
| Memory Evolution | Strategy Engine | Decision Engine |
| Decision Engine | Memory Evolution | Results |

---

## 4. Architektura Komponentów V4

### 4.1 Agent Birth System

**[COMPONENT]**
- **ID:** `AGENT_BIRTH_SYSTEM`
- **Typ:** `Agent Initialization Module`
- **Rola:** Tworzenie pierwszej populacji agentów
- **Proces:**
  1. START SYSTEM
  2. utworzenie agenta
  3. nadanie parametrów początkowych
  4. inicjalizacja osobowości
  5. dodanie do ROOM_CORE
  6. rozpoczęcie ewolucji

### 4.2 ROOM_CORE

**[COMPONENT]**
- **ID:** `ROOM_CORE`
- **Typ:** `Agent Communication Environment`
- **Rola:** Pierwsze środowisko działania agentów
- **Proces:**
  1. Agent otrzymuje osobowość startową
  2. Agent przedstawia swoje parametry
  3. Agent poznaje inne jednostki
  4. Rozpoczyna wymianę informacji

### 4.3 Personality Vector Engine

**[COMPONENT]**
- **ID:** `PERSONALITY_VECTOR_ENGINE`
- **Typ:** `Adaptive Agent Profile`
- **Rola:** Zarządzanie dynamicznym wektorem parametrów osobowości

### 4.4 Personality Evolution Engine

**[COMPONENT]**
- **ID:** `PERSONALITY_EVOLUTION_ENGINE`
- **Typ:** `Adaptive Learning Mechanism`
- **Rola:** Zmiana charakteru agenta na podstawie doświadczeń

### 4.5 Emotional Control System

**[COMPONENT]**
- **ID:** `EMOTIONAL_CONTROL_SYSTEM`
- **Typ:** `Decision Regulation Mechanism`
- **Rola:** Matematyczne parametry sterujące zachowaniem

### 4.6 Resilience Engine

**[COMPONENT]**
- **ID:** `RESILIENCE_ENGINE`
- **Typ:** `Failure Recovery Mechanism`
- **Rola:** Zapewnienie odporności na błędy

### 4.7 Trust Memory

**[COMPONENT]**
- **ID:** `TRUST_MEMORY`
- **Typ:** `Agent Relationship Memory`
- **Rola:** Ocena jakości informacji przekazywanych przez innych agentów

---

## 5. Podsumowanie Zależności

### Hierarchia Zależności
```
DATA_LAYER
  └── V2_MODEL_LABORATORY
        └── V3_WORLD_MEMORY_SYSTEM
              └── V4_AGENT_EVOLUTION
                    ├── AGENT_BIRTH_SYSTEM
                    ├── PERSONALITY_ENGINE
                    ├── RESILIENCE_ENGINE
                    ├── TRUST_MEMORY
                    └── DECISION_LABORATORIES
                          ├── DECISION_LAB
                          ├── GROUP_LAB
                          ├── COUPON_LAB
                          └── STRATEGY_LAB
                                └── STRATEGY_ENGINE
                                      └── MEMORY_EVOLUTION
                                            └── DECISION_ENGINE
```

### Typy Zależności
- **[STRONG DEPENDENCY]** - V2 → V3 → V4 (konieczne do działania)
- **[DATA DEPENDENCY]** - V4 korzysta z pamięci V3
- **[FEEDBACK DEPENDENCY]** - Wyniki → Aktualizacja pamięci
- **[EVOLUTION DEPENDENCY]** - Doświadczenia → Ewolucja agentów

---

## 6. Diagrams

### 6.1 UML Class Diagram (Podstawowe klasy)
```
┌───────────────────────┐
│      DataLayer         │
├───────────────────────┤
│ + load_courses()       │
│ + load_results()       │
│ + generate_database()  │
└────────────┬──────────┘
             ↓
┌───────────────────────┐
│      V2ModelLab        │
├───────────────────────┤
│ - models[]            │
│ + train_models()       │
│ + observe_models()     │
└────────────┬──────────┘
             ↓
┌───────────────────────┐
│     V3WorldMemory      │
├───────────────────────┤
│ - worlds[]             │
│ - memories[]           │
│ - metadata             │
│ + create_worlds()      │
│ + tag_information()    │
└────────────┬──────────┘
             ↓
┌───────────────────────┐
│     V4AgentEvolution   │
├───────────────────────┤
│ - agents[]            │
│ + create_agent()       │
│ + evolve_personality() │
│ + make_decision()      │
└───────────────────────┘
```

---

**Status Dokumentu:** Kompletny  
**Wersja:** 4.0  
**Zgodność z Źródłami:** stuktura1.csv, stuktura2.csv, stuktura3.csv, stuktura4.csv  
**Ostatnia Aktualizacja:** 28.07.2026
