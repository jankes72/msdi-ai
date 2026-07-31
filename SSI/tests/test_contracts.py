"""
SSI Contracts Tests - Testy kontraktów danych V2->V3 i V3->V4

Wersja: 1.0
Date: 2026-07-31

Zawiera testy:
- Kontraktów pozytywnych i negatywnych
- Niekompatybilnych wersji
- Polityki podziału danych
- Walidacji kontraktów
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime
import json

# Dodaj katalog nadrzędny do sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from SSI.contracts import (
    V2ToV3Contract,
    V3ToV4Contract,
    ContractValidationError,
    ContractVersion,
    ContractMetadata,
    DataVersion,
    ModelVersion,
    ConfigVersion,
    ResultVersion,
    LineageInfo,
    DataSplitPolicy,
    SplitRatio,
    SplitResult,
    DataSplitter,
    standard_split,
    validate_split_result,
    ContractValidator,
    validate_contract,
    CompatibilityLevel,
    MigrationStrategy,
    CompatibilityPolicy,
    MigrationPolicy,
    VersionCompatibilityChecker,
)


class TestV2ToV3Contract(unittest.TestCase):
    """Testy kontraktu V2->V3."""
    
    def test_create_empty_contract(self):
        """Test tworzenia pustego kontraktu."""
        contract = V2ToV3Contract()
        self.assertIsNotNone(contract.metadata)
        self.assertEqual(contract.metadata.source, "V2")
        self.assertEqual(contract.metadata.target, "V3")
        self.assertEqual(len(contract.observations), 0)
        self.assertEqual(len(contract.statistics), 0)
        self.assertEqual(len(contract.patterns), 0)
    
    def test_validate_empty_contract(self):
        """Test walidacji pustego kontraktu - powinien być poprawny."""
        contract = V2ToV3Contract()
        # Powinno przejść - metadane będą ustawione domyślnie
        self.assertTrue(contract.validate())
    
    def test_create_contract_with_observations(self):
        """Test tworzenia kontraktu z obserwacjami."""
        contract = V2ToV3Contract(
            data_version="v1.0.0",
            model_versions={"model1": "v1.0.0"}
        )
        
        # Dodaj obserwacje
        from SSI.contracts.data_contracts import V2ObservationData
        obs = V2ObservationData(
            observation_id="obs_001",
            match_id="match_001",
            group_id="group_001",
            model_id="model_001",
            prediction="2:1",
            reality="2:1",
            hit=True,
            hit_group=True,
            confidence=0.85
        )
        contract.observations.append(obs)
        
        # Walidacja
        self.assertTrue(contract.validate())
        self.assertEqual(len(contract.observations), 1)
    
    def test_invalid_confidence(self):
        """Test nieprawidłowej wartości confidence."""
        from SSI.contracts.data_contracts import V2ObservationData
        
        obs = V2ObservationData(
            observation_id="obs_001",
            match_id="match_001",
            group_id="group_001",
            model_id="model_001",
            prediction="2:1",
            reality="2:1",
            hit=True,
            hit_group=True,
            confidence=1.5  # Nieprawidłowe!
        )
        
        with self.assertRaises(ContractValidationError):
            obs.validate()
    
    def test_to_dict_and_from_dict(self):
        """Test serializacji i deserializacji kontraktu."""
        contract = V2ToV3Contract(
            data_version="v1.0.0",
            model_versions={"model1": "v1.0.0"}
        )
        
        from SSI.contracts.data_contracts import V2ObservationData
        obs = V2ObservationData(
            observation_id="obs_001",
            match_id="match_001",
            group_id="group_001",
            model_id="model_001",
            prediction="2:1",
            reality="2:1",
            hit=True,
            hit_group=True,
            confidence=0.85
        )
        contract.observations.append(obs)
        
        # Serializacja
        contract_dict = contract.to_dict()
        
        # Deserializacja
        contract_restored = V2ToV3Contract.from_dict(contract_dict)
        
        self.assertEqual(len(contract_restored.observations), 1)
        self.assertEqual(contract_restored.observations[0].observation_id, "obs_001")
        self.assertEqual(contract_restored.data_version, "v1.0.0")
    
    def test_legacy_contract_conversion(self):
        """Test konwersji z formatu dziedzictwa."""
        legacy_data = {
            "obserwacje": [
                {
                    "id": "obs_001",
                    "mecz_id": "match_001",
                    "grupa_id": "group_001",
                    "model_id": "model_001",
                    "predykcja": "2:1",
                    "rzeczywistosc": "2:1",
                    "trafienie": True,
                    "trafienie_grupa": True,
                    "confidence": 0.85,
                    "klasa_grupa": "2"
                }
            ],
            "statystyki_modeli": {
                "calkowita_liczba_obserwacji": 100,
                "liczba_klas": 3,
                "srednia_skutecznosc": 0.80,
                "sredni_confidence": 0.75,
                "liczba_modeli": 5
            }
        }
        
        contract = V2ToV3Contract.from_legacy_dict(legacy_data)
        
        self.assertEqual(len(contract.observations), 1)
        self.assertEqual(contract.observations[0].observation_id, "obs_001")
        self.assertTrue(contract.validate())


class TestV3ToV4Contract(unittest.TestCase):
    """Testy kontraktu V3->V4."""
    
    def test_create_empty_contract(self):
        """Test tworzenia pustego kontraktu."""
        contract = V3ToV4Contract()
        self.assertIsNotNone(contract.metadata)
        self.assertEqual(contract.metadata.source, "V3")
        self.assertEqual(contract.metadata.target, "V4")
        self.assertEqual(len(contract.worlds), 0)
        self.assertEqual(len(contract.patterns), 0)
    
    def test_create_contract_with_worlds(self):
        """Test tworzenia kontraktu ze światami."""
        from SSI.contracts.data_contracts import V3WorldData
        
        contract = V3ToV4Contract(
            data_version="v1.0.0",
            config_version="v1.0.0"
        )
        
        world = V3WorldData(
            world_id="world_001",
            name="Test World",
            world_type="test",
            status="ACTIVE",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            confidence=0.85
        )
        contract.worlds.append(world)
        
        # Walidacja
        self.assertTrue(contract.validate())
        self.assertEqual(len(contract.worlds), 1)
    
    def test_invalid_world_confidence(self):
        """Test nieprawidłowej pewności świata."""
        from SSI.contracts.data_contracts import V3WorldData
        
        world = V3WorldData(
            world_id="world_001",
            name="Test World",
            world_type="test",
            status="ACTIVE",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            confidence=1.5  # Nieprawidłowe!
        )
        
        with self.assertRaises(ContractValidationError):
            world.validate()
    
    def test_to_dict_and_from_dict(self):
        """Test serializacji i deserializacji kontraktu."""
        from SSI.contracts.data_contracts import V3WorldData, V3PatternData
        
        contract = V3ToV4Contract(
            data_version="v1.0.0",
            config_version="v1.0.0"
        )
        
        world = V3WorldData(
            world_id="world_001",
            name="Test World",
            world_type="test",
            status="ACTIVE",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            confidence=0.85
        )
        contract.worlds.append(world)
        
        pattern = V3PatternData(
            pattern_id="pattern_001",
            pattern_type="test",
            frequency=10,
            confidence=0.8
        )
        contract.patterns.append(pattern)
        
        # Serializacja
        contract_dict = contract.to_dict()
        
        # Deserializacja
        contract_restored = V3ToV4Contract.from_dict(contract_dict)
        
        self.assertEqual(len(contract_restored.worlds), 1)
        self.assertEqual(contract_restored.worlds[0].world_id, "world_001")
        self.assertEqual(contract_restored.data_version, "v1.0.0")


class TestContractValidation(unittest.TestCase):
    """Testy walidacji kontraktów."""
    
    def test_validate_empty_metadata(self):
        """Test walidacji pustych metadanych."""
        metadata = ContractMetadata()
        
        with self.assertRaises(ContractValidationError):
            metadata.validate()
    
    def test_validate_contract_with_validator(self):
        """Test walidacji kontraktu poprzez ContractValidator."""
        contract = V2ToV3Contract()
        validator = ContractValidator()
        
        self.assertTrue(validator.validate(contract))
        self.assertEqual(len(validator.get_errors()), 0)
    
    def test_validate_invalid_contract(self):
        """Test walidacji nieprawidłowego kontraktu."""
        from SSI.contracts.data_contracts import V2ObservationData
        
        contract = V2ToV3Contract()
        
        # Dodaj obserwację z nieprawidłowym confidence
        obs = V2ObservationData(
            observation_id="obs_001",
            match_id="match_001",
            group_id="group_001",
            model_id="model_001",
            prediction="2:1",
            reality="2:1",
            hit=True,
            hit_group=True,
            confidence=2.0  # Nieprawidłowe!
        )
        contract.observations.append(obs)
        
        validator = ContractValidator()
        self.assertFalse(validator.validate(contract))
        self.assertGreater(len(validator.get_errors()), 0)
    
    def test_version_compatibility_checker(self):
        """Test VersionCompatibilityChecker."""
        checker = VersionCompatibilityChecker()
        
        # Test kompatybilności
        self.assertTrue(checker.is_compatible("1.0", "1.0"))
        self.assertTrue(checker.is_compatible("1.0", "1.1"))
        self.assertFalse(checker.is_compatible("1.0", "2.0"))
        
        # Test dostępnych wersji kompatybilnych
        compatible = checker.get_compatible_versions("1.0")
        self.assertIn("1.0", compatible)
        self.assertIn("1.1", compatible)


class TestDataSplitPolicy(unittest.TestCase):
    """Testy polityki podziału danych."""
    
    def test_standard_policy_ratios(self):
        """Test standardowej polityki 50/10/40."""
        policy = DataSplitPolicy.standard_50_10_40()
        
        self.assertEqual(policy.train_ratio, 0.50)
        self.assertEqual(policy.validation_ratio, 0.10)
        self.assertEqual(policy.observation_ratio, 0.40)
    
    def test_policy_normalization(self):
        """Test normalizacji polityki."""
        policy = DataSplitPolicy(
            train_ratio=0.50,
            validation_ratio=0.20,
            observation_ratio=0.30
        )
        
        # Powinny być znormalizowane
        total = policy.train_ratio + policy.validation_ratio + policy.observation_ratio
        self.assertAlmostEqual(total, 1.0, places=5)
    
    def test_invalid_policy(self):
        """Test nieprawidłowej polityki."""
        with self.assertRaises(ValueError):
            DataSplitPolicy(
                train_ratio=0.50,
                validation_ratio=0.20,
                observation_ratio=0.40  # Suma = 1.10
            )
    
    def test_split_data(self):
        """Test podziału danych."""
        policy = DataSplitPolicy.standard_50_10_40()
        splitter = DataSplitter(policy)
        
        data = list(range(100))
        result = splitter.split_data(data, seed=42)
        
        # Sprawdź rozmiary
        self.assertEqual(len(result.train_data), 50)
        self.assertEqual(len(result.validation_data), 10)
        self.assertEqual(len(result.observation_data), 40)
        
        total = len(result.train_data) + len(result.validation_data) + len(result.observation_data)
        self.assertEqual(total, 100)
    
    def test_split_reproducibility(self):
        """Test powtarzalności podziału."""
        policy = DataSplitPolicy.standard_50_10_40()
        splitter = DataSplitter(policy)
        
        data = list(range(100))
        
        # Ten sam seed powinien dać ten sam rezultat
        result1 = splitter.split_data(data, seed=42)
        result2 = splitter.split_data(data, seed=42)
        
        self.assertEqual(result1.train_indices, result2.train_indices)
        self.assertEqual(result1.validation_indices, result2.validation_indices)
        self.assertEqual(result1.observation_indices, result2.observation_indices)
    
    def test_validate_split_result(self):
        """Test walidacji wyniku podziału."""
        policy = DataSplitPolicy.standard_50_10_40()
        splitter = DataSplitter(policy)
        
        data = list(range(100))
        result = splitter.split_data(data, seed=42)
        
        # Walidacja powinna przejść
        self.assertTrue(validate_split_result(result, policy))
    
    def test_validate_invalid_split(self):
        """Test walidacji nieprawidłowego podziału."""
        policy = DataSplitPolicy.standard_50_10_40()
        
        # Utwórz nieprawidłowy wynik
        result = SplitResult(
            train_data=list(range(60)),
            validation_data=list(range(10)),
            observation_data=list(range(30)),
            split_policy=policy,
            seed=42
        )
        
        with self.assertRaises(ValueError):
            validate_split_result(result, policy)


class TestVersionIdentifiers(unittest.TestCase):
    """Testy identyfikatorów wersji."""
    
    def test_data_version(self):
        """Test DataVersion."""
        dv = DataVersion(
            version="1.0.0",
            source="v2_models",
            description="Test data"
        )
        
        self.assertTrue(dv.validate())
        self.assertEqual(dv.version, "1.0.0")
        
        # Test serializacji
        dv_dict = dv.to_dict()
        dv_restored = DataVersion.from_dict(dv_dict)
        self.assertEqual(dv_restored.version, "1.0.0")
        self.assertEqual(dv_restored.source, "v2_models")
    
    def test_model_version(self):
        """Test ModelVersion."""
        mv = ModelVersion(
            version="1.0.0",
            model_id="model_001",
            model_type="random_forest",
            accuracy=0.85
        )
        
        self.assertTrue(mv.validate())
        self.assertEqual(mv.version, "1.0.0")
        self.assertEqual(mv.accuracy, 0.85)
    
    def test_invalid_model_accuracy(self):
        """Test nieprawidłowej dokładności modelu."""
        mv = ModelVersion(
            version="1.0.0",
            model_id="model_001",
            accuracy=1.5  # Nieprawidłowe!
        )
        with self.assertRaises(ValueError):
            mv.validate()
    
    def test_lineage_info(self):
        """Test LineageInfo."""
        lineage = LineageInfo(
            workflow_name="Test Workflow"
        )
        
        # Dodaj wersje
        lineage.add_data_version("v1.0.0")
        lineage.add_model_version("v1.0.0")
        lineage.add_config_version("v1.0.0")
        
        result_version = ResultVersion(
            version="1.0.0",
            result_type="decision",
            confidence=0.85
        )
        lineage.add_result_version(result_version)
        
        # Finalizacja
        lineage_info = lineage.finalize()
        
        self.assertEqual(len(lineage_info.data_versions), 1)
        self.assertEqual(len(lineage_info.model_versions), 1)
        self.assertEqual(len(lineage_info.config_versions), 1)
        self.assertEqual(len(lineage_info.result_versions), 1)


class TestMigrationPolicy(unittest.TestCase):
    """Testy polityki migracji."""
    
    def test_compatibility_policy(self):
        """Test polityki kompatybilności."""
        policy = CompatibilityPolicy()
        
        # Test kompatybilności
        level = policy.get_compatibility("1.0", "1.0")
        self.assertEqual(level, CompatibilityLevel.FULL)
        
        level = policy.get_compatibility("1.0", "1.1")
        self.assertEqual(level, CompatibilityLevel.BACKWARD)
    
    def test_migration_strategy(self):
        """Test strategii migracji."""
        policy = CompatibilityPolicy()
        
        strategy = policy.get_migration_strategy("1.0", "1.0")
        self.assertEqual(strategy, MigrationStrategy.AUTOMATIC)
        
        strategy = policy.get_migration_strategy("1.0", "1.1")
        self.assertEqual(strategy, MigrationStrategy.CONVERT)
    
    def test_can_migrate(self):
        """Test możliwości migracji."""
        policy = CompatibilityPolicy()
        
        self.assertTrue(policy.can_migrate("1.0", "1.0"))
        self.assertTrue(policy.can_migrate("1.0", "1.1"))
        self.assertFalse(policy.can_migrate("1.0", "2.0"))
    
    def test_migration_policy_validation(self):
        """Test walidacji kompatybilności."""
        policy = MigrationPolicy()
        
        contract = V2ToV3Contract()
        
        # Wersja 1.0 powinna być kompatybilna z 1.0
        self.assertTrue(policy.validate_compatibility(contract, "1.0"))
        
        # Wersja 1.0 nie powinna być kompatybilna z 2.0 (chyba że allow_version_mismatch=True)
        contract.metadata.version = ContractVersion.V2_0
        policy.allow_version_mismatch = False
        self.assertFalse(policy.validate_compatibility(contract, "1.0"))


class TestContractMigration(unittest.TestCase):
    """Testy migracji kontraktów."""
    
    def test_migrate_contract_same_version(self):
        """Test migracji kontraktu do tej samej wersji."""
        policy = MigrationPolicy()
        contract = V2ToV3Contract()
        
        result = policy.migrate(contract, "1.0")
        
        self.assertIsInstance(result, V2ToV3Contract)
        self.assertEqual(result.metadata.version.value, "1.0")
    
    def test_migration_history(self):
        """Test historii migracji."""
        policy = MigrationPolicy()
        contract = V2ToV3Contract()
        
        policy.migrate(contract, "1.0")
        
        self.assertEqual(len(policy.migration_history), 1)
        self.assertEqual(policy.migration_history[0]["contract_type"], "V2ToV3Contract")


if __name__ == "__main__":
    unittest.main()
