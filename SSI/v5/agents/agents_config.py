"""
SSI V5 - Agents Configuration
Konfiguracja agentow dla systemu SSI V5

Zgodnie z dokumentacja Sprint 11.5:
- Agent Runtime Foundation
- Memory Observation System
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class AgentStatus(Enum):
    """Status agenta."""
    INITIALIZED = "initialized"
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class AgentType(Enum):
    """Typ agenta."""
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    CONSERVATIVE = "conservative"
    RISK_TAKER = "risk_taker"
    BALANCED = "balanced"
    EXPLORER = "explorer"


class StrategyType(Enum):
    """Typy strategii agentow."""
    ANALYTICAL = "analytical"
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    PASSIVE = "passive"
    ADAPTIVE = "adaptive"
    RANDOM = "random"


class PersonalityTrait(Enum):
    """Cechy osobowosci agenta."""
    RISK_TOLERANCE = "risk_tolerance"
    ANALYSIS_DEPTH = "analysis_depth"
    CREATIVITY = "creativity"
    TRUST_V2 = "trust_v2"
    TRUST_V3 = "trust_v3"
    TRUST_V4 = "trust_v4"
    TRUST_EXTERNAL = "trust_external"
    Patience = "patience"
    CURiosity = "curiosity"


@dataclass
class AgentPersonalityConfig:
    """Konfiguracja osobowosci agenta."""
    
    # Wagi cech
    weights: Dict[PersonalityTrait, float] = field(default_factory=dict)
    
    # Typ agenta
    agent_type: AgentType = AgentType.BALANCED
    
    # Opis
    description: str = ""
    
    # Priorytety
    priorities: List[str] = field(default_factory=list)


@dataclass
class AgentStrategyConfig:
    """Konfiguracja strategii agenta."""
    
    default_strategy: StrategyType = StrategyType.ANALYTICAL
    available_strategies: List[StrategyType] = field(default_factory=list)
    strategy_weights: Dict[StrategyType, float] = field(default_factory=dict)
    
    # Adaptacyjnosc
    adaptive: bool = True
    adaptation_rate: float = 0.1


@dataclass
class AgentMemoryConfig:
    """Konfiguracja pamieci agenta."""
    
    enabled: bool = True
    persistence_enabled: bool = True
    
    # Sciezki
    base_path: str = ""
    personality_file: str = "personality.json"
    behavior_file: str = "behavior.json"
    strategy_file: str = "strategy.json"
    history_file: str = "history.json"
    relationship_file: str = "relationship.json"
    prompt_memory_file: str = "prompt_memory.json"
    
    # Ustawienia
    max_history_entries: int = 1000
    max_strategy_entries: int = 500
    max_behavior_entries: int = 1000
    max_relationship_entries: int = 200
    
    # Synchronizacja
    sync_interval: int = 10  # Ilosc cykli


@dataclass
class AgentConfig:
    """Konfiguracja agenta."""
    
    # Podstawowe informacje
    agent_id: str
    name: str
    description: str = ""
    
    # Status
    status: AgentStatus = AgentStatus.INITIALIZED
    type: AgentType = AgentType.BALANCED
    
    # Osobowosc
    personality: AgentPersonalityConfig = field(default_factory=AgentPersonalityConfig)
    
    # Strategie
    strategy: AgentStrategyConfig = field(default_factory=AgentStrategyConfig)
    
    # Pamiec
    memory: AgentMemoryConfig = field(default_factory=AgentMemoryConfig)
    
    # Zaufanie
    trust_v2: float = 0.8
    trust_v3: float = 0.8
    trust_v4: float = 0.8
    trust_external: float = 0.6
    
    # Priorytety
    priority: int = 1
    
    # Ustawienia wykonania
    enabled: bool = True
    auto_start: bool = True
    
    # Metryki
    track_metrics: bool = True
    
    # Dodatkowe ustawienia
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentRuntimeConfig:
    """Konfiguracja runtime agenta."""
    
    # Czas wykonania
    timeout_seconds: int = 300
    max_cycles: int = 0  # 0 = bez limitu
    
    # Retry
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # kolejnosc wykonywania
    execution_order: List[str] = field(default_factory=lambda: [
        "load_memory",
        "fetch_data",
        "analyze",
        "decide",
        "save_experience",
        "update_history"
    ])
    
    # Integracja
    use_unified_package: bool = True
    
    # Debug
    debug: bool = False
    verbose: bool = False


# Funkcje fabryczne do tworzenia domyslnych konfiguracji

def create_default_personality(agent_type: AgentType = AgentType.BALANCED) -> AgentPersonalityConfig:
    """Tworzenie domyslnej osobowosci."""
    
    if agent_type == AgentType.ANALYTICAL:
        weights = {
            PersonalityTrait.RISK_TOLERANCE: 0.3,
            PersonalityTrait.ANALYSIS_DEPTH: 0.9,
            PersonalityTrait.CREATIVITY: 0.4,
            PersonalityTrait.TRUST_V2: 0.8,
            PersonalityTrait.TRUST_V3: 0.8,
            PersonalityTrait.TRUST_V4: 0.8,
            PersonalityTrait.TRUST_EXTERNAL: 0.6
        }
        priorities = ["accuracy", "analysis", "verification"]
        
    elif agent_type == AgentType.CREATIVE:
        weights = {
            PersonalityTrait.RISK_TOLERANCE: 0.7,
            PersonalityTrait.ANALYSIS_DEPTH: 0.5,
            PersonalityTrait.CREATIVITY: 0.9,
            PersonalityTrait.TRUST_V2: 0.7,
            PersonalityTrait.TRUST_V3: 0.7,
            PersonalityTrait.TRUST_V4: 0.7,
            PersonalityTrait.TRUST_EXTERNAL: 0.7
        }
        priorities = ["innovation", "exploration", "creativity"]
        
    elif agent_type == AgentType.CONSERVATIVE:
        weights = {
            PersonalityTrait.RISK_TOLERANCE: 0.2,
            PersonalityTrait.ANALYSIS_DEPTH: 0.8,
            PersonalityTrait.CREATIVITY: 0.3,
            PersonalityTrait.TRUST_V2: 0.9,
            PersonalityTrait.TRUST_V3: 0.9,
            PersonalityTrait.TRUST_V4: 0.9,
            PersonalityTrait.TRUST_EXTERNAL: 0.5
        }
        priorities = ["safety", "stability", "verification"]
        
    elif agent_type == AgentType.RISK_TAKER:
        weights = {
            PersonalityTrait.RISK_TOLERANCE: 0.9,
            PersonalityTrait.ANALYSIS_DEPTH: 0.4,
            PersonalityTrait.CREATIVITY: 0.6,
            PersonalityTrait.TRUST_V2: 0.6,
            PersonalityTrait.TRUST_V3: 0.6,
            PersonalityTrait.TRUST_V4: 0.6,
            PersonalityTrait.TRUST_EXTERNAL: 0.8
        }
        priorities = ["opportunity", "risk", "reward"]
        
    elif agent_type == AgentType.EXPLORER:
        weights = {
            PersonalityTrait.RISK_TOLERANCE: 0.6,
            PersonalityTrait.ANALYSIS_DEPTH: 0.6,
            PersonalityTrait.CREATIVITY: 0.8,
            PersonalityTrait.TRUST_V2: 0.7,
            PersonalityTrait.TRUST_V3: 0.7,
            PersonalityTrait.TRUST_V4: 0.7,
            PersonalityTrait.TRUST_EXTERNAL: 0.8
        }
        priorities = ["discovery", "exploration", "learning"]
        
    else:  # BALANCED
        weights = {
            PersonalityTrait.RISK_TOLERANCE: 0.5,
            PersonalityTrait.ANALYSIS_DEPTH: 0.7,
            PersonalityTrait.CREATIVITY: 0.5,
            PersonalityTrait.TRUST_V2: 0.8,
            PersonalityTrait.TRUST_V3: 0.8,
            PersonalityTrait.TRUST_V4: 0.8,
            PersonalityTrait.TRUST_EXTERNAL: 0.6
        }
        priorities = ["balance", "adaptation", "performance"]
        
    return AgentPersonalityConfig(
        weights=weights,
        agent_type=agent_type,
        description=f"Default {agent_type.value} personality",
        priorities=priorities
    )


def create_default_strategy() -> AgentStrategyConfig:
    """Tworzenie domyslnej konfiguracji strategii."""
    return AgentStrategyConfig(
        default_strategy=StrategyType.ANALYTICAL,
        available_strategies=[
            StrategyType.ANALYTICAL,
            StrategyType.CONSERVATIVE,
            StrategyType.BALANCED,
            StrategyType.AGGRESSIVE
        ],
        strategy_weights={
            StrategyType.ANALYTICAL: 0.4,
            StrategyType.CONSERVATIVE: 0.2,
            StrategyType.BALANCED: 0.3,
            StrategyType.AGGRESSIVE: 0.1
        },
        adaptive=True,
        adaptation_rate=0.1
    )


def create_default_memory_config(base_path: str, agent_id: str) -> AgentMemoryConfig:
    """Tworzenie domyslnej konfiguracji pamieci."""
    return AgentMemoryConfig(
        enabled=True,
        persistence_enabled=True,
        base_path=os.path.join(base_path, f"agent_{agent_id}"),
        personality_file="personality.json",
        behavior_file="behavior.json",
        strategy_file="strategy.json",
        history_file="history.json",
        relationship_file="relationship.json",
        prompt_memory_file="prompt_memory.json",
        max_history_entries=1000,
        max_strategy_entries=500,
        max_behavior_entries=1000,
        max_relationship_entries=200,
        sync_interval=10
    )


def create_agent_config(agent_id: str, name: str,
                         agent_type: AgentType = AgentType.BALANCED,
                         base_memory_path: str = "D:\\sts\\aplikacjaTyperBetAi\\SSI\\memory\\agents") -> AgentConfig:
    """Tworzenie konfiguracji agenta."""
    
    personality = create_default_personality(agent_type)
    strategy = create_default_strategy()
    memory = create_default_memory_config(base_memory_path, agent_id)
    
    return AgentConfig(
        agent_id=agent_id,
        name=name,
        description=f"Agent {agent_id} - {agent_type.value} type",
        status=AgentStatus.INITIALIZED,
        type=agent_type,
        personality=personality,
        strategy=strategy,
        memory=memory,
        trust_v2=personality.weights.get(PersonalityTrait.TRUST_V2, 0.8),
        trust_v3=personality.weights.get(PersonalityTrait.TRUST_V3, 0.8),
        trust_v4=personality.weights.get(PersonalityTrait.TRUST_V4, 0.8),
        trust_external=personality.weights.get(PersonalityTrait.TRUST_EXTERNAL, 0.6),
        priority=1,
        enabled=True,
        auto_start=True,
        track_metrics=True
    )


def create_all_agent_configs(base_memory_path: str = "D:\\sts\\aplikacjaTyperBetAi\\SSI\\memory\\agents") -> Dict[str, AgentConfig]:
    """Tworzenie konfiguracji dla wszystkich 6 agentow."""
    
    agent_types = [
        AgentType.ANALYTICAL,
        AgentType.CREATIVE,
        AgentType.CONSERVATIVE,
        AgentType.RISK_TAKER,
        AgentType.BALANCED,
        AgentType.EXPLORER
    ]
    
    configs = {}
    for i, agent_type in enumerate(agent_types, 1):
        agent_id = f"0{i}"
        name = f"Agent_{agent_id}"
        config = create_agent_config(
            agent_id=agent_id,
            name=name,
            agent_type=agent_type,
            base_memory_path=base_memory_path
        )
        configs[agent_id] = config
        
    return configs


def save_agent_configs(configs: Dict[str, AgentConfig], base_path: str = "D:\\sts\\aplikacjaTyperBetAi\\SSI\\v5\\agents") -> bool:
    """Zapis konfiguracji agentow do pliku."""
    try:
        path = os.path.join(base_path, "agents_configs.json")
        data = {agent_id: config.__dict__ for agent_id, config in configs.items()}
        
        # Konwersja enumow do stringow
        for agent_id, config_data in data.items():
            if 'personality' in config_data:
                if 'weights' in config_data['personality']:
                    config_data['personality']['weights'] = {
                        k.value if hasattr(k, 'value') else k: v
                        for k, v in config_data['personality']['weights'].items()
                    }
                if 'agent_type' in config_data['personality']:
                    config_data['personality']['agent_type'] = (
                        config_data['personality']['agent_type'].value
                        if hasattr(config_data['personality']['agent_type'], 'value')
                        else config_data['personality']['agent_type']
                    )
                    
            if 'strategy' in config_data:
                if 'default_strategy' in config_data['strategy']:
                    config_data['strategy']['default_strategy'] = (
                        config_data['strategy']['default_strategy'].value
                        if hasattr(config_data['strategy']['default_strategy'], 'value')
                        else config_data['strategy']['default_strategy']
                    )
                if 'available_strategies' in config_data['strategy']:
                    config_data['strategy']['available_strategies'] = [
                        s.value if hasattr(s, 'value') else s
                        for s in config_data['strategy']['available_strategies']
                    ]
                    
            if 'type' in config_data:
                config_data['type'] = (
                    config_data['type'].value if hasattr(config_data['type'], 'value')
                    else config_data['type']
                )
            
            if 'status' in config_data:
                config_data['status'] = (
                    config_data['status'].value if hasattr(config_data['status'], 'value')
                    else config_data['status']
                )
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        return True
        
    except Exception as e:
        print(f"Error saving agent configs: {e}")
        return False


def load_agent_configs(path: str = "D:\\sts\\aplikacjaTyperBetAi\\SSI\\v5\\agents\\agents_configs.json") -> Dict[str, AgentConfig]:
    """Zaladowanie konfiguracji agentow z pliku."""
    try:
        if not os.path.exists(path):
            return {}
            
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        configs = {}
        for agent_id, config_data in data.items():
            # Konwersja stringow do enumow
            if 'type' in config_data and isinstance(config_data['type'], str):
                config_data['type'] = AgentType(config_data['type'])
                
            if 'status' in config_data and isinstance(config_data['status'], str):
                config_data['status'] = AgentStatus(config_data['status'])
                
            if 'personality' in config_data:
                if 'agent_type' in config_data['personality'] and isinstance(config_data['personality']['agent_type'], str):
                    config_data['personality']['agent_type'] = AgentType(config_data['personality']['agent_type'])
                    
                if 'weights' in config_data['personality']:
                    new_weights = {}
                    for k, v in config_data['personality']['weights'].items():
                        try:
                            trait = PersonalityTrait(k)
                            new_weights[trait] = v
                        except ValueError:
                            new_weights[k] = v
                    config_data['personality']['weights'] = new_weights
                    
            if 'strategy' in config_data:
                if 'default_strategy' in config_data['strategy'] and isinstance(config_data['strategy']['default_strategy'], str):
                    config_data['strategy']['default_strategy'] = StrategyType(config_data['strategy']['default_strategy'])
                    
                if 'available_strategies' in config_data['strategy']:
                    config_data['strategy']['available_strategies'] = [
                        StrategyType(s) if isinstance(s, str) else s
                        for s in config_data['strategy']['available_strategies']
                    ]
            
            configs[agent_id] = AgentConfig(**config_data)
            
        return configs
        
    except Exception as e:
        print(f"Error loading agent configs: {e}")
        return {}


if __name__ == "__main__":
    # Test konfiguracji
    print("Testing Agent Configuration...")
    
    # Utworzenie domyslnych konfiguracji
    configs = create_all_agent_configs()
    
    print(f"Created {len(configs)} agent configs")
    
    for agent_id, config in configs.items():
        print(f"\nAgent {agent_id}: {config.name}")
        print(f"  Type: {config.type.value}")
        print(f"  Status: {config.status.value}")
        print(f"  Personality: {config.personality.agent_type.value}")
        print(f"  Default Strategy: {config.strategy.default_strategy.value}")
        print(f"  Memory Path: {config.memory.base_path}")
        
    # Zapis do pliku
    if save_agent_configs(configs):
        print("\n✓ Agent configs saved to file")
    else:
        print("\n✗ Failed to save agent configs")
        
    # Odczyt z pliku
    loaded_configs = load_agent_configs()
    print(f"\n✓ Loaded {len(loaded_configs)} agent configs from file")
    
    print("\nAgent Configuration test completed!")