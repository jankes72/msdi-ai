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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SSI_V5'))

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
    
    def test_agent_personality_parameter(self):
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


if __name__ == '__main__':
    # Uruchom wszystkie testy
    unittest.main()
