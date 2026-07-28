"""
SSI Core Module
Podstawowe klasy i interfejsy systemu SSI

Zawiera:
- SSISystem: Główny system zarządzania
- SSIModule: Klasa bazowa dla modułów
- SSIComponent: Klasa bazowa dla komponentów
- Interfejsy: DataProvider, MemoryAccess, DecisionMaker, itd.
- Base classes: BaseWorld, BaseAgent, BaseStrategy

Wersja: 1.0
Data: 2026-07-28
"""

from .system import SSISystem, SystemStatus, SystemPhase, SystemMetadata, ModuleInfo
from .module import SSIModule, BaseModule, ModuleStatus, ModuleType, ModuleConfig
from .component import SSIComponent, BaseComponent, ComponentStatus, ComponentType, ComponentConfig
from .interfaces import (
    DataProvider, MemoryAccess, DecisionMaker, 
    WorldAccess, AgentAccess, StrategyAccess, SSIInterface
)
from .base_classes import (
    BaseWorld, WorldType, WorldStatus, WorldConfig,
    BaseAgent, AgentStatus, AgentType, PersonalityVector, EmotionalState, TrustEntry,
    BaseStrategy, StrategyStatus, StrategyRanking, StrategyConfig
)

__all__ = [
    # System
    'SSISystem', 'SystemStatus', 'SystemPhase', 'SystemMetadata', 'ModuleInfo',
    # Module
    'SSIModule', 'BaseModule', 'ModuleStatus', 'ModuleType', 'ModuleConfig',
    # Component
    'SSIComponent', 'BaseComponent', 'ComponentStatus', 'ComponentType', 'ComponentConfig',
    # Interfaces
    'DataProvider', 'MemoryAccess', 'DecisionMaker', 'WorldAccess', 'AgentAccess', 'StrategyAccess', 'SSIInterface',
    # Base classes
    'BaseWorld', 'WorldType', 'WorldStatus', 'WorldConfig',
    'BaseAgent', 'AgentStatus', 'AgentType', 'PersonalityVector', 'EmotionalState', 'TrustEntry',
    'BaseStrategy', 'StrategyStatus', 'StrategyRanking', 'StrategyConfig'
]
