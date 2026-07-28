"""
SSI Base Classes - Podstawowe klasy bazowe

Klasy bazowe dla głównych komponentów systemu SSI:
- BaseWorld: Bazowa klasa dla światów (V3)
- BaseAgent: Bazowa klasa dla agentów (V4)
- BaseStrategy: Bazowa klasa dla strategii

Wersja: 1.0
Data: 2026-07-28

Zgodność z dokumentacją: 01_SYSTEM_ARCHITECTURE.md, 02_DATA_STRUCTURE.md
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json
import uuid
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# BAZOWA KLASA DLA ŚWIATÓW (V3)
# ============================================================================

class WorldType(Enum):
    CHANGE_ANALYSIS = "change_analysis"
    DYNAMICS = "dynamics"
    CLASSIFICATION = "classification"
    RELATIONSHIPS = "relationships"


class WorldStatus(Enum):
    CREATED = "created"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    OBSERVING = "observing"
    ANALYZING = "analyzing"
    ARCHIVED = "archived"


@dataclass
class WorldConfig:
    world_id: str
    world_type: str
    name: str = ""
    description: str = ""
    features: List[str] = field(default_factory=list)
    related_models: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "world_type": self.world_type,
            "name": self.name,
            "description": self.description,
            "features": self.features,
            "related_models": self.related_models,
            "metadata": self.metadata
        }


class BaseWorld(ABC):
    """Bazowa klasa dla światów w systemie V3 World Memory System"""
    
    def __init__(self, config: WorldConfig):
        self.world_id = config.world_id
        self.config = config
        self.status = WorldStatus.CREATED
        self.memory: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = config.metadata or {}
        self.tags: Dict[str, List[str]] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.dependencies: Dict[str, Any] = {}
        logger.info(f"Utworzono świat: {config.world_id}")
    
    @abstractmethod
    def initialize(self) -> bool:
        pass
    
    @abstractmethod
    def process_data(self, data: Any, **kwargs) -> Dict[str, Any]:
        pass
    
    def set_status(self, status: WorldStatus) -> None:
        self.status = status
        self.updated_at = datetime.now()
    
    def add_memory_entry(self, entry_id: str, data: Any, metadata: Dict[str, Any] = None) -> None:
        if metadata is None:
            metadata = {}
        self.memory[entry_id] = {"data": data, "metadata": metadata, "timestamp": datetime.now().isoformat()}
    
    def get_memory_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        return self.memory.get(entry_id)
    
    def add_tag(self, category: str, tag: str) -> None:
        if category not in self.tags:
            self.tags[category] = []
        if tag not in self.tags[category]:
            self.tags[category].append(tag)
    
    def add_dependency(self, world_id: str, dependency_type: str, weight: float = 1.0) -> None:
        self.dependencies[world_id] = {"type": dependency_type, "weight": weight}
    
    def get_status_report(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "world_type": self.config.world_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "memory_entries": len(self.memory),
            "tags": self.tags,
            "features": self.config.features
        }
    
    def to_json(self) -> str:
        return json.dumps(self.get_status_report(), indent=2, ensure_ascii=False)


# ============================================================================
# BAZOWA KLASA DLA AGENTÓW (V4)
# ============================================================================

class AgentStatus(Enum):
    BORN = "born"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    THINKING = "thinking"
    DECIDING = "deciding"
    RESTING = "resting"
    ERROR = "error"
    ARCHIVED = "archived"


class AgentType(Enum):
    ANALYST = "analyst"
    VALUE_STRATEGIST = "value_strategist"
    EXPERIMENTATOR = "experimentator"


@dataclass
class PersonalityVector:
    analysis_power: float = 0.5
    risk_acceptance: float = 0.5
    curiosity: float = 0.5
    security_preference: float = 0.5
    experimentation_level: float = 0.5
    independence: float = 0.5
    trust_level: float = 0.5
    resilience: float = 0.5
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "analysis_power": self.analysis_power,
            "risk_acceptance": self.risk_acceptance,
            "curiosity": self.curiosity,
            "security_preference": self.security_preference,
            "experimentation_level": self.experimentation_level,
            "independence": self.independence,
            "trust_level": self.trust_level,
            "resilience": self.resilience
        }


@dataclass
class EmotionalState:
    confidence: float = 0.7
    frustration: float = 0.1
    curiosity_level: float = 0.5
    satisfaction: float = 0.5
    strategic_pressure: float = 0.1
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "confidence": self.confidence,
            "frustration": self.frustration,
            "curiosity_level": self.curiosity_level,
            "satisfaction": self.satisfaction,
            "strategic_pressure": self.strategic_pressure
        }


@dataclass
class TrustEntry:
    trust_score: float = 0.5
    weight: float = 0.5
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {"trust_score": self.trust_score, "weight": self.weight, "history": self.history}


class BaseAgent(ABC):
    """Bazowa klasa dla agentów w systemie V4 Agent Evolution"""
    
    def __init__(self, agent_id: str, agent_type: str, personality: PersonalityVector = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.personality = personality or PersonalityVector()
        self.emotional_state = EmotionalState()
        self.trust_matrix: Dict[str, TrustEntry] = {}
        self.memory: Dict[str, Any] = {}
        self.status = AgentStatus.BORN
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        logger.info(f"Utworzono agenta: {agent_id}")
    
    @abstractmethod
    def initialize(self) -> bool:
        pass
    
    @abstractmethod
    def make_decision(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def learn_from_experience(self, experience: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        pass
    
    def set_status(self, status: AgentStatus) -> None:
        self.status = status
        self.updated_at = datetime.now()
    
    def update_trust(self, agent_id: str, trust_change: float, reason: str) -> None:
        if agent_id not in self.trust_matrix:
            self.trust_matrix[agent_id] = TrustEntry()
        old_score = self.trust_matrix[agent_id].trust_score
        new_score = max(0.0, min(1.0, old_score + trust_change))
        self.trust_matrix[agent_id].trust_score = new_score
        self.trust_matrix[agent_id].weight = new_score
        self.trust_matrix[agent_id].history.append({
            "timestamp": datetime.now().isoformat(),
            "trust_change": trust_change,
            "new_trust_score": new_score,
            "reason": reason
        })
    
    def get_status_report(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "personality": self.personality.to_dict(),
            "emotional_state": self.emotional_state.to_dict()
        }
    
    def to_json(self) -> str:
        return json.dumps(self.get_status_report(), indent=2, ensure_ascii=False)


# ============================================================================
# BAZOWA KLASA DLA STRATEGII
# ============================================================================

class StrategyStatus(Enum):
    BIRTH = "birth"
    NEW = "new"
    TESTING = "testing"
    MATURING = "maturing"
    OBSERVATION = "observation"
    ANALYSIS = "analysis"
    RANKING = "ranking"
    ACTIVE = "active"
    DECLINING = "declining"
    ARCHIVED = "archived"


class StrategyRanking(Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"


@dataclass
class StrategyConfig:
    strategy_id: str
    world_reference: str = ""
    model_reference: str = ""
    ranking: StrategyRanking = StrategyRanking.D
    initial_value_score: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "world_reference": self.world_reference,
            "model_reference": self.model_reference,
            "ranking": self.ranking.value,
            "initial_value_score": self.initial_value_score
        }


class BaseStrategy(ABC):
    """Bazowa klasa dla strategii w Strategy Intelligence Engine"""
    
    def __init__(self, config: StrategyConfig):
        self.strategy_id = config.strategy_id
        self.config = config
        self.status = StrategyStatus.BIRTH
        self.value_score = config.initial_value_score
        self.parameters: Dict[str, Any] = {}
        self.features: List[str] = []
        self.results_history: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.ranking = config.ranking
        logger.info(f"Utworzono strategię: {config.strategy_id}")
    
    @abstractmethod
    def initialize(self) -> bool:
        pass
    
    @abstractmethod
    def generate_prediction(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def evaluate_results(self, results: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        pass
    
    def set_status(self, status: StrategyStatus) -> None:
        self.status = status
        self.updated_at = datetime.now()
    
    def update_value_score(self, new_score: float) -> None:
        self.value_score = max(0.0, min(1.0, new_score))
    
    def set_ranking(self, ranking: StrategyRanking) -> None:
        self.ranking = ranking
    
    def get_status_report(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "status": self.status.value,
            "ranking": self.ranking.value,
            "value_score": self.value_score,
            "created_at": self.created_at.isoformat()
        }
    
    def to_json(self) -> str:
        return json.dumps(self.get_status_report(), indent=2, ensure_ascii=False)
