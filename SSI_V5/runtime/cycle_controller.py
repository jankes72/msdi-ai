# SSI V5 - Cycle Controller
# ETAP 5.3.1: Warstwa Swiadomosci Cyklu
# ==================================================
#
# Odpowiedzialnosc:
# - Wykrywanie aktualnej fazy cyklu na podstawie stanu danych
# - Zarządanie przejściami między fazami
# - Dostarczanie kontekstu wykonania dla agentów
# - Zapis i wznowienie stanu cyklu

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from datetime import datetime
import json
import os
from pathlib import Path
import uuid


class CyclePhase(Enum):
    """Fazy cyklu systemu SSI V5"""
    UNKNOWN = "unknown"
    RESULT_ANALYSIS = "result_analysis"        # ~02:07 - Feedback Cycle
    WORLD_PREPARATION = "world_preparation"  # Po starcie generatora
    PREDICTION_WINDOW = "prediction_window"    # world_ready + odds_available
    STRATEGY_EVOLUTION = "strategy_evolution"  # ~15:07 - Po predykcjach
    OPTIMIZATION = "optimization"              # ~21:07 - Końcowe korekty
    WAITING = "waiting"                        # Brak aktywnej pracy


@dataclass
class CycleState:
    """Stan cyklu systemu"""
    cycle_id: str
    current_phase: CyclePhase
    started_at: Optional[str] = None
    completed_phases: List[str] = field(default_factory=list)
    prediction_cycle_completed: bool = False
    world_generation_completed: bool = False
    results_processed: bool = False
    strategies_evaluated: bool = False
    last_update: Optional[str] = None
    phase_transitions: List[Dict[str, Any]] = field(default_factory=list)
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'cycle_id': self.cycle_id,
            'current_phase': self.current_phase.value,
            'started_at': self.started_at,
            'completed_phases': self.completed_phases.copy(),
            'prediction_cycle_completed': self.prediction_cycle_completed,
            'world_generation_completed': self.world_generation_completed,
            'results_processed': self.results_processed,
            'strategies_evaluated': self.strategies_evaluated,
            'last_update': self.last_update,
            'phase_transitions': [t.copy() for t in self.phase_transitions],
            'version': self.version,
            'metadata': self.metadata.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CycleState':
        """Tworzenie z słownika"""
        return cls(
            cycle_id=data.get('cycle_id', str(uuid.uuid4())),
            current_phase=CyclePhase(data.get('current_phase', 'unknown')),
            started_at=data.get('started_at'),
            completed_phases=data.get('completed_phases', []),
            prediction_cycle_completed=data.get('prediction_cycle_completed', False),
            world_generation_completed=data.get('world_generation_completed', False),
            results_processed=data.get('results_processed', False),
            strategies_evaluated=data.get('strategies_evaluated', False),
            last_update=data.get('last_update'),
            phase_transitions=data.get('phase_transitions', []),
            version=data.get('version', '1.0.0'),
            metadata=data.get('metadata', {})
        )

    def mark_phase_completed(self, phase: CyclePhase) -> None:
        """Oznaczenie fazy jako zakończonej"""
        phase_name = phase.value
        if phase_name not in self.completed_phases:
            self.completed_phases.append(phase_name)
            self.last_update = datetime.now().isoformat()

    def add_phase_transition(self, from_phase: CyclePhase, to_phase: CyclePhase) -> None:
        """Rejestracja przejścia między fazami"""
        self.phase_transitions.append({
            'from': from_phase.value,
            'to': to_phase.value,
            'timestamp': datetime.now().isoformat()
        })
        self.last_update = datetime.now().isoformat()


@dataclass
class WorldState:
    """Stan świata dla detekcji fazy"""
    new_results_available: bool = False
    results_processed: bool = False
    world_status: str = "UNKNOWN"  # UNKNOWN, GENERATING, READY, ERROR
    world_is_ready: bool = False
    database_status: str = "UNKNOWN"  # UNKNOWN, UPDATING, READY, ERROR
    odds_available: bool = False
    current_time: Optional[datetime] = None
    prediction_cycle_completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'new_results_available': self.new_results_available,
            'results_processed': self.results_processed,
            'world_status': self.world_status,
            'world_is_ready': self.world_is_ready,
            'database_status': self.database_status,
            'odds_available': self.odds_available,
            'current_time': self.current_time.isoformat() if self.current_time else None,
            'prediction_cycle_completed': self.prediction_cycle_completed
        }


@dataclass
class ExecutionContext:
    """Kontekst wykonania dla agentów"""
    phase: CyclePhase
    goal: str
    available_memory: List[str]
    allowed_actions: List[str]
    forbidden_actions: List[str]
    priority: str = "medium"
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'phase': self.phase.value,
            'goal': self.goal,
            'available_memory': self.available_memory.copy(),
            'allowed_actions': self.allowed_actions.copy(),
            'forbidden_actions': self.forbidden_actions.copy(),
            'priority': self.priority,
            'parameters': self.parameters.copy()
        }


class PhaseDetector:
    """Detector fazy cyklu na podstawie stanu świata"""

    # Priorytety detekcji (od najważniejszego)
    DETECTION_PRIORITY = [
        '_check_results_state',
        '_check_world_state', 
        '_check_database_state',
        '_check_odds_state',
        '_check_time_based'
    ]

    def __init__(self):
        """Inicjalizacja detektora"""
        self._cache: Dict[str, Any] = {}

    def detect_phase(self, world_state: WorldState, current_time: Optional[datetime] = None) -> CyclePhase:
        """
        Wykrywanie aktualnej fazy na podstawie stanu świata.
        
        Priorytet: RESULTS > WORLD > DATABASE > ODDS > TIME
        
        Args:
            world_state: Aktualny stan świata
            current_time: Aktualny czas (opcjonalny)
            
        Returns:
            Wykryta faza cyklu
        """
        # Ustaw current_time w world_state jeśli przekazany
        if current_time is not None:
            world_state.current_time = current_time
        
        for method_name in self.DETECTION_PRIORITY:
            method = getattr(self, method_name)
            phase = method(world_state)
            if phase is not None:
                return phase
        
        return CyclePhase.UNKNOWN

    def _check_results_state(self, world_state: WorldState) -> Optional[CyclePhase]:
        """Sprawdza stan wyników - najwyższy priorytet"""
        if world_state.new_results_available and not world_state.results_processed:
            return CyclePhase.RESULT_ANALYSIS
        return None

    def _check_world_state(self, world_state: WorldState) -> Optional[CyclePhase]:
        """Sprawdza stan świata"""
        if world_state.world_is_ready:
            return CyclePhase.PREDICTION_WINDOW
        elif world_state.world_status in ["GENERATING", "UPDATING"]:
            return CyclePhase.WORLD_PREPARATION
        return None

    def _check_database_state(self, world_state: WorldState) -> Optional[CyclePhase]:
        """Sprawdza stan bazy danych"""
        if world_state.database_status in ["UPDATING"]:
            return CyclePhase.WORLD_PREPARATION
        return None

    def _check_odds_state(self, world_state: WorldState) -> Optional[CyclePhase]:
        """Sprawdza dostępność kursów"""
        if world_state.odds_available and world_state.world_is_ready:
            return CyclePhase.PREDICTION_WINDOW
        return None

    def _check_time_based(self, world_state: WorldState) -> Optional[CyclePhase]:
        """Używa czasu jako ostatnia wskazówka"""
        if world_state.current_time is None:
            return None
        
        hour = world_state.current_time.hour
        minute = world_state.current_time.minute
        
        # Określone godziny dla poszczególnych faz
        # RESULT_ANALYSIS ~02:07
        if hour == 2 and minute >= 7:
            return CyclePhase.RESULT_ANALYSIS
        
        # PREDICTION_WINDOW ~08:05+
        if hour >= 8 and minute >= 5:
            return CyclePhase.PREDICTION_WINDOW
        
        # STRATEGY_EVOLUTION ~15:07
        if hour == 15 and minute >= 7:
            return CyclePhase.STRATEGY_EVOLUTION
        
        # OPTIMIZATION ~21:07
        if hour == 21 and minute >= 7:
            return CyclePhase.OPTIMIZATION
        
        return CyclePhase.WAITING


# Konteksty dla poszczególnych faz (ETAP 5.3.2)
PHASE_CONTEXTS = {
    CyclePhase.RESULT_ANALYSIS: ExecutionContext(
        phase=CyclePhase.RESULT_ANALYSIS,
        goal="analyze_results_and_update_knowledge",
        available_memory=["world_memory", "strategy_memory", "experience_memory", "result_memory"],
        allowed_actions=["load_results", "analyze_predictions", "evaluate_strategies", "update_rankings", "save_feedback"],
        forbidden_actions=["number_generator", "bet", "trade", "generate_predictions"],
        priority="high",
        parameters={"max_analyzed_matches": 100, "min_confidence_threshold": 0.5}
    ),
    
    CyclePhase.WORLD_PREPARATION: ExecutionContext(
        phase=CyclePhase.WORLD_PREPARATION,
        goal="wait_for_world_data_and_prepare",
        available_memory=["world_memory", "strategy_memory"],
        allowed_actions=["check_world_status", "load_world_data", "validate_data", "wait"],
        forbidden_actions=["number_generator", "bet", "trade", "generate_predictions"],
        priority="medium",
        parameters={"max_wait_time": 300, "validation_threshold": 0.95}
    ),
    
    CyclePhase.PREDICTION_WINDOW: ExecutionContext(
        phase=CyclePhase.PREDICTION_WINDOW,
        goal="generate_accurate_predictions_and_strategies",
        available_memory=["world_database", "market_data", "odds_data", "strategy_memory", "experience_memory"],
        allowed_actions=["load_world_data", "analyze_matches", "run_exact_score_engine", 
                        "generate_predictions", "create_strategies", "evaluate_tensor_flows"],
        forbidden_actions=["number_generator", "bet", "trade"],
        priority="high",
        parameters={"max_predictions": 100, "min_confidence": 0.55, "max_strategies": 10}
    ),
    
    CyclePhase.STRATEGY_EVOLUTION: ExecutionContext(
        phase=CyclePhase.STRATEGY_EVOLUTION,
        goal="evolve_and_test_new_strategies",
        available_memory=["world_memory", "strategy_memory", "evolution_memory", "experience_memory"],
        allowed_actions=["load_existing_strategies", "mutate_strategies", "test_variants", 
                        "evaluate_performance", "save_evolution_results"],
        forbidden_actions=["number_generator", "bet", "trade", "generate_predictions"],
        priority="high",
        parameters={"evolution_rate": 0.15, "max_variants_per_strategy": 5, "testing_budget": 50}
    ),
    
    CyclePhase.OPTIMIZATION: ExecutionContext(
        phase=CyclePhase.OPTIMIZATION,
        goal="optimize_system_and_prepare_for_feedback",
        available_memory=["world_memory", "strategy_memory", "optimization_memory", "experience_memory"],
        allowed_actions=["load_system_state", "analyze_performance", "tune_parameters", 
                        "prepare_feedback_data", "optimize_resources"],
        forbidden_actions=["number_generator", "bet", "trade", "generate_predictions"],
        priority="medium",
        parameters={"optimization_depth": "deep", "max_iterations": 100, "convergence_threshold": 0.01}
    ),
    
    CyclePhase.WAITING: ExecutionContext(
        phase=CyclePhase.WAITING,
        goal="wait_for_next_cycle_trigger",
        available_memory=["world_memory", "strategy_memory"],
        allowed_actions=["check_time", "monitor_system", "wait", "log_status"],
        forbidden_actions=["number_generator", "bet", "trade", "generate_predictions", "evolve_strategies"],
        priority="low",
        parameters={"max_sleep_time": 300, "check_interval": 60}
    ),
    
    CyclePhase.UNKNOWN: ExecutionContext(
        phase=CyclePhase.UNKNOWN,
        goal="determine_current_phase_and_context",
        available_memory=["system_memory"],
        allowed_actions=["detect_phase", "check_system_health", "initialize_context"],
        forbidden_actions=["number_generator", "bet", "trade", "generate_predictions", "evolve_strategies"],
        priority="low",
        parameters={"diagnostic_mode": True}
    )
}


class CycleController:
    """
    Główny kontroler cyklu systemu SSI V5.
    
    Odpowiedzialność:
    - Inicjalizacja i zarządanie stanem cyklu
    - Integracja z PhaseDetector
    - Zarządanie przejściami między fazami
    - Dostarczanie kontekstu wykonania
    - Persystencja stanu cyklu
    """

    DEFAULT_STATE_PATH = "cycle_state.json"

    def __init__(self, state_path: Optional[str] = None, clock = None):
        """
        Inicjalizacja CycleController.
        
        Args:
            state_path: Ścieżka do pliku stanu cyklu
            clock: Opcjonalny zegar symulacyjny (SimulationClock).
                   Wykorzystywany w trybie symulacyjnym (ETAP 5.3.4)
        """
        self.state_path = state_path or self.DEFAULT_STATE_PATH
        self.cycle_state: Optional[CycleState] = None
        self.phase_detector = PhaseDetector()
        self._initialized = False
        self._clock = clock  # Zegar symulacyjny (ETAP 5.3.4)
        
        # Inicjalizacja stanu
        self._initialize_state()

    def _initialize_state(self) -> None:
        """Inicjalizacja stanu cyklu"""
        if not os.path.exists(self.state_path):
            # Tworzenie nowego stanu
            self.cycle_state = CycleState(
                cycle_id=str(uuid.uuid4()),
                current_phase=CyclePhase.WAITING,
                started_at=datetime.now().isoformat(),
                last_update=datetime.now().isoformat()
            )
        else:
            # Ładowanie istniejącego stanu
            self.load_cycle_state()
        
        self._initialized = True

    def detect_current_phase(self, world_state: WorldState, current_time = None) -> CyclePhase:
        """
        Wykrywanie i aktualizacja aktualnej fazy.
        
        Args:
            world_state: Aktualny stan świata
            current_time: Aktualny czas (opcjonalny)
            
        Returns:
            Wykryta faza
        """
        if not self.cycle_state:
            self._initialize_state()
        
        # Priorytet: current_time > clock > datetime.now()
        if current_time is None:
            if self._clock is not None:
                current_time = self._clock.get_current_time()
            else:
                current_time = datetime.now()
        
        current_phase = self.cycle_state.current_phase
        new_phase = self.phase_detector.detect_phase(world_state, current_time)
        
        # Rejestracja przejścia
        if new_phase != current_phase:
            old_phase = self.cycle_state.current_phase
            self.cycle_state.add_phase_transition(old_phase, new_phase)
            self.cycle_state.current_phase = new_phase
            self.cycle_state.last_update = datetime.now().isoformat()
        
        return self.cycle_state.current_phase

    def transition_to_phase(self, new_phase: CyclePhase) -> bool:
        """
        Wymusz przejście do określonej fazy.
        
        Args:
            new_phase: Docelowa faza
            
        Returns:
            True jeśli przejście zostało zarejestrowane
        """
        if not self.cycle_state:
            return False
        
        if self.cycle_state.current_phase != new_phase:
            old_phase = self.cycle_state.current_phase
            self.cycle_state.add_phase_transition(old_phase, new_phase)
            self.cycle_state.current_phase = new_phase
            self.cycle_state.last_update = datetime.now().isoformat()
            return True
        
        return False

    def get_execution_context(self) -> ExecutionContext:
        """
        Pobranie aktualnego kontekstu wykonania.
        
        Returns:
            Aktualny ExecutionContext
        """
        if not self.cycle_state:
            self._initialize_state()
        
        return PHASE_CONTEXTS.get(self.cycle_state.current_phase, PHASE_CONTEXTS[CyclePhase.UNKNOWN])

    def get_execution_context_for_phase(self, phase: CyclePhase) -> ExecutionContext:
        """
        Pobranie kontekstu dla określonej fazy.
        
        Args:
            phase: Docelowa faza
            
        Returns:
            Kontekst dla fazy
        """
        return PHASE_CONTEXTS.get(phase, PHASE_CONTEXTS[CyclePhase.UNKNOWN])

    def get_cycle_state(self) -> Optional[CycleState]:
        """
        Pobranie aktualnego stanu cyklu.
        
        Returns:
            Aktualny stan cyklu
        """
        return self.cycle_state

    def save_cycle_state(self, custom_path: Optional[str] = None) -> bool:
        """
        Zapisanie stanu cyklu do pliku.
        
        Args:
            custom_path: Opcjonalna ścieżka zapisu
            
        Returns:
            True jeśli zapis się powiódł
        """
        if not self.cycle_state:
            return False
        
        path = custom_path or self.state_path
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.cycle_state.to_dict(), f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"[ERROR] Nie udało się zapisać stanu cyklu: {e}")
            return False

    def load_cycle_state(self, custom_path: Optional[str] = None) -> Optional[CycleState]:
        """
        Ładowanie stanu cyklu z pliku.
        
        Args:
            custom_path: Opcjonalna ścieżka do ładowania
            
        Returns:
            Załadowany stan cyklu
        """
        path = custom_path or self.state_path
        
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cycle_state = CycleState.from_dict(data)
                    return self.cycle_state
        except Exception as e:
            print(f"[ERROR] Nie udało się załadować stanu cyklu: {e}")
        
        return None

    def resume_from_state(self, state_path: Optional[str] = None) -> bool:
        """
        Wznowienie pracy z zapisanego stanu.
        
        Args:
            state_path: Ścieżka do pliku stanu
            
        Returns:
            True jeśli wznowienie się powiodło
        """
        loaded_state = self.load_cycle_state(state_path)
        if loaded_state:
            print(f"[INFO] Wznowiono z fazy: {loaded_state.current_phase.value}")
            return True
        return False

    def reset_cycle(self) -> CycleState:
        """
        Resetowanie stanu cyklu (nowy cykl).
        
        Returns:
            Nowy stan cyklu
        """
        old_state = self.cycle_state
        self.cycle_state = CycleState(
            cycle_id=str(uuid.uuid4()),
            current_phase=CyclePhase.WAITING,
            started_at=datetime.now().isoformat(),
            last_update=datetime.now().isoformat(),
            metadata={'reset_from': old_state.cycle_id if old_state else 'initial'}
        )
        return self.cycle_state

    def mark_phase_completed(self, phase: CyclePhase) -> None:
        """
        Oznaczenie fazy jako zakończonej.
        
        Args:
            phase: Faza do oznaczenia
        """
        if self.cycle_state:
            self.cycle_state.mark_phase_completed(phase)

    def is_in_phase(self, phase: CyclePhase) -> bool:
        """
        Sprawdzenie czy system jest w określonej fazie.
        
        Args:
            phase: Sprawdzana faza
            
        Returns:
            True jeśli system jest w fazie
        """
        if not self.cycle_state:
            return False
        return self.cycle_state.current_phase == phase

    def get_phase_transitions(self) -> List[Dict[str, Any]]:
        """
        Pobranie historii przejść między fazami.
        
        Returns:
            Lista przejść
        """
        if not self.cycle_state:
            return []
        return self.cycle_state.phase_transitions.copy()


def create_cycle_controller(state_path: Optional[str] = None, clock = None) -> CycleController:
    """
    Fabryka tworzenia CycleController.
    
    Args:
        state_path: Opcjonalna ścieżka do stanu
        clock: Opcjonalny zegar symulacyjny (SimulationClock).
               Wykorzystywany w trybie symulacyjnym (ETAP 5.3.4)
        
    Returns:
        Nowa instancja CycleController
    """
    return CycleController(state_path=state_path, clock=clock)


# Inicjalizacja globalna (opcjonalne)
# _global_cycle_controller: Optional[CycleController] = None
# 
# def get_global_cycle_controller() -> CycleController:
#     """Pobranie globalnego CycleController"""
#     global _global_cycle_controller
#     if _global_cycle_controller is None:
#         _global_cycle_controller = create_cycle_controller()
#     return _global_cycle_controller
