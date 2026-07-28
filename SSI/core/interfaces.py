"""
SSI Interfaces - Interfejsy komunikacji między modułami

Główne interfejsy:
- DataProvider: Dostarcza dane do systemu
- MemoryAccess: Dostęp do systemu pamięci
- DecisionMaker: Podejmowanie decyzji
- WorldAccess: Dostęp do światów
- AgentAccess: Dostęp do agentów

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, List, Optional, Any, Protocol, runtime_checkable
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


@runtime_checkable
class DataProvider(Protocol):
    @abstractmethod
    def get_data(self, data_type: str, **kwargs) -> Any:
        pass
    
    @abstractmethod
    def get_available_data_types(self) -> List[str]:
        pass
    
    @abstractmethod
    def validate_data(self, data: Any, data_type: str) -> bool:
        pass


@runtime_checkable
class MemoryAccess(Protocol):
    @abstractmethod
    def read_memory(self, memory_type: str, key: str, **kwargs) -> Any:
        pass
    
    @abstractmethod
    def write_memory(self, memory_type: str, key: str, data: Any, **kwargs) -> bool:
        pass
    
    @abstractmethod
    def get_memory_types(self) -> List[str]:
        pass
    
    @abstractmethod
    def search_memory(self, memory_type: str, query: Dict[str, Any], **kwargs) -> List[Any]:
        pass


@runtime_checkable
class DecisionMaker(Protocol):
    @abstractmethod
    def make_decision(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def evaluate_decision(self, decision: Dict[str, Any], outcome: Any, **kwargs) -> float:
        pass
    
    @abstractmethod
    def get_decision_types(self) -> List[str]:
        pass


@runtime_checkable
class WorldAccess(Protocol):
    @abstractmethod
    def get_world(self, world_id: str, **kwargs) -> Any:
        pass
    
    @abstractmethod
    def get_world_by_type(self, world_type: str, **kwargs) -> List[Any]:
        pass


@runtime_checkable
class AgentAccess(Protocol):
    @abstractmethod
    def get_agent(self, agent_id: str, **kwargs) -> Any:
        pass
    
    @abstractmethod
    def get_agent_personality(self, agent_id: str, **kwargs) -> Dict[str, Any]:
        pass


@runtime_checkable
class StrategyAccess(Protocol):
    @abstractmethod
    def get_strategy(self, strategy_id: str, **kwargs) -> Any:
        pass
    
    @abstractmethod
    def generate_prediction(self, strategy_id: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        pass


class SSIInterface:
    def __init__(self):
        self.available_methods = self._get_available_methods()
    
    def _get_available_methods(self) -> List[str]:
        return [method for method in dir(self) 
                if not method.startswith('_') and callable(getattr(self, method))]
    
    def get_interface_info(self) -> Dict[str, Any]:
        return {
            "interface_type": self.__class__.__name__,
            "available_methods": self.available_methods,
            "description": self.__doc__ or ""
        }
