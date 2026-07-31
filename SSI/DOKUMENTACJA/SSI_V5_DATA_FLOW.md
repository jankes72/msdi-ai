# SSI V5 DATA FLOW

**Data utworzenia:** 2026-07-31  
**Wersja:** 1.0.0  
**Status:** PROJEKT  

---

## SPIS TRESCI

1. [PRZEGLAD PRZEPLYWU DANYCH](#przeglad-przeplywu-danych)
2. [MAIN DATA FLOW DIAGRAM](#main-data-flow-diagram)
3. [COLLECTOR DATA FLOW](#collector-data-flow)
4. [AGENT CYCLE DATA FLOW](#agent-cycle-data-flow)
5. [DATA TRANSFORMATIONS](#data-transformations)
6. [DATA FORMATS](#data-formats)
7. [DATA STORAGE LOCATIONS](#data-storage-locations)

---

## PRZEGLAD PRZEPLYWU DANYCH

### KLUCZOWE WEJSCIA I WYJSCIA

| Komponent | Wejścia | Wyjścia |
|-----------|---------|----------|
| V2 Collector | V2 Data Source | V2 Data |
| V3 Collector | V3 Data Source | V3 Data |
| V4 Collector | V4 Data Source | V4 Data |
| External Collector | External Source | External Data |
| Collector Manager | V2, V3, V4, External Data | UnifiedInputPackage |
| Runtime Controller | UnifiedInputPackage, Config | Context, Commands |
| Agent | Context, World Memory | Decisions, Analysis |
| State Manager | Runtime State Updates | State Information |
| Agent Memory | Agent Data | Persistent Storage |

---

## MAIN DATA FLOW DIAGRAM

```
EXTERNAL SOURCES
  │
  ├─▶ V2 Data Source ──▶ V2 Collector ──┐
  │                           │
  ├─▶ V3 Data Source ──▶ V3 Collector ──┼──▶ Collector Manager ──▶ UnifiedInputPackage
  │                           │      │
  ├─▶ V4 Data Source ──▶ V4 Collector ──┼      │
  │                           │      │
  └─▶ External Source ──▶ External ──┘      │
                              Collector     │
                                                  ▼
                           WORLD MEMORY (Shared State, Current Data)
                                  │
                                  ▼
                      RUNTIME CONTROLLER
  ┌─────────────────────────────────────────────────────────┐
  │                    STATE MANAGER                          │
  │  Runtime State │ Agent States │ Memory State │ Collector State │
  └───────────────────────┬──────────────────────────────────┘
                          │
                          ▼
  ┌─────────────────────────────────────────────────────────┐
  │                         AGENTS LAYER                       │
  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
  │  │   Agent 01  │ │   Agent 02  │ │   Agent 06  │         │
  │  │  Decision   │ │  Decision   │ │  Decision   │         │
  │  │  Cycle      │ │  Cycle      │ │  Cycle      │         │
  │  └─────────────┘ └─────────────┘ └─────────────┘         │
  └───────────────────────────────────┬──────────────────────┘
                                  │
  ┌───────────────────────────────────┼──────────────────────┐
  │                               ▼                        │
  │  ┌─────────────────────────────────────────────────────┐  │
  │  │                    AGENT MEMORIES                     │  │
  │  │  (Individual, Private, Persistent)                    │  │
  │  └─────────────────────────────────────────────────────┘  │
  └───────────────────────────────────────────────────────────┘
                                  │
                          ┌────────▼────────┐
                          │ COLLECTIVE        │
                          │ CONTROL LAYER     │
                          │ (Monitoring,      │
                          │  Analysis,        │
                          │  Reporting)       │
                          └────────┬────────┘
                                   │
  ┌─────────────────────────────────┼────────────────────────┐
  │                             ▼                        │
  │  ┌─────────────────────────────────────────────────┐  │
  │  │                 COLLECTIVE MEMORY                │  │
  │  │        (Shared, Collaborative, Persistent)         │  │
  │  └─────────────────────────────────────────────────┘  │
  │                                                           │
  └───────────────────────────────────────────────────────┘
                          │
                          ▼
  ┌─────────────────────────────────────────────────────────┐
  │                   LONG TERM MEMORY                        │
  │                 (Historical, Validated, Persistent)       │
  └─────────────────────────────────────────────────────────┘
```

---

## COLLECTOR DATA FLOW

### COLLECTOR DETAILS

```
V2 Collector Data Flow:
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ V2 Source   │──▶│ Fetch Data  │──▶│ Process     │
│ (External)  │   │ (API/File)  │   │ (Transform) │
└─────────────┘   └─────────────┘   └──────┬──────┘
                                              │
V3 Collector Data Flow:                          │
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ V3 Source   │──▶│ Fetch Data  │──▶│ Process     │──┘
│ (Knowledge) │   │ (Database)  │   │ (Validate)  │
└─────────────┘   └─────────────┘   └─────────────┘
                                              │
V4 Collector Data Flow:                          │
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ V4 Source   │──▶│ Fetch Data  │──▶│ Process     │──┘
│ (Agents)    │   │ (Internal)  │   │ (Format)    │
└─────────────┘   └─────────────┘   └─────────────┘
                                              │
External Collector Data Flow:                    │
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ External    │──▶│ Fetch Data  │──▶│ Process     │──┘
│ (API/User)  │   │ (HTTP/File) │   │ (Normalize) │
└─────────────┘   └─────────────┘   └─────────────┘
                                              │
                                              ▼
                                     ┌─────────────┐
                                     │ Aggregation │
                                     │ (Collector  │
                                     │  Manager)   │
                                     └──────┬──────┘
                                            │
                                            ▼
                                     ┌─────────────┐
                                     │ Unified     │
                                     │ Input       │
                                     │ Package     │
                                     └─────────────┘
```

### AGGREGATION PROCESS

1. **Collector Execution:**
   - Runtime Controller calls each collector
   - Collectors fetch data from their sources
   - Each collector returns its data

2. **Quality Assessment:**
   - Collector Manager assesses data quality
   - Trust scores are calculated for each source
   - Completeness is checked

3. **Package Creation:**
   - All data aggregated into UnifiedInputPackage
   - Metadata added (timestamps, quality, trust)
   - Version information included

4. **World Memory Update:**
   - UnifiedInputPackage stored in World Memory
   - Available to all agents

---

## AGENT CYCLE DATA FLOW

### SINGLE AGENT CYCLE

```
Agent Cycle (Agent_0X):
┌─────────────┐     ┌─────────────┐
│ Cycle Start │────▶│ STEP 1: Load│
│             │     │  Memory     │
└─────────────┘     └──────┬──────┘
                              │
                              ▼
                     ┌─────────────┐
                     │ STEP 2: Get │
                     │  Data       │
                     └──────┬──────┘
                              │
                              ▼
                     ┌─────────────┐
                     │ STEP 3: Com│
                     │  pare      │
                     │  (Old+New) │
                     └──────┬──────┘
                              │
                              ▼
                     ┌─────────────┐
                     │ STEP 4: Ana│
                     │  lyze      │
                     └──────┬──────┘
                              │
                              ▼
                     ┌─────────────┐
                     │ STEP 5: Dec│
                     │  ision     │
                     └──────┬──────┘
                              │
                              ▼
                     ┌─────────────┐
                     │ STEP 6: Sav│
                     │  e Exper.   │
                     └──────┬──────┘
                              │
                              ▼
                     ┌─────────────┐
                     │ STEP 7: Upd│
                     │  ate Hist.  │
                     └──────┬──────┘
                              │
                              ▼
                     ┌─────────────┐
                     │ Return     │
                     │  Decision  │
                     └─────────────┘
```

### STEP DETAILS

**STEP 1: Load Memory**
- Input: None
- Process: Read from disk (JSON files)
- Output: Loaded MemoryEntry objects
- Files: personality.json, behavior.json, strategy.json, history.json, relationship.json, prompt_memory.json

**STEP 2: Get Data**
- Input: None
- Process: Query World Memory
- Output: UnifiedInputPackage data
- Sources: V2, V3, V4, External data

**STEP 3: Compare Old + New**
- Input: Memory (old), Data (new)
- Process: Comparison engine
- Output: Changes, differences, similarities
- Actions: Identify changes, detect patterns

**STEP 4: Analyze**
- Input: Comparison results
- Process: Analysis engine
- Output: AnalysisResult object
- Includes: quality_scores, trust_scores, detected_changes, patterns, anomalies, confidence

**STEP 5: Decision Making**
- Input: Analysis results
- Process: Decision engine
- Output: Decision object
- Includes: choice, confidence, strategy, reasoning

**STEP 6: Save Experience**
- Input: Decision, Analysis
- Process: Create history entries
- Output: Updated Memory
- Actions: Add HistoryMemoryEntry, update BehaviorMemoryEntry, update StrategyMemoryEntry

**STEP 7: Update History**
- Input: Decision
- Process: Update state
- Output: Updated agent state
- Actions: Add HistoryEntry, update statistics

---

## DATA TRANSFORMATIONS

### INPUT LAYER TRANSFORMATIONS

**V2 Processing:**
```
Raw V2 Data
  │
  ▼ Transform:
  - Extract relevant match data
  - Validate data structure
  - Normalize numerical values
  - Add quality metadata
  ▼
Processed V2 Data
```

**V3 Processing:**
```
Raw V3 Data
  │
  ▼ Transform:
  - Parse complex knowledge structures
  - Validate knowledge integrity
  - Add trust scores
  - Categorize information
  ▼
Processed V3 Data
```

**Aggregation:**
```
Individual Collector Data (V2, V3, V4, External)
  │
  ▼ Transform:
  - Aggregate all data
  - Create metadata (quality, trust, completeness)
  - Add timestamps
  - Create version info
  ▼
UnifiedInputPackage
```

### AGENT INTERNAL TRANSFORMATIONS

**Comparison:**
```
Old Knowledge (Memory) + New Data (Collectors)
  │
  ▼ Transform:
  - Identify changes
  - Detect patterns
  - Calculate confidence
  - Prepare structured comparison
  ▼
Comparison Result
```

**Analysis:**
```
Comparison Result
  │
  ▼ Transform:
  - Quality assessment
  - Trust evaluation
  - Pattern recognition
  - Anomaly detection
  - Confidence calculation
  ▼
AnalysisResult
```

**Decision:**
```
AnalysisResult + PersonalityVector
  │
  ▼ Transform:
  - Strategy selection
  - Choice generation
  - Confidence calculation
  - Reasoning creation
  ▼
Decision Object
```

---

## DATA FORMATS

### UnifiedInputPackage Format

```json
{
  "timestamp": "2026-07-31T23:59:59",
  "version": "1.0.0",
  "data": {
    "v2": { "matches": [], "results": {}, "statistics": {} },
    "v3": { "patterns": [], "trends": {}, "historical": {} },
    "v4": { "agents": { "01": {}, "02": {}, "06": {} } },
    "external": { "api_data": {}, "manual_input": {} }
  },
  "metadata": {
    "quality_scores": {"v2": 0.95, "v3": 0.90, "v4": 0.85, "external": 0.60},
    "trust_scores": {"v2": 0.80, "v3": 0.85, "v4": 0.80, "external": 0.50},
    "sources_active": ["v2", "v3", "v4", "external"],
    "data_completeness": 0.95
  },
  "state": {
    "collector_status": {"v2": "completed", "v3": "completed", "v4": "completed", "external": "completed"},
    "aggregation_time": "0.123s",
    "data_valid": true
  }
}
```

### Decision Object Format

```json
{
  "agent_id": "01",
  "decision_id": "dec_01_20260731235959",
  "cycle_count": 5,
  "iteration_count": 30,
  "choice": "high_confidence_choice",
  "confidence": 0.85,
  "strategy": "analytical",
  "reasoning": "Based on high confidence analysis",
  "analysis": {
    "sources_used": ["v2", "v3"],
    "quality_scores": {"v2": 0.95, "v3": 0.90},
    "trust_scores": {"v2": 0.80, "v3": 0.85},
    "overall_confidence": 0.85
  },
  "success": true,
  "timestamp": "2026-07-31T23:59:59"
}
```

### Runtime State Format

```json
{
  "RuntimeName": "SSI_V5_Runtime",
  "version": "1.0.0",
  "start_time": "2026-07-31T23:59:59",
  "stop_time": null,
  "last_save_time": "2026-07-31T23:59:59",
  "status": "running",
  "cycle_count": 5,
  "total_cycles": 50,
  "total_iterations": 300,
  "execution_time_seconds": 3600.0,
  "avg_cycle_time": 72.0,
  "error_count": 0,
  "metadata": {"last_cycle_start": "2026-07-31T23:59:59"}
}
```

---

## DATA STORAGE LOCATIONS

### COMPLETE STORAGE MAP

```
SSI/
├── v5/
│   ├── runtime/
│   │   ├── runtime_config.json        (Config - Generated)
│   │   └── runtime_state.json          (State - Generated)
│   │
│   └── agents/ (Code)
│       └── ...
│
├── memory/
│   └── agents/
│       ├── agent_01/
│       │   ├── personality.json       (Generated)
│       │   ├── behavior.json         (Generated)
│       │   ├── strategy.json          (Generated)
│       │   ├── history.json           (Generated)
│       │   ├── relationship.json      (Generated)
│       │   ├── prompt_memory.json     (Generated)
│       │   ├── indexes.json           (Generated)
│       │   └── stats.json              (Generated)
│       └── agent_06/
│           └── ...
│
├── runtime.log                    (Log File - Generated)
│
└── DOKUMENTACJA/                   (Documentation)
    └── ...
```

### GENERATED FILES SUMMARY

| Kategoria | Sciezka | Opis | Generowany przez |
|----------|---------|------|-----------------|
| Config | `SSI/v5/runtime/runtime_config.json` | Konfiguracja systemu | RuntimeConfigManager |
| State | `SSI/v5/runtime/runtime_state.json` | Stan systemu | StateManager |
| Log | `SSI/runtime.log` | Logi systemowe | RuntimeController |
| Agent Memory | `SSI/memory/agents/agent_{ID}/*.json` | Pamiec agenta | AgentRuntime |

---

**Nota:** Ta dokumentacja jest czescia Projektu SSI V5.

**Ostatnia aktualizacja:** 2026-07-31
