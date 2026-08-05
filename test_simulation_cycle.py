# SSI V5 - Test Symulacji Cyklu 24H
# =====================================
#
# ETAP: 5.3.4 - Symulacja pelnego cyklu 24H
# Data: 2026-08-04
#
# Odpowiedzialnosc:
# - Testowanie detekcji faz przez CycleController
# - Weryfikacja przejsc miedzy fazami w symulowanym czasie
# - Sprawdzenie integracji SimulationClock -> CycleController
#
# ZASADY:
# - TYLKO test symulacyjny
# - NIE uruchamia prawdziwych agentow
# - NIE wplywa na produkcje
#
# Uruchomienie:
# python test_simulation_cycle.py
#
# Autor: SSI V5 System
# Wersja: 1.0.0

import sys
import os
from datetime import datetime

# Dodanie sciezek do importow
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SSI', 'V5', 'runtime'))

from simulation_clock import SimulationClock, create_simulation_clock
from simulation_world_state import SimulatedWorldState, create_simulated_world_state_for_time
from cycle_controller import CycleController, CyclePhase, create_cycle_controller


class PhaseDetectionTest:
    """Test detekcji faz z uzyciem SimulationClock."""
    
    def __init__(self):
        self.clock = create_simulation_clock()
        self.controller = create_cycle_controller(clock=self.clock)
        self.test_results = []
    
    def test_phase_detection(self, hour: int, minute: int, expected_phase: CyclePhase) -> bool:
        """
        Test detekcji fazy dla danego czasu.
        
        Args:
            hour: Godzina
            minute: Minuta
            expected_phase: Oczekiwana faza
        
        Returns:
            Czy test sie powiodl
        """
        # Ustaw czas symulacji
        self.clock.set_time(datetime(2026, 8, 4, hour, minute, 0))
        
        # Utworz symulowany stan swiata dla tego czasu
        world_state = create_simulated_world_state_for_time(hour, minute).to_dict()
        
        # Wykryj faze
        detected_phase = self.controller.detect_current_phase(world_state)
        
        # Sprawdz wynik
        success = detected_phase == expected_phase
        
        time_str = f"{hour:02d}:{minute:02d}"
        result = {
            'time': time_str,
            'expected': expected_phase.value,
            'detected': detected_phase.value,
            'success': success,
            'world_state': world_state
        }
        
        self.test_results.append(result)
        
        if success:
            print(f"[PASS] {time_str} -> {detected_phase.value} (expected: {expected_phase.value})")
        else:
            print(f"[FAIL] {time_str} -> {detected_phase.value} (expected: {expected_phase.value})")
            print(f"       World state: {world_state}")
        
        return success


def run_phase_detection_tests():
    """Uruchomienie testow detekcji faz."""
    print("=" * 60)
    print("SSI V5 - PHASE DETECTION SIMULATION TESTS")
    print("=" * 60)
    print()
    
    tester = PhaseDetectionTest()
    
    # Kluczowe momenty w cyklu 24H (dopasowane do _check_time_based)
    test_cases = [
        # 02:07 - RESULT_ANALYSIS (nowe wyniki dostepne)
        (2, 7, CyclePhase.RESULT_ANALYSIS),
        # 08:05 - WORLD_PREPARATION (swiat w przygotowaniu)
        (8, 5, CyclePhase.WORLD_PREPARATION),
        # 10:00 - PREDICTION_WINDOW (swiat gotowy, kursy dostepne)
        (10, 0, CyclePhase.PREDICTION_WINDOW),
        # 11:00 - PREDICTION_WINDOW ( Европ okna predykcyjnego)
        (11, 0, CyclePhase.PREDICTION_WINDOW),
        # 12:00 - PREDICTION_WINDOW (koniec okna predykcyjnego)
        (12, 0, CyclePhase.PREDICTION_WINDOW),
        # 15:07 - STRATEGY_EVOLUTION (zgodnie z _check_time_based)
        (15, 7, CyclePhase.STRATEGY_EVOLUTION),
        # 21:07 - OPTIMIZATION (zgodnie z _check_time_based)
        (21, 7, CyclePhase.OPTIMIZATION),
        # 22:00 - WAITING (oczekiwanie na nasteppe wyniki)
        (22, 0, CyclePhase.WAITING),
    ]
    
    for hour, minute, expected_phase in test_cases:
        tester.test_phase_detection(hour, minute, expected_phase)
        print()
    
    return tester.test_results


def run_simulation_24h():
    """Symulacja pelnego 24H cyklu z uzyciem SimulationClock."""
    print("=" * 60)
    print("SSI V5 - 24H SIMULATION (Time-based)")
    print("=" * 60)
    print()
    
    clock = create_simulation_clock()
    controller = create_cycle_controller(clock=clock)
    
    # Kluczowe momenty czasu do testowania (dopasowane do _check_time_based)
    test_scenarios = [
        (2, 7, CyclePhase.RESULT_ANALYSIS),
        (8, 5, CyclePhase.WORLD_PREPARATION),
        (10, 0, CyclePhase.PREDICTION_WINDOW),
        (12, 0, CyclePhase.PREDICTION_WINDOW),
        (15, 7, CyclePhase.STRATEGY_EVOLUTION),
        (21, 7, CyclePhase.OPTIMIZATION),
        (22, 0, CyclePhase.WAITING),
    ]
    
    results = []
    
    for hour, minute, expected_phase in test_scenarios:
        clock.set_time(datetime(2026, 8, 4, hour, minute, 0))
        
        world_state = create_simulated_world_state_for_time(hour, minute).to_dict()
        detected_phase = controller.detect_current_phase(world_state)
        
        time_str = f"{hour:02d}:{minute:02d}"
        success = detected_phase == expected_phase
        results.append({
            'time': time_str,
            'expected': expected_phase.value,
            'detected': detected_phase.value,
            'success': success
        })
        
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {time_str}: {detected_phase.value}")
    
    print()
    return results


def generate_test_report(all_results: list) -> str:
    """Generowanie raportu z testow."""
    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results if r['success'])
    failed_tests = total_tests - passed_tests
    
    report = []
    report.append("=" * 60)
    report.append("SSI V5 SIMULATION TEST REPORT")
    report.append("=" * 60)
    report.append(f"Total tests: {total_tests}")
    report.append(f"Passed: {passed_tests}")
    report.append(f"Failed: {failed_tests}")
    report.append("")
    
    if failed_tests > 0:
        report.append("FAILED TESTS:")
        for r in all_results:
            if not r['success']:
                report.append(f"  {r['time']}: Expected {r['expected']}, got {r['detected']}")
    else:
        report.append("[SUCCESS] ALL TESTS PASSED!")
    
    return "\n".join(report)


def main():
    """Glowna funkcja testowa."""
    print("Starting SSI V5 Simulation Cycle Tests...")
    print()
    
    all_results = []
    
    # Test 1: Detekcja faz
    results1 = run_phase_detection_tests()
    all_results.extend(results1)
    
    # Test 2: Symulacja 24H
    results2 = run_simulation_24h()
    all_results.extend(results2)
    
    # Generowanie raportu
    report = generate_test_report(all_results)
    print(report)
    
    # Zwroc kod wyjscia
    failed = sum(1 for r in all_results if not r['success'])
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
