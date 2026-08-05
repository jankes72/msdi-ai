# SSI V5 - Memory Stores
# ETAP 1.2.7.3: Adaptive Knowledge Ecosystem

"""
Memory Stores - Systemy przechowywania wiedzy SSI V5.

Struktura:
    BaseMemoryStore (abstrakcyjna)
        |
        +-- ModelMemoryStore (doświadczenia modeli)
        +-- AgentMemoryStore (doświadczenia agentów)
        +-- ExperimentMemoryStore (wyniki eksperymentów)

Kontrakt:
    - Każdy Store dziedziczy z BaseMemoryStore
    - Wspólna struktura MemoryRecord
    - Interfejs: save(), get(), find(), delete(), all(), count()
"""

from .base_store import BaseMemoryStore, MemoryRecord, MemoryQuery
from .model_store import ModelMemoryStore
from .agent_store import AgentMemoryStore
from .experiment_store import ExperimentMemoryStore

__all__ = [
    'BaseMemoryStore',
    'MemoryRecord',
    'MemoryQuery',
    'ModelMemoryStore',
    'AgentMemoryStore',
    'ExperimentMemoryStore'
]
