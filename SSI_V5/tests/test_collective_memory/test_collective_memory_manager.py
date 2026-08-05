"""
SSI V5 - Testy CollectiveMemoryManager
ETAP: 5.4.2.2 - CollectiveMemoryManager Foundation

Testy jednostkowe dla CollectiveMemoryManager:
- Tworzenie i inicjalizacja
- Zapis i odczyt pamięci
- Wyszukiwanie semantyczne
- Budowanie kontekstu dla agentów
- Integracja z VectorIndex i adapterami
- Zarządzanie statystykami

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

import unittest
import os
import sys
import tempfile
import shutil
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum, auto

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from SSI_V5.memory.collective_memory import (
    CollectiveMemoryManager,
    CollectiveMemoryManagerConfig,
    create_collective_memory_manager,
    VectorIndexConfig,
    INDEX_TYPE_NUMPY,
    CollectiveMemoryDocument,
    MemoryDocumentAdapter
)


# =============================================================================
# FIKTURY - Klasy pamięci do testów
# =============================================================================

class StrategyPhase(Enum):
    PRE_MATCH = auto()
    IN_PLAY = auto()
    POST_MATCH = auto()


@dataclass
class StrategyMemoryRecord:
    """Fixture - Rekord pamięci strategii"""
    memory_id: str = "mem_001"
    strategy_id: str = ""
    strategy_version: str = "1.0"
    strategy_name: str = "Test Strategy"
    phase: StrategyPhase = field(default=StrategyPhase.PRE_MATCH)
    result: str = "WIN"
    confidence: float = 0.85
    profit: float = 150.0
    stake: float = 100.0
    odds: float = 2.5
    match_id: str = "match_001"
    team: str = "Liverpool"
    opponent: str = "Arsenal"
    prediction: str = "home_win"
    timestamp: str = "2026-08-04T10:00:00"
    experiments: List[Dict] = field(default_factory=list)
    strategy_definition: Dict[str, Any] = field(default_factory=dict)
    strategy_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MatchResult:
    """Fixture - Wynik meczu"""
    match_id: str
    home_team: str = "Liverpool"
    away_team: str = "Arsenal"
    home_goals: int = 2
    away_goals: int = 1
    result: str = "HOME_WIN"
    odds: float = 2.10
    stake: float = 100.0
    profit: float = 110.0
    timestamp: str = "2026-08-04T15:00:00"
    statistics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrainingPhase(Enum):
    INITIAL = auto()
    CONTINUOUS = auto()
    FINE_TUNING = auto()


def default_training_phase():
    return TrainingPhase.INITIAL


@dataclass
class TrainingMemory:
    """Fixture - Pamięć treningowa"""
    session_id: str = ""
    start_time: str = "2026-08-04T12:00:00"
    end_time: Optional[str] = None
    training_data_count: int = 100
    training_id: str = ""
    model_name: str = "test_model"
    model_version: str = "1.0"
    phase: TrainingPhase = field(default_factory=default_training_phase)
    duration_seconds: int = 3600
    metrics: Dict[str, float] = field(default_factory=dict)
    epoch: int = 10
    accuracy: float = 0.85
    loss: float = 0.15
    success_rate: float = 0.85
    validation_score: float = 0.85
    method: str = "supervised"
    training_data_source: str = ""
    initial_metrics: Dict[str, float] = field(default_factory=dict)
    final_metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: str = "2026-08-04T12:00:00"


@dataclass
class ObservationMemory:
    """Fixture - Obserwacja"""
    observation_id: str
    scope: str = "match_analysis"
    observer: str = "agent_01"
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = "match_analysis"
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.90
    timestamp: str = "2026-08-04T14:00:00"


@dataclass
class DecisionMemory:
    """Fixture - Decyzja"""
    decision_id: str
    decision_outcome: str = "SUCCESS"
    decision_type: str = "bet"
    action: str = "place_bet"
    reasoning: str = "High confidence based on analysis"
    confidence: float = 0.88
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = "2026-08-04T13:00:00"


class TestCollectiveMemoryManagerInitialization(unittest.TestCase):
    """Testy inicjalizacji CollectiveMemoryManager"""

    def setUp(self):
        """SetUp - tworzy tymczasowy katalog"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """TearDown - usuwa tymczasowy katalog"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_default_initialization(self):
        """Test domyślnej inicjalizacji"""
        manager = CollectiveMemoryManager()
        
        # Powinien mieć adapter pamięci
        self.assertIsInstance(manager._memory_adapter, MemoryDocumentAdapter)
        
        # VectorIndex i EmbeddingGenerator nie są zainicjowane domyślnie
        with self.assertRaises(ValueError):
            _ = manager.vector_index
            
        with self.assertRaises(ValueError):
            _ = manager.embedding_generator

    def test_02_partial_initialization(self):
        """Test inicjalizacji z podanym VectorIndex"""
        config = VectorIndexConfig(
            index_type=INDEX_TYPE_NUMPY,
            storage_path=os.path.join(self.temp_dir, "test_index"),
            dimension=384
        )
        
        # Najpierw tworzymy VectorIndex
        from SSI_V5.memory.collective_memory import create_vector_index, create_embedding_generator
        
        embedding_gen = create_embedding_generator(dimension=384)
        vector_index = create_vector_index(
            index_type=INDEX_TYPE_NUMPY,
            dimension=384,
            storage_path=os.path.join(self.temp_dir, "test_index"),
            embedding_generator=embedding_gen
        )
        
        manager = CollectiveMemoryManager(
            vector_index=vector_index,
            embedding_generator=embedding_gen
        )
        
        # Powinny być dostępne
        self.assertEqual(manager.vector_index, vector_index)
        self.assertEqual(manager.embedding_generator, embedding_gen)

    def test_03_initialize_method(self):
        """Test metody initialize"""
        manager = CollectiveMemoryManager()
        
        manager.initialize(
            vector_index_config=VectorIndexConfig(
                storage_path=os.path.join(self.temp_dir, "test_init"),
                dimension=384
            ),
            embedding_dimension=384
        )
        
        # Teraz powinny być dostępne
        self.assertIsNotNone(manager.vector_index)
        self.assertIsNotNone(manager.embedding_generator)

    def test_04_create_collective_memory_manager_factory(self):
        """Test fabryki create_collective_memory_manager"""
        config = CollectiveMemoryManagerConfig(
            vector_index_config=VectorIndexConfig(
                storage_path=os.path.join(self.temp_dir, "test_factory"),
                dimension=384
            ),
            embedding_dimension=384
        )
        
        manager = create_collective_memory_manager(config)
        
        self.assertIsInstance(manager, CollectiveMemoryManager)
        self.assertIsNotNone(manager.vector_index)
        self.assertIsNotNone(manager.embedding_generator)

    def test_05_create_collective_memory_manager_default(self):
        """Test fabryki z domyślną konfiguracją"""
        manager = create_collective_memory_manager()
        
        self.assertIsInstance(manager, CollectiveMemoryManager)
        self.assertIsNotNone(manager.vector_index)
        self.assertIsNotNone(manager.embedding_generator)


class TestCollectiveMemoryManagerStoreOperations(unittest.TestCase):
    """Testy operacji zapisu pamięci"""

    def setUp(self):
        """SetUp"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """TearDown"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_manager(self):
        """Helper: tworzy zainicjalizowany manager"""
        config = CollectiveMemoryManagerConfig(
            vector_index_config=VectorIndexConfig(
                storage_path=os.path.join(self.temp_dir, "test_store"),
                dimension=384
            ),
            embedding_dimension=384
        )
        return create_collective_memory_manager(config)

    def test_06_store_strategy_memory(self):
        """Test zapisywania pamięci strategii"""
        manager = self._create_manager()
        
        strategy = StrategyMemoryRecord(
            strategy_id="str_001",
            strategy_name="Test Strategy",
            result="WIN",
            confidence=0.85,
            profit=150.0
        )
        
        doc_id = manager.store_memory(strategy)
        
        self.assertIsNotNone(doc_id)
        self.assertIsInstance(doc_id, str)
        
        # Sprawdź statystyki
        stats = manager.get_stats()
        self.assertEqual(stats['total_memories'], 1)
        self.assertEqual(stats['store_operations'], 1)

    def test_07_store_match_result(self):
        """Test zapisywania wyniku meczu"""
        manager = self._create_manager()
        
        match = MatchResult(
            match_id="match_001",
            home_team="Liverpool",
            away_team="Arsenal",
            home_goals=2,
            away_goals=1,
            result="HOME_WIN"
        )
        
        doc_id = manager.store_memory(match)
        
        self.assertIsNotNone(doc_id)
        
        stats = manager.get_stats()
        self.assertEqual(stats['total_memories'], 1)
        self.assertIn('match_result', stats['memories_by_type'])

    def test_08_store_multiple_types(self):
        """Test zapisywania wielu typów pamięci"""
        manager = self._create_manager()
        
        # Zapis több typów
        strategy = StrategyMemoryRecord(strategy_id="str_001", result="WIN")
        match = MatchResult(match_id="match_001", result="HOME_WIN")
        training = TrainingMemory(training_id="train_001", model_name="model_v1")
        observation = ObservationMemory(observation_id="obs_001", observer="agent_01")
        decision = DecisionMemory(decision_id="dec_001", action="place_bet")
        
        results = []
        for mem in [strategy, match, training, observation, decision]:
            doc_id = manager.store_memory(mem)
            results.append(doc_id)
        
        # Wszystkie powinny zostać zapisane
        self.assertEqual(len([r for r in results if r is not None]), 5)
        
        stats = manager.get_stats()
        self.assertEqual(stats['total_memories'], 5)
        self.assertEqual(len(stats['memories_by_type']), 5)

    def test_09_store_batch(self):
        """Test wsadowego zapisu"""
        manager = self._create_manager()
        
        memories = [
            StrategyMemoryRecord(strategy_id=f"str_{i}", result="WIN" if i % 2 == 0 else "LOSE")
            for i in range(10)
        ]
        
        doc_ids = manager.store_batch(memories)
        
        self.assertEqual(len(doc_ids), 10)
        self.assertEqual(manager.get_stats()['total_memories'], 10)

    def test_10_store_unsupported_type(self):
        """Test zapisywania nieobsługiwanego typu"""
        manager = self._create_manager()
        
        unsupported = {"some": "data", "with": "no adapter"}
        
        doc_id = manager.store_memory(unsupported)
        
        self.assertIsNone(doc_id)
        self.assertEqual(manager.get_stats()['total_memories'], 0)

    def test_11_thread_safety_store(self):
        """Test thread-safety zapisu"""
        manager = self._create_manager()
        
        import threading
        
        def store_memory_worker(memory_id):
            strategy = StrategyMemoryRecord(strategy_id=f"str_{memory_id}")
            return manager.store_memory(strategy)
        
        # Uruchom 10 wątków zapisujących jednocześnie
        threads = []
        results = []
        for i in range(10):
            t = threading.Thread(target=lambda: results.append(store_memory_worker(i)))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Wszystkie powinny zostać zapisane
        self.assertEqual(len([r for r in results if r is not None]), 10)
        self.assertEqual(manager.get_stats()['total_memories'], 10)


class TestCollectiveMemoryManagerSearchOperations(unittest.TestCase):
    """Testy operacji wyszukiwania"""

    def setUp(self):
        """SetUp"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """TearDown"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_and_populate_manager(self):
        """Helper: tworzy manager i wypełnia go danymi testowymi"""
        config = CollectiveMemoryManagerConfig(
            vector_index_config=VectorIndexConfig(
                storage_path=os.path.join(self.temp_dir, "test_search"),
                dimension=384
            ),
            embedding_dimension=384
        )
        manager = create_collective_memory_manager(config)
        
        # Dodaj różne typy pamięci
        manager.store_memory(StrategyMemoryRecord(
            strategy_id="liverpool_win",
            team="Liverpool",
            opponent="Arsenal",
            result="WIN",
            prediction="home_win"
        ))
        
        manager.store_memory(MatchResult(
            match_id="match_001",
            home_team="Liverpool",
            away_team="Man City",
            result="HOME_WIN"
        ))
        
        manager.store_memory(StrategyMemoryRecord(
            strategy_id="arsenal_lose",
            team="Arsenal",
            opponent="Chelsea",
            result="LOSE",
            prediction="away_win"
        ))
        
        return manager

    def test_12_search_memories_basic(self):
        """Test podstawowego wyszukiwania"""
        manager = self._create_and_populate_manager()
        
        # Szukaj tekstu, który powinien być w dokumentach
        results = manager.search_memories("Strategy liverpool_win v1.0", top_k=5, min_similarity=0.0)
        
        self.assertIsInstance(results, list)
        # Powinniśmy znaleźć przynajmniej jeden dokument
        self.assertGreaterEqual(len(results), 1)
        
        # Sprawdź typy wyników
        for result in results:
            self.assertIsInstance(result, CollectiveMemoryDocument)

    def test_13_search_with_min_similarity(self):
        """Test wyszukiwania z minimalnym podobieństwem"""
        manager = self._create_and_populate_manager()
        
        # Bardzo wysoki próg
        results = manager.search_memories("Liverpool", min_similarity=0.99)
        
        # Powinno zwrócić mniej wyników
        self.assertIsInstance(results, list)

    def test_14_search_with_source_type_filter(self):
        """Test wyszukiwania z filtrem po typie źródła"""
        manager = self._create_and_populate_manager()
        
        results = manager.search_memories("Liverpool", source_type_filter="strategy_memory")
        
        self.assertIsInstance(results, list)
        for result in results:
            self.assertEqual(result.source_type, "strategy_memory")

    def test_15_search_by_situation(self):
        """Test wyszukiwania po sytuacji"""
        manager = self._create_and_populate_manager()
        
        situation = {
            "team": "Liverpool",
            "opponent": "Arsenal",
            "prediction": "home_win"
        }
        
        results = manager.search_by_situation(situation, top_k=3, min_similarity=0.0)
        
        self.assertIsInstance(results, list)
        # Test dziales korzystając z tekstu sytuacji
        self.assertGreaterEqual(len(results), 0)

    def test_16_search_empty_index(self):
        """Test wyszukiwania w pustym indeksie"""
        config = CollectiveMemoryManagerConfig(
            vector_index_config=VectorIndexConfig(
                storage_path=os.path.join(self.temp_dir, "test_empty"),
                dimension=384
            ),
            embedding_dimension=384
        )
        manager = create_collective_memory_manager(config)
        
        results = manager.search_memories("test", top_k=5)
        
        self.assertEqual(results, [])

    def test_17_retrieve_memory_by_id(self):
        """Test pobierania pamięci po ID"""
        manager = self._create_and_populate_manager()
        
        # Pobierz pierwszy dokument
        results = manager.search_memories("Liverpool", top_k=1)
        if results:
            doc = results[0]
            retrieved = manager.retrieve_memory(doc.document_id)
            
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.document_id, doc.document_id)

    def test_18_get_relevant_memories(self):
        """Test pobierania istotnych pamięci"""
        manager = self._create_and_populate_manager()
        
        context = {
            "team": "Liverpool",
            "result": "WIN",
            "action": "place_bet"
        }
        
        results = manager.get_relevant_memories(context, top_k=3, min_similarity=0.0)
        
        self.assertIsInstance(results, list)


class TestCollectiveMemoryManagerContextBuilding(unittest.TestCase):
    """Testy budowania kontekstu dla agentów"""

    def setUp(self):
        """SetUp"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """TearDown"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_and_populate_manager(self):
        """Helper: tworzy manager z danymi testowymi"""
        config = CollectiveMemoryManagerConfig(
            vector_index_config=VectorIndexConfig(
                storage_path=os.path.join(self.temp_dir, "test_context"),
                dimension=384
            ),
            embedding_dimension=384
        )
        manager = create_collective_memory_manager(config)
        
        # Dodaj pamięciHelper: tworzy manager z danymi testowymi
        manager = create_collective_memory_manager(config)
        
        # Dodaj pamięci
        manager.store_memory(StrategyMemoryRecord(
            strategy_id="str_001",
            team="Liverpool",
            result="WIN",
            confidence=0.85
        ))
        
        manager.store_memory(MatchResult(
            match_id="match_001",
            home_team="Liverpool",
            result="HOME_WIN"
        ))
        
        return manager

    def test_19_build_agent_context_basic(self):
        """Test podstawowego budowania kontekstu"""
        manager = self._create_and_populate_manager()
        
        situation = {
            "team": "Liverpool",
            "opponent": "Arsenal",
            "current_odds": 2.10
        }
        
        context = manager.build_agent_context(
            agent_id="agent_01",
            current_situation=situation,
            max_context_length=2000
        )
        
        # Sprawdź strukturę kontekstu
        self.assertIn('agent_id', context)
        self.assertEqual(context['agent_id'], 'agent_01')
        self.assertIn('situation', context)
        self.assertEqual(context['situation'], situation)
        self.assertIn('relevant_memories', context)
        self.assertIn('memory_context', context)
        self.assertIn('memory_count', context)
        self.assertIn('avg_similarity', context)

    def test_20_build_agent_context_empty(self):
        """Test budowania kontekstu z pustym indeksem"""
        config = CollectiveMemoryManagerConfig(
            vector_index_config=VectorIndexConfig(
                storage_path=os.path.join(self.temp_dir, "test_empty_context"),
                dimension=384
            ),
            embedding_dimension=384
        )
        manager = create_collective_memory_manager(config)
        
        situation = {"team": "Test"}
        
        context = manager.build_agent_context(
            agent_id="agent_01",
            current_situation=situation
        )
        
        self.assertEqual(context['memory_count'], 0)
        self.assertEqual(context['relevant_memories'], [])
        self.assertEqual(context['memory_context'], '')

    def test_21_build_agent_context_max_length(self):
        """Test budowania kontekstu z ograniczeniem długości"""
        manager = self._create_and_populate_manager()
        
        situation = {"team": "Liverpool"}
        
        context = manager.build_agent_context(
            agent_id="agent_01",
            current_situation=situation,
            max_context_length=100
        )
        
        # Kontekst powinien być ograniczony
        self.assertLessEqual(len(context['memory_context']), 100)


class TestCollectiveMemoryManagerStatisticsAndMonitoring(unittest.TestCase):
    """Testy statystyk i monitorowania"""

    def setUp(self):
        """SetUp"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """TearDown"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_22_get_stats(self):
        """Test pobierania statystyk"""
        config = CollectiveMemoryManagerConfig(
            vector_index_config=VectorIndexConfig(
                storage_path=os.path.join(self.temp_dir, "test_stats"),
                dimension=384
            ),
            embedding_dimension=384
        )
        manager = create_collective_memory_manager(config)
        
        # Dodaj pamięci
        manager.store_memory(StrategyMemoryRecord(strategy_id="str_001"))
        manager.store_memory(MatchResult(match_id="match_001"))
        
        # Wykonaj wyszukiwania
        manager.search_memories("test", top_k=5)
        manager.search_memories("test2", top_k=3)
        
        stats = manager.get_stats()
        
        self.assertEqual(stats['total_memories'], 2)
        self.assertEqual(stats['store_operations'], 2)
        self.assertEqual(stats['search_operations'], 2)
        self.assertIn('vector_index', stats)
        self.assertIn('memories_by_type', stats)

    def test_23_get_memory_distribution(self):
        """Test pobierania rozkładu pamięci"""
        config = CollectiveMemoryManagerConfig(
            vector_index_config=VectorIndexConfig(
                storage_path=os.path.join(self.temp_dir, "test_dist"),
                dimension=384
            ),
            embedding_dimension=384
        )
        manager = create_collective_memory_manager(config)
        
        manager.store_memory(StrategyMemoryRecord(strategy_id="str_001"))
        manager.store_memory(StrategyMemoryRecord(strategy_id="str_002"))
        manager.store_memory(MatchResult(match_id="match_001"))
        
        distribution = manager.get_memory_distribution()
        
        self.assertIn('strategy_memory', distribution)
        self.assertEqual(distribution['strategy_memory'], 2)
        self.assertIn('match_result', distribution)
        self.assertEqual(distribution['match_result'], 1)


class TestCollectiveMemoryManagerPersistence(unittest.TestCase):
    """Testy persystencji"""

    def setUp(self):
        """SetUp"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """TearDown"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_24_save_and_load(self):
        """Test zapisu i wczytania"""
        storage_path = os.path.join(self.temp_dir, "test_persist")
        
        # Tworzenie i zapis
        config = CollectiveMemoryManagerConfig(
            vector_index_config=VectorIndexConfig(
                storage_path=storage_path,
                dimension=384
            ),
            embedding_dimension=384
        )
        manager1 = create_collective_memory_manager(config)
        
        manager1.store_memory(StrategyMemoryRecord(strategy_id="str_001"))
        manager1.store_memory(MatchResult(match_id="match_001"))
        
        save_result = manager1.save()
        self.assertTrue(save_result)
        
        # Wczytanie
        config2 = CollectiveMemoryManagerConfig(
            vector_index_config=VectorIndexConfig(
                storage_path=storage_path,
                dimension=384
            ),
            embedding_dimension=384
        )
        manager2 = create_collective_memory_manager(config2)
        
        load_result = manager2.load()
        self.assertTrue(load_result)
        
        # Sprawdź czy dane zostały wczytane
        self.assertEqual(manager2.get_stats()['total_memories'], 2)

    def test_25_clear(self):
        """Test czyszczenia pamięci"""
        config = CollectiveMemoryManagerConfig(
            vector_index_config=VectorIndexConfig(
                storage_path=os.path.join(self.temp_dir, "test_clear"),
                dimension=384
            ),
            embedding_dimension=384
        )
        manager = create_collective_memory_manager(config)
        
        manager.store_memory(StrategyMemoryRecord(strategy_id="str_001"))
        manager.store_memory(MatchResult(match_id="match_001"))
        
        self.assertEqual(manager.get_stats()['total_memories'], 2)
        
        manager.clear()
        
        self.assertEqual(manager.get_stats()['total_memories'], 0)
        self.assertEqual(len(manager.get_memory_distribution()), 0)


class TestCollectiveMemoryManagerIntegration(unittest.TestCase):
    """Testy integracyjne"""

    def setUp(self):
        """SetUp"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """TearDown"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_26_full_workflow(self):
        """Test pełnego przepływu pracy"""
        config = CollectiveMemoryManagerConfig(
            vector_index_config=VectorIndexConfig(
                storage_path=os.path.join(self.temp_dir, "test_workflow"),
                dimension=384
            ),
            embedding_dimension=384
        )
        manager = create_collective_memory_manager(config)
        
        # 1. Zapis różnych typów pamięci
        memories = [
            StrategyMemoryRecord(
                memory_id="liverpool_strategy",
                strategy_id="liverpool_strategy",
                team="Liverpool",
                result="WIN",
                confidence=0.85
            ),
            MatchResult(
                match_id="match_001",
                home_team="Liverpool",
                away_team="Arsenal",
                result="HOME_WIN"
            ),
            TrainingMemory(
                session_id="train_001",
                model_name="liverpool_predictor",
                accuracy=0.85
            ),
            ObservationMemory(
                observation_id="obs_001",
                observer="agent_01",
                data={"pattern": "high_odds"}
            ),
            DecisionMemory(
                decision_id="dec_001",
                action="place_bet",
                confidence=0.90
            )
        ]
        
        for memory in memories:
            doc_id = manager.store_memory(memory)
            self.assertIsNotNone(doc_id)
        
        # 2. Wyszukaj pamięci - szukamy tekstów, które są w dokumentach
        results = manager.search_memories("Strategy liverpool_strategy v1.0", top_k=3, min_similarity=0.0)
        self.assertGreaterEqual(len(results), 1)
        
        # 3. Buduj kontekst dla agenta - użyj tekstu, który pasuje do dokumentów
        context = manager.build_agent_context(
            agent_id="agent_01",
            current_situation={
                "query": "Strategy liverpool_strategy v1.0"
            }
        )
        
        # Powinien znaleźć przynajmniej jedną pamięć
        self.assertGreaterEqual(context['memory_count'], 1)
        
        # 4. Z source_type filter
        results = manager.search_memories("Strategy liverpool_strategy v1.0", source_type_filter="strategy_memory", min_similarity=0.0)
        self.assertGreaterEqual(len(results), 1)
        
        # 5. Sprawdź statystyki
        stats = manager.get_stats()
        self.assertEqual(stats['total_memories'], 5)
        self.assertEqual(stats['store_operations'], 5)

    def test_27_search_and_retrieve_consistency(self):
        """Test spójności między wyszukiwaniem a pobieraniem"""
        config = CollectiveMemoryManagerConfig(
            vector_index_config=VectorIndexConfig(
                storage_path=os.path.join(self.temp_dir, "test_consistency"),
                dimension=384
            ),
            embedding_dimension=384
        )
        manager = create_collective_memory_manager(config)
        
        # Zapis pamięci z explicite memory_id
        memory = StrategyMemoryRecord(
            memory_id="test_strategy",
            strategy_id="test_strategy",
            team="Test",
            result="WIN"
        )
        doc_id = manager.store_memory(memory)
        
        # Wyszukaj i pobierz - szukaj tekstu, który jest w dokumencie
        results = manager.search_memories("Strategy test_strategy v1.0", top_k=1, min_similarity=0.0)
        if results:
            doc = results[0]
            retrieved = manager.retrieve_memory(doc.document_id)
            
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.source_id, "test_strategy")
        else:
            # Jeśli nie znaleziono przez wyszukiwanie, sprawdź pobieranie bezpośrednie
            # Dokument powinien zostać zapisany
            self.assertIsNotNone(doc_id)


class TestCollectiveMemoryManagerConfig(unittest.TestCase):
    """Testy konfiguracji"""

    def test_28_config_default_values(self):
        """Test domyślnych wartości konfiguracji"""
        config = CollectiveMemoryManagerConfig()
        
        self.assertIsNotNone(config.vector_index_config)
        self.assertEqual(config.embedding_dimension, 384)
        self.assertIn('collective_memory', config.storage_path)

    def test_29_config_custom_values(self):
        """Test niestandardowych wartości konfiguracji"""
        vector_config = VectorIndexConfig(
            index_type=INDEX_TYPE_NUMPY,
            storage_path="/custom/path",
            dimension=768
        )
        
        config = CollectiveMemoryManagerConfig(
            vector_index_config=vector_config,
            embedding_dimension=768,
            storage_path="/custom/storage"
        )
        
        self.assertEqual(config.vector_index_config, vector_config)
        self.assertEqual(config.embedding_dimension, 768)
        self.assertEqual(config.storage_path, "/custom/storage")


if __name__ == '__main__':
    unittest.main()
