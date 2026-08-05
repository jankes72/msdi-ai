#!/usr/bin/env python3
"""
Test script to verify MemoryIntegrator and MemoryEcosystem changes.
Tests the architectural changes for ETAP 1.2.7.3.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from SSI_V5.memory.ecosystem import MemoryEcosystem
from SSI_V5.memory.integrator import MemoryIntegrator, IntegrationResult
from SSI_V5.memory.stores.base_store import MemoryRecord
from SSI_V5.memory.stores.experiment_store import ExperimentMemoryStore


def test_record_types_mapping():
    """Test that RECORD_TYPES mapping is correct."""
    print("Test 1: RECORD_TYPES mapping")
    
    integrator = MemoryIntegrator(memory_ecosystem=None)
    
    # Check that cycle maps to system_memory
    assert integrator.RECORD_TYPES.get("cycle") == "system_memory", \
        f"cycle should map to system_memory, got {integrator.RECORD_TYPES.get('cycle')}"
    
    # Check that phase_transition maps to system_memory
    assert integrator.RECORD_TYPES.get("phase_transition") == "system_memory", \
        f"phase_transition should map to system_memory, got {integrator.RECORD_TYPES.get('phase_transition')}"
    
    # Check that knowledge maps to knowledge_record
    assert integrator.RECORD_TYPES.get("knowledge") == "knowledge_record", \
        f"knowledge should map to knowledge_record, got {integrator.RECORD_TYPES.get('knowledge')}"
    
    print("  [OK] RECORD_TYPES mapping is correct")


def test_ecosystem_type_to_store_map():
    """Test that TYPE_TO_STORE_MAP includes system_memory and knowledge_record."""
    print("\nTest 2: TYPE_TO_STORE_MAP")
    
    # Check the class variable directly
    assert "system_memory" in MemoryEcosystem.TYPE_TO_STORE_MAP, \
        "system_memory should be in TYPE_TO_STORE_MAP"
    
    assert "knowledge_record" in MemoryEcosystem.TYPE_TO_STORE_MAP, \
        "knowledge_record should be in TYPE_TO_STORE_MAP"
    
    # Both should map to experiment_store temporarily
    assert MemoryEcosystem.TYPE_TO_STORE_MAP["system_memory"] == "experiment_store", \
        "system_memory should map to experiment_store"
    
    assert MemoryEcosystem.TYPE_TO_STORE_MAP["knowledge_record"] == "experiment_store", \
        "knowledge_record should map to experiment_store"
    
    print("  [OK] TYPE_TO_STORE_MAP is correct")


def test_cycle_record_creation():
    """Test that cycle records don't have experiment_id."""
    print("\nTest 3: Cycle record creation")
    
    ecosystem = MemoryEcosystem()
    integrator = MemoryIntegrator(memory_ecosystem=ecosystem)
    
    # Create a minimal cycle data
    cycle_data = {
        'cycle_id': 'test_cycle_001',
        'status': 'completed',
        'duration': 10.5,
        'steps': {'step1': {'status': 'ok'}},
        'timestamp': '2026-08-04T10:00:00'
    }
    
    # Process the cycle
    result = integrator.process_cycle_result(cycle_data)
    
    assert result.success, f"process_cycle_result failed: {result.errors}"
    assert len(result.memory_ids) > 0, "No memory IDs returned"
    
    # Check the created record
    memory_id = result.memory_ids[0]
    record = ecosystem.get(memory_id)
    
    assert record is not None, "Record not found in ecosystem"
    assert record.type == "system_memory", f"Record type should be system_memory, got {record.type}"
    
    # Check that it does NOT have experiment_id
    assert 'experiment_id' not in record.content, \
        "Cycle record should NOT have experiment_id"
    
    assert 'cycle_id' in record.content, \
        "Cycle record should have cycle_id"
    assert record.content['cycle_id'] == 'test_cycle_001', \
        "Cycle ID should match input"
    
    print("  [OK] Cycle record created without experiment_id")


def test_phase_transition_record_creation():
    """Test that phase transition records don't have experiment_id."""
    print("\nTest 4: Phase transition record creation")
    
    ecosystem = MemoryEcosystem()
    integrator = MemoryIntegrator(memory_ecosystem=ecosystem)
    
    # Process a phase transition
    result = integrator.process_phase_transition(
        from_phase="world",
        to_phase="observation",
        context={'test': 'value'}
    )
    
    assert result.success, f"process_phase_transition failed: {result.errors}"
    assert len(result.memory_ids) > 0, "No memory IDs returned"
    
    # Check the created record
    memory_id = result.memory_ids[0]
    record = ecosystem.get(memory_id)
    
    assert record is not None, "Record not found in ecosystem"
    assert record.type == "system_memory", f"Record type should be system_memory, got {record.type}"
    
    # Check that it does NOT have experiment_id
    assert 'experiment_id' not in record.content, \
        "Phase transition record should NOT have experiment_id"
    
    assert 'transition_id' in record.content, \
        "Phase transition record should have transition_id"
    assert record.content['from_phase'] == 'world', \
        "from_phase should match input"
    assert record.content['to_phase'] == 'observation', \
        "to_phase should match input"
    
    print("  [OK] Phase transition record created without experiment_id")


def test_experiment_record_still_works():
    """Test that experiment records still work and require experiment_id."""
    print("\nTest 5: Experiment record validation")
    
    ecosystem = MemoryEcosystem()
    
    # Create a valid experiment record
    record = MemoryRecord.create(
        content={
            'experiment_id': 'test_exp_001',
            'hypothesis': {'title': 'Test hypothesis'},
            'result': {'outcome': 'confirming'}
        },
        memory_type='experiment_memory',
        source='test'
    )
    
    # This should save successfully
    memory_id = ecosystem.save(record)
    assert memory_id is not None, "Should be able to save valid experiment record"
    
    # Retrieve and verify
    retrieved = ecosystem.get(memory_id)
    assert retrieved is not None, "Should retrieve saved record"
    assert retrieved.type == "experiment_memory", "Type should be preserved"
    assert retrieved.content['experiment_id'] == 'test_exp_001', "experiment_id should be preserved"
    
    print("  [OK] Experiment records still work correctly")


def test_system_memory_record_in_experiment_store():
    """Test that system_memory records can be saved to experiment_store."""
    print("\nTest 6: system_memory in experiment_store")
    
    # Create an experiment store
    store = ExperimentMemoryStore()
    
    # Create a system_memory record WITHOUT experiment_id
    record = MemoryRecord.create(
        content={
            'cycle_id': 'test_cycle_002',
            'status': 'completed'
        },
        memory_type='system_memory',
        source='test'
    )
    
    # This should validate successfully because the record type is system_memory, not experiment_memory
    try:
        memory_id = store.save(record)
        print(f"  [OK] system_memory record saved to ExperimentMemoryStore with ID: {memory_id}")
    except ValueError as e:
        print(f"  ✗ Failed to save system_memory record: {e}")
        raise


def test_base_store_does_not_overwrite_type():
    """Test that BaseMemoryStore doesn't overwrite record type."""
    print("\nTest 7: BaseMemoryStore type preservation")
    
    from SSI_V5.memory.stores.base_store import BaseMemoryStore
    
    # Create a simple test store
    class TestStore(BaseMemoryStore):
        def _validate_record(self, record):
            return True
        
        def _get_memory_type(self):
            return "test_memory"
    
    store = TestStore()
    
    # Create a record with a specific type
    record = MemoryRecord.create(
        content={'test': 'data'},
        memory_type='system_memory',
        source='test'
    )
    
    # Save it
    memory_id = store.save(record)
    
    # Retrieve and check type
    retrieved = store.get(memory_id)
    assert retrieved.type == "system_memory", \
        f"Record type should be preserved as system_memory, got {retrieved.type}"
    
    print("  [OK] BaseMemoryStore preserves record type")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Testing Memory Architecture Changes for ETAP 1.2.7.3")
    print("=" * 60)
    
    try:
        test_record_types_mapping()
        test_ecosystem_type_to_store_map()
        test_cycle_record_creation()
        test_phase_transition_record_creation()
        test_experiment_record_still_works()
        test_system_memory_record_in_experiment_store()
        test_base_store_does_not_overwrite_type()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! [OK]")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n[FAILED] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
