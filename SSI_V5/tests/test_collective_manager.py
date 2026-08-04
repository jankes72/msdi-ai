# SSI V5 Tests - CollectiveManager
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.4
# Data: 2026-08-04
#
# Testy dla CollectiveManager:
# - Tworzenie i inicjalizacja
# - Zbieranie decyzji od agentów
# - Budowanie konsensusu
# - Zarządzanie pamięcią kolektywną
# - Integracja z agentami

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import MagicMock
from SSI_V5.agents.collective_manager import (
    CollectiveManager, 
    CollectiveDecision, 
    CollectiveObservation,
    CollectiveMemory,
    ConsensusType,
    DecisionStatus
)


class TestCollectiveManager(unittest.TestCase):
    """Test klasy CollectiveManager"""
    
    def setUp(self):
        """SetUp"""
        self.manager = CollectiveManager(
            world_name="TEST_WORLD",
            pipeline_reference="test_pipeline"
        )
    
    def test_01_initialization(self):
        """Test inicjalizacji CollectiveManager"""
        self.assertFalse(self.manager._initialized)
        self.assertEqual(self.manager.world_name, "TEST_WORLD")
        self.assertEqual(len(self.manager.agent_names), 6)
        self.assertIsInstance(self.manager.collective_memory, CollectiveMemory)
    
    def test_02_initialize_method(self):
        """Test metody initialize"""
        result = self.manager.initialize()
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(self.manager._initialized)
        self.assertTrue(self.manager._active)
        self.assertIn('collective_memory_id', result)
    
    def test_03_start_cycle(self):
        """Test rozpoczęcia cyklu"""
        self.manager.initialize()
        
        result = self.manager.start_cycle('test_cycle_01')
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(self.manager._current_cycle_id, 'test_cycle_01')
        self.assertEqual(self.manager.total_cycles, 1)
    
    def test_04_collect_agent_decision(self):
        """Test zbierania decyzji od agentów"""
        self.manager.initialize()
        self.manager.start_cycle('test_cycle_01')
        
        # Symulacja decyzji od agenta
        agent_decision = {
            'decision_id': 'dec_01',
            'decision_type': 'bet',
            'action': 'place_bet',
            'confidence': 0.85,
            'timestamp': '2026-08-04T00:00:00'
        }
        
        result = self.manager.collect_agent_decision('agent_01', agent_decision)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['decisions_collected'], 1)
        self.assertEqual(result['agent_id'], 'agent_01')
    
    def test_05_collect_multiple_decisions(self):
        """Test zbierania wielu decyzji"""
        self.manager.initialize()
        self.manager.start_cycle('test_cycle_01')
        
        # Decyzje od 6 agentów
        for i in range(1, 7):
            decision = {
                'decision_id': f'dec_{i:02d}',
                'decision_type': 'bet',
                'action': 'place_bet' if i % 2 == 0 else 'hold',  # 3x place_bet, 3x hold
                'confidence': 0.8 + (i * 0.01),
                'timestamp': '2026-08-04T00:00:00'
            }
            result = self.manager.collect_agent_decision(f'agent_{i:02d}', decision)
            self.assertEqual(result['status'], 'success')
        
        self.assertEqual(len(self.manager._current_decisions), 6)
    
    def test_06_build_majority_consensus(self):
        """Test budowania konsensusu większościowego"""
        self.manager.consensus_type = ConsensusType.MAJORITY
        self.manager.initialize()
        self.manager.start_cycle('test_cycle_01')
        
        # 4 agenci głosują na 'place_bet', 2 na 'hold'
        for i in range(1, 7):
            action = 'place_bet' if i <= 4 else 'hold'
            decision = {
                'decision_id': f'dec_{i:02d}',
                'decision_type': 'bet',
                'action': action,
                'confidence': 0.8
            }
            self.manager.collect_agent_decision(f'agent_{i:02d}', decision)
        
        collective_decision = self.manager.build_consensus('test_cycle_01')
        
        self.assertIsInstance(collective_decision, CollectiveDecision)
        self.assertEqual(collective_decision.consensus_type, ConsensusType.MAJORITY)
        self.assertGreater(collective_decision.confidence_score, 0.5)
        self.assertEqual(collective_decision.status, DecisionStatus.CONSENSUS)
        self.assertEqual(len(collective_decision.agents_participated), 6)
        
        # Sprawdź czy konsensus wybrał najpopularniejszą opcję
        consensus_action = collective_decision.consensus_result.get('action')
        self.assertEqual(consensus_action, 'place_bet')
    
    def test_07_build_unanimous_consensus(self):
        """Test budowania konsensusu jednogłośnego"""
        self.manager.consensus_type = ConsensusType.UNANIMOUS
        self.manager.initialize()
        self.manager.start_cycle('test_cycle_01')
        
        # Wszyscy agenci głosują na to samo
        for i in range(1, 7):
            decision = {
                'decision_id': f'dec_{i:02d}',
                'decision_type': 'bet',
                'action': 'place_bet',
                'value': 100
            }
            self.manager.collect_agent_decision(f'agent_{i:02d}', decision)
        
        collective_decision = self.manager.build_consensus('test_cycle_01')
        
        self.assertEqual(collective_decision.consensus_type, ConsensusType.UNANIMOUS)
        self.assertEqual(collective_decision.confidence_score, 1.0)
        self.assertEqual(collective_decision.consensus_result.get('action'), 'place_bet')
    
    def test_08_build_average_consensus(self):
        """Test budowania konsensusu średnią"""
        self.manager.consensus_type = ConsensusType.AVERAGE
        self.manager.initialize()
        self.manager.start_cycle('test_cycle_01')
        
        # Decyzje z wartościami liczbowymi
        values = [10, 20, 30, 40, 50, 60]
        for i, value in enumerate(values, 1):
            decision = {
                'decision_id': f'dec_{i:02d}',
                'decision_type': 'prediction',
                'value': value
            }
            self.manager.collect_agent_decision(f'agent_{i:02d}', decision)
        
        collective_decision = self.manager.build_consensus('test_cycle_01')
        
        # Średnia z [10, 20, 30, 40, 50, 60] = 35
        expected_avg = sum(values) / len(values)
        self.assertAlmostEqual(collective_decision.consensus_result.get('value'), expected_avg, places=1)
        self.assertEqual(collective_decision.consensus_result.get('decision_type'), 'average')
    
    def test_09_collective_memory(self):
        """Test pamięci kolektywnej"""
        self.manager.initialize()
        self.manager.start_cycle('test_cycle_01')
        
        # Dodaj decyzje
        for i in range(1, 4):
            decision = {
                'decision_id': f'dec_{i:02d}',
                'decision_type': 'bet',
                'action': 'place_bet'
            }
            self.manager.collect_agent_decision(f'agent_{i:02d}', decision)
        
        # Buduj konsensus
        collective_decision = self.manager.build_consensus('test_cycle_01')
        
        # Sprawdź pamięć
        memory_dict = self.manager.get_collective_memory()
        
        self.assertIn('memory_id', memory_dict)
        self.assertIn('decisions', memory_dict)
        self.assertEqual(len(memory_dict['decisions']), 1)
        self.assertIn('statistics', memory_dict)
    
    def test_10_collective_observation(self):
        """Test obserwacji kolektywnej"""
        self.manager.initialize()
        self.manager.start_cycle('test_cycle_01')
        
        # Dodaj obserwacje
        for i in range(1, 7):
            observation = {
                'observation_id': f'obs_{i:02d}',
                'observation_type': 'match_analysis',
                'data': {'match_id': f'match_{i}'}
            }
            result = self.manager.collect_agent_observation(f'agent_{i:02d}', observation)
            self.assertEqual(result['status'], 'success')
        
        # Buduj kolektywną obserwację
        collective_observation = self.manager.build_collective_observation('test_cycle_01')
        
        self.assertIsInstance(collective_observation, CollectiveObservation)
        self.assertEqual(len(collective_observation.agents_participated), 6)
        self.assertEqual(collective_observation.importance_score, 100.0)  # 6/6 * 100
    
    def test_11_end_cycle(self):
        """Test zakończenia cyklu"""
        self.manager.initialize()
        self.manager.start_cycle('test_cycle_01')
        
        # Dodaj decyzje od przynajmniej 4 agentów (większość z 6)
        for i in range(1, 5):  # 4 agenci
            decision = {'decision_type': 'bet', 'action': 'place_bet'}
            self.manager.collect_agent_decision(f'agent_{i:02d}', decision)
        
        # Zakończ cykl
        result = self.manager.end_cycle('test_cycle_01')
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['cycle_id'], 'test_cycle_01')
        # Z 4 agentami i majority consensus, konsensus powinien zostać osiągnięty
        self.assertTrue(result['consensus_reached'])
        self.assertIsNotNone(result['collective_decision_id'])
        self.assertEqual(self.manager.total_collective_decisions, 1)
    
    def test_12_cycle_summary(self):
        """Test podsumowania cyklu"""
        self.manager.initialize()
        self.manager.start_cycle('test_cycle_01')
        
        # Dodaj decyzje i obserwacje
        for i in range(1, 4):
            decision = {'decision_type': 'bet', 'action': 'place_bet'}
            self.manager.collect_agent_decision(f'agent_{i:02d}', decision)
            
            observation = {'observation_type': 'match_analysis'}
            self.manager.collect_agent_observation(f'agent_{i:02d}', observation)
        
        self.manager.build_consensus('test_cycle_01')
        self.manager.end_cycle('test_cycle_01')
        
        # Pobierz podsumowanie
        summary = self.manager.get_cycle_summary('test_cycle_01')
        
        self.assertIn('cycle_id', summary)
        self.assertEqual(summary['cycle_id'], 'test_cycle_01')
        self.assertIn('decisions', summary)
        self.assertIn('observations', summary)
    
    def test_13_set_references(self):
        """Test ustawiania referencji"""
        self.manager.initialize()
        
        mock_agent_runtime_manager = MagicMock()
        mock_memory_manager = MagicMock()
        
        self.manager.set_agent_runtime_manager_reference(mock_agent_runtime_manager)
        self.manager.set_memory_manager_reference(mock_memory_manager)
        
        self.assertEqual(self.manager.agent_runtime_manager, mock_agent_runtime_manager)
        self.assertEqual(self.manager.memory_manager, mock_memory_manager)
    
    def test_14_shutdown(self):
        """Test zamknięcia CollectiveManager"""
        self.manager.initialize()
        self.manager.start_cycle('test_cycle_01')
        
        shutdown_result = self.manager.shutdown()
        
        self.assertEqual(shutdown_result['status'], 'success')
        self.assertFalse(self.manager._initialized)
        self.assertFalse(self.manager._active)
        self.assertIn('total_cycles', shutdown_result)
        self.assertIn('collective_memory_stats', shutdown_result)


class TestCollectiveMemory(unittest.TestCase):
    """Test klasy CollectiveMemory"""
    
    def test_collective_memory_creation(self):
        """Test tworzenia pamięci kolektywnej"""
        memory = CollectiveMemory(
            memory_id='test_memory',
            world_name='TEST_WORLD'
        )
        
        self.assertEqual(memory.memory_id, 'test_memory')
        self.assertEqual(memory.world_name, 'TEST_WORLD')
        self.assertEqual(len(memory.decisions), 0)
        self.assertEqual(len(memory.observations), 0)
    
    def test_add_decision_to_memory(self):
        """Test dodawania decyzji do pamięci"""
        memory = CollectiveMemory(memory_id='test_memory', world_name='TEST_WORLD')
        
        decision = CollectiveDecision(
            decision_id='dec_01',
            cycle_id='cycle_01',
            world_name='TEST_WORLD'
        )
        
        decision_id = memory.add_decision(decision)
        
        self.assertEqual(decision_id, 'dec_01')
        self.assertEqual(len(memory.decisions), 1)
        self.assertIn('_update_statistics', dir(memory))


if __name__ == '__main__':
    unittest.main()
