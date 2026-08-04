# SSI V5 Tests - World Engine
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.3.1
# Data: 2026-08-03
# 
# Testy dla WorldEngine:
# 1. Import
# 2. Inicjalizacja
# 3. Kontrakt danych
# 4. Integracja z Teacher Layer

import unittest
import sys
import os
from datetime import datetime
import pandas as pd
import numpy as np

# Dodanie sciezki do SSI_V5 - poprawka dla Windows i struktury katalogow
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWorldEngineImports(unittest.TestCase):
    """Testy importu modulu WorldEngine"""
    
    def test_import_from_core(self):
        """Test importuworld_engine z SSI_V5.core"""
        try:
            from SSI_V5.core import WorldEngine, WorldEngineOutput, ProcessingContext
            self.assertTrue(True, "Import z SSI_V5.core powiodl sie")
        except ImportError as e:
            self.fail(f"Import z SSI_V5.core nie powiodl sie: {e}")
    
    def test_import_from_core_world_engine(self):
        """Test importu z SSI_V5.core.world_engine"""
        try:
            from SSI_V5.core.world_engine import WorldEngine, WorldEngineOutput, ProcessingContext
            self.assertTrue(True, "Import z SSI_V5.core.world_engine powiodl sie")
        except ImportError as e:
            self.fail(f"Import z SSI_V5.core.world_engine nie powiodl sie: {e}")
    
    def test_import_helper_functions(self):
        """Test importu funkcji pomocniczych"""
        try:
            from SSI_V5.core import (
                create_world_engine_from_generator,
                create_world_engineOutput_from_dict
            )
            self.assertTrue(True, "Import funkcji pomocniczych powiodl sie")
        except ImportError as e:
            self.fail(f"Import funkcji pomocniczych nie powiodl sie: {e}")


class TestWorldEngineOutput(unittest.TestCase):
    """Testy dla klasy WorldEngineOutput (kontrakt danych)"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.world_engine import WorldEngineOutput
        self.WorldEngineOutput = WorldEngineOutput
    
    def test_create_empty_output(self):
        """Test tworzenia pustego kontraktu"""
        output = self.WorldEngineOutput()
        
        self.assertIsInstance(output, self.WorldEngineOutput)
        self.assertEqual(output.results, {})
        self.assertEqual(output.features, {})
        self.assertEqual(output.models, {})
        self.assertEqual(output.predictions, {})
        self.assertEqual(output.observations, {})
        self.assertEqual(output.metadata, {})
    
    def test_create_output_with_data(self):
        """Test tworzenia kontraktu z danymi"""
        output = self.WorldEngineOutput(
            results={'Y': [1, 2, 3]},
            features={'X': [10, 20, 30]},
            metadata={'test': True}
        )
        
        self.assertEqual(output.results, {'Y': [1, 2, 3]})
        self.assertEqual(output.features, {'X': [10, 20, 30]})
        self.assertEqual(output.metadata, {'test': True})
    
    def test_to_dict(self):
        """Test konwersji do slownika"""
        output = self.WorldEngineOutput(
            results={'Y': [1, 2, 3]},
            features={'X': [10, 20, 30]},
            metadata={'test': True}
        )
        
        result = output.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertIn('results', result)
        self.assertIn('features', result)
        self.assertIn('metadata', result)
        self.assertEqual(result['results'], {'Y': [1, 2, 3]})
    
    def test_to_json(self):
        """Test konwersji do JSON"""
        output = self.WorldEngineOutput(
            results={'Y': [1, 2, 3]},
            features={'X': [10, 20, 30]},
            metadata={'test': True}
        )
        
        json_str = output.to_json()
        
        self.assertIsInstance(json_str, str)
        self.assertIn('"results"', json_str)
        self.assertIn('"features"', json_str)
        self.assertIn('"metadata"', json_str)
    
    def test_update_metadata(self):
        """Test aktualizacji metadanych"""
        output = self.WorldEngineOutput()
        
        output.update_metadata('cycle_id', 'test_001')
        
        self.assertIn('cycle_id', output.metadata)
        self.assertEqual(output.metadata['cycle_id'], 'test_001')
        self.assertIn('last_update', output.metadata)


class TestProcessingContext(unittest.TestCase):
    """Testy dla klasy ProcessingContext"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.world_engine import ProcessingContext
        self.ProcessingContext = ProcessingContext
    
    def test_create_context(self):
        """Test tworzenia kontekstu"""
        context = self.ProcessingContext(
            cycle_id="test_001",
            world_name="TEST_WORLD"
        )
        
        self.assertEqual(context.cycle_id, "test_001")
        self.assertEqual(context.world_name, "TEST_WORLD")
        self.assertIsInstance(context.timestamp, datetime)
        self.assertEqual(context.generator_reference, "SSI_V5_SPORTS_WORLD_MODEL_GENERATOR")
    
    def test_default_values(self):
        """Test wartosci domyslnych"""
        context = self.ProcessingContext(
            cycle_id="test_002"
        )
        
        self.assertEqual(context.world_name, "SSI_V5_WORLD")
        self.assertEqual(context.stage, "world_generation")


class TestWorldEngineInitialization(unittest.TestCase):
    """Testy inicjalizacji WorldEngine"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.world_engine import WorldEngine
        self.WorldEngine = WorldEngine
    
    def test_create_engine_default(self):
        """Test tworzenia silnika z parametrami domyslnymi"""
        engine = self.WorldEngine()
        
        self.assertIsInstance(engine, self.WorldEngine)
        self.assertEqual(engine.world_name, "SSI_V5_WORLD")
        self.assertEqual(engine.generator_data, {})
        self.assertTrue(engine._is_initialized)
    
    def test_create_engine_with_world_name(self):
        """Test tworzenia silnika z nazwa swiata"""
        engine = self.WorldEngine(world_name="TEST_WORLD")
        
        self.assertEqual(engine.world_name, "TEST_WORLD")
        self.assertIn("TEST_WORLD", engine.context.cycle_id)
    
    def test_create_engine_with_generator_data(self):
        """Test tworzenia silnika z danymi generatora"""
        test_data = {
            'results': {'Y': [1, 2, 3]},
            'features': {'X': [10, 20, 30]}
        }
        
        engine = self.WorldEngine(generator_data=test_data)
        
        self.assertEqual(engine.generator_data, test_data)
    
    def test_create_engine_with_context(self):
        """Test tworzenia silnika z kontekstem"""
        from SSI_V5.core.world_engine import ProcessingContext
        
        context = ProcessingContext(
            cycle_id="custom_001",
            world_name="CUSTOM_WORLD"
        )
        
        engine = self.WorldEngine(context=context)
        
        self.assertEqual(engine.context.cycle_id, "custom_001")
        self.assertEqual(engine.context.world_name, "CUSTOM_WORLD")
    
    def test_processing_stage_initialization(self):
        """Test etapu przetwarzania po inicjalizacji"""
        engine = self.WorldEngine()
        
        # Po inicjalizacji powinien byc gotowy
        self.assertEqual(engine.get_processing_stage(), "ready")


class TestWorldEngineDataProcessing(unittest.TestCase):
    """Testy przetwarzania danych w WorldEngine"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.world_engine import WorldEngine
        self.WorldEngine = WorldEngine
    
    def test_receive_from_generator(self):
        """Test odbioru danych z generatora"""
        engine = self.WorldEngine()
        
        test_data = {
            'Y': [1, 2, 3],
            'X': [10, 20, 30],
            'metadata': {'source': 'generator'}
        }
        
        engine.receive_from_generator(test_data, generator_name="TEST_GEN")
        
        self.assertEqual(engine.generator_data, test_data)
        self.assertEqual(engine.context.generator_reference, "TEST_GEN")
        self.assertEqual(engine.get_processing_stage(), "data_received")
    
    def test_prepare_contract_empty_data(self):
        """Test przygotowania kontraktu z pustymi danymi"""
        engine = self.WorldEngine()
        
        contract = engine.prepare_contract()
        
        from SSI_V5.core.world_engine import WorldEngineOutput
        self.assertIsInstance(contract, WorldEngineOutput)
        self.assertIn('cycle_id', contract.metadata)
        self.assertIn('engine_version', contract.metadata)
        self.assertEqual(contract.metadata['engine_version'], 'SSI_V5_ETAPE_5.2.4_FAZA_3.3.1')
    
    def test_prepare_contract_with_results(self):
        """Test przygotowania kontraktu z danymi results"""
        engine = self.WorldEngine()
        
        test_data = {
            'results': {'Y': [1, 2, 3], 'accuracy': 0.95}
        }
        
        engine.receive_from_generator(test_data)
        contract = engine.prepare_contract()
        
        # Sprawdzamy czy dane zostaly zmapowane do results
        self.assertTrue(len(contract.results) > 0, "Results powinien nie byc pusty")
        # Dane z generator_data['results'] zostaja przypisane jako zawartosc contract.results
        self.assertEqual(contract.results, {'Y': [1, 2, 3], 'accuracy': 0.95})
    
    def test_prepare_contract_with_features(self):
        """Test przygotowania kontraktu z danymi features"""
        engine = self.WorldEngine()
        
        test_data = {
            'features': {'X1': [1, 2, 3], 'X2': [4, 5, 6]}
        }
        
        engine.receive_from_generator(test_data)
        contract = engine.prepare_contract()
        
        # Dane z generator_data['features'] zostaja przypisane jako zawartosc contract.features
        self.assertEqual(contract.features, {'X1': [1, 2, 3], 'X2': [4, 5, 6]})
    
    def test_prepare_contract_auto_extraction(self):
        """Test automatycznego wydobywania danych z generatora"""
        engine = self.WorldEngine()
        
        # Dane generatora z typowymi kluczami
        test_data = {
            'Y': [1, 2, 3],  # Powinien zostać wydobywany do results
            'X': [10, 20, 30],  # Powinien zostać wydobywany do features
            'modele': {'model1': {}, 'model2': {}},  # Powinien zostać wydobywany do models
            'predykcje': [0.1, 0.2, 0.3]  # Powinien zostać wydobywany do predictions
        }
        
        engine.receive_from_generator(test_data)
        contract = engine.prepare_contract()
        
        # Sprawdzamy czy dane zostaly wydobyte
        self.assertTrue(len(contract.results) > 0, "Results nie zostaly wydobyte")
        self.assertTrue(len(contract.features) > 0, "Features nie zostaly wydobyte")
        self.assertTrue(len(contract.models) > 0, "Models nie zostaly wydobyte")
        self.assertTrue(len(contract.predictions) > 0, "Predictions nie zostaly wydobyte")
    
    def test_process_full_flow(self):
        """Test pelnego przeplywu process()"""
        engine = self.WorldEngine()
        
        test_data = {
            'Y': [1, 2, 3],
            'X': [10, 20, 30]
        }
        
        contract = engine.process(generator_data=test_data)
        
        from SSI_V5.core.world_engine import WorldEngineOutput
        self.assertIsInstance(contract, WorldEngineOutput)
        self.assertEqual(engine.get_processing_stage(), "processed")
        
        # Sprawdzamy historię cykli
        history = engine.get_cycle_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].metadata['cycle_id'], engine.context.cycle_id)


class TestWorldEngineCycleHistory(unittest.TestCase):
    """Testy historii cykli WorldEngine"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.world_engine import WorldEngine
        self.WorldEngine = WorldEngine
    
    def test_cycle_history_multiple_cycles(self):
        """Test historii wielu cykli"""
        engine = self.WorldEngine()
        
        # Wykonanie kilku cykli
        for i in range(3):
            test_data = {
                'Y': [i, i+1, i+2],
                'X': [i*10, (i+1)*10, (i+2)*10]
            }
            engine.process(generator_data=test_data)
        
        history = engine.get_cycle_history()
        self.assertEqual(len(history), 3)
    
    def test_cycle_history_limit(self):
        """Test historii z limitowaniem"""
        engine = self.WorldEngine()
        
        # Wykonanie 5 cykli
        for i in range(5):
            test_data = {'Y': [i]}
            engine.process(generator_data=test_data)
        
        # Pobranie ostatnich 2 cykli
        history = engine.get_cycle_history(limit=2)
        self.assertEqual(len(history), 2)
    
    def test_reset_cycle(self):
        """Test resetowania cyklu"""
        engine = self.WorldEngine(world_name="RESET_TEST")
        
        # Wykonanie cyklu
        engine.process(generator_data={'Y': [1, 2, 3]})
        self.assertEqual(len(engine.get_cycle_history()), 1)
        
        # Reset
        engine.reset_cycle()
        
        # Sprawdzamy czy historia zostala wyczyszczona
        self.assertEqual(len(engine.get_cycle_history()), 1)  # Reset nie czysci historii
        self.assertEqual(engine.generator_data, {})
        self.assertEqual(engine.get_processing_stage(), "initialized")


class TestWorldEngineModelingIntegration(unittest.TestCase):
    """Testy integracji z Modeling Layer"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.world_engine import WorldEngine, WorldEngineOutput
        self.WorldEngine = WorldEngine
        self.WorldEngineOutput = WorldEngineOutput
    
    def test_send_to_modeling_success(self):
        """Test powodzenia przekazania do Modeling Layer"""
        engine = self.WorldEngine()
        
        # Przygotowanie kontraktu
        contract = self.WorldEngineOutput(
            features={'main': {'x1': [1, 2, 3], 'x2': [4, 5, 6]}},
            metadata={'cycle_id': 'test_modeling'}
        )
        
        result = engine.send_to_modeling(contract)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['layer'], 'modeling')
        self.assertEqual(result['contract_id'], 'test_modeling')
        self.assertIn('features_processed', result)
        self.assertEqual(engine.get_processing_stage(), "modeling_sent")
    
    def test_send_to_modeling_with_normalization(self):
        """Test przekazania do Modeling Layer z normalizacja"""
        engine = self.WorldEngine()
        
        # Przygotowanie kontraktu z DataFrame
        df_data = pd.DataFrame({
            'x1': [1, 2, 3],
            'x2': [4, 5, 6]
        })
        
        contract = self.WorldEngineOutput(
            features={'main': df_data.to_dict()},
            metadata={'cycle_id': 'test_normalization'}
        )
        
        result = engine.send_to_modeling(contract)
        
        self.assertEqual(result['status'], 'success')
        # Normalizacja powinna sie powioc (normalizuj_dataframe akceptuje dict)
        self.assertIn('features_shape', result)


class TestWorldEngineTeacherIntegration(unittest.TestCase):
    """Testy integracji z Teacher Layer"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.world_engine import WorldEngine, WorldEngineOutput
        self.WorldEngine = WorldEngine
        self.WorldEngineOutput = WorldEngineOutput
    
    def test_send_to_teacher_success(self):
        """Test powodzenia przekazania do Teacher Layer"""
        engine = self.WorldEngine()
        
        contract = self.WorldEngineOutput(
            metadata={'cycle_id': 'test_teacher'}
        )
        
        result = engine.send_to_teacher(contract)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['layer'], 'teacher')
        self.assertEqual(result['contract_id'], 'test_teacher')
        self.assertIn('processing_start', result)
        self.assertIn('processing_end', result)
        self.assertEqual(engine.get_processing_stage(), "teacher_sent")
    
    def test_send_to_teacher_with_cognitive_teacher(self):
        """Test przekazania do Teacher Layer z CognitiveTeacher"""
        engine = self.WorldEngine()
        
        # Przygotowanie kontraktu z danymi odpowiednimi dla CognitiveTeacher
        contract = self.WorldEngineOutput(
            features={'main': {
                'atak_gospodarzy': [1.5, 2.0, 1.8],
                'obrona_gospodarzy': [1.2, 1.0, 1.4],
                'atak_gosci': [1.3, 1.6, 1.9],
                'obrona_gosci': [1.1, 0.9, 1.0]
            }},
            results={'main': {
                'wynik': ['2:1', '3:2', '1:0']
            }},
            metadata={'cycle_id': 'test_cognitive'}
        )
        
        result = engine.send_to_teacher(contract)
        
        self.assertEqual(result['status'], 'success')
        # Powinien zainicjalizowac CognitiveTeacher
        self.assertTrue(result.get('cognitive_teacher_initialized', False) or 
                       'cognitive_teacher' in result)
    
    def test_send_to_teacher_components_initialization(self):
        """Test inicjalizacji komponentow Teacher Layer"""
        engine = self.WorldEngine()
        
        contract = self.WorldEngineOutput(
            metadata={'cycle_id': 'test_components'}
        )
        
        result = engine.send_to_teacher(contract)
        
        # Sprawdzamy czy zostały zainicjalizowane wszystkie komponenty
        self.assertTrue(result.get('world_hierarchy_initialized', False))
        self.assertTrue(result.get('DynamicWeightsManager_initialized', False) or 
                       'DynamicWeightsManager' in result)
        self.assertTrue(result.get('MemoryManager_initialized', False) or 
                       'MemoryManager' in result)
        self.assertTrue(result.get('ModelEvaluator_initialized', False) or 
                       'ModelEvaluator' in result)


class TestWorldEngineHelperFunctions(unittest.TestCase):
    """Testy funkcji pomocniczych WorldEngine"""
    
    def test_create_world_engine_from_generator(self):
        """Test fabryki create_world_engine_from_generator"""
        from SSI_V5.core.world_engine import create_world_engine_from_generator
        
        engine = create_world_engine_from_generator(
            generator_reference="TEST_GENERATOR",
            world_name="FACTORY_WORLD"
        )
        
        self.assertEqual(engine.context.generator_reference, "TEST_GENERATOR")
        self.assertEqual(engine.world_name, "FACTORY_WORLD")
    
    def test_create_world_engineOutput_from_dict(self):
        """Test fabryki create_world_engineOutput_from_dict"""
        from SSI_V5.core.world_engine import create_world_engineOutput_from_dict
        
        test_data = {
            'results': {'Y': [1, 2, 3]},
            'features': {'X': [4, 5, 6]},
            'metadata': {'test': True}
        }
        
        output = create_world_engineOutput_from_dict(test_data)
        
        self.assertEqual(output.results, {'Y': [1, 2, 3]})
        self.assertEqual(output.features, {'X': [4, 5, 6]})
        self.assertEqual(output.metadata, {'test': True})


class TestWorldEngineEventLog(unittest.TestCase):
    """Testy dziennika zdarzen WorldEngine"""
    
    def setUp(self):
        """Ustawienie testowe"""
        from SSI_V5.core.world_engine import WorldEngine
        self.WorldEngine = WorldEngine
    
    def test_event_log_initialization(self):
        """Test dziennika zdarzen po inicjalizacji"""
        engine = self.WorldEngine()
        
        log = engine.get_event_log()
        self.assertIsInstance(log, list)
        self.assertTrue(len(log) > 0, "Dziennik zdarzen powinien zawierac zdarzenie inicjalizacji")
        
        # Sprawdzamy zdarzenie inicjalizacji
        init_event = log[0]
        self.assertEqual(init_event['event_type'], 'engine_initialized')
    
    def test_event_log_after_receive(self):
        """Test dziennika zdarzen po odbiorze danych"""
        engine = self.WorldEngine()
        
        test_data = {'Y': [1, 2, 3]}
        engine.receive_from_generator(test_data)
        
        log = engine.get_event_log()
        self.assertTrue(len(log) >= 2, "Powinny byc co najmniej 2 zdarzenia")
        
        # Szukamy zdarzenia odbioru danych
        receive_events = [e for e in log if e['event_type'] == 'data_received_from_generator']
        self.assertTrue(len(receive_events) >= 1, "Powinno byc zdarzenie odbioru danych")
    
    def test_event_log_after_process(self):
        """Test dziennika zdarzen po przetworzeniu"""
        engine = self.WorldEngine()
        
        test_data = {'Y': [1, 2, 3]}
        engine.process(generator_data=test_data)
        
        log = engine.get_event_log()
        
        # Szukamy zdarzenia zakonczenia przetwarzania
        process_events = [e for e in log if e['event_type'] == 'processing_complete']
        self.assertTrue(len(process_events) >= 1, "Powinno byc zdarzenie zakonczenia przetwarzania")


if __name__ == '__main__':
    # Uruchomienie testow
    unittest.main(verbosity=2)
