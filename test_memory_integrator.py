#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test integracyjny MemoryIntegrator - ETAP 1.2.7.3"""

from SSI_V5.memory import (
    MemoryEcosystem, MemoryIntegrator, IntegrationResult,
    MemoryRecord
)


def test_integrator_initialization():
    """Test 1: Inicjalizacja MemoryIntegrator."""
    print('Test 1: MemoryIntegrator - Inicjalizacja')
    
    # Tworzenie ekosystemu i integratora
    ecosystem = MemoryEcosystem()
    integrator = MemoryIntegrator(memory_ecosystem=ecosystem)
    
    print(f'  Integrator utworzony: {integrator is not None}')
    assert integrator is not None
    
    print(f'  MemoryEcosystem: {integrator.memory_ecosystem is ecosystem}')
    assert integrator.memory_ecosystem is ecosystem
    
    # Statystyki początkowe
    stats = integrator.get_statistics()
    print(f'  Statystyki poczatkowe: {stats}')
    assert stats['total_integrations'] == 0
    assert stats['successful_integrations'] == 0
    
    print('  [OK] Test 1 zaliczony')


def test_experiment_result_processing():
    """Test 2: Przetwarzanie wyniku eksperymentu."""
    print('\nTest 2: Przetwarzanie eksperymentu')
    
    ecosystem = MemoryEcosystem()
    integrator = MemoryIntegrator(memory_ecosystem=ecosystem)
    
    # Dane eksperymentu
    exp_data = {
        "experiment_id": "exp_test_001",
        "hypothesis": {
            "title": "Test hypothesis",
            "category": "market_behavior"
        },
        "result": {
            "outcome": "confirming",
            "confidence": 0.85
        },
        "conclusion": {
            "verdict": "accept_hypothesis"
        }
    }
    
    # Przetwarzanie
    result = integrator.process_experiment_result(exp_data)
    
    print(f'  Success: {result.success}')
    print(f'  Memory IDs: {result.memory_ids}')
    print(f'  Record count: {result.record_count}')
    print(f'  Errors: {result.errors}')
    
    assert result.success is True
    assert len(result.memory_ids) == 1
    assert result.record_count == 1
    assert len(result.errors) == 0
    
    # Sprawdzenie, czy rekord trafił do ekosystemu
    memory_id = result.memory_ids[0]
    retrieved = ecosystem.get(memory_id)
    print(f'  Rekord zapisany: {retrieved is not None}')
    assert retrieved is not None
    assert retrieved.content['experiment_id'] == 'exp_test_001'
    assert retrieved.content['hypothesis']['title'] == 'Test hypothesis'
    
    print('  [OK] Test 2 zaliczony')


def test_agent_decision_processing():
    """Test 3: Przetwarzanie decyzji agenta."""
    print('\nTest 3: Przetwarzanie decyzji agenta')
    
    ecosystem = MemoryEcosystem()
    integrator = MemoryIntegrator(memory_ecosystem=ecosystem)
    
    # Dane decyzji
    decision_data = {
        "agent_id": "agent_test_001",
        "decision_id": "dec_001",
        "type": "BTTS_Yes",
        "confidence": 0.75,
        "context": {"match": "TeamA vs TeamB"},
        "outcome": {"result": "BTTS_Yes", "profit": 2.0},
        "success": True
    }
    
    # Przetwarzanie
    result = integrator.process_agent_decision(decision_data)
    
    print(f'  Success: {result.success}')
    print(f'  Memory ID: {result.memory_ids[0] if result.memory_ids else "none"}')
    print(f'  Experience type: {result.record_count}')
    
    assert result.success is True
    assert len(result.memory_ids) == 1
    assert result.record_count == 1
    
    # Sprawdzenie rekordu
    memory_id = result.memory_ids[0]
    retrieved = ecosystem.get(memory_id)
    assert retrieved is not None
    assert retrieved.content['agent_id'] == 'agent_test_001'
    assert retrieved.content['decision_type'] == 'BTTS_Yes'
    assert retrieved.content['experience_type'] == 'success'  # Powinno być klasyfikowane
    
    print('  [OK] Test 3 zaliczony')


def test_cycle_result_processing():
    """Test 4: Przetwarzanie wyniku cyklu."""
    print('\nTest 4: Przetwarzanie cyklu')
    
    ecosystem = MemoryEcosystem()
    integrator = MemoryIntegrator(memory_ecosystem=ecosystem)
    
    # Dane cyklu
    cycle_data = {
        "cycle_id": "cycle_test_001",
        "timestamp": "2026-08-04T12:00:00",
        "status": "completed",
        "duration": 45.5,
        "steps": {
            "world_generation": {"status": "success", "duration": 10.0},
            "agent_execution": {"status": "success", "duration": 25.0},
            "memory_update": {"status": "success", "duration": 5.0}
        },
        "agent_data": {
            "agent_id": "cycle_agent_001",
            "decisions": [
                {
                    "decision_id": "dec_cycle_001",
                    "type": "Over25_Yes",
                    "confidence": 0.80,
                    "success": True,
                    "profit": 1.5
                }
            ]
        },
        "experiment_data": {
            "experiment_id": "cycle_exp_001",
            "result": {"outcome": "confirming"}
        }
    }
    
    # Przetwarzanie
    result = integrator.process_cycle_result(cycle_data)
    
    print(f'  Success: {result.success}')
    print(f'  Memory IDs count: {len(result.memory_ids)}')
    print(f'  Record count: {result.record_count}')
    print(f'  Errors: {result.errors}')
    
    assert result.success is True
    assert result.record_count >= 3  # cycle_record + agent_decision + experiment
    assert len(result.memory_ids) >= 3
    
    # Sprawdzenie, że potrzebne rekordy istnieją
    for memory_id in result.memory_ids:
        retrieved = ecosystem.get(memory_id)
        assert retrieved is not None
    
    print('  [OK] Test 4 zaliczony')


def test_phase_transition_processing():
    """Test 5: Przetwarzanie przejścia fazy."""
    print('\nTest 5: Przetwarzanie przejscia fazy')
    
    ecosystem = MemoryEcosystem()
    integrator = MemoryIntegrator(memory_ecosystem=ecosystem)
    
    # Przetwarzanie przejścia
    result = integrator.process_phase_transition(
        from_phase="RESULT_ANALYSIS",
        to_phase="WORLD_PREPARATION",
        context={"trigger": "new_results_available"}
    )
    
    print(f'  Success: {result.success}')
    print(f'  Memory ID: {result.memory_ids[0] if result.memory_ids else "none"}')
    
    assert result.success is True
    assert len(result.memory_ids) == 1
    
    # Sprawdzenie rekordu
    memory_id = result.memory_ids[0]
    retrieved = ecosystem.get(memory_id)
    assert retrieved is not None
    assert retrieved.content['from_phase'] == 'RESULT_ANALYSIS'
    assert retrieved.content['to_phase'] == 'WORLD_PREPARATION'
    
    print('  [OK] Test 5 zaliczony')


def test_integrator_statistics():
    """Test 6: Statystyki integratora."""
    print('\nTest 6: Statystyki integratora')
    
    ecosystem = MemoryEcosystem()
    integrator = MemoryIntegrator(memory_ecosystem=ecosystem)
    
    # Wyzerowanie statystyk
    integrator.reset_statistics()
    stats = integrator.get_statistics()
    print(f'  Statystyki poczatkowe: {stats}')
    assert stats['total_integrations'] == 0
    
    # Wykonanie kilku integracji
    for i in range(3):
        integrator.process_experiment_result({
            "experiment_id": f"exp_stats_{i}",
            "result": {"outcome": "confirming"}
        })
    
    stats = integrator.get_statistics()
    print(f'  Statystyki po 3 integracjach: {stats}')
    assert stats['total_integrations'] == 3
    assert stats['successful_integrations'] == 3
    assert stats['total_records_created'] == 3
    
    # Historia integracji
    history = integrator.get_integration_history()
    print(f'  Historia: {len(history)} wpisow')
    assert len(history) == 3
    
    # Wyczyszczenie historii
    integrator.clear_history()
    assert len(integrator.get_integration_history()) == 0
    
    print('  [OK] Test 6 zaliczony')


def test_integrator_with_ifc():
    """Test 7: Integrator z IFC."""
    print('\nTest 7: Integrator z IFC')
    
    from SSI_V5.ifc import IFCRegistry
    
    # Tworzenie IFC i ekosystemu
    ifc = IFCRegistry()
    ecosystem = MemoryEcosystem()
    
    # Tworzenie integratora z IFC
    integrator = MemoryIntegrator(
        memory_ecosystem=ecosystem,
        ifc=ifc
    )
    
    # Sprawdzenie rejestracji w IFC
    assert ifc.exists("memory_integrator") is True
    print(f'  Zarejestrowany w IFC: [OK]')
    
    # Przetwarzanie z IFC
    result = integrator.process_experiment_result({
        "experiment_id": "exp_ifc_test"
    })
    
    print(f'  Integracja z IFC: {result.success}')
    assert result.success is True
    
    # Sprawdzenie, czy integrator jest w IFC
    integrator_from_ifc = ifc.get("memory_integrator")
    assert integrator_from_ifc is integrator
    print(f'  Pobrany z IFC: [OK]')
    
    # Zamknięcie
    integrator.shutdown()
    assert ifc.exists("memory_integrator") is False
    print(f'  Wyrejestrowany z IFC: [OK]')
    
    print('  [OK] Test 7 zaliczony')


def test_agent_experience_classification():
    """Test 8: Klasyfikacja doświadczenia agenta."""
    print('\nTest 8: Klasyfikacja doswiadczen agenta')
    
    ecosystem = MemoryEcosystem()
    integrator = MemoryIntegrator(memory_ecosystem=ecosystem)
    
    # Test sukces
    result1 = integrator.process_agent_decision({
        "agent_id": "test_agent",
        "success": True,
        "profit": 5.0
    })
    record1 = ecosystem.get(result1.memory_ids[0])
    print(f'  Sukces -> {record1.content["experience_type"]}')
    assert record1.content['experience_type'] == 'success'
    
    # Test porażka (profit < 0)
    result2 = integrator.process_agent_decision({
        "agent_id": "test_agent",
        "success": False,
        "profit": -2.0
    })
    record2 = ecosystem.get(result2.memory_ids[0])
    print(f'  Porazka -> {record2.content["experience_type"]}')
    assert record2.content['experience_type'] == 'failure'
    
    # Test error
    result3 = integrator.process_agent_decision({
        "agent_id": "test_agent",
        "outcome": {"result": "error"}
    })
    record3 = ecosystem.get(result3.memory_ids[0])
    print(f'  Error -> {record3.content["experience_type"]}')
    assert record3.content['experience_type'] == 'error'
    
    # Test decision (domyślne)
    result4 = integrator.process_agent_decision({
        "agent_id": "test_agent",
        "type": "some_decision"
    })
    record4 = ecosystem.get(result4.memory_ids[0])
    print(f'  Decision -> {record4.content["experience_type"]}')
    assert record4.content['experience_type'] == 'decision'
    
    print('  [OK] Test 8 zaliczony')


def test_error_handling():
    """Test 9: Obsługa błędów."""
    print('\nTest 9: Obsluga bledow')
    
    ecosystem = MemoryEcosystem()
    integrator = MemoryIntegrator(memory_ecosystem=ecosystem)
    
    # Próba przetwarzania pustych danych
    result = integrator.process_experiment_result({})
    print(f'  Puste dane: success={result.success}')
    assert result.success is True  # Powinno się powieść (puste dane są akceptowalne)
    
    # Próba z nieoczekiwanym typem
    result2 = integrator.process_agent_decision({
        "agent_id": "test",
        "unknown_field": "value"
    })
    print(f'  Nieznane pole: success={result2.success}')
    assert result2.success is True  # Powinno się powieść (dodatkowe pola są ignorowane)
    
    print('  [OK] Test 9 zaliczony')


if __name__ == '__main__':
    print('=' * 60)
    print('MEMORYINTEGRATOR - TESTY INTEGRACYJNE (ETAP 1.2.7.3)')
    print('=' * 60)
    
    try:
        test_integrator_initialization()
        test_experiment_result_processing()
        test_agent_decision_processing()
        test_cycle_result_processing()
        test_phase_transition_processing()
        test_integrator_statistics()
        test_integrator_with_ifc()
        test_agent_experience_classification()
        test_error_handling()
        
        print('\n' + '=' * 60)
        print('[SUCCESS] WSZYSTKIE TESTY MEMORYINTEGRATOR ZALICZONE!')
        print('=' * 60)
        
    except AssertionError as e:
        print(f'\n[FAIL] TEST NIEZALICZONY: {e}')
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f'\n[ERROR] BLAAD: {e}')
        import traceback
        traceback.print_exc()
        exit(1)
