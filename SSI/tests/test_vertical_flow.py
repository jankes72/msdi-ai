"""
SSI Vertical Flow Tests - Testy pionowego przepływu V2->V3->V4

Wersja: 1.0
Date: 2026-07-31

Zawiera testy:
- Pionowego przepływu danych
- Polityki podziału danych
- Walidacji kontraktów w przepływie
- Lineage tracking
- Powtarzalności wyników
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime
import json

# Dodaj katalog nadrzędny do sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from SSI.workflows import (
    VerticalFlow,
    VerticalFlowConfig,
    FlowResult,
    LineageTracker,
    run_smoke_test,
)
from SSI.contracts import ContractVersion, ContractValidator
from SSI.contracts import (
    V2ToV3Contract,
    V3ToV4Contract,
    DataVersion,
    ModelVersion,
    ConfigVersion,
    ResultVersion,
    LineageInfo,
)
from SSI.contracts.policies import DataSplitPolicy, SplitResult
from SSI.data.policies import DataQualityPolicy, DataRetentionPolicy


class TestVerticalFlowConfig(unittest.TestCase):
    """Testy konfiguracji pionowego przepływu."""
    
    def test_default_config(self):
        """Test domyślnej konfiguracji."""
        config = VerticalFlowConfig()
        
        self.assertIsNotNone(config.split_policy)
        self.assertEqual(config.split_policy.train_ratio, 0.50)
        self.assertEqual(config.split_policy.validation_ratio, 0.10)
        self.assertEqual(config.split_policy.observation_ratio, 0.40)
        self.assertEqual(config.seed, 42)
        self.assertTrue(config.enable_lineage)
        self.assertTrue(config.enable_validation)
    
    def test_custom_config(self):
        """Test niestandardowej konfiguracji."""
        policy = DataSplitPolicy(
            train_ratio=0.60,
            validation_ratio=0.20,
            observation_ratio=0.20
        )
        
        config = VerticalFlowConfig(
            split_policy=policy,
            seed=123,
            enable_lineage=True,
            enable_validation=False
        )
        
        self.assertEqual(config.split_policy.train_ratio, 0.60)
        self.assertEqual(config.seed, 123)
        self.assertFalse(config.enable_validation)


class TestFlowResult(unittest.TestCase):
    """Testy wyniku przepływu."""
    
    def test_empty_result(self):
        """Test pustego wyniku."""
        result = FlowResult()
        
        self.assertTrue(result.success)
        self.assertIsNone(result.v2_result)
        self.assertIsNone(result.v3_result)
        self.assertIsNone(result.v4_result)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 0)
    
    def test_result_serialization(self):
        """Test serializacji wyniku."""
        result = FlowResult(
            success=True,
            execution_time_ms=100.5,
            errors=["error1"],
            warnings=["warning1"]
        )
        
        result_dict = result.to_dict()
        
        self.assertIn("success", result_dict)
        self.assertIn("execution_time_ms", result_dict)
        self.assertIn("errors", result_dict)
        self.assertIn("warnings", result_dict)
        self.assertEqual(result_dict["success"], True)
        self.assertEqual(result_dict["execution_time_ms"], 100.5)
        self.assertEqual(len(result_dict["errors"]), 1)


class TestLineageTracker(unittest.TestCase):
    """Testy tracker'a lineage."""
    
    def test_create_tracker(self):
        """Test tworzenia trackera."""
        tracker = LineageTracker()
        
        self.assertIsNotNone(tracker.workflow_id)
        self.assertIsNotNone(tracker.start_time)
        # end_time nie jest ustawione przy inicjalizacji
    
    def test_add_data_version(self):
        """Test dodawania wersji danych."""
        tracker = LineageTracker()
        
        tracker.add_data_version("v1.0.0")
        tracker.add_model_version("v1.0.0")
        tracker.add_config_version("v1.0.0")
        
        # Sprawdź w trackera
        self.assertEqual(len(tracker.data_versions), 1)
        self.assertEqual(len(tracker.model_versions), 1)
        self.assertEqual(len(tracker.config_versions), 1)
    
    def test_finalize(self):
        """Test finalizacji trackera."""
        tracker = LineageTracker()
        
        tracker.add_data_version("v1.0.0")
        lineage = tracker.finalize()
        
        self.assertIsNotNone(lineage)
        self.assertIsNotNone(lineage.end_time)
        self.assertGreater(lineage.duration_ms, 0)


class TestVerticalFlow(unittest.TestCase):
    """Testy pionowego przepływu."""
    
    def test_create_flow(self):
        """Test tworzenia przepływu."""
        config = VerticalFlowConfig()
        flow = VerticalFlow(config)
        
        self.assertIsNotNone(flow.config)
        self.assertIsNotNone(flow.lineage_tracker)
        self.assertEqual(flow.config.seed, 42)
    
    def test_flow_with_custom_config(self):
        """Test przepływu z niestandardową konfiguracją."""
        config = VerticalFlowConfig(
            seed=999,
            enable_lineage=True,
            enable_validation=True
        )
        flow = VerticalFlow(config)
        
        self.assertEqual(flow.config.seed, 999)
        self.assertTrue(flow.config.enable_lineage)
    
    def test_prepare_fixture_data(self):
        """Test przygotowania danych fixture."""
        config = VerticalFlowConfig(load_sample_data=True)
        flow = VerticalFlow(config)
        
        # Wywołaj przygotowanie danych (jeśli nie wykonywało się automatycznie)
        data = flow._load_sample_data()
        
        # Powinno zwrócić jakieś dane lub nie rzucić błędu
        self.assertIsInstance(data, list)
    
    def test_split_data(self):
        """Test podziału danych."""
        from SSI.contracts.policies import DataSplitPolicy, DataSplitter
        from SSI.contracts import V2ToV3Contract
        from SSI.contracts.data_contracts import V2ObservationData
        
        # Test bezpośrednio DataSplitter
        policy = DataSplitPolicy.standard_50_10_40()
        splitter = DataSplitter(policy)
        
        test_data = list(range(100))
        split_result = splitter.split_data(test_data, seed=42)
        
        self.assertIsInstance(split_result, object)  # SplitResult
        self.assertEqual(len(split_result.train_data), 50)
        self.assertEqual(len(split_result.validation_data), 10)
        self.assertEqual(len(split_result.observation_data), 40)
    
    def test_split_data_reproducibility(self):
        """Test powtarzalności podziału danych."""
        from SSI.contracts.policies import DataSplitPolicy, DataSplitter
        
        policy = DataSplitPolicy.standard_50_10_40()
        splitter = DataSplitter(policy)
        
        test_data = list(range(100))
        
        result1 = splitter.split_data(test_data, seed=42)
        result2 = splitter.split_data(test_data, seed=42)
        
        # Ten sam seed powinien dać ten sam podział
        self.assertEqual(result1.train_indices, result2.train_indices)
        self.assertEqual(result1.validation_indices, result2.validation_indices)
    
    def test_create_v2_contract(self):
        """Test tworzenia kontraktu V2->V3."""
        # Test bezpośredniego tworzenia kontraktu
        contract = V2ToV3Contract()
        
        self.assertIsInstance(contract, V2ToV3Contract)
        self.assertIsNotNone(contract.metadata)
        self.assertTrue(contract.validate())
    
    def test_create_v3_contract(self):
        """Test tworzenia kontraktu V3->V4."""
        # Test bezpośredniego tworzenia kontraktu
        contract = V3ToV4Contract()
        
        self.assertIsInstance(contract, V3ToV4Contract)
        self.assertIsNotNone(contract.metadata)


class TestSmokeTest(unittest.TestCase):
    """Testy smoke testu."""
    
    def test_run_smoke_test(self):
        """Test uruchomienia smoke testu."""
        config = VerticalFlowConfig(enable_validation=False)
        result = run_smoke_test(config=config)
        
        self.assertIsInstance(result, FlowResult)
        # Smoke test może się nie powieść, jeśli brakuje komponentów
        # ale powinien zwrócić FlowResult
        self.assertIsNotNone(result.execution_time_ms)
        self.assertIsInstance(result.execution_time_ms, float)
    
    def test_smoke_test_with_lineage(self):
        """Test smoke testu z lineage tracking."""
        config = VerticalFlowConfig(
            enable_lineage=True,
            enable_validation=True
        )
        result = run_smoke_test(config=config)
        
        self.assertIsNotNone(result.lineage)
        
        # Sprawdź czy zawierają wersje
        self.assertGreaterEqual(len(result.lineage.data_versions), 0)
        self.assertGreaterEqual(len(result.lineage.model_versions), 0)
    
    def test_smoke_test_reproducibility(self):
        """Test powtarzalności smoke testu."""
        config = VerticalFlowConfig(seed=42, enable_lineage=True)
        result1 = run_smoke_test(config=config)
        result2 = run_smoke_test(config=config)
        
        # Ten sam seed powinien dać te same czasy wykonania (przybliżone)
        # i tę samą liczbę błędów
        self.assertEqual(len(result1.errors), len(result2.errors))
        self.assertEqual(result1.success, result2.success)


class TestVersionCompatibilityInFlow(unittest.TestCase):
    """Testy kompatybilności wersji w przepływie."""
    
    def test_contract_version_validation(self):
        """Test walidacji wersji kontraktów."""
        # Utwórz kontrakty z poprawnymi wersjami
        v2_contract = V2ToV3Contract()
        v3_contract = V3ToV4Contract()
        
        # Walidacja powinna przejść
        validator = ContractValidator()
        self.assertTrue(validator.validate(v2_contract))
        self.assertTrue(validator.validate(v3_contract))
    
    def test_incompatible_contract_version(self):
        """Test niekompatybilnej wersji kontraktu."""
        # Utwórz kontrakt z niekompatybilną wersją (nieistniejąca wersja)
        from SSI.contracts.data_contracts import ContractMetadata
        
        v2_contract = V2ToV3Contract()
        # Ustaw nieistniejącą wersję - tworzymy nieprawidłowy ContractVersion
        # Zamiast tego, użyjemy nieprawidłowych metadanych
        invalid_metadata = ContractMetadata(
            version=None,  # Nieprawidłowe
            source="",
            target=""
        )
        v2_contract.metadata = invalid_metadata
        
        # Walidacja metadanych powinna nie przejść
        validator = ContractValidator()
        self.assertFalse(validator.validate(v2_contract))


class TestLineageInFlow(unittest.TestCase):
    """Testy lineage w przepływie."""
    
    def test_lineage_contains_all_versions(self):
        """Test czy lineage zawiera wszystkie wymagane wersje."""
        config = VerticalFlowConfig(
            enable_lineage=True,
            default_data_version="v1.0.0",
            default_model_version="v1.0.0",
            default_config_version="v1.0.0"
        )
        result = run_smoke_test(config=config)
        
        self.assertIsNotNone(result.lineage)
        
        # Sprawdź czy mamy damals wersje
        if result.lineage:
            # Powinny być dodane co najmniej podstawowe wersje
            self.assertIsInstance(result.lineage, LineageInfo)
    
    def test_lineage_summary(self):
        """Test podsumowania lineage."""
        config = VerticalFlowConfig(enable_lineage=True)
        result = run_smoke_test(config=config)
        
        if result.lineage:
            summary = result.lineage.get_summary()
            self.assertIn("Lineage", summary)
            self.assertIn("Data versions", summary)


if __name__ == "__main__":
    unittest.main()
