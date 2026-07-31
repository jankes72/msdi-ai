"""
SSI V3 Integration - Integracja z innymi warstwami

Moduł odpowiedzialny za:
- Integrację z V2 (odbiór predykcji)
- Integrację z V4 (dostarczanie wiedzy)
- Koordynację między systemami
- Przetwarzanie pakietów danych

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.3 (V3 Integration)
- 10_IMPLEMENTATION_MAP.md Etap 3C

Architektura:
V2 Models → V2ToV3Bridge → V3 Integration → V3 World Knowledge Engine → V3 Memory
                                          ↓
                                     V3ToV4Bridge → V4 Agents

Wersja: 1.0
Data: 2026-07-28
"""

from .world_integration import (
    WorldIntegration,
    WorldIntegrationConfig,
    IntegrationStatus,
    tworz_integracje_v3
)

# Bridge V3 -> V4 (Placeholder dla Sprint 4)
from .v3_to_v4_bridge import (
    V3ToV4Bridge,
    V3ToV4BridgeConfig,
    AgentKnowledgePackage,
    BridgeStatus,
    tworz_v3_to_v4_bridge
)

# Re-export V2ToV3Bridge z V2
from ...v2.integration.v2_to_v3_bridge import (
    V2ToV3Bridge,
    BridgeConfig,
    WorldDataPackage
)

# SPRINT 7: Memory Synchronization
from .memory_sync import (
    MemorySynchronizer,
    MemorySyncConfig,
    SyncDirection,
    SyncMode,
    SyncStatus,
    MemoryType,
    MemoryChange,
    SyncPackage,
    SyncStatistics,
    ChangeTracker,
    ConflictResolver,
    tworz_memory_synchronizer,
    get_memory_synchronizer,
    reset_memory_synchronizer
)

__all__ = [
    # V3 Integration
    'WorldIntegration',
    'WorldIntegrationConfig',
    'IntegrationStatus',
    'tworz_integracje_v3',
    
    # V3 to V4 Bridge (Sprint 4)
    'V3ToV4Bridge',
    'V3ToV4BridgeConfig',
    'AgentKnowledgePackage',
    'BridgeStatus',
    'tworz_v3_to_v4_bridge',
    
    # SPRINT 7: Memory Synchronization
    'MemorySynchronizer',
    'MemorySyncConfig',
    'SyncDirection',
    'SyncMode',
    'SyncStatus',
    'MemoryType',
    'MemoryChange',
    'SyncPackage',
    'SyncStatistics',
    'ChangeTracker',
    'ConflictResolver',
    'tworz_memory_synchronizer',
    'get_memory_synchronizer',
    'reset_memory_synchronizer',
    
    # Re-exported from V2
    'V2ToV3Bridge',
    'BridgeConfig',
    'WorldDataPackage'
]
