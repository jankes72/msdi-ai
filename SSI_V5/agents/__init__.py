# SSI V5 Agents Module
# ==================================================
#
# ETAP: 5.2.5 FAZA 1
# Data: 2026-08-04
#
# Moduły agenta:
# - agent_runtime.py: Główna klasa AgentRuntime i AgentRuntimeManager
# - agent_memory.py: Pamięć agenta
# - strategy_manager.py: Menadżer strategii
# - decision_engine.py: Silnik decyzji
# - observation_manager.py: Menadżer obserwacji
# - personality_manager.py: Personality Manager (osobowosc agentów)
# - trust_manager.py: Trust Manager (zaufanie i reputacja)

# Import klasy i narzędzia z agenta runtime
from .agent_runtime import (
    AgentStatus,
    AgentMode,
    AgentTask,
    AgentMemory,
    AgentState,
    AgentContract,
    AgentRuntime,
    AgentRuntimeManager
)

# Import z strategy manager
from .strategy_manager import (
    StrategyType,
    LearningMode,
    Strategy,
    StrategyContext,
    StrategyManager
)

# Import z decision engine
from .decision_engine import (
    DecisionType,
    DecisionStatus,
    Decision,
    DecisionContext,
    DecisionEngine
)

# Import z observation manager
from .observation_manager import (
    ObservationType,
    ObservationStatus,
    Observation,
    ObservationBatch,
    ObservationReport,
    ObservationManager
)

# Import z collective manager
from .collective_manager import (
    ConsensusType,
    DecisionStatus,
    CollectiveDecision,
    CollectiveObservation,
    CollectiveMemory,
    CollectiveManager
)

# Import z personality manager
from .personality_manager import (
    PersonalityParameter,
    PersonalityVector,
    PersonalityChange,
    AgentPersonalityState,
    PersonalityManager,
    DEFAULT_PERSONALITY_PROFILES,
    DEFAULT_PERSONALITY_VALUES,
    PERSONALITY_MAPPING
)

# Import z trust manager
from .trust_manager import (
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

# Eksportowane elementy
__all__ = [
    # Agent Runtime
    'AgentStatus',
    'AgentMode',
    'AgentTask',
    'AgentMemory',
    'AgentState',
    'AgentContract',
    'AgentRuntime',
    'AgentRuntimeManager',
    
    # Strategy Manager
    'StrategyType',
    'LearningMode',
    'Strategy',
    'StrategyContext',
    'StrategyManager',
    
    # Decision Engine
    'DecisionType',
    'DecisionStatus',
    'Decision',
    'DecisionContext',
    'DecisionEngine',
    
    # Observation Manager
    'ObservationType',
    'ObservationStatus',
    'Observation',
    'ObservationBatch',
    'ObservationReport',
    'ObservationManager',
    
    # Collective Manager
    'ConsensusType',
    'DecisionStatus',
    'CollectiveDecision',
    'CollectiveObservation',
    'CollectiveMemory',
    'CollectiveManager',
    
    # Personality Manager
    'PersonalityParameter',
    'PersonalityVector',
    'PersonalityChange',
    'AgentPersonalityState',
    'PersonalityManager',
    'DEFAULT_PERSONALITY_PROFILES',
    'DEFAULT_PERSONALITY_VALUES',
    'PERSONALITY_MAPPING',
    
    # Trust Manager
    'TrustLevel',
    'ReputationLevel',
    'DecisionOutcome',
    'DECISION_WEIGHTS',
    'decision_quality_weights',
    'TrustScore',
    'Reputation',
    'TrustUpdate',
    'AgentTrustState',
    'TrustManager'
]

# Sześć instancji agentów (Agent_01 do Agent_06) będzie tworzonych w AgentRuntimeManager
DEFAULT_AGENT_NAMES = [f"Agent_{i:02d}" for i in range(1, 7)]
