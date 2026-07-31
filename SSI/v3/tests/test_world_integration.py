"""
SSI V3 Tests - Testy WorldIntegration

Testy sprawdzające poprawność integracji światów
oraz komunikację z V4.

Zgodnie z:
- SPRINTY.md Sprint 8 (Testy integracyjne)
- PROJECT_RULES.md

Framework testowy: pytest
"""

import pytest
from datetime import datetime
from SSI.v3.tests import (
    WorldIntegration, WorldIntegrationConfig, IntegrationStatus,
    WorldManager, World, WorldConfig, WorldStatus, WorldType,
    V3ToV4Bridge, tworz_world_integration,
    MemoryManager, MemoryConfig
)


class TestWorldIntegrationBasic:
    """Podstawowe testy WorldIntegration"""
    
    def test_create_world_integration_default(self):
        """Test tworzenia WorldIntegration z konfiguracją domyślną"""
        integration = WorldIntegration()
        assert integration is not None
        assert isinstance(integration, WorldIntegration)
        assert hasattr(integration, 'config')
        assert hasattr(integration, 'world_manager')
    
    def test_create_world_integration_with_config(self):
        """Test tworzenia WorldIntegration z niestandardową konfiguracją"""
        config = WorldIntegrationConfig(
            AUTO_SYNC_ENABLED=True,
            SYNC_INTERVAL_SECONDS=30,
            SEND_TO_V4=True
        )
        integration = WorldIntegration(config=config)
        assert integration is not None
        assert integration.config == config
        assert integration.config.AUTO_SYNC_ENABLED is True
        assert integration.config.SEND_TO_V4 is True
    
    def test_world_integration_config_default_values(self):
        """Test domyślnych wartości konfiguracji WorldIntegration"""
        config = WorldIntegrationConfig()
        assert config.AUTO_SYNC_ENABLED is False
        assert config.SYNC_INTERVAL_SECONDS == 60
        assert config.SEND_TO_V4 is False
        assert config.AUTO_SEND_TO_V4 is False
        assert config.V4_BRIDGE_ENABLED is True
    
    def test_world_integration_status(self):
        """Test statusu integracji"""
        integration = WorldIntegration()
        assert integration.status == IntegrationStatus.DISCONNECTED
        
        # Po inicjalizacji status powinien się zmienić
        integration.initialize()
        assert integration.status == IntegrationStatus.CONNECTED


class TestWorldIntegrationFactory:
    """Testy fabryki tworz_integracje_v3"""
    
    def test_tworz_world_integration(self):
        """Test fabryki WorldIntegration"""
        integration = tworz_world_integration()
        assert integration is not None
        assert isinstance(integration, WorldIntegration)
    
    def test_tworz_world_integration_with_specific_config(self):
        """Test fabryki z konkretną konfiguracją"""
        config = WorldIntegrationConfig(
            SEND_TO_V4=True,
            AUTO_SYNC_ENABLED=True
        )
        integration = tworz_world_integration(config=config)
        assert integration is not None
        assert integration.config.SEND_TO_V4 is True


class TestWorldIntegrationWorldOperations:
    """Testy operacji na światach w WorldIntegration"""
    
    @pytest.fixture
    def world_integration_with_worlds(self):
        """WorldIntegration z dodanymi światami"""
        integration = WorldIntegration()
        integration.world_manager = WorldManager(
            config=WorldConfig(AUTO_CREATE_WORLDS=True)
        )
        
        # Dodaj świat testowy
        test_world = World(
            world_id="test_world_001",
            name="Świat Testowy",
            world_type=WorldType.SIMULATION,
            status=WorldStatus.ACTIVE
        )
        integration.world_manager.add_world(test_world)
        
        return integration
    
    def test_get_worlds(self, world_integration_with_worlds):
        """Test pobierania światów z WorldIntegration"""
        worlds = world_integration_with_worlds.get_worlds()
        assert worlds is not None
        assert len(worlds) > 0
        world_ids = [w.world_id for w in worlds]
        assert "test_world_001" in world_ids
    
    def test_get_world_by_id(self, world_integration_with_worlds):
        """Test pobierania konkretnego świata po ID"""
        world = world_integration_with_worlds.get_world_by_id("test_world_001")
        assert world is not None
        assert world.world_id == "test_world_001"
        assert world.name == "Świat Testowy"
    
    def test_add_world(self):
        """Test dodawania nowego świata"""
        integration = WorldIntegration()
        integration.world_manager = WorldManager()
        
        new_world = World(
            world_id="new_world_001",
            name="Nowy Świat",
            world_type=WorldType.PRODUCTION,
            status=WorldStatus.PENDING
        )
        
        integration.add_world(new_world)
        
        worlds = integration.get_worlds()
        world_ids = [w.world_id for w in worlds]
        assert "new_world_001" in world_ids


class TestWorldIntegrationV4Bridge:
    """Testy integracji WorldIntegration z mostem V3 → V4"""
    
    @pytest.fixture
    def world_integration_with_bridge(self):
        """WorldIntegration z podłączonym mostem V3 → V4"""
        integration = WorldIntegration(
            config=WorldIntegrationConfig(
                V4_BRIDGE_ENABLED=True,
                SEND_TO_V4=True
            )
        )
        
        # Podłączenie mostu
        bridge = V3ToV4Bridge()
        integration.setup_v4_bridge(bridge)
        
        return integration
    
    def test_has_v4_bridge(self, world_integration_with_bridge):
        """Test, że WorldIntegration ma podłączony most V4"""
        assert world_integration_with_bridge.v4_bridge is not None
        assert isinstance(world_integration_with_bridge.v4_bridge, V3ToV4Bridge)
    
    def test_v4_bridge_connected(self, world_integration_with_bridge):
        """Test, że most V4 jest połączony"""
        integration = world_integration_with_bridge
        assert integration.is_v4_bridge_available()
        assert integration.v4_bridge.is_connected()
    
    def test_send_to_v4(self, world_integration_with_bridge):
        """Test wysyłania danych do V4"""
        # Dodaj świat
        test_world = World(
            world_id="v4_test_world",
            name="Świat do V4",
            world_type=WorldType.PRODUCTION,
            status=WorldStatus.ACTIVE
        )
        world_integration_with_bridge.world_manager.add_world(test_world)
        
        # Wyślij do V4
        result = world_integration_with_bridge.send_to_v4()
        assert result is True


class TestWorldIntegrationDataFlow:
    """Testy przepływu danych w WorldIntegration"""
    
    def test_create_knowledge_package(self):
        """Test tworzenia pakietu wiedzy"""
        integration = WorldIntegration()
        
        # Utwórz świata
        test_world = World(
            world_id="knowledge_test_001",
            name="Świat Wiedzy",
            world_type=WorldType.SIMULATION,
            status=WorldStatus.ACTIVE,
            created_at=datetime.now(),
            metadata={"source": "test", "version": "1.0"}
        )
        integration.world_manager.add_world(test_world)
        
        # Utwórz pakiet wiedzy
        package = integration._create_knowledge_package()
        assert package is not None
        assert hasattr(package, 'worlds')
        assert hasattr(package, 'metadata')
        assert len(package.worlds) > 0
        assert any(w.world_id == "knowledge_test_001" for w in package.worlds)
    
    def test_knowledge_package_has_metadata(self):
        """Test, że pakiet wiedzy ma metadane"""
        integration = WorldIntegration()
        
        test_world = World(
            world_id="metadata_test_001",
            name="Świat z Metadanymi",
            world_type=WorldType.PRODUCTION,
            status=WorldStatus.ACTIVE,
            metadata={"test_key": "test_value"}
        )
        integration.world_manager.add_world(test_world)
        
        package = integration._create_knowledge_package()
        assert package.metadata is not None
        assert isinstance(package.metadata, dict)
        assert "timestamp" in package.metadata
        assert "source" in package.metadata


class TestWorldIntegrationSync:
    """Testy mechanizmu synchronizacji WorldIntegration"""
    
    @pytest.fixture
    def world_integration_sync_enabled(self):
        """WorldIntegration z włączoną synchronizacją"""
        config = WorldIntegrationConfig(
            AUTO_SYNC_ENABLED=True,
            SYNC_INTERVAL_SECONDS=10,
            V4_BRIDGE_ENABLED=True
        )
        integration = WorldIntegration(config=config)
        integration.setup_v4_bridge(V3ToV4Bridge())
        return integration
    
    def test_auto_sync_enabled(self, world_integration_sync_enabled):
        """Test, że auto-synchronizacja jest włączona"""
        assert world_integration_sync_enabled.config.AUTO_SYNC_ENABLED is True
        assert world_integration_sync_enabled.config.SYNC_INTERVAL_SECONDS == 10
    
    def test_sync_worlds_method(self, world_integration_sync_enabled):
        """Test metody sync_worlds"""
        # Dodaj świat
        test_world = World(
            world_id="sync_test_001",
            name="Świat do synchronizacji",
            world_type=WorldType.SIMULATION,
            status=WorldStatus.ACTIVE
        )
        world_integration_sync_enabled.world_manager.add_world(test_world)
        
        # Wykonaj synchronizację
        sync_result = world_integration_sync_enabled.sync_worlds()
        assert sync_result is True


class TestWorldIntegrationInitialization:
    """Testy inicjalizacji WorldIntegration"""
    
    def test_initialize_with_memory_manager(self):
        """Test inicjalizacji z MemoryManager"""
        integration = WorldIntegration()
        memory_manager = MemoryManager(config=MemoryConfig())
        
        integration.initialize(memory_manager=memory_manager)
        
        assert integration.memory_manager is memory_manager
        assert integration.world_manager is not None
    
    def test_initialize_sets_status(self):
        """Test, że inicjalizacja ustawia odpowiedni status"""
        integration = WorldIntegration()
        assert integration.status == IntegrationStatus.DISCONNECTED
        
        integration.initialize()
        assert integration.status == IntegrationStatus.CONNECTED
    
    def test_reset(self):
        """Test resetu WorldIntegration"""
        integration = WorldIntegration()
        integration.initialize()
        
        # Reset
        integration.reset()
        assert integration.status == IntegrationStatus.DISCONNECTED


class TestWorldIntegrationConfiguration:
    """Testy konfiguracji WorldIntegration"""
    
    def test_config_from_dict(self):
        """Test tworzenia konfiguracji z dict"""
        config_dict = {
            'AUTO_SYNC_ENABLED': True,
            'SYNC_INTERVAL_SECONDS': 45,
            'SEND_TO_V4': True,
            'AUTO_SEND_TO_V4': False
        }
        config = WorldIntegrationConfig(**config_dict)
        
        assert config.AUTO_SYNC_ENABLED is True
        assert config.SYNC_INTERVAL_SECONDS == 45
        assert config.SEND_TO_V4 is True
        assert config.AUTO_SEND_TO_V4 is False
    
    def test_config_to_dict(self):
        """Test konwersji konfiguracji do dict"""
        config = WorldIntegrationConfig(
            AUTO_SYNC_ENABLED=True,
            SYNC_INTERVAL_SECONDS=30
        )
        
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict['AUTO_SYNC_ENABLED'] is True
        assert config_dict['SYNC_INTERVAL_SECONDS'] == 30


class TestWorldIntegrationStatistics:
    """Testy statystyk WorldIntegration"""
    
    def test_get_integration_stats(self):
        """Test pobierania statystyk integracji"""
        integration = WorldIntegration()
        stats = integration.get_integration_stats()
        
        assert stats is not None
        assert isinstance(stats, dict)
        assert "world_count" in stats
        assert "status" in stats
    
    def test_stats_maintains_counts(self):
        """Test, że statystyki utrzymują liczniki"""
        integration = WorldIntegration()
        
        # Dodaj świat
        test_world = World(
            world_id="stats_test_001",
            name="Świat do statystyk",
            world_type=WorldType.SIMULATION
        )
        integration.world_manager.add_world(test_world)
        
        stats = integration.get_integration_stats()
        assert stats["world_count"] >= 1


class TestWorldIntegrationErrorHandling:
    """Testy obsługi błędów w WorldIntegration"""
    
    def test_get_nonexistent_world(self):
        """Test pobierania nieistniejącego świata"""
        integration = WorldIntegration()
        world = integration.get_world_by_id("nonexistent_world")
        assert world is None
    
    def test_send_to_v4_without_bridge(self):
        """Test wysyłania do V4 bez podłączonego mostu"""
        integration = WorldIntegration(
            config=WorldIntegrationConfig(SEND_TO_V4=True)
        )
        # Bez setup_v4_bridge()
        result = integration.send_to_v4()
        assert result is False
    
    def test_send_to_v4_without_worlds(self):
        """Test wysyłania do V4 bez żadnych światów"""
        integration = WorldIntegration(
            config=WorldIntegrationConfig(SEND_TO_V4=True)
        )
        integration.setup_v4_bridge(V3ToV4Bridge())
        
        # Žadnych światów - powinno pójść pomyślnie ale z pustym pakietem
        result = integration.send_to_v4()
        assert result is True


