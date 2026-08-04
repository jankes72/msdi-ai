# SSI V5 Tests - Pipeline Control Layer
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.3.2
# Data: 2026-08-03
# 
# Testy dla Pipeline:
# 1. Import
# 2. Inicjalizacja
# 3. Polaczenie z WorldEngine
# 4. Wykonanie pojedynczego cyklu
# 5. Wykonanie wielu cykli
# 6. Status systemu
# 7. Obsluga bledow

import unittest
import sys
import os
from datetime import datetime
import time

# Dodanie sciezki do SSI_V5 - poprawka dla Windows i struktury katalogow
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPipelineImports(unittest.TestCase):
    """Testy importu modulu Pipeline"""
    
    def test_import_from_core(self):
        """Test importu pipeline z SSI_V5.core"""
        try:
            from SSI_V5.core import SSIPipeline, CycleStatus, PipelineMode
            self.assertTrue(True, "Import z SSI_V5.core powiodl sie")
        except ImportError as e:
            self.fail(f"Import z SSI_V5.core nie powiodl sie: {e}")
    
    def test_import_from_core_pipeline(self):
        """Test importu z SSI_V5.core.pipeline"""
        try:
            from SSI_V5.core.pipeline import (
                SSIPipeline, CycleStatus, PipelineMode, CycleMetadata,
                PipelineStatus, AgentRuntimeInterface, create_pipeline, run_test_pipeline
            )
            self.assertTrue(True, "Import z SSI_V5.core.pipeline powiodl sie")
        except ImportError as e:
            self.fail(f"Import z SSI_V5.core.pipeline nie powiodl sie: {e}")
    
    def test_import_helper_functions(self):
        """Test importu funkcji pomocniczych"""
        try:
            from SSI_V5.core import create_pipeline, run_test_pipeline
            self.assertTrue(True, "Import funkcji pomocniczych powiodl sie")
        except ImportError as e:
            self.fail(f"Import funkcji pomocniczych nie powiodl sie: {e}")
    
    def test_import_world_engine_integration(self):
        """Test importu zintegrowanych komponentow"""
        try:
            from SSI_V5.core import WorldEngine, SSIPipeline
            self.assertTrue(True, "Import zintegrowanych komponentow powiodl sie")
        except ImportError as e:
            self.fail(f"Import zintegrowanych komponentow nie powiodl sie: {e}")


class TestCycleStatusEnum(unittest.TestCase):
    """Testy dla enum CycleStatus"""
    
    def test_cycle_status_values(self):
        """Test wartosci CycleStatus"""
        from SSI_V5.core.pipeline import CycleStatus
        
        expected_statuses = [
            'idle', 'initializing', 'world_generation', 'modeling',
            'teacher_analysis', 'agent_execution', 'observation',
            'memory_update', 'complete', 'error', 'shutdown'
        ]
        
        actual_statuses = [status.value for status in CycleStatus]
        
        for expected in expected_statuses:
            self.assertIn(expected, actual_statuses)
    
    def test_cycle_status_access(self):
        """Test dostepu do posczegolnych statusow"""
        from SSI_V5.core.pipeline import CycleStatus
        
        self.assertEqual(CycleStatus.IDLE.value, 'idle')
        self.assertEqual(CycleStatus.INITIALIZING.value, 'initializing')
        self.assertEqual(CycleStatus.COMPLETE.value, 'complete')
        self.assertEqual(CycleStatus.ERROR.value, 'error')


class TestPipelineModeEnum(unittest.TestCase):
    """Testy dla enum PipelineMode"""
    
    def test_pipeline_mode_values(self):
        """Test wartosci PipelineMode"""
        from SSI_V5.core.pipeline import PipelineMode
        
        expected_modes = ['test', 'production', 'single']
        actual_modes = [mode.value for mode in PipelineMode]
        
        for expected in expected_modes:
            self.assertIn(expected, actual_modes)
    
    def test_pipeline_mode_access(self):
        """Test dostepu do posczegolnych trybow"""
        from SSI_V5.core.pipeline import PipelineMode
        
        self.assertEqual(PipelineMode.TEST.value, 'test')
        self.assertEqual(PipelineMode.PRODUCTION.value, 'production')
        self.assertEqual(PipelineMode.SINGLE.value, 'single')


class TestCycleMetadata(unittest.TestCase):
    """Testy dla klasy CycleMetadata"""
    
    def test_create_metadata(self):
        """Test tworzenia metadanych cyklu"""
        from SSI_V5.core.pipeline import CycleMetadata, CycleStatus
        
        meta = CycleMetadata(
            cycle_id="test_001",
            start_time=datetime.now()
        )
        
        self.assertEqual(meta.cycle_id, "test_001")
        self.assertIsInstance(meta.start_time, datetime)
        self.assertEqual(meta.status, CycleStatus.IDLE)
        self.assertEqual(meta.world_name, "SSI_V5_WORLD")
    
    def test_get_duration(self):
        """Test obliczania czasu trwania"""
        from SSI_V5.core.pipeline import CycleMetadata
        import time
        
        start = datetime.now()
        time.sleep(0.1)
        end = datetime.now()
        
        meta = CycleMetadata(
            cycle_id="duration_test",
            start_time=start,
            end_time=end
        )
        
        duration = meta.get_duration()
        self.assertIsNotNone(duration)
        self.assertGreaterEqual(duration, 0.1)
    
    def test_add_step(self):
        """Test dodawania krokow"""
        from SSI_V5.core.pipeline import CycleMetadata
        
        meta = CycleMetadata(cycle_id="step_test", start_time=datetime.now())
        
        meta.add_step("world_generation")
        meta.add_step("modeling")
        meta.add_step("world_generation")  # Powtorny krok nie powinien byc dodany
        
        self.assertEqual(len(meta.processing_steps), 2)
        self.assertIn("world_generation", meta.processing_steps)
        self.assertIn("modeling", meta.processing_steps)
    
    def test_add_error(self):
        """Test dodawania bledow"""
        from SSI_V5.core.pipeline import CycleMetadata
        
        meta = CycleMetadata(cycle_id="error_test", start_time=datetime.now())
        
        meta.add_error("test_error", "Test error message", "world_generation")
        
        self.assertEqual(len(meta.errors), 1)
        self.assertEqual(meta.errors[0]['error_type'], "test_error")
        self.assertEqual(meta.errors[0]['error_message'], "Test error message")
        self.assertEqual(meta.errors[0]['step'], "world_generation")


class TestPipelineStatus(unittest.TestCase):
    """Testy dla klasy PipelineStatus"""
    
    def test_create_status(self):
        """Test tworzenia statusu Pipeline"""
        from SSI_V5.core.pipeline import PipelineStatus, CycleStatus, PipelineMode
        
        status = PipelineStatus()
        
        self.assertIsNone(status.current_cycle_id)
        self.assertEqual(status.current_status, CycleStatus.IDLE)
        self.assertEqual(status.total_cycles, 0)
        self.assertEqual(status.successful_cycles, 0)
        self.assertEqual(status.failed_cycles, 0)
    
    def test_to_dict(self):
        """Test konwersji statusu do slownika"""
        from SSI_V5.core.pipeline import PipelineStatus
        
        status = PipelineStatus(
            current_cycle_id="test_001",
            total_cycles=5,
            successful_cycles=4,
            failed_cycles=1
        )
        
        status_dict = status.to_dict()
        
        self.assertIsInstance(status_dict, dict)
        self.assertEqual(status_dict['current_cycle_id'], "test_001")
        self.assertEqual(status_dict['total_cycles'], 5)
        self.assertEqual(status_dict['successful_cycles'], 4)
        self.assertEqual(status_dict['failed_cycles'], 1)


class TestAgentRuntimeInterface(unittest.TestCase):
    """Testy dla interfejsu AgentRuntimeInterface"""
    
    def test_create_interface(self):
        """Test tworzenia interfejsu"""
        from SSI_V5.core.pipeline import AgentRuntimeInterface
        
        interface = AgentRuntimeInterface()
        
        self.assertIsNone(interface.pipeline_reference)
        self.assertEqual(interface.agents, [])
        self.assertFalse(interface.initialized)
        self.assertEqual(interface.cycle_count, 0)
    
    def test_interface_initialize(self):
        """Test inicjalizacji interfejsu"""
        from SSI_V5.core.pipeline import AgentRuntimeInterface
        
        interface = AgentRuntimeInterface()
        result = interface.initialize()
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(interface.initialized)
        self.assertEqual(interface.cycle_count, 0)
    
    def test_interface_execute_cycle(self):
        """Test wykonania cyklu przez interfejs"""
        from SSI_V5.core.pipeline import AgentRuntimeInterface
        
        interface = AgentRuntimeInterface()
        interface.initialize()
        
        result = interface.execute_cycle({'cycle_id': 'test_001'})
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['cycle_id'], 'test_001')
        self.assertEqual(interface.cycle_count, 1)
    
    def test_interface_observe(self):
        """Test obserwacji"""
        from SSI_V5.core.pipeline import AgentRuntimeInterface
        
        interface = AgentRuntimeInterface()
        
        result = interface.observe({'data': 'test'})
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['observations'], {'data': 'test'})
    
    def test_interface_shutdown(self):
        """Test zamkniecia interfejsu"""
        from SSI_V5.core.pipeline import AgentRuntimeInterface
        
        interface = AgentRuntimeInterface()
        interface.initialize()
        interface.execute_cycle()
        
        result = interface.shutdown()
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['total_cycles_executed'], 1)
        self.assertFalse(interface.initialized)
    
    def test_interface_add_agent(self):
        """Test dodawania agenta"""
        from SSI_V5.core.pipeline import AgentRuntimeInterface
        
        interface = AgentRuntimeInterface()
        
        agent_id = interface.add_agent({'name': 'TestAgent', 'type': 'test'})
        
        self.assertEqual(len(interface.agents), 1)
        self.assertEqual(interface.agents[0]['agent_id'], agent_id)
        self.assertEqual(interface.agents[0]['name'], 'TestAgent')


class TestSSIPipelineInitialization(unittest.TestCase):
    """Testy inicjalizacji Pipeline"""
    
    def test_create_pipeline_default(self):
        """Test tworzenia Pipeline z parametrami domyslnymi"""
        from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
        
        pipeline = SSIPipeline()
        
        self.assertIsInstance(pipeline, SSIPipeline)
        self.assertEqual(pipeline.mode, PipelineMode.SINGLE)
        self.assertEqual(pipeline.world_name, "SSI_V5_WORLD")
        # agent_interface jest None aż do wywołania initialize()
        # self.assertIsNotNone(pipeline.agent_interface)
        self.assertFalse(pipeline._initialized)
    
    def test_create_pipeline_with_mode(self):
        """Test tworzenia Pipeline z okreslonym trybem"""
        from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
        
        pipeline = SSIPipeline(mode=PipelineMode.TEST, world_name="TEST_WORLD")
        
        self.assertEqual(pipeline.mode, PipelineMode.TEST)
        self.assertEqual(pipeline.world_name, "TEST_WORLD")
    
    def test_pipeline_initialize(self):
        """Test inicjalizacji Pipeline"""
        from SSI_V5.core.pipeline import SSIPipeline
        
        pipeline = SSIPipeline()
        result = pipeline.initialize()
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(pipeline._initialized)
        self.assertIsNotNone(pipeline.world_engine)
        self.assertIn('components', result)
    
    def test_pipeline_initialize_components(self):
        """Test inicjalizacji komponentow w Pipeline"""
        from SSI_V5.core.pipeline import SSIPipeline
        from SSI_V5.core import WorldEngine
        
        pipeline = SSIPipeline()
        result = pipeline.initialize()
        
        self.assertEqual(result['components']['world_engine'], 'initialized')
        self.assertIsInstance(pipeline.world_engine, WorldEngine)
        self.assertIn('modeling_layer', result['components'])
        self.assertIn('teacher_layer', result['components'])


class TestSSIPipelineSingleCycle(unittest.TestCase):
    """Testy wykonania pojedynczego cyklu"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.pipeline import SSIPipeline
        self.pipeline = SSIPipeline()
        self.pipeline.initialize()
    
    def test_run_single_cycle(self):
        """Test wykonania pojedynczego cyklu"""
        cycle_result = self.pipeline.run_cycle()
        
        self.assertEqual(cycle_result['status'], 'success')
        self.assertIn('cycle_id', cycle_result)
        self.assertIn('start_time', cycle_result)
        self.assertIn('end_time', cycle_result)
        self.assertIn('duration', cycle_result)
        self.assertIn('steps', cycle_result)
    
    def test_single_cycle_steps(self):
        """Test krokow pojedynczego cyklu"""
        cycle_result = self.pipeline.run_cycle()
        
        expected_steps = [
            'world_generation', 'modeling', 'teacher_analysis',
            'agent_execution', 'observation', 'memory_update'
        ]
        
        for step in expected_steps:
            self.assertIn(step, cycle_result['steps'])
            self.assertEqual(cycle_result['steps'][step]['status'], 'success')
    
    def test_single_cycle_with_custom_data(self):
        """Test cyklu z niestandardowymi danymi generatora"""
        custom_data = {
            'X': [[1.5, 2.0], [0.8, 1.2]],
            'Y': ['3:1', '2:2'],
            'features': {
                'feat1': [1.0, 2.0],
                'feat2': [0.5, 1.5]
            }
        }
        
        cycle_result = self.pipeline.run_cycle(generator_data=custom_data)
        
        self.assertEqual(cycle_result['status'], 'success')
    
    def test_single_cycle_status_update(self):
        """Test aktualizacji statusu po cyklu"""
        self.pipeline.run_cycle()
        
        status = self.pipeline.get_status()
        
        self.assertEqual(status['total_cycles'], 1)
        self.assertEqual(status['successful_cycles'], 1)
        self.assertEqual(status['failed_cycles'], 0)


class TestSSIPipelineMultipleCycles(unittest.TestCase):
    """Testy wykonania wielu cykli"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
        self.pipeline = SSIPipeline(mode=PipelineMode.TEST)
        self.pipeline.initialize()
    
    def test_run_multiple_cycles(self):
        """Test wykonania wieli cykli"""
        result = self.pipeline.run_cycles(number=3, delay=0.01)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['total_cycles'], 3)
        self.assertEqual(len(result['cycle_results']), 3)
    
    def test_multiple_cycles_summary(self):
        """Test podsumowania wielu cykli"""
        result = self.pipeline.run_cycles(number=5, delay=0.01)
        
        self.assertIn('successful_cycles', result)
        self.assertIn('failed_cycles', result)
        self.assertIn('total_duration', result)
        self.assertIn('start_time', result)
        self.assertIn('end_time', result)
    
    def test_multiple_cycles_history(self):
        """Test historii wielu cykli"""
        self.pipeline.run_cycles(number=3, delay=0.01)
        
        history = self.pipeline.get_cycle_history()
        
        self.assertEqual(len(history), 3)
        for cycle in history:
            self.assertIn('cycle_id', cycle)
            self.assertIn('start_time', cycle)
            self.assertIn('end_time', cycle)
            self.assertIn('status', cycle)


class TestSSIPipelineStatus(unittest.TestCase):
    """Testy statusu Pipeline"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.pipeline import SSIPipeline
        self.pipeline = SSIPipeline()
        self.pipeline.initialize()
    
    def test_get_status(self):
        """Test pobierania statusu"""
        status = self.pipeline.get_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('current_cycle_id', status)
        self.assertIn('current_status', status)
        self.assertIn('total_cycles', status)
        self.assertIn('mode', status)
    
    def test_status_after_cycles(self):
        """Test statusu po wykonaniu cykli"""
        self.pipeline.run_cycles(number=2, delay=0.01)
        
        status = self.pipeline.get_status()
        
        self.assertEqual(status['total_cycles'], 2)
        self.assertEqual(status['successful_cycles'], 2)
        self.assertEqual(status['failed_cycles'], 0)
        self.assertEqual(status['cycle_history_count'], 2)


class TestSSIPipelineErrorHandling(unittest.TestCase):
    """Testy obslugi bledow w Pipeline"""
    
    def test_uninitialized_run_cycle(self):
        """Test uruchomienia cyklu bez inicjalizacji"""
        from SSI_V5.core.pipeline import SSIPipeline
        
        pipeline = SSIPipeline()
        result = pipeline.run_cycle()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('not initialized', result['error'])
    
    def test_uninitialized_run_cycles(self):
        """Test uruchomienia wielu cykli bez inicjalizacji"""
        from SSI_V5.core.pipeline import SSIPipeline
        
        pipeline = SSIPipeline()
        result = pipeline.run_cycles(number=3)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('not initialized', result['error'])
    
    def test_shutdown_before_initialization(self):
        """Test zamkniecia przed inicjalizacja"""
        from SSI_V5.core.pipeline import SSIPipeline
        
        pipeline = SSIPipeline()
        result = pipeline.shutdown()
        
        self.assertEqual(result['status'], 'success')


class TestSSIPipelineShutdown(unittest.TestCase):
    """Testy zamkniecia Pipeline"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.pipeline import SSIPipeline
        self.pipeline = SSIPipeline()
        self.pipeline.initialize()
    
    def test_shutdown(self):
        """Test zamkniecia Pipeline"""
        self.pipeline.run_cycles(number=2, delay=0.01)
        result = self.pipeline.shutdown()
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('final_status', result)
        self.assertIn('cycles_completed', result)
        self.assertIn('uptime_duration', result)
    
    def test_shutdown_clears_flags(self):
        """Test czy shutdown wyczysci flagi"""
        self.pipeline.run_cycle()
        self.pipeline.shutdown()
        
        self.assertFalse(self.pipeline._initialized)
        self.assertFalse(self.pipeline._shutdown_requested)
        self.assertIsNone(self.pipeline.world_engine)


class TestSSIPipelineReset(unittest.TestCase):
    """Testy resetowania Pipeline"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.pipeline import SSIPipeline
        self.pipeline = SSIPipeline()
        self.pipeline.initialize()
    
    def test_reset_pipeline(self):
        """Test resetowania Pipeline"""
        self.pipeline.run_cycles(number=3, delay=0.01)
        
        reset_result = self.pipeline.reset_pipeline()
        
        self.assertEqual(reset_result['status'], 'success')
        self.assertEqual(reset_result['cycles_cleared'], 3)
        
        # Po resecie powinno byc 0 cykli w historii
        history = self.pipeline.get_cycle_history()
        self.assertEqual(len(history), 0)


class TestSSIPipelineEventLog(unittest.TestCase):
    """Testy dziennika zdarzen Pipeline"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.pipeline import SSIPipeline
        self.pipeline = SSIPipeline()
        self.pipeline.initialize()
    
    def test_event_log_after_initialize(self):
        """Test dziennika zdarzen po inicjalizacji"""
        event_log = self.pipeline.get_event_log()
        
        self.assertIsInstance(event_log, list)
        self.assertTrue(len(event_log) > 0)
        
        # Powinny byc zdarzenia inicjalizacji
        init_events = [e for e in event_log if 'INITIALIZATION' in e['event_type']]
        self.assertTrue(len(init_events) >= 1)
    
    def test_event_log_after_cycles(self):
        """Test dziennika zdarzen po cyklach"""
        self.pipeline.run_cycles(number=2, delay=0.01)
        
        event_log = self.pipeline.get_event_log()
        
        # Powinny byc zdarzenia cykli
        cycle_events = [e for e in event_log if 'CYCLE' in e['event_type']]
        self.assertTrue(len(cycle_events) > 0)


class TestSSIPipelineHelperFunctions(unittest.TestCase):
    """Testy funkcji pomocniczych Pipeline"""
    
    def test_create_pipeline_function(self):
        """Test fabryki create_pipeline"""
        from SSI_V5.core.pipeline import create_pipeline, PipelineMode, SSIPipeline
        
        pipeline = create_pipeline(mode=PipelineMode.TEST, world_name="HELPER_TEST")
        
        self.assertIsInstance(pipeline, SSIPipeline)
        self.assertEqual(pipeline.mode, PipelineMode.TEST)
        self.assertEqual(pipeline.world_name, "HELPER_TEST")
    
    def test_run_test_pipeline_function(self):
        """Test funkcji run_test_pipeline"""
        from SSI_V5.core.pipeline import run_test_pipeline
        
        result = run_test_pipeline(number_of_cycles=2, world_name="AUTO_TEST")
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('initialization', result)
        self.assertIn('test_results', result)
        self.assertIn('shutdown', result)
        self.assertIn('final_status', result)
        
        # Sprawdzenie wynikow testowych
        test_results = result['test_results']
        self.assertEqual(test_results['total_cycles'], 2)


class TestSSIPipelineWorldEngineIntegration(unittest.TestCase):
    """Testy integracji Pipeline z WorldEngine"""
    
    def test_world_engine_available(self):
        """Test dostepnosci WorldEngine w Pipeline"""
        from SSI_V5.core.pipeline import SSIPipeline
        from SSI_V5.core import WorldEngine
        
        pipeline = SSIPipeline()
        pipeline.initialize()
        
        self.assertIsInstance(pipeline.world_engine, WorldEngine)
        self.assertEqual(pipeline.world_engine.world_name, "SSI_V5_WORLD")
    
    def test_world_engine_used_in_cycle(self):
        """Test uzycia WorldEngine w cyklu"""
        from SSI_V5.core.pipeline import SSIPipeline
        
        pipeline = SSIPipeline()
        pipeline.initialize()
        
        # Uruchomienie cyklu
        cycle_result = pipeline.run_cycle()
        
        # Sprawdzenie czy WorldEngine zostal uzyty
        self.assertIn('world_generation', cycle_result['steps'])
        self.assertEqual(cycle_result['steps']['world_generation']['status'], 'success')


class TestSSIPipelineTeacherIntegration(unittest.TestCase):
    """Testy integracji Pipeline z Teacher Layer"""
    
    def test_teacher_layer_in_cycle(self):
        """Test uzycia Teacher Layer w cyklu"""
        from SSI_V5.core.pipeline import SSIPipeline
        
        pipeline = SSIPipeline()
        pipeline.initialize()
        
        cycle_result = pipeline.run_cycle()
        
        # Sprawdzenie czy Teacher Layer zostal uzyty
        self.assertIn('teacher_analysis', cycle_result['steps'])
        self.assertEqual(cycle_result['steps']['teacher_analysis']['status'], 'success')
    
    def test_teacher_components_initialized(self):
        """Test inicjalizacji komponentow Teacher Layer"""
        from SSI_V5.core.pipeline import SSIPipeline
        
        pipeline = SSIPipeline()
        result = pipeline.initialize()
        
        self.assertEqual(result['components']['teacher_layer'], 'available')


if __name__ == '__main__':
    # Uruchomienie testow
    unittest.main(verbosity=2)
