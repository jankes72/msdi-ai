"""
SSI V3 - World Knowledge Engine

Warstwa pamięci, wiedzy i światów systemu SSI.

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3 (V3 World System)
- 02_DATA_STRUCTURE.md Sekcja 4 (Struktury Danych V3)

Odpowiedzialność V3:
- Światy danych (Worlds) - Organizacja danych w światy interpretacji
- Metadane - Informacje o danych, modelach, wzorcach
- Pamięć operacyjna - Centralny system pamięci
- Wzorce zachowań - Wykryte i zapamiętane wzorce
- Relacje - Powiązania między obiektami w światach

Architektura V3:
V3 - WORLD KNOWLEDGE ENGINE
├── Memory System
│   ├── Observation Memory (Obserwacje z V2)
│   ├── Pattern Memory (Wzorce)
│   ├── Metadata Memory (Metadane)
│   └── Relationship Memory (Relacje)
├── World System
│   ├── World Manager
│   ├── World Builder
│   └── World Analyzer
└── Intelligence Layer
    ├── Pattern Detector
    ├── Anomaly Detector
    └── Knowledge Graph

Zależności:
- Zależy od: V2 (dane obserwacyjne)
- Wspiera: V4 (agenci korzystają z wiedzy V3)

Wersja: 1.0
Data: 2026-07-28
"""

# Memory System
from .memory import (
    MemoryManager, MemoryConfig, MemoryType,
    ObservationMemory, PatternMemory, MetadataMemory, RelationshipMemory,
    WorldMemory, tworz_memory_manager
)

# World System  
from .worlds import (
    WorldManager, WorldConfig, World,
    WorldAccess, WorldType, WorldStatus, tworz_world_manager,
    # World Knowledge Engine
    WorldKnowledgeEngine, WorldKnowledgeConfig, WorldSource,
    PatternType, EconomicMetric,
    WorldCreator, PatternDetector, EconomicAnalyzer, EVCalculator,
    tworz_world_knowledge_engine
)

# Intelligence Layer (TODO: Do implementacji w późniejszych sprintach)
# from .intelligence import (
#     PatternDetector as IntelligencePatternDetector,
#     AnomalyDetector, KnowledgeGraph, ReasoningEngine,
#     IntelligenceConfig, tworz_intelligence_layer
# )

# Configuration
from .config import (
    V3Config, IntegrationConfig, V4BridgeConfig, MemoryConfig, WorldConfig,
    LogLevel, ValidationMode,
    tworz_v3_config, get_v3_config, reset_v3_config
)

# Main V3 Integration
from .v3_integration import (
    V3Integration, V3IntegrationConfig, IntegrationStatistics,
    ComponentStatus,
    tworz_v3_integration, get_v3_integration, reset_v3_integration
)

# Integration
from .integration import (
    WorldIntegration, WorldIntegrationConfig, IntegrationStatus,
    tworz_integracje_v3 as tworz_world_integration
)

# Re-export V2ToV3Bridge from V2 for backward compatibility
from ..v2.integration.v2_to_v3_bridge import (
    V2ToV3Bridge, BridgeConfig, WorldDataPackage
)

__all__ = [
    # Memory System
    'MemoryManager', 'MemoryConfig', 'MemoryType',
    'ObservationMemory', 'PatternMemory', 'MetadataMemory', 'RelationshipMemory',
    'WorldMemory', 'tworz_memory_manager',
    
    # World System
    'WorldManager', 'WorldConfig', 'World',
    'WorldAccess', 'WorldType', 'WorldStatus', 'tworz_world_manager',
    
    # World Knowledge Engine
    'WorldKnowledgeEngine', 'WorldKnowledgeConfig', 'WorldSource',
    'PatternType', 'EconomicMetric',
    'WorldCreator',
    'EconomicAnalyzer', 'EVCalculator',
    'tworz_world_knowledge_engine',
    
    # Intelligence Layer (TODO: Do implementacji w późniejszych sprintach)
    # 'IntelligencePatternDetector',
    # 'AnomalyDetector', 'KnowledgeGraph', 'ReasoningEngine',
    # 'IntelligenceConfig', 'tworz_intelligence_layer',
    
    # Configuration (Sprint 2)
    'V3Config', 'IntegrationConfig', 'V4BridgeConfig', 'MemoryConfig', 'WorldConfig',
    'LogLevel', 'ValidationMode',
    'tworz_v3_config', 'get_v3_config', 'reset_v3_config',
    
    # Main V3 Integration (Sprint 3)
    'V3Integration', 'V3IntegrationConfig', 'IntegrationStatistics',
    'ComponentStatus',
    'tworz_v3_integration', 'get_v3_integration', 'reset_v3_integration',
    
    # Integration
    'WorldIntegration', 'WorldIntegrationConfig', 'IntegrationStatus',
    'tworz_integracje_v3',
    
    # World Integration (Etap 3C)
    'tworz_world_integration',
    
    # Re-exported from V2 for backward compatibility
    'V2ToV3Bridge', 'BridgeConfig', 'WorldDataPackage'
]
