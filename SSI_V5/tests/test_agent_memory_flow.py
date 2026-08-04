# SSI V5 Tests - Agent Memory Flow
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.4
# Data: 2026-08-04
#
# Test przepлыwu pamięci między komponentami:
# Agent Memory -> Collective Memory -> System Memory

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
from SSI_V5.teachers import MemoryManager


class TestAgentMemoryFlow(unittest.TestCase):
    """Test przepływu pamięci agentów"""
    
    def setUp(self):
        """SetUp"""
        self.pipeline = SSIPipeline(
            mode=PipelineMode.TEST,
            world_name="TEST_MEMORY_WORLD",
            use_agent_runtime_manager=True
        )
        
        init_result = self.pipeline.initialize()
        self.assertEqual(init_result['status'], 'success')
    
    def tearDown(self):
        """Cleanup"""
        if self.pipeline:
            self.pipeline.shutdown()
    
    def test_01_pipeline_has_memory_manager(self):
        """Test że Pipeline ma MemoryManager"""
        self.assertIsNotNone(self.pipeline.memory_manager)
        self.assertIsInstance(self.pipeline.memory_manager, MemoryManager)
    
    def test_02_agents_have_memory(self):
        """Test że agenci mają swoją pamięć"""
        manager = self.pipeline.agent_runtime_manager
        
        for agent_id, agent in manager.agents.items():
            # Każdy agent powinien mieć memory
            self.assertTrue(hasattr(agent, 'memory'))
            self.assertIsNotNone(agent.memory)
            
            # Pamięć powinna zawierać odpowiednie struktury
            self.assertTrue(hasattr(agent.memory, 'short_term_memory'))
            self.assertTrue(hasattr(agent.memory, 'long_term_memory'))
            self.assertTrue(hasattr(agent.memory, 'observations'))
            self.assertTrue(hasattr(agent.memory, 'decisions'))
    
    def test_03_agents_memory_after_cycle(self):
        """Test pamięci agentów po wykonaniu cyklu"""
        # Wykonaj jeden cykl
        self.pipeline.run_cycle()
        
        manager = self.pipeline.agent_runtime_manager
        
        # Sprawdź czy agenci mają zapisane obserwacje i decyzje
        for agent_id, agent in manager.agents.items():
            memory = agent.memory
            
            # Po jednym cyklu agent powinien mieć co najmniej jedną obserwację
            self.assertGreaterEqual(len(memory.observations), 1)
            
            # I co najmniej jedną decyzję
            self.assertGreaterEqual(len(memory.decisions), 1)
    
    def test_04_collective_memory_after_cycles(self):
        """Test pamięci kolektywnej po cyklach"""
        # Wykonaj 2 cykle
        for i in range(2):
            self.pipeline.run_cycle()
        
        collective_manager = self.pipeline.collective_manager
        collective_memory = collective_manager.get_collective_memory()
        
        # Sprawdź strukturę pamięci kolektywnej
        self.assertIn('decisions', collective_memory)
        self.assertIn('observations', collective_memory)
        self.assertIn('statistics', collective_memory)
        
        # Powinny być zapisane decyzje kolektywne
        self.assertGreaterEqual(len(collective_memory['decisions']), 2)
    
    def test_05_agent_runtime_manager_references(self):
        """Test referencji AgentRuntimeManager"""
        manager = self.pipeline.agent_runtime_manager
        
        # Should have have a collective manager
        self.assertIsNotNone(manager.collective_manager)
        self.assertEqual(manager.collective_manager, self.pipeline.collective_manager)
        
        # Should have memory manager
        self.assertIsNotNone(manager.memory_manager)
        self.assertEqual(manager.memory_manager, self.pipeline.memory_manager)
    
    def test_06_collective_manager_references(self):
        """Test referencji CollectiveManager"""
        collective_manager = self.pipeline.collective_manager
        
        # Should have reference to AgentRuntimeManager
        self.assertIsNotNone(collective_manager.agent_runtime_manager)
        self.assertEqual(collective_manager.agent_runtime_manager, self.pipeline.agent_runtime_manager)
        
        # Should have reference to MemoryManager
        self.assertIsNotNone(collective_manager.memory_manager)
        self.assertEqual(collective_manager.memory_manager, self.pipeline.memory_manager)
    
    def test_07_memory_manager_has_world_memory(self):
        """Test że MemoryManager ma pamięć świata"""
        memory_manager = self.pipeline.memory_manager
        
        # Powinien mieć world_memory
        self.assertTrue(hasattr(memory_manager, 'world_memory'))
        self.assertIsInstance(memory_manager.world_memory, dict)
        
        # Powinien mieć model_memory
        self.assertTrue(hasattr(memory_manager, 'model_memory'))
        self.assertIsInstance(memory_manager.model_memory, dict)
        
        # Powinien mieć observation_memory
        self.assertTrue(hasattr(memory_manager, 'observation_memory'))
        self.assertIsInstance(memory_manager.observation_memory, dict)
    
    def test_08_memory_flow_integration(self):
        """Test integracji przepływu pamięci"""
        # Wykonaj cykl
        cycle_result = self.pipeline.run_cycle()
        
        # Sprawdź że wszystkie komponenty pamięci zostały zaktualizowane
        
        # 1. Agenci powinni mieć swoje pamięci
        manager = self.pipeline.agent_runtime_manager
        for agent_id, agent in manager.agents.items():
            self.assertGreaterEqual(len(agent.memory.observations), 1)
            self.assertGreaterEqual(len(agent.memory.decisions), 1)
        
        # 2. Collective Manager powinien mieć pamięć kolektywną
        collective_memory = self.pipeline.collective_manager.get_collective_memory()
        self.assertGreaterEqual(len(collective_memory['decisions']), 1)
        
        # 3. Memory Manager powinien mieć dostęp do pamięci systemowej
        self.assertIsNotNone(self.pipeline.memory_manager)
    
    def test_09_memory_statistics(self):
        """Test statystyk pamięci"""
        # Wykonaj 2 cykle
        for i in range(2):
            self.pipeline.run_cycle()
        
        # Sprawdź statystyki MemoryManager
        memory_manager = self.pipeline.memory_manager
        stats = memory_manager.get_memory_statistics()
        
        self.assertIn('world_memory', stats)
        self.assertIn('model_memory', stats)
        self.assertIn('observation_memory', stats)
        self.assertIn('experience_history', stats)
    
    def test_10_pipeline_memory_layer(self):
        """Test warstwy pamięci w Pipeline"""
        self.assertIsNotNone(self.pipeline.memory_layer)
        self.assertEqual(self.pipeline.memory_layer['status'], 'available')
        self.assertIn('component', self.pipeline.memory_layer)
        self.assertIn('memory_manager', self.pipeline.memory_layer)


if __name__ == '__main__':
    unittest.main()
