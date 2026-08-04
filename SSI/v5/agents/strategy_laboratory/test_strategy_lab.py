"""
SSI V5 - Strategy Laboratory Tests

Testy dla ETAP 2.3 - Strategy Laboratory.

Wymagane testy:
1. Test tworzenia strategii
2. Test eksperymentu
3. Test rankingu
4. Test zapisu pamięci
5. Test integracji z IFC

Wersja: 1.0.0
Data: 2026-08-01
"""

import unittest
import sys
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Dodanie ścieżki do SSI
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importy z Strategy Laboratory
try:
    from .strategy_models import (
        Strategy,
        StrategyParameters,
        StrategyResult,
        StrategyEvaluation,
        StrategyRanking,
        StrategyStatus,
        StrategyType,
        StrategyVersion,
        create_strategy,
        update_strategy_stats
    )
    from .experiment_models import (
        Experiment,
        ExperimentParameters,
        ExperimentResult,
        ExperimentComparison,
        ExperimentStatus,
        ExperimentType,
        TestMethodology,
        create_experiment,
        update_experiment_stats
    )
    from .strategy_manager import (
        StrategyManager,
        StrategyManagerConfig,
        create_strategy_manager,
        get_strategy_manager
    )
    from .experiment_manager import (
        ExperimentManager,
        ExperimentManagerConfig,
        create_experiment_manager,
        get_experiment_manager
    )
    from .strategy_ranking_engine import (
        StrategyRankingEngine,
        RankingConfig,
        RankingWeights,
        RankingCriteria,
        create_ranking_engine,
        get_ranking_engine
    )
    from .strategy_memory import (
        StrategyMemory,
        StrategyMemoryConfig,
        AgentStrategyLaboratory,
        create_strategy_memory,
        get_strategy_memory
    )
    from .memory_integrator import (
        StrategyMemoryIntegrator,
        MemoryIntegratorConfig,
        create_memory_integrator,
        get_memory_integrator
    )
    from .ifc_integrator import (
        StrategyIFCIntegrator,
        IFCIntegratorConfig,
        create_ifc_integrator,
        get_ifc_integrator
    )
    
    print("✅ Wszystkie moduły Strategy Laboratory załadowane pomyślnie")
    
except Exception as e:
    print(f"❌ Błąd podczas ładowania modułów: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


class TestStrategyModels(unittest.TestCase):
    """Testy modeli strategii."""
    
    def setUp(self):
        """Inicjalizacja testów modeli strategii."""
        self.agent_id = "test_agent_001"
        self.strategy_name = "Test Strategy"
        self.parameters = StrategyParameters(
            strategy_type=StrategyType.DECISION,
            risk_level=0.5,
            confidence_threshold=0.7
        )
    
    def test_strategy_creation(self):
        """Test 1.1: Tworzenie strategii."""
        strategy = create_strategy(
            agent_owner=self.agent_id,
            name=self.strategy_name,
            strategy_type=StrategyType.DECISION,
            description="Test description",
            parameters=self.parameters
        )
        
        self.assertIsNotNone(strategy)
        self.assertEqual(strategy.agent_owner, self.agent_id)
        self.assertEqual(strategy.name, self.strategy_name)
        self.assertEqual(strategy.strategy_type, StrategyType.DECISION)
        self.assertEqual(strategy.status, StrategyStatus.DRAFT)
        self.assertIsNotNone(strategy.strategy_id)
        self.assertIsNotNone(strategy.creation_date)
        
        print("✅ Test 1.1: Tworzenie strategii - ZALICZONY")
    
    def test_strategy_parameters_validation(self):
        """Test 1.2: Walidacja parametrów strategii."""
        # Dołącz广e parametry
        valid_params = StrategyParameters(
            risk_level=0.5,
            confidence_threshold=0.7,
            decision_threshold=0.6,
            analysis_depth=3,
            prediction_horizon=5
        )
        self.assertTrue(valid_params.validate())
        
        # Nieprawidłowe parametry
        invalid_params = StrategyParameters(risk_level=1.5)  # > 1.0
        self.assertFalse(invalid_params.validate())
        
        invalid_params2 = StrategyParameters(analysis_depth=0)  # < 1
        self.assertFalse(invalid_params2.validate())
        
        print("✅ Test 1.2: Walidacja parametrów strategii - ZALICZONY")
    
    def test_strategy_serialization(self):
        """Test 1.3: Serializacja i deserializacja strategii."""
        strategy = create_strategy(
            agent_owner=self.agent_id,
            name="Serializable Strategy",
            description="Test serialization"
        )
        
        # Serializacja do dict
        strategy_dict = strategy.to_dict()
        self.assertIsInstance(strategy_dict, dict)
        self.assertIn('strategy_id', strategy_dict)
        
        # Deserializacja
        restored_strategy = Strategy.from_dict(strategy_dict)
        self.assertEqual(restored_strategy.strategy_id, strategy.strategy_id)
        self.assertEqual(restored_strategy.name, strategy.name)
        
        # Serializacja do JSON
        json_str = strategy.to_json()
        self.assertIsInstance(json_str, str)
        
        # Deserializacja z JSON
        from_json_strategy = Strategy.from_json(json_str)
        self.assertEqual(from_json_strategy.strategy_id, strategy.strategy_id)
        
        print("✅ Test 1.3: Serializacja strategii - ZALICZONY")
    
    def test_strategy_result_update(self):
        """Test 1.4: Aktualizacja strategii na podstawie wyniku."""
        strategy = create_strategy(
            agent_owner=self.agent_id,
            name="Result Test Strategy"
        )
        
        # Utworzenie wyniku
        result = StrategyResult(
            strategy_id=strategy.strategy_id,
            success=True,
            score=0.8,
            confidence=0.9
        )
        
        # Aktualizacja strategii
        updated_strategy = update_strategy_stats(strategy, result)
        
        self.assertEqual(updated_strategy.usage_count, 1)
        self.assertEqual(updated_strategy.success_count, 1)
        self.assertEqual(updated_strategy.failure_count, 0)
        self.assertEqual(updated_strategy.success_rate, 1.0)
        self.assertGreater(updated_strategy.avg_score, 0)
        
        print("✅ Test 1.4: Aktualizacja strategii z wyniku - ZALICZONY")


class TestExperimentModels(unittest.TestCase):
    """Testy modeli eksperymentów."""
    
    def setUp(self):
        """Inicjalizacja testów modeli eksperymentów."""
        self.agent_id = "test_agent_001"
        self.strategy_id = "test_strategy_001"
    
    def test_experiment_creation(self):
        """Test 2.1: Tworzenie eksperymentu."""
        experiment = create_experiment(
            agent_owner=self.agent_id,
            name="Test Experiment",
            strategy_id=self.strategy_id,
            experiment_type=ExperimentType.A_B_TESTING,
            description="Test A/B experiment"
        )
        
        self.assertIsNotNone(experiment)
        self.assertEqual(experiment.agent_owner, self.agent_id)
        self.assertEqual(experiment.strategy_id, self.strategy_id)
        self.assertEqual(experiment.experiment_type, ExperimentType.A_B_TESTING)
        self.assertEqual(experiment.status, ExperimentStatus.PLANNED)
        self.assertIsNotNone(experiment.experiment_id)
        
        print("✅ Test 2.1: Tworzenie eksperymentu - ZALICZONY")
    
    def test_experiment_parameters_validation(self):
        """Test 2.2: Walidacja parametrów eksperymentu."""
        # Prawidłowe parametry
        valid_params = ExperimentParameters(
            experiment_type=ExperimentType.A_B_TESTING,
            iterations=100,
            test_group_size=50,
            control_group_size=50
        )
        self.assertTrue(valid_params.validate())
        
        # Nieprawidłowe parametry
        invalid_params = ExperimentParameters(iterations=0)
        self.assertFalse(invalid_params.validate())
        
        print("✅ Test 2.2: Walidacja parametrów eksperymentu - ZALICZONY")
    
    def test_experiment_result_calculation(self):
        """Test 2.3: Obliczenia w wyniku eksperymentu."""
        result = ExperimentResult(
            experiment_id="test_experiment",
            iteration=1
        )
        
        # Dodanie danych testowych
        result.test_group_results = [
            {'success': True, 'score': 0.8},
            {'success': True, 'score': 0.9},
            {'success': False, 'score': 0.4}
        ]
        
        # Obliczenie istotności statystycznej (uproszczona terapia)
        stats = result.calculate_statistical_significance('score')
        self.assertIn('significant', stats)
        self.assertIn('p_value', stats)
        self.assertIn('effect_size', stats)
        
        print("✅ Test 2.3: Obliczenia w wyniku eksperymentu - ZALICZONY")
    
    def test_experiment_serialization(self):
        """Test 2.4: Serializacja eksperymentu."""
        experiment = create_experiment(
            agent_owner=self.agent_id,
            name="Serializable Experiment",
            strategy_id=self.strategy_id
        )
        
        # Serializacja
        experiment_dict = experiment.to_dict()
        self.assertIsInstance(experiment_dict, dict)
        
        # Deserializacja
        restored = Experiment.from_dict(experiment_dict)
        self.assertEqual(restored.experiment_id, experiment.experiment_id)
        
        # JSON
        json_str = experiment.to_json()
        from_json = Experiment.from_json(json_str)
        self.assertEqual(from_json.experiment_id, experiment.experiment_id)
        
        print("✅ Test 2.4: Serializacja eksperymentu - ZALICZONY")


class TestStrategyManager(unittest.TestCase):
    """Testy Strategy Manager."""
    
    @classmethod
    def setUpClass(cls):
        """Inicjalizacja klasy testów."""
        # Reset singletonów
        from .strategy_manager import _strategy_manager
        from .strategy_manager import _strategy_manager_lock
        
        with _strategy_manager_lock:
            # Utworzenie nowej instancji na potrzeby testów
            cls.test_manager = StrategyManager(StrategyManagerConfig(
                max_strategies_per_agent=10,
                enable_validation=True
            ))
    
    def test_create_strategy(self):
        """Test 3.1: Tworzenie strategii przez manager."""
        strategy = self.test_manager.create_strategy(
            agent_owner="test_agent_002",
            name="Manager Test Strategy",
            description="Test strategy creation"
        )
        
        self.assertIsNotNone(strategy)
        self.assertEqual(strategy.name, "Manager Test Strategy")
        self.assertEqual(strategy.agent_owner, "test_agent_002")
        self.assertEqual(strategy.status, StrategyStatus.DRAFT)
        
        print("✅ Test 3.1: Tworzenie strategii przez manager - ZALICZONY")
    
    def test_get_strategy(self):
        """Test 3.2: Pobieranie strategii."""
        # utwórz strategię
        strategy = self.test_manager.create_strategy(
            agent_owner="test_agent_003",
            name="Retrieve Test Strategy"
        )
        
        # Pobierz strategię
        retrieved = self.test_manager.get_strategy(strategy.strategy_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.strategy_id, strategy.strategy_id)
        
        print("✅ Test 3.2: Pobieranie strategii - ZALICZONY")
    
    def test_get_strategies_by_agent(self):
        """Test 3.3: Pobieranie strategii agenta."""
        agent_id = "test_agent_array"
        
        # Utworzenie kilku strategii
        for i in range(3):
            self.test_manager.create_strategy(
                agent_owner=agent_id,
                name=f"Agent Strategy {i}"
            )
        
        # Pobranie strategii agenta
        strategies = self.test_manager.get_strategies_by_agent(agent_id)
        self.assertEqual(len(strategies), 3)
        
        print("✅ Test 3.3: Pobieranie strategii agenta - ZALICZONY")
    
    def test_evaluate_strategy(self):
        """Test 3.4: Ocena strategii."""
        # Utworzenie strategii
        strategy = self.test_manager.create_strategy(
            agent_owner="test_agent_004",
            name="Evaluation Test Strategy"
        )
        
        # Ocena strategii
        updated_strategy, evaluation = self.test_manager.evaluate_strategy(
            strategy_id=strategy.strategy_id,
            evaluator_agent_id="evaluator_agent_001",
            effectiveness=0.8,
            stability=0.7,
            efficiency=0.9,
            reliability=0.85,
            adaptability=0.75,
            confidence=0.8
        )
        
        self.assertIsNotNone(updated_strategy)
        self.assertIsNotNone(evaluation)
        self.assertEqual(evaluation.overall_score, evaluation.calculate_overall_score())
        self.assertGreater(evaluation.overall_score, 0)
        
        print("✅ Test 3.4: Ocena strategii - ZALICZONY")
    
    def test_rank_strategies(self):
        """Test 3.5: Ranking strategii."""
        # Utworzenie kilku strategii z różnymi wynikami
        agent_id = "ranking_test_agent"
        
        strategies = []
        for i in range(5):
            strategy = self.test_manager.create_strategy(
                agent_owner=agent_id,
                name=f"Ranking Strategy {i}",
                confidence=0.5 + i * 0.1
            )
            strategies.append(strategy)
        
        # Nadanie różnych ranking_scores
        scores = [0.9, 0.7, 0.8, 0.6, 0.95]
        for i, strategy in enumerate(strategy for strategy in strategies):
            strategy.ranking_score = scores[i]
            self.test_manager.storage.update(strategy)
        
        # Ranking
        rankings = self.test_manager.rank_strategies(agent_id=agent_id, limit=5)
        
        self.assertEqual(len(rankings), 5)
        self.assertEqual(rankings[0].rank, 1)
        # Sprawdzenie czy ranking jest posortowany
        for i in range(len(rankings) - 1):
            current_strategy = self.test_manager.get_strategy(rankings[i].strategy_id)
            next_strategy = self.test_manager.get_strategy(rankings[i+1].strategy_id)
            if current_strategy and next_strategy:
                self.assertGreaterEqual(
                    current_strategy.ranking_score,
                    next_strategy.ranking_score
                )
        
        print("✅ Test 3.5: Ranking strategii - ZALICZONY")
    
    def test_archive_strategy(self):
        """Test 3.6: Archiwizacja strategii."""
        # Utworzenie strategii
        strategy = self.test_manager.create_strategy(
            agent_owner="test_agent_005",
            name="Archive Test Strategy"
        )
        
        # Archiwizacja
        archived = self.test_manager.archive_strategy(
            strategy_id=strategy.strategy_id,
            reason="Test archivation"
        )
        
        self.assertIsNotNone(archived)
        self.assertEqual(archived.status, StrategyStatus.ARCHIVED)
        
        print("✅ Test 3.6: Archiwizacja strategii - ZALICZONY")


class TestExperimentManager(unittest.TestCase):
    """Testy Experiment Manager."""
    
    @classmethod
    def setUpClass(cls):
        """Inicjalizacja klasy testów."""
        # Utworzenie nowej instancji na potrzeby testów
        cls.test_manager = ExperimentManager(ExperimentManagerConfig(
            max_experiments_per_agent=10,
            enable_validation=True
        ))
    
    def test_create_experiment(self):
        """Test 4.1: Tworzenie eksperymentu przez manager."""
        experiment = self.test_manager.create_experiment(
            agent_owner="test_agent_exp_001",
            name="Manager Test Experiment",
            strategy_id="test_strategy_exp_001",
            description="Test experiment"
        )
        
        self.assertIsNotNone(experiment)
        self.assertEqual(experiment.name, "Manager Test Experiment")
        self.assertEqual(experiment.agent_owner, "test_agent_exp_001")
        self.assertEqual(experiment.status, ExperimentStatus.PLANNED)
        
        print("✅ Test 4.1: Tworzenie eksperymentu przez manager - ZALICZONY")
    
    def test_get_experiment(self):
        """Test 4.2: Pobieranie eksperymentu."""
        experiment = self.test_manager.create_experiment(
            agent_owner="test_agent_exp_002",
            name="Retrieve Test Experiment",
            strategy_id="test_strategy_exp_002"
        )
        
        retrieved = self.test_manager.get_experiment(experiment.experiment_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.experiment_id, experiment.experiment_id)
        
        print("✅ Test 4.2: Pobieranie eksperymentu - ZALICZONY")
    
    def test_get_experiments_by_agent(self):
        """Test 4.3: Pobieranie eksperymentów agenta."""
        agent_id = "test_agent_exp_array"
        
        for i in range(3):
            self.test_manager.create_experiment(
                agent_owner=agent_id,
                name=f"Agent Experiment {i}",
                strategy_id=f"strategy_{i}"
            )
        
        experiments = self.test_manager.get_experiments_by_agent(agent_id)
        self.assertEqual(len(experiments), 3)
        
        print("✅ Test 4.3: Pobieranie eksperymentów agenta - ZALICZONY")
    
    def test_run_experiment(self):
        """Test 4.4: Uruchomienie eksperymentu."""
        # Utworzenie eksperymentu
        experiment = self.test_manager.create_experiment(
            agent_owner="test_agent_exp_003",
            name="Run Test Experiment",
            strategy_id="test_strategy_exp_003"
        )
        
        # Uruchomienie eksperymentu
        updated_experiment, result = self.test_manager.run_experiment(experiment.experiment_id)
        
        self.assertIsNotNone(updated_experiment)
        self.assertIsNotNone(result)
        self.assertEqual(updated_experiment.status, ExperimentStatus.COMPLETED)
        
        print("✅ Test 4.4: Uruchomienie eksperymentu - ZALICZONY")
    
    def test_compare_experiment_results(self):
        """Test 4.5: Porównanie wyników eksperymentów."""
        # Utworzenie kilku eksperymentów
        experiments = []
        for i in range(3):
            exp = self.test_manager.create_experiment(
                agent_owner="test_agent_exp_004",
                name=f"Comparison Experiment {i}",
                strategy_id="test_strategy_exp_004"
            )
            experiments.append(exp)
            
            # Uruchomienie eksperymentu
            _, _ = self.test_manager.run_experiment(exp.experiment_id)
        
        # Porównanie wyników
        experiment_ids = [exp.experiment_id for exp in experiments]
        comparison = self.test_manager.compare_results(experiment_ids)
        
        self.assertIsNotNone(comparison)
        self.assertEqual(len(comparison.experiment_ids), 3)
        self.assertIsNotNone(comparison.winner_experiment_id)
        
        print("✅ Test 4.5: Porównanie wyników eksperymentów - ZALICZONY")


class TestStrategyRankingEngine(unittest.TestCase):
    """Testy Strategy Ranking Engine."""
    
    @classmethod
    def setUpClass(cls):
        """Inicjalizacja klasy testów."""
        cls.ranking_engine = StrategyRankingEngine(RankingConfig())
    
    def test_calculate_strategy_score(self):
        """Test 5.1: Obliczanie wyniku strategii."""
        # Utworzenie strategii z różnymi parametrami
        strategy = Strategy(
            strategy_id="test_strategy_score",
            agent_owner="test_agent_006",
            name="Scoring Test Strategy",
            success_rate=0.8,
            avg_score=0.85,
            confidence=0.9,
            reliability=0.85,
            usage_count=10
        )
        
        score = self.ranking_engine.calculate_strategy_score(strategy)
        
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0)
        
        print("✅ Test 5.1: Obliczanie wyniku strategii - ZALICZONY")
    
    def test_rank_strategies(self):
        """Test 5.2: Ranking strategii przez engine."""
        # Utworzenie kilku strategii
        strategies = []
        for i in range(5):
            strategy = Strategy(
                strategy_id=f"ranked_strategy_{i}",
                agent_owner="test_agent_007",
                name=f"Ranked Strategy {i}",
                success_rate=0.5 + i * 0.1,
                avg_score=0.5 + i * 0.1,
                confidence=0.5 + i * 0.1,
                usage_count=10 + i * 5
            )
            strategies.append(strategy)
        
        # Ranking
        rankings = self.ranking_engine.rank_strategies(
            strategies=strategies,
            filter_active=False,
            filter_min_usage=False,
            limit=5
        )
        
        self.assertEqual(len(rankings), 5)
        self.assertEqual(rankings[0].rank, 1)
        
        print("✅ Test 5.2: Ranking strategii przez engine - ZALICZONY")
    
    def test_rank_by_agent(self):
        """Test 5.3: Ranking strategii dla konkretnego agenta."""
        # Utworzenie strategii dla różnych agentów
        strategies = []
        for agent_num in range(3):
            agent_id = f"ranking_agent_{agent_num}"
            for i in range(3):
                strategy = Strategy(
                    strategy_id=f"{agent_id}_strategy_{i}",
                    agent_owner=agent_id,
                    name=f"Agent {agent_num} Strategy {i}",
                    success_rate=0.6 + i * 0.1
                )
                strategies.append(strategy)
        
        # Ranking dla konkretnego agenta
        rankings = self.ranking_engine.rank_by_agent(
            strategies=strategies,
            agent_id="ranking_agent_0",
            filter_active=False,
            filter_min_usage=False
        )
        
        self.assertEqual(len(rankings), 3)
        for ranking in rankings:
            strategy = next((s for s in strategies if s.strategy_id == ranking.strategy_id), None)
            if strategy:
                self.assertEqual(strategy.agent_owner, "ranking_agent_0")
        
        print("✅ Test 5.3: Ranking strategii dla agenta - ZALICZONY")
    
    def test_custom_weights(self):
        """Test 5.4: Ranking z niestandardowymi wagami."""
        weights = RankingWeights(
            effectiveness=0.5,
            confidence=0.3,
            usage_count=0.2
        )
        
        strategy = Strategy(
            strategy_id="custom_weights_strategy",
            agent_owner="test_agent_008",
            name="Custom Weights Strategy",
            avg_score=0.9,
            success_rate=0.8,
            confidence=0.95
        )
        
        score = self.ranking_engine.calculate_strategy_score(strategy, weights)
        
        self.assertIsInstance(score, float)
        
        print("✅ Test 5.4: Ranking z niestandardowymi wagami - ZALICZONY")
    
    def test_mus_score(self):
        """Test 5.5: Obliczanie MUS Score."""
        strategy = Strategy(
            strategy_id="mus_test_strategy",
            agent_owner="test_agent_009",
            name="MUS Test Strategy",
            success_rate=0.75,
            avg_score=0.8,
            confidence=0.9
        )
        
        mus_score = self.ranking_engine.calculate_mus_score(strategy)
        
        self.assertIn('mus_score', mus_score)
        self.assertIn('components', mus_score)
        self.assertIn('weighted_components', mus_score)
        self.assertIsInstance(mus_score['mus_score'], float)
        
        print("✅ Test 5.5: Obliczanie MUS Score - ZALICZONY")


class TestStrategyMemory(unittest.TestCase):
    """Testy Strategy Memory."""
    
    def test_agent_lab_creation(self):
        """Test 6.1: Tworzenie laboratorium agenta."""
        lab = AgentStrategyLaboratory(agent_id="memory_test_agent")
        
        self.assertEqual(lab.agent_id, "memory_test_agent")
        self.assertEqual(lab.total_strategies, 0)
        self.assertEqual(lab.total_experiments, 0)
        
        print("✅ Test 6.1: Tworzenie laboratorium agenta - ZALICZONY")
    
    def test_add_strategy_to_lab(self):
        """Test 6.2: Dodawanie strategii do laboratorium."""
        lab = AgentStrategyLaboratory(agent_id="memory_test_agent")
        
        strategy = create_strategy(
            agent_owner="memory_test_agent",
            name="Lab Strategy"
        )
        
        strategy_id = lab.add_strategy(strategy)
        
        self.assertEqual(lab.total_strategies, 1)
        self.assertEqual(strategy_id, strategy.strategy_id)
        
        print("✅ Test 6.2: Dodawanie strategii do laboratorium - ZALICZONY")
    
    def test_add_experiment_to_lab(self):
        """Test 6.3: Dodawanie eksperymentu do laboratorium."""
        lab = AgentStrategyLaboratory(agent_id="memory_test_agent")
        
        experiment = create_experiment(
            agent_owner="memory_test_agent",
            name="Lab Experiment",
            strategy_id="test_strategy"
        )
        
        experiment_id = lab.add_experiment(experiment)
        
        self.assertEqual(lab.total_experiments, 1)
        self.assertEqual(experiment_id, experiment.experiment_id)
        
        print("✅ Test 6.3: Dodawanie eksperymentu do laboratorium - ZALICZONY")
    
    def test_lab_serialization(self):
        """Test 6.4: Serializacja laboratorium."""
        lab = AgentStrategyLaboratory(agent_id="serialization_test_agent")
        
        # Dodanie danych
        strategy = create_strategy(
            agent_owner="serialization_test_agent",
            name="Serialization Strategy"
        )
        lab.add_strategy(strategy)
        
        # Serializacja
        lab_dict = lab.to_dict()
        self.assertIn('agent_id', lab_dict)
        self.assertIn('strategies', lab_dict)
        
        # Deserializacja
        restored_lab = AgentStrategyLaboratory.from_dict(lab_dict)
        self.assertEqual(restored_lab.agent_id, lab.agent_id)
        self.assertEqual(len(restored_lab.strategies), 1)
        
        # JSON
        json_str = lab.to_json()
        self.assertIsInstance(json_str, str)
        
        from_json_lab = AgentStrategyLaboratory.from_json(json_str)
        self.assertEqual(from_json_lab.agent_id, lab.agent_id)
        
        print("✅ Test 6.4: Serializacja laboratorium - ZALICZONY")
    
    def test_memory_manager(self):
        """Test 6.5: Manager pamięci strategii."""
        # Utworzenie singletona
        memory = get_strategy_memory()
        
        # Sprawdzenie czy działa
        self.assertIsNotNone(memory)
        self.assertIsInstance(memory, StrategyMemory)
        
        # Utworzenie laboratorium
        lab = memory.get_or_create_lab("test_memory_manager_agent")
        self.assertIsNotNone(lab)
        self.assertEqual(lab.agent_id, "test_memory_manager_agent")
        
        print("✅ Test 6.5: Manager pamięci strategii - ZALICZONY")


class TestMemoryIntegrator(unittest.TestCase):
    """Testy Memory Integrator."""
    
    @classmethod
    def setUpClass(cls):
        """Inicjalizacja klasy testów."""
        cls.memory_integrator = StrategyMemoryIntegrator()
    
    def test_behavior_memory_entry(self):
        """Test 7.1: Tworzenie wpisu Behavior Memory."""
        strategy = create_strategy(
            agent_owner="test_agent_010",
            name="Behavior Test Strategy",
            strategy_type=StrategyType.DECISION
        )
        
        result = StrategyResult(
            strategy_id=strategy.strategy_id,
            success=True,
            score=0.85,
            confidence=0.9
        )
        
        entry = self.memory_integrator.create_behavior_memory_entry(strategy, result)
        
        self.assertEqual(entry['memory_type'], 'behavior_memory')
        self.assertEqual(entry['agent_id'], strategy.agent_owner)
        self.assertEqual(entry['strategy_id'], strategy.strategy_id)
        self.assertIn('behavior_type', entry)
        self.assertEqual(entry['success'], True)
        
        print("✅ Test 7.1: Tworzenie wpisu Behavior Memory - ZALICZONY")
    
    def test_decision_memory_entry(self):
        """Test 7.2: Tworzenie wpisu Decision Memory."""
        strategy = create_strategy(
            agent_owner="test_agent_011",
            name="Decision Test Strategy"
        )
        
        result = StrategyResult(
            strategy_id=strategy.strategy_id,
            success=True,
            score=0.8,
            confidence=0.85,
            input_data={'test': 'data'},
            output_data={'result': 'success'}
        )
        
        entry = self.memory_integrator.create_decision_memory_entry(strategy, result)
        
        self.assertEqual(entry['memory_type'], 'decision_layer_memory')
        self.assertEqual(entry['decision_outcome'], 'success')
        self.assertIn('input_data', entry)
        self.assertIn('output_data', entry)
        
        print("✅ Test 7.2: Tworzenie wpisu Decision Memory - ZALICZONY")
    
    def test_agent_analysis_entry(self):
        """Test 7.3: Tworzenie wpisu Agent Analysis Memory."""
        strategy = create_strategy(
            agent_owner="test_agent_012",
            name="Analysis Test Strategy",
            success_rate=0.8,
            confidence=0.85
        )
        
        evaluation = StrategyEvaluation(
            strategy_id=strategy.strategy_id,
            evaluator_agent_id="evaluator_002",
            effectiveness=0.8,
            stability=0.75,
            efficiency=0.85,
            reliability=0.9,
            adaptability=0.7,
            confidence=0.85
        )
        
        entry = self.memory_integrator.create_agent_analysis_entry(strategy, evaluation)
        
        self.assertEqual(entry['memory_type'], 'agent_analysis_memory')
        self.assertEqual(entry['analysis_type'], 'BEHAVIOR')
        self.assertIn('effectiveness', entry)
        self.assertIn('strengths', entry)
        
        print("✅ Test 7.3: Tworzenie wpisu Agent Analysis Memory - ZALICZONY")
    
    def test_ranking_analysis_entry(self):
        """Test 7.4: Tworzenie wpisu rankingu do analizy."""
        strategy = create_strategy(
            agent_owner="test_agent_013",
            name="Ranking Analysis Strategy",
            success_rate=0.85,
            ranking_score=0.75
        )
        
        ranking = StrategyRanking(
            strategy_id=strategy.strategy_id,
            rank=2,
            total_strategies=10,
            percentile=0.8
        )
        
        entry = self.memory_integrator.create_ranking_analysis_entry(strategy, ranking)
        
        self.assertEqual(entry['memory_type'], 'agent_analysis_memory')
        self.assertEqual(entry['rank'], 2)
        self.assertIn('ranking_score', entry)
        
        print("✅ Test 7.4: Tworzenie wpisu rankingu do analizy - ZALICZONY")
    
    def test_memory_update_from_result(self):
        """Test 7.5: Aktualizacja pamięci z wyniku strategii."""
        strategy = create_strategy(
            agent_owner="test_agent_014",
            name="Update From Result Strategy",
            strategy_type=StrategyType.DECISION
        )
        
        result = StrategyResult(
            strategy_id=strategy.strategy_id,
            success=True,
            score=0.8,
            confidence=0.9
        )
        
        entries = self.memory_integrator.update_from_strategy_result(strategy, result)
        
        self.assertGreaterEqual(len(entries), 1)
        memory_types = [entry['memory_type'] for entry in entries]
        self.assertIn('behavior_memory', memory_types)
        self.assertIn('decision_layer_memory', memory_types)
        
        print("✅ Test 7.5: Aktualizacja pamięci z wyniku strategii - ZALICZONY")


class TestIFCIntegrator(unittest.TestCase):
    """Testy IFC Integrator."""
    
    def test_message_creation(self):
        """Test 8.1: Tworzenie wiadomości IFC."""
        # Reset singletona dla testów
        from .ifc_integrator import _ifc_integrator
        from .ifc_integrator import _ifc_integrator_lock
        
        with _ifc_integrator_lock:
            # Utworzenie nowej instancji
            integrator = StrategyIFCIntegrator(IFCIntegratorConfig(use_ifc=False))
        
        # Tworzenie wiadomości
        message = integrator.create_strategy_message(
            agent_id="test_agent_ifc",
            strategy_data={
                'name': 'IFC Test Strategy',
                'strategy_type': 'DECISION'
            }
        )
        
        self.assertIsNotNone(message)
        self.assertEqual(message.sender, 'strategy_laboratory')
        self.assertEqual(message.process_type, ProcessType.STRATEGY_CREATE)
        self.assertIn('strategy_data', message.data)
        
        print("✅ Test 8.1: Tworzenie wiadomości IFC - ZALICZONY")
    
    def test_send_message_without_ifc(self):
        """Test 8.2: Wysyłanie wiadomości bez IFC (symulacja)."""
        from .ifc_integrator import _ifc_integrator
        from .ifc_integrator import _ifc_integrator_lock
        
        with _ifc_integrator_lock:
            integrator = StrategyIFCIntegrator(IFCIntegratorConfig(use_ifc=False))
        
        message = integrator.create_strategy_message(
            agent_id="test_agent_ifc_002",
            strategy_data={'name': 'Test'}
        )
        
        response = integrator.send_message(message)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status, MessageStatus.PROCESSED)
        self.assertIn('simulated', response.response_data)
        
        print("✅ Test 8.2: Wysyłanie wiadomości bez IFC - ZALICZONY")
    
    def test_high_level_create_strategy(self):
        """Test 8.3: Wysokopoziomowe tworzenie strategii."""
        from .ifc_integrator import _ifc_integrator
        from .ifc_integrator import _ifc_integrator_lock
        
        with _ifc_integrator_lock:
            integrator = StrategyIFCIntegrator(IFCIntegratorConfig(use_ifc=False))
        
        response = integrator.create_strategy(
            agent_id="test_agent_ifc_003",
            name="High Level Test Strategy",
            strategy_type=StrategyType.DECISION,
            description="Test description"
        )
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status, MessageStatus.PROCESSED)
        
        print("✅ Test 8.3: Wysokopoziomowe tworzenie strategii - ZALICZONY")
    
    def test_high_level_ranking(self):
        """Test 8.4: Wysokopoziomowe ranking strategii."""
        from .ifc_integrator import _ifc_integrator
        from .ifc_integrator import _ifc_integrator_lock
        
        with _ifc_integrator_lock:
            integrator = StrategyIFCIntegrator(IFCIntegratorConfig(use_ifc=False))
        
        response = integrator.rank_strategies(
            agent_id="test_agent_ifc_004",
            limit=10
        )
        
        self.assertIsNotNone(response)
        
        print("✅ Test 8.4: Wysokopoziomowe ranking strategii - ZALICZONY")
    
    def test_get_statistics(self):
        """Test 8.5: Pobieranie statystyk integratora."""
        from .ifc_integrator import _ifc_integrator
        from .ifc_integrator import _ifc_integrator_lock
        
        with _ifc_integrator_lock:
            integrator = StrategyIFCIntegrator(IFCIntegratorConfig(use_ifc=False))
        
        # Wysłanie kilku wiadomości
        for i in range(3):
            message = integrator.create_strategy_message(
                agent_id=f"test_agent_stats_{i}",
                strategy_data={'name': f'Stats Test {i}'}
            )
            integrator.send_message(message)
        
        stats = integrator.get_statistics()
        
        self.assertIn('messages_sent', stats)
        self.assertEqual(stats['messages_sent'], 3)
        self.assertIn('config', stats)
        
        print("✅ Test 8.5: Pobieranie statystyk integratora - ZALICZONY")


class TestIntegration(unittest.TestCase):
    """Testy integracyjne."""
    
    def test_full_workflow(self):
        """Test 9.1: Test pełnego workflow."""
        # Utworzenie managerów
        strategy_manager = StrategyManager(StrategyManagerConfig(
            enable_validation=True,
            max_strategies_per_agent=100
        ))
        
        experiment_manager = ExperimentManager(ExperimentManagerConfig(
            enable_validation=True,
            max_experiments_per_agent=50
        ))
        
        ranking_engine = StrategyRankingEngine()
        memory_integrator = StrategyMemoryIntegrator()
        
        # 1. Utworzenie strategii
        strategy = strategy_manager.create_strategy(
            agent_owner="workflow_agent",
            name="Workflow Test Strategy",
            description="Full workflow test"
        )
        
        self.assertIsNotNone(strategy)
        
        # 2. Utworzenie eksperymentu
        experiment = experiment_manager.create_experiment(
            agent_owner="workflow_agent",
            name="Workflow Test Experiment",
            strategy_id=strategy.strategy_id
        )
        
        self.assertIsNotNone(experiment)
        
        # 3. Uruchomienie eksperymentu
        updated_experiment, result = experiment_manager.run_experiment(experiment.experiment_id)
        
        self.assertIsNotNone(result)
        
        # 4. Aktualizacja strategii na podstawie wyniku
        strategy = strategy_manager.update_strategy_stats(strategy, result)
        
        # 5. Ocena strategii
        updated_strategy, evaluation = strategy_manager.evaluate_strategy(
            strategy_id=strategy.strategy_id,
            evaluator_agent_id="evaluator_workflow",
            effectiveness=0.8,
            stability=0.7,
            efficiency=0.85,
            reliability=0.9,
            adaptability=0.75,
            confidence=0.85
        )
        
        self.assertIsNotNone(evaluation)
        
        # 6. Ranking strategii
        rankings = strategy_manager.rank_strategies(agent_id="workflow_agent")
        
        self.assertGreaterEqual(len(rankings), 1)
        
        # 7. Aktualizacja pamięci
        memory_entries = memory_integrator.update_from_strategy_result(strategy, result)
        self.assertGreaterEqual(len(memory_entries), 1)
        
        # 8. Archiwizacja strategii
        archived_strategy = strategy_manager.archive_strategy(
            strategy_id=strategy.strategy_id,
            reason="Workflow test complete"
        )
        
        self.assertEqual(archived_strategy.status, StrategyStatus.ARCHIVED)
        
        print("✅ Test 9.1: Pełny workflow - ZALICZONY")
    
    def test_data_persistence(self):
        """Test 9.2: Test persistencji danych."""
        # Połączenie kontaktów z pamięcią
        memory = StrategyMemory(StrategyMemoryConfig(
            persistence_enabled=False  # Wyłącz为了 testów
        ))
        
        # Utworzenie laboratorium
        lab = memory.get_or_create_lab("persistence_test_agent")
        
        # Dodanie strategii
        strategy = create_strategy(
            agent_owner="persistence_test_agent",
            name="Persistence Test Strategy"
        )
        lab.add_strategy(strategy)
        
        # Dodanie eksperymentu
        experiment = create_experiment(
            agent_owner="persistence_test_agent",
            name="Persistence Test Experiment",
            strategy_id=strategy.strategy_id
        )
        lab.add_experiment(experiment)
        
        # Sprawdzenie stanu
        self.assertEqual(lab.total_strategies, 1)
        self.assertEqual(lab.total_experiments, 1)
        
        # Serializacja i deserializacja
        lab_dict = lab.to_dict()
        restored_lab = AgentStrategyLaboratory.from_dict(lab_dict)
        
        self.assertEqual(restored_lab.total_strategies, 1)
        self.assertEqual(restored_lab.total_experiments, 1)
        
        print("✅ Test 9.2: Persistencja danych - ZALICZONY")


def run_all_tests():
    """Uruchomienie wszystkich testów."""
    print("\n" + "="*80)
    print("SSI V5 - STRATEGY LABORATORY - ETAP 2.3")
    print("ROZPOCZĘCIE TESTÓW")
    print("="*80 + "\n")
    
    # Utworzenie test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Dodanie wszystkich testów
    test_classes = [
        TestStrategyModels,
        TestExperimentModels,
        TestStrategyManager,
        TestExperimentManager,
        TestStrategyRankingEngine,
        TestStrategyMemory,
        TestMemoryIntegrator,
        TestIFCIntegrator,
        TestIntegration
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Uruchomienie testów
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Podsumowanie
    print("\n" + "="*80)
    print("PODSUMOWANIE TESTÓW")
    print("="*80)
    print(f"Testy uruchomione: {result.testsRun}")
    print(f"Sukcesy: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Porażki: {len(result.failures)}")
    print(f"Błędy: {len(result.errors)}")
    print(f"Czas: {result.testsRun} testów w {result.time:.2f}s")
    
    if result.wasSuccessful():
        print("\n🎯 Wszystkie testy ZALICZONE!")
        print("✅ ETAP 2.3 - Strategy Laboratory - GOTOWY")
    else:
        print("\n❌ Niektóre testy NIE ZALICZONE")
        if result.failures:
            print("\nPorażki:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\nBłędy:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    print("="*80 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


# Eksport dla zewnętrznych testów
__all__ = [
    'run_all_tests',
    'TestStrategyModels',
    'TestExperimentModels', 
    'TestStrategyManager',
    'TestExperimentManager',
    'TestStrategyRankingEngine',
    'TestStrategyMemory',
    'TestMemoryIntegrator',
    'TestIFCIntegrator',
    'TestIntegration'
]
