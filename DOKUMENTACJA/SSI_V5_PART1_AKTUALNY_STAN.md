# SSI V5 - ANALIZA AKTUALNEGO STANU PO SPRINCIE 11.5

**Data:** 2026-07-31  
**Sprint:** 11.5  
**Status:** Działający system runtime  

---

## 🎯 CZĘŚĆ 1: ANALIZA AKTUALNEGO SYSTEMU

---

### 1.1. Punkty wejścia i uruchomienie systemu

#### Główne pliki uruchomieniowe:
```
D:/sts/aplikacjaTyperBetAi/
├── start_ssi.py              # PRODUCTION - 5 godzin ciągłej pracy
└── start_ssi_test.py         # TEST MODE - 10 cykli (60 iteracji)
```

#### Przepływ uruchomienia PRODUCTION (start_ssi.py):
```
main()
├─ create_default_runtime_config()
│  └─ RuntimeConfig(mode=PRODUCTION, test_mode=False, cycle_duration_hours=5)
├─ create_runtime_controller(config)
│  └─ SSIRuntimeController.__init__()
├─ controller.initialize()
│  ├─ RuntimeConfigManager(self.config)
│  ├─ StateManager.initialize()
│  ├─ Scheduler.initialize()
│  ├─ _initialize_agents() → Tworzy 6 agentów z agent_manager
│  └─ _initialize_collectors() → Tworzy V2, V3, V4, External
├─ controller.run_loop()
│  └─ Ciągła pętla while: max_cycles=∞, sleep=1.0s, agent_order=[01,02,03,04,05,06]
└─ controller.save_state() → runtime_state.json
```

#### Przepływ uruchomienia TEST (start_ssi_test.py):
```
main()
├─ create_default_runtime_config()
│  └─ RuntimeConfig(mode=TEST, test_mode=True, test_cycles=10)
├─ create_runtime_controller(config)
├─ controller.initialize() → Tak samo jak production
├─ controller.run_loop()
│  └─ Ciągła pętla: max_cycles=10, sleep=0.1s, agent_order=[01,02,03,04,05,06]
├─ print_test_summary() → Podsumowanie 60 iteracji
└─ controller.save_state() → runtime_state.json
```

---

### 1.2. Przepływ danych w systemie - Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              START SYSTEM                                   │
│                         (start_ssi.py / start_ssi_test.py)                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                        │                                          │
                        ▼                                          ▼
┌─────────────────────────────────────┐   ┌─────────────────────────────────┐
│           RUNTIME CONTROLLER         │   │          CONFIG MANAGER         │
│    (runtime_controller.py:45)         │   │     (runtime_config.py:174)      │
└─────────────────────────────────────┘   └─────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    INITIALIZATION PHASE                                   │
│                                                                          │
│  RuntimeController.initialize()                                             │
│    ├─ config_manager = RuntimeConfigManager(config)                       │
│    ├─ state_manager.initialize() → Tworzy RuntimeState, AgentState×6       │
│    ├─ scheduler.initialize()                                              │
│    ├─ _initialize_agents() → agent_manager.create_agent_manager()         │
│    │   └─ FOR i IN 1..6: create_agent(config) → AgentRuntime()            │
│    │       ├─ AgentRuntime.__init__()                                     │
│    │       │   ├─ memory_store = create_agent_memory_store()              │
│    │       │   ├── state_manager = create_agent_state_manager()           │
│    │       │   └─ _initialize_memory() → Tworzy domyślną pamięć             │
│    │       └─ agent_manager.agents[agent_id] = agent                    │
│    └─ _initialize_collectors() → v2, v3, v4, external collectors          │
└─────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    RUNTIME LOOP PHASE                                     │
│                                                                          │
│  RuntimeController.run_loop()                                             │
│    ├─ state_manager.start_cycle()                                       │
│    ├─ world_context = _get_current_world_context()                      │
│    │   └─ {timestamp, cycle_count, runtime_status, active_agents}        │
│    ├─ collector_data = _collect_current_data()                          │
│    │   └─ {v2: v2_collector.get_latest_data(), ...}                      │
│    ├─ FOR agent_id IN ["01","02","03","04","05","06"]:              │
│    │   └─ result = _run_single_agent_cycle(agent, world_context, N)     │
│    │       ├─ agent.load_memory() → Wczytuje JSON z dysku               │
│    │       ├─ result = agent.run_cycle(collector_data, world_context, N)│
│    │       │   → Zwraca: decision, analysis, success                     │
│    │       └─ agent.save_memory() → Zapisuje do JSON na dysk            │
│    └─ state_manager.end_cycle()                                         │
│    └─ save_state() → runtime_state.json (co 10 cykli czyli zawsze w TEST) │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 1.3. Tworzenie agentów - Dokładny przepływ

**Ścieżka:** `runtime_controller.py:123` → `_initialize_agents()`

```python
# runtime_controller.py - _initialize_agents()
def _initialize_agents(self):
    self.agent_manager = agent_manager.create_agent_manager(self.config)
    
    for i in range(1, 7):
        agent_id = f"0{i}"  # "01" do "06"
        agent_config = self.config_manager.get_agent_config(agent_id)
        # → runtime_config.py:234 → RuntimeConfigManager.get_agent_config()
        #    Tworzy: AgentPersonalityConfig, AgentStrategyConfig, AgentMemoryConfig
        
        agent = self.agent_manager.create_agent(agent_config)
        # → agent_manager.py:??? → create_agent()
        #    Zwraca: AgentRuntime(config)
        
        self.agents[agent_id] = agent
```

**agent_runtime.py - __init__():**
```python
def __init__(self, config: AgentConfig):
    self.agent_id = config.agent_id
    self.memory_store = create_agent_memory_store(self.agent_id, base_path)
    self.state_manager = create_agent_state_manager(self.agent_id)
    self._initialize_memory()  # Tworzy domyślną pamięć jeśli nie istnieje
    self._initialize_state()
```

---

### 1.4. Wykonanie cyklu pojedynczego agenta

**Ścieżka:** `runtime_controller.py:330` → `_run_single_agent_cycle()`

```
_run_single_agent_cycle(agent, world_context, cycle_count):
├─ agent.load_memory()
│  └─ AgentMemoryStore.load_from_disk()
│     └─ Wczytuje z: memory/agents/agent_{id}/{personality,behavior,strategy,history}.json
│
├─ collector_data = self._collect_current_data()
│  └─ Zwraca: {"v2": data, "v3": data, "v4": data, "external": data}
│
├─ result = agent.run_cycle(collector_data, world_context, cycle_count)
│  └─ agent_runtime.py:239 → AgentRuntime.run_cycle()
│      ├─ Step 1: Analiza danych → _analyze_data()
│      │   └─ Zwraca: analysis = {quality_scores, trust_scores, changes, patterns, anomalies}
│      ├─ Step 2: Decyzja → _make_decision(analysis)
│      │   └─ Zwraca: decision = {choice, confidence, strategy, reasoning}
│      ├─ Step 3: Zapis doświadczenia → _save_experience()
│      │   └─ Dodaje: HistoryMemoryEntry do memory_store
│      └─ Step 4: Aktualizacja historii → _update_history()
│          └─ Aktualizuje: state_manager
│
└─ agent.save_memory()
   └─ AgentMemoryStore.save_to_disk()
       └─ Zapisuje do: memory/agents/agent_{id}/{personality,behavior,strategy,history}.json
```

---

### 1.5. Kolektory - Lokalizacja i rola

| **Kolektor** | **Plik** | **Lokalizacja** | **Rola** | **Tworzony w** |
|--------------|----------|----------------|----------|----------------|
| V2 World | `v2_collector.py` | `SSI/v5/input_layer/` | Zbieranie danych światowych | `_initialize_collectors()` |
| V3 Knowledge | `v3_collector.py` | `SSI/v5/input_layer/` | Zbieranie wiedzy | `_initialize_collectors()` |
| V4 Agents | `v4_collector.py` | `SSI/v5/input_layer/` | Zbieranie danych o agentach | `_initialize_collectors()` |
| External | `external.py` | `SSI/v5/input_layer/external/` | Zbieranie danych zewnętrznych | `_initialize_collectors()` |
| Manager | `collector_manager.py` | `SSI/v5/input_layer/` | Zarządzanie kolektorami | `_initialize_collectors()` |

**Użycie:**
- Pobieranie: `_collect_current_data()` (runtime_controller.py:546)
- Pakowanie: `_create_unified_input_package()` (runtime_controller.py:432)

---

### 1.6. Zapis pamięci agenta

**Proces:** `agent.save_memory()` → `AgentMemoryStore.save_to_disk()`

```
AgentRuntime.save_memory()
└─ AgentMemoryStore.save_to_disk() → agent_memory_store.py:512
    └─ FOR mem_type IN MemoryType:
        ├── PERSONALITY → personality.json
        ├── BEHAVIOR → behavior.json
        ├── STRATEGY → strategy.json
        ├── HISTORY → history.json
        ├── RELATIONSHIP → relationship.json
        └── PROMPT → prompt.json
        
        Serializacja:
        entry_dict = asdict(entry)
        if 'memory_type' in entry_dict and isinstance(entry_dict['memory_type'], MemoryType):
            entry_dict['memory_type'] = entry_dict['memory_type'].value  # enum → string
        json.dump(entry_dict, file, ensure_ascii=False)
```

**Lokalizacja:**
```
SSI/memory/agents/
├── agent_01/
│   ├── personality.json
│   ├── behavior.json
│   ├── strategy.json
│   └── history.json
├── agent_02/
│   └── (analogiczne)
... (agent_03 do agent_06)
```

---

### 1.7. Zapis stanu systemu

**Proces:** `controller.save_state()` → `StateManager.save_state()`

**Zawartość runtime_state.json:**
```json
{
  "RuntimeName": "SSI_V5_Runtime",
  "version": "1.0.0",
  "status": "shutdown",
  "start_time": "2026-07-31T12:00:00",
  "stop_time": "2026-07-31T12:00:01",
  "cycle_count": 10,
  "total_cycles": 10,
  "current_test_cycle": 10,
  "last_agent_id": "06",
  "last_save_time": "2026-07-31T12:00:01",
  "test_mode": true,
  "metadata": {"total_iterations": 60}
}
```

---
---

## 📊 CZĘŚĆ 2: MAPA JEDNEGO CYKLU AGENTA

---

### 2.1. Dokładny przepływ - Sekwencyjny diagram

```
CYCLE N (runtime_controller.py:301-357)
├─ 1. state_manager.start_cycle() → cycle_count++, cycle_start_time
├─ 2. world_context = _get_current_world_context() → {timestamp, cycle_count, status, agents}
├─ 3. collector_data = _collect_current_data() → {v2, v3, v4, external}
│
├─ 4. FOR agent_id IN ["01","02","03","04","05","06"]:
│   ├─ a) agent.load_memory() → memory_store.load_from_disk()
│   │   └─ Wczytuje 4 pliki JSON do obiektyw MemoryEntry
│   │
│   ├─ b) result = _run_single_agent_cycle():
│   │   ├─── agent.run_cycle(collector_data, world_context, cycle_count)
│   │   │    ├── Step 1: Wczytana pamięć (juz załadowana)
│   │   │    ├── Step 2: Dane (juz przekazane)
│   │   │    ├── Step 3: _analyze_data() → analysis = {quality, trust, changes, patterns, anomalies}
│   │   │    ├── Step 4: _make_decision() → decision = {choice, confidence, strategy, reasoning}
│   │   │    ├── Step 5: _save_experience() → Dodaje HistoryMemoryEntry
│   │   │    └── Step 6: _update_history() → Aktualizuje state_manager
│   │   └─── Zwraca: result = {agent_id, cycle_count, decision, analysis, success}
│   │
│   ├─ c) runtime_state.last_agent_id = agent_id
│   ├─ d) state_manager.update_agent_state(decision_made=1)
│   └─ e) agent.save_memory() → Zapisz 4 pliki JSON
│
├─ 5. _update_shared_memory() → (pusta metoda, przyszłość)
├─ 6. state_manager.end_cycle() → cycle_end_time, last_cycle_time
├─ 7. save_state() → runtime_state.json (w TEST_MODE: po kazdym cyklu)
└─ 8. time.sleep(0.1) w TEST_MODE, 1.0s w PRODUCTION
```

---

### 2.2. Pliki biorące udział w jednym cyklu

| **Krok** | **Plik odpowiedzialny** | **Metoda** | **Operacja** |
|----------|--------------------------|------------|--------------|
| Inicjalizacja | runtime_controller.py | initialize() | Tworzy agenty |
| Inicjalizacja | agent_manager.py | create_agent() | Fabryka agentów |
| Inicjalizacja | agent_runtime.py | __init__() | Inicjalizuje pamięć |
| Załadowanie pamięci | agent_memory_store.py | load_from_disk() | JSON → Obiekty |
| Zbieranie danych | runtime_controller.py | _collect_current_data() | v2,v3,v4,external |
| Analiza | agent_runtime.py | _analyze_data() | quality_scores, trust_scores |
| Decyzja | agent_runtime.py | _make_decision() | choice, confidence, strategy |
| Zapis doświadczenia | agent_runtime.py | _save_experience() | HistoryMemoryEntry |
| Aktualizacja historii | agent_runtime.py | _update_history() | state_manager.update |
| Zapis pamięci | agent_memory_store.py | save_to_disk() | Obiekty → JSON |
| Aktualizacja stanu | state_manager.py | update_agent_state() | AgentState update |
| Zapis stanu systemu | state_manager.py | save_state() | runtime_state.json |

---

### 2.3. Dane wejściowe i wyjściowe agenta

**Dane wejściowe dla jednego agenta:**
```python
collector_data = {
    "v2": {"world_state": {...}, "events": [...], "timestamp": "..."},
    "v3": {"knowledge_base": {...}, "insights": [...], "timestamp": "..."},
    "v4": {"agents_data": {...}, "relationships": {...}, "timestamp": "..."},
    "external": {"external_inputs": {...}, "market_data": {...}, "timestamp": "..."}
}

world_context = {
    "timestamp": "2026-07-31T12:00:00",
    "cycle_count": 5,
    "runtime_status": "running",
    "active_agents": 6
}

# Pamięć z plików JSON:
agent_memory = {
    "personality": PersonalityMemoryEntry(risk=0.5, analysis=0.8, ...),
    "strategies": [StrategyMemoryEntry(strategy_name="analytical", times_used=5, ...)],
    "history": [HistoryMemoryEntry(event_type="decision_made", confidence=0.87, ...)]
}
```

**Dane wyjściowe z jednego agenta:**
```python
result = {
    "agent_id": "01",
    "cycle_count": 5,
    "decision": {
        "decision_id": "dec_01_20260731120000",
        "choice": "high_confidence_choice",
        "confidence": 0.87,
        "strategy": "analytical",
        "reasoning": "Analytical decision based on confidence 0.87",
        "advanced": {"data_quality": 0.85, "patterns_detected": 1}
    },
    "analysis": {
        "sources_used": ["v2","v3","v4","external"],
        "quality_scores": {"v2":0.95, "v3":0.90, "v4":0.85, "external":0.60},
        "trust_scores": {"v2":0.8, "v3":0.8, "v4":0.8, "external":0.6},
        "overall_confidence": 0.87
    },
    "success": True
}

# Nowe wpisy w pamięci:
new_entries = [
    HistoryMemoryEntry(
        entry_id="hist_01_20260731120000",
        event_type="decision_made",
        related_decision_id="dec_01_20260731120000",
        confidence=0.87
    ),
    BehaviorMemoryEntry(
        entry_id="beh_01_20260731120000",
        behavior_type="decision_making",
        action="analytical",
        data_sources=["v2","v3","v4","external"],
        usage_count=1
    )
]

# Zaktualizowane pliki:
# ✅ memory/agents/agent_01/personality.json (jeśli zmiany)
# ✅ memory/agents/agent_01/behavior.json (+1 wpis)
# ✅ memory/agents/agent_01/strategy.json (zaktualizowane liczniki)
# ✅ memory/agents/agent_01/history.json (+1 wpis)
```

---

## 🏃 CZĘŚĆ 3: MODEL 10 CYKLI TESTOWYCH

---

### 3.1. Schemat wykonywania

```
TEST MODE: test_mode=True, test_cycles=10, auto_save=True, sleep=0.1s

CKLE 1: Agent_01(It#1) → Agent_02(It#2) → Agent_03(It#3) → Agent_04(It#4) → Agent_05(It#5) → Agent_06(It#6)
          save_state() → runtime_state.json (cycle_count=1, total_iterations=6)

CYCLE 2: Agent_01(It#7)  → Agent_02(It#8)  → Agent_03(It#9)  → Agent_04(It#10) → Agent_05(It#11) → Agent_06(It#12)
          save_state() → runtime_state.json (cycle_count=2, total_iterations=12)

...

CYCLE 10: Agent_01(It#55) → Agent_02(It#56) → Agent_03(It#57) → Agent_04(It#58) → Agent_05(It#59) → Agent_06(It#60)
           save_state() → runtime_state.json (cycle_count=10, total_iterations=60)

FINAL: runtime_state.stop_time = "...", status = "shutdown", SSI SHUTDOWN
```

---

### 3.2. Podsumowanie 10 cykli

| **Metryka** | **Wartość** | **Obliczenia** |
|-------------|-------------|----------------|
| Liczba cykli | 10 | test_cycles |
| Liczba agentów | 6 | agent_count |
| Liczba iteracji | 60 | cycles × agents |
| Iteracje na agenta | 10 | cycles |
| Decyzje podjęte | 60 | 1 na iterację |
| Wpisy behavior | 60 | 1 na iterację |
| Wpisy history | 60 | 1 na iterację |
| Pliki pamięci | 24 | 4 pliki × 6 agentów |
| Czas trwania | ~1.2s | 10 cykli × 0.1s sleep |

---

### 3.3. Typy agentów w TEST MODE

| **Agent** | **Typ (AgentType)** | **Osobowość** | **Domyślna strategia** |
|-----------|---------------------|---------------|-----------------------|
| Agent_01 | ANALYTICAL | risk=0.3, analysis=0.9, creativity=0.4 | analytical |
| Agent_02 | CREATIVE | risk=0.7, analysis=0.5, creativity=0.9 | analytical |
| Agent_03 | CONSERVATIVE | risk=0.2, analysis=0.8, creativity=0.3 | analytical |
| Agent_04 | RISK_TAKER | risk=0.9, analysis=0.4, creativity=0.6 | analytical |
| Agent_05 | BALANCED | risk=0.5, analysis=0.7, creativity=0.5 | analytical |
| Agent_06 | EXPLORER | risk=0.6, analysis=0.6, creativity=0.8 | analytical |

---

## 💾 CZĘŚĆ 4: STRUKTURA PAMIĘCI

---

### 4.1. Aktualna struktura (Sprint 11.5 - DZIAŁA)

```
SSI/
└── memory/
    └── agents/
        ├── agent_01/
        │   ├── personality.json    # Cechy osobowości, zaufanie
        │   ├── behavior.json      # Zachowania, akcje, skuteczność
        │   ├── strategy.json      # Strategie, historia użycia
        │   └── history.json       # Historia zdarzeń i decyzji
        ├── agent_02/
        │   └── (analogiczne)
        ├── agent_03/
        │   └── (analogiczne)
        ├── agent_04/
        │   └── (analogiczne)
        ├── agent_05/
        │   └── (analogiczne)
        └── agent_06/
            └── (analogiczne)
```

---

### 4.2. Typy pamięci i ich rola

| **Typ (MemoryType)** | **Plik** | **Klasa (dataclass)** | **Przeznaczenie** | **Częstotliwość aktualizacji** |
|----------------------|----------|------------------------|-------------------|--------------------------------|
| PERSONALITY | personality.json | PersonalityMemoryEntry | Cechy osobowości, wagi, zaufanie | Rzadko (zmiana konfiguracji) |
| BEHAVIOR | behavior.json | BehaviorMemoryEntry | Historia zachowań, akcje, skuteczność | Co cykl (nowy wpis) |
| STRATEGY | strategy.json | StrategyMemoryEntry | Strategie, statystyki użycia | Co cykl (aktualizacja liczników) |
| HISTORY | history.json | HistoryMemoryEntry | Historia zdarzeń, decyzji | Co cykl (nowy wpis) |
| RELATIONSHIP | relationship.json | RelationshipMemoryEntry | Relacje między agentami | Przyszłość (Sprint 13) |
| PROMPT | prompt.json | PromptMemoryEntry | Prompty dla LLM | Przyszłość (Sprint 15) |

---

### 4.3. Przyszła struktura (Sprint 12+ - PLAN)

```
SSI/
├── memory/
│   │
│   ├── agents/                      # ✅ AKTUALNIE
│   │   └── agent_01/ ... agent_06/  # Indywidualna pamięć agentów
│   │
│   ├── collective/                   # 🟡 SPRINT 12 - Collective Memory Layer
│   │   ├── global_memory.json        # Globalna wiedza systemu
│   │   ├── strategy_memory.json      # Wspólne strategie zespołowe
│   │   ├── knowledge_memory.json      # Zunifikowana baza wiedzy
│   │   └── interaction_memory.json    # Historia interakcji agentów
│   │
│   └── long_term/                    # 🟡 SPRINT 12 - Long Term Memory System
│       ├── events_history.json       # Archiwum zdarzeń systemowych
│       ├── agents_evolution.json     # Ewolucja parametrów agentów
│       ├── decisions_archive.json    # Archiwum wszystkich decyzji
│       ├── errors_log.json           # Logi błędów i nauczone lekcje
│       └── patterns_library.json     # Biblioteka wykrytych wzorców
│
└── v5/
    ├── llm/                          # 🟡 SPRINT 15 - LLM Integration
    │   └── language_model/
    │       ├── agent_context/         # Kontekst indywidualny agentów
    │       │   ├── agent_01_context.json
    │       │   └── ...
    │       ├── collective_context/     # Kontekst zespołowy
    │       │   └── team_context.json
    │       └── prompt_memory/          # Pamięć promptów
    │           ├── system_prompts.json
    │           └── ...
    │
    └── core/                         # 🟡 SPRINT 16 - Collective Intelligence
        └── collective_intelligence/
            ├── knowledge_graph.json    # Graf wiedzy zespołu
            └── team_decisions.json      # Decyzje zespołowe
```

---

### 4.4. Opis plików przyszłościowych

| **Katalog** | **Plik** | **Cel** | **Przewidywana zawartość** |
|-------------|----------|---------|---------------------------|
| collective | global_memory.json | Wspólna wiedza | Agregacja wiedzy z V2,V3,V4, external |
| collective | strategy_memory.json | Wspólne strategie | Strategie zespołowe, plany współpracy |
| collective | knowledge_memory.json | Baza wiedzy | Zunifikowana wiedza, indeksowana |
| collective | interaction_memory.json | Historia interakcji | Komunikacja agent-agent, współpraca, konflikty |
| long_term | events_history.json | Archiwum zdarzeń | Wszystkie zdarzenia z timestampem i kontekstem |
| long_term | agents_evolution.json | Ewolucja agentów | Historia zmian parametrów i zachowań |
| long_term | decisions_archive.json | Archiwum decyzji | Wszystkie decyzje z wynikami i ocenami |
| long_term | errors_log.json | Logi błędów | Błędy z kontekstem i nauczonymi lekcjami |
| long_term | patterns_library.json | Biblioteka wzorców | Wykryte wzorce zachowań i trendy |

---
---

## Kontynuacja w kolejnym message (Część 5-8)...
