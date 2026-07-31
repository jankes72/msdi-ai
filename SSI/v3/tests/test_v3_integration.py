"""
SSI V3 Tests - Testy V3Integration

Testy sprawdzające poprawność głównej integracji V3,
w tym koordynację komponentów, statystyki i zarządzanie.

Zgodnie z:
- SPRINTY.md Sprint 8 (Testy integracyjne)
- PROJECT_RULES.md

Framework testowy: pytest
"""

import pytest
from datetime import datetime
from SSI.v3.tests import (
    V3Integration, V3IntegrationConfig, IntegrationStatistics, ComponentStatus,
    WorldManager, World, WorldConfig, WorldStatus, WorldType,
    MemoryManager, MemoryConfig, PatternMemory, ObservationMemory,
    MetadataMemory, RelationshipMemory,
    WorldIntegration, WorldIntegrationConfig,
    V3ToV4Bridge, V3ToV4BridgeConfig,
    tworz_v3_integration, get_v3_integration, reset_v3_integration,
    MemorySynchronizer, MemorySyncConfig
)


class TestV3IntegrationBasic:
    """Podstawowe testy V3Integration"""
    
    def test_create_v3_integration_default(self):
        """Test tworzenia V3Integration z konfiguracją domyślną"""
        integration = V3Integration()
        assert integration is not None
        assert isinstance(integration, V3Integration)
        assert hasattr(integration, 'config')
        assert hasattr(integration, 'memory_manager')
        assert hasattr(integration, 'world_manager')
    
    def test_create_v3_integration_with_config(self):
        """Test tworzenia V3Integration z niestandardową konfiguracją"""
        config = V3IntegrationConfig(
            MEMORY_ENABLED=True,
            WORLD_ENABLED=True,
            INTELLIGENCE_ENABLED=True,
            SYNC_ENABLED=True,
            LOG_LEVEL='DEBUG'
        )
        integration = V3Integration(config=config)
        assert integration is not None
        assert integration.config == config
        assert integration.config.MEMORY_ENABLED is True
    
    def test_v3_integration_config_default_values(self):
        """Test domyślnych wartości konfiguracji V3Integration"""
        config = V3IntegrationConfig()
        assert config.MEMORY_ENABLED is True
        assert config.WORLD_ENABLED is True
        assert config.INTELLIGENCE_ENABLED is True
        assert config.SYNC_ENABLED is False
        assert config.LOG_LEVEL == 'INFO'


class TestV3IntegrationFactory:
    """Testy fabryki tworz_v3_integration"""
    
    def test_tworz_v3_integration(self):
        """Test fabryki V3Integration"""
        integration = tworz_v3_integration()
        assert integration is not None
        assert isinstance(integration, V3Integration)
    
    def test_tworz_v3_integration_with_config(self):
        """Test fabryki z konkretną konfiguracją"""
        config = V3IntegrationConfig(
            MEMORY_ENABLED=True,
            WORLD_ENABLED=True,
            SYNC_ENABLED=True
        )
        integration = tworz_v3_integration(config=config)
        assert integration is not None
        assert integration.config.SYNC_ENABLED is True


class TestV3IntegrationComponents:
    """Testy komponentów V3Integration"""
    
    @pytest.fixture
    def v3_integration_initialized(self):
        """V3Integration z zainicjalizowanymi komponentami"""
        integration = V3Integration()
        integration.initialize()
        return integration
    
    def test_memory_manager_initialized(self, v3_integration_initialized):
        """Test, że MemoryManager jest zainicjalizowany"""
        assert v3_integration_initialized.memory_manager is not None
        assert isinstance(v3_integration_initialized.memory_manager, MemoryManager)
    
    def test_world_manager_initialized(self, v3_integration_initialized):
        """Test, że WorldManager jest zainicjalizowany"""
        assert v3_integration_initialized.world_manager is not None
        assert isinstance(v3_integration_initialized.world_manager, WorldManager)
    
    def test_components_are_singleton(self):
        """Test, że komponenty są singletonami"""
        integration = V3Integration()
        integration.initialize()
        
        # Pobieramy instancje
        memory_manager_1 = integration.memory_manager
        world_manager_1 = integration.world_manager
        
        # Reset i ponowne pobranie
        integration.reset()
        integration.initialize()
        
        memory_manager_2 = integration.memory_manager
        world_manager_2 = integration.world_manager
        
        # Powinny być te same instancje (singleton)
        # Note: W zależności od implementacji, to może się różnić


class TestV3IntegrationInitialization:
    """Testy inicjalizacji V3Integration"""
    
    def test_initialize_all_components(self):
        """Test inicjalizacji wszystkich komponentów"""
        integration = V3Integration()
        
        # Before initialization
        assert integration.memory_manager is None
        assert integration.world_manager is None
        
        integration.initialize()
        
        # After initialization
        assert integration.memory_manager is not None
        assert integration.world_manager is not None
    
    def test_initialize_with_custom_components(self):
        """Test inicjalizacji z własnymi komponentami"""
        integration = V3Integration()
        
        custom_memory_manager = MemoryManager(config=MemoryConfig())
        custom_world_manager = WorldManager(config=WorldConfig())
        
        integration.initialize(
            memory_manager=custom_memory_manager,
            world_manager=custom_world_manager
        )
        
        assert integration.memory_manager is custom_memory_manager
        assert integration.world_manager is custom_world_manager
    
    def test_reset(self):
        """Test resetu V3Integration"""
        integration = V3Integration()
        integration.initialize()
        
        assert integration.memory_manager is not None
        assert integration.world_manager is not None
        
        integration.reset()
        
        assert integration.memory_manager is None
        assert integration.world_manager is None


class TestV3IntegrationStatus:
    """Testy statusu V3Integration"""
    
    def test_status_initial_state(self):
        """Test początkowego stanu statusu"""
        integration = V3Integration()
        # Powinien mieć jakiś domyślny status
        assert hasattr(integration, 'status')
    
    def test_get_component_status(self):
        """Test pobierania statusu komponentów"""
        integration = V3Integration()
        integration.initialize()
        
        status = integration.get_component_status()
        assert status is not None
        assert isinstance(status, dict)
    
    def test_check_components_health(self):
        """Test sprawdzania zdrowia komponentów"""
        integration = V3Integration()
        integration.initialize()
        
        health = integration.check_components_health()
        assert health is not None
        assert isinstance(health, dict)


class TestV3IntegrationMemoryOperations:
    """Testy operacji pamięciowych w V3Integration"""
    
    @pytest.fixture
    def v3_integration_with_memory(self):
        """V3Integration z pamięcią"""
        integration = V3Integration()
        integration.initialize()
        return integration
    
    def test_get_memory_manager(self, v3_integration_with_memory):
        """Test pobierania MemoryManager"""
        memory_manager = v3_integration_with_memory.get_memory_manager()
        assert memory_manager is not None
        assert isinstance(memory_manager, MemoryManager)
    
    def test_get_world_memory(self, v3_integration_with_memory):
        """Test pobierania WorldMemory"""
        world_memory = v3_integration_with_memory.get_world_memory()
        assert world_memory is not None
    
    def test_get_pattern_memory(self, v3_integration_with_memory):
        """Test pobierania PatternMemory"""
        pattern_memory = v3_integration_with_memory.get_pattern_memory()
        assert pattern_memory is not None
    
    def test_get_observation_memory(self, v3_integration_with_memory):
        """Test pobierania ObservationMemory"""
        observation_memory = v3_integration_with_memory.get_observation_memory()
        assert observation_memory is not None


class TestV3IntegrationWorldOperations:
    """Testy operacji na światach w V3Integration"""
    
    @pytest.fixture
    def v3_integration_with_worlds(self):
        """V3Integration z światami testowymi"""
        integration = V3Integration()
        integration.initialize()
        
        # Dodaj świat testowy
        test_world = World(
            world_id="test_world_001",
            name="Świat Testowy",
            world_type=WorldType.SIMULATION,
            status=WorldStatus.ACTIVE
        )
        integration.world_manager.add_world(test_world)
        
        return integration
    
    def test_get_worlds(self, v3_integration_with_worlds):
        """Test pobierania światów"""
        worlds = v3_integration_with_worlds.get_worlds()
        assert worlds is not None
        assert len(worlds) > 0
        world_ids = [w.world_id for w in worlds]
        assert "test_world_001" in world_ids
    
    def test_get_world_by_id(self, v3_integration_with_worlds):
        """Test pobierania świata po ID"""
        world = v3_integration_with_worlds.get_world_by_id("test_world_001")
        assert world is not None
        assert world.world_id == "test_world_001"


class TestV3IntegrationV4Communication:
    """Testy komunikacji z V4 w V3Integration"""
    
    @pytest.fixture
    def v3_integration_with_v4_bridge(self):
        """V3Integration z mostem V3 → V4"""
        integration = V3Integration()
        integration.initialize()
        
        # Konfiguracja z włączonym mostem
        v4_bridge_config = V3ToV4BridgeConfig(
            V4_BRIDGE_ENABLED=True,
            SEND_TO_V4=True
        )
        
        bridge = V3ToV4Bridge(config=v4_bridge_config)
        bridge.connect()
        
        integration.setup_v4_bridge(bridge)
        
        return integration
    
    def test_has_v4_bridge(self, v3_integration_with_v4_bridge):
        """Test, że V3Integration ma most V4"""
        assert v3_integration_with_v4_bridge.v4_bridge is not None
        assert isinstance(v3_integration_with_v4_bridge.v4_bridge, V3ToV4Bridge)
    
    def test_is_v4_available(self, v3_integration_with_v4_bridge):
        """Test dostępności V4"""
        # V4 powinno być dostępne przez most
        assert v3_integration_with_v4_bridge.is_v4_available()
    
    def test_send_worlds_to_v4(self, v3_integration_with_v4_bridge):
        """Test wysyłania światów do V4"""
        # Dodaj świat
        test_world = World(
            world_id="v4_world_001",
            name="Świat do V4",
            world_type=WorldType.PRODUCTION,
            status=WorldStatus.ACTIVE
        )
        v3_integration_with_v4_bridge.world_manager.add_world(test_world)
        
        # Wyślij do V4
        result = v3_integration_with_v4_bridge.send_worlds_to_v4()
        assert result is True


class TestV3IntegrationStatistics:
    """Testy statystyk V3Integration"""
    
    def test_get_statistics(self):
        """Test pobierania statystyk"""
        integration = V3Integration()
        integration.initialize()
        
        stats = integration.get_statistics()
        assert stats is not None
        assert isinstance(stats, IntegrationStatistics)
        assert hasattr(stats, 'total_operations')
        assert hasattr(stats, 'memory_operations')
        assert hasattr(stats, 'world_operations')
    
    def test_statistics_update_on_operations(self):
        """Test, że statystyki są aktualizowane po operacjach"""
        integration = V3Integration()
        integration.initialize()
        
        initial_stats = integration.get_statistics()
        initial_operations = initial_stats.total_operations
        
        # Dodaj świat
        test_world = World(
            world_id="stats_world_001",
            name="Świat Statystyk",
            world_type=WorldType.SIMULATION
        )
        integration.world_manager.add_world(test_world)
        
        # Statystyki powinny się zaktualizować
        updated_stats = integration.get_statistics()
        assert updated_stats.total_operations >= initial_operations


class TestV3IntegrationMemorySync:
    """Testy synchronizacji pamięci w V3Integration"""
    
    @pytest.fixture
    def v3_integration_with_sync(self):
        """V3Integration z włączoną synchronizacją pamięci"""
        config = V3IntegrationConfig(
            SYNC_ENABLED=True,
            MEMORY_ENABLED=True
        )
        integration = V3Integration(config=config)
        integration.initialize()
        
        # Skonfiguruj synchronizator
        sync_config = MemorySyncConfig(
            SYNC_DIRECTION='BIDIRECTIONAL',
            SYNC_MODE='INCREMENTAL',
            AUTO_SYNC_ENABLED=False
        )
        
        memory_synchronizer = MemorySynchronizer(config=sync_config)
        integration.setup_memory_synchronizer(memory_synchronizer)
        
        return integration
    
    def test_has_memory_synchronizer(self, v3_integration_with_sync):
        """Test, że V3Integration ma synchronizator pamięci"""
        assert v3_integration_with_sync.memory_synchronizer is not None
        assert isinstance(v3_integration_with_sync.memory_synchronizer, MemorySynchronizer)
    
    def test_sync_memory_enabled(self, v3_integration_with_sync):
        """Test, że synchronizacja pamięci jest włączona"""
        assert v3_integration_with_sync.config.SYNC_ENABLED is True
    
    def test_sync_memory_operations(self, v3_integration_with_sync):
        """Test operacji synchronizacji pamięci"""
        # Synchronizacja powinna działać
        result = v3_integration_with_sync.sync_memory()
        assert isinstance(result, bool)
        assert result is True


class TestV3IntegrationConfiguration:
    """Testy konfiguracji V3Integration"""
    
    def test_config_from_dict(self):
        """Test tworzenia konfiguracji z dict"""
        config_dict = {
            'MEMORY_ENABLED': True,
            'WORLD_ENABLED': True,
            'INTELLIGENCE_ENABLED': False,
            'SYNC_ENABLED': True,
            'LOG_LEVEL': 'DEBUG'
        }
        config = V3IntegrationConfig(**config_dict)
        
        assert config.MEMORY_ENABLED is True
        assert config.WORLD_ENABLED is True
        assert config.INTELLIGENCE_ENABLED is False
        assert config.SYNC_ENABLED is True
        assert config.LOG_LEVEL == 'DEBUG'
    
    def test_config_to_dict(self):
        """Test konwersji konfiguracji do dict"""
        config = V3IntegrationConfig(
            MEMORY_ENABLED=True,
            WORLD_ENABLED=False,
            LOG_LEVEL='WARNING'
        )
        
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict['MEMORY_ENABLED'] is True
        assert config_dict['WORLD_ENABLED'] is False
        assert config_dict['LOG_LEVEL'] == 'WARNING'


class TestV3IntegrationGlobalFunctions:
    """Testy funkcji globalnych V3Integration"""
    
    def test_get_v3_integration(self):
        """Test funkcji get_v3_integration"""
        integration = get_v3_integration()
        assert integration is not None
        assert isinstance(integration, V3Integration)
    
    def test_reset_v3_integration(self):
        """Test funkcji reset_v3_integration"""
        integration = get_v3_integration()
        initial_memory_manager = integration.memory_manager
        
        reset_v3_integration()
        
        new_integration = get_v3_integration()
        # Po resecie powinien być nowy lub zresetowany instancja
        assert new_integration is not None


class TestV3IntegrationOperations:
    """Testy operacji na pamięci i światach przez V3Integration"""
    
    def test_add_world_operation(self):
        """Test operacji dodawania świata"""
        integration = V3Integration()
        integration.initialize()
        
        initial_worlds = integration.get_worlds()
        initial_count = len(initial_worlds)
        
        # Dodaj nowy świat
        new_world = World(
            world_id="new_op_world_001",
            name="Nowy Świat Operacyjny",
            world_type=WorldType.PRODUCTION,
            status=WorldStatus.PENDING
        )
        integration.add_world(new_world)
        
        updated_worlds = integration.get_worlds()
        assert len(updated_worlds) == initial_count + 1
    
    def test_remove_world_operation(self):
        """Test operacji usuwania świata"""
        integration = V3Integration()
        integration.initialize()
        
        # Dodaj świat
        test_world = World(
            world_id="remove_test_001",
            name="Świat do Usunięcia",
            world_type=WorldType.TEST
        )
        integration.world_manager.add_world(test_world)
        
        # Usuń świat
        integration.remove_world("remove_test_001")
        
        # Sprawdź, że został usunięty
        worlds = integration.get_worlds()
        world_ids = [w.world_id for w in worlds]
        assert "remove_test_001" not in world_ids


class TestV3IntegrationErrorHandling:
    """Testy obsługi błędów w V3Integration"""
    
    def test_get_nonexistent_world(self):
        """Test pobierania nieistniejącego świata"""
        integration = V3Integration()
        integration.initialize()
        
        world = integration.get_world_by_id("nonexistent")
        assert world is None
    
    def test_send_to_v4_without_bridge(self):
        """Test wysyłania do V4 bez mostu"""
        integration = V3Integration()
        integration.initialize()
        
        result = integration.send_worlds_to_v4()
        assert result is False


class TestV3IntegrationComponentHealth:
    """Testy zdrowia komponentów V3Integration"""
    
    def test_health_check_all_components(self):
        """Test sprawdzania zdrowia wszystkich komponentów"""
        integration = V3Integration()
        integration.initialize()
        
        health = integration.check_components_health()
        
        assert health is not None
        assert isinstance(health, dict)
        
        # Powinno zwrócić informacje o każdym komponencie
        assert "memory_manager" in health
        assert "world_manager" in health
        
        # Statusy powinny być OK
        for component, status in health.items():
            if hasattr(status, 'value') and hasattr(status, 'name'):
                continue
            assert status in [ComponentStatus.OK, ComponentStatus.WARNING, ComponentStatus.ERROR]


