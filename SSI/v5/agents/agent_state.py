"""
SSI V5 - Agent State
Stan i zarzadzanie stanem agentow

Zgodnie z dokumentacja Sprint 11.5:
- Agent Runtime Foundation
- Memory Observation System
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

from .agents_config import AgentStatus, AgentType, StrategyType, PersonalityTrait


@dataclass
class DecisionRecord:
    """Rekord decyzji agenta."""
    
    decision_id: str
    timestamp: str
    
    # Decyzja
    decision_type: str
    choice: Any
    confidence: float = 0.0
    
    # Dane wejsciowe
    input_data: Dict[str, Any] = field(default_factory=dict)
    used_sources: List[str] = field(default_factory=list)
    
    # Analiza
    analysis_result: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    
    # Wynik
    outcome: Optional[Any] = None
    success: Optional[bool] = None
    
    # Ocena
    evaluation: float = 0.0  # 0-1
    feedback: str = ""
    
    # Metadata
    strategy_used: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BehaviorRecord:
    """Rekord zachowania agenta."""
    
    record_id: str
    timestamp: str
    
    # Zachowanie
    behavior_type: str
    action: str
    description: str = ""
    
    # Kontekst
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Wykorzystane dane
    data_used: List[str] = field(default_factory=list)
    
    # Skutecznosc
    effectiveness: float = 0.0  # 0-1
    
    # Bledy
    errors: List[str] = field(default_factory=list)
    corrections: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyRecord:
    """Rekord strategii agenta."""
    
    # Pola wymagane
    record_id: str
    strategy_name: str
    usage_timestamp: str
    
    # Pola z domyslnymi wartosciami
    strategy_type: str = ""
    
    # Wynik
    result: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    confidence: float = 0.0
    
    # Skutecznosc
    effectiveness: float = 0.0  # 0-1
    
    # Kontekst
    context: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HistoryEntry:
    """Wpis w historii agenta."""
    
    entry_id: str
    timestamp: str
    event_type: str
    
    # Treść
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Powiazania
    related_decision_id: Optional[str] = None
    related_behavior_id: Optional[str] = None
    related_strategy_id: Optional[str] = None
    
    # Kategorie
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RelationshipEntry:
    """Wpis w pamieci relacji agenta."""
    
    relationship_id: str
    other_agent_id: str
    relationship_type: str  # "trust", "conflict", "collaboration", "competition"
    
    # Wartość
    value: float = 0.0  # -1 (konflikt) do +1 (zaufanie)
    
    # Historia
    interactions: int = 0
    positive_interactions: int = 0
    negative_interactions: int = 0
    
    # Ostatnie zdarzenie
    last_interaction: str = ""
    last_interaction_type: str = ""
    last_interaction_result: str = ""
    
    # Współpraca
    collaboration_score: float = 0.0
    information_shared: int = 0
    information_received: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentRuntimeState:
    """Stan runtime pojedynczego agenta."""
    
    agent_id: str
    
    # Status
    status: str = AgentStatus.INITIALIZED.value
    last_status_change: str = ""
    
    # Czas
    created_time: str = ""
    last_activity_time: str = ""
    total_active_time: float = 0.0
    cycle_count: int = 0
    
    # Decyzje
    decisions: List[DecisionRecord] = field(default_factory=list)
    total_decisions: int = 0
    successful_decisions: int = 0
    
    # Zachowania
    behaviors: List[BehaviorRecord] = field(default_factory=list)
    total_behaviors: int = 0
    
    # Strategie
    strategies: List[StrategyRecord] = field(default_factory=list)
    current_strategy: str = ""
    strategy_success_rate: Dict[str, float] = field(default_factory=dict)
    
    # Historia
    history: List[HistoryEntry] = field(default_factory=list)
    total_history_entries: int = 0
    
    # Relacje
    relationships: List[RelationshipEntry] = field(default_factory=list)
    total_relationships: int = 0
    
    # Bledy
    errors: List[str] = field(default_factory=list)
    total_errors: int = 0
    last_error: str = ""
    
    # Metryki
    avg_confidence: float = 0.0
    avg_effectiveness: float = 0.0
    avg_correctness: float = 0.0
    
    # Pamiec
    memory_loaded: bool = False
    memory_sync_count: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMemoryState:
    """Stan pamieci agenta."""
    
    agent_id: str
    
    # Flagi
    loaded: bool = False
    persistence_enabled: bool = True
    sync_enabled: bool = True
    
    # Statystyki
    read_operations: int = 0
    write_operations: int = 0
    sync_operations: int = 0
    last_sync_time: str = ""
    
    # Rozm insert
    personality_entries: int = 0
    behavior_entries: int = 0
    strategy_entries: int = 0
    history_entries: int = 0
    relationship_entries: int = 0
    prompt_memory_entries: int = 0
    
    # Bledy
    errors: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentStateManager:
    """Manager stanu pojedynczego agenta."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._runtime_state = AgentRuntimeState(agent_id=agent_id)
        self._memory_state = AgentMemoryState(agent_id=agent_id)
        
    def initialize(self, created_time: Optional[str] = None) -> None:
        """Inicjalizacja stanu agenta."""
        now = datetime.now().isoformat()
        self._runtime_state.created_time = created_time or now
        self._runtime_state.last_activity_time = now
        self._runtime_state.status = AgentStatus.INITIALIZED.value
        self._runtime_state.last_status_change = now
        
        self._memory_state.loaded = False
        self._memory_state.persistence_enabled = True
        
    def set_status(self, status: AgentStatus) -> None:
        """Ustawienie statusu agenta."""
        now = datetime.now().isoformat()
        self._runtime_state.status = status.value
        self._runtime_state.last_status_change = now
        
    def update_activity_time(self, duration: float = 0.0) -> None:
        """Aktualizacja czasu aktywnosci agenta."""
        now = datetime.now().isoformat()
        self._runtime_state.last_activity_time = now
        self._runtime_state.total_active_time += duration
        
    def increment_cycle(self) -> None:
        """Zwiek vreme licznika cykli."""
        self._runtime_state.cycle_count += 1
        
    def add_decision(self, decision: DecisionRecord) -> None:
        """Dodanie nowej decyzji."""
        self._runtime_state.decisions.append(decision)
        self._runtime_state.total_decisions += 1
        
        if decision.success:
            self._runtime_state.successful_decisions += 1
            
        # Aktualizacja srednich
        self._update_averages()
        
    def add_behavior(self, behavior: BehaviorRecord) -> None:
        """Dodanie nowego zachowania."""
        self._runtime_state.behaviors.append(behavior)
        self._runtime_state.total_behaviors += 1
        
    def add_strategy_record(self, strategy: StrategyRecord) -> None:
        """Dodanie nowego rekordu strategii."""
        self._runtime_state.strategies.append(strategy)
        
        # Aktualizacja przydatnosci
        if strategy.strategy_name not in self._runtime_state.strategy_success_rate:
            self._runtime_state.strategy_success_rate[strategy.strategy_name] = 0.0
            
        # Aktualizacja przydatnosc
        current_rate = self._runtime_state.strategy_success_rate[strategy.strategy_name]
        new_rate = (current_rate * (len([s for s in self._runtime_state.strategies 
                                         if s.strategy_name == strategy.strategy_name]) - 1) + 
                   (1.0 if strategy.success else 0.0)) / len([s for s in self._runtime_state.strategies 
                                                              if s.strategy_name == strategy.strategy_name])
        
        self._runtime_state.strategy_success_rate[strategy.strategy_name] = new_rate
        
    def add_history_entry(self, entry: HistoryEntry) -> None:
        """Dodanie nowego wpisu do historii."""
        self._runtime_state.history.append(entry)
        self._runtime_state.total_history_entries += 1
        
    def add_relationship(self, relationship: RelationshipEntry) -> None:
        """Dodanie nowej relacji."""
        self._runtime_state.relationships.append(relationship)
        self._runtime_state.total_relationships += 1
        
    def add_error(self, error: str) -> None:
        """Dodanie bledu."""
        self._runtime_state.errors.append(error)
        self._runtime_state.total_errors += 1
        self._runtime_state.last_error = error
        
    def add_memory_error(self, error: str) -> None:
        """Dodanie bledu pamieci."""
        self._memory_state.errors.append(error)
        
    def update_memory_stats(self, read_ops: int = 0, write_ops: int = 0, sync_ops: int = 0) -> None:
        """Aktualizacja statystyk pamieci."""
        self._memory_state.read_operations += read_ops
        self._memory_state.write_operations += write_ops
        self._memory_state.sync_operations += sync_ops
        self._memory_state.last_sync_time = datetime.now().isoformat()
        
    def set_memory_loaded(self, loaded: bool = True, persistence: bool = True) -> None:
        """Ustawienie flagi zaladowania pamieci."""
        self._memory_state.loaded = loaded
        self._memory_state.persistence_enabled = persistence
        self._runtime_state.memory_loaded = loaded
        
    def update_memory_counts(self, personality: int = 0, behavior: int = 0, strategy: int = 0,
                           history: int = 0, relationship: int = 0, prompt: int = 0) -> None:
        """Aktualizacja liczb wpisow w pamieci."""
        self._memory_state.personality_entries = personality
        self._memory_state.behavior_entries = behavior
        self._memory_state.strategy_entries = strategy
        self._memory_state.history_entries = history
        self._memory_state.relationship_entries = relationship
        self._memory_state.prompt_memory_entries = prompt
        
    def set_current_strategy(self, strategy: str) -> None:
        """Ustawienie aktualnej strategii."""
        self._runtime_state.current_strategy = strategy
        
    def _update_averages(self) -> None:
        """Aktualizacja srednich wartosci."""
        if self._runtime_state.total_decisions > 0:
            successful = self._runtime_state.successful_decisions
            self._runtime_state.avg_correctness = successful / self._runtime_state.total_decisions
            
            confidences = [d.confidence for d in self._runtime_state.decisions if d.confidence > 0]
            if confidences:
                self._runtime_state.avg_confidence = sum(confidences) / len(confidences)
                
        if self._runtime_state.total_behaviors > 0:
            effectiveness = [b.effectiveness for b in self._runtime_state.behaviors if b.effectiveness > 0]
            if effectiveness:
                self._runtime_state.avg_effectiveness = sum(effectiveness) / len(effectiveness)
                
    def get_runtime_state(self) -> AgentRuntimeState:
        """Pobranie stanu runtime."""
        return self._runtime_state
        
    def get_memory_state(self) -> AgentMemoryState:
        """Pobranie stanu pamieci."""
        return self._memory_state
        
    def get_full_state(self) -> Dict[str, Any]:
        """Pobranie pelnego stanu agenta."""
        return {
            "runtime_state": asdict(self._runtime_state),
            "memory_state": asdict(self._memory_state)
        }
        
    def save_state(self, base_path: str) -> bool:
        """Zapis stanu do pliku."""
        try:
            os.makedirs(base_path, exist_ok=True)
            
            # Runtime state
            runtime_path = os.path.join(base_path, f"{self.agent_id}_runtime_state.json")
            with open(runtime_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self._runtime_state), f, indent=4, ensure_ascii=False)
                
            # Memory state
            memory_path = os.path.join(base_path, f"{self.agent_id}_memory_state.json")
            with open(memory_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self._memory_state), f, indent=4, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Error saving agent state: {e}")
            return False
            
    def load_state(self, base_path: str) -> bool:
        """Zaladowanie stanu z pliku."""
        try:
            # Runtime state
            runtime_path = os.path.join(base_path, f"{self.agent_id}_runtime_state.json")
            if os.path.exists(runtime_path):
                with open(runtime_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._runtime_state = AgentRuntimeState(**data)
                    
            # Memory state
            memory_path = os.path.join(base_path, f"{self.agent_id}_memory_state.json")
            if os.path.exists(memory_path):
                with open(memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._memory_state = AgentMemoryState(**data)
                    
            return True
            
        except Exception as e:
            print(f"Error loading agent state: {e}")
            return False


def create_agent_state_manager(agent_id: str) -> AgentStateManager:
    """Tworzenie managera stanu agenta."""
    return AgentStateManager(agent_id)


if __name__ == "__main__":
    # Test stanu agenta
    print("Testing Agent State Manager...")
    
    manager = create_agent_state_manager("01")
    manager.initialize()
    
    print(f"Agent ID: {manager.agent_id}")
    print(f"Status: {manager.get_runtime_state().status}")
    
    # dodawanie decyzji
    decision = DecisionRecord(
        decision_id="decision_001",
        timestamp=datetime.now().isoformat(),
        decision_type="prediction",
        choice="win",
        confidence=0.85,
        success=True,
        strategy_used="analytical"
    )
    
    manager.add_decision(decision)
    print(f"Total decisions: {manager.get_runtime_state().total_decisions}")
    
    # Aktualizacja strategii
    manager.set_current_strategy("analytical")
    print(f"Current strategy: {manager.get_runtime_state().current_strategy}")
    
    # Zapis i odczyt
    base_path = "D:\\sts\\aplikacjaTyperBetAi\\SSI\\v5\\agents\\test"
    if manager.save_state(base_path):
        print("✓ State saved")
    
    new_manager = create_agent_state_manager("01")
    if new_manager.load_state(base_path):
        print("✓ State loaded")
        print(f"Loaded decisions: {new_manager.get_runtime_state().total_decisions}")
    
    print("Agent State Manager test completed!")