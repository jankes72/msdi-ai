# SSI V5 Personality + Trust System Tests
# ==========================================
#
# ETAP: 5.2.5 FAZA 1
# Data: 2026-08-04
#
# Testy dla:
# - PersonalityVector
# - AgentPersonalityState
# - PersonalityManager
# - TrustScore, Reputation, TrustManager
# - Integracja z AgentRuntime
#
# Cel: 100% PASS

import unittest
import sys
import os
import copy
from datetime import datetime

# Dodaj ścieżkę do modułów SSI_V5
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.personality_manager import (
    PersonalityParameter,
    PersonalityVector,
    PersonalityChange,
    AgentPersonalityState,
    PersonalityManager,
    DEFAULT_PERSONALITY_PROFILES,
    DEFAULT_PERSONALITY_VALUES,
    PERSONALITY_MAPPING
)

from agents.trust_manager import (
    TrustLevel,
    ReputationLevel,
    DecisionOutcome,
    DECISION_WEIGHTS,
    decision_quality_weights,
    TrustScore,
    Reputation,
    TrustUpdate,
    AgentTrustState,
    TrustManager
)


class TestPersonalityVector(unittest.TestCase):
    """Testy dla PersonalityVector"""
    
    def test_default_creation(self):
        """Test tworzenia domyślnego PersonalityVector"""
        vector = PersonalityVector.default()
        
        # Sprawdź, że wszystkie parametry mają domyślne wartości
        self.assertEqual(vector.analytical_level, 0.50)
        self.assertEqual(vector.risk_tolerance, 0.50)
        self.assertEqual(vector.creativity, 0.50)
        self.assertEqual(vector.exploration_drive, 0.50)
        self.assertEqual(vector.persistence, 0.50)
        self.assertEqual(vector.cooperation, 0.50)
        self.assertEqual(vector.confidence, 0.50)
        self.assertEqual(vector.adaptability, 0.50)
    
    def test_from_dict_creation(self):
        """Test tworzenia PersonalityVector z słownika"""
        data = {
            'analytical_level': 0.8,
            'risk_tolerance': 0.6,
            'creativity': 0.7,
            'exploration_drive': 0.5,
            'persistence': 0.9,
            'cooperation': 0.8,
            'confidence': 0.7,
            'adaptability': 0.6
        }
        
        vector = PersonalityVector.from_dict(data)
        
        self.assertEqual(vector.analytical_level, 0.8)
        self.assertEqual(vector.risk_tolerance, 0.6)
        self.assertEqual(vector.creativity, 0.7)
    
    def test_from_profile_creation(self):
        """Test tworzenia PersonalityVector z profilu"""
        # Test Analityk
        vector = PersonalityVector.from_profile("Agent_01")
        
        self.assertEqual(vector.analytical_level, 0.90)
        self.assertEqual(vector.risk_tolerance, 0.30)
        self.assertEqual(vector.creativity, 0.60)
        
        # Test Eksperymentator
        vector2 = PersonalityVector.from_profile("Agent_03")
        
        self.assertEqual(vector2.analytical_level, 0.70)
        self.assertEqual(vector2.risk_tolerance, 0.80)
        self.assertEqual(vector2.creativity, 0.90)
        self.assertEqual(vector2.exploration_drive, 0.90)
    
    def test_validation(self):
        """Test walidacji wartości"""
        # Test prawidłowych wartości
        vector = PersonalityVector()
        self.assertIsNotNone(vector)
        
        # Test nieprawidłowych wartości
        with self.assertRaises(ValueError):
            PersonalityVector(analytical_level=1.5)  # > 1.0
        
        with self.assertRaises(ValueError):
            PersonalityVector(risk_tolerance=-0.1)  # < 0.0
    
    def test_to_dict(self):
        """Test konwersji do słownika"""
        vector = PersonalityVector(
            analytical_level=0.8,
            risk_tolerance=0.6,
            creativity=0.7,
            exploration_drive=0.5,
            persistence=0.9,
            cooperation=0.8,
            confidence=0.7,
            adaptability=0.6
        )
        
        data = vector.to_dict()
        
        self.assertEqual(data['analytical_level'], 0.8)
        self.assertEqual(data['risk_tolerance'], 0.6)
        self.assertIn('analytical_level', data)
        self.assertIn('creativity', data)
    
    def test_to_list(self):
        """Test konwersji do listy"""
        vector = PersonalityVector.default()
        result = vector.to_list()
        
        self.assertEqual(len(result), 8)
        self.assertTrue(all(0.0 <= v <= 1.0 for v in result))
    
    def test_get_set_parameter(self):
        """Test pobierania i ustawiania parametrów"""
        vector = PersonalityVector.default()
        
        # Pobierz parametr
        self.assertEqual(vector.get_parameter(PersonalityParameter.ANALYTICAL_LEVEL), 0.50)
        
        # Ustaw parametr
        vector.set_parameter(PersonalityParameter.ANALYTICAL_LEVEL, 0.8)
        self.assertEqual(vector.get_parameter(PersonalityParameter.ANALYTICAL_LEVEL), 0.8)
        
        # Sprawdź walidację
        with self.assertRaises(ValueError):
            vector.set_parameter(PersonalityParameter.RISK_TOLERANCE, 1.5)
    
    def test_update_from_dict(self):
        """Test aktualizacji z słownika"""
        vector = PersonalityVector.default()
        
        updates = {'analytical_level': 0.8, 'risk_tolerance': 0.6}
        vector.update_from_dict(updates)
        
        self.assertEqual(vector.analytical_level, 0.8)
        self.assertEqual(vector.risk_tolerance, 0.6)
    
    def test_weighted_average(self):
        """Test obliczania ważonej średniej"""
        vector = PersonalityVector.default()
        avg = vector.weighted_average()
        
        self.assertAlmostEqual(avg, 0.5, places=2)


class TestAgentPersonalityState(unittest.TestCase):
    """Testy dla AgentPersonalityState"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.agent_id = "test_agent_01"
        self.agent_name = "Test Agent"
        self.initial_personality = PersonalityVector.from_profile("Agent_01")
        self.state = AgentPersonalityState(
            agent_id=self.agent_id,
            name=self.agent_name,
            current_personality=copy.deepcopy(self.initial_personality),
            initial_personality=copy.deepcopy(self.initial_personality)
        )
    
    def test_initialization(self):
        """Test inicjalizacji stanu osobowości"""
        self.assertEqual(self.state.agent_id, self.agent_id)
        self.assertEqual(self.state.name, self.agent_name)
        self.assertIsNotNone(self.state.current_personality)
        self.assertIsNotNone(self.state.initial_personality)
        self.assertEqual(len(self.state.personality_history), 0)
    
    def test_to_dict(self):
        """Test konwersji do słownika"""
        data = self.state.to_dict()
        
        self.assertIn('agent_id', data)
        self.assertIn('name', data)
        self.assertIn('current_personality', data)
        self.assertIn('initial_personality', data)
        self.assertIn('personality_history', data)
    
    def test_get_personality_vector(self):
        """Test pobierania wektora osobowości"""
        vector = self.state.get_personality_vector()
        
        self.assertIsInstance(vector, PersonalityVector)
        self.assertEqual(vector.to_dict(), self.state.current_personality.to_dict())
    
    def test_get_parameter(self):
        """Test pobierania parametru"""
        param = self.state.get_parameter(PersonalityParameter.ANALYTICAL_LEVEL)
        
        self.assertEqual(param, 0.90)
    
    def test_update_personality(self):
        """Test aktualizacji osobowości"""
        updates = {'analytical_level': 0.85, 'risk_tolerance': 0.35}
        
        change = self.state.update_personality(updates, "test_update")
        
        self.assertIsInstance(change, PersonalityChange)
        self.assertEqual(len(self.state.personality_history), 1)
        self.assertEqual(self.state.current_personality.analytical_level, 0.85)
        self.assertEqual(self.state.current_personality.risk_tolerance, 0.35)
    
    def test_apply_evolution(self):
        """Test zastosowania ewolucji"""
        # Symuluj dobry wynik
        change = self.state.apply_evolution(
            success_rate=0.9,
            decision_quality=0.85,
            collaboration_score=0.7,
            cycle_id="test_cycle_01"
        )
        
        self.assertIsInstance(change, PersonalityChange)
        self.assertEqual(len(self.state.personality_history), 1)
    
    def test_reset_to_initial(self):
        """Test przywracania do początku"""
        # Najpierw zmień osobowość
        self.state.update_personality({'analytical_level': 0.5}, "test")
        
        # Następnie przywróć
        change = self.state.reset_to_initial()
        
        self.assertIsInstance(change, PersonalityChange)
        self.assertEqual(self.state.current_personality.to_dict(), 
                        self.state.initial_personality.to_dict())
    
    def test_get_history(self):
        """Test pobierania historii"""
        # Dodaj kilka zmian
        self.state.update_personality({'analytical_level': 0.8}, "change1")
        self.state.update_personality({'risk_tolerance': 0.4}, "change2")
        
        history = self.state.get_history()
        
        self.assertEqual(len(history), 2)
        
        # Test z limitem
        history_limit = self.state.get_history(limit=1)
        self.assertEqual(len(history_limit), 1)
    
    def test_get_evolution_summary(self):
        """Test pobierania podsumowania ewolucji"""
        # Dodaj zmien
        self.state.update_personality({'analytical_level': 0.85}, "test")
        
        summary = self.state.get_evolution_summary()
        
        self.assertIn('total_changes', summary)
        self.assertIn('parameters_changed', summary)
        self.assertIn('biggest_increase', summary)
        self.assertIn('biggest_decrease', summary)


class TestPersonalityManager(unittest.TestCase):
    """Testy dla PersonalityManager"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.manager = PersonalityManager(world_name="Test_World")
    
    def test_create_personality_state(self):
        """Test tworzenia stanu osobowości"""
        state = self.manager.create_personality_state(
            agent_id="agent_01",
            agent_name="Agent_01",
            use_profile=True
        )
        
        self.assertIsInstance(state, AgentPersonalityState)
        self.assertEqual(state.name, "Agent_01")
    
    def test_get_personality_state(self):
        """Test pobierania stanu osobowości"""
        self.manager.create_personality_state("agent_01", "Agent_01")
        
        state = self.manager.get_personality_state("agent_01")
        
        self.assertIsNotNone(state)
        self.assertEqual(state.agent_id, "agent_01")
    
    def test_get_personality_vector(self):
        """Test pobierania wektora osobowości"""
        self.manager.create_personality_state("agent_01", "Agent_01")
        
        vector = self.manager.get_personality_vector("agent_01")
        
        self.assertIsNotNone(vector)
        self.assertIsInstance(vector, PersonalityVector)
    
    def test_update_personality(self):
        """Test aktualizacji osobowości"""
        self.manager.create_personality_state("agent_01", "Agent_01")
        
        change = self.manager.update_personality(
            agent_id="agent_01",
            updates={'analytical_level': 0.85},
            reason="test_update"
        )
        
        self.assertIsNotNone(change)
    
    def test_apply_evolution(self):
        """Test zastosowania ewolucji"""
        self.manager.create_personality_state("agent_01", "Agent_01")
        
        change = self.manager.apply_evolution(
            agent_id="agent_01",
            success_rate=0.9,
            decision_quality=0.8,
            collaboration_score=0.7,
            cycle_id="test_cycle"
        )
        
        self.assertIsNotNone(change)
    
    def test_get_personality_summary(self):
        """Test pobierania podsumowania"""
        # Utwórz kilku agentów
        self.manager.create_personality_state("agent_01", "Agent_01")
        self.manager.create_personality_state("agent_02", "Agent_02")
        
        summary = self.manager.get_personality_summary()
        
        self.assertEqual(summary['total_agents'], 2)
        self.assertIn('agents', summary)
        self.assertIn('average_personality', summary)


class TestTrustScore(unittest.TestCase):
    """Testy dla TrustScore"""
    
    def test_default_creation(self):
        """Test tworzenia domyślnego TrustScore"""
        score = TrustScore(from_agent_id="agent_01", to_agent_id="agent_02")
        
        self.assertEqual(score.from_agent_id, "agent_01")
        self.assertEqual(score.to_agent_id, "agent_02")
        self.assertEqual(score.trust_score, 0.5)
        self.assertEqual(score.weight, 1.0)
        self.assertEqual(score.interaction_count, 0)
    
    def test_from_dict_creation(self):
        """Test tworzenia TrustScore z słownika"""
        data = {
            'from_agent_id': 'agent_01',
            'to_agent_id': 'agent_02',
            'trust_score': 0.8,
            'weight': 1.2,
            'interaction_count': 5,
            'correct_interactions': 4,
            'incorrect_interactions': 1
        }
        
        score = TrustScore.from_dict(data)
        
        self.assertEqual(score.trust_score, 0.8)
        self.assertEqual(score.interaction_count, 5)
    
    def test_get_trust_level(self):
        """Test pobierania poziomu zaufania"""
        # Full Trust
        score1 = TrustScore(from_agent_id="a1", to_agent_id="a2", trust_score=0.95)
        self.assertEqual(score1.get_trust_level(), TrustLevel.FULL_TRUST)
        
        # High
        score2 = TrustScore(from_agent_id="a1", to_agent_id="a2", trust_score=0.75)
        self.assertEqual(score2.get_trust_level(), TrustLevel.HIGH)
        
        # Neutral
        score3 = TrustScore(from_agent_id="a1", to_agent_id="a2", trust_score=0.5)
        self.assertEqual(score3.get_trust_level(), TrustLevel.NEUTRAL)
        
        # Low
        score4 = TrustScore(from_agent_id="a1", to_agent_id="a2", trust_score=0.35)
        self.assertEqual(score4.get_trust_level(), TrustLevel.LOW)
        
        # Distrust
        score5 = TrustScore(from_agent_id="a1", to_agent_id="a2", trust_score=0.2)
        self.assertEqual(score5.get_trust_level(), TrustLevel.DISTRUST)
    
    def test_get_success_rate(self):
        """Test obliczania odsetka trafnych interakcji"""
        score = TrustScore(
            from_agent_id="a1",
            to_agent_id="a2",
            correct_interactions=4,
            incorrect_interactions=1,
            interaction_count=5
        )
        
        rate = score.get_success_rate()
        self.assertAlmostEqual(rate, 0.8, places=2)
    
    def test_update_from_feedback(self):
        """Test aktualizacji na podstawie feedbacku"""
        score = TrustScore(from_agent_id="a1", to_agent_id="a2")
        
        # Poprawna decyzja
        score.update_from_feedback(DecisionOutcome.CORRECT, confidence_weight=1.0)
        
        self.assertEqual(score.interaction_count, 1)
        self.assertEqual(score.correct_interactions, 1)
        self.assertGreater(score.trust_score, 0.5)
        
        # Błędna decyzja
        score.update_from_feedback(DecisionOutcome.INCORRECT, confidence_weight=1.0)
        
        self.assertEqual(score.interaction_count, 2)
        self.assertEqual(score.incorrect_interactions, 1)


class TestReputation(unittest.TestCase):
    """Testy dla Reputation"""
    
    def test_default_creation(self):
        """Test tworzenia domyślnej Reputation"""
        rep = Reputation(agent_id="agent_01", agent_name="Agent_01")
        
        self.assertEqual(rep.agent_id, "agent_01")
        self.assertEqual(rep.agent_name, "Agent_01")
        self.assertEqual(rep.reputation_score, 0.5)
        self.assertEqual(rep.total_decisions, 0)
    
    def test_get_reputation_level(self):
        """Test pobierania poziomu reputacji"""
        rep1 = Reputation(agent_id="a1", agent_name="A1", reputation_score=0.98)
        self.assertEqual(rep1.get_reputation_level(), ReputationLevel.OUTSTANDING)
        
        rep2 = Reputation(agent_id="a2", agent_name="A2", reputation_score=0.85)
        self.assertEqual(rep2.get_reputation_level(), ReputationLevel.EXCELLENT)
        
        rep3 = Reputation(agent_id="a3", agent_name="A3", reputation_score=0.65)
        self.assertEqual(rep3.get_reputation_level(), ReputationLevel.GOOD)
        
        rep4 = Reputation(agent_id="a4", agent_name="A4", reputation_score=0.45)
        self.assertEqual(rep4.get_reputation_level(), ReputationLevel.FAIR)
        
        rep5 = Reputation(agent_id="a5", agent_name="A5", reputation_score=0.25)
        self.assertEqual(rep5.get_reputation_level(), ReputationLevel.POOR)
    
    def test_update_from_decision(self):
        """Test aktualizacji na podstawie decyzji"""
        rep = Reputation(agent_id="agent_01", agent_name="Agent_01")
        
        # Poprawna decyzja
        rep.update_from_decision(DecisionOutcome.CORRECT, confidence=0.8, collaboration=0.7)
        
        self.assertEqual(rep.total_decisions, 1)
        self.assertEqual(rep.correct_decisions, 1)
        self.assertGreater(rep.reputation_score, 0.5)
        
        # Błędna decyzja
        rep.update_from_decision(DecisionOutcome.INCORRECT, confidence=0.8, collaboration=0.3)
        
        self.assertEqual(rep.total_decisions, 2)
        self.assertEqual(rep.incorrect_decisions, 1)


class TestAgentTrustState(unittest.TestCase):
    """Testy dla AgentTrustState"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.state = AgentTrustState(
            agent_id="agent_01",
            agent_name="Agent_01"
        )
    
    def test_initialization(self):
        """Test inicjalizacji stanu zaufania"""
        self.assertEqual(self.state.agent_id, "agent_01")
        self.assertEqual(self.state.agent_name, "Agent_01")
        self.assertIsNotNone(self.state.reputation)
        self.assertEqual(len(self.state.trust_in_agents), 0)
        self.assertEqual(len(self.state.trust_history), 0)
    
    def test_get_trust_score(self):
        """Test pobierania poziomu zaufania"""
        # Domyślnie None
        score = self.state.get_trust_score("agent_02")
        self.assertIsNone(score)
        
        # Po dodaniu TrustScore
        self.state.trust_in_agents["agent_02"] = TrustScore(
            from_agent_id="agent_01",
            to_agent_id="agent_02",
            trust_score=0.8
        )
        
        score = self.state.get_trust_score("agent_02")
        self.assertEqual(score, 0.8)
    
    def test_get_trust_level(self):
        """Test pobierania poziomu zaufania"""
        self.state.trust_in_agents["agent_02"] = TrustScore(
            from_agent_id="agent_01",
            to_agent_id="agent_02",
            trust_score=0.85
        )
        
        level = self.state.get_trust_level("agent_02")
        self.assertEqual(level, TrustLevel.HIGH)
    
    def test_update_trust_from_feedback(self):
        """Test aktualizacji zaufania na podstawie feedbacku"""
        update = self.state.update_trust_from_feedback(
            other_agent_id="agent_02",
            outcome=DecisionOutcome.CORRECT,
            confidence=0.8,
            cycle_id="test_cycle"
        )
        
        self.assertIsNotNone(update)
        self.assertIsInstance(update, TrustUpdate)
        self.assertEqual(len(self.state.trust_history), 1)
    
    def test_update_reputation_from_decision(self):
        """Test aktualizacji reputacji na podstawie decyzji"""
        self.state.update_reputation_from_decision(
            outcome=DecisionOutcome.CORRECT,
            confidence=0.8,
            collaboration=0.7
        )
        
        self.assertIsNotNone(self.state.reputation)
        self.assertEqual(self.state.reputation.total_decisions, 1)


class TestTrustManager(unittest.TestCase):
    """Testy dla TrustManager"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.manager = TrustManager(world_name="Test_World")
    
    def test_initialize_agent_trust(self):
        """Test inicjalizacji zaufania agenta"""
        state = self.manager.initialize_agent_trust(
            agent_id="agent_01",
            agent_name="Agent_01",
            known_agents=["agent_02"]
        )
        
        self.assertIsInstance(state, AgentTrustState)
        self.assertEqual(state.agent_id, "agent_01")
    
    def test_get_trust_score(self):
        """Test pobierania poziomu zaufania"""
        self.manager.initialize_agent_trust("agent_01", "Agent_01", ["agent_02"])
        
        score = self.manager.get_trust_score("agent_01", "agent_02")
        
        self.assertIsNotNone(score)
        self.assertAlmostEqual(score, 0.5, places=2)  # Domyślne zaufanie
    
    def test_update_trust_from_feedback(self):
        """Test aktualizacji zaufania na podstawie feedbacku"""
        self.manager.initialize_agent_trust("agent_01", "Agent_01", ["agent_02"])
        
        update = self.manager.update_trust_from_feedback(
            from_agent_id="agent_01",
            to_agent_id="agent_02",
            outcome=DecisionOutcome.CORRECT,
            confidence=0.8,
            cycle_id="test_cycle"
        )
        
        self.assertIsNotNone(update)
    
    def test_initialize_all_trust(self):
        """Test inicjalizacji zaufania pomiędzy wszystkimi agentami"""
        agent_ids = ["agent_01", "agent_02", "agent_03"]
        agent_names = {"agent_01": "Agent_01", "agent_02": "Agent_02", "agent_03": "Agent_03"}
        
        self.manager.initialize_all_trust(agent_ids, agent_names)
        
        # Sprawdź, że wszystkie stany zostały utworzone
        for agent_id in agent_ids:
            state = self.manager.get_agent_trust_state(agent_id)
            self.assertIsNotNone(state)
        
        # Sprawdź macierz zaufania
        trust_matrix = self.manager.get_full_trust_matrix()
        self.assertEqual(len(trust_matrix), len(agent_ids))
    
    def test_get_reputation_ranking(self):
        """Test rankingu reputacji"""
        agent_ids = ["agent_01", "agent_02", "agent_03"]
        agent_names = {"agent_01": "Agent_01", "agent_02": "Agent_02", "agent_03": "Agent_03"}
        
        self.manager.initialize_all_trust(agent_ids, agent_names)
        
        # Aktualizuj reputację
        self.manager.update_reputation_from_decision(
            agent_id="agent_01",
            outcome=DecisionOutcome.CORRECT,
            confidence=0.9
        )
        self.manager.update_reputation_from_decision(
            agent_id="agent_02",
            outcome=DecisionOutcome.CORRECT,
            confidence=0.7
        )
        self.manager.update_reputation_from_decision(
            agent_id="agent_03",
            outcome=DecisionOutcome.INCORRECT,
            confidence=0.5
        )
        
        ranking = self.manager.get_reputation_ranking()
        
        self.assertEqual(len(ranking), 3)
        # Agent_01 powinien być na pierwszym miejscu (najwyższa reputacja)
        self.assertEqual(ranking[0][0], "agent_01")
    
    def test_get_trust_summary(self):
        """Test pobierania podsumowania zaufania"""
        agent_ids = ["agent_01", "agent_02"]
        agent_names = {"agent_01": "Agent_01", "agent_02": "Agent_02"}
        
        self.manager.initialize_all_trust(agent_ids, agent_names)
        
        summary = self.manager.get_trust_summary()
        
        self.assertIn('total_agents', summary)
        self.assertIn('total_interactions', summary)
        self.assertIn('average_trust_score', summary)
        self.assertIn('trust_distribution', summary)
        self.assertIn('reputation_distribution', summary)


class TestAgentRuntimeIntegration(unittest.TestCase):
    """Testy integracji z AgentRuntime"""
    
    def test_agent_personality_initialization(self):
        """Test inicjalizacji osobowości agenta"""
        from agents.agent_runtime import AgentRuntime, AgentMode
        
        agent = AgentRuntime(
            agent_id="test_agent_01",
            name="Agent_01",
            mode=AgentMode.AUTO
        )
        
        # Sprawdź, że osobowość została zainicjalizowana
        personality = agent.get_personality()
        
        self.assertIsNotNone(personality)
        self.assertIn('current_personality', personality)
        self.assertIn('initial_personality', personality)
    
    def test_agent_personality_vector(self):
        """Test wektora osobowości agenta"""
        from agents.agent_runtime import AgentRuntime, AgentMode
        
        agent = AgentRuntime(
            agent_id="test_agent_02",
            name="Agent_02",
            mode=AgentMode.AUTO
        )
        
        vector = agent.get_personality_vector()
        
        self.assertIsNotNone(vector)
        self.assertIn('analytical_level', vector)
        self.assertIn('risk_tolerance', vector)
        self.assertIn('creativity', vector)
    
    def test_agent_personality_vector(self):
        """Test parametru osobowości agenta"""
        from agents.agent_runtime import AgentRuntime, AgentMode
        
        agent = AgentRuntime(
            agent_id="test_agent_01",
            name="Agent_01",
            mode=AgentMode.AUTO
        )
        
        analytical = agent.get_personality_parameter("analytical_level")
        risk = agent.get_personality_parameter("risk_tolerance")
        
        # Agent_01 powinien mieć wysoki analytical_level i niski risk_tolerance
        self.assertEqual(analytical, 0.90)
        self.assertEqual(risk, 0.30)
    
    def test_agent_runtime_manager_integration(self):
        """Test integracji z AgentRuntimeManager"""
        from agents.agent_runtime import AgentRuntimeManager
        
        manager = AgentRuntimeManager(
            number_of_agents=2,
            world_name="Test_World"
        )
        
        init_result = manager.initialize()
        
        self.assertEqual(init_result['status'], 'success')
        self.assertEqual(init_result['agents_initialized'], 2)
        
        # Sprawdź, że wszyscy agenci mają osobowość
        all_agent_ids = list(manager.agents.keys())
        for agent_id in all_agent_ids:
            agent = manager.agents[agent_id]
            personality = agent.get_personality()
            self.assertIsNotNone(personality)


class TestPersonalityTrustPersistence(unittest.TestCase):
    """Testy zapisu i odczytu stanu"""
    
    def test_personality_state_save_load(self):
        """Test zapisu i odczytu stanu osobowości"""
        from agents.personality_manager import AgentPersonalityState, PersonalityVector
        import tempfile
        import shutil
        
        # Tworzymy tymczasowy katalog
        temp_dir = tempfile.mkdtemp()
        
        try:
            state = AgentPersonalityState(
                agent_id="test_agent",
                name="Test Agent",
                current_personality=PersonalityVector.from_profile("Agent_01"),
                initial_personality=PersonalityVector.from_profile("Agent_01")
            )
            
            # Zmień osobowość
            state.update_personality({'analytical_level': 0.85}, "test_change")
            
            # Zapisz
            file_path = os.path.join(temp_dir, "test_agent_personality_history.json")
            result = state.save_personality_history(file_path)
            
            self.assertTrue(result)
            self.assertTrue(os.path.exists(file_path))
        finally:
            # Wyczyść tymczasowy katalog
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    # Uruchom wszystkie testy
    unittest.main()
