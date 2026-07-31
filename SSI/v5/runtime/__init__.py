"""
SSI V5 - Runtime Module
Główny modul systemu runtime

Zgodnie z dokumentacja Sprint 11.5:
- Runtime Controller
- Agent Runtime Foundation
- Memory Observation System

Struktura:
SSI/v5/runtime/
├── runtime_controller.py  # Główny kontroler
├── scheduler.py           # Scheduler zadan
├── state_manager.py       # Manager stanow
├── runtime_config.py      # Konfiguracja
└── __init__.py            # Inicjalizacja modułu
"""

# Runtime Controller
from .runtime_controller import (
    SSIRuntimeController,
    create_runtime_controller
)

# Scheduler
from .scheduler import (
    Scheduler,
    ScheduledTask,
    TaskPriority,
    TaskStatus,
    SchedulerMode,
    CycleConfig,
    create_scheduler
)

# State Manager
from .state_manager import (
    StateManager,
    StateType,
    RuntimeState,
    AgentState,
    MemoryState,
    CollectorState,
    FullSystemState,
    create_state_manager
)

# Configuration
from .runtime_config import (
    RuntimeConfig,
    RuntimeMode,
    RuntimeStatus,
    AgentRuntimeMode,
    MemoryConfig,
    CollectorConfig,
    UnifiedInputPackageConfig,
    RuntimeConfigManager,
    create_default_runtime_config,
    create_default_memory_config,
    create_default_collector_config
)

__all__ = [
    # Runtime Controller
    'SSIRuntimeController',
    'create_runtime_controller',
    
    # Scheduler
    'Scheduler',
    'ScheduledTask',
    'TaskPriority',
    'TaskStatus',
    'SchedulerMode',
    'CycleConfig',
    'create_scheduler',
    
    # State Manager
    'StateManager',
    'StateType',
    'RuntimeState',
    'AgentState',
    'MemoryState',
    'CollectorState',
    'FullSystemState',
    'create_state_manager',
    
    # Configuration
    'RuntimeConfig',
    'RuntimeMode',
    'RuntimeStatus',
    'AgentRuntimeMode',
    'MemoryConfig',
    'CollectorConfig',
    'UnifiedInputPackageConfig',
    'RuntimeConfigManager',
    'create_default_runtime_config',
    'create_default_memory_config',
    'create_default_collector_config'
]

__version__ = "1.0.0"
__author__ = "MSDI AI / SSI System"
__description__ = "SSI V5 Runtime Module - Sprint 11.5"