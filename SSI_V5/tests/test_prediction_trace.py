# SSI V5 Test Suite - Prediction Trace Engine Foundation
# ==========================================================
#
# ETAP: 5.2.6.3 - Prediction Trace Engine Foundation
# Data: 2026-08-04
#
# Kompletny zestaw testów dla Prediction Trace Engine.
# Testuje wszystkie kluczowe funkcjonalności modułu trace.
#
# Autor: Mistral Vibe
# Co-Authored-By: Mistral Vibe <vibe@mistral.ai>

import unittest
import tempfile
import shutil
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
import copy

# Import trace components
from SSI_V5.trace.prediction_trace import (
    PredictionTraceRecord,
    PredictionTraceManager,
    TraceStatus,
    PredictionType,
    InputDataReference,
    ModelReference,
    PredictionResult,
    DecisionReference,
    CollectiveReference,
    TraceContext,
    create_trace_from_strategy_experiment
)

# Import integration components
from SSI_V5.trace.trace_integration import (
    TraceHook,
    WorldEngineHook,
    StrategyLabHook,
    AgentRuntimeHook,
    CollectiveManagerHook,
    ModelEvaluatorHook,
    TraceIntegrationManager,
    create_integration_manager,
    quick_setup
)


class TestInputDataReference(unittest.TestCase):
    """Testy dla InputDataReference - reprodukowalność danych wejściowych"""
    
    def test_from_data_creates_valid_hash(self):
        """Test tworzenia Referencji z danych"""
        test_data = {"feature1": 0.5, "feature2": 0.8, "feature3": 0.3}
        ref = InputDataReference.from_data(test_data, "test_source")
        
        self.assertNotEqual(ref.data_hash, "")
        self.assertEqual(ref.hash_algorithm, "sha256")
        self.assertEqual(ref.source, "test_source")
        self.assertEqual(ref.feature_count, 3)
        self.assertEqual(ref.sample_count, 0)  # Brak list
    
    def test_data_verification_success(self):
        """Test weryfikacji danych - sukces"""
        test_data = {"feature1": 0.5, "feature2": 0.8}
        ref = InputDataReference.from_data(test_data, "test")
        
        self.assertTrue(ref.verify_data(test_data))
    
    def test_data_verification_failure(self):
        """Test weryfikacji danych - niepowodzenie"""
        test_data = {"feature1": 0.5, "feature2": 0.8}
        ref = InputDataReference.from_data(test_data, "test")
        
        different_data = {"feature1": 0.5, "feature2": 0.9}
        self.assertFalse(ref.verify_data(different_data))
    
    def test_data_verification_with_list(self):
        """Test weryfikacji danych z listami"""
        test_data = [{"f1": 0.1}, {"f1": 0.2}, {"f1": 0.3}]
        ref = InputDataReference.from_data(test_data, "list_source")
        
        self.assertTrue(ref.verify_data(test_data))
        self.assertEqual(ref.feature_count, 1)  # Jeden feature w każdym elementcie
        self.assertEqual(ref.sample_count, 3)   # 3 elementy
    
    def test_empty_data_hash(self):
        """Test puste referencji"""
        ref = InputDataReference()
        self.assertEqual(ref.data_hash, "")
        self.assertFalse(ref.verify_data({"test": "data"}))


class TestModelReference(unittest.TestCase):
    """Testy dla ModelReference - referencja do modelu"""
    
    def test_model_identifier_generation(self):
        """Test generacji identyfikatora modelu"""
        model_ref = ModelReference(
            reference="xgboost_v1",
            version="2.0.0",
            parameters={"max_depth": 5, "learning_rate": 0.1}
        )
        
        identifier = model_ref.get_identifier()
        self.assertEqual(identifier, "xgboost_v1@2.0.0")
    
    def test_to_dict_serialization(self):
        """Test serializacji ModelReference do dict"""
        model_ref = ModelReference(
            reference="random_forest",
            version="1.5.0",
            parameters={"n_estimators": 100},
            model_type="classifier",
            trainingTimestamp="2026-08-04T10:00:00",
            performance={"accuracy": 0.95}
        )
        
        data = model_ref.to_dict()
        
        self.assertEqual(data['reference'], "random_forest")
        self.assertEqual(data['version'], "1.5.0")
        self.assertEqual(data['parameters']['n_estimators'], 100)
        self.assertEqual(data['model_type'], "classifier")
        self.assertIn('performance', data)
    
    def test_from_dict_deserialization(self):
        """Test deserializacji ModelReference z dict"""
        data = {
            'reference': 'svm_model',
            'version': '3.0.0',
            'parameters': {'C': 1.0, 'kernel': 'rbf'},
            'model_type': 'classifier',
            'training_timestamp': '2026-08-04T10:00:00',
            'performance': {'accuracy': 0.88}
        }
        
        model_ref = ModelReference.from_dict(data)
        
        self.assertEqual(model_ref.reference, "svm_model")
        self.assertEqual(model_ref.version, "3.0.0")
        self.assertEqual(model_ref.parameters['C'], 1.0)
        self.assertEqual(model_ref.model_type, "classifier")


class TestPredictionResult(unittest.TestCase):
    """Testy dla PredictionResult - wynik predykcji"""
    
    def test_serialization_roundtrip(self):
        """Test pełnego cyklu serializacji/deserializacji"""
        original = PredictionResult(
            result="HOME_WIN",
            confidence=0.75,
            prediction_type=PredictionType.CLASSIFICATION,
            probabilities={"HOME_WIN": 0.75, "AWAY_WIN": 0.20, "DRAW": 0.05},
            raw_output=None,
            model_output={"output": [0.75, 0.20, 0.05]}
        )
        
        # Serializacja
        serialized = original.to_serializable()
        
        # Deserializacja
        deserialized = PredictionResult.from_serializable(serialized)
        
        self.assertEqual(deserialized.result, "HOME_WIN")
        self.assertEqual(deserialized.confidence, 0.75)
        self.assertEqual(deserialized.prediction_type, PredictionType.CLASSIFICATION)
        self.assertEqual(deserialized.probabilities["HOME_WIN"], 0.75)
    
    def test_different_prediction_types(self):
        """Test różnych typów predykcji"""
        for pred_type in [PredictionType.CLASSIFICATION, PredictionType.REGRESSION, 
                         PredictionType.PROBABILITY, PredictionType.BINARY, 
                         PredictionType.MULTICLASS, PredictionType.RANKING]:
            result = PredictionResult(prediction_type=pred_type)
            serialized = result.to_serializable()
            deserialized = PredictionResult.from_serializable(serialized)
            self.assertEqual(deserialized.prediction_type, pred_type)


class TestTraceContext(unittest.TestCase):
    """Testy dla TraceContext - kontekst śladu"""
    
    def test_context_to_dict_with_timestamps(self):
        """Test serializacji kontekstu z timestampami"""
        now = datetime.now()
        context = TraceContext(
            world_version="world_v1",
            world_name="test_world",
            dataset_version="data_v2",
            cycle_id="cycle_123",
            created_timestamp=now,
            prediction_timestamp=now,
            completion_timestamp=now,
            world_snapshot_hash="abc123def456"
        )
        
        data = context.to_dict()
        
        self.assertEqual(data['world_version'], "world_v1")
        self.assertEqual(data['world_name'], "test_world")
        self.assertEqual(data['dataset_version'], "data_v2")
        self.assertEqual(data['cycle_id'], "cycle_123")
        self.assertEqual(data['world_snapshot_hash'], "abc123def456")
        self.assertIsNotNone(data['created_timestamp'])
    
    def test_context_from_dict_roundtrip(self):
        """Test pełnego cyklu kontekstu"""
        original = TraceContext(
            world_version="v1.0",
            world_name="production",
            dataset_version="data_v3",
            cycle_id="prod_cycle_001",
            world_snapshot_hash="hash123"
        )
        
        data = original.to_dict()
        restored = TraceContext.from_dict(data)
        
        self.assertEqual(restored.world_version, original.world_version)
        self.assertEqual(restored.world_name, original.world_name)
        self.assertEqual(restored.dataset_version, original.dataset_version)
        self.assertEqual(restored.cycle_id, original.cycle_id)
        self.assertEqual(restored.world_snapshot_hash, original.world_snapshot_hash)


class TestDecisionReference(unittest.TestCase):
    """Testy dla DecisionReference - referencja do decyzji"""
    
    def test_decision_to_dict(self):
        """Test serializacji decyzji"""
        decision = DecisionReference(
            decision_id="dec_123",
            agent_id="agent_456",
            strategy_id="strategy_789",
            decision_type="bet",
            bet_amount=50.0,
            bet_type="SINGLE",
            odds=1.85,
            confidence=0.75,
            decision_timestamp="2026-08-04T10:00:00"
        )
        
        data = decision.to_dict()
        
        self.assertEqual(data['decision_id'], "dec_123")
        self.assertEqual(data['agent_id'], "agent_456")
        self.assertEqual(data['bet_amount'], 50.0)
        self.assertEqual(data['odds'], 1.85)
    
    def test_decision_from_dict_roundtrip(self):
        """Test pełnego cyklu decyzji"""
        original = DecisionReference(
            decision_id="dec_test",
            agent_id="agent_test",
            strategy_id="strategy_test",
            decision_type="coupon",
            bet_amount=100.0,
            bet_type="MULTIPLE",
            odds=2.5,
            confidence=0.8
        )
        
        data = original.to_dict()
        restored = DecisionReference.from_dict(data)
        
        self.assertEqual(restored.decision_id, original.decision_id)
        self.assertEqual(restored.agent_id, original.agent_id)
        self.assertEqual(restored.bet_amount, original.bet_amount)
        self.assertEqual(restored.confidence, original.confidence)


class TestCollectiveReference(unittest.TestCase):
    """Testy dla CollectiveReference - referencja do konsensusu"""
    
    def test_collective_to_dict(self):
        """Test serializacji konsensusu"""
        collective = CollectiveReference(
            collective_decision_id="coll_123",
            consensus_type="MAJORITY_VOTE",
            confidence_score=0.85,
            participating_agents=["agent_1", "agent_2", "agent_3"],
            consensus_result={"result": "HOME_WIN", "confidence": 0.85},
            collective_timestamp="2026-08-04T10:00:00"
        )
        
        data = collective.to_dict()
        
        self.assertEqual(data['collective_decision_id'], "coll_123")
        self.assertEqual(data['consensus_type'], "MAJORITY_VOTE")
        self.assertEqual(data['confidence_score'], 0.85)
        self.assertEqual(len(data['participating_agents']), 3)
        self.assertIn('consensus_result', data)
    
    def test_collective_from_dict_roundtrip(self):
        """Test pełnego cyklu konsensusu"""
        original = CollectiveReference(
            collective_decision_id="coll_test",
            consensus_type="WEIGHTED_AVERAGE",
            confidence_score=0.9,
            participating_agents=["agent_a", "agent_b"],
            consensus_result={"final_prediction": 0.75, "agents_count": 2}
        )
        
        data = original.to_dict()
        restored = CollectiveReference.from_dict(data)
        
        self.assertEqual(restored.collective_decision_id, original.collective_decision_id)
        self.assertEqual(restored.consensus_type, original.consensus_type)
        self.assertEqual(restored.confidence_score, original.confidence_score)
        self.assertEqual(restored.participating_agents, original.participating_agents)


class TestPredictionTraceRecord(unittest.TestCase):
    """Testy dla PredictionTraceRecord - główny rekord trace"""
    
    def test_record_creation_with_defaults(self):
        """Test tworzenia rekord z domyślnymi wartościami"""
        record = PredictionTraceRecord()
        
        self.assertTrue(record.trace_id.startswith("ptr_"))
        self.assertTrue(record.prediction_id.startswith("pred_"))
        self.assertEqual(record.status, TraceStatus.CREATED)
        self.assertEqual(record.completeness_score, 0.0)
    
    def test_record_creation_with_full_data(self):
        """Test tworzenia rekord z pełnymi danymi"""
        record = PredictionTraceRecord(
            context=TraceContext(
                world_version="world_v1",
                world_name="test_world",
                dataset_version="data_v1",
                cycle_id="cycle_001"
            ),
            model=ModelReference(
                reference="xgboost_v1",
                version="1.0.0",
                parameters={"max_depth": 5}
            ),
            input_features=["feature1", "feature2", "feature3"],
            feature_values={"feature1": 0.5, "feature2": 0.8, "feature3": 0.3},
            prediction=PredictionResult(
                result="HOME_WIN",
                confidence=0.75,
                prediction_type=PredictionType.CLASSIFICATION
            ),
            decision=DecisionReference(
                decision_id="dec_001",
                agent_id="agent_01",
                strategy_id="strategy_v1"
            ),
            strategy_experiment_id="exp_001",
            world_engine_cycle_id="cycle_001",
            evaluation_metrics={"accuracy": 0.85, "roi": 0.15}
        )
        
        self.assertEqual(record.context.world_version, "world_v1")
        self.assertEqual(record.model.get_identifier(), "xgboost_v1@1.0.0")
        self.assertEqual(len(record.input_features), 3)
        self.assertEqual(record.prediction.result, "HOME_WIN")
        self.assertEqual(record.decision.decision_id, "dec_001")
        self.assertEqual(record.strategy_experiment_id, "exp_001")
    
    def test_completeness_calculation_minimal(self):
        """Test obliczania kompletności - minimalne dane"""
        record = PredictionTraceRecord()
        completeness = record.calculate_completeness()
        
        # Powinien mieć minimalną kompletność (tylko trace_id i prediction_id)
        self.assertGreater(completeness, 0.0)
        self.assertLessEqual(completeness, 1.0)
    
    def test_completeness_calculation_full(self):
        """Test obliczania kompletności - pełne dane"""
        record = PredictionTraceRecord(
            context=TraceContext(
                world_version="world_v1",
                world_name="test_world",
                dataset_version="data_v1",
                cycle_id="cycle_001"
            ),
            model=ModelReference(
                reference="model_v1",
                version="2.0.0",
                parameters={"param": "value"}
            ),
            input_features=["f1", "f2"],
            feature_values={"f1": 1.0, "f2": 2.0},
            prediction=PredictionResult(
                result="WIN",
                confidence=0.9,
                prediction_type=PredictionType.CLASSIFICATION
            ),
            decision=DecisionReference(decision_id="dec_001", agent_id="agent_01"),
            collective=CollectiveReference(
                collective_decision_id="coll_001",
                consensus_type="MAJORITY",
                confidence_score=0.85,
                participating_agents=["agent_01", "agent_02"]
            ),
            strategy_experiment_id="exp_001",
            world_engine_cycle_id="cycle_001"
        )
        
        completeness = record.calculate_completeness()
        self.assertEqual(completeness, 1.0)  # Powinien być 100% kompletny
    
    def test_status_update_flow(self):
        """Test przebiegu aktualizacji statusu"""
        record = PredictionTraceRecord()
        
        # Początkowy status
        self.assertEqual(record.status, TraceStatus.CREATED)
        
        # Aktualizacja do PREDICTION_MADE
        record.update_status(TraceStatus.PREDICTION_MADE)
        self.assertEqual(record.status, TraceStatus.PREDICTION_MADE)
        self.assertIsNotNone(record.context.prediction_timestamp)
        
        # Aktualizacja do COMPLETE
        record.update_status(TraceStatus.COMPLETE)
        self.assertEqual(record.status, TraceStatus.COMPLETE)
        self.assertIsNotNone(record.context.completion_timestamp)
    
    def test_trace_chain_generation(self):
        """Test generowania łańcucha trace"""
        record = PredictionTraceRecord(
            context=TraceContext(
                world_version="v1.0",
                dataset_version="data_v1"
            ),
            model=ModelReference(reference="model_v1", version="1.0.0"),
            prediction=PredictionResult(result="HOME_WIN", confidence=0.75),
            decision=DecisionReference(decision_id="dec_001", agent_id="agent_01")
        )
        
        chain = record.get_trace_chain()
        
        self.assertIn("World:v1.0", chain)
        self.assertIn("Dataset:data_v1", chain)
        self.assertIn("Model:model_v1@1.0.0", chain)
        self.assertIn("Prediction:HOME_WIN", chain)
        self.assertIn("Decision:dec_001", chain)
        self.assertIn("→", chain)  # Powinien zawierać strzałki
    
    def test_serialization_to_dict(self):
        """Test serializacji rekord do dict"""
        record = PredictionTraceRecord(
            context=TraceContext(world_version="v1.0", dataset_version="data_v1"),
            model=ModelReference(reference="model_v1", version="1.0.0"),
            input_features=["f1"],
            feature_values={"f1": 1.0},
            prediction=PredictionResult(result="WIN", confidence=0.8)
        )
        
        data = record.to_dict()
        
        self.assertIn('trace_id', data)
        self.assertIn('prediction_id', data)
        self.assertIn('context', data)
        self.assertIn('model', data)
        self.assertIn('input_features', data)
        self.assertIn('feature_values', data)
        self.assertIn('prediction', data)
    
    def test_serialization_to_json(self):
        """Test serializacji rekord do JSON"""
        record = PredictionTraceRecord(
            context=TraceContext(world_version="v1.0"),
            model=ModelReference(reference="model_v1"),
            prediction=PredictionResult(result="WIN", confidence=0.8)
        )
        
        json_str = record.to_json()
        self.assertIsInstance(json_str, str)
        
        # Powinien dać się zdeserializować
        parsed = json.loads(json_str)
        self.assertIn('trace_id', parsed)
        self.assertIn('prediction_id', parsed)


class TestPredictionTraceManager(unittest.TestCase):
    """Testy dla PredictionTraceManager - menadżer śladów"""
    
    def setUp(self):
        """Setup dla testów manager"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PredictionTraceManager(trace_dir=self.temp_dir)
    
    def tearDown(self):
        """Cleanup"""
        self.manager.clear_all_traces()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_manager_initialization(self):
        """Test inicjalizacji managera"""
        self.assertEqual(len(self.manager.get_all_traces()), 0)
        self.assertTrue(hasattr(self.manager, '_trace_register'))
        self.assertTrue(hasattr(self.manager, '_lock'))
    
    def test_create_trace_basic(self):
        """Test tworzenia basic trace"""
        trace = self.manager.create_trace(
            world_version="world_v1",
            world_name="test_world",
            dataset_version="data_v1",
            cycle_id="cycle_001",
            model_reference="model_v1",
            model_version="1.0.0",
            input_features=["f1", "f2"],
            feature_values={"f1": 0.5, "f2": 0.8},
            input_data={"f1": 0.5, "f2": 0.8},
            prediction_result="HOME_WIN",
            prediction_confidence=0.75
        )
        
        self.assertIsNotNone(trace)
        self.assertEqual(len(self.manager.get_all_traces()), 1)
        self.assertTrue(trace.trace_id in self.manager._trace_register)
        self.assertEqual(trace.context.world_version, "world_v1")
        self.assertEqual(trace.model.reference, "model_v1")
    
    def test_get_trace_by_id(self):
        """Test pobierania trace po ID"""
        trace = self.manager.create_trace(
            world_version="v1.0",
            model_reference="model_v1",
            prediction_result="WIN"
        )
        
        retrieved = self.manager.get_trace(trace.trace_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.trace_id, trace.trace_id)
        
        # Test nieistniejącego ID
        self.assertIsNone(self.manager.get_trace("non_existent_id"))
    
    def test_get_trace_by_prediction_id(self):
        """Test pobierania trace po prediction_id"""
        trace = self.manager.create_trace(
            world_version="v1.0",
            model_reference="model_v1",
            prediction_result="WIN"
        )
        
        retrieved = self.manager.get_trace_by_prediction_id(trace.prediction_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.prediction_id, trace.prediction_id)
    
    def test_add_trace_decision(self):
        """Test dodawania decyzji do trace"""
        trace = self.manager.create_trace(
            world_version="v1.0",
            model_reference="model_v1",
            prediction_result="WIN"
        )
        
        success = self.manager.add_trace_decision(
            trace_id=trace.trace_id,
            decision_id="dec_001",
            agent_id="agent_01",
            strategy_id="strategy_v1",
            decision_type="bet",
            bet_amount=50.0,
            bet_type="SINGLE",
            odds=1.85,
            confidence=0.8
        )
        
        self.assertTrue(success)
        
        updated_trace = self.manager.get_trace(trace.trace_id)
        self.assertIsNotNone(updated_trace.decision)
        self.assertEqual(updated_trace.decision.decision_id, "dec_001")
        self.assertEqual(updated_trace.decision.agent_id, "agent_01")
        self.assertEqual(updated_trace.status, TraceStatus.DECISION_MADE)
    
    def test_add_trace_collective(self):
        """Test dodawania konsensusu do trace"""
        trace = self.manager.create_trace(
            world_version="v1.0",
            model_reference="model_v1",
            prediction_result="WIN"
        )
        
        success = self.manager.add_trace_collective(
            trace_id=trace.trace_id,
            collective_decision_id="coll_001",
            consensus_type="MAJORITY_VOTE",
            confidence_score=0.85,
            participating_agents=["agent_01", "agent_02", "agent_03"],
            consensus_result={"result": "HOME_WIN"}
        )
        
        self.assertTrue(success)
        
        updated_trace = self.manager.get_trace(trace.trace_id)
        self.assertIsNotNone(updated_trace.collective)
        self.assertEqual(updated_trace.collective.collective_decision_id, "coll_001")
        self.assertEqual(updated_trace.status, TraceStatus.COLLECTIVE_CONSENSUS)
    
    def test_add_trace_evaluation(self):
        """Test dodawania metryk oceny do trace"""
        trace = self.manager.create_trace(
            world_version="v1.0",
            model_reference="model_v1",
            prediction_result="WIN"
        )
        
        success = self.manager.add_trace_evaluation(
            trace_id=trace.trace_id,
            metrics={"accuracy": 0.85, "precision": 0.82, "recall": 0.88}
        )
        
        self.assertTrue(success)
        
        updated_trace = self.manager.get_trace(trace.trace_id)
        self.assertIn("accuracy", updated_trace.evaluation_metrics)
        self.assertEqual(updated_trace.evaluation_metrics["accuracy"], 0.85)
        self.assertEqual(updated_trace.status, TraceStatus.EVALUATED)
    
    def test_complete_trace(self):
        """Test ukończenia trace"""
        trace = self.manager.create_trace(
            world_version="v1.0",
            model_reference="model_v1",
            prediction_result="WIN"
        )
        
        success = self.manager.complete_trace(trace.trace_id)
        self.assertTrue(success)
        
        updated_trace = self.manager.get_trace(trace.trace_id)
        self.assertEqual(updated_trace.status, TraceStatus.COMPLETE)
    
    def test_search_traces(self):
        """Test wyszukiwania trace"""
        # Utwórz kilka trace
        trace1 = self.manager.create_trace(
            world_version="v1.0",
            model_reference="model_v1",
            prediction_result="WIN"
        )
        trace2 = self.manager.create_trace(
            world_version="v2.0",
            model_reference="model_v2",
            prediction_result="LOSS"
        )
        
        # Wyszukaj po world_version
        results = self.manager.search_traces(world_version="v1.0")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].trace_id, trace1.trace_id)
        
        # Wyszukaj po model_reference
        results = self.manager.search_traces(model_reference="model_v1")
        self.assertEqual(len(results), 1)
        
        # Wyszukaj z has_decision=False
        results = self.manager.search_traces(has_decision=False)
        self.assertEqual(len(results), 2)  # Oba jeszcze nie mają decyzji
    
    def test_get_traces_by_model(self):
        """Test pobierania trace po modelu"""
        trace1 = self.manager.create_trace(
            world_version="v1.0",
            model_reference="model_v1",
            model_version="1.0.0",
            prediction_result="WIN"
        )
        trace2 = self.manager.create_trace(
            world_version="v1.0",
            model_reference="model_v1",
            model_version="1.0.0",
            prediction_result="WIN"
        )
        trace3 = self.manager.create_trace(
            world_version="v1.0",
            model_reference="model_v2",
            model_version="1.0.0",
            prediction_result="LOSS"
        )
        
        results = self.manager.get_traces_by_model("model_v1")
        self.assertEqual(len(results), 2)
        
        results = self.manager.get_traces_by_model("model_v1", "1.0.0")
        self.assertEqual(len(results), 2)
        
        results = self.manager.get_traces_by_model("model_v2")
        self.assertEqual(len(results), 1)
    
    def test_get_traces_by_world_version(self):
        """Test pobierania trace po wersji świata"""
        trace1 = self.manager.create_trace(world_version="v1.0", prediction_result="WIN")
        trace2 = self.manager.create_trace(world_version="v1.0", prediction_result="WIN")
        trace3 = self.manager.create_trace(world_version="v2.0", prediction_result="LOSS")
        
        results = self.manager.get_traces_by_world_version("v1.0")
        self.assertEqual(len(results), 2)
        
        results = self.manager.get_traces_by_world_version("v2.0")
        self.assertEqual(len(results), 1)
    
    def test_get_traces_by_status(self):
        """Test pobierania trace po statusie"""
        trace1 = self.manager.create_trace(world_version="v1.0", prediction_result="WIN")
        trace2 = self.manager.create_trace(world_version="v1.0", prediction_result="WIN")
        
        # Początkowo oba powinny być PREDICTION_MADE (bo mają prediction_result)
        prediction_traces = self.manager.get_traces_by_status(TraceStatus.PREDICTION_MADE)
        self.assertEqual(len(prediction_traces), 2)
        
        # Ustaw jeden jako COMPLETE
        self.manager.complete_trace(trace1.trace_id)
        
        complete_traces = self.manager.get_traces_by_status(TraceStatus.COMPLETE)
        self.assertEqual(len(complete_traces), 1)
        self.assertEqual(complete_traces[0].trace_id, trace1.trace_id)
        
        # Powinien zostać jeden PREDICTION_MADE
        prediction_traces = self.manager.get_traces_by_status(TraceStatus.PREDICTION_MADE)
        self.assertEqual(len(prediction_traces), 1)
        self.assertEqual(prediction_traces[0].trace_id, trace2.trace_id)
    
    def test_get_traces_by_completeness(self):
        """Test pobierania trace po poziomie kompletności"""
        # Utwórz trace z różnymi poziomami kompletności
        trace1 = self.manager.create_trace(
            world_version="v1.0",
            model_reference="model_v1",
            prediction_result="WIN"
        )
        
        trace2 = self.manager.create_trace(
            world_version="v1.0",
            model_reference="model_v1",
            input_features=["f1"],
            feature_values={"f1": 1.0},
            prediction_result="WIN",
            prediction_confidence=0.8
        )
        
        # Dodaj decyzje do trace2
        self.manager.add_trace_decision(
            trace_id=trace2.trace_id,
            decision_id="dec_001",
            agent_id="agent_01"
        )
        
        # trace2 powinien być bardziej kompletny
        high_completeness = self.manager.get_traces_by_completeness(0.5)
        self.assertIn(trace2, high_completeness)
    
    def test_get_statistics(self):
        """Test statystyk managera"""
        # Utwórz kilka trace
        self.manager.create_trace(world_version="v1.0", model_reference="model_v1", prediction_result="WIN")
        self.manager.create_trace(world_version="v1.0", model_reference="model_v1", prediction_result="WIN")
        self.manager.create_trace(world_version="v2.0", model_reference="model_v2", prediction_result="LOSS")
        
        stats = self.manager.get_statistics()
        
        self.assertEqual(stats['total_traces'], 3)
        self.assertIn('status_counts', stats)
        self.assertIn('model_counts', stats)
        self.assertIn('world_counts', stats)
        self.assertIn('average_completeness', stats)
    
    def test_save_all_to_json(self):
        """Test zapisu wszystkich trace do JSON"""
        self.manager.create_trace(world_version="v1.0", prediction_result="WIN")
        self.manager.create_trace(world_version="v1.0", prediction_result="LOSS")
        
        json_file = os.path.join(self.temp_dir, "test_all_traces.json")
        success = self.manager.save_all_to_json(json_file)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(json_file))
        
        # Sprawdź zawartość
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(data['total_traces'], 2)
        self.assertIn('traces', data)
        self.assertEqual(len(data['traces']), 2)
    
    def test_load_all_from_json(self):
        """Test wczytywania wszystkich trace z JSON"""
        # Najpierw zapisz
        self.manager.create_trace(world_version="v1.0", prediction_result="WIN")
        self.manager.create_trace(world_version="v1.0", prediction_result="LOSS")
        
        json_file = os.path.join(self.temp_dir, "test_load_traces.json")
        self.manager.save_all_to_json(json_file)
        
        # Utwórz nowy manager z innym temp dir i wczytaj
        new_temp_dir = tempfile.mkdtemp()
        newManager = PredictionTraceManager(trace_dir=new_temp_dir)
        success = newManager.load_all_from_json(json_file)
        
        self.assertTrue(success)
        self.assertEqual(len(newManager.get_all_traces()), 2)
        
        # Cleanup
        shutil.rmtree(new_temp_dir, ignore_errors=True)
    
    def test_clear_trace(self):
        """Test usuwania pojedynczego trace"""
        trace = self.manager.create_trace(world_version="v1.0", prediction_result="WIN")
        trace_id = trace.trace_id
        
        # Sprawdź, że trace istnieje
        self.assertIsNotNone(self.manager.get_trace(trace_id))
        
        # Usuń trace
        success = self.manager.clear_trace(trace_id)
        self.assertTrue(success)
        
        # Sprawdź, że trace zniknął
        self.assertIsNone(self.manager.get_trace(trace_id))
        self.assertEqual(len(self.manager.get_all_traces()), 0)
    
    def test_clear_all_traces(self):
        """Test usuwania wszystkich trace"""
        self.manager.create_trace(world_version="v1.0", prediction_result="WIN")
        self.manager.create_trace(world_version="v1.0", prediction_result="LOSS")
        self.assertEqual(len(self.manager.get_all_traces()), 2)
        
        success = self.manager.clear_all_traces()
        self.assertTrue(success)
        self.assertEqual(len(self.manager.get_all_traces()), 0)
    
    def test_list_all_traces(self):
        """Test listowania wszystkich trace"""
        self.manager.create_trace(world_version="v1.0", prediction_result="WIN")
        self.manager.create_trace(world_version="v2.0", prediction_result="LOSS")
        
        summaries = self.manager.list_all_traces()
        self.assertEqual(len(summaries), 2)
        
        for summary in summaries:
            self.assertIn('trace_id', summary)
            self.assertIn('world_version', summary)
            self.assertIn('completeness', summary)
    
    def test_receive_from_world_engine_simulation(self):
        """Test odbierania danych z WorldEngine (symulacja)"""
        # Symulacja WorldEngineOutput
        class MockWorldEngineOutput:
            def __init__(self):
                self.features = {"feature1": 0.5, "feature2": 0.8, "feature3": 0.3}
                self.predictions = {"result": "HOME_WIN", "confidence": 0.75}
                self.models = {"model_ref": "xgboost_v1", "version": "1.0.0"}
                self.results = {"accuracy": 0.85}
                self.metadata = {
                    'world_version': 'world_v1',
                    'world_name': 'test_world',
                    'dataset_version': 'data_v1',
                    'cycle_id': 'cycle_001'
                }
        
        mock_output = MockWorldEngineOutput()
        
        trace = self.manager.receive_from_world_engine(
            world_engine_output=mock_output,
            cycle_id="cycle_001",
            world_version="world_v1"
        )
        
        self.assertIsNotNone(trace)
        self.assertEqual(trace.context.world_version, "world_v1")
        self.assertEqual(trace.context.world_name, "test_world")
        self.assertEqual(trace.context.dataset_version, "data_v1")
        self.assertEqual(trace.context.cycle_id, "cycle_001")
        self.assertEqual(len(trace.input_features), 3)
        self.assertEqual(trace.strategy_experiment_id, None)
        self.assertEqual(trace.world_engine_cycle_id, "cycle_001")
    
    def test_reproduce_data_verification(self):
        """Test weryfikacji reprodukowalności danych"""
        original_data = {"feature1": 0.5, "feature2": 0.8}
        trace = self.manager.create_trace(
            world_version="v1.0",
            model_reference="model_v1",
            input_data=original_data,
            prediction_result="WIN",
            prediction_confidence=0.75
        )
        
        # Sprawdź, że dane pasują
        self.assertTrue(trace.verify_reproducibility(original_data))
        
        # Sprawdź, że inne dane nie pasują
        self.assertFalse(trace.verify_reproducibility({"feature1": 0.6, "feature2": 0.8}))


class TestTraceIntegration(unittest.TestCase):
    """Testy integracyjne dla Prediction Trace Engine"""
    
    def setUp(self):
        """Setup dla testów integracyjnych"""
        self.temp_dir = tempfile.mkdtemp()
        self.trace_manager = PredictionTraceManager(trace_dir=self.temp_dir)
        self.integration_manager = TraceIntegrationManager(self.trace_manager)
    
    def tearDown(self):
        """Cleanup"""
        self.trace_manager.clear_all_traces()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_trace_hook_enable_disable(self):
        """Test włączania/wyłączania hooków"""
        hook = TraceHook(self.trace_manager)
        
        self.assertTrue(hook.is_enabled())
        
        hook.disable()
        self.assertFalse(hook.is_enabled())
        
        hook.enable()
        self.assertTrue(hook.is_enabled())
    
    def test_world_engine_hook_creation(self):
        """Test tworzenia hooka dla WorldEngine"""
        hook = WorldEngineHook(self.trace_manager)
        
        self.assertIsNotNone(hook)
        self.assertEqual(hook.trace_manager, self.trace_manager)
        self.assertTrue(hook.is_enabled())
    
    def test_strategy_lab_hook_creation(self):
        """Test tworzenia hooka dla StrategyLab"""
        hook = StrategyLabHook(self.trace_manager)
        
        self.assertIsNotNone(hook)
        self.assertEqual(hook.trace_manager, self.trace_manager)
    
    def test_agent_runtime_hook_creation(self):
        """Test tworzenia hooka dla AgentRuntime"""
        hook = AgentRuntimeHook(self.trace_manager)
        
        self.assertIsNotNone(hook)
        self.assertEqual(hook.trace_manager, self.trace_manager)
    
    def test_collective_manager_hook_creation(self):
        """Test tworzenia hooka dla CollectiveManager"""
        hook = CollectiveManagerHook(self.trace_manager)
        
        self.assertIsNotNone(hook)
        self.assertEqual(hook.trace_manager, self.trace_manager)
    
    def test_model_evaluator_hook_creation(self):
        """Test tworzenia hooka dla ModelEvaluator"""
        hook = ModelEvaluatorHook(self.trace_manager)
        
        self.assertIsNotNone(hook)
        self.assertEqual(hook.trace_manager, self.trace_manager)
    
    def test_trace_integration_manager_creation(self):
        """Test tworzenia TraceIntegrationManager"""
        self.assertIsNotNone(self.integration_manager)
        self.assertEqual(self.integration_manager.trace_manager, self.trace_manager)
        
        # Powinien mieć wszystkie hooki
        self.assertIsNotNone(self.integration_manager.world_engine_hook)
        self.assertIsNotNone(self.integration_manager.strategy_lab_hook)
        self.assertIsNotNone(self.integration_manager.agent_runtime_hook)
        self.assertIsNotNone(self.integration_manager.collective_manager_hook)
        self.assertIsNotNone(self.integration_manager.model_evaluator_hook)
    
    def test_integration_manager_enable_disable_all(self):
        """Test włączania/wyłączania wszystkich hooków"""
        # Wyłącz wszystkie
        self.integration_manager.disable_all_hooks()
        
        self.assertFalse(self.integration_manager.world_engine_hook.is_enabled())
        self.assertFalse(self.integration_manager.strategy_lab_hook.is_enabled())
        self.assertFalse(self.integration_manager.agent_runtime_hook.is_enabled())
        
        # Włącz wszystkie
        self.integration_manager.enable_all_hooks()
        
        self.assertTrue(self.integration_manager.world_engine_hook.is_enabled())
        self.assertTrue(self.integration_manager.strategy_lab_hook.is_enabled())
        self.assertTrue(self.integration_manager.agent_runtime_hook.is_enabled())
    
    def test_get_trace_manager_from_integration(self):
        """Test pobierania trace manager z integration manager"""
        manager = self.integration_manager.get_trace_manager()
        self.assertEqual(manager, self.trace_manager)
    
    def test_factory_create_integration_manager(self):
        """Test fabryki create_integration_manager"""
        # Utwórz nowy integration manager za pomocą fabryki
        new_integration = create_integration_manager()
        
        self.assertIsNotNone(new_integration)
        self.assertIsNotNone(new_integration.trace_manager)
        # Should create its own trace manager
        self.assertIsNotNone(new_integration.trace_manager)
    
    def test_factory_quick_setup(self):
        """Test fabryki quick_setup"""
        # Utwórz nowy integration manager za pomocą quick_setup
        new_integration = quick_setup()
        
        self.assertIsNotNone(new_integration)
        # Powinien mieć max hooki włączone
        self.assertTrue(new_integration.world_engine_hook.is_enabled())


class TestFactoryFunctions(unittest.TestCase):
    """Testy fabrycznych funkcji tworzenia trace"""
    
    def setUp(self):
        """Setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PredictionTraceManager(trace_dir=self.temp_dir)
    
    def tearDown(self):
        """Cleanup"""
        self.manager.clear_all_traces()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_trace_from_strategy_experiment(self):
        """Test fabryki tworzenia trace z StrategyExperiment"""
        # Symulacja StrategyExperiment
        class MockStrategyExperiment:
            def __init__(self):
                self.experiment_id = "exp_123"
                self.world_version = "world_v1"
                self.dataset_version = "data_v1"
                self.model_reference = "xgboost_v1"
                self.features = ["f1", "f2", "f3"]
                self.metadata = {}

        mock_experiment = MockStrategyExperiment()
        
        trace = create_trace_from_strategy_experiment(
            self.manager,
            mock_experiment
        )
        
        self.assertIsNotNone(trace)
        self.assertEqual(trace.context.world_version, "world_v1")
        self.assertEqual(trace.context.dataset_version, "data_v1")
        self.assertEqual(trace.model.reference, "xgboost_v1")
        self.assertEqual(len(trace.input_features), 3)
        self.assertEqual(trace.strategy_experiment_id, "exp_123")


# ============================================================================
# URUCHAMIANIE TESTÓW
# ============================================================================

if __name__ == "__main__":
    # Uruchom wszystkie testy
    unittest.main(verbosity=2)