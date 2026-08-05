#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for SSI V5 ETAP 0 KROK 3 - Complete Memory Integration
"""

import sys

# Add the project directory to Python path
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')


def test_imports():
    """Test importu wszystkich modułów"""
    print("[TEST 1] Import all modules")
    try:
        # Import wszystkich modułów
        from SSI_V5.agents.agent_runtime import AgentRuntime, AgentRuntimeManager
        from SSI_V5.agents.decision_engine import DecisionEngine, DecisionContext
        from SSI_V5.memory.memory_integration import MemoryIntegrationLayer
        from SSI_V5.agents.decision_memory_context import (
            MemoryContext, 
            EnhancedDecisionContext, 
            DecisionMemoryContextBuilder
        )
        print("[OK] All modules imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        return False


def test_agent_runtime_memory_integration():
    """Test memory integration in AgentRuntime"""
    print("\n[TEST 2] AgentRuntime memory integration")
    
    # Mock CollectiveMemoryManager
    class MockCollectiveMemoryManager:
        def store_memory(self, record):
            return f"doc_{hash(str(record)) % 1000}"
        def store_batch(self, records):
            return [f"batch_{i}" for i in range(len(records))]
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
        def build_agent_context(self, agent_id, current_situation, max_context_length=2000):
            return {
                'agent_id': agent_id,
                'situation': current_situation,
                'relevant_memories': [],
                'memory_count': 0
            }
        @property
        def _stats(self):
            return {'total_memories': 0}
    
    try:
        from SSI_V5.agents.agent_runtime import AgentRuntime
        from SSI_V5.memory.memory_integration import MemoryIntegrationLayer
        
        # Create mock CollectiveMemoryManager
        mock_manager = MockCollectiveMemoryManager()
        
        # Create MemoryIntegrationLayer
        memory_layer = MemoryIntegrationLayer(mock_manager)
        
        # Create AgentRuntime
        agent = AgentRuntime(
            agent_id="test_agent_01",
            name="TestAgent",
            mode="AUTO"
        )
        
        # Check if memory integration is disabled initially
        if not agent.is_memory_integration_enabled():
            print("[OK] Memory integration disabled initially")
        else:
            print("[FAIL] Memory integration should be disabled initially")
            return False
        
        # Set memory integration reference
        agent.set_memory_integration_reference(memory_layer)
        
        if agent.is_memory_integration_enabled():
            print("[OK] Memory integration enabled after setting reference")
            return True
        else:
            print("[FAIL] Memory integration not enabled after setting reference")
            return False
            
    except Exception as e:
        print(f"[FAIL] AgentRuntime memory integration test failed: {e}")
        return False


def test_agent_runtime_manager_memory_integration():
    """Test memory integration in AgentRuntimeManager"""
    print("\n[TEST 3] AgentRuntimeManager memory integration")
    
    # Mock CollectiveMemoryManager
    class MockCollectiveMemoryManager:
        def store_memory(self, record):
            return f"doc_{hash(str(record)) % 1000}"
        def store_batch(self, records):
            return [f"batch_{i}" for i in range(len(records))]
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
        def build_agent_context(self, agent_id, current_situation, max_context_length=2000):
            return {
                'agent_id': agent_id,
                'situation': current_situation,
                'relevant_memories': [],
                'memory_count': 0
            }
        @property
        def _stats(self):
            return {'total_memories': 0}
    
    try:
        from SSI_V5.agents.agent_runtime import AgentRuntimeManager
        from SSI_V5.agents.agent_runtime import AgentMode
        
        # Create manager
        manager = AgentRuntimeManager(
            pipeline_reference="test_pipeline",
            number_of_agents=2,  # Fewer agents for faster testing
            world_name="TEST_WORLD"
        )
        
        # Check if collective_manager is None initially
        if manager.collective_manager is None:
            print("[OK] collective_manager is None initially")
        else:
            print("[FAIL] collective_manager should be None initially")
            return False
        
        # Set collective manager
        mock_manager = MockCollectiveMemoryManager()
        manager.set_collective_manager_reference(mock_manager)
        
        if manager.collective_manager is mock_manager:
            print("[OK] collective_manager set successfully")
        else:
            print("[FAIL] collective_manager not set correctly")
            return False
        
        # Initialize manager (this should setup memory integration)
        init_result = manager.initialize()
        
        if init_result['status'] == 'success':
            print("[OK] AgentRuntimeManager initialized successfully")
            
            # Check if agents have memory integration enabled
            memory_integration_count = 0
            for agent_id, agent in manager.agents.items():
                if agent.is_memory_integration_enabled():
                    memory_integration_count += 1
            
            if memory_integration_count == len(manager.agents):
                print(f"[OK] All {memory_integration_count} agents have memory integration enabled")
                return True
            else:
                print(f"[FAIL] Only {memory_integration_count}/{len(manager.agents)} agents have memory integration")
                return False
        else:
            print(f"[FAIL] AgentRuntimeManager initialization failed: {init_result}")
            return False
            
    except Exception as e:
        print(f"[FAIL] AgentRuntimeManager memory integration test failed: {e}")
        return False


def test_decision_engine_memory_context():
    """Test DecisionEngine with memory context"""
    print("\n[TEST 4] DecisionEngine with memory context")
    
    try:
        from SSI_V5.agents.decision_engine import DecisionEngine
        from SSI_V5.agents.decision_memory_context import (
            MemoryContext, 
            EnhancedDecisionContext
        )
        from SSI_V5.agents.decision_engine import DecisionContext
        
        # Create DecisionEngine
        engine = DecisionEngine(agent_id="test_engine")
        
        # Test receive_contract with standard contract
        from SSI_V5.agents.agent_runtime import AgentContract
        import datetime
        
        contract = AgentContract(
            contract_id="test_contract_001",
            cycle_id="test_cycle_001",
            world_name="TestWorld",
            world_data={'team_a': 'TeamA', 'team_b': 'TeamB'},
            model_evaluation={'model_v1': {'accuracy': 0.85}},
            current_weights={'weight1': 0.6, 'weight2': 0.4},
            recommendations=[{'action': 'select', 'model': 'v1'}],
            timestamp=datetime.datetime.now()
        )
        
        # Test without memory context (should work as before)
        engine.receive_contract(contract)
        
        if engine.current_context and isinstance(engine.current_context, DecisionContext):
            print("[OK] DecisionEngine receives contract without memory context")
        else:
            print("[FAIL] DecisionEngine failed to process contract without memory context")
            return False
        
        # Test with memory context (EnhancedDecisionContext)
        memory_context = MemoryContext()
        memory_context.add_similar_case({'type': 'similar_match', 'similarity': 0.9})
        
        enhanced_context = EnhancedDecisionContext(
            original_context=DecisionContext(
                world_data=contract.world_data,
                model_info=contract.model_evaluation,
                weights=contract.current_weights,
                recommendations=contract.recommendations
            ),
            memory_context=memory_context
        )
        
        # This should work with the enhanced context
        engine.receive_contract(contract, memory_context=enhanced_context)
        
        if (engine.current_context and 
            hasattr(engine.current_context, 'memory_context') and
            engine.current_context.memory_context):
            print("[OK] DecisionEngine receives contract with memory context")
            return True
        else:
            print("[FAIL] DecisionEngine failed to process contract with memory context")
            return False
            
    except Exception as e:
        print(f"[FAIL] DecisionEngine memory context test failed: {e}")
        return False


def test_complete_flow():
    """Test complete flow: AgentRuntime -> Memory -> DecisionEngine"""
    print("\n[TEST 5] Complete integration flow")
    
    # Mock CollectiveMemoryManager
    class MockCollectiveMemoryManager:
        def __init__(self):
            self.storage = []
        def store_memory(self, record):
            doc_id = f"doc_{len(self.storage) + 1}"
            self.storage.append(record)
            return doc_id
        def store_batch(self, records):
            doc_ids = []
            for record in records:
                doc_id = f"doc_{len(self.storage) + 1}"
                self.storage.append(record)
                doc_ids.append(doc_id)
            return doc_ids
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
        def build_agent_context(self, agent_id, current_situation, max_context_length=2000):
            return {
                'agent_id': agent_id,
                'situation': current_situation,
                'relevant_memories': [],
                'memory_count': 0
            }
        @property
        def _stats(self):
            return {'total_memories': len(self.storage)}
    
    try:
        from SSI_V5.agents.agent_runtime import AgentRuntime, AgentRuntimeManager
        from SSI_V5.agents.agent_runtime import AgentContract
        from SSI_V5.memory.memory_integration import MemoryIntegrationLayer
        import datetime
        
        # Setup
        mock_manager = MockCollectiveMemoryManager()
        memory_layer = MemoryIntegrationLayer(mock_manager)
        
        # Create agent with memory integration
        agent = AgentRuntime(
            agent_id="test_flow_agent",
            name="FlowTestAgent",
            mode="AUTO"
        )
        agent.set_memory_integration_reference(memory_layer)
        
        # Create test contract
        contract = AgentContract(
            contract_id="flow_test_contract",
            cycle_id="flow_test_cycle",
            world_name="FlowTestWorld",
            world_data={'team_a': 'TeamA', 'team_b': 'TeamB'},
            model_evaluation={'model_v1': {'accuracy': 0.85}},
            current_weights={'weight1': 0.6, 'weight2': 0.4},
            recommendations=[{'action': 'select', 'model': 'v1'}],
            timestamp=datetime.datetime.now()
        )
        
        # Test the flow
        result = agent.receive_contract(contract)
        
        if result['status'] == 'success':
            print("[OK] Complete flow: contract processed successfully")
            
            # Check if decision was stored in collective memory
            if len(mock_manager.storage) > 0:
                print(f"[OK] Decision stored in collective memory: {len(mock_manager.storage)} records")
                return True
            else:
                print("[FAIL] No records stored in collective memory")
                return False
        else:
            print(f"[FAIL] Complete flow failed: {result}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"[FAIL] Complete flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_integration_stats():
    """Test memory integration statistics"""
    print("\n[TEST 6] Memory integration statistics")
    
    # Mock CollectiveMemoryManager
    class MockCollectiveMemoryManager:
        def store_memory(self, record):
            return f"doc_{hash(str(record)) % 1000}"
        def store_batch(self, records):
            return [f"batch_{i}" for i in range(len(records))]
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
        def build_agent_context(self, agent_id, current_situation, max_context_length=2000):
            return {
                'agent_id': agent_id,
                'situation': current_situation,
                'relevant_memories': [],
                'memory_count': 0
            }
        @property
        def _stats(self):
            return {'total_memories': 0}
    
    try:
        from SSI_V5.agents.agent_runtime import AgentRuntimeManager
        from SSI_V5.memory.memory_integration import MemoryIntegrationLayer
        
        # Setup
        mock_manager = MockCollectiveMemoryManager()
        
        # Create manager with memory integration
        manager = AgentRuntimeManager(
            pipeline_reference="stats_test",
            number_of_agents=1,
            world_name="STATS_TEST"
        )
        
        manager.set_collective_manager_reference(mock_manager)
        manager.initialize()
        
        # Get memory integration layer stats
        if manager.memory_integration_layer:
            stats = manager.memory_integration_layer.stats
            print(f"[OK] Memory integration stats: {stats}")
            return True
        else:
            print("[FAIL] Memory integration layer not available")
            return False
            
    except Exception as e:
        print(f"[FAIL] Memory integration stats test failed: {e}")
        return False


def run_all_tests():
    """Uruchamia wszystkie testy"""
    print("=" * 60)
    print("SSI V5 ETAP 0 KROK 3 - Complete Memory Integration Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_agent_runtime_memory_integration,
        test_agent_runtime_manager_memory_integration,
        test_decision_engine_memory_context,
        test_complete_flow,
        test_memory_integration_stats
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"WYNIK: {passed}/{total} testow zaliczonych")
    
    if passed == total:
        print("[SUCCESS] WSZYSTKIE TESTY ZALICZONE!")
        print("[OK] ETAP 0 KROK 3 - Complete Memory Integration works!")
        print("\nPrzeplyw:")
        print("AgentRuntime -> MemoryIntegrationLayer -> DecisionMemoryContext -> DecisionEngine")
    else:
        print("[WARNING] Niektore testy nie przebiegly pomyslnie")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)