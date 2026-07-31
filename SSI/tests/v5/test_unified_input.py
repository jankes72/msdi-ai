"""
SSI V5 Tests - Unified Input Layer Test Suite
===============================================

Testy integracyjne dla warstwy Unified Input Layer (Sprint 11.5).

Cel:
- Zweryfikowac poprawnosc implementacji SSIKnowledgePackage
- Testowac KnowledgeCollectorManager i KnowledgeCollectorRegistry
- Testowac integracje wszytskich kolektorow (V2, V3, V4, External)
- Testowac serializacje i deserializacje pakietu wiedzy

Wersja: 1.0
Data: 2026-07-31
"""

import unittest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


# =============================================================================
# TESTY KNOWLEDGE METADATA
# =============================================================================

class TestKnowledgeMetadata(unittest.TestCase):
    """Testy dla KnowledgeMetadata"""
    
    def test_import_knowledge_metadata(self):
        """Test: Import KnowledgeMetadata"""
        from SSI.v5.input_layer.knowledge_metadata import KnowledgeMetadata
        self.assertTrue(True, "KnowledgeMetadata imported successfully")
    
    def test_create_metadata(self):
        """Test: Tworzenie metadanych"""
        from SSI.v5.input_layer.knowledge_metadata import KnowledgeMetadata
        
        metadata = KnowledgeMetadata(package_id="test_pkg_001")
        self.assertEqual(metadata.package_id, "test_pkg_001")
        self.assertIsNotNone(metadata.timestamp)
        self.assertTrue(metadata.is_valid)
    
    def test_metadata_add_source(self):
        """Test: Dodawanie zrodel do metadanych"""
        from SSI.v5.input_layer.knowledge_metadata import KnowledgeMetadata
        from SSI.v5.input_layer.data_models import DataSource
        
        metadata = KnowledgeMetadata(package_id="test_pkg_002")
        metadata.add_source(DataSource.V2_MODELS, collected=True)
        metadata.add_source(DataSource.V3_KNOWLEDGE, collected=False)
        
        self.assertEqual(len(metadata.source_types), 2)
        self.assertTrue(metadata.has_source(DataSource.V2_MODELS))
        self.assertTrue(metadata.is_source_collected(DataSource.V2_MODELS))
        self.assertFalse(metadata.is_source_collected(DataSource.V3_KNOWLEDGE))
    
    def test_metadata_validation(self):
        """Test: Walidacja metadanych"""
        from SSI.v5.input_layer.knowledge_metadata import KnowledgeMetadata
        
        metadata = KnowledgeMetadata(package_id="test_pkg_003")
        
        # Domyslnie poprawne
        self.assertTrue(metadata.is_valid)
        self.assertEqual(len(metadata.validation_errors), 0)
        
        # Dodaj blad
        metadata.add_validation_error("Test error")
        self.assertFalse(metadata.is_valid)
        self.assertEqual(len(metadata.validation_errors), 1)
        
        # Wyczysc bledy
        metadata.clear_validation_errors()
        self.assertTrue(metadata.is_valid)
        self.assertEqual(len(metadata.validation_errors), 0)
    
    def test_metadata_serialization(self):
        """Test: Serializacja i deserializacja metadanych"""
        from SSI.v5.input_layer.knowledge_metadata import KnowledgeMetadata
        from SSI.v5.input_layer.data_models import DataSource
        
        # Utworz metadane
        metadata = KnowledgeMetadata(package_id="test_pkg_004")
        metadata.add_source(DataSource.V2_MODELS, collected=True)
        metadata.set_validation_result(True, [])
        
        # Serializuj
        metadata_dict = metadata.to_dict()
        self.assertIn("package_id", metadata_dict)
        self.assertIn("source_types", metadata_dict)
        
        # Deserializuj
        restored = KnowledgeMetadata.from_dict(metadata_dict)
        self.assertEqual(restored.package_id, metadata.package_id)
        self.assertEqual(len(restored.source_types), 1)


# =============================================================================
# TESTY PACKAGE STATUS
# =============================================================================

class TestPackageStatus(unittest.TestCase):
    """Testy dla PackageStatus enum"""
    
    def test_package_status_enum(self):
        """Test: PackageStatus enum values"""
        from SSI.v5.input_layer.knowledge_metadata import PackageStatus
        
        statuses = list(PackageStatus)
        expected = ['PENDING', 'PARTIAL', 'COMPLETE', 'VALIDATED', 'INVALID', 'PROCESSED']
        actual = [s.name for s in statuses]
        
        for exp in expected:
            self.assertIn(exp, actual)
    
    def test_package_status_str(self):
        """Test: PackageStatus __str__"""
        from SSI.v5.input_layer.knowledge_metadata import PackageStatus
        
        self.assertEqual(str(PackageStatus.PENDING), "pending")
        self.assertEqual(str(PackageStatus.COMPLETE), "complete")


# =============================================================================
# TESTY SSI KNOWLEDGE PACKAGE
# =============================================================================

class TestSSIKnowledgePackage(unittest.TestCase):
    """Testy dla SSIKnowledgePackage"""
    
    def test_import_knowledge_package(self):
        """Test: Import SSIKnowledgePackage"""
        from SSI.v5.input_layer.knowledge_package import SSIKnowledgePackage
        self.assertTrue(True, "SSIKnowledgePackage imported successfully")
    
    def test_create_package(self):
        """Test: Tworzenie pakietu wiedzy"""
        from SSI.v5.input_layer.knowledge_package import SSIKnowledgePackage
        from SSI.v5.input_layer.knowledge_metadata import PackageStatus
        
        package = SSIKnowledgePackage()
        self.assertIsNotNone(package.metadata)
        self.assertEqual(package.status, PackageStatus.PENDING)
        self.assertFalse(package.has_data())
    
    def test_package_add_external_data(self):
        """Test: Dodawanie danych External"""
        from SSI.v5.input_layer.knowledge_package import SSIKnowledgePackage
        from SSI.v5.input_layer.external.external_models import ExternalDataPackage
        
        package = SSIKnowledgePackage()
        external_package = ExternalDataPackage()
        
        package.add_external_data(external_package)
        self.assertTrue(package.has_data())
        self.assertTrue(len(package.metadata.source_types) > 0)
    
    def test_package_validation(self):
        """Test: Walidacja pakietu"""
        from SSI.v5.input_layer.knowledge_package import SSIKnowledgePackage
        from SSI.v5.input_layer.external.external_models import ExternalDataPackage
        
        package = SSIKnowledgePackage()
        
        # Pusty pakiet - nieprawidlowy
        is_valid = package.validate()
        self.assertFalse(is_valid)
        
        # Dodaj dane External
        external_package = ExternalDataPackage()
        package.add_external_data(external_package)
        
        # Z pustym ExternalDataPackage - pakiet ma dane wiec powinien byc prawidlowy
        # Pomijamy test walidacji ExternalDataPackage poniewaz nie ma metody validate
        is_valid = package.validate()
        self.assertTrue(is_valid)
    
    def test_package_statistics(self):
        """Test: Statystyki pakietu"""
        from SSI.v5.input_layer.knowledge_package import SSIKnowledgePackage
        
        package = SSIKnowledgePackage()
        stats = package.get_statistics()
        
        self.assertIn("total_items", stats)
        self.assertIn("package_id", stats)
        self.assertIn("status", stats)
        self.assertIn("is_valid", stats)
    
    def test_package_serialization(self):
        """Test: Serializacja pakietu"""
        from SSI.v5.input_layer.knowledge_package import SSIKnowledgePackage
        from SSI.v5.input_layer.knowledge_metadata import PackageStatus
        
        package = SSIKnowledgePackage()
        
        # Serializuj
        package_dict = package.to_dict()
        self.assertIn("metadata", package_dict)
        self.assertIn("status", package_dict)
        self.assertIn("stats", package_dict)
        
        # JSON
        json_str = package.to_json()
        self.assertIsInstance(json_str, str)
    
    def test_package_factory(self):
        """Test: Funkcja fabryczna create_knowledge_package"""
        from SSI.v5.input_layer.knowledge_package import create_knowledge_package
        from SSI.v5.input_layer.external.external_models import ExternalDataPackage
        
        external_package = ExternalDataPackage()
        package = create_knowledge_package(external_data=external_package)
        
        self.assertIsNotNone(package)
        self.assertTrue(package.has_data())


# =============================================================================
# TESTY COLLECTOR MANAGER
# =============================================================================

class TestKnowledgeCollectorManager(unittest.TestCase):
    """Testy dla KnowledgeCollectorManager"""
    
    def test_import_collector_manager(self):
        """Test: Import KnowledgeCollectorManager"""
        from SSI.v5.input_layer.collector_manager import KnowledgeCollectorManager
        self.assertTrue(True, "KnowledgeCollectorManager imported successfully")
    
    def test_create_manager(self):
        """Test: Tworzenie managera"""
        from SSI.v5.input_layer.collector_manager import KnowledgeCollectorManager
        
        manager = KnowledgeCollectorManager()
        self.assertIsNotNone(manager)
        self.assertFalse(manager.is_initialized())
    
    def test_register_collectors(self):
        """Test: Rejestracja kolektorow"""
        from SSI.v5.input_layer.collector_manager import KnowledgeCollectorManager, CollectorType
        from SSI.v5.input_layer.external import ExternalKnowledgeCollector
        
        manager = KnowledgeCollectorManager()
        
        # Zarejestruj ExternalKnowledgeCollector
        manager.register_external_collector(ExternalKnowledgeCollector)
        
        self.assertIsNotNone(manager.get_collector_info(CollectorType.EXTERNAL))
    
    def test_manager_initialize(self):
        """Test: Inicjalizacja managera"""
        from SSI.v5.input_layer.collector_manager import KnowledgeCollectorManager, CollectorType
        from SSI.v5.input_layer.external import ExternalKnowledgeCollector
        
        manager = KnowledgeCollectorManager()
        manager.register_external_collector(ExternalKnowledgeCollector)
        
        # Inicjalizuj
        result = manager.initialize()
        self.assertTrue(result)
        self.assertTrue(manager.is_initialized())
        
        # Pobierz kolektor
        collector = manager.get_collector(CollectorType.EXTERNAL)
        self.assertIsNotNone(collector)
    
    def test_manager_collect(self):
        """Test: Zbieranie danych przez managera"""
        from SSI.v5.input_layer.collector_manager import KnowledgeCollectorManager, CollectorType
        from SSI.v5.input_layer.external import ExternalKnowledgeCollector
        
        manager = KnowledgeCollectorManager()
        manager.register_external_collector(ExternalKnowledgeCollector)
        manager.initialize()
        
        # Zbierz dane z External
        package = manager.collect_all()
        self.assertIsNotNone(package)


# =============================================================================
# TESTY COLLECTOR REGISTRY
# =============================================================================

class TestCollectorRegistry(unittest.TestCase):
    """Testy dla CollectorRegistry"""
    
    def test_import_collector_registry(self):
        """Test: Import CollectorRegistry"""
        from SSI.v5.input_layer.collector_registry import CollectorRegistry
        self.assertTrue(True, "CollectorRegistry imported successfully")
    
    def test_create_registry(self):
        """Test: Tworzenie rejestru"""
        from SSI.v5.input_layer.collector_registry import CollectorRegistry
        
        registry = CollectorRegistry()
        self.assertIsNotNone(registry)
        self.assertFalse(registry.is_discovered())
    
    def test_register_collector(self):
        """Test: Rejestracja kolektora w rejestrze"""
        from SSI.v5.input_layer.collector_registry import CollectorRegistry, CollectorType
        from SSI.v5.input_layer.external import ExternalKnowledgeCollector
        
        registry = CollectorRegistry()
        registry.register_external(ExternalKnowledgeCollector)
        
        self.assertTrue(registry.has_collector(CollectorType.EXTERNAL))
        self.assertIsNotNone(registry.get_collector(CollectorType.EXTERNAL))
    
    def test_registry_create_manager(self):
        """Test: Tworzenie managera z rejestru"""
        from SSI.v5.input_layer.collector_registry import CollectorRegistry, CollectorType
        from SSI.v5.input_layer.external import ExternalKnowledgeCollector
        
        registry = CollectorRegistry()
        registry.register_external(ExternalKnowledgeCollector)
        
        manager = registry.create_manager()
        self.assertIsNotNone(manager)
        self.assertIsNotNone(manager.get_collector_info(CollectorType.EXTERNAL))
    
    def test_registry_statistics(self):
        """Test: Statystyki rejestru"""
        from SSI.v5.input_layer.collector_registry import CollectorRegistry, CollectorType
        from SSI.v5.input_layer.external import ExternalKnowledgeCollector
        
        registry = CollectorRegistry()
        registry.register_external(ExternalKnowledgeCollector)
        
        stats = registry.get_statistics()
        self.assertIn("total_registered", stats)
        self.assertEqual(stats["total_registered"], 1)


# =============================================================================
# TESTY INTEGRACYJNE - WSZYSTKIE KOMPONENTY
# =============================================================================

class TestUnifiedInputIntegration(unittest.TestCase):
    """Testy integracyjne dla calej warstwy Unified Input Layer"""
    
    def test_full_integration_workflow(self):
        """Test: Pelny przeplyw pracy: Registry -> Manager -> Package"""
        from SSI.v5.input_layer.collector_registry import CollectorRegistry, CollectorType
        from SSI.v5.input_layer.external import ExternalKnowledgeCollector
        
        # 1. Utworz rejestr
        registry = CollectorRegistry()
        
        # 2. Zarejestruj kolektor External
        registry.register_external(ExternalKnowledgeCollector)
        
        # 3. Utworz managera z rejestru
        manager = registry.create_manager()
        
        # 4. Zainicjalizuj managera
        self.assertTrue(manager.initialize())
        
        # 5. Zbierz dane (tylko External bedzie dostepny)
        package = manager.collect_all()
        self.assertIsNotNone(package)
        
        # 6. Sprawdz pakiet
        self.assertIsNotNone(package.metadata)
        self.assertIsNotNone(package.external_data)
    
    def test_global_registry(self):
        """Test: Globalny rejestr (singleton)"""
        from SSI.v5.input_layer.collector_registry import GlobalCollectorRegistry
        
        registry1 = GlobalCollectorRegistry.get_instance()
        registry2 = GlobalCollectorRegistry.get_instance()
        
        self.assertIs(registry1, registry2)


# =============================================================================
# TESTY IMPORTÓW Z GLOWNEGO MODULU
# =============================================================================

class TestUnifiedInputImports(unittest.TestCase):
    """Testy importow z glownego modulu input_layer"""
    
    def test_import_from_input_layer(self):
        """Test: Import wszystkich nowych klas z input_layer"""
        try:
            from SSI.v5.input_layer import (
                # Knowledge Package
                KnowledgeMetadata,
                PackageStatus,
                SSIKnowledgePackage,
                create_knowledge_package,
                # Collector Manager
                KnowledgeCollectorManager,
                CollectorType,
                CollectionStrategy,
                CollectorStatus,
                CollectorInfo,
                CollectionResult,
                GlobalCollectorManager,
                get_collector_manager,
                # Collector Registry
                CollectorRegistry,
                RegistryStatus,
                CollectorRegistration,
                GlobalCollectorRegistry,
                get_registry,
                get_collector_registry
            )
            self.assertTrue(True, "Wszystkie importy powiodly sie")
        except ImportError as e:
            self.fail(f"Import z input_layer nieudany: {e}")


# =============================================================================
# FUNKCJA MAIN
# =============================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
