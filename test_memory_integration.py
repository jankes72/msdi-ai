#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for SSI V5 ETAP 0 KROK 1 - Memory Integration Layer
"""

import sys

# Add the project directory to Python path
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')


def test_import():
    """Test importu modulu"""
    print("[TEST 1] Import module")
    try:
        from SSI_V5.memory.memory_integration import MemoryIntegrationLayer, MemoryIntegrationError
        print("[OK] Import successful")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        return False


def test_class_creation():
    """Test tworzenia klasy MemoryIntegrationLayer"""
    print("\n[TEST 2] Class creation")
    
    try:
        from SSI_V5.memory.memory_integration import MemoryIntegrationLayer, MemoryIntegrationError
        # This should fail with None
        layer = MemoryIntegrationLayer(None)
        print("[FAIL] Should have failed with None CollectiveMemoryManager")
        return False
    except MemoryIntegrationError as e:
        print(f"[OK] Correctly failed with None: {e}")
    except Exception as e:
        print(f"[FAIL] Wrong exception type: {e}")
        return False
    
    # Create a mock CollectiveMemoryManager
    class MockCollectiveMemoryManager:
        def __init__(self):
            self.storage = []
            self._stats = {'total_memories': 0}
        
        def store_memory(self, record):
            doc_id = f"doc_{len(self.storage) + 1}"
            self.storage.append(record)
            self._stats['total_memories'] += 1
            return doc_id
        
        def store_batch(self, records):
            doc_ids = []
            for record in records:
                doc_id = f"doc_{len(self.storage) + 1}"
                self.storage.append(record)
                doc_ids.append(doc_id)
                self._stats['total_memories'] += 1
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
    
    try:
        mock_manager = MockCollectiveMemoryManager()
        layer = MemoryIntegrationLayer(mock_manager)
        print("[OK] MemoryIntegrationLayer created successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Creation failed: {e}")
        return False


def test_initialization():
    """Test inicializacji warstwy"""
    print("\n[TEST 3] Layer initialization")
    
    class MockCollectiveMemoryManager:
        def store_memory(self, record):
            return "doc_1"
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
        def build_agent_context(self, agent_id, current_situation, max_context_length=2000):
            return {'agent_id': agent_id, 'situation': current_situation}
    
    try:
        from SSI_V5.memory.memory_integration import MemoryIntegrationLayer
        mock_manager = MockCollectiveMemoryManager()
        layer = MemoryIntegrationLayer(mock_manager)
        
        init_result = layer.initialize()
        if init_result['status'] == 'success':
            print("[OK] Initialization successful")
            print(f"   Collective Manager Type: {init_result.get('collective_manager_type', 'Unknown')}")
            return True
        else:
            print(f"[FAIL] Initialization failed: {init_result}")
            return False
    except Exception as e:
        print(f"[FAIL] Initialization test failed: {e}")
        return False


def test_store_decision():
    """Test zapisu decyzji"""
    print("\n[TEST 4] Store decision")
    
    class MockCollectiveMemoryManager:
        def __init__(self):
            self.storage = []
        
        def store_memory(self, record):
            doc_id = f"dec_{len(self.storage) + 1}"
            self.storage.append(record)
            return doc_id
        
        def store_batch(self, records):
            return [f"batch_{i}" for i in range(len(records))]
        
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
        
        def build_agent_context(self, agent_id, current_situation, max_context_length=2000):
            return {'agent_id': agent_id, 'situation': current_situation}
    
    try:
        from SSI_V5.memory.memory_integration import MemoryIntegrationLayer
        mock_manager = MockCollectiveMemoryManager()
        layer = MemoryIntegrationLayer(mock_manager)
        
        decision_data = {
            'decision_id': 'test_decision_001',
            'decision_type': 'model_selection',
            'agent_id': 'agent_01',
            'parameters': {'model_name': 'v2', 'confidence': 0.85},
            'context': {'world_state': 'active'},
            'confidence': 0.75,
            'priority': 1
        }
        
        result = layer.store_decision(
            agent_id='agent_01',
            decision_data=decision_data
        )
        
        if result['status'] == 'success':
            print("[OK] Decision stored successfully")
            print(f"   Decision ID: {result['decision_id']}")
            print(f"   Document ID: {result['document_id']}")
            print(f"   Store time: {result['store_time_ms']:.2f}ms")
            return True
        else:
            print(f"[FAIL] Store decision failed: {result}")
            return False
    except Exception as e:
        print(f"[FAIL] Store decision test failed: {e}")
        return False


def test_retrieve_context():
    """Test pobierania kontekstu"""
    print("\n[TEST 5] Retrieve context")
    
    class MockCollectiveMemoryManager:
        def store_memory(self, record):
            return "doc_1"
        def store_batch(self, records):
            return []
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
        def build_agent_context(self, agent_id, current_situation, max_context_length=2000):
            return {
                'agent_id': agent_id,
                'situation': current_situation,
                'relevant_memories': [],
                'memory_count': 0,
                'memory_context': 'Test context',
                'avg_similarity': 0.0
            }
    
    try:
        from SSI_V5.memory.memory_integration import MemoryIntegrationLayer
        mock_manager = MockCollectiveMemoryManager()
        layer = MemoryIntegrationLayer(mock_manager)
        
        current_situation = {
            'world_name': 'PremierLeague',
            'phase': 'prediction_window',
            'available_models': ['model_v1', 'model_v2'],
            'risk_level': 'medium'
        }
        
        result = layer.retrieve_context(
            agent_id='agent_01',
            current_situation=current_situation,
            top_k=3,
            min_similarity=0.6
        )
        
        if result['status'] == 'success':
            print("[OK] Context retrieved successfully")
            print(f"   Agent ID: {result['agent_id']}")
            print(f"   Memory count: {result['memory_count']}")
            print(f"   Retrieval time: {result['retrieval_time_ms']:.2f}ms")
            return True
        else:
            print(f"[FAIL] Retrieve context failed: {result}")
            return False
    except Exception as e:
        print(f"[FAIL] Retrieve context test failed: {e}")
        return False


def test_error_handling():
    """Test obslugi bledow"""
    print("\n[TEST 6] Error handling")
    
    class MockCollectiveMemoryManager:
        def store_memory(self, record):
            return "doc_1"
        def store_batch(self, records):
            return []
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
        def build_agent_context(self, agent_id, current_situation, max_context_length=2000):
            return {'agent_id': agent_id}
    
    try:
        from SSI_V5.memory.memory_integration import MemoryIntegrationLayer
        mock_manager = MockCollectiveMemoryManager()
        layer = MemoryIntegrationLayer(mock_manager)
        
        # Test with invalid input
        result = layer.store_decision(
            agent_id='',  # Invalid
            decision_data={}
        )
        
        if result['status'] == 'error':
            print("[OK] Error handling works correctly")
            print(f"   Error: {result['error']}")
            return True
        else:
            print(f"[FAIL] Error handling failed: {result}")
            return False
    except Exception as e:
        print(f"[FAIL] Error handling test failed: {e}")
        return False


def run_all_tests():
    """Uruchamia wszystkie testy"""
    print("=" * 50)
    print("SSI V5 ETAP 0 KROK 1 - Memory Integration Layer Tests")
    print("=" * 50)
    
    tests = [
        test_import,
        test_class_creation,
        test_initialization,
        test_store_decision,
        test_retrieve_context,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"WYNIK: {passed}/{total} testow zaliczonych")
    
    if passed == total:
        print("[SUCCESS] WSZYSTKIE TESTY ZALICZONE!")
        print("[OK] memory_integration.py jest gotowy do uzycia")
    else:
        print("[WARNING] Niektore testy nie przebiegly pomyslnie")
    
    print("=" * 50)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)