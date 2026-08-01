# SSI V5 - PHASE 2: ARCHITECTURE LAYERS

**Sprint:** 12+ (Phase 2 Foundation)  
**Data:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** Draft / Awaiting Approval  
**Autor:** Główny Architekt SSI V5  

---

## 📋 SPIS TREŚCI

1. [Warstwy Systemu](#1-warstwy-systemu)
2. [Warstwa 0: Data Layer](#2-warstwa-0-data-layer)
3. [Warstwa 1: Runtime Layer](#3-warstwa-1-runtime-layer)
4. [Warstwa 2: Memory Layer](#4-warstwa-2-memory-layer)
5. [Warstwa 3: Analysis Layer](#5-warstwa-3-analysis-layer)
6. [Warstwa 4: Teacher Models Layer](#6-warstwa-4-teacher-models-layer)
7. [Warstwa 5: Feedback Layer](#7-warstwa-5-feedback-layer)
8. [Podsumowanie Warstw](#8-podsumowanie-warstw)

---

## 1. WARSTWY SYSTEMU

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WARSTWY SSI V5 FAZA 2                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  WARSTWA 0: DATA LAYER (Sprint 11.5 - Frozen)                    │   │
│  │  ┌─────────────┐  ┌─────────────┐                                  │   │
│  │  │ Collectors  │  │ Input Data  │                                  │   │
│  │  └─────────────┘  └─────────────┘                                  │   │
│  │  Output: UnifiedInputPackage                                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                             │                                         │
│                             ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  WARSTWA 1: RUNTIME LAYER (Sprint 11.5 - Frozen)                 │   │
│  │  ┌─────────────┐  ┌─────────────┐                                  │   │
│  │  │ Runtime     │  │ Agents      │                                  │   │
│  │  │ Controller  │──▶│ Execution   │                                  │   │
│  │  └─────────────┘  └─────────────┘                                  │   │
│  │  Output: Agent Decisions                                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                             │                                         │
│                             ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  WARSTWA 2: MEMORY LAYER (Sprint 11.5 + Sprint 12)               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │ Agent       │  │ Collective  │  │ Long Term   │              │   │
│  │  │ Memory      │  │ Memory      │  │ Memory      │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  │  Output: Memory State, Historical Data                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                             │                                         │
│                             ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  WARSTWA 3: ANALYSIS LAYER (NOWY - Sprint 12)                  │   │
│  │  ┌─────────────────────┐  ┌─────────────────────┐              │   │
│  │  │ Memory Context       │  │ Prompt Routing      │              │   │
│  │  │ Builder               │  │ System              │              │   │
│  │  └─────────────────────┘  └─────────────────────┘              │   │
│  │  Output: Context Packages, Routing Decisions                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                             │                                         │
│                             ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  WARSTWA 4: TEACHER MODELS LAYER (NOWY - Sprint 13)             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │ Agent       │  │ Collective  │  │ Laboratory  │              │   │
│  │  │ Teacher     │  │ Teacher     │  │ Teacher     │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  │  Output: Feedback, Recommendations, Learning Updates             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                             │                                         │
│                             ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  WARSTWA 5: FEEDBACK LAYER (NOWY - Sprint 12+)                 │   │
│  │  ┌─────────────┐  ┌─────────────┐                                  │   │
│  │  │ Memory      │  │ Agent       │                                  │   │
│  │  │ Update      │  │ Adaptation │                                  │   │
│  │  └─────────────┘  └─────────────┘                                  │   │
│  │  Output: Updated Memory State                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. WARSTWA 0: DATA LAYER

**Status:** ✅ **FROZEN (Sprint 11.5)** - Brak zmian

### 2.1 Składniki

| **Moduł** | **Plik** | **Odpowiedzialność** | **Output** |
|-----------|----------|--------------------|------------|
| V2 Collector | `v2_collector.py` | Dane rynkowe | V2 Data Package |
| V3 Collector | `v3_collector.py` | Wiedza, wzorce | V3 Data Package |
| V4 Collector | `v4_collector.py` | Dane o agentach | V4 Data Package |
| External Collector | `external_collector.py` | Dane zewnętrzne | External Data Package |
| Collector Manager | `collector_manager.py` | Agregacja, walidacja | UnifiedInputPackage |

### 2.2 Output Warstwy

**UnifiedInputPackage:**
```json
{
  "timestamp": "2026-08-01T12:00:00Z",
  "cycle": 42,
  "v2_data": {"matches": [...], "market_data": {...}},
  "v3_data": {"patterns": [...], "trends": [...], "relationships": [...]},
  "v4_data": {"agents": [...], "team_metrics": {...}},
  "external_data": {"sources": [...], "custom_data": {...}}
}
```

---

## 3. WARSTWA 1: RUNTIME LAYER

**Status:** ✅ **FROZEN (Sprint 11.5)** - Brak zmian

### 3.1 Składniki

| **Moduł** | **Plik** | **Odpowiedzialność** | **Output** |
|-----------|----------|--------------------|------------|
| Runtime Controller | `runtime_controller.py` | Sterowanie cyklem | Agent Results |
| State Manager | `state_manager.py` | Zarządzanie stanem | Runtime State |
| Scheduler | `scheduler.py` | Planowanie | Scheduled Tasks |
| Runtime Config | `runtime_config.py` | Konfiguracja | RuntimeConfig |
| Agent Manager | `agent_manager.py` | Zarządzanie agentami | Agent Runtime[] |

### 3.2 Output Warstwy

**Agent Decisions (x6):**
```json
{
  "agent_id": "01",
  "cycle": 42,
  "decision": {"choice": "HOME_WIN", "confidence": 0.82, "strategy": "..."},
  "reasoning": "Last 5 matches had home wins at 80%",
  "memory_used": ["personality", "strategy", "history"]
}
```

---

## 4. WARSTWA 2: MEMORY LAYER

**Status:** ✅ **Sprint 11.5** + 🟡 **Sprint 12 (rozszerzenie)**

### 4.1 Istniejące Składniki (Sprint 11.5)

**Agent Memory:** 48 plików JSON (6 agentów × 8 typów)
```
SSI/memory/agents/agent_XX/
├── personality.json     # Cechy osobowości
├── behavior.json        # Zachowania
├── strategy.json        # Strategie decyzyjne
├── history.json         # Historia decyzji
├── indexes.json         # Indeksy wyszukiwania
├── relationship.json    # Relacje z innymi agentami
├── prompt_memory.json   # Konwersacje
└── stats.json           # Statystyka
```

### 4.2 Nowe Składniki (Sprint 12+)

| **Typ Pamięci** | **Lokalizacja** | **Sprint** | **Cel** |
|-----------------|----------------|------------|---------|
| **Long Term Memory** | `memory/long_term/` | 12 | Historia systemu między sesjami |
| **Collective Memory** | `memory/collective/` | 12 | Wspólna wiedza zespołu |
| **Laboratory Memory** | `memory/laboratory/` | 13 | Wyniki eksperymentów |
| **Teachers Memory** | `memory/teachers/` | 12 | Historia analiz nauczycieli |

### 4.3 Output Warstwy

**Memory State:**
- Aktualny stan wszystkich typów pamięci
- Historia zmian
- Indeksy dla szybkiego wyszukiwania

---

## 5. WARSTWA 3: ANALYSIS LAYER

**Status:** 🟡 **NOWY (Sprint 12)**

### 5.1 Składniki

| **Moduł** | **Plik** | **Odpowiedzialność** | **Sprint** |
|-----------|----------|--------------------|------------|
| Memory Context Builder | `memory_context_builder.py` | Tworzy relewantne konteksty | 12 |
| Prompt Routing System | `prompt_router.py` | Routuje zadania do Teacher Models | 12 |

### 5.2 Memory Context Builder

**Cel:** Nigdy nie wysyłać CAŁEJ pamięci - zawsze tworzyć **Relevant Context Package** (max 4KB)

**Input:**
- Pełny stan pamięci (wszystkie typy)
- Żądanie kontekstu (Agent ID, Purpose)

**Process:**
1. Purpose Detection (określenie celu)
2. Memory Inventory (spis dostępnej pamięci)
3. Relevance Scoring (ocena istotności)
4. Filtering (filtrowanie danych)
5. Packaging (pakowanie w konteksty)
6. Caching (cache'owanie)

**Output:** `RelevantContextPackage` (max 4096 bytes)

### 5.3 Prompt Routing System

**Cel:** Decydować, który Teacher Model powinien zostać aktywowany

**Input:** Trigger (Agent Decision, Team Conflict, Experiment Result)

**Process:**
1. Analyze trigger type and severity
2. Determine appropriate Teacher Model
3. Set priority based on urgency
4. Select context package
5. Create routing decision

**Routing Decisions:**
| **Trigger** | **Teacher Model** | **Priority** | **Rationale** |
|-------------|-------------------|--------------|---------------|
| Agent decision with error | Agent Teacher | 1 (High) | Individual analysis needed |
| Team conflict | Collective Teacher | 1 (High) | Requires consensus building |
| Experiment result | Laboratory Teacher | 2 (Medium) | Learning from experiments |
| Low confidence decision | Agent Teacher | 2 (Medium) | Confidence calibration |
| Strategy comparison | Collective Teacher | 2 (Medium) | Team optimization |
| New pattern detected | Collective Teacher | 3 (Low) | Knowledge sharing |

**Output:** `RoutingDecision`

### 5.4 Output Warstwy

**Context Package + Routing Decision:**
```json
{
  "context_package": {
    "context_id": "CTX_20260801_001",
    "size": 4096,
    "relevance_score": 0.95,
    "packages": [...]
  },
  "routing_decision": {
    "teacher_model": "AgentTeacher",
    "priority": 1,
    "timeout": 5000
  }
}
```

---

## 6. WARSTWA 4: TEACHER MODELS LAYER

**Status:** 🟡 **NOWY (Sprint 13)**

### 6.1 Trzy Niezależne Modele Nauczycieli

| **Model** | **Plik** | **Odpowiedzialność** | **Focus** |
|----------|----------|--------------------|----------|
| Agent Teacher | `agent_teacher.py` | Analiza indywidualnych agentów | Single Agent |
| Collective Teacher | `collective_teacher.py` | Analiza zespołu agentów | Team |
| Laboratory Teacher | `laboratory_teacher.py` | Środowisko nauki i eksperymenty | Experiments |

### 6.2 Agent Teacher Model

**Odpowiedzialność:**
- Analiza decyzji pojedynczego agenta
- Sprawdzanie logiki i spójności decyzyjnej
- Identyfikacja potencjalnych błędów
- Korekta strategii i parametrów
- Kalibracja confidence
- Monitorowanie ewolucji agenta

**Input:** `AgentDecisionPackage`
**Output:** `FeedbackPackage` + `LearningUpdate`

### 6.3 Collective Teacher Model

**Odpowiedzialność:**
- Analiza współpracy między agentami
- Wykrywanie i rozwiązywanie konfliktów
- Budowanie konsensusu
- Identyfikacja synergii
- Optymalizacja alokacji zasobów
- Monitorowanie dynamiki zespołu

**Input:** `TeamDecisionPackage` + Agent Interactions
**Output:** `TeamFeedbackPackage` + `TeamLearningUpdate`

### 6.4 Laboratory Teacher Model

**Odpowiedzialność:**
- Projektowanie eksperymentów
- Zarządzanie środowiskiem Sandbox
- Dialog z agentami (Student ↔ Teacher)
- Ocena wyników eksperymentów
- Porównanie strategii
- Transfer wiedzy do głównego systemu

**⚠️ KLUCZOWE:** Laboratorium to **ŚRODOWISKO NAUKI**, nie tylko testowanie

**Input:** `ExperimentPackage` + Student Agent State
**Output:** `ExperimentResult` + `KnowledgeTransfer`

### 6.5 Output Warstwy

**Feedback and Learning Updates:**
- Individual feedback for each agent
- Team-level recommendations
- Experiment results and lessons learned
- Memory updates for all layers

---

## 7. WARSTWA 5: FEEDBACK LAYER

**Status:** 🟡 **NOWY (Sprint 12+)**

### 7.1 Składniki

| **Proces** | **Opis** | **Output** |
|------------|----------|------------|
| Memory Update | Aktualizacja wszystkich typów pamięci | Updated Memory State |
| Agent Adaptation | Dostosowywanie parametrów agentów | Updated Agent Config |
| System Learning | Nauka systemowa z doświadczeń | System Knowledge Update |

### 7.2 Memory Update Process

**Kroki:**
1. Receive feedback from Teacher Models
2. Extract learning points and corrections
3. Update appropriate memory types:
   - Agent Memory (for individual learning)
   - Collective Memory (for team learning)
   - Long Term Memory (for system history)
   - Laboratory Memory (for experiment results)
   - Teachers Memory (for conversation history)
4. Log all changes for replay and analysis
5. Trigger backup if significant changes

### 7.3 Output Warstwy

**Updated System State:**
- All memory types synchronized
- Agent configurations updated
- System knowledge enhanced
- Ready for next cycle

---

## 8. PODSUMOWANIE WARSTW

### 8.1 Zestawienie Warstw

| **Warstwa** | **Numer** | **Status** | **Sprint** | **Cel** |
|------------|-----------|------------|------------|---------|
| Data Layer | 0 | ✅ Frozen | 11.5 | Zbieranie danych |
| Runtime Layer | 1 | ✅ Frozen | 11.5 | Przetwarzanie |
| Memory Layer | 2 | ✅+🟡 | 11.5+12 | Przechowywanie wiedzy |
| Analysis Layer | 3 | 🟡 New | 12 | Inteligentne przetwarzanie |
| Teacher Models Layer | 4 | 🟡 New | 13 | Nauka i wsparcie |
| Feedback Layer | 5 | 🟡 New | 12+ | Aktualizacja systemu |

### 8.2 Zależności Między Warstwami

```
Warstwa 0 (Data) → Warstwa 1 (Runtime) → Warstwa 2 (Memory)
                    ↓
Warstwa 2 (Memory) → Warstwa 3 (Analysis) → Warstwa 4 (Teachers)
                    ↓
Warstwa 4 (Teachers) → Warstwa 5 (Feedback) → Warstwa 2 (Memory)
```

**Zależności:**
- Analysis Layer **zależy** od Memory Layer
- Teacher Models Layer **zależy** od Analysis Layer
- Feedback Layer **zależy** od Teacher Models Layer
- Feedback Layer **aktualizuje** Memory Layer

### 8.3 Wpływ Na System

| **Warstwa** | **Wpływ na Dokładność** | **Wpływ na Wydajność** | **Wpływ na Pamięć** |
|------------|------------------------|------------------------|---------------------|
| Data Layer | neutralny | neutralny | neutralny |
| Runtime Layer | neutralny | neutralny | neutralny |
| Memory Layer | + (history) | - (overhead) | + (storage) |
| Analysis Layer | + (context) | - (processing) | + (caching) |
| Teacher Models Layer | ++ (learning) | - (computation) | + (conversations) |
| Feedback Layer | ++ (adaptation) | - (I/O) | + (updates) |

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** Draft (Oczekuje zatwierdzenia)  
**Autor:** Główny Architekt SSI V5  

---

**📌 NOTATKA:**
Ten dokument opisuje **warstwy architektoniczne Fazy 2**.
Szczegóły implementacyjne znajdują się w dokumentach modułów.

**Powiązane dokumenty:**
- `01_VISION_AND_GOALS.md` - Wizja systemu
- `03_DATA_FLOWS.md` - Przepływy danych
- `04_DESIGN_PRINCIPLES.md` - Zasady projektowe
