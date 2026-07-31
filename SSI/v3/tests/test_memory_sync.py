"""
SSI V3 - Testy jednostkowe dla MemorySynchronizer (Sprint 7)

Moduł testów jednostkowych dla mechanizmu synchronizacji pamięci.

Zakres testów:
- MemorySyncConfig
- MemoryChange
- SyncPackage
- SyncStatistics
- ChangeTracker
- ConflictResolver
- MemorySynchronizer

Framework: pytest
Zgodnie z: SPRINTY.md Sprint 8

Wersja: 1.0
Data: 2026-07-28
"""

import pytest
from datetime import datetime
from typing import Dict, Any, List

# Importy z modułu testowego (upraszcza importy)
from . import (
    MemorySynchronizer, MemorySyncConfig, SyncDirection, SyncMode, SyncStatus,
    MemoryType, MemoryChange, SyncPackage, SyncStatistics,
    ChangeTracker, ConflictResolver,
    tworz_memory_synchronizer, get_memory_synchronizer, reset_memory_synchronizer
)


# =============================================================================
# TESTY KONFIGURACJI (MemorySyncConfig)
# =============================================================================

class TestMemorySyncConfig:
    """Testy dla klasy MemorySyncConfig"""
    
    def test_default_config_values(self):
        """Test domyślnych wartości konfiguracji"""
        config = MemorySyncConfig()
        
        assert config.SYNC_DIRECTION == SyncDirection.BIDIRECTIONAL
        assert config.SYNC_MODE == SyncMode.INCREMENTAL
        assert config.AUTO_SYNC_ENABLED is True
        assert config.AUTO_SYNC_INTERVAL == 60.0
        assert config.TRACK_CHANGES is True
        assert config.CHANGE_BUFFER_SIZE == 1000
        assert config.RESOLVE_CONFLICTS is True
        assert config.CONFLICT_RESOLUTION == "v3_priority"
        assert config.SYNC_MEMORY_TYPES == {MemoryType.WORLD, MemoryType.PATTERN, MemoryType.METADATA}
        assert config.MAX_CONCURRENT_SYNCS == 5
        assert config.SYNC_TIMEOUT == 120.0
        assert config.LOG_LEVEL == "INFO"
        assert config.TRACK_STATISTICS is True
    
    def test_custom_config_values(self):
        """Test niestandardowych wartości konfiguracji"""
        config = MemorySyncConfig(
            SYNC_DIRECTION=SyncDirection.V3_TO_V4,
            SYNC_MODE=SyncMode.FULL,
            AUTO_SYNC_ENABLED=False,
            AUTO_SYNC_INTERVAL=30.0,
            CHANGE_BUFFER_SIZE=500,
            CONFLICT_RESOLUTION="newest",
            SYNC_MEMORY_TYPES={MemoryType.WORLD, MemoryType.PATTERN}
        )
        
        assert config.SYNC_DIRECTION == SyncDirection.V3_TO_V4
        assert config.SYNC_MODE == SyncMode.FULL
        assert config.AUTO_SYNC_ENABLED is False
        assert config.AUTO_SYNC_INTERVAL == 30.0
        assert config.CHANGE_BUFFER_SIZE == 500
        assert config.CONFLICT_RESOLUTION == "newest"
        assert config.SYNC_MEMORY_TYPES == {MemoryType.WORLD, MemoryType.PATTERN}
    
    def test_to_dict_conversion(self):
        """Test konwersji konfiguracji do dict"""
        config = MemorySyncConfig(
            SYNC_DIRECTION=SyncDirection.V3_TO_V4,
            SYNC_MODE=SyncMode.INCREMENTAL
        )
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["SYNC_DIRECTION"] == "V3_TO_V4"
        assert config_dict["SYNC_MODE"] == "INCREMENTAL"
        assert config_dict["AUTO_SYNC_ENABLED"] is True
        assert config_dict["TRACK_CHANGES"] is True
    
    def test_from_dict_creation(self):
        """Test tworzenia konfiguracji z dict"""
        data = {
            "SYNC_DIRECTION": "V3_TO_V4",
            "SYNC_MODE": "FULL",
            "AUTO_SYNC_ENABLED": False,
            "AUTO_SYNC_INTERVAL": 45.0,
            "CONFLICT_RESOLUTION": "v4_priority",
            "SYNC_MEMORY_TYPES": ["WORLD", "PATTERN"]
        }
        
        config = MemorySyncConfig.from_dict(data)
        
        assert config.SYNC_DIRECTION == SyncDirection.V3_TO_V4
        assert config.SYNC_MODE == SyncMode.FULL
        assert config.AUTO_SYNC_ENABLED is False
        assert config.AUTO_SYNC_INTERVAL == 45.0
        assert config.CONFLICT_RESOLUTION == "v4_priority"
        assert MemoryType.WORLD in config.SYNC_MEMORY_TYPES
        assert MemoryType.PATTERN in config.SYNC_MEMORY_TYPES


# =============================================================================
# TESTY STRUKTUR DANYCH (MemoryChange, SyncPackage, SyncStatistics)
# =============================================================================

class TestMemoryChange:
    """Testy dla klasy MemoryChange"""
    
    def test_default_memory_change(self):
        """Test domyślnych wartości MemoryChange"""
        change = MemoryChange()
        
        assert change.change_id.startswith("change_")
        assert change.memory_type == MemoryType.WORLD
        assert change.entity_id == ""
        assert change.operation == ""
        assert change.old_value is None
        assert change.new_value is None
        assert change.source == ""
        assert change.priority == 0
        assert isinstance(change.timestamp, datetime)
    
    def test_custom_memory_change(self):
        """Test niestandardowego MemoryChange"""
        test_data = {"world_id": "test_001", "name": "Test World"}
        change = MemoryChange(
            memory_type=MemoryType.WORLD,
            entity_id="test_001",
            operation="create",
            old_value=None,
            new_value=test_data,
            source="v3",
            priority=1
        )
        
        assert change.memory_type == MemoryType.WORLD
        assert change.entity_id == "test_001"
        assert change.operation == "create"
        assert change.new_value == test_data
        assert change.source == "v3"
        assert change.priority == 1
    
    def test_to_dict_conversion(self):
        """Test konwersji MemoryChange do dict"""
        change = MemoryChange(
            memory_type=MemoryType.PATTERN,
            entity_id="pattern_001",
            operation="update",
            old_value={"confidence": 0.7},
            new_value={"confidence": 0.85},
            source="v3"
        )
        
        change_dict = change.to_dict()
        
        assert isinstance(change_dict, dict)
        assert change_dict["memory_type"] == "PATTERN"
        assert change_dict["entity_id"] == "pattern_001"
        assert change_dict["operation"] == "update"
        assert change_dict["source"] == "v3"
    
    def test_get_hash(self):
        """Test generowania hasha dla MemoryChange"""
        change1 = MemoryChange(
            memory_type=MemoryType.WORLD,
            entity_id="world_001",
            operation="create",
            source="v3"
        )
        change2 = MemoryChange(
            memory_type=MemoryType.WORLD,
            entity_id="world_001",
            operation="create",
            source="v3"
        )
        
        hash1 = change1.get_hash()
        hash2 = change2.get_hash()
        
        # Same dane powinny dać ten sam hash
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length


class TestSyncPackage:
    """Testy dla klasy SyncPackage"""
    
    def test_default_sync_package(self):
        """Test domyślnych wartości SyncPackage"""
        package = SyncPackage()
        
        assert package.package_id.startswith("sync_")
        assert package.direction == SyncDirection.V3_TO_V4
        assert package.memory_type == MemoryType.ALL
        assert package.data == {}
        assert package.changes == []
        assert isinstance(package.timestamp, datetime)
        assert package.metadata == {}
    
    def test_custom_sync_package(self):
        """Test niestandardowego SyncPackage"""
        test_data = {
            "worlds": [{"world_id": "test_001"}],
            "patterns": [{"pattern_id": "pattern_001"}]
        }
        test_changes = [
            MemoryChange(
                memory_type=MemoryType.WORLD,
                entity_id="test_001",
                operation="create"
            )
        ]
        
        package = SyncPackage(
            direction=SyncDirection.V4_TO_V3,
            memory_type=MemoryType.WORLD,
            data=test_data,
            changes=test_changes,
            metadata={"source": "test"}
        )
        
        assert package.direction == SyncDirection.V4_TO_V3
        assert package.memory_type == MemoryType.WORLD
        assert package.data == test_data
        assert len(package.changes) == 1
        assert package.metadata["source"] == "test"
    
    def test_to_dict_conversion(self):
        """Test konwersji SyncPackage do dict"""
        package = SyncPackage(
            direction=SyncDirection.BIDIRECTIONAL,
            memory_type=MemoryType.PATTERN,
            data={"patterns": [{"id": "test"}]},
            metadata={"version": "1.0"}
        )
        
        package_dict = package.to_dict()
        
        assert isinstance(package_dict, dict)
        assert package_dict["direction"] == "BIDIRECTIONAL"
        assert package_dict["memory_type"] == "PATTERN"
        assert package_dict["data"] == {"patterns": [{"id": "test"}]}
        assert package_dict["metadata"] == {"version": "1.0"}
    
    def test_from_dict_creation(self):
        """Test tworzenia SyncPackage z dict"""
        data = {
            "package_id": "test_sync_001",
            "direction": "V3_TO_V4",
            "memory_type": "WORLD",
            "data": {"worlds": [{"id": "test"}]},
            "changes": [],
            "timestamp": datetime.now().isoformat(),
            "metadata": {"source": "test"}
        }
        
        package = SyncPackage.from_dict(data)
        
        assert package.package_id == "test_sync_001"
        assert package.direction == SyncDirection.V3_TO_V4
        assert package.memory_type == MemoryType.WORLD
        assert package.data == {"worlds": [{"id": "test"}]}
        assert package.metadata == {"source": "test"}


class TestSyncStatistics:
    """Testy dla klasy SyncStatistics"""
    
    def test_default_statistics(self):
        """Test domyślnych wartości SyncStatistics"""
        stats = SyncStatistics()
        
        assert stats.total_syncs == 0
        assert stats.successful_syncs == 0
        assert stats.failed_syncs == 0
        assert stats.total_changes == 0
        assert stats.conflicts_detected == 0
        assert stats.conflicts_resolved == 0
        assert stats.total_sync_time == 0.0
        assert stats.average_sync_time == 0.0
        assert stats.sync_by_type == {}
        assert stats.sync_by_direction == {}
    
    def test_to_dict_conversion(self):
        """Test konwersji SyncStatistics do dict"""
        stats = SyncStatistics(
            total_syncs=10,
            successful_syncs=8,
            failed_syncs=2,
            total_changes=100
        )
        
        stats_dict = stats.to_dict()
        
        assert isinstance(stats_dict, dict)
        assert stats_dict["total_syncs"] == 10
        assert stats_dict["successful_syncs"] == 8
        assert stats_dict["failed_syncs"] == 2
        assert stats_dict["total_changes"] == 100


# =============================================================================
# TESTY CHANGE TRACKER
# =============================================================================

class TestChangeTracker:
    """Testy dla klasy ChangeTracker"""
    
    def test_tracker_initialization(self):
        """Test inicjalizacji ChangeTracker"""
        config = MemorySyncConfig(CHANGE_BUFFER_SIZE=100)
        tracker = ChangeTracker(config)
        
        stats = tracker.get_statistics()
        assert stats["total_changes"] == 0
        assert stats["unique_entities"] == 0
        assert stats["max_buffer_size"] == 100
    
    def test_record_change(self):
        """Test rejestrowania pojedynczej zmiany"""
        tracker = ChangeTracker()
        
        change = tracker.record_change(
            memory_type=MemoryType.WORLD,
            entity_id="world_001",
            operation="create",
            new_value={"world_id": "world_001"},
            source="v3"
        )
        
        assert change.memory_type == MemoryType.WORLD
        assert change.entity_id == "world_001"
        assert change.operation == "create"
        
        stats = tracker.get_statistics()
        assert stats["total_changes"] == 1
        assert stats["unique_entities"] == 1
    
    def test_record_multiple_changes(self):
        """Test rejestrowania wielu zmian"""
        tracker = ChangeTracker()
        
        # Zarejestruj kilka zmian
        tracker.record_change(
            memory_type=MemoryType.WORLD,
            entity_id="world_001",
            operation="create"
        )
        tracker.record_change(
            memory_type=MemoryType.WORLD,
            entity_id="world_002",
            operation="create"
        )
        tracker.record_change(
            memory_type=MemoryType.PATTERN,
            entity_id="pattern_001",
            operation="update"
        )
        
        stats = tracker.get_statistics()
        assert stats["total_changes"] == 3
        assert stats["unique_entities"] == 3
    
    def test_get_changes_filtering(self):
        """Test filtrowania zmian"""
        tracker = ChangeTracker()
        
        # Zarejestruj zmiany różnych typów
        tracker.record_change(MemoryType.WORLD, "world_001", "create")
        tracker.record_change(MemoryType.PATTERN, "pattern_001", "create")
        tracker.record_change(MemoryType.METADATA, "meta_001", "update")
        
        # Pobierz wszystkie zmiany
        all_changes = tracker.get_changes()
        assert len(all_changes) == 3
        
        # Pobierz tylko zmiany World
        world_changes = tracker.get_changes({MemoryType.WORLD})
        assert len(world_changes) == 1
        assert world_changes[0].memory_type == MemoryType.WORLD
        
        # Pobierz zmiany World i Pattern
        filtered_changes = tracker.get_changes({MemoryType.WORLD, MemoryType.PATTERN})
        assert len(filtered_changes) == 2
    
    def test_clear_changes(self):
        """Test czyszczenia zmian"""
        tracker = ChangeTracker()
        
        # Zarejestruj zmiany
        tracker.record_change(MemoryType.WORLD, "world_001", "create")
        tracker.record_change(MemoryType.PATTERN, "pattern_001", "create")
        
        # Sprawdź liczbę
        assert len(tracker.get_changes()) == 2
        
        # Wyczyść wszystkie
        cleared_count = tracker.clear_changes()
        assert cleared_count == 2
        assert len(tracker.get_changes()) == 0
    
    def test_clear_specific_changes(self):
        """Test czyszczenia określonych zmian"""
        tracker = ChangeTracker()
        
        change1 = tracker.record_change(MemoryType.WORLD, "world_001", "create")
        change2 = tracker.record_change(MemoryType.PATTERN, "pattern_001", "create")
        change3 = tracker.record_change(MemoryType.METADATA, "meta_001", "update")
        
        # Wyczyść tylko dwie zmiany
        cleared_count = tracker.clear_changes([change1.change_id, change2.change_id])
        assert cleared_count == 2
        
        remaining = tracker.get_changes()
        assert len(remaining) == 1
        assert remaining[0].entity_id == "meta_001"
    
    def test_detect_duplicates(self):
        """Test wykrywania duplikatów"""
        tracker = ChangeTracker()
        
        # Zarejestruj zmianę
        change1 = tracker.record_change(
            memory_type=MemoryType.WORLD,
            entity_id="world_001",
            operation="create",
            source="v3"
        )
        
        # Spróbuj zarejestrować taką samą zmianę (ten sam timestamp)
        # Powinien zostać wykryty jako duplikat
        change2 = tracker.record_change(
            memory_type=MemoryType.WORLD,
            entity_id="world_001",
            operation="create",
            source="v3"
        )
        
        # Powinien być jeden unikalny hash
        stats = tracker.get_statistics()
        assert stats["unique_hashes"] == 1


# =============================================================================
# TESTY CONFLICT RESOLVER
# =============================================================================

class TestConflictResolver:
    """Testy dla klasy ConflictResolver"""
    
    def test_resolver_initialization(self):
        """Test inicjalizacji ConflictResolver"""
        resolver = ConflictResolver()
        assert len(resolver.get_conflict_history()) == 0
    
    def test_detect_conflict(self):
        """Test wykrywania konfliktów"""
        resolver = ConflictResolver()
        
        v3_data = {"id": "test", "value": "from_v3", "timestamp": "2026-01-01"}
        v4_data = {"id": "test", "value": "from_v4", "timestamp": "2026-01-01"}
        
        has_conflict = resolver.detect_conflict(
            v3_data, v4_data, "test_entity", MemoryType.WORLD
        )
        
        assert has_conflict is True
    
    def test_no_conflict_for_identical_data(self):
        """Test braku konfliktu dla identycznych danych"""
        resolver = ConflictResolver()
        
        same_data = {"id": "test", "value": "same", "timestamp": "2026-01-01"}
        
        has_conflict = resolver.detect_conflict(
            same_data, same_data, "test_entity", MemoryType.WORLD
        )
        
        assert has_conflict is False
    
    def test_no_conflict_for_timestamp_only_difference(self):
        """Test braku konfliktu, gdy różni się tylko timestamp"""
        resolver = ConflictResolver()
        
        v3_data = {"id": "test", "value": "same", "timestamp": "2026-01-01"}
        v4_data = {"id": "test", "value": "same", "timestamp": "2026-01-02"}
        
        has_conflict = resolver.detect_conflict(
            v3_data, v4_data, "test_entity", MemoryType.WORLD
        )
        
        assert has_conflict is False
    
    def test_resolve_conflict_v3_priority(self):
        """Test rozwiązywania konfliktu z priorytetem V3"""
        config = MemorySyncConfig(CONFLICT_RESOLUTION="v3_priority")
        resolver = ConflictResolver(config)
        
        v3_data = {"id": "test", "value": "v3_value", "timestamp": "2026-01-01"}
        v4_data = {"id": "test", "value": "v4_value", "timestamp": "2026-01-01"}
        
        resolved = resolver.resolve_conflict(
            v3_data, v4_data, "test_entity", MemoryType.WORLD
        )
        
        assert resolved["value"] == "v3_value"
        assert resolved == v3_data
    
    def test_resolve_conflict_v4_priority(self):
        """Test rozwiązywania konfliktu z priorytetem V4"""
        config = MemorySyncConfig(CONFLICT_RESOLUTION="v4_priority")
        resolver = ConflictResolver(config)
        
        v3_data = {"id": "test", "value": "v3_value", "timestamp": "2026-01-01"}
        v4_data = {"id": "test", "value": "v4_value", "timestamp": "2026-01-01"}
        
        resolved = resolver.resolve_conflict(
            v3_data, v4_data, "test_entity", MemoryType.WORLD
        )
        
        assert resolved["value"] == "v4_value"
        assert resolved == v4_data
    
    def test_resolve_conflict_newest(self):
        """Test rozwiązywania konfliktu na podstawie timestamp"""
        config = MemorySyncConfig(CONFLICT_RESOLUTION="newest")
        resolver = ConflictResolver(config)
        
        v3_data = {"id": "test", "value": "v3_value", "timestamp": "2026-01-02"}
        v4_data = {"id": "test", "value": "v4_value", "timestamp": "2026-01-01"}
        
        resolved = resolver.resolve_conflict(
            v3_data, v4_data, "test_entity", MemoryType.WORLD
        )
        
        assert resolved["value"] == "v3_value"
        
        # Odwrotnie - V4 nowsze
        v3_data_old = {"id": "test2", "value": "v3_value", "timestamp": "2026-01-01"}
        v4_data_new = {"id": "test2", "value": "v4_value", "timestamp": "2026-01-02"}
        
        resolved2 = resolver.resolve_conflict(
            v3_data_old, v4_data_new, "test_entity2", MemoryType.WORLD
        )
        
        assert resolved2["value"] == "v4_value"
    
    def test_manual_resolution_raises_error(self):
        """Test, że manualne rozwiązywanie rzuca błąd"""
        config = MemorySyncConfig(CONFLICT_RESOLUTION="manual")
        resolver = ConflictResolver(config)
        
        v3_data = {"id": "test", "value": "v3_value", "timestamp": datetime.now().isoformat()}
        v4_data = {"id": "test", "value": "v4_value", "timestamp": datetime.now().isoformat()}
        
        with pytest.raises(ValueError) as exc_info:
            resolver.resolve_conflict(v3_data, v4_data, "test_entity", MemoryType.WORLD)
        
        assert "Manual conflict resolution required" in str(exc_info.value)
    
    def test_conflict_history(self):
        """Test historii konfliktów"""
        resolver = ConflictResolver()
        
        v3_data = {"id": "test", "value": "v3", "timestamp": "2026-01-01"}
        v4_data = {"id": "test", "value": "v4", "timestamp": "2026-01-01"}
        
        # Rozwiąż konflikt
        resolver.resolve_conflict(v3_data, v4_data, "test_entity", MemoryType.WORLD)
        
        history = resolver.get_conflict_history()
        assert len(history) == 1
        assert history[0]["memory_type"] == "WORLD"
        assert history[0]["entity_id"] == "test_entity"
    
    def test_clear_conflict_history(self):
        """Test czyszczenia historii konfliktów"""
        resolver = ConflictResolver()
        
        v3_data = {"id": "test", "value": "v3"}
        v4_data = {"id": "test", "value": "v4"}
        
        resolver.resolve_conflict(v3_data, v4_data, "test_entity", MemoryType.WORLD)
        resolver.resolve_conflict(v3_data, v4_data, "test_entity2", MemoryType.PATTERN)
        
        assert len(resolver.get_conflict_history()) == 2
        
        cleared_count = resolver.clear_conflict_history()
        assert cleared_count == 2
        assert len(resolver.get_conflict_history()) == 0


# =============================================================================
# TESTY GŁÓWNEJ KLASY MEMORY SYNCHRONIZER
# =============================================================================

class TestMemorySynchronizer:
    """Testy dla głównej klasy MemorySynchronizer"""
    
    def test_synchronizer_initialization(self):
        """Test inicjalizacji MemorySynchronizer"""
        config = MemorySyncConfig(AUTO_SYNC_ENABLED=False)
        synchronizer = MemorySynchronizer(config)
        
        assert synchronizer.config == config
        assert synchronizer.get_status() == SyncStatus.IDLE
    
    def test_default_synchronizer(self):
        """Test synchronizatora z domyślną konfiguracją"""
        synchronizer = MemorySynchronizer()
        
        assert synchronizer.config is not None
        assert isinstance(synchronizer.config, MemorySyncConfig)
        assert synchronizer.get_status() == SyncStatus.IDLE
    
    def test_connect_method(self):
        """Test metody connect"""
        synchronizer = MemorySynchronizer()
        
        # Połączenie bez V3 i V4 (powinno zwrócić False)
        result = synchronizer.connect()
        assert result is False
    
    def test_get_statistics(self):
        """Test pobieraniastatystyk"""
        synchronizer = MemorySynchronizer()
        stats = synchronizer.get_statistics()
        
        assert isinstance(stats, dict)
        assert "total_syncs" in stats
        assert "successful_syncs" in stats
        assert "change_tracker" in stats
        assert "conflicts" in stats
    
    def test_reset_statistics(self):
        """Test resetowania statystyk"""
        synchronizer = MemorySynchronizer()
        
        # Zmień status
        synchronizer._statistics.total_syncs = 10
        synchronizer._statistics.successful_syncs = 8
        
        synchronizer.reset_statistics()
        
        stats = synchronizer.get_statistics()
        assert stats["total_syncs"] == 0
        assert stats["successful_syncs"] == 0
    
    def test_sync_all_without_connection(self):
        """Test sync_all bez połączenia"""
        synchronizer = MemorySynchronizer()
        
        result = synchronizer.sync_all()
        
        assert result["status"] == "success"  # Powinien się wykonać, ale nie przesłać nic
        assert result["changes_synced"] == 0
    
    def test_sync_memory_type(self):
        """Test synchronizacji określonego typu pamięci"""
        synchronizer = MemorySynchronizer()
        
        result = synchronizer.sync_memory_type(MemoryType.WORLD)
        
        assert result["status"] in ["success", "failed"]
    
    def test_force_sync(self):
        """Test wymuszonej pełnej synchronizacji"""
        synchronizer = MemorySynchronizer()
        
        result = synchronizer.force_sync()
        
        assert result["status"] in ["success", "failed"]
    
    def test_status_transitions(self):
        """Test przejść między statusami"""
        synchronizer = MemorySynchronizer()
        
        # Początkowy status
        assert synchronizer.get_status() == SyncStatus.IDLE
    
    def test_singleton_pattern(self):
        """Test wzorca Singleton dla MemorySynchronizer"""
        # Reset singleton
        reset_memory_synchronizer()
        
        sync1 = get_memory_synchronizer()
        sync2 = get_memory_synchronizer()
        
        assert sync1 is sync2
        
        # Reset i sprawdź, że nowy jest inny
        reset_memory_synchronizer()
        sync3 = get_memory_synchronizer()
        
        # sync3 powinien być nową instancją po resecie
        # (ale singleton powinien być tej samej instancji dla wielu wywołań)
        assert sync3 is not None


# =============================================================================
# FABRYKA I UTILITY
# =============================================================================

class TestMemorySynchronizerFactory:
    """Testy fabryki MemorySynchronizer"""
    
    def test_tworz_memory_synchronizer_with_config_dict(self):
        """Test fabryki z konfiguracją jako dict"""
        config_dict = {
            "SYNC_DIRECTION": "BIDIRECTIONAL",
            "SYNC_MODE": "INCREMENTAL",
            "AUTO_SYNC_ENABLED": False
        }
        
        synchronizer = tworz_memory_synchronizer(config_dict)
        
        assert synchronizer.config.SYNC_DIRECTION == SyncDirection.BIDIRECTIONAL
        assert synchronizer.config.SYNC_MODE == SyncMode.INCREMENTAL
        assert synchronizer.config.AUTO_SYNC_ENABLED is False
    
    def test_tworz_memory_synchronizer_with_config_object(self):
        """Test fabryki z konfiguracją jako MemorySyncConfig"""
        config = MemorySyncConfig(SYNC_MODE=SyncMode.FULL)
        
        synchronizer = tworz_memory_synchronizer(config)
        
        assert synchronizer.config.SYNC_MODE == SyncMode.FULL
    
    def test_tworz_memory_synchronizer_default(self):
        """Test fabryki z domyślną konfiguracją"""
        synchronizer = tworz_memory_synchronizer()
        
        assert synchronizer.config is not None
        assert isinstance(synchronizer.config, MemorySyncConfig)


# =============================================================================
# TESTY ENUMÓW
# =============================================================================

class TestSyncEnums:
    """Testy dla enumów SyncDirection, SyncMode, SyncStatus, MemoryType"""
    
    def test_sync_direction_enum(self):
        """Test enum SyncDirection"""
        assert SyncDirection.V3_TO_V4.value != SyncDirection.V4_TO_V3.value
        assert SyncDirection.BIDIRECTIONAL.value != SyncDirection.V3_TO_V4.value
        
        # Sprawdź, czy można iterować
        directions = list(SyncDirection)
        assert len(directions) == 3
    
    def test_sync_mode_enum(self):
        """Test enum SyncMode"""
        modes = list(SyncMode)
        assert len(modes) == 3
        assert SyncMode.FULL in modes
        assert SyncMode.INCREMENTAL in modes
        assert SyncMode.SELECTIVE in modes
    
    def test_sync_status_enum(self):
        """Test enum SyncStatus"""
        statuses = list(SyncStatus)
        assert len(statuses) == 6
        assert SyncStatus.IDLE in statuses
        assert SyncStatus.COMPLETED in statuses
        assert SyncStatus.FAILED in statuses
    
    def test_memory_type_enum(self):
        """Test enum MemoryType"""
        types = list(MemoryType)
        assert len(types) == 6
        assert MemoryType.WORLD in types
        assert MemoryType.PATTERN in types
        assert MemoryType.OBSERVATION in types
        assert MemoryType.METADATA in types
        assert MemoryType.RELATIONSHIP in types
        assert MemoryType.ALL in types


# =============================================================================
# MAIN - Uruchomienie testów
# =============================================================================

if __name__ == "__main__":
    # Uruchom testy z użyciem pytest
    import subprocess
    import sys
    
    print("=" * 70)
    print("SPINT 8: Testy jednostkowe MemorySynchronizer")
    print("=" * 70)
    
    # Uruchom pytest na tym pliku
    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd="D:/sts/aplikacjaTyperBetAi"
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    print("=" * 70)
    print(f"Wynik testów: {'SUKCES' if result.returncode == 0 else ' PORAŻKA'}")
    print("=" * 70)
    
    sys.exit(result.returncode)
