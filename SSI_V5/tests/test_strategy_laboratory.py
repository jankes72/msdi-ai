# SSI V5 Tests - Strategy Laboratory
# ============================================
# ETAP: 5.2.6.1 - Strategy Laboratory Foundation
#
# Testy dla izolowanego srodowiska testowego strategii.
#
# ZASADY:
# - Laboratorium NIE modyfikuje produkcji
# - Laboratorium korzysta z kopii danych
# - Wyniki sa niezalezne

import copy
import json
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from SSI_V5.laboratory.strategy_laboratory import (
    StrategyLab,
    StrategyExperiment,
    ExperimentStatus
)


class TestStrategyLaboratory(unittest.TestCase):
    """Testy dla Strategy Laboratory"""

    def setUp(self):
        """Przygotowanie przed kazdym testem"""
        # Tworzymy tymczasowy katalog dla testow
        self.test_dir = tempfile.mkdtemp()
        self.history_dir = Path(self.test_dir) / "history"
        
        # Testowy world snapshot
        self.world_snapshot = {
            "version": "world_v1",
            "matches": ["match_1", "match_2", "match_3"],
            "generated_at": datetime.now().isoformat(),
            "metadata": {"league": "test_league"}
        }
        
        # Kopia do sprawdzenia izolacji
        self.world_snapshot_copy = copy.deepcopy(self.world_snapshot)
        
        # Testowy dataset
        self.dataset = {
            "version": "dataset_v1",
            "size": 1000,
            "features": ["feature_1", "feature_2", "feature_3"]
        }
        
        # Tworzymy laboratorium z tymczasowym katalogiem historii
        self.lab = StrategyLab(
            lab_name="TEST_LAB",
            history_dir=str(self.history_dir)
        )

    def tearDown(self):
        """Sprzatanie po testach"""
        # Usun tymczasowy katalog
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ===== TESTY PODSTAWOWE =====

    def test_laboratory_creation(self):
        """Test: Tworzenie laboratorium"""
        self.assertIsInstance(self.lab, StrategyLab)
        self.assertEqual(self.lab.lab_name, "TEST_LAB")
        self.assertEqual(len(self.lab.experiments), 0)
        self.assertEqual(len(self.lab.sessions), 0)

    def test_laboratory_repr(self):
        """Test: Reprezentacja tekstowa laboratorium"""
        repr_str = repr(self.lab)
        self.assertIn("StrategyLab", repr_str)
        self.assertIn("TEST_LAB", repr_str)

    # ===== TESTY EKSPERYMENTU =====

    def test_run_experiment(self):
        """Test: Uruchomienie pojedynczego eksperymentu"""
        experiment = self.lab.run_experiment(
            strategy_id="balanced",
            strategy_version="1.0.0",
            world_snapshot=self.world_snapshot,
            parameters={"risk_threshold": 0.5}
        )

        # Sprawdz podstawowe wlasciwosci
        self.assertIsInstance(experiment, StrategyExperiment)
        self.assertEqual(experiment.strategy_id, "balanced")
        self.assertEqual(experiment.strategy_version, "1.0.0")
        self.assertEqual(experiment.world_version, "world_v1")
        self.assertEqual(experiment.status, ExperimentStatus.COMPLETED)
        self.assertIsNotNone(experiment.experiment_id)
        self.assertIsNotNone(experiment.start_time)
        self.assertIsNotNone(experiment.end_time)

        # Sprawdz wyniki
        self.assertIn("simulated_accuracy", experiment.result)
        self.assertIn("simulated_roi", experiment.result)
        self.assertIn("decision_count", experiment.result)

        # Sprawdz metryki
        self.assertIn("accuracy", experiment.metrics)
        self.assertIn("roi", experiment.metrics)
        self.assertIn("simulated_accuracy", experiment.metrics)
        self.assertIn("simulated_roi", experiment.metrics)

    def test_run_experiment_with_dataset(self):
        """Test: Uruchomienie eksperymentu z datasetem"""
        experiment = self.lab.run_experiment(
            strategy_id="test_with_dataset",
            world_snapshot=self.world_snapshot,
            dataset=self.dataset
        )

        self.assertEqual(experiment.dataset_version, "dataset_v1")
        self.assertEqual(experiment.status, ExperimentStatus.COMPLETED)

    def test_run_experiment_with_features(self):
        """Test: Uruchomienie eksperymentu z features"""
        features = ["feature_a", "feature_b", "feature_c"]
        experiment = self.lab.run_experiment(
            strategy_id="test_features",
            world_snapshot=self.world_snapshot,
            features=features
        )

        self.assertEqual(experiment.features, features)

    def test_run_experiment_with_execution_context(self):
        """Test: Uruchomienie eksperymentu z execution_context"""
        context = {
            "engine": "SSI_V5_TEST",
            "environment": "laboratory",
            "random_seed": 42,
            "execution_mode": "test"
        }
        
        experiment = self.lab.run_experiment(
            strategy_id="test_context",
            world_snapshot=self.world_snapshot,
            execution_context=context
        )

        self.assertEqual(experiment.execution_context, context)

    def test_run_experiment_batch(self):
        """Test: Uruchomienie serii eksperymentow"""
        variants = [
            {"strategy_id": "strategy_1", "parameters": {"param": 0.1}},
            {"strategy_id": "strategy_2", "parameters": {"param": 0.5}},
            {"strategy_id": "strategy_3", "parameters": {"param": 0.9}}
        ]

        experiments = self.lab.run_experiment_batch(
            strategy_variants=variants,
            world_snapshot=self.world_snapshot,
            lab_session_id="test_batch"
        )

        self.assertEqual(len(experiments), 3)
        self.assertEqual(len(self.lab.sessions["test_batch"]), 3)

        # Sprawdz, ze wszystkie maja ten sam lab_session_id
        for exp in experiments:
            self.assertEqual(exp.lab_session_id, "test_batch")
            self.assertEqual(exp.status, ExperimentStatus.COMPLETED)

    # ===== TESTY POROWNANIA =====

    def test_compare_variants(self):
        """Test: Porownanie wariantow"""
        variants = [
            {"strategy_id": f"strategy_{i}", "parameters": {"risk": i * 0.1}}
            for i in range(1, 4)
        ]

        experiments = self.lab.run_experiment_batch(
            strategy_variants=variants,
            world_snapshot=self.world_snapshot
        )

        comparison = self.lab.compare_variants(
            experiments=experiments,
            metric="accuracy"
        )

        self.assertIn("ranking", comparison)
        self.assertIn("statistics", comparison)
        self.assertEqual(len(comparison["ranking"]), 3)
        self.assertEqual(comparison["metric"], "accuracy")

    def test_compare_variants_empty(self):
        """Test: Porownanie pustej listy"""
        comparison = self.lab.compare_variants(experiments=[])
        self.assertIn("error", comparison)

    def test_compare_variants_no_completed(self):
        """Test: Porownanie z nieukonczonymi eksperymentami"""
        # Utworz nieukonczony eksperyment
        incomplete_exp = StrategyExperiment(
            strategy_id="incomplete",
            world_version="test"
        )
        incomplete_exp.status = ExperimentStatus.RUNNING
        
        comparison = self.lab.compare_variants(experiments=[incomplete_exp])
        self.assertIn("error", comparison)

    # ===== TESTY OCENY JAKOSCI =====

    def test_evaluate_quality(self):
        """Test: Ocena jakości eksperymentu"""
        experiment = self.lab.run_experiment(
            strategy_id="quality_test",
            world_snapshot=self.world_snapshot
        )

        evaluation = self.lab.evaluate_quality(experiment)

        self.assertIn("quality_score", evaluation)
        self.assertIn("quality_rating", evaluation)
        self.assertIn("recommendation", evaluation)
        self.assertIn("details", evaluation)
        self.assertEqual(evaluation["recommendation"], "ACCEPT")

    def test_evaluate_quality_incomplete(self):
        """Test: Ocena jakości nieukonczonego eksperymentu"""
        incomplete_exp = StrategyExperiment(
            strategy_id="incomplete",
            world_version="test"
        )
        incomplete_exp.status = ExperimentStatus.RUNNING
        
        evaluation = self.lab.evaluate_quality(incomplete_exp)
        self.assertIn("error", evaluation)

    # ===== TEST IZOLACJI (CRITICAL) =====

    def test_isolation_no_modification(self):
        """
        Test: IZOLACJA - Laboratorium nie modyfikuje wejscia
        
        WEZNE: Sprawdzamy, czy world_snapshot pozostal niezmieniony
        po wywolaniu run_experiment()
        """
        # Zapamietaj stan przed eksperymentem
        world_before = copy.deepcopy(self.world_snapshot)

        # Uruchom eksperyment
        self.lab.run_experiment(
            strategy_id="isolation_test",
            world_snapshot=self.world_snapshot
        )

        # ✅ Sprawdz, czy world_snapshot pozostal niezmieniony
        self.assertEqual(self.world_snapshot, world_before)

    def test_isolation_no_dataset_modification(self):
        """Test: IZOLACJA - Laboratorium nie modyfikuje datasetu"""
        dataset_before = copy.deepcopy(self.dataset)

        self.lab.run_experiment(
            strategy_id="dataset_test",
            world_snapshot=self.world_snapshot,
            dataset=self.dataset
        )

        self.assertEqual(self.dataset, dataset_before)

    def test_isolation_no_parameters_modification(self):
        """Test: IZOLACJA - Laboratorium nie modyfikuje parametrow"""
        params = {"risk_threshold": 0.5, "learning_rate": 0.1}
        params_before = copy.deepcopy(params)

        self.lab.run_experiment(
            strategy_id="params_test",
            world_snapshot=self.world_snapshot,
            parameters=params
        )

        self.assertEqual(params, params_before)

    def test_isolation_multiple_experiments(self):
        """Test: IZOLACJA - Wielokrotne eksperymenty nie modyfikuja wejsc"""
        world_before = copy.deepcopy(self.world_snapshot)

        # Uruchom wiecej eksperymentow
        for i in range(5):
            self.lab.run_experiment(
                strategy_id=f"test_{i}",
                world_snapshot=self.world_snapshot
            )

        self.assertEqual(self.world_snapshot, world_before)

    # ===== TESTY ZAPISU I ODCZYTU =====

    def test_save_and_retrieve_experiment(self):
        """Test: Zapis i odzysk eksperymentu"""
        experiment = self.lab.run_experiment(
            strategy_id="persist_test",
            world_snapshot=self.world_snapshot
        )

        # Zapisz do historii
        self.assertTrue(self.lab.save_experiment(experiment))

        # Odzyskaj po ID
        retrieved = self.lab.get_experiment(experiment.experiment_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.strategy_id, experiment.strategy_id)
        self.assertEqual(retrieved.status, ExperimentStatus.COMPLETED)

    def test_get_nonexistent_experiment(self):
        """Test: Pobranie nieistniejacego eksperymentu"""
        result = self.lab.get_experiment("nonexistent_id")
        self.assertIsNone(result)

    def test_get_lab_history(self):
        """Test: Pobranie pelnej historii laboratorium"""
        # Uruchom kilka eksperymentow
        for i in range(3):
            self.lab.run_experiment(
                strategy_id=f"history_test_{i}",
                world_snapshot=self.world_snapshot
            )

        history = self.lab.get_lab_history()
        self.assertEqual(len(history), 3)

    def test_get_session_experiments(self):
        """Test: Pobranie eksperymentow z sesji"""
        session_id = "session_test"
        
        # Uruchom eksperymenty w sesji
        for i in range(3):
            self.lab.run_experiment(
                strategy_id=f"session_test_{i}",
                world_snapshot=self.world_snapshot,
                lab_session_id=session_id
            )

        session_experiments = self.lab.get_session_experiments(session_id)
        self.assertEqual(len(session_experiments), 3)

    def test_clear_lab_history(self):
        """Test: Wyczyszczenie historii laboratorium"""
        # Dodaj eksperymenty
        for i in range(3):
            self.lab.run_experiment(
                strategy_id=f"to_clear_{i}",
                world_snapshot=self.world_snapshot
            )

        self.assertEqual(len(self.lab.experiments), 3)

        # Wyczysc
        self.lab.clear_lab_history()
        self.assertEqual(len(self.lab.experiments), 0)
        self.assertEqual(len(self.lab.sessions), 0)

    # ===== TESTY HISTORII NA DYSKU =====

    def test_save_to_disk(self):
        """Test: Zapis historii na dysk"""
        experiment = self.lab.run_experiment(
            strategy_id="disk_test",
            world_snapshot=self.world_snapshot
        )

        # History file should exist
        self.assertTrue(self.lab.history_file.exists())

        # Load and verify content
        with open(self.lab.history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertIn("experiments", data)
        self.assertEqual(len(data["experiments"]), 1)
        self.assertEqual(data["experiments"][0]["strategy_id"], "disk_test")

    def test_load_from_disk(self):
        """Test: Wczytanie historii z dysku"""
        # Uruchom eksperyment i zapisz
        self.lab.run_experiment(
            strategy_id="load_test",
            world_snapshot=self.world_snapshot
        )

        # Utworz nowe laboratorium i wczytaj historię
        new_lab = StrategyLab(
            lab_name="TEST_LAB",
            history_dir=str(self.history_dir)
        )

        self.assertEqual(len(new_lab.experiments), 1)
        loaded_exp = list(new_lab.experiments.values())[0]
        self.assertEqual(loaded_exp.strategy_id, "load_test")

    # ===== TESTY STRATEGYEXPERIMENT ENTRY =====

    def test_experiment_to_dict(self):
        """Test: Konwersja eksperymentu do slownika"""
        experiment = self.lab.run_experiment(
            strategy_id="to_dict_test",
            world_snapshot=self.world_snapshot
        )

        exp_dict = experiment.to_dict()
        
        self.assertIn("experiment_id", exp_dict)
        self.assertIn("strategy_id", exp_dict)
        self.assertIn("status", exp_dict)
        self.assertIn("result", exp_dict)
        self.assertIn("metrics", exp_dict)
        self.assertIn("execution_context", exp_dict)

    def test_experiment_from_dict(self):
        """Test: Tworzenie eksperymentu z slownika"""
        original = self.lab.run_experiment(
            strategy_id="from_dict_test",
            world_snapshot=self.world_snapshot
        )
        
        exp_dict = original.to_dict()
        restored = StrategyExperiment.from_dict(exp_dict)
        
        self.assertEqual(restored.strategy_id, original.strategy_id)
        self.assertEqual(restored.status, original.status)
        self.assertEqual(restored.metrics, original.metrics)

    def test_experiment_mark_failed(self):
        """Test: Zaznaczenie eksperymentu jako nieudany"""
        experiment = StrategyExperiment(
            strategy_id="fail_test",
            world_version="test"
        )
        
        experiment.mark_failed("Test error")
        
        self.assertEqual(experiment.status, ExperimentStatus.FAILED)
        self.assertEqual(experiment.error, "Test error")
        self.assertIsNotNone(experiment.end_time)


class TestStrategyExperimentIsolation(unittest.TestCase):
    """Testy izolacji StrategyExperiment"""

    def test_experiment_has_required_fields(self):
        """Test: Eksperyment ma wymagane pola"""
        # Utworz eksperyment
        experiment = StrategyExperiment(
            strategy_id="test",
            world_version="v1",
            execution_context={"mode": "test"}
        )
        
        # Zaznacz jako ukonczony
        experiment.mark_completed(
            result={"accuracy": 0.8},
            metrics={"accuracy": 0.8}
        )
        
        # Sprawdz, ze pola sa ustawione
        self.assertEqual(experiment.status, ExperimentStatus.COMPLETED)
        self.assertEqual(experiment.result, {"accuracy": 0.8})
        self.assertEqual(experiment.strategy_id, "test")
        self.assertEqual(experiment.world_version, "v1")
        self.assertIsNotNone(experiment.experiment_id)
        self.assertIsNotNone(experiment.start_time)
        self.assertIsNotNone(experiment.end_time)


if __name__ == "__main__":
    unittest.main()
