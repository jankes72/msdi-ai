# SSI V5 Tests - Pipeline Memory Integration
# ==================================================
#
# ETAP: 1.2.7.3 Adaptive Knowledge Ecosystem
# Data: 2026-08-04
# 
# Testy integracji Pipeline z MemoryEcosystem poprzez MemoryIntegrator i IFC
#
# Sprawdza:
# 1. Pobieranie MemoryIntegrator przez IFC w Pipeline
# 2. Integracja _run_memory_update() z MemoryIntegrator
# 3. Przekazywanie danych cyklu do pamięci
# 4. Tworzenie rekordów pamięci przez MemoryIntegrator
# 5. Fallback do mock когда MemoryIntegrator niedostępny

import unittest
import sys
import os
from datetime import datetime

# Dodanie sciezki do SSI_V5
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPipelineMemoryIntegration(unittest.TestCase):
    """Testy integracji Pipeline z MemoryEcosystem"""
    
    def setUp(self):
        """Przygotowanie testowe - lostWorld tak w kazdym teście"""
        # Czyszczenie ewentualnychmodules
        self.ifc = None
        self.memory_ecosystem = None
        self.memory_integrator = None
        self.pipeline = None
    
    def tearDown(self):
        """Czyszczenie po teście"""
        self.ifc = None
        self.memory_ecosystem = None
        self.memory_integrator = None
        self.pipeline = None
    
    def test_memory_integrator_available_through_ifc(self):
        """Test dostępności MemoryIntegrator przez IFC"""
        from SSI_V5.ifc.registry import IFCRegistry
        from SSI_V5.memory.ecosystem import MemoryEcosystem
        from SSI_V5.memory.integrator import MemoryIntegrator
        
        # Tworzenie komponentów
        ifc = IFCRegistry()
        memory_ecosystem = MemoryEcosystem()
        memory_integrator = MemoryIntegrator(
            memory_ecosystem=memory_ecosystem,
            ifc=ifc
        )
        
        # Sprawdzenie rejestracji
        self.assertIsNotNone(ifc.get("memory_integrator"))
        self.assertEqual(ifc.get("memory_integrator"), memory_integrator)
    
    def test_pipeline_get_memory_integrator_with_ifc(self):
        """Test pobierania MemoryIntegrator przez Pipeline z IFC"""
        from SSI_V5.ifc.registry import IFCRegistry
        from SSI_V5.memory.ecosystem import MemoryEcosystem
        from SSI_V5.memory.integrator import MemoryIntegrator
        from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
        
        # Tworzenie componentów
        ifc = IFCRegistry()
        memory_ecosystem = MemoryEcosystem()
        memory_integrator = MemoryIntegrator(
            memory_ecosystem=memory_ecosystem,
            ifc=ifc
        )
        
        # Tworzenie pipeline z ifc
        pipeline = SSIPipeline(
            mode=PipelineMode.SINGLE,
            ifc=ifc,
            memory_ecosystem=memory_ecosystem
        )
        
        # Sprawdzenie pobierania MemoryIntegrator
        retrieved_integrator = pipeline._get_memory_integrator()
        self.assertIsNotNone(retrieved_integrator)
        self.assertEqual(retrieved_integrator, memory_integrator)
    
    def test_pipeline_memory_integrator_none_without_ifc(self):
        """Test zwracania None przez _get_memory_integrator() bez IFC"""
        from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
        
        # Tworzenie pipeline BEZ ifc
        pipeline = SSIPipeline(mode=PipelineMode.SINGLE)
        
        # Sprawdzenie pobierania MemoryIntegrator - powinno być None
        retrieved_integrator = pipeline._get_memory_integrator()
        self.assertIsNone(retrieved_integrator)
    
    def test_pipeline_get_memory_integrator_without_component(self):
        """Test zwracania None przez _get_memory_integrator() kiedy komponent nie zarejestrowany"""
        from SSI_V5.ifc.registry import IFCRegistry
        from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
        
        # Tworzenie IFC i pipeline
        ifc = IFCRegistry()
        pipeline = SSIPipeline(mode=PipelineMode.SINGLE, ifc=ifc)
        
        # Sprawdzenie pobierania MemoryIntegrator - powinno być None
        retrieved_integrator = pipeline._get_memory_integrator()
        self.assertIsNone(retrieved_integrator)


class TestPipelineMemoryUpdateMethod(unittest.TestCase):
    """Testy metody _run_memory_update() z MemoryIntegrator"""
    
    def test_prepare_cycle_data_for_memory_structure(self):
        """Test struktury danych zwracanych przez _prepare_cycle_data_for_memory()"""
        from SSI_V5.ifc.registry import IFCRegistry
        from SSI_V5.memory.ecosystem import MemoryEcosystem
        from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
        
        # Tworzenie pipeline
        pipeline = SSIPipeline(mode=PipelineMode.SINGLE)
        pipeline._current_cycle_id = "test_cycle_001"
        pipeline._cycle_counter = 1
        pipeline.world_name = "TEST_WORLD"
        
        # Przygotowanie testowych danych
        observation_data = {
            'decisions': {'agent_1': [{'type': 'test', 'value': 1}]},
            'output': {'consensus': True}
        }
        
        # Wywołanie metody
        cycle_data = pipeline._prepare_cycle_data_for_memory(observation_data)
        
        # Sprawdzenie struktury
        self.assertIn('cycle_id', cycle_data)
        self.assertEqual(cycle_data['cycle_id'], 'test_cycle_001')
        self.assertIn('timestamp', cycle_data)
        self.assertIn('world_name', cycle_data)
        self.assertEqual(cycle_data['world_name'], 'TEST_WORLD')
        self.assertIn('pipeline_mode', cycle_data)
        self.assertEqual(cycle_data['pipeline_mode'], 'single')
        self.assertIn('status', cycle_data)
        self.assertEqual(cycle_data['status'], 'complete')
        
        # Sprawdzenie danych etapas
        self.assertIn('agent_data', cycle_data)
        self.assertIn('collective_data', cycle_data)
        self.assertIn('observation_data', cycle_data)
        
        # Sprawdzenie metadanych
        self.assertIn('metadata', cycle_data)
        self.assertIn('source', cycle_data['metadata'])
        self.assertEqual(cycle_data['metadata']['source'], 'pipeline_memory_integration')
        self.assertIn('memory_integration_version', cycle_data['metadata'])
    
    def test_prepare_cycle_data_with_stage_results(self):
        """Test _prepare_cycle_data_for_memory() z wynikami etapow"""
        from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
        
        # Tworzenie pipeline
        pipeline = SSIPipeline(mode=PipelineMode.SINGLE)
        pipeline._current_cycle_id = "test_cycle_002"
        pipeline.world_name = "TEST_WORLD"
        
        # Ustawienie wyników etapów
        pipeline._last_world_result = {'status': 'success', 'world_data': {'leagues': 5}}
        pipeline._last_modeling_result = {'status': 'success', 'modeling_data': {'features': 10}}
        pipeline._last_teacher_result = {'status': 'success', 'teacher_data': {'patterns': 3}}
        pipeline._last_agent_result = {'status': 'success', 'decisions': {'agent_1': []}}
        pipeline._last_collective_result = {'status': 'success', 'consensus_reached': True}
        
        # Przygotowanie testowych danych
        observation_data = {'test': 'observation'}
        
        # Wywołanie metody
        cycle_data = pipeline._prepare_cycle_data_for_memory(observation_data)
        
        # Sprawdzenie danych etapa
        self.assertIn('world_data', cycle_data)
        self.assertEqual(cycle_data['world_data'], {'status': 'success', 'world_data': {'leagues': 5}})
        
        self.assertIn('modeling_data', cycle_data)
        self.assertEqual(cycle_data['modeling_data'], {'status': 'success', 'modeling_data': {'features': 10}})


class TestMemoryUpdateFallback(unittest.TestCase):
    """Testy fallback dla _run_memory_update()"""
    
    def test_memory_update_fallback_without_ifc(self):
        """Test fallback _run_memory_update() bez IFC"""
        from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
        
        # Tworzenie pipeline BEZ ifc
        pipeline = SSIPipeline(mode=PipelineMode.SINGLE)
        
        # Dodanie wsteczne memory_layer (do testu fabryki)
        pipeline.memory_layer = {'status': 'available'}
        
        # Wywołanie metody
        observation_data = {'test': 'data'}
        result = pipeline._run_memory_update(observation_data)
        
        # Sprawdzenie wyników
        self.assertEqual(result['status'], 'success')
        self.assertIn('memory_updates', result)
        self.assertIn('integration_mode', result)
        self.assertEqual(result['integration_mode'], 'fallback')
    
    def test_memory_update_fallback_without_memory_layer(self):
        """Test fallback _run_memory_update() bez memory_layer"""
        from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
        
        # Tworzenie pipeline BEZ ifc i memory_layer
        pipeline = SSIPipeline(mode=PipelineMode.SINGLE)
        pipeline.memory_layer = None  # Ustawione na None, aby nie było memory_layer
        
        # Wywołanie metody
        observation_data = {'test': 'data'}
        result = pipeline._run_memory_update(observation_data)
        
        # Sprawdzenie wyników - powinien byc error
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
        self.assertIn('integration_mode', result)
        self.assertEqual(result['integration_mode'], 'none')


class TestMemoryUpdateWithIntegrator(unittest.TestCase):
    """Testy _run_memory_update() z MemoryIntegrator"""
    
    def test_memory_update_with_memory_integrator(self):
        """Test _run_memory_update() z MemoryIntegrator przez IFC"""
        from SSI_V5.ifc.registry import IFCRegistry
        from SSI_V5.memory.ecosystem import MemoryEcosystem
        from SSI_V5.memory.integrator import MemoryIntegrator
        from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
        
        # Tworzenie componentów
        ifc = IFCRegistry()
        memory_ecosystem = MemoryEcosystem()
        memory_integrator = MemoryIntegrator(
            memory_ecosystem=memory_ecosystem,
            ifc=ifc
        )
        
        # Tworzenie pipeline
        pipeline = SSIPipeline(
            mode=PipelineMode.SINGLE,
            ifc=ifc,
            memory_ecosystem=memory_ecosystem
        )
        
        # Wywołanie _run_memory_update z danymi
        observation_data = {
            'decisions': {
                'agent_1': [
                    {'type': 'test_decision', 'confidence': 0.9, 'timestamp': datetime.now().isoformat()}
                ]
            },
            'output': {'consensus': True, 'confidence': 0.85}
        }
        
        result = pipeline._run_memory_update(observation_data)
        
        # Sprawdzenie wyników
        self.assertIn('status', result)
        self.assertIn('duration', result)
        self.assertIn('memory_updates', result)
        self.assertIn('integration_mode', result)
        
        # Sprawdzenie trybu integracji
        self.assertEqual(result['integration_mode'], 'memory_integrator')


class TestPipelineMemoryIntegrationFullCycle(unittest.TestCase):
    """Testy pełnego cyklu z integracją pamięci"""
    
    def test_pipeline_full_cycle_with_memory_integration(self):
        """Test pełnego cyklu pipeline z integracją pamięci - SCENARIUSZ IDEALNY"""
        from SSI_V5.ifc.registry import IFCRegistry
        from SSI_V5.memory.ecosystem import MemoryEcosystem
        from SSI_V5.memory.integrator import MemoryIntegrator
        from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
        
        # Tworzenie componentów
        ifc = IFCRegistry()
        memory_ecosystem = MemoryEcosystem()
        memory_integrator = MemoryIntegrator(
            memory_ecosystem=memory_ecosystem,
            ifc=ifc
        )
        
        # Tworzenie pipeline
        pipeline = SSIPipeline(
            mode=PipelineMode.TEST,
            world_name="MEMORY_INTEGRATION_TEST",
            ifc=ifc,
            memory_ecosystem=memory_ecosystem
        )
        
        # Inicjalizacja pipeline
        init_result = pipeline.initialize()
        self.assertEqual(init_result['status'], 'success')
        
        # Wykonanie cyklu
        cycle_result = pipeline.run_cycle()
        
        # Sprawdzenie wyników
        self.assertIn('status', cycle_result)
        self.assertIn('steps', cycle_result)
        
        # Sprawdzenie kroku memory_update
        if 'memory_update' in cycle_result['steps']:
            memory_step = cycle_result['steps']['memory_update']
            self.assertIn('status', memory_step)
            self.assertIn('memory_updates', memory_step)
            
            # integration_mode jest w memory_updates
            if 'memory_updates' in memory_step:
                memory_updates = memory_step['memory_updates']
                if isinstance(memory_updates, dict):
                    self.assertIn('integration_mode', memory_updates)
                    # Powinien być memory_integrator lub fallback
                    self.assertIn(memory_updates['integration_mode'], ['memory_integrator', 'fallback'])
            
            # Lub sprawdzenie bezpośrednio w suggestions
            if memory_step.get('integration_mode'):
                self.assertIn(memory_step['integration_mode'], ['memory_integrator', 'fallback'])


if __name__ == '__main__':
    # Uruchomienie testów
    unittest.main(verbosity=2)