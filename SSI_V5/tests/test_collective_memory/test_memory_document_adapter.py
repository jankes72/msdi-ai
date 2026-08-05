"""
SSI V5 - Testy Memory Document Adapter
ETAP: 5.4.1 - Memory Embedding Foundation

Testy jednostkowe dla MemoryDocumentAdapter.

Zakres testow:
1. Tworzenie CollectiveMemoryDocument
2. Konwersja StrategyMemoryRecord
3. Konwersja MatchResult
4. Konwersja innych typow pamieci
5. Serializacja/Deserializacja
6. Auto-detekcja typow

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

import unittest
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# Import klas do testow
from SSI_V5.memory.collective_memory.memory_document_adapter import (
    CollectiveMemoryDocument,
    MemoryDocumentAdapter
)


# =============================================================================
# MOCK KLASY DO TESTOW (symuluja istniejace typy pamieci)
# =============================================================================

@dataclass
class MockStrategyMemoryRecord:
    """Mock StrategyMemoryRecord do testow."""
    memory_id: str = "smr_test_001"
    strategy_id: str = "strategy_001"
    strategy_version: str = "1.0.0"
    strategy_definition: Dict[str, Any] = field(default_factory=dict)
    strategy_parameters: Dict[str, Any] = field(default_factory=dict)
    feature_schema: List[str] = field(default_factory=list)
    model_reference: str = "default"
    creation_time: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    EXPERIMENT_HISTORY: List[Dict[str, Any]] = field(default_factory=list)
    ranking_position: int = 1
    confidence_score: float = 0.95
    tested_variants: List[str] = field(default_factory=list)
    next_evaluation: bool = True
    status: str = "ACTIVE"


@dataclass
class MockMatchResult:
    """Mock MatchResult do testow."""
    match_id: str = "match_001"
    home_team: str = "Team A"
    away_team: str = "Team B"
    home_score: int = 2
    away_score: int = 1
    match_date: str = "2026-08-04"
    source: str = "test_source"
    statistics: Dict[str, Any] = field(default_factory=dict)
    odds: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MockTrainingMemory:
    """Mock TrainingMemory do testow."""
    session_id: str = "training_001"
    start_time: str = "2026-08-04T10:00:00"
    end_time: Optional[str] = None
    duration_seconds: float = 3600.0
    phase: str = "CONTINUOUS"
    method: str = "online_learning"
    model_name: str = "test_model"
    model_version: str = "1.0.0"
    model_parameters: Dict[str, Any] = field(default_factory=dict)
    training_data_count: int = 1000
    training_data_source: str = "test_source"
    training_data_description: str = "Test data"
    initial_metrics: Dict[str, float] = field(default_factory=dict)
    final_metrics: Dict[str, float] = field(default_factory=dict)
    improvement: Dict[str, float] = field(default_factory=dict)


# =============================================================================
# TESTY CollectiveMemoryDocument
# =============================================================================

class TestCollectiveMemoryDocument(unittest.TestCase):
    """Testy klasy CollectiveMemoryDocument."""
    
    def test_create_empty_document(self):
        """Test tworzenia pustego dokumentu."""
        doc = CollectiveMemoryDocument()
        
        self.assertIsNotNone(doc.document_id)
        self.assertEqual(doc.source_id, "")
        self.assertEqual(doc.source_type, "")
        self.assertEqual(doc.text, "")
        self.assertEqual(doc.importance, 0.5)
        self.assertEqual(doc.tags, [])
        self.assertIsInstance(doc.timestamp, datetime)
    
    def test_create_document_with_values(self):
        """Test tworzenia dokumentu z wartosciami."""
        doc = CollectiveMemoryDocument(
            source_id="test_001",
            source_type="strategy_memory",
            text="Test content",
            importance=0.8,
            tags=["test", "memory"]
        )
        
        self.assertEqual(doc.source_id, "test_001")
        self.assertEqual(doc.source_type, "strategy_memory")
        self.assertEqual(doc.text, "Test content")
        self.assertEqual(doc.importance, 0.8)
        self.assertEqual(doc.tags, ["test", "memory"])
    
    def test_document_serialization(self):
        """Test serializacji i deserializacji dokumentu."""
        original = CollectiveMemoryDocument(
            source_id="test_001",
            source_type="strategy_memory",
            text="Test content",
            importance=0.8,
            tags=["test", "memory"],
            metadata={"key": "value"}
        )
        
        # Serializacja
        doc_dict = original.to_dict()
        self.assertIsInstance(doc_dict, dict)
        self.assertEqual(doc_dict['source_id'], "test_001")
        self.assertEqual(doc_dict['text'], "Test content")
        
        # Deserializacja
        restored = CollectiveMemoryDocument.from_dict(doc_dict)
        self.assertEqual(restored.source_id, original.source_id)
        self.assertEqual(restored.source_type, original.source_type)
        self.assertEqual(restored.text, original.text)
        self.assertEqual(restored.importance, original.importance)
        self.assertEqual(restored.tags, original.tags)
    
    def test_document_json_serialization(self):
        """Test serializacji do JSON."""
        doc = CollectiveMemoryDocument(
            source_id="test_001",
            source_type="strategy_memory",
            text="Test content",
            importance=0.8,
            tags=["test", "memory"]
        )
        
        json_str = doc.to_json()
        self.assertIsInstance(json_str, str)
        
        # Deserializacja
        restored = CollectiveMemoryDocument.from_json(json_str)
        self.assertEqual(restored.source_id, doc.source_id)
        self.assertEqual(restored.text, doc.text)


# =============================================================================
# TESTY MemoryDocumentAdapter
# =============================================================================

class TestMemoryDocumentAdapter(unittest.TestCase):
    """Testy klasy MemoryDocumentAdapter."""
    
    def setUp(self):
        """Inicjalizacja adaptera."""
        self.adapter = MemoryDocumentAdapter()
    
    def test_adapter_initialization(self):
        """Test inicjalizacji adaptera."""
        adapter = MemoryDocumentAdapter()
        self.assertIsNotNone(adapter)
    
    def test_get_supported_types(self):
        """Test pobierania obslugiwanych typow."""
        supported = self.adapter.get_supported_types()
        
        self.assertIsInstance(supported, list)
        self.assertIn('StrategyMemoryRecord', supported)
        self.assertIn('MatchResult', supported)
        self.assertIn('TrainingMemory', supported)
        self.assertIn('ObservationMemory', supported)
        self.assertIn('BehaviorMemory', supported)
    
    # ========================================================================
    # TESTY ADAPTERA DLA StrategyMemoryRecord
    # ========================================================================
    
    def test_adapt_strategy_memory_basic(self):
        """Test adaptacji podstawowego StrategyMemoryRecord."""
        record = MockStrategyMemoryRecord(
            strategy_id="strategy_001",
            strategy_version="1.0.0",
            status="ACTIVE"
        )
        
        doc = self.adapter.adapt_strategy_memory(record)
        
        self.assertIsNotNone(doc)
        self.assertEqual(doc.source_type, "strategy_memory")
        self.assertEqual(doc.source_id, "strategy_001")
        self.assertIn("STRATEGY: strategy_001", doc.text)
        self.assertIn("Version: 1.0.0", doc.text)
        self.assertIn("Status: ACTIVE", doc.text)
        self.assertEqual(doc.importance, 0.95)
        self.assertIn("strategy", doc.tags)
        self.assertIn("memory", doc.tags)
    
    def test_adapt_strategy_memory_with_definition(self):
        """Test adaptacji StrategyMemoryRecord z definicja."""
        record = MockStrategyMemoryRecord(
            strategy_id="strategy_002",
            strategy_version="2.0.0",
            strategy_definition={"type": "exact_score", "target": "high_probability"},
            ranking_position=1,
            confidence_score=0.95
        )
        
        doc = self.adapter.adapt_strategy_memory(record)
        
        self.assertIn("Definition:", doc.text)
        self.assertIn("Ranking: 1", doc.text)
        self.assertIn("Confidence: 0.950", doc.text)
        self.assertIn("status:active", doc.tags)
    
    def test_adapt_strategy_memory_with_experiments(self):
        """Test adaptacji StrategyMemoryRecord z historia eksperymentow."""
        record = MockStrategyMemoryRecord(
            strategy_id="strategy_003",
            EXPERIMENT_HISTORY=[
                {"experiment_id": "exp_001", "result": {"accuracy": 0.85}}
            ]
        )
        
        doc = self.adapter.adapt_strategy_memory(record)
        
        self.assertIn("Experiments: 1", doc.text)
        self.assertIn("Last Experiment Result:", doc.text)
    
    # ========================================================================
    # TESTY ADAPTERA DLA MatchResult
    # ========================================================================
    
    def test_adapt_match_result_basic(self):
        """Test adaptacji podstawowego MatchResult."""
        record = MockMatchResult(
            match_id="match_001",
            home_team="Team A",
            away_team="Team B",
            home_score=2,
            away_score=1
        )
        
        doc = self.adapter.adapt_match_result(record)
        
        self.assertIsNotNone(doc)
        self.assertEqual(doc.source_type, "match_result")
        self.assertEqual(doc.source_id, "match_001")
        self.assertIn("MATCH: Team A vs Team B", doc.text)
        self.assertIn("Result: 2-1", doc.text)
        self.assertIn("Outcome: HOME WIN", doc.text)
        self.assertEqual(doc.importance, 0.7)
        self.assertIn("match", doc.tags)
        self.assertIn("result", doc.tags)
        self.assertIn("memory", doc.tags)
        self.assertIn("outcome:home win", doc.tags)
    
    def test_adapt_match_result_draw(self):
        """Test adaptacji MatchResult z remisem."""
        record = MockMatchResult(
            match_id="match_002",
            home_team="Team C",
            away_team="Team D",
            home_score=1,
            away_score=1
        )
        
        doc = self.adapter.adapt_match_result(record)
        
        self.assertIn("Outcome: DRAW", doc.text)
        self.assertIn("outcome:draw", doc.tags)
    
    def test_adapt_match_result_with_statistics(self):
        """Test adaptacji MatchResult ze statystykami."""
        record = MockMatchResult(
            match_id="match_003",
            home_team="Team E",
            away_team="Team F",
            home_score=3,
            away_score=0,
            statistics={"shots": 15, "possession": 65}
        )
        
        doc = self.adapter.adapt_match_result(record)
        
        self.assertIn("Statistics:", doc.text)
        self.assertIn("shots", doc.text)
    
    # ========================================================================
    # TESTY ADAPTERA DLA TrainingMemory
    # ========================================================================
    
    def test_adapt_training_memory_basic(self):
        """Test adaptacji podstawowego TrainingMemory."""
        record = MockTrainingMemory(
            session_id="training_001",
            model_name="test_model",
            model_version="1.0.0",
            training_data_count=1000
        )
        
        doc = self.adapter.adapt_training_memory(record)
        
        self.assertIsNotNone(doc)
        self.assertEqual(doc.source_type, "training_memory")
        self.assertEqual(doc.source_id, "training_001")
        self.assertIn("TRAINING SESSION: training_001", doc.text)
        self.assertIn("Model: test_model v1.0.0", doc.text)
        self.assertIn("Data Count: 1000", doc.text)
        self.assertIn("training", doc.tags)
        self.assertIn("memory", doc.tags)
        self.assertIn("learning", doc.tags)
        # Importance powinien byc zwiazany z data_count
        self.assertEqual(doc.importance, 1.0)  # 1000/1000 = 1.0
    
    def test_adapt_training_memory_with_metrics(self):
        """Test adaptacji TrainingMemory z metrykami."""
        record = MockTrainingMemory(
            session_id="training_002",
            final_metrics={"accuracy": 0.95, "loss": 0.05},
            improvement={"accuracy": 0.10}
        )
        
        doc = self.adapter.adapt_training_memory(record)
        
        self.assertIn("Final Metrics:", doc.text)
        self.assertIn("Improvement:", doc.text)
    
    # ========================================================================
    # TESTY AUTO-DETEKCJI
    # ========================================================================
    
    def test_adapt_any_strategy_memory(self):
        """Test auto-detekcji StrategyMemoryRecord."""
        record = MockStrategyMemoryRecord(
            strategy_id="strategy_auto",
            confidence_score=0.8
        )
        
        doc = self.adapter.adapt_any(record)
        
        self.assertIsNotNone(doc)
        self.assertEqual(doc.source_type, "strategy_memory")
        self.assertEqual(doc.source_id, "strategy_auto")
    
    def test_adapt_any_match_result(self):
        """Test auto-detekcji MatchResult."""
        record = MockMatchResult(
            match_id="match_auto",
            home_team="Team X",
            away_team="Team Y",
            home_score=2,
            away_score=0
        )
        
        doc = self.adapter.adapt_any(record)
        
        self.assertIsNotNone(doc)
        self.assertEqual(doc.source_type, "match_result")
    
    def test_adapt_any_unsupported_type(self):
        """Test auto-detekcji nieobslugiwanego typu."""
        class UnsupportedMemory:
            pass
        
        record = UnsupportedMemory()
        doc = self.adapter.adapt_any(record)
        
        self.assertIsNone(doc)


# =============================================================================
# TESTY METADANYCH I TIMINGU
# =============================================================================

class TestMetadataAndTiming(unittest.TestCase):
    """Testy metadanych i timestampow."""
    
    def setUp(self):
        self.adapter = MemoryDocumentAdapter()
    
    def test_document_has_timestamp(self):
        """Test czy dokument ma timestamp."""
        record = MockStrategyMemoryRecord(strategy_id="test_001")
        doc = self.adapter.adapt_strategy_memory(record)
        
        self.assertIsInstance(doc.timestamp, datetime)
    
    def test_document_metadata_includes_strategy_info(self):
        """Test czy metadane zawieraja informacje o strategii."""
        record = MockStrategyMemoryRecord(
            strategy_id="test_001",
            strategy_version="1.0.0",
            ranking_position=1,
            confidence_score=0.95,
            status="ACTIVE"
        )
        
        doc = self.adapter.adapt_strategy_memory(record)
        
        self.assertEqual(doc.metadata['strategy_id'], "test_001")
        self.assertEqual(doc.metadata['strategy_version'], "1.0.0")
        self.assertEqual(doc.metadata['ranking_position'], 1)
        self.assertEqual(doc.metadata['confidence_score'], 0.95)
        self.assertEqual(doc.metadata['status'], "ACTIVE")
    
    def test_importance_calculation(self):
        """Test obliczania importance."""
        # Wysoki confidence = wysoka importance
        record1 = MockStrategyMemoryRecord(
            strategy_id="high_conf",
            confidence_score=0.95
        )
        doc1 = self.adapter.adapt_strategy_memory(record1)
        self.assertEqual(doc1.importance, 0.95)
        
        # Niski confidence = domyslne 0.5
        record2 = MockStrategyMemoryRecord(
            strategy_id="low_conf",
            confidence_score=0.0
        )
        doc2 = self.adapter.adapt_strategy_memory(record2)
        self.assertEqual(doc2.importance, 0.5)  # Fallback


# =============================================================================
# RUNNER
# =============================================================================

if __name__ == '__main__':
    unittest.main()
