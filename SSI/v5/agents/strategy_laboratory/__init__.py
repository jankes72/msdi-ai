"""
SSI V5 - Strategy Laboratory Module

Główny modul Strategy Laboratory dla systemu SSI V5.

Struktura modulu:
SSI/v5/agents/strategy_laboratory/
├── __init__.py                 # Inicjalizacja modulu
├── strategy_models.py          # Modele danych strategii
├── experiment_models.py        # Modele danych eksperymentów
├── strategy_manager.py         # Manager strategii
├── experiment_manager.py       # Manager eksperymentów
├── strategy_ranking_engine.py  # Silnik rankingu strategii
├── strategy_memory.py          # Pamiec strategii
├── memory_integrator.py        # Integracja z pamięcią systemu
├── ifc_integrator.py           # Integracja z IFC
└── behavior_evolution.py       # Mechanizm ewolucji zachowania

Wspolpraca z:
- SSI/v5/core/information_flow_controller/  # IFC
- SSI/v5/memory/                        # Memory Ecosystem
- SSI/v5/agents/                        # Agent System

Zasada: Wszystkie operacje laboratoryjne przechodzą przez IFC.
"""

# Strategy Models
from .strategy_models import (
    Strategy,
    StrategyParameters,
    StrategyResult,
    StrategyEvaluation,
    StrategyRanking,
    StrategyStatus,
    StrategyVersion,
    create_strategy,
    update_strategy_stats
)

# Experiment Models  
from .experiment_models import (
    Experiment,
    ExperimentParameters,
    ExperimentResult,
    ExperimentComparison,
    ExperimentStatus,
    ExperimentType,
    create_experiment,
    update_experiment_stats
)

# Strategy Manager
from .strategy_manager import (
    StrategyManager,
    create_strategy_manager,
    get_strategy_manager
)

# Experiment Manager
from .experiment_manager import (
    ExperimentManager,
    create_experiment_manager,
    get_experiment_manager
)

# Strategy Ranking Engine
from .strategy_ranking_engine import (
    StrategyRankingEngine,
    create_ranking_engine,
    get_ranking_engine,
    RankingCriteria,
    RankingWeights
)

# Strategy Memory
from .strategy_memory import (
    StrategyMemory,
    StrategyMemoryConfig,
    AgentStrategyLaboratory,
    create_strategy_memory,
    get_strategy_memory
)

# Memory Integrator
from .memory_integrator import (
    StrategyMemoryIntegrator,
    create_memory_integrator,
    get_memory_integrator
)

# IFC Integrator
from .ifc_integrator import (
    StrategyIFCIntegrator,
    create_ifc_integrator,
    get_ifc_integrator
)

# Behavior Evolution
from .behavior_evolution import (
    BehaviorEvolutionConfig,
    BehaviorEvolutionEvent,
    BehaviorEvolutionType,
    EvolutionDirection,
    InfluenceFactor,
    AgentBehaviorProfile,
    StrategyInfluenceAnalysis,
    BehaviorEvolutionEngine,
    create_behavior_evolution_engine,
    get_behavior_evolution_engine
)

__all__ = [
    # Strategy Models
    'Strategy',
    'StrategyParameters', 
    'StrategyResult',
    'StrategyEvaluation',
    'StrategyRanking',
    'StrategyStatus',
    'StrategyVersion',
    'create_strategy',
    'update_strategy_stats',
    
    # Experiment Models
    'Experiment',
    'ExperimentParameters',
    'ExperimentResult',
    'ExperimentComparison',
    'ExperimentStatus',
    'ExperimentType',
    'create_experiment',
    'update_experiment_stats',
    
    # Strategy Manager
    'StrategyManager',
    'create_strategy_manager',
    'get_strategy_manager',
    
    # Experiment Manager
    'ExperimentManager',
    'create_experiment_manager',
    'get_experiment_manager',
    
    # Strategy Ranking Engine
    'StrategyRankingEngine',
    'create_ranking_engine',
    'get_ranking_engine',
    'RankingCriteria',
    'RankingWeights',
    
    # Strategy Memory
    'StrategyMemory',
    'StrategyMemoryConfig',
    'AgentStrategyLaboratory',
    'create_strategy_memory',
    'get_strategy_memory',
    
    # Memory Integrator
    'StrategyMemoryIntegrator',
    'create_memory_integrator',
    'get_memory_integrator',
    
    # IFC Integrator
    'StrategyIFCIntegrator',
    'create_ifc_integrator',
    'get_ifc_integrator',
    
    # Behavior Evolution
    'BehaviorEvolutionConfig',
    'BehaviorEvolutionEvent',
    'BehaviorEvolutionType',
    'EvolutionDirection',
    'InfluenceFactor',
    'AgentBehaviorProfile',
    'StrategyInfluenceAnalysis',
    'BehaviorEvolutionEngine',
    'create_behavior_evolution_engine',
    'get_behavior_evolution_engine'
]

__version__ = "1.0.0"
__author__ = "MSDI AI / SSI System"
__description__ = "SSI V5 Strategy Laboratory Module - Phase 2.3"