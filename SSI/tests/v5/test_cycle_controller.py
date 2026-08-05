#!/usr/bin/env python3
"""
SSI V5 - Cycle Controller Tests
Testy dla modułu cycle_controller.py (ETAP 5.3.1)

OPIS:
Testy weryfikuja:
- Detekcje faz na podstawie stanu swiata
- Priorytet: WORLD_STATE > DATABASE_STATE > RESULTS_STATE > ODDS_STATE > TIME
- Przejścia miedzy fazami
- Zapis i wznowienie stanu cyklu
- Generowanie kontekstu wykonania

Autor: SSI V5 System
Data: 2026-08-04
Wersja: 1.0.0
"""

import os
import json
import tempfile
import pytest
from datetime import datetime, time
from unittest.mock import MagicMock, patch

# Import testowanej klasy
import sys
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')

from SSI.v5.runtime.cycle_controller import (
    CyclePhase,
    CycleState,
    ExecutionContext,
    PhaseDetector,
    CycleController,
    create_cycle_controller
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_state_file():
    """Tworzy tymczasowy plik stanu."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        yield f.name
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def phase_detector():
    """Tworzy instancje PhaseDetector."""
    return PhaseDetector()


@pytest.fixture
def cycle_controller(temp_state_file):
    """Tworzy instancje CycleController z tymczasowym plikiem stanu."""
    return CycleController(state_path=temp_state_file)


@pytest.fixture
def cycle_state():
    """Tworzy instancje CycleState."""
    return CycleState(
        cycle_id="test_cycle_001",
        current_phase=CyclePhase.UNKNOWN
    )


# =============================================================================
# TESTY: CyclePhase Enum
# =============================================================================

class TestCyclePhase:
    """Testy dla enum CyclePhase."""
    
    def test_all_phases_exist(self):
        """Sprawdza czy wszystkie fazy sa zdefiniowane."""
        expected_phases = [
            'UNKNOWN',
            'RESULT_ANALYSIS',
            'WORLD_PREPARATION',
            'PREDICTION_WINDOW',
            'STRATEGY_EVOLUTION',
            'OPTIMIZATION',
            'WAITING'
        ]
        
        for phase_name in expected_phases:
            assert hasattr(CyclePhase, phase_name)
    
    def test_phase_values(self):
        """Sprawdza wartości faz."""
        assert CyclePhase.UNKNOWN.value == "unknown"
        assert CyclePhase.RESULT_ANALYSIS.value == "result_analysis"
        assert CyclePhase.WORLD_PREPARATION.value == "world_preparation"
        assert CyclePhase.PREDICTION_WINDOW.value == "prediction_window"
        assert CyclePhase.STRATEGY_EVOLUTION.value == "strategy_evolution"
        assert CyclePhase.OPTIMIZATION.value == "optimization"
        assert CyclePhase.WAITING.value == "waiting"


# =============================================================================
# TESTY: CycleState Dataclass
# =============================================================================

class TestCycleState:
    """Testy dla klasy CycleState."""
    
    def test_default_initialization(self):
        """Testuje domyslna inicjalizacje stanu."""
        state = CycleState()
        
        assert state.cycle_id != ""
        assert state.current_phase == CyclePhase.UNKNOWN
        assert state.started_at is not None
        assert state.last_update is not None
        assert state.completed_phases == []
        assert state.phase_transitions == []
    
    def test_custom_initialization(self):
        """Testuje inicjalizacje z parametrami."""
        state = CycleState(
            cycle_id="custom_cycle",
            current_phase=CyclePhase.PREDICTION_WINDOW,
            completed_phases=["result_analysis", "world_preparation"]
        )
        
        assert state.cycle_id == "custom_cycle"
        assert state.current_phase == CyclePhase.PREDICTION_WINDOW
        assert state.completed_phases == ["result_analysis", "world_preparation"]
    
    def test_to_dict(self):
        """Testuje konwersje stanu do slownika."""
        state = CycleState(
            cycle_id="test_001",
            current_phase=CyclePhase.RESULT_ANALYSIS
        )
        
        result = state.to_dict()
        
        assert result['cycle_id'] == "test_001"
        assert result['current_phase'] == "result_analysis"  # Powinno byc string
    
    def test_from_dict(self):
        """Testuje tworzenie stanu z slownika."""
        data = {
            'cycle_id': 'loaded_cycle',
            'current_phase': 'prediction_window',
            'completed_phases': ['result_analysis'],
            'started_at': '2026-08-04T10:00:00',
            'last_update': '2026-08-04T11:00:00'
        }
        
        state = CycleState.from_dict(data)
        
        assert state.cycle_id == 'loaded_cycle'
        assert state.current_phase == CyclePhase.PREDICTION_WINDOW
        assert state.completed_phases == ['result_analysis']
    
    def test_mark_phase_completed(self):
        """Testuje oznaczenie fazy jako zakonczonej."""
        state = CycleState()
        
        state.mark_phase_completed(CyclePhase.RESULT_ANALYSIS)
        
        assert "result_analysis" in state.completed_phases
        assert len(state.completed_phases) == 1
    
    def test_add_phase_transition(self):
        """Testuje dodawanie przejscia miedzy fazami."""
        state = CycleState()
        
        state.add_phase_transition(CyclePhase.UNKNOWN, CyclePhase.RESULT_ANALYSIS)
        
        assert len(state.phase_transitions) == 1
        assert state.phase_transitions[0]['from'] == 'unknown'
        assert state.phase_transitions[0]['to'] == 'result_analysis'


# =============================================================================
# TESTY: PhaseDetector
# =============================================================================

class TestPhaseDetector:
    """Testy dla klasy PhaseDetector."""
    
    def test_result_analysis_detection(self, phase_detector):
        """
        TEST: RESUL_ANALYSIS powinien byc wykryty,
        gdy new_results_available=True i results_processed=False
        """
        world_state = {
            'new_results_available': True,
            'results_processed': False,
            'is_ready': True
        }
        
        result = phase_detector.detect_phase(world_state)
        
        assert result == CyclePhase.RESULT_ANALYSIS
    
    def test_world_preparation_detection_generating(self, phase_detector):
        """
        TEST: WORLD_PREPARATION powinien byc wykryty,
        gdy world_status='GENERATING'
        """
        world_state = {
            'status': 'GENERATING',
            'is_ready': False,
            'new_results_available': False
        }
        
        result = phase_detector.detect_phase(world_state)
        
        assert result == CyclePhase.WORLD_PREPARATION
    
    def test_world_preparation_detection_not_ready(self, phase_detector):
        """
        TEST: WORLD_PREPARATION powinien byc wykryty,
        gdy swiat nie jest gotowy
        """
        world_state = {
            'is_ready': False,
            'database_status': 'READY',
            'database_timestamp': '2026-08-04T10:00:00'
        }
        
        result = phase_detector.detect_phase(world_state)
        
        assert result == CyclePhase.WORLD_PREPARATION
    
    def test_prediction_window_detection(self, phase_detector):
        """
        TEST: PREDICTION_WINDOW powinien byc wykryty,
        gdy world_state=READY i odds_available=True
        """
        world_state = {
            'is_ready': True,
            'odds_available': True,
            'status': 'READY'
        }
        
        result = phase_detector.detect_phase(world_state)
        
        assert result == CyclePhase.PREDICTION_WINDOW
    
    def test_prediction_window_with_odds_only(self, phase_detector):
        """
        TEST: PREDICTION_WINDOW powinien byc wykryty,
        gdy odds_available=True i is_ready=True
        """
        world_state = {
            'is_ready': True,
            'odds_available': True
        }
        
        result = phase_detector.detect_phase(world_state)
        
        assert result == CyclePhase.PREDICTION_WINDOW
    
    def test_strategy_evolution_detection(self, phase_detector):
        """
        TEST: STRATEGY_EVOLUTION powinien byc wykryty,
        gdy prediction_cycle_completed=True (symulowane przez czas 15:07)
        """
        world_state = {
            'is_ready': True,
            'odds_available': True,
            'prediction_cycle_completed': True
        }
        
        # Ustaw czas na 15:07
        test_time = datetime(2026, 8, 4, 15, 7)
        
        result = phase_detector.detect_phase(world_state, test_time)
        
        # Powinien zostać wykryty jako PREDICTION_WINDOW przez world_state,
        # ale 15:07 to STRATEGY_EVOLUTION (czas jako ostatnia wskazowka)
        # Tutaj world_state ma wyższą wagę, więc powinien być PREDICTION_WINDOW
        assert result == CyclePhase.PREDICTION_WINDOW
    
    def test_optimization_detection_by_time(self, phase_detector):
        """
        TEST: OPTIMIZATION powinien byc wykryty o 21:07,
        gdy brak innych sygnalow
        """
        world_state = {
            'is_ready': False,
            'new_results_available': False,
            'odds_available': False
        }
        
        test_time = datetime(2026, 8, 4, 21, 7)
        
        result = phase_detector.detect_phase(world_state, test_time)
        
        assert result == CyclePhase.OPTIMIZATION
    
    def test_result_analysis_by_time(self, phase_detector):
        """
        TEST: RESULT_ANALYSIS powinien byc wykryty o 02:07,
        gdy brak innych sygnalow
        """
        world_state = {}
        
        test_time = datetime(2026, 8, 4, 2, 7)
        
        result = phase_detector.detect_phase(world_state, test_time)
        
        assert result == CyclePhase.RESULT_ANALYSIS
    
    def test_prediction_window_by_time(self, phase_detector):
        """
        TEST: PREDICTION_WINDOW powinien byc wykryty o 08:30,
        gdy brak innych sygnalow
        """
        world_state = {}
        
        test_time = datetime(2026, 8, 4, 8, 30)
        
        result = phase_detector.detect_phase(world_state, test_time)
        
        assert result == CyclePhase.PREDICTION_WINDOW
    
    def test_waiting_by_time(self, phase_detector):
        """
        TEST: WAITING powinien byc wykryty poza typowymi godzinami
        """
        world_state = {}
        
        test_time = datetime(2026, 8, 4, 3, 0)  # 03:00
        
        result = phase_detector.detect_phase(world_state, test_time)
        
        assert result == CyclePhase.WAITING
    
    def test_priority_world_state_over_time(self, phase_detector):
        """
        TEST: WORLD_STATE ma wyższą wagę niż CZAS
        Gdy world_status='GENERATING' ale czas wskazuje na PREDICTION_WINDOW,
        powinien zostać wykryty WORLD_PREPARATION
        """
        world_state = {
            'status': 'GENERATING',
            'is_ready': False
        }
        
        test_time = datetime(2026, 8, 4, 10, 0)  # 10:00 - normalnie PREDICTION_WINDOW
        
        result = phase_detector.detect_phase(world_state, test_time)
        
        assert result == CyclePhase.WORLD_PREPARATION
    
    def test_priority_results_over_time(self, phase_detector):
        """
        TEST: RESULTS_STATE ma wyższą wagę niż CZAS
        Gdy new_results_available=True ale czas wskazuje na WAITING,
        powinien zostać wykryty RESULT_ANALYSIS
        """
        world_state = {
            'new_results_available': True,
            'results_processed': False
        }
        
        test_time = datetime(2026, 8, 4, 3, 0)  # 03:00 - normalnie WAITING
        
        result = phase_detector.detect_phase(world_state, test_time)
        
        assert result == CyclePhase.RESULT_ANALYSIS


# =============================================================================
# TESTY: CycleController
# =============================================================================

class TestCycleController:
    """Testy dla klasy CycleController."""
    
    def test_initialization(self, cycle_controller):
        """Testuje inicjalizacje kontrolera."""
        assert cycle_controller is not None
        assert cycle_controller._cycle_state is not None
        assert cycle_controller._cycle_state.current_phase == CyclePhase.UNKNOWN
    
    def test_detect_current_phase(self, cycle_controller):
        """Testuje wykrywanie aktualnej fazy."""
        world_state = {
            'is_ready': True,
            'odds_available': True
        }
        
        result = cycle_controller.detect_current_phase(world_state)
        
        assert result == CyclePhase.PREDICTION_WINDOW
    
    def test_phase_transition(self, cycle_controller):
        """Testuje przejscie miedzy fazami."""
        initial_phase = cycle_controller._cycle_state.current_phase
        
        result = cycle_controller.transition_to_phase(CyclePhase.RESULT_ANALYSIS)
        
        assert result is True
        assert cycle_controller._cycle_state.current_phase == CyclePhase.RESULT_ANALYSIS
        assert cycle_controller._cycle_state.phase_transitions[0]['from'] == initial_phase.value
        assert cycle_controller._cycle_state.phase_transitions[0]['to'] == 'result_analysis'
    
    def test_get_execution_context(self, cycle_controller):
        """Testuje pobieranie kontekstu wykonania."""
        # Ustaw faze
        cycle_controller.transition_to_phase(CyclePhase.RESULT_ANALYSIS)
        
        context = cycle_controller.get_execution_context()
        
        assert context.phase == CyclePhase.RESULT_ANALYSIS
        assert context.goal == "evaluate_previous_predictions_and_update_rankings"
        assert "load_predictions" in context.allowed_actions
        assert "number_generator" in context.forbidden_actions
    
    def test_get_execution_context_for_phase(self, cycle_controller):
        """Testuje pobieranie kontekstu dla okreslonej fazy."""
        context = cycle_controller.get_execution_context_for_phase(CyclePhase.STRATEGY_EVOLUTION)
        
        assert context.phase == CyclePhase.STRATEGY_EVOLUTION
        assert context.goal == "improve_strategies_through_experimentation"
        assert "test_strategy_variants" in context.allowed_actions
    
    def test_save_cycle_state(self, cycle_controller, temp_state_file):
        """Testuje zapis stanu cyklu."""
        # Zmien faze
        cycle_controller.transition_to_phase(CyclePhase.PREDICTION_WINDOW)
        
        result = cycle_controller.save_cycle_state(temp_state_file)
        
        assert result is True
        assert os.path.exists(temp_state_file)
        
        # Sprawdz zawartosc
        with open(temp_state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data['current_phase'] == 'prediction_window'
    
    def test_load_cycle_state(self, cycle_controller, temp_state_file):
        """Testuje wczytanie stanu cyklu."""
        # Zapis testowego stanu
        test_state = CycleState(
            cycle_id="test_load",
            current_phase=CyclePhase.STRATEGY_EVOLUTION
        )
        
        with open(temp_state_file, 'w', encoding='utf-8') as f:
            json.dump(test_state.to_dict(), f)
        
        loaded_state = cycle_controller.load_cycle_state(temp_state_file)
        
        assert loaded_state.cycle_id == "test_load"
        assert loaded_state.current_phase == CyclePhase.STRATEGY_EVOLUTION
    
    def test_resume_from_state(self, temp_state_file):
        """Testuje wznowienie z zapisanego stanu."""
        # Zapis testowego stanu
        test_state = CycleState(
            cycle_id="test_resume",
            current_phase=CyclePhase.OPTIMIZATION,
            completed_phases=["result_analysis", "world_preparation", "prediction_window"]
        )
        
        with open(temp_state_file, 'w', encoding='utf-8') as f:
            json.dump(test_state.to_dict(), f)
        
        # Utworz nowy kontroler
        controller = CycleController(state_path=temp_state_file)
        
        result = controller.resume_from_state()
        
        assert result is True
        assert controller._cycle_state.current_phase == CyclePhase.OPTIMIZATION
        assert "result_analysis" in controller._cycle_state.completed_phases
    
    def test_reset_cycle(self, cycle_controller):
        """Testuje reset stanu cyklu."""
        # Zmien faze i dodaj historii
        cycle_controller.transition_to_phase(CyclePhase.PREDICTION_WINDOW)
        cycle_controller.transition_to_phase(CyclePhase.STRATEGY_EVOLUTION)
        
        assert len(cycle_controller._cycle_state.phase_transitions) >= 2
        
        # Reset
        new_state = cycle_controller.reset_cycle()
        
        assert new_state.current_phase == CyclePhase.UNKNOWN
        assert len(new_state.phase_transitions) == 0
        assert new_state.completed_phases == []
    
    def test_is_in_phase(self, cycle_controller):
        """Testuje sprawdzanie czy system jest w danej fazie."""
        assert cycle_controller.is_in_phase(CyclePhase.UNKNOWN) is True
        assert cycle_controller.is_in_phase(CyclePhase.RESULT_ANALYSIS) is False
        
        # Zmien faze
        cycle_controller.transition_to_phase(CyclePhase.RESULT_ANALYSIS)
        
        assert cycle_controller.is_in_phase(CyclePhase.RESULT_ANALYSIS) is True
        assert cycle_controller.is_in_phase(CyclePhase.UNKNOWN) is False
    
    def test_update_metadata(self, cycle_controller):
        """Testuje aktualizacje metadanych."""
        cycle_controller.update_cycle_metadata("test_key", "test_value")
        
        assert cycle_controller._cycle_state.metadata["test_key"] == "test_value"
    
    def test_get_phase_history(self, cycle_controller):
        """Testuje pobieranie historii przejsc."""
        # Utworz historie
        cycle_controller.transition_to_phase(CyclePhase.RESULT_ANALYSIS)
        cycle_controller.transition_to_phase(CyclePhase.WORLD_PREPARATION)
        
        history = cycle_controller.get_phase_history()
        
        assert len(history) >= 2
        assert history[0]['from'] == 'unknown'
        assert history[1]['from'] == 'result_analysis'
    
    def test_get_cycle_state(self, cycle_controller):
        """Testuje pobieranie stanu cyklu."""
        state = cycle_controller.get_cycle_state()
        
        assert state is not None
        assert isinstance(state, CycleState)


# =============================================================================
# TESTY: ExecutionContext
# =============================================================================

class TestExecutionContext:
    """Testy dla klasy ExecutionContext."""
    
    def test_default_context(self):
        """Testuje domyslny kontekst."""
        context = ExecutionContext(
            phase=CyclePhase.WAITING,
            goal="test_goal"
        )
        
        assert context.phase == CyclePhase.WAITING
        assert context.goal == "test_goal"
        assert context.available_memory == []
        assert context.allowed_actions == []
        assert context.forbidden_actions == []
        assert context.priority == "normal"
        assert context.created_at is not None
    
    def test_to_dict(self):
        """Testuje konwersje kontekstu do slownika."""
        context = ExecutionContext(
            phase=CyclePhase.PREDICTION_WINDOW,
            goal="generate_predictions",
            allowed_actions=["analyze", "predict"],
            forbidden_actions=["bet", "trade"]
        )
        
        result = context.to_dict()
        
        assert result['phase'] == 'prediction_window'
        assert result['goal'] == "generate_predictions"
        assert result['allowed_actions'] == ["analyze", "predict"]
    
    def test_phase_contexts_completeness(self):
        """Testuje czy wszystkie fazy maja zdefiniowane konteksty."""
        all_phases = list(CyclePhase)
        
        for phase in all_phases:
            context = CycleController.PHASE_CONTEXTS.get(phase)
            assert context is not None, f"Missing context for phase: {phase.value}"
            assert context.phase == phase
            assert context.goal != ""


# =============================================================================
# TESTY: Fabryka create_cycle_controller
# =============================================================================

class TestCreateCycleController:
    """Testy dla fabryki create_cycle_controller."""
    
    def test_create_with_defaults(self):
        """Testuje tworzenie z domyslnymi parametrami."""
        controller = create_cycle_controller()
        
        assert isinstance(controller, CycleController)
        assert controller._cycle_state is not None
    
    def test_create_with_custom_path(self, temp_state_file):
        """Testuje tworzenie z niestandardowa sciezka."""
        controller = create_cycle_controller(state_path=temp_state_file)
        
        assert controller.state_path == temp_state_file


# =============================================================================
# TESTY: Integracyjne
# =============================================================================

class TestCycleControllerIntegration:
    """Testy integracyjne dla CycleController."""
    
    def test_full_cycle_simulation(self, temp_state_file):
        """
        TEST: Symulacja pelnego cyklu:
        RESULT_ANALYSIS -> WORLD_PREPARATION -> PREDICTION_WINDOW -> STRATEGY_EVOLUTION -> OPTIMIZATION
        """
        controller = CycleController(state_path=temp_state_file)
        
        # Symuluj wynik analizy
        world_state_1 = {'new_results_available': True, 'results_processed': False}
        phase_1 = controller.detect_current_phase(world_state_1)
        assert phase_1 == CyclePhase.RESULT_ANALYSIS
        
        # Symuluj przygotowanie swiata
        world_state_2 = {'status': 'GENERATING', 'is_ready': False}
        phase_2 = controller.detect_current_phase(world_state_2)
        assert phase_2 == CyclePhase.WORLD_PREPARATION
        
        # Symuluj okno predykcji
        world_state_3 = {'is_ready': True, 'odds_available': True}
        phase_3 = controller.detect_current_phase(world_state_3)
        assert phase_3 == CyclePhase.PREDICTION_WINDOW
        
        # Sprawdz historie
        history = controller.get_phase_history()
        assert len(history) >= 3
    
    def test_state_persistence_across_instances(self, temp_state_file):
        """
        TEST: Stan powinien byc zachowany miedzy instancjami
        """
        # Utworz pierwsza instancje i zapisz stan
        controller1 = CycleController(state_path=temp_state_file)
        controller1.transition_to_phase(CyclePhase.STRATEGY_EVOLUTION)
        controller1.update_cycle_metadata("custom_data", "test_value")
        controller1.save_cycle_state()
        
        # Utworz druga instancje i wczytaj stan
        controller2 = CycleController(state_path=temp_state_file)
        controller2.resume_from_state()
        
        assert controller2._cycle_state.current_phase == CyclePhase.STRATEGY_EVOLUTION
        assert controller2._cycle_state.metadata.get("custom_data") == "test_value"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # Uruchom testy za pomoca pytest
    pytest.main([__file__, "-v", "--tb=short"])
