"""
SSI V5 - Memory Adapters Package
ETAP: 5.4.2.1 - CollectiveMemoryDocument Pipeline

Warstwa adapterow do konwersji istniejacych typow pamieci SSI V5
na spójna strukturę CollectiveMemoryDocument.

Architektura:
    BaseMemoryAdapter (ABC)
        |
        +-- StrategyMemoryAdapter
        +-- WorldMemoryAdapter (MatchResult)
        +-- AgentMemoryAdapter
        +-- ExperimentMemoryAdapter
        +-- TrainingMemoryAdapter
        +-- ObservationMemoryAdapter
        +-- BehaviorMemoryAdapter
        +-- AgentAnalysisMemoryAdapter
        +-- DecisionMemoryAdapter

Zasady:
1. Kazdy adapter dziedziczy po BaseMemoryAdapter
2. Kazdy adapter implementuje can_handle() i convert()
3. Nowe typy pamieci - nowy adapter w oddzielnym pliku
4. NIE modyfikowac istniejacych klas pamieci

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

from .base_memory_adapter import BaseMemoryAdapter
from .strategy_memory_adapter import StrategyMemoryAdapter
from .match_result_adapter import MatchResultAdapter
from .training_memory_adapter import TrainingMemoryAdapter
from .observation_memory_adapter import ObservationMemoryAdapter
from .behavior_memory_adapter import BehaviorMemoryAdapter
from .agent_analysis_memory_adapter import AgentAnalysisMemoryAdapter
from .decision_memory_adapter import DecisionMemoryAdapter

# Rejestr adapterow (lazy loading)
_ADAPTER_REGISTRY = None


def get_adapter_registry():
    """Zwraca zarejestrowane adaptery."""
    global _ADAPTER_REGISTRY
    if _ADAPTER_REGISTRY is None:
        _ADAPTER_REGISTRY = [
            StrategyMemoryAdapter(),
            MatchResultAdapter(),
            TrainingMemoryAdapter(),
            ObservationMemoryAdapter(),
            BehaviorMemoryAdapter(),
            AgentAnalysisMemoryAdapter(),
            DecisionMemoryAdapter(),
        ]
    return _ADAPTER_REGISTRY


def register_adapter(adapter: BaseMemoryAdapter):
    """Rejestruje nowy adapter."""
    global _ADAPTER_REGISTRY
    if _ADAPTER_REGISTRY is None:
        _ADAPTER_REGISTRY = []
    if adapter not in _ADAPTER_REGISTRY:
        _ADAPTER_REGISTRY.append(adapter)


def find_adapter_for(obj) -> 'BaseMemoryAdapter':
    """Znajduje adapter dla danego obiektu."""
    for adapter in get_adapter_registry():
        if adapter.can_handle(obj):
            return adapter
    return None


__all__ = [
    'BaseMemoryAdapter',
    'StrategyMemoryAdapter',
    'MatchResultAdapter',
    'TrainingMemoryAdapter', 
    'ObservationMemoryAdapter',
    'BehaviorMemoryAdapter',
    'AgentAnalysisMemoryAdapter',
    'DecisionMemoryAdapter',
    'get_adapter_registry',
    'register_adapter',
    'find_adapter_for',
]
