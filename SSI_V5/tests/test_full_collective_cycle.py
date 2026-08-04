# SSI V5 Tests - Full Collective Cycle Integration
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.4
# Data: 2026-08-04
#
# Test pełnego przepływu z CollectiveManager:
# World Generation -> Modeling -> Teacher -> Agent Execution -> 
# Collective Consensus -> Observation -> Memory Update

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from SSI_V5.core.pipeline import SSIPipeline, PipelineMode, CycleStatus
from SSI_V5.agents import AgentRuntimeManager
from SSI_V5.agents.collective_manager import CollectiveManager


class TestFullCollectiveCycle(unittest.TestCase):
    """Test pełnego cyklu z CollectiveManager"""
    
    def setUp(self):
        """SetUp - inicjalizacja Pipeline z AgentRuntimeManager i CollectiveManager"""
        self.pipeline = SSIPipeline(
            mode=PipelineMode.TEST,
            world_name="TEST_COLLECTIVE_WORLD",
            use_agent_runtime_manager=True
        )
        
        # Inicjalizacja Pipeline
        init_result = self.pipeline.initialize()
        self.assertEqual(init_result['status'], 'success')
        self.assertTrue(self.pipeline._initialized)
        
        # Sprawdzenie komponentów
        self.assertIsNotNone(self.pipeline.agent_runtime_manager)
        self.assertIsNotNone(self.pipeline.collective_manager)
        self.assertIsNotNone(self.pipeline.memory_manager)
    
    def tearDown(self):
        """Cleanup"""
        if self.pipeline:
            self.pipeline.shutdown()
    
    def test_01_pipeline_initialization_with_collective(self):
        """Test że Pipeline inicjalizuje CollectiveManager"""
        self.assertIsNotNone(self.pipeline.collective_manager)
        self.assertIsInstance(self.pipeline.collective_manager, CollectiveManager)
        
        self.assertIsNotNone(self.pipeline.agent_runtime_manager)
        self.assertIsInstance(self.pipeline.agent_runtime_manager, AgentRuntimeManager)
        
        # Sprawdź czy referencje są ustawione
        self.assertEqual(
            self.pipeline.agent_runtime_manager.collective_manager,
            self.pipeline.collective_manager
        )
    
    def test_02_single_cycle_with_collective(self):
        """Test pojedynczego cyklu z Collective Consensus"""
        # Wykonaj jeden cykl
        cycle_result = self.pipeline.run_cycle()
        
        self.assertEqual(cycle_result['status'], 'success')
        self.assertIn('steps', cycle_result)
        
        # Sprawdź kroki cyklu
        steps = cycle_result['steps']
        self.assertIn('world_generation', steps)
        self.assertIn('modeling', steps)
        self.assertIn('teacher_analysis', steps)
        self.assertIn('agent_execution', steps)
        self.assertIn('collective_consensus', steps)  # Nowy krok
        self.assertIn('observation', steps)
        self.assertIn('memory_update', steps)
        
        # Sprawdź statusy kroków
        self.assertEqual(steps['world_generation']['status'], 'success')
        self.assertEqual(steps['agent_execution']['status'], 'success')
        self.assertEqual(steps['collective_consensus']['status'], 'success')
    
    def test_03_collective_consensus_in_cycle(self):
        """Test że Collective Consensus jest częścią cyklu"""
        cycle_result = self.pipeline.run_cycle()
        
        collective_step = cycle_result['steps']['collective_consensus']
        
        # Sprawdź pola Collective Consensus
        self.assertIn('consensus_reached', collective_step)
        self.assertIn('collective_decision_id', collective_step)
        self.assertIn('duration', collective_step)
        
        # Jeśli konsensus został osiągnięty
        if collective_step['consensus_reached']:
            self.assertIsNotNone(collective_step['collective_decision_id'])
    
    def test_04_multiple_cycles_with_collective(self):
        """Test wielu cykli z CollectiveManager"""
        # Wykonaj 3 cykle
        for i in range(3):
            cycle_result = self.pipeline.run_cycle()
            self.assertEqual(cycle_result['status'], 'success')
            self.assertIn('collective_consensus', cycle_result['steps'])
        
        # Sprawdź stan pipeline
        status = self.pipeline.get_status()
        self.assertEqual(status['total_cycles'], 3)
        
        # Sprawdź stan CollectiveManager
        collective_memory = self.pipeline.collective_manager.get_collective_memory()
        self.assertIn('statistics', collective_memory)
    
    def test_05_pipeline_status_after_cycles(self):
        """Test statusu Pipeline po cyklach"""
        # Wykonaj 2 cykle
        self.pipeline.run_cycle()
        self.pipeline.run_cycle()
        
        # Pobierz status
        status = self.pipeline.get_status()
        
        self.assertEqual(status['total_cycles'], 2)
        self.assertIn('current_cycle_id', status)
        self.assertIn('current_status', status)
    
    def test_06_collective_memory_after_cycles(self):
        """Test pamięci kolektywnej po cyklach"""
        # Wykonaj 2 cykle
        self.pipeline.run_cycle()
        self.pipeline.run_cycle()
        
        # Pobierz pamięć kolektywną
        collective_memory = self.pipeline.collective_manager.get_collective_memory()
        
        # Sprawdź strukturę
        self.assertIn('memory_id', collective_memory)
        self.assertIn('world_name', collective_memory)
        self.assertIn('decisions', collective_memory)
        self.assertIn('observations', collective_memory)
        self.assertIn('statistics', collective_memory)
        
        # Jeśli konsensus został osiągnięty
        if len(collective_memory['decisions']) > 0:
            decision = collective_memory['decisions'][0]
            self.assertIn('decision_id', decision)
            self.assertIn('cycle_id', decision)
            self.assertIn('consensus_result', decision)
            self.assertIn('confidence_score', decision)
    
    def test_07_pipeline_shutdown_with_collective(self):
        """Test zamknięcia Pipeline z CollectiveManager"""
        # Wykonaj jeden cykl
        self.pipeline.run_cycle()
        
        # Zamknij Pipeline
        shutdown_result = self.pipeline.shutdown()
        
        self.assertEqual(shutdown_result['status'], 'success')
        
        # Sprawdź czy CollectiveManager został zamknięty
        self.assertIn('collective_manager_shutdown', shutdown_result)
        self.assertEqual(shutdown_result['collective_manager_shutdown'], 'success')
        
        # Sprawdź czy MemoryManager został zapisany
        self.assertIn('memory_manager_shutdown', shutdown_result)
    
    def test_08_cycle_metadata_with_collective(self):
        """Test metadanych cyklu z Collective Consensus"""
        cycle_result = self.pipeline.run_cycle()
        
        metadata = cycle_result['cycle_metadata']
        
        self.assertIn('cycle_id', metadata)
        self.assertIn('processing_steps', metadata)
        
        # Sprawdź czy collective_consensus jest w processing_steps
        self.assertIn('collective_consensus', metadata['processing_steps'])
    
    def test_09_agent_execution_creates_decisions(self):
        """Test że Agent Execution tworzy decyzje dla Collective Consensus"""
        cycle_result = self.pipeline.run_cycle()
        
        # Sprawdź dane z Agent Execution
        agent_step = cycle_result['steps']['agent_execution']
        self.assertEqual(agent_step['status'], 'success')
        self.assertIn('agents_active', agent_step)
        self.assertEqual(agent_step['agents_active'], 6)
        
        # Sprawdź dane z Collective Consensus
        collective_step = cycle_result['steps']['collective_consensus']
        
        # dei Night Laser
        # Sprawdź czy konsensus próbował zebrać decyzje
        self.assertIn('consensus_reached', collective_step)
    
    def test_10_event_log_includes_collective_events(self):
        """Test czy log zdarzeń zawiera zdarzenia CollectiveManager"""
        # Wykonaj cykl
        self.pipeline.run_cycle()
        
        # Pobierz log zdarzeń
        event_log = self.pipeline.get_event_log()
        
        # Sprawdź czy są zdarzenia związane z kolektywnym działaniem
        event_types = [event['event_type'] for event in event_log]
        
        # Powinny być zdarzenia kolektywne
        collective_events = [e for e in event_types if 'COLLECTIVE' in e or 'CONSENSUS' in e]
        self.assertGreater(len(collective_events), 0)


if __name__ == '__main__':
    unittest.main()
