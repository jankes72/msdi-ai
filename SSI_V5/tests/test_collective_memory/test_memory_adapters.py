"""
SSI V5 - Testy Memory Adapters
ETAP: 5.4.2.1 - CollectiveMemoryDocument Pipeline

Testy jednostkowe dla warstwy adapterow pamieci.

 Zakres testow:
1. BaseMemoryAdapter kontrakt
2. Kazdy adapter (Strategy, MatchResult, Training, etc.)
3. MemoryDocumentAdapter jako router
4. Konwersja do CollectiveMemoryDocument
5. Auto-detekcja typow
6. Rejestracja nowych adapterow

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

import unittest
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum, auto

from SSI_V5.memory.collective_memory.memory_document import CollectiveMemoryDocument
from SSI_V5.memory.collective_memory.memory_document_adapter_v2 import MemoryDocumentAdapter
from SSI_V5.memory.collective_memory.adapters import (
    BaseMemoryAdapter,
    StrategyMemoryAdapter,
    MatchResultAdapter,
    TrainingMemoryAdapter,
    ObservationMemoryAdapter,
    BehaviorMemoryAdapter,
    AgentAnalysisMemoryAdapter,
    DecisionMemoryAdapter,
    find_adapter_for,
    get_adapter_registry,
)


# =============================================================================
# FIKTURY - Klasy pamieci do testow
# =============================================================================

class TrainingPhase(Enum):
    INITIAL = auto()
    CONTINUOUS = auto()
    FINE_TUNING = auto()


class ObservationScope(Enum):
    SYSTEM = auto()
    AGENT = auto()
    GROUP = auto()


class BehaviorType(Enum):
    DECISION = auto()
    ANALYSIS = auto()
    CREATIVE = auto()
    SOCIAL = auto()
    LEARNING = auto()


class AnalysisType(Enum):
    PERFORMANCE = auto()
    BEHAVIOR = auto()
    STRATEGY = auto()
    COLLABORATION = auto()
    EVOLUTION = auto()


@dataclass
class StrategyMemoryRecord:
    """Testowa klasa StrategyMemoryRecord"""
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
    PREDICTION_HISTORY: List[Dict[str, Any]] = field(default_factory=list)
    RESULT_HISTORY: List[Dict[str, Any]] = field(default_factory=list)
    REPUTATION_HISTORY: List[Dict[str, Any]] = field(default_factory=list)
    EVOLUTION_HISTORY: List[Dict[str, Any]] = field(default_factory=list)
    ranking_position: int = 0
    confidence_score: float = 0.0
    tested_variants: List[str] = field(default_factory=list)
    next_evaluation: bool = True
    status: str = "ACTIVE"


@dataclass
class MatchResult:
    """Testowa klasa MatchResult"""
    match_id: str = "match_001"
    home_team: str = "Liverpool"
    away_team: str = "Arsenal"
    home_goals: int = 2
    away_goals: int = 1
    source: str = "premier_league"
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrainingMemory:
    """Testowa klasa TrainingMemory"""
    session_id: str = "session_001"
    start_time: str = "2026-01-01T00:00:00"
    end_time: Optional[str] = None
    duration_seconds: float = 3600.0
    phase: TrainingPhase = TrainingPhase.CONTINUOUS
    method: str = "online_learning"
    training_data_count: int = 1000
    training_data_source: str = "historical_data"
    training_data_description: str = "Test data"
    model_name: str = "model_v1"
    model_version: str = "1.0.0"
    model_parameters: Dict[str, Any] = field(default_factory=dict)
    initial_metrics: Dict[str, float] = field(default_factory=dict)
    final_metrics: Dict[str, float] = field(default_factory=dict)
    improvement: Dict[str, float] = field(default_factory=dict)
    success_rate: float = 0.95
    convergence_rate: float = 0.98
    validation_score: float = 0.92
    context: Dict[str, Any] = field(default_factory=dict)
    notes: str = "Test training"
    created_at: str = "2026-01-01T00:00:00"
    updated_at: str = "2026-01-01T00:00:00"


@dataclass
class ObservationMemory:
    """Testowa klasa ObservationMemory"""
    observation_id: str = "obs_001"
    scope: ObservationScope = ObservationScope.SYSTEM
    start_time: str = "2026-01-01T00:00:00"
    end_time: Optional[str] = None
    description: str = "System observation"
    observation_data: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: str = "2026-01-01T00:00:00"
    updated_at: str = "2026-01-01T00:00:00"


@dataclass
class BehaviorMemory:
    """Testowa klasa BehaviorMemory"""
    behavior_id: str = "beh_001"
    behavior_type: BehaviorType = BehaviorType.DECISION
    description: str = "Decision behavior"
    actions: List[str] = field(default_factory=list)
    outcome: str = "SUCCESS"
    metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: str = "2026-01-01T00:00:00"
    updated_at: str = "2026-01-01T00:00:00"


@dataclass
class AgentAnalysisMemory:
    """Testowa klasa AgentAnalysisMemory"""
    analysis_id: str = "analysis_001"
    analysis_type: AnalysisType = AnalysisType.PERFORMANCE
    agent_id: str = "agent_001"
    target_id: str = "target_001"
    findings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    created_at: str = "2026-01-01T00:00:00"
    updated_at: str = "2026-01-01T00:00:00"


@dataclass
class DecisionMemory:
    """Testowa klasa DecisionMemory"""
    decision_id: str = "decision_001"
    decision_type: str = "strategic"
    context: Dict[str, Any] = field(default_factory=dict)
    options: List[str] = field(default_factory=list)
    selected_option: str = "option_1"
    decision_outcome: str = "SUCCESS"
    rationale: str = "Best option selected"
    metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: str = "2026-01-01T00:00:00"
    updated_at: str = "2026-01-01T00:00:00"


# =============================================================================
# TESTY
# =============================================================================

class TestBaseMemoryAdapter(unittest.TestCase):
    """Testy bazowego kontraktu adaptera."""
    
    def test_contract_methods(self):
        """Test czy BaseMemoryAdapter ma wymagane metody abstraktcyjne."""
        adapter = StrategyMemoryAdapter()  # konkretna implementacja
        
        # Sprawdź wymagane metody
        self.assertTrue(hasattr(adapter, 'can_handle'))
        self.assertTrue(hasattr(adapter, 'convert'))
        self.assertTrue(hasattr(adapter, 'get_source_type'))
        self.assertTrue(hasattr(adapter, 'get_priority'))
        self.assertTrue(hasattr(adapter, 'create_document'))
    
    def test_source_type_defined(self):
        """Test czy adaptery maja zdefiniowany source_type."""
        adapters = [
            StrategyMemoryAdapter(),
            MatchResultAdapter(),
            TrainingMemoryAdapter(),
            ObservationMemoryAdapter(),
            BehaviorMemoryAdapter(),
            AgentAnalysisMemoryAdapter(),
            DecisionMemoryAdapter(),
        ]
        
        for adapter in adapters:
            self.assertTrue(adapter.get_source_type())
            self.assertIsInstance(adapter.get_source_type(), str)
    
    def test_priority_defined(self):
        """Test czy adaptery maja zdefiniowany priorytet."""
        adapters = [
            StrategyMemoryAdapter(),
            MatchResultAdapter(),
            TrainingMemoryAdapter(),
            ObservationMemoryAdapter(),
            BehaviorMemoryAdapter(),
            AgentAnalysisMemoryAdapter(),
            DecisionMemoryAdapter(),
        ]
        
        for adapter in adapters:
            self.assertTrue(adapter.get_priority() >= 0)


class TestAdapterRegistry(unittest.TestCase):
    """Testy rejestru adapterow."""
    
    def test_registry_has_all_adapters(self):
        """Test czy rejestr zawiera wszystkie adaptery."""
        registry = get_adapter_registry()
        expected_types = [
            'strategy_memory',
            'match_result',
            'training_memory',
            'observation_memory',
            'behavior_memory',
            'agent_analysis_memory',
            'decision_memory',
        ]
        
        registered_types = [a.get_source_type() for a in registry]
        for expected_type in expected_types:
            self.assertIn(expected_type, registered_types)
    
    def test_find_adapter_for(self):
        """Test znajdowania adaptera dla obiektu."""
        # Test StrategyMemoryRecord
        strategy = StrategyMemoryRecord()
        adapter = find_adapter_for(strategy)
        self.assertIsNotNone(adapter)
        self.assertIsInstance(adapter, StrategyMemoryAdapter)
        
        # Test MatchResult
        match = MatchResult()
        adapter = find_adapter_for(match)
        self.assertIsNotNone(adapter)
        self.assertIsInstance(adapter, MatchResultAdapter)
        
        # Test nieznany typ
        unknown = object()
        adapter = find_adapter_for(unknown)
        self.assertIsNone(adapter)


class TestStrategyMemoryAdapter(unittest.TestCase):
    """Testy StrategyMemoryAdapter."""
    
    def test_can_handle(self):
        """Test can_handle dla StrategyMemoryRecord."""
        adapter = StrategyMemoryAdapter()
        record = StrategyMemoryRecord()
        
        self.assertTrue(adapter.can_handle(record))
        self.assertFalse(adapter.can_handle(MatchResult()))
    
    def test_convert(self):
        """Test konwersji StrategyMemoryRecord."""
        adapter = StrategyMemoryAdapter()
        record = StrategyMemoryRecord(
            strategy_id="test_strategy",
            strategy_version="2.0.0",
            confidence_score=0.85,
            status="ACTIVE"
        )
        
        doc = adapter.convert(record)
        
        self.assertIsInstance(doc, CollectiveMemoryDocument)
        self.assertEqual(doc.source_type, "strategy_memory")
        self.assertEqual(doc.source_id, record.memory_id)
        self.assertIn("test_strategy", doc.text)
        self.assertIn("2.0.0", doc.text)
        self.assertGreater(doc.importance, 0.5)  # Powinien miec wyzsza waznosc
        self.assertIn("strategy:test_strategy", doc.tags)
    
    def test_metadata_preserved(self):
        """Test czy metadane sa zachowane."""
        adapter = StrategyMemoryAdapter()
        record = StrategyMemoryRecord(
            strategy_id="test_strategy",
            confidence_score=0.78,
            ranking_position=5
        )
        
        doc = adapter.convert(record)
        
        self.assertIn("strategy_id", doc.metadata)
        self.assertEqual(doc.metadata["strategy_id"], "test_strategy")
        self.assertEqual(doc.metadata["confidence_score"], 0.78)
        self.assertEqual(doc.metadata["ranking_position"], 5)


class TestMatchResultAdapter(unittest.TestCase):
    """Testy MatchResultAdapter."""
    
    def test_can_handle(self):
        """Test can_handle dla MatchResult."""
        adapter = MatchResultAdapter()
        result = MatchResult()
        
        self.assertTrue(adapter.can_handle(result))
        self.assertFalse(adapter.can_handle(StrategyMemoryRecord()))
    
    def test_convert(self):
        """Test konwersji MatchResult."""
        adapter = MatchResultAdapter()
        result = MatchResult(
            match_id="test_match",
            home_team="TeamA",
            away_team="TeamB",
            home_goals=3,
            away_goals=1
        )
        
        doc = adapter.convert(result)
        
        self.assertIsInstance(doc, CollectiveMemoryDocument)
        self.assertEqual(doc.source_type, "match_result")
        self.assertEqual(doc.source_id, result.match_id)
        self.assertIn("TeamA", doc.text)
        self.assertIn("TeamB", doc.text)
        self.assertIn("3-1", doc.text)
        self.assertIn("HOME_WIN", doc.metadata["result"])
    
    def test_tags_generated(self):
        """Test generowania tagow."""
        adapter = MatchResultAdapter()
        result = MatchResult(
            home_team="Liverpool",
            away_team="Arsenal",
            home_goals=2,
            away_goals=1
        )
        
        doc = adapter.convert(result)
        
        self.assertIn("team:liverpool", doc.tags)
        self.assertIn("team:arsenal", doc.tags)
        self.assertIn("result:home_win", doc.tags)


class TestTrainingMemoryAdapter(unittest.TestCase):
    """Testy TrainingMemoryAdapter."""
    
    def test_can_handle(self):
        """Test can_handle dla TrainingMemory."""
        adapter = TrainingMemoryAdapter()
        memory = TrainingMemory()
        
        self.assertTrue(adapter.can_handle(memory))
        self.assertFalse(adapter.can_handle(StrategyMemoryRecord()))
    
    def test_convert(self):
        """Test konwersji TrainingMemory."""
        adapter = TrainingMemoryAdapter()
        memory = TrainingMemory(
            session_id="session_001",
            validation_score=0.95,
            method="online_learning"
        )
        
        doc = adapter.convert(memory)
        
        self.assertIsInstance(doc, CollectiveMemoryDocument)
        self.assertEqual(doc.source_type, "training_memory")
        self.assertEqual(doc.source_id, memory.session_id)
        self.assertIn("session_001", doc.text)
        self.assertGreater(doc.importance, 0.7)  # Wysoka waznosc dla dobrego validation score


class TestObservationMemoryAdapter(unittest.TestCase):
    """Testy ObservationMemoryAdapter."""
    
    def test_can_handle(self):
        """Test can_handle dla ObservationMemory."""
        adapter = ObservationMemoryAdapter()
        memory = ObservationMemory()
        
        self.assertTrue(adapter.can_handle(memory))
    
    def test_convert(self):
        """Test konwersji ObservationMemory."""
        adapter = ObservationMemoryAdapter()
        memory = ObservationMemory(
            observation_id="obs_001",
            scope=ObservationScope.SYSTEM
        )
        
        doc = adapter.convert(memory)
        
        self.assertIsInstance(doc, CollectiveMemoryDocument)
        self.assertEqual(doc.source_type, "observation_memory")
        self.assertEqual(doc.source_id, memory.observation_id)
        self.assertIn("System observation", doc.text)


class TestBehaviorMemoryAdapter(unittest.TestCase):
    """Testy BehaviorMemoryAdapter."""
    
    def test_can_handle(self):
        """Test can_handle dla BehaviorMemory."""
        adapter = BehaviorMemoryAdapter()
        memory = BehaviorMemory()
        
        self.assertTrue(adapter.can_handle(memory))
    
    def test_convert(self):
        """Test konwersji BehaviorMemory."""
        adapter = BehaviorMemoryAdapter()
        memory = BehaviorMemory(
            behavior_id="beh_001",
            behavior_type=BehaviorType.DECISION,
            outcome="SUCCESS"
        )
        
        doc = adapter.convert(memory)
        
        self.assertIsInstance(doc, CollectiveMemoryDocument)
        self.assertEqual(doc.source_type, "behavior_memory")
        self.assertEqual(doc.source_id, memory.behavior_id)
        self.assertGreater(doc.importance, 0.6)  # Wysoka waznosc dla DECISION + SUCCESS


class TestAgentAnalysisMemoryAdapter(unittest.TestCase):
    """Testy AgentAnalysisMemoryAdapter."""
    
    def test_can_handle(self):
        """Test can_handle dla AgentAnalysisMemory."""
        adapter = AgentAnalysisMemoryAdapter()
        memory = AgentAnalysisMemory()
        
        self.assertTrue(adapter.can_handle(memory))
    
    def test_convert(self):
        """Test konwersji AgentAnalysisMemory."""
        adapter = AgentAnalysisMemoryAdapter()
        memory = AgentAnalysisMemory(
            analysis_id="analysis_001",
            analysis_type=AnalysisType.EVOLUTION
        )
        
        doc = adapter.convert(memory)
        
        self.assertIsInstance(doc, CollectiveMemoryDocument)
        self.assertEqual(doc.source_type, "agent_analysis_memory")
        self.assertEqual(doc.source_id, memory.analysis_id)
        self.assertGreater(doc.importance, 0.7)  # Wysoka waznosc dla EVOLUTION


class TestDecisionMemoryAdapter(unittest.TestCase):
    """Testy DecisionMemoryAdapter."""
    
    def test_can_handle(self):
        """Test can_handle dla DecisionMemory."""
        adapter = DecisionMemoryAdapter()
        memory = DecisionMemory()
        
        self.assertTrue(adapter.can_handle(memory))
    
    def test_convert(self):
        """Test konwersji DecisionMemory."""
        adapter = DecisionMemoryAdapter()
        memory = DecisionMemory(
            decision_id="decision_001",
            decision_outcome="SUCCESS",
            selected_option="option_1"
        )
        
        doc = adapter.convert(memory)
        
        self.assertIsInstance(doc, CollectiveMemoryDocument)
        self.assertEqual(doc.source_type, "decision_memory")
        self.assertEqual(doc.source_id, memory.decision_id)
        self.assertIn("SUCCESS", doc.text)


class TestMemoryDocumentAdapter(unittest.TestCase):
    """Testy MemoryDocumentAdapter jako router."""
    
    def setUp(self):
        """Inicjalizacja adaptera."""
        self.adapter = MemoryDocumentAdapter()
    
    def test_convert_auto_detection(self):
        """Test auto-detekcji typu."""
        # Test StrategyMemory
        strategy = StrategyMemoryRecord(strategy_id="str_001")
        doc1 = self.adapter.convert(strategy)
        self.assertIsNotNone(doc1)
        self.assertEqual(doc1.source_type, "strategy_memory")
        
        # Test MatchResult
        match = MatchResult(home_team="TeamA", away_team="TeamB")
        doc2 = self.adapter.convert(match)
        self.assertIsNotNone(doc2)
        self.assertEqual(doc2.source_type, "match_result")
    
    def test_convert_unknown_type(self):
        """Test konwersji nieznanego typu."""
        unknown = object()
        doc = self.adapter.convert(unknown)
        self.assertIsNone(doc)
    
    def test_get_adapter(self):
        """Test get_adapter."""
        strategy = StrategyMemoryRecord()
        adapter = self.adapter.get_adapter(strategy)
        self.assertIsNotNone(adapter)
        self.assertIsInstance(adapter, StrategyMemoryAdapter)
    
    def test_get_supported_types(self):
        """Test get_supported_types."""
        types = self.adapter.get_supported_types()
        
        self.assertIsInstance(types, list)
        self.assertIn("strategy_memory", types)
        self.assertIn("match_result", types)
        self.assertIn("training_memory", types)
        self.assertIn("observation_memory", types)
        self.assertIn("behavior_memory", types)
        self.assertIn("agent_analysis_memory", types)
        self.assertIn("decision_memory", types)
    
    def test_register_custom_adapter(self):
        """Test rejestracji custom adaptera."""
        # Stworz custom adapter
        class CustomAdapter(BaseMemoryAdapter):
            source_type = "custom_memory"
            priority = 200
            
            def can_handle(self, obj: Any) -> bool:
                return type(obj).__name__ == 'CustomMemory'
            
            def convert(self, obj: Any) -> CollectiveMemoryDocument:
                return self.create_document(
                    source_id="custom_001",
                    text="Custom memory",
                    source_type=self.source_type
                )
        
        # Zarejestruj
        self.adapter.register_adapter(CustomAdapter())
        
        # Sprawdz czy jest w supported types
        types = self.adapter.get_supported_types()
        self.assertIn("custom_memory", types)


class TestCollectiveMemoryDocument(unittest.TestCase):
    """Testy CollectiveMemoryDocument."""
    
    def test_serialization(self):
        """Test serializacji/deserializacji."""
        doc = CollectiveMemoryDocument(
            source_id="test_001",
            source_type="test_type",
            text="Test document",
            importance=0.8,
            tags=["tag1", "tag2"]
        )
        
        # to_dict
        data = doc.to_dict()
        self.assertIn("source_id", data)
        self.assertEqual(data["source_id"], "test_001")
        
        # from_dict
        restored = CollectiveMemoryDocument.from_dict(data)
        self.assertEqual(restored.source_id, doc.source_id)
        self.assertEqual(restored.source_type, doc.source_type)
        self.assertEqual(restored.text, doc.text)
    
    def test_json_serialization(self):
        """Test serializacji JSON."""
        doc = CollectiveMemoryDocument(
            source_id="test_001",
            source_type="test_type",
            text="Test document"
        )
        
        # to_json
        json_str = doc.to_json()
        self.assertIsInstance(json_str, str)
        
        # from_json
        restored = CollectiveMemoryDocument.from_json(json_str)
        self.assertEqual(restored.source_id, doc.source_id)


# =============================================================================
# RUNNER
# =============================================================================

if __name__ == '__main__':
    unittest.main()
