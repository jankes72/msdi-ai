"""
SSI V5 - State Manager
Zarzadzanie stanem systemu runtime

Zgodnie z dokumentacja Sprint 11.5:
- Runtime Controller
- Agent Runtime Foundation
- Memory Observation System
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

from .runtime_config import RuntimeConfig, RuntimeStatus, RuntimeConfigManager


class StateType(Enum):
    """Typy stanow systemu."""
    RUNTIME = "runtime"
    AGENTS = "agents"
    MEMORY = "memory"
    COLLECTORS = "collectors"
    FULL = "full"


@dataclass
class RuntimeState:
    """Stan systemu runtime."""
    
    # Podstawowe informacje
    RuntimeName: str = "SSI_V5_Runtime"
    version: str = "1.0.0"
    
    # Czas
    start_time: Optional[str] = None
    stop_time: Optional[str] = None
    last_save_time: Optional[str] = None
    cycle_start_time: Optional[str] = None
    cycle_end_time: Optional[str] = None
    
    # Status
    status: str = RuntimeStatus.INITIALIZED.value
    cycle_count: int = 0
    total_cycles: int = 0
    
    # Statystyki
    execution_time_seconds: float = 0.0
    avg_cycle_time: float = 0.0
    last_cycle_time: float = 0.0
    
    # Bledy
    error_count: int = 0
    last_error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    # Integracja
    collectors_loaded: Dict[str, bool] = field(default_factory=dict)
    agents_loaded: Dict[str, bool] = field(default_factory=dict)
    memory_loaded: bool = False
    
    # Kolejnosc agentow i stan petli
    last_agent_id: Optional[str] = None
    next_agent_id: Optional[str] = None
    current_test_cycle: int = 0
    test_mode: bool = False
    
    # Dodatkowe informacje
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """Stan pojedynczego agenta."""
    
    agent_id: str
    name: str
    status: str = "initialized"
    
    # Czas
    created_time: Optional[str] = None
    last_activity_time: Optional[str] = None
    total_active_time: float = 0.0
    
    # Statystyki
    decisions_made: int = 0
    errors_made: int = 0
    correctness_rate: float = 0.0
    confidence_avg: float = 0.0
    
    # Pamiec
    memory_loaded: bool = False
    memory_size_bytes: int = 0
    last_memory_update: Optional[str] = None
    
    # Strategie
    current_strategy: str = "analytical"
    strategies_used: List[str] = field(default_factory=list)
    strategy_success_rate: Dict[str, float] = field(default_factory=dict)
    
    # Osobowosc
    personality_weights: Dict[str, float] = field(default_factory=dict)
    trust_levels: Dict[str, float] = field(default_factory=dict)
    
    # Historia
    history_entries: int = 0
    relationship_entries: int = 0
    behavior_entries: int = 0


@dataclass
class MemoryState:
    """Stan systemu pamieci."""
    
    loaded: bool = False
    persistence_enabled: bool = True
    
    # Rozm insert
    agents_loaded: int = 0
    total_memory_size_bytes: int = 0
    
    # Statystyki
    read_operations: int = 0
    write_operations: int = 0
    sync_operations: int = 0
    
    # Typy pamieci
    personality_memory_entries: int = 0
    behavior_memory_entries: int = 0
    strategy_memory_entries: int = 0
    history_memory_entries: int = 0
    relationship_memory_entries: int = 0
    prompt_memory_entries: int = 0
    
    # Ostatnie operacje
    last_read_time: Optional[str] = None
    last_write_time: Optional[str] = None
    last_sync_time: Optional[str] = None
    
    # Bledy
    errors: List[str] = field(default_factory=list)


@dataclass
class CollectorState:
    """Stan collectorow."""
    
    v2_status: str = "not_initialized"
    v3_status: str = "not_initialized"
    v4_status: str = "not_initialized"
    external_status: str = "not_initialized"
    
    v2_data_timestamp: Optional[str] = None
    v3_data_timestamp: Optional[str] = None
    v4_data_timestamp: Optional[str] = None
    external_data_timestamp: Optional[str] = None
    
    unified_package_created: bool = False
    unified_package_timestamp: Optional[str] = None
    
    errors: Dict[str, str] = field(default_factory=dict)


@dataclass
class FullSystemState:
    """Pelny stan systemu."""
    
    runtime: RuntimeState = field(default_factory=RuntimeState)
    agents: Dict[str, AgentState] = field(default_factory=dict)
    memory: MemoryState = field(default_factory=MemoryState)
    collectors: CollectorState = field(default_factory=CollectorState)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0.0"


class StateManager:
    """Manager stanow systemu."""
    
    def __init__(self, config: Optional[RuntimeConfig] = None):
        self.config = config or RuntimeConfig()
        self._runtime_state = RuntimeState()
        self._agents_state: Dict[str, AgentState] = {}
        self._memory_state = MemoryState()
        self._collectors_state = CollectorState()
        
        # Sciezki
        self._state_file = os.path.join(
            self.config.runtime_path,
            self.config.state_file
        )
        
        # Flagi
        self._initialized = False
        self._loaded = False
        
    def initialize(self) -> None:
        """Inicjalizacja managera stanu."""
        self._runtime_state.RuntimeName = self.config.name
        self._runtime_state.version = self.config.version
        self._runtime_state.status = RuntimeStatus.INITIALIZED.value
        
        # Inicjalizacja agentow
        for i in range(1, 7):
            agent_id = f"0{i}"
            self._agents_state[agent_id] = AgentState(
                agent_id=agent_id,
                name=f"Agent_{agent_id}",
                created_time=datetime.now().isoformat()
            )
        
        self._memory_state.persistence_enabled = self.config.memory_persistence
        self._initialized = True
        
    def start_cycle(self) -> None:
        """Rozpoczecie nowego cyklu."""
        now = datetime.now().isoformat()
        
        self._runtime_state.cycle_start_time = now
        self._runtime_state.status = RuntimeStatus.RUNNING.value
        self._runtime_state.cycle_count += 1
        self._runtime_state.total_cycles += 1
        
        # Uaktualnienie czasu ostatniego zapis
        if self._runtime_state.last_save_time is None:
            self._runtime_state.last_save_time = now
            
        self._runtime_state.metadata["last_cycle_start"] = now
        
    def end_cycle(self) -> None:
        """Zakonczenie cyklu."""
        now = datetime.now().isoformat()
        self._runtime_state.cycle_end_time = now
        
        # Obliczenie czasu cyklu
        if self._runtime_state.cycle_start_time:
            start_dt = datetime.fromisoformat(self._runtime_state.cycle_start_time)
            end_dt = datetime.fromisoformat(now)
            cycle_time = (end_dt - start_dt).total_seconds()
            self._runtime_state.last_cycle_time = cycle_time
            
            # Aktualizacja sredniego czasu
            if self._runtime_state.cycle_count > 0:
                total_time = (self._runtime_state.avg_cycle_time * 
                            (self._runtime_state.cycle_count - 1)) + cycle_time
                self._runtime_state.avg_cycle_time = total_time / self._runtime_state.cycle_count
        
        self._runtime_state.metadata["last_cycle_end"] = now
        
    def stop(self) -> None:
        """Zatrzymanie systemu."""
        now = datetime.now().isoformat()
        self._runtime_state.stop_time = now
        self._runtime_state.status = RuntimeStatus.STOPPED.value
        
        # Obliczenie calkowitego czasu wykonania
        if self._runtime_state.start_time:
            start_dt = datetime.fromisoformat(self._runtime_state.start_time)
            stop_dt = datetime.fromisoformat(now)
            self._runtime_state.execution_time_seconds = (
                stop_dt - start_dt
            ).total_seconds()
            
        self._runtime_state.metadata["stop_time"] = now
        
    def shutdown(self) -> None:
        """Wylaczenie systemu."""
        self._runtime_state.status = RuntimeStatus.SHUTDOWN.value
        self._runtime_state.metadata["shutdown_time"] = datetime.now().isoformat()
        
    def set_error(self, error: str) -> None:
        """Ustawienie bledu."""
        self._runtime_state.error_count += 1
        self._runtime_state.last_error = error
        self._runtime_state.status = RuntimeStatus.ERROR.value
        
    def add_warning(self, warning: str) -> None:
        """Dodanie ostrzezenia."""
        self._runtime_state.warnings.append(warning)
        
    def update_agent_state(self, agent_id: str, **kwargs) -> None:
        """Aktualizacja stanu agenta."""
        if agent_id in self._agents_state:
            for key, value in kwargs.items():
                if hasattr(self._agents_state[agent_id], key):
                    setattr(self._agents_state[agent_id], key, value)
                    
    def update_collector_status(self, collector_name: str, status: str, 
                                timestamp: Optional[str] = None) -> None:
        """Aktualizacja stanu collectora."""
        if collector_name == "v2":
            self._collectors_state.v2_status = status
            if timestamp:
                self._collectors_state.v2_data_timestamp = timestamp
        elif collector_name == "v3":
            self._collectors_state.v3_status = status
            if timestamp:
                self._collectors_state.v3_data_timestamp = timestamp
        elif collector_name == "v4":
            self._collectors_state.v4_status = status
            if timestamp:
                self._collectors_state.v4_data_timestamp = timestamp
        elif collector_name == "external":
            self._collectors_state.external_status = status
            if timestamp:
                self._collectors_state.external_data_timestamp = timestamp
                
    def set_unified_package_created(self, timestamp: Optional[str] = None) -> None:
        """Oznaczenie ze utworzono UnifiedInputPackage."""
        self._collectors_state.unified_package_created = True
        if timestamp:
            self._collectors_state.unified_package_timestamp = timestamp
        else:
            self._collectors_state.unified_package_timestamp = datetime.now().isoformat()
            
    def update_memory_state(self, **kwargs) -> None:
        """Aktualizacja stanu pamieci."""
        for key, value in kwargs.items():
            if hasattr(self._memory_state, key):
                setattr(self._memory_state, key, value)
                
    def get_runtime_state(self) -> RuntimeState:
        """Pobranie stanu runtime."""
        return self._runtime_state
        
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Pobranie stanu agenta."""
        return self._agents_state.get(agent_id)
        
    def get_all_agents_state(self) -> Dict[str, AgentState]:
        """Pobranie stanu wszystkich agentow."""
        return self._agents_state
        
    def get_memory_state(self) -> MemoryState:
        """Pobranie stanu pamieci."""
        return self._memory_state
        
    def get_collectors_state(self) -> CollectorState:
        """Pobranie stanu collectorow."""
        return self._collectors_state
        
    def get_full_state(self) -> FullSystemState:
        """Pobranie pelnego stanu systemu."""
        return FullSystemState(
            runtime=self._runtime_state,
            agents=self._agents_state,
            memory=self._memory_state,
            collectors=self._collectors_state,
            updated_at=datetime.now().isoformat()
        )
    
    def save_state(self, state_type: StateType = StateType.FULL, 
                   custom_path: Optional[str] = None) -> bool:
        """Zapis stanu do pliku."""
        try:
            if custom_path is None:
                if state_type == StateType.RUNTIME:
                    path = os.path.join(
                        self.config.runtime_path,
                        "runtime_state.json"
                    )
                elif state_type == StateType.AGENTS:
                    path = os.path.join(
                        self.config.runtime_path,
                        "agents_state.json"
                    )
                elif state_type == StateType.MEMORY:
                    path = os.path.join(
                        self.config.runtime_path,
                        "memory_state.json"
                    )
                elif state_type == StateType.COLLECTORS:
                    path = os.path.join(
                        self.config.runtime_path,
                        "collectors_state.json"
                    )
                else:  # FULL
                    path = self._state_file
            else:
                path = custom_path
                
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            if state_type == StateType.RUNTIME:
                data = self._state_to_dict(self._runtime_state)
            elif state_type == StateType.AGENTS:
                data = {aid: self._state_to_dict(state) 
                       for aid, state in self._agents_state.items()}
            elif state_type == StateType.MEMORY:
                data = self._state_to_dict(self._memory_state)
            elif state_type == StateType.COLLECTORS:
                data = self._state_to_dict(self._collectors_state)
            else:  # FULL
                data = self._state_to_dict(self.get_full_state())
                
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
            self._runtime_state.last_save_time = datetime.now().isoformat()
            return True
            
        except Exception as e:
            self.set_error(f"Error saving state: {str(e)}")
            return False
            
    def load_state(self, state_type: StateType = StateType.FULL,
                   custom_path: Optional[str] = None) -> bool:
        """Zaladowanie stanu z pliku."""
        try:
            if custom_path is None:
                if state_type == StateType.RUNTIME:
                    path = os.path.join(
                        self.config.runtime_path,
                        "runtime_state.json"
                    )
                elif state_type == StateType.AGENTS:
                    path = os.path.join(
                        self.config.runtime_path,
                        "agents_state.json"
                    )
                elif state_type == StateType.MEMORY:
                    path = os.path.join(
                        self.config.runtime_path,
                        "memory_state.json"
                    )
                elif state_type == StateType.COLLECTORS:
                    path = os.path.join(
                        self.config.runtime_path,
                        "collectors_state.json"
                    )
                else:  # FULL
                    path = self._state_file
            else:
                path = custom_path
                
            if not os.path.exists(path):
                return False
                
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if state_type == StateType.RUNTIME:
                self._runtime_state = self._dict_to_state(data, RuntimeState)
            elif state_type == StateType.AGENTS:
                self._agents_state = {
                    aid: self._dict_to_state(sdata, AgentState)
                    for aid, sdata in data.items()
                }
            elif state_type == StateType.MEMORY:
                self._memory_state = self._dict_to_state(data, MemoryState)
            elif state_type == StateType.COLLECTORS:
                self._collectors_state = self._dict_to_state(data, CollectorState)
            else:  # FULL
                full_data = self._dict_to_state(data, FullSystemState)
                self._runtime_state = full_data.runtime
                self._agents_state = full_data.agents
                self._memory_state = full_data.memory
                self._collectors_state = full_data.collectors
                
            self._loaded = True
            return True
            
        except Exception as e:
            self.set_error(f"Error loading state: {str(e)}")
            return False
            
    def _state_to_dict(self, state_obj: Any) -> Dict[str, Any]:
        """Konwersja stanu do dictionary."""
        return asdict(state_obj)
        
    def _dict_to_state(self, data: Dict[str, Any], state_class: type) -> Any:
        """Konwersja dictionary do stanu."""
        # Filter out None values for Optional fields
        filtered_data = {k: v for k, v in data.items() if v is not None}
        return state_class(**filtered_data)
        
    def get_status(self) -> Dict[str, Any]:
        """Pobranie statusu systemu."""
        return {
            "runtime_status": self._runtime_state.status,
            "cycle_count": self._runtime_state.cycle_count,
            "total_cycles": self._runtime_state.total_cycles,
            "total_iterations": self._runtime_state.metadata.get("total_iterations", 0),
            "agents_count": len(self._agents_state),
            "memory_loaded": self._memory_state.loaded,
            "collectors": self._collectors_state.__dict__,
            "start_time": self._runtime_state.start_time,
            "last_save": self._runtime_state.last_save_time
        }


def create_state_manager(config: Optional[RuntimeConfig] = None) -> StateManager:
    """Tworzenie managera stanu."""
    return StateManager(config)


if __name__ == "__main__":
    # Test stanu
    from .runtime_config import create_default_runtime_config
    
    config = create_default_runtime_config()
    state_manager = create_state_manager(config)
    
    print("Testing State Manager...")
    state_manager.initialize()
    
    print(f"Initial status: {state_manager.get_runtime_state().status}")
    state_manager.start_cycle()
    print(f"After start_cycle: {state_manager.get_runtime_state().status}")
    
    state = state_manager.get_full_state()
    print(f"Agents count: {len(state.agents)}")
    
    # Test zapisu i odczytu
    state_manager.save_state(StateType.RUNTIME, 
                           "D:\\sts\\aplikacjaTyperBetAi\\SSI\\v5\\runtime\\test_state.json")
    
    new_manager = create_state_manager(config)
    new_manager.load_state(StateType.RUNTIME,
                         "D:\\sts\\aplikacjaTyperBetAi\\SSI\\v5\\runtime\\test_state.json")
    
    loaded_state = new_manager.get_runtime_state()
    print(f"Loaded status: {loaded_state.status}")
    print(f"Loaded version: {loaded_state.version}")
    
    print("State Manager test completed!")