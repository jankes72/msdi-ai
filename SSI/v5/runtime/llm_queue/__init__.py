"""
SSI V5 - LLM Queue Module
Zarzadzanie kolejka modeli LLM z ograniczeniem do 1 aktywnego modelu

Zgodnie z dokumentacja:
- 06_AI_LAB_REQUEST_PIPELINE.md (Pipeline do AI Lab)
- 01_SYSTEM_SIGNAL_ARCHITECTURE.md (Ograniczenia sprzetowe)

ZASADA: TYLKO JEDEN MODEL LLM MOZE BYC AKTYWNY
Wzorzec: MODEL START -> WORK -> SAVE MEMORY -> MODEL STOP -> NEXT MODEL

Moduly:
- llm_queue_manager.py: Glowny manager kolejki
- model contexto.py: Kontekst modelu LLM
- queue_config.py: Konfiguracja kolejki
"""

from .llm_queue_manager import (
    LLMQueueManager, 
    LLMQueueConfig, 
    ModelPriority, 
    ModelStatus,
    QueueMode,
    create_llm_queue_manager
)
from .model_context import (
    ModelContext,
    ModelRequest,
    ModelResult,
    ModelType
)
from .queue_config import (
    LLMQueueSettings,
    HardwareConstraints,
    ModelLimits,
    MemoryCleanupStrategy,
    QueueMode,
    create_default_queue_config
)

__all__ = [
    'LLMQueueManager',
    'LLMQueueConfig', 
    'ModelPriority',
    'ModelStatus',
    'QueueMode',
    'create_llm_queue_manager',
    'ModelContext',
    'ModelRequest',
    'ModelResult',
    'ModelType',
    'LLMQueueSettings',
    'HardwareConstraints',
    'ModelLimits',
    'MemoryCleanupStrategy',
    'create_default_queue_config'
]
