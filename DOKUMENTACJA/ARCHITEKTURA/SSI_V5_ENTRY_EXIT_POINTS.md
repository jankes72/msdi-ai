# SSI V5 - PUNKTWEJŚCIA I WYJŚCIA

**Data:** 2026-08-01  
**Sprint:** 11.5 → 12+ (Planowanie)  
**Status:** Dokumentacja projektowa - Wersja 1.0.0  
**Autor:** Główny Architekt SSI V5  

---

## 📋 SPIS TREŚCI

1. [Główne punkty Wejścia](#1-główne-punkty-wejścia)
2. [Główne Punkty Wyjściowe](#2-główne-punkty-wyjściowe)
3. [Wejścia Specjalne (Programista)](#3-wejścia-specjalne-programista)
4. [Diagram Wejścia/Wyjścia](#4-diagram-wejściawyjścia)

---

## 1. GŁÓWNE PUNKTWEJŚCIA

### 1.1. Tabela Punktów Wejścia

| **Punkt Wejścia** | **Plik** | **Typ** | **Opis** | **Parametry** | **Zwracane** | **Status** |
|-------------------|----------|---------|----------|---------------|--------------|------------|
| Production | start_ssi.py | Główne | Uruchomienie systemu PRODUCTION | runtime_config, cycle_duration_hours=5 | RuntimeController | ✅ Sprint 11.5 |
| Test Mode | start_ssi_test.py | Testowe | Uruchomienie systemu TEST | test_cycles=10, auto_save=True | RuntimeController, TestSummary | ✅ Sprint 11.5 |
| RuntimeController | runtime_controller.py | Sterowanie | Kontroler głównego cyklu | config: RuntimeConfig | runtime_state.json, agents[] | ✅ Sprint 11.5 |
| AgentRuntime | agent_runtime.py | Agenci | Wykonanie cyklu agenta | config: AgentConfig, collector_data, world_context | decision, analysis, success | ✅ Sprint 11.5 |

### 1.2. Szczegóły Punktów Wejścia

#### start_ssi.py (Production)
```python
# Główne wejście dla trybu produkcyjnego
# Uruchamiany: python start_ssi.py

def main():
    config = create_default_runtime_config()
    # RuntimeConfig(mode=PRODUCTION, test_mode=False, cycle_duration_hours=5)
    
    controller = create_runtime_controller(config)
    controller.initialize()
    controller.run_loop()  # Ciągła pętla: max_cycles=∞, sleep=1.0s
    controller.save_state()
    
# 6 agentów w kolejności: ["01","02","03","04","05","06"]
# Czas trwania: 5 godzin (konfiguracja domyślna)
```

**Parametry konfiguracji:**
- `mode`: PRODUCTION
- `test_mode`: False
- `cycle_duration_hours`: 5
- `auto_save`: True (co 10 cykli)
- `sleep_between_cycles`: 1.0 (sekundy)

#### start_ssi_test.py (Test Mode)
```python
# Wejście dla trybu testowego
# Uruchamiany: python start_ssi_test.py

def main():
    config = create_default_runtime_config()
    # RuntimeConfig(mode=TEST, test_mode=True, test_cycles=10)
    
    controller = create_runtime_controller(config)
    controller.initialize()
    controller.run_loop()  # 10 cykli, sleep=0.1s
    print_test_summary()  # Podsumowanie 60 iteracji
    controller.save_state()
    
# 6 agentów × 10 cykli = 60 iteracji
# Czas trwania: ~1.2s (10 cykli × 0.1s sleep + przetwarzanie)
```

**Parametry konfiguracji:**
- `mode`: TEST
- `test_mode`: True
- `test_cycles`: 10
- `auto_save`: True (po każdym cyklu)
- `sleep_between_cycles`: 0.1 (sekundy)

### 1.3. Inicjalizacja RuntimeController

```
RuntimeController.initialize():
├─ config_manager = RuntimeConfigManager(config)
│  └─ Zarządzanie konfiguracją runtime
├─ state_manager.initialize()
│  └─ Tworzy RuntimeState, AgentState×6
├─ scheduler.initialize()
│  └─ Inicjalizacja schedulera zadań
├─ _initialize_agents()
│  └─ agent_manager.create_agent_manager()
│      └─ FOR i IN 1..6: create_agent(config) → AgentRuntime()
└─ _initialize_collectors()
   └─ Tworzy: V2, V3, V4, External collectors
```

### 1.4. Cykl Agenta (AgentRuntime.run_cycle)

```
AgentRuntime.run_cycle(collector_data, world_context, cycle_count):
├─ Step 1: _analyze_data()
│  └─ Analiza danych z V2, V3, V4, External
│  └─ Zwraca: analysis {quality_scores, trust_scores, changes, patterns, anomalies}
├─ Step 2: _make_decision()
│  └─ Decyzja na podstawie analizy i pamięci agenta
│  └─ Zwraca: decision {choice, confidence, strategy, reasoning}
├─ Step 3: _save_experience()
│  └─ Zapis doświadczenia do pamięci
│  └─ Dodaje: HistoryMemoryEntry do memory_store
└─ Step 4: _update_history()
   └─ Aktualizacja stanu agenta
   └─ state_manager.update()
```

---

## 2. GŁÓWNE PUNKTWYJŚCIA

### 2.1. Tabela Punktów Wyjściowych

| **Punkt Wyjściowy** | **Plik** | **Typ** | **Opis** | **Dane** | **Format** | **Status** |
|---------------------|----------|---------|----------|----------|------------|------------|
| Runtime State | state_manager.py | Stan systemu | Aktualny stan runtime | RuntimeState | runtime_state.json | ✅ Sprint 11.5 |
| Agent Memory | agent_memory_store.py | Pamięć agentów | Pamięć indywidualna | PersonalityEntry, BehaviorEntry, StrategyEntry, HistoryEntry | 4x JSON per agent | ✅ Sprint 11.5 |
| System Memory | long_term_memory.py (FUTURE) | Pamięć systemowa | Pamięć długoterminowa | EventsHistory, AgentsEvolution, DecisionsArchive | JSON files | 🟡 Sprint 12 |
| Collective Memory | collective_memory.py (FUTURE) | Pamięć zbiorowa | Wspólna wiedza | GlobalMemory, StrategyMemory, KnowledgeMemory, InteractionMemory | JSON files | 🟡 Sprint 12 |

### 2.2. Szczegóły Punktów Wyjściowych

#### Runtime State (runtime_state.json)
**Plik:** state_manager.py  
**Format:** JSON  
**Aktualizacja:** Co 10 cykli (PRODUCTION) / Co cykl (TEST)  
**Zawartość:**

```json
{
  "RuntimeName": "SSI_V5_Runtime",
  "version": "1.0.0",
  "status": "running",
  "start_time": "2026-08-01T12:00:00",
  "stop_time": null,
  "cycle_count": 15,
  "total_cycles": 15,
  "current_test_cycle": null,
  "last_agent_id": "06",
  "last_save_time": "2026-08-01T12:15:00",
  "test_mode": false,
  "metadata": {
    "total_iterations": 90,
    "active_agents": 6,
    "average_cycle_time_ms": 45
  },
  "agents": {
    "01": {"status": "active", "decisions_made": 15, "success_rate": 0.87},
    "02": {"status": "active", "decisions_made": 15, "success_rate": 0.92},
    "03": {"status": "active", "decisions_made": 15, "success_rate": 0.78},
    "04": {"status": "active", "decisions_made": 15, "success_rate": 0.81},
    "05": {"status": "active", "decisions_made": 15, "success_rate": 0.89},
    "06": {"status": "active", "decisions_made": 15, "success_rate": 0.84}
  }
}
```

#### Agent Memory Files
**Lokalizacja:** SSI/memory/agents/agent_XX/  
**Format:** JSON (serializowane dataclass)  
**Aktualizacja:** Co cykl  
**Pliki:**

- `personality.json` - PersonalityMemoryEntry
- `behavior.json` - BehaviorMemoryEntry
- `strategy.json` - StrategyMemoryEntry
- `history.json` - HistoryMemoryEntry

**Przykładowa zawartość (history.json):**
```json
{
  "memory_type": "HISTORY",
  "entries": [
    {
      "entry_id": "hist_01_20260801120000",
      "agent_id": "01",
      "timestamp": "2026-08-01T12:00:00",
      "cycle_count": 1,
      "event_type": "decision_made",
      "related_decision_id": "dec_01_20260801120000",
      "choice": "high_confidence_choice",
      "confidence": 0.87,
      "strategy": "analytical",
      "sources_used": ["v2", "v3", "v4"],
      "outcome": "success"
    }
  ]
}
```

#### Test Summary (TEST MODE)
**Plik:** start_ssi_test.py  
**Format:** Console output + JSON  
**Generowanie:** Po zakończeniu testu  

```json
{
  "test_summary": {
    "start_time": "2026-08-01T12:00:00",
    "end_time": "2026-08-01T12:00:01",
    "test_mode": true,
    "test_cycles": 10,
    "total_iterations": 60,
    "average_iteration_time_ms": 18,
    "agents": {
      "01": {"decisions_made": 10, "success_rate": 0.80, "average_confidence": 0.83},
      "02": {"decisions_made": 10, "success_rate": 0.90, "average_confidence": 0.88},
      "03": {"decisions_made": 10, "success_rate": 0.70, "average_confidence": 0.75},
      "04": {"decisions_made": 10, "success_rate": 0.85, "average_confidence": 0.82},
      "05": {"decisions_made": 10, "success_rate": 0.95, "average_confidence": 0.91},
      "06": {"decisions_made": 10, "success_rate": 0.75, "average_confidence": 0.78}
    },
    "overall": {
      "success_rate": 0.82,
      "average_confidence": 0.83,
      "best_performer": "05",
      "worst_performer": "03"
    }
  }
}
```

---

## 3. WEJŚCIA SPECJALNE (PROGRAMISTA)

### 3.1. Tabela Wejść Programisty

| **Wejście** | **Lokalizacja** | **Opis** | **Dostępne Funkcje** | **Status** | **Sprint** |
|-------------|----------------|----------|----------------------|------------|------------|
| Developer API | runtime_config.py | Konfiguracja programisty | Ustawianie parametrów, flagi feature | ✅ Aktywny | 11.5 |
| Test Protocol | start_ssi_test.py | Testy programisty | Wymuszenie testów, eksperymenty | ✅ Aktywny | 11.5 |
| Lab Environment | SSI/v5/lab/ (FUTURE) | Sandbox | Tworzenie zadań, inicjowanie modeli | 🟡 Planowany | 13 |
| LLM Integration | SSI/v5/llm/ (FUTURE) | Integracja LLM | Konfiguracja modeli, prompty | 🟡 Planowany | 15 |

### 3.2. Developer API (runtime_config.py)

**Opis:** Interfejs do konfiguracji systemu przez programistę

**Dostępne funkcje:**
```python
# runtime_config.py

# Tworzenie konfiguracji
def create_default_runtime_config() -> RuntimeConfig:
    """Tworzy domyślną konfigurację"""
    return RuntimeConfig(
        mode=RuntimeMode.PRODUCTION,
        test_mode=False,
        cycle_duration_hours=5,
        auto_save=True,
        save_interval_cycles=10
    )

def create_test_runtime_config() -> RuntimeConfig:
    """Tworzy konfigurację testową"""
    return RuntimeConfig(
        mode=RuntimeMode.TEST,
        test_mode=True,
        test_cycles=10,
        auto_save=True,
        save_interval_cycles=1
    )

# Modyfikacja konfiguracji
def override_config_values(config: RuntimeConfig, overrides: dict) -> RuntimeConfig:
    """Nadpisanie wartości konfiguracyjnych"""
    for key, value in overrides.items():
        setattr(config, key, value)
    return config

# Feature Flags
def set_feature_flag(flag_name: str, enabled: bool) -> None:
    """Włączanie/wyłączanie feature flagów"""
    FEATURE_FLAGS[flag_name] = enabled

# Konfiguracja agentów
def create_custom_agent_config(agent_id: str, personality: dict) -> AgentConfig:
    """Tworzy indywidualną konfigurację agenta"""
    return AgentConfig(
        agent_id=agent_id,
        personality=PersonalityConfig(**personality),
        strategy=StrategyConfig(default_strategy="analytical"),
        memory=MemoryConfig(enabled_types=[MemoryType.PERSONALITY, ...])
    )
```

**Przykładowe Flag Feature:**
```python
# W runtime_config.py
FEATURE_FLAGS = {
    "ENABLE_COLLECTIVE_MEMORY": False,  # Sprint 12
    "ENABLE_LLM_ANALYSIS": False,      # Sprint 15
    "ENABLE_LONG_TERM_MEMORY": False,  # Sprint 12
    "ENABLE_BEHAVIORAL_CALIBRATION": False,  # Sprint 14
    "ENABLE_COMMUNICATION_ANALYZER": False,  # Sprint 13
    "DEBUG_MODE": False,
    "VERBOSE_LOGGING": False
}
```

### 3.3. Test Protocol (start_ssi_test.py)

**Opis:** Interfejs do uruchamiania testów i eksperymentów

**Dostępne funkcje:**
```python
# start_ssi_test.py

def run_experiment(experiment_config: dict) -> ExperimentResult:
    """Uruchomienie eksperymentu z konkretną konfiguracją"""
    # 1. Utworzenie runtime z custom config
    # 2. Wykonanie określonych cykli
    # 3. Zbieranie wyników
    # 4. Zwrot strukturyzowanych danych
    return ExperimentResult(metrics={...}, decisions=[...])

def run_comparison_test(config_a: RuntimeConfig, config_b: RuntimeConfig) -> ComparisonResult:
    """Porównanie dwóch konfiguracji"""
    # Porównanie wydajności, jakości decyzji, etc.
    return ComparisonResult(differences={...}, winner="A/B")

def run_stress_test(cycle_count: int = 100) -> StressTestResult:
    """Test wydajnościowy z dużą ilością cykli"""
    return StressTestResult(performance_metrics={...})

def print_test_summary() -> dict:
    """Podsumowanie testu (wykonywane automatycznie)"""
    return get_test_metrics()
```

### 3.4. Lab Environment (FUTURE - Sprint 13)

**Lokalizacja:** SSI/v5/lab/  
**Status:** 🟡 Planowany

**Przewidywane pliki:**
- `sandbox.py` - Bezpieczne środowisko testowe
- `experiment_runner.py` - Uruchamianie eksperymentów
- `results_analyzer.py` - Analiza wyników
- `strategy_optimizer.py` - Optymalizacja strategii

**Funkcjonalności:**
- Izolowane środowisko testowe dla agentów
- Definiowanie i uruchamianie eksperymentów
- Automatyczna analiza wyników
- Optymalizacja strategii na podstawie wyników
- Integracja z Long Term Memory

### 3.5. LLM Integration (FUTURE - Sprint 15)

**Lokalizacja:** SSI/v5/llm/  
**Status:** 🟡 Planowany

**Przewidywane pliki:**
- `llm_client.py` - Klient API LLM
- `llm_decision_layer.py` - Warstwa analizy LLM
- `prompt_builder.py` - Budowanie promptów
- `llm_config.py` - Konfiguracja LLM

**Funkcjonalności:**
- Konfiguracja różnych modeli językowych
- Budowanie i optymalizacja promptów
- Analiza decyzji agentów przez LLM
- Zapis insightów LLM do pamięci

---

## 4. DIAGRAM WEJŚCIA/WYJŚCIA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SSI V5 - WEJŚCIA I WYJŚCIA                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────┐     ┌─────────────────────────┐               │
│  │      PROGRAMISTA          │     │      SYSTEM SSI V5       │               │
│  │                         │     │                         │               │
│  │  ┌───────────────────┐  │     │  ┌───────────────────┐  │               │
│  │  │ start_ssi.py       │  │     │  │ RuntimeController │  │               │
│  │  │ start_ssi_test.py  │─────►│  │    .initialize()   │  │               │
│  │  │                   │  │     │  │    .run_loop()     │  │               │
│  │  │ DEVELOPER API     │  │     │  └─────────┬─────────┘  │               │
│  │  │ ↓                 │  │     │            │            │               │
│  │  │ runtime_config.py │  │     │  ┌─────────▼─────────┐  │               │
│  │  │/env variables     │  │     │  │   _initialize_    │  │               │
│  │  │ feature flags     │  │     │  │   agents()       │  │               │
│  │  └───────────────────┘  │     │  │   _initialize_    │  │               │
│  │                         │     │  │   collectors()   │  │               │
│  └─────────────────────────┘     │  └─────────┬─────────┘  │               │
│                                      │            │            │               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │              RUNTIME LOOP                                               │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │  FOR agent IN agents:                                           │  │ │
│  │  │    agent.load_memory()   ◄──────────────────┐                   │  │ │
│  │  │    agent.run_cycle()     ◄──────────────────┼──input            │  │ │
│  │  │    agent.save_memory()   ◄──────────────────┼                   │  │ │
│  │  │                                                           │  │ │
│  │  │  _update_shared_memory()  ◄─── FUTURE (Sprint 12)             │  │ │
│  │  │  save_state() ────────────► runtime_state.json                    │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  WYJŚCIA:                                                                     │
│  ┌─────────────────────────┐                                               │
│  │  1. runtime_state.json │  ◄──── RuntimeController.save_state()        │
│  │  2. 4x JSON per agent   │  ◄──── AgentMemoryStore.save_to_disk()       │
│  │  3. FUTURE:              │                                               │
│  │     collective/*.json    │  ◄──── CollectiveMemoryManager (Sprint12)   │
│  │     long_term/*.json     │  ◄──── LongTermMemoryManager (Sprint 12)    │
│  │     language_model/*.json│  ◄──── LLMDecisionLayer (Sprint 15)         │
│  └─────────────────────────┘                                               │
│                                                                             │
│  ┌─────────────────────────┐                                               │
│  │     TEST MODE OUTPUT     │                                               │
│  │  print_test_summary()    │  ◄──── Podsumowanie 60 iteracji            │
│  └─────────────────────────┘                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** Gotowy do przeglądu