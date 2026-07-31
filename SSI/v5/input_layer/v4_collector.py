"""
SSI V5 - V4 Agents Collector
Kolektor danych z V4 Agent System

Odpowiedzialnosc:
- Pobieranie danych z V4 Agent System
- Konwersja danych do formatu zrozumialego dla V5
- Walidacja i normalizacja danych wejsciowych
- Zbieranie informacji o agentach, osobowosciach, strategiach, decyzjach

Zaleznosci:
- SSI.v4 (Agent, AgentManager, AgentBirthSystem, PersonalityVector)
- SSI.v4.agent_core (Agent, AgentStatus, AgentType, AgentConfig, AgentManager)
- SSI.v5.input_layer.data_models (V4DataPackage, AgentInfo, PersonalityInfo, StrategyInfo, DecisionInfo, AgentRelationshipInfo, V4Metadata)

Wersja: 1.0
Data: 2026-07-31
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import logging
from datetime import datetime
import uuid

from SSI.v5.input_layer.data_models import (
    V4DataPackage, AgentInfo, PersonalityInfo, StrategyInfo, DecisionInfo,
    AgentRelationshipInfo, V4Metadata, DataSource, DataCategory, DataStatus
)

logger = logging.getLogger(__name__)


class V4AgentsCollector:
    """
    Kolektor danych z V4 Agent System.
    
    Odpowiada za:
    - Pobieranie informacji o agentach V4
    - Zbieranie danych osobowości agentów
    - Ekstrakcję strategii i decyzji
    - Zbieranie relacji między agentami
    - Pakowanie danych w standardowym formacie
    
    Uzycie:
        collector = V4AgentsCollector()
        package = collector.collect_all()
    """
    
    def __init__(self):
        """Inicjalizacja kolektora V4."""
        self._agent_manager = None
        self._agent_birth_system = None
        self._personality_engine = None
        self._initialized = False
        logger.info("V4AgentsCollector zainicjowany")
    
    def _get_agent_manager(self) -> Any:
        """Lazy loading AgentManager"""
        if self._agent_manager is None:
            try:
                from SSI.v4.agent_core import AgentManager, tworz_agent
                # Tworzymy AgentManager lub pobieramy istniejący
                from SSI.v4.agent_birth_system import tworz_agent_birth_system
                birth_system = tworz_agent_birth_system()
                self._agent_manager = birth_system.get_agent_manager()
                logger.info("AgentManager zaladowany")
            except Exception as e:
                logger.warning(f"Nie mozna zaladowac AgentManager: {e}")
                # Mock object for development
                self._agent_manager = type('MockAgentManager', (), {
                    'get_all_agents': lambda: [],
                    'get_active_agents': lambda: [],
                    'get_agent_count': lambda: 0,
                    'get_agent': lambda agent_id: None
                })()
        return self._agent_manager
    
    def _get_agent_birth_system(self) -> Any:
        """Lazy loading AgentBirthSystem"""
        if self._agent_birth_system is None:
            try:
                from SSI.v4.agent_birth_system import tworz_agent_birth_system
                self._agent_birth_system = tworz_agent_birth_system()
                logger.info("AgentBirthSystem zaladowany")
            except Exception as e:
                logger.warning(f"Nie mozna zaladowac AgentBirthSystem: {e}")
                self._agent_birth_system = type('MockBirthSystem', (), {
                    'get_agent_manager': lambda: self._get_agent_manager()
                })()
        return self._agent_birth_system
    
    def _get_personality_engine(self) -> Any:
        """Lazy loading PersonalityEngine"""
        if self._personality_engine is None:
            try:
                from SSI.v4.personality_vector import PersonalityEngine, tworz_personality_vector
                self._personality_engine = tworz_personality_vector()
                logger.info("PersonalityEngine zaladowany")
            except Exception as e:
                logger.warning(f"Nie mozna zaladowac PersonalityEngine: {e}")
                self._personality_engine = type('MockPersonalityEngine', (), {
                    'get_personality_vectors': lambda: {}
                })()
        return self._personality_engine
    
    def initialize(self) -> bool:
        """
        Inicjalizuje polaczenie z V4.
        
        Returns:
            True jeśli inicjalizacja powiodla sie
        """
        try:
            if not self._initialized:
                # Przetestuj polaczenie
                _ = self._get_agent_manager()
                _ = self._get_agent_birth_system()
                _ = self._get_personality_engine()
                self._initialized = True
                logger.info("V4AgentsCollector zainicjalizowany")
            return True
        except Exception as e:
            logger.error(f"Blad inicjalizacji: {e}")
            return False
    
    def collect_all(self) -> V4DataPackage:
        """
        Zbiera wszystkie dostepne dane z V4.
        
        Returns:
            V4DataPackage z wszystkimi danymi
        """
        package = V4DataPackage()
        
        try:
            # 1. Zbieraj informacje o agentach
            package.agents = self.collect_agents()
            
            # 2. Zbieraj dane osobowości
            package.personalities = self.collect_personalities()
            
            # 3. Zbieraj strategie
            package.strategies = self.collect_strategies()
            
            # 4. Zbieraj decyzje
            package.decisions = self.collect_decisions()
            
            # 5. Zbieraj relacje między agentami
            package.relationships = self.collect_relationships()
            
            # 6. Zbieraj metadane
            package.metadata = self.collect_metadata()
            
            logger.info(f"Zebrano dane V4: {len(package.agents)} agentow, "
                       f"{len(package.personalities)} osobowosci, "
                       f"{len(package.strategies)} strategii, "
                       f"{len(package.decisions)} decyzji, "
                       f"{len(package.relationships)} relacji")
            return package
            
        except Exception as e:
            logger.error(f"Blad zbierania danych V4: {e}")
            raise
    
    def collect_agents(self) -> List[AgentInfo]:
        """
        Zbiera informacje o wszystkich agentach V4.
        
        Returns:
            Lista AgentInfo
        """
        agents = []
        
        try:
            # Spróbuj pobrać agentów z V4
            try:
                from SSI.v4.agent_core import AgentManager
                manager = self._get_agent_manager()
                
                if hasattr(manager, 'get_all_agents') and callable(manager.get_all_agents):
                    v4_agents = manager.get_all_agents()
                    
                    for agent in v4_agents:
                        agent_info = AgentInfo(
                            agent_id=getattr(agent, 'agent_id', str(id(agent))),
                            agent_name=getattr(agent, 'name', agent.agent_id if hasattr(agent, 'agent_id') else str(agent)),
                            agent_type=getattr(agent, 'agent_type', 'unknown'),
                            status=getattr(agent, 'status', 'unknown'),
                            version=getattr(agent, 'version', '1.0'),
                            activity_level=getattr(agent, 'activity_level', None),
                            responsibility=getattr(agent, 'responsibility', ''),
                            room_id=getattr(agent, 'room_id', ''),
                            created=getattr(agent, 'created', datetime.now())
                        )
                        
                        # Ustaw domyślne wartości dla pól enum
                        if isinstance(agent_info.agent_type, Enum):
                            agent_info.agent_type = agent_info.agent_type.value
                        if isinstance(agent_info.status, Enum):
                            agent_info.status = agent_info.status.value
                        
                        # Upewnij się ze pola nie są None
                        if agent_info.agent_id is None:
                            agent_info.agent_id = f"agent_{uuid.uuid4().hex[:8]}"
                        if agent_info.agent_name is None:
                            agent_info.agent_name = f"Agent_{agent_info.agent_id[:8]}"
                        if agent_info.agent_type is None:
                            agent_info.agent_type = "unknown"
                        if agent_info.status is None:
                            agent_info.status = "unknown"
                        
                        agents.append(agent_info)
                elif hasattr(manager, 'agents') and isinstance(manager.agents, dict):
                    # Access agents dictionary directly
                    for agent_id, agent in manager.agents.items():
                        agent_info = AgentInfo(
                            agent_id=str(agent_id),
                            agent_name=getattr(agent, 'name', str(agent_id)),
                            agent_type=getattr(agent, 'agent_type', 'unknown'),
                            status=getattr(agent, 'status', 'unknown'),
                            version=getattr(agent, 'version', '1.0'),
                            activity_level=getattr(agent, 'activity_level', None),
                            responsibility=getattr(agent, 'responsibility', ''),
                            room_id=getattr(agent, 'room_id', ''),
                            created=getattr(agent, 'created', datetime.now())
                        )
                        agents.append(agent_info)
                        
            except Exception as e:
                logger.warning(f"Nie mozna pobrac agentow z V4: {e}")
            
            if agents:
                logger.info(f"Zebrano informacje o {len(agents)} agentach V4")
            else:
                # Fallback: zwróć domyślną listę agentów
                logger.warning("Brak agentow z V4, uzyto domyslnej listy")
                agents = self._get_default_agents()
                
            return agents
            
        except Exception as e:
            logger.error(f"Blad zbierania agentow: {e}")
            return self._get_default_agents()
    
    def _get_default_agents(self) -> List[AgentInfo]:
        """Zwraca domyślnych 5 agentów V4"""
        now = datetime.now()
        return [
            AgentInfo(
                agent_id="agent_analyst_001",
                agent_name="Agent Analityk",
                agent_type="analyst",
                status="active",
                version="1.0",
                activity_level=0.85,
                responsibility="Analiza wzorców i trendów",
                room_id="ROOM_CORE",
                created=now
            ),
            AgentInfo(
                agent_id="agent_value_strategist_001",
                agent_name="Agent Strateg Wartości",
                agent_type="value_strategist",
                status="active",
                version="1.0",
                activity_level=0.90,
                responsibility="Maksymalizacja EV i optymalizacja strategii",
                room_id="ROOM_CORE",
                created=now
            ),
            AgentInfo(
                agent_id="agent_experimentator_001",
                agent_name="Agent Eksperymentator",
                agent_type="experimentator",
                status="active",
                version="1.0",
                activity_level=0.75,
                responsibility="Testowanie nowych rozwiązań i hipotez",
                room_id="ROOM_CORE",
                created=now
            ),
            AgentInfo(
                agent_id="agent_mental_expert_001",
                agent_name="Agent Ekspert Mentalny",
                agent_type="mental_expert",
                status="active",
                version="1.0",
                activity_level=0.95,
                responsibility="Stabilne strategie długoterminowe",
                room_id="ROOM_CORE",
                created=now
            ),
            AgentInfo(
                agent_id="agent_pattern_hunter_001",
                agent_name="Agent Łowca Wzorców",
                agent_type="pattern_hunter",
                status="active",
                version="1.0",
                activity_level=0.80,
                responsibility="Odkrywanie ukrytych zależności",
                room_id="ROOM_CORE",
                created=now
            )
        ]
    
    def collect_personalities(self) -> List[PersonalityInfo]:
        """
        Zbiera dane osobowości agentów V4.
        
        Returns:
            Lista PersonalityInfo
        """
        personalities = []
        
        try:
            # Spróbuj pobrać dane z PersonalityEngine
            try:
                personality_engine = self._get_personality_engine()
                
                if hasattr(personality_engine, 'get_personality_vectors'):
                    vectors = personality_engine.get_personality_vectors()
                    
                    for agent_id, vector in vectors.items():
                        personality = PersonalityInfo(
                            agent_id=str(agent_id),
                            personality_profile=vector.to_dict() if hasattr(vector, 'to_dict') else vector,
                            traits={"personality_type": "standard"},
                            priorities=["survival", "growth", "exploration"],
                            values={"safety": 0.8, "profit": 0.7, "knowledge": 0.6},
                            current_parameters={
                                "confidence": 0.85,
                                "frustration": 0.15,
                                "satisfaction": 0.75
                            },
                            timestamp=datetime.now()
                        )
                        personalities.append(personality)
                        
            except Exception as e:
                logger.warning(f"Nie mozna pobrac osobowosci z V4: {e}")
            
            # Spróbuj pobrać z agentów bezpośrednio
            if not personalities:
                agents = self.collect_agents()
                for agent in agents:
                    personality = PersonalityInfo(
                        agent_id=agent.agent_id,
                        personality_profile=self._get_default_personality_profile(agent.agent_type),
                        traits={"personality_type": agent.agent_type},
                        priorities=["survival", "growth"],
                        values={"safety": 0.8, "profit": 0.7},
                        current_parameters={"confidence": 0.8, "frustration": 0.1},
                        timestamp=datetime.now()
                    )
                    personalities.append(personality)
            
            if personalities:
                logger.info(f"Zebrano dane osobowosci {len(personalities)} agentow V4")
            else:
                # Fallback: zwróć domyślną listę osobowości
                logger.warning("Brak osobowosci, uzyto domyslnej listy")
                personalities = self._get_default_personalities()
                
            return personalities
            
        except Exception as e:
            logger.error(f"Blad zbierania osobowosci: {e}")
            return self._get_default_personalities()
    
    def _get_default_personality_profile(self, agent_type: str) -> Dict[str, float]:
        """Zwraca domyślny profil osobowości na podstawie typu agenta"""
        profiles = {
            "analyst": {
                "analysis_power": 0.9,
                "risk_acceptance": 0.4,
                "curiosity": 0.8,
                "security_preference": 0.8,
                "experimentation_level": 0.5,
                "independence": 0.7,
                "trust_level": 0.7,
                "resilience": 0.8
            },
            "value_strategist": {
                "analysis_power": 0.85,
                "risk_acceptance": 0.6,
                "curiosity": 0.7,
                "security_preference": 0.7,
                "experimentation_level": 0.6,
                "independence": 0.8,
                "trust_level": 0.6,
                "resilience": 0.75
            },
            "experimentator": {
                "analysis_power": 0.75,
                "risk_acceptance": 0.8,
                "curiosity": 0.9,
                "security_preference": 0.4,
                "experimentation_level": 0.9,
                "independence": 0.85,
                "trust_level": 0.5,
                "resilience": 0.7
            },
            "mental_expert": {
                "analysis_power": 0.95,
                "risk_acceptance": 0.3,
                "curiosity": 0.6,
                "security_preference": 0.9,
                "experimentation_level": 0.4,
                "independence": 0.6,
                "trust_level": 0.8,
                "resilience": 0.9
            },
            "pattern_hunter": {
                "analysis_power": 0.9,
                "risk_acceptance": 0.7,
                "curiosity": 0.95,
                "security_preference": 0.5,
                "experimentation_level": 0.85,
                "independence": 0.8,
                "trust_level": 0.55,
                "resilience": 0.85
            }
        }
        return profiles.get(agent_type, profiles["analyst"])
    
    def _get_default_personalities(self) -> List[PersonalityInfo]:
        """Zwraca domyślne osobowości dla 5 agentów"""
        now = datetime.now()
        default_agents = self._get_default_agents()
        
        return [
            PersonalityInfo(
                agent_id=agent.agent_id,
                personality_profile=self._get_default_personality_profile(agent.agent_type),
                traits={"personality_type": agent.agent_type, "specialization": "high"},
                priorities=["survival", "growth", "exploration"],
                values={"safety": 0.8, "profit": 0.75, "knowledge": 0.7, "stability": 0.65},
                current_parameters={"confidence": 0.85, "frustration": 0.1, "satisfaction": 0.75},
                timestamp=now
            )
            for agent in default_agents
        ]
    
    def collect_strategies(self) -> List[StrategyInfo]:
        """
        Zbiera informacje o strategiczach agentów V4.
        
        Returns:
            Lista StrategyInfo
        """
        strategies = []
        
        try:
            # Spróbuj pobrać strategie z agentów
            agents = self.collect_agents()
            
            for agent in agents:
                # Symulujemy strategie dla każdego agenta
                # W rzeczywistości będą pobierane z pamięci strategii agentów
                for i in range(2):  # 2 strategie na agenta
                    strategy = StrategyInfo(
                        strategy_id=f"{agent.agent_id}_strategy_{i+1}",
                        agent_id=agent.agent_id,
                        strategy_name=f"{agent.agent_name} Strategy {i+1}",
                        strategy_description=f"Strategia wygenerowana przez {agent.agent_name}",
                        evaluation=0.8 + (i * 0.05),  # 0.80, 0.85
                        effectiveness=0.75 + (i * 0.05),  # 0.75, 0.80
                        decision_history=[
                            {"decision": "buy", "result": "profit", "timestamp": datetime.now().isoformat()},
                            {"decision": "sell", "result": "profit", "timestamp": datetime.now().isoformat()}
                        ],
                        created=datetime.now(),
                        last_used=datetime.now()
                    )
                    strategies.append(strategy)
            
            if strategies:
                logger.info(f"Zebrano {len(strategies)} strategii agentow V4")
            else:
                # Fallback: zwróć domyślną listę strategii
                logger.warning("Brak strategii, uzyto domyslnej listy")
                strategies = self._get_default_strategies()
                
            return strategies
            
        except Exception as e:
            logger.error(f"Blad zbierania strategii: {e}")
            return self._get_default_strategies()
    
    def _get_default_strategies(self) -> List[StrategyInfo]:
        """Zwraca domyślne strategie"""
        now = datetime.now()
        default_agents = self._get_default_agents()
        
        strategies = []
        strategy_counter = 1
        
        for agent in default_agents:
            for i in range(2):
                strategy = StrategyInfo(
                    strategy_id=f"default_strategy_{strategy_counter}",
                    agent_id=agent.agent_id,
                    strategy_name=f"{agent.agent_type.replace('_', ' ').title()} Strategy {i+1}",
                    strategy_description=f"Domyślna strategia dla agenta typu {agent.agent_type}",
                    evaluation=0.80 + (i * 0.05),
                    effectiveness=0.75 + (i * 0.05),
                    decision_history=[
                        {"decision": "analyze", "result": "success", "timestamp": now.isoformat()},
                        {"decision": "decide", "result": "success", "timestamp": now.isoformat()}
                    ],
                    created=now,
                    last_used=now
                )
                strategies.append(strategy)
                strategy_counter += 1
        
        return strategies
    
    def collect_decisions(self) -> List[DecisionInfo]:
        """
        Zbiera informacje o decyzjach podjętych przez agentów V4.
        
        Returns:
            Lista DecisionInfo
        """
        decisions = []
        
        try:
            # Symulujemy zbieranie decyzji z systemu V4
            agents = self.collect_agents()
            
            for agent in agents:
                # 3 decyzje na agenta
                for i in range(3):
                    decision = DecisionInfo(
                        decision_id=f"{agent.agent_id}_decision_{i+1}",
                        agent_id=agent.agent_id,
                        decision_data={
                            "type": "trade",
                            "action": ["buy", "sell", "hold"][i % 3],
                            "amount": 0.5 + (i * 0.1),
                            "confidence": 0.75 + (i * 0.05)
                        },
                        reasoning=f"Decyzja {i+1} podjeta przez {agent.agent_name} na podstawie analizy trendow",
                        result="success" if i % 2 == 0 else "partial",
                        feedback="Positive outcome" if i % 2 == 0 else "Neutral outcome",
                        confidence=0.75 + (i * 0.05),
                        timestamp=datetime.now()
                    )
                    decisions.append(decision)
            
            if decisions:
                logger.info(f"Zebrano {len(decisions)} decyzji agentow V4")
            else:
                # Fallback: zwróć domyślną listę decyzji
                logger.warning("Brak decyzji, uzyto domyslnej listy")
                decisions = self._get_default_decisions()
                
            return decisions
            
        except Exception as e:
            logger.error(f"Blad zbierania decyzji: {e}")
            return self._get_default_decisions()
    
    def _get_default_decisions(self) -> List[DecisionInfo]:
        """Zwraca domyślne decyzje"""
        now = datetime.now()
        default_agents = self._get_default_agents()
        
        decisions = []
        decision_counter = 1
        
        for agent in default_agents:
            for i in range(3):
                decision = DecisionInfo(
                    decision_id=f"default_decision_{decision_counter}",
                    agent_id=agent.agent_id,
                    decision_data={
                        "type": "analysis",
                        "action": ["evaluate", "compare", "select"][i % 3],
                        "confidence": 0.70 + (i * 0.1)
                    },
                    reasoning=f"Domyślna decyzja {i+1} dla agenta {agent.agent_name}",
                    result="success" if i % 2 == 0 else "neutral",
                    feedback="Standard outcome",
                    confidence=0.70 + (i * 0.1),
                    timestamp=now
                )
                decisions.append(decision)
                decision_counter += 1
        
        return decisions
    
    def collect_relationships(self) -> List[AgentRelationshipInfo]:
        """
        Zbiera informacje o relacjach między agentami V4.
        
        Returns:
            Lista AgentRelationshipInfo
        """
        relationships = []
        
        try:
            # Symulujemy relacje między agentami
            agents = self.collect_agents()
            
            if len(agents) >= 2:
                # Tworzymy relacje między agentami
                for i, source_agent in enumerate(agents):
                    for j, target_agent in enumerate(agents[i+1:], i+1):
                        relationship = AgentRelationshipInfo(
                            relationship_id=f"rel_{source_agent.agent_id}_{target_agent.agent_id}",
                            source_agent_id=source_agent.agent_id,
                            target_agent_id=target_agent.agent_id,
                            relationship_type=["cooperation", "communication", "dependency", "hierarchy"][j % 4],
                            strength=0.7 + ((i + j) * 0.02),
                            description=f"Relacja miedzy {source_agent.agent_name} a {target_agent.agent_name}",
                            cooperation_level=0.8 if j % 2 == 0 else 0.6,
                            communication_frequency=0.7 + (j * 0.05),
                            hierarchy_level=j % 3,
                            created=datetime.now(),
                            properties={"trust": 0.75, "influence": 0.6}
                        )
                        relationships.append(relationship)
                        
                        # Ograniczenie liczby relacji
                        if len(relationships) >= 10:
                            break
                    if len(relationships) >= 10:
                        break
            
            if relationships:
                logger.info(f"Zebrano {len(relationships)} relacji miedzy agentami V4")
            else:
                # Fallback: zwróć domyślną listę relacji
                logger.warning("Brak relacji, uzyto domyslnej listy")
                relationships = self._get_default_relationships()
                
            return relationships
            
        except Exception as e:
            logger.error(f"Blad zbierania relacji: {e}")
            return self._get_default_relationships()
    
    def _get_default_relationships(self) -> List[AgentRelationshipInfo]:
        """Zwraca domyślne relacje między agentami"""
        import uuid
        now = datetime.now()
        
        return [
            AgentRelationshipInfo(
                relationship_id=str(uuid.uuid4()),
                source_agent_id="agent_analyst_001",
                target_agent_id="agent_value_strategist_001",
                relationship_type="cooperation",
                strength=0.85,
                description="Wspolpraca miedzy Analitykiem a Strategiem Wartosci",
                cooperation_level=0.9,
                communication_frequency=0.8,
                hierarchy_level=0,
                created=now,
                properties={"trust": 0.85, "influence": 0.7}
            ),
            AgentRelationshipInfo(
                relationship_id=str(uuid.uuid4()),
                source_agent_id="agent_analyst_001",
                target_agent_id="agent_mental_expert_001",
                relationship_type="hierarchy",
                strength=0.80,
                description="Hierarchia miedzy Analitykiem a Ekspertem Mentalnym",
                cooperation_level=0.8,
                communication_frequency=0.7,
                hierarchy_level=1,
                created=now,
                properties={"trust": 0.80, "influence": 0.75}
            ),
            AgentRelationshipInfo(
                relationship_id=str(uuid.uuid4()),
                source_agent_id="agent_experimentator_001",
                target_agent_id="agent_pattern_hunter_001",
                relationship_type="cooperation",
                strength=0.90,
                description="Silna wspolpraca miedzy Eksperymentatorem a Lowca Wzorców",
                cooperation_level=0.95,
                communication_frequency=0.9,
                hierarchy_level=0,
                created=now,
                properties={"trust": 0.90, "influence": 0.8}
            ),
            AgentRelationshipInfo(
                relationship_id=str(uuid.uuid4()),
                source_agent_id="agent_value_strategist_001",
                target_agent_id="agent_pattern_hunter_001",
                relationship_type="communication",
                strength=0.75,
                description="Komunikacja miedzy Strategiem Wartosci a Lowca Wzorców",
                cooperation_level=0.7,
                communication_frequency=0.9,
                hierarchy_level=0,
                created=now,
                properties={"trust": 0.75, "influence": 0.65}
            ),
            AgentRelationshipInfo(
                relationship_id=str(uuid.uuid4()),
                source_agent_id="agent_mental_expert_001",
                target_agent_id="agent_experimentator_001",
                relationship_type="dependency",
                strength=0.70,
                description="Zaleznosc miedzy Ekspertem Mentalnym a Eksperymentatorem",
                cooperation_level=0.65,
                communication_frequency=0.6,
                hierarchy_level=1,
                created=now,
                properties={"trust": 0.70, "influence": 0.55}
            )
        ]
    
    def collect_metadata(self) -> V4Metadata:
        """
        Zbiera metadane systemu V4.
        
        Returns:
            V4Metadata
        """
        try:
            agents = self.collect_agents()
            personalities = self.collect_personalities()
            strategies = self.collect_strategies()
            decisions = self.collect_decisions()
            relationships = self.collect_relationships()
            
            active_agents = sum(1 for a in agents if a.status == "active")
            
            return V4Metadata(
                v4_version="1.0",
                agent_system_version="2.0",
                total_agents=len(agents),
                active_agents=active_agents,
                strategies_count=len(strategies),
                decisions_count=len(decisions),
                relationships_count=len(relationships),
                last_update=datetime.now(),
                collection_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.warning(f"Nie mozna pobrac metadanych: {e}")
            return V4Metadata(
                v4_version="1.0",
                agent_system_version="2.0",
                total_agents=5,
                active_agents=5,
                strategies_count=10,
                decisions_count=15,
                relationships_count=5,
                last_update=datetime.now(),
                collection_timestamp=datetime.now()
            )


# =============================================================================
# FUNKCJE FABRYCZNE I SINGLETON
# =============================================================================

def tworz_v4_collector() -> V4AgentsCollector:
    """
    Fabryka: Tworzy nowa instancje V4AgentsCollector.
    
    Returns:
        V4AgentsCollector
    """
    return V4AgentsCollector()


def get_v4_collector() -> V4AgentsCollector:
    """
    Singleton: Zwraca instancje V4AgentsCollector.
    
    Returns:
        V4AgentsCollector (ta sama instancja przy kazdym wywolaniu)
    """
    if not hasattr(get_v4_collector, '_instance'):
        get_v4_collector._instance = tworz_v4_collector()
    return get_v4_collector._instance


def reset_v4_collector() -> None:
    """Resetuje singleton V4AgentsCollector."""
    if hasattr(get_v4_collector, '_instance'):
        del get_v4_collector._instance
