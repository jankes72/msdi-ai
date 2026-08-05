# SSI V5 - Runtime Architecture Document
# ETAP 5.3: Complete Runtime System with Cycle Awareness

**Data:** 2026-08-04  
**Wersja:** 1.0.0  
**Status:** ZAKONCZONY  
**Autor:** SSI V5 System / Mistral Vibe

---

## 📋 SPIS TREŚCI

1. [Podsumowanie Executive](#1-podsumowanie-executive)
2. [Przegląd Architektury Runtime](#2-przegląd-architektury-runtime)
3. [Świadomość Cyklu (ETAP 5.3.1)](#3-świadomość-cyklu-etap-531)
4. [Kontekst Wykonania (ETAP 5.3.2)](#4-kontekst-wykonania-etap-532)
5. [Pamięć Strategii (ETAP 5.3.3)](#5-pamięć-strategii-etap-533)
6. [Symulacja Cyklu 24H (ETAP 5.3.4)](#6-symulacja-cyklu-24h-etap-534)
7. [Przepływ Startowy Systemu](#7-przepływ-startowy-systemu)
8. [Lifecycle Cyklu](#8-lifecycle-cyklu)
9. [Fazy Systemu](#9-fazy-systemu)
10. [Przepływ ExecutionContext](#10-przepływ-executioncontext)
11. [Przepływ Pamięci Strategii](#11-przepływ-pamięci-strategii)
12. [Tryb Produkcyjny vs Symulacyjny](#12-tryb-produkcyjny-vs-symulacyjny)
13. [Nazewnictwo Modułów](#13-nazewnictwo-modułów)
14. [Integracja z Istniejącym Systemem](#14-integracja-z-istniejącym-systemem)
15. [Dokumentacja Powiązana](#15-dokumentacja-powiązana)

---

## 1. PODSUMOWANIE EXECUTIVE

### Status ETAP 5.3
**ZAKOŃCZONY** - Wszystkie podetapy zaimplementowane i udokumentowane.

| ETAP | Nazwa | Status | Testy | Raport |
|------|-------|--------|-------|--------|
| 5.3.1 | Cycle Controller | ✅ | 40/40 PASS | SSI_V5_CYCLE_CONTROLLER_IMPLEMENTATION_REPORT.md |
| 5.3.2 | Execution Context Delivery | ✅ | - | Zintegrowany |
| 5.3.3 | Strategy Persistence Memory | ✅ | 10/10 PASS | SSI_V5_STRATEGY_PERSISTENCE_MEMORY_REPORT.md |
| 5.3.4 | Simulation Cycle | ✅ | 15/15 PASS | SSI_V5_SIMULATION_CYCLE_REPORT.md |
| 5.3.5 | Documentation Alignment | ✅ | - | **SSI_V5_RUNTIME_ALIGNMENT_REPORT.md** |

**Łącznie:** 65/65 testów PASS

### Główne Dokumenty
- **SSI_V5_RUNTIME_ARCHITECTURE.md** - Ten dokument (architektura)
- **SSI_V5_RUNTIME_ALIGNMENT_REPORT.md** - Raport końcowy ETAP 5.3.5

---

## 2. PRZEGLĄD ARCHITEKTURY RUNTIME

### Hierarchia Systemu SSI V5 Runtime

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SSI V5 RUNTIME SYSTEM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     ZEWNĘTRZNY ZEGAR (V1)                           │   │
│  │              (uruchamianieModulow.py / start_ssi.py)                  │   │
│  │                         ⏰ NIE ZMIENIONY ⏰                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                           │
│                                   ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                 SSI V5 RUNTIME CONTROLLER                          │   │
│  │              (SSI/v5/runtime/runtime_controller.py)                  │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │  CycleController (ETAP 5.3.1)                              │  │   │
│  │  │  - detect_current_phase()                                  │  │   │
│  │  │  - get_execution_context()                                │  │   │
│  │  │  - save_cycle_state() / resume_from_state()               │  │   │
│  │  │  - PhaseDetector with priority: RESULTS > WORLD > DB > ODDS │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │  LLM Queue Manager (FAZA 1)                              │  │   │
│  │  │  - HardwareConstraints, ModelLimits                       │  │   │
│  │  │  - ModelMemoryStore, TrainingMemory                       │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │  Teacher Engine (FAZA 1)                                  │  │   │
│  │  │  - CognitiveTeacher, MemoryManager                        │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                           │
│                                   ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    PIPELINE                                   │   │
│  │              (SSI_V5/core/pipeline.py)                            │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │   │
│  │  │  World Engine   │  │  Modeling Layer │  │  Teacher Layer  │    │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘    │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │   │
│  │  │ Agent Runtime   │  │ Collective      │  │ Trust/Personality│   │   │
│  │  │ Manager         │  │ Manager        │  │ Manager         │    │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                           │
│                                   ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    AGENTS (01-06)                               │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ ┌─────┐ │   │
│  │  │ Agent 01│ │ Agent 02│ │ Agent 03│ │ Agent 04│ │ Agent 05│ │06 │ │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └────────┘ └─────┘ │   │
│  │                                                                     │   │
│  │  Each receives: ExecutionContext (phase, goal, actions, memory)   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                           │
│                                   ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    MEMORY LAYER                                 │   │
│  │  ┌─────────────────────────────────────────────────────────────┐ │   │
│  │  │  StrategyMemoryManager (ETAP 5.3.3)                         │ │   │
│  │  │  - ranking_position, confidence_score, tested_variants     │ │   │
│  │  │  - next_evaluation, status                                │ │   │
│  │  │  - update_performance(), update_ranking()                   │ │   │
│  │  └─────────────────────────────────────────────────────────────┘ │   │
│  │  ┌─────────────────────────────────────────────────────────────┐ │   │
│  │  │  ModelMemoryStore (FAZA 1)                                  │ │   │
│  │  │  - TrainingMemory, ObservationMemory, BehaviorMemory        │ │   │
│  │  └─────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. ŚWIADOMOŚĆ CYKLU (ETAP 5.3.1)

### Problem Rozwiązany
System SSI V5 nie miał świadomości, w jakiej **fazie cyklu pracy** aktualnie się znajduje. Wszystkie akcje były wykonywane sekwencyjnie bez kontekstu czasowego i stanu danych.

### Rozwiązanie: Cycle Controller

**Lokalizacja:** `SSI/v5/runtime/cycle_controller.py`

**Odpowiedzialność:**
- Wykrywanie aktualnej fazy cyklu na podstawie stanu danych (NIE czasu!)
- Zarządzanie przejściami między fazami
- Dostarczanie kontekstu wykonania dla agentów
- Zapis i wznowienie stanu cyklu

### Priorytety Detekcji Faz

```
1. RESULTS_STATE      (new_results_available > results_processed)
   ↓
2. WORLD_STATE        (world_status, world_is_ready)
   ↓
3. DATABASE_STATE     (database_status, database_timestamp)
   ↓
4. ODDS_STATE         (odds_available, odds_timestamp)
   ↓
5. TIME               (jako ostatnia wskazówka)
```

### Fazy Systemu

| Faza | Warunek | Typowy Moment | Cel |
|------|---------|---------------|-----|
| `RESULT_ANALYSIS` | `new_results_available && !results_processed` | ~02:07 | Analiza zakonczonych predykcji, porownanie kuponow, ocena strategii |
| `WORLD_PREPARATION` | `world_status != READY` | ~08:05 | Oczekiwanie na gotowosc swiata |
| `PREDICTION_WINDOW` | `world_is_ready && odds_available` | 08:30-12:59 | Generowanie predykcji, Exact Score Engine |
| `STRATEGY_EVOLUTION` | `prediction_cycle_completed` | ~15:07 | Eksperymenty, testowanie wariantow strategii |
| `OPTIMIZATION` | Czasowy trigger | ~21:07 | Koncowe korekty systemu |
| `WAITING` | Brak aktywnych warunkow | Pozostale czasy | Oczekiwanie na nastepna faze |

### Komponenty

#### CyclePhase (Enum)
```python
class CyclePhase(Enum):
    UNKNOWN = "unknown"
    RESULT_ANALYSIS = "result_analysis"
    WORLD_PREPARATION = "world_preparation"
    PREDICTION_WINDOW = "prediction_window"
    STRATEGY_EVOLUTION = "strategy_evolution"
    OPTIMIZATION = "optimization"
    WAITING = "waiting"
```

#### CycleState (dataclass)
- `cycle_id: str` - Identyfikator cyklu
- `current_phase: CyclePhase` - Aktualna faza
- `started_at: datetime` - Czas rozpoczęcia
- `completed_phases: List[str]` - Lista zakończonych faz
- `phase_transitions: List[Dict]` - Historia przejść
- `prediction_cycle_completed: bool` - Flaga zakończenia predykcji
- `world_generation_completed: bool` - Flaga zakończenia generacji świata

#### PhaseDetector
- `detect_phase(world_state, current_time) -> CyclePhase`
- Sprawdza w kolejności: RESULTS → WORLD → DATABASE → ODDS → TIME

#### CycleController
- `__init__(state_path, logger, clock=None)` - **clock** dodany w ETAP 5.3.4
- `detect_current_phase(world_state, current_time=None)`
- `transition_to_phase(new_phase)` - Wymusz przejście
- `get_execution_context() -> ExecutionContext`
- `save_cycle_state() / load_cycle_state()` - Persystencja
- `resume_from_state()` - Odzysk po restarcie

---

## 4. KONTEKST WYKONANIA (ETAP 5.3.2)

### Problem Rozwiązany
Agenci nie mieli informacji o tym, w jakim kontekście powinni działać. Każdy agent działał w izolacji bez znajomości aktualnej fazy cyklu.

### Rozwiązanie: ExecutionContext

**Lokalizacja:** `SSI/v5/runtime/cycle_controller.py` (rozwiązanie zintegrowane z CycleController)

**Odpowiedzialność:**
- Dostarczanie kontekstu działaniadla agentów
- Określenie dozwolonych i zakazanych akcji
- Określenie dostępnych pamieci

### Przekazywany Kontekst

Każdy agent otrzymuje:
```python
{
    "phase": "result_analysis|world_preparation|...",
    "goal": "evaluate_previous_predictions_and_update_rankings",
    "allowed_actions": ["load_predictions", "compare_with_results", ...],
    "forbidden_actions": ["number_generator", "bet", "trade"],
    "available_memory": ["prediction_history", "strategy_memory", ...],
    "priority": "high|medium|low",
    "parameters": {...}
}
```

### Mapowanie Faz do Kontekstów

| Faza | Cel | Dozwolone Akcje | Zakazane Akcje | Pamieci |
|------|-----|----------------|-----------------|---------|
| RESULT_ANALYSIS | Ocena poprzednich predykcji | load_predictions, compare_with_results, evaluate_strategies | number_generator, bet, trade, generate_world | prediction_history, strategy_memory, result_feedback |
| WORLD_PREPARATION | Oczekiwanie na swiat | check_world_status, monitor_database, validate_data | number_generator, bet, trade, generate_predictions | world_config, database_status |
| PREDICTION_WINDOW | Generowanie predykcji | load_world_data, run_exact_score_engine, rank_strategies | number_generator, bet, trade | world_database, market_data, odds_data |
| STRATEGY_EVOLUTION | Ewolucja strategii | test_strategy_variants, analize_behavior, update_ranking | number_generator, bet, trade, generate_world | prediction_history, performance_data |
| OPTIMIZATION | Optymalizacja | analyze_daily_results, optimize_parameters, cleanup | number_generator, bet, trade, generate_world | daily_performance, strategy_rankings |
| WAITING | Oczekiwanie | monitor_system, check_triggers | number_generator, bet, trade, generate_predictions | system_status |

### Przepływ ExecutionContext

```
SSIPipeline.run_cycle()
    ↓
CycleController.detect_current_phase(world_state)
    ↓
CycleController.get_execution_context()
    ↓
cycle_data["execution_context"]
    ↓
AgentRuntimeManager.receive_context()
    ↓
AgentContract.execution_context
    ↓
Agent memory/context
```

---

## 5. PAMIĘĆ STRATEGII (ETAP 5.3.3)

### Problem Rozwiązany
System SSI V5 nie zachowywał pamięci strategii między cyklami. Po zakończeniu cyklu wyniki strategii były tracone.

### Rozwiązanie: Strategy Persistence Memory

**Lokalizacja:** `SSI_V5/memory/strategy_memory.py`

**Odpowiedzialność:**
- Przechowywanie historii i ewolucji strategii
- Powiązanie z Strategy Laboratory
- Zapis i odczyt doświadczeń strategii
- Wersjonowanie strategii

### Rozszerzone Pola (ETAP 5.3.3)

**StrategyMemoryRecord:**
```python
# Nowe pola:
ranking_position: int = 0              # Pozycja w rankingu (niższa = lepsza)
confidence_score: float = 0.0         # Poziom pewności (0.0-1.0)
tested_variants: List[str] = []        # Lista testowanych wariantów
next_evaluation: bool = True           # Czy wymaga ponownej ewaluacji
status: str = "ACTIVE"                   # Status: ACTIVE, INACTIVE, ARCHIVED
```

**StrategyMemoryManager:**
- `update_ranking(strategy_id, position)` - Aktualizacja rankingu
- `add_tested_variant(strategy_id, variant_id)` - Dodanie wariantu
- `update_performance(strategy_id, cycle_data)` - Zapis wyniku
- `schedule_evaluation(strategy_id, required)` - Zaplanuj ewaluację
- `set_status(strategy_id, status)` - Zmień status
- `get_ranked_strategies(limit)` - Pobierz posortowane strategie
- `get_strategies_requireing_evaluation()` - Strategie do ewaluacji

### Przepływ Pamięci Strategii

```
Agent Execution
    ↓
Strategy Evaluation (w SSIPipeline)
    ↓
_record_agent_results_to_strategy_memory()
    ↓
StrategyMemoryManager.update_performance()
    ↓
StrategyMemoryManager.update_ranking()
    ↓
JSON Persistence (memory/strategy_memory/)
    ↓
Wznowienie po restarcie
```

### Integracja z Pipeline

W `SSI_V5/core/pipeline.py` (linia ~1961):
```python
def _record_agent_results_to_strategy_memory(
    self, agent_result: Dict[str, Any], cycle_id: str, 
    execution_context: Optional[ExecutionContext]) -> None:
    
    # Pobranie testów od agentów
    for agent_id, agent_decisions in decisions.items():
        strategy_id = f"agent_{agent_id}_strategy"
        
        # Obliczenie accuracy, profit_factor, success
        performance_data = {
            'cycle_id': cycle_id,
            'accuracy': accuracy,
            'profit_factor': 1.0,
            'success': accuracy > 0.5,
            # ... inne metryki
        }
        
        # Zapis do pamięci
        self.strategy_memory_manager.update_performance(strategy_id, performance_data)
        self.strategy_memory_manager.update_ranking(strategy_id, ranking_position)
```

---

## 6. SYMULACJA CYKLU 24H (ETAP 5.3.4)

### Problem Rozwiązany
Brak możliwości przetestowania pełnego cyklu 24H bez uruchamiania prawdziwego harmonogramu V1 (5 godzin).

### Rozwiązanie: SimulationClock + SimulatedWorldState

**Nowe komponenty:**

#### 1. SimulationClock (`SSI/v5/runtime/simulation_clock.py`)

**Odpowiedzialność:**
- TYLKO dostarczanie symulowanego czasu
- NIE zarządza fazami, NIE steruje pipeline, NIE uruchamia agentów

**Interfejs:**
```python
class SimulationClock:
    current_time: datetime
    start_time: datetime
    speed_factor: float = 1.0
    
    def set_time(new_time: datetime) -> None
    def advance_time(minutes: int) -> None
    def advance_seconds(seconds: int) -> None
    def get_current_time() -> datetime
    def set_speed_factor(speed: float) -> None
    def reset() -> None
```

**Użycie:**
```python
# Tworzenie zegara symulacyjnego
clock = SimulationClock()

# Ustawienie czasu na 02:07
clock.set_time(datetime(2026, 8, 4, 2, 7, 0))

# Uruchomienie detekcji fazy
controller = create_cycle_controller(clock=clock)
phase = controller.detect_current_phase(world_state)
# Zwraca: CyclePhase.RESULT_ANALYSIS
```

#### 2. SimulatedWorldState (`SSI/v5/runtime/simulation_world_state.py`)

**Odpowiedzialność:**
- Dostarczanie realistycznych stanów świata dla testów
- NIE wymuszanie faz - CycleController sam wykrywa fazę

**Generowanie stanów:**
```python
world_state = create_simulated_world_state_for_time(15, 7).to_dict()
# Zwraca: {
#   'new_results_available': False,
#   'results_processed': True,
#   'status': 'COMPLETED',
#   'is_ready': False,
#   'database_status': 'COMPLETED',
#   'odds_available': False,
#   'prediction_cycle_completed': True,
#   ...
# }
```

### Integracja z CycleController

**Priorytet czasu w detect_current_phase:**
```python
def detect_current_phase(self, world_state, current_time=None):
    # 1. current_time (jesli przekazany)
    # 2. self._clock.get_current_time() (jesli clock dostepny)
    # 3. datetime.now() (domyslnie)
    if current_time is None:
        if self._clock is not None:
            current_time = self._clock.get_current_time()
        else:
            current_time = datetime.now()
    
    return self._phase_detector.detect_phase(world_state, current_time)
```

### Integracja z SSIPipeline

**Konstruktor z parametrem clock:**
```python
def __init__(self, 
             mode: PipelineMode = PipelineMode.SINGLE,
             world_name: str = "SSI_V5_WORLD", 
             use_agent_runtime_manager: bool = True,
             clock = None):  # Opcjonalny zegar symulacyjny
    self._clock = clock
```

### Testy Symulacji

**Wyniki:** 15/15 testów PASS ✅

| Czas | Oczekiwana Faza | Wykryta Faza | Status |
|------|-----------------|--------------|--------|
| 02:07 | RESULT_ANALYSIS | result_analysis | ✅ PASS |
| 08:05 | WORLD_PREPARATION | world_preparation | ✅ PASS |
| 10:00 | PREDICTION_WINDOW | prediction_window | ✅ PASS |
| 12:00 | PREDICTION_WINDOW | prediction_window | ✅ PASS |
| 15:07 | STRATEGY_EVOLUTION | strategy_evolution | ✅ PASS |
| 21:07 | OPTIMIZATION | optimization | ✅ PASS |
| 22:00 | WAITING | waiting | ✅ PASS |

### Zarządzanie Symulacją Pełnego Dnia

```python
from SSI.v5.runtime import SimulationClock, create_cycle_controller
from SSI.v5.runtime.simulation_world_state import create_simulated_world_state_for_time

 clock = SimulationClock()
 controller = create_cycle_controller(clock=clock)

# Symulacja kluczowych momentów
for hour in range(24):
    for minute in [0, 7, 15, 30, 45]:
        clock.set_time(datetime(2026, 8, 4, hour, minute, 0))
        world_state = create_simulated_world_state_for_time(hour, minute).to_dict()
        phase = controller.detect_current_phase(world_state)
        # Zapis do logów symulacji...
```

---

## 7. PRZEPŁYW STARTOWY SYSTEMU

### Produkcyjny Launch Flow

```
V1 Scheduler (uruchamianieModulow.py)
    ↓
start_ssi.py (ProductionLauncher)
    ↓
SSIPipeline(mode=PipelineMode.PRODUCTION)
    ↓
SSIPipeline.initialize()
    ↓
- Inicjalizacja WorldEngine
- Inicjalizacja AgentRuntimeManager
- Inicjalizacja Teacher Layer
- Inicjalizacja CycleController (z domyślnym clock=None)
- Inicjalizacja StrategyMemoryManager
    ↓
SSIPipeline.run_cycle()
    ↓
- Detekcja fazy (CycleController)
- Generowanie świata (WorldEngine)
- Modelowanie (Modeling Layer)
- Analiza nauczyciela (Teacher Layer)
- Wykonanie agentów (AgentRuntimeManager)
- Konsensus kolektywny (Collective Manager)
- Aktualizacja zaufania (Trust Manager)
- Obserwacja wyników
- Aktualizacja pamięci (w tym StrategyMemory)
    ↓
Zapis stanu systemu
```

### Symulacyjny Launch Flow

```
SimulationClock()
    ↓
create_cycle_controller(clock=sim_clock)
    ↓ (opcjonalnie)
SSIPipeline(mode=PipelineMode.TEST, clock=sim_clock)
    ↓
create_simulated_world_state_for_time(hour, minute).to_dict()
    ↓
CycleController.detect_current_phase(world_state)
    ↓
CyclePhase (np. RESULT_ANALYSIS)
```

---

## 8. LIFECYCLE CYKLU

### Życie Cyklu

```
┌─────────────────────────────────────────────────────────────┐
│                        CYCLE LIFECYCLE                          │
├─────────────────────────────────────────────────────────────┤
│                                                                  │
│  START CYCLE         WAITING         RESULT_ANALYSIS           │
│        │                │                    │                  │
│        ▼                ▼                    ▼                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ initialize()│  │  Monitor    │  │ Analiza     │            │
│  │             │  │  stanu      │  │ wyników     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│        │                                   │                  │
│        ▼                                   ▼                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   WORLD PREPARATION                      │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │ │
│  │  │ Generuj    │→ │ Waliduj    │→ │ Gotowość   │       │ │
│  │  │ świat      │  │ dane       │  │ świata      │       │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                        │                                          │
│                        ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  PREDICTION WINDOW                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │ │
│  │  │ Modelowanie │→ │Predykcja   │→ │Ranking     │       │ │
│  │  │ danych     │  │ strategii  │  │ strategii  │       │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                        │                                          │
│                        ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                STRATEGY EVOLUTION                           │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │ │
│  │  │ Testuj     │→ │ Analizuj   │→ │ Ewoluuj    │       │ │
│  │  │ warianty   │  │ zachowanie │  │ strategie  │       │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                        │                                          │
│                        ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   OPTIMIZATION                              │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │ │
│  │  │ Korekty     │→ │ Optymal.   │→ │ Preparowanie│       │ │
│  │  │ parametrów  │  │ systemu    │  │ na feedback  │       │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                        │                                          │
│                        ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                     WAITING                                  │ │
│  │              Oczekiwanie na nowy cykl                       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────┘
```

### Typowy Przebieg 24H

| Godzina | Faza | Działanie |
|---------|------|-----------|
| 00:00-02:00 | WAITING | Oczekiwanie na nowe wyniki |
| 02:00-02:15 | RESULT_ANALYSIS | Analiza wyników z poprzedniego dnia |
| 02:15-08:05 | WORLD_PREPARATION | Generowanie świata sportowego |
| 08:05-12:59 | PREDICTION_WINDOW | Tworzenie predykcji i ranking strategii |
| 13:00-15:06 | STRATEGY_EVOLUTION | Testowanie wariantów strategii |
| 15:07-21:06 | STRATEGY_EVOLUTION/OPTIMIZATION | Ewolucja i optymalizacja |
| 21:07-23:59 | OPTIMIZATION/WAITING | Końcowe przygotowania |

---

## 9. FAZY SYSTEMU

### Definicje Faz

#### 1. RESULT_ANALYSIS
- **Warunek:** `new_results_available == True && results_processed == False`
- **Cel:** Analiza zakonczonych predykcji, porownanie kuponow, ocena strategii
- **Typowy moment:** ~02:07
- **ExecutionContext:**
  - Cel: `evaluate_previous_predictions_and_update_rankings`
  - Priorytet: HIGH
  - Dozwolone akcje: load_predictions, compare_with_results, evaluate_strategies
  - Zakazane akcje: number_generator, bet, trade, generate_world

#### 2. WORLD_PREPARATION
- **Warunek:** `world_status != READY` (np. GENERATING, BUILDING, LOADING)
- **Cel:** Oczekiwanie na gotowosc swiata
- **Typowy moment:** ~08:05
- **ExecutionContext:**
  - Cel: `wait_for_world_database_ready`
  - Priorytet: MEDIUM
  - Dozwolone akcje: check_world_status, monitor_database, validate_data
  - Zakazane akcje: number_generator, bet, trade, generate_predictions, run_strategy_evolution

#### 3. PREDICTION_WINDOW
- **Warunek:** `world_is_ready == True && odds_available == True`
- **Cel:** Generowanie predykcji, Exact Score Engine, Strategy Laboratory
- **Typowy moment:** 08:30-12:59
- **ExecutionContext:**
  - Cel: `generate_accurate_predictions_and_strategies`
  - Priorytet: HIGH
  - Dozwolone akcje: load_world_data, analyze_matches, run_exact_score_engine, generate_predictions
  - Zakazane akcje: number_generator, bet, trade

#### 4. STRATEGY_EVOLUTION
- **Warunek:** `prediction_cycle_completed == True` (lub czasowy: ~15:07)
- **Cel:** Eksperymenty, testowanie wariantow strategii, rozwoj agentow
- **Typowy moment:** ~15:07
- **ExecutionContext:**
  - Cel: `improve_strategies_through_experimentation`
  - Priory tet: HIGH
  - Dozwolone akcje: test_strategy_variants, analyze_behavior, update_strategy_ranking
  - Zakazane akcje: number_generator, bet, trade, generate_world

#### 5. OPTIMIZATION
- **Warunek:** Czasowy trigger (~21:07)
- **Cel:** Kontymalizacja koncowa, przygotowanie systemu do nastepego feedback cycle
- **Typowy moment:** ~21:07
- **ExecutionContext:**
  - Cel: `final_corrections_and_system_preparation`
  - Priorytet: MEDIUM
  - Dozwolone akcje: analyze_daily_results, optimize_parameters, prepare_feedback_cycle
  - Zakazane akcje: number_generator, bet, trade, generate_world

#### 6. WAITING
- **Warunek:** Brak aktywnych warunkow
- **Cel:** Oczekiwanie na zmiane stanu
- **Typowy moment:** Pozostale czasy
- **ExecutionContext:**
  - Cel: `wait_for_next_trigger`
  - Priorytet: LOW
  - Dozwolone akcje: monitor_system, check_triggers
  - Zakazane akcje: number_generator, bet, trade, generate_predictions

---

## 10. PRZEPŁYW EXECUTIONCONTEXT

### Schemat Przepływu

```
SSIPipeline.run_cycle()
    │
    ├─▶ world_generation (WorldEngine)
    │
    ├─▶ modeling (Modeling Layer)
    │
    ├─▶ teacher_analysis (Teacher Layer)
    │
    ├─▶ cycle_controller.detect_current_phase(world_state)
    │       │
    │       ├─▶ PhaseDetector (RESULTS > WORLD > DATABASE > ODDS > TIME)
    │       │
    │       └─▶ current_phase
    │
    └─▶ cycle_controller.get_execution_context()
            │
            └─▶ ExecutionContext(phase, goal, allowed_actions, forbidden_actions, ...)
                    │
                    └─▶ cycle_data["execution_context"]
                            │
                            └─▶ AgentRuntimeManager.receive_context()
                                    │
                                    ├─▶ Agent_01.execution_context
                                    ├─▶ Agent_02.execution_context
                                    ├─▶ Agent_03.execution_context
                                    ├─▶ Agent_04.execution_context
                                    ├─▶ Agent_05.execution_context
                                    └─▶ Agent_06.execution_context
```

### Kontekst a Zachowanie Agentów

| Faza | Kontekst | Zachowanie Agentów |
|------|----------|-------------------|
| RESULT_ANALYSIS | Ocena badań | Analiza historycznych predykcji, aktualizacja rankingow |
| WORLD_PREPARATION | Oczekiwanie | Monitorowanie stanu świata, walidacja danych |
| PREDICTION_WINDOW | Generowanie | Tworzenie nowych predykcji, ranking strategii |
| STRATEGY_EVOLUTION | Ewolucja | Testowanie nowych wariantow, optymalizacja |
| OPTIMIZATION | Optymalizacja | Końcowe poprawki, przygotowanie systemu |
| WAITING | Oczekiwanie | Minimalna aktywność, monitorowanie |

---

## 11. PRZEPŁYW PAMIĘCI STRATEGII

### Schemat Integracji

```
SSIPipeline.run_cycle()
    │
    ├─▶ world_generation (WorldEngine)
    │
    ├─▶ agent_execution (AgentRuntimeManager)
    │       │
    │       └─▶ agents (01-06) generuja predykcje
    │
    └─▶ _record_agent_results_to_strategy_memory()
            │
            ├─▶ Pest processing: agent_results → performance_data
            │       │
            │       ├─▶ accuracy = correct_predictions / total_predictions
            │       ├─▶ profit_factor = ...
            │       ├─▶ success = accuracy > 0.5
            │       └─▶ confidence_avg = mean confidence
            │
            ├─▶ StrategyMemoryManager.update_performance(strategy_id, performance_data)
            │
            ├─▶ StrategyMemoryManager.update_ranking(strategy_id, position)
            │
            ├─▶ StrategyMemoryManager.schedule_evaluation(strategy_id, required)
            │
            └─▶ JSON Persistence (memory/strategy_memory/)
                    │
                    ├─▶ strategy_{id}_v{version}.json
                    └─▶ strategy_memory_index.json
```

### Struktura Pamięci Strategii

```
StrategyMemoryRecord
├── memory_id: str (uuid)
├── strategy_id: str
├── strategy_version: str
├── strategy_definition: Dict
├── strategy_parameters: Dict
├── feature_schema: List[str]
├── model_reference: str
├── creation_time: datetime
├── last_updated: datetime
│
├── EXPERIMENT_HISTORY: List[Dict]  # Historia eksperymentow
├── PREDICTION_HISTORY: List[Dict]  # Historia predykcji
├── RESULT_HISTORY: List[Dict]      # Historia wynikow
├── REPUTATION_HISTORY: List[Dict]  # Historia reputacji
└── EVOLUTION_HISTORY: List[Dict]   # Historia ewolucji

└── ETAP 5.3.3 Extensions:
    ├── ranking_position: int
    ├── confidence_score: float
    ├── tested_variants: List[str]
    ├── next_evaluation: bool
    └── status: str (ACTIVE/INACTIVE/ARCHIVED)
```

### Metody StrategyMemoryManager

| Metoda | Opis |
|--------|------|
| `update_ranking(strategy_id, position)` | Aktualizuje pozycję w rankingu |
| `add_tested_variant(strategy_id, variant_id)` | Dodaje testowany wariant |
| `update_performance(strategy_id, cycle_data)` | Aktualizuje historię wyników |
| `schedule_evaluation(strategy_id, required)` | Planuje ponowną ewaluację |
| `set_status(strategy_id, status)` | Ustawia status strategii |
| `get_ranked_strategies(limit)` | Pobiera posortowane strategie |
| `get_strategies_requireing_evaluation()` | Pobiera strategie wymagające ewaluacji |

---

## 12. TRYB PRODUKCYJNY vs SYMULACYJNY

### Równice

| Aspekt | Tryb Produkcyjny | Tryb Symulacyjny |
|--------|------------------|------------------|
| Clock | `datetime.now()` | `SimulationClock` |
| Czas wykonania | Rzeczywisty (do 5h) | Symulowany (przyspieszony) |
| World State | Rzeczywisty | Symulowany |
| Agenci | Uruchamiani | NIE uruchamiani (tylko test detekcji) |
| Persystencja | Zapis do pliku | Opcjonalne |
| Cel | Produkcja predykcji | Testy i walidacja |

### Przełączanie Trybów

**Tryb Produkcyjny (domyślny):**
```python
# Bez przekazywania clock
pipeline = SSIPipeline(mode=PipelineMode.PRODUCTION)
# Używa datetime.now()
```

**Tryb Symulacyjny:**
```python
from SSI.v5.runtime import SimulationClock

clock = SimulationClock()
clock.set_time(datetime(2026, 8, 4, 15, 7, 0))

pipeline = SSIPipeline(mode=PipelineMode.TEST, clock=clock)
# Używa clock.get_current_time()
```

### Integracja CycleController

```python
# Produkcyjny
controller = create_cycle_controller()
# Używa datetime.now()

# Symulacyjny
clock = SimulationClock()
controller = create_cycle_controller(clock=clock)
# Używa clock.get_current_time()

# Detekcja fazy - ta sama logika
phase = controller.detect_current_phase(world_state)
```

---

## 13. NAZEWNICTWO MODUŁÓW

### Zasady Nazewnictwa

1. **Nowe nazwy modulow SSI V5 sa nazwami docelowymi**
2. **Stare nazwy traktować jako historyczne/tymczasowe**
3. **Nie przywracać starych nazw**

### Obowiązujące Nazwy (Docelowe)

| Komponent | Docelowa Nazwa | Lokalizacja |
|-----------|----------------|-------------|
| Główne moduły runtime | SSI/V5/runtime/ | `SSI/V5/runtime/` |
| Cycle Controller | cycle_controller.py | `SSI/V5/runtime/cycle_controller.py` |
| Simulation Clock | simulation_clock.py | `SSI/V5/runtime/simulation_clock.py` |
| Simulated World State | simulation_world_state.py | `SSI/V5/runtime/simulation_world_state.py` |
| Pipeline | SSIPipeline | `SSI_V5/core/pipeline.py` |
| World Engine | WorldEngine | `SSI_V5/core/world_engine.py` |
| Collectory | SSI_V5_*_COLLECTOR.py | `SSI_V5/*/SSI_V5_*_COLLECTOR.py` |

### Historyczne/Tymczasowe Nazwy (NIE używać)

| Komponent | Stara Nazwa | Status |
|-----------|-------------|--------|
| Collector | V2Collector | ❌ PRZESTARZAŁE |
| World Model | WorldModel | ❌ PRZESTARZAŁE |
| Runtime | SSIRuntime | ❌ UŻYWAĆ SSIRuntimeController |

### Reguły Tworzenia Nowych Nazw

1. Używać prefixu `SSI_V5_` dla modułów w SSI_V5/
2. Używać `SSI/v5/` dla modułów runtime
3. Unikać polskich znaków w nazwach plików
4. Używać `_` zamiast spacji
5.för Dokumentację używać `-` w nazwach plików (.md)

---

## 14. INTEGRACJA Z ISTNIEJĄCYM SYSTEMEM

### Niezmienione Komponenty

| Komponent | Lokalizacja | Status |
|-----------|-------------|--------|
| V1 Scheduler | uruchamianieModulow.py | ❌ NIE ZMIENIAĆ |
| Start Scheduler | start_ssi.py | ❌ NIE ZMIENIAĆ |
| Production Launcher | SSI_V5/runtime/start_ssi.py | ❌ NIE ZMIENIAĆ |

### Nowe Komponenty (ETAP 5.3)

| Komponent | Lokalizacja | Status |
|-----------|-------------|--------|
| CycleController | SSI/v5/runtime/cycle_controller.py | ✅ NOWY |
| SimulationClock | SSI/v5/runtime/simulation_clock.py | ✅ NOWY |
| SimulatedWorldState | SSI/v5/runtime/simulation_world_state.py | ✅ NOWY |

### Zmienione Komponenty

| Komponent | Lokalizacja | Zmiana | Status |
|-----------|-------------|--------|--------|
| SSIPipeline | SSI_V5/core/pipeline.py | + clock param | ✅ ZMIENIONY |
| CycleController (V5) | SSI/V5/runtime/cycle_controller.py | + clock support | ✅ ZMIENIONY |
| CycleController (V5 copy) | SSI_V5/runtime/cycle_controller.py | + clock support | ✅ ZMIENIONY |
| Runtime __init__ | SSI/v5/runtime/__init__.py | + SimulationClock export | ✅ ZMIENIONY |

---

## 15. DOKUMENTACJA POWIĄZANA

### Raporty ETAP 5.3

| Dokument | Opis | Status |
|----------|------|--------|
| [SSI_V5_CYCLE_CONTROLLER_IMPLEMENTATION_REPORT.md](SSI_V5_CYCLE_CONTROLLER_IMPLEMENTATION_REPORT.md) | Implementacja Cycle Controller (5.3.1) | ✅ ISTNIEJE |
| [SSI_V5_STRATEGY_PERSISTENCE_MEMORY_REPORT.md](SSI_V5_STRATEGY_PERSISTENCE_MEMORY_REPORT.md) | Implementacja StrategyMemory (5.3.3) | ✅ ISTNIEJE |
| [SSI_V5_SIMULATION_CYCLE_REPORT.md](SSI_V5_SIMULATION_CYCLE_REPORT.md) | Symulacja cyklu 24H (5.3.4) | ✅ ISTNIEJE |
| **SSI_V5_RUNTIME_ARCHITECTURE.md** | **Ten dokument** - Główna architektura (5.3) | ✅ NOWY |
| **SSI_V5_RUNTIME_ALIGNMENT_REPORT.md** | **Raport końcowy** - Documentation Alignment (5.3.5) | ✅ ZAKOŃCZONY |

### Dokumenty Powiązane

| Dokument | Opis |
|----------|------|
| [SPRINT_11_5_ARCHITECTURE.md](SPRINT_11_5_ARCHITECTURE.md) | Ogólna architekura Sprint 11.5 |
| [SSI_V5_LIFE_CYCLE_ARCHITECTURE.md](SSI_V5/SSI_V5_LIFE_CYCLE_ARCHITECTURE.md) | Lifecycle systemu (5.2.4) |

### Dokumenty powiązane

| Dokument | Opis |
|----------|------|
| [SPRINT_11_5_ARCHITECTURE.md](SPRINT_11_5_ARCHITECTURE.md) | Ogólna architekura Sprint 11.5 |
| [SSI_V5_LIFE_CYCLE_ARCHITECTURE.md](SSI_V5/SSI_V5_LIFE_CYCLE_ARCHITECTURE.md) | Lifecycle systemu (5.2.4) |

---

## 🎯 PODSUMOWANIE ETAP 5.3

### Statusy

| ETAP | Nazwa | Status | Data |
|------|-------|--------|------|
| 5.3.1 | Cycle Controller | ✅ ZAKOŃCZONY | 2026-08-04 |
| 5.3.2 | Execution Context Delivery | ✅ ZAKOŃCZONY | 2026-08-04 |
| 5.3.3 | Strategy Persistence Memory | ✅ ZAKOŃCZONY | 2026-08-04 |
| 5.3.4 | Simulation Cycle | ✅ ZAKOŃCZONY | 2026-08-04 |
| 5.3.5 | Documentation Alignment | ✅ **ZAKOŃCZONY** | **2026-08-04** |

### Funkcjonalności Zaimplementowane

✅ **Świadomość Cyklu** - System wie w jakiej fazie się znajduje  
✅ **Kontekst Wykonania** - Agenci otrzymują informacje o aktualnej fazie  
✅ **Pamięć Strategii** - Historia i ewolucja strategii jest zapamiętywana  
✅ **Symulacja 24H** - Możliwość testowania pełnego cyklu bez produkcji  
✅ **Persystencja** - Stan cyklu i pamięć strategii są zapisywane  
✅ **Integracja** - Wszystkie komponenty współpracują ze sobą  

### Testy

- **Cycle Controller Tests:** 40/40 PASS ✅  
- **Strategy Memory Tests:** 10/10 PASS ✅  
- **Simulation Cycle Tests:** 15/15 PASS ✅  
- **Total:** 65/65 PASS ✅  

---

*Generated by Mistral Vibe for ETAP 5.3.5*  
*Co-Authored-By: Mistral Vibe <vibe@mistral.ai>*  
*Data: 2026-08-04*
