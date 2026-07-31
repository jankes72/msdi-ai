"""
SSI V5 Tests - External Knowledge Collector Test Suite
======================================================

Testy jednostkowe dla ExternalKnowledgeCollector (Sprint 11.4 - FAZA 4).

Cel:
- Zweryfikowac poprawnosc implementacji ExternalKnowledgeCollector
- Testowac inicjalizacje zrodel danych
- Testowac zbieranie danych z roznych zrodel
- Testowac agregacje i walidacje danych

Wersja: 1.0
Data: 2026-07-31
"""

import unittest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


class TestExternalKnowledgeCollectorImports(unittest.TestCase):
    """Testy importow - weryfikacja ze ExternalKnowledgeCollector moze byc zaimportowany."""
    
    def test_import_external_collector_module(self):
        """Test: Import modulu external_collector"""
        try:
            from SSI.v5.input_layer.external import external_collector
            self.assertTrue(True, "Import external_collector module powiodl sie")
        except ImportError as e:
            self.fail(f"Import external_collector module nieudany: {e}")
    
    def test_import_ExternalKnowledgeCollector_class(self):
        """Test: Import klasy ExternalKnowledgeCollector"""
        try:
            from SSI.v5.input_layer.external.external_collector import ExternalKnowledgeCollector
            self.assertTrue(True, "Import ExternalKnowledgeCollector class powiodl sie")
        except ImportError as e:
            self.fail(f"Import ExternalKnowledgeCollector class nieudany: {e}")
    
    def test_import_from_input_layer_external(self):
        """Test: Import ExternalKnowledgeCollector z SSI.v5.input_layer.external"""
        try:
            from SSI.v5.input_layer.external import ExternalKnowledgeCollector
            self.assertTrue(True, "Import z SSI.v5.input_layer.external powiodl sie")
        except ImportError as e:
            self.fail(f"Import z SSI.v5.input_layer.external nieudany: {e}")


class TestExternalKnowledgeCollectorInitialization(unittest.TestCase):
    """Testy inicjalizacji ExternalKnowledgeCollector."""
    
    def setUp(self):
        """Przygotowanie do testu."""
        from SSI.v5.input_layer.external.external_collector import ExternalKnowledgeCollector
        self.collector = ExternalKnowledgeCollector()
    
    def test_create_collector_instance(self):
        """Test: Utworzenie instancji ExternalKnowledgeCollector"""
        from SSI.v5.input_layer.external.external_collector import ExternalKnowledgeCollector
        collector = ExternalKnowledgeCollector()
        self.assertIsInstance(collector, ExternalKnowledgeCollector)
        self.assertTrue(True, "Instancja ExternalKnowledgeCollector zostala utworzona")
    
    def test_collector_default_status(self):
        """Test: Domyslny status kolektora po utworzeniu"""
        from SSI.v5.input_layer.external.source_types import ExternalStatus
        self.assertEqual(self.collector._status, ExternalStatus.PENDING)
        self.assertFalse(self.collector._initialized)
    
    def test_collector_has_source_attributes(self):
        """Test: Kolektor ma atrybuty dla zrodel danych"""
        self.assertIsNone(self.collector._developer_source)
        self.assertEqual(self.collector._laboratory_sources, {})
        self.assertIsNone(self.collector._agent_source)
        self.assertIsNone(self.collector._system_source)


class TestExternalKnowledgeCollectorInitialize(unittest.TestCase):
    """Testy metody initialize() ExternalKnowledgeCollector."""
    
    def setUp(self):
        """Przygotowanie do testu."""
        from SSI.v5.input_layer.external.external_collector import ExternalKnowledgeCollector
        self.collector = ExternalKnowledgeCollector()
    
    def test_initialize_returns_true(self):
        """Test: initialize() zwraca True"""
        result = self.collector.initialize()
        self.assertTrue(result, "initialize() powinno zwrocic True")
    
    def test_initialize_sets_initialized_flag(self):
        """Test: initialize() ustawia _initialized na True"""
        self.collector.initialize()
        self.assertTrue(self.collector._initialized)
    
    def test_initialize_sets_status_to_ready(self):
        """Test: initialize() ustawia status na READY"""
        from SSI.v5.input_layer.external.source_types import ExternalStatus
        self.collector.initialize()
        self.assertEqual(self.collector._status, ExternalStatus.READY)
    
    def test_initialize_creates_developer_source(self):
        """Test: initialize() tworzy DeveloperSource"""
        from SSI.v5.input_layer.external.sources.developer_source import DeveloperSource
        self.collector.initialize()
        self.assertIsInstance(self.collector._developer_source, DeveloperSource)
        self.assertEqual(self.collector._developer_source.developer_id, "default")
    
    def test_initialize_creates_system_source(self):
        """Test: initialize() tworzy SystemSource"""
        from SSI.v5.input_layer.external.sources.system_source import SystemSource
        self.collector.initialize()
        self.assertIsInstance(self.collector._system_source, SystemSource)
    
    def test_initialize_creates_agent_source(self):
        """Test: initialize() tworzy AgentSource"""
        from SSI.v5.input_layer.external.sources.agent_source import AgentSource
        self.collector.initialize()
        self.assertIsInstance(self.collector._agent_source, AgentSource)
    
    def test_initialize_creates_laboratory_sources(self):
        """Test: initialize() tworzy LaboratorySource dla kazdego LaboratoryType"""
        from SSI.v5.input_layer.external.sources.laboratory_source import LaboratorySource
        from SSI.v5.input_layer.external.source_types import LaboratoryType
        
        self.collector.initialize()
        
        # Powinny byc 4 typy laboratoriow
        self.assertEqual(len(self.collector._laboratory_sources), 4)
        
        # Sprawdz, ze kazdy typ ma swoje zrodlo
        for lab_type in LaboratoryType:
            self.assertIn(lab_type.value, self.collector._laboratory_sources)
            source = self.collector._laboratory_sources[lab_type.value]
            self.assertIsInstance(source, LaboratorySource)
            self.assertEqual(source.laboratory_type, lab_type)
    
    def test_initialize_with_custom_developer_id(self):
        """Test: initialize() z niestandardowym developer_id"""
        custom_id = "test_developer_123"
        result = self.collector.initialize(developer_id=custom_id)
        self.assertTrue(result)
        self.assertEqual(self.collector._developer_source.developer_id, custom_id)


class TestExternalKnowledgeCollectorSourceTypes(unittest.TestCase):
    """Testy typow zrodel w ExternalKnowledgeCollector."""
    
    def test_laboratory_type_iteration(self):
        """Test: Laboratorium types can be iterated (the fix for line 110 bug)"""
        from SSI.v5.input_layer.external.source_types import LaboratoryType
        
        # This was the bug: trying to iterate over SourceType.LABORATORIES
        # Now we iterate over LaboratoryType directly
        lab_types_count = 0
        for lab_type in LaboratoryType:
            self.assertTrue(hasattr(lab_type, 'value'))
            self.assertTrue(hasattr(lab_type, 'name'))
            lab_types_count += 1
        
        self.assertEqual(lab_types_count, 4)  # WORLD_LAB, TYPE_LAB, GROUP_LAB, COUPON_LAB
    
    def test_laboratory_type_values(self):
        """Test: LaboratoryType values are correct"""
        from SSI.v5.input_layer.external.source_types import LaboratoryType
        
        expected_values = ["world_lab", "type_lab", "group_lab", "coupon_lab"]
        actual_values = [lab_type.value for lab_type in LaboratoryType]
        
        self.assertEqual(sorted(actual_values), sorted(expected_values))


class TestExternalKnowledgeCollectorStatus(unittest.TestCase):
    """Testy statusow ExternalKnowledgeCollector."""
    
    def test_external_status_enum(self):
        """Test: ExternalStatus enum values"""
        from SSI.v5.input_layer.external.source_types import ExternalStatus
        
        statuses = list(ExternalStatus)
        self.assertGreater(len(statuses), 0)
        
        # Check that we have expected statuses
        expected_status_names = ['PENDING', 'COLLECTING', 'COMPLETED', 'FAILED', 
                                 'VALIDATING', 'VALIDATED', 'INVALID']
        actual_names = [s.name for s in statuses]
        
        for expected in expected_status_names:
            self.assertIn(expected, actual_names)
    
    def test_status_is_successful(self):
        """Test: is_successful() method"""
        from SSI.v5.input_layer.external.source_types import ExternalStatus
        
        self.assertTrue(ExternalStatus.COMPLETED.is_successful())
        self.assertTrue(ExternalStatus.VALIDATED.is_successful())
        self.assertFalse(ExternalStatus.FAILED.is_successful())
        self.assertFalse(ExternalStatus.PENDING.is_successful())
    
    def test_status_is_failed(self):
        """Test: is_failed() method"""
        from SSI.v5.input_layer.external.source_types import ExternalStatus
        
        self.assertTrue(ExternalStatus.FAILED.is_failed())
        self.assertTrue(ExternalStatus.INVALID.is_failed())
        self.assertFalse(ExternalStatus.COMPLETED.is_failed())
    
    def test_status_is_in_progress(self):
        """Test: is_in_progress() method"""
        from SSI.v5.input_layer.external.source_types import ExternalStatus
        
        self.assertTrue(ExternalStatus.COLLECTING.is_in_progress())
        self.assertTrue(ExternalStatus.VALIDATING.is_in_progress())
        self.assertFalse(ExternalStatus.COMPLETED.is_in_progress())


if __name__ == '__main__':
    unittest.main()
