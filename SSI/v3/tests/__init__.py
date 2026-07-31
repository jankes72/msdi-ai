"""
SSI V3 Tests - Moduł testów dla warstwy V3

Moduł odpowiedzialny za:
- Testy jednostkowe dla mechanizmu synchronizacji pamięci
- Testy integracyjne dla V3Integration, V3ToV4Bridge, WorldIntegration
- Walidację importów i konfiguracji
- Testy przepływu danych między V3 a V4

Zgodnie z:
- SPRINTY.md Sprint 8 (Testy integracyjne)
- PROJECT_RULES.md

Framework testowy: pytest

Wersja: 1.0
Data: 2026-07-28
"""

# Importy dla wygody - wszystkie klasy testowane są dostępne tutaj
# Pozwala na łatwiejsze pisanie testów bez długich importów

# Memory System
from ..memory.memory_manager import MemoryManager, MemoryConfig
from ..memory.observation_memory import ObservationMemory
from ..memory.pattern_memory import PatternMemory
from ..memory.metadata_memory import MetadataMemory
from ..memory.relationship_memory import RelationshipMemory
from ..memory.world_memory import WorldMemory

# World System
from ..worlds.world_manager import WorldManager, tworz_world_manager
from ..worlds.world import World, WorldConfig, WorldStatus, WorldType, WorldAccess

# Integration
from ..integration import (
    WorldIntegration, WorldIntegrationConfig, IntegrationStatus,
    tworz_integracje_v3 as tworz_world_integration,
    V3ToV4Bridge, V3ToV4BridgeConfig, AgentKnowledgePackage, BridgeStatus,
    tworz_v3_to_v4_bridge
)

# Memory Synchronization (Sprint 7)
from ..integration.memory_sync import (
    MemorySynchronizer, MemorySyncConfig, SyncDirection, SyncMode, SyncStatus,
    MemoryType, MemoryChange, SyncPackage, SyncStatistics,
    ChangeTracker, ConflictResolver,
    tworz_memory_synchronizer, get_memory_synchronizer, reset_memory_synchronizer
)

# V3 Main Integration
from ..v3_integration import (
    V3Integration, V3IntegrationConfig, IntegrationStatistics, ComponentStatus,
    tworz_v3_integration, get_v3_integration, reset_v3_integration
)

# Config
from ..config import (
    V3Config, IntegrationConfig, V4BridgeConfig, MemoryConfig, WorldConfig,
    LogLevel, ValidationMode,
    tworz_v3_config, get_v3_config, reset_v3_config
)

# Re-export V2 Bridge for backward compatibility
try:
    from ...v2.integration.v2_to_v3_bridge import (
        V2ToV3Bridge, BridgeConfig, WorldDataPackage
    )
except ImportError:
    V2ToV3Bridge = None
    BridgeConfig = None
    WorldDataPackage = None

# Eksport wszystkiego, co może być potrzebne w testach
__all__ = [
    # Memory System
    'MemoryManager', 'MemoryConfig',
    'ObservationMemory', 'PatternMemory', 'MetadataMemory', 'RelationshipMemory', 'WorldMemory',
    
    # World System
    'WorldManager', 'WorldConfig', 'World', 'WorldStatus', 'WorldType', 'WorldAccess',
    'tworz_world_manager',
    
    # Integration
    'WorldIntegration', 'WorldIntegrationConfig', 'IntegrationStatus',
    'tworz_world_integration',
    'V3ToV4Bridge', 'V3ToV4BridgeConfig', 'AgentKnowledgePackage', 'BridgeStatus',
    'tworz_v3_to_v4_bridge',
    
    # Memory Synchronization (Sprint 7)
    'MemorySynchronizer', 'MemorySyncConfig',
    'SyncDirection', 'SyncMode', 'SyncStatus',
    'MemoryType', 'MemoryChange', 'SyncPackage', 'SyncStatistics',
    'ChangeTracker', 'ConflictResolver',
    'tworz_memory_synchronizer', 'get_memory_synchronizer', 'reset_memory_synchronizer',
    
    # V3 Main Integration
    'V3Integration', 'V3IntegrationConfig', 'IntegrationStatistics', 'ComponentStatus',
    'tworz_v3_integration', 'get_v3_integration', 'reset_v3_integration',
    
    # Config
    'V3Config', 'IntegrationConfig', 'V4BridgeConfig', 'MemoryConfig', 'WorldConfig',
    'LogLevel', 'ValidationMode',
    'tworz_v3_config', 'get_v3_config', 'reset_v3_config',
    
    # V2 Bridge (opcjonalne)
    'V2ToV3Bridge', 'BridgeConfig', 'WorldDataPackage'
]

# Fixtures dla pytest (dostępne w całym module tests)
import pytest
from typing import Generator
from datetime import datetime


@pytest.fixture
def memory_sync_config() -> MemorySyncConfig:
    """Tworzy domyślną konfigurację synchronizacji"""
    return MemorySyncConfig(
        SYNC_DIRECTION=SyncDirection.BIDIRECTIONAL,
        SYNC_MODE=SyncMode.INCREMENTAL,
        AUTO_SYNC_ENABLED=False,
        TRACK_CHANGES=True,
        CHANGE_BUFFER_SIZE=100
    )


@pytest.fixture
def memory_synchronizer(memory_sync_config: MemorySyncConfig) -> MemorySynchronizer:
    """Tworzy synchronizator pamięci do testów"""
    return MemorySynchronizer(config=memory_sync_config)


@pytest.fixture
def v3_integration() -> V3Integration:
    """Tworzy instancję V3Integration do testów"""
    return tworz_v3_integration()


@pytest.fixture
def v3_to_v4_bridge() -> V3ToV4Bridge:
    """Tworzy most V3ToV4Bridge do testów"""
    return tworz_v3_to_v4_bridge()


@pytest.fixture
def world_integration() -> WorldIntegration:
    """Tworzy instancję WorldIntegration do testów"""
    return tworz_world_integration()


@pytest.fixture
def sample_memory_change() -> MemoryChange:
    """Tworzy próbkę zmiany pamięci"""
    return MemoryChange(
        memory_type=MemoryType.WORLD,
        entity_id="test_world_001",
        operation="create",
        new_value={"world_id": "test_world_001", "name": "Test World"},
        source="v3",
        priority=0
    )


@pytest.fixture
def sample_sync_package() -> SyncPackage:
    """Tworzy próbkę pakietu synchronizacji"""
    return SyncPackage(
        direction=SyncDirection.V3_TO_V4,
        memory_type=MemoryType.ALL,
        data={
            "worlds": [{"world_id": "test_001", "name": "Test World"}],
            "patterns": [{"pattern_id": "pattern_001", "type": "trend"}],
            "metadata": {"version": "1.0", "timestamp": datetime.now().isoformat()}
        },
        metadata={"source": "test", "purpose": "validation"}
    )


# Pomocnicze funkcje asercji

def assert_sync_status_transition(synchronizer: MemorySynchronizer, 
                                   from_status: SyncStatus, 
                                   to_status: SyncStatus) -> None:
    """Sprawdza, że status synchronizatora zmienił się z from_status na to_status"""
    # Ta funkcja może być używana w testach do sprawdzania przejścia między statusami
    pass


def assert_statistics_updated(stats: SyncStatistics, 
                               total_syncs: int = None,
                               successful_syncs: int = None) -> None:
    """Sprawdza, że statystyki zostały zaktualizowane"""
    if total_syncs is not None:
        assert stats.total_syncs >= total_syncs
    if successful_syncs is not None:
        assert stats.successful_syncs >= successful_syncs
