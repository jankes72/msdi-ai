"""
SSI V5 - Agents Module
Glowny modul agentow dla systemu SSI V5

Zgodnie z dokumentacja Sprint 11.5 v2.0:
- Runtime Controller
- Agent Runtime Foundation
- Memory Observation System

Struktura modulu:
SSI/v5/agents/
├── __init__.py                 # Inicjalizacja modulu
├── agents_config.py           # Konfiguracja agentow
├── agent_runtime.py           # Runtime pojedynczego agenta
├── agent_manager.py           # Centralny manager agentow
├── agent_state.py             # Stan agenta
├── agent_memory_store.py      # Przechowalnia pamieci agenta
├── agent_memory_manager.py    # Manager pamieci agentow
└── prompt_memory_builder.py   # Builder kontekstu promptow

Wspolpraca z:
- SSI/v5/runtime/              # Runtime Controller
- SSI/memory/agents/           # Pamiec agentow
- SSI/v2/, SSI/v3/, SSI/v4/    # Collectory (zrodla danych)
"""

# Agent Configuration
from .agents_config import (
    AgentConfig,
    AgentRuntimeConfig,
    AgentPersonalityConfig,
    AgentStrategyConfig,
    AgentMemoryConfig,
    AgentStatus,
    AgentType,
    StrategyType,
    PersonalityTrait,
    create_default_personality,
    create_default_strategy,
    create_default_memory_config,
    create_agent_config,
    create_all_agent_configs,
    save_agent_configs,
    load_agent_configs
)

# Agent Runtime
from .agent_runtime import (
    AgentRuntime,
    create_agent
)

# Agent Manager
from .agent_manager import (
    AgentManager,
    create_agent_manager
)

# Agent State
from .agent_state import (
    DecisionRecord,
    BehaviorRecord,
    StrategyRecord,
    HistoryEntry,
    RelationshipEntry,
    AgentRuntimeState,
    AgentMemoryState,
    AgentStateManager,
    create_agent_state_manager
)

# Agent Memory Store
from .agent_memory_store import (
    AgentMemoryStore,
    MemoryEntry,
    PersonalityMemoryEntry,
    BehaviorMemoryEntry,
    StrategyMemoryEntry,
    HistoryMemoryEntry,
    RelationshipMemoryEntry,
    PromptMemoryEntry,
    MemoryType,
    create_agent_memory_store
)

# Agent Memory Manager
from .agent_memory_manager import (
    AgentMemoryManager,
    create_agent_memory_manager
)

# Prompt Memory Builder
from .prompt_memory_builder import (
    PromptMemoryBuilder,
    create_prompt_memory_builder
)

__all__ = [
    # Configuration
    'AgentConfig',
    'AgentRuntimeConfig',
    'AgentPersonalityConfig',
    'AgentStrategyConfig',
    'AgentMemoryConfig',
    'AgentStatus',
    'AgentType',
    'StrategyType',
    'PersonalityTrait',
    'create_default_personality',
    'create_default_strategy',
    'create_default_memory_config',
    'create_agent_config',
    'create_all_agent_configs',
    'save_agent_configs',
    'load_agent_configs',
    
    # Runtime
    'AgentRuntime',
    'create_agent',
    
    # Manager
    'AgentManager',
    'create_agent_manager',
    
    # State
    'DecisionRecord',
    'BehaviorRecord',
    'StrategyRecord',
    'HistoryEntry',
    'RelationshipEntry',
    'AgentRuntimeState',
    'AgentMemoryState',
    'AgentStateManager',
    'create_agent_state_manager',
    
    # Memory Store
    'AgentMemoryStore',
    'MemoryEntry',
    'PersonalityMemoryEntry',
    'BehaviorMemoryEntry',
    'StrategyMemoryEntry',
    'HistoryMemoryEntry',
    'RelationshipMemoryEntry',
    'PromptMemoryEntry',
    'MemoryType',
    'create_agent_memory_store',
    
    # Memory Manager
    'AgentMemoryManager',
    'create_agent_memory_manager',
    
    # Prompt Builder
    'PromptMemoryBuilder',
    'create_prompt_memory_builder'
]

__version__ = "1.0.0"
__author__ = "MSDI AI / SSI System"
__description__ = "SSI V5 Agents Module - Sprint 11.5"