"""
SSI V5 - Main Module
Glowny modul warstwy V5 (AI Core + Samorozwoj Systemu)

Odpowiedzialnosc:
- Input Layer (warstwa wejscia) - Sprint 11
- Knowledge Memory (pamiec wejsciowa) - Sprint 12
- LLM Core (model jezykowy) - Sprint 13
- Classification & Routing (klasyfikacja i routowanie) - Sprint 14
- Developer Panel (panel programisty) - Sprint 15
- User Panel (panel uzytkownika) - Sprint 16
- Model Router (zarzadzanie modelami) - Sprint 17
- Laboratories Integration (integracja laboratoriow) - Sprint 18
- Collective System (kolektyw agentow) - Sprint 19

FAZA 2 (Aktualna):
- Core Layer: Information Flow Controller, Message Validation, Context Integrity
- Strategy Laboratory: Agent Strategy Management
- Decision Layer: System Decision Making
- Developer Interface: Developer Communication Channel

Zaleznosci:
- SSI.v2 (V2 Model Laboratory)
- SSI.v3 (V3 World Memory System)
- SSI.v4 (V4 Agent Evolution)

Wersja: 2.0.0
Data: 2026-08-01
"""

# Core Layer (Phase 2)
from SSI.v5.core import (
    information_flow_controller,
    validation,
    context_integrity,
    decision_layer,
    developer_interface
)

# Input Layer (Sprint 11)
from SSI.v5.input_layer import (
    data_models,
    v2_collector
)

# Existing modules
from SSI.v5.agents import (
    agent_manager,
    agent_runtime,
    agent_memory_store,
    agent_memory_manager
)

from SSI.v5.teacher import (
    teacher_engine,
    teacher_config
)

from SSI.v5.runtime import (
    runtime_controller,
    state_manager,
    runtime_config,
    scheduler
)

from SSI.v5.runtime.llm_queue import (
    llm_queue_manager,
    model_context,
    queue_config
)

from SSI.v5.memory import (
    memory_types,
    model_memory_store
)

__all__ = [
    # Core Layer (Phase 2)
    'information_flow_controller',
    'validation',
    'context_integrity',
    'decision_layer',
    'developer_interface',
    
    # Input Layer
    'data_models',
    'v2_collector',
    
    # Existing modules
    'agent_manager',
    'agent_runtime',
    'agent_memory_store',
    'agent_memory_manager',
    
    'teacher_engine',
    'teacher_config',
    
    'runtime_controller',
    'state_manager',
    'runtime_config',
    'scheduler',
    
    'llm_queue_manager',
    'model_context',
    'queue_config',
    
    'memory_types',
    'model_memory_store'
]

__version__ = "2.0.0"
__author__ = "MSDI AI / SSI System"
__phase__ = "2"
