"""
SSI V5 - Model Memory Ecosystem
System pamieci modeli

Zgodnie z dokumentacja:
- 04_AGENT_MEMORY_BEHAVIOR_EVOLUTION.md (Model Memory Ecosystem)
- 01_SYSTEM_SIGNAL_ARCHITECTURE.md (Information Flow)

Model Memory powinien zawierac:
- Training Memory: Pamiec tresowania i uczenia
- Observation Memory: Pamiec obserwacji systemu i agentow
- Behavior Memory: Pamiec zachowan i wzorcou
- Agent Analysis Memory: Pamiec analiz agentow
- Decision Layer Memory: Pamiec podejmowanych decyzji

Moduly:
- model_memory_store.py: Glowny storage pamieci modeli
- memory_types.py: Typy pamieci modeli
"""

from .model_memory_store import (
    ModelMemoryStore,
    TrainingMemoryEntry,
    ObservationMemoryEntry,
    BehaviorMemoryEntry,
    AgentAnalysisMemoryEntry,
    DecisionMemoryEntry,
    ModelMemoryType,
    create_model_memory_store,
    get_model_memory_store
)

from .memory_types import (
    TrainingMemory,
    ObservationMemory,
    BehaviorMemory,
    AgentAnalysisMemory,
    DecisionMemory,
    TrainingPhase,
    ObservationScope,
    BehaviorType,
    AnalysisType
)

__all__ = [
    # Model Memory Store
    'ModelMemoryStore',
    'TrainingMemoryEntry',
    'ObservationMemoryEntry',
    'BehaviorMemoryEntry',
    'AgentAnalysisMemoryEntry',
    'DecisionMemoryEntry',
    'ModelMemoryType',
    'create_model_memory_store',
    'get_model_memory_store',
    
    # Memory Types
    'TrainingMemory',
    'ObservationMemory',
    'BehaviorMemory',
    'AgentAnalysisMemory',
    'DecisionMemory',
    
    # Enums
    'TrainingPhase',
    'ObservationScope',
    'BehaviorType',
    'AnalysisType'
]
