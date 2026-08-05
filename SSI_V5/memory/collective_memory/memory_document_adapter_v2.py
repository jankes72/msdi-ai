"""
SSI V5 - Memory Document Adapter v2
ETAP: 5.4.2.1 - CollectiveMemoryDocument Pipeline

Zrefaktoryzowana wersja - uzywa warstwy adapterow.

Architektura:
    MemoryDocumentAdapter (router)
        |
        +-- adapters/ package
            |
            +-- BaseMemoryAdapter (ABC)
            +-- StrategyMemoryAdapter
            +-- MatchResultAdapter
            +-- TrainingMemoryAdapter
            +-- ObservationMemoryAdapter
            +-- BehaviorMemoryAdapter
            +-- AgentAnalysisMemoryAdapter
            +-- DecisionMemoryAdapter

Zasady:
1. NIE modyfikowac istniejacych klas pamieci
2. Adapter TYLKO konwertuje, NIE przechowuje
3. Nowe typy pamieci - nowy adapter w oddzielnym pliku
4. wyjsciowa struktura to CollectiveMemoryDocument

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 2.0.0
"""

from typing import Any, Optional, List, Dict
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import uuid

# Import CollectiveMemoryDocument z oddzielnego pliku
from .memory_document import CollectiveMemoryDocument

# Import warstwy adapterow
from .adapters import (
    BaseMemoryAdapter,
    find_adapter_for,
    register_adapter,
    get_adapter_registry,
)
from .adapters.base_memory_adapter import BaseMemoryAdapter
from .adapters.strategy_memory_adapter import StrategyMemoryAdapter
from .adapters.match_result_adapter import MatchResultAdapter
from .adapters.training_memory_adapter import TrainingMemoryAdapter
from .adapters.observation_memory_adapter import ObservationMemoryAdapter
from .adapters.behavior_memory_adapter import BehaviorMemoryAdapter
from .adapters.agent_analysis_memory_adapter import AgentAnalysisMemoryAdapter
from .adapters.decision_memory_adapter import DecisionMemoryAdapter


# =============================================================================
# MemoryDocumentAdapter v2 (router)
# =============================================================================

class MemoryDocumentAdapter:
    """
    Adapter konwertujacy istniejace typy pamieci SSI V5 na CollectiveMemoryDocument.
    
    Uzywa warstwy adapterow (adapters/) do konwersji poszczegolnych typow pamieci.
    
    Nowa architektura (ETAP 5.4.2.1):
        - Kazdy typ pamieci ma swuj wlasny adapter
        - Adaptery dziedzicza po BaseMemoryAdapter
        - MemoryDocumentAdapter jest routerem
    
    Metody:
        - convert(obj) -> CollectiveMemoryDocument (auto-detekcja)
        - register_adapter(adapter) -> None (rejestracja nowego adaptera)
        - get_adapter(obj) -> BaseMemoryAdapter (zwraca adapter dla typu)
        - get_supported_types() -> List[str] (lista obslugiwanych typow)
    """
    
    def __init__(self):
        """Inicjalizacja adaptera."""
        self._custom_adapters: List[BaseMemoryAdapter] = []
    
    def convert(self, obj: Any) -> Optional[CollectiveMemoryDocument]:
        """
        Konwertuje dowolny obiekt pamieci na CollectiveMemoryDocument.
        Auto-detekcja typu na podstawie zarejestrowanych adapterow.
        
        Args:
            obj: Obiekt pamieci do konwersji
            
        Returns:
            CollectiveMemoryDocument lub None jesli typ nieobslugiwany
        """
        # Najpierw sprobuj znalezc adapter w globalnym rejestrze
        adapter = find_adapter_for(obj)
        if adapter:
            return adapter.convert(obj)
        
        # Nastepnie sprobuj w custom adapterach
        for custom_adapter in self._custom_adapters:
            if custom_adapter.can_handle(obj):
                return custom_adapter.convert(obj)
        
        return None
    
    def register_adapter(self, adapter: BaseMemoryAdapter) -> None:
        """
        Rejestruje nowy adapter.
        
        Args:
            adapter: Nowy adapter do zarejestrowania
        """
        register_adapter(adapter)
        if adapter not in self._custom_adapters:
            self._custom_adapters.append(adapter)
    
    def get_adapter(self, obj: Any) -> Optional[BaseMemoryAdapter]:
        """
        Zwraca adapter dla danego obiektu.
        
        Args:
            obj: Obiekt pamieci
            
        Returns:
            BaseMemoryAdapter lub None
        """
        return find_adapter_for(obj)
    
    def get_supported_types(self) -> List[str]:
        """
        Zwraca liste obslugiwanych typow pamieci.
        
        Returns:
            Lista nazw typow pamieci
        """
        registry = get_adapter_registry()
        custom_types = [a.get_source_type() for a in self._custom_adapters]
        all_types = [a.get_source_type() for a in registry] + custom_types
        return list(set(all_types))  # Usun duplikaty
    
    # ========================================================================
    # METODY ZAPASOWE (dla kompatybilnosci wstecz)
    # ========================================================================
    
    def adapt_any(self, obj: Any) -> Optional[CollectiveMemoryDocument]:
        """
        Metoda zapasowa - Deleguje do convert().
        Zachowana dla kompatybilnosci z istniejacym kodem.
        """
        return self.convert(obj)
    
    def adapt_strategy_memory(self, record: Any) -> Optional[CollectiveMemoryDocument]:
        """Metoda zapasowa - uzywa StrategyMemoryAdapter."""
        adapter = StrategyMemoryAdapter()
        if adapter.can_handle(record):
            return adapter.convert(record)
        return None
    
    def adapt_match_result(self, record: Any) -> Optional[CollectiveMemoryDocument]:
        """Metoda zapasowa - uzywa MatchResultAdapter."""
        adapter = MatchResultAdapter()
        if adapter.can_handle(record):
            return adapter.convert(record)
        return None
    
    def adapt_training_memory(self, record: Any) -> Optional[CollectiveMemoryDocument]:
        """Metoda zapasowa - uzywa TrainingMemoryAdapter."""
        adapter = TrainingMemoryAdapter()
        if adapter.can_handle(record):
            return adapter.convert(record)
        return None
    
    def adapt_observation_memory(self, record: Any) -> Optional[CollectiveMemoryDocument]:
        """Metoda zapasowa - uzywa ObservationMemoryAdapter."""
        adapter = ObservationMemoryAdapter()
        if adapter.can_handle(record):
            return adapter.convert(record)
        return None
    
    def adapt_behavior_memory(self, record: Any) -> Optional[CollectiveMemoryDocument]:
        """Metoda zapasowa - uzywa BehaviorMemoryAdapter."""
        adapter = BehaviorMemoryAdapter()
        if adapter.can_handle(record):
            return adapter.convert(record)
        return None
    
    def adapt_agent_analysis_memory(self, record: Any) -> Optional[CollectiveMemoryDocument]:
        """Metoda zapasowa - uzywa AgentAnalysisMemoryAdapter."""
        adapter = AgentAnalysisMemoryAdapter()
        if adapter.can_handle(record):
            return adapter.convert(record)
        return None
    
    def adapt_decision_memory(self, record: Any) -> Optional[CollectiveMemoryDocument]:
        """Metoda zapasowa - uzywa DecisionMemoryAdapter."""
        adapter = DecisionMemoryAdapter()
        if adapter.can_handle(record):
            return adapter.convert(record)
        return None


# =============================================================================
# EKSPORT
# =============================================================================

__all__ = [
    'CollectiveMemoryDocument',
    'MemoryDocumentAdapter',
    'BaseMemoryAdapter',
]
