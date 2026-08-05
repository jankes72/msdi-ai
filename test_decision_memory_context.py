#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for SSI V5 ETAP 0 KROK 2 - Decision Memory Context
"""

import sys

# Add the project directory to Python path
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')


def test_import():
    """Test importu modulu"""
    print("[TEST 1] Import module")
    try:
        from SSI_V5.agents.decision_memory_context import (
            MemoryContext, 
            EnhancedDecisionContext, 
            DecisionMemoryContextBuilder, 
            DecisionMemoryContextError
        )
        print("[OK] Import successful")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        return False


def test_memory_context_creation():
    """Test tworzenia MemoryContext"""
    print("\n[TEST 2] MemoryContext creation")
    
    try:
        from SSI_V5.agents.decision_memory_context import MemoryContext
        
        # Test basic creation
        context = MemoryContext()
        print("[OK] Empty MemoryContext created")
        
        # Test with data
        context.add_historical_memory({'type': 'decision', 'data': 'test'})
        context.add_similar_case({'type': 'case', 'similarity': 0.9})
        context.add_previous_decision({'decision_type': 'model_selection', 'outcome': 'success'})
        context.add_agent_experience('model_preference', 'v2')
        context.add_relevant_knowledge('pattern', 'high_confidence_leads_to_success')
        
        # Check stats
        summary = context.get_summary()
        if (summary['has_historical_data'] and 
            summary['has_similar_cases'] and 
            summary['has_previous_decisions'] and
            summary['has_agent_experience'] and
            summary['has_relevant_knowledge']):
            print("[OK] MemoryContext with data works correctly")
            print(f"   Stats: {summary['stats']}")
            return True
        else:
            print(f"[FAIL] MemoryContext data not properly set: {summary}")
            return False
            
    except Exception as e:
        print(f"[FAIL] MemoryContext creation test failed: {e}")
        return False


def test_memory_context_from_retrieval():
    """Test tworzenia MemoryContext z wyniku retrieval"""
    print("\n[TEST 3] MemoryContext from retrieval result")
    
    try:
        from SSI_V5.agents.decision_memory_context import MemoryContext
        
        # Mock retrieval result (wie to co zwraca memory_layer.retrieve_context())
        retrieval_result = {
            'status': 'success',
            'agent_id': 'agent_01',
            'memory_context': {
                'agent_id': 'agent_01',
                'situation': {'world_name': 'PremierLeague'},
                'relevant_memories': [
                    {'type': 'decision', 'decision_type': 'model_selection'},
                    {'type': 'experience', 'outcome': 'success'}
                ],
                'memory_count': 2,
                'memory_context': 'Test context'
            },
            'related_memories': [
                {'document_id': 'doc_1', 'type': 'decision', 'data': {'test': 'data1'}},
                {'document_id': 'doc_2', 'type': 'experience', 'data': {'test': 'data2'}}
            ],
            'memory_count': 2,
            'retrieval_time_ms': 10.5,
            'timestamp': '2026-08-04T00:00:00'
        }
        
        # Create MemoryContext from retrieval result
        memory_context = MemoryContext.from_memory_retrieval_result(retrieval_result)
        
        # Check if data was properly extracted
        if (len(memory_context.historical_memories) == 2 and
            memory_context.memory_stats['memory_count'] == 2):
            print("[OK] MemoryContext from retrieval result works")
            print(f"   Historical memories: {len(memory_context.historical_memories)}")
            return True
        else:
            print(f"[FAIL] MemoryContext not properly populated: {memory_context.get_summary()}")
            return False
            
    except Exception as e:
        print(f"[FAIL] MemoryContext from retrieval test failed: {e}")
        return False


def test_enhanced_decision_context():
    """Test EnhancedDecisionContext"""
    print("\n[TEST 4] EnhancedDecisionContext")
    
    try:
        from SSI_V5.agents.decision_memory_context import EnhancedDecisionContext, MemoryContext
        from SSI_V5.agents.decision_engine import DecisionContext
        
        # Create original DecisionContext
        original_context = DecisionContext(
            world_data={'teams': ['TeamA', 'TeamB']},
            model_info={'model_v1': {'accuracy': 0.85}},
            weights={'weight1': 0.6, 'weight2': 0.4},
            recommendations=[{'action': 'select', 'model': 'v1'}],
            risk_factors={'risk_level': 'medium'},
            constraints={'max_bet': 100}
        )
        
        # Create MemoryContext
        memory_context = MemoryContext()
        memory_context.add_previous_decision({'decision_type': 'model_selection', 'parameters': {}})
        memory_context.add_similar_case({'type': 'similar_match', 'similarity': 0.85})
        
        # Create EnhancedDecisionContext
        enhanced_context = EnhancedDecisionContext(
            original_context=original_context,
            memory_context=memory_context
        )
        
        # Check properties
        if (enhanced_context.has_original_context and 
            enhanced_context.has_memory_context and
            enhanced_context.has_previous_decisions() and
            enhanced_context.has_similar_cases()):
            print("[OK] EnhancedDecisionContext works correctly")
            
            # Check combined context
            combined = enhanced_context.get_combined_context()
            if ('world_data' in combined and 
                'memory_context' in combined and
                'previous_decisions' in combined):
                print("[OK] Combined context contains all expected data")
                return True
            else:
                print(f"[FAIL] Combined context missing data: {list(combined.keys())}")
                return False
        else:
            print(f"[FAIL] EnhancedDecisionContext properties not set correctly")
            return False
            
    except Exception as e:
        print(f"[FAIL] EnhancedDecisionContext test failed: {e}")
        return False


def test_context_builder():
    """Test DecisionMemoryContextBuilder"""
    print("\n[TEST 5] DecisionMemoryContextBuilder")
    
    # Create mock MemoryIntegrationLayer
    class MockMemoryIntegrationLayer:
        def __init__(self):
            pass
        
        def retrieve_context(self, agent_id, current_situation, top_k=5, min_similarity=0.6):
            return {
                'status': 'success',
                'agent_id': agent_id,
                'memory_context': {
                    'agent_id': agent_id,
                    'situation': current_situation,
                    'relevant_memories': [],
                    'memory_count': 0
                },
                'related_memories': [
                    {'type': 'decision', 'decision_id': 'prev_001'},
                    {'type': 'experience', 'experience_id': 'exp_001'}
                ],
                'memory_count': 2,
                'retrieval_time_ms': 5.0
            }
    
    try:
        from SSI_V5.agents.decision_memory_context import (
            DecisionMemoryContextBuilder, 
            DecisionMemoryContextError
        )
        
        # Create builder
        mock_memory_layer = MockMemoryIntegrationLayer()
        builder = DecisionMemoryContextBuilder(mock_memory_layer)
        print("[OK] DecisionMemoryContextBuilder created")
        
        # Test building memory context
        current_situation = {
            'world_name': 'PremierLeague',
            'phase': 'prediction'
        }
        
        memory_context = builder.build_memory_context(
            agent_id='agent_01',
            current_situation=current_situation,
            top_k=3
        )
        
        if memory_context and len(memory_context.historical_memories) == 2:
            print("[OK] Builder created MemoryContext with data")
            
            # Test enhancing decision context
            from SSI_V5.agents.decision_engine import DecisionContext
            original_context = DecisionContext()
            
            enhanced_context = builder.enhance_decision_context(
                original_context=original_context,
                memory_context=memory_context
            )
            
            if enhanced_context.has_memory_context:
                print("[OK] Builder enhanced DecisionContext successfully")
                return True
            else:
                print("[FAIL] Enhanced context doesn't have memory context")
                return False
        else:
            print(f"[FAIL] Builder didn't create proper MemoryContext")
            return False
            
    except Exception as e:
        print(f"[FAIL] DecisionMemoryContextBuilder test failed: {e}")
        return False


def test_learning_patterns():
    """Test ekstrakcji wzorców uczenia"""
    print("\n[TEST 6] Learning patterns extraction")
    
    try:
        from SSI_V5.agents.decision_memory_context import (
            DecisionMemoryContextBuilder,
            MemoryContext
        )
        
        # Create MemoryContext with test data
        memory_context = MemoryContext()
        
        # Add some test decisions
        memory_context.add_previous_decision({
            'decision_type': 'model_selection',
            'outcome': 'success',
            'confidence': 0.9,
            'parameters': {'model': 'v2'}
        })
        
        memory_context.add_previous_decision({
            'decision_type': 'weight_adjustment',
            'outcome': 'failure',
            'confidence': 0.4,
            'parameters': {'weight': 'high'}
        })
        
        memory_context.add_similar_case({
            'type': 'match_pattern',
            'similarity': 0.95,
            'data': {'teams': ['Strong', 'Weak']}
        })
        
        # Create builder and extract patterns
        builder = DecisionMemoryContextBuilder()
        patterns = builder.extract_learning_patterns(memory_context)
        
        # Check if patterns were extracted correctly
        # We expect: 2 decision patterns, 2 success patterns (1 decision + 1 case with similarity > 0.8),
        # 1 failure pattern, 1 opportunity pattern (confidence > 0.8), 1 risk pattern (confidence < 0.5)
        if (len(patterns['decision_patterns']) == 2 and
            len(patterns['success_patterns']) >= 1 and
            len(patterns['failure_patterns']) == 1 and
            len(patterns['opportunity_patterns']) >= 1 and
            len(patterns['risk_patterns']) >= 1):
            print("[OK] Learning patterns extracted correctly")
            print(f"   Decision patterns: {len(patterns['decision_patterns'])}")
            print(f"   Success patterns: {len(patterns['success_patterns'])}")
            print(f"   Failure patterns: {len(patterns['failure_patterns'])}")
            print(f"   Opportunity patterns: {len(patterns['opportunity_patterns'])}")
            print(f"   Risk patterns: {len(patterns['risk_patterns'])}")
            return True
        else:
            print(f"[FAIL] Learning patterns not extracted correctly: {patterns}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Learning patterns test failed: {e}")
        return False


def run_all_tests():
    """Uruchamia wszystkie testy"""
    print("=" * 60)
    print("SSI V5 ETAP 0 KROK 2 - Decision Memory Context Tests")
    print("=" * 60)
    
    tests = [
        test_import,
        test_memory_context_creation,
        test_memory_context_from_retrieval,
        test_enhanced_decision_context,
        test_context_builder,
        test_learning_patterns
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
        print("[OK] decision_memory_context.py jest gotowy do uzycia")
    else:
        print("[WARNING] Niektore testy nie przebiegly pomyslnie")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)