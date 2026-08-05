#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for SSI V5 ETAP 0 KROK 4 - RAG Retrieval Layer
"""

import sys

# Add the project directory to Python path
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')


def test_imports():
    """Test importu RAG Retrieval modułu"""
    print("[TEST 1] Import RAG Retrieval module")
    try:
        from SSI_V5.memory.collective_memory.rag_retrieval import RAGRetrieval, RAGRetrievalError
        from SSI_V5.memory.collective_memory import RAGRetrieval, RAGRetrievalError
        print("[OK] RAGRetrieval module imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        return False


def test_rag_retrieval_initialization():
    """Test inicializacji RAGRetrieval"""
    print("\n[TEST 2] RAGRetrieval initialization")
    
    # Mock VectorIndex
    class MockVectorIndex:
        def search(self, query, top_k=5, min_similarity=0.0):
            return [
                {'id': 'vec_1', 'content': {'type': 'decision', 'action': 'select_model'}, 'similarity': 0.95},
                {'id': 'vec_2', 'content': {'type': 'observation', 'data': 'test'}, 'similarity': 0.88}
            ]
    
    # Mock CollectiveMemoryManager
    class MockCollectiveMemoryManager:
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
    
    try:
        from SSI_V5.memory.collective_memory.rag_retrieval import RAGRetrieval
        
        # Tworzenie mocków
        mock_vector_index = MockVectorIndex()
        mock_collective_manager = MockCollectiveMemoryManager()
        
        # Inicjalizacja RAGRetrieval
        rag_retrieval = RAGRetrieval(mock_vector_index, mock_collective_manager)
        
        # Test bez inicjalizacji
        if not rag_retrieval.is_initialized:
            print("[OK] RAGRetrieval not initialized by default")
        else:
            print("[FAIL] RAGRetrieval should not be initialized by default")
            return False
        
        # Inicjalizacja
        init_result = rag_retrieval.initialize()
        
        if init_result['status'] == 'success' and rag_retrieval.is_initialized:
            print("[OK] RAGRetrieval initialized successfully")
            return True
        else:
            print(f"[FAIL] Initialization failed: {init_result}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retrieve_knowledge():
    """Test retrieve_knowledge method"""
    print("\n[TEST 3] retrieve_knowledge method")
    
    # Mock VectorIndex
    class MockVectorIndex:
        def search(self, query, top_k=5, min_similarity=0.0):
            return [
                {
                    'id': 'vec_1', 
                    'content': {'type': 'decision', 'action': 'select_model', 'outcome': 'success'},
                    'similarity': 0.95,
                    'type': 'decision'
                },
                {
                    'id': 'vec_2', 
                    'content': {'type': 'observation', 'data': 'test'},
                    'similarity': 0.88,
                    'type': 'observation'
                },
                {
                    'id': 'vec_3', 
                    'content': {'type': 'risk_assessment', 'level': 'high'},
                    'similarity': 0.75,
                    'type': 'risk_assessment'
                }
            ]
    
    # Mock CollectiveMemoryManager
    class MockCollectiveMemoryManager:
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
    
    try:
        from SSI_V5.memory.collective_memory.rag_retrieval import RAGRetrieval
        
        # Tworzenie mocków i RAGRetrieval
        mock_vector_index = MockVectorIndex()
        mock_collective_manager = MockCollectiveMemoryManager()
        rag_retrieval = RAGRetrieval(mock_vector_index, mock_collective_manager)
        rag_retrieval.initialize()
        
        # Test wyszukiwania
        result = rag_retrieval.retrieve_knowledge(
            query=" Liverpool match prediction",
            agent_id="test_agent",
            top_k=3,
            min_similarity=0.7
        )
        
        if result['status'] == 'success':
            print("[OK] Knowledge retrieval successful")
            
            if len(result['results']) == 3:
                print(f"[OK] Retrieved {len(result['results'])} results")
            else:
                print(f"[FAIL] Expected 3 results, got {len(result['results'])}")
                return False
            
            if result['summary']['total_results'] == 3:
                print("[OK] Summary contains correct count")
            else:
                print(f"[FAIL] Summary count mismatch")
                return False
            
            return True
        else:
            print(f"[FAIL] Retrieval failed: {result}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retrieve_for_decision_context():
    """Test retrieve_for_decision_context method"""
    print("\n[TEST 4] retrieve_for_decision_context method")
    
    # Mock VectorIndex
    class MockVectorIndex:
        def search(self, query, top_k=5, min_similarity=0.0):
            return [
                {
                    'id': 'vec_1', 
                    'content': {'type': 'decision', 'decision_type': 'model_selection'},
                    'similarity': 0.95,
                    'type': 'decision'
                }
            ]
    
    # Mock CollectiveMemoryManager
    class MockCollectiveMemoryManager:
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
    
    try:
        from SSI_V5.memory.collective_memory.rag_retrieval import RAGRetrieval
        
        # Tworzenie i inicializacja
        rag_retrieval = RAGRetrieval(MockVectorIndex(), MockCollectiveMemoryManager())
        rag_retrieval.initialize()
        
        # Kontekst aktualny
        current_situation = {
            'world_name': 'PremierLeague',
            'phase': 'prediction_window',
            'world_data_keys': ['team_a', 'team_b', 'odds']
        }
        
        # Pobranie wiedzy
        result = rag_retrieval.retrieve_for_decision_context(
            current_situation=current_situation,
            agent_id="test_agent_01",
            top_k=5,
            min_similarity=0.6
        )
        
        if result['status'] == 'success':
            print("[OK] Decision context retrieval successful")
            
            if 'relevant_memories' in result:
                print("[OK] Result contains relevant_memories")
            else:
                print("[FAIL] Result missing relevant_memories")
                return False
            
            if 'memory_count' in result:
                print("[OK] Result contains memory_count")
            else:
                print("[FAIL] Result missing memory_count")
                return False
            
            return True
        else:
            print(f"[FAIL] Decision context retrieval failed: {result}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Decision context test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_relevant_knowledge_for_decision():
    """Test get_relevant_knowledge_for_decision method"""
    print("\n[TEST 5] get_relevant_knowledge_for_decision method")
    
    # Mock VectorIndex
    class MockVectorIndex:
        def search(self, query, top_k=5, min_similarity=0.0):
            return [
                {
                    'id': 'vec_1', 
                    'content': {'type': 'decision', 'decision_type': 'model_selection'},
                    'similarity': 0.95,
                    'type': 'model_selection'
                },
                {
                    'id': 'vec_2', 
                    'content': {'type': 'strategy_change'},
                    'similarity': 0.85,
                    'type': 'strategy_change'
                }
            ]
    
    # Mock CollectiveMemoryManager
    class MockCollectiveMemoryManager:
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
    
    try:
        from SSI_V5.memory.collective_memory.rag_retrieval import RAGRetrieval
        
        # Tworzenie i inicializacja
        rag_retrieval = RAGRetrieval(MockVectorIndex(), MockCollectiveMemoryManager())
        rag_retrieval.initialize()
        
        # Pobranie wiedzy dla typu decyzji
        result = rag_retrieval.get_relevant_knowledge_for_decision(
            decision_type='model_selection',
            context={'phase': 'prediction_window'},
            agent_id="test_agent_01"
        )
        
        if result['status'] == 'success':
            print("[OK] Decision-specific knowledge retrieval successful")
            
            # Powinno być zfieltrowane do model_selection
            filtered = [r for r in result['results'] if r.get('type') == 'model_selection']
            if len(filtered) > 0:
                print(f"[OK] Found {len(filtered)} model_selection relevant results")
                return True
            else:
                print("[FAIL] No model_selection results found")
                return False
        else:
            print(f"[FAIL] Decision-specific retrieval failed: {result}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Decision-specific test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistics():
    """Test mechanizmu statystyk"""
    print("\n[TEST 6] Statistics tracking")
    
    # Mock VectorIndex
    class MockVectorIndex:
        def search(self, query, top_k=5, min_similarity=0.0):
            return []
    
    # Mock CollectiveMemoryManager
    class MockCollectiveMemoryManager:
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
    
    try:
        from SSI_V5.memory.collective_memory.rag_retrieval import RAGRetrieval
        
        # Tworzenie
        rag_retrieval = RAGRetrieval(MockVectorIndex(), MockCollectiveMemoryManager())
        
        # Początkowo statystyki powinny być zerowe
        stats = rag_retrieval.stats
        if stats['retrieval_operations'] == 0:
            print("[OK] Initial statistics are zero")
        else:
            print("[FAIL] Initial statistics should be zero")
            return False
        
        # Wykonanie operacji
        rag_retrieval.retrieve_knowledge(query="test", top_k=1)
        
        # Sprawdzenie statystyk po operacji
        stats = rag_retrieval.stats
        if stats['retrieval_operations'] >= 1:
            print("[OK] Statistics updated after operation")
            return True
        else:
            print("[FAIL] Statistics not updated")
            return False
            
    except Exception as e:
        print(f"[FAIL] Statistics test failed: {e}")
        return False


def test_error_handling():
    """Test obsługi błędów"""
    print("\n[TEST 7] Error handling")
    
    # Mock VectorIndex
    class MockVectorIndex:
        def search(self, query, top_k=5, min_similarity=0.0):
            return []
    
    # Mock CollectiveMemoryManager
    class MockCollectiveMemoryManager:
        def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
            return []
        def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
            return []
    
    try:
        from SSI_V5.memory.collective_memory.rag_retrieval import RAGRetrieval
        
        # Tworzenie
        rag_retrieval = RAGRetrieval(MockVectorIndex(), MockCollectiveMemoryManager())
        
        # Test z pustym zapytaniem
        result = rag_retrieval.retrieve_knowledge(query="", top_k=1)
        
        if result['status'] == 'error':
            print("[OK] Empty query handled correctly")
            return True
        else:
            print("[FAIL] Empty query should return error")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error handling test failed: {e}")
        return False


def main():
    """Główna funkcja testowa"""
    print("=" * 60)
    print("SSI V5 ETAP 0 KROK 4 - RAG Retrieval Layer Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_rag_retrieval_initialization,
        test_retrieve_knowledge,
        test_retrieve_for_decision_context,
        test_get_relevant_knowledge_for_decision,
        test_statistics,
        test_error_handling
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[ERROR] Test {test.__name__} crashed: {e}")
            results.append(False)
    
    # Podsumowanie
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"WYNIK: {passed}/{total} testow zaliczonych")
    
    if passed == total:
        print("[SUCCESS] WSZYSTKIE TESTY ZALICZONE!")
        print("[OK] ETAP 0 KROK 4 - RAG Retrieval Layer works!")
    elif passed >= total * 0.8:
        print("[WARNING] Wiekszosc testow zaliczona")
    else:
        print("[FAIL] Zbyt wiele testow nie zaliczono")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
