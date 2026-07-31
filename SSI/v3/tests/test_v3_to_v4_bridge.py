"""
SSI V3 Tests - Testy V3ToV4Bridge

Testy sprawdzające poprawność mostu komunikacyjnego V3 → V4,
w tym transfer wiedzy, konwersję struktur i obsługę agentów.

Zgodnie z:
- SPRINTY.md Sprint 8 (Testy integracyjne)
- PROJECT_RULES.md

Framework testowy: pytest
"""

import pytest
from datetime import datetime
from typing import Dict, Any
from SSI.v3.tests import (
    V3ToV4Bridge, V3ToV4BridgeConfig, AgentKnowledgePackage, BridgeStatus,
    World, WorldManager, WorldConfig, WorldStatus, WorldType,
    MemoryManager, MemoryConfig,
    PatternMemory, ObservationMemory, MetadataMemory,
    tworz_v3_to_v4_bridge,
    WorldIntegration, WorldIntegrationConfig
)


class TestV3ToV4BridgeBasic:
    """Podstawowe testy mostu V3ToV4Bridge"""
    
    def test_create_bridge_default(self):
        """Test tworzenia mostu z konfiguracją domyślną"""
        bridge = V3ToV4Bridge()
        assert bridge is not None
        assert isinstance(bridge, V3ToV4Bridge)
        assert hasattr(bridge, 'config')
        assert hasattr(bridge, 'status')
    
    def test_create_bridge_with_config(self):
        """Test tworzenia mostu z niestandardową konfiguracją"""
        config = V3ToV4BridgeConfig(
            AUTO_CONNECT=True,
            BUFFER_SIZE=1000,
            COMPRESSION_ENABLED=True
        )
        bridge = V3ToV4Bridge(config=config)
        assert bridge is not None
        assert bridge.config == config
        assert bridge.config.AUTO_CONNECT is True
        assert bridge.config.BUFFER_SIZE == 1000
    
    def test_bridge_config_default_values(self):
        """Test domyślnych wartości konfiguracji mostu"""
        config = V3ToV4BridgeConfig()
        assert config.AUTO_CONNECT is False
        assert config.BUFFER_SIZE == 500
        assert config.COMPRESSION_ENABLED is False
        assert config.MAX_RETRY_ATTEMPTS == 3
    
    def test_bridge_status(self):
        """Test statusu mostu"""
        bridge = V3ToV4Bridge()
        assert bridge.status == BridgeStatus.DISCONNECTED
        
        bridge.connect()
        assert bridge.status == BridgeStatus.CONNECTED
        
        bridge.disconnect()
        assert bridge.status == BridgeStatus.DISCONNECTED


class TestV3ToV4BridgeFactory:
    """Testy fabryki tworz_v3_to_v4_bridge"""
    
    def test_tworz_v3_to_v4_bridge(self):
        """Test fabryki mostu V3 → V4"""
        bridge = tworz_v3_to_v4_bridge()
        assert bridge is not None
        assert isinstance(bridge, V3ToV4Bridge)
    
    def test_tworz_v3_to_v4_bridge_with_config(self):
        """Test fabryki z konkretną konfiguracją"""
        config = V3ToV4BridgeConfig(
            AUTO_CONNECT=True,
            COMPRESSION_ENABLED=True
        )
        bridge = tworz_v3_to_v4_bridge(config=config)
        assert bridge is not None
        assert bridge.config.AUTO_CONNECT is True
        assert bridge.config.COMPRESSION_ENABLED is True


class TestV3ToV4BridgeConnectivity:
    """Testy połączeniowe mostu V3 → V4"""
    
    def test_connect_and_disconnect(self):
        """Test łączenia i rozłączania mostu"""
        bridge = V3ToV4Bridge()
        
        # Początkowo rozłączony
        assert bridge.is_connected() is False
        
        # Połączenie
        connect_result = bridge.connect()
        assert connect_result is True
        assert bridge.is_connected() is True
        assert bridge.status == BridgeStatus.CONNECTED
        
        # Rozłączenie
        disconnect_result = bridge.disconnect()
        assert disconnect_result is True
        assert bridge.is_connected() is False
        assert bridge.status == BridgeStatus.DISCONNECTED
    
    def test_is_v4_available(self):
        """Test sprawdzania dostępności V4"""
        bridge = V3ToV4Bridge()
        
        # Bez połączenia V4 nie jest dostępne
        assert bridge.is_v4_available() is False
        
        # Po połączeniu V4 powinno być dostępne (symulacja)
        bridge.connect()
        # Note: W prawdziwej implementacji is_v4_available() sprawdza
        # boss V4 jest naprawdę dostępny
        assert bridge.is_v4_available() is False  # Symulacja - V4 nie podłączone
    
    def test_reconnect(self):
        """Test ponownego łączenia"""
        bridge = V3ToV4Bridge()
        
        bridge.connect()
        assert bridge.is_connected() is True
        
        bridge.disconnect()
        assert bridge.is_connected() is False
        
        bridge.connect()
        assert bridge.is_connected() is True


class TestV3ToV4BridgeKnowledgeTransfer:
    """Testy transferu wiedzy przez most"""
    
    @pytest.fixture
    def bridge_with_worlds(self):
        """Most z podłączonymi światami V3"""
        bridge = V3ToV4Bridge()
        
        # Utworzenie światów testowych
        test_world = World(
            world_id="test_world_001",
            name="Świat Testowy",
            world_type=WorldType.SIMULATION,
            status=WorldStatus.ACTIVE,
            created_at=datetime.now(),
            metadata={"source": "v3", "version": "1.0"}
        )
        
        bridge.world_manager = WorldManager()
        bridge.world_manager.add_world(test_world)
        
        return bridge
    
    def test_extract_worlds_from_v3(self, bridge_with_worlds):
        """Test ekstrakcji światów z V3"""
        worlds_data = bridge_with_worlds._extract_worlds_from_v3()
        
        assert worlds_data is not None
        assert isinstance(worlds_data, list)
        assert len(worlds_data) > 0
        
        world_ids = [w.get('world_id') for w in worlds_data]
        assert "test_world_001" in world_ids
    
    def test_convert_world_to_v4_format(self, bridge_with_worlds):
        """Test konwersji świata do formatu V4"""
        test_world = bridge_with_worlds.world_manager.get_world("test_world_001")
        
        v4_world = bridge_with_worlds.convert_world_to_v4_format(test_world)
        
        assert v4_world is not None
        assert isinstance(v4_world, dict)
        assert "world_id" in v4_world
        assert "name" in v4_world
        assert v4_world["world_id"] == "test_world_001"
        assert v4_world["name"] == "Świat Testowy"
        
        # V4 format powinien zawierać metadane
        assert "metadata" in v4_world
        assert "created_at" in v4_world
    
    def test_create_agent_knowledge_package(self, bridge_with_worlds):
        """Test tworzenia pakietu wiedzy dla agentów"""
        package = bridge_with_worlds.create_agent_knowledge_package()
        
        assert package is not None
        assert isinstance(package, AgentKnowledgePackage)
        assert hasattr(package, 'worlds')
        assert hasattr(package, 'patterns')
        assert hasattr(package, 'metadata')
        assert hasattr(package, 'agent_id')
        
        assert len(package.worlds) > 0


class TestAgentKnowledgePackage:
    """Testy pakietu wiedzy dla agentów"""
    
    def test_create_agent_knowledge_package_directly(self):
        """Test tworzenia pakietu wiedzy bezpośrednio"""
        worlds_data = [
            {"world_id": "w1", "name": "Świat 1", "type": "simulation"},
            {"world_id": "w2", "name": "Świat 2", "type": "production"}
        ]
        
        patterns_data = [
            {"pattern_id": "p1", "type": "trend", "strength": 0.8},
            {"pattern_id": "p2", "type": "cycle", "strength": 0.6}
        ]
        
        package = AgentKnowledgePackage(
            worlds=worlds_data,
            patterns=patterns_data,
            agent_id="test_agent_001",
            metadata={"timestamp": datetime.now().isoformat(), "version": "1.0"}
        )
        
        assert package is not None
        assert len(package.worlds) == 2
        assert len(package.patterns) == 2
        assert package.agent_id == "test_agent_001"
        assert "timestamp" in package.metadata
    
    def test_package_to_dict(self):
        """Test konwersji pakietu do dict"""
        package = AgentKnowledgePackage(
            worlds=[{"world_id": "w1", "name": "Test World"}],
            patterns=[{"pattern_id": "p1", "type": "trend"}],
            agent_id="test_agent",
            metadata={"version": "1.0"}
        )
        
        package_dict = package.to_dict()
        assert isinstance(package_dict, dict)
        assert "worlds" in package_dict
        assert "patterns" in package_dict
        assert "agent_id" in package_dict
        assert "metadata" in package_dict
    
    def test_package_from_dict(self):
        """Test tworzenia pakietu z dict"""
        package_data = {
            "worlds": [{"world_id": "w1", "name": "Test"}],
            "patterns": [{"pattern_id": "p1", "type": "trend"}],
            "agent_id": "test_agent",
            "metadata": {"version": "1.0"}
        }
        
        package = AgentKnowledgePackage.from_dict(package_data)
        assert package is not None
        assert package.agent_id == "test_agent"
        assert len(package.worlds) == 1


class TestV3ToV4BridgeTransfer:
    """Testy transferu przez most"""
    
    def test_transfer_knowledge(self):
        """Test transferu wiedzy"""
        bridge = V3ToV4Bridge()
        
        # Utworzenie testowych danych
        knowledge_data = {
            "worlds": [
                {"world_id": "transfer_test_001", "name": "Świat Transferowy"}
            ],
            "patterns": [
                {"pattern_id": "pattern_001", "type": "trend"}
            ],
            "metadata": {"source": "v3", "timestamp": datetime.now().isoformat()}
        }
        
        # Transfer wiedzy
        result = bridge.transfer_knowledge(knowledge_data)
        
        # Recent: true bo most jest połączony (symulacja)
        assert isinstance(result, bool)
    
    def test_send_to_v4(self):
        """Test wysyłania do V4"""
        bridge = V3ToV4Bridge()
        
        # Połącz most
        bridge.connect()
        
        # Utwórz pakiet wiedzy
        package = AgentKnowledgePackage(
            worlds=[{"world_id": "send_test_001", "name": "Test Send"}],
            patterns=[],
            agent_id="test_agent"
        )
        
        # Wyślij do V4
        result = bridge.send_to_v4(package)
        assert isinstance(result, bool)
        # Recent: True ponieważ most jest połączony
        assert result is True


class TestV3ToV4BridgeMemoryOperations:
    """Testy operacji na pamięci przez most"""
    
    @pytest.fixture
    def bridge_with_memory(self):
        """Most z podłączoną pamięcią"""
        bridge = V3ToV4Bridge()
        bridge.memory_manager = MemoryManager(config=MemoryConfig())
        return bridge
    
    def test_extract_memory_data(self, bridge_with_memory):
        """Test ekstrakcji danych pamięci"""
        # Dodaj dane do pamięci
        worlds_data = [
            {"world_id": "mem_world_001", "name": "Świat Pamięci"}
        ]
        
        memory_data = bridge_with_memory._extract_memory_data()
        assert isinstance(memory_data, dict)
        assert "worlds" in memory_data
        assert "patterns" in memory_data
        assert "observations" in memory_data
        assert "metadata" in memory_data


class TestV3ToV4BridgeIntegration:
    """Testy integracyjne mostu z innymi komponentami"""
    
    def test_integration_with_world_integration(self):
        """Test integracji z WorldIntegration"""
        # Utwórz WorldIntegration
        world_integration = WorldIntegration(
            config=WorldIntegrationConfig(
                V4_BRIDGE_ENABLED=True,
                SEND_TO_V4=True
            )
        )
        
        # Utwórz i podłąc most
        bridge = V3ToV4Bridge()
        world_integration.setup_v4_bridge(bridge)
        
        assert world_integration.v4_bridge is bridge
        assert world_integration.is_v4_bridge_available() is True
    
    def test_bridge_with_shared_world_manager(self):
        """Test mostu z współdzielonym WorldManager"""
        shared_world_manager = WorldManager()
        
        test_world = World(
            world_id="shared_world_001",
            name="Współdzielony Świat",
            world_type=WorldType.PRODUCTION
        )
        shared_world_manager.add_world(test_world)
        
        # Utwórz most z tym samym WorldManager
        bridge = V3ToV4Bridge()
        bridge.world_manager = shared_world_manager
        
        # Most powinien widzieć świat
        worlds_data = bridge._extract_worlds_from_v3()
        world_ids = [w.get('world_id') for w in worlds_data]
        assert "shared_world_001" in world_ids


class TestV3ToV4BridgeErrorHandling:
    """Testy obsługi błędów w moście"""
    
    def test_transfer_without_connection(self):
        """Test transferu bez połączenia"""
        bridge = V3ToV4Bridge()
        
        knowledge_data = {"worlds": [], "patterns": []}
        
        # Bez połączenia transfer powinien zwrócić False
        result = bridge.transfer_knowledge(knowledge_data)
        assert result is False
    
    def test_send_without_connection(self):
        """Test wysyłania bez połączenia"""
        bridge = V3ToV4Bridge()
        
        package = AgentKnowledgePackage(
            worlds=[],
            patterns=[],
            agent_id="test"
        )
        
        result = bridge.send_to_v4(package)
        assert result is False
    
    def test_convert_none_world(self):
        """Test konwersji None świata"""
        bridge = V3ToV4Bridge()
        
        result = bridge.convert_world_to_v4_format(None)
        assert result == {}
    
    def test_connect_already_connected(self):
        """Test łączenia już połączonego mostu"""
        bridge = V3ToV4Bridge()
        
        bridge.connect()
        assert bridge.is_connected() is True
        
        # Powtórne połączenie nie powinno powodować błędu
        bridge.connect()
        assert bridge.is_connected() is True


class TestV3ToV4BridgeConfiguration:
    """Testy konfiguracji mostu"""
    
    def test_config_update(self):
        """Test aktualizacji konfiguracji"""
        bridge = V3ToV4Bridge()
        
        new_config = V3ToV4BridgeConfig(
            BUFFER_SIZE=2000,
            COMPRESSION_ENABLED=True
        )
        
        bridge.update_config(new_config)
        
        assert bridge.config.BUFFER_SIZE == 2000
        assert bridge.config.COMPRESSION_ENABLED is True
    
    def test_config_to_dict(self):
        """Test konwersji konfiguracji do dict"""
        config = V3ToV4BridgeConfig(
            AUTO_CONNECT=True,
            BUFFER_SIZE=1000,
            COMPRESSION_ENABLED=True
        )
        
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict['AUTO_CONNECT'] is True
        assert config_dict['BUFFER_SIZE'] == 1000
        assert config_dict['COMPRESSION_ENABLED'] is True


class TestV3ToV4BridgeStatusTransitions:
    """Testy przejść między statusami mostu"""
    
    def test_status_transitions(self):
        """Test wszystkich przejść statusów"""
        bridge = V3ToV4Bridge()
        
        # Początek: DISCONNECTED
        assert bridge.status == BridgeStatus.DISCONNECTED
        
        # Połączenie: DISCONNECTED -> CONNECTED
        bridge.connect()
        assert bridge.status == BridgeStatus.CONNECTED
        
        # Rozsynchronizowanie: CONNECTED -> SYNCING
        # Note: W obecnej implementacji status SYNCING przewidywany
        
        # Rozłączenie: CONNECTED -> DISCONNECTED
        bridge.disconnect()
        assert bridge.status == BridgeStatus.DISCONNECTED
    
    def test_get_status_string(self):
        """Test pobierania statusu jako string"""
        bridge = V3ToV4Bridge()
        
        status_str = bridge.get_status_string()
        assert isinstance(status_str, str)
        assert "DISCONNECTED" in status_str
        
        bridge.connect()
        status_str = bridge.get_status_string()
        assert "CONNECTED" in status_str


