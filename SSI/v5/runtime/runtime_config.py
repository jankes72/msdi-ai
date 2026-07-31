"""
SSI V5 - Runtime Configuration
Konfiguracja systemu runtime dla SSI V5

Zgodnie z dokumentacja Sprint 11.5:
- Runtime Controller
- Agent Runtime Foundation
- Memory Observation System
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from SSI.v5.agents.agents_config import AgentConfig


class RuntimeMode(Enum):
    """Tryby pracy systemu runtime."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"
    DEBUG = "debug"


class RuntimeStatus(Enum):
    """Status systemu runtime."""
    INITIALIZED = "initialized"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class AgentRuntimeMode(Enum):
    """Tryby pracy agentow."""
    STANDALONE = "standalone"
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"
    HIERARCHICAL = "hierarchical"


@dataclass
class RuntimeConfig:
    """Konfiguracja glownego runtime."""
    
    # Podstawowe ustawienia
    mode: RuntimeMode = RuntimeMode.DEVELOPMENT
    name: str = "SSI_V5_Runtime"
    version: str = "1.0.0"
    description: str = "SSI V5 Runtime Controller - Sprint 11.5"
    
    # Czas pracy
    cycle_duration_hours: int = 5
    auto_start: bool = False
    auto_shutdown: bool = True
    
    # Tryb testowy
    test_mode: bool = False
    test_cycles: int = 10
    
    # Ustawienia zapisu
    auto_save: bool = True
    save_interval_minutes: int = 30
    state_file: str = "runtime_state.json"
    
    # Sciezki
    base_path: str = "D:\\sts\\aplikacjaTyperBetAi\\SSI"
    runtime_path: str = "D:\\sts\\aplikacjaTyperBetAi\\SSI\\v5\\runtime"
    agents_path: str = "D:\\sts\\aplikacjaTyperBetAi\\SSI\\v5\\agents"
    memory_path: str = "D:\\sts\\aplikacjaTyperBetAi\\SSI\\memory"
    
    # Logowanie
    log_level: str = "INFO"
    log_file: str = "runtime.log"
    enable_console_log: bool = True
    
    # Integracja z collectorami
    enable_v2_collector: bool = True
    enable_v3_collector: bool = True
    enable_v4_collector: bool = True
    enable_external_collector: bool = True
    
    # Ustawienia agentow
    enable_all_agents: bool = True
    agent_count: int = 6
    agent_runtime_mode: AgentRuntimeMode = AgentRuntimeMode.STANDALONE
    
    # Pamiec
    enable_memory_system: bool = True
    memory_persistence: bool = True
    
    # Debug
    enable_debug: bool = False
    debug_verbose: bool = False
    
    # Dodatkowe ustawienia
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryConfig:
    """Konfiguracja systemu pamieci."""
    
    enabled: bool = True
    persistence_enabled: bool = True
    
    # Sciezki
    base_path: str = "D:\\sts\\aplikacjaTyperBetAi\\SSI\\memory"
    agents_path: str = "D:\\sts\\aplikacjaTyperBetAi\\SSI\\memory\\agents"
    
    # Typy pamieci
    personality_memory: bool = True
    behavior_memory: bool = True
    strategy_memory: bool = True
    history_memory: bool = True
    relationship_memory: bool = True
    prompt_memory: bool = True
    
    # Ustawienia zapisu
    auto_save: bool = True
    save_interval: int = 10  # Ilosc cykli miedzy zapisami
    backup_enabled: bool = True
    max_backups: int = 5
    
    # Integracja
    sync_with_v3: bool = True
    sync_with_v4: bool = True


@dataclass
class CollectorConfig:
    """Konfiguracja collectorow."""
    
    v2_enabled: bool = True
    v3_enabled: bool = True
    v4_enabled: bool = True
    external_enabled: bool = True
    
    # Kolejnosc wykonywania
    execution_order: List[str] = field(default_factory=lambda: [
        "v2", "v3", "v4", "external"
    ])
    
    # Czas oczekiwania
    timeout_seconds: int = 300
    retry_attempts: int = 3
    
    # Pakiet danych
    create_unified_package: bool = True
    package_name: str = "UnifiedInputPackage"


@dataclass
class UnifiedInputPackageConfig:
    """Konfiguracja dla UnifiedInputPackage."""
    
    include_v2_data: bool = True
    include_v3_knowledge: bool = True
    include_v4_agents: bool = True
    include_external_input: bool = True
    
    # Format danych
    data_format: str = "json"
    compression: bool = False
    
    # Walidacja
    validate_data: bool = True
    validation_strict: bool = False


class RuntimeConfigManager:
    """Manager konfiguracji runtime."""
    
    def __init__(self, config: Optional[RuntimeConfig] = None):
        self.config = config or RuntimeConfig()
        self._loaded = False
        
    def load_config(self, config_path: Optional[str] = None) -> RuntimeConfig:
        """Zaladowanie konfiguracji z pliku."""
        if config_path is None:
            config_path = os.path.join(
                self.config.runtime_path, 
                "runtime_config.json"
            )
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._update_config_from_dict(data)
                self._loaded = True
        
        return self.config
    
    def save_config(self, config_path: Optional[str] = None) -> None:
        """Zapis konfiguracji do pliku."""
        if config_path is None:
            config_path = os.path.join(
                self.config.runtime_path,
                "runtime_config.json"
            )
        
        data = self._config_to_dict()
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def _update_config_from_dict(self, data: Dict[str, Any]) -> None:
        """Aktualizacja konfiguracji z dictionary."""
        for key, value in data.items():
            if hasattr(self.config, key):
                if isinstance(getattr(self.config, key), dict):
                    getattr(self.config, key).update(value)
                else:
                    setattr(self.config, key, value)
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """Konwersja konfiguracji do dictionary."""
        result = {}
        for key, value in self.config.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, Enum):
                    result[key] = value.value
                elif isinstance(value, dict):
                    result[key] = {k: v.value if isinstance(v, Enum) else v 
                                  for k, v in value.items()}
                elif isinstance(value, list):
                    result[key] = [v.value if isinstance(v, Enum) else v 
                                  for v in value]
                else:
                    result[key] = value
        return result
    
    def get_agent_config(self, agent_id: str) -> "AgentConfig":
        """Pobranie konfiguracji dla agenta."""
        from SSI.v5.agents import AgentPersonalityConfig, AgentStrategyConfig, AgentMemoryConfig
        from SSI.v5.agents.agents_config import PersonalityTrait, AgentType, AgentConfig
        
        # Tworzenie konfiguracji osobowosci
        personality = AgentPersonalityConfig(
            weights={
                PersonalityTrait.RISK_TOLERANCE: 0.5,
                PersonalityTrait.ANALYSIS_DEPTH: 0.8,
                PersonalityTrait.CREATIVITY: 0.5,
                PersonalityTrait.TRUST_V2: 0.8,
                PersonalityTrait.TRUST_V3: 0.8,
                PersonalityTrait.TRUST_V4: 0.8
            },
            agent_type=AgentType.BALANCED
        )
        
        # Tworzenie konfiguracji strategii
        strategy = AgentStrategyConfig(
            default_strategy="analytical",
            available_strategies=["analytical", "conservative", "balanced"]
        )
        
        # Tworzenie konfiguracji pamieci
        memory = AgentMemoryConfig(
            base_path=os.path.join(
                self.config.memory_path,
                "agents",
                f"agent_{agent_id}"
            )
        )
        
        return AgentConfig(
            agent_id=agent_id,
            name=f"Agent_{agent_id}",
            description=f"Agent {agent_id} - SSI V5 Runtime",
            personality=personality,
            strategy=strategy,
            memory=memory
        )
    
    def get_default_agent_configs(self) -> List["AgentConfig"]:
        """Pobranie domyslnych konfiguracji dla wszystkich agentow."""
        agents = []
        for i in range(1, 7):
            agent_id = f"0{i}"
            agents.append(self.get_agent_config(agent_id))
        return agents


def create_default_runtime_config() -> RuntimeConfig:
    """Tworzenie domyslnej konfiguracji runtime."""
    return RuntimeConfig()


def create_default_memory_config() -> MemoryConfig:
    """Tworzenie domyslnej konfiguracji pamieci."""
    return MemoryConfig()


def create_default_collector_config() -> CollectorConfig:
    """Tworzenie domyslnej konfiguracji collectorow."""
    return CollectorConfig()


if __name__ == "__main__":
    # Test konfiguracji
    config = create_default_runtime_config()
    print("Runtime Config:")
    print(f"  Mode: {config.mode}")
    print(f"  Cycle Duration: {config.cycle_duration_hours} hours")
    print(f"  Auto Save: {config.auto_save}")
    print(f"  Agents: {config.agent_count}")
    
    manager = RuntimeConfigManager(config)
    agent_configs = manager.get_default_agent_configs()
    print(f"\nGenerated {len(agent_configs)} agent configs")
    for ac in agent_configs:
        print(f"  - {ac.name}: {ac.agent_id}")