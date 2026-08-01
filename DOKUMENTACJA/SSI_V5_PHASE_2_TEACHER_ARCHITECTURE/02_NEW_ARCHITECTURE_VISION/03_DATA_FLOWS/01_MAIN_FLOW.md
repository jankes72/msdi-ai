# SSI V5 PHASE 2: MAIN DATA FLOW

**Sprint:** 12+ (Phase 2 Foundation)
**Data:** 2026-08-01
**Wersja:** 1.0.0
**Status:** Draft / In Progress
**Autor:** Glowny Architekt SSI V5

---

## SPIS TRESCI

1. [Podsumowanie Glownego Przeplywu](#1-podsumowanie-glownego-przeplywu)
2. [Cykl Dobowy Systemu](#2-cykl-dobowy-systemu)
3. [Faza 0200 - Aktualizacja Wynikow](#3-faza-0200---aktualizacja-wynikow)
4. [Faza 0200-0800 - Feedback Loop](#4-faza-0200-0800---feedback-loop)
5. [Faza 0800 - Nowe Dane Wejsciowe](#5-faza-0800---nowe-dane-wejsciowe)
6. [Faza 0800-1000 - Praca Laboratoriow](#6-faza-0800-1000---praca-laboratoriow)
7. [Faza 1000 - Generowanie Decyzji](#7-faza-1000---generowanie-decyzji)
8. [Szczegoly Przeplywu Miedzy Warstwami](#8-szczegoly-przeplywu-miedzy-warstwami)
9. [Przeplyw Wiedzy Teacher Models](#9-przeplyw-wiedzy-teacher-models)
10. [Memory Update Flow](#10-memory-update-flow)
11. [Error Handling i Recovery](#11-error-handling-i-recovery)

---

## 1. PODSUMOWANIE GLOWNEGO PRZEPLYWU

### 1.1 Macierz Przeplywu Systemu

```
DATA (02:00)
   |
   v
MEMORY (UnifiedInputPackage)
   |
   v
RUNTIME LAYER (Agent Decisions)
   |
   v
MEMORY LAYER (Context & State)
   |
   v
ANALYSIS LAYER (Memory Context Builder + Prompt Router)
   |
   v
TEACHER MODELS LAYER (Feedback + Learning Updates)
   |
   v
FEEDBACK LAYER (Memory Update + System Learning)
   |
   v
MEMORY (Updated State)
   |
   +---> NEXT CYCLE (02:00)
```

### 1.2 Podsumowanie Cyklu

**Calkowity czas cyklu:** 24 godziny
**Czas aktywnosci systemu:** ~4 godziny (02:00-06:00 + 08:00-10:00)
**Czas uczenia i analizy:** ~2 godziny
**Czas gotowosci do decyzji:** 10:00

---

## 2. CYKL DOBOWY SYSTEMU

### 2.1 Harmonogram

| **Godzina** | **Faza** | **Modul** | **Czas Trwania** | **Wyjsciowy Stan** |
|-------------|----------|-----------|------------------|---------------------|
| 02:00 | Aktualizacja Wynikow | Data Layer | 1 min |wyniki.csv zaktualizowane |
| 02:00-08:00 | Feedback Loop | Feedback Layer | 6 godz. | Memory zaktualizowane |
| 08:00 | Nowe Dane Wejsciowe | Data Layer | 1 min | UnifiedInputPackage gotowy |
| 08:00-10:00 | Praca Laboratoriow | Teacher Models + Analysis Layer | 2 godz. | Strategie wybrany |
| 10:00 | Gotowosc Systemu | Runtime Layer | - | System gotowy do decyzji |

---

## 3. FAZA 02:00 - AKTUALIZACJA WYNIKOW

### 3.1 Input

**Zrodlo:** `/dane/wyniki.csv`
**Format:**
- **Kodowanie:** UTF-8
- **Separator:** `;`
- **Struktura:**
  - INDEKS 0: nazwa meczu (string)
  - INDEKS 1: wynik (string, format "X:Y")

**Przyklad:**
```csv
FC Barcelona-Real Madrid;2:1
Liverpool-Chelsea;0:0
Juventus-AC Milan;3:2
```

**Interpretacja:**
- Pierwsza wartosc: gole gospodarzy
- Druga wartosc: gole gosci
- **ZASADA:** Zawsze GOSPODARZE:GOSCIE - NIGDY nie odwracac kolejnosci

### 3.2 Process

```
1. System wykrywa nowy plik /dane/wyniki.csv
2. Parsowanie pliku CSV z separatorem ";"
3. Walidacja formatu:
   - Sprawdzenie kodowania UTF-8
   - Sprawdzenie separatora ";"
   - Walidacja formatu wyniku (X:Y)
4. Mapowanie meczy na wewnetrzne ID
5. Porownanie z oczekiwanymi rezultatami z systemu
6. Przygotowanie InputPackage dla Feedback Loop
```

### 3.3 Output

**ResultsInputPackage:**
```json
{
  "timestamp": "2026-08-01T02:00:00Z",
  "cycle_id": "CYCLE_20260801",
  "source_file": "/dane/wyniki.csv",
  "results_count": 147,
  "results": [
    {
      "match_id": "MATCH_20260801_001",
      "match_name": "FC Barcelona-Real Madrid",
      "expected_result": "2:1",
      "actual_result": "2:1",
      "result_type": "HOME_WIN",
      "is_correct": true
    },
    {
      "match_id": "MATCH_20260801_002", 
      "match_name": "Liverpool-Chelsea",
      "expected_result": "1:0",
      "actual_result": "0:0", 
      "result_type": "DRAW",
      "is_correct": false
    }
  ],
  "statistics": {
    "total_matches": 147,
    "correct_predictions": 112,
    "incorrect_predictions": 35,
    "accuracy": 0.7619
  }
}
```

### 3.4 Memory Used
- Agent Memory (history.json)
- Collective Memory (team_decisions.json)
- Laboratory Memory (experiment_predictions.json)

### 3.5 Memory Updated
- **NEW:** Results Memory (tymczasowa pamięć wyników)

### 3.6 Next Module
- Trigger: `FEEDBACK_LOOP` (Faza 02:00-08:00)

### 3.7 Error Handling
- **BLAD_PARSOWANIA:** Jesli plik nie moze zostac sparsowany, system generuje alert i kontynuuje z poprzednimi danymi
- **BLAD_FORMATU:** Jesli format wyniku jest nieprawidlowy, pomija mecz i loguje blad
- **BLAD_BRAKU_PLIKU:** Jesli plik nie istnieje o 02:15, system zaklada brak nowych wynikow i przerywa Feedback Loop

---

## 4. FAZA 02:00-08:00 - FEEDBACK LOOP

### 4.1 Podfazy

#### 4.1.1 Podfaza A: Porownanie Predykcji (02:00-02:30)

**Input:** ResultsInputPackage

**Process:**
1. System laduje wszystkie predykcje od agentow (V2, V3, V4, Teacher Models)
2. Porownuje kazda predykcje z rzeczywistym wyniki
3. Oblicza accuracy dla kazdego agenta
4. Tworzy raport trafien

**Output:** ComparisonReport

**Memory Updated:**
- Agent Memory (stats.json - accuracy update)
- Collective Memory (team_performance.json)

#### 4.1.2 Podfaza B: Analiza Bledow (02:30-04:00)

**Input:** ComparisonReport

**Process:**
1. Teacher Models analizuja wszystkie bledne predykcje
2. Agent Teacher:
   - Analizujez decyzyjne pojedynczych agentow
   - Sprawdza wykorzytana pamiec i strategie
   - Identyfikuje bledne wzorce
3. Collective Teacher:
   - Porownuje decyzje wszystkich agentow
   - Wykrywa konflikty i rozbieznosci
   - Buduje konsensus na przyszlosc
4. Laboratory Teacher:
   - Analizuje wyniki eksperymentow
   - Porownuje strategie laboratoryjne z rzeczywistosci

**Output:** ErrorAnalysisReport

**Memory Updated:**
- Teacher Memory (analysis_history.json)
- Laboratory Memory (experiment_results.json)

#### 4.1.3 Podfaza C: Generowanie Feedbacku (04:00-06:00)

**Input:** ErrorAnalysisReport

**Process:**
1. Agent Teacher generuje feedback dla kazdego agenta
2. Collective Teacher generuje rekomendacje zespołowe
3. Laboratory Teacher generuje wnioski z eksperymentow
4. Tworzone sa Learning Updates dla wszystkich warstw

**Output:** FeedbackPackage

**Memory Updated:**
- Agent Memory (prompt_memory.json - new feedback)
- Collective Memory (recommendations.json)
- Long Term Memory (lessons_learned.json)

#### 4.1.4 Podfaza D: Aktualizacja Pamieci (06:00-08:00)

**Input:** FeedbackPackage

**Process:**
1. Memory Update System aplikuje wszystkie Learning Updates
2. Aktualizowane sa:
   - Agent Memory (6 agentow x 8 typow pamięci)
   - Collective Memory
   - Long Term Memory
   - Laboratory Memory
   - Teacher Memory
3. Tworzone sa backupy pamieci
4. System sprawdza integralnosc pamieci

**Output:** UpdatedMemoryState

**Memory Updated:** Wszystkie typy pamieci

### 4.2 Memory Used
- Wszystkie typy pamieci (do czytania)
- ResultsInputPackage
- ComparisonReport
- ErrorAnalysisReport

### 4.3 Memory Updated
- Agent Memory (wszystkie pliki)
- Collective Memory
- Long Term Memory
- Laboratory Memory
- Teacher Memory
- Decision Replay Memory (nowe wpisy)

### 4.4 Next Module
- Trigger: `WAIT_FOR_NEW_DATA` (oczekiwanie do 08:00)

### 4.5 Error Handling
- **BLAD_KONFLIKTU_PAMIECI:** Jesli wystapi konflikt podczas aktualizacji, system wykonuje rollback do poprzedniej wersji
- **BLAD_INTEGRALNOSCI:** Jesli pamiec uznana za uszkodzona, system laduje backup i kontynuuje
- **BLAD_CZASU:** Jesli proces trwa dluzej niz 6 godzin, system przerywa Feedback Loop i kontynuuje z czesciowa aktualizacja

---

## 5. FAZA 08:00 - NOWE DANE WEJSCIOWE

### 5.1 Input

**Zrodla:**
- V2 Collector: dane rynkowe
- V3 Collector: wiedza i wzorce
- V4 Collector: dane o agentach
- External Collector: dane zewnetrzne (kursy, trendy)

**Format wejsciowy:**
- kursy_przygotowane.csv (dla kursow)
- Inne zrodla w formacie JSON/CSV

**Przetwarzanie Kursow:**
- System analizuje kurs koncowy przed meczem
- Zamiana informacji kursowych na prawdopodobienstwo:
  - kurs 1 -> P(home_win)
  - kurs X -> P(draw)
  - kurs 2 -> P(away_win)

### 5.2 Process

```
1. Uruchomienie Collector Manager
2. Agregacja danych z wszystkich kolektorow
3. Walidacja i normalizacja danych
4. Tworzenie UnifiedInputPackage
5. Przekazanie do Runtime Layer
```

### 5.3 Output

**UnifiedInputPackage:**
```json
{
  "timestamp": "2026-08-01T08:00:00Z",
  "cycle": 43,
  "v2_data": {
    "matches": [
      {
        "match_id": "MATCH_20260801_001",
        "teams": ["FC Barcelona", "Real Madrid"],
        "market_data": {
          "odds_home": 2.10,
          "odds_draw": 3.20,
          "odds_away": 3.50
        }
      }
    ],
    "market_trends": {...}
  },
  "v3_data": {
    "patterns": [...],
    "trends": [...],
    "relationships": [...]
  },
  "v4_data": {
    "agents": [...],
    "team_metrics": {...}
  },
  "external_data": {
    "sources": [...],
    "odds_analysis": {
      "conversion_rates": {
        "MATCH_20260801_001": {
          "P_home_win": 0.476,
          "P_draw": 0.312,
          "P_away_win": 0.212
        }
      }
    }
  }
}
```

### 5.4 Memory Used
- Long Term Memory (historyczne dane)
- Collective Memory (zespolowe wzorce)

### 5.5 Memory Updated
- **NEW:** Current Input Memory (tymczasowa pamiec wejsciowa)

### 5.6 Next Module
- Trigger: `RUNTIME_PROCESSING` (Faza 08:00-10:00)

### 5.7 Error Handling
- **BLAD_KOLEKTORA:** Jesli kolektor zawodzi, system uzywa danych z poprzedniego cyklu
- **BLAD_DANYCH:** Jesli dane sa niekompletne, system uzupelnia je domyslnymi wartosciami
- **BLAD_WALIDACJI:** Jesli dane sa nieprawidlowe, system generuje alert i korzysta z backupu

---

## 6. FAZA 08:00-10:00 - PRACA LABORATORIOW

### 6.1 Podfazy

#### 6.1.1 Podfaza A: Analiza Modeli (08:00-08:30)

**Input:** UnifiedInputPackage + UpdatedMemoryState

**Process:**
1. Memory Context Builder tworzy Relevant Context Package dla kazdego Teacher Model
2. Prompt Router decyduje, ktore Teacher Models powinny zostac aktywowane
3. Agent Teacher:
   - Analizuje decyzje pojedynczych agentow
   - Sprawdza confidence i logike decyzyjna
4. Collective Teacher:
   - Analizuje wszystkie agenty jako zespol
   - Wykrywa potencjalne konflikty
5. Laboratory Teacher:
   - Uruchamia eksperymenty w sandbox
   - Testuje nowe strategie i konfiguracje

**Output:** ModelAnalysisReport

#### 6.1.2 Podfaza B: Dialog Nauczyciel-Uczen (08:30-09:00)

**Input:** ModelAnalysisReport

**Process:**
1. Laboratory Teacher prowadzi dialog z agentami:
   - "Dlaczego podiales taka decyzje?"
   - "Jakie czynniki wziales pod uwage?"
   - "Co moi zdaniem powinienes ulepszyc?"
2. Agenci przekazuja swoje reasoning i confidence
3. Teacher Models analizuja odpowiedzi i generuja feedback
4. System uczy sie z dialogu

**Output:** DialogTranscript + LearningPoints

**Memory Updated:**
- Teacher Memory (conversation_history.json)
- Agent Memory (learning_history.json)

#### 6.1.3 Podfaza C: Wybor Strategii (09:00-09:30)

**Input:** DialogTranscript + LearningPoints

**Process:**
1. Collective Teacher porownuje wszystkie strategie
2. Laboratory Teacher wybor najbardziej obiecujace strategie z eksperymentow
3. System laczy rekomendacje z analizy modeli i dialogow
4. Tworzona jest finalna strategia dla kazdego agenta

**Output:** StrategyPackage

#### 6.1.4 Podfaza D: Optymalizacja (09:30-10:00)

**Input:** StrategyPackage

**Process:**
1. Agent Teacher dostraja parametry kazdego agenta
2. Collective Teacher optymalizuje kolektyw
3. Laboratory Teacher aktualizuje laboratoria na podstawie nowej wiedzy
4. System sprawdza spojnosc strategii

**Output:** OptimizedStrategyPackage

### 6.2 Memory Used
- UpdatedMemoryState
- ModelAnalysisReport
- DialogTranscript

### 6.3 Memory Updated
- Agent Memory (strategy.json, behavior.json)
- Collective Memory (team_strategy.json)
- Laboratory Memory (experiment_configs.json)

### 6.4 Next Module
- Trigger: `RUNTIME_EXECUTION` (Faza 10:00)

### 6.5 Error Handling
- **BLAD_DIALOGU:** Jesli dialog sie nie udaje, system uzywa domyslnych strategii
- **BLAD_STRATEGII:** Jesli strategie sa niekonsekwentne, system korzysta z poprzednich ustawien
- **BLAD_OPTYMALIZACJI:** Jesli optymalizacja sie nie udaje, system uzywa strategii nieoptymalizowanych

---

## 7. FAZA 10:00 - GENEROWANIE DECYZJI

### 7.1 Input

**OptimizedStrategyPackage:**
```json
{
  "timestamp": "2026-08-01T10:00:00Z",
  "cycle": 43,
  "strategies": [
    {
      "agent_id": "01",
      "strategy_type": "CONSERVATIVE",
      "parameters": {
        "confidence_threshold": 0.75,
        "risk_factor": 0.3,
        "preferred_outcome": "HOME_WIN"
      },
      "decision_template": "..."
    },
    {
      "agent_id": "02",
      "strategy_type": "AGGRESSIVE",
      "parameters": {
        "confidence_threshold": 0.60,
        "risk_factor": 0.8,
        "preferred_outcome": "HIGH_ODDS"
      }
    }
  ],
  "team_strategy": {
    "consensus_threshold": 0.6,
    "conflict_resolution": "VOTING",
    "collaboration_weight": 0.7
  }
}
```

### 7.2 Process

```
1. Runtime Controller laduje OptimizedStrategyPackage
2. Agent Manager konfiguruje wszystkie agenty wedlug nowych strategii
3. Runtime Controller uruchamia cykl decyzyjny
4. Kazdy agent:
   a. Otrzymuje Relevant Context Package
   b. Analizuje dane wejsciowe
   c. Wykonuje predykcje wedlug zoptymalizowanej strategii
   d. Generuje confidence score
   e. Tworzy reasoning
5. State Manager zbiera wszystkie decyzje
6. System sprawdza spojnosc decyzji
```

### 7.3 Output

**AgentDecisions (x6):**
```json
{
  "agent_id": "01",
  "cycle": 43,
  "timestamp": "2026-08-01T10:00:00Z",
  "decision": {
    "match_id": "MATCH_20260801_001",
    "choice": "HOME_WIN",
    "confidence": 0.88,
    "strategy": "CONSERVATIVE",
    "risk_level": "LOW"
  },
  "reasoning": "Home team has 80% win rate at home in last 10 matches. Current odds confirm home advantage. Collective analysis supports this decision.",
  "memory_used": ["personality", "strategy", "history", "collective_knowledge"],
  "context_package_id": "CTX_20260801_043",
  "teacher_feedback": {
    "last_feedback": "Increase confidence in home advantage scenarios",
    "applied": true
  }
}
```

### 7.4 Memory Used
- Agent Memory (strategy.json, behavior.json, history.json)
- Collective Memory (team_strategy.json, consensus_rules.json)
- Long Term Memory (historical_trends.json)

### 7.5 Memory Updated
- Agent Memory (history.json - new decision)
- Collective Memory (current_decisions.json)
- Decision Replay Memory (new entry)

### 7.6 Next Module
- Trigger: `WAIT_FOR_RESULTS` (oczekiwanie na wyniki meczy)
- Next Cycle: 02:00 (nastepnego dnia)

### 7.7 Error Handling
- **BLAD_DECYZJI:** Jesli agent nie moze podjac decyzji, system uzywa domyslnej strategii
- **BLAD_CONFIDENCE:** Jesli confidence jest zbyt niski (<0.5), systemNie uwzględnia decyzji w konsensusie
- **BLAD_KONSENSUSU:** Jesli brak konsensusu, system uzywa mechanizmu rozstrzygania (VOTING/WEIGHTED_AVERAGE)

---

## 8. SZCZEGOLY PRZEPLYWU MIEDZY WARSTWAMI

### 8.1 Data Flow Matrix

| **From** | **To** | **Data Type** | **Size (avg)** | **Frequency** |
|----------|---------|---------------|----------------|---------------|
| Data Layer | Runtime Layer | UnifiedInputPackage | ~5-10KB | 1x/day (08:00) |
| Runtime Layer | Memory Layer | AgentDecisions | ~2-5KB | Per decision |
| Memory Layer | Analysis Layer | MemoryState | ~100-500KB | On request |
| Analysis Layer | Teacher Models | ContextPackage + RoutingDecision | ~4KB | On trigger |
| Teacher Models | Feedback Layer | FeedbackPackage + LearningUpdates | ~8-16KB | Per cycle |
| Feedback Layer | Memory Layer | MemoryUpdateCommands | ~5-20KB | Per cycle |

### 8.2 Zaleznosci Warstw

```
Warstwa 0 (Data Layer)
   |
   v
Warstwa 1 (Runtime Layer) ---> AgentDecisions
   |
   v
Warstwa 2 (Memory Layer) ---> MemoryState
   |
   v
Warstwa 3 (Analysis Layer) ---> ContextPackages + RoutingDecisions
   |
   v
Warstwa 4 (Teacher Models Layer) ---> Feedback + LearningUpdates
   |
   v
Warstwa 5 (Feedback Layer) ---> MemoryUpdates
   |
   v
Warstwa 2 (Memory Layer) (Updated)
```

**Zaleznosci kluczowe:**
- Analysis Layer **WYMAGA** Memory Layer (nie dziala bez pamieci)
- Teacher Models Layer **WYMAGA** Analysis Layer (nie dziala bez kontekstu)
- Feedback Layer **WYMAGA** Teacher Models Layer (nie dziala bez feedbacku)
- Feedback Layer **AKTUALIZUJE** Memory Layer

### 8.3 Contemporaneous Operations

**Operacje wykluczajace sie:**
- Memory Update (Feedback Layer) **BLUKUJE** Memory Reads (Analysis Layer)
- Teacher Models execution **BLOKUJE** Runtime Execution

**Operacje moliwe do wykonania rownolegle:**
- V2/V3/V4 Collectors (Data Layer)
- Individual Agent Analysis (Agent Teacher)
- Team Analysis (Collective Teacher)
- Experiment Analysis (Laboratory Teacher)

---

## 9. PRZEPLYW WIEDZY TEACHER MODELS

### 9.1 Agent Teacher Knowledge Flow

```
INPUT:
- AgentDecision (z Runtime Layer)
- AgentMemory (z Memory Layer)
- ContextPackage (z Analysis Layer)

PROCESS:
1. Analiza decyzji:
   - Sprawdzenie logicznej spojnosci
   - Ocena confidence
   - Identyfikacja bledow
2. Analiza pamieci:
   - Czy agent korzystal z odpowiedniej pamieci?
   - Czy pamiec byla kompletna?
3. Analiza strategii:
   - Czy strategia byla optymalna?
   - Czy parametry byly dostosowane?

OUTPUT:
- FeedbackPackage (dla agenta)
- LearningUpdate (dla pamieci)
- ConfidenceRecalibration (dla decyzji)

MEMORY USED:
- Agent Memory (history.json, strategy.json, behavior.json)
- Teacher Memory (agent_analysis_history.json)

MEMORY UPDATED:
- Agent Memory (feedback.json, learning_history.json)
- Teacher Memory (new analysis entry)
```

### 9.2 Collective Teacher Knowledge Flow

```
INPUT:
- All AgentDecisions (z Runtime Layer)
- TeamInteractions (z Memory Layer)
- ContextPackage (z Analysis Layer)

PROCESS:
1. Analiza zespołowa:
   - Porownanie decyzji miedzy agentami
   - Wykrywanie konfliktow
   - Identyfikacja synergii
2. Consensus Building:
   - Budowanie konsensusu
   - Rozwiazywanie konfliktow
3. Team Optimization:
   - Optymalizacja alokacji zasobow
   - Poprawa sempreacji

OUTPUT:
- TeamFeedbackPackage (dla zespołóW)
- TeamLearningUpdate (dla pamieci zbiorowej)
- ConsensusRecommendations (dla Runtime Layer)

MEMORY USED:
- Collective Memory (team_decisions.json, conflict_history.json)
- Agent Memory (all agents - strategy.json)
- Teacher Memory (team_analysis_history.json)

MEMORY UPDATED:
- Collective Memory (recommendations.json, consensus_rules.json)
- Teacher Memory (new team analysis entry)
```

### 9.3 Laboratory Teacher Knowledge Flow

```
INPUT:
- ExperimentPackage (z Laboratory System)
- StudentAgentState (z Runtime Layer)
- ContextPackage (z Analysis Layer)

PROCESS:
1. Dialog Nauczyciel-Uczen:
   - Pytania i odpowiedzi
   - Analiza resposta
2. Eksperymenty:
   - Testowanie nowych strategii
   - Porownanie wynikow
3. Transfer Wiedzy:
   - Uczenie sie z eksperymentow
   - Aktualizacja wiedzy systemowej

OUTPUT:
- ExperimentResult (dla laboratorium)
- KnowledgeTransfer (dla systemu)
- StudentFeedback (dla agenta)

MEMORY USED:
- Laboratory Memory (experiments.json, sandbox_state.json)
- Student Agent Memory (all types)
- Teacher Memory (laboratory_conversations.json)

MEMORY UPDATED:
- Laboratory Memory (experiment_results.json, lessons_learned.json)
- Long Term Memory (new knowledge)
- Teacher Memory (new conversation entry)
```

---

## 10. MEMORY UPDATE FLOW

### 10.1 Hierarchia Pamieci

```
┌─────────────────────────────────────────────┐
│              MEMORY UPDATE HIERARCHY              │
├─────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────┐    ┌─────────────────┐  │
│  │  Agent Memory    │    │ Collective      │  │
│  │  (6 agents × 8   │    │ Memory          │  │
│  │   types = 48)    │    │                 │  │
│  └────────┬────────┘    └────────┬────────┘  │
│           │                       │             │
│           └──────────┬────────────┘             │
│                      ▼                          │
│              ┌─────────────────┐                 │
│              │   Long Term      │                 │
│              │   Memory         │                 │
│              └────────┬────────┘                 │
│                       │                           │
│          ┌────────────┼────────────┐            │
│          ▼            ▼            ▼            │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │ Laboratory  │ │ Teacher      │ │ Decision  │ │
│  │ Memory      │ │ Memory       │ │ Replay    │ │
│  └─────────────┘ └─────────────┘ └───────────┘ │
│                                                 │
└─────────────────────────────────────────────┘
```

### 10.2 Proces Aktualizacji

**Kroki:**
1. **Receive:** Otrzymanie FeedbackPackage z Teacher Models
2. **Extract:** Wyodrebnienie LearningPoints i Corrections
3. **Validate:** Walidacja zmian (sprawdzenie integralnosci)
4. **Apply:** Zastosowanie zmian do odpowiednich typow pamieci
5. **Index:** Aktualizacja indeksow wyszukiwania
6. **Backup:** Tworzenie backupu po istotnych zmianach
7. **Verify:** Weryfikacja spojnosci pamieci
8. **Log:** Logowanie wszystkich zmian do Decision Replay Memory

### 10.3 Colejność Aktualizacji

1. **Agent Memory** (pierwsze - indywidualna nauka)
2. **Collective Memory** (drugie - zespolowa nauka)
3. **Long Term Memory** (trzecie - systemowa pamięć długoterminowa)
4. **Laboratory Memory** (czwarte - wyniki eksperymentow)
5. **Teacher Memory** (piate - historia analiz nauczycieli)
6. **Decision Replay Memory** (ostatnie - zapisy decyzji)

### 10.4 Synchronizacja

- **Blokada:** Pamieci sa blokowane podczas aktualizacji
- **Kolejka:** Zmiany sa aplikowane w kolejce FIFO
- **Rollback:** W przypadku bledow, system wykonuje rollback do poprzedniej wersji

---

## 11. ERROR HANDLING I RECOVERY

### 11.1 Klasyfikacja Blędów

| **Kategoria** | **Poziom** | **Opis** | **Recovery Strategy** |
|--------------|------------|----------|----------------------|
| CRITICAL | 1 | Blad systemowy (pamiec, dysk) | Restart systemu, rollback pamieci |
| HIGH | 2 | Blad warstwy (Data, Runtime, Memory) | Restart warstwy, uzycie backupu |
| MEDIUM | 3 | Blad modulu (Collector, Teacher) | Restart modulu, uzycie domyslnych |
| LOW | 4 | Blad analizy (nieprawidlowe dane) | Pomijanie danych, logowanie |

### 11.2 Strategie Recovery

**CRITICAL (Poziom 1):**
- System zatrzymuje wszystkie operacje
- Wykonuje pelny backup pamieci
- Uruchamia procedure awaryjna
- Powiadamia administratora

**HIGH (Poziom 2):**
- Warstwa zostaje zrestartowana
- System laduje backup pamieci
- Kontynuuje dzialanie z ograniczonymi funkcjami

**MEDIUM (Poziom 3):**
- Modul zostaje zrestartowany
- System uzywa domyslnych ustawien
- Kontynuuje dzialanie

**LOW (Poziom 4):**
- Dane sa pomijane
- Blad jest logowany
- System kontynuuje normalna prace

### 11.3 Logowanie i Monitorowanie

**Logi systemowe:**
- Wszystkie operacje sa logowane
- Logi zawieraja:
  - Timestamp
  - Module/Component
  - Operation Type
  - Status (SUCCESS/ERROR/WARNING)
  - Details

**Monitorowanie:**
- System monitoruje:
  - Uzycie pamieci
  - Czas odpowiedzi
  - Accuracy decyzji
  - Liczbe bledow
- Alerty sa generowane dla krytycznych situation

---

**Data utworzenia:** 2026-08-01
**Wersja:** 1.0.0
**Status:** Completed
**Autor:** Glowny Architekt SSI V5

---

**NOTATKA:**
Ten dokument opisuje **glowny przeplyw danych SSI V5 Phase 2**.
Kazdy etap zosta opisan zgodnie ze standardem:
- Cel
- Input
- Process
- Output
- Memory Used
- Memory Updated
- Next Module
- Error Handling

**Powiazane dokumenty:**
- `02_ARCHITECTURE_LAYERS.md` - Warstwy systemu
- `02_VISION_AND_GOALS.md` - Wizja i cele
- `01_CURRENT_STATE.md` - Aktualny stan systemu

**Nastepny sugerowany dokument:**
- `02_INTEGRATION_FLOW.md` - Szczegołowy przeplyw integracji miedzy warstwami
