"""
SSI V3 Tests - Testy importów

Testy sprawdzające poprawność importów i zależności
między modułami V3 ↔ V4.

Zgodnie z:
- SPRINTY.md Sprint 8 (Testy integracyjne)
- PROJECT_RULES.md

Framework testowy: pytest
"""

import sys
import importlib
import pytest


class TestV3Imports:
    """Testy importów dla modułów V3"""
    
    def test_import_v3_main_module(self):
        """Test importu głównego modułu V3"""
        from SSI.v3 import (
            V3Integration, V3Config, MemoryManager, WorldManager,
            V3ToV4Bridge, WorldIntegration
        )
        assert V3Integration is not None
        assert V3Config is not None
        assert MemoryManager is not None
        assert WorldManager is not None
        assert V3ToV4Bridge is not None
        assert WorldIntegration is not None
    
    def test_import_v3_config(self):
        """Test importu modułu konfiguracyjnego V3"""
        from SSI.v3.config import (
            V3Config, IntegrationConfig, V4BridgeConfig, MemoryConfig, WorldConfig,
            LogLevel, ValidationMode,
            tworz_v3_config, get_v3_config, reset_v3_config
        )
        assert V3Config is not None
        assert IntegrationConfig is not None
        assert V4BridgeConfig is not None
        assert LogLevel is not None
    
    def test_import_v3_integration(self):
        """Test importu głównej integracji V3"""
        from SSI.v3.v3_integration import (
            V3Integration, V3IntegrationConfig, IntegrationStatistics, ComponentStatus,
            tworz_v3_integration, get_v3_integration, reset_v3_integration
        )
        assert V3Integration is not None
        assert V3IntegrationConfig is not None
        assert IntegrationStatistics is not None
    
    def test_import_memory_system(self):
        """Test importu systemu pamięci"""
        from SSI.v3.memory.memory_manager import MemoryManager, MemoryConfig
        from SSI.v3.memory.observation_memory import ObservationMemory
        from SSI.v3.memory.pattern_memory import PatternMemory
        from SSI.v3.memory.metadata_memory import MetadataMemory
        from SSI.v3.memory.relationship_memory import RelationshipMemory
        from SSI.v3.memory.world_memory import WorldMemory
        
        assert MemoryManager is not None
        assert ObservationMemory is not None
        assert PatternMemory is not None
        assert MetadataMemory is not None
        assert RelationshipMemory is not None
        assert WorldMemory is not None
    
    def test_import_world_system(self):
        """Test importu systemu światów"""
        from SSI.v3.worlds.world_manager import WorldManager, tworz_world_manager
        from SSI.v3.worlds.world import World, WorldConfig, WorldStatus, WorldType, WorldAccess
        
        assert WorldManager is not None
        assert World is not None
        assert WorldConfig is not None
        assert tworz_world_manager is not None
    
    def test_import_world_integration(self):
        """Test importu integracji światów"""
        from SSI.v3.integration.world_integration import WorldIntegration, WorldIntegrationConfig
        from SSI.v3.integration import (
            WorldIntegration, WorldIntegrationConfig, IntegrationStatus,
            tworz_integracje_v3 as tworz_world_integration
        )
        
        assert WorldIntegration is not None
        assert WorldIntegrationConfig is not None
        assert IntegrationStatus is not None
    
    def test_import_v3_to_v4_bridge(self):
        """Test importu mostu V3 → V4"""
        from SSI.v3.integration.v3_to_v4_bridge import (
            V3ToV4Bridge, V3ToV4BridgeConfig, AgentKnowledgePackage, BridgeStatus,
            tworz_v3_to_v4_bridge
        )
        from SSI.v3.integration import (
            V3ToV4Bridge, V3ToV4BridgeConfig, AgentKnowledgePackage, BridgeStatus,
            tworz_v3_to_v4_bridge
        )
        
        assert V3ToV4Bridge is not None
        assert V3ToV4BridgeConfig is not None
        assert AgentKnowledgePackage is not None
    
    def test_import_memory_sync(self):
        """Test importu synchronizacji pamięci"""
        from SSI.v3.integration.memory_sync import (
            MemorySynchronizer, MemorySyncConfig, SyncDirection, SyncMode, SyncStatus,
            MemoryType, MemoryChange, SyncPackage, SyncStatistics,
            ChangeTracker, ConflictResolver,
            tworz_memory_synchronizer, get_memory_synchronizer, reset_memory_synchronizer
        )
        
        assert MemorySynchronizer is not None
        assert MemorySyncConfig is not None
        assert SyncDirection is not None
        assert SyncMode is not None
        assert MemoryType is not None
        assert MemoryChange is not None
        assert SyncPackage is not None
        assert ChangeTracker is not None
        assert ConflictResolver is not None


class TestV3TestModuleImports:
    """Testy importów z modułu testowego V3"""
    
    def test_import_from_tests_init(self):
        """Test importu z __init__.py modułu testów"""
        from SSI.v3.tests import (
            MemoryManager, MemoryConfig,
            WorldManager, WorldConfig, World,
            V3Integration, V3IntegrationConfig,
            V3ToV4Bridge, V3ToV4BridgeConfig,
            WorldIntegration, WorldIntegrationConfig,
            MemorySynchronizer, MemorySyncConfig,
            SyncDirection, SyncMode, SyncStatus,
            MemoryType, MemoryChange, SyncPackage
        )
        
        assert MemoryManager is not None
        assert V3Integration is not None
        assert V3ToV4Bridge is not None
        assert WorldIntegration is not None
        assert MemorySynchronizer is not None
    
    def test_import_fixtures(self):
        """Test importu fixture'ów z modułu testów"""
        from SSI.v3.tests import (
            memory_sync_config, memory_synchronizer,
            v3_integration, v3_to_v4_bridge, world_integration,
            sample_memory_change, sample_sync_package
        )
        # Fixtures są funkcjami, sprawdzamy czy istnieją
        assert callable(memory_sync_config)
        assert callable(memory_synchronizer)
        assert callable(v3_integration)
        assert callable(v3_to_v4_bridge)
        assert callable(world_integration)
        assert callable(sample_memory_change)
        assert callable(sample_sync_package)


class TestV4Dependencies:
    """Testy zależności V3 ↔ V4"""
    
    def test_import_v4_from_v3_bridge(self):
        """Test, że V3ToV4Bridge może importować zależności V4"""
        # V3ToV4Bridge powinien mieć dostęp do struktury V4
        from SSI.v3.integration.v3_to_v4_bridge import V3ToV4Bridge, AgentKnowledgePackage
        
        # Utworzenie instancji mostu
        bridge = V3ToV4Bridge()
        assert bridge is not None
        
        # Sprawdzamy, że most ma metody integracyjne
        assert hasattr(bridge, 'transfer_knowledge')
        assert hasattr(bridge, 'create_agent_knowledge_package')
        assert hasattr(bridge, 'convert_world_to_v4_format')
        assert hasattr(bridge, 'send_to_v4')
        
    def test_v3_integration_dependencies(self):
        """Test zależności V3Integration"""
        from SSI.v3.v3_integration import V3Integration
        
        # Utworzenie instancji
        integration = V3Integration()
        assert integration is not None
        
        # Sprawdzamy, że V3Integration ma dostęp do componentów
        assert hasattr(integration, 'memory_manager')
        assert hasattr(integration, 'world_manager')
        assert hasattr(integration, 'intelligence')


class TestCircularImportPrevention:
    """Testy zapobiegająca importom cyklicznym"""
    
    def test_no_circular_import_v3_integration(self):
        """Test, że V3Integration nie powoduje importów cyklicznych"""
        # Importujemy moduł i sprawdzamy, czy nie ma błędów
        import SSI.v3.v3_integration
        assert SSI.v3.v3_integration is not None
    
    def test_no_circular_import_memory_sync(self):
        """Test, że memory_sync nie powoduje importów cyklicznych"""
        import SSI.v3.integration.memory_sync
        assert SSI.v3.integration.memory_sync is not None
    
    def test_no_circular_import_world_integration(self):
        """Test, że world_integration nie powoduje importów cyklicznych"""
        import SSI.v3.integration.world_integration
        assert SSI.v3.integration.world_integration is not None


class TestModuleAvailability:
    """Testy dostępności modułów w systemie"""
    
    def test_all_v3_modules_exist(self):
        """Test, że wszystkie moduły V3 istnieją"""
        v3_modules = [
            'SSI.v3',
            'SSI.v3.config',
            'SSI.v3.v3_integration',
            'SSI.v3.integration',
            'SSI.v3.integration.world_integration',
            'SSI.v3.integration.v3_to_v4_bridge',
            'SSI.v3.integration.memory_sync',
            'SSI.v3.memory',
            'SSI.v3.memory.memory_manager',
            'SSI.v3.worlds',
            'SSI.v3.worlds.world_manager',
        ]
        
        for module_name in v3_modules:
            try:
                module = importlib.import_module(module_name)
                assert module is not None
            except ImportError as e:
                pytest.fail(f"Nie można zaimportować modułu {module_name}: {e}")
    
    def test_v4_modules_accessible_from_v3(self):
        """Test, że V4 jest dostępne z poziomu V3 (przez bridge)"""
        from SSI.v3.integration.v3_to_v4_bridge import V3ToV4Bridge
        
        bridge = V3ToV4Bridge()
        
        # Most powinien mieć mechanizmy do komunikacji z V4
        assert hasattr(bridge, 'connect_to_v4')
        assert hasattr(bridge, 'is_v4_available')


class TestImportPerformance:
    """Testy wydajności importów"""
    
    def test_import_speed_main_modules(self, benchmark):
        """Test czasu importu głównych modułów"""
        def import_main_modules():
            from SSI.v3 import V3Integration, V3Config, MemoryManager
            return V3Integration, V3Config, MemoryManager
        
        result = benchmark(import_main_modules)
        assert result is not None
    
    def test_import_speed_memory_system(self, benchmark):
        """Test czasu importu systemu pamięci"""
        def import_memory_system():
            from SSI.v3.memory.memory_manager import MemoryManager
            return MemoryManager
        
        result = benchmark(import_memory_system)
        assert result is not None


if __name__ == "__main__":
    # Uruchomienie testów przy bezpośrednim wywołaniu
    pytest.main([__file__, "-v", "--tb=short"])
