# SSI V5 ARCHITEKTURA - CZESC 1

**Data utworzenia:** 2026-07-31  
**Wersja:** 1.0.0  
**Status:** PROJEKT  

---

## SPIS TRESCI

1. [WSTEP](#wstep)
2. [Zalozenia Architektury](#zalozenia-architektury)
3. [Przeglad Systemu](#przeglad-systemu)
4. [Architektura Warstwowa](#architektura-warstwowa)
5. [Modul Runtime](#modul-runtime)
6. [Modul Agents](#modul-agents)
7. [Modul Memory](#modul-memory)
8. [Modul Input Layer](#modul-input-layer)
9. [Integracja Miedzy-Modulowa](#integracja-miedzy-modulowa)

---

## WSTEP

SSI V5 jest systemem agentowym budowanym modułowo, zgodnie z zasadami:
- **Modularnosci** - Kazdy modul ma okreslona odpowiedzialnosc
- **Elastycznosci** - Latrowe dodawanie nowych komponentow
- **Skalowalnosci** - Mozliwosc pracy z rosnaca iloscia agentow
- **Obserwowalnosci** - Pelne monitorowanie stanu i dzialan

---

## ZALOZENIA ARCHITEKTURY

### 1. Separation of Concerns

Kazdy modul odpowiedzialny jest za jedna konkretna funkcjonalnosc:
- **Runtime:** Kontrola wykonania
- **Agents:** Podejmowanie decyzji
- **Memory:** Przechowywanie stanu
- **Input:** Zbiorki danych

### 2. Event-Driven Design

System reaguje na zdarzenia:
- Nowe dane od collectorow
- Zmiany stanu agentow
- Zmiany pamieci
- Komendy zewnetrzne

### 3. Data Flow

Dane plyna w jedna strone:
```
INPUT -> COLLECTORS -> WORLD MEMORY -> AGENTS -> OUTPUT -> MEMORY UPDATE
```

### 4. Persistence

Wszystkie istotne dane sa zapisywane:
- Stan systemu
- Pamieci agentow
- Historia decyzji
- Konfiguracja

---

## PRZEGLAD SYSTEMU

### DIAGRAM ARCHITEKTURY

```
┌─────────────────────────────────────────────────────────────┐
│                          SSI V5 SYSTEM                            │
├─────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│  │   INPUT     │────▶│   RUNTIME   │────▶│    AGENTS   │   │
│  │   LAYER    │     │  CONTROLLER │     │   MODULE    │   │
│  └─────────────┘     └─────────────┘     └─────────────┘   │
│           │                   │                   │            │
│           ▼                   ▼                   ▼            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    WORLD MEMORY                         │   │
│  │              (Shared State, Knowledge)                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│  │   V2        │     │   V3        │     │   V4        │   │
│  │  Collector   │     │  Collector   │     │  Collector   │   │
│  └─────────────┘     └─────────────┘     └─────────────┘   │
│           │                   │                   │            │
│           └───────────────────┼───────────────────┘            │
│                               ▼                                │
│                ┌─────────────────────────────┐                │
│                │    UnifiedInputPackage       │                │
│                │    (Aggregated Data)         │                │
│                └─────────────────────────────┘                │
│                                       │                          │
│                                       ▼                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    AGENT MEMORY                         │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │Personality│ │Behavior │ │Strategy │ │History  │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                       │                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 COLLECTIVE MEMORY                       │   │
│  │  Knowledge | Relations | Conflicts | Alliances      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  LONG TERM MEMORY                       │   │
│  │  Patterns | Experience | Validated Knowledge           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### SKLOADNIKI SYSTEMU

| Składnik | Opis | Lokalizacja |
|----------|------|-------------|
| Input Layer | Zbiorki danych V2, V3, V4, External | `SSI/v5/input_layer/` |
| Runtime | Kontroler glowny, zarzadzanie cyklem | `SSI/v5/runtime/` |
| Agents | Pojedynczy agent, podejmowanie decyzji | `SSI/v5/agents/` |
| Memory | Pamieci agentow, kolektywna, dlugoterminowa | `SSI/memory/` |
| State | Stan systemu, monitorowanie | `SSI/v5/runtime/state_manager.py` |

---

## ARCHITEKTURA WARSTWOWA

### WARSTWA 1: INPUT LAYER

**Odpowiedzialnosc:** Zbieranie i agregacja danych wejsciowych

```
Input Layer
├── V2 Collector
│   └── World data (matches, results, statistics)
├── V3 Collector
│   └── Knowledge data (patterns, trends, historical)
├── V4 Collector
│   └── Agents data (decisions, behaviors, strategies)
├── External Collector
│   └── Additional input (API, manual, config)
└── Collector Manager
    └── UnifiedInputPackage creation
```

**Przeplyw danych:**
1. Kazdy collector pobiera dane ze swoich zródeł
2. Collector Manager agreguje dane w UnifiedInputPackage
3. UnifiedInputPackage przekazywany jest do Runtime Controller

### WARSTWA 2: RUNTIME LAYER

**Odpowiedzialnosc:** Kontrola wykonania systemu

```
Runtime Layer
├── Runtime Controller
│   ├── Cycle management
│   ├── Agent scheduling
│   ├── State management
│   └── Error handling
├── Runtime Config
│   └── Configuration management
└── State Manager
    ├── Runtime state
    ├── Agent states
    ├── Memory state
    └── Collector states
```

**Przeplyw danych:**
1. Runtime Controller inicjalizuje system
2. Uruchamia collectory
3. Odbiera UnifiedInputPackage
4. Uruchamia agenty w ustalonej kolejnosci
5. Monitoruje stan systemu

### WARSTWA 3: AGENTS LAYER

**Odpowiedzialnosc:** Podejmowanie decyzji przez poszczególne agenty

```
Agents Layer
├── Agent Manager
│   └── Agent creation and management
└── Agent Runtime (x6)
    ├── Agent_01
    ├── Agent_02
    ├── Agent_03
    ├── Agent_04
    ├── Agent_05
    └── Agent_06
        └── Decision Cycle
            ├── Load Memory
            ├── Get Data
            ├── Compare (Old + New)
            ├── Analyze
            ├── Decide
            ├── Save Experience
            └── Update History
```

**Przeplyw danych:**
1. Agent odbywa swój cykl decyzyjny
2. Pobiera dane z World Memory
3. Analizuje dane i podejmuje decyzje
4. Zapisuje doświadczenie i aktualizuje pamięć

### WARSTWA 4: MEMORY LAYER

**Odpowiedzialnosc:** Przechowywanie i zarzadzanie pamięcia

```
Memory Layer
├── Agent Memory (per agent)
│   ├── Personality Memory
│   ├── Behavior Memory
│   ├── Strategy Memory
│   ├── History Memory
│   ├── Relationship Memory
│   └── Prompt Memory
├── World Memory
│   └── UnifiedInputPackage (current state)
├── Collective Memory
│   ├── Knowledge
│   ├── Relations
│   ├── Conflicts
│   ├── Alliances
│   └── Consensus
└── Long Term Memory
    ├── Patterns
    ├── Experience
    └── Validated Knowledge
```

---

## MODUL RUNTIME

### SKLOADNIKI

| Składnik | Opis | Plik |
|----------|------|------|
| RuntimeController | Glowny kontroler, zarzadza cyklem życia | `runtime_controller.py` |
| RuntimeConfig | Konfiguracja systemu | `runtime_config.py` |
| StateManager | Zarzialdzanie stanem systemu | `state_manager.py` |
| Scheduler | Planowanie zadan | `scheduler.py` |

### ODPOWIEDZIALNOSC

**RuntimeController:**
- Inicjalizacja systemu
- Uruchamianie i zatrzymywanie cykli
- Zarzadzanie agentami
- Zarzadzanie collectorami
- Zapis i odczyt stanu

**RuntimeConfig:**
- Przechowywanie konfiguracji
- Zarzadzanie ustawieniami agentow
- Konfiguracja collectorow

**StateManager:**
- Przechowywanie stanu runtime
- Stan agentow
- Stan collectorow
- Stan pamieci
- Zapis/odczyt stanu do pliku

### PRZEPLYW DANYCH

```
RuntimeController
    │
    ├── Input: Configuration (RuntimeConfig)
    ├── Input: Commands (start, stop, status)
    │
    ├── Output: State information (StateManager)
    ├── Output: Agent results (to Memory)
    │
    ├── Controls: Collectors (V2, V3, V4, External)
    └── Controls: Agents (Agent_01 to Agent_06)
```

### KONFIGURACJA

```json
{
  "mode": "development",
  "test_mode": false,
  "test_cycles": 10,
  "auto_save": true,
  "cycle_duration_hours": 5,
  "agent_count": 6,
  "enable_v2_collector": true,
  "enable_v3_collector": true,
  "enable_v4_collector": true,
  "enable_external_collector": true,
  "memory_persistence": true
}
```

---

## MODUL AGENTS

### SKLOADNIKI

| Składnik | Opis | Plik |
|----------|------|------|
| AgentRuntime | Pojedynczy agent, cykl życia | `agent_runtime.py` |
| AgentMemoryStore | Przechowywanie pamięci agenta | `agent_memory_store.py` |
| AgentStateManager | Zarzadzanie stanem agenta | `agent_state.py` |
| AgentManager | Zarzadzanie wszystkimi agentami | `agent_manager.py` |
| AgentsConfig | Konfiguracja agentow | `agents_config.py` |

### ODPOWIEDZIALNOSC

**AgentRuntime:**
- Wykonanie cyklu agenta
- Zarzadzanie pamięcia
- Podejmowanie decyzji
- Rejestrowanie doświadczeń

**AgentMemoryStore:**
- Przechowywanie wpisow pamieci
- Indexowanie i wyszukiwanie
- Zapis/odczyt z dysku
- Statystyki pamieci

**AgentStateManager:**
- Zarzadzanie stanem pojedynczego agenta
- Historia decyzji
- Historia zachowan
- Historia strategii

### CYKL AGENTA

```
Agent Cycle (Sprint 11.5 v2.0):

STEP 1: Load Memory
├── Personality (risk, analysis, creativity, trust)
├── Behavior (actions, effectiveness)
├── Strategy (available, history)
└── History (past decisions)

STEP 2: Get Data
├── V2 Data (world state)
├── V3 Data (knowledge)
├── V4 Data (other agents)
└── External Data

STEP 3: Compare Old Knowledge + New Data
├── Identify changes
├── Detect patterns
└── Evaluate data quality

STEP 4: Analyze
├── Quality assessment
├── Trust evaluation
├── Anomaly detection
└── Pattern recognition

STEP 5: Decide
├── Strategy selection
├── Choice generation
└── Confidence calculation

STEP 6: Save Experience
├── Save to History Memory
├── Update Behavior Memory
└── Update Strategy Memory

STEP 7: Update History
├── Add History Entry
└── Update Agent State
```

### PAMIEC AGENTA

| Typ | Opis | Przechowywane dane |
|-----|------|-------------------|
| Personality | Cechy osobowosci | Risk, analysis, creativity, trust scores |
| Behavior | Zachowania agenta | Actions, effectiveness, success rates |
| Strategy | Strategie decyzyjne | Available strategies, usage history, success rates |
| History | Historia agents | Decisions, outcomes, evaluations, confidence |
| Relationship | Relacje z innymi | Trust scores, interactions, collaboration |
| Prompt | Prompty LLM | Prompt text, usage history, response quality |

---

## MODUL MEMORY

### STRUKTURA KATALOGOW

```
SSI/memory/
├── agents/
│   ├── agent_01/
│   │   ├── personality.json
│   │   ├── behavior.json
│   │   ├── strategy.json
│   │   ├── history.json
│   │   ├── relationship.json
│   │   ├── prompt_memory.json
│   │   ├── indexes.json
│   │   └── stats.json
│   ├── agent_02/
│   │   └── ...
│   └── agent_06/
│       └── ...
└── runtime/
    └── runtime_state.json
```

### TYPY PAMIECI

| Typ | Zakres | Przeznaczenie |
|-----|--------|---------------|
| Agent Memory | Per agent | Indywidualna pamiec agenta |
| World Memory | Global | Aktualny stan świata |
| Collective Memory | System-wide | Wiedza wspólna wszystkich agentow |
| Long Term Memory | System-wide | Historyczna wiedza i doświadczenie |

---

## MODUL INPUT LAYER

### SKLOADNIKI

| Składnik | Opis | Plik |
|----------|------|------|
| V2DataCollector | Zbieranie danych V2 | `v2_collector.py` |
| V3KnowledgeCollector | Zbieranie wiedzy V3 | `v3_collector.py` |
| V4AgentsCollector | Zbieranie danych agentow V4 | `v4_collector.py` |
| ExternalKnowledgeCollector | Dane zewnetrzne | `external.py` |
| CollectorManager | Zarzadzanie collectorami | `collector_manager.py` |

### ODPOWIEDZIALNOSC

**V2DataCollector:**
- Pobieranie danych o meczach
- Statystyki i wyniki
- Aktualny stan świata

**V3KnowledgeCollector:**
- Wiedza historyczna
- Wzorce i trendy
- Walidowana wiedza

**V4AgentsCollector:**
- Decyzje innych agentow
- Zachowania agentow
- Strategie agentow

**ExternalKnowledgeCollector:**
- Dane z API
- Ręczne wejście
- Konfiguracja zewnetrzna

### UNIFIED INPUT PACKAGE

**Struktura:**
```json
{
  "timestamp": "2026-07-31T23:59:59",
  "version": "1.0.0",
  "data": {
    "v2": { ... },
    "v3": { ... },
    "v4": { ... },
    "external": { ... }
  }
}
```

**Lokalizacja:** `SSI/memory/unified_input_package.json`

---

## INTEGRACJA MIEDZY-MODULOWA

### KOMUNIKACJA

```
1. Input Layer → Runtime Controller
   - UnifiedInputPackage
   - Data quality information

2. Runtime Controller → Agents
   - World context
   - Collector data
   - Configuration

3. Agents → Memory
   - Memory entries (Personality, Behavior, Strategy, History)
   - Statistics updates
   - Experience records

4. Agents → Runtime Controller
   - Decision results
   - Analysis results
   - Status updates

5. Runtime Controller → State Manager
   - Runtime state updates
   - Agent state updates
   - Error reporting
```

### ZALEZNOSCI

```
Runtime Controller
├── depends on: RuntimeConfig
├── depends on: StateManager
├── depends on: AgentManager
├── depends on: Collectors (V2, V3, V4, External)
└── depends on: Memory system

AgentManager
├── depends on: AgentConfig
└── creates: AgentRuntime instances

AgentRuntime
├── depends on: AgentConfig
├── depends on: AgentMemoryStore
└── depends on: AgentStateManager

CollectorManager
├── depends on: V2DataCollector
├── depends on: V3KnowledgeCollector
├── depends on: V4AgentsCollector
└── depends on: ExternalKnowledgeCollector
```

---

**Nota:** Ta dokumentacja jest czescia Projektu SSI V5. Kolejne czesci zawieraRESSI_V5_ARCHITECTURE_PART2.md, SSI_V5_MEMORY_DESIGN.md, SSI_V5_DATA_FLOW.md, SSI_V5_AGENT_BEHAVIOR.md.

**Ostatnia aktualizacja:** 2026-07-31
