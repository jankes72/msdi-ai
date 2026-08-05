#!/usr/bin/env python3
"""
Bootstrap Integration Test for ETAP 1.2.7.3
Tests the integration of IFC, MemoryEcosystem, MemoryIntegrator with ProductionLauncher.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all imports work correctly."""
    print("Test 1: Imports")
    
    try:
        from SSI_V5.runtime.start_ssi import ProductionLauncher
        from SSI_V5.ifc.registry import IFCRegistry
        from SSI_V5.ifc.message import IFCMessage, MessageType
        from SSI_V5.memory.ecosystem import MemoryEcosystem
        from SSI_V5.memory.integrator import MemoryIntegrator
        from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
        print("  [OK] All imports successful")
        return True
    except ImportError as e:
        print(f"  [FAILED] Import error: {e}")
        return False


def test_production_launcher_bootstrap():
    """Test ProductionLauncher bootstrap with memory components."""
    print("\nTest 2: ProductionLauncher Bootstrap")
    
    try:
        from SSI_V5.runtime.start_ssi import ProductionLauncher, CONFIG_PRODUCTION
        
        # Create launcher
        launcher = ProductionLauncher(config=CONFIG_PRODUCTION)
        
        # Check initial state
        assert launcher.ifc is None, "IFC should be None before initialize"
        assert launcher.memory_ecosystem is None, "MemoryEcosystem should be None before initialize"
        assert launcher.memory_integrator is None, "MemoryIntegrator should be None before initialize"
        assert launcher.pipeline is None, "Pipeline should be None before initialize"
        
        print("  [OK] Initial state is clean")
        
        # Initialize
        init_result = launcher.initialize()
        
        assert init_result['status'] == 'success', f"Initialization failed: {init_result}"
        
        # Check components exist
        assert launcher.ifc is not None, "IFC should exist after initialize"
        assert launcher.memory_ecosystem is not None, "MemoryEcosystem should exist after initialize"
        assert launcher.memory_integrator is not None, "MemoryIntegrator should exist after initialize"
        assert launcher.pipeline is not None, "Pipeline should exist after initialize"
        
        print("  [OK] All components created successfully")
        
        # Check types
        from SSI_V5.ifc.registry import IFCRegistry
        from SSI_V5.memory.ecosystem import MemoryEcosystem
        from SSI_V5.memory.integrator import MemoryIntegrator
        from SSI_V5.core.pipeline import SSIPipeline
        
        assert isinstance(launcher.ifc, IFCRegistry), "IFC should be IFCRegistry instance"
        assert isinstance(launcher.memory_ecosystem, MemoryEcosystem), "MemoryEcosystem should be MemoryEcosystem instance"
        assert isinstance(launcher.memory_integrator, MemoryIntegrator), "MemoryIntegrator should be MemoryIntegrator instance"
        assert isinstance(launcher.pipeline, SSIPipeline), "Pipeline should be SSIPipeline instance"
        
        print("  [OK] All components have correct types")
        
        # Check IFC registrations
        assert launcher.ifc.exists("ifc_registry"), "IFC should be registered in itself"
        assert launcher.ifc.exists("memory_ecosystem"), "MemoryEcosystem should be registered in IFC"
        assert launcher.ifc.exists("memory_integrator"), "MemoryIntegrator should be registered in IFC"
        assert launcher.ifc.exists("pipeline"), "Pipeline should be registered in IFC"
        
        print("  [OK] All components registered in IFC")
        
        # Check Pipeline has references
        assert launcher.pipeline.ifc is launcher.ifc, "Pipeline should have IFC reference"
        assert launcher.pipeline.memory_ecosystem is launcher.memory_ecosystem, "Pipeline should have MemoryEcosystem reference"
        
        print("  [OK] Pipeline has correct references")
        
        # Check MemoryEcosystem has stores
        stores = launcher.memory_ecosystem.list_stores()
        assert len(stores) > 0, "MemoryEcosystem should have stores"
        assert "model_store" in stores, "MemoryEcosystem should have model_store"
        assert "agent_store" in stores, "MemoryEcosystem should have agent_store"
        assert "experiment_store" in stores, "MemoryEcosystem should have experiment_store"
        
        print("  [OK] MemoryEcosystem has all required stores")
        
        # Shutdown
        shutdown_result = launcher.shutdown()
        assert shutdown_result['status'] in ['success', 'error'], f"Shutdown failed: {shutdown_result}"
        
        print("  [OK] Shutdown completed")
        
        return True
        
    except Exception as e:
        print(f"  [FAILED] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ifc_communication():
    """Test IFC communication between components."""
    print("\nTest 3: IFC Communication")
    
    try:
        from SSI_V5.runtime.start_ssi import ProductionLauncher
        from SSI_V5.ifc.message import IFCMessage, MessageType
        
        launcher = ProductionLauncher()
        launcher.initialize()
        
        # Test IFC message routing
        message = IFCMessage(
            source="test",
            target="memory_ecosystem",
            message_type=MessageType.EVENT,
            payload={"test": "value"}
        )
        
        # Route message through IFC
        routed = launcher.ifc.route(message)
        assert routed is not None, "Message should be routed"
        
        print("  [OK] IFC message routing works")
        
        # Test getting component from IFC
        memory_ecosystem = launcher.ifc.get("memory_ecosystem")
        assert memory_ecosystem is launcher.memory_ecosystem, "IFC get should return correct component"
        
        print("  [OK] IFC component retrieval works")
        
        launcher.shutdown()
        return True
        
    except Exception as e:
        print(f"  [FAILED] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_ecosystem_health():
    """Test MemoryEcosystem health and statistics."""
    print("\nTest 4: MemoryEcosystem Health")
    
    try:
        from SSI_V5.runtime.start_ssi import ProductionLauncher
        
        launcher = ProductionLauncher()
        launcher.initialize()
        
        # Check health
        health = launcher.memory_ecosystem.health()
        assert health['status'] == 'healthy', f"MemoryEcosystem should be healthy: {health}"
        
        print("  [OK] MemoryEcosystem is healthy")
        
        # Check statistics
        stats = launcher.memory_ecosystem.statistics()
        assert 'total_stores' in stats, "Statistics should include total_stores"
        assert stats['total_stores'] >= 3, "Should have at least 3 stores"
        
        print("  [OK] MemoryEcosystem statistics are correct")
        
        launcher.shutdown()
        return True
        
    except Exception as e:
        print(f"  [FAILED] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline_memory_access():
    """Test that Pipeline can access MemoryEcosystem."""
    print("\nTest 5: Pipeline Memory Access")
    
    try:
        from SSI_V5.runtime.start_ssi import ProductionLauncher
        from SSI_V5.memory.stores.base_store import MemoryRecord
        
        launcher = ProductionLauncher()
        launcher.initialize()
        
        # Pipeline should have access to memory_ecosystem
        pipeline = launcher.pipeline
        assert pipeline.memory_ecosystem is not None, "Pipeline should have MemoryEcosystem"
        
        # Test saving a record through pipeline's memory_ecosystem
        record = MemoryRecord.create(
            content={"test": "data", "experiment_id": "test_exp_001"},
            memory_type="experiment_memory",
            source="bootstrap_test"
        )
        
        memory_id = pipeline.memory_ecosystem.save(record)
        assert memory_id is not None, "Should be able to save record"
        
        # Verify we can retrieve it
        retrieved = pipeline.memory_ecosystem.get(memory_id)
        assert retrieved is not None, "Should be able to retrieve record"
        assert retrieved.content["test"] == "data", "Retrieved record should have correct content"
        
        print("  [OK] Pipeline can access and use MemoryEcosystem")
        
        launcher.shutdown()
        return True
        
    except Exception as e:
        print(f"  [FAILED] {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all bootstrap integration tests."""
    print("=" * 60)
    print("Bootstrap Integration Test - ETAP 1.2.7.3")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("ProductionLauncher Bootstrap", test_production_launcher_bootstrap()))
    results.append(("IFC Communication", test_ifc_communication()))
    results.append(("MemoryEcosystem Health", test_memory_ecosystem_health()))
    results.append(("Pipeline Memory Access", test_pipeline_memory_access()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "[OK]" if result else "[FAILED]"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")
    print("=" * 60)
    
    if failed == 0:
        print("\nALL BOOTSTRAP INTEGRATION TESTS PASSED! [OK]")
        return 0
    else:
        print(f"\n{failed} TEST(S) FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
