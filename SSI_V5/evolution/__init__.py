# SSI V5 Evolution Module
# ========================
#
# ETAP: 5.2.7 - Strategy Evolution Engine Foundation
# Data: 2026-08-04
#
# Odpowiedzialnosc:
# - Strategia Evolution Engine: fundament pod przyszla autonomiczna ewolucje strategii
# - Zarzadzanie genomami strategii
# - Kontrolowane mutacje i selekcja
# - Zachowanie historii ewolucji
#
# ZASADY:
# 1. TYLKO LABORATORIUM - nie wplywa na produkcje
# 2. NIE modyfikuje: TrustManager, AgentRuntime, Pipeline, WorldEngine, CollectiveManager
# 3. TYLKO odczyt z: StrategyMemory, CouponLaboratory, PredictionTrace
# 4. Izolowane srodowisko
# 5. Reprodukowalnosc i historycznosc
#
# Architektura:
# StrategyGenome -> (MutationEngine) -> StrategyPopulation
#               -> (EvolutionRecord) -> EvolutionHistory
#
# Autor: Mistral Vibe
# Co-Authored-By: Mistral Vibe <vibe@mistral.ai>

# Import hujnestentacion
from .strategy_genome import (
    StrategyGenome,
    Gene,
    GeneType,
    MutationType
)

from .evolution_record import (
    EvolutionRecord,
    EvolutionHistory,
    EvolutionStatus,
    EvolutionType
)

from .strategy_mutation_engine import (
    StrategyMutationEngine,
    MutationConfig
)

from .strategy_population import (
    StrategyPopulation,
    PopulationStats,
    SelectionResult
)

__all__ = [
    # Strategy Genome
    'StrategyGenome',
    'Gene',
    'GeneType',
    'MutationType',
    
    # Evolution Record
    'EvolutionRecord',
    'EvolutionHistory',
    'EvolutionStatus',
    'EvolutionType',
    
    # Mutation Engine
    'StrategyMutationEngine',
    'MutationConfig',
    
    # Population
    'StrategyPopulation',
    'PopulationStats',
    'SelectionResult'
]
