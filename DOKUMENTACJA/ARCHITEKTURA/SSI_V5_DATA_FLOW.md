# SSI V5 - MAPA PRZEPŁYWU DANYCH

**Data:** 2026-08-01  
**Sprint:** 11.5 → 12+ (Planowanie)  
**Status:** Dokumentacja projektowa - Wersja 1.0.0  
**Autor:** Główny Architekt SSI V5  

---

## 📋 SPIS TREŚCI

1. [Makro Przepływ (Runtime Loop)](#1-makro-przepływ-runtime-loop)
2. [Szczegółowy Przepływ Danych w Jednym Cyklu Agenta](#2-szczegółowy-przepływ-danych-w-jednym-cyklu-agenta)
3. [Tabela Przepływu Danych](#3-tabela-przepływu-danych)

---

## 1. MAKRO PRZEPŁYW (RUNTIME LOOP)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    SSI V5 - MAKRO PRZEPŁYW DANYCH                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  [START]──────────────────────────────────────────────────────────────────────────┐│
│                          │                                                       ││
│          ┌───────────────────▼───────────────────┐                              ││
│          │          RUNTIME INITIALIZATION        │                              ││
│          │    runtime_controller.initialize()      │                              ││
│          └───────────────────┬───────────────────┘                              ││
│                          │                                                       ││
│  ┌───────────────────────────▼──────────────────────────────┐               ││
│  │              1. CREATE COMPONENTS                        │               ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │               ││
│  │  │ConfigManager│  │StateManager │  │Scheduler    │           │               ││
│  │  └─────┬────────┘  └─────┬────────┘  └─────┬────────┘          │               ││
│  │        │                │                │                   │               ││
│  │  ┌─────▼────────┐ ┌─────▼────────┐ ┌─────▼────────┐           │               ││
│  │  │ RuntimeConfig │ │ RuntimeState │ │ CycleConfig │           │               ││
│  │  └──────────────┘ └──────────────┘ └──────────────┘           │               ││
│  └───────────────────────────┬──────────────────────────────┘               ││
│                          │                                                       ││
│  ┌───────────────────────────▼──────────────────────────────┐               ││
│  │              2. CREATE AGENTS                               │               ││
│  │  _initialize_agents() -> agent_manager.create_agent()       │               ││
│  │  ┌─────────────────────────────────────────────────────┐   │               ││
│  │  │ FOR i IN 1..6:                                          │   │               ││
│  │  │   agent_id = f"0{i}"                                    │   │               ││
│  │  │   AgentRuntime.__init__(config)                         │   │               ││
│  │  │   + memory_store = create_agent_memory_store()       │   │               ││
│  │  │   + state_manager = create_agent_state_manager()   │   │               ││
│  │  │   + _initialize_memory() -> domyslne JSON             │   │               ││
│  │  └─────────────────────────────────────────────────────┘   │               ││
│  └───────────────────────────┬──────────────────────────────┘               ││
│                          │                                                       ││
│  ┌───────────────────────────▼──────────────────────────────┐               ││
│  │              3. CREATE COLLECTORS                            │               ││
│  │  _initialize_collectors()                                   │               ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │               ││
│  │  │ V2Collector  │  │ V3Collector  │  │ V4Collector  │  │External  │ │               ││
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │               ││
│  └───────────────────────────┬──────────────────────────────┘               ││
│                          │                                                       ││
│  ┌───────────────────────────▼──────────────────────────────┐               ││
│  │              4. RUNTIME LOOP (CYKLE)                         │               ││
│  │  run_loop() -> while True (PROD) / 10 cycles (TEST)           │               ││
│  │  ┌────────────────────────────────────────────────────────────┐│       ││
│  │  │ CYCLE N:                                                   ││       ││
│  │  │  1. state_manager.start_cycle()                           ││       ││
│  │  │     -> cycle_count++, cycle_start_time                    ││       ││
│  │  │                                                        ││       ││
│  │  │  2. world_context = _get_current_world_context()         ││       ││
│  │  │     -> {timestamp, cycle_count, runtime_status, ...}      ││       ││
│  │  │                                                        ││       ││
│  │  │  3. collector_data = _collect_current_data()             ││       ││
│  │  │     -> {v2: {...}, v3: {...}, v4: {...}, external: {...}} ││       ││
│  │  │                                                        ││       ││
│  │  │  4. FOR agent_id IN ["01","02","03","04","05","06"]:   ││       ││
│  │  │        _run_single_agent_cycle(agent, world_context, N) ││       ││
│  │  │                                                        ││       ││
│  │  │     +-----------------------------------------------+    ││       ││
│  │  │     | AGENT CYCLE:                              |    ││       ││
│  │  │     |  a) agent.load_memory()                  |    ││       ││
│  │  │     |     -> memory_store.load_from_disk()       |    ││       ││
│  │  │     |        personality.json                   |    ││       ││
│  │  │     |        behavior.json                       |    ││       ││
│  │  │     |        strategy.json                       |    ││       ││
│  │  │     |        history.json                         |    ││       ││
│  │  │     |                                           |    ││       ││
│  │  │     |  b) result = agent.run_cycle()           |    ││       ││
│  │  │     |     Step 1: _analyze_data()                |    ││       ││
│  │  │     |        IN: collector_data, world_context   |    ││       ││
│  │  │     |        OUT: analysis {quality, trust, ...} |    ││       ││
│  │  │     |     Step 2: _make_decision(analysis)        |    ││       ││
│  │  │     |        OUT: decision {choice, confidence}   |    ││       ││
│  │  │     |     Step 3: _save_experience()             |    ││       ││
│  │  │     |        -> HistoryMemoryEntry added        |    ││       ││
│  │  │     |     Step 4: _update_history()               |    ││       ││
│  │  │     |        -> state_manager updated           |    ││       ││
│  │  │     |                                           |    ││       ││
│  │  │     |  c) agent.save_memory()                   |    ││       ││
│  │  │     |     -> AgentMemoryStore.save_to_disk()   |    ││       ││
│  │  │     |        OUT: 4 pliki JSON zapisane          |    ││       ││
│  │  │     +-----------------------------------------------+    ││       ││
│  │  │                                                        ││       ││
│  │  │  5. _update_shared_memory() -> FUTURE (Sprint 12)     ││       ││
│  │  │  6. state_manager.end_cycle()                          ││       ││
│  │  │  7. controller.save_state() -> runtime_state.json      ││       ││
│  │  └────────────────────────────────────────────────────────────┘│       ││
│  │                                                        ││       ││
│  │  [LOOP: sleep(0.1s TEST) / sleep(1.0s PROD)]            ││       ││
│  └───────────────────────────┬──────────────────────────────┘               ││
│                          │                                                       ││
│                    [END/INTERRUPT]──────────────────────────────────────────┘│
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. SZCZEGÓŁOWY PRZEPŁYW DANYCH W JEDNYM CYKLU AGENTA

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              AGENT SINGLE CYCLE - DETAILED DATA FLOW                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  INPUT SIDE:                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    Collector Manager                                       │    │
│  │  _collect_current_data() -> runtime_controller.py:546                     │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │    │
│  │  │  v2:        │ │  v3:        │ │  v4:        │ │  external:  │       │    │
│  │  │  world_state│ │ knowledge_ │ │ agents_    │ │ market_    │       │    │
│  │  │  events[]   │ │ base       │ │ data       │ │ data       │       │    │
│  │  └─────┬───────┘ └─────┬───────┘ └─────┬───────┘ └─────┬───────┘       │    │
│  │        │               │               │               │               │    │
│  └────────┼───────────────┼───────────────┼───────────────┼───────────────┘    │
│           │               │               │               │                      │
│           └───────────────┼───────────────┼───────────────┘                      │
│                               │                                           │                      │
│               ┌───────────────▼───────────────┐                              │                      │
│               │    UNIFIED INPUT PACKAGE       │                              │                      │
│               │    _create_unified_input_package() -> runtime_controller.py:432 │                      │
│               └───────────────┬───────────────┘                              │                      │
│                               │                                           │                      │
│  ┌─────────────────────────────▼─────────────────────────────┐              │                      │
│  │              WORLD CONTEXT                               │              │                      │
│  │    _get_current_world_context() -> runtime_controller.py:???            │              │                      │
│  │    {timestamp, cycle_count, runtime_status, active_agents}             │              │                      │
│  └─────────────────────────────┬─────────────────────────────┘              │                      │
│                                │                                          │                      │
│  ┌─────────────────────────────▼─────────────────────────────┐              │                      │
│  │              AGENT MEMORY (LOAD)                          │              │                      │
│  │    agent.load_memory() -> AgentMemoryStore.load_from_disk()              │              │                      │
│  │    MemoryType: PERSONALITY, BEHAVIOR, STRATEGY, HISTORY                 │              │                      │
│  │    File: memory/agents/agent_XX/{personality,behavior,strategy,history}.json │              │                      │
│  │    Format: JSON -> List[MemoryEntry] (dataclass)                       │              │                      │
│  └─────────────────────────────┬─────────────────────────────┘              │                      │
│                                │                                          │                      │
│  ┌─────────────────────────────▼──────────────────────────────────────┐    │                      │
│  │                    AGENT PROCESSING                                   │    │                      │
│  │  agent_runtime.py:239 -> AgentRuntime.run_cycle()                     │    │                      │
│  │                                                                        │    │                      │
│  │  STEP 1: ANALYZE DATA                                              │    │    │                      │
│  │  _analyze_data(collector_data, world_context) -> agent_runtime.py       │    │    │                      │
│  │  INPUT:  collector_data (v2,v3,v4,external)                              │    │    │                      │
│  │         world_context (timestamp, cycle, status)                        │    │    │                      │
│  │         agent_memory (personality, behavior, strategy, history)        │    │    │                      │
│  │  OUTPUT: analysis = {                                                │    │    │                      │
│  │    quality_scores: {v2:0.95, v3:0.90, v4:0.85, external:0.60},         │    │    │                      │
│  │    trust_scores: {v2:0.8, v3:0.8, v4:0.8, external:0.6},            │    │    │                      │
│  │    changes: [...], patterns: [...], anomalies: [...]                  │    │    │                      │
│  │  }                                                                   │    │    │
│  │                                                                        │    │                      │
│  │  STEP 2: MAKE DECISION                                            │    │    │                      │
│  │  _make_decision(analysis) -> agent_runtime.py                         │    │    │                      │
│  │  INPUT:  analysis (from STEP 1)                                         │    │    │                      │
│  │         agent_memory (personality, strategy)                          │    │    │                      │
│  │  OUTPUT: decision = {                                                │    │    │                      │
│  │    decision_id: "dec_XX_YYYYMMDDHHMMSS",                            │    │    │                      │
│  │    choice: "high_confidence_choice",                                │    │    │                      │
│  │    confidence: 0.87,    strategy: "analytical",                        │    │    │
│  │    reasoning: "Analytical decision based on confidence 0.87",        │    │    │
│  │    advanced: {data_quality: 0.85, patterns_detected: 1}              │    │    │
│  │  }                                                                   │    │
│  │                                                                        │    │                      │
│  │  STEP 3: SAVE EXPERIENCE                                         │    │                      │
│  │  _save_experience() -> agent_runtime.py                              │    │                      │
│  │  INPUT:  decision (from STEP 2), analysis (from STEP 1)              │    │                      │
│  │  OUTPUT: new HistoryMemoryEntry(entry_id, event_type, related_id, conf)│    │
│  │                                                                        │    │
│  │  STEP 4: UPDATE HISTORY                                           │    │                      │
│  │  _update_history() -> state_manager.update_agent_state()              │    │                      │
│  │  OUTPUT: AgentState updated                                         │    │
│  │                                                                        │    │
│  └─────────────────────────────┬──────────────────────────────────────┘    │                      │
│                                │                                          │                      │
│  ┌─────────────────────────────▼─────────────────────────────┐              │                      │
│  │              AGENT MEMORY (SAVE)                          │              │                      │
│  │    agent.save_memory() -> AgentMemoryStore.save_to_disk()              │              │                      │
│  │    MemoryType: PERSONALITY, BEHAVIOR, STRATEGY, HISTORY                 │              │                      │
│  │    File: memory/agents/agent_XX/{personality,behavior,strategy,history}.json │              │
│  │    Format: List[MemoryEntry] (dataclass) -> JSON                        │              │
│  └─────────────────────────────────────────────────────────────┘              │
│                                                                                  │
│  OUTPUT SIDE:                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    RESULT OUTPUT                                        │    │
│  │    result = {                                                         │    │
│  │      agent_id: "01", cycle_count: 5,                                   │    │
│  │      decision: {decision_id, choice, confidence, strategy, reasoning, adv},│    │
│  │      analysis: {sources_used, quality_scores, trust_scores, overall_conf},│    │
│  │      success: True                                                    │    │
│  │    }                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. TABELA PRZEPŁYWU DANYCH

| **Krok** | **Moduł** | **Metoda** | **Dane Wejściowe** | **Dane Wyjściowe** | **Plik** | **Lokalizacja** |
|----------|-----------|------------|---------------------|---------------------|----------|----------------|
| 1 | RuntimeController | initialize() | RuntimeConfig | ConfigManager, StateManager, Scheduler, AgentManager, CollectorManager | runtime_controller.py | SSI/v5/runtime/ |
| 2 | ConfigManager | get_agent_config() | agent_id | AgentConfig (PersonalityConfig, StrategyConfig, MemoryConfig) | runtime_config.py | SSI/v5/runtime/ |
| 3 | AgentManager | create_agent() | AgentConfig | AgentRuntime | agent_manager.py | SSI/v5/agents/ |
| 4 | AgentRuntime | __init__() | AgentConfig | memory_store, state_manager, initialized memory | agent_runtime.py | SSI/v5/agents/ |
| 5 | AgentMemoryStore | load_from_disk() | agent_id, base_path | PersonalityMemoryEntry, BehaviorMemoryEntry, StrategyMemoryEntry, HistoryMemoryEntry | agent_memory_store.py | SSI/v5/agents/ |
| 6 | CollectorManager | get_latest_data() | collector_type | v2_data, v3_data, v4_data, external_data | collector_manager.py | SSI/v5/input_layer/ |
| 7 | RuntimeController | _collect_current_data() | - | {v2, v3, v4, external} | runtime_controller.py | SSI/v5/runtime/ |
| 8 | RuntimeController | _get_current_world_context() | cycle_count, runtime_status | world_context {timestamp, cycle_count, status, agents} | runtime_controller.py | SSI/v5/runtime/ |
| 9 | AgentRuntime | _analyze_data() | collector_data, world_context, agent_memory | analysis {quality_scores, trust_scores, changes, patterns, anomalies} | agent_runtime.py | SSI/v5/agents/ |
| 10 | AgentRuntime | _make_decision() | analysis, agent_memory | decision {decision_id, choice, confidence, strategy, reasoning, advanced} | agent_runtime.py | SSI/v5/agents/ |
| 11 | AgentRuntime | _save_experience() | decision, analysis | HistoryMemoryEntry | agent_runtime.py | SSI/v5/agents/ |
| 12 | AgentRuntime | _update_history() | decision | AgentState updated | agent_runtime.py | SSI/v5/agents/ |
| 13 | AgentMemoryStore | save_to_disk() | MemoryEntry[] | personality.json, behavior.json, strategy.json, history.json | agent_memory_store.py | SSI/v5/agents/ |
| 14 | StateManager | save_state() | RuntimeState | runtime_state.json | state_manager.py | SSI/v5/runtime/ |

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** Gotowy do przeglądu