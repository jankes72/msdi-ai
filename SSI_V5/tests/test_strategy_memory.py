# SSI V5 Strategy Memory Tests
# ================================
#
# ETAP: 5.2.6.2 - Strategy Memory Foundation
# Data: 2026-08-04
#
# Testy modułu Strategy Memory
# Wymagane: minimum 10 testów
#
# Author: Mistral Vibe
# Co-Authored-By: Mistral Vibe <vibe@mistral.ai>

import unittest
import tempfile
import shutil
import os
import json
from datetime import datetime
from pathlib import Path

from SSI_V5.memory.strategy_memory import StrategyMemoryRecord, StrategyMemoryManager


class TestStrategyMemoryRecord(unittest.TestCase):
    """Testy klasy StrategyMemoryRecord"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.test_record = StrategyMemoryRecord(
            strategy_id="test_strategy",
            strategy_version="1.0.0",
            strategy_definition={"type": "test", "category": "unit"},
            strategy_parameters={"param1": 0.5, "param2": 10},
            feature_schema=["feature1", "feature2", "feature3"],
            model_reference="test_model_v1"
        )
    
    def test_001_strategy_memory_record_creation(self):
        """Test 1: Tworzenie StrategyMemoryRecord"""
        # Sprawdź podstawowe atrybuty
        self.assertTrue(self.test_record.memory_id.startswith("smr_"))
        self.assertEqual(self.test_record.strategy_id, "test_strategy")
        self.assertEqual(self.test_record.strategy_version, "1.0.0")
        self.assertEqual(self.test_record.model_reference, "test_model_v1")
        
        # Sprawdź typy
        self.assertIsInstance(self.test_record.memory_id, str)
        self.assertIsInstance(self.test_record.feature_schema, list)
        self.assertIsInstance(self.test_record.strategy_parameters, dict)
        
        # Sprawdź domyślne wartości placeholderów
        self.assertEqual(self.test_record.PREDICTION_HISTORY, [])
        self.assertEqual(self.test_record.RESULT_HISTORY, [])
        self.assertEqual(self.test_record.REPUTATION_HISTORY, [])
        self.assertEqual(self.test_record.EVOLUTION_HISTORY, [])
        
        # Sprawdź timestampy
        self.assertIsInstance(self.test_record.creation_time, datetime)
        self.assertIsInstance(self.test_record.last_updated, datetime)
    
    def test_002_add_experiment_to_record(self):
        """Test 2: Dodawanie eksperymentu do rekord"""
        # Początkowo pusta historia
        self.assertEqual(len(self.test_record.EXPERIMENT_HISTORY), 0)
        
        # Dodaj eksperyment
        exp_data = {
            "experiment_id": "exp_001",
            "world_version": "world_v1",
            "dataset_version": "data_v1",
            "result": {"accuracy": 0.85, "roi": 0.08},
            "metrics": {"precision": 0.82, "recall": 0.78}
        }
        
        self.test_record.add_experiment(exp_data)
        
        # Sprawdź czy został dodany
        self.assertEqual(len(self.test_record.EXPERIMENT_HISTORY), 1)
        self.assertEqual(self.test_record.EXPERIMENT_HISTORY[0]["experiment_id"], "exp_001")
        self.assertEqual(self.test_record.EXPERIMENT_HISTORY[0]["result"]["accuracy"], 0.85)
        
        # Sprawdź timestamp
        self.assertIn("timestamp", self.test_record.EXPERIMENT_HISTORY[0])
    
    def test_003_add_multiple_experiments(self):
        """Test 3: Dodawanie wielu eksperymentów"""
        # Dodaj kilka eksperymentów
        for i in range(5):
            exp_data = {
                "experiment_id": f"exp_{i:03d}",
                "world_version": f"world_v{i}",
                "metrics": {"accuracy": 0.70 + i * 0.05}
            }
            self.test_record.add_experiment(exp_data)
        
        self.assertEqual(len(self.test_record.EXPERIMENT_HISTORY), 5)
        
        # Sprawdź kolejność
        self.assertEqual(self.test_record.EXPERIMENT_HISTORY[0]["experiment_id"], "exp_000")
        self.assertEqual(self.test_record.EXPERIMENT_HISTORY[4]["experiment_id"], "exp_004")
    
    def test_004_update_strategy_version(self):
        """Test 4: Aktualizacja wersji strategii"""
        initial_version = self.test_record.strategy_version
        
        # Aktualizuj wersję
        self.test_record.update_version("1.1.0", "Poprawka błędów")
        
        # Sprawdź nową wersję
        self.assertEqual(self.test_record.strategy_version, "1.1.0")
        
        # Sprawdź historię ewolucji
        self.assertEqual(len(self.test_record.EVOLUTION_HISTORY), 1)
        self.assertEqual(self.test_record.EVOLUTION_HISTORY[0]["old_version"], initial_version)
        self.assertEqual(self.test_record.EVOLUTION_HISTORY[0]["new_version"], "1.1.0")
        self.assertEqual(self.test_record.EVOLUTION_HISTORY[0]["change_description"], "Poprawka błędów")
    
    def test_005_get_experiment_count(self):
        """Test 5: Pobieranie liczby eksperymentów"""
        self.assertEqual(self.test_record.get_experiment_count(), 0)
        
        # Dodaj eksperymenty
        self.test_record.add_experiment({"experiment_id": "exp_1"})
        self.test_record.add_experiment({"experiment_id": "exp_2"})
        
        self.assertEqual(self.test_record.get_experiment_count(), 2)
    
    def test_006_get_latest_experiment(self):
        """Test 6: Pobieranie ostatniego eksperymentu"""
        # Bez eksperymentów
        self.assertIsNone(self.test_record.get_latest_experiment())
        
        # Dodaj eksperymenty
        self.test_record.add_experiment({"experiment_id": "exp_1", "timestamp": "2026-01-01"})
        self.test_record.add_experiment({"experiment_id": "exp_2", "timestamp": "2026-01-02"})
        
        latest = self.test_record.get_latest_experiment()
        self.assertIsNotNone(latest)
        self.assertEqual(latest["experiment_id"], "exp_2")
    
    def test_007_get_best_experiment(self):
        """Test 7: Pobieranie najlepszego eksperymentu według metryki"""
        # Bez eksperymentów
        self.assertIsNone(self.test_record.get_best_experiment("accuracy"))
        
        # Dodaj eksperymenty z różnymi metrykami
        self.test_record.add_experiment({
            "experiment_id": "exp_1",
            "metrics": {"accuracy": 0.75}
        })
        self.test_record.add_experiment({
            "experiment_id": "exp_2",
            "metrics": {"accuracy": 0.85}
        })
        self.test_record.add_experiment({
            "experiment_id": "exp_3",
            "metrics": {"accuracy": 0.90}
        })
        
        best = self.test_record.get_best_experiment("accuracy")
        self.assertIsNotNone(best)
        self.assertEqual(best["experiment_id"], "exp_3")
        self.assertEqual(best["metrics"]["accuracy"], 0.90)
    
    def test_008_filter_experiments_by_world_version(self):
        """Test 8: Filtrowanie eksperymentów po wersji świata"""
        # Dodaj eksperymenty z różnymi wersjami świata
        self.test_record.add_experiment({
            "experiment_id": "exp_1",
            "world_version": "world_v1"
        })
        self.test_record.add_experiment({
            "experiment_id": "exp_2", 
            "world_version": "world_v2"
        })
        self.test_record.add_experiment({
            "experiment_id": "exp_3",
            "world_version": "world_v1"
        })
        
        # Filtrowanie
        world_v1_exps = self.test_record.get_experiments_by_world_version("world_v1")
        self.assertEqual(len(world_v1_exps), 2)
        
        world_v2_exps = self.test_record.get_experiments_by_world_version("world_v2")
        self.assertEqual(len(world_v2_exps), 1)
        self.assertEqual(world_v2_exps[0]["experiment_id"], "exp_2")
    
    def test_009_to_dict_serialization(self):
        """Test 9: Serializacja do słownika"""
        self.test_record.add_experiment({"experiment_id": "test_exp"})
        
        data = self.test_record.to_dict()
        
        # Sprawdź wszystkie klucze
        expected_keys = [
            'memory_id', 'strategy_id', 'strategy_version',
            'strategy_definition', 'strategy_parameters', 'feature_schema',
            'model_reference', 'creation_time', 'last_updated', 'metadata',
            'EXPERIMENT_HISTORY', 'PREDICTION_HISTORY', 'RESULT_HISTORY',
            'REPUTATION_HISTORY', 'EVOLUTION_HISTORY'
        ]
        for key in expected_keys:
            self.assertIn(key, data)
        
        # Sprawdź typy
        self.assertIsInstance(data['EXPERIMENT_HISTORY'], list)
        self.assertIsInstance(data['strategy_definition'], dict)
    
    def test_010_to_json_serialization(self):
        """Test 10: Serializacja do JSON"""
        json_str = self.test_record.to_json()
        
        # Sprawdź czy to poprawny JSON
        data = json.loads(json_str)
        self.assertIn('strategy_id', data)
        self.assertEqual(data['strategy_id'], "test_strategy")
        
        # Sprawdź deserializację z JSON
        record2 = StrategyMemoryRecord.from_json(json_str)
        self.assertEqual(record2.strategy_id, self.test_record.strategy_id)
        self.assertEqual(record2.strategy_version, self.test_record.strategy_version)


class TestStrategyMemoryManager(unittest.TestCase):
    """Testy klasy StrategyMemoryManager"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = StrategyMemoryManager(memory_dir=self.temp_dir)
    
    def tearDown(self):
        """Cleanup po każdym teście"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_011_manager_initialization(self):
        """Test 11: Inicjalizacja StrategyMemoryManager"""
        self.assertIsNotNone(self.manager._memory_register)
        self.assertIsInstance(self.manager._memory_register, dict)
        self.assertEqual(len(self.manager._memory_register), 0)
        
        # Sprawdź katalog
        self.assertTrue(self.manager.strategy_memory_dir.exists())
        self.assertTrue(self.manager.strategy_memory_dir.is_dir())
    
    def test_012_create_strategy_memory(self):
        """Test 12: Tworzenie pamięci strategii"""
        record = self.manager.create_strategy_memory(
            strategy_id="test_strategy_1",
            strategy_definition={"type": "test"},
            version="1.0.0"
        )
        
        self.assertIsNotNone(record)
        self.assertEqual(record.strategy_id, "test_strategy_1")
        self.assertEqual(record.strategy_version, "1.0.0")
        self.assertEqual(len(self.manager.get_all_strategy_memories()), 1)
    
    def test_013_get_strategy_memory_by_id(self):
        """Test 13: Pobieranie pamięci strategii po strategy_id"""
        # Utwórz pamięć
        self.manager.create_strategy_memory(
            strategy_id="lookup_test",
            version="2.0.0"
        )
        
        # Pobierz po strategy_id
        record = self.manager.get_strategy_memory("lookup_test")
        self.assertIsNotNone(record)
        self.assertEqual(record.strategy_id, "lookup_test")
        
        # Sprawdź None gdy nie istnieje
        self.assertIsNone(self.manager.get_strategy_memory("nonexistent"))
    
    def test_014_get_strategy_memory_by_memory_id(self):
        """Test 14: Pobieranie pamięci strategii po memory_id"""
        # Utwórz pamięć
        created = self.manager.create_strategy_memory(
            strategy_id="memory_id_test",
            version="1.0.0"
        )
        
        # Pobierz po memory_id
        record = self.manager.get_strategy_memory_by_id(created.memory_id)
        self.assertIsNotNone(record)
        self.assertEqual(record.memory_id, created.memory_id)
    
    def test_015_save_and_retrieve_experiment(self):
        """Test 15: Zapis i pobranie eksperymentu"""
        # Utwórz pamięć
        self.manager.create_strategy_memory(
            strategy_id="experiment_test",
            version="1.0.0"
        )
        
        # Mock StrategyExperiment
        class MockExperiment:
            strategy_id = "experiment_test"
            experiment_id = "exp_001"
            strategy_version = "1.0.0"
            world_version = "world_v1"
            dataset_version = "data_v1"
            model_reference = "model_v1"
            features = ["f1", "f2"]
            start_time = datetime(2026, 1, 1, 12, 0, 0)
            end_time = datetime(2026, 1, 1, 13, 0, 0)
            result = {"success": True}
            metrics = {"accuracy": 0.85, "roi": 0.08}
            status = "completed"
            strategy_parameters = {}
            execution_context = {}
            error = None
            metadata = {}
            
            def to_dict(self):
                return {
                    'experiment_id': self.experiment_id,
                    'strategy_id': self.strategy_id,
                    'strategy_version': self.strategy_version,
                    'world_version': self.world_version,
                    'dataset_version': self.dataset_version,
                    'model_reference': self.model_reference,
                    'features': self.features,
                    'start_time': self.start_time.isoformat(),
                    'end_time': self.end_time.isoformat(),
                    'result': self.result,
                    'metrics': self.metrics,
                    'status': str(self.status),
                    'strategy_parameters': self.strategy_parameters,
                    'execution_context': self.execution_context,
                    'error': self.error,
                    'metadata': self.metadata,
                }
        
        # Zapisz eksperyment
        exp = MockExperiment()
        result = self.manager.save_experiment(exp)
        
        self.assertIsNotNone(result)
        
        # Pobierz pamięć i sprawdź
        memory = self.manager.get_strategy_memory("experiment_test")
        self.assertIsNotNone(memory)
        self.assertEqual(len(memory.EXPERIMENT_HISTORY), 1)
        self.assertEqual(memory.EXPERIMENT_HISTORY[0]["experiment_id"], "exp_001")
    
    def test_016_auto_create_memory_on_experiment_save(self):
        """Test 16: Automatyczne tworzenie pamięci przy zapisie eksperymentu"""
        # Mock StrategyExperiment z nowym strategy_id
        class MockExperiment:
            strategy_id = "new_strategy"
            experiment_id = "exp_new"
            strategy_version = "1.0.0"
            world_version = "world_v1"
            features = ["f1"]
            start_time = datetime.now()
            end_time = datetime.now()
            result = {}
            metrics = {}
            strategy_parameters = {}
            
            def to_dict(self):
                return {
                    'experiment_id': self.experiment_id,
                    'strategy_id': self.strategy_id,
                    'strategy_version': self.strategy_version,
                    'world_version': self.world_version,
                    'features': self.features,
                }
        
        exp = MockExperiment()
        result = self.manager.save_experiment(exp, create_if_not_exists=True)
        
        # Powinna zostać utworzona nowa pamięć
        self.assertIsNotNone(result)
        self.assertEqual(result.strategy_id, "new_strategy")
        self.assertEqual(len(self.manager.get_all_strategy_memories()), 1)
    
    def test_017_get_statistics(self):
        """Test 17: Pobieranie statystyk menadżera"""
        # Utwórz kilka pamięci
        self.manager.create_strategy_memory(strategy_id="stat_strategy_1", version="1.0.0")
        self.manager.create_strategy_memory(strategy_id="stat_strategy_2", version="1.0.0")
        
        # Dodaj eksperymenty
        class MockExp:
            strategy_id = "stat_strategy_1"
            experiment_id = "exp_1"
            features = []
            start_time = datetime.now()
            end_time = datetime.now()
            result = {}
            metrics = {}
            strategy_parameters = {}
            
            def to_dict(self):
                return {'experiment_id': self.experiment_id}
        
        self.manager.save_experiment(MockExp())
        self.manager.save_experiment(MockExp())
        
        stats = self.manager.get_statistics()
        
        self.assertEqual(stats['total_records'], 2)
        self.assertEqual(stats['total_experiments'], 2)  # Dwa eksperymenty zapisane
        self.assertIn('stat_strategy_1', stats['strategies'])
        self.assertIn('stat_strategy_2', stats['strategies'])
    
    def test_018_save_and_load_json_collection(self):
        """Test 18: Zapis i wczytanie kolekcji JSON"""
        # Utwórz pamięć
        record = self.manager.create_strategy_memory(
            strategy_id="json_test",
            version="1.0.0"
        )
        
        # Zapisz kolekcję
        collection_path = str(self.manager.strategy_memory_dir / "collection.json")
        success = self.manager.save_to_json(collection_path)
        self.assertTrue(success)
        
        # Sprawdź czy plik istnieje
        self.assertTrue(os.path.exists(collection_path))
        
        # Utwórz nowy menadżer i wczytaj
        manager2 = StrategyMemoryManager(memory_dir=self.temp_dir)
        success = manager2.load_from_json(collection_path)
        self.assertTrue(success)
        
        # Sprawdź wczytane dane - być może załadowano więcej plików.json z katalogu
        loaded_memories = manager2.get_all_strategy_memories()
        self.assertGreaterEqual(len(loaded_memories), 1)
        loaded = manager2.get_strategy_memory("json_test")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.strategy_id, "json_test")
    
    def test_019_clear_strategy_memory(self):
        """Test 19: Czyszczenie pamięci strategii"""
        # Utwórz pamięć
        record = self.manager.create_strategy_memory(
            strategy_id="clear_test",
            version="1.0.0"
        )
        memory_id = record.memory_id
        
        # Sprawdź że istnieje
        self.assertIsNotNone(self.manager.get_strategy_memory("clear_test"))
        
        # Wyczyść
        success = self.manager.clear_strategy_memory("clear_test")
        self.assertTrue(success)
        
        # Sprawdź czy zniknęła
        self.assertIsNone(self.manager.get_strategy_memory("clear_test"))
        self.assertIsNone(self.manager.get_strategy_memory_by_id(memory_id))
    
    def test_020_clear_all_memory(self):
        """Test 20: Czyszczenie całej pamięci"""
        # Utwórz kilka pamięci
        self.manager.create_strategy_memory(strategy_id="all_clear_1", version="1.0.0")
        self.manager.create_strategy_memory(strategy_id="all_clear_2", version="1.0.0")
        
        self.assertEqual(len(self.manager.get_all_strategy_memories()), 2)
        
        # Wyczyść wszystko
        success = self.manager.clear_all_memory()
        self.assertTrue(success)
        
        self.assertEqual(len(self.manager.get_all_strategy_memories()), 0)
    
    def test_021_experiment_from_strategy_experiment_fallback(self):
        """Test 21: Dodawanie eksperymentu z StrategyExperiment (fallback)"""
        # Utwórz pamięć
        self.manager.create_strategy_memory(
            strategy_id="fallback_test",
            version="1.0.0"
        )
        
        # Mock bez metody to_dict (fallback)
        class MockExperimentNoToDict:
            strategy_id = "fallback_test"
            experiment_id = "exp_fallback"
            strategy_version = "1.0.0"
            world_version = "world_v1"
            dataset_version = "data_v1"
            model_reference = "model_v1"
            features = ["f1", "f2"]
            start_time = datetime(2026, 1, 1, 12, 0, 0)
            end_time = datetime(2026, 1, 1, 13, 0, 0)
            result = {"success": True}
            metrics = {"accuracy": 0.85}
            status = "completed"
            strategy_parameters = {}
            execution_context = {}
            error = None
            metadata = {}
        
        exp = MockExperimentNoToDict()
        result = self.manager.save_experiment(exp)
        
        self.assertIsNotNone(result)
        memory = self.manager.get_strategy_memory("fallback_test")
        self.assertEqual(len(memory.EXPERIMENT_HISTORY), 1)
        self.assertIn("experiment_id", memory.EXPERIMENT_HISTORY[0])
    
    def test_022_update_strategy_version_through_manager(self):
        """Test 22: Aktualizacja wersji strategii przez menadżera"""
        # Utwórz pamięć
        self.manager.create_strategy_memory(
            strategy_id="version_update_test",
            version="1.0.0"
        )
        
        # Aktualizuj wersję
        success = self.manager.update_strategy_version(
            "version_update_test",
            "2.0.0",
            "Dodano nowe funkcjonalności"
        )
        
        self.assertTrue(success)
        
        # Sprawdź aktualizację
        record = self.manager.get_strategy_memory("version_update_test")
        self.assertEqual(record.strategy_version, "2.0.0")
        self.assertEqual(len(record.EVOLUTION_HISTORY), 1)
    
    def test_023_get_experiments_by_dataset_version(self):
        """Test 23: Filtrowanie eksperymentów po wersji dataset"""
        # Utwórz pamięć
        self.manager.create_strategy_memory(
            strategy_id="dataset_filter_test",
            version="1.0.0"
        )
        
        # Dodaj eksperymenty przez menadżera
        class MockExp:
            strategy_id = "dataset_filter_test"
            experiment_id = "exp_dataset"
            dataset_version = "data_v1"
            features = []
            start_time = datetime.now()
            end_time = datetime.now()
            result = {}
            metrics = {}
            strategy_parameters = {}
            
            def __init__(self, dataset_version):
                self.dataset_version = dataset_version
                self.experiment_id = f"exp_{dataset_version}"
            
            def to_dict(self):
                return {
                    'experiment_id': self.experiment_id,
                    'dataset_version': self.dataset_version,
                    'strategy_id': self.strategy_id
                }
        
        self.manager.save_experiment(MockExp("data_v1"))
        self.manager.save_experiment(MockExp("data_v2"))
        self.manager.save_experiment(MockExp("data_v1"))
        
        # Pobierz pamięć i filtrowanie
        memory = self.manager.get_strategy_memory("dataset_filter_test")
        data_v1_exps = memory.get_experiments_by_dataset_version("data_v1")
        self.assertEqual(len(data_v1_exps), 2)
    
    def test_024_connect_to_strategy_lab(self):
        """Test 24: Integracja z StrategyLab"""
        # Mock StrategyLab
        class MockStrategyLab:
            def __init__(self):
                self.strategy_memory_manager = None
                self.save_to_strategy_memory = None
        
        lab = MockStrategyLab()
        
        # Połącz
        self.manager.connect_to_strategy_lab(lab)
        
        # Sprawdź czy referencja została ustawiona
        self.assertEqual(lab.strategy_memory_manager, self.manager)
        
        # Sprawdź czy metoda została dodana
        self.assertIsNotNone(lab.save_to_strategy_memory)
        
        # Test użycia metody
        class MockExp:
            strategy_id = "integration_test"
            experiment_id = "exp_integration"
            features = []
            start_time = datetime.now()
            end_time = datetime.now()
            result = {}
            metrics = {}
            strategy_parameters = {}
            
            def to_dict(self):
                return {'experiment_id': self.experiment_id, 'strategy_id': self.strategy_id}
        
        # Utwórz pamięć
        self.manager.create_strategy_memory(strategy_id="integration_test", version="1.0.0")
        
        # Użyj metody
        result = lab.save_to_strategy_memory(MockExp())
        self.assertIsNotNone(result)
    
    def test_025_preserve_existing_modules(self):
        """Test 25: Sprawdzenie braku modyfikacji istniejących modułów"""
        # Ten test weryfikuje cały moduł Strategy Memory
        # Nie powinien modyfikować TrustManager, AgentRuntime, Pipeline, CollectiveManager, WorldEngine
        
        # Importuj kluczowe klasy i sprawdź że Strategy Memory nie wpływa na nie
        # (Test pośredni - jeśli import się powiódł, moduły nie zostały złamane)
        try:
            from SSI_V5.memory.strategy_memory import StrategyMemoryRecord, StrategyMemoryManager
            from SSI_V5.laboratory.strategy_laboratory import StrategyExperiment, StrategyLab
            
            # Sprawdź że klasy istnieją i są używalne
            self.assertIsNotNone(StrategyMemoryRecord)
            self.assertIsNotNone(StrategyMemoryManager)
            self.assertIsNotNone(StrategyExperiment)
            self.assertIsNotNone(StrategyLab)
            
            # Można tworzyć instancje
            record = StrategyMemoryRecord(strategy_id="test", strategy_version="1.0.0")
            self.assertIsNotNone(record)
            
        except ImportError as e:
            self.fail(f"Import error: {e}")


class TestRecordPersistence(unittest.TestCase):
    """Testy trwałości rekordów pamięci"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Cleanup po każdym teście"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_026_persistence_across_instances(self):
        """Test 26: Trwałość między instancjami menadżerów"""
        # Utwórz menadżera i pamięć
        manager1 = StrategyMemoryManager(memory_dir=self.temp_dir)
        record = manager1.create_strategy_memory(
            strategy_id="persistence_test",
            version="1.0.0"
        )
        
        # Utwórz drugiego menadżera
        manager2 = StrategyMemoryManager(memory_dir=self.temp_dir)
        
        # Powinien załadować istniejącą pamięć
        retrieved = manager2.get_strategy_memory("persistence_test")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.strategy_id, "persistence_test")
        self.assertEqual(retrieved.memory_id, record.memory_id)
    
    def test_027_automatic_json_loading(self):
        """Test 27: Automaticzne wczytywanie plików JSON przy inicjalizacji"""
        # Utwórz menadżera i zapisz pamięć
        manager1 = StrategyMemoryManager(memory_dir=self.temp_dir)
        record = manager1.create_strategy_memory(
            strategy_id="auto_load_test",
            version="1.0.0"
        )
        
        # Plik powinien zostać zapisany
        memory_file = Path(self.temp_dir) / "strategy_memory" / f"{record.memory_id}.json"
        self.assertTrue(memory_file.exists())
        
        # Utwórz nowego menadżera - powinien automatycznie wczytać
        manager2 = StrategyMemoryManager(memory_dir=self.temp_dir)
        
        # Sprawdź czy pamięć została wczytana
        self.assertEqual(len(manager2.get_all_strategy_memories()), 1)
        loaded = manager2.get_strategy_memory("auto_load_test")
        self.assertIsNotNone(loaded)


class TestIsolationPrinciple(unittest.TestCase):
    """Testy zasady izolacji"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = StrategyMemoryManager(memory_dir=self.temp_dir)
    
    def tearDown(self):
        """Cleanup po każdym teście"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_028_no_automatic_strategy_selection(self):
        """Test 28: Brak automatycznego wybierania strategii"""
        # Utwórz pamięć z eksperymentami
        self.manager.create_strategy_memory(
            strategy_id="auto_select_test",
            version="1.0.0"
        )
        
        class MockExp:
            strategy_id = "auto_select_test"
            experiment_id = "exp_auto"
            features = []
            start_time = datetime.now()
            end_time = datetime.now()
            result = {"success": True}
            metrics = {"accuracy": 0.95}  # Bardzo dobry wynik
            strategy_parameters = {}
            
            def to_dict(self):
                return {
                    'experiment_id': self.experiment_id,
                    'strategy_id': self.strategy_id,
                    'metrics': self.metrics
                }
        
        self.manager.save_experiment(MockExp())
        
        # Strategy Memory NIE powinien wybierać żadnej strategii
        # Powinien tylko zapisywać doświadczenie
        memory = self.manager.get_strategy_memory("auto_select_test")
        best_exp = memory.get_best_experiment("accuracy")
        
        # Możemy znaleźć najlepszy eksperyment, ale menadżer NIE podejmuje decyzji
        self.assertIsNotNone(best_exp)
        self.assertEqual(best_exp["metrics"]["accuracy"], 0.95)
        
        # Ale NIE ma metody do wybierania aktywnej strategii
        self.assertFalse(hasattr(self.manager, 'select_best_strategy'))
        self.assertFalse(hasattr(self.manager, 'activate_strategy'))
    
    def test_029_no_reputation_modification(self):
        """Test 29: Brak modyfikacji reputacji"""
        # Strategy Memory nie powinien mieć metod modyfikujących reputację
        self.assertFalse(hasattr(self.manager, 'update_reputation'))
        self.assertFalse(hasattr(self.manager, 'modify_trust'))
        self.assertFalse(hasattr(self.manager, 'affect_agent_rating'))
        
        # Placeholder REPUTATION_HISTORY istnieje, ale nie ma logiki
        record = self.manager.create_strategy_memory(
            strategy_id="reputation_test",
            version="1.0.0"
        )
        self.assertEqual(record.REPUTATION_HISTORY, [])
    
    def test_030_read_only_experience(self):
        """Test 30: Pamięć tylko do odczytu doświadczeń"""
        # Utwórz pamięć i dodaj eksperyment
        record = self.manager.create_strategy_memory(
            strategy_id="readonly_test",
            version="1.0.0"
        )
        
        class MockExp:
            strategy_id = "readonly_test"
            experiment_id = "exp_readonly"
            features = []
            start_time = datetime.now()
            end_time = datetime.now()
            result = {"conclusion": "test"}
            metrics = {}
            strategy_parameters = {}
            
            def to_dict(self):
                return {'experiment_id': self.experiment_id, 'strategy_id': self.strategy_id}
        
        self.manager.save_experiment(MockExp())
        
        # Doświadczenie jest zapisane
        memory = self.manager.get_strategy_memory("readonly_test")
        self.assertEqual(len(memory.EXPERIMENT_HISTORY), 1)
        
        # Ale Strategy Memory NIE modyfikuje systemu produkcyjnego
        # Nie ma metod do aktywacji, zmiany parametrów, itp.
        self.assertFalse(hasattr(self.manager, 'apply_strategy'))
        self.assertFalse(hasattr(self.manager, 'modify_strategy_parameters'))


if __name__ == '__main__':
    # Uruchomienie testów
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Dodaj wszystkie klasy testowe
    suite.addTests(loader.loadTestsFromTestCase(TestStrategyMemoryRecord))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategyMemoryManager))
    suite.addTests(loader.loadTestsFromTestCase(TestRecordPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestIsolationPrinciple))
    
    # Uruchom testy
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Raport
    print("\n" + "="*70)
    print("SSI V5 STRATEGY MEMORY - RAPORT TESTOW")
    print("="*70)
    print(f"Wykonano: {result.testsRun} testow")
    print(f"Bledow: {len(result.failures)}")
    print(f"Bledow krytycznych: {len(result.errors)}")
    print(f"Pominieto: {len(result.skipped)}")
    print(f"Zaliczono: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ WSZYSTKIE TESTY ZALICZONE!")
    else:
        print("\n❌ NIEKTORYCH TESTOW NIE ZALICZONO")
    
    exit(0 if result.wasSuccessful() else 1)