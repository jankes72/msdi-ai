"""
SSI V5 Tests - Testy dla V2 Data Collector
Testy jednostkowe dla SSI/v5/input_layer/v2_collector.py

Wersja: 1.0
Data: 2026-07-31
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Testowany moduł
from SSI.v5.input_layer.v2_collector import (
    V2DataCollector, tworz_v2_collector, get_v2_collector, reset_v2_collector
)
from SSI.v5.input_layer.data_models import (
    V2DataPackage, ModelInfo, PredictionData, ValidationResult,
    WorldInterpretation, V2Metadata, DataSource, DataCategory, DataStatus
)


class TestV2DataCollector(unittest.TestCase):
    """Testy dla klasy V2DataCollector"""
    
    def setUp(self):
        """Procedura przygotowawcza przed kazdym testem"""
        # Resetuj singleton
        reset_v2_collector()
        self.collector = tworz_v2_collector()
    
    def tearDown(self):
        """Sprzatanie po kazdym tescie"""
        reset_v2_collector()
    
    # =============================================================================
    # TESTY INICJALIZACJI
    # =============================================================================
    
    def test_init_creates_collector(self):
        """Test: Inicjalizacja tworzy poprawny kolektor"""
        collector = tworz_v2_collector()
        self.assertIsInstance(collector, V2DataCollector)
        self.assertFalse(collector._initialized)
    
    def test_init_sets_default_values(self):
        """Test: Inicjalizacja ustawia domyslne wartosci"""
        collector = tworz_v2_collector()
        self.assertIsNone(collector._v2_integration)
        self.assertIsNone(collector._bridge_v2_v3)
    
    # =============================================================================
    # TESTY SINGLETON
    # =============================================================================
    
    def test_get_v2_collector_returns_singleton(self):
        """Test: get_v2_collector zwraca te sama instancje"""
        collector1 = get_v2_collector()
        collector2 = get_v2_collector()
        self.assertIs(collector1, collector2)
    
    def test_reset_v2_collector_creates_new_instance(self):
        """Test: reset_v2_collector tworzy nowa instancje"""
        collector1 = get_v2_collector()
        reset_v2_collector()
        collector2 = get_v2_collector()
        self.assertIsNot(collector1, collector2)
    
    # =============================================================================
    # TESTY COLLECT_MODELS
    # =============================================================================
    
    def test_collect_models_returns_list(self):
        """Test: collect_models zwraca liste ModelInfo"""
        models = self.collector.collect_models()
        self.assertIsInstance(models, list)
        if models:
            self.assertIsInstance(models[0], ModelInfo)
    
    def test_collect_models_returns_default_models(self):
        """Test: collect_models zwraca domyslne modele"""
        models = self.collector.collect_models()
        # Powinno zwrocic 5 domyslnych modeli
        self.assertEqual(len(models), 5)
        self.assertIn("siec_01_zmiana_kursow", [m.name for m in models])
        self.assertIn("random_forest", [m.name for m in models])
    
    def test_collect_models_has_required_fields(self):
        """Test: Modele maja wszystkie wymagane pola"""
        models = self.collector.collect_models()
        for model in models:
            self.assertIsInstance(model.name, str)
            self.assertIsInstance(model.model_type, str)
            self.assertIsInstance(model.status, str)
            self.assertIsInstance(model.version, str)
            self.assertTrue(len(model.name) > 0)
            self.assertTrue(len(model.model_type) > 0)
    
    # =============================================================================
    # TESTY COLLECT_PREDICTIONS
    # =============================================================================
    
    def test_collect_predictions_returns_list(self):
        """Test: collect_predictions zwraca liste PredictionData"""
        predictions = self.collector.collect_predictions()
        self.assertIsInstance(predictions, list)
    
    # =============================================================================
    # TESTY COLLECT_VALIDATION_RESULTS
    # =============================================================================
    
    def test_collect_validation_results_returns_list(self):
        """Test: collect_validation_results zwraca liste ValidationResult"""
        results = self.collector.collect_validation_results()
        self.assertIsInstance(results, list)
    
    def test_collect_validation_results_returns_default_values(self):
        """Test: collect_validation_results zwraca domyslne wyniki"""
        results = self.collector.collect_validation_results()
        # Powinno zwrocic 5 domyslnych wynikow (po jednym dla kazdego modelu)
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertIsInstance(result, ValidationResult)
            self.assertIn(result.model_name, ["siec_01_zmiana_kursow", "siec_02_amplituda", 
                                              "siec_03_tempo", "siec_04_synchronizacja", "random_forest"])
    
    # =============================================================================
    # TESTY COLLECT_WORLD_INTERPRETATIONS
    # =============================================================================
    
    def test_collect_world_interpretations_returns_list(self):
        """Test: collect_world_interpretations zwraca liste WorldInterpretation"""
        interpretations = self.collector.collect_world_interpretations()
        self.assertIsInstance(interpretations, list)
    
    # =============================================================================
    # TESTY COLLECT_METADATA
    # =============================================================================
    
    def test_collect_metadata_returns_v2metadata(self):
        """Test: collect_metadata zwraca V2Metadata"""
        metadata = self.collector.collect_metadata()
        self.assertIsInstance(metadata, V2Metadata)
        self.assertEqual(metadata.v2_version, "1.0")
        self.assertEqual(metadata.data_split_policy, "60/40")
        self.assertEqual(metadata.models_count, 5)
    
    # =============================================================================
    # TESTY COLLECT_ALL
    # =============================================================================
    
    def test_collect_all_returns_v2data_package(self):
        """Test: collect_all zwraca V2DataPackage"""
        package = self.collector.collect_all()
        self.assertIsInstance(package, V2DataPackage)
    
    def test_collect_all_package_has_all_components(self):
        """Test: Pakiet ma wszystkie komponenty"""
        package = self.collector.collect_all()
        
        # Sprawdzamy czy pakiet ma wszystkie pola
        self.assertIsInstance(package.timestamp, datetime)
        self.assertIsInstance(package.models, list)
        self.assertIsInstance(package.predictions, list)
        self.assertIsInstance(package.validation_results, list)
        self.assertIsInstance(package.world_interpretations, list)
        self.assertIsInstance(package.metadata, V2Metadata)
        self.assertIsInstance(package.status, DataStatus)
    
    def test_collect_all_models_not_empty(self):
        """Test: Pakiet ma niepusta liste modeli"""
        package = self.collector.collect_all()
        self.assertGreater(len(package.models), 0)
    
    def test_collect_all_metadata_not_none(self):
        """Test: Pakiet ma metadane"""
        package = self.collector.collect_all()
        self.assertIsNotNone(package.metadata)
    
    # =============================================================================
    # TESTY KONWERSJI DO SLOWNIKA
    # =============================================================================
    
    def test_v2data_package_to_dict(self):
        """Test: V2DataPackage moze byc konwertowany do slownika"""
        package = self.collector.collect_all()
        result = package.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertIn("timestamp", result)
        self.assertIn("models", result)
        self.assertIn("predictions", result)
        self.assertIn("validation_results", result)
        self.assertIn("world_interpretations", result)
        self.assertIn("metadata", result)
        self.assertIn("status", result)
    
    def test_v2data_package_to_json(self):
        """Test: V2DataPackage moze byc konwertowany do JSON"""
        package = self.collector.collect_all()
        json_str = package.to_json()
        
        self.assertIsInstance(json_str, str)
        self.assertTrue(len(json_str) > 0)
    
    # =============================================================================
    # TESTY SERIALIZACJI/DESERIALIZACJI
    # =============================================================================
    
    def test_model_info_to_dict_and_back(self):
        """Test: ModelInfo serialization/deserialization"""
        original = ModelInfo(
            name="test_model",
            model_type="neural_network",
            status="trained",
            version="1.0",
            accuracy=0.85
        )
        
        data = original.to_dict()
        restored = ModelInfo.from_dict(data)
        
        self.assertEqual(original.name, restored.name)
        self.assertEqual(original.model_type, restored.model_type)
        self.assertEqual(original.status, restored.status)
    
    def test_v2data_package_from_dict(self):
        """Test: V2DataPackage deserialization"""
        data = {
            "timestamp": "2026-07-31T12:00:00",
            "models": [
                {
                    "name": "test_model",
                    "model_type": "neural_network",
                    "status": "trained",
                    "version": "1.0"
                }
            ],
            "predictions": [],
            "validation_results": [],
            "world_interpretations": [],
            "metadata": {
                "v2_version": "1.0",
                "data_split_policy": "60/40",
                "models_count": 1,
                "last_update": "2026-07-31T12:00:00",
                "collection_timestamp": "2026-07-31T12:00:00"
            }
        }
        
        package = V2DataPackage.from_dict(data)
        
        self.assertIsInstance(package, V2DataPackage)
        self.assertEqual(len(package.models), 1)
        self.assertEqual(package.models[0].name, "test_model")
    
    # =============================================================================
    # TESTY Z MOCKAMI
    # =============================================================================
    
    @patch('SSI.v5.input_layer.v2_collector.V2DataCollector._get_v2_integration')
    def test_collect_models_with_mock(self, mock_get_integration):
        """Test: collect_models z mockowana integracja"""
        # Mock V2Integration
        mock_integration = Mock()
        mock_integration.get_all_models.return_value = {
            "test_model": Mock(
                model_type="neural_network",
                status="trained",
                version="1.0",
                last_trained=None,
                accuracy=0.90,
                description="Test model"
            )
        }
        mock_get_integration.return_value = mock_integration
        
        models = self.collector.collect_models()
        
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0].name, "test_model")
        self.assertEqual(models[0].accuracy, 0.90)
    
    @patch('SSI.v5.input_layer.v2_collector.V2DataCollector._get_v2_integration')
    def test_collect_predictions_with_mock(self, mock_get_integration):
        """Test: collect_predictions z mockowana integracja"""
        mock_integration = Mock()
        mock_integration.get_latest_predictions.return_value = {
            "test_model": {"prediction": [1, 2, 3], "confidence": 0.95}
        }
        mock_get_integration.return_value = mock_integration
        
        predictions = self.collector.collect_predictions()
        
        self.assertEqual(len(predictions), 1)
        self.assertEqual(predictions[0].model_name, "test_model")
    
    @patch('SSI.v5.input_layer.v2_collector.V2DataCollector._get_v2_integration')
    def test_collect_validation_results_with_mock(self, mock_get_integration):
        """Test: collect_validation_results z mockowana integracja"""
        mock_integration = Mock()
        mock_integration.get_validation_results.return_value = {
            "test_model": {"accuracy": 0.95, "precision": 0.90}
        }
        mock_get_integration.return_value = mock_integration
        
        results = self.collector.collect_validation_results()
        
        self.assertEqual(len(results), 2)  # accuracy i precision
        metrics = [r.metric for r in results]
        self.assertIn("accuracy", metrics)
        self.assertIn("precision", metrics)
    
    @patch('SSI.v5.input_layer.v2_collector.V2DataCollector._get_v2_v3_bridge')
    def test_collect_world_interpretations_with_mock(self, mock_get_bridge):
        """Test: collect_world_interpretations z mockowanym mostem"""
        mock_bridge = Mock()
        mock_bridge.extract_world_knowledge.return_value = {
            "test_model": {
                "world_1": {"type": "trend", "value": "up"},
                "world_2": {"type": "amplitude", "value": "high"}
            }
        }
        mock_get_bridge.return_value = mock_bridge
        
        interpretations = self.collector.collect_world_interpretations()
        
        self.assertEqual(len(interpretations), 2)
        world_names = [i.world_name for i in interpretations]
        self.assertIn("world_1", world_names)
        self.assertIn("world_2", world_names)


# =============================================================================
# TESTY INTEGRACYJNE (Smoke Tests)
# =============================================================================

class TestV2CollectorSmoke(unittest.TestCase):
    """Testy integracyjne (smoke tests)"""
    
    def test_import_v2_collector_module(self):
        """Test: Import modulu v2_collector nie rzuca bledu"""
        try:
            from SSI.v5.input_layer import v2_collector
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Import error: {e}")
    
    def test_import_data_models_module(self):
        """Test: Import modulu data_models nie rzuca bledu"""
        try:
            from SSI.v5.input_layer import data_models
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Import error: {e}")
    
    def test_create_collector_no_error(self):
        """Test: Tworzenie kolektora nie rzuca bledu"""
        try:
            collector = V2DataCollector()
            self.assertIsInstance(collector, V2DataCollector)
        except Exception as e:
            self.fail(f"Creation error: {e}")
    
    def test_collect_all_no_error(self):
        """Test: collect_all nie rzuca bledu"""
        try:
            collector = V2DataCollector()
            package = collector.collect_all()
            self.assertIsInstance(package, V2DataPackage)
        except Exception as e:
            self.fail(f"collect_all error: {e}")


# =============================================================================
# URUCHOMIENIE TESTOW
# =============================================================================

if __name__ == '__main__':
    # Uruchom testy
    unittest.main()
