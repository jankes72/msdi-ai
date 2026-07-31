"""
SSI V5 Tests - Testy dla V3 Knowledge Collector
Testy jednostkowe dla SSI/v5/input_layer/v3_collector.py

Wersja: 1.0
Data: 2026-07-31
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import uuid

# Testowany moduł
from SSI.v5.input_layer.v3_collector import (
    V3KnowledgeCollector, tworz_v3_collector, get_v3_collector, reset_v3_collector
)
from SSI.v5.input_layer.data_models import (
    V3DataPackage, WorldInfo, PatternInfo, RelationshipInfo, V3Metadata,
    DataSource, DataCategory, DataStatus
)


class TestV3KnowledgeCollector(unittest.TestCase):
    """Testy dla klasy V3KnowledgeCollector"""
    
    def setUp(self):
        """Procedura przygotowawcza przed kazdym testem"""
        # Resetuj singleton
        reset_v3_collector()
        self.collector = tworz_v3_collector()
    
    def tearDown(self):
        """Sprzatanie po kazdym tescie"""
        reset_v3_collector()
    
    # =============================================================================
    # TESTY INICJALIZACJI
    # =============================================================================
    
    def test_init_creates_collector(self):
        """Test: Inicjalizacja tworzy poprawny kolektor"""
        collector = tworz_v3_collector()
        self.assertIsInstance(collector, V3KnowledgeCollector)
        self.assertFalse(collector._initialized)
    
    def test_init_sets_default_values(self):
        """Test: Inicjalizacja ustawia domyslne wartosci"""
        collector = tworz_v3_collector()
        self.assertIsNone(collector._v3_integration)
        self.assertIsNone(collector._world_manager)
        self.assertIsNone(collector._memory_manager)
        self.assertIsNone(collector._knowledge_engine)
    
    # =============================================================================
    # TESTY SINGLETON
    # =============================================================================
    
    def test_get_v3_collector_returns_singleton(self):
        """Test: get_v3_collector zwraca te sama instancje"""
        collector1 = get_v3_collector()
        collector2 = get_v3_collector()
        self.assertIs(collector1, collector2)
    
    def test_reset_v3_collector_creates_new_instance(self):
        """Test: reset_v3_collector tworzy nowa instancje"""
        collector1 = get_v3_collector()
        reset_v3_collector()
        collector2 = get_v3_collector()
        self.assertIsNot(collector1, collector2)
    
    # =============================================================================
    # TESTY COLLECT_WORLDS
    # =============================================================================
    
    def test_collect_worlds_returns_list(self):
        """Test: collect_worlds zwraca liste WorldInfo"""
        worlds = self.collector.collect_worlds()
        self.assertIsInstance(worlds, list)
        if worlds:
            self.assertIsInstance(worlds[0], WorldInfo)
    
    def test_collect_worlds_returns_default_worlds(self):
        """Test: collect_worlds zwraca domyslne swiaty"""
        worlds = self.collector.collect_worlds()
        # Powinno zwrocic 5 domyslnych swiatow
        self.assertEqual(len(worlds), 5)
        world_names = [w.world_name for w in worlds]
        self.assertIn("swiat_zmian_kursow", world_names)
        self.assertIn("swiat_meta", world_names)
    
    def test_collect_worlds_has_required_fields(self):
        """Test:Swiaty maja wszystkie wymagane pola"""
        worlds = self.collector.collect_worlds()
        for world in worlds:
            self.assertIsInstance(world.world_name, str)
            self.assertIsInstance(world.world_type, str)
            self.assertIsInstance(world.status, str)
            self.assertIsInstance(world.version, str)
            self.assertTrue(len(world.world_name) > 0)
            self.assertTrue(len(world.world_type) > 0)
    
    # =============================================================================
    # TESTY COLLECT_PATTERNS
    # =============================================================================
    
    def test_collect_patterns_returns_list(self):
        """Test: collect_patterns zwraca liste PatternInfo"""
        patterns = self.collector.collect_patterns()
        self.assertIsInstance(patterns, list)
        if patterns:
            self.assertIsInstance(patterns[0], PatternInfo)
    
    def test_collect_patterns_returns_default_patterns(self):
        """Test: collect_patterns zwraca domyslne wzorce"""
        patterns = self.collector.collect_patterns()
        # Powinno zwrocic 5 domyslnych wzorców
        self.assertEqual(len(patterns), 5)
        pattern_names = [p.pattern_name for p in patterns]
        self.assertIn("wzorzec_ rosnacy_trend", pattern_names)
        self.assertIn("wzorzec_synchronizacja", pattern_names)
    
    def test_collect_patterns_has_required_fields(self):
        """Test: Wzorce maja wszystkie wymagane pola"""
        patterns = self.collector.collect_patterns()
        for pattern in patterns:
            self.assertIsInstance(pattern.pattern_name, str)
            self.assertIsInstance(pattern.pattern_type, str)
            self.assertTrue(len(pattern.pattern_name) > 0)
            self.assertTrue(len(pattern.pattern_type) > 0)
    
    # =============================================================================
    # TESTY COLLECT_RELATIONSHIPS
    # =============================================================================
    
    def test_collect_relationships_returns_list(self):
        """Test: collect_relationships zwraca liste RelationshipInfo"""
        relationships = self.collector.collect_relationships()
        self.assertIsInstance(relationships, list)
        if relationships:
            self.assertIsInstance(relationships[0], RelationshipInfo)
    
    def test_collect_relationships_returns_default_relationships(self):
        """Test: collect_relationships zwraca domyslne relacje"""
        relationships = self.collector.collect_relationships()
        # Powinno zwrocic 5 domyslnych relacji
        self.assertEqual(len(relationships), 5)
        relationship_ids = [r.relationship_id for r in relationships]
        # Sprawdzamy czy ID sa unikalne
        self.assertEqual(len(relationship_ids), len(set(relationship_ids)))
    
    def test_collect_relationships_has_required_fields(self):
        """Test: Relacje maja wszystkie wymagane pola"""
        relationships = self.collector.collect_relationships()
        for rel in relationships:
            self.assertIsInstance(rel.relationship_id, str)
            self.assertIsInstance(rel.source_element, str)
            self.assertIsInstance(rel.target_element, str)
            self.assertIsInstance(rel.relationship_type, str)
            self.assertTrue(len(rel.source_element) > 0)
            self.assertTrue(len(rel.target_element) > 0)
    
    # =============================================================================
    # TESTY COLLECT_METADATA
    # =============================================================================
    
    def test_collect_metadata_returns_v3metadata(self):
        """Test: collect_metadata zwraca V3Metadata"""
        metadata = self.collector.collect_metadata()
        self.assertIsInstance(metadata, V3Metadata)
        self.assertEqual(metadata.v3_version, "2.0")
        self.assertEqual(metadata.knowledge_engine_version, "1.0")
        # Metadane używają fallback gdy nie można pobrać rzeczywistych wartości
        self.assertGreaterEqual(metadata.worlds_count, 0)
        self.assertGreaterEqual(metadata.patterns_count, 0)
        self.assertGreaterEqual(metadata.relationships_count, 0)
    
    # =============================================================================
    # TESTY COLLECT_ALL
    # =============================================================================
    
    def test_collect_all_returns_v3data_package(self):
        """Test: collect_all zwraca V3DataPackage"""
        package = self.collector.collect_all()
        self.assertIsInstance(package, V3DataPackage)
    
    def test_collect_all_package_has_all_components(self):
        """Test: Pakiet ma wszystkie komponenty"""
        package = self.collector.collect_all()
        
        # Sprawdzamy czy pakiet ma wszystkie pola
        self.assertIsInstance(package.timestamp, datetime)
        self.assertIsInstance(package.worlds, list)
        self.assertIsInstance(package.patterns, list)
        self.assertIsInstance(package.relationships, list)
        self.assertIsInstance(package.metadata, V3Metadata)
        self.assertIsInstance(package.status, DataStatus)
    
    def test_collect_all_worlds_not_empty(self):
        """Test: Pakiet ma niepusta liste swiatow"""
        package = self.collector.collect_all()
        self.assertGreater(len(package.worlds), 0)
    
    def test_collect_all_patterns_not_empty(self):
        """Test: Pakiet ma niepusta liste wzorców"""
        package = self.collector.collect_all()
        self.assertGreater(len(package.patterns), 0)
    
    def test_collect_all_relationships_not_empty(self):
        """Test: Pakiet ma niepusta liste relacji"""
        package = self.collector.collect_all()
        self.assertGreater(len(package.relationships), 0)
    
    def test_collect_all_metadata_not_none(self):
        """Test: Pakiet ma metadane"""
        package = self.collector.collect_all()
        self.assertIsNotNone(package.metadata)
    
    # =============================================================================
    # TESTY KONWERSJI DO SLOWNIKA
    # =============================================================================
    
    def test_v3data_package_to_dict(self):
        """Test: V3DataPackage moze byc konwertowany do slownika"""
        package = self.collector.collect_all()
        result = package.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertIn("timestamp", result)
        self.assertIn("worlds", result)
        self.assertIn("patterns", result)
        self.assertIn("relationships", result)
        self.assertIn("metadata", result)
        self.assertIn("status", result)
    
    def test_v3data_package_to_json(self):
        """Test: V3DataPackage moze byc konwertowany do JSON"""
        package = self.collector.collect_all()
        json_str = package.to_json()
        
        self.assertIsInstance(json_str, str)
        self.assertTrue(len(json_str) > 0)
    
    # =============================================================================
    # TESTY SERIALIZACJI/DESERIALIZACJI
    # =============================================================================
    
    def test_world_info_to_dict_and_back(self):
        """Test: WorldInfo serialization/deserialization"""
        original = WorldInfo(
            world_name="test_world",
            world_type="test_type",
            status="active",
            version="1.0",
            description="Test world"
        )
        
        data = original.to_dict()
        restored = WorldInfo.from_dict(data)
        
        self.assertEqual(original.world_name, restored.world_name)
        self.assertEqual(original.world_type, restored.world_type)
        self.assertEqual(original.status, restored.status)
    
    def test_pattern_info_to_dict_and_back(self):
        """Test: PatternInfo serialization/deserialization"""
        original = PatternInfo(
            pattern_name="test_pattern",
            pattern_type="test_type",
            confidence=0.85,
            frequency=0.3
        )
        
        data = original.to_dict()
        restored = PatternInfo.from_dict(data)
        
        self.assertEqual(original.pattern_name, restored.pattern_name)
        self.assertEqual(original.pattern_type, restored.pattern_type)
        self.assertEqual(original.confidence, restored.confidence)
    
    def test_relationship_info_to_dict_and_back(self):
        """Test: RelationshipInfo serialization/deserialization"""
        original = RelationshipInfo(
            relationship_id="test_rel",
            source_element="source",
            target_element="target",
            relationship_type="depends_on",
            strength=0.85,
            description="Test relationship"
        )
        
        data = original.to_dict()
        restored = RelationshipInfo.from_dict(data)
        
        self.assertEqual(original.relationship_id, restored.relationship_id)
        self.assertEqual(original.source_element, restored.source_element)
        self.assertEqual(original.target_element, restored.target_element)
    
    def test_v3data_package_from_dict(self):
        """Test: V3DataPackage deserialization"""
        data = {
            "timestamp": "2026-07-31T12:00:00",
            "worlds": [
                {
                    "world_name": "test_world",
                    "world_type": "test_type",
                    "status": "active",
                    "version": "1.0"
                }
            ],
            "patterns": [
                {
                    "pattern_name": "test_pattern",
                    "pattern_type": "test_type"
                }
            ],
            "relationships": [
                {
                    "relationship_id": "test_rel",
                    "source_element": "source",
                    "target_element": "target",
                    "relationship_type": "depends_on"
                }
            ],
            "metadata": {
                "v3_version": "1.0",
                "knowledge_engine_version": "1.0",
                "worlds_count": 1,
                "patterns_count": 1,
                "relationships_count": 1,
                "last_update": "2026-07-31T12:00:00",
                "collection_timestamp": "2026-07-31T12:00:00"
            }
        }
        
        package = V3DataPackage.from_dict(data)
        
        self.assertIsInstance(package, V3DataPackage)
        self.assertEqual(len(package.worlds), 1)
        self.assertEqual(package.worlds[0].world_name, "test_world")
        self.assertEqual(len(package.patterns), 1)
        self.assertEqual(len(package.relationships), 1)
        self.assertIsNotNone(package.metadata)
    
    # =============================================================================
    # TESTY Z MOCKAMI
    # =============================================================================
    
    @patch('SSI.v5.input_layer.v3_collector.V3KnowledgeCollector._get_world_manager')
    def test_collect_worlds_with_mock(self, mock_get_world_manager):
        """Test: collect_worlds z mockowanym WorldManager"""
        # Mock WorldManager
        mock_manager = Mock()
        mock_world = Mock()
        mock_world.name = "mock_world"
        mock_world.world_type = "mock_type"
        mock_world.status = "active"
        mock_world.version = "1.0"
        mock_world.description = "Mock world"
        mock_world.classification = {"category": "test"}
        mock_world.dependencies = []
        mock_world.created = datetime.now()
        
        mock_manager.get_all_worlds.return_value = [mock_world]
        mock_get_world_manager.return_value = mock_manager
        
        worlds = self.collector.collect_worlds()
        
        self.assertEqual(len(worlds), 1)
        self.assertEqual(worlds[0].world_name, "mock_world")
        self.assertEqual(worlds[0].world_type, "mock_type")
    
    @patch('SSI.v5.input_layer.v3_collector.V3KnowledgeCollector._get_memory_manager')
    def test_collect_patterns_with_mock(self, mock_get_memory_manager):
        """Test: collect_patterns z mockowanym MemoryManager"""
        # Mock MemoryManager i PatternMemory
        mock_memory_manager = Mock()
        mock_pattern_memory = Mock()
        mock_pattern = Mock()
        mock_pattern.name = "mock_pattern"
        mock_pattern.pattern_type = "mock_type"
        mock_pattern.detection_timestamp = datetime.now()
        mock_pattern.examples = []
        mock_pattern.statistics = {}
        mock_pattern.confidence = 0.9
        mock_pattern.frequency = 0.5
        
        mock_pattern_memory.get_all_patterns.return_value = [mock_pattern]
        mock_memory_manager.get_pattern_memory.return_value = mock_pattern_memory
        mock_get_memory_manager.return_value = mock_memory_manager
        
        patterns = self.collector.collect_patterns()
        
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0].pattern_name, "mock_pattern")
        self.assertEqual(patterns[0].confidence, 0.9)
    
    @patch('SSI.v5.input_layer.v3_collector.V3KnowledgeCollector._get_memory_manager')
    def test_collect_relationships_with_mock(self, mock_get_memory_manager):
        """Test: collect_relationships z mockowanym MemoryManager"""
        # Mock MemoryManager i RelationshipMemory
        mock_memory_manager = Mock()
        mock_relationship_memory = Mock()
        mock_rel = Mock()
        mock_rel.relationship_id = "mock_rel"
        mock_rel.source_element = "source"
        mock_rel.target_element = "target"
        mock_rel.relationship_type = "depends_on"
        mock_rel.strength = 0.85
        mock_rel.description = "Mock relationship"
        mock_rel.created = datetime.now()
        mock_rel.properties = {}
        
        mock_relationship_memory.get_all_relationships.return_value = [mock_rel]
        mock_memory_manager.get_relationship_memory.return_value = mock_relationship_memory
        mock_get_memory_manager.return_value = mock_memory_manager
        
        relationships = self.collector.collect_relationships()
        
        self.assertEqual(len(relationships), 1)
        self.assertEqual(relationships[0].relationship_id, "mock_rel")
        self.assertEqual(relationships[0].source_element, "source")


# =============================================================================
# TESTY INTEGRACYJNE (Smoke Tests)
# =============================================================================

class TestV3CollectorSmoke(unittest.TestCase):
    """Testy integracyjne (smoke tests)"""
    
    def test_import_v3_collector_module(self):
        """Test: Import modulu v3_collector nie rzuca bledu"""
        try:
            from SSI.v5.input_layer import v3_collector
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
            collector = V3KnowledgeCollector()
            self.assertIsInstance(collector, V3KnowledgeCollector)
        except Exception as e:
            self.fail(f"Creation error: {e}")
    
    def test_collect_all_no_error(self):
        """Test: collect_all nie rzuca bledu"""
        try:
            collector = V3KnowledgeCollector()
            package = collector.collect_all()
            self.assertIsInstance(package, V3DataPackage)
        except Exception as e:
            self.fail(f"collect_all error: {e}")


# =============================================================================
# TESTY WALIDACJI
# =============================================================================

class TestV3Validation(unittest.TestCase):
    """Testy walidacji pakietu V3"""
    
    def test_validate_v3_package_with_valid_data(self):
        """Test: Walidacja pakietu z poprawnymi danymi"""
        from SSI.v5.input_layer.data_models import validate_v3_package
        
        package = V3DataPackage()
        package.worlds = [
            WorldInfo(
                world_name="test_world",
                world_type="test_type",
                status="active",
                version="1.0"
            )
        ]
        
        result = validate_v3_package(package)
        self.assertTrue(result)
        self.assertEqual(package.status, DataStatus.VALIDATED)
    
    def test_validate_v3_package_with_empty_worlds(self):
        """Test: Walidacja pakietu z pustym światami"""
        from SSI.v5.input_layer.data_models import validate_v3_package
        
        package = V3DataPackage()
        package.worlds = []
        
        result = validate_v3_package(package)
        self.assertFalse(result)
    
    def test_get_v3_package_summary(self):
        """Test: Podsumowanie pakietu V3"""
        from SSI.v5.input_layer.data_models import get_v3_package_summary
        
        package = V3DataPackage()
        package.worlds = [
            WorldInfo(world_name="test1", world_type="type1", status="active", version="1.0"),
            WorldInfo(world_name="test2", world_type="type2", status="active", version="1.0")
        ]
        package.patterns = [
            PatternInfo(pattern_name="pattern1", pattern_type="type1")
        ]
        package.relationships = [
            RelationshipInfo(
                relationship_id="rel1",
                source_element="s1",
                target_element="t1",
                relationship_type="type1"
            )
        ]
        
        summary = get_v3_package_summary(package)
        
        self.assertEqual(summary["total_worlds"], 2)
        self.assertEqual(summary["total_patterns"], 1)
        self.assertEqual(summary["total_relationships"], 1)
        self.assertEqual(summary["status"], "raw")


# =============================================================================
# URUCHOMIENIE TESTOW
# =============================================================================

if __name__ == '__main__':
    # Uruchom testy
    unittest.main()
