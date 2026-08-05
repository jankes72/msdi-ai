#!/usr/bin/env python3
"""
SSI V5 - Cycle Controller
Warstwat swiadomosci cyklu dla systemu runtime.

OPIS:
Cycle Controller jest mala warstwa sterujaca, ktora nadaje systemowi SSI V5
swiadomosc, w jakiej Fazie cyklu pracy aktualnie sie znajduje.

ZASADY ARCHITEKTONICZNE:
- NIE zastepuje istniejacego schedulera
- NIE modyfikuje uruchamianieModulow.py (V1)
- Jest warstwa nadrzedna nad runtime_controller.py
- Priorytet detekcji: WORLD_STATE > DATABASE_STATE > RESULTS_STATE > ODDS_STATE > TIME

FAZY:
- UNKNOWN: Stan poczatkowy/nieokreslony
- RESULT_ANALYSIS: Analiza wynikow (okolo 02:07, gdy new_results_available=True)
- WORLD_PREPARATION: Oczekiwanie na gotowosc swiata (world_status != READY)
- PREDICTION_WINDOW: Generowanie predykcji (world_state==READY AND odds_available==True)
- STRATEGY_EVOLUTION: Ewolucja strategii (po zakonczeniu predykcji, okolo 15:07)
- OPTIMIZATION: Optymalizacja koncowa (okolo 21:07)
- WAITING: Brak aktywnej pracy

Autor: SSI V5 System
Data: 2026-08-04
Wersja: 1.0.0
"""

import os
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, time as datetime_time
from typing import Dict, Any, Optional, List
from enum import Enum
from pathlib import Path


# =============================================================================
# ENUM: CyclePhase - Dostepne fazy cyklu
# =============================================================================

class CyclePhase(Enum):
    """Dostepne fazy cyklu pracy systemu SSI V5."""
    
    UNKNOWN = "unknown"
    """Stan poczatkowy lub nieokreslony."""
    
    RESULT_ANALYSIS = "result_analysis"
    """
    Faza analizy wynikow.
    
    Warunek: new_results_available == True
    Cel: analiza zakonczonych predykcji, porownanie kuponow, 
         ocena strategii, aktualizacja rankingow, zapis feedback memory.
    
    Typowy moment: okolo 02:07
    """
    
    WORLD_PREPARATION = "world_preparation"
    """
    Faza przygotowania swiata.
    
    Warunek: world_status != READY
    Cel: oczekiwanie az baza swiata zostanie wygenerowana,
         timestamp bazy jest aktualny, dane zostana przygotowane.
    
    Typowy moment: po starcie generatora swiata okolo 08:05
    """
    
    PREDICTION_WINDOW = "prediction_window"
    """
    Faza generowania predykcji.
    
    Warunek: world_state == READY AND odds_available == True
    Cel: generowanie predykcji, Exact Score Engine, Strategy Laboratory,
         ranking strategii, przygotowanie kuponow.
    """
    
    STRATEGY_EVOLUTION = "strategy_evolution"
    """
    Faza ewolucji strategii.
    
    Warunek: prediction_cycle_completed == True
    Cel: eksperymenty, testowanie wariantow strategii,
         rozwoj agentow, analiza alternatywnych modeli.
    
    Typowy moment: okolo 15:07
    """
    
    OPTIMIZATION = "optimization"
    """
    Faza optymalizacji koncowej.
    
    Cel: koncowe korekty, przygotowanie systemu do nastepego feedback cycle.
    
    Typowy moment: okolo 21:07
    """
    
    WAITING = "waiting"
    """Brak aktywnej pracy - system oczekuje na zmiane stanu."""


# =============================================================================
# DATACLASS: CycleState - Stan cyklu
# =============================================================================

@dataclass
class CycleState:
    """
    Stan cyklu pracy systemu SSI V5.
    
    Zawiera informacje o:
    - aktualnej fazie
    - historii przejsc
    - stanie predykcji
    - timestampach
    """
    
    # Identyfikator cyklu
    cycle_id: str = ""
    
    # Aktualna faza
    current_phase: CyclePhase = CyclePhase.UNKNOWN
    
    # Czas rozpoczęcia cyklu
    started_at: Optional[str] = None
    
    # Lista zakonczonych faz w biezacym cyklu
    completed_phases: List[str] = field(default_factory=list)
    
    # Flagi stanu
    prediction_cycle_completed: bool = False
    world_generation_completed: bool = False
    results_processed: bool = False
    strategies_evaluated: bool = False
    
    # Czas ostatniej aktualizacji
    last_update: Optional[str] = None
    
    # Historia przejsc miedzy fazami
    phase_transitions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Wersja stanu
    version: str = "1.0.0"
    
    # Dodatkowe metadane
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicjalizacja domyslnych wartosci."""
        if not self.cycle_id:
            self.cycle_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not self.started_at:
            self.started_at = datetime.now().isoformat()
        if not self.last_update:
            self.last_update = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja stanu do slownika."""
        result = asdict(self)
        # Konwersja enumow do stringow
        if isinstance(result.get('current_phase'), CyclePhase):
            result['current_phase'] = result['current_phase'].value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CycleState':
        """Tworzenie stanu z slownika."""
        if 'current_phase' in data and isinstance(data['current_phase'], str):
            data['current_phase'] = CyclePhase(data['current_phase'])
        return cls(**data)
    
    def mark_phase_completed(self, phase: CyclePhase) -> None:
        """Oznaczenie fazy jako zakonczonej."""
        if phase.value not in self.completed_phases:
            self.completed_phases.append(phase.value)
        self.last_update = datetime.now().isoformat()
    
    def add_phase_transition(self, from_phase: CyclePhase, to_phase: CyclePhase) -> None:
        """Dodanie przejscia miedzy fazami do historii."""
        transition = {
            "from": from_phase.value,
            "to": to_phase.value,
            "timestamp": datetime.now().isoformat()
        }
        self.phase_transitions.append(transition)
        self.last_update = datetime.now().isoformat()


# =============================================================================
# CLASS: PhaseDetector - Wykrywanie fazy na podstawie stanu swiata
# =============================================================================

class PhaseDetector:
    """
    Detektor fazy cyklu.
    
    Okresla aktualna faze na podstawie stanu swiata i danych.
    Priorytet: WORLD_STATE > DATABASE_STATE > RESULTS_STATE > ODDS_STATE > TIME
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    def detect_phase(
        self,
        world_state: Dict[str, Any],
        current_time: Optional[datetime] = None
    ) -> CyclePhase:
        """
        Wykrywa aktualna faze na podstawie stanu swiata.
        
        Kolejnosc sprawdzania (od najwazniejszego):
        1. RESULTS_STATE (dostepnosc nowych wynikow) - NAJWYZSZE PRIORYTET
        2. WORLD_STATE (status swiata)
        3. DATABASE_STATE (gotowosc bazy danych)
        4. ODDS_STATE (dostepnosc kursow)
        5. CZAS (jako ostatnia wskazowka)
        
        Args:
            world_state: Slownik ze stanem swiata i systemu
            current_time: Aktualny czas (opcjonalny, domyslnie now())
        
        Returns:
            CyclePhase: Wykryta faza
        """
        current_time = current_time or datetime.now()
        
        # 1. Sprawdz dostepnosc wynikow (NAJWYZSZY PRIORYTET)
        phase = self._check_results_state(world_state, current_time)
        if phase != CyclePhase.UNKNOWN:
            return phase
        
        # 2. Sprawdz stan swiata
        phase = self._check_world_state(world_state, current_time)
        if phase != CyclePhase.UNKNOWN:
            return phase
        
        # 3. Sprawdz stan bazy danych
        phase = self._check_database_state(world_state, current_time)
        if phase != CyclePhase.UNKNOWN:
            return phase
        
        # 4. Sprawdz dostepnosc kursow
        phase = self._check_odds_state(world_state, current_time)
        if phase != CyclePhase.UNKNOWN:
            return phase
        
        # 5. Na koniec sprawdz czas (jako wskazowka)
        phase = self._check_time_based(current_time)
        return phase
    
    def _check_world_state(
        self,
        world_state: Dict[str, Any],
        current_time: datetime
    ) -> CyclePhase:
        """Sprawdza faze na podstawie stanu swiata."""
        world_status = world_state.get('status', '').upper()
        world_ready = world_state.get('is_ready', False)
        world_timestamp = world_state.get('timestamp')
        
        # Jesli swiat jest gotowy
        if world_ready or world_status == 'READY':
            # Sprawdz czy odds sa dostepne
            odds_available = world_state.get('odds_available', False)
            if odds_available:
                return CyclePhase.PREDICTION_WINDOW
            else:
                # Swiat gotowy ale brak kursow - oczekiwanie
                return CyclePhase.WORLD_PREPARATION
        
        # Jesli swiat nie jest gotowy
        if world_status in ['GENERATING', 'BUILDING', 'LOANDING']:
            return CyclePhase.WORLD_PREPARATION
        
        return CyclePhase.UNKNOWN
    
    def _check_database_state(
        self,
        world_state: Dict[str, Any],
        current_time: datetime
    ) -> CyclePhase:
        """Sprawdza faze na podstawie stanu bazy danych."""
        db_version = world_state.get('database_version')
        db_timestamp = world_state.get('database_timestamp')
        db_status = world_state.get('database_status', '').upper()
        
        # Jesli baza jest aktualna i gotowa
        if db_status == 'READY' and db_timestamp:
            # Sprawdz czy swiat jest gotowy (jesli nie, to WORLD_PREPARATION)
            if not world_state.get('is_ready', False):
                return CyclePhase.WORLD_PREPARATION
        
        # Jesli baza sie generuje
        if db_status in ['GENERATING', 'UPDATING']:
            return CyclePhase.WORLD_PREPARATION
        
        return CyclePhase.UNKNOWN
    
    def _check_results_state(
        self,
        world_state: Dict[str, Any],
        current_time: datetime
    ) -> CyclePhase:
        """Sprawdza faze na podstawie dostepnosci wynikow."""
        new_results_available = world_state.get('new_results_available', False)
        results_processed = world_state.get('results_processed', False)
        
        # Jesli sa nowe wyniki i nie zostaly przetworzone
        if new_results_available and not results_processed:
            return CyclePhase.RESULT_ANALYSIS
        
        return CyclePhase.UNKNOWN
    
    def _check_odds_state(
        self,
        world_state: Dict[str, Any],
        current_time: datetime
    ) -> CyclePhase:
        """Sprawdza faze na podstawie dostepnosci kursow."""
        odds_available = world_state.get('odds_available', False)
        odds_timestamp = world_state.get('odds_timestamp')
        
        # Kursy sa dostepne - sprawdz czy swiat jest gotowy
        if odds_available:
            if world_state.get('is_ready', False):
                return CyclePhase.PREDICTION_WINDOW
        
        return CyclePhase.UNKNOWN
    
    def _check_time_based(self, current_time: datetime) -> CyclePhase:
        """
        Sprawdza faze na podstawie czasu (tylko jako ostatnia wskazowka).
        
        Godziny orientacyjne:
        - 02:07: RESULT_ANALYSIS
        - 08:05-13:00: PREDICTION_WINDOW / WORLD_PREPARATION
        - 15:07: STRATEGY_EVOLUTION
        - 21:07: OPTIMIZATION
        """
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        # 02:07 - Feedback Cycle
        if current_hour == 2 and current_minute >= 5 and current_minute <= 10:
            return CyclePhase.RESULT_ANALYSIS
        
        # 08:05-13:00 - Prediction Window
        if current_hour >= 8 and current_hour < 13:
            return CyclePhase.PREDICTION_WINDOW
        
        # 15:07 - Strategy Evolution
        if current_hour == 15 and current_minute >= 5 and current_minute <= 10:
            return CyclePhase.STRATEGY_EVOLUTION
        
        # 21:07 - Optimization
        if current_hour == 21 and current_minute >= 5 and current_minute <= 10:
            return CyclePhase.OPTIMIZATION
        
        # Pozostale godziny - WAITING
        return CyclePhase.WAITING


# =============================================================================
# DATACLASS: ExecutionContext - Kontekst wykonania dla agentow
# =============================================================================

@dataclass
class ExecutionContext:
    """
    Kontekst wykonania dla agentow.
    
    Okresla:
    - w jakiej fazie jest system
    - jaki jest cel aktualnego cyklu
    - jakie pamieci sa dostepne
    - jakie akcje sa dozwolone/zakazane
    """
    
    # Faza cyklu
    phase: CyclePhase
    
    # Cel wykonania
    goal: str
    
    # Dostepne typy pamieci
    available_memory: List[str] = field(default_factory=list)
    
    # Dozwolone akcje
    allowed_actions: List[str] = field(default_factory=list)
    
    # Zakazane akcje (np. "number_generator", "bet")
    forbidden_actions: List[str] = field(default_factory=list)
    
    # Priorytet zadan
    priority: str = "normal"
    
    # Dodatkowe parametry
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamp
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        result = asdict(self)
        if isinstance(result.get('phase'), CyclePhase):
            result['phase'] = result['phase'].value
        return result


# =============================================================================
# CLASS: CycleController - Glowny kontroler cyklu
# =============================================================================

class CycleController:
    """
    Glowny kontroler cyklu pracy systemu SSI V5.
    
    Odpowiedzialnosc:
    - Wykrywanie aktualnej fazy cyklu
    - Zarzadzanie przejsciami miedzy fazami
    - Tworzenie kontekstu wykonania
    - Zapis i wznowienie stanu cyklu
    
    ZASADY:
    - Nie zastpuje istniejacego schedulera
    - Jest warstwa nadrzedna nad runtime_controller
    - Priorytet: stan danych > czas
    """
    
    # Domyslna sciezka do zapisu stanu
    DEFAULT_STATE_PATH = "D:/sts/aplikacjaTyperBetAi/SSI/v5/runtime/cycle_state.json"
    
    # Mapowanie faz do kontekstow wykonania
    PHASE_CONTEXTS: Dict[CyclePhase, ExecutionContext] = {
        CyclePhase.UNKNOWN: ExecutionContext(
            phase=CyclePhase.UNKNOWN,
            goal="wait_for_initialization",
            available_memory=[],
            allowed_actions=[],
            forbidden_actions=["number_generator", "bet", "trade"],
            priority="low"
        ),
        CyclePhase.RESULT_ANALYSIS: ExecutionContext(
            phase=CyclePhase.RESULT_ANALYSIS,
            goal="evaluate_previous_predictions_and_update_rankings",
            available_memory=[
                "prediction_history",
                "strategy_memory", 
                "result_feedback",
                "performance_metrics"
            ],
            allowed_actions=[
                "load_predictions",
                "compare_with_results",
                "evaluate_strategies",
                "update_rankings",
                "save_feedback",
                "analyze_performance"
            ],
            forbidden_actions=["number_generator", "bet", "trade", "generate_world"],
            priority="high",
            parameters={"max_iterations": 10, "confidence_threshold": 0.6}
        ),
        CyclePhase.WORLD_PREPARATION: ExecutionContext(
            phase=CyclePhase.WORLD_PREPARATION,
            goal="wait_for_world_database_ready",
            available_memory=["world_config", "database_status"],
            allowed_actions=[
                "check_world_status",
                "monitor_database",
                "validate_data"
            ],
            forbidden_actions=[
                "number_generator", 
                "bet", 
                "trade", 
                "generate_predictions",
                "run_strategy_evolution"
            ],
            priority="medium",
            parameters={"timeout_minutes": 60, "retry_interval": 30}
        ),
        CyclePhase.PREDICTION_WINDOW: ExecutionContext(
            phase=CyclePhase.PREDICTION_WINDOW,
            goal="generate_accurate_predictions_and_strategies",
            available_memory=[
                "world_database",
                "market_data",
                "odds_data",
                "strategy_memory",
                "agent_experience"
            ],
            allowed_actions=[
                "load_world_data",
                "analyze_matches",
                "run_exact_score_engine",
                "generate_predictions",
                "rank_strategies",
                "build_market_intelligence",
                "save_predictions"
            ],
            forbidden_actions=["number_generator", "bet", "trade"],
            priority="high",
            parameters={"max_predictions": 100, "min_confidence": 0.55}
        ),
        CyclePhase.STRATEGY_EVOLUTION: ExecutionContext(
            phase=CyclePhase.STRATEGY_EVOLUTION,
            goal="improve_strategies_through_experimentation",
            available_memory=[
                "prediction_history",
                "performance_data",
                "strategy_memory",
                "agent_knowledge"
            ],
            allowed_actions=[
                "test_strategy_variants",
                "analyze_behavior",
                "update_strategy_ranking",
                "save_experiments",
                "evolve_agents"
            ],
            forbidden_actions=["number_generator", "bet", "trade", "generate_world"],
            priority="high",
            parameters={"max_experiments": 20, "evolution_rate": 0.1}
        ),
        CyclePhase.OPTIMIZATION: ExecutionContext(
            phase=CyclePhase.OPTIMIZATION,
            goal="final_corrections_and_system_preparation",
            available_memory=[
                "daily_performance",
                "strategy_rankings",
                "system_state"
            ],
            allowed_actions=[
                "analyze_daily_results",
                "optimize_parameters",
                "prepare_feedback_cycle",
                "cleanup_temporary_data"
            ],
            forbidden_actions=["number_generator", "bet", "trade", "generate_world"],
            priority="medium",
            parameters={"optimization_depth": "final"}
        ),
        CyclePhase.WAITING: ExecutionContext(
            phase=CyclePhase.WAITING,
            goal="wait_for_next_trigger",
            available_memory=["system_status"],
            allowed_actions=["monitor_system", "check_triggers"],
            forbidden_actions=["number_generator", "bet", "trade", "generate_predictions"],
            priority="low"
        )
    }
    
    def __init__(
        self,
        state_path: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        clock: Optional[Any] = None
    ):
        """
        Inicjalizacja kontrolera cyklu.
        
        Args:
            state_path: Sciezka do pliku stanu cyklu
            logger: Logger do uzycia
            clock: Opcjonalny zegar symulacyjny (SimulationClock). 
                   Jesli przekazany,bedzie uzywany zamiast datetime.now()
        """
        self.state_path = state_path or self.DEFAULT_STATE_PATH
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._clock = clock  # Zegar symulacyjny (ETAP 5.3.4)
        
        # Stan cyklu
        self._cycle_state: Optional[CycleState] = None
        
        # Detektor fazy
        self._phase_detector = PhaseDetector(self.logger)
        
        # Inicjalizacja stanu
        self._initialize_state()
        
        self.logger.info(f"CycleController initialized. State path: {self.state_path}")
    
    def _initialize_state(self) -> None:
        """Inicjalizacja stanu cyklu (zaladuj lub utworz nowy)."""
        if os.path.exists(self.state_path):
            try:
                self._cycle_state = self.load_cycle_state()
                self.logger.info(f"Cycle state loaded. Current phase: {self._cycle_state.current_phase.value}")
            except Exception as e:
                self.logger.warning(f"Failed to load cycle state: {e}. Creating new state.")
                self._cycle_state = CycleState()
        else:
            self._cycle_state = CycleState()
            self.logger.info("Created new cycle state.")
    
    def detect_current_phase(
        self,
        world_state: Dict[str, Any],
        current_time: Optional[datetime] = None
    ) -> CyclePhase:
        """
        Wykrywa aktualna faze na podstawie stanu swiata.
        
        Priorytet czasu:
        1. current_time (jesli przekazany)
        2. self._clock.get_current_time() (jesli clock zostal przekazany)
        3. datetime.now() (domyslnie)
        
        Args:
            world_state: Slownik ze stanem swiata i systemu
            current_time: Aktualny czas (opcjonalny)
        
        Returns:
            CyclePhase: Wykryta faza
        """
        # Priorytet: current_time > clock > datetime.now()
        if current_time is None:
            if self._clock is not None:
                current_time = self._clock.get_current_time()
            else:
                current_time = datetime.now()
        
        phase = self._phase_detector.detect_phase(world_state, current_time)
        
        # Zaktualizuj stan cyklu (jesli faza sie zmienila)
        if self._cycle_state and phase != self._cycle_state.current_phase:
            old_phase = self._cycle_state.current_phase
            self._cycle_state.current_phase = phase
            self._cycle_state.add_phase_transition(old_phase, phase)
            self._cycle_state.last_update = datetime.now().isoformat()
            self.logger.info(f"Phase transition: {old_phase.value} -> {phase.value}")
        
        return phase
    
    def transition_to_phase(self, new_phase: CyclePhase) -> bool:
        """
        Wymusz przejscie do nowej fazy.
        
        Args:
            new_phase: Nowa faza do przejścia
        
        Returns:
            bool: Czy przejscie sie powiodlo
        """
        if not self._cycle_state:
            self.logger.error("Cycle state not initialized")
            return False
        
        old_phase = self._cycle_state.current_phase
        
        if old_phase == new_phase:
            self.logger.info(f"Already in phase: {new_phase.value}")
            return True
        
        # Zapisz przejscie
        self._cycle_state.add_phase_transition(old_phase, new_phase)
        self._cycle_state.current_phase = new_phase
        self._cycle_state.last_update = datetime.now().isoformat()
        
        # Oznaczenie starej fazy jako zakonczonej
        self._cycle_state.mark_phase_completed(old_phase)
        
        self.logger.info(f"Forced transition: {old_phase.value} -> {new_phase.value}")
        return True
    
    def get_execution_context(self) -> ExecutionContext:
        """
        Pobiera aktualny kontekst wykonania.
        
        Returns:
            ExecutionContext: Kontekst dla agentow
        """
        if not self._cycle_state:
            return self.PHASE_CONTEXTS[CyclePhase.UNKNOWN]
        
        return self.PHASE_CONTEXTS.get(
            self._cycle_state.current_phase,
            self.PHASE_CONTEXTS[CyclePhase.UNKNOWN]
        )
    
    def get_execution_context_for_phase(self, phase: CyclePhase) -> ExecutionContext:
        """
        Pobiera kontekst wykonania dla okreslonej fazy.
        
        Args:
            phase: Faza dla ktorej pobrac kontekst
        
        Returns:
            ExecutionContext: Kontekst dla fazy
        """
        return self.PHASE_CONTEXTS.get(phase, self.PHASE_CONTEXTS[CyclePhase.UNKNOWN])
    
    def get_cycle_state(self) -> Optional[CycleState]:
        """
        Pobiera aktualny stan cyklu.
        
        Returns:
            CycleState: Aktualny stan cyklu
        """
        return self._cycle_state
    
    def save_cycle_state(self, custom_path: Optional[str] = None) -> bool:
        """
        Zapisuje stan cyklu do pliku.
        
        Args:
            custom_path: Opcjonalna sciezka do zapisu
        
        Returns:
            bool: Czy zapis sie powiodl
        """
        if not self._cycle_state:
            self.logger.error("No cycle state to save")
            return False
        
        save_path = custom_path or self.state_path
        
        try:
            # Zapisz stan
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self._cycle_state.to_dict(), f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"Cycle state saved to: {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save cycle state: {e}")
            return False
    
    def load_cycle_state(self, custom_path: Optional[str] = None) -> CycleState:
        """
        Laczy stan cyklu z pliku.
        
        Args:
            custom_path: Opcjonalna sciezka do pliku
        
        Returns:
            CycleState: Zaladowany stan cyklu
        
        Raises:
            Exception: Jesli plik nie istnieje lub jest uszkodzony
        """
        load_path = custom_path or self.state_path
        
        if not os.path.exists(load_path):
            raise FileNotFoundError(f"Cycle state file not found: {load_path}")
        
        try:
            with open(load_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cycle_state = CycleState.from_dict(data)
            self.logger.info(f"Cycle state loaded from: {load_path}")
            return cycle_state
            
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON in cycle state file: {e}")
        except Exception as e:
            raise Exception(f"Failed to load cycle state: {e}")
    
    def resume_from_state(self) -> bool:
        """
        Wznawia prace z zapisanego stanu cyklu.
        
        Returns:
            bool: Czy wznowienie sie powiodlo
        """
        if not os.path.exists(self.state_path):
            self.logger.warning("No saved cycle state to resume from")
            return False
        
        try:
            self._cycle_state = self.load_cycle_state()
            self.logger.info(
                f"Resumed from cycle state. Phase: {self._cycle_state.current_phase.value}, "
                f"Completed: {self._cycle_state.completed_phases}"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resume from state: {e}")
            return False
    
    def reset_cycle(self) -> CycleState:
        """
        Resetuje stan cyklu (nowy cykl).
        
        Returns:
            CycleState: Nowy stan cyklu
        """
        self._cycle_state = CycleState()
        self.logger.info("Cycle state reset. New cycle started.")
        return self._cycle_state
    
    def update_cycle_metadata(self, key: str, value: Any) -> None:
        """
        Aktualizuje metadane stanu cyklu.
        
        Args:
            key: Klucz metadanych
            value: Wartosc
        """
        if self._cycle_state:
            self._cycle_state.metadata[key] = value
            self._cycle_state.last_update = datetime.now().isoformat()
    
    def get_phase_history(self) -> List[Dict[str, Any]]:
        """
        Pobiera historie przejsc miedzy fazami.
        
        Returns:
            List[Dict]: Historia przejsc
        """
        if self._cycle_state:
            return self._cycle_state.phase_transitions
        return []
    
    def is_in_phase(self, phase: CyclePhase) -> bool:
        """
        Sprawdza czy system jest w podanej fazie.
        
        Args:
            phase: Faza do sprawdzenia
        
        Returns:
            bool: Czy system jest w tej fazie
        """
        if self._cycle_state:
            return self._cycle_state.current_phase == phase
        return False


# =============================================================================
# FABRYKA: create_cycle_controller
# =============================================================================

def create_cycle_controller(
    state_path: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
    clock: Optional[Any] = None
) -> CycleController:
    """
    Tworzy nowa instancje CycleController.
    
    Args:
        state_path: Sciezka do pliku stanu
        logger: Logger do uzycia
        clock: Opcjonalny zegar symulacyjny (SimulationClock).
               Wykorzystywany w trybie symulacyjnym (ETAP 5.3.4)
    
    Returns:
        CycleController: Nowy kontroler cyklu
    """
    return CycleController(state_path=state_path, logger=logger, clock=clock)


# =============================================================================
# INICJALIZACJA MODULU
# =============================================================================

# Rejestracja w module runtime
# (Importy zostana dodane w __init__.py)
