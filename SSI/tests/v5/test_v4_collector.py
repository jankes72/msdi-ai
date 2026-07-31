"""
SSI V5 Tests - Testy dla V4 Agents Collector
Testy jednostkowe dla SSI/v5/input_layer/v4_collector.py

Wersja: 1.0
Data: 2026-07-31
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import uuid

# Testowany moduł
from SSI.v5.input_layer.v4_collector import (
    V4AgentsCollector, tworz_v4_collector, get_v4_collector, reset_v4_collector
)
from SSI.v5.input_layer.data_models import (
    V4DataPackage, AgentInfo, PersonalityInfo, StrategyInfo, DecisionInfo,
    AgentRelationshipInfo, V4Metadata, DataSource, DataCategory, DataStatus
)


class TestV4AgentsCollector(unittest.TestCase):
    """Testy dla klasy V4AgentsCollector"""
    
    def setUp(self):
        """Procedura przygotowawcza przed kazdym testem"""
        # Resetuj singleton
        reset_v4_collector()
        self.collector = tworz_v4_collector()
    
    def tearDown(self):
        """Sprzatanie po kazdym tescie"""
        reset_v4_collector()
    
    # =============================================================================
    # TESTY INICJALIZACJI
    # =============================================================================
    
    def test_init_creates_collector(self):
        """Test: Inicjalizacja tworzy poprawny kolektor"""
        collector = tworz_v4_collector()
        self.assertIsInstance(collector, V4AgentsCollector)
        self.assertFalse(collector._initialized)
    
    def test_init_sets_default_values(self):
        """Test: Inicjalizacja ustawia domyslne wartosci"""
        collector = tworz_v4_collector()
        self.assertIsNone(collector._agent_manager)
        self.assertIsNone(collector._agent_birth_system)
        self.assertIsNone(collector._personality_engine)
    
    # =============================================================================
    # TESTY SINGLETON
    # =============================================================================
    
    def test_get_v4_collector_returns_singleton(self):
        """Test: get_v4_collector zwraca te sama instancje"""
        collector1 = get_v4_collector()
        collector2 = get_v4_collector()
        self.assertIs(collector1, collector2)
    
    def test_reset_v4_collector_creates_new_instance(self):
        """Test: reset_v4_collector tworzy nowa instancje"""
        collector1 = get_v4_collector()
        reset_v4_collector()
        collector2 = get_v4_collector()
        self.assertIsNot(collector1, collector2)
    
    # =============================================================================
    # TESTY COLLECT_AGENTS
    # =============================================================================
    
    def test_collect_agents_returns_list(self):
        """Test: collect_agents zwraca liste AgentInfo"""
        agents = self.collector.collect_agents()
        self.assertIsInstance(agents, list)
        if agents:
            self.assertIsInstance(agents[0], AgentInfo)
    
    def test_collect_agents_returns_default_agents(self):
        """Test: collect_agents zwraca domyslnych 5 agentow"""
        agents = self.collector.collect_agents()
        self.assertEqual(len(agents), 5)
        agent_ids = [a.agent_id for a in agents]
        self.assertIn("agent_analyst_001", agent_ids)
        self.assertIn("agent_experimentator_001", agent_ids)
    
    def test_collect_agents_has_required_fields(self):
        """Test: Agenci maja wszystkie wymagane pola"""
        agents = self.collector.collect_agents()
        for agent in agents:
            self.assertIsInstance(agent.agent_id, str)
            self.assertIsInstance(agent.agent_name, str)
            self.assertIsInstance(agent.agent_type, str)
            self.assertIsInstance(agent.status, str)
            self.assertIsInstance(agent.version, str)
            self.assertTrue(len(agent.agent_id) > 0)
            self.assertTrue(len(agent.agent_name) > 0)
    
    # =============================================================================
    # TESTY COLLECT_PERSONALITIES
    # =============================================================================
    
    def test_collect_personalities_returns_list(self):
        """Test: collect_personalities zwraca liste PersonalityInfo"""
        personalities = self.collector.collect_personalities()
        self.assertIsInstance(personalities, list)
        if personalities:
            self.assertIsInstance(personalities[0], PersonalityInfo)
    
    def test_collect_personalities_returns_default_personalities(self):
        """Test: collect_personalities zwraca domyslne osobowosci"""
        personalities = self.collector.collect_personalities()
        self.assertEqual(len(personalities), 5)
        for Personality in personalities:
            self.assertIsInstance(Personality.agent_id, str)
            self.assertIsInstance(Personality.personality_profile, dict)
    
    def test_collect_personalities_has_required_fields(self):
        """Test: Osobowosci maja wszystkie wymagane pola"""
        personalities = self.collector.collect_personalities()
        for personality in personalities:
            self.assertIsInstance(personality.agent_id, str)
            self.assertIsInstance(personality.personality_profile, dict)
            self.assertTrue(len(personality.agent_id) > 0)
    
    # =============================================================================
    # TESTY COLLECT_STRATEGIES
    # =============================================================================
    
    def test_collect_strategies_returns_list(self):
        """Test: collect_strategies zwraca liste StrategyInfo"""
        strategies = self.collector.collect_strategies()
        self.assertIsInstance(strategies, list)
        if strategies:
            self.assertIsInstance(strategies[0], StrategyInfo)
    
    def test_collect_strategies_returns_default_strategies(self):
        """Test: collect_strategies zwraca domyslne strategie"""
        strategies = self.collector.collect_strategies()
        # 2 strategie na agenta * 5 agentow = 10 strategii
        self.assertEqual(len(strategies), 10)
    
    def test_collect_strategies_has_required_fields(self):
        """Test: Strategie maja wszystkie wymagane pola"""
        strategies = self.collector.collect_strategies()
        for strategy in strategies:
            self.assertIsInstance(strategy.strategy_id, str)
            self.assertIsInstance(strategy.agent_id, str)
            self.assertIsInstance(strategy.strategy_name, str)
            self.assertTrue(len(strategy.strategy_id) > 0)
    
    # =============================================================================
    # TESTY COLLECT_DECISIONS
    # =============================================================================
    
    def test_collect_decisions_returns_list(self):
        """Test: collect_decisions zwraca liste DecisionInfo"""
        decisions = self.collector.collect_decisions()
        self.assertIsInstance(decisions, list)
        if decisions:
            self.assertIsInstance(decisions[0], DecisionInfo)
    
    def test_collect_decisions_returns_default_decisions(self):
        """Test: collect_decisions zwraca domyslne decyzje"""
        decisions = self.collector.collect_decisions()
        # 3 decyzje na agenta * 5 agentow = 15 decyzji
        self.assertEqual(len(decisions), 15)
    
    def test_collect_decisions_has_required_fields(self):
        """Test: Decyzje maja wszystkie wymagane pola"""
        decisions = self.collector.collect_decisions()
        for decision in decisions:
            self.assertIsInstance(decision.decision_id, str)
            self.assertIsInstance(decision.agent_id, str)
            self.assertIsInstance(decision.decision_data, dict)
            self.assertTrue(len(decision.decision_id) > 0)
    
    # =============================================================================
    # TESTY COLLECT_RELATIONSHIPS
    # =============================================================================
    
    def test_collect_relationships_returns_list(self):
        """Test: collect_relationships zwraca liste AgentRelationshipInfo"""
        relationships = self.collector.collect_relationships()
        self.assertIsInstance(relationships, list)
        if relationships:
            self.assertIsInstance(relationships[0], AgentRelationshipInfo)
    
    def test_collect_relationships_returns_default_relationships(self):
        """Test: collect_relationships zwraca domyslne relacje"""
        relationships = self.collector.collect_relationships()
        # 5 domyslnych agentow -> maksymalnie 10 relacji (dynamicznie generowanych)
        # Liczba relacji zalezy od implementacji: min(10, n*(n-1)/2) dla n=5 agentow
        self.assertGreaterEqual(len(relationships), 5)
        self.assertLessEqual(len(relationships), 10)
    
    def test_collect_relationships_has_required_fields(self):
        """Test: Relacje maja wszystkie wymagane pola"""
        relationships = self.collector.collect_relationships()
        for rel in relationships:
            self.assertIsInstance(rel.relationship_id, str)
            self.assertIsInstance(rel.source_agent_id, str)
            self.assertIsInstance(rel.target_agent_id, str)
            self.assertIsInstance(rel.relationship_type, str)
            self.assertTrue(len(rel.source_agent_id) > 0)
    
    # =============================================================================
    # TESTY COLLECT_METADATA
    # =============================================================================
    
    def test_collect_metadata_returns_v4metadata(self):
        """Test: collect_metadata zwraca V4Metadata"""
        metadata = self.collector.collect_metadata()
        self.assertIsInstance(metadata, V4Metadata)
        self.assertEqual(metadata.v4_version, "1.0")
        self.assertEqual(metadata.agent_system_version, "2.0")
    
    # =============================================================================
    # TESTY COLLECT_ALL
    # =============================================================================
    
    def test_collect_all_returns_v4data_package(self):
        """Test: collect_all zwraca V4DataPackage"""
        package = self.collector.collect_all()
        self.assertIsInstance(package, V4DataPackage)
    
    def test_collect_all_package_has_all_components(self):
        """Test: Pakiet ma wszystkie komponenty"""
        package = self.collector.collect_all()
        
        # Sprawdzamy czy pakiet ma wszystkie pola
        self.assertIsInstance(package.timestamp, datetime)
        self.assertIsInstance(package.agents, list)
        self.assertIsInstance(package.personalities, list)
        self.assertIsInstance(package.strategies, list)
        self.assertIsInstance(package.decisions, list)
        self.assertIsInstance(package.relationships, list)
        self.assertIsInstance(package.metadata, V4Metadata)
        self.assertIsInstance(package.status, DataStatus)
    
    def test_collect_all_agents_not_empty(self):
        """Test: Pakiet ma niepusta liste agentow"""
        package = self.collector.collect_all()
        self.assertGreater(len(package.agents), 0)
    
    def test_collect_all_personalities_not_empty(self):
        """Test: Pakiet ma niepusta liste osobowosci"""
        package = self.collector.collect_all()
        self.assertGreater(len(package.personalities), 0)
    
    def test_collect_all_strategies_not_empty(self):
        """Test: Pakiet ma niepusta liste strategii"""
        package = self.collector.collect_all()
        self.assertGreater(len(package.strategies), 0)
    
    def test_collect_all_decisions_not_empty(self):
        """Test: Pakiet ma niepusta liste decyzji"""
        package = self.collector.collect_all()
        self.assertGreater(len(package.decisions), 0)
    
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
    
    def test_v4data_package_to_dict(self):
        """Test: V4DataPackage moze byc konwertowany do slownika"""
        package = self.collector.collect_all()
        result = package.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertIn("timestamp", result)
        self.assertIn("agents", result)
        self.assertIn("personalities", result)
        self.assertIn("strategies", result)
        self.assertIn("decisions", result)
        self.assertIn("relationships", result)
        self.assertIn("metadata", result)
        self.assertIn("status", result)
    
    def test_v4data_package_to_json(self):
        """Test: V4DataPackage moze byc konwertowany do JSON"""
        package = self.collector.collect_all()
        json_str = package.to_json()
        
        self.assertIsInstance(json_str, str)
        self.assertTrue(len(json_str) > 0)
    
    # =============================================================================
    # TESTY SERIALIZACJI/DESERIALIZACJI
    # =============================================================================
    
    def test_agent_info_to_dict_and_back(self):
        """Test: AgentInfo serialization/deserialization"""
        original = AgentInfo(
            agent_id="test_agent",
            agent_name="Test Agent",
            agent_type="analyst",
            status="active",
            version="1.0",
            activity_level=0.85,
            responsibility="Test responsibility",
            room_id="ROOM_001"
        )
        
        data = original.to_dict()
        restored = AgentInfo.from_dict(data)
        
        self.assertEqual(original.agent_id, restored.agent_id)
        self.assertEqual(original.agent_name, restored.agent_name)
        self.assertEqual(original.agent_type, restored.agent_type)
        self.assertEqual(original.status, restored.status)
    
    def test_personality_info_to_dict_and_back(self):
        """Test: PersonalityInfo serialization/deserialization"""
        original = PersonalityInfo(
            agent_id="test_agent",
            personality_profile={"analysis_power": 0.9, "risk_acceptance": 0.5},
            traits={"type": "analytical"},
            priorities=["survival", "growth"],
            values={"safety": 0.8, "profit": 0.7},
            current_parameters={"confidence": 0.85}
        )
        
        data = original.to_dict()
        restored = PersonalityInfo.from_dict(data)
        
        self.assertEqual(original.agent_id, restored.agent_id)
        self.assertEqual(original.personality_profile, restored.personality_profile)
        self.assertEqual(original.priorities, restored.priorities)
    
    def test_strategy_info_to_dict_and_back(self):
        """Test: StrategyInfo serialization/deserialization"""
        original = StrategyInfo(
            strategy_id="test_strategy",
            agent_id="test_agent",
            strategy_name="Test Strategy",
            strategy_description="Test description",
            evaluation=0.85,
            effectiveness=0.80
        )
        
        data = original.to_dict()
        restored = StrategyInfo.from_dict(data)
        
        self.assertEqual(original.strategy_id, restored.strategy_id)
        self.assertEqual(original.agent_id, restored.agent_id)
        self.assertEqual(original.evaluation, restored.evaluation)
    
    def test_decision_info_to_dict_and_back(self):
        """Test: DecisionInfo serialization/deserialization"""
        original = DecisionInfo(
            decision_id="test_decision",
            agent_id="test_agent",
            decision_data={"action": "buy", "amount": 1.0},
            reasoning="Test reasoning",
            result="success",
            feedback="Positive",
            confidence=0.85
        )
        
        data = original.to_dict()
        restored = DecisionInfo.from_dict(data)
        
        self.assertEqual(original.decision_id, restored.decision_id)
        self.assertEqual(original.agent_id, restored.agent_id)
        self.assertEqual(original.result, restored.result)
    
    def test_agent_relationship_info_to_dict_and_back(self):
        """Test: AgentRelationshipInfo serialization/deserialization"""
        original = AgentRelationshipInfo(
            relationship_id="test_rel",
            source_agent_id="agent_001",
            target_agent_id="agent_002",
            relationship_type="cooperation",
            strength=0.85,
            description="Test relationship",
            cooperation_level=0.9,
            communication_frequency=0.8,
            hierarchy_level=0
        )
        
        data = original.to_dict()
        restored = AgentRelationshipInfo.from_dict(data)
        
        self.assertEqual(original.relationship_id, restored.relationship_id)
        self.assertEqual(original.source_agent_id, restored.source_agent_id)
        self.assertEqual(original.relationship_type, restored.relationship_type)
    
    def test_v4data_package_from_dict(self):
        """Test: V4DataPackage deserialization"""
        data = {
            "timestamp": "2026-07-31T12:00:00",
            "agents": [
                {
                    "agent_id": "test_agent",
                    "agent_name": "Test Agent",
                    "agent_type": "analyst",
                    "status": "active",
                    "version": "1.0"
                }
            ],
            "personalities": [
                {
                    "agent_id": "test_agent",
                    "personality_profile": {"analysis_power": 0.9}
                }
            ],
            "strategies": [
                {
                    "strategy_id": "test_strategy",
                    "agent_id": "test_agent",
                    "strategy_name": "Test Strategy"
                }
            ],
            "decisions": [
                {
                    "decision_id": "test_decision",
                    "agent_id": "test_agent",
                    "decision_data": {"action": "buy"}
                }
            ],
            "relationships": [
                {
                    "relationship_id": "test_rel",
                    "source_agent_id": "agent_001",
                    "target_agent_id": "agent_002",
                    "relationship_type": "cooperation"
                }
            ],
            "metadata": {
                "v4_version": "1.0",
                "agent_system_version": "2.0",
                "total_agents": 1,
                "active_agents": 1,
                "strategies_count": 1,
                "decisions_count": 1,
                "relationships_count": 1,
                "last_update": "2026-07-31T12:00:00",
                "collection_timestamp": "2026-07-31T12:00:00"
            }
        }
        
        package = V4DataPackage.from_dict(data)
        
        self.assertIsInstance(package, V4DataPackage)
        self.assertEqual(len(package.agents), 1)
        self.assertEqual(package.agents[0].agent_id, "test_agent")
        self.assertEqual(len(package.personalities), 1)
        self.assertEqual(len(package.strategies), 1)
        self.assertEqual(len(package.decisions), 1)
        self.assertEqual(len(package.relationships), 1)
        self.assertIsNotNone(package.metadata)


# =============================================================================
# TESTY INTEGRACYJNE (Smoke Tests)
# =============================================================================

class TestV4CollectorSmoke(unittest.TestCase):
    """Testy integracyjne (smoke tests)"""
    
    def test_import_v4_collector_module(self):
        """Test: Import modulu v4_collector nie rzuca bledu"""
        try:
            from SSI.v5.input_layer import v4_collector
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
            collector = V4AgentsCollector()
            self.assertIsInstance(collector, V4AgentsCollector)
        except Exception as e:
            self.fail(f"Creation error: {e}")
    
    def test_collect_all_no_error(self):
        """Test: collect_all nie rzuca bledu"""
        try:
            collector = V4AgentsCollector()
            package = collector.collect_all()
            self.assertIsInstance(package, V4DataPackage)
        except Exception as e:
            self.fail(f"collect_all error: {e}")


# =============================================================================
# TESTY WALIDACJI
# =============================================================================

class TestV4Validation(unittest.TestCase):
    """Testy walidacji pakietu V4"""
    
    def test_validate_v4_package_with_valid_data(self):
        """Test: Walidacja pakietu z poprawnymi danymi"""
        from SSI.v5.input_layer.data_models import validate_v4_package
        
        package = V4DataPackage()
        package.agents = [
            AgentInfo(
                agent_id="test_agent",
                agent_name="Test Agent",
                agent_type="analyst",
                status="active",
                version="1.0"
            )
        ]
        
        result = validate_v4_package(package)
        self.assertTrue(result)
        self.assertEqual(package.status, DataStatus.VALIDATED)
    
    def test_validate_v4_package_with_empty_agents(self):
        """Test: Walidacja pakietu z pustym lista agentów"""
        from SSI.v5.input_layer.data_models import validate_v4_package
        
        package = V4DataPackage()
        package.agents = []
        
        result = validate_v4_package(package)
        self.assertFalse(result)
    
    def test_get_v4_package_summary(self):
        """Test: Podsumowanie pakietu V4"""
        from SSI.v5.input_layer.data_models import get_v4_package_summary
        
        package = V4DataPackage()
        package.agents = [
            AgentInfo(agent_id="a1", agent_name="Agent 1", agent_type="analyst", status="active", version="1.0"),
            AgentInfo(agent_id="a2", agent_name="Agent 2", agent_type="value_strategist", status="active", version="1.0")
        ]
        package.personalities = [
            PersonalityInfo(agent_id="a1", personality_profile={})
        ]
        package.strategies = [
            StrategyInfo(strategy_id="s1", agent_id="a1", strategy_name="Strategy 1")
        ]
        package.decisions = [
            DecisionInfo(decision_id="d1", agent_id="a1", decision_data={})
        ]
        package.relationships = [
            AgentRelationshipInfo(
                relationship_id="r1",
                source_agent_id="a1",
                target_agent_id="a2",
                relationship_type="cooperation"
            )
        ]
        
        summary = get_v4_package_summary(package)
        
        self.assertEqual(summary["total_agents"], 2)
        self.assertEqual(summary["total_personalities"], 1)
        self.assertEqual(summary["total_strategies"], 1)
        self.assertEqual(summary["total_decisions"], 1)
        self.assertEqual(summary["total_relationships"], 1)
        self.assertEqual(summary["status"], "raw")


# =============================================================================
# URUCHOMIENIE TESTOW
# =============================================================================

if __name__ == '__main__':
    # Uruchom testy
    unittest.main()
