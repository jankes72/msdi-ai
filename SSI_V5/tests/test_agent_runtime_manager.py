# SSI V5 Tests - AgentRuntimeManager
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.4
# Data: 2026-08-04
#
# Testy dla AgentRuntimeManager:
# - Tworzenie i inicjalizacja
# - Wykonanie cyklu
# - Zarządzanie agentami
# - Obsługa pamięci
# - Integracja z CollectiveManager

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import MagicMock
from SSI_V5.agents import AgentRuntimeManager, AgentRuntime
from SSI_V5.agents.collective_manager import CollectiveManager


class TestAgentRuntimeManager(unittest.TestCase):
    """Test klasy AgentRuntimeManager"""
    
    def setUp(self):
        """SetUp"""
        self.manager = AgentRuntimeManager(
            pipeline_reference="test_pipeline",
            number_of_agents=6,
            world_name="TEST_WORLD"
        )
    
    def test_01_initialization(self):
        """Test inicjalizacji AgentRuntimeManager"""
        self.assertFalse(self.manager._initialized)
        self.assertEqual(len(self.manager.agents), 0)
        self.assertEqual(self.manager.world_name, "TEST_WORLD")
        self.assertEqual(len(self.manager.agent_names), 6)
        self.assertEqual(self.manager.agent_names, ["Agent_01", "Agent_02", "Agent_03", "Agent_04", "Agent_05", "Agent_06"])
    
    def test_02_agents_creation(self):
        """Test tworzenia agentów"""
        result = self.manager.initialize()
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(self.manager._initialized)
        self.assertEqual(len(self.manager.agents), 6)
        self.assertEqual(result['agents_initialized'], 6)
        self.assertEqual(result['agents_failed'], 0)
    
    def test_03_agents_properties(self):
        """Test właściwości agentów"""
        self.manager.initialize()
        
        for agent_id, agent in self.manager.agents.items():
            self.assertIsInstance(agent, AgentRuntime)
            self.assertIn(agent.name, self.manager.agent_names)
            # AgentRuntime nie ma world_name, ale Manager ma world_name
            self.assertEqual(self.manager.world_name, "TEST_WORLD")
    
    def test_04_execute_cycle(self):
        """Test wykonania cyklu"""
        self.manager.initialize()
        
        cycle_data = {
            'cycle_id': 'test_cycle_01',
            'world_name': 'TEST_WORLD',
            'input_data': {'test': 'data'},
            'timestamp': '2026-08-04T00:00:00',
            'pipeline_mode': 'test'
        }
        
        result = self.manager.execute_cycle(cycle_data)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['cycle_id'], 'test_cycle_01')
        self.assertEqual(result['agents_active'], 6)
        self.assertGreater(result['execution_time'], 0)
        self.assertEqual(len(result['agent_results']), 6)
        self.assertEqual(self.manager.cycle_count, 1)
    
    def test_05_observe_method(self):
        """Test metody observe"""
        self.manager.initialize()
        
        observation_data = {
            'type': 'world_analysis',
            'data': {'match': 'test_match'},
            'timestamp': '2026-08-04T00:00:00'
        }
        
        result = self.manager.observe(observation_data)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['agents_notified'], 6)
        self.assertEqual(self.manager.total_observations_recorded, 6)
    
    def test_06_multiple_cycles(self):
        """Test wielu cykli"""
        self.manager.initialize()
        
        for i in range(3):
            cycle_data = {
                'cycle_id': f'test_cycle_{i+1}',
                'world_name': 'TEST_WORLD',
                'input_data': {},
                'timestamp': '2026-08-04T00:00:00',
                'pipeline_mode': 'test'
            }
            result = self.manager.execute_cycle(cycle_data)
            self.assertEqual(result['status'], 'success')
        
        self.assertEqual(self.manager.cycle_count, 3)
        self.assertEqual(self.manager.total_contracts_sent, 18)  # 6 agentów * 3 cykle
    
    def test_07_add_remove_agent(self):
        """Test dodawania i usuwania agentów"""
        self.manager.initialize()
        
        # Dodawanie nowego agenta
        new_agent_config = {'name': 'Agent_07', 'mode': 'auto'}  # AgentMode używa małych liter
        agent_id = self.manager.add_agent(new_agent_config)
        
        self.assertIn(agent_id, self.manager.agents)
        self.assertEqual(len(self.manager.agents), 7)
        
        # Usuwanie agenta
        result = self.manager.remove_agent(agent_id)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.agents), 6)
    
    def test_08_set_collective_manager_reference(self):
        """Test ustawiania referencji do CollectiveManager"""
        self.manager.initialize()
        
        collective_manager = CollectiveManager(
            world_name="TEST_WORLD",
            pipeline_reference="test_pipeline"
        )
        collective_manager.initialize()
        
        self.manager.set_collective_manager_reference(collective_manager)
        
        self.assertIsNotNone(self.manager.collective_manager)
        self.assertIsInstance(self.manager.collective_manager, CollectiveManager)
    
    def test_09_set_memory_manager_reference(self):
        """Test ustawiania referencji do MemoryManager"""
        self.manager.initialize()
        
        mock_memory_manager = MagicMock()
        self.manager.set_memory_manager_reference(mock_memory_manager)
        
        self.assertIsNotNone(self.manager.memory_manager)
        self.assertEqual(self.manager.memory_manager, mock_memory_manager)
    
    def test_10_get_statistics(self):
        """Test pobierania statystyk"""
        self.manager.initialize()
        
        # Wykonaj jeden cykl
        cycle_data = {
            'cycle_id': 'test_cycle_01',
            'world_name': 'TEST_WORLD',
            'input_data': {},
            'timestamp': '2026-08-04T00:00:00',
            'pipeline_mode': 'test'
        }
        self.manager.execute_cycle(cycle_data)
        
        stats = self.manager.get_agent_statistics()
        
        self.assertEqual(len(stats), 6)
        for stat in stats:
            self.assertIn('agent_id', stat)
            self.assertIn('name', stat)
            self.assertIn('cycle_count', stat)
    
    def test_11_shutdown(self):
        """Test zamknięcia menadżera"""
        self.manager.initialize()
        
        shutdown_result = self.manager.shutdown()
        
        self.assertEqual(shutdown_result['status'], 'success')
        self.assertFalse(self.manager._initialized)
        self.assertEqual(len(self.manager.agents), 0)  # zamknięcie agentów
        self.assertEqual(shutdown_result['total_cycles_executed'], 0)


if __name__ == '__main__':
    unittest.main()
