# SYSTEM RESOURCE MAP - SSI V5 Phase 2 Design

**Wersja:** 1.0.0  
**Data:** 2026-07-31  
**Status:** PROJEKT FAZY 2 (Przed implementacją)  
**Autor:** SSI V5 Architecture Team  

---

## 📋 SPIS TREŚCI

1. [Przegląd Mapowania Zasobów](#1-przegląd-mapowania-zasobów)
2. [Mapa Przepływu Danych](#2-mapa-przepływu-danych)
3. [Mapa Pamięci Systemu](#3-mapa-pamięci-systemu)
4. [Mapa Plików i Katalogów](#4-mapa-plików-i-katalogów)
5. [Legenda i Konwencje](#5-legendy-i-konwencje)

---

## 1. Przegląd Mapowania Zasobów

### 1.1 Cel Dokumentu

Dokument **SYSTEM_RESOURCE_MAP.md** definiuje kompletne mapowanie wszystkich zasobów systemowych SSI V5, w tym:

- **Przepływ danych** pomiędzy modułami V2 → V3 → V4 → V5
- **Struktura pamięci** (indywidualna, kolektywna, długoterminowa, świat, modele)
- **Lokalizacja plików** i katalogów
- **Odpowiedzialność modułów** za tworzenie, odczyt i modyfikację zasobów

### 1.2 Zakres

- ✅ Istniejące moduły (Sprint 11.5 fundament)
- ✅ Przyszłe moduły (Phase 2)
- ✅ Wszystkie typy pamięci
- ✅ Wszystkie pliki generowane runtime
- ✅ Zależności pomiędzy zasobami

---

## 2. Mapa Przepływu Danych

### 2.1밖 Przepływ Główny (High-Level)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SSI V5 DATA FLOW ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │             │     │             │     │             │     │             │  │
│  │   V2 World  │────▶│   V3 World  │────▶│   V4 World  │────▶│  V5 Runtime  │  │
│  │   Models    │     │  Knowledge  │     │   Agents   │     │   Controller │  │
│  │             │     │             │     │             │     │             │  │
│  └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘  │
│           │                   │                   │                   │        │
│           ▼                   ▼                   ▼                   ▼        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        COLLECTOR MANAGER (V5)                         │   │
│  │  (v2_collector.py, v3_collector.py, v4_collector.py, external/)     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                           │                                           │          │
│                           ▼                                           │          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   UNIFIED INPUT PACKAGE (UIP)                       │   │
│  │  Format: JSON | Typ: SSIKnowledgePackage | Właściciel: CollectorManager │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                           │                                           │          │
│           ┌───────────────┼───────────────┬──────────────┐                │
│           ▼               ▼               ▼              ▼                │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐    ┌─────────┐                  │
│  │ Agent_01│   │ Agent_02│   │ Agent_03│    │  ...   │                  │
│  │ Memory  │   │ Memory  │   │ Memory  │    │ Agent_06│                  │
│  └────┬────┘   └────┬────┘   └────┬────┘    └────┬────┘                  │
│       │              │              │             │                      │
│       ▼              ▼              ▼             ▼                      │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     WORLD MEMORY (V5)                             │    │
│  │  - Knowledge Base (z V3)                                         │    │
│  │  - Agent Experiences (z V4)                                      │    │
│  │  - Validated Patterns                                            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                          │                                            │           │
│                          ▼                                            │           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                  COLLECTIVE MEMORY (V5)                          │    │
│  │  - Agent Relations                                               │    │
│  │  - Alliances & Conflicts                                         │    │
│  │  - Consensus Records                                             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                          │                                            │           │
│                          ▼                                            │           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │               COLLECTIVE CONTROL LAYER (CCL)                     │    │
│  │  - Monitoruje współpracę agentów                                  │    │
│  │  - Analizuje konflikty i sojusze                                 │    │
│  │  - Kontroluje przepływ informacji                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Szczegóły Przepływu Danych

#### 2.2.1 V2 → V5

| **Źródło** | **Dane** | **Format** | **Częstotliwość** | **Odbiorca** | **Zapis** |
|-----------|----------|------------|-------------------|--------------|-----------|
| V2 Models | Model predictions, features | JSON | Na żądanie | v2_collector.py | memory/world/v2_data.json |
| V2 Observation | Bet observations, market data | JSON | Cykliczny | v2_collector.py | memory/world/v2_observations.json |
| V2 Integration | Integrated model outputs | JSON | Cykliczny | v2_collector.py | memory/world/v2_integrated.json |

**v2_collector.py** (`SSI/v5/input_layer/v2_collector.py`):
- **Wejście:** Dane z `SSI/v2/models/`, `SSI/v2/observation/`
- **Wyjście:** `V2DataPackage` → UnifiedInputPackage
- **Odpowiedzialność:** Pobieranie, normalizacja, pakowanie danych V2

#### 2.2.2 V3 → V5

| **Źródło** | **Dane** | **Format** | **Częstotliwość** | **Odbiorca** | **Zapis** |
|-----------|----------|------------|-------------------|--------------|-----------|
| V3 Knowledge | Knowledge graphs, patterns | JSON | Cykliczny | v3_collector.py | memory/world/v3_knowledge.json |
| V3 Intelligence | Insights, correlations | JSON | Cykliczny | v3_collector.py | memory/world/v3_intelligence.json |
| V3 Memory | Historical knowledge | JSON | Cykliczny | v3_collector.py | memory/world/v3_memory.json |
| V3 Worlds | World states | JSON | Cykliczny | v3_collector.py | memory/world/v3_worlds.json |
| V3 Integration | Integrated knowledge | JSON | Cykliczny | v3_collector.py | memory/world/v3_integrated.json |

**v3_collector.py** (`SSI/v5/input_layer/v3_collector.py`):
- **Wejście:** Dane z `SSI/v3/knowledge/`, `SSI/v3/intelligence/`, `SSI/v3/memory/`, `SSI/v3/worlds/`
- **Wyjście:** `V3DataPackage` → UnifiedInputPackage
- **Odpowiedzialność:** Pobieranie, walidacja, segregacja wiedzy V3

#### 2.2.3 V4 → V5

| **Źródło** | **Dane** | **Format** | **Częstotliwość** | **Odbiorca** | **Zapis** |
|-----------|----------|------------|-------------------|--------------|-----------|
| V4 Agent Birth | Agent creation logs | JSON | Event-driven | v4_collector.py | memory/agents/v4_birth_logs.json |
| V4 Agent Core | Agent states, decisions | JSON | Cykliczny | v4_collector.py | memory/agents/v4_agent_states.json |
| V4 Room Core | Room interactions | JSON | Cykliczny | v4_collector.py | memory/agents/v4_room_interactions.json |
| V4 Personality | Personality vectors | JSON | Cykliczny | v4_collector.py | memory/agents/v4_personality_vectors.json |
| V4 Sync Policy | Synchronization events | JSON | Event-driven | v4_collector.py | memory/agents/v4_sync_events.json |

**v4_collector.py** (`SSI/v5/input_layer/v4_collector.py`):
- **Wejście:** Dane z `SSI/v4/agent_birth_system.py`, `SSI/v4/agent_core.py`, `SSI/v4/room_core.py`
- **Wyjście:** `V4DataPackage` → UnifiedInputPackage
- **Odpowiedzialność:** Monitorowanie agentów V4, zbieranie doświadczeń

#### 2.2.4 External → V5

| **Źródło** | **Dane** | **Format** | **Częstotliwość** | **Odbiorca** | **Zapis** |
|-----------|----------|------------|-------------------|--------------|-----------|
| Developer Input | Commands, requirements | JSON | Na żądanie | external/ | memory/external/developer_input.json |
| Laboratory | Experiments, discoveries | JSON | Event-driven | external/ | memory/external/laboratory_data.json |
| Agent Messages | Agent communication | JSON | Cykliczny | external/ | memory/external/agent_messages.json |
| System Events | System status, logs | JSON | Event-driven | external/ | memory/external/system_events.json |

**ExternalKnowledgeCollector** (`SSI/v5/input_layer/external/`):
- **Wejście:** Developer commands, laboratory results, agent messages
- **Wyjście:** `ExternalDataPackage` → UnifiedInputPackage
- **Odpowiedzialność:** Obsługa zewnętrznych źródeł wiedzy

### 2.3 Unified Input Package (UIP)

**Lokalizacja:** `SSI/v5/input_layer/collector_manager.py`

```python
# Format UIP
UnifiedInputPackage = {
    "timestamp": "2026-07-31T12:00:00Z",
    "version": "1.0.0",
    "data": {
        "v2": V2DataPackage,
        "v3": V3DataPackage, 
        "v4": V4DataPackage,
        "external": ExternalDataPackage
    },
    "metadata": {
        "sources_active": ["v2", "v3", "v4", "external"],
        "collection_time_ms": 150,
        "validation_status": "validated"
    }
}
```

**Przepływ UIP:**
1. **Tworzenie:** `CollectorManager._create_unified_input_package()`
2. **Dystrybucja:** Do wszystkich agentów V5
3. **Wykorzystanie:** `AgentRuntime.run_cycle(collector_data, world_context, cycle_count)`
4. **Zapis:** `memory/runtime/unified_input_package_{timestamp}.json`

### 2.4 Przepływ w Runtime Controller

```
┌─────────────────────────────────────────────────────────────┐
│                    Runtime Controller Cycle                       │
├─────────────────────────────────────────────────────────────┤
│  1. start_cycle()                                                  │
│     └── StateManager.start_cycle()                               │
│     └── runtime_state.status = RUNNING                          │
│     └── runtime_state.cycle_count += 1                         │
│                                                                 │
│  2. _run_collectors()                                             │
│     ├── v2_collector.collect() → V2DataPackage                  │
│     ├── v3_collector.collect() → V3DataPackage                  │
│     ├── v4_collector.collect() → V4DataPackage                  │
│     ├── external_collector.collect() → ExternalDataPackage      │
│     └── _create_unified_input_package() → UnifiedInputPackage    │
│                                                                 │
│  3. _run_agents_single_pass() / run_loop()                        │
│     └── For agent_id in "01", "02", "03", "04", "05", "06":    │
│         ├── agent.load_memory()                                  │
│         ├── collector_data = _collect_current_data()             │
│         ├── world_context = _get_current_world_context()        │
│         └── agent.run_cycle(collector_data, world_context, cycle) │
│                                                                 │
│  4. _update_shared_memory()                                       │
│     └── (Przyszła implementacja: World Memory Update)            │
│                                                                 │
│  5. save_state()                                                  │
│     ├── StateManager.save_state(StateType.FULL)                 │
│     └── runtime_state.json + agents_state.json + ...            │
│                                                                 │
│  6. end_cycle()                                                   │
│     └── StateManager.end_cycle()                                 │
└─────────────────────────────────────────────────────────────┘
```

### 2.5 Przepływ w Agent Runtime

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Cycle (Sprint 11.5 v2.0)                  │
├─────────────────────────────────────────────────────────────┤
│                                                                  │
│  CYKL AGENTA:                                                   │
│  1. Wczytaj pamięć                                              │
│     └── memory_store.load_from_disk()                           │
│     └── personality.json, strategy.json, history.json, ...     │
│                                                                  │
│  2. Pobierz dane (V2, V3, V4, External)                         │
│     └── collector_data (z UnifiedInputPackage)                  │
│     └── world_context (z RuntimeController)                     │
│                                                                  │
│  3. Porównaj: STARA WIEDZA + NOWE DANE                          │
│     └── _analyze_data(collector_data, world_context)           │
│     └── quality_scores, trust_scores, detected_changes        │
│                                                                  │
│  4. Analiza                                                     │
│     ├── Ocena jakości danych (_evaluate_data_quality)           │
│     ├── Porównanie z pamięcią (_compare_with_memory)           │
│     ├── Identyfikacja wzorców (_identify_patterns)             │
│     └── Identyfikacja anomalii (_identify_anomalies)           │
│                                                                  │
│  5. Decyzja                                                     │
│     ├── Wyběr strategii (_select_strategy)                       │
│     ├── Generowanie decyzji (_generate_decision)                │
│     └── Obliczenie zaufania (_calculate_decision_confidence)    │
│                                                                  │
│  6. Zapis doświadczenia                                         │
│     └── _save_experience(decision, analysis, cycle_count)       │
│     └── HistoryMemoryEntry → history.json                      │
│                                                                  │
│  7. Aktualizacja historii                                       │
│     └── _update_history(decision, analysis, cycle_count)       │
│     └── HistoryEntry → agent_state.json                         │
│                                                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Mapa Pamięci Systemu

### 3.1 Kategorizacja Pamięci

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SSI V5 MEMORY ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    A) PAMIĘĆ INDYWIDUALNA AGENTA                         │   │
│  │  Właściciel: AgentRuntime | Lokalizacja: SSI/memory/agents/agent_{ID}/ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│          │                              │                              │             │
│          ▼                              ▼                              ▼             │
│  ┌─────────────┐              ┌─────────────┐              ┌─────────────┐   │
│  │ PERSONALITY │              │ BEHAVIOR   │              │ STRATEGY   │   │
│  │ personality │              │ behavior   │              │ strategy   │   │
│  │    .json    │              │    .json    │              │    .json    │   │
│  └─────────────┘              └─────────────┘              └─────────────┘   │
│                                 │                                          │
│                                 ▼                                          │
│                         ┌─────────────────┐                                 │
│                         │    HISTORY     │                                 │
│                         │   history.json  │                                 │
│                         └─────────────────┘                                 │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    B) PAMIĘĆ KOLEKTYWNA                              │   │
│  │  Właściciel: CollectiveMemoryManager | Lokalizacja: SSI/memory/collective/ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│          │                              │                              │             │
│          ▼                              ▼                              ▼             │
│  ┌─────────────┐              ┌─────────────┐              ┌─────────────┐   │
│  │  KNOWLEDGE  │              │ RELATIONS   │              │ CONFLICTS  │   │
│  │ knowledge   │              │ relations   │              │ conflicts   │   │
│  │    .json    │              │    .json    │              │    .json    │   │
│  └─────────────┘              └─────────────┘              └─────────────┘   │
│                                 │                                          │
│                                 ▼                                          │
│                         ┌─────────────────┐                                 │
│                         │  CONSENSUS      │                                 │
│                         │  consensus.json  │                                 │
│                         └─────────────────┘                                 │
│                          був                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    C) PAMIĘĆ DŁUGOTERMINOWA                            │   │
│  │  Właściciel: LongTermMemoryManager | Lokalizacja: SSI/memory/long_term/ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│          │                              │                              │             │
│          ▼                              ▼                              ▼             │
│  ┌─────────────┐              ┌─────────────┐              ┌─────────────┐   │
│  │  PATTERNS   │              │EXPERIENCE  │              │ VALIDATED   │   │
│  │ patterns    │              │ experience  │              │  KNOWLEDGE  │   │
│  │    .json    │              │    .json    │              │    .json    │   │
│  └─────────────┘              └─────────────┘              └─────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    D) PAMIĘĆ ŚWIATA                                   │   │
│  │  Właściciel: WorldMemoryManager | Lokalizacja: SSI/memory/world/   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│          │                              │                              │             │
│          ▼                              ▼                              ▼             │
│  ┌─────────────┐              ┌─────────────┐              ┌─────────────┐   │
│  │   V2_DATA   │              │   V3_       │              │   V4_       │   │
│  │ v2_data.json│              │  KNOWLEDGE  │              │  AGENTS     │   │
│  └─────────────┘              └─────────────┘              └─────────────┘   │
│                                 │                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    E) PAMIĘĆ MODELI                                  │   │
│  │  Właściciel: ModelMemoryManager | Lokalizacja: SSI/memory/models/   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│          │                              │                              │             │
│          ▼                              ▼                              ▼             │
│  ┌─────────────┐              ┌─────────────┐              ┌─────────────┐   │
│  │ MODEL_REG   │              │ MODEL_PERF  │              │ MODEL_     │   │
│  │ registry    │              │ performance │              │ VERSIONS   │   │
│  │    .json    │              │    .json    │              │    .json    │   │
│  └─────────────┘              └─────────────┘              └─────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Szczegóły Pamięci Indywidualnej Agenta

#### A) Personality Memory

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | AgentRuntime | Każdy agent zarządza swoją własną osobowością |
| **Katalog** | `SSI/memory/agents/agent_{ID}/` | Indywidualny katalog για agenta |
| **Plik** | `personality.json` | Zbiorek wpisów PersonalityMemoryEntry |
| **Format** | JSON (List[Dict]) | Lista serializowanych wpisów |
| **Zapisujący moduł** | `AgentMemoryStore.save_to_disk()` | Metoda w agent_memory_store.py |
| **Odczytujący moduł** | `AgentMemoryStore.load_from_disk()` | Ładowanie przy starcie agenta |
| **Częstotliwość zapisu** | Po każdym cyklu | `agent.save_memory()` w runtime_controller.py |

**Struktura pliku:**
```json
[
  {
    "entry_id": "personality_01_001",
    "created_at": "2026-07-31T12:00:00Z",
    "updated_at": "2026-07-31T12:00:00Z",
    "memory_type": "personality",
    "risk": 0.5,
    "analysis": 0.8,
    "creativity": 0.5,
    "trust_v2": 0.8,
    "trust_v3": 0.8,
    "trust_v4": 0.8,
    "trust_external": 0.6,
    "agent_type": "balanced",
    "traits": {
      "risk_tolerance": 0.5,
      "analysis_depth": 0.7,
      "creativity_level": 0.5
    },
    "priorities": []
  }
]
```

**Użycie:**
- Inicjalizacja: `_create_default_memory()` w agent_runtime.py
- Decyzje: `_select_strategy()` używa wag osobowości
- Zaufanie: `_get_trust_score()` pobiera trust_v2, trust_v3, etc.

#### B) Behavior Memory

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | AgentRuntime | Indywidualne zachowania agenta |
| **Katalog** | `SSI/memory/agents/agent_{ID}/` | Indywidualny katalog |
| **Plik** | `behavior.json` | Zbiorek wpisów BehaviorMemoryEntry |
| **Format** | JSON (List[Dict]) | Lista serializowanych wpisów |
| **Zapisujący moduł** | `AgentMemoryStore.save_to_disk()` | Autom adjacency |
| **Odczytujący moduł** | `AgentMemoryStore.load_from_disk()` | Ładowanie przy starcie |
| **Częstotliwość zapisu** | Po każdym cyklu | `agent.save_memory()` |

**Przykładowy wpis:**
```json
{
  "entry_id": "beh_01_20260731120000",
  "created_at": "2026-07-31T12:00:00Z",
  "updated_at": "2026-07-31T12:00:00Z",
  "memory_type": "behavior",
  "action": "decision_making",
  "behavior_type": "decision_making",
  "description": "Made decision using analytical strategy",
  "context": {},
  "data_sources": ["v2", "v3", "v4"],
  "effectiveness": 0.0,
  "success_rate": 0.0,
  "usage_count": 1,
  "first_used": "2026-07-31T12:00:00Z",
  "last_used": "2026-07-31T12:00:00Z"
}
```

**Użycie:**
- Tworzenie: `_make_decision()` → dodaje BehaviorMemoryEntry
- Analiza: Śledzenie skuteczności zachowań

#### C) Strategy Memory

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | AgentRuntime | Dostępne strategie agenta |
| **Katalog** | `SSI/memory/agents/agent_{ID}/` | Indywidualny katalog |
| **Plik** | `strategy.json` | Zbiorek wpisów StrategyMemoryEntry |
| **Format** | JSON (List[Dict]) | Lista serializowanych wpisów |

**Przykładowy wpis:**
```json
{
  "entry_id": "strategy_01_analytical_001",
  "created_at": "2026-07-31T12:00:00Z",
  "strategy_name": "analytical",
  "strategy_type": "analytical",
  "description": "Default analytical strategy",
  "times_used": 5,
  "times_successful": 4,
  "success_rate": 0.8,
  "avg_confidence": 0.85,
  "first_used": "2026-07-31T12:00:00Z",
  "last_used": "2026-07-31T12:05:00Z"
}
```

**Użycie:**
- Inicjalizacja: `_create_default_memory()` tworzy domyślne strategie
- Wybór: `_select_strategy()` wybiera aktywną strategię
- Aktualizacja: `_update_strategy_effectiveness()` aktualizuje success_rate

#### D) History Memory

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | AgentRuntime | Historia działań agenta |
| **Katalog** | `SSI/memory/agents/agent_{ID}/` | Indywidualny katalog |
| **Plik** | `history.json` | Zbiorek wpisów HistoryMemoryEntry |
| **Format** | JSON (List[Dict]) | Lista serializowanych wpisów |

**Przykładowy wpis:**
```json
{
  "entry_id": "hist_01_20260731120000",
  "created_at": "2026-07-31T12:00:00Z",
  "updated_at": "2026-07-31T12:00:00Z",
  "memory_type": "history",
  "event_type": "decision_made",
  "description": "Decision: high_confidence_choice",
  "categories": ["decision", "autonomous"],
  "related_decision_id": "dec_01_20260731120000",
  "outcome": {},
  "success": null,
  "evaluation": 0.0,
  "confidence": 0.85
}
```

**Użycie:**
- Zapis: `_save_experience()` dodaje wpis historii
- Aktualizacja: `_update_history()` dodaje do state_manager

#### E) Relationship Memory

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | AgentRuntime | Relacje z innymi agentami |
| **Katalog** | `SSI/memory/agents/agent_{ID}/` | Indywidualny katalog |
| **Plik** | `relationship.json` | Zbiorek wpisów RelationshipMemoryEntry |
| **Format** | JSON (List[Dict]) | Lista serializowanych wpisów |

**Przykładowy wpis:**
```json
{
  "entry_id": "rel_01_02_20260731120000",
  "created_at": "2026-07-31T12:00:00Z",
  "other_agent_id": "02",
  "relationship_type": "neutral",
  "trust_score": 0.0,
  "collaboration_score": 0.0,
  "conflict_score": 0.0,
  "interactions": 0,
  "positive_interactions": 0,
  "negative_interactions": 0,
  "neutral_interactions": 0
}
```

### 3.3 Szczegóły Pamięci Kolektywnej

#### A) Knowledge Base (z V3)

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | CollectiveMemoryManager (przyszły) | Wspólna wiedza systemu |
| **Katalog** | `SSI/memory/collective/` | Katalog pamięci kolektywnej |
| **Plik** | `knowledge.json` | Zbiorek wiedzy z V3 |
| **Format** | JSON | Struktura wiedzy |
| **Źródło** | v3_collector.py | Dane z V3 Knowledge |
| **Zapisujący moduł** | WorldMemoryManager (przyszły) | Konsolidacja wiedzy |
| **Odczytujący moduł** | Wszyscy agenci | Dostęp przez WorldMemory |

#### B) Relations

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | CollectiveMemoryManager | Relacje pomiędzy agentami |
| **Katalog** | `SSI/memory/collective/` | Katalog pamięci kolektywnej |
| **Plik** | `relations.json` | Macierz relacji agentów |
| **Format** | JSON | Graf relacji |

**Struktura:**
```json
{
  "agent_01": {
    "agent_02": {
      "trust_score": 0.7,
      "collaboration_score": 0.8,
      "conflict_score": 0.1,
      "interactions": 10
    },
    "agent_03": {
      "trust_score": 0.5,
      "collaboration_score": 0.3,
      "conflict_score": 0.4,
      "interactions": 5
    }
  }
}
```

#### C) Conflicts

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | CollectiveControlLayer (przyszły) | Rejestr konfliktów |
| **Katalog** | `SSI/memory/collective/` | Katalog pamięci kolektywnej |
| **Plik** | `conflicts.json` | Historia konfliktów |
| **Format** | JSON | Lista konfliktów |

#### D) Consensus

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | CollectiveControlLayer | Rejestr konsensusów |
| **Katalog** | `SSI/memory/collective/` | Katalog pamięci kolektywnej |
| **Plik** | `consensus.json` | Historia decyzji konsensusowych |
| **Format** | JSON | Lista konsensusów |

### 3.4 Szczegóły Pamięci Długoterminowej

#### A) Patterns

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | LongTermMemoryManager (przyszły) | Wzorce wykryte w systemie |
| **Katalog** | `SSI/memory/long_term/` | Katalog pamięci długoterminowej |
| **Plik** | `patterns.json` | Zbiorek wzorców |
| **Format** | JSON | Lista wzorców z metadanych |

#### B) Experience

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | LongTermMemoryManager | Doświadczenia systemowe |
| **Katalog** | `SSI/memory/long_term/` | Katalog pamięci długoterminowej |
| **Plik** | `experience.json` | Zbiorek doświadczeń |
| **Format** | JSON | Lista doświadczeń |

#### C) Validated Knowledge

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | LongTermMemoryManager | Zweryfikowana wiedza |
| **Katalog** | `SSI/memory/long_term/` | Katalog pamięci długoterminowej |
| **Plik** | `validated_knowledge.json` | Baza wiedzy zweryfikowanej |
| **Format** | JSON | Struktura wiedzy |

### 3.5 Szczegóły Pamięci Świata

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | WorldMemoryManager (przyszły) | Stan świata systemu |
| **Katalog** | `SSI/memory/world/` | Katalog pamięci świata |
| **Pliki** | `v2_data.json`, `v3_knowledge.json`, `v4_agents.json` | Dane z kolektorów |
| **Format** | JSON | Struktury danych źródłowych |
| **Źródło** | Collectory V2, V3, V4 | Dane wejściowe |
| **Zapisujący moduł** | CollectorManager | Konsolidacja danych świata |

### 3.6 Szczegóły Pamięci Modeli

| **Atrybut** | **Wartość** | **Opis** |
|-------------|-------------|----------|
| **Właściciel** | ModelMemoryManager (przyszły) | Rejestr modeli systemu |
| **Katalog** | `SSI/memory/models/` | Katalog pamięci modeli |
| **Pliki** | `registry.json`, `performance.json`, `versions.json` | Rejestry modeli |
| **Format** | JSON | Struktury modeli |

---

## 4. Mapa Plików i Katalogów

### 4.1 Struktura Katalogów

```
SSI/
├── v2/
│   ├── models/
│   │   ├── (modele V2)
│   │   └── runtime_state.json (stan V2)
│   ├── observation/
│   │   └── (dane obserwacyjne)
│   ├── training/
│   │   └── (dane treningowe)
│   └── integration/
│       └── (integracja V2)
│
├── v3/
│   ├── intelligence/
│   │   └── (dane inteligencji)
│   ├── knowledge/
│   │   └── (baza wiedzy)
│   ├── memory/
│   │   └── (pamięć V3)
│   ├── worlds/
│   │   └── (stany świata)
│   ├── integration/
│   │   └── (integracja V3)
│   └── tests/
│       └── (testy V3)
│
├── v4/
│   ├── agent_birth_system.py
│   ├── agent_core.py
│   ├── agent_sync_policy.py
│   ├── personality_vector.py
│   ├── room_core.py
│   └── __init__.py
│
├── v5/
│   ├── runtime/
│   │   ├── runtime_controller.py
│   │   ├── runtime_config.py
│   │   ├── state_manager.py
│   │   ├── scheduler.py
│   │   ├── runtime_state.json (generowany)
│   │   ├── agents_state.json (generowany)
│   │   ├── memory_state.json (generowany)
│   │   └── collectors_state.json (generowany)
│   │
│   ├── agents/
│   │   ├── agent_runtime.py
│   │   ├── agent_memory_store.py
│   │   ├── agent_state.py
│   │   ├── agents_config.py
│   │   ├── agent_manager.py
│   │   └── __init__.py
│   │
│   └── input_layer/
│       ├── collector_manager.py
│       ├── collector_registry.py
│       ├── data_models.py
│       ├── knowledge_metadata.py
│       ├── knowledge_package.py
│       ├── v2_collector.py
│       ├── v3_collector.py
│       ├── v4_collector.py
│       ├── external/
│       │   └── (moduły external input)
│       └── __init__.py
│
├── memory/
│   ├── agents/
│   │   ├── agent_01/
│   │   │   ├── personality.json (generowany)
│   │   │   ├── behavior.json (generowany)
│   │   │   ├── strategy.json (generowany)
│   │   │   ├── history.json (generowany)
│   │   │   ├── relationship.json (generowany)
│   │   │   ├── prompt.json (generowany)
│   │   │   ├── indexes.json (generowany)
│   │   │   └── stats.json (generowany)
│   │   ├── agent_02/
│   │   │   └── (takie same pliki)
│   │   ├── agent_03/
│   │   ├── agent_04/
│   │   ├── agent_05/
│   │   └── agent_06/
│   │
│   ├── collective/ (PRZYSZŁOŚĆ - Phase 2)
│   │   ├── knowledge.json
│   │   ├── relations.json
│   │   ├── conflicts.json
│   │   └── consensus.json
│   │
│   ├── long_term/ (PRZYSZŁOŚĆ - Phase 2)
│   │   ├── patterns.json
│   │   ├── experience.json
│   │   └── validated_knowledge.json
│   │
│   ├── world/ (PRZYSZŁOŚĆ - Phase 2)
│   │   ├── v2_data.json
│   │   ├── v3_knowledge.json
│   │   └── v4_agents.json
│   │
│   └── models/ (PRZYSZŁOŚĆ - Phase 2)
│       ├── registry.json
│       ├── performance.json
│       └── versions.json
│
├── config/
│   └── (konfiguracje systemowe)
│
├── data/
│   └── (dane systemowe)
│
├── DOKUMENTACJA/
│   ├── PROJECT_JOURNAL_V5.md
│   ├── SSI_V5_ARCHITECTURE_PART1.md
│   ├── SSI_V5_ARCHITECTURE_PART2.md
│   ├── SSI_V5_MEMORY_DESIGN.md
│   ├── SSI_V5_DATA_FLOW.md
│   ├── SSI_V5_AGENT_BEHAVIOR.md
│   ├── RAPORT_KONCOWY_SSI_V5_PHASE_1.md
│   ├── SYSTEM_RESOURCE_MAP.md (TEN DOKUMENT)
│   ├── TOOL_DEPENDENCY_GRAPH.md (PRZYSZŁY)
│   ├── DEVELOPER_INTERFACE.md (PRZYSZŁY)
│   └── PHASE_2_IMPLEMENTATION_PLAN.md (PRZYSZŁY)
│
└── workflows/
    └── (przepływy pracy)
```

### 4.2 Istniejące Pliki (Sprint 11.5)

| **Ścieżka** | **Kto tworzy** | **Kiedy powstaje** | **Dane zawarte** | **Kto korzysta** |
|--------------|----------------|-------------------|------------------|------------------|
| `SSI/v5/runtime/runtime_state.json` | StateManager | `save_state()` | Stan runtime, cykle, czasy | RuntimeController, Agenci |
| `SSI/v5/runtime/agents_state.json` | StateManager | `save_state(StateType.AGENTS)` | Stany wszystkich agentów | RuntimeController |
| `SSI/v5/runtime/memory_state.json` | StateManager | `save_state(StateType.MEMORY)` | Stan systemu pamięci | StateManager |
| `SSI/v5/runtime/collectors_state.json` | StateManager | `save_state(StateType.COLLECTORS)` | Stany kolektorów | RuntimeController |
| `SSI/v5/runtime/runtime_config.json` | RuntimeConfigManager | `save_config()` | Konfiguracja runtime | RuntimeController |
| `SSI/memory/agents/agent_{ID}/personality.json` | AgentMemoryStore | `save_to_disk()` | Osobowość agenta | AgentRuntime |
| `SSI/memory/agents/agent_{ID}/behavior.json` | AgentMemoryStore | `save_to_disk()` | Zachowania agenta | AgentRuntime |
| `SSI/memory/agents/agent_{ID}/strategy.json` | AgentMemoryStore | `save_to_disk()` | Strategie agenta | AgentRuntime |
| `SSI/memory/agents/agent_{ID}/history.json` | AgentMemoryStore | `save_to_disk()` | Historia agenta | AgentRuntime |
| `SSI/memory/agents/agent_{ID}/relationship.json` | AgentMemoryStore | `save_to_disk()` | Relacje agenta | AgentRuntime |
| `SSI/memory/agents/agent_{ID}/prompt.json` | AgentMemoryStore | `save_to_disk()` | Prompty agenta | AgentRuntime |
| `SSI/memory/agents/agent_{ID}/indexes.json` | AgentMemoryStore | `save_to_disk()` | Indeksy pamięci | AgentMemoryStore |
| `SSI/memory/agents/agent_{ID}/stats.json` | AgentMemoryStore | `save_to_disk()` | Statystyki pamięci | AgentMemoryStore |

### 4.3 Przyszłe Pliki (Phase 2)

| **Ścieżka** | **Kto tworzy** | **Kiedy powstaje** | **Dane zawarte** | **Kto korzysta** |
|--------------|----------------|-------------------|------------------|------------------|
| `SSI/memory/collective/knowledge.json` | CollectiveMemoryManager | Po zebraniu wiedzy | Wspólna baza wiedzy | Wszyscy agenci |
| `SSI/memory/collective/relations.json` | CollectiveMemoryManager | Po interakcjach | Macierz relacji agentów | CCL |
| `SSI/memory/collective/conflicts.json` | CollectiveControlLayer | Przy wykryciu konfliktu | Rejestr konfliktów | CCL |
| `SSI/memory/collective/consensus.json` | CollectiveControlLayer | Przy konsensusie | Rejestr konsensusów | CCL |
| `SSI/memory/long_term/patterns.json` | LongTermMemoryManager | Po identyfikacji wzorców | Wzorce systemowe | Wszyscy agenci |
| `SSI/memory/long_term/experience.json` | LongTermMemoryManager | Po zebraniu doświadczeń | Doświadczenia systemowe | Wszyscy agenci |
| `SSI/memory/long_term/validated_knowledge.json` | LongTermMemoryManager | Po weryfikacji | Zweryfikowana wiedza | Wszyscy agenci |
| `SSI/memory/world/v2_data.json` | WorldMemoryManager | Po zebraniu V2 | Dane V2 | Agenci |
| `SSI/memory/world/v3_knowledge.json` | WorldMemoryManager | Po zebraniu V3 | Wiedza V3 | Agenci |
| `SSI/memory/world/v4_agents.json` | WorldMemoryManager | Po zebraniu V4 | Stany agentów V4 | Agenci |
| `SSI/memory/world/unified_input_package_{timestamp}.json` | CollectorManager | Po stworzeniu UIP | Zunifikowany pakiet wejściowy | Archiwum |
| `SSI/memory/models/registry.json` | ModelMemoryManager | przy rejestracji modelu | Rejestr modeli | System |
| `SSI/memory/models/performance.json` | ModelMemoryManager | Po ocenie modelu | Wydajność modeli | System |
| `SSI/memory/models/versions.json` | ModelMemoryManager | Przy aktualizacji | Wersje modeli | System |

### 4.4 Pliki Tymczasowe Runtime

| **Ścieżka** | **Kto tworzy** | **Kiedy powstaje** | **Dane zawarte** | **Czas życia** |
|--------------|----------------|-------------------|------------------|----------------|
| `SSI/v5/runtime/test_state.json` | StateManager | Testy | Stan testowy | Do usunięcia |
| `SSI/v5/input_layer/test_package.json` | CollectorManager | Testy | Testowy UIP | Do usunięcia |

---

## 5. Legendy i Konwencje

### 5.1 Konwencje Nazewnictwa

| **Typ** | **Format** | **Przykład** | **Opis** |
|---------|------------|--------------|----------|
| Plik pamięci agenta | `{memory_type}.json` | `personality.json` | Zbiorek wpisów danego typu |
| ID wpisu pamięci | `{type}_{agent_id}_{timestamp}` | `hist_01_20260731120000` | Unikalny identyfikator |
| Plik stanu | `{state_type}_state.json` | `runtime_state.json` | Stan systemu |
| Katalog agenta | `agent_{ID}` | `agent_01` | Indywidualny katalog |

### 5.2 Typy Pamięci (MemoryType Enum)

```python
# SSI/v5/agents/agent_memory_store.py
class MemoryType(Enum):
    PERSONALITY = "personality"
    BEHAVIOR = "behavior"
    STRATEGY = "strategy"
    HISTORY = "history"
    RELATIONSHIP = "relationship"
    PROMPT = "prompt"
```

### 5.3 Statusy Plików

| **Status** | **Opis** | **Kolor** |
|------------|----------|-----------|
| ✅ Istniejący | Plik istnieje w Sprint 11.5 | Zielony |
| 🟡 Planowany | Plik zostanie utworzony w Phase 2 | Żółty |
| 🔴 Przyszły | Plik dla faz późniejszych | Czerwony |

### 5.4 Symbolika Strzałek

| **Symbol** | **Znaczenie** |
|------------|---------------|
| `→` | Przepływ danych |
| `↓` | Zapis do pliku |
| `↑` | Odczyt z pliku |
| `↔` | Wzajemna interakcja |
| `---` | Zależność |

---

## 📌 Podsumowanie

Dokument **SYSTEM_RESOURCE_MAP.md** definiuje:

- ✅ **Mapę przepływu danych** V2 → V3 → V4 → V5
- ✅ **5 typów pamięci** (A-E) z detalami
- ✅ **Strukturę katalogów** i plików
- ✅ **Odpowiedzialność modułów** za zasoby
- ✅ **Częstotliwość** operacji na zasobach

**Następne kroki:**
1. Utworzenie **TOOL_DEPENDENCY_GRAPH.md** - zależności narzędzi
2. Utworzenie **DEVELOPER_INTERFACE.md** - interfejs programisty
3. Utworzenie **PHASE_2_IMPLEMENTATION_PLAN.md** - plan implementacji

---

**Dokument podpisany cyfrowo:** SSI V5 Architecture Team  
**Data utrwalenia:** 2026-07-31  
**Wersja systemu:** Sprint 11.5 + Phase 2 Design
